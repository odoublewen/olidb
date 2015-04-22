#!/usr/bin/env python
#
import argparse
import logging
from Bio import SeqIO
from subprocess import Popen, PIPE
from re import match, search
import pandas as pd
import sys
import pdb

log = logging.getLogger(__name__)


def run_primer3(primer3_in):

    primer3_in = '\n'.join(primer3_in) + '\n'

    p = Popen(['primer3_core', '-strict_tags'], stdin=PIPE, stdout=PIPE, bufsize=1)
    primer3_out = p.communicate(input=primer3_in)[0]

    primers = []
    explain = []
    seqid = ''
    for l in primer3_out.splitlines():

        seqidpatt = search('SEQUENCE_ID=(.+)', l)
        if seqidpatt:
            seqid = seqidpatt.group(1)
            continue

        explainpatt = search('PRIMER_(LEFT|RIGHT|INTERNAL|PAIR)_EXPLAIN=(.+)', l)
        if explainpatt:
            ptype = explainpatt.group(1)
            for kv in explainpatt.group(2).split(','):
                kvpatt = search('(.+) ([0-9]+)', kv.strip())
                explain.append([seqid, ptype, kvpatt.group(1), kvpatt.group(2)])
            continue

        primerpatt = match('PRIMER_(LEFT|RIGHT|INTERNAL|PAIR)_([0-9]+)_?(.*)=(.+)', l)
        if primerpatt:
            pnum = primerpatt.group(2)
            pid = seqid + '____' + pnum

            ptype = primerpatt.group(1)
            metric = primerpatt.group(3)
            if metric == '':
                metric = 'COORDS'
            variable = ptype + '_' + metric

            value = primerpatt.group(4)
            primers.append([pid, variable, value])
            continue

    try:
        primers = pd.DataFrame(primers, columns=['pid', 'variable', 'value'])
    except ValueError:
        primers = None

    try:
        explain = pd.DataFrame(explain, columns=['seqid', 'ptype', 'variable', 'value'])
    except ValueError:
        explain = None

    return primers, explain


def taqman_primers(seqid, seq, p3settings):

    # inner taqman primers
    primer3_in = list()
    primer3_in.append("SEQUENCE_ID=%s" % seqid)
    primer3_in.append("SEQUENCE_TEMPLATE=%s" % seq)
    primer3_in.append("SEQUENCE_INCLUDED_REGION=50,%d" % (len(seq)-100))
    primer3_in += p3settings
    primer3_in.append("=")

    innerdf, innerexp = run_primer3(primer3_in)

    if innerdf is not None:
        innerdf['variable'] = 'TAQMAN_' + innerdf['variable'].astype(str)

    if innerexp is not None:
        innerexp['ptype'] = 'TAQMAN_' + innerexp['ptype'].astype(str)

    return innerdf, innerexp


def preamp_primers(seqid, seq, p3settings, p3coords):

    # outer flanking primers
    primer3_in = list()
    for index, row in p3coords.iterrows():
        leftpos = map(int, row.TAQMAN_LEFT_COORDS.split(','))
        rightpos = map(int, row.TAQMAN_RIGHT_COORDS.split(','))
        primer3_in.append("SEQUENCE_ID=%s" % index)
        primer3_in.append("SEQUENCE_TEMPLATE=%s" % seq)
        primer3_in.append("SEQUENCE_TARGET=%d,%d" % (leftpos[0]+leftpos[1]-12, rightpos[0]-rightpos[1]+12))
        primer3_in += p3settings
        primer3_in.append("=")

    outerdf, outerexp = run_primer3(primer3_in)

    if outerdf is not None:
        outerdf['variable'] = 'PREAMP_' + outerdf['variable'].astype(str)

    if outerdf is not None:
        outerexp['ptype'] = 'PREAMP_' + outerexp['ptype'].astype(str)

    return outerdf, outerexp


def make_5primer_set(seqs, settings1, settings2):

    innerprimerlist = []
    innerexplainlist = []
    outerprimerlist = []
    outerexplainlist = []

    for seqid, seqstring in seqs.iteritems():
        innerpr, innerexp = taqman_primers(seqid, seqstring, settings1)
        innerexplainlist.append(innerexp)

        if innerpr is not None:
            log.info('%s: Found %d INNER primers sets' % (seqid, innerpr.pid.nunique()))
            innerprimerlist.append(innerpr)

            # get the coordinates of each primer pair, so that we can target the flanking primers
            p3coords = innerpr[innerpr.variable.str.contains('COORDS')].pivot(index='pid', columns='variable', values='value')
            outerdf, outerexp = preamp_primers(seqid, seqstring, settings2, p3coords)
            outerexplainlist.append(outerexp)

            if outerdf is not None:
                log.info('%s: Found %d OUTER primers sets' % (seqid, outerdf.pid.nunique()))
                outerprimerlist.append(outerdf)

            else:
                log.info('%s: Failed to find OUTER primers; try relaxing requirements.' % seqid)

        else:
            log.info('%s: Failed to find INNER primers; try relaxing requirements.' % seqid)

    try:
        innerprimerdf = pd.concat(innerprimerlist)
        innerprimerdf = innerprimerdf.pivot(index='pid', columns='variable', values='value')
        outerprimerdf = pd.concat(outerprimerlist)
        outerprimerdf = outerprimerdf.pivot(index='pid', columns='variable', values='value')
        outerprimerdf['pidkey'] = outerprimerdf.index.to_series().replace(to_replace=r'(.+____[0-9]+)____[0-9]+', value=r'\1', inplace=False, regex=True)
        primerdf = pd.merge(left=innerprimerdf, right=outerprimerdf, left_index=True, right_on='pidkey', suffixes=('_inner','_outer'))
    except ValueError:
        primerdf = None

    innerexplaindf = pd.concat(innerexplainlist)
    if outerexplainlist is not None:
        outerexplaindf = pd.concat(outerexplainlist)
        outerexplaindf['seqid'].replace(to_replace=r'(.+)____[0-9]+', value=r'\1', inplace=True, regex=True)
        explaindf = pd.concat([innerexplaindf, outerexplaindf])
    else:
        explaindf = innerexplaindf

    explaindf['value'] = explaindf['value'].astype(int)
    explaindf = explaindf.groupby(['seqid', 'ptype', 'variable'], as_index=False)['value'].sum().\
        sort(['seqid', 'ptype', 'value'], ascending=[True, True, False])


    # import ipdb; ipdb.set_trace()

    return primerdf, explaindf


