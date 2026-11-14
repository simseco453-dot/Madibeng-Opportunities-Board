"""Madibeng Local Municipality. Semi-automatic.

The municipality posts vacancies as PDFs. This collector does not publish anything:
it finds vacancy PDFs that haven't been reviewed yet and adds them to
data/review_queue.json, so a person can read the PDF and add the posts by hand.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from common import fetch, today


def RECENT_CUTOFF() -> str:
    return (date.today() - timedelta(days=90)).isoformat()

NAME = "Madibeng Municipality"
API = ("https://www.madibeng.gov.za/wp-json/wp/v2/media?search=vacanc&per_page=20"
       "&_fields=id,date,title,source_url")
REVIEWED = Path(__file__).resolve().parent.parent / "data" / "reviewed_pdfs.json"


def find_new_pdfs() -> list[dict]:
    reviewed = set(json.loads(REVIEWED.read_text())) if REVIEWED.exists() else set()
    media = fetch(API, as_json=True)
    new = []
    for m in media:
        url = m.get("source_url", "")
        if not url.lower().endswith(".pdf") or url in reviewed:
            continue
        if m["date"][:10] < RECENT_CUTOFF():  # older PDFs have long closed
            continue
        new.append({
            "source": NAME,
            "title": m["title"]["rendered"],
            "uploaded": m["date"][:10],
            "pdf": url,
            "found": today(),
        })
    return new
