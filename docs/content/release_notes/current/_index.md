---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2506"
weight: 1
---

# CSIT-2506 Release Report

This section includes release notes for FD.io CSIT-2506. The CSIT report
will be published on **Jul-09 2025**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2506_plan) pages.

The release notes of the previous CSIT release can be found
[here]({{< relref "../previous/csit_rls2502" >}}).

## CSIT-2506 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

## CSIT-2506 Release Data

To access CSIT-2506 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2506`
  - `DUT` > `vpp`
  - `DUT Version` > `25.06-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v25.06 vs v25.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2502-25.02-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2506-25.06-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2506`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2506`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2506 Selected Performance Tests

CSIT-2506 VPP v25.06 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstuwjAQ_Jr0grayF5v0wqGQ_6hcZylRQ3BtNyr9-hqEtImgEpWgXHzwSzPWjnc0kkPcenoJ1M4LvSjKRYFlU6epmD5P0uLbgFrMoHcOUD-mnaeWTCDADhr7BVKIN0In6UkK-wGmX0HjFMzUK0gLFNf7UxrBmpZQvIPvauhqvy-By2OJk3qM1p-R0aRihPTkGRzJY5pb7wac30Qz33gyfCEpZyhSGIg5_zZmr7zZUGi-ia-krjBuU-MZknZcJ-7cAD02rKwOjH9yyWWX_uaSu51LmLN0uUt4ryxhztK1XLphllTO0uUuqXtlSeUsXcslzpKuHrqt3xz-err6AWX4rr4)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIGynupYek_o-iypvG1HHUlWNIv75KCKxNW0ghaS466MWM2NEOA4r9luklUvtU2GVRLgssmzpNxWxxnxZuI1o1hyEEQPuQdkwtuUiAHcTAoJV6IwyaHrXyH-CGFTTBwNy8gvZA_fpwSiN61xKqd-Cuhq7mQwl8PpX4Vk_QetcLmlRMkIFYwIk8oYX1fsT5TbTwHZOTC0m5QD3FkZif3ybsFbsNxeaT5ErqiuA-NV4g7ad1-n0YoaeGldWR8U8uhezS31wK13MJc5bOdwlvlSXMWbqUS1fMkslZOt8lc6ssmZylS7kkWbLVXbflzfGvZ6svmlavig)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXOYjdcOFDyD2TshUZN08U2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5pG-glUv9YmWXVLCtsOp-X6v7pNv9CH9GoBeyYAc1d3gXqyUYCHCBygFqpd0Ku6aFW7gM8-zV0rGGhX6F2QGl1OOUvOtsTqjWEwcPgw4EDn08cPwgF9Z9J0CxjguwoCDjRJ2W82o9q_lQtDTaQlY4sXaBEcaTm98tJ9VuwG4rdF0lLHovgLo9eoNpNedKeR-hpYk17rPgvn7j4NNMnvqBPWPI0wye8Wp6w5OlsPl0yT7rkaYZP-mp50iVPZ_NJ8mTam2EbNsd3n2m_ARsRtFI)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJYjcnDrT5BzLOQiOc1FqbqOX1uFWlTQQcIrX04kMcW7OrGe9oJIe4Y3oJ5J4KvS7qdYF116aleHy-Tz92AXW5gtF7QP2QdkyOTCDAAYJnwLJ8J_SV3dcjmQi922vovIKVeoXKAsXt8ZS-YI0jLD-AhxaGlo8kuDmT_GAUtP2MgiYdM2QkFnAmUMr89jCp-Vu2dBgmIy1Ju0CRwkTO77eT6jc2PYXui6QlzUVwm4YvUGXnPPHgJ-h5ZHVzqvg3p3x2aqlT_ppOYc7UEqfwdpnCnKnLOXXVTKmcqSVOqdtlSuVMXc4pyZRu7oYd96c3oG6-ARUBvkI)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl01qwzAQhU_jbsoUaxLZ3XTR1PcoqjRtTBxFSEogPX1lExibtKWBpMlCC__xnpnxfDwGh7jx9BqoeyrkoqgXBdatSadi9nyfLr4LKMsKds4Byod056kjFQjQgq5aC1iWHyScIKvAOLOC1s1BSPH4BkIDxWX_nI6gVUdYrsBbA9b4vga-HGocFWTVbCOrqY2JsiPP4qQ_trnlfuT5oWu2K0-K_alxliKFUS_ffxq7371aU2g_iV8ZxsIOnUY_EvW0Uty7kXqYWN0Mjv_i5DKnEzm5C3LCnKcTOOHV8oQ5T2fjdJk8VfO8nY4opaHc0m76nZHLjG5gL_WM8lb6OyO8Uo7yRjoXI86RbO7sxq-H_ybZfAFeaZNp)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl01uwjAQhU-Tbqqp4gGTbrqA5h7ItacQEYxlu0j09HUipElEWxUJCgsv8qf3opnMp6dRQtx5WgZqXwq5KKpFgVVj0qmYzB_TxbcBZTmDvXOA8indeWpJBQK0oKuVBVGWKxJOkFVgnNlA46YgpHh-A6GB4rp7TkfQqiUsN-CtAWt8VwNfjzVOCrJqPiKrqY2RsifP4qg_trn1YeD5oWu2K0-K_alxliKFQS_ffxq7373aUmg-iV_px8IOnUY_EPW4Ujy4gXqcWFX3jv_i5DKnMzm5K3LCnKczOOHN8oQ5TxfjdJ08zaZ5O51QSkO5p930OyOXGd3BXuoY5a30d0Z4oxzljXQpRpwjWT_Ynd_2_02y_gKBypNJ)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsJW564dCS_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0UZllUywKrtklTcb-4TQt3AY2aweA9oLlLO6aObCDAHlr3AVqpF0Kvaa6VewM7rKD1M6jmz6AdUFzvT2kEZztC9QrcN9A3vC-Bj8cS3-oJ2rxHQZOKCTIQCziRJzS_3o04v4kWvmWyciEpFyhSGIn5-W3CXrHdUGg_Sa6krgjuUuMF0m5aJ-78CD02rKoPjH9yyWeX_uaSv5xLmLN0ukt4rSxhztK5XLpglsqcpdNdKq-VpTJn6VwuSZZMfdNveXP465n6C_3Kr0I)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIGyvOpYcm_o-iypvG1HHUlWpIv75KCKxNW0ghaS466MWM2NEOAwpxx_QcqHsszLKolgVWbZOmYvZ0nxbuAho1h8F7QPOQdkwd2UCAPQTPoJV6JfSaFlq5d7DDGlo_h2rxAtoBxc3hlEZwtiNUb8B9A33DhxK4OpX4Vk_Q5iMKmlRMkIFYwIk8ofnNfsT5TbTwLZOVC0m5QJHCSMzPbxP2mu2WQvtJciV1RXCXGi-QdtM6ce9H6KlhVX1k_JNLPrv0N5f89VzCnKXzXcJbZQlzli7l0hWzVOYsne9SeasslTlLl3JJsmTqu37H2-Nfz9RfMjewDg)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFuwjAQfE16qbayTUy49ADNPyrX3paIELZrg0RfX4OQNlHbQyQolxzi2JpdzXhHIzmmHeNrxPa5sKuiWhWmakJeitnyMf-4jcaqORyIwNinvGNs0UUE00EkBq3UBxrSuNDKf0KgsIGG5lAt3kB7wLQ-nfIXvWvRqA1wF6ALfOIwLxeOH4SChn0SNMsYIAdkAQf6pIzWx17Nn6qlwTE66cjSBUoYe2p-v5xUv7PbYmy-UFryWAT3efQCaT_kSUfqoZeJVfW54r98osmnkT7RDX0yU55G-GTulicz5elqPt0yT-WUpxE-lXfLUznl6Wo-SZ5s_dDteHt-99n6G7W5tNY)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJEtdcOFDyD2SchUY4qbU2UcvrcatKmwg4RGrpxYc4tmZXM97RSA5xy_QSyD0Wal3odYG6a9NS3D_dph-7gKpcweg9oLpLOyZHJhDgAMEzYFm-E_rK7vRIJkLvdgo6vwL98AqVBYqbwyl9wRpHWH4ADy0MLR9I8PlE8oNR0PYzCpp0zJCRWMCZQCnzm_2k5m_Z0mGYjLQk7QJFChM5v99Oqt_Y9BS6L5KWNBfBbRq-QJWd88S9n6CnkenmWPFvTvns1FKn_CWdwpypJU7h9TKFOVPnc-qimapzppY4VV8vU3XO1Pmckkyp5mbYcn98A6rmG7J_vsY)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYW2T10kNT_0dRpW1j4ihCUgPp11cxgbVJCw3YTQ86-MWM2fEOw-CYdoFeIvWPlVxValWh6mw-VfdPt_kS-oiybmDvPaC8y3eBetKRAB2YpnOAdf1OwgtyGqy3G-h8A0KKh1cQBiitj8_5iEb3hPUGgrPgbDjOwOfTjLOBjNqPxGiWMUH2FBic6GOaXx9GnB9UM10H0szPwhlKFEdavv80Zr8FvaXYfRK_MqyFGSavfgSa6aR08CP0tDHVDoy_8skXny70yS_oE5Y8XeATXi1PWPI0m0_L5EmVdjp3Sf2vblKlmWb0aLkclVb6vUd4pRyVRprLI86RbG_cLmyH_ybZfgFm8pPx)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYWxT10kMT_0dRpW1i4ihCUgPp11cxgbVJCw3YTQ86-MWM2fEOw-CY9oFeI3XPlVxWalmham0-VY8v9_kSuoiyXsDBe0D5kO8CdaQjATowau1A1PWahBfkNFhvt9D6BQgpnt5AGKC0OT3nIxrdEdZbCM6Cs-E0A1fnGRcDGbUfidEsY4QcKDA40sc0vzkOOD-oZroOpJmfhTOUKA60fP9pzH4Pekex_SR-pV8LM0xe_QA040np6AfoeWOq6Rl_5ZMvPl3pk5_RJyx5usInvFmesORpMp_myZMq7XTpkvpf3aRKM03o0Xw5Kq30e4_wRjkqjTSVR5wj2dy5fdj1_02y-QKKU5PR)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ7DpNNyxacg_kOtPWUj7GNqHh9DihkhshJEB1wsKbfDTjzNhPTxrF2Fbjs8HqMcl2Sb5LaC5Ld0lW23t305WhWbqGTimg2YN70lghNwirBqQ4A0nTI1JFcENS8QK8O4DQvbItkIxs9kAEoD1JxaQyKFhqm8q8gXvfDx-RjQWOrsT6KGpoSj1Upk-Xyl_a8NHy1fqoa24S6VD74KRrn6ZOvc_5di8-n2vkfsHnFn3Uornq56cb9usPmtdo5Dv6j4zH5zOEw3QVFNPatldX0cs55sWYsSxTFZnehKkKzJRGTwMwpYt6SqOnszMN7SmLngZgyhb1lEVPZ2cazlNZy3Mce_-KdDi9_zb1_ppolPQmRAM7GkfeAETpko7GgXd2ooEdjeNuAKJsSUfjsDs7Ue9oVtw1ra7Hf71Z8QF2Biye)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ7NpNNywouQdKnaG1yMfYpjScHidUciKEBKhOuvAmH804M_bTk0YxttX4ZLC6T_g2ybYJzWTpLsnq4dbddGUoT9dwVAoov3NPGissDMKqASlOQNJ0j1QR3JBUvEKpyhcQulO2BcLJZgdEANqDVEwqg4KltqnMO7j3Xf8V2Vgo0NVY70UNTan70vTxXPpbHz5avlkfdd1NIkfUPjhp26epQ-dzft6MX1BoLPyKrz36qEUzaui3O_brn3VRo5Ef6D8ynJ_PEA7UKCimtW2nRtHzQWb5kLEwVRWpXoaqCk2VRldDUKXLukqjq_NTDe4qi66GoMqWdZVFV-enGtBVWctTHIH_DbU_vqubgP_MNIp6GaahPY3jbwimdFFP4_A7P9PQnsbRNwRTtqincfCdn6n3lOc3Tavr4R8wzz8Brco2Lg)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OhDAQgJ8GL2YM7ZbdvXhw5T1MKbO7TfipbUXx6S24SSHGRM0WPPTCT2bKTPvlSyYY22p8MljdJ9kh2R0SupOluySbh1t305WhWbqFTimg2Z170lghNwibpgCjNJA0PSFVBPckFc_AuyMI3SvbAsnIvgAiAO1ZKiaVQcFS21TmFdx7MXxFNhY4uhrbk6ihKfVQmj5eSn_pw0fLF-ujrrtZpEPtg7O2fZo69z7n-834BVwj9ys-9-ijFs2koZ_u2K8_al6jke_oPzKen88QDtQkKOa1ba8m0ctB7vIxY2WqKlK9DlUVmiqNroagStd1lUZXl6ca3FUWXQ1Bla3rKouuLk81oKuylm9xBP4z1OH4_t0E_GumUdTrMA3taRx_QzClq3oah9_lmYb2NI6-IZiyVT2Ng-_yTL2nWX7TtLoe_wFn-Qe3Ojdm)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1KxDAQgJ-mXmSkzSZbLx527XtINh13A_0JSaytT29aF9JFEMWN8ZBLf5hJZ5KPD4Ya22t8Mtg8ZGyflfuMlLJ2l2yzu3U33RjC8i0MSgFhd-5JY4PcIGw6DkZpIHl-RKIKMZYDcgttMzIQelK2h4IV9wcoBKA9SUWlMihobrvGvIJ7P8zfkZ0Fjq7K9iha6Go9FyeP5-KfOvHR-sX6qOvvIjKg9sGLxn2aOk0-56vt-CVcI_drPnbpoxbNqqXv7tmvf9a8RSPf0H9kOUGfIRysVVBc1raTWkXPR1lWS0Z0siqRvRZZFZ4sSc6GIUtiO0uSszHI_oGzNDkbhiyN7SxNzsYgG9RZ2coxjca_ADsf4D-cjH_MNQl7La7hfU1jcRiuJLKvaSiOwTW8r2kkDsOVRvY1DcQxuHpfWXXT9bpd_hmz6h2NsFS-)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctuwjAQ_Jr0Um1lG9xw6QGa_6gce9tYBGK8DoJ-fU2EuolarhzIxbY0M_sarUypi_hB2L4VelOUm0KV3uWjWKyf8xVbUlq8wjEEUPolvyK2aAhhsQdvTyCF-EIVJK6ksAdwwW2h6ShRMnYLUq1EDdICpgZ8WPYuHHpv60uAHBJt00Ed6JJPvV_z_UnOqOsTo1k_QY4YGZzUyrTQnJlzuwMWmIiGFb-NMSEhjWq63SYrPqPZIflvZNkwJmbYbMkItNNs6RxG6HV6ZTUw7uQfWdNi5rdS0Ax8_K_dB_VzXnY-spvzWs4776aunvZd3A1_pq5-AD91Cfg)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCUuJeemjqf1QYb2tUHFMWR05fX2JFXVttrjk4F0CaGWZ3RwhKfcQ3Qv9c6F1R7gpVuiYvxeblPm_Rk9JiC4cQQOmHfIro0RDCZg_OjiCF-EAVpB23zQidHzW0PSVKxn6CVE-iBmkBUwsuPA5N-BqcrU_6fCPatoc60MlOvZ7t_ngz2gyJ0axfIAeMDC5KZVpoj8y52ADzTUTDgt--mJCQZiVd7pIV79F0SO4bWTZNiRk2BzID7dItHcMMPQ-vrCbGddIjazxKYb0UtP4U_-t2nWneVJgrzvKmHuaV36Wu7vZ97Ka_Ulc_f4YJ6A)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctugzAQ_Bp6qbaynTr00kMS_qMyZltQTXC8BiX9-jooyoL6OOYQLralmdnXaGWKXcA3Qvea6W2WbzOVN1U6stXmMV3BkdJiDYP3oPRTegV0aAhhtTdAPoAS4gOVl_aYD2gitO6ooe4oUjT2E6R6ESVICxhraPxzX_lD39jyHCIFRVt3UHo6Z1S7S8Yf6Rmt-sho0s-QAQODs2qZ5usTc_7rgSUmoGHNtTUmRKRJVX83yor3YFqk5gtZNg6KGTbZMgHtPFs8-Ql6mV9ejIybeUjWOJTCOiloEV7-1vDdero0S-_b0aUt6Y13VBcP-y604x-qi2-nMBQo)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCHOJeemjqf1QYNrUVElOWRE1fX2JFXVtVmlN7iC-AmBl2hxGCUh_xldA_FXpVVKtCVZ3LQ1E-3-cpelJaLOEQAij9kFcRPRpCKHfQ2Q-QQryhChIfpbDv4ILbQNtTomTsBuRiKRqQFjC10IVFsqE5ib0L-ZzeuLyJcV1CE-hUVL2ci_7ogFG3T4zmvibIASODk4aZFtojcy7bYIGJaFjx7Y4JCWnU0xWvLFtHs0XqPpG1w4Uxw-ZwRqCdlkzHMELPV1jVA-MfkiRrPErrpaC5BPqb5dvIde_m80Iveb2ZJOf2Qq9Y_vtcdX236-N2-Et1_QVm_BE-)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVcFuwyAM_ZrsMnkKpCSnHdblPyYC7hKNNAjTKt3Xj0bVnGjqeuqluQDiPWM_P1lQHAJ-ELrXTG2zapvJqrNpyYq357QFR1LlJRy9B6le0imgQ00IxR46M4LI80-UXpixtCP0blTQDhQpavMFYlPmDQgDGFvo_CYa35xjnfXpmUHbdIlhV0Dj6ZxTvl9y_imAUXuIjKayFsgRA4OLepnm2xNzrqpgvg6oOeBXHBMi0qykG1I5bBd0j9R9I8dO_WKGSdbMQLNMGU9-hl46WNUT4_4-ktEOhXEip5XY-Z_ih3D1YFczndekPoqPK5vOG4rv76qqn_ZD6Kc_VNU_iMYRLg)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCO4576SGp_1Fh2NRWSLxlSaT09SVW1LVVNTm1h_gCiJlhdxghOPYB3xj9S1aus2qd5VXn0pAVq8c0Bc95qZZwJIK8fEqrgB4NIxT7BpgCaKXeMSeNz1rZD3DkttD2HDkauwW9WKoGtAWMLXS0iJaas9o7Sgf1xqVNDJsCGuJz1fz1UvVHC4K6QxQ0NTZBjhgEnHQsNGpPwrniQxQmoBHJtz0hRORRUzfMimwTzA65-0TRDjcmDJviGYF2WjKeaIRe7rCqB8Z_ZMnWeNTWa8WzifSa5ztJ9uBm9Ep_M3s_Wc7uld7w_PfJlvXDvg-74U8t6y9uthTW)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbbCOMSnHpr6HxWGTW0Vx4glVpLXh1hR11bV5NQe4gsgZobdYYSg2Af8IHSvmdpk5SaTZWvTkBVvz2kKjqQSaxi8B6le0iqgQ00IxU4D-QBSiE-UPjeHckAdoXMHBU1PkaI2X5Cv1qKG3ADGBlq_isbXF7mzPp3Ua5s2MWwLqD1dysr3a9kfPTBq95HR1NkMGTAwOGuZab45MueWEZbogJo13_6YEJEmXd1xy7Jt0B1Se0LWjlfGDJMCmoBmXjIe_QS9XmJZjYx_SZOMdpgblwtaTqi3TD9Ktnu7pJf6m9sHSnN5L_WO6b_PVlVPuz5049-qqjOEFBtu)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiX70kNS_0dQ5E1tcJytpJikX18pDcimGAotLYRc9JpZ7Y6GRc4fLG4c9s-ZXGflOhNl14Qhy1ePYbK9E5IpGIlAyKewstijdghigM6cgDP2ioI4VpyZN9DjDjoq4vEWuAH0bdh6Q_F0G-NazkQBpHJwqpBcgKejh6GxMal4uSb9UkFCm6NPaKhrhoxoEzgrONGoPU84SzISX1vUKSDoSJBHNynmm2JT-M7qPbruHdMd8eESwQRzJpiZZ_ZnmqDXJyzrC-PfnKS7kz91kv7cSSVlrj7VFVxUpapuuy0X9N5MZy75SXc_f7U_Zf0wHOz-8nfK-gPvmfU7)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYsiT70kNS_0dR5U1tcJytpBjSr6-cBtamGAotLYRc9JqRdmeHRSEePD4H7B8zvc3KbSbLrklDVmzu0-T7IHVuYCQCqR_SymOPNiDIAQJ5EHn-ipIEViJ3b2DHHXSkpuMXEA4wtmkbHcFgo1LYQCtyqYBMAcEoLSREOkYYGj8FlU-XoF8yYLQ5RkZTXgtkRM_gImGmUXuacdZkMN96tHwhyWEoYpgl802xfH3n7R5D9478xlQ4Jrhkzgxzy8jxRDP0UsKyPjP-zUm6OflTJ-nPnTRaF-ZTnRKyKk113W25ovdqOnPNT7r5-av9qeu74eD3579T1x8FXvQj)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRGWEhYkIlLnLp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAGgdO6z)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsh659JDU_1FUeVsbbGeRFJPk66OkAdkUQ6GFQMhFD2ZXO7PDohC3Ht8Ddq-F2hRmUwjT1mkpyvVz2nwXhGIaRiIQ6iWdPHZoA4IYIJAHwdgXCuJub0a0Efpur6AlCZyxD-AOMDbpGh3BYKOUWEPDmZBAuoSgpeICIu0iDLU_lxVv17I_OGS03sWMJmYzZESfwRnlHEbNYRKzLCRnWI82pyRBGYoYJnR-KTenf3rbY2iPmN84ty4HuGTQBHPzyvFAE_TaRFNdIm7oJj3c_LubdAM3tVKl_tYnuVgZvbr38VxQfEcTuuQpPTz95zlV1dOw9f3lL1XVCW9t_fM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVsFqwzAM_Zr0MlRir0522WFd_qO4jtoGUleznbDu6-uUgJKOwQ6FQtKLbfyeLMmPh-3DyeHGY_2eqHWSrxOZV2UcktePlzi52kuVZtASgVTLuHJYo_YI0kJlvkGk6R4lCXwTqfkC3e6gotUmNNZi7SFbbUEYwHCIu9DPTUl7tNgiiCwSu4Btd6QtXZdZfvaZf5XBaNkERmNxI6RFx-CoaqbR4Tzg_NUL87VDzQGDFpkS0A-K-lfLHLxz-oi--kE-Id4d4ybKxJAw47ThTAO0v8e8uDIeqyk9Nb2LpvRYTedn06m7dH4mnbhHpZrfYzrueYo-vVGVnqre26uqWNiTO17_v6q4AK3cG6E)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtls2OwiAUhZ-ms5lc0yK0KxejfQ9T6R1tQpEAdeo8vdSY3DYzLjT-bNiUhnPgXvhyEpzfW1w7VItELJNimbCiqcMnmX99hsEqx0Saw8EYYGIW_iwqrBzCXEMje8jSdIvMZLLP6x5a1QtoDF_7TmtUDnK-gUwC-l2Y3XrTuZ9B3ww76NoOhdjqUuhPVVLrzpMaepkoB7QkTpokm9kdyXO1dfJXFitaMDoRWTy6UVP_nZC837Zq0TW_SAvCzZAuAwSSMjmt4o9mpF6urSjPjpcSM5HYPcTM84mxmLHbiLF3Z4zFjD2S2AsyxmPGbiPG350xHjP2SGKUMVF-6L1tz29GUZ4AmhDcTg)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFqwzAM_ZrsMjQSt25OO6zNfxTH0daA4wjZDWm_fm4XUMLYLj0USi-28dOz9PQQDrFn3Ad075neZuU2U2XbpCVbfbymjV1QOt_AQARKv6UTo0MTEFbeQCAGledfqKiwYzmgidC5UUNL6308eo8uwGZdQ2EB4yHdDqMzHpyqmzo90hnr2INv-JJR7aaMv9IL2hyjoKmoBTIgC7ioVsLocJKY_zQIxTAa4cykSUjEMKvrb6nC-GTTYWjPKLTUKMFtskWgwi5zxRPN0Kl_ZXWNuI-H9PTwJg_pPh6O9iLswSfwR-RDzd7kGz19u3nedPXie-6u_5-uvgGMyv37)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFqwzAQRU_jbsoUW5HiVRdNfY-g2NPEICuDJLtJT185BMampZASTBbaWMb_j2ekxwf5cHS49WheM7XJyk0myraJj2z19hwXZ7xQ-RoGIhDqJb45NKg9wspq8ORA5PkeBRX1qRxQB-jMSUFLcht6a9F4WMsdFDVgOMSv-0C9_xz13fgT27ixl3i_9vrRmNWmD6zGcWbKgI7F2Zxso8OZPX9NzyXaoeaayabYEtBP5vptk-z9cLpD334hF8TDYb2OKFgq6nmXcKaJej25sro4luZGids_udEi3ETK283cxAPkTaS83ZnbMnmTKW83c5MPkDeZ8nZnbpw3VT3Zo-su90pVfQOnxeuu)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVl1rwyAU_TXZy3ConYsve2iX_1FsctcGjJWrSdv9-plQuAmD7WWsUPei4jnX-3E4YIhHhG0A-1qoTVFuClm2TVqK1foxbWiDVPyFDd4zqZ7SCcGCCcBWzrDgkUnO9yC9qM_lACayzp4Va_3zNvbOgQ1MKKF3TNQM4iHd940_tQj73mAjOI_OhtPI342PugbH3PLtmvtLIYQ2fSQ0lbdABkACF3UTzR8uxPmuGwoxCIZiZk0SJUKY1fVzyxT5jqaD0H4AhU-jI0adpJqB9TJrvPgZep1kWU2MW-vq_3X9JV39TXXNzq0ZeDU7p96_T3VuPtX371Odm0_1H_tUVQ_uiN30D1bVJ9FVK90)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVstuwyAQ_Br3Um1liIlz6SGp_yOy8TZB9WMLJK379SVupLVV9VLJiQ--AGKGZZbRSDjfWtw7rJ4jtYvSXSRTU4YhWm0fw2QrJ1W8hjMRSPUUVhYrzB3CqgGjP0HE8QElCdyIWL9DSeUbaNuRb0EosSlAaEB_NJQYcqgDPfZN5T4g7BSXOqbxkGO4ZX3QdaieO4d1UXXQlPaiQ75cdfwSxWh58owGqSPkjJbBUQ9Mo2PHnL874wN5EMonfhpm1KMbCPpX-1zs1eY1OvOFXLF_WWboYOEA1GMhvqMBen3VNOsZc_KbFr8n8Jum9lsu-b6t3_K--ZZLvufk9-T5TpZ839bv5L75TpZ8z8lvzrfKHprW1v0_XWXf2KNU7Q)

