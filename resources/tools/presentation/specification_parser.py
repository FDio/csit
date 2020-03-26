# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Specification

Parsing of the specification YAML file.
"""


import logging
from pprint import pformat

from yaml import load, FullLoader, YAMLError

from pal_errors import PresentationError
from pal_utils import (
    get_last_successful_build_nr, get_last_completed_build_number
)


class Specification:
    """Specification of Presentation and analytics layer.

    - based on specification specified in the specification YAML file
    - presentation and analytics layer is model driven
    """

    # Tags are used in specification YAML file and replaced while the file is
    # parsed.
    TAG_OPENER = u"{"
    TAG_CLOSER = u"}"

    def __init__(self, cfg_file):
        """Initialization.

        :param cfg_file: File handler for the specification YAML file.
        :type cfg_file: BinaryIO
        """
        self._cfg_file = cfg_file
        self._cfg_yaml = None

        self._specification = {
            u"environment": dict(),
            u"configuration": dict(),
            u"static": dict(),
            u"input": dict(),
            u"output": dict(),
            u"tables": list(),
            u"plots": list(),
            u"files": list(),
            u"cpta": dict()
        }

    @property
    def specification(self):
        """Getter - specification.

        :returns: Specification.
        :rtype: dict
        """
        return self._specification

    @property
    def environment(self):
        """Getter - environment.

        :returns: Environment specification.
        :rtype: dict
        """
        return self._specification[u"environment"]

    @property
    def configuration(self):
        """Getter - configuration.

        :returns: Configuration of PAL.
        :rtype: dict
        """
        return self._specification[u"configuration"]

    @property
    def static(self):
        """Getter - static content.

        :returns: Static content specification.
        :rtype: dict
        """
        return self._specification[u"static"]

    @property
    def mapping(self):
        """Getter - Mapping.

        :returns: Mapping of the old names of test cases to the new (actual)
            one.
        :rtype: dict
        """
        return self._specification[u"configuration"][u"mapping"]

    @property
    def ignore(self):
        """Getter - Ignore list.

        :returns: List of ignored test cases.
        :rtype: list
        """
        return self._specification[u"configuration"][u"ignore"]

    @property
    def alerting(self):
        """Getter - Alerting.

        :returns: Specification of alerts.
        :rtype: dict
        """
        return self._specification[u"configuration"][u"alerting"]

    @property
    def input(self):
        """Getter - specification - inputs.
        - jobs and builds.

        :returns: Inputs.
        :rtype: dict
        """
        return self._specification[u"input"]

    @input.setter
    def input(self, new_value):
        """Setter - specification - inputs.

        :param new_value: New value to be set.
        :type new_value: dict
        """
        self._specification[u"input"] = new_value

    @property
    def builds(self):
        """Getter - builds defined in specification.

        :returns: Builds defined in the specification.
        :rtype: dict
        """
        return self.input[u"builds"]

    @builds.setter
    def builds(self, new_value):
        """Setter - builds defined in specification.

        :param new_value: New value to be set.
        :type new_value: dict
        """
        self.input[u"builds"] = new_value

    def add_build(self, job, build):
        """Add a build to the specification.

        :param job: The job which run the build.
        :param build: The build to be added.
        :type job: str
        :type build: dict
        """
        if self._specification[u"input"][u"builds"].get(job, None) is None:
            self._specification[u"input"][u"builds"][job] = list()
        self._specification[u"input"][u"builds"][job].append(build)

    @property
    def output(self):
        """Getter - specification - output formats and versions to be generated.
        - formats: html, pdf
        - versions: full, ...

        :returns: Outputs to be generated.
        :rtype: dict
        """
        return self._specification[u"output"]

    @property
    def tables(self):
        """Getter - tables to be generated.

        :returns: List of specifications of tables to be generated.
        :rtype: list
        """
        return self._specification[u"tables"]

    @property
    def plots(self):
        """Getter - plots to be generated.

        :returns: List of specifications of plots to be generated.
        :rtype: list
        """
        return self._specification[u"plots"]

    @property
    def files(self):
        """Getter - files to be generated.

        :returns: List of specifications of files to be generated.
        :rtype: list
        """
        return self._specification[u"files"]

    @property
    def cpta(self):
        """Getter - Continuous Performance Trending and Analysis to be
        generated.

        :returns: List of specifications of Continuous Performance Trending and
            Analysis to be generated.
        :rtype: list
        """
        return self._specification[u"cpta"]

    def set_input_state(self, job, build_nr, state):
        """Set the state of input

        :param job: Job name.
        :param build_nr: Build number.
        :param state: The new input state.
        :type job: str
        :type build_nr: int
        :type state: str
        :raises: PresentationError if wrong job and/or build is provided.
        """

        try:
            for build in self._specification[u"input"][u"builds"][job]:
                if build[u"build"] == build_nr:
                    build[u"status"] = state
                    break
            else:
                raise PresentationError(
                    f"Build {build_nr} is not defined for job {job} in "
                    f"specification file."
                )
        except KeyError:
            raise PresentationError(
                f"Job {job} and build {build_nr} is not defined in "
                f"specification file."
            )

    def set_input_file_name(self, job, build_nr, file_name):
        """Set the state of input

        :param job: Job name.
        :param build_nr: Build number.
        :param file_name: The new file name.
        :type job: str
        :type build_nr: int
        :type file_name: str
        :raises: PresentationError if wrong job and/or build is provided.
        """

        try:
            for build in self._specification[u"input"][u"builds"][job]:
                if build[u"build"] == build_nr:
                    build[u"file-name"] = file_name
                    break
            else:
                raise PresentationError(
                    f"Build {build_nr} is not defined for job {job} in "
                    f"specification file."
                )
        except KeyError:
            raise PresentationError(
                f"Job {job} and build {build_nr} is not defined in "
                f"specification file."
            )

    def _get_build_number(self, job, build_type):
        """Get the number of the job defined by its name:
         - lastSuccessfulBuild
         - lastCompletedBuild

        :param job: Job name.
        :param build_type: Build type:
         - lastSuccessfulBuild
         - lastCompletedBuild
        :type job" str
        :raises PresentationError: If it is not possible to get the build
            number.
        :returns: The build number.
        :rtype: int
        """

        # defined as a range <start, end>
        if build_type == u"lastSuccessfulBuild":
            # defined as a range <start, lastSuccessfulBuild>
            ret_code, build_nr, _ = get_last_successful_build_nr(
                self.environment[u"urls"][u"URL[JENKINS,CSIT]"], job)
        elif build_type == u"lastCompletedBuild":
            # defined as a range <start, lastCompletedBuild>
            ret_code, build_nr, _ = get_last_completed_build_number(
                self.environment[u"urls"][u"URL[JENKINS,CSIT]"], job)
        else:
            raise PresentationError(f"Not supported build type: {build_type}")
        if ret_code != 0:
            raise PresentationError(u"Not possible to get the number of the "
                                    u"build number.")
        try:
            build_nr = int(build_nr)
            return build_nr
        except ValueError as err:
            raise PresentationError(
                f"Not possible to get the number of the build number. Reason:\n"
                f"{repr(err)}"
            )

    def _get_type_index(self, item_type):
        """Get index of item type (environment, input, output, ...) in
        specification YAML file.

        :param item_type: Item type: Top level items in specification YAML file,
            e.g.: environment, input, output.
        :type item_type: str
        :returns: Index of the given item type.
        :rtype: int
        """

        index = 0
        for item in self._cfg_yaml:
            if item[u"type"] == item_type:
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
            the key is the tag and the value is the tag value. If not given,
            'data' is used instead.
        :type data: str, list or dict
        :type src_data: dict
        :returns: Data with the tags replaced.
        :rtype: str, list or dict
        :raises: PresentationError if it is not possible to replace the tag or
            the data is not the supported data type (str, list or dict).
        """

        if src_data is None:
            src_data = data

        if isinstance(data, str):
            tag = self._find_tag(data)
            if tag is not None:
                data = data.replace(tag, src_data[tag[1:-1]])
            return data

        if isinstance(data, list):
            new_list = list()
            for item in data:
                new_list.append(self._replace_tags(item, src_data))
            return new_list

        if isinstance(data, dict):
            counter = 0
            for key, value in data.items():
                tag = self._find_tag(value)
                if tag is not None:
                    try:
                        data[key] = value.replace(tag, src_data[tag[1:-1]])
                        counter += 1
                    except KeyError:
                        raise PresentationError(
                            f"Not possible to replace the tag {tag}"
                        )
            if counter:
                self._replace_tags(data, src_data)
            return data

        raise PresentationError(u"Replace tags: Not supported data type.")

    def _parse_env(self):
        """Parse environment specification in the specification YAML file.
        """

        logging.info(u"Parsing specification file: environment ...")

        idx = self._get_type_index(u"environment")
        if idx is None:
            return

        try:
            self._specification[u"environment"][u"configuration"] = \
                self._cfg_yaml[idx][u"configuration"]
        except KeyError:
            self._specification[u"environment"][u"configuration"] = None

        try:
            self._specification[u"environment"][u"paths"] = \
                self._replace_tags(self._cfg_yaml[idx][u"paths"])
        except KeyError:
            self._specification[u"environment"][u"paths"] = None

        try:
            self._specification[u"environment"][u"urls"] = \
                self._cfg_yaml[idx][u"urls"]
        except KeyError:
            self._specification[u"environment"][u"urls"] = None

        try:
            self._specification[u"environment"][u"make-dirs"] = \
                self._cfg_yaml[idx][u"make-dirs"]
        except KeyError:
            self._specification[u"environment"][u"make-dirs"] = None

        try:
            self._specification[u"environment"][u"remove-dirs"] = \
                self._cfg_yaml[idx][u"remove-dirs"]
        except KeyError:
            self._specification[u"environment"][u"remove-dirs"] = None

        try:
            self._specification[u"environment"][u"build-dirs"] = \
                self._cfg_yaml[idx][u"build-dirs"]
        except KeyError:
            self._specification[u"environment"][u"build-dirs"] = None

        try:
            self._specification[u"environment"][u"testbeds"] = \
                self._cfg_yaml[idx][u"testbeds"]
        except KeyError:
            self._specification[u"environment"][u"testbeds"] = None

        logging.info(u"Done.")

    def _load_mapping_table(self):
        """Load a mapping table if it is specified. If not, use empty list.
        """

        mapping_file_name = self._specification[u"configuration"].\
            get(u"mapping-file", None)
        if mapping_file_name:
            try:
                with open(mapping_file_name, u'r') as mfile:
                    mapping = load(mfile, Loader=FullLoader)
                    # Make sure everything is lowercase
                    self._specification[u"configuration"][u"mapping"] = \
                        {key.lower(): val.lower() for key, val in
                         mapping.items()}
                logging.debug(f"Loaded mapping table:\n{mapping}")
            except (YAMLError, IOError) as err:
                raise PresentationError(
                    msg=f"An error occurred while parsing the mapping file "
                        f"{mapping_file_name}",
                    details=repr(err)
                )
        else:
            self._specification[u"configuration"][u"mapping"] = dict()

    def _load_ignore_list(self):
        """Load an ignore list if it is specified. If not, use empty list.
        """

        ignore_list_name = self._specification[u"configuration"].\
            get(u"ignore-list", None)
        if ignore_list_name:
            try:
                with open(ignore_list_name, u'r') as ifile:
                    ignore = load(ifile, Loader=FullLoader)
                    # Make sure everything is lowercase
                    self._specification[u"configuration"][u"ignore"] = \
                        [item.lower() for item in ignore]
                logging.debug(f"Loaded ignore list:\n{ignore}")
            except (YAMLError, IOError) as err:
                raise PresentationError(
                    msg=f"An error occurred while parsing the ignore list file "
                        f"{ignore_list_name}.",
                    details=repr(err)
                )
        else:
            self._specification[u"configuration"][u"ignore"] = list()

    def _parse_configuration(self):
        """Parse configuration of PAL in the specification YAML file.
        """

        logging.info(u"Parsing specification file: configuration ...")

        idx = self._get_type_index("configuration")
        if idx is None:
            logging.warning(
                u"No configuration information in the specification file."
            )
            return

        try:
            self._specification[u"configuration"] = self._cfg_yaml[idx]
        except KeyError:
            raise PresentationError(u"No configuration defined.")

        # Data sets: Replace ranges by lists
        for set_name, data_set in self.configuration[u"data-sets"].items():
            if not isinstance(data_set, dict):
                continue
            for job, builds in data_set.items():
                if not builds:
                    continue
                if isinstance(builds, dict):
                    build_end = builds.get(u"end", None)
                    try:
                        build_end = int(build_end)
                    except ValueError:
                        # defined as a range <start, build_type>
                        build_end = self._get_build_number(job, build_end)
                    builds = [x for x in range(builds[u"start"],
                                               build_end + 1)
                              if x not in builds.get(u"skip", list())]
                    self.configuration[u"data-sets"][set_name][job] = builds
                elif isinstance(builds, list):
                    for idx, item in enumerate(builds):
                        try:
                            builds[idx] = int(item)
                        except ValueError:
                            # defined as a range <build_type>
                            builds[idx] = self._get_build_number(job, item)

        # Data sets: add sub-sets to sets (only one level):
        for set_name, data_set in self.configuration[u"data-sets"].items():
            if isinstance(data_set, list):
                new_set = dict()
                for item in data_set:
                    try:
                        for key, val in self.configuration[u"data-sets"][item].\
                                items():
                            new_set[key] = val
                    except KeyError:
                        raise PresentationError(
                            f"Data set {item} is not defined in "
                            f"the configuration section."
                        )
                self.configuration[u"data-sets"][set_name] = new_set

        # Mapping table:
        self._load_mapping_table()

        # Ignore list:
        self._load_ignore_list()

        logging.info(u"Done.")

    def _parse_input(self):
        """Parse input specification in the specification YAML file.

        :raises: PresentationError if there are no data to process.
        """

        logging.info(u"Parsing specification file: input ...")

        idx = self._get_type_index(u"input")
        if idx is None:
            raise PresentationError(u"No data to process.")

        try:
            for key, value in self._cfg_yaml[idx][u"general"].items():
                self._specification[u"input"][key] = value
            self._specification[u"input"][u"builds"] = dict()

            for job, builds in self._cfg_yaml[idx][u"builds"].items():
                if builds:
                    if isinstance(builds, dict):
                        build_end = builds.get(u"end", None)
                        try:
                            build_end = int(build_end)
                        except ValueError:
                            # defined as a range <start, build_type>
                            build_end = self._get_build_number(job, build_end)
                        builds = [x for x in range(builds[u"start"],
                                                   build_end + 1)
                                  if x not in builds.get(u"skip", list())]
                    self._specification[u"input"][u"builds"][job] = list()
                    for build in builds:
                        self._specification[u"input"][u"builds"][job]. \
                            append({u"build": build, u"status": None})

                else:
                    logging.warning(
                        f"No build is defined for the job {job}. Trying to "
                        f"continue without it."
                    )
        except KeyError:
            raise PresentationError(u"No data to process.")

        logging.info(u"Done.")

    def _parse_output(self):
        """Parse output specification in the specification YAML file.

        :raises: PresentationError if there is no output defined.
        """

        logging.info(u"Parsing specification file: output ...")

        idx = self._get_type_index(u"output")
        if idx is None:
            raise PresentationError(u"No output defined.")

        try:
            self._specification[u"output"] = self._cfg_yaml[idx]
        except (KeyError, IndexError):
            raise PresentationError(u"No output defined.")

        logging.info(u"Done.")

    def _parse_static(self):
        """Parse specification of the static content in the specification YAML
        file.
        """

        logging.info(u"Parsing specification file: static content ...")

        idx = self._get_type_index(u"static")
        if idx is None:
            logging.warning(u"No static content specified.")

        for key, value in self._cfg_yaml[idx].items():
            if isinstance(value, str):
                try:
                    self._cfg_yaml[idx][key] = self._replace_tags(
                        value, self._specification[u"environment"][u"paths"])
                except KeyError:
                    pass

        self._specification[u"static"] = self._cfg_yaml[idx]

        logging.info(u"Done.")

    def _parse_elements_tables(self, table):
        """Parse tables from the specification YAML file.

        :param table: Table to be parsed from the specification file.
        :type table: dict
        :raises PresentationError: If wrong data set is used.
        """

        try:
            table[u"template"] = self._replace_tags(
                table[u"template"],
                self._specification[u"environment"][u"paths"])
        except KeyError:
            pass

        # Add data sets
        try:
            for item in (u"reference", u"compare"):
                if table.get(item, None):
                    data_set = table[item].get(u"data", None)
                    if isinstance(data_set, str):
                        table[item][u"data"] = \
                            self.configuration[u"data-sets"][data_set]
                    data_set = table[item].get(u"data-replacement", None)
                    if isinstance(data_set, str):
                        table[item][u"data-replacement"] = \
                            self.configuration[u"data-sets"][data_set]

            if table.get(u"history", None):
                for i in range(len(table[u"history"])):
                    data_set = table[u"history"][i].get(u"data", None)
                    if isinstance(data_set, str):
                        table[u"history"][i][u"data"] = \
                            self.configuration[u"data-sets"][data_set]
                    data_set = table[u"history"][i].get(
                        u"data-replacement", None)
                    if isinstance(data_set, str):
                        table[u"history"][i][u"data-replacement"] = \
                            self.configuration[u"data-sets"][data_set]

            if table.get(u"columns", None):
                for i in range(len(table[u"columns"])):
                    data_set = table[u"columns"][i].get(u"data-set", None)
                    if isinstance(data_set, str):
                        table[u"columns"][i][u"data-set"] = \
                            self.configuration[u"data-sets"][data_set]
                    data_set = table[u"columns"][i].get(
                        u"data-replacement", None)
                    if isinstance(data_set, str):
                        table[u"columns"][i][u"data-replacement"] = \
                            self.configuration[u"data-sets"][data_set]

        except KeyError:
            raise PresentationError(
                f"Wrong data set used in {table.get(u'title', u'')}."
            )

        self._specification[u"tables"].append(table)

    def _parse_elements_plots(self, plot):
        """Parse plots from the specification YAML file.

        :param plot: Plot to be parsed from the specification file.
        :type plot: dict
        :raises PresentationError: If plot layout is not defined.
        """

        # Add layout to the plots:
        layout = plot[u"layout"].get(u"layout", None)
        if layout is not None:
            plot[u"layout"].pop(u"layout")
            try:
                for key, val in (self.configuration[u"plot-layouts"]
                                 [layout].items()):
                    plot[u"layout"][key] = val
            except KeyError:
                raise PresentationError(
                    f"Layout {layout} is not defined in the "
                    f"configuration section."
                )
        self._specification[u"plots"].append(plot)

    def _parse_elements_files(self, file):
        """Parse files from the specification YAML file.

        :param file: File to be parsed from the specification file.
        :type file: dict
        """

        try:
            file[u"dir-tables"] = self._replace_tags(
                file[u"dir-tables"],
                self._specification[u"environment"][u"paths"])
        except KeyError:
            pass
        self._specification[u"files"].append(file)

    def _parse_elements_cpta(self, cpta):
        """Parse cpta from the specification YAML file.

        :param cpta: cpta to be parsed from the specification file.
        :type cpta: dict
        :raises PresentationError: If wrong data set is used or if plot layout
            is not defined.
        """

        for plot in cpta[u"plots"]:
            # Add layout to the plots:
            layout = plot.get(u"layout", None)
            if layout is not None:
                try:
                    plot[u"layout"] = \
                        self.configuration[u"plot-layouts"][layout]
                except KeyError:
                    raise PresentationError(
                        f"Layout {layout} is not defined in the "
                        f"configuration section."
                    )
            # Add data sets:
            if isinstance(plot.get(u"data", None), str):
                data_set = plot[u"data"]
                try:
                    plot[u"data"] = \
                        self.configuration[u"data-sets"][data_set]
                except KeyError:
                    raise PresentationError(
                        f"Data set {data_set} is not defined in "
                        f"the configuration section."
                    )
        self._specification[u"cpta"] = cpta

    def _parse_elements(self):
        """Parse elements (tables, plots, ..) specification in the specification
        YAML file.
        """

        logging.info(u"Parsing specification file: elements ...")

        count = 1
        for element in self._cfg_yaml:

            # Replace tags:
            try:
                element[u"output-file"] = self._replace_tags(
                    element[u"output-file"],
                    self._specification[u"environment"][u"paths"])
            except KeyError:
                pass

            try:
                element[u"input-file"] = self._replace_tags(
                    element[u"input-file"],
                    self._specification[u"environment"][u"paths"])
            except KeyError:
                pass

            try:
                element[u"output-file-links"] = self._replace_tags(
                    element[u"output-file-links"],
                    self._specification[u"environment"][u"paths"])
            except KeyError:
                pass

            # Add data sets to the elements:
            if isinstance(element.get(u"data", None), str):
                data_set = element[u"data"]
                try:
                    element[u"data"] = \
                        self.configuration[u"data-sets"][data_set]
                except KeyError:
                    raise PresentationError(
                        f"Data set {data_set} is not defined in the "
                        f"configuration section."
                    )
            elif isinstance(element.get(u"data", None), list):
                new_list = list()
                for item in element[u"data"]:
                    try:
                        new_list.append(
                            self.configuration[u"data-sets"][item]
                        )
                    except KeyError:
                        raise PresentationError(
                            f"Data set {item} is not defined in the "
                            f"configuration section."
                        )
                element[u"data"] = new_list

            # Parse elements:
            if element[u"type"] == u"table":

                logging.info(f"  {count:3d} Processing a table ...")
                self._parse_elements_tables(element)
                count += 1

            elif element[u"type"] == u"plot":

                logging.info(f"  {count:3d} Processing a plot ...")
                self._parse_elements_plots(element)
                count += 1

            elif element[u"type"] == u"file":

                logging.info(f"  {count:3d} Processing a file ...")
                self._parse_elements_files(element)
                count += 1

            elif element[u"type"] == u"cpta":

                logging.info(
                    f"  {count:3d} Processing Continuous Performance Trending "
                    f"and Analysis ..."
                )
                self._parse_elements_cpta(element)
                count += 1

        logging.info(u"Done.")

    def read_specification(self):
        """Parse specification in the specification YAML file.

        :raises: PresentationError if an error occurred while parsing the
            specification file.
        """
        try:
            self._cfg_yaml = load(self._cfg_file, Loader=FullLoader)
        except YAMLError as err:
            raise PresentationError(msg=u"An error occurred while parsing the "
                                        u"specification file.",
                                    details=repr(err))

        self._parse_env()
        self._parse_configuration()
        self._parse_input()
        self._parse_output()
        self._parse_static()
        self._parse_elements()

        logging.debug(f"Specification: \n{pformat(self._specification)}")
