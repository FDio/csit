# Copyright (c) 2025 Cisco and/or its affiliates.
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

from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class Sfdp:
    """General utilities for managing SFDP functionality in VPP"""

    @staticmethod
    def add_sfdp_tenant(node, tenant_id=1, context_id=1):
        """FIXME"""
        cmd = "sfdp_tenant_add_del"
        err_msg = f"Failed to add SFDP tenant"
        args = dict(tenant_id=tenant_id, context_id=context_id, is_del=0)
        with PapiSocketExecutor(node) as papi_exec:
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
    def set_sfdp_services_ip4(node, tenant_id=1):
        """FIXME"""
        cmd = "sfdp_set_services"
        err_msg = f"Failed to enable SFDP input on {sw_if_index=}"
        args = dict(tenant_id=tenant_id, services=["ip4-lookup"])
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

    @staticmethod
    def log_sfdp_sessions(node):
        """FIXME"""
        cmd = "sfdp_session_dump"
        err_msg = f"Failed to get SFDP sessions"
        args = dict()
        with PapiSocketExecutor(node) as papi_exec:
            sessions = papi_exec.add(cmd, **args).get_details(err_msg)
        logger.info(f"{sessions=}")
