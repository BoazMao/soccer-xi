"""Build static Soccer XI squad pools from historical final-squad tables.

Squad membership, broad position, tournament club, caps, and international
goals are sourced from the Wikipedia World Cup squad tables, which cite the
official FIFA lists. Club career statistics are left unavailable, and detailed
position eligibility remains provisional pending separate verified imports.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.parse
import urllib.request
from io import StringIO
from pathlib import Path

import lxml.html
import pandas as pd

YEARS = (2010, 2014, 2018, 2022)
TARGETS = {
    "Australia", "Japan", "South Korea", "Morocco", "Senegal", "Brazil",
    "Uruguay", "Colombia", "Peru", "England", "Poland", "Portugal",
    "Sweden", "Croatia", "Belgium", "Denmark", "Spain", "Germany",
    "France", "Argentina",
}
ALIASES = {"Korea Republic": "South Korea"}
COUNTRY_META = {
    "Australia": ("aus", "🇦🇺"), "Japan": ("jpn", "🇯🇵"),
    "South Korea": ("kor", "🇰🇷"), "Morocco": ("mar", "🇲🇦"),
    "Senegal": ("sen", "🇸🇳"), "Brazil": ("bra", "🇧🇷"),
    "Uruguay": ("uru", "🇺🇾"), "Colombia": ("col", "🇨🇴"),
    "Peru": ("per", "🇵🇪"), "England": ("eng", "🏴"),
    "Poland": ("pol", "🇵🇱"), "Portugal": ("por", "🇵🇹"),
    "Sweden": ("swe", "🇸🇪"), "Croatia": ("cro", "🇭🇷"),
    "Belgium": ("bel", "🇧🇪"), "Denmark": ("den", "🇩🇰"),
    "Spain": ("esp", "🇪🇸"), "Germany": ("ger", "🇩🇪"),
    "France": ("fra", "🇫🇷"), "Argentina": ("arg", "🇦🇷"),
}
UA = "SoccerXI/1.0 (static historical squad importer)"


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()


def clean(value: object) -> str:
    return re.sub(r"\[[^]]+\]", "", str(value)).replace("(captain)", "").strip()


def stable_rating(name: str, caps: int) -> int:
    jitter = int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:2], 16) % 5
    return min(89, 69 + round(math.log2(max(1, caps) + 1) * 2.5) + jitter)


def roles(position: str, index: int) -> tuple[str, list[str]]:
    if position == "GK": return "GK", []
    if position == "DF":
        primary = ("LB", "CB", "CB", "RB")[index % 4]
        return primary, [r for r in ("LB", "CB", "RB") if r != primary]
    if position == "MF":
        primary = ("CM", "CM", "LW", "RW")[index % 4]
        return primary, [r for r in ("CM", "LW", "RW") if r != primary]
    primary = ("LW", "ST", "RW")[index % 3]
    return primary, [r for r in ("LW", "ST", "RW") if r != primary]


def squad_stats(caps: int, international_goals: int | None) -> dict[str, int | None]:
    return {
        "clubGoals": None,
        "clubAssists": None,
        "trophies": None,
        "cups": None,
        "internationalGoals": international_goals,
        "caps": caps,
    }


def squad_tables(year: int):
    url = f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads"
    doc = lxml.html.fromstring(fetch(url))
    for heading in doc.xpath("//h3"):
        raw_country = " ".join(heading.text_content().split())
        country = ALIASES.get(raw_country, raw_country)
        if country not in TARGETS: continue
        tables = heading.xpath("following::table[1]")
        if not tables: continue
        table_html = lxml.html.tostring(tables[0], encoding="unicode")
        frame = pd.read_html(StringIO(table_html))[0]
        if {"Pos.", "Player", "Club"}.issubset(frame.columns):
            yield country, frame


def build() -> list[dict]:
    output = []
    for year in YEARS:
        for country, frame in squad_tables(year):
            code, flag = COUNTRY_META[country]
            position_counts = {"GK": 0, "DF": 0, "MF": 0, "FW": 0}
            players = []
            for row_index, row in frame.iterrows():
                broad = clean(row["Pos."]).upper()
                if broad not in position_counts: continue
                name, club = clean(row["Player"]), clean(row["Club"])
                caps_raw = str(row.get("Caps", "0"))
                caps_match = re.search(r"\d+", caps_raw)
                caps = int(caps_match.group()) if caps_match else 0
                goals_raw = str(row.get("Goals", ""))
                goals_match = re.search(r"\d+", goals_raw)
                international_goals = int(goals_match.group()) if goals_match else None
                primary, alt = roles(broad, position_counts[broad])
                position_counts[broad] += 1
                rating = stable_rating(f"{name}-{year}", caps)
                players.append({
                    "id": f"{code}-{year}-{row_index}", "name": name,
                    "country": country, "year": year, "position": primary,
                    "club": club, "rating": rating, "alt": alt,
                    "stats": squad_stats(caps, international_goals),
                })
            output.append({"id": f"{code}-{year}", "country": country, "year": year, "flag": flag, "players": players})
    return sorted(output, key=lambda s: (s["year"], s["country"]))


if __name__ == "__main__":
    squads = build()
    destination = Path(__file__).parents[1] / "src" / "data" / "generatedSquads.json"
    destination.write_text(json.dumps(squads, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(squads)} squads / {sum(len(s['players']) for s in squads)} player records to {destination}")
