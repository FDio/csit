# Test Groups for Trending

## Introduction

Specifications of test groups for daily Trending graphs (see
[Trending web page]) are provided in this note.

### Order of Chapters on Trending Web Page
1. L2 Ethernet Switching
2. IPv4 Routing
3. IPv6 Routing
4. SRv6 Routing
5. IPv4 Tunnels
6. KVM VMs vhost-user
7. LXC/DRC Container Memif
8. IPsec with IPv4 Routing
9. Virtual Topology System
10. NF Service Density
11. DPDK

### Presented Test Configurations

Only tests with NICs, processor cores and frame sizes specified below
will be presented in the Trending.

#### NICs
- See [Performance Tests Job Specifications, chapter NICs]
- See item nr 1 in TODO list.

#### Processor Cores in Trending Graphs
- 1c (1t1c or 2t1c),
- 2c (2t2c or 4t2c),
- 4c (4t4c or 8t4c).

See item nr 3 in TODO list.

#### Frame Sizes
- See [Performance Tests Job Specifications, chapter Frame Sizes]
- See item nr 2 in TODO list.

### Backward compatibility

The new structure will not be backward compatible with the previous one.
The old data and graphs will be stored and accessible on the link:
<https://docs.fd.io/csit/master/trending-archive/>. A link to this page
will be on the Trending web page.

### Notes
1. The lists of tests are based on running tests in trending jobs
   - [2n-skx]
   - [3n-skx]
   - [3n-hsw]
   - [3n-tsh]
   - [2n-dnv]
   - [3n-dnv]
   - [2n-clx]

   and on the lists of selected tests (test_select_list_*.md) stored in
   the [Jobs specifications] directory.
2. The order of chapters, sub-chapters and tests in the graphs on the
   [Trending web page] will be the same as specified in this document.

### TODO List
1. Change the trending jobs to use primary and secondary NICs as they
   are defined in [Performance Tests Job Specifications, chapter NICs].
2. Change the trending jobs to use frame sizes as they are defined in
   [Performance Tests Job Specifications, chapter Frame Sizes].
3. Change the trending jobs to use processor cores as they are defined
   in [Performance Tests Job Specifications, chapter Processor Cores].

# Test Groups

## L2 Ethernet Switching

### 2n-skx-xxv710

#### 64b-?t?c-l2switching-base-avf
    2n1l-25ge2p1xxv710-avf-eth-l2patch-mrr
    2n1l-25ge2p1xxv710-avf-eth-l2xcbase-mrr
    2n1l-25ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-avf-eth-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-gbp-mrr

#### 64b-?t?c-l2switching-base-i40e
    2n1l-25ge2p1xxv710-eth-l2patch-mrr
    2n1l-25ge2p1xxv710-dot1q-l2xcbase-mrr
    2n1l-25ge2p1xxv710-eth-l2xcbase-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-i40e
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale10kmaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale100kmaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale1mmaclrn-mrr

### 2n-skx-x710

#### 64b-?t?c-l2switching-base-scale-avf-i40e
    2n1l-10ge2p1x710-avf-eth-l2xcbase-mrr
    2n1l-10ge2p1x710-avf-dot1q-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-avf-eth-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-dot1q-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-eth-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-eth-l2bdscale1mmaclrn-mrr

### 3n-skx-xxv710

#### 64b-?t?c-l2switching-base-avf
    25ge2p1xxv710-avf-eth-l2patch-mrr
    25ge2p1xxv710-avf-eth-l2xcbase-mrr
    25ge2p1xxv710-avf-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-i40e
    25ge2p1xxv710-dot1q-l2xcbase-mrr
    25ge2p1xxv710-eth-l2xcbase-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-i40e
    25ge2p1xxv710-eth-l2patch-mrr
    25ge2p1xxv710-eth-l2xcbase-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-mrr
    25ge2p1xxv710-eth-l2bdscale10kmaclrn-mrr
    25ge2p1xxv710-eth-l2bdscale100kmaclrn-mrr
    25ge2p1xxv710-eth-l2bdscale1mmaclrn-mrr

