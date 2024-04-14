import itertools
from operator import attrgetter
import os
import textwrap

from zshzlekeybinding import get_zshzle_key_bindings
from zshzlekeyformatter import KeysFormatter, Separators, Wrappers, html_wrap

def generate_md():
    
    bindings = sorted(get_zshzle_key_bindings(), key = attrgetter("desc.section", "action", "keys"))
    fmt = KeysFormatter(
        Wrappers(chord=html_wrap("kbd"), escape=lambda v: f"`{v}`", line=lambda keys: f"* {keys}"),
        Separators(line="\n")
    )

    with open("keys.md", "w") as f:
        f.write("# ZshZle bindings")

        f.write("\n\n## TOC\n")
        for section in itertools.groupby(bindings, key = lambda b: b.desc.section):
            f.write(f"\n1. [{section}](<#{section}>)")

        for section, section_bindings in itertools.groupby(bindings, key = lambda b: b.desc.section):
            f.write(f"\n\n## {section}")
            for action, action_bindings in itertools.groupby(section_bindings, key = lambda b: b.action):
                f.write(f"\n\n### `{action.text}`")
                f.write(f"\n\n### Keys\n{fmt.format_binding_keys(action_bindings)}")
                if description := bindings[0].desc.description:
                    f.write(f"\n\n### Description\n{os.linesep.join(textwrap.wrap(description, 120))}")
                f.write("\n\n---")

generate_md()