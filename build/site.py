"""Static site generator for 自動車製造工程図鑑.

  python3 site.py            build into ../out
  BUILD_DATE=2026-10-01 python3 site.py   (override the date used for new/changed pages)

Pages are rendered by the same UI code as the app (site_tpl.html) inside headless Chromium,
then wrapped here with head tags, structured data and the shared shell. The build fails if a
published URL disappears without a redirect, if links break, or if pages lose their content.
"""
import os as _os
_B = _os.path.dirname(_os.path.abspath(__file__))
_D = _os.path.join(_os.path.dirname(_B), "data")

import datetime
import glob
import gzip
import hashlib
import html
import json
import os
import re
import runpy
import shutil
import sys
from collections import Counter, defaultdict

B = _B
OUT = os.environ.get("OUT", _os.path.join(_os.path.dirname(_D), "out"))
STATE = B + "/state"
CACHE = B + "/.cache"
CFG = json.load(open(B + "/site_config.json", encoding="utf-8"))
BASE = CFG["base"].rstrip("/")
TODAY = os.environ.get("BUILD_DATE") or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
SITE = "自動車製造工程図鑑"
FONTS = "/tmp/claude-0/-home-claude/d64aa5d8-91f8-5c74-a54e-ffbc453c9481/scratchpad/fonts/node_modules/@fontsource"
FONTS = os.environ.get("FONTSOURCE", FONTS if os.path.isdir(FONTS) else B + "/node_modules/@fontsource")
os.makedirs(STATE, exist_ok=True)
os.makedirs(CACHE + "/og", exist_ok=True)


def sha(x):
    return hashlib.sha256(x if isinstance(x, bytes) else x.encode("utf-8")).hexdigest()


def jdump(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def ja_date(d):
    y, m, dd = d.split("-")
    return "%s年%d月%d日" % (y, int(m), int(dd))


# ============================================================ 1. data
g = runpy.run_path(B + "/build.py")
data = g["data"]
systems, cats, groups, kinds = data["systems"], data["cats"], data["groups"], data["kinds"]
parts = [p for s in systems for p in s["parts"]]
for s in systems:
    for p in s["parts"]:
        p["_s"] = s

# ---- slugs
SL = {}
for l in open(_D + "/slugs.tsv", encoding="utf-8"):
    l = l.rstrip("\n")
    if not l or l.startswith("#"):
        continue
    t, n, sl = l.split("\t")
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", sl), sl
    SL[(t, n)] = sl
for s in systems:
    s["slug"] = SL[("system", s["name"])]
for p in parts:
    p["slug"] = SL[("part", p["name"])]
for c in cats:
    c["slug"] = SL[("cat", c["n"])]
data["gslug"] = [SL[("group", x)] for x in groups]
for k in kinds:
    k["slug"] = SL[("method", k["n"])]
for lst, key in ((systems, "slug"), (parts, "slug"), (cats, "slug"), (kinds, "slug")):
    dup = [x for x, n in Counter(o[key] for o in lst).items() if n > 1]
    assert not dup, dup
assert len(set(data["gslug"])) == len(groups)

# ---- operation numbers are stored, never recomputed from order
opn_path = STATE + "/opnums.json"
OPN = json.load(open(opn_path, encoding="utf-8")) if os.path.exists(opn_path) else {}
for p in parts:
    keys, seen = [], Counter()
    for o in p["ops"]:
        seen[o["n"]] += 1
        keys.append(o["n"] if seen[o["n"]] == 1 else "%s#%d" % (o["n"], seen[o["n"]]))
    old = dict(OPN.get(p["slug"], []))
    nums = [old.get(k) for k in keys]
    if not old:
        nums = [(i + 1) * 10 for i in range(len(keys))]
    for i, v in enumerate(nums):
        if v is None:
            lo = max([x for x in nums[:i] if x is not None] or [0])
            hi = min([x for x in nums[i + 1:] if x is not None] or [lo + 20])
            v = lo + 10 if hi - lo > 10 else (lo + hi) // 2
            assert lo < v < hi or not any(x is not None for x in nums[i + 1:]), ("no room for new op", p["slug"], keys[i])
            nums[i] = v
    assert nums == sorted(nums) and len(set(nums)) == len(nums), (p["slug"], nums)
    for o, v in zip(p["ops"], nums):
        o["no"] = v
    OPN[p["slug"]] = [[k, v] for k, v in zip(keys, nums)]

# ---- written content (methods / equipment), with first-mention links
PART_URL = {p["name"]: "/parts/%s/" % p["slug"] for p in parts}
EQ_URL = {c["n"]: "/equipment/%s/" % c["slug"] for c in cats}


ATLAS_DIC = None


def linkify(text, used, skip=(), dic=None, minlen=3):
    """escape text and link the first mention (per article) of part / equipment names."""
    global ATLAS_DIC
    if ATLAS_DIC is None:
        ATLAS_DIC = dict(EQ_URL)
        ATLAS_DIC.update(PART_URL)
    dic = dic or ATLAS_DIC
    names = sorted([n for n in dic if n not in skip and len(n) >= minlen], key=len, reverse=True)
    spans, taken = [], [False] * len(text)
    for n in names:
        if n in used:
            continue
        i = text.find(n)
        while i >= 0 and any(taken[i:i + len(n)]):
            i = text.find(n, i + 1)
        if i < 0:
            continue
        used.add(n)
        for j in range(i, i + len(n)):
            taken[j] = True
        spans.append((i, i + len(n), dic[n]))
    out, pos = "", 0
    for a, b, u in sorted(spans):
        out += html.escape(text[pos:a], quote=False) + '<a href="%s">%s</a>' % (u, html.escape(text[a:b], quote=False))
        pos = b
    return out + html.escape(text[pos:], quote=False)


def md(body, used, skip=(), dic=None, minlen=3):
    out, para, lst, tbl, sec = [], [], [], [], ""

    def flush():
        nonlocal para, lst, tbl
        if para:
            out.append("<p>%s</p>" % linkify("".join(para), used, skip, dic, minlen))
        if lst:
            cls = ' class="refs"' if sec == "参考" else ""
            out.append("<ul%s>%s</ul>" % (cls, "".join("<li>%s</li>" % (html.escape(x) if sec == "参考" else linkify(x, used, skip, dic, minlen)) for x in lst)))
        if tbl:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in tbl if not re.fullmatch(r"\|?[\s:\-|]+\|?", r.strip())]
            h = "<thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % html.escape(c) for c in rows[0])
            b = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % linkify(c, used, skip, dic, minlen) for c in r) for r in rows[1:])
            out.append('<div class="tw"><table>%s<tbody>%s</tbody></table></div>' % (h, b))
        para, lst, tbl = [], [], []
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("## "):
            flush()
            sec = s[3:].strip()
            out.append("<h2>%s</h2>" % html.escape(sec))
        elif s.startswith("|"):
            if para or lst:
                flush()
            tbl.append(s)
        elif s.startswith("- "):
            if para or tbl:
                flush()
            lst.append(s[2:].strip())
        else:
            if lst or tbl:
                flush()
            para.append(s)
    flush()
    return "".join(out)


KBYN = {k["n"]: k for k in kinds}
for f in sorted(glob.glob(_D + "/content/methods_*.md")):
    for blk in re.split(r"^@method ", open(f, encoding="utf-8").read(), flags=re.M)[1:]:
        name, rest = blk.split("\n", 1)
        k = KBYN[name.strip()]
        m = re.match(r"title:\s*(.+)\nlead:\s*(.+)\n", rest)
        k["title"], k["lead"] = m.group(1).strip(), m.group(2).strip()
        k["body"] = md(rest[m.end():], set())
        k["idx"] = True
CBYN = {c["n"]: c for c in cats}
for f in sorted(glob.glob(_D + "/content/equipment_*.md")):
    for blk in re.split(r"^@eq ", open(f, encoding="utf-8").read(), flags=re.M)[1:]:
        name, rest = blk.split("\n", 1)
        c = CBYN[name.strip()]
        c["body"] = md(rest.strip(), set(), skip=(c["n"],))
        c["idx"] = True

# ---- machine-tool atlas (/machine-tools/)
import il_mt
MT_FAM = [{"id": "lathe", "n": "旋盤", "en": "LATHES"}, {"id": "mc", "n": "マシニングセンタ", "en": "MACHINING CENTERS"},
          {"id": "grind", "n": "研削盤", "en": "GRINDERS"}, {"id": "gear", "n": "歯車加工機", "en": "GEAR MACHINES"},
          {"id": "special", "n": "特殊加工機・専用機", "en": "SPECIAL MACHINES"}]
FAM_OF = {"cnc-lathe": "lathe", "vertical-turning-lathe": "lathe", "turn-mill": "lathe", "swiss-type-lathe": "lathe",
          "vertical-machining-center": "mc", "horizontal-machining-center": "mc", "5-axis-machining-center": "mc", "double-column-machining-center": "mc",
          "cylindrical-grinder": "grind", "internal-grinder": "grind", "surface-grinder": "grind", "centerless-grinder": "grind",
          "gear-hobbing-machine": "gear", "gear-grinding-machine": "gear", "gear-skiving-machine": "gear",
          "edm": "special", "laser-machine": "special", "transfer-machine": "special"}
MT_EQ = {"cnc-lathe": "NC旋盤", "vertical-turning-lathe": "立形旋盤", "swiss-type-lathe": "自動旋盤（主軸移動形）", "vertical-machining-center": "立形マシニングセンタ",
         "horizontal-machining-center": "横形マシニングセンタ", "5-axis-machining-center": "5軸マシニングセンタ", "double-column-machining-center": "門形マシニングセンタ",
         "cylindrical-grinder": "円筒研削盤", "internal-grinder": "内面研削盤", "surface-grinder": "平面研削盤", "centerless-grinder": "センタレス研削盤",
         "gear-hobbing-machine": "ホブ盤", "gear-grinding-machine": "歯車研削盤", "gear-skiving-machine": "ギヤスカイビング盤", "edm": "放電加工機",
         "laser-machine": "レーザ加工機", "transfer-machine": "トランスファーマシン・専用機",
         "robot-loading": "ハンドリングロボット", "in-process-gauging": "インプロセス計測装置"}
