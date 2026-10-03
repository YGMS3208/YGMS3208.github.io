/* Operation training game. Loaded only on /machine-tools/{type}/training/ pages.
   Reads the scenario from #simdata, drives the machine drawing by data-* attributes on #sim. */
(function(){
  "use strict";
  var root = document.getElementById("sim"), dataEl = document.getElementById("simdata");
  if(!root || !dataEl) return;
  var S = JSON.parse(dataEl.textContent);
  var card = document.getElementById("simcard"), modal = document.getElementById("simmodal");
  var PEN = { 1: 10, 2: 20, 3: 35 }, NG = 3;
  var KEY_FX = {
    power: { power: true }, hyd: { lamp: "yellow" }, home: { homed: true, tool: "home" }, cycle: { lamp: "green" }, hold: { lamp: "yellow", chips: false }, reset: { lamp: "yellow", chips: false },
    spindle: { spindle: true }, sstop: { spindle: false, chips: false }, wheel: { spindle: true }, wstop: { spindle: false, chips: false },
    pump: { coolant: true, fluid: true }, bar: { bar: true }, wire: { wire: true }
  };
  var TOGGLE = { coolant: "coolant", door: "door", chuck: "clamp", magnet: "clamp", tail: "tail", wspin: "wspin", gas: "gas", line: "line", apc: "pallet", single: "single", dress: "dress" };
  var MODES = { mode_edit: "EDIT", mode_mem: "MEM", mode_mdi: "MDI", mode_jog: "JOG", mode_handle: "HANDLE" };
  var st = {}, snap = null, mode = "practice", si = -1, score = 100, seen = {}, hist = [], ngs = 0, stepNg = 0, t0 = 0, busy = false, nc = "—", jog = null, pos = 0;
  var store = (function(){ try { var k = "__t"; localStorage.setItem(k, k); localStorage.removeItem(k); return localStorage; } catch(e){ return null; } })();
  var bestKey = "mts-sim-" + S.slug;

  function $(id){ return document.getElementById(id); }
  function esc(s){ return String(s == null ? "" : s).replace(/[&<>"']/g, function(c){ return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c]; }); }
  function sv(v){ return typeof v === "boolean" ? (v ? "1" : "0") : String(v); }
  function clone(o){ return JSON.parse(JSON.stringify(o)); }
  function shuffle(a){ a = a.slice(); for(var i = a.length - 1; i > 0; i--){ var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }

  /* ---------- drawing state */
  var tfEls = Array.prototype.slice.call(root.querySelectorAll("[data-s]")).map(function(el){
    var specs = el.getAttribute("data-s").split("|").map(function(part){
      var i = part.indexOf(":"), map = {};
      part.slice(i + 1).split(";").forEach(function(kv){ var j = kv.indexOf("="); map[kv.slice(0, j)] = kv.slice(j + 1); });
      return { key: part.slice(0, i), map: map };
    });
    return { el: el, specs: specs };
  });
  function draw(){
    root.classList.toggle("jogging", !!jog);
    Object.keys(st).forEach(function(k){ root.setAttribute("data-" + k, sv(st[k])); });
    tfEls.forEach(function(t){
      t.el.style.transform = t.specs.map(function(sp){
        if(sp.key === "tool" && jog) return jogTf(sp.map);
        return sp.map[sv(st[sp.key])] || "";
      }).join(" ").trim();
    });
    screen();
  }
  function set(o){ if(!o) return; Object.keys(o).forEach(function(k){ st[k] = o[k]; }); }
  function screen(){
    $("simmode").textContent = st.power ? nc : "—";
    var s = !st.power ? "POWER OFF" : st.lamp === "red" ? "ALARM" : st.lamp === "green" ? "RUN" : st.lamp === "yellow" ? "READY" : "NOT READY";
    $("simstat").textContent = s;
    root.setAttribute("data-stat", s.replace(" ", "").toLowerCase());
    var p = $("simpos");
    if(jog) p.textContent = jog.axis + "  " + (-(jog.from - jog.gap)).toFixed(3) + "  相対";
    else p.textContent = st.power ? (st.homed ? "原点復帰 済" : "原点復帰 未") + (st.single ? "　SINGLE" : "") : "";
  }
  function msg(t){ $("simmsg").textContent = t || ""; }

  /* ---------- top bar */
  var phases = []; S.steps.forEach(function(s){ if(phases.indexOf(s.phase) < 0) phases.push(s.phase); });
  function bar(){
    var cur = si >= 0 && si < S.steps.length ? phases.indexOf(S.steps[si].phase) : si >= S.steps.length ? phases.length : -1;
    Array.prototype.forEach.call($("simph").children, function(el, i){ el.className = i < cur ? "done" : i === cur ? "on" : ""; });
    $("simsc").textContent = Math.max(0, score);
    $("siminc").textContent = hist.length;
  }

  /* ---------- panel keys */
  var keys = {};
  Array.prototype.forEach.call(root.querySelectorAll(".key"), function(b){ keys[b.getAttribute("data-b")] = b; b.addEventListener("click", function(){ press(b.getAttribute("data-b")); }); });
  function leds(){
    Object.keys(keys).forEach(function(k){
      var on = false;
      if(MODES[k]) on = st.power && nc === MODES[k];
      else if(k === "power") on = st.power;
      else if(k === "estop") on = !st.power || !st.estopOk;
      else if(k === "cycle") on = st.lamp === "green";
      else if(k === "hold") on = st.power && st.lamp === "yellow" && st.ran;
      else if(k === "spindle" || k === "wheel") on = st.spindle;
      else if(TOGGLE[k]) on = k === "door" ? st.door === "closed" : k === "apc" ? false : !!st[TOGGLE[k]];
      keys[k].classList.toggle("lit", !!on);
    });
  }
  function press(b){
    var s = S.steps[si];
    if(busy || !s || card.getAttribute("data-phase") !== "q"){ flashKey(b); return; }
    if(s.type !== "panel"){ fb("このステップでは、操作盤は使いません。", "info"); flashKey(b); return; }
    var exp = s.seq[pos];
    if(b === exp){
      applyKey(b); pos++;
      keys[b].classList.add("ok"); setTimeout(function(){ keys[b].classList.remove("ok"); }, 600);
      Array.prototype.forEach.call(card.querySelectorAll(".seq i"), function(el, i){ el.classList.toggle("on", i < pos); });
      root.querySelectorAll(".key.hint").forEach(function(k){ k.classList.remove("hint"); });
      draw(); leds();
      if(pos >= s.seq.length) setTimeout(success, 350);
      else fb(S.keys[b][0] + " ✓", "good");
      return;
    }
    if(s.traps && s.traps[b]){ incident(s.traps[b]); return; }
    ng(s.seq.indexOf(b) >= 0 ? "順番が違います。" : "今は「" + S.keys[b][0] + "」ではありません。");
    if(mode === "practice" && keys[exp]) keys[exp].classList.add("hint");
  }
  function flashKey(b){ var k = keys[b]; if(!k) return; k.classList.add("nope"); setTimeout(function(){ k.classList.remove("nope"); }, 300); }
  function applyKey(b){
    if(b === "estop"){ st.estopOk = true; msg(""); return; }
    if(MODES[b]){ nc = MODES[b]; return; }
    if(KEY_FX[b]) set(KEY_FX[b]);
    if(b === "cycle") st.ran = true;
    var t = TOGGLE[b];
    if(t === "door") st.door = st.door === "open" ? "closed" : "open";
    else if(t === "pallet"){ st.pallet = st.pallet === "A" ? "B" : "A"; root.setAttribute("data-swap", "1"); setTimeout(function(){ root.removeAttribute("data-swap"); }, 1100); }
    else if(t) st[t] = !st[t];
  }

  /* ---------- step card */
  function fb(t, kind){ var el = card.querySelector(".fb"); if(el){ el.className = "fb " + (kind || ""); el.textContent = t; } }
  function head(s){
    return "<div class=\"sh\"><span class=\"ph\">" + esc(s.phase) + "</span><span class=\"no\" lang=\"en\">STEP " + (si + 1) + " / " + S.steps.length + "</span></div><h3>" + esc(s.title) + "</h3><p class=\"stx\">" + esc(s.text) + "</p>";
  }
  function foot(s){
    return "<p class=\"fb\" role=\"status\" aria-live=\"polite\"></p>" + (mode === "practice" && s.hint ? "<details class=\"hint\"><summary>ヒント</summary><p>" + esc(s.hint) + "</p></details>" : "");
  }
  function startStep(){
    jog = null; pos = 0; stepNg = 0;
    var s = S.steps[si];
    set(s.pre); snap = clone(st); draw(); leds(); bar();
    card.setAttribute("data-phase", "q");
    root.classList.toggle("panelmode", s.type === "panel");
    var h = head(s), i;
    if(s.type === "check"){
      h += "<div class=\"chk\">" + shuffle(s.items.map(function(x, j){ return j; })).map(function(j){ return "<button type=\"button\" class=\"opt\" aria-pressed=\"false\" data-i=\"" + j + "\"><i></i>" + esc(s.items[j].t) + "</button>"; }).join("") + "</div><button type=\"button\" class=\"cta go\">確認完了</button>";
    } else if(s.type === "panel"){
      h += "<p class=\"seq\">" + s.seq.map(function(){ return "<i></i>"; }).join("") + "</p><p class=\"pnote\">" + (window.matchMedia("(max-width: 979px)").matches ? "下の" : "左の") + "操作盤のボタンを、正しい順に押してください。</p>";
    } else if(s.type === "choice"){
      h += "<div class=\"chs\">" + shuffle(s.options.map(function(o, j){ return j; })).map(function(j){ return "<button type=\"button\" class=\"opt\" data-i=\"" + j + "\">" + esc(s.options[j].t) + "</button>"; }).join("") + "</div>";
    } else if(s.type === "input"){
      h += "<form class=\"inp\" novalidate><label for=\"simin\">" + esc(s.label) + "</label><div><input id=\"simin\" type=\"text\" inputmode=\"decimal\" autocomplete=\"off\" spellcheck=\"false\"><span>" + esc(s.unit) + "</span></div><button type=\"submit\" class=\"cta\">入力する</button></form>";
    } else if(s.type === "order"){
      var it = s.items.map(function(x, j){ return j; }), sh = shuffle(it);
      for(i = 0; i < 6 && sh.join() === it.join(); i++) sh = shuffle(it);
      h += "<div class=\"ord\">" + sh.map(function(j){ return "<button type=\"button\" class=\"opt\" data-i=\"" + j + "\"><em></em>" + esc(s.items[j]) + "</button>"; }).join("") + "</div><button type=\"button\" class=\"lnk sm clr\">選び直す</button>";
    } else if(s.type === "jog"){
      var off = Math.round((s.tol + 0.017) * 1000) / 1000;
      jog = { axis: s.axis, from: s.from + off, gap: s.from + off, step: 0.1, deg: 0 };
      h += "<div class=\"jog\"><div class=\"gap\"><div class=\"gbar\"><i></i><b></b></div><div class=\"gl\"><span>10mm</span><span>1</span><span>0.1</span><span>0.01</span><span>接触</span></div></div>" +
        "<div class=\"jrow\"><div class=\"mul\" role=\"radiogroup\" aria-label=\"ハンドルの倍率\">" + [["0.001", "×1"], ["0.01", "×10"], ["0.1", "×100"]].map(function(m){ return "<button type=\"button\" role=\"radio\" aria-checked=\"" + (m[0] === "0.1") + "\" data-m=\"" + m[0] + "\"><b>" + m[1] + "</b><small>" + m[0] + "mm</small></button>"; }).join("") + "</div>" +
        "<div class=\"mpg\"><button type=\"button\" class=\"jb\" data-d=\"1\" aria-label=\"離す（＋）\">＋</button><span class=\"dial\" aria-hidden=\"true\"><i></i></span><button type=\"button\" class=\"jb\" data-d=\"-1\" aria-label=\"近づける（−）\">−</button></div></div>" +
        "<button type=\"button\" class=\"cta go\">位置を決定</button></div>";
    }
    card.innerHTML = h + foot(s);
    card.classList.remove("res");
    wire(s);
    if(s.type === "jog") jogDraw();
    draw();
  }
  function wire(s){
    if(s.type === "check"){
      card.querySelectorAll(".chk .opt").forEach(function(b){ b.addEventListener("click", function(){ b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true")); b.classList.remove("miss", "bad"); }); });
      card.querySelector(".go").addEventListener("click", function(){
        var sel = {}; card.querySelectorAll(".chk .opt").forEach(function(b){ if(b.getAttribute("aria-pressed") === "true") sel[b.getAttribute("data-i")] = 1; });
        var miss = [], bad = [];
        s.items.forEach(function(x, j){ if(x.req && !sel[j]) miss.push(j); if(!x.req && sel[j]) bad.push(j); });
        if(miss.length){
          miss.forEach(function(j){ var b = card.querySelector(".chk .opt[data-i=\"" + j + "\"]"); if(b) b.classList.add("miss"); });
          var withInc = miss.filter(function(j){ return s.items[j].inc; })[0];
          if(withInc !== undefined) return incident(s.items[withInc].inc);
          if(s.miss) return incident(s.miss);
          return ng("確認が足りない項目があります。");
        }
        if(bad.length){ bad.forEach(function(j){ var b = card.querySelector(".chk .opt[data-i=\"" + j + "\"]"); if(b) b.classList.add("bad"); }); return ng(s.items[bad[0]].ng); }
        success();
      });
    } else if(s.type === "choice"){
      card.querySelectorAll(".chs .opt").forEach(function(b){ b.addEventListener("click", function(){
        if(busy || b.disabled) return;
        var o = s.options[+b.getAttribute("data-i")];
        if(o.ok){ b.classList.add("right"); success(); }
        else if(o.inc){ b.classList.add("wrong"); incident(o.inc); }
        else { b.classList.add("wrong"); b.disabled = true; ng(o.ng); }
      }); });
    } else if(s.type === "input"){
      var f = card.querySelector(".inp"), inp = f.querySelector("input");
      f.addEventListener("submit", function(e){
        e.preventDefault(); if(busy) return;
        var raw = inp.value.replace(/[０-９．－]/g, function(c){ return c === "．" ? "." : c === "－" ? "-" : String.fromCharCode(c.charCodeAt(0) - 0xFEE0); }).replace(/[−ーｰ―‐]/g, "-").replace(/[,，\s]/g, "");
        var v = parseFloat(raw);
        if(!/^[-+]?(\d+\.?\d*|\.\d+)$/.test(raw) || isNaN(v)){ fb("数値を入力してください。", "info"); return; }
        if(v >= s.ok[0] - 1e-9 && v <= s.ok[1] + 1e-9){ success(); return; }
        var cs = s.cases || [];
        for(var i = 0; i < cs.length; i++){
          var c = cs[i];
          if(("lt" in c && v < c.lt) || ("gt" in c && v > c.gt)){ if(c.inc) return incident(c.inc); return ng(c.ng); }
        }
        ng(s.ng);
      });
      setTimeout(function(){ try { inp.focus({ preventScroll: true }); } catch(e){} }, 50);
    } else if(s.type === "order"){
      var picked = [];
      card.querySelectorAll(".ord .opt").forEach(function(b){ b.addEventListener("click", function(){
        if(busy || b.classList.contains("pk")) return;
        picked.push(+b.getAttribute("data-i")); b.classList.add("pk"); b.querySelector("em").textContent = picked.length;
        if(picked.length === s.items.length){
          var ok = picked.every(function(x, i){ return x === i; });
          if(ok) success();
          else if(s.inc) incident(s.inc);
          else { ng(s.ng); setTimeout(clear, 900); }
        }
      }); });
      var clear = function(){ picked = []; card.querySelectorAll(".ord .opt").forEach(function(b){ b.classList.remove("pk"); b.querySelector("em").textContent = ""; }); };
      card.querySelector(".clr").addEventListener("click", clear);
    } else if(s.type === "jog"){
      card.querySelectorAll(".mul button").forEach(function(b){ b.addEventListener("click", function(){ jog.step = +b.getAttribute("data-m"); card.querySelectorAll(".mul button").forEach(function(x){ x.setAttribute("aria-checked", String(x === b)); }); }); });
      card.querySelectorAll(".jb").forEach(function(b){
        var timer = null, d = +b.getAttribute("data-d");
        var stop = function(){ clearTimeout(timer); clearInterval(timer); timer = null; };
        b.addEventListener("pointerdown", function(e){ e.preventDefault(); if(busy) return; tick(d); stop(); timer = setTimeout(function(){ timer = setInterval(function(){ if(busy || !jog) return stop(); tick(d); }, 85); }, 380); });
        ["pointerup", "pointerleave", "pointercancel"].forEach(function(ev){ b.addEventListener(ev, stop); });
        b.addEventListener("keydown", function(e){ if(e.key === "Enter" || e.key === " "){ e.preventDefault(); tick(d); } });
      });
      card.querySelector(".go").addEventListener("click", function(){
        if(busy) return;
        if(jog.gap < -1e-9) return ng("刃先がワークに食い込んでいます。＋側に少し戻してください。");
        if(jog.gap > s.tol + 1e-9) return ng("まだ離れています（あと" + (jog.gap < 0.1 ? "わずか" : "少し") + "）。");
        success();
      });
    }
  }
  function tick(d){
    var s = S.steps[si];
    if(!jog || busy) return;
    var g = Math.round((jog.gap + d * jog.step) * 1000) / 1000;
    jog.deg += d * (jog.step >= 0.1 ? 36 : jog.step >= 0.01 ? 18 : 9);
    if(d < 0 && g < 0 && (jog.step >= 0.1 || -g > 0.01 + 1e-9)){ jog.gap = g; jogDraw(); draw(); incident(s.inc); return; }
    if(d < 0 && g < 0){ jog.gap = g; jogDraw(); draw(); ng("刃先が軽く触れました。＋側に戻してください。"); return; }
    if(g > jog.from + 5) g = jog.from + 5;
    jog.gap = g; jogDraw(); draw();
  }
  function jogPos(g){ var lg = Math.log(1 + Math.max(g, 0) * 100) / Math.log(1 + 10 * 100); return Math.max(0, Math.min(1, lg)); }
  function jogDraw(){
    var el = card.querySelector(".gbar"); if(!el || !jog) return;
    var p = jogPos(jog.gap);
    el.querySelector("i").style.width = (100 - p * 100) + "%";
    el.classList.toggle("in", jog.gap >= 0 && jog.gap <= S.steps[si].tol + 1e-9);
    el.classList.toggle("over", jog.gap < 0);
    var dl = card.querySelector(".dial i"); if(dl) dl.style.transform = "rotate(" + jog.deg + "deg)";
  }
  function parseT(t){ var m = /translate\((-?[\d.]+)px,\s*(-?[\d.]+)px\)/.exec(t || ""); return m ? [+m[1], +m[2]] : [0, 0]; }
  function jogTf(map){
    var a = parseT(map.home), b = parseT(map.near), k = Math.min(1, jogPos(jog.gap) * 1.15);
    var sc = /scale\(([\d.]+)\)/.exec(map.home || ""), s0 = sc ? +sc[1] : 1;
    return "translate(" + (b[0] + (a[0] - b[0]) * k).toFixed(1) + "px," + (b[1] + (a[1] - b[1]) * k).toFixed(1) + "px)" + (s0 !== 1 ? " scale(" + (1 + (s0 - 1) * k).toFixed(3) + ")" : "");
  }

  /* ---------- outcomes */
  function ng(t){
    stepNg++; ngs++;
    if(stepNg <= 2){ score -= NG; bar(); }
    fb(t + (stepNg <= 2 ? "（−" + NG + "）" : ""), "warn");
    card.classList.remove("shake"); void card.offsetWidth; card.classList.add("shake");
  }
  function success(){
    var s = S.steps[si];
    jog = null; set(s.set); draw(); leds(); bar();
    card.setAttribute("data-phase", "ok");
    root.classList.remove("panelmode");
    root.querySelectorAll(".key.hint").forEach(function(k){ k.classList.remove("hint"); });
    var ia = card.querySelectorAll(".chk,.chs,.inp,.ord,.jog,.seq,.pnote,.go,.clr,.hint,.fb");
    Array.prototype.forEach.call(ia, function(el){ if(!el.classList.contains("chs")) el.remove(); else el.classList.add("done"); });
    card.insertAdjacentHTML("beforeend", "<div class=\"okp\"><p class=\"okh\"><i></i>OK</p><p>" + esc(s.explain) + "</p><button type=\"button\" class=\"cta nx\">" + (si + 1 < S.steps.length ? "次のステップへ" : "結果を見る") + "</button></div>");
    var nx = card.querySelector(".nx");
    nx.addEventListener("click", next);
    try { nx.focus({ preventScroll: true }); } catch(e){}
  }
  function next(){ si++; if(si >= S.steps.length) return finish(); startStep(); scrollCard(); }
  function scrollCard(){ var r = card.getBoundingClientRect(); if(r.top < 60 || r.top > window.innerHeight * .7) card.scrollIntoView({ behavior: "smooth", block: "start" }); }
  function incident(id){
    var I = S.incidents[id]; if(!I || busy) return;
    busy = true;
    var first = !seen[id];
    if(first){ seen[id] = 1; score -= PEN[I.sev]; hist.push(id); }
    bar();
    root.setAttribute("data-fx", I.fx);
    if(I.sev >= 2 || I.fx === "alarm"){ st.lamp = "red"; }
    if(I.fx === "crash" || I.fx === "fly" || I.fx === "burst") { st.chips = false; }
    draw(); leds();
    var tag = { alarm: "ALARM", deform: "不良", burn: "研削焼け", wirebreak: "ワイヤ断線", slip: "ずれ", chatter: "ビビり", leak: "液漏れ" }[I.fx];
    $("simtag").textContent = tag || "";
    msg(I.fx === "alarm" ? "ALARM" : "");
    setTimeout(function(){ openModal(I, first); }, I.fx === "alarm" ? 700 : 1500);
  }
  function openModal(I, first){
    modal.innerHTML = "<div class=\"md\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"simmdt\"><p class=\"eyebrow\" lang=\"en\">TROUBLE</p><p class=\"tags\"><span class=\"sev s" + I.sev + "\">" + esc(S.sev[I.sev]) + "</span><span>" + esc(S.fx[I.fx] || "") + "</span>" + (first ? "<span class=\"pen\">−" + PEN[I.sev] + "点</span>" : "<span class=\"pen\">（減点済み）</span>") + "</p>" +
      "<h3 id=\"simmdt\">" + esc(I.title) + "</h3><dl><div><dt>現象</dt><dd>" + esc(I.what) + "</dd></div><div><dt>原因</dt><dd>" + esc(I.why) + "</dd></div><div><dt>損失</dt><dd>" + esc(I.loss) + "</dd></div><div><dt>対策</dt><dd>" + esc(I.prevent) + "</dd></div></dl>" +
      "<button type=\"button\" class=\"cta\">状態を戻して、やり直す</button></div>";
    modal.hidden = false;
    document.documentElement.classList.add("simlock");
    var b = modal.querySelector("button");
    b.addEventListener("click", closeModal);
    try { b.focus({ preventScroll: true }); } catch(e){}
  }
  function closeModal(){
    modal.hidden = true; modal.innerHTML = "";
    document.documentElement.classList.remove("simlock");
    root.removeAttribute("data-fx"); $("simtag").textContent = ""; msg("");
    busy = false;
    st = clone(snap);
    startStep();
    scrollCard();
  }
  document.addEventListener("keydown", function(e){ if(e.key === "Escape" && !modal.hidden) closeModal(); });

  /* ---------- start / finish */
  function begin(m){
    mode = m; si = 0; score = 100; seen = {}; hist = []; ngs = 0; nc = "—"; t0 = Date.now();
    st = clone(S.init); st.estopOk = false; st.ran = false;
    root.setAttribute("data-mode", m); root.classList.add("live");
    startStep(); scrollCard();
  }
  function grade(p){ return p >= 95 ? "S" : p >= 80 ? "A" : p >= 60 ? "B" : "C"; }
  function finish(){
    var p = Math.max(0, score), g = grade(p), sec = Math.round((Date.now() - t0) / 1000);
    card.setAttribute("data-phase", "end"); bar();
    var best = null;
    if(store){ try { best = JSON.parse(store.getItem(bestKey) || "null"); if(!best || p > best.p) store.setItem(bestKey, JSON.stringify({ p: p, g: g, m: mode })); } catch(e){} }
    var msgs = { S: "完璧です。現場の人と同じ目線で機械を見られています。", A: "よくできました。起きたトラブルの「防ぐには」を読み返しておきましょう。", B: "もう一歩。トラブルの原因を確かめて、もう一度挑戦しましょう。", C: "機械が何度も止まりました。練習モードのヒントを見ながら、手順の理由を確かめましょう。" };
    card.classList.add("res");
    card.innerHTML = "<p class=\"eyebrow\" lang=\"en\">RESULT · " + (mode === "exam" ? "EXAM" : "PRACTICE") + "</p><div class=\"rs\"><div class=\"gr g" + g + "\" lang=\"en\">" + g + "</div><div><b class=\"tn\">" + p + "</b><span>点</span><p>" + Math.floor(sec / 60) + "分" + (sec % 60) + "秒　トラブル " + hist.length + "件　軽いミス " + ngs + "回</p>" + (best && best.p > p ? "<p>自己ベスト " + best.p + "点（" + best.g + "）</p>" : "") + "</div></div>" +
      "<p class=\"rm\">" + msgs[g] + "</p>" +
      (hist.length ? "<p class=\"h4\">起きたトラブル</p><ul class=\"rl\">" + hist.map(function(id){ var I = S.incidents[id]; return "<li><span class=\"sev s" + I.sev + "\">" + esc(S.sev[I.sev]) + "</span><a href=\"#" + id + "\">" + esc(I.title) + "</a></li>"; }).join("") + "</ul>" : "<p class=\"rm\">トラブルはゼロ。機械も工具も無傷です。</p>") +
      "<div class=\"modes\"><button type=\"button\" class=\"cta\" data-start=\"" + (mode === "practice" ? "exam" : "practice") + "\">" + (mode === "practice" ? "本番モードで挑戦" : "練習モードで復習") + "</button><button type=\"button\" class=\"cta ghost\" data-start=\"" + mode + "\">もう一度</button></div>" +
      "<p class=\"note\"><a class=\"lnk sm\" href=\"/machine-tools/training/\">ほかの機械に挑戦する</a></p>";
    root.classList.remove("live", "panelmode");
    wireStart();
    scrollCard();
  }
  function wireStart(){ card.querySelectorAll("[data-start]").forEach(function(b){ b.addEventListener("click", function(){ begin(b.getAttribute("data-start")); }); }); }

  st = clone(S.init); st.estopOk = false; draw(); leds();
  if(store){ try { var b0 = JSON.parse(store.getItem(bestKey) || "null"); if(b0) card.querySelector(".note").insertAdjacentHTML("beforebegin", "<p class=\"best\">自己ベスト " + b0.p + "点（" + esc(b0.g) + "）</p>"); } catch(e){} }
  wireStart();
})();
