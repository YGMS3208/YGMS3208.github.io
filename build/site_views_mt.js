/* ===================================================================== machine-tool atlas (/machine-tools/) */
var MTD = D.mt || null;
function mtU(kind, slug){ return kind === "type" ? "/machine-tools/" + slug + "/" : kind === "comp" ? "/machine-tools/components/" + slug + "/" : kind === "auto" ? "/machine-tools/automation/" + slug + "/" : "/machine-tools/guide/" + slug + "/"; }
function mtBy(list, slug){ for(var i = 0; i < list.length; i++) if(list[i].slug === slug) return list[i]; return null; }
function mtSvg(slug, label, extra){ var f = MTD.ill[slug]; return f ? "<svg class=\"ilu " + (extra || "") + "\" viewBox=\"" + f.vb + "\" role=\"img\" aria-label=\"" + esc(label) + "\">" + f.svg + "</svg>" : ""; }
function mtImg(slug, alt){ return "<img src=\"/machine-tools/img/" + slug + ".svg\" alt=\"" + esc(alt) + "\" loading=\"lazy\" decoding=\"async\" width=\"640\" height=\"400\">"; }
function mtAnat(slug, name, cap){
  var f = MTD.ill[slug]; if(!f) return "";
  return "<div class=\"anat\"><figure class=\"stage\">" + mtSvg(slug, name + "の構造図") + "<figcaption>" + esc(cap || (name + "の主な部位（模式図）")) + "</figcaption></figure><ol class=\"notes\">" +
    f.notes.map(function(x, i){ return "<li><span class=\"no\">" + (i + 1) + "</span><div><b>" + esc(x[0]) + "</b>" + (x[1] ? "<span>" + esc(x[1]) + "</span>" : "") + "</div></li>"; }).join("") + "</ol></div>";
}
function mtCard(it, kind, eyebrow){
  return "<a class=\"card\" href=\"" + mtU(kind, it.slug) + "\"><div class=\"stage thumb\">" + mtImg(it.slug, it.name + "の図") + "</div><div class=\"tx\"><p class=\"eyebrow\">" + esc(eyebrow || it.en) + "</p><h3>" + esc(it.name) + "</h3><p>" + esc(it.lead.length > 72 ? it.lead.slice(0, 70) + "…" : it.lead) + "</p></div></a>";
}
function mtPills(slugs, list, kind){ return "<div class=\"pills\">" + slugs.map(function(s){ var it = mtBy(list, s); return it ? "<a class=\"pill\" href=\"" + mtU(kind, s) + "\">" + esc(it.name) + "</a>" : ""; }).join("") + "</div>"; }
function mtSec(eyebrow, title, inner, cls){ return "<section class=\"sec tight" + (cls ? " " + cls : "") + "\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">" + eyebrow + "</p><h2 class=\"d3\">" + title + "</h2></div>" + inner + "</div></section>"; }
function mtNext(list, it, kind, label){
  var i = list.indexOf(it), p = list[i - 1], n = list[i + 1];
  return "<div class=\"wrap\"><nav class=\"next\" aria-label=\"前後の" + label + "\">" + (p ? "<a href=\"" + mtU(kind, p.slug) + "\"><small>PREVIOUS</small><b>" + esc(p.name) + "</b></a>" : "<span></span>") + (n ? "<a href=\"" + mtU(kind, n.slug) + "\"><small>NEXT</small><b>" + esc(n.name) + "</b></a>" : "") + "</nav></div><div style=\"height:40px\"></div>";
}
function famOf(t){ for(var i = 0; i < MTD.fam.length; i++) if(MTD.fam[i].id === t.fam) return MTD.fam[i]; return MTD.fam[0]; }

