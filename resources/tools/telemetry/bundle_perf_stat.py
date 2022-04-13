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

"""Perf Stat performance bundle."""

from logging import getLogger
import sys
import subprocess

from .constants import Constants


class BundlePerfStat:
    """
    Creates a Perf stat object. This is the main object for defining a Perf Stat
    program and interacting with its output.

    Syntax: perf stat [-e <EVENT> | --event=EVENT] [-a] — <command> [<options>]
    """
    def __init__(self, program, serializer, hook):
        """Initialize Bundle BPF Perf event class.

        :param program: events
        :param serializer: Metric serializer.
        :param hook: Process ID.
        :type program: dict
        :type serializer: Serializer
        :type hook: int
        """
        self.metrics = program[u"metrics"]
        self.events = program[u"events"]
        self.api_replies_list = list()
        self.serializer = serializer
        self.hook = hook

    def attach(self, sample_period):
        pass

    def detach(self, sample_period):
        pass

    def fetch_data(self, duration=1):
        """
        Performs perf stat.

        :param duration: Time how long perf stat is collecting data (in
        seconds). Default value is 1 second.
        :type duration: int
        """
        try:
            self.serializer.create(metrics=self.metrics)
            for event in self.events:
                text = subprocess.getoutput(
                    f"""
                    sudo perf stat -x\; -e '{event[u"name"]}'\
                    -a --per-thread\
                    sleep {duration}"""
                )

                if text == u"":
                    getLogger("console_stdout").info(event[u"name"])
                    continue
                if u";" not in text:
                    getLogger("console_stdout").info(
                        f"Could not get counters for event \"{event[u'name']}\""
                        f". Is it supported by CPU?"
                    )

                for line in text.splitlines():
                    item = dict()
                    labels = dict()
                    item[u"name"] = event[u"name"]
                    item[u"value"] = line.split(";")[1]
                    labels["thread"] = u"-".join(line.split("-")[:-1])
                    labels["name"] = u" ".join((line.split(";")[3]).split())
                    labels["pid"] = line.split("-")[-1].split(";")[0]
                    item[u"labels"] = labels

                    getLogger("console_stdout").info(item)
                    self.api_replies_list.append(item)

        except AttributeError:
            getLogger("console_stderr").error(f"Could not successfully run "
                                              f"perf stat command.")
            sys.exit(Constants.err_linux_perf_stat)

    def process_data(self):
        """
        Post process API replies.
        """
        for item in self.api_replies_list:
            self.serializer.serialize(
                metric=item[u"name"], labels=item[u"labels"], item=item
            )
