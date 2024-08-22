start_pattern='^  TG:'
end_pattern='^ \? \?[A-Za-z0-9]\+:'
# Remove the TG section from topology file
sed_command="/${start_pattern}/,/${end_pattern}/d"
available=$(sed "${sed_command}" "topologies/available/mrvl_testbed.yaml" \
                | grep -hoP "model: \K.*" | sort -u)
nic_tag=NIC_${available}
# replace dpdk_plugin.so with dev_octeon_plugin.so
grep -rl '| @{plugins_to_enable}= | dpdk_plugin.so' tests | xargs sed -i 's/| @{plugins_to_enable}= | dpdk_plugin.so /| @{plugins_to_enable}= | dev_octeon_plugin.so /g'
#run robot command
#robot --loglevel TRACE --variable TOPOLOGY_PATH:topologies/available/mrvl_testbed.yaml -G DOP -v nic_vfs:1 -v TEST_PLUGIN:DOP --suite 'tests.vpp.perf.ip4.2n1l-*a063-ethip4-ip4base-ndrpdr' --include ${nic_tag} ./tests
