Spectre and Meltdown Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following section displays the output of a running shell script to tell if
system is vulnerable against the several speculative execution CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.44+

  Hardware check
   * Hardware support (CPU microcode) for mitigation techniques
     * Indirect Branch Restricted Speculation (IBRS)
       * SPEC_CTRL MSR is available: YES
       * CPU indicates IBRS capability: YES (SPEC_CTRL feature bit)
     * Indirect Branch Prediction Barrier (IBPB)
       * PRED_CMD MSR is available: YES
       * CPU indicates IBPB capability: YES (SPEC_CTRL feature bit)
     * Single Thread Indirect Branch Predictors (STIBP)
       * SPEC_CTRL MSR is available: YES
       * CPU indicates STIBP capability: YES (Intel STIBP feature bit)
     * Speculative Store Bypass Disable (SSBD)
       * CPU indicates SSBD capability: YES (Intel SSBD)
     * L1 data cache invalidation
       * FLUSH_CMD MSR is available: YES
       * CPU indicates L1D flush capability: YES (L1D flush feature bit)
     * Microarchitectural Data Sampling
       * VERW instruction is available: YES (MD_CLEAR feature bit)
     * Enhanced IBRS (IBRS_ALL)
       * CPU indicates ARCH_CAPABILITIES MSR availability: YES
       * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: YES
     * CPU explicitly indicates not being vulnerable to Meltdown/L1TF (RDCL_NO): YES
     * CPU explicitly indicates not being vulnerable to Variant 4 (SSB_NO): NO
     * CPU/Hypervisor indicates L1D flushing is not necessary on this system: YES
     * Hypervisor indicates host CPU might be vulnerable to RSB underflow (RSBA): NO
     * CPU explicitly indicates not being vulnerable to Microarchitectural Data Sampling (MDS_NO): YES
     * CPU explicitly indicates not being vulnerable to TSX Asynchronous Abort (TAA_NO): NO
     * CPU explicitly indicates not being vulnerable to iTLB Multihit (PSCHANGE_MSC_NO): NO
     * CPU explicitly indicates having MSR for TSX control (TSX_CTRL_MSR): YES
       * TSX_CTRL MSR indicates TSX RTM is disabled: YES
       * TSX_CTRL MSR indicates TSX CPUID bit is cleared: YES
     * CPU supports Transactional Synchronization Extensions (TSX): NO
     * CPU supports Software Guard Extensions (SGX): NO
     * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
     * CPU microcode is known to cause stability problems: NO (family 0x6 model 0x55 stepping 0x7 ucode 0x500002c cpuid 0x50657)
     * CPU microcode is the latest known available version: NO (latest version is 0x5003102 dated 2021/03/08 according to builtin firmwares DB v191+i20210217)
   * CPU vulnerability to the speculative execution attack variants
     * Affected by CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
     * Affected by CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
     * Affected by CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
     * Affected by CVE-2018-3640 (Variant 3a, rogue system register read): YES
     * Affected by CVE-2018-3639 (Variant 4, speculative store bypass): YES
     * Affected by CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
     * Affected by CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): YES
     * Affected by CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): YES
     * Affected by CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
     * Affected by CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
     * Affected by CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
     * Affected by CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO
     * Affected by CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): NO
     * Affected by CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): YES
     * Affected by CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka  Spectre Variant 1, bounds check bypass
   * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
   > STATUS: UNKNOWN (/sys vulnerability interface use forced, but it  s not available!)

  CVE-2017-5715 aka  Spectre Variant 2, branch target injection
   * Mitigated according to the /sys interface: YES (Mitigation: Enhanced IBRS, IBPB: conditional, RSB filling)
   > STATUS: VULNERABLE (IBRS+IBPB or retpoline+IBPB+RSB filling, is needed to mitigate the vulnerability)

  CVE-2017-5754 aka  Variant 3, Meltdown, rogue data cache load
   * Mitigated according to the /sys interface: YES (Not affected)
   * Running as a Xen PV DomU: NO
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka  Variant 3a, rogue system register read
   * CPU microcode mitigates the vulnerability: YES
   > STATUS: NOT VULNERABLE (your CPU microcode mitigates the vulnerability)

  CVE-2018-3639 aka  Variant 4, speculative store bypass
   * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
   > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

  CVE-2018-3615 aka  Foreshadow (SGX), L1 terminal fault
   * CPU microcode mitigates the vulnerability: N/A
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka  Foreshadow-NG (OS), L1 terminal fault
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (Not affected)

  CVE-2018-3646 aka  Foreshadow-NG (VMM), L1 terminal fault
   * Information from the /sys interface: Not affected
   > STATUS: NOT VULNERABLE (your kernel reported your CPU model as not vulnerable)

  CVE-2018-12126 aka  Fallout, microarchitectural store buffer data sampling (MSBDS)
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka  ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka  RIDL, microarchitectural load port data sampling (MLPDS)
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka  RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11135 aka  ZombieLoad V2, TSX Asynchronous Abort (TAA)
   * Mitigated according to the /sys interface: YES (Mitigation: TSX disabled)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12207 aka  No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
   * Mitigated according to the /sys interface: YES (KVM: Mitigation: Split huge pages)
   > STATUS: NOT VULNERABLE (KVM: Mitigation: Split huge pages)

  CVE-2020-0543 aka  Special Register Buffer Data Sampling (SRBDS)
   * Mitigated according to the /sys interface: YES (Not affected)
   > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

   > SUMMARY: CVE-2017-5753:?? CVE-2017-5715:KO CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK

::

  Spectre and Meltdown mitigation detection tool v0.44+

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64
  CPU is Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz

  Hardware check
  * Hardware support (CPU microcode) for mitigation techniques
    * Indirect Branch Restricted Speculation (IBRS)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates IBRS capability: YES (SPEC_CTRL feature bit)
    * Indirect Branch Prediction Barrier (IBPB)
      * PRED_CMD MSR is available: YES
      * CPU indicates IBPB capability: YES (SPEC_CTRL feature bit)
    * Single Thread Indirect Branch Predictors (STIBP)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates STIBP capability: YES (Intel STIBP feature bit)
    * Speculative Store Bypass Disable (SSBD)
      * CPU indicates SSBD capability: YES (Intel SSBD)
    * L1 data cache invalidation
      * FLUSH_CMD MSR is available: YES
      * CPU indicates L1D flush capability: YES (L1D flush feature bit)
    * Microarchitectural Data Sampling
      * VERW instruction is available: YES (MD_CLEAR feature bit)
    * Enhanced IBRS (IBRS_ALL)
      * CPU indicates ARCH_CAPABILITIES MSR availability: YES
      * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: YES
    * CPU explicitly indicates not being vulnerable to Meltdown/L1TF (RDCL_NO): YES
    * CPU explicitly indicates not being vulnerable to Variant 4 (SSB_NO): NO
    * CPU/Hypervisor indicates L1D flushing is not necessary on this system: YES
    * Hypervisor indicates host CPU might be vulnerable to RSB underflow (RSBA): NO
    * CPU explicitly indicates not being vulnerable to Microarchitectural Data Sampling (MDS_NO): YES
    * CPU explicitly indicates not being vulnerable to TSX Asynchronous Abort (TAA_NO): NO
    * CPU explicitly indicates not being vulnerable to iTLB Multihit (PSCHANGE_MSC_NO): NO
    * CPU explicitly indicates having MSR for TSX control (TSX_CTRL_MSR): YES
      * TSX_CTRL MSR indicates TSX RTM is disabled: YES
      * TSX_CTRL MSR indicates TSX CPUID bit is cleared: YES
    * CPU supports Transactional Synchronization Extensions (TSX): NO
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
    * CPU microcode is known to cause stability problems: NO (family 0x6 model 0x55 stepping 0x7 ucode 0x500002c cpuid 0x50657)
    * CPU microcode is the latest known available version: NO (latest version is 0x5003102 dated 2021/03/08 according to builtin firmwares DB v191+i20210217)
  * CPU vulnerability to the speculative execution attack variants
    * Affected by CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Affected by CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Affected by CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Affected by CVE-2018-3640 (Variant 3a, rogue system register read): YES
    * Affected by CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Affected by CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Affected by CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): YES
    * Affected by CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): YES
    * Affected by CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
    * Affected by CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
    * Affected by CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
    * Affected by CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO
    * Affected by CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): NO
    * Affected by CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): YES
    * Affected by CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka Spectre Variant 1, bounds check bypass
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
  > STATUS: UNKNOWN (/sys vulnerability interface use forced, but its not available!)

  CVE-2017-5715 aka Spectre Variant 2, branch target injection
  * Mitigated according to the /sys interface: YES (Mitigation: Enhanced IBRS, IBPB: conditional, RSB filling)
  > STATUS: VULNERABLE (IBRS+IBPB or retpoline+IBPB+RSB filling, is needed to mitigate the vulnerability)

  CVE-2017-5754 aka Variant 3, Meltdown, rogue data cache load
  * Mitigated according to the /sys interface: YES (Not affected)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka Variant 3a, rogue system register read
  * CPU microcode mitigates the vulnerability: YES
  > STATUS: NOT VULNERABLE (your CPU microcode mitigates the vulnerability)

  CVE-2018-3639 aka Variant 4, speculative store bypass
  * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
  > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

  CVE-2018-3615 aka Foreshadow (SGX), L1 terminal fault
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka Foreshadow-NG (OS), L1 terminal fault
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (Not affected)

  CVE-2018-3646 aka Foreshadow-NG (VMM), L1 terminal fault
  * Information from the /sys interface: Not affected
  > STATUS: NOT VULNERABLE (your kernel reported your CPU model as not vulnerable)

  CVE-2018-12126 aka Fallout, microarchitectural store buffer data sampling (MSBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka RIDL, microarchitectural load port data sampling (MLPDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11135 aka ZombieLoad V2, TSX Asynchronous Abort (TAA)
  * Mitigated according to the /sys interface: YES (Mitigation: TSX disabled)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12207 aka No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
  * Mitigated according to the /sys interface: YES (KVM: Mitigation: Split huge pages)
  > STATUS: NOT VULNERABLE (KVM: Mitigation: Split huge pages)

  CVE-2020-0543 aka Special Register Buffer Data Sampling (SRBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:?? CVE-2017-5715:KO CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK
