FRED API client

This small script fetches time-series data from the St. Louis Fed (FRED) API and
returns it as a pandas DataFrame. It can also save the series to CSV.

Setup

- Install dependencies:

```bash
python -m pip install -r requirements.txt
```

- Obtain a FRED API key from https://fred.stlouisfed.org and set it as an environment variable:

```bash
export FRED_API_KEY=your_key_here
```

Usage examples

- Print the first rows of the GDP series:

```bash
python fred_client.py GDP --start 2000-01-01 --end 2020-12-31 --head
```

- Save a series to CSV:

```bash
python fred_client.py UNRATE -o unemployment.csv
```

- Override the API key on the command line:

```bash
python fred_client.py CPIAUCSL --api-key YOUR_KEY -o cpi.csv
```

Notes

- The script reads `FRED_API_KEY` from the environment if `--api-key` is not provided.
- The returned DataFrame uses a DateTime index and `value` column as float (NaN when missing).
