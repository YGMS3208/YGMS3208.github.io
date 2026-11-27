# -*- coding: utf-8 -*-
"""Small HTML helpers shared by the handbook pages (handbook_a/b/c.py)."""
G = "/machine-tools/guide/"

def T(head, rows):
    """A table that turns into cards on phones (see .gx table rules in gxstyle.py)."""
    return ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f'<td data-l="{head[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows) + "</tbody></table></div>")

def EQ(lines):
    """Formulas: [(formula, note)]."""
    return '<p class="eq">' + "".join(f"<span>{a}<small>{b}</small></span>" if b else f"<span>{a}</span>" for a, b in lines) + "</p>"

def NOTE(label, text):
    return f'<p class="note"><b>{label}</b>{text}</p>'

def CALC(name, **defaults):
    """A calculator; atlas.js builds the inputs and results from its CALC table. defaults override the initial values."""
    a = "".join(f' data-{k.lower()}="{v}"' for k, v in defaults.items())
    return f'<div class="lab calc" data-calc="{name}"{a}></div>'
