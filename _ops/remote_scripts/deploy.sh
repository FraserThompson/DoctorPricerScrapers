#!/bin/bash
#
# Brings up the docker service! Designed to be run on remote.
#
#

echo "BRINGING UP CONTAINERS. Environment is ${ENV}."

cd ~/docker-services/doctorpricer
docker login --username=${DOCKER_USERNAME} --password=${DOCKER_PASSWORD}
docker-compose pull
docker-compose up --build -d