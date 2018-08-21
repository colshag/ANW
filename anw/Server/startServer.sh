#
#
# Arguments allowed
#
# -o <port>     (defaults to 8000)
# -d <database> (defaults to all galaxies in Database directory)
#
# eg.  sh start.sh logfile.out -o 8001 -d ANW77
# starts ANW77 on port 8001. 
#
if [ ! -n "$1" ]
then
  echo "Usage: `basename $0` <logfile> -o <port> -d <database>"
  echo "eg.  sh start.sh logfile.out -o 8001 -d ANW77"
  exit 1
fi  

export PYTHONPATH=$PYTHONPATH:../Packages/


if [ -f main.py ]
  then
    FILE="main.py"
  else
    FILE="main.pyc"
fi

LOGFILE=$1
shift
echo "Attempting to start Armada Net Wars server...  See $LOGFILE for launch details"
nohup python $FILE $@ >> $LOGFILE &
