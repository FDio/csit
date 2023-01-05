# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""Debug class. Only for internal debugging puproses.
"""

import logging

from data.data import Data
from utils.constants import Constants as C


logging.basicConfig(
    format=u"%(asctime)s: %(levelname)s: %(message)s",
    datefmt=u"%Y/%m/%d %H:%M:%S",
    level=logging.INFO
)

# Set the time period for data fetch
if C.TIME_PERIOD is None or C.TIME_PERIOD > C.MAX_TIME_PERIOD:
    time_period = C.MAX_TIME_PERIOD
else:
    time_period = C.TIME_PERIOD

#data_mrr = Data(
#    data_spec_file=C.DATA_SPEC_FILE,
#    debug=True
#).read_trending_mrr(days=time_period)
#
#data_ndrpdr = Data(
#    data_spec_file=C.DATA_SPEC_FILE,
#    debug=True
#).read_trending_ndrpdr(days=time_period)

data_list = Data(
    data_spec_file=C.DATA_SPEC_FILE,
    debug=True
).check_datasets(days=time_period)