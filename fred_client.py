"""Simple FRED API client to fetch a series as a pandas DataFrame.

Usage examples:
  export FRED_API_KEY=YOUR_KEY
  python fred_client.py GDP --start 2000-01-01 --end 2020-12-31 -o gdp.csv

The script uses the FRED "series/observations" endpoint and returns a DataFrame
with a DateTime index and numeric `value` column (NaN for missing values).
"""

import os
import argparse
from typing import Optional

import requests
import pandas as pd

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"


def get_fred_series(
    series_id: str,
    api_key: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch a FRED series and return a pandas DataFrame indexed by date.

    Args:
        series_id: FRED series id (e.g., GDP, UNRATE)
        api_key: FRED API key (if None, will read from env FRED_API_KEY)
        start_date: optional start date string YYYY-MM-DD
        end_date: optional end date string YYYY-MM-DD
        frequency: optional frequency (e.g., "m", "q", "a")

    Returns:
        DataFrame with index=DatetimeIndex and column `value` as float.
    """
    key = api_key or os.environ.get("FRED_API_KEY")
    if not key:
        raise RuntimeError("FRED API key is required (env FRED_API_KEY or --api-key)")

    params = {
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
    }
    if start_date:
        params["observation_start"] = start_date
    if end_date:
        params["observation_end"] = end_date
    if frequency:
        params["frequency"] = frequency

    resp = requests.get(FRED_BASE, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    obs = data.get("observations", [])
    if not obs:
        return pd.DataFrame(columns=["value"])  # empty

    df = pd.DataFrame(obs)
    # expected keys: date, value (value may be "." for missing)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
    # convert value to numeric, coerce non-numeric to NaN
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Fetch a FRED time series into CSV or print head."
    )
    parser.add_argument("series_id", help="FRED series id (e.g., GDP)")
    parser.add_argument("--start", dest="start", help="start date YYYY-MM-DD")
    parser.add_argument("--end", dest="end", help="end date YYYY-MM-DD")
    parser.add_argument(
        "--frequency", dest="frequency", help="frequency (d, w, m, q, a)"
    )
    parser.add_argument(
        "--api-key", dest="api_key", help="FRED API key (overrides env)"
    )
    parser.add_argument("-o", "--out", dest="out", help="Write CSV to path")
    parser.add_argument(
        "--head", action="store_true", help="Print first 10 rows instead of saving"
    )

    args = parser.parse_args()

    df = get_fred_series(
        args.series_id,
        api_key=args.api_key,
        start_date=args.start,
        end_date=args.end,
        frequency=args.frequency,
    )

    if args.head or not args.out:
        print(df.head(10))

    if args.out:
        df.to_csv(args.out)
        print(f"Saved {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
