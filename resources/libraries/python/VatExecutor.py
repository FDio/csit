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

"""VAT executor library."""

import json

from paramiko.ssh_exception import SSHException
from robot.api import logger

from resources.libraries.python.ssh import SSH, SSHTimeout
from resources.libraries.python.constants import Constants
from resources.libraries.python.VatHistory import VatHistory

__all__ = ['VatExecutor']


def cleanup_vat_json_output(json_output):
    """Return VAT JSON output cleaned from VAT clutter.

    Clean up VAT JSON output from clutter like vat# prompts and such.

    :param json_output: Cluttered JSON output.
    :returns: Cleaned up output JSON string.
    """

    retval = json_output
    clutter = ['vat#', 'dump_interface_table error: Misc']
    for garbage in clutter:
        retval = retval.replace(garbage, '')
    return retval


def get_vpp_pid(node):
    """Get PID of running VPP process.

    :param node: DUT node.
    :type node> dict
    :returns: PID of VPP process / List of PIDs if more VPP processes are
    running on the DUT node.
    :rtype: int or list
    """
    import resources.libraries.python.DUTSetup as PidLib
    pid = PidLib.DUTSetup.get_vpp_pid(node)
    return pid


class VatExecutor(object):
    """Contains methods for executing VAT commands on DUTs."""
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._ret_code = None

    def execute_script(self, vat_name, node, timeout=10, json_out=True):
        """Copy local_path script to node, execute it and return result.

        :param vat_name: Name of the vat script file. Only the file name of
        the script is required, the resources path is prepended automatically.
        :param node: Node to execute the VAT script on.
        :param timeout: Seconds to allow the script to run.
        :param json_out: Require JSON output.
        :type vat_name: str
        :type node: dict
        :type timeout: int
        :type json_out: bool
        :returns: (rc, stdout, stderr) tuple.
        """

        ssh = SSH()
        try:
            ssh.connect(node)
        except:
            raise SSHException("Cannot open SSH connection to execute VAT "
                               "command(s) from template {0}".format(vat_name))

        remote_file_path = '{0}/{1}/{2}'.format(Constants.REMOTE_FW_DIR,
                                                Constants.RESOURCES_TPL_VAT,
                                                vat_name)
        # TODO this overwrites the output if the vat script has been used twice
        # remote_file_out = remote_file_path + ".out"

        cmd = "sudo -S {vat} {json} in {input} script".format(
            vat=Constants.VAT_BIN_NAME,
            json="json" if json_out is True else "",
            input=remote_file_path)

        try:
            (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout)
        except SSHTimeout:
            logger.error("Command execution timeout: {0}".format(cmd))
            raise
        except:
            raise RuntimeError("Command execution failed: {0}".format(cmd))

        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

        # TODO: download vpp_api_test output file
        # self._delete_files(node, remote_file_path, remote_file_out)

    def scp_and_execute_script(self, vat_name, node, timeout=10, json_out=True):
        """Copy vat_name script to node, execute it and return result.

        :param vat_name: Name of the vat script file.
        Full path and name of the script is required.
        :param node: Node to execute the VAT script on.
        :param timeout: Seconds to allow the script to run.
        :param json_out: Require JSON output.
        :type vat_name: str
        :type node: dict
        :type timeout: int
        :type json_out: bool
        :returns: Status code, stdout and stderr of executed script
        :rtype: tuple
        """

        ssh = SSH()
        try:
            ssh.connect(node)
        except:
            raise SSHException("Cannot open SSH connection to execute VAT "
                               "command(s) from template {0}".format(vat_name))

        ssh.scp(vat_name, vat_name)

        cmd = "sudo -S {vat} {json} in {input} script".format(
            json="json" if json_out is True else "",
            vat=Constants.VAT_BIN_NAME,
            input=vat_name)

        try:
            (ret_code, stdout, stderr) = ssh.exec_command(cmd, timeout)
        except SSHTimeout:
            logger.error("Command execution timeout: {0}".format(cmd))
            raise
        except:
            raise RuntimeError("Command execution failed: {0}".format(cmd))

        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

        self._delete_files(node, vat_name)

    def scp_and_execute_cli_script(self, fname, node, timeout=10,
                                   json_out=True):
        """Copy vat_name script to node, execute it and return result.

        :param fname: Name of the VPP script file.
        Full path and name of the script is required.
        :param node: Node to execute the VPP script on.
        :param timeout: Seconds to allow the script to run.
        :param json_out: Require JSON output.
        :type fname: str
        :type node: dict
        :type timeout: int
        :type json_out: bool
        :returns: Status code, stdout and stderr of executed script
        :rtype: tuple
        """

        ssh = SSH()
        try:
            ssh.connect(node)
        except:
            raise SSHException("Cannot open SSH connection to execute CLI "
                               "command(s) from template {0}".format(fname))

        ssh.scp(fname, fname)

        cmd = "{vat} {json}".format(json="json" if json_out is True else "",
                                    vat=Constants.VAT_BIN_NAME)
        cmd_input = "exec exec {0}".format(fname)

        try:
            (ret_code, stdout, stderr) = ssh.exec_command_sudo(cmd, cmd_input,
                                                               timeout)
        except SSHTimeout:
            logger.error("Command execution timeout: {0}{1}".
                         format(cmd, "<<< " + cmd_input if cmd_input else ""))
            raise
        except:
            raise RuntimeError("Command execution failed: {0}{1}".format(
                cmd, "<<< " + cmd_input if cmd_input else ""))

        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

        self._delete_files(node, fname)

    def execute_script_json_out(self, vat_name, node, timeout=10):
        """Pass all arguments to 'execute_script' method, then cleanup returned
        json output.

         :param vat_name: Name of the vat script file. Only the file name of
        the script is required, the resources path is prepended automatically.
        :param node: Node to execute the VAT script on.
        :param timeout: Seconds to allow the script to run.
        :type vat_name: str
        :type node: dict
        :type timeout: int
        """
        self.execute_script(vat_name, node, timeout, json_out=True)
        self._stdout = cleanup_vat_json_output(self._stdout)

    @staticmethod
    def _delete_files(node, *files):
        """Use SSH to delete the specified files on node.

        :param node: Node in topology.
        :param files: Files to delete.
        :type node: dict
        :type files: iterable
        """

        ssh = SSH()
        ssh.connect(node)
        files = " ".join([str(x) for x in files])
        ssh.exec_command("rm {0}".format(files))

    def script_should_have_failed(self):
        """Read return code from last executed script and raise exception if the
        script didn't fail."""
        if self._ret_code is None:
            raise Exception("First execute the script!")
        if self._ret_code == 0:
            raise AssertionError(
                "Script execution passed, but failure was expected")

    def script_should_have_passed(self):
        """Read return code from last executed script and raise exception if the
        script failed."""
        if self._ret_code is None:
            raise Exception("First execute the script!")
        if self._ret_code != 0:
            raise AssertionError(
                "Script execution failed, but success was expected")

    def get_script_stdout(self):
        """Returns value of stdout from last executed script."""
        return self._stdout

    def get_script_stderr(self):
        """Returns value of stderr from last executed script."""
        return self._stderr

    @staticmethod
    def cmd_from_template(node, vat_template_file, **vat_args):
        """Execute VAT script on specified node. This method supports
        script templates with parameters.

        :param node: Node in topology on witch the script is executed.
        :param vat_template_file: Template file of VAT script.
        :param vat_args: Arguments to the template file.
        :return: List of JSON objects returned by VAT.
        """
        with VatTerminal(node) as vat:
            return vat.vat_terminal_exec_cmd_from_template(vat_template_file,
                                                           **vat_args)


