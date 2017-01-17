#!/bin/bash

WORKING_DIR='_tmp'
BUILD_DIR='_build'
SOURCE_DIR='../../../docs/report'
STATIC_DIR="${BUILD_DIR}/_static"
CSS_PATCH_FILE="${BUILD_DIR}/_static/theme_overrides.css"

sudo apt-get install -y libxml2 libxml2-dev libxslt-dev build-essential zlib1g-dev

# Clean-up when finished:
trap 'rm -rf ${WORKING_DIR}; exit' EXIT
trap 'rm -rf ${WORKING_DIR}; exit' ERR

# Remove the old build:
rm -rf ${BUILD_DIR} || true
rm -rf ${WORKING_DIR} || true

# Create working directories
mkdir ${BUILD_DIR}

# Create virtual environment:
virtualenv ${WORKING_DIR}/env
. ${WORKING_DIR}/env/bin/activate

# Install Sphinx:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

# Generate the documentation:
sphinx-build -v -c . -a -b html -E -D release=$1 -D version=$1 ${SOURCE_DIR} ${BUILD_DIR}/

# Patch the CSS for tables layout
cat - > ${CSS_PATCH_FILE} <<"_EOF"
/* override table width restrictions */
@media screen and (min-width: 767px) {
    .wy-table-responsive table td, .wy-table-responsive table th {
        white-space: normal !important;
    }

    .wy-table-responsive {
        font-size: small;
        margin-bottom: 24px;
        max-width: 100%;
        overflow: visible !important;
    }
}
_EOF

# Download raw outputs for plots
echo Downloading raw outputs for plots ...
JENKINS_URL='https://jenkins.fd.io/view/csit/job/'
JENKINS_DIR='/artifact/'

PERF_JENKINS_JOB='csit-vpp-perf-1701-all'
PERF_JENKINS_BUILD=(1 3 4)
PERF_JENKINS_FILE='output_perf_data.xml'

for i in "${PERF_JENKINS_BUILD[@]}"; do
    wget -q ${JENKINS_URL}${PERF_JENKINS_JOB}/${i}${JENKINS_DIR}${PERF_JENKINS_FILE} -O ${STATIC_DIR}/${PERF_JENKINS_JOB}-${i}.xml
done

# Plot packets per second

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-l2-ndrdisc --title "64B-1t1c-*l2[bdbase|xcbase]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-l2-ndrdisc --title "64B-2t2c-*l2[bdbase|xcbase]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-l2-ndrdisc --title "64B-4t4c-*l2[bdbase|xcbase]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-ndrdisc --title "64B-1t1c-ethip4-ip4*-ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-ndrdisc --title "64B-2t2c-ethip4-ip4*-ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-ndrdisc --title "64B-4t4c-ethip4-ip4*-ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-ndrdisc --title "78B-1t1c-ethip6-ip6*-ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-ndrdisc --title "78B-2t2c-ethip6-ip6*-ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-ndrdisc --title "78B-4t4c-ethip6-ip6*-ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ndrdisc --title "64B-1t1c-ethip4*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ndrdisc --title "64B-2t2c-ethip4*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ndrdisc --title "64B-4t4c-ethip4*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ndrdisc --title "78B-1t1c-ethip6*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ndrdisc --title "78B-2t2c-ethip6*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ndrdisc --title "78B-4t4c-ethip6*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-ndrdisc --title "64B-1t1c-*vhost*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-ndrdisc --title "64B-2t2c-*vhost*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-ndrdisc --title "64B-4t4c-*vhost*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-l2-pdrdisc --title "64B-1t1c-*l2[bdbase|xcbase]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-l2-pdrdisc --title "64B-2t2c-*l2[bdbase|xcbase]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-l2-pdrdisc --title "64B-4t4c-*l2[bdbase|xcbase]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-pdrdisc --title "64B-1t1c-ethip4-ip4*-pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-pdrdisc --title "64B-2t2c-ethip4-ip4*-pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-pdrdisc --title "64B-4t4c-ethip4-ip4*-pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-pdrdisc --title "78B-1t1c-ethip6-ip6*-pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-pdrdisc --title "78B-2t2c-ethip6-ip6*-pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-pdrdisc --title "78B-4t4c-ethip6-ip6*-pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-pdrdisc --title "64B-1t1c-ethip4*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-pdrdisc --title "64B-2t2c-ethip4*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-pdrdisc --title "64B-4t4c-ethip4*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-pdrdisc --title "78B-1t1c-ethip6*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-pdrdisc --title "78B-2t2c-ethip6*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-pdrdisc --title "78B-4t4c-ethip6*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-pdrdisc --title "64B-1t1c-*vhost*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-pdrdisc --title "64B-2t2c-*vhost*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --lower 2000000 --upper 10000000
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-pdrdisc --title "64B-4t4c-*vhost*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and contains(@tags,"VHOST")]' --lower 2000000 --upper 10000000

