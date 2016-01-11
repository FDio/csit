# Copyright (c) 2015 Cisco and/or its affiliates.
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
from ssh import SSH
from robot.api import logger
from constants import Constants

__all__ = ['VatExecutor']

class VatExecutor(object):

    __VAT_BIN = "vpe_api_test"

    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._ret_code = None

    def execute_script(self, vat_name, node, timeout=10, json_out=True):
        """Copy local_path script to node, execute it and return result.

        :param vat_name: name of the vat script file. Only the file name of
            the script is required, the resources path is prepended
            automatically.
        :param node: node to execute the VAT script on.
        :param timeout: seconds to allow the script to run.
        :param json_out: require json output.
        :return: (rc, stdout, stderr) tuple.
        """

        ssh = SSH()
        ssh.connect(node)

        remote_file_path = '{0}/{1}/{2}'.format(Constants.REMOTE_FW_DIR,
                Constants.RESOURCES_TPL_VAT, vat_name)
        #TODO this overwrites the output if the vat script has been used twice
        remote_file_out = remote_file_path + ".out"

        cmd = "sudo -S {vat} {json} < {input}".format(vat=self.__VAT_BIN,
                json="json" if json_out == True else "",
                input=remote_file_path)
        (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout)
        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

        logger.trace("Command '{0}' returned {1}'".format(cmd, self._ret_code))
        logger.trace("stdout: '{0}'".format(self._stdout))
        logger.trace("stderr: '{0}'".format(self._stderr))

        #TODO: download vpe_api_test output file
        #self._delete_files(node, remote_file_path, remote_file_out)

    def _delete_files(self, node, *files):
        ssh = SSH()
        ssh.connect(node)
        files = " ".join([str(x) for x in files])
        ssh.exec_command("rm {0}".format(files))

    def script_should_have_failed(self):
        if self._ret_code is None:
            raise Exception("First execute the script!")
        if self._ret_code == 0:
            raise AssertionError(
                    "Script execution passed, but failure was expected")

    def script_should_have_passed(self):
        if self._ret_code is None:
            raise Exception("First execute the script!")
        if self._ret_code != 0:
            raise AssertionError(
                    "Script execution failed, but success was expected")

    def get_script_stdout(self):
        return self._stdout

    def get_script_stderr(self):
        return self._stderr

