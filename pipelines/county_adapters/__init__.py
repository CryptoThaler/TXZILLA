from typing import Optional

from pipelines.county_adapters.base import CountyAdapter
from pipelines.county_adapters.bexar import BexarCountyAdapter
from pipelines.county_adapters.hays import HaysCountyAdapter
from pipelines.county_adapters.travis import TravisCountyAdapter
from pipelines.county_adapters.williamson import WilliamsonCountyAdapter


ADAPTERS: dict[str, CountyAdapter] = {
    "bexar": BexarCountyAdapter(),
    "hays": HaysCountyAdapter(),
    "travis": TravisCountyAdapter(),
    "williamson": WilliamsonCountyAdapter(),
}


def get_county_adapter(county: str) -> Optional[CountyAdapter]:
    return ADAPTERS.get(county.lower())


def list_county_adapters() -> list[CountyAdapter]:
    return [ADAPTERS[key] for key in sorted(ADAPTERS)]
