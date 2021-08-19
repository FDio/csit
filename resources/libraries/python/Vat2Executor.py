# Copyright (c) 2021 Cisco and/or its affiliates.
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

from paramiko.ssh_exception import SSHException
from robot.api import logger

from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import SSH, SSHTimeout

__all__ = [u"execute_vat2_script"]


def execute_vat2_script(command, script_name, node, timeout=120, history=True):
    """Execute VAT script on remote node, and store the result.

    :param command: API message name to execute.
    :param script_name: Name of the file with JSON (bulk) arguments.
    :param node: Node to execute the VAT2 script on.
    :param timeout: Seconds to allow the script to run.
    :param history: If true, add command to history.
    :type command: str
    :type script_name: str
    :type node: dict
    :type timeout: int
    :type history: bool
    :returns: Return code, stdout and stderr.
    :rtype: Tuple[int, str, str]
    :raises SSHException: If cannot open connection for VAT.
    :raises SSHTimeout: If VAT execution is timed out.
    :raises RuntimeError: If VAT script execution fails.
    """
    ssh = SSH()
    try:
        ssh.connect(node)
    except:
        raise SSHException(
            f"Cannot open SSH connection to execute VAT command(s)."
        )

    ssh.scp(script_name, script_name)
    cmd = f"vat2 --debug --file {script_name} {command}"
    try:
        ret_code, stdout, stderr = ssh.exec_command(
            cmd=cmd, timeout=timeout
        )
    except SSHTimeout:
        logger.error(f"VAT2 script execution timeout: {cmd}")
        raise
    except Exception:
        raise RuntimeError(f"VAT2 script execution failed: {cmd}")

    return ret_code, stdout, stderr
