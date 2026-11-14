"""DPSA Public Service Vacancy Circular, published weekly on gov.za as PDFs.

Keeps posts whose CENTRE is near Brits, plus entry-level posts (salary level 1 to 7)
anywhere in the North West annexure.
"""
from __future__ import annotations

import io
import re

import pdfplumber

from common import clean, fetch, guess_qualification, guess_type, is_local, listing, parse_date

NAME = "DPSA circular"
WEEK_PAGE = "https://www.gov.za/government-jobs-week"
BASE = "https://www.gov.za"

FIELD_RE = re.compile(
    r"^(POST|SALARY|CENTRE|REQUIREMENTS|DUTIES|ENQUIRIES|APPLICATIONS|FOR ATTENTION|"
    r"CLOSING DATE|NOTE|NOTES|OTHER POSTS)\s*(\d+/\d+)?\s*:\s*(.*)$"
)
PROVINCE_RE = re.compile(r"PROVINCIAL ADMINISTRATION\s*:\s*([A-Z \-]+)")
DEPT_RE = re.compile(r"^(DEPARTMENT OF [A-Z ,&\-]+|OFFICE OF THE PREMIER)\s*$")
LEVEL_RE = re.compile(r"\(?\s*Level\s*(\d{1,2})\s*\)?", re.I)
CIRC_RE = re.compile(r"CIRCULAR\D{0,10}(\d{1,2})\s*OF\s*(20\d{2})", re.I)


def circular_pdfs() -> tuple[str, list[str]]:
    """Return (label, [pdf urls]) for this week's national and provincial PDFs."""
    page = fetch(WEEK_PAGE)
    links = re.findall(r'href="([^"]+\.pdf)"[^>]*>([^<]*)<', page, re.I)
    wanted = []
    for href, text in links:
        t = text.lower()
        if "national government jobs" in t or "provincial government jobs" in t:
            wanted.append(href if href.startswith("http") else BASE + href)
    label = ""
    m = re.search(r"Vacancy Circular No\.?\s*(\d+)\s*of\s*([^<]+?)<", page)
    if m:
        label = f"Circular {m.group(1)} ({clean(m.group(2))})"
    if not wanted:  # fall back to the complete circular
        for href, text in links:
            if "vacancy circular" in text.lower():
                wanted.append(href if href.startswith("http") else BASE + href)
                break
    return label, wanted


def pdf_lines(data: bytes) -> list[str]:
    lines = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            lines += (page.extract_text() or "").splitlines()
    return [ln.strip() for ln in lines]


def parse_posts(lines: list[str]) -> list[dict]:
    """Split circular text into posts. Each post carries its province and department."""
    posts, cur, field = [], None, None
    province, dept, dept_closing = "", "", None
    for ln in lines:
        if not ln:
            continue
        pm = PROVINCE_RE.search(ln)
        if pm:
            province, dept, dept_closing, cur = clean(pm.group(1)).title(), "", None, None
            continue
        if ln.startswith("NATIONAL DEPARTMENT") or ln.startswith("ANNEXURE"):
            if ln.startswith("NATIONAL"):
                province = "National"
            continue
        dm = DEPT_RE.match(ln)
        if dm and (cur is None or field not in ("REQUIREMENTS", "DUTIES")):
            dept, dept_closing, cur = clean(dm.group(1)).title(), None, None
            continue
        fm = FIELD_RE.match(ln)
        if fm:
            field, value = fm.group(1), fm.group(3)
            if field == "POST":
                cur = {"POST": value, "province": province, "dept": dept,
                       "dept_closing": dept_closing}
                posts.append(cur)
            elif field == "CLOSING DATE":
                d = parse_date(value)
                if cur is None:
                    dept_closing = d  # stated once for the whole department
                else:
                    cur["CLOSING DATE"] = d
            elif cur is not None:
                cur[field] = (cur.get(field, "") + " " + value).strip()
            continue
        if cur is not None and field and field != "CLOSING DATE":
            cur[field] = (cur.get(field, "") + " " + ln).strip()
    for p in posts:
        p["CLOSING DATE"] = p.get("CLOSING DATE") or p.pop("dept_closing", None)
        p.pop("dept_closing", None)
    return posts


def _title_and_ref(post_field: str) -> tuple[str, str]:
    # "40/12 : ADMINISTRATION CLERK REF NO: NW/DSD/2026/14"  (the first part is the post number)
    s = re.sub(r"^\d+/\d+\s*:?\s*", "", post_field)
    m = re.search(r"\bREF\.?\s*(?:NO\.?|NUMBER)?\s*:?\s*(\S.*)$", s, re.I)
    ref = clean(m.group(1)) if m else ""
    title = clean(s[: m.start()] if m else s)
    title = re.sub(r"\(X\s*\d+\s*POSTS?\)", "", title, flags=re.I).strip(" -:")
    return title.title(), ref


def wanted(post: dict) -> bool:
    centre = post.get("CENTRE", "")
    if is_local(centre):
        return True
    if post.get("province", "").lower().startswith("north west"):
        lv = LEVEL_RE.search(post.get("SALARY", ""))
        if lv and int(lv.group(1)) <= 7:
            return True
        if re.search(r"intern|learner|general worker|cleaner|clerk", post.get("POST", ""), re.I):
            return True
    return False


def collect() -> list[dict]:
    label, pdfs = circular_pdfs()
    out = []
    for url in pdfs:
        posts = parse_posts(pdf_lines(fetch(url, timeout=120)))
        for p in posts:
            if not wanted(p):
                continue
            title, ref = _title_and_ref(p["POST"])
            centre = clean(p.get("CENTRE", "")) or p.get("province", "")
            org = p.get("dept") or f"{p.get('province', '')} government".strip()
            reqs = p.get("REQUIREMENTS", "")
            out.append(listing(
                source_key="dpsa", ext_id=f"{ref or title}-{centre}",
                title=title, organisation=org,
                type_=guess_type(title),
                min_qualification=guess_qualification(reqs),
                sector="Government", location=centre[:60],
                closing_date=p.get("CLOSING DATE"),
                apply_link=url,
                source=f"DPSA vacancy {label}".strip(),
            ))
    return out
