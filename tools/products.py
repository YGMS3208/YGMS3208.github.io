#!/usr/bin/env python3
"""Add the 'machine elements & tooling' industry: industry/system/part/op/equipment pages, gear guide,
and wire counts, menus, equipment back-links, search, sitemaps. Runs after build.py + practice.py, before glossary.py."""
import glob, hashlib, html, json, os, re, shutil, sys
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from products_data import INDUSTRY, SYSTEMS, PARTS, NEW_EQUIPMENT
from drawings import ALL as DRAW
from gear_guide import GUIDE_HTML, GUIDE_TITLE, GUIDE_DESC, GUIDE_H1, GUIDE_LEAD, GUIDE_TOC, gear_terms_svg

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(SITE)
B = "https://ygms3208.github.io"
TODAY, TODAY_J = "2026-11-06", "2026年11月6日"
e = lambda s: html.escape(s, quote=False)
ea = lambda s: html.escape(s, quote=True)
IND = INDUSTRY
IURL = f"/{IND['slug']}/"
GUIDE_URL = f"{IURL}gear-guide/"
NEWEQ = {q["slug"]: q for q in NEW_EQUIPMENT}
INDEXABLE_EQ = {"jig-grinder", "profile-grinder"}
SYS = {s["slug"]: s for s in SYSTEMS}

# ---------- clean previous output ----------
for d in [IND["slug"]] + [f"systems/{s['slug']}" for s in SYSTEMS] + [f"parts/{p['slug']}" for p in PARTS] + [f"equipment/{q}" for q in NEWEQ]:
    if os.path.isdir(d): shutil.rmtree(d)

# ---------- helpers ----------
def read(p): return open(p, encoding="utf-8").read()
def write(p, s):
    if os.path.dirname(p): os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)

def strip_svg_file(path):
    s = read(path.lstrip("/"))
    s = re.sub(r"<style>.*?</style>", "", s, count=1, flags=re.S)
    s = re.sub(r"<svg><defs>.*?</defs></svg>", "", s, count=1, flags=re.S)
    s = re.sub(r'^<svg xmlns="http://www.w3.org/2000/svg" class="([^"]*)"', r'<svg class="\1"', s)
    return s

SVG_HEAD = None
def standalone(svg_inner):
    """wrap an inline drawing as a standalone file using the house style header."""
    global SVG_HEAD
    if SVG_HEAD is None:
        t = read("parts/img/transmission-gear.svg")
        m = re.match(r'(<svg xmlns="http://www.w3.org/2000/svg" class="ilu " viewBox="0 0 320 200">)(<style>.*?</style><svg><defs>.*?</defs></svg>)', t, re.S)
        SVG_HEAD = m.group(2)
    return svg_inner.replace('<svg class="ilu "', '<svg xmlns="http://www.w3.org/2000/svg" class="ilu "', 1).replace(">", ">" + SVG_HEAD, 1)

EQ_CACHE = {}
def eq_info(slug):
    if slug in EQ_CACHE: return EQ_CACHE[slug]
    if slug in NEWEQ:
        q = NEWEQ[slug]; g = read(f"equipment/group/{q['group']}/index.html")
        gname = re.search(r'<h1 class="d2">([^<]*)</h1>', g).group(1)
        info = dict(name=q["name"], group=gname, makers="・".join(q["makers"]) or "—", svg=DRAW[slug](), desc=q["desc"])
    else:
        s = read(f"equipment/{slug}/index.html")
        name = re.search(r'<h1 class="d2[^"]*"[^>]*>([^<]*)', s).group(1)
        crumbs = re.findall(r'<a href="/equipment/group/[^"]*">([^<]*)</a>', s)
        mk = re.search(r'MAKERS</p>.*?<div class="pills">(.*?)</div>', s, re.S)
        makers = "・".join(re.findall(r'<a class="pill"[^>]*>([^<]*)</a>', mk.group(1))) if mk else ""
        fig = re.search(r'<section class="wrap ehero">.*?<figure class="stage">(<svg.*?</svg>)', s, re.S).group(1)
        info = dict(name=name, group=crumbs[0] if crumbs else "", makers=makers or "—", svg=fig, desc="")
    EQ_CACHE[slug] = info
    return info

def page(template, title, desc, path, crumbs_ld, main, robots=None, og_type="article"):
    t = read(template)
    head = t[:t.index("<style>")]
    head = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", head)
    for prop in ["description"]:
        head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + ea(desc), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + ea(desc), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + ea(title), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + B + path, head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + B + path, head)
    head = re.sub(r'(<meta property="og:image" content=")[^"]*', lambda m: m.group(1) + B + "/og/site.jpg", head)
    head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + ea(title.split("｜")[0] + "（製造工程図鑑）"), head)
    if robots: head = re.sub(r'(<meta name="robots" content=")[^"]*', lambda m: m.group(1) + robots, head)
    style_end = t.index("</style>") + 8
    between = re.sub(r'<script type="application/ld\+json">.*?</script>', "", t[style_end:t.index("<body")], flags=re.S)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": B + u} for i, (n, u) in enumerate(crumbs_ld)]},
        {"@type": "WebPage", "@id": B + path + "#webpage", "url": B + path, "name": title, "inLanguage": "ja", "description": desc, "dateModified": TODAY,
         "isPartOf": {"@id": B + "/#website"}}]}
    between = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>' + between
    body = t[t.index("<body"):t.index("<main")]
    foot = t[t.index("</main>"):]
    return head + t[t.index("<style>"):style_end] + between + body + main + foot

def crumbs_html(items):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<span>{e(n)}</span>' if i == len(items) - 1 else f'<a href="{u}">{e(n)}</a><span class="sep">/</span>')
    return '<nav class="wrap crumbs" aria-label="現在地">' + "".join(out) + "</nav>"

MFOOT = f'<div class="wrap mfoot"><p>文・図：<a href="/about/">Machine Tool Scout</a>　公開 <time datetime="{TODAY}">{TODAY_J}</time>　更新 <time datetime="{TODAY}">{TODAY_J}</time></p></div>'
ARROWS = re.search(r'<div class="arrows">.*?</div>', read("parts/marine-reduction-gear/index.html"), re.S).group(0)

