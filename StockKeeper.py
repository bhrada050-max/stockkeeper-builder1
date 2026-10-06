import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1) next to this file (works in the APK and in Pydroid)
# 2) Download folder (Pydroid fallback)
FONT_CANDIDATES = [
    os.path.join(BASE_DIR, "Vazirmatn-Regular.ttf"),
    "Vazirmatn-Regular.ttf",
    "/storage/emulated/0/Download/Vazirmatn-Regular.ttf",
]

FONT_NAME = "Roboto"
for _path in FONT_CANDIDATES:
    if os.path.exists(_path):
        FONT_NAME = _path
        break

# ---------------------------------------------------------------------------
# Persian/Arabic text fix for Kivy on Pydroid 3
#
# The Kivy text renderer on Pydroid 3 does NOT do Arabic shaping or
# bidirectional ordering, so Persian shows up reversed and/or with
# disconnected letters. rtl_text() converts normal (logical) Persian text
# into the "visual" form this renderer needs:
#   1) letters are joined (isolated/initial/medial/final forms)
#   2) the line is reordered right-to-left, numbers/English stay left-to-right
#
# Use rtl_text() ONLY when putting text on screen. Keep stored data
# (product names, etc.) in normal order.
#
# If your device ever shows the text correctly WITHOUT this fix, set
# FIX_PERSIAN_TEXT = False
# ---------------------------------------------------------------------------
FIX_PERSIAN_TEXT = True

# char: (isolated, final) for right-joining letters,
#       (isolated, final, initial, medial) for dual-joining letters
_AR_FORMS = {
    "\u0621": (0xFE80,),
    "\u0622": (0xFE81, 0xFE82),
    "\u0623": (0xFE83, 0xFE84),
    "\u0624": (0xFE85, 0xFE86),
    "\u0625": (0xFE87, 0xFE88),
    "\u0626": (0xFE89, 0xFE8A, 0xFE8B, 0xFE8C),
    "\u0627": (0xFE8D, 0xFE8E),
    "\u0628": (0xFE8F, 0xFE90, 0xFE91, 0xFE92),
    "\u0629": (0xFE93, 0xFE94),
    "\u062A": (0xFE95, 0xFE96, 0xFE97, 0xFE98),
    "\u062B": (0xFE99, 0xFE9A, 0xFE9B, 0xFE9C),
    "\u062C": (0xFE9D, 0xFE9E, 0xFE9F, 0xFEA0),
    "\u062D": (0xFEA1, 0xFEA2, 0xFEA3, 0xFEA4),
    "\u062E": (0xFEA5, 0xFEA6, 0xFEA7, 0xFEA8),
    "\u062F": (0xFEA9, 0xFEAA),
    "\u0630": (0xFEAB, 0xFEAC),
    "\u0631": (0xFEAD, 0xFEAE),
    "\u0632": (0xFEAF, 0xFEB0),
    "\u0633": (0xFEB1, 0xFEB2, 0xFEB3, 0xFEB4),
    "\u0634": (0xFEB5, 0xFEB6, 0xFEB7, 0xFEB8),
    "\u0635": (0xFEB9, 0xFEBA, 0xFEBB, 0xFEBC),
    "\u0636": (0xFEBD, 0xFEBE, 0xFEBF, 0xFEC0),
    "\u0637": (0xFEC1, 0xFEC2, 0xFEC3, 0xFEC4),
    "\u0638": (0xFEC5, 0xFEC6, 0xFEC7, 0xFEC8),
    "\u0639": (0xFEC9, 0xFECA, 0xFECB, 0xFECC),
    "\u063A": (0xFECD, 0xFECE, 0xFECF, 0xFED0),
    "\u0640": (0x0640, 0x0640, 0x0640, 0x0640),
    "\u0641": (0xFED1, 0xFED2, 0xFED3, 0xFED4),
    "\u0642": (0xFED5, 0xFED6, 0xFED7, 0xFED8),
    "\u0643": (0xFED9, 0xFEDA, 0xFEDB, 0xFEDC),
    "\u0644": (0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0),
    "\u0645": (0xFEE1, 0xFEE2, 0xFEE3, 0xFEE4),
    "\u0646": (0xFEE5, 0xFEE6, 0xFEE7, 0xFEE8),
    "\u0647": (0xFEE9, 0xFEEA, 0xFEEB, 0xFEEC),
    "\u0648": (0xFEED, 0xFEEE),
    "\u0649": (0xFEEF, 0xFEF0),
    "\u064A": (0xFEF1, 0xFEF2, 0xFEF3, 0xFEF4),
    "\u067E": (0xFB56, 0xFB57, 0xFB58, 0xFB59),
    "\u0686": (0xFB7A, 0xFB7B, 0xFB7C, 0xFB7D),
    "\u0698": (0xFB8A, 0xFB8B),
    "\u06A9": (0xFB8E, 0xFB8F, 0xFB90, 0xFB91),
    "\u06AF": (0xFB92, 0xFB93, 0xFB94, 0xFB95),
    "\u06CC": (0xFBFC, 0xFBFD, 0xFBFE, 0xFBFF),
}

_AR_LAM_ALEF = {
    "\u0622": (0xFEF5, 0xFEF6),
    "\u0623": (0xFEF7, 0xFEF8),
    "\u0625": (0xFEF9, 0xFEFA),
    "\u0627": (0xFEFB, 0xFEFC),
}

