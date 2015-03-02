from oliapp import app
from oliapp.models import Oligoset, Target, Experiment, search_oligosets
from oliapp import db

from flask import request, send_from_directory, render_template, g, abort
# from flask import make_response, url_for, flash, redirect
# from flask.ext.sqlalchemy import Pagination
from flask.ext.security import login_required

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html", title='Hello world home')


@app.route('/oligoset/detail/<int:oligosetid>')
def oligoset_detail(oligosetid):
    g.des = Oligoset.query.get_or_404(oligosetid)
    return render_template("oligoset_detail.html", title='Oligoset detail')


@app.route('/oligoset', defaults={'page': 1})
@app.route('/oligoset/page/<int:page>')
def oligoset_browse(page):
    g.items = Oligoset.query.join(Target).paginate(page).items
    g.active_page = 'oligoset_browse'
    return render_template('oligoset_browse.html')


@app.route('/experiment/', defaults={'page': 1})
@app.route('/experiment/page/<int:page>')
def experiment_browse(page):
    g.items = Experiment.query.paginate(page).items
    g.active_page = 'experiment_browse'
    return render_template('experiment_browse.html')


@app.route('/search')
def site_search():
    if 'term' in request.args:
        g.term = request.args['term']
    else:
        g.term = 'actin'
    g.results = search_oligosets(db.session, g.term)
    g.active_page = 'search'
    return render_template('search_results.html')

@app.route('/design/create')
@login_required
def oligoset_create():
    g.active_page = 'design_create'
    return render_template('index.html')