def thumb_for_op(op, part):
    for sl, _ in op[5] + op[6]:
        return eq_info(sl)["svg"]
    return part_svg(part)

PSVG = {}
def part_svg(p):
    key = p["slug"]
    if key not in PSVG:
        PSVG[key] = DRAW[key]() if key in DRAW else strip_svg_file(p["img"])
    return PSVG[key]

# ---------- write standalone images for new drawings ----------
for k in ["precision-jig", "precision-press-die", "roll-forming-rolls"]:
    write(f"parts/img/{k}.svg", standalone(DRAW[k]()))

# ---------- usage index ----------
USE = {}   # eq slug -> list of (part, op, spec, role)
for p in PARTS:
    for op in p["ops"]:
        for sl, spec in op[5]: USE.setdefault(sl, []).append((p, op, spec, "m"))
        for sl, spec in op[6]: USE.setdefault(sl, []).append((p, op, spec, "i"))

n_ops = sum(len(p["ops"]) for p in PARTS)
eq_all = sorted({sl for p in PARTS for op in p["ops"] for sl, _ in op[5] + op[6]})

# ---------- part pages & op pages ----------
for pi, p in enumerate(PARTS):
    sysd = SYS[p["system"]]
    base = f"/parts/{p['slug']}/"
    mach = []; insp = []
    for op in p["ops"]:
        for sl, _ in op[5]:
            if sl not in mach: mach.append(sl)
        for sl, _ in op[6]:
            if sl not in insp: insp.append(sl)
    crumbs = [("トップ", "/"), (IND["name"], IURL), (sysd["name"], f"/systems/{sysd['slug']}/"), (p["name"], base)]
    cards = []
    for op in p["ops"]:
        first = (op[5] or op[6] or [("", "")])[0][0]
        sub = eq_info(first)["name"] if first else "設計"
        cards.append(f'<a class="card op" href="{base}op{op[0]}/" style="background:var(--bg)"><div class="stage thumb">{thumb_for_op(op, p)}</div>'
                     f'<div class="tx"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px"><span class="no">OP{op[0]}</span>'
                     f'<span class="kchip {op[3]}"><i></i>{e(op[2])}</span></div><h3>{e(op[1])}</h3><p>{e(sub)}</p></div></a>')
    def eqlinks(lst):
        return "、".join(f'<a href="/equipment/{sl}/">{e(eq_info(sl)["name"])}</a>' for sl, _ in lst) or '<span class="muted">—</span>'
    oplist = "".join(
        f'<article class="opx" id="op{op[0]}"><span class="no tn">{op[0]}</span><div class="bd"><div class="hrow"><h3>{e(op[1])}</h3><span class="kchip {op[3]}"><i></i>{e(op[2])}</span></div>'
        f'<p>{e(op[4])}</p><dl><div><dt>設備</dt><dd>{eqlinks(op[5])}</dd></div><div><dt>検査</dt><dd>{eqlinks(op[6])}</dd></div>'
        f'<div><dt>管理ポイント</dt><dd>{e("、".join(op[7]))}</dd></div></dl><a class="lnk sm" href="{base}op{op[0]}/">OP{op[0]}の工程図を見る</a></div></article>' for op in p["ops"])
    def lst(sls):
        cnt = {}
        for op in p["ops"]:
            for sl, _ in op[5] + op[6]: cnt[sl] = cnt.get(sl, 0) + 1
        return "".join(f'<a class="li" href="/equipment/{sl}/"><span class="t">{e(eq_info(sl)["name"])}</span><span class="n">{"×" + str(cnt[sl]) if cnt[sl] > 1 else ""}</span></a>' for sl in sls)
    learn = []
    if p["system"] == "gears": learn.append(f'<a class="pill" href="{GUIDE_URL}">歯車の教科書</a>')
    learn += [f'<a class="pill" href="/methods/{m}/">{t}</a>' for m, t in [("gear-cutting", "歯切り・歯車加工とは"), ("heat-treatment", "熱処理とは"), ("grinding", "研削加工とは"), ("machining", "切削加工とは")]
              if (m != "gear-cutting" or p["system"] == "gears")]
    for mt in ["gear-hobbing-machine", "gear-grinding-machine", "cylindrical-grinder", "surface-grinder", "edm", "vertical-machining-center", "cnc-lathe", "internal-grinder", "gear-skiving-machine"]:
        eqs = mt if mt != "edm" else "electrical-discharge-machine"
        if eqs in mach and os.path.exists(f"machine-tools/{mt}/index.html"):
            nm = re.search(r'<h1 class="d1"[^>]*>(.*?)</h1>', read(f"machine-tools/{mt}/index.html")).group(1)
            learn.append(f'<a class="pill" href="/machine-tools/{mt}/">{e(nm)}の構造と仕組み</a>')
    prev_p = PARTS[pi - 1] if pi > 0 else None
    next_p = PARTS[pi + 1] if pi + 1 < len(PARTS) else None
    nav = ('<div class="wrap"><nav class="next" aria-label="前後の部品">'
           + (f'<a href="/parts/{prev_p["slug"]}/"><small lang="en">PREV</small><b>{e(prev_p["name"])}</b></a>' if prev_p else "<span></span>")
           + (f'<a href="/parts/{next_p["slug"]}/"><small lang="en">NEXT</small><b>{e(next_p["name"])}</b></a>' if next_p else "<span></span>")
           + "</nav></div>")
    points = "".join(f"<li>{e(x)}</li>" for x in p["points"])
    main = ('<main id="main"><div class="page">' + crumbs_html(crumbs) +
            f'<section class="phero wrap"><p class="eyebrow"><a href="/systems/{sysd["slug"]}/">{e(sysd["name"])}</a></p><h1 class="kicker">{e(p["kicker"])}</h1>'
            f'<p class="d1" style="font-size:clamp(34px,5.6vw,80px)">{e(p["name"])}</p><p class="mat">{e(p["mat"])}</p></section>'
            f'<div class="wrap pvis"><figure class="stage">{part_svg(p)}<figcaption>{e(p["name"])}のイメージ（模式図）</figcaption></figure></div>'
            f'<div class="wrap"><div class="specs"><div><b>{len(p["ops"])}</b><span>工程</span></div><div><b>{len(mach)}</b><span>加工・生産設備</span></div><div><b>{len(insp)}</b><span>検査・測定</span></div>'
            f'<div><span>業界</span><div class="fit"><i class="on">{e(IND["name"])}</i></div></div></div>'
            f'<p class="desc" style="margin-top:clamp(40px,5vw,64px)">{e(p["desc"])}</p></div>'
            f'<section class="sec tight" style="padding-bottom:0"><div class="wrap"><article class="prose"><h2>つくり方の勘どころ</h2><ul>{points}</ul>'
            + (f'<p><a href="{GUIDE_URL}">歯車の種類・モジュール・精度・加工法を基礎から読む（歯車の教科書）</a></p>' if p["system"] == "gears" else "") +
            '</article></div></section>'
            f'<section class="sec paper"><div class="hd row wrap"><div><p class="eyebrow" lang="en">PROCESS</p><h2 class="d3">{len(p["ops"])}の工程で、できあがる。</h2>'
            f'<p class="sub" style="font-size:16px">各工程の加工原理と主な設備の模式図です。選ぶと工程図と設備を開きます。</p></div>{ARROWS}</div>'
            f'<div class="track big" id="car2">{"".join(cards)}</div></section>'
            f'<section class="sec tight" id="ops"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">OPERATIONS</p><h2 class="d3">{e(p["name"])}の工程と設備</h2></div>'
            f'<div class="oplist">{oplist}</div></div></section>'
            f'<section class="sec tight" style="padding-top:0"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">EQUIPMENT</p><h2 class="d3">この部品で使う設備</h2></div>'
            f'<div class="cols2"><div><p class="h4">加工・生産設備</p><div class="list">{lst(mach)}</div></div><div><p class="h4">検査・測定・試験機</p><div class="list">{lst(insp)}</div></div></div></div></section>'
            f'<section class="sec tight" style="padding-top:0"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">LEARN MORE</p><h2 class="d3">{e(p["name"])}の加工法と工作機械を詳しく</h2></div><div class="pills">{"".join(learn)}</div></div></section>'
            + nav + '<div style="height:40px"></div></div>' + MFOOT + "</main>")
    title = f"{p['kicker']}｜工程と設備を図解｜製造工程図鑑"
    write(f"parts/{p['slug']}/index.html", page("parts/marine-reduction-gear/index.html", title, p["desc"], base, crumbs, main))

    # op pages
    for k, op in enumerate(p["ops"]):
        steps = "".join(f'<li class="{o[3]}"><a href="{base}op{o[0]}/"{" aria-current=\"step\"" if o is op else ""}><span class="bar"></span><span class="o">OP{o[0]}</span><span class="n">{e(o[1])}</span></a></li>' for o in p["ops"])
        def eqt(rows, head):
            if not rows: return ""
            rr = "".join(f'<div class="r"><div class="cat"><a href="/equipment/{sl}/">{e(eq_info(sl)["name"])}</a><small>{e(eq_info(sl)["group"])}</small></div>'
                         f'<div class="spec"><span class="lab">仕様・用途</span>{e(spec)}</div><div class="mk"><span class="lab">メーカー例</span>{e(eq_info(sl)["makers"])}</div></div>' for sl, spec in rows)
            lab, h2 = ("MACHINES", "加工・生産設備") if head == "m" else ("INSPECTION", "検査・測定・試験機")
            pad = "" if head == "m" else ' style="padding-top:0"'
            return (f'<section class="sec tight"{pad}><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">{lab}</p><h2 class="d3">{h2}</h2></div>'
                    f'<div class="eqt"><div class="r th"><span lang="en">{"MACHINE" if head == "m" else "INSPECTION"}</span><span lang="en">SPEC</span><span lang="en">MAKERS</span></div>{rr}</div></div></section>')
        first = (op[5] or op[6] or [("", "")])[0][0]
        fig = eq_info(first)["svg"] if first else part_svg(p)
        figcap = f"{p['name']}のOP{op[0]}「{op[1]}」の原理図（模式図）" if first else f"{p['name']}のイメージ（模式図）"
        prv = p["ops"][k - 1] if k > 0 else None
        nxt = p["ops"][k + 1] if k + 1 < len(p["ops"]) else None
        onav = ('<div class="wrap"><nav class="next" aria-label="前後の工程">'
                + (f'<a href="{base}op{prv[0]}/"><small>OP{prv[0]}</small><b>{e(prv[1])}</b></a>' if prv else f'<a href="{base}"><small>PART</small><b>{e(p["name"])}</b></a>')
                + (f'<a href="{base}op{nxt[0]}/"><small>OP{nxt[0]}</small><b>{e(nxt[1])}</b></a>' if nxt else f'<a href="{base}"><small>PART</small><b>{e(p["name"])}</b></a>')
                + "</nav></div>")
        if not op[5] and not op[6]:
            nomach = '<section class="sec tight"><div class="wrap"><p class="sub" style="font-size:16px">この工程はCADや解析ソフトで行う設計の工程で、工作機械は使わない。</p></div></section>'
        else:
            nomach = ""
        checks = "".join(f"<li>{e(c)}</li>" for c in op[7])
        omain = ('<main id="main"><div class="page">' + crumbs_html(crumbs + [(f"OP{op[0]}", f"{base}op{op[0]}/")]) +
                 f'<div class="wrap"><ol class="steps" aria-label="工程の順序">{steps}</ol><section class="ohead"><span class="big">{op[0]}</span><div class="meta">'
                 f'<p class="eyebrow">OPERATION {k + 1} / {len(p["ops"])}</p><h1 class="d3">{e(op[1])}</h1><div class="row"><span class="kchip {op[3]}"><i></i>{e(op[2])}</span>'
                 f'<a href="{base}">{e(p["name"])}</a></div></div></section></div>'
                 f'<div class="wrap ovis"><figure class="stage">{fig}<figcaption>{e(figcap)}</figcaption></figure></div>'
                 f'<div class="wrap oside"><div><p class="desc">{e(op[4])}</p></div><div class="mini"><div class="stage thumb">{part_svg(p)}</div><p>対象の部品 — {e(p["name"])}</p></div></div>'
                 + nomach + eqt(op[5], "m") + eqt(op[6], "i") +
                 f'<section class="sec tight" style="padding-top:0"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">CHECK POINTS</p><h2 class="d3">管理ポイント</h2></div><ul class="checks">{checks}</ul></div></section>'
                 + onav + '<div style="height:40px"></div></div>' + MFOOT + "</main>")
        otitle = f"{p['name']} OP{op[0]} {op[1]}｜工程図と設備｜製造工程図鑑"
        write(f"parts/{p['slug']}/op{op[0]}/index.html",
              page("parts/marine-reduction-gear/op50/index.html", otitle, op[4], f"{base}op{op[0]}/", crumbs + [(f"OP{op[0]}", f"{base}op{op[0]}/")], omain))

