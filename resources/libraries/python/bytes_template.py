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

from robot.api import logger

class BytesTemplate:
    """This is a class for internal use (no Robot keywords are defined here).

    Internally, a template is a list, elements can be of two types.
    Bytes elements are substrings to be copied verbatim.
    Integer elements are to be serialized as u32 type.
    Their values are set to what has been serialized last,
    and bumped just before serializing next.
    The first value is assumed to be context ID,
    external source is needed (as it can be shared with other code).
    All the other values are incremented by one.

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
        :type template: list of bytes or int
        """
        self.template = template

    # TODO: __repr__, __str__?

    @classmethod
    def from_two_messages(cls, first, second):
        """Create template instance fitting the two bytes string messages.

        :param first: Binary string with next to last message.
        :param second: Binary string with last message.
        :type first: bytes
        :type second: bytes
        :raises RuntimeError: If two messages are not similar enough.
        """
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
        template = list()
        reserve = b""
        inequals = 0
        for index in range(length):
            if inequals and first[index] == second[index]:
                # This is the interesting branch.
                # First equal after sequence of inequals.
                numbers = -(-inequals // 4)
                offset = 4 * numbers
                # The following line fails if it was not 4 byte int increase.
                text = reserve[:-offset]
                reserve = reserve[-offset:]
                for _ in range(numbers):
                    template.append(text)
                    text = b""
                    num_bytes = reserve[:4]
                    reserve = reserve[4:]
                    num_int = cls.packunp.unpack(num_bytes)
                    template.append(num_int)
                # TODO: Assert? reserved == b""
                inequals = 0
                # Do not forget to start the new substring.
                reserve = second[index:index + 1]
            else:
                # Nothing interesting, keep growing the reserve.
                reserve += second[index:index + 1]
                if first[index] != second[index]:
                    inequals += 1
        # Usually, there is a trailing substring.
        if inequals:
            # We did not have equals to close the cycle, so copypaste.
            numbers = -(-inequals // 4)
            offset = 4 * numbers
            text = reserve[:-offset]
            reserve = reserve[-offset:]
            for _ in numbers:
                template.append(text)
                text = b""
                num_bytes = reserve[:4]
                reserve = reserve[4:]
                num_int = cls.packunp.unpack(num_bytes)
                template.append(num_int)
        else:
            # Reserve contains the final substring.
            template.append(reserve)
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
                if not isinstance(item, int):
                    raise RuntimeError(f"Unsupported type {type(item)!r}: {item!r}")
                if needs_context:
                    item = get_context()
                    needs_context = False
                else:
                    item += 1
                self.template[index] = item
                packed = self.packunp.pack(item)
                material_list.append(packed)
            generated = b"".join(material_list)
            yield generated
