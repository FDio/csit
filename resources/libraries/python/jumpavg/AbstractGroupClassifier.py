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

"""Module holding AbstractGroupClassifier class."""

from abc import ABCMeta, abstractmethod


class AbstractGroupClassifier(object):
    """Abstract class defining API for classifier.

    The classifier is an object with classify() method
    which divides data into groups containing metadata.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def classify(self, values):
        """Divide values into consecutive groups with metadata.

        The metadata does not need to follow any specific rules,
        although progression/regression/outlier description would be fine.

        :param values: Sequence of runs to classify.
        :type values: Iterable of float or of AvgStdevMetadata
        :returns: Classified groups
        :rtype: Iterable of RunGroup
        """
        pass
