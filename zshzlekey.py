

from dataclasses import dataclass
from typing import Iterable, Optional
from enum import Enum, auto
from zshzlebinding import ZshZleBinding, ZshZleBindingType, get_zshzle_bindings
import re 

keymap: dict[str, list[list[list[str]]]] = {
    "^?": [
        [
            ["Backspace"]
        ], 
        [
            ["Ctrl", "Shift", "/"]
        ]
    ],
    "^M": [[["Enter"]], [["Ctrl", "M"]]],
    "^I": [[["Tab"]], [["Ctrl", "I"]]]
}

key_pattern = re.compile(r"(?P<alt>\^\[)?(?P<ctrl>\^)?(?P<char>.)")

def parse_key(key: str) -> Optional[list[str]]:

    m = key_pattern.fullmatch(key) 
    if m:
        result = []
        if m.group("ctrl"):
            result.append("Ctrl")
        if m.group("alt"):
            result.append("Alt")
        result.append(m.group("char").upper())
        return result

    return None


def kbd(key: str):
    return f"<kbd>{key}</kbd>"

def format_bindings(bindings: Iterable[ZshZleBinding]):
    return " | ".join([ kbd(b.key) for b in bindings ])

print(parse_key("^[^N"))
print(parse_key("^[^n"))
print(parse_key("^[m"))
print(parse_key("^Q"))
print(parse_key("q"))
print(parse_key("^Xa"))
print(parse_key("aaa"))
