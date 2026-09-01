from threading import Thread

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.metrics import dp

from mobile.config import (
    APP_NAME,
    SYSTEM_TITLE,
    SCHOOL_NAME,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    WHITE,
    ERROR,
)

from mobile.ui import font_name, rtl_text


class LoginScreen(Screen):

    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)

        self.app_state = app_state
        self._busy = False

        self._build()

    # ========================================================
    # UI
    # ========================================================

    def _build(self):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(10),
        )

        root.add_widget(
            BoxLayout(
                size_hint_y=0.08
            )
        )

        root.add_widget(
            Label(
                text=rtl_text(APP_NAME),
                font_name=font_name(),
                font_size="34sp",
                bold=True,
                color=PRIMARY,
                size_hint_y=None,
                height=dp(52),
            )
        )

        root.add_widget(
            Label(
                text=rtl_text(SYSTEM_TITLE),
                font_name=font_name(),
                font_size="17sp",
                color=SECONDARY,
                size_hint_y=None,
                height=dp(40),
            )
        )

        root.add_widget(
            Label(
                text=rtl_text(SCHOOL_NAME),
                font_name=font_name(),
                font_size="13sp",
                color=PRIMARY,
                size_hint_y=None,
                height=dp(34),
            )
        )

        card = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(18),
            size_hint_y=None,
            height=dp(300),
        )

        self.identifier = TextInput(
            hint_text=rtl_text("ایمیل کاربر"),
            font_name=font_name(),
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(52),
            padding=[
                dp(12),
                dp(14),
                dp(12),
                dp(14),
            ],
        )

        self.password = TextInput(
            hint_text=rtl_text("رمز عبور"),
            font_name=font_name(),
            password=True,
            multiline=False,
            write_tab=False,
            size_hint_y=None,
            height=dp(52),
            padding=[
                dp(12),
                dp(14),
                dp(12),
                dp(14),
            ],
        )

        self.status = Label(
            text="",
            font_name=font_name(),
            font_size="12sp",
            color=SECONDARY,
            halign="center",
            text_size=(None, None),
            size_hint_y=None,
            height=dp(44),
        )

        self.login_button = Button(
            text=rtl_text("ورود به فراهوش"),
            font_name=font_name(),
            font_size="15sp",
            background_normal="",
            background_color=SUCCESS,
            color=WHITE,
            size_hint_y=None,
            height=dp(54),
        )

        self.login_button.bind(
            on_release=self.login
        )

        card.add_widget(self.identifier)
        card.add_widget(self.password)
        card.add_widget(self.status)
        card.add_widget(self.login_button)

        root.add_widget(card)

        root.add_widget(
            Label(
                text=rtl_text(
                    "ورود با حساب سازمانی فراهوش و Supabase انجام می‌شود."
                ),
                font_name=font_name(),
                font_size="11sp",
                color=SECONDARY,
                halign="center",
            )
        )

        root.add_widget(
            BoxLayout(
                size_hint_y=0.2
            )
        )

        self.add_widget(root)

    # ========================================================
    # Login
    # ========================================================

    def login(self, *_):

        if self._busy:
            return

        identifier = (
            self.identifier.text or ""
        ).strip()

        password = (
            self.password.text or ""
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        if not identifier or not password:

            self._set_status(
                "ایمیل و رمز عبور را وارد کنید.",
                ERROR,
            )

            return

        # ----------------------------------------------------
        # Supabase configuration
        # ----------------------------------------------------

        if not self.app_state.api.configured:

            self._set_status(
                "تنظیمات اتصال به Supabase برای این Build وارد نشده است.",
                ERROR,
            )

            return

        # ----------------------------------------------------
        # Start login
        # ----------------------------------------------------

        self._busy = True

        self.login_button.disabled = True

        self.login_button.text = rtl_text(
            "در حال ورود..."
        )

        self._set_status(
            "در حال اتصال به سرور...",
            SECONDARY,
        )

        Thread(
            target=self._login_worker,
            args=(identifier, password),
            daemon=True,
        ).start()

    # ========================================================
    # Login Worker
    # ========================================================

    def _login_worker(
        self,
        identifier,
        password,
    ):

        try:

            payload = (
                self.app_state.api.sign_in(
                    identifier,
                    password,
                )
            )

            Clock.schedule_once(
                lambda dt: self._login_success(
                    payload
                ),
                0,
            )

        except Exception as exc:

            message = (
                str(exc).strip()
                or
                "ورود ناموفق بود. اتصال اینترنت و اطلاعات ورود را بررسی کنید."
            )

            Clock.schedule_once(
                lambda dt, m=message:
                    self._login_failed(m),
                0,
            )

    # ========================================================
    # Login Success
    # ========================================================

    def _login_success(self, payload):

        try:

            # ------------------------------------------------
            # ذخیره کامل Session
            # ------------------------------------------------

            saved = (
                self.app_state.set_session(
                    payload
                )
            )

            if not saved:

                raise RuntimeError(
                    "نشست کاربر ذخیره نشد."
                )

            # ------------------------------------------------
            # پاک کردن رمز از فرم
            # ------------------------------------------------

            self.password.text = ""

            # ------------------------------------------------
            # Refresh Dashboard
            # ------------------------------------------------

            try:

                dashboard = (
                    self.manager.get_screen(
                        "dashboard"
                    )
                )

                if hasattr(
                    dashboard,
                    "refresh"
                ):
                    dashboard.refresh()

            except Exception:
                pass

            # ------------------------------------------------
            # Finish
            # ------------------------------------------------

            self._busy = False

            self.login_button.disabled = False

            self.login_button.text = rtl_text(
                "ورود به فراهوش"
            )

            self.status.text = ""

            self.manager.current = "dashboard"

        except Exception as exc:

            self._login_failed(
                str(exc).strip()
                or
                "ورود انجام شد اما ذخیره نشست کاربر ناموفق بود."
            )

    # ========================================================
    # Login Failed
    # ========================================================

    def _login_failed(self, message):

        self._busy = False

        self.login_button.disabled = False

        self.login_button.text = rtl_text(
            "ورود به فراهوش"
        )

        self._set_status(
            message,
            ERROR,
        )

    # ========================================================
    # Status
    # ========================================================

    def _set_status(
        self,
        message,
        color,
    ):

        self.status.color = color

        self.status.text = rtl_text(
            message or ""
        )


