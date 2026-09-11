import unittest

import pandas as pd

from dashboard.ui.dashboard import build_dashboard, build_status_page


class DashboardUITests(unittest.TestCase):
    def test_build_dashboard_returns_html(self):
        statistics = pd.DataFrame(
            {
                "job": ["job-a"],
                "build": [1],
                "start_time": ["2026-06-05"],
                "duration": [123],
            }
        )

        html = build_dashboard(statistics)

        self.assertIsInstance(html, str)
        self.assertIn("CSIT dashboard", html)

    def test_build_status_page_returns_not_ready_html(self):
        html = build_status_page({"status": "loading", "ready": False})

        self.assertIsInstance(html, str)
        self.assertIn("CSIT data is not ready", html)


if __name__ == "__main__":
    unittest.main()
