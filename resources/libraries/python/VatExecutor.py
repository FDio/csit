# Copyright (c) 2020 Cisco and/or its affiliates.
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

from os import remove

from paramiko.ssh_exception import SSHException
from robot.api import logger

import resources.libraries.python.DUTSetup as PidLib

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import SSH, SSHTimeout

__all__ = [u"VatExecutor"]


def cleanup_vat_json_output(json_output, vat_name=None):
    """Return VAT JSON output cleaned from VAT clutter.

    Clean up VAT JSON output from clutter like vat# prompts and such.

    :param json_output: Cluttered JSON output.
    :param vat_name: Name of the VAT script.
    :type json_output: JSON
    :type vat_name: str
    :returns: Cleaned up output JSON string.
    :rtype: JSON
    """

    retval = json_output
    clutter = [u"vat#", u"dump_interface_table error: Misc"]
    if vat_name:
        remote_file_path = f"{Constants.REMOTE_FW_DIR}/" \
            f"{Constants.RESOURCES_TPL_VAT}/{vat_name}"
        clutter.append(f"{remote_file_path}(2):")
    for garbage in clutter:
        retval = retval.replace(garbage, u"")
    return retval


def get_vpp_pid(node):
    """Get PID of running VPP process.

    :param node: DUT node.
    :type node: dict
    :returns: PID of VPP process / List of PIDs if more VPP processes are
        running on the DUT node.
    :rtype: int or list
    """
    pid = PidLib.DUTSetup.get_pid(node, u"vpp")
    return pid


