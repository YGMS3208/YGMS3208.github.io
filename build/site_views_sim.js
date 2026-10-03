/* ===================================================================== operation training (/machine-tools/{type}/training/)
   Build-time views: the animated machine drawings, the control panel markup and the static
   explanation sections. The game itself runs in site_sim.js (loaded only on training pages). */
var SIM = D.sim || {};
var SIM_ORDER = (D.mt ? D.mt.types : []).map(function(t){ return t.slug; }).filter(function(s){ return SIM[s]; });

/* ---------- panel keys: id → [label, english, kind] */
var SKEY = {
  power: ["主電源", "POWER", "pw"], estop: ["非常停止", "E-STOP", "es"], hyd: ["運転準備", "READY", ""], home: ["原点復帰", "HOME", ""],
  mode_edit: ["編集", "EDIT", "md"], mode_mem: ["メモリ運転", "MEMORY", "md"], mode_mdi: ["MDI", "MDI", "md"], mode_jog: ["ジョグ", "JOG", "md"], mode_handle: ["ハンドル", "HANDLE", "md"],
  single: ["シングルブロック", "SINGLE", "tg"], dry: ["ドライラン", "DRY RUN", "tg"], cycle: ["サイクルスタート", "CYCLE START", "go"], hold: ["フィードホールド", "FEED HOLD", "ho"], reset: ["リセット", "RESET", ""],
  spindle: ["主軸起動", "SPINDLE", ""], sstop: ["主軸停止", "SP STOP", ""], coolant: ["クーラント", "COOLANT", "tg"], door: ["ドア開閉", "DOOR", "tg"],
  chuck: ["チャック開閉", "CHUCK", "tg"], tail: ["心押台", "TAILSTOCK", "tg"], bar: ["棒材送り", "BAR FEED", ""], tool_unclamp: ["工具アンクランプ", "TOOL UNCLAMP", ""],
  apc: ["パレット交換", "APC", ""], wheel: ["といし起動", "WHEEL", ""], wstop: ["といし停止", "WHEEL STOP", ""], wspin: ["工作物回転", "WORK ROT", "tg"],
  dress: ["ドレス", "DRESS", ""], magnet: ["マグネット", "MAGNET", "tg"], pump: ["加工液", "PUMP", "tg"], wire: ["自動結線", "WIRE", ""],
  gas: ["アシストガス", "ASSIST GAS", "tg"], beam: ["レーザ出力", "BEAM", ""], line: ["ライン起動", "LINE", "tg"], conv: ["チップコンベヤ", "CONVEYOR", "tg"],
  measure: ["計測", "MEASURE", ""], lube: ["手動給油", "LUBE", ""]
};
var SKEY_GROUPS = [["power", "estop"], ["hyd", "home", "reset"], ["mode_edit", "mode_mem", "mode_mdi", "mode_jog", "mode_handle"], ["single", "dry"],
  ["spindle", "sstop", "wheel", "wstop", "wspin", "dress"], ["door", "chuck", "tail", "bar", "magnet", "tool_unclamp", "apc", "coolant", "pump", "wire", "gas", "beam", "line", "conv", "measure", "lube"], ["cycle", "hold"]];
var SFX = { crash: "衝突", fly: "飛散", burst: "破裂", fire: "発火", smoke: "発煙・過熱", alarm: "アラーム停止", chatter: "ビビり", slip: "ずれ・滑り", deform: "不良", wirebreak: "断線", burn: "研削焼け", leak: "液漏れ", hazard: "人への危険" };
var SSEV = { 1: "軽微", 2: "中程度", 3: "重大" };
var SIM_INIT = { power: false, lamp: "off", door: "open", homed: false, single: false, work: "none", clamp: false, tool: "home", spindle: false, coolant: false, chips: false, chatter: false,
  tail: false, bar: false, mill: false, tilt: 0, probe: false, pallet: "A", dress: false, wspin: false, wire: false, fluid: false, gas: false, line: false, jaws: false };

/* ---------- tiny svg helpers */
function sv(v){ return typeof v === "boolean" ? (v ? "1" : "0") : String(v); }
function sR(x, y, w, h, f, ex){ return "<rect x=\"" + x + "\" y=\"" + y + "\" width=\"" + w + "\" height=\"" + h + "\" fill=\"" + f + "\"" + (ex || "") + "/>"; }
function sC(cx, cy, r, f, ex){ return "<circle cx=\"" + cx + "\" cy=\"" + cy + "\" r=\"" + r + "\" fill=\"" + f + "\"" + (ex || "") + "/>"; }
function sP(d, f, ex){ return "<path d=\"" + d + "\" fill=\"" + f + "\"" + (ex || "") + "/>"; }
function sL(x1, y1, x2, y2, c, w, ex){ return "<line x1=\"" + x1 + "\" y1=\"" + y1 + "\" x2=\"" + x2 + "\" y2=\"" + y2 + "\" stroke=\"" + c + "\" stroke-width=\"" + (w || 1) + "\"" + (ex || "") + "/>"; }
function sG(cls, inner, s, ex){ return "<g" + (cls ? " class=\"" + cls + "\"" : "") + (s ? " data-s=\"" + s + "\"" : "") + (ex || "") + ">" + inner + "</g>"; }
function sOrg(x, y){ return " style=\"transform-origin:" + x + "px " + y + "px\""; }
var sCN = 0;
function sStripe(x, y, w, h, dir, cls, op, gap, rx){
  var id = "svc" + (++sCN), g = gap || 14, s = "", o = " opacity=\"" + (op || .2) + "\"";
  if(dir === "v") for(var yy = y - g * 2; yy < y + h + g; yy += g) s += sR(x, yy, w, 2.2, "#fff", o);
  else for(var xx = x - g * 2; xx < x + w + g; xx += g) s += sR(xx, y, 2.2, h, "#fff", o);
  return "<clipPath id=\"" + id + "\">" + sR(x, y, w, h, "#000", rx ? " rx=\"" + rx + "\"" : "") + "</clipPath><g clip-path=\"url(#" + id + ")\"><g class=\"" + (dir === "v" ? "spv " : "sph ") + cls + "\" style=\"--g:" + g + "px\">" + s + "</g></g>";
}
function sDisc(cx, cy, r, fill, cls, marks, hub){
  var s = sC(cx, cy, r, fill), n = marks || 8;
  for(var i = 0; i < n; i++){ var a = i * Math.PI * 2 / n; s += sL((cx + Math.cos(a) * r * .38).toFixed(1), (cy + Math.sin(a) * r * .38).toFixed(1), (cx + Math.cos(a) * r * .92).toFixed(1), (cy + Math.sin(a) * r * .92).toFixed(1), "#fff", 1.4, " opacity=\".22\""); }
  if(hub) s += sC(cx, cy, hub, "url(#sgDv)") + sC(cx, cy, hub * .42, "#1d2025");
  return sG("rot " + cls, s);
}
function sGearPath(cx, cy, r, n, d, inner){
  var p = "", step = Math.PI * 2 / n;
  for(var i = 0; i < n; i++){
    var a = i * step, pts = [[a, r - d], [a + step * .18, r], [a + step * .5, r], [a + step * .68, r - d]];
    if(inner) pts = [[a, r + d], [a + step * .18, r], [a + step * .5, r], [a + step * .68, r + d]];
    pts.forEach(function(q, j){ p += (i === 0 && j === 0 ? "M" : "L") + (cx + Math.cos(q[0]) * q[1]).toFixed(1) + "," + (cy + Math.sin(q[0]) * q[1]).toFixed(1); });
  }
  return p + "Z";
}
/* chips / sparks / discharge flashes, drawn at x,y and thrown toward angle a */
function sEmit(x, y, a, type){
  var s = "", i;
  if(type === "spark"){
    for(i = 0; i < 14; i++){ var r = -28 + (i * 37) % 56, L = 10 + (i * 7) % 14; s += "<g transform=\"rotate(" + r + ")\"><line class=\"sk\" x1=\"0\" y1=\"0\" x2=\"" + L + "\" y2=\"0\" stroke=\"" + (i % 3 ? "#ffd27a" : "#fff3c4") + "\" stroke-width=\"" + (i % 4 ? 1.6 : 2.2) + "\" stroke-linecap=\"round\" style=\"animation-delay:-" + (i * .047).toFixed(2) + "s\"/></g>"; }
  } else if(type === "flash"){
    for(i = 0; i < 9; i++) s += "<circle class=\"fsh\" cx=\"" + ((i % 3) - 1) * 2 + "\" cy=\"" + (-22 + i * 5.5).toFixed(1) + "\" r=\"" + (2 + i % 3) + "\" fill=\"#e3f1ff\" style=\"animation-delay:-" + ((i * .37) % 1).toFixed(2) + "s\"/>";
  } else {
    for(i = 0; i < 9; i++){ var dx = 26 + (i * 17) % 44, dy = -10 + (i * 23) % 70; s += "<path class=\"ch\" d=\"M0 0c2-3 6-3 6 0s-4 4-5 1\" fill=\"none\" stroke=\"" + (i % 3 ? "#c8a46a" : "#8fa3c9") + "\" stroke-width=\"1.6\" style=\"--dx:" + dx + "px;--dy:" + dy + "px;animation-delay:-" + (i * .11).toFixed(2) + "s\"/>"; }
  }
  return "<g class=\"em em-" + (type || "chip") + "\" transform=\"translate(" + x + " " + y + ") rotate(" + (a || 0) + ")\">" + s + "</g>";
}
function sCool(d, oil){ return "<path class=\"cl\" d=\"" + d + "\" stroke=\"" + (oil ? "#e2b75a" : "#9ad7ff") + "\"/>"; }
function sDoor(tint){
  var s = sR(6, 6, 628, 388, tint || "url(#sgGl)", " rx=\"6\"") + sR(6, 6, 628, 388, "none", " rx=\"6\" stroke=\"#c9ccd1\" stroke-width=\"10\" opacity=\".9\"") +
    sR(612, 150, 10, 100, "#e9eaec", " rx=\"5\"") +
    sG("crk", sP("M320 170l-34-40M320 170l40-22M320 170l8 46M320 170l-42 18M286 130l-18-6M360 148l14-22M328 216l-10 24M278 188l-16 22", "none", " stroke=\"#fff\" stroke-width=\"1.4\" opacity=\".85\""));
  return sG("door", s, "door:open=translate(-640px,0px);closed=");
}

