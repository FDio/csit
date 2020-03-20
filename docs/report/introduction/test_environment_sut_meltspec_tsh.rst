Spectre and Meltdown Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following section displays sample output of a running shell script to tell if
a system is vulnerable to the several "speculative execution" CVEs, which were
made public in 2018. The script is available at `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.43

  awk: cannot open bash (No such file or directory)
  Checking for vulnerabilities on current system
  Kernel is Linux 4.15.0-23-generic #25-Ubuntu SMP Wed May 23 18:02:16 UTC 2018 x86_64
  CPU is Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz

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
      * CPU indicates SSBD capability: NO
    * L1 data cache invalidation
      * FLUSH_CMD MSR is available: NO
      * CPU indicates L1D flush capability: NO
    * Microarchitectural Data Sampling
      * VERW instruction is available: NO
    * Enhanced IBRS (IBRS_ALL)
      * CPU indicates ARCH_CAPABILITIES MSR availability: NO
      * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: NO
    * CPU explicitly indicates not being vulnerable to Meltdown/L1TF (RDCL_NO): NO
    * CPU explicitly indicates not being vulnerable to Variant 4 (SSB_NO): NO
    * CPU/Hypervisor indicates L1D flushing is not necessary on this system: NO
    * Hypervisor indicates host CPU might be vulnerable to RSB underflow (RSBA): NO
    * CPU explicitly indicates not being vulnerable to Microarchitectural Data Sampling (MDS_NO): NO
    * CPU explicitly indicates not being vulnerable to TSX Asynchronous Abort (TAA_NO): NO
    * CPU explicitly indicates not being vulnerable to iTLB Multihit (PSCHANGE_MSC_NO): NO
    * CPU explicitly indicates having MSR for TSX control (TSX_CTRL_MSR): NO
    * CPU supports Transactional Synchronization Extensions (TSX): YES (RTM feature bit)
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU microcode is known to cause stability problems: NO (model 0x55 family 0x6 stepping 0x4 ucode 0x2000043 cpuid 0x50654)
    * CPU microcode is the latest known available version: awk: cannot open bash (No such file or directory)
  UNKNOWN (latest microcode version for your CPU model is unknown)
  * CPU vulnerability to the speculative execution attack variants
    * Vulnerable to CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Vulnerable to CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Vulnerable to CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): YES
    * Vulnerable to CVE-2018-3640 (Variant 3a, rogue system register read): YES
    * Vulnerable to CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Vulnerable to CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): YES
    * Vulnerable to CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): YES
    * Vulnerable to CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): YES
    * Vulnerable to CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): YES
    * Vulnerable to CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): YES
    * Vulnerable to CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): YES
    * Vulnerable to CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): YES
    * Vulnerable to CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): YES

  CVE-2017-5753 aka Spectre Variant 1, bounds check bypass
  * Mitigated according to the /sys interface: YES (Mitigation: __user pointer sanitization)
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  > STATUS: NOT VULNERABLE (Mitigation: __user pointer sanitization)

  CVE-2017-5715 aka Spectre Variant 2, branch target injection
  * Mitigated according to the /sys interface: YES (Mitigation: Full generic retpoline, IBPB, IBRS_FW)
  * Mitigation 1
    * Kernel is compiled with IBRS support: YES
      * IBRS enabled and active: YES (for firmware code only)
    * Kernel is compiled with IBPB support: YES
      * IBPB enabled and active: YES
  * Mitigation 2
    * Kernel has branch predictor hardening (arm): NO
    * Kernel compiled with retpoline option: YES
      * Kernel compiled with a retpoline-aware compiler: YES (kernel reports full retpoline compilation)
    * Kernel supports RSB filling: YES
  > STATUS: NOT VULNERABLE (Full retpoline + IBPB are mitigating the vulnerability)

  CVE-2017-5754 aka Variant 3, Meltdown, rogue data cache load
  * Mitigated according to the /sys interface: YES (Mitigation: PTI)
  * Kernel supports Page Table Isolation (PTI): YES
    * PTI enabled and active: YES
    * Reduced performance impact of PTI: YES (CPU supports INVPCID, performance impact of PTI will be greatly reduced)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (Mitigation: PTI)

  CVE-2018-3640 aka Variant 3a, rogue system register read
  * CPU microcode mitigates the vulnerability: NO
  > STATUS: VULNERABLE (an up-to-date CPU microcode is needed to mitigate this vulnerability)

  CVE-2018-3639 aka Variant 4, speculative store bypass
  * Mitigated according to the /sys interface: NO (Vulnerable)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: NO
  > STATUS: VULNERABLE (Your CPU doesnt support SSBD)

  CVE-2018-3615 aka Foreshadow (SGX), L1 terminal fault
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka Foreshadow-NG (OS), L1 terminal fault
  * Kernel supports PTE inversion: NO
  * PTE inversion enabled and active: UNKNOWN (sysfs interface not available)
  > STATUS: VULNERABLE (Your kernel doesnt support PTE inversion, update it)

  CVE-2018-3646 aka Foreshadow-NG (VMM), L1 terminal fault
  * This system is a host running a hypervisor: NO
  * Mitigation 1 (KVM)
    * EPT is disabled: NO
  * Mitigation 2
    * L1D flush is supported by kernel: NO
    * L1D flush enabled: UNKNOWN (cant find or read /sys/devices/system/cpu/vulnerabilities/l1tf)
    * Hardware-backed L1D flush supported: NO (flush will be done in software, this is slower)
    * Hyper-Threading (SMT) is enabled: YES
  > STATUS: NOT VULNERABLE (this system is not running a hypervisor)

  CVE-2018-12126 aka Fallout, microarchitectural store buffer data sampling (MSBDS)
  * Kernel supports using MD_CLEAR mitigation: NO
  > STATUS: VULNERABLE (Neither your kernel or your microcode support mitigation, upgrade both to mitigate the vulnerability)

  CVE-2018-12130 aka ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
  * Kernel supports using MD_CLEAR mitigation: NO
  > STATUS: VULNERABLE (Neither your kernel or your microcode support mitigation, upgrade both to mitigate the vulnerability)

  CVE-2018-12127 aka RIDL, microarchitectural load port data sampling (MLPDS)
  * Kernel supports using MD_CLEAR mitigation: NO
  > STATUS: VULNERABLE (Neither your kernel or your microcode support mitigation, upgrade both to mitigate the vulnerability)

  CVE-2019-11091 aka RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
  * Kernel supports using MD_CLEAR mitigation: NO
  > STATUS: VULNERABLE (Neither your kernel or your microcode support mitigation, upgrade both to mitigate the vulnerability)

  CVE-2019-11135 aka ZombieLoad V2, TSX Asynchronous Abort (TAA)
  * TAA mitigation is supported by kernel: NO
  * TAA mitigation enabled and active: NO (tsx_async_abort not found in sysfs hierarchy)
  > STATUS: VULNERABLE (Your kernel doesnt support TAA mitigation, update it)

  CVE-2018-12207 aka No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
  * This system is a host running a hypervisor: NO
  * iTLB Multihit mitigation is supported by kernel: NO
  * iTLB Multihit mitigation enabled and active: NO (itlb_multihit not found in sysfs hierarchy)
  > STATUS: NOT VULNERABLE (this system is not running a hypervisor)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:KO CVE-2018-3639:KO CVE-2018-3615:OK CVE-2018-3620:KO CVE-2018-3646:OK CVE-2018-12126:KO CVE-2018-12130:KO CVE-2018-12127:KO CVE-2019-11091:KO CVE-2019-11135:KO CVE-2018-12207:OK
