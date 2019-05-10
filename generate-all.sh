#!/bin/bash

mkdir -p palettes

for FMT in ccxml gpl json
do
    python generate.py --format $FMT palettes/githublangs.$FMT
done
