from dataclasses import dataclass
from typing import Iterable, Optional
from zshzlebinding import ZshZleBinding
import re 

KeyChord = tuple[str, ...]

@dataclass
class EscapeChord:
    escapes: list[str]
    chords: list[list[str]]

lookup_table = [
    (["^M"], ["Enter"]),
    (["^I"], ["Tab"]),
    (["^?"], ["Backspace", ("Ctrl", "Shift", "/")]),
    (["^H"], [("Ctrl", "Backspace")]),
    
    (["^[[2~"], ["Insert"]),
    (["^[[2;3~"], [("Alt", "Insert")]),
    (["^[[2;5~"], [("Ctrl", "Insert")]),
    (["^[[2;7~"], [("Ctrl", "Alt", "Insert")]),
    
    (["^[[3~"], ["Delete"]),
    (["^[[3;3~"], [("Alt", "Delete")]),
    (["^[[3;4~"], [("Alt", "Shift", "Delete")]),
    (["^[[3;5~"], [("Ctrl", "Delete")]),
    (["^[[3;6~"], [("Ctrl", "Shift", "Delete")]),
    (["^[[3;7~"], [("Ctrl", "Alt", "Delete")]),

    (["^[[5~"], ["PgUp"]),
    (["^[[5;3~"], [("Alt", "PgUp")]),
    (["^[[5;5~"], [("Ctrl", "PgUp")]),
    (["^[[5;6~"], [("Ctrl", "Shift", "PgUp")]),
    (["^[[5;7~"], [("Ctrl", "Alt", "PgUp")]),

    (["^[[6~"], ["PgDown"]),
    (["^[[6;3~"], [("Alt", "PgDown")]),
    (["^[[6;5~"], [("Ctrl", "PgDown")]),
    (["^[[6;7~"], [("Ctrl", "Alt", "PgDown")]),

    (["^[[H"], ["Home"]),
    (["^[[1;3H"], [("Alt", "Home")]),
    (["^[[1;5H"], [("Ctrl", "Home")]),
    (["^[[1;7H"], [("Ctrl", "Alt", "Home")]),

    (["^[[F"], ["End"]),
    (["^[[1;3F"], [("Alt", "End")]),
    (["^[[1;5F"], [("Ctrl", "End")]),
    (["^[[1;7F"], [("Ctrl", "Alt", "End")]),

    (["^[OA", "^[[A"], ["Up"]),
    (["^[OB", "^[[B"], ["Down"]),
    (["^[OC", "^[[C"], ["Right"]),
    (["^[OD", "^[[D"], ["Left"]),
]

lookup_map = { 
    key: frozenset([ chord if isinstance(chord, tuple) else (chord,) for chord in e[1] ]) 
    for e in lookup_table 
    for key in e[0] 
}

csi_sequence = r'(?P<csi>\^\[\[[\x30-\x3F]*[\x20-\x2F]*[\x40-\x7E])'
char_sequence = r'(?P<esc>\^\[)?(?P<ctrl>\^)?)(?:\\\\\\(?P<slash>\\)|\\(?P<escchar>.)|(?P<char>.)'
esc_sequence = fr"^(?:{csi_sequence}|{char_sequence})"
esc_pattern = re.compile(esc_sequence)

def get_chord_by_match(m: Optional[re.Match]) -> Optional[KeyChord]:
    if m and not m["csi"]:
        return tuple([k for k in [
            "Ctrl" if m["ctrl"] else None,
            "Alt" if m["esc"] else None,
            next((m[g] for g in ["slash", "escchar", "char"] if m[g] )).upper()
        ] if k])

def lookup_escape_map(seq: str) -> Optional[str]:
    while seq:
        if seq in lookup_map:
            return seq
        seq = seq[:-1]

def parse_escape_sequence(seq: str) -> list[set[KeyChord]]:
    result = []
    chords = set()
    while seq:
        lookup_seq = lookup_escape_map(seq)
        if lookup_seq: # subsequence found in lookup table
            
            chords.update(lookup_map[lookup_seq])
            lookup_chord = get_chord_by_match(esc_pattern.fullmatch(lookup_seq))
            if lookup_chord:
                chords.add(lookup_chord)
            seq = seq[len(lookup_seq):]

        else:
            parsed_match = esc_pattern.search(seq)
            parsed_chord = get_chord_by_match(parsed_match)
            if parsed_chord:
                chords.add(parsed_chord)
                seq = seq[parsed_match.end():]

        if not chords:
            return None

        if chords:
            result.append(chords)
            chords = set()

    return result


def kbd(key: str):
    return f"<kbd>{key}</kbd>"

def format_bindings(bindings: Iterable[ZshZleBinding]):
    return " | ".join([ kbd(b.key) for b in bindings ])

print( parse_escape_sequence("^[^n") )
print( parse_escape_sequence("n") )
print( parse_escape_sequence("\\\\\\\\") )
print( parse_escape_sequence("^Q") )
print( parse_escape_sequence("^M") )
print( parse_escape_sequence("^[p") )
print( parse_escape_sequence("^[^\\\\\\\\") )
print( parse_escape_sequence("^[[3;5~^M^I") )