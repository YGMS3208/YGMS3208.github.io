/* ---------- part page: every operation as its own section ---------- */
function opSections(p){
  function links(rows){ return rows.length ? rows.map(function(r){ return "<a href=\"" + he(r[0]) + "\">" + esc(C[r[0]].n) + "</a>"; }).join("、") : "<span class=\"muted\">—</span>"; }
  return "<div class=\"oplist\">" + p.ops.map(function(o){
    return "<article class=\"opx\" id=\"op" + o.no + "\"><span class=\"no tn\">" + o.no + "</span><div class=\"bd\"><div class=\"hrow\"><h3>" + esc(o.n) + "</h3>" + kchip(o.k) + "</div><p>" + esc(o.d) + "</p><dl>" +
      "<div><dt>設備</dt><dd>" + links(o.m) + "</dd></div><div><dt>検査</dt><dd>" + links(o.x) + "</dd></div>" +
      (o.kp ? "<div><dt>管理ポイント</dt><dd>" + esc(o.kp) + "</dd></div>" : "") + "</dl><a class=\"lnk sm\" href=\"" + ho(o) + "\">" + opNo(o) + "の工程図を見る</a></div></article>";
  }).join("") + "</div>";
}

/* ---------- equipment: index of groups, one hub page per group ---------- */
function groupList(gi){ var l = []; C.forEach(function(c, ci){ if(c.g === gi) l.push(ci); }); l.sort(function(a, b){ return use[b].length - use[a].length || a - b; }); return l; }
function eqIndex(){
  var h = "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">EQUIPMENT</p><h1 class=\"d2\">" + C.length + "の設備。</h1><p class=\"sub\">自動車部品の工場で使われる工作機械・生産設備・検査機を、" + G.length + "の分類に整理しています。分類を開くと、それぞれの仕組みと、どの部品のどの工程で使われるかを一覧できます。</p></div><div class=\"ggrid\">";
  G.forEach(function(g, gi){
    var l = groupList(gi);
    h += "<section class=\"gcard\"><a class=\"gh\" href=\"" + hg(gi) + "\"><span class=\"stage thumb\">" + catPic(l[0]) + "</span><span class=\"t\"><span class=\"eyebrow\">" + pad(gi + 1) + "</span><h2>" + esc(g) + "</h2><span class=\"n\">" + l.length + "種類</span></span></a><ul class=\"gl\">" +
      l.map(function(ci){ return "<li><a href=\"" + he(ci) + "\">" + esc(C[ci].n) + "</a></li>"; }).join("") + "</ul></section>";
  });
  h += "</div></div></section>";
  show(h, [["設備"]], "eq");
}
function eqGroupView(gi){
  var l = groupList(gi), g = G[gi];
  var h = "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">EQUIPMENT GROUP " + pad(gi + 1) + "</p><h1 class=\"d2\">" + esc(g) + "</h1><p class=\"sub\">" + esc(g) + "に分類される" + l.length + "種類の設備です。それぞれの仕組みと、この図鑑の中で使われている部品・工程の数をまとめています。</p></div>";
  h += "<div class=\"gblock gdesc\" style=\"margin-top:0\">" + l.map(function(ci){
    var ps = uniq(use[ci].map(function(u){ return u.o.p.name; }));
    return "<a class=\"erow\" href=\"" + he(ci) + "\"><span class=\"tp stage thumb\">" + catPic(ci) + "</span><b>" + esc(C[ci].n) + "</b><span class=\"c\">" + use[ci].length + " OPS · " + ps.length + " PARTS</span><span class=\"w\">" + esc(C[ci].d) + "<small>" + esc(ps.slice(0, 6).join("、") + (ps.length > 6 ? " ほか" : "")) + "</small></span></a>";
  }).join("") + "</div>";
  var others = G.map(function(x, i){ return i === gi ? "" : "<a class=\"pill\" href=\"" + hg(i) + "\">" + esc(x) + "</a>"; }).join("");
  h += "<div class=\"hd\" style=\"margin:72px 0 20px\"><p class=\"eyebrow\">OTHER GROUPS</p></div><div class=\"pills\">" + others + "</div></div></section>";
  show(h, [["設備", "/equipment/"], [g]], "eq");
}

