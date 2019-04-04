# Simple script to detect changes in testcases run between production and sandbox.

rm -rf output.xml output.xml_ output.xml.gz
wget https://jenkins.fd.io/sandbox/job/csit-vpp-perf-mrr-daily-master-3n-skx/5/artifact/csit/archive/output.xml
wget https://logs.fd.io/production/vex-yul-rot-jenkins-1/csit-vpp-perf-mrr-daily-master-3n-skx/383/archives/output.xml.gz
cp output.xml output.xml_
python o2st.py
mv st.txt s_st.txt
rm output.xml
gunzip -k output.xml.gz
python o2st.py
mv st.txt p_st.txt
diff -dur p_st.txt s_st.txt >.diff
echo SUCCESS