####  64b-?t?c-features-l2switching-base-i40e
    25ge2p1xxv710-eth-l2bdbasemaclrn-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr

### 3n-skx-x710

#### 64b-?t?c-l2switching-base-scale-avf-i40e
    10ge2p1x710-avf-eth-l2patch-mrr
    10ge2p1x710-avf-eth-l2xcbase-mrr
    10ge2p1x710-avf-eth-l2bdbasemaclrn-mrr
    10ge2p1x710-dot1q-l2bdbasemaclrn-mrr
    10ge2p1x710-eth-l2bdbasemaclrn-mrr
    10ge2p1x710-eth-l2bdscale1mmaclrn-mrr

### 3n-hsw-xl710

#### 64b-?t?c-l2switching-base-scale-i40e
    40ge2p1xl710-eth-l2patch-mrr
    40ge2p1xl710-dot1q-l2xcbase-mrr
    40ge2p1xl710-eth-l2xcbase-mrr
    40ge2p1xl710-dot1q-l2bdbasemaclrn-mrr
    40ge2p1xl710-eth-l2bdbasemaclrn-mrr
    40ge2p1xl710-eth-l2bdscale1mmaclrn-mrr

### 3n-tsh-x520

#### 64b-?t?c-l2switching-base-ixgbe
    10ge2p1x520-dot1q-l2xcbase-mrr
    10ge2p1x520-eth-l2xcbase-mrr
    10ge2p1x520-dot1q-l2bdbasemaclrn-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-ixgbe
    10ge2p1x520-eth-l2patch-mrr
    10ge2p1x520-eth-l2xcbase-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-mrr
    10ge2p1x520-eth-l2bdscale10kmaclrn-mrr
    10ge2p1x520-eth-l2bdscale100kmaclrn-mrr
    10ge2p1x520-eth-l2bdscale1mmaclrn-mrr

#### 64b-?t?c-features-l2switching-base-ixgbe
    10ge2p1x520-eth-l2bdbasemaclrn-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr

### 2n-dnv-x553

#### 64b-?t?c-l2switching-base-ixgbe
    10ge2p1x553-dot1q-l2xcbase-mrr
    10ge2p1x553-eth-l2xcbase-mrr
    10ge2p1x553-dot1q-l2bdbasemaclrn-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-ixgbe
    10ge2p1x553-eth-l2patch-mrr
    10ge2p1x553-eth-l2xcbase-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-mrr
    10ge2p1x553-eth-l2bdscale10kmaclrn-mrr
    10ge2p1x553-eth-l2bdscale100kmaclrn-mrr
    10ge2p1x553-eth-l2bdscale1mmaclrn-mrr

### 3n-dnv-x553

#### 64b-?t?c-l2switching-base-ixgbe
    10ge2p1x553-dot1q-l2xcbase-mrr
    10ge2p1x553-eth-l2xcbase-mrr
    10ge2p1x553-dot1q-l2bdbasemaclrn-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-ixgbe
    10ge2p1x553-eth-l2patch-mrr
    10ge2p1x553-eth-l2xcbase-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-mrr
    10ge2p1x553-eth-l2bdscale10kmaclrn-mrr
    10ge2p1x553-eth-l2bdscale100kmaclrn-mrr
    10ge2p1x553-eth-l2bdscale1mmaclrn-mrr

####  64b-?t?c-features-l2switching-base-ixgbe
    10ge2p1x553-eth-l2bdbasemaclrn-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
    10ge2p1x553-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr

### 2n-clx-xxv710

#### 64b-?t?c-l2switching-base-avf
    2n1l-25ge2p1xxv710-avf-eth-l2patch-mrr
    2n1l-25ge2p1xxv710-avf-eth-l2xcbase-mrr
    2n1l-25ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-avf-eth-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-avf-dot1q-l2bdbasemaclrn-gbp-mrr

