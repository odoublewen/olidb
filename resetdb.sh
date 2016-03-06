#!/usr/bin/env bash
dropdb olidb
createdb olidb
rm -rf /vagrant/oliapp/migrations
/vagrant/manage.py makemigrations oliapp
/vagrant/manage.py migrate
/vagrant/manage.py loaddata /vagrant/oliapp/fixtures/fixtures.json