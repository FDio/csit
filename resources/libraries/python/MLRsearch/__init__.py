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

"""
__init__ file for Python package "MLRsearch".
"""

# TODO: Move submodules to separate modules.
# Not obvious how to do that from PyPI point of view
# without affecting the current CSIT global "resources" package root.
# Probably it can be done by specifying multiple directories
# in PYTHONPATH used throughout CSIT.

# Import user-facing (API) stuff, so useds do not need to know submodules.
from .config import Config
from .criteria import Criteria
from .criterion import Criterion
from .multiple_loss_ratio_search import MultipleLossRatioSearch
