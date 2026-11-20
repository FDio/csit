import gzip
import math
import tempfile
import unittest
from pathlib import Path

import openpyxl

import compare_releases as cr


def robot_report(test_name, tags, status, message):
    strings = ["*Root", f"*{test_name}"]
    tag_indexes = []
    for tag in tags:
        tag_indexes.append(len(strings))
        strings.append(f"*{tag}")
    message_index = len(strings)
    strings.append(f"*{message}")
    status_index = {"Fail": 0, "Pass": 1, "Skip": 2, "Not Run": 3}[status]
    test = [1, 0, 0, tag_indexes, [status_index, 0, 1, message_index], []]
    suite = [0, 0, 0, 0, [], [1, 0, 1], [], [test], [], [1, 1 if status == "Pass" else 0, 1 if status == "Fail" else 0, 0]]
    return (
        '<script type="text/javascript">\n'
        f'window.output["suite"] = {suite!r};\n'
        "</script>\n"
        '<script type="text/javascript">\n'
        'window.output["strings"] = [];\n'
        f'window.output["strings"] = window.output["strings"].concat({strings!r});\n'
        "</script>\n"
    ).replace("'", '"')


def gzipped_report(test_name, tags, status, message):
    return gzip.compress(robot_report(test_name, tags, status, message).encode("utf-8"))


def make_workbook(path, rows, headers=None):
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.append(headers or ["DUT", "Node", "Job type", "Test type", "Testbed", "Log"])
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


class ReleaseAndWorkbookTests(unittest.TestCase):
    def test_release_filename_and_order(self):
        previous, current = cr.determine_releases([Path("2606.xlsx"), Path("2602.xlsx")])
        self.assertEqual(previous.label, "2602")
        self.assertEqual(current.label, "2606")
        with self.assertRaises(cr.InputError):
            cr.parse_release_path(Path("release-2606.xlsx"))
        with self.assertRaises(cr.InputError):
            cr.parse_release_path(Path("2699.xlsx"))

    def test_duplicate_log_headers_and_missing_testbed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2601.xlsx"
            make_workbook(
                path,
                [["vpp", "2n", "iterative", "mrr", "", "http://example/log"]],
                headers=["DUT", "Node", "Job type", "Test type", "Log", "Log"],
            )
            rows = cr.read_workbook_rows(path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].log_url, "http://example/log")
        self.assertEqual(rows[0].testbed, "")


class RobotAndMetricTests(unittest.TestCase):
    def test_robot_report_decoding_and_tag_extraction(self):
        html = robot_report(
            "64B-1c-ethip4-ip4base-mrr",
            ["NIC_Intel-E810CQ", "DRV_VFIO_PCI", "64B", "1C", "ethip4-ip4base", "MRR"],
            "Pass",
            "Maximum Receive Rate trial results in packets per second: [10, 10, 10]",
        )
        tests = cr.collect_robot_tests(html)
        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0].status, "Pass")
        fields = cr.extract_tag_fields(tests[0].name, tests[0].tags, "mrr")
        self.assertEqual(fields.nic, "Intel-E810CQ")
        self.assertEqual(fields.driver, "VFIO_PCI")
        self.assertEqual(fields.framesize, "64B")
        self.assertEqual(fields.cores, "1c")
        self.assertEqual(fields.test_area, "ethip4-ip4base")

    def test_robot_payload_accepts_javascript_array_literals(self):
        parsed = cr.parse_js_array_literal("[1, undefined, null, true, false, 'text']", "fixture")
        self.assertEqual(parsed, [1, None, None, True, False, "text"])

    def test_robot_payload_accepts_split_suite_parts(self):
        strings = [
            "*Root",
            "*64B-1c-ethip4-ip4base-mrr",
            "*NIC_Intel",
            "*64B",
            "*Maximum Receive Rate trial results in packets per second: [1, 1]",
        ]
        test = [1, 0, 0, [2, 3], [1, 0, 1, 4], []]
        suite = "[0,0,0,0,[],[1,0,1],[],window.sPart0,[],[1,1,0,0]]"
        html = (
            '<script type="text/javascript">\n'
            f"window.sPart0 = {[test]!r};\n"
            f'window.output["suite"] = {suite};\n'
            "</script>\n"
            '<script type="text/javascript">\n'
            'window.output["strings"] = [];\n'
            f'window.output["strings"] = window.output["strings"].concat({strings!r});\n'
            "</script>\n"
        ).replace("'", '"')

        tests = cr.collect_robot_tests(html)

        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0].name, "64B-1c-ethip4-ip4base-mrr")
        self.assertEqual(tests[0].status, "Pass")

    def test_metric_parsers(self):
        mrr = cr.parse_test_result("mrr", "Maximum Receive Rate trial results in packets per second: [10, 10, 10, 100]")
        self.assertEqual(mrr.standard, 10)
        gso = cr.parse_test_result("gso", "iPerf3 trial results in Gbits per second: ['20.0', '22.0']")
        self.assertEqual(gso.standard, 21)
        ndrpdr = cr.parse_test_result("ndrpdr", "NDR: 100 pps, 1 Gbps\nPDR: 200 pps, 2 Gbps")
        self.assertEqual(ndrpdr.ndr, 100)
        self.assertEqual(ndrpdr.pdr, 200)
        hoststack = cr.parse_test_result("hoststack", "Transfer Rate: 45463.2 [Kbytes/sec]\nLatency: 1 ms")
        self.assertEqual(hoststack.standard, 45463.2)
        soak = cr.parse_test_result("soak", "PLRsearch lower bound: 7732719.4 pps, 7 Gbps")
        self.assertEqual(soak.standard, 7732719.4)
        soak_cps = cr.parse_test_result(
            "soak",
            "PLRsearch lower bound: 689714.5607157522 CPS\n"
            "PLRsearch upper bound: 691830.9170358563 CPS",
        )
        self.assertEqual(soak_cps.standard, 689714.5607157522)

    def test_outlier_population_stdev_and_single_value(self):
        self.assertEqual(cr.exclude_outliers([10, 10, 10, 100]), [10.0, 10.0, 10.0])
        summary = cr.summarize([1, 2, 3])
        self.assertEqual(summary.mean, 2)
        self.assertAlmostEqual(summary.stdev, math.sqrt(2 / 3))
        single = cr.summarize([42])
        self.assertEqual(single.mean, 42)
        self.assertIsNone(single.stdev)


