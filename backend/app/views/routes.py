from flask import Blueprint, jsonify, request, make_response, redirect, current_app
from urllib.parse import urlencode, urljoin
from flask_cors import CORS
from datetime import datetime
import app.src.grade_extractor as ge
from app.src.session import main as session_main
from dotenv import load_dotenv
import os
import secrets
import requests

api = Blueprint('api', __name__)

load_dotenv()

print(os.environ)
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))

WEB_ORIGIN = os.environ.get("WEB_ORIGIN", "http://localhost:5173")
CORS(api, supports_credentials=True, origins=[WEB_ORIGIN])

BB_BASE_URL = os.environ["BB_BASE_URL"].rstrip("/")
BB_CLIENT_ID = os.environ["BB_CLIENT_ID"]
BB_CLIENT_SECRET = os.environ["BB_CLIENT_SECRET"]
BB_REDIRECT_URI = os.environ.get("BB_REDIRECT_URI")

COOKIE_KW = dict(httponly=True, secure=True, samesite="Lax", path="/")



@api.route('/health')
def health():
    health = 200 ## Health should always be 200 for now, scalability not a concern
    if health == 200: # Service is healthy
        return jsonify(
            {
                "healthy": True
            }
            ), 200

@api.route('/courses/<string:course_code>/assessments', methods=['GET'])
def get_assessments(course_code: str, semester: ge.Semester=ge.Semester.SEM1, year: int=2025):
    """
    Get assessments for a course
    """
    extractor = ge.CourseExtractor(courses=[course_code])
    try:
        site = extractor.get_page(course_code, semester, year)
        table = extractor.get_table(site)
        return jsonify(table), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@api.get("/auth/3lo/login")
def three_legged_login():
    cfg = current_app.config
    BB_BASE_URL = cfg["BB_BASE_URL"]
    BB_CLIENT_ID = cfg["BB_CLIENT_ID"]
    BB_REDIRECT_URI = cfg["BB_REDIRECT_URI"]
    if not BB_REDIRECT_URI:
        return "BB_REDIRECT_URI not set", 500

    # You can also persist a CSRF state in a short-lived cookie if desired
    state = f"xsrf_{secrets.token_urlsafe(8)}"
    print(BB_CLIENT_ID)
    params = {
        "response_type": "code",
        "client_id": BB_CLIENT_ID,
        "redirect_uri": BB_REDIRECT_URI,
        "scope": "read",
        "state": state,
    }
    auth_url = f"{BB_BASE_URL}/learn/api/public/v1/oauth2/authorizationcode?{urlencode(params)}"
    resp = make_response(redirect(auth_url, code=302))
    return resp

@api.get("/auth/3lo/callback")
def three_legged_callback():
    cfg = current_app.config
    mgr = current_app.extensions["bb_tokens"]

    BB_BASE_URL = cfg["BB_BASE_URL"]
    BB_CLIENT_ID = cfg["BB_CLIENT_ID"]
    BB_CLIENT_SECRET = cfg["BB_CLIENT_SECRET"]
    WEB_ORIGIN = cfg["WEB_ORIGIN"]
    code = request.args.get("code")
    state = request.args.get("state")

    # Optional: validate CSRF state
    # if state != request.cookies.get("oauth_state"): return "Bad state", 400

    token_url = f"{BB_BASE_URL}/learn/api/public/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type": "client_credentials",
        "redirect_uri": cfg["BB_REDIRECT_URI"],
    }

    r = requests.post(token_url, headers=headers, data=body, timeout=20)
    if not r.ok:
        return f"Token exchange failed: {r.text}", 502

    tok = r.json()
    access = tok.get("access_token")
    refresh = tok.get("refresh_token")
    expires_in = int(tok.get("expires_in", 3600))

    # Create an opaque session id and store tokens server-side
    sid = secrets.token_urlsafe(24)
    mgr.save_3lo(sid, access, expires_in, refresh)

    # Set only the opaque session id in the browser
    resp = make_response(redirect(f"{WEB_ORIGIN}/app?auth=ok"))
    resp.set_cookie("sid", sid, max_age=30*24*3600, **COOKIE_KW)  # 30 days, adjust as needed
    # Clear ephemeral oauth_state
    resp.delete_cookie("oauth_state", path="/")
    return resp

@api.post("/auth/3lo/refresh")
def three_legged_refresh():
    mgr = current_app.extensions["bb_tokens"]
    sid = request.cookies.get("sid")
    if not sid:
        return jsonify({"error": "no_session"}), 401

    # Force a refresh attempt via helper (will refresh only if expired)
    # If still valid, returns the current access token.
    access = mgr.refresh_3lo_if_needed(sid)
    if not access:
        return jsonify({"error": "refresh_failed"}), 401
    return jsonify({"ok": True})

# If you still want a manual 2LO endpoint (optional)
@api.post("/auth/2lo/token")
def two_legged_token():
    mgr = current_app.extensions["bb_tokens"]
    # get_2lo_token caches & auto-refreshes in memory
    _ = mgr.get_2lo_token()
    return jsonify({"ok": True})

@api.route("/api/bb/<path:api_path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def bb_proxy(api_path: str):
    """
    Order of precedence:
      1) Use 3LO session (sid cookie) and auto-refresh if needed.
      2) Else fall back to app-level 2LO token from TokenManager.
      3) If neither, 401.
    """
    cfg = current_app.config
    mgr = current_app.extensions["bb_tokens"]
    BB_BASE_URL = cfg["BB_BASE_URL"]

    # 1) Try 3LO server-side session
    token = None
    sid = request.cookies.get("sid")
    print(sid)
    if sid:
        token = mgr.refresh_3lo_if_needed(sid)

    if not token:
        return jsonify({"error": "not_authenticated"}), 401

    # Whitelist only public Learn REST
    upstream_url = urljoin(BB_BASE_URL + "/", api_path)
    if not upstream_url.startswith(BB_BASE_URL + "/learn/api/public/"):
        return jsonify({"error": "blocked_path"}), 403

    headers = {"Authorization": f"Bearer {token}"}
    if "Content-Type" in request.headers:
        headers["Content-Type"] = request.headers["Content-Type"]

    try:
        if request.method in ("GET", "HEAD"):
            rr = requests.request(request.method, upstream_url, headers=headers, params=request.args, timeout=30)
        else:
            rr = requests.request(
                request.method, upstream_url, headers=headers, params=request.args, data=request.get_data(), timeout=60
            )
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

    resp = make_response(rr.content, rr.status_code)
    resp.headers["Content-Type"] = rr.headers.get("Content-Type", "application/octet-stream")
    return resp

@api.post("/auth/logout")
def logout():
    mgr = current_app.extensions["bb_tokens"]
    sid = request.cookies.get("sid")
    if sid:
        mgr.clear_3lo(sid)
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie("sid", path="/")
    return resp