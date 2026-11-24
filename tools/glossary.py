#!/usr/bin/env python3
"""Build /machine-tools/glossary/, auto-link terms on machine-tool pages, wire search/sitemap/menus.
Run after build.py and practice.py (works on the freshly rebuilt tree)."""
import glob, hashlib, html, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, S)
from glossary_data import TERMS, CATS, BLOCKERS

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(SITE)
BASEURL = "https://ygms3208.github.io"
GURL = "/machine-tools/glossary/"
e = lambda s: html.escape(s, quote=False)
ea = lambda s: html.escape(s, quote=True)

T = {t[0]: dict(id=t[0], term=t[1], yomi=t[2], en=t[3], cat=t[4], alias=t[5], short=t[6], detail=t[7], rel=t[8], page=t[9]) for t in TERMS}
assert len(T) == len(TERMS), "duplicate id"
for t in T.values():
    for r in t["rel"]:
        assert r in T, (t["id"], r)
    assert t["cat"] in {c[0] for c in CATS}, t["id"]
    if t["page"]:
        assert os.path.exists(t["page"].lstrip("/") + "index.html"), t["page"]

# ---------- glossary json (for hover previews) ----------
gj = json.dumps({k: [v["term"], v["yomi"], v["short"]] for k, v in T.items()}, ensure_ascii=False, separators=(",", ":"))
gjp = f"assets/glossary.{hashlib.sha1(gj.encode()).hexdigest()[:10]}.json"
for old in glob.glob("assets/glossary.*.json"):
    os.remove(old)
open(gjp, "w", encoding="utf-8").write(gj)

# ---------- glossary page ----------
tpl = open("machine-tools/guide/index.html", encoding="utf-8").read()
title = "工作機械 用語辞典｜主軸・ドレッシング・工具補正などをやさしく解説｜工作機械図鑑"
desc = f"工作機械の用語{len(T)}語を、初心者向けの「ひとこと」と実務者向けの「詳しく」の2段で解説。構造、切削、NCと段取り、研削、歯車、放電・レーザ、精度と測定、自動化、安全の9分野。"
head = tpl[:tpl.index("<style>")]
head = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", head)
head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + ea(desc), head)
head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + ea(desc), head)
head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + ea(title), head)
head = head.replace(f"{BASEURL}/machine-tools/guide/", f"{BASEURL}{GURL}")
head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + "工作機械 用語辞典（製造工程図鑑）", head)
style_end = tpl.index("</style>") + len("</style>")
style = tpl[tpl.index("<style>"):style_end]
ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "トップ", "item": BASEURL + "/"},
        {"@type": "ListItem", "position": 2, "name": "工作機械図鑑", "item": BASEURL + "/machine-tools/"},
        {"@type": "ListItem", "position": 3, "name": "用語辞典", "item": BASEURL + GURL}]},
    {"@type": "DefinedTermSet", "@id": BASEURL + GURL + "#set", "name": "工作機械 用語辞典", "url": BASEURL + GURL, "inLanguage": "ja",
     "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f"{BASEURL}{GURL}{t['id']}/#term", "name": t["term"], "alternateName": [t["en"]] + t["alias"],
                         "description": t["short"], "url": f"{BASEURL}{GURL}{t['id']}/", "inDefinedTermSet": BASEURL + GURL + "#set"} for t in T.values()]}]}
between = tpl[style_end:tpl.index("<body")]
between = re.sub(r'<script type="application/ld\+json">.*?</script>', "", between, flags=re.S)
between = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>' + between
body_open = tpl[tpl.index("<body"):tpl.index("<main")]
foot = tpl[tpl.index("</main>"):]

