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

from os import makedirs
from os.path import isdir
from shutil import rmtree, copytree, Error

from pal_errors import PresentationError


def prepare_static_content(spec):
    """Prepare the static content which is stored in the git.

    :param spec: Specification read from the specification file.
    :type spec: Specification
    :raises PresentationError: If it is not possible to process the static
        content.
    """

    src = spec.static.get(u"src-path", None)
    dst = spec.static.get(u"dst-path", None)
    if src is None or dst is None:
        logging.warning(u"No static content specified, skipping")
        return

    # Copy all the static content to the build directory:
    logging.info(u"Copying the static content ...")
    logging.info(f"  Source:      {src}")
    logging.info(f"  Destination: {dst}")

    try:
        if isdir(dst):
            rmtree(dst)

        copytree(src, dst)

        makedirs(spec.environment[u"paths"][u"DIR[WORKING,SRC,STATIC]"])

    except (Error, OSError) as err:
        raise PresentationError(
            u"Not possible to process the static content.",
            repr(err)
        )

    logging.info(u"Done.")
