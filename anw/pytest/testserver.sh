#!/bin/sh
clear
./gaesetup.sh
sleep 3
PYTHONPATH=../Packages/ py.test agae/*.py --verbose --showlocals
PYTHONPATH=../Packages/ py.test server/*.py --verbose --showlocals
pkill -9 -f dev_appserver.py