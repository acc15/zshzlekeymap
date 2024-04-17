from __future__ import annotations

import enum
import functools
import itertools
import re
from typing import Callable, NamedTuple, Optional

class KeyMod(enum.Flag):
    SHIFT = enum.auto()
    ALT = enum.auto()
    CTRL = enum.auto()
    SUPER = enum.auto()
    HYPER = enum.auto()
    META = enum.auto()
    CAPS_LOCK = enum.auto()
    NUM_LOCK = enum.auto()

    def format_single(self):
        assert len(self) == 1 and self.name is not None
        return " ".join(map(str.capitalize, self.name.split("_")))

    def __lt__(self, other: KeyMod):
        ls, lo = len(self), len(other)
        return self.value < other.value if ls == lo else ls < lo

class KeyChord(NamedTuple):
    
    mods: KeyMod
    key: str

    def __str__(self):
        return self.format()

    def format(self, wrap: Callable[[str], str] = lambda s: s, sep: str = " + "):
        return sep.join(itertools.chain(
            map(lambda mod: wrap(mod.format_single()), reversed(list(self.mods))), 
            (wrap(self.key),)
        ))

KeyVars = tuple[KeyChord,...]
KeySeq = tuple[KeyVars,...]

class EscKeySeq(NamedTuple):
    esc: str
    seq: KeySeq

EscKeySeqs = tuple[EscKeySeq,...]

class MatchedKeyChord(NamedTuple):
    match: re.Match
    chord: KeyChord

class EscLookup(NamedTuple):
    esc: str
    variants: KeyVars

csi = {
    (27, 'u'): "Escape",
    (13, 'u'): "Enter",
    (9, 'u'): "Tab",
    (127, 'u'): "Backspace",
    (2, '~'): "Insert",
    (3, '~'): "Delete",
    (1, 'D'): "Left",
    (1, 'C'): "Right",
    (1, 'A'): "Up",
    (1, 'B'): "Down",
    (5, '~'): "PgUp",
    (6, '~'): "PgDown",
    (1, 'H'): "Home",
    (1, 'F'): "End",
    (1, 'P'): "F1",
    (1, 'Q'): "F2",
    (13, '~'): "F3",
    (1, 'S'): "F4",
    (15, '~'): "F5",
    (17, '~'): "F6",
    (18, '~'): "F7",
    (19, '~'): "F8",
    (20, '~'): "F9",
    (21, '~'): "F10",
    (23, '~'): "F11",
    (24, '~'): "F12",
    (1, 'E'): "KpBegin"
}

def kv(*args: KeyChord):
    return KeyVars(args) 

def kc(*keys: KeyMod | str):
    mod = KeyMod(0)
    key = ""
    for k in keys:
        if isinstance(k, KeyMod):
            mod |= k
        else:
            key = k
    return KeyChord(mod, key)

esc = {
    "^M": kv(kc("Enter"), kc(KeyMod.CTRL, "M")),
    "^I": kv(kc("Tab"), kc(KeyMod.CTRL, "I")),
    "^[[Z": kv(kc(KeyMod.SHIFT, "Tab")),
    "^?": kv(kc("Backspace")),
    "^[^?": kv(kc(KeyMod.ALT, "Backspace")),
    "^H": kv(kc(KeyMod.CTRL, "Backspace")),
    "^[^H": kv(kc(KeyMod.CTRL, KeyMod.ALT, "Backspace")),
    "^[^_": kv(kc(KeyMod.CTRL, KeyMod.ALT, "/")),
    "^_": kv(kc(KeyMod.CTRL, "/")),
    "^[OA": kv(kc("Up")),
    "^[OB": kv(kc("Down")),
    "^[OC": kv(kc("Right")),
    "^[OD": kv(kc("Left")),
    "^[OE": kv(kc("KpBegin")),
    "^[OF": kv(kc("End")),
    "^[OH": kv(kc("Home")),
    "^[OP": kv(kc("F1")),
    "^[OQ": kv(kc("F2")),
    "^[OR": kv(kc("F3")),
    "^[OS": kv(kc("F4"))
}

