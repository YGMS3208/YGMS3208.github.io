/* 製造工程図鑑 — runtime for the static site: menu, search, tabs, carousels. */
(function(){
"use strict";
var d = document, RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function $(s, r){ return (r || d).querySelector(s); }
function $$(s, r){ return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
function esc(s){ return String(s == null ? "" : s).replace(/[&<>"']/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]; }); }
function hl(s, q){
  s = String(s || ""); if(!q) return esc(s);
  var lo = s.toLowerCase(), out = "", i = 0, j;
  while((j = lo.indexOf(q, i)) >= 0){ out += esc(s.slice(i, j)) + "<mark>" + esc(s.slice(j, j + q.length)) + "</mark>"; i = j + q.length; }
  return out + esc(s.slice(i));
}
function fmt(n){ return Math.round(n).toLocaleString("ja-JP"); }

/* ---------- overlays ---------- */
var sov = $("#sov"), mov = $("#mov"), qIn = $("#q"), last = null;
function openOv(el){ last = d.activeElement; el.classList.add("on"); d.body.style.overflow = "hidden"; if(el === sov){ loadIdx(); setTimeout(function(){ qIn.focus(); }, 60); } else { var a = el.querySelector("a"); if(a) a.focus(); } }
function closeOv(){ var was = sov.classList.contains("on") || mov.classList.contains("on"); [sov, mov].forEach(function(e){ e.classList.remove("on"); }); d.body.style.overflow = ""; if(was && last && last.focus) last.focus({ preventScroll: true }); }
$("#sbtn").addEventListener("click", function(){ openOv(sov); });
$("#mbtn").addEventListener("click", function(){ openOv(mov); });
$$("[data-close]").forEach(function(b){ b.addEventListener("click", closeOv); });
d.addEventListener("keydown", function(e){
  if(e.key === "Escape") closeOv();
  if(e.key === "/" && !/input|textarea/i.test((d.activeElement || {}).tagName || "")){ e.preventDefault(); openOv(sov); }
});

/* ---------- search index (loaded on first use) ---------- */
var IDX = null, waiting = [], loading = false;
function loadIdx(cb){
  if(IDX){ if(cb) cb(); return; }
  if(cb) waiting.push(cb);
  if(loading) return; loading = true;
  fetch(d.documentElement.getAttribute("data-si")).then(function(r){ return r.json(); }).then(function(j){ IDX = j; var w = waiting; waiting = []; w.forEach(function(f){ f(); }); });
}
function has(t, q){ return String(t || "").toLowerCase().indexOf(q) >= 0; }
var qs = $("#qs"), QUICK = qs.innerHTML, composing = false;
function suggest(){
  var raw = qIn.value.trim(), q = raw.toLowerCase();
  if(!q){ qs.innerHTML = QUICK; return; }
  loadIdx(function(){
    var out = [];
    IDX.p.forEach(function(p){ if(out.length < 5 && (has(p[0], q) || has(p[1], q))) out.push("<a href=\"" + p[3] + "\">" + hl(p[0], q) + " <small>部品</small></a>"); });
    IDX.c.forEach(function(c){ if(out.length < 9 && has(c[0], q)) out.push("<a href=\"" + c[2] + "\">" + hl(c[0], q) + " <small>設備</small></a>"); });
    IDX.k.forEach(function(k){ if(out.length < 10 && has(k[0], q)) out.push("<a href=\"" + k[1] + "\">" + hl(k[0], q) + " <small>加工法</small></a>"); });
    (IDX.m || []).forEach(function(m){ if(out.length < 11 && has(m[0], q)) out.push("<a href=\"" + m[2] + "\">" + hl(m[0], q) + " <small>" + esc(m[1]) + "</small></a>"); });
    IDX.o.forEach(function(o){ if(out.length < 12 && has(o[2], q)) out.push("<a href=\"" + o[5] + "\">" + hl(o[2], q) + " <small>" + esc(o[0]) + "・" + o[1] + "</small></a>"); });
    var all = "/search/?q=" + encodeURIComponent(raw);
    qs.innerHTML = "<p lang=\"en\">SUGGESTIONS</p>" + (out.join("") || "<a href=\"" + all + "\">「" + esc(raw) + "」で全体を検索</a>") + (out.length ? "<a class=\"all\" href=\"" + all + "\">すべての結果を見る</a>" : "");
  });
}
qIn.addEventListener("compositionstart", function(){ composing = true; });
qIn.addEventListener("compositionend", function(){ composing = false; suggest(); });
qIn.addEventListener("input", function(){ if(!composing) suggest(); });
qIn.addEventListener("keydown", function(e){ if(e.key === "Enter" && !e.isComposing && qIn.value.trim()) location.href = "/search/?q=" + encodeURIComponent(qIn.value.trim()); });

/* ---------- search page ---------- */
var sres = $("#sres");
if(sres){
  var raw = (new URLSearchParams(location.search).get("q") || "").trim(), q = raw.toLowerCase();
  var si = $("#sq"); if(si) si.value = raw;
  if(q){
    $("#sh1").textContent = "「" + raw + "」";
    d.title = "「" + raw + "」の検索結果｜製造工程図鑑";
    sres.innerHTML = "<p class=\"sub\">検索しています…</p>";
    loadIdx(function(){
      var rp = IDX.p.filter(function(p){ return has(p[0], q) || has(p[1], q) || has(p[2], q); });
      var rc = IDX.c.filter(function(c){ return has(c[0], q) || has(c[1], q); });
      var ro = IDX.o.filter(function(o){ return has(o[2], q) || has(o[3], q) || has(o[4], q); });
      var rm = IDX.r.filter(function(r){ return has(r[1], q) || has(r[2], q); });
      var rk = IDX.k.filter(function(k){ return has(k[0], q); });
      var rmt = (IDX.m || []).filter(function(m){ return has(m[0], q); });
      var h = "<h2 class=\"sr\">検索結果</h2><div class=\"stats\" style=\"margin-bottom:12px\"><div><b>" + rp.length + "</b><span>部品</span></div><div><b>" + rc.length + "</b><span>設備</span></div><div><b>" + ro.length + "</b><span>工程</span></div><div><b>" + rm.length + "</b><span>仕様・メーカー</span></div></div>";
      if(!(rp.length + rc.length + ro.length + rm.length + rk.length + rmt.length)){ sres.innerHTML = h + "<p class=\"sub\" style=\"margin-top:32px\">当てはまる項目がありません。表記を変えるか、短い言葉で試してください（例：研削、プレス）。</p>"; return; }
      if(rmt.length) h += "<div class=\"gblock\"><h3>工作機械図鑑<small>" + rmt.length + "</small></h3>" + rmt.map(function(m){ return "<a class=\"use\" href=\"" + m[2] + "\"><span class=\"w\"><b>" + hl(m[0], q) + "</b><small>" + esc(m[1]) + "</small></span></a>"; }).join("") + "</div>";
      if(rk.length) h += "<div class=\"gblock\"><h3>加工法<small>" + rk.length + "</small></h3>" + rk.map(function(k){ return "<a class=\"use\" href=\"" + k[1] + "\"><span class=\"w\"><b>" + hl(k[0], q) + "</b></span></a>"; }).join("") + "</div>";
      if(rc.length) h += "<div class=\"gblock\"><h3>設備<small>" + rc.length + "</small></h3>" + rc.map(function(c){ return "<a class=\"use\" href=\"" + c[2] + "\"><span class=\"w\"><b>" + hl(c[0], q) + "</b><small>" + esc(c[3]) + "</small></span><span class=\"s\">" + hl(c[1], q) + "</span><span class=\"m\"></span></a>"; }).join("") + "</div>";
      if(rp.length) h += "<div class=\"gblock\"><h3>部品<small>" + rp.length + "</small></h3>" + rp.map(function(p){ return "<a class=\"use\" href=\"" + p[3] + "\"><span class=\"w\"><b>" + hl(p[0], q) + "</b><small>" + esc(p[4]) + "</small></span><span class=\"s\">" + hl(p[2], q) + "</span><span class=\"m\">" + hl(p[1], q) + "</span></a>"; }).join("") + "</div>";
      if(rm.length) h += "<div class=\"gblock\"><h3>設備の仕様・メーカー<small>" + rm.length + "</small></h3>" + rm.map(function(r){ return "<a class=\"use\" href=\"" + r[6] + "\"><span class=\"w\"><b>" + esc(r[0]) + " <span class=\"role" + (r[7] === "i" ? " i" : "") + "\">" + (r[7] === "i" ? "検査" : "設備") + "</span></b><small>" + esc(r[3]) + " · <span class=\"tn\">" + r[4] + "</span>" + esc(r[5]) + "</small></span><span class=\"s\">" + hl(r[1], q) + "</span><span class=\"m\">" + hl(r[2], q) + "</span></a>"; }).join("") + "</div>";
      if(ro.length) h += "<div class=\"gblock\"><h3>工程<small>" + ro.length + "</small></h3>" + ro.map(function(o){ return "<a class=\"use\" href=\"" + o[5] + "\"><span class=\"w\"><b>" + esc(o[0]) + "</b><small><span class=\"tn\">" + o[1] + "</span>" + hl(o[2], q) + "</small></span><span class=\"s\">" + hl(o[3], q) + "</span><span class=\"m\">" + hl(o[4], q) + "</span></a>"; }).join("") + "</div>";
      sres.innerHTML = h;
    });
  }
}

/* ---------- machine-tool finder ---------- */
var selF = $("#selector"), selD = $("#seldata");
if(selF && selD){
  var SD = JSON.parse(selD.textContent), NM = {};
  SD.names.forEach(function(x){ NM[x[0]] = x; });
  function val(name){ var e = selF.querySelector("input[name=" + name + "]:checked"); return e ? e.value : ""; }
  function runSel(){
    var a = { shape: val("shape"), prec: val("prec"), vol: val("vol"), size: val("size") }, res = [];
    Object.keys(SD.t).forEach(function(slug){
      var t = SD.t[slug], sc = 0;
      var si = t[0].indexOf(a.shape);
      if(si < 0) return;
      sc += si === 0 ? 4 : 2;                                   // primary shape counts more
      if(a.prec === "high") sc += t[1].indexOf("high") >= 0 ? 2 : -3; else if(t[1].indexOf("std") < 0) sc -= 3;
      sc += t[2].indexOf(a.vol) >= 0 ? 2 : -1;
      sc += t[3].indexOf(a.size) >= 0 ? 1 : -2;
      if(sc >= 2) res.push([sc, slug]);
    });
    res.sort(function(x, y){ return y[0] - x[0]; });
    var box = $("#selres");
    if(!res.length){ box.innerHTML = "<p class=\"sub\">この組み合わせに合う機種は、この図鑑の範囲では見つかりませんでした。条件を1つ変えて試してください。</p>"; return; }
    box.innerHTML = "<p class=\"selh\">まず検討したい機種</p><div class=\"list\">" + res.slice(0, 4).map(function(x, i){ var n = NM[x[1]]; return "<a class=\"li" + (i ? "" : " top") + "\" href=\"" + n[2] + "\"><span class=\"t\">" + esc(n[1]) + "</span><span class=\"n\">" + esc(SD.t[x[1]][4]) + "</span></a>"; }).join("") + "</div><p class=\"selnote\">目安です。実際には、試し削りやメーカーへの相談で確認してください。</p>";
  }
  selF.addEventListener("change", runSel);
  runSel();
}

/* ---------- carousels ---------- */
$$(".track").forEach(function(t){
  function upd(){ var bs = $$("[data-car=\"" + t.id + "\"]"); if(bs.length === 2){ bs[0].disabled = t.scrollLeft < 4; bs[1].disabled = t.scrollLeft + t.clientWidth > t.scrollWidth - 4; } }
  t.addEventListener("scroll", upd, { passive: true }); upd();
});

/* ---------- tabs (every state is already in the page) ---------- */
function countFrom(oldP, newP){
  if(RM || !oldP) return;
  var a = $$("[data-to]", oldP), b = $$("[data-to]", newP);
  b.forEach(function(el, i){
    var to = +el.getAttribute("data-to"), from = a[i] ? +a[i].getAttribute("data-to") : to, t0 = null;
    if(from === to) return;
    function step(ts){ if(t0 === null) t0 = ts; var k = Math.min(1, (ts - t0) / 650), e = 1 - Math.pow(1 - k, 3); el.textContent = fmt(from + (to - from) * e); if(k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  });
}
function selectTab(btn, focus){
  var list = btn.closest("[role=tablist]"), old = list.querySelector("[aria-selected=true]");
  if(old === btn) return;
  var oldP = old ? d.getElementById(old.getAttribute("aria-controls")) : null, newP = d.getElementById(btn.getAttribute("aria-controls"));
  if(old){ old.setAttribute("aria-selected", "false"); old.setAttribute("tabindex", "-1"); }
  btn.setAttribute("aria-selected", "true"); btn.removeAttribute("tabindex");
  if(oldP) oldP.hidden = true;
  if(newP){ newP.hidden = false; countFrom(oldP, newP); }
  if(focus) btn.focus();
  if(list.id === "seg2") $$(".cc").forEach(function(c){ c.classList.toggle("on", c.getAttribute("data-cc") === btn.getAttribute("data-pt")); });
}
d.addEventListener("click", function(e){
  var t = e.target; if(!t || !t.closest) return;
  var tab = t.closest("[role=tab]");
  if(tab){ selectTab(tab); return; }
  var cc = t.closest(".cc [data-pt]");
  if(cc){ var b = $("#seg2 [data-pt=\"" + cc.getAttribute("data-pt") + "\"]"); if(b){ selectTab(b); $("#shift").scrollIntoView({ behavior: RM ? "auto" : "smooth" }); } return; }
  var c = t.closest("[data-car]");
  if(c){ var tr = d.getElementById(c.getAttribute("data-car")); if(tr) tr.scrollBy({ left: +c.getAttribute("data-dir") * tr.clientWidth * .8, behavior: RM ? "auto" : "smooth" }); return; }
  if(t.closest(".mm a") || t.closest("#qs a")) closeOv();
});
d.addEventListener("keydown", function(e){
  var tab = e.target && e.target.closest && e.target.closest("[role=tab]");
  if(!tab || (e.key !== "ArrowRight" && e.key !== "ArrowLeft")) return;
  var tabs = $$("[role=tab]", tab.closest("[role=tablist]")), i = tabs.indexOf(tab);
  var n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
  e.preventDefault(); selectTab(n, true);
});

/* ---------- composition table filter ---------- */
var od = $("#onlydiff");
if(od) od.addEventListener("change", function(){ $("#matrix").classList.toggle("only", od.checked); });

/* ---------- operation rail: keep the current step in view ---------- */
var cur = $(".steps [aria-current]");
if(cur){ var r = cur.closest(".steps"); r.scrollLeft = Math.max(0, cur.parentNode.offsetLeft - r.clientWidth / 2 + 56); }

/* ---------- training hub: show the visitor's own best score ---------- */
$$("[data-simbest]").forEach(function(a){
  try {
    var b = JSON.parse(localStorage.getItem("mts-sim-" + a.getAttribute("data-simbest")) || "null"), el = a.querySelector(".best");
    if(b && el){ el.textContent = "BEST " + b.p + " · " + b.g; el.hidden = false; }
  } catch(e){}
});
})();

/* ---------- atlas layer: reading bar, header, reveals, statement, counters ---------- */
(function(){
"use strict";
var d = document, root = d.documentElement, RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var bar = d.createElement("div"); bar.className = "rd"; bar.setAttribute("aria-hidden", "true"); d.body.appendChild(bar);
var hero = d.querySelector(".home .hero"), stmt = d.querySelectorAll(".stmt .q span, .stmt .q em");
var lastY = window.scrollY, ticking = false;
function frame(){
  ticking = false;
  var y = window.scrollY, h = root.scrollHeight - window.innerHeight;
  bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, y / h) : 0) + ")";
  lastY = y;
  if(RM) return;
  if(stmt.length){
    var line = window.innerHeight * .62;
    for(var i = 0; i < stmt.length; i++){ var r = stmt[i].getBoundingClientRect(); stmt[i].classList.toggle("on", r.top < line); }
  }
}
window.addEventListener("scroll", function(){ if(!ticking){ ticking = true; requestAnimationFrame(frame); } }, { passive: true });
frame();
if(hero) requestAnimationFrame(function(){ requestAnimationFrame(function(){ hero.classList.add("in"); }); });

/* process ticker: drifts on its own, but stays a normal scroller you can swipe or drag */
var tk = d.querySelector(".tick");
if(tk){
  var pos = 0, hold = 0, half = 0, own = false, drag = null;
  function measure(){ half = tk.querySelector(".row>div").offsetWidth; }
  function wrap(){ if(!half) return; if(tk.scrollLeft >= half){ tk.scrollLeft -= half; } else if(tk.scrollLeft <= 0 && hold){ tk.scrollLeft += half; } pos = tk.scrollLeft; }
  function pause(){ hold = Date.now() + 2600; }
  measure(); window.addEventListener("resize", measure);
  ["touchstart", "wheel", "keydown", "focusin"].forEach(function(ev){ tk.addEventListener(ev, pause, { passive: true }); });
  tk.addEventListener("mouseenter", function(){ hold = Infinity; });
  tk.addEventListener("mouseleave", function(){ if(!drag) pause(); });
  tk.addEventListener("scroll", function(){ if(own){ own = false; return; } pos = tk.scrollLeft; pause(); wrap(); }, { passive: true });
  tk.addEventListener("pointerdown", function(e){ if(e.pointerType !== "mouse") return; drag = { x: e.clientX, s: tk.scrollLeft, moved: false }; hold = Infinity; });
  window.addEventListener("pointermove", function(e){ if(!drag) return; var dx = e.clientX - drag.x; if(Math.abs(dx) > 4){ drag.moved = true; tk.classList.add("drag"); } tk.scrollLeft = drag.s - dx; });
  window.addEventListener("pointerup", function(){ if(!drag) return; var m = drag.moved; drag = null; setTimeout(function(){ tk.classList.remove("drag"); }, 0); if(!tk.matches(":hover")) pause(); if(m) pause(); });
  tk.addEventListener("click", function(e){ if(tk.classList.contains("drag")) e.preventDefault(); }, true);
  var seen = true;
  if("IntersectionObserver" in window) new IntersectionObserver(function(es){ seen = es[0].isIntersecting; }).observe(tk);
  var t0 = 0;
  (function loop(ts){
    var dt = t0 ? Math.min(64, ts - t0) : 16; t0 = ts;
    if(!RM && seen && Date.now() > hold && half){ pos += dt * .04; if(pos >= half) pos -= half; own = true; tk.scrollLeft = pos; }
    requestAnimationFrame(loop);
  })(0);
}

function count(el){
  var to = +el.getAttribute("data-n"), t0 = null;
  if(RM || !to){ el.textContent = to.toLocaleString("ja-JP"); return; }
  function step(ts){ if(t0 === null) t0 = ts; var k = Math.min(1, (ts - t0) / 1600), e = 1 - Math.pow(1 - k, 4); el.textContent = Math.round(to * e); if(k < 1) requestAnimationFrame(step); }
  requestAnimationFrame(step);
}
var els = d.querySelectorAll("[data-r], [data-n]");
if(!("IntersectionObserver" in window)){ Array.prototype.forEach.call(els, function(e){ e.classList.add("in"); }); return; }
var io = new IntersectionObserver(function(es){
  es.forEach(function(e){
    if(!e.isIntersecting) return;
    e.target.classList.add("in");
    if(e.target.hasAttribute("data-n")) count(e.target);
    io.unobserve(e.target);
  });
}, { rootMargin: "0px 0px -8% 0px", threshold: .08 });
Array.prototype.forEach.call(els, function(e){ io.observe(e); });
if(stmt.length) frame();
})();

/* ---------- glossary: remember where you came from, preview on hover, filter ---------- */
(function(){
"use strict";
var d = document, RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var GL = "/machine-tools/glossary/", onGL = location.pathname.indexOf(GL) === 0, onGLIndex = location.pathname === GL, KEY = "gl-back", RKEY = "gl-restore";
function ss(k, v){ try { if(v === undefined) return JSON.parse(sessionStorage.getItem(k) || "null"); if(v === null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, JSON.stringify(v)); } catch(e){ return null; } }
/* returning from the glossary: put the reader back where they were */
var rs = ss(RKEY);
if(rs && rs.u === location.href.split("#")[0]){ ss(RKEY, null); window.addEventListener("load", function(){ window.scrollTo(0, rs.y); }); }
/* leaving for the glossary */
if(!onGL) d.addEventListener("click", function(e){
  var a = e.target.closest && e.target.closest('a[href^="' + GL + '"]');
  if(!a) return;
  ss(KEY, { u: location.href.split("#")[0], t: ((d.querySelector("main h1.d1, main h1.d2") || {}).textContent || d.title.split("｜")[0] || "前のページ").trim(), y: window.scrollY });
}, true);

if(onGL){
  var back = ss(KEY), ref = d.referrer.split("#")[0];
  if(back && back.u !== location.href.split("#")[0]){
    var b = d.createElement("a"); b.className = "glback"; b.href = back.u; b.hidden = true;
    b.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg><span></span>';
    b.querySelector("span").textContent = "「" + back.t + "」に戻る";
    d.body.appendChild(b);
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ b.hidden = false; }); });
    b.addEventListener("click", function(e){
      e.preventDefault();
      ss(RKEY, { u: back.u, y: back.y }); ss(KEY, null);
      if(ref === back.u && history.length > 1) history.back(); else location.href = back.u;
    });
  }
  /* jumping between terms keeps a single history entry, so "back" returns to the article */
  function hit(id){ var el = d.getElementById(id); if(!el) return; d.querySelectorAll(".gt.hit").forEach(function(x){ x.classList.remove("hit"); }); el.classList.add("hit"); }
  d.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if(!a) return;
    var id = a.getAttribute("href").slice(1), el = d.getElementById(id);
    if(!el) return;
    e.preventDefault();
    history.replaceState(null, "", "#" + id);
    el.scrollIntoView({ behavior: RM ? "auto" : "smooth", block: "start" });
    if(id.indexOf("t-") === 0) hit(id);
  });
  if(location.hash.indexOf("#t-") === 0) hit(location.hash.slice(1));
  /* filter */
  var q = d.getElementById("gq"), arts = d.querySelectorAll(".gt"), cats = d.querySelectorAll(".gcat"), none = d.getElementById("gnone");
  if(q) q.addEventListener("input", function(){
    var v = q.value.trim().toLowerCase(), any = false;
    arts.forEach(function(a){ var ok = !v || a.getAttribute("data-s").indexOf(v) >= 0 || a.textContent.toLowerCase().indexOf(v) >= 0; a.hidden = !ok; if(ok) any = true; });
    cats.forEach(function(c){ c.hidden = !c.querySelector(".gt:not([hidden])"); });
    none.hidden = any;
  });
}

