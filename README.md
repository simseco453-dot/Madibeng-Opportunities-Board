# Madibeng Opportunities Board

A free website that collects learnerships, bursaries, internships and entry-level jobs for Brits and Madibeng in one place, refreshed automatically every day. It sits beside [Water & Power Watch](https://simseco453-dot.github.io/madibeng-watch/) as the second Madibeng community tool.

Live site (once Pages is on): https://simseco453-dot.github.io/Madibeng-Opportunities-Board/

## Ground rules

- We never take applications. Every listing links to the original advert.
- We only collect from public sources whose terms allow it. No LinkedIn or Indeed scraping.
- Nothing from the public goes live until it is checked against a real source.
- Real employers never ask for money. The site says so on every page.
- It must load fast on a cheap phone and cost R0 to run.

## Folders

| Folder | What lives there |
| --- | --- |
| `collectors/` | One Python script per source, plus the main script that runs them all |
| `data/` | `listings.json` (live), `archive.json` (expired), `status.json` (last run), `sample-listing.json` (the format) |
| `site/` | The website, published to GitHub Pages |
| `docs/` | Project notes in Obsidian format: plan, sources, build log, problems and fixes, decisions |
| `.github/workflows/` | The Pages deploy and (from Phase 3) the twice-daily refresh |

## Listing format

See `data/sample-listing.json` and `docs/Data format.md`.

This is a community board, not an official service of any employer, SETA or government department.
