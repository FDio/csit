# Copyright (c) 2021 Cisco and/or its affiliates.
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-2.0-or-later
#
# Licensed under the Apache License 2.0 or
# GNU General Public License v2.0 or later;  you may not use this file
# except in compliance with one of these Licenses. You
# may obtain a copy of the Licenses at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#     https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
#
# Note: If this file is linked with Scapy, which is GPLv2+, your use of it
# must be under GPLv2+.  If at any point in the future it is no longer linked
# with Scapy (or other GPLv2+ licensed software), you are free to choose
# Apache 2.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PacketVerifier module.

  Example. ::

    | >>> from scapy.all import *
    | >>> from PacketVerifier import *
    | >>> rxq = RxQueue('eth1')
    | >>> txq = TxQueue('eth1')
    | >>> src_mac = "AA:BB:CC:DD:EE:FF"
    | >>> dst_mac = "52:54:00:ca:5d:0b"
    | >>> src_ip = "11.11.11.10"
    | >>> dst_ip = "11.11.11.11"
    | >>> sent_packets = []
    | >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    | ... IP(src=src_ip, dst=dst_ip) /
    | ... ICMP()
    | >>> sent_packets.append(pkt_send)
    | >>> txq.send(pkt_send)
    | >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    | ... ARP(hwsrc=src_mac, psrc=src_ip, hwdst=dst_mac, pdst=dst_ip, op=2)
    | >>> sent_packets.append(pkt_send)
    | >>> txq.send(pkt_send)
    | >>> rxq.recv(100, sent_packets).show()
    | ###[ Ethernet ]###
    |   dst       = aa:bb:cc:dd:ee:ff
    |   src       = 52:54:00:ca:5d:0b
    |   type      = 0x800
    | ###[ IP ]###
    |   version   = 4L
    |   ihl       = 5L
    |   tos       = 0x0
    |   len       = 28
    |   id        = 43183
    |   flags     =
    |   frag      = 0L
    |   ttl       = 64
    |   proto     = icmp
    |   chksum    = 0xa607
    |   src       = 11.11.11.11
    |   dst       = 11.11.11.10
    |   options
    | ###[ ICMP ]###
    |   type      = echo-reply
    |   code      = 0
    |   chksum    = 0xffff
    |   id        = 0x0
    |   seq       = 0x0
    | ###[ Padding ]###
    |   load = 'RT\x00\xca]\x0b\xaa\xbb\xcc\xdd\xee\xff\x08\x06\x00\x01\x08\x00'

  Example end.
