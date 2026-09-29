/* 自動車製造工程図鑑 — runtime for the static site: menu, search, tabs, carousels. */
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
    IDX.o.forEach(function(o){ if(out.length < 12 && has(o[2], q)) out.push("<a href=\"" + o[5] + "\">" + hl(o[2], q) + " <small>" + esc(o[0]) + "・" + o[1] + "</small></a>"); });
    var all = "/search/?q=" + encodeURIComponent(raw);
    qs.innerHTML = "<p>SUGGESTIONS</p>" + (out.join("") || "<a href=\"" + all + "\">「" + esc(raw) + "」で全体を検索</a>") + (out.length ? "<a class=\"all\" href=\"" + all + "\">すべての結果を見る</a>" : "");
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
    d.title = "「" + raw + "」の検索結果｜自動車製造工程図鑑";
    sres.innerHTML = "<p class=\"sub\">検索しています…</p>";
    loadIdx(function(){
      var rp = IDX.p.filter(function(p){ return has(p[0], q) || has(p[1], q) || has(p[2], q); });
      var rc = IDX.c.filter(function(c){ return has(c[0], q) || has(c[1], q); });
      var ro = IDX.o.filter(function(o){ return has(o[2], q) || has(o[3], q) || has(o[4], q); });
      var rm = IDX.r.filter(function(r){ return has(r[1], q) || has(r[2], q); });
      var rk = IDX.k.filter(function(k){ return has(k[0], q); });
      var h = "<h2 class=\"sr\">検索結果</h2><div class=\"stats\" style=\"margin-bottom:12px\"><div><b>" + rp.length + "</b><span>部品</span></div><div><b>" + rc.length + "</b><span>設備</span></div><div><b>" + ro.length + "</b><span>工程</span></div><div><b>" + rm.length + "</b><span>仕様・メーカー</span></div></div>";
      if(!(rp.length + rc.length + ro.length + rm.length + rk.length)){ sres.innerHTML = h + "<p class=\"sub\" style=\"margin-top:32px\">当てはまる項目がありません。表記を変えるか、短い言葉で試してください（例：研削、プレス）。</p>"; return; }
      if(rk.length) h += "<div class=\"gblock\"><h3>加工法<small>" + rk.length + "</small></h3>" + rk.map(function(k){ return "<a class=\"use\" href=\"" + k[1] + "\"><span class=\"w\"><b>" + hl(k[0], q) + "</b></span></a>"; }).join("") + "</div>";
      if(rc.length) h += "<div class=\"gblock\"><h3>設備<small>" + rc.length + "</small></h3>" + rc.map(function(c){ return "<a class=\"use\" href=\"" + c[2] + "\"><span class=\"w\"><b>" + hl(c[0], q) + "</b><small>" + esc(c[3]) + "</small></span><span class=\"s\">" + hl(c[1], q) + "</span><span class=\"m\"></span></a>"; }).join("") + "</div>";
      if(rp.length) h += "<div class=\"gblock\"><h3>部品<small>" + rp.length + "</small></h3>" + rp.map(function(p){ return "<a class=\"use\" href=\"" + p[3] + "\"><span class=\"w\"><b>" + hl(p[0], q) + "</b><small>" + esc(p[4]) + "</small></span><span class=\"s\">" + hl(p[2], q) + "</span><span class=\"m\">" + hl(p[1], q) + "</span></a>"; }).join("") + "</div>";
      if(rm.length) h += "<div class=\"gblock\"><h3>設備の仕様・メーカー<small>" + rm.length + "</small></h3>" + rm.map(function(r){ return "<a class=\"use\" href=\"" + r[6] + "\"><span class=\"w\"><b>" + esc(r[0]) + " <span class=\"role" + (r[7] === "i" ? " i" : "") + "\">" + (r[7] === "i" ? "検査" : "設備") + "</span></b><small>" + esc(r[3]) + " · <span class=\"tn\">" + r[4] + "</span>" + esc(r[5]) + "</small></span><span class=\"s\">" + hl(r[1], q) + "</span><span class=\"m\">" + hl(r[2], q) + "</span></a>"; }).join("") + "</div>";
      if(ro.length) h += "<div class=\"gblock\"><h3>工程<small>" + ro.length + "</small></h3>" + ro.map(function(o){ return "<a class=\"use\" href=\"" + o[5] + "\"><span class=\"w\"><b>" + esc(o[0]) + "</b><small><span class=\"tn\">" + o[1] + "</span>" + hl(o[2], q) + "</small></span><span class=\"s\">" + hl(o[3], q) + "</span><span class=\"m\">" + hl(o[4], q) + "</span></a>"; }).join("") + "</div>";
      sres.innerHTML = h;
    });
  }
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
})();
