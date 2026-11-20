"""お便りの文字から、日付つきの予定・締め切りと持ち物を拾う。

まずは決まった書き方だけを確実に拾う土台。拾えない書き方は検査に足してから直す。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

_ZEN = str.maketrans("0123456789/():", "0123456789/():")
_ERA_BASE = {"令和": 2018, "平成": 1988}
_DATE_RE = re.compile(
    r"(?:(令和|平成)\s*(\d{1,2}|元)\s*年|(\d{4})\s*年)?\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
)
_DEADLINE_WORDS = ("まで", "締切", "締め切り", "〆切", "提出", "期限")
_BRING_RE = re.compile(r"持ち物\s*[】\])]?\s*[::]?\s*(.+)")


@dataclass(frozen=True)
class Item:
    kind: str  # "event" | "deadline" | "bring"
    date: Optional[str]  # ISO の日付。持ち物は None
    text: str  # 根拠になった行(持ち物は品名)


def _year_for(month: int, day: int, today: date) -> Optional[int]:
    """年が書かれていない日付の年を決める。2か月より前になるなら翌年とみなす。"""
    for year in (today.year, today.year + 1):
        try:
            candidate = date(year, month, day)
        except ValueError:
            return None
        if candidate >= today - timedelta(days=60):
            return year
    return None


def _dates_in(line: str, today: date) -> List[date]:
    found = []
    for era, era_year, western, month, day in _DATE_RE.findall(line):
        m, d = int(month), int(day)
        if era:
            year = _ERA_BASE[era] + (1 if era_year == "元" else int(era_year))
        elif western:
            year = int(western)
        else:
            year = _year_for(m, d, today)
        if year is None:
            continue
        try:
            found.append(date(year, m, d))
        except ValueError:
            continue  # 2月30日 のような、ありえない日付は捨てる
    return found


def extract(text: str, today: date) -> List[Item]:
    items: List[Item] = []
    for raw in text.splitlines():
        line = raw.translate(_ZEN).strip()
        if not line:
            continue
        bring = _BRING_RE.search(line)
        if bring:
            for name in re.split(r"[、,・]", bring.group(1)):
                name = name.strip(" 。")
                if name:
                    items.append(Item("bring", None, name))
            continue
        kind = "deadline" if any(w in line for w in _DEADLINE_WORDS) else "event"
        for d in _dates_in(line, today):
            items.append(Item(kind, d.isoformat(), line))
    return items