class AggregationAndOutputTests(unittest.TestCase):
    def test_output_diff_and_ndrpdr_split(self):
        identity = cr.TestIdentity("vpp", "2n", "iterative", "mrr", "Intel", "VFIO", "64B", "1c", "ip4base")
        row = cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://current", 2)
        current = cr.TestAggregate(identity, "tb")
        current.add(row, "Pass", cr.MetricValues(standard=120))
        current.add(row, "Pass", cr.MetricValues(standard=100))
        previous = cr.TestAggregate(identity, "tb")
        previous.add(cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://previous", 2), "Pass", cr.MetricValues(standard=100))

        ndr_identity = cr.TestIdentity("vpp", "2n", "coverage", "ndrpdr", "Intel", "VFIO", "64B", "1c", "ip4base")
        current_ndr = cr.TestAggregate(ndr_identity, "tb")
        current_ndr.add(cr.WorkbookRow("vpp", "2n", "coverage", "ndrpdr", "tb", "http://current-ndr", 3), "Pass", cr.MetricValues(ndr=200, pdr=300))
        previous_ndr = cr.TestAggregate(ndr_identity, "tb")
        previous_ndr.add(cr.WorkbookRow("vpp", "2n", "coverage", "ndrpdr", "tb", "http://previous-ndr", 3), "Pass", cr.MetricValues(ndr=100, pdr=150))

        rows = cr.output_rows({identity: current, ndr_identity: current_ndr}, {identity: previous, ndr_identity: previous_ndr})
        mrr_row = next(row for row in rows if row["Test type"] == "mrr")
        self.assertEqual(mrr_row["Mean current"], 110)
        self.assertEqual(mrr_row["Diff"], 10)
        self.assertAlmostEqual(mrr_row["Rel Diff"], 10 / 110)
        ndr_row = next(row for row in rows if row["Test type"] == "ndrpdr")
        self.assertEqual(ndr_row["Mean NDR current"], 200)
        self.assertEqual(ndr_row["Diff NDR"], 100)
        self.assertEqual(ndr_row["Diff PDR"], 150)

    def test_diff_uses_numeric_values_even_when_status_is_fail(self):
        identity = cr.TestIdentity("vpp", "2n", "iterative", "mrr", "Intel", "VFIO", "64B", "1c", "ip4base")
        current = cr.TestAggregate(identity, "tb")
        current.add(cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://current-pass", 2), "Pass", cr.MetricValues(standard=10))
        current.add(cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://current-fail", 3), "Fail", cr.MetricValues())
        previous = cr.TestAggregate(identity, "tb")
        previous.add(cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://previous", 2), "Pass", cr.MetricValues(standard=5))

        row = cr.output_rows({identity: current}, {identity: previous})[0]

        self.assertEqual(row["Status"], "Fail")
        self.assertEqual(row["Mean current"], 10)
        self.assertEqual(row["Diff"], 5)
        self.assertEqual(row["Rel Diff"], 0.5)

        ndr_identity = cr.TestIdentity("vpp", "2n", "coverage", "ndrpdr", "Intel", "VFIO", "64B", "1c", "ip4base")
        current_ndr = cr.TestAggregate(ndr_identity, "tb")
        current_ndr.add(cr.WorkbookRow("vpp", "2n", "coverage", "ndrpdr", "tb", "http://current-ndr", 4), "Pass", cr.MetricValues(ndr=20, pdr=30))
        current_ndr.add(cr.WorkbookRow("vpp", "2n", "coverage", "ndrpdr", "tb", "http://current-ndr-fail", 5), "Fail", cr.MetricValues())
        previous_ndr = cr.TestAggregate(ndr_identity, "tb")
        previous_ndr.add(cr.WorkbookRow("vpp", "2n", "coverage", "ndrpdr", "tb", "http://previous-ndr", 4), "Pass", cr.MetricValues(ndr=10, pdr=15))

        ndr_row = cr.output_rows({ndr_identity: current_ndr}, {ndr_identity: previous_ndr})[0]

        self.assertEqual(ndr_row["Status"], "Fail")
        self.assertEqual(ndr_row["Diff NDR"], 10)
        self.assertEqual(ndr_row["Rel Diff NDR"], 0.5)
        self.assertEqual(ndr_row["Diff PDR"], 15)
        self.assertEqual(ndr_row["Rel Diff PDR"], 0.5)

    def test_process_release_warns_and_continues_after_bad_report(self):
        tags = ["NIC_Intel", "DRV_VFIO_PCI", "64B", "1C", "ethip4-ip4base", "MRR"]
        message = "Maximum Receive Rate trial results in packets per second: [10, 10]"
        rows = [
            cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://bad", 2),
            cr.WorkbookRow("vpp", "2n", "iterative", "mrr", "tb", "http://good", 3),
        ]

        def fetcher(log_url, cache_dir, timeout, retries, offline):
            if "bad" in log_url:
                return b"<html>not a robot report</html>"
            return gzipped_report("64B-1c-ethip4-ip4base-mrr", tags, "Pass", message)

        with tempfile.TemporaryDirectory() as tmp:
            messages = []
            aggregates = cr.process_release(
                rows,
                Path(tmp),
                1,
                0,
                False,
                fetcher=fetcher,
                release_label="2602",
                logger=messages.append,
            )

        self.assertEqual(len(aggregates), 1)
        aggregate = next(iter(aggregates.values()))
        self.assertEqual(aggregate.status, "Pass")
        self.assertEqual(aggregate.standard_values, [10])
        self.assertTrue(any("WARNING: skipped http://bad/report.html.gz" in message for message in messages))

    def test_download_report_offline_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            url = "http://example.invalid/build/123"
            data = gzip.compress(b"<html></html>")
            cr.cache_file_for_url(cache_dir, cr.report_url(url)).write_bytes(data)
            self.assertEqual(cr.download_report(url, cache_dir, offline=True), data)
            with self.assertRaises(cr.LogFetchError):
                cr.download_report("http://example.invalid/build/missing", cache_dir, offline=True)

    def test_end_to_end_compare_with_mocked_fetcher(self):
        tags = ["NIC_Intel", "DRV_VFIO_PCI", "64B", "1C", "ethip4-ip4base", "MRR"]
        current_message = "Maximum Receive Rate trial results in packets per second: [20, 20]"
        previous_message = "Maximum Receive Rate trial results in packets per second: [10, 10]"

        def fetcher(log_url, cache_dir, timeout, retries, offline):
            if "current" in log_url:
                return gzipped_report("64B-1c-ethip4-ip4base-mrr", tags, "Pass", current_message)
            return gzipped_report("64B-1c-ethip4-ip4base-mrr", tags, "Pass", previous_message)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            previous_path = tmp_path / "2601.xlsx"
            current_path = tmp_path / "2602.xlsx"
            output_path = tmp_path / "out.xlsx"
            messages = []
            make_workbook(previous_path, [["vpp", "2n", "iterative", "mrr", "tb", "http://previous"]])
            make_workbook(current_path, [["vpp", "2n", "iterative", "mrr", "tb", "http://current"]])

            cr.compare_workbooks(
                previous_path,
                current_path,
                output_path,
                tmp_path / "cache",
                1,
                0,
                False,
                None,
                fetcher,
                messages.append,
            )
            workbook = openpyxl.load_workbook(output_path, data_only=True)
            worksheet = workbook["Comparison"]
            headers = [cell.value for cell in worksheet[1]]
            values = [cell.value for cell in worksheet[2]]
            workbook.close()

        self.assertEqual(headers, cr.OUTPUT_COLUMNS)
        self.assertNotIn("Testbed", headers)
        self.assertNotIn("Log current", headers)
        self.assertNotIn("Log previous", headers)
        row = dict(zip(headers, values))
        self.assertEqual(row["Status"], "Pass")
        self.assertEqual(row["Mean current"], 20)
        self.assertEqual(row["Mean previous"], 10)
        self.assertEqual(row["Diff"], 10)
        self.assertAlmostEqual(row["Rel Diff"], 0.5)
        self.assertTrue(any("Reading previous workbook" in message for message in messages))
        self.assertTrue(any("Done:" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
