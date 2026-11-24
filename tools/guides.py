#!/usr/bin/env python3
"""Guides: spindle torque chart, interference/working-range diagrams, physical AI. Runs after products.py, before glossary.py."""
import collections, glob, html, json, math, os, re, sys
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from practice_data import DATA as PRACTICE
# load only the helper functions of products.py (running that script twice would duplicate its edits)
_src = open(os.path.join(S, "products.py"), encoding="utf-8").read()
_helpers = _src[_src.index("# ---------- helpers ----------"):_src.index("# ---------- write standalone images")]
class _NS: pass
P = _NS()
_g = {"__name__": "helpers", "html": html, "json": json, "re": re, "os": os, "glob": glob, "B": "https://ygms3208.github.io", "TODAY": "2026-11-15", "TODAY_J": "2026年11月15日",
      "e": lambda s: html.escape(s, quote=False), "ea": lambda s: html.escape(s, quote=True), "NEWEQ": {}, "DRAW": {}}
P.SITE = os.path.dirname(S)
os.chdir(P.SITE)
exec(_helpers, _g)
e, ea, write, read, page, crumbs_html = _g["e"], _g["ea"], _g["write"], _g["read"], _g["page"], _g["crumbs_html"]
def _add_urls(fn, urls):
    s = read(fn)
    add = "".join(f"<url><loc>https://ygms3208.github.io{u}</loc><lastmod>2026-11-15</lastmod></url>\n" for u in urls if f"https://ygms3208.github.io{u}<" not in s)
    write(fn, s.replace("</urlset>", add + "</urlset>"))
P.add_urls = _add_urls
TODAY, TODAY_J = "2026-11-15", "2026年11月15日"
MFOOT = f'<div class="wrap mfoot"><p>文・図：<a href="/about/">Machine Tool Scout</a>　公開 <time datetime="{TODAY}">{TODAY_J}</time>　更新 <time datetime="{TODAY}">{TODAY_J}</time></p></div>'
TPL = "machine-tools/guide/machine-accuracy/index.html"
G = "/machine-tools/guide/"
NEW = [("spindle-torque-chart", "主軸のトルク線図の見方", "HOW TO READ"), ("interference-diagram", "干渉図・動作範囲図の見方", "HOW TO READ"),
       ("guideways", "案内面（すべり案内・リニアガイド・静圧案内）の比較", "COMPARE"), ("grinding-coolant", "研削盤のクーラントユニット", "GRINDING"),
       ("maintenance-standards", "保全部隊が見るところと完成立会いの指摘事項", "PRACTICE")]

CSS = ("/*gx*/.gx{max-width:860px}.gx h2{scroll-margin-top:calc(var(--gn) + 20px);padding-top:28px;border-top:1px solid var(--ink);font-size:clamp(24px,2.6vw,32px)}"
       ".gx h3{font-size:18px;margin:32px 0 10px}"
       ".gx .note{font-size:14.5px;padding:16px 20px;border-left:2px solid var(--mark);background:var(--paper);border-radius:0 6px 6px 0;color:var(--ink2)}.gx .note b{color:var(--mark);font-weight:500;margin-right:8px}"
       ".gx .eq{font:400 15px/2 var(--f-en);background:var(--paper);border-radius:6px;padding:16px 20px;margin:0 0 1.3em;color:var(--ink)}.gx .eq span{display:block}.gx .eq small{font-family:var(--f-jp);color:var(--muted);margin-left:10px;font-size:13px}"
       ".lab{background:var(--paper);border-radius:8px;box-shadow:0 0 0 1px var(--hair2);padding:clamp(16px,2.4vw,28px);margin:10px 0 34px}"
       ".lab svg{display:block;width:100%;height:auto}.lab .ax{stroke:var(--ink);stroke-width:1}.lab .grid{stroke:var(--hair);stroke-width:1}.lab text{fill:var(--ink2);font:500 12px var(--f-jp)}"
       ".lab text.en{font-family:var(--f-en)}.lab .tq{fill:none;stroke:var(--ink);stroke-width:2.4}.lab .tq6{fill:none;stroke:var(--ink);stroke-width:1.6;stroke-dasharray:6 5}"
       ".lab .pw{fill:none;stroke:var(--mark);stroke-width:2.4}.lab .pw6{fill:none;stroke:var(--mark);stroke-width:1.6;stroke-dasharray:6 5}"
       ".lab .zone{fill:var(--ink);opacity:.045}.lab .zl{font-size:11px;fill:var(--muted)}.lab .cur{stroke:var(--accent);stroke-width:1.4}.lab .dot{fill:var(--accent)}"
       ".lab .ctl{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;margin-top:14px;font-size:14px}"
       ".lab input[type=range]{flex:1;min-width:200px;accent-color:var(--mark)}"
       ".lab .read{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:14px}"
       ".lab .read div{background:var(--bg);border-radius:6px;padding:10px 14px}.lab .read b{display:block;font:300 26px var(--f-en);color:var(--ink)}.lab .read span{font-size:12px;color:var(--muted)}"
       ".lab .msg{margin-top:12px;font-size:14.5px;line-height:1.9;color:var(--ink2)}.lab .msg strong{color:var(--mark)}"
       ".lab form{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px 18px}.lab label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--ink2)}"
       ".lab label input{height:40px;border:1px solid var(--hair);border-radius:6px;background:var(--bg);color:var(--ink);font:400 16px var(--f-en);padding:0 12px}"
       ".lab .ok{color:#1F7A5C}.lab .ng{color:var(--mark)}"
       ".legend2{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:12.5px;color:var(--ink2);margin-top:8px}.legend2 i{display:inline-block;width:22px;height:0;border-top:2.4px solid var(--ink);vertical-align:middle;margin-right:6px}"
       ".legend2 i.p{border-color:var(--mark)}.legend2 i.d{border-top-style:dashed;border-top-width:1.6px}"
       ".bars{margin:8px 0 30px}.bars .r{display:grid;grid-template-columns:10em minmax(0,1fr) 4.5em;gap:12px;align-items:center;padding:7px 0;border-bottom:1px solid var(--hair);font-size:14px}"
       ".bars .b{height:10px;background:var(--soft);border-radius:999px;overflow:hidden}.bars .b i{display:block;height:100%;background:var(--ink);border-radius:999px}.bars .r.hi .b i{background:var(--mark)}"
       ".bars .n{font:400 14px var(--f-en);text-align:right}"
       ".layers{list-style:none;padding:0;counter-reset:ly}.layers>li{counter-increment:ly;position:relative;margin:0 0 18px;padding:18px 20px 18px 64px;background:var(--paper);border-radius:6px;box-shadow:0 0 0 1px var(--hair2)}"
       ".layers>li::before{content:counter(ly,decimal-leading-zero);position:absolute;left:20px;top:16px;font:300 24px var(--f-en);color:var(--mark)}"
       ".layers h3{margin:0 0 6px;font-size:18px}.layers p{margin:.4em 0;font-size:15px}.layers .st{display:inline-block;font-size:11.5px;letter-spacing:.1em;padding:2px 9px;border-radius:999px;margin-right:6px;border:1px solid var(--hair)}"
       ".layers .st.now{border-color:#1F7A5C;color:#1F7A5C}.layers .st.near{border-color:var(--accent);color:var(--accent)}.layers .st.far{border-color:var(--mark);color:var(--mark)}"
       "@media (max-width:640px){.bars .r{grid-template-columns:7em minmax(0,1fr) 3.6em}.layers>li{padding-left:20px;padding-top:48px}}"
       "@media (max-width:760px){.gx .tw{overflow:visible}.gx table{min-width:0}.gx thead{display:none}.gx tr{display:block;padding:14px 0;border-bottom:1px solid var(--hair)}"
       ".gx td{display:block;border:0;padding:3px 0;white-space:normal}.gx td:first-child{font-size:16px;padding-bottom:6px}"
       ".gx td+td::before{content:attr(data-l);display:block;font-size:11px;letter-spacing:.1em;color:var(--muted);margin-top:4px}}")

def guide_page(slug, title_h1, eyebrow, lead, body, title, desc, extra_js=""):
    path = f"{G}{slug}/"
    cr = [("トップ", "/"), ("工作機械図鑑", "/machine-tools/"), ("選び方", G), (title_h1, path)]
    more = ('<section class="sec tight paper"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">MORE GUIDES</p><h2 class="d3">ほかのガイド</h2></div><div class="list">'
            + "".join(f'<a class="li" href="{G}{s}/"><span class="t">{e(t)}</span><span class="n" lang="en">{ey}</span></a>' for s, t, ey in NEW if s != slug)
            + f'<a class="li" href="{G}machine-accuracy/"><span class="t">工作機械の精度の見方</span><span class="n" lang="en">COMPARE</span></a>'
            + f'<a class="li" href="/machine-tools/physical-ai/"><span class="t">フィジカルAIと工作機械</span><span class="n" lang="en">ESSAY</span></a>'
            + f'<a class="li" href="{G}"><span class="t">工作機械の選び方</span><span class="n" lang="en">GUIDE</span></a></div></div></section>')
    main = ('<main id="main"><div class="page">' + crumbs_html(cr) +
            f'<section class="phero wrap"><p class="eyebrow" lang="en">{eyebrow}</p><h1 class="d2">{e(title_h1)}</h1><p class="sub lead" style="margin:20px auto 0">{e(lead)}</p></section>'
            f'<section class="sec tight"><div class="wrap"><article class="prose gx">{body}</article></div></section>' + more + "</div>" + MFOOT + extra_js + "</main>")
    pg = page(TPL, title, desc, path, cr, main).replace("</style>", CSS + "</style>", 1)
    write(path.lstrip("/") + "index.html", pg)

def T(head, rows):
    return ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f'<td data-l="{head[i]}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows) + "</tbody></table></div>")

# =====================================================================
# 1. spindle torque chart
# =====================================================================
NMAX, NB, NC = 12000, 1500, 8000
P1, P6 = 11.0, 15.0
def power(n, pr):
    if n <= NB: return pr * n / NB
    if n <= NC: return pr
    return pr * (1 - 0.30 * (n - NC) / (NMAX - NC))
