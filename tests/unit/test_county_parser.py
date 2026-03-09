import csv
import io
import zipfile

import pytest

from pipelines.county_parser import LayoutBindingError, parse_delimited_export


def _build_zip_payload(filename: str, rows: list[list[str]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(rows)
        archive.writestr(filename, csv_buffer.getvalue())
    return buffer.getvalue()


def test_parse_delimited_export_reads_hays_zip_and_trims_rows():
    payload = _build_zip_payload(
        "hays_export.csv",
        [
            ["acct", "property_address", "city", "lat", "lon", "owner", "market_value", "year"],
            [" HAY-001 ", " 100 River Rd ", "San Marcos", "29.88", "-97.94", "Owner LLC", "350000", "2025"],
        ],
    )

    rows = parse_delimited_export("hays", payload, "https://hayscad.com/files/hays_export.zip")

    assert rows == [
        {
            "acct": "HAY-001",
            "property_address": "100 River Rd",
            "city": "San Marcos",
            "lat": "29.88",
            "lon": "-97.94",
            "owner": "Owner LLC",
            "market_value": "350000",
            "year": "2025",
        }
    ]


def test_parse_delimited_export_rejects_missing_required_layout_bindings():
    payload = _build_zip_payload(
        "travis_export.csv",
        [
            ["owner", "city", "market_value"],
            ["Owner LLC", "Austin", "425000"],
        ],
    )

    with pytest.raises(LayoutBindingError, match="missing required layout bindings"):
        parse_delimited_export(
            "travis",
            payload,
            "https://traviscad.org/exports/travis_export.zip",
        )