/* hover preview (mouse / trackpad only; a tap simply opens the glossary) */
var src = d.documentElement.getAttribute("data-gj");
if(!src || !(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches)) return;
var data = null, tip = null, timer = 0, cur = null;
function load(cb){ if(data) return cb(); fetch(src).then(function(r){ return r.json(); }).then(function(j){ data = j; cb(); }).catch(function(){}); }
function show(a){
  var t = data && data[a.getAttribute("data-t") || (a.hash || "").replace("#t-", "")];
  if(!t || cur !== a) return;
  if(!tip){ tip = d.createElement("div"); tip.className = "gtip"; tip.setAttribute("role", "tooltip"); d.body.appendChild(tip); }
  tip.innerHTML = ""; var b = d.createElement("b"), i = d.createElement("i"), p = d.createElement("p"), s = d.createElement("small");
  b.textContent = t[0]; i.textContent = t[1]; p.textContent = t[2]; s.textContent = onGL ? "クリックでこの用語へ移動" : "クリックで用語辞典を開く";
  tip.appendChild(b); tip.appendChild(i); tip.appendChild(p); tip.appendChild(s);
  var r = a.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
  var x = Math.max(16, Math.min(r.left + r.width / 2 - w / 2, window.innerWidth - w - 16));
  var y = r.top - h - 10 < 64 ? r.bottom + 10 : r.top - h - 10;
  tip.style.left = x + "px"; tip.style.top = y + "px"; tip.style.transformOrigin = (r.left + r.width / 2 - x) + "px " + (y > r.top ? "0" : "100%"); tip.classList.add("on");
}
function hide(){ clearTimeout(timer); cur = null; if(tip) tip.classList.remove("on"); }
d.addEventListener("mouseover", function(e){
  var a = e.target.closest && e.target.closest("a.gl, .gt .rl a");
  if(!a || a === cur) return;
  cur = a; clearTimeout(timer);
  timer = setTimeout(function(){ load(function(){ show(a); }); }, 220);
});
d.addEventListener("mouseout", function(e){ var a = e.target.closest && e.target.closest("a.gl, .gt .rl a"); if(a && !a.contains(e.relatedTarget)) hide(); });
window.addEventListener("scroll", hide, { passive: true });
})();