def torque(n, pr): return 9549 * power(max(n, 1), pr) / max(n, 1) if n > 0 else 9549 * pr / NB
W, H, L, R, TOP, BOT = 640, 360, 62, 64, 26, 300
TMAX, PMAX = 120, 24
X = lambda n: L + (W - L - R) * n / NMAX
YT = lambda t: BOT - (BOT - TOP) * t / TMAX
YP = lambda p: BOT - (BOT - TOP) * p / PMAX
def path(fn, pr, Y):
    pts = [(X(n), Y(fn(n, pr))) for n in range(60, NMAX + 1, 60)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
grid = "".join(f'<line class="grid" x1="{X(n):.1f}" y1="{TOP}" x2="{X(n):.1f}" y2="{BOT}"/><text class="en" x="{X(n):.1f}" y="{BOT + 18}" text-anchor="middle">{n:,}</text>' for n in range(0, NMAX + 1, 2000))
grid += "".join(f'<line class="grid" x1="{L}" y1="{YT(t):.1f}" x2="{W - R}" y2="{YT(t):.1f}"/><text class="en" x="{L - 8}" y="{YT(t) + 4:.1f}" text-anchor="end">{t}</text><text class="en" x="{W - R + 8}" y="{YP(t * PMAX / TMAX) + 4:.1f}">{t * PMAX // TMAX}</text>' for t in range(0, TMAX + 1, 20))
zones = (f'<rect class="zone" x="{X(0):.1f}" y="{TOP}" width="{X(NB) - X(0):.1f}" height="{BOT - TOP}"/>'
         f'<text class="zl" x="{(X(0) + X(NB)) / 2:.1f}" y="{TOP + 14}" text-anchor="middle">定トルク域</text>'
         f'<text class="zl" x="{(X(NB) + X(NC)) / 2:.1f}" y="{TOP + 14}" text-anchor="middle">定出力域</text>'
         f'<rect class="zone" x="{X(NC):.1f}" y="{TOP}" width="{X(NMAX) - X(NC):.1f}" height="{BOT - TOP}"/>'
         f'<text class="zl" x="{(X(NC) + X(NMAX)) / 2:.1f}" y="{TOP + 14}" text-anchor="middle">高速域（出力が落ちる）</text>')
chart = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="主軸のトルク線図と出力線図の例" id="tqsvg">{zones}{grid}'
         f'<line class="ax" x1="{L}" y1="{BOT}" x2="{W - R}" y2="{BOT}"/><line class="ax" x1="{L}" y1="{TOP}" x2="{L}" y2="{BOT}"/><line class="ax" x1="{W - R}" y1="{TOP}" x2="{W - R}" y2="{BOT}"/>'
         f'<path class="tq6" d="{path(torque, P6, YT)}"/><path class="tq" d="{path(torque, P1, YT)}"/>'
         f'<path class="pw6" d="{path(power, P6, YP)}"/><path class="pw" d="{path(power, P1, YP)}"/>'
         f'<text x="{L - 44}" y="{TOP - 8}">トルク（N·m）</text><text x="{W - R + 44}" y="{TOP - 8}" text-anchor="end" style="fill:var(--mark)">出力（kW）</text>'
         f'<text x="{(L + W - R) / 2:.1f}" y="{H - 8}" text-anchor="middle">主軸回転数（min⁻¹）</text>'
         f'<text x="{X(900):.1f}" y="{YT(torque(900, P6)) - 8:.1f}" text-anchor="middle" class="en">95.5</text>'
         f'<line class="cur" id="tqcur" x1="0" y1="{TOP}" x2="0" y2="{BOT}"/><circle class="dot" id="tqd1" r="4.5"/><circle class="dot" id="tqd2" r="4.5" style="fill:var(--mark)"/></svg>')
tq_lab = (f'<div class="lab" id="tqlab">{chart}<div class="legend2"><span><i></i>トルク（連続定格 S1）</span><span><i class="d"></i>トルク（短時間定格 S6）</span>'
          '<span><i class="p"></i>出力（連続定格 S1）</span><span><i class="p d"></i>出力（短時間定格 S6）</span></div>'
          '<div class="ctl"><label for="tqn" style="flex-direction:row;align-items:center;gap:10px">回転数</label><input id="tqn" type="range" min="100" max="12000" step="50" value="1000"></div>'
          '<div class="read"><div><b id="tqrn">1,000</b><span>回転数（min⁻¹）</span></div><div><b id="tqrt">70.0</b><span>トルク S1（N·m）</span></div><div><b id="tqrp">7.3</b><span>出力 S1（kW）</span></div><div><b id="tqrp6">10.0</b><span>出力 S6（kW）</span></div></div>'
          '<p class="msg" id="tqmsg"></p></div>')
tq_js = ("<script>(function(){var NB=" + str(NB) + ",NC=" + str(NC) + ",NM=" + str(NMAX) + ",L=" + str(L) + ",W=" + str(W - L - R) + ",TOP=" + str(TOP) + ",BOT=" + str(BOT) + ",TM=" + str(TMAX) + ",PM=" + str(PMAX) + ";"
         "function pw(n,p){return n<=NB?p*n/NB:(n<=NC?p:p*(1-.3*(n-NC)/(NM-NC)))}function tq(n,p){return 9549*pw(n,p)/n}"
         "var s=document.getElementById('tqn');if(!s)return;function f(x,d){return x.toLocaleString('ja-JP',{minimumFractionDigits:d,maximumFractionDigits:d})}"
         "function up(){var n=+s.value,t=tq(n,11),p=pw(n,11),p6=pw(n,15),x=L+W*n/NM;"
         "var c=document.getElementById('tqcur');c.setAttribute('x1',x);c.setAttribute('x2',x);"
         "var a=document.getElementById('tqd1');a.setAttribute('cx',x);a.setAttribute('cy',BOT-(BOT-TOP)*t/TM);"
         "var b=document.getElementById('tqd2');b.setAttribute('cx',x);b.setAttribute('cy',BOT-(BOT-TOP)*p/PM);"
         "document.getElementById('tqrn').textContent=f(n,0);document.getElementById('tqrt').textContent=f(t,1);document.getElementById('tqrp').textContent=f(p,1);document.getElementById('tqrp6').textContent=f(p6,1);"
         "var m=n<NB?'<strong>定トルク域</strong>：トルクは一定で、出力は回転数に比例して増える。この回転数では最大出力の'+Math.round(p/11*100)+'%しか使えない。大径の正面フライス・ドリル・タップはここを使う。'"
         ":(n<=NC?'<strong>定出力域</strong>：出力は最大のまま一定で、トルクは回転数に反比例して下がる。回転数を2倍にするとトルクは半分になる。':'<strong>高速域</strong>：出力そのものが下がり始める。小径工具の高速加工・仕上げ向きで、重切削には向かない。');"
         "document.getElementById('tqmsg').innerHTML=m}s.addEventListener('input',up);up()})();</script>")

tq_body = f'''
<p class="note"><b>3行で</b>トルク線図は「この回転数で、どれだけの力（トルク）と仕事の速さ（出力）を出せるか」を表した図。カタログの最大出力は、限られた回転数の範囲でしか出ない。自分の加工で使う回転数のところで、線図の値を読むのが正しい使い方である。</p>

<h2 id="t-axes">何が描いてあるか</h2>
<p>横軸が主軸の回転数、縦軸がトルク（左、N·m）と出力（右、kW）。トルクは「回す力の強さ」、出力は「1秒あたりにできる仕事の量」で、次の関係で結ばれている。</p>
<div class="eq"><span>出力 P（kW）＝ トルク T（N·m）× 回転数 n（min⁻¹）÷ 9,549</span><span>トルク T ＝ 9,549 × P ÷ n</span></div>
<p>つまり、同じ出力なら回転数が低いほどトルクは大きく、回転数が高いほどトルクは小さい。下の図は、立形マシニングセンタでよくある「連続11kW・短時間15kW、基底回転数1,500min⁻¹、最高12,000min⁻¹」の主軸を想定した例である。回転数を動かして、線図の読み方を確かめてほしい。</p>
{tq_lab}

<h2 id="t-zones">3つの領域</h2>
{T(["領域", "回転数の範囲（例）", "トルク", "出力", "向いている加工"], [
 ["定トルク域", "0〜基底回転数（1,500）", "一定（最大）", "回転数に比例して増える", "大径の正面フライス、太いドリル、大きなタップ。低い回転数で大きな力が要る加工"],
 ["定出力域", "基底回転数〜約8,000", "回転数に反比例して下がる", "一定（最大）", "一般的なエンドミル加工。最も効率よく削れる範囲"],
 ["高速域", "約8,000〜最高回転数", "さらに下がる", "下がる", "小径工具の高速加工、仕上げ。重い切削には向かない"]])}
<p>2つの領域の境目の回転数を<b>基底回転数</b>という。「15kWの機械」と書いてあっても、たとえば500min⁻¹では15×500÷1,500＝5kWしか出ない。カタログの最大出力の数字だけで機械を比べてはいけない理由がここにある。</p>

<h2 id="t-ratings">実線と点線：連続定格と短時間定格</h2>
<p>多くの線図には2本の線が描かれている。モータは熱で能力が制限されるため、いつまで出し続けられるかで定格が分かれる。</p>
{T(["表示", "意味", "読み方"], [
 ["S1（連続定格）", "ずっと出し続けられる値", "量産で長く続く加工は、この線の内側で計画する"],
 ["S2（30分定格など）", "決めた時間（例：30分）なら出せる値", "大物の荒加工が長いときに確認する"],
 ["S3・S6（25%ED、40%EDなど）", "運転と休止を繰り返す前提で、運転の割合（ED）が25%などのときに出せる値", "工具交換や早送りをはさむ加工向け。カタログの「最大出力」はこちらのことが多い"]])}
<p>カタログの仕様表に「主軸出力 15/11kW」とあれば、短時間15kW・連続11kWの意味である。比べるときは、同じ種類の定格どうしをそろえる。</p>

<h2 id="t-example">例題：この正面フライスは削れるか</h2>
<p>炭素鋼を、直径63mmの正面フライスで削るとする。切込み3mm、削る幅50mm、テーブル送り1,000mm/min、切削速度200m/min。</p>
<div class="eq"><span>回転数 n ＝ 1,000 × 200 ÷（π × 63）≒ 1,010 min⁻¹</span><span>必要な切削動力 Pc ＝ 切込み × 幅 × 送り × 比切削抵抗 ÷（60 × 10⁶）</span><span>　＝ 3 × 50 × 1,000 × 2,000 ÷ 60,000,000 ≒ 5.0 kW<small>（比切削抵抗は鋼の目安2,000N/mm²）</small></span><span>モータに要る出力 ≒ 5.0 ÷ 0.8（機械効率）≒ 6.3 kW</span></div>
<p>線図で1,010min⁻¹を読むと、連続定格で約7.4kW、短時間定格で約10kW。6.3kWなら連続定格の内側に入るので、量産で続けても大丈夫と判断できる。もし同じ加工を「15kWの機械だから余裕」と思って切込みを倍にすると、1,010min⁻¹では連続定格を超えてしまう。<b>大径工具の重切削ほど、最大出力ではなく低い回転数でのトルクで決まる</b>のがポイントである。</p>

<h2 id="t-shapes">機種による線図の形の違い</h2>
{T(["主軸の形式", "線図の特徴", "向いている用途"], [
 ["ギヤ付き（2段変速など）", "低速段で大きなトルク、高速段で高回転。線図に山が2つ現れる", "重切削・大径工具を多く使う大型機"],
 ["ベルト駆動", "中程度のトルクと回転数のバランス型", "汎用のマシニングセンタ・旋盤"],
 ["ビルトインモータ（直結）", "高回転で振動が少ないが、低速のトルクは小さめ", "高速加工、金型、アルミ"],
 ["巻線切替え式のモータ", "低速用と高速用の巻線を切り替え、1台で広い範囲をカバーする", "1台で重切削と高速加工を両方こなしたい場合"]])}

<h2 id="t-check">機械を選ぶときに見るところ</h2>
<ul><li>自分の加工で一番重い工程（大径の正面フライス、太いドリル、タップ）の回転数で、<b>連続定格のトルク</b>が足りるか。</li>
<li>一番速い工程（小径エンドミルの仕上げ）の回転数で、高速域の出力が足りるか。</li>
<li>最大出力が<b>どの定格（S1・S3・S6）</b>の値か。比べる機械どうしでそろっているか。</li>
<li>工具を付けた状態での<b>加減速の時間</b>（0から最高回転まで何秒か）。タップや小穴の多い加工ではサイクルタイムに効く。</li>
<li>主軸テーパの大きさと保持の剛性。トルクが足りても、工具の保持が負けるとびびる。</li></ul>
<p class="note"><b>営業の現場から</b>線図を見せずに「最大出力」だけで比較表をつくると、導入後に「重切削で負ける」というトラブルになりやすい。打ち合わせでは、お客様の一番重い工程の回転数に線を引いて、その場で一緒に読むのが一番伝わる。</p>
'''
guide_page("spindle-torque-chart", "主軸のトルク線図の見方", "HOW TO READ",
           "カタログの「主軸出力 15kW」は、限られた回転数でしか出ない。トルク線図を読めば、自分の加工の回転数で本当に使える力が分かる。図を動かしながら、定トルク域・定出力域・連続定格と短時間定格の意味を押さえる。",
           tq_body, "主軸のトルク線図・出力線図の見方｜定トルク域・定出力域・S1/S6定格を図で解説｜工作機械図鑑",
           "工作機械の主軸のトルク線図・出力線図の読み方を、回転数を動かせる図で解説。定トルク域と定出力域、基底回転数、連続定格S1と短時間定格S6の違い、正面フライスの例題、機械を選ぶときの見方まで。", tq_js)

