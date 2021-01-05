#!/bin/bash

set -x

ROOTDIR=/tmp/openvpp-testing
VSAP_DIR=${ROOTDIR}/tests/vsap
VSAP_CONFIG_DIR=/usr/local/nginx/conf


# RPS or CPS.
RPS_CPS=$2

# Nginx process number.
CORE_NUM=$3

TLS_TCP=tls

if [ ! -z $4 ]; then
    if [ $4 = 'tcp' ]; then
        TLS_TCP=tcp
    fi
fi

# Set nginx config.
function func_set_nginx_conf() {
    sudo killall -v -s 9 nginx | true
    sudo cp -rf ${VSAP_CONFIG_DIR}/nginx.conf ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Copy failed."
    export VCL_CONFIG=${VSAP_CONFIG_DIR}/vcl.conf  || die "Export failed."

    if [ ${RPS_CPS} = "cps" ]; then
        sudo sed -i 's|keepalive_timeout 300s|keepalive_timeout 0s|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
    fi

    if [ ${TLS_TCP} = "tls" ]; then
        if [ ${CORE_NUM} -eq 1 ]; then
            sudo sed -i 's|#worker_processes 1|worker_processes 2|' \
                ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
        elif [ ${CORE_NUM} -eq 2 ]; then
            sudo sed -i 's|#worker_processes 2|worker_processes 4|' \
                ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
        elif [ ${CORE_NUM} -eq 4 ]; then
            sudo sed -i 's|#worker_processes 4|worker_processes 8|' \
                ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
        fi
    else
        sudo sed -i 's|#worker_processes 1|worker_processes 6|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
    fi

    if [ ${TLS_TCP} = "tcp" ]; then
        sudo sed -i 's|listen 443|listen 80|' \
            ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."
    fi
}

# Set library path.
function func_export_lib_path() {
    if [ ! -f /etc/ld.so.conf.d/openssl3.conf ]; then
        echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl3.conf
        ldconfig
    fi
}

# Vcl nginx daemon start.
function func_run_vcl_nginx() {
    func_set_nginx_conf
    pushd ${VSAP_DIR}
    if [ ${TLS_TCP} = "tls" ]; then
        export NGXVCL_TLS_ON=1
        export NGXVCL_TLS_CERT=${VSAP_CONFIG_DIR}/tls-test-cert
        export NGXVCL_TLS_KEY=${VSAP_CONFIG_DIR}/tls-test-key
    fi
    /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    sleep 2
    func_taskset_nginx
    popd
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
    sleep 2
    func_taskset_nginx
    popd
}


function func_taskset_nginx() {
    vppmain=`cat /etc/vpp/startup.conf | grep main-core | awk '{print $2}'`
    vl=`cat /etc/vpp/startup.conf | grep corelist-workers | awk '{print $2}'`
    cores=`cat /proc/cpuinfo| grep "cpu cores" | uniq | awk '{print $4}'`
    need_core_num=$[$[CORE_NUM*3]+CORE_NUM+1]

    if [ ${cores} -ge ${need_core_num} ]; then
        echo "core ok: ${cores}"
    else
        echo "core is less ${need_core_num}, exit"
        exit
    fi

    varray=(${vl//,/ })
    n=`ps -ef | grep "nginx: worker process" | grep -v grep | awk '{print $2}'`
    last_core=${varray[-1]}
    
    # offset of VPP and nginx core
    i=1
    for pid in ${n}
    do
      i=$[$i+1]
      taskset -pc $[$last_core+i] ${pid}
    done

}

# Kill all nginx process.
function func_kill_nginx() {
    ps -A|grep vpp
    if [ $? = '0' ]; then
        vppctl show int address
        vppctl show session verbose
    fi
    sudo killall -v -s 9 nginx | true
}

args=("$@")
case ${1} in
    task)
        func_taskset_nginx
	;;
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
