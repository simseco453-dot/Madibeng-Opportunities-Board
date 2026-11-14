---
tags: [project, madibeng, log]
---
# Build log

Back to [[Madibeng Opportunities Board]]. Newest first.

## 2026-11-14: Phase 3 collectors

- Wrote `collectors/common.py`, `dpsa.py`, `mqa.py`, `smartrecruiters.py`, `madibeng.py` and `run_all.py`, plus 7 offline tests with sample data. Details in [[Collectors]].
- Added `.github/workflows/refresh.yml` (twice daily, commits data, redeploys) and made `pages.yml` callable from it.
- Added empty `data/manual.json`, `data/review_queue.json` and `data/reviewed_pdfs.json`.
- Tested live through a pull request dry run on GitHub Actions, which can reach the source sites: 12 listings found. Fixed three things the first run showed (see [[Problems and fixes]]) and ran it again.

## 2026-11-14: Phase 1 source audit

- Found the official page for each candidate source with web searches.
- Opened each site in the built-in browser on Jared's computer (the Claude workspace can't reach these sites directly) and checked robots.txt, page structure and any data feeds.
- Found three sources with machine-readable data: MQA's WordPress job-listing API, the SmartRecruiters public posting API (Valterra Platinum, Bosch), and the gov.za "Government jobs this week" page, which always links the latest DPSA circular PDFs.
- Madibeng Municipality publishes vacancies as PDFs; its WordPress media API shows each new PDF with an upload date.
- Results and the v1 picks are in [[Sources]].

## 2026-11-14: Site live (Phase 0 done)

- Claude merged PR #1 (Phase 0 setup) through the GitHub API.
- The first deploy failed: Pages was not switched on yet. Claude couldn't change that setting remotely (GitHub's Pages settings API is blocked from the session, and the desktop browser wasn't signed in to GitHub).
- Jared set Settings → Pages → Source to "GitHub Actions" on his phone. He did not press "Configure" on the suggested workflow, because the repo already has its own (`.github/workflows/pages.yml`).
- Claude re-ran the deploy; it succeeded. Checked the live page in the built-in browser: heading, Coming soon card and scam warning all show.
- Live: https://simseco453-dot.github.io/Madibeng-Opportunities-Board/

## 2026-11-12: Phase 0 setup

- Jared created the GitHub repo `simseco453-dot/Madibeng-Opportunities-Board` (GitHub turned the spaces in the name into dashes).
- Claude added the folder structure: `collectors/`, `data/`, `site/`, `docs/`, `.github/workflows/`.
- Wrote `README.md` with the ground rules and folder guide.
- Created `data/sample-listing.json` (the listing template), empty `listings.json` and `archive.json`, and `status.json`.
- Added `.github/workflows/pages.yml`: on every push to `main` that touches `site/` or `data/`, it copies the site and the latest data into one bundle and deploys it to GitHub Pages.
- Added a placeholder `site/index.html` with a "Coming soon" card and the scam warning. It uses the same colours and fonts as Water & Power Watch (Barlow Condensed + Public Sans, ink `#142231`), copied from `madibeng-watch/style.css`.
- Wrote these notes in `docs/` in Obsidian format, because Jared's computer wasn't connected for writing into the vault directly. They can be copied into the vault as one folder.