/* ---------- motion layer ---------- */
(function(){
"use strict";
var d = document, RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
/* header: highlight follows the hovered link */
var nav = d.querySelector(".gn nav");
if(nav){
  var hl = d.createElement("span"); hl.className = "gn-hl"; hl.setAttribute("aria-hidden", "true"); nav.appendChild(hl);
  nav.addEventListener("mouseover", function(e){
    var a = e.target.closest && e.target.closest("a"); if(!a || !nav.contains(a)) return;
    hl.style.left = a.offsetLeft + "px"; hl.style.width = a.offsetWidth + "px";
  });
}
/* menu: stagger the items */
d.querySelectorAll(".ov .mm").forEach(function(mm){
  var k = 0; mm.querySelectorAll(":scope > a, .grp > *").forEach(function(el){ el.style.setProperty("--k", k++); });
});
/* tabs: a sliding indicator */
d.querySelectorAll(".seg[role=tablist]").forEach(function(seg){
  var ind = d.createElement("span"); ind.className = "seg-ind"; ind.setAttribute("aria-hidden", "true"); seg.insertBefore(ind, seg.firstChild); seg.classList.add("js-ind");
  function move(){ var b = seg.querySelector("[aria-selected=true]"); if(!b) return; ind.style.left = b.offsetLeft + "px"; ind.style.width = b.offsetWidth + "px"; }
  move(); window.addEventListener("resize", move); if(d.fonts && d.fonts.ready) d.fonts.ready.then(move);
  new MutationObserver(move).observe(seg, { attributes: true, subtree: true, attributeFilter: ["aria-selected"] });
});
/* accordions open and close smoothly */
d.querySelectorAll("details.qa").forEach(function(det){
  var sum = det.querySelector("summary"), body = det.querySelector(".qb"); if(!sum || !body || RM) return;
  var anim = null;
  sum.addEventListener("click", function(e){
    e.preventDefault(); if(anim) anim.cancel();
    var open = det.open, h0 = det.offsetHeight;
    if(!open){ det.open = true; }
    var h1 = open ? sum.offsetHeight : det.offsetHeight;
    det.style.overflow = "hidden";
    anim = det.animate({ height: [h0 + "px", h1 + "px"] }, { duration: open ? 260 : 380, easing: "cubic-bezier(.16,1,.3,1)" });
    if(!open) body.animate({ opacity: [0, 1], transform: ["translateY(-6px)", "none"] }, { duration: 380, easing: "cubic-bezier(.16,1,.3,1)" });
    anim.onfinish = function(){ if(open) det.open = false; det.style.overflow = ""; anim = null; };
  });
});
/* copy a link to a section */
var toast = null, tt = 0;
function say(msg){
  if(!toast){ toast = d.createElement("div"); toast.className = "toast"; toast.setAttribute("role", "status"); d.body.appendChild(toast); }
  toast.textContent = msg; toast.classList.add("on"); clearTimeout(tt); tt = setTimeout(function(){ toast.classList.remove("on"); }, 1800);
}
d.querySelectorAll(".gguide h2[id], .pblk[id] > header h3, .prac[id] .hd h2").forEach(function(h){
  var id = h.id || h.closest("[id]").id; if(!id) return;
  var b = d.createElement("button"); b.type = "button"; b.className = "hlink"; b.textContent = "#"; b.setAttribute("aria-label", "この見出しへのリンクをコピー");
  b.addEventListener("click", function(e){
    e.preventDefault(); e.stopPropagation();
    var url = location.href.split("#")[0] + "#" + id;
    (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject()).then(function(){ say("リンクをコピーしました"); }, function(){ history.replaceState(null, "", "#" + id); say("アドレス欄のリンクを使えます"); });
  });
  h.appendChild(b);
});
/* a soft light follows the pointer on dark panels */
if(window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches && !RM){
  d.querySelectorAll(".tile.dk").forEach(function(t){
    t.addEventListener("pointermove", function(e){ var r = t.getBoundingClientRect(); t.style.setProperty("--mx", (e.clientX - r.left) + "px"); t.style.setProperty("--my", (e.clientY - r.top) + "px"); });
  });
}
})();