/* ---------- the 18 machine drawings (viewBox 0 0 640 400). Each returns {svg, P:[x,y] trouble point, W:[x,y] wheel/rotor centre, chip, vars} */
var SVIS = {};
function sBase(){ return sR(0, 0, 640, 400, "url(#sgBg)") + sL(0, 330, 640, 330, "#000", 1, " opacity=\".4\"") + sR(0, 331, 640, 69, "#111317") + sR(0, 0, 640, 3, "#fff", " opacity=\".06\""); }

SVIS.lathe = function(){
  var wk = sG("raw", sR(166, 154, 170, 72, "url(#sgSh)") + sStripe(166, 154, 170, 72, "v", "r-s")) +
    sG("fn", sR(166, 154, 96, 72, "url(#sgSh)") + sR(262, 163, 74, 54, "url(#sgSh)") + sStripe(166, 154, 170, 72, "v", "r-s")) + sR(166, 154, 170, 72, "url(#sgBrn)", " class=\"burn\"");
  var poly = "";
  for(var i = 0; i < 12; i++){ var a = (i * 30 + 15) * Math.PI / 180; poly += (i ? "L" : "M") + (520 + Math.cos(a) * 66).toFixed(1) + " " + (96 + Math.sin(a) * 66).toFixed(1); }
  var tur = "";
  [15, 75, 195, 255, 315].forEach(function(a){ tur += "<g transform=\"rotate(" + a + " 520 96)\">" + sR(568, 85, 26, 22, "url(#sgPd)", " rx=\"2\"") + sR(592, 89, 12, 14, "#2a2d33") + sP("M602 90l8 6-8 6z", "url(#sgGold)") + "</g>"; });
  tur += sP(poly + "Z", "url(#sgDv)") + sC(520, 96, 48, "url(#sgDh)") + sC(520, 96, 48, "none", " stroke=\"#fff\" stroke-opacity=\".08\" stroke-width=\"2\"") + sC(520, 96, 14, "#202328");
  for(i = 0; i < 12; i++) tur += "<g transform=\"rotate(" + (i * 30) + " 520 96)\">" + sC(574, 96, 3.5, "#1d2025") + "</g>";
  tur += "<g transform=\"rotate(135 520 96)\">" + sR(572, 84, 42, 24, "url(#sgPd)", " rx=\"2\"") + sR(612, 88, 10, 16, "#2a2d33") + sP("M620 88l12 8-12 8z", "url(#sgGold)") + "</g>";
  tur += sCool("M488 128Q466 150 446 170");
  var tool = sG("tl", sG("jt", sG("feed", tur + sEmit(441, 175, 200, "chip"))), "tool:home=;near=translate(-95px,-27px);cut=translate(-123px,-18px)");
  var s = sBase() + sP("M0 290H640V330H0Z", "url(#sgPd)") + sR(0, 286, 640, 4, "#fff", " opacity=\".08\"") +
    sR(0, 84, 116, 206, "url(#sgP)", " rx=\"6\"") + sR(8, 96, 100, 6, "#000", " opacity=\".08\"") + sR(108, 150, 16, 80, "url(#sgDh)") +
    sR(122, 116, 46, 148, "url(#sgDh)", " rx=\"5\"") + sStripe(122, 116, 46, 148, "v", "r-s", .12) +
    sG("wk", wk) +
    sG("", sR(166, 120, 24, 26, "url(#sgSv)", " rx=\"2\"") + sR(166, 120, 24, 26, "#fff", " class=\"jaws\" opacity=\"0\""), "clamp:0=;1=translate(0px,8px)") +
    sG("", sR(166, 234, 24, 26, "url(#sgSv)", " rx=\"2\"") + sR(166, 234, 24, 26, "#fff", " class=\"jaws\" opacity=\"0\""), "clamp:0=;1=translate(0px,-8px)") +
    sG("", sR(560, 166, 90, 50, "url(#sgP)", " rx=\"4\"") + sR(530, 178, 34, 26, "url(#sgSh)") + sP("M530 181L512 190L530 199Z", "url(#sgSh)"), "tail:0=;1=translate(-176px,0px)") +
    tool;
  return { svg: s, P: [318, 157], W: [520, 96], vars: "--fx:-70px;--fy:0px" };
};
SVIS.vtl = function(){
  var wk = sG("raw", sR(150, 186, 340, 82, "url(#sgSv)") + sStripe(150, 186, 340, 82, "h", "r-s", .16, 22)) +
    sG("fn", sR(150, 196, 340, 72, "url(#sgSv)") + sR(150, 196, 340, 3, "#fff", " opacity=\".5\"") + sStripe(150, 196, 340, 72, "h", "r-s", .16, 22)) + sR(150, 186, 340, 82, "url(#sgBrn)", " class=\"burn\"");
  var ram = sR(404, 40, 44, 200, "url(#sgDv)") + sR(398, 232, 56, 18, "url(#sgPd)") + sR(436, 246, 14, 24, "#2a2d33") + sP("M436 270l7 10 7-10z", "url(#sgGold)") + sCool("M462 236Q456 262 446 278");
  var s = sBase() + sR(16, 40, 64, 292, "url(#sgP)", " rx=\"5\"") + sR(560, 40, 64, 292, "url(#sgP)", " rx=\"5\"") +
    sG("tl", sG("jt", sG("feed", ram + sEmit(443, 280, 160, "chip"))), "tool:home=translate(0px,-160px);near=translate(0px,-100px);cut=translate(0px,-90px)") +
    sR(16, 34, 608, 52, "url(#sgP)", " rx=\"5\"") + sR(380, 70, 92, 36, "url(#sgPd)", " rx=\"3\"") +
    sR(84, 300, 472, 32, "url(#sgPd)") + sR(104, 268, 432, 32, "url(#sgDv)") + sStripe(104, 268, 432, 32, "h", "r-s", .12, 22) +
    sG("wk", wk) +
    sG("", sR(122, 234, 26, 34, "url(#sgDh)", " rx=\"2\""), "clamp:0=translate(-10px,0px);1=") + sG("", sR(492, 234, 26, 34, "url(#sgDh)", " rx=\"2\""), "clamp:0=translate(10px,0px);1=");
  return { svg: s, P: [443, 190], W: [320, 230], vars: "--fx:-170px;--fy:0px" };
};
SVIS.turnmill = function(){
  var wk = sG("raw", sR(166, 154, 190, 72, "url(#sgSh)") + sStripe(166, 154, 190, 72, "v", "r-s")) +
    sG("fn", sR(166, 154, 110, 72, "url(#sgSh)") + sR(276, 163, 80, 54, "url(#sgSh)") + sR(200, 154, 50, 6, "#2a2d33") + sStripe(166, 154, 190, 72, "v", "r-s")) + sR(166, 154, 190, 72, "url(#sgBrn)", " class=\"burn\"");
  var head = sR(422, 112, 36, 74, "url(#sgDv)") + sR(428, 186, 24, 14, "url(#sgDh)") + sR(434, 200, 12, 40, "url(#sgSv)") + sStripe(434, 200, 12, 40, "h", "r-m", .3, 5) + sCool("M462 196Q452 222 444 238");
  var hd = sG("", head, "tilt:0=;45=rotate(45deg);90=rotate(90deg)", sOrg(440, 112)) + sC(440, 112, 34, "url(#sgDh)") + sC(440, 112, 12, "#202328");
  var s = sBase() + sP("M0 290H640V330H0Z", "url(#sgPd)") +
    sR(0, 84, 116, 206, "url(#sgP)", " rx=\"6\"") + sR(108, 150, 16, 80, "url(#sgDh)") + sR(122, 116, 46, 148, "url(#sgDh)", " rx=\"5\"") + sStripe(122, 116, 46, 148, "v", "r-s", .12) +
    sG("wk", wk) +
    sG("", sR(166, 120, 24, 26, "url(#sgSv)", " rx=\"2\""), "clamp:0=;1=translate(0px,8px)") + sG("", sR(166, 234, 24, 26, "url(#sgSv)", " rx=\"2\""), "clamp:0=;1=translate(0px,-8px)") +
    sR(560, 140, 90, 100, "url(#sgP)", " rx=\"4\"") + sR(536, 160, 26, 60, "url(#sgDh)") +
    sG("tl", sG("jt", sG("feed", sR(392, 0, 96, 84, "url(#sgP)", " rx=\"4\"") + hd + sEmit(440, 240, 160, "chip"))), "tool:home=translate(0px,-70px);near=translate(-130px,-92px);cut=translate(-130px,-82px)");
  return { svg: s, P: [310, 156], W: [440, 112], vars: "--fx:-60px;--fy:0px" };
};
SVIS.swiss = function(){
  var bar = function(){ return sR(0, 178, 330, 24, "url(#sgSh)") + sStripe(0, 178, 330, 24, "v", "r-s", .25, 8); };
  var s = sBase() + sP("M0 300H640V330H0Z", "url(#sgPd)") +
    sG("wk", sG("raw", bar()) + sG("fn", bar() + sR(380, 300, 34, 18, "url(#sgSh)", " rx=\"3\"") + sR(420, 304, 30, 14, "url(#sgSh)", " rx=\"3\"")) + sR(300, 178, 30, 24, "url(#sgBrn)", " class=\"burn\"")) +
    sG("", sR(40, 130, 150, 120, "url(#sgP)", " rx=\"5\"") + sR(180, 160, 20, 60, "url(#sgDh)"), "", " class=\"hs\"") +
    sR(250, 110, 52, 160, "url(#sgP)", " rx=\"4\"") + sR(296, 168, 10, 44, "url(#sgDh)") +
    sG("tl", sG("jt", sG("feed", sR(298, 30, 100, 56, "url(#sgDh)", " rx=\"3\"") + sR(306, 86, 16, 80, "url(#sgPd)") + sR(332, 86, 16, 62, "url(#sgPd)") + sR(358, 86, 16, 70, "url(#sgPd)") +
      sP("M306 166h16l-8 9z", "url(#sgGold)") + sCool("M296 96Q300 150 312 172", true) + sEmit(314, 175, 200, "chip"))), "tool:home=translate(0px,-60px);near=translate(4px,-6px);cut=translate(4px,5px)") +
    sG("", sR(338, 236, 18, 64, "url(#sgPd)") + sR(342, 214, 10, 22, "url(#sgSv)") + sStripe(342, 214, 10, 22, "h", "r-m", .4, 4), "") +
    sR(500, 140, 120, 100, "url(#sgP)", " rx=\"4\"") + sR(480, 166, 22, 48, "url(#sgDh)");
  return { svg: s, P: [316, 178], W: [120, 190], vars: "--fx:0px;--fy:0px" };
};
function sMcHead(x, tipY, probe){
  var cx = x;
  return sR(cx - 50, tipY - 198, 100, 112, "url(#sgP)", " rx=\"5\"") + sR(cx - 20, tipY - 88, 40, 16, "url(#sgDh)") + sR(cx - 14, tipY - 72, 28, 22, "url(#sgDh)") +
    sG("ct", sR(cx - 7, tipY - 50, 14, 50, "url(#sgSv)", " rx=\"2\"") + sStripe(cx - 7, tipY - 50, 14, 46, "h", "r-s", .35, 5)) +
    (probe !== false ? sG("prb", sR(cx - 2, tipY - 50, 4, 44, "#d9dce0") + sC(cx, tipY - 4, 5, "#d33a2c")) : "") +
    sCool("M" + (cx + 36) + " " + (tipY - 68) + "Q" + (cx + 22) + " " + (tipY - 30) + " " + (cx + 4) + " " + (tipY - 4));
}
SVIS.vmc = function(){
  var wk = sG("raw", sR(250, 232, 140, 40, "url(#sgBk)")) + sG("fn", sR(250, 232, 140, 40, "url(#sgBk)") + sR(290, 232, 60, 12, "#2c3036") + sC(270, 252, 5, "#1d2025") + sC(370, 252, 5, "#1d2025")) + sR(250, 232, 140, 40, "url(#sgBrn)", " class=\"burn\"");
  var s = sBase() + sR(240, 8, 160, 300, "url(#sgPd)") + sR(250, 8, 6, 300, "#fff", " opacity=\".06\"") +
    sR(140, 330, 360, 26, "url(#sgP)") + sR(110, 300, 420, 30, "url(#sgDh)") + sR(110, 312, 420, 3, "#000", " opacity=\".35\"") + sR(110, 322, 420, 3, "#000", " opacity=\".35\"") +
    sR(220, 284, 200, 16, "url(#sgDh)") + sR(232, 252, 18, 48, "url(#sgDh)") + sR(250, 272, 140, 12, "url(#sgSv)") +
    sG("wk", wk) + sG("", sR(390, 252, 18, 48, "url(#sgDh)"), "clamp:0=translate(16px,0px);1=") +
    sG("tl", sG("jt", sG("feed", sMcHead(320, 238) + sEmit(322, 236, 200, "chip"))), "tool:home=translate(0px,-90px);near=translate(0px,-12px);cut=translate(0px,-2px)");
  return { svg: s, P: [320, 234], W: [320, 200], vars: "--fx:-50px;--fy:0px" };
};
SVIS.hmc = function(){
  var tool = sR(400, 140, 100, 100, "url(#sgP)", " rx=\"5\"") + sR(380, 170, 22, 40, "url(#sgDv)") + sR(354, 176, 28, 28, "url(#sgDv)") +
    sG("ct", sR(314, 183, 42, 14, "url(#sgSh)", " rx=\"2\"") + sStripe(314, 183, 42, 14, "v", "r-s", .35, 5)) + sG("prb", sR(312, 188, 44, 4, "#d9dce0") + sC(312, 190, 5, "#d33a2c")) + sCool("M392 160Q350 166 318 186");
  var s = sBase() + sR(480, 20, 150, 300, "url(#sgPd)") +
    sG("pal", sR(60, 300, 300, 26, "url(#sgDh)") + sR(130, 110, 130, 190, "url(#sgP)", " rx=\"3\"") + sR(140, 120, 6, 170, "#000", " opacity=\".08\"") +
      "<text class=\"pa\" x=\"84\" y=\"318\" fill=\"#cfd3d8\" font-size=\"14\" font-family=\"Jost,sans-serif\" letter-spacing=\"2\">PALLET A</text><text class=\"pb\" x=\"84\" y=\"318\" fill=\"#cfd3d8\" font-size=\"14\" font-family=\"Jost,sans-serif\" letter-spacing=\"2\">PALLET B</text>" +
      sG("wk", sG("raw", sR(260, 140, 40, 100, "url(#sgBk)")) + sG("fn", sR(260, 140, 40, 100, "url(#sgBk)") + sR(292, 170, 8, 40, "#2c3036")) + sR(260, 140, 40, 100, "url(#sgBrn)", " class=\"burn\"")) +
      sG("", sR(250, 128, 24, 14, "url(#sgDh)") + sR(250, 238, 24, 14, "url(#sgDh)"), "clamp:0=translate(-8px,0px);1=")) + sR(40, 326, 340, 6, "url(#sgPd)") +
    sG("tl", sG("jt", sG("feed", tool + sEmit(314, 190, 120, "chip"))), "tool:home=translate(80px,0px);near=translate(-8px,0px);cut=translate(-18px,0px)");
  return { svg: s, P: [300, 190], W: [195, 210], vars: "--fx:0px;--fy:-36px" };
};
SVIS["5axis"] = function(){
  var wk = sG("raw", sP("M272 214V170l14-12h68l14 12v44Z", "url(#sgBk)")) + sG("fn", sP("M272 214V176q48-34 96 0v38Z", "url(#sgSh)") + sP("M290 196q30-18 60 0", "none", " stroke=\"#fff\" stroke-width=\"1.4\" opacity=\".5\"")) + sR(272, 158, 96, 56, "url(#sgBrn)", " class=\"burn\"");
  var cradle = sR(150, 232, 340, 30, "url(#sgDh)", " rx=\"4\"") + sR(150, 200, 22, 40, "url(#sgDh)") + sR(468, 200, 22, 40, "url(#sgDh)") + sR(214, 216, 212, 16, "url(#sgDv)") + sStripe(214, 216, 212, 16, "h", "r-c", .2, 12) + sG("wk", wk);
  var s = sBase() + sR(250, 8, 140, 140, "url(#sgPd)") + sR(90, 330, 460, 24, "url(#sgP)") +
    sR(104, 196, 46, 134, "url(#sgP)", " rx=\"4\"") + sR(490, 196, 46, 134, "url(#sgP)", " rx=\"4\"") + sC(127, 247, 12, "url(#sgDh)") + sC(513, 247, 12, "url(#sgDh)") +
    sG("", cradle, "tilt:0=;45=rotate(-45deg);90=rotate(-90deg)", sOrg(320, 247)) +
    sG("tl", sG("jt", sG("feed", sMcHead(320, 190) + sC(320, 186, 6, "url(#sgSh)") + sEmit(322, 188, 200, "chip"))), "tool:home=translate(0px,-60px);near=translate(0px,-38px);cut=translate(0px,-28px)");
  return { svg: s, P: [320, 160], W: [320, 247], vars: "--fx:-40px;--fy:0px" };
};
SVIS.gantry = function(){
  var head = sR(298, 60, 44, 190, "url(#sgDv)") + sR(298, 240, 44, 14, "url(#sgDh)") +
    sG("ct", sR(282, 254, 76, 18, "url(#sgDh)", " rx=\"2\"") + sStripe(282, 254, 76, 18, "h", "r-s", .3, 9) + sR(284, 266, 72, 3, "url(#sgGold)")) +
    sG("prb", sR(318, 254, 4, 22, "#d9dce0") + sC(320, 276, 5, "#d33a2c")) + sCool("M370 236Q350 262 340 274");
  var s = sBase() + sR(16, 56, 54, 276, "url(#sgP)", " rx=\"5\"") + sR(570, 56, 54, 276, "url(#sgP)", " rx=\"5\"") +
    sG("tl", sG("jt", sG("feed", head + sEmit(330, 272, 200, "chip"))), "tool:home=translate(0px,-110px);near=translate(0px,2px);cut=translate(0px,10px)") +
    sR(16, 46, 608, 52, "url(#sgP)", " rx=\"5\"") + sR(284, 54, 72, 74, "url(#sgPd)", " rx=\"3\"") +
    sR(40, 320, 560, 24, "url(#sgDh)") + sR(40, 330, 560, 3, "#000", " opacity=\".35\"") +
    sG("wk", sG("raw", sR(110, 280, 420, 40, "url(#sgBk)")) + sG("fn", sR(110, 280, 420, 40, "url(#sgBk)") + sR(110, 280, 420, 3, "#fff", " opacity=\".55\"")) + sR(110, 280, 420, 40, "url(#sgBrn)", " class=\"burn\"")) +
    sG("", sR(92, 272, 34, 10, "url(#sgDh)") + sR(514, 272, 34, 10, "url(#sgDh)") + sR(104, 262, 10, 18, "#9aa0a8") + sR(526, 262, 10, 18, "#9aa0a8"), "clamp:0=translate(0px,-14px);1=");
  return { svg: s, P: [320, 282], W: [320, 263], vars: "--fx:-150px;--fy:0px" };
};
function sGrind(cx, cy, r, guard){
  var s = sC(cx, cy, r, "url(#sgWh)") + sC(cx, cy, r, "url(#sgGr)") + sC(cx, cy, r - 3, "none", " stroke=\"#000\" stroke-opacity=\".12\" stroke-width=\"2\"");
  for(var i = 0; i < 10; i++){ var a = i * Math.PI / 5; s += sL((cx + Math.cos(a) * r * .5).toFixed(1), (cy + Math.sin(a) * r * .5).toFixed(1), (cx + Math.cos(a) * r * .93).toFixed(1), (cy + Math.sin(a) * r * .93).toFixed(1), "#000", 1.2, " opacity=\".12\""); }
  s += sC(cx, cy, r * .36, "url(#sgDv)") + sC(cx, cy, r * .13, "#1d2025");
  return s;
}
function sGuard(cx, cy, r, a0, a1){
  var R = r + 14, x0 = cx + Math.cos(a0) * R, y0 = cy + Math.sin(a0) * R, x1 = cx + Math.cos(a1) * R, y1 = cy + Math.sin(a1) * R;
  var lg = (a1 - a0) > Math.PI ? 1 : 0;
  return sP("M" + x0.toFixed(1) + " " + y0.toFixed(1) + "A" + R + " " + R + " 0 " + lg + " 1 " + x1.toFixed(1) + " " + y1.toFixed(1) + "L" + (cx + Math.cos(a1) * (r + 2)).toFixed(1) + " " + (cy + Math.sin(a1) * (r + 2)).toFixed(1) + "A" + (r + 2) + " " + (r + 2) + " 0 " + lg + " 0 " + (cx + Math.cos(a0) * (r + 2)).toFixed(1) + " " + (cy + Math.sin(a0) * (r + 2)).toFixed(1) + "Z", "url(#sgP)");
}
SVIS.cylgrind = function(){
  var wheel = sG("wh", sG("rot r-s rotr", sGrind(470, 200, 110))) + sGuard(470, 200, 110, -2.0, 2.0);
  var s = sBase() + sR(0, 300, 640, 30, "url(#sgPd)") + sR(150, 130, 170, 150, "#23262b", " rx=\"8\"") + sR(150, 130, 170, 3, "#fff", " opacity=\".05\"") +
    sG("", sC(250, 200, 46, "url(#sgDv)") + sC(250, 200, 18, "#1d2025"), "tail:0=scale(.6);1=", sOrg(250, 200)) +
    sG("wk", sG("rot r-w", sC(250, 200, 34, "url(#sgSv)") + sL(250, 172, 250, 190, "#fff", 2, " opacity=\".4\"") + sL(222, 208, 236, 202, "#000", 2, " opacity=\".2\"")) + sC(250, 200, 34, "url(#sgBrn)", " class=\"burn\"")) +
    sG("tl", sG("jt", wheel + sEmit(362, 206, 110, "spark")), "tool:home=;near=translate(-70px,0px);cut=translate(-76px,0px)") + sCool("M318 96Q298 150 288 192") +
    sG("", sR(462, 14, 16, 58, "url(#sgDh)") + sP("M464 72h12l-6 12z", "#e8f2ff"), "dress:0=translate(0px,-30px);1=translate(0px,6px)", "");
  return { svg: s, P: [286, 200], W: [394, 200], vars: "" };
};
SVIS.intgrind = function(){
  var ring = sC(260, 200, 112, "url(#sgSv)") + sC(260, 200, 112, "none", " stroke=\"#000\" stroke-opacity=\".18\" stroke-width=\"3\"") + sC(260, 200, 54, "#16181c") + sC(260, 200, 54, "none", " stroke=\"#fff\" stroke-opacity=\".3\" stroke-width=\"1.5\"") +
    sL(260, 96, 260, 140, "#fff", 2.4, " opacity=\".3\"") + sL(170, 250, 205, 230, "#000", 2.4, " opacity=\".18\"");
  var jaws = "";
  [-90, 30, 150].forEach(function(a){ jaws += "<g transform=\"rotate(" + a + " 260 200)\">" + sG("", sR(372, 186, 30, 28, "url(#sgDh)", " rx=\"3\""), "clamp:0=translate(12px,0px);1=") + "</g>"; });
  var wheel = sG("", sC(270, 200, 22, "url(#sgDh)") + sG("rot r-s", sC(270, 200, 34, "url(#sgWh)") + sC(270, 200, 34, "url(#sgGr)") + sL(270, 170, 270, 186, "#000", 1.4, " opacity=\".25\"") + sL(244, 214, 256, 208, "#000", 1.4, " opacity=\".25\"")) + sC(270, 200, 9, "#1d2025"), "", "");
  var s = sBase() + sC(260, 200, 150, "#24272c") + sC(260, 200, 150, "none", " stroke=\"#fff\" stroke-opacity=\".05\" stroke-width=\"2\"") +
    sG("wk", sG("rot r-w", ring) + sC(260, 200, 112, "url(#sgBrn)", " class=\"burn\"")) + sG("", jaws) +
    sR(420, 120, 200, 160, "url(#sgP)", " rx=\"6\"") + sR(408, 182, 16, 36, "url(#sgDh)") +
    sG("tl", sG("jt", sG("feed", wheel + sEmit(304, 200, -40, "spark") + sCool("M430 150Q350 150 308 190"))), "tool:home=translate(-10px,0px) scale(1.25);near=;cut=translate(8px,0px)", sOrg(270, 200)) +
    sG("", sR(150, 194, 76, 12, "url(#sgDh)") + sP("M226 194l10 6-10 6z", "#e8f2ff"), "dress:0=translate(-30px,0px);1=");
  return { svg: s, P: [304, 200], W: [270, 200], vars: "--fx:0px;--fy:0px" };
};
SVIS.surfgrind = function(){
  var table = sR(100, 294, 440, 22, "url(#sgPd)") + sR(120, 268, 400, 26, "url(#sgDh)");
  for(var x = 128; x < 516; x += 12) table += sR(x, 270, 5, 22, "#000", " opacity=\".25\"");
  table += sC(138, 281, 4, "#3a1d1d", " class=\"mag\"") + sR(236, 262, 10, 6, "#9aa0a8") + sR(394, 262, 10, 6, "#9aa0a8") + sR(150, 260, 10, 8, "url(#sgDh)") + sP("M152 260l3-8 3 8z", "#e8f2ff");
  table += sG("wk", sG("raw", sR(250, 252, 140, 16, "url(#sgBk)")) + sG("fn", sR(250, 254, 140, 14, "url(#sgBk)") + sR(250, 254, 140, 2, "#fff", " opacity=\".6\"")) + sR(250, 252, 140, 16, "url(#sgBrn)", " class=\"burn\""));
  var s = sBase() + sR(420, 10, 200, 300, "url(#sgPd)") + sR(60, 316, 520, 20, "url(#sgP)") +
    sG("", sG("feed", table), "dress:0=;1=translate(165px,-6px)") +
    sG("tl", sG("jt", sR(300, 30, 140, 40, "url(#sgP)", " rx=\"4\"") + sG("wh", sG("rot r-s", sGrind(320, 150, 90))) + sGuard(320, 150, 90, 2.9, 6.5) + sCool("M432 196Q380 240 330 246") + sEmit(316, 240, 150, "spark")), "tool:home=translate(0px,-30px);near=translate(0px,6px);cut=translate(0px,12px)");
  return { svg: s, P: [320, 252], W: [320, 162], vars: "--fx:90px;--fy:0px;--fd:1.6s" };
};
SVIS.centerless = function(){
  var s = sBase() + sR(0, 300, 640, 30, "url(#sgPd)") +
    sG("wh", sG("rot r-s rotr", sGrind(190, 190, 120))) + sGuard(190, 190, 120, 1.2, 5.1) +
    sG("", sR(182, 14, 16, 40, "url(#sgDh)") + sP("M184 54h12l-6 10z", "#e8f2ff"), "dress:0=translate(0px,-24px);1=translate(0px,6px)") +
    sP("M318 200L346 192V300H318Z", "url(#sgDh)") + sR(312, 296, 40, 10, "url(#sgDh)") +
    sG("wk", sG("rot r-w", sC(330, 178, 20, "url(#sgSv)") + sL(330, 160, 330, 170, "#fff", 2, " opacity=\".45\"")) + sC(330, 178, 20, "url(#sgBrn)", " class=\"burn\"")) +
    sG("tl", sG("jt", sG("rot r-w", sC(440, 196, 90, "#5d6067") + sC(440, 196, 90, "url(#sgGr)") + sL(440, 110, 440, 140, "#fff", 2, " opacity=\".2\"") + sC(440, 196, 30, "url(#sgDv)")) + sR(500, 150, 130, 100, "url(#sgP)", " rx=\"5\"")), "tool:home=translate(40px,0px);near=translate(8px,0px);cut=") +
    sCool("M262 70Q300 120 314 170") + sEmit(310, 182, 120, "spark");
  return { svg: s, P: [312, 180], W: [190, 190], vars: "" };
};
SVIS.hob = function(){
  var gear = sG("raw", sR(240, 210, 160, 70, "url(#sgSv)") + sStripe(240, 210, 160, 70, "h", "r-s", .16, 12)) +
    sG("fn", sR(240, 210, 160, 70, "url(#sgSv)") + sStripe(240, 210, 160, 70, "h", "r-s", .55, 10)) + sR(240, 210, 160, 70, "url(#sgBrn)", " class=\"burn\"");
  var hob = sG("rot r-s", sP(sGearPath(450, 200, 46, 16, 7), "url(#sgSv)") + sC(450, 200, 18, "url(#sgDh)") + sC(450, 200, 7, "#1d2025"));
  var s = sBase() + sR(200, 280, 240, 50, "url(#sgP)", " rx=\"4\"") + sR(300, 30, 40, 40, "url(#sgPd)") + sR(312, 70, 16, 140, "url(#sgDh)") + sR(510, 30, 110, 300, "url(#sgP)", " rx=\"5\"") +
    sG("wk", gear) +
    sG("tl", sG("jt", sG("feed", sR(470, 150, 60, 100, "url(#sgPd)", " rx=\"4\"") + hob + sEmit(404, 210, 160, "chip") + sCool("M494 136Q430 150 410 200", true))), "tool:home=translate(60px,-70px);near=;cut=translate(-6px,0px)");
  return { svg: s, P: [400, 220], W: [450, 200], vars: "--fx:0px;--fy:56px;--fd:4s" };
};
SVIS.geargrind = function(){
  var gear = sG("raw", sR(220, 200, 160, 70, "url(#sgSv)") + sStripe(220, 200, 160, 70, "h", "r-s", .5, 10)) +
    sG("fn", sR(220, 200, 160, 70, "url(#sgSv)") + sStripe(220, 200, 160, 70, "h", "r-s", .65, 10) + sR(220, 200, 160, 3, "#fff", " opacity=\".5\"")) + sR(220, 200, 160, 70, "url(#sgBrn)", " class=\"burn\"");
  var wheel = sG("wh", sG("rot r-s rotr", sGrind(468, 235, 82) + sC(468, 235, 80, "none", " stroke=\"#000\" stroke-opacity=\".16\" stroke-width=\"6\" stroke-dasharray=\"3 4\""))) + sGuard(468, 235, 82, -1.4, 1.4);
  var s = sBase() + sR(180, 270, 240, 60, "url(#sgP)", " rx=\"4\"") + sR(282, 30, 36, 170, "url(#sgDh)") +
    sG("wk", gear) +
    sG("tl", sG("jt", sG("feed", wheel + sEmit(386, 240, 100, "spark") + sCool("M372 150Q384 190 386 228", true))), "tool:home=translate(60px,0px);near=;cut=translate(-8px,0px)") +
    sG("", sG("rot r-s", sC(574, 106, 24, "url(#sgDv)") + sL(574, 86, 574, 96, "#fff", 2, " opacity=\".4\"")) + sR(596, 96, 40, 20, "url(#sgDh)"), "dress:0=;1=translate(-38px,48px)");
  return { svg: s, P: [380, 236], W: [468, 235], vars: "--fx:0px;--fy:30px;--fd:3s" };
};
SVIS.skive = function(){
  var ring = sC(300, 196, 132, "url(#sgSv)") + sP(sGearPath(300, 196, 98, 40, 8, true), "#16181c") + sL(300, 64, 300, 86, "#fff", 2.4, " opacity=\".35\"");
  var jaws = "";
  [-90, 30, 150].forEach(function(a){ jaws += "<g transform=\"rotate(" + a + " 300 196)\">" + sG("", sR(430, 182, 30, 28, "url(#sgDh)", " rx=\"3\""), "clamp:0=translate(12px,0px);1=") + "</g>"; });
  var tool = sG("rot r-s rotr", sP(sGearPath(300, 252, 40, 18, 6), "url(#sgDv)") + sC(300, 252, 14, "#1d2025") + sL(300, 214, 300, 228, "#fff", 2, " opacity=\".35\""));
  var s = sBase() + sC(300, 196, 168, "#23262b") +
    sG("wk", sG("rot r-s", ring) + sC(300, 196, 132, "url(#sgBrn)", " class=\"burn\"")) + sG("", jaws) +
    sR(470, 40, 150, 130, "url(#sgP)", " rx=\"6\"") +
    sG("tl", sG("jt", sR(296, 120, 8, 130, "url(#sgDh)") + sG("", tool) + sEmit(300, 294, 60, "chip") + sCool("M480 160Q380 260 316 290")), "tool:home=translate(0px,-56px) scale(1.15);near=translate(0px,-6px);cut=", sOrg(300, 252));
  return { svg: s, P: [300, 292], W: [300, 252], vars: "" };
};
SVIS.wedm = function(){
  var head = sR(268, 10, 104, 120, "url(#sgP)", " rx=\"5\"") + sR(304, 130, 32, 66, "url(#sgDh)") + sR(310, 196, 20, 12, "#8d939b") +
    sR(200, 292, 160, 14, "url(#sgDh)") + sR(310, 280, 20, 12, "#8d939b") +
    sG("wr", sL(320, 208, 320, 244, "#e2bd5a", 2.4, " class=\"wa\"") + sL(320, 244, 320, 280, "#e2bd5a", 2.4, " class=\"wb\"")) +
    sCool("M314 208Q310 220 318 232") + sCool("M326 280Q330 268 322 256");
  var s = sBase() + sR(84, 168, 472, 156, "#2c3137", " rx=\"4\"") +
    sG("", sR(90, 174, 460, 146, "#4aa3dc", " opacity=\".32\""), "fluid:0=scaleY(0);1=", " style=\"transform-origin:320px 320px\"") +
    sR(130, 262, 380, 20, "url(#sgDh)") +
    sG("wk", sG("raw", sR(220, 214, 200, 48, "url(#sgBk)")) + sG("fn", sR(220, 214, 200, 48, "url(#sgBk)") + sP("M300 214h44v48h-44z", "#1f2328")) + sR(220, 214, 200, 48, "url(#sgBrn)", " class=\"burn\"")) +
    sG("", sR(206, 250, 16, 12, "url(#sgDh)") + sR(418, 250, 16, 12, "url(#sgDh)"), "clamp:0=translate(0px,-10px);1=") +
    sG("tl", sG("jt", sG("feed", head + sEmit(320, 238, 0, "flash"))), "tool:home=translate(150px,0px);near=translate(104px,0px);cut=translate(80px,0px)") +
    sR(84, 168, 472, 6, "#fff", " opacity=\".06\"");
  return { svg: s, P: [400, 238], W: [400, 238], vars: "--fx:-80px;--fy:0px;--fd:5s" };
};
SVIS.laser = function(){
  var head = sR(286, 50, 68, 70, "url(#sgPd)", " rx=\"4\"") + sR(304, 120, 32, 70, "url(#sgSv)") + sP("M306 190h28l-6 16h-16z", "url(#sgGold)") +
    sG("gs", sP("M314 206h12l10 10h-32z", "#9ad7ff")) + sG("bm", sR(318.5, 206, 3, 12, "#fff") + sR(316, 206, 8, 12, "#ff6a3d", " opacity=\".5\""));
  var slats = "";
  for(var x = 90; x < 560; x += 20) slats += sP("M" + x + " 312l10-30 10 30z", "#3b4047");
  var s = sBase() + sR(60, 312, 520, 20, "url(#sgPd)") + slats +
    sG("wk", sG("raw", sR(80, 276, 480, 6, "url(#sgSh)")) + sG("fn", sR(80, 276, 480, 6, "url(#sgSh)") + sR(250, 276, 50, 6, "#16181c") + sR(360, 276, 30, 6, "#16181c")) + sR(80, 276, 480, 6, "url(#sgBrn)", " class=\"burn\"")) +
    sG("tl", sG("jt", sG("feed", head + sEmit(320, 218, 90, "spark"))), "tool:home=;near=translate(0px,62px);cut=translate(0px,66px)") +
    sR(30, 40, 580, 30, "url(#sgP)", " rx=\"4\"");
  return { svg: s, P: [320, 276], W: [320, 270], vars: "--fx:-200px;--fy:0px;--fd:3.4s" };
};
SVIS.transfer = function(){
  var st = "", hd = "", parts = "";
  [110, 250, 390, 530].forEach(function(x, i){
    st += sR(x - 42, 250, 84, 38, "url(#sgP)", " rx=\"3\"") + sG("", sR(x - 40, 238, 12, 12, "url(#sgDh)") + sR(x + 28, 238, 12, 12, "url(#sgDh)"), "clamp:0=translate(0px,-8px);1=");
    parts += sR(x - 24, 222, 48, 28, "url(#sgBk)");
    hd += sR(x - 32, 50, 64, 100, "url(#sgP)", " rx=\"4\"") + sR(x - 10, 150, 20, 14, "url(#sgDh)") + sR(x - 5, 164, 10, 30, "url(#sgSv)") + sStripe(x - 5, 164, 10, 30, "h", "r-s", .4, 4) + sCool("M" + (x + 26) + " 152Q" + (x + 14) + " 190 " + (x + 4) + " 212");
  });
  var s = sBase() + sR(10, 30, 620, 24, "url(#sgPd)") + sR(10, 288, 620, 12, "url(#sgDh)") + st +
    sG("wk", sG("xf", sG("raw", parts) + sG("fn", parts + sR(240, 222, 20, 8, "#2c3036") + sR(380, 222, 20, 8, "#2c3036")))) +
    sG("tl", sG("jt", hd + sEmit(250, 194, 200, "chip")), "tool:home=translate(0px,-30px);near=translate(0px,18px);cut=translate(0px,28px)") +
    sR(0, 300, 640, 30, "url(#sgPd)");
  return { svg: s, P: [250, 222], W: [250, 200], vars: "" };
};

