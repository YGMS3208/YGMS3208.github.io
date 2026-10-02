"""Derive the website render template (site_tpl.html) from the app template.
The result is only ever run at build time inside headless Chromium: it renders one route at a
time and hands the HTML back to site.py. Nothing in here ships to visitors as-is."""
import os as _os
_B = _os.path.dirname(_os.path.abspath(__file__))
_D = _os.path.join(_os.path.dirname(_B), "data")

import re

src = open(_B + "/template.html", encoding="utf-8").read()
out = src


def rep(old, new, count=1):
    global out
    n = out.count(old)
    assert n >= 1, ("missing", old[:120])
    if count == 1:
        assert n == 1, ("ambiguous", n, old[:120])
    out = out.replace(old, new)


# ---------------------------------------------------------------- css tweaks
rep("--ink2:#3A3A3F; --muted:#86868B;", "--ink2:#3A3A3F; --muted:#6E6E73;")
rep(".page.enter{animation:fadein .5s var(--ease) both}\n", "")
rep("animation:sweep 7s var(--ease) 1.2s infinite}", "animation:sweep 7s var(--ease) 1.2s 2}")

# ---------------------------------------------------------------- links → real paths
rep('''function hs(s){ return "#s-" + s.id; }
function hp(p){ return "#p-" + p.s.id + "-" + p.id; }
function ho(o){ return "#o-" + o.p.s.id + "-" + o.p.id + "-" + (o.i + 1); }
function he(ci){ return "#e-" + ci; }
function hk(ki){ return "#k-" + ki; }
function opNo(o){ return "OP" + ((o.i + 1) * 10); }''',
    '''function hs(s){ return "/systems/" + s.slug + "/"; }
function hp(p){ return "/parts/" + p.slug + "/"; }
function ho(o){ return "/parts/" + o.p.slug + "/op" + o.no + "/"; }
function hoa(o){ return "/parts/" + o.p.slug + "/#op" + o.no; }
function he(ci){ return "/equipment/" + C[ci].slug + "/"; }
function hg(gi){ return "/equipment/group/" + D.gslug[gi] + "/"; }
function hk(ki){ return "/methods/" + K[ki].slug + "/"; }
function opNo(o){ return "OP" + o.no; }''')
rep('<a href=\\"#top\\">トップ</a>";', '<a href=\\"/\\">トップ</a>";')
rep('''function show(html, cr, nav){
  view.innerHTML = "<div class=\\"page enter\\">" + crumb(cr) + html + "</div>";
  document.querySelectorAll("[data-nav]").forEach(function(a){ if(a.getAttribute("data-nav") === nav) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
  wireCarousels();
}''', '''var CUR = null;
function show(html, cr, nav){ CUR = { html: "<div class=\\"page\\">" + crumb(cr) + html + "</div>", nav: nav, crumbs: cr || [] }; }''')
for a, b in [("#systems", "/systems/"), ("#pt", "/powertrain/"), ("#map", "/map/"), ("#eq", "/equipment/"), ("#kinds", "/methods/")]:
    out = out.replace('href=\\"%s\\"' % a, 'href=\\"%s\\"' % b)
    out = out.replace('"%s"]' % a, '"%s"]' % b)
rep('var view = document.getElementById("view"), qIn = document.getElementById("q");', "")
rep('(o.i + 1) * 10) + "</span><span class=\\"nm\\">', 'o.no) + "</span><span class=\\"nm\\">')
rep('<span class=\\"big\\">" + ((o.i + 1) * 10) + "</span>', '<span class=\\"big\\">" + o.no + "</span>')
rep('''  var cur = view.querySelector(".steps [aria-current]");
  if(cur){ var r = cur.closest(".steps"); r.scrollLeft = Math.max(0, cur.parentNode.offsetLeft - r.clientWidth / 2 + 56); }
''', "")

# ---------------------------------------------------------------- tabs: every state rendered, hidden unless selected
rep('''function ptSeg(id){ return "<div class=\\"seg\\" role=\\"tablist\\" aria-label=\\"パワートレイン\\" id=\\"" + id + "\\">" + TY.map(function(t, ti){ return "<button type=\\"button\\" role=\\"tab\\" data-pt=\\"" + ti + "\\" aria-selected=\\"" + (ti === state.pt) + "\\">" + esc(t.n) + "</button>"; }).join("") + "</div>"; }''',
    '''function ptSeg(id, pre, from){ from = from || 0; return "<div class=\\"seg\\" role=\\"tablist\\" aria-label=\\"パワートレイン\\" id=\\"" + id + "\\">" + TY.map(function(t, ti){ if(ti < from) return ""; var on = ti === 4; return "<button type=\\"button\\" role=\\"tab\\" id=\\"" + pre + "-t" + ti + "\\" aria-controls=\\"" + pre + "-" + ti + "\\" data-pt=\\"" + ti + "\\" aria-selected=\\"" + on + "\\"" + (on ? "" : " tabindex=\\"-1\\"") + ">" + esc(t.n) + "</button>"; }).join("") + "</div>"; }
function panel(pre, ti, body){ return "<div class=\\"ptpanel\\" role=\\"tabpanel\\" id=\\"" + pre + "-" + ti + "\\" aria-labelledby=\\"" + pre + "-t" + ti + "\\"" + (ti === 4 ? "" : " hidden") + ">" + body + "</div>"; }''')
rep('''function renderPtHome(){
  var box = document.getElementById("ptbox"); if(!box) return;
  var prev = box.querySelectorAll("[data-to]");
  var sh = shiftRows(state.pt, 6), t = TY[state.pt];
  box.innerHTML = "<div class=\\"kpis\\">" + kpiBlock(state.pt) + "</div><p class=\\"ptnote\\"><b>" + esc(t.spec) + "</b>　" + esc(t.note) + "</p>" +
    (state.pt === 0 ? "" : typeDiff(state.pt) + "<div class=\\"shift\\"><div><h3>増える設備<small>MORE</small></h3>" + sh.up + "</div><div><h3>減る設備<small>LESS</small></h3>" + sh.dn + "</div></div>");
  var now = box.querySelectorAll("[data-to]");
  now.forEach(function(el, i){ if(prev[i]) el.setAttribute("data-from", prev[i].getAttribute("data-to")); else el.setAttribute("data-from", el.getAttribute("data-to")); });
  countUp(box);
  document.querySelectorAll("#seg1 button").forEach(function(b){ b.setAttribute("aria-selected", String(+b.getAttribute("data-pt") === state.pt)); });
}''', '''function ptHomePanels(){
  return TY.map(function(t, ti){
    var sh = shiftRows(ti, 6);
    return panel("pth", ti, "<div class=\\"kpis\\">" + kpiBlock(ti) + "</div><p class=\\"ptnote\\"><b>" + esc(t.spec) + "</b>　" + esc(t.note) + "</p>" +
      (ti === 0 ? "" : typeDiff(ti) + "<div class=\\"shift\\"><div><h3>増える設備<small>MORE</small></h3>" + sh.up + "</div><div><h3>減る設備<small>LESS</small></h3>" + sh.dn + "</div></div>"));
  }).join("");
}''')
rep('" + ptSeg("seg1") + "</div><div id=\\"ptbox\\"></div>', '" + ptSeg("seg1", "pth", 0) + "</div><div id=\\"ptbox\\">" + ptHomePanels() + "</div>')
rep('''  show(h, null, "top");
  renderPtHome();
}''', '''  show(h, null, "top");
}''')
# home: numbers are counted on this atlas's own classification
rep('''<div><b class=\\"tn\\">" + C.length + "</b><span>設備</span></div></div></div></section>";''',
    '''<div><b class=\\"tn\\">" + C.length + "</b><span>設備</span></div></div><p class=\\"hnote\\">数はこの図鑑の分類で数えたものです。</p></div></section>";''')
# home highlight tiles: real links
out = re.sub(r'"#o-drivetrain-gear-(\d+)"', lambda m: 'ho(partByKey["drivetrain.gear"].ops[%d])' % (int(m.group(1)) - 1), out)
out = re.sub(r'"#p-(\w+?)-(\w+)"\]', lambda m: 'hp(partByKey["%s.%s"])]' % (m.group(1), m.group(2)), out)
rep('" + C.length + "の設備。</h2><p class=\\"sub\\">旋盤から三次元測定機まで。どの部品のどの工程で使われているかを、設備から逆引きできます。</p></div><a class=\\"lnk\\" href=\\"/equipment/\\">設備をすべて見る</a>',
    '" + C.length + "の設備。</h2><p class=\\"sub\\">旋盤から三次元測定機まで。どの部品のどの工程で使われているかを、設備から逆引きできます。</p></div><a class=\\"lnk\\" href=\\"/equipment/\\">設備をすべて見る</a>')

# ---------------------------------------------------------------- part page: each operation as a section of the page
rep('''  h += "<section class=\\"sec tight\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">OPERATIONS</p><h2 class=\\"d3\\">工程と設備の一覧</h2></div><div class=\\"tbl\\"><div class=\\"tr th\\"><span>OP</span><span>工程</span><span>加工・生産設備</span><span>検査・測定</span></div>";
  p.ops.forEach(function(o){''', '''  h += "<section class=\\"sec tight\\" id=\\"ops\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">OPERATIONS</p><h2 class=\\"d3\\">" + esc(p.name) + "の工程と設備</h2></div>" + opSections(p) + "</div></section>";
  if(false) p.ops.forEach(function(o){''')
rep('''  h += "</div></div></section>";
  function lst(obj){''', '''  function lst(obj){''')
rep('<p class=\\"sub\\" style=\\"font-size:16px\\">" + (hasD(p) ? "青い線はその工程で加工する面です。" : "各工程の加工原理と主な設備の模式図です。") + "選ぶと拡大図と設備を開きます。</p>',
    '<p class=\\"sub\\" style=\\"font-size:16px\\">" + (hasD(p) ? "青い線はその工程で加工する面です。" : "各工程の加工原理と主な設備の模式図です。") + "選ぶと工程図と設備を開きます。</p>')
rep('"<div class=\\"wrap pvis\\"><div class=\\"stage\\">" + partPic(p) + "</div></div>" +\n    "<div class=\\"wrap\\"><div class=\\"specs\\"><div><b>" + p.ops.length',
    '"<div class=\\"wrap pvis\\"><figure class=\\"stage\\">" + partPic(p) + "<figcaption>" + esc(p.name) + "のイメージ（模式図）</figcaption></figure></div>" +\n    "<div class=\\"wrap\\"><div class=\\"specs\\"><div><b>" + p.ops.length')

# ---------------------------------------------------------------- op page
rep('h += "<div class=\\"wrap ovis\\"><div class=\\"stage\\">" + (hasD(p) ? opDraw(o) : opPic(o)) + "</div></div>";',
    'h += "<div class=\\"wrap ovis\\"><figure class=\\"stage\\">" + (hasD(p) ? opDraw(o) : opPic(o)) + "<figcaption>" + esc(p.name) + "の" + opNo(o) + "「" + esc(o.n) + "」" + (hasD(p) ? "の工程図" : "の原理図") + "（模式図）</figcaption></figure></div>";')

# ---------------------------------------------------------------- powertrain page
rep('''  h += "<section class=\\"sec paper\\" id=\\"shift\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">MACHINE TOOLS</p><h2 class=\\"d3\\">ガソリン車と比べて、増える設備・減る設備。</h2><p class=\\"sub\\" style=\\"font-size:16px\\">数字は、その設備を使う工程の数に部品の搭載数量を掛けた合計の差です。</p>" + ptSeg("seg2") + "</div><div id=\\"shiftbox\\"></div></div></section>";''',
    '''  var sp = "";
  for(var ti = 1; ti < TY.length; ti++){ var sh = shiftRows(ti, 10); sp += panel("pts", ti, typeDiff(ti) + "<div class=\\"shift\\"><div><h3>増える設備<small>" + esc(TY[ti].en) + "</small></h3>" + sh.up + "</div><div><h3>減る設備<small>VS GASOLINE</small></h3>" + sh.dn + "</div></div>"); }
  h += "<section class=\\"sec paper\\" id=\\"shift\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">MACHINE TOOLS</p><h2 class=\\"d3\\">ガソリン車と比べて、増える設備・減る設備。</h2><p class=\\"sub\\" style=\\"font-size:16px\\">数字は、その設備を使う工程の数に部品の搭載数量を掛けた合計の差です。</p>" + ptSeg("seg2", "pts", 1) + "</div><div id=\\"shiftbox\\">" + sp + "</div></div></section>";''')
rep('return "<div class=\\"cc" + (ti === state.pt ? " on" : "")', 'return "<div class=\\"cc" + (ti === 4 ? " on" : "")')
rep('<label class=\\"tog\\"><input type=\\"checkbox\\" id=\\"onlydiff\\"" + (state.onlyDiff ? " checked" : "") + ">違いがある部品だけ表示</label></div><div class=\\"matrix\\" id=\\"matrix\\"></div>',
    '<label class=\\"tog\\"><input type=\\"checkbox\\" id=\\"onlydiff\\" checked>違いがある部品だけ表示</label></div><div class=\\"matrix only\\" id=\\"matrix\\">" + matrixHTML() + "</div>')
