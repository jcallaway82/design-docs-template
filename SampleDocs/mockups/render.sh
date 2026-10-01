#!/bin/sh
# Renders each mNN_*.html to PNG with headless Edge (1600x934 incl. caption bar).
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
cd "$(dirname "$0")"
for f in ${@:-m*.html}; do
  b="${f%.html}"
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1602,904 --virtual-time-budget=4000 --screenshot="$(pwd -W)/$b.png" "file:///$(pwd -W)/$f" >/dev/null 2>&1
  echo "$b.png $(stat -c %s "$b.png" 2>/dev/null)"
done
