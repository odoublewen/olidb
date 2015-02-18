from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('oliapp.config')

db = SQLAlchemy(app)

from oliapp import views, models

