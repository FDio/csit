# Copyright (c) 2026 Cisco and/or its affiliates.
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

"""SFDP library."""

import re
from time import monotonic, sleep
from typing import Callable, List, Tuple

from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class Sfdp:
    """General utilities for managing SFDP functionality in VPP"""

    @staticmethod
    def add_sfdp_tenant(node: dict, tenant_id: int = 1) -> None:
        """Configure one tenant and set large enough timer values.

        :param node: Topology node to operate on.
        :param tenant_id: Use this ID if the default 1 is not good.
        :type node: dict
        :type tenant_id: int
        """
        cmd = "sfdp_tenant_add_del"
        err_msg = "Failed to add SFDP tenant"
        args = dict(tenant_id=tenant_id, context_id=tenant_id, is_del=0)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
        cmd = "sfdp_set_timeout"
        args = dict(tenant_id=tenant_id, timeout_id=0, timeout_value=3000)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def enable_sfdp_interface_input(
        node: dict, sw_if_index: int, tenant_id: int = 1
    ) -> None:
        """Enable SFDP input on the interface.

        :param node: Topology node to operate on.
        :param sw_if_index: Software interface index to use.
        :param tenant_id: ID of a created tenant to use for this interface.
        :type node: dict
        :type sw_if_index: int
        :type tenant_id: int
        """
        cmd = "sfdp_interface_input_set"
        err_msg = f"Failed to enable SFDP input on {sw_if_index=}"
        args = dict(sw_if_index=sw_if_index, tenant_id=tenant_id, is_del=0)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def set_sfdp_services(
        node: dict, services: List[str], tenant_id: int = 1
    ) -> None:
        """Enable listed services for the SFDP tenant.

        Services available depend on plugins enabled,
        search for SFDP_SERVICE_DEFINE macro in VPP sources,
        node_name is the attribute containing the recognized service name.

        Currently, the same set of services in enabled in both directions.

        :param node: Topology node to operate on.
        :param services: Human readable service names.
        :param tenant_id: ID of a created tenant to enable.
        :type node: dict
        :type services: List[str]
        :type tenant_id: int
        """
        cmd = "sfdp_set_services"
        err_msg = "Failed to enable IP4 for SFDP"
        args = dict(
            tenant_id=tenant_id,
            services=[dict(data=service) for service in services],
            n_services=len(services),
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
        args["dir"] = 1
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def get_remaining_sfdp_tenant_sessions(
        node: dict, tenant_id: int = 1, log: bool = True
    ) -> Tuple[int, str]:
        """Compute the number of active sessions, return also raw details.

        This can be useful both in CPS tests when waiting for reset,
        but also in teardowns ase an useful debug output.
        The current VPP CLI return text with separate counts for
        created and removed sessions.

        :param node: Topology node to operate on.
        :param tenant_id: ID of a created tenant to investigate.
        :param log: Whether to log the result as a Robot info.
        :type node: dict
        :type tenant_id: int
        :type log: bool
        :returns: Number of sessions and raw details.
        :rtype: Tuple[int, str]
        :raises RuntimeError: If text parsing fails.
        """
        detail = None
        try:
            cmd = f"show sfdp tenant {tenant_id} detail"
            detail = PapiSocketExecutor.run_cli_cmd(node, cmd, log=False)
            created_match = re.search(r"created sessions:\s+(\d+)", detail)
            if not created_match:
                raise ValueError(f"{detail=} lacks created sessions.")
            created_sessions = int(created_match.group(1))
            removed_match = re.search(r"removed sessions:\s+(\d+)", detail)
            if not removed_match:
                raise ValueError(f"{detail=} lacks removed sessions.")
            removed_sessions = int(removed_match.group(1))
        except (ValueError, OSError) as err:
            raise RuntimeError(f"{detail=} {err=}") from err
        remaining_sessions = created_sessions - removed_sessions
        if log:
            logger.info(
                f"SFDP sessions: {created_sessions} - {removed_sessions}"
                f" = {remaining_sessions}"
            )
        return remaining_sessions, detail

    @staticmethod
    def wait_for_no_remaining_sfdp_sessions(
        node: dict, tenant_id: int = 1, delay: float = 0.1, timeout: float = 10
    ) -> None:
        """Wait some time until there are no active sessions.

        CPS tests rely on this to confirm the session table is empty.

        :param node: Topology node to operate on.
        :param tenant_id: ID of a created tenant to investigate.
        :param delay: How many seconds to wait between subsequent checks.
        :param timeout: How many seconds to repeat before giving up.
        :type node: dict
        :type tenant_id: int
        :type delay: float
        :type timeout: float
        :raises RuntimeError: On parsing error or sessions left after timeout.
        """
        time_stop = monotonic() + timeout
        while monotonic() < time_stop:
            remaining, _ = Sfdp.get_remaining_sfdp_tenant_sessions(
                node, tenant_id
            )
            if not remaining:
                break
            sleep(delay)
        else:
            raise RuntimeError("Timeout waiting for session table clear.")

    @staticmethod
    def log_sfdp_tenants(node: dict) -> None:
        """Emit robot info with SFDP tenant information, but API and CLI.

        :param node: Topology node to operate on.
        :type node: dict
        """
        cmd = "sfdp_tenant_dump"
        err_msg = "Failed to get SFDP tenants"
        args = dict()
        with PapiSocketExecutor(node) as papi_exec:
            tenants = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.info(f"{tenants=}")
        _, detail = Sfdp.get_remaining_sfdp_tenant_sessions(node, log=False)
        logger.info(f"{detail=}")
        cmd = "show features verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show interface iavf0/0 features verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show interface iavf1/0 features verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show vlib graph iavf0/0-rx"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show vlib graph iavf1/0-rx"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show node iavf0/0-rx verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show node iavf1/0-rx verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show vlib graph ethernet-input"
        PapiSocketExecutor.run_cli_cmd(node, cmd)
        cmd = "show node ethernet-input verbose"
        PapiSocketExecutor.run_cli_cmd(node, cmd)

    @staticmethod
    def log_sfdp_sessions(node: dict, max_num: int = 10) -> None:
        """List first few active SFDP sessions as CLI logging.

        CLI over API is too slow to print thousands of sessions.

        :param node: Topology node to operate on.
        :param max_num: Limit to this many sessions.
        :type node: dict
        :type max_num: int
        """
        cmd = f"show sfdp session-table max {max_num}"
        PapiSocketExecutor.run_cli_cmd(node, cmd)

    @staticmethod
    def create_sfdp_resetter(node: dict) -> Callable[[], None]:
        """Return a resetter suitable for CPS tests.

        :param node: Topology node to operate on.
        :type node: dict
        :returns: A Python closure other functions can call.
        :rtype: Callable[[], None]
        """

        def kill_all_sfdp_sessions() -> None:
            """Kill all SFDP sessions and wait to confirm the table is empty.

            Also log first few initial sessions for debug purposes.
            """
            Sfdp.log_sfdp_sessions(node)
            cmd = "sfdp_kill_session"
            err_msg = "Failed to kill all SFDP sessions"
            args = dict(is_all=True)
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
            Sfdp.wait_for_no_remaining_sfdp_sessions(node)

        return kill_all_sfdp_sessions
