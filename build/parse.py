import os as _os
_B = _os.path.dirname(_os.path.abspath(__file__))
_D = _os.path.join(_os.path.dirname(_B), "data")

import json, glob, re, sys, os
from collections import OrderedDict, defaultdict

KINDS = ["素材","鋳造","鍛造","プレス","切削","研削","歯車","熱処理","表面処理","接合","成形","塗装","巻線","組立","電子","化学","検査","物流","保全"]

def parse(files):
    systems = []
    cur_sys = cur_part = cur_op = None
    for f in files:
        for ln, raw in enumerate(open(f, encoding="utf-8"), 1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            def fields(s, n):
                parts = [p.strip() for p in s.split(" | ")]
                while len(parts) < n:
                    parts.append("")
                if len(parts) > n:
                    raise SystemExit(f"{f}:{ln} too many fields: {s}")
                return parts
            if line.startswith("@sys "):
                i, name, sub, desc = fields(line[5:], 4)
                cur_sys = {"id": i, "name": name, "sub": sub, "desc": desc, "parts": []}
                systems.append(cur_sys)
            elif line.startswith("@part "):
                i, name, mat, desc = fields(line[6:], 4)
                cur_part = {"id": i, "name": name, "mat": mat, "desc": desc, "ops": []}
                cur_sys["parts"].append(cur_part)
            elif line.startswith("> "):
                name, kind, desc = fields(line[2:], 3)
                if kind not in KINDS:
                    raise SystemExit(f"{f}:{ln} unknown kind {kind}")
                cur_op = {"name": name, "kind": kind, "desc": desc, "m": [], "i": [], "k": ""}
                cur_part["ops"].append(cur_op)
            elif line.startswith("M ") or line.startswith("I "):
                cat, spec, mk = fields(line[2:], 3)
                cur_op["m" if line[0] == "M" else "i"].append([cat, spec, mk])
            elif line.startswith("K "):
                cur_op["k"] = line[2:].strip()
            else:
                raise SystemExit(f"{f}:{ln} bad line: {line}")
    return systems

if __name__ == "__main__":
    files = sorted(glob.glob(_D + "/[0-9]*.txt"))
    systems = parse(files)
    cats = defaultdict(lambda: [0, 0])
    nparts = nops = 0
    ids = set()
    for s in systems:
        for p in s["parts"]:
            key = s["id"] + "." + p["id"]
            if key in ids: print("DUP", key)
            ids.add(key)
            nparts += 1
            for o in p["ops"]:
                nops += 1
                for c in o["m"]: cats[c[0]][0] += 1
                for c in o["i"]: cats[c[0]][1] += 1
    print("systems", len(systems), "parts", nparts, "ops", nops, "cats", len(cats))
    for c, (m, i) in sorted(cats.items(), key=lambda x: -(x[1][0] + x[1][1])):
        print(f"{c}\tM{m}\tI{i}")
