#!/bin/bash

# This should be added to ~/.bashrc as ALIAS commands


alias directory_list='( for d in */; do [ -d "$d" ] && printf "%s\n" "${d%/}"; done ) > directory_list.csv'
# USAGE: directory_list

# CSV transpose: preserves quoting & commas

alias csvt='python -c '\''import sys,csv;r=list(csv.reader(open(sys.argv[1], newline="")));w=max((len(x) for x in r), default=0);r=[x+[""]*(w-len(x)) for x in r];csv.writer(sys.stdout, lineterminator="\n").writerows(zip(*r))'\'''

# USAGE: csvt input.csv > input_T.csv

# TSV transpose: preserves quoting

alias tsvt='python -c '\''import sys,csv;r=list(csv.reader(open(sys.argv[1], newline=""), delimiter="\t"));w=max((len(x) for x in r), default=0);r=[x+[""]*(w-len(x)) for x in r];csv.writer(sys.stdout, delimiter="\t", lineterminator="\n").writerows(zip(*r))'\'''

# USAGE: tsvt input.tsv > input_T.tsv
