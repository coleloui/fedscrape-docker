import datetime
from typing import Optional

from pydantic import BaseModel


class RateResponse(BaseModel):
    date: datetime.date
    federal_funds: Optional[str] = None
    cp_nonfinancial_1m: Optional[str] = None
    cp_nonfinancial_2m: Optional[str] = None
    cp_nonfinancial_3m: Optional[str] = None
    cp_financial_1m: Optional[str] = None
    cp_financial_2m: Optional[str] = None
    cp_financial_3m: Optional[str] = None
    bank_prime_loan: Optional[str] = None
    discount_window_primary: Optional[str] = None
    tbill_4w: Optional[str] = None
    tbill_3m: Optional[str] = None
    tbill_6m: Optional[str] = None
    tbill_1y: Optional[str] = None
    treasury_1m: Optional[str] = None
    treasury_3m: Optional[str] = None
    treasury_6m: Optional[str] = None
    treasury_1y: Optional[str] = None
    treasury_2y: Optional[str] = None
    treasury_3y: Optional[str] = None
    treasury_5y: Optional[str] = None
    treasury_7y: Optional[str] = None
    treasury_10y: Optional[str] = None
    treasury_20y: Optional[str] = None
    treasury_30y: Optional[str] = None
    tips_5y: Optional[str] = None
    tips_7y: Optional[str] = None
    tips_10y: Optional[str] = None
    tips_20y: Optional[str] = None
    tips_30y: Optional[str] = None
    inflation_long_term: Optional[str] = None

    model_config = {"from_attributes": True}


class RateSeriesEntry(BaseModel):
    date: datetime.date
    value: Optional[str] = None


class RateSeriesResponse(BaseModel):
    rate_type: str
    data: list[RateSeriesEntry]


class SpreadResponse(BaseModel):
    date: datetime.date
    rate_a: str
    rate_b: str
    spread: float


class RefreshResponse(BaseModel):
    upserted: int


class RateTypesResponse(BaseModel):
    rate_types: dict[str, str]


class RateAverageResponse(BaseModel):
    rate_type: str
    display_name: str
    days: int
    average: Optional[float] = None
