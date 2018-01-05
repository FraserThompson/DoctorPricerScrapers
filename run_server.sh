#!/bin/bash

sleep 10

/usr/local/bin/migrate
/usr/local/bin/createsuperuser
python manage.py collectstatic --no-input
gunicorn --timeout 300 --bind=unix:/run/django/gunicorn.sock -w 1 --reload wsgi