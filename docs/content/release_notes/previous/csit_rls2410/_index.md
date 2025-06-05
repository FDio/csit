---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2410"
weight: 2
---

# CSIT-2410 Release Report

This section includes release notes for FD.io CSIT-2410. The CSIT report
was published on **Nov-13 2024**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2410_plan) pages.

## CSIT-2410 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

For infra reasons, we ultimately stopped device testing.

## CSIT-2410 Release Data

To access CSIT-2410 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2410`
  - `DUT` > `vpp`
  - `DUT Version` > `24.10-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v24.10 vs v24.06
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2406-24.06-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2410-24.10-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2410`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2410`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2410 Selected Performance Tests

CSIT-2410 VPP v24.10 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsrUO4cGjJfyDjbGlEmpq1G1G-HreqtIkAqUgtvfjgl2asHe9oJIe4YXoO1D0W5aKoFgVWbZOmYja_TQt3AY1WMHgPaO7SjqkjGwiwh9Z9gFbqldBretDKvYMdltB6A_fmBbQDiqv9KY3gbEeo3oD7BvqG9yXw6VjiWz1Bm20UNKmYIAOxgBN5QvOr3Yjzm2jhWyYrF5JygSKFkZif3ybsJds1hfaT5ErqiuAuNV4g7aZ14s6P0GPDqvrA-CeXfHbpby75y7mEOUunu4TXyhLmLJ3LpQtmyeQsne6SuVaWTM7SuVySLJX1Tb_h9eGvV9ZfVxOuLg)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_BrnUrZIWznupYem_o-iypvG1HHUlWpIv75KCKxNUkghaS466MWM2NEOAwpxw_QaqHsqykVRLQqs2iZNxcPzXVq4C2i0gsF7QHOfdkwd2UCAPQTPoJV6J_SaHrVyn2CHJbTewNy8gXZAcbU7pRGc7QjVB3DfQN_wrgS-HEoc1RO0-YqCJhUTZCAWcCJPaH61HXF-Ey18y2TlQlIuUKQwEnP6bcJesl1TaL9JrqSuCO5S4wXSblonbv0IPTSsqveMf3LJZ5f-5pK_nkuYs3S-S3irLGHO0qVcumKWTM7S-S6ZW2XJ5CxdyiXJUlnP-g2v93-9sv4Bi3Gu-g)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEW2cQgXDi35BzL2QqOm6bI2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5py_gSsX-q6mXVLCvTdCEv1f3iNv-4j8ZqBTsiMPYu7xh7dBHBDBCJQSv1joY0PmrlPyBQWENHFh7sK2gPmFaHU_6idz0atQYeAgyBDxzm-cTxg1DQ8JkEzTImyA5ZwIk-KaPVflTzp2ppcIxOOrJ0gRLGkZrfLyfVb-w2GLsvlJY8FsF9Hr1A2k950p5G6GliTXus-C-fqPg00ye6oE-m5GmGT-ZqeTIlT2fz6ZJ5siVPM3yyV8uTLXk6m0-Sp7q9Gba8Ob776vYbCISzwg)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UjbYG7k-9dDU_xEUeZuYyo5YqSbp11cJgbVpezDkcdHBssTsMqMdBuTDnmntyb5m5SqrVhlWbROXbPn2HH9sPaoih8E5QLWIOyZL2hNgD94xYJ5vCV1hDtVAOkBnDyW0TsGL2kBhgMLudIqfN9oS5p_AfQN9wycSfL-Q_GIUtPkKgkYdE2QgFnAiUMrc7jiq-V-2dGgmLS1Ru0CB_EjO37eT6g_WHfn2m6QlzkVwE4cvUGGmPOHoRuhlZFV9rribUy45Ndcpd0unMGVqjlP4uExhytT1nLppplTK1Byn1OMypVKmrueUZKqsn_o9d-c3YFn_AP69vbI)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasZo0u9nFurzH8GxtDU1dYaeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7j6TVQ-5SVi6xaZFg1Np6y2fN9vPg2YKFy2DEDFg_xzlNLOhCgAzNvHGCef5BiRU6DZbuChgtQpXp8A2WAumX_HI9gdEuYr8A7C876vga-HGocFRTVbjtRYxsTZUdexEl_YuPlfuT5oWuxa09a_LFxkToKo16-_zRxv3u9ptB8krwyjEUcJo5-JJpppW7PI_UwsaoeHP_FiROnEznxBTlhytMJnPBqecKUp7Nxukye5kXaTkeU4lBuaTf9zogToxvYSz2jtJX-zgivlKO0kc7FSHJU1ndu49fDf1NZfwEQ_pKp)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasZosu9nFurzH8GytDU1dYaeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7j6S1Q-5yV86yaZ1g1Np6y2ct9vPg2YKFy2DEDFg_xzlNLOhCgA1MtHKg8X5BiRU6DZbuChgtQpXp6B2WAumX_HI9gdEuYr8A7C876vga-HmocFRTVbjtRYxsTZUdexEl_YuPlfuT5oWuxa09a_LFxkToKo16-_zRxf3i9ptB8krwyjEUcJo5-JJpppW7PI_UwsaoeHP_FiROnEznxBTlhytMJnPBqecKUp7NxukyeHou0nY4oxaHc0m76nREnRjewl3pGaSv9nRFeKUdpI52LkeSorO_cxq-H_6ay_gI0X5KJ)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsrUN64UCb_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0U5aKoFgVWbZOmYvZ4mxbuAhqtYPAe0NylHVNHNhBgD637AK3UC6HXNNfKvYEdVtD6e6jmz6AdUFzvT2kEZztC9QrcN9A3vC-By2OJb_UEbd6joEnFBBmIBZzIE5pf70ac30QL3zJZuZCUCxQpjMT8_DZhr9huKLSfJFdSVwR3qfECaTetE3d-hB4bVtUHxj-55LNLf3PJX84lzFk63SW8VpYwZ-lcLl0wSyZn6XSXzLWyZHKWzuWSZKmsb_otbw5_vbL-Au7lrrI)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIG7nOpYek_o-iypvG1HHUlWJIv75KCKxNW0ghaS466MWM2NEOAwpxy_QSqHsqymVRLQus2iZNxWxxnxbuAhqtYPAe0DykHVNHNhBgD8EzaKXeCL2muVbuA-ywgtY_QjV_Be2A4vpwSiM42xGqd-C-gb7hQwl8PpX4Vk_QZhcFTSomyEAs4ESe0Px6P-L8Jlr4lsnKhaRcoEhhJObntwl7xXZDof0kuZK6IrhLjRdIu2mduPcj9NSwqj4y_skln136m0v-ei5hztL5LuGtsoQ5S5dy6YpZMjlL57tkbpUlk7N0KZckS2V91295c_zrlfUXI1Kvfg)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEW2cUgvHCj5BzL2QqOm6bI2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5py_gSsX-s6mXVLCvTdCEv1f3Tbf5xH43VCnZEYOxd3jH26CKCGSASg1bqHQ1pXGjlPyBQWENHD9AsXkF7wLQ6nPIXvevRqDXwEGAIfOAwzyeOH4SChs8kaJYxQXbIAk70SRmt9qOaP1VLg2N00pGlC5QwjtT8fjmpfmO3wdh9obTksQju8-gF0n7Kk_Y0Qk8Ta9pjxX_5RMWnmT7RBX0yJU8zfDJXy5MpeTqbT5fMky15muGTvVqebMnT2XySPNXtzbDlzfHdV7ffoyy0Rg)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJ4mAuHFryD2SchUY4qbU2UcvrcatKmwg4RGrpxYc4tmZXM97RSA5xy_QSyD0V9brQ6wJ116aluF_dph-7gKoqYfQeUN2lHZMjEwhwgOAZsCzfCX1ld3okE6F3uxo6_wD68RUqCxQ3h1P6gjWOsPwAHloYWj6Q4POJ5AejoO1nFDTpmCEjsYAzgVLmN_tJzd-ypcMwGWlJ2gWKFCZyfr-dVL-x6Sl0XyQtaS6C2zR8gSo754l7P0FPI9PNseLfnPLZqaVO-Us6hTlTS5zC62UKc6bO59RFM6VyppY4pa6XKZUzdT6nJFN1czNsuT--AevmG5xKvjY)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZY2zjqpYem_o-iSNvGxFGEpAbSr49iAmuTBBqwmx508IsZs-MdhsEhbj19BGpfi2pRyEWBsjHpVDy_PaaLbwPORAk75wBnT-nOU0sqEKAFPW8sYFl-kXCCrALjzBoaNwdRiZclCA0UV8fndAStWsJyDd4asMYfZ-D7acbZQEbNd2Q0yRggO_IMDvQxza32Pc4V1UxXnhTzk3CGIoWelsufxuxPrzYUmh_iV7q1MEOn1fdAPZwU966HnjYm647xVz657NONPrkJfcKcpxt8wrvlCXOeRvNpmjzJ3E7nLsn_1U0yN9OIHk2Xo9xKv_cI75Sj3EhjecQ5quoHu_Wb7r-pqg8Zh5Mx)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_BrnUjZY27jqpYem_o-gStvExFGEpAaSr69iAmuTFhqwmx508IsZs-MdhsEh7j2tArUvRbUs5LJA2Zh0Kh5fH9LFtwEXooSDc4CLebrz1JIKBGhBy7UFUZZrEk6QVWCc2ULjnkBU4vkdhAaKm_NzOoJWLWG5BW8NWOPPM_DtMuNqIKPmMzKaZAyQA3kGB_qY5jbHHucH1UxXnhTzk3CGIoWelu8_jdkfXu0oNCfiV7q1MEOn1fdAPZwUj66HXjYm647xVz657NONPrkJfcKcpxt8wrvlCXOeRvNpmjzJ3E7XLsn_1U0yN9OIHk2Xo9xKv_cI75Sj3EhjecQ5quqZ3ftd999U1V886JMR)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYwlK7Fw-ufQ_D0tldkv4gYN369NK6CW2MiZql9cClP5kBBr58yQRjW43PBquHJNsl-S6huSzdI9k83rqXrgxlJIVOKaDszn1prJAbhE0DUpyBpOkRqSK4Jal4Ad4dQOhe2RZIRrZ7IALQnqRiUhkULLVNZd7A_e-HSWRjgaOh2f1R1NCUeliZPl1W_lKGj5av1kddcbNIh9oHZ1X7NHXqfc63e_H5XCP3Az636KMWzaSen27Yjz9oXqOR7-gnGY_PZwiHaRIU87VtrybRyznmxZixLlMVmV6FqQrMlEZPAzClq3pKo6eLMw3tKYueBmDKVvWURU8XZxrOU1nLc2x7_4p0OL3_1vX-mmiU9CpEAzsaW94AROmajsaGd3GigR2N7W4AomxNR2OzuzhR72hW3DStrse73qz4AI6LK34)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ7DqkGxaU3AOlztBa5GNsUxpOjxMqTSqEBKhOWHiTj2Zsj_30pJGt6ww-WqzvkmyT5JuE56ryj2R1f-1fprZcsBQOWgMXN_7LYI2lRVi1oOQRWJrukGuGa5bKF6h09QzS9Np1wDK23gKTgG6vtFDaohSpa2v7Bv5_O8yiWgclWp7d7mQDbWWGpfnDaekvdVC0enUU9dWdRQ5oKHhWNqXpfU8532-GBpQGSxrxuUeKOrSTgn66Yxr_ZMoGrXpHmmQ8P8qQHtQkKM_Xdr2eRE8HmRdjxsJUdaR6Gao6NFUeXQ1BlS_rKo-uzk81uKsiuhqCqljWVRFdnZ9qQFdVo46xBf4z1OH4_l0H_GumUdTLMA3taWx_QzDli3oam9_5mYb2NLa-IZiKRT2Nje_8TMnTrLhqO9OMd8BZ8QG4PzUO)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYwlK7Fw-79j0MpbO7JP1BwGp9emndhG2MiZql9cClP5kBBr58yQRjO41PBuuHJNsn-T6huazcI9nsbt1L14YykkKvFFB257401sgNwqYtwSgNJE2PSBXBLUnFM_D-AEIPynZAMrItgQhAe5KKSWVQsNS2tXkF91-Os8jWAkdDs_ujaKCt9Lg0fTwv_aUOH61erI-66maRHrUPzsr2aeo0-JzvN-MHcI3cj_jco49aNBcF_XTHfvxB8waNfEc_yXR-PkM4UBdBMV_bDuoiej7IvJgyVqaqItXrUFWhqdLoagiqdF1XaXR1earBXWXR1RBU2bqusujq8lQDuiob-RZb4D9DHY_v33XAv2YaRb0O09CexvY3BFO6qqex-V2eaWhPY-sbgilb1dPY-C7P1HuaFTdtp5vpDjgrPgDBrzZG)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYlgXrxYNr38OwdNwl6Q8BrK1PL62b0MbEaFzEA5f-ZAYY-PIlE4ztNT4ZbO4zts_KfUZKWbtHtnu4di_dGEKLHAalgNAb96WxQW4Qdh0HozSQPD8iUYUYywG5hbYZGQg9KdtDwYq7AxQC0J6kolIZFDS3XWNewf0f5nlkZ4GjIez2KFroaj0vTh7Pi3-qxEfrF-ujrr5NZEDtg5vCfZo6TT7nq-34IVwj92M-dumjFs2qpO_u2Y9_1rxFI9_QT7KcoM8QDtYqKLZr20mtouejLKslIzpZlcheiqwKT5YkZ8OQJbGdJcnZGGT_wFmanA1DlsZ2liZnY5AN6qxs5Zha41-AnQ_wH3bGP-aahL0U1_C-prY4DFcS2dfUFMfgGt7X1BKH4Uoj-5oa4hhcva-suup63S53xqx6B3wFU54)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctuwyAQ_Br3Um0FxJZz6aGJ_6PCsK1RSExYHDX9-hIr6tpqc80hvgDSzOxrtIJSH_Gd0L8W1aaoN4Wqnc1HsXp7zlf0pEop4BQCqPIlvyJ61ISwOoAzXyCF-EQVJK6lMEewwe6g6ylR0mYHUq1FC9IApg5cKAcbjoMz7SVADomm66ENdMmnttd8f5IzaofEaNbPkBNGBme1Mi10Z-bc7oAFOqJmxW9jTEhIk5put8mKj6j3SO4bWTaOiRkmWzIBzTxbOocJep1e3YyMO_lHRnvMfC8FLcDH_9p9UD-XZecju7ms5bzzblbN06GP-_HPrJofsq8JmA)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCYte99NDU_6gw3taoOKYsjpy8PsSKurbaXHNwLoA0M8zujhAU-4AfhO41K7ZZuc1UaZu0ZJu3x7QFRyqXAvbeg8qf0imgQ00Imx1YM4IU4guVl2Z8bkbo3FhA21OkqM03SPUiapAGMLZgfT40_mewpj7r041o2h5qT2c79X6x--PNaDNERpN-gewxMLgolWm-PTDnagPM1wE1C377YkJEmpV0vUtWfAbdIdkjsmyaEjNMCmQGmqVbPPgZehleWU2M26RHRjuUwjgpaP0p_tftOtO8qzBXnOVdPcwbv8uietj1oZv-yqI6AfRwCYg)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctugzAQ_Bp6qbayHRC99NCE_4iM2RRUExyvQUm-Pg6KsqA-jjmEi21pZvY1WplC53FLaD-SbJ3k60TlTRWPZPX5Gi9vSaVSwOAcqPQtvjxa1ISw2msg50EJ8YXKSXPMB9QBWnvMoO4oUNDmG6R6FyVIAxhqaFzaV-7QN6a8hohB0dQdlI6uGdXmlvFHekarPjAa9TNkQM_grFqmufrEnP96YIn2qFlzb40JAWlS1d-NsmLndYvUnJFl46CYYaItE9DMs4WTm6C3-eXFyHiYh2S0RSmMlYIW4eVvDT-tp0uz9LkdXdqSPnhHs-Jl3_l2_EOz4gIXGRPI)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbNe99JDU_4gwbGorJKYsiZK-vsSKuraqNKf2EF8AMTPsDiMExT7gitC9ZuUyq5aZqjqbhixfPKYpOFKFFHDwHlTxlFYBHWpCyHfQmSNIId5ReYkvUpgPsN5uoO0pUtRmA7J4Fg1IAxhb6HwRjW_OYmd9OqfXNm1iWOfQeDoXVW-Xoj86YNTuI6OprwlywMDgpGGm-fbEnOs2WKADalZ8u2NCRBr1dMMry9ZBb5G6T2TtcGHMMCmcEWimJePJj9DLFVb1wPiHJMloh9I4KWgugf5m-T5y3dv5vNBrXu8mybm90BuW_z7Xsn7Y9WE7_KVl_QXVthDe)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVcFuwyAM_ZrsMnkCkjSnHdblPyYC7hKNNAjTKt3Xj0bVnGjqeuqluQDiPWM_P1lQHAJ-ELrXrNxm1TZTVWfTkuVvz2kLjlQhBRy9B1W8pFNAh5oQ8j10ZgQpxCcqL824sSP0biyhHShS1OYLZLERDUgDGFvofBGNb86xzvr0zKBtusSwy6HxdM6p3i85_xTAqD1ERlNZC-SIgcFFvUzz7Yk5V1UwXwfUHPArjgkRaVbSDakctgu6R-q-kWOnfjHDJGtmoFmmjCc_Qy8drOqJcX8fyWiH0jgpaCV2_qf4IVw92NVM5zWpj-LjyqbzhuL7u1rWT_sh9NMfWtY_-TAQzg)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVctOwzAQ_JpwQYvsPAgXDpT8B3LsLYnqNovXrVS-Hjeq2ESI9gSH5mJbnhnvjkeWOQ4B3xj9c1atsnqV5XXv0pAVL_dpCp7zUis4EEFePqRVQI-GEYpdC0wBtFLvmJPGJ63sBzhyG-gGjhyN3YAuH1UL2gLGDnoqo6X2pPaO0kGDcWkTw7qAlvhUNX89V_3RgqBuHwVNjc2QAwYBZx0LjbqjcC74EIUJaETybU8IEXnS1BWzIlsHs0XuP1G0440Jw6Z4JqCdl4xHmqDnO6ybkfEfWbI1HrX1WvFiIr3k-UaS3bsFvdLfzN5Olot7pVc8_32yVXO3G8J2_FOr5gvbwBR2)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbNenHpr4HxWGTW0Vx4glVtLXl1hR11bV5NQe4gsgZobdYYSgOAR8I3QvWbnJqk2mqs6mIctfH9MUHKlCChi9B1U8pVVAh5oQ8r0G8gGUEO-ovDTHakQdoXfHEtqBIkVtPkAWz6IBaQBjC50vovHNWe6sTycN2qZNDLscGk_nsmp7KfujB0btITKaOlsgIwYGFy0zzbcn5lwzwhIdULPm2x8TItKsqxtuWbYLukfqPpG105Uxw6SAZqBZlownP0Mvl1jVE-Nf0iSjHUrjpKD1hHrN9L1ke7Breqm_ub2jNNf3Um-Y_vtsy_phP4R--lvL-gvvbhsO)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiT70kNS_0dQ5E1tcJytpJikX185DcimGAotLYRc9JpZ7Y6GRT4cHG48ds-ZWmfFOhNFW8chy1ePcXKdF5IzGIhAyKe4ctih8Qiih9aegDP2ioI4lpzZNzDDDlqS4_EWuAUMTdwGS-PpdoxrOBMSSOfgtVRcQKBjgL52Y1Lxck36pYKE1seQ0FjXDBnQJXBWcKJRc55wlmQkvnFoUkDUkaCAflLMN8Wm8J0ze_TtO6Y7xodLBBvNmWB2njmcaYJen7CoLox_c5LuTv7USfpzJ7VSuf5UJ7koC13edlsu6L2Zzlzyk-5-_mp_quqhP7j95e9U1Qdh8vTb)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYsiT70kNS_0dR5U1tcJytpBjSr6-cBtamGAotLYRc9JqRdmeHRSEePD4H7B8zvc3KbSbLrklDVmzu0-T7IJXIYSQCqR7SymOPNiDIAQJ5EHn-ipIEViJ3b2DHHXSkpuMXEA4wtmkbHcFgo1LYQCtyqYBMAcEoLSREOkYYGj8FlU-XoF8yYLQ5RkZTXgtkRM_gImGmUXuacdZkMN96tHwhyWEoYpgl802xfH3n7R5D9478xlQ4Jrhkzgxzy8jxRDP0UsKyPjP-zUm6OflTJ-nPnTRaF-ZTnRKyKk113W25ovdqOnPNT7r5-av9qeu74eD3579T1x93qPPD)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRKWlgIkIlL7Lp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAEWLe5T)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsh659JDU_1FUeVsbbGeRFJPk66OkAdkUQ6GFQMhFD2ZXO7PDohC3Ht8Ddq-F2hRmUwjT1mkpyvVz2nwXhOQMRiIQ8iWdPHZoA4IYIJAHwdgXCuJub0a0Efpur6AlCZyxD-AOMDbpGh3BYKOUWEPDmZBAuoSgpeICIu0iDLU_lxVv17I_OGS03sWMJmYzZESfwRnlHEbNYRKzLCRnWI82pyRBGYoYJnR-KTenf3rbY2iPmN84ty4HuGTQBHPzyvFAE_TaRFNdIm7oJj3c_LubdAM3tVKl_tYnuVgZvbr38VxQfEcTuuQpPTz95zlV1dOw9f3lL1XVCd5X_ZM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVsGKwjAQ_ZruZZmlia3dyx7U_ofEdNRCjWOSFvXrN5XCtCvCHgSh9ZKEvDeZmTweifNHi2uH1U-ULqNsGcmsLMIQzRafYbKVk4mIoSECmXyFlcUKlUOQBkp9BhHHO5Qk8FvE-gSq2UJJydrXxmDlYJ5sQGhAvw-70M11QTs02CCIeSC2AZv2SFPYNrNcdZnvymC0qD2jobgB0qBlcFA102h_6XEe9cJ8ZVFxQK9Fpnh0vaL-1TIHb606oCuvyCeEu2NcB5kYEnqY1l-oh3b3mOU3xms1pbemT9GUXqvp9Gw6dpdOz6Qj96hMp_eYDnseo0__qEpvVZ_t1TT_MEd7uP1_0_wXSh8bEQ)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFuwyAQRU_jbqqpDMHxqosmvkfk4GliCZMR4NTp6YujSGOr7SJVmmzYGIv_YQaevoQPB4cbj-Y1K1ZZucpk2Tbxky3enuPgjJdK5HAkAqle4p9Dg7VHWFho9QAiz3coSehh2QzQmaGAltQm9Nai8bBUWxAaMOzj7C5Q7z9GfTvuYBs3FpLrS6FvVVlt-sBq7GWmHNGxOGuSbbQ_sefX1tlfO6x5weREbAnoJ039dEL2vru6Q99-Ii-IN8O6jhBYEnpeJZxool6urazOjrsSo0TsL8To_4nJlLHriMlHZ0ymjN2S2B0yplLGriOmHp0xlTJ2S2KcsaJ6sgfXnd-MRfUFdTvbvg)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFuwjAM_ZpymTy1oV1PHAb9D5SmHlRKg-WEquzrF1glt0Jw4YCEuCRRnl_s5ycrPhwYtx7tKinWSblOVNk2cUmW3x9xY-tVnqXQE4HKP-OJ0aL2CEunwRODStMdKsrMUPaoA3R2KKClfBuOzqH18JXXkBnAsI-3_WC1A6vqpo6PdNpYduAaPmdUmzHjVXpBm2MQNBY1Q3pkAWfVShjtTxJzT4NQNKMWzkSahAT0k7puSxXGD-sOffuLQouNEtxEWwTKzDxXONEEHftXVpeI53hIbw8f8pCe4-FgzsJefAL_Rb7U7I2-0du3h-etqBbuwN3l_yuqPw8r_Zs)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlt2KgzAQhZ_G3iyzaBrXq73Y1vcoqc62QkyHJNqfp99YCqN0WehSpBe5MeI540zycSDOHyxuHOrPJF8lxSoRRVOHR7L8eguL1U7ILIWeCIR8D28WNSqHsDQKHFkQabpDQVl1KnpUHlp9yqEhufGdMagdfMgtZBWg34evO0-dOw76dviJqe3QS6xvve4as1p3ntUwzkTp0bI4mZNttD-z56_puURZVFwz2hRbPLrRXL9tkr3fVrXomgtyQTgc1quAgqWsmnbxZxqpt5Mryqtjbm4Uuf2TG83CTcS8PcxNvEDeRMzbk7nNkzcZ8_YwN_kCeZMxb0_mxnnLy4U52PZ6r8zLH3f46x4)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVl1rwyAU_TXZy3BEG4kvfVib_1FsvGsDxsrVpO1-_Uwo3ITB9jJWaPqi4jnX-3E4YIgnhF0Au87kJis3mSgbk5Zs9f6aNrRBFDxnvfdMFG_phGBBB2Arp1nwyESeH0B4Xl_KHnRkrb1I1vhiFzvnwAbGJVd7xmsG8ZjuO-PPDcKh02h4nkdnw3ng74dHncEht9jecn8rhFDTRUJTeTOkByRwVjfR_PFKnJ-6oRCNoClm0iRRIoRJXb-3TJEfqFsIzSdQ-Dg6YtRJqglYz7PGq5-gt0mW1ci4t67-qesf6ervquvi3LoAry7OqY_vU7U0n6rH96lamk_VP_tUVi_uhO34D5bVF21oK00)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEWx65BeOFDyD5Q4S2uROIttCuH1uKHSJkJckNLmkIttecar2R2NZB86h88em4ck2yX5LpG5qeOSbB5v4-YaL5VI4UgEUt3Fk8MGS4-wsWD0J4g03aMkgVuR6jeoqX4F7XoKHYhMbCsQGjAcDClDHnWkp8E2_gPiTXWqY2yAEr3M7ve6jdVL77Gtmh5s7U465NNZxy9RjNbvgdEodYIc0TE46YFpdOiZ83dn_KCMQvnFT8OMBvQjQf9qn4u9uLJFb76QKw6TZYaOFo5APRUSehqh56nmxcBYkt-0-j2D3zS333LN92X9ltfNt1zzvSS_Z8-3WvN9Wb_VdfOt1nwvyW_Od1bc2M61wz89K74BQnZUXQ)

