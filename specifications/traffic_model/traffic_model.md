# Traffic model

Traffic model is treated to be source of traffic specification for Traffic
Generator (TG) to provide required traffic at the output of TG ports and
possibly to be source of data for configuration of (virtual) switch (e.g. VPP).

Traffic model will be stored in traffic_model.json file in directory
csit/specifications/traffic_model/ and will contain following data:

- ports p0, p1, ... that can be mapped to NIC ports, switch (VPP) ports,

- streams per port s0, s1, ... that defines output streams for TG ports and
  inputs streams for switch (VPP) ports,

- stream_type per stream defines the purpose of the stream; default value is
  "standard", for special latency streams use value "latency",

  __Note 1__: Latency streams mostly use the same template packets as standard
  traffic streams. If different template packet definition for the latency
  stream is required just add another stream specification (e.g. stream s1 if
  there is only one standard traffic stream defined) and set the stream_type to
  "latency" and instruct TG to use this stream for latency stream.

- frame_size per stream defining the default frame size in bytes (e.g. 64B) or
  as a string (e.g. IMIX_v2); default value can be changed on the test case
  level when passing traffic data to TG,

- destination_port per stream p0, p1, ... defines to which port the traffic
  should be forwarded,

  __todo__: Use this parameter? Could be used for the configuration / check of
  the configuration of the switch (VPP).

- weight per stream that can be used to set different rate for streams per
  port; 1 can be used as a default value,

- isg per stream that defines inter-stream gap in microseconds,

- layers per stream l0, l1, ... in order from the most outer layer to
  the inner one,

- layer_name of the layer (e.g. Ether, IP),

  __Note 2__: Scapy layer naming used here.

- layer_params that contain layer parameters needed for the traffic generation
  or switchconfiguration.

  __Note 3__: Traffic flows are be defined by ranges of MAC addresses, IP
  addresses, UDP/TCP ports, etc. or by their combinations (depending on the
  test scenario).

  __Note 4__: The decision if values in ranges are updated incrementally or
  randomly is defined on the test suite level when passing traffic data to TG.

Traffic model file will be created on the fly per test suite in suite setup
based on test suite variables.

  __todo__: Possibly too complicated parameter names would be required in
  the test suit to create traffic_modle.json file on the fly. Use separate
  traffic_model_xxx.json per test suite?

## traffic_model.json example

__todo__: Move this example to separate traffic_model_example.json file?

```
[
    {
        "port_id": "p0",
        "streams": [
            {
                "stream_id"; "s0",
                "stream_type": "standard",
                "frame_size": 64B,
                "destination_port": "p1",
                "weight": 1,
                "isg": 10.0,
                "layers": [
                    {
                        "layer_id": "l0",
                        "layer_name": Ether",
                        "layer_params": {
                            "dst_mac": "00:01:02:03:04:05",
                            "dst_mac_count": 1,
                            "src_mac": "0f:01:02:03:04:05",
                            "src_mac_count": 1,
                        },
                    },
                    {
                        "layer_id": "l1",
                        "layer_name": "IP",
                        "layer_params": {
                            "src_ip": "10.0.0.1",
                            "src_ip_count": 255,
                            "dst_ip": "20.0.0.1",
                            "dst_ip_count": 1,
                        },
                    },
                    {
                        "layer_id": "l2",
                        "layer_name": "Raw",
                        # load created on the fly for required frame size
                        "layer_params": {},
                    },
                ]
            },
        ],
    },
    {
        "port_id": "p1",
        "streams": [
            {    
                "stream_id"; "s0",
                "stream_type": "standard",
                "frame_size": 64B,
                "destination_port": "p0",
                "weight": 1,
                "isg": 10.0,
                "layers": [
                    {
                        "layer_id": "l0",
                        "layer_name": "Ether",  # outer Ether
                        "layer_params": {
                            "dst_mac": "00:01:02:03:04:05",
                            "dst_mac_count": 1,
                            "src_mac": "0f:01:02:03:04:05",
                            "src_mac_count": 1,
                        },
                    },
                    {
                        "layer_id": "l1",
                        "layer_name": "IP",  # outer IP
                        "layer_params": {
                            "src_ip": "1.1.1.2",
                            "src_ip_count": 1,
                            "dst_ip": "1.1.1.1",
                            "dst_ip_count": 1,
                        },
                    },
                    {
                        "layer_id": "l2",
                        "layer_name": "UDP",
                        "layer_params": {
                            # sport calculated, not defined here
                            "dport": 6081,
                            "dport_count": 1,
                        },
                    },
                    {
                        "layer_id": "l3",
                        "layer_name": "GENEVE",
                        "layer_params": {
                            "vni": 1,
                            "vni_count": 4,
                        },
                    },
                    {
                        "layer_id": "l4",
                        "layer_name": "Ether",  # inner Ether
                        "layer_params": {
                            "dst_mac": "ee:01:02:03:04:05",
                            "dst_mac_count": 1,
                            "src_mac": "ef:01:02:03:04:01",
                            "src_mac_count": 4,
                        },
                    },
                    {
                        "layer_id": "l5",
                        "layer_name": "IP",  # inner IP
                        "layer_params": {
                            "src_ip": "10.0.1.0",
                            "src_ip_count": 1024,
                            "dst_ip": "10.128.1.0",
                            "dst_ip_count": 1024,
                        },
                    },
                    {
                        "layer_id": "l6",
                        "layer_name": "Raw",
                        # load created on the fly for required frame size
                        "layer_params": {},  
                    },
                ]
            },
        ]
    },
]
```
