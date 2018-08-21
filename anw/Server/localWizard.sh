export PYTHONPATH=$PYTHONPATH:../Packages/
if [ -f wizard.py ]
  then
    FILE="wizard.py"
  else
    FILE="wizard.pyc"
fi

python wizard.py -l 1
