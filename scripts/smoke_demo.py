"""Smoke-test the TXZILLA API against a running instance.

Usage:
    python scripts/smoke_demo.py --base-url http://localhost:8000

The script exercises the main endpoints (health, search, property detail,
analysis, scoring, provider ingest) and exits non-zero on any failure.
"""

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

SEED_PROPERTY_ID = "prop-bexar-001"
SCORE_PAYLOAD = {
    "list_price": 365000,
    "estimated_rent": 2450,
    "taxes_monthly": 525,
    "insurance_monthly": 140,
    "maintenance_monthly": 170,
    "hoa_monthly": 55,
    "vacancy_reserve_monthly": 120,
    "management_cost_monthly": 180,
    "appreciation_score": 72,
    "market_growth_score": 69,
    "risk_inverse_score": 73.75,
    "liquidity_score": 64,
}


def _get(base_url: str, path: str) -> dict:
    url = f"{base_url}{path}"
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"  FAIL {exc.code} {url}\n  {body}", file=sys.stderr)
        raise


def _post(base_url: str, path: str, payload: dict) -> dict:
    url = f"{base_url}{path}"
    data = json.dumps(payload).encode()
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"  FAIL {exc.code} {url}\n  {body}", file=sys.stderr)
        raise


def run_demo(base_url: str) -> dict:
    results: dict = {}

    # 1. Health
    print("[1/6] GET /health")
    health = _get(base_url, "/health")
    assert health.get("status") in ("healthy", "degraded"), f"Unexpected health: {health}"
    results["health"] = "ok"

    # 2. Liveness
    print("[2/6] GET /live")
    live = _get(base_url, "/live")
    assert live.get("status") == "ok", f"Unexpected liveness: {live}"
    results["live"] = "ok"

    # 3. Search
    print("[3/6] GET /search")
    search = _get(base_url, "/search?limit=5")
    assert "items" in search, f"Missing items in search: {search}"
    assert search["total"] > 0, "Search returned zero results"
    results["search_total"] = search["total"]

    # 4. Property detail
    print(f"[4/6] GET /properties/{SEED_PROPERTY_ID}")
    prop = _get(base_url, f"/properties/{SEED_PROPERTY_ID}")
    assert prop.get("property_id") == SEED_PROPERTY_ID
    results["property_detail"] = "ok"

    # 5. Score
    print("[5/6] POST /score")
    score = _post(base_url, "/score", SCORE_PAYLOAD)
    assert "investment_score" in score, f"Missing investment_score: {score}"
    results["investment_score"] = score["investment_score"]

    # 6. Provider ingest (fixture)
    print("[6/6] POST /providers/ingest")
    fixture_path = FIXTURES_DIR / "provider_ingest.json"
    provider_payload = json.loads(fixture_path.read_text())
    ingest = _post(base_url, "/providers/ingest", provider_payload)
    assert ingest.get("run", {}).get("run_status") == "completed", f"Ingest failed: {ingest}"
    results["provider_ingest"] = "ok"
    results["canonical_properties_upserted"] = ingest.get("canonical_properties_upserted", 0)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="TXZILLA smoke test")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the running TXZILLA API (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    print(f"Smoke test targeting {args.base_url}\n")
    try:
        output = run_demo(args.base_url)
    except Exception as exc:
        print(f"\nSMOKE TEST FAILED: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\n--- Results ---")
    for key, value in output.items():
        print(f"  {key}: {value}")
    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
