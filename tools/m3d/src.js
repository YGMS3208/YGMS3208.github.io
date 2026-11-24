/* 3D viewers for the atlas.
   A page asks for one with <figure class="m3d" data-3d="<scene>" data-*="…">; app.js loads this module
   when the figure comes near and calls mount(figure). Each scene builds a small, procedurally modelled
   mechanism that moves the way the real one does. Look and feel follow the site's isometric drawings:
   orthographic camera at the isometric angle, light steel with dark outlines, blue for what moves.
   Rules: see CLAUDE.md (3D section). */
import {
  WebGLRenderer, Scene, OrthographicCamera, Group, Mesh, LineSegments, Line, LineLoop, EdgesGeometry, BufferGeometry,
  BoxGeometry, CylinderGeometry, SphereGeometry, TorusGeometry, ConeGeometry, ExtrudeGeometry, LatheGeometry, TubeGeometry,
  CircleGeometry, PlaneGeometry, Shape, Path, Curve, Vector2, Vector3, Box3, Sphere, Color, MeshStandardMaterial,
  MeshBasicMaterial, LineBasicMaterial, LineDashedMaterial, HemisphereLight, DirectionalLight, CanvasTexture,
  Float32BufferAttribute, MathUtils, DoubleSide, SRGBColorSpace
} from "three";

const TAU = Math.PI * 2;
const RM = matchMedia("(prefers-reduced-motion: reduce)");

