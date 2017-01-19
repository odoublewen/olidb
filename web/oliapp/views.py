from django.shortcuts import render, HttpResponse, redirect
from oliapp.models import Oligoset, Experiment, Gene
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from oliapp.forms import UserForm


def navbar_context_processor(request):
    navbar = [
        ('oligosets', 'Oligos'),
        ('experiments', 'Experiments'),
        ('design', 'Design'),
    ]
    return {'navbar': navbar}


def index(request):

    context = {'recentexp': Experiment.get_recent(),
               'recentoli': Oligoset.get_recent()}

    return render(request, 'oliapp/index.html', context)


def browse_oligosets(request):

    context = {'currpage': 'oligosets'}
    # if g.sijax.is_sijax_request:
    #     g.sijax.register_object(SijaxHandler)
    #     return g.sijax.process_request()
    #
    experiment_num = request.GET.get('exp', None)

    if experiment_num:
        experiment = Experiment.objects.prefetch_related('oligosets').get(pk=experiment_num)
        context['experiment'] = experiment
        oligosets = experiment.oligosets.all()

    else:
        oligosets = Oligoset.objects.all()

    context['oligosets'] = \
        [(i, obj) for i, obj in enumerate(oligosets.order_by('gene__taxonomy', 'gene__oligoset__tmid'))]

    return render(request, 'oliapp/oligoset_browse.html', context)


def oligoset_details(request, taxatmid):
    try:
        taxa, tmid = taxatmid.split('-')
        item = Oligoset.objects.filter(gene__taxonomy=taxa, tmid=int(tmid)).get()
        context = {'item': item}
    except ObjectDoesNotExist:
        raise Http404()
    return render(request, "oliapp/oligoset_details.html", context)


def browse_experiments(request):
    context = {'currpage': 'experiments'}
    items = Experiment.objects.all()
    context['items'] = items

    return render(request, 'oliapp/experiment_browse.html', context)


def logout_view(request):
    logout(request)


def add_user(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            login(request, new_user)
            # redirect, or however you want to get to the main view
            return index(request)
            # return redirect('oliapp/index.html')
    else:
        form = UserForm()

    return render(request, 'registration/adduser.html', {'form': form})


@login_required
def benchtop(request):

    context = {'recentexp': Experiment.get_recent(),
               'recentoli': Oligoset.get_recent()}

    return render(request, 'oliapp/index.html', context)

    # if g.sijax.is_sijax_request:
    #     g.sijax.register_object(SijaxHandler)
    #     return g.sijax.process_request()
    #
    # form = ExperimentForm(request.form)
    # form.saveas.choices = [('NewExperiment', 'New Experiment')] + [(str(e.id), e.name) for e in current_user.experiments]
    #
    # if form.validate_on_submit():
    #     if form.saveas.data == "NewExperiment":
    #         exp = Experiment(name=form.name.data, description=form.description.data, is_public=form.is_public.data,
    #                          oliuser_id=current_user.id, oligosets=current_user.benchtop_oligosets)
    #     else:
    #         exp = Experiment.query.get(int(form.saveas.data))
    #         exp.oligosets = current_user.benchtop_oligosets
    #         if form.name.data != '':
    #             exp.name = form.name.data
    #         if form.description.data != '':
    #             exp.description = form.description.data
    #
    #     db.session.add(exp)
    #     current_user.benchtop_oligosets = []
    #     db.session.add(current_user)
    #     db.session.commit()
    #     flash('Your benchtop was saved as %s' % exp.name)
    #
    # for job in current_user.jobs:
    #     if datetime.datetime.now() - job.created > datetime.timedelta(seconds=CELERY_TASK_RESULT_EXPIRES):
    #         db.session.delete(job)
    #         db.session.commit()
    #
    # oligoset_list = [o.id for o in current_user.benchtop_oligosets]
    #
    # if len(oligoset_list) > 0:
    #     query = Oligoset.query.join(Target)
    #     query = query.filter(Oligoset.id.in_(oligoset_list))
    #     g.onbench = query.order_by(Target.taxonomy, Oligoset.name).all()
    # else:
    #     g.onbench = []
    #
    # g.myexperiments = current_user.experiments
    #
    # g.active_page = 'benchtop'
    # return render_template('benchtop.html', form=form)