## CSIT-2410 Selected Performance Comparisons

Comparisons 24.10 vs 24.06
- [2n-icx 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkNEOgiAUhp9Gb5oNSLObLjIfoLVegOGxsSnSAV319IFaZFdt7MDP-Q7n8BtoQFio9lFeRCxHqAFBCXDnaHNYTbcG7Kwv2LvUcTVe-krZqQVa9W_UbYPWXky8ywyAIYmNYSnZJixdu4juNW4g4FLVyAPNVCLFPaGEXIFpCjtKxC3hQx0qRIefsTM_Cz16mZVzvsbWyOcS2abFgrH2oZfEqTzPRD6ud69Wc_zDJUfxFuz3x4MREzLwpocfXyjxvrj45cvYP1Ydtns_WlbGXW8bCWhm_QJp6Hnp)

## CSIT-2410 Selected Performance Coverage Data

CSIT-2410 VPP v24.10 coverage data
- [2n-icx 200ge cx7 mlx5 ip4](https://csit.fd.io/coverage/#eNpVjsEOwiAQRL8GLwYDWwinHtT-hyG4sSRICSDSv2-JB-plk5k3s5mEDk22ix-JuhFQ0aX9kuF6_gkQnDUD7s14fnKnJYQ_UjB2COLCGY37d52wx8K8HjKeWlMpMPZCCNxUVVBn-nZV9oaOqHvFBtGEmk5pXr4PpzN6s45Etu1Hq6XktAEmgz2f)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
