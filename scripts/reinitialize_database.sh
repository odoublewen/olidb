#!/bin/sh
dropdb olidb
createdb olidb
rm /vagrant/migrations/versions/*
/vagrant/manage.py db migrate -m 'initial commit'
/vagrant/manage.py db upgrade
