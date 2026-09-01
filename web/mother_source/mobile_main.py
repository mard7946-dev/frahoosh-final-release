# ============================================================
# Frahoosh Mobile
# نقطه شروع نسخه موبایل
# ============================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.login import LoginScreen
from screens.dashboard import DashboardScreen
from screens.update import UpdateScreen


class FrahooshMobileApp(App):

    def build(self):

        manager = ScreenManager()

        manager.add_widget(
            LoginScreen(name="login")
        )

        manager.add_widget(
            DashboardScreen(name="dashboard")
        )

        manager.add_widget(
            UpdateScreen(name="update")
        )

        manager.current = "login"

        return manager


if __name__ == "__main__":
    FrahooshMobileApp().run()