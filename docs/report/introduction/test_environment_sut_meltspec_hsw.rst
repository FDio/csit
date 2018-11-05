SPECTRE - MELTDOWN Checks - Haswell
-----------------------------------

Following section displays the output of a running shell script to tell if
system is vulnerable against the several "speculative execution" CVEs that were
made public in 2018. Script is available on `Spectre & Meltdown Checker Github
<https://github.com/speed47/spectre-meltdown-checker>`_.

- CVE-2017-5753 [bounds check bypass] aka 'Spectre Variant 1'
- CVE-2017-5715 [branch target injection] aka 'Spectre Variant 2'
- CVE-2017-5754 [rogue data cache load] aka 'Meltdown' aka 'Variant 3'
- CVE-2018-3640 [rogue system register read] aka 'Variant 3a'
- CVE-2018-3639 [speculative store bypass] aka 'Variant 4'
- CVE-2018-3615 [L1 terminal fault] aka 'Foreshadow (SGX)'
- CVE-2018-3620 [L1 terminal fault] aka 'Foreshadow-NG (OS)'
- CVE-2018-3646 [L1 terminal fault] aka 'Foreshadow-NG (VMM)'

::

    $ sudo ./spectre-meltdown-checker.sh --no-color

    Spectre and Meltdown mitigation detection tool v0.40

    Checking for vulnerabilities on current system
    Kernel is Linux 4.15.0-36-generic #39-Ubuntu SMP Mon Sep 24 16:19:09 UTC 2018 x86_64
    CPU is Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz

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
      * Enhanced IBRS (IBRS_ALL)
        * CPU indicates ARCH_CAPABILITIES MSR availability: NO
        * ARCH_CAPABILITIES MSR advertises IBRS_ALL capability: NO
      * CPU explicitly indicates not being vulnerable to Meltdown (RDCL_NO): NO
      * CPU explicitly indicates not being vulnerable to Variant 4 (SSB_NO): NO
      * CPU/Hypervisor indicates L1D flushing is not necessary on this system: NO
      * Hypervisor indicates host CPU might be vulnerable to RSB underflow (RSBA): NO
      * CPU supports Software Guard Extensions (SGX): NO
      * CPU microcode is known to cause stability problems: NO (model 0x3f family 0x6 stepping 0x2 ucode 0x3d cpuid 0x306f2)
      * CPU microcode is the latest known available version: YES (latest version is 0x3d dated 2018/04/20 according to builtin MCExtractor DB v84 - 2018/09/27)
    * CPU vulnerability to the speculative execution attack variants
      * Vulnerable to CVE-2017-5753 (Spectre Variant 1, bounds check bypass): YES
      * Vulnerable to CVE-2017-5715 (Spectre Variant 2, branch target injection): YES
      * Vulnerable to CVE-2017-5754 (Variant 3, Meltdown, rogue data cache load): YES
      * Vulnerable to CVE-2018-3640 (Variant 3a, rogue system register read): YES
      * Vulnerable to CVE-2018-3639 (Variant 4, speculative store bypass): YES
      * Vulnerable to CVE-2018-3615 (Foreshadow (SGX), L1 terminal fault): NO
      * Vulnerable to CVE-2018-3620 (Foreshadow-NG (OS), L1 terminal fault): YES
      * Vulnerable to CVE-2018-3646 (Foreshadow-NG (VMM), L1 terminal fault): YES

    CVE-2017-5753 aka 'Spectre Variant 1, bounds check bypass'
    * Mitigated according to the /sys interface: YES (Mitigation: __user pointer sanitization)
    * Kernel has array_index_mask_nospec: YES (1 occurrence(s) found of x86 64 bits array_index_mask_nospec())
    * Kernel has the Red Hat/Ubuntu patch: NO
    * Kernel has mask_nospec64 (arm64): NO
    > STATUS: NOT VULNERABLE (Mitigation: __user pointer sanitization)

    CVE-2017-5715 aka 'Spectre Variant 2, branch target injection'
    * Mitigated according to the /sys interface: YES (Mitigation: Full generic retpoline, IBPB, IBRS_FW)
    * Mitigation 1
      * Kernel is compiled with IBRS support: YES
        * IBRS enabled and active: YES (for kernel and firmware code)
      * Kernel is compiled with IBPB support: YES
        * IBPB enabled and active: YES
    * Mitigation 2
      * Kernel has branch predictor hardening (arm): NO
      * Kernel compiled with retpoline option: YES
        * Kernel compiled with a retpoline-aware compiler: YES (kernel reports full retpoline compilation)
    > STATUS: NOT VULNERABLE (Full retpoline + IBPB are mitigating the vulnerability)

    CVE-2017-5754 aka 'Variant 3, Meltdown, rogue data cache load'
    * Mitigated according to the /sys interface: YES (Mitigation: PTI)
    * Kernel supports Page Table Isolation (PTI): YES
      * PTI enabled and active: YES
      * Reduced performance impact of PTI: YES (CPU supports INVPCID, performance impact of PTI will be greatly reduced)
    * Running as a Xen PV DomU: NO
    > STATUS: NOT VULNERABLE (Mitigation: PTI)

    CVE-2018-3640 aka 'Variant 3a, rogue system register read'
    * CPU microcode mitigates the vulnerability: YES
    > STATUS: NOT VULNERABLE (your CPU microcode mitigates the vulnerability)

    CVE-2018-3639 aka 'Variant 4, speculative store bypass'
    * Mitigated according to the /sys interface: YES (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)
    * Kernel supports speculation store bypass: YES (found in /proc/self/status)
    > STATUS: NOT VULNERABLE (Mitigation: Speculative Store Bypass disabled via prctl and seccomp)

    CVE-2018-3615 aka 'Foreshadow (SGX), L1 terminal fault'
    * CPU microcode mitigates the vulnerability: N/A
    > STATUS: NOT VULNERABLE (your CPU vendor reported your CPU model as not vulnerable)

    CVE-2018-3620 aka 'Foreshadow-NG (OS), L1 terminal fault'
    * Mitigated according to the /sys interface: YES (Mitigation: PTE Inversion)
    * Kernel supports PTE inversion: YES (found in kernel image)
    * PTE inversion enabled and active: YES
    > STATUS: NOT VULNERABLE (Mitigation: PTE Inversion)

    CVE-2018-3646 aka 'Foreshadow-NG (VMM), L1 terminal fault'
    * Information from the /sys interface: VMX: conditional cache flushes, SMT disabled
    * This system is a host running an hypervisor: NO
    * Mitigation 1 (KVM)
      * EPT is disabled: NO
    * Mitigation 2
      * L1D flush is supported by kernel: YES (found flush_l1d in /proc/cpuinfo)
      * L1D flush enabled: YES (conditional flushes)
      * Hardware-backed L1D flush supported: YES (performance impact of the mitigation will be greatly reduced)
      * Hyper-Threading (SMT) is enabled: NO
    > STATUS: NOT VULNERABLE (this system is not running an hypervisor)

    > SUMMARY: CVE-2017-5753:OK CVE-2017-5715:OK CVE-2017-5754:OK CVE-2018-3640:OK CVE-2018-3639:OK CVE-2018-3615:OK CVE-2018-3620:OK CVE-2018-3646:OK

    Need more detailed information about mitigation options? Use --explain
    A false sense of security is worse than no security at all, see --disclaimer
