"""Shared helpers for every collector."""
from __future__ import annotations

import re
import time
from datetime import date, datetime

import requests

USER_AGENT = (
    "MadibengOpportunitiesBoard/1.0 "
    "(+https://simseco453-dot.github.io/Madibeng-Opportunities-Board/; community job board)"
)

# Places that count as "local". Lower case, matched as whole words.
LOCAL_PLACES = [
    "brits", "madibeng", "hartbeespoort", "hartbeespoortdam", "mooinooi", "letlhabile",
    "mothotlung", "oukasie", "damonsville", "majakaneng", "bapong", "sonop",
    "marikana", "rustenburg", "kroondal", "bojanala", "mmakau", "ga-rankuwa",
]

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def fetch(url: str, *, as_json: bool = False, timeout: int = 45, tries: int = 3):
    """GET a URL politely, with a few retries. Returns text, bytes or parsed JSON."""
    last = None
    for attempt in range(tries):
        try:
            r = _session.get(url, timeout=timeout)
            r.raise_for_status()
            if as_json:
                return r.json()
            ctype = r.headers.get("content-type", "")
            return r.content if "pdf" in ctype or url.lower().endswith(".pdf") else r.text
        except requests.RequestException as e:  # network hiccups are common on gov sites
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def is_local(*texts: str | None) -> bool:
    blob = " ".join(t for t in texts if t).lower()
    return any(re.search(rf"\b{re.escape(p)}\b", blob) for p in LOCAL_PLACES)


def slug(text: str, limit: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:limit].rstrip("-")


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], 1)}
_MONTHS.update({k[:3]: v for k, v in list(_MONTHS.items())})
_MONTHS["sept"] = 9

_DATE_RE = re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(20\d{2})")


def parse_date(text: str | None) -> str | None:
    """'21 November 2026' / '21st Nov 2026' -> '2026-11-21'. None if no date found."""
    if not text:
        return None
    for d, mon, y in _DATE_RE.findall(text):
        m = _MONTHS.get(mon.lower())
        if m:
            try:
                return date(int(y), m, int(d)).isoformat()
            except ValueError:
                continue
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", text)
    if m:
        return m.group(0)
    return None


_CLOSING_RE = re.compile(
    r"closing\s*date\s*(?:for\s+applications?\s*)?(?:is|:|-)?\s*(?:on\s+)?"
    r"(?:\w+day,?\s+)?([^\n.;]{0,40})",
    re.I,
)


def find_closing_date(text: str | None) -> str | None:
    """Look for 'Closing date: 19 November 2026' style phrases."""
    if not text:
        return None
    for m in _CLOSING_RE.finditer(text):
        d = parse_date(m.group(1))
        if d:
            return d
    return None


def guess_type(*texts: str | None) -> str:
    blob = " ".join(t for t in texts if t).lower()
    if "bursar" in blob or "bursary" in blob or "scholarship" in blob:
        return "bursary"
    if "learnership" in blob or "apprentice" in blob or "learner " in blob or "cadet" in blob:
        return "learnership"
    if "intern" in blob or "graduate programme" in blob or "graduate program" in blob or "wil " in blob:
        return "internship"
    return "job"


def guess_qualification(text: str | None) -> str:
    t = (text or "").lower()
    if re.search(r"\b(degree|bachelor|b\.?tech|honours|nqf\s*level\s*[78])\b", t):
        return "Degree"
    if re.search(r"\b(diploma|nqf\s*level\s*6)\b", t):
        return "Diploma"
    if re.search(r"\bn[3-6]\b|\bnc\(?v\)?\b|trade test|red seal", t):
        return "N3 or trade"
    if re.search(r"grade\s*12|matric|senior certificate|nqf\s*level\s*4", t):
        return "Grade 12"
    if re.search(r"abet|grade\s*(8|9|10|11)|basic literacy|no (formal )?qualification", t):
        return "None"
    return "See advert"


def listing(*, source_key: str, ext_id: str, title: str, organisation: str, type_: str,
            min_qualification: str, sector: str, location: str, closing_date: str | None,
            apply_link: str, source: str, verified: bool = True) -> dict:
    return {
        "id": f"{source_key}-{slug(ext_id, 80)}",
        "title": clean(title),
        "organisation": clean(organisation),
        "type": type_,
        "min_qualification": min_qualification,
        "sector": sector,
        "location": location,
        "closing_date": closing_date,
        "apply_link": apply_link,
        "source": source,
        "verified": verified,
        "date_added": date.today().isoformat(),
    }


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
