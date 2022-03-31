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

"""Configuration parsing library."""

from logging import getLogger
from pathlib import Path
import sys

from yaml import safe_load, YAMLError


class Parser:
    """
    Parser class reponsible for loading configuration.
    """
    def __init__(self, configuration_file):
        """
        Config Parser init.

        :param configuration_file: Telemetry configuration file path.
        :type configuration_file: str
        """
        self.instance = None
        self.config = None
        self.suffix = Path(configuration_file).suffix[1:].capitalize()

        try:
            self.instance = globals()[self.suffix+"Loader"](configuration_file)
        except KeyError:
            raise ParserError(u"Unsupported file format!")

        self.config = FileLoader(self.instance).load()


class FileLoader:
    """
    Creates a File Loader object. This is the main object for interacting
    with configuration file.
    """
    def __init__(self, loader):
        """
        File Loader class init.

        :param loader: Loader object responsible for handling file type.
        :type loader: obj
        """
        self.loader = loader

    def load(self):
        """
        File format parser.
        """
        return self.loader.load()


class YamlLoader:
    """
    Creates a YAML Loader object. This is the main object for interacting
    with YAML file.
    """
    def __init__(self, configuration_file):
        """
        YAML Loader class init.

        :param configuration_file: YAML configuration file path.
        :type configuration_file: str
        """
        self.configuration_file = configuration_file

    def load(self):
        """
        YAML format parser.
        """
        with open(self.configuration_file, u"r") as stream:
            try:
                return safe_load(stream)
            except YAMLError as exc:
                raise ParserError(str(exc))


class ParserError(Exception):
    """
    Creates a Parser Error Exception. This exception is supposed to handle
    all the errors raised during processing.
    """
    def __init__(self, message):
        """
        Parser Error Excpetion init.

        :param message: Exception error message.
        :type message: str
        """
        super().__init__()
        self.message = message
        getLogger("console_stderr").error(self.message)
        sys.exit(Constants.err_telemetry_yaml)
