"""Resource helper compatibility functions."""

from typing import Mapping

import pandas as pd

from ..services.data_cache import DataCacheService
from ..settings import get_settings


def load_parquet() -> Mapping[str, pd.DataFrame]:
    """Load CSIT parquet data for the configured time window.

    This compatibility wrapper preserves the previous helper API while the
    cache ownership now lives in ``DataCacheService``.

    Returns:
        Mapping of CSIT data categories to Pandas dataframes.
    """
    return DataCacheService(settings=get_settings()).load()