#### 64b-?t?c-l2switching-base-i40e
    2n1l-25ge2p1xxv710-eth-l2patch-mrr
    2n1l-25ge2p1xxv710-dot1q-l2xcbase-mrr
    2n1l-25ge2p1xxv710-eth-l2xcbase-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-mrr

#### 64b-?t?c-l2switching-base-scale-i40e
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale10kmaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale100kmaclrn-mrr
    2n1l-25ge2p1xxv710-eth-l2bdscale1mmaclrn-mrr

### 2n-clx-x710

#### 64b-?t?c-l2switching-base-scale-avf-i40e
    2n1l-10ge2p1x710-avf-eth-l2xcbase-mrr
    2n1l-10ge2p1x710-avf-dot1q-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-avf-eth-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-dot1q-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-eth-l2bdbasemaclrn-mrr
    2n1l-10ge2p1x710-eth-l2bdscale1mmaclrn-mrr

## IPv4 Routing

### 2n-skx-xxv710

#### 64b-?t?c-ip4routing-base-scale-avf
    2n1l-25ge2p1xxv710-avf-dot1q-ip4base-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale20k-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale200k-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale2m-mrr

#### 64b-?t?c-ip4routing-base-scale-i40e
    2n1l-25ge2p1xxv710-dot1q-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale20k-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale200k-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-i40e
    2n1l-25ge2p1xxv710-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-nat44-mrr

### 2n-skx-x710

####  64b-?t?c-ip4routing-base-scale-avf-i40e
    2n1l-10ge2p1x710-avf-ethip4-ip4base-mrr
    2n1l-10ge2p1x710-avf-ethip4-ip4scale2m-mrr
    2n1l-10ge2p1x710-dot1q-ip4base-mrr
    2n1l-10ge2p1x710-ethip4-ip4base-mrr
    2n1l-10ge2p1x710-ethip4-ip4scale2m-mrr

### 3n-skx-xxv710

#### 64b-?t?c-ip4routing-base-scale-avf
    25ge2p1xxv710-avf-eth-ip4base-mrr
    25ge2p1xxv710-avf-ethip4-ip4scale20k-mrr
    25ge2p1xxv710-avf-ethip4-ip4scale200k-mrr
    25ge2p1xxv710-avf-ethip4-ip4scale2m-mrr

#### 64b-?t?c-ip4routing-base-scale-i40e
    25ge2p1xxv710-dot1q-ip4base-mrr
    25ge2p1xxv710-ethip4-ip4base-mrr
    25ge2p1xxv710-ethip4-ip4scale20k-mrr
    25ge2p1xxv710-ethip4-ip4scale200k-mrr
    25ge2p1xxv710-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-i40e
    25ge2p1xxv710-ethip4-ip4base-mrr
    25ge2p1xxv710-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    25ge2p1xxv710-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    25ge2p1xxv710-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    25ge2p1xxv710-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    25ge2p1xxv710-ethip4udp-ip4base-nat44-mrr

### 3n-skx-x710

#### 64b-?t?c-ip4routing-base-scale-avf-i40e
    10ge2p1x710-avf-ethip4-ip4base-mrr
    10ge2p1x710-avf-ethip4-ip4scale2m-mrr
    10ge2p1x710-dot1q-ip4base-mrr
    10ge2p1x710-ethip4-ip4base-mrr
    10ge2p1x710-ethip4-ip4scale2m-mrr

### 3n-hsw-xl710

#### 64b-?t?c-ip4routing-base-scale-i40e
    40ge2p1xl710-dot1q-ip4base-mrr
    40ge2p1xl710-ethip4-ip4base-mrr
    40ge2p1xl710-ethip4-ip4scale2m-mrr

### 3n-tsh-x520