COMP_NAMES = {"主軸軸受": "spindle", "主軸": "spindle", "ボールねじ": "ball-screw", "リニアガイド": "linear-guide", "すべり案内面": "slideway", "サーボモータ": "servo-motor",
              "リニアモータ": "servo-motor", "NC装置": "cnc", "ATC": "atc", "ツールホルダ": "tool-holder", "チャック": "chuck", "タレット": "turret", "クーラント": "coolant",
              "ベッド": "bed", "熱変位": "thermal-displacement"}
AUTO_NAMES = {"ガントリーローダ": "gantry-loader", "ロボット": "robot-loading", "パレットチェンジャ": "pallet-changer", "APC": "pallet-changer", "バーフィーダ": "bar-feeder",
              "機上計測": "in-process-gauging", "インプロセス計測": "in-process-gauging", "タッチプローブ": "in-process-gauging", "チップコンベヤ": "chip-conveyor", "FMS": "fms-cell"}
GUIDE_PICS = {"lathe-vs-machining-center": ["cnc-lathe", "vertical-machining-center"], "vertical-vs-horizontal-mc": ["vertical-machining-center", "horizontal-machining-center"],
              "3-axis-vs-5-axis": ["vertical-machining-center", "5-axis-machining-center"], "nc-vs-conventional": ["cnc", "cnc-lathe"], "machine-accuracy": ["ball-screw", "thermal-displacement"]}


def mt_blocks(pattern, tag):
    out = []
    for f in sorted(glob.glob(_D + "/mt/" + pattern)):
        for blk in re.split(r"^@%s " % tag, open(f, encoding="utf-8").read(), flags=re.M)[1:]:
            slug, rest = blk.split("\n", 1)
            head = dict(re.findall(r"^(name|en|lead):\s*(.+)$", rest.split("\n## ", 1)[0], re.M))
            body = "## " + rest.split("\n## ", 1)[1] if "\n## " in rest else ""
            out.append({"slug": slug.strip(), "name": head["name"].strip(), "en": head.get("en", "").strip(), "lead": head["lead"].strip(), "raw": body})
    return out


MT_TYPES, MT_COMPS, MT_AUTOS = mt_blocks("types_*.md", "type"), mt_blocks("components.md", "component"), mt_blocks("automation.md", "automation")
_g = mt_blocks("guides.md", "guide")
MT_OVERVIEW = [g for g in _g if g["slug"] == "overview"][0]
MT_SELECT = [g for g in _g if g["slug"] == "selection"][0]
MT_GUIDES = [g for g in _g if g["slug"] not in ("overview", "selection")]
MT_DIC = {}
for t in MT_TYPES:
    MT_DIC[t["name"]] = "/machine-tools/%s/" % t["slug"]
for nm, sl in COMP_NAMES.items():
    MT_DIC[nm] = "/machine-tools/components/%s/" % sl
for nm, sl in AUTO_NAMES.items():
    MT_DIC[nm] = "/machine-tools/automation/%s/" % sl
MT_DIC.update(PART_URL)
CIDX = {c["n"]: i for i, c in enumerate(cats)}
for t in MT_TYPES:
    t["fam"] = FAM_OF[t["slug"]]
    t["comps"] = list(dict.fromkeys(sl for nm, sl in sorted(COMP_NAMES.items(), key=lambda x: t["raw"].find(x[0]) if x[0] in t["raw"] else 1e9) if nm in t["raw"]))
    t["autos"] = list(dict.fromkeys(sl for nm, sl in sorted(AUTO_NAMES.items(), key=lambda x: t["raw"].find(x[0]) if x[0] in t["raw"] else 1e9) if nm in t["raw"]))
for lst in (MT_TYPES, MT_COMPS, MT_AUTOS, MT_GUIDES, [MT_OVERVIEW, MT_SELECT]):
    for it in lst:
        own = [k for k, v in MT_DIC.items() if v.rstrip("/").endswith("/" + it["slug"])] + [it["name"]]
        it["body"] = md(it["raw"], set(), skip=tuple(own), dic=MT_DIC, minlen=2)
for c in MT_COMPS:
    c["types"] = [t["slug"] for t in MT_TYPES if c["slug"] in t["comps"]]
for a in MT_AUTOS:
    a["types"] = [t["slug"] for t in MT_TYPES if a["slug"] in t["autos"]]
for it in MT_TYPES + MT_AUTOS:
    it["eq"] = CIDX.get(MT_EQ.get(it["slug"]), -1)
    if it["eq"] >= 0:
        cats[it["eq"]]["mt"] = ("/machine-tools/%s/" if it in MT_TYPES else "/machine-tools/automation/%s/") % it["slug"]
        cats[it["eq"]]["mtn"] = it["name"]
for g in MT_GUIDES:
    g["pics"] = GUIDE_PICS.get(g["slug"], [])
MT_ILL = {}
for sl, (fn, vb) in il_mt.MT.items():
    svg_, notes = fn()
    MT_ILL[sl] = {"svg": svg_, "notes": notes, "vb": vb}
SEL_Q = [{"id": "shape", "label": "ワークの形", "def": 0, "opts": [["round", "丸物（軸・円盤）"], ["box", "角物・箱物"], ["plate", "板・平面"], ["gear", "歯車"], ["die", "金型・複雑な曲面"]]},
         {"id": "prec", "label": "求める精度", "def": 0, "opts": [["std", "標準（10μm前後）"], ["high", "高精度（数μm以下）"]]},
         {"id": "vol", "label": "生産量", "def": 1, "opts": [["low", "試作・少量"], ["mid", "中量"], ["high", "大量（専用ライン）"]]},
         {"id": "size", "label": "ワークの大きさ", "def": 1, "opts": [["s", "小物"], ["m", "中物"], ["l", "大物"]]}]
SEL_T = {
    "cnc-lathe": [["round"], ["std"], ["low", "mid", "high"], ["s", "m"], "丸物の外径・内径・端面・ねじを削る基本の機械"],
    "vertical-turning-lathe": [["round"], ["std"], ["low", "mid"], ["l"], "大径で重い円盤・リングを安定して削る"],
    "turn-mill": [["round", "box"], ["std", "high"], ["low", "mid"], ["s", "m"], "旋削と穴あけ・フライスを1台で済ませ、段取りを減らす"],
    "swiss-type-lathe": [["round"], ["std", "high"], ["mid", "high"], ["s"], "細長い小物を棒材から連続して加工する"],
    "vertical-machining-center": [["box", "plate", "die"], ["std"], ["low", "mid"], ["s", "m"], "平面・穴・ポケットを上から加工する汎用機"],
    "horizontal-machining-center": [["box"], ["std", "high"], ["mid", "high"], ["m", "l"], "箱物の多面を割り出して量産加工する"],
    "5-axis-machining-center": [["die", "box"], ["std", "high"], ["low", "mid"], ["s", "m"], "曲面や斜めの面を1回の段取りで加工する"],
    "double-column-machining-center": [["die", "plate", "box"], ["std"], ["low"], ["l"], "大型の金型や構造物を加工する"],
    "cylindrical-grinder": [["round"], ["high"], ["mid", "high"], ["s", "m"], "軸の外径を数μmで仕上げる"],
    "internal-grinder": [["round"], ["high"], ["mid", "high"], ["s", "m"], "穴の内面を高精度に仕上げる"],
    "surface-grinder": [["plate", "box", "die"], ["high"], ["low", "mid"], ["s", "m"], "平面度・平行度を研削で出す"],
    "centerless-grinder": [["round"], ["high"], ["high"], ["s"], "細長い軸の外径を連続で大量に研削する"],
    "gear-hobbing-machine": [["gear"], ["std"], ["mid", "high"], ["s", "m", "l"], "外歯車の歯切りの主力"],
    "gear-grinding-machine": [["gear"], ["high"], ["mid", "high"], ["s", "m"], "焼入れ後の歯面を仕上げ、騒音を抑える"],
    "gear-skiving-machine": [["gear"], ["std"], ["mid", "high"], ["s", "m"], "内歯車を高能率に加工する"],
    "edm": [["die"], ["high"], ["low"], ["s", "m"], "焼入れ鋼や超硬の細かい形状・抜き型を加工する"],
    "laser-machine": [["plate"], ["std"], ["low", "mid", "high"], ["s", "m", "l"], "板材の切断・穴あけを金型なしで行う"],
    "transfer-machine": [["box", "round"], ["std"], ["high"], ["s", "m"], "大量生産専用。工程を分けて同時に加工する"]}
for k in [k for k in list(MT_ILL) if k not in {t["slug"] for t in MT_TYPES + MT_COMPS + MT_AUTOS}]:
    pass
data["mt"] = {"fam": MT_FAM, "types": [{k: v for k, v in t.items() if k != "raw"} for t in MT_TYPES],
              "comps": [{k: v for k, v in t.items() if k != "raw"} for t in MT_COMPS], "autos": [{k: v for k, v in t.items() if k != "raw"} for t in MT_AUTOS],
              "guides": [{k: v for k, v in t.items() if k != "raw"} for t in MT_GUIDES],
              "overview": {k: v for k, v in MT_OVERVIEW.items() if k != "raw"}, "selection": {k: v for k, v in MT_SELECT.items() if k != "raw"},
              "ill": MT_ILL, "sel": {"q": SEL_Q, "t": SEL_T}}
for t in MT_TYPES:
    assert t["slug"] in MT_ILL and t["slug"] in SEL_T, t["slug"]
# operation training scenarios (data/mt/sim/*.json), validated by sim_check
import sim_check  # noqa: E402
_sp = []
SIM = {}
for _f in sorted(glob.glob(_D + "/mt/sim/*.json")):
    _sp += sim_check.check(_f)
    SIM[os.path.basename(_f)[:-5]] = json.load(open(_f, encoding="utf-8"))
if _sp:
    sys.exit("ERROR: training scenarios:\n  " + "\n  ".join(_sp))
SIM_TYPES = [t for t in MT_TYPES if t["slug"] in SIM]
for t in MT_TYPES:
    t["sim"] = SIM[t["slug"]]["title"] if t["slug"] in SIM else None
data["mt"]["types"] = [{k: v for k, v in t.items() if k != "raw"} for t in MT_TYPES]
data["sim"] = SIM
for c in MT_COMPS + MT_AUTOS:
    assert c["slug"] in MT_ILL, c["slug"]

