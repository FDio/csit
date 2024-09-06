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
You are a computer scientist, collaborating with the user.
The current content of IETF draft document is:
```markdown
${draft}
```
''',
    },
    {
        'role': 'user',
        'content': '''
Currently, I believe the early chapters are stable enough.
I am now focusing on chapters `Additional Considerations`
and `Logic of Load Classification`.
I think larger edits are needed there, maybe removing larger areas
and perhaps adding more areas there, or at least increasing or decreasing verbosity.
For that, I fist need to get a high-level familiarity with what is currently there,
regardless of the surrect subsection structure.

How would you summarize the content there into a bullet list?
''',
    },
    {
        'role': 'assistant',
        'content': '''
Certainly! Here is a summarized bullet list of the content in the `Additional Considerations` and `Logic of Load Classification` chapters:

### Additional Considerations

- **Stopping Conditions**
  - MLRsearch introduces the concept of Goal Width to determine the precision of the result and when to stop the search.
  - The search stops when the distance between the tightest upper bound and the tightest lower bound is smaller than the Goal Width.
  - MLRsearch implementations can use different stopping conditions.

- **Load Classification**
  - MLRsearch keeps the basic logic of binary search but may need more than one trial to classify a load.
  - The classification logic is explained in the next section.
  - For repeatability and comparability, given a set of trial results, all implementations of MLRsearch should classify the load equivalently.

- **Loss Ratios**
  - MLRsearch can search for multiple goals differing in their loss ratios.
  - Different goals may have different loss ratios and Goal Widths.
  - A load can be classified as an upper bound for some goals and a lower bound for others.
  - Loss inversion is a phenomenon where a load classified as an upper bound for one goal may be a lower bound for another.

- **Loss Inversion**
  - MLRsearch is conservative in handling loss inversion.
  - The upper bound is considered real, and lossless trials at higher loads are considered coincidental.
  - Relevant Upper Bound and Relevant Lower Bound are defined to handle loss inversion.

- **Exceed Ratio**
  - The exceed ratio controls the frequency of high-loss trials that can be ignored.
  - A recommended value for the exceed ratio is 0.5 for explainability.

- **Duration Sum**
  - The duration sum controls the number of trials needed for load classification.
  - The duration sum has a big impact on the overall search duration.

- **Short Trials**
  - Short trials are trials with intended durations shorter than the goal final trial duration.
  - MLRsearch allows the use of short trials to save time.
  - Short trials can cause loss inversion and lower the Relevant Lower Bound.

- **Throughput**
  - Throughput is generalized for loads with multiple trial results and non-zero loss ratios.
  - Conditional Throughput is defined as the trial forwarding rate from one of the trials performed at the load in question.
  - Conditional Throughput is partially related to load classification.
  - It is recommended to set the Goal Width to a value no smaller than the Goal Loss Ratio.

- **Search Time**
  - The art of achieving short search times is in the smart selection of intended loads and durations for the next trial.
  - Implementations prioritizing minimizing search time are unlikely to suffer from bias.
  - The definition of the Relevant Lower Bound is strict enough to ensure result repeatability and comparability.

- **RFC2544 Compliance**
  - Some Search Goal instances lead to results compliant with RFC2544.
  - The presence of other Search Goals does not affect the compliance of this Goal Result.

### Logic of Load Classification

- **Introductory Remarks**
  - This chapter explains load classification and Conditional Throughput.
  - Definitions are wordy, and implementers should read the MLRsearch Specification section and Appendices for more concise definitions.

- **Performance Spectrum**
  - The performance spectrum is a function that maps trial forwarding rates to sums of trial durations.
  - The performance probability function is the performance spectrum divided by the sum of durations of all trials.
  - Conditional Throughput is a quantile value for a specifically chosen set of trials.

- **Trials with Single Duration**
  - When all trials have the same duration, load classification is simpler.
  - The load is classified based on the sums of durations of good and bad trials.
  - The Conditional Throughput is the smallest trial forwarding rate among the trials if the Goal Exceed Ratio is 0.

