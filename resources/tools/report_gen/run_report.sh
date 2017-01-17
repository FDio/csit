#!/bin/bash

WORKING_DIR='_tmp'
BUILD_DIR='_build'
SOURCE_DIR='../../../docs/report'
PLOT_DIR="${BUILD_DIR}/_static"
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
sphinx-build -v -c . -a -b html ${SOURCE_DIR} ${BUILD_DIR}/

# Patch the CSS for tables layout
cat - > ${CSS_PATCH_FILE} <<"_EOF"
/* override table width restrictions */
@media screen and (min-width: 767px) {
    .wy-table-responsive table td, .wy-table-responsive table th {
        white-space: normal !important;
    }

    .wy-table-responsive {
        margin-bottom: 24px;
        max-width: 100%;
        overflow: visible !important;
    }
}
_EOF

# Generate the plots
JENKINS_JOB='https://jenkins.fd.io/view/csit/job/csit-vpp-perf-1701-all/'
JENKINS_BUILD=(1)
JENKINS_DIR='/artifact/'
JENKINS_FILE='output_perf_data.xml'

for i in ${JENKINS_BUILD[@]}; do
    wget ${JENKINS_JOB}${i}${JENKINS_DIR}${JENKINS_FILE} -O ${PLOT_DIR}/${i}-${JENKINS_FILE}
done

# Plot packets per second

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-eth-l2-ndrdisc --title 64B-1t1c-eth-l2\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-eth-l2-ndrdisc --title 64B-2t2c-eth-l2\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 26000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-eth-l2-ndrdisc --title 64B-4t4c-eth-l2\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 36000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-ndrdisc --title 64B-1t1c-ethip4-ip4\*-ndrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP4FWD")]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-ndrdisc --title 64B-2t2c-ethip4-ip4\*-ndrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP4FWD")]' --lower 0 --upper 24000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-ndrdisc --title 64B-4t4c-ethip4-ip4\*-ndrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP4FWD")]' --lower 0 --upper 32000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-ndrdisc --title 78B-1t1c-ethip6-ip6\*-ndrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP6FWD")]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-ndrdisc --title 78B-2t2c-ethip6-ip6\*-ndrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP6FWD")]' --lower 5000000 --upper 20000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-ndrdisc --title 78B-4t4c-ethip6-ip6\*-ndrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP6FWD")]' --lower 14000000 --upper 30000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ndrdisc --title 64B-1t1c-ethip4\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ndrdisc --title 64B-2t2c-ethip4\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ndrdisc --title 64B-4t4c-ethip4\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ndrdisc --title 78B-1t1c-ethip6\*-ndrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ndrdisc --title 78B-2t2c-ethip6\*-ndrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ndrdisc --title 78B-4t4c-ethip6\*-ndrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-ndrdisc --title 64B-1t1c-\*vhost\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-ndrdisc --title 64B-2t2c-\*vhost\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-ndrdisc --title 64B-4t4c-\*vhost\*-ndrdisc --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "VHOST")]' --lower 0 --upper 8000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-eth-l2-pdrdisc --title 64B-1t1c-eth-l2\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-eth-l2-pdrdisc --title 64B-2t2c-eth-l2\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 26000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-eth-l2-pdrdisc --title 64B-4t4c-eth-l2\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --lower 0 --upper 36000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-pdrdisc --title 64B-1t1c-ethip4-ip4\*-pdrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP4FWD")]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-pdrdisc --title 64B-2t2c-ethip4-ip4\*-pdrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP4FWD")]'
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-pdrdisc --title 64B-4t4c-ethip4-ip4\*-pdrdisc --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP4FWD")]'

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-pdrdisc --title 78B-1t1c-ethip6-ip6\*-pdrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP6FWD")]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-pdrdisc --title 78B-2t2c-ethip6-ip6\*-pdrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP6FWD")]'
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-pdrdisc --title 78B-4t4c-ethip6-ip6\*-pdrdisc --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "PDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP6FWD")]'

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-pdrdisc --title 64B-1t1c-ethip4\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-pdrdisc --title 64B-2t2c-ethip4\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 0 --upper 16000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-pdrdisc --title 64B-4t4c-ethip4\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-pdrdisc --title 78B-1t1c-ethip6\*-pdrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-pdrdisc --title 78B-2t2c-ethip6\*-pdrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-pdrdisc --title 78B-4t4c-ethip6\*-pdrdisc --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "PDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-pdrdisc --title 64B-1t1c-\*vhost\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "PDRDISC") and contains(@tags, "1T1C") and contains(@tags, "VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-pdrdisc --title 64B-2t2c-\*vhost\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "PDRDISC") and contains(@tags, "2T2C") and contains(@tags, "VHOST")]' --lower 2000000 --upper 10000000
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-pdrdisc --title 64B-4t4c-\*vhost\*-pdrdisc --xpath '//*[@framesize="64B" and contains(@tags, "PDRDISC") and contains(@tags, "4T4C") and contains(@tags, "VHOST")]' --lower 2000000 --upper 10000000

# Plot latency

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-eth-l2-ndrdisc-lat --title 64B-1t1c-eth-l2\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-eth-l2-ndrdisc-lat --title 64B-2t2c-eth-l2\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-eth-l2-ndrdisc-lat --title 64B-4t4c-eth-l2\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --latency lat_50

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ip4-ndrdisc-lat --title 64B-1t1c-ethip4-ip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP4FWD")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ip4-ndrdisc-lat --title 64B-2t2c-ethip4-ip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP4FWD")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ip4-ndrdisc-lat --title 64B-4t4c-ethip4-ip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP4FWD")]' --latency lat_50

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ip6-ndrdisc-lat --title 78B-1t1c-ethip6-ip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IP6FWD")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ip6-ndrdisc-lat --title 78B-2t2c-ethip6-ip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IP6FWD")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ip6-ndrdisc-lat --title 78B-4t4c-ethip6-ip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and (contains(@tags, "BASE") or contains(@tags, "SCALE") or contains(@tags, "FEATURE")) and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "IP6FWD")]' --latency lat_50

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-ethip4-ndrdisc-lat --title 64B-1t1c-ethip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-ethip4-ndrdisc-lat --title 64B-2t2c-ethip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-ethip4-ndrdisc-lat --title 64B-4t4c-ethip4\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-1t1c-ethip6-ndrdisc-lat --title 78B-1t1c-ethip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-2t2c-ethip6-ndrdisc-lat --title 78B-2t2c-ethip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/78B-4t4c-ethip6-ndrdisc-lat --title 78B-4t4c-ethip6\*-ndrdisc-lat --xpath '//*[@framesize="78B" and contains(@tags, "ENCAP") and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and (contains(@tags, "VXLAN") or contains(@tags, "VXLANGPE") or contains(@tags, "LISP") or contains(@tags, "LISPGPE") or contains(@tags, "GRE"))]' --latency lat_50

python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-1t1c-vhost-ndrdisc-lat --title 64B-1t1c-\*vhost\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "VHOST")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-2t2c-vhost-ndrdisc-lat --title 64B-2t2c-\*vhost\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "VHOST")]' --latency lat_50
python run_plot.py --input ${PLOT_DIR} --output ${BUILD_DIR}/_static/64B-4t4c-vhost-ndrdisc-lat --title 64B-4t4c-\*vhost\*-ndrdisc-lat --xpath '//*[@framesize="64B" and contains(@tags, "NDRDISC") and contains(@tags, "4T4C") and contains(@tags, "VHOST")]' --latency lat_50

echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}

