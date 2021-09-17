# Copyright (c) 2021 Cisco and/or its affiliates.
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

from resources.libraries.python.Constants import Constants


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
        :type template_string: str
        """
        self.template = Template(template_string)

    def generate(self, frame_size, phy_cores=None):
        """Return string of test case code with placeholders filled.

        Fail if there are placeholders left unfilled.
        It is not required for all placeholders to be present in template.

        :param frame_size: Imix string or numeric frame size. Example: 74.
        :param phy_cores: Number of physical cores to use. Example: 2. It can
            be None in n2n testcases.
        :type frame_size: str or int
        :type phy_cores: int, str or None
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
        if phy_cores is None:
            return self.template.substitute(subst_dict)
        cores_str = str(phy_cores)
        cores_num = int(cores_str)
        subst_dict.update(
            {
                u"cores_num": f"${{{cores_num:d}}}",
                u"cores_str": phy_cores,
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
| ${{frame_str}}-${{cores_str}}c-{suite_id}
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
            if u"rps" in suite_id or u"cps" in suite_id:
                template_string = f'''
| ${{frame_str}}-${{cores_str}}c-{suite_id}
| | [Tags] | ${{frame_str}} | ${{cores_str}}C
| | frame_size=${{frame_num}} | phy_cores=${{cores_num}}
'''
            else:
                template_string = f'''
| IMIX-${{cores_str}}c-{suite_id}
| | [Tags] | ${{cores_str}}C
| | phy_cores=${{cores_num}}
'''
        else:
            template_string = f'''
| ${{frame_str}}-${{cores_str}}c-{suite_id[:-4]}-{suite_id[-3:]}
| | [Tags] | ${{cores_str}}C\n| | phy_cores=${{cores_num}}
'''
        return cls(template_string)

    @classmethod
    def iperf3(cls, suite_id):
        """Factory method for creating "iperf3" testcase objects.

        Testcase name will contain core count, but not frame size.

        :param suite_id: Part of suite name to distinguish from other suites.
        :type suite_id: str
        :returns: Instance for generating testcase text of this type.
        :rtype: Testcase
        """
        template_string = f'''
| 128KB-${{cores_str}}c-{suite_id}
| | [Tags] | 128KB | ${{cores_str}}C
| | frame_size=${{frame_num}} | phy_cores=${{cores_num}}
'''
        return cls(template_string)

    @classmethod
    def trex(cls, suite_id):
        """Factory method for creating "trex" testcase objects.

        Testcase name will contain frame size, but not core count.

        :param suite_id: Part of suite name to distinguish from other suites.
        :type suite_id: str
        :returns: Instance for generating testcase text of this type.
        :rtype: Testcase
        """
        template_string = f'''
| ${{frame_str}}--{suite_id}
| | [Tags] | ${{frame_str}}
| | frame_size=${{frame_num}}
'''
        return cls(template_string)

def add_testcases_to_file(testcase, suite_id, file_out, tc_kwargs_list):
    """Generate text according to kwargs and append it to a file.

    Here we add a bunch of last minute conditions on when to skip a testcase.
    When they get too complicated, add a more specialized suite subtype instead.

    :param testcase: Testcase instance to use for generating.
    :param suite_id: Suite ID.
    :param file_out: File to write testcases to, assumed open for writing.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type suite_id: str
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for kwargs in tc_kwargs_list:
        # TODO: Is there a better way to disable some combinations?
        emit = True
        if u"-16vm2t-" in suite_id or u"-16dcr2t-" in suite_id:
            if kwargs[u"phy_cores"] > 3:
                # CSIT lab only has 28 (physical) core processors,
                # so these test would fail when attempting to assign cores.
                emit = False
        if u"-24vm1t-" in suite_id or u"-24dcr1t-" in suite_id:
            if kwargs[u"phy_cores"] > 3:
                # CSIT lab only has 28 (physical) core processors,
                # so these test would fail when attempting to assign cores.
                emit = False
        if u"soak" in suite_id:
            # Soak test take too long, do not risk other than tc01.
            if kwargs[u"phy_cores"] != 1:
                emit = False
            if kwargs[u"frame_size"] not in Constants.MIN_FRAME_SIZE_VALUES:
                emit = False
        if kwargs[u"frame_size"] not in Constants.MIN_FRAME_SIZE_VALUES:
            if (
                u"-cps-" in suite_id
                or u"-pps-" in suite_id
                or u"-tput-" in suite_id
            ):
                emit = False
        if emit:
            file_out.write(testcase.generate(**kwargs))


def write_test_cases(state, file_out):
    """Based on edit state, generate testcase blocks and append them to file.

    This is where the protocol is detected
    and testcase instance and kwargs list is created.

    The file is assumed to be open for write with prolog already written there.

    :param state: Edited suite state.
    :param file_out: Text file open for writing, to append test cases to.
    :type state: EditState
    :type file_out: file
    """
    _, suite_id, _ = state.get_iface_and_suite_ids(state.filename)
    # TODO: Set min frame size directly, without mentioning protocol.
    protocol = u"ip4"
    if u"ethip6" in suite_id or u"ip6base" in suite_id:
        if u"ethip4" not in suite_id:
            # We may need more complicated logic if both IP4oIP6 and IP6oIP4
            # sncap/decap tests become common.
            protocol = u"ip6"
    if u"ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase" in suite_id:
        # We only want to match VTS tests. Vhost encapsulates
        # only on DUT-DUT link, and we do not touch scapy tests.
        protocol = u"ethip4vxlan"
    if u"dot1qip4vxlan" in suite_id:
        protocol = u"dot1qip4vxlan"
    tc_kwargs_list = state.subtype.value.kwargs_function(protocol)
    testcase = state.subtype.value.testcase_factory(suite_id)
    add_testcases_to_file(testcase, suite_id, file_out, tc_kwargs_list)
