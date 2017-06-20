
# Directory structure re-organization

## Table of contents

1. [The new structure](#the-new-structure)
1. [Tests](#tests)
   1. [Performance](#performance)
   1. [Functional](#functional)
1. [Keywords](#keywords)
   1. [L2 Robot keywords](#l2-robot-keywords)
   1. [L1 Python keywords](#l1-python-keywords)

## The new structure

### Tests
```
$CSIT/
    tests/
        vpp/
            func/
                l2bd/
                l2xc/
                ip4/
                ip6/
                ip4_tunnels/
                ip6_tunnels/
                vm_vhost/
                crypto/
                interfaces/
                telemetry/
                honeycomb/
            perf/
                l2/
                ip4/
                ip6/
                ip4_tunnels/
                ip6_tunnels/
                vm_vhost/
                crypto/
        dpdk/
            func/
            perf/
        nsh_sfc/
            func/
            perf/
        tldk/
            func/
            perf/
```

### Keywords
```
$CSIT/
    resources/
        libraries/
            bash/
            python/
                packages/ (dirs): feature | area
                    modules/
            robot/
                shared/
                l2/
                ip/
                overlay/
                vm/
                crypto/
                dpdk/
                nsh_sfc/
                tldk/
                honeycomb/
                performance/
                telemetry/
                features/
                fds/
```

*Notes:*
1. **l1/** - L1 will not be created, L1 KWs will be temporarily kept in L2 (their
   current place) and asap refactored using Python
1. **l2/** - Not needed if we do not have l1/


### Other resources
```
$CSIT/
    resources/
        templates/
            vat/
            honeycomb/
        test_data/
            honeycomb/
            lisp/
            softwire/
        tools/
            disk_image_builder/
            doc_gen/
            report_gen/
            scripts/
            testbed_setup/
            topology/
            trex/
            vagrant/
            virl/
        topology_schemas/
        traffic_scripts/
        traffic_profiles/
           trex/
           ixia/
```

## Tests

### Performance

#### L2 Ethernet Switching
```
ls | grep -E "(eth|dot1q|dot1ad)-(l2xcbase|l2bdbasemaclrn)-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
l2/
    10ge2p1vic1227-eth-l2bdbasemaclrn-ndrpdrdisc.robot
    10ge2p1x520-dot1ad-l2xcbase-ndrchk.robot
    10ge2p1x520-dot1ad-l2xcbase-ndrpdrdisc.robot
    10ge2p1x520-dot1q-l2xcbase-ndrchk.robot
    10ge2p1x520-dot1q-l2xcbase-ndrpdrdisc.robot
    10ge2p1x520-eth-l2bdbasemaclrn-ndrchk.robot
    10ge2p1x520-eth-l2bdbasemaclrn-ndrpdrdisc.robot
    10ge2p1x520-eth-l2bdbasemaclrn-pdrchk.robot
    10ge2p1x520-eth-l2xcbase-ndrchk.robot
    10ge2p1x520-eth-l2xcbase-ndrpdrdisc.robot
    10ge2p1x520-eth-l2xcbase-pdrchk.robot
    10ge2p1x710-eth-l2bdbasemaclrn-ndrpdrdisc.robot
    40ge2p1vic1385-eth-l2bdbasemaclrn-ndrpdrdisc.robot
    40ge2p1xl710-eth-l2bdbasemaclrn-ndrpdrdisc.robot
    40ge2p1xl710-eth-l2xcbase-ndrpdrdisc.robot
```

#### IPv4 Routed-Forwarding
```
ls | grep -P 'ethip4(udp|)-ip4(base|scale)[a-z0-9]*(?!-eth-[0-9]vhost).*-(ndrpdrdisc|ndrchk|pdrchk)'
```
```
ip4/
    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrchk.robot
    10ge2p1x520-ethip4-ip4base-copwhtlistbase-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrchk.robot
    10ge2p1x520-ethip4-ip4base-iacldstbase-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrchk.robot
    10ge2p1x520-ethip4-ip4base-ipolicemarkbase-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-ndrchk.robot
    10ge2p1x520-ethip4-ip4base-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-pdrchk.robot
    10ge2p1x520-ethip4-ip4base-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4scale200k-ndrchk.robot
    10ge2p1x520-ethip4-ip4scale200k-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4scale20k-ndrchk.robot
    10ge2p1x520-ethip4-ip4scale20k-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4scale2m-ndrchk.robot
    10ge2p1x520-ethip4-ip4scale2m-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4base-udpsrcscale15-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4scale1000-udpsrcscale15-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4scale100-udpsrcscale15-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4scale10-udpsrcscale15-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4scale2000-udpsrcscale15-snat-ndrpdrdisc.robot
    10ge2p1x520-ethip4udp-ip4scale4000-udpsrcscale15-snat-ndrpdrdisc.robot
    40ge2p1xl710-ethip4-ip4base-ndrpdrdisc.robot
```

#### IPv6 Routed-Forwarding
```
ls | grep -E "ethip6-ip6(base|scale)[-a-z0-9]*-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
ip6/
    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrchk.robot
    10ge2p1x520-ethip6-ip6base-copwhtlistbase-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrchk.robot
    10ge2p1x520-ethip6-ip6base-iacldstbase-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6base-ndrchk.robot
    10ge2p1x520-ethip6-ip6base-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6base-pdrchk.robot
    10ge2p1x520-ethip6-ip6scale200k-ndrchk.robot
    10ge2p1x520-ethip6-ip6scale200k-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6scale20k-ndrchk.robot
    10ge2p1x520-ethip6-ip6scale20k-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6scale2m-ndrchk.robot
    10ge2p1x520-ethip6-ip6scale2m-ndrpdrdisc.robot
    10ge2p1x520-ethip6-ip6scale2m-pdrchk.robot
    40ge2p1xl710-ethip6-ip6base-ndrpdrdisc.robot
```

#### IPv4 Overlay Tunnels
```
ls | grep -E "ethip4[a-z0-9]+-[a-z0-9]*-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
ip4_tunnels/
    10ge2p1x520-ethip4lispip4-ip4base-ndrchk.robot
    10ge2p1x520-ethip4lispip4-ip4base-ndrpdrdisc.robot
    10ge2p1x520-ethip4lispip4-ip4base-pdrchk.robot
    10ge2p1x520-ethip4lispip6-ip4base-ndrchk.robot
    10ge2p1x520-ethip4lispip6-ip4base-ndrpdrdisc.robot
    10ge2p1x520-ethip4lispip6-ip4base-pdrchk.robot
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrpdrdisc.robot
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrchk.robot
    10ge2p1x520-ethip4vxlan-l2xcbase-ndrpdrdisc.robot
    10ge2p1x520-ethip4vxlan-l2xcbase-pdrchk.robot
```

#### IPv6 Overlay Tunnels
```
ls | grep -E "ethip6[a-z0-9]+-[a-z0-9]*-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
ip6_tunnels/
    10ge2p1x520-ethip6lispip4-ip6base-ndrchk.robot
    10ge2p1x520-ethip6lispip4-ip6base-ndrpdrdisc.robot
    10ge2p1x520-ethip6lispip4-ip6base-pdrchk.robot
    10ge2p1x520-ethip6lispip6-ip6base-ndrchk.robot
    10ge2p1x520-ethip6lispip6-ip6base-ndrpdrdisc.robot
    10ge2p1x520-ethip6lispip6-ip6base-pdrchk.robot
```

#### VM vhost Connections
```
ls | grep -E ".*vhost.*-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
vm_vhost/
    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-dot1q-l2xcbase-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot
    10ge2p1x520-eth-l2xcbase-eth-2vhost-1vm-ndrpdrdisc.robot
    10ge2p1x520-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot
    10ge2p1x710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot
    40ge2p1xl710-ethip4-ip4base-eth-4vhost-2vm-ndrpdrdisc.robot
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrpdrdisc.robot
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-4vhost-2vm-ndrpdrdisc.robot
    40ge2p1xl710-eth-l2xcbase-eth-4vhost-2vm-ndrpdrdisc.robot
```

#### IPSec Crypto HW: IP4 Routed-Forwarding
```
ls | grep -E ".*ipsec.*-(ndrpdrdisc|ndrchk|pdrchk)"
```
```
crypto/
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-aes-gcm-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1-ndrpdrdisc.robot
    40ge2p1xl710-ethip4ipsectptlispgpe-ip4base-cbc-sha1-ndrpdrdisc.robot
```

### Functional

#### L2 Ethernet Switching
```
l2bd/
    eth4p-eth-l2bdbasemaclrn-l2shg-func.robot
    eth2p-eth-l2bdbasemaclrn-func.robot
    eth2p-eth-l2bdbasemacstc-func.robot
    eth2p-dot1ad--dot1q-l2bdbasemaclrn-vlantrans21-func.robot
    eth2p-dot1ad-l2bdbasemaclrn-vlantrans22-func.robot
    eth2p-dot1q--dot1ad-l2bdbasemaclrn-vlantrans12-func.robot
    eth2p-dot1q-l2bdbasemaclrn-vlantrans11-func.robot
```

```
l2xc/
    eth2p-eth-l2xcbase-func.robot
    eth2p-dot1ad-l2xcbase-func.robot
    eth2p-dot1ad--dot1q-l2xcbase-vlantrans21-func.robot
    eth2p-dot1ad-l2xcbase-vlantrans22-func.robot
    eth2p-dot1q--dot1ad-l2xcbase-vlantrans12-func.robot
    eth2p-dot1q-l2xcbase-vlantrans11-func.robot
    eth2p-eth-l2xcbase-iaclbase-func.robot
```

#### IPv4 Routed-Forwarding
```
ip4/
    eth2p-ethip4-ip4base-func.robot
    eth2p-ethip4-ip4base-ip4proxyarp-func.robot
    eth2p-ethip4-ip4base-ip4arp-func.robot
    eth2p-ethip4-ip4base-ip4ecmp-func.robot
    eth2p-dot1q-ip4base-func.robot
    eth2p-ethip4-ip4base-ip4dhcpclient-func.robot
    eth2p-ethip4-ip4base-ip4dhcpproxy-func.robot
    eth2p-ethip4-ip4base-copwhlistbase-func.robot
    eth2p-ethip4-ip4base-copblklistbase-func.robot
    eth2p-ethip4-ip4base-iaclbase-func.robot
    eth2p-ethip4-ip4base-ipolicemarkbase-func.robot
    eth2p-ethip4-ip4base-rpf-func.robot
    eth2p-ethip4-ip4basevrf-func.robot
```

#### IPv6 Routed-Forwarding
```
ip6/
    eth2p-ethip6-ip6base-func.robot
    eth2p-ethip6-ip6base-ip6ra-func.robot
    eth2p-ethip6-ip6base-ip6ecmp-func.robot
    eth2p-ethip6-ip6base-ip6dhcpproxy-func.robot
    eth2p-ethip6-ip6base-copwhlistbase-func.robot
    eth2p-ethip6-ip6base-copblklistbase-func.robot
    eth2p-ethip6-ip6base-iaclbase-func.robot
    eth2p-ethip6-ip6base-ipolicemarkbase-func.robot
    eth2p-ethip6-ip6basevrf-func.robot
```

#### IPv4 Overlay Tunnels
```
ip4_tunnels/
    gre/
        eth2p-ethip4gre-ip4base-func.robot
    lisp/
        api-crud-lisp-func.robot
        eth2p-ethip4lispgpe-ip4basevrf-func.robot
        eth2p-ethip4lispgpe-ip6base-func.robot
        eth2p-ethip4lispgpe-ip6basevrf-func.robot
        eth2p-ethip4lispgpe-ip4base-func.robot
        eth2p-ethip4lisp-ip4base-func.robot
        eth2p-ethip4lisp-l2bdbasemaclrn-func.robot
    softwire/
        eth2p-ethip4--ethip6ip4-ip4base--ip6base-swiremapt-func.robot
        eth2p-ethip4--ethip6ip4-ip4base--ip6base-swirelw46-func.robot
        eth2p-ethip4--ethip6ip4-ip4base--ip6base-swiremape-func.robot
    vxlan/
        eth4p-ethip4vxlan-l2bdbasemaclrn-l2shg-func.robot
        eth2p-dot1qip4vxlan-l2bdbasemaclrn-func.robot
        eth2p-ethip4vxlan-l2bdbasemaclrn-func.robot
        eth2p-ethip4vxlan-l2xcbase-func.robot
```

#### IPv6 Overlay Tunnels
```
ip6_tunnels/
    lisp/
        eth2p-ethip6lispgpe-ip6base-func.robot
        eth2p-ethip6lispgpe-ip6basevrf-func.robot
        eth2p-ethip6lispgpe-ip4base-func.robot
        eth2p-ethip6lisp-l2bdbasemaclrn-func.robot
    vxlan/
        eth4p-ethip6vxlan-l2bdbasemaclrn-l2shg-func.robot
        eth2p-ethip6vxlan-l2bdbasemaclrn-func.robot
```

#### VM vhost Connections
```
vm_vhost/
    l2bd/
        eth2p-eth-l2bdbasemacstc-eth-2vhost-1vm-func.robot
        eth2p-eth-l2bdbasemaclrn-eth-2vhost-1vm-func.robot
        eth2p-dot1q-l2bdbasemaclrn-eth-4vhost-2vm-fds-provider-nets-func.robot
        eth2p-ethip4vxlan-l2bdbasemaclrn--eth-4vhost-2vm-fds-tenant-nets-func.robot
        eth2p-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-func.robot
        eth2p-ethip4-l2bdbase-vhost-client-reconnect-2vm-func.robot
        eth2p-ethip6vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot
        eth2p-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-func.robot
    l2xc/
        eth2p-eth-l2xcbase-eth-2vhost-1vm-func.robot
    ip4/
        eth2p-ethip4-ip4base-eth-2vhost-1vm.robot
        eth2p-ethip4lispgpe-ip4basevrf-eth-2vhost-1vm-func.robot
        eth2p-ethip4ipsectptlispgpe-ip4base-eth-2vhost-1vm-func.robot
        eth2p-ethip4lispgpe-ip6base-eth-2vhost-1vm-func.robot
        eth2p-ethip4lispgpe-ip4base-eth-2vhost-1vm-func.robot
        eth2p-ethip4ipsectptlispgpe-ip6base-eth-2vhost-1vm-func.robot
    ip6/
        eth2p-ethip6lispgpe-ip6base-eth-2vhost-1vm-func.robot
        eth2p-ethip6ipsectptlispgpe-ip6base-eth-2vhost-1vm-func.robot
        eth2p-ethip6ipsectptlispgpe-ip4base-eth-2vhost-1vm-func.robot
        eth2p-ethip6lispgpe-ip6basevrf-eth-2vhost-1vm-func.robot
```

#### Crypto HW: IP4 Routed-Forwarding
```
crypto/
    eth2p-ethip4ipsectpt-ip4base-func.robot
    eth2p-ethip4ipsectnl-ip4base-func.robot
    eth2p-ethip6ipsectpt-ip6base-func.robot
    eth2p-ethip6ipsectnl-ip6base-func.robot
    eth2p-ethip4ipsectptlispgpe-ip6basevrf-func.robot
    eth2p-ethip4ipsectptlispgpe-ip4base-func.robot
    eth2p-ethip4ipsectptlispgpe-ip6base-func.robot
    eth2p-ethip6ipsectptlispgpe-ip6base-func.robot
    eth2p-ethip6ipsectptlispgpe-ip4base-func.robot
```

#### Honecomb
```
honeycomb/
    __init__.robot
    mgmt-cfg-l2fib-apihc-apivat-func.robot
    mgmt-cfg-slaac-apihc-func.robot
    mgmt-cfg-l2bd-apihc-apivat-func.robot
    mgmt-cfg-lisp-apihc-apivat-func.robot
    mgmt-cfg-intip4-intip6-apihc-apivat-func.robot
    mgmt-cfg-nsh-apihc-apivat-func.robot
    mgmt-cfg-proxyarp-apihc-func.robot
    mgmt-cfg-int-subint-apihc-apivat-func.robot
    mgmt-cfg-snat44-apihc-apivat-func.robot
    mgmt-cfg-vxlangpe-apihc-apivat-func.robot
    mgmt-cfg-pluginacl-apihc-apivat-func.robot
    mgmt-cfg-dhcp-apihc-apivat-func.robot
    mgmt-cfg-inttap-apihc-apivat-func.robot
    mgmt-cfg-routing-apihc-apivat-func.robot
    mgmt-cfg-spanrx-apihc-apivat-func.robot
    mgmt-cfg-vxlan-apihc-apivat-func.robot
    mgmt-cfg-policer-apihc-func.robot
    mgmt-cfg-intvhost-apihc-apivat-func.robot
    mgmt-notif-apihcnc-func.robot
    mgmt-cfg-proxynd6-apihc-func.robot
    mgmt-cfg-pbb-apihc-apivat-func.robot
    mgmt-statepersist-apihc-func.robot
    mgmt-cfg-int-apihcnc-func.robot
    mgmt-cfg-acl-apihc-apivat-func.robot
```

#### Telemetry
```
telemetry/
    eth2p-ethip6-ip6base-spanrx-func.robot
    eth2p-ethip4-ip4base-spanrx-func.robot
    eth2p-ethip4-ip4base-ip4ipfixscale-func.robot
    eth2p-ethip6-ip6base-ip6ipfixscale-func.robot
    eth2p-ethip4-ip4base-ip4ipfixbase-func.robot
    eth2p-ethip6-ip6base-ip6ipfixbase-func.robot
```

#### Interface
```
interfaces/
    eth2p-ethip4-ip4base-eth-1tap-func.robot
    eth2p-eth-l2bdbasemaclrn-eth-2tap-func.robot
    eth2p-eth-l2bdbasemaclrn-l2shg-eth-2tap-func.robot
    api-crud-tap-func.robot
```


## Keywords

### L2 Robot keywords
```
shared/
    counters.robot
    default.robot
    interfaces.robot
    traffic.robot
    testing_path.robot
    lxc.robot
l2/
    bridge_domain.robot
    l2_traffic.robot
    l2_xconnect.robot
    tagging.robot
ip/
    ipv4.robot
    ipv6.robot
    snat.robot
    map.robot
overlay/
    gre.robot
    lisp_static_adjacency.robot
    lispgpe.robot
    l2lisp.robot
    lisp_api.robot
    vxlan.robot
vm/
    double_qemu_setup.robot
    qemu.robot
crypto/
    ipsec.robot
dpdk/
    default.robot
nsh_sfc/
    default.robot
tldk/
    TLDKUtils.robot
honeycomb/
    policer.robot
    nat.robot
    port_mirroring.robot
    vhost_user.robot
    netconf.robot
    nsh.robot
    vxlan.robot
    dhcp.robot
    slaac.robot
    notifications.robot
    routing.robot
    access_control_lists.robot
    tap.robot
    interfaces.robot
    honeycomb.robot
    persistence.robot
    sub_interface.robot
    provider_backbone_bridge.robot
    vxlan_gpe.robot
    proxyarp.robot
    bridge_domain.robot
    lisp.robot
    l2_fib.robot
performance/
    performance_configuration.robot
    performance_utils.robot
    performance_setup.robot
telemetry/
    span.robot
    ipfix.robot
features/
    policer.robot
    dhcp_client.robot
    dhcp_proxy.robot
fds/
    default.robot
```

### L1 Python keywords

No changes at this stage.
