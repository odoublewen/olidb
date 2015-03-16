from oliapp import app
from oliapp.models import Oligoset, Target, Experiment, search_oligosets
from oliapp import db

from flask import request, send_from_directory, render_template, g, abort
# from flask import make_response, url_for, flash, redirect
from flask.ext.security import login_required

@app.template_filter('isodate')
def _jinja2_filter_datetime(date, fmt=None):
    try:
        return date.strftime('%Y-%m-%d')
    except AttributeError:
        return ''

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

    g.term = request.args.get('term')
    g.taxonomy = request.args.get('taxonomy')

    query = Oligoset.query.join(Target)

    if g.taxonomy:
        query = query.filter(Target.taxonomy == g.taxonomy)

    if g.term:
        for term in g.term.split(' '):
            term = '%%%s%%' % term
            query = query.filter(Oligoset.name.ilike(term) | Target.namelong.ilike(term))

    g.pagination = query.paginate(page)
    g.active_page = 'oligoset_browse'
    g.taxa = [q.taxa for q in db.session.query(Target.taxonomy.distinct().label("taxa")).order_by(Target.taxonomy).all()]
    return render_template('oligoset_browse.html')


@app.route('/experiment/', defaults={'page': 1})
@app.route('/experiment/page/<int:page>')
def experiment_browse(page):
    g.pagination = Experiment.query.paginate(page)
    g.active_page = 'experiment_browse'
    return render_template('experiment_browse.html')


@app.route('/search')
def site_search():
    g.siteterm = request.args.get('siteterm')
    g.results = search_oligosets(db.session, g.siteterm)

    g.active_page = 'search'
    return render_template('site_search.html')

@app.route('/design/create')
@login_required
def oligoset_create():
    g.active_page = 'design_create'
    return render_template('index.html')

