#!/usr/bin/env python3
"""The practical handbook (added after the 2026-11 expert review): 11 guide pages with calculators,
the learning path, and the links to them from the hub, the guide index, the machine pages, search, sitemap, feed and llms.txt.
Runs after guides.py and before glossary.py (so the glossary links the new pages too)."""
import glob, hashlib, html, json, os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from gxstyle import CSS
from handbook_lib import G
import handbook_a, handbook_b, handbook_c

# helpers from products.py (same loader as guides.py)
_src = open(os.path.join(S, "products.py"), encoding="utf-8").read()
_helpers = _src[_src.index("# ---------- helpers ----------"):_src.index("# ---------- write standalone images")]
PUB, PUB_J = "2026-11-28", "2026年11月28日"
_g = {"__name__": "helpers", "html": html, "json": json, "re": re, "os": os, "glob": glob, "B": "https://ygms3208.github.io", "TODAY": PUB, "TODAY_J": PUB_J,
      "e": lambda s: html.escape(s, quote=False), "ea": lambda s: html.escape(s, quote=True), "NEWEQ": {}, "DRAW": {}}
os.chdir(os.path.dirname(S))
exec(_helpers, _g)
e, write, read, page, crumbs_html = _g["e"], _g["write"], _g["read"], _g["page"], _g["crumbs_html"]

PAGES = {}
for m in (handbook_a, handbook_b, handbook_c): PAGES.update(m.PAGES)
# display order
ORDER = ["learning-path", "cutting-conditions", "cutting-tools", "nc-programming", "accuracy-testing", "grinding-conditions",
         "rigidity-thermal", "line-planning", "maintenance-basics", "safety", "history-industry"]
assert set(ORDER) == set(PAGES), set(ORDER) ^ set(PAGES)

# ---- the learning path: each step names pages to read; handbook pages show "previous / next" along it ----
STEPS = [
 ("工作機械とは何か", "機械をつくる機械（マザーマシン）としての役割、機種の分け方、歴史。", [("/machine-tools/", "工作機械図鑑"), (G + "history-industry/", "工作機械の歴史と業界")]),
 ("削る仕組みと条件", "切削速度・送り・切込みの意味と、回転数の計算。", [("/methods/machining/", "切削加工とは"), (G + "cutting-conditions/", "切削条件の決め方と計算")]),
 ("旋盤", "工作物を回して削る機械。構造、段取り、周速一定制御。", [("/machine-tools/cnc-lathe/", "NC旋盤"), (G + "lathe-vs-machining-center/", "旋盤とマシニングセンタの違い")]),
 ("マシニングセンタ", "工具を回して削る機械。ATC、ワーク座標、3軸と5軸。", [("/machine-tools/vertical-machining-center/", "立形マシニングセンタ"), (G + "3-axis-vs-5-axis/", "3軸と5軸の違い")]),
 ("切削工具", "工具の種類と材種、傷み方の見分け方。", [(G + "cutting-tools/", "切削工具の種類・材種と傷み方")]),
 ("NCプログラム", "Gコード、座標系、工具補正、プログラム例。", [(G + "nc-programming/", "NCプログラムの基本"), ("/machine-tools/training/", "操作トレーニング")]),
 ("精度と測定", "精度の種類、検査の方法、数字の読み方。", [(G + "machine-accuracy/", "工作機械の精度の見方"), (G + "accuracy-testing/", "精度検査の読み方")]),
 ("研削", "砥石で仕上げる機械と、研削条件・ドレス。", [("/methods/grinding/", "研削加工とは"), ("/machine-tools/cylindrical-grinder/", "円筒研削盤"), (G + "grinding-conditions/", "研削条件と砥石の選び方")]),
 ("自動化と設備計画", "ローダ・ロボット、タクトと台数、投資回収。", [("/machine-tools/automation/", "自動化・周辺機器"), (G + "line-planning/", "設備計画の基本"), (G + "spindle-torque-chart/", "主軸のトルク線図の見方")]),
 ("保全と安全", "止めないための点検と、事故を起こさないための決まり。", [(G + "maintenance-basics/", "工作機械の保全"), (G + "safety/", "工作機械の安全"), ("/machine-tools/troubles/", "トラブル事例集")]),
]
ADV = [(G + "rigidity-thermal/", "剛性・びびり・熱変位を数字で見る"), (G + "maintenance-standards/", "設備規格と完成立会いの指摘事項"), ("/machine-tools/physical-ai/", "フィジカルAIと工作機械"), ("/machine-tools/glossary/", "用語辞典")]

