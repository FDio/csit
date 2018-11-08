set -exuo pipefail

run=23
echo > res.txt
echo > suc.txt
res=`readlink -e res.txt`
suc=`readlink -e suc.txt`

function after () {
    set -exuo pipefail

    fgrep 'Trial 248' $res > $suc
    sed -i -E 's/<msg timestamp="(.*)" level="INFO">Trial 248 computed avg (.*) stdev (.*) stretch (.*)/\1,\2,\3/g' $suc
    sed -i -E 's/(.{4})(.{2})(.*)/\1-\2-\3/g' $suc
    cp $suc /home/vrpolak/Downloads/paste.txt
}

trap "after" EXIT
while true; do
    mkdir -p $run
    pushd $run
    echo $run >> $res
    wget -N https://jenkins.fd.io/sandbox/job/csit-vpp-perf-verify-1810-2n-skx/$run/artifact/archive/output.xml
    fgrep computed output.xml >as.txt
    tail -n 1 as.txt >> $res
    cut -d ' ' -f 5- as.txt >as.txt~ ; mv as.txt~ as.txt
    sed -i 's# computed avg#,#g' as.txt
    sed -i 's# stdev#,#g' as.txt
    cut -d ' ' -f 1-3 as.txt >as.txt~ ; mv as.txt~ as.txt
    popd
    ((run+=1))
done