/* ---------- figures: every rule here keys off the shared markup, so new pages inherit it ----------
   .anat > figure.stage, .pvis > figure.stage (assemblies), figure[data-td]  -> teardown (exploded view)
   svg.ilu with .a / .mfe / .hl / .cool / .cutl / .beam                      -> process motion
   svg.ilu with .bal + .balt beside ol.notes                                 -> numbered callouts, linked to the list
   .lab svg (charts and diagrams in the guides)                              -> lines draw in
   .oplist                                                                   -> process rail that follows the reader
   opt out of any of them with data-motion="off" on the figure or list */
(function(){
"use strict";
var d = document, RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches, HAS_IO = "IntersectionObserver" in window;
function cls(el){ return (el.getAttribute("class") || "").trim(); }
function off(el){ return !!(el.closest && el.closest('[data-motion="off"]')); }
function len(el){ try { return Math.ceil(el.getTotalLength()) + 1; } catch(e){ return 0; } }
function dashed(el){ var v = getComputedStyle(el).strokeDasharray; return v && v !== "none"; }
/* run fn once when el comes near, and keep a "live" class while it is on screen */
function watch(el, near, fn, opt){
  if(!HAS_IO){ near(); fn(); return; }
  var done = false, pre = false;
  new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting && !pre){ pre = true; near(); } }); }, { rootMargin: "300px 0px" }).observe(el);
  new IntersectionObserver(function(es){ es.forEach(function(e){
    el.classList.toggle("live", e.isIntersecting);
    if(e.isIntersecting && !done){ done = true; if(!pre){ pre = true; near(); } fn(); }
  }); }, opt || { threshold: .35 }).observe(el);
}

