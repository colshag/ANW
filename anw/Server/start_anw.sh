#!/bin/bash
# Checks for running ANW instances.
# if no instances are running, uses ANW##.info file to start games
# If .info file is not found, asks the user which port to use.
#
# input <game id>
# if a <game id> is specified as a command-line parameter, starts
#       only that instance
#       e.g.  start.sh ANW34

############################################
# User Variables
# get the location of this file
DIR="$( cd "$( dirname "$0" )" && pwd )"
LOGPATH=$HOME  #where the log file should go
ANWROOT="$DIR/../../../../"
ANWPATH="$DIR/.."
############################################
echo LOGPATH=$LOGPATH
echo ANWROOT=$ANWROOT
echo ANWPATH=$ANWPATH

cd $ANWPATH/Server
export PYTHONPATH=$PYTHONPATH:../Packages/
if [ -f $ANWPATH/Server/main.py ]; then
   FILE="main.py"
else
   FILE="main.pyc"
fi
cd $ANWPATH/Server

if [ $# -gt 0 ]; then
   if [ -f $HOME/.anw/$1.info ]; then
      . $HOME/.anw/$1.info
   else
      echo "ANW.info file not found for $1"
      read -p "Enter the port to use (e.g. 8000) to {enter} to abort: " INPUT
      if [ ! -z $INPUT ]; then
         port=$INPUT
      else
         exit
      fi
      #backup the log file before starting
      #(may error if log file doesn't exist, so redirect output to NULL)
      cp -f $LOGPATH/$1.log $LOGPATH/$1.log.bak &> /dev/null

      #start the server
      nohup python $FILE -o $port -d $1 >> $LOGPATH/$1.log&
   fi
else
   #Loop through the games defined in the Database folder
   for GAME in `ls $ANWPATH/Database | grep ANW`
   do
      pid=0
      if [ ! -f $ANWROOT/$GAME.info ]; then
         echo "ANW.info file not found for $GAME"
         read -p "Enter the port to use (e.g. 8000) to {enter} to abort: " INPUT
         if [ ! -z $INPUT ]; then
            port=$INPUT
         else
            continue
         fi
      else
         #check if the game is running
         . $ANWROOT/$GAME.info
         if [ $pid -ne 0 ]; then
            echo "WARNING! $GAME is already running (PID defined in $GAME.info)"
            read -p "Force start? (y/N)" -n 1 INPUT
            echo ""
            if [[ $INPUT != "y" && $INPUT != "Y" ]]; then
            #skip this $GAME
               continue
            fi
         fi
      fi
      echo "Starting $GAME on port $port..."
      #backup the log file before starting
      #(may error if log file doesn't exist, so redirect output to NULL)
      cp -f $LOGPATH/$GAME.log $LOGPATH/$GAME.log.bak &> /dev/null

      #start the server
      nohup python $FILE -o $port -d $GAME >> $LOGPATH/$GAME.log&
   done
fi