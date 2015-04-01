#!/usr/bin/env python
#

import sys
import argparse
import logging
from Bio import Entrez
# from Bio import SeqIO
from tempfile import TemporaryFile, NamedTemporaryFile
from subprocess import Popen, PIPE


def temp_fasta(sequence):
    fastahandle = NamedTemporaryFile(delete=False)
    # SeqIO.write(sequence, fastahandle, 'fasta')
    fastahandle.write('>temp\n' + sequence + '\n')
    fastahandle.close()

    return fastahandle.name


def run_primer3(seqid, seq, config_file):

    primer3_in = "SEQUENCE_ID=%s\n" % seqid
    primer3_in += "SEQUENCE_TEMPLATE=%s\n" % seq
    primer3_in += "SEQUENCE_EXCLUDED_REGION=1,50 %d,50\n" % (len(seq)-50)
    primer3_in += "="

    print primer3_in

    p = Popen(['primer3_core', '-p3_settings_file', config_file, '-strict_tags'], stdin=PIPE, stdout=PIPE, bufsize=1)
    primer3_out = p.communicate(input=primer3_in)

    print primer3_out



def main():
    # logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    sequence = 'gcctcaagaccttgggctgggactggctgagcctggcgggaggcggggtccgagtcaccgcctgccgccgcgcccccggtttctataaattgagcccgcagcctcccgcttcgctctctgctcctcctgttcgacagtcagccgcatcttcttttgcgtcgccagccgagccacatcgctcagacaccatggggaaggtgaaggtcggagtcaacggatttggtcgtattgggcgcctggtcaccagggctgcttttaactctggtaaagtggatattgttgccatcaatgaccccttcattgacctcaactacatggtttacatgttccaatatgattccacccatggcaaattccatggcaccgtcaaggctgagaacgggaagcttgtcatcaatggaaatcccatcaccatcttccaggagcgagatccctccaaaatcaagtggggcgatgctggcgctgagtacgtcgtggagtccactggcgtcttcaccaccatggagaaggctggggctcatttgcaggggggagccaaaagggtcatcatctctgccccctctgctgatgcccccatgttcgtcatgggtgtgaaccatgagaagtatgacaacagcctcaagatcatcagcaatgcctcctgcaccaccaactgcttagcacccctggccaaggtcatccatgacaactttggtatcgtggaaggactcatgaccacagtccatgccatcactgccacccagaagactgtggatggcccctccgggaaactgtggcgtgatggccgcggggctctccagaacatcatccctgcctctactggcgctgccaaggctgtgggcaaggtcatccctgagctgaacgggaagctcactggcatggccttccgtgtccccactgccaacgtgtcagtggtggacctgacctgccgtctagaaaaacctgccaaatatgatgacatcaagaaggtggtgaagcaggcgtcggagggccccctcaagggcatcctgggctacactgagcaccaggtggtctcctctgacttcaacagcgacacccactcctccacctttgacgctggggctggcattgccctcaacgaccactttgtcaagctcatttcctggtatgacaacgaatttggctacagcaacagggtggtggacctcatggcccacatggcctccaaggagtaagacccctggaccaccagccccagcaagagcacaagaggaagagagagaccctcactgctggggagtccctgccacactcagtcccccaccacactgaatctcccctcctcacagttgccatgtagaccccttgaagaggggaggggcctagggagccgcaccttgtcatgtaccatcaataaagtaccctgtgctcaaccagttaaaaaaaaaaaaaaaaaaaaa'

    config_file = 'primer3_config_inner.txt'
    # config_file = 'primer3_config_inner_relaxed.txt'

    run_primer3(seqid='gapdh',seq=sequence, config_file=config_file)




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
