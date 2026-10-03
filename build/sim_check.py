"""Validate operation-training scenarios (data/mt/sim/*.json).
Usage: python3 build/sim_check.py [file ...]   (no args = all scenarios)
Prints problems and exits 1 if any. site.py runs the same check during the build."""
import glob
import json
import os
import re
import sys

B = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(os.path.dirname(B), "data", "mt", "sim")

VISUAL = {
    "cnc-lathe": "lathe", "vertical-turning-lathe": "vtl", "turn-mill": "turnmill", "swiss-type-lathe": "swiss",
    "vertical-machining-center": "vmc", "horizontal-machining-center": "hmc", "5-axis-machining-center": "5axis",
    "double-column-machining-center": "gantry", "cylindrical-grinder": "cylgrind", "internal-grinder": "intgrind",
    "surface-grinder": "surfgrind", "centerless-grinder": "centerless", "gear-hobbing-machine": "hob",
    "gear-grinding-machine": "geargrind", "gear-skiving-machine": "skive", "edm": "wedm", "laser-machine": "laser",
    "transfer-machine": "transfer",
}
PANEL = ["power", "estop", "hyd", "home", "mode_edit", "mode_mem", "mode_mdi", "mode_jog", "mode_handle", "single", "dry",
         "cycle", "hold", "reset", "spindle", "sstop", "coolant", "door", "chuck", "tail", "bar", "tool_unclamp", "apc",
         "wheel", "wstop", "wspin", "dress", "magnet", "pump", "wire", "gas", "beam", "line", "conv", "measure", "lube"]
COMMON = {"power": bool, "lamp": ("off", "yellow", "green", "red"), "door": ("open", "closed"), "homed": bool, "single": bool,
          "work": ("none", "set", "done"), "clamp": bool, "tool": ("home", "near", "cut"), "spindle": bool, "coolant": bool,
          "chips": bool, "chatter": bool}
EXTRA = {"tail": bool, "bar": bool, "tilt": (0, 45, 90), "mill": bool, "probe": bool, "pallet": ("A", "B"), "dress": bool,
         "wspin": bool, "wire": bool, "fluid": bool, "gas": bool, "line": bool, "jaws": bool}
FX = ["crash", "fly", "burst", "fire", "smoke", "alarm", "chatter", "slip", "deform", "wirebreak", "burn", "leak", "hazard"]
TYPES = ["check", "panel", "choice", "input", "order", "jog"]
BANNED = ["ファナック", "FANUC", "Fanuc", "三菱", "シーメンス", "Siemens", "SIEMENS", "ハイデンハイン", "HEIDENHAIN", "オークマ", "OKUMA",
          "マザック", "Mazak", "DMG", "森精機", "牧野", "ジェイテクト", "豊田工機", "ブラザー", "安田工業", "ソディック", "Sodick",
          "アマダ", "AMADA", "トルンプ", "TRUMPF", "グリーソン", "Gleason", "カペラ", "Kapp", "ライスハウワー", "Reishauer",
          "ノリタケ", "クレトイシ", "北川", "豊和", "インコネル", "テフロン", "Inconel", "マクロB", "カスタムマクロ"]


