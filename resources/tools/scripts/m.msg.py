# Copyright (c) 2024 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

messages = [
    {
        'role': 'system',
        'content': '''
You are a software engineer collaborating with the user.
''',
    },
    {
        'role': 'user',
        'content': '''
I have a collection of console log files,
and I am developing a bash script to extract important information (without unneeded details).
Currently I am focusing of that part of console logs that describe test results.
In my script, I currently have this line:
```
        fgrep '| FAIL' "console.log" | fgrep -v 'Tests'
```
It prints the name of each failed test (without suite summaries that also contain `| FAILED |` as a substring.

Here is a typical block of test failure details followed by passed test details and suite summary. Note that the summary ends with equals, not dashes:
```
IMIX-2c-eth-l2xcbase-testpmd-ndrpdr                                   | FAIL |
T-Rex STL runtime error
Command execution failed: 'python3 '/tmp/openvpp-testing/GPL/tools/trex/trex_stl_profile.py' --profile '/tmp/openvpp-testing/GPL/traffic_profiles/trex/trex-stl-ethip4-ip4src254.py' --duration 1.0 --frame_size IMIX_v4_1 --rate '33437360.677663844pps' --ports 0 1 --traffic_directions 2 --delay 0.0'
RC: 1
/opt/trex-core-3.03/scripts/external_libs/scapy-2.4.3/scapy/layers/ipsec.py:469: CryptographyDeprecationWarning: Blowfish has been deprecated
  cipher=algorithms.Blowfish,
/opt/trex-core-3.03/scripts/external_libs/scapy-2.4.3/scapy/layers/ipsec.py:483: CryptographyDeprecationWarning: CAST5 has been deprecated
  cipher=algorithms.CAST5,
T-Rex STL runtime error!
Traceback (most recent call last):
  File "/tmp/openvpp-testing/GPL/tools/trex/trex_stl_profile.py", line 341, in <module>
    main()
  File "/tmp/openvpp-testing/GPL/tools/trex/trex_stl_profile.py", line 326, in main
    simple_burst(
    [ Message content over the limit has been removed. ]
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/stl/trex_stl_client.py", line 787, in start
    ports = self.__pre_start_check('START', ports, force, streams_per_port)
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/stl/trex_stl_client.py", line 686, in __pre_start_check
    return self.psv.validate(cmd_name, ports, states)
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/common/trex_psv.py", line 279, in validate
    self.validators[state].validate(self.client, cmd_name, ports, err_msg)
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/common/trex_psv.py", line 52, in wrapper
    return supermeth(*args, **kwargs)
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/common/trex_psv.py", line 72, in validate
    self.print_err_msg(invalid_ports, custom_err_msg)
  File "/opt/trex-core-3.03/scripts/automation/trex_control_plane/interactive/trex/common/trex_psv.py", line 78, in print_err_msg
    raise TRexError('port(s) {0}: {1}'.format(invalid_ports, err_msg))
trex.common.trex_exceptions.TRexError: port(s) [0]: link is DOWN - check the connection or specify 'force'
------------------------------------------------------------------------------
IMIX-4c-eth-l2xcbase-testpmd-ndrpdr                                   | PASS |
NDR: 64893503.97848667 pps, 194.0748392316608 Gbps (initial) 
PDR: 64893503.97848667 pps, 194.0748392316608 Gbps (initial) 
Latency at 90% PDR: ['-1/-1/-1/', '-1/-1/-1/'] 
Latency at 50% PDR: ['-1/-1/-1/', '-1/-1/-1/'] 
Latency at 10% PDR: ['-1/-1/-1/', '-1/-1/-1/'] 
Latency at 0% PDR: ['-1/-1/-1/', '-1/-1/-1/']
------------------------------------------------------------------------------
Tests.Dpdk.Perf.2N1L-100Ge2P1E810Cq-Eth-L2Xcbase-Testpmd-Ndrpdr ::... | FAIL |
9 tests, 5 passed, 4 failed
==============================================================================
```

Currently, my script prints the first line of such block.
But now I want to show also "type" of failure, which would be the last line before dashes (before next test output starts),
so my new desired output to echo is:
```
IMIX-2c-eth-l2xcbase-testpmd-ndrpdr                                   | FAIL |
trex.common.trex_exceptions.TRexError: port(s) [0]: link is DOWN - check the connection or specify 'force'
```

Can you write a bash block to replace my one code line with to get that output?
''',
    },
    {
        'role': 'assistant',
        'content': '''
Certainly! To achieve the desired output, you can use a combination of `grep`, `awk`, and `sed` to extract the relevant lines from the log file. Here's a bash script block that should do the job:

```bash
#!/bin/bash

# Extract the lines with '| FAIL' and the corresponding error message
awk '
    /\| FAIL \|/ {
        print
        getline
        while ($0 !~ /^[-=]+$/) {
            print
            getline
        }
    }
' console.log | grep -v 'Tests'
```

Explanation:
1. `awk` is used to process the log file.
2. The pattern `/\| FAIL \|/` matches lines containing `| FAIL |`.
3. When a match is found, the line is printed.
4. `getline` reads the next line.
5. The `while` loop continues to print lines until it encounters a line that starts with dashes (`-`) or equals (`=`), which indicates the end of the error message block.
6. `grep -v 'Tests'` is used to exclude lines containing 'Tests', which are typically suite summaries.

This script will output the test name and the corresponding error message for each failed test, as desired.
''',
    },
    {
        'role': 'user',
        'content': '''
I do not want to prints all lines before dashes, only the last one.
''',
    },
    {
        'role': 'assistant',
        'content': '''
Got it! To print only the test name and the last line before the dashes, you can use a combination of `awk` and `sed`. Here's a bash script block that achieves this:

```bash
#!/bin/bash

# Extract the lines with '| FAIL' and the corresponding last error message before dashes
awk '
    /\| FAIL \|/ {
        print
        getline
        while ($0 !~ /^[-=]+$/) {
            last_line = $0
            getline
        }
        print last_line
    }
' console.log | grep -v 'Tests'
```

Explanation:
1. `awk` is used to process the log file.
2. The pattern `/\| FAIL \|/` matches lines containing `| FAIL |`.
3. When a match is found, the line is printed.
4. `getline` reads the next line.
5. The `while` loop continues to read lines until it encounters a line that starts with dashes (`-`) or equals (`=`), which indicates the end of the error message block.
6. During the loop, the `last_line` variable is updated with each line read.
7. After exiting the loop, the `last_line` is printed, which contains the last line before the dashes.
8. `grep -v 'Tests'` is used to exclude lines containing 'Tests', which are typically suite summaries.

This script will output the test name and the corresponding last error message for each failed test, as desired.
''',
    },
    {
        'role': 'user',
        'content': '''
I bet that would also print suite summary (fail status and last line). Your code should not even enter the while loop when the "FAIL" line contains "Tests".
''',
    },
    {
        'role': 'assistant',
        'content': '''
You're right. To ensure that the script does not process suite summaries, we need to add a condition to skip lines containing "Tests" before entering the while loop. Here's the updated script:

```bash
#!/bin/bash

# Extract the lines with '| FAIL' and the corresponding last error message before dashes
awk '
    /\| FAIL \|/ {
        if ($0 !~ /Tests/) {
            print
            getline
            while ($0 !~ /^[-=]+$/) {
                last_line = $0
                getline
            }
            print last_line
        }
    }
' console.log
```

Explanation:
1. `awk` is used to process the log file.
2. The pattern `/\| FAIL \|/` matches lines containing `| FAIL |`.
3. The `if ($0 !~ /Tests/)` condition ensures that the script only processes lines that do not contain "Tests".
4. When a match is found and the line does not contain "Tests", the line is printed.
5. `getline` reads the next line.
6. The `while` loop continues to read lines until it encounters a line that starts with dashes (`-`) or equals (`=`), which indicates the end of the error message block.
7. During the loop, the `last_line` variable is updated with each line read.
8. After exiting the loop, the `last_line` is printed, which contains the last line before the dashes.

This script will output the test name and the corresponding last error message for each failed test, excluding suite summaries.
''',
    },
]
