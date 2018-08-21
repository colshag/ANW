#!/bin/sh
# get the location of this file
DIR="$( cd "$( dirname "$0" )" && pwd )"
echo $DIR/../../anwgae 
cd $DIR/../../anwgae 
nohup ./startDevl.sh &
