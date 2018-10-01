#!/usr/bin/env bash

source env.sh

echo "Now forwarding local connections on port 3333 to remote production server database port"
sshpass -p ${PROD_PASSWORD} ssh -L 3333:127.0.0.1:${PROD_DB_PORT} ${PROD_USER}@${PROD_HOST} -N

