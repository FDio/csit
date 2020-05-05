# Copyright (c) 2018 Cisco and/or its affiliates.
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

from pal_errors import PresentationError


class Environment:
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

    def _make_dirs(self):
        """Create the directories specified in the 'make-dirs' part of
        'environment' section in the specification file.

        :raises: PresentationError if it is not possible to remove or create a
        directory.
        """

        if self._force:
            logging.info(u"Removing old build(s) ...")
            for directory in self._env[u"build-dirs"]:
                dir_to_remove = self._env[u"paths"][directory]
                if os.path.isdir(dir_to_remove):
                    try:
                        shutil.rmtree(dir_to_remove)
                        logging.info(f"  Removed: {dir_to_remove}")
                    except OSError:
                        raise PresentationError(
                            f"Cannot remove the directory {dir_to_remove}"
                        )
            logging.info(u"Done.")

        logging.info(u"Making directories ...")

        for directory in self._env[u"make-dirs"]:
            dir_to_make = self._env[u"paths"][directory]
            try:
                if os.path.isdir(dir_to_make):
                    logging.warning(
                        f"The directory {dir_to_make} exists, skipping."
                    )
                else:
                    os.makedirs(dir_to_make)
                    logging.info(f"  Created: {dir_to_make}")
            except OSError:
                raise PresentationError(
                    f"Cannot make the directory {dir_to_make}"
                )

        logging.info(u"Done.")

    def set_environment(self):
        """Set the environment.
        """

        self._make_dirs()


def clean_environment(env):
    """Clean the environment.

    :param env: Environment specification.
    :type env: dict
    """

    logging.info(u"Cleaning the environment ...")

    if not env[u"remove-dirs"]:  # None or empty
        logging.info(u"  No directories to remove.")
        return

    for directory in env[u"remove-dirs"]:
        dir_to_remove = env[u"paths"][directory]
        logging.info(f"  Removing the working directory {dir_to_remove} ...")
        if os.path.isdir(dir_to_remove):
            try:
                shutil.rmtree(dir_to_remove)
            except OSError as err:
                logging.warning(
                    f"Cannot remove the directory {dir_to_remove}"
                )
                logging.debug(str(err))
        else:
            logging.warning(f"The directory {dir_to_remove} does not exist.")

    logging.info(u"Done.")
