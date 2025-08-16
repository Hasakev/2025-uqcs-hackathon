from __future__ import annotations
import base64, threading, time, requests
from typing import Optional

class TokenManager:
    """
    Caches Anthology (Blackboard) tokens in-memory with auto refresh.
    - 2LO: single, app-level token (client_credentials)
    - 3LO: optional per-session storage (dict) if you choose to keep tokens server-side
    """
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret

        # 2LO cache
        self._lock = threading.Lock()
        self._two_lo_token: Optional[str] = None
        self._two_lo_expiry: float = 0.0  # epoch seconds

        # Optional: 3LO store (session_id -> {access, refresh, exp})
        self._3lo = {}
        self._3lo_lock = threading.Lock()

    # ===== 2LO (app token) =====
    def _fetch_2lo(self) -> tuple[str, int]:
        url = f"{self.base_url}/learn/api/public/v1/oauth2/token"
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        r = requests.post(
            url,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
            timeout=20,
        )
        r.raise_for_status()
        j = r.json()
        return j["access_token"], int(j.get("expires_in", 3600))

    def get_2lo_token(self) -> str:
        # Refresh if missing or expiring in <30s
        with self._lock:
            now = time.time()
            if not self._two_lo_token or (self._two_lo_expiry - now) < 30:
                token, ttl = self._fetch_2lo()
                self._two_lo_token = token
                self._two_lo_expiry = now + ttl
            return self._two_lo_token

    # ===== 3LO (optional server-side store) =====
    def save_3lo(self, session_id: str, access: str, expires_in: int=3600, refresh: str | None=None):
        with self._3lo_lock:
            self._3lo[session_id] = {
                "access": access,
                "exp": time.time() + max(30, expires_in - 30),
                "refresh": refresh,
            }

    def get_3lo_access(self, session_id: str) -> Optional[str]:
        with self._3lo_lock:
            rec = self._3lo.get(session_id)
            if not rec:
                return None
            if rec["exp"] > time.time():
                return rec["access"]
            # could auto-refresh here if refresh token exists
            return None

    def clear_3lo(self, session_id: str):
        with self._3lo_lock:
            self._3lo.pop(session_id, None)
            
    def refresh_3lo_if_needed(self, session_id: str) -> str | None:
        rec = None
        with self._3lo_lock:
            rec = self._3lo.get(session_id)
        print(f"Refreshing 3LO for {session_id}: {rec}")
        if not rec:
            return None
        
        # Still valid?
        if rec["exp"] > time.time():
            return rec["access"]
        print("Tp2")
        # No refresh token -> can’t refresh
        rt = rec.get("refresh")
        if not rt:
            return None

        # Do refresh
        url = f"{self.base_url}/learn/api/public/v1/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": rt,
        }
        r = requests.post(url, data=data, timeout=20)
        if not r.ok:
            # refresh failed; remove session
            self.clear_3lo(session_id)
            return None

        j = r.json()
        access = j.get("access_token")
        expires_in = int(j.get("expires_in", 3600))
        new_rt = j.get("refresh_token", rt)  # sometimes unchanged
        self.save_3lo(session_id, access, expires_in, new_rt)
        return access
