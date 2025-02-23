#!/bin/bash

# export DB_CONNECTION_STRING=${DB_CONNECTION_STRING}Pwd=$(cat /run/secrets/sa_password);
pip3 install -r /app/requirements.txt
# pip3 install gunicorn
# gunicorn app:app -b 0.0.0.0:50505 --chdir=/app