#!/usr/bin/env python3
"""Apply the atlas refinement to the generated site in-place (idempotent from git HEAD)."""
import glob, hashlib, html, os, re, subprocess, sys
from html.parser import HTMLParser

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.dirname(os.path.abspath(__file__))
os.chdir(SITE)
BASE = "5ca5a0e"
KEEP = ("tools/", "CLAUDE.md", ".github/", ".gitignore")
# throw away the previous run's output (but never the generator itself or uncommitted edits to it)
subprocess.run(["git", "checkout", "-q", "HEAD", "--", ".", ":(exclude)tools", ":(exclude)CLAUDE.md", ":(exclude).gitignore"], check=True)
subprocess.run(["git", "clean", "-fdq", "--", ".", ":(exclude)tools", ":(exclude)CLAUDE.md", ":(exclude).gitignore"], check=True)
for f in subprocess.run(["git", "diff", "--name-only", "--diff-filter=A", BASE, "HEAD"], capture_output=True, text=True).stdout.split():
    if not f.startswith(KEEP) and os.path.exists(f): os.remove(f)
subprocess.run(["git", "checkout", BASE, "--", "."], check=True)
for f in glob.glob("assets/app.*.js") + glob.glob("assets/fonts/atlas-mincho.*.woff2"):
    if subprocess.run(["git", "ls-files", "--error-unmatch", f], capture_output=True).returncode:
        os.remove(f)

STYLE_RE = re.compile(r"<style>(.*?)</style>", re.S)
pages = sorted(glob.glob("**/*.html", recursive=True))

# ---------- home markup ----------
idx = open("index.html", encoding="utf-8").read()
idx = idx.replace("<body>", '<body class="home">', 1)
idx = idx.replace("</title>", '</title><script>document.documentElement.classList.add("js")</script>', 1)

hero_svg = re.search(r'<div class="v">(<svg.*?</svg>)<div class="sweep"></div></div>', idx, re.S)
assert hero_svg
stats = dict(re.findall(r'<div><b class="tn">(\d+)</b><span>([^<]+)</span></div>', idx))
en = {"系統": "SYSTEMS", "部品": "PARTS", "工程": "OPERATIONS", "設備": "EQUIPMENT"}
stats_html = "".join(f'<div><b class="tn" data-n="{n}">{n}</b><span>{l}<small lang="en">{en[l]}</small></span></div>' for n, l in stats.items())
old_hero = re.search(r'<section class="hero night">.*?</section>', idx, re.S).group(0)
new_hero = (
    '<section class="hero night"><div class="wrap hx"><div class="t">'
    '<p class="meta" lang="en"><span><b>Vol.01</b></span><span>Manufacturing Process Atlas</span><span>Ed. 2026</span></p>'
    '<h1 class="kicker">製造工程図鑑：部品の製造工程と工作機械を図解</h1>'
    '<p class="d1"><span class="ln"><span>ものは、</span></span><span class="ln"><span>工程で</span></span><span class="ln"><span>できている。</span></span></p>'
    '<p class="sub">クルマ、船のエンジン、データセンターの非常用発電機。部品をつくる工程と、そこで働く工作機械・検査機を、ひとつずつ解き明かす図鑑。</p>'
    '<p class="ctas"><a class="cta" href="#industries">業界から見る</a><a class="lnk" href="/systems/">部品を見る</a></p></div>'
    f'<figure class="v">{hero_svg.group(1)}<div class="sweep"></div>'
    '<figcaption><span class="en" lang="en">Fig. 01</span><span>ホブ盤による歯切り。ホブと歯車を同期させて回し、歯を一枚ずつ削り出す。</span></figcaption></figure></div>'
    f'<div class="wrap"><div class="hstats">{stats_html}</div><p class="hnote">数はこの図鑑の分類で数えたものです。</p></div>'
    '<div class="cue" aria-hidden="true" lang="en"><span>Scroll</span><i></i></div></section>'
)
idx = idx.replace(old_hero, new_hero)

# process ticker after hero
methods = [("鋳造", "casting", "Casting"), ("鍛造", "forging", "Forging"), ("プレス", "stamping", "Stamping"),
           ("切削", "machining", "Machining"), ("研削", "grinding", "Grinding"), ("歯切り", "gear-cutting", "Gear cutting"),
           ("熱処理", "heat-treatment", "Heat treatment"), ("表面処理", "surface-treatment", "Surface"),
           ("溶接・接合", "joining", "Joining"), ("樹脂成形", "molding", "Molding"), ("塗装", "painting", "Painting"),
           ("巻線", "coil-winding", "Winding"), ("組立", "assembly", "Assembly"), ("検査", "inspection", "Inspection")]
