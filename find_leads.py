#!/usr/bin/env python3
"""
find_leads.py — Local Business Lead Finder v2
Finds businesses without a website listed on Google Maps.
Outputs results to a CSV, appending and deduplicating on every run.

WHY THE GRID:
    Google Nearby Search returns max 20 results per call, regardless of radius.
    A larger radius doesn't give more results — it just shifts which 20 Google
    picks. To get full coverage, we split the area into a grid of smaller
    overlapping circles and search each one, then deduplicate by place_id.

Requirements:
    pip install requests openpyxl

Get a free Google API key:
    1. Go to https://console.cloud.google.com/
    2. Create a project → Enable "Places API (New)" + "Geocoding API"
    3. APIs & Services → Credentials → Create API Key
    4. You get $200/month free credit — enough for thousands of searches.

Usage examples:
    # City-level sweep (auto grid, ~dozens of API calls)
    python find_leads.py --api-key KEY --city "Kayseri" --radius 10000

    # Specific mahalle (right-click Google Maps → "What's here?" to get coords)
    python find_leads.py --api-key KEY --lat 38.7312 --lng 35.4787 --radius 800

    # Filter by type and quality
    python find_leads.py --api-key KEY --city "Kayseri" --radius 10000 --type restaurant --min-rating 4.0 --min-reviews 20

    # Save to a separate file per city
    python find_leads.py --api-key KEY --city "Istanbul" --radius 15000 --output istanbul_leads.csv

    # Smaller sub-radius = denser grid = more results (more API calls)
    python find_leads.py --api-key KEY --city "Kayseri" --radius 10000 --sub-radius 500

NOTES:
    - Geocoding "Kayseri Melikgazi" returns the same center as "Kayseri".
      For specific districts, use --lat/--lng with coordinates from Google Maps.
    - Max radius is 50000m (Google hard limit). Script clamps automatically.
    - Each run appends to the CSV and skips already-seen place_ids.
"""

import argparse
import csv
import math
import os
import sys
import time
import requests
from datetime import datetime

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
MAX_RADIUS = 50000  # Google hard limit

FIELD_MASK = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.internationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.types",
    "places.googleMapsUri",
    "places.businessStatus",
])

TYPE_ALIASES = {
    "restaurant": "restaurant",
    "cafe": "cafe",
    "barber": "barber",
    "hair": "hair_salon",
    "salon": "beauty_salon",
    "dentist": "dentist",
    "doctor": "doctor",
    "pharmacy": "pharmacy",
    "gym": "gym",
    "hotel": "lodging",
    "market": "supermarket",
    "bakery": "bakery",
    "auto": "car_repair",
    "realestate": "real_estate_agency",
    "lawyer": "lawyer",
    "accountant": "accounting",
    "shop": "store",
    "school": "school",
}


def geocode(api_key: str, city_name: str) -> tuple[float, float]:
    resp = requests.get(GEOCODE_URL, params={"address": city_name, "key": api_key}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise ValueError(f"Could not geocode '{city_name}'. Try a more specific name or use --lat/--lng.")
    loc = results[0]["geometry"]["location"]
    return loc["lat"], loc["lng"]


def generate_grid(center_lat: float, center_lng: float, total_radius_m: int, sub_radius_m: int) -> list[tuple[float, float]]:
    """
    Generate overlapping circle centers covering the total area.
    Step = sub_radius * 1.5 so adjacent circles overlap by ~33%, avoiding gaps.
    """
    lat_per_m = 1.0 / 111320.0
    lng_per_m = 1.0 / (111320.0 * math.cos(math.radians(center_lat)))

    step_m = sub_radius_m * 1.5
    lat_step = step_m * lat_per_m
    lng_step = step_m * lng_per_m

    n = math.ceil(total_radius_m / step_m) + 1
    centers = []

    for i in range(-n, n + 1):
        for j in range(-n, n + 1):
            clat = center_lat + i * lat_step
            clng = center_lng + j * lng_step
            dist_m = math.sqrt(
                ((clat - center_lat) / lat_per_m) ** 2 +
                ((clng - center_lng) / lng_per_m) ** 2
            )
            if dist_m <= total_radius_m:
                centers.append((clat, clng))

    return centers


def nearby_search(api_key: str, lat: float, lng: float, radius: int, business_type: str | None) -> list[dict]:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body: dict = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": float(radius),
            }
        },
        "maxResultCount": 20,
    }
    if business_type:
        resolved = TYPE_ALIASES.get(business_type.lower(), business_type.lower())
        body["includedTypes"] = [resolved]

    resp = requests.post(PLACES_SEARCH_URL, json=body, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json().get("places", [])


def load_existing_ids(csv_path: str) -> set[str]:
    if not os.path.exists(csv_path):
        return set()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["place_id"] for row in reader if "place_id" in row}


FIELDNAMES = ["place_id", "name", "category", "phone", "address", "rating", "reviews", "google_maps_url", "found_date"]


def append_results(csv_path: str, businesses: list[dict], existing_ids: set[str]) -> int:
    file_exists = os.path.exists(csv_path)
    new_count = 0
    today = datetime.now().strftime("%Y-%m-%d")

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()

        for b in businesses:
            place_id = b.get("id", "")
            if not place_id or place_id in existing_ids:
                continue
            types = b.get("types", [])
            writer.writerow({
                "place_id": place_id,
                "name": b.get("displayName", {}).get("text", ""),
                "category": types[0] if types else "unknown",
                "phone": b.get("internationalPhoneNumber", ""),
                "address": b.get("formattedAddress", ""),
                "rating": b.get("rating", ""),
                "reviews": b.get("userRatingCount", ""),
                "google_maps_url": b.get("googleMapsUri", ""),
                "found_date": today,
            })
            existing_ids.add(place_id)
            new_count += 1

    return new_count


def apply_filters(places: list[dict], min_rating: float | None, min_reviews: int | None) -> list[dict]:
    result = [p for p in places if p.get("businessStatus") != "CLOSED_PERMANENTLY"]
    result = [p for p in result if not p.get("websiteUri")]
    result = [p for p in result if p.get("internationalPhoneNumber")]
    if min_rating:
        result = [p for p in result if (p.get("rating") or 0) >= min_rating]
    if min_reviews:
        result = [p for p in result if (p.get("userRatingCount") or 0) >= min_reviews]
    return result


