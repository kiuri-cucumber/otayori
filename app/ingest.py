"""資料を文字に直す。まずは文字が埋め込まれた PDF とテキストだけ。"""
from __future__ import annotations

from pathlib import Path


class NeedsOcr(Exception):
    """文字が埋め込まれていない(スキャンの)PDF。OCR の段で扱う。"""


def to_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _pdf_to_text(path)
    raise ValueError(f"まだ扱えない種類です: {suffix}")


def _pdf_to_text(path: Path) -> str:
    import fitz  # PyMuPDF。PDF を読むときだけ要る

    with fitz.open(path) as doc:
        pages = [page.get_text() for page in doc]
    text = "\n".join(pages)
    if not text.strip():
        raise NeedsOcr(str(path))
    return text