rep('<li>電池セルは工程の数え方をそろえるため、1ロットとして数えています（搭載数は約60〜100セル）。</li></ul></div></section>";',
    '<li>電池セルは工程の数え方をそろえるため、1ロットとして数えています（搭載数は約60〜100セル）。</li></ul><p class=\\"dl\\"><a class=\\"lnk\\" href=\\"/powertrain/powertrain-comparison.csv\\" download>比較データをCSVでダウンロード</a></p></div></section>";')
rep('''  show(h, null, "pt");
  renderShift(); renderMatrix();
}''', '''  show(h, [["パワートレイン比較"]], "pt");
}''')
rep('''function renderMatrix(){
  var box = document.getElementById("matrix"); if(!box) return;
  var h = "<table>''', '''function matrixHTML(){
  var h = "<table>''')
rep('''      if(state.onlyDiff && !diff) return;
      var qd = PT.qd[pkey(p)];
      rows += "<tr><td>''', '''      var qd = PT.qd[pkey(p)];
      if(diff) anyDiff = true;
      rows += "<tr" + (diff ? "" : " class=\\"same\\"") + "><td>''')
rep('''  D.systems.forEach(function(s){
    var rows = "";''', '''  D.systems.forEach(function(s){
    var rows = "", anyDiff = false;''')
rep('''    if(rows) h += "<tr class=\\"g\\"><td colspan=\\"6\\">" + esc(s.name) + "</td></tr>" + rows;
  });
  box.innerHTML = h + "</tbody></table>";''', '''    if(rows) h += "<tr class=\\"g" + (anyDiff ? "" : " same") + "\\"><td colspan=\\"6\\">" + esc(s.name) + "</td></tr>" + rows;
  });
  return h + "</tbody></table>";''')

# ---------------------------------------------------------------- where-used lists point into the part page
rep('return "<a class=\\"use\\" href=\\"" + ho(o) + "\\"><span class=\\"w\\"><b>" + esc(o.p.name)', 'return "<a class=\\"use\\" href=\\"" + hoa(o) + "\\"><span class=\\"w\\"><b>" + esc(o.p.name)', count=2)
rep('''return "<a class=\\"f" + KF[o.k] + "\\" href=\\"" + ho(o) + "\\" title=''', '''return "<a class=\\"f" + KF[o.k] + "\\" href=\\"" + hoa(o) + "\\" title=''')

# ---------------------------------------------------------------- equipment page
rep('''<div class=\\"stats\\" style=\\"margin-top:32px\\"><div><b>" + u.length + "</b><span>工程で使用</span></div><div><b>" + partsOf(ci) + "</b><span>部品</span></div><div><b>" + sysN + "</b><span>系統</span></div></div></div><div class=\\"stage\\">" + catPic(ci) + "</div></section>";''',
    '''<div class=\\"stats\\" style=\\"margin-top:32px\\"><div><b>" + u.length + "</b><span>工程で使用</span></div><div><b>" + partsOf(ci) + "</b><span>部品</span></div><div><b>" + sysN + "</b><span>系統</span></div></div></div><figure class=\\"stage\\">" + catPic(ci) + "<figcaption>" + esc(c.n) + "の原理図（模式図）</figcaption></figure></section>";
  if(c.body) h += "<section class=\\"sec tight\\" style=\\"padding-bottom:0\\"><div class=\\"wrap\\"><article class=\\"prose\\"><h2 class=\\"d3\\">" + esc(c.n) + "のしくみと使われ方</h2>" + c.body + "</article></div></section>";''')
rep('mkeys.map(function(m){ return "<a class=\\"pill\\" href=\\"/equipment/\\" data-q=\\"" + esc(m) + "\\">"', 'mkeys.map(function(m){ return "<a class=\\"pill\\" href=\\"/search/?q=" + encodeURIComponent(m) + "\\">"') if 'href=\\"/equipment/\\" data-q=' in out else rep('mkeys.map(function(m){ return "<a class=\\"pill\\" href=\\"#q\\" data-q=\\"" + esc(m) + "\\">"', 'mkeys.map(function(m){ return "<a class=\\"pill\\" rel=\\"nofollow\\" href=\\"/search/?q=" + encodeURIComponent(m) + "\\">"')
rep('show(h, [["設備", "/equipment/"], [c.n]], "eq");', 'show(h, [["設備", "/equipment/"], [G[c.g], hg(c.g)], [c.n]], "eq");')