# =====================================================================
# 2. interference / working range
# =====================================================================
def lathe_svg():
    # top view of a turret lathe: chuck at left, work, turret below with tools; swing circle and interference
    return ('<svg viewBox="0 0 640 380" role="img" aria-label="NC旋盤の干渉図の例">'
            '<rect x="30" y="70" width="70" height="200" rx="6" style="fill:var(--soft);stroke:var(--ink)"/>'
            '<rect x="100" y="110" width="26" height="40" style="fill:var(--ink2)"/><rect x="100" y="190" width="26" height="40" style="fill:var(--ink2)"/>'
            '<rect x="100" y="140" width="220" height="60" style="fill:var(--bg);stroke:var(--ink)"/>'
            '<line x1="20" y1="170" x2="600" y2="170" style="stroke:var(--muted);stroke-dasharray:10 4 2 4"/>'
            '<text x="590" y="160" text-anchor="end">主軸中心</text>'
            '<circle cx="410" cy="300" r="70" style="fill:var(--paper);stroke:var(--ink)"/>'
            '<circle cx="410" cy="300" r="118" style="fill:none;stroke:var(--mark);stroke-dasharray:6 5"/>'
            '<rect x="400" y="190" width="20" height="45" style="fill:var(--ink2)"/><rect x="400" y="182" width="20" height="10" style="fill:var(--mark)"/>'
            '<rect x="330" y="292" width="45" height="16" style="fill:var(--ink2)" transform="rotate(-45 352 300)"/>'
            '<rect x="455" y="292" width="70" height="16" style="fill:var(--ink2)" transform="rotate(45 490 300)"/>'
            '<text x="478" y="112" style="fill:var(--mark)">刃物台の旋回径</text><text x="478" y="128" style="fill:var(--mark)">（外側の工具が描く円）</text><line x1="520" y1="134" x2="505" y2="190" style="stroke:var(--mark)"/>'
            '<path d="M120 250 L120 345" style="stroke:var(--ink)"/><path d="M114 339 L120 351 L126 339" style="fill:var(--ink)"/>'
            '<text x="128" y="330">チャックの爪・ワークと</text><text x="128" y="346">旋回円が重なると衝突</text>'
            '<line x1="320" y1="60" x2="320" y2="132" style="stroke:var(--accent)"/><line x1="100" y1="60" x2="100" y2="68" style="stroke:var(--accent)"/>'
            '<line x1="100" y1="64" x2="320" y2="64" style="stroke:var(--accent)"/><text x="210" y="56" text-anchor="middle" style="fill:var(--accent)">最大加工長さ</text>'
            '<line x1="350" y1="140" x2="350" y2="200" style="stroke:var(--accent)"/><text x="356" y="158" style="fill:var(--accent)">最大加工径</text>'
            '<line x1="22" y1="70" x2="22" y2="270" style="stroke:var(--accent)"/><text x="18" y="290" style="fill:var(--accent)">最大振り（ぶつからずに回せる径）</text>'
            '<text x="410" y="304" text-anchor="middle">タレット</text></svg>')

def mc_svg():
    return ('<svg viewBox="0 0 640 400" role="img" aria-label="立形マシニングセンタの動作範囲図の例（側面）">'
            '<rect x="430" y="40" width="70" height="320" style="fill:var(--soft);stroke:var(--ink)"/><text x="465" y="30" text-anchor="middle">コラム</text>'
            '<rect x="230" y="70" width="200" height="70" style="fill:var(--soft);stroke:var(--ink)"/><text x="330" y="100" text-anchor="middle">主軸頭</text>'
            '<rect x="296" y="140" width="28" height="22" style="fill:var(--ink2)"/><rect x="304" y="162" width="12" height="62" style="fill:var(--ink2)"/>'
            '<text x="286" y="156" text-anchor="end">主軸端</text>'
            '<rect x="120" y="300" width="300" height="28" style="fill:var(--soft);stroke:var(--ink)"/><text x="130" y="320">テーブル</text>'
            '<rect x="200" y="268" width="170" height="32" style="fill:var(--paper);stroke:var(--ink)"/><text x="285" y="289" text-anchor="middle">治具</text>'
            '<rect x="230" y="232" width="110" height="36" style="fill:var(--bg);stroke:var(--ink)"/><text x="285" y="255" text-anchor="middle">ワーク</text>'
            '<line x1="80" y1="140" x2="80" y2="300" style="stroke:var(--accent)"/><line x1="72" y1="140" x2="296" y2="140" style="stroke:var(--accent);stroke-dasharray:3 3"/><line x1="72" y1="300" x2="120" y2="300" style="stroke:var(--accent);stroke-dasharray:3 3"/>'
            '<text x="74" y="214" text-anchor="end" style="fill:var(--accent)">主軸端〜</text><text x="74" y="230" text-anchor="end" style="fill:var(--accent)">テーブル上面</text>'
            '<line x1="540" y1="70" x2="540" y2="210" style="stroke:var(--mark)"/><path d="M534 76 L540 64 L546 76" style="fill:var(--mark)"/><path d="M534 204 L540 216 L546 204" style="fill:var(--mark)"/>'
            '<text x="550" y="140" style="fill:var(--mark)">Z軸ストローク</text>'
            '<line x1="316" y1="162" x2="370" y2="162" style="stroke:var(--muted);stroke-dasharray:3 3"/><line x1="316" y1="224" x2="370" y2="224" style="stroke:var(--muted);stroke-dasharray:3 3"/>'
            '<line x1="366" y1="162" x2="366" y2="224" style="stroke:var(--ink)"/><text x="372" y="198">工具長</text>'
            '<line x1="120" y1="348" x2="420" y2="348" style="stroke:var(--accent)"/><text x="270" y="368" text-anchor="middle" style="fill:var(--accent)">テーブルの大きさ／X軸ストローク</text></svg>')

mc_lab = ('<div class="lab" id="fitlab"><form onsubmit="return false">'
          '<label>主軸端〜テーブル上面（最小）mm<input type="number" id="f_min" value="150"></label>'
          '<label>主軸端〜テーブル上面（最大）mm<input type="number" id="f_max" value="660"></label>'
          '<label>ATCで使える最大工具長 mm<input type="number" id="f_tl" value="300"></label>'
          '<label>治具の高さ mm<input type="number" id="f_jig" value="120"></label>'
          '<label>ワークの高さ mm<input type="number" id="f_w" value="180"></label>'
          '<label>いちばん長い工具の長さ mm<input type="number" id="f_l" value="250"></label>'
          '<label>いちばん深い加工の深さ mm<input type="number" id="f_d" value="60"></label>'
          '<label>工具をワークの上で逃がす余裕 mm<input type="number" id="f_c" value="20"></label></form>'
          '<div class="read"><div><b id="r_top">—</b><span>工具がワークの上に逃げたときの主軸端の高さ</span></div><div><b id="r_bot">—</b><span>いちばん深く削るときの主軸端の高さ</span></div></div><p class="msg" id="r_msg"></p></div>')
mc_js = ("<script>(function(){var ids=['min','max','tl','jig','w','l','d','c'];function v(k){return +document.getElementById('f_'+k).value||0}"
         "function up(){var top=v('jig')+v('w')+v('l')+v('c'),bot=v('jig')+v('w')-v('d')+v('l'),m=[],ok=true;"
         "document.getElementById('r_top').textContent=top.toLocaleString('ja-JP')+' mm';document.getElementById('r_bot').textContent=bot.toLocaleString('ja-JP')+' mm';"
         "if(top>v('max')){ok=false;m.push('<span class=ng>✕ 上に逃げられない</span>：工具をワークの上に逃がすには主軸端が'+top+'mm必要だが、最大'+v('max')+'mmしか上がらない。治具を低くする、短い工具にする、またはZ軸の長い機種が必要。')}"
         "if(bot<v('min')){ok=false;m.push('<span class=ng>✕ 下まで届かない</span>：いちばん深い所を削るには主軸端を'+bot+'mmまで下げる必要があるが、最小'+v('min')+'mmまでしか下がらない。かさ上げ（治具を高く）するか、長い工具が必要。')}"
         "if(v('l')>v('tl')){ok=false;m.push('<span class=ng>✕ ATCに入らない</span>：工具長'+v('l')+'mmが、自動交換できる最大の長さ'+v('tl')+'mmを超えている。')}"
         "if(ok){m.push('<span class=ok>○ 収まる</span>：上下とも範囲内。上の余裕 '+(v('max')-top)+'mm、下の余裕 '+(bot-v('min'))+'mm。工具交換時に主軸が上がる位置（ATC位置）でワークや治具に当たらないかも、干渉図で確かめる。')}"
         "document.getElementById('r_msg').innerHTML=m.join('<br>')}"
         "ids.forEach(function(k){document.getElementById('f_'+k).addEventListener('input',up)});up()})();</script>")

