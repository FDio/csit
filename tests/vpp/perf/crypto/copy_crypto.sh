#!/bin/bash

input_tunnel=1
suite_prefix="ethip4ipsec"
prefix="10ge2p1x710-${suite_prefix}"
output_prefix="${prefix}"
output_prefix="2n1l-${prefix}"
directions="-udir"
directions=""

#2n1l-10ge2p1x710-ethip4ipsec1tnlsw-ip4base-int-aes128cbc-hmac512sha-udir-ndrpdr.robot
mid="-ip4base-int"
file_suffix="-ndrpdr.robot"
tunnel_str="tnlsw"
tunnels="10000 1000 4 20000 40000 400 40 5000 60000"

#2n1l-10ge2p1x710-ethip4ipsec1tnlsw-1atnl-ip4base-int-aes128cbc-hmac512sha-udir-reconf.robot
mid="-1atnl-ip4base-int"
file_suffix="-reconf.robot"
tunnel_str="tnlsw"
tunnels="10000 1000 4 20000 40000 400 40 5000 60000"

#2n1l-10ge2p1x710-ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha-udir-ndrpdr.robot
mid="-scheduler-ip4base-int"
file_suffix="-ndrpdr.robot"
tunnel_str="tnlswasync"
tunnels="2 4 8"

#2n1l-10ge2p1x710-ethip4ipsec1tnlsw-ip4base-policy-aes128cbc-hmac512sha-udir-ndrpdr.robot
mid="-ip4base-policy"
file_suffix="-ndrpdr.robot"
tunnel_str="tnlsw"
tunnels="4 40 400"

#2n1l-10ge2p1x710-ethip4ipsec1spe-cache-ip4base-policy-outbound-nocrypto-ndrpdr.robot
mid="-cache-ip4base-policy-outbound-nocrypto"
file_suffix="-ndrpdr.robot"
tunnel_str="spe"
tunnels="10 100 1000"

#2n1l-10ge2p1x710-ethip4ipsec1spe-ip4base-policy-outbound-nocrypto-ndrpdr.robot
#mid="-ip4base-policy-outbound-nocrypto"
#file_suffix="-ndrpdr.robot"
#tunnel_str="spe"
#tunnels="10 100 1000"

#2n1l-10ge2p1x710-ethip4ipsec1spe-cache-ip4base-policy-inbound-nocrypto-ndrpdr.robot
mid="-cache-ip4base-policy-inbound-nocrypto"
file_suffix="-ndrpdr.robot"
tunnel_str="spe"
tunnels="10 100 1000"

#2n1l-10ge2p1x710-ethip4ipsec1spe-ip4base-policy-inbound-nocrypto-ndrpdr.robot
#mid="-ip4base-policy-inbound-nocrypto"
#file_suffix="-ndrpdr.robot"
#tunnel_str="spe"
#tunnels="10 100 1000"

input_files=$(ls ${output_prefix}${input_tunnel}${tunnel_str}${mid}*${directions}${file_suffix})

for input_file in ${input_files}
do
    #aes=$(echo ${input_file} | grep -Eo -- "-aes[^-]*")
    #hmac=$(echo ${input_file} | grep -Eo -- "-hmac[^-]*")
    #output_suffix="${tunnel_str}${mid}${aes}${hmac}${directions}"
    output_suffix="${tunnel_str}${mid}${directions}"

    for tunnel in $tunnels
    do
        target_file="${output_prefix}${tunnel}${output_suffix}${file_suffix}"
        cp ${input_file} "${target_file}"
        source_suite_name="${suite_prefix}${input_tunnel}${output_suffix}"
        target_suite_name="${suite_prefix}${tunnel}${output_suffix}"
        #sed -i "s/TNL_${input_tunnel}/TNL_${tunnel}/" ${target_file}
        sed -i "s/SPE_${input_tunnel}/SPE_${tunnel}/" ${target_file}
        sed -i "s/${source_suite_name}/${target_suite_name}/" ${target_file}
        sed -i "s/| \${n_tunnels}= | \${${input_tunnel}}/| \${n_tunnels}= | \${${tunnel}}/" ${target_file}
        sed -i "s/| \${rule_amount}= | \${${input_tunnel}}/| \${rule_amount}= | \${${tunnel}}/" ${target_file}
        sed -i "s/BASE/SCALE/" ${target_file}
    done
done
