"""Semantic metadata helpers for configured CSIT result columns."""

from pathlib import Path
from typing import Any

from yaml import YAMLError, safe_load


DEFAULT_RESULT_METADATA_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "result_metadata.yaml"
)
DEFAULT_COMPARABLE_DIMENSIONS = [
    "hosts",
    "test_id",
    "build",
    "release",
    "job",
    "dut_type",
    "dut_version",
    "tg_type",
    "passed",
    "start_time",
]
VALID_PREFERRED_DIRECTIONS = {"higher", "lower", "neutral"}


class ResultMetadataService:
    """Load and expose static semantic metadata for result columns."""

    def __init__(self, metadata_file: str | Path | None = None) -> None:
        self._metadata_file = Path(metadata_file or DEFAULT_RESULT_METADATA_FILE)
        raw = self._load_metadata(self._metadata_file)
        self._default_comparable_dimensions = self._normalize_dimensions(
            raw.get("default_comparable_dimensions"),
            DEFAULT_COMPARABLE_DIMENSIONS,
        )
        self._results = self._normalize_results(
            raw.get("results"),
            self._default_comparable_dimensions,
        )

    @property
    def metadata_file(self) -> Path:
        """Return the metadata file path used by this service."""

        return self._metadata_file

    @property
    def default_comparable_dimensions(self) -> list[str]:
        """Return default dimensions used when an entry does not override them."""

        return list(self._default_comparable_dimensions)

    @property
    def result_columns(self) -> list[str]:
        """Return result columns that have semantic metadata."""

        return sorted(self._results)

    def all_metadata(self) -> dict[str, dict[str, Any]]:
        """Return all known result metadata keyed by column name."""

        return {
            column: dict(metadata)
            for column, metadata in sorted(self._results.items())
        }

    def metadata_for_column(self, column: str) -> dict[str, Any] | None:
        """Return metadata for one column, or None when it is unknown."""

        metadata = self._results.get(column)
        if metadata is None:
            return None
        return dict(metadata)

    def metadata_for_columns(self, columns: list[str]) -> dict[str, dict[str, Any]]:
        """Return metadata for all known columns in stable key order."""

        return {
            column: metadata
            for column in sorted(columns)
            if (metadata := self.metadata_for_column(column)) is not None
        }

    @staticmethod
    def _load_metadata(metadata_file: Path) -> dict[str, Any]:
        try:
            loaded = safe_load(metadata_file.read_text(encoding="utf-8")) or {}
        except (OSError, YAMLError):
            return {}
        if not isinstance(loaded, dict):
            return {}
        return loaded

    @classmethod
    def _normalize_results(
            cls,
            raw_results: Any,
            default_dimensions: list[str]
        ) -> dict[str, dict[str, Any]]:
        if not isinstance(raw_results, dict):
            return {}

        results: dict[str, dict[str, Any]] = {}
        for column, raw_entry in raw_results.items():
            if not isinstance(column, str) or not column.startswith("result_"):
                continue
            if not isinstance(raw_entry, dict):
                continue
            entry = cls._normalize_entry(column, raw_entry, default_dimensions)
            if entry is not None:
                results[column] = entry
        return results

    @classmethod
    def _normalize_entry(
            cls,
            column: str,
            raw_entry: dict[str, Any],
            default_dimensions: list[str]
        ) -> dict[str, Any] | None:
        display_name = str(raw_entry.get("display_name") or column)
        preferred_direction = str(
            raw_entry.get("preferred_direction") or "neutral"
        ).lower()
        if preferred_direction not in VALID_PREFERRED_DIRECTIONS:
            preferred_direction = "neutral"

        entry: dict[str, Any] = {
            "display_name": display_name,
            "scale": cls._normalize_scale(raw_entry.get("scale")),
            "preferred_direction": preferred_direction,
            "comparable_dimensions": cls._normalize_dimensions(
                raw_entry.get("comparable_dimensions"),
                default_dimensions,
            ),
            "description": str(raw_entry.get("description") or ""),
        }

        unit = raw_entry.get("unit")
        unit_column = raw_entry.get("unit_column")
        if isinstance(unit_column, str) and unit_column:
            entry["unit_column"] = unit_column
        elif isinstance(unit, str) and unit:
            entry["unit"] = unit
        else:
            entry["unit"] = "unknown"
        return entry

    @staticmethod
    def _normalize_dimensions(
            raw_dimensions: Any,
            fallback: list[str]
        ) -> list[str]:
        if not isinstance(raw_dimensions, list):
            return list(fallback)
        dimensions: list[str] = []
        for value in raw_dimensions:
            if not isinstance(value, str):
                continue
            dimension = value.strip()
            if dimension and dimension not in dimensions:
                dimensions.append(dimension)
        return dimensions or list(fallback)

    @staticmethod
    def _normalize_scale(raw_scale: Any) -> int | float:
        if isinstance(raw_scale, bool):
            return 1
        if isinstance(raw_scale, (int, float)):
            return raw_scale
        try:
            return float(raw_scale)
        except (TypeError, ValueError):
            return 1
