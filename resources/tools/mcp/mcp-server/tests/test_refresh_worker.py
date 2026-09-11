import tempfile
import unittest
from pathlib import Path

from dashboard.services.refresh_worker import run_cache_refresh_worker
from dashboard.settings import get_settings


class RefreshWorkerTests(unittest.TestCase):
    def test_fixture_generation_is_built_in_disposable_process(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot_path = Path(directory) / "snapshot"
            settings = get_settings(environ={
                "CSIT_DATA_MODE": "fixture",
                "CSIT_TIME_PERIOD": "200",
                "CSIT_CACHE_SNAPSHOT_PATH": str(snapshot_path),
            })

            result = run_cache_refresh_worker(settings, timeout_seconds=30)

            self.assertEqual(result["status"], "ready")
            self.assertEqual(result["worker_exit_code"], 0)
            self.assertTrue((snapshot_path / "manifest.json").is_file())
            self.assertGreater(result["row_counts"]["trending"], 0)


if __name__ == "__main__":
    unittest.main()
