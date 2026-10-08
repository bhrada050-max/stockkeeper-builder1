"""
Remote "under maintenance" screen.

How it works
------------
When the app starts (and when it comes back to the foreground) it reads a tiny
file called status.json from your GitHub repo:

    https://raw.githubusercontent.com/bhrada050-max/stockkeeper-builder1/main/status.json

  - "maintenance": true   -> everyone sees the full-screen update message
  - "maintenance": false  -> app works normally

If the phone is offline, or the file can't be read, the app works normally
(it never blocks people because of a network problem).
"""
import json
import math
import ssl
import threading
import time
import urllib.request

from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget

from rtl_fix import FONT_NAME, rtl_text

STATUS_URL = (
    "https://raw.githubusercontent.com/"
    "bhrada050-max/stockkeeper-builder1/main/status.json"
)
TIMEOUT = 5

DEFAULT_TITLE = "برنامه در حال بروزرسانی است"
DEFAULT_MESSAGE = (
    "در حال آماده‌سازی نسخه‌ی جدید و بهتر هستیم.\n"
    "لطفاً کمی بعد دوباره تلاش کنید."
)
DEFAULT_FOOTER = "از صبوری شما سپاسگزاریم"

AMBER = (1.0, 0.72, 0.20, 1)
BG = (0.03, 0.04, 0.07, 1)
CARD = (0.08, 0.09, 0.13, 1)
TEXT = (0.95, 0.97, 1, 1)
MUTED = (0.62, 0.66, 0.72, 1)
GREEN = (0.05, 0.72, 0.38, 1)
PANEL2 = (0.12, 0.14, 0.19, 1)


# ---------------------------------------------------------------------------
# network
# ---------------------------------------------------------------------------
def _fetch_status():
    url = STATUS_URL + "?t=" + str(int(time.time()))
    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context()

        req = urllib.request.Request(url, headers={"User-Agent": "StockKeeper"})
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _is_on(value):
    if value is True:
        return True
    return str(value).strip().lower() in ("true", "1", "yes", "on")


# ---------------------------------------------------------------------------
# text helpers (word-wrap in logical order, then convert each line)
# ---------------------------------------------------------------------------
_MEASURE = {}


def _width(text, size):
    key = round(float(size), 1)
    core = _MEASURE.get(key)
    if core is None:
        core = CoreLabel(font_name=FONT_NAME, font_size=size)
        _MEASURE[key] = core
    return core.get_extents(text)[0]


def _wrap(raw, width, size):
    try:
        lines = []
        for paragraph in str(raw).split("\n"):
            current = ""
            for word in paragraph.split(" "):
                candidate = (current + " " + word) if current else word
                if current and _width(rtl_text(candidate), size) > width:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            lines.append(current)
        return "\n".join(rtl_text(line) for line in lines)
    except Exception:
        return rtl_text(raw)


def _make_text(raw, size, color):
    label = Label(
        text=rtl_text(raw),
        font_size=dp(size),
        color=color,
        halign="center",
        valign="middle",
        font_name=FONT_NAME,
        size_hint_y=None,
        height=dp(size * 2),
    )
    label._raw = raw

    def relayout(obj, *_):
        width = obj.width
        if width <= dp(20):
            return
        obj.text_size = (width, None)
        new_text = _wrap(obj._raw, width - dp(4), obj.font_size)
        if new_text != obj.text:
            obj.text = new_text

    def fit(obj, tex_size):
        obj.height = tex_size[1] + dp(8)

    label.bind(width=relayout, texture_size=fit)
    return label


# ---------------------------------------------------------------------------
# widgets
# ---------------------------------------------------------------------------
class _Icon(Widget):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(dp(96), dp(96)), **kwargs)
        self.bind(pos=self._draw, size=self._draw)
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        r = min(self.width, self.height) / 2
        with self.canvas:
            Color(1, 0.72, 0.2, 0.12)
            Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
            for i in range(8):
                angle = i * math.pi / 4
                x = cx + math.cos(angle) * r * 0.72
                y = cy + math.sin(angle) * r * 0.72
                d = dp(5) + (i % 4) * dp(1.4)
                Color(1, 0.72, 0.2, 0.30 + 0.09 * i)
                Ellipse(pos=(x - d / 2, y - d / 2), size=(d, d))
            Color(1, 0.72, 0.2, 1)
            Ellipse(
                pos=(cx - r * 0.22, cy - r * 0.22),
                size=(r * 0.44, r * 0.44),
            )


