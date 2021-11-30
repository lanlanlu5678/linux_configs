#!/usr/bin/zsh
# V2Ray Proxy
~/.v2ray/v2admin.sh start

# Start X Window
if [ -z "${DISPLAY}" ] && [ "${XDG_VTNR}" -eq 1 ]; then
	startx
fi
