#!/bin/bash

set -x

DEBUG=0

WORKING_DIR='_tmp'
BUILD_DIR='_build'

SOURCE_DIR='../../../docs/report'

PLOT_VPP_SOURCE_DIR=${WORKING_DIR}/vpp_plot
PLOT_TESTPMD_SOURCE_DIR=${WORKING_DIR}/testpmd_plot

DTR_SOURCE_DIR=${SOURCE_DIR}/detailed_test_results
DTR_PERF_SOURCE_DIR=${DTR_SOURCE_DIR}/vpp_performance_results
DTR_TESTPMD_SOURCE_DIR=${DTR_SOURCE_DIR}/testpmd_performance_results
DTR_FUNC_SOURCE_DIR=${DTR_SOURCE_DIR}/vpp_functional_results
DTR_HONEYCOMB_SOURCE_DIR=${DTR_SOURCE_DIR}/honeycomb_functional_results

DTC_SOURCE_DIR=${SOURCE_DIR}/test_configuration
DTC_PERF_SOURCE_DIR=${DTC_SOURCE_DIR}/vpp_performance_configuration
DTC_FUNC_SOURCE_DIR=${DTC_SOURCE_DIR}/vpp_functional_configuration

DTO_SOURCE_DIR=${SOURCE_DIR}/test_operational_data
DTO_PERF_SOURCE_OPER_DIR=${DTO_SOURCE_DIR}/vpp_performance_operational_data

STATIC_DIR="${BUILD_DIR}/_static"
STATIC_DIR_VPP="${STATIC_DIR}/vpp"
STATIC_DIR_TESTPMD="${STATIC_DIR}/testpmd"
STATIC_DIR_ARCH="${STATIC_DIR}/archive"
CSS_PATCH_FILE="${STATIC_DIR}/theme_overrides.css"
JEN_URL='https://jenkins.fd.io/view/csit/job'

sudo apt-get -y update
sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
    zlib1g-dev unzip

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

# Download raw outputs for plots
echo Downloading raw outputs for plots ...
mkdir -p ${STATIC_DIR_VPP}
mkdir -p ${STATIC_DIR_TESTPMD}
mkdir -p ${STATIC_DIR_ARCH}
mkdir -p ${PLOT_VPP_SOURCE_DIR}
mkdir -p ${PLOT_TESTPMD_SOURCE_DIR}

### VPP PERFORMANCE SOURCE DATA

JEN_FILE_PERF='output_perf_data.xml'
JEN_JOB='csit-vpp-perf-1704-all'
JEN_BUILD=(6 7 8 9 10)

for i in "${JEN_BUILD[@]}"; do
    curl --fail -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/${JEN_FILE_PERF} \
        -o ${PLOT_VPP_SOURCE_DIR}/${JEN_JOB}-${i}.xml
    if [[ ${DEBUG} -eq 1 ]] ;
    then
        cp ./${JEN_JOB}-${JEN_BUILD[-1]}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD[-1]}.zip
    else
        curl --fail -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip \
            -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
    fi
done

unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-10.zip -d ${WORKING_DIR}/
# L2 Ethernet Switching
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_l2.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndr" \
    --title "L2 Ethernet Switching"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_l2.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndr" \
    --title "L2 Ethernet Switching"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_l2.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndr" \
    --title "L2 Ethernet Switching"
# IPv4 Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_ipv4.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+ethip4-ip4[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv4 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_ipv4.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+ethip4-ip4[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv4 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_ipv4.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+ethip4-ip4[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv4 Routed-Forwarding"
# IPv6 Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_ipv6.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+ethip6-ip6[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv6 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_ipv6.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+ethip6-ip6[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv6 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_ipv6.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+ethip6-ip6[a-z0-9]+-[a-z-]*ndr" \
    --title "IPv6 Routed-Forwarding"
# IPv4 Overlay Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_ipv4o.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+ethip4[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv4 Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_ipv4o.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+ethip4[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv4 Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_ipv4o.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+ethip4[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv4 Overlay Tunnels"
# IPv6 Overlay Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_ipv6o.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+ethip6[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv6 Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_ipv6o.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+ethip6[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv6 Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_ipv6o.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+ethip6[a-z0-9]+-[a-z0-9]*-ndr" \
    --title "IPv6 Overlay Tunnels"
