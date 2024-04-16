import subprocess
import unittest

from zshzlebinding import parse_zshzle_binding
import zshzlekey

class ZshZleKeyTests(unittest.TestCase):
    def test_parse_escape_chord(self):
        examples = [
            ("\\M-^@", ("Meta", "Ctrl", "@")),
            ("^[d", ("Alt", "D")),
        ]
        for esc, chord in examples:
            with self.subTest(esc = esc, chord = chord):
                r = zshzlekey.parse_keychord(esc, False)
                self.assertEqual(r.chord, chord) if r is not None else self.assertIsNone(chord)

    def get_bindkey_escape(self, code: int) -> str:
        km = "test"
        return parse_zshzle_binding(subprocess.run(
            ["zsh", "-c", f"bindkey -N {km} && bindkey -M {km} -s '\\x{code:0x}' '' && bindkey -M {km}"], 
            capture_output=True, 
            text=True, 
            encoding="utf-8"
        ).stdout.strip()).key

    def test_parse_char_esc(self):
        for code in range(0x100):
            esc = self.get_bindkey_escape(code)
            with self.subTest(esc = esc, code = code):
                r = zshzlekey.parse_char_esc(esc)
                self.assertEqual(code, r) if r is not None else self.assertIsNone(code)

    def test_format_char_esc(self):
        for code in range(0x100):
            esc = self.get_bindkey_escape(code)
            with self.subTest(code = code, esc = esc):
                r = zshzlekey.format_char_esc(code)
                self.assertEqual(esc, r) if r is not None else self.assertIsNone(esc)

