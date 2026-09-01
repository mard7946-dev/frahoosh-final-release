from threading import Thread

from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.metrics import dp

from mobile.config import (
    APP_NAME,
    SYSTEM_TITLE,
    LOGO_PATH,
    PRIMARY,
    SECONDARY,
)

from mobile.ui import font_name, rtl_text


class LoadingScreen(Screen):

    def __init__(self, app_state, **kwargs):

        super().__init__(**kwargs)

        self.app_state = app_state
        self._finished = False

        self.add_widget(
            self._build()
        )

        Clock.schedule_once(
            self._start_auth_check,
            0.65,
        )

    # ========================================================
    # UI
    # ========================================================

    def _build(self):

        root = BoxLayout(
            orientation="vertical",
            padding=dp(28),
            spacing=dp(12),
        )

        root.add_widget(
            BoxLayout(
                size_hint_y=0.22
            )
        )

        from pathlib import Path

        if Path(LOGO_PATH).exists():

            root.add_widget(
                Image(
                    source=LOGO_PATH,
                    size_hint_y=None,
                    height=dp(150),
                    allow_stretch=True,
                    keep_ratio=True,
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
                height=dp(60),
            )
        )

        root.add_widget(
            Label(
                text=rtl_text(SYSTEM_TITLE),
                font_name=font_name(),
                font_size="16sp",
                color=SECONDARY,
                size_hint_y=None,
                height=dp(45),
            )
        )

        self.status = Label(
            text=rtl_text(
                "در حال آماده‌سازی برنامه..."
            ),
            font_name=font_name(),
            font_size="13sp",
            color=SECONDARY,
            size_hint_y=None,
            height=dp(36),
        )

        root.add_widget(
            self.status
        )

        root.add_widget(
            BoxLayout(
                size_hint_y=0.45
            )
        )

        return root

    # ========================================================
    # Authentication Check
    # ========================================================

    def _start_auth_check(self, *_):

        if self._finished:
            return

        self.status.text = rtl_text(
            "در حال بررسی نشست کاربر..."
        )

        Thread(
            target=self._auth_worker,
            daemon=True,
        ).start()

    # ========================================================
    # Worker
    # ========================================================

    def _auth_worker(self):

        try:

            # ------------------------------------------------
            # هیچ Sessionای وجود ندارد
            # ------------------------------------------------

            if not self.app_state.logged_in:

                Clock.schedule_once(
                    lambda dt:
                        self._go_login(),
                    0,
                )

                return

            # ------------------------------------------------
            # Session وجود دارد.
            #
            # ابتدا Token فعلی را امتحان می‌کنیم.
            # اگر API قابلیت بررسی/Refresh داشته باشد،
            # Refresh انجام می‌شود.
            # ------------------------------------------------

            refreshed = False

            try:

                if (
                    self.app_state.api.refresh_token
                    and hasattr(
                        self.app_state.api,
                        "refresh_access_token",
                    )
                ):

                    refreshed = (
                        self.app_state.refresh_session()
                    )

            except Exception:

                refreshed = False

            # ------------------------------------------------
            # اگر Refresh موفق بود → Dashboard
            # ------------------------------------------------

            if refreshed:

                Clock.schedule_once(
                    lambda dt:
                        self._go_dashboard(),
                    0,
                )

                return

            # ------------------------------------------------
            # اگر Access Token قبلی وجود دارد ولی
            # Refresh انجام نشد، فعلاً Session را نگه
            # می‌داریم و Dashboard را باز می‌کنیم.
            #
            # درخواست‌های API در صورت 401 باید بعداً
            # Refresh/Logout را مدیریت کنند.
            # ------------------------------------------------

            if self.app_state.logged_in:

                Clock.schedule_once(
                    lambda dt:
                        self._go_dashboard(),
                    0,
                )

                return

            # ------------------------------------------------
            # Session نامعتبر
            # ------------------------------------------------

            Clock.schedule_once(
                lambda dt:
                    self._go_login(),
                0,
            )

        except Exception:

            Clock.schedule_once(
                lambda dt:
                    self._go_login(),
                0,
            )

    # ========================================================
    # Navigation
    # ========================================================

    def _go_dashboard(self):

        if self._finished:
            return

        self._finished = True

        self.manager.current = (
            "dashboard"
        )

    def _go_login(self):

        if self._finished:
            return

        self._finished = True

        self.manager.current = (
            "login"
        )

