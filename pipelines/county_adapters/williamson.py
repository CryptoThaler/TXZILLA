from pipelines.county_adapters.base import (
    CountyAdapter,
    CountyAdapterSpec,
    CountyProcedureStep,
    CountySource,
)


class WilliamsonCountyAdapter(CountyAdapter):
    spec = CountyAdapterSpec(
        county="Williamson",
        display_name="Williamson Central Appraisal District",
        region_key="central_texas",
        bulk_sources=[
            CountySource(
                label="Williamson CAD data downloads",
                url="https://www.wcad.org/data-downloads/",
                access_method="bulk_http",
                format="txt_zip_gis",
                priority=1,
                notes="Preferred source for certified, preliminary, GIS, and historical data.",
            ),
            CountySource(
                label="Williamson CAD historical data",
                url="https://www.wcad.org/historical-data/",
                access_method="bulk_http",
                format="txt_zip",
                priority=2,
                notes="Use for backfills and longitudinal assessment history.",
            ),
        ],
        clerk_sources=[
            CountySource(
                label="Williamson County official public records",
                url="https://williamson.tx.publicsearch.us/",
                access_method="official_records",
                format="html",
                priority=1,
                notes="Use for deed / ownership history after parcel load.",
            )
        ],
        procedure=[
            CountyProcedureStep(1, "Download current and historical exports", "Use WCAD posted downloads before any interactive workflows.", "Bulk files are the primary input path."),
            CountyProcedureStep(2, "Build assessment time series", "Write certified/current records into assessment history.", "Preserve tax year slices separately."),
            CountyProcedureStep(3, "Exact parcel join", "Anchor by account / parcel id for canonical property creation.", "No silent address-only merges."),
            CountyProcedureStep(4, "Refresh deed ownership", "Backfill clerk ownership on a weekly cadence.", "Use clerk data only after property_id is fixed."),
        ],
        field_aliases={
            "source_record_id": ["acct", "account", "prop_id"],
            "parcel_number": ["acct", "account", "parcel", "parcel_id"],
            "address": ["property_address", "situs_address"],
            "postal_code": ["zip", "zipcode"],
            "owner_name": ["owner", "owner_name"],
            "mailing_address": ["mail_address", "mailing_address"],
            "assessed_total_value": ["market_value", "appraised_value", "total_value"],
            "tax_year": ["taxyear", "year"],
            "latitude": ["lat", "y"],
            "longitude": ["lon", "lng", "x"],
        },
    )
