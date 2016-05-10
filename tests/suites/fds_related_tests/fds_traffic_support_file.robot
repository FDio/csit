*** Keywords ***
| Positive Scenario Ping Dut1 -> Dut2
| | [Arguments] | ${qemu_node}
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.2 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.1 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.2 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.1 | nmspace2
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.2 | nmspace2
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace4
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace4

| Positive Scenario Ping Dut2 -> Dut1
| | [Arguments] | ${qemu_node}
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.2 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.1 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.2 | nmspace1
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.1 | nmspace2
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.2 | nmspace2
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace3
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace4
| | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace4

| Negative Scenario Ping Dut1 -> Dut2
| | [Arguments] | ${qemu_node}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.1 | nmspace3
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.2 | nmspace3
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.1 | nmspace4
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.2 | nmspace4

| Negative Scenario Ping Dut2 -> Dut1
| | [Arguments] | ${qemu_node}
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace1
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.3 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.20.4 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.3 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.4 | nmspace2
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.1 | nmspace3
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.2 | nmspace3
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.1 | nmspace4
| | Run keyword and expect error | Ping Not Successful
| | ... | Send Ping From Node To Dst | ${qemu_node} | 16.0.10.2 | nmspace4
