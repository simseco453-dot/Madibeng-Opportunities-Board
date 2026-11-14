"""Offline tests: no network. Run with  python -m unittest discover collectors/tests"""
import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import common  # noqa: E402
import dpsa  # noqa: E402
import mqa  # noqa: E402
import run_all  # noqa: E402
import smartrecruiters  # noqa: E402

FUTURE = (date.today() + timedelta(days=20))
FUTURE_TXT = FUTURE.strftime("%d %B %Y")

CIRCULAR = f"""ANNEXURE H
PROVINCIAL ADMINISTRATION: NORTH WEST
DEPARTMENT OF SOCIAL DEVELOPMENT
APPLICATIONS : Hand deliver to Garona Building, Mahikeng
CLOSING DATE : {FUTURE_TXT}
NOTE : Applications must be on the new Z83.
OTHER POSTS
POST 40/101 : SOCIAL AUXILIARY WORKER GRADE 1 REF NO: DSD/2026/14
SALARY : R228 321 per annum (Level 05)
CENTRE : Brits Service Point
REQUIREMENTS : Grade 12 certificate and Further Education and Training
Certificate in Social Auxiliary Work.
DUTIES : Assist social workers.
ENQUIRIES : Ms X Mokoena Tel No: 018 388 0000
POST 40/102 : DIRECTOR: FINANCE REF NO: DSD/2026/15
SALARY : R1 216 824 per annum (Level 13)
CENTRE : Mahikeng Head Office
REQUIREMENTS : Degree in Accounting
POST 40/103 : ADMINISTRATION CLERK (X2 POSTS) REF NO: DSD/2026/16
SALARY : R228 321 per annum (Level 05)
CENTRE : Vryburg District Office
REQUIREMENTS : Grade 12 or equivalent
PROVINCIAL ADMINISTRATION: GAUTENG
DEPARTMENT OF HEALTH
POST 40/200 : CLEANER REF NO: GH/1
SALARY : R118 000 per annum (Level 02)
CENTRE : Pretoria
REQUIREMENTS : ABET
CLOSING DATE : {FUTURE_TXT}
"""


class DpsaTests(unittest.TestCase):
    def test_parse_and_filter(self):
        posts = dpsa.parse_posts(CIRCULAR.splitlines())
        self.assertEqual(len(posts), 4)
        kept = [p for p in posts if dpsa.wanted(p)]
        titles = [dpsa._title_and_ref(p["POST"])[0] for p in kept]
        # Brits post (local) and Vryburg clerk (NW, level 5) kept; NW director and Gauteng cleaner not
        self.assertEqual(titles, ["Social Auxiliary Worker Grade 1", "Administration Clerk"])
        self.assertEqual(kept[0]["CLOSING DATE"], FUTURE.isoformat())  # department-wide date applies
        self.assertEqual(kept[0]["dept"], "Department Of Social Development")
        self.assertEqual(common.guess_qualification(kept[0]["REQUIREMENTS"]), "Grade 12")

    def test_ref(self):
        self.assertEqual(dpsa._title_and_ref("40/101 : SOCIAL WORKER REF NO: DSD/2026/14"),
                         ("Social Worker", "DSD/2026/14"))


class MqaTests(unittest.TestCase):
    def test_skips_tenders_and_finds_dates(self):
        api = [
            {"id": 1, "link": "https://mqa.org.za/job/a/", "date": "2026-11-05",
             "title": {"rendered": "MQA/06/26-27: Appointment of a Travel Management Company"},
             "content": {"rendered": "<p>Tender</p>"}},
            {"id": 2, "link": "https://mqa.org.za/job/b/", "date": "2026-10-19",
             "title": {"rendered": "2027 Bursary Applications for Unemployed Learners Now Open"},
             "content": {"rendered": "<p>Must have Grade 12. Closing date: 19 November 2026.</p>"}},
            {"id": 3, "link": "https://mqa.org.za/job/c/", "date": "2026-10-23",
             "title": {"rendered": "MQA Provincial Research Colloquium Workshops"},
             "content": {"rendered": ""}},
        ]
        with mock.patch.object(mqa, "fetch", return_value=api):
            out = mqa.collect()
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["type"], "bursary")
        self.assertEqual(out[0]["closing_date"], "2026-11-19")
        self.assertEqual(out[0]["min_qualification"], "Grade 12")


class SmartRecruitersTests(unittest.TestCase):
    def test_local_only(self):
        page = {"totalFound": 2, "limit": 100, "content": [
            {"id": "111", "name": "Metallurgist", "location": {"city": "Rustenburg"}},
            {"id": "222", "name": "Learner Miner – Learnership Program", "location": {"city": "Thabazimbi"}},
        ]}
        with mock.patch.object(smartrecruiters, "fetch", return_value=page):
            out = smartrecruiters.collect_valterra()
        self.assertEqual([x["title"] for x in out], ["Metallurgist"])
        self.assertTrue(out[0]["apply_link"].endswith("/ValterraPlatinum1/111"))


class RunAllTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name)
        self.patch = mock.patch.object(run_all, "DATA", self.data)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def _item(self, key, title, closing):
        return common.listing(source_key=key, ext_id=title, title=title, organisation="Org",
                              type_="job", min_qualification="Grade 12", sector="Mining",
                              location="Brits", closing_date=closing, apply_link="https://x",
                              source=key)

    def test_failed_source_keeps_old_and_expired_is_archived(self):
        old_mqa = self._item("mqa", "Old MQA bursary", FUTURE.isoformat())
        old_mqa["date_added"] = "2026-11-01"
        (self.data / "listings.json").write_text(json.dumps([old_mqa]))
        past = (date.today() - timedelta(days=1)).isoformat()

        def boom():
            raise RuntimeError("site down")

        sources = {
            "dpsa": ("DPSA", lambda: [self._item("dpsa", "Clerk", FUTURE.isoformat()),
                                      self._item("dpsa", "Clerk", FUTURE.isoformat()),
                                      self._item("dpsa", "Expired post", past)]),
            "mqa": ("MQA", boom),
        }
        with mock.patch.object(run_all, "SOURCES", sources), \
                mock.patch.object(run_all.madibeng, "find_new_pdfs", return_value=[]):
            status = run_all.run()
        live = json.loads((self.data / "listings.json").read_text())
        archive = json.loads((self.data / "archive.json").read_text())
        self.assertEqual(sorted(x["title"] for x in live), ["Clerk", "Old MQA bursary"])
        self.assertEqual(next(x for x in live if x["title"] == "Old MQA bursary")["date_added"], "2026-11-01")
        self.assertEqual([x["title"] for x in archive], ["Expired post"])
        self.assertFalse(status["sources"]["mqa"]["ok"])
        self.assertEqual(len(status["errors"]), 1)


class CommonTests(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(common.parse_date("Friday, 21st Nov 2026"), "2026-11-21")
        self.assertEqual(common.find_closing_date("The closing date is 5 December 2026."), "2026-12-05")
        self.assertIsNone(common.find_closing_date("No date here"))

    def test_local(self):
        self.assertTrue(common.is_local("Brits Service Point"))
        self.assertFalse(common.is_local("Britstown"))


if __name__ == "__main__":
    unittest.main()