data["site"] = {
    "handle": CFG["handle"], "bio": CFG["bio"], "license": "CC BY-NC 4.0",
    "licenseUrl": "https://creativecommons.org/licenses/by-nc/4.0/deed.ja", "base": BASE + "/",
    "issues": CFG["issues"], "publishedJa": ja_date(CFG["published"]), "quick": CFG["quick"],
    "analytics": bool(CFG.get("cf_analytics_token", "")),
}

# ============================================================ 2. render every route in headless Chromium
tpl = open(B + "/site_tpl.html", encoding="utf-8").read()
tpl = tpl.replace("/*__ILCSS__*/", open(B + "/il.css", encoding="utf-8").read())
CSS_APP = re.search(r"<style>(.*?)</style>", tpl, re.S).group(1)
DEFS = open(B + "/il_defs.svg", encoding="utf-8").read()
for p in parts:
    p.pop("_s", None)
pre = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
os.makedirs(CACHE, exist_ok=True)
open(CACHE + "/prerender.html", "w", encoding="utf-8").write(pre)
for s in systems:
    for p in s["parts"]:
        p["_s"] = s

ROUTES = [{"t": "home", "u": "/"}, {"t": "systems", "u": "/systems/"}, {"t": "pt", "u": "/powertrain/"}, {"t": "map", "u": "/map/"},
          {"t": "eqi", "u": "/equipment/"}, {"t": "methods", "u": "/methods/"}, {"t": "about", "u": "/about/"},
          {"t": "search", "u": "/search/"}, {"t": "404", "u": "/404.html"}]
ROUTES += [{"t": "sys", "k": s["slug"], "u": "/systems/%s/" % s["slug"], "o": s} for s in systems]
ROUTES += [{"t": "part", "k": p["slug"], "u": "/parts/%s/" % p["slug"], "o": p} for p in parts]
ROUTES += [{"t": "op", "k": p["slug"], "no": o["no"], "u": "/parts/%s/op%d/" % (p["slug"], o["no"]), "o": o, "p": p} for p in parts for o in p["ops"]]
ROUTES += [{"t": "eqg", "k": gs, "u": "/equipment/group/%s/" % gs, "gi": gi} for gi, gs in enumerate(data["gslug"])]
ROUTES += [{"t": "eq", "k": c["slug"], "u": "/equipment/%s/" % c["slug"], "o": c, "ci": ci} for ci, c in enumerate(cats)]
ROUTES += [{"t": "method", "k": k["slug"], "u": "/methods/%s/" % k["slug"], "o": k, "ki": ki} for ki, k in enumerate(kinds)]
ROUTES += [{"t": "mthome", "u": "/machine-tools/", "o": MT_OVERVIEW}, {"t": "mtcomps", "u": "/machine-tools/components/"},
           {"t": "mtautos", "u": "/machine-tools/automation/"}, {"t": "mtselect", "u": "/machine-tools/guide/", "o": MT_SELECT}]
ROUTES += [{"t": "mttype", "k": t["slug"], "u": "/machine-tools/%s/" % t["slug"], "o": t} for t in MT_TYPES]
ROUTES += [{"t": "mtcomp", "k": c["slug"], "u": "/machine-tools/components/%s/" % c["slug"], "o": c} for c in MT_COMPS]
ROUTES += [{"t": "mtauto", "k": c["slug"], "u": "/machine-tools/automation/%s/" % c["slug"], "o": c} for c in MT_AUTOS]
ROUTES += [{"t": "mtguide", "k": g["slug"], "u": "/machine-tools/guide/%s/" % g["slug"], "o": g} for g in MT_GUIDES]
if SIM_TYPES:
    ROUTES += [{"t": "mtsimhub", "u": "/machine-tools/training/"}, {"t": "mttrouble", "u": "/machine-tools/troubles/"}]
    ROUTES += [{"t": "mtsim", "k": t["slug"], "u": "/machine-tools/%s/training/" % t["slug"], "o": t} for t in SIM_TYPES]

from playwright.sync_api import sync_playwright  # noqa: E402

with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1280, "height": 900}, reduced_motion="reduce", color_scheme="light")
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + CACHE + "/prerender.html")
    pg.wait_for_function("window.__render !== undefined")
    assert not errs, errs
    SHELL = pg.evaluate("window.__shell()")
    MTPROMO = pg.evaluate("(r) => window.__render(r)", {"t": "mtpromo"})["html"]
    MET = pg.evaluate("window.__met()")
    for r in ROUTES:
        res = pg.evaluate("(r) => window.__render(r)", {k: v for k, v in r.items() if k in ("t", "k", "no")})
        assert res and res["html"], r["u"]
        r["html"], r["nav"], r["crumbs"] = res["html"], res["nav"], res["crumbs"]
    assert not errs, errs
    br.close()

# ============================================================ 3. what each page is (titles, descriptions, index or not)
KT = {"歯車": "歯切り", "切削": "切削", "研削": "研削", "鍛造": "鍛造", "鋳造": "鋳造", "プレス": "プレス", "熱処理": "熱処理", "表面処理": "表面処理",
      "接合": "接合", "成形": "成形", "塗装": "塗装", "巻線": "巻線", "組立": "組立", "電子": "実装", "化学": "電極加工"}
SKIPK = {"素材", "検査", "物流", "保全", "組立"}
use = defaultdict(list)
for p in parts:
    for o in p["ops"]:
        for r in o["m"]:
            use[r[0]].append((p, o, r, "m"))
        for r in o["x"]:
            use[r[0]].append((p, o, r, "i"))


def clip(s, n=118):
    s = re.sub(r"\s+", "", s)
    if len(s) <= n:
        return s
    cut = s[:n]
    j = max(cut.rfind("。"), cut.rfind("、"))
    return (cut[:j] if j > n * .6 else cut[:n - 1]) + "…"


def part_title(p):
    ks = [kinds[o["k"]]["n"] for o in p["ops"] if kinds[o["k"]]["n"] in KT and kinds[o["k"]]["n"] not in SKIPK]
    pick = []
    if ks:
        pick.append(ks[0])
        rest = Counter(k for k in ks if k != ks[0] and k not in ("熱処理", "表面処理", "塗装")) or Counter(k for k in ks if k != ks[0])
        if rest:
            top = max(rest.values())
            pick.append([k for k in ks if rest.get(k) == top][0])
    lead = "・".join(KT[k] for k in pick)
    return "%sの製造工程｜%s%d工程と設備を図解" % (p["name"], (lead + "など") if lead else "", len(p["ops"]))


def part_desc(p):
    seq = "→".join(o["n"] for o in p["ops"][:5]) + ("→…" if len(p["ops"]) > 5 else "")
    return clip("%sは%sの%d工程でつくられる。使う工作機械・検査機と管理ポイントを図解で解説。" % (p["name"], seq, len(p["ops"])), 130)


