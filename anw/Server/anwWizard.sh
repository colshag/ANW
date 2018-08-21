export PYTHONPATH=$PYTHONPATH:../Packages/
if [ -f wizard.py ]
  then
    FILE="wizard.py"
  else
    FILE="wizard.pyc"
fi

python $FILE -l 0
