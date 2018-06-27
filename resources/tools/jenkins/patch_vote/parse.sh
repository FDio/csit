#!/bin/bash

set -exu

# TODO: Do we need to make filepaths configurable?
# TODO: Absolute paths via "readlink -e"?
IN_FILE="csit/output.xml"
OUT_FILE="csit/results.txt"

echo "Parsing $IN_FILE putting results into $OUT_FILE"
echo "TODO: Re-use parts of PAL when they support subsample test parsing."

grep -o "'Maximum Receive Rate Results .*\]" "$IN_FILE"

grep -o "'Maximum Receive Rate Results .*\]" "$IN_FILE" | grep -o '\[.*\]' > "$OUT_FILE"
