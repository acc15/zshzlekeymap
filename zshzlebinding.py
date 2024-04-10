from dataclasses import dataclass
from typing import Optional
import subprocess
from enum import Enum, auto

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
    string: str
    position: int
    
    def __init__(self, s: str, p: int = 0):
        self.string = s
        self.position = p

    def has_next(self):
        return self.position < len(self.string)

    def peek(self):
        assert self.has_next()
        return self.string[self.position : self.position + 1]
    
    def next(self):
        result = self.peek()
        self.position += 1
        return result
    
    def remainder(self):
        return self.string[self.position:]

def parse_quoted_string(it: CharIter) -> str:
    assert it.next() == '"'

    next_escape = False
    result = ""

    while it.has_next():
        ch = it.next()
        if next_escape:
            result += ch
            next_escape = False
            continue
        if ch == '\\':
            next_escape = True
            continue
        if ch == '"':
            break
        result += ch
    return result

def parse_zshzle_binding(binding: str) -> ZshZleBinding:
    it = CharIter(binding)
    key = parse_quoted_string(it)
    sep = it.next()
    key_end = None
    if sep == "-":
        key_end = parse_quoted_string(it)
        sep = it.next()
    
    text = None
    type = ZshZleBindingType.WIDGET
    if it.peek() == '"':
        text = parse_quoted_string(it)
        type = ZshZleBindingType.COMMAND
    else:
        text = it.remainder()

    return ZshZleBinding(key, key_end, text, type)

def get_zshzle_bindings():
    binding_strings = subprocess.run(
        ["zsh", "-c", ". ~/.zshrc && bindkey"], 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    ).stdout.splitlines()
    return [ parse_zshzle_binding(binding) for binding in binding_strings ]