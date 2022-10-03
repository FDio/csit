Spectre and Meltdown Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following section displays the output of a running shell script to tell if
system is vulnerable against the several "speculative execution" CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.45

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64
  CPU is Intel(R) Atom(TM) CPU C3858 @ 2.00GHz

  Hardware check
  * Hardware support (CPU microcode) for mitigation techniques
    * Indirect Branch Restricted Speculation (IBRS)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates IBRS capability: YES (SPEC_CTRL feature bit)
    * Indirect Branch Prediction Barrier (IBPB)
      * CPU indicates IBPB capability: YES (SPEC_CTRL feature bit)
    * Single Thread Indirect Branch Predictors (STIBP)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates STIBP capability: YES (Intel STIBP feature bit)
    * Speculative Store Bypass Disable (SSBD)
      * CPU indicates SSBD capability: NO
    * L1 data cache invalidation
      * CPU indicates L1D flush capability: NO
    * Microarchitectural Data Sampling
      * VERW instruction is available: NO
    * Indirect Branch Predictor Controls
      * Indirect Predictor Disable feature is available: NO
      * Bottomless RSB Disable feature is available: NO
      * BHB-Focused Indirect Predictor Disable feature is available: NO
    * Enhanced IBRS (IBRS_ALL)
      * CPU indicates ARCH_CAPABILITIES MSR availability: YES
      * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: NO
    * CPU explicitly indicates not being affected by Meltdown/L1TF (RDCL_NO): YES
    * CPU explicitly indicates not being affected by Variant 4 (SSB_NO): NO
    * CPU/Hypervisor indicates L1D flushing is not necessary on this system: NO
    * Hypervisor indicates host CPU might be affected by RSB underflow (RSBA): NO
    * CPU explicitly indicates not being affected by Microarchitectural Data Sampling (MDS_NO): NO
    * CPU explicitly indicates not being affected by TSX Asynchronous Abort (TAA_NO): NO
    * CPU explicitly indicates not being affected by iTLB Multihit (PSCHANGE_MSC_NO): NO
    * CPU explicitly indicates having MSR for TSX control (TSX_CTRL_MSR): NO
    * CPU supports Transactional Synchronization Extensions (TSX): NO
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
    * CPU microcode is known to cause stability problems: NO (family 0x6 model 0x5f stepping 0x1 ucode 0x20 cpuid 0x506f1)
    * CPU microcode is the latest known available version: NO (latest version is 0x36 dated 2021/05/10 according to builtin firmwares DB v222+i20220208)
  * CPU vulnerability to the speculative execution attack variants
    * Affected by CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Affected by CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Affected by CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Affected by CVE-2018-3640 (Variant 3a, rogue system register read): YES
    * Affected by CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Affected by CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Affected by CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): NO
    * Affected by CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): NO
    * Affected by CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
    * Affected by CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
    * Affected by CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
    * Affected by CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO
    * Affected by CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): NO
    * Affected by CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): NO
    * Affected by CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka Spectre Variant 1, bounds check bypass
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
  > STATUS: UNKNOWN (/sys vulnerability interface use forced, but its not available!)

  CVE-2017-5715 aka Spectre Variant 2, branch target injection
  * Mitigated according to the /sys interface: YES (Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: disabled, RSB filling)
  > STATUS: VULNERABLE (IBRS+IBPB or retpoline+IBPB is needed to mitigate the vulnerability)

  CVE-2017-5754 aka Variant 3, Meltdown, rogue data cache load
  * Mitigated according to the /sys interface: YES (Not affected)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-3640 aka Variant 3a, rogue system register read
  * CPU microcode mitigates the vulnerability: NO
  > STATUS: VULNERABLE (an up-to-date CPU microcode is needed to mitigate this vulnerability)

  CVE-2018-3639 aka Variant 4, speculative store bypass
  * Mitigated according to the /sys interface: NO (Vulnerable)
  > STATUS: VULNERABLE (Neither your CPU nor your kernel support SSBD)

  CVE-2018-3615 aka Foreshadow (SGX), L1 terminal fault
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-3620 aka Foreshadow-NG (OS), L1 terminal fault
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-3646 aka Foreshadow-NG (VMM), L1 terminal fault
  * Information from the /sys interface: Not affected
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-12126 aka Fallout, microarchitectural store buffer data sampling (MSBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-12130 aka ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-12127 aka RIDL, microarchitectural load port data sampling (MLPDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2019-11091 aka RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2019-11135 aka ZombieLoad V2, TSX Asynchronous Abort (TAA)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2018-12207 aka No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  CVE-2020-0543 aka Special Register Buffer Data Sampling (SRBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not affected)

  > SUMMARY: CVE-2017-5753:?? CVE-2017-5715:KO CVE-2017-5754:OK CVE-2018-3640:KO CVE-2018-3639:KO CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK
