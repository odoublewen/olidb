#!/usr/bin/env python

import pandas as pd
from oliapp import db
from oliapp.models import Target, Oligoset, Oligo, Experiment, Recipe
import sys
from sqlalchemy import func, select, update
from subprocess import check_output, CalledProcessError
import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

def loadgenes():
    genes = pd.io.parsers.read_csv(os.path.join(BASE_PATH, 'fixturedata', 'genes.csv'))
    genes = genes.sort(['TAXONOMY', 'GENENAME'])

    for i, row in genes.iterrows():
        t = db.session.query(Target).filter_by(symbol=row.GENENAME)
        if t.count() == 0:
            print '%s [%d]' % (row.GENENAME, i)
            t = Target()
            t.taxonomy = row.TAXONOMY
            t.symbol = row.GENENAME
            t.namelong = row.GENENAMELONG
            t.namealts = row.GENENAMEALTS
        elif t.count() == 1:
            t = t.one()
        else:
            raise RuntimeError('More than one record matching %s' % row.GENENAME)

        print '\t%s' % row.TUBENAME

        d = Oligoset()
        d.tmid = row.TMID
        d.name = row.TUBENAME
        d.notes = row.DESIGNER
        d.location = row.LOCATION
        d.is_obsolete = row.STATUS == 1
        d.is_public = row.G_PUBLIC == 1

        t.oligosets.append(d)

        db.session.add(t)

    db.session.commit()


def loadoligos():
    oligos = pd.io.parsers.read_csv(os.path.join(BASE_PATH, 'fixturedata', 'oligos.csv'), na_filter=False)

    oligos = oligos.sort(['TAXONOMY', 'ID'])
    oligos['ORDERDATEDATE'] = pd.to_datetime(oligos.ORDERDATE)

    last_tubename = ''
    for i, row in oligos.iterrows():
        if row.TUBENAME != last_tubename:
            last_tubename = row.TUBENAME
            d = db.session.query(Oligoset).filter_by(name=row.TUBENAME)
            if d.count() == 0:
                print 'WARNING NOT FOUND %s [%d]' % (row.TUBENAME, i)
            elif d.count() == 1:
                d = d.one()
                print '%s' % row.TUBENAME
            else:
                raise RuntimeError('More than one record matching %s' % row.TUBENAME)

        print '\t%s' % row.OLIGO

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
            o.orderdate = row.ORDERDATEDATE

        d.oligos.append(o)

        db.session.add(d)

    db.session.commit()


def updateoligosetdate():
    for r in Oligoset.query.all():
        newdate = db.session.query(func.min(Oligo.orderdate)).filter(Oligo.oligoset_id==r.id).one()
        print r.id, r.date, newdate
        r.date = newdate
    db.session.commit()



def loadgenesets():
    genesets = pd.io.parsers.read_csv(os.path.join(BASE_PATH, 'fixturedata', 'genesets.csv'), na_filter=False)
    genesets['DATEDATE'] = pd.to_datetime(genesets.GS_DATE)

    genesets_data = pd.io.parsers.read_csv(os.path.join(BASE_PATH, 'fixturedata', 'genesets_data.csv'))

    for i, gs in genesets.iterrows():
        ex = Experiment()
        ex.name = gs.GS_ID
        ex.description = ' / '.join([x for x in [gs.FOLDER, gs.GS_NAME] if x != ''])
        ex.date = gs.GS_DATE
        ex.is_public = True
        print "%s\t%d" % (gs.GS_NAME, i)

        # subset genesets_data
        for j, d in genesets_data.ix[genesets_data.GS_ID == gs.GS_ID].iterrows():
            child = db.session.query(Oligoset).filter_by(name=d.TUBENAME).one()
            ex.oligosets.append(child)
            print '\t%s\t%d' % (child.name, j)

        db.session.add(ex)

    db.session.commit()


def loadrecipes():
    recipefiles = [['auto', 'primer3_config_inner_auto.txt', 'primer3_config_outer_auto.txt'],
                   ['strict', 'primer3_config_inner_strict.txt', 'primer3_config_outer_strict.txt'],
                   ['relaxed', 'primer3_config_inner_relaxed.txt', 'primer3_config_outer_relaxed.txt']]

    for recipename, innerfile, outerfile in recipefiles:
        innerdata = open(os.path.join(BASE_PATH, 'fixturedata', innerfile)).readlines()
        outerdata = open(os.path.join(BASE_PATH, 'fixturedata', outerfile)).readlines()

        innerdata = ''.join([l for l in innerdata if l[:7] == 'PRIMER_'])
        outerdata = ''.join([l for l in outerdata if l[:7] == 'PRIMER_'])

        r = Recipe(recipename=recipename, inner_recipe=innerdata, outer_recipe=outerdata)

        db.session.add(r)

    db.session.commit()


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

