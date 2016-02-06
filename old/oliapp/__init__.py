from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore, ConfirmRegisterForm, RegisterForm
from wtforms import StringField
import flask_sijax
from redis import StrictRedis
from celery import Celery

redis = StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.config.from_object('oliapp.config')
db = SQLAlchemy(app)


def make_celery(app):
    celeryapp = Celery(app.import_name)
    celeryapp.conf.update(app.config)
    task_base = celeryapp.Task
    class ContextTask(task_base):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celeryapp.Task = ContextTask
    return celeryapp

celeryapp = make_celery(app)

from oliapp import views, models


user_datastore = SQLAlchemyUserDatastore(db, models.OliUser, models.Role)

# class ExtendedRegisterForm(ConfirmRegisterForm):
#     name = StringField('First Name')
# security = Security(app, user_datastore, confirm_register_form=ExtendedRegisterForm)

class ExtendedRegisterForm(RegisterForm):
    name = StringField('First Name')
security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


mail = Mail(app)
flask_sijax.Sijax(app)

