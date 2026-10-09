"""Word-wrapped Persian label (auto height) used for product descriptions."""
from kivy.core.text import Label as CoreLabel
from kivy.metrics import dp
from kivy.uix.label import Label

from rtl_fix import FONT_NAME, rtl_text

_MEASURE = {}


def _text_width(text, size):
    key = round(float(size), 1)
    core = _MEASURE.get(key)
    if core is None:
        core = CoreLabel(font_name=FONT_NAME, font_size=size)
        _MEASURE[key] = core
    return core.get_extents(text)[0]


def wrap_text(raw, width, size):
    """Wrap in normal reading order, then convert every line for display."""
    try:
        lines = []
        for paragraph in str(raw).split("\n"):
            current = ""
            for word in paragraph.split(" "):
                candidate = (current + " " + word) if current else word
                if current and _text_width(rtl_text(candidate), size) > width:
                    lines.append(current)
                    current = word
                else:
                    current = candidate
            lines.append(current)
        # trailing space = small safety margin so the first (right-most)
        # letter is never clipped at the label edge
        return "\n".join(rtl_text(line) + " " for line in lines)
    except Exception:
        return rtl_text(raw)


def wrapped_label(raw, size=14, color=(1, 1, 1, 1), halign="right"):
    label = Label(
        text=rtl_text(raw),
        font_size=dp(size),
        color=color,
        halign=halign,
        valign="top",
        font_name=FONT_NAME,
        size_hint_y=None,
        height=dp(6),
    )
    label._raw = str(raw or "")

    def relayout(obj, *_):
        width = obj.width
        if width <= dp(20):
            return
        obj.text_size = (width, None)
        new_text = wrap_text(obj._raw, width - dp(4), obj.font_size)
        if new_text != obj.text:
            obj.text = new_text

    def fit(obj, tex_size):
        obj.height = tex_size[1] + dp(6)

    def set_raw(value):
        label._raw = str(value or "")
        if not label._raw:
            label.text = ""
        relayout(label)

    label.set_raw = set_raw
    label.bind(width=relayout, texture_size=fit)
    return label
