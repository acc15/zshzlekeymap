import itertools
from operator import attrgetter
from typing_extensions import override

from zshzlebinding import ZshZleAction
from zshzlekeybinding import get_zshzle_key_bindings
from zshzlekeyformatter import KeysFormatter, Separators, Wrappers, html_wrap

def generate_html():
    
    bindings = sorted(get_zshzle_key_bindings(), key = attrgetter("desc.section", "action", "keys"))
    with open("keys.html", "w") as f:
        f.write(
            "<!DOCTYPE html><html><head>"
            "<title>ZshZle bindings</title>"
            "<link href=\"keys.css\" rel=\"stylesheet\"/>"
            "</head><body><table>"
            "<thead><tr><th>Keys</th><th>Action</th><th>Description</th></thead>"
            "<tbody>"
        )

        fmt = KeysFormatter(
            Wrappers(chord=html_wrap("kbd"), escape=html_wrap("code"), line=html_wrap("div", [("class", "keys")])), 
            Separators(line="")
        )

        for section, section_bindings in itertools.groupby(bindings, key = attrgetter("desc.section")):
            f.write(f'<tr><td colspan="3"><h4>{section}</h4></td></tr>')

            action: ZshZleAction
            for action, action_bindings in itertools.groupby(section_bindings, key = attrgetter("action")):
                b = list(action_bindings)
                f.write('<tr>'
                        f'<td>{fmt.format_binding_keys(b)}</td>'
                        f'<td><code>{action.text}</code></td>'
                        f'<td>{b[0].desc.description}</td>'
                        '</tr>')

        f.write("</tbody></table></body></html>")


generate_html()