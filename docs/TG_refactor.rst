..
   Copyright (c) 2019 Cisco and/or its affiliates.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at:
..
       http://www.apache.org/licenses/LICENSE-2.0
..
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Introduction
^^^^^^^^^^^^

We have few Jira tasks for improving TrafficGenerator.py,
but it is not clear how the end result should look like,
and how to get there.

When this dosument is reviewed, new Jira tasks should be created,
subtasks for each planned step.

Current issues
^^^^^^^^^^^^^^

1. We do not have hardware traffic generators to test with.
   This limits our imagination on what the capabilities and restrictions
   of managing them from TrafficGenerator.py would be.

2. We have software traffic generators with incompatible APIs.
   Our current way of using TRex is not suitable for TCP tests.
   Similarly, WRK is not suitable for raw traffic tests.
   Typical difference: TRex needs frame_size, you cannot set it for WRK.

3. Software traffic generators are not bound to a specific node.
   Currently, both TRex and WRK are started on subtype TREX nodes.

4. Traffic profiles. Are Ixia or Spirent able to use our current
   definitions (based on trex.stl.api) for traffic profiles?

5. Latency. Even for TRex, we are switching form the old way to HDRhistogram.
   Other traffic generators are expected to have even more different output.

Plan of changes
^^^^^^^^^^^^^^^

1. Step one: Code cleanup.
   Remove unused APIs (DropRateSearch), keep used APIs the same.
   Do not change the internal structure of TrafficGenerator much.

2. Step two: Modularize.
   The used APIs can be changed/simplified/unified if it simplifies the code.
   Create a TRex "driver" class to hide implementation details.
   Keep the old logic (TG driver chosen by subtype, WRK logic separate,
   just tearing down TRex on setup).

3. Step three: Topology improvements.
   Add useful abstractions to topology.py in order to simplify
   some arguments (mainly for TRex init). Still keep the old logic.

4. Step four: CSIT-1618.
   Abolish DUT-side traffic scripts. Use robot-side TRex client object instead.

5. Step five: Abstract away different rate quantities.
   Create a class to facilitate conversions between different ways to quantify
   traffic rate. Pps vs bps vs percentage of line rate. Aggregate vs
   per-traffic-direction.

6. Step six: Centralize rate limits.
   Move existing code of applying different bps and pps limits to the rate class.
   Make sure the packets of latency flows are included in pps calculations.

7. Step seven: Design the new TG subtype logic.
   Add more steps according to the final design.