# ---------------------------------------------------------------- method page
rep('''  var h = "<section class=\\"sec tight\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">" + FAM[KF[ki]].en + "</p><h1 class=\\"d2\\">" + esc(K[ki].n) + "</h1><p class=\\"sub\\">" + esc(K[ki].d) + "</p><div class=\\"stats\\"><div><b>" + list.length + "</b><span>工程</span></div><div><b>" + uniq(list.map(function(x){ return pkey(x.o.p); })).length + "</b><span>部品</span></div></div></div>" +
    "<p class=\\"h4\\">この工法で使う設備</p><div class=\\"pills\\">" + keys.map(function(ci){ return "<a class=\\"pill\\" href=\\"" + he(ci) + "\\">" + esc(C[ci].n) + "<span class=\\"n\\">" + cnt[ci] + "</span></a>"; }).join("") + "</div>" + usageList(list, false) + "</div></section>";''',
    '''  var k = K[ki], nm = k.title || k.n;
  var h = "<section class=\\"sec tight\\"><div class=\\"wrap\\"><div class=\\"hd\\" style=\\"margin-bottom:0\\"><p class=\\"eyebrow\\">" + FAM[KF[ki]].en + "</p><h1 class=\\"d2\\">" + esc(nm) + "</h1><p class=\\"sub lead\\">" + esc(k.lead || k.d) + "</p><div class=\\"stats\\"><div><b>" + list.length + "</b><span>工程</span></div><div><b>" + uniq(list.map(function(x){ return pkey(x.o.p); })).length + "</b><span>部品</span></div><div><b>" + keys.length + "</b><span>設備</span></div></div></div></div></section>";
  if(k.body) h += "<section class=\\"sec tight\\" style=\\"padding-top:0\\"><div class=\\"wrap\\"><article class=\\"prose\\">" + k.body + "</article></div></section>";
  h += "<section class=\\"sec tight paper\\"><div class=\\"wrap\\"><div class=\\"hd\\"><p class=\\"eyebrow\\">EQUIPMENT</p><h2 class=\\"d3\\">" + esc(nm) + "で使う設備</h2></div><div class=\\"pills\\">" + keys.map(function(ci){ return "<a class=\\"pill\\" href=\\"" + he(ci) + "\\">" + esc(C[ci].n) + "<span class=\\"n\\">" + cnt[ci] + "</span></a>"; }).join("") + "</div></div></section>";
  h += "<section class=\\"sec tight\\"><div class=\\"wrap\\"><div class=\\"hd\\" style=\\"margin-bottom:0\\"><p class=\\"eyebrow\\">WHERE IT'S USED</p><h2 class=\\"d3\\">この図鑑での" + esc(nm) + "の工程</h2></div>" + usageList(list, false) + "</div></section>";''')
rep('show(h, [["加工法", "/methods/"], [K[ki].n]], "kinds");', 'show(h, [["加工法", "/methods/"], [K[ki].title || K[ki].n]], "kinds");')
rep('''h += "<a class=\\"fcard\\" href=\\"" + hk(ki) + "\\"><div class=\\"top\\"><b>" + esc(k.n) + "</b>''', '''h += "<a class=\\"fcard\\" href=\\"" + hk(ki) + "\\"><div class=\\"top\\"><b>" + esc(k.title || k.n) + "</b>''')

# ---------------------------------------------------------------- equipment index → group hubs; drop search/overlay/router code
i0 = out.index("/* ---------- equipment index ---------- */")
i1 = out.index("/* ---------- materials ---------- */")
out = out[:i0] + "/*__EQINDEX__*/\n" + out[i1:]
i0 = out.index("/* ---------- search ---------- */")
i1 = out.index("})();\n</script>")
out = out[:i0] + "/*__API__*/\n" + out[i1:]

rep('<h2 class=\\"d3\\">" + esc(s.name) + "の部品</h2></div><div class=\\"grid-cards\\">" + s.parts.map(partCard).join("")', '<h2 class=\\"d3\\">" + esc(s.name) + "の部品</h2></div><div class=\\"grid-cards\\">" + s.parts.map(partCardD).join("")')
extra = open(_B + "/site_views.js", encoding="utf-8").read() + "\n" + open(_B + "/site_views_mt.js", encoding="utf-8").read()
out = out.replace("/*__EQINDEX__*/", "").replace("/*__API__*/", extra)
open(_B + "/site_tpl.html", "w", encoding="utf-8").write(out)
left = re.findall(r'href=\\"#[a-z]', out)
print("site_tpl.html", len(out), "leftover hash hrefs:", left)
