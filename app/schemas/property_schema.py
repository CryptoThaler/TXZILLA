from typing import Optional

from pydantic import BaseModel, Field


class ListingSnapshot(BaseModel):
    listing_id: str
    source_name: str
    source_record_id: str
    listing_status: str
    list_price: float
    listed_at: Optional[str] = None
    removed_at: Optional[str] = None
    days_on_market: Optional[int] = None
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    building_area_sqft: Optional[float] = None
    lot_size_acres: Optional[float] = None


class TransactionSnapshot(BaseModel):
    transaction_id: str
    transaction_type: str
    recorded_date: str
    sale_price: Optional[float] = None
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None


class LandFeatureSnapshot(BaseModel):
    feature_name: str
    feature_value: Optional[float] = None
    value_unit: Optional[str] = None
    effective_date: str
    source_name: str
    source_record_id: str


class AssessmentSnapshot(BaseModel):
    tax_year: int
    assessed_total_value: float
    assessed_land_value: Optional[float] = None
    assessed_improvement_value: Optional[float] = None
    taxable_value: Optional[float] = None
    tax_amount_annual: Optional[float] = None
    source_name: str
    source_record_id: str
    source_observed_at: str


class OwnershipSnapshot(BaseModel):
    owner_name: str
    ownership_start_date: Optional[str] = None
    ownership_end_date: Optional[str] = None
    mailing_address: Optional[str] = None
    source_name: str
    source_record_id: str
    source_observed_at: str


class PropertySummary(BaseModel):
    property_id: str
    address_line1: str
    city: str
    county: str
    region_key: str
    property_type: str
    bedrooms: Optional[float] = None
    bathrooms: Optional[float] = None
    building_area_sqft: Optional[float] = None
    estimated_rent: Optional[float] = None
    active_listing: Optional[ListingSnapshot] = None
    latest_assessment: Optional[AssessmentSnapshot] = None


class PropertyDetail(PropertySummary):
    parcel_number: str
    state: str = Field(default="TX")
    postal_code: Optional[str] = None
    latitude: float
    longitude: float
    lot_size_acres: Optional[float] = None
    zoning_code: Optional[str] = None
    land_use_code: Optional[str] = None
    parcel_resolution_confidence: float
    taxes_monthly: float
    insurance_monthly: float
    maintenance_monthly: float
    hoa_monthly: float
    vacancy_reserve_monthly: float
    management_cost_monthly: float
    source_name: str
    source_record_id: str
    source_observed_at: str
    source_fetched_at: str
    last_transaction: Optional[TransactionSnapshot] = None
    land_features: list[LandFeatureSnapshot] = Field(default_factory=list)
    latest_assessment: Optional[AssessmentSnapshot] = None
    ownership_history: list[OwnershipSnapshot] = Field(default_factory=list)


class SearchResponse(BaseModel):
    total: int
    items: list[PropertySummary]
    region_key: Optional[str] = None
    counties: list[str] = Field(default_factory=list)
