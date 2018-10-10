#!/usr/bin/env bash

source env.sh
source $PYTHON_ENV_LOCATION/bin/activate

python $DJANGO_MANAGE_FILE graph_models AspiraUser -o ../figures/models_AspiraUser.png
python $DJANGO_MANAGE_FILE graph_models Twitter -o ../figures/models_Twitter.png
python $DJANGO_MANAGE_FILE graph_models Facebook -o ../figures/models_Facebook.png
python $DJANGO_MANAGE_FILE graph_models Youtube -o ../figures/models_Youtube.png
python $DJANGO_MANAGE_FILE graph_models Collection -o ../figures/models_Collections.png


