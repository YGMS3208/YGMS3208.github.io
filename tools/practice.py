#!/usr/bin/env python3
"""Insert the 'in practice' section (spec meeting / how to use / what to know) into each machine page. Idempotent."""
import html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from practice_data import DATA
from qa_data import QA, COMMON

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = ("/*prac*/.prac .hd{margin-bottom:clamp(28px,4vw,48px)}"
".pjump{display:flex;flex-wrap:wrap;gap:8px 28px;margin-top:6px}"
".pjump a{display:inline-flex;align-items:baseline;gap:10px;font-size:15px;color:var(--ink);border-bottom:1px solid var(--hair);padding:6px 0;transition:border-color .3s,color .3s}"
".pjump a b{font:400 13px var(--f-en);color:var(--mark);letter-spacing:.06em}"
".pjump a:hover{color:var(--mark);border-color:var(--mark)}"
".pblk{scroll-margin-top:calc(var(--gn) + 20px);border-top:1px solid var(--ink);padding-top:clamp(24px,3vw,36px);margin-top:clamp(56px,7vw,96px)}"
".pblk:first-of-type{margin-top:0}"
".pblk>header{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr);gap:12px clamp(24px,4vw,64px);margin-bottom:clamp(24px,3vw,40px)}"
".pblk>header h3{font:600 clamp(24px,2.6vw,34px)/1.4 var(--f-disp);letter-spacing:.04em;display:flex;gap:16px;align-items:baseline}"
".pblk>header h3 span{font:300 .7em var(--f-en);color:var(--mark);letter-spacing:.06em}"
".pblk>header p{font-size:15.5px;line-height:1.95;color:var(--ink2)}"
".pspec{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.6fr) minmax(0,1.3fr);border-bottom:1px solid var(--hair)}"
".pspec>*{padding:16px 20px 16px 0;border-top:1px solid var(--hair);font-size:14.5px;line-height:1.85;color:var(--ink2)}"
".pspec .h{font:500 11px var(--f-en);letter-spacing:.24em;color:var(--muted);border-top:0;padding-top:0}"
".pspec b{color:var(--ink);font-size:15px}"
".pspec .m{color:var(--muted);font-size:13.5px}"
".psteps{counter-reset:st;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:0 clamp(20px,3vw,40px)}"
".psteps li{counter-increment:st;position:relative;padding:18px 0 22px 52px;border-top:1px solid var(--hair)}"
".psteps li::before{content:counter(st,decimal-leading-zero);position:absolute;left:0;top:18px;font:300 22px/1.2 var(--f-en);color:var(--mark)}"
".psteps b{display:block;font-size:16px;color:var(--ink);margin-bottom:4px}"
".psteps p{font-size:14px;line-height:1.85;color:var(--ink2)}"
".pknow{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:clamp(12px,2vw,20px)}"
".pknow .k{background:var(--paper);border-radius:4px;box-shadow:0 0 0 1px var(--hair2);padding:clamp(22px,2.6vw,32px)}"
".pknow .k.wide{grid-column:1/-1}"
".pknow h4{font:600 19px/1.5 var(--f-disp);letter-spacing:.04em;color:var(--ink);margin-bottom:10px;display:flex;gap:12px;align-items:baseline}"
".pknow h4::before{content:\"\";flex:none;width:8px;height:8px;border-radius:50%;background:var(--mark);transform:translateY(-.15em)}"
".pknow p{font-size:14.5px;line-height:1.95;color:var(--ink2)}.pknow p+p{margin-top:.8em}"
".qas{border-top:1px solid var(--hair)}"
".qa{border-bottom:1px solid var(--hair)}"
".qa summary{list-style:none;display:grid;grid-template-columns:28px minmax(0,1fr) 20px;gap:14px;align-items:baseline;padding:20px 0;cursor:pointer;font-size:16px;line-height:1.7;color:var(--ink);font-weight:500}"
".qa summary::-webkit-details-marker{display:none}"
".qa summary::after{content:\"\";width:9px;height:9px;border-right:1.5px solid var(--muted);border-bottom:1.5px solid var(--muted);transform:rotate(45deg);justify-self:end;transition:transform .3s var(--ease)}"
".qa[open] summary::after{transform:rotate(-135deg) translate(-3px,-3px)}"
".qa summary:hover .qt{color:var(--mark)}"
".qm{font:500 18px/1.4 var(--f-en);color:var(--mark)}"
".qb{padding:0 0 24px 42px}"
".qa1{display:grid;grid-template-columns:28px minmax(0,1fr);gap:14px;margin-left:-42px;font-size:15px;line-height:1.95;color:var(--ink2)}"
".qa1 .qm{color:var(--accent)}"
".qp{margin-top:14px;padding:14px 18px;background:var(--bg);border-left:2px solid var(--mark);border-radius:0 4px 4px 0;font-size:13.5px;line-height:1.9;color:var(--ink2)}"
".qp b{display:block;font-size:12px;letter-spacing:.12em;color:var(--mark);font-weight:500;margin-bottom:2px}"
".qsub{margin:36px 0 10px;font:500 12px var(--f-en);letter-spacing:.2em;color:var(--muted)}"
"@media (max-width:760px){.pblk>header{grid-template-columns:1fr}.qb{padding-left:0}.qa1{margin-left:0}"
".pspec{grid-template-columns:1fr}.pspec .h{display:none}"
".pspec>*{border-top:0;padding:0 0 4px}.pspec>b{border-top:1px solid var(--hair);padding-top:16px}"
".pspec>.m{padding-bottom:16px}.pspec>.m::before{content:\"用意する情報：\";color:var(--ink2)}}")

