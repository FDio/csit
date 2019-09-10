Spectre and Meltdown Checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Following section displays the output of a running shell script to tell if
system is vulnerable against the several speculative execution CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

::

  Spectre and Meltdown mitigation detection tool v0.42

  Checking for vulnerabilities on current system
  Kernel is Linux 4.15.0-60-generic #67-Ubuntu SMP Thu Aug 22 16:55:30 UTC 2019 x86_64
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
    * Microarchitecture Data Sampling
      * VERW instruction is available: YES (MD_CLEAR feature bit)
    * Enhanced IBRS (IBRS_ALL)
      * CPU indicates ARCH_CAPABILITIES MSR availability: YES
      * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: YES
    * CPU explicitly indicates not being vulnerable to Meltdown/L1TF (RDCL_NO): YES
    * CPU explicitly indicates not being vulnerable to Variant 4 (SSB_NO): NO
    * CPU/Hypervisor indicates L1D flushing is not necessary on this system: YES
    * Hypervisor indicates host CPU might be vulnerable to RSB underflow (RSBA): NO
    * CPU explicitly indicates not being vulnerable to Microarchitectural Data Sampling (MDS_NO): YES
    * CPU supports Software Guard Extensions (SGX): NO
    * CPU microcode is known to cause stability problems: NO (model 0x55 family 0x6 stepping 0x7 ucode 0x5000021 cpuid 0x50657)
    * CPU microcode is the latest known available version: awk: fatal: cannot open file `bash' for reading (No file or directory)
  UNKNOWN (latest microcode version for your CPU model is unknown)
  * CPU vulnerability to the speculative execution attack variants
    * Vulnerable to CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
    * Vulnerable to CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
    * Vulnerable to CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): NO
    * Vulnerable to CVE-2018-3640 (Variant 3a, rogue system register read): YES
    * Vulnerable to CVE-2018-3639 (Variant 4, speculative store bypass): YES
    * Vulnerable to CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): NO
    * Vulnerable to CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): NO
    * Vulnerable to CVE-2018-12126 (Fallout, microarchitectural store buffer data sampling (MSBDS)): NO
    * Vulnerable to CVE-2018-12130 (ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)): NO
    * Vulnerable to CVE-2018-12127 (RIDL, microarchitectural load port data sampling (MLPDS)): NO
    * Vulnerable to CVE-2019-11091 (RIDL, microarchitectural data sampling uncacheable memory (MDSUM)): NO

  CVE-2017-5753 aka 'Spectre Variant 1, bounds check bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: usercopy/swapgs barriers and __user pointer saniation)
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
  * Kernel has the Red Hat/Ubuntu patch: NO
  * Kernel has mask_nospec64 (arm64): NO
  > STATUS: NOT VULNERABLE (Mitigation: usercopy/swapgs barriers and __user pointer sanitization)

  CVE-2017-5715 aka 'Spectre Variant 2, branch target injection'
  * Mitigated according to the /sys interface: YES (Mitigation: Enhanced IBRS, IBPB: conditional, RSB filling)
  * Mitigation 1
    * Kernel is compiled with IBRS support: YES
      * IBRS enabled and active: YES (Enhanced flavor, performance impact will be greatly reduced)
    * Kernel is compiled with IBPB support: YES
      * IBPB enabled and active: YES
  * Mitigation 2
    * Kernel has branch predictor hardening (arm): NO
    * Kernel compiled with retpoline option: YES
    * Kernel supports RSB filling: YES
  > STATUS: NOT VULNERABLE (Enhanced IBRS + IBPB are mitigating the vulnerability)

  CVE-2017-5754 aka 'Variant 3, Meltdown, rogue data cache load'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports Page Table Isolation (PTI): YES
    * PTI enabled and active: NO
    * Reduced performance impact of PTI: YES (CPU supports INVPCID, performance impact of PTI will be greatly reduced)
  * Running as a Xen PV DomU: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-3640 aka 'Variant 3a, rogue system register read'
  * CPU microcode mitigates the vulnerability: YES
  > STATUS: NOT VULNERABLE (your CPU microcode mitigates the vulnerability)

  CVE-2018-3639 aka 'Variant 4, speculative store bypass'
  * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
  * Kernel supports disabling speculative store bypass (SSB): YES (found in /proc/self/status)
  * SSB mitigation is enabled and active: YES (per-thread through prctl)
  * SSB mitigation currently active for selected processes: YES ((deleted) systemd-journald systemd-logind systemd-networkd systemd-resolved systemd-timesyncd systemd-udevd)
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
    * EPT is disabled: NO
  * Mitigation 2
    * L1D flush is supported by kernel: YES (found flush_l1d in /proc/cpuinfo)
    * L1D flush enabled: NO
    * Hardware-backed L1D flush supported: YES (performance impact of the mitigation will be greatly reduced)

    * Hyper-Threading (SMT) is enabled: YES
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12126 aka 'Fallout, microarchitectural store buffer data sampling (MSBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12130 aka 'ZombieLoad, microarchitectural fill buffer data sampling (MFBDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2018-12127 aka 'RIDL, microarchitectural load port data sampling (MLPDS)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  CVE-2019-11091 aka 'RIDL, microarchitectural data sampling uncacheable memory (MDSUM)'
  * Mitigated according to the /sys interface: YES (Not affected)
  * Kernel supports using MD_CLEAR mitigation: YES (md_clear found in /proc/cpuinfo)
  * Kernel mitigation is enabled and active: NO
  * SMT is either mitigated or disabled: NO
  > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

  > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK CVE-2018-12126:OK CVE-2018-12130:OK CVE-2018-12127:OK CVE-2019-11091:OK

