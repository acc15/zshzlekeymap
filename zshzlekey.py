from dataclasses import dataclass
from typing import Iterable, Optional
import re

from groupby import groupby 

KeyChord = tuple[str,...]
KeyVariant = frozenset[KeyChord]
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

csi_mod_bits = {
    7: "Num Lock",
    6: "Caps Lock",
    5: "Meta",
    4: "Hyper",
    3: "Super",
    2: "Ctrl",
    1: "Alt",
    0: "Shift"
}

esc = {
    "^M": [["Enter"], ["Ctrl", "M"]],
    "^I": [["Tab"], ["Ctrl", "I"]],
    "^[[Z": [["Shift", "Tab"]],
    "^?": [["Backspace"]],
    "^[^?": [["Alt", "Backspace"]],
    "^H": [["Ctrl", "Backspace"]],
    "^[^H": [["Ctrl", "Alt", "Backspace"]],
    "^[^_": [["Ctrl", "Alt", "/"]],
    "^_": [["Ctrl", "/"]],
    "^[OA": [["Up"]],
    "^[OB": [["Down"]],
    "^[OC": [["Right"]],
    "^[OD": [["Left"]],
    "^[OE": [["KpBegin"]],
    "^[OF": [["End"]],
    "^[OH": [["Home"]],
    "^[OP": [["F1"]],
    "^[OQ": [["F2"]],
    "^[OR": [["F3"]],
    "^[OS": [["F4"]]
}

csi_sequence = r'(?:\^\[\[(?P<csi_key>\d+)?(?:;(?P<csi_mod>\d+))?[\x30-\x3F]*[\x20-\x2F]*(?P<csi_trailer>[\x40-\x7E]))'
char_sequence = r'(?:(?P<esc>\^\[)?(?P<ctrl>\^)?)(?:\\\\\\(?P<slash>\\)|\\(?P<escchar>.)|(?P<char>.))'
esc_sequence = fr"^(?:{csi_sequence}|{char_sequence})"
esc_pattern = re.compile(esc_sequence)

@dataclass
class MatchedKeyChord:
    match: re.Match
    chord: KeyChord

def parse_escape_chord(seq: str, partial: bool) -> Optional[MatchedKeyChord]:
    m = esc_pattern.search(seq) if partial else esc_pattern.fullmatch(seq)
    if not m:
        return None

    csi_trailer = m["csi_trailer"]

    if not csi_trailer:
        return MatchedKeyChord(m, tuple(filter(None, (
            "Ctrl" if m["ctrl"] else None,
            "Alt" if m["esc"] else None,
            next(("Space" if ch == " " else ch.upper() for g in ["slash", "escchar", "char"] if (ch := m[g]) )
        )))))

    csi_key = int(m["csi_key"] or "1")
    csi_mod = int(m["csi_mod"] or "0")
    key = csi.get((csi_key, csi_trailer), None)
    if not key:
        return None
    
    mods = [ mod for mod_bit, mod in csi_mod_bits.items() if csi_mod and (csi_mod - 1) & (1 << mod_bit) != 0 ] 
    return MatchedKeyChord(m, tuple(mods + [ key ]))
    
@dataclass
class EscLookup:
    seq: str
    chords: list[list[str]]

def lookup_esc_map(seq: str) -> Optional[EscLookup]:
    while seq:
        chords = esc.get(seq, None)
        if chords:
            return EscLookup(seq, chords)
        seq = seq[:-1]

def parse_escape_sequence(seq: str) -> Optional[KeySequence]:
    result = []
    while seq:
        esc_lookup = lookup_esc_map(seq)
        if esc_lookup: # subsequence found in lookup table
            result.append(frozenset([ tuple(chord) for chord in esc_lookup.chords]))
            seq = seq[len(esc_lookup.seq):]
        else:
            if not (p := parse_escape_chord(seq, True)):
                return None
            result.append(frozenset((p.chord,)))
            seq = seq[p.match.end():]
    return tuple(result)

def format_key(key: str):
    return f"<kbd>{key}</kbd>"

def format_esc(esc: str):
    return f"`{esc}`"

def format_chord(chord: KeyChord) -> str:
    return "+".join(map(format_key, chord))

def format_variants(variants: KeyVariant) -> str:
    return " | ".join(map(format_chord, variants))

def format_sequence(seq: Optional[KeySequence]) -> str:
    if seq:
        return ", ".join(map(format_variants, seq))
    else:
        return "Unknown key"

def format_binding(seq: Optional[KeySequence], escapes: Iterable[str]) -> str:
    return f"* {format_sequence(seq)} ({', '.join(map(format_esc, escapes))})"

def format_escapes(escapes: Iterable[str]) -> str:
    grouped_keys = groupby(escapes, key=parse_escape_sequence)
    return "\n".join([ format_binding(seq, esc) for seq, esc in grouped_keys ])
