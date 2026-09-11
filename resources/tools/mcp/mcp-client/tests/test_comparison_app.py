import csv
import io
import unittest

from starlette.testclient import TestClient

from app import create_app
from tests.test_app import (
    FakeMCPClient,
    FakeMCPContextFactory,
    comparison_catalog_payload,
    comparison_table_payload,
)


QUERY = (
    "release=rls2606&dut=vpp&dut_version=26.06-release&"
    "infra=2n-skx-100ge2p1e810cq-avf&framesize=64B&cores=1c&"
    "test_type=mrr&parameter=dut_version&value=rls2610%3A%3A26.10-release"
)


def comparison_data_payload():
    return {
        "schema_version": 1,
        "dataset": "comparison_data",
        "row_count": 1,
        "returned_count": 1,
        "offset": 0,
        "limit": 500,
        "has_more": False,
        "next_offset": None,
        "records": [{
            "job": "csit-vpp-perf-mrr-release-2n-skx",
            "build": 1,
            "dut_type": "vpp",
            "dut_version": "26.06-release",
            "tg_type": "trex",
            "hosts": ["10.0.0.1"],
            "start_time": "2026-01-01T10:00:00+00:00",
            "passed": False,
            "test_id": "tests.vpp.perf.ip4.example",
            "test_type": "mrr",
            "release": "rls2606",
            "ref_cmp": "reference",
        }],
    }


class ComparisonAppTests(unittest.TestCase):
    def test_initial_comparison_calls_only_catalog(self):
        fake = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get("/?dataset=comparison")

        self.assertEqual(response.status_code, 200)
        self.assertIn('aria-current="page">Comparison</a>', response.text)
        self.assertEqual(fake.calls, [
            ("datasets", {}),
            ("comparison_catalog", {}),
        ])

    def test_complete_comparison_loads_table_with_outlier_flag(self):
        fake = FakeMCPClient(payloads={
            "comparison_catalog": comparison_catalog_payload(complete=True),
            "comparison_table": comparison_table_payload(),
        })
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get(
                f"/?dataset=comparison&{QUERY}&remove_extreme_outliers=true"
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("64B-1c-ethip4-ip4base", response.text)
        self.assertEqual(fake.calls[2][0], "comparison_table")
        self.assertTrue(fake.calls[2][1]["remove_extreme_outliers"])
        self.assertEqual(fake.calls[2][1]["offset"], 0)

    def test_comparison_json_errors_are_inline_and_thrown_errors_are_503(self):
        fake = FakeMCPClient(payloads={
            "comparison_catalog": {
                "error": "data_unavailable", "message": "Iterative is loading.",
            },
        })
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get("/?dataset=comparison")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Iterative is loading.", response.text)

        fake = FakeMCPClient(tool_errors={
            "comparison_catalog": RuntimeError("comparison down"),
        })
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get("/?dataset=comparison")
        self.assertEqual(response.status_code, 503)
        self.assertIn("comparison down", response.text)

    def test_table_and_raw_csv_exports(self):
        fake = FakeMCPClient(payloads={
            "comparison_table": comparison_table_payload(),
            "comparison_data": comparison_data_payload(),
        })
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            table = client.get(
                f"/api/comparison/export?view=table&format=csv&{QUERY}"
            )
            raw = client.get(
                f"/api/comparison/export?view=data&format=csv&{QUERY}"
            )

        self.assertEqual(table.status_code, 200)
        self.assertEqual(raw.status_code, 200)
        table_rows = list(csv.reader(io.StringIO(table.content.decode("utf-8-sig"))))
        raw_rows = list(csv.reader(io.StringIO(raw.content.decode("utf-8-sig"))))
        self.assertEqual(table_rows[0][0], "Test Name")
        self.assertEqual(raw_rows[0][-1], "ref/cmp")
        self.assertEqual(raw_rows[1][-1], "reference")
        self.assertIn("comparison-table-", table.headers["content-disposition"])
        self.assertIn("comparison-data-", raw.headers["content-disposition"])

    def test_export_validates_view_and_complete_selection(self):
        fake = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            invalid_view = client.get("/api/comparison/export?view=nope")
            incomplete = client.get("/api/comparison/export?view=table")

        self.assertEqual(invalid_view.status_code, 400)
        self.assertEqual(incomplete.status_code, 400)

    def test_export_follows_pagination_and_rejects_malformed_metadata(self):
        first = comparison_table_payload(has_more=True, next_offset=1)
        second = comparison_table_payload(offset=1)
        second["records"][0]["test_name"] = "1518B-2c-ip4base"
        fake = FakeMCPClient(payloads={"comparison_table": [first, second]})
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get(
                f"/api/comparison/export?view=table&format=csv&{QUERY}"
            )
        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 3)
        offsets = [
            arguments["offset"] for name, arguments in fake.calls
            if name == "comparison_table"
        ]
        self.assertEqual(offsets, [0, 1])

        malformed = comparison_table_payload(has_more=True, next_offset=None)
        fake = FakeMCPClient(payloads={"comparison_table": malformed})
        app = create_app(client_factory=FakeMCPContextFactory([fake]))
        with TestClient(app) as client:
            response = client.get(
                f"/api/comparison/export?view=table&format=csv&{QUERY}"
            )
        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
