import unittest
from datetime import date
from pathlib import Path

from app import feed, ingest, store
from app.extract import Item, extract

SAMPLE = Path(__file__).parent / "fixtures" / "sample_otayori.txt"
TODAY = date(2027, 3, 1)


class ExtractTest(unittest.TestCase):
    def test_sample_printout(self):
        items = extract(ingest.to_text(SAMPLE), TODAY)
        self.assertEqual(
            [(i.kind, i.date) for i in items if i.date],
            [("event", "2027-04-08"), ("deadline", "2027-04-02"), ("event", "2027-04-15")],
        )
        self.assertEqual(
            [i.text for i in items if i.kind == "bring"], ["上履き", "手さげ袋", "筆記用具"]
        )

    def test_full_width_digits_and_first_era_year(self):
        self.assertEqual(extract("令和元年5月1日 開園", TODAY)[0].date, "2019-05-01")
        self.assertEqual(extract("４月８日 入園式", TODAY)[0].date, "2027-04-08")

    def test_date_without_year_rolls_into_next_year(self):
        self.assertEqual(extract("1月10日 始業式", date(2026, 12, 1))[0].date, "2027-01-10")

    def test_impossible_date_is_dropped(self):
        self.assertEqual(extract("2月30日 遠足", TODAY), [])


class StoreAndFeedTest(unittest.TestCase):
    def test_same_document_is_stored_once(self):
        conn = store.connect(":memory:")
        items = [Item("deadline", "2027-04-02", "調査票は4月2日までに提出")]
        first = store.add_document(conn, "a.pdf", b"same", "text", items)
        second = store.add_document(conn, "b.pdf", b"same", "text", items)
        self.assertEqual((first[1], second[1], second[0]), (True, False, first[0]))
        self.assertEqual(len(store.dated_items(conn)), 1)

    def test_feed_has_all_day_event_and_short_lines(self):
        long_text = "健康調査票,緊急連絡先カード;写真つきの書類は" * 4 + "4月2日までに提出"
        ics = feed.build_ics([(7, "deadline", "2027-04-02", long_text)])
        self.assertIn("DTSTART;VALUE=DATE:20270402\r\n", ics)
        self.assertIn("DTEND;VALUE=DATE:20270403\r\n", ics)
        self.assertIn("SUMMARY:【締切】", ics)
        self.assertIn("\\,", ics)
        self.assertIn("\\;", ics)
        for line in ics.split("\r\n"):
            self.assertLessEqual(len(line.encode("utf-8")), 75)


if __name__ == "__main__":
    unittest.main()
