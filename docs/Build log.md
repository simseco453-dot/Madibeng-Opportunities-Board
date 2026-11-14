---
tags: [project, madibeng, log]
---
# Build log

Back to [[Madibeng Opportunities Board]]. Newest first.

## 2026-11-12: Phase 0 setup

- Jared created the GitHub repo `simseco453-dot/Madibeng-Opportunities-Board` (GitHub turned the spaces in the name into dashes).
- Claude added the folder structure: `collectors/`, `data/`, `site/`, `docs/`, `.github/workflows/`.
- Wrote `README.md` with the ground rules and folder guide.
- Created `data/sample-listing.json` (the listing template), empty `listings.json` and `archive.json`, and `status.json`.
- Added `.github/workflows/pages.yml`: on every push to `main` that touches `site/` or `data/`, it copies the site and the latest data into one bundle and deploys it to GitHub Pages.
- Added a placeholder `site/index.html` with a "Coming soon" card and the scam warning. It uses the same colours and fonts as Water & Power Watch (Barlow Condensed + Public Sans, ink `#142231`), copied from `madibeng-watch/style.css`.
- Wrote these notes in `docs/` in Obsidian format, because Jared's computer wasn't connected for writing into the vault directly. They can be copied into the vault as one folder.
