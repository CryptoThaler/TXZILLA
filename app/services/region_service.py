from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from app.schemas.region_schema import RegionResponse


REGIONS_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "regions.yaml"


@lru_cache(maxsize=1)
def _load_regions_config() -> dict:
    with REGIONS_CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def list_regions() -> list[RegionResponse]:
    config = _load_regions_config()
    return [
        RegionResponse(
            region_key=region_key,
            display_name=payload.get("display_name", region_key.replace("_", " ").title()),
            counties=payload.get("counties", []),
        )
        for region_key, payload in config.items()
    ]


def get_region(region_key: str) -> Optional[RegionResponse]:
    for region in list_regions():
        if region.region_key == region_key:
            return region
    return None


def resolve_region_for_county(county: str) -> Optional[str]:
    normalized_county = county.lower()
    for region in list_regions():
        if any(entry.lower() == normalized_county for entry in region.counties):
            return region.region_key
    return None
