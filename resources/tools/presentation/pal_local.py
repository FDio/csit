# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""CSIT Presentation and analytics layer.
"""

import sys
import argparse
import logging

from pal_errors import PresentationError
from environment import Environment, clean_environment
from specification_parser import Specification
from input_data_parser import InputData
from generator_tables import generate_tables
from generator_plots import generate_plots
from generator_files import generate_files
from static_content import prepare_static_content
from generator_report import generate_report
from generator_cpta import generate_cpta
from generator_alerts import Alerting, AlertingError


def parse_args():
    """Parse arguments from cmd line.

    :returns: Parsed arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument(u"-s", u"--specification",
                        required=True,
                        type=argparse.FileType(u'r'),
                        help=u"Specification YAML file.")
    parser.add_argument(u"-r", u"--release",
                        default=u"master",
                        type=str,
                        help=u"Release string of the product.")
    parser.add_argument(u"-w", u"--week",
                        default=u"1",
                        type=str,
                        help=u"Calendar week when the report is published.")
    parser.add_argument(u"-l", u"--logging",
                        choices=[u"DEBUG", u"INFO", u"WARNING",
                                 u"ERROR", u"CRITICAL"],
                        default=u"ERROR",
                        help=u"Logging level.")
    parser.add_argument(u"-f", u"--force",
                        action=u"store_true",
                        help=u"Force removing the old build(s) if present.")
    parser.add_argument(u"-o", u"--print-all-oper-data",
                        action=u"store_true",
                        help=u"Print all operational data to console. Be "
                             u"careful, the output can be really long.")
    parser.add_argument(u"-i", u"--input",
                        required=True,
                        type=str,
                        help="Robot XML log file")

    return parser.parse_args()

def main():
    """Main function."""

    log_levels = {u"NOTSET": logging.NOTSET,
                  u"DEBUG": logging.DEBUG,
                  u"INFO": logging.INFO,
                  u"WARNING": logging.WARNING,
                  u"ERROR": logging.ERROR,
                  u"CRITICAL": logging.CRITICAL}

    args = parse_args()
    logging.basicConfig(format=u"%(asctime)s: %(levelname)s: %(message)s",
                        datefmt=u"%Y/%m/%d %H:%M:%S",
                        level=log_levels[args.logging])

    logging.info(u"Application started.")
    try:
        spec = Specification(args.specification)
        spec.read_specification()
    except PresentationError:
        logging.critical(u"Finished with error.")
        return 1

    ret_code = 1
    try:
        env = Environment(spec.environment, args.force)
        env.set_environment()

        data = InputData(spec)

        result = {
            u"data": data._parse_tests("local", {u"file-name": args.input}, list()),
            u"state": "processed",
            u"job": "local",
            u"build": {u"file-name": args.input}
        }
        import pandas as pd
        if result[u"data"]:
            ldata = result[u"data"]
            build_data = pd.Series({
                u"metadata": pd.Series(
                    list(ldata[u"metadata"].values()),
                    index=list(ldata[u"metadata"].keys())
                ),
                u"suites": pd.Series(
                    list(ldata[u"suites"].values()),
                    index=list(ldata[u"suites"].keys())
                ),
                u"tests": pd.Series(
                    list(ldata[u"tests"].values()),
                    index=list(ldata[u"tests"].keys())
                )
            })
        if data._input_data.get("local", None) is None:
            data._input_data["local"] = pd.Series()
        data._input_data["local"][str(1)] = build_data

        for job in data._input_data.values:
            for build in job.values:
                for test_id, test_data in build[u"tests"].items():
                    print(f"{test_id}")
                    if 'MRR' in test_data.get(u'tags'):
                        print(
                            f"{test_data[u'result'][u'receive-rate']}\n"
                        )
                    elif 'NDRPDR' in test_data.get(u'tags'):
                        print(
                            f"{test_data[u'troughput']}\n"
                    )

        if args.print_all_oper_data:
            data.print_all_oper_data()

        logging.info(u"Successfully finished.")
        ret_code = 0

    except AlertingError as err:
        logging.critical(f"Finished with an alerting error.\n{repr(err)}")
    except PresentationError as err:
        logging.critical(f"Finished with an PAL error.\n{repr(err)}")
    except (KeyError, ValueError) as err:
        logging.critical(f"Finished with an error.\n{repr(err)}")
    finally:
        if spec is not None:
            clean_environment(spec.environment)
    return ret_code


if __name__ == "__main__":
    sys.exit(main())
