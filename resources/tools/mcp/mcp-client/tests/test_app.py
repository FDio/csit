import csv
import io
import json
import unittest
import warnings
import zipfile
from types import SimpleNamespace

warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
)

from starlette.testclient import TestClient

from app import _canonical_failed_test_name, create_app


TOOL_NAMES = [
    "datasets",
    "columns",
    "values",
    "job_statistics",
    "trending_catalog",
    "trending_series",
    "trending",
    "iterative",
    "coverage",
]
DATASET_LABELS = {
    "statistics": "Statistics",
    "trending": "Trending",
    "iterative": "Iterative",
    "coverage": "Coverage",
}


def datasets_payload():
    return {
        "schema_version": 1,
        "data_status": "ready",
        "ready": True,
        "freshness": "2026-08-04T09:30:00+00:00",
        "datasets": [
            {"name": "statistics", "row_count": 2, "status": "loaded"},
            {"name": "trending", "row_count": 4, "status": "loaded"},
            {"name": "iterative", "row_count": 3, "status": "loaded"},
            {"name": "coverage", "row_count": 2, "status": "loaded"},
        ],
    }


def statistics_payload():
    return {
        "schema_version": 1,
        "dataset": "statistics",
        "total_row_count": 2,
        "row_count": 2,
        "returned_count": 2,
        "limit": 10000,
        "has_more": False,
        "next_offset": None,
        "freshness": "2026-08-04T09:30:00+00:00",
        "data_status": "ready",
        "filters": {
            "days": None,
            "job": None,
            "limit": 10000,
            "dut": "vpp",
            "test_type": "mrr",
            "cadence": "daily",
            "testbed": "2n-skx",
            "select_defaults": True,
        },
        "filter_options": {
            "dut": ["dpdk", "vpp"],
            "test_type": ["mrr", "ndrpdr"],
            "cadence": ["daily", "weekly"],
            "testbed": ["2n-skx", "3n-alt"],
        },
        "records": [
            {
                "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                "build": 201,
                "start_time": "2026-08-01T10:00:00+00:00",
                "duration": 123.4,
                "dut": "vpp",
                "dut_version": "24.10-release",
                "hosts": ["10.0.0.1", "10.0.0.2"],
                "test_type": "mrr",
                "cadence": "daily",
                "testbed": "2n-skx",
                "passed_count": 10,
                "failed_count": 2,
                "total_test_count": 12,
                "counts_available": True,
            },
            {
                "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                "build": 202,
                "start_time": "2026-08-03T10:00:00+00:00",
                "duration": 150.0,
                "dut": "vpp",
                "dut_version": "24.10-release",
                "hosts": ["10.0.0.1", "10.0.0.3"],
                "test_type": "mrr",
                "cadence": "daily",
                "testbed": "2n-skx",
                "passed_count": 11,
                "failed_count": 1,
                "total_test_count": 12,
                "counts_available": True,
            },
        ],
    }


def trending_payload(records, *, has_more=False, next_offset=None):
    return {
        "schema_version": 1,
        "dataset": "trending",
        "has_more": has_more,
        "next_offset": next_offset,
        "records": records,
    }


def trending_catalog_payload(records=None, *, has_more=False, next_offset=None):
    return {
        "schema_version": 1,
        "dataset": "trending_catalog",
        "row_count": len(records or []),
        "returned_count": len(records or []),
        "offset": 0,
        "limit": 500,
        "has_more": has_more,
        "next_offset": next_offset,
        "freshness": "2026-08-04T09:30:00+00:00",
        "data_status": "ready",
        "filters": {
            "dut": "vpp",
            "area": "ip4_tunnels",
            "test": "ethip4geneve",
            "infra": "2n-emr-100ge2p1e810cq-avf",
            "testbed": "all",
            "framesize": "all",
            "cores": "all",
            "test_type": "all",
            "select_defaults": True,
            "offset": 0,
            "limit": 500,
        },
        "filter_options": {
            "dut": ["vpp"],
            "area": ["ip4_tunnels"],
            "test": ["ethip4geneve"],
            "infra": ["2n-emr-100ge2p1e810cq-avf"],
            "testbed": ["2n-emr"],
            "framesize": ["64B"],
            "cores": ["1c"],
            "test_type": ["mrr"],
        },
        "option_labels": {"area": {"ip4_tunnels": "IPv4 Tunnels"}},
        "unclassified_row_count": 0,
        "records": records or [],
    }


