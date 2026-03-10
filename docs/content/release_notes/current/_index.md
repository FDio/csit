---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2602"
weight: 1
---

# CSIT-2602 Release Report

This section includes release notes for FD.io CSIT-2602. The CSIT report
has been published on **Mar-11 2026**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2602_plan) pages.

## CSIT-2602 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

## CSIT-2602 Release Data

To access CSIT-2602 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2602`
  - `DUT` > `vpp`
  - `DUT Version` > `26.02-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v26.02 vs v25.10
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2510-25.10-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2602-26.02-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2602`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2602`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2602 Selected Performance Tests

CSIT-2602 VPP v26.02 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsxUm4cKDkP5BxtjQiTc3aRJSvx60qbSJAKlJLLz74pRlrxzsaySFumJ4C9fdFuSjqRYF116apuH24Tgv3ASuFMHoPWN2kHVNPNhDgAJ37AK3UC6HXdKeVewM7LqHzBirzDNoBxdXulEZwtidUr8BDC0PLuxL4eCjxrZ6g7XsUNKmYISOxgDN5QvOr7YTzm2jhWyYrF5JygSKFiZif3ybsJds1he6T5ErqiuAuNV4g7eZ14tZP0EPD6mbP-CeXfHbpby7587mEOUvHu4SXyhLmLJ3KpTNmyeQsHe-SuVSWTM7SqVySLJXN1bDh9f6vVzZf3syudg)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsxUm4cGjJfyDjbGlEmpq1iVS-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoO1D8W5bKolwXWXZum4n5xmxbuA1YKYfQesLpLO6aebCDAAYJn0Eq9EnpND1q5d7DjCjpvoDIvoB1QXO9PaQRne0L1Bjy0MLS8L4FPxxLf6gnafkRBk4oZMhILOJMnNL_eTTi_iRa-ZbJyISkXKFKYiPn5bcJesd1Q6D5JrqSuCO5S4wXSbl4n7vwEPTasbg6Mf3LJZ5f-5pK_nEuYs3S6S3itLGHO0rlcumCWTM7S6S6Za2XJ5CydyyXJUtncDFveHP56ZfMFEzmvQg)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXO1km4cKDNP5CxFxo1Tc3aVCqvx60qbSLgEKmlFx_i2JpdzXhHIznEHdNLoP6pqJZFsyyw6VxaisXzffpxH7BWCHvvAeuHtGPqyQQCHCB4hlKpd0Jf0mOp7Ac47zbQeQ21foXSAsX18ZS-YE1PqDbAg4PB8ZEDV2eOH4SCus8oaJIxQfbEAk70SZlfH0Y1f6qWBsNkpCNJFyhSGKn5_XJS_cZmS6H7ImlJYxHcptELVNopTzz4EXqeWNOeKv7LJ599mumTv6JPmPM0wye8WZ4w5-liPl0zTzrnaYZP-mZ50jlPF_NJ8lS1d8OOt6d3X9V-A5IRtAo)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFqwzAQfI17KVvsjWyfemjifxRV3jamsiNWqkny-iohsDZtD4akuehgWWJ2mdEOA_Jhx_TqyT5n5Tqr1xnWXRuXbPXyGH9sPVY5wugcYPUUd0yWtCfAAbxjwDz_IHSF2dcj6QC93ZfQOQWVeoPCAIXt6RQ_b7QlzD-BhxaGlk8kuLmQ_GAUtP0KgkYdM2QkFnAmUMrc9jCp-Vu2dGgmLS1Ru0CB_ETO77eT6nfWPfnuSNIS5yK4icMXqDBznnBwE_Qysro5V_ybUy45tdQpd0unMGVqiVN4v0xhytT1nLppplTK1BKn1P0ypVKmrueUZKpsHoYd9-c3YNl8A4otvfo)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasdoku9nFurzH8GxtDU1dYaeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7j6TVQ-5QVi6xaZFg1Np6y2fN9vPg2YJkj7JgBy4d456klHQjQgSkbB5jnH6RYkdNg2a6g4TmoQj2-gTJA3bJ_jkcwuiXMV-CdBWd9XwNfDjWOCopqt52osY2JsiMv4qQ_sfFyP_L80LXYtSct_ti4SB2FUS_ff5q4371eU2g-SV4ZxiIOE0c_Es20UrfnkXqYWFUPjv_ixInTiZz4gpww5ekETni1PGHK09k4XSZP5TxtpyNKcSi3tJt-Z8SJ0Q3spZ5R2kp_Z4RXylHaSOdiJDkq6ju38evhv6movwC4FJMJ)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91qwzAMhZ8muxkasdYku9lFu7zH8GytDU1dYWeF7unnhIISuo0V2rUXvsgf5wQp-jiIhG7r6TVQ-5wVi6xaZFg1Np6yx_l9vPg2YJkj7JgBy4d456klHQjQgamWDlSeL0mxIqfBsl1DwzNQhXp6A2WAulX_HI9gdEuYr8E7C876vga-HGocFRTVfnSixjYmyo68iJP-xMar_cjzQ9di1560-GPjInUURr18_2nifvd6Q6H5JHllGIs4TBz9SDTTSt2eR-phYlU9OP6LEydOJ3LiC3LClKcTOOHV8oQpT2fjdJk8lbO0nY4oxaHc0m76nREnRjewl3pGaSv9nRFeKUdpI52LkeSoqO_c1m-G_6ai_gLbdZLp)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIGz9y6SGp_6Oo8qYxdRx1pZimX18lBNamLaSQNBcd9GJG7GiHAfmwZXr21D1mxTKrlhlWbROnbLa4jwt3HkuFMDgHWD7EHVNHxhNgD639AK3UK6HTNNfKvoMZVtC6Eqr5C2gLFNaHUxzemo5QvQH3DfQNH0rg06nEt3qCNrsgaFQxQQZiASfyhObW-xHnN9HCN0xGLkTlAgXyIzE_v03YKzYb8u0nyZXYFcFtbLxA2k7rhL0boaeGVfWR8U8uueTS31xy13MJU5bOdwlvlSVMWbqUS1fMUp6ydL5L-a2ylKcsXcolyVJR3_Vb3hz_ekX9BXatrvo)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_BrnUjZIWz9y6aGp_6Mo8qYxdRx1pRrSr68SAmuTFlJImosOejEjdrTDgHzYMb166p6yYplVywyrtolT9vj8EBfuPJYKYXAOsJzHHVNHxhNgD94xaKXeCJ2mhVb2A8ywhtaVUC1WoC1Q2BxOcXhrOkL1Dtw30Dd8KIEvpxJn9QRtPoOgUcUEGYgFnMgTmtvsR5zfRAvfMBm5EJULFMiPxPz8NmGv2WzJt18kV2JXBLex8QJpO60T9m6EnhpW1UfGP7nkkkt_c8ndziVMWbrcJbxXljBl6Vou3TBLecrS5S7l98pSnrJ0LZckS0U963e8Pf71ivobqwuvxg)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsJY9eOLTkP5CxFxo1Tc3aVCpfj1tV2kTAIVJLLz7EsTW7mvGORnKIO6aXQP1TUa2KZlVg07m0FI_L-_TjPmCtEPbeA9YPacfUkwkEOEDwDFqpd0KvaaGV_QDn3QY6X0OzeAVtgeL6eEpfsKYnVBvgwcHg-MiBz2eOH4SCus8oaJIxQfbEAk70SZlfH0Y1f6qWBsNkpCNJFyhSGKn5_XJS_cZmS6H7ImlJYxHcptELpO2UJx78CD1PrGlPFf_lk88-zfTJX9EnzHma4RPeLE-Y83Qxn66ZpzLnaYZP5c3yVOY8XcwnyVPV3g073p7efVX7DSzItI4)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJNom5cKDkH8g4C41wUmvtRi2vx60qbSLgEKmlFx_i2JpdzXhHI9mHLdOrJ_uUVetMrTNUXRuXbPV8H39sPdY5wugcYP0Qd0yWtCfAAbxjwDz_IHSF2auRdIDe7ivoXA3q8Q0KAxQ2x1P8vNGWMP8EHloYWj6S4MuZ5AejoO0uCBp1zJCRWMCZQClzm8Ok5m_Z0qGZtLRE7QIF8hM5v99Oqt9Z9-S7L5KWOBfBTRy-QIWZ84SDm6DnkanmVPFvTrnk1FKn3DWdwpSpJU7h7TKFKVOXc-qqmSpTppY4Vd4uU2XK1OWckkxVzd2w5f70Bqyabye6vn4)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UjZYW2z10kNT_0dRpG1i4ihCUgPp11cxgbVJCwnYTQ86-MWM2fEOw-AQ957eA3UvRbUs5LJA2Zp0Kp5eH9PFdwHrEuHgHGC9SHeeOlKBAC3ourWAZbkm4QRZBcaZLbSuBlGJ5xUIDRQ3p-d0BK06wnIL3hqwxp9m4Nt5xsVARs1nZDTJGCEH8gyO9DHNbY4Dzi-qma48KeYn4QxFCgMtP38asz-82lFov4hf6dfCDJ1WPwD1eFI8ugF63phsesZf-eSyTzf65Gb0CXOebvAJ75YnzHmazKd58iRzO126JP9XN8ncTBN6NF-Ocitd7xHeKUe5kabyiHNUNQ9273f9f1PVfAPAnZOR)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYG2z10kMT_0dRpW1i4ihCUgPJ11cxgbVJCw3YTQ86-MWM2fEOw-AQ957eAnUvRbUs5LJA2Zp0Khavj-niu4B1iXBwDrB-SneeOlKBAC1oubYgynJNwgmyCowzW2hdDaISz-8gNFDcnJ_TEbTqCMsteGvAGn-egavLjKuBjJrPyGiSMUIO5Bkc6WOa2xwHnB9UM115UsxPwhmKFAZavv80Zn94taPQnohf6dfCDJ1WPwD1eFI8ugF62ZhsesZf-eSyTzf65Gb0CXOebvAJ75YnzHmazKd58iRzO127JP9XN8ncTBN6NF-Ociv93iO8U45yI03lEeeoah7s3u_6_6aq-QLj_pNx)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmEtuwyAQQE_jbqqpbILtbLpI6ntUBE8SJH8oUDfu6YvdSNiqKrVVsLtg449mgIGnJ43QplX4rLF6jNJ9lO8jkovSPqLN7t6-VKVJFhPopASSPdgvhRUyjbBpQPALJHF8QiIT3CYxfwHWHYGrXpoWkjTZHiDhgOYsJBVSI6exaSr9Bvb_MEwiGgMMNUmzE6-hKdWwMnm6rvylDBctX42L2uJmkQ6VC86qdmny3Lucb_fi8plC5gZ8btFFDepJPT_dsBt_VKxGLd7RTTIen8vgFtMkyOdrm15OotdzzIsxY12mMjC9CVPpmSkJnnpgSlb1lARPF2fq21MaPPXAlK7qKQ2eLs7Un6eiFpfQ9v4V6XB6_63r_TXRIOlNiHp2NLS8HoiSNR0NDe_iRD07GtpdD0Tpmo6GZndxos7RtLhrWlWPd71p8QEC7CwO)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmEtOwzAQQE8TNmhQ7CZpNywouQdKnaG1yMfYpjScHidUmkQICVCddOFNPpqxPfbTk0Y2ttX4ZLC6j9JttN5GfC1L94hWD7fupSvDs5jDUSng2Z370lhhYRBWDUhxAhbHe-SK4YbF4hVKVb6A0J2yLbCUbXbABKA9SJVIZVAksW0q8w7uf9fPIhsLBRqeZntRQ1Pqfmn-eF76Wx0ULd8sRV11k8gRNQUnZVOaOnSU8_NmaEChsaARX3ukqEUzKui3O6bxz7qo0cgPpEmG86MM4UCNgmK6tu3UKHo-yHU-ZCxMVQWql6GqfFPlwVUfVPmyrvLg6vxUvbuaBFd9UE2WdTUJrs5P1aOrspan0AL_G2p_fFfXAf-ZaRD1Mkx9exraXx9M-aKehuZ3fqa-PQ2trw-myaKehsZ3fqbkaZrfNK2uhzvgNP8EM6g1ng)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OhDAQgJ8GL2YM7RbYiwdX3sOUMrvbhJ_aVhSfXsBNCjEmarbgoRd-MtN22i9fMqmxrcYng9V9lByi7BDRTJbDI9o93A4vXRmaxhQ6pYCmd8OXxgq5Qdg1BRilgcTxCakiuCexeAbeHUHoXtkWSEL2BRABaM9SMakMChbbpjKvMPwX4yyyscDR0CQ9iRqaUo9L08fL0l_qcNHyxbroUN0i0qF2wUXZLk2de5fz_WbcAK6RuxGfe3RRi2ZW0E937MYfNa_RyHd0k0zn5zLEAGoWFMu1ba9m0ctBZvmUsTFVFaheh6ryTZUGV31Qpdu6SoOr61P17ioLrvqgyrZ1lQVX16fq0VVZy7fQAv8Z6nh8_64D_jXTIOp1mPr2NLS_PpjSTT0Nze_6TH17GlpfH0zZpp6Gxnd9ps7TJL9pWl1Pd8BJ_gE9GDbW)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1OxCAQgJ-mXsyYloXWi4dd-x6GpeMuSX8IYG19etu6CW1MjMZFPHDpT2aAgS9fMsHYTuOTwfohYYekOCSkkNX0SHb72-mla0PylECvFJD8bvrSWCM3CLuWg1EaSJqekKhMDEWP3EJTDwyEHpXtIGPZ_REyAWjPUlGpDAqa2rY2rzD9H-d5ZGuBoyEsP4kG2krPi5PHy-KfKnHR6sW66FTfJtKjdsFN4S5NnUeX89V23BCukbsxH7t0UYtmVdJ39-zGP2veoJFv6CZZTtBliAnWKii2a9tRraKXoyzKJSM4WRXJXous8k-WRGf9kCWhnSXR2RBk_8BZGp31Q5aGdpZGZ0OQ9eqsbOQQW-NfgJ0P8B92xj_mGoW9Flf_vsa22A9XEtjX2BSH4Orf19gS--FKA_saG-IQXJ2vrLxpO90sd8asfAcFflQu)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctuwjAQ_Jr0Um1lm4Zw6aE0_4Ece9tYGGK8DoJ-fU2EuolarhzIxbY0M_sarUypi7gh9G9FuS6qdaEqZ_NRLN6f8xU9qaVQcAwB1PIlvyJ61ISw2IMzJ5BCfKEKEldSmAPYYLfQdpQoabMFqVaiAWkAUwsuvPY2HHpnmkuAHBJN20ET6JJPfVzz_UnOqO0To1k_QY4YGZzUyrTQnplzuwMW6IiaFb-NMSEhjWq63SYrPqPeIblvZNkwJmaYbMkINNNs6RxG6HV6VT0w7uQfGe0x870UNAMf_2v3Qf2cl52P7Oa8lvPOu1nWT_su7oY_s6x_AHlGCcg)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCEtu99NDU_6gw3taoOKYsjpy8vsSKurbaXHNwLoA0M8zujhAU-4DvhO4ly3dZuctUaZu0ZJvXx7QFR6oQCg7egyqe0imgQ00Imz1YM4IU4hOVl2YsmhE6N-bQ9hQpavMFUj2LGqQBjC1Yvx0a_z1YU5_16UY0bQ-1p7OdervY_fFmtBkio0m_QA4YGFyUyjTfHplztQHm64CaBb99MSEizUq63iUrPoLukOwJWTZNiRkmBTIDzdItHv0MvQyvrCbGbdIjox1KYZwUtP4U_-t2nWneVZgrzvKuHuaN32VePez70E1_ZV79ALovCbg)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctOwzAQ_JpwQYtslzRcOFDyH8hxFhLhNIvXiVq-Hjeq2EQ8jj00F9vSzOxrtDLHPuALo3_M8l1W7DJTtHU6ss3TbbqCZ7NVBkYiMNu79Aro0TLCZm-BKYBR6g0NaXcoRrQROn_Ioek5crTuHbR5UBVoBxgbaOl-qOljaF11CpGComt6qIhPGc3zOeOP9ILWQxQ06RfIiEHARbVCo-YonP96EIkNaEXz3ZoQIvKsqr8bFcVrsB1y-4kimwYlDJdsmYFumS0eaYae51eUE-NiHrKzHrVyXitehZe_NXy1nq7N0ut2dG1LeuEdzcubfR-66Q_Nyy_fURP4)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCHNu99NDE_4gwbGorJKYsiZq-vsSKuraqNKf2EF8AMTPsDiMExT7gmtC9ZMUyq5aZqjqbhix_fUxTcKRKoeDoPajyKa0COtSEkO-hMx8ghXhD5SU-S2HewXq7hbanSFGbLchFKRqQBjC20PlFNL45i5316Zxe27SJYZND4-lcVK0uRX90wKg9REZTXxPkiIHBScNM8-2JOddtsEAH1Kz4dseEiDTq6YZXlm2C3iF1n8ja4cKYYVI4I9BMS8aTH6GXK6zqgfEPSZLRDqVxUtBcAv3N8n3kerDzeaHXvN5NknN7oTcs_32uRf2w78Nu-EuL-guejREO)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVcFuwyAM_ZrsMnkC0iSnHdblPyYC7hKNNAjTKt3Xj0bVnGjqeuqluQDiPWM_P1lQHAJ-ELrXrNhm1TZTVWfTkuVvz2kLjlQpFBy9B1W-pFNAh5oQ8j10ZgQpxCcqL81Y2hF6NxbQDhQpavMFclOKBqQBjC10fhONb86xzvr0zKBtusSwy6HxdM6p3i85_xTAqD1ERlNZC-SIgcFFvUzz7Yk5V1UwXwfUHPArjgkRaVbSDakctgu6R-q-kWOnfjHDJGtmoFmmjCc_Qy8drOqJcX8fyWiH0jgpaCV2_qf4IVw92NVM5zWpj-LjyqbzhuL7u1rUT_sh9NMfWtQ_wS8Q_g)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCHNu99JDU_4gwbGorJKYsiZS8vsSKuraqJqf2EF8AMTPsDiMExT7gmtC9ZcUqq1aZqjqbhixfPqcpOFKlUHD0HlT5klYBHWpCyPcNkA8ghfhA5SW-SmE-wXq7hbanSFGbLchFKRqQBjC20PlFNL65qJ316aBe27SJYZND4-lSVb1fq_5ogVF7iIymxibIEQODk46Z5tsTc274YIUOqFnybY8JEWnU1B2zLNsEvUPqzsja4caYYVI8I9BMS8aTH6HXO6zqgfEfWZLRDqVxUtBsIr3l-UGSPdgZvdLfzD5OlrN7pXc8_32yRf2078Nu-FOL-gulbxSm)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCHNunHpr6HxWGTW0Vx4glVtLXl1hR11bV5NQe4gsgZobdYYSgOAR8I3TPWbHNqm2mqs6mIctfHtMUHKlSKBi9B1U-pVVAh5oQ8r0G8gGUEO-ovDTHakQdoXfHAtqBIkVtPkBuStGANICxhc5vovHNWe6sTycN2qZNDLscGk_nsur1UvZHD4zaQ2Q0dbZARgwMLlpmmm9PzLlmhCU6oGbNtz8mRKRZVzfcsmwXdI_UfSJrpytjhkkBzUCzLBlPfoZeLrGqJ8a_pElGO5TGSUHrCfWa6XvJ9mDX9FJ_c3tHaa7vpd4w_ffZFvXDfgj99LcW9Re59Rs-)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiX70kNS_0dQ5E1tcJytpJikX18pDcimGAotLYRc9JpZ7Y6GRc4fLG4c9s-ZXGflOhNl14Qhy1ePYbK9E4oJGIlAqKewstijdghigM6cgDP2ioI4VpyZN9DjDjoq4vEWuAH0bdh6Q_F0G-NazkQBpHJwqpBcgKejh6GxMal4uSb9UkFCm6NPaKhrhoxoEzgrONGoPU84SzISX1vUKSDoSJBHNynmm2JT-M7qPbruHdMd8eESwQRzJpiZZ_ZnmqDXJyzrC-PfnKS7kz91kv7cSSVlrj7VFVxUpapuuy0X9N5MZy75SXc_f7U_Zf0wHOz-8nfK-gMpAfUL)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYsiT70kNS_0dR5U1tcJytpBjSr6-cBtamGAotLYRc9JqRdmeHRSEePD4H7B8zvc3KbSbLrklDVmzu0-T7IE0uYSQCaR7SymOPNiDIAQJ5EHn-ipIEViJ3b2DHHXSkpuMXEA4wtmkbHcFgo1LYQCtyqYBMAcEoLSREOkYYGj8FlU-XoF8yYLQ5RkZTXgtkRM_gImGmUXuacdZkMN96tHwhyWEoYpgl802xfH3n7R5D9478xlQ4Jrhkzgxzy8jxRDP0UsKyPjP-zUm6OflTJ-nPnTRaF-ZTnRKyKk113W25ovdqOnPNT7r5-av9qeu74eD3579T1x8-t_Pz)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRGWFgokIlL3Lp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAHbfe6D)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYiu30ZQ_t8h_DS7QlkKTCdkPbr6_bFZwwAoMNCqUvvnAk6xwdhH3YOnr31L1mepMVmwyLto5Llq-f4-Y6j0YgjMyA5iWeHHVkPQEO4NkBCvFFyLLaFyPZAH2319CyAinEB8gKKDTxGiqGwQalqIZGClTAJgdvlJYIgXcBhtqdy-LbtewPDgmtdyGhkdkMGcklcEY5hXFzmMQsC0kZ1pFNKVFQggL5CZ1fyk3pn8725NsjpTfOrUsBVTRoglXzyuHAE_TaxKK8RNzQTX64-Xc3-QZuGq1z861PSVwVZnXv47mg-I4mdMlTfnj6z3Oqy6dh6_rLX6rLE6cW_cM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVsGKwjAQ_ZruZZmlibbdyx7U_ofEdNRCjWOSFvXrN5XCtCvCHgSh9ZKEvDeZmTweifNHi2uH1U-ULKNsGcmsLMIQzRafYbKVk2ksoSECmX6FlcUKlUOQBkp9BhHHO5Qk8FvE-gSq2UJJ87WvjcHKQTrfgNCAfh92oZvrgnZosEEQaSC2AZv2SFPYNrNcdZnvymC0qD2jobgB0qBlcFA102h_6XEe9cJ8ZVFxQK9Fpnh0vaL-1TIHb606oCuvyCeEu2NcB5kYEnqY1l-oh3b3mOU3xms1pbemT9GUXqvp9Gw6dpdOz6Qj96hMpveYDnseo0__qEpvVZ_t1ST_MEd7uP1_k_wX_EQbWQ)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFuwjAQRU-TbqpByeAkqy4KuQcKzhQiOcayHRp6ehyENInaLqgobLyJI_9vz9hPX7LzB0sbR-otyVdJuUqwbJvwSZbvr2GwymGRIhyNASwW4c-SotoRLDW0coAsTXeEJpND0QzQqSGH1oiN77Um5aAQW8gkkN-H2Z03vfsc9e24g27sWAjX10LfqrLa9J7V0MtMOZJlcdYk28z-xJ5fW2d_banmBZMTscWTmzT10wnZ-2Hrjlz7Rbwg3AzrMkBgKZPzKv5kJur12srq4ngoMROJ_YWY-X9iGDN2GzF8dsYwZuyexB6QMREzdhsx8eyMiZixexLjjOXViz7Y7vJmzKszB_vcBg)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFuwjAM_Zrugjy1gbYnDrD-B0pTDyqlwXJCVfb1BKjkVtN24YCEuCRRnl_s5ycrPhwZdx7tOsm3SblNVNk2cUmWm0Xc2HpVpAp6IlDFZzwxWtQeYek0eGJQabpHRZkZyh51gM4OObS02oWTc2g9FKsaMgMYDvG2H6x2YFXd1PGRThvLDlzD14zqa8z4K72gzSkIGouaIT2ygLNqJYwOZ4n5T4NQNKMWzkSahAT0k7r-liqMb9Yd-vYHhRYbJbiJtgiUmXmucKYJOvavrG4Rz_GQ3h4-5CE9x8PBXIW9-ATeRb7U7I2-0du3h-ctrz7ckbvb_5dXF84n_cs)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlsGKgzAQhp_GvSyz6DTqaQ_b9T1KqrOtENOQRLft0zeWwii7LHQp0kMuRvz_cSb5-CHOHyxtHKn3JF8n5TrBsm3CI1l9vIbFKodFijAYA1i8hTdLiqQjWGkJzljANN0Rmqw-lgNJD5065tAasfG91qQcFGILWQ3k9-HrzpvefY_6dvyJbuzYCz9vvX40ZrXpPathnJkykGVxNifbzP7Enr-m5xJpSXLNZFNs8eQmc_22SfZ-WdmRa8_EBeFwWK8DCpayet7Fn8xEvZ1cWV0dS3Mzkds_uZlFuGHM293c8AnyhjFvD-a2TN5EzNvd3MQT5E3EvD2YG-ctr170wXbXe2VeXQAQNOtm)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVl1rwyAU_TXZy3CoXRpf9rAu_6PYeNcGjJWrSdv9-plQuAmD7WWsUPei4jnX-3E4YIhHhG0A-1KUm6LaFLJqTVqK1etj2tAGueaSDd4zuX5KJwQLOgBbOc2CRyY534P0ojlXA-jIOnsuWeuft7F3DmxgohRqx0TDIB7SfW_8qUXY9xqN4Dw6G04jfzc-6gyOueXbNfeXQgg1fSQ0lbdABkACF3UTzR8uxPmuGwrRCJpiZk0SJUKY1fVzyxT5jrqD0H4AhU-jI0aTpJqBzTJrvPgZep1kVU-MW-vq_3X9JV39TXXNzq0ZeDU7p96_T1VuPlX371OVm0_VH_u0rB_cEbvpH1zWnx-0K5U)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYtiN49eOLTkP1DiLK1F4iy2KYSvxw2VNhHigpQ2h1xsyzNeze5oJDvfWXx22DxG6T7K95HMdR2WaLO7D5ttnMxiCScikNlDOFlssHQIGwNafYKI4wNKErgVsXqDmupXULYn34FIxbYCoQD9UVOiyaEK9Nibxn1AuKnOdbTxUKKTaXZQbaheOodt1fRganvWIZ8uOn6JYrR-94wGqRPkhJbBSQ9Mo2PPnL874wdlEMovfhpm1KMbCfpX-1zsxZYtOv2FXHGYLDNUsHAEqqkQ39MIvUw1LwbGkvym1e8Z_Ka5_ZZrvq_rt7xtvuWa7yX5PXu-kzXf1_U7uW2-kzXfS_Kb850Wd6az7fBPT4tvDeJUpQ)

## CSIT-2602 Selected Performance Comparisons

Comparisons v26.02 vs v25.10

[2n-emr 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkEEOwiAQRU9TNwYDKK0bF9YewBgvQOrUNCkUB9pETy-0VWRnQgY-84YZvoUOage3Q1aUGS8QGkDQNfhztj2u51sLbtFXHHzqtJ4uQ2Xb6wS9DR_Ub6MxQcy8z4yAMYmd5YJRwsXGR_SvSQsRb3WDMtJcE1BIGKV34IbBntH6QeTYxIq6x-_YIszCTkGKask3qGz7SpF8VyaMc0-TEufqshDFtD69lJH4h0uekgrc78ejETMyym6A1JeccsLzjY8_vkz9V7pHdQijiWrVD65rAe2i32DXeec)

## CSIT-2602 Selected Performance Coverage Data

CSIT-2602 VPP v26.02 coverage data

[2n-emr 100ge e810cq avf ip4]()

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