def save_excel(csv_path: str) -> str | None:
    """Regenerate an Excel file from the current CSV. Returns the Excel path or None."""
    if not EXCEL_AVAILABLE or not os.path.exists(csv_path):
        return None

    excel_path = os.path.splitext(csv_path)[0] + ".xlsx"

    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A5F", end_color="1E3A5F", fill_type="solid")

    for col_idx, value in enumerate(rows[0], 1):
        cell = ws.cell(row=1, column=col_idx, value=value.upper().replace("_", " "))
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for row_idx, row in enumerate(rows[1:], 2):
        for col_idx, value in enumerate(row, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    ws.freeze_panes = "A2"

    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 3, 55)

    wb.save(excel_path)
    return excel_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find local businesses without a website (Google Places API)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    loc = parser.add_mutually_exclusive_group(required=True)
    loc.add_argument("--city", metavar="NAME",
                     help="City name to geocode. For specific districts use --lat/--lng instead.")
    loc.add_argument("--lat", type=float, metavar="LAT", help="Latitude (pair with --lng)")

    parser.add_argument("--lng", type=float, metavar="LNG")
    parser.add_argument("--radius", type=int, default=3000, metavar="METERS",
                        help="Total search area radius in meters, max 50000 (default: 3000)")
    parser.add_argument("--sub-radius", type=int, default=1000, metavar="METERS",
                        help="Radius of each grid cell (default: 1000). "
                             "Smaller = denser grid = more results + more API calls.")
    parser.add_argument("--type", dest="business_type", metavar="TYPE",
                        help=f"Business type. Shortcuts: {', '.join(TYPE_ALIASES.keys())}")
    parser.add_argument("--min-rating", type=float, metavar="N")
    parser.add_argument("--min-reviews", type=int, metavar="N")
    parser.add_argument("--output", default="leads.csv", metavar="FILE",
                        help="Output CSV (default: leads.csv). Appends on each run.")
    parser.add_argument("--api-key", required=True, metavar="KEY")

    args = parser.parse_args()

    # Clamp radius
    if args.radius > MAX_RADIUS:
        print(f"Warning: radius clamped from {args.radius}m to {MAX_RADIUS}m (Google limit).")
        args.radius = MAX_RADIUS

    if args.sub_radius > args.radius:
        args.sub_radius = args.radius

    # Resolve center
    if args.city:
        print(f"Geocoding '{args.city}'...")
        try:
            lat, lng = geocode(args.api_key, args.city)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"  → {lat:.5f}, {lng:.5f}")
        print(f"  Tip: for a specific district, right-click that spot on Google Maps")
        print(f"  and use --lat/--lng with those coordinates instead.")
    else:
        if args.lng is None:
            parser.error("--lng is required when using --lat")
        lat, lng = args.lat, args.lng

    # Build grid
    centers = generate_grid(lat, lng, args.radius, args.sub_radius)
    estimated_cost = len(centers) * 0.032
    print(f"\nGrid: {len(centers)} search points × {args.sub_radius}m sub-radius covering {args.radius}m total")
    print(f"Estimated API cost: ${estimated_cost:.3f} (from your $200/mo free credit)")

    # Search all grid cells
    all_places: dict[str, dict] = {}
    errors = 0

    print()
    for idx, (clat, clng) in enumerate(centers, 1):
        print(f"  [{idx:3d}/{len(centers)}] {clat:.4f},{clng:.4f} ...", end=" ", flush=True)
        try:
            places = nearby_search(args.api_key, clat, clng, args.sub_radius, args.business_type)
            before = len(all_places)
            for p in places:
                pid = p.get("id")
                if pid:
                    all_places[pid] = p
            new_unique = len(all_places) - before
            print(f"{len(places)} results, {new_unique} new unique")
        except requests.HTTPError as e:
            print(f"HTTP {e.response.status_code} — skipped")
            errors += 1
        except Exception as e:
            print(f"Error: {e} — skipped")
            errors += 1
        time.sleep(0.25)

    print(f"\nTotal unique businesses collected: {len(all_places)}")
    if errors:
        print(f"  ({errors} grid cells had errors and were skipped)")

    # Filter
    all_list = list(all_places.values())
    no_website = [p for p in all_list if p.get("businessStatus") != "CLOSED_PERMANENTLY" and not p.get("websiteUri")]
    filtered = apply_filters(all_list, args.min_rating, args.min_reviews)

    print(f"  → {len(no_website)} without a website")
    print(f"  → {len(filtered)} without a website AND with a phone number", end="")
    if args.min_rating or args.min_reviews:
        print(f" (after rating/review filters)", end="")
    print()

    if not filtered:
        print("\nNo leads found. Try loosening filters or expanding the area.")
        return

    # Preview
    print("\nPreview (first 5):")
    print("─" * 60)
    for b in filtered[:5]:
        name = b.get("displayName", {}).get("text", "Unknown")
        phone = b.get("internationalPhoneNumber", "no phone")
        rating = b.get("rating", "–")
        reviews = b.get("userRatingCount", 0)
        address = b.get("formattedAddress", "")
        print(f"  {name}")
        print(f"  📞 {phone}   ⭐ {rating} ({reviews} reviews)")
        print(f"  📍 {address}")
        print()

    # Save
    existing_ids = load_existing_ids(args.output)
    before = len(existing_ids)
    new_count = append_results(args.output, filtered, existing_ids)

    print(f"✓ {new_count} new leads added to '{args.output}'")
    print(f"  Total records in file: {len(existing_ids)} (was {before})")

    excel_path = save_excel(args.output)
    if excel_path:
        print(f"  Excel updated: '{excel_path}'")
    elif not EXCEL_AVAILABLE:
        print("  Tip: run 'pip install openpyxl' to also get an Excel file.")


if __name__ == "__main__":
    main()
