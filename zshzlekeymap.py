#!/bin/python

from dataclasses import dataclass
from typing import Iterable
import textwrap
import os

from zshzlebinding import ZshZleBinding, ZshZleBindingType, get_zshzle_bindings
from zshzleman import ZshZleWidget, parse_zshzle_standard_widgets

widgets = parse_zshzle_standard_widgets()
bindings = get_zshzle_bindings()

@dataclass(frozen=True)
class ZshZleAction:
    type: ZshZleBindingType
    text: str

widget_map = { c.widget: c for c in widgets }
binding_map: dict[ZshZleAction, list[ZshZleBinding]] = {}

for b in bindings:
    if b.type == ZshZleBindingType.WIDGET and b.text == "self-insert":
        continue
    action = ZshZleAction(b.type, b.text)
    if action in binding_map:
        binding_map[action].append(b)
    else:
        binding_map[action] = [b]

def format_bindings(bindings: Iterable[ZshZleBinding]):
    return " | ".join([ f"<kbd>{b.key}</kbd>" for b in bindings ])

with open("keys.md", "w") as f:
    f.write("# ZshZle binding")
    for (action, bindings) in binding_map.items():
        f.write(f"\n\n## {format_bindings(bindings)}")
        match action.type:
            case ZshZleBindingType.WIDGET:
                widget_desc = widget_map.get(
                    action.text, 
                    ZshZleWidget(section="Unknown", widget=action.text, description="!!! No description !!!"))
                f.write(f"\n\nWidget: `{widget_desc.widget}`")
                f.write(f"\n\n{os.linesep.join(textwrap.wrap(widget_desc.description, 120))}")
            case ZshZleBindingType.COMMAND:
                f.write(f"\n\nCommand: `{action.text}`")

