import itertools
from operator import attrgetter
import os
import textwrap

from zshzlekeybinding import ZshZleKeyBinding, get_zshzle_key_bindings
from zshzlekeyformatter import KeysFormatter, Separators, Wrappers, html_wrap

def generate_md():
    
    bindings = get_zshzle_key_bindings()
    fmt = KeysFormatter(
        Wrappers(chord=html_wrap("kbd"), escape=lambda v: f"`{v}`", line=lambda keys: f"* {keys}"),
        Separators(line="\n")
    )

    def section_key(b: ZshZleKeyBinding):
        return b.desc.section

    with open("keys.md", "w") as f:
        f.write("# ZshZle bindings")

        f.write("\n\n## TOC\n")
        for section, _ in itertools.groupby(bindings, key = section_key):
            f.write(f"\n1. [{section}](<#{section}>)")

        for section, section_bindings in itertools.groupby(bindings, key = section_key):
            f.write(f"\n\n## {section}")
            
            for binding in section_bindings:
                f.write(f"\n\n### `{binding.action.text}`")
                f.write(f"\n\n### Keys\n{fmt.binding_keys(binding)}")
                if binding.desc.description:
                    f.write(f"\n\n### Description\n{os.linesep.join(textwrap.wrap(binding.desc.description, 120))}")
                f.write("\n\n---")

generate_md()