# ---------- system pages ----------
def part_card(p):
    return (f'<a class="card" href="/parts/{p["slug"]}/"><div class="stage thumb"><img src="{p["img"]}" alt="{ea(p["name"])}の模式図（製造工程図鑑）" loading="lazy" decoding="async" width="320" height="200"></div>'
            f'<div class="tx"><p class="eyebrow" lang="en">{len(p["ops"])} OPS</p><h3>{e(p["name"])}</h3><p>{e(p["desc"][:70] + ("…" if len(p["desc"]) > 70 else ""))}</p><span class="ft"><span>{e(p["mat"])}</span></span></div></a>')
for sd in SYSTEMS:
    ps = [p for p in PARTS if p["system"] == sd["slug"]]
    ops = sum(len(p["ops"]) for p in ps)
    mc = sum(1 for p in ps for op in p["ops"] if op[3] == "f1")
    path = f"/systems/{sd['slug']}/"
    crumbs = [("トップ", "/"), (IND["name"], IURL), (sd["name"], path)]
    extra = (f'<section class="sec tight" style="padding-top:0"><div class="wrap"><a class="tile full dk mtpromo" href="{GUIDE_URL}"><div class="tx"><p class="eyebrow" lang="en">GEAR GUIDE</p>'
             '<h3><span class="nw">歯車の教科書。</span></h3><p>種類・モジュール・材料・加工法・精度規格・騒音・損傷、量産と一品物の違いまで。歯車の世界を基礎から徹底的に。</p><span class="lnk">歯車の教科書を読む</span></div>'
             f'<div class="vis">{gear_terms_svg()}</div></a></div></section>') if sd["slug"] == "gears" else ""
    main = ('<main id="main"><div class="page">' + crumbs_html(crumbs) +
            f'<section class="phero wrap"><p class="eyebrow">SYSTEM {sd["no"]}</p><h1 class="kicker">{e(sd["name"])}の部品と製造工程</h1><p class="d1" style="font-size:clamp(40px,6.4vw,88px)">{e(sd["name"])}</p><p class="sub">{e(sd["lead"])}</p></section>'
            f'<div class="wrap pvis"><div class="stage"><img src="{sd["img"]}" alt="{ea(sd["name"])}の模式図" width="640" height="400" style="display:block;width:100%;height:auto"></div></div>'
            f'<div class="wrap"><div class="specs"><div><b>{len(ps)}</b><span>部品</span></div><div><b>{ops}</b><span>工程</span></div><div><b>{mc}</b><span>機械加工の工程</span></div><div><b>{len(ps)}</b><span>詳細工程図のある部品</span></div></div></div>'
            f'<section class="sec"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">PARTS</p><h2 class="d3">{e(sd["name"])}の部品</h2></div><div class="grid-cards">{"".join(part_card(p) for p in ps)}</div></div></section>'
            + extra + '<div style="height:40px"></div></div>' + MFOOT + "</main>")
    write(f"systems/{sd['slug']}/index.html", page("systems/marine-propulsion/index.html", f"{sd['name']}の部品と製造工程｜{sd['sub']}｜製造工程図鑑", sd["lead"], path, crumbs, main))