#### 64b-?t?c-ip4routing-base-scale-ixgbe
    10ge2p1x520-dot1q-ip4base-mrr
    10ge2p1x520-ethip4-ip4base-mrr
    10ge2p1x520-ethip4-ip4scale20k-mrr
    10ge2p1x520-ethip4-ip4scale200k-mrr
    10ge2p1x520-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-ixgbe
    10ge2p1x520-ethip4-ip4base-mrr
    10ge2p1x520-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    10ge2p1x520-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    10ge2p1x520-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    10ge2p1x520-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    10ge2p1x520-ethip4udp-ip4base-nat44-mrr

### 2n-dnv-x553

#### 64b-?t?c-ip4routing-base-scale-ixgbe
    10ge2p1x553-dot1q-ip4base-mrr
    10ge2p1x553-ethip4-ip4base-mrr
    10ge2p1x553-ethip4-ip4scale20k-mrr
    10ge2p1x553-ethip4-ip4scale200k-mrr
    10ge2p1x553-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-ixgbe
    10ge2p1x553-ethip4-ip4base-mrr
    10ge2p1x553-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-nat44-mrr

### 3n-dnv-x553

#### 64b-?t?c-ip4routing-base-scale-ixgbe
    10ge2p1x553-dot1q-ip4base-mrr
    10ge2p1x553-ethip4-ip4base-mrr
    10ge2p1x553-ethip4-ip4scale20k-mrr
    10ge2p1x553-ethip4-ip4scale200k-mrr
    10ge2p1x553-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-ixgbe
    10ge2p1x553-ethip4-ip4base-mrr
    10ge2p1x553-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    10ge2p1x553-ethip4udp-ip4base-nat44-mrr

### 2n-clx-xxv710

#### 64b-?t?c-ip4routing-base-scale-avf
    2n1l-25ge2p1xxv710-avf-dot1q-ip4base-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale20k-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale200k-mrr
    2n1l-25ge2p1xxv710-avf-ethip4-ip4scale2m-mrr

#### 64b-?t?c-ip4routing-base-scale-i40e
    2n1l-25ge2p1xxv710-dot1q-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale20k-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale200k-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4scale2m-mrr

#### 64b-?t?c-features-ip4routing-base-i40e
    2n1l-25ge2p1xxv710-ethip4-ip4base-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-iacl50sf-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-iacl50sl-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-oacl50sf-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-oacl50sl-10kflows-mrr
    2n1l-25ge2p1xxv710-ethip4udp-ip4base-nat44-mrr

### 2n-clx-x710

####  64b-?t?c-ip4routing-base-scale-avf-i40e
    2n1l-10ge2p1x710-avf-ethip4-ip4base-mrr
    2n1l-10ge2p1x710-avf-ethip4-ip4scale2m-mrr
    2n1l-10ge2p1x710-dot1q-ip4base-mrr
    2n1l-10ge2p1x710-ethip4-ip4base-mrr
    2n1l-10ge2p1x710-ethip4-ip4scale2m-mrr

## IPv6 Routing

### 2n-skx-xxv710

#### 78b-?t?c-ip6routing-base-scale-i40e
    2n1l-25ge2p1xxv710-dot1q-ip6base-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6base-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale20k-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale200k-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale2m-mrr

### 2n-skx-x710

#### 78b-?t?c-ip6routing-base-scale-i40e
    2n1l-10ge2p1x710-ethip6-ip6base-mrr
    2n1l-10ge2p1x710-ethip6-ip6scale2m-mrr

### 3n-skx-xxv710

#### 78b-?t?c-ip6routing-base-scale-i40e
    25ge2p1xxv710-dot1q-ip6base-mrr
    25ge2p1xxv710-ethip6-ip6base-mrr
    25ge2p1xxv710-ethip6-ip6scale20k-mrr
    25ge2p1xxv710-ethip6-ip6scale200k-mrr
    25ge2p1xxv710-ethip6-ip6scale2m-mrr

### 3n-skx-x710

