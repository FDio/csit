import unittest

import pandas as pd

from dashboard.services.statistics import (
    enrich_job_statistics,
    filter_job_statistics,
    parse_job_dimensions,
    statistics_counts,
)


class StatisticsServiceTests(unittest.TestCase):
    def test_parse_job_dimensions_supports_known_values_and_testbeds(self):
        cases = {
            "csit-dpdk-perf-hoststack-weekly-master-2n-icx": {
                "dut": "dpdk",
                "test_type": "hoststack",
                "cadence": "weekly",
                "testbed": "2n-icx",
            },
            "csit-trex-perf-mrr-daily-master-3na-spr": {
                "dut": "trex",
                "test_type": "mrr",
                "cadence": "daily",
                "testbed": "3na-spr",
            },
            "csit-vpp-perf-soak-daily-master-2n1l-nv": {
                "dut": "vpp",
                "test_type": "soak",
                "cadence": "daily",
                "testbed": "2n1l-nv",
            },
        }

        for job, expected in cases.items():
            with self.subTest(job=job):
                self.assertEqual(parse_job_dimensions(job), expected)

        self.assertEqual(
            parse_job_dimensions("unclassified-job"),
            {
                "dut": None,
                "test_type": None,
                "cadence": None,
                "testbed": None,
            },
        )

    def test_enrichment_joins_counts_without_mutating_sources(self):
        statistics = pd.DataFrame(
            {
                "job": [
                    "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "csit-vpp-perf-mrr-daily-master-3n-alt",
                ],
                "build": [101, 102],
                "duration": [100.0, 200.0],
            }
        )
        trending = pd.DataFrame(
            {
                "job": [
                    "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "csit-vpp-perf-mrr-daily-master-2n-skx",
                ],
                "build": ["101", "101", "101"],
                "passed": [True, False, None],
                "dut_version": ["24.10", "24.10", "24.11"],
                "hosts": [
                    ["10.0.0.1", "10.0.0.2"],
                    ["10.0.0.2", "10.0.0.3"],
                    "10.0.0.4",
                ],
            }
        )
        statistics_before = statistics.copy(deep=True)
        trending_before = trending.copy(deep=True)

        enriched = enrich_job_statistics(statistics, trending)

        first = enriched.iloc[0]
        second = enriched.iloc[1]
        self.assertEqual(first["passed_count"], 1)
        self.assertEqual(first["failed_count"], 1)
        self.assertEqual(first["total_test_count"], 2)
        self.assertTrue(first["counts_available"])
        self.assertEqual(first["dut_version"], "24.10, 24.11")
        self.assertEqual(
            first["hosts"],
            ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
        )
        self.assertEqual(second["passed_count"], 0)
        self.assertEqual(second["failed_count"], 0)
        self.assertFalse(second["counts_available"])
        self.assertIsNone(second["dut_version"])
        self.assertIsNone(second["hosts"])
        pd.testing.assert_frame_equal(statistics, statistics_before)
        pd.testing.assert_frame_equal(trending, trending_before)

    def test_cascading_filters_select_defaults_and_natural_testbed_order(self):
        data = pd.DataFrame(
            {
                "dut": ["vpp", "vpp", "vpp", "dpdk"],
                "test_type": ["mrr", "mrr", "ndrpdr", "mrr"],
                "cadence": ["daily", "daily", "weekly", "daily"],
                "testbed": ["10n-lab", "2n-skx", "3n-alt", "2n-dpdk"],
            }
        )

        filtered, options, selected, errors = filter_job_statistics(
            data,
            dut="vpp",
            test_type="missing",
            cadence=None,
            testbed=None,
            select_defaults=True,
        )

        self.assertEqual(options["dut"], ["dpdk", "vpp"])
        self.assertEqual(options["test_type"], ["mrr", "ndrpdr"])
        self.assertEqual(selected["test_type"], "mrr")
        self.assertEqual(options["cadence"], ["daily"])
        self.assertEqual(options["testbed"], ["2n-skx", "10n-lab"])
        self.assertEqual(selected["testbed"], "2n-skx")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(errors, [])

    def test_cascading_filters_prefer_phase_three_defaults(self):
        data = pd.DataFrame(
            {
                "dut": ["dpdk", "vpp", "vpp", "vpp"],
                "test_type": ["hoststack", "hoststack", "mrr", "mrr"],
                "cadence": ["weekly", "weekly", "weekly", "daily"],
                "testbed": ["2n-dpdk", "3n-alt", "10n-lab", "2n-skx"],
            }
        )

        filtered, options, selected, errors = filter_job_statistics(
            data,
            dut=None,
            test_type=None,
            cadence=None,
            testbed=None,
            select_defaults=True,
        )

        self.assertEqual(options["dut"], ["dpdk", "vpp"])
        self.assertEqual(selected, {
            "dut": "vpp",
            "test_type": "mrr",
            "cadence": "daily",
            "testbed": "2n-skx",
        })
        self.assertEqual(len(filtered), 1)
        self.assertEqual(errors, [])

    def test_cascading_filters_fall_back_when_preferred_values_are_absent(self):
        data = pd.DataFrame(
            {
                "dut": ["dpdk", "dpdk"],
                "test_type": ["hoststack", "hoststack"],
                "cadence": ["weekly", "weekly"],
                "testbed": ["10n-lab", "2n-lab"],
            }
        )

        filtered, _options, selected, errors = filter_job_statistics(
            data,
            dut=None,
            test_type=None,
            cadence=None,
            testbed=None,
            select_defaults=True,
        )

        self.assertEqual(selected, {
            "dut": "dpdk",
            "test_type": "hoststack",
            "cadence": "weekly",
            "testbed": "2n-lab",
        })
        self.assertEqual(len(filtered), 1)
        self.assertEqual(errors, [])

    def test_explicit_invalid_filter_reports_available_values(self):
        data = pd.DataFrame(
            {
                "dut": ["vpp"],
                "test_type": ["mrr"],
                "cadence": ["daily"],
                "testbed": ["2n-skx"],
            }
        )

        _filtered, _options, selected, errors = filter_job_statistics(
            data,
            dut="dpdk",
            test_type=None,
            cadence=None,
            testbed=None,
            select_defaults=False,
        )

        self.assertIsNone(selected["dut"])
        self.assertEqual(errors[0]["field"], "dut")
        self.assertEqual(errors[0]["available"], ["vpp"])

    def test_statistics_counts_reports_unclassified_and_unmatched(self):
        data = pd.DataFrame(
            {
                "dut": ["vpp", None],
                "test_type": ["mrr", None],
                "cadence": ["daily", None],
                "testbed": ["2n-skx", None],
                "counts_available": [True, False],
            }
        )

        self.assertEqual(
            statistics_counts(data),
            {"unclassified_row_count": 1, "unmatched_run_count": 1},
        )


if __name__ == "__main__":
    unittest.main()