var SIM_DEFS = "<defs>" +
  "<linearGradient id=\"sgBg\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#2f333a\"/><stop offset=\"1\" stop-color=\"#16181c\"/></linearGradient>" +
  "<linearGradient id=\"sgSh\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#7c838c\"/><stop offset=\".22\" stop-color=\"#eef1f3\"/><stop offset=\".4\" stop-color=\"#c4c9cf\"/><stop offset=\".78\" stop-color=\"#858c95\"/><stop offset=\"1\" stop-color=\"#575d64\"/></linearGradient>" +
  "<linearGradient id=\"sgSv\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\"0\" stop-color=\"#6f767f\"/><stop offset=\".25\" stop-color=\"#eef1f3\"/><stop offset=\".45\" stop-color=\"#c4c9cf\"/><stop offset=\".8\" stop-color=\"#858c95\"/><stop offset=\"1\" stop-color=\"#575d64\"/></linearGradient>" +
  "<linearGradient id=\"sgBk\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#f3f5f7\"/><stop offset=\".1\" stop-color=\"#d3d8dd\"/><stop offset=\".12\" stop-color=\"#b7bdc4\"/><stop offset=\"1\" stop-color=\"#8c939b\"/></linearGradient>" +
  "<linearGradient id=\"sgDh\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#3a3e45\"/><stop offset=\".3\" stop-color=\"#767c86\"/><stop offset=\".6\" stop-color=\"#4a4f57\"/><stop offset=\"1\" stop-color=\"#2a2d32\"/></linearGradient>" +
  "<linearGradient id=\"sgDv\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\"0\" stop-color=\"#3a3e45\"/><stop offset=\".3\" stop-color=\"#767c86\"/><stop offset=\".6\" stop-color=\"#4a4f57\"/><stop offset=\"1\" stop-color=\"#2a2d32\"/></linearGradient>" +
  "<linearGradient id=\"sgP\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#e9e8e4\"/><stop offset=\"1\" stop-color=\"#bdbbb5\"/></linearGradient>" +
  "<linearGradient id=\"sgPd\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stop-color=\"#5f656e\"/><stop offset=\"1\" stop-color=\"#3d4148\"/></linearGradient>" +
  "<linearGradient id=\"sgGl\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#cfe3ff\" stop-opacity=\".16\"/><stop offset=\".3\" stop-color=\"#cfe3ff\" stop-opacity=\".05\"/><stop offset=\".33\" stop-color=\"#fff\" stop-opacity=\".2\"/><stop offset=\".37\" stop-color=\"#cfe3ff\" stop-opacity=\".05\"/><stop offset=\".7\" stop-color=\"#cfe3ff\" stop-opacity=\".04\"/><stop offset=\".73\" stop-color=\"#fff\" stop-opacity=\".14\"/><stop offset=\".76\" stop-color=\"#cfe3ff\" stop-opacity=\".05\"/></linearGradient>" +
  "<linearGradient id=\"sgGlL\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#2f8f5a\" stop-opacity=\".42\"/><stop offset=\".33\" stop-color=\"#5fd398\" stop-opacity=\".5\"/><stop offset=\".37\" stop-color=\"#2f8f5a\" stop-opacity=\".42\"/><stop offset=\"1\" stop-color=\"#1d6e44\" stop-opacity=\".45\"/></linearGradient>" +
  "<radialGradient id=\"sgWh\"><stop offset=\"0\" stop-color=\"#d6d0c0\"/><stop offset=\".8\" stop-color=\"#bcb4a2\"/><stop offset=\"1\" stop-color=\"#9e9684\"/></radialGradient>" +
  "<pattern id=\"sgGr\" width=\"7\" height=\"7\" patternUnits=\"userSpaceOnUse\"><circle cx=\"1.5\" cy=\"1.5\" r=\".8\" fill=\"#000\" opacity=\".22\"/><circle cx=\"5\" cy=\"4.5\" r=\".7\" fill=\"#fff\" opacity=\".3\"/></pattern>" +
  "<linearGradient id=\"sgBrn\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\"><stop offset=\"0\" stop-color=\"#c79a3a\"/><stop offset=\".45\" stop-color=\"#8a4b8f\"/><stop offset=\"1\" stop-color=\"#3e5fbf\"/></linearGradient>" +
  "<linearGradient id=\"sgGold\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"1\"><stop offset=\"0\" stop-color=\"#f4d27a\"/><stop offset=\"1\" stop-color=\"#a8812a\"/></linearGradient>" +
  "<linearGradient id=\"sgGoldV\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\" gradientUnits=\"userSpaceOnUse\"><stop offset=\"0\" stop-color=\"#f4d27a\"/><stop offset=\"1\" stop-color=\"#c9a24a\"/></linearGradient>" +
  "<radialGradient id=\"sgFl\"><stop offset=\"0\" stop-color=\"#fff\"/><stop offset=\".35\" stop-color=\"#ffe08a\"/><stop offset=\"1\" stop-color=\"#ff7a1a\" stop-opacity=\"0\"/></radialGradient>" +
  "<radialGradient id=\"sgSm\"><stop offset=\"0\" stop-color=\"#9ea3aa\" stop-opacity=\".75\"/><stop offset=\"1\" stop-color=\"#9ea3aa\" stop-opacity=\"0\"/></radialGradient>" +
  "</defs>";

