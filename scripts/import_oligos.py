#!/usr/bin/env python3
import os
import django
import pandas as pd
import sys
import pytz
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Min

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "common.settings")
django.setup()

from oliapp.models import Gene, Oligoset, Oligo, Experiment, Recipe
from common.settings import BASE_DIR

from subprocess import check_output, CalledProcessError
import os


def loadgenes():
    genes = pd.read_csv(os.path.join(BASE_DIR, 'oliapp', 'fixtures', 'genes.csv'))
    genes = genes.sort_values(by=['TAXONOMY', 'GENENAME'])

    for i, row in genes.iterrows():
        try:
            g = Gene.objects.get(symbol=row.GENENAME)
        except ObjectDoesNotExist:
            print('%s [%d]' % (row.GENENAME, i))
            g = Gene()
            g.taxonomy = row.TAXONOMY
            g.symbol = row.GENENAME
            g.namelong = row.GENENAMELONG
            g.namealts = row.GENENAMEALTS
            g.save()
        except MultipleObjectsReturned:
            raise RuntimeError('More than one record matching %s' % row.GENENAME)

        print('\t%s' % row.TUBENAME)

        d = Oligoset()
        d.tmid = row.TMID
        d.name = row.TUBENAME
        d.notes = row.DESIGNER
        d.location = row.LOCATION
        d.is_obsolete = row.STATUS == 1
        d.is_public = row.G_PUBLIC == 1
        d.gene = g
        d.save()


def loadoligos():
    oligos = pd.read_csv(os.path.join(BASE_DIR, 'oliapp', 'fixtures', 'oligos.csv'), na_filter=False)

    oligos = oligos.sort(['TAXONOMY', 'ID'])
    oligos['ORDERDATEDATE'] = pd.to_datetime(oligos.ORDERDATE)

    last_tubename = ''
    for i, row in oligos.iterrows():
        if row.TUBENAME != last_tubename:
            last_tubename = row.TUBENAME
            try:
                d = Oligoset.objects.get(name=row.TUBENAME)
                print('%s' % row.TUBENAME)
            except ObjectDoesNotExist:
                raise RuntimeError('WARNING NOT FOUND %s' % row.TUBENAME, i)
            except MultipleObjectsReturned:
                raise RuntimeError('More than one record matching %s' % row.TUBENAME)

        print('\t%s' % row.OLIGO)

        try:
            tm = check_output(['oligotm','-tp','1','-sc','1',row.SEQUENCE]).strip()
        except CalledProcessError:
            tm = None

        o = Oligo()

        o.oligoid = row.ID
        o.sequence = row.SEQUENCE
        o.tubename = row.OLIGO
        o.probe = row.PROBE
        o.comments = row.COMMENTS
        o.tm = tm

        if not pd.isnull(row.ORDERDATEDATE):
            o.orderdate = pytz.utc.localize(row.ORDERDATEDATE)

        o.oligoset = d
        o.save()


def updateoligosetdate():
    for r in Oligoset.objects.all():
        newdate = Oligo.objects.filter(oligoset=r).aggregate(Min('orderdate'))['orderdate__min']
        print(r.id, r.date, newdate)
        r.date = newdate
        r.save()


def loadgenesets():
    genesets = pd.read_csv(os.path.join(BASE_DIR, 'oliapp', 'fixtures', 'genesets.csv'), na_filter=False)
    genesets['DATEDATE'] = pd.to_datetime(genesets.GS_DATE)

    genesets_data = pd.read_csv(os.path.join(BASE_DIR, 'oliapp', 'fixtures', 'genesets_data.csv'))

    for i, gs in genesets.iterrows():
        ex = Experiment()
        ex.name = gs.GS_ID
        ex.description = ' / '.join([x for x in [gs.FOLDER, gs.GS_NAME] if x != ''])
        ex.date = pytz.utc.localize(gs.DATEDATE)
        ex.is_public = True
        print("%s\t%d" % (gs.GS_NAME, i))
        ex.save()

        # subset genesets_data
        for j, d in genesets_data.ix[genesets_data.GS_ID == gs.GS_ID].iterrows():
            child = Oligoset.objects.get(name=d.TUBENAME)
            ex.oligosets.add(child)
            print('\t%s\t%d' % (child.name, j))


def loadrecipes():
    recipefiles = [['auto', 'primer3_config_inner_auto.txt', 'primer3_config_outer_auto.txt'],
                   ['strict', 'primer3_config_inner_strict.txt', 'primer3_config_outer_strict.txt'],
                   ['relaxed', 'primer3_config_inner_relaxed.txt', 'primer3_config_outer_relaxed.txt']]

    for recipename, innerfile, outerfile in recipefiles:
        innerdata = open(os.path.join(BASE_DIR, 'oliapp', 'fixtures', innerfile)).readlines()
        outerdata = open(os.path.join(BASE_DIR, 'oliapp', 'fixtures', outerfile)).readlines()

        innerdata = ''.join([l for l in innerdata if l[:7] == 'PRIMER_'])
        outerdata = ''.join([l for l in outerdata if l[:7] == 'PRIMER_'])

        r = Recipe(recipename=recipename, inner_recipe=innerdata, outer_recipe=outerdata)
        r.save()


if sys.argv[1] == 'genes':
    loadgenes()

if sys.argv[1] == 'oligos':
    loadoligos()

if sys.argv[1] == 'dates':
    updateoligosetdate()

if sys.argv[1] == 'genesets':
    loadgenesets()

if sys.argv[1] == 'recipes':
    loadrecipes()

if sys.argv[1] == 'all':
    loadgenes()
    loadoligos()
    updateoligosetdate()
    loadgenesets()
    loadrecipes()

