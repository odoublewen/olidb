from oliapp import app
from oliapp import models
from oliapp import db

from flask import request, send_from_directory, render_template, g, abort
# from flask import make_response, url_for, flash, redirect
# from flask.ext.sqlalchemy import Pagination

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title='Hello world home')


@app.route('/design/detail/<int:designid>')
def design_detail(designid):
    des = models.Design.by_id(designid)
    if not des:
        abort(404)
    g.des = des
    return render_template("design_details.html", title='Design detail')


@app.route('/design/list')
def design_list():
    if 'search' in request.args:
        g.term = request.args['search']
        g.results = models.search_designs(db.session, g.term)
        return render_template('design_searchresults.html')
    else:
        abort(404)


