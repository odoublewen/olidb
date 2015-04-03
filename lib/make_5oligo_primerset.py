#!/usr/bin/env python
#

import sys
import argparse
import logging
from Bio import Entrez
# from Bio import SeqIO
from tempfile import TemporaryFile, NamedTemporaryFile
from subprocess import Popen, PIPE
from re import match, search
import pandas as pd
from collections import defaultdict

def temp_fasta(sequence):
    fastahandle = NamedTemporaryFile(delete=False)
    # SeqIO.write(sequence, fastahandle, 'fasta')
    fastahandle.write('>temp\n' + sequence + '\n')
    fastahandle.close()

    return fastahandle.name


def run_primer3(primer3_in, config_file):

    p = Popen(['primer3_core', '-p3_settings_file', config_file, '-strict_tags'], stdin=PIPE, stdout=PIPE, bufsize=1)
    primer3_out = p.communicate(input=primer3_in)[0]

    # print primer3_out
    primers = []
    explain = defaultdict(list)
    seqid = ''
    for l in primer3_out.splitlines():

        seqidpatt = search('SEQUENCE_ID=(.+)', l)
        if seqidpatt:
            seqid = seqidpatt.group(1)
            continue

        explainpatt = search('EXPLAIN', l)
        if explainpatt:
            explain[seqid].append(l)
            continue

        primerpatt = match('PRIMER_(LEFT|RIGHT|INTERNAL|PAIR)_([0-9]+)_?(.*)=(.+)', l)
        if primerpatt:
            pid = primerpatt.group(2)
            end = primerpatt.group(1)
            metric = primerpatt.group(3)
            if metric == '':
                metric = 'COORDS'
            value = primerpatt.group(4)
            primers.append([seqid, pid, end, metric, value])
            continue

    try:
        primers = pd.DataFrame(primers, columns=['seqid', 'pid', 'end', 'metric', 'value'])
    except ValueError:
        primers = None

    return primers, explain


def make_inner(seqid, seq, config_file):

    # inner taqman primers
    primer3_in = "SEQUENCE_ID=%s\n" % seqid
    primer3_in += "SEQUENCE_TEMPLATE=%s\n" % seq
    primer3_in += "SEQUENCE_INCLUDED_REGION=50,%d\n" % (len(seq)-100)
    primer3_in += "=\n"

    innerdf, innerexp = run_primer3(primer3_in, config_file=config_file)

    if innerdf is None:
        raise RuntimeError(innerexp)

    innerdf['end'] = 'TAQMAN_' + innerdf['end'].astype(str)
    return innerdf


def make_outer(seqid, seq, config_file, p3coords):

    # outer flanking primers
    primer3_in = ''
    for index, row in p3coords.iterrows():
        leftpos = map(int, row.TAQMAN_LEFT.split(','))
        rightpos = map(int, row.TAQMAN_RIGHT.split(','))
        primer3_in += "SEQUENCE_ID=%s_____%s\n" % (seqid, index)
        primer3_in += "SEQUENCE_TEMPLATE=%s\n" % seq
        primer3_in += "SEQUENCE_TARGET=%d,%d\n" % (leftpos[0]+leftpos[1]-12, rightpos[0]-rightpos[1]+12)
        primer3_in += "=\n"

    outerdf, outerexp = run_primer3(primer3_in, config_file=config_file)

    if outerdf is None:
        raise RuntimeError(outerexp)

    outerdf['end'] = 'PREAMP_' + outerdf['end'].astype(str)
    outerdf['pid2'] = outerdf['pid']
    outerdf['seqid'], outerdf['pid'] = zip(*outerdf['seqid'].str.split('_____').tolist())
    return outerdf


