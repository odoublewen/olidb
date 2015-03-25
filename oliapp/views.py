from oliapp import app
from oliapp.models import Oligoset, Target, Experiment, search_oligosets
from oliapp import db
from sqlalchemy import and_, or_
from flask import request, send_from_directory, render_template, g, abort, jsonify, session
# from flask import make_response, url_for, flash, redirect
from flask.ext.security import login_required, current_user
from flask.ext.login import user_logged_in
from sqlalchemy.orm.exc import NoResultFound
import flask_sijax

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


@app.route('/oligosets/detail/<taxatmid>')
def oligoset_detail(taxatmid):
    try:
        taxa, tmid = taxatmid.split('-')
        g.oligoset = Oligoset.query.join(Target).filter(Target.taxonomy == taxa).filter(Oligoset.tmid == int(tmid)).one()
    except NoResultFound:
        abort(404)
    except ValueError:
        abort(404)
    return render_template("oligoset_detail.html")


@user_logged_in.connect_via(app)
def on_user_logged_in(sender, user):
    session['benchtop_size'] = len(get_benchtop_expt(current_user.id).oligosets)


def get_benchtop_expt(userid):
    experiment = Experiment.query.filter(and_(Experiment.user_id == userid, Experiment.is_benchtop.is_(True))).first()
    if experiment is None:
        experiment = Experiment(name='My Benchtop', is_benchtop=True, user_id=userid)
        db.session.add(g.experiment)
        db.session.commit()
    return experiment


@flask_sijax.route(app, '/benchtop')
@login_required
def benchtop(page=1):
    g.active_page = 'benchtop'
    g.experiment = get_benchtop_expt(current_user.id)
    oligoset_list = [o.id for o in g.experiment.oligosets]

    query = Oligoset.query.join(Target)
    query = query.filter(Oligoset.id.in_(oligoset_list))

    g.pagination = query.order_by(Target.taxonomy, Oligoset.name).paginate(page, per_page=100)

    return render_template('benchtop.html')


@flask_sijax.route(app, '/oligosets', defaults={'page': 1})
@flask_sijax.route(app, '/oligosets/page/<int:page>')
def oligosets(page):

    def to_benchtop(obj_response, id):
        oset = Oligoset.query.get(id)
        exp = get_benchtop_expt(current_user.id)
        exp.oligosets.append(oset)
        db.session.add(exp)
        db.session.commit()
        session['benchtop_size'] += 1
    if g.sijax.is_sijax_request:
        g.sijax.register_callback('to_benchtop', to_benchtop)
        return g.sijax.process_request()

    g.experiment_num = request.args.get('exp')
    g.term = request.args.get('term')
    g.taxonomy = request.args.get('taxonomy')

    query = Oligoset.query.join(Target)

    if g.experiment_num:
        experiment = Experiment.query.get(g.experiment_num)
        g.experiment_name = experiment.name
        oligoset_list = [o.id for o in experiment.oligosets]
        query = query.filter(Oligoset.id.in_(oligoset_list))

    if g.term:
        for term in g.term.split(' '):
            term = '%%%s%%' % term
            query = query.filter(or_(Oligoset.name.ilike(term), Target.namelong.ilike(term)))

    if g.taxonomy:
        query = query.filter(Target.taxonomy == g.taxonomy)

    g.pagination = query.order_by(Target.taxonomy, Oligoset.name).paginate(page, per_page=100)
    g.active_page = 'oligosets'
    g.taxa = [q.taxa for q in db.session.query(Target.taxonomy.distinct().label("taxa")).order_by(Target.taxonomy).all()]
    return render_template('oligoset_browse.html')



@app.route('/experiments/', defaults={'page': 1})
@app.route('/experiments/page/<int:page>')
def experiments(page):

    g.term = request.args.get('term')
    g.mine = request.args.get('mine')

    query = Experiment.query #.filter(Experiment.is_public is True)

    if g.term:
        for term in g.term.split(' '):
            term = '%%%s%%' % term
            query = query.filter(Experiment.name.ilike(term) | Experiment.description.ilike(term))

    if g.mine == 'T':
        query = query.filter(Experiment.user_id == current_user.id)

    g.pagination = query.paginate(page)
    g.active_page = 'experiments'
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

