# Traffic model

Traffic model is treated to be source of traffic data for Traffic Generator
(TG) to provide required traffic at the output of TG ports and possibly to be
source of data for configuration of (virtual) switch (e.g. VPP).

Traffic model will be stored in traffic_model.json file in directory
csit/docs/traffic_model/ and will contain following data:

- ports p0, p1, ... that can be mapped to NIC ports, switch (VPP) ports,

- streams per port s0, s1, ... that defines output streams for TG ports and
  inputs streams for switch (VPP) ports,

- layers per stream  l0, l1, ... in order from the most outer layer to
  the inner one; each layer contain the name of the layer (e.g. Ether, IP) with
  corresponding parameters needed for traffic generation or switch
  configuration,
  
  __note 1__: Scapy layer naming used here.
  
  __note 2__: Traffic flows will be defined by ranges of MAC addresses, IP
  addresses, UDP/TCP ports, etc. or by their combinations (depending on the
  test scenario).

- frame_size defining the default frame size in B,

- direction or destination_ port p0, p1, ... ???
  could be used for configuration of the switch (VPP)

Traffic model file will be created on the fly per test suite in suite setup
based on test suite variables.

## trafic_model.json example

__note__: Move this example to separate traffic_model_example.json file?

```
{
    "p0": {
        "s0": {
            "l0": "Ether": {
                "dst_mac": "00:01:02:03:04:05",
                "dst_mac_count": 1,
                "src_mac": "0f:01:02:03:04:05",
                "src_mac_count": 1,
            },
            "l1": "IP":{
                "src_ip": "10.0.0.1",
                "src_ip_count": 255,
                "dst_ip": "20.0.0.1",
                "dst_ip_count": 1,
            },
            "l2": "Raw":{},  # load created on the fly for required frame size
        },
    },
    "p1": {
        "s0": {
            "l0": "Ether": {  # outer Ether
                "dst_mac": "00:01:02:03:04:05",
                "dst_mac_count": 1,
                "src_mac": "0f:01:02:03:04:05",
                "src_mac_count": 1,
            },
            "l1": "IP":{  # outer IP
                "src_ip": "1.1.1.2",
                "src_ip_count": 1,
                "dst_ip": "1.1.1.1",
                "dst_ip_count": 1,
            },
            "l2": "UDP":{  # sport calculated, not defined here
                "dport": 6081,
                "dport_count": 1,
            },
            "l3": "GENEVE":{
                "vni": 1,
                "vni_count": 4,
            },
            "l4": "Ether": {  # inner Ether
                "dst_mac": "ee:01:02:03:04:05",
                "dst_mac_count": 1,
                "src_mac": "ef:01:02:03:04:01",
                "src_mac_count": 4,
            },
            "l5": "IP":{  # inner IP
                "src_ip": "10.0.1.0",
                "src_ip_count": 1024,
                "dst_ip": "10.128.1.0",
                "dst_ip_count": 1024,
            },
            "l6": "Raw":{},  # load created on the fly for required frame size
        },
    },
}
```
