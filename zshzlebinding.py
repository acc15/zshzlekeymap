from typing import NamedTuple, Optional
import subprocess
import re

class ZshZleAction(NamedTuple):
    text: str
    command: bool

class ZshZleBinding(NamedTuple):
    key: str
    key_end: Optional[str]
    action: ZshZleAction

def q(name: str):
    return fr'(?:"(?P<{name}>(?:\.|.)*?)")'

binding_pattern = re.compile(fr'{q("key")}(?:-{q("key_end")})? (?:{q("command")}|(?P<widget>.+))')

def parse_zshzle_binding(binding: str) -> ZshZleBinding:
    if not (m := binding_pattern.fullmatch(binding)):
        raise ValueError(f"can't parse zshzle binding: {binding}")
    return ZshZleBinding(
        m["key"], m["key_end"], 
        ZshZleAction(m["widget"], False) if m["widget"] else ZshZleAction(m["command"], True)
    )

def get_zshzle_bindings():
    binding_strings = subprocess.run(
        ["zsh", "-c", ". ~/.zshrc && bindkey"], 
        capture_output=True, 
        text=True, 
        encoding="utf-8"
    ).stdout.splitlines()
    return map(parse_zshzle_binding, binding_strings)
