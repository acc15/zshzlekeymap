from dataclasses import dataclass, field
from typing import Optional
import subprocess
from enum import Enum, auto
import typing

class ZshZleBindingType(Enum):
    WIDGET = auto()
    COMMAND = auto()

@dataclass
class ZshZleBinding:
    key: str
    key_end: Optional[str]
    text: str
    type: ZshZleBindingType

class CharIter:
    value: str
    pos: int
    
    def __init__(self, s: str, p: int = 0):
        self.value = s
        self.pos = p

    def has_next(self):
        return self.pos < len(self.value)

    def peek(self):
        return self.value[self.pos : self.pos + 1]
    
    def skip(self, amount: int = 1):
        self.pos += amount

    def next(self):
        res = self.peek()
        self.pos += 1
        return res
    
    def remainder(self):
        return self.value[self.pos:]

def parse_quoted_string(it: CharIter) -> str:
    assert it.next() == '"'
    start_pos = it.pos
    next_escape = False
    while ch := it.next():
        if next_escape:
            next_escape = False
            continue
        if ch == '"':
            break
        if ch == '\\':
            next_escape = True

    return it.value[start_pos:it.pos-1]

def parse_zshzle_binding(b: str) -> ZshZleBinding:
    it = CharIter(b)
    
    key = parse_quoted_string(it)
    key_end: Optional[str] = None
    if it.next() == "-":
        key_end = parse_quoted_string(it)
        it.skip()
    
    text, type = (
        (parse_quoted_string(it), ZshZleBindingType.COMMAND) 
        if it.peek() == '"' else 
        (it.remainder(), ZshZleBindingType.WIDGET) 
    )
    return ZshZleBinding(key, key_end, text, type)

def get_zshzle_bindings():
    binding_strings = subprocess.run(
        ["zsh", "-c", ". ~/.zshrc && bindkey"], 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    ).stdout.splitlines()
    return [ parse_zshzle_binding(binding) for binding in binding_strings ]