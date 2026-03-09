from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.property_schema import PropertyDetail


class MarketFeatureValue(BaseModel):
    feature_name: str
    feature_value: float
    value_unit: Optional[str] = None
    effective_date: str


class MarketContextResponse(BaseModel):
    region_key: str
    property_type: str
    bedroom_count: Optional[int] = None
    median_rent: float
    vacancy_rate: Optional[float] = None
    growth_yoy: Optional[float] = None
    appreciation_score: float
    market_growth_score: float
    liquidity_score: float
    target_cap_rate: float
    market_growth_rate: float
    features: list[MarketFeatureValue] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ValuationResponse(BaseModel):
    estimated_value: float
    income_approach_value: float
    market_anchor_value: float
    discount_to_value: float
    confidence: float
    assumptions: list[str] = Field(default_factory=list)


class RiskLayerResponse(BaseModel):
    risk_layer: str
    risk_level: str
    risk_score: float
    source_name: str
    source_record_id: str
    effective_date: str


class RiskAssessmentResponse(BaseModel):
    overall_risk_score: float
    risk_inverse_score: float
    parcel_confidence_penalty: float
    layers: list[RiskLayerResponse] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class LandTransitionResponse(BaseModel):
    transition_score: float
    strategy: str
    assumptions: list[str] = Field(default_factory=list)


class InvestmentAnalysisResponse(BaseModel):
    formula_version: str
    acquisition_basis: float
    monthly_cash_flow: float
    annual_noi: float
    cap_rate: float
    cash_flow_score: float
    appreciation_score: float
    market_growth_score: float
    risk_inverse_score: float
    liquidity_score: float
    investment_score: float
    assumptions: list[str] = Field(default_factory=list)


class PropertyAnalysisReport(BaseModel):
    property: PropertyDetail
    market: MarketContextResponse
    valuation: ValuationResponse
    risk: RiskAssessmentResponse
    land_transition: LandTransitionResponse
    investment: InvestmentAnalysisResponse
