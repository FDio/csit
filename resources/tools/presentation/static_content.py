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

"""Static content

Process the static content stored in the git.
"""

import logging

from os.path import isdir
from os import makedirs
from shutil import rmtree, copytree, Error

from errors import PresentationError


def prepare_static_content(config):
    """Prepare the static content which is stored in the git.

    :param config: Configuration read from the specification file.
    :type config: Configuration
    :raises PresentationError: If it is not possible to process the static
    content.
    """

    src = config.static["src-path"]
    dst = config.static["dst-path"]

    # Copy all the static content to the build directory:
    logging.info("Copying the static content ...")
    logging.info("  Source:      {0}".format(src))
    logging.info("  Destination: {0}".format(dst))

    try:
        if isdir(dst):
            rmtree(dst)

        copytree(src, dst)

        for directory in config.environment["make-dirs"]:
            dir_to_make = config.environment["paths"][directory]
            if not isdir(dir_to_make):
                makedirs(dir_to_make)
                logging.info("  Created: {}".format(dir_to_make))

    except (Error, OSError) as err:
        raise PresentationError("Not possible to process the static content.",
                                str(err))

    logging.info("Done.")
