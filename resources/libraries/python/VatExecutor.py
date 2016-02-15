# Copyright (c) 2016 Cisco and/or its affiliates.
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
import json

__all__ = ['VatExecutor']


def cleanup_vat_json_output(json_output):
    """Return VAT json output cleaned from VAT clutter.

    Clean up VAT json output from clutter like vat# prompts and such
    :param json_output: cluttered json output.
    :return: cleaned up output json string
    """

    retval = json_output
    clutter = ['vat#', 'dump_interface_table error: Misc']
    for garbage in clutter:
        retval = retval.replace(garbage, '')
    return retval


class VatExecutor(object):

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
                                                Constants.RESOURCES_TPL_VAT,
                                                vat_name)
        # TODO this overwrites the output if the vat script has been used twice
        remote_file_out = remote_file_path + ".out"

        cmd = "sudo -S {vat} {json} < {input}".format(
            vat=Constants.VAT_BIN_NAME,
            json="json" if json_out is True else "",
            input=remote_file_path)
        (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout)
        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

        logger.trace("Command '{0}' returned {1}'".format(cmd, self._ret_code))
        logger.trace("stdout: '{0}'".format(self._stdout))
        logger.trace("stderr: '{0}'".format(self._stderr))

        # TODO: download vpe_api_test output file
        # self._delete_files(node, remote_file_path, remote_file_out)

    def execute_script_json_out(self, vat_name, node, timeout=10,):
        self.execute_script(vat_name, node, timeout, json_out=True)
        self._stdout = cleanup_vat_json_output(self._stdout)

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

    @staticmethod
    def cmd_from_template(node, vat_template_file, **vat_args):
        """Execute VAT script on specified node. This method supports
         script templates with parameters
        :param node: node in topology on witch the scrtipt is executed
        :param vat_template_file: template file of VAT script
        :param vat_args: arguments to the template file
        :return: list of json objects returned by VAT
        """
        vat = VatTerminal(node)
        ret = vat.vat_terminal_exec_cmd_from_template(vat_template_file,
                                                      **vat_args)
        vat.vat_terminal_close()
        return ret

    @staticmethod
    def copy_config_to_remote(node, local_path, remote_path):
        # TODO: will be removed once v4 is merged to master.
        """Copies vat configuration file to node

        :param node: Remote node on which to copy the VAT configuration file
        :param local_path: path of the VAT script on local device that launches
        test cases.
        :param remote_path: path on remote node where to copy the VAT
        configuration script file
        """
        ssh = SSH()
        ssh.connect(node)
        logger.trace("Removing old file {}".format(remote_path))
        ssh.exec_command_sudo("rm -f {}".format(remote_path))
        ssh.scp(local_path, remote_path)


class VatTerminal(object):
    """VAT interactive terminal

       :param node: Node to open VAT terminal on.
    """

    __VAT_PROMPT = "vat# "
    __LINUX_PROMPT = ":~$ "

    def __init__(self, node):
        self._ssh = SSH()
        self._ssh.connect(node)
        self._tty = self._ssh.interactive_terminal_open()
        self._ssh.interactive_terminal_exec_command(
            self._tty,
            'sudo -S {vat} json'.format(vat=Constants.VAT_BIN_NAME),
            self.__VAT_PROMPT)

    def vat_terminal_exec_cmd(self, cmd):
        """Execute command on the opened VAT terminal.

           :param cmd: Command to be executed.

           :return: Command output in python representation of JSON format.
        """
        logger.debug("Executing command in VAT terminal: {}".format(cmd));
        out = self._ssh.interactive_terminal_exec_command(self._tty,
                                                          cmd,
                                                          self.__VAT_PROMPT)
        logger.debug("VAT output: {}".format(out));
        json_out = json.loads(out)
        return json_out

    def vat_terminal_close(self):
        """Close VAT terminal."""
        self._ssh.interactive_terminal_exec_command(self._tty,
                                                    'quit',
                                                    self.__LINUX_PROMPT)
        self._ssh.interactive_terminal_close(self._tty)

    def vat_terminal_exec_cmd_from_template(self, vat_template_file, **args):
        """Execute VAT script from a file.
        :param vat_template_file: template file name of a VAT script
        :param args: dictionary of parameters for VAT script
        :return: list of json objects returned by VAT
        """
        file_path = '{}/{}'.format(Constants.RESOURCES_TPL_VAT,
                                   vat_template_file)
        with open(file_path, 'r') as template_file:
            cmd_template = template_file.readlines()
        ret = []
        for line_tmpl in cmd_template:
            vat_cmd = line_tmpl.format(**args)
            ret.append(self.vat_terminal_exec_cmd(vat_cmd.replace('\n', '')))
        return ret