/* ---------- look ---------- */
function css(name, fb){ const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim(); return v || fb; }
function palette(){
  const dark = matchMedia("(prefers-color-scheme: dark)").matches && document.documentElement.getAttribute("data-theme") !== "light"
    || document.documentElement.getAttribute("data-theme") === "dark";
  return {
    dark,
    ink: css("--ink", dark ? "#EFEDE7" : "#161512"),
    accent: css("--accent", dark ? "#86A0FF" : "#25459A"),
    mark: css("--mark", dark ? "#E07150" : "#B8401F"),
    steel: dark ? "#9aa3ad" : "#d9dee3",
    steel2: dark ? "#7d8691" : "#b9c1c9",
    iron: dark ? "#5d646d" : "#8e959d",
    paint: dark ? "#6f7d70" : "#c9d3c4",
    warm: dark ? "#8c7f69" : "#e6dcc8",
    edge: dark ? "#0b0b0a" : "#2b2a27"
  };
}
function mats(P){
  const std = (c, o = {}) => new MeshStandardMaterial(Object.assign({ color: new Color(c), roughness: .55, metalness: .18 }, o));
  return {
    steel: std(P.steel), steel2: std(P.steel2), iron: std(P.iron, { roughness: .7 }), paint: std(P.paint, { roughness: .8, metalness: .05 }),
    warm: std(P.warm, { roughness: .85, metalness: 0 }),
    accent: std(P.accent, { roughness: .45, metalness: .25 }),
    ball: std(P.mark, { roughness: .3, metalness: .35 }),
    glass: std(P.steel, { transparent: true, opacity: .22, depthWrite: false, side: DoubleSide }),
    edge: new LineBasicMaterial({ color: new Color(P.edge), transparent: true, opacity: P.dark ? .55 : .5 }),
    edgeSoft: new LineBasicMaterial({ color: new Color(P.edge), transparent: true, opacity: .16 }),
    line: new LineBasicMaterial({ color: new Color(P.accent) }),
    pitch: new MeshBasicMaterial({ color: new Color(P.mark) }),
    dash: new LineDashedMaterial({ color: new Color(P.accent), dashSize: .18, gapSize: .12 })
  };
}
/* a mesh with the drawing's outline */
function part(geo, mat, M, edges = 30, soft){
  const g = new Group(), m = new Mesh(geo, mat); g.add(m);
  if(edges !== false){ const e = new LineSegments(new EdgesGeometry(geo, edges), soft ? M.edgeSoft : M.edge); g.add(e); }
  g.userData.mesh = m; return g;
}
function at(o, x, y, z){ o.position.set(x, y, z); return o; }
/* soft contact shadow, like the ellipse under every drawing */
function shadow(w, d){
  const c = document.createElement("canvas"); c.width = c.height = 128; const x = c.getContext("2d");
  const gr = x.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, "rgba(0,0,0,.30)"); gr.addColorStop(.55, "rgba(0,0,0,.10)"); gr.addColorStop(1, "rgba(0,0,0,0)");
  x.fillStyle = gr; x.fillRect(0, 0, 128, 128);
  const t = new CanvasTexture(c); t.colorSpace = SRGBColorSpace;
  const m = new Mesh(new PlaneGeometry(w, d), new MeshBasicMaterial({ map: t, transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.renderOrder = -1; m.userData.noFit = true; return m;
}
/* a curved arrow round an axis (for rotary axes) */
function arcArrow(r, M, span = 1.3, thick = .035){
  const g = new Group();
  const tor = new Mesh(new TorusGeometry(r, thick, 8, 48, span), M.accent); g.add(tor);
  const cone = new Mesh(new ConeGeometry(thick * 3.2, thick * 9, 16), M.accent);
  cone.position.set(r * Math.cos(span), r * Math.sin(span), 0); cone.rotation.z = span; g.add(cone);
  return g;
}
function straightArrow(len, M, thick = .03){
  const g = new Group();
  const shaft = new Mesh(new CylinderGeometry(thick, thick, len, 10), M.accent); g.add(shaft);
  for(const s of [1, -1]){ const c = new Mesh(new ConeGeometry(thick * 3.2, thick * 9, 16), M.accent); c.position.y = s * len / 2; if(s < 0) c.rotation.z = Math.PI; g.add(c); }
  return g;
}

/* ---------- scenes ---------- */
/* each scene: (M, P, opts) -> { root, labels:[{text, obj, at:Vector3, key?}], update(t, dt), toggles?:[{label, on, set(on)}], fit? } */
const SCENES = {};

/* Involute gear pair. data-z1, data-z2 (teeth), data-helix (deg, 0 = spur), data-toggle="helix" */
function gearShape(z, m, alpha){
  const r = m * z / 2, rb = r * Math.cos(alpha), ra = r + m, rf = r - 1.25 * m;
  const inv = a => Math.tan(a) - a;
  const half = Math.PI / (2 * z) + inv(alpha);
  const N = 7, pts = [];
  const flank = (c, side) => {
    const out = [], r0 = Math.max(rf, rb);
    for(let k = 0; k <= N; k++){
      const rr = r0 + (ra - r0) * k / N, a = Math.acos(Math.min(1, rb / rr));
      const ang = c + side * (half - inv(a)); out.push([rr, ang]);
    }
    if(rf < rb) out.unshift([rf, out[0][1]]);
    return out;
  };
  for(let i = 0; i < z; i++){
    const c = TAU * i / z;
    const L = flank(c, -1), R = flank(c, 1).reverse();
    L.forEach(p => pts.push(p));
    const a0 = L[L.length - 1][1], a1 = R[0][1];
    for(let k = 1; k < 3; k++){ pts.push([ra, a0 + (a1 - a0) * k / 3]); }
    R.forEach(p => pts.push(p));
    const n0 = R[R.length - 1][1]; /* root arc up to the next tooth's left flank */
    const nl = flank(TAU * (i + 1) / z, -1)[0][1];
    for(let k = 1; k < 4; k++){ pts.push([rf, n0 + (nl - n0) * k / 4]); }
  }
  const s = new Shape(pts.map(([rr, a]) => new Vector2(rr * Math.cos(a), rr * Math.sin(a))));
  const hole = new Path(); hole.absarc(0, 0, Math.max(r * .28, m * 1.6), 0, TAU, true); s.holes.push(hole);
  return { shape: s, r, ra, rf };
}
function gearMesh(z, m, width, helixDeg, M, mat){
  const { shape, r, ra } = gearShape(z, m, 20 * Math.PI / 180);
  const geo = new ExtrudeGeometry(shape, { depth: width, bevelEnabled: false, steps: helixDeg ? 10 : 1, curveSegments: 4 });
  geo.translate(0, 0, -width / 2);
  if(helixDeg){
    const k = Math.tan(helixDeg * Math.PI / 180) / r, p = geo.attributes.position;
    for(let i = 0; i < p.count; i++){
      const x = p.getX(i), y = p.getY(i), zz = p.getZ(i), a = zz * k, c = Math.cos(a), s = Math.sin(a);
      p.setXY(i, x * c - y * s, x * s + y * c);
    }
    geo.computeVertexNormals();
  }
  geo.rotateX(-Math.PI / 2);
  const g = part(geo, mat, M, 35);
  /* pitch circle on the top face */
  const circ = new Mesh(new TorusGeometry(r, m * .07, 6, 96), M.pitch); circ.rotation.x = Math.PI / 2; circ.position.y = width / 2 + .01; g.add(circ);
  const hub = part(new CylinderGeometry(Math.max(r * .28, m * 1.6) * .98, Math.max(r * .28, m * 1.6) * .98, width * 2.2, 32), M.iron, M);
  g.add(hub);
  g.userData.r = r; g.userData.ra = ra;
  return g;
}
SCENES.gears = (M, P, o) => {
  const z1 = +(o.z1 || 18), z2 = +(o.z2 || 30), m = .26, w = .9;
  let helix = +(o.helix || 0);
  const root = new Group(), a = m * (z1 + z2) / 2;
  const sh = shadow(a * 2.6, a * 2.2); sh.position.set(a / 2, -w * 1.15, 0); root.add(sh);
  let g1, g2, phase2;
  const build = () => {
    if(g1){ root.remove(g1); root.remove(g2); }
    g1 = gearMesh(z1, m, w, helix, M, M.accent); g2 = gearMesh(z2, m, w, -helix, M, M.steel);
    g2.position.x = a; root.add(g1); root.add(g2);
    phase2 = Math.PI + Math.PI / z2;
  };
  build();
  const ratio = z1 / z2;
  return {
    root,
    labels: [
      { text: `駆動歯車（${z1}歯）`, at: () => new Vector3(-m * z1 / 2 * .2, w * .6, m * z1 / 2 * .9) },
      { text: `被動歯車（${z2}歯）`, at: () => new Vector3(a + m * z2 / 2 * .35, w * .6, m * z2 / 2 * .9) },
      { text: "ピッチ円（朱の線）どうしが接して転がる", at: () => new Vector3(a / 2 + m * (z1 - z2) / 4, w * .55, -m * 2), dim: true }
    ],
    note: `歯数比 ${z2}:${z1}。被動歯車は ${(ratio).toFixed(2)} 倍の速さで逆向きに回る`,
    update(t){ const th = t * .6; g1.rotation.y = th; g2.rotation.y = -th * ratio + phase2; },
    toggles: o.toggle === "helix" ? [{ label: "はすば歯車にする", on: !!helix, set(on){ helix = on ? 22 : 0; build(); } }] : null
  };
};

/* Ball screw: shaft turns, the nut moves one lead per turn, balls run round the helix and back through the return tube */
class Helix extends Curve {
  constructor(r, lead, turns, x0){ super(); this.r = r; this.lead = lead; this.turns = turns; this.x0 = x0; }
  getPoint(t, v = new Vector3()){ const a = TAU * this.turns * t; return v.set(this.x0 + this.lead * this.turns * t, this.r * Math.cos(a), this.r * Math.sin(a)); }
}
class Bez extends Curve {
  constructor(p0, p1, p2, p3){ super(); this.p = [p0, p1, p2, p3]; }
  getPoint(t, v = new Vector3()){
    const [a, b, c, d] = this.p, u = 1 - t;
    return v.set(0, 0, 0).addScaledVector(a, u * u * u).addScaledVector(b, 3 * u * u * t).addScaledVector(c, 3 * u * t * t).addScaledVector(d, t * t * t);
  }
}
SCENES.ballscrew = (M, P, o) => {
  const R = .55, lead = .5, L = 7, turns = 3, nutL = lead * turns + .5, ballR = .1;
  const root = new Group();
  root.add(at(shadow(L * 1.2, 2.4), 0, -1.35, 0));
  /* supports and motor */
  for(const s of [-1, 1]){
    const b = part(new BoxGeometry(.6, 1.6, 1.3), M.paint, M); b.position.set(s * (L / 2 + .2), -.45, 0); root.add(b);
  }
  const motor = part(new BoxGeometry(1.1, 1.1, 1.1), M.iron, M); motor.position.set(-L / 2 - 1.05, 0, 0); root.add(motor);
  /* shaft with its thread */
  const shaft = new Group(); root.add(shaft);
  const core = part(new CylinderGeometry(R * .82, R * .82, L, 40, 1), M.steel, M, 30); core.rotation.z = Math.PI / 2; shaft.add(core);
  const thread = new Mesh(new TubeGeometry(new Helix(R * .86, lead, L / lead, -L / 2), Math.round(L / lead * 40), R * .2, 8, false), M.steel2); shaft.add(thread);
  /* nut */
  const nut = new Group(); root.add(nut);
  const shell = new Mesh(new CylinderGeometry(R * 1.55, R * 1.55, nutL, 40, 1, true), M.glass); shell.rotation.z = Math.PI / 2; nut.add(shell);
  const shellE = new LineSegments(new EdgesGeometry(new CylinderGeometry(R * 1.55, R * 1.55, nutL, 40, 1, true), 30), M.edge); shellE.rotation.z = Math.PI / 2; nut.add(shellE);
  const fl = part(new CylinderGeometry(R * 2.3, R * 2.3, .22, 40), M.accent, M); fl.rotation.z = Math.PI / 2; fl.position.x = -nutL / 2 - .11; nut.add(fl);
  /* ball path in the nut's frame: helix + return tube over the top */
  const h = new Helix(R, lead, turns, -nutL / 2 + .25);
  const p0 = h.getPoint(1), p1 = h.getPoint(0);
  const top = R * 2.35;
  const ret = new Bez(p0.clone(), new Vector3(p0.x + .3, top, p0.z * .3), new Vector3(p1.x - .3, top, p1.z * .3), p1.clone());
  const retTube = new Mesh(new TubeGeometry(ret, 40, ballR * 1.6, 10, false), M.glass); nut.add(retTube);
  nut.add(new LineSegments(new EdgesGeometry(new TubeGeometry(ret, 12, ballR * 1.6, 6, false), 40), M.edgeSoft));
  const hl = h.getLength(), rl = ret.getLength(), loop = hl + rl;
  const n = Math.floor(loop / (ballR * 2.15));
  const balls = []; const bg = new SphereGeometry(ballR, 14, 10);
  for(let i = 0; i < n; i++){ const b = new Mesh(bg, M.ball); nut.add(b); balls.push(b); }
  const pt = new Vector3();
  let glass = true;
  return {
    root,
    labels: [
      { text: "ねじ軸（回る）", at: () => new Vector3(-L * .3, R * 1.1, 0) },
      { text: "ナット（進む）", obj: nut, at: () => new Vector3(-nutL / 2 - .1, -R * 2.3, 0) },
      { text: "ボール（ねじ溝を転がる）", obj: nut, at: () => new Vector3(nutL / 2, -R * .6, R * 1.4) },
      { text: "リターン経路（元の位置へ戻る）", obj: nut, at: () => new Vector3(0, top + .25, 0), dim: true },
      { text: "サーボモータ", at: () => new Vector3(-L / 2 - 1.05, .7, 0), dim: true }
    ],
    note: "ねじ軸が1回転すると、ナットはリード（ねじ1山ぶん）だけ進む。ボールはすべらずに転がり、端まで来るとリターン経路で戻る",
    update(t){
      const ang = Math.sin(t * .35) * (L - nutL - 1) / lead * Math.PI;  /* shaft angle */
      shaft.rotation.x = ang;
      nut.position.x = ang / TAU * lead;
      /* balls roll at half the relative speed */
      const s0 = ((ang / TAU) * hl / turns * .5) % loop;
      for(let i = 0; i < n; i++){
        let s = (s0 + i * loop / n) % loop; if(s < 0) s += loop;
        if(s < hl) h.getPointAt(s / hl, pt); else ret.getPointAt((s - hl) / rl, pt);
        balls[i].position.copy(pt);
      }
    },
    toggles: [{ label: "ナットを透かす", on: true, set(on){ glass = on; shell.material = on ? M.glass : M.steel2; retTube.material = on ? M.glass : M.steel2; } }]
  };
};

/* Linear guide: the block slides on the rail, balls circulate inside it */
SCENES.lguide = (M, P, o) => {
  const L = 8, bw = 1.7, bl = 2.4, rail = { w: .9, h: .8 }, ballR = .085;
  const root = new Group();
  root.add(at(shadow(L * 1.15, 2.6), 0, -.05, 0));
  const base = part(new BoxGeometry(L + .6, .3, 2.4), M.warm, M, 30, true); base.position.y = -.15; root.add(base);
  const r = part(new BoxGeometry(L, rail.h, rail.w), M.steel, M); r.position.y = rail.h / 2; root.add(r);
  for(let x = -L / 2 + .5; x < L / 2; x += 1){ const hole = new Mesh(new CylinderGeometry(.12, .12, .02, 16), M.iron); hole.position.set(x, rail.h + .005, 0); root.add(hole); }
  const block = new Group(); root.add(block);
  const by = rail.h * .45 + .55;
  const body = new Mesh(new BoxGeometry(bl, 1.1, bw), M.glass); body.position.y = by; block.add(body);
  block.add(at(new LineSegments(new EdgesGeometry(new BoxGeometry(bl, 1.1, bw)), M.edge), 0, by, 0));
  for(const s of [-1, 1]){
    const cap = part(new BoxGeometry(.18, 1.1, bw), M.accent, M); cap.position.set(s * (bl / 2 + .09), by, 0); block.add(cap);
    const seal = part(new BoxGeometry(.06, 1.0, bw * .96), M.iron, M); seal.position.set(s * (bl / 2 + .21), by - .02, 0); block.add(seal);
  }
  /* four ball loops: load row against the rail groove, return row inside the block */
  const loops = [];
  for(const side of [-1, 1]) for(const lvl of [0, 1]){
    const y = rail.h * (lvl ? .82 : .5), zl = side * (rail.w / 2 + ballR * .6), zr = side * (rail.w / 2 + .2 + lvl * .1);
    const half = bl / 2 + .02, rad = Math.abs(zr - zl) / 2, zc = (zl + zr) / 2;
    const segs = [half * 2, Math.PI * rad, half * 2, Math.PI * rad], tot = segs.reduce((a, b) => a + b);
    const at = (s, v) => {
      s = ((s % tot) + tot) % tot;
      if(s < segs[0]) return v.set(-half + s, y, zl);
      s -= segs[0];
      if(s < segs[1]){ const a = s / rad; return v.set(half + Math.sin(a) * rad, y, zc - side * Math.cos(a) * rad); }
      s -= segs[1];
      if(s < segs[2]) return v.set(half - s, y, zr);
      s -= segs[2]; const a = s / rad; return v.set(-half - Math.sin(a) * rad, y, zc + side * Math.cos(a) * rad);
    };
    const n = Math.floor(tot / (ballR * 2.2)), balls = [];
    for(let i = 0; i < n; i++){ const b = new Mesh(new SphereGeometry(ballR, 12, 8), M.ball); block.add(b); balls.push(b); }
    loops.push({ at, n, balls, tot, dir: 1 });
  }
  const v = new Vector3(); let travel = 0;
  return {
    root,
    labels: [
      { text: "レール", at: () => new Vector3(-L * .4, rail.h + .05, 0) },
      { text: "ブロック（進む）", obj: block, at: () => new Vector3(0, by + .7, 0) },
      { text: "ボール（無限に循環）", obj: block, at: () => new Vector3(-bl / 2 - .1, rail.h * .5, rail.w / 2 + .3) },
      { text: "エンドプレート・シール", obj: block, at: () => new Vector3(bl / 2 + .25, by + .45, -bw / 2), dim: true }
    ],
    note: "ブロックが進むと、レールとの間のボールは転がって後ろへ送られ、ブロック内の戻り穴を通って前へ戻る。すべりがないので軽く、精度が長く保たれる",
    update(t){
      const x = Math.sin(t * .45) * (L / 2 - bl / 2 - .6);
      travel = x; block.position.x = x;
      for(const lp of loops){
        const s0 = -x * .5 * 1;  /* balls in contact move back at half speed relative to the block */
        for(let i = 0; i < lp.n; i++){ lp.at(s0 + i * lp.tot / lp.n, v); lp.balls[i].position.copy(v); }
      }
    },
    toggles: [{ label: "ブロックを透かす", on: true, set(on){ body.material = on ? M.glass : M.steel2; } }]
  };
};

/* Trunnion-type 5-axis: A tilts the cradle, C turns the table, the tool stays upright */
SCENES.fiveaxis = (M, P, o) => {
  const root = new Group();
  root.add(at(shadow(7.5, 5.5), 0, -.02, 0));
  const bed = part(new BoxGeometry(6.4, .5, 4.2), M.paint, M); bed.position.y = .25; root.add(bed);
  for(const s of [-1, 1]){ const p = part(new BoxGeometry(.7, 2.0, 1.6), M.paint, M); p.position.set(s * 2.75, 1.5, 0); root.add(p); }
  const cradle = new Group(); cradle.position.y = 2.0; root.add(cradle);
  const cb = part(new BoxGeometry(4.3, .35, 2.2), M.steel, M); cb.position.y = -.6; cradle.add(cb);
  for(const s of [-1, 1]){ const w = part(new BoxGeometry(.35, 1.0, 2.2), M.steel, M); w.position.set(s * 2.15, -.25, 0); cradle.add(w);
    const ax = part(new CylinderGeometry(.32, .32, .5, 24), M.iron, M); ax.rotation.z = Math.PI / 2; ax.position.set(s * 2.45, 0, 0); cradle.add(ax); }
  const table = new Group(); table.position.y = -.42; cradle.add(table);
  table.add(part(new CylinderGeometry(1.45, 1.45, .28, 48), M.accent, M, 40));
  const work = new Group(); work.position.y = .14; table.add(work);
  const wk = part(new CylinderGeometry(.75, .95, .9, 6), M.warm, M); wk.position.y = .45; work.add(wk);
  const head = new Group(); root.add(head);
  const col = part(new BoxGeometry(1.0, 2.4, 1.0), M.paint, M, 30, true); col.position.set(0, 5.6, -1.9); head.add(col);
  const hs = part(new BoxGeometry(1.1, 1.5, 1.6), M.steel2, M); hs.position.set(0, 5.2, -.6); head.add(hs);
  const sp = part(new CylinderGeometry(.38, .38, .9, 32), M.steel, M); sp.position.set(0, 4.05, -.1); head.add(sp);
  const tool = part(new CylinderGeometry(.09, .09, 1.0, 16), M.iron, M); tool.position.set(0, 3.15, -.1); head.add(tool);
  const aA = arcArrow(.85, M, 1.6); aA.rotation.y = Math.PI / 2; aA.position.set(3.35, 2.0, 0); root.add(aA);
  const aC = arcArrow(1.75, M, 1.8); aC.rotation.x = -Math.PI / 2; aC.position.y = .06; table.add(aC);
  const zA = straightArrow(1.0, M); zA.position.set(.85, 4.1, -.1); head.add(zA);
  return {
    root,
    labels: [
      { text: "A軸：クレードルが傾く", at: () => new Vector3(3.35, 2.95, 0), key: "a" },
      { text: "C軸：テーブルが回る", obj: table, at: () => new Vector3(-1.4, .2, 1.2), key: "c" },
      { text: "主軸・工具（X・Y・Zで動く）", at: () => new Vector3(.9, 4.7, -.1) },
      { text: "工作物", obj: work, at: () => new Vector3(0, 1.05, 0), dim: true }
    ],
    note: "工具はまっすぐのまま、テーブル側が傾いて（A軸）回る（C軸）。工作物の5面を、段取り替えなしで工具に向けられる",
    update(t){
      cradle.rotation.x = Math.sin(t * .32) * .62;
      table.rotation.y = t * .28;
      head.position.y = Math.max(0, Math.sin(t * .64 + 1)) * .35;
    }
  };
};

/* Machining center strokes: table X, saddle Y, head Z; the box is what the tool can reach */
SCENES.strokes = (M, P, o) => {
  const sx = +(o.x || 5.2), sy = +(o.y || 3.0), sz = +(o.z || 2.6);
  const root = new Group();
  root.add(at(shadow(sx * 1.9, sy * 2.6), 0, -.02, .4));
  const bed = part(new BoxGeometry(sx * .95, .7, sy * 2.1), M.paint, M); bed.position.set(0, .35, .4); root.add(bed);
  const col = part(new BoxGeometry(1.8, 5.6, 1.6), M.paint, M); col.position.set(0, 3.5, -sy * .85); root.add(col);
  const saddle = new Group(); root.add(saddle);
  saddle.add(at(part(new BoxGeometry(sx * .55, .45, sy * .9), M.steel2, M), 0, .93, 0));
  const table = new Group(); saddle.add(table);
  table.add(at(part(new BoxGeometry(sx * .95, .35, sy * .62), M.steel, M), 0, 1.33, 0));
  for(let k = -1; k <= 1; k++){ const s = new Mesh(new BoxGeometry(sx * .95, .02, .06), M.iron); s.position.set(0, 1.51, k * sy * .18); table.add(s); }
  const work = part(new BoxGeometry(1.2, .7, 1.0), M.warm, M); work.position.set(0, 1.86, 0); table.add(work);
  const head = new Group(); root.add(head);
  head.add(at(part(new BoxGeometry(1.4, 1.6, 1.8), M.steel2, M), 0, 5.0, -sy * .3));
  const sp = part(new CylinderGeometry(.35, .35, .7, 28), M.steel, M); sp.position.set(0, 3.85, -sy * .15 + .2); head.add(sp);
  const tool = part(new CylinderGeometry(.08, .08, .7, 14), M.iron, M); tool.position.set(0, 3.15, -sy * .15 + .2); head.add(tool);
  /* reach box, drawn in dashes, fixed to the table */
  const reach = new LineSegments(new EdgesGeometry(new BoxGeometry(sx * .8, sz * .55, sy * .55)), M.dash);
  reach.computeLineDistances(); reach.position.set(0, 1.5 + sz * .55 / 2, 0); table.add(reach);
  const ax = straightArrow(sx * .5, M); ax.rotation.z = Math.PI / 2; ax.position.set(0, 1.6, sy * .45); table.add(ax);
  const ay = straightArrow(sy * .5, M); ay.rotation.x = Math.PI / 2; ay.position.set(sx * .36, 1.1, 0); saddle.add(ay);
  const az = straightArrow(1.0, M); az.position.set(.95, 4.0, -sy * .15 + .2); head.add(az);
  return {
    root,
    labels: [
      { text: "X：テーブルが左右", obj: table, at: () => new Vector3(-sx * .3, 1.6, sy * .45) },
      { text: "Y：サドルが前後", obj: saddle, at: () => new Vector3(sx * .36, .9, sy * .4) },
      { text: "Z：主軸頭が上下", obj: head, at: () => new Vector3(1.0, 4.7, -sy * .15) },
      { text: "工具が届く範囲（ストローク）", obj: table, at: () => new Vector3(-sx * .4, 1.5 + sz * .55, -sy * .27), dim: true }
    ],
    note: "ストロークは「工具が届く箱」の大きさ。工作物と治具がこの箱に収まり、テーブルや主軸頭が動いても周りに当たらないことを、干渉図で確かめる",
    update(t){
      const ph = (t * .18) % 3, e = x => .5 - .5 * Math.cos(Math.min(1, Math.max(0, x)) * Math.PI);
      const k = Math.floor(ph), f = ph - k;
      table.position.x = (k === 0 ? Math.sin(f * TAU) : 0) * sx * .24;
      saddle.position.z = (k === 1 ? Math.sin(f * TAU) : 0) * sy * .24;
      head.position.y = (k === 2 ? -Math.sin(f * Math.PI) : 0) * .9;
      this.active = ["x", "y", "z"][k];
    }
  };
};

/* Deep-groove ball bearing: inner ring turns, cage at ~0.4x, balls roll */
SCENES.bearing = (M, P, o) => {
  const rows = +(o.rows || 1), Ro = 2.0, Ri = 1.15, w = .9, br = .36, pr = (Ro + Ri) / 2 + .02, nb = 9;
  const root = new Group();
  root.add(at(shadow(5.4, 5.4), 0, -w * rows / 2 - .55, 0));
  /* outer ring with groove facing in, cut away a quarter to show the inside */
  const outerP = [new Vector2(Ro + .55, -w * rows / 2), new Vector2(Ro + .55, w * rows / 2), new Vector2(Ro, w * rows / 2)];
  const gys = rows === 1 ? [0] : [w / 2, -w / 2];
  gys.forEach(gy => { for(let k = 0; k <= 10; k++){ const a = Math.PI / 2 - Math.PI * k / 10; outerP.push(new Vector2(Ro + Math.cos(a) * br * .3, gy + Math.sin(a) * br * 1.05)); } });
  outerP.push(new Vector2(Ro, -w * rows / 2)); outerP.push(outerP[0].clone());
  const outer = part(new LatheGeometry(outerP, 64, Math.PI * .5, Math.PI * 1.5), M.steel, M, 40); root.add(outer);
  const innerP = [new Vector2(Ri - .5, -w * rows / 2), new Vector2(Ri, -w * rows / 2)];
  gys.slice().reverse().forEach(gy => { for(let k = 0; k <= 10; k++){ const a = -Math.PI / 2 + Math.PI * k / 10; innerP.push(new Vector2(Ri - Math.cos(a) * br * .3, gy + Math.sin(a) * br * 1.05)); } });
  innerP.push(new Vector2(Ri, w * rows / 2)); innerP.push(new Vector2(Ri - .5, w * rows / 2)); innerP.push(innerP[0].clone());
  const inner = new Group(); root.add(inner);
  inner.add(part(new LatheGeometry(innerP, 64), M.accent, M, 40));
  const mark = new Mesh(new BoxGeometry(.06, .02, .3), M.iron); mark.position.set(0, w * rows / 2 + .01, -(Ri - .25)); inner.add(mark);
  const cage = new Group(); root.add(cage);
  const balls = [];
  gys.forEach(gy => {
    const c = new Mesh(new TorusGeometry(pr, .04, 6, 72), M.iron); c.rotation.x = Math.PI / 2; c.position.y = gy + br * .75; cage.add(c);
    for(let i = 0; i < nb; i++){ const a = TAU * i / nb; const b = new Mesh(new SphereGeometry(br, 20, 14), M.ball); b.position.set(pr * Math.cos(a), gy, pr * Math.sin(a)); cage.add(b); balls.push(b);
      const strip = new Mesh(new BoxGeometry(.05, .05, .25), M.steel2); strip.position.set(0, br * .82, 0); b.add(strip); }
  });
  return {
    root,
    labels: [
      { text: "外輪（ハウジングに固定）", at: () => new Vector3(-(Ro + .3), w * rows / 2 + .1, 0) },
      { text: "内輪（軸と一緒に回る）", at: () => new Vector3(0, w * rows / 2 + .15, Ri - .2) },
      { text: "玉（自転しながら公転）", at: () => new Vector3(pr * .7, gys[0] + br, pr * .7) },
      { text: "保持器（玉の間隔を保つ）", at: () => new Vector3(pr * .1, gys[0] + br * .9, -pr), dim: true }
    ],
    note: "内輪が回ると、玉は自転しながら内輪のおよそ4割の速さで公転する。すべらずに転がるので、摩擦は平軸受の数分の一",
    update(t){
      const th = t * .9; inner.rotation.y = th; cage.rotation.y = th * .4;
      balls.forEach(b => { b.rotation.x = -th * (Ri / br) * .6; });
    }
  };
};

/* ---------- viewer ---------- */
const ISO_AZ = Math.PI / 4, ISO_EL = Math.atan(1 / Math.SQRT2);
export function mount(fig){
  const make = SCENES[fig.getAttribute("data-3d")];
  if(!make) return false;
  let renderer;
  try { renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" }); }
  catch(e){ return false; }
  const stage = fig.querySelector(".m3d-stage") || fig;
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1));
  renderer.outputColorSpace = SRGBColorSpace;
  stage.appendChild(renderer.domElement);
  renderer.domElement.setAttribute("aria-hidden", "true");
  const scene = new Scene();
  let P = palette(); const M = mats(P);
  const hemi = new HemisphereLight(0xffffff, 0x8a8070, 1.25); scene.add(hemi);
  const sun = new DirectionalLight(0xffffff, 1.6); sun.position.set(-4, 9, 6); scene.add(sun);
  const fill = new DirectionalLight(0xffffff, .5); fill.position.set(6, 3, -4); scene.add(fill);
  const opts = {}; for(const a of fig.attributes) if(a.name.startsWith("data-") && a.name !== "data-3d") opts[a.name.slice(5)] = a.value;
  let S = make(M, P, opts); scene.add(S.root);
  /* camera: orthographic at the drawings' isometric angle, framed to the model */
  const cam = new OrthographicCamera(-1, 1, 1, -1, -100, 100);
  /* frame the model: the largest extent it shows while turning round at the default elevation */
  const box = new Box3();
  S.root.updateMatrixWorld(true);
  S.root.traverse(o => { if(o.isMesh && !o.userData.noFit){ o.geometry.computeBoundingBox(); box.union(o.geometry.boundingBox.clone().applyMatrix4(o.matrixWorld)); } });
  const center = box.getCenter(new Vector3());
  let az = ISO_AZ + (+opts.az || 0), el = ISO_EL;
  function place(){
    cam.position.set(center.x + Math.sin(az) * Math.cos(el) * 20, center.y + Math.sin(el) * 20, center.z + Math.cos(az) * Math.cos(el) * 20);
    cam.lookAt(center); cam.updateMatrixWorld();
  }
  const corners = [];
  for(const x of [box.min.x, box.max.x]) for(const y of [box.min.y, box.max.y]) for(const z of [box.min.z, box.max.z]) corners.push(new Vector3(x, y, z));
  function extent(a, e){
    const sa = az, se = el; az = a; el = e; place();
    let hw = 0, hh = 0; const p = new Vector3();
    for(const c of corners){ p.copy(c).applyMatrix4(cam.matrixWorldInverse); hw = Math.max(hw, Math.abs(p.x)); hh = Math.max(hh, Math.abs(p.y)); }
    az = sa; el = se; return [hw, hh];
  }
  let HW = 0, HH = 0;
  for(let k = 0; k < 12; k++){ const [w, h] = extent(az + k * Math.PI / 6, el); HW = Math.max(HW, w); HH = Math.max(HH, h); }
  const [w0, h0] = extent(az, el); HW = (HW + w0) / 2; HH = (HH + h0) / 2;  /* mostly the default view, with room to turn */
  function size(){
    const w = stage.clientWidth, h = stage.clientHeight || w * .62;
    renderer.setSize(w, h, false);
    const asp = w / h, m = 1.12;
    let hw = HW * m, hh = HH * m;
    if(hw / hh > asp) hh = hw / asp; else hw = hh * asp;
    cam.left = -hw; cam.right = hw; cam.top = hh; cam.bottom = -hh;
    cam.updateProjectionMatrix(); dirty = true;
  }
  /* labels */
  const layer = document.createElement("div"); layer.className = "m3d-labels"; stage.appendChild(layer);
  const labs = S.labels.map(l => { const e = document.createElement("span"); e.className = "m3d-l" + (l.dim ? " dim" : ""); e.textContent = l.text; layer.appendChild(e); return { l, e }; });
  const cap = fig.querySelector(".m3d-note"); if(cap && S.note && !cap.textContent.trim()) cap.textContent = S.note;
  const v = new Vector3();
  function placeLabels(){
    const w = stage.clientWidth, h = stage.clientHeight;
    for(const { l, e } of labs){
      v.copy(l.at()); if(l.obj) l.obj.localToWorld(v); v.project(cam);
      const x = (v.x * .5 + .5) * w, y = (-v.y * .5 + .5) * h;
      const ow = e.offsetWidth, flip = x + ow > w - 8 && x - ow > 8;
      e.classList.toggle("flip", flip);
      e.style.transform = `translate(${(flip ? x - ow + 12 : x).toFixed(1)}px,${y.toFixed(1)}px)`;
      e.classList.toggle("on", !!(l.key && S.active === l.key));
    }
  }
  /* controls: drag to turn (touch: sideways only, so the page still scrolls) */
  const cv = renderer.domElement; let drag = null;
  cv.style.touchAction = "pan-y";
  cv.addEventListener("pointerdown", e => { drag = { x: e.clientX, y: e.clientY, az, el, touch: e.pointerType !== "mouse" }; cv.setPointerCapture(e.pointerId); fig.classList.add("grab"); });
  cv.addEventListener("pointermove", e => {
    if(!drag) return;
    az = drag.az - (e.clientX - drag.x) * .008;
    if(!drag.touch) el = MathUtils.clamp(drag.el + (e.clientY - drag.y) * .006, .08, 1.35);
    place(); dirty = true; fig.classList.add("turned");
  });
  const end = () => { drag = null; fig.classList.remove("grab"); };
  cv.addEventListener("pointerup", end); cv.addEventListener("pointercancel", end);
  cv.addEventListener("dblclick", () => { az = ISO_AZ + (+opts.az || 0); el = ISO_EL; place(); dirty = true; fig.classList.remove("turned"); });
  /* buttons */
  const ui = fig.querySelector(".m3d-ui");
  let playing = !RM.matches;
  if(ui){
    const pb = document.createElement("button"); pb.type = "button"; pb.className = "m3d-b";
    const setP = () => { pb.textContent = playing ? "一時停止" : "動かす"; pb.setAttribute("aria-pressed", playing ? "false" : "true"); };
    pb.addEventListener("click", () => { playing = !playing; setP(); last = 0; });
    setP(); ui.appendChild(pb);
    (S.toggles || []).forEach(tg => {
      const b = document.createElement("button"); b.type = "button"; b.className = "m3d-b"; b.textContent = tg.label;
      b.setAttribute("aria-pressed", tg.on ? "true" : "false");
      b.addEventListener("click", () => { tg.on = !tg.on; b.setAttribute("aria-pressed", tg.on ? "true" : "false"); tg.set(tg.on); dirty = true; });
      ui.appendChild(b);
    });
    const rs = document.createElement("button"); rs.type = "button"; rs.className = "m3d-b ghost"; rs.textContent = "向きを戻す";
    rs.addEventListener("click", () => { az = ISO_AZ + (+opts.az || 0); el = ISO_EL; place(); dirty = true; fig.classList.remove("turned"); });
    ui.appendChild(rs);
  }
  /* run only while on screen */
  let seen = false, t = 2.2, last = 0, dirty = true, raf = 0;
  function frame(ts){
    raf = 0;
    if(!seen) return;
    if(playing){ const dt = last ? Math.min(.05, (ts - last) / 1000) : 0; last = ts; t += dt; S.update.call(S, t, dt); dirty = true; }
    if(dirty){ renderer.render(scene, cam); placeLabels(); dirty = false; }
    raf = requestAnimationFrame(frame);
  }
  new IntersectionObserver(es => { seen = es[0].isIntersecting; last = 0; if(seen && !raf) raf = requestAnimationFrame(frame); }, { threshold: .05 }).observe(fig);
  new ResizeObserver(size).observe(stage);
  /* theme */
  const retheme = () => {
    P = palette(); const N = mats(P);
    for(const k in M){ M[k].color.copy(N[k].color); if("opacity" in N[k]) M[k].opacity = N[k].opacity; }
    dirty = true;
  };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", retheme);
  new MutationObserver(retheme).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  S.update.call(S, t, 0); place(); size();
  fig.classList.add("ready");
  return true;
}
