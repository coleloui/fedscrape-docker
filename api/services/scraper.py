"""Port of scrape.py — parses the Fed H.15 HTML table into RateRecord objects."""

import datetime
import unicodedata

import pandas as pd
import requests
from bs4 import BeautifulSoup

from db.models import SCRAPE_COLUMN_MAP, RateRecord

FED_H15_URL = "https://www.federalreserve.gov/releases/h15/"

# Column names in the order they appear in the H.15 HTML table
# (skipped rows are handled separately below).
_TABLE_COLUMNS = [
    "date",
    "Federal Funds",
    "Commercial Paper - Nonfinancial - 1 Month",
    "Commercial Paper - Nonfinancial - 2 Month",
    "Commercial Paper - Nonfinancial - 3 Month",
    "Commercial Paper - Financial - 1 Month",
    "Commercial Paper - Financial - 2 Month",
    "Commercial Paper - Financial - 3 Month",
    "Bank Prime Loan",
    "Discount Window Primary Credit",
    "U.S. Gov - Bills - 4 week",
    "U.S. Gov - Bills - 3 month",
    "U.S. Gov - Bills - 6 month",
    "U.S. Gov - Bills - 1 year",
    "U.S. Gov - Maturities - Nominal 9 - 1 month",
    "U.S. Gov - Maturities - Nominal 9 - 3 month",
    "U.S. Gov - Maturities - Nominal 9 - 6 month",
    "U.S. Gov - Maturities - Nominal 9 - 1 year",
    "U.S. Gov - Maturities - Nominal 9 - 2 year",
    "U.S. Gov - Maturities - Nominal 9 - 3 year",
    "U.S. Gov - Maturities - Nominal 9 - 5 year",
    "U.S. Gov - Maturities - Nominal 9 - 7 year",
    "U.S. Gov - Maturities - Nominal 9 - 10 year",
    "U.S. Gov - Maturities - Nominal 9 - 20 year",
    "U.S. Gov - Maturities - Nominal 9 - 30 year",
    "U.S. Gov - Maturities - Inflation indexed - 5 year",
    "U.S. Gov - Maturities - Inflation indexed - 7 year",
    "U.S. Gov - Maturities - Inflation indexed - 10 year",
    "U.S. Gov - Maturities - Inflation indexed - 20 year",
    "U.S. Gov - Maturities - Inflation indexed - 30 year",
    "U.S. Gov - Inflation-Indexed Long-Term Average",
]

# Row indices to skip — they contain section headers, not data.
_SKIP_ROWS = {2, 3, 7, 13, 14, 19, 20, 32}


def _month_to_number(month: str) -> str:
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    }
    try:
        return months[month]
    except KeyError:
        raise ValueError(f"Unrecognised month abbreviation: {month!r}")


def _build_dataframe(table_rows: list) -> pd.DataFrame:
    """Convert parsed HTML <tr> rows into a tidy DataFrame (one row per date)."""
    linked: list[list[str]] = []
    row_data: list[str] = []

    for i, tr in enumerate(table_rows):
        if i in _SKIP_ROWS:
            continue

        cells = tr.find_all(["td", "th"])
        for j, cell in enumerate(cells):
            text = unicodedata.normalize("NFKD", cell.text).strip()
            # The H.15 table interleaves label and data cells; skip label cols.
            if int((j - 1) / 2) == 0 or j % 2 == 0:
                continue

            if i == 0:
                # Date header row
                year = text[0:4]
                month_abbr = text[4:7]
                month_num = _month_to_number(month_abbr)
                day_raw = text[7:]
                day = day_raw[:-1] if len(day_raw) > 2 else day_raw
                row_data.append(f"{year}-{month_num}-{day.zfill(2)}")
            else:
                row_data.append(text if text else "n.a.")

        if not row_data:
            continue
        linked.append(row_data)
        row_data = []

    data_dict = dict(zip(_TABLE_COLUMNS, linked))
    return pd.DataFrame(data=data_dict)


def scrape_latest() -> list[RateRecord]:
    """
    Fetch the Fed H.15 release page and return a list of RateRecord objects.

    Raises:
        requests.HTTPError: if the HTTP request fails.
        ValueError: if the expected table is missing from the page.
    """
    response = requests.get(FED_H15_URL, timeout=30)
    response.raise_for_status()

    doc = BeautifulSoup(response.text, "html.parser")
    table = doc.find(id="h15table")
    if table is None:
        raise ValueError("Could not locate #h15table on the Fed H.15 page.")

    df = _build_dataframe(table.findChildren("tr"))

    records: list[RateRecord] = []
    for _, row in df.iterrows():
        record_data: dict = {"date": datetime.date.fromisoformat(str(row["date"]))}
        for col_header, field_name in SCRAPE_COLUMN_MAP.items():
            raw = row.get(col_header)
            record_data[field_name] = None if (raw is None or raw == "n.a.") else str(raw)
        records.append(RateRecord(**record_data))

    return records
