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
"""

import os
import re
import json
import logging

from os.path import join
from shutil import rmtree
from copy import deepcopy
from pprint import pprint, pformat


class JSONData:
    """A Class storing and manipulating data from tests.

    TODO: Move to a dedicated file???
    """

    def __init__(self, template=None):
        """

        :param template:
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
        return self._data

    def add_element(self, value, path_to_value):
        """

        :param value: Element value.
        :param path_to_value: List of tuples where the first item is the element
            on the path and the second one is its type.
        :type value: dict, list, str, int, float, bool
        :type path_to_value: list
        :raises: IndexError if the path is empty.
        :raises: TypeError if the val is of not supported type.
        """

        def _add_element(val, path, structure):
            """

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

        if not (isinstance(value, dict) or isinstance(value, list) or
                isinstance(value, str) or isinstance(value, int) or
                isinstance(value, float) or isinstance(value, bool)):
            raise TypeError(
                u"The value must be one of these types: dict, list, str, int, "
                u"float, bool.\n"
                f"Value: {value}\n"
                f"Path: {path_to_value}"
            )
        _add_element(deepcopy(value), path_to_value, self._data)

    def get_element(self, path):
        """

        :param path: List of keys and indices to the requested element or
            sub-tree.
        :type path: list
        :returns:
        """
        raise NotImplementedError

    def dump(self, file_out):
        """Write JSON data to a file.

        :param file_out: Path to the output JSON file.
        :type file_out: str
        """
        with open(file_out, u"w") as file_handler:
            json.dump(self._data, file_handler)

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
    """

    :param tid: Test ID.
    :param in_data: Test data.
    :param out: Path to output json file.
    :param template: JSON template.
    :param metadata: Data which are not stored in XML structure.
    :return:
    """

    p_test = [(u"test", dict), ]

    data = JSONData(template=template)
    data.add_element({u"test-id": tid}, p_test)
    t_type = in_data.get(u"type", u"")
    data.add_element({u"test-type": t_type}, p_test)
    data.add_element({u"tags": in_data.get(u"tags", list())}, p_test)
    data.add_element(
        {u"documentation": in_data.get(u"documentation", u"")}, p_test
    )
    execution = {
        u"ci": metadata.get(u"ci", u""),
        u"job": metadata.get(u"job", u""),
        u"build": metadata.get(u"build", u""),
        u"start_time": in_data.get(u"starttime", u""),
        u"end_time": in_data.get(u"endtime", u""),
        u"status": in_data.get(u"status", u"FAILED"),
    }
    data.add_element({u"execution": execution}, p_test)

    # Process configuration history:
    in_papi = in_data.get(u"conf-history", None)
    if in_papi:
        p_log = [(u"log", list), (-1, list)]
        papi_item = {
            u"source": {
                u"type": u"node",
                u"id": ""
            },
            u"msg-type": u"papi",
            u"log-level": u"INFO",
            u"timestamp": in_data.get(u"starttime", u""),  # replacement
            u"msg": u"",
            u"data": {}
        }
        regex_dut = re.compile(r'\*\*DUT(\d):\*\*')
        node_id = u"dut1"
        for line in in_papi.split(u"\n"):
            if not line:
                continue
            groups = re.search(regex_dut, line)
            if groups:
                node_id = f"dut{groups.group(1)}"
            else:
                papi_item[u"source"][u"id"] = node_id
                papi_item[u"msg"] = line
                data.add_element(papi_item, p_log)

    # Process show runtime:
    in_sh_run = in_data.get(u"runtime", None)
    if in_sh_run:
        p_nodes = p_test + [(u"node", dict), ]
        data.add_element(in_sh_run, p_nodes)

    # Process results:
    results = dict()
    if t_type == u"DEVICETEST":
        pass  # Nothing to add.
    elif t_type == u"NDRPDR":
        results = {
            u"ndr": {
                u"value_pps": {
                    u"lower": in_data.get(u"throughput", dict()).
                    get(u"NDR", dict()).get(u"LOWER", float(u"NaN")),
                    u"upper": in_data.get(u"throughput", dict()).
                    get(u"NDR", dict()).get(u"UPPER", float(u"NaN"))
                },
                u"value_gbps": {
                    u"lower": in_data.get(u"gbps", dict()).
                    get(u"NDR", dict()).get(u"LOWER", float(u"NaN")),
                    u"upper": in_data.get(u"gbps", dict()).
                    get(u"NDR", dict()).get(u"UPPER", float(u"NaN"))
                }
            },
            u"pdr": {
                u"value_pps": {
                    u"lower": in_data.get(u"throughput", dict()).
                    get(u"PDR", dict()).get(u"LOWER", float(u"NaN")),
                    u"upper": in_data.get(u"throughput", dict()).
                    get(u"PDR", dict()).get(u"UPPER", float(u"NaN"))
                },
                u"value_gbps": {
                    u"lower": in_data.get(u"gbps", dict()).
                    get(u"PDR", dict()).get(u"LOWER", float(u"NaN")),
                    u"upper": in_data.get(u"gbps", dict()).
                    get(u"PDR", dict()).get(u"UPPER", float(u"NaN"))
                }
            },
            u"hdrh": {
                u"forward": {
                    u"pdr-90": in_data.get(u"latency", dict()).
                    get(u"PDR90", dict()).get(u"direction1", float(u"NaN")),
                    u"pdr-50": in_data.get(u"latency", dict()).
                    get(u"PDR50", dict()).get(u"direction1", float(u"NaN")),
                    u"pdr-10": in_data.get(u"latency", dict()).
                    get(u"PDR10", dict()).get(u"direction1", float(u"NaN")),
                    u"pdr-0": in_data.get(u"latency", dict()).
                    get(u"LAT0", dict()).get(u"direction1", float(u"NaN"))
                },
                u"reverse": {
                    u"pdr-90": in_data.get(u"latency", dict()).
                    get(u"PDR90", dict()).get(u"direction2", float(u"NaN")),
                    u"pdr-50": in_data.get(u"latency", dict()).
                    get(u"PDR50", dict()).get(u"direction2", float(u"NaN")),
                    u"pdr-10": in_data.get(u"latency", dict()).
                    get(u"PDR10", dict()).get(u"direction2", float(u"NaN")),
                    u"pdr-0": in_data.get(u"latency", dict()).
                    get(u"LAT0", dict()).get(u"direction2", float(u"NaN"))
                }
            }
        }
    elif t_type == "MRR" or t_type == "MRR":
        pass
    elif t_type == "SOAK":
        pass
    elif t_type == "HOSTSTACK":
        pass
    elif t_type == "TCP":
        pass
    elif t_type == "RECONF":
        pass
    else:
        pass
    p_results = p_test + [(u"results", dict), ]
    data.add_element({u"test": results}, p_results)

    data.dump(out)


def convert_xml_to_json(spec, data):
    """Convert downloaded XML files into JSON.
    """

    logging.info(u"Converting downloaded XML files to JSON ...")

    template_name = spec.output.get(u"use-template", None)
    structure = spec.output.get(u"structure", u"flat")
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
                    file_name = f"{join(build_dir, job, build_nr, test_id)}.json"
                else:
                    file_name = f"{join(build_dir, u'.'.join((job, build_nr, test_id, u'json')))}"
                metadata ={"ci": "jenkins.fd.io", "job": job, "build": build_nr}
                _export_test_from_xml_to_json(test_id, test_data, file_name, template, metadata)

    logging.info(u"Done.")
