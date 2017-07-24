#!/bin/bash

set -x

# Build locally without jenkins integrations
DEBUG=0

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load configuration
source ${SCRIPT_DIR}/run_report.cfg

# Install system dependencies
sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
    zlib1g-dev unzip

# Clean-up when finished
trap 'rm -rf ${DIR[WORKING]}; exit' EXIT
trap 'rm -rf ${DIR[WORKING]}; exit' ERR

# Remove the old build
rm -rf ${DIR[BUILD]} || true
rm -rf ${DIR[WORKING]} || true

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv ${DIR[WORKING]}/env
. ${DIR[WORKING]}/env/bin/activate

# Install python dependencies:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

# Download raw outputs for plots
echo Downloading raw outputs for plots ...
mkdir -p ${DIR[STATIC,VPP]}
mkdir -p ${DIR[STATIC,DPDK]}
mkdir -p ${DIR[STATIC,ARCH]}
mkdir -p ${DIR[STATIC,TREND]}
mkdir -p ${DIR[PLOT,VPP]}
mkdir -p ${DIR[PLOT,DPDK]}

### VPP PERFORMANCE SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[PERF,VPP]}-${JOB[PERF,VPP,FBLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[PERF,VPP]}-${JOB[PERF,VPP,FBLD]}.zip
#fi

blds=${JOB[PERF,VPP,BLD]}
for i in ${blds[@]}; do
    curl --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,VPP]}/${i}/robot/report/output_perf_data.xml \
        --output ${DIR[PLOT,VPP]}/${JOB[PERF,VPP]}-${i}.xml
    #curl --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,VPP]}/${i}/robot/report/output_perf_data.json \
    #    --output ${DIR[PLOT,VPP]}/${JOB[PERF,VPP]}-${i}.json
    if [[ ${DEBUG} -eq 0 ]] ;
    then
        curl --fail --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,VPP]}/${i}/robot/report/\*zip\*/robot-plugin.zip \
            --output ${DIR[STATIC,ARCH]}/${JOB[PERF,VPP]}-${i}.zip
    fi
done
# Archive trending
cp ${DIR[PLOT,VPP]}/* ${DIR[STATIC,TREND]}
blds=${JOB[1704,VPP,BLD]}
for i in ${blds[@]}; do
    curl --silent ${URL[JENKINS,CSIT]}/${JOB[1704,PERF,VPP]}/${i}/robot/report/output_perf_data.xml \
        --output ${DIR[STATIC,TREND]}/${JOB[1704,PERF,VPP]}-${i}.xml
done

### DPDK PERFORMANCE SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[PERF,DPDK]}-${JOB[PERF,DPDK,FBLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[PERF,DPDK]}-${JOB[PERF,DPDK,FBLD]}.zip
#fi

blds=${JOB[PERF,DPDK,BLD]}
for i in ${blds[@]}; do
    curl --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,DPDK]}/${i}/robot/report/output_perf_data.xml \
        --output ${DIR[PLOT,DPDK]}/${JOB[PERF,DPDK]}-${i}.xml
    #curl --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,DPDK]}/${i}/robot/report/output_perf_data.json \
    #    --output ${DIR[PLOT,DPDK]}/${JOB[PERF,DPDK]}-${i}.json
    if [[ ${DEBUG} -eq 0 ]] ;
    then
        curl --fail --silent ${URL[JENKINS,CSIT]}/${JOB[PERF,DPDK]}/${i}/robot/report/\*zip\*/robot-plugin.zip \
            --output ${DIR[STATIC,ARCH]}/${JOB[PERF,DPDK]}-${i}.zip
    fi