/* ---------- about ---------- */
function aboutView(){
  var S = D.site;
  var h = "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">ABOUT</p><h1 class=\"d2\">この図鑑について</h1><p class=\"sub lead\">自動車製造工程図鑑は、クルマの部品がどんな工程と設備でつくられているかを、図解で一つずつ説明する個人運営の図鑑です。</p></div>" +
    "<article class=\"prose\">" +
    "<h2 id=\"author\">運営者</h2><p><b>" + esc(S.handle) + "</b></p><p>" + esc(S.bio) + "</p><p>本サイトは所属する企業とは関係のない、個人のサイトです。特定の企業や製品を推奨・宣伝するものではなく、広告やアフィリエイトリンクも掲載していません。</p>" +
    "<h2 id=\"policy\">編集方針</h2><ul>" +
    "<li>内容は、公開されている技術資料・規格・一般的な技術知識をもとにまとめています。取引先や顧客の現場で知り得た情報は掲載しません。</li>" +
    "<li>工程・設備・数値は乗用車の量産で一般的な構成と目安です。実際の工程はメーカー・車種・生産量によって異なります。</li>" +
    "<li>「" + parts.length + "部品」「" + ops.length + "工程」「" + C.length + "設備」などの数は、この図鑑の分類で数えたものです。自動車全体の部品数や工程数を表すものではありません。</li>" +
    "<li>パワートレイン比較の数量は、代表的な仕様を仮定した目安です。前提は<a href=\"/powertrain/\">比較ページ</a>の末尾に記載しています。</li>" +
    "<li>図はすべて独自に作成した模式図で、寸法や比率は実物と一致しません。</li>" +
    "<li>メーカー名は各設備分野でよく知られる例示で、網羅・推奨・順位を示すものではありません。社名・製品ラインアップは変わることがあります。</li></ul>" +
    "<h2 id=\"license\">利用条件</h2><p>本サイトの文章と図解は <a href=\"" + S.licenseUrl + "\" rel=\"license\">" + esc(S.license) + "</a>（クリエイティブ・コモンズ 表示-非営利 4.0 国際）で提供しています。出典を明記すれば、授業・レポート・勉強会の資料など非営利の目的で、改変を含めて自由に使えます。営利目的での利用はできません。</p>" +
    "<p class=\"cite\">出典の書き方の例：「自動車製造工程図鑑（" + esc(S.handle) + "）" + esc(S.base) + "」</p>" +
    "<h2 id=\"report\">誤りの報告</h2><p>内容の誤りや古くなった情報に気づいた方は、<a href=\"" + S.issues + "\" rel=\"nofollow\">GitHubのIssue</a>からお知らせください。確認のうえ修正し、ページの更新日を改めます。</p>" +
    "<h2 id=\"history\">更新履歴</h2><ul><li>" + esc(S.publishedJa) + "　公開</li></ul>" +
    "</article></div></section>";
  show(h, [["この図鑑について"]], "");
}
function notFoundView(){
  var h = "<section class=\"sec\"><div class=\"wrap\" style=\"text-align:center\"><p class=\"eyebrow\">404 NOT FOUND</p><h1 class=\"d2\" style=\"margin:18px 0\">ページが見つかりません。</h1><p class=\"sub\" style=\"margin:0 auto 32px\">URLが変わったか、削除された可能性があります。トップや系統の一覧からお探しください。</p><p class=\"ctas\" style=\"justify-content:center\"><a class=\"cta\" href=\"/\">トップへ</a><a class=\"lnk\" href=\"/systems/\">系統から探す</a></p></div></section>";
  show(h, null, "");
}
function searchShell(){
  var h = "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">SEARCH</p><h1 class=\"d2\" id=\"sh1\">検索</h1><form class=\"sform\" action=\"/search/\" method=\"get\" role=\"search\"><label class=\"sr\" for=\"sq\">検索語</label><input id=\"sq\" name=\"q\" type=\"search\" autocomplete=\"off\" placeholder=\"部品・工程・設備・メーカー・材料\"><button class=\"cta\" type=\"submit\">検索</button></form></div><div id=\"sres\"><p class=\"sub\">部品・工程・設備・メーカー・材料・管理項目を探せます。</p></div></div></section>";
  show(h, [["検索"]], "");
}

/* ---------- shell parts shared by every page ---------- */
function shellParts(){
  var mm = "<a href=\"/\">トップ</a><a href=\"/systems/\">系統</a><a href=\"/powertrain/\">パワートレイン比較</a><a href=\"/map/\">工程マップ</a><a href=\"/methods/\">加工法</a><a href=\"/equipment/\">設備</a><a href=\"/about/\">この図鑑について</a><div class=\"sys\">" + D.systems.map(function(s, si){ return "<a href=\"" + hs(s) + "\"><span>" + pad(si + 1) + "</span>" + esc(s.name) + "</a>"; }).join("") + "</div>";
  var qs = "<p lang=\"en\">QUICK LINKS</p>" + D.site.quick.map(function(x){ return "<a href=\"/search/?q=" + encodeURIComponent(x) + "\">" + esc(x) + "</a>"; }).join("");
  return { mm: mm, qs: qs };
}

/* ---------- build-time API ---------- */
function findBy(list, slug){ for(var i = 0; i < list.length; i++) if(list[i].slug === slug) return list[i]; return null; }
window.__render = function(r){
  CUR = null;
  var t = r.t, k = r.k;
  if(t === "home") home();
  else if(t === "systems") systemsView();
  else if(t === "sys") sysView(findBy(D.systems, k));
  else if(t === "part") partView(findBy(parts, k));
  else if(t === "op"){ var p = findBy(parts, k); var o = p.ops.filter(function(x){ return x.no === r.no; })[0]; opView(o); }
  else if(t === "pt") ptView();
  else if(t === "map") mapView();
  else if(t === "eqi") eqIndex();
  else if(t === "eqg") eqGroupView(D.gslug.indexOf(k));
  else if(t === "eq") eqView(C.map(function(c){ return c.slug; }).indexOf(k));
  else if(t === "methods") kindsView();
  else if(t === "method") kindView(K.map(function(c){ return c.slug; }).indexOf(k));
  else if(t === "about") aboutView();
  else if(t === "search") searchShell();
  else notFoundView();
  return CUR;
};
window.__shell = shellParts;
window.__met = function(){ return MET.map(function(m, ti){ return { parts: m.parts, ops: m.ops, mops: m.mops, vol: volIdx(ti) }; }); };

/* part card with its description (system pages) */
function partCardD(p){
  return "<a class=\"card\" href=\"" + hp(p) + "\"><div class=\"stage thumb\">" + partPic(p) + "</div><div class=\"tx\"><p class=\"eyebrow\">" + p.ops.length + " OPS</p><h3>" + esc(p.name) + "</h3><p>" + esc(p.desc) + "</p><span class=\"ft\"><span>" + esc(p.mat) + "</span></span></div></a>";
}