"""

import os
import select

from scapy.all import ETH_P_IP, ETH_P_IPV6, ETH_P_ALL, ETH_P_ARP
from scapy.config import conf
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether, ARP
from scapy.packet import Raw, Padding

# Enable libpcap's L2listen
conf.use_pcap = True

__all__ = [
    u"RxQueue", u"TxQueue", u"Interface", u"create_gratuitous_arp_request",
    u"auto_pad", u"checksum_equal"
]

# TODO: http://stackoverflow.com/questions/320232/
# ensuring-subprocesses-are-dead-on-exiting-python-program


class PacketVerifier:
    """Base class for TX and RX queue objects for packet verifier."""
    def __init__(self, interface_name):
        os.system(
            f"sudo echo 1 > /proc/sys/net/ipv6/conf/{interface_name}/"
            f"disable_ipv6"
        )
        os.system(f"sudo ip link set {interface_name} up promisc on")
        self._ifname = interface_name


def extract_one_packet(buf):
    """Extract one packet from the incoming buf buffer.

    Takes string as input and looks for first whole packet in it.
    If it finds one, it returns substring from the buf parameter.

    :param buf: String representation of incoming packet buffer.
    :type buf: str
    :returns: String representation of first packet in buf.
    :rtype: str
    """
    pkt_len = 0

    if len(buf) < 60:
        return None

    try:
        ether_type = Ether(buf[0:14]).type
    except AttributeError:
        raise RuntimeError(f"No EtherType in packet {buf!r}")

    if ether_type == ETH_P_IP:
        # 14 is Ethernet fame header size.
        # 4 bytes is just enough to look for length in ip header.
        # ip total length contains just the IP packet length so add the Ether
        #     header.
        pkt_len = Ether(buf[0:14+4]).len + 14
        if len(buf) < 60:
            return None
    elif ether_type == ETH_P_IPV6:
        if not Ether(buf[0:14+6]).haslayer(IPv6):
            raise RuntimeError(f"Invalid IPv6 packet {buf!r}")
        # ... to add to the above, 40 bytes is the length of IPV6 header.
        #   The ipv6.len only contains length of the payload and not the header
        pkt_len = Ether(buf)[u"IPv6"].plen + 14 + 40
        if len(buf) < 60:
            return None
    elif ether_type == ETH_P_ARP:
        pkt = Ether(buf[:20])
        if not pkt.haslayer(ARP):
            raise RuntimeError(u"Incomplete ARP packet")
        # len(eth) + arp(2 hw addr type + 2 proto addr type
        #                + 1b len + 1b len + 2b operation)

        pkt_len = 14 + 8
        pkt_len += 2 * pkt.getlayer(ARP).hwlen
        pkt_len += 2 * pkt.getlayer(ARP).plen

        del pkt
    elif ether_type == 32821:  # RARP (Reverse ARP)
        pkt = Ether(buf[:20])
        pkt.type = ETH_P_ARP  # Change to ARP so it works with scapy
        pkt = Ether(pkt)
        if not pkt.haslayer(ARP):
            pkt.show()
            raise RuntimeError(u"Incomplete RARP packet")

        # len(eth) + arp(2 hw addr type + 2 proto addr type
        #                + 1b len + 1b len + 2b operation)
        pkt_len = 14 + 8
        pkt_len += 2 * pkt.getlayer(ARP).hwlen
        pkt_len += 2 * pkt.getlayer(ARP).plen

        del pkt
    else:
        raise RuntimeError(f"Unknown protocol {ether_type}")

    if pkt_len < 60:
        pkt_len = 60

    if len(buf) < pkt_len:
        return None

    return buf[0:pkt_len]


def packet_reader(interface_name, queue):
    """Sub-process routine that reads packets and puts them to queue.

    This function is meant to be run in separate subprocess and is in tight
    loop reading raw packets from interface passed as parameter.

    :param interface_name: Name of interface to read packets from.
    :param queue: Queue in which this function will push incoming packets.
    :type interface_name: str
    :type queue: multiprocessing.Queue
    """
    sock = conf.L2listen(iface=interface_name, type=ETH_P_ALL)

    while True:
        pkt = sock.recv(0x7fff)
        queue.put(pkt)


class RxQueue(PacketVerifier):
    """Receive queue object.

    This object creates raw socket, reads packets from it and provides
    function to access them.

    :param interface_name: Which interface to bind to.
    :type interface_name: str
    """
    def __init__(self, interface_name):
        PacketVerifier.__init__(self, interface_name)
        self._sock = conf.L2listen(iface=interface_name, type=ETH_P_ALL)

    def recv(self, timeout=3, ignore=None, verbose=True):
        """Read next received packet.

        Returns scapy's Ether() object created from next packet in the queue.
        Queue is being filled in parallel in subprocess. If no packet
        arrives in given timeout None is returned.

        If the list of packets to ignore is given, they are logged
        but otherwise ignored upon arrival, not adding to the timeout.
        Each time a packet is ignored, it is removed from the ignored list.

        :param timeout: How many seconds to wait for next packet.
        :param ignore: List of packets that should be ignored.
        :param verbose: Used to suppress detailed logging of received packets.
        :type timeout: int
        :type ignore: list
        :type verbose: bool

        :returns: Ether() initialized object from packet data.
        :rtype: scapy.Ether
        """
        time_end = time.monotonic() + timeout
        ignore = ignore if ignore else list()
        # Auto pad all packets in ignore list
        ignore = [str(auto_pad(ig_pkt)) for ig_pkt in ignore]
        while 1:
            time_now = time.monotonic()
            if time_now >= time_end:
                return None
            timedelta = time_end - time_now
            rlist, _, _ = select.select([self._sock], [], [], timedelta)
            if self._sock not in rlist:
                # Might have been an interrupt.
                continue
            pkt = self._sock.recv(0x7fff)
            pkt_pad = str(auto_pad(pkt))
            print(f"Received packet on {self._ifname} of len {len(pkt)}")
            if verbose:
                if hasattr(pkt, u"show2"):
                    pkt.show2()
                else:
                    # Never happens in practice, but Pylint does not know that.
                    print(f"Unexpected instance: {pkt!r}")
                print()
            if pkt_pad in ignore:
                ignore.remove(pkt_pad)
                print(u"Received packet ignored.")
                continue
            return pkt


class TxQueue(PacketVerifier):
    """Transmission queue object.

    This object is used to send packets over RAW socket on a interface.

    :param interface_name: Which interface to send packets from.
    :type interface_name: str
    """
    def __init__(self, interface_name):
        PacketVerifier.__init__(self, interface_name)
        self._sock = conf.L2socket(iface=interface_name, type=ETH_P_ALL)

    def send(self, pkt, verbose=True):
        """Send packet out of the bound interface.

        :param pkt: Packet to send.
        :param verbose: Used to suppress detailed logging of sent packets.
        :type pkt: string or scapy Packet derivative.
        :type verbose: bool
        """
        pkt = auto_pad(pkt)
        print(f"Sending packet out of {self._ifname} of len {len(pkt)}")
        if verbose:
            pkt.show2()
            print()

        self._sock.send(pkt)


class Interface:
    """Class for network interfaces. Contains methods for sending and receiving
     packets."""
    def __init__(self, if_name):
        """Initialize the interface class.

        :param if_name: Name of the interface.
        :type if_name: str
        """
        self.if_name = if_name
        self.sent_packets = []
        self.rxq = RxQueue(if_name)
        self.txq = TxQueue(if_name)

    def send_pkt(self, pkt):
        """Send the provided packet out the interface."""
        self.sent_packets.append(pkt)
        self.txq.send(pkt)

    def recv_pkt(self, timeout=3):
        """Read one packet from the interface's receive queue.

        :param timeout: Timeout value in seconds.
        :type timeout: int
        :returns: Ether() initialized object from packet data.
        :rtype: scapy.Ether
        """
        return self.rxq.recv(timeout, self.sent_packets)


def create_gratuitous_arp_request(src_mac, src_ip):
    """Creates scapy representation of gratuitous ARP request."""
    return (Ether(src=src_mac, dst=u"ff:ff:ff:ff:ff:ff") /
            ARP(psrc=src_ip, hwsrc=src_mac, pdst=src_ip)
            )


def auto_pad(packet):
    """Pads zeroes at the end of the packet if the total packet length is less
    then 60 bytes in case of IPv4 or 78 bytes in case of IPv6.
    """
    # TODO: add document explaining deduction of FCS part
    min_len = 78 if packet.haslayer(IPv6) else 60
    pad_layer = Raw if packet.haslayer(Raw) \
        else Padding if packet.haslayer(Padding) else None
    if pad_layer:
        packet[pad_layer].load += (b"\0" * (min_len - len(packet)))
    return packet


def checksum_equal(chksum1, chksum2):
    """Compares two checksums in one's complement notation.

    Checksums to be compared are calculated as 16 bit one's complement of the
    one's complement sum of 16 bit words of some buffer.
    In one's complement notation 0x0000 (positive zero) and 0xFFFF
    (negative zero) are equivalent.

    :param chksum1: First checksum.
    :param chksum2: Second checksum.
    :type chksum1: uint16
    :type chksum2: uint16

    :returns: True if checksums are equivalent, False otherwise.
    :rtype: boolean
    """
    if chksum1 == 0xFFFF:
        chksum1 = 0
    if chksum2 == 0xFFFF:
        chksum2 = 0
    return chksum1 == chksum2
