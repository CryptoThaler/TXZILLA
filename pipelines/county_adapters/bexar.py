from pipelines.county_adapters.base import (
    CountyAdapter,
    CountyAdapterSpec,
    CountyProcedureStep,
    CountySource,
)


class BexarCountyAdapter(CountyAdapter):
    spec = CountyAdapterSpec(
        county="Bexar",
        display_name="Bexar Appraisal District",
        region_key="central_texas",
        bulk_sources=[
            CountySource(
                label="BCAD property search",
                url="https://esearch.bcad.org/",
                access_method="interactive_search",
                format="html",
                priority=3,
                notes="Operational source for parcel lookup and spot validation; not the preferred bulk pipeline.",
            ),
            CountySource(
                label="BCAD public information request form",
                url="https://bcad.org/wp-content/uploads/2025/08/Online-Public-Information-Request-Form-2025-08-01.pdf",
                access_method="public_information_request",
                format="pdf",
                priority=1,
                notes="Formal bulk path for appraisal exports and GIS when self-serve files are not posted.",
            ),
        ],
        clerk_sources=[
            CountySource(
                label="Bexar County official public records search",
                url="https://bexar.tx.publicsearch.us/",
                access_method="official_records",
                format="html",
                priority=1,
                notes="Use for ownership/deed validation after parcel data is anchored.",
            )
        ],
        procedure=[
            CountyProcedureStep(1, "Seek posted bulk path first", "Check BCAD for current public export or FTP availability before manual search use.", "Avoid HTML search scraping for production ingestion."),
            CountyProcedureStep(2, "Formalize public information request", "Request recurring appraisal export layout, appraisal data, and GIS data delivery.", "Needed if no self-serve bulk package is posted."),
            CountyProcedureStep(3, "Load parcel identifiers first", "Create canonical properties only from exact parcel/account matches.", "Address-only records stay out of auto-ingest."),
            CountyProcedureStep(4, "Cross-check with clerk", "Use county clerk records for ownership/deed history once parcel anchors exist.", "Do not infer sale events from search pages alone."),
        ],
        field_aliases={
            "source_record_id": ["acct", "account", "property_id", "prop_id"],
            "parcel_number": ["acct", "account", "parcel", "geo_id"],
            "address": ["property_address", "situs_address", "situs"],
            "postal_code": ["zip", "zipcode"],
            "owner_name": ["owner", "owner_name"],
            "mailing_address": ["mail_address", "mailing_address"],
            "assessed_total_value": ["market_value", "appraised_value", "total_value"],
            "tax_year": ["tax_year", "year"],
            "latitude": ["lat", "y"],
            "longitude": ["lon", "lng", "x"],
        },
        formalization_strategy=[
            "Contact BCAD through the public information request process and request recurring delivery of appraisal export data plus GIS layers for Bexar County.",
            "Ask BCAD to confirm whether current appraisal export and GIS files can be delivered through FTP or another repeatable bulk mechanism referenced in their public-information materials.",
            "Request the official export layout/version with every delivery so the parser can be bound deterministically.",
            "Use BCAD property search only for spot validation while the formal bulk channel is being established.",
            "Backfill ownership and deed history from the Bexar County clerk once parcel-level appraisal data is loaded.",
        ],
    )
