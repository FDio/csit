Mellanox NIC
------------

Performance test results using Mellanox ConnectX5 2p100GE are reported for
2-Node Xeon Cascade Lake physical testbed type present in FD.io labs. For
description of physical testbeds used please refer to
:ref:`tested_physical_topologies`.

Mellanox NIC settings
~~~~~~~~~~~~~~~~~~~~~

Mellanox ConnectX5 NIC settings are following recommendations from
[DpdkPerformanceReport]_, [MellanoxDpdkGuide]_ and [MellanoxDpdkBits]_.
Specifically:

- Flow Control OFF:
  ::

      $ ethtool -A $netdev rx off tx off

- Set CQE COMPRESSION to "AGGRESSIVE":
  ::

      $ mlxconfig -d $PORT_PCI_ADDRESS set CQE_COMPRESSION=1

Mellanox :abbr:`OFED (OpenFabrics Enterprise Distribution)` driver is installed
and used to manage the NIC settings.

::

    $ sudo lspci -vvvs 5e:00.0
    5e:00.0 Ethernet controller: Mellanox Technologies MT28800 Family [ConnectX-5 Ex]
	    Subsystem: Mellanox Technologies MT28800 Family [ConnectX-5 Ex]
	    Control: I/O- Mem+ BusMaster+ SpecCycle- MemWINV- VGASnoop- ParErr+ Stepping- SERR+ FastB2B- DisINTx+
	    Status: Cap+ 66MHz- UDF- FastB2B- ParErr- DEVSEL=fast >TAbort- <TAbort- <MAbort- >SERR- <PERR- INTx-
	    Latency: 0, Cache Line Size: 32 bytes
	    Interrupt: pin A routed to IRQ 37
	    NUMA node: 0
	    Region 0: Memory at 38fffe000000 (64-bit, prefetchable) [size=32M]
	    Expansion ROM at c5e00000 [disabled] [size=1M]
	    Capabilities: [60] Express (v2) Endpoint, MSI 00
		    DevCap:	MaxPayload 512 bytes, PhantFunc 0, Latency L0s unlimited, L1 unlimited
			    ExtTag+ AttnBtn- AttnInd- PwrInd- RBE+ FLReset+ SlotPowerLimit 0.000W
		    DevCtl:	Report errors: Correctable- Non-Fatal- Fatal+ Unsupported-
			    RlxdOrd+ ExtTag+ PhantFunc- AuxPwr- NoSnoop+ FLReset-
			    MaxPayload 256 bytes, MaxReadReq 4096 bytes
		    DevSta:	CorrErr+ UncorrErr- FatalErr- UnsuppReq+ AuxPwr- TransPend-
		    LnkCap:	Port #0, Speed 16GT/s, Width x16, ASPM not supported, Exit Latency L0s unlimited, L1 unlimited
			    ClockPM- Surprise- LLActRep- BwNot- ASPMOptComp+
		    LnkCtl:	ASPM Disabled; RCB 64 bytes Disabled- CommClk+
			    ExtSynch- ClockPM- AutWidDis- BWInt- AutBWInt-
		    LnkSta:	Speed 8GT/s, Width x16, TrErr- Train- SlotClk+ DLActive- BWMgmt- ABWMgmt-
		    DevCap2: Completion Timeout: Range ABCD, TimeoutDis+, LTR-, OBFF Not Supported
		    DevCtl2: Completion Timeout: 50us to 50ms, TimeoutDis-, LTR-, OBFF Disabled
		    LnkCtl2: Target Link Speed: 16GT/s, EnterCompliance- SpeedDis-
			     Transmit Margin: Normal Operating Range, EnterModifiedCompliance- ComplianceSOS-
			     Compliance De-emphasis: -6dB
		    LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+, EqualizationPhase1+
			     EqualizationPhase2+, EqualizationPhase3+, LinkEqualizationRequest-
	    Capabilities: [48] Vital Product Data
		    Product Name: CX556A - ConnectX-5 QSFP28
		    Read-only fields:
			    [PN] Part number: MCX556A-EDAT
			    [EC] Engineering changes: AA
			    [V2] Vendor specific: MCX556A-EDAT
			    [SN] Serial number: MT1945X00360
			    [V3] Vendor specific: f8d15ef7e701ea118000b8599ffe4aa8
			    [VA] Vendor specific: MLX:MODL=CX556A:MN=MLNX:CSKU=V2:UUID=V3:PCI=V0
			    [V0] Vendor specific: PCIeGen4 x16
			    [RV] Reserved: checksum good, 2 byte(s) reserved
		    End
	    Capabilities: [9c] MSI-X: Enable+ Count=64 Masked-
		    Vector table: BAR=0 offset=00002000
		    PBA: BAR=0 offset=00003000
	    Capabilities: [c0] Vendor Specific Information: Len=18 <?>
	    Capabilities: [40] Power Management version 3
		    Flags: PMEClk- DSI- D1- D2- AuxCurrent=375mA PME(D0-,D1-,D2-,D3hot-,D3cold+)
		    Status: D0 NoSoftRst+ PME-Enable- DSel=0 DScale=0 PME-
	    Capabilities: [100 v1] Advanced Error Reporting
		    UESta:	DLP- SDES- TLP- FCP- CmpltTO- CmpltAbrt- UnxCmplt- RxOF- MalfTLP- ECRC- UnsupReq- ACSViol-
		    UEMsk:	DLP- SDES- TLP- FCP- CmpltTO- CmpltAbrt- UnxCmplt- RxOF- MalfTLP- ECRC- UnsupReq+ ACSViol-
		    UESvrt:	DLP+ SDES- TLP- FCP+ CmpltTO- CmpltAbrt- UnxCmplt- RxOF+ MalfTLP+ ECRC- UnsupReq- ACSViol-
		    CESta:	RxErr- BadTLP- BadDLLP- Rollover- Timeout- NonFatalErr-
		    CEMsk:	RxErr- BadTLP- BadDLLP- Rollover- Timeout- NonFatalErr+
		    AERCap:	First Error Pointer: 04, GenCap+ CGenEn- ChkCap+ ChkEn-
	    Capabilities: [150 v1] Alternative Routing-ID Interpretation (ARI)
		    ARICap:	MFVC- ACS-, Next Function: 1
		    ARICtl:	MFVC- ACS-, Function Group: 0
	    Capabilities: [1c0 v1] #19
	    Capabilities: [230 v1] Access Control Services
		    ACSCap:	SrcValid- TransBlk- ReqRedir- CmpltRedir- UpstreamFwd- EgressCtrl- DirectTrans-
		    ACSCtl:	SrcValid- TransBlk- ReqRedir- CmpltRedir- UpstreamFwd- EgressCtrl- DirectTrans-
	    Capabilities: [320 v1] #27
	    Capabilities: [370 v1] #26
	    Capabilities: [420 v1] #25
	    Kernel driver in use: mlx5_core
	    Kernel modules: mlx5_core

TG and SUT settings
~~~~~~~~~~~~~~~~~~~

For the TG and SUT environment settings please refer to
:ref:`_vpp_test_environment` and :ref:`_dpdk_test_environment`.

Links
~~~~~

.. [DpdkPerformanceReport] `DPDK 19.11 performance report <http://static.dpdk.org/doc/perf/DPDK_19_11_Mellanox_NIC_performance_report.pdf>`
.. [MellanoxDpdkGuide] `Mellanox DPDK guide <https://www.mellanox.com/related-docs/prod_software/MLNX_DPDK_Quick_Start_Guide_v16.11_3.0.pdf>`
.. [MellanoxDpdkBits] `Mellanox DPDK bits <https://community.mellanox.com/s/article/mellanox-dpdk>`
