#!/bin/bash

set -exu

# TODO: Absolute paths via "readlink -e"?
REL_DIR="$1"
IN_FILE="$REL_DIR/output.xml"
OUT_FILE="$REL_DIR/results.txt"

echo "Parsing $IN_FILE putting results into $OUT_FILE"
echo "TODO: Re-use parts of PAL when they support subsample test parsing."

grep -o "'\\\\nMaximum Receive Rate trial results in packets per second: .*\]'" "$IN_FILE" | grep -o '\[.*\]' > "$OUT_FILE"
