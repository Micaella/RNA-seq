#!/usr/bin/env python

import sys
import os
from parsl import load, python_app, bash_app
from parsl.configs.local_threads import config
from parsl.data_provider.files import File
from pathlib import Path
load(config)

@bash_app
def bowtie(p, baseGenomica, inputs, stdout=None):
    #print(baseGenomica, inputs)
    return 'bowtie2 -p {0} -x {1} -U {2}'.format(p, baseGenomica, inputs)

@bash_app
def htSeq_count(saida, gtf, stdout=None):
    #print(saida, gtf)
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union  {0} {1}'.format(saida, gtf)

@bash_app
def DEseq(dseq2, saida, vetor, stdout=None ):
    #print(dseq2, saida)
    return '{0} {1} {2}'.format(dseq2, saida, vetor)

###   Bowtei2   ###
base_bowtie= sys.argv[1]
inputs_bowtie= sys.argv[2]
saida= sys.argv[3]

###   htSeq-count   ###
gtf= sys.argv[4]

###   DEseq   ###
exc_dseq2= sys.argv[5]


p = Path(inputs_bowtie)
fasta = list(p.glob('*.gz'))
output = Path(saida)

###   Bowtei2   ###
for i in fasta:
    prefix = Path(i).stem
    saida_bowtie = os.path.join(output, prefix+'.sam')
    #print('saida_bowtie:', saida_bowtie)
    teste = bowtie(1, Path(base_bowtie).resolve(), i, stdout=saida_bowtie)

teste.result()

###   HtSeq-count   ###
sam = list(output.glob('*.sam'))

for l in sam:
    prefix = Path(l).stem
    saida_htseq = os.path.join(output, prefix+'.counts')
    #print('entreda_htseq:', l)
    #print('saida_htseq:', saida_htseq)
    teste = htSeq_count(l, Path(gtf).resolve(), stdout=saida_htseq)

teste.result()

### DEseq2   ###
count = list(output.glob('*.counts'))
vetor = []

for c in count:
    vetor.append(c)

saida_DEseq = os.path.join(output, 'teste.deseq')
teste = DEseq(Path(exc_dseq2).resolve(), output, vetor, stdout=saida_DEseq)
teste.result()

