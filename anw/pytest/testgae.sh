#!/bin/sh
clear
pkill -9 -f dev_appserver.py
./gaesetup.sh
sleep 3
PYTHONPATH=../Packages/ py.test agae/*.py --verbose --showlocals
