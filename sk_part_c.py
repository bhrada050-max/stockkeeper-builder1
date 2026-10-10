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
                warning.size_hint_y = None
                warning.height = dp(30)
                card.add_widget(warning)

                product_label = self.make_label(
                    "محصول: %s" % str(product.get("name", "")),
                    size=15
                )
                product_label.size_hint_y = None
                product_label.height = dp(25)
                card.add_widget(product_label)

                qty = self.safe_int(product.get("qty", 0))
                low = self.safe_int(product.get("low", 0))

                details = self.make_label(
                    "فقط %d عدد باقی مانده\n"
                    "Alert level: %d\n"
                    "لطفاً به‌زودی موجودی را افزایش دهید."
                    % (qty, low),
                    size=13, color=c["muted"]
                )
                details.size_hint_y = None
                details.height = dp(65)
                card.add_widget(details)

                alert_list.add_widget(card)

        scroll.add_widget(alert_list)
        self.main_area.add_widget(scroll)

    def product_details(self, index):
        if index < 0 or index >= len(self.products):
            return

        c = self.colors()
        product = self.products[index]

        name = str(product.get("name", ""))
        qty = self.safe_int(product.get("qty", 0))
        low = self.safe_int(product.get("low", 0))
        purchase = self.safe_float(product.get("purchase_price", 0))
        sale = self.safe_float(product.get("sale_price", 0))
        date = str(product.get("date", "") or "").strip()
        desc = str(product.get("desc", "") or "").strip()

        status = "موجودی کم" if qty <= low else "موجود"
        status_color = c["red"] if status == "موجودی کم" else c["green"]

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(14), dp(14), dp(14), dp(14)]
        )

        title_label = self.make_label(
            "جزئیات محصول",
            size=18,
            bold=True,
            halign="center"
        )
        title_label.size_hint_y = None
        title_label.height = dp(40)
        content.add_widget(title_label)

        name_title = self.make_label(name, size=21, bold=True)
        name_title.size_hint_y = None
        name_title.height = dp(42)
        content.add_widget(name_title)

        info_text = (
            "قیمت خرید: %s\n"
            "قیمت فروش: %s\n"
            "تعداد: %d\n"
            "حد هشدار: %d"
            % (format_price(purchase), format_price(sale), qty, low)
        )
        if date:
            info_text += "\nتاریخ: " + date
        if desc:
            info_text += "\nتوضیحات: " + desc

        info = self.make_label(info_text, size=16)
        content.add_widget(info)

        status_label = self.make_label(
            "وضعیت: %s" % status,
            size=16,
            color=status_color,
            bold=True
        )
        status_label.size_hint_y = None
        status_label.height = dp(40)
        content.add_widget(status_label)

        close_button = self.make_button("بستن", bg=c["panel2"], height=48)
        content.add_widget(close_button)

        popup = Popup(
            content=content,
            size_hint=(0.90, 0.80),
            auto_dismiss=True,
            title="",
            separator_height=0
        )

        close_button.bind(on_release=popup.dismiss)
        popup.open()

    def message(self, title, text):
        c = self.colors()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(18), dp(18), dp(18), dp(18)]
        )

        title_label = self.make_label(
            title,
            size=18,
            bold=True,
            halign="center"
        )
        title_label.size_hint_y = None
        title_label.height = dp(40)
        content.add_widget(title_label)

        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4)
        )

        label = self.make_label(
            text,
            size=15,
            halign="center",
            valign="middle"
        )
        label.size_hint_y = None
        label.bind(
            width=lambda obj, w: setattr(
                obj, "text_size", (w - dp(10), None)
            ),
            texture_size=lambda obj, ts: setattr(
                obj, "height", ts[1] + dp(20)
            )
        )
        scroll.add_widget(label)
        content.add_widget(scroll)

        close = self.make_button("بستن", bg=c["panel2"], height=48)
        content.add_widget(close)

        popup = Popup(
            content=content,
            size_hint=(0.92, 0.75),
            auto_dismiss=True,
            title="",
            separator_height=0
        )

        close.bind(on_release=popup.dismiss)
        popup.open()

    def change_theme(self, *_):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def data_file(self):
        return os.path.join(self.user_data_dir, "stockkeeper_data.json")

    def load_data(self):
        self.products = []

        try:
            path = self.data_file()
            if not os.path.exists(path):
                return

            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                return

            clean = []

            for item in data:
                if not isinstance(item, dict):
                    continue

                name = str(item.get("name", "")).strip()
                if not name:
                    continue

                try:
                    qty = int(item.get("qty", 0))
                    low = int(item.get("low", 0))

                    if "purchase_price" in item:
                        purchase = float(item.get("purchase_price", 0))
                    else:
                        purchase = 0.0

                    if "sale_price" in item:
                        sale = float(item.get("sale_price", 0))
                    else:
                        sale = float(item.get("price", 0))

                except (ValueError, TypeError):
                    continue

                if qty < 0 or low < 0 or purchase < 0 or sale < 0:
                    continue

                clean.append({
                    "name": name,
                    "qty": qty,
                    "purchase_price": purchase,
                    "sale_price": sale,
                    "low": low,
                    "desc": str(item.get("desc", "") or "").strip(),
                    "date": str(item.get("date", "") or "").strip()
                })

            self.products = clean

        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.products = []

    def save_data(self):
        try:
            path = self.data_file()
            folder = os.path.dirname(path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)

            temp_path = path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(self.products, file, ensure_ascii=False, indent=2)

            try:
                os.replace(temp_path, path)
            except OSError:
                with open(path, "w", encoding="utf-8") as file:
                    json.dump(self.products, file, ensure_ascii=False, indent=2)
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            return True

        except (OSError, TypeError, ValueError):
            return False

    def safe_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def safe_float(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _copy_to_clipboard(self, text):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(text)
            return True
        except Exception:
            return False

    def _paste_from_clipboard(self):
        try:
            from kivy.core.clipboard import Clipboard
            return Clipboard.paste()
        except Exception:
            return ""

    def export_data(self, *_):
        try:
            data_text = json.dumps(
                self.products,
                ensure_ascii=False,
                indent=2
            )

            ok = self._copy_to_clipboard(data_text)

            if ok:
                self.message(
                    "موفق",
                    "محتوا تو کلیپ‌بورد کپی شد.\n\n"
                    "الان برو تلگرام یا واتساپ، پیست کن و بفرست به خودت."
                )
            else:
                self.message("خطا", "کپی نشد.")
        except Exception as e:
            self.message("خطا", "خطا:\n" + str(e))

    def import_data(self, *_):
        try:
            text = self._paste_from_clipboard()

            if not text or not text.strip():
                self.message(
                    "خطا",
                    "کلیپ‌بورد خالیه.\n\n"
                    "اول محتوای بکاپ رو از تلگرام/واتساپ کپی کن."
                )
                return

            text = text.strip()

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                self.message("خطا", "متن کپی‌شده معتبر نیست.")
                return

            if not isinstance(data, list):
                self.message("خطا", "فایل خراب است.")
                return

            self.products = data
            self.save_data()
            self.message(
                "موفق",
                "بازگردانی شد. تعداد: %d" % len(self.products)
            )

            if self.current_page == "settings":
                self.settings_page()
            elif self.current_page == "products":
                self.refresh_products()
        except Exception as e:
            self.message("خطا", "خطا:\n" + str(e))

    def share_backup(self, *_):
        self.message(
            "راهنما",
            "۱. دکمه «خروجی گرفتن» رو بزن\n"
            "۲. محتوا تو کلیپ‌بورد کپی می‌شه\n"
            "۳. برو تلگرام، پیست کن، بفرست به خودت\n\n"
            "برای بازگردانی:\n"
            "۱. محتوا رو از تلگرام کپی کن\n"
            "۲. تو اپ، دکمه «وارد کردن» رو بزن"
        )
