---
tags: [project, madibeng, problems]
---
# Problems and fixes

Back to [[Madibeng Opportunities Board]]. Newest first.

## 2026-11-14: Source sites unreachable from the workspace

- **Problem:** the Claude workspace's network only allows package registries and GitHub, so it couldn't open madibeng.gov.za, mqa.org.za and the others.
- **Fix:** used the built-in browser in the Claude desktop app on Jared's computer, approving each site once. This doesn't affect the real collectors: they run on GitHub Actions, which can reach these sites.

## 2026-11-14: dpsa.gov.za wouldn't load

- **Problem:** the DPSA's own circular page failed to load in the browser.
- **Fix:** gov.za hosts the same circulars at `gov.za/government-jobs-week`, which links the newest circular's PDFs each week. Use that instead.

## 2026-11-14: nwpg.gov.za returns 404

- **Problem:** the North West Provincial Government site returned "Not Found" for every page tested.
- **Fix:** skip it. Provincial posts are also published in the DPSA circular's North West annexure.

## 2026-11-14: First Pages deploy failed

- **Problem:** the deploy workflow failed at `actions/configure-pages` because Pages wasn't enabled for the repo.
- **Fix:** Settings → Pages → Source: GitHub Actions (done by hand; the setting can't be changed from the Claude session), then re-ran the workflow.
- **Note:** after choosing GitHub Actions, GitHub suggests starter workflows with a "Configure" button. Ignore it; this repo has its own.

## 2026-11-12: GitHub Pages can't serve from `site/`

- **Problem:** the plan said to serve the site from `site/`, but GitHub Pages' simple mode only serves from the repo root or `docs/`, and `docs/` holds these notes.
- **Fix:** deploy with a GitHub Actions workflow (`.github/workflows/pages.yml`) instead. It also lets each deploy include the latest `data/` files.
- **Needs:** Settings → Pages → Source set to "GitHub Actions".

## 2026-11-12: Computer not connected for Obsidian

- **Problem:** the notes were meant to go straight into the Obsidian vault, but the desktop bridge wasn't connected.
- **Fix:** notes written to `docs/` in Obsidian format (wikilinks, frontmatter tags). Copy the folder into the vault, or open `docs/` as its own vault.
