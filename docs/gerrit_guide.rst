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


Git
^^^

TODO: Talk about "git clone", "git checkout -b mybranch -t master",
"git pull -r" (twice), chaining changes, "git review -Ry" and similar stuff.

Gerrit
^^^^^^

Debugging
---------

TODO: Talk about "recheck" and various "csit-2n-skx-perftest" options.

When you see "fd.io JJB" adding "Patch Set 4: Verified-1" comment,
it means at least one of the verify jobs (started for patch set 4) failed.
Click that comment and you see list of job runs, results and links.

You can ignore "FAILURE (skipped)" result, as it comes from jobs
without voting power (probably new and not stable enough to be reliable).

To examine a failed (voting) job, you can click directly at link to logs.
(e.g. https://logs.fd.io/production/vex-yul-rot-jenkins-1/csit-vpp-device-master-ubuntu1804-1n-skx/2843 )
From there console-timestamp.log.gz can be informative,
but more details are visible from archives/console-timestamp.log.gz
which opens log.html file with Robot results.
Paths to failed keywords are expanded by default, so just follow red nodes
until you see what it was.
Sometimes it comes from unrelated unstable test,
sometimes it comes from a bad thing not detected earlier in test case execution,
so more general guidelines are hard to write without explicit examples.

TODO: Talk about failures before robot is even run.

TODO: Do we have a document on using Sandbox?
