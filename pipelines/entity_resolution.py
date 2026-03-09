AUTO_MATCH_THRESHOLD = 0.85
REVIEW_THRESHOLD = 0.70


def resolve_property_match(property_record: dict, listing_record: dict) -> dict:
    property_parcel = property_record.get("parcel_number")
    listing_parcel = listing_record.get("parcel_number")

    if (
        property_parcel
        and listing_parcel
        and property_record["county"].lower() == listing_record["county"].lower()
        and property_parcel == listing_parcel
    ):
        return {
            "match_status": "matched",
            "confidence": 1.0,
            "property_id": property_record.get("property_id"),
            "reason": "exact_parcel_match",
        }

    property_address = property_record["address_line1"].lower()
    listing_address = listing_record["address_line1"].lower()
    if (
        property_record["county"].lower() == listing_record["county"].lower()
        and property_address == listing_address
    ):
        return {
            "match_status": "review",
            "confidence": 0.78,
            "property_id": property_record.get("property_id"),
            "reason": "address_match_below_auto_threshold",
        }

    return {
        "match_status": "unmatched",
        "confidence": 0.0,
        "property_id": None,
        "reason": "no_deterministic_match",
    }


def resolve_entities(property_records: list[dict], listing_record: dict) -> dict:
    best_match = {
        "match_status": "unmatched",
        "confidence": 0.0,
        "property_id": None,
        "reason": "no_deterministic_match",
    }

    for property_record in property_records:
        candidate = resolve_property_match(property_record, listing_record)
        if candidate["confidence"] > best_match["confidence"]:
            best_match = candidate

    if REVIEW_THRESHOLD <= best_match["confidence"] < AUTO_MATCH_THRESHOLD:
        best_match["match_status"] = "review"

    return best_match
