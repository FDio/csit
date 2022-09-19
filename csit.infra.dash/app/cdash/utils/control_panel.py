# Copyright (c) 2022 Cisco and/or its affiliates.
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


"""A module implementing the control panel data structure.
"""


from copy import deepcopy


class ControlPanel:
    """A class representing the control panel.
    """

    def __init__(self, params: dict, panel: dict=dict()) -> None:
        """Initialisation of the control pannel by default values. If
        particular values are provided (parameter "panel") they are set
        afterwards.

        :param params: Default values to be set to the control panel. This
            dictionary also defines the full set of the control panel's
            parameters and their order.
        :param panel: Custom values to be set to the control panel.
        :type params: dict
        :type panel: dict
        """

        if not params:
            raise ValueError("The params must be defined.")
        self._panel = deepcopy(params)
        for key in panel:
            if key in self._panel:
                self._panel[key] = panel[key]
            else:
                raise AttributeError(
                    f"The parameter {key} is not defined in the list of "
                    f"parameters."
                )

    @property
    def panel(self) -> dict:
        return self._panel

    def set(self, kwargs: dict=dict()) -> None:
        """Set the values of the Control panel.

        :param kwargs: key - value pairs to be set.
        :type kwargs: dict
        :raises KeyError: If the key in kwargs is not present in the Control
            panel.
        """
        for key, val in kwargs.items():
            if key in self._panel:
                self._panel[key] = val
            else:
                raise KeyError(f"The key {key} is not defined.")

    def get(self, key: str) -> any:
        """Returns the value of a key from the Control panel.

        :param key: The key which value should be returned.
        :type key: str
        :returns: The value of the key.
        :rtype: any
        :raises KeyError: If the key in kwargs is not present in the Control
            panel.
        """
        return self._panel[key]

    def values(self) -> tuple:
        """Returns the values from the Control panel as a list.

        :returns: The values from the Control panel.
        :rtype: list
        """
        return tuple(self._panel.values())