def _round_button(text, bg, callback):
    btn = Button(
        text=rtl_text(text),
        size_hint_y=None,
        height=dp(50),
        font_size=dp(15),
        color=TEXT,
        background_normal="",
        background_down="",
        background_color=(0, 0, 0, 0),
        font_name=FONT_NAME,
    )
    with btn.canvas.before:
        Color(*bg)
        rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])

    def update(*_):
        rect.pos = btn.pos
        rect.size = btn.size

    btn.bind(pos=update, size=update)
    btn.bind(on_release=callback)
    return btn


class MaintenanceScreen(ModalView):
    def __init__(self, app, data, **kwargs):
        super().__init__(
            size_hint=(1, 1),
            auto_dismiss=False,
            background="",
            background_color=BG,
            overlay_color=(0, 0, 0, 0),
            **kwargs
        )
        self.app = app

        title = data.get("title") or DEFAULT_TITLE
        message = data.get("message") or DEFAULT_MESSAGE
        footer = data.get("footer") or DEFAULT_FOOTER

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(16),
        )

        root.add_widget(Widget())  # top spacer

        column = BoxLayout(
            orientation="vertical",
            spacing=dp(16),
            size_hint_y=None,
        )
        column.bind(minimum_height=column.setter("height"))

        icon_box = AnchorLayout(
            anchor_x="center", anchor_y="center",
            size_hint_y=None, height=dp(110),
        )
        icon_box.add_widget(_Icon())
        column.add_widget(icon_box)

        card = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(20), dp(18), dp(20)],
            spacing=dp(12),
            size_hint_y=None,
        )
        card.bind(minimum_height=card.setter("height"))

        with card.canvas.before:
            Color(*CARD)
            card_rect = RoundedRectangle(
                pos=card.pos, size=card.size, radius=[dp(18)]
            )

        def update_card(*_):
            card_rect.pos = card.pos
            card_rect.size = card.size

        card.bind(pos=update_card, size=update_card)

        card.add_widget(_make_text(title, 22, AMBER))

        bar_box = AnchorLayout(
            anchor_x="center", size_hint_y=None, height=dp(4)
        )
        bar = Widget(size_hint=(None, 1), width=dp(54))
        with bar.canvas:
            Color(*AMBER)
            bar_rect = RoundedRectangle(
                pos=bar.pos, size=bar.size, radius=[dp(2)]
            )

        def update_bar(*_):
            bar_rect.pos = bar.pos
            bar_rect.size = bar.size

        bar.bind(pos=update_bar, size=update_bar)
        bar_box.add_widget(bar)
        card.add_widget(bar_box)

        card.add_widget(_make_text(message, 16, TEXT))
        card.add_widget(_make_text(footer, 13, MUTED))
        column.add_widget(card)

        buttons = BoxLayout(
            orientation="vertical", spacing=dp(10),
            size_hint_y=None,
        )
        buttons.bind(minimum_height=buttons.setter("height"))

        self.retry_button = _round_button(
            "تلاش دوباره", GREEN, self._on_retry
        )
        close_button = _round_button(
            "بستن برنامه", PANEL2, self._on_close
        )
        buttons.add_widget(self.retry_button)
        buttons.add_widget(close_button)
        column.add_widget(buttons)

        root.add_widget(column)
        root.add_widget(Widget())  # bottom spacer

        self.add_widget(root)

    def set_busy(self, busy):
        self.retry_button.text = rtl_text(
            "در حال بررسی..." if busy else "تلاش دوباره"
        )
        self.retry_button.disabled = bool(busy)

    def _on_retry(self, *_):
        self.set_busy(True)
        start_maintenance_check(self.app)

    def _on_close(self, *_):
        try:
            self.app.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------
_state = {"screen": None, "checking": False}


def _on_dismiss(*_):
    _state["screen"] = None


def _apply(app, data):
    _state["checking"] = False
    screen = _state["screen"]

    if screen is not None:
        screen.set_busy(False)

    if data and _is_on(data.get("maintenance")):
        if screen is None:
            screen = MaintenanceScreen(app, data)
            screen.bind(on_dismiss=_on_dismiss)
            _state["screen"] = screen
            screen.open()
    else:
        # not in maintenance (or could not check) -> let the user in
        if screen is not None:
            screen.dismiss()
            _state["screen"] = None


def start_maintenance_check(app):
    """Check status.json in the background; never blocks the UI."""
    if _state["checking"]:
        return
    _state["checking"] = True

    def worker():
        data = _fetch_status()
        Clock.schedule_once(lambda dt: _apply(app, data), 0)

    threading.Thread(target=worker, daemon=True).start()
