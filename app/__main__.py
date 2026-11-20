"""使い方:
    python -m app add <資料>...   資料を読み取って登録する
    python -m app feed            カレンダー(.ics)を標準出力に出す
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from . import feed, ingest, store
from .extract import extract

DB_PATH = Path("data/otayori.db")


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[0] == "add":
        DB_PATH.parent.mkdir(exist_ok=True)
        conn = store.connect(DB_PATH)
        for name in argv[1:]:
            path = Path(name)
            try:
                text = ingest.to_text(path)
            except ingest.NeedsOcr:
                print(f"{path.name}: 文字が入っていない PDF です(OCR はまだ)")
                continue
            items = extract(text, date.today())
            _, added = store.add_document(conn, path.name, path.read_bytes(), text, items)
            print(f"{path.name}: {len(items)} 件" + ("" if added else "(登録済み)"))
        return 0
    if argv == ["feed"]:
        sys.stdout.write(feed.build_ics(store.dated_items(store.connect(DB_PATH))))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
