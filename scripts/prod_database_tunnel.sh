#!/usr/bin/env bash

source env.sh

sshpass -p ${PROD_PASSWORD} ssh -L 3333:127.0.0.1:${PROD_DB_PORT} ${PROD_USER}@${PROD_HOST} -N

