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

"""BPF performance bundle."""

from bcc import BPF


class BundleBpf:
    """
    Creates a BPF object. This is the main object for defining a BPF program,
    and interacting with its output.

    Syntax: BPF({text=BPF_program | src_file=filename}
                [, usdt_contexts=[USDT_object, ...]]
                [, cflags=[arg1, ...]] [, debug=int]
            )

    Exactly one of text or src_file must be supplied (not both).
    """
    def __init__(self, program, pid):
        """Initialize Bundle BPF Perf event class.

        :param program: BPF C code.
        :param pid: Process ID.
        :type program: dict
        :type pid: int
        """
        self.obj = None
        self.code = program[u"code"]
        self.metrics = program[u"metrics"]
        self.events = program[u"events"]
        self.metric_json = list()
        self.metric_open = dict()
        self.pid = pid

        self.obj = BPF(text=self.code)

    def scheduler(self, scheduler=None):
        """
        BPF Telemetry scheduler.

        :param scheduler: Scheduler parameters.
        :type scheduler: dict
        """
        for _ in range(scheduler[u"multiplicity"]):
            self.attach(duration=scheduler[u"duration"])
            self.fetch_data()
            self.process_data()
            self.detach()

    def attach(self, duration):
        """
        Attach events to BPF.

        :param duration: Trial duration.
        :type duration: int
        """
        try:
            for event in self.events:
                self.obj.attach_perf_event(
                    ev_type=event[u"type"],
                    ev_config=event[u"name"],
                    fn_name=event[u"target"],
                    sample_period=duration
                )
        except AttributeError as exp:
            print(exp)

    def detach(self):
        """
        Dettach events from BPF.
        """
        try:
            for event in self.events:
                self.obj.detach_perf_event(
                    ev_type=event[u"type"],
                    ev_config=event[u"name"]
                )
        except AttributeError as exp:
            print(exp)

    def fetch_data(self):
        """
        Fetch data by invoking API calls to BPF.
        """
        for _, value in self.obj.get_table("instructions").items():
            print(value.value)

    def process_data(self):
        """
        Post process command reply.
        """
