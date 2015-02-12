#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y build-essential git postgresql-9.3 postgresql-server-dev-9.3 ipython

echo '# "local" is for Unix domain socket connections only
local   all             all                                  trust
# IPv4 local connections:
host    all             all             0.0.0.0/0            trust
# IPv6 local connections:
host    all             all             ::/0                 trust' | sudo tee /etc/postgresql/9.3/main/pg_hba.conf

sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/9.3/main/postgresql.conf
sudo /etc/init.d/postgresql restart
sudo su - postgres -c 'createuser -s vagrant'
createdb olidb

sudo pip install -r /vagrant/requirements.txt

echo "You've been provisioned"