def entry(t):
    rel = "".join(f'<a href="#t-{r}">{e(T[r]["term"])}</a>' for r in t["rel"])
    more = f'<a class="lnk" href="{GURL}{t["id"]}/">{e(t["term"])}とは（詳しく）</a>' + (f'<a class="lnk" href="{t["page"]}">関連するページを読む</a>' if t["page"] else "")
    al = f'<span class="al">別名：{e("・".join(t["alias"]))}</span>' if t["alias"] else ""
    return (f'<article class="gt" id="t-{t["id"]}" data-s="{ea((t["term"] + t["yomi"] + t["en"] + "".join(t["alias"])).lower())}">'
            f'<header><h3><a href="{GURL}{t["id"]}/">{e(t["term"])}</a></h3><p class="yo"><span>{e(t["yomi"])}</span><span lang="en">{e(t["en"])}</span></p>{al}</header>'
            f'<div class="bd"><p class="gs">{e(t["short"])}</p><p class="gd"><span class="lb">詳しく</span>{e(t["detail"])}</p>'
            f'<footer>{"<span class=rl><b>関連</b>" + rel + "</span>" if rel else ""}{more}</footer></div></article>')

secs, chips = [], []
for cid, cname, cen in CATS:
    items = [t for t in T.values() if t["cat"] == cid]
    chips.append(f'<a href="#c-{cid}">{e(cname)}<small>{len(items)}</small></a>')
    secs.append(f'<section class="gcat" id="c-{cid}"><div class="gch"><p class="eyebrow" lang="en">{cen}</p><h2 class="d3">{e(cname)}</h2></div>'
                + "".join(entry(t) for t in items) + "</section>")
main = ('<main id="main"><div class="page"><nav class="wrap crumbs" aria-label="現在地"><a href="/">トップ</a><span class="sep">/</span>'
        '<a href="/machine-tools/">工作機械図鑑</a><span class="sep">/</span><span>用語辞典</span></nav>'
        '<section class="phero wrap"><p class="eyebrow" lang="en">GLOSSARY</p><h1 class="d2">工作機械 用語辞典</h1>'
        f'<p class="sub lead" style="margin:20px auto 0">工作機械の現場で使う{len(T)}の言葉を、まず「ひとこと」でつかみ、必要なら「詳しく」で仕組みと実務の勘どころまで読めるようにまとめた。本文中の点線の付いた言葉からも、ここへ移動できる。</p></section>'
        '<div class="gtool"><div class="wrap"><label class="sr" for="gq">用語を絞り込む</label>'
        '<input id="gq" type="search" placeholder="用語・よみ・英語で絞り込む（例：ドレス、spindle）" autocomplete="off" enterkeyhint="search">'
        f'<nav class="gchips" aria-label="分野">{"".join(chips)}</nav></div></div>'
        f'<div class="wrap gbody">{"".join(secs)}<p class="gnone" id="gnone" hidden>当てはまる用語がありません。短い言葉で試してください。</p></div>'
        '</div></main>')
os.makedirs("machine-tools/glossary", exist_ok=True)
page = head + style + between + body_open + main + foot
page = page.replace('<a href="/machine-tools/guide/">選び方</a>', '<a href="/machine-tools/guide/">選び方</a>')  # noop guard
open("machine-tools/glossary/index.html", "w", encoding="utf-8").write(page)

# ---------- auto-link terms on machine-tool pages ----------
keys = {}
for t in T.values():
    for k in ([t["term"]] if t["id"] not in ("feed", "dry-run", "slug") else []) + t["alias"]:
        keys[k] = t["id"]
blk = [b for b in BLOCKERS + ["ミーリングチャック", "油圧チャック", "ダイヤフラムチャック", "焼きばめ", "主軸受", "電池モジュール", "パワーモジュール", "IGBTモジュール",
       "触媒モジュール", "モジュール化", "タレットパンチ", "ボンドコート", "ワイヤボンド", "ウェルドボンド", "油砥石", "砂中子", "チップドレス", "チップドレッサ",
       "突出し量", "専用CAM", "陸上試運転", "シートモジュール", "カメラモジュール"] if b not in keys]
