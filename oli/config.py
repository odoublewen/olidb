import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = '9CA7C618-005E-4553-9DCF-C38D14CACB71'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://localhost/olidb'