/* ---- callouts: balloons and leaders appear in order; list and drawing point at each other ---- */
function callouts(svg){
  var ts = svg.querySelectorAll(".balt"); if(!ts.length) return null;
  var map = {}, order = 0, pend = [];
  [].forEach.call(svg.querySelectorAll(".leadl, .leadd, .bal, .balt"), function(el){
    pend.push(el);
    if(cls(el) !== "balt") return;
    var k = el.textContent.trim(); order++;
    pend.forEach(function(p){ p.style.setProperty("--n", order); p.setAttribute("data-k", k); if(cls(p) === "leadl") p.style.setProperty("--len", len(p)); });
    (map[k] = map[k] || []).push.apply(map[k], pend); pend = [];
  });
  svg.classList.add("co");
  var box = svg.closest(".anat"), list = box && box.querySelector("ol.notes"), lis = {};
  if(list) [].forEach.call(list.children, function(li){ var n = li.querySelector(".no"); if(n) lis[n.textContent.trim()] = li; });
  var sticky = null;
  function pick(k){
    svg.classList.toggle("pick", !!k);
    [].forEach.call(svg.querySelectorAll(".co .on"), function(x){ x.classList.remove("on"); });
    Object.keys(lis).forEach(function(n){ lis[n].classList.toggle("on", n === k); });
    if(k && map[k]) map[k].forEach(function(x){ x.classList.add("on"); });
    if(api.onpick) api.onpick(k);
  }
  Object.keys(lis).forEach(function(k){
    var li = lis[k];
    li.addEventListener("mouseenter", function(){ pick(k); });
    li.addEventListener("mouseleave", function(){ pick(sticky); });
    li.addEventListener("click", function(e){ if(e.target.closest("a")) return; sticky = sticky === k ? null : k; pick(sticky); });
  });
  Object.keys(map).forEach(function(k){ map[k].forEach(function(x){
    x.addEventListener("mouseenter", function(){ pick(k); });
    x.addEventListener("mouseleave", function(){ pick(sticky); });
  }); });
  var api = {
    map: map,
    show: function(){ svg.classList.add("cin"); },
    hide: function(){ svg.classList.remove("cin"); }
  };
  return api;
}

