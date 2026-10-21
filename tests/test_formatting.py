import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from linkedin_automation import SPACER, normalize_spacing, validate

class TestFormatting(unittest.TestCase):
    def test_spacer(self):
        self.assertEqual(normalize_spacing("Hello\n\nWorld"), f"Hello\n{SPACER}\nWorld")

    def test_no_double_spacers(self):
        self.assertEqual(normalize_spacing("Hello\n\n\nWorld"), f"Hello\n{SPACER}\nWorld")

    def test_reject_duplicate_topics(self):
        caption = ("A specific marketing insight. " * 15) + "\n#Growth #Marketing #Leadership"
        plan = {"posts": [
            {"day": "Tuesday", "topic": "Same", "caption": caption, "graphic_concept": "A diagram"},
            {"day": "Thursday", "topic": "Same", "caption": caption, "graphic_concept": "A diagram"}
        ]}
        self.assertTrue(any("repeated" in x for x in validate(plan, [])))

if __name__ == "__main__":
    unittest.main()
