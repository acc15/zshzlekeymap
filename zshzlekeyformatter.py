import html
import itertools
from operator import attrgetter
from typing import Callable, Iterable, NamedTuple, Optional
from zshzlekey import KeyChord, KeySequence, KeyVariant
from zshzlekeybinding import ZshZleKeyBinding

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
    
    def format_chord(self, chord: KeyChord) -> str:
        return self.wrap.chord(self.sep.chord.join(map(self.wrap.key, chord)))

    def format_variants(self, variants: KeyVariant) -> str:
        return self.wrap.variants(self.sep.variants.join(map(self.format_chord, variants)))

    def format_keys(self, keys: Optional[KeySequence]) -> str:
        return self.wrap.sequence(self.sep.sequence.join(map(self.format_variants, keys)) if keys else "Unknown key")

    def format_keys_with_escapes(self, keys: Optional[KeySequence], escapes: Iterable[str]) -> str:
        return self.wrap.line(f"{self.format_keys(keys)} ({self.sep.escape.join(map(self.wrap.escape, escapes))})")

    def format_binding_keys(self, bindings: Iterable[ZshZleKeyBinding]) -> str:
        return self.sep.line.join((
            self.format_keys_with_escapes(keys, map(attrgetter("escape"), keys_bindings)) 
            for keys, keys_bindings in itertools.groupby(bindings, key=attrgetter("keys")) 
        ))