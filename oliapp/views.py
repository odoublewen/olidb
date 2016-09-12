from django.shortcuts import render, HttpResponse
from oliapp.models import Oligoset, Experiment
from django.core.paginator import Paginator


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

    # g.pagination = query.order_by(Gene.taxonomy, Oligoset.name).paginate(page, per_page=100)
    # g.itemids = [i.id for i in g.pagination.items]
    # g.taxa = [q.taxa for q in db.session.query(Gene.taxonomy.distinct().label("taxa")).order_by(Gene.taxonomy).all()]

    context['oligosets'] = oligosets

    return render(request, 'oliapp/oligoset_browse.html', context)


def browse_experiments(request):
    context = {'currpage': 'experiments'}
    items = Experiment.objects.all()
    context['items'] = items

    return render(request, 'oliapp/experiment_browse.html', context)
