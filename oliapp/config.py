import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = '9CA7C618-005E-4553-9DCF-C38D14CACB71'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://localhost/olidb'

SECURITY_PASSWORD_HASH = 'sha512_crypt'
SECURITY_PASSWORD_SALT = '57f544b8-be11-11e4-ae1d-3c15c2d09704'
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = True

MAIL_SERVER = 'smtp.mailgun.org'
# MAIL_PORT : default 25
# MAIL_USE_TLS : default False
# MAIL_USE_SSL : default False
# MAIL_DEBUG : default app.debug
MAIL_USERNAME = 'postmaster@sandboxb9243efefa074a75bd30d57d78a6c13b.mailgun.org'
MAIL_PASSWORD = '9510fe09e22c6cf4490fc1efdf2d5a16'