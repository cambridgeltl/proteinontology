#!/bin/bash

# Download source data.

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SOURCES="
http://purl.obolibrary.org/obo/pr.obo
"

DATADIR="$SCRIPTDIR/../data/original-data"

set -eu

mkdir -p "$DATADIR"

for url in $SOURCES; do
    bn=$(basename "$url")
    if [ -e "$DATADIR/$bn" ]; then
	echo "$DATADIR/$bn exists, skipping download." >&2
    else
	echo "Downloading $url ..." >&2
	wget -P "$DATADIR" "$url"
    fi
done
