#!/bin/bash

set -x

# Build locally without jenkins integrations
DEBUG=0

# Build directories
WORKING_DIR='_tmp'
BUILD_DIR='_build'

STATIC_DIR="${BUILD_DIR}/_static"
STATIC_DIR_VPP="${STATIC_DIR}/vpp"
STATIC_DIR_DPDK="${STATIC_DIR}/dpdk"
STATIC_DIR_ARCH="${STATIC_DIR}/archive"
CSS_PATCH_FILE="${STATIC_DIR}/theme_overrides.css"

SOURCE_DIR='../../../docs/report'

PLOT_VPP_SOURCE_DIR=${WORKING_DIR}/vpp_plot
PLOT_DPDK_SOURCE_DIR=${WORKING_DIR}/dpdk_plot

DTR_SOURCE_DIR=${SOURCE_DIR}/detailed_test_results
DTR_PERF_IMPROVEMENTS=${SOURCE_DIR}/vpp_performance_tests/performance_improvements
DTR_DPDK_SOURCE_DIR=${DTR_SOURCE_DIR}/dpdk_performance_results
DTR_VPP_PERF_SOURCE_DIR=${DTR_SOURCE_DIR}/vpp_performance_results
DTR_VPP_FUNC_SOURCE_DIR=${DTR_SOURCE_DIR}/vpp_functional_results
DTR_HC_PERF_SOURCE_DIR=${DTR_SOURCE_DIR}/honeycomb_performance_results
DTR_HC_FUNC_SOURCE_DIR=${DTR_SOURCE_DIR}/honeycomb_functional_results
DTR_NSHSFC_FUNC_SOURCE_DIR=${DTR_SOURCE_DIR}/nshsfc_functional_results

DTC_SOURCE_DIR=${SOURCE_DIR}/test_configuration
DTC_VPP_PERF_SOURCE_DIR=${DTC_SOURCE_DIR}/vpp_performance_configuration
DTC_VPP_FUNC_SOURCE_DIR=${DTC_SOURCE_DIR}/vpp_functional_configuration

DTO_SOURCE_DIR=${SOURCE_DIR}/test_operational_data
DTO_VPP_PERF_SOURCE_OPER_DIR=${DTO_SOURCE_DIR}/vpp_performance_operational_data

# Jenkins links
CSIT_JEN_URL='https://jenkins.fd.io/view/csit/job'
HC_JEN_URL='https://jenkins.fd.io/view/hc2vpp/job'

sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
    zlib1g-dev unzip

# Clean-up when finished
trap 'rm -rf ${WORKING_DIR}; exit' EXIT
trap 'rm -rf ${WORKING_DIR}; exit' ERR

# Remove the old build
rm -rf ${BUILD_DIR} || true
rm -rf ${WORKING_DIR} || true

# Create working directories
mkdir ${BUILD_DIR}

# Create virtual environment
virtualenv ${WORKING_DIR}/env
. ${WORKING_DIR}/env/bin/activate

# Install Sphinx:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

# Download raw outputs for plots
echo Downloading raw outputs for plots ...
mkdir -p ${STATIC_DIR_VPP}
mkdir -p ${STATIC_DIR_DPDK}
mkdir -p ${STATIC_DIR_ARCH}
mkdir -p ${PLOT_VPP_SOURCE_DIR}
mkdir -p ${PLOT_DPDK_SOURCE_DIR}

### VPP PERFORMANCE SOURCE DATA

JEN_JOB='csit-vpp-perf-1707-all'
JEN_BUILD=(1)
JEN_FBUILD=1

for i in "${JEN_BUILD[@]}"; do
    curl --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/output_perf_data.xml \
        --output ${PLOT_VPP_SOURCE_DIR}/${JEN_JOB}-${i}.xml
    curl --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/output_perf_data.json \
        --output ${PLOT_VPP_SOURCE_DIR}/${JEN_JOB}-${i}.json
    if [[ ${DEBUG} -eq 0 ]] ;
    then
        curl --fail --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/\*zip\*/robot-plugin.zip \
            --output ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
    fi
done

if [[ ${DEBUG} -eq 0 ]] ;
then
    unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_FBUILD}.zip -d ${WORKING_DIR}/
    python run_robot_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_VPP_PERF_SOURCE_DIR}/vpp_performance_results.rst \
        --formatting rst --start 4 --level 2
    python run_robot_teardown_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTC_VPP_PERF_SOURCE_DIR}/vpp_performance_configuration.rst \
        --data "VAT_H" --formatting rst --start 4 --level 2
    python run_robot_teardown_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTO_VPP_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data.rst \
        --data "SH_RUN" --formatting rst --start 4 --level 2
#else
#    cp ./${JEN_JOB}-${JEN_FBUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_FBUILD}.zip
fi

### DPDK PERFORMANCE SOURCE DATA

JEN_JOB='csit-dpdk-perf-1707-all'
JEN_BUILD=(1 2 3 4 5 6 7 8 9 10)

