# Copyright (c) 2020 PANTHEON.tech and/or its affiliates.
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

""" File Locking Utilities """

from robot.api import logger

import fcntl


class FileLock:
    """ Simple File Locking class """

    def __init__(self, node, lock_file_path):
        """Open and lock a file when initializing the object. If the file is
        None, don't lock anything.

        :param lock_file_path: The path to the lock file.
        :type lock_file_path: str
        """
        self.node = node
        if lock_file_path:
            logger.trace("Acquiring lock on {}".format(lock_file_path))
            import os
            if os.path.exists(os.path.dirname(lock_file_path)):
                logger.trace("dir contents: {}".format(os.listdir(os.path.dirname(lock_file_path))))
            else:
                logger.trace("{} does not exist".format(os.path.dirname(lock_file_path)))
            self.lock_file = open(lock_file_path, mode='w')
            fcntl.lockf(self.lock_file, fcntl.LOCK_EX)
        else:
            self.lock_file = None

    def __enter__(self):
        """Return the lock file upon entering the with statement."""
        return self.lock_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close and unlock the locked file when exiting the with statement."""
        if self.lock_file:
            logger.trace("Releasing lock on {}".format(self.lock_file.name))
            self.lock_file.close()
            fcntl.lockf(self.lock_file, fcntl.LOCK_UN)
