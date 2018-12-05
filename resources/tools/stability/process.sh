set -exuo pipefail

as="as.txt"
rm -f output.xml $as /home/vrpolak/Downloads/paste.txt
run=14
#wget -N https://logs.fd.io/production/vex-yul-rot-jenkins-1/csit-vpp-perf-verify-1810-2n-skx/$run/archives/output.xml.gz
#wget -N https://logs.fd.io/production/vex-yul-rot-jenkins-1/csit-vpp-perf-verify-1810-3n-hsw/$run/archives/output.xml.gz
wget -N https://logs.fd.io/production/vex-yul-rot-jenkins-1/csit-dpdk-perf-verify-1810-2n-skx/$run/archives/output.xml.gz
gunzip output.xml.gz
#wget -N https://jenkins.fd.io/sandbox/job/csit-vpp-perf-verify-1810-2n-skx/16/artifact/archive/output.xml
fgrep computed output.xml | uniq > $as
cut -d ' ' -f 5- $as > $as~ ; mv $as~ $as
sed -i 's# computed avg#,#g' $as
sed -i 's# stdev#,#g' $as
sed -i 's# stretch#,#g' $as
sed -i 's# erf#,#g' $as
cut -d ' ' -f 1-5 $as > $as~ ; mv $as~ $as
cp $as /home/vrpolak/Downloads/paste.txt
as="rsl.txt"
fgrep frameLoss output.xml | fgrep result: | uniq > $as
sed -E -i 's#(.*)result: rate=(.*)pps, totalReceived=(.*), totalSent=(.*), frameLoss=(.*),(.*),(.*)#    \(\2, \4, \5\),#g' $as
