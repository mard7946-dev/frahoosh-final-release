from mobile.services.api import SupabaseClient
from mobile.services.session import (
    load_session,
    save_session,
    clear_session,
    update_session_tokens,
)


class AppState:

    def __init__(self):
        self.api = SupabaseClient()

        try:
            self.session = load_session() or {}
        except Exception:
            self.session = {}

        self._load_tokens()

    # ========================================================
    # Session / Token
    # ========================================================

    def _load_tokens(self):
        """بارگذاری Tokenها از Session ذخیره‌شده."""

        self.api.access_token = (
            self.session.get("access_token", "")
            if self.session
            else ""
        )

        self.api.refresh_token = (
            self.session.get("refresh_token", "")
            if self.session
            else ""
        )

        self.api.expires_in = (
            self.session.get("expires_in")
            if self.session
            else None
        )

        self.api.expires_at = (
            self.session.get("expires_at")
            if self.session
            else None
        )

        self.api.token_type = (
            self.session.get(
                "token_type",
                "bearer"
            )
            if self.session
            else "bearer"
        )

    # ========================================================
    # Login State
    # ========================================================

    @property
    def logged_in(self):
        return bool(
            self.session
            and self.api.access_token
        )

    # ========================================================
    # Profile
    # ========================================================

    @property
    def profile(self):
        return (
            self.session.get("profile") or {}
            if self.session
            else {}
        )

    @property
    def role(self):
        return str(
            self.profile.get("role")
            or "student"
        ).strip().lower()

    @property
    def display_name(self):
        return (
            self.profile.get("display_name")
            or self.profile.get("username")
            or self.profile.get("full_name")
            or "کاربر فراهوش"
        )

    # ========================================================
    # Set Session
    # ========================================================

    def set_session(self, payload):

        payload = payload or {}

        access_token = payload.get(
            "access_token",
            ""
        )

        refresh_token = payload.get(
            "refresh_token",
            ""
        )

        if not access_token:
            self.session = {}
            self.api.access_token = ""
            self.api.refresh_token = ""
            clear_session()
            return False

        self.session = dict(payload)

        save_session(
            self.session
        )

        self._load_tokens()

        return True

    # ========================================================
    # Save Refreshed Token
    # ========================================================

    def persist_refreshed_token(self):

        """
        ذخیره Token جدیدی که Supabase بعد از
        refresh در اختیار برنامه قرار داده است.
        """

        if not self.api.access_token:
            return False

        if not self.session:
            self.session = {}

        self.session["access_token"] = (
            self.api.access_token
        )

        if self.api.refresh_token:
            self.session["refresh_token"] = (
                self.api.refresh_token
            )

        if self.api.expires_in is not None:
            self.session["expires_in"] = (
                self.api.expires_in
            )

        if self.api.expires_at is not None:
            self.session["expires_at"] = (
                self.api.expires_at
            )

        if self.api.token_type:
            self.session["token_type"] = (
                self.api.token_type
            )

        return save_session(
            self.session
        )

    # ========================================================
    # Refresh Session
    # ========================================================

    def refresh_session(self):

        """
        تلاش برای تمدید نشست با Refresh Token.
        """

        if not self.api.refresh_token:
            return False

        refreshed = (
            self.api.refresh_access_token()
        )

        if not refreshed:
            return False

        return self.persist_refreshed_token()

    # ========================================================
    # Logout
    # ========================================================

    def logout(self):

        try:
            self.api.sign_out()
        except Exception:
            pass

        clear_session()

        self.session = {}

        self.api.access_token = ""
        self.api.refresh_token = ""
        self.api.expires_in = None
        self.api.expires_at = None
        self.api.token_type = "bearer"

        return True
