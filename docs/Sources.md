---
tags: [project, madibeng, sources]
---
# Sources

Back to [[Madibeng Opportunities Board]]. Audited 2026-11-14 (Phase 1). Each site was opened in the built-in browser; robots.txt and any data feeds were checked directly.

Bins: **Automatic** (feed, API or a clean, stable page the collector reads daily), **Semi-automatic** (the collector spots new adverts; you check the details), **Manual** (added by hand), **Not usable** (can't be collected).

## Audit

| Source | Where | Format | Robots/terms | Closing dates | Posts | Bin |
| --- | --- | --- | --- | --- | --- | --- |
| DPSA Public Service Vacancy Circular | `gov.za/government-jobs-week` links the latest circular as 3 PDFs (complete, national, provincial) | PDF, very consistent fields: POST, SALARY, CENTRE, REQUIREMENTS, CLOSING DATE | gov.za robots.txt allows `/sites/default/files/` | Yes, per post | Weekly (Fridays), none in December | **Automatic** (PDF parsing) |
| MQA (mining SETA) | `mqa.org.za/wp-json/wp/v2/job-listings`, also RSS at `/?feed=job_feed` | JSON (WordPress job plugin): title, date, link, `_job_location`, `_company_name` | Allowed (only `/wp-admin/` blocked) | In the advert text, not a field | Few per month | **Automatic** (filter out tenders and events) |
| Valterra Platinum (ex Anglo American Platinum) | Public SmartRecruiters API: `api.smartrecruiters.com/v1/companies/ValterraPlatinum1/postings` | JSON: title, city, date, link | Public posting API, meant for job boards | Often no closing date | 11 live on 14 Nov, 3 in Rustenburg | **Automatic** |
| Bosch (Brits plant) | Same API: `companies/BoschGroup/postings`, filter by city = Brits | JSON | Public posting API | Often none | 0 South African posts on 14 Nov; Brits roles have appeared before | **Automatic** (usually empty) |
| Madibeng Local Municipality | `madibeng.gov.za/vacancies/` (list of PDF downloads); new PDFs also show in `/wp-json/wp/v2/media?search=vacanc` | One PDF per batch of posts | Allowed (only `/wp-admin/` blocked) | Inside the PDF | Every 2 to 5 months | **Semi-automatic**: collector spots each new PDF, you read and add the posts |
| merSETA | `merseta.org.za/wp-json/wp/v2/media?search=advert` | PDF adverts | Allowed | Inside the PDF | Mostly head-office staff jobs in Johannesburg; learnerships are advertised by employers | **Manual** (only when local) |
| North West Provincial Government | `nwpg.gov.za` | — | — | — | Site returned 404 on every page tested | **Not usable**; its posts also appear in the DPSA circular's North West annexure |
| SA Youth (Harambee) | `sayouth.mobi` | Behind a login (ID number) | — | — | — | **Not usable**; link to it on the help page instead (zero-rated, 18 to 34) |
| ESSA (Dept of Employment and Labour) | Registration portal | Behind a login | — | — | — | **Not usable**; link to it on the help page |
| Bojanala District Municipality | `bojanala.gov.za` | Not checked yet | | | | To check |
| NYDA | | Not checked yet | | | | To check |
| Sibanye-Stillwater (Marikana, Rustenburg), Samancor Western Chrome (Mooinooi), Tharisa, Bridgestone Brits | Own careers portals | Not checked yet; none of them were on SmartRecruiters | | | | To check |

## Picked for version 1

1. **DPSA weekly circular**: keep posts whose CENTRE is in Brits, Madibeng, Hartbeespoort, Mooinooi, Rustenburg or Bojanala, plus entry-level posts anywhere in the North West annexure.
2. **MQA job listings**: bursaries and learnerships (mostly national).
3. **Valterra Platinum**: Rustenburg-area roles and learnerships.
4. **Bosch**: Brits roles when they appear.
5. **Madibeng Local Municipality**: semi-automatic. The collector flags new PDFs and you add the posts.

## Notes

- SA Youth and ESSA are where many local opportunities are posted, but both need a login. The board should point people to them on the help page.
- Third-party aggregators (Edupstairs, StudentRoom, MyJobMag and similar) are not sources. We link to the original advert only.
