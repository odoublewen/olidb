import oliapp
from flask import render_template

@oliapp.app.route('/')
@oliapp.app.route('/index')
def index():
    return render_template("index.html", title='Hello world home')
