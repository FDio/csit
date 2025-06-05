---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2502"
weight: 1
---

# CSIT-2502 Release Report

This section includes release notes for FD.io CSIT-2502. The CSIT report
was published on **Mar-12 2025**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2502_plan) pages.

## CSIT-2502 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

## CSIT-2502 Release Data

To access CSIT-2502 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2502`
  - `DUT` > `vpp`
  - `DUT Version` > `25.02-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v25.10 vs v24.10
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2410-24.10-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2502-25.02-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2502`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2502`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2502 Selected Performance Tests

CSIT-2502 VPP v25.02 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstuwjAQ_Jr0grayF7vphQM0_1G5zlKihuDaJip8PQYhbaK2EpWgXHzwSzPWjnc0kkPceHoN1M4KvSjKRYFlU6epmM4nafFtQC0QeucA9WPaeWrJBALsoLFfIIV4J3SSnqWwn2D6JTROwZN6A2mB4up4SiNY0xKKD_BdDV3tjyXw5VziWz1G621kNKkYIT15BkfymOZWuwHnN9HMN54MX0jKGYoUBmJ-fhuzl96sKTR74iupK4zb1HiGpB3XiTs3QM8NK6sT459cctmlv7nkbucS5ixd7hLeK0uYs3Qtl26YJZWzdLlL6l5ZUjlL13KJs6Srh27j16e_nq4OXCKuXg)
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsxSZcOFDyH8g4WxqRpmZtIpWvx60qbSJAKlJLLz74pRlrxzsayTFtmJ4j9Q-VXVT1osK6a_NU3T5e54X7iFYhjCEA2pu8Y-rJRQIcIAYGrdQrYdB0r5V_BzcuoQsG7swLaA-UVrtTHtG7nlC9AQ8tDC3vSuDTocS3eoK2H0nQrGKGjMQCzuQJLay2E85vooXvmJxcyMoFShQnYn5-m7CX7NYUu0-SK7krgvvceIG0n9dJ2zBBDw2rmz3jn1wKxaW_uRTO5xKWLB3vEl4qS1iydCqXzpglU7J0vEvmUlkyJUunckmyZJurYcPr_V_PNl-QgK8q)
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXOYhMuHFryD2TshUZN08U2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5pG-glUv9UmWXVLCtsOp-X6n5xm3-hj2gUwo4Z0NzlXaCebCTAASIHqJV6J-SaHmvlPsCzX0PHGh70K9QOKK0Op_xFZ3tCtYYweBh8OHDg84njB6Gg_jMJmmVMkB0FASf6pIxX-1HNn6qlwQay0pGlC5QojtT8fjmpfgt2Q7H7ImnJYxHc5dELVLspT9rzCD1NrGmPFf_lExefZvrEF_QJS55m-IRXyxOWPJ3Np0vmSZc8zfBJXy1PuuTpbD5Jnkx7M2zD5vjuM-03Dsuz8g)
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJ1iYnDpT8ozLOQiOc1FqbqOX1uFWlTQQcIrX04kMcW7OrGe9oJIe4Y9oEck-FXhf1usC6a9NSrJ7v049dQF0ijN4D6oe0Y3JkAgEOEDwDluU7oa_svh7JROjdXkPnFTyqV6gsUNweT-kL1jjC8gN4aGFo-UiCL2eSH4yCtp9R0KRjhozEAs4ESpnfHiY1f8uWDsNkpCVpFyhSmMj5_XZS_camp9B9kbSkuQhu0_AFquycJx78BD2PrG5OFf_mlM9OLXXKX9MpzJla4hTeLlOYM3U5p66aKZUztcQpdbtMqZypyzklmdLN3bDj_vQG1M03Bku94g)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91OwzAMhZ-m3CCj1iwrN1ww-h4oJIZV6zIrCZPG05NWk9xqgJi0sV3kon86p7LrT0dWQ9x4egnUPRZqUdSLAuvWplNx_3SbLr4LqEqELTOgukt3njrSgQAdmHnrAMvynSquyGmwbFfQ8gwqVT28QmWA4rJ_TkcwuiMsV-CdBWd9XwOf9zUOCopqP6KoqY2JsiUv4qQ_sfFyN_L80LXYtSct_tS4SJHCqJfvP03cb16vKbSfJK8MYxGHSaMfiWZaKe54pO4nVjeD4784ceZ0JCc-IyfMeTqCE14sT5jzdDJO58nTfJa30wGlNJRr2k2_M-LM6Ar2Us8ob6W_M8IL5ShvpFMxkhyp5sZt_Hr4b1LNF9WNkuk)
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd](https://csit.fd.io/report/#eNrtl91OwzAMhZ-m3CCjxiyUGy4YfQ8UErNV6zIrKZPG05NWk9xqgJi0sV3kon86p7LrT0dWY7cJ9BqpfSr0vKjmBVaNS6fi_vk2XUIbUZcIW2ZAfZfuArVkIgF6sNXCgyrLBSlW5A04ditoeAZKq8c3UBaoW_bP6YjWtITlCoJ34F3oa-DLvsZBQVHdRydqamOibCmIOOlPbLzcjTw_dC12E8iIPzUuUkdx1Mv3nybu92DWFJtPkleGsYjDptGPRDut1O14pO4nVtWD4784ceZ0JCc-IyfMeTqCE14sT5jzdDJO58nTwyxvpwNKaSjXtJt-Z8SZ0RXspZ5R3kp_Z4QXylHeSKdiJDnS9Y3fhPXw36TrL_juksk)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstOwzAQ_JpwQYvsbUx64UCb_0DG2dKINDVrE1G-HreqtIkAqUgtvfjgl2asHe9oJIe4ZXoK1D0UZlFUiwKrtklTMXu8TQt3AY1CGLwHNHdpx9SRDQTYQ-s-QCv1Qug1zbVyb2CHFbT-Hqr5M2gHFNf7UxrB2Y5QvQL3DfQN70vg8ljiWz1Bm_coaFIxQQZiASfyhObXuxHnN9HCt0xWLiTlAkUKIzE_v03YK7YbCu0nyZXUFcFdarxA2k3rxJ0foceGVfWB8U8u-ezS31zyl3MJc5ZOdwmvlSXMWTqXSxfMUpmzdLpL5bWyVOYsncslyZKpb_otbw5_PVN_AfP0ruI)
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVstqwzAQ_Br3UrZIG6vOpYek_o-iypvG1HHUlWJIv75KCKxNW0ghaS466MWM2NEOAwpxy_QSqHsqzLKolgVWbZOmYra4Twt3AY1CGLwHNA9px9SRDQTYQ_AMWqk3Qq9prpX7ADusoPWPUM1fQTuguD6c0gjOdoTqHbhvoG_4UAKfTyW-1RO02UVBk4oJMhALOJEnNL_ejzi_iRa-ZbJyISkXKFIYifn5bcJesd1QaD9JrqSuCO5S4wXSblon7v0IPTWsqo-Mf3LJZ5f-5pK_nkuYs3S-S3irLGHO0qVcumKWypyl810qb5WlMmfpUi5Jlkx91295c_zrmfoLKGGvrg)
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEX2EpNeOFDyD2TshUZNU7M2lcrrcatKmwg4RGrpxYc4tmZXM97RSI5py_QSqX-szLJqlhU2nc9Ldf90m3_cRzQKYRcCoLnLO6aebCTAAWJg0Eq9EwZNC63cB_jg19CFB2gWr6AdUFodTvmLzvaEag08eBg8Hzjw-cTxg1BQ_5kEzTImyI5YwIk-KQur_ajmT9XSYJmsdGTpAiWKIzW_X06q39huKHZfJC15LIK7PHqBtJvypH0YoaeJNe2x4r98CsWnmT6FC_qEJU8zfMKr5QlLns7m0yXzVJc8zfCpvlqe6pKns_kkeTLtzbDlzfHdZ9pvqXO0dg)
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEXJEmMuHFryD2SchUY4qbU2UcvrcatKmwg4RGrpxYc4tmZXM97RSA5xy_QSyD0Val3odYG6a9NS3K9u049dQFUijN4Dqru0Y3JkAgEOEDwDluU7oa_sTo9kIvRup6DzD6AfX6GyQHFzOKUvWOMIyw_goYWh5QMJPp9IfjAK2n5GQZOOGTISCzgTKGV-s5_U_C1bOgyTkZakXaBIYSLn99tJ9RubnkL3RdKS5iK4TcMXqLJznrj3E_Q0Mt0cK_7NKZ-dWuqUv6RTmDO1xCm8XqYwZ-p8Tl00U3XO1BKn6utlqs6ZOp9TkinV3Axb7o9vQNV8A6PJvmY)
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYWxT1kkNT_0dRpW1j4ihCUgPp11cxgbVJCw3YTQ46-MWM2fEOw-CYdoFeI3XLSq4qtapQtTafqsfn-3wJXURZI-y9B5QP-S5QRzoSoAOzaB1gXX-Q8IKcBuvtBlq_ACHF0xsIA5TWx-d8RKM7wnoDwVlwNhxn4MtpxtlARu1nYjTLGCF7CgyO9DHNrw8Dzi-qma4DaeZn4QwligMtP38as9-D3lJsv4hf6dfCDJNXPwDNeFI6-AF62phqesZ_-eSLTxf65Gf0CUueLvAJr5YnLHmazKd58qRKO527pG6rm1Rppgk9mi9HpZX-7hFeKUelkabyiHMkmzu3C9v-v0k2394Wk3E)
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd](https://csit.fd.io/report/#eNrtV8tqwzAQ_Br3UrZYW1T1kkNT_0dRpW1i4ihCUgPp11cxgbVJCw3YTQ46-MWM2fEOw-CYdoHeInWLSi4rtaxQtTafqseX-3wJXURZI-y9B5QP-S5QRzoSoAOjVg5EXa9IeEFOg_V2A61_AiHF8zsIA5TWx-d8RKM7wnoDwVlwNhxn4OtpxtlARu1nYjTLGCF7CgyO9DHNrw8Dzi-qma4DaeZn4QwligMtP38asz-C3lJsv4hf6dfCDJNXPwDNeFI6-AF62phqesZ_-eSLTxf65Gf0CUueLvAJr5YnLHmazKd58qRKO527pG6rm1Rppgk9mi9HpZX-7hFeKUelkabyiHMkmzu3C9v-v0k23wGGk1E)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OhDAQgJ8GL2YM7RbZiwdX3sN0y-xuE35qW3Hx6S24SSHGRM0WPPTCT2bKTPvlSyYY22p8Nlg9JNkuyXcJzWXpLsnm8dbddGVollLolAKa3bknjRVyg7BpQIozkDQ9IlUEtyQVL8C7AwjdK9sCych2D0QA2pNUTCqDgqW2qcwbuPf98BHZWODoStwfRQ1NqYfK9OlS-UsbPlq-Wh91zc0iHWofnHXt09Sp9znf7sXnc43cL_jcoo9aNJN-frphv_6geY1GvqP_yHh8PkM4TJOgmNe2vZpEL-eYF2PGukxVZHoVpiowUxo9DcCUruopjZ4uzjS0pyx6GoApW9VTFj1dnGk4T2Utz3Hs_SvS4fT-29T7a6JR0qsQDexoHHkDEKVrOhoH3sWJBnY0jrsBiLI1HY3D7uJEvaNZcdO0uh7_9WbFB9vfK94)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](https://csit.fd.io/report/#eNrtmM1OwzAMgJ-mXJBRk6V0Fw6MvgfqUrNF9CckYaw8PWmZ5E4ICdDScsilP7JTO_n0SVat6ww-WqzvkmyT5JuE56ryl2R1f-1vprY8SzkctAae3fgngzWWFmHVgpJHYGm6Q64ZrlkqX6DS1TNI02vXAcvYegtMArq90kJpi1Kkrq3tG_j37fAV1Too0de43ckG2soMpfnDqfSXPihavTqK-u7OIgc0FDxrm9L0vqec7zdDC0qDJa343CNFHdpJQz_dMa1_MmWDVr0jfWQ8P8qQHtQkKM9ru15PoqeDzIsxY2GqOlK9DFUdmiqProagypd1lUdX56ca3FURXQ1BVSzrqoiuzk81oKuqUcc4Av8Z6nB8_24C_jXTKOplmIb2NI6_IZjyRT2Nw-_8TEN7GkffEEzFop7GwXd-puRpVly1nWnGf8BZ8QEKUjVu)
  - [3n-spr 100ge e810cq avf 40tnlsw](https://csit.fd.io/report/#eNrtmM1OhDAQgJ8GL2YM7VLZi4ddeQ9TyuxuE35qW1F8egtu0iXGRM0WPPTCT2bKTPvlSyYY22l8Mlg_JGyf5PuE5rJyl2Szu3U3XRvKUgq9UkDZnXvSWCM3CJu2BKM0kDQ9IlUEtyQVz8D7Awg9KNsBYWRbAhGA9iRVJpVBkaW2rc0ruPdy_IpsLXB0Ne6PooG20mNp-ngu_aUPH61erI-67maRHrUPztr2aeo0-JzvN-MXcI3cr_jco49aNBcN_XTHfv1B8waNfEf_ken8fIZwoC6CYl7bDuoiej7IvJgyVqaqItXrUFWhqdLoagiqdF1XaXR1earBXc2iqyGoZuu6mkVXl6ca0FXZyLc4Av8Z6nh8_24C_jXTKOp1mIb2NI6_IZjSVT2Nw-_yTEN7GkffEEyzVT2Ng-_yTL2nrLhpO91M_4BZ8QETwjam)
  - [3n-spr 200ge cx7 mlx5 40tnlsw](https://csit.fd.io/report/#eNrtmM1KxDAQgJ-mXmSkzSbWiwfXvodk03E30J-QxNr69KZ1IS2CKG6Mh1z6w0w6k3x8MNTYXuOTweY-Y_us3GeklLW7ZLuHa3fTjSEsJzAoBYTduCeNDXKDsOs4GKWB5PkRiSrEWA7ILbTNyEDoSdkeClbcHaAQgPYkFZXKoKC57RrzCu79MH9HdhY4uiq3R9FCV-u5OHk8F__UiY_WL9ZHXX-byIDaBzeN-zR1mnzOV9vxS7hG7td87NJHLZpVS9_ds1__rHmLRr6h_8hygj5DOFiroNjWtpNaRc9HWVZLRnSyKpG9FFkVnixJzoYhS2I7S5KzMcj-gbM0ORuGLI3tLE3OxiAb1FnZyjGNxr8AOx_gP5yMf8w1CXspruF9TWNxGK4ksq9pKI7BNbyvaSQOw5VG9jUNxDG4el9ZddX1ul3-GbPqHddpU_4)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](https://csit.fd.io/report/#eNrlVctuwyAQ_Br3Um0FpMi59NDU_1Fh2NYoJCYsjpp-fYkVdW21ueYQXwBpZvY1WkG5T_hOGF4qvanqTaVq78pRrV4fy5UCKS0UHGMEpZ_KK2FAQwirPXj7BVKIT1RR4loKewAX3Ra6njJlY7cg1Vq0IC1g7sDH58HFw-Btew5QQqLtemgjnfOpt0u-P8kZdUNmtOhnyBETg7NamRa7E3Oud8ACk9Cw4rcxJmSkSU3X22TFRzI7JP-NLBvHxAxbLJmAdp4tn-IEvUyvbkbGjfwjawIWfpCCFuDjf-3eqZ_LsvOe3VzWct54N3XzsO_TbvwzdfMDNwYJuA)
  - [3n-icx 100ge cx6 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCUupeekjqf1QYb2tUHFMWR05fX2JFXVttrjk4F0CaGWZ3RwhKfcQ3Qv9S6F1R7gpVuiYvxWZ7n7foSWmh4BACKP2QTxE9GkLY7MHZEaQQH6iCtONTM0LnRw1tT4mSsZ8g1bOoQVrA1IILj0MTvgZn65M-34i27aEOdLJTr2e7P96MNkNiNOsXyAEjg4tSmRbaI3MuNsB8E9Gw4LcvJiSkWUmXu2TFezQdkvtGlk1TYobNgcxAu3RLxzBDz8Mrq4lxnfTIGo9SWC8FrT_F_7pdZ5o3FeaKs7yph3nld6mru30fu-mv1NUPeDcJqA)
  - [3n-spr 200ge cx7 mlx5 ip4udpquic](https://csit.fd.io/report/#eNrlVctugzAQ_Bp6qbaynVj00kNT_qMyZlNQTXC9BiX9-jgoyoKa9JhDuNiWZmZfo5UpdgE_Cd1bpjdZvslU3lTpyFbvz-kKjpQWCgbvQemX9Aro0BDCameAfAAlxBcqL-0-H9BEaN1eQ91RpGjsN0j1KkqQFjDW0Ph1X_mfvrHlKUQKirbuoPR0yqg-zhn_pGe06iOjST9DBgwMzqplmq8PzPmvB5aYgIY1l9aYEJEmVd1ulBXbYFqk5hdZNg6KGTbZMgHtPFs8-Al6nl9ejIy7eUjWOJTCOiloEV5ea_hhPV2apY_t6NKW9M47qounXRfa8Q_VxRGcgRPo)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qbYCHOpeekjqf1QYNrUVElOWRE1fX2JFXVtVmlN7iC-AmBl2hxGCUh_xldA_F3pVVKtCVZ3LQ1Eu7_MUPSktFBxCAKUf8iqiR0MI5Q46-wFSiDdUQeKTFPYdXHAbaHtKlIzdgFw8igakBUwtdGGRbGhOYu9CPqc3Lm9iXJfQBDoVVS_noj86YNTtE6O5rwlywMjgpGGmhfbInMs2WGAiGlZ8u2NCQhr1dMUry9bRbJG6T2TtcGHMsDmcEWinJdMxjNDzFVb1wPiHJMkaj9J6KWgugf5m-TZy3bv5vNBLXm8mybm90CuW_z5XXd_t-rgd_lJdfwFbjRD-)
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVcFuwyAM_ZrsMnkKpDSnHdblPyYC7hKNNAjTKu3Xl0bVnGjqeuqluQDiPWM_P1lQ7AN-Ebr3TG2ycpPJsrVpyYqP17QFR1LlEg7eg1Rv6RTQoSaEYgetGUDk-TdKL8ywtgN0blDQ9BQpavMDYrXOaxAGMDbQ-lU0vr7EOuvTM7226RLDtoDa0yWn_Lzm_FMAo3YfGU1lzZADBgZn9TLNN0fm3FTBfB1Qc8CvOCZEpElJd6Ry2DboDqk9IceO_WKGSdZMQDNPGY9-gl47WFYj4_E-ktEOhXEip4XY-Z_ip3B1bxcznbekPouPC5vOO4of76qqXnZ96MY_VFVnfncQ7g)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFOwzAQfE24oEW20xAuHCj5B3LsLYnqNovXrVRejxtVbCJEe4JDe7Etz4x3xyPLnIaIb4zhuaiWRb0sTN37PBTly32eYmBTKQN7IjDVQ15FDGgZody2wBRBK_WOhjQ-aeU-wJNfQzdw4mTdGvTiUbWgHWDqoKdFctQe1cFTPmiwPm9iXJXQEh-rmtdT1R8tCOp3SdDc2AzZYxRw1rHQqDsI54wPUdiIViTf9oSQkCdNXTArslW0G-T-E0U73pgwXI5nArp5yXSgCXq6w7oZGf-RJTsbULugFd9MpOc8X0myO39Dr_Q3s9eT5c290gue_z7ZqrnbDnEz_qlV8wViJxSW)
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp](https://csit.fd.io/report/#eNrlVUFuwyAQfI17qTbCONSnHpr4HxWGTW0Vx4glVtLXh1hR11bV5NQe4gsgZobdYYSg2Ad8J3Svmdpk5SaTZWvTkBVvz2kKjqQSEgbvQapVWgV0qAmh2GsgH0AK8YHS5-ZYDqgjdO6ooOkpUtTmE_L1i6ghN4Cxgdavo_H1Re6sTyf12qZNDLsCak-XsnJ7LfujB0btITKaOpshAwYGZy0zzTcn5twywhIdULPm2x8TItKkqztuWbYLukNqv5C145Uxw6SAJqCZl4wnP0Gvl1hWI-Nf0iSjHebG5YKWE-ot04-S7cEu6aX-5vaB0lzeS71j-u-zVdXTvg_d-Leq6gx2ZRsu)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZIsiX70kNS_0dQ5E1tcJytpJikX18pDcimGAotLYRc9JpZ7Y6GRc4fLG4c9s-ZXGflOhNl14Qhy1ePYbK9E5IJGIlAyKewstijdghigM6cgDP2ioI4VpyZN9DjDjoq4vEWuAH0bdh6Q_F0G-NazkQBpHJwqpBcgKejh6GxMal4uSb9UkFCm6NPaKhrhoxoEzgrONGoPU84SzISX1vUKSDoSJBHNynmm2JT-M7qPbruHdMd8eESwQRzJpiZZ_ZnmqDXJyzrC-PfnKS7kz91kv7cSSVlrj7VFVxUpapuuy0X9N5MZy75SXc_f7U_Zf0wHOz-8nfK-gPmivT7)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVctqwzAQ_Br3UrZYsiT70kNS_0dR5U1tcJytpBjSr6-cBtamGAotLYRc9JqRdmeHRSEePD4H7B8zvc3KbSbLrklDVmzu0-T7IHUuYSQCqR_SymOPNiDIAQJ5EHn-ipIEViJ3b2DHHXSkpuMXEA4wtmkbHcFgo1LYQCtyqYBMAcEoLSREOkYYGj8FlU-XoF8yYLQ5RkZTXgtkRM_gImGmUXuacdZkMN96tHwhyWEoYpgl802xfH3n7R5D9478xlQ4Jrhkzgxzy8jxRDP0UsKyPjP-zUm6OflTJ-nPnTRaF-ZTnRKyKk113W25ovdqOnPNT7r5-av9qeu74eD3579T1x_8QPPj)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYju3kZQ_r8h_Fc9QlkKaa7QXar5_XFZSwFQYbG5S--MKRfHR0EI5pF3AdcbgvzKqoVoWq-jYvRflwm7cwRGWEgokIlLnLp4ADuoigRogUQArxjIok1lL4F3DTBnrSYPUTSA-YunxLnmB0SWtsoZNCaSBbQrTaSAWeIoxteKdUjyfKT_yMtq-J0VzVApkwMLgol8Oo289izongeBfQcUJWw1DCOCvme1o5exPcFmN_QH4id41xn41hSPolb9rTDD01sGqOEf_kIl1d_JmL9NcuWmNK-yFNS1VXtr7ocfxa7oVM5Bkv6erlL86laW7GXdge_0rTvAGZpe5z)
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput](https://csit.fd.io/report/#eNrtVdtqwzAM_ZrsZWjYip30ZQ_t8h_Dc7QlkKTCdkPbr6_bFZwwAoMNCqUvvnAk6xwdhH3YOnr31L1mepOVmwzLto5Llq-f4-Y6j1ogjMyA-iWeHHVkPAEO4NkBCvFFyNLuy5FMgL7ba2hZgRTiA6QFCk28BsswmKAU1dBIgQq4yMEXSkuEwLsAQ-3OZfHtWvYHh4TWu5DQyGyGjOQSOKOcwrg5TGKWhaQM48iklCgoQYH8hM4v5ab0T2d68u2R0hvn1qUAGw2aYHZeORx4gl6bWFaXiBu6yQ83_-4m38DNQuu8-NanJK7KYnXv47mg-I4mdMlTfnj6z3Oqq6dh6_rLX6qrE2Qe_bM)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](https://csit.fd.io/report/#eNrtVsGKwjAQ_ZruRUaarLF78bBu_0NiOmqhxtkkLerXm0ph2l0W9iAIrZck5L3JzOTxSHw4Odx4rFaJWifZOpFZWcQhef-cxclVXqpUQkMEUs3jymGF2iNIC6U5g0jTPUoS-CFS8w262UFJi02orcXKw3KxBWEAwyHuQjfXBe3RYoMglpHYBmzbI23h2szyq8v8qwxGizowGosbIA06BgdVM40Olx7nr16Yrx1qDui1yJSAvlfUv1rm4J3TR_TlFfmEeHeMmygTQ8IM04YL9dDuHrP8zniupvTS9CGa0nM1nZ5Nx-7S6Zl05B6VanqP6bDnMfr0h6r0UvXRXlX5mz254_3_q_Iba3YbQQ)
  - [3n-icx 100ge cx6 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFuwyAQRU_jbqqp7AnEqy6a-B6Rg6eJJUwQ4NTp6YujSGOr7SJVmmzYGIv_YQaevoQPB0cbT_o1k6usXGVYtk38ZIu35zg47VHmCEdrAeVL_HOkqfYECwOtGqDI8x2hLdSwbAbo9CChtWITemNIe1iKLRQKKOzj7C7Y3n-M-nbcwTRuLITrS6FvVVlt-sBq7GWmHMmxOGuSbXZ_Ys-vrbO_dlTzgsmJ2BLIT5r66YTsfXd1R779JF4Qb4Z1FSGwVKh5lXCyE_VybWV1dtyVmE3E_kLM_j8xTBm7jhg-OmOYMnZLYnfImEgZu46YeHTGRMrYLYlxxmT1ZA6uO78ZZfUFgZrb7g)
  - [3n-spr 200ge cx7 mlx5 vxlan](https://csit.fd.io/report/#eNrtVcFuwjAM_ZruMnlqA1lPHAb9D5SmHlRKg-WEqvD1BFbJrabtwgEJcUmiPL_Yz09WQjwwbgO6VabXWbnOVNk2ackWX-9pYxeUzhX0RKD0RzoxOjQBYeENBGJQeb5DRYUdyh5NhM4NGlpabuPRe3QBPpc1FBYw7tNtPzjjwam6qdMjnbGOPfiGrxnVZsz4K72gzTEKmoqaIT2ygLNqJYz2J4n5T4NQDKMRzkSahEQMk7r-liqMbzYdhvaMQkuNEtwmWwQq7DxXPNEEHftXVreIx3hILw_v8pAe4-Fgr8KefAJ_RD7V7I2-0cu3u-dNV2_-wN3t_9PVBY5r_bs)
  - [3n-spr 200ge cx7 mlx5 gtpu sw](https://csit.fd.io/report/#eNrtlkFqwzAQRU_jbsoUW5HqVRdNfI-g2NPEICuDJLtJT185BMampZASTBbaWMb_j2ekxwf5cHS49WjeMrXOynUmyraJj2z1_hwXZ7xQuYCBCIR6iW8ODWqPsLIaPDkQeb5HQUV9KgfUATpzUtCS3IbeWjQeXuUOihowHOLXfaDef476bvyJbdzYS2yuvX40ZrXpA6txnJkyoGNxNifb6HBmz1_Tc4l2qLlmsim2BPSTuX7bJHs_nO7Qt1_IBfFwWK8jCpaKet4lnGmiXk-urC6OpblR4vZPbrQIN5HydjM38QB5Eylvd-a2TN5kytvN3OQD5E2mvN2ZG-dNVU_26LrLvVJV34f_604)
  - [3n-spr 200ge cx7 mlx5 wireguard](https://csit.fd.io/report/#eNrtVl1rwyAU_TXZy3AYW4kve1iX_1FsvGsDxsrVpO1-fU0o3ITB9jJWqHtR8Zzr_TgcMMQjwjaAfS3kpqg2hahak5Zi9facNrRBSC7Y4D0T8iWdECzoAGzlNAsemeB8D8KXzbkaQEfW2bNkrV9vY-8c2MBKWaodKxsG8ZDue-NPLcK-12hKzqOz4TTyd-OjzuCYW7zfcn8phFDTR0JTeQtkACRwUTfR_OFCnO-6oRCNoClm1iRRIoRZXT-3TJEfqDsI7SdQ-DQ6YjRJqhnYLLPGi5-ht0lW9cS4t67-X9df0tXfVdfs3JqBV7Nz6uP7VOXmU_X4PlW5-VT9sU9l_eSO2E3_YFlfAY7PK30)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](https://csit.fd.io/report/#eNrtVkFOwzAQfE24oEWxG5NeOFDyD5Q4S2uROIttCuH1uKHSJkJckNLmkIttecbrWY9Gsg-dw2ePzUOidkm-S2Ru6jgkm8fbOLnGS5VKOBKBVHdx5bDB0iNsLBj9CSJN9yhJ4Fak-g1qql9Bu55CB0KJbQVCA4aDocyQRx3pabCN_4C4U53qGBugxHjL_V63sXrpPbZV04Ot3UmHfDrr-CWK0fo9MBqlTpAjOgYnPTCNDj1z_u6MD5RRKJ_4aZjRgH4k6F_tc7EXV7bozRdyxeFlmaGjhSNQT4WEnkbo-VXzYmAsyW9a_Z7Bb5rbb7nm-7J-y-vmW675XpLfs-c7W_N9Wb-z6-Y7W_O9JL8536q4sZ1rh3-6Kr4BdJ1UjQ)

## CSIT-2502 Selected Performance Comparisons

Comparisons v25.02 vs v24.10

- [2n-icx 100ge e810cq avf 1c 64B PDR](https://csit.fd.io/comparisons/#eNqNkMGOwiAQhp-mXgwGsFgvHtQ-wGbjCxCcGpKW4kCb1adfaKvIzYQM_Mw3zPA7aEF5uB6K6lTwCqEBBKMgnIvtcT3fOvCLvuAQUuf1dBkrdW8y9Dq80LCN1kYx8yEzAqYkto6XjBJebkLE8Jp0kHBtGpSJ5oZo9UcYpTfglsGeUXUncmxSherxPbaIs7BzlKJe8g12Tj9zZFeeMsb7h82Jn_p3IappvXp1VuIXLgVKduA_P56MmJFRtgPkvgjKCRebED98mfqvTI_dIY4m6lU_-FYDukX_A13XeeM)

## CSIT-2502 Selected Performance Coverage Data

CSIT-2502 VPP v25.02 coverage data

- [2n-icx 200ge cx7 mlx5 ip4](https://csit.fd.io/coverage/#eNpVjsEOwiAQRL8GLwaDq4RTD2r_wxDcWBKkBBDp39uNh62XTWbezGYKBnTVz3EQ5irA5FDWK06X_U-AVkAG3Mh4vCvTltIfaZgZgj4okHn9bgtyLE3LJhOld12CUk-EdHTdNLRVvkLX3LAZLVd8OpMw465M8-cebMXolkFo2r61KKXHLykAPaM)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
