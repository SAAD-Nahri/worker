from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from source_engine.cleaner import clean_text, word_count


class CleanerTests(unittest.TestCase):
    def test_clean_text_strips_html_and_normalizes_whitespace(self) -> None:
        value = "<p>Hello&nbsp;&nbsp;<strong>world</strong></p>\n<div> again </div>"
        self.assertEqual(clean_text(value), "Hello world again")

    def test_word_count_uses_cleaned_text(self) -> None:
        value = "<p>Hello <strong>world</strong> again</p>"
        self.assertEqual(word_count(value), 3)


if __name__ == "__main__":
    unittest.main()
