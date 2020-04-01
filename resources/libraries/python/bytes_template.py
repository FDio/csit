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

"""Class for rapid generation of incremental data using templates."""

import struct


class BytesTemplate:
    """This is a class for internal use (no Robot keywords are defined here).

    Internally, a template is a list, elements can be of two types.
    Bytes elements are substrings to be copied verbatim.
    Elements of type (int, int) are numbers, to be serialized as u32 type,
    starting with the first value, and incrementing by the second value.
    The stored value is set to what has been serialized last,
    and bumped just before serializing next.
    The first value (unless optionally disabled) is assumed to be context ID,
    external source is needed (as it can be shared with other code).

    The intended use:
    1. Get two bytes strings from another source (e.g. spying socket).
    2. Create a template instance from them.
    3. Initialize generator.
    4. Keep getting values.
    """

    packunp = struct.Struct(u">I")

    def __init__(self, template):
        """Initialize the instance.

        No real logic here, themplate is assumed to be a list of corect types.

        :param template: Template constisting of substrings and numbers.
        :type template: list of bytes or (int, int)
        """
        self.template = template

    def __repr__(self):
        """Return string usable as code crating equivalent instance.

        :returns: The string expression.
        :rtype: str
        """
        return f"BytesTemplate({self.template!r})"

    def __str__(self):
        """Return short string revealing content of the instance.

        :returns: The string description.
        :rtype: str
        """
        ret_list = list()
        for item in self.template:
            if isinstance(item, bytes):
                ret_list.append(item.hex())
            else:
                ret_list.append(repr(item))
        return u"[" + u", ".join(ret_list) + u"]"

    @classmethod
    def from_two_messages(cls, first, second):
        """Create template instance fitting the two bytes string messages.

        :param first: Binary string with next to last message.
        :param second: Binary string with last message.
        :type first: bytes or bytearray
        :type second: bytes or bytearray
        :raises RuntimeError: If two messages are not similar enough.
        """
        # Support bytearray while allowing user to edit post call.
        first = bytes(first)
        second = bytes(second)
        length = len(first)
        sec_len = len(second)
        if sec_len != length:
            raise RuntimeError(f"Lengths do not match. {length} vs {sec_len}")
        # Substrings are always equal.
        # Numbers always contain inequal bytes, but usually also equal bytes.
        # We may be unlucky, all bytes become inequal.
        # Inequal byte followed by equal byte (or end of message)
        # means the last 4 (ending on the inequal) form a number,
        # so we postpone substring creation until that happens.
        # We keep both reserves to compute increment.
        template = list()
        reserve_1, reserve_2 = b"", b""
        inequals = 0
        for index in range(length):
            if inequals and first[index] == second[index]:
                # This is the interesting branch.
                # First equal after sequence of inequals.
                numbers = -(-inequals // 4)
                offset = 4 * numbers
                # The following line fails if it was not 4 byte int increase.
                text = reserve_2[:-offset]
                reserve_1, reserve_2 = reserve_1[-offset:], reserve_2[-offset:]
                template.append(text)
                list_int_1, list_int_2 = list(), list()
                for count in range(numbers):
                    offset = count * 4
                    word_1 = reserve_1[offset:offset + 4]
                    word_2 = reserve_2[offset:offset + 4]
                    list_int_1.extend(cls.packunp.unpack(word_1))
                    list_int_2.extend(cls.packunp.unpack(word_2))
                list_tuple = [
                    (list_int_2[idx], list_int_2[idx] - list_int_1[idx])
                    for idx in range(len(list_int_2))
                ]
                template.extend(list_tuple)
                # TODO: Assert? reserved == b""
                inequals = 0
                # Do not forget to start the new substring.
                reserve_1 = first[index:index + 1]
                reserve_2 = second[index:index + 1]
            else:
                # Nothing interesting, keep growing the reserve.
                reserve_1 += first[index:index + 1]
                reserve_2 += second[index:index + 1]
                if first[index] != second[index]:
                    inequals += 1
        # Usually, there is a trailing substring.
        if inequals:
            # We did not have equals to close the cycle, so copypaste.
            numbers = -(-inequals // 4)
            offset = 4 * numbers
            # The following line fails if it was not 4 byte int increase.
            text = reserve_2[:-offset]
            reserve_1, reserve_2 = reserve_1[-offset:], reserve_2[-offset:]
            template.append(text)
            list_int_1 = cls.packunp.unpack(reserve_1)
            list_int_2 = cls.packunp.unpack(reserve_2)
            list_tuple = [
                (list_int_2[index], list_int_2[index] - list_int_1[index])
                for index in range(len(list_int_2))
            ]
            template.extend(list_tuple)
        else:
            # Reserve contains the final substring.
            template.append(reserve_2)
        # Create and return the new instance.
        return cls(template)

    def generator(self, iterations, get_context=None):
        """A generator that yields bytes strings created from the template.

        The first int field gets context (from callable),
        other get serialized value incremented by one.

        Iterating edits the template values,
        so subsequent iterations set continued values.

        If get_context is None, also the first value is just incremented.
        This is useful in debugging, when generator has to predict the messages,
        but other code uses the real context source.

        :param iterations: How many strings to yield.
        :param get_context: Callable to obtain context values.
        :type iterations: int
        :type get_context: () -> int
        """
        for _ in range(iterations):
            material_list = list()
            needs_context = get_context is not None
            for index, item in enumerate(self.template):
                if isinstance(item, bytes):
                    material_list.append(item)
                    continue
                value, increment = item
                if needs_context:
                    value = get_context()
                    needs_context = False
                else:
                    value += increment
                    # Avoid overflows and underflows.
                    value = value % 4294967296
                self.template[index] = (value, increment)
                packed = self.packunp.pack(value)
                material_list.append(packed)
            generated = b"".join(material_list)
            yield generated