/* ---- teardown + callouts: each leader stays attached to its part while the parts move apart ---- */
function link(svg, co){
  var parts = [].slice.call(svg.querySelectorAll("g.td")), pk = {}, legs = [], resolved = false;
  function offs(g){ var cs = getComputedStyle(g); return [parseFloat(cs.getPropertyValue("--dx")) || 0, parseFloat(cs.getPropertyValue("--dy")) || 0]; }
  /* which parts does each number name: the figure's data-pk (checked by hand, see tools/callout_parts.json),
     else the topmost part painted under the leader's dot */
  var fixed = null; try { fixed = JSON.parse(svg.getAttribute("data-pk") || "null"); } catch(e){}
  function resolve(){
    resolved = true;
    Object.keys(co.map).forEach(function(k){
      var dot = null, line = null;
      co.map[k].forEach(function(x){ var c = cls(x); if(c.indexOf("leadd") === 0) dot = x; if(c.indexOf("leadl") === 0) line = x; });
      if(!dot) return;
      var gs = [];
      if(fixed && fixed[k]) gs = fixed[k].map(function(i){ return parts[i]; }).filter(Boolean);
      if(!gs.length){
        var cx = +dot.getAttribute("cx"), cy = +dot.getAttribute("cy"), g = null, m = dot.getScreenCTM();
        if(m && d.elementsFromPoint){
          var px = m.a * cx + m.c * cy + m.e, py = m.b * cx + m.d * cy + m.f;
          if(px > 0 && py > 0 && px < innerWidth && py < innerHeight)
            d.elementsFromPoint(px, py).some(function(el){ var t = el.closest && el.closest("g.td"); if(t && svg.contains(t)){ g = t; return true; } return false; });
        }
        if(!g){
          var best = 0;
          parts.forEach(function(p){ var b = p.getBBox(), a = b.width * b.height; if(cx >= b.x - 2 && cx <= b.x + b.width + 2 && cy >= b.y - 2 && cy <= b.y + b.height + 2 && (!g || a < best)){ g = p; best = a; } });
        }
        if(g) gs = [g];
      }
      if(!gs.length) return;
      pk[k] = gs;
      var o = offs(gs[0]); dot.style.setProperty("--ldx", o[0] + "px"); dot.style.setProperty("--ldy", o[1] + "px"); dot.classList.add("tdl");
      if(line){
        var x1 = +line.getAttribute("x1"), y1 = +line.getAttribute("y1"), x2 = +line.getAttribute("x2"), y2 = +line.getAttribute("y2");
        var dcx = +dot.getAttribute("cx"), dcy = +dot.getAttribute("cy");
        var first = Math.hypot(x1 - dcx, y1 - dcy) <= Math.hypot(x2 - dcx, y2 - dcy);
        legs.push({ el: line, a: first ? "x1" : "x2", b: first ? "y1" : "y2", x: first ? x1 : x2, y: first ? y1 : y2, dx: o[0], dy: o[1] });
      }
    });
  }
  var raf = 0, k0 = 0;
  function ease(t){ return 1 - Math.pow(1 - t, 4); }
  co.onpick = function(k){
    if(!resolved) resolve();
    parts.forEach(function(p){ p.classList.remove("on"); });
    svg.classList.toggle("tdpick", !!(k && pk[k]));
    if(k && pk[k]) pk[k].forEach(function(g){ g.classList.add("on"); });
  };
  return function(on){
    if(!resolved) resolve();
    cancelAnimationFrame(raf);
    var from = k0, to = on ? 1 : 0, t0 = performance.now(), dur = RM ? 0 : 950;
    (function step(ts){
      var t = dur ? Math.min(1, (ts - t0) / dur) : 1; k0 = from + (to - from) * ease(t);
      legs.forEach(function(l){ l.el.setAttribute(l.a, (l.x + l.dx * k0).toFixed(1)); l.el.setAttribute(l.b, (l.y + l.dy * k0).toFixed(1)); });
      if(t < 1) raf = requestAnimationFrame(step);
    })(t0);
  };
}

