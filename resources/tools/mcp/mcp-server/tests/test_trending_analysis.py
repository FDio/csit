import math
import unittest
from unittest.mock import patch

import pandas as pd

from dashboard.services.trending_analysis import (
    METRIC_DIRECTIONS,
    _performance_classification,
    analyze_trending_points,
)


def semantic_points(values, *, metric="throughput", unit="pps"):
    records = []
    for index, value in enumerate(values):
        records.append({
            "series_id": "series-a",
            "start_time": f"2026-08-{index + 1:02d}T10:00:00+00:00",
            "build": 100 + index,
            f"{metric}_value": value,
            f"{metric}_unit": unit,
        })
    return pd.DataFrame(records)


class TrendingAnalysisTests(unittest.TestCase):
    def test_metric_directions_make_latency_explicitly_lower_is_better(self):
        self.assertEqual(METRIC_DIRECTIONS, {
            "throughput": "higher",
            "bandwidth": "higher",
            "latency": "lower",
        })
        self.assertEqual(
            _performance_classification(
                "regression", preferred_direction="lower",
            ),
            "progression",
        )
        self.assertEqual(
            _performance_classification(
                "progression", preferred_direction="lower",
            ),
            "regression",
        )
        self.assertEqual(
            _performance_classification(
                "regression", preferred_direction="higher",
            ),
            "regression",
        )

    def test_jumpavg_groups_decorate_only_changed_group_boundaries(self):
        values = [
            10.0, 10.1, 9.9,
            13.0, 13.1, 12.9,
            8.0, 8.1, 7.9,
        ]

        analyzed, metadata = analyze_trending_points(semantic_points(values))
        results = analyzed["throughput_analysis"].tolist()

        self.assertEqual(results[0]["classification"], "normal")
        self.assertEqual(results[3]["classification"], "progression")
        self.assertEqual(results[4]["classification"], "normal")
        self.assertEqual(results[6]["classification"], "regression")
        self.assertEqual(results[7]["classification"], "normal")
        self.assertAlmostEqual(results[0]["trend"], 10.0)
        self.assertAlmostEqual(results[3]["trend"], 13.0)
        self.assertAlmostEqual(results[6]["trend"], 8.0)
        self.assertAlmostEqual(results[0]["stdev"], 0.0816496581)
        self.assertEqual(metadata["engine"], "jumpavg")
        self.assertEqual(metadata["version"], "0.4.2")
        self.assertEqual(metadata["classified_series_metrics"], 1)
        self.assertEqual(metadata["skipped_series_metrics"], 0)

    def test_lower_latency_is_classified_by_performance_direction(self):
        values = [
            10.0, 10.1, 9.9,
            7.0, 7.1, 6.9,
            12.0, 12.1, 11.9,
        ]

        analyzed, _metadata = analyze_trending_points(
            semantic_points(values, metric="latency", unit="us")
        )
        results = analyzed["latency_analysis"].tolist()

        self.assertEqual(results[3]["classification"], "progression")
        self.assertEqual(results[6]["classification"], "regression")
        self.assertAlmostEqual(results[3]["trend"], 7.0)
        self.assertAlmostEqual(results[6]["trend"], 12.0)

    def test_analysis_sorts_by_time_then_build_and_preserves_input_rows(self):
        points = semantic_points([13.0, 10.0, 10.1, 9.9])
        points.loc[0, "start_time"] = "2026-08-04T10:00:00+00:00"
        points.loc[1:, "start_time"] = "2026-08-01T10:00:00+00:00"
        points.loc[1:, "build"] = [101, 102, 103]

        analyzed, _metadata = analyze_trending_points(points)

        self.assertEqual(len(analyzed), len(points))
        self.assertEqual(
            analyzed.loc[0, "throughput_analysis"]["classification"],
            "progression",
        )

    def test_missing_values_are_skipped_and_units_are_analyzed_separately(self):
        points = semantic_points([1.0, math.nan, 1.1, 1000.0, 1010.0])
        points.loc[3:, "throughput_unit"] = "kbps"

        analyzed, metadata = analyze_trending_points(points)

        self.assertIsNone(analyzed.loc[1, "throughput_analysis"])
        self.assertIsNotNone(analyzed.loc[0, "throughput_analysis"])
        self.assertIsNotNone(analyzed.loc[3, "throughput_analysis"])
        self.assertEqual(metadata["classified_series_metrics"], 2)

    def test_single_sample_is_a_normal_zero_stdev_trend(self):
        analyzed, metadata = analyze_trending_points(semantic_points([5.0]))

        result = analyzed.loc[0, "throughput_analysis"]
        self.assertEqual(result, {
            "trend": 5.0,
            "stdev": 0.0,
            "classification": "normal",
        })
        self.assertEqual(metadata["classified_series_metrics"], 1)

    def test_classification_failure_is_reported_without_losing_samples(self):
        points = semantic_points([1.0, 2.0])

        with patch(
                "dashboard.services.trending_analysis.classify",
                side_effect=RuntimeError("classification failed"),
            ):
            analyzed, metadata = analyze_trending_points(points)

        self.assertEqual(analyzed["throughput_value"].tolist(), [1.0, 2.0])
        self.assertTrue(analyzed["throughput_analysis"].isna().all())
        self.assertEqual(metadata["classified_series_metrics"], 0)
        self.assertEqual(metadata["skipped_series_metrics"], 1)
        self.assertEqual(metadata["errors"][0]["metric"], "throughput")
        self.assertEqual(
            metadata["errors"][0]["message"], "classification failed"
        )


if __name__ == "__main__":
    unittest.main()