#### 78b-?t?c-ip6routing-base-scale-i40e
    10ge2p1x710-ethip6-ip6base-mrr
    10ge2p1x710-ethip6-ip6scale2m-mrr

### 3n-hsw-xl710

#### 78b-?t?c-ip6routing-base-scale-i40e
    40ge2p1xl710-dot1q-ip6base-mrr
    40ge2p1xl710-ethip6-ip6base-mrr
    40ge2p1xl710-ethip6-ip6scale2m-mrr

### 3n-tsh-x520

#### 78b-?t?c-ip6routing-base-scale-ixgbe
    10ge2p1x520-dot1q-ip6base-mrr
    10ge2p1x520-ethip6-ip6base-mrr
    10ge2p1x520-ethip6-ip6scale20k-mrr
    10ge2p1x520-ethip6-ip6scale200k-mrr
    10ge2p1x520-ethip6-ip6scale2m-mrr

### 2n-dnv-x553

#### 78b-?t?c-ip6routing-base-scale-ixgbe
    10ge2p1x553-dot1q-ip6base-mrr
    10ge2p1x553-ethip6-ip6base-mrr
    10ge2p1x553-ethip6-ip6scale20k-mrr
    10ge2p1x553-ethip6-ip6scale200k-mrr
    10ge2p1x553-ethip6-ip6scale2m-mrr

### 3n-dnv-x553

#### 78b-?t?c-ip6routing-base-scale-ixgbe
    10ge2p1x553-dot1q-ip6base-mrr
    10ge2p1x553-ethip6-ip6base-mrr
    10ge2p1x553-ethip6-ip6scale20k-mrr
    10ge2p1x553-ethip6-ip6scale200k-mrr
    10ge2p1x553-ethip6-ip6scale2m-mrr

### 2n-clx-xxv710

#### 78b-?t?c-ip6routing-base-scale-i40e
    2n1l-25ge2p1xxv710-dot1q-ip6base-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6base-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale20k-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale200k-mrr
    2n1l-25ge2p1xxv710-ethip6-ip6scale2m-mrr

### 2n-clx-x710

#### 78b-?t?c-ip6routing-base-scale-i40e
    10ge2p1x710-ethip6-ip6base-mrr
    10ge2p1x710-ethip6-ip6scale2m-mrr

## SRv6 Routing

### 3n-skx-xxv710

#### 78b-?t?c-srv6-ip6routing-base-i40e
    25ge2p1xxv710-ethip6ip6-ip6base-srv6enc1sid-mrr
    25ge2p1xxv710-ethip6srhip6-ip6base-srv6enc2sids-mrr
    25ge2p1xxv710-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
    25ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
    25ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-masq-mrr
    25ge2p1xxv710-ethip6srhip6-ip6base-srv6proxy-stat-mrr

### 3n-hsw-xl710

#### 78b-?t?c-srv6-ip6routing-base-i40e
    40ge2p1xl710-ethip6ip6-ip6base-srv6enc1sid-mrr
    40ge2p1xl710-ethip6srhip6-ip6base-srv6enc2sids-mrr
    40ge2p1xl710-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
    40ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
    40ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-masq-mrr
    40ge2p1xl710-ethip6srhip6-ip6base-srv6proxy-stat-mrr

### 3n-tsh-x520

#### 78b-?t?c-srv6-ip6routing-base-ixgbe
    10ge2p1x520-ethip6ip6-ip6base-srv6enc1sid-mrr
    10ge2p1x520-ethip6srhip6-ip6base-srv6enc2sids-mrr
    10ge2p1x520-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
    10ge2p1x520-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
    10ge2p1x520-ethip6srhip6-ip6base-srv6proxy-masq-mrr
    10ge2p1x520-ethip6srhip6-ip6base-srv6proxy-stat-mrr

### 3n-dnv-x553

