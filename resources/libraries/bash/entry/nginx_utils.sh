#!/bin/bash

set -x

ROOTDIR=/tmp/openvpp-testing
VSAP_DIR=${ROOTDIR}/tests/vsap
VSAP_CONFIG_DIR=/usr/local/nginx/conf


# RPS or CPS.
RPS_CPS=$2

# Nginx process number.
CORE_NUM=$3


# Set nginx config.
function func_set_nginx_conf() {
    if [ ${RPS_CPS} == "cps" ]; then
        sed -i 's|keepalive_timeout 300s|keepalive_timeout 0s|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    fi
    if [ ${CORE_NUM} -eq 1 ]; then
        sed -i 's|#worker_processes 1|worker_processes 1|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    elif [ ${CORE_NUM} -eq 2 ]; then
        sed -i 's|#worker_processes 2|worker_processes 2|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    elif [ ${CORE_NUM} -eq 4 ]; then
        sed -i 's|#worker_processes 4|worker_processes 4|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    fi
}


# Set library path.
function func_export_lib_path() {
    if [ ! -f /etc/ld.so.conf.d/openssl3.conf ]; then
        echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl3.conf
        ldconfig
    fi
}

# Setting restore.
function func_clean_export() {
    if [ -f /etc/ld.so.conf.d/openssl3.conf ]; then
        rm /etc/ld.so.conf.d/openssl3.conf
        ldconfig
    fi
}


# Vcl nginx daemon start.
function func_run_vcl_nginx() {
    killall -v -s 9 nginx
    cp ${VSAP_CONFIG_DIR}/nginx.conf ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    func_set_nginx_conf
    pushd ${VSAP_DIR}
    echo ${VSAP_CONFIG_DIR}
    export VCL_CONFIG=${VSAP_CONFIG_DIR}/vcl.conf
    export NGXVCL_TLS_ON=1
    export NGXVCL_TLS_CERT=${VSAP_CONFIG_DIR}/tls-test-cert
    export NGXVCL_TLS_KEY=${VSAP_CONFIG_DIR}/tls-test-key
    /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    sleep 2
    popd
}

# Ldp nginx daemon start.
function func_run_ldp_nginx() {
    cp ${VSAP_CONFIG_DIR}/nginx.conf ${VSAP_CONFIG_DIR}/nginx-tmp.conf
    func_set_nginx_conf
    killall -v -s 9 nginx
    pushd ${VSAP_DIR}
    export VCL_CONFIG=${VSAP_CONFIG_DIR}/vcl.conf
    export LDP_TRANSPARENT_TLS=1
    export LDP_TLS_CERT_FILE=${VSAP_CONFIG_DIR}/tls-test-cert
    export LDP_TLS_KEY_FILE=${VSAP_CONFIG_DIR}/tls-test-key
    LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so \
        /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    sleep 2
    popd
}

# Kill all nginx process.
function func_kill_nginx() {
    ps -A|grep vpp
    if [ $? = '0' ]; then
        vppctl show int address
        vppctl show session verbose
    fi
    killall -v -s 9 nginx
    func_clean_export
}

args=("$@")
case ${1} in
    vcl)
        func_run_vcl_nginx
        ;;
    ldp)
        func_run_ldp_nginx
        ;;
    export)
        func_export_lib_path
        ;;
    kill)
        func_kill_nginx
        ;;
esac