class VatExecutor:
    """Contains methods for executing VAT commands on DUTs."""
    def __init__(self):
        self._stdout = None
        self._stderr = None
        self._ret_code = None
        self._script_name = None

    def execute_script(
            self, vat_name, node, timeout=120, json_out=True,
            copy_on_execute=False, history=True):
        """Execute VAT script on remote node, and store the result. There is an
        option to copy script from local host to remote host before execution.
        Path is defined automatically.

        :param vat_name: Name of the vat script file. Only the file name of
            the script is required, the resources path is prepended
            automatically.
        :param node: Node to execute the VAT script on.
        :param timeout: Seconds to allow the script to run.
        :param json_out: Require JSON output.
        :param copy_on_execute: If true, copy the file from local host to remote
            before executing.
        :param history: If true, add command to history.
        :type vat_name: str
        :type node: dict
        :type timeout: int
        :type json_out: bool
        :type copy_on_execute: bool
        :type history: bool
        :raises SSHException: If cannot open connection for VAT.
        :raises SSHTimeout: If VAT execution is timed out.
        :raises RuntimeError: If VAT script execution fails.
        """
        ssh = SSH()
        try:
            ssh.connect(node)
        except:
            raise SSHException(
                f"Cannot open SSH connection to execute VAT command(s) "
                f"from vat script {vat_name}"
            )

        if copy_on_execute:
            ssh.scp(vat_name, vat_name)
            remote_file_path = vat_name
            if history:
                with open(vat_name, u"rt") as vat_file:
                    for line in vat_file:
                        PapiHistory.add_to_papi_history(
                            node, line.replace(u"\n", u""), papi=False
                        )
        else:
            remote_file_path = f"{Constants.REMOTE_FW_DIR}/" \
                f"{Constants.RESOURCES_TPL_VAT}/{vat_name}"

        cmd = f"{Constants.VAT_BIN_NAME}" \
            f"{u' json' if json_out is True else u''} " \
            f"in {remote_file_path} script"
        try:
            ret_code, stdout, stderr = ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout
            )
        except SSHTimeout:
            logger.error(f"VAT script execution timeout: {cmd}")
            raise
        except Exception:
            raise RuntimeError(f"VAT script execution failed: {cmd}")

        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr
        self._script_name = vat_name

    def write_and_execute_script(
            self, node, tmp_fn, commands, timeout=300, json_out=False):
        """Write VAT commands to the script, copy it to node and execute it.

        :param node: VPP node.
        :param tmp_fn: Path to temporary file script.
        :param commands: VAT command list.
        :param timeout: Seconds to allow the script to run.
        :param json_out: Require JSON output.
        :type node: dict
        :type tmp_fn: str
        :type commands: list
        :type timeout: int
        :type json_out: bool
        """
        with open(tmp_fn, u"wt") as tmp_f:
            tmp_f.writelines(commands)

        self.execute_script(
            tmp_fn, node, timeout=timeout, json_out=json_out,
            copy_on_execute=True
        )
        remove(tmp_fn)

    def execute_script_json_out(self, vat_name, node, timeout=120):
        """Pass all arguments to 'execute_script' method, then cleanup returned
        json output.

        :param vat_name: Name of the vat script file. Only the file name of
            the script is required, the resources path is prepended
            automatically.
        :param node: Node to execute the VAT script on.
        :param timeout: Seconds to allow the script to run.
        :type vat_name: str
        :type node: dict
        :type timeout: int
        """
        self.execute_script(vat_name, node, timeout, json_out=True)
        self._stdout = cleanup_vat_json_output(self._stdout, vat_name=vat_name)

    def script_should_have_failed(self):
        """Read return code from last executed script and raise exception if the
        script didn't fail."""
        if self._ret_code is None:
            raise Exception(u"First execute the script!")
        if self._ret_code == 0:
            raise AssertionError(
                f"VAT Script execution passed, but failure was expected: "
                f"{self._script_name}"
            )

    def script_should_have_passed(self):
        """Read return code from last executed script and raise exception if the
        script failed."""
        if self._ret_code is None:
            raise Exception(u"First execute the script!")
        if self._ret_code != 0:
            raise AssertionError(
                f"VAT Script execution failed, but success was expected: "
                f"{self._script_name}"
            )

    def get_script_stdout(self):
        """Returns value of stdout from last executed script."""
        return self._stdout

    def get_script_stderr(self):
        """Returns value of stderr from last executed script."""
        return self._stderr

    @staticmethod
    def cmd_from_template(node, vat_template_file, json_param=True, **vat_args):
        """Execute VAT script on specified node. This method supports
        script templates with parameters.

        :param node: Node in topology on witch the script is executed.
        :param vat_template_file: Template file of VAT script.
        :param json_param: Require JSON mode.
        :param vat_args: Arguments to the template file.
        :returns: List of JSON objects returned by VAT.
        """
        with VatTerminal(node, json_param=json_param) as vat:
            return vat.vat_terminal_exec_cmd_from_template(
                vat_template_file, **vat_args
            )


