from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from mobile.config import PRIMARY, SECONDARY, SUCCESS, WHITE, MUTED
from mobile.ui import font_name, rtl_text


class ModuleScreen(Screen):
    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        self.root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))
        self.title = Label(font_name=font_name(), font_size="24sp", color=PRIMARY, size_hint_y=None, height=dp(60))
        self.info = Label(font_name=font_name(), font_size="14sp", color=SECONDARY, halign="right", valign="top")
        self.info.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.root.add_widget(self.title); self.root.add_widget(self.info)
        back = Button(text=rtl_text("بازگشت به پنل"), font_name=font_name(), background_normal="", background_color=SUCCESS, color=WHITE, size_hint_y=None, height=dp(54))
        back.bind(on_release=lambda *_: setattr(self.manager, "current", "dashboard"))
        self.root.add_widget(back)
        self.add_widget(self.root)

    def show_module(self, name, role):
        self.title.text = rtl_text(name)
        role_label = {"manager":"مدیریت", "admin":"مدیریت", "executive":"معاون اجرایی", "educational":"معاون آموزشی", "teacher":"دبیر", "advisor":"مشاور", "counselor":"مشاور", "student":"دانش‌آموز", "parent":"ولی", "parent_guardian":"ولی"}.get(role, role)
        self.info.text = rtl_text(
            f"پنل {name}\n\n"
            f"نقش فعال: {role_label}\n\n"
            "هسته موبایل و مسیر ناوبری این بخش آماده است. اتصال داده این ماژول باید بر اساس جدول و مجوز همان بخش در Backend انجام شود؛ از ساختن جدول فرضی یا داده جعلی خودداری می‌شود."
        )
