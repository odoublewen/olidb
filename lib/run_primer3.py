#!/usr/bin/env python
#
import argparse
import logging
from Bio import SeqIO
from subprocess import Popen, PIPE
from re import match, search
from pandas import DataFrame, concat
import sys

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
            pid = primerpatt.group(2)
            ptype = primerpatt.group(1)
            metric = primerpatt.group(3)
            if metric == '':
                metric = 'COORDS'
            value = primerpatt.group(4)
            primers.append([seqid, pid, ptype, metric, value])
            continue

    try:
        primers = DataFrame(primers, columns=['seqid', 'pid', 'ptype', 'metric', 'value'])
    except ValueError:
        primers = None

    try:
        explain = DataFrame(explain, columns=['seqid', 'ptype', 'metric', 'value'])
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
        innerdf['ptype'] = 'TAQMAN_' + innerdf['ptype'].astype(str)

    return innerdf, innerexp


def preamp_primers(seqid, seq, p3settings, p3coords):

    # outer flanking primers
    primer3_in = list()
    for index, row in p3coords.iterrows():
        leftpos = map(int, row.TAQMAN_LEFT.split(','))
        rightpos = map(int, row.TAQMAN_RIGHT.split(','))
        primer3_in.append("SEQUENCE_ID=%s_____%s" % (seqid, index))
        primer3_in.append("SEQUENCE_TEMPLATE=%s" % seq)
        primer3_in.append("SEQUENCE_TARGET=%d,%d" % (leftpos[0]+leftpos[1]-12, rightpos[0]-rightpos[1]+12))
        primer3_in += p3settings
        primer3_in.append("=")

    outerdf, outerexp = run_primer3(primer3_in)

    if outerdf is not None:
        outerdf['ptype'] = 'PREAMP_' + outerdf['ptype'].astype(str)
        outerdf['pid2'] = outerdf['pid']
        outerdf['seqid'], outerdf['pid'] = zip(*outerdf['seqid'].str.split('_____').tolist())

    if outerexp is not None:
        outerexp['ptype'] = 'PREAMP_' + outerexp['ptype'].astype(str)
        outerexp['seqid'].replace(to_replace=r'(.+)_____.*', value=r'\1', inplace=True, regex=True)

    return outerdf, outerexp


def make_5primer_set(seqs, settings1, settings2):

    primerlist = []
    explainlist = []
    for rec in seqs:
        innerdf, innerexp = taqman_primers(rec.id, rec.seq, settings1)
        primerlist.append(innerdf)
        explainlist.append(innerexp)

        if innerdf is not None:
            log.info('%s: Found %d INNER primers sets' % (rec.id, innerdf.pid.nunique()))
            # get the coordinates of each primer pair, so that we can target the flanking primers
            p3coords = innerdf[innerdf.metric == 'COORDS'].pivot(index='pid', columns='ptype', values='value')
            outerdf, outerexp = preamp_primers(rec.id, rec.seq, settings2, p3coords)
            primerlist.append(outerdf)
            explainlist.append(outerexp)

            if outerdf is not None:
                log.info('%s: Found %d OUTER primers sets' % (rec.id, outerdf.pid2.nunique()))
                # primerlist.append(innerdf.append(outerdf))
            else:
                log.info('%s: Failed to find OUTER primers; try relaxing requirements.' % rec.id)
        else:
            log.info('%s: Failed to find INNER primers; try relaxing requirements.' % rec.id)

    try:
        primerdf = concat(primerlist)
    except ValueError:
        primerdf = None

    try:
        explaindf = concat(explainlist)
    except ValueError:
        explaindf = None

    print primerdf
    return primerdf, explaindf


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

    seqobject = SeqIO.parse(args.fasta, format='fasta')

    s1 = [l for l in open(args.settings1).readlines() if l[:7] == 'PRIMER_']
    s2 = [l for l in open(args.settings2).readlines() if l[:7] == 'PRIMER_']

    pdf, edf = make_5primer_set(seqobject, settings1=s1, settings2=s2)

    print pdf
    print edf