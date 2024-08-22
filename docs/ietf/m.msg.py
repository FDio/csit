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
```
${draft}
```
''',
    },
    {
        'role': 'user',
        'content': '''
The current definition of load classification using code is exact,
but not very intuitive. Can you write an explanation that does not need the code?
Use such formatting to allow pasting your explanation somewhere into the draft.
Avoid lists and math formulas.
''',
    },
    {
        'role': 'assistant',
        'content': '''
Certainly! Here is an explanation of load classification without relying on code:

---

### Load Classification

Load classification in MLRsearch determines whether a specific load is considered a lower bound, an upper bound, or remains undecided based on the trial results and the specified search goals. This process involves evaluating the trial results against the goal's parameters, such as the Goal Loss Ratio, Goal Exceed Ratio, and Goal Duration Sum.

#### Key Concepts

- **Good Trials**: Trials with a Trial Loss Ratio not exceeding the Goal Loss Ratio.
- **Bad Trials**: Trials with a Trial Loss Ratio higher than the Goal Loss Ratio.
- **Full-Length Trials**: Trials with a duration equal to or longer than the Goal Final Trial Duration.
- **Short Trials**: Trials with a duration shorter than the Goal Final Trial Duration.

#### Classification Logic

1. **Sum of Durations**:
   - Calculate the sum of durations for good full-length trials (`good_long_sum`).
   - Calculate the sum of durations for bad full-length trials (`bad_long_sum`).
   - Calculate the sum of durations for good short trials (`good_short_sum`).
   - Calculate the sum of durations for bad short trials (`bad_short_sum`).

2. **Balancing Sum**:
   - Compute the balancing sum as the product of the `good_short_sum` and the Goal Exceed Ratio divided by one minus the Goal Exceed Ratio.

3. **Effective Bad Sum**:
   - Compute the effective bad sum by adding the `bad_long_sum` to the maximum of zero and the difference between the `bad_short_sum` and the balancing sum.

4. **Effective Whole Sum**:
   - Compute the effective whole sum as the maximum of the sum of `good_long_sum` and the effective bad sum, and the Goal Duration Sum.

5. **Quantile Duration Sum**:
   - Compute the quantile duration sum as the product of the effective whole sum and the Goal Exceed Ratio.

6. **Classification**:
   - If the effective bad sum is less than or equal to the quantile duration sum, the load is classified as a lower bound.
   - If the difference between the effective whole sum and the `good_long_sum` is less than or equal to the quantile duration sum, the load is classified as an upper bound.
   - Otherwise, the load remains undecided.

#### Explanation

The classification logic ensures that the load is considered a lower bound only if the proportion of bad trials (both full-length and short) does not exceed the Goal Exceed Ratio. Conversely, the load is considered an upper bound if the proportion of good trials (both full-length and short) does not exceed the Goal Exceed Ratio. This approach balances the impact of short trials, ensuring that they do not unduly influence the classification while still providing useful information.

By using this classification logic, MLRsearch aims to achieve a more accurate and repeatable determination of the throughput, taking into account the variability and noise inherent in software-based networking systems.

---

This explanation should provide a clear understanding of the load classification process without relying on code.
''',
    },
]
