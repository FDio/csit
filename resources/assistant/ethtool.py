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

import logging
import os
import sys

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

logging.basicConfig(level=logging.DEBUG)

client = MistralClient(api_key=api_key)

#print(f"{client.list_models()!r}")
#sys.exit(1)


messages = [
    ChatMessage(role="system", content='''
You are a system administrator.
'''),
    ChatMessage(role="user", content='''
Hi, I have a problem.
I have a perfomance test for IPsec protocol,
but it sets up multiple tunnels with the same 5-tuple,
only differing by SPI field.
As my application uses multiple cores,
I rely on RSS to distribute the encrypted traffic over receive queues,
but currently everything goes to the same queue.
My application uses user-space networking
(bypassing kernel), but I believe the RSS settings
get "inherited", so I can use ethtool to reconfigure RSS.

Using command ```ethtool -n "${device}" rx-flow-hash esp4``` I get
```
IPSEC AH/ESP over IPV4 flows use these fields for computing Hash flow key:
None
```
and similarly ```ethtool -n "${device}" rx-flow-hash udp4``` returns
```
UDP over IPV4 flows use these fields for computing Hash flow key:
IP SA
IP DA
L4 bytes 0 & 1 [TCP/UDP src port]
L4 bytes 2 & 3 [TCP/UDP dst port]
```

I would like to change both (some of my tests do apply UDP encapsulation,
some do not) and it seems I could use ```ethtool -N```,
but I have trouble searching Internet for example of corrrect usage.
Most examples use -N to set up specific flows,
but I want only to change the hashing.

Here are parts of ethtool manual page. Can you figure out the correct usage
of -N for my case?

```
ethtool [ FLAGS ] -n|-u|--show-nfc|--show-ntuple DEVNAME        Show Rx network flow classification options or rules
        [ rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6 [context %d] |
          rule %d ]
        ethtool [ FLAGS ] -N|-U|--config-nfc|--config-ntuple DEVNAME    Configure Rx network flow classification options or rules
        rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6 m|v|t|s|d|f|n|r... [context %d] |
        flow-type ether|ip4|tcp4|udp4|sctp4|ah4|esp4|ip6|tcp6|udp6|ah6|esp6|sctp6
            [ src %x:%x:%x:%x:%x:%x [m %x:%x:%x:%x:%x:%x] ]
            [ dst %x:%x:%x:%x:%x:%x [m %x:%x:%x:%x:%x:%x] ]
            [ proto %d [m %x] ]
            [ src-ip IP-ADDRESS [m IP-ADDRESS] ]
            [ dst-ip IP-ADDRESS [m IP-ADDRESS] ]
            [ tos %d [m %x] ]
            [ tclass %d [m %x] ]
            [ l4proto %d [m %x] ]
            [ src-port %d [m %x] ]
            [ dst-port %d [m %x] ]
            [ spi %d [m %x] ]
            [ vlan-etype %x [m %x] ]
            [ vlan %x [m %x] ]
            [ user-def %x [m %x] ]
            [ dst-mac %x:%x:%x:%x:%x:%x [m %x:%x:%x:%x:%x:%x] ]
            [ action %d ] | [ vf %d queue %d ]
            [ context %d ]
            [ loc %d]] |
        delete %d
```
'''),
    ChatMessage(role="assistant", content='''
Based on the ethtool manual page you provided, it seems that the `-N` or `--config-nfc` flag is used to configure the Rx network flow classification options or rules. To change the hashing for IPsec ESP over IPv4 and UDP over IPv4, you can use the following commands:

For IPsec ESP over IPv4:
```
ethtool -N "${device}" rx-flow-hash esp4 s d ip
```
This command configures the Rx flow hash for ESP over IPv4 to use the source and destination IP addresses.

For UDP over IPv4:
```
ethtool -N "${device}" rx-flow-hash udp4 s d ip udp
```
This command configures the Rx flow hash for UDP over IPv4 to use the source and destination IP addresses, as well as the UDP source and destination ports.

In both commands, `${device}` should be replaced with the name of your network interface.

After running these commands, you can verify the changes by using the `-n` or `--show-nfc` flag:

For IPsec ESP over IPv4:
```
ethtool -n "${device}" rx-flow-hash esp4
```
For UDP over IPv4:
```
ethtool -n "${device}" rx-flow-hash udp4
```
These commands should now display the updated hash fields for ESP over IPv4 and UDP over IPv4, respectively.
'''),
]

stream_response = client.chat_stream(
    model=model,
    messages=messages,
    temperature=0.0,
    safe_prompt=False,
    safe_mode=True,
    max_tokens=5000,
)

for chunk in stream_response:
    print(chunk.choices[0].delta.content, end="", flush=True)

print(f"\n\n\n{chunk.choices[0].finish_reason!r}")
print(f"{chunk.usage!r}")
