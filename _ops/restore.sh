#!/bin/bash
#
# Makes the remote host do a backup.
# 
# THESE LINES ARE THE SAME FOR ALL SCRIPTS
########################################################################################################################
source .env

# Ensure the directory is there
ssh fraser@${DP_SERVER} "mkdir -p ~/docker-services/doctorpricer"

# Copy the docker-compose files and remote scripts
scp ../{docker-compose,docker-compose.extra}.yml ./remote_scripts/*.sh fraser@${DP_SERVER}:~/docker-services/doctorpricer
#########################################################################################################################

ssh fraser@${DP_SERVER} 'mkdir -p ~/restore'

scp ./restore/backup.tar.gz fraser@${DP_SERVER}:~/restore

# Run the script which fetches the images and brings up the containers
ssh fraser@${DP_SERVER} "ENV=live DOCKER_USERNAME=${DOCKER_USERNAME} DOCKER_PASSWORD=${DOCKER_PASSWORD} ADMIN_PASSWORD=${ADMIN_PASSWORD} DATABASE_PASSWORD=${DATABASE_PASSWORD} RABBITMQ_DEFAULT_PASS=${RABBITMQ_DEFAULT_PASS} SECRET_KEY=${SECRET_KEY} ~/docker-services/doctorpricer/restore.sh"