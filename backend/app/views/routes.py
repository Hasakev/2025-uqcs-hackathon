from dataclasses import dataclass
from operator import or_
from app.models import db
from app.src import session
from flask import Blueprint, jsonify, request, make_response, redirect, current_app
from urllib.parse import urlencode, urljoin
from flask_cors import CORS
from datetime import datetime
import app.src.grade_extractor as ge
from app.src.session import main as session_main, SessionManager
from dotenv import load_dotenv
import os
import secrets
import requests
import base64, hashlib, os, secrets, urllib.parse as urlparse
from app.models.db import User, Bets, Courses, AssignmentMap, BetStatus, BetType
import time
from http.cookies import SimpleCookie
import uuid
from bs4 import BeautifulSoup, NavigableString
from uuid import UUID as _UUID


api = Blueprint('api', __name__)

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))

WEB_ORIGIN = os.environ.get("WEB_ORIGIN", "http://localhost:5173")
CORS(api) #removed security for dev purposes


BB_BASE_URL = os.environ["BB_BASE_URL"].rstrip("/")
BB_CLIENT_ID = os.environ["BB_CLIENT_ID"]
BB_CLIENT_SECRET = os.environ["BB_CLIENT_SECRET"]
BB_REDIRECT_URI = os.environ.get("BB_REDIRECT_URI")

COOKIE_KW = dict(httponly=True, secure=True, samesite="Lax", path="/")

SESSION = SessionManager("data")

@api.route('/create_user', methods=['POST'])
def create_user():
    data = request.json
    print(data)
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    if not username or not password or not email:
        return jsonify({"error": "Missing username, password or email"}), 400
    user = User(username=username, password=password, email=email,token = "", token_status = False)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@api.route('/get_user/<string:username>', methods=['GET'])
def get_user(username: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_json()), 200

