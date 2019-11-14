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

from robot.api import logger

from errors import PresentationError
from environment import Environment, clean_environment
from specification_parser import Specification
from input_data_parser import InputData
from generator_tables import generate_tables
from generator_plots import generate_plots
from generator_files import generate_files
from static_content import prepare_static_content
from generator_report import generate_report
from generator_CPTA import generate_cpta
from generator_alerts import Alerting, AlertingError


def parse_args():
    """Parse arguments from cmd line.

    :returns: Parsed arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--specification",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Specification YAML file.")
    parser.add_argument("-r", "--release",
                        default="master",
                        type=str,
                        help="Release string of the product.")
    parser.add_argument("-w", "--week",
                        default="1",
                        type=str,
                        help="Calendar week when the report is published.")
    parser.add_argument("-l", "--logging",
                        choices=["DEBUG", "INFO", "WARN", "ERROR"],
                        default="ERROR",
                        help="Logging level.")
    parser.add_argument("-f", "--force",
                        action='store_true',
                        help="Force removing the old build(s) if present.")

    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()

    logger.info("Application started.")
    try:
        spec = Specification(args.specification)
        spec.read_specification()
    except PresentationError:
        logger.error("Finished with error.")
        return 1

    if spec.output["output"] not in ("report", "CPTA"):
        logger.error("The output '{0}' is not supported.".
                     format(spec.output["output"]))
        return 1

    # ret_code = 1
    # try:
    env = Environment(spec.environment, args.force)
    env.set_environment()

    prepare_static_content(spec)

    data = InputData(spec)
    data.download_and_parse_data(repeat=1)

    generate_tables(spec, data)
    generate_plots(spec, data)
    generate_files(spec, data)

    if spec.output["output"] == "report":
        generate_report(args.release, spec, args.week)
        logger.info("Successfully finished.")
    elif spec.output["output"] == "CPTA":
        sys.stdout.write(generate_cpta(spec, data))
        try:
            alert = Alerting(spec)
            alert.generate_alerts()
        except AlertingError as err:
            logger.warn(repr(err))
        logger.info("Successfully finished.")
    ret_code = 0

    # except AlertingError as err:
    #     logger.error("Finished with an alerting error.")
    #     logger.error(repr(err))
    # except PresentationError as err:
    #     logger.error("Finished with an PAL error.")
    #     logger.error(repr(err))
    # except (KeyError, ValueError) as err:
    #     logger.error("Finished with an error.")
    #     logger.error(repr(err))
    # except Exception as err:
    #     logger.error("Finished with an unexpected error.")
    #     logger.error(repr(err))
    # finally:
    #     if spec is not None:
    #         clean_environment(spec.environment)
    #     return ret_code


if __name__ == '__main__':
    sys.exit(main())
