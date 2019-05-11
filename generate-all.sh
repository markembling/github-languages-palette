#!/bin/bash

mkdir -p palettes

for FMT in ccxml gpl ase aco json csv
do
    python generate.py --format $FMT palettes/githublangs.$FMT
done
