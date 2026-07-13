"""Port of download.py — parallel bulk download of Fed H.15 CSV series."""

import os
from concurrent.futures import ThreadPoolExecutor

import requests

_BASE_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx"
    "?rel=H15&series={series}&lastobs=&from=01/01/2000&to={to_date}"
    "&filetype=csv&label=omit&layout=seriescolumn"
)

# Series IDs and the local directory name for each series.
SERIES: dict[str, str] = {
    "federal_eff_funds": "c5025f4bbbed155a6f17c587772ed69e",
    "commercial_paper_nonfinancial": "ca2dd1ccd5102a49176c86b6646496c3",
    "commercial_paper_financial": "268dcdcf1b746c42fb990fe2107b7dad",
    "bank_prime_loan": "02338be6957591cdba0a59c6f09b8389",
    "discount_window_primary_credit": "e048853c9a3f0734b8538f508828f298",
    "us_gov_securities_tresury_bills": "4ab494d223ec49ec01fe09b49c6d17da",
    "maturities_nominal_9": "bf17364827e38702b42a58cf8eaa3f78",
    "maturities_inflation_indexed": "a5efc8cebeae2f178010054da08cb1f1",
    "inflation_indexed_long_term": "68447ee78d1e78718e4a96db9405d605",
}


def _build_url(series_id: str, to_date: str = "12/31/2099") -> str:
    return _BASE_URL.format(series=series_id, to_date=to_date)


def _download_one(name: str, url: str, dest_dir: str) -> None:
    os.makedirs(os.path.join(dest_dir, name), exist_ok=True)
    path = os.path.join(dest_dir, name, f"{name}.csv")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(response.content)
        print(f"Downloaded: {name}")
    except requests.exceptions.RequestException as exc:
        print(f"Failed to download {name}: {exc}")


def bulk_download(dest_dir: str = "download") -> None:
    """Download all Fed H.15 series CSVs into dest_dir/<series_name>/."""
    items = [(name, _build_url(sid)) for name, sid in SERIES.items()]
    with ThreadPoolExecutor() as executor:
        for name, url in items:
            executor.submit(_download_one, name, url, dest_dir)
