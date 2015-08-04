# olidb
OliDB is a Flask-based oligonucleotide database for labs to create and organize complex RT-PCR primers.

Vagrant provisioning is complete, so assuming you have vagrant installed on your system, setting up a dev instance of OliDB should be as simple as:

1. git clone git@github.com:odoublewen/olidb.git
2. cd olidb
3. vagrant up
4. vagrant ssh
5. cd /vagrant
6. ./scripts/reinitialize_database.sh  (first time only)
7. ./manage.py runserver --host 0.0.0.0 --reload --debug

For convenience, the last two commands are copied in the bash history by the vagrant provisioning script, so should be able to just arrow-up to find them.

If all is working, after you issue the last command, you should be able to connect to the web app at this URL, on your workstation (ie, the host machine):  http://127.0.0.1:5050/

Documentation and screenshots coming soon!
