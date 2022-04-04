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

"""BPF performance bundle."""

from logging import getLogger
import sys

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
    def __init__(self, program, serializer, hook):
        """Initialize Bundle BPF Perf event class.

        :param program: BPF C code.
        :param serializer: Metric serializer.
        :param hook: Process ID.
        :type program: dict
        :type serializer: Serializer
        :type hook: int
        """
        self.obj = None
        self.code = program[u"code"]
        self.metrics = program[u"metrics"]
        self.events = program[u"events"]
        self.api_replies_list = list()
        self.serializer = serializer
        self.hook = hook

        self.obj = BPF(text=self.code)

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
        except AttributeError:
            getLogger(__name__).error(u"Cannot attach BPF events!")
            sys.exit(1)

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
        except AttributeError:
            getLogger(__name__).error(u"Cannot dettach BPF events!")
            sys.exit(1)

    def fetch_data(self):
        """
        Fetch data by invoking API calls to BPF.
        """
        self.serializer.create(metrics=self.metrics)


        class MaxLens:
            """Class to store the max lengths of strings displayed in
            linux telemetry.
            """

            def __init__(self, cpu, pid, name, value):
                """Initialization.

                :param cpu: CPU to be measured.
                :param pid: PID to be measured.
                :param name: Name to be measured.
                :param value: measured value.
                """
                self.cpu = cpu
                self.pid = pid
                self.name = name
                self.value = value

        max_len = MaxLens(3, 3, 4, 5)
        text = ""
        table_name = ""
        item_list = []

        for _, metric_list in self.metrics.items():
            for metric in metric_list:
                for (key, val) in self.obj.get_table(metric[u"name"]).items():
                    item = dict()
                    labels = dict()
                    item[u"name"] = metric[u"name"]
                    item[u"value"] = val.value
                    for label in metric[u"labelnames"]:
                        labels[label] = getattr(key, label)
                    item[u"labels"] = labels
                    item[u'labels'][u'name'] = item[u'labels'][u'name'].decode(
                        u'utf-8')
                    if item[u"labels"][u"name"] == u"python3":
                        continue
                    if len(str(item[u'value'])) > max_len.value:
                        max_len.value = len(str(item[u'value']))
                    if len(str(item[u'labels'][u'cpu'])) > max_len.cpu:
                        max_len.cpu = len(str(item[u'labels'][u'cpu']))
                    if len(str(item[u'labels'][u'pid'])) > max_len.pid:
                        max_len.pid = len(str(item[u'labels'][u'pid']))
                    if len(str(item[u'labels'][u'name'])) > max_len.name:
                        max_len.name = len(str(item[u'labels'][u'name']))

                    self.api_replies_list.append(item)
                    item_list.append(item)

        item_list = sorted(item_list, key=lambda x: x['labels']['cpu'])
        item_list = sorted(item_list, key=lambda x: x['name'])

        for it in item_list:
            if table_name != it[u"name"]:
                table_name = it[u"name"]
                text += f"\n==={table_name}===\n" \
                        f"cpu {u' ' * (max_len.cpu - 3)} " \
                        f"pid {u' ' * (max_len.pid - 3)} " \
                        f"name {u' ' * (max_len.name - 4)} " \
                        f"value {u' ' * (max_len.value - 5)}\n"
            text += (
                f"""{str(it[u'labels'][u'cpu']) + u' ' *
                     (max_len.cpu - len(str(it[u'labels'][u'cpu'])))}  """
                f"""{str(it[u'labels'][u'pid']) + u' ' *
                     (max_len.pid - len(str(it[u'labels'][u'pid'])))}  """
                f"""{str(it[u'labels'][u'name']) + u' ' *
                     (max_len.name - len(str(it[u'labels'][u'name'])))}  """
                f"""{str(it[u'value']) + u' ' *
                     (max_len.value - len(str(it[u'value'])))}\n"""
            )
        getLogger(__name__).info(text)

    def process_data(self):
        """
        Post process API replies.
        """
        for item in self.api_replies_list:
            self.serializer.serialize(
                metric=item[u"name"], labels=item[u"labels"], item=item
            )
