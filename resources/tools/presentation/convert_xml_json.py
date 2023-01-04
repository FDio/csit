# Copyright (c) 2023 Cisco and/or its affiliates.
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
Date:    22nd June 2021

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
from json import loads

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

    def update(self, kwargs):
        """Update the data with new data from the dictionary.

        :param kwargs: Key value pairs to be added to the data.
        :type kwargs: dict
        """
        self._data.update(kwargs)

    def set_key(self, key, val):
        """Setter.

        :param key: The key to be updated / added.
        :param val: The key value.
        :type key: str
        :type val: object
        """
        self._data[key] = deepcopy(val)

    def add_to_list(self, key, val):
        """Add an item to the list identified by key.

        :param key: The key identifying the list.
        :param val: The val to be appended to the list. If val is a list,
            extend is used.
        """
        if self._data.get(key, None) is None:
            self._data[key] = list()
        if isinstance(val, list):
            self._data[key].extend(val)
        else:
            self._data[key].append(val)

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

    data = JSONData(template=template)

    data.update(metadata)
    data.set_key(u"test_id", tid)
    t_type = in_data.get(u"type", u"")
    t_type = u"NDRPDR" if t_type == u"CPS" else t_type  # It is NDRPDR
    data.set_key(u"test_type", t_type)
    tags = in_data.get(u"tags", list())
    data.set_key(u"tags", tags)
    data.set_key(u"documentation", in_data.get(u"documentation", u""))
    data.set_key(u"message", in_data.get(u"msg", u""))
    data.set_key(u"start_time", in_data.get(u"starttime", u""))
    data.set_key(u"end_time", in_data.get(u"endtime", u""))
    data.set_key(u"status", in_data.get(u"status", u"FAILED"))
    sut_type = u""
    if u"vpp" in tid:
        sut_type = u"vpp"
    elif u"dpdk" in tid:
        sut_type = u"dpdk"
    data.set_key(u"sut_type", sut_type)

    # Process configuration history:
    in_papi = deepcopy(in_data.get(u"conf_history", None))
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
                data.add_to_list(
                    u"log",
                    {
                        u"source_type": u"node",
                        u"source_id": node_id,
                        u"msg_type": u"papi",
                        u"log_level": u"INFO",
                        u"timestamp": in_data.get(u"starttime", u""),
                        u"msg": line,
                        u"data": list()
                    }
                )

    # Process show runtime:
    if in_data.get(u"telemetry-show-run", None):
        for item in in_data[u"telemetry-show-run"].values():
            data.add_to_list(u"log", item.get(u"runtime", dict()))
    else:
        in_sh_run = deepcopy(in_data.get(u"show-run", None))
        if in_sh_run:
            # Transform to openMetrics format
            for key, val in in_sh_run.items():
                log_item = {
                    u"source_type": u"node",
                    u"source_id": key,
                    u"msg_type": u"metric",
                    u"log_level": u"INFO",
                    u"timestamp": in_data.get(u"starttime", u""),
                    u"msg": u"show_runtime",
                    u"data": list()
                }
                runtime = loads(val.get(u"runtime", list()))
                for item in runtime:
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
                                        u"graph_node": item.get(u"name", u""),
                                        u"thread_id": str(idx)
                                    }
                                }
                            )
                data.add_to_list(u"log", log_item)

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
                                  get(u"NDR", dict()).get(u"LOWER", u"NaN"),
                        u"upper": in_data.get(u"throughput", dict()).
                                  get(u"NDR", dict()).get(u"UPPER", u"NaN")
                    },
                    u"value_gbps": {
                        u"lower": in_data.get(u"gbps", dict()).
                                  get(u"NDR", dict()).get(u"LOWER", u"NaN"),
                        u"upper": in_data.get(u"gbps", dict()).
                                  get(u"NDR", dict()).get(u"UPPER", u"NaN")
                    }
                },
                u"pdr": {
                    u"value": {
                        u"lower": in_data.get(u"throughput", dict()).
                                  get(u"PDR", dict()).get(u"LOWER", u"NaN"),
                        u"upper": in_data.get(u"throughput", dict()).
                                  get(u"PDR", dict()).get(u"UPPER", u"NaN")
                    },
                    u"value_gbps": {
                        u"lower": in_data.get(u"gbps", dict()).
                                  get(u"PDR", dict()).get(u"LOWER", u"NaN"),
                        u"upper": in_data.get(u"gbps", dict()).
                                  get(u"PDR", dict()).get(u"UPPER", u"NaN")
                    }
                }
            },
            u"latency": {
                u"forward": {
                    u"pdr_90": in_data.get(u"latency", dict()).
                               get(u"PDR90", dict()).get(u"direction1", u"NaN"),
                    u"pdr_50": in_data.get(u"latency", dict()).
                               get(u"PDR50", dict()).get(u"direction1", u"NaN"),
                    u"pdr_10": in_data.get(u"latency", dict()).
                               get(u"PDR10", dict()).get(u"direction1", u"NaN"),
                    u"pdr_0": in_data.get(u"latency", dict()).
                              get(u"LAT0", dict()).get(u"direction1", u"NaN")
                },
                u"reverse": {
                    u"pdr_90": in_data.get(u"latency", dict()).
                               get(u"PDR90", dict()).get(u"direction2", u"NaN"),
                    u"pdr_50": in_data.get(u"latency", dict()).
                               get(u"PDR50", dict()).get(u"direction2", u"NaN"),
                    u"pdr_10": in_data.get(u"latency", dict()).
                               get(u"PDR10", dict()).get(u"direction2", u"NaN"),
                    u"pdr_0": in_data.get(u"latency", dict()).
                              get(u"LAT0", dict()).get(u"direction2", u"NaN")
                }
            }
        }
    elif t_type == "MRR":
        results = {
            u"unit": u"pps",  # Old data use only pps
            u"samples": in_data.get(u"result", dict()).get(u"samples", list()),
            u"avg": in_data.get(u"result", dict()).get(u"receive-rate", u"NaN"),
            u"stdev": in_data.get(u"result", dict()).
                      get(u"receive-stdev", u"NaN")
        }
    elif t_type == "SOAK":
        results = {
            u"critical_rate": {
                u"lower": in_data.get(u"throughput", dict()).
                          get(u"LOWER", u"NaN"),
                u"upper": in_data.get(u"throughput", dict()).
                          get(u"UPPER", u"NaN"),
            }
        }
    elif t_type == "HOSTSTACK":
        results = in_data.get(u"result", dict())
    # elif t_type == "TCP":  # Not used ???
    #     results = in_data.get(u"result", u"NaN")
    elif t_type == "RECONF":
        results = {
            u"loss": in_data.get(u"result", dict()).get(u"loss", u"NaN"),
            u"time": in_data.get(u"result", dict()).get(u"time", u"NaN")
        }
    else:
        pass
    data.set_key(u"results", results)

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
                groups = re.search(re.compile(r'-(\d+[tT](\d+[cC]))-'), test_id)
                if groups:
                    test_id = test_id.replace(groups.group(1), groups.group(2))
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
                        u"build_number": build_nr,
                        u"suite_id": suite_id,
                        u"suite_doc": build[u"suites"].get(suite_id, dict()).
                                      get(u"doc", u""),
                        u"testbed": build[u"metadata"].get(u"testbed", u""),
                        u"sut_version": build[u"metadata"].get(u"version", u"")
                    }
                )

    # gzip the json files:
    for file in get_files(build_dir, u"json"):
        with open(file, u"rb") as src:
            with gzip.open(f"{file}.gz", u"wb") as dst:
                dst.writelines(src)
            os.remove(file)

    logging.info(u"Done.")
