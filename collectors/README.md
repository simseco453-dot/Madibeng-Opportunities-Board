# Collectors

One Python script per automatic source (Phase 3). Each returns listings in the format of `data/sample-listing.json`.

A main script (`run_all.py`, still to come) runs every collector, keeps going if one fails, applies the location filter, removes duplicates, archives expired listings, merges approved community submissions, and writes `data/listings.json` and `data/status.json`.

Rules: one visit per source per day, a user-agent that names this site, respect each site's robots.txt and terms.
