def upload_text(text):
    try:
        import ssl
        import certifi
        import urllib.request

        ctx = ssl.create_default_context(cafile=certifi.where())
        data = text.encode("utf-8")

        req = urllib.request.Request(
            "https://paste.rs/",
            data=data,
            method="POST",
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "User-Agent": "StockKeeper/1.0"
            }
        )

        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            url = response.read().decode("utf-8").strip()
            if url.startswith("http"):
                return url
    except Exception:
        pass

    return None


def download_text(url):
    try:
        import ssl
        import certifi
        import urllib.request

        ctx = ssl.create_default_context(cafile=certifi.where())

        url = url.strip().rstrip("/")
        if not url.startswith("http"):
            return None

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "StockKeeper/1.0"}
        )

        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None               "purchase_price": purchase,
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

    def export_data(self, *_):
        data_text = json.dumps(
            self.products,
            ensure_ascii=False,
            indent=2
        )

        self.message("لطفاً صبر کنید...", "در حال ساخت کد بکاپ...")

        def do_upload(dt):
            url = upload_text(data_text)

            Clock.schedule_once(
                lambda dt: self._show_export_result(url), 0
            )

        Clock.schedule_once(do_upload, 0.1)

    def _show_export_result(self, url):
        if url:
            copy_to_clipboard(url)

            self.message(
                "بکاپ ساخته شد",
                "کد بکاپ شما:\n\n" + url +
                "\n\n(این کد در کلیپ‌بورد کپی شد)\n\n"
                "این کد رو تو تلگرام برای خودت بفرست تا همیشه داشته باشی."
            )
        else:
            self.message(
                "خطا",
                "ساخته نشد. اینترنت رو چک کن و دوباره امتحان کن."
            )

    def import_data(self, *_):
        url = paste_from_clipboard().strip()

        if not url or not url.startswith("http"):
            self.message(
                "خطا",
                "اول کد بکاپ رو از تلگرام کپی کن، بعد این دکمه رو بزن."
            )
            return

        self.message("لطفاً صبر کنید...", "در حال بازگردانی از کد:\n\n" + url)

        def do_download(dt):
            text = download_text(url)

            Clock.schedule_once(
                lambda dt: self._do_import_from_text(text), 0
            )

        Clock.schedule_once(do_download, 0.1)

    def _do_import_from_text(self, text):
        if not text:
            self.message("خطا", "بازگردانی نشد. اینترنت رو چک کن.")
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            self.message("خطا", "کد بکاپ معتبر نیست.")
            return

        if not isinstance(data, list):
            self.message("خطا", "کد بکاپ خراب است.")
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

    def share_backup(self, *_):
        self.message(
            "راهنمای بکاپ",
            "بکاپ چیه؟\n"
            "یه کد اینترنتی هست که اطلاعات محصولاتت رو نگه می‌داره.\n\n"
            "چطور بکاپ بگیرم؟\n"
            "1. دکمه «خروجی گرفتن» رو بزن\n"
            "2. چند ثانیه صبر کن\n"
            "3. یه کد بهت می‌ده\n"
            "4. اون کد رو تو تلگرام برای خودت بفرست\n\n"
            "چطور بکاپ رو برگردونم؟\n"
            "1. کد بکاپ رو از تلگرام کپی کن\n"
            "2. دکمه «وارد کردن» رو بزن\n"
            "3. اطلاعاتت برمی‌گرده"
                )
