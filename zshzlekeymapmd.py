from dataclasses import dataclass
import itertools
from operator import attrgetter
import os
import textwrap
from typing import Iterable, Optional

from zshzlebinding import ZshZleAction
from zshzlekey import KeyChord, KeySequence, KeyVariant
from zshzlekeybinding import ZshZleKeyBinding, get_zshzle_key_bindings

def format_key(key: str):
    return f"<kbd>{key}</kbd>"

def format_esc(esc: str):
    return f"`{esc}`"

def format_chord(chord: KeyChord) -> str:
    return "+".join(map(format_key, chord))

def format_variants(variants: KeyVariant) -> str:
    return " | ".join(map(format_chord, variants))

def format_sequence(seq: Optional[KeySequence]) -> str:
    return ", ".join(map(format_variants, seq)) if seq else "Unknown key"

def format_key_sequence(key_sequence: Optional[KeySequence], escapes: Iterable[str]) -> str:
    return f"* {format_sequence(key_sequence)} ({', '.join(map(format_esc, escapes))})"

def format_binding_keys(bindings: Iterable[ZshZleKeyBinding]) -> str:
    return "\n".join((
        format_key_sequence(key_sequence, map(attrgetter("escape"), key_bindings)) 
        for key_sequence, key_bindings in itertools.groupby(bindings, key=attrgetter("keys")) 
    ))

def generate_md():
    
    bindings = sorted(get_zshzle_key_bindings(), key = attrgetter("desc.section", "action", "keys"))
    sections: dict[str, dict[ZshZleAction, list[ZshZleKeyBinding]]] = {
        section: {
            action: list(group_bindings)
            for action, group_bindings in itertools.groupby(section_bindings, key = attrgetter("action"))
        }
        for section, section_bindings in itertools.groupby(bindings, key = attrgetter("desc.section"))
    }

    with open("keys.md", "w") as f:
        f.write("# ZshZle bindings")

        f.write("\n\n## TOC\n")
        for section in sections:
            f.write(f"\n1. [{section}](<#{section}>)")

        for section, actions in sections.items():
            f.write(f"\n\n## {section}")
            for action, bindings in actions.items():
                f.write(f"\n\n### `{action.text}`")
                f.write(f"\n\n### Keys\n{format_binding_keys(bindings)}")
                if description := bindings[0].desc.description:
                    f.write(f"\n\n### Description\n{os.linesep.join(textwrap.wrap(description, 120))}")
                f.write("\n\n---")

generate_md()