# Copyright (c) 2020 Cisco and/or its affiliates.
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

# TODO: Add docstrings with explanations.

from math import sqrt


class Color:

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        rr = (r + 0.5) / 256
        gg = (g + 0.5) / 256
        bb = (b + 0.5) / 256
        self.rr = rr
        self.gg = gg
        self.bb = bb
        br2 = 0.5 * gg * gg + 0.3 * rr * rr + 0.2 * bb * bb
        br = sqrt(br2)
        self.br2 = br2
        rg = rr - gg
        o = rr + gg - 2 * bb
        nrg = rg / br
        no = o / br
        self.nrg = nrg
        self.no = no

    def invdist2(self, c):
        w_nrg = 0.5  # Less means more repulsion.
        w_no = 1.0
        dist2 = w_nrg * (self.nrg - c.nrg) * (self.nrg - c.nrg)
        dist2 += w_no * (self.no - c.no) * (self.no - c.no)
        return 9e4 if not dist2 else 1.0 / dist2


def main():
    n_col = 7
    max_br2 = 0.25
    w_br2 = 1e1
    colors = list()
    for count in range(n_col):
        target_br2 = count / (n_col - 1) * max_br2
        print(f"target br2 {target_br2}")
        record = -9e4
        for g in range(256):
            for r in range(256):
                for b in range(256):
                    c = Color(r, g, b)
                    if g and c.br2 < 0.9 * target_br2:
                        continue
                    score = -w_br2 * (c.br2 - target_br2) * (c.br2 - target_br2)
                    for col in colors:
                        score -= c.invdist2(col)
                    if score > record:
                        record = score
                        cr = c
                    if c.br2 > 1.1 * target_br2:
                        break
        print(f"#{cr.r:02x}{cr.g:02x}{cr.b:02x} rb2 {cr.br2} score {record}")
        colors.append(cr)


if __name__ == u"__main__":
    main()
