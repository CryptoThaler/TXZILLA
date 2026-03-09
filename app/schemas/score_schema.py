from typing import Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    list_price: float = Field(gt=0)
    acquisition_basis: Optional[float] = Field(default=None, gt=0)
    estimated_rent: float = Field(ge=0)
    taxes_monthly: float = Field(default=0, ge=0)
    insurance_monthly: float = Field(default=0, ge=0)
    maintenance_monthly: float = Field(default=0, ge=0)
    hoa_monthly: float = Field(default=0, ge=0)
    vacancy_reserve_monthly: float = Field(default=0, ge=0)
    management_cost_monthly: float = Field(default=0, ge=0)
    appreciation_score: float = Field(default=50, ge=0, le=100)
    market_growth_score: float = Field(default=50, ge=0, le=100)
    risk_inverse_score: float = Field(default=50, ge=0, le=100)
    liquidity_score: float = Field(default=50, ge=0, le=100)


class ScoreResponse(BaseModel):
    monthly_cash_flow: float
    annual_noi: float
    cap_rate: float
    cash_flow_score: float
    investment_score: float
    assumptions: list[str]