alts = sorted(set(keys) | set(blk), key=len, reverse=True)
RX = re.compile("|".join(re.escape(a) for a in alts))
SKIP_TAGS = {"a", "h1", "h2", "h3", "h4", "h5", "h6", "script", "style", "button", "label", "select", "option", "textarea", "nav", "code", "title", "legend", "small", "figcaption"}
SKIP_CLS = re.compile(r'class="[^"]*\b(eyebrow|pill|lnk|crumbs|h4|n|no|tn|eq|ft|best)\b')
VOID = {"br", "img", "input", "meta", "link", "hr", "source", "wbr", "col", "area", "base", "embed", "param", "track"}
TOK = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)

def link_page(s, here):
    a, b = s.find("<main"), s.find("</main>")
    if a < 0: return s, 0
    parts = TOK.split(s[a:b]); stack = []; svg = 0; done = set(); n = 0
    own = {t["id"] for t in T.values() if t["page"] and here.startswith(t["page"].lstrip("/"))}
    for i, p in enumerate(parts):
        if not p: continue
        if p.startswith("<"):
            if p.startswith("<!--"): continue
            m = re.match(r"</?\s*([a-zA-Z0-9]+)", p)
            if not m: continue
            tag = m.group(1).lower()
            if tag == "svg":
                if p.startswith("</"): svg -= 1
                elif not p.endswith("/>"): svg += 1
                continue
            if svg: continue
            if p.startswith("</"):
                while stack:
                    t0, _ = stack.pop()
                    if t0 == tag: break
            elif tag not in VOID and not p.endswith("/>"):
                stack.append((tag, tag in SKIP_TAGS or bool(SKIP_CLS.search(p))))
            continue
        if svg or any(sk for _, sk in stack) or not stack: continue
        def rep(m):
            nonlocal n
            w = m.group(0); tid = keys.get(w)
            if not tid or tid in done or tid in own: return w
            if tid in NEED and NEED[tid] not in s: return w
            done.add(tid); n += 1; OCC.setdefault(tid, []).append(here)
            return f'<a class="gl" href="{GURL}{tid}/" data-t="{tid}">{w}</a>'
        parts[i] = RX.sub(rep, p)
    return s[:a] + "".join(parts) + s[b:], n

stats = {}
OCC = {}
NEED = {"module": "歯車", "pressure-angle": "歯車", "helix-angle": "歯車", "contact-ratio": "歯車"}
from products_data import PARTS as _NP, SYSTEMS as _NS, NEW_EQUIPMENT as _NE, INDUSTRY as _NI
_scope = glob.glob("machine-tools/**/index.html", recursive=True) + glob.glob(_NI["slug"] + "/**/index.html", recursive=True)
for _p in _NP: _scope += glob.glob(f"parts/{_p['slug']}/**/index.html", recursive=True)
_scope += [f"systems/{_s['slug']}/index.html" for _s in _NS] + [f"equipment/{_q['slug']}/index.html" for _q in _NE]
for _d in ["parts", "equipment", "methods", "systems", "powertrain", "automotive", "marine", "datacenter-power"]:
    _scope += glob.glob(f"{_d}/**/index.html", recursive=True)
_scope = [x for x in _scope if "移動しました" not in open(x, encoding="utf-8").read()[:3000]]
for p in sorted(set(_scope)):
    if p.startswith("machine-tools/glossary/"): continue
    s = open(p, encoding="utf-8").read()
    s2, n = link_page(s, p)
    if n:
        s2 = s2.replace("<html ", f'<html data-gj="/{gjp}" ', 1)
    stats[p] = n
    if s2 != s: open(p, "w", encoding="utf-8").write(s2)
gpage = open("machine-tools/glossary/index.html", encoding="utf-8").read().replace("<html ", f'<html data-gj="/{gjp}" ', 1)
open("machine-tools/glossary/index.html", "w", encoding="utf-8").write(gpage)