# ---------- industry page ----------
sys_cards = "".join(
    f'<a class="card" href="/systems/{sd["slug"]}/"><div class="stage thumb"><img src="{sd["img"]}" alt="{ea(sd["name"])}の模式図（製造工程図鑑）" loading="lazy" decoding="async" width="320" height="200"></div>'
    f'<div class="tx"><p class="eyebrow">{sd["no"]}</p><h3>{e(sd["name"])}</h3><p>{e(sd["sub"])}</p><span class="ft"><span lang="en">{sum(1 for p in PARTS if p["system"] == sd["slug"])} PARTS</span>'
    f'<span lang="en">{sum(len(p["ops"]) for p in PARTS if p["system"] == sd["slug"])} OPS</span></span></div></a>' for sd in SYSTEMS)
mlist = "".join(f'<li><a href="/equipment/{sl}/">{e(eq_info(sl)["name"])}</a>: {e(t.split(": ", 1)[1])}</li>' for sl, t in IND["machines"])
icr = [("トップ", "/"), ("業界と部品", "/systems/"), (IND["name"], IURL)]
imain = ('<main id="main"><div class="page">' + crumbs_html(icr) +
         f'<section class="phero wrap"><p class="eyebrow" lang="en">INDUSTRY · {IND["en"]}</p><h1 class="kicker">{e(IND["name"])}の製造工程</h1>'
         f'<p class="d1" style="font-size:clamp(34px,5.6vw,80px)">{e(IND["name"])}</p><p class="sub">{e(IND["lead"])}</p></section>'
         f'<div class="wrap pvis"><div class="stage"><img src="/parts/img/precision-press-die.svg" alt="精密プレス金型の模式図" width="640" height="400" style="display:block;width:100%;height:auto"></div></div>'
         f'<div class="wrap"><div class="specs"><div><b>{len(SYSTEMS)}</b><span>系統</span></div><div><b>{len(PARTS)}</b><span>部品</span></div><div><b>{n_ops}</b><span>工程</span></div><div><b>{len(eq_all)}</b><span>設備・検査機の種類</span></div></div></div>'
         f'<section class="sec"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">SYSTEMS</p><h2 class="d3">{e(IND["name"])}の系統</h2></div><div class="grid-cards">{sys_cards}</div></div></section>'
         f'<section class="sec tight" style="padding-top:0"><div class="wrap"><a class="tile full dk mtpromo" href="{GUIDE_URL}"><div class="tx"><p class="eyebrow" lang="en">GEAR GUIDE</p>'
         '<h3><span class="nw">歯車を、</span><span class="nw">基礎から徹底的に。</span></h3><p>種類・モジュール・材料と熱処理・加工法・精度規格・騒音・損傷、そして量産と一品物の違い。歯車の世界の全体像を1ページで。</p><span class="lnk">歯車の教科書を読む</span></div>'
         f'<div class="vis">{gear_terms_svg()}</div></a></div></section>'
         '<section class="sec tight" style="padding-top:0"><div class="wrap"><article class="prose">'
         '<h2>業界の構造</h2><ul>' + "".join(f"<li>{e(x)}</li>" for x in IND["structure"]) + '</ul>'
         '<h2>つくり方の特徴</h2><ul>' + "".join(f"<li>{e(x)}</li>" for x in IND["features"]) + '</ul>'
         f'<h2>必要とされる工作機械・設備</h2><ul>{mlist}</ul></article></div></section>'
         '<div style="height:40px"></div></div>' + MFOOT + "</main>")
