Overview
--------

This document describes a high-level design of a system for continuous
performance measuring, trending and change detection for FD.io VPP SW
data plane (and other performance tests run within CSIT sub-project).

There is a Performance Trending (PT) CSIT module, and a separate
Performance Analysis (PA) module ingesting results from PT and
analysing, detecting and reporting any performance anomalies using
historical data and statistical metrics. PA does also produce
trending dashboard, list of failed tests and graphs with summary and
drill-down views across all specified tests that can be reviewed and
inspected regularly by FD.io developers and users community.
