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

from time import sleep

from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class Sfdp:
    """General utilities for managing SFDP functionality in VPP"""

    @staticmethod
    def add_sfdp_tenant(node, tenant_id=1):
        """FIXME"""
        cmd = "sfdp_tenant_add_del"
        err_msg = f"Failed to add SFDP tenant"
        args = dict(tenant_id=tenant_id, context_id=tenant_id, is_del=0)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
        cmd = "sfdp_set_timeout"
        args = dict(tenant_id=tenant_id, timeout_id=0, timeout_value=300)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)
            args["timeout_id"] += 1
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def enable_sfdp_interface_input(node, sw_if_index, tenant_id=1):
        """FIXME"""
        cmd = "sfdp_interface_input_set"
        err_msg = f"Failed to enable SFDP input on {sw_if_index=}"
        args = dict(sw_if_index=sw_if_index, tenant_id=tenant_id, is_del=0)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def set_sfdp_services(node, services, tenant_id=1):
        """FIXME"""
        cmd = "sfdp_set_services"
        err_msg = f"Failed to enable IP4 for SFDP"
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
    def log_sfdp_tenants(node):
        """FIXME"""
        cmd = "sfdp_tenant_dump"
        err_msg = f"Failed to get SFDP tenants"
        args = dict()
        with PapiSocketExecutor(node) as papi_exec:
            tenants = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.info(f"{tenants=}")
        PapiSocketExecutor.run_cli_cmd(node, "show sfdp tenant 1 detail")

    @staticmethod
    def log_sfdp_sessions(node):
        """FIXME"""
        cmd = "sfdp_session_dump"
        err_msg = f"Failed to get SFDP sessions"
        args = dict()
        with PapiSocketExecutor(node) as papi_exec:
            sessions = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.info(f"{sessions=}")
        PapiSocketExecutor.run_cli_cmd(node, "show features verbose")

    @staticmethod
    def log_sfdp_num_sessions(node):
        """FIXME"""
        cmd = "sfdp_session_dump"
        err_msg = f"Failed to get SFDP sessions"
        args = dict()
        with PapiSocketExecutor(node) as papi_exec:
            sessions = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.info(f"{len(sessions)=}")

    @staticmethod
    def create_sfdp_resetter(node):
        """FIXME"""
        def kill_all_sfdp_sessions():
            """FIXME"""
            Sfdp.log_sfdp_tenants(node)
            cmd = "sfdp_kill_session"
            err_msg = f"Failed to kill all SFDP sessions"
            args = dict(is_all=True)
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
            Sfdp.log_sfdp_tenants(node)
            # VPP main worker needs some time for proper cleanup.
            # FIXME: make the workaround less dumb.
            sleep(3)
            Sfdp.log_sfdp_tenants(node)
        return kill_all_sfdp_sessions
