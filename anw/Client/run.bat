cd ..
set PYTHONPATH=%CD%\Packages
cd Client
IF EXIST run.py GOTO SOURCE
python run.pyc %1
exit
:SOURCE
python run.py %1
exit