for r in ROUTES:
    t = r["t"]
    r["index"] = True
    if t == "home":
        r["title"], r["full"] = SITE + "｜部品・工程・工作機械を図解で知る", True
        r["desc"] = "クルマの部品がどんな工程と工作機械・検査機でつくられるかを図解で解説。%d部品・%d工程・%d設備と、EV・ハイブリッド・エンジン車の違いまで。" % (len(parts), sum(len(p["ops"]) for p in parts), len(cats))
        r["eyebrow"], r["name"], r["stats"] = "AUTOMOTIVE MANUFACTURING ATLAS", "クルマは、工程でできている。", "%d部品・%d工程・%d設備" % (len(parts), sum(len(p["ops"]) for p in parts), len(cats))
    elif t == "systems":
        r["title"] = "自動車の部品一覧（系統別）｜%d部品の製造工程" % len(parts)
        r["desc"] = "自動車を%d系統に分け、エンジン・駆動系・シャシー・電動化ユニットなど%d部品の製造工程と使う設備をまとめた一覧。" % (len(systems), len(parts))
        r["eyebrow"], r["name"], r["stats"] = "SYSTEMS", "系統から、部品へ。", "%d系統・%d部品" % (len(systems), len(parts))
    elif t == "sys":
        s = r["o"]
        n_ops = sum(len(p["ops"]) for p in s["parts"])
        r["title"] = "%sの部品と製造工程｜%d部品・%d工程を図解" % (s["name"], len(s["parts"]), n_ops)
        r["desc"] = clip(s["desc"] + " 収録部品：" + "、".join(p["name"] for p in s["parts"]))
        r["eyebrow"], r["name"], r["stats"] = "SYSTEM", s["name"], "%d部品・%d工程" % (len(s["parts"]), n_ops)
    elif t == "part":
        p = r["o"]
        r["title"], r["desc"] = part_title(p), part_desc(p)
        mc = {x[0] for o in p["ops"] for x in o["m"]}
        r["eyebrow"], r["name"], r["stats"] = "PART · " + p["_s"]["name"], p["name"], "%d工程・設備%d・検査%d" % (len(p["ops"]), len(mc), len({x[0] for o in p["ops"] for x in o["x"]}))
    elif t == "op":
        o, p = r["o"], r["p"]
        r["index"] = False
        r["title"] = "%s OP%d %s｜工程図と設備" % (p["name"], o["no"], o["n"])
        r["desc"] = clip("%sのOP%d「%s」。%s" % (p["name"], o["no"], o["n"], o["d"]))
    elif t == "pt":
        r["title"] = "EVとエンジン車の部品・製造工程の違い｜必要な設備を比較"
        m0, m4 = MET[0], MET[4]
        r["desc"] = "ガソリン・ディーゼル・ハイブリッド・軽自動車・EVで、部品構成と工程数、必要な工作機械がどう変わるかを比較。EVの機械加工はガソリン車の約%d%%（本図鑑の目安）。" % m4["vol"]
        r["eyebrow"], r["name"], r["stats"] = "POWERTRAIN", "EVとエンジン車、つくり方の違い", "ガソリン %d工程 → EV %d工程" % (m0["ops"], m4["ops"])
    elif t == "map":
        n_ops = sum(len(p["ops"]) for p in parts)
        r["title"] = "自動車部品の全工程マップ｜%d部品・%d工程を一覧" % (len(parts), n_ops)
        r["desc"] = "%d部品・%d工程を1枚に。部品ごとに加工の順番と工法（鋳造・鍛造・切削・研削・熱処理・検査など）を色分けして一覧できる工程マップ。" % (len(parts), n_ops)
        r["eyebrow"], r["name"], r["stats"] = "PROCESS MAP", "全工程を、一枚に。", "%d部品・%d工程" % (len(parts), n_ops)
    elif t == "eqi":
        r["title"] = "自動車部品の生産設備・検査装置一覧｜%d種類を%d分類で解説" % (len(cats), len(groups))
        r["desc"] = "旋盤・マシニングセンタ・研削盤・歯車加工機から、鋳造・プレス・溶接設備、三次元測定機やX線検査装置まで。自動車部品の工場で使う%d種類の設備を分類して解説。" % len(cats)
        r["eyebrow"], r["name"], r["stats"] = "EQUIPMENT", "%dの設備。" % len(cats), "%d分類" % len(groups)
    elif t == "eqg":
        gi = r["gi"]
        lst = [ci for ci, c in enumerate(cats) if c["g"] == gi]
        lst.sort(key=lambda ci: (-len(use[ci]), ci))
        r["title"] = "%sの設備の種類｜%sなど%d種類" % (groups[gi], "・".join(cats[ci]["n"] for ci in lst[:2]), len(lst))
        r["desc"] = clip("%sに分類される%d種類の設備（%sなど）の仕組みと、自動車部品のどの工程で使われるかを解説。" % (groups[gi], len(lst), "、".join(cats[ci]["n"] for ci in lst[:3])))
        r["eyebrow"], r["name"], r["stats"] = "EQUIPMENT GROUP", groups[gi], "%d種類" % len(lst)
        r["ci0"] = lst[0]
    elif t == "eq":
        c, ci = r["o"], r["ci"]
        r["index"] = bool(c.get("idx"))
        r["title"] = ("%sの自動車部品での使われ方｜工程と使用例" if c.get("mt") else "%sとは｜仕組みと自動車部品での使われ方" if r["index"] else "%s｜使われる自動車部品と工程") % c["n"]
        r["desc"] = clip(c["d"])
        r["eyebrow"], r["name"], r["stats"] = "EQUIPMENT · " + groups[c["g"]], c["n"], "%d工程・%d部品で使用" % (len(use[ci]), len({x[0]["slug"] for x in use[ci]}))
    elif t == "methods":
        r["title"] = "加工法一覧｜自動車部品をつくる%dの工法" % len(kinds)
        r["desc"] = "鋳造・鍛造・プレス・切削・研削・歯切り・熱処理・溶接など、自動車部品をつくる%dの加工法を、仕組み・種類・使う設備と一緒に解説。" % len(kinds)
        r["eyebrow"], r["name"], r["stats"] = "PROCESSES", "加工法から探す。", "%dの工法" % len(kinds)
    elif t == "method":
        k = r["o"]
        r["index"] = bool(k.get("idx"))
        nm = k.get("title") or k["n"]
        r["title"] = ("%sとは｜種類・仕組みと自動車部品での使われ方" if r["index"] else "%s｜自動車部品の工程と設備") % nm
        r["desc"] = clip(k.get("lead") or k["d"])
        n = sum(1 for p in parts for o in p["ops"] if o["k"] == r["ki"])
        r["eyebrow"], r["name"], r["stats"] = "PROCESS", nm, "%d工程" % n
    elif t == "mthome":
        r["title"] = "工作機械とは｜種類・構造・選び方を図解"
        r["desc"] = clip(MT_OVERVIEW["lead"] + " 旋盤・マシニングセンタ・研削盤・歯車加工機など%d機種の構造と、主軸・ボールねじなどの構成部品、自動化まで。" % len(MT_TYPES), 130)
        r["eyebrow"], r["name"], r["stats"] = "MACHINE TOOL ATLAS", "工作機械図鑑", "%d機種・%d構成部品・%d自動化" % (len(MT_TYPES), len(MT_COMPS), len(MT_AUTOS))
    elif t == "mttype":
        it = r["o"]
        r["title"] = "%sとは｜構造・仕組み・種類を図解" % it["name"]
        r["desc"] = clip(it["lead"])
        r["eyebrow"], r["name"], r["stats"] = "MACHINE TOOL · " + [f["n"] for f in MT_FAM if f["id"] == it["fam"]][0], it["name"], "構造・種類・仕様の見方・選び方"
    elif t == "mtcomp":
        it = r["o"]
        r["title"] = "%sとは｜仕組み・種類と工作機械での役割" % it["name"]
        r["desc"] = clip(it["lead"])
        r["eyebrow"], r["name"], r["stats"] = "MACHINE TOOL COMPONENT", it["name"], "仕組み・種類・点検のポイント"
    elif t == "mtauto":
        it = r["o"]
        r["title"] = ("%sとは｜仕組み・種類と導入のポイント" if len(it["name"]) <= 12 else "%s｜仕組みと導入のポイント") % it["name"]
        r["desc"] = clip(it["lead"])
        r["eyebrow"], r["name"], r["stats"] = "AUTOMATION", it["name"], "仕組み・種類・導入のポイント"
    elif t == "mtcomps":
        r["title"] = "工作機械の構成部品｜主軸・ボールねじ・リニアガイドなど%d種" % len(MT_COMPS)
        r["desc"] = "工作機械の精度と速さを決める構成部品を図解。主軸と軸受、ボールねじ、リニアガイド、サーボモータ、NC装置、ATC、ツールホルダ、チャック、熱変位まで。"
        r["eyebrow"], r["name"], r["stats"] = "COMPONENTS", "工作機械の構成部品", "%d種" % len(MT_COMPS)
    elif t == "mtautos":
        r["title"] = "工作機械の自動化・周辺機器｜ローダ・ロボット・パレットチェンジャ"
        r["desc"] = "ガントリーローダ、ロボット、パレットチェンジャ、バーフィーダ、機上計測、切りくず処理、FMSまで。工作機械を無人で動かすための周辺機器を図解。"
        r["eyebrow"], r["name"], r["stats"] = "AUTOMATION", "自動化・周辺機器", "%d種" % len(MT_AUTOS)
    elif t == "mtselect":
        r["title"] = "工作機械の選び方｜用途別の早見表と機種診断"
        r["desc"] = clip(MT_SELECT["lead"])
        r["eyebrow"], r["name"], r["stats"] = "GUIDE", "工作機械の選び方", "ワークの形・精度・生産量から"
    elif t == "mtguide":
        it = r["o"]
        r["title"] = "%s｜比較表と選び分けの目安" % it["name"]
        r["desc"] = clip(it["lead"])
        r["eyebrow"], r["name"], r["stats"] = "GUIDE · COMPARE", it["name"], "比較表と選び分けの目安"
    elif t == "mtsim":
        it, sc = r["o"], SIM[r["k"]]
        r["title"] = "%sの操作トレーニング｜段取りとトラブルを体験" % it["name"]
        top3 = [v["title"] for v in sc["incidents"].values() if v["sev"] == 3][:1]
        r["desc"] = clip("%sの基本操作を、%dステップのゲームで体験。「%s」の手順を自分で操作し、間違えると起きるトラブル%d件（%sなど）の原因と対策も学べる。" % (it["name"], len(sc["steps"]), sc["title"], len(sc["incidents"]), "、".join(top3)), 130)
        r["eyebrow"], r["name"], r["stats"] = "OPERATION TRAINING", it["name"] + "の操作トレーニング", "%dステップ・トラブル%d件" % (len(sc["steps"]), len(sc["incidents"]))
    elif t == "mtsimhub":
        n_inc = sum(len(SIM[x["slug"]]["incidents"]) for x in SIM_TYPES)
        r["title"] = "工作機械の操作トレーニング｜%d機種の段取りとトラブルを体験" % len(SIM_TYPES)
        r["desc"] = "NC旋盤、マシニングセンタ、研削盤、歯車加工機など%d機種の基本操作を、1ステップずつ自分で体験。設定やワークの取付けを間違えると、衝突・飛散・不良などのトラブル（全%d件）が起き、原因と対策を学べる。" % (len(SIM_TYPES), n_inc)
        r["eyebrow"], r["name"], r["stats"] = "OPERATION TRAINING", "工作機械の操作トレーニング", "%d機種・トラブル%d件" % (len(SIM_TYPES), n_inc)
    elif t == "mttrouble":
        n_inc = sum(len(SIM[x["slug"]]["incidents"]) for x in SIM_TYPES)
        r["title"] = "工作機械のトラブル事例集｜衝突・飛散・不良の原因と対策%d件" % n_inc
        r["desc"] = "工作機械で起きやすい衝突、ワークや工具の飛散、火災、人への危険、寸法不良などのトラブル%d件を種類別にまとめた事例集。%d機種の操作トレーニングと連動し、原因・損失・防ぎ方を解説。" % (n_inc, len(SIM_TYPES))
        r["eyebrow"], r["name"], r["stats"] = "TROUBLE CASEBOOK", "工作機械のトラブル事例集", "%d件・%d機種" % (n_inc, len(SIM_TYPES))
    elif t == "about":
        r["title"] = "この図鑑について｜運営者・編集方針・利用条件"
        r["desc"] = "自動車製造工程図鑑の運営者（%s）、編集方針、図解と文章の利用条件（CC BY-NC 4.0）、誤りの報告方法。" % CFG["handle"]
        r["eyebrow"], r["name"], r["stats"] = "ABOUT", "この図鑑について", CFG["handle"]
    elif t == "search":
        r["index"], r["title"], r["desc"] = False, "検索", "部品・工程・設備・メーカー・材料を検索。"
    elif t == "404":
        r["index"], r["title"], r["desc"] = False, "ページが見つかりません", "お探しのページは見つかりませんでした。"
    if not r.get("full"):
        r["title"] = r["title"] + "｜" + ("工作機械図鑑" if t.startswith("mt") else SITE)