_AR_MIRROR = {
    "(": ")", ")": "(", "[": "]", "]": "[", "{": "}", "}": "{",
    "<": ">", ">": "<", "\u00AB": "\u00BB", "\u00BB": "\u00AB",
}

_AR_NEUTRAL = "\u060C\u061B\u061F\u066A\u066B\u066C"
_AR_DROP = "\u200C\u200D\u200E\u200F\u202A\u202B\u202C\u202D\u202E"


def _ar_is_mark(ch):
    return "\u064B" <= ch <= "\u065F" or ch == "\u0670"


def _ar_is_arabic(ch):
    o = ord(ch)
    return (
        0x0600 <= o <= 0x06FF
        or 0x0750 <= o <= 0x077F
        or 0xFB50 <= o <= 0xFDFF
        or 0xFE70 <= o <= 0xFEFF
    )


def has_persian(value):
    return any(_ar_is_arabic(ch) for ch in str(value))


def _ar_reshape(text):
    chars = list(text)
    n = len(chars)
    out = []

    def prev_dual(i):
        j = i - 1
        while j >= 0 and _ar_is_mark(chars[j]):
            j -= 1
        return j >= 0 and len(_AR_FORMS.get(chars[j], ())) == 4

    def next_joins(i):
        j = i + 1
        while j < n and _ar_is_mark(chars[j]):
            j += 1
        return j < n and len(_AR_FORMS.get(chars[j], ())) >= 2

    i = 0
    while i < n:
        ch = chars[i]

        if ch in _AR_DROP:
            i += 1
            continue

        forms = _AR_FORMS.get(ch)
        if forms is None:
            out.append(ch)
            i += 1
            continue

        if ch == "\u0644":
            j = i + 1
            while j < n and _ar_is_mark(chars[j]):
                j += 1
            if j < n and chars[j] in _AR_LAM_ALEF:
                lig = _AR_LAM_ALEF[chars[j]]
                out.append(chr(lig[1] if prev_dual(i) else lig[0]))
                i = j + 1
                continue

        pd = prev_dual(i)

        if len(forms) == 1:
            code = forms[0]
        elif len(forms) == 2:
            code = forms[1] if pd else forms[0]
        else:
            nj = next_joins(i)
            if pd and nj:
                code = forms[3]
            elif pd:
                code = forms[1]
            elif nj:
                code = forms[2]
            else:
                code = forms[0]

        out.append(chr(code))
        i += 1

    return "".join(out)


def _ar_visual_line(line):
    shaped = _ar_reshape(line)

    # group base char + its combining marks into clusters
    clusters = []
    for ch in shaped:
        if _ar_is_mark(ch) and clusters:
            clusters[-1] += ch
        else:
            clusters.append(ch)

    types = []
    for cl in clusters:
        ch = cl[0]
        if ch.isdigit():
            types.append("L")
        elif _ar_is_arabic(ch):
            types.append("N" if ch in _AR_NEUTRAL else "R")
        elif ch.isalpha():
            types.append("L")
        else:
            types.append("N")

    count = len(clusters)

    # % and $ stuck to a number stay with the number
    for i in range(count):
        if types[i] == "N" and clusters[i][0] in "%$\u066A":
            before = i > 0 and clusters[i - 1][0].isdigit()
            after = i + 1 < count and clusters[i + 1][0].isdigit()
            if before or after:
                types[i] = "L"

    # neutrals: between two LTR items they are LTR, otherwise RTL
    resolved = list(types)
    for i in range(count):
        if types[i] != "N":
            continue
        left = "R"
        j = i - 1
        while j >= 0:
            if types[j] != "N":
                left = types[j]
                break
            j -= 1
        right = "R"
        j = i + 1
        while j < count:
            if types[j] != "N":
                right = types[j]
                break
            j += 1
        resolved[i] = "L" if (left == "L" and right == "L") else "R"

    # split into runs
    runs = []
    for cl, t in zip(clusters, resolved):
        if runs and runs[-1][0] == t:
            runs[-1][1].append(cl)
        else:
            runs.append([t, [cl]])

    result = []
    for t, items in reversed(runs):
        if t == "R":
            for cl in reversed(items):
                result.append(_AR_MIRROR.get(cl, cl))
        else:
            result.extend(items)

    return "".join(result)


def rtl_text(value):
    if value is None:
        return value
    text = str(value)
    if not FIX_PERSIAN_TEXT or not has_persian(text):
        return text
    return "\n".join(_ar_visual_line(line) for line in text.split("\n"))


class PersianInput(TextInput):
    """
    TextInput for Persian typing on Pydroid.

    Kivy draws typed text left-to-right without joining letters. This input
    keeps what you typed in normal order in `.logical` (use that to READ the
    value) and shows the fixed visual form on screen.
    Typing always goes to the end; use backspace to correct mistakes.
    """

    logical = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.halign = "right"
        except Exception:
            pass

    def _show(self):
        self.text = rtl_text(self.logical)
        Clock.schedule_once(self._cursor_to_start, 0)

    def _cursor_to_start(self, *_):
        try:
            self.cursor = (0, 0)
        except Exception:
            pass

    def set_logical(self, value):
        self.logical = "" if value is None else str(value)
        self._show()

    def insert_text(self, substring, from_undo=False):
        substring = str(substring).replace("\r", " ").replace("\n", " ")
        if not substring:
            return
        self.logical += substring
        self._show()

    def do_backspace(self, from_undo=False, mode="bkspc"):
        if self.logical:
            self.logical = self.logical[:-1]
            self._show()


