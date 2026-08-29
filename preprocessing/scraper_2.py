"""
Telstra NSW payphone scraper — starter template
=================================================

Telstra's "Find us" page (telstra.com.au/find-us?search=payphone) renders
its results client-side: the raw HTML has no payphone data in it. The
page's JavaScript calls a backend JSON API after load and injects the
results. So this script calls that same API directly instead of trying
to scrape rendered HTML.

WHAT YOU NEED TO FILL IN (marked TODO below):
Use your browser's DevTools (Network tab, filter to Fetch/XHR) on the
find-us page to find the actual API call, then copy its URL, method,
query params, and field names here. See the step-by-step walkthrough
in the chat for how to find it.

Once filled in, this handles the parts that are the same regardless of
the exact API: tiling searches across NSW, deduplicating by payphone
ID, being polite to Telstra's servers, and writing a clean CSV.
"""

import csv
import time
import requests

# --- TODO: fill these in after inspecting DevTools ---
API_URL = "https://www.telstra.com.au/REPLACE/WITH/REAL/ENDPOINT"
HTTP_METHOD = "GET"  # or "POST" — check what DevTools shows

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
    # Add any other headers DevTools shows as required (e.g. a referer,
    # an API key header, or a session cookie) — copy them exactly.
}

# NSW postcodes to search around. This is a small example — get the
# full NSW postcode list from a source like the Australia Post postcode
# file, or data.gov.au's "Australian Postcodes" dataset, and paste it in.
# The right radius/spacing depends on what the API itself supports.
NSW_POSTCODES = [
    "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070",
    "2080", "2090", "2100", "2110", "2120", "2130", "2140", "2150",
    # ... add the rest of NSW's ~600 postcodes here
]

REQUEST_DELAY_SECONDS = 0.5  # be polite — don't hammer their servers


def fetch_payphones_near(postcode: str) -> list[dict]:
    """Call the locator API for one postcode and return raw result records."""
    params = {
        "search": postcode,
        # TODO: add/rename params to match what DevTools actually shows,
        # e.g. "type": "payphone", "radius": 10, "state": "NSW"
    }

    if HTTP_METHOD == "GET":
        resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    else:
        resp = requests.post(API_URL, json=params, headers=HEADERS, timeout=15)

    resp.raise_for_status()
    data = resp.json()

    # TODO: adjust this to match the real JSON shape — this assumes
    # something like {"results": [...]} or {"locations": [...]}.
    return data.get("results", [])


def main():
    seen: dict[str, dict] = {}

    for postcode in NSW_POSTCODES:
        try:
            records = fetch_payphones_near(postcode)
        except requests.RequestException as e:
            print(f"  [!] failed for {postcode}: {e}")
            continue

        for item in records:
            # TODO: rename these keys to match the real field names.
            payphone_id = item.get("id")
            if not payphone_id:
                continue
            seen[payphone_id] = {
                "id": payphone_id,
                "phone_number": item.get("phoneNumber") or item.get("msisdn"),
                "address": item.get("address") or item.get("formattedAddress"),
            }

        print(f"  {postcode}: {len(records)} results, {len(seen)} unique so far")
        time.sleep(REQUEST_DELAY_SECONDS)

    out_path = "nsw_payphones.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "phone_number", "address"])
        writer.writeheader()
        writer.writerows(seen.values())

    print(f"\nDone — saved {len(seen)} unique NSW payphones to {out_path}")


if __name__ == "__main__":
    main()