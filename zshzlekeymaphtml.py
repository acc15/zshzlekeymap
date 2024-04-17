import itertools

from zshzlekeybinding import get_zshzle_key_bindings
from zshzlekeyformatter import KeysFormatter, Separators, Wrappers, html_wrap

def generate_html():
    
    bindings = get_zshzle_key_bindings()
    fmt = KeysFormatter(
        Wrappers(key=html_wrap("kbd"), escape=html_wrap("code"), line=html_wrap("div", {"class":"keys"})), 
        Separators(line="")
    )

    with open("keys.html", "w") as f:
        f.write(
            '<!DOCTYPE html><html><head>'
            '<title>ZshZle bindings</title>'
            '<link href="keys.css" rel="stylesheet"/>'
            '</head><body><table>'
            '<thead><tr><th id="keys">Keys</th><th id="action">Action</th><th id="description">Description</th></thead>'
            '<tbody>'
        )

        for section, section_bindings in itertools.groupby(bindings, key = lambda b: b.desc.section):
            f.write(f'<tr><td colspan="3"><h4>{section}</h4></td></tr>')

            for binding in section_bindings:
                f.write('<tr>'
                        f'<td>{fmt.binding_keys(binding)}</td>'
                        f'<td><code>{binding.action.text}</code></td>'
                        f'<td>{binding.desc.description}</td>'
                        '</tr>')

        f.write("</tbody></table></body></html>")

generate_html()