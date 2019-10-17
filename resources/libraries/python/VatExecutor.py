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

from os import remove

import resources.libraries.python.DUTSetup as PidLib

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import exec_cmd, scp_node

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
        if copy_on_execute:
            scp_node(node, vat_name, vat_name)
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
        ret, stdout, stderr = exec_cmd(node, cmd, sudo=True, timeout=timeout)

        self._ret_code = ret
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
