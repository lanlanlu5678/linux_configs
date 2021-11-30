#!/bin/sh

# Environment
export GTK_IM_MODULE=fcitx
export XMODIFIERS="@im=fcitx"

# Input Method
exec fcitx5 > /dev/null 2>&1 &

# For services depend on dwm
~/.delay.sh &

# Window Manager
exec dwm
