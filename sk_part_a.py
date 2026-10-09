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


class PartA:
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
        elif self.current_page == "settings":
            self.settings_page()

        self.update_nav_theme()

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

    def make_bottom_nav(self):
        c = self.colors()

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            spacing=dp(4)
        )

        self.nav_products = self.make_button(
            "محصولات",
            lambda *_: self.show_page("products"),
            bg=c["panel2"],
            height=52,
            font_size=12
        )

        self.nav_create = self.make_button(
            "افزودن",
            lambda *_: self.show_page("create"),
            bg=c["panel2"],
            height=52,
            font_size=12
        )

        self.nav_alerts = self.make_button(
            "هشدارها",
            lambda *_: self.show_page("alerts"),
            bg=c["panel2"],
            height=52,
            font_size=12
        )

        self.nav_settings = self.make_button(
            "تنظیمات",
            lambda *_: self.show_page("settings"),
            bg=c["panel2"],
            height=52,
            font_size=12
        )

        nav.add_widget(self.nav_products)
        nav.add_widget(self.nav_create)
        nav.add_widget(self.nav_alerts)
        nav.add_widget(self.nav_settings)

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

        self.nav_settings.background_color = (
            c["blue"] if self.current_page == "settings"
            else c["panel2"]
        )

        self.nav_products.color = c["text"]
        self.nav_create.color = c["text"]
        self.nav_alerts.color = c["text"]
        self.nav_settings.color = c["text"]

    def show_page(self, page):
        self.current_page = page
        self.main_area.clear_widgets()

        if page == "products":
            self.products_page()
        elif page == "create":
            self.create_page()
        elif page == "alerts":
            self.alerts_page()
        elif page == "settings":
            self.settings_page()

        self.update_nav_theme()

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
            or search_text in str(
                product.get("desc", "") or ""
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
