import itertools
import re
from typing import NamedTuple, Optional

KeyChord = tuple[str,...]
KeyVariant = tuple[KeyChord,...]
KeySequence = tuple[KeyVariant,...]

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

modifiers = [
    ("Num Lock", 7),
    ("Caps Lock", 6),
    ("Meta", 5),
    ("Hyper", 4),
    ("Super", 3),
    ("Ctrl", 2),
    ("Alt", 1),
    ("Shift", 0)
]

def kv(*args: list[str]):
    return KeyVariant(map(KeyChord, args)) 

esc = {
    "^M": kv(["Enter"], ["Ctrl", "M"]),
    "^I": kv(["Tab"], ["Ctrl", "I"]),
    "^[[Z": kv(["Shift", "Tab"]),
    "^?": kv(["Backspace"]),
    "^[^?": kv(["Alt", "Backspace"]),
    "^H": kv(["Ctrl", "Backspace"]),
    "^[^H": kv(["Ctrl", "Alt", "Backspace"]),
    "^[^_": kv(["Ctrl", "Alt", "/"]),
    "^_": kv(["Ctrl", "/"]),
    "^[OA": kv(["Up"]),
    "^[OB": kv(["Down"]),
    "^[OC": kv(["Right"]),
    "^[OD": kv(["Left"]),
    "^[OE": kv(["KpBegin"]),
    "^[OF": kv(["End"]),
    "^[OH": kv(["Home"]),
    "^[OP": kv(["F1"]),
    "^[OQ": kv(["F2"]),
    "^[OR": kv(["F3"]),
    "^[OS": kv(["F4"])
}

csi_sequence = r'(?:\^\[\[(?P<csi_key>\d+)?(?:;(?P<csi_mod>\d+))?[\x30-\x3F]*[\x20-\x2F]*(?P<csi_trailer>[\x40-\x7E]))'
char_sequence = r'(?:(?P<alt>\^\[)|(?P<meta>\\M\-))?(?P<ctrl>\^)?(?:\\\\\\(?P<slash>\\)|\\(?P<esc>.)|(?P<char>.))'
esc_sequence = fr"^(?:{csi_sequence}|{char_sequence})"
esc_pattern = re.compile(esc_sequence)

def get_chord_from_match(m: re.Match) -> Optional[KeyChord]:
    if csi_trailer := m["csi_trailer"]:
        csi_key, csi_mod = int(m["csi_key"] or "1"), int(m["csi_mod"] or "1") - 1
        return tuple(
            [mod for mod, bit in modifiers if csi_mod & (1 << bit) != 0] + 
            [key]
        ) if (key := csi.get((csi_key, csi_trailer))) else None
    else:
        ch: str
        return tuple(
            [mod.capitalize() for mod in ["meta", "ctrl", "alt"] if m[mod]] + 
            [next(("Space" if ch == " " else ch.upper() for g in ["slash", "esc", "char"] if (ch := m[g])))]
        )

MatchedKeyChord = NamedTuple("MatchedKeyChord", [("match", re.Match), ("chord", KeyChord)])
def parse_escape_chord(seq: str, partial: bool) -> Optional[MatchedKeyChord]:
    return (MatchedKeyChord(m, chord) if 
        (m := esc_pattern.search(seq) if partial else esc_pattern.fullmatch(seq)) and 
        (chord := get_chord_from_match(m))
    else None)

EscLookup = NamedTuple("EscLookup", [("escape", str), ("variant", KeyVariant)])
def lookup_esc_map(seq: str) -> Optional[EscLookup]:
    while seq:
        if chords := esc.get(seq):
            return EscLookup(seq, chords)
        seq = seq[:-1]
    return None

def parse_escape_sequence(esc: str) -> Optional[KeySequence]:
    result: list[KeyVariant] = []
    while esc:
        if l := lookup_esc_map(esc):
            result.append(l.variant)
            esc = esc[len(l.escape):]
        elif p := parse_escape_chord(esc, True):
            result.append((p.chord,))
            esc = esc[p.match.end():]
        else:
            return None
    return tuple(result)