#### 78b-?t?c-srv6-ip6routing-base-ixgbe
    10ge2p1x553-ethip6ip6-ip6base-srv6enc1sid-mrr
    10ge2p1x553-ethip6srhip6-ip6base-srv6enc2sids-mrr
    10ge2p1x553-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
    10ge2p1x553-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
    10ge2p1x553-ethip6srhip6-ip6base-srv6proxy-masq-mrr
    10ge2p1x553-ethip6srhip6-ip6base-srv6proxy-stat-mrr

## IPv4 Tunnels

### 3n-skx-xxv710

#### 64b-?t?c-ip4tunnel-base-scale-i40e
    25ge2p1xxv710-ethip4vxlan-l2xcbase-mrr
    25ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-mrr
    25ge2p1xxv710-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
    25ge2p1xxv710-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr

### 3n-hsw-xl710

#### 64b-?t?c-ip4tunnel-base-i40e
    40ge2p1xl710-ethip4vxlan-l2xcbase-mrrjaja
    40ge2p1xl710-ethip4vxlan-l2bdbasemaclrn-mrr

### 3n-tsh-x520

#### 64b-?t?c-ip4tunnel-base-scale-ixgbe
    10ge2p1x520-ethip4vxlan-l2xcbase-mrr
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-mrr
    10ge2p1x520-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
    10ge2p1x520-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr

### 3n-dnv-x553

#### 64b-?t?c-ip4tunnel-base-scale-ixgbe
    10ge2p1x553-ethip4vxlan-l2xcbase-mrr
    10ge2p1x553-ethip4vxlan-l2bdbasemaclrn-mrr
    10ge2p1x553-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
    10ge2p1x553-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr

## KVM VMs vhost-user

### 2n-skx-xxv710

#### 64b-?t?c-vhost-base-i40e-testpmd
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-vhost-base-i40e-vpp
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-vppl2xc-mrr

### 3n-skx-xxv710

#### 64b-?t?c-vhost-base-i40e-testpmd
    25ge2p1xxv710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-vhost-base-i40e-vpp
    25ge2p1xxv710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-vppl2xc-mrr

#### 64b-?t?c-link-bonding-vhost-base-i40e-testpmd
    25ge2p1xxv710-1lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-link-bonding-vhost-base-i40e-vpp
    25ge2p1xxv710-1lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr

### 3n-skx-x710

#### 64b-?t?c-link-bonding-vhost-base-i40e-testpmd
    10ge2p1x710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x710-1lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x710-2lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x710-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x710-2lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-link-bonding-vhost-base-i40e-vpp
    10ge2p1x710-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    10ge2p1x710-1lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    10ge2p1x710-2lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    10ge2p1x710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    10ge2p1x710-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    10ge2p1x710-2lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr

### 3n-hsw-xl710

#### 64b-?t?c-vhost-base-i40e-testpmd
    40ge2p1xl710-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    40ge2p1xl710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    40ge2p1xl710-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-vhost-base-i40e-vpp
    40ge2p1xl710-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    40ge2p1xl710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    40ge2p1xl710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    40ge2p1xl710-ethip4-ip4base-eth-2vhostvr1024-1vm-vppl2xc-mrr

### 3n-tsh-x520

#### 64b-?t?c-vhost-base-ixgbe
    10ge2p1x520-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-link-bonding-vhost-base-ixgbe
    10ge2p1x520-1lbvpplacp-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-1lbvpplacp-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr

### 2n-clx-xxv710

#### 64b-?t?c-vhost-base-i40e-testpmd
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr

#### 64b-?t?c-vhost-base-i40e-vpp
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2vhostvr1024-1vm-vppl2xc-mrr

## LXC/DRC Container Memif

### 2n-skx-xxv710

#### 64b-?t?c-memif-base-i40e
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2memif-1dcr-mrr

### 3n-skx-xxv710

