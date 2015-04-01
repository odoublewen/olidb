#!/usr/bin/env python
from Bio import SeqIO
from Bio.Emboss import Primer3
from Bio.Seq import Seq
from Bio.Seq import reverse_complement
import sys
import os
import shlex
from subprocess import Popen
from Bio.Blast import NCBIStandalone
from Bio.Blast import NCBIXML

fasta_file = sys.argv[1]
output_file = sys.argv[2]
blast_string = sys.argv[3]
#gene2refseq = sys.argv[4]

blast_db_dict = {'human':'/raid/blastdb/Homo_sapiens.GRCh37.75.cdna.all.fa', \
                 'mouse':'/raid/blastdb/Mus_musculus.GRCm38.75.cdna.all.fa'}
#                 'h37rv':'/usr/share/blastdb/Mus_musculus.NCBIM37.59.cdna.all'}

#if blast_db in blast_db_dict.keys():
try:
    blast_db = blast_db_dict[blast_string]
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise

blast_parser = NCBIStandalone.BlastParser()
blastcmd='/usr/bin/blastall'


def write_primers(rtf, rtr, tmf, tmp, tmr, cur_record, psuffix): #, transcript_hits, gene_hits):

    ratio = 7

    schematic = "-" * int(round(len(cur_record)/ratio))
    primername = cur_record.name + "-" + psuffix

    for (position, note) in [(rtf[1], "RTF"), (rtr[1],"RTR"), (tmf[1], "TMF"), (tmp[1], "TMP"), (tmr[1], "TMR")]:
        position = int(round(position/ratio))
        schematic = schematic[:position] + note + schematic[position+3:]
    print primername + "\t" + schematic

    #blastinfo = ",,," + ",".join( [ " ".join(gene_hits[3]), " ".join(gene_hits[4]), " ".join(gene_hits[5]) ])
    #
    #if max(gene_hits) > 5:
    #    blastinfo = blastinfo + ", MULTIPLE PRIMER BINDING SITES"

#    out.write(schematic + "\n")
    out.write(primername + "-RTF," + ",".join(map(str,rtf) + ['',''] + blast_primer(rtf[0], "rtf")) + "\n")
    out.write(primername + "-RTR," + ",".join(map(str,rtr) + ['',''] + blast_primer(rtr[0], "rtr")) + "\n")
    out.write(primername + "-TMF," + ",".join(map(str,tmf) + ['',''] + blast_primer(tmf[0], "tmf")) + "\n")
    out.write(primername + "-TMP," + ",".join(map(str,tmp) + blast_primer(tmp[0], "tmp")) + "\n")
    out.write(primername + "-TMR," + ",".join(map(str,tmr) + ['',''] + blast_primer(tmr[0], "tmr")) + "\n")

def write_temp_fasta(cur_record):
    output_handle = open("temp-tmprimer-in.fasta", "w")
    output_handle.write(cur_record.format("fasta"))
    output_handle.close()
#    print cur_record.format("fasta")

def make_primers(cur_record):
    seqlength = len(cur_record.seq)
    exclude_beg = "1,50"
    exclude_end = str(seqlength-50) + "," + str(seqlength)
    
    #primer_cl = "eprimer3 "
    primer_cl = "-sequence temp-tmprimer-in.fasta "
    primer_cl += "-outfile temp-tmprimer-out.pr3 "
    primer_cl += "-prange 50-600 "
    primer_cl += "-psizeopt 66 "
    primer_cl += "-hybridprobe Y "
    primer_cl += "-numreturn 200 "
    primer_cl += '-excludedregion "' + exclude_beg + ' ' + exclude_end + '" '

    primer_cl += "-osize 20 "
    primer_cl += "-minsize 15 "
    primer_cl += "-maxsize 30 "

    primer_cl += "-otm 62 "
    primer_cl += "-mintm 56 "
    primer_cl += "-maxtm 65 "

    primer_cl += "-ogcpercent 55 "
    primer_cl += "-mingc 15 "
    primer_cl += "-maxgc 85 "

    primer_cl += "-maxpolyx 10 "

    primer_cl += "-osizeopt 22 "
    primer_cl += "-ominsize 15 "
    primer_cl += "-omaxsize 30 "

    primer_cl += "-otmopt 71 "
    primer_cl += "-otmmin 67 "
    primer_cl += "-otmmax 77 "

    primer_cl += "-ogcopt 55 "
    primer_cl += "-ogcmin 15 "
    primer_cl += "-ogcmax 85 "

    primer_cl += "-opolyxmax 10 "

