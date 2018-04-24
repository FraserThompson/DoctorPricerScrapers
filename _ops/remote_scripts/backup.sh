#!/bin/bash

echo "Backing up database..."

cd ~/docker-services/doctorpricer
docker-compose -f docker-compose.extra.yml run backup