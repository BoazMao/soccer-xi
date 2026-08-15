"""Align Simplified Chinese player and club names from Chinese squad tables."""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request
from io import StringIO
from pathlib import Path

import lxml.html
import pandas as pd

ROOT = Path(__file__).parents[1]
UA = "SoccerXI/1.0 (Chinese historical squad importer)"
YEARS = (2010, 2014, 2018, 2022)
TITLES = {year: f"{year}年國際足協世界盃參賽球員名單" for year in YEARS}
ALIASES = {"Korea Republic": "South Korea"}
ZH_TO_EN = {"澳大利亚":"Australia","日本":"Japan","韩国":"South Korea","摩洛哥":"Morocco","塞内加尔":"Senegal","巴西":"Brazil","乌拉圭":"Uruguay","哥伦比亚":"Colombia","秘鲁":"Peru","英格兰":"England","波兰":"Poland","葡萄牙":"Portugal","瑞典":"Sweden","克罗地亚":"Croatia","比利时":"Belgium","丹麦":"Denmark","西班牙":"Spain","德国":"Germany","法国":"France","阿根廷":"Argentina"}


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()


def clean(value):
    return re.sub(r"\[[^]]+\]|（队长）|（隊長）|\(captain\)", "", str(value)).strip()


def page_tables(url, chinese=False):
    doc = lxml.html.fromstring(fetch(url))
    output = []
    for heading in doc.xpath("//h3"):
        tables = heading.xpath("following::table[1]")
        if not tables: continue
        html = lxml.html.tostring(tables[0], encoding="unicode")
        try: frame = pd.read_html(StringIO(html))[0]
        except ValueError: continue
        if len(frame) not in (23, 24, 25, 26): continue
        if chinese:
            output.append((heading.text_content().strip(), frame))
        elif {"Pos.", "Player", "Club"}.issubset(frame.columns):
            output.append((ALIASES.get(heading.text_content().strip(), heading.text_content().strip()), frame))
    return output


if __name__ == "__main__":
    generated = json.loads((ROOT / "src/data/generatedSquads.json").read_text(encoding="utf-8"))
    by_key = {(s["country"], s["year"]): s for s in generated}
    players, clubs = {}, {}
    for year in YEARS:
        en_url = f"https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup_squads"
        zh_title = urllib.parse.quote(TITLES[year])
        zh_url = f"https://zh.wikipedia.org/zh-cn/{zh_title}"
        english = page_tables(en_url)
        chinese = {ZH_TO_EN.get(name): frame for name, frame in page_tables(zh_url, chinese=True) if ZH_TO_EN.get(name)}
        for country, en_frame in english:
            squad = by_key.get((country, year))
            zh_frame = chinese.get(country)
            if not squad or zh_frame is None: continue
            for player, (_, en_row), (_, zh_row) in zip(squad["players"], en_frame.iterrows(), zh_frame.iterrows()):
                en_name, en_club = clean(en_row["Player"]), clean(en_row["Club"])
                zh_name, zh_club = clean(zh_row.iloc[2]), clean(zh_row.iloc[-1])
                if en_name and zh_name: players[en_name] = zh_name
                if en_club and zh_club: clubs[en_club] = zh_club
    target = ROOT / "src/data/generatedZh.json"
    target.write_text(json.dumps({"players": players, "clubs": clubs}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(players)} player and {len(clubs)} club translations")