def make_5primer_set():

    # logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    seqid = 'gapdh'
    seq = 'gcctcaagaccttgggctgggactggctgagcctggcgggaggcggggtccgagtcaccgcctgccgccgcgcccccggtttctataaattgagcccgcagcctcccgcttcgctctctgctcctcctgttcgacagtcagccgcatcttcttttgcgtcgccagccgagccacatcgctcagacaccatggggaaggtgaaggtcggagtcaacggatttggtcgtattgggcgcctggtcaccagggctgcttttaactctggtaaagtggatattgttgccatcaatgaccccttcattgacctcaactacatggtttacatgttccaatatgattccacccatggcaaattccatggcaccgtcaaggctgagaacgggaagcttgtcatcaatggaaatcccatcaccatcttccaggagcgagatccctccaaaatcaagtggggcgatgctggcgctgagtacgtcgtggagtccactggcgtcttcaccaccatggagaaggctggggctcatttgcaggggggagccaaaagggtcatcatctctgccccctctgctgatgcccccatgttcgtcatgggtgtgaaccatgagaagtatgacaacagcctcaagatcatcagcaatgcctcctgcaccaccaactgcttagcacccctggccaaggtcatccatgacaactttggtatcgtggaaggactcatgaccacagtccatgccatcactgccacccagaagactgtggatggcccctccgggaaactgtggcgtgatggccgcggggctctccagaacatcatccctgcctctactggcgctgccaaggctgtgggcaaggtcatccctgagctgaacgggaagctcactggcatggccttccgtgtccccactgccaacgtgtcagtggtggacctgacctgccgtctagaaaaacctgccaaatatgatgacatcaagaaggtggtgaagcaggcgtcggagggccccctcaagggcatcctgggctacactgagcaccaggtggtctcctctgacttcaacagcgacacccactcctccacctttgacgctggggctggcattgccctcaacgaccactttgtcaagctcatttcctggtatgacaacgaatttggctacagcaacagggtggtggacctcatggcccacatggcctccaaggagtaagacccctggaccaccagccccagcaagagcacaagaggaagagagagaccctcactgctggggagtccctgccacactcagtcccccaccacactgaatctcccctcctcacagttgccatgtagaccccttgaagaggggaggggcctagggagccgcaccttgtcatgtaccatcaataaagtaccctgtgctcaaccagttaaaaaaaaaaaaaaaaaaaaa'

    seqid = 'ACTB'
    seq = 'ACCGCCGAGACCGCGTCCGCCCCGCGAGCACAGAGCCTCGCCTTTGCCGATCCGCCGCCCGTCCACACCCGCCGCCAGCTCACCATGGATGATGATATCGCCGCGCTCGTCGTCGACAACGGCTCCGGCATGTGCAAGGCCGGCTTCGCGGGCGACGATGCCCCCCGGGCCGTCTTCCCCTCCATCGTGGGGCGCCCCAGGCACCAGGGCGTGATGGTGGGCATGGGTCAGAAGGATTCCTATGTGGGCGACGAGGCCCAGAGCAAGAGAGGCATCCTCACCCTGAAGTACCCCATCGAGCACGGCATCGTCACCAACTGGGACGACATGGAGAAAATCTGGCACCACACCTTCTACAATGAGCTGCGTGTGGCTCCCGAGGAGCACCCCGTGCTGCTGACCGAGGCCCCCCTGAACCCCAAGGCCAACCGCGAGAAGATGACCCAGATCATGTTTGAGACCTTCAACACCCCAGCCATGTACGTTGCTATCCAGGCTGTGCTATCCCTGTACGCCTCTGGCCGTACCACTGGCATCGTGATGGACTCCGGTGACGGGGTCACCCACACTGTGCCCATCTACGAGGGGTATGCCCTCCCCCATGCCATCCTGCGTCTGGACCTGGCTGGCCGGGACCTGACTGACTACCTCATGAAGATCCTCACCGAGCGCGGCTACAGCTTCACCACCACGGCCGAGCGGGAAATCGTGCGTGACATTAAGGAGAAGCTGTGCTACGTCGCCCTGGACTTCGAGCAAGAGATGGCCACGGCTGCTTCCAGCTCCTCCCTGGAGAAGAGCTACGAGCTGCCTGACGGCCAGGTCATCACCATTGGCAATGAGCGGTTCCGCTGCCCTGAGGCACTCTTCCAGCCTTCCTTCCTGGGCATGGAGTCCTGTGGCATCCACGAAACTACCTTCAACTCCATCATGAAGTGTGACGTGGACATCCGCAAAGACCTGTACGCCAACACAGTGCTGTCTGGCGGCACCACCATGTACCCTGGCATTGCCGACAGGATGCAGAAGGAGATCACTGCCCTGGCACCCAGCACAATGAAGATCAAGATCATTGCTCCTCCTGAGCGCAAGTACTCCGTGTGGATCGGCGGCTCCATCCTGGCCTCGCTGTCCACCTTCCAGCAGATGTGGATCAGCAAGCAGGAGTATGACGAGTCCGGCCCCTCCATCGTCCACCGCAAATGCTTCTAGGCGGACTATGACTTAGTTGCGTTACACCCTTTCTTGACAAAACCTAACTTGCGCAGAAAACAAGATGAGATTGGCATGGCTTTATTTGTTTTTTTTGTTTTGTTTTGGTTTTTTTTTTTTTTTTGGCTTGACTCAGGATTTAAAAACTGGAACGGTGAAGGTGACAGCAGTCGGTTGGAGCGAGCATCCCCCAAAGTTCACAATGTGGCCGAGGACTTTGATTGCACATTGTTGTTTTTTTAATAGTCATTCCAAATATGAGATGCGTTGTTACAGGAAGTCCCTTGCCATCCTAAAAGCCACCCCACTTCTCTCTAAGGAGAATGGCCCAGTCCTCTCCCAAGTCCACACAGGGGAGGTGATAGCATTGCTTTCGTGTAAATTATGTAATGCAAAATTTTTTTAATCTTCGCCTTAATACTTTTTTATTTTGTTTTATTTTGAATGATGAGCCTTCGTGCCCCCCCTTCCCCCTTTTTTGTCCCCCAACTTGAGATGTATGAAGGCTTTTGGTCTCCCTGGGAGTGGGTGGAGGCAGCCAGGGCTTACCTGTACACTGACTTGAGACCAGTTGAATAAAAGTGCACACCTTAAAAATGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'


    try:
        innerdf = make_inner(seqid, seq, 'primer3_config_inner.txt')
    except RuntimeError:
        innerdf = make_inner(seqid, seq, 'primer3_config_inner_relaxed.txt')

    # get the coordinates of each primer pair, so that we can target the flanking primers
    p3coords = innerdf[innerdf.metric == 'COORDS'].pivot(index='pid', columns='end', values='value')
    # config_file = 'primer3_config_outer.txt'
    config_file = 'primer3_config_outer_relaxed.txt'
    outerdf = make_outer(seqid, seq, config_file, p3coords)

    # print innerdf
    # print outerdf
    df = innerdf.append(outerdf)
    print df

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Designs a five-oligo primer set (taqman probe and primers, plus flanking primers for pre-amp)"
    )

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

    make_5primer_set()
