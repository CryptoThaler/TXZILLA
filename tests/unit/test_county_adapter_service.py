from app.services.county_adapter_service import (
    get_county_pipeline_plan,
    get_supported_county,
    list_county_pipeline_plans,
    list_supported_counties,
)


def test_list_supported_counties_returns_first_four_adapters():
    counties = [adapter.county for adapter in list_supported_counties()]
    assert counties == ["Bexar", "Hays", "Travis", "Williamson"]


def test_bexar_adapter_contains_formalization_strategy():
    adapter = get_supported_county("bexar")
    assert adapter is not None
    assert adapter.required_exact_fields == ["parcel_number"]
    assert len(adapter.formalization_strategy) >= 3
    assert "public information request" in adapter.formalization_strategy[0].lower()


def test_ready_pipeline_plans_exist_for_hays_travis_and_williamson():
    plans = {plan.county: plan for plan in list_county_pipeline_plans()}

    assert plans["Hays"].readiness == "ready_now"
    assert plans["Travis"].readiness == "ready_now"
    assert plans["Williamson"].readiness == "ready_now"
    assert plans["Bexar"].readiness == "formalize_access"


def test_hays_pipeline_requires_layout_binding_and_exact_parcel_match():
    plan = get_county_pipeline_plan("hays")
    assert plan is not None
    primary_dataset = plan.datasets[0]
    assert primary_dataset.parser_profile.layout_binding_required is True
    assert primary_dataset.parser_profile.exact_match_fields == ["parcel_number"]