## CSIT-2506 Selected Performance Comparisons

Comparisons v25.06 vs v25.02

- [2n-icx 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkNEOgiAUhp_GbpxNKbSbLjIfoLVegNGxsSnQAV319IFaaFdtDPjP-Q7n8BtogFu47qOijEiBUAOC5ODu0eYQj1EDdtIX7FzqGA9BXymUXKDX7oO6o9fai5F3mR4wJLExhKYkIXTtdnSvMQMBF7JGFmgiE8EfSZamNyA6g12W8nvC-jpUcIXfsamfJTt6SaspX2NrxGuJ5NtywVj71EviVJ0nohjWp1erGf7hkqNYC3b-8WDEiPSs6eDXl3zwJZ_7MvRfSYXt3o9Gq5XqbCMAzaTfZIZ57w)

## CSIT-2506 Selected Performance Coverage Data

CSIT-2506 VPP v25.06 coverage data

- [2n-emr 100ge e810cq avf ip4](https://csit.fd.io/coverage/#eNpVjkEOwiAQRU-DG4MZqBQ3Xai9hyE42iZIESimt7cTF9TNJP_9N5NJ6NDmcfId0xcmdXRpnaw5739BKmgJyCuB-5xrW0L4awrGWkp1gJbH9bpJWLUwLBvHc3xFLgCeKIPAkwD75qY8qm8imrowhiMF3e_SMH1uzmT0dumYos-3iCzVfwGABDxx)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