if_body = f'''
<p class="note"><b>3行で</b>干渉図・動作範囲図は「どこまで動けて、どこで何とぶつかるか」を表した図。カタログの「最大加工径」「ストローク」は、工具や治具を付けると実際には小さくなる。自分のワーク・治具・工具を図の上に置いて確かめるのが正しい使い方である。</p>

<h2 id="i-what">干渉図と動作範囲図の違い</h2>
{T(["図", "何が描いてあるか", "主に見る機種"], [
 ["動作範囲図（ワーキングレンジ）", "各軸が動ける範囲、主軸端とテーブルの距離、テーブルの大きさなど、加工できる空間の大きさ", "マシニングセンタ、5軸、門形"],
 ["干渉図（インターフェアレンス）", "刃物台の旋回、チャック、心押台、ATCの工具など、動いたときにぶつかる可能性のある範囲", "NC旋盤、複合加工機、5軸"],
 ["工具干渉図（ツーリング図）", "刃物台の各ステーションに付けた工具の位置と、突き出せる長さの上限", "NC旋盤、主軸移動形自動旋盤"]])}

<h2 id="i-lathe">NC旋盤の干渉図の読み方</h2>
<figure><div class="lab">{lathe_svg()}</div></figure>
<ul><li><b>最大振り</b>：ベッドやカバーにぶつからずに回せる最大の径。<b>最大加工径</b>はそれより小さく、刃物台が届いて削れる最大の径である。ワークがこの2つの間にあるなら、回せても削れない。</li>
<li><b>刃物台の旋回径</b>：タレットが回るとき、いちばん外に出ている工具の先が描く円。この円がチャックの爪・ワーク・心押台と重なると、工具を割り出した瞬間に衝突する。長いボーリングバーや大きなドリルを付けたときに特に危ない。</li>
<li><b>工具の突出し制限</b>：ツーリング図には、ステーションごとに工具を突き出せる長さの上限が描かれている。隣の工具や反対側の刃物台とぶつからない範囲である。</li>
<li><b>Z方向</b>：チャックの端面から刃物台までの距離で、加工できる長さと、長い工具を使ったときにチャックに近づける限界が決まる。</li></ul>
<p class="note"><b>現場でよくある失敗</b>カタログの最大加工径だけを見て決め、実際には爪の高さと内径用の工具の突出しで旋回径がぶつかる。打ち合わせでは「一番大きなワーク」「一番長い工具」「爪の形」を干渉図の上に描き込んで確かめる。</p>

<h2 id="i-mc">マシニングセンタの動作範囲図の読み方</h2>
<figure><div class="lab">{mc_svg()}</div></figure>
<p>立形マシニングセンタで一番見落とされやすいのが、<b>主軸端からテーブル上面までの距離</b>である。Z軸のストロークが500mmあっても、治具・ワーク・工具の長さを足すと、上下どちらかで足りなくなることがある。次の2つの条件を両方満たす必要がある。</p>
<div class="eq"><span>上の条件：治具の高さ ＋ ワークの高さ ＋ 工具長 ＋ 逃がす余裕 ≦ 主軸端〜テーブル（最大）</span><span>下の条件：治具の高さ ＋ ワークの高さ − 加工の深さ ＋ 工具長 ≧ 主軸端〜テーブル（最小）</span></div>
<p>自分の値を入れて確かめられる。初期値は、よくある立形マシニングセンタの例である。</p>
{mc_lab}
<h3>そのほかに見るところ</h3>
{T(["項目", "見るポイント"], [
 ["テーブルの大きさと積載質量", "ワーク＋治具が載るか。偏った重さでも許されるか"],
 ["X・Y軸のストローク", "テーブルの大きさより小さいことが多い。ワークの端の穴まで主軸が届くか"],
 ["ATCの工具の最大径・長さ・質量", "隣の工具を空けたときの最大径の条件も確認する"],
 ["ATC位置（工具交換のときの主軸の高さ）", "工具交換でZ軸が上がる位置で、長い工具が治具やワークに当たらないか"],
 ["扉の開口と吊り込み", "クレーンでワークを入れるなら、扉の開口の幅と上方向の開き"],
 ["ロータリテーブルの干渉円（第4軸・5軸）", "回したときにワークや治具の角が描く円が、機械のカバーや主軸頭に当たらないか"]])}

<h2 id="i-5axis">5軸・複合加工機はさらに慎重に</h2>
<p>回転軸がある機械では、傾けたときに主軸頭や治具が当たる範囲が、角度によって変わる。カタログの図は代表的な姿勢だけを描いていることが多いため、機械の3Dモデルを使ったシミュレーションで確かめるのが確実である。<a href="/machine-tools/5-axis-machining-center/">5軸マシニングセンタ</a>や<a href="/machine-tools/turn-mill/">複合加工機</a>の打ち合わせでは、メーカーに機械モデルの提供を依頼しておく。</p>
<p class="note"><b>営業の現場から</b>干渉は、機械が届いてから見つかると取り返しがつかない。発注前に「一番大きなワーク」「一番長い工具」「治具の外形」の3つをメーカーに渡し、干渉チェックの図を出してもらうのが、もっとも安い保険である。</p>
'''
guide_page("interference-diagram", "干渉図・動作範囲図の見方", "HOW TO READ",
           "カタログの「最大加工径」や「ストローク」は、工具・治具・ワークを付けると実際には小さくなる。干渉図と動作範囲図の読み方と、マシニングセンタにワークと工具が収まるかを確かめる計算を、図と一緒に解説する。",
           if_body, "干渉図・動作範囲図の見方｜NC旋盤とマシニングセンタで確かめること｜工作機械図鑑",
           "工作機械の干渉図・動作範囲図の読み方を図で解説。NC旋盤の最大振りと最大加工径、刃物台の旋回径、マシニングセンタの主軸端〜テーブル距離、ATC、5軸の干渉まで。ワークと工具が収まるかを計算できるツール付き。", mc_js)

# =====================================================================
# 3. physical AI
# =====================================================================
cat = collections.Counter()
for p in glob.glob("parts/*/index.html"):
    s = read(p)
    if "移動しました" in s[:3000]: continue
    for m in re.finditer(r'<article class="opx" id="op\d+">.*?<span class="kchip f\d"><i></i>([^<]*)</span>', s):
        cat[m.group(1)] += 1
total_ops = sum(cat.values())
RULES = [("段取り・取付け（人の手）", r"取付|芯出し|爪|治具|吊り|着座|段取|チャック|載せ|保持|準備|結線|組付|締め|支え|調整|裏返し"),
         ("計測・確認（人の目と判断）", r"測|確認|検査|点検|試し|振れ"),
         ("機械の手入れ", r"暖機|ドレッ|ドレス|清掃|バランス|水質|始業|終業|原点|試運転"),
         ("条件・プログラム", r"条件|プログラム|補正|設定|座標|シミュレーション|入力|パス|受け渡し"),
         ("機械が自動で削る・運転する", r"加工|研削|量産|運転|切")]
steps = [(k, a) for k, v in PRACTICE.items() for a, _ in v["use"]]
sc = collections.Counter(); sx = collections.defaultdict(list)
for k, a in steps:
    for name, rx in RULES:
        if re.search(rx, a): sc[name] += 1; sx[name].append(a); break
    else: sc["その他"] += 1; sx["その他"].append(a)
nsteps = len(steps)
human = sc[RULES[0][0]] + sc[RULES[1][0]]
def bars(items, total, hi=()):
    mx = max(v for _, v in items)
    return '<div class="bars">' + "".join(f'<div class="r{" hi" if k in hi else ""}"><span>{e(k)}</span><span class="b"><i style="width:{v / mx * 100:.1f}%"></i></span><span class="n">{v}<small>（{v / total * 100:.0f}%）</small></span></div>' for k, v in items) + "</div>"
GROUP = [("検査", ["検査"]), ("切削・研削・歯車", ["切削", "研削", "歯車"]), ("組立・接合・巻線・電子", ["組立", "接合", "巻線", "電子"]),
         ("鍛造・鋳造・プレス・成形・素材", ["鍛造", "鋳造", "プレス", "成形", "素材"]), ("熱処理・表面処理・塗装・化学", ["熱処理", "表面処理", "塗装", "化学"]), ("物流・保全", ["物流", "保全"])]
_top = cat.most_common(9)
gitems = _top + [("そのほか", total_ops - sum(v for _, v in _top))]
sitems = [(r[0], sc[r[0]]) for r in RULES] + ([("その他", sc["その他"])] if sc["その他"] else [])

