#!/bin/bash

echo "Backing up database..."

cd ~/docker-services/doctorpricer
docker-compose exec django python manage.py dbbackup