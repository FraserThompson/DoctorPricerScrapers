#!/bin/bash

sleep 10

/usr/local/bin/migrate

python manage.py collectstatic --noinput
gunicorn --bind=unix:/socks/gunicorn.sock -w 2 --reload wsgi