# primerdf.columns.values
# array(['TAQMAN_INTERNAL_COORDS', 'TAQMAN_INTERNAL_GC_PERCENT',
#        'TAQMAN_INTERNAL_HAIRPIN_TH', 'TAQMAN_INTERNAL_PENALTY',
#        'TAQMAN_INTERNAL_SELF_ANY_TH', 'TAQMAN_INTERNAL_SELF_END_TH',
#        'TAQMAN_INTERNAL_SEQUENCE', 'TAQMAN_INTERNAL_TM',
#        'TAQMAN_LEFT_COORDS', 'TAQMAN_LEFT_END_STABILITY',
#        'TAQMAN_LEFT_GC_PERCENT', 'TAQMAN_LEFT_HAIRPIN_TH',
#        'TAQMAN_LEFT_PENALTY', 'TAQMAN_LEFT_SELF_ANY_TH',
#        'TAQMAN_LEFT_SELF_END_TH', 'TAQMAN_LEFT_SEQUENCE', 'TAQMAN_LEFT_TM',
#        'TAQMAN_PAIR_COMPL_ANY_TH', 'TAQMAN_PAIR_COMPL_END_TH',
#        'TAQMAN_PAIR_PENALTY', 'TAQMAN_PAIR_PRODUCT_SIZE',
#        'TAQMAN_RIGHT_COORDS', 'TAQMAN_RIGHT_END_STABILITY',
#        'TAQMAN_RIGHT_GC_PERCENT', 'TAQMAN_RIGHT_HAIRPIN_TH',
#        'TAQMAN_RIGHT_PENALTY', 'TAQMAN_RIGHT_SELF_ANY_TH',
#        'TAQMAN_RIGHT_SELF_END_TH', 'TAQMAN_RIGHT_SEQUENCE',
#        'TAQMAN_RIGHT_TM', 'PREAMP_LEFT_COORDS',
#        'PREAMP_LEFT_END_STABILITY', 'PREAMP_LEFT_GC_PERCENT',
#        'PREAMP_LEFT_HAIRPIN_TH', 'PREAMP_LEFT_PENALTY',
#        'PREAMP_LEFT_SELF_ANY_TH', 'PREAMP_LEFT_SELF_END_TH',
#        'PREAMP_LEFT_SEQUENCE', 'PREAMP_LEFT_TM',
#        'PREAMP_PAIR_COMPL_ANY_TH', 'PREAMP_PAIR_COMPL_END_TH',
#        'PREAMP_PAIR_PENALTY', 'PREAMP_PAIR_PRODUCT_SIZE',
#        'PREAMP_RIGHT_COORDS', 'PREAMP_RIGHT_END_STABILITY',
#        'PREAMP_RIGHT_GC_PERCENT', 'PREAMP_RIGHT_HAIRPIN_TH',
#        'PREAMP_RIGHT_PENALTY', 'PREAMP_RIGHT_SELF_ANY_TH',
#        'PREAMP_RIGHT_SELF_END_TH', 'PREAMP_RIGHT_SEQUENCE',
#        'PREAMP_RIGHT_TM', 'pidkey'], dtype=object)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Designs a five-oligo primer set (taqman probe and primers, plus flanking primers for pre-amp)"
    )

    parser.add_argument(
        "-f",
        '--fasta',
        help="fasta file",
        required=True)
    parser.add_argument(
        "-s1",
        '--settings1',
        help="settings file for inner primers",
        required=True)
    parser.add_argument(
        "-s2",
        '--settings2',
        help="settings file for outer primers",
        required=True)

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    args = parser.parse_args()

    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    seqdict = dict([(rec.id, str(rec.seq)) for rec in SeqIO.parse(args.fasta, format='fasta')])

    s1 = [l.strip() for l in open(args.settings1).readlines() if l[:7] == 'PRIMER_']
    s2 = [l.strip() for l in open(args.settings2).readlines() if l[:7] == 'PRIMER_']

    pdf, edf = make_5primer_set(seqdict, settings1=s1, settings2=s2)
