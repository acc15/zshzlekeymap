from html.parser import HTMLParser
from typing import NamedTuple, Optional
import subprocess
import re
import json

class ZshZleDescriptor(NamedTuple):
    section: str
    description: str

class ZshZleManHTMLParser(HTMLParser):

    h2: bool = False
    """in start of H2, until any other tag"""
    
    sw: bool = False
    """in STANDARD WIDGETS"""
    
    sw_h3: bool = False
    """in STANDARD WIDGETS > h3, until any other tag"""
    
    section: Optional[str] = None
    """STANDARD WIDGETS > h3 > text"""

    specs: list[str] = [] 
    """STANDARD WIDGETS > p[style=margin-left=9%] > all text in any nested tags"""

    description: Optional[str] = None
    """STANDARD WIDGETS > p[style=margin-left=18%]:first > all text in any nested tags"""

    widgets: dict[str, ZshZleDescriptor] = {}
    """parsed widgets"""

    def handle_starttag(self, tag, attrs):
        self.h2 = tag == "h2"
        self.sw_h3 = self.sw and tag == "h3"
        
        if not self.sw or not self.section:
            return

        if tag == "br" and self.specs:
            self.specs.append("")
            return
        
        if tag == "p" and not self.specs and has_style(attrs, "margin-left:9%;"):
            self.specs.append("")
            return
        
        if tag == "p" and self.specs and has_style(attrs, "margin-left:18%;"):
            self.description = ""
            return

    def handle_endtag(self, tag):
        self.h2 = False
        self.sw_h3 = False
        if tag == "p" and self.section and self.description:
            self.process(self.section, self.description)
            self.specs.clear()
            self.description = None

    def handle_data(self, data: str) -> None:
        if self.h2:
            self.sw = data.strip() == "STANDARD WIDGETS"
            self.section = None
        elif self.sw_h3:
            self.section = data.strip()
        elif self.description is not None:
            self.description += data
        elif self.specs:
            self.specs[-1] += data

    def process(self, section: str, description: str):
        description = fix_ws(description)
        for spec in self.specs:
            widget = parse_widget_from_spec(fix_ws(spec))
            if widget:
                self.widgets[widget] = ZshZleDescriptor(section, description)

def has_style(attrs, str: str):
    return any([ k == "style" and str in v for k, v in attrs ])

def fix_ws(str: str):
    stripped = str.strip()
    return re.sub(r"\s+", " ", stripped)

def parse_widget_from_spec(spec: str) -> Optional[str]:
    match = re.fullmatch(r"([a-z0-9\-]+).*", spec)
    return match.group(1) if match else None

def get_zshzle_standard_widgets() -> dict[str, ZshZleDescriptor]:
    parser = ZshZleManHTMLParser()
    parser.feed(subprocess.run(["man", "-Thtml", "zshzle"], capture_output=True, text=True, encoding="utf-8").stdout)
    return parser.widgets

def get_zshzle_aux_widgets() -> dict[str, ZshZleDescriptor]:
    with open("aux_widgets.json") as f:
        data: dict[str, dict[str, str]] = json.load(f)
    return { k: ZshZleDescriptor(**v) for k, v in data.items() }
    
def get_zshzle_widgets():
    return { **get_zshzle_standard_widgets(), **get_zshzle_aux_widgets() }