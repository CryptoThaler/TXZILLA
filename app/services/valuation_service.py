from app.schemas.analysis_schema import MarketContextResponse, ValuationResponse
from app.schemas.property_schema import PropertyDetail


MARKET_ANCHOR_WEIGHT = 0.55
INCOME_ANCHOR_WEIGHT = 0.45


def build_valuation(
    property_detail: PropertyDetail,
    market_context: MarketContextResponse,
) -> ValuationResponse:
    assumptions: list[str] = []
    active_listing = property_detail.active_listing
    last_transaction = property_detail.last_transaction
    latest_assessment = property_detail.latest_assessment

    rent_estimate = property_detail.estimated_rent or market_context.median_rent
    if property_detail.estimated_rent is None:
        assumptions.append("estimated_rent_defaulted_to_market_median")

    if not market_context.target_cap_rate:
        raise ValueError("Target cap rate must be non-zero.")

    annual_rent = rent_estimate * 12
    income_approach_value = annual_rent / market_context.target_cap_rate

    if active_listing:
        market_anchor_value = active_listing.list_price
        comparable_value = active_listing.list_price
        confidence = 0.55
    else:
        comparable_value = None
        market_anchor_value = 0.0
        confidence = 0.45

    if last_transaction and last_transaction.sale_price:
        market_anchor_value = last_transaction.sale_price * (
            1 + market_context.market_growth_rate
        )
        comparable_value = market_anchor_value
        confidence = 0.78
    elif latest_assessment:
        market_anchor_value = latest_assessment.assessed_total_value
        comparable_value = latest_assessment.assessed_total_value
        assumptions.append("market_anchor_defaulted_to_assessment")
    elif active_listing:
        assumptions.append("market_anchor_defaulted_to_list_price")
    else:
        raise ValueError("Listing or assessment anchor is required to build a valuation.")

    estimated_value = (
        MARKET_ANCHOR_WEIGHT * market_anchor_value
        + INCOME_ANCHOR_WEIGHT * income_approach_value
    )
    discount_to_value = (estimated_value - comparable_value) / estimated_value

    return ValuationResponse(
        estimated_value=round(estimated_value, 2),
        income_approach_value=round(income_approach_value, 2),
        market_anchor_value=round(market_anchor_value, 2),
        discount_to_value=round(discount_to_value, 4),
        confidence=round(confidence, 2),
        assumptions=assumptions,
    )
