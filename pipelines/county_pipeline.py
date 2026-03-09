from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from pipelines.county_adapters import get_county_adapter


@dataclass(frozen=True)
class ParserProfile:
    parser_kind: str
    archive_format: str
    geometry_expected: bool
    layout_binding_required: bool
    exact_match_fields: list[str] = field(default_factory=list)
    review_trigger_fields: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DatasetManifest:
    dataset_key: str
    label: str
    county: str
    url: str
    cadence: str
    priority: int
    parser_profile: ParserProfile
    purpose: str
    status: str
    notes: str


@dataclass(frozen=True)
class CountyPipelinePlan:
    county: str
    display_name: str
    region_key: str
    readiness: str
    fastest_path: str
    accuracy_controls: list[str] = field(default_factory=list)
    datasets: list[DatasetManifest] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "county": self.county,
            "display_name": self.display_name,
            "region_key": self.region_key,
            "readiness": self.readiness,
            "fastest_path": self.fastest_path,
            "accuracy_controls": self.accuracy_controls,
            "datasets": [
                {
                    **asdict(dataset),
                    "parser_profile": asdict(dataset.parser_profile),
                }
                for dataset in self.datasets
            ],
            "next_actions": self.next_actions,
        }


def _bulk_txt_profile() -> ParserProfile:
    return ParserProfile(
        parser_kind="bulk_export_layout",
        archive_format="zip_or_txt",
        geometry_expected=False,
        layout_binding_required=True,
        exact_match_fields=["parcel_number"],
        review_trigger_fields=["address"],
    )


def _gis_profile() -> ParserProfile:
    return ParserProfile(
        parser_kind="gis_shapefile_bundle",
        archive_format="zip_shapefile",
        geometry_expected=True,
        layout_binding_required=False,
        exact_match_fields=["parcel_number"],
        review_trigger_fields=[],
    )


