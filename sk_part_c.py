import json
import os
import shutil

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


def format_price(value):
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return str(num)
    except (ValueError, TypeError):
        return str(value)


class PartC:

    def alerts_page(self):
        self.current_page = "alerts"
        self.main_area.clear_widgets()
        c = self.colors()

        self.main_area.add_widget(self.make_header("هشدارهای موجودی کم"))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))

        alert_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[dp(1), dp(5), dp(1), dp(10)],
            size_hint_y=None
        )
        alert_list.bind(minimum_height=alert_list.setter("height"))

        low_products = []
        for index, product in enumerate(self.products):
            qty = self.safe_int(product.get("qty", 0))
            low = self.safe_int(product.get("low", 0))
            if qty <= low:
                low_products.append((index, product))

        if not low_products:
            empty = self.make_label(
                "محصولی با موجودی کم وجود ندارد.",
                size=17, color=c["muted"], halign="center"
            )
            empty.size_hint_y = None
            empty.height = dp(90)
            alert_list.add_widget(empty)
        else:
            for index, product in low_products:
                card = BoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(145),
                    padding=[dp(12), dp(10), dp(12), dp(10)],
                    spacing=dp(3)
                )
                self.add_card_background(card)

                warning = self.make_label("هشدار", size=17, color=c["red"], bold=True)
                warning.size_hint_y =
