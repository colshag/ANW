#!/bin/sh
clear
PYTHONPATH=../Packages/ py.test war/*.py --verbose --showlocals
