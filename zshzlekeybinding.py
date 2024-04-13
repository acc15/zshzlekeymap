
from dataclasses import dataclass
from typing import Iterator, Optional

from zshzlebinding import ZshZleAction, ZshZleBinding, get_zshzle_bindings
from zshzlekey import KeySequence, parse_escape_sequence
from zshzlewidget import ZshZleDescriptor, get_zshzle_widgets

@dataclass
class ZshZleKeyBinding:
    action: ZshZleAction
    """binding action, command or widget"""

    escape: str
    """escape sequence of binding"""
    
    keys: Optional[KeySequence]
    """detected key binding"""

    desc: ZshZleDescriptor
    """descriptor"""

def skip_binding(b: ZshZleAction) -> bool:
    return not b.command and (b.text == "self-insert" or b.text.startswith("_"))

def get_zshzle_action_desc(action: ZshZleAction, widgets: dict[str, ZshZleDescriptor]) -> ZshZleDescriptor:
    return ZshZleDescriptor("Command", "") if action.command else widgets.get(action.text, ZshZleDescriptor("Unknown", "!!! NO DESCRIPTION !!!"))

def make_zshzle_key_binding(binding: ZshZleBinding, widgets: dict[str, ZshZleDescriptor]) -> ZshZleKeyBinding:
    return ZshZleKeyBinding(
        binding.action, 
        binding.key, 
        parse_escape_sequence(binding.key), 
        get_zshzle_action_desc(binding.action, widgets)
    )

def get_zshzle_key_bindings() -> Iterator[ZshZleKeyBinding]:
    widgets = get_zshzle_widgets()
    return map(
        lambda b: make_zshzle_key_binding(b, widgets), 
        filter(lambda b: not skip_binding(b.action), get_zshzle_bindings())
    )
