#!/bin/bash
#
# Deploys the docker service. Designed to be run locally and pointed at the remote with the DP_SERVER variable.
# Requires these environment variables: ADMIN_PASSWORD, DATABASE_PASSWORD, RABBITMQ_DEFAULT_PASS, SECRET_KEY
# 
# THESE LINES ARE THE SAME FOR ALL SCRIPTS
########################################################################################################################
source .env

# Ensure the directory is there
ssh -v fraser@${DP_SERVER} "mkdir -p ~/docker-services/doctorpricer"

# Copy the docker-compose files and remote scripts
scp ./{docker-compose,docker-compose.extra}.yml ./_ops/remote_scripts/*.sh fraser@${DP_SERVER}:~/docker-services/doctorpricer
#########################################################################################################################

# Run the script which fetches the images and brings up the containers
ssh fraser@${DP_SERVER} "ENV=live DOCKER_USERNAME=${DOCKER_USERNAME} DOCKER_PASSWORD=${DOCKER_PASSWORD} ADMIN_PASSWORD=${ADMIN_PASSWORD} DATABASE_PASSWORD=${DATABASE_PASSWORD} RABBITMQ_DEFAULT_PASS=${RABBITMQ_DEFAULT_PASS} SECRET_KEY=${SECRET_KEY} ~/docker-services/doctorpricer/deploy.sh"