# Copyright (c) 2022 Cisco and/or its affiliates.
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

import dataclasses
import logging
import math
import pandas as pd
import numpy as np

#from KeyboardMeasurer import KeyboardMeasurer as measurer
#from RandomMeasurer import RandomMeasurer as measurer
#from SingleLossMeasurer import SingleLossMeasurer as measurer
#from TwoPhaseMeasurer import TwoPhaseMeasurer as measurer
from StretchMeasurer import StretchMeasurer as measurer
from LoggingMeasurer import LoggingMeasurer as infologging
from TimeTrackingMeasurer import TimeTrackingMeasurer as tracking

#logging.basicConfig(filename='debug.log', level=getattr(logging, "DEBUG"))

# 0.75 is not a good value for twophase, but it found a bug, and it is good for singleloss.
p = tracking(measurer(offsets={31.0: 1e6}, mrr=1e8, spread=5e6))

from resources.libraries.python.MLRsearch import (
    MultipleLossRatioSearch as my_search, Config, Criteria, Criterion
)
crit = Criterion(
    loss_ratio=0.0,
    bad_ratio=0.0,
    trials_duration=100.0,
    intermediate_phases=3,
    relative_width=1e-3,
    expansion_coefficient=4,
)
ratios = (2/3, 3/4, 4/5, 5/6, 6/7, 7/8, 8/9, 9/10)
criteria = list(dataclasses.replace(crit, bad_ratio=ratio) for ratio in ratios)
config = Config()
config.min_rate = 1e4
config.max_rate = 1e9

def stat():
    """Print statistics from many runs of algorithm s."""
    # For Pandas magic, see https://stackoverflow.com/a/24913075
    numberOfRows = 1000000
    for index in range(10):
        criterion = criteria[index]
        print(f"\nFor criterion {criterion}")
        config.criteria = Criteria([criterion])
        # create dataframe
        df = pd.DataFrame(index=np.arange(0, numberOfRows), columns=('time', 'lo'))
        # now fill it up row by row
        algo = my_search(config)
        for x in np.arange(0, numberOfRows):
            result = algo.search(p)
            df.loc[x] = [
                p.total_time,
                math.log(float(list(result.values())[0].low_end)),
            ]
            p.reset()
        print(u"mean:")
        print(f"{df.mean()}")
        print(u"standard deviation:")
        print(f"{df.std()}")

print(u"optimized search, spectr crits, stretch measurer")
stat()
