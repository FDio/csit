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

"""Constants used in telemetry.

"Constant" means a value that keeps its value since initialization. The value
does not need to be hard coded here, but can be read from environment variables.
"""

class Constants:
    """Constants used in telemetry.
    1-10: Telemetry errors
    11-50: VPP bundle error
    51-100: Linux bundle errors"""

    # Failed when processing data
    err_telemetry_process = 1

    # Failed to read YAML file
    err_telemetry_yaml = 2

    # Error executing bundle
    err_telemetry_bundle = 3

    # Could not connect to VPP
    err_vpp_connect = 11

    # Could not disconnect from VPP
    err_vpp_disconnect = 12

    # Failed when executing command
    err_vpp_execute = 13

    # Could not attach BPF events
    err_linux_attach = 51

    # Could not detach BPF events
    err_linux_detach = 52
