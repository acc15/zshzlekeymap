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

esc_map = { seq: tuple((tuple(chord) for chord in variants)) for seq, variants in esc.items() }

csi_sequence = r'(?:\^\[\[(?P<csi_key>\d+)?(?:;(?P<csi_mod>\d+))?[\x30-\x3F]*[\x20-\x2F]*(?P<csi_trailer>[\x40-\x7E]))'
char_sequence = r'(?:(?P<esc>\^\[)?(?P<ctrl>\^)?)(?:\\\\\\(?P<slash>\\)|\\(?P<escaped_char>.)|(?P<char>.))'
esc_sequence = fr"^(?:{csi_sequence}|{char_sequence})"
esc_pattern = re.compile(esc_sequence)

def get_chord_from_match(m: re.Match) -> Optional[KeyChord]:
    if csi_trailer := m["csi_trailer"]:
        csi_key, csi_mod = int(m["csi_key"] or "1"), int(m["csi_mod"] or "0")
        if key := csi.get((csi_key, csi_trailer)):
            return tuple(
                [ mod for mod_bit, mod in csi_mod_bits.items() if csi_mod > 0 and (csi_mod - 1) & (1 << mod_bit) != 0 ] + 
                [ key ]
            )
    else:
        ch: str
        return tuple(filter(None, (
            m["ctrl"] and "Ctrl",
            m["esc"] and "Alt",
            next(("Space" if ch == " " else ch.upper() for g in ["slash", "escaped_char", "char"] if (ch := m[g]) )
        ))))

MatchedKeyChord = NamedTuple("MatchedKeyChord", [("match", re.Match), ("chord", KeyChord)])
def parse_escape_chord(seq: str, partial: bool) -> Optional[MatchedKeyChord]:
    if (m := esc_pattern.search(seq) if partial else esc_pattern.fullmatch(seq)) and (chord := get_chord_from_match(m)):
        return MatchedKeyChord(m, chord)

EscLookup = NamedTuple("EscLookup", [("seq", str), ("chords", list[KeyChord])])
def lookup_esc_map(seq: str) -> Optional[EscLookup]:
    while seq:
        if chords := esc_map.get(seq):
            return EscLookup(seq, chords)
        seq = seq[:-1]

def parse_escape_sequence(seq: str) -> Optional[KeySequence]:
    result: list[KeyVariant] = []
    while seq:
        if l := lookup_esc_map(seq):
            result.append(l.chords)
            seq = seq[len(l.seq):]
        elif p := parse_escape_chord(seq, True):
            result.append((p.chord,))
            seq = seq[p.match.end():]
        else:
            return None
    return tuple(result)
