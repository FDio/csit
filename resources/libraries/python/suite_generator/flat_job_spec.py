# Copyright (c) 2025 Cisco and/or its affiliates.
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

"""Generate an old fashioned flat MD file defining tests as a set of tags joint
together by logical AND.
"""


import logging

from itertools import product
from os import path

import constants as C


def generate_flat_spec(spec: dict, job: str, outputdir: str,
                       outputfile: str) -> int:
    """Generate an old fashioned flat MD file defining tests as a set of tags
    joint together by logical AND.
    """

    logging.info(f"Generating job specification for '{job}'...")

    job_spec = str()
    count = 0
    for itm in spec:
        l_params = list()
        for param in C.TEST_PARAMS:
            if param not in itm:
                logging.error(f"The parameter '{param}' is mandatory.")
                return 1
            if param == "infra":
                tmp_lst = list()
                for nic, drv_lst in itm[param].items():
                    for drv in drv_lst:
                        drv = f"drv_{drv}" if drv != "-" else "-"
                        tmp_lst.append(f"{nic} AND {drv}")
                l_params.append(tmp_lst)
            elif param == "core":
                l_params.append(
                    [f"{c}c" if c != "-" else "-" for c in itm[param]]
                )
            elif param == "framesize":
                l_params.append(
                    [f"{f}b" if isinstance(f, int) else f for f in itm[param]]
                )
            elif isinstance(itm[param], str):
                l_params.append([itm[param], ])
            else:
                l_params.append(itm[param])
        l_params.append(itm["tests"])
        for comb in product(*l_params):
            job_spec += " AND ".join(comb) + "\n"
            count += 1

    logging.info(f"Number of tests in the job specification: {count}")

    # Write the job spec as an md file:
    try:
        with open(path.join(outputdir, f"{outputfile}.md"), "wt") as fw:
            fw.write(job_spec)
    except IOError as err:
        logging.error(f"Cannot write the MD file.\n {err}")
        return 1

    return 0
