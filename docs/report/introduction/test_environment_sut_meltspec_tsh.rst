Spectre and Meltdown Checks
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following section displays the output of a running shell script to tell if
system is vulnerable against the several "speculative execution" CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.44+

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64
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
      * CPU indicates SSBD capability: YES (Intel SSBD)
    * L1 data cache invalidation
      * FLUSH_CMD MSR is available: YES
      * CPU indicates L1D flush capability: YES (L1D flush feature bit)
    * Microarchitectural Data Sampling
      * VERW instruction is available: YES (MD_CLEAR feature bit)
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
    * CPU supports Special Register Buffer Data Sampling (SRBDS): NO
    * CPU microcode is known to cause stability problems: NO (family 0x6 model 0x55 stepping 0x4 ucode 0x2000065 cpuid 0x50654)
    * CPU microcode is the latest known available version: NO (latest version is 0x2006b06 dated 2021/03/08 according to builtin firmwares DB v191+i20210217)
  * CPU vulnerability to the speculative execution attack variants
    * Affected by CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Affected by CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Affected by CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): YES
    * Affected by CVE-2018-3640 (Variant 3a, rogue system register read): YES
    * Affected by CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Affected by CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Affected by CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): YES
    * Affected by CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): YES
    * Affected by CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): YES
    * Affected by CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): YES
    * Affected by CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): YES
    * Affected by CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): YES
    * Affected by CVE-2019-11135 (ZombieLoad V2, TSX Asynchronous Abort (TAA)): YES
    * Affected by CVE-2018-12207 (No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)): YES
    * Affected by CVE-2020-0543 (Special Register Buffer Data Sampling (SRBDS)): NO

  CVE-2017-5753 aka Spectre Variant 1, bounds check bypass
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  * Kernel has array_index_nospec (arm64): NO
  > STATUS: NOT VULNERABLE (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)

  CVE-2017-5715 aka Spectre Variant 2, branch target injection
  * Mitigated according to the /sys interface: YES (Mitigation: Full generic retpoline, IBPB: conditional, IBRS_FW, STIBP: conditional, RSB filling)
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
  * CPU microcode mitigates the vulnerability: YES
  > STATUS: NOT VULNERABLE (your CPU microcode mitigates the vulnerability)

  CVE-2018-3639 aka Variant 4, speculative store bypass
  * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: YES (per-thread through prctl)
  * SSB mitigation currently active for selected processes: YES (boltd fwupd irqbalance systemd-journald systemd-logind systemd-networkd systemd-resolved systemd-timesyncd systemd-udevd)
  > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

  CVE-2018-3615 aka Foreshadow (SGX), L1 terminal fault
  * CPU microcode mitigates the vulnerability: N/A
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3620 aka Foreshadow-NG (OS), L1 terminal fault
  * Mitigated according to the /sys interface: YES (Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable)
  * Kernel supports PTE inversion: YES (found in kernel image)
  * PTE inversion enabled and active: YES
  > STATUS: NOT VULNERABLE (Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable)

  CVE-2018-3646 aka Foreshadow-NG (VMM), L1 terminal fault
  * Information from the /sys interface: Mitigation: PTE Inversion; VMX: conditional cache flushes, SMT vulnerable
  * This system is a host running a hypervisor: NO
  * Mitigation 1 (KVM)
    * EPT is disabled: NO
  * Mitigation 2
    * L1D flush is supported by kernel: YES (found flush_l1d in /proc/cpuinfo)
    * L1D flush enabled: YES (conditional flushes)
    * Hardware-backed L1D flush supported: YES (performance impact of the mitigation will be greatly reduced)
    * Hyper-Threading (SMT) is enabled: YES
  > STATUS: NOT VULNERABLE (this system is not running a hypervisor)

  CVE-2018-12126 aka Fallout, microarchitectural store buffer data sampling (MSBDS)
  * Mitigated according to the /sys interface: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: YES
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (Your microcode and kernel are both up to date for this mitigation, and mitigation is enabled)

  CVE-2018-12130 aka ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)
  * Mitigated according to the /sys interface: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: YES
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (Your microcode and kernel are both up to date for this mitigation, and mitigation is enabled)

  CVE-2018-12127 aka RIDL, microarchitectural load port data sampling (MLPDS)
  * Mitigated according to the /sys interface: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: YES
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (Your microcode and kernel are both up to date for this mitigation, and mitigation is enabled)

  CVE-2019-11091 aka RIDL, microarchitectural data sampling uncacheable memory (MDSUM)
  * Mitigated according to the /sys interface: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: YES
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (Your microcode and kernel are both up to date for this mitigation, and mitigation is enabled)

  CVE-2019-11135 aka ZombieLoad V2, TSX Asynchronous Abort (TAA)
  * Mitigated according to the /sys interface: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  * TAA mitigation is supported by kernel: YES (found tsx_async_abort in kernel image)
  * TAA mitigation enabled and active: YES (Mitigation: Clear CPU buffers; SMT vulnerable)
  > STATUS: NOT VULNERABLE (Mitigation: Clear CPU buffers; SMT vulnerable)

  CVE-2018-12207 aka No eXcuses, iTLB Multihit, machine check exception on page size changes (MCEPSC)
  * Mitigated according to the /sys interface: YES (KVM: Mitigation: Split huge pages)
  * This system is a host running a hypervisor: NO
  * iTLB Multihit mitigation is supported by kernel: YES (found itlb_multihit in kernel image)
  * iTLB Multihit mitigation enabled and active: YES (KVM: Mitigation: Split huge pages)
  > STATUS: NOT VULNERABLE (this system is not running a hypervisor)

  CVE-2020-0543 aka Special Register Buffer Data Sampling (SRBDS)
  * Mitigated according to the /sys interface: YES (Not affected)
  * SRBDS mitigation control is supported by the kernel: YES (found SRBDS implementation evidence in kernel image. Your kernel is up to date for SRBDS mitigation)
  * SRBDS mitigation control is enabled and active: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK

::

  Spectre and Meltdown mitigation detection tool v0.44+

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:27:25 UTC 2021 aarch64
  CPU is ARM v8 model 0xd08

  Hardware check
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

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:KO CVE-2018-3639:KO CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK

  Need more detailed information about mitigation options? Use --explain
  A false sense of security is worse than no security at all, see --disclaimer
  ok: [10.30.51.37] =>
  spectre_meltdown_poll_results.stdout_lines:
  Spectre and Meltdown mitigation detection tool v0.44+

  Checking for vulnerabilities on current system
  Kernel is Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:27:25 UTC 2021 aarch64
  CPU is ARM v8 model 0xd08

  Hardware check
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

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:KO CVE-2018-3639:KO CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK CVE-2019-11135:OK CVE-2018-12207:OK CVE-2020-0543:OK