function simApplyS(svg, st){
  return svg.replace(/data-s="([^"]*)"((?: style="[^"]*")?)/g, function(m, spec, sty){
    var tf = spec.split("|").map(function(part){
      var i = part.indexOf(":"), key = part.slice(0, i), map = {};
      part.slice(i + 1).split(";").forEach(function(kv){ var j = kv.indexOf("="); map[kv.slice(0, j)] = kv.slice(j + 1); });
      return map[sv(st[key])] || "";
    }).join(" ").trim();
    var org = sty ? sty.replace(/^ style="|"$/g, "") : "";
    return "data-s=\"" + spec + "\" style=\"" + org + (org && tf ? ";" : "") + (tf ? "transform:" + tf : "") + "\"";
  });
}
function simSvg(visual, label){
  sCN = 0;
  var v = SVIS[visual](), st = SIM_INIT;
  var noDoor = { transfer: 1, surfgrind: 1, centerless: 1, gantry: 1 }[visual];
  var fx = "<g class=\"fxg\" transform=\"translate(" + v.P[0] + " " + v.P[1] + ")\">" + sC(0, 0, 46, "url(#sgFl)", " class=\"fxf\"") +
    "<g class=\"fxs\">" + [0, 1, 2, 3].map(function(i){ return sC(-14 + i * 10, -6, 16 + i * 3, "url(#sgSm)", " style=\"animation-delay:-" + (i * .35) + "s\""); }).join("") + "</g>" +
    "<g class=\"fxi\">" + sP("M-14 0c-6-16 6-20 2-34 10 8 16 20 10 34z", "#ff8a2a") + sP("M0 0c-4-14 4-18 4-30 8 10 10 20 6 30z", "#ffc24a") + sP("M10 0c-2-8 2-12 2-18 6 6 6 12 4 18z", "#ff6a1a") + "</g>" +
    sEmit(0, 0, -90, "spark").replace("class=\"em em-spark\"", "class=\"emx\"") + "</g>";
  var frag = "<g class=\"frg\" transform=\"translate(" + v.W[0] + " " + v.W[1] + ")\">" + [0, 1, 2, 3, 4].map(function(i){ return "<g transform=\"rotate(" + (i * 72) + ")\"><path class=\"fr\" d=\"M0 0L40 -12A42 42 0 0 1 36 22Z\" fill=\"#bcb4a2\"/></g>"; }).join("") + "</g>";
  var leak = sR(0, 330, 640, 70, "#4aa3dc", " class=\"lk\" opacity=\".45\"");
  var svg = "<svg class=\"ilu simv\" viewBox=\"0 0 640 400\" role=\"img\" aria-label=\"" + esc(label) + "\" style=\"" + v.vars + "\">" + SIM_DEFS +
    "<g class=\"mc\">" + v.svg + "</g>" + fx + frag + leak + (noDoor ? "" : sDoor(visual === "laser" ? "url(#sgGlL)" : "")) + "</svg>";
  return simApplyS(svg, st);
}

