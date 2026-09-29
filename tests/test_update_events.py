import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import update_events


class UpdateEventsTests(unittest.TestCase):
    def test_pages_are_filtered_sorted_and_deduplicated(self):
        event = {"id": 959045, "name": "Critical Hit Freshers Event 2026", "startAt": 1790866800,
                 "slug": "tournament/critical-hit-freshers-event-2026"}
        later = {"id": 3, "name": "Honeycomb", "startAt": 1791000000, "slug": "tournament/honeycomb"}
        other = {"id": 4, "name": "Unrelated", "startAt": 1790000000, "slug": "tournament/other"}
        pages = [
            {"nodes": [later, other, event], "pageInfo": {"totalPages": 2}},
            {"nodes": [event], "pageInfo": {"totalPages": 2}},
        ]
        with tempfile.TemporaryDirectory() as directory, patch.object(update_events, "OUTPUT", Path(directory) / "events.json"), \
                patch.dict(os.environ, {"START_GG_TOKEN": "test"}), \
                patch.object(update_events, "fetch_page", side_effect=pages) as fetch:
            update_events.main()
            self.assertEqual(json.loads(update_events.OUTPUT.read_text()), [event, later])
            self.assertEqual(fetch.call_count, 2)

    def test_failed_page_keeps_existing_snapshot(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(update_events, "OUTPUT", Path(directory) / "events.json"), \
                patch.dict(os.environ, {"START_GG_TOKEN": "expired"}), \
                patch.object(update_events, "fetch_page", side_effect=RuntimeError("Token has expired")):
            update_events.OUTPUT.write_text('[{"existing": true}]\n')
            with self.assertRaisesRegex(RuntimeError, "expired"):
                update_events.main()
            self.assertEqual(update_events.OUTPUT.read_text(), '[{"existing": true}]\n')


if __name__ == "__main__":
    unittest.main()
