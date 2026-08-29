#!/usr/bin/env python3
"""Export Australian Telstra payphones to CSV/JSON.

Sources:
  telstra - Telstra's first-party Find Us API (current/live)
  list    - Tasmania Government LIST mirror of Telstra payphone data

Examples:
  python scrape_telstra_payphones.py
  python scrape_telstra_payphones.py --state NSW
  python scrape_telstra_payphones.py --source list --state NSW
  python scrape_telstra_payphones.py --output telstra_payphones.csv --json telstra_payphones.json
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from typing import Any, Iterable

import requests

TELSTRA_URL = "https://tapi.telstra.com/v1/gcm-geoprocessing-service/telstra/payphones/list"
TELSTRA_LEGACY_URL = "https://tapi.telstra.com/presentation/v1/tcom/geo/payphones/list"
# Public client API key currently used by the Telstra locator scraper ecosystem.
# Override with TELSTRA_API_KEY if Telstra rotates it.
DEFAULT_TELSTRA_API_KEY = "tAqmM4O7ROFgWXYXiqAICbozH6UACU8K"
LIST_URL = "https://services.thelist.tas.gov.au/arcgis/rest/services/Public/Infrastructure/MapServer/74/query"

FIELDS = [
    "cabinet_id",
    "phone_number",
    "address",
    "locality",
    "state",
    "postcode",
    "latitude",
    "longitude",
    "fnn",
    "phone_attributes",
    "source",
]


def _text(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _phone(v: Any) -> str:
    """Preserve/restore Australian leading zero where source stores numbers numerically."""
    if v is None or v == "":
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    s = str(v).strip().replace(".0", "")
    digits = "".join(ch for ch in s if ch.isdigit())
    # LIST's PHONE_NU is numeric, so a 10-digit Australian number may arrive as 9 digits.
    if len(digits) == 9:
        digits = "0" + digits
    return digits or s


def normalize_telstra(p: dict[str, Any]) -> dict[str, Any]:
    return {
        "cabinet_id": _text(p.get("cabinet_id")),
        "phone_number": _phone(p.get("cli")),
        "address": _text(p.get("address")),
        "locality": _text(p.get("locality") or p.get("suburb")),
        "state": _text(p.get("state")),
        "postcode": _text(p.get("postcode")),
        "latitude": p.get("latitude", ""),
        "longitude": p.get("longitude", ""),
        "fnn": _text(p.get("fnn")),
        "phone_attributes": json.dumps(p.get("phone_attributes"), ensure_ascii=False) if p.get("phone_attributes") not in (None, "") else "",
        "source": "Telstra Find Us API",
    }


def _scrape_telstra_endpoint(
    session: requests.Session, url: str, headers: dict[str, str], *, legacy: bool, page_size: int = 100
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    offset = 0

    while True:
        payload: dict[str, Any] = {
            "point": {"lat": 0, "lon": 0},
            "pagination": {"size": page_size, "from": offset},
        }
        # The older Telstra endpoint expects/accepts a radius. A very large radius
        # makes the request behave as an Australia-wide paginated export.
        if legacy:
            payload["radius"] = 100000000000

        r = session.post(url, headers=headers, json=payload, timeout=45)
        r.raise_for_status()
        data = r.json()
        try:
            block = data["results"][0]["value"][0]
            features = block["featureList"]
            pagination = block.get("pagination", {})
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected Telstra API response: {json.dumps(data)[:1000]}") from exc

        if not features:
            break

        for p in features:
            row = normalize_telstra(p)
            key_tuple = (
                row["cabinet_id"], row["phone_number"],
                str(row["latitude"]), str(row["longitude"]),
            )
            if key_tuple not in seen:
                seen.add(key_tuple)
                rows.append(row)

        count = int(pagination.get("count", len(features)) or 0)
        size = int(pagination.get("size", page_size) or page_size)
        current_from = int(pagination.get("from", offset) or offset)
        print(f"Telstra: {len(rows):,} unique records", file=sys.stderr)

        if count < size:
            break
        offset = current_from + size
        time.sleep(0.05)

    return rows


def scrape_telstra(session: requests.Session, page_size: int = 100) -> list[dict[str, Any]]:
    key = os.environ.get("TELSTRA_API_KEY", DEFAULT_TELSTRA_API_KEY)
    common = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://www.telstra.com.au",
        "Referer": "https://www.telstra.com.au/",
        "User-Agent": "Mozilla/5.0 payphone-data-export/1.0",
    }
    modern_headers = {**common, "apikey": key}
    try:
        return _scrape_telstra_endpoint(session, TELSTRA_URL, modern_headers, legacy=False, page_size=page_size)
    except (requests.RequestException, RuntimeError) as exc:
        print(f"Modern Telstra endpoint failed ({exc}); trying legacy locator endpoint...", file=sys.stderr)
        legacy_headers = {**common, "source": "tcom"}
        return _scrape_telstra_endpoint(session, TELSTRA_LEGACY_URL, legacy_headers, legacy=True, page_size=page_size)


def normalize_list(a: dict[str, Any]) -> dict[str, Any]:
    return {
        "cabinet_id": _text(a.get("CAB_ID")),
        "phone_number": _phone(a.get("PHONE_NU")),
        "address": _text(a.get("ADDRESS")),
        "locality": _text(a.get("LOCALITY")),
        "state": _text(a.get("STATE")),
        "postcode": _text(int(a["POSTCODE"])) if isinstance(a.get("POSTCODE"), float) and a["POSTCODE"].is_integer() else _text(a.get("POSTCODE")),
        "latitude": a.get("LATITUDE", ""),
        "longitude": a.get("LONGITUDE", ""),
        "fnn": "",
        "phone_attributes": "",
        "source": "Tasmania Government LIST Telstra Payphones layer",
    }


def scrape_list(session: requests.Session, page_size: int = 2000) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        params = {
            "where": "1=1",
            "outFields": "OBJECTID,CAB_ID,ADDRESS,LOCALITY,STATE,POSTCODE,LONGITUDE,LATITUDE,PHONE_NU,UPDATED",
            "returnGeometry": "false",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "orderByFields": "OBJECTID",
            "f": "json",
        }
        r = session.get(LIST_URL, params=params, timeout=45)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"LIST API error: {data['error']}")
        features = data.get("features", [])
        rows.extend(normalize_list(f.get("attributes", {})) for f in features)
        print(f"LIST: {len(rows):,} records", file=sys.stderr)
        if len(features) < page_size:
            break
        offset += page_size
        time.sleep(0.05)
    return rows


def write_csv(path: str, rows: Iterable[dict[str, Any]]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Export Telstra payphones with IDs, phone numbers, addresses and coordinates.")
    ap.add_argument("--source", choices=["telstra", "list"], default="telstra",
                    help="Data source. telstra is live first-party; list is the government mirror.")
    ap.add_argument("--state", help="Optional state filter, e.g. NSW")
    ap.add_argument("--output", default="telstra_payphones.csv", help="Output CSV path")
    ap.add_argument("--json", dest="json_path", help="Optional JSON output path")
    args = ap.parse_args()

    with requests.Session() as session:
        rows = scrape_telstra(session) if args.source == "telstra" else scrape_list(session)

    if args.state:
        state = args.state.upper().strip()
        rows = [r for r in rows if str(r.get("state", "")).upper().strip() == state]

    rows.sort(key=lambda r: (str(r.get("state", "")), str(r.get("postcode", "")), str(r.get("locality", "")), str(r.get("cabinet_id", ""))))
    write_csv(args.output, rows)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    with_phone = sum(bool(r.get("phone_number")) for r in rows)
    print(f"Wrote {len(rows):,} payphones to {args.output}; {with_phone:,} have a phone number.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