function mtHome(){
  var O = MTD.overview;
  var h = "<section class=\"hero night\"><div class=\"wrap t\"><p class=\"eyebrow\">MACHINE TOOL ATLAS</p><h1 class=\"d1\"><span class=\"nw\">工作機械図鑑</span></h1>" +
    "<p class=\"sub\">" + esc(O.lead) + "</p><p class=\"ctas\"><a class=\"cta\" href=\"#machines\">機種を見る</a><a class=\"lnk\" href=\"/machine-tools/guide/\">選び方から探す</a></p></div>" +
    "<div class=\"v mtv\">" + mtSvg("vertical-machining-center", "立形マシニングセンタの構造") + "</div>" +
    "<div class=\"wrap\"><div class=\"hstats\"><div><b class=\"tn\">" + MTD.types.length + "</b><span>機種</span></div><div><b class=\"tn\">" + MTD.comps.length + "</b><span>構成部品</span></div><div><b class=\"tn\">" + MTD.autos.length + "</b><span>自動化・周辺機器</span></div><div><b class=\"tn\">" + (MTD.guides.length + 1) + "</b><span>選び方ガイド</span></div></div></div></section>";
  h += "<section class=\"sec\" id=\"machines\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">MACHINES</p><h2 class=\"d2\">機種から、仕組みへ。</h2><p class=\"sub\">旋盤、マシニングセンタ、研削盤、歯車加工機。主な機種の構造と動き方を、部位の名前と一緒に図解します。</p></div>";
  MTD.fam.forEach(function(f, fi){
    var l = MTD.types.filter(function(t){ return t.fam === f.id; });
    h += "<div class=\"famh f" + (fi % 5) + "\"" + (fi ? "" : " style=\"margin-top:0\"") + "><i></i><b>" + esc(f.n) + "</b><small lang=\"en\">" + esc(f.en) + "</small></div><div class=\"grid-cards\">" + l.map(function(t){ return mtCard(t, "type", f.en); }).join("") + "</div>";
  });
  h += "</div></section>";
  if(SIM_ORDER.length) h += "<section class=\"sec tight\" style=\"padding-top:0\"><div class=\"wrap\"><a class=\"tile full dk mtpromo\" href=\"/machine-tools/training/\"><div class=\"tx\"><p class=\"eyebrow\" lang=\"en\">OPERATION TRAINING</p><h3><span class=\"nw\">触って、</span><span class=\"nw\">失敗して、覚える。</span></h3><p>" + SIM_ORDER.length + "機種の基本操作を、1ステップずつ自分で体験する操作トレーニング。設定やワークの取付けを間違えると、衝突や飛散、不良が起きます。</p><span class=\"lnk\">操作トレーニングへ</span></div><div class=\"vis\">" + mtImg("cnc-lathe", "NC旋盤の図") + "</div></a><p style=\"margin-top:16px\"><a class=\"lnk\" href=\"/machine-tools/troubles/\">衝突・飛散・不良の原因と対策をまとめた、工作機械のトラブル事例集</a></p></div></section>";
  h += "<section class=\"sec paper\"><div class=\"wrap\"><div class=\"hd row\"><div><p class=\"eyebrow\">COMPONENTS</p><h2 class=\"d2\">中身を、知る。</h2><p class=\"sub\">主軸、ボールねじ、リニアガイド、NC装置。精度と速さを決める構成部品です。</p></div><a class=\"lnk\" href=\"/machine-tools/components/\">構成部品をすべて見る</a></div><div class=\"grid-cards\">" +
    MTD.comps.map(function(c){ return mtCard(c, "comp", "COMPONENT"); }).join("") + "</div></div></section>";
  h += "<section class=\"sec\"><div class=\"wrap\"><div class=\"hd row\"><div><p class=\"eyebrow\">AUTOMATION</p><h2 class=\"d2\">止めずに、回す。</h2><p class=\"sub\">ローダ、ロボット、パレットチェンジャ。工作機械を無人で動かすための周辺機器です。</p></div><a class=\"lnk\" href=\"/machine-tools/automation/\">自動化をすべて見る</a></div><div class=\"grid-cards\">" +
    MTD.autos.map(function(c){ return mtCard(c, "auto", "AUTOMATION"); }).join("") + "</div></div></section>";
  h += "<section class=\"sec paper\"><div class=\"wrap\"><div class=\"hd row\"><div><p class=\"eyebrow\">GUIDE</p><h2 class=\"d2\">選び方と、違い。</h2><p class=\"sub\">ワークの形・精度・生産量から機種を絞り込む方法と、よく比べられる機種の違いをまとめています。</p></div><a class=\"lnk\" href=\"/machine-tools/guide/\">選び方ガイドへ</a></div><div class=\"list\">" +
    "<a class=\"li\" href=\"/machine-tools/guide/\"><span class=\"t\">" + esc(MTD.selection.name) + "</span><span class=\"n\">GUIDE</span></a>" +
    MTD.guides.map(function(g){ return "<a class=\"li\" href=\"" + mtU("guide", g.slug) + "\"><span class=\"t\">" + esc(g.name) + "</span><span class=\"n\">COMPARE</span></a>"; }).join("") + "</div></div></section>";
  h += "<section class=\"sec tight\"><div class=\"wrap\"><article class=\"prose\"><h2 class=\"d3\">" + esc(O.name) + "</h2>" + O.body + "</article></div></section>";
  show(h, [["工作機械図鑑"]], "mt");
}

