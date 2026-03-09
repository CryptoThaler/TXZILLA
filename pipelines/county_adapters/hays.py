from pipelines.county_adapters.base import (
    CountyAdapter,
    CountyAdapterSpec,
    CountyProcedureStep,
    CountySource,
)


class HaysCountyAdapter(CountyAdapter):
    spec = CountyAdapterSpec(
        county="Hays",
        display_name="Hays Central Appraisal District",
        region_key="central_texas",
        bulk_sources=[
            CountySource(
                label="Hays CAD data downloads",
                url="https://hayscad.com/data-downloads/",
                access_method="bulk_http",
                format="txt_zip_shapefile",
                priority=1,
                notes="Preferred source for property exports, certified exports, and GIS shapefiles.",
            ),
            CountySource(
                label="Hays CAD property search",
                url="https://esearch.hayscad.com",
                access_method="interactive_search",
                format="html",
                priority=3,
                notes="Use only for spot validation or single-record recovery.",
            ),
        ],
        clerk_sources=[
            CountySource(
                label="Hays County Clerk records division",
                url="https://www.hayscountytx.gov/county-clerk/records-division",
                access_method="official_records",
                format="html",
                priority=1,
                notes="Use for ownership and deed backfill after CAD parcel anchoring.",
            )
        ],
        procedure=[
            CountyProcedureStep(1, "Fetch bulk export", "Pull latest posted property export and GIS bundle.", "Always prefer published bulk files over search pages."),
            CountyProcedureStep(2, "Validate file layout", "Bind parser to the posted export layout before ingest.", "Stop if layout version changes unexpectedly."),
            CountyProcedureStep(3, "Normalize by parcel", "Resolve `property_id` from county plus parcel number.", "Reject records with missing parcel numbers."),
            CountyProcedureStep(4, "Backfill clerk history", "Enrich ownership from county clerk after CAD load.", "Run only after parcel anchors are loaded."),
        ],
        field_aliases={
            "source_record_id": ["acct", "account", "prop_id"],
            "parcel_number": ["acct", "account", "parcelid", "geo_id"],
            "address": ["situs_address", "property_address"],
            "postal_code": ["zip", "zipcode"],
            "owner_name": ["owner", "owner1"],
            "mailing_address": ["mail_address", "mailingaddress"],
            "assessed_total_value": ["market_value", "appraised_value", "total_value"],
            "tax_year": ["year", "taxyear"],
            "latitude": ["lat", "y"],
            "longitude": ["lon", "lng", "x"],
        },
    )
