import unittest

from dashboard.settings import get_settings


class SettingsValidationTests(unittest.TestCase):
    def test_valid_defaults_have_no_validation_errors(self):
        settings = get_settings(environ={})

        self.assertEqual(settings.data_mode, "s3")
        self.assertEqual(settings.time_period, 200)
        self.assertEqual(settings.refresh_interval_seconds, 0)
        self.assertEqual(settings.cors_allow_origins, ("*",))
        self.assertEqual(settings.max_pool_size, 30)
        self.assertEqual(settings.telemetry_max_source_rows, 500)
        self.assertEqual(settings.telemetry_max_samples, 100_000)
        self.assertEqual(settings.validation_errors, ())
        self.assertTrue(settings.configuration_status()["valid"])
        self.assertEqual(
            settings.configuration_status()["values"]["CSIT_CORS_ALLOW_ORIGINS"],
            ["*"],
        )

    def test_fixture_data_mode_normalizes(self):
        settings = get_settings(environ={"CSIT_DATA_MODE": " Fixture "})

        self.assertEqual(settings.data_mode, "fixture")
        self.assertEqual(settings.validation_errors, ())

    def test_invalid_data_mode_reports_field_error(self):
        settings = get_settings(environ={"CSIT_DATA_MODE": "local"})

        self.assertEqual(settings.data_mode, "local")
        self.assertFalse(settings.configuration_status()["valid"])
        self.assertEqual(settings.validation_errors[0]["field"], "CSIT_DATA_MODE")

    def test_invalid_integer_settings_report_errors(self):
        settings = get_settings(
            environ={
                "CSIT_TIME_PERIOD": "abc",
                "CSIT_REFRESH_INTERVAL_SECONDS": "soon",
                "CSIT_MAX_POOL_SIZE": "0",
                "CSIT_TELEMETRY_MAX_SOURCE_ROWS": "none",
                "CSIT_TELEMETRY_MAX_SAMPLES": "0",
            }
        )
        fields = {error["field"] for error in settings.validation_errors}

        self.assertEqual(settings.time_period, 200)
        self.assertEqual(settings.refresh_interval_seconds, 0)
        self.assertEqual(settings.max_pool_size, 30)
        self.assertEqual(
            fields,
            {
                "CSIT_TIME_PERIOD",
                "CSIT_REFRESH_INTERVAL_SECONDS",
                "CSIT_MAX_POOL_SIZE",
                "CSIT_TELEMETRY_MAX_SOURCE_ROWS",
                "CSIT_TELEMETRY_MAX_SAMPLES",
            },
        )

    def test_negative_time_period_is_invalid(self):
        settings = get_settings(environ={"CSIT_TIME_PERIOD": "-1"})

        self.assertEqual(settings.time_period, 200)
        self.assertEqual(settings.validation_errors[0]["field"], "CSIT_TIME_PERIOD")
        self.assertIn("positive integer", settings.validation_errors[0]["message"])

    def test_time_period_above_max_is_valid_and_capped(self):
        settings = get_settings(environ={"CSIT_TIME_PERIOD": "999"})

        self.assertEqual(settings.time_period, 999)
        self.assertEqual(settings.effective_time_period(), 200)
        self.assertEqual(settings.validation_errors, ())

    def test_zero_and_negative_refresh_intervals_are_valid(self):
        zero = get_settings(environ={"CSIT_REFRESH_INTERVAL_SECONDS": "0"})
        negative = get_settings(environ={"CSIT_REFRESH_INTERVAL_SECONDS": "-1"})

        self.assertEqual(zero.refresh_interval_seconds, 0)
        self.assertEqual(negative.refresh_interval_seconds, -1)
        self.assertEqual(zero.validation_errors, ())
        self.assertEqual(negative.validation_errors, ())

    def test_invalid_boolean_flags_report_errors(self):
        settings = get_settings(
            environ={
                "CSIT_START_TRENDING": "maybe",
                "CSIT_START_REPORT": "perhaps",
                "CSIT_START_COVERAGE": "enabled",
                "CSIT_START_STATISTICS": "",
                "CSIT_START_FAILURES": "disabled",
            }
        )
        fields = {error["field"] for error in settings.validation_errors}

        self.assertEqual(
            fields,
            {
                "CSIT_START_TRENDING",
                "CSIT_START_REPORT",
                "CSIT_START_COVERAGE",
                "CSIT_START_STATISTICS",
                "CSIT_START_FAILURES",
            },
        )
        self.assertFalse(settings.configuration_status()["valid"])

    def test_cors_allow_origins_accepts_explicit_http_origins(self):
        settings = get_settings(
            environ={
                "CSIT_CORS_ALLOW_ORIGINS": (
                    " http://localhost:7860,https://csit.example "
                ),
            }
        )

        self.assertEqual(
            settings.cors_allow_origins,
            ("http://localhost:7860", "https://csit.example"),
        )
        self.assertEqual(settings.validation_errors, ())

    def test_invalid_cors_allow_origins_report_field_errors(self):
        invalid_origin = get_settings(
            environ={"CSIT_CORS_ALLOW_ORIGINS": "localhost:7860"}
        )
        wildcard_with_origin = get_settings(
            environ={"CSIT_CORS_ALLOW_ORIGINS": "*,http://localhost:7860"}
        )
        empty_origin = get_settings(environ={"CSIT_CORS_ALLOW_ORIGINS": ""})

        self.assertEqual(invalid_origin.cors_allow_origins, ("*",))
        self.assertEqual(
            invalid_origin.validation_errors[0]["field"],
            "CSIT_CORS_ALLOW_ORIGINS",
        )
        self.assertEqual(wildcard_with_origin.cors_allow_origins, ("*",))
        self.assertEqual(
            wildcard_with_origin.validation_errors[0]["field"],
            "CSIT_CORS_ALLOW_ORIGINS",
        )
        self.assertEqual(empty_origin.cors_allow_origins, ("*",))
        self.assertEqual(
            empty_origin.validation_errors[0]["field"],
            "CSIT_CORS_ALLOW_ORIGINS",
        )


if __name__ == "__main__":
    unittest.main()
