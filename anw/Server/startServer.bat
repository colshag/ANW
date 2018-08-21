cd ..
set PYTHONPATH=%CD%\Packages
cd Server
if EXIST main.py GOTO SOURCE
python main.pyc %1 %2 %3 %4 %5 %6 %7
exit
:SOURCE
python main.py %1 %2 %3 %4 %5 %6 %7
exit