done
cp ${DIR[PLOT,DPDK]}/* ${DIR[STATIC,TREND]}

### FUNCTIONAL SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[FUNC,VPP]}-${JOB[FUNC,VPP,BLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[FUNC,VPP]}-${JOB[FUNC,VPP,BLD]}.zip
#fi

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${URL[JENKINS,CSIT]}/${JOB[FUNC,VPP]}/${JOB[FUNC,VPP,BLD]}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${DIR[STATIC,ARCH]}/${JOB[FUNC,VPP]}-${JOB[FUNC,VPP,BLD]}.zip
fi

### HONEYCOMB FUNCTIONAL SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[FUNC,HC]}-${JOB[FUNC,HC,BLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[FUNC,HC]}-${JOB[FUNC,HC,BLD]}.zip
#fi

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${URL[JENKINS,HC]}/${JOB[FUNC,HC]}/${JOB[FUNC,HC,BLD]}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${DIR[STATIC,ARCH]}/${JOB[FUNC,HC]}-${JOB[FUNC,HC,BLD]}.zip
fi

### HONEYCOMB PERFORMANCE SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[PERF,HC]}-${JOB[PERF,HC,BLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[PERF,HC]}-${JOB[PERF,HC,BLD]}.zip
#fi

if [[ ${DEBUG} -eq 0 ]] ;
then
    blds=${JOB[PERF,HC,BLD]}
    for i in ${blds[@]}; do
        curl --silent ${URL[JENKINS,HC]}/${JOB[PERF,HC]}/${JOB[PERF,HC,BLD]}/robot/report/\*zip\*/robot-plugin.zip \
            --output ${DIR[STATIC,ARCH]}/${JOB[PERF,HC]}-${JOB[PERF,HC,BLD]}.zip
done
fi

### NSH_SFC SOURCE DATA

#if [[ ${DEBUG} -eq 1 ]] ;
#    cp ./${JOB[FUNC,NSH]}-${JOB[FUNC,NSH,BLD]}.zip ${DIR[STATIC,ARCH]}/${JOB[FUNC,NSH]}-${JOB[FUNC,NSH,BLD]}.zip
#fi

if [[ ${DEBUG} -eq 0 ]] ;
then
    curl --fail --silent ${URL[JENKINS,CSIT]}/${JOB[FUNC,NSH]}/${JOB[FUNC,NSH,BLD]}/robot/report/\*zip\*/robot-plugin.zip \
        --output ${DIR[STATIC,ARCH]}/${JOB[FUNC,NSH]}-${JOB[FUNC,NSH,BLD]}.zip
fi

# Data post processing

if [[ ${DEBUG} -eq 0 ]] ;
then
    # VPP PERF
    unzip -o ${DIR[STATIC,ARCH]}/${JOB[PERF,VPP]}-${JOB[PERF,VPP,FBLD]}.zip -d ${DIR[WORKING]}/
    python run_robot_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTR,PERF,VPP]}/vpp_performance_results.rst \
        --formatting rst --start 4 --level 2
    python run_robot_teardown_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTC,PERF,VPP]}/vpp_performance_configuration.rst \
        --data "VAT_H" --formatting rst --start 4 --level 2
    python run_robot_teardown_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTO,PERF,VPP]}/vpp_performance_operational_data.rst \
        --data "SH_RUN" --formatting rst --start 4 --level 2

    blds=${JOB[PERF,VPP,BLD]}
    for i in ${blds[@]}; do
        unzip -o ${DIR[STATIC,ARCH]}/${JOB[PERF,VPP]}-${i}.zip -d ${DIR[WORKING]}/
        ./run_robot_json_data.py \
            --input ${DIR[WORKING]}/output.xml \
            --output ${DIR[DTR,PERF,VPP,IMPRV]}/${JOB[PERF,VPP]}-${i}.json \
            --vdevice ${i}
    done

    # DPDK PERF
    unzip -o ${DIR[STATIC,ARCH]}/${JOB[PERF,DPDK]}-${JOB[PERF,DPDK,FBLD]}.zip -d ${DIR[WORKING]}/
    python run_robot_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTR,PERF,DPDK]}/dpdk_performance_results.rst \
        --formatting rst --start 4 --level 2

    # VPP FUNC
    unzip -o ${DIR[STATIC,ARCH]}/${JOB[FUNC,VPP]}-${JOB[FUNC,VPP,BLD]}.zip -d ${DIR[WORKING]}/
    python run_robot_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTR,FUNC,VPP]}/vpp_functional_results.rst \
        --formatting rst --start 5 --level 2
    python run_robot_teardown_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTC,FUNC,VPP]}/vpp_functional_configuration.rst \
        --data "VAT_H" --formatting rst --start 5 --level 2

    # HC FUNC
    unzip -o ${DIR[STATIC,ARCH]}/${JOB[FUNC,HC]}-${JOB[FUNC,HC,BLD]}.zip -d ${DIR[WORKING]}/
    python run_robot_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTR,FUNC,HC]}/honeycomb_functional_results.rst \
        --formatting rst --start 5 --level 2

    # NSHSFC FUNC
    unzip -o ${DIR[STATIC,ARCH]}/${JOB[FUNC,NSH]}-${JOB[FUNC,NSH,BLD]}.zip -d ${DIR[WORKING]}/
    python run_robot_data.py -i ${DIR[WORKING]}/robot-plugin/output.xml \
        --output ${DIR[DTR,FUNC,NSHSFC]}/nshsfc_functional_results.rst \
        --formatting rst --start 5 --level 2
