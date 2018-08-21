# On the mac, the .bash_profile sets the python path
if [ -f ~/.bash_profile ]; then
    . ~/.bash_profile
fi
export PYTHONPATH=$PYTHONPATH:../Packages/

python run.py -r 'http://localhost:8000' -g 'ANW4' -e '1' -s False -o '1024x768' -f False

