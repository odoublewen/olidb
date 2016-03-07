from django.shortcuts import render, HttpResponse
from oliapp.models import Oligoset, Experiment


def index(request):

    context = {'recentexp': Experiment.get_recent(),
               'recentoli': Oligoset.get_recent()}

    return render(request, 'oliapp/index.html', context)


def oligosets(request):

    # if g.sijax.is_sijax_request:
    #     g.sijax.register_object(SijaxHandler)
    #     return g.sijax.process_request()
    #
    # g.experiment_num = request.args.get('exp')
    # g.term = request.args.get('term')
    # g.taxonomy = request.args.get('taxonomy')
    #
    # query = Oligoset.query.join(Gene)
    #
    # if g.experiment_num:
    #     experiment = Experiment.query.get(g.experiment_num)
    #     g.experiment_name = experiment.name
    #     oligoset_list = [o.id for o in experiment.oligosets]
    #     query = query.filter(Oligoset.id.in_(oligoset_list))
    #
    # if g.term:
    #     for term in g.term.split(' '):
    #         term = '%%%s%%' % term
    #         query = query.filter(or_(Oligoset.name.ilike(term), Gene.namelong.ilike(term)))
    #
    # if g.taxonomy:
    #     query = query.filter(Gene.taxonomy == g.taxonomy)

    # g.pagination = query.order_by(Gene.taxonomy, Oligoset.name).paginate(page, per_page=100)
    # g.itemids = [i.id for i in g.pagination.items]
    # g.taxa = [q.taxa for q in db.session.query(Gene.taxonomy.distinct().label("taxa")).order_by(Gene.taxonomy).all()]

    context = {'oligosets': Oligoset.objects.all()}

    return render(request, 'oliapp/oligoset_browse.html', context)