#    print primer_cl

    primercommand = Popen(args=shlex.split(primer_cl), executable="eprimer3")
    primercommand.wait()



def blast_primer(seq, oligotype):

    qfile = open("temp-blast-query.fasta", "w")
    qfile.write(">query\n"+seq)
    qfile.close()

    os.system("blastn -task blastn-short -dust no -soft_masking false -db " + blast_db + " -outfmt 5 -query temp-blast-query.fasta -out temp-blast-out.xml")

    blast_out = open("temp-blast-out.xml", "r")
    b_records = NCBIXML.parse(blast_out)

    hits = {}

    try:
        for b_record in b_records:
            for alig in b_record.alignments:

                for hsp in alig.hsps:
                    pctmatch = hsp.identities / float(len(seq))
                    if oligotype=="tmp":
                        if hsp.query_end > hsp.query_start:
                            critzone = hsp.query_end==len(seq) and hsp.sbjct[:3]==hsp.query[:3]
                        else:
                            critzone = hsp.query_start==len(seq) and hsp.sbjct[-3:]==hsp.query[-3:]
                    else:
                        if hsp.query_end > hsp.query_start:
                            critzone = hsp.query_end==len(seq) and hsp.sbjct[-3:]==hsp.query[-3:]
                        else:
                            critzone = hsp.query_start==len(seq) and hsp.sbjct[:3]==hsp.query[:3]

                    if pctmatch == 1 or (pctmatch > .75 and critzone):

                        genehit = ""
                        try:
                            genehit = alig.title.split("gene:")[1]
                        except:
                            pass
                        if genehit == "":
                            genehit = "unknown"

                        if genehit in hits:
                            hits[genehit].append(alig.accession)
                        else:
                            hits[genehit] = [alig.accession]

    except ValueError:
        print "ValueError caught:", sys.exc_info()[0]
        pass

    return (['"' + k + ': ' + ', '.join(v) + '"' for k, v in hits.items()])

    
    for b_record in b_records:
        for alig in b_record.alignments:
            hits = len(alig.hsps)



            if hits in transcript_hits:
                transcript_hits[hits].append(str(alig.accession))
            else:
                transcript_hits[hits] = [str(alig.accession)]
                


            if hits in gene_hits:
                gene_hits[hits].append(accession)
            else:
                gene_hits[hits] = [accession]
            


    return (transcript_hits, gene_hits)




def make_flanking(cur_record, target):
    #primer_cl = "eprimer3 "
    primer_cl = "-sequence temp-tmprimer-in.fasta "
    primer_cl += "-outfile temp-tmprimer-out2.pr3 "
    primer_cl += "-prange 50-1000 "
    primer_cl += "-psizeopt 0 "
    primer_cl += "-numreturn 100 "
    primer_cl += "-target " + target + " "

    primer_cl += "-osize 24 "
    primer_cl += "-minsize 15 "
    primer_cl += "-maxsize 30 "

    primer_cl += "-otm 62 "
    primer_cl += "-mintm 56 "
    primer_cl += "-maxtm 68 "

    primer_cl += "-ogcpercent 55 "
    primer_cl += "-mingc 15 "
    primer_cl += "-maxgc 85 "

    primer_cl += "-maxpolyx 10 "
    primer_cl += "-explainflag Y "
    
#    print primer_cl

    primercommand = Popen(args=shlex.split(primer_cl), executable="eprimer3")
    primercommand.wait()