ai_body = f'''
<p class="note"><b>この記事の立場</b>工作機械商社で量産ラインの設備検討に立ち会ってきた立場から、この図鑑に収めた1,232の工程と、18機種の作業手順のデータを使って書く。AIの未来予想ではなく、「現場のどこに、どの順番で入ってくるか」の見立てである。数字はこの図鑑の分類で数えたもので、世の中の工場の割合を表すものではない。</p>

<h2 id="a-what">フィジカルAIとは、工場にとって何か</h2>
<p>フィジカルAIは、カメラやセンサで現実の世界を認識し、ロボットや機械を動かして、物に対して直接仕事をするAIのことである。文章や画像をつくる生成AIが画面の中で完結するのに対し、フィジカルAIは「つかむ・置く・押す・削る」の結果が現物として残る。</p>
<p>工作機械の世界から見ると、ここには1つ大事な前提がある。<b>工作機械は、50年以上前からNC（数値制御）で「プログラムどおりに物を動かす」ことを実現してきた</b>。削る動作そのものは、すでに高い精度で自動化されている。だから工作機械にとってのAIの本当の出番は、削る動作よりも、その前後で人がやっている「見る・判断する・段取りする」の部分にある。次のデータが、それをはっきり示している。</p>

<h2 id="a-data1">データ1：工程の5つに1つは「検査」</h2>
<p>この図鑑に収めた{total_ops:,}の工程を、加工法の系統で分けた。いちばん多いのは切削でも組立でもなく、<b>検査（{cat["検査"]}工程、{cat["検査"] / total_ops * 100:.0f}%）</b>である。2位の切削（{cat["切削"]}工程）より多い。</p>
{bars(gitems, total_ops, hi=("検査",))}
<p>検査は、目で見て、測って、良し悪しを判断する仕事である。画像検査はAIがもっとも早く実用になった分野で、<a href="/parts/traction-motor-stator/">モーターのヘアピン溶接</a>の全数画像検査や、塗装面の欠陥検出は、すでに多くの量産ラインで使われている。一方で、<a href="/machine-tools/glossary/grinding-burn/">研削焼け</a>のように表面を見ても分からない不良や、大型歯車の<a href="/machine-tools/glossary/tooth-contact/">歯当たり</a>のように熟練者が総合的に判断するものは、まだ人の仕事として残っている。</p>

<h2 id="a-data2">データ2：機械を動かす手順の{human / nsteps * 100:.0f}%は、人の手と目</h2>
<p>この図鑑の工作機械18機種には、電源を入れてから量産に入るまでの「使い方の流れ」を、合計{nsteps}の手順で書いている。それぞれの手順を、作業の中身で5つに分けた。</p>
{bars(sitems, nsteps, hi=(RULES[0][0], RULES[1][0]))}
<p><b>「機械が自動で削る・運転する」手順は{sc[RULES[4][0]]}（{sc[RULES[4][0]] / nsteps * 100:.0f}%）しかない</b>。残りの大半は、ワークや工具を取り付け、芯を出し、測って確かめ、砥石を整える、人の手と目と判断の仕事である。量産ラインでは、この部分を専用の治具やローダで固めて自動化している。しかし多品種・少量の現場や、一品物の大物では、今もほとんどを人がやっている。</p>
<p class="note"><b>分け方</b>各手順の見出しに含まれる言葉で分けた。たとえば「取付・芯出し・爪・治具・吊り・着座」を含むものは段取り、「測・確認・検査・試し」は計測・確認、「暖機・ドレス・清掃・原点・試運転」は機械の手入れ。手順の一覧は各機種のページの「使い方の流れ」で確かめられる。</p>

<h2 id="a-layers">AIが入ってくる5つの層</h2>
<p>工作機械の周りでAIが働く場所を、現実に近い順に並べた。「すでに使われている」「数年で広がる」「まだ遠い」の見立ては、この図鑑の筆者の判断である。</p>
<ol class="layers">
<li><h3>見る：検査と計測</h3><p><span class="st now">すでに使われている</span>画像による外観検査、溶接の良否判定、寸法の自動計測。量産の全数検査から入り、効果が数字で見えやすい。</p><p>難しいのは、見えない不良（内部の欠陥、研削焼け、残留応力）と、合否の基準がはっきりしない官能的な判断。</p></li>
<li><h3>補正する：熱変位と摩耗</h3><p><span class="st now">すでに使われている</span>機械の温度や運転の履歴から、<a href="/machine-tools/components/thermal-displacement/">熱変位</a>を予測して補正する機能は、NCメーカーや工作機械メーカーが機械学習を使った機能として提供している。工具や砥石の摩耗の予測も同じ考え方である。</p><p>μm単位の精度を出す研削盤やジグ研削盤では、温度の管理そのものが品質を決めるため、効果が大きい。</p></li>
<li><h3>考える：加工条件とプログラム</h3><p><span class="st near">数年で広がる</span>びびりを検知して回転数を変える機能、CAMでの工具経路の自動生成、図面からNCプログラムの下書きをつくる生成AI。条件出しにかかっていた熟練者の時間を短くする。</p><p>ただし、「この条件で本当に削ってよいか」を最後に判断する人は必要である。<a href="/machine-tools/glossary/interference/">干渉</a>や研削焼けを起こしたときの損失が大きいからだ。</p></li>
<li><h3>動かす：段取りと搬送（フィジカルAIの本丸）</h3><p><span class="st near">数年で広がる</span>カメラでワークの位置と向きを認識してつかむロボット、バラ積みピッキング、ワークの自動計測と座標の自動設定。データ2で最も多かった「段取り・取付け」に直接効く。</p><p><span class="st far">まだ遠い</span>単動チャックでの芯出し、大物ワークの吊り込みとジャッキでの水平出し、締め付けひずみを見ながらの締め直し。力の加減と、ワークごとに違う判断が要る作業は、人の手が当分残る。</p></li>
<li><h3>伝える：技能の継承</h3><p><span class="st near">数年で広がる</span>作業標準・トラブル事例・機械の取扱説明書を学んだAIが、現場で「この不良の原因は何か」に答える。熟練者の退職で失われる知恵を残す手段として、もっとも期待が大きい。</p><p>この図鑑の<a href="/machine-tools/troubles/">トラブル事例集</a>や<a href="/machine-tools/glossary/">用語辞典</a>のように、知識が言葉と図で整理されていることが前提になる。</p></li></ol>

<h2 id="a-where">業界によって入り方は逆になる</h2>
{T(["", "自動車の量産", "舶用・発電・大型歯車などの一品物"], [
 ["AIが効く場所", "全数検査、条件の最適化、設備の故障予知。1%の改善が年間数十万個に効く", "段取りと計測の支援、技能の継承。1回の失敗を防ぐことに価値がある"],
 ["データ", "同じ部品のデータが大量に集まる", "1個ごとに条件が違い、データが少ない"],
 ["壁", "既存の専用ラインに後から入れる難しさ", "学習できるデータの少なさ。人の判断に頼る部分が大きい"],
 ["始めやすいこと", "画像検査、熱変位・摩耗の補正", "作業記録とトラブル記録をデータとして残すこと"]])}
<p>量産では「同じことを大量に繰り返す」ことがAIの学習に向いている。一品物では逆に、AIに学ばせるデータそのものが少ない。<a href="/parts/gear-large-one-off/">大型歯車</a>のように1個で数か月かかる品物は、AIで自動化するより、熟練者の判断を記録して次の人に渡すところから始めるのが現実的である。</p>

<h2 id="a-ask">「AI搭載」の機械を選ぶときに聞くべき10の質問</h2>
<p>最近は「AI搭載」をうたう工作機械や周辺機器が増えた。営業の立場から、お客様に代わってメーカーに確かめてほしいことをまとめた。</p>
<ol><li>そのAIは<b>何を入力にして、何を出力する</b>のか（温度→補正量、音→回転数の変更、など）。</li>
<li>学習済みのモデルを使うのか、<b>自社のデータで学習</b>するのか。学習に何個・何時間のデータが要るか。</li>
<li>AIが判断を誤ったとき、<b>機械はどう止まるか</b>。人が最後に確認する仕組みはあるか。</li>
<li>AIの機能を<b>切って</b>、従来どおり運転できるか。</li>
<li>効果は<b>どの条件で</b>測った数字か（ワーク・材質・環境温度）。自社のワークで試せるか。</li>
<li>集めたデータは<b>誰のもの</b>か。メーカーのクラウドに送られるか。</li>
<li>工場のネットワークにつなぐ場合の<b>セキュリティ</b>対策と、更新の方法。</li>
<li>AIの機能は<b>買い切り</b>か、年間の使用料が必要か。</li>
<li>機能の<b>更新（アップデート）</b>で動きが変わったとき、検収した条件は保証されるか。</li>
<li>使いこなすための<b>教育</b>と、社内に誰が必要か。</li></ol>

<h2 id="a-human">それでも人が要る理由</h2>
<p>この図鑑の各機種のページに書いた「知っておくべきこと」を読み返すと、その多くは「なぜそうなるか」を理解していないと防げない現象である。<a href="/machine-tools/glossary/dressing/">ドレッシング</a>の条件で砥石の性格が変わること。締め付けで薄いリングが楕円になること。センタレス研削で<a href="/machine-tools/glossary/lobing/">おむすび形</a>が生まれること。AIは条件と結果の関係を見つけるのは得意だが、初めて起きた不良の理由を物理で説明し、対策を決めて、その責任を持つのは人である。</p>
<p>だから工作機械とAIの関係は「人の仕事を置き換える」よりも、<b>人が、なぜそうなるかを考える時間を取り戻すための道具</b>と考えるのが、現場の実感に近い。段取りと検査の手間をAIとロボットが引き受け、人は原因と対策を考える。そこに向けて、まずは自分たちの工程と知恵を、言葉と図とデータで残しておくこと。それが、この図鑑をつくっている理由のひとつでもある。</p>
'''
cr = [("トップ", "/"), ("工作機械図鑑", "/machine-tools/"), ("フィジカルAIと工作機械", "/machine-tools/physical-ai/")]
ai_main = ('<main id="main"><div class="page">' + crumbs_html(cr) +
           '<section class="phero wrap"><p class="eyebrow" lang="en">ESSAY · PHYSICAL AI</p><h1 class="d2">フィジカルAIと工作機械</h1>'
           f'<p class="sub lead" style="margin:20px auto 0">工作機械は半世紀前から「プログラムどおりに動く」機械だった。だからAIの出番は、削る動作ではなくその前後にある。この図鑑の{total_ops:,}工程と{nsteps}の作業手順のデータから、AIとロボットが現場のどこに、どの順番で入ってくるかを読み解く。</p></section>'
           f'<section class="sec tight"><div class="wrap"><article class="prose gx">{ai_body}</article></div></section>'
           '<section class="sec tight paper"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">READ NEXT</p><h2 class="d3">あわせて読む</h2></div><div class="list">'
           '<a class="li" href="/machine-tools/troubles/"><span class="t">工作機械のトラブル事例集</span><span class="n" lang="en">TROUBLES</span></a>'
           '<a class="li" href="/machine-tools/automation/"><span class="t">自動化・周辺機器</span><span class="n" lang="en">AUTOMATION</span></a>'
           '<a class="li" href="/machine-tools/glossary/"><span class="t">工作機械 用語辞典</span><span class="n" lang="en">GLOSSARY</span></a>'
           '<a class="li" href="/map/"><span class="t">全工程マップ</span><span class="n" lang="en">MAP</span></a></div></div></section>'
           "</div>" + MFOOT + "</main>")
ai_page = page(TPL, "フィジカルAIと工作機械｜1,232工程のデータで読む、AIが現場に入る順番｜工作機械図鑑",
               f"フィジカルAIは工作機械の現場のどこに入るのか。製造工程図鑑の{total_ops:,}工程と工作機械18機種・{nsteps}の作業手順のデータから、検査・補正・条件・段取り・技能継承の5つの層と、量産と一品物の違い、AI搭載機を選ぶときの10の質問まで、工作機械商社の現場目線で解説。",
               "/machine-tools/physical-ai/", cr, ai_main).replace("</style>", CSS + "</style>", 1)
write("machine-tools/physical-ai/index.html", ai_page)

# =====================================================================
# 4. guideways compared
# =====================================================================
def gw_svg():
    def lab(x, y, t, cls="", anchor="middle"):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}"{" class=" + chr(34) + cls + chr(34) if cls else ""}>{t}</text>'
    ink = 'style="fill:var(--soft);stroke:var(--ink)"'; dark = 'style="fill:var(--ink2);stroke:var(--ink)"'
    oil = 'style="fill:#D9A441;opacity:.55"'; acc = 'style="fill:var(--mark)"'
    out = ['<svg viewBox="0 0 640 260" role="img" aria-label="すべり案内・転がり案内・静圧案内の断面の模式図">']
    # 1 sliding
    out += [f'<rect x="30" y="150" width="160" height="60" {ink}/>', f'<rect x="20" y="96" width="180" height="40" {ink}/>',
            f'<rect x="30" y="136" width="160" height="6" {acc}/>', f'<rect x="30" y="142" width="160" height="8" {oil}/>',
            lab(110, 120, "テーブル"), lab(110, 186, "ベッド"), lab(110, 236, "すべり案内"), lab(110, 252, "面で受ける・油膜と樹脂", "zl")]
    # 2 rolling
    out += [f'<rect x="250" y="176" width="140" height="34" {ink}/>', f'<rect x="290" y="150" width="60" height="26" {dark}/>',
            f'<rect x="270" y="112" width="100" height="34" {ink}/>', f'<rect x="230" y="78" width="180" height="34" {ink}/>']
    for cx in (282, 358):
        for cy in (156, 170):
            out.append(f'<circle cx="{cx}" cy="{cy}" r="6" style="fill:var(--bg);stroke:var(--ink)"/>')
    out += [lab(320, 100, "テーブル"), lab(320, 134, "ブロック"), lab(320, 198, "ベッド"), lab(320, 168, "レール", "zl"),
            lab(320, 236, "転がり案内（リニアガイド）"), lab(320, 252, "点・線で受ける・鋼球やころ", "zl")]
    # 3 hydrostatic
    out += [f'<rect x="460" y="150" width="160" height="60" {ink}/>', f'<rect x="450" y="96" width="180" height="40" {ink}/>',
            f'<rect x="460" y="136" width="160" height="14" {oil}/>', f'<rect x="500" y="136" width="30" height="6" {acc}/>', f'<rect x="550" y="136" width="30" height="6" {acc}/>',
            '<path d="M515 70 L515 96" style="stroke:var(--mark);stroke-width:2"/><path d="M509 88 L515 98 L521 88" style="fill:var(--mark)"/>',
            '<path d="M565 70 L565 96" style="stroke:var(--mark);stroke-width:2"/><path d="M559 88 L565 98 L571 88" style="fill:var(--mark)"/>',
            lab(540, 62, "圧力油を送り込む", "zl"), lab(540, 120, "テーブル"), lab(540, 186, "ベッド"), lab(540, 236, "静圧案内"), lab(540, 252, "油膜で浮かせる・接触しない", "zl")]
    out.append("</svg>")
    return "".join(out)

