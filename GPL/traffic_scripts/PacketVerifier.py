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
    | >>> txq, rxq = start_queue_pair('eth1', ignore_list=list())
    | >>> src_mac = "AA:BB:CC:DD:EE:FF"
    | >>> dst_mac = "52:54:00:ca:5d:0b"
    | >>> src_ip = "11.11.11.10"
    | >>> dst_ip = "11.11.11.11"
    | >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    | ... IP(src=src_ip, dst=dst_ip) /
    | ... ICMP()
    | >>> txq.send(pkt_send)
    | >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    | ... ARP(hwsrc=src_mac, psrc=src_ip, hwdst=dst_mac, pdst=dst_ip, op=2)
    | >>> txq.send(pkt_send)
    | >>> rxq.recv(100).show()
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
import time

from scapy.all import ETH_P_IP, ETH_P_IPV6, ETH_P_ALL, ETH_P_ARP
from scapy.config import conf
from scapy.layers.inet6 import IPv6, ICMPv6ND_NS, ICMPv6MLReport2, ICMPv6ND_RA
from scapy.layers.l2 import Ether, ARP
from scapy.packet import Raw, Padding

# Enable libpcap's L2listen
conf.use_pcap = True

__all__ = [
    u"FilteringRxQueue", u"DefaultRxQueue", u"TxQueue",
    u"start_queue_pair", u"start_4_queues",
    u"create_gratuitous_arp_request", u"auto_pad", u"checksum_equal"
]

# TODO: http://stackoverflow.com/questions/320232/
# ensuring-subprocesses-are-dead-on-exiting-python-program


class PacketVerifier:
    """Base class for TX and RX queue objects for packet verifier."""
    def __init__(self, interface_name, *args, **kwargs):
        """Attempt to disable ipv6, set interface up in promisc mode.

        Args and kwargs are there to enable subclass constructors
        to have additional arguments.

        :param interface_name: Which interface to bind to.
        :type interface_name: str
        """
        # TODO: How is this disabled (on Ubuntu 20.04)
        # when we still have to filter out some IPv6 packets?
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
    except AttributeError as exc:
        raise RuntimeError(f"No EtherType in packet {buf!r}") from exc

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

    pkt_len = max(60, pkt_len)

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


class FilteringRxQueue(PacketVerifier):
    """Receive queue object able to skip over some (configurable) packets.

    This object creates raw socket, reads packets from it and provides
    function to access them.

    Upon creation, a filter function can be provided to control
    which packets are silently ignored.
    """

    def __init__(self, interface_name, filter_f=None, *args, **kwargs):
        """Construct the instance, start listening on the interface.

        Args and kwargs are there to enable subclass constructors
        to have additional arguments.

        :param interface_name: Which interface to bind to.
        :param filter_f: Function to classify packets, return True means skip.
            If None, no packet is skipped.
        :type interface_name: str
        :type filter_f: Optional[Callable[[scapy.Ether], bool]]
        """
        super().__init__(interface_name, *args, **kwargs)
        self._sock = conf.L2listen(iface=interface_name, type=ETH_P_ALL)
        self._filter_f = (lambda pkt: False) if filter_f is None else filter_f

    def recv(self, timeout=3, verbose=True, do_raise=True):
        """Read packets within timeout, return first one that is not filtered.

        Returns scapy's Ether() object created from next packet in the queue.
        Queue is being filled in parallel in subprocess. If no packet
        (passing the filter) arrives in given timeout, None is returned
        or RuntimeError is raised, depending on do_raise argument.

        Benign interrupt signals and filtered-out packets
        are silently ignored, without affecting timeout.

        :param timeout: How many seconds to wait for next packet.
        :param verbose: Used to suppress detailed logging of received packets.
        :param do_raise: Whether timeout should raise exception or return None.
        :type timeout: int
        :type verbose: bool
        :type do_raise: bool
        :returns: Ether() initialized object from packet data.
        :rtype: Optional[scapy.Ether]
        :raises RuntimeError: On timeout, if do_raise is true.
        """
        time_end = time.monotonic() + timeout
        while 1:
            time_now = time.monotonic()
            if time_now >= time_end:
                if do_raise:
                    raise RuntimeError("Timed out waiting for a packet.")
                return None
            timedelta = time_end - time_now
            rlist, _, _ = select.select([self._sock], [], [], timedelta)
            if self._sock not in rlist:
                # Might have been an interrupt.
                continue
            pkt = self._sock.recv(0x7fff)
            print(f"Received packet on {self._ifname} of len {len(pkt)}")
            if verbose:
                if hasattr(pkt, u"show2"):
                    pkt.show2()
                else:
                    # Never happens in practice, but Pylint does not know that.
                    print(f"Unexpected instance: {pkt!r}")
                print()
            if self._filter_f(pkt):
                print(u"Received packet ignored.")
                continue
            return pkt


