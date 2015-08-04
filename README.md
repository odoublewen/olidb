# OliDB, an oligonucleotide database

Introduction
============

OliDB is a Flask-based oligonucleotide database for labs to create and organize complex RT-PCR primers.

Setup
=====

Vagrant provisioning is complete, so assuming you have vagrant installed on your system, setting up a dev instance of OliDB should be as simple as:

1. git clone git@github.com:odoublewen/olidb.git
2. cd olidb
3. vagrant up
4. vagrant ssh
5. cd /vagrant
6. ./scripts/reinitialize_database.sh
7. PYTHONPATH=/vagrant ./scripts/import_oligos.py all
8. ./manage.py runserver --host 0.0.0.0 --reload --debug
9. celery -A oliapp.celeryapp worker

Steps 6 and 7 only necessary the first time.

For convenience, the last few commands are copied in the bash history by the vagrant provisioning script, so should be able to just arrow-up to find them.

If all is working, after you issue the last command, you should be able to connect to the web app at this URL, on your workstation (ie, the host machine):  http://127.0.0.1:5050/

**Documentation and screenshots coming soon!**
