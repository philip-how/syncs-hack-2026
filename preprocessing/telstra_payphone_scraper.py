"""
Telstra NSW payphone scraper
=============================

Telstra's "Find us" page (telstra.com.au/find-us?search=payphone) is a
client-side app. It calls a backend JSON API — found via the browser's
DevTools Network tab — instead of returning payphone data in the raw
HTML. This script calls that same API directly.

THE API (confirmed via DevTools):

    POST https://prod.okapi.ogw.evolve.okapi.telstra.com/tcom-ext/v1/geo/payphones/list
    Body: {"point": {"lat": ..., "lon": ...}, "radius": 10000,
           "pagination": {"size": 50, "from": 0}}

It searches around a single point with a radius (10000 = 10km) and
paginates results 50 at a time. To cover the whole of NSW we query it
once per NSW postcode, using each postcode's centroid as the search
point, and dedupe the results afterwards (adjacent postcodes overlap,
so the same payphone shows up in multiple queries).

SETUP — one manual step required:
Download australian_postcodes.csv from
https://github.com/matthewproctor/australianpostcodes
(the "Code" -> "Download ZIP" button, or grab the raw CSV) and place
it next to this script. It has ~17,000 rows with postcode/state/lat/long
columns for every Australian postcode.
"""

import csv
import time
import requests

PAYPHONES_URL = "https://prod.okapi.ogw.evolve.okapi.telstra.com/tcom-ext/v1/geo/payphones/list"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.telstra.com.au",
    "Referer": "https://www.telstra.com.au/",
    "Source": "tcom",  # custom header the gateway seems to need to route the request —
                       # without it every call 404s regardless of the body sent
}

POSTCODE_CSV_PATH = "nsw_postcodes.csv"  # from matthewproctor/australianpostcodes
SEARCH_RADIUS_METRES = 10000  # 10km — matches what the site itself uses
PAGE_SIZE = 50
REQUEST_DELAY_SECONDS = 0.3  # be polite — don't hammer their servers
OUTPUT_CSV_PATH = "nsw_payphones.csv"


def fetch_payphones_page(lat, lon, radius, size, from_):
    """One page of results for one search point."""
    body = {
        "point": {"lat": lat, "lon": lon},
        "radius": radius,
        "pagination": {"size": size, "from": from_},
    }
    # separate connect/read timeouts, so a silent network hang can't
    # outlast a slow-but-working request
    resp = requests.post(PAYPHONES_URL, json=body, headers=HEADERS, timeout=(5, 15))
    resp.raise_for_status()
    data = resp.json()
    try:
        value = data["results"][0]["value"][0]
    except (KeyError, IndexError, TypeError):
        return []
    return value.get("featureList", [])


MAX_PAGES_PER_POINT = 40  # hard safety cap — 40 x 50 = 2000 results is far
                           # more than one 10km radius should ever have; if
                           # this cap is being hit, the API isn't honouring
                           # the "from" offset and is just repeating pages


def fetch_all_payphones_near(lat, lon, radius=SEARCH_RADIUS_METRES, size=PAGE_SIZE, verbose=True):
    """Page through every result around one point until a short page is
    returned, an empty page is returned, the same page repeats, or the
    safety cap is hit — whichever comes first."""
    records = []
    from_ = 0
    last_ids = None
    for page_num in range(1, MAX_PAGES_PER_POINT + 1):
        if verbose:
            print(f"    fetching page {page_num} (from={from_})...", flush=True)
        page = fetch_payphones_page(lat, lon, radius, size, from_)
        if not page:
            break

        # guard against a backend that ignores "from" and just resends
        # the same nearest-N results every time
        this_ids = tuple(item.get("cabinet_id") for item in page)
        if this_ids == last_ids:
            if verbose:
                print("    (same page repeated — API isn't honouring pagination offset, stopping)")
            break
        last_ids = this_ids

        records.extend(page)
        if len(page) < size:
            break  # short page = last page
        from_ += size
        time.sleep(REQUEST_DELAY_SECONDS)
    else:
        if verbose:
            print(f"    hit the {MAX_PAGES_PER_POINT}-page safety cap — stopping this point")
    return records


def load_nsw_postcode_points(csv_path):
    """One (postcode, lat, lon) tuple per unique NSW postcode.

    NOTE: if matthewproctor/australianpostcodes changes its column
    names, adjust the keys below to match — open the CSV once and
    check its header row.
    """
    points, seen = [], set()
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("state") != "NSW":
                continue
            pc = row.get("postcode")
            if not pc or pc in seen:
                continue
            # Postcodes 1000-1999 are PO Boxes / large-volume mail receivers,
            # not physical locations — skip them, real NSW codes start at 2000.
            try:
                if int(pc) < 2000:
                    continue
                lat, lon = float(row["lat"]), float(row["long"])
            except (KeyError, ValueError):
                continue
            seen.add(pc)
            points.append((pc, lat, lon))
    return points


def main():
    points = load_nsw_postcode_points(POSTCODE_CSV_PATH)
    print(f"Querying {len(points)} NSW postcode centres (~{len(points)} requests minimum)...")

    seen = {}
    for i, (pc, lat, lon) in enumerate(points, 1):
        try:
            records = fetch_all_payphones_near(lat, lon)
        except requests.RequestException as e:
            print(f"  [!] postcode {pc}: request failed ({e})")
            continue

        for item in records:
            payphone_id = item.get("cabinet_id")
            if not payphone_id:
                continue
            phone_number = (item.get("fnn") or "").replace("PH:", "").strip()
            seen[payphone_id] = {
                "id": payphone_id,
                "phone_number": phone_number,
                "cli": item.get("cli", ""),
                "address": item.get("address", ""),
                "postcode": item.get("postcode", ""),
                "state": item.get("state", ""),
                "latitude": item.get("latitude", ""),
                "longitude": item.get("longitude", ""),
                "features": item.get("phone_attributes", ""),
            }

        if i % 25 == 0 or i == len(points):
            print(f"  {i}/{len(points)} postcodes done — {len(seen)} unique payphones so far")

        time.sleep(REQUEST_DELAY_SECONDS)

    fieldnames = ["id", "phone_number", "cli", "address", "postcode",
                  "state", "latitude", "longitude", "features"]
    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(seen.values())

    print(f"\nDone — saved {len(seen)} unique NSW payphones to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