def check(fn):
    P = []
    try:
        d = json.load(open(fn, encoding="utf-8"))
    except Exception as e:  # noqa
        return ["%s: JSON error %s" % (fn, e)]
    slug = os.path.basename(fn)[:-5]
    if d.get("slug") != slug:
        P.append("slug must be %s" % slug)
    if d.get("visual") != VISUAL.get(slug):
        P.append("visual must be %s" % VISUAL.get(slug))
    for k in ("title", "summary", "job"):
        if not isinstance(d.get(k), str) or not d.get(k):
            P.append("missing %s" % k)
    if not (60 <= len(d.get("summary", "")) <= 220):
        P.append("summary length %d (60-220)" % len(d.get("summary", "")))
    if d.get("level") not in (1, 2, 3):
        P.append("level must be 1, 2 or 3")
    if not isinstance(d.get("minutes"), int):
        P.append("minutes must be an integer")
    panel = d.get("panel", [])
    for b in panel:
        if b not in PANEL:
            P.append("unknown panel button %s" % b)
    if not (6 <= len(panel) <= 18):
        P.append("panel should list 6-18 buttons (has %d)" % len(panel))
    inc = d.get("incidents", {})
    used = set()

    def ref(i, where):
        used.add(i)
        if i not in inc:
            P.append("%s: unknown incident %s" % (where, i))

    def setcheck(s, where):
        for k, v in (s or {}).items():
            spec = COMMON.get(k, EXTRA.get(k))
            if spec is None:
                P.append("%s: unknown state key %s" % (where, k))
            elif spec is bool:
                if not isinstance(v, bool):
                    P.append("%s: %s must be true/false" % (where, k))
            elif v not in spec:
                P.append("%s: %s must be one of %s" % (where, k, spec))

    steps = d.get("steps", [])
    if not (12 <= len(steps) <= 18):
        P.append("steps: %d (12-18)" % len(steps))
    ids = [s.get("id") for s in steps]
    if len(set(ids)) != len(ids):
        P.append("duplicate step ids")
    kinds = [s.get("type") for s in steps]
    for need, n in (("check", 1), ("panel", 1), ("choice", 5), ("input", 2), ("order", 1)):
        if kinds.count(need) < n:
            P.append("needs at least %d %s step(s)" % (n, need))
    for s in steps:
        w = s.get("id", "?")
        for k in ("phase", "type", "title", "text", "hint", "explain"):
            if not s.get(k):
                P.append("%s: missing %s" % (w, k))
        t = s.get("type")
        if t not in TYPES:
            P.append("%s: bad type %s" % (w, t))
        setcheck(s.get("set"), w + ".set")
        setcheck(s.get("pre"), w + ".pre")
        if t == "check":
            it = s.get("items", [])
            if not (4 <= len(it) <= 8):
                P.append("%s: 4-8 items" % w)
            if not any(not x.get("req") for x in it):
                P.append("%s: include at least one wrong item (req false + ng)" % w)
            for x in it:
                if not x.get("req") and not x.get("ng"):
                    P.append("%s: wrong item needs ng text" % w)
                if x.get("inc"):
                    ref(x["inc"], w)
            if s.get("miss"):
                ref(s["miss"], w)
        elif t == "panel":
            seq = s.get("seq", [])
            if not seq:
                P.append("%s: empty seq" % w)
            for b in seq + list(s.get("traps", {}).keys()):
                if b not in panel:
                    P.append("%s: button %s not in panel" % (w, b))
            for b, i in s.get("traps", {}).items():
                if b in seq:
                    P.append("%s: trap %s is also in seq" % (w, b))
                ref(i, w)
        elif t == "choice":
            op = s.get("options", [])
            if not (3 <= len(op) <= 4):
                P.append("%s: 3-4 options" % w)
            if sum(1 for o in op if o.get("ok")) != 1:
                P.append("%s: exactly one ok option" % w)
            for o in op:
                if not o.get("ok") and not o.get("inc") and not o.get("ng"):
                    P.append("%s: option needs ok, inc or ng" % w)
                if o.get("inc"):
                    ref(o["inc"], w)
            if not any(o.get("inc") for o in op):
                P.append("%s: at least one option should cause an incident" % w)
        elif t == "input":
            ok = s.get("ok")
            if not (isinstance(ok, list) and len(ok) == 2 and ok[0] <= ok[1]):
                P.append("%s: ok must be [min, max]" % w)
            for k in ("label", "unit", "ng"):
                if k not in s:
                    P.append("%s: missing %s" % (w, k))
            for c in s.get("cases", []):
                if ("lt" in c) == ("gt" in c):
                    P.append("%s: case needs lt or gt" % w)
                if c.get("inc"):
                    ref(c["inc"], w)
                elif not c.get("ng"):
                    P.append("%s: case needs inc or ng" % w)
                if ok and isinstance(ok, list) and len(ok) == 2:
                    if "lt" in c and c["lt"] > ok[0]:
                        P.append("%s: case lt %s overlaps the ok range" % (w, c["lt"]))
                    if "gt" in c and c["gt"] < ok[1]:
                        P.append("%s: case gt %s overlaps the ok range" % (w, c["gt"]))
        elif t == "order":
            if not (2 <= len(s.get("items", [])) <= 6):
                P.append("%s: 2-6 items" % w)
            if s.get("inc"):
                ref(s["inc"], w)
            elif not s.get("ng"):
                P.append("%s: order needs inc or ng" % w)
        elif t == "jog":
            for k in ("axis", "from", "tol", "inc"):
                if k not in s:
                    P.append("%s: missing %s" % (w, k))
            if s.get("inc"):
                ref(s["inc"], w)
            if not (0.5 <= s.get("from", 0) <= 20):
                P.append("%s: from 0.5-20 mm" % w)
            if not (0.005 <= s.get("tol", 0) <= 0.1):
                P.append("%s: tol 0.005-0.1 mm" % w)
    if not (12 <= len(inc) <= 30):
        P.append("incidents: %d (12-30)" % len(inc))
    for k, v in inc.items():
        for f in ("title", "what", "why", "loss", "prevent"):
            if not v.get(f):
                P.append("incident %s: missing %s" % (k, f))
        if v.get("sev") not in (1, 2, 3):
            P.append("incident %s: sev 1-3" % k)
        if v.get("fx") not in FX:
            P.append("incident %s: fx must be one of %s" % (k, FX))
        if k not in used:
            P.append("incident %s is never triggered" % k)
    if not any(v.get("sev") == 3 for v in inc.values()):
        P.append("include at least one sev 3 incident")
    for k in ("safety", "sales"):
        if not (4 <= len(d.get(k, [])) <= 7):
            P.append("%s: 4-7 lines" % k)
    txt = json.dumps(d, ensure_ascii=False)
    for b in BANNED:
        if b in txt:
            P.append("banned name: %s" % b)
    if re.search(r"[A-Za-z]+社", txt):
        P.append("looks like a company name")
    return ["%s: %s" % (slug, p) for p in P]


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(SIM + "/*.json"))
    probs = []
    for f in files:
        probs += check(f)
    for p in probs:
        print(p)
    print("checked %d file(s), %d problem(s)" % (len(files), len(probs)))
    sys.exit(1 if probs else 0)
