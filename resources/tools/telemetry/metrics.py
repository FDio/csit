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

"""Metric library."""

from collections import namedtuple
from importlib import import_module
from logging import getLogger
from re import compile
from threading import Lock
from time import time


class Value:
    """
    A value protected by a mutex.
    """
    def __init__(self):
        """
        """
        self._value = 0.0
        self._lock = Lock()

    def inc(self, amount):
        """
        """
        with self._lock:
            self._value += amount

    def set(self, value):
        """
        """
        with self._lock:
            self._value = value

    def get(self):
        """
        """
        with self._lock:
            return self._value


class Metric(object):
    """
    A single metric family and its samples.
    """
    def __init__(self, name, documentation, typ):
        """
        """
        self.metric_types = (
            u"counter", u"gauge", u"info"
        )
        self.metric_sample = namedtuple(
            u"Sample", [u"name", u"labels", u"value", u"timestamp"]
        )

        if not compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$").match(name):
            raise ValueError(u"Invalid metric name: {name}")
        if typ not in self.metric_types:
            raise ValueError(u"Invalid metric type: {typ}")

        self.name = name
        self.documentation = documentation
        self.type = typ
        self.samples = []

    def add_sample(self, name, labels, value, timestamp=time()):
        """
        Add a sample to the metric.
        """
        self.samples.append(
            self.metric_sample(name, labels, value, timestamp)
        )

    def __eq__(self, other):
        """
        """
        return (isinstance(other, Metric)
            and self.name == other.name
            and self.documentation == other.documentation
            and self.type == other.type
            and self.samples == other.samples
        )

    def __repr__(self):
        """
        """
        return (
            f"Metric({self.name}, "
            f"{self.documentation}, "
            f"{self.type}, "
            f"{self.samples})"
        )


class MetricBase:
    _type = None

    def __init__(
            self, name, documentation, labelnames=(), namespace="",
            subsystem="", labelvalues=None,
        ):
        """
        """
        self._name = self.validate_name(self._type, name, namespace, subsystem)
        self._labelnames = self.validate_labelnames(labelnames)
        self._labelvalues = tuple(labelvalues or ())
        self._documentation = documentation

        if self._is_parent():
            self._lock = Lock()
            self._metrics = {}

        if self._is_observable():
            self._metric_init()

    def validate_name(self, metric_type, name, namespace, subsystem):
        """
        """
        full_name = u""
        full_name += f"{namespace}_" if namespace else u""
        full_name += f"{subsystem}_" if subsystem else u""
        full_name += name

        if not compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$").match(full_name):
            raise ValueError(
                f"Invalid metric name: {full_name}"
            )
        return full_name

    def validate_labelnames(self, labelnames):
        """
        """
        labelnames = tuple(labelnames)
        for label in labelnames:
            if not compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$").match(label):
                raise ValueError(f"Invalid label metric name: {label}")
            if compile(r"^__.*$").match(label):
                raise ValueError(f"Reserved label metric name: {label}")
        return labelnames

    def _is_observable(self):
        # Whether this metric is observable, i.e.
        # * a metric without label names and values, or
        # * the child of a labelled metric.
        return not self._labelnames or (self._labelnames and self._labelvalues)

    def _raise_if_not_observable(self):
        # Functions that mutate the state of the metric, for example incrementing
        # a counter, will fail if the metric is not observable, because only if a
        # metric is observable will the value be initialized.
        if not self._is_observable():
            raise ValueError(u"Metric is missing label values")

    def _is_parent(self):
        """
        """
        return self._labelnames and not self._labelvalues

    def _get_metric(self):
        """
        """
        return Metric(self._name, self._documentation, self._type)

    def describe(self):
        """
        """
        return [self._get_metric()]

    def collect(self):
        """
        """
        metric = self._get_metric()
        for suffix, labels, value in self._samples():
            metric.add_sample(self._name + suffix, labels, value)
        return [metric]


    def labels(self, *labelvalues, **labelkwargs):
        """
        Return the child for the given labelset.
        """
        if not self._labelnames:
            raise ValueError(
                u"No label names were set when constructing {self}"
            )

        if self._labelvalues:
            raise ValueError(
                u"{self} already has labels set; can not chain .labels() calls"
            )

        if labelvalues and labelkwargs:
            raise ValueError(u"Can't pass both *args and **kwargs")

        if labelkwargs:
            if sorted(labelkwargs) != sorted(self._labelnames):
                raise ValueError(u"Incorrect label names")
            labelvalues = tuple(labelkwargs[l] for l in self._labelnames)
        else:
            if len(labelvalues) != len(self._labelnames):
                raise ValueError(u"Incorrect label count")
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

    def _samples(self):
        """
        """
        if self._is_parent():
            return self._multi_samples()
        else:
            return self._child_samples()

    def _multi_samples(self):
        """
        """
        with self._lock:
            metrics = self._metrics.copy()
        for labels, metric in metrics.items():
            series_labels = list(zip(self._labelnames, labels))
            for suffix, sample_labels, value in metric._samples():
                yield (
                    suffix, dict(series_labels + list(sample_labels.items())),
                    value
                )

    def _child_samples(self):
        """
        """
        raise NotImplementedError(
            f"_child_samples() must be implemented by {self}"
        )

    def _metric_init(self):
        """
        Initialize the metric object as a child, i.e. when it has labels
        (if any) set.
        """
        raise NotImplementedError(
            f"_metric_init() must be implemented by {self}"
        )

    def __str__(self):
        """
        """
        return f"{self._type}:{self._name}"

    def __repr__(self):
        """
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
        """
        self._value = Value()
        self._created = time()

    def inc(self, amount=1):
        """
        Increment counter by the given amount.
        """
        if amount < 0:
            raise ValueError(
                u"Counters can only be incremented by non-negative amounts.")
        self._value.inc(amount)

    def _child_samples(self):
        """
        """
        return ((u"", {}, self._value.get()),)


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
        """
        self._value = Value()
        self._created = time()

    def inc(self, amount=1):
        """
        Increment gauge by the given amount.
        """
        self._value.inc(amount)

    def dec(self, amount=1):
        """
        Decrement gauge by the given amount.
        """
        self._value.inc(-amount)

    def set(self, value):
        """
        Set gauge to the given value.
        """
        self._value.set(float(value))

    def _child_samples(self):
        """
        """
        return ((u"", {}, self._value.get()),)


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
        """
        self._labelname_set = set(self._labelnames)
        self._lock = Lock()
        self._value = {}

    def info(self, val):
        """
        Set info metric.
        """
        if self._labelname_set.intersection(val.keys()):
            raise ValueError(
                u"Overlapping labels for Info metric, "
                f"metric: {self._labelnames} child: {val}"
            )
        with self._lock:
            self._value = dict(val)

    def _child_samples(self):
        """
        """
        with self._lock:
            return (('_info', self._value, 1.0,),)
