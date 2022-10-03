<<<<<<< HEAD   (2c46cb job-spec: Add wireguard test to regression)
=======
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
        """Initialize Bundle Perf Stat event class.

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

    def attach(self, duration=1):
        """
               Performs perf stat.

               :param duration: Time how long perf stat is collecting data (in
               seconds). Default value is 1 second.
               :type duration: int
               """
        try:
            self.serializer.create(metrics=self.metrics)
            event = self.events[0]
            text = subprocess.getoutput(
                f"""sudo perf stat -x\; -e\
                '{{cpu/event={hex(event[u"eventcode"])},\
                umask={hex(event[u"umask"])}/u}}'\
                -a --per-thread\
                sleep {duration}"""
            )
        except subprocess.CalledProcessError:
            getLogger("console_stderr").error(f"Could not successfully run "
                                              f"perf stat command.")
            sys.exit(Constants.err_linux_perf_stat)

        if text == u"":
            getLogger("console_stdout").info(event[u"eventcode"])
        elif text.count(u";") < 6:
            getLogger("console_stdout").info(
                f"Could not get counters for event "\
                f"{event[u'eventcode']}. "\
                f"Is it supported by CPU?"
            )
        else:
            for line in text.splitlines():
                item = dict()
                labels = dict()
                item[u"name"] = self.metrics['counter'][0]['name']
                item[u"value"] = line.split(";")[1]
                labels["thread"] = u"-".join(
                    line.split(";")[0].split("-")[0:-1]
                )
                labels["pid"] = line.split(";")[0].split("-")[-1]
                item[u"labels"] = labels

                getLogger("console_stdout").info(item)
                self.api_replies_list.append(item)


    def detach(self):
        pass

    def fetch_data(self):
       pass

    def process_data(self):
        """
        Post process API replies.
        """
        for item in self.api_replies_list:
            self.serializer.serialize(
                metric=item[u"name"], labels=item[u"labels"], item=item
            )
>>>>>>> CHANGE (5cd951 telemetry: small fixes)