@api.route('/token_status/<string:username>', methods=['GET'])
def token_status(username: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.token_status = check_token_status(user.token)
    db.session.commit()
    return jsonify({"token status": user.token_status}), 200

@api.route('/update_bets/<string:username>', methods=['GET'])
def update_bets(username: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    token = user.token
    if not check_token_status(token):
        return jsonify({"error": "Blackboard token has expired. please update"}), 404
    bets = Bets.query.filter_by(u1=username, status=BetStatus.Accepted).all()

    updates = 0
    for bet in bets:
        course_code = bet.coursecode
        data = grade_scrape_with_cookie(course_code, token)
        if data == {}:
            continue
        target_name = AssignmentMap.query.filter_by(ECP_name=bet.assessment).first().Grade_name
        grade = next((item['grade'] for item in data['grades'] if item['name'] == target_name), None)
        if not grade:
            continue
        updates += 1
        if bet.lower >= grade:
            bet.status = BetStatus.Win
            user.money += bet.wager1
            u2 = User.query.filter_by(username=bet.u2).first()
            u2.money -= bet.wager2
        else:
            bet.status = BetStatus.Loss
            user.money -= bet.wager1
            u2 = User.query.filter_by(username=bet.u2).first()
            u2.money += bet.wager2
        db.session.commit()
    
    db.session.commit()
    return jsonify({"number of bets updated": updates}), 200

def check_token_status(token: str) -> bool:
    if not token:
        return False
    cookie_string = "BbRouter="+token+"; Path=/; Secure; HttpOnly;"
    # Parse the cookie string into a SimpleCookie object
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    # Convert SimpleCookie to a dictionary for requests
    cookies_dict = {key: morsel.value for key, morsel in cookie.items()}

    courseId = Courses.query.filter_by(course_code="CSSE2010").first().course_id
    url = f"https://learn.uq.edu.au/webapps/bb-mygrades-BB5fd17f67f4120/myGrades?course_id={courseId}&stream_name=mygrades&is_stream=true"
    response = requests.get(url, cookies=cookies_dict)
    status_code = response.status_code
    if status_code != 200:
        return False

    return True

def grade_scrape_with_cookie(course_code: str, token: str) -> str:
    """
    Scrapes the course grades for a given student
    Args:
        url: The URL of the website to scrape.
        cookie_string: The cookie string to set for the request.
    Returns:
        Json of grade data (with empties or pending removed)
    """
    try:
        cookie_string = "BbRouter="+token+"; Path=/; Secure; HttpOnly;"
        # Parse the cookie string into a SimpleCookie object
        cookie = SimpleCookie()
        cookie.load(cookie_string)
        # Convert SimpleCookie to a dictionary for requests
        cookies_dict = {key: morsel.value for key, morsel in cookie.items()}

        courseId = Courses.query.filter_by(course_code=course_code).first().course_id
        url = f"https://learn.uq.edu.au/webapps/bb-mygrades-BB5fd17f67f4120/myGrades?course_id={courseId}&stream_name=mygrades&is_stream=true"
        response = requests.get(url, cookies=cookies_dict)
        if response.status_code != 200:
            return {}
        soup = BeautifulSoup(response.text, "html.parser")
        
        #check if user is allowwed to view grades for the course
        main_body = soup.find('div', id='streamDetailMainBodyRight')
        if not main_body:
            return {}
        # Find the first element (could be text or tag)
        for child in main_body.contents:
            if not child.strip():
                continue  # skip empty whitespace
            if not "mygrades" in str(child):
                # print(f"e0 : {child}")
                return {}
            else:
                break

        # First real element is a tag
        grades_wrapper = soup.find('div', id='grades_wrapper')
        if not grades_wrapper:
            return {}
        
        grades = []
        rows = grades_wrapper.find_all('div', class_='graded_item_row')
        for row in rows:
            # Extract assessment name
            name_span = row.select_one('.cell.gradable span')
            name = name_span.get_text(strip=True) if name_span else None

            # Extract grade
            grade_span = row.select_one('.cell.grade span.grade')
            grade = grade_span.get_text(strip=True) if grade_span else None

            if name and grade:
                grades.append({"name": name, "grade": grade})

        return {"grades": grades}
    except requests.exceptions.RequestException as e:
        return f"Error scraping website: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
    
@api.route('/course_check/<string:username>/<string:course_code>', methods=['GET'])
def course_check(username: str, course_code: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not check_token_status(user.token):
        return jsonify({"Course Grades Available": False}), 200
    token = user.token
    grades = grade_scrape_with_cookie(course_code, token)
    print(grades)
    if grades == {}:
        return jsonify({"Course Grades Available": False}), 200
    return jsonify({"Course Grades Available": True}), 200

@api.route('/grade_check/<string:username>/<string:course_code>', methods=['GET'])
def grade_check(username: str, course_code: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not check_token_status(user.token):
        return jsonify({"Course Grades Available": False}), 200
    token = user.token
    grades = grade_scrape_with_cookie(course_code, token)
    if grades == {}:
        return jsonify({"Course Grades Available": False}), 200
    return jsonify({"Grades": grades}), 200

@api.route('/update_token/<string:user>/<string:token>', methods=['GET'])
def update_token(user: str,token: str):
    user = User.query.filter_by(username=user).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.token = token
    user.token_status = check_token_status(token)
    db.session.commit()

    return jsonify({"token_status": user.token_status}), 200

@api.route('/add_course', methods=['POST'])
def add_course():
    data = request.json
    course_code = data.get("course_code")
    course_id = data.get("course_id")
    course_name = data.get("course_name")
    if not course_id or not course_code:
        return jsonify({"error": "Missing course code, course id"}), 400
    course = Courses(course_code=course_code, course_id=course_id, course_name=course_name)
    db.session.add(course)
    db.session.commit()
    return jsonify({"succesful addition": True}), 200

@api.route('/add_assaignment_map', methods=['POST'])
def add_assaignment_map():
    data = request.json
    ECP_name = data.get("ECP_name")
    Grade_name = data.get("Grade_name")
    if not ECP_name or not Grade_name:
        return jsonify({"error": "Missing one of the names"}), 400
    aMap = AssignmentMap(uuid = uuid.uuid4(), ECP_name=ECP_name, Grade_name=Grade_name)
    db.session.add(aMap)
    db.session.commit()
    return jsonify({"succesful addition": True}), 200

@api.route('/get_balance/<string:username>', methods=['GET'])
def get_balance(username: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"balance": user.money}), 200

@api.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.username for user in users]), 200

@api.route('/check_user', methods=['POST'])
def check_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"authenticated": False}), 200
    return jsonify({"authenticated": True}), 200

@api.route('/add_funds/<string:username>', methods=['POST'])
def add_funds(username: str):
    data = request.json
    amount = data.get("amount", 0)
    amount = float(amount)
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.money += amount
    db.session.commit()
    return jsonify({"new_balance": user.money}), 200

@api.route('/create_bet', methods=['POST'])
def create_bet():
    data = request.json
    u1 = data.get("u1")
    u2 = data.get("u2")
    type = data.get("type")
    coursecode = data.get("coursecode")
    year = data.get("year")
    semester = data.get("semester")
    assesment = data.get("assessment")
    upper = data.get("upper")
    lower = data.get("lower")
    wager1 = data.get("wager1")
    wager2 = data.get("wager2")
    description = data.get("description")

    if not u1 or not upper or not lower:
        print(u1, upper, lower)
        return jsonify({"error": "Missing required contents: User 1, User 2, Upper, Lower"}), 400
    bet = Bets(
        uuid = uuid.uuid4(),
        u1=u1,
        u2=None if not u2 else u2, 
        type=BetType.Monetary, 
        status = BetStatus.Pending, 
        coursecode=coursecode, 
        year=year, 
        semester=semester, 
        assessment=assesment, 
        upper=upper, 
        lower=lower, 
        wager1=wager1, 
        wager2=wager1, 
        description=description)
    db.session.add(bet)
    db.session.commit()
    return jsonify({"message": "Bet successfully added"}), 201

