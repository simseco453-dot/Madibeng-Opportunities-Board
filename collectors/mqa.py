"""MQA (Mining Qualifications Authority) adverts, from its WordPress job-listing API."""
from __future__ import annotations

import html
import re

from common import clean, fetch, find_closing_date, guess_qualification, guess_type, listing

NAME = "MQA"
API = "https://mqa.org.za/wp-json/wp/v2/job-listings?per_page=30&_fields=id,date,link,title,content"

# Adverts that are not for job seekers: tenders, events, grants for employers.
SKIP = re.compile(
    r"tender|request for (proposal|quotation)|rfq|rfp|appointment of an? |panel of|"
    r"service provider|colloquium|workshop|conference|discretionary grant|"
    r"^mqa/\d+/\d+",
    re.I,
)


def _text(rendered: str) -> str:
    return clean(html.unescape(re.sub(r"<[^>]+>", " ", rendered or "")))


def collect() -> list[dict]:
    posts = fetch(API, as_json=True)
    out = []
    for p in posts:
        title = _text(p["title"]["rendered"])
        body = _text(p.get("content", {}).get("rendered", ""))
        if SKIP.search(title):
            continue
        if re.search(r"applications have closed|closed vacancies", body, re.I):
            continue
        out.append(listing(
            source_key="mqa", ext_id=str(p["id"]), title=title,
            organisation="Mining Qualifications Authority (MQA)",
            type_=guess_type(title, body[:400]),
            min_qualification=guess_qualification(body),
            sector="Mining", location="National",
            closing_date=find_closing_date(body),
            apply_link=p["link"], source="MQA website",
        ))
    return out
