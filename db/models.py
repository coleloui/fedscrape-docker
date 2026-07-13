import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RateRecord(SQLModel, table=True):
    __tablename__ = "rate_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime.date = Field(unique=True, index=True)

    # Federal Funds effective rate
    federal_funds: Optional[str] = Field(default=None)

    # Commercial Paper — Nonfinancial
    cp_nonfinancial_1m: Optional[str] = Field(default=None)
    cp_nonfinancial_2m: Optional[str] = Field(default=None)
    cp_nonfinancial_3m: Optional[str] = Field(default=None)

    # Commercial Paper — Financial
    cp_financial_1m: Optional[str] = Field(default=None)
    cp_financial_2m: Optional[str] = Field(default=None)
    cp_financial_3m: Optional[str] = Field(default=None)

    # Bank Prime Loan
    bank_prime_loan: Optional[str] = Field(default=None)

    # Discount Window Primary Credit
    discount_window_primary: Optional[str] = Field(default=None)

    # Treasury Bills
    tbill_4w: Optional[str] = Field(default=None)
    tbill_3m: Optional[str] = Field(default=None)
    tbill_6m: Optional[str] = Field(default=None)
    tbill_1y: Optional[str] = Field(default=None)

    # Treasury Constant Maturities — Nominal
    treasury_1m: Optional[str] = Field(default=None)
    treasury_3m: Optional[str] = Field(default=None)
    treasury_6m: Optional[str] = Field(default=None)
    treasury_1y: Optional[str] = Field(default=None)
    treasury_2y: Optional[str] = Field(default=None)
    treasury_3y: Optional[str] = Field(default=None)
    treasury_5y: Optional[str] = Field(default=None)
    treasury_7y: Optional[str] = Field(default=None)
    treasury_10y: Optional[str] = Field(default=None)
    treasury_20y: Optional[str] = Field(default=None)
    treasury_30y: Optional[str] = Field(default=None)

    # TIPS — Inflation-Indexed Constant Maturities
    tips_5y: Optional[str] = Field(default=None)
    tips_7y: Optional[str] = Field(default=None)
    tips_10y: Optional[str] = Field(default=None)
    tips_20y: Optional[str] = Field(default=None)
    tips_30y: Optional[str] = Field(default=None)

    # Inflation-Indexed Long-Term Average
    inflation_long_term: Optional[str] = Field(default=None)


# Maps the original H.15 HTML column header to the model field name.
SCRAPE_COLUMN_MAP: dict[str, str] = {
    "Federal Funds": "federal_funds",
    "Commercial Paper - Nonfinancial - 1 Month": "cp_nonfinancial_1m",
    "Commercial Paper - Nonfinancial - 2 Month": "cp_nonfinancial_2m",
    "Commercial Paper - Nonfinancial - 3 Month": "cp_nonfinancial_3m",
    "Commercial Paper - Financial - 1 Month": "cp_financial_1m",
    "Commercial Paper - Financial - 2 Month": "cp_financial_2m",
    "Commercial Paper - Financial - 3 Month": "cp_financial_3m",
    "Bank Prime Loan": "bank_prime_loan",
    "Discount Window Primary Credit": "discount_window_primary",
    "U.S. Gov - Bills - 4 week": "tbill_4w",
    "U.S. Gov - Bills - 3 month": "tbill_3m",
    "U.S. Gov - Bills - 6 month": "tbill_6m",
    "U.S. Gov - Bills - 1 year": "tbill_1y",
    "U.S. Gov - Maturities - Nominal 9 - 1 month": "treasury_1m",
    "U.S. Gov - Maturities - Nominal 9 - 3 month": "treasury_3m",
    "U.S. Gov - Maturities - Nominal 9 - 6 month": "treasury_6m",
    "U.S. Gov - Maturities - Nominal 9 - 1 year": "treasury_1y",
    "U.S. Gov - Maturities - Nominal 9 - 2 year": "treasury_2y",
    "U.S. Gov - Maturities - Nominal 9 - 3 year": "treasury_3y",
    "U.S. Gov - Maturities - Nominal 9 - 5 year": "treasury_5y",
    "U.S. Gov - Maturities - Nominal 9 - 7 year": "treasury_7y",
    "U.S. Gov - Maturities - Nominal 9 - 10 year": "treasury_10y",
    "U.S. Gov - Maturities - Nominal 9 - 20 year": "treasury_20y",
    "U.S. Gov - Maturities - Nominal 9 - 30 year": "treasury_30y",
    "U.S. Gov - Maturities - Inflation indexed - 5 year": "tips_5y",
    "U.S. Gov - Maturities - Inflation indexed - 7 year": "tips_7y",
    "U.S. Gov - Maturities - Inflation indexed - 10 year": "tips_10y",
    "U.S. Gov - Maturities - Inflation indexed - 20 year": "tips_20y",
    "U.S. Gov - Maturities - Inflation indexed - 30 year": "tips_30y",
    "U.S. Gov - Inflation-Indexed Long-Term Average": "inflation_long_term",
}

# Ordered list of all rate-type field names (excludes id and date).
RATE_TYPES: list[str] = list(SCRAPE_COLUMN_MAP.values())
