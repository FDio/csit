set -exuo pipefail

as="as.txt"

cat "log.txt" | fgrep 'measure_and_compute finished' | uniq > $as
sed -E -i 's/.*duration=(.*),target_tr=(.*),.*,.* avg (.*) stdev (.*) stretch (.*) erf (.*) new trackers.*/\1, \2, \3, \4, \5, \6/' $as
cp "$as" "/home/vrpolak/Downloads/paste.txt"
echo "SUCCESS"
