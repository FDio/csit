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
        Config Executor init.=
        """
        self.metric_json = list()
        self.metric_open = dict()
        self.registry = CollectorRegistry()

    def create_metrics(self, metrics):
        """
        Create Openmetrics based on input configuration.

        :param metrics: Metric list to create.
        :type metrics: list
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
        Serialize metric into destination format.

        :param metrics: Metric name.
        :param labels: Metric labels.
        :param item: Metric dict.
        :type metrics: str
        :type labels: dict
        :type item: dict
        """
        self.metric_json.append(deepcopy(item))
        if type(self.metric_open[metric]).__name__ == u"Counter":
            self.metric_open[metric].labels(**labels).inc(
                float(item[u"value"])
            )
        if type(self.metric_open[metric]).__name__ == u"Gauge":
            self.metric_open[metric].labels(**labels).set(
                float(item[u"value"])
            )
        if type(self.metric_open[metric]).__name__ == u"Summary":
            self.metric_open[metric].labels(**labels).observe(
                float(item[u"value"])
            )
        if type(self.metric_open[metric]).__name__ == u"Histogram":
            self.metric_open[metric].labels(**labels).observe(
                float(item[u"value"])
            )
        if type(self.metric_open[metric]).__name__ == u"Info":
            self.metric_open[metric].labels(**labels).info(
                item[u"value"]
            )

    def publish(self):
        """
        Log metric into specific logger.
        """
        for line in generate_latest(self.registry).splitlines():
            getLogger(u"prom").info(line.decode(u"utf-8"))
