from oliapp import app
from oliapp.models import Oligoset, Target, Experiment, User, search_oligosets
from oliapp import db
from sqlalchemy import and_, or_, desc
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

@app.template_filter('seqmask')
def _mask_sequence(seq, is_public):
    if current_user.is_authenticated() or is_public:
        return seq
    else:
        return 'N' * len(seq)

@app.route('/')
@app.route('/index/')
def index():
    g.recentexp = Experiment.query.filter(Experiment.date != None).order_by(desc(Experiment.date)).limit(10)
    g.recentoli = Oligoset.query.join(Target).filter(Oligoset.date != None).order_by(desc(Oligoset.date)).limit(10)
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


# @user_logged_in.connect_via(app)
# def on_user_logged_in(sender, user):
#     session['benchtop_size'] = len(current_user.oligosets)


@flask_sijax.route(app, '/benchtop')
@login_required
def benchtop():

    g.active_page = 'benchtop'
    oligoset_list = [o.id for o in current_user.oligosets]

    query = Oligoset.query.join(Target)
    query = query.filter(Oligoset.id.in_(oligoset_list))

    g.rows = query.order_by(Target.taxonomy, Oligoset.name).all()

    return render_template('benchtop.html')


@flask_sijax.route(app, '/oligosets', defaults={'page': 1})
@flask_sijax.route(app, '/oligosets/page/<int:page>')
def oligosets(page):

    def to_benchtop(obj_response, id):
        oset = Oligoset.query.get(id)
        if oset not in current_user.oligosets:
            current_user.oligosets.append(oset)
            db.session.add(current_user)
            db.session.commit()
            obj_response.html("#benchtop_size", len(current_user.oligosets))

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

    g.pagination = query.order_by(Target.taxonomy, Oligoset.name).paginate(page, per_page=500)
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



