"""Refresh the public event snapshot from start.gg (run by GitHub Actions)."""

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

API_URL = "https://api.start.gg/gql/alpha"
OUTPUT = Path(__file__).with_name("events.json")
QUERY = """
query CanterburyTournaments($page: Int!, $perPage: Int!, $coordinates: String!, $radius: String!) {
  tournaments(query: {
    page: $page, perPage: $perPage, sortBy: "startAt asc",
    filter: {upcoming: true, location: {distanceFrom: $coordinates, distance: $radius}}
  }) {
    pageInfo { totalPages }
    nodes { id name city startAt slug }
  }
}
"""


def fetch_page(token, page):
    request = Request(
        API_URL,
        data=json.dumps({"query": QUERY, "variables": {
            "page": page, "perPage": 50,
            "coordinates": "51.2770, 1.0838", "radius": "3mi",
        }}).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
    )
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("errors") or result.get("success") is False:
        raise RuntimeError(f"start.gg API error: {result.get('errors') or result.get('message')}")
    tournaments = (result.get("data") or {}).get("tournaments")
    if not tournaments or not isinstance(tournaments.get("nodes"), list):
        raise RuntimeError("start.gg returned no tournament list")
    return tournaments


def main():
    token = os.environ["START_GG_TOKEN"]
    events = {}
    page = 1
    while True:
        tournaments = fetch_page(token, page)
        for event in tournaments["nodes"]:
            if any(name in event["name"].lower() for name in ("critical", "honeycomb", "melody")):
                events[event["id"]] = event
        total_pages = tournaments["pageInfo"]["totalPages"]
        if page >= total_pages:
            break
        page += 1

    # Write only after every page succeeds; failed refreshes preserve the last snapshot.
    output = sorted(events.values(), key=lambda event: event["startAt"])
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    print(f"Saved {len(output)} upcoming events")


if __name__ == "__main__":
    main()
