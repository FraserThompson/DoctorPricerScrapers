#!/bin/bash
#
# Stops the docker service! Designed to be run on remote.
#
#

echo "STOPPING CONTAINERS. Environment is ${ENV}."

cd ~/docker-services/doctorpricer
docker-compose down