@api.route('/accept_bet/<string:user>/<string:id>', methods=['GET'])
def get_bet(user: str, id: str):
    try:
        uuid.UUID(id)
    except ValueError:
        return jsonify({"error": "Invalid UUID"}), 400
    
    bet_id = uuid.UUID(id)
    bet = Bets.query.filter_by(uuid=bet_id).first()
    if not bet:
        return jsonify({"error": "Bet not found"}), 404
    if bet.u1 == user:
        return jsonify({"error": "You cannot accept your own bet"}), 400
    
    bet.status = BetStatus.Accepted
    bet.u1 = user
    db.session.commit()
    return jsonify({"message": "Bet successfully accepted"}), 200


@api.route('/check_bets/<string:username>/<int:bet_status>', methods=['GET'])
def check_bets(username: str, bet_status: int):
    q = Bets.query.filter(or_(Bets.u1 == username, Bets.u2 == username))
    if bet_status != 0:
        status_enum = BetStatus(bet_status)
        q = q.filter(Bets.status == status_enum)
    bets = q.all()
    return jsonify([Bets.to_json(b) for b in bets]), 200

@api.route('/check_open_bets/<string:username>/<int:bet_status>', methods=['GET']) 
def check_open_bets(username: str, bet_status: int):
    q = Bets.query.filter(Bets.u1 != username, Bets.u2 == "NONE")
    if bet_status != 0:
        status_enum = BetStatus(bet_status)
        q = q.filter(Bets.status == status_enum)
    bets = q.all()
    return jsonify([Bets.to_json(b) for b in bets]), 200

@api.route('/accept_open_bet/<string:username>/<string:bet_id>', methods=['POST'])
def accept_open_bet(username: str, bet_id: str):
    # 1) Validate + convert to uuid.UUID (matches your UUID/BINARY(16) column)
    try:
        bet_uuid = _UUID(bet_id)
    except ValueError:
        return jsonify({"error": "Invalid bet id"}), 400

    # 2) Atomically claim the open, pending bet
    rows = (db.session.query(Bets)
            .filter(
                Bets.uuid == bet_uuid,
                Bets.status == BetStatus.Pending # only accept pending
            )
            .update(
                {"u2": username, "status": BetStatus.Accepted},
                synchronize_session=False
            ))

    if rows == 0:
        db.session.rollback()
        return jsonify({"error": "Bet not found, already accepted, or not pending"}), 409

    db.session.commit()
    return jsonify({"message": "Bet successfully accepted"}), 200

@api.route('/health')
def health():
    health = 200 ## Health should always be 200 for now, scalability not a concern
    if health == 200: # Service is healthy
        return jsonify(
            {
                "healthy": True
            }
            ), 200

@api.route('/courses/<string:course_code>/<int:semester>/<int:year>/assessments', methods=['GET'])
def get_assessments(course_code: str, semester: int, year: int=2025):
    """
    Get assessments for a course
    """
    if semester == 1:
        semester = ge.Semester.SEM1
    elif semester == 2:
        semester = ge.Semester.SEM2
    elif semester == 3:
        semester = ge.Semester.SUMMER
    else:
        return jsonify({"error": "Invalid semester"}), 400
    extractor = ge.CourseExtractor(courses=[course_code])
    try:
        site = extractor.get_page(course_code, semester, year)
        table = extractor.get_table(site)
        return jsonify(table), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def make_pkce():
    verifier = _b64url(os.urandom(32))                    # 43–128 chars after b64url
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


@api.get("/test")
def scrape():
    website = "https://learn.uq.edu.au"
    response = requests.get(website)
    if response.status_code == 200:
        return jsonify({"content": response.text}), 200
    return jsonify({"error": "Failed to retrieve content"}), 500

@api.route('/grade_check/<string:username>/<string:course_code>', methods=['GET'])
def grade_check(username: str, course_code: str):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not check_token_status(user.token):
        return jsonify({"Course Grades Available": False}), 200
    token = user.token
    grades = grade_scrape_with_cookie(course_code, token)
    if grades == {}:
        return jsonify({"Course Grades Available": False}), 200
    return jsonify({"Grades": grades}), 200