/* ---------- panel + screen + start card */
function simPanel(sc){
  var on = {}; sc.panel.forEach(function(b){ on[b] = 1; });
  return "<div class=\"panel\" role=\"group\" aria-label=\"操作盤\">" + SKEY_GROUPS.map(function(g){
    var ks = g.filter(function(b){ return on[b]; });
    if(!ks.length) return "";
    return "<div class=\"pg\">" + ks.map(function(b){ var k = SKEY[b]; return "<button type=\"button\" class=\"key" + (k[2] ? " k-" + k[2] : "") + "\" data-b=\"" + b + "\"><i class=\"led\"></i><b>" + esc(k[0]) + "</b><small lang=\"en\">" + k[1] + "</small></button>"; }).join("") + "</div>";
  }).join("") + "</div>";
}
function simTypeName(slug){ var t = mtBy(MTD.types, slug); return t ? t.name : slug; }
function simAnswer(s){
  if(s.type === "check") return "確認すること：" + s.items.filter(function(x){ return x.req; }).map(function(x){ return x.t; }).join("／") + "。" + s.items.filter(function(x){ return !x.req; }).map(function(x){ return "「" + x.t + "」はしない（" + x.ng + "）"; }).join("");
  if(s.type === "panel") return "押す順番：" + s.seq.map(function(b){ return SKEY[b][0]; }).join(" → ");
  if(s.type === "choice") return "正解：" + s.options.filter(function(o){ return o.ok; })[0].t;
  if(s.type === "input") return "答え：" + (s.ok[0] === s.ok[1] ? s.ok[0] : s.ok[0] + "〜" + s.ok[1]) + " " + s.unit;
  if(s.type === "order") return "順番：" + s.items.join(" → ");
  if(s.type === "jog") return "ハンドルの倍率を×100 → ×10 → ×1と下げながら寄せ、すき間" + s.tol + "mm以下で止める。";
  return "";
}
function simWrongs(sc, s){
  var out = [];
  if(s.type === "choice") s.options.forEach(function(o){ if(o.inc && sc.incidents[o.inc]) out.push([o.t, sc.incidents[o.inc].title, o.inc]); });
  if(s.type === "panel") Object.keys(s.traps || {}).forEach(function(b){ if(sc.incidents[s.traps[b]]) out.push(["「" + SKEY[b][0] + "」を押す", sc.incidents[s.traps[b]].title, s.traps[b]]); });
  if(s.type === "input") (s.cases || []).forEach(function(c){ if(c.inc && sc.incidents[c.inc]) out.push([("lt" in c ? c.lt + "未満の値" : c.gt + "を超える値"), sc.incidents[c.inc].title, c.inc]); });
  if((s.type === "order" || s.type === "jog") && s.inc && sc.incidents[s.inc]) out.push([s.type === "order" ? "順番を間違える" : "倍率を下げずに寄せる", sc.incidents[s.inc].title, s.inc]);
  if(s.type === "check"){ s.items.forEach(function(x){ if(x.req && x.inc && sc.incidents[x.inc]) out.push(["「" + x.t + "」を確認しない", sc.incidents[x.inc].title, x.inc]); }); if(s.miss && sc.incidents[s.miss]) out.push(["確認を省く", sc.incidents[s.miss].title, s.miss]); }
  return out;
}
function simIncCard(sc, id){
  var I = sc.incidents[id];
  return "<article class=\"inc\" id=\"" + id + "\"><header><span class=\"sev s" + I.sev + "\">" + SSEV[I.sev] + "</span><span class=\"fxk\">" + esc(SFX[I.fx] || "") + "</span><h3>" + esc(I.title) + "</h3></header><dl>" +
    "<div><dt>現象</dt><dd>" + esc(I.what) + "</dd></div><div><dt>原因</dt><dd>" + esc(I.why) + "</dd></div><div><dt>損失</dt><dd>" + esc(I.loss) + "</dd></div><div><dt>対策</dt><dd>" + esc(I.prevent) + "</dd></div></dl></article>";
}
function simPhases(sc){ var ph = []; sc.steps.forEach(function(s){ if(ph.indexOf(s.phase) < 0) ph.push(s.phase); }); return ph; }

