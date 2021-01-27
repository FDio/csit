#!/usr/bin/env bash

set -x

ROOTDIR=/tmp/openvpp-testing
VSAP_DIR=${ROOTDIR}/tests/vsap
VSAP_CONFIG_DIR=/usr/local/nginx/conf
# RPS or CPS.
RPS_CPS=$2

# Nginx process number.
CORE_NUM=$3

# Core IDLE .
CORE_IDLE_STR=$5

# Vsap Mode
TLS_TCP=$4

# Set nginx config.
function func_set_nginx_conf() {
    sudo killall -v -s 9 nginx | true
    sudo cp -rf ${VSAP_CONFIG_DIR}/nginx.conf \
        ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Copy failed."
    export VCL_CONFIG=${VSAP_CONFIG_DIR}/vcl.conf  || die "Export failed."

    if [ ${RPS_CPS} = "cps" ]; then
        sudo sed -i 's|keepalive_timeout 300s|keepalive_timeout 0s|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
    fi

    nginx_cores=$(($CORE_NUM*6))
    nginx_worker_processes=`cat ${VSAP_CONFIG_DIR}/nginx-tmp.conf \
    | grep worker_processes | awk '{print $2}'`

    sudo sed -i "s|worker_processes ${nginx_worker_processes}|worker_processes ${nginx_cores};|" \
          ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
}

# Set library path.
function func_export_lib_path() {
    if [ ! -f /etc/ld.so.conf.d/openssl3.conf ]; then
        echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl3.conf
        ldconfig
    fi
}

# Ldp nginx daemon start.
function func_run_ldp_nginx() {
    func_set_nginx_conf
    pushd ${VSAP_DIR}
    if [ ${TLS_TCP} = "tls" ]; then
        export LDP_TRANSPARENT_TLS=1
        export LDP_TLS_CERT_FILE=${VSAP_CONFIG_DIR}/tls-test-cert
        export LDP_TLS_KEY_FILE=${VSAP_CONFIG_DIR}/tls-test-key
    fi
    LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so \
        /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    sleep 1
    func_taskset_nginx
    popd
}


function func_taskset_nginx() {
    vppmain=`cat /etc/vpp/startup.conf | grep main-core | awk '{print $2}'`
    vl=`cat /etc/vpp/startup.conf | grep corelist-workers | awk '{print $2}'`
    cores=`cat /proc/cpuinfo| grep "cpu cores" | uniq | awk '{print $4}'`

    need_core_num=$[$[CORE_NUM*6]+CORE_NUM+1]
    core_list=(${CORE_IDLE_STR//,/ })
    varray=(${vl//,/ })

    if [ ${cores} -ge ${need_core_num} ]; then
        echo "core ok: ${cores}"
    else
        echo "core is less ${need_core_num}, exit"
        exit 1
    fi

    echo " core_list:  ${core_list[@]}"
    n=`ps -ef | grep "nginx: worker process" | grep -v grep | awk '{print $2}'`
    # offset of VPP and nginx core
    i=1
    for pid in ${n}
    do
      i=$[$i+1]
      taskset -pc ${core_list[i]} ${pid}
    done
    sleep 1
    vppctl show interface addr
    vppctl show session verbose
}

# Kill all nginx process.
function func_kill_nginx() {
    sudo killall -v -s 9 nginx | true
}

args=("$@")
case ${1} in
    task)
        func_taskset_nginx
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
    *)
        exit 1
esac
