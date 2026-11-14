"""Employers that use SmartRecruiters' public posting API (Valterra Platinum, Bosch)."""
from __future__ import annotations

from common import fetch, guess_qualification, guess_type, is_local, listing

API = "https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=100&offset={offset}"

# company id on SmartRecruiters -> (display name, sector, source key, country filter)
EMPLOYERS = {
    "ValterraPlatinum1": ("Valterra Platinum", "Mining", "valterra", "za"),
    "BoschGroup": ("Bosch", "Manufacturing", "bosch", "za"),
}


def _postings(company: str, country: str) -> list[dict]:
    items, offset = [], 0
    while True:
        url = API.format(company=company, offset=offset) + f"&country={country}"
        page = fetch(url, as_json=True)
        items += page.get("content", [])
        offset += page.get("limit", 100)
        if offset >= page.get("totalFound", 0) or offset >= 1000:
            return items


def collect_company(company: str) -> list[dict]:
    display, sector, key, country = EMPLOYERS[company]
    out = []
    for p in _postings(company, country):
        loc = p.get("location") or {}
        city = loc.get("city") or ""
        if not is_local(city, loc.get("region"), loc.get("fullLocation")):
            continue
        title = p.get("name", "")
        level = (p.get("experienceLevel") or {}).get("label", "")
        out.append(listing(
            source_key=key, ext_id=p["id"], title=title, organisation=display,
            type_=guess_type(title, level),
            min_qualification=guess_qualification(title),
            sector=sector, location=city or "North West",
            closing_date=None,
            apply_link=f"https://jobs.smartrecruiters.com/{company}/{p['id']}",
            source=f"{display} careers (SmartRecruiters)",
        ))
    return out


def collect_valterra() -> list[dict]:
    return collect_company("ValterraPlatinum1")


def collect_bosch() -> list[dict]:
    return collect_company("BoschGroup")
