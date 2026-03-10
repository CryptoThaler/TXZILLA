import argparse
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.repositories.provider_repository import ProviderRepository


def wait_for_live(base_url: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    last_error = None
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/live", timeout=5.0)
            if response.status_code == 200:
                return
            last_error = f"unexpected_status:{response.status_code}"
        except Exception as exc:  # pragma: no cover - network wait loop
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"API did not become live within {timeout_seconds}s: {last_error}")


def run_demo(base_url: str) -> dict:
    output: dict = {}

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        live = client.get("/live")
        ready = client.get("/ready")
        health = client.get("/health")

        provider_ingest = client.post(
            "/providers/ingest",
            json={
                "provider_name": "github_smoke_demo",
                "provider_type": "cad",
                "records": [
                    {
                        "county": "Travis",
                        "source_name": "tcad_smoke",
                        "acct": "TRV-SMOKE-001",
                        "situs": "500 Smoke Demo Ave",
                        "city": "Austin",
                        "lat": 30.2672,
                        "lon": -97.7431,
                        "owner": "Smoke Demo Owner LLC",
                        "market_value": 575000,
                        "year": 2025,
                        "source_observed_at": "2026-03-09T00:00:00Z",
                    }
                ],
            },
        )
        provider_payload = provider_ingest.json()
        run_id = provider_payload["run"]["provider_run_id"]

        ProviderRepository().store_run_artifact(
            provider_run_id=run_id,
            county="Travis",
            dataset_key="travis_current_export",
            source_url="https://traviscad.org/publicinformation/",
            local_path="/tmp/github-smoke-travis-export.zip",
            checksum_sha256="githubsmokedemo001",
            media_type="application/zip",
            bytes_downloaded=2048,
        )

        search = client.get("/search", params={"query": "500 Smoke Demo"})
        runs = client.get("/providers/runs")
        artifacts = client.get(
            "/providers/artifacts",
            params={"county": "Travis", "dataset_key": "travis_current_export"},
        )
        counties = client.get("/counties/pipelines")
        bexar = client.post("/counties/pipelines/bexar/run-sync", json={})

    output["live"] = {"status_code": live.status_code, "body": live.json()}
    output["ready"] = {"status_code": ready.status_code, "body": ready.json()}
    output["health"] = {"status_code": health.status_code, "body": health.json()}
    output["provider_ingest"] = {
        "status_code": provider_ingest.status_code,
        "body": provider_payload,
    }
    output["search"] = {"status_code": search.status_code, "body": search.json()}
    output["provider_runs"] = {"status_code": runs.status_code, "body": runs.json()}
    output["provider_artifacts"] = {
        "status_code": artifacts.status_code,
        "body": artifacts.json(),
    }
    output["counties"] = {"status_code": counties.status_code, "body": counties.json()}
    output["bexar_sync"] = {"status_code": bexar.status_code, "body": bexar.json()}

    if live.status_code != 200:
        raise RuntimeError("Smoke demo liveness check failed.")
    if ready.status_code != 200:
        raise RuntimeError("Smoke demo readiness check failed.")
    if provider_ingest.status_code != 200:
        raise RuntimeError("Smoke demo provider ingest failed.")
    if search.status_code != 200 or search.json().get("total", 0) < 1:
        raise RuntimeError("Smoke demo search did not return the ingested property.")
    if artifacts.status_code != 200 or not artifacts.json():
        raise RuntimeError("Smoke demo artifact audit did not return stored artifacts.")
    if bexar.status_code != 400:
        raise RuntimeError("Smoke demo expected Bexar sync to remain blocked.")

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TXZILLA smoke demo.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="artifacts/smoke-demo.json")
    parser.add_argument("--wait-seconds", type=int, default=60)
    args = parser.parse_args()

    wait_for_live(args.base_url, args.wait_seconds)
    output = run_demo(args.base_url)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
