#!/usr/bin/env bash

# Copyright (c) 2021 Intel and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -exuo pipefail

function export_vsap_vcl_conf () {
    # Export vcl conf file
    #
    # Variables read:
    # - VCL_CONF_PATH - Vcl Conf File Path
    # Functions called:
    # - die - Print to stderr and exit.+
    TEMPLATES_PATH=/tmp/openvpp-testing/resources/templates/
    VCL_CONF_PATH=${TEMPLATES_PATH}/vcl/vcl_iperf3.conf
    export VCL_CONFIG="${VCL_CONF_PATH}" || die "Export vcl conf file failed."

}

function set_ngignx_conf() {
    # Configure nginx according to different parameters.
    #
    # Variables read:
    # - ${1} - nginx work processes number.
    # - ${2} - test case rps or cps to configure nginx keepalive_time_out.
    # - ${3} - patcket  type to configure nginx listen port.

    nginx_cores=${1}
    RPS_CPS=${2}
    TLS_TCP=${3}
    NGINX_DIR=$(readlink -e "/usr/local/nginx") || {
        die "Readlink failed."
    }
    VSAP_CONFIG_DIR=${NGINX_DIR}/conf
    VSAP_NGINX_CONF=${TEMPLATES_PATH}/vsap/vsap-nginx.conf
    sudo cp ${VSAP_NGINX_CONF} ${VSAP_CONFIG_DIR}/nginx-tmp.conf \
    || die "copy vsap conf file  failed."
    nginx_cores=$(($nginx_cores*6))

    current_worker_processes=`cat ${VSAP_CONFIG_DIR}/nginx-tmp.conf \
    | grep worker_processes | awk '{print $2}'`
    current_keepalive_time_out=`cat ${VSAP_CONFIG_DIR}/nginx-tmp.conf \
    | grep keepalive_timeout | awk '{print $2}'`
    current_listen_port=`cat ${VSAP_CONFIG_DIR}/nginx-tmp.conf \
    | grep  listen | awk '{print $2}'`

    keepalive_time_out=0
    listen_port=80
    if [ ${RPS_CPS} = "cps" ]; then
        keepalive_time_out=300
    fi

    if [ ${TLS_TCP} = "tls" ]; then
        listen_port=443
    fi

    sudo sed -i "s|keepalive_timeout ${current_keepalive_time_out}}|keepalive_timeout ${keepalive_time_out}s;|" \
          ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die 'Sed failed.'

    sudo sed -i "s|worker_processes ${current_worker_processes}|worker_processes ${nginx_cores};|" \
          ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."

    sudo sed -i "s|listen ${current_listen_port}|listen ${listen_port};|" \
          ${VSAP_CONFIG_DIR}/nginx-tmp.conf || die "Sed failed."

}



function start_nginx() {
    # Configure start nginx.
    #
    # Variables read:
    # - ${@} - START_NGINX_MODE, Use the VCL LD_PRELOAD library start nginx.

    START_NGINX_MODE=${@}
    if [ ${START_NGINX_MODE} = "ldp" ]; then
        sudo LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so \
          /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    else
        sudo /usr/local/nginx/sbin/nginx -c ${VSAP_CONFIG_DIR}/nginx-tmp.conf &
    fi
    if [ $? -eq '1' ]; then
        echo "start nginx failed"
        exit 1
    fi
    sleep 1
    NGINX_CORES=`ps -ef | grep 'nginx: worker process' | grep -v grep | awk '{print $2}'`
    echo ${NGINX_CORES}
    if [ ! -n "$NGINX_CORES" ]; then
        exit 1
    fi
    sleep 1

}

function tasket_cores_to_nginx_pid() {
    # taskset CPU idle cores to nginx process.
    #
    # Variables read:
    # - ${@} - CPU_IDLE_CORES_STR,CPU idle cores.

    CPU_IDLE_CORES_STR=${@}
    core_list=(${CPU_IDLE_CORES_STR//,/ })
    i=0
    for pid in ${NGINX_CORES}
    do
      echo $i
      taskset -pc ${core_list[i]} ${pid}
      i=$[$i+1]
    done
}