def learning_body():
    li = []
    for i, (t, d, links) in enumerate(STEPS, 1):
        ls = "".join(f'<a href="{u}">{e(n)}</a>' for u, n in links)
        li.append(f'<li id="step-{i}"><h3>{e(t)}</h3><p>{e(d)}</p><p class="lp-links">{ls}</p></li>')
    adv = "".join(f'<a href="{u}">{e(n)}</a>' for u, n in ADV)
    return (f'<p>この図鑑には、機種・構成部品・加工法・ガイドを合わせて数百のページがある。はじめての人は、次の順に読むと、つながりが見えやすい。各ステップは、1〜2ページを読めば先に進める分量にしてある。</p>'
            f'<ol class="layers lp">{"".join(li)}</ol>'
            f'<h2 id="lp-next">その先へ</h2><p>現場の判断に踏み込む人には、次のページもある。</p><p class="lp-links">{adv}</p>'
            f'<p>わからない言葉は、本文の点線の下線をクリックすると<a href="/machine-tools/glossary/">用語辞典</a>で引ける。</p>')
PAGES["learning-path"]["body"] = learning_body()

def neighbours(url):
    """previous / next step for a page on the learning path"""
    for i, (t, d, links) in enumerate(STEPS):
        if any(u == url for u, _ in links):
            prev = STEPS[i - 1] if i > 0 else None
            nxt = STEPS[i + 1] if i + 1 < len(STEPS) else None
            return i + 1, prev, nxt
    return None

LP_CSS = (".lp>li h3{margin:0 0 4px}.lp-links{display:flex;flex-wrap:wrap;gap:8px 10px;margin-top:10px}"
          ".lp-links a{display:inline-flex;align-items:center;height:34px;padding:0 14px;border-radius:999px;box-shadow:0 0 0 1px var(--hair);font-size:13.5px;color:var(--ink);transition:box-shadow .2s,color .2s}"
          ".lp-links a:hover{box-shadow:0 0 0 1px var(--accent);color:var(--accent)}"
          ".lpnav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:clamp(40px,5vw,64px)}"
          ".lpnav a{display:block;padding:16px 20px;border-radius:8px;box-shadow:0 0 0 1px var(--hair);transition:box-shadow .2s}"
          ".lpnav a:hover{box-shadow:0 0 0 1px var(--ink2)}.lpnav small{display:block;font-size:11.5px;letter-spacing:.12em;color:var(--muted)}"
          ".lpnav b{font-size:15px;font-weight:500}.lpnav .nx{text-align:right;grid-column:2}"
          ".gx table.prog code{font:400 13.5px var(--f-en);white-space:nowrap}.gx code{font-family:var(--f-en)}"
          "@media (max-width:640px){.lpnav{grid-template-columns:1fr}.lpnav .nx{grid-column:1}}")

ALL_GUIDES = None
def more_list(slug):
    gi = read("machine-tools/guide/index.html")
    items = re.findall(r'<a class="li" href="(/machine-tools/[^"]+)"><span class="t">([^<]+)</span><span class="n" lang="en">([^<]*)</span></a>', gi)
    own = [(f"{G}{s}/", PAGES[s]["h1"], PAGES[s]["eyebrow"]) for s in ORDER]
    seen, out = set(), []
    for u, t, ey in own + items:
        if u in seen or u == f"{G}{slug}/": continue
        seen.add(u); out.append((u, t, ey))
    return out