# VM Vhost Connections
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_vhost.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+vhost.*" \
    --title "VM Vhost Connections"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_vhost.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+vhost.*" \
    --title "VM Vhost Connections"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_vhost.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+vhost.*" \
    --title "VM Vhost Connections"
# IPSec Crypto HW: IP4 Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_PERF_SOURCE_DIR}/vpp_performance_results_ipsec.rst \
    --formatting rst --start 3 --level 2 \
    --regex ".+ipsec.*" \
    --title "IPSec Crypto HW: IP4 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_PERF_SOURCE_DIR}/vpp_performance_configuration_ipsec.rst \
    --data "VAT_H" -f "rst" --start 3 --level 2 \
    --regex ".+ipsec.*" \
    --title "IPSec Crypto HW: IP4 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    -o ${DTO_PERF_SOURCE_OPER_DIR}/vpp_performance_operational_data_ipsec.rst \
    --data "SH_RUN" -f "rst" --start 3 --level 2 \
    --regex ".+ipsec.*" \
    --title "IPSec Crypto HW: IP4 Routed-Forwarding"
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTR_PERF_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTR_PERF_SOURCE_DIR}/index.rst
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTC_PERF_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTC_PERF_SOURCE_DIR}/index.rst
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTO_PERF_SOURCE_OPER_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTO_PERF_SOURCE_OPER_DIR}/index.rst

### DPDK PERFORMANCE SOURCE DATA

JEN_JOB='csit-dpdk-perf-1704-all'
JEN_BUILD=(1 2 3 4 5)

for i in "${JEN_BUILD[@]}"; do
    curl --fail -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/${JEN_FILE_PERF} \
        -o ${PLOT_TESTPMD_SOURCE_DIR}/${JEN_JOB}-${i}.xml
    if [[ ${DEBUG} -eq 1 ]] ;
    then
        cp ./${JEN_JOB}-${JEN_BUILD[-1]}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD[-1]}.zip
    else
        curl --fail -fs ${JEN_URL}/${JEN_JOB}/${i}/artifact/\*zip\*/archive.zip \
            -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${i}.zip
    fi
done

unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD[-1]}.zip -d ${WORKING_DIR}/
# Testpmd Performance Results
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_TESTPMD_SOURCE_DIR}/testpmd_performance_results.rst \
    --formatting rst --start 3 --level 2
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTR_TESTPMD_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD[-1]}@g" \
    ${DTR_TESTPMD_SOURCE_DIR}/index.rst

### FUNCTIONAL SOURCE DATA

JEN_JOB='csit-vpp-functional-1704-ubuntu1604-virl'
JEN_BUILD=71

if [[ ${DEBUG} -eq 1 ]] ;
then
    cp ./${JEN_JOB}-${JEN_BUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
else
    curl -fs ${JEN_URL}/${JEN_JOB}/${JEN_BUILD}/artifact/\*zip\*/archive.zip \
        -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
fi

unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip -d ${WORKING_DIR}/
# Cop Address Security
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_cop.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+cop.*" \
    --title "Cop Address Security"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_cop.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+cop.*" \
    --title "Cop Address Security"
# DHCP Client and proxy
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_dhcp.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+dhcp.*" \
    --title "DHCP - Client and Proxy"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_dhcp.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+dhcp.*" \
    --title "DHCP - Client and Proxy"
# GRE Overlay Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_gre.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ethip4gre.*" \
    --title "GRE Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_gre.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ethip4gre.*" \
    --title "GRE Overlay Tunnels"
# iACL Security
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_iacl.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+iacl.*" \
    --title "iACL Security"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_iacl.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+iacl.*" \
    --title "iACL Security"
# IPSec - Tunnels and Transport
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_ipsec.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ipsec(tnl|tpt)+-.*" \
    --title "IPSec - Tunnels and Transport"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_ipsec.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ipsec(tnl|tpt)+-.*" \
    --title "IPSec - Tunnels and Transport"
# IPv4 Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_ipv4.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ethip4-ip4base-(func|ip4ecmp\-func|ip4proxyarp\-func|ip4arp\-func)+" \
    --title "IPv4 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_ipv4.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ethip4-ip4base-(func|ip4ecmp\-func|ip4proxyarp\-func|ip4arp\-func)+" \
    --title "IPv4 Routed-Forwarding"
# IPv6 Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_ipv6.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ethip6-ip6base-(func|ip6ecmp\-func|ip6ra\-func)+" \
    --title "IPv6 Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_ipv6.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ethip6-ip6base-(func|ip6ecmp\-func|ip6ra\-func)+" \
    --title "IPv6 Routed-Forwarding"
# L2BD Ethernet Switching
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_SOURCE_DIR}/vpp_functional_results/vpp_functional_results_l2bd.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+eth-l2bdbasemac(lrn|stc)+-(func|eth\-2vhost|l2shg\-func).*" \
    --title "L2BD Ethernet Switching"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_l2bd.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+eth-l2bdbasemac(lrn|stc)+-(func|eth\-2vhost|l2shg\-func).*" \
    --title "L2BD Ethernet Switching"
