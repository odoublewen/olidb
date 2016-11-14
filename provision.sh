#!/usr/bin/env bash

apt-get update
apt-get install -y git postgresql postgresql-server-dev-all libcurl4-openssl-dev python3-pip rabbitmq-server unzip libncurses5-dev bowtie
apt-get install -y emacs24-nox byobu htop primer3
apt-get autoremove
#apt-get install -y build-essential

echo '# "local" is for Unix domain socket connections only
local   all             all                                  trust
# IPv4 local connections:
host    all             all             0.0.0.0/0            trust
# IPv6 local connections:
host    all             all             ::/0                 trust' > /etc/postgresql/9.3/main/pg_hba.conf

sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/9.3/main/postgresql.conf

/etc/init.d/postgresql restart
su - postgres -c 'createuser -s vagrant'
su - vagrant -c 'createdb olidb'

pip3 install --upgrade pip
pip3 install Cython
pip3 install -r /vagrant/requirements.txt

# adding these commands to the bash history just for convenience
su - vagrant -c "echo './scripts/reinitialize_database.sh
./manage.py runserver --host 0.0.0.0 --reload --debug
PYTHONPATH=/vagrant
./scripts/import_oligos.py all
celery -A oliapp.celeryapp worker
' > /home/vagrant/.bash_history"

echo "You've been provisioned"
