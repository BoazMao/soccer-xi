"""Import historical SoFIFA overall ratings into the World Cup squad dataset.

Usage:
  python scripts/import_fifa_ratings.py --source-dir work/rating-source/FIFA/players

The source CSVs are not committed. Each match is constrained by nationality and
scored from the player's surname, given-name initial, full name, and tournament
club. A report is written so every automatic match can be audited.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).parents[1]
DATA_PATH = ROOT / "src/data/generatedSquads.json"
REPORT_PATH = ROOT / "src/data/ratingCoverage.json"
YEAR_TO_EDITION = {2010: 10, 2014: 14, 2018: 18, 2022: 23}
COUNTRY_ALIASES = {"Korea Republic": "South Korea"}


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"\([^)]*\)", " ", value).lower()
    value = re.sub(r"\b(fc|cf|sc|afc|calcio|club|football)\b", " ", value)
    return " ".join(re.findall(r"[a-z0-9]+", value))


def player_name(value: str) -> str:
    # SoFIFA appends one or more position codes to its short display name.
    positions = r"GK|RWB|LWB|RB|LB|CB|CDM|CM|CAM|RAM|LAM|RM|LM|RW|LW|RF|LF|CF|ST"
    return re.sub(rf"\s+({positions})(\s+({positions}))*$", "", value).strip()


def surname(value: str) -> str:
    parts = norm(value).split()
    return parts[-1] if parts else ""


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def match_score(target: dict, candidate: dict) -> float:
    target_name, candidate_name = target["name"], candidate["name"]
    target_parts, candidate_parts = norm(target_name).split(), norm(candidate_name).split()
    score = similarity(target_name, candidate_name) * 52
    if surname(target_name) == surname(candidate_name):
        score += 32
    if target_parts and candidate_parts and target_parts[0][0] == candidate_parts[0][0]:
        score += 8
    club_score = similarity(target["club"], candidate["club"])
    score += club_score * 8
    return score


def load_ratings(source_dir: Path, edition: int) -> list[dict]:
    path = source_dir / f"Players-FIFA{edition}.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = []
    for row in rows:
        country = COUNTRY_ALIASES.get(row.get("country", ""), row.get("country", ""))
        rating_match = re.match(r"\d+", row.get("Overall rating", ""))
        if not rating_match:
            continue
        team = re.split(r"\s+\d{4}(?:\s*~.*)?$", row.get("Team & Contract", ""))[0]
        result.append({
            "name": player_name(row.get("Name", "")),
            "country": country,
            "club": team,
            "rating": int(rating_match.group()),
            "sofifaId": row.get("ID", ""),
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    squads = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    editions = {edition: load_ratings(args.source_dir, edition) for edition in YEAR_TO_EDITION.values()}
    report = {
        "source": "SoFIFA historical player snapshots",
        "sourceUrl": "https://github.com/aleksey-karasev/Andan_project/tree/main/FIFA/players",
        "editions": {}, "unmatched": [], "matches": [],
    }

    for squad in squads:
        edition = YEAR_TO_EDITION[squad["year"]]
        country_rows = [row for row in editions[edition] if row["country"] == squad["country"]]
        matched = 0
        for player in squad["players"]:
            ranked = sorted(((match_score(player, row), row) for row in country_rows), key=lambda item: item[0], reverse=True)
            best_score, best = ranked[0] if ranked else (0, None)
            runner_up = ranked[1][0] if len(ranked) > 1 else 0
            # Strong surname agreement is required. The margin catches duplicate
            # initials/surnames, which are common in Korea and Portugal.
            exact = bool(best and norm(player["name"]) == norm(best["name"]))
            confident = bool(best and (exact or (
                surname(player["name"]) == surname(best["name"])
                and best_score >= 68
                and best_score - runner_up >= 3
            )))
            if confident:
                player["rating"] = best["rating"]
                player["ratingSource"] = f"FIFA {edition} / SoFIFA"
                player["sofifaId"] = best["sofifaId"]
                matched += 1
                report["matches"].append({"player": player["name"], "year": squad["year"], "matched": best["name"], "rating": best["rating"], "score": round(best_score, 1)})
            else:
                player["ratingSource"] = "provisional"
                report["unmatched"].append({"player": player["name"], "country": squad["country"], "year": squad["year"], "candidate": best["name"] if best else None, "score": round(best_score, 1)})
        year_report = report["editions"].setdefault(str(edition), {"matched": 0, "total": 0})
        year_report["matched"] += matched
        year_report["total"] += len(squad["players"])

    DATA_PATH.write_text(json.dumps(squads, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for edition, coverage in report["editions"].items():
        print(f"FIFA {edition}: {coverage['matched']}/{coverage['total']} matched")
    print(f"Unmatched: {len(report['unmatched'])}")


if __name__ == "__main__":
    main()