write(f"{IND['slug']}/index.html", page("marine/index.html", f"{IND['name']}の製造工程｜歯車・ボールねじ・治具・金型・成形ロールを図解｜製造工程図鑑", IND["lead"], IURL, icr, imain, og_type="website"))

# ---------- gear guide ----------
gcr = [("トップ", "/"), (IND["name"], IURL), ("歯車の教科書", GUIDE_URL)]
toc = "".join(f'<a href="#{a}"><b lang="en">{i + 1:02d}</b>{e(t)}</a>' for i, (a, t) in enumerate(GUIDE_TOC))
gmain = ('<main id="main"><div class="page">' + crumbs_html(gcr) +
         f'<section class="phero wrap"><p class="eyebrow" lang="en">GEAR GUIDE</p><h1 class="d2">{e(GUIDE_H1)}</h1><p class="sub lead" style="margin:20px auto 0">{e(GUIDE_LEAD)}</p></section>'
         f'<div class="wrap"><nav class="gtoc" aria-label="目次">{toc}</nav></div>'
         f'<section class="sec tight"><div class="wrap"><article class="prose gguide">{GUIDE_HTML}</article></div></section>'
         '<div style="height:40px"></div></div>' + MFOOT + "</main>")
gpage = page("machine-tools/guide/index.html", GUIDE_TITLE, GUIDE_DESC, GUIDE_URL, gcr, gmain)
GCSS = ("/*gg*/.gtoc{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:0 28px;margin-top:clamp(36px,5vw,64px);border-top:1px solid var(--ink)}"
        ".gtoc a{display:flex;gap:12px;align-items:baseline;padding:13px 0;border-bottom:1px solid var(--hair);font-size:15px;color:var(--ink);transition:color .2s}"
        ".gtoc a b{font:400 13px var(--f-en);color:var(--mark)}.gtoc a:hover{color:var(--mark)}"
        ".gguide{max-width:860px}.gguide h2{scroll-margin-top:calc(var(--gn) + 20px);padding-top:28px;border-top:1px solid var(--ink);font-size:clamp(24px,2.6vw,32px)}"
        ".gguide h3{font-size:18px;margin:34px 0 10px}"
        ".gguide .eq{font:400 15px/2 var(--f-en);background:var(--paper);border-radius:6px;padding:16px 20px;margin:0 0 1.3em;color:var(--ink)}"
        ".gguide .eq span{display:block}.gguide .eq small{font-family:var(--f-jp);color:var(--muted);margin-left:10px;font-size:13px}"
        ".gguide .note{font-size:14.5px;padding:16px 20px;border-left:2px solid var(--mark);background:var(--paper);border-radius:0 6px 6px 0;color:var(--ink2)}"
        ".gguide .note b{color:var(--mark);font-weight:500;margin-right:8px}"
        ".gguide figure{margin:8px 0 30px}.gguide figure .stage{border-radius:6px;padding:12px}.gguide figcaption{font-size:12px;color:var(--muted);text-align:center;margin-top:8px}"
        ".gguide .flow{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 1.4em;padding:0;list-style:none}.gguide .flow li{margin:0;padding:6px 12px;border:1px solid var(--hair);border-radius:999px;font-size:13.5px;background:var(--paper)}"
        ".gguide .flow li.h{border-color:var(--mark);color:var(--mark)}"
        "@media (max-width:760px){.gguide .tw{overflow:visible}.gguide table{min-width:0}.gguide thead{display:none}.gguide tr{display:block;padding:14px 0;border-bottom:1px solid var(--hair)}"
        ".gguide td{display:block;border:0;padding:3px 0;white-space:normal}.gguide td:first-child{font-size:16px;padding-bottom:6px}"
        ".gguide td+td::before{content:attr(data-l);display:block;font-size:11px;letter-spacing:.1em;color:var(--muted);margin-top:4px}}")
gpage = gpage.replace("</style>", GCSS + "</style>", 1)
write(f"{IND['slug']}/gear-guide/index.html", gpage)

