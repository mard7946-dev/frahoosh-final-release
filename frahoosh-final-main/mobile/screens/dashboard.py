from kivy.uix.screen import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from mobile.config import APP_NAME, PRIMARY, SECONDARY, SUCCESS, WHITE, MUTED, ERROR
from mobile.ui import font_name, rtl_text

ROLE_LABELS = {
    "manager": "مدیریت", "admin": "مدیریت", "مدیر": "مدیریت",
    "executive": "معاون اجرایی", "educational": "معاون آموزشی", "پرورشی": "معاون پرورشی",
    "teacher": "دبیر", "advisor": "مشاور", "counselor": "مشاور",
    "student": "دانش‌آموز", "parent": "ولی", "parent_guardian": "ولی",
}

ROLE_MODULES = {
    "manager": ["مدیریت مدرسه", "کلاس‌ها و برنامه هفتگی", "امتحانات", "گزارش عملکرد", "پیام‌ها", "تخلف و انضباط"],
    "admin": ["مدیریت مدرسه", "کلاس‌ها و برنامه هفتگی", "امتحانات", "گزارش عملکرد", "پیام‌ها", "تخلف و انضباط"],
    "executive": ["امور اجرایی", "کلاس‌ها", "حضور و غیاب", "گزارش‌ها", "پیام‌ها", "پرونده دانش‌آموز"],
    "educational": ["امور آموزشی", "کلاس‌ها", "برنامه هفتگی", "امتحانات", "نمرات", "گزارش عملکرد"],
    "teacher": ["کلاس‌های من", "حضور و غیاب", "نمرات", "آزمون‌ها", "برنامه هفتگی", "پیام‌ها"],
    "advisor": ["پرونده مشاوره", "جلسات", "گزارش‌ها", "پیام‌ها", "دانش‌آموزان"],
    "counselor": ["پرونده مشاوره", "جلسات", "گزارش‌ها", "پیام‌ها", "دانش‌آموزان"],
    "student": ["کلاس من", "برنامه هفتگی", "امتحانات", "نمرات", "حضور و غیاب", "مسابقات و فعالیت‌ها"],
    "parent": ["فرزندان من", "نمرات", "حضور و غیاب", "امتحانات", "پیام‌ها", "پرداخت‌ها"],
    "parent_guardian": ["فرزندان من", "نمرات", "حضور و غیاب", "امتحانات", "پیام‌ها", "پرداخت‌ها"],
}


class DashboardScreen(Screen):
    def __init__(self, app_state, **kwargs):
        super().__init__(**kwargs)
        self.app_state = app_state
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        self.header = Label(font_name=font_name(), font_size="20sp", color=PRIMARY, halign="right", valign="middle", size_hint_y=None, height=dp(78))
        self.header.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        root.add_widget(self.header)
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self.grid = GridLayout(cols=2, spacing=dp(9), padding=[0, dp(4)], size_hint_y=None, row_default_height=dp(58))
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        root.add_widget(scroll)
        self.add_widget(root)
        self.refresh()

    def refresh(self):
        self.grid.clear_widgets()
        role = self.app_state.role
        label = ROLE_LABELS.get(role, role or "کاربر")
        self.header.text = rtl_text(f"{APP_NAME}\n{self.app_state.display_name} — {label}")
        modules = ROLE_MODULES.get(role, ROLE_MODULES["student"])
        for module in modules:
            button = Button(text=rtl_text(module), font_name=font_name(), font_size="13sp", background_normal="", background_color=SECONDARY, color=WHITE)
            button.bind(on_release=lambda _btn, name=module: self.open_module(name))
            self.grid.add_widget(button)
        update = Button(text=rtl_text("مرکز به‌روزرسانی"), font_name=font_name(), background_normal="", background_color=SUCCESS, color=WHITE)
        update.bind(on_release=self.open_update); self.grid.add_widget(update)
        logout = Button(text=rtl_text("خروج از حساب"), font_name=font_name(), background_normal="", background_color=PRIMARY, color=WHITE)
        logout.bind(on_release=self.logout); self.grid.add_widget(logout)

    def open_module(self, name):
        screen = self.manager.get_screen("module")
        screen.show_module(name, self.app_state.role)
        self.manager.current = "module"

    def open_update(self, *_):
        self.manager.current = "update"

    def logout(self, *_):
        self.app_state.logout()
        self.manager.current = "login"
