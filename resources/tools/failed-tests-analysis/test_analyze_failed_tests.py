import io
import tarfile
import tempfile
import unittest
from pathlib import Path

import analyze_failed_tests as aft


AVF_ROBOT = """
*** Settings ***
| Force Tags | PERFTEST | NIC_Intel-E810CQ | DRV_AVF
| ... | ethip4udp-ip4base-h65536-p63-s4128768-cps

*** Variables ***
| ${nic_name}= | Intel-E810CQ
| ${nic_driver}= | avf

*** Test Cases ***

| 64B-1c-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr
| | [Tags] | 64B | 1C
| | frame_size=${64} | phy_cores=${1}

| 64B-2c-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr
| | [Tags] | 64B | 2C
| | frame_size=${64} | phy_cores=${2}
"""


HOSTSTACK_ROBOT = """
*** Settings ***
| Force Tags | HOSTSTACK | TCP | NIC_Intel-E810CQ | DRV_VFIO_PCI
| ... | eth-ip4tcphttp-ldpreload-nginx-1_21_5

*** Variables ***
| ${nic_name}= | Intel-E810CQ
| ${nic_driver}= | vfio-pci

*** Test Cases ***

| 0B-1c-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps
| | [Tags] | 0B | 1c
| | frame_size=${0} | phy_cores=${1}

| 2048B-2c-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps
| | [Tags] | 2048B | 2c
| | frame_size=${2048} | phy_cores=${2}
"""


def make_execution(name, failed=False, **params):
    return aft.TestExecution(
        name=name,
        nic=params.get("nic", "100ge2p1e810cq"),
        driver=params.get("driver", "avf"),
        framesize=params.get("framesize", "64B"),
        cores=params.get("cores", "1c"),
        test_area=params.get("test_area", "ip4base"),
        failed=failed,
        row_number=2,
        run="run",
        run_url="https://example.invalid/run",
        log_url="https://example.invalid/log",
        source_file="suite.robot",
    )


class FailedTestAnalysisTests(unittest.TestCase):
    def test_split_failed_tests(self):
        self.assertEqual(
            aft.split_failed_tests("a; b ; ; c"),
            ["a", "b", "c"],
        )

    def test_group_id_rules(self):
        iterative = {"DUT": "vpp", "Node": "2n", "Job type": "iterative", "Test type": "mrr"}
        coverage = {"DUT": "vpp", "Node": "2n", "Job type": "coverage", "Test type": "ndrpdr"}
        self.assertEqual(aft.group_id_for_row(iterative, 10), "vpp|2n|iterative|mrr")
        self.assertEqual(aft.group_id_for_row(coverage, 10), "vpp|2n|coverage|ndrpdr|row-10")

    def test_parse_avf_robot_file(self):
        tests = aft.parse_robot_file(
            "generated/tests/vpp/perf/ip4/2n1l-100ge2p1e810cq-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr.robot",
            AVF_ROBOT,
        )
        self.assertEqual(len(tests), 2)
        first = tests[0]
        self.assertEqual(first["NIC"], "100ge2p1e810cq")
        self.assertEqual(first["Driver"], "avf")
        self.assertEqual(first["Framesize"], "64B")
        self.assertEqual(first["Number of cores"], "1c")
        self.assertEqual(first["Test area"], "ethip4udp-ip4base-h65536-p63-s4128768-cps")

    def test_parse_avf_robot_file_without_topology_prefix(self):
        tests = aft.parse_robot_file(
            "generated/tests/vpp/perf/ip4/100ge2p1e810cq-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr.robot",
            AVF_ROBOT,
        )
        first = tests[0]
        self.assertEqual(first["NIC"], "100ge2p1e810cq")
        self.assertEqual(first["Driver"], "avf")
        self.assertEqual(first["Test area"], "ethip4udp-ip4base-h65536-p63-s4128768-cps")

    def test_parse_hoststack_driver_from_variable_without_stripping_eth_area(self):
        tests = aft.parse_robot_file(
            "generated/tests/vpp/perf/hoststack/2n1l-100ge2p1e810cq-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps.robot",
            HOSTSTACK_ROBOT,
        )
        self.assertEqual(len(tests), 2)
        first = tests[0]
        self.assertEqual(first["NIC"], "100ge2p1e810cq")
        self.assertEqual(first["Driver"], "vfio-pci")
        self.assertEqual(first["Framesize"], "0B")
        self.assertEqual(first["Number of cores"], "1c")
        self.assertEqual(first["Test area"], "eth-ip4tcphttp-ldpreload-nginx-1_21_5")

    def test_parse_hoststack_without_topology_prefix_keeps_nic_and_eth_area(self):
        tests = aft.parse_robot_file(
            "generated/tests/vpp/perf/hoststack/100ge2p1e810cq-eth-ip4tcphttp-ldpreload-nginx-1_21_5-cps.robot",
            HOSTSTACK_ROBOT,
        )
        first = tests[0]
        self.assertEqual(first["NIC"], "100ge2p1e810cq")
        self.assertEqual(first["Driver"], "vfio-pci")
        self.assertEqual(first["Test area"], "eth-ip4tcphttp-ldpreload-nginx-1_21_5")

    def test_parse_generated_archive_marks_exact_failed_tests(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "generated_tests.tar.gz"
            member_name = (
                "scratch/generated/tests/vpp/perf/ip4/"
                "2n1l-100ge2p1e810cq-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr.robot"
            )
            with tarfile.open(archive_path, "w:gz") as archive:
                data = AVF_ROBOT.encode("utf-8")
                info = tarfile.TarInfo(member_name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))

            failed_name = "64B-2c-avf-ethip4udp-ip4base-h65536-p63-s4128768-cps-ndrpdr"
            run = aft.parse_generated_tests_archive(
                archive_path,
                {failed_name},
                {"Run": "run", "Run URL": "url", "Log": "log"},
                2,
            )
            self.assertEqual(len(run.executions), 2)
            self.assertEqual([execution.failed for execution in run.executions], [False, True])
            self.assertEqual(run.unmatched_failures, [])

    def test_mine_patterns_finds_all_failed_framesize(self):
        executions = [
            make_execution("a", failed=True, framesize="9000B", cores="1c"),
            make_execution("b", failed=True, framesize="9000B", cores="2c"),
            make_execution("c", failed=False, framesize="64B", cores="1c"),
            make_execution("d", failed=False, framesize="64B", cores="2c"),
        ]
        candidates = aft.mine_candidates(executions, min_failed_share=0.30, min_lift=1.5)
        candidate_params = [dict(candidate.params) for candidate in candidates]
        self.assertIn({"Framesize": "9000B"}, candidate_params)

    def test_no_failure_group_returns_no_failed_tests_message(self):
        row = {
            "DUT": "vpp",
            "Node": "2n",
            "Job type": "iterative",
            "Test type": "mrr",
        }
        run = aft.RunAnalysis(row=row, row_number=2, executions=[make_execution("a", failed=False)])
        group = aft.GroupAnalysis("vpp|2n|iterative|mrr", aft.group_meta_for_row(row, 2), [run])
        findings = aft.findings_for_group(group, min_failed_share=0.30, min_lift=1.5, top_per_group=5)
        self.assertEqual(len(findings), 1)
        self.assertIn("There are no failed tests", findings[0]["Finding"])


if __name__ == "__main__":
    unittest.main()
