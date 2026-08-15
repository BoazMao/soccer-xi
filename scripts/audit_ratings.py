"""Audit every game rating against its edition-specific historical FIFA row."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from import_fifa_ratings import COUNTRY_ALIASES, RATING_OVERRIDES, YEAR_TO_EDITION, load_ratings, match_score, norm


ROOT = Path(__file__).parents[1]
DATA_PATH = ROOT / "src/data/generatedSquads.json"
OUTPUT_PATH = ROOT / "src/data/ratingAudit.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    squads = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    sources = {edition: load_ratings(args.source_dir, edition) for edition in YEAR_TO_EDITION.values()}
    by_id = {edition: {row["sofifaId"]: row for row in rows} for edition, rows in sources.items()}
    statuses: Counter[str] = Counter()
    by_edition: dict[str, Counter[str]] = defaultdict(Counter)
    issues: list[dict] = []
    unresolved: list[dict] = []
    used: dict[tuple[str, int, str], list[str]] = defaultdict(list)

    for squad in squads:
        edition = YEAR_TO_EDITION[squad["year"]]
        for player in squad["players"]:
            key = (squad["country"], squad["year"], norm(player["name"]))
            if player.get("ratingSource") == "provisional":
                statuses["unresolved"] += 1
                by_edition[str(edition)]["unresolved"] += 1
                unresolved.append({"player": player["name"], "country": squad["country"], "year": squad["year"], "provisionalRating": player["rating"]})
                continue
            source = by_id[edition].get(str(player.get("sofifaId", "")))
            failures = []
            if not source:
                failures.append("source ID missing from edition")
            else:
                source_country = COUNTRY_ALIASES.get(source["country"], source["country"])
                if source["rating"] != player["rating"]:
                    failures.append(f"rating differs from source ({source['rating']})")
                if source_country != squad["country"]:
                    failures.append(f"country differs from source ({source_country})")
                if key not in RATING_OVERRIDES and match_score(player, source) < 68:
                    failures.append("identity confidence below audit threshold")
                used[(squad["country"], squad["year"], str(player["sofifaId"]))].append(player["name"])
            if failures:
                statuses["failed"] += 1
                by_edition[str(edition)]["failed"] += 1
                issues.append({"player": player["name"], "country": squad["country"], "year": squad["year"], "sofifaId": player.get("sofifaId"), "failures": failures})
            else:
                statuses["verified"] += 1
                by_edition[str(edition)]["verified"] += 1

    for (country, year, sofifa_id), names in used.items():
        if len(names) > 1:
            issues.append({"country": country, "year": year, "sofifaId": sofifa_id, "failures": ["source player assigned more than once"], "players": names})

    report = {
        "source": "Edition-specific historical SoFIFA snapshots",
        "editions": {"2010": "FIFA 10", "2014": "FIFA 14", "2018": "FIFA 18", "2022": "FIFA 23"},
        "summary": {"total": sum(statuses.values()), **statuses},
        "byEdition": {edition: dict(counts) for edition, counts in sorted(by_edition.items())},
        "issues": issues,
        "unresolved": unresolved,
    }
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Audit issues: {len(issues)}")


if __name__ == "__main__":
    main()
