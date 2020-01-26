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

"""Module defining utilities for testcase autogeneration."""

from string import Template


class Testcase:
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

    def generate(self, num, frame_size, phy_cores, clients, streams,
                 bytes_str):
        """Return string of test case code with placeholders filled.

        Fail if there are placeholders left unfilled.
        It is not required for all placeholders to be present in template.

        :param num: Test case number. Example value: 4.
        :param frame_size: Imix string or numeric frame size. Example: 74.
        :param phy_cores: Number of physical cores to use. Example: 2.
        :param clients: Number of clients used by test program. Example: 4.
        :param streams: Number of streams used by test program. Example: 10.
        :param bytes_str: Size in bytes of stream sent by test program.
            Example: 1G
        :type num: int
        :type frame_size: str or int
        :type phy_cores: int or str
        :type clients: int
        :type streams: int
        :type bytes_str: str
        :returns: Filled template, usable as test case code.
        :rtype: str
        """
        try:
            fsize = int(frame_size)
            subst_dict = {
                u"frame_num": f"${{{fsize:d}}}",
                u"frame_str": f"{fsize:d}B"
            }
        except ValueError:  # Assuming an IMIX string.
            subst_dict = {
                u"frame_num": str(frame_size),
                u"frame_str": u"IMIX"
            }
        cores_str = str(phy_cores)
        cores_num = int(cores_str)
        subst_dict.update(
            {
                u"cores_num": f"${{{cores_num:d}}}",
                u"cores_str": phy_cores,
                u"tc_num": f"tc{num:02d}",
                u"clients_num": f"${{{clients:d}}}",
                u"clients_str": str(clients),
                u"streams_num": f"${{{streams:d}}}",
                u"streams_str": str(streams),
                u"bytes_str": bytes_str,
            }
        )
        return self.template.substitute(subst_dict)

    @classmethod
    def default(cls, suite_id):
        """Factory method for creating "default" testcase objects.

        Testcase name will contain both frame size and core count.
        Used for most performance tests, except TCP ones.

        :param suite_id: Part of suite name to distinguish from other suites.
        :type suite_id: str
        :returns: Instance for generating testcase text of this type.
        :rtype: Testcase
        """
        template_string = f'''
| ${{tc_num}}-${{frame_str}}-${{cores_str}}c-{suite_id}
| | [Tags] | ${{frame_str}} | ${{cores_str}}C
| | frame_size=${{frame_num}} | phy_cores=${{cores_num}}
'''
        return cls(template_string)

    @classmethod
    def tcp(cls, suite_id):
        """Factory method for creating "tcp" testcase objects.

        Testcase name will contain core count, but not frame size.

        :param suite_id: Part of suite name to distinguish from other suites.
        :type suite_id: str
        :returns: Instance for generating testcase text of this type.
        :rtype: Testcase
        """
        # TODO: Choose a better frame size identifier for streamed protocols
        # (TCP, QUIC, SCTP, ...) where DUT (not TG) decides frame size.
        if u"tcphttp" in suite_id:
            template_string = f'''
| ${{tc_num}}-IMIX-${{cores_str}}c-{suite_id}
| | [Tags] | ${{cores_str}}C
| | phy_cores=${{cores_num}}
'''
        elif u"iperf3" in suite_id:
            template_string = f'''
| ${{tc_num}}-9000B-${{cores_str}}c-{suite_id}
| | [Tags] | ${{cores_str}}C | ${{clients_str}}CLIENT | ${{streams_str}}STREAM
| | phy_cores=${{cores_num}} | clients=${{clients_num}}'''
            template_string += f" | streams=${{streams_num}}\n"
        else:
            template_string = f'''
| ${{tc_num}}-9000B-${{cores_str}}c-{suite_id}
| | [Tags] | ${{cores_str}}C | ${{clients_str}}CLIENT | ${{streams_str}}STREAM
| | phy_cores=${{cores_num}} | clients=${{clients_num}}'''
            template_string += f" | streams=${{streams_num}}" \
                               f" | bytes=${{bytes_str}}\n"
        return cls(template_string)
