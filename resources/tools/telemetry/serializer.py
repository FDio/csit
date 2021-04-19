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

"""Config executor library."""

from copy import deepcopy
from importlib import import_module
from logging import getLogger

from prometheus_client import CollectorRegistry, generate_latest


class Serializer:
    """
    Executor class reponsible for executing configuration.
    """
    def __init__(self):
        """
        Config Executor init.

        :param configuration_file: Telemetry configuration file path.
        :type configuration_file: str
        """
        self.metric_json = list()
        self.metric_open = dict()
        self.registry = CollectorRegistry()

    def create_metrics(self, metrics):
        """
        Create Openmetrics based on input configuration.

        :param metrics: Metric list to create.
        :param registry: Openmetric registry collector.
        :type metrics: list
        :type registry: CollectorRegistry
        """
        self.metric_open = dict()

        for metric_type, metric_list in metrics.items():
            for metric in metric_list:
                module = import_module(
                    name="prometheus_client", package=metric_type.capitalize()
                )
                self.metric_open[metric[u"name"]] = getattr(
                    module, metric_type.capitalize())(
                        metric[u"name"],
                        metric[u"help"],
                        metric[u"labels"],
                        registry=self.registry
                    )

    def serialize(self, metric, labels, item):
        """
        Main executor function will run programs from all bundles in a loop.

        Function call:
            scheduler()

        :param pid: Process ID to attach. None by default.
        :type pid: int
        """
        self.metric_open[metric].labels(**labels).inc(
            float(item[u"value"])
        )
        self.metric_json.append(deepcopy(item))

    def write(self, pid=None):
        """
        Main executor function will run programs from all bundles in a loop.

        Function call:
            scheduler()

        :param pid: Process ID to attach. None by default.
        :type pid: int
        """
        for line in generate_latest(self.registry).splitlines():
            getLogger(u"prom").info(line.decode("utf-8"))
        getLogger(u"json").info(self.metric_json)