def build_county_pipeline_plan(county: str) -> Optional[CountyPipelinePlan]:
    adapter = get_county_adapter(county)
    if adapter is None:
        return None

    spec = adapter.spec
    county_key = spec.county.lower()

    if county_key == "hays":
        return CountyPipelinePlan(
            county=spec.county,
            display_name=spec.display_name,
            region_key=spec.region_key,
            readiness="ready_now",
            fastest_path="Use Hays CAD data downloads for bulk exports and GIS, then enrich ownership from the county clerk.",
            accuracy_controls=[
                "Bind parser to the posted Hays export layout before ingest.",
                "Require exact parcel/account id for canonical property creation.",
                "Use GIS bundle only to enrich geometry after parcel load.",
            ],
            datasets=[
                DatasetManifest(
                    dataset_key="hays_property_export",
                    label="Hays property export",
                    county=spec.county,
                    url="https://hayscad.com/data-downloads/",
                    cadence="daily",
                    priority=1,
                    parser_profile=_bulk_txt_profile(),
                    purpose="canonical properties plus assessment history",
                    status="implement_now",
                    notes="Primary input for current property facts and values.",
                ),
                DatasetManifest(
                    dataset_key="hays_certified_export",
                    label="Hays certified export",
                    county=spec.county,
                    url="https://hayscad.com/data-downloads/",
                    cadence="annual",
                    priority=2,
                    parser_profile=_bulk_txt_profile(),
                    purpose="certified annual baseline snapshot",
                    status="implement_now",
                    notes="Lock annual certified appraisal roll separately from current export.",
                ),
                DatasetManifest(
                    dataset_key="hays_gis_bundle",
                    label="Hays GIS shapefile",
                    county=spec.county,
                    url="https://hayscad.com/data-downloads/",
                    cadence="weekly",
                    priority=3,
                    parser_profile=_gis_profile(),
                    purpose="parcel geometry enrichment",
                    status="implement_now",
                    notes="Apply after exact parcel match; never geometry-match without parcel key.",
                ),
            ],
            next_actions=[
                "Implement Hays export manifest fetcher.",
                "Bind parser to posted property export layout.",
                "Write GIS parcel geometry enrichment pass.",
            ],
        )

    if county_key == "travis":
        return CountyPipelinePlan(
            county=spec.county,
            display_name=spec.display_name,
            region_key=spec.region_key,
            readiness="ready_now",
            fastest_path="Use TCAD public-information exports and published layouts as the primary bulk input, then join clerk records for ownership.",
            accuracy_controls=[
                "Do not ingest unrecognized TCAD layouts.",
                "Anchor every property on account/parcel id.",
                "Keep supplemental and certified exports as separate freshness slices.",
            ],
            datasets=[
                DatasetManifest(
                    dataset_key="travis_current_export",
                    label="Travis appraisal roll/current export",
                    county=spec.county,
                    url="https://traviscad.org/publicinformation/",
                    cadence="daily",
                    priority=1,
                    parser_profile=_bulk_txt_profile(),
                    purpose="canonical properties and current values",
                    status="implement_now",
                    notes="Primary dataset for current parcel facts and market values.",
                ),
                DatasetManifest(
                    dataset_key="travis_certified_export",
                    label="Travis certified export",
                    county=spec.county,
                    url="https://traviscad.org/publicinformation/",
                    cadence="annual",
                    priority=2,
                    parser_profile=_bulk_txt_profile(),
                    purpose="annual certified baseline",
                    status="implement_now",
                    notes="Use to establish annual property and assessment snapshots.",
                ),
                DatasetManifest(
                    dataset_key="travis_supplemental_export",
                    label="Travis supplemental export",
                    county=spec.county,
                    url="https://traviscad.org/publicinformation/",
                    cadence="weekly",
                    priority=3,
                    parser_profile=_bulk_txt_profile(),
                    purpose="delta updates and supplement tracking",
                    status="implement_now",
                    notes="Store as a separate run class to preserve freshness.",
                ),
            ],
            next_actions=[
                "Implement TCAD export manifest discovery.",
                "Version file-layout bindings for TCAD public information exports.",
                "Add supplemental-export delta ingestion path.",
            ],
        )

    if county_key == "williamson":
        return CountyPipelinePlan(
            county=spec.county,
            display_name=spec.display_name,
            region_key=spec.region_key,
            readiness="ready_now",
            fastest_path="Use WCAD data downloads for current files and historical downloads for time-series backfill.",
            accuracy_controls=[
                "Separate current/preliminary from historical certified files.",
                "Preserve tax-year slices in assessment history.",
                "Require exact parcel/account id before ownership enrichment.",
            ],
            datasets=[
                DatasetManifest(
                    dataset_key="williamson_current_export",
                    label="Williamson current/preliminary export",
                    county=spec.county,
                    url="https://www.wcad.org/data-downloads/",
                    cadence="daily",
                    priority=1,
                    parser_profile=_bulk_txt_profile(),
                    purpose="current canonical property state",
                    status="implement_now",
                    notes="Primary current-state appraisal input.",
                ),
                DatasetManifest(
                    dataset_key="williamson_historical_export",
                    label="Williamson historical certified exports",
                    county=spec.county,
                    url="https://www.wcad.org/historical-data/",
                    cadence="manual_backfill",
                    priority=2,
                    parser_profile=_bulk_txt_profile(),
                    purpose="historical assessment backfill",
                    status="implement_now",
                    notes="Use to build longitudinal assessment history.",
                ),
                DatasetManifest(
                    dataset_key="williamson_gis_bundle",
                    label="Williamson GIS downloads",
                    county=spec.county,
                    url="https://www.wcad.org/data-downloads/",
                    cadence="weekly",
                    priority=3,
                    parser_profile=_gis_profile(),
                    purpose="parcel geometry enrichment",
                    status="implement_now",
                    notes="Apply post-parcel-anchor only.",
                ),
            ],
            next_actions=[
                "Implement WCAD current download manifest parser.",
                "Add historical backfill runner for certified years.",
                "Add GIS enrichment path keyed by parcel/account id.",
            ],
        )

    if county_key == "bexar":
        return CountyPipelinePlan(
            county=spec.county,
            display_name=spec.display_name,
            region_key=spec.region_key,
            readiness="formalize_access",
            fastest_path="Formalize recurring BCAD bulk export delivery before implementing automated production ingest.",
            accuracy_controls=[
                "Do not treat BCAD interactive search as the production bulk pipeline.",
                "Require official export layout/version with every delivery.",
                "Anchor on parcel/account id before clerk enrichment.",
            ],
            datasets=[
                DatasetManifest(
                    dataset_key="bexar_requested_export",
                    label="BCAD requested appraisal export",
                    county=spec.county,
                    url="https://bcad.org/wp-content/uploads/2025/08/Online-Public-Information-Request-Form-2025-08-01.pdf",
                    cadence="pending_formalization",
                    priority=1,
                    parser_profile=_bulk_txt_profile(),
                    purpose="canonical properties and assessment history",
                    status="blocked_pending_access",
                    notes="Formal public-information request required.",
                )
            ],
            next_actions=spec.formalization_strategy,
        )

    return None


def list_priority_county_pipeline_plans() -> list[CountyPipelinePlan]:
    counties = ("hays", "travis", "williamson", "bexar")
    plans = [build_county_pipeline_plan(county) for county in counties]
    return [plan for plan in plans if plan is not None]
