import oli
from flask import render_template

@oli.app.route('/')
@oli.app.route('/index')
def index():
    return render_template("index.html", title='Hello world home')
