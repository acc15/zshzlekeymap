from dataclasses import dataclass
import itertools
import os
import textwrap
from typing import Iterable, Optional

from groupby import groupby
from zshzlebinding import ZshZleBinding, get_zshzle_bindings
from zshzlekey import KeyChord, KeySequence, KeyVariant, parse_escape_sequence
from zshzlewidget import ZshZleWidget, parse_zshzle_widgets

@dataclass(frozen=True)
class ZshZleAction:
    command: bool
    text: str

def skip_binding(b: ZshZleBinding) -> bool:
    return not b.command and (b.text == "self-insert" or b.text.startswith("_"))

def get_binding_section(b: ZshZleBinding, widgets: dict[str, ZshZleWidget]) -> str:
    return "Commands" if b.command else (w := widgets.get(b.text)) and w.section or "Unknown"

def get_action_description(a: ZshZleAction, widgets: dict[str, ZshZleWidget]) -> Optional[str]:
    return None if a.command else (w := widgets.get(a.text)) and w.description or "!!! NO DESCRIPTION !!!"

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

def generate_md():
    
    widgets = parse_zshzle_widgets()
    
    sections = { 
        section: {
            action: list(map(lambda b: b.key, group_bindings))
            for action, group_bindings in sorted(groupby(
                section_bindings, 
                lambda b: ZshZleAction(b.command, b.text)
            ), key = lambda k: k[0].text)
        }
        for section, section_bindings in sorted(groupby(
            itertools.filterfalse(skip_binding, get_zshzle_bindings()), 
            lambda b: get_binding_section(b, widgets)
        ), key = lambda k: k[0])
    }

    with open("keys.md", "w") as f:
        f.write("# ZshZle bindings")

        f.write("\n\n## TOC\n")
        for section in sections:
            f.write(f"\n1. [{section}](<#{section}>)")

        for section, actions in sections.items():
            f.write(f"\n\n## {section}")
            for action, escapes in actions.items():
                f.write(f"\n\n### `{action.text}`")
                f.write(f"\n\n### Keys\n{format_escapes(escapes)}")
                description = get_action_description(action, widgets)
                if description:
                    f.write(f"\n\n### Description\n{os.linesep.join(textwrap.wrap(description, 120))}")
                f.write("\n\n---")

generate_md()