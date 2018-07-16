# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Module defining utilities for testcase autogeneration."""

from string import Template


class Testcase(object):
    """Class containing a template string and a substitution method."""

    def __init__(self, template_string):
        """Construct instance by storing template given by string.

        :param template_string: Template string to generate test case code with.
            See string.Template documentation for template string syntax.
            Only the following placeholders are supported:
            - cores_num - Number of cores as robot number, example: "${2}".
            - cores_str - Number of physical cores to use, example: "2".
            - frame_num - Framesize as a number, example: "${74}".
            - frame_str - Framesize in upper case, example: "74B".
            - tc_num - Start of testcase name, example: "tc04".
        :type template_string: str
        """
        self.template = Template(template_string)

    def generate(self, num, framesize, phy_cores):
        """Return string of test case code with placeholders filled.

        Fail if there are placeholders left unfilled.

        :param num: Test case number. Example value: 4.
        :param framesize: Imix string or numeric frame size. Example: 74.
        :param phy_cores: Number of physical cores to use. Example: 2.
        :type num: int
        :type framesize: str or int
        :type phy_cores: int or str
        :returns: Filled template, usable as test case code.
        :rtype: str
        """
        try:
            fs = int(framesize)
            subst_dict = {
                "frame_num": "${{{fs:d}}}".format(fs=fs),
                "frame_str": "{fs:d}B".format(fs=fs)
            }
        except ValueError:  # Assuming IMIX string.
            subst_dict = {
                "frame_num": "{fs}".format(fs=str(framesize)),
                "frame_str": "IMIX"
            }
        cores_str = str(phy_cores)
        cores_num = int(cores_str)
        subst_dict.update(
            {
                "cores_num": "${{{cores:d}}}".format(cores=cores_num),
                "cores_str": phy_cores,
                "tc_num": "tc{num:02d}".format(num=num)
            })
        return self.template.substitute(subst_dict)
