import logging
from datetime import timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

log = logging.getLogger(__name__)

URL_TEMPLATE = (
    "https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{yyyymm}_{region}.csv"
)
# NEM time: UTC+10
NEM_TZ = timezone(timedelta(hours=10))


def fetch_prices(raw_dir: Path, yyyymm: str, region: str) -> Path:
    """Return the cached CSV for a month, downloading it from AEMO if needed."""
    path = raw_dir / f"PRICE_AND_DEMAND_{yyyymm}_{region}.csv"
    if path.exists():
        return path
    url = URL_TEMPLATE.format(yyyymm=yyyymm, region=region)
    log.info("downloading %s", url)
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    raw_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(response.text)
    return path


def load_prices(raw_dir: Path, yyyymm: str, region: str) -> pd.DataFrame:
    raw = pd.read_csv(fetch_prices(raw_dir, yyyymm, region))
    return pd.DataFrame(
        {
            "settlement_time": pd.to_datetime(raw["SETTLEMENTDATE"]).dt.tz_localize(NEM_TZ),
            "rrp": raw["RRP"].astype(float),
        }
    )
