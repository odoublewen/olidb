#!/bin/sh
dropdb olidb
createdb olidb
rm /vagrant/migrations/versions/*
./manage.py db migrate -m 'initial commit'
./manage.py db upgrade