- **Trials with Short Duration**
  - Short trials are trials with durations shorter than the goal final trial duration.
  - The classification logic for short trials is based on three scenarios: False Good, True Bad, and Balanced.
  - The bad sum is defined differently for short trials.

- **Trials with Longer Duration**
  - Trials with durations longer than the goal final trial duration are treated the same as trials with durations equal to the goal final trial duration.
  - Bad trials with longer durations may bias the search towards lower load values.

### Appendix A: Load Classification

- **Pseudocode for Load Classification**
  - The pseudocode computes two values, `optimistic` and `pessimistic`, which determine the load classification.
  - The pseudocode is valid Python code and expects specific input variables.

### Appendix B: Conditional Throughput

- **Pseudocode for Conditional Throughput**
  - The pseudocode computes the Conditional Throughput based on the trial results.
  - The pseudocode is valid Python code and expects specific input variables.

This bullet list summarizes the key points and concepts discussed in the `Additional Considerations` and `Logic of Load Classification` chapters.
''',
    },
    {
        'role': 'user',
        'content': '''
Pick one item you think describes part of the document (say one subsection)
that is currently written too verbosely,
and suggest a way to rewrite that part of the document.
''',
    },
    {
        'role': 'assistant',
        'content': '''
Certainly! Let's focus on the subsection "Stopping Conditions" under the "Additional Considerations" chapter. Here is the original text:

---

## Stopping Conditions

[RFC2544] prescribes that after performing one trial at a specific offered load, the next offered load should be larger or smaller, based on frame loss.

The usual implementation uses binary search. Here a lossy trial becomes a new upper bound, a lossless trial becomes a new lower bound. The span of values between the tightest lower bound and the tightest upper bound (including both values) forms an interval of possible results, and after each trial the width of that interval halves.

Usually the binary search implementation tracks only the two tightest bounds, simply calling them bounds. But the old values still remain valid bounds, just not as tight as the new ones.

After some number of trials, the tightest lower bound becomes the throughput. [RFC2544] does not specify when, if ever, should the search stop.

MLRsearch introduces a concept of [Goal Width] (#Goal-Width). The search stops when the distance between the tightest upper bound and the tightest lower bound is smaller than a user-configured value, called Goal Width from now on. In other words, the interval width at the end of the search has to be no larger than the Goal Width.

This Goal Width value therefore determines the precision of the result. Due to the fact that MLRsearch specification requires a particular structure of the result (see [Trial Result] (#Trial-Result) section), the result itself does contain enough information to determine its precision, thus it is not required to report the Goal Width value.

This allows MLRsearch implementations to use stopping conditions different from Goal Width.

---

Here is a more concise version of the same subsection:

---

## Stopping Conditions

[RFC2544] prescribes that after performing one trial at a specific offered load, the next offered load should be larger or smaller, based on frame loss.

The usual implementation uses binary search. Here, a lossy trial becomes a new upper bound, and a lossless trial becomes a new lower bound. The span of values between the tightest lower bound and the tightest upper bound forms an interval of possible results, which halves after each trial.

Typically, the binary search implementation tracks only the two tightest bounds, but older values remain valid bounds, just not as tight as the new ones.

After some number of trials, the tightest lower bound becomes the throughput. [RFC2544] does not specify when, if ever, the search should stop.

MLRsearch introduces the concept of [Goal Width] (#Goal-Width). The search stops when the distance between the tightest upper bound and the tightest lower bound is smaller than a user-configured value, called Goal Width. In other words, the interval width at the end of the search must be no larger than the Goal Width.

This Goal Width value determines the precision of the result. Since MLRsearch specification requires a particular structure of the result (see [Trial Result] (#Trial-Result) section), the result itself contains enough information to determine its precision, making it unnecessary to report the Goal Width value.

This allows MLRsearch implementations to use stopping conditions different from Goal Width.

---

This revised version maintains the essential information while reducing verbosity and improving clarity.
''',
    },
]
