#/bin/bash

for i in `seq 100` ; do
    DATE=`date +%F-%H-%M-%S`

    pybot -L TRACE -W 136 -v TOPOLOGY_PATH:/home/cisco/csit/topologies/enabled/3_node_VIRL_topo.yaml --exitonfailure --suite tests.func --include vm_envAND3_node_single_link_topo --include vm_envAND3_node_double_link_topo --exclude PERFTEST --noncritical EXPECTED_FAILING --output log_func_test_set1 tests/

    mv log.html log.run$i.$DATE.html
    mv report.html report.run$i.$DATE.html
done

