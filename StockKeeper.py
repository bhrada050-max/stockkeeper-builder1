import json
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

LabelBase.register(
    name="Vazir",
    fn_regular="Vazirmatn-Regular.ttf",
    fn_bold="Vazirmatn-Bold.ttf"
)


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

    def make_label(self, text="", size=16, color=None, bold=False, halign="left", valign="middle"):
        c = self.colors()
        label = Label(
            text=text,
            font_size=dp(size),
            color=color if color else c["text"],
            bold=bold,
            halign=halign,
            valign=valign,
            font_name="Vazir"
        )
        label.bind(
            size=lambda obj, value: setattr(obj, "text_size", (obj.width - dp(4), None))
        )
        return label

    def make_button(self, text, callback=None, bg=None, height=46, font_size=14):
        c = self.colors()
        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            font_size=dp(font_size),
            color=c["text"],
            background_normal="",
            background_down="",
            background_color=bg if bg else c["panel2"],
            font_name="Vazir"
        )
        if callback:
            button.bind(on_release=callback)
        return button

    def make_text_input(self, hint, multiline=False, input_filter=None):
        c = self.colors()
        field = TextInput(
            hint_text=hint,
            multiline=multiline,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name="Vazir"
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
        self.nav_products.background_color = (
            c["green"] if self.current_page == "products" else c["panel2"]
        )
        self.nav_create.background_color = (
            c["green"] if self.current_page == "create" else c["panel2"]
        )
        self.nav_alerts.background_color = (
            c["red"] if self.current_page == "alerts" else c["panel2"]
        )
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
        self.search_input = TextInput(
            hint_text="جستجوی محصولات...",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16),
            foreground_color=c["text"],
            hint_text_color=c["muted"],
            background_color=c["input"],
            padding=[dp(12), dp(12)],
            cursor_color=c["text"],
            font_name="Vazir"
        )
        self.search_input.bind(text=self.search_changed)
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
            search_text = search_widget.text if search_widget else ""
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

   