gw_body = f'''
<p class="note"><b>3行で</b>案内面は、テーブルや主軸頭を「まっすぐ」動かすための道。面で滑らせる<b>すべり案内</b>、鋼球やころを転がす<b>転がり案内（リニアガイド）</b>、油の膜で浮かせる<b>静圧案内</b>の3つがあり、重く削るか、速く動かすか、精度を極めるかで選び方が変わる。どれが優れているかではなく、何を削る機械かで決まる。</p>

<h2 id="g-kinds">3つの方式の仕組み</h2>
<figure><div class="lab">{gw_svg()}</div></figure>
<ul><li><b>すべり案内</b>：テーブルとベッドの面どうしを、油膜をはさんで滑らせる。相手面には樹脂（フッ素樹脂系のシート）を貼り、きさげ（手作業で面を薄く削り、油だまりと当たりをつくる仕上げ）で当たりを整えるのが一般的。広い面で力を受けるので、振動を吸収しやすい。</li>
<li><b>転がり案内（リニアガイド）</b>：レールの上を、鋼球（ボール）やころ（ローラ）を入れたブロックが転がって動く。摩擦が非常に小さく、速く・軽く動ける。部品として買えるので、組立が速く、交換もできる。</li>
<li><b>静圧案内</b>：ポンプで送った圧力油（または空気）の膜でテーブルを浮かせる。部品どうしが触れないので、摩耗がなく、動きが極めて滑らか。超精密な研削盤や大型の精密機に使う。</li></ul>

<h2 id="g-compare">比較表</h2>
{T(["項目", "すべり案内", "リニアガイド（ボール）", "リニアガイド（ローラ）", "静圧案内（油）"], [
 ["減衰性（振動の吸収）", "◎ 高い", "△ 低い", "○ 中", "◎ 高い"],
 ["剛性", "◎ 高い", "○", "◎ 高い", "◎ 高い"],
 ["摩擦（動きの軽さ）", "△ 大きい（0.05〜0.1前後）", "◎ 非常に小さい（0.005以下）", "◎ 非常に小さい", "◎ ほぼゼロ（油の粘性だけ）"],
 ["低速での滑らかさ", "△ スティックスリップが出やすい", "○", "○", "◎"],
 ["早送りの速さ", "△ 遅め", "◎ 速い", "○ 速い", "○"],
 ["位置決めの精度", "○", "◎", "◎", "◎"],
 ["摩耗と寿命", "○ 摩耗するが、きさげで直せる", "○ 寿命が計算できる。交換できる", "○ 同左", "◎ 摩耗しない"],
 ["保守", "給油量と当たりの管理", "給脂・ワイパーの管理。交換が早い", "同左", "油圧ユニット・油の清浄度・温度の管理"],
 ["コスト", "○（きさげに熟練の手間）", "◎ 安い・組立が速い", "○", "△ 高い（ユニット・配管が必要）"],
 ["向いている機械", "重切削の大型機、研削盤、旋盤のベッド", "高速のマシニングセンタ、小型機", "重切削もこなすマシニングセンタ・5軸", "超精密研削盤、大型の精密機"]])}
<p class="note"><b>読み方</b>◎○△は方式どうしの相対的な比較で、機種や設計で大きく変わる。摩擦係数は一般的な目安である。</p>

<h2 id="g-damping">なぜ「減衰」が大事なのか</h2>
<p>剛性が「押されてもたわまない強さ」なら、減衰は「揺れをすぐに止める力」である。重い切削や研削では、刃が当たるたびに機械が小さく揺れる。この揺れが止まらないと、<a href="/machine-tools/glossary/chatter/">びびり</a>として面に模様が残り、工具の寿命も縮む。すべり案内は広い面と油膜が揺れを吸収するため、昔から重切削機や研削盤に選ばれてきた。リニアガイドは剛性は高くても減衰が小さいため、重切削向けの機種ではローラ形を使ったり、減衰を補う部品を足したりする。</p>

<h2 id="g-choose">何で選ぶか</h2>
{T(["こんな機械なら", "向いている方式", "理由"], [
 ["鋳鉄や鋼を大きく削る大型機・門形", "すべり案内、ローラガイド", "重い切削の揺れを吸収し、剛性を保つ"],
 ["アルミや小物を速く削る量産のマシニングセンタ", "ボールのリニアガイド", "早送りが速く、サイクルタイムが短い"],
 ["μmの精度と滑らかな面がほしい研削盤", "すべり案内、静圧案内", "低速でも滑らかに動き、振動が少ない"],
 ["超精密加工機、大型の精密研削盤", "静圧案内", "接触せず、摩耗も引っかかりもない"]])}

<h2 id="g-maint">保全の現場で見るところ</h2>
<ul><li><b>潤滑</b>：すべり案内は摺動面油の給油量と、給油ポンプの作動を毎日確認する。リニアガイドは給脂（グリス）または集中給油の量と間隔。どちらも給油切れは焼付きと精度低下に直結する。</li>
<li><b>ワイパー（スクレーパ）とカバー</b>：切りくずやクーラントが案内面に入ると、傷や早い摩耗の原因になる。ワイパーのゴムの劣化と、テレスコピックカバーの変形を定期的に点検する。</li>
<li><b>ガタと当たり</b>：すべり案内は、ジブ（すき間を調整する板）の調整でガタを詰める。リニアガイドは予圧が抜けると精度が落ちるため、異音や振動の変化に注意する。</li>
<li><b>静圧案内</b>：油の清浄度（フィルタ）、油温、圧力の監視が要る。油が汚れると絞り（油の出口）が詰まり、浮上量が変わる。</li></ul>
<p class="note"><b>営業の現場から</b>カタログで「すべり案内」と「リニアガイド」はよく比べられるが、お客様にとって大事なのは方式の名前ではなく「自分のワークを、どの切込みで、どのくらいの速さで削るか」である。重切削の比率が高いのに早送りの速さだけで選ぶと、びびりと工具寿命で後悔しやすい。</p>
'''
guide_page("guideways", "案内面（すべり案内・リニアガイド・静圧案内）の比較", "COMPARE",
           "工作機械のテーブルや主軸頭を、まっすぐ正確に動かす案内面。すべり案内・リニアガイド（ボール・ローラ）・静圧案内の仕組み、剛性と減衰と速さの違い、機械による選び方、保全で見るところまでを比較する。",
           gw_body, "すべり案内とリニアガイドの違い｜静圧案内も含めた工作機械の案内面の比較｜工作機械図鑑",
           "工作機械の案内面（摺動面）を比較。すべり案内（樹脂貼り・きさげ）、リニアガイド（ボール・ローラ）、静圧案内の仕組みと、減衰性・剛性・摩擦・速さ・寿命・保守・コストの違い、機械の用途による選び方、保全の点検項目まで。")

# =====================================================================
# 5. coolant unit for grinding machines
# =====================================================================
def cl_svg():
    box = lambda x, y, w, h, t, sub="": (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" style="fill:var(--soft);stroke:var(--ink)"/>'
                                          f'<text x="{x + w / 2}" y="{y + h / 2 + (-2 if sub else 4)}" text-anchor="middle">{t}</text>'
                                          + (f'<text x="{x + w / 2}" y="{y + h / 2 + 14}" text-anchor="middle" class="zl">{sub}</text>' if sub else ""))
    arr = lambda x1, y1, x2, y2, c="var(--accent)": (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="stroke:{c};stroke-width:2"/>'
                                                   f'<circle cx="{x2}" cy="{y2}" r="3.5" style="fill:{c}"/>')
    out = ['<svg viewBox="0 0 640 300" role="img" aria-label="研削盤のクーラントユニットの流れの模式図">',
           box(20, 30, 130, 56, "研削盤", "砥石・ワーク"), box(190, 30, 120, 56, "汚液槽", "戻った液"), box(350, 30, 130, 56, "マグネット", "セパレータ"),
           box(510, 30, 110, 56, "ペーパー", "フィルタ"), box(20, 200, 130, 56, "ノズル", "流量・流速"), box(190, 200, 120, 56, "ポンプ", ""),
           box(350, 200, 130, 56, "クーラ", "液温を一定に"), box(510, 200, 110, 56, "清浄槽", ""),
           arr(150, 58, 186, 58, "var(--mark)"), arr(310, 58, 346, 58, "var(--mark)"), arr(480, 58, 506, 58, "var(--mark)"),
           arr(565, 86, 565, 196), arr(510, 228, 484, 228), arr(350, 228, 314, 228), arr(190, 228, 154, 228), arr(85, 200, 85, 90),
           '<text x="415" y="118" text-anchor="middle" class="zl">鉄粉を磁石で取る</text><text x="565" y="118" text-anchor="middle" class="zl">細かい砥粒をこす</text>',
           '<text x="575" y="156" class="zl">きれいな液</text>',
           '<text x="300" y="290" text-anchor="middle" class="zl">朱色：汚れた液の流れ　青：きれいな液の流れ（構成は一例）</text></svg>']
    return "".join(out)

