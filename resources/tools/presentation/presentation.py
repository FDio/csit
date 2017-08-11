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

"""CSIT Presentation and analytics layer.
"""

import sys
import argparse
import logging

from errors import PresentationError
from environment import Environment, clean_environment
from configuration import Configuration
from inputs import download_data_files, unzip_files
from data import InputData
from tables import generate_tables
from plots import generate_plots
from files import generate_files
from static_content import prepare_static_content


def parse_args():
    """Parse arguments from cmd line.

    :returns: Parsed arguments.
    :rtype: ArgumentParser
    """

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.
                                     RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--configuration",
                        required=True,
                        type=argparse.FileType('r'),
                        help="Configuration YAML file.")
    parser.add_argument("-l", "--logging",
                        choices=["DEBUG", "INFO", "WARNING",
                                 "ERROR", "CRITICAL"],
                        default="ERROR",
                        help="Logging level.")
    parser.add_argument("-f", "--force",
                        action='store_true',
                        help="Force removing the old build(s) if present.")

    return parser.parse_args()


def main():
    """Main function."""

    log_levels = {"NOTSET": logging.NOTSET,
                  "DEBUG": logging.DEBUG,
                  "INFO": logging.INFO,
                  "WARNING": logging.WARNING,
                  "ERROR": logging.ERROR,
                  "CRITICAL": logging.CRITICAL}

    args = parse_args()
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                        level=log_levels[args.logging])

    logging.info("Application started.")
    try:
        config = Configuration(args.configuration)
        config.read_configuration()
    except PresentationError:
        logging.critical("Finished with error.")
        sys.exit(1)

    try:
        env = Environment(config.environment, args.force)
        env.set_environment()

        if config.is_debug:
            if config.debug["input-format"] == "zip":
                unzip_files(config)
        else:
            download_data_files(config)

        prepare_static_content(config.static)

        data = InputData(config)
        data.read_data()

        generate_tables(config, data)
        generate_plots(config, data)
        generate_files(config, data)

        logging.info("Successfully finished.")

    except (KeyError, ValueError, PresentationError) as err:
        logging.info("Finished with an error.")
        logging.critical(str(err))
    except Exception as err:
        logging.info("Finished with an error.")
        logging.critical(str(err))

    finally:
        if config is not None and not config.is_debug:
            clean_environment(config.environment)
        sys.exit(1)


if __name__ == '__main__':
    main()
