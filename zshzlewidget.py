from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Optional
import subprocess
import re
import json

@dataclass
class ZshZleWidget:
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

    specs: Optional[list[str]] = None 
    """STANDARD WIDGETS > p[style=margin-left=9%] > all text in any nested tags"""

    description: Optional[str] = None
    """STANDARD WIDGETS > p[style=margin-left=18%]:first > all text in any nested tags"""

    widgets: dict[str, ZshZleWidget] = {}
    """parsed widgets"""

    def handle_starttag(self, tag, attrs):
        self.h2 = tag == "h2"
        self.sw_h3 = self.sw and tag == "h3"
        
        if not self.sw or not self.section:
            return

        if tag == "br" and self.specs:
            self.specs.append("")
            return
        
        if tag == "p" and any([ k == "style" and v.startswith("margin-left:9%;") for (k, v) in attrs ]):
            self.specs = [""]
            return
        
        if tag == "p" and self.specs and any([ k == "style" and v.startswith("margin-left:18%;") for (k, v) in attrs ]):
            self.description = ""
            return

    def handle_endtag(self, tag):
        self.h2 = False
        self.sw_h3 = False
        if self.description != None and tag == "p":
            self.process()
            self.specs = None
            self.description = None

    def handle_data(self, data: str) -> None:
        if self.h2:
            self.sw = data.strip() == "STANDARD WIDGETS"
            self.section = None
        elif self.sw_h3:
            self.section = data.strip()
        elif self.description != None:
            self.description += data
        elif self.specs:
            self.specs[-1] += data

    def process(self):
        description = fix_ws(self.description)
        for spec in self.specs:
            widget = parse_widget_from_spec(fix_ws(spec))
            if widget:
                self.widgets[widget] = ZshZleWidget(self.section, description)

def fix_ws(str: str):
    stripped = str.strip()
    return re.sub(r"\s+", " ", stripped)

def parse_widget_from_spec(spec: str) -> Optional[str]:
    match = re.fullmatch(r"([a-z0-9\-]+).*", spec)
    return match.group(1) if match else None

def parse_zshzle_standard_widgets() -> dict[str, ZshZleWidget]:
    parser = ZshZleManHTMLParser()
    parser.feed(subprocess.run(["man", "-Thtml", "zshzle"], capture_output=True, text=True, encoding="utf-8").stdout)
    return parser.widgets

def parse_zshzle_aux_widgets() -> dict[str, ZshZleWidget]:
    with open("aux_widgets.json") as f:
        data: dict[str, object] = json.load(f)
    return { k: ZshZleWidget(**v) for k, v in data.items() }
    
def parse_zshzle_widgets():
    return { **parse_zshzle_standard_widgets(), **parse_zshzle_aux_widgets() }