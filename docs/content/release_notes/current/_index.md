---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2406"
weight: 1
---

# CSIT-2406 Release Report

This section includes release notes for FD.io CSIT-2406. The CSIT report
has been published on **Jul-10 2024**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2406_plan) pages.

The release notes of the previous CSIT release can be found
[here]({{< relref "../previous/csit_rls2402" >}}).

## CSIT-2406 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})
- [VPP Device]({{< relref "vpp_device" >}})

## CSIT-2406 Release Data

To access CSIT-2406 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2406`
  - `DUT` > `vpp`
  - `DUT Version` > `24.06-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v24.06 vs v24.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2402-24.02-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2406-24.06-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2406`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2406`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2406 Selected Performance Tests

CSIT-2406 VPP v24.06 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsrdNw4UCb_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0U5aKoFgVWbZOmYvZ4mxbuAho1h8F7QHOXdkwd2UCAPbTuA7RSL4Re071W7g3ssILWG5ibZ9AOKK73pzSCsx2hegXuG-gb3pfA5bHEt3qCNu9R0KRiggzEAk7kCc2vdyPOb6KFb5msXEjKBYoURmJ-fpuwV2w3FNpPkiupK4K71HiBtJvWiTs_Qo8Nq-oD459c8tmlv7nkL-cS5iyd7hJeK0uYs3Quly6YJZOzdLpL5lpZMjlL53JJslTWN_2WN4e_Xll_AeM_rqY)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIGznupYek_o-iypvG1HHUlWJIv75KCKxNW0ghaS466MWM2NEOAwpxy_QSqHsqymVRLQus2iZNxWxxnxbuAho1h8F7QPOQdkwd2UCAPQTPoJV6I_SaHrVyH2CHFbTewNy8gnZAcX04pRGc7QjVO3DfQN_woQQ-n0p8qydos4uCJhUTZCAWcCJPaH69H3F-Ey18y2TlQlIuUKQwEvPz24S9Yruh0H6SXEldEdylxguk3bRO3PsRempYVR8Z_-SSzy79zSV_PZcwZ-l8l_BWWcKcpUu5dMUsmZyl810yt8qSyVm6lEuSpbK-67e8Of71yvoLF6yvcg)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEX24jRcOFDyD2TshUZNU7M2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5py_QSqX-s6mXVLCtsOp-X6v7pNv-4j2jUAnYhAJq7vGPqyUYCHCAGBq3UO2HQ9KCV-wAf_Bq6YGBhXkE7oLQ6nPIXne0J1Rp48DB4PnDg84njB6Gg_jMJmmVMkB2xgBN9UhZW-1HNn6qlwTJZ6cjSBUoUR2p-v5xUv7HdUOy-SFryWAR3efQCaTflSfswQk8Ta9pjxX_5FIpPM30KF_QJS55m-IRXyxOWPJ3Np0vmyZQ8zfDJXC1PpuTpbD5Jnur2Ztjy5vjuq9tvl7y0Og)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFuwjAQfE24VIuSrUNOPRTyj8p1lhLVCdbajaCvr0FIm4j2EAnKxYc4tmZXM97RSPZhz_Tmyb5k5Tqr1hlWbROX7Pn1Kf7YelT5CgbnANUy7pgsaU-APXjHgHn-QegKc6gG0gE6eyihdQpW6h0KAxR2p1P8vNGWMP8E7hvoGz6R4OZCcsUoaPMVBI06JshALOBEoJS53XFU87ds6dBMWlqidoEC-ZGc328n1VvWHfn2m6QlzkVwE4cvUGGmPOHoRuhlZFV9rvg3p1xyaq5T7p5OYcrUHKfwcZnClKnbOXXXTKmUqTlOqcdlSqVM3c4pyVRZL_o9d-c3YFn_AJEQvio)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91Kw0AQhZ8m3shIdsyPN15Y8x6y7o42NN0Ou7FQn95NKExCVSy0thd7kT_OCTOZj8OQ0G88vQTqHrNykdWLDOvWxlN2_3QbL74LWOQVbJkBi7t456kjHQjQgalaB5jn76RYkdNg2a6g5QJUqR5eQRmgfjk8xyMY3RHmK_DOgrN-qIHP-xoHBUW1H72osY2ZsiUv4qw_sfFyN_H80LXYtSct_ti4SD2FSS_ff5q437xeU2g_SV4ZxyIOE0c_Ec28Ur_jibqfWN2Mjv_ixInTkZz4jJww5ekITnixPGHK08k4nSdPVZG20wGlOJRr2k2_M-LE6Ar20sAobaW_M8IL5ShtpFMxkhyVzY3b-PX431Q2X3vik0k)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasZY0u9lFu7zH8GytDU1dYWeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7r6TVQ-5yVi6xaZFg1Np6yx_l9vPg2YJHPYMcMWDzEO08t6UCADky1dKDyfEmKFTkNlu0aGi5AlerpDZQB6lb9czyC0S1hvgbvLDjr-xr4cqhxVFBU-9GJGtuYKDvyIk76Exuv9iPPD12LXXvS4o-Ni9RRGPXy_aeJ-93rDYXmk-SVYSziMHH0I9FMK3V7HqmHiVX14PgvTpw4nciJL8gJU55O4IRXyxOmPJ2N02XyNCvSdjqiFIdyS7vpd0acGN3AXuoZpa30d0Z4pRyljXQuRpKjsr5zW78Z_pvK-gufQ5Mp)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsxWl64dCS_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0U5bKolgVWbZOm4n5xmxbuAho1g8F7QHOXdkwd2UCAPbTuA7RSL4Re01wr9wZ2WEHrZ1DNn0E7oLjen9IIznaE6hW4b6BveF8CH48lvtUTtHmPgiYVE2QgFnAiT2h-vRtxfhMtfMtk5UJSLlCkMBLz89uEvWK7odB-klxJXRHcpcYLpN20Ttz5EXpsWFUfGP_kks8u_c0lfzmXMGfpdJfwWlnCnKVzuXTBLJmcpdNdMtfKkslZOpdLkqWyvum3vDn89cr6C3sgryo)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIGznOpYcm_o-iypvG1HHUlWpIv75KCKxNW0ghaS466MWM2NEOAwpxx_QcqHssymVRLQus2iZNxezpPi3cBTRqDoP3gOYh7Zg6soEAewieQSv1Sug1LbRy72CHNbR-DtXiBbQDipvDKY3gbEeo3oD7BvqGDyVwdSrxrZ6gzUcUNKmYIAOxgBN5QvOb_Yjzm2jhWyYrF5JygSKFkZif3ybsNdsthfaT5ErqiuAuNV4g7aZ14t6P0FPDqvrI-CeXfHbpby7567mEOUvnu4S3yhLmLF3KpStmyeQsne-SuVWWTM7SpVySLJX1Xb_j7fGvV9Zfr36v9g)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFuwjAQfE16qbayjUO49ADNPyrX3paIELZrg0RfX4OQNlHbQyQolxzi2JpdzXhHIzmmHeNrxPa5KFdFtSpM1YS8FLPlY_5xG41VczgQgbFPecfYoosIpoNIDFqpDzSkcaGV_4RAYQMNzaFavIH2gGl9OuUveteiURvgLkAX-MRhXi4cPwgFDfskaJYxQA7IAg70SRmtj72aP1VLg2N00pGlC5Qw9tT8fjmpfme3xdh8obTksQju8-gF0n7Ik47UQy8Tq-pzxX_5RJNPI32iG_pkpjyN8MncLU9mytPVfLplnuyUpxE-2bvlyU55uppPkqeyfuh2vD2_-8r6GzJztL4)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJ4tRcOFDyD2SchUY4qbU2UcvrcatKmwg4RGrpxYc4tmZXM97RSA5xy_QSyD0W9brQ6wJ116aluH-6TT92AVW5gtF7QHWXdkyOTCDAAYJnwLJ8J_SV3emRTITe7Wro_Ar0wytUFihuDqf0BWscYfkBPLQwtHwgwecTyQ9GQdvPKGjSMUNGYgFnAqXMb_aTmr9lS4dhMtKStAsUKUzk_H47qX5j01Povkha0lwEt2n4AlV2zhP3foKeRqabY8W_OeWzU0ud8pd0CnOmljiF18sU5kydz6mLZkrlTC1xSl0vUypn6nxOSabq5mbYcn98A9bNNy6dvq4)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZY29jKpYem_o-iStvGxFGEpAbSr69iAmuTFhqwmxx08IsZs-MdhsEh7jy9BuqeimpVyFWBsjXpVDw-36eL7wIuyhr2zgEuHtKdp45UIEALum4tYFl-kHCCrALjzAZaV4OoxPINhAaK6-NzOoJWHWG5AW8NWOOPM_DlNONsIKPmMzKaZIyQPXkGR_qY5taHAecX1UxXnhTzk3CGIoWBlp8_jdnvXm0ptF_Er_RrYYZOqx-AejwpHtwAPW1MNj3jv3xy2acLfXIz-oQ5Txf4hFfLE-Y8TebTPHmSuZ3OXZK31U0yN9OEHs2Xo9xKf_cIr5Sj3EhTecQ5qpo7u_Pb_r-par4BhGuT0Q)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYmzjqpYek_o-gStvExFGEpAbSr69iAmuTFhqwmx508IsZs-MdhsEhHjytA7UvRbUq5KpA2Zh0KmbLx3TxbcB5uYCjc4Dzp3TnqSUVCNCClhsLoiw3JJwgq8A4s4PGLUBU4vkNhAaK2_NzOoJWLWG5A28NWOPPM_D1MuNqIKPmIzKaZAyQI3kGB_qY5ranHucH1UxXnhTzk3CGIoWelu8_jdnvXu0pNJ_Er3RrYYZOq--BejgpnlwPvWxM1h3jr3xy2acbfXIT-oQ5Tzf4hHfLE-Y8jebTNHmSuZ2uXZL_q5tkbqYRPZouR7mVfu8R3ilHuZHG8ohzVNUP9uD33X9TVX8Bp8yTsQ)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmEtuwyAQQE_jbqqpDMFxNl0k9T0qgicJkj8UqBv39MVuJGJVldoq2F2w8UczwMDTk0YY22p8Nlg9JtkuyXcJzWXpHslqe-9eujKUpWvolALKHtyXxgq5QVg1IMUZSJoekSqCG5KKF-DdAYTulW2BZGSzByIA7UkqJpVBwVLbVOYN3P9-mEQ2Fjgamq2Pooam1MPK9Omy8pcyfLR8tT7qiptEOtQ-OKnap6lT73O-3YvP5xq5H_C5RR-1aK7q-emG_fiD5jUa-Y5-kvH4fIZwmK6CYrq27dVV9HKOeTFmLMtURaY3YaoCM6XR0wBM6aKe0ujp7ExDe8qipwGYskU9ZdHT2ZmG81TW8hzb3r8iHU7vv3W9vyYaJb0J0cCOxpY3AFG6pKOx4Z2daGBHY7sbgChb0tHY7M5O1DuaFXdNq-vxrjcrPgBPCCxu)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ4jpNNywouQdKnaG1yMfYpjScHidUmkQICVCddOFNPpqxPfbTk0Y2ttX4ZLC6j9JtlG0jlsnSPaLVw6176cowHq_hqBQwfue-NFZYGIRVA1KcIInjPTKV4CaJxSuUqnwBoTtlW0jSZLODRADag1RcKoOCx7apzDu4_10_i2wsFGhYut6LGppS90uzx_PS3-qgaPlmKeqqm0SOqCk4KZvS1KGjnJ83QwMKjQWN-NojRS2aUUG_3TGNf9ZFjUZ-IE0ynB9lCAdqFBTTtW2nRtHzQWb5kLEwVRWoXoaq8k2VBVd9UGXLusqCq_NT9e4qD676oMqXdZUHV-en6tFVWctTaIH_DbU_vqvrgP_MNIh6Gaa-PQ3trw-mbFFPQ_M7P1PfnobW1wdTvqinofGdnyl5muY3Tavr4Q44zT8BhHQ1_g)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYwtLdvXhw7XsYSmd3SfqDgNX69NK6CW2MiZql9cClP5kBBr58yQRjW41PBqv7JDsku0NCd7J0j2TzcOteujKUpVvolALK7tyXxgq5Qdg0BRilgaTpCakiuCepeAbeHUHoXtkWSEb2BRABaM9SMakMCpbapjKv4P6LYRbZWOBoaLY9iRqaUg9L08fL0l_q8NHyxfqoq24W6VD74Kxsn6bOvc_5fjN-ANfI_YjPPfqoRTMp6Kc79uOPmtdo5Dv6Scbz8xnCgZoExXxt26tJ9HKQu3zMWJmqilSvQ1WFpkqjqyGo0nVdpdHV5akGd5VFV0NQZeu6yqKry1MN6Kqs5Vtsgf8MdTi-f9cB_5ppFPU6TEN7GtvfEEzpqp7G5nd5pqE9ja1vCKZsVU9j47s8U-9plt80ra7HO-As_wCN5Dc2)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYloWtFw-79j0MS8ddkv4QwNr69NK6Cd2YGI2LeODSn8wAA1--ZIKxvcYng81DxvZZuc9IKWv3yDa7W_fSjSE038KgFBB65740NsgNwqbjYJQGkudHJKoQYzkgt9A2IwOhJ2V7KFhxf4BCANqTVFQqg4LmtmvMK7j_wzyP7CxwNIRtj6KFrtbz4uTxvPinSny0frE-6uq7iAyoffCicJ-mTpPP-Wo7fgjXyP2Yj136qEWzKum7e_bjnzVv0cg39JMsJ-gzhIO1CorLte2kVtHzUZbVkhGdrEpkr0VWhSdLkrNhyJLYzpLkbAyyf-AsTc6GIUtjO0uTszHIBnVWtnJMrfEvwM4H-A874x9zTcJei2t4X1NbHIYriexraopjcA3va2qJw3ClkX1NDXEMrt5XVt10vW6XO2NWvQNfqlSO)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctOwzAQ_JpwQYtsNyG9cKDkP5BjL8Sq27hep6J8PW5UsYmg1x6ai21pZvY1WplSH_Gd0L8U1aaoN4Wqnc1HsXp9zFf0pErxDMcQQJVP-RXRoyaE1R6c-QIpxCeqIHEthTmADXYLXU-JkjZbkGotWpAGMHXgQjnYcBicac8Bckg0XQ9toHM-9XbJ9yc5o3ZIjGb9DDliZHBWK9NCd2LO9Q5YoCNqVvw2xoSENKnpepus-Ih6h-S-kWXjmJhhsiUT0MyzpVOYoJfp1c3IuJF_ZLTHzPdS0AJ8_K_dO_VzWXbes5vLWs4b72bVPOz7uBv_zKr5Af0mCeg)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCYse99JDU_6gw3taoOKYsjpy-vsSKurbaXHNwLoA0M8zujhAU-4BvhO4lK_ZZuc9UaZu0ZJvdY9qCI5WLLRy9B5U_pVNAh5oQNgewZgQpxAcqL824bUbo3FhA21OkqM0nSPUsapAGMLZgfT40_muwpj7r041o2h5qT2c79Xqx--PNaDNERpN-gRwxMLgolWm-PTHnagPM1wE1C377YkJEmpV0vUtWvAfdIdlvZNk0JWaYFMgMNEu3ePIz9DK8spoYt0mPjHYohXFS0PpT_K_bdaZ5V2GuOMu7epg3fpdF9XDoQzf9lUX1Az2OCdg)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctugzAQ_Bp6qbayHQi99NCU_6iM2QZUE1yvQUm-Pg6KsqCmPeYQLralmdnXaGUKncdPQvuWZJsk3yQqb6p4JKv353h5SyoVaxicA5W-xJdHi5oQVjsN5DwoIbaonDT7fEAdoLX7DOqOAgVtvkGqV1GCNIChhsalfeV--saU5xAxKJq6g9LROaP6uGT8lZ7Rqg-MRv0MGdAzOKuWaa4-MOe_HliiPWrWXFtjQkCaVPV3o6z48rpFao7IsnFQzDDRlglo5tnCwU3Qy_zyYmTczUMy2qIUxkpBi_DyVsMP6-nSLH1sR5e2pHfe0ax42nW-Hf_QrDgBZGAUGA)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbMe99NDE_4gwbGorJKYsiZq-vsSKuraqNKf2EF8AMTPsDiMExT7gmtC9ZOUyq5aZqjqbhix_fUxTcKQKsYCj96CKp7QK6FATQr6HznyAFOINlZf4LIV5B-vtFtqeIkVttiCLhWhAGsDYQueLaHxzFjvr0zm9tmkTwyaHxtO5qFpdiv7ogFF7iIymvibIEQODk4aZ5tsTc67bYIEOqFnx7Y4JEWnU0w2vLNsEvUPqPpG1w4Uxw6RwRqCZlownP0IvV1jVA-MfkiSjHUrjpKC5BPqb5fvI9WDn80Kveb2bJOf2Qm9Y_vtcy_ph34fd8JeW9Rcj_BEu)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVU1vwyAM_TXZZfIUyNdph3X5HxMBd4lGGoRplfbXl0bVnGjqeuqluQDiPWM_P1lQGDx-Edr3pNgk1SaRVWfikmQfr3HzlmSelnBwDmT-Fk8eLSpCyHbQ6RFEmn6jdEKPpRmht2MB7UCBgtI_IPIybUBowNBC5_KgXXOJtcbFZwZl4iX6bQaNo0tO-XnN-acARs0-MBrLWiAH9Awu6mWaa4_MuamC-cqj4oBfcUwISLOS7kjlsK1XPVJ3Qo6d-sUMHa2ZgXqZMhzdDL12sKonxuN9JK0sCm1FSiux8z_FT-Hq3qxmOm9JfRYfVzaddxQ_3tWiftkNvp_-0KI-A0YOER4)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVctuwyAQ_Br3Um0FfsS99JDU_1Fh2NRWSLxlSaT060usqGuranJqD8kFEDPD7jBCcBwCvjH6l6xaZfUqy-vepSErlo9pCp7zUi3gQAR5-ZRWAT0aRih2LTAF0Eq9Y04an7WyH-DIbaAbOHI0dgO6XKgWtAWMHfRURkvtSe0dpYMG49ImhnUBLfGpav56rvqjBUHdPgqaGpshBwwCzjoWGnVH4VzwIQoT0Ijk254QIvKkqStmRbYOZovcf6JoxxsThk3xTEA7LxmPNEHPd1g3I-M_smRrPGrrteK7ifSS5xtJdu_u6JX-ZvZ2sry7V3rF898nWzUPuyFsxz-1ar4AK24Uxg)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCbMenHpr6HxWGTW0Vx4glVtLXl1hR11bV5NQe4gsgZobdYYSgOAR8I3TPWbnNqm2mqs6mIctfHtMUHKlCbGD0HlTxlFYBHWpCyPcayAdQQryj8tIcqxF1hN4dS2gHihS1-QBZbEQD0gDGFjpfROObs9xZn04atE2bGHY5NJ7OZdXrpeyPHhi1h8ho6myBjBgYXLTMNN-emHPNCEt0QM2ab39MiEizrm64Zdku6B6p-0TWTlfGDJMCmoFmWTKe_Ay9XGJVT4x_SZOMdiiNk4LWE-o10_eS7cGu6aX-5vaO0lzfS71h-u-zLeuH_RD66W8t6y9AhBte)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiT70kNS_0dQ5E1tcJytpJikX185DcimGAotLYRc9JpZ7Y6GRT4cHG48ds-ZWmfFOhNFW8chy1ePcXKdF5JpGIhAyKe4ctih8Qiih9aegDP2ioI4lpzZNzDDDlqS4_EWuAUMTdwGS-PpdoxrOBMSSOfgtVRcQKBjgL52Y1Lxck36pYKE1seQ0FjXDBnQJXBWcKJRc55wlmQkvnFoUkDUkaCAflLMN8Wm8J0ze_TtO6Y7xodLBBvNmWB2njmcaYJen7CoLox_c5LuTv7USfpzJ7VSuf5UJ7koC13edlsu6L2Zzlzyk-5-_mp_quqhP7j95e9U1QetMfUr)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYsiT70kNS_0dR5U1tcJytpBjSr6-cBtamGAotLYRc9JqRdmeHRSEePD4H7B8zvc3KbSbLrklDVmzu0-T7IFVuYCQCqR7SymOPNiDIAQJ5EHn-ipIEViJ3b2DHHXSkpuMXEA4wtmkbHcFgo1LYQCtyqYBMAcEoLSREOkYYGj8FlU-XoF8yYLQ5RkZTXgtkRM_gImGmUXuacdZkMN96tHwhyWEoYpgl802xfH3n7R5D9478xlQ4Jrhkzgxzy8jxRDP0UsKyPjP-zUm6OflTJ-nPnTRaF-ZTnRKyKk113W25ovdqOnPNT7r5-av9qeu74eD3579T1x_C5_QT)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRKWFhYkIlL7Lp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAFenO6j)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsh659JDU_1FUeVsbbGeRFJPk66OkAdkUQ6GFQMhFD2ZXO7PDohC3Ht8Ddq-F2hRmUwjT1mkpyvVz2nwXhGQaRiIQ8iWdPHZoA4IYIJAHwdgXCuJub0a0Efpur6AlCZyxD-AOMDbpGh3BYKOUWEPDmZBAuoSgpeICIu0iDLU_lxVv17I_OGS03sWMJmYzZESfwRnlHEbNYRKzLCRnWI82pyRBGYoYJnR-KTenf3rbY2iPmN84ty4HuGTQBHPzyvFAE_TaRFNdIm7oJj3c_LubdAM3tVKl_tYnuVgZvbr38VxQfEcTuuQpPTz95zlV1dOw9f3lL1XVCSx1_eM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVk2LwjAQ_TXdi4w02X7sxcO6_R8S01ELNc4maVF_vakUpt1lYQ-C0HpJQt6bzEwej8T5k8WNw3oVpesoX0cyr8owRO-fizDZ2skkzqAlApksw8pijcohSAOVPoOI4z1KEvghYv0Nqt1BRcnGN8Zg7SBLtiA0oD-EXejnpqQ9GmwRRBaIXcC2O9KUtsssv_rMv8pgtGw8o6G4EdKiZXBUNdPocBlw_uqF-cqi4oBBi0zx6AZF_atlDt5ZdURXXZFPCHfHuA4yMST0OK2_0ADt7zEv7oznakovTR-iKT1X0_nZdOounZ9JJ-5Rmc7vMR33PEWf_lCVXqo-2qtp8WZO9nj__6bFDR0OG4k)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFuwjAQRU-TbqpBiXGSVReF3AMFZwqRHDOyHRp6ehyENInaLqgobLyJI_9vz9hPX7LzB4sbh_otyVdJuUpE2TbhkyzfX8NgtRMyLeBIBEIuwp9FjbVDWBpo1QBZmu5QUKaGohmg00MOLcmN741B7aCQW8gUoN-H2Z2n3n2O-nbcwTR2LCTW10LfqrLa9J7V0MtMOaJlcdYk22h_Ys-vrbO_tljzgsmJ2OLRTZr66YTs_bB1h679Ql4QboZ1FSCwlKl5FX-iiXq9trK6OB5KjCKxvxCj_ycmYsZuIyaenTERM3ZPYg_ImIwZu42YfHbGZMzYPYlxxvLqxRxsd3kz5tUZE77cNg)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFuwjAM_Zrugjy1oaUnDrD-B0pTDyqlwXJCVfb1BKjkVtN24YCEuCRRnl_s5ycrPhwZdx7tOim2SblNVNk2cUmWm0Xc2HqVpyvoiUDln_HEaFF7hKXT4IlBpekeFWVmKHvUATo7FNBSvgsn59B6WOU1ZAYwHOJtP1jtwKq6qeMjnTaWHbiGrxnV15jxV3pBm1MQNBY1Q3pkAWfVShgdzhLznwahaEYtnIk0CQnoJ3X9LVUY36w79O0PCi02SnATbREoM_Nc4UwTdOxfWd0inuMhvT18yEN6joeDuQp78Qm8i3yp2Rt9o7dvD89bUX24I3e3_6-oLk0O_es)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlsGKgzAQhp_GXsoUTWM97aFd36OkOtsKMR2S6Lb79BtLYZRdFroU6SEXI_7_OJN8_BDnzxb3DvVbku-SYpeIoqnDI1lvl2Gx2gmZbqAnAiFX4c2iRuUQ1kaBIwsiTY8oKKsuRY_KQ6svOTQk974zBrWDjTxAVgH6U_h69NS5z0E_DD8xtR16ifd7rx-NWa07z2oYZ6L0aFmczMk2Ol3Z89f0XKIsKq4ZbYotHt1ort82yd4Pq1p0zRdyQTgc1quAgqWsmnbxVxqp95Mryptjbm4Uuf2TG83CTcS8PcxNvEDeRMzbk7nNkzcZ8_YwN_kCeZMxb0_mxnnLy4U52_Z2r8zLbx-f65Y)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVstuwyAQ_Br3UlFhYtdcemjq_4iI2SaWMEELdh5fH2xFWluV2kvVSKEXQMws-xiNhA8HhI0H85aV66xaZ6JqdVyy1ftz3NB4UfBXNjjHRPESTwgGlAe2sop5h0xwvgPh8uZUDaAC68ypZK0rNqG3FoxneZnLLcsbBmEf73vtji3Crleoc86DNf448rfjo1bjmFt83HJ_KYRQ3QdCY3kLZAAkcFE30dz-TJzvuqEQhaAoZtYkUQL4WV0_t0yRn6g68O0FKHwaHTGaKNUMbJZZw9nN0Nskq3pi3FtX96_rL-nq7qprcm5NwKvJOfXxfSpT86l8fJ_K1Hwq_9inZf1kD9hN_-CyvgJAfyvF)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYti12l64dCS_6gSZ2kt8lhstxC-HjdU2kSIC1LaHHKxLc94Nbujkex8a3HvsHqOkl2U7iKZmjIs0Wr7GDZbOaniNZyJQKqncLJYYe4QVg0Y_Qkijg8oSeBGxPodSirfQNuOfAsiEZsChAb0R0PKkEMd6LFvKvcB4aa41DGNhxydTNYHXYfquXNYF1UHTWkvOuTLVccvUYyWJ89okDpCzmgZHPXANDp2zPm7M36QB6H84qdhRj26gaB_tc_FXm1eozNfyBX7yTJDBwsHoB4L8R0N0OtU06xnzMlvWvyewG-a2m-55Pu2fsv75lsu-Z6T35PnWy35vq3f6r75Vku-5-Q35zvJHprW1v0_Pcm-AT9tVNU)