# L2XC Ethernet Switching
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_l2xc.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+eth-l2xcbase-(eth|func).*" \
    --title "L2XC Ethernet Switching"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_l2xc.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+eth-l2xcbase-(eth|func).*" \
    --title "L2XC Ethernet Switching"
# LISP Overlay Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_lisp.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+lisp.*" \
    --title "LISP Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_lisp.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+lisp.*" \
    --title "LISP Overlay Tunnels"
# QoS Policer Metering
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_policer.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ipolicemark.*" \
    --title "QoS Policer Metering"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_policer.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ipolicemark.*" \
    --title "QoS Policer Metering"
# RPF Source Security
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_rpf.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+rpf.*" \
    --title "RPF Source Security"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_rpf.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+rpf.*" \
    --title "RPF Source Security"
# Softwire Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_softwire.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+swire.*" \
    --title "Softwire Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_softwire.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+swire.*" \
    --title "Softwire Tunnels"
# Tap Interface
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_tap.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+tap.*" \
    --title "Tap Interface"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_tap.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+tap.*" \
    --title "Tap Interface"
# Telemetry - IPFIX and SPAN
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_telemetry.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+(ipfix|spanrx).*" \
    --title "Telemetry - IPFIX and SPAN"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_telemetry.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+(ipfix|spanrx).*" \
    --title "Telemetry - IPFIX and SPAN"
# VLAN Tag Translation
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_vlan.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+(dot1q\-|dot1ad\-).*" \
    --title "VLAN Tag Translation"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_vlan.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+(dot1q\-|dot1ad\-).*" \
    --title "VLAN Tag Translation"
# VRF Routed-Forwarding
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_vrf.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+ethip(4|6)+-ip(4|6)+basevrf.*" \
    --title "VRF Routed-Forwarding"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_vrf.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+ethip(4|6)+-ip(4|6)+basevrf.*" \
    --title "VRF Routed-Forwarding"
# VXLAN Overlay Tunnels
python run_robot_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTR_FUNC_SOURCE_DIR}/vpp_functional_results_vxlan.rst \
    --formatting rst --start 4 --level 2 \
    --regex ".+(ip4vxlan|ip6vxlan).*" \
    --title "VXLAN Overlay Tunnels"
python run_robot_teardown_data.py -i ${WORKING_DIR}/archive/output.xml \
    --output ${DTC_FUNC_SOURCE_DIR}/vpp_functional_configuration_vxlan.rst \
    --data "VAT_H" -f "rst" --start 4 --level 2 \
    --regex ".+(ip4vxlan|ip6vxlan).*" \
    --title "VXLAN Overlay Tunnels"
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTR_FUNC_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTR_FUNC_SOURCE_DIR}/index.rst
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTC_FUNC_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTC_FUNC_SOURCE_DIR}/index.rst

### HONEYCOMB SOURCE DATA

JEN_URL='https://jenkins.fd.io/view/hc2vpp/job'
JEN_JOB='hc2vpp-csit-integration-1704-ubuntu1604'
JEN_BUILD=41

if [[ ${DEBUG} -eq 1 ]] ;
then
    cp ./${JEN_JOB}-${JEN_BUILD}.zip ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
else
    curl -fs ${JEN_URL}/${JEN_JOB}/${JEN_BUILD}/artifact/\*zip\*/archive.zip \
        -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip
fi

unzip -o ${STATIC_DIR_ARCH}/${JEN_JOB}-${JEN_BUILD}.zip -d ${WORKING_DIR}/
python run_robot_data.py -i ${WORKING_DIR}/archive/csit/output.xml \
    --output ${DTR_HONEYCOMB_SOURCE_DIR}/honeycomb_functional_results.rst \
    --formatting rst --start 3 --level 2
