from trex_stl_lib.api import *

# Simulates UDP flows by creating multiple streams with random dst ports
#
# Parameters:
# size            - packet size
# mpps            - total pps rate in single direction
# n_flows         - total number of simulated flows
# burst_sec       - single stream duration in seconds
# inter_burst_gap - duration between 2 bursts of specific stream
# streams_per_sec - number of streams started every second, 10 means new
#                   stream is started every 100 msec
#
# By default this profile will generate 200 streams, new stream every 100 msec
# and each stream will burst for 10 seconds and then wait for another 10 sec
# repeatedly. As a result it will never be there more than 100 streams
# bursting and each stream will have pps rate of 100Kpps resulting in total
# rate of 10 Mpps on each port
# To simulate multiple flows per stream, each flow will randomize src or dst
# port (based on direction). To get 1000 flows each of 200 streams will
# randomize port in range 0-4
# Gemerated traffic is symetrical, so it can represent bi-directional traffic
#
# Standard way start traffic with cusrom arguments from TRex console:
#
# trex>start -f stl/flowsim.py -p 0 1 -t mpps=11,n_flows=4000000; tui; stop -a



class STLS1(object):

    def get_streams(self, size=64, rate=10, n_flows=10, burst_sec=10,
                    inter_burst_gap=10, streams_per_second=10,
                    direction=0, **kwargs):

        ip = ["20.0.0.0", "12.0.0.2"]
        ip2 = ["12.0.0.2", "200.0.0.0"]
        smac = ["3c:fe:b5:3f:61:00", "3c:fe:b5:3f:60:00"]
        dmac = ["3c:fd:fe:b5:3e:c9", "3c:fd:fe:b5:3e:c8"]

        #pps = mpps * 1e6
        pps = float(rate[:-3])
        n_streams = streams_per_second * (burst_sec + inter_burst_gap)
        duty_cycle = burst_sec / (burst_sec + inter_burst_gap)
        pps_per_stream = int(pps / (n_streams * duty_cycle))
        pkts_per_burst = int(burst_sec * pps / (n_streams * duty_cycle))
        n_flows_per_stream = int(n_flows / n_streams)
        print(pps, n_streams, duty_cycle, pps_per_stream, pkts_per_burst, n_flows_per_stream)
        if direction == 0:
            src_ip = ip[0]
            dst_ip = ip[1]
            src_mac = smac[0]
            dst_mac = dmac[0]
        else:
            src_ip = ip2[0]
            dst_ip = ip2[1]
            src_mac = smac[1]
            dst_mac = dmac[1]

        pkt = Ether()
        pkt = pkt/IP(src=src_ip, dst=dst_ip)
        pkt = pkt/UDP(dport=1, sport=2)
        pad = max(0, size - len(pkt)) * 'x'
        pkt = pkt/pad

        mode = STLTXCont()
        rv = []
        for x in range(0, n_streams):
            vm = STLVM()
            vm.var(name="port",
                   min_value=0,
                   max_value=n_flows_per_stream,
                   size=2,
                   op="random")

            pkt = Ether()
            pkt = pkt/IP(src=src_ip, dst=dst_ip)

            if direction == 0:
                pkt = pkt/UDP(dport=x, sport=0)
                vm.write(fv_name="port", pkt_offset="UDP.sport")
            else:
                pkt = pkt/UDP(dport=0, sport=x)
                vm.write(fv_name="port", pkt_offset="UDP.sport")

            pad = max(0, size - len(pkt) - 4) * 'x'
            p = STLPktBuilder(pkt=pkt/pad, vm=vm)
            m = STLTXMultiBurst(pps=pps_per_stream,
                                pkts_per_burst=pkts_per_burst,
                                ibg=inter_burst_gap * 1e6,
                                count=1000000)
            rv.append(STLStream(isg=x*(1e6/streams_per_second),
                                packet=p,
                                mode=m))

        return rv


def register():
    return STLS1()