def trending_series_payload():
    series = {
        "series_id": "series-mrr",
        "name": (
            "vpp-2n-emr-100ge2p1e810cq-avf-ip4_tunnels-64B-1c-"
            "ethip4geneve-mrr"
        ),
        "dut": "vpp",
        "area": "ip4_tunnels",
        "area_label": "IPv4 Tunnels",
        "test": "ethip4geneve",
        "infra": "2n-emr-100ge2p1e810cq-avf",
        "testbed": "2n-emr",
        "framesize": "64B",
        "cores": "1c",
        "test_type": "mrr",
    }
    return {
        "schema_version": 1,
        "dataset": "trending_series",
        "row_count": 1,
        "returned_count": 1,
        "offset": 0,
        "limit": 500,
        "has_more": False,
        "next_offset": None,
        "freshness": "2026-08-04T09:30:00+00:00",
        "data_status": "ready",
        "filters": {"series": ["series-mrr"], "offset": 0, "limit": 500},
        "series": [series],
        "unknown_series": [],
        "records": [{
            **series,
            "start_time": "2026-08-03T10:00:00+00:00",
            "job": "csit-vpp-perf-mrr-daily-master-2n-emr",
            "build": 201,
            "dut_version": "26.06-release",
            "dut_type": "vpp",
            "hosts": ["10.0.0.1", "10.0.0.2"],
            "tg_type": "trex",
            "test_id": "tests.vpp.perf.ip4_tunnels.example-mrr",
            "throughput_value": 10_000_000.0,
            "throughput_unit": "pps",
            "bandwidth_value": 25_000_000_000.0,
            "bandwidth_unit": "bps",
            "latency_value": None,
            "latency_unit": None,
        }],
    }


class FakeMCPContextFactory:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0
        self.contexts = []

    def __call__(self, url):
        self.calls += 1
        outcome = self.outcomes.pop(0) if self.outcomes else RuntimeError("no outcome")
        context = FakeMCPContext(outcome)
        self.contexts.append(context)
        return context


class FakeMCPContext:
    def __init__(self, outcome):
        self.outcome = outcome
        self.closed = False

    async def __aenter__(self):
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome

    async def __aexit__(self, exc_type, exc, tb):
        self.closed = True
        if not isinstance(self.outcome, Exception):
            self.outcome.connected = False


class FakeMCPClient:
    def __init__(self, *, payloads=None, tool_errors=None, raw_text=None):
        self.connected = True
        self.payloads = {
            "datasets": datasets_payload(),
            "job_statistics": statistics_payload(),
            "trending_catalog": trending_catalog_payload(),
        }
        if payloads:
            self.payloads.update(payloads)
        self.tool_errors = tool_errors or {}
        self.raw_text = raw_text or {}
        self.calls = []

    def is_connected(self):
        return self.connected

    async def initialize(self, timeout=None):
        return SimpleNamespace(
            serverInfo=SimpleNamespace(name="csit_mcp", version="1.0.0")
        )

    async def list_tools(self):
        return [SimpleNamespace(name=name) for name in TOOL_NAMES]

    async def list_resources(self):
        return [SimpleNamespace(name="server://info")]

    async def list_prompts(self):
        return []

    async def call_tool(self, name, arguments=None):
        self.calls.append((name, arguments or {}))
        if name in self.tool_errors:
            raise self.tool_errors[name]
        text = self.raw_text.get(name)
        if text is None:
            payload = self.payloads.get(name, {})
            if isinstance(payload, list):
                payload = payload.pop(0)
            text = json.dumps(payload)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)]
        )