sed -i -e "s@###JOB###@${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTR_HONEYCOMB_SOURCE_DIR}/index.rst
sed -i -e "s@###LINK###@${JEN_URL}\/${JEN_JOB}\/${JEN_BUILD}@g" \
    ${DTR_HONEYCOMB_SOURCE_DIR}/index.rst

# Delete temporary json files
find ${SOURCE_DIR} -name "*.json" -type f -delete

# Generate the documentation:

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

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-ndrdisc \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-ndrdisc \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-ndrdisc \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-ndrdisc \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-pdrdisc \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-pdrdisc \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-pdrdisc \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-pdrdisc \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*pdrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-pdrdisc \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-pdrdisc \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-pdrdisc \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-pdrdisc \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-pdrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-pdrdisc \
    --title "64B-1t1c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"1T1C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST")]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-pdrdisc \
    --title "64B-2t2c-.*vhost.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"PDRDISC") and contains(@tags,"2T2C") and not(contains(@tags,"NDRDISC")) and contains(@tags,"VHOST")]'

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-pdrdisc \
    --title "64B-1t1c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-pdrdisc \
    --title "64B-2t2c-.*ipsec.*-pdrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]'

python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-ndrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-ndrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-pdrdisc \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'
python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-pdrdisc \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-pdrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"PDRDISC") and not(contains(@tags,"NDRDISC")) and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]'

# Plot latency

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-l2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-l2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4-ip4[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="64B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP4FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6-ip6[a-z0-9]+-[a-z-]*ndrdisc" \
    --xpath '//*[@framesize="78B" and (contains(@tags,"BASE") or contains(@tags,"SCALE") or contains(@tags,"FEATURE")) and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"IP6FWD") and not(contains(@tags,"IPSEC")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ethip4-ndrdisc-lat50 \
    --title "64B-1t1c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ethip4-ndrdisc-lat50 \
    --title "64B-2t2c-ethip4[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-1t1c-ethip6-ndrdisc-lat50 \
    --title "78B-1t1c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/78B-2t2c-ethip6-ndrdisc-lat50 \
    --title "78B-2t2c-ethip6[a-z0-9]+-[a-z0-9]*-ndrdisc" \
    --xpath '//*[@framesize="78B" and contains(@tags,"ENCAP") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"VXLAN") or contains(@tags,"VXLANGPE") or contains(@tags,"LISP") or contains(@tags,"LISPGPE") or contains(@tags,"GRE")) and not(contains(@tags,"VHOST"))]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-vhost-ndrdisc-lat50 \
    --title "64B-1t1c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and contains(@tags,"VHOST")]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-vhost-ndrdisc-lat50 \
    --title "64B-2t2c-.*vhost.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and contains(@tags,"VHOST")]' --latency lat_50

python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-1t1c-ipsechw-ndrdisc-lat50 \
    --title "64B-1t1c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "1T1C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50
python run_plot.py --input ${PLOT_VPP_SOURCE_DIR} \
    --output ${STATIC_DIR_VPP}/64B-2t2c-ipsechw-ndrdisc-lat50 \
    --title "64B-2t2c-.*ipsec.*-ndrdisc" \
    --xpath '//*[@framesize="64B" and not(contains(@tags, "VHOST")) and contains(@tags, "IP4FWD") and contains(@tags, "NDRDISC") and contains(@tags, "2T2C") and contains(@tags, "IPSECHW") and (contains(@tags, "IPSECTRAN") or contains(@tags, "IPSECTUN"))]' --latency lat_50

python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-1t1c-l2-ndrdisc-lat50 \
    --title "64B-1t1c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"1T1C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50
python run_plot.py --input ${PLOT_TESTPMD_SOURCE_DIR} \
    --output ${STATIC_DIR_TESTPMD}/64B-2t2c-l2-ndrdisc-lat50 \
    --title "64B-2t2c-(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-ndrdisc" \
    --xpath '//*[@framesize="64B" and contains(@tags,"BASE") and contains(@tags,"NDRDISC") and contains(@tags,"2T2C") and (contains(@tags,"L2BDMACSTAT") or contains(@tags,"L2BDMACLRN") or contains(@tags,"L2XCFWD")) and not(contains(@tags,"VHOST"))]' --latency lat_50

# Create archive
echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}