# Plot latency

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-l2-ndrdisc-lat50 --title "64B-1t1c-*l2[bdbase|xcbase]*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-l2-ndrdisc-lat50 --title "64B-2t2c-*l2[bdbase|xcbase]*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-l2-ndrdisc-lat50 --title "64B-4t4c-*l2[bdbase|xcbase]*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-ndrdisc-lat50 --title "64B-1t1c-ethip4-ip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-ndrdisc-lat50 --title "64B-2t2c-ethip4-ip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-ndrdisc-lat50 --title "64B-4t4c-ethip4-ip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-ndrdisc-lat50 --title "78B-1t1c-ethip6-ip6*-ndrdisc-lat50" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-ndrdisc-lat50 --title "78B-2t2c-ethip6-ip6*-ndrdisc-lat50" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-ndrdisc-lat50 --title "78B-4t4c-ethip6-ip6*-ndrdisc-lat50" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ndrdisc-lat50 --title "64B-1t1c-ethip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ndrdisc-lat50 --title "64B-2t2c-ethip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ndrdisc-lat50 --title "64B-4t4c-ethip4*-ndrdisc-lat50" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ndrdisc-lat50 --title "78B-1t1c-ethip6*-ndrdisc-lat" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ndrdisc-lat50 --title "78B-2t2c-ethip6*-ndrdisc-lat" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ndrdisc-lat50 --title "78B-4t4c-ethip6*-ndrdisc-lat" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-ndrdisc-lat50 --title "64B-1t1c-*vhost*-ndrdisc-lat" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-ndrdisc-lat50 --title "64B-2t2c-*vhost*-ndrdisc-lat" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --latency lat_50
python run_plot.py --input ${STATIC_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-ndrdisc-lat50 --title "64B-4t4c-*vhost*-ndrdisc-lat" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"VHOST")]' --latency lat_50


# Download raw outputs for archive
#echo Downloading raw outputs for archive ...
#JENKINS_URL='https://jenkins.fd.io/view/csit/job/'
#JENKINS_DIR='/artifact/*zip*/'
#JENKINS_FILE='archive.zip'

#PERF_JENKINS_JOB='csit-vpp-perf-1701-all'
#PERF_JENKINS_BUILD=(1 3 4)

#for i in "${PERF_JENKINS_BUILD[@]}"; do
#    wget -q ${JENKINS_URL}${PERF_JENKINS_JOB}/${i}${JENKINS_DIR}${JENKINS_FILE} -O ${STATIC_DIR}/${PERF_JENKINS_JOB}-${i}.zip
#done

#PERF_JENKINS_JOB='csit-vpp-perf-1701-long'
#PERF_JENKINS_BUILD=(1 2)

#for i in "${PERF_JENKINS_BUILD[@]}"; do
#    wget -q ${JENKINS_URL}${PERF_JENKINS_JOB}/${i}${JENKINS_DIR}${JENKINS_FILE} -O ${STATIC_DIR}/${PERF_JENKINS_JOB}-${i}.zip
#done

#FUNC_JENKINS_JOB='csit-vpp-functional-1701-virl'
#FUNC_JENKINS_BUILD=(18)

#for i in "${FUNC_JENKINS_BUILD[@]}"; do
#    wget -q ${JENKINS_URL}${FUNC_JENKINS_JOB}/${i}${JENKINS_DIR}${JENKINS_FILE} -O ${STATIC_DIR}/${FUNC_JENKINS_JOB}-${i}.zip
#done

# Create archive
echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}

