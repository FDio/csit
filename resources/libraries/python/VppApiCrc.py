# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module for keeping track of VPP API CRCs relied on by CSIT."""

import json
import os
import yaml

from robot.api import logger

from resources.libraries.python.Constants import Constants

def _str(text):
    """Convert from possible unicode without interpreting as number.

    :param text: Input to convert.
    :type text: str or unicode
    :returns: Converted text.
    :rtype: str
    """
    return text.encode("utf-8") if isinstance(text, unicode) else text


class VppApiCrcChecker(object):
    """Holder of data related to tracking VPP API CRCs.

    Both message names and crc hexa strings are tracked as
    ordinary Python2 (bytes) str, so _str() is used when input is
    possibly unicode or otherwise not safe.

    Each instance of this class starts with same default state,
    so make sure the calling libraries have appropriate robot library scope.
    For usual testing, it means "GLOBAL" scope."""

    def __init__(self, directory,
                 fail_on_mismatch=Constants.CRC_MISMATCH_FAILS_TEST):
        """Initialize empty state, then register known collections.

        This also scans directory for .api.json files
        and performs initial checks, but does not report the findings yet.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        """

        self.fail_on_mismatch = fail_on_mismatch
        """If True, mismatch leads to test failure, by raising exception.
        If False, the mismatch is logged, but the test is allowed to continue.
        """

        self._expected = dict()
        """Mapping from collection name to mapping from API name to CRC string.

        Colection name should be something useful for logging.

        Order of addition reflects the order colections should be queried.
        If an incompatible CRC is found, affected collections are removed.
        A CRC that would remove all does not, added to _reported instead,
        while causing a failure in single test."""

        self._missing = dict()
        """Mapping from collection name to mapping from API name to CRC string.

        Starts the same as _expected, but each time an encountered api,crc pair
        fits the expectation, the pair is removed from this mapping.
        Ideally, the active mappings will become empty.
        If not, it is an error, VPP removed or renamed a message CSIT needs."""

        self._found = dict()
        """Mapping from API name to CRC string.

        This gets populated with CRCs found in .api.json,
        to serve as a hint when reporting errors."""

        self._reported = dict()
        """Mapping from API name to CRC string.

        This gets populated with APIs used, but not found in collections,
        just before the fact is reported in an exception.
        The CRC comes from _found mapping (otherwise left as None).
        The idea is to not report those next time, allowing the job
        to find more problems in a single run."""

        self._initial_conflicts_reported = False
        self._register_all()
        self._check_dir(directory)

    def raise_or_log(self, exception):
        """If fail_on_mismatch, raise, else log to console the exception.

        :param exception: The exception to raise or log.
        :type exception: RuntimeError
        """
        if self.fail_on_mismatch:
            raise exception
        logger.console("{exc!r}".format(exc=exception))

    def _register_collection(self, collection_name, name_to_crc_mapping):
        """Add a named (copy of) collection of CRCs.

        :param collection_name: Helpful string describing the collection.
        :param name_to_crc_mapping: Mapping from API names to CRCs.
        :type collection_name: str or unicode
        :type name_to_crc_mapping: dict from str/unicode to str/unicode
        """
        collection_name = _str(collection_name)
        if collection_name in self._expected:
            raise RuntimeError("Collection {cl!r} already registered.".format(
                cl=collection_name))
        mapping = {_str(k): _str(v) for k, v in name_to_crc_mapping.items()}
        self._expected[collection_name] = mapping
        self._missing[collection_name] = mapping.copy()

    def _register_all(self):
        """Add all collections this CSIT codebase is tested against."""

        file_path = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..",
            "api", "vpp", "supported_crcs.yaml"))
        with open(file_path, "r") as file_in:
            collections_dict = yaml.load(file_in.read())
        for collection_name, name_to_crc_mapping in collections_dict.items():
            self._register_collection(collection_name, name_to_crc_mapping)

    @staticmethod
    def _get_name(msg_obj):
        """Utility function to extract API name from an intermediate json.

        :param msg_obj: Loaded json object, item of "messages" list.
        :type msg_obj: list of various types
        :returns: Name of the message.
        :rtype: str or unicode
        :raises RuntimeError: If no name is found.
        """
        for item in msg_obj:
            if isinstance(item, (dict, list)):
                continue
            return _str(item)
        raise RuntimeError("No name found for message: {obj!r}".format(
            obj=msg_obj))

    @staticmethod
    def _get_crc(msg_obj):
        """Utility function to extract API CRC from an intermediate json.

        :param msg_obj: Loaded json object, item of "messages" list.
        :type msg_obj: list of various types
        :returns: CRC of the message.
        :rtype: str or unicode
        :raises RuntimeError: If no CRC is found.
        """
        for item in reversed(msg_obj):
            if not isinstance(item, dict):
                continue
            crc = item.get("crc", None)
            if crc:
                return _str(crc)
        raise RuntimeError("No CRC found for message: {obj!r}".format(
            obj=msg_obj))

    def _process_crc(self, api_name, crc):
        """Compare API to verified collections, update class state.

        Conflict is NOT when a collection does not recognize the API.
        Such APIs are merely added to _found for later reporting.
        Conflict is when a collection recognizes the API under a different CRC.
        If a partial match happens, only the matching collections are preserved.
        On no match, all current collections are preserved,
        but the offending API is added to _reported mapping.

        Note that it is expected that collections are incompatible
        with each other for some APIs. The removal of collections
        on partial match is there to help identify the intended collection
        for the VPP build under test. But if no collection fits perfectly,
        the last collections to determine the "known" flag
        depends on the order of api_name submitted,
        which tends to be fairly random (depends on order of .api.json files).
        Order of collection registrations does not help much in this regard.

        Attempts to overwrite value in _found or _reported should not happen,
        so the code does not check for that, simply overwriting.

        The intended usage is to call this method multiple times,
        and then raise exception listing all _reported.

        :param api_name: API name to check.
        :param crc: Discovered CRC to check for the name.
        :type api_name: str
        :type crc: str
        """
        # Regardless of the result, remember as found.
        self._found[api_name] = crc
        old_expected = self._expected
        new_expected = old_expected.copy()
        for collection_name, name_to_crc_mapping in old_expected.items():
            if api_name not in name_to_crc_mapping:
                continue
            if name_to_crc_mapping[api_name] == crc:
                self._missing[collection_name].pop(api_name, None)
                continue
            # Remove the offending collection.
            new_expected.pop(collection_name, None)
        if new_expected:
            # Some collections recognized the CRC.
            self._expected = new_expected
            self._missing = {name: self._missing[name] for name in new_expected}
            return
        # No new_expected means some colections knew the api_name,
        # but CRC does not match any. This has to be reported.
        self._reported[api_name] = crc

    def _check_dir(self, directory):
        """Parse every .api.json found under directory, remember conflicts.

        As several collections are supported, each conflict invalidates
        one of them, failure happens only when no collections would be left.
        In that case, set of collections just before the failure is preserved,
        the _reported mapping is filled with conflicting APIs.
        The _found mapping is filled with discovered api names and crcs.

        The exception is not thrown here, but from report_initial_conflicts.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        """
        for root, _, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(".api.json"):
                    continue
                with open(root + '/' + filename, "r") as file_in:
                    json_obj = json.load(file_in)
                msgs = json_obj["messages"]
                for msg_obj in msgs:
                    msg_name = self._get_name(msg_obj)
                    msg_crc = self._get_crc(msg_obj)
                    self._process_crc(msg_name, msg_crc)
        logger.debug("Surviving collections: {col!r}".format(
            col=self._expected.keys()))

    def report_initial_conflicts(self, report_missing=False):
        """Report issues discovered by _check_dir, if not done that already.

        Intended use: Call once after init, at a time when throwing exception
        is convenient.

        Optionally, report also missing messages.
        Missing reporting is disabled by default, because some messages
        come from plugins that might not be enabled at runtime.

        :param report_missing: Whether to raise on missing messages.
        :type report_missing: bool
        :raises RuntimeError: If CRC mismatch or missing messages are detected,
            and fail_on_mismatch is True.
        """
        if self._initial_conflicts_reported:
            return
        self._initial_conflicts_reported = True
        if self._reported:
            self.raise_or_log(
                RuntimeError("Dir check found incompatible API CRCs: {rep!r}"\
                    .format(rep=self._reported)))
        if not report_missing:
            return
        missing = {name: mapp for name, mapp in self._missing.items() if mapp}
        if missing:
            self.raise_or_log(
                RuntimeError("Dir check found missing API CRCs: {mis!r}"\
                    .format(mis=missing)))

    def check_api_name(self, api_name):
        """Fail if the api_name has no known CRC associated.

        Do not fail if this particular failure has been already reported.

        Intended use: Call everytime an API call is queued or response received.

        :param api_name: VPP API messagee name to check.
        :type api_name: str or unicode
        :raises RuntimeError: If no verified CRC for the api_name is found.
        """
        logger.debug("Checking API name {name!r} ...".format(name=api_name))
        api_name = _str(api_name)
        if api_name in self._reported:
            logger.debug("... already reported.")
            return
        old_expected = self._expected
        new_expected = old_expected.copy()
        for collection_name, name_to_crc_mapping in old_expected.items():
            if api_name in name_to_crc_mapping:
                continue
            # Remove the offending collection.
            new_expected.pop(collection_name, None)
        if new_expected:
            # Some collections recognized the message name.
            self._expected = new_expected
            logger.debug("... recognized.")
            return
        crc = self._found.get(api_name, None)
        logger.debug("... not recongnized, crc {crc}.".format(crc=crc))
        self._reported[api_name] = crc
        self.raise_or_log(
            RuntimeError("No active collection has API {api!r}"
                         " CRC found {crc!r}".format(api=api_name, crc=crc)))
