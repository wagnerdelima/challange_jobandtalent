#!/usr/bin/env bash
sleep 5
python3 manage.py migrate
python3 manage.py collectstatic --noinput
gunicorn wsgi -b 0.0.0.0:80 -w 2