TCSS = ("/*tt*/.tyo{display:flex;justify-content:center;gap:14px;margin-top:10px;font-size:13px;color:var(--muted);letter-spacing:.08em}.tyo [lang=en]{font-family:var(--f-en)}"
        ".tterm{max-width:760px;margin:0 auto}.tterm .tal{font-size:14px;color:var(--muted)}"
        ".prose .trel,.prose .tocc{list-style:none;padding:0;border-top:1px solid var(--hair)}.prose .trel li,.prose .tocc li{margin:0}.trel li,.tocc li{margin:0;border-bottom:1px solid var(--hair)}"
        ".trel a{display:grid;grid-template-columns:9em minmax(0,1fr);gap:16px;padding:14px 0;text-decoration:none;color:inherit}"
        ".trel b{color:var(--accent);font-weight:500}.trel span{font-size:14px;color:var(--ink2);line-height:1.8}"
        ".tocc a{display:block;padding:11px 0;font-size:15px;text-decoration:none}.tocc a:hover,.trel a:hover b{color:var(--mark)}"
        ".tback{margin-top:40px}@media (max-width:640px){.trel a{grid-template-columns:1fr;gap:2px}}")

# ---------- one page per term ----------
CATN = {c[0]: c[1] for c in CATS}
GIDX = open("machine-tools/glossary/index.html", encoding="utf-8").read()
def ptitle(path):
    m = re.search(r"<title>(.*?)</title>", open(path, encoding="utf-8").read(3000))
    return html.unescape(m.group(1).split("｜")[0]) if m else path
def occ_rank(p):  # part & machine pages first, op pages last
    return (3 if re.search(r"/op\d+/", p) else 0 if p.startswith("parts/") else 1 if p.startswith(("machine-tools/", "machine-elements/", "methods/")) else 2, p)
for t in T.values():
    url = f"{GURL}{t['id']}/"
    rel = "".join(f'<li><a href="{GURL}{r}/"><b>{e(T[r]["term"])}</b><span>{e(T[r]["short"])}</span></a></li>' for r in t["rel"])
    occ = sorted(set(OCC.get(t["id"], [])), key=occ_rank)[:12]
    occh = "".join(f'<li><a href="/{q[:-len("index.html")]}">{e(ptitle(q))}</a></li>' for q in occ)
    al = f'<p class="tal">別名・言い換え：{e("・".join(t["alias"]))}</p>' if t["alias"] else ""
    more = f'<p><a class="lnk" href="{t["page"]}">{e(t["term"])}をもっと詳しく（図解のページへ）</a></p>' if t["page"] else ""
    det = "".join(f"<p>{e(x)}</p>" for x in re.split(r"(?<=。)(?=.{60,})", t["detail"]) if x)
    main = ('<main id="main"><div class="page"><nav class="wrap crumbs" aria-label="現在地"><a href="/">トップ</a><span class="sep">/</span>'
            f'<a href="/machine-tools/">工作機械図鑑</a><span class="sep">/</span><a href="{GURL}">用語辞典</a><span class="sep">/</span><span>{e(t["term"])}</span></nav>'
            f'<section class="phero wrap"><p class="eyebrow">{e(CATN[t["cat"]])}</p><h1 class="d2">{e(t["term"])}とは</h1>'
            f'<p class="tyo"><span>{e(t["yomi"])}</span><span lang="en">{e(t["en"])}</span></p>'
            f'<p class="sub lead" style="margin:20px auto 0">{e(t["short"])}</p></section>'
            f'<section class="sec tight"><div class="wrap"><article class="prose tterm"><h2>{e(t["term"])}の仕組みと実務のポイント</h2>{det}{al}{more}'
            + (f'<h2>関連する用語</h2><ul class="trel">{rel}</ul>' if rel else "")
            + (f'<h2>{e(t["term"])}が出てくるページ</h2><ul class="tocc">{occh}</ul>' if occh else "")
            + f'<p class="tback"><a class="lnk" href="{GURL}#t-{t["id"]}">用語辞典の一覧で見る</a></p></article></div></section>'
            '<div style="height:40px"></div></div></main>')
    desc = (t["short"] + t["detail"])[:118] + "…"
    title = f"{t['term']}とは｜意味と仕組みをやさしく解説｜工作機械 用語辞典"
    pg = GIDX
    pg = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", pg, count=1)
    for pat in [r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*']:
        pg = re.sub(pat, lambda m: m.group(1) + ea(desc), pg, count=1)
    pg = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + ea(title), pg, count=1)
    pg = pg.replace(f'{BASEURL}{GURL}"', f'{BASEURL}{url}"')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "トップ", "item": BASEURL + "/"},
            {"@type": "ListItem", "position": 2, "name": "工作機械図鑑", "item": BASEURL + "/machine-tools/"},
            {"@type": "ListItem", "position": 3, "name": "用語辞典", "item": BASEURL + GURL},
            {"@type": "ListItem", "position": 4, "name": t["term"], "item": BASEURL + url}]},
        {"@type": "DefinedTerm", "@id": BASEURL + url + "#term", "name": t["term"], "alternateName": [t["en"]] + t["alias"], "description": t["short"] + t["detail"],
         "url": BASEURL + url, "inDefinedTermSet": {"@type": "DefinedTermSet", "@id": BASEURL + GURL + "#set", "name": "工作機械 用語辞典"}}]}
    pg = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}</script>', pg, count=1, flags=re.S)
    pg = pg[:pg.index("<main")] + main + pg[pg.index("</main>") + 7:]
    pg = pg.replace("</style>", TCSS + "</style>", 1)
    os.makedirs(f"machine-tools/glossary/{t['id']}", exist_ok=True)
    open(f"machine-tools/glossary/{t['id']}/index.html", "w", encoding="utf-8").write(pg)

