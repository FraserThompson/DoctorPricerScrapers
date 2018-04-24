#!/bin/bash

echo "Restoring a backup..."

cd ~/docker-services/doctorpricer
docker-compose -f docker-compose.extra.yml run restore