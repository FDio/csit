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

"""Metric library.

Time measurements are done by time.time().
Although time.time() is susceptible to big (or even negative) jumps
when a system is badly synchronized, it is still better
than time.monotonic(), as that value has no relation to epoch time.
"""

from collections import namedtuple
from threading import Lock
from time import time
import re


class Value:
    """
    A value storage protected by a mutex.
    """
    def __init__(self):
        """
        Initialize value to default and create a lock.
        """
        self._value = 0.0
        self._lock = Lock()
        self._timestamp = None

    def inc(self, amount):
        """
        Increment value by amount under mutex.
        Add a timestamp of capturing value.

        :param amount: Amount of increment.
        :type amount: int or float
        """
        with self._lock:
            self._value += amount
            self._timestamp = time()

    def set(self, value):
        """
        Set to a specific value under mutex.
        Add a timestamp of capturing value.

        :param value: Amount of increment.
        :type value: int or float
        """
        with self._lock:
            self._value = value
            self._timestamp = time()

    def get(self):
        """
        Get a value under mutex.

        :returns: Stored value.
        :rtype: int or float
        """
        with self._lock:
            return self._value

    def get_timestamp(self):
        """
        Get a timestamp under mutex.

        :returns: Stored timestamp.
        :rtype: str
        """
        with self._lock:
            return self._timestamp


class Metric:
    """
    A single metric parent and its samples.
    """
    def __init__(self, name, documentation, typ):
        """
        Initialize class and do basic sanitize.

        :param name: Full metric name.
        :param documentation: Metric HELP string.
        :param typ: Metric type [counter|gauge|info].
        :type name: str
        :type documentation: str
        :type typ: str
        """
        self.metric_types = (
            u"counter", u"gauge", u"info"
        )
        self.metric_sample = namedtuple(
            u"Sample", [u"name", u"labels", u"value", u"timestamp"]
        )

        if not re.compile(r"^[a-zA-Z_:\-][a-zA-Z0-9_:\-]*$").match(name):
            raise ValueError(f"Invalid metric name: {name}!")
        if typ not in self.metric_types:
            raise ValueError(f"Invalid metric type: {typ}!")

        self.name = name
        self.documentation = documentation
        self.type = typ
        self.samples = []

    def add_sample(self, name, labels, value, timestamp):
        """
        Add a sample (entry) to the metric.

        :param name: Full metric name.
        :param labels: Metric labels.
        :param value: Metric value.
        :param timestamp: Timestamp. Default to be when accessed.
        :type name: str
        :type lables: tuple
        :type value: int or float
        :type timestamp: float
        """
        self.samples.append(
            self.metric_sample(name, labels, value, timestamp)
        )

    def __eq__(self, other):
        """
        Check equality of added metric.

        :param other: Metric to compare.
        :type other: Metric
        """
        return (isinstance(other, Metric)
                and self.name == other.name
                and self.documentation == other.documentation
                and self.type == other.type
                and self.samples == other.samples)

    def __repr__(self):
        """
        Represantation as a string for a debug print.
        """
        return (
            f"Metric({self.name}, "
            f"{self.documentation}, "
            f"{self.type}, "
            f"{self.samples})"
        )


