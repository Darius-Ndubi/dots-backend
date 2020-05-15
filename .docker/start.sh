#!/bin/bash

source /root/.local/share/virtualenvs/dots-api-*/bin/activate
echo "<<<<<<<<<< Export LANG to the Env>>>>>>>>>>"

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

echo "+++++++++++++++++ Export environment variables ++++++++++++++++++++++++"
source .env.dev
echo "+++++++++++++++++ Export Done ++++++++++++++++++++++++"

echo "+++++++++++++++++ Make migrations ++++++++++++++++++++++++"
python3 manage.py migrate
echo "------------------- Make migrations Done !!! ------------------------"

echo "+++++++++++++++++ Make staff users ++++++++++++++++++++++++"
python3 manage.py make_staff_users
echo "------------------- Make staff users Done !!! ------------------------"

echo "+++++++++++++++++ Start up the server ++++++++++++++++++++++++"
gunicorn --workers 2  dots.wsgi -b 0.0.0.0:8000 --access-logfile '-'
echo "------------------- Development server up and running ------------------------"
