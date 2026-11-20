"""日付のある項目を、iPhone のカレンダーで購読できる .ics にする。"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, List, Tuple

_PREFIX = {"deadline": "【締切】"}


def _escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    )


def _fold(line: str) -> List[str]:
    """1行を75バイト以内に折る(続きの行は空白で始める)。"""
    out, current, size = [], "", 0
    for ch in line:
        width = len(ch.encode("utf-8"))
        if size + width > 74:
            out.append(current)
            current, size = " ", 1
        current += ch
        size += width
    out.append(current)
    return out


def build_ics(rows: Iterable[Tuple[int, str, str, str]]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//otayori//JP",
        "X-WR-CALNAME:おたより",
    ]
    for item_id, kind, iso, text in rows:
        day = date.fromisoformat(iso)
        lines += [
            "BEGIN:VEVENT",
            f"UID:item-{item_id}@otayori",
            f"DTSTAMP:{day:%Y%m%d}T000000Z",
            f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
            f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}",
            f"SUMMARY:{_escape(_PREFIX.get(kind, '') + text)}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(part for line in lines for part in _fold(line)) + "\r\n"
