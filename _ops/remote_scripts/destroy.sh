#!/bin/bash
#
# Stops the docker service! Designed to be run on remote.
#
#

echo "DESTROYING CONTAINERS. Environment is ${ENV}."

cd ~/docker-services/doctorpricer
docker-compose down -v --remove-orphans