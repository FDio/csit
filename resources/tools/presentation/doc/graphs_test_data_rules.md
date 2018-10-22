# Test Data Presentation Rules for Graphs

rules
  max 6 test cases grouped per graph
  test cases listed in specified order
applicability
  all plotly graphs used in FD.io CSIT reports up to CSIT-18.10
    plotly.graph_objs.Box throughput packet
    plotly.graph_objs.Scatter Latency E-W W-E
    plotly.graph_objs.Scatter Speedup Multi-Core

# Packet Throughput Graphs

plotly.graph_objs.Box: L2 Ethernet Switching
  3n-hsw-x520
  3n-hsw-x710
  3n-hsw-xl710
  3n-hsw-vic1227
  3n-hsw-vic1385
  3n-skx-x710

    64b-2t1c-base_and_scale
      Throughput: l2sw-3n-skx-x710-64b-2t1c-base_and_scale-ndr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn
      Throughput: l2sw-3n-skx-x710-64b-2t1c-base_and_scale-pdr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn

    64b-2t1c-base_and_features
      Throughput: l2sw-3n-skx-x710-64b-2t1c-base_and_features-ndr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase
      Throughput: l2sw-3n-skx-x710-64b-2t1c-base_and_features-pdr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase

    64b-4t2c-base_and_scale
      Throughput: l2sw-3n-skx-x710-64b-4t2c-base_and_scale-ndr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn
      Throughput: l2sw-3n-skx-x710-64b-4t2c-base_and_scale-pdr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn

    64b-4t2c-base_and_features
      Throughput: l2sw-3n-skx-x710-64b-4t2c-base_and_features-ndr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase
      Throughput: l2sw-3n-skx-x710-64b-4t2c-base_and_features-pdr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase

    64b-8t4c-base_and_scale
      Throughput: l2sw-3n-skx-x710-64b-8t4c-base_and_scale-ndr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn
      Throughput: l2sw-3n-skx-x710-64b-8t4c-base_and_scale-pdr
        1. 10ge2p1x710-l2patch
        2. 10ge2p1x710-l2xcbase
        3. 10ge2p1x710-l2bdbase
        4. 10ge2p1x710-l2bdscale10kmaclrn
        5. 10ge2p1x710-l2bdscale100kmaclrn
        6. 10ge2p1x710-l2bdscale1mmaclrn

    64b-8t4c-base_and_features
      Throughput: l2sw-3n-skx-x710-64b-8t4c-base_and_features-ndr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase
      Throughput: l2sw-3n-skx-x710-64b-8t4c-base_and_features-pdr
        1. 10ge2p1x710-l2xcbase
        2. 10ge2p1x710-l2bdbase
        3. 10ge2p1x710-dot1q-l2xcbase
        4. 10ge2p1x710-dot1q-l2bdbase

plotly.graph_objs.box: IPv4 Routing

  3n-hsw-x520

    64b-1t1c-base_and_scale
      Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_scale-ndr
        1. 10ge2p1x520-ethip4-ip4base
        2. 10ge2p1x520-ethip4-ip4scale20k
        3. 10ge2p1x520-ethip4-ip4scale200k
        4. 10ge2p1x520-ethip4-ip4scale2m
      Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_scale-pdr
        1. 10ge2p1x520-ethip4-ip4base
        2. 10ge2p1x520-ethip4-ip4scale20k
        3. 10ge2p1x520-ethip4-ip4scale200k
        4. 10ge2p1x520-ethip4-ip4scale2m

    64b-1t1c-base_and_features
      Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_features-ndr
        1. 10ge2p1x520-ethip4-ip4base
        2. 10ge2p1x520-ethip4-ip4base-nat44
        3. 10ge2p1x520-ethip4-ip4base-ipolicemarkbase
        4. 10ge2p1x520-ethip4udp-ip4base-iacl10sl-10kflows
        5. 10ge2p1x520-ethip4udp-ip4base-oacl10sl-10kflows
      Throughput: ip4-3n-hsw-x520-64b-1t1c-base_and_features-pdr
        1. 10ge2p1x520-ethip4-ip4base
        2. 10ge2p1x520-ethip4-ip4base-nat44
        3. 10ge2p1x520-ethip4-ip4base-ipolicemarkbase
        4. 10ge2p1x520-ethip4udp-ip4base-iacl10sl-10kflows
        5. 10ge2p1x520-ethip4udp-ip4base-oacl10sl-10kflows

    64b-1t1c-features_and_scale_nat44
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_nat44-ndr
        1. 10ge2p1x520-ethip4-ip4base-nat44
        2. 10ge2p1x710-ethip4-ip4base-updsrcscale15-nat44
        3. 10ge2p1x710-ethip4-ip4scale10-updsrcscale15-nat44
        4. 10ge2p1x710-ethip4-ip4scale100-updsrcscale15-nat44
        5. 10ge2p1x710-ethip4-ip4scale1000-updsrcscale15-nat44
        6. 10ge2p1x710-ethip4-ip4scale2000-updsrcscale15-nat44
