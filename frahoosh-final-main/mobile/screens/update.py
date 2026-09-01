from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from mobile.config import APP_NAME, APP_VERSION, PRIMARY, SECONDARY, SUCCESS, WHITE
from mobile.ui import font_name, rtl_text


class UpdateScreen(Screen):
    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        root = BoxLayout(orientation="vertical", padding=dp(22), spacing=dp(14))
        self.title = Label(text=rtl_text("مرکز به‌روزرسانی فراهوش"), font_name=font_name(), font_size="24sp", color=PRIMARY, size_hint_y=None, height=dp(60))
        self.info = Label(font_name=font_name(), font_size="14sp", color=SECONDARY, halign="right", valign="top")
        self.info.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(self.title); root.add_widget(self.info)
        back = Button(text=rtl_text("بازگشت"), font_name=font_name(), background_normal="", background_color=SUCCESS, color=WHITE, size_hint_y=None, height=dp(54))
        back.bind(on_release=self.go_back); root.add_widget(back)
        self.add_widget(root); self.refresh()

    def refresh(self):
        state = "متصل به Backend" if self.app_state.api.configured else "Backend در این Build پیکربندی نشده است"
        self.info.text = rtl_text(f"نسخه نصب‌شده: {APP_VERSION}\n{state}\n\nبه‌روزرسانی رسمی در نسخه نهایی باید از مسیر امن انتشار فراهوش انجام شود.")

    def go_back(self, *_):
        if self.manager: self.manager.current = "dashboard"
