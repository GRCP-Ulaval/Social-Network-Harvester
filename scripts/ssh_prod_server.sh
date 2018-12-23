#!/usr/bin/env bash

source env.sh

sshpass -p ${PROD_PASSWORD} ssh ${PROD_USER}@${PROD_HOST}