# ---------- menus, footer, machine-tools hub ----------
for p in glob.glob("**/*.html", recursive=True):
    s = open(p, encoding="utf-8").read()
    s2 = s.replace('<a href="/machine-tools/troubles/">トラブル事例集</a></div>',
                   '<a href="/machine-tools/troubles/">トラブル事例集</a><a href="/machine-tools/glossary/">用語辞典</a></div>')
    if s2 != s: open(p, "w", encoding="utf-8").write(s2)
hub = open("machine-tools/index.html", encoding="utf-8").read()
hub = hub.replace('<a class="lnk" href="/machine-tools/guide/">選び方から探す</a></p>',
                  '<a class="lnk" href="/machine-tools/guide/">選び方から探す</a><a class="lnk" href="/machine-tools/glossary/">用語辞典</a></p>', 1)
open("machine-tools/index.html", "w", encoding="utf-8").write(hub)

# ---------- search index ----------
si_old = glob.glob("assets/search.*.json")[0]
si = json.load(open(si_old, encoding="utf-8"))
si["m"] = [m for m in si["m"] if m[1] != "用語"] + [["用語辞典", "工作機械図鑑", GURL]] + [[t["term"], "用語", f"{GURL}{t['id']}/"] for t in T.values()]
sj = json.dumps(si, ensure_ascii=False, separators=(",", ":"))
si_new = f"assets/search.{hashlib.sha1(sj.encode()).hexdigest()[:10]}.json"
if si_new != si_old:
    open(si_new, "w", encoding="utf-8").write(sj); os.remove(si_old)
    for p in glob.glob("**/*.html", recursive=True):
        s = open(p, encoding="utf-8").read()
        if si_old in s: open(p, "w", encoding="utf-8").write(s.replace("/" + si_old, "/" + si_new))

# ---------- sitemap ----------
sm = open("sitemap-machine-tools.xml", encoding="utf-8").read()
add = "".join(f"<url><loc>{BASEURL}{u}</loc><lastmod>2026-11-08</lastmod></url>\n" for u in [GURL] + [f"{GURL}{t['id']}/" for t in T.values()] if f"{BASEURL}{u}<" not in sm)
sm = sm.replace("</urlset>", add + "</urlset>")
open("sitemap-machine-tools.xml", "w", encoding="utf-8").write(sm)

tot = sum(stats.values())
print(f"terms {len(T)}, linked pages {sum(1 for v in stats.values() if v)}/{len(stats)}, links {tot}")
for k, v in sorted(stats.items(), key=lambda x: -x[1])[:5]: print(" ", k, v)
