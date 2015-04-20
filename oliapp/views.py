from oliapp import app
from oliapp.models import Oligoset, Target, Experiment, OliUser, Job, search_oligosets
from oliapp.forms import ExperimentForm, SequenceForm
from sqlalchemy import and_, or_, desc
from flask import request, send_from_directory, render_template, g, abort, jsonify, session, flash, make_response, url_for, redirect
from flask.ext.security import login_required, current_user
import flask_sijax
from sqlalchemy.orm.exc import NoResultFound
from lib.run_primer3 import make_5primer_set
from Bio import SeqIO
import cStringIO
from collections import namedtuple
import pandas as pd
from oliapp import db, tasks, redis
import datetime
from oliapp.config import CELERY_TASK_RESULT_EXPIRES

def iternamedtuples(df):
    Row = namedtuple('Row', df.columns)
    for row in df.itertuples():
        yield Row(*row[1:])


class SijaxHandler(object):

    @staticmethod
    def oligoset_benchtop(obj_response, id, action='toggle'):
        oset = Oligoset.query.get(id)
        if oset in current_user.benchtop_oligosets:
            if action in ['toggle', 'remove']:
                current_user.benchtop_oligosets.remove(oset)
                db.session.add(current_user)
                db.session.commit()
                obj_response.html(".benchtop_size", len(current_user.benchtop_oligosets))
                obj_response.script("$('#oligoset" + str(id) + "').removeClass().addClass('glyphicon glyphicon-unchecked');")
        else:
            if action in ['toggle', 'add']:
                current_user.benchtop_oligosets.append(oset)
                db.session.add(current_user)
                db.session.commit()
                obj_response.html(".benchtop_size", len(current_user.benchtop_oligosets))
                obj_response.script("$('#oligoset" + str(id) + "').removeClass().addClass('glyphicon glyphicon-check');")

    @staticmethod
    def query_benchtop(obj_response, ids, action='toggle'):
        for id in ids:
            SijaxHandler.oligoset_benchtop(obj_response, id, action=action)


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


@flask_sijax.route(app, '/benchtop')
@login_required
def benchtop():

    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
        return g.sijax.process_request()

    form = ExperimentForm(request.form)
    form.saveas.choices = [('NewExperiment', 'New Experiment')] + [(str(e.id), e.name) for e in current_user.experiments]

    if form.validate_on_submit():
        if form.saveas.data == "NewExperiment":
            exp = Experiment(name=form.name.data, description=form.description.data, is_public=form.is_public.data,
                             oliuser_id=current_user.id, oligosets=current_user.benchtop_oligosets)
        else:
            exp = Experiment.query.get(int(form.saveas.data))
            exp.oligosets = current_user.benchtop_oligosets
            if form.name.data != '':
                exp.name = form.name.data
            if form.description.data != '':
                exp.description = form.description.data

        db.session.add(exp)
        current_user.benchtop_oligosets = []
        db.session.add(current_user)
        db.session.commit()
        flash('Your benchtop was saved as %s' % exp.name)

    for job in current_user.jobs:
        if datetime.datetime.now() - job.created > datetime.timedelta(seconds=CELERY_TASK_RESULT_EXPIRES):
            current_user.jobs.remove(job)
    db.session.add(current_user)
    db.session.commit()

    oligoset_list = [o.id for o in current_user.benchtop_oligosets]

    query = Oligoset.query.join(Target)
    query = query.filter(Oligoset.id.in_(oligoset_list))

    g.onbench = query.order_by(Target.taxonomy, Oligoset.name).all()
    g.myexperiments = current_user.experiments

    g.active_page = 'benchtop'
    return render_template('benchtop.html', form=form)


@flask_sijax.route(app, '/oligosets', defaults={'page': 1})
@flask_sijax.route(app, '/oligosets/page/<int:page>')
def oligoset_browse(page):

    if g.sijax.is_sijax_request:
        g.sijax.register_object(SijaxHandler)
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
    g.itemids = [i.id for i in g.pagination.items]
    g.active_page = 'oligoset_browse'
    g.taxa = [q.taxa for q in db.session.query(Target.taxonomy.distinct().label("taxa")).order_by(Target.taxonomy).all()]
    return render_template('oligoset_browse.html')



@app.route('/experiments/', defaults={'page': 1})
@app.route('/experiments/page/<int:page>')
def experiment_browse(page):

    g.term = request.args.get('term')
    g.mine = request.args.get('mine')

    query = Experiment.query.outerjoin(OliUser) #.filter(Experiment.is_public is True)

    if g.term:
        for term in g.term.split(' '):
            term = '%%%s%%' % term
            query = query.filter(Experiment.name.ilike(term) | Experiment.description.ilike(term))

    if g.mine == 'T':
        query = query.filter(Experiment.oliuser_id == current_user.id)

    g.pagination = query.paginate(page)
    g.active_page = 'experiment_browse'
    return render_template('experiment_browse.html')


@app.route('/search')
def site_search():
    g.siteterm = request.args.get('siteterm')
    g.results = search_oligosets(db.session, g.siteterm)

    g.active_page = 'search'
    return render_template('site_search.html')


@app.route('/design', methods=['GET', 'POST'])
@login_required
def oligoset_design():

    form = SequenceForm(request.form)

    if request.method == 'POST':
        if form.validate():

            jobname = form.jobname.data
            if jobname == "" or jobname is None:
                jobname = current_user.name + ' ' + str(len(current_user.jobs) + 1)

            seqhandle = cStringIO.StringIO(form.fasta_sequences.data)
            seqdict = dict([(rec.id, str(rec.seq)) for rec in SeqIO.parse(seqhandle, format='fasta')])

            s1 = form.primer3_config_taqman.data.splitlines()
            s2 = form.primer3_config_preamp.data.splitlines()

            job = tasks.enqueue_5primer_set.delay(seqdict, s1, s2)

            # import ipdb; ipdb.set_trace()

            jobrec = Job(jobid=job.id, jobname=jobname, numbertotal=len(seqdict))
            current_user.jobs.append(jobrec)
            db.session.add(current_user)
            db.session.commit()

            flash('Your job was submitted %s' % job.id)

            return redirect(url_for('benchtop'))

    g.active_page = 'oligoset_design'
    return render_template('oligoset_design.html', form=form)


@app.route('/results', methods=['GET'])
@login_required
def oligoset_results():

    jobid = request.args.get('jobid')
    if jobid is not None:
        job = tasks.enqueue_5primer_set.AsyncResult(jobid)
        if job.ready():
            g.results = iternamedtuples(job.get()[0])
            g.explain = iternamedtuples(job.get()[1])


    g.active_page = 'oligoset_results'
    return render_template('oligoset_results.html')

