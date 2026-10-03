#!/data/data/com.termux/files/usr/bin/bash
set -e
G="\033[1;32m"; R="\033[1;31m"; Y="\033[1;33m"
B="\033[1;34m"; C="\033[1;36m"; N="\033[0m"
step()  { echo -e "\n${B}▶ $1${N}"; }
ok()    { echo -e "${G}✔ $1${N}"; }
warn()  { echo -e "${Y}⚠ $1${N}"; }
err()   { echo -e "${R}✘ $1${N}"; }

APP_TITLE="StockKeeper"
PKG_NAME="stockkeeper"
PKG_DOMAIN="org.mystore"
MAIN_FILE="StockKeeper.py"
VERSION="1.0.0"
WORK_DIR="$HOME/StockKeeperBuild"

echo "شروع ساخت خودکار StockKeeper"

step "بررسی و نصب پیش‌نیازها"
pkg update -y >/dev/null 2>&1 || true
for p in python git openjdk-17 wget unzip zip ncurses-utils; do
    if ! dpkg -s "$p" >/dev/null 2>&1; then
        pkg install -y "$p" >/dev/null 2>&1 || true
    fi
done
ok "پیش‌نیازها آماده شد"

step "نصب buildozer"
python -m pip install --upgrade pip wheel setuptools >/dev/null 2>&1 || true
python -m pip install --upgrade buildozer cython >/dev/null 2>&1
ok "buildozer نصب شد"

step "آماده‌سازی پوشه کاری"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

if [ ! -f "$MAIN_FILE" ]; then
    FOUND=$(find /sdcard /storage/emulated/0 "$HOME" -maxdepth 4 -name "$MAIN_FILE" 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        cp "$FOUND" "$WORK_DIR/$MAIN_FILE"
        ok "فایل پیدا شد"
    else
        err "فایل $MAIN_FILE پیدا نشد"
        exit 1
    fi
fi

step "ساخت buildozer.spec"
cat > buildozer.spec << EOF
[app]
title = $APP_TITLE
package.name = $PKG_NAME
package.domain = $PKG_DOMAIN
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = $VERSION
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = 
android.accept_sdk_license = True
EOF
ok "buildozer.spec ساخته شد"

step "شروع بیلد APK"
warn "اولین بیلد ۲۰-۴۰ دقیقه طول می‌کشد"
buildozer -v android debug

step "کپی APK"
APK=$(find bin -name "*.apk" 2>/dev/null | head -1)
if [ -n "$APK" ]; then
    cp "$APK" "/sdcard/Download/stockkeeper-debug.apk"
    ok "APK آماده شد: /sdcard/Download/stockkeeper-debug.apk"
else
    err "APK ساخته نشد"
    exit 1
fi
