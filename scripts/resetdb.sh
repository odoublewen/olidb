#!/usr/bin/env bash

docker exec olidb_postgres_1 /docker-entrypoint-initdb.d/initialize_olidb.sh

docker exec olidb_web_1 /bin/sh -c "rm -rf oliapp/migrations
./manage.py makemigrations oliapp
./manage.py migrate
./manage.py loaddata oliapp/fixtures/fixtures.json"
