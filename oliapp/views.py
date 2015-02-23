from oliapp import app, db
from oliapp.models import *
from flask import request, send_from_directory, render_template, g, abort
from flask import make_response, url_for, flash, redirect
from flask.ext.sqlalchemy import Pagination

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title='Hello world home')


@app.route('/design/detail/<int:designid>')
def design(designid):
    des = Design.by_id(designid)
    if not des:
        abort(404)
    g.des = des
    return render_template("design_details.html", title='Design detail')

@app.route('/design/search/<term>')
def design_search(term):
    g.term = term
    g.results = Design.search(term)
    return render_template('design_searchresults.html')

