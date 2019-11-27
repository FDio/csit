# Copyright (c) 2019 Cisco and/or its affiliates.
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
__init__ file for directory presentation

This makes the presentation a part of the great CSIT resources package.
"""

from .pal_errors import PresentationError
from .pal_utils import archive_input_data, classify_anomalies, \
    convert_csv_to_pretty_txt, execute_command, get_files, \
    get_last_completed_build_number, get_last_successful_build_nr, \
    get_rst_title_char, mean, relative_change, relative_change_stdev, stdev
from .environment import Environment
from .specification_parser import Specification
from .input_data_parser import InputData
from .generator_tables import generate_tables
from .generator_plots import generate_plots
from .generator_files import generate_files
from .static_content import prepare_static_content
from .generator_report import generate_report
from .generator_cpta import generate_cpta
from .generator_alerts import Alerting
