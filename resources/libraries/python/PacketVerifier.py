# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""PacketVerifier module.

    :Example:

    >>> from scapy.all import *
    >>> from PacketVerifier import *
    >>> rxq = RxQueue('eth1')
    >>> txq = TxQueue('eth1')
    >>> src_mac = "AA:BB:CC:DD:EE:FF"
    >>> dst_mac = "52:54:00:ca:5d:0b"
    >>> src_ip = "11.11.11.10"
    >>> dst_ip = "11.11.11.11"
    >>> sent_packets = []
    >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    ... IP(src=src_ip, dst=dst_ip) /
    ... ICMP()
    >>> sent_packets.append(pkt_send)
    >>> txq.send(pkt_send)
    >>> pkt_send = Ether(src=src_mac, dst=dst_mac) /
    ... ARP(hwsrc=src_mac, psrc=src_ip, hwdst=dst_mac, pdst=dst_ip, op=2)
    >>> sent_packets.append(pkt_send)
    >>> txq.send(pkt_send)
    >>> rxq.recv(100, sent_packets).show()
    ###[ Ethernet ]###
      dst       = aa:bb:cc:dd:ee:ff
      src       = 52:54:00:ca:5d:0b
      type      = 0x800
    ###[ IP ]###
      version   = 4L
      ihl       = 5L
      tos       = 0x0
      len       = 28
      id        = 43183
      flags     =
      frag      = 0L
      ttl       = 64
      proto     = icmp
      chksum    = 0xa607
      src       = 11.11.11.11
      dst       = 11.11.11.10
      \options   \
    ###[ ICMP ]###
      type      = echo-reply
      code      = 0
      chksum    = 0xffff
      id        = 0x0
      seq       = 0x0
    ###[ Padding ]###
      load = 'RT\x00\xca]\x0b\xaa\xbb\xcc\xdd\xee\xff\x08\x06\x00\x01\x08\x00'
    >>> rxq._proc.terminate()
