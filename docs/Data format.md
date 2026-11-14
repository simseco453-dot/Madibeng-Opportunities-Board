---
tags: [project, madibeng, data]
---
# Data format

Back to [[Madibeng Opportunities Board]]. Example file: `data/sample-listing.json`.

| Field | Example | Required |
| --- | --- | --- |
| id | `mqa-2026-0412` | Yes |
| title | Process Plant Learnership | Yes |
| organisation | Name of employer or SETA | Yes |
| type | job / learnership / bursary / internship | Yes |
| min_qualification | Grade 12 / N3 / Diploma / Degree / None | Yes |
| sector | Mining, Manufacturing, Government, Retail… | Yes |
| location | Brits / Madibeng / North West / National | Yes |
| closing_date | 2026-12-05 (YYYY-MM-DD) | If known |
| apply_link | Link to the original advert | Yes |
| source | Where we found it | Yes |
| verified | true once checked | Yes |
| date_added | 2026-11-20 | Yes |

## Location filter

Keep a listing if it mentions Brits, Madibeng, Hartbeespoort, Mooinooi, Rustenburg or Bojanala, or if it is a national programme open to anyone.

## Files

- `data/listings.json`: live listings
- `data/archive.json`: listings past their closing date
- `data/status.json`: last run time, count per source, errors
