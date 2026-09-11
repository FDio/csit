import csv
import io
import unittest
import zipfile
from datetime import UTC, datetime

from trending_export import (
    TRENDING_EXPORT_HEADERS,
    csv_export_bytes,
    default_trending_export_filename,
    sanitized_trending_export_filename,
    trending_export_table,
    xlsx_export_bytes,
)


class TrendingExportTests(unittest.TestCase):
    def test_table_uses_exact_columns_and_sorts_samples_oldest_first(self):
        records = [
            {
                "start_time": "2026-08-03T10:31:00+02:00",
                "job": "csit-vpp-perf-ndrpdr-daily-master-2n-emr",
                "build": 203,
                "dut_type": "vpp",
                "dut_version": "26.06-release",
                "hosts": ["host-a", "host-b", "host-a"],
                "tg_type": "trex",
                "test_id": "tests.vpp.perf.ip4.sample",
                "throughput_value": 10_000_000.0,
                "throughput_unit": "pps",
                "bandwidth_value": 25_000_000_000.5,
                "bandwidth_unit": "bps",
                "latency_value": 7.5,
                "latency_unit": "us",
            },
            {
                "start_time": "2026-08-01T09:00:00Z",
                "job": "older-job",
                "build": 201,
                "dut": "dpdk",
                "hosts": "host-c",
                "throughput_value": 9_000_000,
            },
        ]

        headers, rows = trending_export_table(records)

        self.assertEqual(headers, TRENDING_EXPORT_HEADERS)
        self.assertEqual(rows[0][0:6], [
            "2026-08-01 09:00", "older-job", 201, "dpdk", "", "host-c",
        ])
        self.assertEqual(rows[1][0], "2026-08-03 08:31")
        self.assertEqual(rows[1][5], "host-a, host-b")
        self.assertEqual(rows[1][6:10], [
            "trex", "tests.vpp.perf.ip4.sample", 10_000_000, "pps",
        ])
        self.assertEqual(rows[1][10:14], [
            25_000_000_000.5, "bps", 7.5, "us",
        ])

    def test_missing_or_non_finite_values_are_blank(self):
        _, rows = trending_export_table([{
            "start_time": "invalid",
            "build": "not-an-integer",
            "throughput_value": float("nan"),
            "bandwidth_value": None,
            "latency_value": float("inf"),
        }])

        self.assertEqual(rows[0], ["", "", "", "", "", "", "", "", "", "", "", "", "", ""])

    def test_default_filename_uses_exact_utc_timestamp_and_is_sanitized_safely(self):
        now = datetime(2026, 8, 10, 14, 30, 45, tzinfo=UTC)
        default = default_trending_export_filename(now)

        self.assertEqual(default, "trending-2026-08-10 14:30:45")
        self.assertEqual(
            sanitized_trending_export_filename(None, default, "xlsx"),
            "trending-2026-08-10 14:30:45.xlsx",
        )
        self.assertEqual(
            sanitized_trending_export_filename(
                '../../My "Trending" export.csv', default, "csv",
            ),
            "My Trending export.csv",
        )

    def test_csv_is_utf8_with_spreadsheet_header(self):
        content = csv_export_bytes(["date", "throughput"], [["2026-08-01 09:00", 7]])

        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
        self.assertEqual(rows, [["date", "throughput"], ["2026-08-01 09:00", "7"]])

    def test_xlsx_contains_sortable_table_and_frozen_header(self):
        content = xlsx_export_bytes(
            ["date", "throughput"],
            [["2026-08-01 09:00", 7], ["2026-08-02 09:00", 8]],
        )

        self.assertTrue(content.startswith(b"PK"))
        with zipfile.ZipFile(io.BytesIO(content)) as workbook:
            table = workbook.read("xl/tables/table1.xml").decode("utf-8")
            sheet = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn('name="TrendingTable"', table)
        self.assertIn("<autoFilter", table)
        self.assertIn('ySplit="1"', sheet)
        self.assertIn('state="frozen"', sheet)

    def test_empty_xlsx_still_has_headers_and_autofilter(self):
        content = xlsx_export_bytes(["date", "throughput"], [])

        with zipfile.ZipFile(io.BytesIO(content)) as workbook:
            sheet = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn("<autoFilter", sheet)
        self.assertIn('ySplit="1"', sheet)


if __name__ == "__main__":
    unittest.main()
