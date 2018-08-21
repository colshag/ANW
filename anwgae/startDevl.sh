#!/bin/sh
pkill -9 -f dev_appserver.py
clear
dev_appserver.py --port 8090 --admin_port 8091 --clear_datastore true anetwars