fi

# Generate tables for performance improvements
if [[ ${DEBUG} -eq 0 ]] ;
then
    python run_improvments_tables.py \
        --input ${DIR[DTR,PERF,VPP,IMPRV]} \
        --output ${DIR[DTR,PERF,VPP,IMPRV]}
fi

# Delete temporary json files
find ${DIR[RST]} -name "*.json" -type f -delete

# Generate the documentation
DATE=$(date -u '+%d-%b-%Y')
sphinx-build -v -c . -a -b html -E \
    -D release=$1 -D version="$1 report - $DATE" \
    ${DIR[RST]} ${DIR[BUILD]}/

# Patch the CSS for tables layout
cat - > ${DIR[CSS_PATCH_FILE]} <<"_EOF"
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

# VPP L2 sel1

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel1-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel1-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel1-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel1-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

# VPP L2 sel2

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 8000000
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 5000000 --upper 12000000

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 0 --upper 8000000
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --lower 5000000 --upper 12000000

# VPP IP4

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-ip4-ndrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-ip4-ndrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-ip4-pdrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-ip4-pdrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

# VPP IP6

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-ip6-ndrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-ip6-ndrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-ip6-pdrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-ip6-pdrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

# VPP IP4_overlay

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-ndrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-ndrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-pdrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-pdrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]'

# VPP IP6_overlay

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-ndrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-ndrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-pdrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-pdrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

# VPP VM VHOST

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel1-ndrdisc \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel1-ndrdisc \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel1-pdrdisc \
    --title "64B-1t1c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel1-pdrdisc \
    --title "64B-2t2c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]'

# VPP VM VHOST SELECTION

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel2-ndrdisc \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel2-ndrdisc \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel2-pdrdisc \
    --title "64B-1t1c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel2-pdrdisc \
    --title "64B-2t2c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]'

# VPP CRYPTO

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ipsechw-ndrdisc \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ipsechw-ndrdisc \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ipsechw-pdrdisc \
    --title "64B-1t1c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ipsechw-pdrdisc \
    --title "64B-2t2c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

# DPDK

python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-l2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-l2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-ipv4-ndrdisc \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' \
    --lower 2000000 --upper 12000000
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-ipv4-ndrdisc \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' \
    --lower 2000000 --upper 12000000

python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-l2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-l2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-ipv4-pdrdisc \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' \
    --lower 20000000 --upper 30000000
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-ipv4-pdrdisc \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' \
    --lower 20000000 --upper 30000000

# Plot latency

# VPP L2 sel1

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel1-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel1-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP L2 sel2

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-l2-sel2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-l2-sel2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and ((contains(@tags,"FEATURE") and contains(@tags,"ACL50") and contains(@tags,"10k_FLOWS"))) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP4

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP6

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP IP4_overlay

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ethip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ethip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST")) and not(contains(@tags, "IPSECHW"))]' --latency lat_50

# VPP IP6_overlay

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-1t1c-ethip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/78B-2t2c-ethip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# VPP VM VHOST

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel1-ndrdisc-lat50 \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel1-ndrdisc-lat50 \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD"))]' --latency lat_50

# VPP VM VHOST selection

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-vhost-sel2-ndrdisc-lat50 \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-vhost-sel2-ndrdisc-lat50 \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST") and not(contains(@tags,"VXLAN")) and not(contains(@tags,"IP4FWD")) and not(contains(@tags,"DOT1Q")) and not(contains(name(), "2Vm"))]' --latency lat_50

# VPP CRYPTO

python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-1t1c-ipsechw-ndrdisc-lat50 \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,VPP]} \
    --output ${DIR[STATIC,VPP]}/64B-2t2c-ipsechw-ndrdisc-lat50 \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50

# DPDK

python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-l2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-l2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-1t1c-ipv4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD")]' --latency lat_50
python run_plot.py --input ${DIR[PLOT,DPDK]} \
    --output ${DIR[STATIC,DPDK]}/64B-2t2c-ipv4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD")]' --latency lat_50

# Create archive
echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${DIR[BUILD]}
