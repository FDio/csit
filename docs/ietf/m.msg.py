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

messages = [
    {
        'role': 'system',
        'content': '''
You are a computer scientist, collaborating with the user,
wrapping your responses to line length of 80 (or fewer) characters.

The current content of IETF draft document is:
```markdown
${draft}
```
''',
    },
    {
        'role': 'user',
        'content': '''
I am now focusing on `Loss Ratios and Loss Inversion` section.
Can you rewrite it to address the TODOs?
''',
    },
    {
        'role': 'assistant',
        'content': '''
Certainly! Here is the revised `Loss Ratios and Loss Inversion` section, addressing the TODOs:

---

## Loss Ratios and Loss Inversion

Another difference between MLRsearch and [RFC2544] binary search is in the goals of the search. [RFC2544] has a single goal, based on classifying full-length trials as either lossless or lossy.

MLRsearch, as the name suggests, can search for multiple goals, differing in their loss ratios. The precise definition of the Goal Loss Ratio will be given later. The [RFC2544] throughput goal then simply becomes a zero Goal Loss Ratio. Different goals also may have different Goal Widths.

A set of trial results for one specific intended load value can classify the load as an upper bound for some goals, but a lower bound for some other goals, and undecided for the rest of the goals.

Therefore, the load classification depends not only on trial results but also on the goal. The overall search procedure becomes more complicated, when compared to binary search with a single goal, but most of the complications do not affect the final result, except for one phenomenon, loss inversion.

In [RFC2544] throughput search using bisection, any load with a lossy trial becomes a hard upper bound, meaning every subsequent trial has a smaller intended load.

But in MLRsearch, a load that is classified as an upper bound for one goal may still be a lower bound for another goal, and due to the other goal, MLRsearch will probably perform trials at even higher loads. What to do when all such higher load trials happen to have zero loss? Does it mean the earlier upper bound was not real? Does it mean the later lossless trials are not considered a lower bound? Surely we do not want to have an upper bound at a load smaller than a lower bound.

MLRsearch is conservative in these situations. The upper bound is considered real, and the lossless trials at higher loads are considered to be a coincidence, at least when computing the final result.

This is formalized using new notions, the [Relevant Upper Bound](#Relevant-Upper-Bound) and the [Relevant Lower Bound](#Relevant-Lower-Bound). Load classification is still based just on the set of trial results at a given intended load (trials at other loads are ignored), making it possible to have a lower load classified as an upper bound, and a higher load classified as a lower bound (for the same goal). The Relevant Upper Bound (for a goal) is the smallest load classified as an upper bound. But the Relevant Lower Bound is not simply the largest among lower bounds. It is the largest load among loads that are lower bounds while also being smaller than the Relevant Upper Bound.

With these definitions, the Relevant Lower Bound is always smaller than the Relevant Upper Bound (if both exist), and the two relevant bounds are used analogously as the two tightest bounds in the binary search. When they are less than the Goal Width apart, the relevant bounds are used in the output.

One consequence is that every trial result can have an impact on the search result. That means if your SUT (or your traffic generator) needs a warmup, be sure to warm it up before starting the search.

---

This revised section addresses the TODOs by clarifying the concepts and ensuring that the text is clear and concise.
''',
    },
]