# ============================================================ 4. content hashes → stable dates
def sig(r):
    t = r["t"]
    if t == "part":
        p = r["o"]
        return jdump([p["name"], p["mat"], p["desc"], [[o["no"], o["n"], o["d"], o["kp"], [cats[x[0]]["n"] for x in o["m"]], [cats[x[0]]["n"] for x in o["x"]]] for o in p["ops"]], data["pt"]["q"].get(p["_s"]["id"] + "." + p["id"])])
    if t == "op":
        o = r["o"]
        return jdump([r["p"]["name"], o["no"], o["n"], o["d"], o["kp"], o["m"] and [[cats[x[0]]["n"], x[1], x[2]] for x in o["m"]], [[cats[x[0]]["n"], x[1], x[2]] for x in o["x"]]])
    if t == "eq":
        c = r["o"]
        return jdump([c["n"], c["d"], c.get("body"), groups[c["g"]], [[x[0]["name"], x[1]["n"], x[2][1], x[2][2]] for x in use[r["ci"]]]] + ([c["mt"]] if c.get("mt") else []))
    if t == "method":
        k = r["o"]
        return jdump([k.get("title"), k.get("lead"), k.get("body"), k["d"], [[p["name"], o["n"]] for p in parts for o in p["ops"] if o["k"] == r["ki"]]])
    if t == "eqg":
        return jdump([groups[r["gi"]], [[c["n"], c["d"]] for c in cats if c["g"] == r["gi"]]])
    if t == "sys":
        s = r["o"]
        return jdump([s["name"], s["desc"], [p["name"] for p in s["parts"]]])
    if t == "home":
        return jdump([data["pt"], MET, [p["name"] for p in parts], [c["n"] for c in cats], len(MT_TYPES)])
    if t == "pt":
        return jdump([data["pt"], MET, [p["name"] for p in parts], [c["n"] for c in cats]])
    if t == "about":
        return jdump([CFG["handle"], CFG["bio"], CFG["issues"]])
    if t == "mtsim":
        return jdump([r["o"]["name"], SIM[r["k"]], [x["slug"] for x in SIM_TYPES]])
    if t in ("mtsimhub", "mttrouble"):
        return jdump([t, [[x["name"], SIM[x["slug"]]["title"], SIM[x["slug"]]["level"], SIM[x["slug"]]["minutes"], len(SIM[x["slug"]]["steps"]), [[k, v["title"], v["sev"], v["fx"]] for k, v in SIM[x["slug"]]["incidents"].items()]] for x in SIM_TYPES]])
    if t.startswith("mt"):
        o = r.get("o") or {}
        return jdump([t, o.get("name"), o.get("lead"), o.get("raw"), o.get("comps"), o.get("autos"), o.get("types")] + ([o.get("sim")] if o.get("sim") else []) + ([len(SIM_TYPES)] if t == "mthome" else []) + [
                      [[x["name"], x["lead"]] for x in (MT_TYPES if t in ("mthome",) else MT_COMPS if t == "mtcomps" else MT_AUTOS if t == "mtautos" else MT_GUIDES if t == "mtselect" else [])]])
    return jdump([[p["name"], len(p["ops"])] for p in parts] + [c["n"] for c in cats] + [k["n"] for k in kinds])


urls_path = STATE + "/urls.json"
URLS = json.load(open(urls_path, encoding="utf-8")) if os.path.exists(urls_path) else {}
REDIR = {}
if os.path.exists(STATE + "/redirects.txt"):
    for l in open(STATE + "/redirects.txt", encoding="utf-8"):
        l = l.split("#")[0].strip()
        if l:
            a, b = l.split()
            REDIR[a] = b
new_urls = {r["u"] for r in ROUTES}
lost = [u for u in URLS if u not in new_urls and u not in REDIR]
if lost:
    sys.exit("ERROR: published URLs disappeared without a redirect (add them to state/redirects.txt):\n  " + "\n  ".join(lost))
for r in ROUTES:
    h = sha(sig(r))[:16]
    rec = URLS.get(r["u"])
    if not rec:
        rec = {"h": h, "pub": TODAY, "mod": TODAY}
    elif rec["h"] != h:
        rec = {"h": h, "pub": rec["pub"], "mod": TODAY}
    rec["idx"] = r["index"]
    URLS[r["u"]] = rec
    r["pub"], r["mod"] = rec["pub"], rec["mod"]

# ============================================================ 5. assets: css, fonts, js, search index
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT + "/assets/fonts")


def mincss(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{};:,>])\s*", r"\1", s)
    return s.replace(";}", "}").strip()


CSS = mincss(CSS_APP + open(B + "/site.css", encoding="utf-8").read())
text_all = "".join(r["html"] for r in ROUTES) + "".join(r["title"] + r["desc"] for r in ROUTES) + SHELL["mm"] + SHELL["qs"]
USED = set(ord(ch) for ch in html.unescape(re.sub(r"<[^>]+>", " ", text_all)))
USED |= set(range(0x20, 0x7F))


def ranges(ur):
    out = []
    for part in ur.split(","):
        part = part.strip().replace("U+", "").replace("u+", "")
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a, 16), int(b, 16)))
        elif "?" in part:
            out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
        else:
            out.append((int(part, 16), int(part, 16)))
    return out


