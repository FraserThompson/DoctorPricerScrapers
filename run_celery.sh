#!/bin/sh

sleep 10
celery -A dp_server worker --loglevel=info