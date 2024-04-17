import html
from typing import Callable, Iterable, NamedTuple, Optional
from zshzlekey import KeyChord, KeySeq, KeyVars
from zshzlekeybinding import EscKeySeqGroup, ZshZleKeyBinding

WrapFunction = Callable[[str], str] 

def html_wrap(tag: str, attrs: dict[str, Optional[str]] = {}) -> WrapFunction:
    html_attrs = " " + " ".join(
        f'{name}="{html.escape(value)}"' if value is not None else name 
        for name, value in attrs.items()
    ) if attrs else ""
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
    key: str = " + "
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
    
    def keychord(self, chord: KeyChord) -> str:
        return self.wrap.chord(chord.format(self.wrap.key, self.sep.key))

    def keyvars(self, variants: KeyVars) -> str:
        return self.wrap.variants(self.sep.variants.join(map(self.keychord, variants)))

    def keyseq(self, keys: KeySeq) -> str:
        seq = self.sep.sequence.join(map(self.keyvars, keys)) if keys else "Unknown key"
        return self.wrap.sequence(seq)

    def esckeyseqgroup(self, group: EscKeySeqGroup) -> str:
        line = f"{self.keyseq(group.seq)} ({self.sep.escape.join(map(self.wrap.escape, group.esc))})"
        return self.wrap.line(line)

    def esckeyseqgroups(self, groups: Iterable[EscKeySeqGroup]) -> str:
        return self.sep.line.join(map(self.esckeyseqgroup, groups))
    
    def binding_keys(self, binding: ZshZleKeyBinding) -> str:
        return self.esckeyseqgroups(binding.keys)