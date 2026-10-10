from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

from rtl_fix import *
from sk_part_a import PartA
from sk_part_b import PartB
from sk_part_c import PartC


class StockKeeper(PartA, PartB, PartC, App):
    pass


def request_storage_permissions():
    if platform != "android":
        return

    # نسخه اندروید رو چک می‌کنیم
    from jnius import autoclass
    Build = autoclass("android.os.Build$VERSION")
    sdk = Build.SDK_INT

    # برای اندروید ۱۱ به بالا (API 30+)
    if sdk >= 30:
        from jnius import autoclass
        Environment = autoclass("android.os.Environment")
        Intent = autoclass("android.content.Intent")
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        if not Environment.isExternalStorageManager():
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            intent.setData(Uri.parse("package:" + PythonActivity.mActivity.getPackageName()))
            PythonActivity.mActivity.startActivity(intent)
    else:
        # برای اندروید ۱۰ و پایین‌تر
        request_permissions([
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ])


if __name__ == "__main__":
    request_storage_permissions()
    StockKeeper().run()