# ---------- new equipment pages ----------
for q in NEW_EQUIPMENT:
    sl = q["slug"]; info = eq_info(sl); uses = USE.get(sl, [])
    g = read(f"equipment/group/{q['group']}/index.html")
    gname = info["group"]
    crumbs = [("トップ", "/"), ("設備", "/equipment/"), (gname, f"/equipment/group/{q['group']}/"), (q["name"], f"/equipment/{sl}/")]
    parts_n = len({u[0]["slug"] for u in uses}); sys_n = len({u[0]["system"] for u in uses})
    makers = "".join(f'<a class="pill" rel="nofollow" href="/search/?q={ea(m)}">{e(m)}</a>' for m in q["makers"])
    usys = ""
    for sd in SYSTEMS:
        us = [u for u in uses if u[0]["system"] == sd["slug"]]
        if not us: continue
        usys += f'<div class="usys"><h3>{e(sd["name"])}<small>{len(us)}</small></h3>' + "".join(
            f'<a class="use" href="/parts/{u[0]["slug"]}/#op{u[1][0]}"><span class="w"><b>{e(u[0]["name"])}</b><small><span class="tn">OP{u[1][0]}</span>{e(u[1][1])} <span class="role{" i" if u[3] == "i" else ""}">{"検査" if u[3] == "i" else "設備"}</span></small></span>'
            f'<span class="s">{e(u[2])}</span><span class="m">{e(info["makers"])}</span></a>' for u in us) + "</div>"
    em = ('<main id="main"><div class="page">' + crumbs_html(crumbs) +
          f'<section class="wrap ehero"><div><p class="eyebrow">{e(gname)}</p><h1 class="d2" style="margin:14px 0 20px">{e(q["name"])}</h1><p class="desc">{e(q["desc"])}</p>'
          f'<div class="stats" style="margin-top:32px"><div><b>{len(uses)}</b><span>工程で使用</span></div><div><b>{parts_n}</b><span>部品</span></div><div><b>{sys_n}</b><span>系統</span></div></div></div>'
          f'<figure class="stage">{info["svg"]}<figcaption>{e(q["name"])}の原理図（模式図）</figcaption></figure></section>'
          + (f'<section class="sec tight"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">MAKERS</p><h2 class="d3">代表メーカー（例）</h2><p class="sub" style="font-size:14px">この設備分野でよく知られるメーカーの例です。並びは五十音・アルファベット順で、推奨や順位を示すものではありません。</p></div><div class="pills">{makers}</div></div></section>' if makers else "")
          + f'<section class="sec tight" style="padding-top:0"><div class="wrap"><div class="hd" style="margin-bottom:0"><p class="eyebrow" lang="en">WHERE IT\'S USED</p><h2 class="d3">使われている部品と工程</h2></div>{usys}</div></section>'
          '</div>' + MFOOT + "</main>")
    write(f"equipment/{sl}/index.html", page("equipment/thread-grinder/index.html", f"{q['name']}とは｜仕組みと使われる部品・工程｜製造工程図鑑", q["desc"], f"/equipment/{sl}/", crumbs, em, robots=("index,follow,max-image-preview:large" if sl in INDEXABLE_EQ else "noindex,follow")))

# ---------- existing equipment: back-links, counts ----------
for sl, uses in USE.items():
    if sl in NEWEQ: continue
    p = f"equipment/{sl}/index.html"; s = read(p)
    newparts = {u[0]["slug"] for u in uses}; newsys = {u[0]["system"] for u in uses}
    def bump(m):
        return f'<div class="stats" style="margin-top:32px"><div><b>{int(m.group(1)) + len(uses)}</b><span>工程で使用</span></div><div><b>{int(m.group(2)) + len(newparts)}</b><span>部品</span></div><div><b>{int(m.group(3)) + len(newsys)}</b><span>系統</span></div></div>'
    s = re.sub(r'<div class="stats" style="margin-top:32px"><div><b>(\d+)</b><span>工程で使用</span></div><div><b>(\d+)</b><span>部品</span></div><div><b>(\d+)</b><span>系統</span></div></div>', bump, s, count=1)
    makers = eq_info(sl)["makers"]
    usys = ""
    for sd in SYSTEMS:
        us = [u for u in uses if u[0]["system"] == sd["slug"]]
        if not us: continue
        usys += f'<div class="usys"><h3>{e(sd["name"])}<small>{len(us)}</small></h3>' + "".join(
            f'<a class="use" href="/parts/{u[0]["slug"]}/#op{u[1][0]}"><span class="w"><b>{e(u[0]["name"])}</b><small><span class="tn">OP{u[1][0]}</span>{e(u[1][1])} <span class="role{" i" if u[3] == "i" else ""}">{"検査" if u[3] == "i" else "設備"}</span></small></span>'
            f'<span class="s">{e(u[2])}</span><span class="m">{e(makers)}</span></a>' for u in us) + "</div>"
    anchor = '<h2 class="d3">使われている部品と工程</h2></div>'
    if anchor in s:
        i = s.index(anchor) + len(anchor)
        j = s.index("</div></section>", i)
        s = s[:j] + usys + s[j:]
    write(p, s)

# equipment group pages + index
for q in NEW_EQUIPMENT:
    gp = f"equipment/group/{q['group']}/index.html"; g = read(gp)
    uses = USE.get(q["slug"], [])
    names = "、".join(dict.fromkeys(u[0]["name"] for u in uses))
    row = (f'<a class="erow" href="/equipment/{q["slug"]}/"><span class="tp stage thumb">{eq_info(q["slug"])["svg"]}</span><b>{e(q["name"])}</b>'
           f'<span class="c" lang="en">{len(uses)} OPS · {len({u[0]["slug"] for u in uses})} PARTS</span><span class="w">{e(q["desc"])}<small>{e(names)}</small></span></a>')
    i = g.index('<div class="gblock gdesc"'); i = g.index(">", i) + 1
    g = g[:i] + row + g[i:]
    g = re.sub(r"分類される(\d+)種類", lambda m: f"分類される{int(m.group(1)) + 1}種類", g, count=1)
    write(gp, g)
