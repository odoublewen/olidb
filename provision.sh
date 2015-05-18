#!/usr/bin/env bash

apt-get update
apt-get install -y git postgresql-9.3 postgresql-server-dev-9.3 ipython python-pip python-dev libcurl4-openssl-dev primer3 redis-server bowtie2 unzip #python-tk
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

pip install -r /vagrant/requirements.txt

cd ~
wget -q http://downloads.sourceforge.net/project/bowtie-bio/bowtie/1.1.1/bowtie-1.1.1-linux-x86_64.zip
unzip bowtie-1.1.1-linux-x86_64.zip
rm bowtie-1.1.1-linux-x86_64.zip
mv bowtie-1.1.1 /opt
echo PATH=/opt/bowtie-1.1.1:$PATH >> /etc/profile

wget -q https://dl.dropboxusercontent.com/u/24849204/bowtie2_indexes.tar.gz
tar xf bowtie2_indexes.tar.gz
rm bowtie2_indexes.tar.gz
mv bowtie2_indexes /opt


# adding these commands to the bash history just for convenience
su - vagrant -c "echo './scripts/reinitialize_database.sh
./manage.py runserver --host 0.0.0.0 --reload --debug
PYTHONPATH=/vagrant ./scripts/import_oligos.py all
celery -A oliapp.celeryapp worker
' > /home/vagrant/.bash_history"

echo "You've been provisioned"