run = "".join(f'<a href="/methods/{s}/">{j}<small lang="en">{e}</small></a>' for j, s, e in methods)
run_h = "".join(f'<a href="/methods/{s}/" tabindex="-1">{j}<small lang="en">{e}</small></a>' for j, s, e in methods)
ticker = f'<nav class="tick" aria-label="加工法"><div class="row"><div>{run}</div><div aria-hidden="true">{run_h}</div></div></nav>'
idx = idx.replace(new_hero, new_hero + ticker)

# numbered section heads + reveal hooks
n = 0
def num(m):
    global n
    n += 1
    return f'<p class="eyebrow" lang="en"><span class="no">{n:02d}</span>{m.group(1)}</p>'
idx = re.sub(r'(?<=<div class="hd">)<p class="eyebrow" lang="en">([^<]+)</p>', num, idx)
idx = re.sub(r'(?<=<div class="hd row"><div>)<p class="eyebrow" lang="en">([^<]+)</p>', num, idx)
idx = idx.replace('<div class="hd" style="align-items:center;text-align:center"><p class="eyebrow" lang="en">AUTOMOTIVE · POWERTRAIN</p>',
                  '<div class="hd">' + num(re.match(r"(.*)", "AUTOMOTIVE · POWERTRAIN")))
idx = idx.replace('<p class="sub center">', '<p class="sub">')
# re-number in document order
n = 0
idx = re.sub(r'<span class="no">\d\d</span>', lambda m: (globals().__setitem__("n", n + 1), f'<span class="no">{n:02d}</span>')[1], idx)
idx = idx.replace('<div class="hd">', '<div class="hd" data-r>').replace('<div class="hd row">', '<div class="hd row" data-r>')
for cls in ("fcard", "card", "tile full dk mtpromo"):
    k = 0
    def rv(m):
        global k
        k += 1
        return f'{m.group(0)} data-r style="--i:{(k - 1) % 4}"'
    idx = re.sub(rf'<a class="{cls}"', rv, idx)
idx = re.sub(r'class="tile ([^"]*)\brv"', lambda m: f'class="tile {m.group(1).strip()}" data-r', idx)
idx = idx.replace('<div class="cols2">', '<div class="cols2" data-r>').replace('<div class="pills">', '<div class="pills" data-r>')
idx = idx.replace('<div id="ptbox">', '<div id="ptbox" data-r>')

# statement before highlights
words = ["1本の", "クランクシャフトは、", "<em>鍛えられ、</em>", "<em>削られ、</em>", "<em>焼きを入れられ、</em>",
         "<em>磨かれ、</em>", "<em>測られる。</em>", "16の", "工程を", "くぐって、", "ようやく", "部品になる。"]
q = "".join(w if w.startswith("<em>") else f"<span>{w}</span>" for w in words)
stmt = (f'<section class="stmt"><div class="wrap"><p class="q">{q}</p>'
        '<p class="src" data-r><span>クランクシャフト　OP10 素材切断 ― OP160 最終検査</span>'
        '<a class="lnk" href="/parts/crankshaft/">16工程を順に見る</a></p></div></section>')
hl = idx.index('<section class="sec"><div class="wrap"><div class="hd" data-r><p class="eyebrow" lang="en"><span class="no">03</span>HIGHLIGHTS')
idx = idx[:hl] + stmt + idx[hl:]

# closing colophon before footer
fin = ('<section class="fin" aria-label="結び"><div class="wrap"><p class="d1" data-r>部品の数だけ、<br>工程がある。</p><p class="go" data-r><a class="cta" href="/systems/">147の部品を見る</a></p>'
       '<p class="end" lang="en" data-r><span>Manufacturing Process Atlas</span><span>147 Parts · 1174 Operations · 279 Equipment</span></p></div></section>')
idx = idx.replace("</main><footer", fin + "</main><footer", 1)
open("index.html", "w", encoding="utf-8").write(idx)

# ---------- font subset: every glyph set in display type ----------
class Grab(HTMLParser):
    def __init__(s):
        super().__init__(); s.depth = 0; s.stack = []; s.buf = []; s.tile = 0; s.tstack = []; s.foot = False
    def handle_starttag(s, tag, a):
        cls = dict(a).get("class") or ""
        if tag in ("br", "img", "input", "meta", "link", "path", "rect", "circle", "line", "polygon", "polyline", "ellipse", "use"):
            return
        if re.search(r"\btile\b", cls): s.tile += 1; s.tstack.append(True)
        else: s.tstack.append(False)
        disp = (tag in ("h1", "h2") and "kicker" not in cls) or re.search(r"\b(d1|d2|d3|q|brand|tick|fcard)\b", cls) or (tag == "h3" and s.tile) or (tag == "b" and s.depth == 0 and s.foot)
        if "foot" in cls.split(): s.foot = True
        s.stack.append(bool(disp)); s.depth += bool(disp)
    def handle_endtag(s, tag):
        if s.stack and tag not in ("br",):
            s.depth -= s.stack.pop(); s.tile -= s.tstack.pop()
    def handle_data(s, data):
        if s.depth > 0: s.buf.append(data)