class DefaultRxQueue(FilteringRxQueue):
    """Receive queue object able to skip over some (hardcoded) packets.

    This object creates raw socket, reads packets from it and provides
    function to access them.

    Filter function can still be provided to override the default filtering.

    TODO: Does this need to be a subclass?
    Maybe we can have a factory function for FilteringRxQueue,
    defined either inside or outside that class.
    """

    def __init__(
            self, interface_name, filter_f=None, ignore=None,
            filter_ip6=True, *args, **kwargs):
        """Construct the instance, start listening on the interface.

        Args and kwargs are there to enable subclass constructors
        to have additional arguments.

        If filter_f is None, the default filter is used.
        See docstring of default_filter for details.

        The "ignore" value is treated as a reference to an iterable
        that also supports .remove(), so basically it has to be a list.
        Filter tracks which packet was skipped by removing it from the list.

        :param interface_name: Which interface to bind to.
        :param filter_f: Override function to classify packets.
            None means the default filter is used.
        :param ignore: List of packets to skip over, once each.
            None means empty list.
        :param filter_ip6: Skip over autogenerated IP6 related packets if true.
        :type interface_name: str
        :type filter_f: Optional[Callable[[scapy.Ether], bool]]
        :type ignore: Optional[List[scapy.Ether]]
        :type filter_ip6: bool
        """
        ignore_list = list() if ignore is None else ignore
        # Default filter accesses the ignore list (the line above),
        # so it is a closure and has to be defined here, inside the constructor.
        def default_filter(packet):
            """Return whether this (auto_padded) packet can be skipped.

            There are two conditions for skip.

            First, some packet types related to IPv6 autonegotiation are
            always skipped (unless overriden by filter_ip6==False).

            Second, packets listed in ignore_list are skipped, each once.
            For packet comparison, both are auto-padded and converted to str.
            Filter tracks which packet was skipped by removing it from the list.

            :param packet: The packet to classify.
            :type packet: scapy.Ether
            :returns: True if skip, False if no skip.
            :rtype bool
            """
            # One-time ignore part.
            pkt_pad = str(auto_pad(packet))
            for ignored in ignore_list:
                # Caller may have mutated the referenced list
                # since the constructor or the recv method was called last,
                # so we cannot cache the padded forms.
                ignored_pad = str(auto_pad(ignored))
                if ignored_pad == pkt_pad:
                    ignore_list.remove(ignored)
                    return True
            # IPv6 part, more readable when at the end.
            return filter_ip6 and (
                packet.haslayer(ICMPv6ND_NS)
                or packet.haslayer(ICMPv6MLReport2)
                or packet.haslayer(ICMPv6ND_RA)
            )
        filter_f = default_filter if filter_f is None else filter_f
        super().__init__(interface_name, filter_f=filter_f, *args, **kwargs)

    # .recv() is inherited from FilteringRxQueue

class TxQueue(PacketVerifier):
    """Transmission queue object.

    This object is used to send packets over RAW socket on a interface.

    Optionally, it remembers packets sent in an external list.
    That is useful for DefaultRxQueue filtering.
    """
    def __init__(self, interface_name, remember=None, *args, **kwargs):
        """Construct the instance, start listening on the interface.

        Args and kwargs are there to enable subclass constructors
        to have additional arguments.

        :param interface_name: Which interface to send packets from.
        :param remember: List reference to append sent packets to.
            None means do not append anywhere.
        :type interface_name: str
        :type remember: Optuional[List[scapy.Ether]]
        """
        super().__init__(interface_name, *args, **kwargs)
        self._sock = conf.L2socket(iface=interface_name, type=ETH_P_ALL)
        self._remember = remember

    def send(self, pkt, verbose=True):
        """Send packet out of the bound interface.

        Auto-pad the packet before sending.

        Optionally append the padded packet to a list,
        useful for the default rx filter.

        :param pkt: Packet to send.
        :param verbose: Used to suppress detailed logging of sent packets.
        :param append_to: List of packets to append this one to, if not None.
        :type pkt: string or scapy Packet derivative.
        :type verbose: bool
        :type append_to: Optional[List[scapy.Ether]]
        """
        pkt = auto_pad(pkt)
        print(f"Sending packet out of {self._ifname} of len {len(pkt)}")
        if verbose:
            pkt.show2()
            print()
        if self._remember is not None:
            self._remember.append(pkt)

        self._sock.send(pkt)


