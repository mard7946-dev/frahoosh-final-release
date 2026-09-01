from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from mobile.config import APP_NAME, BACKGROUND
from mobile.services.app_state import AppState
from mobile.ui import register_fonts
from mobile.screens.loading import LoadingScreen
from mobile.screens.login import LoginScreen
from mobile.screens.dashboard import DashboardScreen
from mobile.screens.module import ModuleScreen
from mobile.screens.update import UpdateScreen


class FrahooshMobileApp(App):
    title = APP_NAME

    def build(self):
        Window.clearcolor = BACKGROUND
        register_fonts()
        self.state = AppState()
        manager = ScreenManager(transition=FadeTransition(duration=0.12))
        manager.add_widget(LoadingScreen(self.state, name="loading"))
        manager.add_widget(LoginScreen(self.state, name="login"))
        manager.add_widget(DashboardScreen(self.state, name="dashboard"))
        manager.add_widget(ModuleScreen(self.state, name="module"))
        manager.add_widget(UpdateScreen(self.state, name="update"))
        manager.current = "loading"
        return manager


if __name__ == "__main__":
    FrahooshMobileApp().run()