/* ---- process motion: arrows and machined faces draw in, heat and coolant keep moving while visible ---- */
function motion(svg){
  var lines = [].filter.call(svg.querySelectorAll(".a, .mfe"), function(el){ return el.tagName !== "text" && !dashed(el); });
  var loops = svg.querySelectorAll(".hl, .cool, .cutl, .cutframe, .beam, .beamf");
  if(!lines.length && !loops.length && !svg.querySelector(".af")) return false;
  lines.forEach(function(el){ el.style.setProperty("--len", len(el)); });
  [].forEach.call(svg.querySelectorAll(".hl"), function(el, i){ el.style.setProperty("--n", i % 6); });
  svg.classList.add("mo");
  return true;
}

/* ---- teardown: split the flattened drawing at each outline (class="el") and move the parts apart ---- */
var NOTE = /^(a|af|al|hl|lead|leadl|leadd|bal|balt|no|tol|tbg|tbl|ttl)$/;
function explode(svg){
  var vb = svg.viewBox && svg.viewBox.baseVal; if(!vb || !vb.width) return 0;
  var W = vb.width, H = vb.height, kids = [].slice.call(svg.children);
  var comps = [], cur = [], notes = [], shadow = [];
  kids.forEach(function(el){
    var t = el.tagName.toLowerCase(); if(t === "defs" || t === "title" || t === "desc" || t === "style") return;
    var c = cls(el), c0 = c.split(/\s+/)[0];
    if(c0 === "sh"){ shadow.push(el); return; }
    if(t === "text" || NOTE.test(c)){ notes.push(el); return; }
    cur.push(el);
    if(c0 === "el"){ comps.push(cur); cur = []; }
  });
  if(cur.length) comps.push(cur);
  if(comps.length < 6) return 0;
  var box = comps.map(function(c){
    var x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    c.forEach(function(e){ try { var b = e.getBBox(); if(!b.width && !b.height) return; x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y); x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height); } catch(err){} });
    if(x0 > x1) return [0, 0, 0, 0, 0];
    return [x0, y0, x1, y1, (x1 - x0) * (y1 - y0)];
  });
  var n = comps.length, amax = Math.max.apply(null, box.map(function(b){ return b[4]; }));
  if(!amax) return 0;
  /* the base: among the large parts, the one reaching lowest */
  var base = -1;
  box.forEach(function(b, i){ if(b[4] >= .18 * amax && (base < 0 || b[3] > box[base][3] || (b[3] === box[base][3] && b[4] > box[base][4]))) base = i; });
  var bx = (box[base][0] + box[base][2]) / 2, by = (box[base][1] + box[base][3]) / 2;
  /* small parts ride along with the part they sit on */
  var small = .004 * W * H, parent = [];
  for(var i = 0; i < n; i++){
    parent[i] = i;
    if(box[i][4] >= small) continue;
    var cx = (box[i][0] + box[i][2]) / 2, cy = (box[i][1] + box[i][3]) / 2, best = -1;
    for(var j = 0; j < n; j++){
      if(j === i || box[j][4] < small) continue;
      if(box[j][0] - 4 <= cx && cx <= box[j][2] + 4 && box[j][1] - 4 <= cy && cy <= box[j][3] + 4 && (best < 0 || box[j][4] < box[best][4])) best = j;
    }
    if(best >= 0) parent[i] = best;
  }
  var mv = {};
  for(i = 0; i < n; i++){
    if(parent[i] !== i) continue;
    if(i === base){ mv[i] = [0, 0]; continue; }
    /* spread outward in proportion to the distance from the base, with a lift, so neighbours separate */
    var b = box[i], vx = (b[0] + b[2]) / 2 - bx, vy = (b[1] + b[3]) / 2 - by - .18 * H, L = Math.hypot(vx, vy) || 1, S = Math.max(W, H);
    var dist = Math.max(.06 * S, Math.min(.17 * S, L * .42));
    var dx = vx / L * dist, dy = vy / L * dist, m = 4, ex = dx, ey = dy;
    if(b[0] + dx < m) dx = m - b[0];
    if(b[2] + dx > W - m) dx = W - m - b[2];
    if(b[1] + dy < m) dy = m - b[1];
    if(b[3] + dy > H - m) dy = H - m - b[3];
    if((dx > 0) !== (ex > 0) && Math.abs(vx) > 1) dx = 0;
    if((dy > 0) !== (ey > 0) && Math.abs(vy) > 1) dy = 0;
    mv[i] = [dx, dy];
  }
  var NS = "http://www.w3.org/2000/svg";
  shadow.forEach(function(e){ svg.appendChild(e); });
  comps.forEach(function(c, i){
    var g = d.createElementNS(NS, "g"), v = mv[parent[i]] || [0, 0];
    g.setAttribute("class", "td");
    g.setAttribute("style", "--dx:" + v[0].toFixed(1) + "px;--dy:" + v[1].toFixed(1) + "px;--i:" + Math.min(i, 40));
    c.forEach(function(e){ g.appendChild(e); });
    svg.appendChild(g);
  });
  var gn = d.createElementNS(NS, "g"); gn.setAttribute("class", "tdn");
  notes.forEach(function(e){ gn.appendChild(e); }); svg.appendChild(gn);
  return n;
}
function assembly(){
  var h = d.querySelector("h1.kicker");
  return /assembl|-test\b|-unit\b/.test(location.pathname) || (h && /組立|アセンブリ|ユニット|試験/.test(h.textContent));
}
var BTN = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M8 2v4M8 10v4M2 8h4M10 8h4"/></svg><span>分解して見る</span>';

var cands = [].slice.call(d.querySelectorAll("figure[data-td], .anat > figure.stage"));
if(assembly()) cands = cands.concat([].slice.call(d.querySelectorAll(".pvis > figure.stage")));
var tdSet = new Set(cands.filter(function(f){ return f.getAttribute("data-td") !== "off" && !off(f) && f.querySelector("svg.ilu"); }));

