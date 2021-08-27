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

"""Module defining class for tracking incremental edits."""

from resources.libraries.python.Constants import Constants


class EditState:
    """Track file name, prolog and which splits are remaining.

    This is a persistent data structure. Immutable,
    but with methods creating edited copies.

    Busines logic is quite limited, this is basically just a container
    introduced to reduce number of function arguments,
    with few simple operations on top.
    The real logic (what to edit and how) is driven by external functions.

    The subtype field is just riding along, to be used after filename
    and prolog are edited, but next versions my want to edit that too.
    """
    def __init__(
        self, filename, prolog, subtype, nic_model=None,
        test_type_split=None, nic_model_split=None, nic_driver_split=None,
    ):
        """Store the values.

        If a split value is None, the value from subtype is used.
        This allows edit process to gradually disable splitting
        (after performing it) without affecting the subtype.

        During dragual edit, one function choses NIC model name,
        but a different function needs to know it to select correct
        NIC drivers, that is why we track it here.

        :param filename: Current form of file name to write to.
        :param prolog: Current form of suite content without test cases.
        :param subtype: Test classification, with default split values.
        :param nic_model: NIC model name, if already chosen.
        :param test_type_split: Whether to generate other test types.
        :param nic_model_split: Whether to generate other NIC models.
        :param nic_driver_split: Whether to generate other NIC drivers.
        :type filename: str
        :type prolog: str
        :type subtype: SuiteSubtype
        :type nic_model: Optional[str]
        :type test_type_split: Optional[bool]
        :type nic_model_split: Optional[bool]
        :type nic_driver_split: Optional[bool]
        """
        self.filename = filename
        self.prolog = prolog
        self.subtype = subtype
        self.nic_model = nic_model
        if test_type_split is None:
            test_type_split = subtype.value.test_type_split
        self.test_type_split = test_type_split
        if nic_model_split is None:
            nic_model_split = subtype.value.nic_model_split
        self.nic_model_split = nic_model_split
        if nic_driver_split is None:
            nic_driver_split = subtype.value.nic_driver_split
        self.nic_driver_split = nic_driver_split

    def _replace_defensively(
        self, whole, to_replace, replace_with, how_many, msg
    ):
        """Replace substrings while checking the number of occurrences.

        Return edited copy of the text. Assuming "whole" is really a string,
        or something else with .replace not affecting it.

        :param whole: The text to perform replacements on.
        :param to_replace: Substring occurrences of which to replace.
        :param replace_with: Substring to replace occurrences with.
        :param how_many: Number of occurrences to expect.
        :param msg: Error message to raise.
        :type whole: str
        :type to_replace: str
        :type replace_with: str
        :type how_many: int
        :type msg: str
        :returns: The whole text after replacements are done.
        :rtype: str
        :raises ValueError: If number of occurrences does not match.
        """
        found = whole.count(to_replace)
        if found != how_many:
            raise ValueError(f"{self.filename}: {msg}")
        return whole.replace(to_replace, replace_with)

    def with_filename_replaced(self, to_replace, replace_with, how_many, msg):
        """Return new instance with replacements in filename.

        :param to_replace: Substring occurrences of which to replace.
        :param replace_with: Substring to replace occurrences with.
        :param how_many: Number of occurrences to expect.
        :param msg: Error message to raise.
        :type to_replace: str
        :type replace_with: str
        :type how_many: int
        :type msg: str
        :returns: New instance with replacements in filename.
        :rtype: EditState
        :raises ValueError: If number of occurrences does not match.
        """
        return EditState(
            filename=self._replace_defensively(
                self.filename, to_replace, replace_with, how_many, msg,
            ),
            prolog=self.prolog,
            subtype=self.subtype,
            nic_model=self.nic_model,
            test_type_split=self.test_type_split,
            nic_model_split=self.nic_model_split,
            nic_driver_split=self.nic_driver_split,
        )

    def with_prolog_replaced(self, to_replace, replace_with, how_many, msg):
        """Return new instance with replacements in prolog.

        :param to_replace: Substring occurrences of which to replace.
        :param replace_with: Substring to replace occurrences with.
        :param how_many: Number of occurrences to expect.
        :param msg: Error message to raise.
        :type to_replace: str
        :type replace_with: str
        :type how_many: int
        :type msg: str
        :returns: New instance with replacements in filename.
        :rtype: EditState
        :raises ValueError: If number of occurrences does not match.
        """
        return EditState(
            filename=self.filename,
            prolog=self._replace_defensively(
                self.prolog, to_replace, replace_with, how_many, msg,
            ),
            subtype=self.subtype,
            nic_model=self.nic_model,
            test_type_split=self.test_type_split,
            nic_model_split=self.nic_model_split,
            nic_driver_split=self.nic_driver_split,
        )

    def with_nic_model_chosen(self, nic_model):
        """Return new instance with nic model set. Fail if set already.
        """
        if self.nic_model is not None:
            raise ValueError("NIC model aready set to {self.nic_model}.")
        return EditState(
            filename=self.filename,
            prolog=self.prolog,
            subtype=self.subtype,
            nic_model=str(nic_model),
            test_type_split=self.test_type_split,
            nic_model_split=self.nic_model_split,
            nic_driver_split=self.nic_driver_split,
        )

    def without_test_type_split(self):
        """Return new instance with test_type_split set to False.

        Fail if it is already False.

        :returns: New instance with test_type_split set to False.
        :rtype: EditState
        :raises ValueError: If test_type_split is already False.
        """
        if not self.test_type_split:
            raise ValueError("Already without test type split.")
        return EditState(
            filename=self.filename,
            prolog=self.prolog,
            subtype=self.subtype,
            nic_model=self.nic_model,
            test_type_split=False,
            nic_model_split=self.nic_model_split,
            nic_driver_split=self.nic_driver_split,
        )

    def without_nic_model_split(self):
        """Return new instance with nic_model_split set to False.

        Fail if it is already False.

        :returns: New instance with nic_model_split set to False.
        :rtype: EditState
        :raises ValueError: If nic_model_split is already False.
        """
        if not self.nic_model_split:
            raise ValueError("Already without NIC model split.")
        return EditState(
            filename=self.filename,
            prolog=self.prolog,
            subtype=self.subtype,
            nic_model=self.nic_model,
            test_type_split=self.test_type_split,
            nic_model_split=False,
            nic_driver_split=self.nic_driver_split,
        )

    def without_nic_driver_split(self):
        """Return new instance with nic_driver_split set to False.

        Fail if it is already False.

        :returns: New instance with nic_driver_split set to False.
        :rtype: EditState
        :raises ValueError: If nic_driver_split is already False.
        """
        if not self.nic_driver_split:
            raise ValueError("Already without NIC driver split.")
        return EditState(
            filename=self.filename,
            prolog=self.prolog,
            subtype=self.subtype,
            nic_model=self.nic_model,
            test_type_split=self.test_type_split,
            nic_model_split=self.nic_model_split,
            nic_driver_split=False,
        )

    @staticmethod
    def get_iface_and_suite_ids(filename):
        """Get NIC code, suite ID and suite tag.

        This is useful even before EditState instance is created.

        NIC code is the part of suite name
        which should be replaced for other NIC.
        Suite ID is the part of suite name
        which is appended to test case names.
        Suite tag is suite ID without both test type and NIC driver parts.

        :param filename: Name of the suite file.
        :type filename: str
        :returns: NIC code, suite ID, suite tag.
        :rtype: 3-tuple of str
        """
        dash_split = filename.split(u"-", 1)
        if len(dash_split[0]) <= 4:
            # It was something like "2n1l", we need one more split.
            dash_split = dash_split[1].split(u"-", 1)
        nic_code = dash_split[0]
        try:
            suite_id = dash_split[1].split(u".robot", 1)[0]
        except IndexError as err:
            raise RuntimeError(f"Failed to parse {filename}") from err
        suite_tag = suite_id.rsplit(u"-", 1)[0]
        for prefix in Constants.FORBIDDEN_SUITE_PREFIX_LIST:
            if suite_tag.startswith(prefix):
                suite_tag = suite_tag[len(prefix):]
        return nic_code, suite_id, suite_tag

    def check_suite_tag_and_add_suite_id(self, filename_set):
        """Verify suite tag occurres once in prolog, add suite filename to set.

        Fail if the suite filename is already in the list.

        Call this after all splits are done,
        to confirm the (edited) suite tag still matches the (edited) suite name.

        Currently, the edited suite tag is expect to be identical
        to the primary suite tag, but having a function is more flexible.

        The occurences are counted including "| " prefix,
        to lower the chance to match a comment.

        :param filename_set: Suite filenames encountered so far.
        :tyep filename_set: Set[str]
        :raises ValueError: If tag is not found exactly once, or ID is in list.
        """
        filename = self.filename
        _, suite_id, suite_tag = self.get_iface_and_suite_ids(filename)
        found = self.prolog.count(u"| " + suite_tag)
        if found != 1:
            raise ValueError(f"Suite tag found {found} times for {suite_tag}")
        if filename in filename_set:
            raise ValueError(f"Suite filename {filename} already generated.")
        filename_set.add(filename)