for i in "${JEN_BUILD[@]}"; do
    curl --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/output_perf_data.xml \
        --output ${PLOT_DPDK_SOURCE_DIR}/${JEN_JOB}-${i}.xml
    curl --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/output_perf_data.json \
        --output ${PLOT_DPDK_SOURCE_DIR}/${JEN_JOB}-${i}.json
    if [[ ${DEBUG} -eq 0 ]] ;
    then
        curl --fail --silent ${CSIT_JEN_URL}/${JEN_JOB}/${i}/robot/report/\*zip\*/robot-plugin.zip \
            --output ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
    fi
done

if [[ ${DEBUG} -eq 0 ]] ;
then
    unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD[-1]}.zip -d ${WORKING_DIR}/
    python run_robot_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_DPDK_SOURCE_DIR}/dpdk_performance_results.rst \
        --formatting rst --start 4 --level 2
#else
#    cp ./${JEN_JOB}-${JEN_FBUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_FBUILD}.zip
fi

### FUNCTIONAL SOURCE DATA

JEN_JOB='csit-vpp-functional-1707-ubuntu1604-virl'
JEN_BUILD='lastSuccessfulBuild'

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${CSIT_JEN_URL}/${JEN_JOB}/${JEN_BUILD}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
    unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip -d ${WORKING_DIR}/
    python run_robot_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_VPP_FUNC_SOURCE_DIR}/vpp_functional_results.rst \
        --formatting rst --start 5 --level 2
    python run_robot_teardown_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_VPP_FUNC_SOURCE_DIR}/vpp_functional_configuration.rst \
        --data "VAT_H" --formatting rst --start 5 --level 2
#else
#    cp ./${JEN_JOB}-${JEN_BUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
fi

### HONEYCOMB SOURCE DATA

JEN_JOB='hc2vpp-csit-integration-1707-ubuntu1604'
JEN_BUILD='lastSuccessfulBuild'

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${HC_JEN_URL}/${JEN_JOB}/${JEN_BUILD}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
    unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip -d ${WORKING_DIR}/
    python run_robot_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_HC_FUNC_SOURCE_DIR}/honeycomb_functional_results.rst \
        --formatting rst --start 5 --level 2
#else
#    cp ./${JEN_JOB}-${JEN_BUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
fi

### NSH_SFC SOURCE DATA

JEN_JOB='csit-nsh_sfc-verify-func-1707-ubuntu1604-virl'
JEN_BUILD='lastSuccessfulBuild'

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${CSIT_JEN_URL}/${JEN_JOB}/${JEN_BUILD}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
    unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip -d ${WORKING_DIR}/
    python run_robot_data.py -i ${WORKING_DIR}/robot-plugin/output.xml \
        --output ${DTR_NSHSFC_FUNC_SOURCE_DIR}/nshsfc_functional_results.rst \
        --formatting rst --start 5 --level 2
#else
#    cp ./${JEN_JOB}-${JEN_BUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
fi

# Delete temporary json files
find ${SOURCE_DIR} -name "*.json" -type f -delete

# Generate tables for performance improvements
python run_improvments_tables.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${DTR_PERF_IMPROVEMENTS}

# Generate the documentation

DATE=$(date -u '+%d-%b-%Y')

sphinx-build -v -c . -a -b html -E \
    -D release=$1 -D version="$1 report - $DATE" \
    ${SOURCE_DIR} ${BUILD_DIR}/

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

# Plot packets per second

# VPP L2

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

# VPP IP4

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-pdrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-pdrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

# VPP IP6

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-pdrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-pdrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

# VPP IP4_overlay

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-pdrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-pdrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

# VPP IP6_overlay

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-pdrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-pdrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

# VPP VM VHOST

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel1-ndrdisc \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel1-ndrdisc \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel1-pdrdisc \
    --title "64B-1t1c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel1-pdrdisc \
    --title "64B-2t2c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]'

# VPP VM VHOST SELECTION

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel2-ndrdisc \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel2-ndrdisc \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel2-pdrdisc \
    --title "64B-1t1c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel2-pdrdisc \
    --title "64B-2t2c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'

# VPP CRYPTO

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-ndrdisc \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-ndrdisc \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-pdrdisc \
    --title "64B-1t1c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-pdrdisc \
    --title "64B-2t2c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

# DPDK

python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-l2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-l2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-ipv4-ndrdisc \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' \
    --lower 2000000 --upper 12000000
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-ipv4-ndrdisc \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' \
    --lower 2000000 --upper 12000000

python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-l2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-l2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-ipv4-pdrdisc \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' \
    --lower 20000000 --upper 30000000
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-ipv4-pdrdisc \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' \
    --lower 20000000 --upper 30000000

# Plot latency

# VPP L2

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP4

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP6

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP4_overlay

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP6_overlay

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP VM VHOST latency

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel1-ndrdisc-lat50 \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel1-ndrdisc-lat50 \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and (contains(@tags,"VXLAN") or contains(@tags,"IP4FWD") or contains(@tags,"DOT1Q"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-sel2-ndrdisc-lat50 \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-sel2-ndrdisc-lat50 \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]' --latency lat_50

# VPP CRYPTO

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-ndrdisc-lat50 \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-ndrdisc-lat50 \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50

# DPDK

python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-l2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-l2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-1t1c-ipv4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' --latency lat_50
python run_plot.py --input ${PLOT_DPDK_SOURCE_DIR} \
    --output ${STATIC_DIR_DPDK}/64B-2t2c-ipv4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' --latency lat_50

# Create archive
echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}