#### 64b-?t?c-memif-base-i40e
    25ge2p1xxv710-eth-l2xcbase-eth-2memif-1lxc-mrr
    25ge2p1xxv710-eth-l2xcbase-eth-2memif-1dcr-mrr
    25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2memif-1lxc-mrr
    25ge2p1xxv710-ethip4-ip4base-eth-2memif-1dcr-mrr

### 3n-tsh-x520

#### 64b-?t?c-memif-base-ixgbe
    10ge2p1x520-eth-l2xcbase-eth-2memif-1lxc-mrr
    10ge2p1x520-eth-l2xcbase-eth-2memif-1dcr-mrr
    10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    10ge2p1x520-eth-l2bdbasemaclrn-eth-2memif-1lxc-mrr
    10ge2p1x520-ethip4-ip4base-eth-2memif-1dcr-mrr

### 2n-clx-xxv710

#### 64b-?t?c-memif-base-i40e
    2n1l-25ge2p1xxv710-eth-l2xcbase-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-eth-l2bdbasemaclrn-eth-2memif-1dcr-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-eth-2memif-1dcr-mrr

## IPsec with IPv4 Routing

### 3n-skx-xxv710

#### imix-?t?c-ipsec-ip4routing-base-scale-sw-i40e
    25ge2p1xxv710-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
    25ge2p1xxv710-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    25ge2p1xxv710-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
    25ge2p1xxv710-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    25ge2p1xxv710-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
    25ge2p1xxv710-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr

### 3n-hsw-xl710

#### imix-?t?c-ipsec-ip4routing-base-scale-sw-i40e
    40ge2p1xl710-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
    40ge2p1xl710-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    40ge2p1xl710-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
    40ge2p1xl710-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    40ge2p1xl710-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
    40ge2p1xl710-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr

#### imix-?t?c-ipsec-ip4routing-base-scale-hw-i40e
    40ge2p1xl710-ethip4ipsec1tnlhw-ip4base-int-aes256gcm-mrr
    40ge2p1xl710-ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha-mrr
    40ge2p1xl710-ethip4ipsec1000tnlhw-ip4base-int-aes256gcm-mrr
    40ge2p1xl710-ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha-mrr

### 3n-tsh-x520

#### imix-?t?c-ipsec-ip4routing-base-scale-sw-ixgbe
    10ge2p1x520-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x520-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    10ge2p1x520-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x520-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    10ge2p1x520-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x520-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr

### 3n-dnv-x553

#### imix-?t?c-ipsec-ip4routing-base-scale-sw-ixgbe
    10ge2p1x553-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x553-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    10ge2p1x553-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x553-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
    10ge2p1x553-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
    10ge2p1x553-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr

## Virtual Topology System

### 3n-skx-xxv710

#### 114b-?t?c-vts-l2switching-base-i40e
    25ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm-mrr
    25ge2p1xxv710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm-mrr

### 3n-hsw-xl710

#### 114b-?t?c-vts-l2switching-base-i40e
    40ge2p1xl710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm-mrr
    40ge2p1xl710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm-mrr
    40ge2p1xl710-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm-mrr

### 3n-tsh-x520

#### 114b-?t?c-vts-l2switching-base-ixgbe
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm-mrr
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm-mrr
    10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm-mrr

## NF Service Density

### VNF Service Chains

####  2n-skx-xxv710

##### imix-?t?c-vhost-chains-i40e
    2n-25ge2p1xxv710-eth-l2bd-10ch-20vh-10vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-10ch-40vh-20vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-12vh-6vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-16vh-8vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-20vh-10vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-2vh-1vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-4vh-2vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-8vh-4vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-16vh-8vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-24vh-12vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-32vh-16vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-40vh-20vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-4vh-2vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-8vh-4vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-16vh-8vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-32vh-16vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-48vh-24vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-8vh-4vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-12vh-6vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-24vh-12vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-48vh-24vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8ch-16vh-8vm1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8ch-32vh-16vm1t-vppip4-mrr

### CNF Service Chains

#### 2n-skx-xxv710

