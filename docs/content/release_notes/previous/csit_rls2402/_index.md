---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2402"
weight: 1
---

# CSIT-2402 Release Report

This section includes release notes for FD.io CSIT-2402. The CSIT report
was published on **Mar-13 2024**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2402_plan) pages.

## CSIT-2402 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})
- [VPP Device]({{< relref "vpp_device" >}})

## CSIT-2402 Release Data

To access CSIT-2402 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2402`
  - `DUT` > `vpp`
  - `DUT Version` > `24.02-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of chioce`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v24.02 vs v23.10
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2402-23.10-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2402-24.02-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2402`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2402`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2402 Selected Performance Tests

CSIT-2402 VPP v24.02 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsrUO4cGjJfyDjbGlEmpq1G1G-HreqtIkAqUgtvfjgl2asHe9oJIe4YXoO1D0W5aKoFgVWbZOmYja_TQt3AY1CGLwHNHdpx9SRDQTYQ-s-QCv1Sug1PWjl3sEOS2i9gXvzAtoBxdX-lEZwtiNUb8B9A33D-xL4dCzxrZ6gzTYKmlRMkIFYwIk8ofnVbsT5TbTwLZOVC0m5QJHCSMzPbxP2ku2aQvtJciV1RXCXGi-QdtM6cedH6LFhVX1g_JNLPrv0N5f85VzCnKXTXcJrZQlzls7l0gWzZHKWTnfJXCtLJmfpXC5Jlsr6pt_w-vDXK-sv2WmuRg)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_BrnUrZIWznupYem_o-iypvG1HHUlWpIv75KCKxNUkghaS466MWM2NEOAwpxw_QaqHsqykVRLQqs2iZNxcPzXVq4C2gUwuA9oLlPO6aObCDAHoJn0Eq9E3pNj1q5T7DDElpvYG7eQDuguNqd0gjOdoTqA7hvoG94VwJfDiWO6gnafEVBk4oJMhALOJEnNL_ajji_iRa-ZbJyISkXKFIYiTn9NmEv2a4ptN8kV1JXBHep8QJpN60Tt36EHhpW1XvGP7nks0t_c8lfzyXMWTrfJbxVljBn6VIuXTFLJmfpfJfMrbJkcpYu5ZJkqaxn_YbX-79eWf8ADdavEg)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEX24hAuHFryD2TshUZN08U2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5pG-glUv9U1cuqWVbYdD4v1f3iNv9CH9EohB0zoLnLu0A92UiAA0QOoJV6J2RNj1q5D_Ds19CxgQfzCtoBpdXhlL_obE-o1hAGD4MPBw58PnH8IBTUfyZBs4wJsqMg4ESflPFqP6r5U7U02EBWOrJ0gRLFkZrfLyfVb8FuKHZfJC15LIK7PHqBtJvypD2P0NPEmvZY8V8-cfFppk98QZ-w5GmGT3i1PGHJ09l8umSeTMnTDJ_M1fJkSp7O5pPkqW5vhm3YHN99dfsNi3az2g)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UjbYG7k-9dDU_xEUeZuYyo5YqSbp11cJgbVpezDkcdHBssTsMqMdBuTDnmntyb5m5SqrVhlWbROXbPn2HH9sPaocYXAOUC3ijsmS9gTYg3cMmOdbQleYQzWQDtDZQwmtU_CiNlAYoLA7neLnjbaE-Sdw30Df8IkE3y8kvxgFbb6CoFHHBBmIBZwIlDK3O45q_pctHZpJS0vULlAgP5Lz9-2k-oN1R779JmmJcxHcxOELVJgpTzi6EXoZWVWfK-7mlEtOzXXK3dIpTJma4xQ-LlOYMnU9p26aKZUyNccp9bhMqZSp6zklmSrrp37P3fkNWNY_glq9yg)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasZo0u9nFurzH8GxtDU1dYaeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7j6TVQ-5SVi6xaZFg1Np6y2fN9vPg2YJEj7JgBi4d456klHQjQgZk3DjDPP0ixIqfBsl1BwwWoUj2-gTJA3bJ_jkcwuiXMV-CdBWd9XwNfDjWOCopqt52osY2JsiMv4qQ_sfFyP_L80LXYtSct_ti4SB2FUS_ff5q4371eU2g-SV4ZxiIOE0c_Es20UrfnkXqYWFUPjv_ixInTiZz4gpww5ekETni1PGHK09k4XSZP8yJtpyNKcSi3tJt-Z8SJ0Q3spZ5R2kp_Z4RXylHaSOdiJDkq6zu38evhv6msvwDzBpLJ)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasZosu9nFurzH8GytDU1dYaeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7j6S1Q-5yV86yaZ1g1Np6y2ct9vPg2YJEj7JgBi4d456klHQjQgakWDlSeL0ixIqfBsl1BwwWoUj29gzJA3bJ_jkcwuiXMV-CdBWd9XwNfDzWOCopqt52osY2JsiMv4qQ_sfFyP_L80LXYtSct_ti4SB2FUS_ff5q4P7xeU2g-SV4ZxiIOE0c_Es20UrfnkXqYWFUPjv_ixInTiZz4gpww5ekETni1PGHK09k4XSZPj0XaTkeU4lBuaTf9zogToxvYSz2jtJX-zgivlKO0kc7FSHJU1ndu49fDf1NZfwEWdpKp)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsrUN64UCb_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0U5aKoFgVWbZOmYvZ4mxbuAhqFMHgPaO7SjqkjGwiwh9Z9gFbqhdBrmmvl3sAOK2j9PVTzZ9AOKK73pzSCsx2hegXuG-gb3pfA5bHEt3qCNu9R0KRiggzEAk7kCc2vdyPOb6KFb5msXEjKBYoURmJ-fpuwV2w3FNpPkiupK4K71HiBtJvWiTs_Qo8Nq-oD459c8tmlv7nkL-cS5iyd7hJeK0uYs3Quly6YJZOzdLpL5lpZMjlL53JJslTWN_2WN4e_Xll_AXFKrso)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIG7nOpYek_o-iypvG1HHUlWJIv75KCKxNW0ghaS466MWM2NEOAwpxy_QSqHsqymVRLQus2iZNxWxxnxbuAhqFMHgPaB7SjqkjGwiwh-AZtFJvhF7TXCv3AXZYQesfoZq_gnZAcX04pRGc7QjVO3DfQN_woQQ-n0p8qydos4uCJhUTZCAWcCJPaH69H3F-Ey18y2TlQlIuUKQwEvPz24S9Yruh0H6SXEldEdylxguk3bRO3PsRempYVR8Z_-SSzy79zSV_PZcwZ-l8l_BWWcKcpUu5dMUsmZyl810yt8qSyVm6lEuSpbK-67e8Of71yvoLpaivlg)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEX24pBeOFDyD2TshUZN08U2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5pG-glUv9Y1cuqWVbYdD4v1f3Tbf6FPqJRCDtmQHOXd4F6spEAB4gcQCv1TsiaFlq5D_Ds19DxAzSLV9AOKK0Op_xFZ3tCtYYweBh8OHDg84njB6Gg_jMJmmVMkB0FASf6pIxX-1HNn6qlwQay0pGlC5QojtT8fjmpfgt2Q7H7ImnJYxHc5dELpN2UJ-15hJ4m1rTHiv_yiYtPM33iC_qEJU8zfMKr5QlLns7m0yXzZEqeZvhkrpYnU_J0Np8kT3V7M2zD5vjuq9tvJi20Xg)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJ4mAuHFryD2SchUY4qbU2UcvrcatKmwg4RGrpxYc4tmZXM97RSA5xy_QSyD0V9brQ6wJ116aluF_dph-7gKpEGL0HVHdpx-TIBAIcIHgGLMt3Ql_ZnR7JROjdrobOP4B-fIXKAsXN4ZS-YI0jLD-AhxaGlg8k-Hwi-cEoaPsZBU06ZshILOBMoJT5zX5S87ds6TBMRlqSdoEihYmc328n1W9segrdF0lLmovgNg1foMrOeeLeT9DTyHRzrPg3p3x2aqlT_pJOYc7UEqfwepnCnKnzOXXRTKmcqSVOqetlSuVMnc8pyVTd3Axb7o9vwLr5Bh_nvk4)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZY2zjqpYem_o-iSNvGxFGEpAbSr49iAmuTBBqwmx508IsZs-MdhsEhbj19BGpfi2pRyEWBsjHpVDy_PaaLbwPOSoSdc4Czp3TnqSUVCNCCnjcWsCy_SDhBVoFxZg2Nm4OoxMsShAaKq-NzOoJWLWG5Bm8NWOOPM_D9NONsIKPmOzKaZAyQHXkGB_qY5lb7HueKaqYrT4r5SThDkUJPy-VPY_anVxsKzQ_xK91amKHT6nugHk6Ke9dDTxuTdcf4K59c9ulGn9yEPmHO0w0-4d3yhDlPo_k0TZ5kbqdzl-T_6iaZm2lEj6bLUW6l33uEd8pRbqSxPOIcVfWD3fpN999U1Qf7j5NR)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_BrnUjZY27jqpYem_o-gStvExFGEpAaSr69iAmuTFhqwmx508IsZs-MdhsEh7j2tArUvRbUs5LJA2Zh0Kh5fH9LFtwEXJcLBOcDFPN15akkFArSg5dqCKMs1CSfIKjDObKFxTyAq8fwOQgPFzfk5HUGrlrDcgrcGrPHnGfh2mXE1kFHzGRlNMgbIgTyDA31Mc5tjj_ODaqYrT4r5SThDkUJPy_efxuwPr3YUmhPxK91amKHT6nugHk6KR9dDLxuTdcf4K59c9ulGn9yEPmHO0w0-4d3yhDlPo_k0TZ5kbqdrl-T_6iaZm2lEj6bLUW6l33uEd8pRbqSxPOIcVfXM7v2u-2-q6i8e_5Mx)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYwlK7Fw-ufQ_D0tldkv4gYN369NK6CW2MiZql9cClP5kBBr58yQRjW43PBquHJNsl-S6huSzdI9k83rqXrgxlKYVOKaDszn1prJAbhE0DUpyBpOkRqSK4Jal4Ad4dQOhe2RZIRrZ7IALQnqRiUhkULLVNZd7A_e-HSWRjgaOh2f1R1NCUeliZPl1W_lKGj5av1kddcbNIh9oHZ1X7NHXqfc63e_H5XCP3Az636KMWzaSen27Yjz9oXqOR7-gnGY_PZwiHaRIU87VtrybRyznmxZixLlMVmV6FqQrMlEZPAzClq3pKo6eLMw3tKYueBmDKVvWURU8XZxrOU1nLc2x7_4p0OL3_1vX-mmiU9CpEAzsaW94AROmajsaGd3GigR2N7W4AomxNR2OzuzhR72hW3DStrse73qz4ALThK64)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ7DqkGxaU3AOlztBa5GNsUxpOjxMqTSqEBKhOWHiTj2Zsj_30pJGt6ww-WqzvkmyT5JuE56ryj2R1f-1fprZcpBwOWgMXN_7LYI2lRVi1oOQRWJrukGuGa5bKF6h09QzS9Np1wDK23gKTgG6vtFDaohSpa2v7Bv5_O8yiWgclWp7d7mQDbWWGpfnDaekvdVC0enUU9dWdRQ5oKHhWNqXpfU8532-GBpQGSxrxuUeKOrSTgn66Yxr_ZMoGrXpHmmQ8P8qQHtQkKM_Xdr2eRE8HmRdjxsJUdaR6Gao6NFUeXQ1BlS_rKo-uzk81uKsiuhqCqljWVRFdnZ9qQFdVo46xBf4z1OH4_l0H_GumUdTLMA3taWx_QzDli3oam9_5mYb2NLa-IZiKRT2Nje_8TMnTrLhqO9OMd8BZ8QHg7TU-)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYwlK7Fw-79j0MpbO7JP1BwGp9emndhG2MiZql9cClP5kBBr58yQRjO41PBuuHJNsn-T6huazcI9nsbt1L14aylEKvFFB257401sgNwqYtwSgNJE2PSBXBLUnFM_D-AEIPynZAMrItgQhAe5KKSWVQsNS2tXkF91-Os8jWAkdDs_ujaKCt9Lg0fTwv_aUOH61erI-66maRHrUPzsr2aeo0-JzvN-MHcI3cj_jco49aNBcF_XTHfvxB8waNfEc_yXR-PkM4UBdBMV_bDuoiej7IvJgyVqaqItXrUFWhqdLoagiqdF1XaXR1earBXWXR1RBU2bqusujq8lQDuiob-RZb4D9DHY_v33XAv2YaRb0O09CexvY3BFO6qqex-V2eaWhPY-sbgilb1dPY-C7P1HuaFTdtp5vpDjgrPgDqXTZ2)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYlgXrxYNr38OwdNwl6Q8BrK1PL62b0MbEaFzEA5f-ZAYY-PIlE4ztNT4ZbO4zts_KfUZKWbtHtnu4di_dGEJzAoNSQOiN-9LYIDcIu46DURpInh-RqEKM5YDcQtuMDISelO2hYMXdAQoBaE9SUakMCprbrjGv4P4P8zyys8DREHZ7FC10tZ4XJ4_nxT9V4qP1i_VRV98mMqD2wU3hPk2dJp_z1Xb8EK6R-zEfu_RRi2ZV0nf37Mc_a96ikW_oJ1lO0GcIB2sVFNu17aRW0fNRltWSEZ2sSmQvRVaFJ0uSs2HIktjOkuRsDLJ_4CxNzoYhS2M7S5OzMcgGdVa2ckyt8S_Azgf4DzvjH3NNwl6Ka3hfU1schiuJ7GtqimNwDe9raonDcKWRfU0NcQyu3ldWXXW9bpc7Y1a9A6ljU84)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctuwyAQ_Br3Um0FxJZz6aGJ_6PCsK1RSExYHDX9-hIr6tpqc80hvgDSzOxrtIJSH_Gd0L8W1aaoN4Wqnc1HsXp7zlf0pEqh4BQCqPIlvyJ61ISwOoAzXyCF-EQVJK6lMEewwe6g6ylR0mYHUq1FC9IApg5cKAcbjoMz7SVADomm66ENdMmnttd8f5IzaofEaNbPkBNGBme1Mi10Z-bc7oAFOqJmxW9jTEhIk5put8mKj6j3SO4bWTaOiRkmWzIBzTxbOocJep1e3YyMO_lHRnvMfC8FLcDH_9p9UD-XZecju7ms5bzzblbN06GP-_HPrJof9LcJqA)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCYte99NDU_6gw3taoOKYsjpy8PsSKurbaXHNwLoA0M8zujhAU-4AfhO41K7ZZuc1UaZu0ZJu3x7QFRyoXCvbeg8qf0imgQ00Imx1YM4IU4guVl2Z8bkbo3FhA21OkqM03SPUiapAGMLZgfT40_mewpj7r041o2h5qT2c79X6x--PNaDNERpN-gewxMLgolWm-PTDnagPM1wE1C377YkJEmpV0vUtWfAbdIdkjsmyaEjNMCmQGmqVbPPgZehleWU2M26RHRjuUwjgpaP0p_tftOtO8qzBXnOVdPcwbv8uietj1oZv-yqI6ATY_CZg)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctugzAQ_Bp6qbayHRC99NCE_4iM2RRUExyvQUm-Pg6KsqA-jjmEi21pZvY1WplC53FLaD-SbJ3k60TlTRWPZPX5Gi9vSaVCweAcqPQtvjxa1ISw2msg50EJ8YXKSXPMB9QBWnvMoO4oUNDmG6R6FyVIAxhqaFzaV-7QN6a8hohB0dQdlI6uGdXmlvFHekarPjAa9TNkQM_grFqmufrEnP96YIn2qFlzb40JAWlS1d-NsmLndYvUnJFl46CYYaItE9DMs4WTm6C3-eXFyHiYh2S0RSmMlYIW4eVvDT-tp0uz9LkdXdqSPnhHs-Jl3_l2_EOz4gJZsRPY)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbNe99JDU_4gwbGorJKYsiZK-vsSKuraqNKf2EF8AMTPsDiMExT7gitC9ZuUyq5aZqjqbhixfPKYpOFKFUHDwHlTxlFYBHWpCyHfQmSNIId5ReYkvUpgPsN5uoO0pUtRmA7J4Fg1IAxhb6HwRjW_OYmd9OqfXNm1iWOfQeDoXVW-Xoj86YNTuI6OprwlywMDgpGGm-fbEnOs2WKADalZ8u2NCRBr1dMMry9ZBb5G6T2TtcGHMMCmcEWimJePJj9DLFVb1wPiHJMloh9I4KWgugf5m-T5y3dv5vNBrXu8mybm90BuW_z7Xsn7Y9WE7_KVl_QUYjRDu)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVcFuwyAM_ZrsMnkCkjSnHdblPyYC7hKNNAjTKt3Xj0bVnGjqeuqluQDiPWM_P1lQHAJ-ELrXrNxm1TZTVWfTkuVvz2kLjlQhFBy9B1W8pFNAh5oQ8j10ZgQpxCcqL824sSP0biyhHShS1OYLZLERDUgDGFvofBGNb86xzvr0zKBtusSwy6HxdM6p3i85_xTAqD1ERlNZC-SIgcFFvUzz7Yk5V1UwXwfUHPArjgkRaVbSDakctgu6R-q-kWOnfjHDJGtmoFmmjCc_Qy8drOqJcX8fyWiH0jgpaCV2_qf4IVw92NVM5zWpj-LjyqbzhuL7u1rWT_sh9NMfWtY_O78Q3g)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFOwzAQfE24oEW2kxAuHCj5B3LsLYmaNovXrVRejxtVbCJEe4JDc7Etz4x3xyPLHIeAb4z9c1ausmqVmarzacjyl_s0hZ5NoQwciMAUD2kVsEfLCPmuAaYAWql3NKTxSSv3AZ78BtqBI0frNqCLR9WAdoCxhY6K6Kg5qXtP6aDB-rSJYZ1DQ3yqal7PVX-0IKjfR0FTYzPkgEHAWcdCo_YonAs-RGEDWpF82xNCRJ40dcWsyNbBbpG7TxTteGPCcCmeCejmJeORJuj5Dqt6ZPxHluxsj9r1WvFiIr3k-UaS3fsFvdLfzN5Olot7pVc8_32yZX23G8J2_FPL-gse3xSG)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbNenHpr4HxWGTW0Vx4glVtLXl1hR11bV5NQe4gsgZobdYYSgOAR8I3QvWbnJqk2mqs6mIctfH9MUHKlCKBi9B1U8pVVAh5oQ8r0G8gGUEO-ovDTHakQdoXfHEtqBIkVtPkAWz6IBaQBjC50vovHNWe6sTycN2qZNDLscGk_nsmp7KfujB0btITKaOlsgIwYGFy0zzbcn5lwzwhIdULPm2x8TItKsqxtuWbYLukfqPpG105Uxw6SAZqBZlownP0Mvl1jVE-Nf0iSjHUrjpKD1hHrN9L1ke7Breqm_ub2jNNf3Um-Y_vtsy_phP4R--lvL-gsy1Rse)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiT70kNS_0dQ5E1tcJytpJikX185DcimGAotLYRc9JpZ7Y6GRT4cHG48ds-ZWmfFOhNFW8chy1ePcXKdF5IJGIhAyKe4ctih8Qiih9aegDP2ioI4lpzZNzDDDlqS4_EWuAUMTdwGS-PpdoxrOBMSSOfgtVRcQKBjgL52Y1Lxck36pYKE1seQ0FjXDBnQJXBWcKJRc55wlmQkvnFoUkDUkaCAflLMN8Wm8J0ze_TtO6Y7xodLBBvNmWB2njmcaYJen7CoLox_c5LuTv7USfpzJ7VSuf5UJ7koC13edlsu6L2Zzlzyk-5-_mp_quqhP7j95e9U1QekIvTr)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYa0n2pYek_o-iypva4DhbSTGkX185DcimGAotLYRc9JqRdmeHRT4cHD176h8ztc3KbYZl18QhKzb3cXK9R5kjjMyA8iGuHPVkPAEO4NmByPNXQhZUidy-gRl30LGcjl9AWKDQxm2wDIMJUlIDrchRAusCvJZKIAQ-BhgaNwXFp0vQLxkktDmGhMa8FshILoGLhBON29OMsyYj8Y0jky5EOQkK5GfJfFNsur5zZk--e6f0xlS4RLDRnBlml5HDiWfopYRlfWb8m5N8c_KnTvKfO6mVKvSnOimwKnV13W25ovdqOnPNT775-av9qeq74eD2579T1R-52PPT)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRKWFgokIlL7Lp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAFXze5j)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYip30ZQ_t8h_Dc7QlkKTCdkPbr6_bFZwwAoMNCqUvvnAk6xwdhH3YOnr31L1mepOVmwzLto5Llq-f4-Y6j0ogjMyA6iWeHHVkPAEO4NkBCvFFyNLuy5FMgL7ba2hZgRTiA6QFCk28BsswmKAU1dBIgQq4yMEXSkuEwLsAQ-3OZfHtWvYHh4TWu5DQyGyGjOQSOKOcwrg5TGKWhaQM48iklCgoQYH8hM4v5ab0T2d68u2R0hvn1qUAGw2aYHZeORx4gl6bWFaXiBu6yQ83_-4m38DNQuu8-NanJK7KYnXv47mg-I4mdMlTfnj6z3Oqq6dh6_rLX6qrEyEm_aM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVsGKwjAQ_ZruZZmlia3dyx7U_ofEdNRCjWOSFvXrN5XCtCvCHgSh9ZKEvDeZmTweifNHi2uH1U-ULqNsGcmsLMIQzRafYbKVk0ksoSECmXyFlcUKlUOQBkp9BhHHO5Qk8FvE-gSq2UJJydrXxmDlYJ5sQGhAvw-70M11QTs02CCIeSC2AZv2SFPYNrNcdZnvymC0qD2jobgB0qBlcFA102h_6XEe9cJ8ZVFxQK9Fpnh0vaL-1TIHb606oCuvyCeEu2NcB5kYEnqY1l-oh3b3mOU3xms1pbemT9GUXqvp9Gw6dpdOz6Qj96hMp_eYDnseo0__qEpvVZ_t1TT_MEd7uP1_0_wX2pkbKQ)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFuwjAQRU-TbqqpksEhqy4KuQcKzhQiOcayHQicvg5CmkQtCxCFjTdx5P_tGfvpS3Z-Z2nlSH0m-SIpFgkWTR0-yezrPQxWORQpwt4YQPER_iwpqhzBTEMje8jSdENoMtnP6x5a1efQGLHyndakHMzFGjIJ5LdhduNN5w6Dvh520LUdCuHyUuhXVVbrzrMaepkoe7IsTppkm9ke2XO1dfZXlipeMDoRWzy5UVN_nZC937ZqyTUn4gXhZliXAQJLmZxW8UczUi_XVpRnx1OJmUjsHmLm_4lhzNhtxPDVGcOYsUcSe0LGRMzYbcTEqzMmYsYeSYwzlpdvemfb85sxL38A-znb1g)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFuwjAM_ZpymTy1oV1PHAb9D5SmHlRKg-WEquzrF1glt0Jw4YCEuCRRnl_s5ycrPhwYtx7tKinWSblOVNk2cUmW3x9xY-tVniroiUDln_HEaFF7hKXT4IlBpekOFWVmKHvUATo7FNBSvg1H59B6-MpryAxg2MfbfrDagVV1U8dHOm0sO3ANnzOqzZjxKr2gzTEIGouaIT2ygLNqJYz2J4m5p0EomlELZyJNQgL6SV23pQrjh3WHvv1FocVGCW6iLQJlZp4rnGiCjv0rq0vEczykt4cPeUjP8XAwZ2EvPoH_Il9q9kbf6O3bw_NWVAt34O7y_xXVH06v_as)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlsFugzAMhp-GXSZP4IZx2mEt71Gl4LVIgVpJYO2efqGqZNCmSZ0q1EMuBPH_xk4-_VKcP1raOjJvSb5OinWCRVOHR7J6fw6LNQ5VijAwA6qX8GbJkHYEq06DYwuYpntCzqpTMZD20JpTDg2rre-7joyDV7WDrALyh_B177l3n6O-G3_S1XbshZtrrx-NRa17L2oYZ6YMZEWczSk2PpzF89f0UqItaamZbEosntxkrt82Kd4Pq1tyzRdJQTgc0auAQqSsmnfxZ56o15MryotjaW4cuf2TGy_CDWPebuaGD5A3jHm7M7dl8qZi3m7mph4gbyrm7c7cJG95-dQdbXu5V-blN__K6zY)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVl1rwyAU_TXZy3CoTUhe-rA2_6PYeNcGjJWrSdv9-plQuAmD7WWsUPui4jnX-3E4oA8nhJ0Hs86KTVZuMlm2Oi7Z6v01bmi8zLlkg3NM5m_xhGBAeWArq5h3yCTnB5BONJdyABVYZy4Fa12-C721YDwThaj2TDQMwjHe99qdW4RDr1ALzoM1_jzy9-OjVuOYW25vub8VQqjuA6GxvAUyABK4qJto7nglzk_dUIhCUBQza5IoAfysrt9bpsgPVB349hMofBodMZoo1QxsllnD1c3Q2yTLemLcW1f31PWPdHV31TU5tybg1eSc-vg-rVLzafX4Pq1S82n1zz4t6hd7wm76Bxf1F_3qK2U)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEWx65BeOFDyD5Q4S2uROMZrCuH1uKHSJkJckNLmkIttecar2R2NZAqdx2fC5iHJdkm-S2Ru6rgkm8fbuPmGpEolHJ0Dqe7iyWODJSFsLBj9CSJN9yidwK1I9RvUrn4F7XsXOhCZ2FYgNGA4GKeMI9SRngbb0AfEm-pUx9gAJZLM7ve6jdVLImyrpgdb-5MO-XTW8UsUo_V7YDRKnSBH9AxOemCaO_TM-bszflBGofzip2FGA9JI0L_a52IvvmyRzBdyxWGyzNDRwhGop0JC70boeap5MTCW5Ldb_Z7Bbze333LN92X9ltfNt1zzvSS_Z8-3WvN9Wb_VdfOt1nwvyW_Od1bc2M63wz89K74B21hUdQ)

## CSIT-2402 Selected Performance Comparisons

Comparisons 24.02 vs 23.10
- [2n-icx 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkE0OwiAQhU9TN4YGsLVuXFh7AGO8AMGpadJSHGijnl7oj9jEhQkBZt43zPAM1CAtXPdRlkc8QygBQUlw92hzWI9ZA3aKL9g56bgekr6yatUCvXYz6o5eax-MvFN6wCBibXhCOeGbmFGC7jVhIOCVKlEEmitSyQdhlN6AawY7RuWdiL4MFbLFz9ipn4UdfZgWk15iY6rXEtkm-YKx9qmXxKk4T0Q2rLlXowX-4ZKjRAP2--PBiBHpRd3BD1-S2O1fvgz9V6rFZu9HS4s34Cl0zQ)

## CSIT-2402 Selected Performance Coverage Data

CSIT-2402 VPP v24.02 coverage data
- [2n-icx 200ge cx7 mlx5 ip4](https://csit.fd.io/coverage/#eNpVjsEOwiAQRL8GLwaDK4RTD9r-h9ngxpIgJYBI_94SD9TLJjNvZjOJHJlsFz8wfWOgo0vbZZfr8SdACmgGjM14vHOnJYQ_Uih2CPIkgMftOybqsTCvu4zn1lQOQjwJwtlUXQgzf7mqegMjYa_YIJvQ0yHNy-fuMJM368BU2763WkpNXye-PaE)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
