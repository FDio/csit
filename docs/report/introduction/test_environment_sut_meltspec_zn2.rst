Spectre and Meltdown Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following section displays the output of a running shell script to tell if
system is vulnerable against the several speculative execution CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.43

  Checking for vulnerabilities on current system
  Kernel is Linux 4.15.0-72-generic #81-Ubuntu SMP Tue Nov 26 12:20:02 UTC 2019 x86_64
  CPU is AMD EPYC 7532 32-Core Processor

  Hardware check
  * Hardware support (CPU microcode) for mitigation techniques
    * Indirect Branch Restricted Speculation (IBRS)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates IBRS capability: YES (IBRS_SUPPORT feature bit)
      * CPU indicates preferring IBRS always-on: NO
      * CPU indicates preferring IBRS over retpoline: YES
    * Indirect Branch Prediction Barrier (IBPB)
      * PRED_CMD MSR is available: YES
      * CPU indicates IBPB capability: YES (IBPB_SUPPORT feature bit)
    * Single Thread Indirect Branch Predictors (STIBP)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates STIBP capability: YES (AMD STIBP feature bit)
      * CPU indicates preferring STIBP always-on: NO
    * Speculative Store Bypass Disable (SSBD)
      * CPU indicates SSBD capability: YES (AMD SSBD in SPEC_CTRL)
    * L1 data cache invalidation
      * FLUSH_CMD MSR is available: NO
      * CPU indicates L1D flush capability: NO
    * CPU supports Transactional Synchronization Extensions (TSX): NO
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
    * CPU microcode is known to cause stability problems: NO (family 0x17 model 0x31 stepping 0x0 ucode 0x8301034 cpuid 0x830f10)
    * CPU microcode is the latest known available version: NO (latest version is 0x8301039 dated 2020/02/07 according to builtin firmwares DB v160.20200912+i20200722)
  * CPU vulnerability to the speculative execution attack variants
    * Vulnerable to CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Vulnerable to CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Vulnerable to CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Vulnerable to CVE-2018-3640 (Variant 3a, rogue system register read): NO
    * Vulnerable to CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Vulnerable to CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): NO
    * Vulnerable to CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
    * Vulnerable to CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
    * Vulnerable to CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
    * Vulnerable to CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO
    * Vulnerable to CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): NO
    * Vulnerable to CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): NO
    * Vulnerable to CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka 'Spectre Variant 1, bounds check bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  * Kernel has array_index_nospec (arm64): NO
  > STATUS: NOT VULNERABLE (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)

  CVE-2017-5715 aka 'Spectre Variant 2, branch target injection'
  * Mitigated according to the /sys interface: YES (Mitigation: Full AMD retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling)
  * Mitigation 1
    * Kernel is compiled with IBRS support: YES
      * IBRS enabled and active: YES (for firmware code only)
    * Kernel is compiled with IBPB support: YES
      * IBPB enabled and active: YES
  * Mitigation 2
    * Kernel has branch predictor hardening (arm): NO
    * Kernel compiled with retpoline option: YES
      * Kernel compiled with a retpoline-aware compiler: YES (kernel reports full retpoline compilation)
  > STATUS: NOT VULNERABLE (Full retpoline + IBPB are mitigating the vulnerability)

  CVE-2017-5754 aka 'Variant 3, Meltdown, rogue data cache load'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports Page Table Isolation (PTI): YES
    * PTI enabled and active: NO
    * Reduced performance impact of PTI: NO (PCID/INVPCID not supported, performance impact of PTI will be significant)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka 'Variant 3a, rogue system register read'
  * CPU microcode mitigates the vulnerability: YES
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3639 aka 'Variant 4, speculative store bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: YES (per-thread through prctl)
  * SSB mitigation currently active for selected processes: YES (systemd-journald systemd-logind systemd-networkd systemd-resolved systemd-timesyncd systemd-udevd)
  > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

  CVE-2018-3615 aka 'Foreshadow (SGX), L1 terminal fault'
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka 'Foreshadow-NG (OS), L1 terminal fault'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports PTE inversion: YES (found in kernel image)
  * PTE inversion enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3646 aka 'Foreshadow-NG (VMM), L1 terminal fault'
  * Information from the /sys interface: Not affected
  * This system is a host running a hypervisor: NO
  * Mitigation 1 (KVM)
    * EPT is disabled: N/A (the kvm_intel module is not loaded)
  * Mitigation 2
    * L1D flush is supported by kernel: YES (found flush_l1d in kernel image)
    * L1D flush enabled: NO
    * Hardware-backed L1D flush supported: NO (flush will be done in software, this is slower)
    * Hyper-Threading (SMT) is enabled: YES
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12126 aka 'Fallout, microarchitectural store buffer data sampling (MSBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka 'ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka 'RIDL, microarchitectural load port data sampling (MLPDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka 'RIDL, microarchitectural data sampling uncacheable memory (MDSUM)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11135 aka 'ZombieLoad V2, TSX Asynchronous Abort (TAA)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * TAA mitigation is supported by kernel: YES (found tsx_async_abort in kernel image)
  * TAA mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12207 aka 'No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * This system is a host running a hypervisor: NO
  * iTLB Multihit mitigation is supported by kernel: YES (found itlb_multihit in kernel image)
  * iTLB Multihit mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2020-0543 aka 'Special Register Buffer Data Sampling (SRBDS)'
  * SRBDS mitigation control is supported by the kernel: NO
  * SRBDS mitigation control is enabled and active: NO (SRBDS not found in sysfs hierarchy)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK

  Need more detailed information about mitigation options? Use --explain
  A false sense of security is worse than no security at all, see --disclaimer

