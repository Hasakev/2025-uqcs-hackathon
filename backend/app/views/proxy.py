# proxy.py
from __future__ import annotations
from flask import Blueprint, request, jsonify, current_app
import requests, socket, ipaddress, uuid
from urllib.parse import urlparse
from typing import Dict

proxy_bp = Blueprint("proxy", __name__, url_prefix="/proxy")

# ---- In-memory session store (swap for Redis if needed) ----
SESSIONS: Dict[str, requests.Session] = {}

# ---- Helpers / SSRF guards ----
def _cfg(name: str, default):
    return current_app.config.get(name, default)

def _is_ip_private(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None)
        for family, _, _, _, sockaddr in infos:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                return True
        return False
    except Exception:
        # if resolution fails, be safe
        return True

def _is_host_allowed(host: str) -> bool:
    host = host.lower()
    allowlist: set[str] = _cfg("PROXY_ALLOWLIST", set())
    suffixes: set[str] = _cfg("PROXY_ALLOWLIST_SUFFIX", set())
    if allowlist or suffixes:
        if host in allowlist:
            return True
        for suf in suffixes:
            suf = suf.lstrip(".").lower()
            if host == suf or host.endswith("." + suf):
                return True
        return False
    # Open mode if no allowlist configured
    return True

def _validate_url(raw: str) -> tuple[bool, str | None]:
    if not raw:
        return False, "Missing url"
    try:
        u = urlparse(raw)
    except Exception:
        return False, "Invalid URL"
    if u.scheme not in _cfg("PROXY_ALLOWED_SCHEMES", {"http", "https"}):
        return False, f"Disallowed scheme: {u.scheme}"
    if not u.hostname:
        return False, "Missing hostname"
    if not _is_host_allowed(u.hostname):
        return False, f"Host not allowed: {u.hostname}"
    if _cfg("PROXY_BLOCK_PRIVATE_IPS", True) and _is_ip_private(u.hostname):
        return False, "Host resolves to a private/blocked address"
    return True, None

def _collect_set_cookie(resp: requests.Response) -> list[str]:
    vals: list[str] = []
    try:
        raw = resp.raw.headers
        if hasattr(raw, "get_all"):
            vals = raw.get_all("Set-Cookie") or []
    except Exception:
        pass
    if not vals:
        sc = resp.headers.get("Set-Cookie")
        if sc:
            vals = [sc]
    return vals

# ---- Routes ----
@proxy_bp.get("/session/start")
def start_session():
    """Create a new upstream session (persists cookies)."""
    sid = str(uuid.uuid4())
    s = requests.Session()
    s.max_redirects = int(_cfg("PROXY_MAX_REDIRECTS", 5))
    SESSIONS[sid] = s
    return jsonify({"session_id": sid})

@proxy_bp.post("/session/request")
def session_request():
    """
    Make a request using a stored session.

    JSON:
      {
        "session_id": "...",                 # required
        "url": "https://example.com/login",  # required
        "method": "GET|POST|PUT|PATCH|DELETE|HEAD",  # default GET
        "headers": {"User-Agent": "..."},
        "body": "raw string (forwarded as data)",
        "cookies": {"k": "v"},               # extra request cookies
        "follow_redirects": true              # default true
      }
    """
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    url = data.get("url", "")
    method = (data.get("method") or "GET").upper()
    headers = data.get("headers") or {}
    body = data.get("body")
    extra_cookies = data.get("cookies") or {}
    follow_redirects = bool(data.get("follow_redirects", True))

    if not sid or sid not in SESSIONS:
        return jsonify({"error": "Invalid session_id"}), 400

    ok, err = _validate_url(url)
    if not ok:
        return jsonify({"error": err}), 400

    # Strip hop-by-hop headers
    for hop in (
        "host",
        "content-length",
        "connection",
        "keep-alive",
        "transfer-encoding",
        "upgrade",
    ):
        headers.pop(hop, None)

    s = SESSIONS[sid]
    timeout = (
        float(_cfg("PROXY_CONNECT_TIMEOUT", 6.0)),
        float(_cfg("PROXY_READ_TIMEOUT", 15.0)),
    )

    try:
        resp = s.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            cookies=extra_cookies or None,
            timeout=timeout,
            allow_redirects=follow_redirects,
            stream=False,
        )

        # Gather redirect chain cookies (if followed)
        redirects = []
        set_cookies: list[str] = []
        if follow_redirects and resp.history:
            for r in resp.history:
                rc = _collect_set_cookie(r)
                redirects.append(
                    {
                        "status": r.status_code,
                        "url": r.url,
                        "location": r.headers.get("Location"),
                        "set_cookie": rc,
                    }
                )
                set_cookies.extend(rc)

        final_set = _collect_set_cookie(resp)
        set_cookies.extend(final_set)

        safe_headers = {
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in ("connection", "transfer-encoding", "keep-alive", "upgrade")
        }
        
        def cookies(dicti: dict[str,str]) -> str:
            return "; ".join(f"{k}={v}" for k, v in dicti.items())

        return jsonify(
            {
                "requested_url": url,
                "final_url": resp.url,
                "status": resp.status_code,
                "response_headers": safe_headers,
                "set_cookie": set_cookies,           # response cookies (incl HttpOnly)
                "session_cookies": cookies(s.cookies.get_dict()),  # cookie jar held by this server
                "redirect_chain": redirects,
                "body_preview": resp.text[:1000],
            }
        )
    except requests.TooManyRedirects:
        return jsonify({"error": f"Too many redirects (>{_cfg('PROXY_MAX_REDIRECTS',5)})"}), 502
    except requests.Timeout:
        return jsonify({"error": "Upstream timeout"}), 504
    except Exception as e:
        return jsonify({"error": f"Upstream error: {type(e).__name__}: {e}"}), 502

@proxy_bp.get("/session/use")
def use_session():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    new_website = data.get("url")
    if sid not in SESSIONS:
        return jsonify({"error": "Invalid session_id"}), 400
    cookies = SESSIONS[sid].cookies.get_dict()
    print(cookies)
    # use the cookies to access the new website using GET
    try:
        resp = requests.get(new_website, cookies=cookies)
        return jsonify({"status": resp.status_code, "body": resp.text})
    except Exception as e:
        return jsonify({"error": f"Failed to access new website: {e}"}), 502

@proxy_bp.post("/session/end")
def end_session():
    data = request.get_json(silent=True) or {}
    sid = data.get("session_id")
    if sid in SESSIONS:
        del SESSIONS[sid]
    return jsonify({"ended": sid})