class StockKeeper(App):
    def build(self):
        self.title = "مدیریت موجودی"
        self.dark_mode = True
        self.products = []
        self.current_page = "products"

        try:
            Window.softinput_mode = "below_target"
        except Exception:
            pass

        self.load_data()

        self.root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(10), dp(8), dp(10), dp(8)]
        )

        self.main_area = BoxLayout(
            orientation="vertical",
            spacing=dp(8)
        )
        self.root.add_widget(self.main_area)

        self.bottom_nav = self.make_bottom_nav()
        self.root.add_widget(self.bottom_nav)

        self.show_page("products")
        return self.root

    # -----------------------------
    # Theme / colors
    # -----------------------------
    def colors(self):
        if self.dark_mode:
            return {
                "bg": (0.03, 0.04, 0.06, 1),
                "panel": (0.065, 0.075, 0.10, 1),
                "panel2": (0.09, 0.10, 0.13, 1),
                "text": (0.95, 0.97, 1, 1),
                "muted": (0.62, 0.66, 0.72, 1),
                "green": (0.05, 0.72, 0.38, 1),
                "red": (0.88, 0.18, 0.20, 1),
                "blue": (0.18, 0.42, 0.85, 1),
                "input": (0.09, 0.10, 0.14, 1),
                "border": (0.16, 0.18, 0.23, 1),
            }

        return {
            "bg": (0.95, 0.96, 0.98, 1),
            "panel": (1, 1, 1, 1),
            "panel2": (0.91, 0.93, 0.96, 1),
            "text": (0.08, 0.09, 0.11, 1),
            "muted": (0.35, 0.38, 0.43, 1),
            "green": (0.04, 0.62, 0.31, 1),
            "red": (0.78, 0.08, 0.10, 1),
            "blue": (0.10, 0.34, 0.72, 1),
            "input": (1, 1, 1, 1),
            "border": (0.78, 0.80, 0.84, 1),
        }

    def apply_theme(self):
        c = self.colors()

        try:
            Window.clearcolor = c["bg"]
        except Exception:
            pass

        if self.current_page == "products":
            self.products_page()
        elif self.current_page == "create":
            self.create_page()
        elif self.current_page == "alerts":
            self.alerts_page()

        self.update_nav_theme()

    # -----------------------------
    # Basic widget helpers
    # -----------------------------
    def make_label(
        self,
        text="",
        size=16,
        color=None,
        bold=False,
        halign="left",
        valign="middle"
    ):
        c = self.colors()

        if halign == "left" and has_persian(text):
            halign = "right"

        label = Label(
            text=rtl_text(text),
            font_size=dp(size),
            color=color if color else c["text"],
            bold=bold,
            halign=halign,
            valign=valign,
            font_name=FONT_NAME
        )

        label.bind(
            size=lambda obj, value: setattr(
                obj, "text_size", (obj.width - dp(4), None)
            )
        )

        return label

    def make_button(
        self,
        text,
        callback=None,
        bg=None,
        height=46,
        font_size=14
    ):
        c = self.colors()

        button = Button(
            text=rtl_text(text),
            size_hint_y=None,
            height=dp(height),
            font_size=dp(font_size),
            color=c["text"],
            background_normal="",
            background_down="",
            background_color=bg if bg else c["panel2"],
            font_name=FONT_NAME
        )

        if callback:
            button.bind(on_release=callback)

        return button

    def make_text_input(
        self,
        hint,
        multiline=False,
        input_filter=None,
        persian=False
    ):
        c = self.colors()

        field = (PersianInput if persian else TextInput)(
            hint_text=rtl_text(hint),
            multiline=multiline,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name=FONT_NAME
        )

        if input_filter:
            field.input_filter = input_filter

        return field

    # -----------------------------
    # Product card background
    # -----------------------------
    def add_card_background(self, widget):
        c = self.colors()

        with widget.canvas.before:
            Color(*c["panel"])
            widget._card_rect = RoundedRectangle(
                pos=widget.pos,
                size=widget.size,
                radius=[dp(10)]
            )

            Color(*c["border"])
            widget._card_line = Line(
                rounded_rectangle=(
                    widget.x,
                    widget.y,
                    widget.width,
                    widget.height,
                    dp(10)
                ),
                width=1.2
            )

        def update_card(*_):
            widget._card_rect.pos = widget.pos
            widget._card_rect.size = widget.size
            widget._card_line.rounded_rectangle = (
                widget.x,
                widget.y,
                widget.width,
                widget.height,
                dp(10)
            )

        widget.bind(pos=update_card, size=update_card)

    # -----------------------------
    # Header
    # -----------------------------
    def make_header(self, title):
        c = self.colors()

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8)
        )

        title_label = self.make_label(
            title,
            size=22,
            bold=True
        )
        header.add_widget(title_label)

        theme_text = "روشن" if self.dark_mode else "تیره"

        theme_button = self.make_button(
            theme_text,
            self.change_theme,
            bg=c["blue"],
            height=42,
            font_size=12
        )
        theme_button.size_hint_x = None
        theme_button.width = dp(78)

        header.add_widget(theme_button)

        return header

    # -----------------------------
    # Bottom navigation
    # -----------------------------
    def make_bottom_nav(self):
        c = self.colors()

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            spacing=dp(6)
        )

        self.nav_products = self.make_button(
            "محصولات",
            lambda *_: self.show_page("products"),
            bg=c["panel2"],
            height=52
        )

        self.nav_create = self.make_button(
            "افزودن",
            lambda *_: self.show_page("create"),
            bg=c["panel2"],
            height=52
        )

        self.nav_alerts = self.make_button(
            "هشدارها",
            lambda *_: self.show_page("alerts"),
            bg=c["panel2"],
            height=52
        )

        nav.add_widget(self.nav_products)
        nav.add_widget(self.nav_create)
        nav.add_widget(self.nav_alerts)

        return nav

    def update_nav_theme(self):
        if not hasattr(self, "bottom_nav"):
            return

        c = self.colors()

        self.nav_products.background_color = (
            c["green"] if self.current_page == "products"
            else c["panel2"]
        )

        self.nav_create.background_color = (
            c["green"] if self.current_page == "create"
            else c["panel2"]
        )

        self.nav_alerts.background_color = (
            c["red"] if self.current_page == "alerts"
            else c["panel2"]
        )

        self.nav_products.color = c["text"]
        self.nav_create.color = c["text"]
        self.nav_alerts.color = c["text"]

    # -----------------------------
    # Page handling
    # -----------------------------
    def show_page(self, page):
        self.current_page = page
        self.main_area.clear_widgets()

        if page == "products":
            self.products_page()
        elif page == "create":
            self.create_page()
        elif page == "alerts":
            self.alerts_page()

        self.update_nav_theme()

    # -----------------------------
    # PRODUCTS PAGE
    # -----------------------------
    def products_page(self):
        self.current_page = "products"
        self.main_area.clear_widgets()
        c = self.colors()

        self.main_area.add_widget(
            self.make_header("مدیریت موجودی")
        )

        self.search_input = PersianInput(
            hint_text=rtl_text("جستجوی محصولات..."),
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name=FONT_NAME
        )

        self.search_input.bind(
            logical=self.search_changed
        )

        self.main_area.add_widget(self.search_input)

        self.product_scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        self.product_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(1), dp(5), dp(1), dp(10)],
            size_hint_y=None
        )

        self.product_list.bind(
            minimum_height=self.product_list.setter("height")
        )

        self.product_scroll.add_widget(self.product_list)
        self.main_area.add_widget(self.product_scroll)

        self.refresh_products()

    def search_changed(self, instance, value):
        self.refresh_products(value)

    def refresh_products(self, search_text=None):
        if not hasattr(self, "product_list"):
            return

        self.product_list.clear_widgets()

        c = self.colors()

        if search_text is None:
            search_widget = getattr(
                self,
                "search_input",
                None
            )
            search_text = (
                search_widget.logical
                if search_widget
                else ""
            )

        search_text = search_text.sn="middle"):
        c = self.colors()

        if halign == "left" and has_persian(text):
            halign = "right"

        label = Label(
            text=rtl_text(text),
            font_size=dp(size),
            color=color if color else c["text"],
            bold=bold,
            halign=halign,
            valign=valign,
            font_name=FONT_NAME
        )

        label.bind(
            size=lambda obj, value: setattr(obj, "text_size", (obj.width - dp(4), None))
        )

        return label

    def make_button(self, text, callback=None, bg=None, height=46, font_size=14):
        c = self.colors()

        button = Button(
            text=rtl_text(text),
            size_hint_y=None,
            height=dp(height),
            font_size=dp(font_size),
            color=c["text"],
            background_normal="",
            background_down="",
            background_color=bg if bg else c["panel2"],
            font_name=FONT_NAME
        )

        if callback:
            button.bind(on_release=callback)

        return button

    def make_text_input(self, hint, multiline=False, input_filter=None, persian=False):
        c = self.colors()

        field = (PersianInput if persian else TextInput)(
            hint_text=rtl_text(hint),
            multiline=multiline,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name=FONT_NAME
        )

        if input_filter:
            field.input_filter = input_filter

        return field

    def add_card_background(self, widget):
        c = self.colors()

        with widget.canvas.before:
            Color(*c["panel"])
            widget._card_rect = RoundedRectangle(
                pos=widget.pos,
                size=widget.size,
                radius=[dp(10)]
            )

            Color(*c["border"])
            widget._card_line = Line(
                rounded_rectangle=(
                    widget.x,
                    widget.y,
                    widget.width,
                    widget.height,
                    dp(10)
                ),
                width=1.2
            )

        def update_card(*_):
            widget._card_rect.pos = widget.pos
            widget._card_rect.size = widget.size
            widget._card_line.rounded_rectangle = (
                widget.x,
                widget.y,
                widget.width,
                widget.height,
                dp(10)
            )

        widget.bind(pos=update_card, size=update_card)

    def make_header(self, title):
        c = self.colors()

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8)
        )

        title_label = self.make_label(title, size=22, bold=True)
        header.add_widget(title_label)

        theme_text = "روشن" if self.dark_mode else "تیره"

        theme_button = self.make_button(
            theme_text,
            self.change_theme,
            bg=c["blue"],
            height=42,
            font_size=12
        )
        theme_button.size_hint_x = None
        theme_button.width = dp(78)

        header.add_widget(theme_button)

        return header

    def make_bottom_nav(self):
        c = self.colors()

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            spacing=dp(6)
        )

        self.nav_products = self.make_button(
            "محصولات",
            lambda *_: self.show_page("products"),
            bg=c["panel2"],
            height=52
        )

        self.nav_create = self.make_button(
            "افزودن",
            lambda *_: self.show_page("create"),
            bg=c["panel2"],
            height=52
        )

        self.nav_alerts = self.make_button(
            "هشدارها",
            lambda *_: self.show_page("alerts"),
            bg=c["panel2"],
            height=52
        )

        nav.add_widget(self.nav_products)
        nav.add_widget(self.nav_create)
        nav.add_widget(self.nav_alerts)

        return nav

    def update_nav_theme(self):
        if not hasattr(self, "bottom_nav"):
            return

        c = self.colors()

        self.nav_products.background_color = c["green"] if self.current_page == "products" else c["panel2"]
        self.nav_create.background_color = c["green"] if self.current_page == "create" else c["panel2"]
        self.nav_alerts.background_color = c["red"] if self.current_page == "alerts" else c["panel2"]

        self.nav_products.color = c["text"]
        self.nav_create.color = c["text"]
        self.nav_alerts.color = c["text"]

    def show_page(self, page):
        self.current_page = page
        self.main_area.clear_widgets()

        if page == "products":
            self.products_page()
        elif page == "create":
            self.create_page()
        elif page == "alerts":
            self.alerts_page()

        self.update_nav_theme()

    def products_page(self):
        self.current_page = "products"
        self.main_area.clear_widgets()
        c = self.colors()

        self.main_area.add_widget(self.make_header("مدیریت موجودی"))

        self.search_input = PersianInput(
            hint_text=rtl_text("جستجوی محصولات..."),
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name=FONT_NAME
        )

        self.search_input.bind(logical=self.search_changed)
        self.main_area.add_widget(self.search_input)

        self.product_scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))

        self.product_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(1), dp(5), dp(1), dp(10)],
            size_hint_y=None
        )

        self.product_list.bind(minimum_height=self.product_list.setter("height"))
        self.product_scroll.add_widget(self.product_list)
        self.main_area.add_widget(self.product_scroll)

        self.refresh_products()

    def search_changed(self, instance, value):
        self.refresh_products(value)

    def refresh_products(self, search_text=None):
        if not hasattr(self, "product_list"):
            return

        self.product_list.clear_widgets()
        c = self.colors()

        if search_text is None:
            search_widget = getattr(self, "search_input", None)
            search_text = search_widget.logical if search_widget else ""

        search_text = search_text.strip().lower()

        if not self.products:
            empty = self.make_label(
                "هنوز محصولی وجود ندارد.\nبرای افزودن محصول روی «افزودن» بزنید.",
                size=17, color=c["muted"], halign="center"
            )
            empty.size_hint_y = None
            empty.height = dp(100)
            self.product_list.add_widget(empty)
            return

        visible = [
            (index, product)
            for index, product in enumerate(self.products)
            if search_text in str(product.get("name", "")).lower()
        ]

        if not visible:
            empty = self.make_label(
                "محصولی پیدا نشد.",
                size=17, color=c["muted"], halign="center"
            )
            empty.size_hint_y = None
            empty.height = dp(80)
            self.product_list.add_widget(empty)
            return

        for index, product in visible:
            self.add_product_card(product, index)

    def add_product_card(self, product, index):
        c = self.colors()

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(190),
            padding=[dp(10), dp(9), dp(10), dp(9)],
            spacing=dp(3)
        )

        self.add_card_background(card)

        name_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32)
        )

        name = str(product.get("name", ""))
        qty = self.safe_int(product.get("qty", 0))
        low = self.safe_int(product.get("low", 0))

        name_label = self.make_label(name, size=18, bold=True)
        name_row.add_widget(name_label)

        if qty <= low:
            warning = self.make_label(
                "[موجودی کم]",
                size=12, color=c["red"], bold=True, halign="right"
            )
            warning.size_hint_x = None
            warning.width = dp(105)
            name_row.add_widget(warning)

        card.add_widget(name_row)

        purchase = self.safe_float(product.get("purchase_price", 0))
        sale = self.safe_float(product.get("sale_price", 0))

        info = self.make_label(
            "قیمت خرید: %.2f\nقیمت فروش: %.2f\nتعداد: %d\nحد هشدار: %d"
            % (purchase, sale, qty, low),
            size=13, color=c["muted"]
        )

        info.size_hint_y = None
        info.height = dp(82)
        card.add_widget(info)

        edit = self.make_button(
            "ویرایش",
            lambda *_args, i=index: self.edit_product(i),
            bg=c["blue"],
            height=42,
            font_size=14
        )

        card.add_widget(edit)
        self.product_list.add_widget(card)

    def create_page(self):
        self.current_page = "create"
        self.main_area.clear_widgets()
        c = self.colors()

        self.main_area.add_widget(self.make_header("افزودن محصول"))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
 eight = dp(100)
            self.product_list.add_widget(empty)
            return
        visible = [
            (index, product)
            for index, product in enumerate(self.products)
            if search_text in str(product.get("name", "")).lower()
        ]
        if not visible:
            empty = self.make_label(
                "محصولی پیدا نشد.",
                size=17,
                color=c["muted"],
                halign="center"
            )
            empty.size_hint_y = None
            empty.height = dp(80)
            self.product_list.add_widget(empty)
            return
        for index, product in visible:
            self.add_product_card(product, index)

    def add_product_card(self, product, index):
        c = self.colors()
        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(190),
            padding=[dp(10), dp(9), dp(10), dp(9)],
            spacing=dp(3)
        )
        self.add_card_background(card)
        name_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32)
        )
        name = str(product.get("name", ""))
        qty = self.safe_int(product.get("qty", 0))
        low = self.safe_int(product.get("low", 0))
        name_label = self.make_label(name, size=18, bold=True)
        name_row.add_widget(name_label)
        if qty <= low:
            warning = self.make_label(
                "[موجودی کم]",
                size=12,
                color=c["red"],
                bold=True,
                halign="right"
            )
            warning.size_hint_x = None
            warning.width = dp(105)
            name_row.add_widget(warning)
        card.add_widget(name_row)
        purchase = self.safe_float(product.get("purchase_price", 0))
        sale = self.safe_float(product.get("sale_price", 0))
        info = self.make_label(
            "قیمت خرید: %.2f\n"
            "قیمت فروش: %.2f\n"
            "تعداد: %d\n"
            "حد هشدار: %d"
            % (purchase, sale, qty, low),
            size=13,
            color=c["muted"]
        )
        info.size_hint_y = None
        info.height = dp(82)
        card.add_widget(info)
        edit = self.make_button(
            "ویرایش",
            lambda *_args, i=index: self.edit_product(i),
            bg=c["blue"],
            height=42,
            font_size=14
        )
        card.add_widget(edit)
        self.product_list.add_widget(card)

    def create_page(self):
        self.current_page = "create"
        self.main_area.clear_widgets()
        c = self.colors()
        self.main_area.add_widget(self.make_header("افزودن محصول"))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))
        form = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(2), dp(6), dp(2), dp(12)],
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))
        title = self.make_label("افزودن محصول", size=21, bold=True)
        title.size_hint_y = None
        title.height = dp(42)
        form.add_widget(title)
        self.name_input = self.make_text_input("نام محصول")
        self.qty_input = self.make_text_input("تعداد", input_filter="int")
        self.purchase_input = self.make_text_input("قیمت خرید", input_filter="float")
        self.sale_input = self.make_text_input("قیمت فروش", input_filter="float")
        self.low_input = self.make_text_input("حد هشدار موجودی کم", input_filter="int")
        form.add_widget(self.name_input)
        form.add_widget(self.qty_input)
        form.add_widget(self.purchase_input)
        form.add_widget(self.sale_input)
        form.add_widget(self.low_input)
        note = self.make_label(
            "وارد کردن قیمت‌ها اختیاری است.",
            size=12,
            color=c["muted"]
        )
        note.size_hint_y = None
        note.height = dp(28)
        form.add_widget(note)
        form.add_widget(BoxLayout(size_hint_y=None, height=dp(5)))
        save_button = self.make_button(
            "ذخیره محصول",
            self.save_product,
            bg=c["green"],
            height=52,
            font_size=15
        )
        form.add_widget(save_button)
        scroll.add_widget(form)
        self.main_area.add_widget(scroll)

    def save_product(self, *_):
        name = self.name_input.text.strip()
        if not name:
            self.message("خطا", "نام محصول الزامی است.")
            return
        qty_text = self.qty_input.text.strip()
        purchase_text = self.purchase_input.text.strip()
        sale_text = self.sale_input.text.strip()
        low_text = self.low_input.text.strip()
        if not qty_text or not low_text:
            self.message("خطا", "لطفاً اعداد معتبر وارد کنید.")
            return
        try:
            qty = int(qty_text)
            low = int(low_text)
            if qty < 0 or low < 0:
                raise ValueError
            purchase = float(purchase_text) if purchase_text else 0.0
            sale = float(sale_text) if sale_text else 0.0
            if purchase < 0 or sale < 0:
                raise ValueError
        except (ValueError, TypeError):
            self.message("خطا", "لطفاً اعداد معتبر وارد کنید.")
            return
        product = {
            "name": name,
            "qty": qty,
            "purchase_price": purchase,
            "sale_price": sale,
            "low": low
        }
        self.products.append(product)
        self.save_data()
        self.show_page("products")

    def edit_product(self, index):
        if index < 0 or index >= len(self.products):
            return
        product = self.products[index]
        c = self.colors()
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(12), dp(12), dp(12), dp(12)]
        )
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        form = BoxLayout(
            orientation="vertical",
            spacing=dp(9),
            size_hint_y=None
        )
        form.bind(minimum_height=form.setter("height"))
        name_input = self.make_text_input("نام محصول")
        name_input.text = str(product.get("name", ""))
        qty_input = self.make_text_input("تعداد", input_filter="int")
        qty_input.text = str(self.safe_int(product.get("qty", 0)))
        purchase_input = self.make_text_input("قیمت خرید", input_filter="float")
        purchase_value = self.safe_float(product.get("purchase_price", 0))
        purchase_input.text = str(purchase_value) if purchase_value != 0 else ""
        sale_input = self.make_text_input("قیمت فروش", input_filter="float")
        sale_value = self.safe_float(product.get("sale_price", 0))
        sale_input.text = str(sale_value) if sale_value != 0 else ""
        low_input = self.make_text_input("حد هشدار موجودی کم", input_filter="int")
        low_input.text = str(self.safe_int(product.get("low", 0)))
        form.add_widget(name_input)
        form.add_widget(qty_input)
        form.add_widget(purchase_input)
        form.add_widget(sale_input)
        form.add_widget(low_input)
        scroll.add_widget(form)
        content.add_widget(scroll)
        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(7)
        )
        save_button = self.make_button("ذخیره", bg=c["green"], height=46)
        delete_button = self.make_button("حذف", bg=c["red"], height=46)
        close_button = self.make_button("بستن", bg=c["panel2"], height=46)
        buttons.add_widget(save_button)
        buttons.add_widget(delete_button)
        buttons.add_widget(close_button)
        content.add_widget(buttons)
        popup = Popup(
            title="ویرایش محصول",
            content=content,
            size_hint=(0.94, 0.82),
            auto_dismiss=False,
            title_size=dp(18)
        )

        def save_changes(*_):
            new_name = name_input.text.strip()
            qty_text = qty_input.text.strip()
            purchase_text = purchase_input.text.strip()
            sale_text = sale_input.text.strip()
            low_text = low_input.text.strip()
            if not new_name:
                self.message("خطا", "نام محصول الزامی است.")
                return
            if not qty_text or not low_text:
                self.message("خطا", "لطفاً اعداد معتبر وارد کنید.")
                return
            try:
                new_qty = int(qty_text)
                new_low = int(low_text)
                new_purchase = float(purchase_text) if purchase_text else 0.0
                new_sale = float(sale_text) if sale_text else 0.0
                if (new_qty < 0 or new_low < 0 or new_purchase < 0 or new_sale < 0):
                    raise ValueError
            except (ValueError, TypeError):
                self.message("خطا", "لطفاً اعداد معتبر وارد کنید.")
                return
            product["name"] = new_name
            product["qty"] = new_qty
            product["purchase_price"] = new_purchase
            product["sale_price"] = new_sale
            product["low"] = new_low
            self.save_data()
            popup.dismiss()
            self.refresh_products()

        def delete_product(*_):
            self.confirm_delete(index, popup)

        save_button.bind(on_release=save_changes)
        delete_button.bind(on_release=delete_product)
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete(self, index, edit_popup):
        if index < 0 or index >= len(self.products):
            return
        c = self.colors()
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(12), dp(12), dp(12), dp(12)]
        )
        label = self.make_label("این محصول حذف شود؟", size=16, halign="center")
        content.add_wid   def search_changed(self, instance, value):
        self.refresh_products(value)

    def refresh_products(self, search_text=None):
        if not hasattr(self, "product_list"):
            return

        self.product_list.clear_widgets()

        c = self.colors()

        if search_text is None:
            search_widget = getattr(
                self,
                "search_input",
                None
            )
            search_text = (
                search_widget.text
                if search_widget
                else ""
            )

        search_text = search_text.strip().lower()

        if not self.products:
            empty = self.make_label(
                "هنوز محصولی وجود ندارد.\nبرای افزودن محصول روی «افزودن» بزنید.",
                size=17,
                color=c["muted"],
                halign="center"
            )

            empty.size_hint_y = None
            empty.height = dp(100)

            self.product_list.add_widget(empty)
            return

        visible = [
            (index, product)
            for index, product in enumerate(self.products)
            if search_text in str(
                product.get("name", "")
            ).lower()
        ]

        if not visible:
            empty = self.make_label(
                "محصولی پیدا نشد.",
                size=17,
                color=c["muted"],
                halign="center"
            )

            empty.size_hint_y = None
            empty.height = dp(80)

            self.product_list.add_widget(empty)
            return

        for index, product in visible:
            self.add_product_card(
                product,
                index
            )

    def add_product_card(self, product, index):
        c = self.colors()

        card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(190),
            padding=[
                dp(10),
                dp(9),
                dp(10),
                dp(9)
            ],
            spacing=dp(3)
        )

        self.add_card_background(card)

        name_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32)
        )

        name = str(product.get("name", ""))

        qty = self.safe_int(
            product.get("qty", 0)
        )

        low = self.safe_int(
            product.get("low", 0)
        )

        name_label = self.make_label(
            name,
            size=18,
            bold=True
        )

        name_row.add_widget(name_label)

        if qty <= low:
            warning = self.make_label(
                "[موجودی کم]",
                size=12,
                color=c["red"],
                bold=True,
                halign="right"
            )

            warning.size_hint_x = None
            warning.width = dp(105)

            name_row.add_widget(warning)

        card.add_widget(name_row)

        purchase = self.safe_float(
            product.get("purchase_price", 0)
        )

        sale = self.safe_float(
            product.get("sale_price", 0)
        )

        info = self.make_label(
            "قیمت خرید: %.2f\n"
            "قیمت فروش: %.2f\n"
            "تعداد: %d\n"
            "حد هشدار: %d"
            % (
                purchase,
                sale,
                qty,
                low
            ),
            size=13,
            color=c["muted"]
        )

        info.size_hint_y = None
        info.height = dp(82)

        card.add_widget(info)

        edit = self.make_button(
            "ویرایش",
            lambda *_args, i=index: self.edit_product(i),
            bg=c["blue"],
            height=42,
            font_size=14
        )

        card.add_widget(edit)

        self.product_list.add_widget(card)

    # -----------------------------
    # CREATE PAGE
    # -----------------------------
    def create_page(self):
        self.current_page = "create"
        self.main_area.clear_widgets()

        c = self.colors()

        self.main_area.add_widget(
            self.make_header("افزودن محصول")
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(2), dp(6), dp(2), dp(12)],
            size_hint_y=None
        )

        form.bind(
            minimum_height=form.setter("height")
        )

        title = self.make_label(
            "افزودن محصول",
            size=21,
            bold=True
        )

        title.size_hint_y = None
        title.height = dp(42)

        form.add_widget(title)

        self.name_input = self.make_text_input(
            "نام محصول"
        )

        self.qty_input = self.make_text_input(
            "تعداد",
            input_filter="int"
        )

        self.purchase_input = self.make_text_input(
            "قیمت خرید",
            input_filter="float"
        )

        self.sale_input = self.make_text_input(
            "قیمت فروش",
            input_filter="float"
        )

        self.low_input = self.make_text_input(
            "حد هشدار موجودی کم",
            input_filter="int"
        )

        form.add_widget(self.name_input)
        form.add_widget(self.qty_input)
        form.add_widget(self.purchase_input)
        form.add_widget(self.sale_input)
        form.add_widget(self.low_input)

        note = self.make_label(
            "وارد کردن قیمت‌ها اختیاری است.",
            size=12,
            color=c["muted"]
        )

        note.size_hint_y = None
        note.height = dp(28)

        form.add_widget(note)

        form.add_widget(
            BoxLayout(
                size_hint_y=None,
                height=dp(5)
            )
        )

        save_button = self.make_button(
            "ذخیره محصول",
            self.save_product,
            bg=c["green"],
            height=52,
            font_size=15
        )

        form.add_widget(save_button)

        scroll.add_widget(form)

        self.main_area.add_widget(scroll)

    def save_product(self, *_):
        name = self.name_input.text.strip()

        if not name:
            self.message(
                "خطا",
                "نام محصول الزامی است."
            )
            return

        qty_text = self.qty_input.text.strip()
        purchase_text = self.purchase_input.text.strip()
        sale_text = self.sale_input.text.strip()
        low_text = self.low_input.text.strip()

        # Quantity and low-stock level are required numeric fields.
        if not qty_text or not low_text:
            self.message(
                "خطا",
                "لطفاً اعداد معتبر وارد کنید."
            )
            return

        try:
            qty = int(qty_text)
            low = int(low_text)

            if qty < 0 or low < 0:
                raise ValueError

            purchase = (
                float(purchase_text)
                if purchase_text
                else 0.0
            )

            sale = (
                float(sale_text)
                if sale_text
                else 0.0
            )

            if purchase < 0 or sale < 0:
                raise ValueError

        except (ValueError, TypeError):
            self.message(
                "خطا",
                "لطفاً اعداد معتبر وارد کنید."
            )
            return

        product = {
            "name": name,
            "qty": qty,
            "purchase_price": purchase,
            "sale_price": sale,
            "low": low
        }

        self.products.append(product)

        self.save_data()

        self.show_page("products")

    # -----------------------------
    # EDIT PRODUCT
    # -----------------------------
    def edit_product(self, index):
        if index < 0 or index >= len(self.products):
            return

        product = self.products[index]
        c = self.colors()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[
                dp(12),
                dp(12),
                dp(12),
                dp(12)
            ]
        )

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3)
        )

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(9),
            size_hint_y=None
        )

        form.bind(
            minimum_height=form.setter("height")
        )

        name_input = self.make_text_input(
            "نام محصول"
        )
        name_input.text = str(
            product.get("name", "")
        )

        qty_input = self.make_text_input(
            "تعداد",
            input_filter="int"
        )
        qty_input.text = str(
            self.safe_int(
                product.get("qty", 0)
            )
        )

        purchase_input = self.make_text_input(
            "قیمت خرید",
            input_filter="float"
        )
        purchase_value = self.safe_float(
            product.get("purchase_price", 0)
        )
        purchase_input.text = (
            str(purchase_value)
            if purchase_value != 0
            else ""
        )

        sale_input = self.make_text_input(
            "قیمت فروش",
            input_filter="float"
        )
        sale_value = self.safe_float(
            product.get("sale_price", 0)
        )
        sale_input.text = (
            str(sale_value)
            if sale_value != 0
            else ""
        )

        low_input = self.make_text_input(
            "حد هشدار موجودی کم",
            input_filter="int"
        )
        low_input.text = str(
            self.safe_int(
                product.get("low", 0)
            )
        )

        form.add_widget(name_input)
        form.add_widget(qty_input)
        form.add_widget(purchase_input)
        form.add_widget(sale_input)
        form.add_widget(low_input)

   
