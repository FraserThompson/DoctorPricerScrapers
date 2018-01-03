#!/bin/bash

sleep 10

/usr/local/bin/migrate
/usr/local/bin/createsuperuser
python manage.py collectstatic --no-input
gunicorn --bind=unix:/socks/gunicorn.sock -w 2 --reload wsgi