def build(slug):
    p = PAGES[slug]; path = f"{G}{slug}/"
    cr = [("トップ", "/"), ("工作機械図鑑", "/machine-tools/"), ("選び方・ガイド", G), (p["h1"], path)]
    nb = neighbours(path)
    nav = ""
    if nb:
        i, prev, nxt = nb
        nav = '<nav class="lpnav" aria-label="学びの順路">'
        if prev: nav += f'<a href="{prev[2][0][0]}"><small>学びの順路 {i - 1}：前へ</small><b>{e(prev[0])}</b></a>'
        if nxt: nav += f'<a class="nx" href="{nxt[2][0][0]}"><small>学びの順路 {i + 1}：次へ</small><b>{e(nxt[0])}</b></a>'
        nav += "</nav>"
    more = ('<section class="sec tight paper"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">MORE GUIDES</p><h2 class="d3">ほかのガイド</h2></div><div class="list">'
            + "".join(f'<a class="li" href="{u}"><span class="t">{e(t)}</span><span class="n" lang="en">{e(ey)}</span></a>' for u, t, ey in more_list(slug)) + "</div></div></section>")
    foot = f'<div class="wrap mfoot"><p>文・図：<a href="/about/">Machine Tool Scout</a>　公開 <time datetime="{PUB}">{PUB_J}</time>　更新 <time datetime="{PUB}">{PUB_J}</time></p></div>'
    main = ('<main id="main"><div class="page">' + crumbs_html(cr) +
            f'<section class="phero wrap"><p class="eyebrow" lang="en">{p["eyebrow"]}</p><h1 class="d2">{e(p["h1"])}</h1><p class="sub lead" style="margin:20px auto 0">{e(p["lead"])}</p></section>'
            f'<section class="sec tight"><div class="wrap"><article class="prose gx">{p["body"]}{nav}</article></div></section>' + more + "</div>" + foot + "</main>")
    pg = page("machine-tools/guide/machine-accuracy/index.html", p["title"], p["desc"], path, cr, main).replace("</style>", CSS + LP_CSS + "</style>", 1)
    pg = re.sub(r'"datePublished":"[0-9-]+"', f'"datePublished":"{PUB}"', pg)
    write(path.lstrip("/") + "index.html", pg)

for s in ORDER: build(s)

# ---------------------------------------------------------------------
# links
# ---------------------------------------------------------------------
def cards(slugs):
    return "".join(f'<a class="li" href="{G}{s}/"><span class="t">{e(PAGES[s]["h1"])}</span><span class="n" lang="en">{PAGES[s]["eyebrow"]}</span></a>' for s in slugs)
HB = [s for s in ORDER if s != "learning-path"]
# guide index: a handbook block right after the page hero
gi = read("machine-tools/guide/index.html")
blk = ('<section class="sec tight paper"><div class="wrap"><div class="hd row"><div><p class="eyebrow" lang="en">HANDBOOK</p><h2 class="d3">実務ハンドブック</h2>'
       '<p class="sub">選んだあとに要る知識。条件の計算、工具、プログラム、精度、研削、設備計画、保全、安全を、計算ツール付きでまとめた。</p></div>'
       f'<a class="lnk" href="{G}learning-path/">はじめての人は学びの順路から</a></div><div class="list">' + cards(HB) + "</div></div></section>")
m = re.search(r'</section>', gi[gi.index('<section class="phero'):])
pos = gi.index('<section class="phero') + m.end()
gi = gi[:pos] + blk + gi[pos:]
write("machine-tools/guide/index.html", gi)
# hub: "start here" + handbook, right after the hero
hub = read("machine-tools/index.html")
start = ('<section class="sec tight"><div class="wrap"><div class="hd row"><div><p class="eyebrow" lang="en">START HERE</p><h2 class="d3">はじめての人へ。</h2>'
         '<p class="sub">工作機械とは何かから、削る仕組み、旋盤とマシニングセンタ、工具、NCプログラム、精度、研削、自動化、保全と安全まで。読む順番を10のステップにした。</p></div>'
         f'<a class="lnk" href="{G}learning-path/">学びの順路を見る</a></div>'
         '<ol class="hubsteps">' + "".join(f'<li><a href="{links[0][0]}"><span class="n" lang="en">{i:02d}</span><span class="t">{e(t)}</span></a></li>' for i, (t, d, links) in enumerate(STEPS, 1)) + '</ol>'
         '<div class="hd" style="margin-top:clamp(48px,6vw,80px)"><p class="eyebrow" lang="en">HANDBOOK</p><h2 class="d3">実務ハンドブック</h2><p class="sub">切削条件・研削条件・設備計画・熱変位などは、計算ツールで数字を確かめながら読める。</p></div>'
         '<div class="list">' + cards(HB) + "</div></div></section>")
HUB_CSS = (".hubsteps{list-style:none;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;counter-reset:none}"
           ".hubsteps a{display:flex;flex-direction:column;gap:8px;height:100%;padding:16px 16px 18px;border-radius:8px;box-shadow:0 0 0 1px var(--hair);transition:box-shadow .25s,transform .45s var(--spring)}"
           ".hubsteps a:hover{box-shadow:0 0 0 1px var(--accent);transform:translateY(-2px)}.hubsteps .n{font:300 22px var(--f-en);color:var(--mark)}.hubsteps .t{font-size:14.5px;line-height:1.5}"
           "@media (max-width:900px){.hubsteps{grid-template-columns:repeat(2,minmax(0,1fr))}}")
