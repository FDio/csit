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
from logging.config import dictConfig
from logging import getLogger
import sys

from .parser import Parser
from .serializer import Serializer
from .constants import Constants


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

    def execute(self, hook=None):
        """
        Main executor function will run programs from all bundles in a loop.

        Function call:
            attach(duration)
            fetch_data()
            process_data()
            detach()

        :param hook: Process ID or socket to attach. None by default.
        :type hook: int
        """
        for program in self.programs:
            serializer = Serializer()
            try:
                package = program[u"name"]
                name = f"telemetry.{package}"
                package = package.replace("_", " ").title().replace(" ", "")
                module = import_module(
                    name=name,
                    package=package
                )
                bundle = getattr(module, package)(
                    program=program,
                    serializer=serializer,
                    hook=hook
                )
                bundle.attach(self.scheduler[u"duration"])
                bundle.fetch_data()
                bundle.process_data()
                bundle.detach()
            except (ImportError, AttributeError) as exc:
                raise ExecutorError(
                    f"Error executing bundle {package!r}! - {exc}"
                )
            serializer.publish()

    def execute_daemon(self, hook=None):
        """
        Daemon executor will execute endless loop.

        :param hook: Process ID to attach. None by default.
        :type hook: int
        """
        while True:
            self.execute(hook=hook)


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
        getLogger("console_stderr").error(message)
        sys.exit(Constants.err_telemetry_bundle)
