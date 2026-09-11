import csv
import io
import unittest
import zipfile
from datetime import UTC, datetime

from coverage_export import (
    COVERAGE_EXPORT_HEADERS,
    coverage_export_table,
    csv_export_bytes,
    default_coverage_export_filename,
    sanitized_coverage_export_filename,
    xlsx_export_bytes,
)


class CoverageExportTests(unittest.TestCase):
    def test_table_uses_exact_headers_natural_order_and_blanks(self):
        records = [
            {
                "suite": "suite-10",
                "test_name": "1518B-2c-test",
                "throughput_unit": "pps",
                "throughput_ndr": 12.5,
                "throughput_ndr_gbps": None,
                "throughput_pdr": 14.0,
                "throughput_pdr_gbps": 21.25,
                "latency_forward_pdr_10_p50": 22,
            },
            {
                "suite": "suite-2",
                "test_name": "64B-1c-test",
                "throughput_unit": "pps",
                "throughput_ndr": 10.0,
            },
        ]

        headers, rows = coverage_export_table(records)

        self.assertEqual(headers, COVERAGE_EXPORT_HEADERS)
        self.assertEqual(rows[0][0:4], ["suite-2", "64B-1c-test", "pps", 10])
        self.assertEqual(rows[1][0:7], [
            "suite-10", "1518B-2c-test", "pps", 12.5, "", 14, 21.25,
        ])
        self.assertEqual(rows[1][7], 22)

    def test_csv_is_utf8_bom_and_xlsx_has_table_and_autofilter(self):
        headers, rows = coverage_export_table([{
            "suite": "IPv4",
            "test_name": "64B-1c-test",
        }])
        csv_data = csv_export_bytes(headers, rows)
        parsed = list(csv.reader(io.StringIO(csv_data.decode("utf-8-sig"))))
        self.assertEqual(parsed[0], headers)

        xlsx_data = xlsx_export_bytes(headers, rows)
        with zipfile.ZipFile(io.BytesIO(xlsx_data)) as archive:
            names = set(archive.namelist())
            self.assertIn("xl/tables/table1.xml", names)
            table = archive.read("xl/tables/table1.xml").decode()
            self.assertIn("autoFilter", table)
            self.assertIn("CoverageTable", table)

    def test_filename_defaults_and_sanitization(self):
        default = default_coverage_export_filename(
            datetime(2026, 9, 16, 12, 13, 14, tzinfo=UTC),
        )
        self.assertEqual(default, "coverage-2026-09-16 12:13:14")
        self.assertEqual(
            sanitized_coverage_export_filename("../my\nfile.csv", default, "xlsx"),
            "myfile.xlsx",
        )


if __name__ == "__main__":
    unittest.main()