class MetricBase:
    """
    Abstract class for Metric implementation.
    """
    _type = None

    def __init__(
            self, name, documentation, labelnames=(), namespace="",
            subsystem="", labelvalues=None,
        ):
        """
        Metric initialization.

        :param name: Metric name.
        :param documentation: Metric HELP string.
        :param labelnames: Metric label list.
        :param namespace: Metric namespace (will be added as prefix).
        :param subsystem: Metric susbsystem (will be added as prefix).
        :param labelvalues: Metric label values.
        :type name: str
        :type documentation: str
        :type labelnames: list
        :type namespace: str
        :type subsystem: str
        :type labelvalues: list
        """
        self._name = self.validate_name(name, namespace, subsystem)
        self._labelnames = self.validate_labelnames(labelnames)
        self._labelvalues = tuple(labelvalues or ())
        self._documentation = documentation

        if self._is_parent():
            self._lock = Lock()
            self._metrics = {}

        if self._is_observable():
            self._metric_init()

    @staticmethod
    def validate_name(name, namespace, subsystem):
        """
        Construct metric full name and validate naming convention.

        :param name: Metric name.
        :param namespace: Metric namespace (will be added as prefix).
        :param subsystem: Metric susbsystem (will be added as prefix).
        :type name: str
        :type namespace: str
        :type subsystem: str
        :returns: Metric full name.
        :rtype: str
        :rasies ValueError: If name does not conform with naming conventions.
        """
        full_name = u""
        full_name += f"{namespace}_" if namespace else u""
        full_name += f"{subsystem}_" if subsystem else u""
        full_name += name

        if not re.compile(r"^[a-zA-Z_:\-][a-zA-Z0-9_:\-]*$").match(full_name):
            raise ValueError(
                f"Invalid metric name: {full_name}!"
            )
        return full_name

    @staticmethod
    def validate_labelnames(labelnames):
        """
        Create label tuple and validate naming convention.

        :param labelnames: Metric label list.
        :type labelnames: list
        :returns: Label names.
        :rtype: tuple
        :rasies ValueError: If name does not conform with naming conventions.
        """
        labelnames = tuple(labelnames)
        for label in labelnames:
            if not re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$").match(label):
                raise ValueError(f"Invalid label metric name: {label}!")
            if re.compile(r"^__.*$").match(label):
                raise ValueError(f"Reserved label metric name: {label}!")
        return labelnames

    def _is_observable(self):
        """
        Check whether this metric is observable, i.e.
        * a metric without label names and values, or
        * the child of a labelled metric.

        :return: Observable
        :rtype: bool
        """
        return not self._labelnames or (self._labelnames and self._labelvalues)

    def _is_parent(self):
        """
        Check whether metric is parent, i.e.
        * a metric with label names but not its values.

        :return: Parent
        :rtype: bool
        """
        return self._labelnames and not self._labelvalues

    def _get_metric(self):
        """
        Returns metric that will handle samples.

        :returns: Metric object.
        :rtype: Metric
        """
        return Metric(self._name, self._documentation, self._type)

    def describe(self):
        """
        Returns metric that will handle samples.

        :returns: List of metric objects.
        :rtype: list
        """
        return [self._get_metric()]

    def collect(self):
        """
        Returns metric with samples.

        :returns: List with metric object.
        :rtype: list
        """
        metric = self._get_metric()
        for suffix, labels, value, timestamp in self.samples():
            metric.add_sample(self._name + suffix, labels, value, timestamp)
        return [metric]

    def labels(self, *labelvalues, **labelkwargs):
        """
        Return the child for the given labelset.

        :param labelvalues: Label values.
        :param labelkwargs: Dictionary with label names and values.
        :type labelvalues: list
        :type labelkwargs: dict
        :returns: Metric with labels and values.
        :rtype: Metric
        :raises ValueError: If labels were not initialized.
        :raises ValueError: If labels are already set (chaining).
        :raises ValueError: If both parameters are passed.
        :raises ValueError: If label values are not matching label names.
        """
        if not self._labelnames:
            raise ValueError(
                f"No label names were set when constructing {self}!"
            )

        if self._labelvalues:
            raise ValueError(
                f"{self} already has labels set; can not chain .labels() calls!"
            )

        if labelvalues and labelkwargs:
            raise ValueError(
                u"Can't pass both *args and **kwargs!"
            )

        if labelkwargs:
            if sorted(labelkwargs) != sorted(self._labelnames):
                raise ValueError(u"Incorrect label names!")
            labelvalues = tuple(labelkwargs[l] for l in self._labelnames)
        else:
            if len(labelvalues) != len(self._labelnames):
                raise ValueError(u"Incorrect label count!")
            labelvalues = tuple(l for l in labelvalues)
        with self._lock:
            if labelvalues not in self._metrics:
                self._metrics[labelvalues] = self.__class__(
                    self._name,
                    documentation=self._documentation,
                    labelnames=self._labelnames,
                    labelvalues=labelvalues
                )
            return self._metrics[labelvalues]

    def samples(self):
        """
        Returns samples whether an object is parent or child.

        :returns: List of Metric objects with values.
        :rtype: list
        """
        if self._is_parent():
            return self._multi_samples()
        return self._child_samples()

    def _multi_samples(self):
        """
        Returns parent and its childs with its values.

        :returns: List of Metric objects with values.
        :rtype: list
        """
        with self._lock:
            metrics = self._metrics.copy()
        for labels, metric in metrics.items():
            series_labels = list(zip(self._labelnames, labels))
            for suffix, sample_labels, value, timestamp in metric.samples():
                yield (
                    suffix, dict(series_labels + list(sample_labels.items())),
                    value, timestamp
                )

    def _child_samples(self):
        """
        Returns child with its values. Should be implemented by child class.

        :raises NotImplementedError: If implementation in not in subclass.
        """
        raise NotImplementedError(
            f"_child_samples() must be implemented by {self}!"
        )

    def _metric_init(self):
        """
        Initialize the metric object as a child.

        :raises NotImplementedError: If implementation in not in subclass.
        """
        raise NotImplementedError(
            f"_metric_init() must be implemented by {self}!"
        )

    def __str__(self):
        """
        String for a debug print.
        """
        return f"{self._type}:{self._name}"

    def __repr__(self):
        """
        Represantation as a string for a debug print.
        """
        metric_type = type(self)
        return f"{metric_type.__module__}.{metric_type.__name__}({self._name})"