## CSIT-2406 Selected Performance Comparisons

Comparisons 24.06 vs 24.02
- [2n-icx 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkE0OwiAQhU_TbgyGYn_cuFB7AGO8AMGpIWkpDrRRTy_0R2ziwoQEHu8bZngGahAWrruoOESsQKgAQQlw52izX423BuykL9g567gaLn2lbNUCvXYz6rZeay9G3jk9YDCxNiylOWHpmjKC7jVuIOBSVcgDzRSR4kESSm_AdALbhIo74X0VKkSLn7EzP0ty9DIrJ7_CxsjXEsnTw4Kx9qmXxKk8T0QxrLlXozn-kZKjeAP2--MhiBHped3B71zy71yG_rFqsdn50bIybjtbS0Az6TdmuHnv)

## CSIT-2406 Selected Performance Coverage Data

CSIT-2406 VPP v24.06 coverage data
- [2n-icx 200ge cx7 mlx5 ip4](https://csit.fd.io/coverage/#eNpVjsEOwiAQRL8GLwaDWyinHqz9D0NwY0mQEkCkf98SD9TLJjNvZjMRLepkFjcQORKQwcb9ku52_gngrK8G3Kvx_KRGs_d_JGNoEPiF9TTs31XEFvPzesg4anShwNgLwV91kRlVom9bRGuogKpVjOdVyOkU5-X7sCqh0-tARN1-tGpKTBsssj2p)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
