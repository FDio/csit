# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Configuration

Parsing of the configuration YAML file.
"""


import logging
from yaml import load, YAMLError
from pprint import pformat

from errors import PresentationError


class Configuration(object):
    """Configuration of Presentation and analytics layer.

    - based on configuration specified in the configuration YAML file
    - presentation and analytics layer is model driven
    """

    # Tags are used in configuration YAML file and replaced while the file is
    # parsed.
    TAG_OPENER = "{"
    TAG_CLOSER = "}"

    def __init__(self, cfg_file):
        """Initialization.

        :param cfg_file: File handler for the configuration YAML file.
        :type cfg_file: BinaryIO
        """
        self._cfg_file = cfg_file
        self._cfg_yaml = None

        # The configuration is stored in this directory.
        self._configuration = {"environment": dict(),
                               "debug": dict(),
                               "static": dict(),
                               "input": dict(),
                               "output": dict(),
                               "tables": list(),
                               "plots": list(),
                               "files": list()}

    @property
    def configuration(self):
        """Getter - configuration.

        :returns: Configuration.
        :rtype: dict
        """
        return self._configuration

    @property
    def environment(self):
        """Getter - environment.

        :returns: Environment configuration.
        :rtype: dict
        """
        return self._configuration["environment"]

    @property
    def static(self):
        """Getter - static content.

        :returns: Static content configuration.
        :rtype: dict
        """
        return self._configuration["static"]

    @property
    def debug(self):
        """Getter - debug

        :returns: Debug configuration
        :rtype: dict
        """
        return self._configuration["debug"]

    @property
    def is_debug(self):
        """Getter - debug mode

        :returns: True if debug mode is on, otherwise False.
        :rtype: bool
        """

        try:
            if self.environment["configuration"]["CFG[DEBUG]"] == 1:
                return True
            else:
                return False
        except KeyError:
            return False

    @property
    def input(self):
        """Getter - configuration - inputs.
        - jobs and builds.

        :returns: Inputs.
        :rtype: dict
        """
        return self._configuration["input"]

    @property
    def builds(self):
        """Getter - builds defined in configuration.

        :returns: Builds defined in the configuration.
        :rtype: dict
        """
        return self.input["builds"]

    @property
    def output(self):
        """Getter - configuration - output formats and versions to be generated.
        - formats: html, pdf
        - versions: full, ...

        :returns: Outputs to be generated.
        :rtype: dict
        """
        return self._configuration["output"]

    @property
    def tables(self):
        """Getter - tables to be generated.

        :returns: List of specifications of tables to be generated.
        :rtype: list
        """
        return self._configuration["tables"]

    @property
    def plots(self):
        """Getter - plots to be generated.

        :returns: List of specifications of plots to be generated.
        :rtype: list
        """
        return self._configuration["plots"]

    @property
    def files(self):
        """Getter - files to be generated.

        :returns: List of specifications of files to be generated.
        :rtype: list
        """
        return self._configuration["files"]

    def set_input_state(self, job, build_nr, state):
        """Set the state of input

        :param job:
        :param build_nr:
        :param state:
        :return:
        """

        try:
            for build in self._configuration["input"]["builds"][job]:
                if build["build"] == build_nr:
                    build["status"] = state
                    break
            else:
                raise PresentationError("Build '{}' is not defined for job '{}'"
                                        " in configuration file.".
                                        format(build_nr, job))
        except KeyError:
            raise PresentationError("Job '{}' and build '{}' is not defined in "
                                    "configuration file.".format(job, build_nr))

    def set_input_file_name(self, job, build_nr, file_name):
        """Set the state of input

        :param job:
        :param build_nr:
        :param file_name:
        :return:
        """

        try:
            for build in self._configuration["input"]["builds"][job]:
                if build["build"] == build_nr:
                    build["file-name"] = file_name
                    break
            else:
                raise PresentationError("Build '{}' is not defined for job '{}'"
                                        " in configuration file.".
                                        format(build_nr, job))
        except KeyError:
            raise PresentationError("Job '{}' and build '{}' is not defined in "
                                    "configuration file.".format(job, build_nr))

    def _get_type_index(self, item_type):
        """Get index of item type (environment, input, output, ...) in
        configuration YAML file.

        :param item_type: Item type: Top level items in configuration YAML file,
        e.g.: environment, input, output.
        :type item_type: str
        :returns: Index of the given item type.
        :rtype: int
        """

        index = 0
        for item in self._cfg_yaml:
            if item["type"] == item_type:
                return index
            index += 1
        return None

    def _find_tag(self, text):
        """Find the first tag in the given text. The tag is enclosed by the
        TAG_OPENER and TAG_CLOSER.

        :param text: Text to be searched.
        :type text: str
        :returns: The tag, or None if not found.
        :rtype: str
        """
        try:
            start = text.index(self.TAG_OPENER)
            end = text.index(self.TAG_CLOSER, start + 1) + 1
            return text[start:end]
        except ValueError:
            return None

    def _replace_tags(self, data, src_data=None):
        """Replace tag(s) in the data by their values.

        :param data: The data where the tags will be replaced by their values.
        :param src_data: Data where the tags are defined. It is dictionary where
        the key is the tag and the value is the tag value. If not given, 'data'
        is used instead.
        :type data: str or dict
        :type src_data: dict
        :returns: Data with the tags replaced.
        :rtype: str or dict
        :raises: PresentationError if it is not possible to replace the tag or
        the data is not the supported data type (str, dict).
        """

        if src_data is None:
            src_data = data

        if isinstance(data, str):
            tag = self._find_tag(data)
            if tag is not None:
                data = data.replace(tag, src_data[tag[1:-1]])

        elif isinstance(data, dict):
            counter = 0
            for key, value in data.items():
                tag = self._find_tag(value)
                if tag is not None:
                    try:
                        data[key] = value.replace(tag, src_data[tag[1:-1]])
                        counter += 1
                    except KeyError:
                        raise PresentationError("Not possible to replace the "
                                                "tag '{}'".format(tag))
            if counter:
                self._replace_tags(data, src_data)
        else:
            raise PresentationError("Replace tags: Not supported data type.")

        return data

    def _parse_env(self):
        """Parse environment configuration in the configuration YAML file.
        """

        logging.info("Parsing configuration file: environment ...")

        idx = self._get_type_index("environment")
        if idx is None:
            return None

        try:
            self._configuration["environment"]["configuration"] = \
                self._cfg_yaml[idx]["configuration"]
        except KeyError:
            self._configuration["environment"]["configuration"] = None

        try:
            self._configuration["environment"]["paths"] = \
                self._replace_tags(self._cfg_yaml[idx]["paths"])
        except KeyError:
            self._configuration["environment"]["paths"] = None

        try:
            self._configuration["environment"]["urls"] = \
                self._replace_tags(self._cfg_yaml[idx]["urls"])
        except KeyError:
            self._configuration["environment"]["urls"] = None

        try:
            self._configuration["environment"]["make-dirs"] = \
                self._cfg_yaml[idx]["make-dirs"]
        except KeyError:
            self._configuration["environment"]["make-dirs"] = None

        try:
            self._configuration["environment"]["remove-dirs"] = \
                self._cfg_yaml[idx]["remove-dirs"]
        except KeyError:
            self._configuration["environment"]["remove-dirs"] = None

        try:
            self._configuration["environment"]["build-dirs"] = \
                self._cfg_yaml[idx]["build-dirs"]
        except KeyError:
            self._configuration["environment"]["build-dirs"] = None

        logging.info("Done.")

    def _parse_debug(self):
        """Parse debug configuration in the configuration YAML file.
        """

        logging.info("Parsing configuration file: debug ...")

        idx = self._get_type_index("debug")
        if idx is None:
            self.environment["configuration"]["CFG[DEBUG]"] = 0
            return None

        try:
            for key, value in self._cfg_yaml[idx]["general"].items():
                self._configuration["debug"][key] = value

            self._configuration["input"]["builds"] = dict()
            for job, builds in self._cfg_yaml[idx]["builds"].items():
                if builds:
                    self._configuration["input"]["builds"][job] = list()
                    for build in builds:
                        self._configuration["input"]["builds"][job].\
                            append({"build": build["build"],
                                    "status": "downloaded",
                                    "file-name": self._replace_tags(
                                        build["file"],
                                        self.environment["paths"])})
                else:
                    logging.warning("No build is defined for the job '{}'. "
                                    "Trying to continue without it.".
                                    format(job))

        except KeyError:
            raise PresentationError("No data to process.")

    def _parse_input(self):
        """Parse input configuration in the configuration YAML file.

        :raises: PresentationError if there are no data to process.
        """

        logging.info("Parsing configuration file: input ...")

        idx = self._get_type_index("input")
        if idx is None:
            raise PresentationError("No data to process.")

        try:
            for key, value in self._cfg_yaml[idx]["general"].items():
                self._configuration["input"][key] = value
            self._configuration["input"]["builds"] = dict()
            for job, builds in self._cfg_yaml[idx]["builds"].items():
                if builds:
                    self._configuration["input"]["builds"][job] = list()
                    for build in builds:
                        self._configuration["input"]["builds"][job].\
                            append({"build": build, "status": None})
                else:
                    logging.warning("No build is defined for the job '{}'. "
                                    "Trying to continue without it.".
                                    format(job))
        except KeyError:
            raise PresentationError("No data to process.")

        logging.info("Done.")

    def _parse_output(self):
        """Parse output configuration in the configuration YAML file.

        :raises: PresentationError if there is no output defined.
        """

        logging.info("Parsing configuration file: output ...")

        idx = self._get_type_index("output")
        if idx is None:
            raise PresentationError("No output defined.")

        try:
            self._configuration["output"] = self._cfg_yaml[idx]["format"]
        except KeyError:
            raise PresentationError("No output defined.")

        logging.info("Done.")

    def _parse_static(self):
        """Parse configuration of the static content in the configuration YAML
        file.
        """

        logging.info("Parsing configuration file: static content ...")

        idx = self._get_type_index("static")
        if idx is None:
            logging.warning("No static content specified.")

        for key, value in self._cfg_yaml[idx].items():
            if isinstance(value, str):
                try:
                    self._cfg_yaml[idx][key] = self._replace_tags(
                        value, self._configuration["environment"]["paths"])
                except KeyError:
                    pass

        self._configuration["static"] = self._cfg_yaml[idx]

        logging.info("Done.")

    def _parse_elements(self):
        """Parse elements (tables, plots) configuration in the configuration
        YAML file.
        """

        logging.info("Parsing configuration file: elements ...")

        count = 1
        for element in self._cfg_yaml:
            try:
                element["output-file"] = self._replace_tags(
                    element["output-file"],
                    self._configuration["environment"]["paths"])
            except KeyError:
                pass
            if element["type"] == "table":
                logging.info("  {:3d} Processing a table ...".format(count))
                try:
                    element["template"] = self._replace_tags(
                        element["template"],
                        self._configuration["environment"]["paths"])
                except KeyError:
                    pass
                self._configuration["tables"].append(element)
                count += 1
            elif element["type"] == "plot":
                logging.info("  {:3d} Processing a plot ...".format(count))
                self._configuration["plots"].append(element)
                count += 1
            elif element["type"] == "file":
                logging.info("  {:3d} Processing a file ...".format(count))
                try:
                    element["dir-tables"] = self._replace_tags(
                        element["dir-tables"],
                        self._configuration["environment"]["paths"])
                except KeyError:
                    pass
                self._configuration["files"].append(element)
                count += 1

        logging.info("Done.")

    def read_configuration(self):
        """Parse configuration in the configuration YAML file.

        :raises: PresentationError if an error occurred while parsing the
        configuration file.
        """
        try:
            self._cfg_yaml = load(self._cfg_file)
        except YAMLError as err:
            raise PresentationError(msg="An error occurred while parsing the "
                                        "configuration file.",
                                    details=str(err))

        self._parse_env()
        self._parse_debug()
        if not self.debug:
            self._parse_input()
        self._parse_output()
        self._parse_static()
        self._parse_elements()

        logging.debug("Configuration: \n{}".
                      format(pformat(self._configuration)))