class Counter(MetricBase):
    """
    A Counter tracks counts of events or running totals.
    """
    _type = u"counter"

    def __init__(self,
                 name,
                 documentation,
                 labelnames=(),
                 namespace=u"",
                 subsystem=u"",
                 labelvalues=None
                 ):
        """
        Initialize the Counter metric object.

        :param name: Metric name.
        :param documentation: Metric HELP string.
        :param labelnames: Metric label list.
        :param namespace: Metric namespace (will be added as prefix).
        :param subsystem: Metric susbsystem (will be added as prefix).
        :param labelvalues: Metric label values.
        :type name: str
        :type documentation: str
        :type labelnames: list
        :type namespace: str
        :type subsystem: str
        :type labelvalues: list
        """
        super(Counter, self).__init__(
            name=name,
            documentation=documentation,
            labelnames=labelnames,
            namespace=namespace,
            subsystem=subsystem,
            labelvalues=labelvalues,
        )

    def _metric_init(self):
        """
        Initialize counter value.
        """
        self._value = Value()

    def inc(self, amount=1):
        """
        Increment counter by the given amount.

        :param amount: Amount to increment.
        :type amount: int or float
        :raises ValueError: If amout is not positive.
        """
        if amount < 0:
            raise ValueError(
                u"Counters can only be incremented by non-negative amounts."
            )
        self._value.inc(amount)

    def _child_samples(self):
        """
        Returns list of child samples.

        :returns: List of child samples.
        :rtype: tuple
        """
        return ((u"", {}, self._value.get(), self._value.get_timestamp()),)


class Gauge(MetricBase):
    """
    Gauge metric, to report instantaneous values.
    """
    _type = u"gauge"

    def __init__(self,
                 name,
                 documentation,
                 labelnames=(),
                 namespace=u"",
                 subsystem=u"",
                 labelvalues=None
                 ):
        """
        Initialize the Gauge metric object.

        :param name: Metric name.
        :param documentation: Metric HELP string.
        :param labelnames: Metric label list.
        :param namespace: Metric namespace (will be added as prefix).
        :param subsystem: Metric susbsystem (will be added as prefix).
        :param labelvalues: Metric label values.
        :type name: str
        :type documentation: str
        :type labelnames: list
        :type namespace: str
        :type subsystem: str
        :type labelvalues: list
        """
        super(Gauge, self).__init__(
            name=name,
            documentation=documentation,
            labelnames=labelnames,
            namespace=namespace,
            subsystem=subsystem,
            labelvalues=labelvalues,
        )

    def _metric_init(self):
        """
        Initialize gauge value.
        """
        self._value = Value()

    def inc(self, amount=1):
        """
        Increment gauge by the given amount.

        :param amount: Amount to increment.
        :type amount: int or float
        """
        self._value.inc(amount)

    def dec(self, amount=1):
        """
        Decrement gauge by the given amount.

        :param amount: Amount to decrement.
        :type amount: int or float
        """
        self._value.inc(-amount)

    def set(self, value):
        """
        Set gauge to the given value.

        :param amount: Value to set.
        :type amount: int or float
        """
        self._value.set(float(value))

    def _child_samples(self):
        """
        Returns list of child samples.

        :returns: List of child samples.
        :rtype: tuple
        """
        return ((u"", {}, self._value.get(), self._value.get_timestamp()),)


class Info(MetricBase):
    """
    Info metric, key-value pairs.
    """
    _type = u"info"

    def __init__(self,
                 name,
                 documentation,
                 labelnames=(),
                 namespace=u"",
                 subsystem=u"",
                 labelvalues=None
                 ):
        """
        Initialize the Info metric object.

        :param name: Metric name.
        :param documentation: Metric HELP string.
        :param labelnames: Metric label list.
        :param namespace: Metric namespace (will be added as prefix).
        :param subsystem: Metric susbsystem (will be added as prefix).
        :param labelvalues: Metric label values.
        :type name: str
        :type documentation: str
        :type labelnames: list
        :type namespace: str
        :type subsystem: str
        :type labelvalues: list
        """
        super(Info, self).__init__(
            name=name,
            documentation=documentation,
            labelnames=labelnames,
            namespace=namespace,
            subsystem=subsystem,
            labelvalues=labelvalues,
        )

    def _metric_init(self):
        """
        Initialize gauge value and time it was created.
        """
        self._labelname_set = set(self._labelnames)
        self._lock = Lock()
        self._value = {}

    def info(self, value):
        """
        Set info to the given value.

        :param value: Value to set.
        :type value: int or float
        :raises ValueError: If labels are overlapping.
        """
        if self._labelname_set.intersection(value.keys()):
            raise ValueError(
                u"Overlapping labels for Info metric, "
                f"metric: {self._labelnames} child: {value}!"
            )
        with self._lock:
            self._value = dict(value)

    def _child_samples(self):
        """
        Returns list of child samples.

        :returns: List of child samples.
        :rtype: tuple
        """
        with self._lock:
            return ((u"_info", self._value, 1.0, time()),)
