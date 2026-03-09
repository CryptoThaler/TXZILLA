import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx


@dataclass(frozen=True)
class DownloadArtifact:
    source_url: str
    local_path: str
    checksum_sha256: str
    media_type: Optional[str]
    bytes_downloaded: int


class CountyFetchClient:
    def fetch_text(self, url: str) -> str:
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text

    def download_bytes(self, url: str) -> tuple[bytes, Optional[str]]:
        with httpx.Client(follow_redirects=True, timeout=60.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.content, response.headers.get("content-type")


def write_download_artifact(
    county: str,
    dataset_key: str,
    source_url: str,
    payload: bytes,
    media_type: Optional[str],
    download_dir: str,
) -> DownloadArtifact:
    target_dir = Path(download_dir) / county.lower() / dataset_key
    target_dir.mkdir(parents=True, exist_ok=True)
    checksum = hashlib.sha256(payload).hexdigest()
    extension = ".bin"
    lowered_url = source_url.lower()
    if lowered_url.endswith(".zip"):
        extension = ".zip"
    elif lowered_url.endswith(".csv"):
        extension = ".csv"
    elif lowered_url.endswith(".txt"):
        extension = ".txt"
    target_path = target_dir / f"{checksum}{extension}"
    target_path.write_bytes(payload)
    return DownloadArtifact(
        source_url=source_url,
        local_path=str(target_path),
        checksum_sha256=checksum,
        media_type=media_type,
        bytes_downloaded=len(payload),
    )
