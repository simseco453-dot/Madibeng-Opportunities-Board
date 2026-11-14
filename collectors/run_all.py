"""Run every collector and rebuild the board's data files.

    python collectors/run_all.py            # collect and write data/
    python collectors/run_all.py --dry-run  # collect and print, write nothing

Rules:
- A source that fails keeps its listings from the last good run, so one broken
  website never empties the board.
- Listings past their closing date move to data/archive.json.
- Hand-added listings (data/manual.json) and approved community submissions
  (the published Google Sheet CSV in SUBMISSIONS_CSV_URL) are merged in.
- Duplicates (same title, organisation and closing date) are dropped.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dpsa  # noqa: E402
import madibeng  # noqa: E402
import mqa  # noqa: E402
import smartrecruiters  # noqa: E402
from common import clean, fetch, guess_qualification, listing, now_iso, slug, today  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
ZERO_ALERT_RUNS = 6  # twice a day, so about 3 days

# source key (the id prefix) -> (display name, collector)
SOURCES = {
    "dpsa": ("DPSA circular", dpsa.collect),
    "mqa": ("MQA", mqa.collect),
    "valterra": ("Valterra Platinum", smartrecruiters.collect_valterra),
    "bosch": ("Bosch", smartrecruiters.collect_bosch),
}
# Sources that are often empty for long stretches; zero results is not a warning sign.
OFTEN_EMPTY = {"bosch"}
KEEP_ALWAYS = {"manual", "community"}

VALID_TYPES = {"job", "learnership", "bursary", "internship"}


def load(name: str, default):
    p = DATA / name
    return json.loads(p.read_text()) if p.exists() else default


def save(name: str, value) -> None:
    (DATA / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def key_of(item: dict) -> str:
    return item["id"].split("-", 1)[0]


def dedupe_key(item: dict) -> tuple:
    return (slug(item["title"]), slug(item["organisation"]), item.get("closing_date"))


def submissions() -> tuple[list[dict], str | None]:
    """Approved rows from the community form's published CSV, if one is set up."""
    url = os.environ.get("SUBMISSIONS_CSV_URL", "").strip()
    if not url:
        return [], None
    try:
        text = fetch(url)
        rows = csv.DictReader(io.StringIO(text))
        out = []
        for r in rows:
            r = {clean(k).lower(): clean(v) for k, v in r.items() if k}
            if r.get("approved", "").lower() not in ("yes", "true", "1", "y"):
                continue
            if not (r.get("title") and r.get("organisation") and r.get("apply_link")):
                continue
            t = r.get("type", "job").lower()
            out.append(listing(
                source_key="community", ext_id=f"{r['title']}-{r['organisation']}",
                title=r["title"], organisation=r["organisation"],
                type_=t if t in VALID_TYPES else "job",
                min_qualification=r.get("min_qualification") or guess_qualification(r.get("title")),
                sector=r.get("sector") or "Other", location=r.get("location") or "Madibeng",
                closing_date=r.get("closing_date") or None,
                apply_link=r["apply_link"], source="Community submission (checked)",
            ))
        return out, None
    except Exception as e:  # a broken sheet must not stop the run
        return [], f"{type(e).__name__}: {e}"


def run(dry_run: bool = False) -> dict:
    old = load("listings.json", [])
    old_by_id = {x["id"]: x for x in old}
    status_old = load("status.json", {})
    sources_old = status_old.get("sources", {})

    fresh: list[dict] = []
    status = {"last_run": now_iso(), "sources": {}, "errors": [], "warnings": []}

    for key, (name, fn) in SOURCES.items():
        prev = sources_old.get(key, {})
        try:
            items = fn()
            zero_runs = 0 if items else prev.get("zero_runs", 0) + 1
            status["sources"][key] = {"name": name, "ok": True, "count": len(items),
                                      "zero_runs": zero_runs, "last_success": status["last_run"]}
            if zero_runs >= ZERO_ALERT_RUNS and key not in OFTEN_EMPTY:
                status["warnings"].append(
                    f"{name} has returned nothing {zero_runs} runs in a row; its page may have changed.")
            fresh += items
        except Exception as e:
            kept = [x for x in old if key_of(x) == key]
            status["sources"][key] = {"name": name, "ok": False, "count": len(kept),
                                      "zero_runs": prev.get("zero_runs", 0),
                                      "last_success": prev.get("last_success"),
                                      "error": f"{type(e).__name__}: {e}"}
            status["errors"].append(f"{name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            fresh += kept  # keep last good listings

    # Hand-added and community listings
    fresh += [x for x in load("manual.json", []) if x.get("title")]
    subs, sub_err = submissions()
    fresh += subs
    if sub_err:
        status["errors"].append(f"Community submissions: {sub_err}")

    # Keep the first date each listing was seen
    for x in fresh:
        if x["id"] in old_by_id:
            x["date_added"] = old_by_id[x["id"]].get("date_added", x["date_added"])

    # Split live vs expired, drop duplicates
    t = today()
    live, expired, seen = [], [], set()
    for x in fresh:
        if x.get("closing_date") and x["closing_date"] < t:
            expired.append(x)
            continue
        k = dedupe_key(x)
        if k in seen:
            continue
        seen.add(k)
        live.append(x)
    live.sort(key=lambda x: (x.get("closing_date") or "9999", x["title"]))

    # Archive: expired now, plus anything that vanished from a source that worked
    live_ids = {x["id"] for x in live}
    gone = [x for x in old if x["id"] not in live_ids and key_of(x) not in KEEP_ALWAYS
            and status["sources"].get(key_of(x), {}).get("ok", True)]
    archive = load("archive.json", [])
    archived_ids = {x["id"] for x in archive}
    for x in expired + gone:
        if x["id"] not in archived_ids:
            archive.append({**x, "archived_on": t})
            archived_ids.add(x["id"])

    # Madibeng: queue new vacancy PDFs for a person to review
    queue = load("review_queue.json", [])
    try:
        queued = {q["pdf"] for q in queue}
        new_pdfs = [q for q in madibeng.find_new_pdfs() if q["pdf"] not in queued]
        queue += new_pdfs
        status["sources"]["madibeng"] = {"name": madibeng.NAME, "ok": True,
                                         "new_pdfs": len(new_pdfs), "waiting_for_review": len(queue)}
    except Exception as e:
        status["sources"]["madibeng"] = {"name": madibeng.NAME, "ok": False,
                                         "error": f"{type(e).__name__}: {e}",
                                         "waiting_for_review": len(queue)}
        status["errors"].append(f"{madibeng.NAME}: {type(e).__name__}: {e}")

    status["live_listings"] = len(live)

    if dry_run:
        print(json.dumps({"status": status, "sample": live[:15]}, indent=2, ensure_ascii=False))
    else:
        save("listings.json", live)
        save("archive.json", archive)
        save("review_queue.json", queue)
        save("status.json", status)
        print(f"{len(live)} live listings; {len(expired)} expired; "
              f"{len(status['errors'])} errors; {len(queue)} PDFs waiting for review")
        for e in status["errors"]:
            print("ERROR:", e)
    return status


if __name__ == "__main__":
    run(dry_run="--dry-run" in sys.argv)
