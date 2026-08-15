"""Build Simplified Chinese names without relying on squad-table row order.

English and zh-cn squad rows are aligned by country, tournament, and shirt
number. This avoids the row-order mismatch that previously attached some
Chinese names to the wrong footballers.
"""
from __future__ import annotations
import json
import re
import time
import urllib.parse
import urllib.error
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
MAINLAND_OVERRIDES = {
    "Luis Suárez": "路易斯·苏亚雷斯", "Kylian Mbappé": "基利安·姆巴佩",
    "Robert Lewandowski": "罗伯特·莱万多夫斯基", "Thibaut Courtois": "蒂博·库尔图瓦",
    "Alisson Becker": "阿利松·贝克尔", "Antoine Griezmann": "安托万·格列兹曼",
    "Karim Benzema": "卡里姆·本泽马", "Olivier Giroud": "奥利维耶·吉鲁",
    "Sergio Agüero": "塞尔希奥·阿圭罗", "Ángel Di María": "安赫尔·迪马利亚",
    "Bastian Schweinsteiger": "巴斯蒂安·施魏因施泰格", "Mario Götze": "马里奥·格策",
    "Andrés Iniesta": "安德烈斯·伊涅斯塔", "Cristiano Ronaldo": "克里斯蒂亚诺·罗纳尔多",
    "Neymar": "内马尔·儒尼奥尔", "Luka Modrić": "卢卡·莫德里奇",
    "Kevin De Bruyne": "凯文·德布劳内", "Harry Kane": "哈里·凯恩",
    "Son Heung-min": "孙兴慜", "Kim Min-jae": "金玟哉",
    "Javier Pastore": "哈维尔·帕斯托雷",
}


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            return urllib.request.urlopen(request).read()
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4: raise
            time.sleep(2 ** attempt)


def clean(value):
    return re.sub(r"\[[^]]+\]|（队长）|（隊長）|\(captain\)", "", str(value)).strip()


def shirt_number(value):
    match = re.search(r"\d+", str(value))
    return match.group() if match else ""


def chinese_only(value):
    return re.sub(r"\s*[（(][^）)]*[）)]\s*", "", clean(value)).strip()


def page_tables(url, chinese=False):
    payload = fetch(url)
    doc = lxml.html.fromstring(payload if chinese else payload.decode("utf-8"))
    output = []
    for heading in doc.xpath("//h3"):
        tables = heading.xpath("following::table[1]")
        if not tables: continue
        html = lxml.html.tostring(tables[0], encoding="unicode")
        try: frame = pd.read_html(StringIO(html))[0]
        except ValueError: continue
        if len(frame) not in (23, 24, 25, 26): continue
        if chinese:
            output.append((heading.text_content().strip(), frame, []))
        elif {"Pos.", "Player", "Club"}.issubset(frame.columns):
            titles = []
            for row in tables[0].xpath(".//tr[td]"):
                links = row.xpath("./th//a[contains(@href,'/wiki/')]")
                titles.append(urllib.parse.unquote(links[0].get("href").split("/wiki/", 1)[1]).replace("_", " ") if links else None)
            output.append((ALIASES.get(heading.text_content().strip(), heading.text_content().strip()), frame, titles))
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
        chinese = {ZH_TO_EN.get(name): frame for name, frame, _ in page_tables(zh_url, chinese=True) if ZH_TO_EN.get(name)}
        for country, en_frame, _ in english:
            squad = by_key.get((country, year))
            zh_frame = chinese.get(country)
            if not squad or zh_frame is None: continue
            zh_by_number = {shirt_number(row.iloc[0]): row for _, row in zh_frame.iterrows()}
            for player, (_, en_row) in zip(squad["players"], en_frame.iterrows()):
                zh_row = zh_by_number.get(shirt_number(en_row.iloc[0]))
                if zh_row is None: continue
                en_name, en_club = clean(en_row["Player"]), clean(en_row["Club"])
                zh_name = chinese_only(zh_row.iloc[2])
                zh_club = clean(zh_row.iloc[-1])
                if en_name and zh_name: players[en_name] = zh_name
                if en_club and zh_club: clubs[en_club] = zh_club
    players.update(MAINLAND_OVERRIDES)
    target = ROOT / "src/data/generatedZh.json"
    target.write_text(json.dumps({"players": players, "clubs": clubs}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(players)} player and {len(clubs)} club translations")