def e(s): return html.escape(s, quote=False)

def qa_block(slug):
    def item(q, a, pt, i):
        return (f'<details class="qa"{" open" if i == 0 else ""}><summary><span class="qm" lang="en">Q</span><span class="qt">{e(q)}</span></summary>'
                f'<div class="qb"><p class="qa1"><span class="qm" lang="en">A</span><span>{e(a)}</span></p>'
                f'<p class="qp"><b>確認のポイント</b>{e(pt)}</p></div></details>')
    own = "".join(item(*x, i) for i, x in enumerate(QA[slug]))
    com = "".join(item(*x, 1) for x in COMMON)
    return ('<div class="pblk" id="qa"><header><h3><span lang="en">04</span>想定問答</h3>'
            '<p>仕様の打ち合わせで、お客様から実際によく聞かれる質問と、その答え方の例。数値をその場で約束せず、条件を確かめてから根拠とともに答えるのが基本である。</p></header>'
            f'<div class="qas">{own}</div><p class="qsub">どの機械でも聞かれること</p><div class="qas">{com}</div></div>')

def section(name, d, slug=None):
    spec = ('<div class="pspec" role="table" aria-label="仕様の打ち合わせ項目">'
            '<span class="h" role="columnheader" lang="en">ITEM</span><span class="h" role="columnheader" lang="en">DECIDE</span><span class="h" role="columnheader" lang="en">PREPARE</span>'
            + "".join(f'<b role="cell">{e(a)}</b><span role="cell">{e(b)}</span><span class="m" role="cell">{e(c)}</span>' for a, b, c in d["spec"]) + '</div>')
    steps = '<ol class="psteps">' + "".join(f'<li><b>{e(a)}</b><p>{e(b)}</p></li>' for a, b in d["use"]) + '</ol>'
    def kp(t):
        parts = [p for p in re.split(r"(?<=。)(?=[^」）])", t) if p]
        # long entries: split into two paragraphs near the middle
        if len(t) > 200:
            mid = len(parts) // 2
            return f'<p>{e("".join(parts[:mid]))}</p><p>{e("".join(parts[mid:]))}</p>'
        return f'<p>{e(t)}</p>'
    know = '<div class="pknow">' + "".join(
        f'<div class="k{" wide" if len(b) > 260 else ""}"><h4>{e(a)}</h4>{kp(b)}</div>' for a, b in d["know"]) + '</div>'
    return (f'<section class="sec tight paper prac" id="practice"><div class="wrap">'
            f'<div class="hd"><p class="eyebrow" lang="en">IN PRACTICE</p><h2 class="d3">導入と運用の実務</h2>'
            f'<p class="sub">{e(name)}を入れるときの打ち合わせから、毎日の使い方、現場で押さえておくべき勘どころ、お客様からよく聞かれる質問の答え方まで。</p>'
            '<nav class="pjump" aria-label="この章の目次"><a href="#spec-meeting"><b lang="en">01</b>仕様の打ち合わせ</a>'
            '<a href="#how-to-use"><b lang="en">02</b>使い方の流れ</a><a href="#know-how"><b lang="en">03</b>知っておくべきこと</a><a href="#qa"><b lang="en">04</b>想定問答</a></nav></div>'
            '<div class="pblk" id="spec-meeting"><header><h3><span lang="en">01</span>仕様の打ち合わせ</h3>'
            f'<p>{e(name)}の仕様は、メーカーとの打ち合わせで1つずつ決めていく。項目ごとに、打ち合わせで詰める内容と、事前に用意しておくと話が早く進む情報をまとめた。図面・材質・硬さ・年間数量・目標サイクルタイムは、どの項目にも共通して必要になる。</p></header>{spec}</div>'
            '<div class="pblk" id="how-to-use"><header><h3><span lang="en">02</span>使い方の流れ</h3>'
            f'<p>電源を入れてから1個目を仕上げ、量産に移るまでの標準的な流れ。実際の手順と数値は、機械の取扱説明書と社内の作業標準に従う。</p></header>{steps}</div>'
            '<div class="pblk" id="know-how"><header><h3><span lang="en">03</span>知っておくべきこと</h3>'
            f'<p>削る・磨くといった主な機能の陰で、仕上がりと安全を左右する作業や現象がある。トラブルの多くはここから起きる。</p></header>{know}</div>'
            + qa_block(slug) + '</div></section>')

n = 0
for slug, d in DATA.items():
    p = f"{SITE}/machine-tools/{slug}/index.html"
    s = open(p, encoding="utf-8").read()
    name = re.search(r'<h1 class="d1"[^>]*>(.*?)</h1>', s).group(1)
    s = re.sub(r'<section class="sec tight paper prac" id="practice">.*?</section>', "", s, flags=re.S)
    s = re.sub(r'<p class="pgo">.*?</p>', "", s)
    anchor = '<section class="sec tight"><div class="wrap"><div class="hd"><p class="eyebrow" lang="en">COMPONENTS'
    assert anchor in s, slug
    s = s.replace(anchor, section(name, d, slug) + anchor, 1)
    # jump link under the lead
    s = re.sub(r'(<p class="sub lead"[^>]*>.*?</p>)(</section>)',
               r'\1<p class="pgo" style="margin-top:22px;text-align:center"><a class="lnk" href="#practice">仕様の打ち合わせ・使い方・知っておくべきこと</a></p>\2', s, count=1)
    s = re.sub(r"/\*prac\*/.*?(?=</style>)", "", s, flags=re.S)
    s = s.replace("</style>", CSS + "</style>", 1)
    open(p, "w", encoding="utf-8").write(s); n += 1
print("pages:", n)
