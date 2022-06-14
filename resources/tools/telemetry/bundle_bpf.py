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
from .constants import Constants


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
            getLogger("console_stderr").error(u"Could not attach BPF events!")
            sys.exit(Constants.err_linux_attach)

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
            getLogger("console_stderr").error(u"Could not detach BPF events!")
            sys.exit(Constants.err_linux_detach)

    def fetch_data(self):
        """
        Fetch data by invoking API calls to BPF.
        """
        self.serializer.create(metrics=self.metrics)

        max_len = {"cpu": 3, "pid": 3, "name": 4, "value": 5}
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
                    item[u'labels'][u'name'] = \
                        item[u'labels'][u'name'].decode(u'utf-8')
                    if item[u"labels"][u"name"] == u"python3":
                        continue
                    if len(str(item[u'labels'][u'cpu'])) > max_len["cpu"]:
                        max_len["cpu"] = len(str(item[u'labels'][u'cpu']))
                    if len(str(item[u'labels'][u'pid'])) > max_len[u"pid"]:
                        max_len[u"pid"] = len(str(item[u'labels'][u'pid']))
                    if len(str(item[u'labels'][u'name'])) > max_len[u"name"]:
                        max_len[u"name"] = len(str(item[u'labels'][u'name']))
                    if len(str(item[u'value'])) > max_len[u"value"]:
                        max_len[u"value"] = len(str(item[u'value']))

                    self.api_replies_list.append(item)
                    item_list.append(item)

        item_list = sorted(item_list, key=lambda x: x['labels']['cpu'])
        item_list = sorted(item_list, key=lambda x: x['name'])

        for itl in item_list:
            if table_name != itl[u"name"]:
                table_name = itl[u"name"]
                text += f"\n==={table_name}===\n" \
                        f"cpu {u' ' * (max_len[u'cpu'] - 3)} " \
                        f"pid {u' ' * (max_len[u'pid'] - 3)} " \
                        f"name {u' ' * (max_len[u'name'] - 4)} " \
                        f"value {u' ' * (max_len[u'value'] - 5)}\n"
            text += (
                f"""{str(itl[u'labels'][u'cpu']) + u' ' *
                     (max_len[u"cpu"] - len(str(itl[u'labels'][u'cpu'])))} """
                f"""{str(itl[u'labels'][u'pid']) + u' ' *
                     (max_len[u"pid"] - len(str(itl[u'labels'][u'pid'])))} """
                f"""{str(itl[u'labels'][u'name']) + u' ' *
                     (max_len[u"name"] - len(str(itl[u'labels'][u'name'])))} """
                f"""{str(itl[u'value']) + u' ' *
                     (max_len[u"value"] - len(str(itl[u'value'])))}\n""")
        getLogger(u"console_stdout").info(text)

    def process_data(self):
        """
        Post process API replies.
        """
        for item in self.api_replies_list:
            self.serializer.serialize(
                metric=item[u"name"], labels=item[u"labels"], item=item
            )
