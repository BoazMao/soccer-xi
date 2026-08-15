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
# Verified historical records whose abbreviated source display name cannot be
# matched safely from name similarity alone.
RATING_OVERRIDES = {
    ("South Korea", 2014, "park joo ho"): (73, "191566"),
    ("Portugal", 2014, "rafa silva"): (76, "216547"),
    ("Brazil", 2018, "alisson becker"): (84, "212831"),
    ("Morocco", 2018, "munir mohamedi"): (70, "223573"),
    ("Brazil", 2022, "vinicius junior"): (86, "238794"),
    ("Morocco", 2022, "munir mohamedi"): (73, "223573"),
    ("Spain", 2022, "dani carvajal"): (84, "204963"),
}


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


def name_tokens(value: str) -> list[str]:
    """Compare names independent of display order and hyphenation."""
    return sorted(norm(value).split())


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def match_score(target: dict, candidate: dict) -> float:
    target_name = target["name"]
    scores = []
    for candidate_name in {candidate["name"], candidate["displayName"]}:
        target_parts, candidate_parts = norm(target_name).split(), norm(candidate_name).split()
        if name_tokens(target_name) == name_tokens(candidate_name):
            scores.append(100 + similarity(target["club"], candidate["club"]))
            continue
        if (len(target_parts) >= 2 and set(target_parts).issubset(candidate_parts)
                and surname(target_name) == surname(candidate["displayName"])):
            scores.append(96 + similarity(target["club"], candidate["club"]))
            continue
        score = similarity(target_name, candidate_name) * 52
        if surname(target_name) == surname(candidate["displayName"]):
            score += 32
        if target_parts and candidate_parts and target_parts[0][0] == candidate_parts[0][0]:
            score += 8
        score += similarity(target["club"], candidate["club"]) * 8
        scores.append(score)
    return max(scores)


def exact_name_match(target_name: str, candidate: dict) -> bool:
    if any(
        norm(target_name) == norm(value) or name_tokens(target_name) == name_tokens(value)
        for value in {candidate["name"], candidate["displayName"]}
    ):
        return True
    target_parts = norm(target_name).split()
    return bool(
        len(target_parts) >= 2
        and set(target_parts).issubset(norm(candidate["name"]).split())
        and surname(target_name) == surname(candidate["displayName"])
    )


def surname_match(target_name: str, candidate: dict) -> bool:
    return surname(target_name) == surname(candidate["displayName"])


def given_initial_match(target_name: str, candidate: dict) -> bool:
    target = norm(target_name).split()
    candidates = norm(candidate["name"]).split() + norm(candidate["displayName"]).split()
    return bool(target and candidates and any(part[0] == target[0][0] for part in candidates))


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
        display_name = player_name(row.get("Name", ""))
        slug_match = re.search(r"/player/\d+/([^/]+)/", row.get("href", ""))
        profile_name = slug_match.group(1).replace("-", " ") if slug_match else display_name
        result.append({
            "name": profile_name,
            "displayName": display_name,
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
            override = RATING_OVERRIDES.get((squad["country"], squad["year"], norm(player["name"])))
            if override:
                player["rating"], player["sofifaId"] = override
                player["ratingSource"] = f"FIFA {edition} / SoFIFA"
                matched += 1
                report["matches"].append({"player": player["name"], "year": squad["year"], "matched": "verified override", "rating": player["rating"], "score": 100.0})
                continue
            ranked = sorted(((match_score(player, row), row) for row in country_rows), key=lambda item: item[0], reverse=True)
            best_score, best = ranked[0] if ranked else (0, None)
            runner_up = ranked[1][0] if len(ranked) > 1 else 0
            # Strong surname agreement is required. The margin catches duplicate
            # initials/surnames, which are common in Korea and Portugal.
            exact = bool(best and exact_name_match(player["name"], best))
            display_is_surname_only = bool(best and len(norm(best["displayName"]).split()) == 1)
            confident = bool(best and (exact or (
                surname_match(player["name"], best)
                and (given_initial_match(player["name"], best) or (display_is_surname_only and best_score - runner_up >= 15))
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
