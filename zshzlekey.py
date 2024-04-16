import re
from typing import NamedTuple, Optional

KeyChord = tuple[str,...]
KeyVariants = tuple[KeyChord,...]
KeySeq = tuple[KeyVariants,...]

class EscKeySeq(NamedTuple):
    esc: str
    seq: KeySeq

EscKeySeqs = tuple[EscKeySeq,...]

class MatchedKeyChord(NamedTuple):
    match: re.Match
    chord: KeyChord

class EscLookup(NamedTuple):
    esc: str
    variants: KeyVariants

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
    return KeyVariants(map(KeyChord, args)) 

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
        csi_key, csi_mod = int(m["csi_key"] or "1"), int(m["csi_mod"] or "1") - 1
        return tuple(
            [mod for mod, bit in modifiers if csi_mod & (1 << bit) != 0] + 
            [key]
        ) if (key := csi.get((csi_key, csi_trailer))) else None
    else:
        return tuple(
            [mod.capitalize() for mod in ["meta", "ctrl", "alt"] if m[mod]] + 
            ["Space" if (ch := get_char_from_match(m)) == " " else ch.upper()]
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
    result: list[KeyVariants] = []
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
