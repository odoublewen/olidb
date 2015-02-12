from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('oli.config')
db = SQLAlchemy(app)

from oli import views, models

