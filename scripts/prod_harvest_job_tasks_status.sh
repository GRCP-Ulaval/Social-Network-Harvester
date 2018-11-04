#!/usr/bin/env bash

source env.sh

sshpass -p ${PROD_PASSWORD} ssh ${PROD_USER}@${PROD_HOST} tail -f /aspira/Social-Network-Harvester/SocialNetworkHarvester/log/harvest_job_tasks_status.log