class ClientAppTests(unittest.TestCase):
    def test_failed_test_name_uses_canonical_csit_component_order(self):
        raw_name = (
            "tests.vpp.perf.ip4_tunnels.100ge2p1e810cq-ethip4gtpuhw-"
            "ip4base-mrr.64b-1c-ethip4gtpuhw-ip4base-mrr"
        )

        self.assertEqual(
            _canonical_failed_test_name(raw_name),
            "100ge2p1e810cq-64b-1c-ethip4gtpuhw-ip4base-mrr",
        )

    def test_failed_test_name_preserves_canonical_and_unknown_values(self):
        canonical = (
            "100ge2p1e810cq-avf-1518b-1c-"
            "ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr"
        )

        self.assertEqual(_canonical_failed_test_name(canonical), canonical)
        self.assertEqual(
            _canonical_failed_test_name("legacy-failed-test"),
            "legacy-failed-test",
        )

    def test_failed_test_name_preserves_hyphenated_driver(self):
        raw_name = "3na-200ge2p1cx7veat-af-xdp-ip4base-2c-64b-mrr"

        self.assertEqual(
            _canonical_failed_test_name(raw_name),
            "200ge2p1cx7veat-af-xdp-64b-2c-ip4base-mrr",
        )

    def test_failed_hoststack_name_uses_suite_type_and_keeps_workload(self):
        raw_name = (
            "tests.vpp.perf.hoststack."
            "2n1l-25ge2p1e810xxv-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps."
            "2048b-1c-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps"
        )

        self.assertEqual(
            _canonical_failed_test_name(raw_name),
            "25ge2p1e810xxv-2048b-1c-"
            "eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps-hoststack",
        )

    def test_lifespan_survives_initial_connection_failure(self):
        factory = FakeMCPContextFactory(
            [RuntimeError("startup down"), RuntimeError("health down")]
        )
        app = create_app(client_factory=factory)

        with TestClient(app) as client:
            response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "healthy")
        self.assertEqual(payload["service"], "mcp-client")
        self.assertFalse(payload["mcp"]["connected"])
        self.assertIn("health down", payload["mcp"]["last_error"])

    def test_health_reports_connected_server_metadata(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/health")

        payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["mcp"]["connected"])
        self.assertEqual(payload["mcp"]["url"], "http://mcp-server:8000/mcp")
        self.assertEqual(payload["mcp"]["server"]["name"], "csit_mcp")
        self.assertEqual(payload["mcp"]["tools"], TOOL_NAMES)
        self.assertEqual(payload["mcp"]["resources"], ["server://info"])
        self.assertEqual(payload["mcp"]["reconnect_attempts"], 1)

    def test_default_statistics_page_renders_filters_and_charts(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>CSIT Dashboard</title>", response.text)
        self.assertIn("<h1>CSIT Dashboard</h1>", response.text)
        self.assertNotIn("<h2>Statistics</h2>", response.text)
        self.assertIn('name="dut"', response.text)
        self.assertIn('name="test_type"', response.text)
        self.assertIn('name="cadence"', response.text)
        self.assertIn('name="testbed"', response.text)
        self.assertIn("Passed / Failed Tests", response.text)
        self.assertIn("Duration", response.text)
        self.assertIn('<svg class="bar-chart"', response.text)
        self.assertEqual(
            fake_client.calls,
            [
                ("datasets", {}),
                (
                    "job_statistics",
                    {"limit": 10000, "select_defaults": True},
                ),
            ],
        )

    def test_non_statistics_tabs_keep_phase_one_placeholder(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            for dataset in ("iterative", "coverage"):
                with self.subTest(dataset=dataset):
                    label = DATASET_LABELS[dataset]
                    response = client.get(f"/?dataset={dataset}")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(
                        f'href="/?dataset={dataset}" aria-current="page">{label}</a>',
                        response.text,
                    )
                    self.assertIn(f"<h2>{label}</h2>", response.text)
                    self.assertNotIn("statistics-filters", response.text)

        self.assertEqual(fake_client.calls, [("datasets", {})] * 2)

    def test_trending_tab_renders_filters_and_only_loads_catalog_initially(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending")

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="trending-filters"', response.text)
        self.assertIn('name="area"', response.text)
        self.assertIn('name="framesize"', response.text)
        self.assertIn("Add Selected", response.text)
        self.assertIn("Selected tests", response.text)
        self.assertNotIn("<h2>Trending</h2>", response.text)
        self.assertEqual(
            fake_client.calls,
            [
                ("datasets", {}),
                (
                    "trending_catalog",
                    {"select_defaults": True, "offset": 0, "limit": 500},
                ),
            ],
        )

    def test_trending_selected_series_loads_semantic_points(self):
        fake_client = FakeMCPClient(
            payloads={"trending_series": trending_series_payload()}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending&series=series-mrr")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Throughput", response.text)
        self.assertIn("Bandwidth", response.text)
        self.assertNotIn("Average Latency at 50% PDR", response.text)
        self.assertIn('r="2.5"', response.text)
        self.assertEqual(
            fake_client.calls[-1],
            (
                "trending_series",
                {"series": ["series-mrr"], "offset": 0, "limit": 500},
            ),
        )

    def test_trending_add_redirects_to_canonical_series_url(self):
        catalog_record = trending_series_payload()["series"][0]
        fake_client = FakeMCPClient(
            payloads={"trending_catalog": trending_catalog_payload([catalog_record])}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app, follow_redirects=False) as client:
            response = client.get(
                "/?dataset=trending&trending_action=add&dut=vpp&"
                "area=ip4_tunnels"
            )

        self.assertEqual(response.status_code, 303)
        self.assertIn("dataset=trending", response.headers["location"])
        self.assertIn("series=series-mrr", response.headers["location"])
        self.assertNotIn("trending_action", response.headers["location"])

    def test_trending_add_follows_catalog_pagination(self):
        first_record = {**trending_series_payload()["series"][0]}
        second_record = {
            **first_record,
            "series_id": "series-pdr",
            "name": first_record["name"].replace("-mrr", "-pdr"),
            "test_type": "pdr",
        }
        first = trending_catalog_payload(
            [first_record],
            has_more=True,
            next_offset=500,
        )
        second = trending_catalog_payload([second_record])
        second["offset"] = 500
        second["filters"]["offset"] = 500
        fake_client = FakeMCPClient(
            payloads={"trending_catalog": [first, second]}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app, follow_redirects=False) as client:
            response = client.get(
                "/?dataset=trending&trending_action=add&dut=vpp"
            )

        self.assertEqual(response.status_code, 303)
        self.assertIn("series=series-mrr", response.headers["location"])
        self.assertIn("series=series-pdr", response.headers["location"])
        self.assertEqual(fake_client.calls[-1][0], "trending_catalog")
        self.assertEqual(fake_client.calls[-1][1]["offset"], 500)

    def test_trending_catalog_json_error_renders_inline(self):
        fake_client = FakeMCPClient(payloads={
            "trending_catalog": {
                "error": "data_unavailable",
                "message": "Trending cache is loading.",
            },
        })
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Trending catalog unavailable", response.text)
        self.assertIn("Trending cache is loading.", response.text)

    def test_trending_catalog_failure_returns_status_page(self):
        fake_client = FakeMCPClient(
            tool_errors={"trending_catalog": RuntimeError("catalog failed")}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending")

        self.assertEqual(response.status_code, 503)
        self.assertIn("catalog failed", response.text)

    def test_malformed_trending_pagination_returns_status_page(self):
        payload = trending_series_payload()
        payload["has_more"] = True
        payload["next_offset"] = 0
        fake_client = FakeMCPClient(payloads={"trending_series": payload})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending&series=series-mrr")

        self.assertEqual(response.status_code, 503)
        self.assertIn("invalid next_offset", response.text)

    def test_trending_remove_actions_update_url_selection(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app, follow_redirects=False) as client:
            selected = client.get(
                "/?dataset=trending&series=series-a&series=series-b&"
                "remove=series-a&trending_action=remove_selected"
            )
            removed_all = client.get(
                "/?dataset=trending&series=series-b&trending_action=remove_all"
            )

        self.assertIn("series=series-b", selected.headers["location"])
        self.assertNotIn("series=series-a", selected.headers["location"])
        self.assertNotIn("series=", removed_all.headers["location"])

    def test_invalid_dataset_falls_back_to_statistics(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=not-a-dataset")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'href="/?dataset=statistics" aria-current="page">Statistics</a>',
            response.text,
        )
        self.assertIn("statistics-filters", response.text)

    def test_statistics_query_parameters_are_passed_to_mcp(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/?dataset=statistics&dut=vpp&test_type=mrr&cadence=daily&"
                "testbed=2n-skx&ignored=value"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            fake_client.calls[-1],
            (
                "job_statistics",
                {
                    "limit": 10000,
                    "select_defaults": True,
                    "dut": "vpp",
                    "test_type": "mrr",
                    "cadence": "daily",
                    "testbed": "2n-skx",
                },
            ),
        )

    def test_status_panel_shows_connection_data_freshness_and_url(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending")

        self.assertIn("<strong>MCP:</strong> connected", response.text)
        self.assertIn("<strong>Data status:</strong> ready", response.text)
        self.assertIn("<strong>Freshness:</strong> 2026-08-04 09:30 UTC", response.text)
        self.assertIn("<code>http://mcp-server:8000/mcp</code>", response.text)
        self.assertIn("status-ready", response.text)

    def test_statistics_json_error_renders_inline(self):
        fake_client = FakeMCPClient(
            payloads={
                "job_statistics": {
                    "error": "data_unavailable",
                    "message": "Statistics are loading.",
                }
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Statistics unavailable", response.text)
        self.assertIn("Statistics are loading.", response.text)
        self.assertNotIn('<svg class="bar-chart"', response.text)

    def test_invalid_datasets_json_renders_warning_without_crashing(self):
        fake_client = FakeMCPClient(raw_text={"datasets": "not-json"})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/?dataset=trending")

        self.assertEqual(response.status_code, 200)
        self.assertIn("<strong>Data status:</strong> warning", response.text)

    def test_static_assets_are_served_separately(self):
        app = create_app(client_factory=FakeMCPContextFactory([FakeMCPClient()]))

        with TestClient(app) as client:
            page = client.get("/")
            css = client.get("/static/dashboard.css")
            javascript = client.get("/static/dashboard.js")

        self.assertIn('href="/static/dashboard.css?v=10"', page.text)
        self.assertIn('src="/static/dashboard.js?v=10"', page.text)
        self.assertEqual(css.status_code, 200)
        self.assertIn(".statistics-filters", css.text)
        self.assertIn("font-size: 10px", css.text)
        self.assertIn(".chart-tooltip", css.text)
        self.assertIn(".details-dialog", css.text)
        self.assertIn(".copy-icon", css.text)
        self.assertIn(".statistics-actions", css.text)
        self.assertIn(".action-dialog", css.text)
        self.assertIn(".trending-layout", css.text)
        self.assertIn(".scatter-chart", css.text)
        self.assertIn(".trending-trend-hit-target", css.text)
        self.assertIn(".details-dialog-actions", css.text)
        self.assertIn("repeat(5, minmax(0, 1fr))", css.text)
        self.assertIn("font-size: 14px", css.text)
        self.assertEqual(javascript.status_code, 200)
        self.assertIn("requestSubmit", javascript.text)
        self.assertIn("data-tooltip", javascript.text)
        self.assertIn("showModal", javascript.text)
        self.assertIn("/api/statistics/run-details", javascript.text)
        self.assertIn("navigator.clipboard.writeText", javascript.text)
        self.assertIn("detailsController.abort", javascript.text)
        self.assertIn('addEventListener("cancel"', javascript.text)
        self.assertGreaterEqual(javascript.text.count('event.key === "Escape"'), 3)
        self.assertIn("showSaveFilePicker", javascript.text)
        self.assertIn("/api/statistics/export", javascript.text)
        self.assertIn("downloadButton.dataset.exportEndpoint", javascript.text)
        self.assertIn("URL.createObjectURL", javascript.text)
        self.assertIn("window.location.href", javascript.text)
        self.assertIn('searchParams.set("dataset", "statistics")', javascript.text)
        self.assertIn("data-trending-filter", javascript.text)
        self.assertIn(".chart-tooltip-target", javascript.text)
        self.assertIn("#trending-details-dialog", javascript.text)
        self.assertIn(".trending-details-target[data-tooltip]", javascript.text)
        self.assertIn("data-trending-details-content", javascript.text)
        self.assertIn("data-copy-trending-details", javascript.text)
        self.assertIn("openTrendingDetails", javascript.text)
        self.assertIn("closeTrendingDetails", javascript.text)
        self.assertIn("originatingTarget", javascript.text)
        self.assertIn("Copied detailed information.", javascript.text)
        self.assertIn("chart.scrollWidth - chart.clientWidth", javascript.text)
        self.assertIn("data-copy-url", javascript.text)

    def test_trending_csv_export_uses_selected_series_and_exact_columns(self):
        fake_client = FakeMCPClient(
            payloads={"trending_series": trending_series_payload()}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/trending/export",
                params=[
                    ("format", "csv"),
                    ("filename", "../../My Trending.xlsx"),
                    ("series", "series-mrr"),
                ],
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/csv"))
        self.assertEqual(
            response.headers["content-disposition"],
            'attachment; filename="My Trending.csv"',
        )
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(rows[0], [
            "date", "job", "build", "dut type", "dut version", "hosts",
            "tg_type", "test_id", "throughput", "throughput unit",
            "bandwidth", "bandwidth unit", "latency", "latency unit",
        ])
        self.assertEqual(rows[1][0:8], [
            "2026-08-03 10:00",
            "csit-vpp-perf-mrr-daily-master-2n-emr",
            "201",
            "vpp",
            "26.06-release",
            "10.0.0.1, 10.0.0.2",
            "trex",
            "tests.vpp.perf.ip4_tunnels.example-mrr",
        ])
        self.assertEqual(rows[1][8:12], [
            "10000000", "pps", "25000000000", "bps",
        ])
        self.assertEqual(
            fake_client.calls,
            [(
                "trending_series",
                {"series": ["series-mrr"], "offset": 0, "limit": 500},
            )],
        )

    def test_trending_export_follows_all_series_pages(self):
        first = trending_series_payload()
        first["has_more"] = True
        first["next_offset"] = 500
        second = trending_series_payload()
        second["offset"] = 500
        second["records"][0]["build"] = 202
        fake_client = FakeMCPClient(
            payloads={"trending_series": [first, second]}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/trending/export?format=csv&series=series-mrr"
            )

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(fake_client.calls[1], (
            "trending_series",
            {"series": ["series-mrr"], "offset": 500, "limit": 500},
        ))

    def test_trending_xlsx_export_uses_timestamped_default_and_excel_table(self):
        fake_client = FakeMCPClient(
            payloads={"trending_series": trending_series_payload()}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/trending/export?series=series-mrr")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertRegex(
            response.headers["content-disposition"],
            r'^attachment; filename="trending-\d{4}-\d{2}-\d{2} '
            r'\d{2}:\d{2}:\d{2}\.xlsx"$',
        )
        with zipfile.ZipFile(io.BytesIO(response.content)) as workbook:
            table = workbook.read("xl/tables/table1.xml").decode("utf-8")
        self.assertIn('name="TrendingTable"', table)
        self.assertIn("<autoFilter", table)

    def test_trending_export_accepts_valid_stale_series_as_empty_table(self):
        payload = trending_series_payload()
        payload["records"] = []
        payload["series"] = []
        payload["unknown_series"] = ["stale-id"]
        fake_client = FakeMCPClient(payloads={"trending_series": payload})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/trending/export?format=csv&series=stale-id"
            )

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 1)

    def test_trending_export_validates_format_and_selected_series(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            invalid_format = client.get(
                "/api/trending/export?format=pdf&series=series-mrr"
            )
            missing_series = client.get("/api/trending/export?format=csv")

        self.assertEqual(invalid_format.status_code, 400)
        self.assertEqual(missing_series.status_code, 400)
        self.assertEqual(fake_client.calls, [])

    def test_trending_export_maps_malformed_and_unavailable_payloads(self):
        malformed = trending_series_payload()
        malformed["has_more"] = "yes"
        cases = [
            (FakeMCPClient(payloads={"trending_series": malformed}), 502),
            (FakeMCPClient(raw_text={"trending_series": "not-json"}), 502),
            (FakeMCPClient(payloads={"trending_series": {
                "error": "validation_error", "message": "Bad series.",
            }}), 400),
            (FakeMCPClient(payloads={"trending_series": {
                "error": "data_unavailable", "message": "Loading.",
            }}), 503),
            (FakeMCPClient(
                tool_errors={"trending_series": RuntimeError("tool failed")}
            ), 503),
        ]

        for fake_client, expected_status in cases:
            with self.subTest(expected_status=expected_status):
                app = create_app(
                    client_factory=FakeMCPContextFactory([fake_client])
                )
                with TestClient(app) as client:
                    response = client.get(
                        "/api/trending/export?series=series-mrr"
                    )
                self.assertEqual(response.status_code, expected_status)
                self.assertIn("error", response.json())

    def test_run_details_returns_failed_tests_without_eager_trending_call(self):
        raw_test_id = (
            "tests.vpp.perf.ip4_tunnels.100ge2p1e810cq-ethip4gtpuhw-"
            "ip4base-mrr.64b-1c-ethip4gtpuhw-ip4base-mrr"
        )
        canonical_test_id = (
            "100ge2p1e810cq-64b-1c-ethip4gtpuhw-ip4base-mrr"
        )
        fake_client = FakeMCPClient(
            payloads={
                "trending": trending_payload(
                    [{"test_id": raw_test_id}, {"test_id": canonical_test_id}]
                )
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            page = client.get("/")
            calls_after_page = list(fake_client.calls)
            response = client.get(
                "/api/statistics/run-details",
                params={
                    "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "build": "201",
                },
            )

        self.assertEqual(page.status_code, 200)
        self.assertEqual(
            calls_after_page,
            [
                ("datasets", {}),
                ("job_statistics", {"limit": 10000, "select_defaults": True}),
            ],
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                "build": 201,
                "failed_count": 2,
                "failed_tests": [canonical_test_id, canonical_test_id],
            },
        )
        self.assertEqual(
            fake_client.calls[-1],
            (
                "trending",
                {
                    "job": "csit-vpp-perf-mrr-daily-master-2n-skx",
                    "build": 201,
                    "passed": False,
                    "offset": 0,
                    "aggregation": "none",
                    "columns": ["test_id"],
                    "limit": 1000,
                },
            ),
        )

    def test_run_details_follows_pagination_and_preserves_source_rows(self):
        fake_client = FakeMCPClient(
            payloads={
                "trending": [
                    trending_payload(
                        [
                            {"test_id": "duplicate-test"},
                            {},
                            {"test_id": "duplicate-test"},
                        ],
                        has_more=True,
                        next_offset=3,
                    ),
                    trending_payload(
                        [{"test_id": None}, {"test_id": "last-test"}]
                    ),
                ]
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/statistics/run-details?job=fixture-job&build=9"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["failed_tests"],
            [
                "duplicate-test",
                "[test_id unavailable]",
                "duplicate-test",
                "[test_id unavailable]",
                "last-test",
            ],
        )
        self.assertEqual(response.json()["failed_count"], 5)
        self.assertEqual(fake_client.calls[0][1]["offset"], 0)
        self.assertEqual(fake_client.calls[1][1]["offset"], 3)

    def test_run_details_rejects_invalid_arguments_without_calling_tool(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            responses = [
                client.get("/api/statistics/run-details?build=1"),
                client.get("/api/statistics/run-details?job=fixture-job"),
                client.get("/api/statistics/run-details?job=fixture-job&build=-1"),
                client.get("/api/statistics/run-details?job=fixture-job&build=1.5"),
            ]

        self.assertTrue(all(response.status_code == 400 for response in responses))
        self.assertTrue(all(response.json()["error"] == "validation_error" for response in responses))
        self.assertEqual(fake_client.calls, [])

    def test_run_details_returns_502_for_malformed_upstream_pagination(self):
        cases = [
            {"records": {}, "has_more": False, "next_offset": None},
            trending_payload([], has_more=True, next_offset=0),
            {"records": [], "has_more": "yes", "next_offset": None},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                fake_client = FakeMCPClient(payloads={"trending": payload})
                app = create_app(
                    client_factory=FakeMCPContextFactory([fake_client])
                )
                with TestClient(app) as client:
                    response = client.get(
                        "/api/statistics/run-details?job=fixture-job&build=1"
                    )
                self.assertEqual(response.status_code, 502)
                self.assertEqual(
                    response.json()["error"],
                    "invalid_upstream_response",
                )

    def test_run_details_maps_mcp_payload_and_call_failures_to_503(self):
        payload_client = FakeMCPClient(
            payloads={
                "trending": {
                    "error": "data_unavailable",
                    "message": "Trending is loading.",
                }
            }
        )
        call_client = FakeMCPClient(
            tool_errors={"trending": RuntimeError("trending failed")}
        )

        for fake_client in (payload_client, call_client):
            with self.subTest(fake_client=fake_client):
                app = create_app(
                    client_factory=FakeMCPContextFactory([fake_client])
                )
                with TestClient(app) as client:
                    response = client.get(
                        "/api/statistics/run-details?job=fixture-job&build=1"
                    )
                self.assertEqual(response.status_code, 503)
                self.assertIn("error", response.json())

    def test_run_details_returns_502_for_invalid_tool_json(self):
        fake_client = FakeMCPClient(raw_text={"trending": "not-json"})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/statistics/run-details?job=fixture-job&build=1"
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["error"], "invalid_upstream_response")

    def test_statistics_csv_export_uses_fresh_filters_and_failed_tests(self):
        payload = statistics_payload()
        payload["records"] = [payload["records"][0]]
        raw_test_id = (
            "tests.vpp.perf.ip4_tunnels.100ge2p1e810cq-ethip4gtpuhw-"
            "ip4base-mrr.64b-1c-ethip4gtpuhw-ip4base-mrr"
        )
        fake_client = FakeMCPClient(
            payloads={
                "job_statistics": payload,
                "trending": trending_payload(
                    [{"test_id": raw_test_id}, {"test_id": "duplicate-test"}]
                ),
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get(
                "/api/statistics/export",
                params={
                    "format": "csv",
                    "filename": "../../My statistics.xlsx",
                    "dut": "vpp",
                    "test_type": "mrr",
                    "cadence": "daily",
                    "testbed": "2n-skx",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/csv"))
        self.assertEqual(
            response.headers["content-disposition"],
            'attachment; filename="My-statistics.csv"',
        )
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(
            rows[0],
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
        self.assertEqual(rows[1][0:5], ["201", "2026-08-01 10:00", "00:02", "10", "2"])
        self.assertEqual(
            rows[1][8],
            "100ge2p1e810cq-64b-1c-ethip4gtpuhw-ip4base-mrr, duplicate-test",
        )
        self.assertEqual(
            fake_client.calls[0],
            (
                "job_statistics",
                {
                    "limit": 10000,
                    "select_defaults": True,
                    "dut": "vpp",
                    "test_type": "mrr",
                    "cadence": "daily",
                    "testbed": "2n-skx",
                },
            ),
        )
        self.assertEqual(fake_client.calls[1][0], "trending")

    def test_statistics_export_pages_failed_tests_once_per_unique_run(self):
        payload = statistics_payload()
        record = payload["records"][0]
        record["failed_count"] = 3
        payload["records"] = [record, dict(record)]
        fake_client = FakeMCPClient(
            payloads={
                "job_statistics": payload,
                "trending": [
                    trending_payload(
                        [{"test_id": "duplicate-test"}, {"test_id": None}],
                        has_more=True,
                        next_offset=2,
                    ),
                    trending_payload([{"test_id": "duplicate-test"}]),
                ],
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/statistics/export?format=csv")

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            rows[1][8],
            "duplicate-test, [test_id unavailable], duplicate-test",
        )
        trending_calls = [call for call in fake_client.calls if call[0] == "trending"]
        self.assertEqual(len(trending_calls), 2)
        self.assertEqual(trending_calls[0][1]["offset"], 0)
        self.assertEqual(trending_calls[1][1]["offset"], 2)

    def test_statistics_xlsx_export_uses_default_filename_and_excel_table(self):
        payload = statistics_payload()
        payload["records"] = [payload["records"][1]]
        payload["records"][0]["failed_count"] = 0
        fake_client = FakeMCPClient(payloads={"job_statistics": payload})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/statistics/export")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response.headers["content-disposition"],
            'attachment; filename="stats-vpp-mrr-daily-2n-skx.xlsx"',
        )
        with zipfile.ZipFile(io.BytesIO(response.content)) as workbook:
            self.assertIn("xl/tables/table1.xml", workbook.namelist())
        self.assertEqual(
            [call for call in fake_client.calls if call[0] == "trending"],
            [],
        )

    def test_statistics_export_accepts_empty_complete_dataset(self):
        payload = statistics_payload()
        payload["records"] = []
        payload["returned_count"] = 0
        fake_client = FakeMCPClient(payloads={"job_statistics": payload})
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/statistics/export?format=csv")

        self.assertEqual(response.status_code, 200)
        rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "build")

    def test_statistics_export_rejects_invalid_format_without_tool_call(self):
        fake_client = FakeMCPClient()
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/statistics/export?format=pdf")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")
        self.assertEqual(fake_client.calls, [])

    def test_statistics_export_rejects_truncated_or_malformed_results(self):
        cases = [
            {**statistics_payload(), "has_more": True},
            {**statistics_payload(), "has_more": "yes"},
            {**statistics_payload(), "records": {}},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                fake_client = FakeMCPClient(payloads={"job_statistics": payload})
                app = create_app(
                    client_factory=FakeMCPContextFactory([fake_client])
                )
                with TestClient(app) as client:
                    response = client.get("/api/statistics/export")
                self.assertEqual(response.status_code, 502)
                self.assertEqual(
                    response.json()["error"],
                    "invalid_upstream_response",
                )

    def test_statistics_export_maps_upstream_errors(self):
        cases = [
            (
                FakeMCPClient(
                    payloads={
                        "job_statistics": {
                            "error": "validation_error",
                            "message": "Bad filters.",
                        }
                    }
                ),
                400,
            ),
            (
                FakeMCPClient(
                    payloads={
                        "job_statistics": {
                            "error": "data_unavailable",
                            "message": "Statistics are loading.",
                        }
                    }
                ),
                503,
            ),
            (
                FakeMCPClient(
                    tool_errors={"job_statistics": RuntimeError("tool failed")}
                ),
                503,
            ),
        ]
        for fake_client, status in cases:
            with self.subTest(status=status, fake_client=fake_client):
                app = create_app(
                    client_factory=FakeMCPContextFactory([fake_client])
                )
                with TestClient(app) as client:
                    response = client.get("/api/statistics/export")
                self.assertEqual(response.status_code, status)
                self.assertIn("error", response.json())

    def test_statistics_export_fails_when_failed_test_rows_are_incomplete(self):
        payload = statistics_payload()
        payload["records"] = [payload["records"][0]]
        fake_client = FakeMCPClient(
            payloads={
                "job_statistics": payload,
                "trending": trending_payload([{"test_id": "only-one"}]),
            }
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/api/statistics/export")

        self.assertEqual(response.status_code, 502)
        self.assertIn("incomplete", response.json()["message"])

    def test_dashboard_returns_status_page_when_connection_fails(self):
        factory = FakeMCPContextFactory(
            [RuntimeError("startup down"), RuntimeError("still down")]
        )
        app = create_app(client_factory=factory)

        with TestClient(app) as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertIn("CSIT MCP dashboard is unavailable", response.text)
        self.assertIn("RuntimeError: still down", response.text)

    def test_dashboard_returns_status_page_when_required_tool_raises(self):
        fake_client = FakeMCPClient(
            tool_errors={"job_statistics": RuntimeError("statistics failed")}
        )
        app = create_app(client_factory=FakeMCPContextFactory([fake_client]))

        with TestClient(app) as client:
            response = client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertIn("CSIT MCP dashboard is unavailable", response.text)
        self.assertIn("RuntimeError: statistics failed", response.text)

    def test_lazy_reconnect_updates_attempts_and_status(self):
        fake_client = FakeMCPClient()
        factory = FakeMCPContextFactory(
            [RuntimeError("startup down"), fake_client]
        )
        app = create_app(client_factory=factory)

        with TestClient(app) as client:
            response = client.get("/")
            health = client.get("/health").json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(factory.calls, 2)
        self.assertEqual(health["mcp"]["reconnect_attempts"], 2)
        self.assertTrue(health["mcp"]["connected"])
        self.assertIsNone(health["mcp"]["last_error"])

    def test_shutdown_closes_active_mcp_client(self):
        fake_client = FakeMCPClient()
        factory = FakeMCPContextFactory([fake_client])
        app = create_app(client_factory=factory)

        with TestClient(app) as client:
            self.assertTrue(client.get("/health").json()["mcp"]["connected"])

        self.assertFalse(fake_client.connected)
        self.assertTrue(factory.contexts[0].closed)


if __name__ == "__main__":
    unittest.main()
