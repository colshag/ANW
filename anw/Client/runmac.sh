# On the mac, the .bash_profile sets the python path
if [ -f ~/.bash_profile ]; then
    . ~/.bash_profile
fi

export PYTHONPATH=$PYTHONPATH:../Packages/:/Developer/Panda3D/lib/

python run.py $1 || python run.pyc $1
