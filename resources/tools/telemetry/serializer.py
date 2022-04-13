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

"""Config executor library."""

from importlib import import_module
from logging import getLogger


class Serializer:
    """
    Executor class responsible for executing configuration.
    """
    def __init__(self):
        """
        Config Executor init.=
        """
        self.metric_registry = dict()

    def create(self, metrics):
        """
        Create metrics based on input configuration.

        :param metrics: Metric list to create.
        :type metrics: list
        """
        for metric_type, metric_list in metrics.items():
            for metric in metric_list:
                module = import_module(
                    name=u"telemetry.metrics", package=metric_type.capitalize()
                )
                self.metric_registry[metric[u"name"]] = getattr(
                    module, metric_type.capitalize()
                )(**metric)

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
        if type(self.metric_registry[metric]).__name__ == u"Counter":
            self.metric_registry[metric].labels(**labels).inc(
                float(item[u"value"])
            )
        if type(self.metric_registry[metric]).__name__ == u"Gauge":
            self.metric_registry[metric].labels(**labels).set(
                float(item[u"value"])
            )
        if type(self.metric_registry[metric]).__name__ == u"Info":
            self.metric_registry[metric].labels(**labels).info(
                item[u"value"]
            )

    def publish(self):
        """
        Publish metric into logger.
        """
        output = []
        for _, metric_list in self.metric_registry.items():
            for metric in metric_list.collect():
                mname = metric.name
                mtype = metric.type

                # Adjust from OpenMetrics into Prometheus format.
                mname = f"{mname}_total" if mtype == u"counter" else mname
                mname = f"{mname}_info" if mtype == u"info" else mname
                if mtype in (u"info", u"stateset"):
                    mtype = u"gauge"
                if mtype in (u"gaugehistogram", u"histogram"):
                    mtype = u"histogram"

                mdocumentation = metric.documentation.replace(u"\\", r"\\")
                mdocumentation = mdocumentation.replace(u"\n", r"\n")
                output.append(f"# HELP {mname} {mdocumentation}\n")
                output.append(f"# TYPE {mname} {mtype}\n")

                for line in metric.samples:
                    if line.labels:
                        llabel = []
                        for k, value in sorted(line.labels.items()):
                            value = str(value)
                            value = value.replace(u"\\", r"\\")
                            value = value.replace(u"\n", r"\n")
                            value = value.replace(u'"', r'\"')
                            llabel.append(f'{k}="{value}"')
                        labelstr = f"{{{','.join(llabel)}}}"
                    else:
                        labelstr = u""

                    timestamp = f" {int(float(line.timestamp) * 1000):d}" \
                        if line.timestamp else u""
                    output.append(
                        f"{line.name}{labelstr} {line.value}{timestamp}\n"
                    )
        getLogger(u"prom").info(u"".join(output))