/* every large drawing on the page */
d.querySelectorAll("svg.ilu").forEach(function(svg){
  if(svg.closest(".thumb, .tile, .hero, .card, .gtip") || off(svg)) return;
  var fig = svg.closest("figure, .stage") || svg.parentNode;
  var td = tdSet.has(fig), co = null, mo = false, ctl = null;
  watch(fig, function(){
    if(td && explode(svg)){
      fig.classList.add("tdfig");
      var b = d.createElement("button"); b.type = "button"; b.className = "tdbtn"; b.setAttribute("aria-pressed", "false"); b.innerHTML = BTN;
      var cap = fig.querySelector("figcaption"); if(cap && cap.parentNode === fig) fig.insertBefore(b, cap); else fig.appendChild(b);
      ctl = { fig: fig, btn: b };
    }
    co = callouts(svg);
    mo = motion(svg);
    if(ctl){
      var touched = false, t1 = 0, t2 = 0, t3 = 0;
      var follow = co ? link(svg, co) : null;
      ctl.set = function(on){
        if(follow) follow(on);
        fig.classList.toggle("boom", on); clearTimeout(t3);
        ctl.btn.setAttribute("aria-pressed", on ? "true" : "false"); ctl.btn.querySelector("span").textContent = on ? "元に戻す" : "分解して見る";
      };
      ctl.btn.addEventListener("click", function(){ touched = true; clearTimeout(t1); clearTimeout(t2); ctl.set(!fig.classList.contains("boom")); });
      ctl.auto = function(){
        if(RM) return;
        t1 = setTimeout(function(){ if(!touched) ctl.set(true); }, (mo || co) ? 1500 : 450);
        t2 = setTimeout(function(){ if(!touched) ctl.set(false); }, (mo || co) ? 4300 : 3300);
      };
    }
    if(RM){ svg.classList.add("play"); if(co) co.show(); }
  }, function(){
    if(RM) return;
    svg.classList.add("play");
    if(co) co.show();
    if(ctl) ctl.auto();
  }, { threshold: td ? .55 : .35 });
});

/* ---- charts in the guides: lines draw in, areas and labels follow ---- */
d.querySelectorAll(".lab svg").forEach(function(svg){
  if(off(svg) || RM) return;
  var k = 0, lines = [];
  [].forEach.call(svg.querySelectorAll("path, polyline, line"), function(el){
    var cs = getComputedStyle(el);
    if(el.closest("defs") || /\bgrid\b/.test(cls(el)) || cs.stroke === "none" || dashed(el)) return;
    if(el.tagName !== "line" && cs.fill !== "none") return;
    var L = len(el); if(L < 40) return;
    el.style.setProperty("--len", L); el.style.setProperty("--n", k++); lines.push(el);
  });
  if(!lines.length) return;
  svg.classList.add("dr");
  watch(svg, function(){}, function(){
    svg.classList.add("play");
    setTimeout(function(){ svg.classList.add("done"); lines.forEach(function(el){ el.style.removeProperty("--len"); }); }, 1800 + k * 160);
  }, { threshold: .4 });
});

/* ---- process rail: a line runs down the operations and the one you are reading lights up ---- */
d.querySelectorAll(".oplist").forEach(function(ol){
  if(off(ol)) return;
  var ops = ol.querySelectorAll(".opx"); if(ops.length < 3) return;
  var rail = d.createElement("i"); rail.className = "oprail"; rail.setAttribute("aria-hidden", "true"); rail.innerHTML = "<b></b><s></s>"; ol.appendChild(rail); ol.classList.add("railed");
  var fill = rail.firstChild, dot = rail.lastChild, tick = false, curI = -1;
  function upd(){
    tick = false;
    var r = ol.getBoundingClientRect(), line = window.innerHeight * .45;
    var p = Math.max(0, Math.min(1, (line - r.top) / r.height));
    fill.style.transform = "scaleY(" + p + ")"; dot.style.transform = "translateY(" + (p * r.height) + "px)"; dot.style.opacity = p > 0 && p < 1 ? 1 : 0;
    var now = -1;
    for(var i = 0; i < ops.length; i++){ if(ops[i].getBoundingClientRect().top < line) now = i; }
    if(r.bottom < line) now = -1;
    if(now !== curI){
      if(curI >= 0) ops[curI].classList.remove("now");
      if(now >= 0) ops[now].classList.add("now");
      for(i = 0; i < ops.length; i++) ops[i].classList.toggle("past", i < now);
      curI = now;
    }
  }
  window.addEventListener("scroll", function(){ if(!tick){ tick = true; requestAnimationFrame(upd); } }, { passive: true });
  window.addEventListener("resize", upd); upd();
});

/* ---- quiet reveals for the inner pages (the home page has its own) ---- */
if(!RM && HAS_IO && !d.querySelector(".home")){
  var vh = window.innerHeight, rio = new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add("in"); rio.unobserve(e.target); } }); }, { rootMargin: "0px 0px -6% 0px", threshold: .05 });
  d.querySelectorAll("main .sec .hd, .opx, .notes li, .pblk, .legend li, .refs li, .grid-cards > *, .specs > div, .stats > div, details.qa").forEach(function(el){
    if(el.closest("[data-r], [data-motion=off]") || el.getBoundingClientRect().top < vh * .92) return;
    var sib = el.parentNode ? [].indexOf.call(el.parentNode.children, el) : 0;
    el.style.setProperty("--k", sib % 6); el.classList.add("rv"); rio.observe(el);
  });
}

/* ---- figures in the specs count up when they come into view ---- */
d.querySelectorAll(".specs > div > b, .stats > div > b").forEach(function(b){
  var t = b.textContent.trim(); if(!/^\d{1,3}(,\d{3})*$/.test(t) || RM) return;
  var to = +t.replace(/,/g, ""); if(to < 3) return;
  b.style.minWidth = b.offsetWidth + "px"; b.style.display = "inline-block";
  watch(b, function(){}, function(){
    var t0 = null;
    (function step(ts){ if(t0 === null) t0 = ts; var k = Math.min(1, (ts - t0) / 1300), e = 1 - Math.pow(1 - k, 4); b.textContent = Math.round(to * e).toLocaleString("ja-JP"); if(k < 1) requestAnimationFrame(step); })(performance.now());
  }, { threshold: .6 });
});
})();
