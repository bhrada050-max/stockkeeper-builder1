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
