dropdb olidb
createdb olidb
rm -rf /vagrant/oliapp/migrations
/vagrant/manage.py makemigrations oliapp
/vagrant/manage.py migrate
#/vagrant/manage.py loaddata provision/fixture_data.json
