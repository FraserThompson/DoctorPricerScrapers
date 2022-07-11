#!/bin/bash

echo "Restoring a backup..."

cd ~/docker-services/doctorpricer
docker-compose exec -it django python manage.py dbrestore