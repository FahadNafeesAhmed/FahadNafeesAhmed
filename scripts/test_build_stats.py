"""Check that profile charts preserve and label GitHub data correctly."""

import datetime as dt
import json
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import build_stats as charts


class ChartTests(unittest.TestCase):
    def test_calendar_parses_reordered_attributes_and_zero_days(self):
        start = dt.date(2025, 1, 1)
        html = "".join(
            f'<td id="day-{i}" data-date="{start + dt.timedelta(days=i)}"></td>'
            f'<tool-tip for="day-{i}">{"1,234 contributions" if i == 0 else "No contributions"} on this day.</tool-tip>'
            for i in range(365)
        )
        with patch.object(charts, "get", return_value=html):
            days = charts.contributions()
        self.assertEqual(len(days), 365)
        self.assertEqual(sum(count for _, count in days), 1234)
        with patch.object(charts, "get", return_value=html.replace("1,234 contributions", "Unknown count")):
            with self.assertRaises(ValueError):
                charts.contributions()

    def test_incomplete_calendar_is_rejected(self):
        with patch.object(charts, "get", return_value="<html></html>"):
            with self.assertRaises(ValueError):
                charts.contributions()

    def test_language_pagination_filters_and_equal_weight(self):
        fork = {"fork": True, "name": "fork"}
        profile = {"fork": False, "name": charts.USER}
        first = [fork] * 98 + [profile, {"fork": False, "name": "a", "languages_url": "langs-a"}]
        second = [{"fork": False, "name": "b", "languages_url": "langs-b"},
                  {"fork": False, "name": "empty", "languages_url": "langs-empty"}]
        responses = [first, second, {"Python": 1000}, {"TypeScript": 10}, {}]
        with patch.object(charts, "get", side_effect=[json.dumps(item) for item in responses]) as get:
            count, share = charts.repos_and_languages()
        self.assertEqual(count, 3)
        self.assertEqual(dict(share), {"Python": 1.0, "TypeScript": 1.0})
        self.assertIn("page=2", get.call_args_list[1].args[0])

    def test_svg_valid_for_zero_activity_and_no_languages(self):
        today = dt.date(2026, 9, 24)
        days = [(today - dt.timedelta(days=i), 0) for i in reversed(range(365))]
        for content in (charts.stats_card(days, 0, today), charts.languages_card([], today), charts.stack_card()):
            ET.fromstring(content)
            self.assertNotIn("animation:", content)
            self.assertNotIn("nan", content.lower())

    def test_language_overflow_is_grouped_as_other(self):
        share = [(f"Language {i}", 1) for i in range(8)]
        svg = charts.languages_card(share, dt.date(2026, 9, 24))
        ET.fromstring(svg)
        self.assertIn("Other: 37.5%", svg)


if __name__ == "__main__":
    unittest.main()
