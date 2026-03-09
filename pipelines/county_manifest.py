from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urljoin

from pipelines.county_pipeline import build_county_pipeline_plan


@dataclass(frozen=True)
class ManifestLink:
    href: str
    text: str


@dataclass(frozen=True)
class CountyDatasetCandidate:
    dataset_key: str
    label: str
    url: str
    matched_text: str


@dataclass(frozen=True)
class CountyManifestSnapshot:
    county: str
    source_url: str
    discovered_links: list[ManifestLink] = field(default_factory=list)
    dataset_candidates: list[CountyDatasetCandidate] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "county": self.county,
            "source_url": self.source_url,
            "discovered_links": [asdict(link) for link in self.discovered_links],
            "dataset_candidates": [asdict(candidate) for candidate in self.dataset_candidates],
        }


class _AnchorParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self._current_href: Optional[str] = None
        self._text_parts: list[str] = []
        self.links: list[ManifestLink] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._current_href = urljoin(self.base_url, href)
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self._current_href is None:
            return
        text = " ".join(part.strip() for part in self._text_parts if part.strip()).strip()
        self.links.append(ManifestLink(href=self._current_href, text=text))
        self._current_href = None
        self._text_parts = []


def extract_manifest_links(html: str, base_url: str) -> list[ManifestLink]:
    parser = _AnchorParser(base_url)
    parser.feed(html)
    return parser.links


def _classify_candidate(county: str, link: ManifestLink) -> Optional[CountyDatasetCandidate]:
    haystack = f"{link.text} {link.href}".lower()
    county_key = county.lower()

    if county_key == "hays":
        if "shapefile" in haystack or "gis" in haystack:
            return CountyDatasetCandidate("hays_gis_bundle", "Hays GIS shapefile", link.href, link.text)
        if "certified" in haystack:
            return CountyDatasetCandidate("hays_certified_export", "Hays certified export", link.href, link.text)
        if "property" in haystack and "export" in haystack:
            return CountyDatasetCandidate("hays_property_export", "Hays property export", link.href, link.text)

    if county_key == "travis":
        if "supplemental" in haystack:
            return CountyDatasetCandidate("travis_supplemental_export", "Travis supplemental export", link.href, link.text)
        if "certified" in haystack:
            return CountyDatasetCandidate("travis_certified_export", "Travis certified export", link.href, link.text)
        if "appraisal roll" in haystack or ("export" in haystack and "layout" not in haystack):
            return CountyDatasetCandidate("travis_current_export", "Travis appraisal roll/current export", link.href, link.text)

    if county_key == "williamson":
        if "historical" in haystack:
            return CountyDatasetCandidate("williamson_historical_export", "Williamson historical certified exports", link.href, link.text)
        if "gis" in haystack or "map" in haystack:
            return CountyDatasetCandidate("williamson_gis_bundle", "Williamson GIS downloads", link.href, link.text)
        if "preliminary" in haystack or "current" in haystack or "certified" in haystack:
            return CountyDatasetCandidate("williamson_current_export", "Williamson current/preliminary export", link.href, link.text)

    return None


def build_manifest_snapshot(
    county: str,
    html: str,
    source_url: Optional[str] = None,
) -> CountyManifestSnapshot:
    plan = build_county_pipeline_plan(county)
    if plan is None:
        raise ValueError(f"Unsupported county pipeline: {county}")

    resolved_source_url = source_url or plan.datasets[0].url
    links = extract_manifest_links(html, resolved_source_url)

    seen_dataset_keys: set[str] = set()
    candidates: list[CountyDatasetCandidate] = []
    for link in links:
        candidate = _classify_candidate(county, link)
        if candidate is None or candidate.dataset_key in seen_dataset_keys:
            continue
        candidates.append(candidate)
        seen_dataset_keys.add(candidate.dataset_key)

    return CountyManifestSnapshot(
        county=plan.county,
        source_url=resolved_source_url,
        discovered_links=links,
        dataset_candidates=candidates,
    )
