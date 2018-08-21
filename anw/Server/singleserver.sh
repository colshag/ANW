#!/bin/bash
#
# Start the server for LOCAL GAE TESTING
# Arguments allowed
#
# -d <database> (defaults to ANW4 testing)
# The port defaults to 8000
#
# eg.  sh testserver.sh -d ANW77
#
# Outputs to standard out
#
export PYTHONPATH=$PYTHONPATH:../Packages/


if [ -f main.py ]
  then
    FILE="main.py"
  else
    FILE="main.pyc"
fi

if [ ! -n "$1" ]
then
  echo "Attempting to start Armada Net Wars server with ANW4  "
  python $FILE -l 1 -d ANW4 -s 1
else
  echo "Assuming you passed in -d ANWX, starting server "
  python $FILE -l 1 $@
fi


