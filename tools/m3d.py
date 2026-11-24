#!/usr/bin/env python3
"""3D viewers: copy the bundle into /assets and put a 3D figure on the pages listed in PAGES.
To give a new page a 3D view, add it to PAGES (or write the same <figure class="m3d"> markup into the page's generator).
Scenes live in tools/m3d/src.js (rebuild with tools/m3d/build.sh). Rules: CLAUDE.md, section 2-2."""
import hashlib, html, os, re, shutil
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(SITE)

# scene -> (heading, lead)
SCENE_TEXT = {
    "gears": ("かみ合いを3Dで見る", "図をドラッグすると向きを変えられます。歯の形と、ピッチ円（点線）どうしがすべらずに転がる様子を、好きな角度から確かめてください。"),
    "ballscrew": ("ボールの循環を3Dで見る", "ナットを透かしています。ねじ溝を転がったボールが、端まで来るとリターン経路を通って戻る様子を確かめられます。"),
    "lguide": ("ボールの循環を3Dで見る", "ブロックを透かしています。4列のボールが、レールの溝を転がってからブロックの中を通って戻る様子を確かめられます。"),
    "fiveaxis": ("5軸の動きを3Dで見る", "テーブル傾斜形（トラニオン形）の5軸です。A軸でクレードルが傾き、C軸でテーブルが回ります。工具はまっすぐのまま、工作物の向きが変わります。"),
    "strokes": ("ストロークを3Dで見る", "X・Y・Zの3軸が順に動きます。点線の箱が、工具の届く範囲（ストローク）です。"),
    "bearing": ("転がりを3Dで見る", "外輪の一部を切り欠いています。内輪が回ると、玉と保持器がどう動くかを確かめられます。"),
}
# page -> (scene, {data-*}, where)   where: "anat" = after the structure-diagram section, "paper" = before the first paper section,
#                                     "before:<regex>" = inline, before the first match (for long guides)
PAGES = {
    "machine-elements/gear-guide/index.html": ("gears", {"z1": 18, "z2": 30, "toggle": "helix"}, r'before:<h2 id="g-material"'),
    "parts/gear-mass-production/index.html": ("gears", {"z1": 19, "z2": 37, "toggle": "helix"}, "anat"),
    "parts/gear-large-one-off/index.html": ("gears", {"z1": 17, "z2": 53, "toggle": "helix"}, "anat"),
    "parts/transmission-gear/index.html": ("gears", {"z1": 23, "z2": 31, "helix": 25, "toggle": "helix"}, "anat"),
    "parts/e-axle-reduction-gear/index.html": ("gears", {"z1": 19, "z2": 58, "helix": 25, "toggle": "helix"}, "anat"),
    "machine-tools/components/ball-screw/index.html": ("ballscrew", {}, "anat"),
    "parts/precision-ball-screw/index.html": ("ballscrew", {}, "anat"),
    "machine-tools/components/linear-guide/index.html": ("lguide", {}, "anat"),
    "machine-tools/guide/guideways/index.html": ("lguide", {}, "paper"),
    "machine-tools/5-axis-machining-center/index.html": ("fiveaxis", {}, "anat"),
    "machine-tools/guide/3-axis-vs-5-axis/index.html": ("fiveaxis", {}, "paper"),
    "machine-tools/vertical-machining-center/index.html": ("strokes", {}, "anat"),
    "machine-tools/guide/interference-diagram/index.html": ("strokes", {}, "paper"),
    "parts/ball-bearing/index.html": ("bearing", {}, "anat"),
    "parts/hub-bearing/index.html": ("bearing", {"rows": 2}, "anat"),
}

# ---- the bundle ----
src = os.path.join(SITE, "tools", "m3d", "m3d.bundle.js")
data = open(src, "rb").read()
for f in os.listdir("assets"):
    if f.startswith("m3d.") and f.endswith(".js"): os.remove(os.path.join("assets", f))
url = f"/assets/m3d.{hashlib.sha1(data).hexdigest()[:10]}.js"
open(url[1:], "wb").write(data)

def figure(scene, attrs):
    a = "".join(f' data-{k}="{html.escape(str(v))}"' for k, v in attrs.items())
    return (f'<figure class="m3d" data-3d="{scene}"{a}><div class="m3d-stage"></div>'
            '<div class="m3d-bar"><div class="m3d-ui"></div><span class="m3d-hint">ドラッグで向きを変えられます</span></div>'
            '<figcaption class="m3d-note"></figcaption></figure>')

n = 0
for page, (scene, attrs, where) in PAGES.items():
    if not os.path.exists(page): print("m3d: missing", page); continue
    s = open(page, encoding="utf-8").read()
    if 'class="m3d"' in s: continue
    h, lead = SCENE_TEXT[scene]
    fig = figure(scene, attrs)
    if where.startswith("before:"):
        m = re.search(where[7:], s)
        if not m: print("m3d: anchor not found on", page); continue
        block = f'<div class="m3dinline"><h3 class="m3dh">{h}</h3><p class="m3dlead">{lead}</p>{fig}</div>'
        s = s[:m.start()] + block + s[m.start():]
    else:
        sec = (f'<section class="sec tight m3dsec"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">IN 3D</p>'
               f'<h2 class="d3">{h}</h2><p class="sub">{lead}</p></div>{fig}</div></section>')
        pos = -1
        if where == "anat" and 'class="anat"' in s:
            pos = s.find("</section>", s.index('class="anat"'))
            if pos >= 0: pos += len("</section>")
        if pos < 0:
            m = re.search(r'<section class="sec tight paper', s)
            pos = m.start() if m else -1
        if pos < 0:
            m = re.search(r"</main>", s); pos = m.start()
        s = s[:pos] + sec + s[pos:]
    s = s.replace("<html ", f'<html data-m3d="{url}" ', 1)
    open(page, "w", encoding="utf-8").write(s); n += 1
print("3D views on", n, "pages ->", url)
