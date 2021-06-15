Spectre and Meltdown Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following section displays the output of a running shell script to tell if
system is vulnerable against the several "speculative execution" CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.44+

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:27:25 UTC 2021 aarch64
  CPU is

  Hardware check
  * CPU vulnerability to the speculative execution attack variants
    * Affected by CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Affected by CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Affected by CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Affected by CVE-2018-3640 (Variant 3a, rogue system register read): NO
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
  * Mitigated according to the /sys interface: YES (Mitigation: __user pointer sanitization)
  * Kernel has array_index_mask_nospec: NO
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  * Kernel has array_index_nospec (arm64): NO
  * Checking count of LFENCE instructions following a jump in kernel... NO (only 0 jump-then-lfence instructions found, should be >= 30 (heuristic))
  > STATUS: NOT VULNERABLE (Mitigation: __user pointer sanitization)

  CVE-2017-5715 aka Spectre Variant 2, branch target injection
  * Mitigated according to the /sys interface: NO (Vulnerable)
  * Mitigation 1
    * Kernel is compiled with IBRS support: YES
      * IBRS enabled and active: NO
    * Kernel is compiled with IBPB support: NO
      * IBPB enabled and active: NO
  * Mitigation 2
    * Kernel has branch predictor hardening (arm): YES
    * Kernel compiled with retpoline option: NO
  > STATUS: NOT VULNERABLE (Branch predictor hardening mitigates the vulnerability)

  CVE-2017-5754 aka Variant 3, Meltdown, rogue data cache load
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports Page Table Isolation (PTI): YES
    * PTI enabled and active: UNKNOWN (dmesg truncated, please reboot and relaunch this script)
    * Reduced performance impact of PTI: NO (PCID/INVPCID not supported, performance impact of PTI will be significant)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka Variant 3a, rogue system register read
  * CPU microcode mitigates the vulnerability: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3639 aka Variant 4, speculative store bypass
  * Mitigated according to the /sys interface: NO (Vulnerable)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: NO
  > STATUS: VULNERABLE (Your CPU doesnt support SSBD)

  CVE-2018-3615 aka Foreshadow (SGX), L1 terminal fault
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka Foreshadow-NG (OS), L1 terminal fault
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports PTE inversion: NO
  * PTE inversion enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3646 aka Foreshadow-NG (VMM), L1 terminal fault
  * Information from the /sys interface: Not affected
  * This system is a host running a hypervisor: NO
  * Mitigation 1 (KVM)
    * EPT is disabled: N/A (the kvm_intel module is not loaded)
  * Mitigation 2
    * L1D flush is supported by kernel: NO
    * L1D flush enabled: NO
    * Hardware-backed L1D flush supported: NO (flush will be done in software, this is slower)
    * Hyper-Threading (SMT) is enabled: UNKNOWN
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12126 aka Fallout, microarchitectural store buffer data sampling (MSBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: NO
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: NO
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka RIDL, microarchitectural load port data sampling (MLPDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: NO
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: NO
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11135 aka ZombieLoad V2, TSX Asynchronous Abort (TAA)
  * Mitigated according to the /sys interface: YES (Not affected)
  * TAA mitigation is supported by kernel: YES (found tsx_async_abort in kernel image)
  * TAA mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12207 aka No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
  * Mitigated according to the /sys interface: YES (Not affected)
  * This system is a host running a hypervisor: NO
  * iTLB Multihit mitigation is supported by kernel: YES (found itlb_multihit in kernel image)
  * iTLB Multihit mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2020-0543 aka Special Register Buffer Data Sampling (SRBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  * SRBDS mitigation control is supported by the kernel: NO
  * SRBDS mitigation control is enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:KO CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK