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
    return 'bowtie2 -p {0} -x {1} -U {2}'.format(p, baseGenomica, inputs)

@bash_app
def htSeq_count(saida, gtf, stdout=None):
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union  {0} {1}'.format(saida, gtf)

# Cleaning head lines of counts files obtained with htseq-count
# @bahs_app
# def grep(file, stdout):
#     return 'grep -vwE "processed" {} > {}'.format(file, stdout)

@bash_app
def DEseq(dseq2, saida, stdout=None):
    return '{0} {1}'.format(dseq2, saida)

# Parâmetros bowtie2
base_bowtie, inputs_bowtie, saida = sys.argv[1], sys.argv[2], sys.argv[3]

p = Path(inputs_bowtie).parent
pattern = str(Path(inputs_bowtie).name)+'*'
fasta = list(p.glob(pattern))
output = Path(saida)

for i in fasta:
    prefix = Path(i).stem
    saida_bowtie = os.path.join(output, prefix+'.sam')
    bow = bowtie(1, Path(base_bowtie).resolve(), i, stdout=saida_bowtie)

bow.result()

# Parâmetros htSeq-count
gtf= sys.argv[4]
saida = []

sam = list(output.glob('*.sam'))

for l in sam:
    prefix = Path(l).stem
    saida_htseq = os.path.join(output, prefix)
    exc = htSeq_count(l, Path(gtf).resolve(), stdout=saida_htseq)
    saida.append(exc)

wait_results = [i.result() for i in saida]

# Parâmetros DEseq
exc_dseq2= sys.argv[5]

# counts = list(output.glob('*.counts'))
# lista_exe = []
# for i in counts:
#     prefix = Path(i).stem
#     cleanFile = os.path.join(output, prefix + '.clean.counts')
#     exe_grep = grep(i, stdout = cleanFile)
#     lista_exe.append(exe_grep)
# grep_results = [j.results for j in lista_exe]

saida_DEseq = os.path.join(output, 'teste.deseq')
teste = DEseq(Path(exc_dseq2).resolve(), output, stdout=saida_DEseq)
teste.result()