class VatTerminal:
    """VAT interactive terminal.

    :param node: Node to open VAT terminal on.
    :param json_param: Defines if outputs from VAT are in JSON format.
        Default is True.
    :type node: dict
    :type json_param: bool

    """

    __VAT_PROMPT = (u"vat# ", )
    __LINUX_PROMPT = (u":~# ", u":~$ ", u"~]$ ", u"~]# ")

    def __init__(self, node, json_param=True):
        json_text = u" json" if json_param else u""
        self.json = json_param
        self._node = node
        self._ssh = SSH()
        self._ssh.connect(self._node)
        try:
            self._tty = self._ssh.interactive_terminal_open()
        except Exception:
            raise RuntimeError(
                f"Cannot open interactive terminal on node "
                f"{self._node[u'host']}"
            )

        for _ in range(3):
            try:
                self._ssh.interactive_terminal_exec_command(
                    self._tty, f"sudo -S {Constants.VAT_BIN_NAME}{json_text}",
                    self.__VAT_PROMPT
                )
            except Exception:
                continue
            else:
                break
        else:
            vpp_pid = get_vpp_pid(self._node)
            if vpp_pid:
                if isinstance(vpp_pid, int):
                    logger.trace(f"VPP running on node {self._node[u'host']}")
                else:
                    logger.error(
                        f"More instances of VPP running "
                        f"on node {self._node[u'host']}."
                    )
            else:
                logger.error(f"VPP not running on node {self._node[u'host']}.")
            raise RuntimeError(
                f"Failed to open VAT console on node {self._node[u'host']}"
            )

        self._exec_failure = False
        self.vat_stdout = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.vat_terminal_close()

    def vat_terminal_exec_cmd(self, cmd):
        """Execute command on the opened VAT terminal.

        :param cmd: Command to be executed.

        :returns: Command output in python representation of JSON format or
            None if not in JSON mode.
        """
        PapiHistory.add_to_papi_history(self._node, cmd, papi=False)
        logger.debug(f"Executing command in VAT terminal: {cmd}")
        try:
            out = self._ssh.interactive_terminal_exec_command(
                self._tty, cmd, self.__VAT_PROMPT
            )
            self.vat_stdout = out
        except Exception:
            self._exec_failure = True
            vpp_pid = get_vpp_pid(self._node)
            if not vpp_pid:
                msg = f"VPP not running on node {self._node[u'host']}. " \
                    f"VAT command {cmd} execution failed."
            elif len(vpp_pid) == 1:
                msg = f"VPP running on node {self._node[u'host']} " \
                    f"but VAT command {cmd} execution failed."
            else:
                msg = f"More instances of VPP running on node " \
                    f"{self._node[u'host']}. VAT command {cmd} " \
                    f"execution failed."

            raise RuntimeError(msg)

        logger.debug(f"VAT output: {out}")
        if self.json:
            obj_start = out.find(u"{")
            obj_end = out.rfind(u"}")
            array_start = out.find(u"[")
            array_end = out.rfind(u"]")

            if obj_start == -1 and array_start == -1:
                raise RuntimeError(f"VAT command {cmd}: no JSON data.")

            if obj_start < array_start or array_start == -1:
                start = obj_start
                end = obj_end + 1
            else:
                start = array_start
                end = array_end + 1
            out = out[start:end]
            json_out = json.loads(out)
            return json_out

        return None

    def vat_terminal_close(self):
        """Close VAT terminal."""
        # interactive terminal is dead, we only need to close session
        if not self._exec_failure:
            try:
                self._ssh.interactive_terminal_exec_command(
                    self._tty, u"quit", self.__LINUX_PROMPT
                )
            except Exception:
                vpp_pid = get_vpp_pid(self._node)
                if vpp_pid:
                    if isinstance(vpp_pid, int):
                        logger.trace(
                            f"VPP running on node {self._node[u'host']}."
                        )
                    else:
                        logger.error(
                            f"More instances of VPP running "
                            f"on node {self._node[u'host']}."
                        )
                else:
                    logger.error(
                        f"VPP not running on node {self._node[u'host']}."
                    )
                raise RuntimeError(
                    f"Failed to close VAT console "
                    f"on node {self._node[u'host']}"
                )
        try:
            self._ssh.interactive_terminal_close(self._tty)
        except Exception:
            raise RuntimeError(
                f"Cannot close interactive terminal "
                f"on node {self._node[u'host']}"
            )

    def vat_terminal_exec_cmd_from_template(self, vat_template_file, **args):
        """Execute VAT script from a file.

        :param vat_template_file: Template file name of a VAT script.
        :param args: Dictionary of parameters for VAT script.
        :returns: List of JSON objects returned by VAT.
        """
        file_path = f"{Constants.RESOURCES_TPL_VAT}/{vat_template_file}"

        with open(file_path, u"rt") as template_file:
            cmd_template = template_file.readlines()
        ret = list()
        for line_tmpl in cmd_template:
            vat_cmd = line_tmpl.format(**args)
            ret.append(self.vat_terminal_exec_cmd(vat_cmd.replace(u"\n", u"")))
        return ret
