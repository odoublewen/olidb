#!/usr/bin/env python

import pandas as pd
from oliapp import db, models
import sys


def loadgenes():
    genes = pd.io.parsers.read_csv('scripts/genes.csv')
    genes = genes.sort(['TAXONOMY', 'GENENAME'])

    for i, row in genes.iterrows():
        t = db.session.query(models.Target).filter_by(genename=row.GENENAME)
        if t.count() == 0:
            print '%s [%d]' % (row.GENENAME, i)
            t = models.Target()
            t.taxonomy = row.TAXONOMY
            t.genename = row.GENENAME
            t.targetnamelong = row.GENENAMELONG
            t.targetnamealts = row.GENENAMEALTS
        elif t.count() == 1:
            t = t.one()
        else:
            raise RuntimeError('More than one record matching %s' % row.GENENAME)

        print '\t%s' % row.TUBENAME

        d = models.Oligoset()
        d.tmid = row.TMID
        d.setname = row.TUBENAME
        d.designer = row.DESIGNER
        d.location = row.LOCATION
        d.is_obsolete = row.STATUS == 1
        d.is_public = row.G_PUBLIC == 1

        t.oligosets.append(d)

        db.session.add(t)

    db.session.commit()


def loadoligos():
    oligos = pd.io.parsers.read_csv('scripts/oligos.csv', na_filter=False)

    oligos = oligos.sort(['TAXONOMY', 'ID'])
    oligos['ORDERDATEDATE'] = pd.to_datetime(oligos.ORDERDATE)

    last_tubename = ''
    for i, row in oligos.iterrows():
        if row.TUBENAME != last_tubename:
            last_tubename = row.TUBENAME
            d = db.session.query(models.Oligoset).filter_by(setname=row.TUBENAME)
            if d.count() == 0:
                print 'WARNING NOT FOUND %s [%d]' % (row.TUBENAME, i)
            elif d.count() == 1:
                d = d.one()
                print '%s' % row.TUBENAME
            else:
                raise RuntimeError('More than one record matching %s' % row.TUBENAME)

        print '\t%s' % row.OLIGO

        o = models.Oligo()

        o.oligoid = row.ID
        o.sequence = row.SEQUENCE
        o.tubename = row.OLIGO
        o.probe = row.PROBE
        o.comments = row.COMMENTS
        if not pd.isnull(row.ORDERDATEDATE):
            o.orderdate = row.ORDERDATEDATE

        d.oligos.append(o)

        db.session.add(d)

    db.session.commit()

def loadgenesets():
    genesets = pd.io.parsers.read_csv('scripts/genesets.csv', na_filter=False)
    genesets['DATEDATE'] = pd.to_datetime(genesets.GS_DATE)

    genesets_data = pd.io.parsers.read_csv('scripts/genesets_data.csv')

    for i, gs in genesets.iterrows():
        ex = models.Experiment()
        ex.name = gs.GS_ID
        ex.description = gs.GS_NAME
        ex.date = gs.GS_DATE
        ex.folder = gs.FOLDER
        ex.notes = gs.GS_NOTES
        print "%s\t%d" % (gs.GS_NAME, i)

        # subset genesets_data
        for j, d in genesets_data.ix[genesets_data.GS_ID == gs.GS_ID].iterrows():
            child = db.session.query(models.Oligoset).filter_by(setname=d.TUBENAME).one()
            ex.oligosets.append(child)
            print '\t%s\t%d' % (child.setname, j)

        db.session.add(ex)

    db.session.commit()


if sys.argv[1] == 'genes':
    loadgenes()

if sys.argv[1] == 'oligos':
    loadoligos()

if sys.argv[1] == 'genesets':
    loadgenesets()

if sys.argv[1] == 'all':
    loadgenes()
    loadoligos()
    loadgenesets()

