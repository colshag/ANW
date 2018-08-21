#!/bin/sh
pkill -9 -f dev_appserver.py
clear
./gaesetup.sh
sleep 3
PYTHONPATH=../Packages/ py.test --showlocals -vv
pkill -9 -f dev_appserver.py