class VatTerminal(object):
    """VAT interactive terminal.

    :param node: Node to open VAT terminal on.
    :param json_param: Defines if outputs from VAT are in JSON format.
    Default is True.
    :type node: dict
    :type json_param: bool

    """

    __VAT_PROMPT = ("vat# ", )
    __LINUX_PROMPT = (":~$ ", "~]$ ")

    def __init__(self, node, json_param=True):
        json_text = ' json' if json_param else ''
        self.json = json_param
        self._node = node
        self._ssh = SSH()
        self._ssh.connect(self._node)
        try:
            self._tty = self._ssh.interactive_terminal_open()
        except Exception:
            raise RuntimeError("Cannot open interactive terminal on node {0}".
                               format(self._node))

        for _ in range(3):
            try:
                self._ssh.interactive_terminal_exec_command(
                    self._tty,
                    'sudo -S {0}{1}'.format(Constants.VAT_BIN_NAME, json_text),
                    self.__VAT_PROMPT)
            except Exception:
                    continue
            else:
                break
        else:
            vpp_pid = get_vpp_pid(self._node)
            if vpp_pid:
                if isinstance(vpp_pid, int):
                    logger.trace("VPP running on node {0}".
                                 format(self._node['host']))
                else:
                    logger.error("More instances of VPP running on node {0}.".
                                 format(self._node['host']))
            else:
                logger.error("VPP not running on node {0}.".
                             format(self._node['host']))
            raise RuntimeError("Failed to open VAT console on node {0}".
                               format(self._node['host']))

        self._exec_failure = False
        self.vat_stdout = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.vat_terminal_close()

    def vat_terminal_exec_cmd(self, cmd):
        """Execute command on the opened VAT terminal.

        :param cmd: Command to be executed.

        :return: Command output in python representation of JSON format or
        None if not in JSON mode.
        """
        VatHistory.add_to_vat_history(self._node, cmd)
        logger.debug("Executing command in VAT terminal: {0}".format(cmd))
        try:
            out = self._ssh.interactive_terminal_exec_command(self._tty, cmd,
                                                              self.__VAT_PROMPT)
            self.vat_stdout = out
        except Exception:
            self._exec_failure = True
            vpp_pid = get_vpp_pid(self._node)
            if vpp_pid:
                if isinstance(vpp_pid, int):
                    raise RuntimeError("VPP running on node {0} but VAT command"
                                       " {1} execution failed.".
                                       format(self._node['host'], cmd))
                else:
                    raise RuntimeError("More instances of VPP running on node "
                                       "{0}. VAT command {1} execution failed.".
                                       format(self._node['host'], cmd))
            else:
                raise RuntimeError("VPP not running on node {0}. VAT command "
                                   "{1} execution failed.".
                                   format(self._node['host'], cmd))

        logger.debug("VAT output: {0}".format(out))
        if self.json:
            obj_start = out.find('{')
            obj_end = out.rfind('}')
            array_start = out.find('[')
            array_end = out.rfind(']')

            if obj_start == -1 and array_start == -1:
                raise RuntimeError("VAT command {0}: no JSON data.".format(cmd))

            if obj_start < array_start or array_start == -1:
                start = obj_start
                end = obj_end + 1
            else:
                start = array_start
                end = array_end + 1
            out = out[start:end]
            json_out = json.loads(out)
            return json_out
        else:
            return None

    def vat_terminal_close(self):
        """Close VAT terminal."""
        # interactive terminal is dead, we only need to close session
        if not self._exec_failure:
            try:
                self._ssh.interactive_terminal_exec_command(self._tty,
                                                            'quit',
                                                            self.__LINUX_PROMPT)
            except Exception:
                vpp_pid = get_vpp_pid(self._node)
                if vpp_pid:
                    if isinstance(vpp_pid, int):
                        logger.trace("VPP running on node {0}.".
                                     format(self._node['host']))
                    else:
                        logger.error("More instances of VPP running on node "
                                     "{0}.".format(self._node['host']))
                else:
                    logger.error("VPP not running on node {0}.".
                                 format(self._node['host']))
                raise RuntimeError("Failed to close VAT console on node {0}".
                                   format(self._node['host']))
        try:
            self._ssh.interactive_terminal_close(self._tty)
        except:
            raise RuntimeError("Cannot close interactive terminal on node {0}".
                               format(self._node['host']))

    def vat_terminal_exec_cmd_from_template(self, vat_template_file, **args):
        """Execute VAT script from a file.

        :param vat_template_file: Template file name of a VAT script.
        :param args: Dictionary of parameters for VAT script.
        :return: List of JSON objects returned by VAT.
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
