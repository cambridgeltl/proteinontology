#!/bin/bash

# Extract mapping to UniProt IDs.

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INDIR="$SCRIPTDIR/../data/compacted"
OUTDIR="$SCRIPTDIR/../"

set -eu

for f in $(find "$INDIR" -maxdepth 1 -name '*.jsonld'); do
    b=$(basename $f .og)
    o="$OUTDIR/${b}-idmapping.dat"
    if [[ -s "$o" && "$o" -nt "$f" ]]; then
	echo "Newer $o exists, skipping ..." >&2
    else
	echo "Extracting IDs from $f to $o..." >&2
	python "$SCRIPTDIR/getidmapping.py" -g "$f" > "$o"
    fi
done
