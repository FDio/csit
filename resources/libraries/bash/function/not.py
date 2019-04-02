
import glob

tags_all = set([
    '100_flows', '100k_flows', '10k_flows', '10r1c', '114b', '1518b', '1c',
    '1numa', '1r10c', '1r1c', '1r2c', '1r4c', '1r6c', '1r8c', '1vm', '1vnf',
    '1vswitch', '2c', '2r1c', '2r2c', '2r4c', '2r6c', '2r8c', '2vm', '2vnf',
    '4c', '4r1c', '4r2c', '4r4c', '4vnf', '64b', '6r1c', '6r2c', '78b', '8r1c',
    '8r2c', '9000b', 'acl', 'acl1', 'acl10', 'acl50', 'acl_permit',
    'acl_permit_reflect', 'acl_stateful', 'acl_stateless', 'aes_gcm', 'base',
    'cbc_sha1', 'cfs_opt', 'chain', 'copwhlist', 'docker', 'dot1ad', 'dot1q',
    'dpdk', 'drv_avf', 'encap', 'eth', 'feature', 'fib_100k', 'fib_10k',
    'fib_1m', 'fib_200k', 'fib_20k', 'fib_2m', 'horizontal', 'hw_env', 'iacl',
    'iacldst', 'imix', 'ip4base', 'ip4fwd', 'ip4ovrlay', 'ip4unrlay', 'ip6base',
    'ip6fwd', 'ip6ovrlay', 'ip6unrlay', 'ipsec', 'ipsechw', 'ipsecint',
    'ipsecsw', 'ipsectran', 'ipsectun', 'k8s', 'l2bd_1', 'l2bd_10', 'l2bd_100',
    'l2bd_1k', 'l2bdbase', 'l2bdmaclrn', 'l2bdscale', 'l2ovrlay', 'l2patch',
    'l2xcbase', 'l2xcfwd', 'lbond', 'lbond_1l', 'lbond_2l', 'lbond_dpdk',
    'lbond_lb_l34', 'lbond_mode_lacp', 'lbond_mode_xor', 'lbond_vpp', 'lisp',
    'lispgpe', 'lxc', 'macip', 'memif', 'mrr', 'nat44', 'ndrpdr', 'nf_density',
    'nf_l3fwdip4', 'nf_vppip4', 'nic_cisco-vic-1227', 'nic_cisco-vic-1385',
    'nic_intel-x520-da2', 'nic_intel-x553', 'nic_intel-x710', 'nic_intel-xl710',
    'nic_intel-xxv710', 'oacl', 'parallel', 'pipeline', 'police_mark', 'scale',
    'sfc_controller', 'single_memif', 'src_user_1', 'src_user_10',
    'src_user_100', 'src_user_1000', 'src_user_2000', 'src_user_4000', 'srv6',
    'srv6_1sid', 'srv6_2sid_decap', 'srv6_2sid_nodecap', 'srv6_proxy',
    'srv6_proxy_dyn', 'srv6_proxy_masq', 'srv6_proxy_stat', 'tnl_1000', 'vhost',
    'vhost_1024', 'vlan_1', 'vlan_10', 'vlan_100', 'vlan_1k', 'vpp_agent',
    'vts', 'vxlan', 'vxlan_1', 'vxlan_10', 'vxlan_100', 'vxlan_1k'])

for filename_in in glob.iglob("*.nonot.txt"):
    filename_out = filename_in.replace(".nonot.", ".")
    with open(filename_in, "r") as file_in:
        lines_in = file_in.readlines()
    lines_out = list()
    for line_in in lines_in:
        line_in = line_in.strip()
        if not line_in or line_in[0] == '#':
            continue
        tags_and = set(line_in.split("AND"))
        tags_not = tags_all - tags_and
        tags_not.add("")
        line_out = "AND".join(sorted(tags_and)) + "NOT".join(sorted(tags_not))
        lines_out.append(line_out + '\n')
    with open(filename_out, "w") as file_out:
        file_out.writelines(sorted(lines_out))