def start_queue_pair(interface_name, ignore_list=None, filter_ip6=True):
    """Return TX queue and RX queue where RX may ignores packets sent.

    In many circumstances, a packet sent via the TX queue is immediately
    seen also in the RX queue. Some tests do not want to see such "self-cast".
    Example: If the "other side" is the same interface.

    If ignore_list is not None,
    packets are appended ther by TxQueue.send(),
    and removed by one when seen in DefaultRxQueue.recv().
    You can use the same list for multiple calls, resulting in the sent packet
    to be ignored in the first rxq that sees it.

    TODO: Are separate queues useful?
    If not, replace them with Interface class with both send() and recv().

    :param interface_name: Which interface to send packets from and bind to.
    :param ignore_list: Reference to an existing list to track sent packets.
        If None, packets are not tracket (so not skipped on receive).
    :param filter_ip6: Skip over autogenerated IP6 related packets if true.
    :type interface_name: str
    :type ignore_list: Optional[List[scapy.Ether]]
    :type filter_ip6: bool
    :returns: Initialized instances for TX queue and Rx queue.
    :rtype: TxQueue, DefaultRxQueue
    """
    txq = TxQueue(interface_name, remember=ignore_list)
    rxq = DefaultRxQueue(
        interface_name, ignore=ignore_list, filter_ip6=filter_ip6
    )
    return txq, rxq


def start_4_queues(args, filter_ip6=True):
    """Start 2 or 4 queues, ignoring self-cast on either side.

    Names for the interfaces are read from args.

    Traditionally, tx_interface is where the first packet is sent from,
    but there frequently are response packets comming back from rx_interface,
    so a general traffic script needs two TX queues and two RX queues.
    If a script needs only ony direction (2 queues), it can ignore the other 2.

    As interfaces are listening in promisc mode, they see also the packets
    the send. Such packets are ignored, using a list of sent packets
    for each interface separately.

    The case where the two interface names are equal is also supported,
    in that case only two queues are created (one list of sent packets
    to ignore), but still returned as 4 queue references.

    :param args: Script arg object with parsed command line arguments.
        May be identical to the first one.
    :param filter_ip6: Skip over autogenerated IP6 related packets if true.
    :type args: TrafficScriptArg
    :type filter_ip6: bool
    :returns: Queue references: tx_txq, tx_rxq, rx_txq, rx_rxq.
    :rtype: TxQueue, DefaultRxQueue, TxQueue, DefaultRxQueue
    """
    tx_interface = args.get_arg(u"tx_if")
    rx_interface = args.get_arg(u"rx_if")
    if tx_interface == rx_interface:
        ignore_list = list()
        txq, rxq = start_queue_pair(
            tx_interface, ignore_list=ignore_list, filter_ip6=filter_ip6
        )
        return txq, rxq, txq, rxq
    ignore_list_tx, ignore_list_rx = list(), list()
    tx_txq, tx_rxq = start_queue_pair(
        tx_interface, ignore_list=ignore_list_tx, filter_ip6=filter_ip6
    )
    rx_txq, rx_rxq = start_queue_pair(
        rx_interface, ignore_list=ignore_list_rx, filter_ip6=filter_ip6
    )
    return tx_txq, tx_rxq, rx_txq, rx_rxq


def create_gratuitous_arp_request(src_mac, src_ip):
    """Creates scapy representation of gratuitous ARP request."""
    return (
        Ether(src=src_mac, dst=u"ff:ff:ff:ff:ff:ff")
        / ARP(psrc=src_ip, hwsrc=src_mac, pdst=src_ip)
    )


def auto_pad(packet):
    """Pads zeroes at the end of the packet if the total packet length is less
    then 60 bytes in case of IPv4 or 78 bytes in case of IPv6.

    :param packet: The packet to pad.
    :type packet: scapy.Ether
    :returns: The packet, with its data padded with zero to minimal length.
    :rtype: scapy.Ether
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
