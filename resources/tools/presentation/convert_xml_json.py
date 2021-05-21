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

"""Convert output_info.xml files into JSON structures.

Version: 0.1.0
Date:    20th May 2021

The json structure is defined in https://gerrit.fd.io/r/c/csit/+/28992
"""

import os
import re
import json
import logging
import gzip

from os.path import join
from shutil import rmtree
from copy import deepcopy

from pal_utils import get_files


class JSONData:
    """A Class storing and manipulating data from tests.
    """

    def __init__(self, template=None):
        """Initialization.

        :param template: JSON formatted template used to store data. It can
            include default values.
        :type template: dict
        """

        self._template = deepcopy(template)
        self._data = self._template if self._template else dict()

    def __str__(self):
        """Return a string with human readable data.

        :returns: Readable description.
        :rtype: str
        """
        return str(self._data)

    def __repr__(self):
        """Return a string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return f"JSONData(template={self._template!r})"

    @property
    def data(self):
        """Getter

        :return: Data stored in the object.
        :rtype: dict
        """
        return self._data

    def add_element(self, value, path_to_value):
        """Add an element to the json structure.

        :param value: Element value.
        :param path_to_value: List of tuples where the first item is the element
            on the path and the second one is its type.
        :type value: dict, list, str, int, float, bool
        :type path_to_value: list
        :raises: IndexError if the path is empty.
        :raises: TypeError if the val is of not supported type.
        """

        def _add_element(val, path, structure):
            """Add an element to the given path.

            :param val: Element value.
            :param path: List of tuples where the first item is the element
            on the path and the second one is its type.
            :param structure: The structure where the element is added.
            :type val: dict, list, str, int, float, bool
            :type path: list
            :type structure: dict
            :raises TypeError if there is a wrong type in the path.
            """
            if len(path) == 1:
                if isinstance(structure, dict):
                    if path[0][1] is dict:
                        if path[0][0] not in structure:
                            structure[path[0][0]] = dict()
                        structure[path[0][0]].update(val)
                    elif path[0][1] is list:
                        if path[0][0] not in structure:
                            structure[path[0][0]] = list()
                        if isinstance(val, list):
                            structure[path[0][0]].extend(val)
                        else:
                            structure[path[0][0]].append(val)
                    else:
                        structure[path[0][0]] = val
                elif isinstance(structure, list):
                    if path[0][0] == -1 or path[0][0] >= len(structure):
                        if isinstance(val, list):
                            structure.extend(val)
                        else:
                            structure.append(val)
                    else:
                        structure[path[0][0]] = val
                return

            if isinstance(structure, dict):
                if path[0][1] is dict:
                    if path[0][0] not in structure:
                        structure[path[0][0]] = dict()
                elif path[0][1] is list:
                    if path[0][0] not in structure:
                        structure[path[0][0]] = list()
            elif isinstance(structure, list):
                if path[0][0] == -1 or path[0][0] >= len(structure):
                    if path[0][1] is list:
                        structure.append(list())
                    elif path[0][1] is dict:
                        structure.append(dict())
                    else:
                        structure.append(0)
                    path[0][0] = len(structure) - 1
            else:
                raise TypeError(
                    u"Only the last item in the path can be different type "
                    u"then list or dictionary."
                )
            _add_element(val, path[1:], structure[path[0][0]])

        if not isinstance(value, (dict, list, str, int, float, bool)):
            raise TypeError(
                u"The value must be one of these types: dict, list, str, int, "
                u"float, bool.\n"
                f"Value: {value}\n"
                f"Path: {path_to_value}"
            )
        _add_element(deepcopy(value), path_to_value, self._data)

    def get_element(self, path):
        """Get the element specified by the path.

        :param path: List of keys and indices to the requested element or
            sub-tree.
        :type path: list
        :returns: Element specified by the path.
        :rtype: any
        """
        raise NotImplementedError

    def dump(self, file_out, indent=None):
        """Write JSON data to a file.

        :param file_out: Path to the output JSON file.
        :param indent: Indentation of items in JSON string. It is directly
            passed to json.dump method.
        :type file_out: str
        :type indent: str
        """
        try:
            with open(file_out, u"w") as file_handler:
                json.dump(self._data, file_handler, indent=indent)
        except OSError as err:
            logging.warning(f"{repr(err)} Skipping")

    def load(self, file_in):
        """Load JSON data from a file.

        :param file_in: Path to the input JSON file.
        :type file_in: str
        :raises: ValueError if the data being deserialized is not a valid
            JSON document.
        :raises: IOError if the file is not found or corrupted.
        """
        with open(file_in, u"r") as file_handler:
            self._data = json.load(file_handler)


def _export_test_from_xml_to_json(tid, in_data, out, template, metadata):
    """Export data from a test to a json structure.

    :param tid: Test ID.
    :param in_data: Test data.
    :param out: Path to output json file.
    :param template: JSON template with optional default values.
    :param metadata: Data which are not stored in XML structure.
    :type tid: str
    :type in_data: dict
    :type out: str
    :type template: dict
    :type metadata: dict
    """

    p_metadata = [(u"metadata", dict), ]
    p_test = [(u"test", dict), ]
    p_log = [(u"log", list), (-1, list)]

    data = JSONData(template=template)

    data.add_element({u"suite-id": metadata.pop(u"suite-id", u"")}, p_metadata)
    data.add_element(
        {u"suite-doc": metadata.pop(u"suite-doc", u"")}, p_metadata
    )
    data.add_element({u"testbed": metadata.pop(u"testbed", u"")}, p_metadata)
    data.add_element(
        {u"sut-version": metadata.pop(u"sut-version", u"")}, p_metadata
    )

    data.add_element({u"test-id": tid}, p_test)
    t_type = in_data.get(u"type", u"")
    t_type = u"NDRPDR" if t_type == u"CPS" else t_type  # It is NDRPDR
    data.add_element({u"test-type": t_type}, p_test)
    tags = in_data.get(u"tags", list())
    data.add_element({u"tags": tags}, p_test)
    data.add_element(
        {u"documentation": in_data.get(u"documentation", u"")}, p_test
    )
    execution = {
        u"start_time": in_data.get(u"starttime", u""),
        u"end_time": in_data.get(u"endtime", u""),
        u"status": in_data.get(u"status", u"FAILED"),
    }
    execution.update(metadata)
    data.add_element({u"execution": execution}, p_test)

    log_item = {
        u"source": {
            u"type": u"node",
            u"id": ""
        },
        u"msg-type": u"",
        u"log-level": u"INFO",
        u"timestamp": in_data.get(u"starttime", u""),  # replacement
        u"msg": u"",
        u"data": []
    }

    # Process configuration history:
    in_papi = deepcopy(in_data.get(u"conf-history", None))
    if in_papi:
        regex_dut = re.compile(r'\*\*DUT(\d):\*\*')
        node_id = u"dut1"
        for line in in_papi.split(u"\n"):
            if not line:
                continue
            groups = re.search(regex_dut, line)
            if groups:
                node_id = f"dut{groups.group(1)}"
            else:
                log_item[u"source"][u"id"] = node_id
                log_item[u"msg-type"] = u"papi"
                log_item[u"msg"] = line
                data.add_element(log_item, p_log)

    # Process show runtime:
    in_sh_run = deepcopy(in_data.get(u"show-run", None))
    if in_sh_run:
        # Transform to openMetrics format
        for key, val in in_sh_run.items():
            log_item[u"source"][u"id"] = key
            log_item[u"msg-type"] = u"metric"
            log_item[u"msg"] = u"show-runtime"
            log_item[u"data"] = list()
            for item in val.get(u"runtime", list()):
                for metric, m_data in item.items():
                    if metric == u"name":
                        continue
                    for idx, m_item in enumerate(m_data):
                        log_item[u"data"].append(
                            {
                                u"name": metric,
                                u"value": m_item,
                                u"labels": {
                                    u"host": val.get(u"host", u""),
                                    u"socket": val.get(u"socket", u""),
                                    u"graph-node": item.get(u"name", u""),
                                    u"thread-id": str(idx)
                                }
                            }
                        )
            data.add_element(log_item, p_log)

    # Process results:
    results = dict()
    if t_type == u"DEVICETEST":
        pass  # Nothing to add.
    elif t_type == u"NDRPDR":
        results = {
            u"throughput": {
                u"unit":
                    u"cps" if u"TCP_CPS" in tags or u"UDP_CPS" in tags
                    else u"pps",
                u"ndr": {
                    u"value": {
                        u"lower": in_data.get(u"throughput", dict()).
                                  get(u"NDR", dict()).
                                  get(u"LOWER", float(u"NaN")),
                        u"upper": in_data.get(u"throughput", dict()).
                                  get(u"NDR", dict()).
                                  get(u"UPPER", float(u"NaN"))
                    },
                    u"value_gbps": {
                        u"lower": in_data.get(u"gbps", dict()).
                                  get(u"NDR", dict()).
                                  get(u"LOWER", float(u"NaN")),
                        u"upper": in_data.get(u"gbps", dict()).
                                  get(u"NDR", dict()).
                                  get(u"UPPER", float(u"NaN"))
                    }
                },
                u"pdr": {
                    u"value": {
                        u"lower": in_data.get(u"throughput", dict()).
                                  get(u"PDR", dict()).
                                  get(u"LOWER", float(u"NaN")),
                        u"upper": in_data.get(u"throughput", dict()).
                                  get(u"PDR", dict()).
                                  get(u"UPPER", float(u"NaN"))
                    },
                    u"value_gbps": {
                        u"lower": in_data.get(u"gbps", dict()).
                                  get(u"PDR", dict()).
                                  get(u"LOWER", float(u"NaN")),
                        u"upper": in_data.get(u"gbps", dict()).
                                  get(u"PDR", dict()).
                                  get(u"UPPER", float(u"NaN"))
                    }
                }
            },
            u"hdrh": {
                u"forward": {
                    u"pdr-90": in_data.get(u"latency", dict()).
                               get(u"PDR90", dict()).
                               get(u"direction1", float(u"NaN")),
                    u"pdr-50": in_data.get(u"latency", dict()).
                               get(u"PDR50", dict()).
                               get(u"direction1", float(u"NaN")),
                    u"pdr-10": in_data.get(u"latency", dict()).
                               get(u"PDR10", dict()).
                               get(u"direction1", float(u"NaN")),
                    u"pdr-0": in_data.get(u"latency", dict()).
                              get(u"LAT0", dict()).
                              get(u"direction1", float(u"NaN"))
                },
                u"reverse": {
                    u"pdr-90": in_data.get(u"latency", dict()).
                               get(u"PDR90", dict()).
                               get(u"direction2", float(u"NaN")),
                    u"pdr-50": in_data.get(u"latency", dict()).
                               get(u"PDR50", dict()).
                               get(u"direction2", float(u"NaN")),
                    u"pdr-10": in_data.get(u"latency", dict()).
                               get(u"PDR10", dict()).
                               get(u"direction2", float(u"NaN")),
                    u"pdr-0": in_data.get(u"latency", dict()).
                              get(u"LAT0", dict()).
                              get(u"direction2", float(u"NaN"))
                }
            }
        }
    elif t_type == "MRR":
        results = {
            u"unit": u"pps",  # Old data use only pps
            u"samples": in_data.get(u"result", dict()).get(u"samples", list()),
            u"mrr": in_data.get(u"result", dict()).
                    get(u"receive-rate", float(u"NaN")),
            u"stdev": in_data.get(u"result", dict()).
                      get(u"receive-stdev", float(u"NaN"))
        }
    elif t_type == "SOAK":
        results = {
            u"critical-rate": {
                u"lower": in_data.get(u"throughput", dict()).
                          get(u"LOWER", float(u"NaN")),
                u"upper": in_data.get(u"throughput", dict()).
                          get(u"UPPER", float(u"NaN")),
            }
        }
    elif t_type == "HOSTSTACK":
        results = in_data.get(u"result", dict())
    # elif t_type == "TCP":  # Not used ???
    #     results = in_data.get(u"result", float(u"NaN"))
    elif t_type == "RECONF":
        results = {
            u"loss": in_data.get(u"result", dict()).
                     get(u"loss", float(u"NaN")),
            u"time": in_data.get(u"result", dict()).
                     get(u"time", float(u"NaN"))
        }
    else:
        pass
    data.add_element({u"results": results}, p_test)

    data.dump(out, indent=u"    ")


def convert_xml_to_json(spec, data):
    """Convert downloaded XML files into JSON.

    Procedure:
    - create one json file for each test,
    - gzip all json files one by one,
    - delete json files.

    :param spec: Specification read from the specification files.
    :param data: Input data parsed from output.xml files.
    :type spec: Specification
    :type data: InputData
    """

    logging.info(u"Converting downloaded XML files to JSON ...")

    template_name = spec.output.get(u"use-template", None)
    structure = spec.output.get(u"structure", u"tree")
    if template_name:
        with open(template_name, u"r") as file_handler:
            template = json.load(file_handler)
    else:
        template = None

    build_dir = spec.environment[u"paths"][u"DIR[BUILD,JSON]"]
    try:
        rmtree(build_dir)
    except FileNotFoundError:
        pass  # It does not exist

    os.mkdir(build_dir)

    for job, builds in data.data.items():
        logging.info(f"  Processing job {job}")
        if structure == "tree":
            os.makedirs(join(build_dir, job), exist_ok=True)
        for build_nr, build in builds.items():
            logging.info(f"  Processing build {build_nr}")
            if structure == "tree":
                os.makedirs(join(build_dir, job, build_nr), exist_ok=True)
            for test_id, test_data in build[u"tests"].items():
                logging.info(f"  Processing test {test_id}")
                if structure == "tree":
                    dirs = test_id.split(u".")[:-1]
                    name = test_id.split(u".")[-1]
                    os.makedirs(
                        join(build_dir, job, build_nr, *dirs), exist_ok=True
                    )
                    file_name = \
                        f"{join(build_dir, job, build_nr, *dirs, name)}.json"
                else:
                    file_name = join(
                        build_dir,
                        u'.'.join((job, build_nr, test_id, u'json'))
                    )
                suite_id = test_id.rsplit(u".", 1)[0].replace(u" ", u"_")
                _export_test_from_xml_to_json(
                    test_id, test_data, file_name, template,
                    {
                        u"ci": u"jenkins.fd.io",
                        u"job": job,
                        u"build": build_nr,
                        u"suite-id": suite_id,
                        u"suite-doc": build[u"suites"].get(suite_id, dict()).
                            get(u"doc", u""),
                        u"testbed": build[u"metadata"].get(u"testbed", u""),
                        u"sut-version": build[u"metadata"].get(u"version", u"")
                    }
                )

    # gzip the json files:
    for file in get_files(build_dir, u"json"):
        with open(file, u"rb") as src:
            with gzip.open(f"{file}.gz", u"wb") as dst:
                dst.writelines(src)
            os.remove(file)

    logging.info(u"Done.")
