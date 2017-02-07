#!/bin/bash

WORKING_DIR='_tmp'
BUILD_DIR='_build'
SOURCE_DIR='../../../docs/report'
STATIC_DIR="${BUILD_DIR}/_static"
STATIC_DIR_VPP="${STATIC_DIR}/vpp"
STATIC_DIR_TESTPMD="${STATIC_DIR}/testpmd"
STATIC_DIR_ARCH="${STATIC_DIR}/archive"
CSS_PATCH_FILE="${STATIC_DIR}/theme_overrides.css"

sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential zlib1g-dev

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

DATE=$(date -u '+%d-%b-%Y')

sphinx-build -v -c . -a -b html -E -D release=$1 -D version="$1 report - $DATE" ${SOURCE_DIR} ${BUILD_DIR}/

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
mkdir -p ${STATIC_DIR_VPP}
mkdir -p ${STATIC_DIR_TESTPMD}
mkdir -p ${STATIC_DIR_ARCH}

JEN_URL='https://jenkins.fd.io/view/csit/job'
JEN_FILE_PERF='output_perf_data.xml'

JEN_JOB='csit-vpp-perf-1701-all'
JEN_BUILD=(3 4 7 8 9)

for i in "${JEN_BUILD[@]}"; do
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/${JEN_FILE_PERF} -o ${STATIC_DIR_VPP}/${JEN_JOB}-${i}.xml
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
done

JEN_JOB='csit-vpp-perf-1701-long'
JEN_BUILD=(2 4 5 6)

for i in "${JEN_BUILD[@]}"; do
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/${JEN_FILE_PERF} -o ${STATIC_DIR_VPP}/${JEN_JOB}-${i}.xml
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
done

JEN_JOB='csit-dpdk-perf-1701-all'
JEN_BUILD=(2 3)

for i in "${JEN_BUILD[@]}"; do
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/${JEN_FILE_PERF} -o ${STATIC_DIR_TESTPMD}/${JEN_JOB}-${i}.xml
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
done

JEN_JOB='csit-vpp-functional-1701-virl'
JEN_BUILD=(48)

for i in "${JEN_BUILD[@]}"; do
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
done

JEN_URL='https://jenkins.fd.io/view/hc2vpp/job'
JEN_JOB='hc2vpp-csit-integration-1701-ubuntu1404'
JEN_BUILD=(1)

for i in "${JEN_BUILD[@]}"; do
    curl -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
done


# Plot packets per second

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-l2-ndrdisc --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-ip4-ndrdisc --title "64B-4t4c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-ip6-ndrdisc --title "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-ndrdisc --title "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-ndrdisc --title "78B-4t4c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-ndrdisc --title "64B-1t1c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-ndrdisc --title "64B-2t2c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-vhost-ndrdisc --title "64B-4t4c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"VHOST")]' --lower 0 --upper 8000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-l2-pdrdisc --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-l2-pdrdisc --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-l2-pdrdisc --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-pdrdisc --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-pdrdisc --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-ip4-pdrdisc --title "64B-4t4c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-pdrdisc --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-pdrdisc --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-ip6-pdrdisc --title "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --lower 0 --upper 36000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-pdrdisc --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-pdrdisc --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 16000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-pdrdisc --title "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 20000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-pdrdisc --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-pdrdisc --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-pdrdisc --title "78B-4t4c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --lower 2000000 --upper 12000000

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-pdrdisc --title "64B-1t1c-.*vhost.*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST")]' --lower 0 --upper 8000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-pdrdisc --title "64B-2t2c-.*vhost.*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST")]' --lower 2000000 --upper 10000000
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-vhost-pdrdisc --title "64B-4t4c-.*vhost.*-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"4T4C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST")]' --lower 2000000 --upper 10000000

python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-ndrdisc --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-ndrdisc --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-4t4c-l2-ndrdisc --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000

python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-pdrdisc --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-pdrdisc --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-4t4c-l2-pdrdisc --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 26000000

# Plot latency

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc-lat50 --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc-lat50 --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-l2-ndrdisc-lat50 --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc-lat50 --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc-lat50 --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-ip4-ndrdisc-lat50 --title "64B-4t4c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP4FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc-lat50 --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc-lat50 --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-ip6-ndrdisc-lat50 --title "78B-4t4c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"IP6FWD") and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc-lat50 --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc-lat50 --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-ethip4-ndrdisc-lat50 --title "64B-4t4c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc-lat50 --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc-lat50 --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/78B-4t4c-ethip6-ndrdisc-lat50 --title "78B-4t4c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-ndrdisc-lat50 --title "64B-1t1c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-ndrdisc-lat50 --title "64B-2t2c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_VPP} --output ${STATIC_DIR_VPP}/64B-4t4c-vhost-ndrdisc-lat50 --title "64B-4t4c-.*vhost.*-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and contains(@tags,"VHOST")]' --latency lat_50

python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-ndrdisc-lat50 --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-ndrdisc-lat50 --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${STATIC_DIR_TESTPMD} --output ${STATIC_DIR_TESTPMD}/64B-4t4c-l2-ndrdisc-lat50 --title "64B-4t4c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"4T4C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# Create archive
echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}
