# Copyright (c) 2021 PANTHEON.tech s.r.o.
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

"""Increment utilities library."""


class ObjIncrement(object):
    """
    An iterator class used to generate incremented values in each iteration
    or when inc_fmt is called.

    Subclasses should override:
        _incr: when a simple '+' binary operation isn't sufficient.
        _str_fmt: when a simple str representation of the incremented object
        isn't the proper format.
    """
    def __init__(self, initial_value, increment):
        """
        :param initial_value: The first value to be returned.
        :param increment: Each iteration/inc_fmt call will return the previous
            value incremented by this.
        :type initial_value: object supporting the '+' binary operation
        :type increment: object supporting the '+' binary operation
        """
        self._value = initial_value
        self._increment = increment

    def _incr(self):
        """
        This function will be called in each iteration/inc_fmt call. Subclasses
        should override this when their object is incremented differently.
        The function must compute the next iterated value and store it in
        self._value.
        """
        self._value += self._increment

    def __next__(self):
        """
        Each iteration returns the current object and stores the incremented
        object (which will be returned in the next iteration). The first
        iteration returns the initial value.
        """
        return_value = self._value
        self._incr()
        return return_value

    def __iter__(self):
        return self

    def _str_fmt(self):
        """
        The string representation is a standard string representation of the
        incremented object. Subclasses may override this for a different
        string representation.
        """
        return str(self._value)

    def inc_fmt(self):
        """
        Return a string representation and increment the current value.
        """
        return_value = self._str_fmt()
        self._incr()
        return return_value
