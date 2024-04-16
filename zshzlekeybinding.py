
from dataclasses import dataclass
import itertools
from typing import Iterable, NamedTuple

from more_itertools import flatten

from zshzlebinding import ZshZleAction, ZshZleBinding, get_zshzle_bindings
from zshzlekey import EscKeySeq, KeySeq, parse_esckeyseq
from zshzlewidget import ZshZleDescriptor, get_zshzle_widgets

class ZshZleDescBinding(NamedTuple):
    binding: ZshZleBinding
    desc: ZshZleDescriptor

class EscKeySeqGroup(NamedTuple):
    seq: KeySeq
    esc: tuple[str, ...]

class ZshZleKeyBinding(NamedTuple):
    action: ZshZleAction
    desc: ZshZleDescriptor
    keys: tuple[EscKeySeqGroup, ...]

def skip_binding(b: ZshZleAction) -> bool:
    return (b.text == "self-insert" or b.text.startswith("_")) and not b.command 

command_action_desc = ZshZleDescriptor("Commands", "")
default_action_desc = ZshZleDescriptor("Unknown", "!!! NO DESCRIPTION !!!")

def get_zshzle_action_desc(action: ZshZleAction, widgets: dict[str, ZshZleDescriptor]) -> ZshZleDescriptor:
    return command_action_desc if action.command else widgets.get(action.text, default_action_desc)

def make_zshzle_key_binding(group: Iterable[ZshZleDescBinding]) -> ZshZleKeyBinding:
    
    bindings = list(group)
    binding, desc = bindings[0]

    def esckeyseq_key(k: EscKeySeq):
        return k.seq

    keys = sorted(
        flatten(map(lambda b: parse_esckeyseq(b.binding.key, b.binding.key_end), bindings )), 
        key = esckeyseq_key
    )

    key_groups = tuple((
        EscKeySeqGroup(seq, tuple((seq.esc for seq in group))) 
        for seq, group in itertools.groupby(keys, key = esckeyseq_key)
    ))

    return ZshZleKeyBinding(binding.action, desc, key_groups)

def get_zshzle_key_bindings() -> Iterable[ZshZleKeyBinding]:
    widgets = get_zshzle_widgets()

    def binding_sort_key(t: ZshZleDescBinding):
        return (t.desc.section, t.binding.action)

    desc_bindings = sorted([
        ZshZleDescBinding(b, get_zshzle_action_desc(b.action, widgets))
        for b in get_zshzle_bindings() 
        if not skip_binding(b.action)
    ], key = binding_sort_key)

    return (make_zshzle_key_binding(group) for _, group in itertools.groupby(desc_bindings, key = binding_sort_key))
