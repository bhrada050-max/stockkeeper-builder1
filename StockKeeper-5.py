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

from rtl_fix import *
from sk_part_a import PartA
from sk_part_b import PartB
from sk_part_c import PartC


class StockKeeper(PartA, PartB, PartC, App):
    pass


# ---------------------------------------------------------------------------
# Crash viewer: instead of the app closing silently, show the error on screen
# (and save it to crash_log.txt inside the app's data folder).
# ---------------------------------------------------------------------------
def _save_crash(text):
    try:
        folder = App.get_running_app().user_data_dir if App.get_running_app() else BASE_DIR
        with open(os.path.join(folder, "crash_log.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


def _show_crash_popup(text):
    try:
        box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        viewer = TextInput(
            text=text,
            readonly=True,
            font_size=dp(11),
            font_name="Roboto"
        )
        close = Button(text="Close", size_hint_y=None, height=dp(44))
        box.add_widget(viewer)
        box.add_widget(close)
        popup = Popup(
            title="Error (send a screenshot of this)",
            content=box,
            size_hint=(0.98, 0.9),
            auto_dismiss=False
        )
        close.bind(on_release=popup.dismiss)
        popup.open()
    except Exception:
        pass


def _install_crash_handler():
    try:
        import traceback
        from kivy.base import ExceptionHandler, ExceptionManager

        class CrashHandler(ExceptionHandler):
            def handle_exception(self, inst):
                text = "".join(
                    traceback.format_exception(
                        type(inst), inst, inst.__traceback__
                    )
                )
                _save_crash(text)
                Clock.schedule_once(
                    lambda *_: _show_crash_popup(text), 0
                )
                return ExceptionManager.PASS

        ExceptionManager.add_handler(CrashHandler())
    except Exception:
        pass


class CrashApp(App):
    def build(self):
        box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        box.add_widget(
            TextInput(
                text=self.crash_text,
                readonly=True,
                font_size=dp(11),
                font_name="Roboto"
            )
        )
        return box


if __name__ == "__main__":
    _install_crash_handler()

    try:
        StockKeeper().run()
    except Exception:
        import traceback

        error_text = traceback.format_exc()
        _save_crash(error_text)
        CrashApp.crash_text = error_text
        CrashApp().run()
