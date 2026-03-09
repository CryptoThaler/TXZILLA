from app.services.region_service import get_region, resolve_region_for_county


def test_resolve_region_for_central_texas_county():
    assert resolve_region_for_county("Travis") == "central_texas"


def test_get_region_returns_display_name():
    region = get_region("central_texas")
    assert region is not None
    assert region.display_name == "Central Texas"
