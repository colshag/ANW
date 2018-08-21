#!/bin/bash
# kill_anw.sh
# If a command-line perameter is used, kills that ANW game
# Otherwise, promts the user for which game to kill
# updates the .info file (if it exists) to remove the $pid and $key
# (leaving only the port)

currentdir="$( cd "$( dirname "$0" )" && pwd )"

if [ $# -eq 0 ]; then
   INPUT="foo"
   while [[ -n "$INPUT" && -n $(pidof python) ]]; do
      clear
      sh $currentdir/running_anw.sh
      echo ""
      echo "Enter the GameID (eg ANW29) of ANW you want stopped"
      read -p "or {ENTER} to exit: " INPUT
      echo ""
      if [ -n "$INPUT" ]; then
         #try to load the PID of the gameID from the config file
         if [ -f $HOME/.anw/$INPUT.info ]; then
            . $HOME/.anw/$INPUT.info
         else
            #try to get the pid from running processes
            pid=`ps ax | grep $INPUT | grep -v grep | awk '{print $1}'`
         fi

         #Check for valid pid
         if [ -n "$pid" ]; then
            echo "Stopping ANW server $INPUT..."
            kill -SIGINT $pid
            if [ $? -eq 0 ]; then
               #remove the PID from the .info file
               echo "port=$port" > $HOME/.anw/$INPUT.info
            fi
         else
            echo "Error! $INPUT not found as a valid ANW game."
         fi
         sleep 5
      fi
   done
else
   if [ -f $HOME/.anw/$1.info ]; then
      . $HOME/.anw/$1.info
   else
      #try to get the pid from running processes
      pid=`ps ax | grep $INPUT | grep -v grep | awk '{print $1}'`
   fi
   echo "Killing $1..."
   kill -SIGINT $pid
   if [ $? -eq 0 ]; then
      #remove the PID and KEY from the .info file
      echo "port=$port" > $HOME/.anw/$INPUT.info
   fi

   sleep 1
fi