##### imix-?t?c-memif-chains-i40e
    2n-25ge2p1xxv710-eth-l2bd-10ch-20mif-10dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-10ch-40mif-20dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-12mif-6dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-16mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-20mif-10dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-2mif-1dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-4mif-2dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1ch-8mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-16mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-24mif-12dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-32mif-16dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-40mif-20dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-4mif-2dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2ch-8mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-16mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-32mif-16dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-48mif-24dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4ch-8mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-12mif-6dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-24mif-12dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6ch-48mif-24dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8ch-16mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8ch-32mif-16dcr1t-vppip4-mrr

### CNF Service Pipelines

#### 2n-skx-xxv710

##### imix-?t?c-memif-pipelines-i40e
    2n-25ge2p1xxv710-eth-l2bd-10pl-20mif-10dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-10pl-20mif-20dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-10dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-1dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-2dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-6dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-1pl-2mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-12dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-16dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-20dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-2dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-4mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-2pl-8mif-4dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4pl-8mif-16dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4pl-8mif-24dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-4pl-8mif-8dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6pl-12mif-12dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6pl-12mif-24dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-6pl-12mif-6dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8pl-16mif-16dcr1t-vppip4-mrr
    2n-25ge2p1xxv710-eth-l2bd-8pl-16mif-8dcr1t-vppip4-mrr

## DPDK

### 2n-skx-xxv710

#### 64b-?t?c-testpmd-l3fwd
    2n1l-25ge2p1xxv710-eth-l2xcbase-testpmd-mrr
    2n1l-25ge2p1xxv710-ethip4-ip4base-l3fwd-mrr

### 2n-skx-x710

#### 64b-?t?c-testpmd-l3fwd
    2n1l-10ge2p1x710-eth-l2xcbase-testpmd-mrr
    2n1l-10ge2p1x710-ethip4-ip4base-l3fwd-mrr

### 3n-skx-xxv710

#### 64b-?t?c-testpmd-l3fwd
    25ge2p1xxv710-eth-l2xcbase-testpmd-mrr
    25ge2p1xxv710-ethip4-ip4base-l3fwd-mrr

### 3n-skx-x710

#### 64b-?t?c-testpmd-l3fwd
    10ge2p1x710-eth-l2xcbase-testpmd-mrr
    10ge2p1x710-ethip4-ip4base-l3fwd-mrr

### 3n-hsw-xl710

#### 64b-?t?c-testpmd-l3fwd
    40ge2p1xl710-eth-l2xcbase-testpmd-mrr
    40ge2p1xl710-ethip4-ip4base-l3fwd-mrr

### 3n-hsw-x710

#### 64b-?t?c-testpmd-l3fwd
    10ge2p1x710-eth-l2xcbase-testpmd-mrr
    10ge2p1x710-ethip4-ip4base-l3fwd-mrr

[Trending web page]: https://docs.fd.io/csit/master/trending/index.html
[2n-skx]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-2n-skx/
[3n-skx]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-3n-skx/
[3n-hsw]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master/
[3n-tsh]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-3n-tsh/
[2n-dnv]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-2n-dnv/
[3n-dnv]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-3n-dnv/
[2n-clx]: https://jenkins.fd.io/view/csit/job/csit-vpp-perf-mrr-daily-master-2n-clx/
[Performance Tests Job Specifications, chapter NICs]: https://github.com/FDio/csit/blob/master/docs/job_specs/perf_tests_job_specs.md#nics
[Performance Tests Job Specifications, chapter Frame Sizes]: https://github.com/FDio/csit/blob/master/docs/job_specs/perf_tests_job_specs.md#frame-sizes
[Performance Tests Job Specifications, chapter Processor Cores]: https://github.com/FDio/csit/blob/master/docs/job_specs/perf_tests_job_specs.md#processor-cores
[Jobs specifications]: https://github.com/FDio/csit/tree/master/docs/job_specs

# END OF DOCUMENT
