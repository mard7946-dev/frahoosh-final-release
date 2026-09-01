import json
from pathlib import Path


# ============================================================
# Frahoosh Mobile
# Session Storage
# ============================================================

SESSION_FILE = (
    Path(__file__).resolve().parent.parent
    / "storage"
    / "session.json"
)


def save_session(data: dict):
    """
    ذخیره نشست کاربر.

    اطلاعاتی که از Supabase دریافت می‌شوند،
    شامل access_token، refresh_token و اطلاعات پروفایل
    در این فایل ذخیره می‌شوند.
    """

    if not isinstance(data, dict):
        return False

    try:
        SESSION_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        SESSION_FILE.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                separators=(",", ":")
            ),
            encoding="utf-8"
        )

        return True

    except (
        OSError,
        TypeError,
        ValueError
    ):
        return False


def load_session():
    """
    بازیابی نشست قبلی کاربر.

    اگر فایل وجود نداشته باشد،
    خراب باشد یا Access Token نداشته باشد،
    نشست معتبر محسوب نمی‌شود.
    """

    try:

        if not SESSION_FILE.exists():
            return None

        raw = SESSION_FILE.read_text(
            encoding="utf-8"
        )

        data = json.loads(raw)

        if not isinstance(data, dict):
            return None

        # بدون Access Token نشست قابل استفاده نیست.
        if not data.get("access_token"):
            return None

        return data

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        OSError,
        TypeError,
        ValueError
    ):
        return None


def update_session_tokens(
    access_token,
    refresh_token=None,
    expires_in=None,
    expires_at=None,
    token_type=None
):
    """
    به‌روزرسانی Tokenهای نشست بعد از Refresh.

    Session قبلی حفظ می‌شود و فقط اطلاعات Token
    به‌روزرسانی می‌شوند.
    """

    session = load_session()

    if not session:
        session = {}

    if access_token:
        session["access_token"] = access_token

    if refresh_token:
        session["refresh_token"] = refresh_token

    if expires_in is not None:
        session["expires_in"] = expires_in

    if expires_at is not None:
        session["expires_at"] = expires_at

    if token_type:
        session["token_type"] = token_type

    return save_session(session)


def clear_session():
    """
    خروج کامل کاربر و حذف Session ذخیره‌شده.
    """

    try:

        if SESSION_FILE.exists():
            SESSION_FILE.unlink()

        return True

    except OSError:
        return False