csi_group = r'(?:\^\[\[(?P<csi_key>\d+)?(?:;(?P<csi_mod>\d+))?[\x30-\x3F]*[\x20-\x2F]*(?P<csi_trailer>[\x40-\x7E]))'
meta_group = r'(?P<meta>\\M\-)'
alt_meta_group = fr'(?:(?P<alt>\^\[)|{meta_group})'
char_group = r'(?:\\\\\\(?P<slash>\\)|\\(?P<esc>.)|(?P<char>.))'
ctrl_char_group = fr'(?P<ctrl>\^)?{char_group}'

esc_pattern = re.compile(fr'^(?:{csi_group}|(?:{alt_meta_group}?{ctrl_char_group}))')
char_pattern = re.compile(fr'^{meta_group}?{ctrl_char_group}')

def get_char_from_match(m: re.Match) -> str:
    return next(ch for g in ["slash", "esc", "char"] if (ch := m[g]))

def get_chord_from_match(m: re.Match) -> Optional[KeyChord]:
    if csi_trailer := m["csi_trailer"]:
        csi_key, csi_mod = int(m["csi_key"] or "1"), KeyMod(int(m["csi_mod"] or "1") - 1)
        key = csi.get((csi_key, csi_trailer))
        return KeyChord(csi_mod, key) if key else None
    else:
        groups = m.groupdict()
        mods = (mod for mod in KeyMod if mod.name and groups.get(mod.name.lower()))
        return KeyChord(
            functools.reduce(lambda a, b: a | b, mods, KeyMod(0)),
            "Space" if (ch := get_char_from_match(m)) == " " else ch.upper()
        )

def parse_keychord(seq: str, partial: bool) -> Optional[MatchedKeyChord]:
    return (MatchedKeyChord(m, chord) if 
        (m := esc_pattern.search(seq) if partial else esc_pattern.fullmatch(seq)) and 
        (chord := get_chord_from_match(m))
    else None)

def lookup_esc_map(seq: str) -> Optional[EscLookup]:
    while seq:
        if chords := esc.get(seq):
            return EscLookup(seq, chords)
        seq = seq[:-1]
    return None

def parse_keyseq(esc: str) -> KeySeq:
    result: list[KeyVars] = []
    while esc:
        if l := lookup_esc_map(esc):
            result.append(l.variants)
            esc = esc[len(l.esc):]
        elif p := parse_keychord(esc, True):
            result.append((p.chord,))
            esc = esc[p.match.end():]
        else:
            return KeySeq() # empty tuple if can't parse
    return KeySeq(result)

def parse_char_esc(esc: str) -> Optional[int]:
    if m := char_pattern.fullmatch(esc):
        meta, ctrl, char = m["meta"] and 0x80 or 0, m["ctrl"] and 0x40 or 0, get_char_from_match(m)
        return (0x7F if ctrl and char == '?' else ord(char) - ctrl) | meta 
    else:
        return None

chars_to_escape = frozenset(['^', '`', '"', '$', '\\'])

def format_char_esc(code: int) -> str:
    esc = ""
    if code & 0x80:
        code -= 0x80
        esc += "\\M-"

    if code == 0x7F:
        return esc + "^?"
    
    if code < 0x20:
        code += 0x40
        esc += "^"
    
    ch = chr(code)
    if ch in chars_to_escape:
        esc += "\\"
    
    if ch == '\\':
        esc += "\\\\"
        
    esc += ch
    return esc

def parse_esckeyseq(esc_first: str, esc_last: Optional[str]) -> EscKeySeqs:
    if not esc_last:
        return (EscKeySeq(esc_first, parse_keyseq(esc_first)),)
    
    start, end = parse_char_esc(esc_first), parse_char_esc(esc_last)
    if start is None or end is None:
        return (EscKeySeq(f'"{esc_first}"-"{esc_last}"', KeySeq()),)
    
    return tuple(EscKeySeq(esc := format_char_esc(code), parse_keyseq(esc)) for code in range(start, end + 1))