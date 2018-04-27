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

"""Environment

Setting of the environment according to the specification specified in the
specification YAML file.
"""

import os
import shutil
import logging

from errors import PresentationError


class Environment(object):
    """Setting of the environment:
    - set environment variables,
    - create directories.
    """

    def __init__(self, env, force=False):
        """Initialization.

        :param env: Environment specification.
        :param force: If True, remove old build(s) if present.
        :type env: dict
        :type force: bool
        """

        self._env = env
        self._force = force

    @property
    def environment(self):
        """Getter.

        :returns: Environment settings.
        :rtype: dict
        """
        return self._env

    def _set_environment_variables(self):
        """Set environment variables.
        """
        logging.info("Setting the environment variables ...")
        # logging.debug("Environment variables before:\n{}".format(os.environ))

        count = 1

        for var, value in self._env["configuration"].items():
            logging.debug("  {:3d} Setting the variable {} = {}".
                          format(count, var, value))
            os.environ[var] = str(value)
            count += 1

        for var, value in self._env["paths"].items():
            logging.debug("  {:3d} Setting the variable {} = {}".
                          format(count, var, value))
            os.environ[var] = str(value)
            count += 1

        for var, value in self._env["urls"].items():
            logging.debug("  {:3d} Setting the variable {} = {}".
                          format(count, var, value))
            os.environ[var] = str(value)
            count += 1

        # logging.debug("Environment variables after:\n{}".format(os.environ))
        logging.info("Done.")

    def _make_dirs(self):
        """Create the directories specified in the 'make-dirs' part of
        'environment' section in the specification file.

        :raises: PresentationError if it is not possible to remove or create a
        directory.
        """

        if self._force:
            logging.info("Removing old build(s) ...")
            for directory in self._env["build-dirs"]:
                dir_to_remove = self._env["paths"][directory]
                if os.path.isdir(dir_to_remove):
                    try:
                        shutil.rmtree(dir_to_remove)
                        logging.info("  Removed: {}".format(dir_to_remove))
                    except OSError:
                        raise PresentationError("Cannot remove the directory "
                                                "'{}'".format(dir_to_remove))
            logging.info("Done.")

        logging.info("Making directories ...")

        for directory in self._env["make-dirs"]:
            dir_to_make = self._env["paths"][directory]
            try:
                if os.path.isdir(dir_to_make):
                    logging.warning("The directory '{}' exists, skipping.".
                                    format(dir_to_make))
                else:
                    os.makedirs(dir_to_make)
                    logging.info("  Created: {}".format(dir_to_make))
            except OSError:
                raise PresentationError("Cannot make the directory '{}'".
                                        format(dir_to_make))

        logging.info("Done.")

    def set_environment(self):
        """Set the environment.
        """

        self._set_environment_variables()
        self._make_dirs()


def clean_environment(env):
    """Clean the environment.

    :param env: Environment specification.
    :type env: dict
    :raises: PresentationError if it is not possible to remove a directory.
    """

    logging.info("Cleaning the environment ...")

    if not env["remove-dirs"]:  # None or empty
        logging.info("  No directories to remove.")
        return

    for directory in env["remove-dirs"]:
        dir_to_remove = env["paths"][directory]
        logging.info("  Removing the working directory {} ...".
                     format(dir_to_remove))
        if os.path.isdir(dir_to_remove):
            try:
                shutil.rmtree(dir_to_remove)
            except OSError:
                pass
                # raise PresentationError("Cannot remove the directory '{}'".
                #                         format(dir_to_remove))
        else:
            logging.warning("The directory '{}' does not exist.".
                            format(dir_to_remove))

    logging.info("Done.")
