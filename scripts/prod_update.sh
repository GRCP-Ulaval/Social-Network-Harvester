#!/usr/bin/env bash

source env.sh

sshpass -p ${PROD_PASSWORD} ssh -tt ${PROD_USER}@${PROD_HOST} \
    'cd '${PROD_SCRIPT_LOCATION}'&& sudo ./update_site.sh'
