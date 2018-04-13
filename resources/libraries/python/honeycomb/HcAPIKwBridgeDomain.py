# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Keywords to manipulate bridge domain configuration using Honeycomb REST API.

The keywords make possible to put and get configuration data and to get
operational data.
"""

from resources.libraries.python.HTTPRequest import HTTPCodes
from resources.libraries.python.honeycomb.HoneycombSetup import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import DataRepresentation
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil


class BridgeDomainKeywords(object):
    """Keywords to manipulate bridge domain configuration.

    Implements keywords which get configuration and operational data about
    bridge domains and put the bridge domains' parameters using Honeycomb REST
    API.
    """

    PARAMS = ("flood", "forward", "learn", "unknown-unicast-flood",
              "arp-termination")

    def __init__(self):
        pass

    @staticmethod
    def _configure_bd(node, bd_name, data,
                      data_representation=DataRepresentation.JSON):
        """Send bridge domain configuration data and check the response.

        :param node: Honeycomb node.
        :param bd_name: The name of bridge domain.
        :param data: Configuration data to be sent in PUT request.
        :param data_representation: How the data is represented.
        :type node: dict
        :type bd_name: str
        :type data: dict
        :type data_representation: DataRepresentation
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If the status code in response on PUT is not
            200 = OK.
        """

        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_bridge_domain", data,
                               data_representation=data_representation)
        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "The configuration of bridge domain '{0}' was not successful. "
                "Status code: {1}.".format(bd_name, status_code))
        return resp

    @staticmethod
    def _set_bd_properties(node, bd_name, path, new_value=None):
        """Set bridge domain properties.

        This method reads bridge domain configuration data, creates, changes or
        removes the requested data and puts it back to Honeycomb.

        :param node: Honeycomb node.
        :param bd_name: The name of bridge domain.
        :param path:  Path to data we want to change, create or remove.
        :param new_value: The new value to be set. If None, the item will be
            removed.
        :type node: dict
        :type bd_name: str
        :type path: tuple
        :type new_value: str, dict or list
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to get or set the data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_bridge_domain")
        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "bridge domains. Status code: {0}.".format(status_code))

        if new_value:
            new_data = HcUtil.set_item_value(resp, path, new_value)
        else:
            new_data = HcUtil.remove_item(resp, path)

        return BridgeDomainKeywords._configure_bd(node, bd_name, new_data)

    @staticmethod
    def _create_bd_structure(bd_name, **kwargs):
        """Create the bridge domain data structure as it is expected by
        Honeycomb REST API.

        :param bd_name: Bridge domain name.
        :param kwargs: Parameters and their values. The accepted parameters are
            defined in BridgeDomainKeywords.PARAMS.
        :type bd_name: str
        :type kwargs: dict
        :returns: Bridge domain data structure.
        :rtype: dict
        """

        bd_structure = {"name": bd_name}

        for param, value in kwargs.items():
            if param not in BridgeDomainKeywords.PARAMS:
                raise HoneycombError("The parameter {0} is invalid.".
                                     format(param))
            bd_structure[param] = str(value)

        return bd_structure

    @staticmethod
    def get_all_bds_cfg_data(node):
        """Get configuration data about all bridge domains from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Configuration data about all bridge domains from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get configuration data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_bridge_domain")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "bridge domains. Status code: {0}.".format(status_code))
        try:
            return resp["bridge-domains"]["bridge-domain"]

        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_bd_cfg_data(node, bd_name):
        """Get configuration data about the given bridge domain from Honeycomb.

        :param node: Honeycomb node.
        :param bd_name: The name of bridge domain.
        :type node: dict
        :type bd_name: str
        :returns: Configuration data about the given bridge domain from
            Honeycomb.
        :rtype: dict
        """

        intfs = BridgeDomainKeywords.get_all_bds_cfg_data(node)
        for intf in intfs:
            if intf["name"] == bd_name:
                return intf
        return {}

    @staticmethod
    def get_all_bds_oper_data(node):
        """Get operational data about all bridge domains from Honeycomb.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Operational data about all bridge domains from Honeycomb.
        :rtype: list
        :raises HoneycombError: If it is not possible to get operational data.
        """

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "oper_bridge_domains")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get operational information about the "
                "bridge domains. Status code: {0}.".format(status_code))
        try:
            return resp["bridge-domains-state"]["bridge-domain"]

        except (KeyError, TypeError):
            return []

    @staticmethod
    def get_bd_oper_data(node, bd_name):
        """Get operational data about the given bridge domain from Honeycomb.

        :param node: Honeycomb node.
        :param bd_name: The name of bridge domain.
        :type node: dict
        :type bd_name: str
        :returns: Operational data about the given bridge domain from Honeycomb.
        :rtype: dict
        """

        intfs = BridgeDomainKeywords.get_all_bds_oper_data(node)
        for intf in intfs:
            if intf["name"] == bd_name:
                return intf
        return {}

    @staticmethod
    def add_first_bd(node, bd_name, **kwargs):
        """Add the first bridge domain.

        If there are any other bridge domains configured, they will be removed.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain name.
        :param kwargs: Parameters and their values. The accepted parameters are
            defined in BridgeDomainKeywords.PARAMS
        :type node: dict
        :type bd_name: str
        :type kwargs: dict
        :returns: Bridge domain data structure.
        :rtype: dict
        """

        new_bd = BridgeDomainKeywords._create_bd_structure(bd_name, **kwargs)
        bridge_domain = {"bridge-domains": {"bridge-domain": [new_bd, ]}}
        return BridgeDomainKeywords._configure_bd(node, bd_name, bridge_domain)

    @staticmethod
    def add_bd(node, bd_name, **kwargs):
        """Add a bridge domain.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain name.
        :param kwargs: Parameters and their values. The accepted parameters are
            defined in BridgeDomainKeywords.PARAMS
        :type node: dict
        :type bd_name: str
        :type kwargs: dict
        :returns: Bridge domain data structure.
        :rtype: dict
        """

        path = ("bridge-domains", "bridge-domain")
        new_bd = BridgeDomainKeywords._create_bd_structure(bd_name, **kwargs)
        bridge_domain = [new_bd, ]
        return BridgeDomainKeywords._set_bd_properties(node, bd_name, path,
                                                       bridge_domain)

    @staticmethod
    def remove_all_bridge_domains(node):
        """Remove all bridge domains.

        :param node: Honeycomb node.
        :type node: dict
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to remove all bridge
            domains.
        """

        data = {"bridge-domains": {"bridge-domain": []}}

        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_bridge_domain", data)

        if status_code not in (HTTPCodes.OK, HTTPCodes.ACCEPTED):
            raise HoneycombError("Not possible to remove all bridge domains. "
                                 "Status code: {0}.".format(status_code))
        return resp

    @staticmethod
    def remove_bridge_domain(node, bd_name):
        """Remove a bridge domain.

        :param node:  Honeycomb node.
        :param bd_name: The name of bridge domain to be removed.
        :type node: dict
        :type bd_name: str
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to remove the bridge
            domain.
        """

        path = ("bridge-domains", ("bridge-domain", "name", bd_name))

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_bridge_domain")
        if status_code != HTTPCodes.OK:
            raise HoneycombError(
                "Not possible to get configuration information about the "
                "bridge domains. Status code: {0}.".format(status_code))

        new_data = HcUtil.remove_item(resp, path)
        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_bridge_domain", new_data)
        if status_code != HTTPCodes.OK:
            raise HoneycombError("Not possible to remove bridge domain {0}. "
                                 "Status code: {1}.".
                                 format(bd_name, status_code))
        return resp

    @staticmethod
    def configure_bridge_domain(node, bd_name, param, value):
        """Configure a bridge domain.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain name.
        :param param: Parameter to set, change or remove. The accepted
            parameters are defined in BridgeDomainKeywords.PARAMS
        :param value: The new value to be set, change or remove. If None, the
            item will be removed.
        :type node: dict
        :type bd_name: str
        :type param: str
        :type value: str
        :returns: Content of response.
        :rtype: bytearray
        """

        if param not in BridgeDomainKeywords.PARAMS:
            raise HoneycombError("The parameter {0} is invalid.".format(param))

        path = ("bridge-domains", ("bridge-domain", "name", bd_name), param)
        return BridgeDomainKeywords.\
            _set_bd_properties(node, bd_name, path, value)

    @staticmethod
    def add_l2_fib_entry(node, bd_name, l2_fib_entry):
        """Add an L2 FIB entry to the bridge domain's list of L2 FIB entries.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :param l2_fib_entry: L2 FIB entry to be added to the L2 FIB table.
        :type node: dict
        :type bd_name: str
        :type l2_fib_entry: dict
        :returns: Content of response.
        :rtype: bytearray
        """

        path = ("bridge-domains",
                ("bridge-domain", "name", bd_name),
                "l2-fib-table",
                "l2-fib-entry")

        new_l2_fib_entry = [l2_fib_entry, ]
        return BridgeDomainKeywords._set_bd_properties(
            node, bd_name, path, new_l2_fib_entry)

    @staticmethod
    def modify_l2_fib_entry(node, bd_name, mac, param, value):
        """Modify an existing L2 FIB entry in the bridge domain's L2 FIB table.
        The L2 FIB entry is specified by MAC address.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :param mac: MAC address used as the key in L2 FIB data structure.
        :param param: The parameter to be modified.
        :param value: The new value of the parameter.
        :type node: dict
        :type bd_name: str
        :type mac: str
        :type param: str
        :type value: str or int
        :returns: Content of response.
        :rtype: bytearray
        """

        path = ("bridge-domains",
                ("bridge-domain", "name", bd_name),
                "l2-fib-table",
                ("l2-fib-entry", "phys-address", mac),
                param)

        return BridgeDomainKeywords._set_bd_properties(
            node, bd_name, path, value)

    @staticmethod
    def remove_l2_fib_entry(node, bd_name, mac):
        """Remove an L2 FIB entry from bridge domain's L2 FIB table. The
        entry is specified by MAC address.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :param mac: MAC address used as the key in L2 FIB data structure.
        :type node: dict
        :type bd_name: str
        :type mac: str
        :returns: Content of response.
        :rtype: bytearray
        :raises HoneycombError: If it is not possible to remove the specified
            entry.
        """

        path = ("bridge-domains",
                ("bridge-domain", "name", bd_name),
                "l2-fib-table",
                ("l2-fib-entry", "phys-address", str(mac)))

        status_code, resp = HcUtil.\
            get_honeycomb_data(node, "config_bridge_domain")
        if status_code != HTTPCodes.OK:
            raise HoneycombError("Not possible to get configuration information"
                                 " about the L2 FIB entry {0} from bridge "
                                 "domain {1}. Status code: {2}.".
                                 format(mac, bd_name, status_code))

        new_data = HcUtil.remove_item(resp, path)
        status_code, resp = HcUtil.\
            put_honeycomb_data(node, "config_bridge_domain", new_data)
        if status_code != HTTPCodes.OK:
            raise HoneycombError("Not possible to remove L2 FIB entry {0} from "
                                 "bridge domain {1}. Status code: {2}.".
                                 format(mac, bd_name, status_code))
        return resp


    @staticmethod
    def remove_all_l2_fib_entries(node, bd_name):
        """Remove all entries from the bridge domain's L2 FIB table.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :type node: dict
        :type bd_name: str
        :returns: Content of response.
        :rtype: bytearray
        """

        path = ("bridge-domains",
                ("bridge-domain", "name", bd_name),
                "l2-fib-table")

        return BridgeDomainKeywords._set_bd_properties(
            node, bd_name, path, None)

    @staticmethod
    def get_all_l2_fib_entries(node, bd_name):
        """Retrieves all entries from the bridge domain's L2 FIB table.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :type node: dict
        :type bd_name: str
        :returns: Bridge domain's L2 FIB table or empty list if the table does
            not exist or it is empty.
        :rtype: list
        """

        bd_data = BridgeDomainKeywords.get_bd_oper_data(node, bd_name)
        try:
            return bd_data["l2-fib-table"]["l2-fib-entry"]
        except KeyError:
            return []

    @staticmethod
    def get_l2_fib_entry(node, bd_name, mac):
        """Retrieves an entry from bridge domain's L2 FIB table. The entry is
        specified by MAC address.

        :param node: Honeycomb node.
        :param bd_name: Bridge domain's name.
        :param mac: MAC address used as the key in L2 FIB data structure.
        :type node: dict
        :type bd_name: str
        :type mac: str
        :returns: The requested entry from bridge domain's L2 FIB table or empty
            dictionary if it does not exist in the L2 FIB table.
        :rtype: dict
        """

        l2_fib = BridgeDomainKeywords.get_all_l2_fib_entries(node, bd_name)
        for entry in l2_fib:
            if entry["phys-address"] == mac:
                return entry
        return {}
