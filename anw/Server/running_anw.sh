#!/bin/bash
# Check for running instances and exits with the count

z=0

for i in `ps ax | grep main.py | grep -v grep | awk '{print $1}'`
do
   z=$((z+1))
done

echo "Found $z running instances of ANW."

if [ $z -gt 0 ]; then
   ps axo pid,args | grep main.py | grep -v grep
fi

exit $z