def check_probeseq(probeseq):
#    if probeseq[:2].count('G') == 0 and probeseq.count('C') >= probeseq.count('G'):
#        return (probeseq, 'plus')
#    elif probeseq[-2:].count('C') == 0 and probeseq.count('G') > probeseq.count('C'):
#        return (reverse_complement(probeseq), 'minus')
#    else:
#        return (False, False)
    if probeseq[:2].count('G') == 0 and probeseq[-2:].count('C') == 0:
        if probeseq.count('C') >= probeseq.count('G'):
            return (probeseq, 'plus')
        else:
            return (reverse_complement(probeseq), 'minus')
    elif probeseq[:2].count('G') == 0 and probeseq[-2:].count('C') > 0:
        return (probeseq, 'plus')
    elif probeseq[:2].count('G') > 0 and probeseq[-2:].count('C') == 0:
        return (reverse_complement(probeseq), 'minus')
    return (False, False)

def check_flanking(fseq, rseq):
    #print fseq, fseq[-5:], fseq[-5:].count('C')
    #print fseq, fseq[-5:], fseq[-5:].count('G')
    return True

def pick_primers(cur_record):
    handle_internals = open('temp-tmprimer-out.pr3')
    primer_record = Primer3.read(handle_internals)
    pindex = 0
    for p in primer_record.primers[:10]:
        #print pindex, p.size
        #print p.forward_seq, p.forward_start, p.forward_length, p.forward_length, p.forward_gc
        #print p.internal_seq, p.internal_start, p.internal_length, p.internal_length, p.internal_gc
        #print p.reverse_seq, p.reverse_start, p.reverse_length, p.reverse_length, p.reverse_gc
        pindex += 1
        
        p.internal_seq, probe_strand = check_probeseq(p.internal_seq)
        if p.internal_seq:
            target = str(p.forward_start+12) + ',' + str(p.reverse_start+p.reverse_length-12)
            #print target
            make_flanking(cur_record, target)

            handle_externals = open('temp-tmprimer-out2.pr3')
            flanker_record = Primer3.read(handle_externals)
            findex = 0
            for f in flanker_record.primers[:5]:
                #print findex, f.size
                #print f.forward_seq, f.forward_start, f.forward_length, f.forward_tm, f.forward_gc
                #print f.reverse_seq, f.reverse_start, f.reverse_length, f.reverse_length, f.reverse_gc
                findex += 1

                if check_flanking(f.forward_seq, f.reverse_seq):
                    if probe_strand == 'plus':
                        probe_gap = p.internal_start - (p.forward_start + p.forward_length)
                    else:
                        probe_gap = p.reverse_start - (p.internal_start + p.internal_length)
                    psuffix = str(pindex) + "." + str(findex)

                    write_primers((f.forward_seq, f.forward_start, f.forward_length, f.forward_tm, f.forward_gc), (f.reverse_seq, f.reverse_start, f.reverse_length, f.reverse_tm, f.reverse_gc), (p.forward_seq, p.forward_start, p.forward_length, p.forward_tm, p.forward_gc), (p.internal_seq, p.internal_start, p.internal_length, p.internal_tm, p.internal_gc, probe_strand, probe_gap), (p.reverse_seq, p.reverse_start, p.reverse_length, p.reverse_tm, p.reverse_gc), cur_record, psuffix) #, transcript_hits, gene_hits)


input_file = open(fasta_file, "r")
out = open(output_file, "w")
out.write("Oligo,Seq,Start,Length,TM,GC,ProbeStrand,ProbePrimerGap,BLAST Results\n")

for cur_record in SeqIO.parse(input_file, "fasta"):
    write_temp_fasta(cur_record)
    make_primers(cur_record)

    out.write(cur_record.name + "\n")
    pick_primers(cur_record)


out.close()
os.system("rm temp-tmprimer-out.pr3 temp-tmprimer-out2.pr3 temp-tmprimer-in.fasta temp-blast-query.fasta")