function mtSimPage(slug){
  var sc = SIM[slug], t = mtBy(MTD.types, slug), f = famOf(t), ph = simPhases(sc);
  var ids = Object.keys(sc.incidents), n3 = ids.filter(function(k){ return sc.incidents[k].sev === 3; }).length;
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">OPERATION TRAINING · " + esc(f.en) + "</p><h1 class=\"d2\">" + esc(t.name) + "の操作トレーニング</h1>" +
    "<p class=\"sub lead\" style=\"margin:20px auto 0\">" + esc(sc.summary) + "</p>" +
    "<div class=\"stats simst\"><div><b>" + sc.steps.length + "</b><span>ステップ</span></div><div><b>" + ids.length + "</b><span>トラブル</span></div><div><b>" + sc.minutes + "</b><span>分</span></div><div><b>" + sc.level + "<i>/3</i></b><span>難しさ</span></div></div></section>";
  var data = { slug: slug, name: t.name, title: sc.title, job: sc.job, level: sc.level, panel: sc.panel, steps: sc.steps, incidents: sc.incidents, keys: SKEY, init: SIM_INIT, fx: SFX, sev: SSEV };
  h += "<section class=\"simsec\" id=\"play\"><div class=\"wrap wide\"><div class=\"sim\" id=\"sim\" data-v=\"" + sc.visual + "\"" + Object.keys(SIM_INIT).map(function(k){ return " data-" + k + "=\"" + sv(SIM_INIT[k]) + "\""; }).join("") + ">" +
    "<div class=\"sim-top\"><div class=\"phases\" id=\"simph\">" + ph.map(function(p){ return "<span>" + esc(p) + "</span>"; }).join("") + "</div><div class=\"sco\"><span class=\"lbl\" lang=\"en\">SCORE</span><b id=\"simsc\">100</b><span class=\"lbl\">トラブル</span><b id=\"siminc\">0</b></div></div>" +
    "<div class=\"sim-main\"><div class=\"sim-l\"><div class=\"vis\">" + simSvg(sc.visual, t.name + "の機内（模式図）") +
    "<div class=\"tower\" aria-hidden=\"true\"><i class=\"r\"></i><i class=\"y\"></i><i class=\"g\"></i></div><div class=\"vtag\" id=\"simtag\" aria-hidden=\"true\"></div>" +
    "<div class=\"hz\" aria-hidden=\"true\"><svg viewBox=\"0 0 64 56\"><path d=\"M32 3 61 53H3Z\" fill=\"#ffcc00\" stroke=\"#111\" stroke-width=\"3\" stroke-linejoin=\"round\"/><path d=\"M32 20v16\" stroke=\"#111\" stroke-width=\"6\" stroke-linecap=\"round\"/><circle cx=\"32\" cy=\"44\" r=\"3.6\" fill=\"#111\"/></svg><b>危険</b></div></div>" +
    "<div class=\"ctrl\"><div class=\"scr\" aria-live=\"off\"><div class=\"r1\"><span id=\"simmode\" lang=\"en\">—</span><span id=\"simstat\" lang=\"en\">POWER OFF</span></div><div class=\"r2\" id=\"simpos\"></div><div class=\"r3\" id=\"simmsg\"></div></div>" + simPanel(sc) + "</div></div>" +
    "<div class=\"sim-r\"><div class=\"scard\" id=\"simcard\"><p class=\"eyebrow\" lang=\"en\">TODAY'S JOB</p><h2 class=\"jt\">" + esc(sc.title) + "</h2><p class=\"job\">" + esc(sc.job) + "</p>" +
    "<div class=\"modes\"><button type=\"button\" class=\"cta\" data-start=\"practice\">練習モードで始める</button><button type=\"button\" class=\"cta ghost\" data-start=\"exam\">本番モード（ヒントなし）</button></div>" +
    "<p class=\"note\">操作を間違えると、現場で実際に起きるトラブルが再現されます。100点から、トラブルの重さに応じて減点されます。</p>" +
    "<noscript><p class=\"note\">このトレーニングはJavaScriptを使います。下の「手順の解説」と「起きやすいトラブル」はそのまま読めます。</p></noscript></div></div></div>" +
    "<div class=\"modal\" id=\"simmodal\" hidden></div></div></div>" +
    "<script type=\"application/json\" id=\"simdata\">" + JSON.stringify(data).replace(/</g, "\\u003c") + "<\/scr" + "ipt></section>";
  h += mtSec("FLOW", "トレーニングの流れ", "<ol class=\"simflow\">" + ph.map(function(p){
    return "<li><b>" + esc(p) + "</b><span>" + sc.steps.filter(function(s){ return s.phase === p; }).map(function(s){ return esc(s.title); }).join("、") + "</span></li>"; }).join("") + "</ol>");
  h += mtSec("ANSWERS", "手順の解説（正しい操作と理由）", "<details class=\"simans\"><summary>解説を開く（答えが表示されます）</summary><ol>" + sc.steps.map(function(s, i){
    var w = simWrongs(sc, s);
    return "<li><span class=\"no\">" + (i + 1) + "</span><div><p class=\"ph\">" + esc(s.phase) + "</p><h3>" + esc(s.title) + "</h3><p class=\"q\">" + esc(s.text) + "</p><p class=\"a\">" + esc(simAnswer(s)) + "</p><p>" + esc(s.explain) + "</p>" +
      (w.length ? "<ul class=\"wr\">" + w.map(function(x){ return "<li>" + esc(x[0]) + " → <a href=\"#" + x[2] + "\">" + esc(x[1]) + "</a></li>"; }).join("") + "</ul>" : "") + "</div></li>";
  }).join("") + "</ol></details>", "paper");
  var bySev = ids.slice().sort(function(a, b){ return sc.incidents[b].sev - sc.incidents[a].sev; });
  h += mtSec("TROUBLES", t.name + "で起きやすいトラブルと対策", "<p class=\"sub\" style=\"font-size:16px;margin:-24px 0 28px\">このトレーニングで起きる" + ids.length + "件のトラブル（うち重大" + n3 + "件）。何が起き、なぜ起き、どれだけの損失になり、どう防ぐかをまとめています。</p><div class=\"incs\">" + bySev.map(function(k){ return simIncCard(sc, k); }).join("") + "</div>");
  h += mtSec("SAFETY", "安全の基本", "<ul class=\"simli\">" + sc.safety.map(function(x){ return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>", "paper");
  h += mtSec("FOR SALES", "商談で役立つ現場の視点", "<ul class=\"simli\">" + sc.sales.map(function(x){ return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" +
    "<p class=\"simnote\">手順・数値は一般的な例です。実際の操作は、機械の取扱説明書と職場の作業標準に従ってください。</p>");
  h += mtSec("MORE", "あわせて読む", "<div class=\"list\"><a class=\"li\" href=\"" + mtU("type", slug) + "\"><span class=\"t\">" + esc(t.name) + "の構造と仕組み</span><span class=\"n\">MACHINE</span></a>" +
    "<a class=\"li\" href=\"/machine-tools/troubles/\"><span class=\"t\">工作機械のトラブル事例集</span><span class=\"n\">CASEBOOK</span></a><a class=\"li\" href=\"/machine-tools/training/\"><span class=\"t\">ほかの機械の操作トレーニング</span><span class=\"n\">TRAINING</span></a></div>", "paper");
  var i = SIM_ORDER.indexOf(slug), p = SIM_ORDER[i - 1], n = SIM_ORDER[i + 1];
  h += "<div class=\"wrap\"><nav class=\"next\" aria-label=\"前後のトレーニング\">" + (p ? "<a href=\"/machine-tools/" + p + "/training/\"><small>PREVIOUS</small><b>" + esc(simTypeName(p)) + "の操作トレーニング</b></a>" : "<span></span>") + (n ? "<a href=\"/machine-tools/" + n + "/training/\"><small>NEXT</small><b>" + esc(simTypeName(n)) + "の操作トレーニング</b></a>" : "") + "</nav></div><div style=\"height:40px\"></div>";
  show(h, [["工作機械図鑑", "/machine-tools/"], ["操作トレーニング", "/machine-tools/training/"], [t.name]], "mt");
}

function simCard(slug){
  var sc = SIM[slug], t = mtBy(MTD.types, slug);
  return "<a class=\"card simcard\" href=\"/machine-tools/" + slug + "/training/\" data-simbest=\"" + slug + "\"><div class=\"stage thumb\">" + mtImg(slug, t.name + "の図") + "</div><div class=\"tx\"><p class=\"eyebrow\" lang=\"en\">LEVEL " + sc.level + " · " + sc.steps.length + " STEPS · " + sc.minutes + " MIN</p><h3>" + esc(t.name) + "</h3><p>" + esc(sc.title) + "</p><span class=\"best\" hidden></span></div></a>";
}
function mtSimHub(){
  var nInc = 0, n3 = 0;
  SIM_ORDER.forEach(function(s){ Object.keys(SIM[s].incidents).forEach(function(k){ nInc++; if(SIM[s].incidents[k].sev === 3) n3++; }); });
  var h = "<section class=\"hero night\"><div class=\"wrap t\"><p class=\"eyebrow\">OPERATION TRAINING</p><h1 class=\"d1\"><span class=\"nw\">工作機械の</span><span class=\"nw\">操作トレーニング</span></h1>" +
    "<p class=\"sub\">電源を入れる、ワークをつかむ、工具の位置を教える、1個目を削る。" + SIM_ORDER.length + "機種の基本操作を、自分の手で1ステップずつ体験します。間違えると、現場で実際に起きる衝突や飛散、不良が再現されます。</p>" +
    "<p class=\"ctas\"><a class=\"cta\" href=\"#machines\">機械を選ぶ</a><a class=\"lnk\" href=\"/machine-tools/troubles/\">トラブル事例集を見る</a></p></div>" +
    "<div class=\"wrap\"><div class=\"hstats\"><div><b class=\"tn\">" + SIM_ORDER.length + "</b><span>機種</span></div><div><b class=\"tn\">" + SIM_ORDER.reduce(function(a, s){ return a + SIM[s].steps.length; }, 0) + "</b><span>ステップ</span></div><div><b class=\"tn\">" + nInc + "</b><span>トラブル</span></div><div><b class=\"tn\">" + n3 + "</b><span>重大トラブル</span></div></div></div></section>";
  h += "<section class=\"sec tight\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">HOW IT WORKS</p><h2 class=\"d3\">遊び方</h2></div><ol class=\"how\">" +
    "<li><b>今日の仕事を読む</b><span>材料、寸法、段取りの状況が示されます。練習モードではヒントを見られます。</span></li>" +
    "<li><b>自分で操作する</b><span>始業点検、操作盤のボタン、ワークの取付け、補正値の入力、ハンドルでの寄せ。手順どおりに進めると、機械の図が動きます。</span></li>" +
    "<li><b>失敗から学ぶ</b><span>間違えるとトラブルが起き、何が起きたか・原因・損失・防ぎ方が表示されます。最後に得点と評価が出ます。</span></li></ol>" +
    "<p class=\"sub\" style=\"font-size:16px;margin-top:32px\">現場で機械を動かしたことのない営業・技術・購買の担当者が、機械の動きと「なぜその手順なのか」をつかむための教材です。新人オペレータの復習や、段取りのリスクを説明する資料にも使えます。手順・数値は一般的な例で、実際の操作は機械の取扱説明書と職場の作業標準に従ってください。</p></div></section>";
  h += "<section class=\"sec paper\" id=\"machines\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\">MACHINES</p><h2 class=\"d2\">機械を選ぶ。</h2></div>";
  MTD.fam.forEach(function(f, fi){
    var l = SIM_ORDER.filter(function(s){ return mtBy(MTD.types, s).fam === f.id; });
    if(!l.length) return;
    h += "<div class=\"famh f" + (fi % 5) + "\"" + (fi ? "" : " style=\"margin-top:0\"") + "><i></i><b>" + esc(f.n) + "</b><small lang=\"en\">" + esc(f.en) + "</small></div><div class=\"grid-cards\">" + l.map(simCard).join("") + "</div>";
  });
  h += "</div></section>";
  show(h, [["工作機械図鑑", "/machine-tools/"], ["操作トレーニング"]], "mt");
}

var SKIND = [["crash", "衝突・工具の破損", "工具やワークが機械の一部とぶつかるトラブル。原点やオフセットの入力ミス、1個目を確認せずに流す、退避の順番の誤りが主な原因です。工具だけでなく、主軸やタレットの芯ずれまで及ぶと修理と精度調整で長く止まります。", ["crash"]],
  ["fly", "飛散・破裂", "ワークや工具、といしが機内で飛ぶトラブル。把握力や回転数の設定、といしの点検と試運転、機内の置き忘れが関わります。ドアや安全カバーが人を守る最後の壁です。", ["fly", "burst"]],
  ["fire", "火災・発煙・過熱", "油性の切削油や加工液、切りくずの堆積、レーザの反射などが原因になります。無人運転中の発火は被害が大きく、消火設備と監視が欠かせません。", ["fire", "smoke"]],
  ["hazard", "人への危険", "巻き込まれ、挟まれ、感電、やけど、目の障害など、人に直接かかわるトラブル。安全装置を無効にしない、停止とロックアウトを守ることが基本です。", ["hazard"]],
  ["quality", "品質不良（寸法・面・焼け・ずれ）", "機械は壊れていなくても、不良品を作り続けてしまうトラブル。補正値の符号や半径・直径の取り違え、暖機不足、研削焼け、ビビりなどがあります。", ["deform", "burn", "chatter", "slip"]],
  ["stop", "停止・アラーム・設備の不具合", "保護機能が働いて止まる、液があふれる、ワイヤが切れるなど。止まること自体は機械を守る働きですが、原因を取り除かないと稼働率が下がります。", ["alarm", "leak", "wirebreak"]]];
function mtTroubles(){
  var all = [];
  SIM_ORDER.forEach(function(s){ var sc = SIM[s]; Object.keys(sc.incidents).forEach(function(k){ all.push({ s: s, k: k, I: sc.incidents[k] }); }); });
  var n3 = all.filter(function(x){ return x.I.sev === 3; }).length;
  var h = "<section class=\"phero wrap\"><p class=\"eyebrow\" lang=\"en\">TROUBLE CASEBOOK</p><h1 class=\"d2\">工作機械のトラブル事例集</h1><p class=\"sub lead\" style=\"margin:20px auto 0\">操作トレーニングで起きる" + all.length + "件のトラブル（うち重大" + n3 + "件）を、種類ごとにまとめました。工作機械の事故や不良の多くは、段取り替えの直後、補正値の入力、安全装置の扱いで起きます。原因と損失、防ぎ方は各トレーニングのページで読めます。</p></section>";
  h += "<div class=\"wrap\"><nav class=\"tkinds\" aria-label=\"トラブルの種類\">" + SKIND.map(function(kd){ var n = all.filter(function(x){ return kd[3].indexOf(x.I.fx) >= 0; }).length; return "<a href=\"#tk-" + kd[0] + "\"><b>" + esc(kd[1]) + "</b><span class=\"tn\">" + n + "</span></a>"; }).join("") + "</nav></div>";
  SKIND.forEach(function(kd, i){
    var l = all.filter(function(x){ return kd[3].indexOf(x.I.fx) >= 0; }).sort(function(a, b){ return b.I.sev - a.I.sev; });
    h += "<section class=\"sec tight" + (i % 2 ? " paper" : "") + "\" id=\"tk-" + kd[0] + "\"><div class=\"wrap\"><div class=\"hd\"><p class=\"eyebrow\" lang=\"en\">" + kd[0].toUpperCase() + "</p><h2 class=\"d3\">" + esc(kd[1]) + "</h2><p class=\"sub\" style=\"font-size:16px\">" + esc(kd[2]) + "</p></div><ul class=\"tlist\">" +
      l.map(function(x){ return "<li><a href=\"/machine-tools/" + x.s + "/training/#" + x.k + "\"><span class=\"sev s" + x.I.sev + "\">" + SSEV[x.I.sev] + "</span><b>" + esc(x.I.title) + "</b><small>" + esc(simTypeName(x.s)) + "</small></a></li>"; }).join("") + "</ul></div></section>";
  });
  h += mtSec("TRAINING", "トレーニングで体験する", "<div class=\"pills\">" + SIM_ORDER.map(function(s){ return "<a class=\"pill\" href=\"/machine-tools/" + s + "/training/\">" + esc(simTypeName(s)) + "</a>"; }).join("") + "</div>");
  show(h, [["工作機械図鑑", "/machine-tools/"], ["トラブル事例集"]], "mt");
}
function mtSimLink(slug){
  var sc = SIM[slug]; if(!sc) return "";
  return "<section class=\"sec tight\" style=\"padding-bottom:0\"><div class=\"wrap\"><a class=\"mtlink simlink\" href=\"/machine-tools/" + slug + "/training/\"><span class=\"eyebrow\" lang=\"en\">OPERATION TRAINING</span><b>" + esc(sc.title) + "</b><span>操作を1ステップずつ体験する。間違えると起きるトラブル" + Object.keys(sc.incidents).length + "件と、その原因・対策も読めます</span><span class=\"lnk\">トレーニングを始める</span></a><p style=\"margin-top:14px\"><a class=\"lnk\" href=\"/machine-tools/troubles/\">ほかの機械も含めたトラブル事例集を見る</a></p></div></section>";
}
