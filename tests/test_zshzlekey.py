import unittest

import zshzlekey

class ZshZleKeyTests(unittest.TestCase):
    def test_parse_escape_chord(self):
        examples = [
            ("\\M-^@", ("Meta", "Ctrl", "@")),
            ("^[d", ("Alt", "D")),
        ]
        for esc, expected_chord in examples:
            with self.subTest(esc = esc):
                m = zshzlekey.parse_escape_chord(esc, False)
                self.assertEqual(m.chord, expected_chord) if m else self.assertIsNone(expected_chord)
