#!/bin/bash
echo "python -m venv env"
rm env -r
python -m venv env
echo "source (sourceme)"
rm sourceme
ln -s env/bin/activate sourceme
echo "source sourceme"
# source sourceme
echo "env/bin/pip install -r requirements.txt"
env/bin/pip install -r requirements.txt # pip freeze > requirements.txt
