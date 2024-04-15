import html
from typing import Callable, Iterable, NamedTuple
from zshzlekey import KeyChord, KeySeq, KeyVariants
from zshzlekeybinding import EscKeySeqGroup, ZshZleKeyBinding

WrapFunction = Callable[[str], str] 

def html_wrap(tag: str, attrs: list[str | tuple[str, str]] = []) -> WrapFunction:
    html_attrs = " " + " ".join(map(lambda attr: 
        f'{attr[0]}="{html.escape(attr[1])}"' if isinstance(attr, tuple) else 
        f"{attr}", attrs)) if attrs else ""
    return lambda v: f"<{tag}{html_attrs}>{v}</{tag}>"

no_wrap: WrapFunction = lambda b: b

class Wrappers(NamedTuple):
    key: WrapFunction = no_wrap
    chord: WrapFunction = no_wrap
    variants: WrapFunction = no_wrap
    sequence: WrapFunction = no_wrap
    escape: WrapFunction = no_wrap
    line: WrapFunction = no_wrap

class Separators(NamedTuple):
    chord: str = " + "
    variants: str = " | "
    sequence: str = ", "
    escape: str = ", "
    line: str = "\n"

class KeysFormatter:

    wrap: Wrappers
    sep: Separators

    def __init__(self, wrap = Wrappers(), sep = Separators()):
        self.wrap = wrap
        self.sep = sep
    
    def format_keychord(self, chord: KeyChord) -> str:
        return self.wrap.chord(self.sep.chord.join(map(self.wrap.key, chord)))

    def format_keyvariants(self, variants: KeyVariants) -> str:
        return self.wrap.variants(self.sep.variants.join(map(self.format_keychord, variants)))

    def format_keyseq(self, keys: KeySeq) -> str:
        seq = self.sep.sequence.join(map(self.format_keyvariants, keys)) if keys else "Unknown key"
        return self.wrap.sequence(seq)

    def format_esckeyseqgroup(self, group: EscKeySeqGroup) -> str:
        line = f"{self.format_keyseq(group.seq)} ({self.sep.escape.join(map(self.wrap.escape, group.esc))})"
        return self.wrap.line(line)

    def format_esckeyseqgroups(self, groups: Iterable[EscKeySeqGroup]) -> str:
        return self.sep.line.join(map(self.format_esckeyseqgroup, groups))
    
    def format_binding_keys(self, binding: ZshZleKeyBinding) -> str:
        return self.format_esckeyseqgroups(binding.keys)