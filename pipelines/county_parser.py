import csv
import io
import zipfile
from pathlib import Path
from typing import Optional

from pipelines.county_adapters import get_county_adapter


class LayoutBindingError(ValueError):
    pass


def _extract_tabular_bytes(payload: bytes, source_url: str) -> bytes:
    lowered_url = source_url.lower()
    if lowered_url.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            members = [
                member
                for member in archive.namelist()
                if member.lower().endswith((".txt", ".csv"))
            ]
            if not members:
                raise LayoutBindingError("Zip archive contains no tabular text files.")
            members.sort(key=lambda name: (Path(name).suffix.lower() != ".txt", name))
            return archive.read(members[0])
    return payload


def _sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",|\t;")
    except csv.Error:
        return csv.excel


def parse_delimited_export(
    county: str,
    payload: bytes,
    source_url: str,
) -> list[dict]:
    adapter = get_county_adapter(county)
    if adapter is None:
        raise LayoutBindingError(f"Unsupported county parser: {county}")

    raw_bytes = _extract_tabular_bytes(payload, source_url)
    text = raw_bytes.decode("utf-8-sig")
    sample = text[:4096]
    dialect = _sniff_dialect(sample)
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)

    headers = [header.strip() for header in (reader.fieldnames or []) if header]
    if not headers:
        raise LayoutBindingError("No headers found in tabular export.")

    header_lookup = {header.lower(): header for header in headers}
    available_fields = set(headers)

    missing_bindings = []
    for field_name in adapter.spec.required_exact_fields:
        if field_name in available_fields:
            continue
        aliases = adapter.spec.field_aliases.get(field_name, [])
        if not any(alias.lower() in header_lookup for alias in aliases):
            missing_bindings.append(field_name)

    if missing_bindings:
        raise LayoutBindingError(
            f"{adapter.spec.county} export missing required layout bindings: "
            + ", ".join(missing_bindings)
        )

    rows: list[dict] = []
    for raw_row in reader:
        row = {
            key.strip(): (value or "").strip()
            for key, value in raw_row.items()
            if key
        }
        if not any(value for value in row.values()):
            continue
        rows.append(row)
    return rows