# @api.get("/auth/3lo/login")
# def three_legged_login():
#     cfg = current_app.config
#     BB_BASE_URL = cfg["BB_BASE_URL"]
#     BB_CLIENT_ID = cfg["BB_CLIENT_ID"]
#     BB_REDIRECT_URI = cfg["BB_REDIRECT_URI"]
#     if not BB_REDIRECT_URI:
#         return "BB_REDIRECT_URI not set", 500
#     verifier, challenge = make_pkce()
#     # You can also persist a CSRF state in a short-lived cookie if desired
#     state = f"xsrf_{secrets.token_urlsafe(8)}"
#     mgr = current_app.extensions["bb_tokens"]
#     # mgr.save_3lo(session_id, access)
#     print(BB_CLIENT_ID)
#     params = {
#         "response_type": "code",
#         "client_id": BB_CLIENT_ID,
#         "redirect_uri": BB_REDIRECT_URI,
#         "scope": "read",
#         "state": state,
#         "code_challenge": challenge,
#         "code_challenge_method": "S256",
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Bearer"}
#     # save auth
#     # include header
#     auth_url = f"{BB_BASE_URL}/learn/api/public/v1/oauth2/authorizationcode?{urlencode(params)}"
#     print(urlencode(params))
#     resp = make_response(redirect(auth_url, code=302))
#     return resp

@dataclass
class _Pending3LO:
    verifier: str
    created_at: float

_PENDING: dict[str, _Pending3LO] = {}
_PENDING_TTL = 600  # seconds


def _make_pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    return verifier, challenge


def _remember_state(state: str, verifier: str) -> None:
    _PENDING[state] = _Pending3LO(verifier=verifier, created_at=time.time())


def _pop_verifier(state: str) -> str | None:
    rec = _PENDING.pop(state, None)
    if not rec:
        return None
    if time.time() - rec.created_at > _PENDING_TTL:
        return None
    return rec.verifier

@api.route("/auth/3lo/login", methods=["GET"])
def three_legged_login():
    cfg = current_app.config
    BB_BASE_URL = cfg["BB_BASE_URL"].rstrip("/")
    BB_CLIENT_ID = cfg["BB_CLIENT_ID"]
    BB_REDIRECT_URI = cfg["BB_REDIRECT_URI"]  # MUST be this endpoint's URL (below)

    if not BB_REDIRECT_URI:
        return "BB_REDIRECT_URI not set", 500

    # PKCE + CSRF state
    verifier, challenge = _make_pkce()
    state = f"xsrf_{secrets.token_urlsafe(16)}"

    _remember_state(state, verifier)

    # (Optional) also set a short-lived state cookie for extra CSRF defense
    resp = make_response()
    resp.set_cookie(
        "oauth_state",
        state,
        max_age=30000,
        httponly=True,
        secure=True,      # devtunnels is https; keep this True for prod
        samesite="Lax",
        path="/",
    )
    # print the cookie for debug
    print("Set-Cookie:", resp.headers.get("Set-Cookie"))
    auth_cookie = SimpleCookie()
    auth_cookie.load(resp.headers.get("Set-Cookie"))
    print("Potential-Token:", auth_cookie["oauth_state"].value)

    params = {
        "response_type": "code",
        "client_id": BB_CLIENT_ID,
        "redirect_uri": BB_REDIRECT_URI,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        # "scope": "read",  # Blackboard scopes are typically set at app level; include if required
    }

    auth_url = f"{BB_BASE_URL}/learn/api/public/v1/oauth2/authorizationcode?{urlencode(params)}"
    resp.headers["Location"] = auth_url
    resp.status_code = 302
    return resp
    # redirect again to callback
    # request = make_request("GET", BB_REDIRECT_URI, params={"state": state, "code": code})
    # return request


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
    if not code or not state:
        return jsonify(error="missing code/state"), 400

    # Optional: validate CSRF state
    if state != request.cookies.get("oauth_state"): return "Bad state", 400

    token_url = f"{BB_BASE_URL}/learn/api/public/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {code}"}
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

@api.route('/bet/<string:user_id>/<int:bet_status>', methods=['GET'])
def get_pending_bets(user_id: str,bet_status: int):
    """
    Get pending bets
    """
    if semester == 1:
        semester = ge.Semester.SEM1
    elif semester == 2:
        semester = ge.Semester.SEM2
    elif semester == 3:
        semester = ge.Semester.SUMMER
    else:
        return jsonify({"error": "Invalid semester"}), 400
    
    extractor = ge.CourseExtractor(courses=[course_code])
    try:
        site = extractor.get_page(course_code, semester, year)
        table = extractor.get_table(site)
        return jsonify(table), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
    