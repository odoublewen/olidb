#!/usr/bin/env bash

apt-get update
apt-get install -y git postgresql-9.3 postgresql-server-dev-9.3 ipython python-pip python-dev libcurl4-openssl-dev #build-essential

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

pip install -r /vagrant/requirements.txt

# adding three commands to the bash history just for convenience
su - vagrant -c "echo './scripts/reinitialize_database.sh
./manage.py runserver --host 0.0.0.0 --reload --debug
PYTHONPATH=/vagrant ./scripts/import_oligos.py all
' > /home/vagrant/.bash_history"

echo "You've been provisioned"