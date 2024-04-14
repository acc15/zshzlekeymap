from dataclasses import dataclass
import itertools
from operator import attrgetter
from typing import Iterable, Optional

from zshzlebinding import ZshZleAction
from zshzlekey import KeyChord, KeySequence, KeyVariant
from zshzlekeybinding import ZshZleKeyBinding, get_zshzle_key_bindings

def format_key(key: str):
    return f"<kbd>{key}</kbd>"

def format_esc(esc: str):
    return f"<code>{esc}</code>"

def format_chord(chord: KeyChord) -> str:
    return "+".join(map(format_key, chord))

def format_variants(variants: KeyVariant) -> str:
    return " | ".join(map(format_chord, variants))

def format_sequence(keys: Optional[KeySequence]) -> str:
    return ", ".join(map(format_variants, keys)) if keys else "Unknown key"

def format_key_sequence(keys: Optional[KeySequence], escapes: Iterable[str]) -> str:
    return f"<div>{format_sequence(keys)} ({', '.join(map(format_esc, escapes))})</div>"

def format_binding_keys(bindings: Iterable[ZshZleKeyBinding]) -> str:
    return "".join((
        format_key_sequence(key_sequence, map(attrgetter("escape"), key_bindings)) 
        for key_sequence, key_bindings in itertools.groupby(bindings, key=attrgetter("keys")) 
    ))

def generate_html():
    
    bindings = sorted(get_zshzle_key_bindings(), key = attrgetter("desc.section", "action", "keys"))
    print(*bindings, sep="\n")

    with open("keys.html", "w") as f:
        f.write(
            "<!DOCTYPE html><html><head>"
            "<title>ZshZle bindings</title>"
            "<style>"
            "html,body { font-family: Intel, Helvetica, sans-serif; }"
            "table,th,td { border: 1px solid black; }"
            "table { width: 100%; border-collapse: collapse; }"
            "h4 { margin: 0; }"
            "</style></head><body><table>"
            "<thead><tr><th>Keys</th><th>Action</th><th>Description</th></thead>"
            "<tbody>"
        )

        for section, section_bindings in itertools.groupby(bindings, key = attrgetter("desc.section")):
            f.write(f'<tr><td colspan="3"><h4>{section}</h4></td></tr>')

            action: ZshZleAction
            for action, action_bindings in itertools.groupby(section_bindings, key = attrgetter("action")):
                b = list(action_bindings)
                f.write('<tr>'
                        f'<td>{format_binding_keys(b)}</td>'
                        f'<td><code>{action.text}</code></td>'
                        f'<td>{b[0].desc.description}</td>'
                        '</tr>')

        f.write("</tbody></table></body></html>")


generate_html()