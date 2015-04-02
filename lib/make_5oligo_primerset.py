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
    explain = []
    # seqid = ''
    for l in primer3_out.splitlines():

        seqidpatt = search('SEQUENCE_ID=(.+)', l)
        if seqidpatt:
            seqid = seqidpatt.group(1)
            continue

        explainpatt = search('EXPLAIN', l)
        if explainpatt:
            explain.append(l)
            continue

        primerpatt = match('PRIMER_(LEFT|RIGHT|INTERNAL|PAIR)_([0-9]+)_?(.*)=(.+)', l)
        if primerpatt:
            primers.append([seqid, primerpatt.group(2), primerpatt.group(1), primerpatt.group(3), primerpatt.group(4)])
            continue

    try:
        primers = pd.DataFrame(primers, columns=['seqid', 'num', 'end', 'metric', 'value'])
    except ValueError:
        primers = None

    return primers, explain


def main():
    # logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    seqid = 'gapdh'
    seq = 'gcctcaagaccttgggctgggactggctgagcctggcgggaggcggggtccgagtcaccgcctgccgccgcgcccccggtttctataaattgagcccgcagcctcccgcttcgctctctgctcctcctgttcgacagtcagccgcatcttcttttgcgtcgccagccgagccacatcgctcagacaccatggggaaggtgaaggtcggagtcaacggatttggtcgtattgggcgcctggtcaccagggctgcttttaactctggtaaagtggatattgttgccatcaatgaccccttcattgacctcaactacatggtttacatgttccaatatgattccacccatggcaaattccatggcaccgtcaaggctgagaacgggaagcttgtcatcaatggaaatcccatcaccatcttccaggagcgagatccctccaaaatcaagtggggcgatgctggcgctgagtacgtcgtggagtccactggcgtcttcaccaccatggagaaggctggggctcatttgcaggggggagccaaaagggtcatcatctctgccccctctgctgatgcccccatgttcgtcatgggtgtgaaccatgagaagtatgacaacagcctcaagatcatcagcaatgcctcctgcaccaccaactgcttagcacccctggccaaggtcatccatgacaactttggtatcgtggaaggactcatgaccacagtccatgccatcactgccacccagaagactgtggatggcccctccgggaaactgtggcgtgatggccgcggggctctccagaacatcatccctgcctctactggcgctgccaaggctgtgggcaaggtcatccctgagctgaacgggaagctcactggcatggccttccgtgtccccactgccaacgtgtcagtggtggacctgacctgccgtctagaaaaacctgccaaatatgatgacatcaagaaggtggtgaagcaggcgtcggagggccccctcaagggcatcctgggctacactgagcaccaggtggtctcctctgacttcaacagcgacacccactcctccacctttgacgctggggctggcattgccctcaacgaccactttgtcaagctcatttcctggtatgacaacgaatttggctacagcaacagggtggtggacctcatggcccacatggcctccaaggagtaagacccctggaccaccagccccagcaagagcacaagaggaagagagagaccctcactgctggggagtccctgccacactcagtcccccaccacactgaatctcccctcctcacagttgccatgtagaccccttgaagaggggaggggcctagggagccgcaccttgtcatgtaccatcaataaagtaccctgtgctcaaccagttaaaaaaaaaaaaaaaaaaaaa'

    # inner taqman primers
    config_file = 'primer3_config_inner_relaxed.txt'
    primer3_in = "SEQUENCE_ID=%s\n" % seqid
    primer3_in += "SEQUENCE_TEMPLATE=%s\n" % seq
    primer3_in += "SEQUENCE_INCLUDED_REGION=50,%d\n" % (len(seq)-100)
    primer3_in += "=\n"

    p3df, explain3 = run_primer3(primer3_in, config_file=config_file)

    p3coords = p3df[p3df.metric == ''].pivot(index='num', columns='end', values='value')
    # p3coords['num'] = p3coords.index.astype(int)
    # p3coords = p3coords.sort(['num'])

    # outer flanking primers
    config_file = 'primer3_config_outer.txt'
    primer3_in = ''
    for index, row in p3coords.iterrows():
        leftpos = map(int, row.LEFT.split(','))
        rightpos = map(int, row.RIGHT.split(','))
        primer3_in += "SEQUENCE_ID=%s__p3__%s\n" % (seqid, index)
        primer3_in += "SEQUENCE_TEMPLATE=%s\n" % seq
        primer3_in += "SEQUENCE_TARGET=%d,%d\n" % (leftpos[0]+leftpos[1]-12, rightpos[0]-rightpos[1]+12)
        primer3_in += "=\n"

    p2df, explain2 = run_primer3(primer3_in, config_file=config_file)
    # print p2df




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

    main()
