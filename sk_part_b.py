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
from desc_ui import wrapped_label


class PartB:

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

        desc = str(product.get("desc", "") or "").strip()
        if desc:
            desc_label = wrapped_label(
                "توضیحات: " + desc,
                size=13,
                color=c["text"]
            )

            def fit_card(*_args, lbl=desc_label):
                card.height = dp(190) + lbl.height + dp(3)

            desc_label.bind(height=fit_card)
            fit_card()
            card.add_widget(desc_label)

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

        self.main_area.add_widget(
            self.make_header("افزودن محصول")
        )

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

        self.name_input = self.make_text_input("نام محصول", persian=True)
        self.qty_input = self.make_text_input("تعداد", input_filter="int")
        self.purchase_input = self.make_text_input("قیمت خرید", input_filter="float")
        self.sale_input = self.make_text_input("قیمت فروش", input_filter="float")
        self.low_input = self.make_text_input("حد هشدار موجودی کم", input_filter="int")

        form.add_widget(self.name_input)
        form.add_widget(self.qty_input)
        form.add_widget(self.purchase_input)
        form.add_widget(self.sale_input)
        form.add_widget(self.low_input)

        self.desc_input = self.make_text_input(
            "توضیحات (اگر داری بنویس)",
            persian=True
        )
        form.add_widget(self.desc_input)

        self.desc_preview = wrapped_label(
            "",
            size=13,
            color=c["muted"]
        )
        self.desc_input.bind(
            logical=lambda _inst, value:
            self.desc_preview.set_raw(value)
        )
        form.add_widget(self.desc_preview)

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
        name = self.name_input.logical.strip()
        desc = self.desc_input.logical.strip()

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
            "low": low,
            "desc": desc
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

        name_input = self.make_text_input("نام محصول", persian=True)
        name_input.set_logical(product.get("name", ""))

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

        desc_input = self.make_text_input("توضیحات (اگر داری بنویس)", persian=True)
        desc_input.set_logical(product.get("desc", ""))
        form.add_widget(desc_input)

        desc_preview = wrapped_label(
            str(product.get("desc", "") or ""),
            size=13,
            color=c["muted"]
        )
        desc_input.bind(
            logical=lambda _inst, value:
            desc_preview.set_raw(value)
        )
        form.add_widget(desc_preview)

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
            title=rtl_text("ویرایش محصول"),
            content=content,
            size_hint=(0.94, 0.82),
            auto_dismiss=False,
            title_size=dp(18)
        )

        def save_changes(*_):
            new_name = name_input.logical.strip()
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
                if new_qty < 0 or new_low < 0 or new_purchase < 0 or new_sale < 0:
                    raise ValueError
            except (ValueError, TypeError):
                self.message("خطا", "لطفاً اعداد معتبر وارد کنید.")
                return

            product["name"] = new_name
            product["qty"] = new_qty
            product["purchase_price"] = new_purchase
            product["sale_price"] = new_sale
            product["low"] = new_low
            product["desc"] = desc_input.logical.strip()

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

        label = self.make_label(
            "این محصول حذف شود؟",
            size=16,
            halign="center"
        )
        content.add_widget(label)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(7)
        )

        yes = self.make_button("حذف", bg=c["red"], height=46)
        no = self.make_button("لغو", bg=c["panel2"], height=46)

        buttons.add_widget(yes)
        buttons.add_widget(no)
        content.add_widget(buttons)

        popup = Popup(
            title=rtl_text("تأیید حذف"),
            content=content,
            size_hint=(0.88, 0.38),
            auto_dismiss=False,
            title_size=dp(18)
        )

        def do_delete(*_):
            if 0 <= index < len(self.products):
                self.products.pop(index)
            self.save_data()
            popup.dismiss()
            edit_popup.dismiss()
            self.refresh_products()

        yes.bind(on_release=do_delete)
        no.bind(on_release=popup.dismiss)

        popup.open()

    def settings_page(self):
        self.current_page = "settings"
        self.main_area.clear_widgets()
        c = self.colors()

        self.main_area.add_widget(
            self.make_header("تنظیمات")
        )

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(4))

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(6), dp(6), dp(6), dp(12)],
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        info_card = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(6)
        )
        self.add_card_background(info_card)

        info_title = self.make_label("اطلاعات", size=18, bold=True)
        info_title.size_hint_y = None
        info_title.height = dp(30)
        info_card.add_widget(info_title)

        total_products = len(self.products)
        total_qty = sum(
            self.safe_int(p.get("qty", 0))
            for p in self.products
        )

        info_text = self.make_label(
            "تعداد محصولات: %d\n"
            "مجموع موجودی: %d"
            % (total_products, total_qty),
            size=14,
            color=c["muted"]
        )
        info_text.size_hint_y = None
        info_text.height = dp(70)
        info_card.add_widget(info_text)

        content.add_widget(info_card)

        backup_title = self.make_label("پشتیبان‌گیری", size=18, bold=True)
        backup_title.size_hint_y = None
        backup_title.height = dp(35)
        content.add_widget(backup_title)

        export_btn = self.make_button(
            "خروجی گرفتن (ذخیره فایل)",
            self.export_data,
            bg=c["green"],
            height=52,
            font_size=15
        )
        content.add_widget(export_btn)

        import_btn = self.make_button(
            "وارد کردن (بازگردانی از فایل)",
            self.import_data,
            bg=c["blue"],
            height=52,
            font_size=15
        )
        content.add_widget(import_btn)

        note = self.make_label(
            "فایل پشتیبان در پوشه Download ذخیره می‌شود.",
            size=12,
            color=c["muted"]
        )
        note.size_hint_y = None
        note.height = dp(40)
        content.add_widget(note)

        content.add_widget(BoxLayout(size_hint_y=None, height=dp(10)))

        delete_title = self.make_label(
            "منطقه خطر",
            size=18,
            bold=True,
            color=c["red"]
        )
        delete_title.size_hint_y = None
        delete_title.height = dp(35)
        content.add_widget(delete_title)

        delete_all_btn = self.make_button(
            "حذف همه محصولات",
            self.confirm_delete_all,
            bg=c["red"],
            height=52,
            font_size=15
        )
        content.add_widget(delete_all_btn)

        scroll.add_widget(content)
        self.main_area.add_widget(scroll)

    def confirm_delete_all(self, *_):
        c = self.colors()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(12), dp(12), dp(12), dp(12)]
        )

        label = self.make_label(
            "همه محصولات حذف شوند؟\nاین عمل قابل بازگشت نیست!",
            size=16,
            halign="center",
            color=c["red"]
        )
        content.add_widget(label)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(7)
        )

        yes = self.make_button("حذف همه", bg=c["red"], height=46)
        no = self.make_button("لغو", bg=c["panel2"], height=46)

        buttons.add_widget(yes)
        buttons.add_widget(no)
        content.add_widget(buttons)

        popup = Popup(
            title=rtl_text("تأیید حذف"),
            content=content,
            size_hint=(0.88, 0.42),
            auto_dismiss=False,
            title_size=dp(18)
        )

        def do_delete(*_):
            self.products = []
            self.save_data()
            popup.dismiss()
            self.settings_page()

        yes.bind(on_release=do_delete)
        no.bind(on_release=popup.dismiss)
        popup.open()
