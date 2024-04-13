from dataclasses import dataclass
from typing import Optional
import subprocess
from enum import Enum, auto
import re

class ZshZleBindingType(Enum):
    WIDGET = auto()
    COMMAND = auto()

@dataclass
class ZshZleBinding:
    key: str
    key_end: Optional[str]
    text: str
    command: bool

def q(name: str):
    return fr'(?:"(?P<{name}>(?:\.|.)*?)")'

binding_pattern = re.compile(fr'{q("key")}(?:-{q("key_end")})? (?:{q("command")}|(?P<widget>.+))')

def parse_zshzle_binding(binding: str) -> ZshZleBinding:
    if not (m := binding_pattern.fullmatch(binding)):
        raise ValueError(f"can't parse zshzle binding: {binding}")
    text, type = (
        (m["widget"], False) if m["widget"] else 
        (m["command"], True)
    )
    return ZshZleBinding(m["key"], m["key_end"], text, type)

def get_zshzle_bindings():
    binding_strings = subprocess.run(
        ["zsh", "-c", ". ~/.zshrc && bindkey"], 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    ).stdout.splitlines()
    return [ parse_zshzle_binding(binding) for binding in binding_strings ]
