import io
import unittest
import zipfile

from comparison_export import (
    RAW_HEADERS,
    comparison_data_export,
    comparison_table_export,
    csv_export_bytes,
    sanitized_comparison_export_filename,
    xlsx_export_bytes,
)


class ComparisonExportTests(unittest.TestCase):
    def test_summary_headers_rows_csv_and_xlsx(self):
        records = [{
            "test_name": "64B-1c-ip4base",
            "unit": "MPPS",
            "reference_mean": 10,
            "reference_stdev": None,
            "compared_mean": 12.5,
            "compared_stdev": 0.4,
            "relative_change_mean": 25,
            "relative_change_stdev": None,
        }]
        headers, rows = comparison_table_export(records, "reference", "compare")

        self.assertEqual(headers[0], "Test Name")
        self.assertEqual(headers[1], "reference [MPPS] Mean")
        self.assertEqual(headers[-1], "Relative Change [%] Stdev")
        self.assertEqual(rows[0], ["64B-1c-ip4base", 10, "", 12.5, 0.4, 25, ""])
        self.assertTrue(csv_export_bytes(headers, rows).startswith(b"\xef\xbb\xbf"))
        workbook = xlsx_export_bytes(headers, rows, view="table")
        with zipfile.ZipFile(io.BytesIO(workbook)) as archive:
            self.assertIn("xl/tables/table1.xml", archive.namelist())
            table = archive.read("xl/tables/table1.xml")
            self.assertIn(b"autoFilter", table)

    def test_raw_export_has_exact_order_and_deterministic_sort(self):
        records = [
            {"ref_cmp": "compare", "start_time": "2026-02-01", "job": "b", "build": 2, "hosts": ["b", "a"]},
            {"ref_cmp": "reference", "start_time": "2026-01-01", "job": "a", "build": 1, "hosts": ["a"]},
        ]
        headers, rows = comparison_data_export(records)

        self.assertEqual(headers, RAW_HEADERS)
        self.assertEqual(rows[0][-1], "reference")
        self.assertEqual(rows[0][5], "a")
        self.assertEqual(rows[1][-1], "compare")
        self.assertEqual(rows[1][5], "b, a")

    def test_filename_is_sanitized(self):
        self.assertEqual(
            sanitized_comparison_export_filename(
                "../../comparison\n.csv", "fallback", "xlsx"
            ),
            "comparison.xlsx",
        )


if __name__ == "__main__":
    unittest.main()
