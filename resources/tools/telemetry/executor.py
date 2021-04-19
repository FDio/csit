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

from importlib import import_module
from logging.config import dictConfig
from logging import getLogger
import sys

from prometheus_client import CollectorRegistry, generate_latest

from .parser import Parser


class Executor:
    """
    Executor class reponsible for executing configuration.
    """
    def __init__(self, configuration_file):
        """
        Config Executor init.

        :param configuration_file: Telemetry configuration file path.
        :type configuration_file: str
        """
        self.parser = Parser(configuration_file)
        self.log = self.parser.config[u"logging"]
        self.programs = self.parser.config[u"programs"]
        self.scheduler = self.parser.config[u"scheduler"]

        dictConfig(self.log)

    def execute(self, pid=None):
        """
        Main executor function will run programs from all bundles in a loop.

        Function call:
            scheduler()

        :param pid: Process ID to attach. None by default.
        :type pid: int
        """
        for program in self.programs:
            try:
                package = program[u"name"]
                name = f"telemetry.bundles.{package}"
                package = package.replace("_", " ").title().replace(" ", "")
                module = import_module(
                    name=name,
                    package=package
                )
                registry = CollectorRegistry()
                bundle = getattr(module, package)(
                    program=program,
                    pid=pid
                )
                bundle.metric_open = self.create_metrics(
                    metrics=program[u"metrics"],
                    registry=registry
                )
                bundle.scheduler(self.scheduler)
            except (ImportError, AttributeError):
                raise ExecutorError(f"Error loading bundle {package!r}!")

            for line in generate_latest(registry).splitlines():
                getLogger(u"prom").info(line.decode("utf-8"))
            getLogger(u"json").info(bundle.metric_json)

    @staticmethod
    def create_metrics(metrics, registry):
        """
        Create Openmetrics based on input configuration.

        :param metrics: Metric list to create.
        :param registry: Openmetric registry collector.
        :type metrics: list
        :type registry: CollectorRegistry
        """
        metric_open = dict()

        for metric_type, metric_list in metrics.items():
            for metric in metric_list:
                module = import_module(
                    name="prometheus_client", package=metric_type.capitalize()
                )
                metric_open[metric[u"name"]] = getattr(
                    module, metric_type.capitalize())(
                        metric[u"name"],
                        metric[u"help"],
                        metric[u"labels"],
                        registry=registry
                    )
        return metric_open


class ExecutorError(Exception):
    """
    Creates a Executor Error Exception. This exception is supposed to handle
    all the errors raised during executing.
    """
    def __init__(self, message):
        """
        Execute Error Excpetion init.

        :param message: Exception error message.
        :type message: str
        """
        super().__init__()
        self.message = message
        getLogger(__name__).error(message)
        sys.exit(1)