i0 = hub.index('<section class="hero')
i1 = hub.index("</section>", i0) + len("</section>")
hub = hub[:i1] + start + hub[i1:]
hub = hub.replace("</style>", HUB_CSS + "</style>", 1)
hub = re.sub(r'<b class="tn">(\d+)</b><span>選び方ガイド</span>', lambda m: f'<b class="tn">{int(m.group(1)) + len(HB)}</b><span>選び方ガイド</span>', hub, count=1)
write("machine-tools/index.html", hub)

# machine pages: point to the handbook pages that matter for that machine
CUT = ["cnc-lathe", "vertical-machining-center", "horizontal-machining-center", "5-axis-machining-center", "double-column-machining-center", "turn-mill", "vertical-turning-lathe", "swiss-type-lathe", "transfer-machine"]
GRIND = ["cylindrical-grinder", "internal-grinder", "surface-grinder", "centerless-grinder", "gear-grinding-machine"]
for p in glob.glob("machine-tools/*/index.html"):
    slug = p.split("/")[1]
    s = read(p)
    if '<div class="pspec" role="table"' not in s: continue
    links = []
    if slug in CUT: links += [("cutting-conditions", "切削条件の計算"), ("cutting-tools", "切削工具"), ("nc-programming", "NCプログラム")]
    if slug in GRIND: links += [("grinding-conditions", "研削条件と砥石")]
    links += [("accuracy-testing", "精度検査"), ("maintenance-basics", "保全"), ("safety", "安全")]
    tip = ('<p class="tal hbline" style="margin-top:10px;font-size:14px">実務ハンドブック：'
           + "／".join(f'<a href="{G}{a}/">{b}</a>' for a, b in links) + "</p>")
    s = s.replace('<div class="pspec" role="table"', tip + '<div class="pspec" role="table"', 1)
    write(p, s)

# sitemap
sm = read("sitemap-machine-tools.xml")
add = "".join(f"<url><loc>https://ygms3208.github.io{G}{s}/</loc><lastmod>{PUB}</lastmod></url>\n" for s in ORDER if f"{G}{s}/<" not in sm)
write("sitemap-machine-tools.xml", sm.replace("</urlset>", add + "</urlset>"))
# search index
si_old = glob.glob("assets/search.*.json")[0]
d = json.load(open(si_old, encoding="utf-8"))
d["m"] += [[PAGES[s]["h1"], "ガイド", f"{G}{s}/"] for s in ORDER]
sj = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
si_new = f"assets/search.{hashlib.sha1(sj.encode()).hexdigest()[:10]}.json"
write(si_new, sj)
if si_new != si_old:
    os.remove(si_old)
    for p in glob.glob("**/*.html", recursive=True):
        s = read(p)
        if si_old in s: write(p, s.replace("/" + si_old, "/" + si_new))
# feed: newest first
fd = read("feed.xml")
ent = "".join(f'<entry><title>{e(PAGES[s]["title"])}</title><link href="https://ygms3208.github.io{G}{s}/"/><id>https://ygms3208.github.io{G}{s}/</id>'
              f'<updated>{PUB}T00:00:00+09:00</updated><summary>{e(PAGES[s]["desc"])}</summary></entry>\n' for s in ORDER)
fd = re.sub(r"<updated>[^<]+</updated>", f"<updated>{PUB}T00:00:00+09:00</updated>", fd, count=1)
fd = fd.replace("<entry>", ent + "<entry>", 1)
write("feed.xml", fd)
# llms.txt
ll = read("llms.txt")
sec = "\n## 実務ハンドブック（工作機械）\n" + "".join(f'- [{PAGES[s]["h1"]}](https://ygms3208.github.io{G}{s}/): {PAGES[s]["desc"]}\n' for s in ORDER)
write("llms.txt", ll.rstrip("\n") + "\n" + sec)
# heading glyphs for the Mincho subset (picked up on the next build)
ex = open(f"{S}/extra_chars.txt", encoding="utf-8").read()
chars = "".join(PAGES[s]["h1"] + "".join(re.findall(r"<h[23][^>]*>([^<]*)</h[23]>", PAGES[s]["body"])) for s in ORDER) + "はじめての人へ。実務ハンドブック学びの順路" + "".join(t for t, _, _ in STEPS)
open(f"{S}/extra_chars.txt", "w", encoding="utf-8").write("".join(sorted(set(ex) | set(chars))))
print("handbook:", len(ORDER), "pages")
