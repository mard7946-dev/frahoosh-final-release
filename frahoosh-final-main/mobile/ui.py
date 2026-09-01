from pathlib import Path

from kivy.core.text import LabelBase
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.widget import Widget

from mobile.config import FONT_REGULAR, FONT_BOLD, CARD, BORDER


def register_fonts():
    regular = Path(FONT_REGULAR)
    bold = Path(FONT_BOLD)
    if regular.exists():
        try:
            LabelBase.register(name="Frahoosh", fn_regular=str(regular), fn_bold=str(bold if bold.exists() else regular))
        except Exception:
            pass


def font_name():
    return "Frahoosh"


def rtl_text(value):
    text = str(value or "")
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


class Card(Widget):
    def __init__(self, radius=18, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color = Color(*CARD)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            self._line_color = Color(*BORDER)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, radius), width=0.8)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        r = self._line.rounded_rectangle[4]
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, r)
