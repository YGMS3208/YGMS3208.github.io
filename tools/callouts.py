#!/usr/bin/env python3
"""Pin each callout number on the structure diagrams to the parts it names.
callout_parts.json: page -> {number: [part indices]} (index = order of the parts the teardown splits the drawing into;
the first part carries the leader's dot when exploded). Written onto the figure's svg as data-pk; atlas.js reads it."""
import json, os, re
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(SITE)
data = json.load(open(os.path.join(SITE, "tools", "callout_parts.json"), encoding="utf-8"))
n = 0
for page, pk in data.items():
    s = open(page, encoding="utf-8").read()
    m = re.search(r'(<div class="anat"><figure class="stage[^"]*"><svg )', s)
    if not m: print("callouts: no figure on", page); continue
    attr = "data-pk='" + json.dumps(pk, separators=(",", ":")) + "' "
    s = s[:m.end()] + attr + s[m.end():]
    open(page, "w", encoding="utf-8").write(s); n += 1
print("callouts pinned on", n, "figures")