"""


import socket
import os
import time
from multiprocessing import Queue, Process
from scapy.all import ETH_P_IP, ETH_P_IPV6, ETH_P_ALL, ETH_P_ARP
from scapy.all import Ether, ARP, Packet
from scapy.layers.inet6 import IPv6

__all__ = ['RxQueue', 'TxQueue', 'Interface', 'create_gratuitous_arp_request',
           'auto_pad']

# TODO: http://stackoverflow.com/questions/320232/ensuring-subprocesses-are-dead-on-exiting-python-program

class PacketVerifier(object):
    """Base class for TX and RX queue objects for packet verifier."""
    def __init__(self, interface_name):
        os.system('sudo echo 1 > /proc/sys/net/ipv6/conf/{0}/disable_ipv6'
                  .format(interface_name))
        os.system('sudo ip link set {0} up promisc on'.format(interface_name))
        self._sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                                   ETH_P_ALL)
        self._sock.bind((interface_name, ETH_P_ALL))


def extract_one_packet(buf):
    """Extract one packet from the incoming buf buffer.

    Takes string as input and looks for first whole packet in it.
    If it finds one, it returns substring from the buf parameter.

    :param buf: string representation of incoming packet buffer.
    :type buf: string
    :return: String representation of first packet in buf.
    :rtype: string
    """
    pkt_len = 0

    if len(buf) < 60:
        return None

    # print
    # print buf.__repr__()
    # print Ether(buf).__repr__()
    # print len(Ether(buf))
    # print
    try:
        ether_type = Ether(buf[0:14]).type
    except AttributeError:
        raise RuntimeError(
            'No EtherType in packet {0}'.format(buf.__repr__()))

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
            raise RuntimeError(
                'Invalid IPv6 packet {0}'.format(buf.__repr__()))
        # ... to add to the above, 40 bytes is the length of IPV6 header.
        #   The ipv6.len only contains length of the payload and not the header
        pkt_len = Ether(buf)['IPv6'].plen + 14 + 40
        if len(buf) < 60:
            return None
    elif ether_type == ETH_P_ARP:
        pkt = Ether(buf[:20])
        if not pkt.haslayer(ARP):
            raise RuntimeError('Incomplete ARP packet')
        # len(eth) + arp(2 hw addr type + 2 proto addr type
        #                + 1b len + 1b len + 2b operation)

        pkt_len = 14 + 8
        pkt_len += 2 * pkt.getlayer(ARP).hwlen
        pkt_len += 2 * pkt.getlayer(ARP).plen

        del pkt
    elif ether_type == 32821:  # RARP (Reverse ARP)
        pkt = Ether(buf[:20])
        pkt.type = ETH_P_ARP  # Change to ARP so it works with scapy
        pkt = Ether(str(pkt))
        if not pkt.haslayer(ARP):
            pkt.show()
            raise RuntimeError('Incomplete RARP packet')

        # len(eth) + arp(2 hw addr type + 2 proto addr type
        #                + 1b len + 1b len + 2b operation)
        pkt_len = 14 + 8
        pkt_len += 2 * pkt.getlayer(ARP).hwlen
        pkt_len += 2 * pkt.getlayer(ARP).plen

        del pkt
    else:
        raise RuntimeError('Unknown protocol {0}'.format(ether_type))

    if pkt_len < 60:
        pkt_len = 60

    if len(buf) < pkt_len:
        return None

    return buf[0:pkt_len]


def packet_reader(interface_name, queue):
    """Sub-process routine that reads packets and puts them to queue.

    This function is meant to be run in separate subprocess and is in tight
    loop reading raw packets from interface passed as parameter.

    :param interace_name: Name of interface to read packets from.
    :param queue: Queue in which this function will push incoming packets.
    :type interface_name: string
    :type queue: multiprocessing.Queue
    :return: None
    """
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, ETH_P_ALL)
    sock.bind((interface_name, ETH_P_ALL))

    buf = ""
    while True:
        recvd = sock.recv(1500)
        buf = buf + recvd

        pkt = extract_one_packet(buf)
        while pkt is not None:
            if pkt is None:
                break
            queue.put(pkt)
            buf = buf[len(pkt):]
            pkt = extract_one_packet(buf)


class RxQueue(PacketVerifier):
    """Receive queue object.

    This object creates raw socket, reads packets from it and provides
    function to access them.

    :param interface_name: Which interface to bind to.
    :type interface_name: string
    """

    def __init__(self, interface_name):
        PacketVerifier.__init__(self, interface_name)

        self._queue = Queue()
        self._proc = Process(target=packet_reader, args=(interface_name,
                                                         self._queue))
        self._proc.daemon = True
        self._proc.start()
        time.sleep(2)

    def recv(self, timeout=3, ignore=None):
        """Read next received packet.

        Returns scapy's Ether() object created from next packet in the queue.
        Queue is being filled in parallel in subprocess. If no packet
        arrives in given timeout queue.Empty exception will be risen.

        :param timeout: How many seconds to wait for next packet.
        :type timeout: int

        :return: Ether() initialized object from packet data.
        :rtype: scapy.Ether
        """

        pkt = self._queue.get(True, timeout=timeout)

        if ignore is not None:
            for i, ig_pkt in enumerate(ignore):
                # Auto pad all packets in ignore list
                ignore[i] = auto_pad(ig_pkt)
            for ig_pkt in ignore:
                if ig_pkt == pkt:
                    # Found the packet in ignore list, get another one
                    # TODO: subtract timeout - time_spent in here
                    ignore.remove(ig_pkt)
                    return self.recv(timeout, ignore)

        return Ether(pkt)


class TxQueue(PacketVerifier):
    """Transmission queue object.

    This object is used to send packets over RAW socket on a interface.

    :param interface_name: Which interface to send packets from.
    :type interface_name: string
    """
    def __init__(self, interface_name):
        PacketVerifier.__init__(self, interface_name)

    def send(self, pkt):
        """Send packet out of the bound interface.

        :param pkt: Packet to send.
        :type pkt: string or scapy Packet derivative.
        """
        if isinstance(pkt, Packet):
            pkt = str(pkt)
        pkt = auto_pad(pkt)
        self._sock.send(pkt)


class Interface(object):
    def __init__(self, if_name):
        self.if_name = if_name
        self.sent_packets = []
        self.txq = TxQueue(if_name)
        self.rxq = RxQueue(if_name)

    def send_pkt(self, pkt):
        self.sent_packets.append(pkt)
        self.txq.send(pkt)

    def recv_pkt(self, timeout=3):
        while True:
            pkt = self.rxq.recv(timeout, self.sent_packets)
            # TODO: FIX FOLLOWING: DO NOT SKIP RARP IN ALL TESTS!!!
            if pkt.type != 32821:  # Skip RARP packets
                return pkt

    def close(self):
        self.rxq._proc.terminate()


def create_gratuitous_arp_request(src_mac, src_ip):
    """Creates scapy representation of gratuitous ARP request"""
    return (Ether(src=src_mac, dst='ff:ff:ff:ff:ff:ff') /
            ARP(psrc=src_ip, hwsrc=src_mac, pdst=src_ip))


def auto_pad(packet):
    """Pads zeroes at the end of the packet if the total len < 60 bytes."""
    padded = str(packet)
    if len(padded) < 60:
        padded += ('\0' * (60 - len(padded)))
    return padded