cl_body = f'''
<p class="note"><b>3行で</b>研削盤の品質は、砥石と同じくらいクーラントで決まる。役目は冷やす・滑らせる・削りかすを流す・砥石の目詰まりを防ぐの4つ。そのために、削りかすを取り除くろ過と、液の温度を一定に保つ温度管理と、砥石にきちんと届けるノズルの3つが要になる。</p>

<h2 id="c-role">クーラントの4つの役目</h2>
{T(["役目", "うまくいかないと"], [
 ["冷やす（研削点と工作物）", "<a href=\"/machine-tools/glossary/grinding-burn/\">研削焼け</a>、熱で寸法が変わる"],
 ["滑らせる（摩擦を減らす）", "砥石の摩耗が早い、面が荒れる"],
 ["削りかすを流す", "削りかすが面をこすって傷（スクラッチ）が付く"],
 ["砥石の目詰まりを防ぐ", "<a href=\"/machine-tools/glossary/loading/\">目詰まり</a>で切れ味が落ち、焼けやびびりが出る"]])}

<h2 id="c-flow">クーラントユニットの構成</h2>
<figure><div class="lab">{cl_svg()}</div></figure>
<p>研削盤から戻った汚れた液は、いったん汚液槽にたまり、ろ過で削りかすと砥粒を取り除かれて清浄槽に入る。そこからクーラで温度を整えられてから、ポンプでノズルへ送られる。研削の削りかすは非常に細かいため、ろ過の方式を組み合わせて使うのが一般的である。</p>

<h2 id="c-filter">ろ過の方式</h2>
{T(["方式", "仕組み", "得意なもの", "注意点"], [
 ["マグネットセパレータ", "回転する磁石のドラムで鉄の削りかすを吸い寄せて取る", "鋼・鋳鉄の研削の1段目", "砥粒やアルミなど磁石に付かないものは取れない"],
 ["ペーパーフィルタ（ロールペーパー）", "紙のろ材で液をこす。目詰まりしたら紙を送る", "細かい砥粒まで取りたいとき", "紙の消費量（ランニングコスト）"],
 ["サイクロン", "渦を巻かせて、重い粒を遠心力で分ける", "比較的重く粒のそろった削りかす", "細かく軽い粒は取りきれない"],
 ["プリコートフィルタ", "ろ材の表面に粉の層をつくって、とても細かくこす", "高い面品質が要る研削、不水溶性の油", "装置が大きく、粉の管理が必要"],
 ["遠心分離機", "高速回転で微粒子を分ける", "スラッジを減らしたい、液を長持ちさせたい", "処理量に対して装置が高価"],
 ["沈殿槽", "時間をかけて重い粒を沈める", "大容量の集中ろ過の1段目", "場所をとる。細かい粒は沈みにくい"]])}
<p>ろ過の細かさ（何μmの粒まで取るか）は、要求する面粗さで決める。仕上げ面にスクラッチ（細い傷）が出るときは、まずろ過を疑う。</p>

<h2 id="c-temp">温度管理：寸法が合わない原因の多く</h2>
<p>クーラントは工作物と機械に直接かかり続けるため、液温の変化はそのまま<a href="/machine-tools/components/thermal-displacement/">熱変位</a>になる。朝と昼で寸法がずれる、季節で補正量が変わる、といった現象の多くは液温が原因である。μm単位の研削では、クーラ（冷凍機）で液温を室温に近い一定の温度に保つ。タンクの容量が小さいと、研削の熱ですぐに液温が上がるため、容量にも余裕を持たせる。</p>

<h2 id="c-nozzle">ノズル：届かなければ意味がない</h2>
<ul><li>高速で回る砥石の周りには空気の層ができ、クーラントがはじかれて研削点に届かないことがある。液の速さを砥石の周速に近づける、空気の層を断ち切る板（スクレーパ）を付ける、などで届けやすくする。</li>
<li>流量だけ増やしても、向きが悪いと冷えない。ノズルの位置と向きは、砥石を交換して径が変わったら調整し直す。</li>
<li>目詰まりしやすい砥石には、別の高圧ノズルで砥石の表面を洗う方法もある。</li></ul>

<h2 id="c-fluid">液の種類と管理</h2>
{T(["種類", "特徴", "主な用途"], [
 ["水溶性（ソリューブル・ケミカル・エマルション）", "冷却性が高く、火災の危険がない。濃度と腐敗の管理が必要", "円筒研削、平面研削、センタレス研削の多く"],
 ["不水溶性（研削油）", "潤滑性が高く、面がよい。ミストと火災への対策が必要", "歯車研削、ねじ研削、CBN砥石の高能率研削"]])}
<ul><li><b>濃度</b>：水溶性は屈折計で濃度を測り、薄まったら原液を足す。薄いとさび、濃いと泡と皮膚のかぶれの原因になる。</li>
<li><b>腐敗</b>：においとpHの変化が目安。休日明けに臭うなら、液の循環や浮き油（摺動面油の混入）を疑う。</li>
<li><b>ミストと火災</b>：不水溶性の油を使う機械は、ミストコレクタと消火設備を備え、機械の周りの清掃を徹底する。</li>
<li><b>スラッジの処理</b>：取り除いた削りかすと砥粒（スラッジ）は産業廃棄物として処理する。量と処理費も運用費に入れる。</li></ul>

<h2 id="c-trouble">よくあるトラブルと原因</h2>
{T(["症状", "まず疑うこと"], [
 ["仕上げ面に細い傷（スクラッチ）", "ろ過の不足、フィルタの破れ、タンクの底のスラッジの巻き上げ"],
 ["研削焼け", "流量・向きの不足、砥石の目詰まり、液の濃度"],
 ["寸法が時間や季節でずれる", "液温の変化、クーラの能力不足、タンク容量"],
 ["泡があふれる", "濃度が高すぎる、ポンプの空気の吸い込み、戻りの落差"],
 ["さびが出る", "濃度が低い、液の腐敗"],
 ["においが出る、皮膚がかぶれる", "液の腐敗、浮き油の混入、濃度の管理不足"]])}

<h2 id="c-spec">導入の打ち合わせで決めること</h2>
<ul><li>液の種類（水溶性か不水溶性か）と、メーカーが推奨する液。</li>
<li>ろ過の方式と細かさ。要求する面粗さと、1日に出るスラッジの量から決める。</li>
<li>タンクの容量と、液温の制御幅（クーラの能力）。</li>
<li>単独のユニットか、複数台をまとめる集中ろ過か。</li>
<li>ミストコレクタ・消火設備の要否、設置スペースと保守の動線（紙の交換、スラッジの取り出し）。</li>
<li>ランニングコスト（ろ材、液の補充、廃液とスラッジの処理費、電気代）。</li></ul>
<p class="note"><b>営業の現場から</b>研削盤の見積りでは、本体に目が行き、クーラントユニットは「付属品」扱いされがちである。しかし立上げ後の面粗さや寸法の不安定の相談は、ろ過と液温が原因のことが本当に多い。本体と同じ熱量で、ユニットの仕様を詰めておきたい。</p>
'''
guide_page("grinding-coolant", "研削盤のクーラントユニット", "GRINDING",
           "研削盤の仕上がりは、砥石と同じくらいクーラントで決まる。ろ過・温度管理・ノズルの3つを中心に、クーラントユニットの構成、ろ過方式の比較、液の管理、よくあるトラブル、導入の打ち合わせで決めることまでをまとめる。",
           cl_body, "研削盤のクーラントユニット｜ろ過方式・液温管理・ノズル・液の管理とトラブル｜工作機械図鑑",
           "研削盤のクーラントユニットを解説。4つの役目、マグネットセパレータ・ペーパーフィルタ・サイクロン・プリコートフィルタなどのろ過方式の比較、液温管理と熱変位、ノズル、水溶性と不水溶性、濃度・腐敗の管理、トラブルと原因、導入時の打ち合わせ項目まで。")

# =====================================================================
# 6. what big-customer maintenance teams check, and run-off findings
# =====================================================================
STD = [
 ("電気・制御", [
  "制御盤の構成：盤内の余裕スペース（増設用に2〜3割など）、予備の端子、盤内温度の管理（盤用クーラ）、保護等級。",
  "指定メーカー：PLC・NC・サーボ・インバータ・センサ・安全機器のメーカーと型式が指定されている。保全部隊が持つ予備品と、使い慣れた機器にそろえるため。",
  "ラダー（シーケンス）の書き方：コメント、デバイスの番号の割り振り、異常処理の書き方のルール。保全員が自分で追えることが目的。",
  "配線：電線の色・太さ、線番号の表示、端子への圧着の方法、ダクトの使い方、可動部のケーブルの曲げ半径。",
  "ネットワークと信号：上位システムへ出す稼働・停止・異常の信号、フィールドネットワークの種類。",
  "アラーム：日本語のメッセージ、アラーム番号の体系、原因と復帰の手順が画面で分かること。"]),
 ("機械・ユーティリティ", [
  "指定部品：シリンダ、電磁弁、軸受、ボールねじ、リニアガイド、継手などの指定メーカー。社内の共通予備品で直せるようにするため。",
  "潤滑：集中給油の方式、給油口の位置（前面から給油できるか）、油の種類の統一と表示。",
  "油圧・エア：油圧ユニットのタンク容量・油温・フィルタの目詰まり表示、エアの3点セット（フィルタ・レギュレータ・ルブリケータ）と圧力計、残圧を抜く弁。",
  "配管：配管の色分けと流れの向きの表示、継手の種類、油漏れを受けるパン。",
  "塗装と表示：機械の塗装色の指定、銘板、注意ラベル、給油・点検箇所の表示。"]),
 ("保全性", [
  "点検のしやすさ：給油口・フィルタ・圧力計・油面計が、カバーを外さずに前から見えるか。",
  "交換のしやすさ：消耗品（ワイパー、ベルト、フィルタ、センサ）が、決めた時間内に交換できるか。カバーは工具なしで開くか、重さは一人で扱えるか。",
  "故障の診断：入出力の状態、軸の負荷、アラームの履歴が画面で見られるか。",
  "予備品：推奨予備品のリスト、入手までの期間、生産中止の予定。",
  "書類：取扱説明書、保全マニュアル、電気図面、部品表、ラダーのデータ。紙と電子データの両方、形式の指定。"]),
 ("安全", [
  "リスクアセスメント：機械の危険源の洗い出しと対策の記録（ISO 12100の考え方）。",
  "ガードとインターロック：扉を開けたら止まること、無効にできない構造であること。",
  "非常停止：押しボタンの位置と数、止まり方、復帰の方法。",
  "エネルギーの遮断：保全で入るときに、電気・油圧・エア・重力（落ちてくる部分）を遮断して施錠できる場所と表示（ロックアウト）。",
  "環境：騒音の上限、ミスト・粉じんの対策、油の飛散。"]),
]
FIND = [
 ("油漏れ・にじみ", "配管の継手、油圧ユニット、カバーのすき間からのにじみ", "工場内の床と品質を汚し、火災や転倒の原因になる", "出荷前の連続運転後に、白い紙で継手を一つずつ確認する"),
 ("配線の固定・保護", "ケーブルの固定不足、保護チューブなし、可動部の曲げが急", "断線と誤作動。止まると原因を探しにくい", "可動部を全ストローク動かしてケーブルの動きを見る"),
 ("盤内の清掃", "盤の中に切りくず・ビス・結束バンドの切れ端", "短絡や接触不良。大手ほど厳しく見る", "盤の扉を閉める前に、底面まで清掃し写真で残す"),
 ("表示・ラベル", "銘板、配管の流れの向き、給油箇所、注意ラベルの不足", "保全員が迷う、間違える", "設備規格の表示の項目を一覧にして、出荷前にチェックする"),
 ("アラームの分かりにくさ", "英語や略語のメッセージ、復帰の手順が分からない", "夜勤の作業者が復帰できず、ラインが長く止まる", "全アラームの一覧と復帰手順を事前に客先に確認してもらう"),
 ("安全機能", "扉を開けても動く、インターロックが簡単に無効にできる", "重大な事故につながる。最も厳しく指摘される", "インターロックと非常停止を、全数その場で実演する"),
 ("点検・給油のしにくさ", "給油口が奥、油面計が見えない、カバーが重い", "日常点検が省かれ、故障につながる", "設計審査の段階で、保全員に実物大の配置を見てもらう"),
 ("精度検査成績書", "測定条件（温度・測定器・方法）が書かれていない", "受入れ時の再検査で値が合わない", "規格名、測定器、室温を成績書に必ず書く"),
 ("能力の未達", "サイクルタイム、工程能力（Cpk）、可動率が約束に届かない", "検収が延び、支払いも遅れる", "合格基準と測り方を契約時に数値で決めておく"),
 ("指定外の部品", "設備規格で指定されていないメーカーの部品が使われている", "保全部隊の予備品で直せない", "部品表を規格の指定リストと照合してから手配する"),
 ("切りくず・クーラント", "切りくずが機械の中にたまる、クーラントが外に飛ぶ", "清掃の手間と火災・転倒の危険", "実際のワークと条件で長めに連続運転して確認する"),
 ("書類の不足", "図面・ラダー・予備品リストが未提出、版が古い", "保全ができない、改造の履歴が分からない", "提出書類の一覧と期日を、発注時に合意する")]

