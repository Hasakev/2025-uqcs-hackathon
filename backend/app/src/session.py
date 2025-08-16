# session.py
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet, InvalidToken
from playwright.sync_api import sync_playwright, Browser, BrowserContext

@dataclass
class _LiveSession:
    session_id: str
    browser: Browser
    context: BrowserContext
    created_at: float


class SessionManager:
    """
    Encapsulates:
      - Launching a headful Playwright browser to complete login
      - Persisting storage state (cookies, localStorage)
      - Replaying those cookies to scrape pages with requests + BeautifulSoup
    Provides a thin dispatcher via `main(action, **kwargs)` so callers (routes) stay simple.
    """

    def __init__(
        self,
        storage_dir: Path | str = "data",
        encryption_key: Optional[str] = None,  # Fernet.generate_key().decode()
        user_agent: str | None = None,
    ) -> None:
        self.storage_dir = Path(storage_dir).resolve()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._fernet: Optional[Fernet] = None
        if encryption_key:
            try:
                self._fernet = Fernet(encryption_key.encode("utf-8"))
            except Exception as e:
                raise RuntimeError("Invalid ENCRYPTION_KEY for Fernet.") from e

        self._sessions: Dict[str, _LiveSession] = {}
        self._lock = threading.RLock()
        self._ua = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    # ---------- Public: single entrypoint ----------

    def main(self, action: str, **kwargs) -> Tuple[int, dict]:
        """
        Dispatcher for routes. Returns (http_status, json_payload).
        Supported actions:
          - start_login(login_url:str) -> {session_id}
          - commit(session_id:str) -> {message, state_path}
          - close(session_id:str) -> {message}
          - status(session_id:str) -> {in_memory, state_saved}
          - scrape(session_id:str, url:str) -> {status, title, content_length, sample_links}
        """
        try:
            if action == "start_login":
                login_url = kwargs.get("login_url")
                if not login_url:
                    return 400, {"error": "login_url required"}
                return 200, self._start_login(login_url)

            if action == "commit":
                session_id = kwargs.get("session_id")
                if not session_id:
                    return 400, {"error": "session_id required"}
                path = self._commit(session_id)
                return 200, {"message": "Session committed. Cookies saved.", "state_path": str(path)}

            if action == "close":
                session_id = kwargs.get("session_id")
                if not session_id:
                    return 400, {"error": "session_id required"}
                self._close(session_id)
                return 200, {"message": "Closed session (no cookies saved)."}

            if action == "status":
                session_id = kwargs.get("session_id")
                if not session_id:
                    return 400, {"error": "session_id required"}
                return 200, self._status(session_id)

            if action == "scrape":
                session_id = kwargs.get("session_id")
                url = kwargs.get("url")
                if not session_id or not url:
                    return 400, {"error": "session_id and url are required"}
                return self._scrape(session_id, url)

            return 404, {"error": f"Unknown action '{action}'"}
        except PermissionError as e:
            return 403, {"error": str(e)}
        except KeyError as e:
            return 404, {"error": str(e)}
        except requests.HTTPError as e:
            return 502, {"error": f"Upstream HTTP error: {e}"}
        except Exception as e:
            # Last-resort guard
            return 500, {"error": f"{type(e).__name__}: {e}"}

    # ---------- Internals ----------

    def _gen_session_id(self) -> str:
        return secrets.token_urlsafe(16)

    def _state_path(self, session_id: str) -> Path:
        return (self.storage_dir / f"{session_id}.state").resolve()

    def _write_state(self, path: Path, data: dict) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        if self._fernet:
            raw = self._fernet.encrypt(raw)
        path.write_bytes(raw)

    def _read_state(self, path: Path) -> dict:
        raw = path.read_bytes()
        if self._fernet:
            try:
                raw = self._fernet.decrypt(raw)
            except InvalidToken:
                raise PermissionError("Cookie state decryption failed. Wrong ENCRYPTION_KEY?")
        return json.loads(raw.decode("utf-8"))

    def _ensure_live(self, session_id: str) -> _LiveSession:
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError("Unknown session_id. Start with /auth/login.")
            return self._sessions[session_id]

    def _close(self, session_id: str) -> None:
        with self._lock:
            sess = self._sessions.pop(session_id, None)
        if not sess:
            return
        # Close outside the lock
        try:
            sess.context.close()
        except Exception:
            pass
        try:
            sess.browser.close()
        except Exception:
            pass

    # ----- actions -----

    def _start_login(self, login_url: str) -> dict:
        parsed = urlparse(login_url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("login_url must be http(s)")

        session_id = self._gen_session_id()

        def worker():
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
                page.goto(login_url, wait_until="domcontentloaded")
                with self._lock:
                    self._sessions[session_id] = _LiveSession(
                        session_id=session_id,
                        browser=browser,
                        context=context,
                        created_at=time.time(),
                    )
                # Keep the thread alive until commit/close tears it down
                while True:
                    time.sleep(1)

        t = threading.Thread(target=worker, name=f"login-{session_id}", daemon=True)
        t.start()

        return {
            "session_id": session_id,
            "message": "Browser launched. Complete login, then call commit(session_id).",
        }

    def _commit(self, session_id: str) -> Path:
        sess = self._ensure_live(session_id)
        path = self._state_path(session_id)
        state = sess.context.storage_state()
        self._write_state(path, state)
        self._close(session_id)
        return path

    def _status(self, session_id: str) -> dict:
        with self._lock:
            in_memory = session_id in self._sessions
        state_exists = self._state_path(session_id).exists()
        return {"in_memory": in_memory, "state_saved": state_exists}

    def _build_requests_session_from_state(self, state: dict) -> requests.Session:
        s = requests.Session()
        s.headers.update({"User-Agent": self._ua})
        for c in state.get("cookies", []):
            domain = (c.get("domain") or "").lstrip(".")
            cookie = requests.cookies.create_cookie(
                name=c["name"],
                value=c["value"],
                domain=domain or None,
                path=c.get("path", "/"),
                secure=bool(c.get("secure", False)),
                expires=c.get("expires"),
                rest={"HttpOnly": bool(c.get("httpOnly", False))},
            )
            s.cookies.set_cookie(cookie)
        return s

    def _scrape(self, session_id: str, url: str) -> Tuple[int, dict]:
        path = self._state_path(session_id)
        if not path.exists():
            return 401, {"error": "No saved cookies for this session_id. Run start_login → commit first."}

        state = self._read_state(path)
        s = self._build_requests_session_from_state(state)
        r = s.get(url, timeout=30)
        if r.status_code in (401, 403):
            return 401, {"error": f"Unauthorized ({r.status_code}). Cookies may be expired or scoped to another domain."}
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        title_el = soup.select_one("title")
        title = title_el.get_text(strip=True) if title_el else None
        links = [
            {"text": a.get_text(strip=True), "href": a.get("href")}
            for a in soup.select("a[href]")
        ][:25]

        return 200, {
            "status": r.status_code,
            "title": title,
            "content_length": len(r.text),
            "sample_links": links,
        }

    # ----- optional maintenance -----

    def purge_zombies(self) -> None:
        """Best-effort cleanup of sessions whose contexts were already closed."""
        with self._lock:
            dead = []
            for sid, live in self._sessions.items():
                try:
                    _ = live.context.pages  # touch
                except Exception:
                    dead.append(sid)
            for sid in dead:
                self._sessions.pop(sid, None)


# --------- module-level singleton + convenience ---------

# Build from environment for convenience; routes can import `main` directly.
_MANAGER = SessionManager(
    storage_dir=os.getenv("STORAGE_DIR", "data"),
    encryption_key=os.getenv("ENCRYPTION_KEY"),
)

def main(action: str, **kwargs: Any) -> Tuple[int, dict]:
    """
    Public entrypoint for routes.py - thin wrapper around SessionManager.main().
    """
    return _MANAGER.main(action, **kwargs)

if __name__ == "__main__":
    # For testing purposes only
    import sys
    url = "https://learn.uq.edu.au/"
    action = sys.argv[1] if len(sys.argv) > 1 else "start_login"
    # include url
    kwargs = {"login_url": url}
    kwargs.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    status, payload = main(action, **kwargs)
    print(f"Status: {status}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    