 import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from mobile.config import SUPABASE_URL, SUPABASE_ANON_KEY, API_TIMEOUT


class ApiError(RuntimeError):
    pass


class _Response:
    def __init__(self, status, body):
        self.status_code = status
        self._body = body or b""

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        if not self._body:
            return {}
        return json.loads(self._body.decode("utf-8"))

    def text(self):
        return self._body.decode("utf-8", errors="replace")


def _request(method, url, headers=None, payload=None, params=None, timeout=15):
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)

    data = None
    req_headers = dict(headers or {})

    if payload is not None:
        data = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

        req_headers["Content-Type"] = "application/json"

    request = Request(
        url,
        data=data,
        headers=req_headers,
        method=method
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            return _Response(
                response.status,
                response.read()
            )

    except HTTPError as exc:
        return _Response(
            exc.code,
            exc.read()
        )

    except URLError as exc:
        raise ApiError(
            f"خطای اتصال به سرور: {exc.reason}"
        ) from exc

    except TimeoutError as exc:
        raise ApiError(
            "زمان اتصال به سرور به پایان رسید."
        ) from exc


class SupabaseClient:

    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_ANON_KEY

        self.access_token = ""
        self.refresh_token = ""

        # اطلاعات تکمیلی نشست
        self.expires_in = None
        self.expires_at = None
        self.token_type = "bearer"

    @property
    def configured(self):
        return bool(
            self.url and
            self.key
        )

    # ---------------------------------------------------------
    # Headers
    # ---------------------------------------------------------

    def _headers(self, authenticated=False):

        headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }

        if authenticated and self.access_token:
            headers["Authorization"] = (
                f"Bearer {self.access_token}"
            )

        return headers

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------

    def sign_in(self, identifier, password):

        if not self.configured:
            raise ApiError(
                "اتصال سرور در تنظیمات این نسخه فعال نشده است."
            )

        identifier = (identifier or "").strip()

        if not identifier or not password:
            raise ApiError(
                "نام کاربری و رمز عبور را وارد کنید."
            )

        response = _request(
            "POST",
            f"{self.url}/auth/v1/token"
            "?grant_type=password",

            headers=self._headers(),

            payload={
                "email": identifier,
                "password": password
            },

            timeout=API_TIMEOUT
        )

        if not response.ok:
            raise ApiError(
                self._error(
                    response,
                    "ایمیل یا رمز عبور صحیح نیست."
                )
            )

        data = response.json() or {}

        self.access_token = data.get(
            "access_token",
            ""
        )

        self.refresh_token = data.get(
            "refresh_token",
            ""
        )

        self.expires_in = data.get(
            "expires_in"
        )

        self.expires_at = data.get(
            "expires_at"
        )

        self.token_type = data.get(
            "token_type",
            "bearer"
        )

        # نشست بدون Access Token معتبر نیست
        if not self.access_token:
            self.access_token = ""
            self.refresh_token = ""

            raise ApiError(
                "سرور نشست معتبر ایجاد نکرد."
            )

        user = data.get("user") or {}

        return {
            "user": user,

            "profile": self._profile(user),

            "access_token": self.access_token,

            "refresh_token": self.refresh_token,

            "expires_in": self.expires_in,

            "expires_at": self.expires_at,

            "token_type": self.token_type
        }

    # ---------------------------------------------------------
    # Refresh Token
    # ---------------------------------------------------------

    def refresh_access_token(self):

        if not self.configured:
            return False

        if not self.refresh_token:
            return False

        response = _request(
            "POST",
            f"{self.url}/auth/v1/token"
            "?grant_type=refresh_token",

            headers=self._headers(),

            payload={
                "refresh_token": self.refresh_token
            },

            timeout=API_TIMEOUT
        )

        if not response.ok:
            self.access_token = ""
            self.refresh_token = ""
            self.expires_in = None
            self.expires_at = None

            return False

        data = response.json() or {}

        new_access_token = data.get(
            "access_token"
        )

        if not new_access_token:
            self.access_token = ""
            self.refresh_token = ""

            return False

        self.access_token = new_access_token

        # Supabase ممکن است Refresh Token جدید بدهد.
        new_refresh_token = data.get(
            "refresh_token"
        )

        if new_refresh_token:
            self.refresh_token = new_refresh_token

        self.expires_in = data.get(
            "expires_in"
        )

        self.expires_at = data.get(
            "expires_at"
        )

        self.token_type = data.get(
            "token_type",
            self.token_type or "bearer"
        )

        return True

    # ---------------------------------------------------------
    # Profile
    # ---------------------------------------------------------

    def _profile(self, user):

        metadata = (
            user.get("user_metadata") or {}
        )

        profile = {}

        for key in (
            "role",
            "display_name",
            "full_name",
            "username"
        ):

            if key in metadata:
                profile[key] = metadata[key]

        email = user.get(
            "email",
            ""
        )

        if not self.configured or not email:

            profile.setdefault(
                "email",
                email
            )

            return profile

        try:

            response = _request(
                "GET",
                f"{self.url}/rest/v1/account_settings",

                headers=self._headers(True),

                params={
                    "email": f"eq.{email}",
                    "limit": "1"
                },

                timeout=API_TIMEOUT
            )

            if response.ok:

                rows = response.json() or []

                if rows and isinstance(
                    rows[0],
                    dict
                ):

                    merged = dict(profile)

                    merged.update(
                        rows[0]
                    )

                    return merged

        except Exception:
            pass

        profile.setdefault(
            "email",
            email
        )

        profile.setdefault(
            "username",
            email
        )

        profile.setdefault(
            "display_name",
            email
        )

        return profile

    # ---------------------------------------------------------
    # Database SELECT
    # ---------------------------------------------------------

    def table_select(
        self,
        table,
        params=None
    ):

        if not self.configured:
            raise ApiError(
                "اتصال سرور فعال نیست."
            )

        if not self.access_token:
            raise ApiError(
                "نشست معتبر نیست."
            )

        request_params = (
            params or
            {
                "select": "*",
                "limit": "50"
            }
        )

        response = _request(
            "GET",
            f"{self.url}/rest/v1/{table}",

            headers=self._headers(True),

            params=request_params,

            timeout=API_TIMEOUT
        )

        # -----------------------------------------------------
        # Access Token expired
        # -----------------------------------------------------

        if (
            response.status_code == 401
            and self.refresh_token
        ):

            refreshed = (
                self.refresh_access_token()
            )

            if refreshed:

                # درخواست اصلی را یک بار دیگر
                # با Access Token جدید اجرا می‌کنیم.

                response = _request(
                    "GET",
                    f"{self.url}/rest/v1/{table}",

                    headers=self._headers(True),

                    params=request_params,

                    timeout=API_TIMEOUT
                )

        if not response.ok:

            raise ApiError(
                self._error(
                    response
                )
            )

        return response.json()

    # ---------------------------------------------------------
    # Error Handler
    # ---------------------------------------------------------

    def _error(
        self,
        response,
        default="خطای سرور"
    ):

        try:

            payload = (
                response.json() or {}
            )

            return (
                payload.get("message")
                or payload.get(
                    "error_description"
                )
                or payload.get("msg")
                or payload.get("hint")
                or payload.get("details")
                or default
            )

        except Exception:

            return (
                f"{default} "
                f"({response.status_code})"
            )

    # ---------------------------------------------------------
    # Logout
    # ---------------------------------------------------------

    def sign_out(self):

        if (
            self.configured
            and self.access_token
        ):

            try:

                _request(
                    "POST",
                    f"{self.url}/auth/v1/logout",

                    headers=self._headers(True),

                    timeout=API_TIMEOUT
                )

            except Exception:
                pass

        # پاک‌سازی کامل نشست

        self.access_token = ""
        self.refresh_token = ""

        self.expires_in = None
        self.expires_at = None
        self.token_type = "bearer"

           