::

  Spectre and Meltdown mitigation detection tool v0.43

  Checking for vulnerabilities on current system
  Kernel is Linux 4.15.0-72-generic #81-Ubuntu SMP Tue Nov 26 12:20:02 UTC 2019 x86_64
  CPU is AMD EPYC 7532 32-Core Processor

  Hardware check
  * Hardware support (CPU microcode) for mitigation techniques
    * Indirect Branch Restricted Speculation (IBRS)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates IBRS capability: YES (IBRS_SUPPORT feature bit)
      * CPU indicates preferring IBRS always-on: NO
      * CPU indicates preferring IBRS over retpoline: YES
    * Indirect Branch Prediction Barrier (IBPB)
      * PRED_CMD MSR is available: YES
      * CPU indicates IBPB capability: YES (IBPB_SUPPORT feature bit)
    * Single Thread Indirect Branch Predictors (STIBP)
      * SPEC_CTRL MSR is available: YES
      * CPU indicates STIBP capability: YES (AMD STIBP feature bit)
      * CPU indicates preferring STIBP always-on: NO
    * Speculative Store Bypass Disable (SSBD)
      * CPU indicates SSBD capability: YES (AMD SSBD in SPEC_CTRL)
    * L1 data cache invalidation
      * FLUSH_CMD MSR is available: NO
      * CPU indicates L1D flush capability: NO
    * CPU supports Transactional Synchronization Extensions (TSX): NO
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
    * CPU microcode is known to cause stability problems: NO (family 0x17 model 0x31 stepping 0x0 ucode 0x8301034 cpuid 0x830f10)
    * CPU microcode is the latest known available version: NO (latest version is 0x8301039 dated 2020/02/07 according to builtin firmwares DB v160.20200912+i20200722)
  * CPU vulnerability to the speculative execution attack variants
    * Vulnerable to CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Vulnerable to CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Vulnerable to CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Vulnerable to CVE-2018-3640 (Variant 3a, rogue system register read): NO
    * Vulnerable to CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Vulnerable to CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): NO
    * Vulnerable to CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
    * Vulnerable to CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
    * Vulnerable to CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
    * Vulnerable to CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO
    * Vulnerable to CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): NO
    * Vulnerable to CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): NO
    * Vulnerable to CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka 'Spectre Variant 1, bounds check bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  * Kernel has array_index_nospec (arm64): NO
  > STATUS: NOT VULNERABLE (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)

  CVE-2017-5715 aka 'Spectre Variant 2, branch target injection'
  * Mitigated according to the /sys interface: YES (Mitigation: Full AMD retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling)
  * Mitigation 1
    * Kernel is compiled with IBRS support: YES
      * IBRS enabled and active: YES (for firmware code only)
    * Kernel is compiled with IBPB support: YES
      * IBPB enabled and active: YES
  * Mitigation 2
    * Kernel has branch predictor hardening (arm): NO
    * Kernel compiled with retpoline option: YES
      * Kernel compiled with a retpoline-aware compiler: YES (kernel reports full retpoline compilation)
  > STATUS: NOT VULNERABLE (Full retpoline + IBPB are mitigating the vulnerability)

  CVE-2017-5754 aka 'Variant 3, Meltdown, rogue data cache load'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports Page Table Isolation (PTI): YES
    * PTI enabled and active: NO
    * Reduced performance impact of PTI: NO (PCID/INVPCID not supported, performance impact of PTI will be significant)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka 'Variant 3a, rogue system register read'
  * CPU microcode mitigates the vulnerability: YES
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3639 aka 'Variant 4, speculative store bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: YES (per-thread through prctl)
  * SSB mitigation currently active for selected processes: YES (systemd-journald systemd-logind systemd-networkd systemd-resolved systemd-timesyncd systemd-udevd)
  > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

  CVE-2018-3615 aka 'Foreshadow (SGX), L1 terminal fault'
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka 'Foreshadow-NG (OS), L1 terminal fault'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports PTE inversion: YES (found in kernel image)
  * PTE inversion enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3646 aka 'Foreshadow-NG (VMM), L1 terminal fault'
  * Information from the /sys interface: Not affected
  * This system is a host running a hypervisor: NO
  * Mitigation 1 (KVM)
    * EPT is disabled: N/A (the kvm_intel module is not loaded)
  * Mitigation 2
    * L1D flush is supported by kernel: YES (found flush_l1d in kernel image)
    * L1D flush enabled: NO
    * Hardware-backed L1D flush supported: NO (flush will be done in software, this is slower)
    * Hyper-Threading (SMT) is enabled: YES
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12126 aka 'Fallout, microarchitectural store buffer data sampling (MSBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka 'ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka 'RIDL, microarchitectural load port data sampling (MLPDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka 'RIDL, microarchitectural data sampling uncacheable memory (MDSUM)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (found md_clear implementation evidence in kernel image)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11135 aka 'ZombieLoad V2, TSX Asynchronous Abort (TAA)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * TAA mitigation is supported by kernel: YES (found tsx_async_abort in kernel image)
  * TAA mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12207 aka 'No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * This system is a host running a hypervisor: NO
  * iTLB Multihit mitigation is supported by kernel: YES (found itlb_multihit in kernel image)
  * iTLB Multihit mitigation enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2020-0543 aka 'Special Register Buffer Data Sampling (SRBDS)'
  * SRBDS mitigation control is supported by the kernel: NO
  * SRBDS mitigation control is enabled and active: NO (SRBDS not found in sysfs hierarchy)
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK

  Need more detailed information about mitigation options? Use --explain
  A false sense of security is worse than no security at all, see --disclaimer