for sl, uses in USE.items():
    if sl in NEWEQ: continue
    s = read(f"equipment/{sl}/index.html")
    grp = re.search(r'<a href="/equipment/group/([^/]+)/">', s).group(1)
    gp = f"equipment/group/{grp}/index.html"; g = read(gp)
    np_ = len({u[0]["slug"] for u in uses})
    def bump_row(m):
        return f'{m.group(1)}{int(m.group(2)) + len(uses)} OPS · {int(m.group(3)) + np_} PARTS'
    g = re.sub(rf'(<a class="erow" href="/equipment/{re.escape(sl)}/">.*?<span class="c" lang="en">)(\d+) OPS · (\d+) PARTS', bump_row, g, count=1, flags=re.S)
    write(gp, g)
ei = read("equipment/index.html")
for q in NEW_EQUIPMENT:
    m = re.search(rf'<a class="gh" href="/equipment/group/{q["group"]}/">.*?<ul[^>]*>', ei, re.S)
    if m: ei = ei[:m.end()] + f'<li><a href="/equipment/{q["slug"]}/">{e(q["name"])}</a></li>' + ei[m.end():]
write("equipment/index.html", ei)

# ---------- counts, home, systems index, menus ----------
old = dict(parts=147, ops=1174, eq=279, sys=20)
new = dict(parts=147 + len(PARTS), ops=1174 + n_ops, eq=279 + len(NEW_EQUIPMENT), sys=20 + len(SYSTEMS))
REPL = [(f"{old['parts']}部品・{old['ops']}工程・{old['eq']}設備", f"{new['parts']}部品・{new['ops']}工程・{new['eq']}設備"),
        (f"「{old['parts']}部品」「{old['ops']}工程」「{old['eq']}設備」", f"「{new['parts']}部品」「{new['ops']}工程」「{new['eq']}設備」"),
        (f"{old['parts']} Parts · {old['ops']} Operations · {old['eq']} Equipment", f"{new['parts']} Parts · {new['ops']} Operations · {new['eq']} Equipment"),
        (f"3つの業界を{old['sys']}の系統に分け、{old['parts']}の部品", f"4つの業界を{new['sys']}の系統に分け、{new['parts']}の部品"),
        ("自動車、舶用エンジン、データセンター向け非常用発電設備の部品が", "自動車、舶用エンジン、データセンター向け非常用発電設備、歯車・ボールねじ・金型などの機械要素が"),
        ("3つの業界を、工程で読む。", "4つの業界を、工程で読む。"),
        (f"{old['parts']}の部品を見る", f"{new['parts']}の部品を見る")]
for p in ["index.html", "about/index.html", "systems/index.html", "methods/index.html", "llms.txt"]:
    s = read(p); o = s
    for a, b in REPL: s = s.replace(a, b)
    if s != o: write(p, s)
h = read("index.html")
for k, lab in [("sys", "系統"), ("parts", "部品"), ("ops", "工程"), ("eq", "設備")]:
    h = h.replace(f'<b class="tn" data-n="{old[k]}">{old[k]}</b><span>{lab}', f'<b class="tn" data-n="{new[k]}">{new[k]}</b><span>{lab}')
h = h.replace('<b>部品のつくり方</b><span class="n">147</span>', f'<b>部品のつくり方</b><span class="n">{new["parts"]}</span>')
h = h.replace('<b>設備・検査機</b><span class="n">279</span>', f'<b>設備・検査機</b><span class="n">{new["eq"]}</span>')
card = (f'<a class="card" data-r style="--i:3" href="{IURL}"><div class="stage thumb"><img src="/parts/img/precision-press-die.svg" alt="精密プレス金型の模式図（製造工程図鑑）" loading="lazy" decoding="async" width="320" height="200"></div>'
        f'<div class="tx"><p class="eyebrow" lang="en">MACHINE ELEMENTS</p><h3>{e(IND["name"])}</h3><p>{e(IND["tagline"])}</p><span class="ft"><span lang="en">{len(SYSTEMS)} SYSTEMS</span><span lang="en">{len(PARTS)} PARTS</span><span lang="en">{n_ops} OPS</span></span></div></a>')
i = h.index('id="industries"'); j = h.index('</div></div></section>', i)
h = h[:j] + card + h[j:]
write("index.html", h)
si = read("systems/index.html")
card2 = card.replace(' data-r style="--i:3"', "")
i = si.index('<div class="grid-cards">'); j = si.index("</div>", si.index("DATA CENTER POWER", i))
j = si.index("</a>", si.index("DATA CENTER POWER", i)) + 4
si = si[:j] + card2 + si[j:]
sec = (f'<div class="hd" style="margin:72px 0 24px"><p class="eyebrow" lang="en">MACHINE ELEMENTS &amp; TOOLING</p><h2 class="d3"><a href="{IURL}">{e(IND["name"])}</a></h2></div>'
       f'<div class="grid-cards">{sys_cards}</div>')
k = si.rindex("</div></div></section>") if False else si.index("</div></section>", si.rindex('<div class="grid-cards">'))
si = si[:k] + sec + si[k:]
write("systems/index.html", si)
MENU_OLD = '<a href="/datacenter-power/">データセンター向け非常用発電</a><a href="/systems/">業界と部品の一覧</a>'
MENU_NEW = f'<a href="/datacenter-power/">データセンター向け非常用発電</a><a href="{IURL}">{IND["name"]}</a><a href="/systems/">業界と部品の一覧</a>'
for p in glob.glob("**/*.html", recursive=True):
    s = read(p)
    if MENU_OLD in s: write(p, s.replace(MENU_OLD, MENU_NEW))

# ---------- search index ----------
si_old = glob.glob("assets/search.*.json")[0]
d = json.load(open(si_old, encoding="utf-8"))
for p in PARTS:
    d["p"].append([p["name"], p["mat"], p["desc"], f"/parts/{p['slug']}/", SYS[p["system"]]["name"]])
    for op in p["ops"]:
        d["o"].append([p["name"], f"OP{op[0]}", op[1], op[4], "、".join(op[7]), f"/parts/{p['slug']}/#op{op[0]}"])
        for sl, spec in op[5] + op[6]:
            info = eq_info(sl)
            d["r"].append([info["name"], spec, "" if info["makers"] == "—" else info["makers"], p["name"], f"OP{op[0]}", op[1], f"/parts/{p['slug']}/#op{op[0]}", "i" if (sl, spec) in op[6] else "m"])
