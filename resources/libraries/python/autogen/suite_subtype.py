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

"""Module for detecting suite subtypes.

The term "test type" usually refers to mrr/ndrpdr/soak split.

Most logic that depends on suite subtype (testcase template, kargs)
is elsewhere, here is just the enum and the classifier.

The test subtype is classified before autogeneration,
so for example "soak" is not a subtype, as it is generated from "ndrpdr".

The effect of protocol is not detected and applied here,
so kwargs are prepared only as functions.
"""

from collections import namedtuple
from enum import Enum

import resources.libraries.python.autogen.kwargs as kwargs
from resources.libraries.python.autogen.test_case import Testcase

fields = [
    # TODO: Add a "comment" field when we have good enough descriptions.
    u"testcase_factory",  # Factory creating Testcase instances from suite ID.
    u"kwargs_function",  # Function from protocol to kwargs, see kwargs module.
    u"test_type_split",  # Boolean, telling whether to split to mrr/ndrpdr/soak.
    u"nic_model_split",  # Boolean, telling whether to split on NIC models.
    u"nic_driver_split",  # Boolean, telling whether to split on NIC driver.
]
SuiteSubtypeTuple = namedtuple(u"SuiteSubtypeTuple", fields)

class SuiteSubtype(Enum):
    """Recognized test subtypes.

    TODO: Unify the symbolic names. Is _PERF useful?
    """
    # Candidates for future "comment" values added as comments.
    STATELESS_PERF = SuiteSubtypeTuple(
        # Most performance tests, splitting to MRR, NDRPDR and SOAK.
        testcase_factory=Testcase.default,
        kwargs_function=kwargs.default_kwargs,
        test_type_split=True,
        nic_model_split=True,
        nic_driver_split=True,
    )
    # Add a subtype for ASTF perf tests (instead of adding exclusions later),
    # or make them fully compatible with the default perf subtype
    # (by setting MSS according to frame_size).
    # CPS tests may never be compatible, as they do not hit MSS.
    SCHEDULER_PERF = SuiteSubtypeTuple(
        # Still stateless perf, but with at least 2 physical cores.
        testcase_factory=Testcase.default,
        kwargs_function=kwargs.dp1_kwargs,
        test_type_split=True,
        nic_model_split=True,
        nic_driver_split=True,
    )
    RECONF_PERF = SuiteSubtypeTuple(
        # Separate perf type, not related to mrr/ndrpdr/soak.
        testcase_factory=Testcase.default,
        kwargs_function=kwargs.default_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=True,
    )
    TREX_PERF = SuiteSubtypeTuple(
        # A TG perf type without any DUTs, NIC drive split not supported yet.
        testcase_factory=Testcase.trex,
        kwargs_function=kwargs.trex_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=False,
    )
    HTTP_PERF = SuiteSubtypeTuple(
        # One type of TCP tests, special kwargs without frame size.
        testcase_factory=Testcase.tcp,
        kwargs_function=kwargs.http_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=False,
        # TODO: Fix issues which currently prevent nic driver split.
    )
    HOSTSTACK_BPS = SuiteSubtypeTuple(
        # Another type of TCP tests, different kwargs.
        testcase_factory=Testcase.tcp,
        kwargs_function=kwargs.hs_bps_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=False,
        # TODO: Fix issues which currently prevent nic driver split.
    )
    HOSTSTACK_QUIC_PERF = SuiteSubtypeTuple(
        # Yet another TCP test type, yet another kwargs.
        testcase_factory=Testcase.tcp,
        kwargs_function=kwargs.hs_quic_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=False,
        # TODO: Fix issues which currently prevent nic driver split.
    )
    IPERF3_MRR = SuiteSubtypeTuple(
        # TCP test which is not quite identical to MRR yet.
        testcase_factory=Testcase.iperf3,
        kwargs_function=kwargs.iperf3_kwargs,
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=False,
        # TODO: Did we even attempt to support different NIC drivers?
    )
    SCAPY_FUNC = SuiteSubtypeTuple(
        # Functional "device" tests. Not splittable from stateless_perf yet.
        testcase_factory=Testcase.default,
        kwargs_function=kwargs.device_kwargs,
        # Currently the tests are not sensitive to frame_size.
        test_type_split=False,
        nic_model_split=True,
        nic_driver_split=True,
        # TODO: Did we even attempt to support different NIC drivers?
    )

    @classmethod
    def from_filename(cls, filename):
        """Classify the suite to its subtype.

        Probably does not work for subclasses.

        :param filename: File name (without dir) of the suite to classify.
        :type filename: str
        :returns: Test subtype this suite has been identified as.
        :rtype: cls
        :raises ValueError: If the suite name is not recognized.
        """
        if u"-tg-" in filename or u"-n2n-" in filename:
            return cls.TREX_PERF
        if filename.endswith(u"-ndrpdr.robot"):
            if u"scheduler" in filename:
                return cls.SCHEDULER_PERF
            return cls.STATELESS_PERF
        if filename.endswith(u"-reconf.robot"):
            return cls.RECONF_PERF
        if filename.endswith(u"-rps.robot") or filename.endswith(u"-cps.robot"):
            return cls.HTTP_PERF
        if filename.endswith(u"-bps.robot"):
            if u"quic" in filename:
                return cls.HOSTSTACK_QUIC_PERF
            return cls.HOSTSTACK_BPS
        if filename.endswith(u"-iperf3-mrr.robot"):
            return cls.IPERF3_MRR
        if filename.endswith(u"-scapy.robot"):
            return cls.SCAPY_FUNC
        raise ValueError(f"{filename}: Not a recognized subtype.")
