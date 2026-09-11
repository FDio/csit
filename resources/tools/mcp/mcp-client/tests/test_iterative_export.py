import csv
import io
import unittest
import zipfile
from datetime import UTC, datetime

from iterative_export import (
    ITERATIVE_EXPORT_HEADERS,
    csv_export_bytes,
    default_iterative_export_filename,
    iterative_export_table,
    sanitized_iterative_export_filename,
    xlsx_export_bytes,
)
from tests.test_app import iterative_series_payload


class IterativeExportTests(unittest.TestCase):
    def test_table_columns_values_and_oldest_first_order(self):
        records = list(reversed(iterative_series_payload()["records"]))
        headers, rows = iterative_export_table(records)

        self.assertEqual(headers, ITERATIVE_EXPORT_HEADERS)
        self.assertEqual(rows[0][0], "2026-06-01 10:00")
        self.assertEqual(rows[-1][0], "2026-06-05 10:00")
        self.assertEqual(rows[0][1], "csit-vpp-perf-mrr-release-2n-skx")
        self.assertEqual(rows[0][2], 301)
        self.assertEqual(rows[0][3], "vpp")
        self.assertEqual(rows[0][4], "26.06-release")
        self.assertEqual(rows[0][5], "10.30.0.1, 10.30.0.2")
        self.assertEqual(rows[0][6], "trex")
        self.assertEqual(rows[0][8], 8_000_000)
        self.assertEqual(rows[0][9], "pps")
        self.assertEqual(rows[0][12], "")

    def test_csv_is_excel_friendly_utf8(self):
        headers, rows = iterative_export_table(
            iterative_series_payload()["records"][:1]
        )
        content = csv_export_bytes(headers, rows)
        parsed = list(csv.reader(io.StringIO(content.decode("utf-8-sig"))))

        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(parsed[0], ITERATIVE_EXPORT_HEADERS)
        self.assertEqual(parsed[1][0], "2026-06-01 10:00")

    def test_xlsx_contains_sortable_excel_table(self):
        headers, rows = iterative_export_table(
            iterative_series_payload()["records"][:2]
        )
        content = xlsx_export_bytes(headers, rows)

        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = set(archive.namelist())
            table = archive.read("xl/tables/table1.xml").decode()
            sheet = archive.read("xl/worksheets/sheet1.xml").decode()
        self.assertIn("xl/tables/table1.xml", names)
        self.assertIn('name="IterativeTable"', table)
        self.assertIn("autoFilter", table)
        self.assertIn("pane", sheet)

    def test_filename_default_and_sanitization(self):
        now = datetime(2026, 9, 11, 12, 13, 14, tzinfo=UTC)
        default = default_iterative_export_filename(now)

        self.assertEqual(default, "iterative-2026-09-11 12:13:14")
        self.assertEqual(
            sanitized_iterative_export_filename("../../my export.csv", default, "xlsx"),
            "my export.xlsx",
        )


if __name__ == "__main__":
    unittest.main()