font_css, nfiles, fbytes = [], 0, 0
HEAD_TXT = "".join(re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", "".join(r["html"] for r in ROUTES), re.S)) + "工程図鑑自動車製造工程図鑑"
HEAD_USED = set(ord(ch) for ch in html.unescape(re.sub(r"<[^>]+>", "", HEAD_TXT))) | set(range(0x20, 0x7F))
for fam, fdir, weights in (("Zen Kaku Gothic New", "zen-kaku-gothic-new", (700,)), ("Jost", "jost", (200, 300, 400, 500))):
    need_cp = HEAD_USED if fam != "Jost" else USED
    for w in weights:
        src = open("%s/%s/%d.css" % (FONTS, fdir, w), encoding="utf-8").read()
        for blk in re.findall(r"@font-face\s*{[^}]*}", src):
            m = re.search(r"url\(\./files/([^)]+\.woff2)\)", blk)
            ur = re.search(r"unicode-range:\s*([^;]+);", blk)
            if not m:
                continue
            if fam == "Jost" and ("latin-ext" in m.group(1) or "cyrillic" in m.group(1)):
                continue
            if ur:
                rg = ranges(ur.group(1))
                if not any(a <= cp <= b for cp in need_cp for a, b in rg):
                    continue
            fn = m.group(1)
            shutil.copy("%s/%s/files/%s" % (FONTS, fdir, fn), OUT + "/assets/fonts/" + fn)
            nfiles += 1
            fbytes += os.path.getsize(OUT + "/assets/fonts/" + fn)
            font_css.append("@font-face{font-family:'%s';font-style:normal;font-display:swap;font-weight:%d;src:url(/assets/fonts/%s) format('woff2');%s}" % (fam, w, fn, ("unicode-range:%s;" % ur.group(1).strip()) if ur else ""))
fcss = "".join(font_css)
FCSS = "/assets/fonts.%s.css" % sha(fcss)[:10]
open(OUT + FCSS, "w", encoding="utf-8").write(fcss)

simjs = open(B + "/site_sim.js", encoding="utf-8").read()
SIMJS = "/assets/sim.%s.js" % sha(simjs)[:10]
open(OUT + SIMJS, "w", encoding="utf-8").write(simjs)
SIMCSS_ST = mincss(open(B + "/site_sim_static.css", encoding="utf-8").read())
SIMCSS = mincss(open(B + "/site_sim.css", encoding="utf-8").read()) + SIMCSS_ST
SIMT = ("mtsim", "mtsimhub", "mttrouble")
appjs = open(B + "/site_app.js", encoding="utf-8").read()
APPJS = "/assets/app.%s.js" % sha(appjs)[:10]
open(OUT + APPJS, "w", encoding="utf-8").write(appjs)


def anchor(p, o):
    return "/parts/%s/#op%d" % (p["slug"], o["no"])


SI = {"p": [[p["name"], p["mat"], p["desc"], "/parts/%s/" % p["slug"], p["_s"]["name"]] for p in parts],
      "c": [[c["n"], c["d"], "/equipment/%s/" % c["slug"], groups[c["g"]]] for c in cats],
      "k": [[k.get("title") or k["n"], "/methods/%s/" % k["slug"]] for k in kinds],
      "o": [[p["name"], "OP%d" % o["no"], o["n"], o["d"], o["kp"], anchor(p, o)] for p in parts for o in p["ops"]],
      "r": [[cats[x[0]]["n"], x[1], x[2], p["name"], "OP%d" % o["no"], o["n"], anchor(p, o), role] for p in parts for o in p["ops"] for role, rows in (("m", o["m"]), ("i", o["x"])) for x in rows]}
SI["m"] = ([[t["name"], "工作機械", "/machine-tools/%s/" % t["slug"]] for t in MT_TYPES] + [[c["name"], "構成部品", "/machine-tools/components/%s/" % c["slug"]] for c in MT_COMPS] +
           [[c["name"], "自動化", "/machine-tools/automation/%s/" % c["slug"]] for c in MT_AUTOS] + [[g["name"], "ガイド", "/machine-tools/guide/%s/" % g["slug"]] for g in MT_GUIDES] +
           [["工作機械の選び方", "ガイド", "/machine-tools/guide/"], ["工作機械とは", "工作機械図鑑", "/machine-tools/"]] +
           [[t["name"] + "の操作トレーニング", "トレーニング", "/machine-tools/%s/training/" % t["slug"]] for t in SIM_TYPES] +
           ([["工作機械の操作トレーニング", "トレーニング", "/machine-tools/training/"], ["工作機械のトラブル事例集", "トラブル事例", "/machine-tools/troubles/"]] if SIM_TYPES else []))
sij = json.dumps(SI, ensure_ascii=False, separators=(",", ":"))
SIURL = "/assets/search.%s.json" % sha(sij)[:10]
open(OUT + SIURL, "w", encoding="utf-8").write(sij)

# ============================================================ 6. social images (1200x630), cached by content
OGDIR = OUT + "/og"
os.makedirs(OGDIR)


def og_name(r):
    t = r["t"]
    if t in ("mttype", "mtcomp", "mtauto", "mtguide"):
        return "mt-%s-%s.jpg" % (t[2:], r["k"])
    if t == "mtsim":
        return "mt-training-%s.jpg" % r["k"]
    if t in ("mtsimhub", "mttrouble"):
        return {"mtsimhub": "mt-training.jpg", "mttrouble": "mt-troubles.jpg"}[t]
    if t in ("mthome", "mtcomps", "mtautos", "mtselect"):
        return {"mthome": "machine-tools.jpg", "mtcomps": "mt-components.jpg", "mtautos": "mt-automation.jpg", "mtselect": "mt-guide.jpg"}[t]
    if t in ("part", "sys", "eq", "method", "eqg"):
        return "%s-%s.jpg" % ({"part": "part", "sys": "system", "eq": "equipment", "method": "method", "eqg": "group"}[t], r["k"])
    return {"home": "site.jpg", "systems": "systems.jpg", "pt": "powertrain.jpg", "map": "map.jpg", "eqi": "equipment.jpg", "methods": "methods.jpg", "about": "about.jpg"}.get(t)


BY_U = {r["u"]: r for r in ROUTES}
for r in ROUTES:
    if r["t"] == "op":
        r["og"] = "/og/part-%s.jpg" % r["k"]
    elif r["t"] == "eq" and not r["index"]:
        r["og"] = "/og/group-%s.jpg" % data["gslug"][r["o"]["g"]]
    elif r["t"] == "method" and not r["index"]:
        r["og"] = "/og/methods.jpg"
    elif r["t"] in ("search", "404"):
        r["og"] = "/og/site.jpg"
    else:
        r["og"] = "/og/" + og_name(r)


def first_svg(h):
    m = re.search(r'<svg class="ilu[^"]*"[^>]*>.*?</svg>', h, re.S)
    return m.group(0) if m else ""


OGSRC = {"home": ("home", None), "pt": ("pt", None)}
og_jobs = []
for r in ROUTES:
    name = og_name(r)
    if not name or r["t"] in ("op", "search", "404") or (r["t"] in ("eq", "method") and not r["index"]):
        continue
    pic = first_svg(r["html"])
    if r["t"] == "method" or not pic:
        # method pages have no hero drawing: use the most-used equipment of that method
        if r["t"] == "method":
            cnt = Counter(x[0] for p in parts for o in p["ops"] if o["k"] == r["ki"] for x in (o["m"] or o["x"]))
            ci = cnt.most_common(1)[0][0]
            pic = first_svg(BY_U["/equipment/%s/" % cats[ci]["slug"]]["html"])
        elif r["t"] == "methods":
            pic = first_svg(BY_U["/"]["html"])
        elif r["t"] == "about":
            pic = first_svg(BY_U["/"]["html"])
        elif r["t"] == "mtselect":
            pic = first_svg(BY_U["/machine-tools/"]["html"])
        elif r["t"] in ("mtsimhub", "mttrouble"):
            pic = first_svg(BY_U["/machine-tools/cnc-lathe/training/" if r["t"] == "mtsimhub" else "/machine-tools/vertical-machining-center/training/"]["html"])
        elif r["t"] == "eqg":
            pic = first_svg(BY_U["/equipment/%s/" % cats[r["ci0"]]["slug"]]["html"])
    if r["t"] == "eqg":
        pic = first_svg(BY_U["/equipment/%s/" % cats[r["ci0"]]["slug"]]["html"])
    key = sha(jdump([r["eyebrow"], r["name"], r["stats"], pic, 4] + ([SIMCSS] if "simv" in pic else [])))[:20]
    og_jobs.append((r, name, pic, key))

need = [j for j in og_jobs if not os.path.exists(CACHE + "/og/%s.jpg" % j[3])]
if need:
    zcss = open("%s/zen-kaku-gothic-new/700.css" % FONTS).read().replace("./files/", "file://%s/zen-kaku-gothic-new/files/" % FONTS)
    zcss += open("%s/zen-kaku-gothic-new/500.css" % FONTS).read().replace("./files/", "file://%s/zen-kaku-gothic-new/files/" % FONTS)
    jcss = open("%s/jost/300.css" % FONTS).read().replace("./files/", "file://%s/jost/files/" % FONTS)
    jcss += open("%s/jost/500.css" % FONTS).read().replace("./files/", "file://%s/jost/files/" % FONTS)
    OGCSS = """
    html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#0A0A0B}
    .og{position:relative;width:1200px;height:630px;display:grid;grid-template-columns:560px 1fr;background:radial-gradient(90% 90% at 78% 40%,#2A2B2F 0%,#141416 55%,#0A0A0B 100%);color:#F5F5F7;font-family:'Zen Kaku Gothic New',sans-serif}
    .tx{padding:64px 0 56px 68px;display:flex;flex-direction:column}
    .eb{font:500 17px 'Jost',sans-serif;letter-spacing:.28em;color:#A1A1A6;text-transform:uppercase}
    h1{margin:26px 0 0;font-weight:700;line-height:1.16;letter-spacing:-.005em}
    .st{margin-top:22px;font:500 24px 'Zen Kaku Gothic New',sans-serif;color:#D2D2D7}
    .br{margin-top:auto;display:flex;align-items:center;gap:14px;font-weight:700;font-size:22px;letter-spacing:.06em}
    .br small{font:300 14px 'Jost',sans-serif;letter-spacing:.3em;color:#A1A1A6}
    .br svg{width:34px;height:34px;color:#F5F5F7}
    .pic{position:relative;margin:48px 48px 48px 0;border-radius:28px;background:radial-gradient(120% 100% at 50% 12%,#FFFFFF 0%,#F2F2F1 52%,#E6E6E4 100%);display:flex;align-items:center;justify-content:center;overflow:hidden}
    .pic .ilu{width:100%;height:auto}
    .pic .ilu text,.pic .ilu .bal,.pic .ilu .leadl,.pic .ilu .leadd{display:none}
    """
    BRAND = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="13" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M16 3v26M3 16h26" stroke="currentColor" stroke-width="1" opacity=".5"/><path d="M16 16V3a13 13 0 0 1 13 13Z" fill="currentColor"/><path d="M16 16v13A13 13 0 0 1 3 16Z" fill="currentColor"/></svg>'
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": 1200, "height": 630}, color_scheme="light")
        for r, name, pic, key in need:
            nm = r["name"]
            fs = 64 if len(nm) <= 8 else 54 if len(nm) <= 12 else 46 if len(nm) <= 18 else 40
            if "simv" in pic:
                pic = '<div class="ogsim">%s</div>' % pic
            doc = "<!doctype html><html lang=ja><head><meta charset=utf-8><style>%s%s%s%s</style></head><body>%s<div class=og><div class=tx><div class=eb>%s</div><h1 style='font-size:%dpx'>%s</h1><div class=st>%s</div><div class=br>%s<span>%s<br><small>AUTOMOTIVE ATLAS</small></span></div></div><div class=pic>%s</div></div></body></html>" % (
                zcss, jcss, CSS_APP, OGCSS + SIMCSS + ".ogsim{width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#16181C}.ogsim .simv{width:100%;height:auto}", DEFS, html.escape(r["eyebrow"]), fs, html.escape(nm), html.escape(r["stats"]), BRAND, SITE, pic)
            open(CACHE + "/og_tmp.html", "w", encoding="utf-8").write(doc)
            pg.goto("file://" + CACHE + "/og_tmp.html")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(80)
            pg.screenshot(path=CACHE + "/og/%s.jpg" % key, type="jpeg", quality=84)
        br.close()
for r, name, pic, key in og_jobs:
    shutil.copy(CACHE + "/og/%s.jpg" % key, OGDIR + "/" + name)

# ---- favicons (drawn from the brand mark)
FAV = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#0A0A0B"/><g transform="translate(4 4) scale(.75)" color="#F5F5F7"><circle cx="16" cy="16" r="13" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M16 16V3a13 13 0 0 1 13 13Z" fill="currentColor"/><path d="M16 16v13A13 13 0 0 1 3 16Z" fill="currentColor"/></g></svg>'
open(OUT + "/favicon.svg", "w").write(FAV)
if not os.path.exists(CACHE + "/fav-180.png"):
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for sz in (48, 96, 180, 192, 512):
            pg = br.new_page(viewport={"width": sz, "height": sz})
            pg.set_content("<html><body style='margin:0'>%s</body></html>" % FAV.replace("<svg ", "<svg width='%d' height='%d' " % (sz, sz)))
            pg.screenshot(path=CACHE + "/fav-%d.png" % sz, omit_background=True)
        br.close()
for sz in (48, 96, 192, 512):
    shutil.copy(CACHE + "/fav-%d.png" % sz, OUT + "/favicon-%d.png" % sz)
shutil.copy(CACHE + "/fav-180.png", OUT + "/apple-touch-icon.png")
open(OUT + "/site.webmanifest", "w").write(json.dumps({"name": SITE, "short_name": "工程図鑑", "start_url": "/", "display": "standalone", "background_color": "#0A0A0B", "theme_color": "#0A0A0B",
                                                        "icons": [{"src": "/favicon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/favicon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))

# ============================================================ 7. structured data
PERSON = {"@type": "Person", "@id": BASE + "/about/#author", "name": CFG["handle"], "url": BASE + "/about/", "description": CFG["bio"]}
WEBSITE = {"@type": "WebSite", "@id": BASE + "/#website", "name": SITE, "alternateName": "AUTOMOTIVE ATLAS", "url": BASE + "/", "inLanguage": "ja", "publisher": {"@id": PERSON["@id"]}}
LIC = "https://creativecommons.org/licenses/by-nc/4.0/"


def crumbs_ld(r):
    items = [("トップ", "/")] + [(c[0], c[1] if len(c) > 1 else r["u"]) for c in r["crumbs"]]
    if r["t"] == "part":
        items = [("トップ", "/"), ("系統", "/systems/"), (r["o"]["_s"]["name"], "/systems/%s/" % r["o"]["_s"]["slug"]), (r["o"]["name"], r["u"])]
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}


def ld(r):
    g_ = [WEBSITE, PERSON]
    url = BASE + r["u"]
    if r["t"] not in ("home", "404", "search"):
        g_.append(crumbs_ld(r))
    if not r["index"]:
        return g_
    page = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": r["title"], "isPartOf": {"@id": WEBSITE["@id"]}, "inLanguage": "ja"}
    if r["t"] == "about":
        page = {"@type": "ProfilePage", "@id": url + "#webpage", "url": url, "name": r["title"], "mainEntity": {"@id": PERSON["@id"]}, "isPartOf": {"@id": WEBSITE["@id"]}, "inLanguage": "ja",
                "dateCreated": r["pub"], "dateModified": r["mod"]}
        return g_ + [page]
    art = {"@type": "Article", "@id": url + "#article", "headline": r["title"].split("｜")[0][:110], "description": r["desc"], "image": [BASE + r["og"]],
           "author": {"@id": PERSON["@id"]}, "publisher": {"@id": PERSON["@id"]}, "datePublished": r["pub"], "dateModified": r["mod"],
           "inLanguage": "ja", "mainEntityOfPage": {"@id": url + "#webpage"}, "isPartOf": {"@id": WEBSITE["@id"]}, "license": LIC}
    if r["t"] in ("part", "eq", "method", "sys", "eqg", "mttype", "mtcomp", "mtauto", "mtguide"):
        art["about"] = {"@type": "Thing", "name": r["name"]}
    elif r["t"] == "mtsim":
        art["about"] = {"@type": "Thing", "name": r["o"]["name"], "url": BASE + "/machine-tools/%s/" % r["k"]}
    items = None
    if r["t"] == "systems":
        items = [(s["name"], "/systems/%s/" % s["slug"]) for s in systems]
    elif r["t"] == "sys":
        items = [(p["name"], "/parts/%s/" % p["slug"]) for p in r["o"]["parts"]]
    elif r["t"] == "eqi":
        items = [(gname, "/equipment/group/%s/" % gs) for gname, gs in zip(groups, data["gslug"])]
    elif r["t"] == "eqg":
        items = [(c["n"], "/equipment/%s/" % c["slug"]) for c in cats if c["g"] == r["gi"]]
    elif r["t"] == "methods":
        items = [(k.get("title") or k["n"], "/methods/%s/" % k["slug"]) for k in kinds]
    elif r["t"] == "mthome":
        items = [(t["name"], "/machine-tools/%s/" % t["slug"]) for t in MT_TYPES]
    elif r["t"] == "mtcomps":
        items = [(c["name"], "/machine-tools/components/%s/" % c["slug"]) for c in MT_COMPS]
    elif r["t"] == "mtautos":
        items = [(c["name"], "/machine-tools/automation/%s/" % c["slug"]) for c in MT_AUTOS]
    elif r["t"] == "mtselect":
        items = [(g["name"], "/machine-tools/guide/%s/" % g["slug"]) for g in MT_GUIDES]
    elif r["t"] == "mtsimhub":
        items = [(t["name"] + "の操作トレーニング", "/machine-tools/%s/training/" % t["slug"]) for t in SIM_TYPES]
    out = g_ + [page, art]
    if items:
        out.append({"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": BASE + u} for i, (n, u) in enumerate(items)]})
    if r["t"] == "pt":
        out.append({"@type": "Dataset", "name": "パワートレイン別の部品構成・工程数・設備需要（自動車製造工程図鑑）",
                    "description": "ガソリン車・ディーゼル車・ハイブリッド車・軽自動車・電気自動車の5つの代表仕様について、本図鑑に収録した部品ごとの搭載数量と、そこから積み上げた工程数・機械加工の工程数の目安をまとめたデータ。",
                    "url": url, "license": LIC, "creator": {"@id": PERSON["@id"]}, "inLanguage": "ja", "dateModified": r["mod"],
                    "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": BASE + "/powertrain/powertrain-comparison.csv"}]})
    return out


# ============================================================ 8. write pages
NAVS = [("systems", "/systems/", "系統"), ("pt", "/powertrain/", "パワートレイン比較"), ("map", "/map/", "工程マップ"), ("kinds", "/methods/", "加工法"), ("eq", "/equipment/", "設備"), ("mt", "/machine-tools/", "工作機械")]
BRANDSVG = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="13" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M16 3v26M3 16h26" stroke="currentColor" stroke-width="1" opacity=".5"/><path d="M16 16V3a13 13 0 0 1 13 13Z" fill="currentColor"/><path d="M16 16v13A13 13 0 0 1 3 16Z" fill="currentColor"/></svg>'
X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>'


def shell_top(nav):
    links = "".join('<a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if k == nav else "", n) for k, u, n in NAVS)
    return ('<a class="skip" href="#main">本文へスキップ</a>' + DEFS +
            '<header class="gn"><div class="in"><a class="brand" href="/" aria-label="自動車製造工程図鑑 トップへ">%s<span><b>工程図鑑</b><small lang="en">AUTOMOTIVE ATLAS</small></span></a>'
            '<nav aria-label="メイン">%s</nav><div class="icons">'
            '<button class="ib" id="sbtn" type="button" aria-label="検索" aria-controls="sov"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg></button>'
            '<button class="ib menu" id="mbtn" type="button" aria-label="メニュー" aria-controls="mov"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 9h16M4 15h16"/></svg></button>'
            '</div></div></header>'
            '<div class="ov" id="sov" role="dialog" aria-label="検索" aria-modal="true"><button class="ib x" type="button" data-close aria-label="閉じる">%s</button><div class="box"><label class="sr" for="q">検索</label><input id="q" type="search" autocomplete="off" enterkeyhint="search" placeholder="部品・工程・設備・メーカーを検索"><div class="qs" id="qs">%s</div></div></div>'
            '<div class="ov" id="mov" role="dialog" aria-label="メニュー" aria-modal="true"><button class="ib x" type="button" data-close aria-label="閉じる">%s</button><div class="box mm" id="mm">%s</div></div>'
            '<div class="spacer"></div>') % (BRANDSVG, links, X, SHELL["qs"], X, SHELL["mm"])


FOOT = ('<footer class="foot"><div class="wrap in"><div><b>自動車製造工程図鑑</b><span class="en" lang="en" style="letter-spacing:.3em;font-size:10.5px">AUTOMOTIVE MANUFACTURING ATLAS</span></div><div>'
        '<p>工程・設備・数値は乗用車の量産で一般的な構成と目安をまとめたもので、実際の工程はメーカー・車種・生産量によって異なります。部品・工程・設備の数はこの図鑑の分類で数えたものです。パワートレイン比較の数量は代表的な仕様を仮定した目安です。図はすべて模式図です。</p>'
        '<p>代表メーカーは各設備分野でよく知られる例示で、網羅や推奨ではありません。社名・製品ラインアップは変わることがあるため、個別の案件では最新情報を確認してください。</p>'
        '<nav aria-label="フッター"><a href="/">トップ</a><a href="/systems/">系統</a><a href="/powertrain/">パワートレイン比較</a><a href="/map/">工程マップ</a><a href="/methods/">加工法</a><a href="/equipment/">設備</a><a href="/machine-tools/">工作機械図鑑</a><a href="/about/">この図鑑について</a></nav>'
        '<p class="lic">© %s %s ・ 文章と図解は <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.ja" rel="license">CC BY-NC 4.0</a> で提供しています</p>'
        '</div></div></footer>') % (CFG["published"][:4], html.escape(CFG["handle"]))

_cft = re.sub(r"[^0-9a-fA-F]", "", CFG.get("cf_analytics_token", ""))
CFBEACON = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{"token": "%s"}\'></script>' % _cft) if _cft else ""
VERIFY = "".join('<meta name="%s" content="%s">' % (k, html.escape(v)) for k, v in CFG.get("verify", {}).items() if v)


def esc_a(s):
    return html.escape(s, quote=True)


HUB_H1 = {"/systems/": "自動車の部品一覧（系統別）", "/map/": "自動車部品の全工程マップ", "/equipment/": "自動車部品の生産設備・検査装置一覧",
          "/methods/": "自動車部品の加工法一覧", "/powertrain/": "パワートレイン別 部品・工程・設備の比較"}
HUB_H2 = {"/systems/": ('<div class="grid-cards">', "系統の一覧"), "/map/": ('<div class="msys">', "部品ごとの工程")}


def page(r):
    url = BASE + (r["u"] if r["u"] != "/404.html" else "/404.html")
    body = r["html"]
    if r["u"] in HUB_H1:
        # the subject name is the h1; the tagline stays as the big display line
        body = re.sub(r'<h1 class="(d[12])"([^>]*)>(.*?)</h1>', lambda m: '<h1 class="kicker">%s</h1><p class="%s"%s>%s</p>' % (HUB_H1[r["u"]], m.group(1), m.group(2), m.group(3)), body, count=1, flags=re.S)
    if r["t"] == "home":
        body = body.replace('<section class="sec paper"><div class="wrap"><div class="hd row"><div><p class="eyebrow">EQUIPMENT</p>', MTPROMO + '<section class="sec paper"><div class="wrap"><div class="hd row"><div><p class="eyebrow">EQUIPMENT</p>', 1)
    if r["t"] == "eq" and r["o"].get("mt"):
        c = r["o"]
        blk = ('<section class="sec tight" style="padding-bottom:0"><div class="wrap"><a class="mtlink" href="%s"><span class="eyebrow" lang="en">MACHINE TOOL ATLAS</span>'
               '<b>%sの構造・種類・選び方</b><span>工作機械図鑑で、主な部位の名前と仕組みを図解で見る</span></a></div></section>') % (c["mt"], html.escape(c["mtn"]))
        for mk in ('<p class="eyebrow">BY POWERTRAIN</p>', '<p class="eyebrow">MAKERS</p>', "<p class=\"eyebrow\">WHERE IT'S USED</p>"):
            i = body.find(mk)
            if i >= 0:
                j = body.rfind("<section", 0, i)
                body = body[:j] + blk + body[j:]
                break
    if r["u"] in HUB_H2:
        a, t = HUB_H2[r["u"]]
        body = body.replace(a, '<h2 class="sr">%s</h2>' % t + a, 1)
    body = re.sub(r'<(p|span|small|b|div)( class="[^"]*")?>([A-Z0-9][A-Z0-9 &\'·.,/()=\-]*[A-Z])</\1>', r'<\1\2 lang="en">\3</\1>', body)
    if r["t"] not in ("search", "404", "home"):
        body += '<div class="wrap mfoot"><p>文・図：<a href="/about/">%s</a>　公開 <time datetime="%s">%s</time>　更新 <time datetime="%s">%s</time></p></div>' % (
            html.escape(CFG["handle"]), r["pub"], ja_date(r["pub"]), r["mod"], ja_date(r["mod"]))
    robots = "index,follow,max-image-preview:large" if r["index"] else "noindex,follow"
    head = ['<!doctype html><html lang="ja" data-si="%s"><head><meta charset="utf-8">' % SIURL,
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
            "<title>%s</title>" % html.escape(r["title"], quote=False),
            '<meta name="description" content="%s">' % esc_a(r["desc"]),
            '<meta name="robots" content="%s">' % robots]
    if r["t"] != "404":
        head.append('<link rel="canonical" href="%s">' % url)
    head += ['<meta name="color-scheme" content="light dark">',
             '<meta name="theme-color" content="#F4F4F2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0B0B0C" media="(prefers-color-scheme: dark)">',
             '<meta property="og:site_name" content="%s"><meta property="og:locale" content="ja_JP">' % SITE,
             '<meta property="og:type" content="%s">' % ("website" if r["t"] == "home" else "article"),
             '<meta property="og:title" content="%s">' % esc_a(r["title"].split("｜" + SITE)[0] if r["t"] != "home" else r["title"]),
             '<meta property="og:description" content="%s">' % esc_a(r["desc"]),
             '<meta property="og:url" content="%s">' % url,
             '<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">' % (BASE + r["og"]),
             '<meta property="og:image:alt" content="%s">' % esc_a(r.get("name", SITE) + "（" + SITE + "）"),
             '<meta name="twitter:card" content="summary_large_image">',
             '<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">',
             VERIFY,
             CFBEACON,
             '<link rel="preload" href="%s" as="style" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="%s"></noscript>' % (FCSS, FCSS),
             "<style>%s</style>" % CSS + ("<style>%s</style>" % (SIMCSS if r["t"] == "mtsim" else SIMCSS_ST) if r["t"] in SIMT else ""),
             '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": ld(r)}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
             '<script src="%s" defer></script>' % APPJS + ('<script src="%s" defer></script>' % SIMJS if r["t"] == "mtsim" else ""),
             "</head><body>"]
    doc = "".join(head) + shell_top(r["nav"]) + '<main id="main">' + body + "</main>" + FOOT + "</body></html>"
    return doc


for r in ROUTES:
    fn = OUT + (r["u"] + "index.html" if r["u"].endswith("/") else r["u"])
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    r["doc"] = page(r)
    open(fn, "w", encoding="utf-8").write(r["doc"])

# machine-tool drawings as standalone SVG files (card thumbnails, image search)
os.makedirs(OUT + "/machine-tools/img", exist_ok=True)
_svgcss = mincss(open(B + "/il.css", encoding="utf-8").read()) + "text,.bal,.balt,.leadl,.leadd,.a,.af{display:none}"
for sl, f in MT_ILL.items():
    body_ = re.sub(r'<text[^>]*>.*?</text>', "", f["svg"], flags=re.S)
    body_ = re.sub(r'<(?:line|circle|path|polygon|ellipse)[^>]*class="(?:leadl|leadd|bal|balt|a|af)"[^>]*/>', "", body_)
    doc = ('<svg xmlns="http://www.w3.org/2000/svg" class="ilu" viewBox="%s"><style>%s</style>%s%s</svg>'
           % (f["vb"], _svgcss, re.sub(r'<svg class="ildefs"[^>]*>', "<svg>", DEFS), body_))
    open(OUT + "/machine-tools/img/%s.svg" % sl, "w", encoding="utf-8").write(doc)

# redirects: tiny pages that forward old URLs
for a, b in REDIR.items():
    fn = OUT + (a + "index.html" if a.endswith("/") else a)
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    open(fn, "w", encoding="utf-8").write('<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>移動しました</title><link rel="canonical" href="%s"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=%s"></head><body><p><a href="%s">新しいページへ移動しました</a></p></body></html>' % (BASE + b, b, b))

# ============================================================ 9. sitemap, robots, llms.txt, csv, misc
idx = [r for r in ROUTES if r["index"]]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for r in idx:
    sm.append("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (BASE + r["u"], r["mod"]))
sm.append("</urlset>")
open(OUT + "/sitemap.xml", "w", encoding="utf-8").write("\n".join(sm) + "\n")
BLOCK = ["GPTBot", "Google-Extended", "CCBot", "ClaudeBot", "anthropic-ai", "Applebot-Extended", "Bytespider", "meta-externalagent", "Meta-ExternalAgent", "cohere-training-data-crawler", "Diffbot", "Omgilibot", "Amazonbot", "cohere-ai", "AI2Bot", "FacebookBot", "Timpibot", "PanguBot", "ImagesiftBot"]
robots = "# 検索エンジンとAI検索は歓迎します。AIの学習用クローラーはお断りしています。\n\n" + "".join("User-agent: %s\nDisallow: /\n\n" % b for b in BLOCK) + "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE
open(OUT + "/robots.txt", "w", encoding="utf-8").write(robots)
L = ["# %s（AUTOMOTIVE ATLAS）" % SITE, "", "> 自動車の部品がどんな工程と工作機械・検査機でつくられるかを図解で解説する日本語の図鑑。%d部品・%d工程・%d設備（数はこの図鑑の分類による）と、パワートレイン別の比較、工作機械図鑑（機種・構成部品・自動化・選び方）を収録。運営：%s。文章と図解は CC BY-NC 4.0。" % (len(parts), sum(len(p["ops"]) for p in parts), len(cats), CFG["handle"]), ""]
for head_, ts in (("主要ページ", ("home", "systems", "pt", "map", "methods", "eqi", "about")), ("加工法", ("method",)), ("系統", ("sys",)), ("部品", ("part",)), ("設備の分類", ("eqg",)), ("設備", ("eq",)), ("工作機械図鑑", ("mthome", "mtselect", "mtcomps", "mtautos")), ("工作機械の機種", ("mttype",)), ("工作機械の構成部品", ("mtcomp",)), ("自動化・周辺機器", ("mtauto",)), ("比較ガイド", ("mtguide",)), ("操作トレーニングとトラブル事例", ("mtsimhub", "mttrouble", "mtsim"))):
    L.append("## " + head_)
    for r in idx:
        if r["t"] in ts:
            L.append("- [%s](%s): %s" % (r["title"].split("｜")[0], BASE + r["u"], r["desc"]))
    L.append("")
open(OUT + "/llms.txt", "w", encoding="utf-8").write("\n".join(L))
# powertrain CSV (Dataset)
rows = ["系統,部品," + ",".join(t["n"] for t in data["pt"]["types"])]
for s in systems:
    for p in s["parts"]:
        q = data["pt"]["q"][s["id"] + "." + p["id"]]
        rows.append('"%s","%s",%s' % (s["name"], p["name"], ",".join(str(v) for v in q)))
rows += ["", "指標," + ",".join(t["n"] for t in data["pt"]["types"]), "部品の種類," + ",".join(str(m["parts"]) for m in MET), "工程," + ",".join(str(m["ops"]) for m in MET),
         "機械加工の工程," + ",".join(str(m["mops"]) for m in MET), "機械加工のボリューム（ガソリン車=100）," + ",".join(str(m["vol"]) for m in MET),
         "", "出典：自動車製造工程図鑑（%s） %s/powertrain/  CC BY-NC 4.0。代表的な仕様を仮定した目安。" % (CFG["handle"], BASE)]
open(OUT + "/powertrain/powertrain-comparison.csv", "w", encoding="utf-8-sig").write("\n".join(rows) + "\n")
open(OUT + "/.nojekyll", "w").write("")
if CFG.get("cname"):
    open(OUT + "/CNAME", "w").write(CFG["cname"] + "\n")
for vf in CFG.get("verify_files", []):
    open(OUT + "/" + vf["name"], "w").write(vf["content"])

# ============================================================ 10. checks
problems = []
files = {os.path.relpath(f, OUT) for f in glob.glob(OUT + "/**", recursive=True) if os.path.isfile(f)}


def exists(u):
    u = u.split("#")[0].split("?")[0]
    if u.endswith("/"):
        return (u[1:] + "index.html") in files
    return u[1:] in files


titles = Counter(r["title"] for r in idx)
problems += ["duplicate title: %s" % t for t, n in titles.items() if n > 1]
for r in ROUTES:
    d_ = r["doc"]
    main = d_.split('<main id="main">', 1)[1].split("</main>", 1)[0]
    if len(re.findall(r"<h1[\s>]", main)) != 1:
        problems.append("h1 count %s: %s" % (len(re.findall(r"<h1[\s>]", main)), r["u"]))
    txt = re.sub(r"<[^>]+>", "", main)
    if r["index"] and len(re.sub(r"\s", "", txt)) < 300:
        problems.append("thin page (%d chars): %s" % (len(re.sub(r"\s", "", txt)), r["u"]))
    for h in re.findall(r'href="([^"]+)"', d_):
        if h.startswith("#"):
            if re.match(r"#(top|systems|pt|map|eq|kinds|q|[spoekm]-)", h):
                problems.append("hash route link %s in %s" % (h, r["u"]))
            continue
        if h.startswith("/") and not h.startswith("//"):
            if not exists(h):
                problems.append("broken link %s in %s" % (h, r["u"]))
            elif "#op" in h and ('id="%s"' % h.split("#")[1]) not in BY_U.get(h.split("#")[0], {"doc": ""})["doc"]:
                problems.append("missing anchor %s in %s" % (h, r["u"]))
    ids = re.findall(r'\sid="([^"]+)"', d_)
    dup = [i for i, n in Counter(ids).items() if n > 1]
    if dup:
        problems.append("duplicate ids %s in %s" % (dup[:5], r["u"]))
    if r["t"] != "404" and '<link rel="canonical" href="%s">' % (BASE + r["u"]) not in d_:
        problems.append("canonical: " + r["u"])
cssgz = len(gzip.compress(CSS.encode()))
if cssgz > 15 * 1024:
    problems.append("inline css %d bytes gzipped (> 15KB)" % cssgz)
sizes = sorted(((len(gzip.compress(r["doc"].encode())), r["u"]) for r in ROUTES), reverse=True)
print("pages %d (index %d), redirects %d, fonts %d files %.0fKB, css gz %.1fKB, biggest pages gz: %s" % (
    len(ROUTES), len(idx), len(REDIR), nfiles, fbytes / 1024, cssgz / 1024, ", ".join("%s %.0fKB" % (u, s / 1024) for s, u in sizes[:4])))
if problems:
    print("PROBLEMS (%d):" % len(problems))
    for p_ in problems[:60]:
        print("  " + p_)
    sys.exit(1)
json.dump(URLS, open(urls_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
json.dump(OPN, open(opn_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
print("OK", OUT)
