from app.services.market_service import MarketService
from app.services.property_service import PropertyService
from app.services.valuation_service import build_valuation


def test_build_valuation_is_deterministic_for_seed_property():
    property_detail = PropertyService().get_property_detail("prop-bexar-001")
    assert property_detail is not None

    market_context = MarketService().build_market_context(property_detail)
    valuation = build_valuation(property_detail, market_context)

    assert valuation.market_anchor_value == 343530.0
    assert valuation.income_approach_value == 470400.0
    assert valuation.estimated_value == 400621.5
    assert valuation.discount_to_value == 0.0889
