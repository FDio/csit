import csv
import io
import unittest
import zipfile

from statistics_export import (
    csv_export_bytes,
    default_export_filename,
    sanitized_export_filename,
    statistics_export_table,
    xlsx_export_bytes,
)


class StatisticsExportTests(unittest.TestCase):
    def test_table_uses_exact_columns_and_normalizes_rows_oldest_first(self):
        records = [
            {
                "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                "build": 202,
                "start_time": "2026-08-03T10:31:00+02:00",
                "duration": 3630,
                "dut_version": "25.02",
                "hosts": ["host-a", "host-b", "host-a"],
                "passed_count": 11,
                "failed_count": 2,
                "counts_available": True,
            },
            {
                "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                "build": 201,
                "start_time": "2026-08-01T09:00:00Z",
                "duration": 89,
                "counts_available": False,
            },
        ]
        failed = {
            ("csit-vpp-perf-mrr-daily-master-2n-skx", 202): [
                "failed-a",
                "failed-a",
            ]
        }

        headers, rows = statistics_export_table(
            records,
            dut="vpp",
            failed_tests=failed,
        )

        self.assertEqual(
            headers,
            [
                "build",
                "date",
                "duration",
                "passed",
                "failed",
                "vpp-ver",
                "csit-ref",
                "hosts",
                "Failed tests",
            ],
        )
        self.assertEqual(rows[0][0:5], [201, "2026-08-01 09:00", "00:01", "", ""])
        self.assertEqual(rows[1][0:6], [202, "2026-08-03 08:31", "01:01", 11, 2, "25.02"])
        self.assertEqual(rows[1][6], "csit-vpp-perf-mrr-daily-master-2n-skx/202")
        self.assertEqual(rows[1][7], "host-a, host-b")
        self.assertEqual(rows[1][8], "failed-a, failed-a")

    def test_filename_defaults_and_sanitization(self):
        filters = {
            "dut": "vpp",
            "test_type": "mrr",
            "cadence": "daily",
            "testbed": "2n-skx",
        }

        self.assertEqual(
            default_export_filename(filters),
            "stats-vpp-mrr-daily-2n-skx",
        )
        self.assertEqual(
            sanitized_export_filename(
                "../../My statistics.xlsx",
                "fallback",
                "csv",
            ),
            "My-statistics.csv",
        )

    def test_csv_is_utf8_with_spreadsheet_header(self):
        content = csv_export_bytes(["build", "Failed tests"], [[7, "test-a, test-b"]])

        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))
        self.assertEqual(rows, [["build", "Failed tests"], ["7", "test-a, test-b"]])

    def test_xlsx_contains_sortable_table_and_frozen_header(self):
        content = xlsx_export_bytes(
            ["build", "date"],
            [[1, "2026-08-01 09:00"], [2, "2026-08-02 09:00"]],
        )

        self.assertTrue(content.startswith(b"PK"))
        with zipfile.ZipFile(io.BytesIO(content)) as workbook:
            names = set(workbook.namelist())
            self.assertIn("xl/tables/table1.xml", names)
            table = workbook.read("xl/tables/table1.xml").decode("utf-8")
            sheet = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn('name="StatisticsTable"', table)
        self.assertIn("<autoFilter", table)
        self.assertIn('ySplit="1"', sheet)
        self.assertIn('state="frozen"', sheet)

    def test_empty_xlsx_still_has_headers_and_autofilter(self):
        content = xlsx_export_bytes(["build", "date"], [])

        with zipfile.ZipFile(io.BytesIO(content)) as workbook:
            sheet = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn("<autoFilter", sheet)
        self.assertIn('ySplit="1"', sheet)


if __name__ == "__main__":
    unittest.main()
