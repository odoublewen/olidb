from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.security import Security, SQLAlchemyUserDatastore, ConfirmRegisterForm
from wtforms import StringField
import flask_sijax

app = Flask(__name__)
app.config.from_object('oliapp.config')
db = SQLAlchemy(app)
from oliapp import views, models


class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('First Name')

user_datastore = SQLAlchemyUserDatastore(db, models.OliUser, models.Role)
security = Security(app, user_datastore, confirm_register_form=ExtendedRegisterForm)

mail = Mail(app)
flask_sijax.Sijax(app)