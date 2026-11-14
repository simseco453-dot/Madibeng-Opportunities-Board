---
tags: [project, madibeng, decisions]
---
# Decisions

Back to [[Madibeng Opportunities Board]]. Newest first.

| Date | Decision | Why |
| --- | --- | --- |
| 2026-11-14 | v1 sources: DPSA circular, MQA, Valterra, Bosch (automatic) + Madibeng Municipality (semi-automatic) | Best mix of local relevance and data a script can read reliably |
| 2026-11-14 | Use gov.za's weekly page for the DPSA circular, not dpsa.gov.za | dpsa.gov.za didn't load; gov.za links the same PDFs |
| 2026-11-14 | Don't collect from SA Youth or ESSA; link to them on the help page | Both need a login |
| 2026-11-14 | Never use aggregator sites (Edupstairs, StudentRoom, MyJobMag) as sources | We only link to original adverts |
| 2026-11-12 | Deploy Pages through GitHub Actions, not a branch folder | Lets the site live in `site/` and ship the latest data with each deploy |
| 2026-11-12 | Static site + JSON data, no database for listings | Free, fast on slow phones, nothing to maintain |
| 2026-11-12 | Google Form + Sheet for community submissions | Free, easy moderation with an `approved` column |
| 2026-11-12 | Same look as Water & Power Watch | Both sites read as one Madibeng community brand |
| 2026-11-12 | Never take applications; always link to the original advert | Protects people from scams and keeps us out of handling personal data |
| 2026-11-12 | No LinkedIn or Indeed scraping | Their terms forbid it |
