#!/usr/bin/env bash

apt-get update
apt-get install -y git postgresql-9.3 postgresql-server-dev-9.3 libcurl4-openssl-dev primer3 rabbitmq-server bowtie2 unzip ncurses-dev
apt-get install -y emacs24-nox byobu htop
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

cd ~
wget -q https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tar.xz
tar xf Python-3.5.1.tar.xz
cd Python-3.5.1
./configure --prefix=/usr/local
make && make altinstall
cd /usr/local/bin
ln -s python3.5 pip3.5 .
pip3 install --upgrade pip
pip3 install -r /vagrant/requirements_freeze.txt

cd ~
wget -q http://downloads.sourceforge.net/project/bowtie-bio/bowtie/1.1.2/bowtie-1.1.2-linux-x86_64.zip
unzip bowtie-1.1.2-linux-x86_64.zip
rm bowtie-1.1.2-linux-x86_64.zip
mv bowtie-1.1.2 /opt

echo PATH=/opt/bowtie-1.1.2:$PATH >> /etc/profile

wget -q https://dl.dropboxusercontent.com/u/24849204/bowtie2_indexes.tar.gz
tar xf bowtie2_indexes.tar.gz
rm bowtie2_indexes.tar.gz
mv bowtie2_indexes /opt


# adding these commands to the bash history just for convenience
su - vagrant -c "echo './scripts/reinitialize_database.sh
./manage.py runserver --host 0.0.0.0 --reload --debug
PYTHONPATH=/vagrant
./scripts/import_oligos.py all
celery -A oliapp.celeryapp worker
' > /home/vagrant/.bash_history"

echo "You've been provisioned"