std_html = "".join(f"<h3>{e(t)}</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>" for t, items in STD)
find_rows = [[f"<b>{e(a)}</b>", e(b), e(c), e(d)] for a, b, c, d in FIND]
checklist = '<div class="lab ck" id="ck"><p class="ckh"><b>立会いチェックリスト</b><span id="ckn"></span><button type="button" class="ckb" onclick="window.print()">印刷する</button></p>' + "".join(
    f'<label><input type="checkbox" data-k="{i}"><span>{e(a)}：{e(d)}</span></label>' for i, (a, b, c, d) in enumerate(FIND)) + "</div>"
ck_css = (".ck label{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--hair);font-size:14.5px;line-height:1.7;cursor:pointer}"
          ".ck input{width:20px;height:20px;margin-top:3px;accent-color:var(--mark);flex:none}.ck input:checked+span{color:var(--muted);text-decoration:line-through}"
          ".ckh{display:flex;align-items:center;gap:14px;margin:0 0 6px}.ckh span{font:400 13px var(--f-en);color:var(--muted)}"
          ".ckb{margin-left:auto;height:36px;padding:0 16px;border-radius:999px;border:1px solid var(--hair);font-size:13px}.ckb:hover{border-color:var(--ink)}"
          "@media print{.gn,.foot,.crumbs,.phero,.glback,.rd,.ov,.sec.paper,.ckb{display:none!important}.gx>*:not(#ck):not(#m-check){display:none}.ck{box-shadow:none}}")
ck_js = ("<script>(function(){var K='mt-runoff-check',box=document.getElementById('ck');if(!box)return;var s={};try{s=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}"
         "var cb=box.querySelectorAll('input');function cnt(){var n=0;cb.forEach(function(c){if(c.checked)n++});document.getElementById('ckn').textContent=n+' / '+cb.length}"
         "cb.forEach(function(c){c.checked=!!s[c.dataset.k];c.addEventListener('change',function(){s[c.dataset.k]=c.checked;try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}cnt()})});cnt()})();</script>")

mt_body = f'''
<p class="note"><b>この記事について</b>自動車部品メーカーなど大手の客先は、設備を買うときに自社の「設備仕様書」「設備規格」（呼び方は会社ごとに違う）を機械メーカーに渡し、それに沿ってつくることを求める。中身は各社の社外秘で、会社によって大きく違う。ここでは、工作機械商社の営業として立ち会ってきた経験から、多くの会社に共通する傾向をまとめた。特定の会社の規格を紹介するものではない。</p>

<h2 id="m-why">なぜ保全部隊は細かく指定するのか</h2>
<p>保全部隊の仕事は、工場の設備を止めないこと、止まったら最短で直すことである。工場には何百台もの設備があり、メーカーも年式もばらばらだと、予備品も知識も揃えきれない。だから<b>「うちの保全員が、うちの予備品で、夜中でも直せる設備」</b>にするために、部品のメーカー、配線の色、ラダーの書き方、表示まで指定する。設備規格は、過去の故障やトラブルの経験が積み重なってできた「再発防止の集大成」でもある。</p>
<p>機械メーカーや商社から見ると細かく面倒に見えるが、この背景を理解すると、指摘の意図が読めるようになり、打ち合わせが速く進む。</p>

<h2 id="m-std">設備規格によく載っている項目</h2>
{std_html}

<h2 id="m-flow">立会いの流れ</h2>
{T(["段階", "どこで", "主に確かめること"], [
 ["設計審査（デザインレビュー）", "発注後、製作前", "配置図・電気図・ラダーの方針が規格に合っているか、保全の動線"],
 ["メーカーでの完成立会い（一次立会い）", "機械メーカーの工場", "動作、安全機能、精度、試し加工、規格の項目、外観"],
 ["据付け後の立会い（二次立会い）", "客先の工場", "据付け後の精度、実際のワークでの連続運転、サイクルタイム、工程能力"],
 ["検収", "客先", "指摘事項がすべて直り、書類がそろったことの確認"]])}

<h2 id="m-find">完成立会いでよくある指摘事項</h2>
{T(["指摘", "具体的には", "なぜ問題か", "防ぎ方"], find_rows)}

<h2 id="m-check">立会い前のチェックリスト</h2>
<p>上の指摘を、出荷前の自主点検用のチェックリストにした。チェックはこの端末に保存され、印刷もできる。</p>
{checklist}

<h2 id="m-tips">商社・メーカーの立場から、うまく進めるコツ</h2>
<ul><li><b>見積りの前に設備規格を入手する</b>：規格の版と、例外を認めてもらえる範囲を確認し、規格に合わせるための費用を見積りに入れる。後から「規格どおりに」と言われると、改造費が持ち出しになる。</li>
<li><b>規格との違いは一覧にして先に合意する</b>：メーカーの標準仕様と規格が違う所を表にし、どちらに合わせるかを設計審査で決める。</li>
<li><b>保全部隊を早く巻き込む</b>：設計審査に生産技術だけでなく保全の担当者を呼ぶ。立会いで初めて保全の人が機械を見ると、指摘が一気に増える。</li>
<li><b>指摘はその場で記録し、期日と担当を決める</b>：立会いの最後に、指摘の一覧を客先と一緒に確認して、直す期日と方法を合意する。</li></ul>
<p>あわせて、各機種のページの<a href="/machine-tools/cnc-lathe/#qa">想定問答</a>には、仕様の打ち合わせでお客様から聞かれる質問と答え方をまとめている。</p>
'''
guide_page("maintenance-standards", "保全部隊が見るところと完成立会いの指摘事項", "PRACTICE",
           "大手の客先は、自社の設備規格に沿って設備をつくることを求める。保全部隊がなぜ細かく指定するのか、設備規格によく載る項目、立会いの流れ、完成立会いでよくある指摘事項と防ぎ方、出荷前のチェックリストまでを、工作機械商社の現場目線でまとめる。",
           mt_body, "設備規格と完成立会いの指摘事項｜大手客先の保全部隊が見るところ｜工作機械図鑑",
           "大手客先の保全部隊が設備規格（設備仕様書）で重視する項目を、電気・制御、機械・ユーティリティ、保全性、安全に分けて解説。完成立会いでよくある指摘事項と理由・防ぎ方、立会いの流れ、出荷前のチェックリスト付き。工作機械商社の現場目線で。", ck_js)
_mp = "machine-tools/guide/maintenance-standards/index.html"
write(_mp, read(_mp).replace("</style>", ck_css + "</style>", 1))

# related links from existing pages
for slug in ["components/slideway", "components/linear-guide", "components/coolant"]:
    p = f"machine-tools/{slug}/index.html"
    if not os.path.exists(p): continue
    s = read(p)
    lk = (f'<p><a href="{G}guideways/">案内面（すべり案内・リニアガイド・静圧案内）の比較を読む</a></p>' if "coolant" not in slug
          else f'<p><a href="{G}grinding-coolant/">研削盤のクーラントユニット（ろ過・液温・ノズル）を読む</a></p>')
    s = s.replace("</article>", lk + "</article>", 1)
    write(p, s)
for slug in ["cylindrical-grinder", "internal-grinder", "surface-grinder", "centerless-grinder", "gear-grinding-machine"]:
    p = f"machine-tools/{slug}/index.html"; s = read(p)
    tip = f'<p class="tal" style="margin-top:18px;font-size:14px">研削の仕上がりを左右する：<a href="{G}grinding-coolant/">研削盤のクーラントユニット</a></p>'
    s = s.replace('<div class="pspec" role="table"', tip + '<div class="pspec" role="table"', 1)
    write(p, s)
for p in glob.glob("machine-tools/*/index.html"):
    s = read(p)
    if '<p class="qsub">どの機械でも聞かれること</p>' in s:
        s = s.replace('<p class="qsub">どの機械でも聞かれること</p>',
                      f'<p class="qsub">どの機械でも聞かれること</p><p style="font-size:14px;margin:0 0 10px">大手客先の設備規格と立会いの指摘事項は<a href="{G}maintenance-standards/">こちらにまとめた</a>。</p>', 1)
        write(p, s)

# =====================================================================
# links: guide index, machine-tools hub, machine pages, sitemap, search
# =====================================================================
gi = read("machine-tools/guide/index.html")
add = "".join(f'<a class="li" href="{G}{s}/"><span class="t">{e(t)}</span><span class="n" lang="en">{ey}</span></a>' for s, t, ey in NEW)
add += '<a class="li" href="/machine-tools/physical-ai/"><span class="t">フィジカルAIと工作機械</span><span class="n" lang="en">ESSAY</span></a>'
gi = gi.replace('<span class="t">工作機械の精度の見方</span><span class="n" lang="en">COMPARE</span></a></div>', '<span class="t">工作機械の精度の見方</span><span class="n" lang="en">COMPARE</span></a>' + add + "</div>", 1)
write("machine-tools/guide/index.html", gi)
hub = read("machine-tools/index.html")
hub = hub.replace('<a class="lnk" href="/machine-tools/glossary/">用語辞典</a></p>', '<a class="lnk" href="/machine-tools/glossary/">用語辞典</a><a class="lnk" href="/machine-tools/physical-ai/">フィジカルAIと工作機械</a></p>', 1)
hub = hub.replace('<b class="tn">6</b><span>選び方ガイド</span>', f'<b class="tn">{6 + len(NEW)}</b><span>選び方ガイド</span>')
write("machine-tools/index.html", hub)
SPINDLE = ["cnc-lathe", "vertical-machining-center", "horizontal-machining-center", "5-axis-machining-center", "double-column-machining-center", "turn-mill", "vertical-turning-lathe", "swiss-type-lathe"]
for slug in SPINDLE:
    p = f"machine-tools/{slug}/index.html"; s = read(p)
    tip = ('<p class="tal" style="margin-top:18px;font-size:14px">カタログの線図の読み方：'
           f'<a href="{G}spindle-torque-chart/">主軸のトルク線図の見方</a>／<a href="{G}interference-diagram/">干渉図・動作範囲図の見方</a></p>')
    s = s.replace('<div class="pspec" role="table"', tip + '<div class="pspec" role="table"', 1)
    write(p, s)
P.add_urls("sitemap-machine-tools.xml", [f"{G}{s}/" for s, _, _ in NEW] + ["/machine-tools/physical-ai/"])
si_old = glob.glob("assets/search.*.json")[0]
d = json.load(open(si_old, encoding="utf-8"))
d["m"] += [[t, "ガイド", f"{G}{s}/"] for s, t, _ in NEW] + [["フィジカルAIと工作機械", "ガイド", "/machine-tools/physical-ai/"]]
import hashlib
sj = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
si_new = f"assets/search.{hashlib.sha1(sj.encode()).hexdigest()[:10]}.json"
write(si_new, sj)
if si_new != si_old:
    os.remove(si_old)
    for p in glob.glob("**/*.html", recursive=True):
        s = read(p)
        if si_old in s: write(p, s.replace("/" + si_old, "/" + si_new))
ex = open(f"{S}/extra_chars.txt", encoding="utf-8").read()
open(f"{S}/extra_chars.txt", "w", encoding="utf-8").write("".join(sorted(set(ex) | set("主軸のトルク線図の見方干渉図・動作範囲図フィジカルAIと工作機械ほかのガイドあわせて読む" + "".join(re.findall(r"<h[23][^>]*>([^<]*)</h[23]>", tq_body + if_body + ai_body + gw_body + cl_body + mt_body)) + "".join(t for _, t, _ in NEW)))))
print("guides ok | ops", total_ops, "steps", nsteps, dict(sc))
