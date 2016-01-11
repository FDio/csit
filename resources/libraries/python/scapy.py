# Copyright (c) 2015 Cisco and/or its affiliates.
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

"""This is an idea how Scapy could be used to do conformance packet testing.


Scapy can't be listening and seding at the same time, so we need to initialize
sniffing in a multiprocess sub process and send the packets in the main one.

 - start sniff background process
 - send packets as per test
 - wait for the background process with timeout
 - collect captured packets (pcap file?)
 - verify everything is received as expected

"""



#Following code is just an idea how to start laying out the code for this lib

from multiprocessing import Process

from scapy.all import *


def sub_sniff(**kwargs):
        #import pdb; pdb.set_trace()
        p = sniff(**kwargs)
        p.show()


proc = Process(target=sub_sniff, kwargs={'count' : 1, 'iface' : 'eth2'})

proc.start()


import time

time.sleep(2)
sendp(Ether(), iface='eth1')



proc.join()

