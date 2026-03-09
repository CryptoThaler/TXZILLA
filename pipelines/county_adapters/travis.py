from pipelines.county_adapters.base import (
    CountyAdapter,
    CountyAdapterSpec,
    CountyProcedureStep,
    CountySource,
)


class TravisCountyAdapter(CountyAdapter):
    spec = CountyAdapterSpec(
        county="Travis",
        display_name="Travis Central Appraisal District",
        region_key="central_texas",
        bulk_sources=[
            CountySource(
                label="Travis CAD public information exports",
                url="https://traviscad.org/publicinformation/",
                access_method="bulk_http",
                format="txt_zip",
                priority=1,
                notes="Preferred source for appraisal roll, certified exports, and file layouts.",
            ),
            CountySource(
                label="Travis CAD property search",
                url="https://traviscad.org/propertysearch/",
                access_method="interactive_search",
                format="html",
                priority=3,
                notes="Use for parcel spot checks only.",
            ),
        ],
        clerk_sources=[
            CountySource(
                label="Travis County Clerk real property records",
                url="https://countyclerk.traviscountytx.gov/departments/recording/real-property/",
                access_method="official_records",
                format="html",
                priority=1,
                notes="Use for deed and ownership validation after CAD ingestion.",
            )
        ],
        procedure=[
            CountyProcedureStep(1, "Load export manifest", "Read latest appraisal/public information export set.", "Prefer certified or current export over search pages."),
            CountyProcedureStep(2, "Parse posted layout", "Lock parser to published layout docs.", "Block ingest if unrecognized column set appears."),
            CountyProcedureStep(3, "Anchor by parcel", "Use account/parcel id as the exact identifier.", "Address-only matches go to review."),
            CountyProcedureStep(4, "Overlay clerk data", "Join deed history after canonical parcel load.", "Never replace parcel anchors with clerk-only address matches."),
        ],
        field_aliases={
            "source_record_id": ["acct", "account", "prop_id"],
            "parcel_number": ["acct", "account", "geo_id", "parcel"],
            "address": ["situs", "situs_address"],
            "postal_code": ["zip", "zipcode"],
            "owner_name": ["owner", "owner_name"],
            "mailing_address": ["mail_address", "mailing_address"],
            "assessed_total_value": ["market_value", "total_value", "appraised_value"],
            "tax_year": ["tax_year", "year"],
            "latitude": ["lat", "y"],
            "longitude": ["lon", "lng", "x"],
        },
    )