for q in NEW_EQUIPMENT:
    gname = eq_info(q["slug"])["group"]
    d["c"].append([q["name"], q["desc"], f"/equipment/{q['slug']}/", gname])
d["m"].append(["歯車の教科書", "機械要素", GUIDE_URL])
sj = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
si_new = f"assets/search.{hashlib.sha1(sj.encode()).hexdigest()[:10]}.json"
write(si_new, sj)
if si_new != si_old:
    os.remove(si_old)
    for p in glob.glob("**/*.html", recursive=True):
        s = read(p)
        if si_old in s: write(p, s.replace("/" + si_old, "/" + si_new))

# ---------- sitemaps ----------
def add_urls(fn, urls):
    s = read(fn)
    add = "".join(f"<url><loc>{B}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls if f"{B}{u}<" not in s)
    write(fn, s.replace("</urlset>", add + "</urlset>"))
add_urls("sitemap-pages.xml", [IURL, GUIDE_URL])
add_urls("sitemap-parts.xml", [f"/systems/{sd['slug']}/" for sd in SYSTEMS] + [f"/parts/{p['slug']}/" for p in PARTS])
add_urls("sitemap-equipment.xml", [f"/equipment/{q['slug']}/" for q in NEW_EQUIPMENT if q["slug"] in INDEXABLE_EQ])

# ---------- chars for the display font ----------
chars = set(IND["name"] + "".join(s["name"] + s["sub"] for s in SYSTEMS) + "".join(p["name"] + p["kicker"] + "".join(o[1] for o in p["ops"]) for p in PARTS)
            + "".join(q["name"] for q in NEW_EQUIPMENT) + GUIDE_H1 + "".join(t for _, t in GUIDE_TOC) + "".join(re.findall(r"<h[23][^>]*>([^<]*)</h[23]>", GUIDE_HTML))
            + "つくり方の勘どころ工程で、できあがる。の工程と設備この部品で使う設備加工法と工作機械を詳しく歯車の教科書基礎から徹底的に業界の構造特徴必要とされる系統" + "0123456789")
open(f"{S}/extra_chars.txt", "w", encoding="utf-8").write("".join(sorted(chars)))
print(f"parts {len(PARTS)} ops {n_ops} new eq {len(NEW_EQUIPMENT)} | totals {new}")

# ---------- process map ----------
AB = {"切削": "削", "研削": "研", "歯車": "歯", "熱処理": "熱", "表面処理": "表", "素材": "素", "鍛造": "鍛", "組立": "組", "検査": "検"}
mp = read("map/index.html")
msec = (f'<div class="hd" style="margin:64px 0 0"><p class="eyebrow" lang="en">MACHINE ELEMENTS &amp; TOOLING</p><h2 class="d3"><a href="{IURL}">{e(IND["name"])}</a></h2></div>')
for sd in SYSTEMS:
    ps = [p for p in PARTS if p["system"] == sd["slug"]]
    msec += (f'<div class="msys"><h3><a href="/systems/{sd["slug"]}/">{e(sd["name"])}</a><small lang="en">{len(ps)} PARTS · {sum(len(p["ops"]) for p in ps)} OPS</small></h3>'
             + "".join(f'<div class="mrow"><a href="/parts/{p["slug"]}/">{e(p["name"])}</a><div class="cells">' + "".join(
                 f'<a class="{op[3]}" href="/parts/{p["slug"]}/#op{op[0]}" title="OP{op[0]} {ea(op[1])}（{op[2]}）" aria-label="OP{op[0]} {ea(op[1])}">{AB.get(op[2], op[2][0])}</a>' for op in p["ops"]) + "</div></div>" for p in ps)
             + "</div>")
k = mp.rindex('</div></section></div><div class="wrap mfoot">')
mp = mp[:k] + msec + mp[k:]
mp = mp.replace(f"3業界・{old['parts']}部品・{old['ops']}工程", f"4業界・{new['parts']}部品・{new['ops']}工程").replace(f"{old['parts']}部品・{old['ops']}工程", f"{new['parts']}部品・{new['ops']}工程")
write("map/index.html", mp)
for p in ["systems/index.html", "llms.txt"]:
    s = read(p)
    s = s.replace(f"{old['parts']}部品・{old['ops']}工程", f"{new['parts']}部品・{new['ops']}工程").replace(f"{old['parts']}部品の製造工程", f"{new['parts']}部品の製造工程")
    write(p, s)

# ---------- llms.txt ----------
L = read("llms.txt").split("\n")
def insert_after_section(lines, head, new_lines):
    i = lines.index(head) + 1
    while i < len(lines) and not lines[i].startswith("## "): i += 1
    while lines[i - 1] == "": i -= 1
    return lines[:i] + new_lines + lines[i:]
L = insert_after_section(L, "## 業界", [f"- [{IND['name']}の製造工程]({B}{IURL}): {IND['lead']}", f"- [歯車の教科書]({B}{GUIDE_URL}): {GUIDE_DESC}"])
L = insert_after_section(L, "## 系統", [f"- [{sd['name']}]({B}/systems/{sd['slug']}/): {sd['lead']}" for sd in SYSTEMS])
L = insert_after_section(L, "## 部品", [f"- [{p['name']}]({B}/parts/{p['slug']}/): {p['desc']}" for p in PARTS])
L = insert_after_section(L, "## 設備", [f"- [{q['name']}]({B}/equipment/{q['slug']}/): {q['desc']}" for q in NEW_EQUIPMENT])
write("llms.txt", "\n".join(L))

# ---------- home: guides ----------
h = read("index.html")
h = h.replace('<a class="pill" href="/machine-tools/guide/">工作機械の選び方</a></div>',
              f'<a class="pill" href="/machine-tools/guide/">工作機械の選び方</a><a class="pill" href="{GUIDE_URL}">歯車の教科書（種類・モジュール・精度・加工法）</a><a class="pill" href="/machine-tools/glossary/">工作機械 用語辞典（149語）</a></div>', 1)
write("index.html", h)