chars = set("ものは、工程でできている。0123456789")
for p in pages:
    g = Grab(); g.feed(open(p, encoding="utf-8").read()); chars |= set("".join(g.buf))
chars |= set("ー－・「」『』（）！？：；…―〜%")
sys.path.insert(0, S)
from practice_data import DATA as _PD
chars |= set("導入と運用の実務仕様の打ち合わせ使い方の流れ知っておくべきこと0123456789")
for _d in _PD.values(): chars |= set("".join(t for t, _ in _d["know"]))
from glossary_data import TERMS as _GT, CATS as _GC
chars |= set("工作機械用語辞典選び方") | set("".join(t[1] for t in _GT)) | set("".join(c[1] for c in _GC))
if os.path.exists(f"{S}/extra_chars.txt"): chars |= set(open(f"{S}/extra_chars.txt", encoding="utf-8").read())
chars = {c for c in chars if ord(c) > 32}
src = f"{S}/font/zen-old-mincho-japanese-600-normal.woff2"
lat = f"{S}/font/zen-old-mincho-latin-600-normal.woff2"
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.merge import Merger
home_chars = set()
g = Grab(); g.feed(open("index.html", encoding="utf-8").read()); home_chars = set("".join(g.buf))
kana = {c for c in chars if ord(c) < 0x3400 or ord(c) > 0xFF00}
groups = [sorted(home_chars | kana), sorted(chars - home_chars - kana)]
opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
faces = []
def rng(cs):
    cps = sorted(ord(c) for c in cs); out = []; i = 0
    while i < len(cps):
        j = i
        while j + 1 < len(cps) and cps[j + 1] == cps[j] + 1: j += 1
        out.append(f"U+{cps[i]:x}" + (f"-{cps[j]:x}" if j > i else "")); i = j + 1
    return ",".join(out)
for gi, cs in enumerate(groups):
    f = TTFont(src); cov = set(f.getBestCmap()); cs = [c for c in cs if ord(c) in cov]
    s_ = subset.Subsetter(opts); s_.populate(text="".join(cs)); s_.subset(f); f.flavor = "woff2"; f.recalcTimestamp = False
    import tempfile; tmp = os.path.join(tempfile.gettempdir(), f"atlas-sub{gi}.woff2"); f.save(tmp); data = open(tmp, "rb").read()
    fp = f"/assets/fonts/atlas-mincho.{hashlib.sha1(data).hexdigest()[:10]}.woff2"
    open(fp[1:], "wb").write(data)
    faces.append(f'@font-face{{font-family:"Atlas Mincho";font-style:normal;font-weight:600;font-display:swap;src:url({fp}) format("woff2");unicode-range:{rng(cs)}}}')
    print(f"font chunk {gi}: {len(cs)} glyphs, {len(data)//1024} KB")
font_path = faces[0]

# ---------- js ----------
old_js = glob.glob("assets/app.*.js")[0]
js = open(old_js, encoding="utf-8").read() + open(f"{S}/atlas.js", encoding="utf-8").read()
jh = hashlib.sha1(js.encode()).hexdigest()[:10]
new_js = f"assets/app.{jh}.js"
open(new_js, "w", encoding="utf-8").write(js)
subprocess.run(["git", "rm", "-q", "-f", old_js], check=True)

# ---------- css + refs on every page ----------
layer = re.sub(r"@font-face\{[^}]*__FONT__[^}]*\}", lambda m: "".join(faces), open(f"{S}/atlas.css", encoding="utf-8").read())
layer = re.sub(r"/\*(?!\s*=+ Atlas).*?\*/", "", layer, flags=re.S)
layer = re.sub(r"\s*\n\s*", "", layer)
count = 0
for p in pages:
    s = open(p, encoding="utf-8").read()
    o = s
    s = STYLE_RE.sub(lambda m: "<style>" + m.group(1) + layer + "</style>", s, count=1)
    s = s.replace("/" + old_js, "/" + new_js)
    s = s.replace('<meta name="theme-color" content="#F4F4F2"', '<meta name="theme-color" content="#F1EFE9"')
    s = s.replace('<meta name="theme-color" content="#0B0B0C"', '<meta name="theme-color" content="#0F0F0E"')
    if s != o:
        open(p, "w", encoding="utf-8").write(s); count += 1
print("pages updated:", count, "js:", new_js)