function indsUsing(ci){ var seen = {}; use[ci].forEach(function(u){ seen[u.o.p.s.ind] = 1; }); return INDS.filter(function(d){ return seen[d.id]; }).map(indName).join("・"); }
function mtRelatedParts(t){
  if(t.eq < 0) return "";
  var ci = t.eq, ps = [], seen = {};
  use[ci].forEach(function(u){ var p = u.o.p; if(!seen[p.slug]){ seen[p.slug] = 1; ps.push(p); } });
  if(!ps.length) return "";
  return mtSec("IN THE ATLAS", "部品工場での使われ方",
    "<p class=\"sub\" style=\"font-size:16px;margin:-24px 0 28px\">製造工程図鑑では、" + esc(C[ci].n) + "が" + indsUsing(ci) + "の" + use[ci].length + "の工程・" + ps.length + "の部品で使われています。</p>" +
    "<div class=\"grid-cards\">" + ps.slice(0, 6).map(partCard).join("") + "</div>" +
    "<p style=\"margin-top:28px\"><a class=\"lnk\" href=\"" + he(ci) + "\">" + esc(C[ci].n) + "が使われる工程をすべて見る</a></p>", "paper");
}
function mtType(slug){
  var t = mtBy(MTD.types, slug), f = famOf(t);
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">" + esc(f.en) + "</p><h1 class=\"d1\" style=\"font-size:clamp(36px,6vw,80px)\">" + esc(t.name) + "</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(t.lead) + "</p></section>";
  h += "<section class=\"sec tight\" style=\"padding-top:clamp(40px,5vw,64px)\"><div class=\"wrap\">" + mtAnat(slug, t.name) + "</div></section>";
  h += mtSimLink(slug);
  h += "<section class=\"sec tight\"" + (SIM[slug] ? "" : " style=\"padding-top:0\"") + "><div class=\"wrap\"><article class=\"prose\">" + t.body + "</article></div></section>";
  if(t.comps.length) h += mtSec("COMPONENTS", "この機種を構成する主な部品", mtPills(t.comps, MTD.comps, "comp"));
  if(t.autos.length) h += mtSec("AUTOMATION", "組み合わせる自動化・周辺機器", mtPills(t.autos, MTD.autos, "auto"), "") ;
  h += mtRelatedParts(t);
  var sib = MTD.types.filter(function(x){ return x.fam === t.fam && x !== t; });
  if(sib.length) h += mtSec("SAME FAMILY", f.n + "のほかの機種", "<div class=\"grid-cards\">" + sib.map(function(x){ return mtCard(x, "type", f.en); }).join("") + "</div>");
  h += mtNext(MTD.types, t, "type", "機種");
  show(h, [["工作機械図鑑", "/machine-tools/"], [t.name]], "mt");
}
function mtComp(slug){
  var c = mtBy(MTD.comps, slug);
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">COMPONENT</p><h1 class=\"d1\" style=\"font-size:clamp(36px,6vw,80px)\">" + esc(c.name) + "</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(c.lead) + "</p></section>";
  h += "<section class=\"sec tight\" style=\"padding-top:clamp(40px,5vw,64px)\"><div class=\"wrap\">" + mtAnat(slug, c.name) + "</div></section>";
  h += "<section class=\"sec tight\" style=\"padding-top:0\"><div class=\"wrap\"><article class=\"prose\">" + c.body + "</article></div></section>";
  if(c.types.length) h += mtSec("USED IN", c.name + "が使われる主な機種", "<div class=\"grid-cards\">" + c.types.slice(0, 6).map(function(s){ var t = mtBy(MTD.types, s); return mtCard(t, "type", famOf(t).en); }).join("") + "</div>" + (c.types.length > 6 ? mtPills(c.types.slice(6), MTD.types, "type") : ""), "paper");
  h += mtNext(MTD.comps, c, "comp", "構成部品");
  show(h, [["工作機械図鑑", "/machine-tools/"], ["構成部品", "/machine-tools/components/"], [c.name]], "mt");
}
function mtAuto(slug){
  var c = mtBy(MTD.autos, slug);
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">AUTOMATION</p><h1 class=\"d1\" style=\"font-size:clamp(36px,6vw,80px)\">" + esc(c.name) + "</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(c.lead) + "</p></section>";
  h += "<section class=\"sec tight\" style=\"padding-top:clamp(40px,5vw,64px)\"><div class=\"wrap\">" + mtAnat(slug, c.name, c.name + "の構成例（模式図）") + "</div></section>";
  h += "<section class=\"sec tight\" style=\"padding-top:0\"><div class=\"wrap\"><article class=\"prose\">" + c.body + "</article></div></section>";
  if(c.types.length) h += mtSec("WORKS WITH", "よく組み合わせる機種", mtPills(c.types, MTD.types, "type"), "paper");
  if(c.eq >= 0) h += mtSec("IN THE ATLAS", "部品工場では", "<p class=\"sub\" style=\"font-size:16px;margin:-24px 0 24px\">製造工程図鑑では、" + esc(C[c.eq].n) + "が" + indsUsing(c.eq) + "の" + use[c.eq].length + "の工程で使われています。</p><p><a class=\"lnk\" href=\"" + he(c.eq) + "\">" + esc(C[c.eq].n) + "が使われる工程を見る</a></p>");
  h += mtNext(MTD.autos, c, "auto", "自動化・周辺機器");
  show(h, [["工作機械図鑑", "/machine-tools/"], ["自動化・周辺機器", "/machine-tools/automation/"], [c.name]], "mt");
}
function mtIndex(kind){
  var comp = kind === "comp", list = comp ? MTD.comps : MTD.autos;
  var h = "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\" lang=\"en\">" + (comp ? "COMPONENTS" : "AUTOMATION") + "</p><h1 class=\"d2\">" + (comp ? "工作機械の構成部品" : "工作機械の自動化・周辺機器") + "</h1><p class=\"sub\">" +
    (comp ? "工作機械の精度・速さ・寿命は、主軸、送り軸（サーボモータ・ボールねじ・リニアガイド）、構造体、制御（NC装置）、工具とワークの保持（ツールホルダ・チャック）で決まります。それぞれの仕組みと役割を図解します。"
          : "量産の現場では、工作機械を人が付きっきりで操作することはまれです。工作物の出し入れ、段取り、計測、切りくず処理を自動化する周辺機器と、その組み合わせ方をまとめています。") + "</p></div>" +
    "<h2 class=\"sr\">" + (comp ? "構成部品の一覧" : "自動化・周辺機器の一覧") + "</h2><div class=\"grid-cards\">" + list.map(function(c){ return mtCard(c, kind, comp ? "COMPONENT" : "AUTOMATION"); }).join("") + "</div>" +
    "<div class=\"list\" style=\"margin-top:56px\">" + list.map(function(c){ return "<a class=\"li\" href=\"" + mtU(kind, c.slug) + "\"><span class=\"t\">" + esc(c.name) + "</span><span class=\"n\">" + esc(c.lead.slice(0, 44)) + "…</span></a>"; }).join("") + "</div></div></section>";
  show(h, [["工作機械図鑑", "/machine-tools/"], [comp ? "構成部品" : "自動化・周辺機器"]], "mt");
}
function mtGuide(slug){
  var g = mtBy(MTD.guides, slug);
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">COMPARE</p><h1 class=\"d2\">" + esc(g.name) + "</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(g.lead) + "</p></section>";
  if(g.pics.length) h += "<div class=\"wrap\"><div class=\"vs\">" + g.pics.map(function(s){ var it = mtBy(MTD.types, s) || mtBy(MTD.comps, s); var k = mtBy(MTD.types, s) ? "type" : "comp"; return "<a class=\"vsi\" href=\"" + mtU(k, s) + "\"><span class=\"stage thumb\">" + mtImg(s, it.name + "の図") + "</span><b>" + esc(it.name) + "</b></a>"; }).join("") + "</div></div>";
  h += "<section class=\"sec tight\"><div class=\"wrap\"><article class=\"prose\">" + g.body + "</article></div></section>";
  h += mtSec("MORE GUIDES", "ほかのガイド", "<div class=\"list\"><a class=\"li\" href=\"/machine-tools/guide/\"><span class=\"t\">" + esc(MTD.selection.name) + "</span><span class=\"n\">GUIDE</span></a>" + MTD.guides.filter(function(x){ return x !== g; }).map(function(x){ return "<a class=\"li\" href=\"" + mtU("guide", x.slug) + "\"><span class=\"t\">" + esc(x.name) + "</span><span class=\"n\">COMPARE</span></a>"; }).join("") + "</div>", "paper");
  show(h, [["工作機械図鑑", "/machine-tools/"], ["選び方", "/machine-tools/guide/"], [g.name]], "mt");
}
function mtSelect(){
  var S = MTD.selection, Q = MTD.sel.q;
  var form = "<form class=\"selector\" id=\"selector\" onsubmit=\"return false\">" + Q.map(function(q){
    return "<fieldset><legend>" + esc(q.label) + "</legend><div class=\"opts\">" + q.opts.map(function(o, i){ return "<label><input type=\"radio\" name=\"" + q.id + "\" value=\"" + o[0] + "\"" + (i === q.def ? " checked" : "") + "><span>" + esc(o[1]) + "</span></label>"; }).join("") + "</div></fieldset>";
  }).join("") + "</form><div class=\"selres\" id=\"selres\" aria-live=\"polite\"><p class=\"sub\">条件を選ぶと、まず検討したい機種が表示されます（JavaScriptが必要です）。下の早見表も参考にしてください。</p></div>" +
    "<script type=\"application/json\" id=\"seldata\">" + JSON.stringify({ t: MTD.sel.t, names: MTD.types.map(function(t){ return [t.slug, t.name, mtU("type", t.slug)]; }) }).replace(/</g, "\\u003c") + "<\/scr" + "ipt>";
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">GUIDE</p><h1 class=\"d2\">" + esc(S.name) + "</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(S.lead) + "</p></section>";
  h += mtSec("FINDER", "条件から機種を絞り込む", form, "paper");
  h += "<section class=\"sec tight\"><div class=\"wrap\"><article class=\"prose\">" + S.body + "</article></div></section>";
  h += mtSec("COMPARE", "よく比べられる機種の違い", "<div class=\"list\">" + MTD.guides.map(function(x){ return "<a class=\"li\" href=\"" + mtU("guide", x.slug) + "\"><span class=\"t\">" + esc(x.name) + "</span><span class=\"n\">COMPARE</span></a>"; }).join("") + "</div>", "paper");
  show(h, [["工作機械図鑑", "/machine-tools/"], ["選び方"]], "mt");
}
function mtPromo(){
  return "<section class=\"sec\"><div class=\"wrap\"><a class=\"tile full dk mtpromo\" href=\"/machine-tools/\"><div class=\"tx\"><p class=\"eyebrow\" lang=\"en\">MACHINE TOOL ATLAS</p><h3><span class=\"nw\">工場の主役を、</span><span class=\"nw\">図解する。</span></h3><p>旋盤、マシニングセンタ、研削盤、歯車加工機。" + MTD.types.length + "機種の構造と、主軸・ボールねじなどの構成部品、自動化までをまとめた工作機械図鑑。</p><span class=\"lnk\">工作機械図鑑を見る</span></div><div class=\"vis\">" + mtImg("horizontal-machining-center", "横形マシニングセンタの図") + "</div></a></div></section>";
}
function mtRender(r){
  var t = r.t, k = r.k;
  if(t === "mthome") mtHome();
  else if(t === "mttype") mtType(k);
  else if(t === "mtcomp") mtComp(k);
  else if(t === "mtauto") mtAuto(k);
  else if(t === "mtcomps") mtIndex("comp");
  else if(t === "mtautos") mtIndex("auto");
  else if(t === "mtguide") mtGuide(k);
  else if(t === "mtselect") mtSelect();
  else if(t === "mtpromo") CUR = { html: mtPromo(), nav: "", crumbs: [] };
  else if(t === "mtsim") mtSimPage(k);
  else if(t === "mtsimhub") mtSimHub();
  else if(t === "mttrouble") mtTroubles();
}