REMOVE  7. 10ge2p1x710-ethip4-ip4scale4000-updsrcscale15-nat44
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_nat44-pdr
        1. 10ge2p1x520-ethip4-ip4base-nat44
        2. 10ge2p1x710-ethip4-ip4base-updsrcscale15-nat44
        3. 10ge2p1x710-ethip4-ip4scale10-updsrcscale15-nat44
        4. 10ge2p1x710-ethip4-ip4scale100-updsrcscale15-nat44
        5. 10ge2p1x710-ethip4-ip4scale1000-updsrcscale15-nat44
        6. 10ge2p1x710-ethip4-ip4scale2000-updsrcscale15-nat44
REMOVE  7. 10ge2p1x710-ethip4-ip4scale4000-updsrcscale15-nat44

    64b-1t1c-features_and_scale_iacl
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_iacl-ndr
        1. 10ge2p1x520-ethip4udp-ip4base-iacl10sl-10kflows
        2. 10ge2p1x520-ethip4udp-ip4base-iacl10sf-10kflows
        3. 10ge2p1x520-ethip4udp-ip4base-iacl50sf-10kflows
        4. 10ge2p1x520-ethip4udp-ip4base-iacl50sl-10kflows
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_iacl-pdr
        1. 10ge2p1x520-ethip4udp-ip4base-iacl10sl-10kflows
        2. 10ge2p1x520-ethip4udp-ip4base-iacl10sf-10kflows
        3. 10ge2p1x520-ethip4udp-ip4base-iacl50sf-10kflows
        4. 10ge2p1x520-ethip4udp-ip4base-iacl50sl-10kflows

    64b-1t1c-features_and_scale_oacl
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_oacl-ndr
        1. 10ge2p1x520-ethip4udp-ip4base-oacl10sl-10kflows
        2. 10ge2p1x520-ethip4udp-ip4base-oacl10sf-10kflows
        3. 10ge2p1x520-ethip4udp-ip4base-oacl50sf-10kflows
        4. 10ge2p1x520-ethip4udp-ip4base-oacl50sl-10kflows
      Throughput: ip4-3n-hsw-x520-64b-1t1c-features_and_scale_oacl-pdr
        1. 10ge2p1x520-ethip4udp-ip4base-oacl10sl-10kflows
        2. 10ge2p1x520-ethip4udp-ip4base-oacl10sf-10kflows
        3. 10ge2p1x520-ethip4udp-ip4base-oacl50sf-10kflows
        4. 10ge2p1x520-ethip4udp-ip4base-oacl50sl-10kflows

  3n-skx-x710

    64b-2t1c-base_and_scale
      Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_scale-ndr
        1. 10ge2p1x710-ethip4-ip4base
        2. 10ge2p1x710-ethip4-ip4scale20k
        3. 10ge2p1x710-ethip4-ip4scale200k
        4. 10ge2p1x710-ethip4-ip4scale2m
      Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_scale-pdr
        1. 10ge2p1x710-ethip4-ip4base
        2. 10ge2p1x710-ethip4-ip4scale20k
        3. 10ge2p1x710-ethip4-ip4scale200k
        4. 10ge2p1x710-ethip4-ip4scale2m

    64b-2t1c-base_and_features
      Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_features-ndr
        1. 10ge2p1x710-ethip4-ip4base
        2. 10ge2p1x710-ethip4-ip4base-nat44
        3. 10ge2p1x710-ethip4-ip4base-ipolicemarkbase
      Throughput: ip4-3n-skx-x710-64b-2t1c-base_and_features-pdr
        1. 10ge2p1x710-ethip4-ip4base
        2. 10ge2p1x710-ethip4-ip4base-nat44
        3. 10ge2p1x710-ethip4-ip4base-ipolicemarkbase

  3n-hsw-x520
  3n-hsw-x710
  3n-hsw-xl710
  3n-hsw-vic1227
  3n-hsw-vic1385
  3n-skx-x710

# Packet Latency Graphs

plotly.graph_objs.Scatter: L2 Ethernet Switching

# Speedup Multi-Core Graphs

plotly.graph_objs.Scatter: L2 Ethernet Switching