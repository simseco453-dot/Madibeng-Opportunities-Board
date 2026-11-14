---
tags: [project, madibeng, collectors]
---
# Collectors

Back to [[Madibeng Opportunities Board]]. Built in Phase 3 (2026-11-14). Code is in `collectors/`.

## How a refresh runs

`.github/workflows/refresh.yml` runs at 05:00 and 17:00 South African time (03:00 and 15:00 UTC), and on demand from the Actions tab.

1. Installs `collectors/requirements.txt` (requests, pdfplumber).
2. Runs the offline tests (`collectors/tests/`). If they fail, nothing is collected.
3. Runs `collectors/run_all.py`, which writes the `data/` files.
4. If `data/` changed, commits it as "madibeng-board-bot" and redeploys the site (it calls `pages.yml`, because a commit made by a workflow doesn't trigger other workflows).

On a pull request the same workflow runs the tests and a **dry run** that prints what it would collect and writes nothing. That's how new collector code is tested against the real sites before it goes live.

## The collectors

| File | Source | What it keeps |
| --- | --- | --- |
| `dpsa.py` | gov.za "Government jobs this week" → this week's national and provincial circular PDFs | Posts whose CENTRE names a local place, plus North West posts at salary level 1 to 7 or with clerk/intern/learner/general worker/cleaner in the title. Department-wide closing dates are applied to every post under them. |
| `mqa.py` | `mqa.org.za/wp-json/wp/v2/job-listings` | Everything except tenders, events and grant calls for employers. Closing date found in the advert text ("closing date", "closes on"). |
| `smartrecruiters.py` | SmartRecruiters public API, South African posts of Valterra Platinum and Bosch | Posts whose city is a local place. |
| `madibeng.py` | Madibeng media library (`/wp-json/wp/v2/media?search=vacanc`) | Publishes nothing. Adds vacancy PDFs from the last 90 days that nobody has reviewed to `data/review_queue.json`. |
| `common.py` | — | Shared helpers: polite fetching with retries, the list of local places, date parsing, guessing the listing type and minimum qualification. |
| `run_all.py` | — | Runs everything and writes the data files (rules below). |

Local places (`common.LOCAL_PLACES`): Brits, Madibeng, Hartbeespoort, Mooinooi, Letlhabile, Mothotlung, Oukasie, Damonsville, Majakaneng, Bapong, Sonop, Marikana, Rustenburg, Kroondal, Bojanala, Mmakau, Ga-Rankuwa.

## Rules in `run_all.py`

- A source that fails keeps its listings from the last good run, so one broken website never empties the board. The error is written to `data/status.json`.
- A source that returns nothing 6 runs in a row (about 3 days) gets a warning in `status.json`. Bosch is exempt because it's usually empty.
- Listings past their closing date move to `data/archive.json`, and so do listings that disappear from a source that worked.
- `date_added` keeps the first day a listing was seen.
- Duplicates (same title, organisation and closing date) are dropped.
- Merges `data/manual.json` (hand-added listings) and approved rows from the community form, when the repo variable `SUBMISSIONS_CSV_URL` is set (Phase 5).

## Weekly job: Madibeng PDFs

1. Open `data/review_queue.json` on GitHub. Each entry has the PDF link.
2. Read the PDF and add each post to `data/manual.json` in the [[Data format]] (id starting `manual-`).
3. Add the PDF's link to `data/reviewed_pdfs.json` and remove its entry from `review_queue.json`.

## First live test (dry run, PR #4)

12 listings: 8 from the DPSA circular 40 of 6 November 2026 (5 Department of Water and Sanitation posts at Hartbeespoort, 3 North West entry-level posts), 2 MQA bursaries closing 19 November, 3 Valterra posts in Rustenburg (2 identical "Metallurgist" titles merged into one), 0 Bosch, 0 new Madibeng PDFs.

## Known limits

- DPSA listings link to the whole circular PDF, because posts don't have their own pages. The title and reference number help people find the post inside it.
- The minimum qualification is a guess from the requirements text. "See advert" when unsure.
- SmartRecruiters posts rarely give a closing date.
