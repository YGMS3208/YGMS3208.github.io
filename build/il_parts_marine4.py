"""Part drawings for the marine sections: 4-stroke medium-speed engine (marine4) and the large
turbocharger / fuel injection / exhaust after-treatment group (marineaux).
Same studio-lit metal style as il_parts.py: viewBox 0 0 320 200, theme classes only, no text.

Material notes
- The page puts the part's material class (mt-fe / mt-al / ...) on the <svg>; w/w2/w3 and the shaded
  solids (ws1..4) follow it. Where one drawing mixes materials:
  cast iron inside a steel drawing -> fe() group; steel inside a cast-iron drawing -> the "m" tones;
  aluminium -> "alu"; copper alloy -> "cu"; nickel alloy -> warm "gw" tones; painted casings -> "pt".
"""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il_mt import Scene


# =====================================================================================
# helpers
# =====================================================================================
def fe(s):
    """cast-iron colouring for pieces inside a drawing whose root material is steel."""
    return '<g class="ilu mt-fe">%s</g>' % s


def alg(s):
    """aluminium colouring for 2D w/w2/w3 shapes regardless of the root material class."""
    return '<g class="ilu mt-al">%s</g>' % s


def cug(s):
    return '<g class="ilu mt-cu">%s</g>' % s


def faint(s, op=0.4):
    return '<g opacity="%s">%s</g>' % (op, s)


def P(pts_, close=True):
    d = "M" + " L".join(n(x) + " " + n(y) for x, y in pts_)
    return d + ("Z" if close else "")


def pg(pts_, c="w"):
    return path(P(pts_), c)


def arcpts(cx, cy, rx, ry, a0, a1, seg=24):
    """points on an ellipse arc, angles in degrees (screen: +y down, cw positive)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / seg)))
            for k in range(seg + 1)]


def hatch(polys, step=3.6, ang=45, cls="hatch"):
    """section hatching clipped to polygon(s) (even-odd); polys = list of (x,y) or list of such lists."""
    if not polys:
        return ""
    if isinstance(polys[0][0], (int, float)):
        polys = [polys]
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    edges, vs = [], []
    for pl in polys:
        R = [(x * ca + y * sa, -x * sa + y * ca) for x, y in pl]
        for i in range(len(R)):
            edges.append((R[i], R[(i + 1) % len(R)]))
            vs.append(R[i][1])
    v = math.floor(min(vs) / step) * step + step * 0.5
    d = ""
    while v < max(vs):
        xs = []
        for (u1, w1), (u2, w2) in edges:
            if (w1 <= v < w2) or (w2 <= v < w1):
                xs.append(u1 + (v - w1) / (w2 - w1) * (u2 - u1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            ua, ub = xs[k], xs[k + 1]
            d += "M%s %sL%s %s" % (n(ua * ca - v * sa), n(ua * sa + v * ca), n(ub * ca - v * sa), n(ub * sa + v * ca))
        v += step
    return path(d, cls) if d else ""


def section(polys, c="w", step=3.6, ang=45):
    """filled section face (material class c) with hatching on top."""
    if not polys or not polys[0]:
        return ""
    if isinstance(polys[0][0], (int, float)):
        polys = [polys]
    d = "".join(P(p) for p in polys)
    return '<path class="%s" fill-rule="evenodd" d="%s"/>' % (c, d) + hatch(polys, step, ang)


def clip_convex(subj, clip):
    """Sutherland-Hodgman: clip polygon subj by convex polygon clip (any winding)."""
    def side(a, b, p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    ar = sum(clip[i][0] * clip[(i + 1) % len(clip)][1] - clip[(i + 1) % len(clip)][0] * clip[i][1] for i in range(len(clip)))
    sg = 1 if ar > 0 else -1
    out = list(subj)
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        if not inp:
            break
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(a, b, p) * sg, side(a, b, q) * sg
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def clip_line(a, b, poly):
    """Cyrus-Beck: clip segment a-b to convex polygon; returns (p, q) or None."""
    ar = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    sg = 1 if ar > 0 else -1
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        nx, ny = -(q[1] - p[1]) * sg, (q[0] - p[0]) * sg          # inward normal
        num = nx * (a[0] - p[0]) + ny * (a[1] - p[1])
        den = nx * dx + ny * dy
        if abs(den) < 1e-12:
            if num < 0:
                return None
            continue
        t = -num / den
        if den > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return None
    return (a[0] + dx * t0, a[1] + dy * t0), (a[0] + dx * t1, a[1] + dy * t1)


def lines_in(segs, poly, cls="gr"):
    d = ""
    for a, b in segs:
        r = clip_line(a, b, poly)
        if r:
            d += "M%s %sL%s %s" % (n(r[0][0]), n(r[0][1]), n(r[1][0]), n(r[1][1]))
    return path(d, cls) if d else ""


def person(x, y, h=26, c="m3"):
    """standing human silhouette, feet centre at (x, y), height h px (1.7 m)."""
    k = h / 26.0

    def q(px, py):
        return (x + px * k, y - py * k)
    body = [q(-2.2, 0), q(-1.2, 11.5), q(-0.4, 11.5), q(0.4, 11.5), q(1.2, 11.5), q(2.2, 0), q(3.4, 0), q(2.8, 12.5),
            q(3.6, 19.6), q(4.6, 12.6), q(5.6, 12.8), q(4.6, 20.4), q(3.0, 21.6), q(-3.0, 21.6), q(-4.6, 20.4), q(-5.6, 12.8),
            q(-4.6, 12.6), q(-3.6, 19.6), q(-2.8, 12.5), q(-3.4, 0)]
    hx, hy = q(0, 23.9)
    s = path(P(body), c) + circ(hx, hy, 2.2 * k, c)
    return s + path(P(body), "o thin") + circ(hx, hy, 2.2 * k, "o thin")


def fit_scene(fn, az, el, area=(16, 14, 304, 172), sh=True, sh_ry=None, post=None, pre=None):
    """run fn(scene) twice: probe extents with a unit camera, then fit into area (x0,y0,x1,y1).
    post(scene) may return extra svg drawn on top (overlays that need the final camera)."""
    pr = Scene(0, 0, az, el, 1.0)
    pr.k = 1.0
    fn(pr)
    x0, y0, x1, y1 = pr.extent()
    L, T, R, B = area
    k = min((R - L) / (x1 - x0), (B - T) / (y1 - y0))
    ox = L + ((R - L) - (x1 - x0) * k) / 2 - x0 * k
    oy = T + ((B - T) - (y1 - y0) * k) / 2 - y0 * k
    sc = Scene(ox, oy, az, el, k)
    sc.k = k
    fn(sc)
    body, _ = sc.render(shadow_=False)
    out = ""
    if sh:
        ex = sc.extent()
        out += shadow((ex[0] + ex[2]) / 2, ex[3] - 2, (ex[2] - ex[0]) * 0.5, sh_ry or 9)
    if pre:
        out += pre(sc)
    out += body
    if post:
        out += post(sc)
    return out


def X(sc, x0, L, yz, mat="w", bias=0.0, **kw):
    """outline in (y,z) [optionally with fid as 3rd item] extruded along +x from x0."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(yz)]
    ys, zs = [p[0] for p in yz], [p[1] for p in yz]
    sc.add(GE.prism(sc.cam, (x0, 0, 0), (1, 0, 0), loop, L, mat, **kw),
           ((min(x0, x0 + L), min(ys), min(zs)), (max(x0, x0 + L), max(ys), max(zs))), bias)


def Y(sc, y0, L, xz, mat="w", bias=0.0, **kw):
    """outline in (x,z) extruded from y0 toward the viewer (-y) by L."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(GE.prism(sc.cam, (0, y0, 0), (0, -1, 0), loop, L, mat, **kw), ((min(xs), y0 - L, min(zs)), (max(xs), y0, max(zs))), bias)


def Z(sc, z0, L, xy, mat="w", bias=0.0, **kw):
    """outline in (x,y) extruded along +z from z0."""
    loop = [(-p[1], p[0], p[2] if len(p) > 2 else i) for i, p in enumerate(xy)]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    sc.add(GE.prism(sc.cam, (0, 0, z0), (0, 0, 1), loop, L, mat, **kw), ((min(xs), min(ys), z0), (max(xs), max(ys), z0 + L)), bias)


def BOX(sc, x, y, z, sx, sy, sz, mat="w", bias=0.0, **kw):
    Z(sc, z, sz, [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)], mat, bias, **kw)


def CYL(sc, O, A, r, h, mat="w", bias=0.0, **kw):
    kw.setdefault("seg", 28)
    a = GE._norm(A)
    p1 = tuple(O[i] + a[i] * h for i in range(3))
    lo = tuple(min(O[i], p1[i]) - (r if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (r if abs(a[i]) < .99 else 0) for i in range(3))
    sc.add(GE.cyl(sc.cam, O, a, r, h, mat, **kw), (lo, hi), bias)


def RING(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=32):
    a = GE._norm(A)
    p1 = tuple(O[i] + a[i] * h for i in range(3))
    lo = tuple(min(O[i], p1[i]) - (ro if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (ro if abs(a[i]) < .99 else 0) for i in range(3))
    sc.add(GE.prism(sc.cam, O, a, GE.circle_outline(ro, seg, 12), h, mat, holes=[GE.circle_outline(ri, 24, 8)], smooth=True), (lo, hi), bias)


def RAW(sc, fn, bb, bias=0.0):
    sc.add(fn, bb, bias)


def circ3(cam, C, A, r, seg=28, a0=0.0, a1=360.0):
    """screen points of a circle (centre C, normal A, radius r) in 3D; optional arc a0..a1 (deg)."""
    E1, E2, _ = GE.frame(A)
    full = abs(a1 - a0) >= 359.9
    cnt = seg if full else seg + 1
    out = []
    for k in range(cnt):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        out.append(cam.xy(tuple(C[i] + r * (math.cos(t) * E1[i] + math.sin(t) * E2[i]) for i in range(3))))
    return out


def hole3(cam, C, A, r, c="bg", seg=None):
    seg = seg or max(10, min(28, int(r * 3)))
    return pg(circ3(cam, C, A, r, seg), c)


def quad3(cam, ps, c="w"):
    return pg([cam.xy(p) for p in ps], c)


def smooth_d(ps, close=False):
    """Catmull-Rom spline through screen points -> cubic bezier path data."""
    if len(ps) < 3:
        return P(ps, close)
    pts_ = list(ps)
    if close:
        pts_ = [ps[-1]] + list(ps) + [ps[0], ps[1]]
    else:
        pts_ = [ps[0]] + list(ps) + [ps[-1]]
    d = "M%s %s" % (n(pts_[1][0]), n(pts_[1][1]))
    for i in range(1, len(pts_) - 2):
        p0, p1, p2, p3 = pts_[i - 1], pts_[i], pts_[i + 1], pts_[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += " C%s %s %s %s %s %s" % (n(c1[0]), n(c1[1]), n(c2[0]), n(c2[1]), n(p2[0]), n(p2[1]))
    return d + ("Z" if close else "")


FLOW = {  # kind: (line class, extra style, head class)
    "air": ("fo", "stroke-width:2", "fdot"),
    "water": ("fo", "stroke-width:1.6;stroke-dasharray:4 2.5", "fdot"),
    "gas": ("clampl", "stroke-width:2.2", "clamph"),
    "grey": ("done", "stroke-width:2", "d"),
    "fuel": ("fence", "stroke-width:2", "bolt"),
    "oil": ("chipc", "stroke-width:1.8", "t"),
    "a": ("a", "", "af"),
}


def flow(ps, kind="air", hs=6.5, smooth=True, w=None):
    """coloured flow arrow along screen points ps (head at the last point)."""
    lc, st, hc = FLOW[kind]
    if w:
        st = "stroke-width:%s" % n(w) + (";" + st.split(";", 1)[1] if ";" in st else "")
    x1, y1 = ps[-2]
    x2, y2 = ps[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    q = list(ps[:-1]) + [(x2 - hs * 0.55 * math.cos(ang), y2 - hs * 0.55 * math.sin(ang))]
    d = smooth_d(q) if smooth and len(q) > 2 else P(q, False)
    s = '<path class="%s" style="fill:none;%s" d="%s"/>' % (lc, st, d)
    return s + head(x2, y2, ang, hs).replace('class="af"', 'class="%s"' % hc)


def lens(cx, cy, r, tx=None, ty=None):
    """magnifier frame: theme-aware disc + rim; optional leader line to (tx, ty)."""
    s = ""
    if tx is not None:
        a = math.atan2(ty - cy, tx - cx)
        s += line(cx + r * math.cos(a), cy + r * math.sin(a), tx, ty, "o thin dash")
        s += circ(tx, ty, 2.2, "o")
    return s + circ(cx, cy, r, "void") + circ(cx, cy, r, "o")


def lens_rim(cx, cy, r):
    return circ(cx, cy, r, "o") + circ(cx, cy, r + 1.6, "o thin")


def panel(x, y, w, h, r=6):
    return rect(x, y, w, h, "void", r) + rect(x, y, w, h, "o", r)


def bolt_hex(cx, cy, r, c="w2"):
    ps = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * 0.9 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    return pg(ps, c)


# =====================================================================================
# marine4: 4-stroke medium-speed engine
# =====================================================================================
M4_CYL = [40 + 64 * i for i in range(6)]          # cylinder centres along the block (x)
M4_BRG = [8 + 64 * i for i in range(7)]           # main bearing bulkheads


def cyl_strips(cam, C, r, z0, z1, a0=180, a1=360, seg=12, mat="w"):
    """shaded strips of a vertical cylinder surface (front part a0..a1 deg in the x-y plane)."""
    out = []
    for k in range(seg):
        t0 = math.radians(a0 + (a1 - a0) * k / seg)
        t1 = math.radians(a0 + (a1 - a0) * (k + 1) / seg)
        tm = (t0 + t1) / 2
        nrm = (math.cos(tm), math.sin(tm), 0.0)
        cls = mat + "s%d" % GE.shade(nrm)
        ps = [cam.xy((C[0] + r * math.cos(t0), C[1] + r * math.sin(t0), z0)), cam.xy((C[0] + r * math.cos(t1), C[1] + r * math.sin(t1), z0)),
              cam.xy((C[0] + r * math.cos(t1), C[1] + r * math.sin(t1), z1)), cam.xy((C[0] + r * math.cos(t0), C[1] + r * math.sin(t0), z1))]
        out.append((ps, cls))
    return out


# =====================================================================================
# marine4: 4-stroke medium-speed engine
# =====================================================================================
M4_CYL = [40 + 64 * i for i in range(6)]          # cylinder centres along the block (x)
M4_BRG = [8 + 64 * i for i in range(7)]           # main bearing bulkheads


def m4_block_section(cx, cy, s):
    """transverse schematic section: bore + water jacket above, underslung cap + studs below."""
    def T(ps):
        return [(cx + (y - 43) * s, cy - (z - 60) * s) for y, z in ps]
    sad = [(50 + 20 * math.cos(math.radians(k * 15)), 38 + 20 * math.sin(math.radians(k * 15))) for k in range(13)]
    outer = [(0, 0), (0, 56), (-14, 56), (-14, 86), (0, 86), (0, 120), (19, 120), (19, 113), (23, 113), (23, 64), (77, 64), (77, 113),
             (81, 113), (81, 120), (100, 120), (100, 0), (92, 0), (92, 38)] + sad + [(8, 38), (8, 0)]
    jl = [(6, 70), (15, 70), (15, 110), (6, 110)]
    jr = [(85, 70), (94, 70), (94, 110), (85, 110)]
    camb = [(-5 + 6 * math.cos(math.radians(k * 30)), 71 + 6 * math.sin(math.radians(k * 30))) for k in range(12)]
    gal = [(4 + 2.4 * math.cos(math.radians(k * 45)), 48 + 2.4 * math.sin(math.radians(k * 45))) for k in range(8)]
    o = section([T(outer), T(jl), T(jr), T(camb), T(gal)], "w", 2.6, 45)
    o += pg(T(jl), "fl") + pg(T(jr), "fl") + pg(T(camb), "bg") + pg(T(gal), "bg")
    capb = [(50 - 20 * math.cos(math.radians(k * 15)), 38 - 20 * math.sin(math.radians(k * 15))) for k in range(13)]
    cap = [(8, 38), (30, 38)] + capb[1:-1] + [(70, 38), (92, 38), (92, 20), (86, 11), (14, 11), (8, 20)]
    o += section([T(cap)], "w2", 2.6, -45)
    jr_ = [(50 + 17 * math.cos(math.radians(k * 20)), 38 + 17 * math.sin(math.radians(k * 20))) for k in range(18)]
    o += pg(T(jr_), "m")                                                    # journal
    for yy in (22, 78):                                                     # vertical studs + nuts below
        o += pg(T([(yy - 2, 4), (yy + 2, 4), (yy + 2, 50), (yy - 2, 50)]), "m")
        o += pg(T([(yy - 5, 4), (yy + 5, 4), (yy + 5, 10.5), (yy - 5, 10.5)]), "m2")
    for y0, y1, yn in ((-5, 18, -5), (82, 105, 100)):                       # horizontal side studs
        o += pg(T([(y0, 22), (y1, 22), (y1, 26), (y0, 26)]), "m")
        o += pg(T([(yn, 19), (yn + 5, 19), (yn + 5, 29), (yn, 29)]), "m2")
    return o


@part("marine4.m4block")
def _():
    Lb, Wb, Hb, zc = 400, 100, 120, 38            # length, width, height, crank centre height

    def cap_yz():
        a = [(50 + 20 * math.cos(math.radians(180 - 180 * k / 12)), zc - 20 * math.sin(math.radians(180 * k / 12))) for k in range(13)]
        return [(8, zc), (30, zc)] + a[1:-1] + [(70, zc), (92, zc), (92, 22), (86, 10), (14, 10), (8, 22)]

    def bulk_yz():
        a = [(50 + 20 * math.cos(math.radians(180 - 180 * k / 12)), zc + 20 * math.sin(math.radians(180 * k / 12))) for k in range(13)]
        return [(8, zc), (30, zc)] + a[1:-1] + [(70, zc), (92, zc), (92, 56), (8, 56)]

    def build(sc):
        BOX(sc, 0, 92, 0, Lb, 8, 56, "w", dark=2)                         # far skirt (inner face seen)
        BOX(sc, 0, 0, 56, Lb, Wb, Hb - 56, "w", lines=False)   # cylinder section, machined deck
        for xb in M4_BRG:
            X(sc, xb - 6, 12, bulk_yz(), "w", dark=1)                       # bulkhead with saddle
            X(sc, xb - 7, 14, cap_yz(), "w")                                # underslung main bearing cap
            for yy in (22, 78):                                             # vertical studs, nut under the cap
                CYL(sc, (xb, yy, 3.5), (0, 0, 1), 5.4, 6.5, "m", seg=6)
                CYL(sc, (xb, yy, -1.5), (0, 0, 1), 2.7, 5, "m", seg=8)
            CYL(sc, (xb, 0, 24), (0, 1, 0), 2.6, 8, "m", seg=8)            # horizontal side stud
        BOX(sc, 0, 0, 46, Lb, 8, 10, "w", dark=1)                           # top band of the near skirt
        BOX(sc, 0, -14, 56, Lb, 14, 30, "w")                                # cam housing
        for xc in M4_CYL:
            BOX(sc, xc - 11, -13, 86, 22, 12, 3, "m", bias=-0.1)            # fuel pump seats
        Y(sc, 100, 114, [(-5, 6), (-5, 92), (0, 92), (0, 6)], "w", lines=False)
        X(sc, -5, 5, [(-12, 0), (100, 0), (100, 70), (80, 90), (-12, 90)], "m", cap_mat="m2")   # gear-case mounting face
        for xc in M4_CYL:
            for dx, dy in ((-22, 14), (22, 14), (-22, 86), (22, 86)):
                CYL(sc, (xc + dx, dy, Hb), (0, 0, 1), 3.6, 11, "m", seg=10)
        RAW(sc, lambda s_: person(*s_.P((428, -26, 0)), h=136 * s_.k * s_.cam.ce), ((418, -32, 0), (438, -20, 136)))

    def post(sc):
        cam = sc.cam
        o = ""
        # near skirt as phantom: outline only, side-bolt nuts on its face
        ps = [cam.xy(p) for p in ((0, 0, 0), (Lb, 0, 0), (Lb, 0, 46), (0, 0, 46))]
        o += pg(ps, "o thin dash")
        o += P([cam.xy((Lb, 0, 0)), cam.xy((Lb, 8, 0))], False) and path(P([cam.xy((Lb, 0, 0)), cam.xy((Lb, 0, 0))], False), "o thin")
        for xb in M4_BRG[1:]:
            c = cam.xy((xb, 0, 24))
            o += bolt_hex(c[0], c[1], 5.2 * sc.k, "m2")
        # stepped cylinder bores on the deck
        for xc in M4_CYL:
            o += hole3(cam, (xc, 50, Hb), (0, 0, 1), 31, "m2")
            o += pg(circ3(cam, (xc, 50, Hb), (0, 0, 1), 26.5, 24), "bg")
            wall = circ3(cam, (xc, 50, Hb - 3), (0, 0, 1), 26.5, 14, 180, 360) + circ3(cam, (xc, 50, Hb - 16), (0, 0, 1), 26.5, 14, 360, 180)
            o += pg(wall, "w3")
            ring = circ3(cam, (xc, 50, Hb), (0, 0, 1), 31, 14, 180, 360) + circ3(cam, (xc, 50, Hb - 3), (0, 0, 1), 31, 14, 360, 180)
            o += pg(ring, "w2")
            o += pg(circ3(cam, (xc, 50, Hb - 3), (0, 0, 1), 31, 24), "o thin")
            o += hole3(cam, (xc + 32, 50, Hb), (0, 0, 1), 2.4, "bg")
        # cam housing: inspection openings, cam bearing bores, pump seat holes
        for xc in M4_CYL:
            o += pg([cam.xy((xc - 17, -14, 62)), cam.xy((xc + 17, -14, 62)), cam.xy((xc + 17, -14, 80)), cam.xy((xc - 17, -14, 80))], "bg")
            o += hole3(cam, (xc, -6.5, 89), (0, 0, 1), 4.2, "bg")
            for dx, dy in ((-7, -11), (7, -11), (-7, -2), (7, -2)):
                o += hole3(cam, (xc + dx, dy, 89), (0, 0, 1), 1.1, "bg")
        for xb in M4_BRG[1:-1]:
            o += hole3(cam, (xb, -14, 71), (0, 1, 0), 6.5, "m2") + hole3(cam, (xb, -14, 71), (0, 1, 0), 4, "bg")
        # front face openings and bolt holes
        o += hole3(cam, (-5, 46, zc), (1, 0, 0), 15, "bg") + hole3(cam, (-5, 2, 71), (1, 0, 0), 9, "bg")
        o += hole3(cam, (-5, 78, 66), (1, 0, 0), 7, "m2") + hole3(cam, (-5, 78, 66), (1, 0, 0), 3.5, "bg")
        for k in range(9):
            o += hole3(cam, (-5, -7 + k * 13, 5), (1, 0, 0), 1.4, "bg")
        for k in range(6):
            o += hole3(cam, (-5, -7, 18 + k * 13), (1, 0, 0), 1.4, "bg")
        # main oil gallery (hidden line along the block)
        a, b = cam.xy((0, 4, 51)), cam.xy((Lb, 4, 51))
        o += line(a[0], a[1], b[0], b[1], "hid")
        # cut-out at cylinder 1: water jacket around the bore barrel
        win = [cam.xy(p) for p in ((8, 0, 89), (72, 0, 89), (72, 0, 117), (8, 0, 117))]
        o += pg(win, "bg") + pg(win, "coolin")
        for ps, cls in cyl_strips(cam, (M4_CYL[0], 50, 0), 25, 60, 130, 180, 360, 14):
            q = clip_convex(ps, win)
            if len(q) > 2:
                o += pg(q, cls)
        for t in (180, 360):
            a = cam.xy((M4_CYL[0] + 25 * math.cos(math.radians(t)), 50 + 25 * math.sin(math.radians(t)), 60))
            b = cam.xy((M4_CYL[0] + 25 * math.cos(math.radians(t)), 50 + 25 * math.sin(math.radians(t)), 130))
            q = clip_convex([a, b, (b[0] + 0.01, b[1]), (a[0] + 0.01, a[1])], win)
            if len(q) > 2:
                o += line(q[0][0], q[0][1], q[-1][0], q[-1][1], "o thin")
        o += pg([cam.xy(p) for p in ((8, 0, 89), (72, 0, 89), (72, 10, 89), (8, 10, 89))], "cut")
        o += pg([cam.xy(p) for p in ((72, 0, 89), (72, 10, 89), (72, 10, 117), (72, 0, 117))], "cut")
        o += pg(win, "o")
        c = cam.xy((-5, 50, 80))
        o += lens(44, 44, 31, c[0], c[1]) + m4_block_section(44, 44, 0.335) + lens_rim(44, 44, 31)
        return o

    return fit_scene(build, 30, 26, area=(14, 34, 308, 184), sh_ry=10, post=post)


def hull2(c1, r1, c2, r2, seg=20):
    """convex hull outline of two circles in a plane (u,v): list of (u,v)."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    d = math.hypot(dx, dy) or 1e-6
    base = math.atan2(dy, dx)
    a = math.acos(max(-1.0, min(1.0, (r1 - r2) / d)))
    out = []
    for k in range(seg + 1):                       # big arc around circle 1 (away from circle 2)
        t = base + a + (2 * math.pi - 2 * a) * k / seg
        out.append((c1[0] + r1 * math.cos(t), c1[1] + r1 * math.sin(t)))
    for k in range(seg + 1):                       # arc around circle 2
        t = base - a + 2 * a * k / seg
        out.append((c2[0] + r2 * math.cos(t), c2[1] + r2 * math.sin(t)))
    return out


def grain_panel(x, y, w, h):
    """magnified longitudinal section of one crank throw with continuous grain-flow lines."""
    s = min(w / 64.0, h / 62.0)
    ox, oy = x + w / 2 - 28 * s, y + h / 2 + 11 * s

    def T(p):
        return (ox + p[0] * s, oy - p[1] * s)
    o = panel(x, y, w, h, 5)
    shape = [(0, -10), (13, -10), (14, -16), (22, -16), (22, 13), (23, 14), (33, 14), (34, 13), (34, -16), (42, -16), (43, -10), (56, -10),
             (56, 10), (43, 10), (42, 38), (34, 38), (34, 34), (22, 34), (22, 38), (14, 38), (13, 10), (0, 10)]
    o += pg([T(p) for p in shape], "w2")
    for f in (-0.78, -0.47, -0.16, 0.16, 0.47, 0.78):
        ps = [(1, 9 * f), (11, 9 * f), (18 - 3.4 * f, 6), (18 - 3.4 * f, 20), (25, 24 + 8.6 * f), (31, 24 + 8.6 * f),
              (38 + 3.4 * f, 20), (38 + 3.4 * f, 6), (45, 9 * f), (55, 9 * f)]
        o += path(smooth_d([T(p) for p in ps]), "o thin")
    o += pg([T(p) for p in shape], "o")
    return o


@part("marine4.m4crank")
def _():
    rj, rp, T, Lj, Lw, Lp = 20, 19, 28, 20, 16, 18
    phis = [90, -30, 210, 210, -30, 90]
    cw_on = (0, 2, 3, 5)

    def pin_c(phi):
        return (T * math.cos(math.radians(phi)), T * math.sin(math.radians(phi)))

    def fillet(sc, x, r, toward):            # small flare where a journal/pin meets a web
        if toward > 0:
            CYL(sc, (x, 0, 0), (1, 0, 0), r, 4, "w", seg=24, scale=lambda t: (r + 4 * t) / r)
        else:
            CYL(sc, (x, 0, 0), (1, 0, 0), r + 4, 4, "w", seg=24, scale=lambda t: (r + 4 - 4 * t) / (r + 4))

    def build(sc):
        # free end: damper and gear seats
        CYL(sc, (-44, 0, 0), (1, 0, 0), 12, 16, "w", seg=24)
        CYL(sc, (-28, 0, 0), (1, 0, 0), 15.5, 20, "w", seg=24)
        CYL(sc, (-8, 0, 0), (1, 0, 0), 17.5, 8, "w", seg=24)
        x = 0
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, Lj, "m", seg=30)
        x += Lj
        for i, phi in enumerate(phis):
            pc = pin_c(phi)
            web = [(u, v, k // 4) for k, (u, v) in enumerate(hull2((0, 0), 27, pc, 24, 14))]
            for xw in (x, x + Lw + Lp):
                X(sc, xw, Lw, web, "w", dark=1, smooth=True)
                if i in cw_on:
                    a0 = phi + 180
                    sec = []
                    for k in range(9):
                        t = math.radians(a0 - 52 + 104 * k / 8)
                        sec.append((46 * math.cos(t), 46 * math.sin(t)))
                    for k in range(7):
                        t = math.radians(a0 + 40 - 80 * k / 6)
                        sec.append((22 * math.cos(t), 22 * math.sin(t)))
                    X(sc, xw + 1, Lw - 2, [(u, v, k) for k, (u, v) in enumerate(sec)], "w", bias=-0.2)
            fillet(sc, x - 4, rj, 1)
            CYL(sc, (x + Lw, pc[0], pc[1]), (1, 0, 0), rp, Lp, "m", seg=30)
            x += 2 * Lw + Lp
            CYL(sc, (x, 0, 0), (1, 0, 0), rj, Lj, "m", seg=30)
            x += Lj
        CYL(sc, (x, 0, 0), (1, 0, 0), rj + 2, 4, "w", seg=30)
        CYL(sc, (x + 4, 0, 0), (1, 0, 0), 38, 12, "w", seg=36)          # flywheel flange
        CYL(sc, (x + 16, 0, 0), (1, 0, 0), 13, 4, "w", seg=24)          # pilot spigot

    def post(sc):
        cam = sc.cam
        o = ""
        x = Lj
        for i, phi in enumerate(phis):
            pc = pin_c(phi)
            if i in cw_on:                                          # counterweight bolts (on the +x face)
                a0 = math.radians(phi + 180)
                for da in (-0.42, 0.42):
                    for xw in (x + Lw - 1, x + 2 * Lw + Lp - 1):
                        c = (xw, 36 * math.cos(a0 + da), 36 * math.sin(a0 + da))
                        o += hole3(cam, c, (1, 0, 0), 2.6, "m2") + hole3(cam, c, (1, 0, 0), 1.2, "bg")
            if i in (0, 3):                                         # oil hole journal -> web -> pin
                a = cam.xy((x - Lj / 2, 0, 0))
                b = cam.xy((x + Lw + Lp / 2, pc[0], pc[1]))
                o += line(a[0], a[1], b[0], b[1], "hid")
            x += 2 * Lw + Lp + Lj
        xe = x + 4 + 12
        for k in range(8):
            t = math.radians(22.5 + 45 * k)
            o += hole3(cam, (xe, 28 * math.cos(t), 28 * math.sin(t)), (1, 0, 0), 2.6, "bg")
        a, b = cam.xy((-26, -2, 15.5)), cam.xy((-12, -2, 15.5))      # keyway on the gear seat
        o += line(a[0], a[1], b[0], b[1], "o") + line(a[0], a[1] + 1.6, b[0], b[1] + 1.6, "o thin")
        # pin arrangement (end view): 1-6 / 2-5 / 3-4 at 120 deg
        cx, cy, R = 276, 158, 26
        o += lens(cx, cy, R)
        o += circ(cx, cy, 6.5, "m")
        for k, ang in enumerate((-90, 30, 150)):
            t = math.radians(ang)
            px, py = cx + 15 * math.cos(t), cy + 15 * math.sin(t)
            o += line(cx, cy, px, py, "o")
            o += circ(px + 1.6, py - 1.2, 5.6, "w2") + circ(px, py, 5.6, "m")
        o += lens_rim(cx, cy, R)
        o += grain_panel(18, 138, 84, 52)
        return o

    return fit_scene(build, -18, 19, area=(10, 10, 310, 130), sh_ry=7, post=post)


def box_sil(cam, x0, y0, z0, sx, sy, sz):
    """screen silhouette (convex hull) of an axis-aligned box."""
    ps = [cam.xy((x, y, z)) for x in (x0, x0 + sx) for y in (y0, y0 + sy) for z in (z0, z0 + sz)]
    ps.sort()
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in ps:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(ps):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def m4_head_face(cx, cy, r):
    """combustion face seen from below: 4 valve seats (2 in / 2 ex) round the central fuel valve."""
    o = lens(cx, cy, r)
    a = r * 0.78
    ch = a * 0.22
    sq = [(cx - a + ch, cy - a), (cx + a - ch, cy - a), (cx + a, cy - a + ch), (cx + a, cy + a - ch), (cx + a - ch, cy + a),
          (cx - a + ch, cy + a), (cx - a, cy + a - ch), (cx - a, cy - a + ch)]
    o += fe(pg(sq, "w"))
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        vx, vy = cx + sx * a * 0.42, cy + sy * a * 0.42
        o += circ(vx, vy, a * 0.37, "m2")                        # seat ring (steel)
        o += circ(vx, vy, a * 0.31, "gw")                        # hard-faced seat band
        o += circ(vx, vy, a * 0.27, "gw" if sx > 0 else "m")     # valve head (exhaust: Ni alloy)
        o += circ(cx + sx * a * 0.82, cy + sy * a * 0.82, a * 0.08, "bg")   # stud holes
    o += circ(cx, cy, a * 0.13, "m2") + circ(cx, cy, a * 0.06, "bg")
    return o + lens_rim(cx, cy, r)


def m4_head_section(x, y, w, h):
    """double-deck section: flame plate, intermediate deck, ports, valve guides, drilled cooling bores."""
    o = panel(x, y, w, h, 5)
    s = min((w - 10) / 104.0, (h - 10) / 84.0)
    ox, oy = x + w / 2, y + h / 2 + 40 * s

    def T(ps):
        return [(ox + u * s, oy - v * s) for u, v in ps]
    body = [(-50, 0), (50, 0), (50, 80), (-50, 80)]
    o += fe(section(T(body), "w", 2.4, 45))
    # water spaces: between flame plate and intermediate deck, and round the fuel valve sleeve above it
    for u0, u1 in ((-45, -33), (-11, -5), (5, 11), (33, 45)):
        o += pg(T([(u0, 15), (u1, 15), (u1, 35), (u0, 35)]), "fl")
    for u0, u1 in ((-12, -5), (5, 12)):
        o += pg(T([(u0, 42), (u1, 42), (u1, 72), (u0, 72)]), "fl")
    # ports: intake (left) and exhaust (right), from the valve throat out to the side wall
    for sg in (-1, 1):
        port = [(sg * 29, 0), (sg * 29, 12), (sg * 31, 28), (sg * 40, 42), (sg * 50, 47), (sg * 50, 63), (sg * 38, 60),
                (sg * 25, 49), (sg * 17, 34), (sg * 14, 12), (sg * 14, 0)]
        o += pg(T(port), "void")
    # drilled cooling bores from the water space toward the flame face behind the seats
    for u0, v0, u1, v1 in ((-38, 17, -32, 4), (-8, 17, -11, 4), (8, 17, 11, 4), (38, 17, 32, 4)):
        a, b = T([(u0, v0), (u1, v1)])
        o += '<path class="fo" style="stroke-width:1.8" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    # fuel valve sleeve (centre)
    o += pg(T([(-4, 0), (4, 0), (4, 80), (-4, 80)]), "m2") + pg(T([(-1.6, 0), (1.6, 0), (1.6, 80), (-1.6, 80)]), "bg")
    # valves, seat rings, guides
    for sg in (-1, 1):
        vc = sg * 21.5
        o += pg(T([(vc - 2, 2), (vc + 2, 2), (vc + 2, 86), (vc - 2, 86)]), "m")                        # stem
        o += cug(pg(T([(vc - 4.5, 44), (vc + 4.5, 44), (vc + 4.5, 72), (vc - 4.5, 72)]), "w"))        # guide
        o += pg(T([(vc - 2, 44), (vc + 2, 44), (vc + 2, 72), (vc - 2, 72)]), "m")
        o += pg(T([(vc - 9, 0), (vc + 9, 0), (vc + 3, 6), (vc + 2, 9), (vc - 2, 9), (vc - 3, 6)]), "gw" if sg > 0 else "m")
        for sd in (-1, 1):
            o += pg(T([(vc + sd * 9.5, 0), (vc + sd * 12.5, 0), (vc + sd * 12.5, 5), (vc + sd * 8, 5)]), "m2")
    a1, a2, a3 = T([(-56, 58), (-34, 52), (-24, 22)])
    o += flow([a1, a2, a3], "air", 5)
    b1, b2, b3 = T([(24, 22), (34, 50), (56, 58)])
    o += flow([b1, b2, b3], "gas", 5)
    return o


@part("marine4.m4head")
def _():
    Wd, Ht, ch = 100, 80, 12

    def build(sc):
        sc.box(-50, -50, 0, Wd, Wd, Ht, "w", ch=ch)
        Y(sc, -50, 5, [(-30, 18), (30, 18), (30, 60), (-30, 60)], "w", cap_mat="m2", bias=-0.1)      # exhaust flange
        X(sc, 50, 4, [(-16, 30), (16, 30), (16, 52), (-16, 52)], "w", cap_mat="m2", bias=-0.1)        # water outlet boss
        CYL(sc, (0, 0, Ht), (0, 0, 1), 10, 5, "w", cap_mat="m2")                                       # fuel valve boss
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            vx, vy = sx * 22, sy * 22
            CYL(sc, (vx, vy, Ht), (0, 0, 1), 8.5, 13, "m", seg=24)                                    # valve spring
            CYL(sc, (vx, vy, Ht + 13), (0, 0, 1), 9.5, 2.5, "m", seg=24, cap_mat="m2")                 # retainer
            CYL(sc, (vx, vy, Ht + 15.5), (0, 0, 1), 2.4, 4, "m", seg=12)                               # stem tip
            CYL(sc, (sx * 37, sy * 37, Ht), (0, 0, 1), 9, 1.2, "w", cap_mat="m2")                      # stud spot face
        RAW(sc, lambda s_: "", ((-156, -50, 0), (-56, 50, Ht)))

    def post(sc):
        cam = sc.cam
        o = ""
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            o += hole3(cam, (sx * 37, sy * 37, Ht + 1.2), (0, 0, 1), 5.4, "bg")
            vx, vy = sx * 22, sy * 22
            for k in range(4):                                  # spring coils (front half)
                z = Ht + 2 + k * 3
                o += path(smooth_d(circ3(cam, (vx, vy, z), (0, 0, 1), 8.6, 10, 200, 340)), "o thin")
        o += hole3(cam, (0, 0, Ht + 5), (0, 0, 1), 4.5, "bg")
        rr = []
        for k in range(4):
            cxp, czp = (14 if k in (0, 3) else -14), (47 if k < 2 else 25)
            for j in range(5):
                t = math.radians(90 * k + 22.5 * j)
                rr.append(cam.xy((cxp * (1 if k in (0, 3) else 1) + 7 * math.cos(t), -55, czp + 7 * math.sin(t))))
        o += pg(rr, "bg")
        for u, v in ((-25, 23), (25, 23), (-25, 55), (25, 55)):
            o += hole3(cam, (u, -55, v), (0, 1, 0), 1.6, "bg")
        o += hole3(cam, (54, 0, 41), (1, 0, 0), 6, "bg")
        c = cam.xy((0, -58, 40))
        o += flow([c, (c[0] - 6, c[1] + 10), (c[0] - 16, c[1] + 20)], "gas")
        return o

    def pre(sc):                       # neighbouring head: one head per cylinder
        sil = box_sil(sc.cam, -156, -50, 0, Wd, Wd, Ht)
        return faint(pg(sil, "o dash"), 0.55)

    out = fit_scene(build, -28, 30, area=(10, 18, 214, 186), sh_ry=10, post=post, pre=pre)
    out += m4_head_face(266, 52, 36)
    out += m4_head_section(224, 100, 86, 88)
    return out


def halfplane(cx, cy, nx, ny, big=400):
    """convex polygon for the half-plane (p - c).n >= 0."""
    ux, uy = -ny, nx
    return [(cx + ux * big, cy + uy * big), (cx + ux * big + nx * big, cy + uy * big + ny * big),
            (cx - ux * big + nx * big, cy - uy * big + ny * big), (cx - ux * big, cy - uy * big)]


def box_hull(ps):
    ps = sorted(set((round(x, 3), round(y, 3)) for x, y in ps))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in ps:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(ps):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def rbar(x0, y0, x1, y1, w, c="m"):
    """bar of width w from (x0,y0) to (x1,y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a) * w / 2, math.cos(a) * w / 2
    return pg([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], c)


def zigzag(x0, y0, x1, y1, amp=1.6, pitch=3.0):
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    m = max(2, int(L / pitch))
    ps = []
    for k in range(m + 1):
        t = L * k / m
        a = amp * (1 if k % 2 else -1) if 0 < k < m else 0
        ps.append((x0 + ux * t + nx * a, y0 + uy * t + ny * a))
    return ps


def rod_top(cx, ys, yb, w0, w1):
    """small end + I-section shank down to yb (w0 width at top, w1 at bottom)."""
    o = ""
    sh = [(cx - w0 / 2, ys + 10), (cx + w0 / 2, ys + 10), (cx + w1 / 2, yb), (cx - w1 / 2, yb)]
    o += pg(sh, "w")
    web = [(cx - w0 / 2 + 4, ys + 20), (cx + w0 / 2 - 4, ys + 20), (cx + w1 / 2 - 5, yb - 6), (cx - w1 / 2 + 5, yb - 6)]
    o += pg(web, "w2")
    o += circ(cx, ys, 18, "w")
    o += cug(circ(cx, ys, 12.5, "w")) + circ(cx, ys, 10.5, "bg")         # small-end bush (copper alloy)
    return o


def big_bore(cx, cy):
    return circ(cx, cy, 17.5, "m2") + circ(cx, cy, 15.4, "cu") + circ(cx, cy, 14.2, "bg")


@part("marine4.m4conrod")
def _():
    o = shadow(160, 190, 130, 6)
    # --------------------------------------------------------------- left: oblique split
    cx, ys, cy = 86, 32, 150
    for xx in (cx - 37, cx + 37):                       # liner bore (dashed): the big end passes through it
        o += line(xx, 12, xx, 192, "o thin dash")
    o += flow([(cx - 47, 128), (cx - 47, 60)], "a", 7)
    o += rod_top(cx, ys, cy - 22, 20, 34)
    k = math.sqrt(0.5)
    ux, uy, nx, ny = k, -k, k, k                         # joint direction / joint normal
    pts_ = [(cx + 30 * math.cos(math.radians(a)), cy + 30 * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    for a_, b_ in ((-33, -12), (33, -12), (33, 12), (-33, 12)):
        pts_.append((cx + ux * a_ + nx * b_, cy + uy * a_ + ny * b_))
    pts_ += [(cx - 17, cy - 34), (cx + 17, cy - 34)]
    end = box_hull(pts_)
    rodp = clip_convex(end, halfplane(cx, cy, -nx, -ny))
    capp = clip_convex(end, halfplane(cx, cy, nx, ny))
    o += pg(rodp, "w") + pg(capp, "w2")
    for sg in (-1, 1):                                  # serrated joint faces either side of the bore
        a = (cx + sg * 17.5 * ux, cy + sg * 17.5 * uy)
        b = (cx + sg * 33.5 * ux, cy + sg * 33.5 * uy)
        o += path(P(zigzag(a[0], a[1], b[0], b[1], 1.4, 2.4), False), "o")
    for sg in (-1, 1):                                  # bolts square to the joint face
        bx, by = cx + sg * 24 * ux, cy + sg * 24 * uy
        o += rbar(bx + 8 * nx, by + 8 * ny, bx - 10 * nx, by - 10 * ny, 4.6, "m")
        o += rbar(bx + 7 * nx, by + 7 * ny, bx + 12 * nx, by + 12 * ny, 8, "m2")
    o += big_bore(cx, cy)
    o += line(cx, cy - 16, cx, ys + 12, "hid")
    # --------------------------------------------------------------- right: marine type
    cx2 = 236
    o += rod_top(cx2, ys, 112, 20, 30)
    o += rect(cx2 - 30, 110, 60, 9, "w", 1.5)                           # shank foot flange
    o += rect(cx2 - 28, 119, 56, 2.6, "m2")                             # compression shim
    box_ = [(cx2 - 32, 121.6), (cx2 + 32, 121.6), (cx2 + 32, cy), (cx2 - 32, cy)]
    o += pg(box_, "w")
    lowb = [(cx2 - 32, cy), (cx2 + 32, cy), (cx2 + 32, cy + 22), (cx2 + 24, cy + 31), (cx2 - 24, cy + 31), (cx2 - 32, cy + 22)]
    o += pg(lowb, "w2")
    for sg in (-1, 1):
        o += rect(cx2 + sg * 17 - 2.5, 104, 5, 34, "m") + rect(cx2 + sg * 17 - 5, 103, 10, 7, "m2", 1)   # flange studs + nuts
        o += rect(cx2 + sg * 25 - 2.4, cy - 18, 4.8, 48, "m") + rect(cx2 + sg * 25 - 5, cy + 31, 10, 6, "m2", 1)  # box bolts
    o += line(cx2 - 34, cy, cx2 + 34, cy, "o")
    o += big_bore(cx2, cy)
    o += line(cx2, cy - 16, cx2, ys + 12, "hid")
    # --------------------------------------------------------------- insets
    # I-section of the shank
    ix, iy = 161, 44
    o += lens(ix, iy, 17, cx + 4, 78)
    o += section([(ix - 9, iy - 11), (ix + 9, iy - 11), (ix + 9, iy - 7), (ix + 2.5, iy - 7), (ix + 2.5, iy + 7), (ix + 9, iy + 7),
                  (ix + 9, iy + 11), (ix - 9, iy + 11), (ix - 9, iy + 7), (ix - 2.5, iy + 7), (ix - 2.5, iy - 7), (ix - 9, iy - 7)], "w", 2.2)
    o += circ(ix, iy, 1.4, "bg") + lens_rim(ix, iy, 17)
    # serrations, enlarged
    sx, sy = 161, 150
    o += lens(sx, sy, 24, cx + 30 * ux, cy + 30 * uy)
    zz = zigzag(sx - 30, sy, sx + 30, sy, 3.6, 5.2)
    up = zz + [(sx + 40, sy - 40), (sx - 40, sy - 40)]
    dn = zz + [(sx + 40, sy + 40), (sx - 40, sy + 40)]
    o += section(clip_convex(up, [(sx + 24 * math.cos(math.radians(a)), sy + 24 * math.sin(math.radians(a))) for a in range(0, 360, 12)]), "w", 2.6, 45)
    o += section(clip_convex(dn, [(sx + 24 * math.cos(math.radians(a)), sy + 24 * math.sin(math.radians(a))) for a in range(0, 360, 12)]), "w2", 2.6, -45)
    o += lens_rim(sx, sy, 24)
    return o


@part("marine4.m4piston")
def _():
    cx, top, R = 136, 22, 60
    yc, ys, yb = top + 48, top + 48, top + 146                  # crown/skirt joint, skirt bottom
    o = shadow(176, 190, 124, 7)
    # ghost con-rod small end + shank (oil comes up its centre)
    rodg = [(cx - 20, 90), (cx + 20, 90), (cx + 20, 134), (cx + 12, 146), (cx + 12, 194), (cx - 12, 194), (cx - 12, 146), (cx - 20, 134)]
    o += faint(pg(rodg, "w"), 0.45) + pg(rodg, "o thin dash")
    # ---------------- left half: outside view
    grooves = [(top + 8, 4), (top + 17, 4), (top + 27, 5)]
    o += pg([(cx - R, top + 3), (cx - R + 3, top), (cx, top), (cx, yc), (cx - R, yc)], "w")
    for y0, hh in grooves:
        o += fe(rect(cx - R, y0, R, hh, "w2"))
    for k in range(7):
        o += rect(cx - R + 5 + k * 8, grooves[2][0] + 1.6, 4, 1.8, "bg")        # oil-ring slots
    o += fe(pg([(cx - R + 1, yc), (cx, yc), (cx, yb), (cx - R + 2.5, yb), (cx - R + 1, yb - 30)], "w"))
    o += line(cx - R + 1, yc, cx, yc, "o")
    o += line(cx - 30, yc + 6, cx - 30, yc + 50, "hid")                          # far-side stretch bolt (hidden)
    # ---------------- right half: section
    bowl = [(cx + 38 * t, top + 9 - 9 * math.sin(math.radians(90 * t)) ** 1.2 * 1.0 + 0) for t in [i / 10 for i in range(11)]]
    bowl = [(cx + 38 * t, top + 8 * (1 - math.sin(math.radians(90 * t)))) for t in [i / 10 for i in range(11)]]
    xo = cx + R
    crown = bowl + [(xo - 3, top), (xo, top + 3)]
    for y0, hh in grooves:
        crown += [(xo, y0), (xo - 5, y0), (xo - 5, y0 + hh), (xo, y0 + hh)]
    crown += [(xo, yc), (xo - 10, yc), (xo - 10, top + 12), (xo - 26, top + 12), (xo - 26, yc), (xo - 36, yc), (xo - 36, top + 22),
              (cx, top + 22)]
    o += section(crown, "w", 2.8, 45)
    for y0, hh in grooves:                                                       # rings + hardened groove flanks
        o += fe(rect(xo - 4.6, y0 + 0.4, 4.6, hh - 0.8, "w2"))
        o += '<path class="o" style="stroke-width:1.7" d="M%s %sL%s %sM%s %sL%s %s"/>' % (
            n(xo - 5), n(y0), n(xo), n(y0), n(xo - 5), n(y0 + hh), n(xo), n(y0 + hh))
    skirt = [(cx, yc), (xo, yc), (xo, yb), (xo - 6, yb), (xo - 6, top + 118), (cx + 30, top + 118), (cx + 30, top + 66), (cx + 24, top + 58),
             (cx, top + 58)]
    o += fe(section(skirt, "w", 2.8, -45))
    # oil passages through the skirt top plate
    o += rect(cx + 9, yc - 0.5, 4, 11, "void") + rect(xo - 21, yc - 0.5, 4, 10, "void")
    # hollow piston pin (cut lengthwise)
    o += rect(cx, top + 73, R - 7, 34, "m") + rect(cx, top + 82, R - 9, 16, "w3")
    o += rect(xo - 25, top + 12.5, 15, yc - top - 13, "warmin")
    o += line(cx, top + 73, cx, top + 107, "o thin")
    # stretch bolt crown <- skirt
    o += rect(cx + 18, top + 14, 5, 46, "m") + rect(cx + 14.5, yc + 10, 12, 6, "m2", 1)
    o += line(cx, top - 4, cx, yb + 4, "cl")
    o += '<path class="o" style="stroke-width:1.8" d="M%s %sL%s %s"/>' % (n(cx), n(yc), n(xo), n(yc))   # crown/skirt joint face
    # cooling oil: up the con-rod -> through the skirt plate -> crown centre -> gallery -> back down
    o += flow([(cx + 3, 188), (cx + 3, 152), (cx + 3, top + 104)], "oil", 5.5)
    o += flow([(cx + 11, yc + 10), (cx + 11, top + 34), (cx + 30, top + 27), (xo - 18, top + 18), (xo - 18, top + 40)], "oil", 5.5)
    o += flow([(xo - 19, yc + 2), (xo - 19, yc + 18), (xo - 15, yc + 30)], "oil", 5.5)
    # ---------------- same-scale passenger-car piston (aluminium) for comparison
    px, pr = 270, 16
    o += vcyl(px, yb - 29, 29, pr, 4, "alu", "alu")
    for yy in (yb - 24, yb - 21, yb - 18):
        o += path("M%s %s A%s 4 0 0 0 %s %s" % (n(px - pr), n(yy), n(pr), n(px + pr), n(yy)), "o thin")
    o += circ(px, yb - 10, 3.6, "alu") + circ(px, yb - 10, 1.8, "bg")
    return o


@part("marine4.m4liner")
def _():
    cx, top = 150, 26
    ri, ro, rc, L, hc = 25, 31, 40.5, 148, 30
    yb, ys = top + L, top + hc
    o = shadow(162, 190, 92, 6)
    # ---- surrounding block and head (faint, right side only)
    blk = [(cx + 41.5, top + 2), (cx + 72, top + 2), (cx + 72, yb + 4), (cx + 31.5, yb + 4), (cx + 31.5, yb - 32), (cx + 42, yb - 32),
           (cx + 42, ys + 16), (cx + 31.5, ys + 16), (cx + 31.5, ys), (cx + 41.5, ys)]
    o += faint(section(blk, "w", 3.2, -45), 0.5)
    o += pg([(cx + 31.5, ys + 16), (cx + 42, ys + 16), (cx + 42, yb - 32), (cx + 31.5, yb - 32)], "fl")       # water jacket
    head = [(cx - 6, top - 22), (cx + 72, top - 22), (cx + 72, top - 1.6), (cx - 6, top - 1.6)]
    o += faint(section(head, "w", 3.2, -45), 0.45)
    o += rect(cx + 26, top - 1.6, 15, 1.6, "cu")                                                            # gasket
    # ---- left half: outside
    o += rect(cx - rc, top, rc, hc, "w")
    o += pg([(cx - ro, ys), (cx, ys), (cx, yb), (cx - ro, yb)], "w")
    o += rect(cx - rc, ys - 1, rc - ro, 2, "m2")
    for yy in (yb - 26, yb - 17, yb - 8):
        o += rect(cx - ro - 0.6, yy - 1.6, 2.4, 3.2, "rb")
    # ---- right half: section
    o += rect(cx, top, ri - 1.6, 12, "m2")                                                                # APR, far side
    bw = [(cx, top + 12), (cx + ri, top + 12), (cx + ri, yb), (cx, yb)]
    o += pg(bw, "w")                                                                                     # far bore wall
    segs = []
    for k in range(-3, 16):                                                                              # honing marks
        y0 = top + 12 + k * 10
        segs += [((cx, y0), (cx + ri, y0 + 12)), ((cx, y0 + 12), (cx + ri, y0))]
    o += lines_in(segs, bw)
    wall = [(cx + ri + 1.6, top), (cx + rc, top), (cx + rc, ys), (cx + ro, ys), (cx + ro, yb - 30), (cx + ro - 2, yb - 30), (cx + ro - 2, yb - 23),
            (cx + ro, yb - 23), (cx + ro, yb - 21), (cx + ro - 2, yb - 21), (cx + ro - 2, yb - 14), (cx + ro, yb - 14), (cx + ro, yb - 12),
            (cx + ro - 2, yb - 12), (cx + ro - 2, yb - 5), (cx + ro, yb - 5), (cx + ro, yb), (cx + ri, yb), (cx + ri, top + 12), (cx + ri + 1.6, top + 12)]
    o += section(wall, "w", 2.6, 45)
    for k, (y0, r0) in enumerate(((ys - 4, rc - 3), (ys - 13, rc - 4))):                                 # collar cooling bores
        o += '<path class="fo" style="stroke-width:2.2" d="M%s %sL%s %s"/>' % (n(cx + r0), n(y0), n(cx + ri + 4), n(top + 5 + k * 3))
    for yy in (yb - 26, yb - 17, yb - 8):
        o += circ(cx + ro - 0.4, yy, 1.9, "rb")
    o += rect(cx + ri - 1.6, top, 3.2, 12, "m")                                                            # anti-polishing ring
    o += '<path class="o" style="stroke-width:2" d="M%s %sL%s %s"/>' % (n(cx + ro), n(ys), n(cx + rc), n(ys))  # collar seat
    o += line(cx, top - 26, cx, yb + 6, "cl")
    # ---- inset: honed surface (cross-hatch) + plateau profile
    hx, hy, hr = 272, 48, 27
    o += lens(hx, hy, hr, cx + 12, top + 70)
    disc = [(hx + hr * math.cos(math.radians(a)), hy + hr * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    o += pg(disc, "w")
    segs = []
    for k in range(-9, 10):
        segs += [((hx - 40, hy + k * 6 - 20), (hx + 40, hy + k * 6 + 20)), ((hx - 40, hy + k * 6 + 20), (hx + 40, hy + k * 6 - 20))]
    o += lines_in(segs, disc, "o thin")
    o += lens_rim(hx, hy, hr)
    px0, py0 = 238, 92
    o += panel(px0, py0, 68, 36, 5)
    prof = [(px0 + 4, py0 + 15)]
    xs = [6, 12, 15, 17, 26, 31, 34, 36, 46, 50, 53, 56, 64]
    for i, xx in enumerate(xs):
        prof.append((px0 + xx, py0 + (15 if i % 4 in (0, 3) else 27 - (i % 2) * 3)))
    prof.append((px0 + 64, py0 + 15))
    o += fe(pg(prof + [(px0 + 64, py0 + 32), (px0 + 4, py0 + 32)], "w"))
    o += line(px0 + 4, py0 + 15, px0 + 64, py0 + 15, "o thin dash")
    # ---- inset: centrifugally cast blank -> machined liner
    bx, by = 14, 112
    o += panel(bx, by, 84, 74, 5)
    for x0, done in ((bx + 22, False), (bx + 62, True)):
        for sg in (-1, 1):
            blank = [(x0 + sg * 8, by + 10), (x0 + sg * 16, by + 10), (x0 + sg * 16, by + 66), (x0 + sg * 8, by + 66)]
            if not done:
                o += section(blank, "w", 2.4, 45 * sg)
            else:
                o += faint(pg(blank, "w2"), 0.6) + pg(blank, "o thin dash")
                fin = [(x0 + sg * 9.5, by + 10), (x0 + sg * 16, by + 10), (x0 + sg * 16, by + 22), (x0 + sg * 12.5, by + 22),
                       (x0 + sg * 12.5, by + 66), (x0 + sg * 9.5, by + 66)]
                o += section(fin, "w", 2.4, 45 * sg)
    o += flow([(bx + 38, by + 38), (bx + 46, by + 38)], "a", 5)
    return o


def cam_outline(rb, lift, th, sharp=2.0, seg=48, flank=1.0):
    """cam profile in (u,v): base circle rb + lobe of height lift pointing to angle th (deg)."""
    out = []
    t0 = math.radians(th)
    for k in range(seg):
        ph = 2 * math.pi * k / seg
        c = max(0.0, math.cos((ph - t0) * flank))
        r = rb + lift * c ** sharp
        out.append((r * math.cos(ph), r * math.sin(ph), k // 6))
    return out


@part("marine4.m4cam")
def _():
    rs, rjr, rb = 10, 24, 16.5
    segL = 150
    # per cylinder: (offset, width, kind, lobe angle)
    cyl_a = [(0, 9, "in", 60), (13, 15, "fuel", 190), (32, 9, "ex", 300)]
    cyl_b = [(0, 9, "in", 180), (13, 15, "fuel", 310), (32, 9, "ex", 60)]

    def lobes(sc, x0, plan):
        for off, w, kind, th in plan:
            if kind == "fuel":
                ol = cam_outline(rb, 8.5, th, 1.0, 40, 1.9)
            else:
                ol = cam_outline(rb, 6.0, th, 2.2, 40, 1.0)
            sc.add(GE.prism(sc.cam, (x0 + off, 0, 0), (1, 0, 0), ol, w, "w", dark=1, smooth=True),
                   ((x0 + off, -rb - 9, -rb - 9), (x0 + off + w, rb + 9, rb + 9)))

    def segment(sc, x0, flange_left, flange_right, plans):
        occ = []
        if flange_left:
            CYL(sc, (x0, 0, 0), (1, 0, 0), 30, 7, "w", seg=30)
            occ.append((x0, x0 + 7))
        for xj in (x0 + 10, x0 + 83):
            CYL(sc, (xj, 0, 0), (1, 0, 0), rjr, 16, "m", seg=30)                 # journal
            occ.append((xj, xj + 16))
        for xl, plan in ((x0 + 36, plans[0]), (x0 + 104, plans[1])):
            lobes(sc, xl, plan)
            occ += [(xl + off, xl + off + w) for off, w, _, _ in plan]
        if flange_right:
            CYL(sc, (x0 + segL - 7, 0, 0), (1, 0, 0), 30, 7, "w", seg=30)
            occ.append((x0 + segL - 7, x0 + segL))
        occ.sort()
        xa = x0
        for a, b in occ + [(x0 + segL, x0 + segL)]:
            if a - xa > 0.5:
                CYL(sc, (xa, 0, 0), (1, 0, 0), rs, a - xa, "w", seg=24)
            xa = max(xa, b)

    def build(sc):
        CYL(sc, (-26, 0, 0), (1, 0, 0), 7.5, 26, "w", seg=24)                    # drive end stub
        segment(sc, 0, False, True, (cyl_a, cyl_b))
        segment(sc, segL, True, False, (cyl_a, cyl_b))

    def post(sc):
        cam = sc.cam
        o = ""
        xf = segL + 7                                                             # visible face of the right flange
        for k in range(6):
            t = math.radians(30 + 60 * k)
            c = (xf, 22 * math.cos(t), 22 * math.sin(t))
            o += hole3(cam, c, (1, 0, 0), 3.4, "m2") + hole3(cam, c, (1, 0, 0), 1.6, "m")
        c = (xf, 22 * math.cos(math.radians(0)), 22 * math.sin(math.radians(0)))
        o += hole3(cam, c, (1, 0, 0), 2, "bg")                                    # dowel pin hole
        # end view: phase of inlet / fuel / exhaust cams of one cylinder
        cx, cy, R = 270, 152, 34
        o += lens(cx, cy, R)
        for off, w, kind, th in cyl_a:
            if kind == "fuel":
                ol = cam_outline(rb, 8.5, th, 1.0, 60, 1.9)
                cls, sc_ = "w2", 1.15
            else:
                ol = cam_outline(rb, 6.0, th, 2.2, 60, 1.0)
                cls, sc_ = "o", 1.15
            ps = [(cx + u * sc_, cy - v * sc_) for u, v, _ in ol]
            o += pg(ps, cls) if cls != "o" else path(P(ps), "o" + (" dash" if kind == "ex" else ""))
            t = math.radians(th)
            o += line(cx, cy, cx + (rb + (8.5 if kind == "fuel" else 6)) * sc_ * math.cos(t), cy - (rb + (8.5 if kind == "fuel" else 6)) * sc_ * math.sin(t), "o thin")
        o += circ(cx, cy, rs * 1.15, "m") + circ(cx, cy, 2.2, "bg")
        o += lens_rim(cx, cy, R)
        return o

    return fit_scene(build, -18, 17, area=(10, 12, 310, 120), sh_ry=7, post=post)


def m4_crush_stage(cx, cy, closed):
    """housing halves + bearing shells: open (shell ends stand proud) or bolted (pressed home)."""
    Rh, Rs, gap, ex = 15, 12.6, (0 if closed else 9), 3.0
    o = ""
    hw, hh = 25, 13

    def half_ring(r0, r1, up, dy=0.0, a_ext=0.0):
        a0, a1 = (180, 360) if up else (0, 180)
        out = []
        for k in range(19):
            t = math.radians(a0 + (a1 - a0) * k / 18)
            out.append((cx + r1 * math.cos(t), cy + dy + r1 * math.sin(t)))
        for k in range(19):
            t = math.radians(a1 - (a1 - a0) * k / 18)
            out.append((cx + r0 * math.cos(t), cy + dy + r0 * math.sin(t)))
        if a_ext:
            # extend the shell ends past the joint line (crush height)
            sgn = 1 if up else -1
            e = [(cx + r1, cy + dy), (cx + r1, cy + dy + sgn * a_ext), (cx + r0, cy + dy + sgn * a_ext), (cx + r0, cy + dy)]
            f = [(cx - r0, cy + dy), (cx - r0, cy + dy + sgn * a_ext), (cx - r1, cy + dy + sgn * a_ext), (cx - r1, cy + dy)]
            return out, e, f
        return out, None, None
    # lower housing (block with half bore), upper cap raised when open
    low = [(cx - hw, cy), (cx - Rh, cy)] + [(cx + Rh * math.cos(math.radians(180 - k * 10)), cy + Rh * math.sin(math.radians(180 - k * 10))) for k in range(19)] + \
          [(cx + Rh, cy), (cx + hw, cy), (cx + hw, cy + hh + 6), (cx - hw, cy + hh + 6)]
    up_ = [(cx - hw, cy - gap), (cx - Rh, cy - gap)] + [(cx + Rh * math.cos(math.radians(180 + k * 10)), cy - gap + Rh * math.sin(math.radians(180 + k * 10))) for k in range(19)] + \
          [(cx + Rh, cy - gap), (cx + hw, cy - gap), (cx + hw, cy - gap - hh), (cx - hw, cy - gap - hh)]
    o += fe(pg(low, "w2")) + fe(pg(up_, "w2"))
    for sg in (-1, 1):                                                       # bolts
        bx = cx + sg * 20
        o += rect(bx - 1.8, cy - gap - hh - 4, 3.6, hh + gap + hh + 10, "m")
        o += rect(bx - 3.6, cy - gap - hh - 5, 7.2, 3.2, "m2")
    e = 0 if closed else ex
    lo, a, b = half_ring(Rs, Rh, False, 0, -e if e else 0)
    hi, c, d = half_ring(Rs, Rh, True, -gap, e if e else 0)
    o += pg(lo, "w") + pg(hi, "w")
    for q in (a, b, c, d):
        if q:
            o += pg(q, "w")
    for up, dy in ((False, 0), (True, -gap)):
        a0, a1 = (180, 360) if up else (0, 180)
        ring = [(cx + Rs * math.cos(math.radians(a0 + (a1 - a0) * k / 18)), cy + dy + Rs * math.sin(math.radians(a0 + (a1 - a0) * k / 18))) for k in range(19)]
        ring += [(cx + (Rs - 1.3) * math.cos(math.radians(a1 - (a1 - a0) * k / 18)), cy + dy + (Rs - 1.3) * math.sin(math.radians(a1 - (a1 - a0) * k / 18))) for k in range(19)]
        o += pg(ring, "cu")
    if not closed:
        o += line(cx - hw - 3, cy, cx + hw + 3, cy, "o thin dash")
    else:
        for k in range(8):                                                   # contact pressure all round
            t = math.radians(22.5 + 45 * k)
            o += head(cx + (Rs + 1.8) * math.cos(t), cy + (Rs + 1.8) * math.sin(t), t + math.pi, 3.2)
    return o


@part("marine4.m4bearing")
def _():
    Ro, Rm, W = 50, 45, 40

    def ri_(th):        # inner radius with crush relief near the joint faces (exaggerated)
        d = min(abs(th - 180), abs(th - 360))
        return 41.6 + 2.6 * max(0.0, 1 - d / 30.0) ** 1.5

    def arc(r, a0, a1, seg=36, f=None):
        return [((f(a0 + (a1 - a0) * k / seg) if f else r) * math.cos(math.radians(a0 + (a1 - a0) * k / seg)),
                 (f(a0 + (a1 - a0) * k / seg) if f else r) * math.sin(math.radians(a0 + (a1 - a0) * k / seg))) for k in range(seg + 1)]

    def build(sc):
        back = arc(Ro, 180, 360) + arc(Rm, 360, 180)
        X(sc, 0, W, [(u, v, 0 if k <= 36 else 1) for k, (u, v) in enumerate(back)], "w", smooth=True)
        lin = arc(Rm, 180, 360) + arc(0, 360, 180, f=ri_)
        X(sc, 0.01, W - 0.02, [(u, v, 0 if k <= 36 else 1) for k, (u, v) in enumerate(lin)], "cu", smooth=True, bias=0.1)
        # locating lug at one joint face
        X(sc, 4, 8, [(-Ro - 5, -1), (-Rm + 1, -1), (-Rm + 1, -6), (-Ro - 5, -6)], "w", bias=-0.1)

    def post(sc):
        cam = sc.cam
        o = ""
        g0 = [cam.xy((W / 2 - 1.7, ri_(t) * math.cos(math.radians(t)), ri_(t) * math.sin(math.radians(t)))) for t in range(204, 337, 6)]
        g1 = [cam.xy((W / 2 + 1.7, ri_(t) * math.cos(math.radians(t)), ri_(t) * math.sin(math.radians(t)))) for t in range(336, 203, -6)]
        o += pg(g0 + g1, "bg")
        c = (W / 2, 0, -ri_(270))
        o += hole3(cam, c, (0, 0, 1), 3.4, "bg")
        return o

    def relief_lens(sc):
        cam = sc.cam
        lx, ly, lr = 40, 160, 24
        tip = cam.xy((W, -43, 0))
        o = lens(lx, ly, lr, tip[0], tip[1])
        disc = _circ_pts(lx, ly, lr, 40)
        C = (lx + 30, ly - 12)

        def arc(fr, a1=60, seg=24):
            return [(C[0] - fr(a) * math.cos(math.radians(a)), C[1] + fr(a) * math.sin(math.radians(a))) for a in [a1 * k / seg for k in range(seg + 1)]]
        ri = lambda a: 29 + 4.2 * max(0.0, 1 - a / 26.0) ** 1.5
        back = arc(lambda a: 41) + arc(lambda a: 35)[::-1]
        lin = arc(lambda a: 35) + arc(ri)[::-1]
        o += section(clip_convex(back, disc), "w", 2.4, 45)
        o += pg(clip_convex(lin, disc), "cu")
        o += lines_in([(arc(lambda a: 29)[k], arc(lambda a: 29)[k + 1]) for k in range(0, 12)], disc, "o thin dash")
        o += line(lx - lr, C[1], lx + lr, C[1], "o thin")
        return o + lens_rim(lx, ly, lr)

    out = fit_scene(build, -52, 28, area=(14, 26, 184, 178), sh_ry=8, post=lambda sc: post(sc) + relief_lens(sc))
    # layer build-up (bottom to top): steel back / bearing alloy / nickel barrier / overlay / tin flash
    px, py, pw, ph = 196, 14, 110, 74
    out += panel(px, py, pw, ph, 5)
    x0, x1 = px + 8, px + pw - 8
    layers = [(28, "w", True), (14, "cu", False), (3, "gw", False), (7, "m2", False), (2.4, "m", False)]
    y = py + ph - 6
    for th, cls, hat in layers:
        y0 = y - th
        if hat:
            o2 = section([(x0, y0), (x1, y0), (x1, y), (x0, y)], "w", 3, 45)
        else:
            o2 = rect(x0, y0, x1 - x0, th, cls)
        out += o2
        y = y0
    zz = zigzag(x0 - 3, py + ph - 20, x1 + 3, py + ph - 20, 1.8, 5)
    band = [(x, y - 1.6) for x, y in zz] + [(x, y + 1.6) for x, y in reversed(zz)]
    out += pg(band, "void") + path(P([(x, y - 1.6) for x, y in zz], False), "o thin") + path(P([(x, y + 1.6) for x, y in zz], False), "o thin")
    # crush height: open -> bolted
    out += panel(190, 100, 116, 88, 5)
    out += m4_crush_stage(219, 150, False) + m4_crush_stage(277, 150, True)
    out += flow([(244, 122), (252, 122)], "a", 5)
    return out


def test_bed(x, y, w, h):
    """test-bed schematic: engine - generator - load bank, with cylinder-pressure and exhaust-gas measurement."""
    o = panel(x, y, w, h, 5)
    gy = y + h - 12
    o += rect(x + 6, gy, w - 12, 4, "m2")                                       # bed plate
    # engine
    o += rect(x + 10, gy - 22, 28, 22, "pt") + rect(x + 12, gy - 30, 24, 8, "pt")
    for k in range(4):
        o += rect(x + 13 + k * 6, gy - 33, 4.4, 3, "m2")
    o += rect(x + 30, gy - 40, 6, 10, "m")                                      # exhaust stack
    # coupling + generator + load bank
    o += rect(x + 38, gy - 13, 8, 4, "m")
    o += rect(x + 46, gy - 22, 22, 22, "dk", 3)
    for k in range(4):
        o += line(x + 49 + k * 5, gy - 20, x + 49 + k * 5, gy - 2, "o thin")
    o += path("M%s %s L%s %s L%s %s" % (n(x + 68), n(gy - 14), n(x + 74), n(gy - 14), n(x + 74), n(gy - 6)), "cable")
    o += rect(x + 76, gy - 20, 18, 20, "m", 2)
    for k in range(3):
        o += path("M%s %s l3 -3 l3 3 l3 -3 l3 3" % (n(x + 79), n(gy - 14 + k * 5)), "hl")
    # instruments: cylinder pressure trace + exhaust analyser
    sx, sy = x + 10, y + 6
    o += rect(sx, sy, 24, 15, "scrn", 2)
    o += path("M%s %s l5 0 c3 0 3 -9 5 -9 c2 0 3 9 6 9 l5 0" % (n(sx + 2), n(sy + 12)), "scrg")
    o += path("M%s %s L%s %s" % (n(sx + 12), n(sy + 15), n(sx + 12), n(gy - 30)), "o thin dash")
    ax, ay = x + 44, y + 6
    o += rect(ax, ay, 20, 15, "m", 2) + circ(ax + 7, ay + 7.5, 4, "scrn") + rect(ax + 13, ay + 4, 4, 7, "m2")
    o += path("M%s %s L%s %s L%s %s" % (n(ax), n(ay + 10), n(x + 33), n(ay + 10), n(x + 33), n(gy - 40)), "o thin dash")
    return o


@part("marine4.m4assy")
def _():
    pitch, L = 80, 480
    cyl = [40 + pitch * i for i in range(6)]

    def FE(sc, svg_, bb, bias=0.0):
        sc.add('<g class="ilu mt-fe">%s</g>' % svg_, bb, bias)

    def build(sc):
        cam = sc.cam
        BOX(sc, -20, -14, 0, 590, 178, 20, "dk")                                       # base frame
        BOX(sc, 0, 0, 20, L, 150, 130, "pt", lines=False)                               # block
        for xc in cyl:                                                                  # crankcase doors
            Y(sc, 0, 3, [(xc - 26, 36), (xc + 26, 36), (xc + 26, 80), (xc - 26, 80)], "pt", bias=-0.1)
        BOX(sc, 0, -16, 92, L, 16, 18, "pt")                                            # pump ledge
        for xc in cyl:                                                                  # fuel injection pumps
            BOX(sc, xc - 9, -15, 110, 18, 13, 26, "m")
            CYL(sc, (xc, -8.5, 136), (0, 0, 1), 5, 7, "m", seg=16)
        for xc in cyl:                                                                  # heads + rocker covers
            BOX(sc, xc - 36, 6, 150, 72, 138, 42, "pt")
            BOX(sc, xc - 30, 18, 192, 60, 112, 16, "pt", cap_mat="m2")
            BOX(sc, xc - 12, 144, 162, 24, 12, 26, "m")                                 # exhaust branch
        for k in range(6):                                                              # insulated exhaust manifold
            BOX(sc, 14 + k * 77.5, 156, 158, 75.5, 34, 44, "m", cap_mat="m2")
        # free end: gear case, engine-driven pumps, charge air cooler, turbocharger, air filter-silencer
        X(sc, -12, 12, [(8, 28), (142, 28), (142, 118), (110, 140), (8, 140)], "pt")
        for yy in (36, 112):
            CYL(sc, (-46, yy, 62), (1, 0, 0), 14, 34, "pt", seg=24)
            CYL(sc, (-52, yy, 62), (1, 0, 0), 9, 6, "m", seg=20)
        BOX(sc, -64, 26, 128, 52, 118, 62, "pt")                                        # charge air cooler
        BOX(sc, -12, 150, 196, 34, 30, 30, "m")                                         # manifold -> turbine duct
        FE(sc, GE.cyl(cam, (-40, 100, 238), (1, 0, 0), 22, 30, "w", seg=28), ((-40, 78, 216), (-10, 122, 260)))      # bearing casing
        FE(sc, GE.cyl(cam, (-10, 100, 238), (1, 0, 0), 38, 34, "w", seg=32), ((-10, 62, 200), (24, 138, 276)))       # turbine casing
        sc.add(GE.cyl(cam, (-74, 100, 238), (1, 0, 0), 36, 34, "alu", seg=32), ((-74, 64, 202), (-40, 136, 274)))   # compressor casing
        sc.add(GE.cyl(cam, (-118, 100, 238), (1, 0, 0), 40, 44, "m", seg=32), ((-118, 60, 198), (-74, 140, 278)), -0.1)  # filter-silencer
        BOX(sc, -66, 70, 190, 22, 50, 22, "alu")                                        # compressor -> cooler duct
        CYL(sc, (6, 100, 270), (0, 0, 1), 20, 22, "m", seg=24)                          # gas outlet
        # rear end: flywheel + coupling to the generator
        CYL(sc, (L, 75, 86), (1, 0, 0), 66, 18, "m", seg=40)
        CYL(sc, (L + 18, 75, 86), (1, 0, 0), 28, 30, "m", seg=28)
        CYL(sc, (L + 48, 75, 86), (1, 0, 0), 44, 10, "m", seg=36)
        RAW(sc, lambda s_: person(*s_.P((-150, -40, 0)), h=140 * s_.k * s_.cam.ce), ((-160, -46, 0), (-140, -34, 140)))

    def post(sc):
        cam = sc.cam
        o = ""
        for xc in cyl:                                                                  # double-walled HP fuel pipes
            a = cam.xy((xc, -8.5, 143))
            b = cam.xy((xc - 4, -10, 168))
            c = cam.xy((xc - 8, 2, 176))
            d = cam.xy((xc - 10, 6, 176))
            dd = smooth_d([a, b, c, d])
            o += '<path class="pipe" style="stroke-width:4.2" d="%s"/>' % dd + '<path class="o thin" d="%s"/>' % dd
        for xc in cyl:                                                                  # door handles / bolts
            c = cam.xy((xc, -3, 58))
            o += circ(c[0], c[1], 1.6 * sc.k * 1.5, "m2")
        for xx in (-110, -98, -86):
            o += path(smooth_d(circ3(cam, (xx, 100, 238), (1, 0, 0), 40.5, 16, 90, 270)), "o thin")
        return o

    out = fit_scene(build, 28, 22, area=(8, 6, 306, 168), sh_ry=10, post=post)
    out += test_bed(212, 140, 96, 54)
    return out


# =====================================================================================
# marineaux: large turbocharger, fuel injection, exhaust after-treatment
# =====================================================================================
def _up(ps, ax=100.0):
    return [(x, ax - r) for x, r in ps]


def _dn(ps, ax=100.0):
    return [(x, ax + r) for x, r in ps]


def _circ_pts(cx, cy, r, seg=28):
    return [(cx + r * math.cos(2 * math.pi * k / seg), cy + r * math.sin(2 * math.pi * k / seg)) for k in range(seg)]


@part("marineaux.mxtcassy")
def _():
    o = shadow(160, 194, 140, 5)
    # ---------------- solid casings (cavities painted over afterwards)
    compC = [(54, 0), (54, 35), (92, 35), (97, 66), (104, 80), (116, 84), (128, 81), (134, 71), (134, 0)]
    brgC = [(126, 0), (126, 40), (132, 45), (190, 45), (196, 40), (196, 0)]
    tinC = [(194, 0), (194, 82), (203, 90), (222, 90), (232, 84), (238, 70), (238, 0)]
    outC = [(236, 31.5), (236, 58), (292, 58), (292, 66), (304, 66), (304, 49), (238, 31.5)]
    sil = [(10, 34), (54, 34), (54, 64), (46, 70), (10, 70)]
    for f, poly_, cls, ang in ((_up, compC, "alu", 45), (_dn, compC, "alu", 45)):
        o += section(f(poly_), cls, 3, ang)
    for f in (_up, _dn):
        o += section(f(brgC), "w", 3, -45)
        o += section(f(tinC), "w", 3, 45)
        o += section(f(outC), "w", 3, -45)
    o += rect(10, 36, 44, 128, "m", 4)                                                   # air filter-silencer
    for k in range(9):
        o += line(14 + k * 4.6, 40, 14 + k * 4.6, 160, "o thin")
    o += rect(10, 74, 44, 52, "void") + rect(10, 74, 44, 52, "o")
    # ---------------- cavities: air path, volutes, gas path, oil
    air = [(54, 0), (54, 26), (88, 25), (90, 25.5), (100, 29), (110, 34), (116, 38.5), (118.5, 41), (118.5, 56), (123.5, 56),
           (123.5, 41), (124.8, 41), (124.8, 0)]
    gas = [(200.5, 0), (200.5, 41), (203.5, 41), (203.5, 53), (213, 53), (213, 41), (214, 40.5), (220, 38.5), (228, 35), (236.5, 31.5),
           (304, 49), (304, 0)]
    for f in (_up, _dn):
        o += pg(f(air), "void") + pg(f(gas), "void")
    o += pg(_circ_pts(116, 100 - 67, 13), "void") + pg(_circ_pts(116, 100 + 64, 10), "void")             # compressor volute
    o += pg(_circ_pts(214, 100 - 67, 14), "void") + pg(_circ_pts(214, 100 + 65, 18), "void")             # gas inlet volute
    o += rect(205, 172, 18, 26, "void")                                                                  # gas inlet (from below)
    o += pg(_up([(162, 9), (166, 9), (166, 46), (162, 46)]), "void")                                     # oil feed
    o += pg(_dn([(148, 9), (180, 9), (180, 46), (148, 46)]), "void")                                     # oil drain
    for f in (_up, _dn):
        o += pg(f([(138, 4.5), (190, 4.5), (190, 9.5), (138, 9.5)]), "void")
    # outlines of the cavities
    for f in (_up, _dn):
        o += path(P(f(air[1:-1]), False), "o") + path(P(f(gas[1:-1]), False), "o")
    o += path(P(_circ_pts(116, 33, 13)), "o") + path(P(_circ_pts(116, 164, 10)), "o")
    o += path(P(_circ_pts(214, 33, 14)), "o") + path(P(_circ_pts(214, 165, 18)), "o")
    o += rect(203, 194, 22, 4, "w") + line(205, 172, 205, 194, "o") + line(223, 172, 223, 194, "o")      # inlet flange
    o += rect(158, 46, 12, 8, "m", 1.5)                                                                  # oil inlet fitting
    # ---------------- rotor
    o += rect(84, 95.5, 120, 9, "m")                                                                    # shaft
    o += rect(80, 94, 6, 12, "m2", 1)                                                                   # compressor nut
    hubc = [(90 + 32 * t, 7 + 31 * t ** 1.7) for t in [k / 12 for k in range(13)]]
    shr = [(90 + 28 * t, 24 + 14.5 * t ** 1.8) for t in [k / 12 for k in range(13)]]
    for f in (_up, _dn):
        o += pg(f([(90, 7.5), (90, 24)] + shr + [(122, 38.5)] + hubc[::-1]), "alu")                    # blades (meridional)
        o += section(f([(87, 4.5), (87, 7)] + hubc + [(124.5, 38.5), (124.5, 4.5)]), "alu", 2.2, -45)   # hub
    th = [(205 + 35 * t, 9 + 31 * (1 - t) ** 1.6) for t in [k / 12 for k in range(13)]]
    ts = [(212 + 24 * t, 30 + 10 * (1 - t) ** 2) for t in [k / 12 for k in range(13)]]
    for f in (_up, _dn):
        o += pg(f([(205, 40.5), (212, 40.5)] + ts[1:] + [(236, 10)] + [p for p in th[::-1] if p[0] < 236]), "gw")
        o += section(f([(202.5, 0), (202.5, 42), (205, 42)] + th + [(241, 6), (241, 0)]), "gw", 2.2, 45)
        nz = f([(204, 41.5), (213, 41.5), (213, 52.5), (204, 52.5)])
        o += pg(nz, "gw")
        y0, y1 = min(p[1] for p in nz), max(p[1] for p in nz)
        for k in range(4):
            o += line(205 + k * 2.4, y1, 207.5 + k * 2.4, y0, "o thin")
    o += '<path class="o" style="stroke-width:2.2" d="M202.5 95.5L202.5 104.5"/>'                       # friction weld
    o += rect(198, 60, 3, 80, "m")                                                                      # heat shield
    # bearings
    for x0 in (140, 176):
        for f in (_up, _dn):
            o += pg(f([(x0, 4.5), (x0 + 12, 4.5), (x0 + 12, 9.5), (x0, 9.5)]), "cu")
    o += rect(156, 84, 4, 32, "m")                                                                      # thrust collar
    for x0 in (152.5, 160):
        for f in (_up, _dn):
            o += pg(f([(x0, 8.5), (x0 + 3.5, 8.5), (x0 + 3.5, 16), (x0, 16)]), "cu")
    for k in range(4):                                                                                   # labyrinth
        o += line(192 + k * 2, 95.5, 192 + k * 2, 93, "o thin") + line(192 + k * 2, 104.5, 192 + k * 2, 107, "o thin")
    o += line(4, 100, 310, 100, "cl")
    # ---------------- flows
    o += flow([(2, 60), (24, 68), (52, 82), (80, 86), (100, 80), (111, 64), (116, 46)], "air")
    o += flow([(2, 140), (24, 132), (52, 118), (80, 114), (100, 120), (111, 136), (116, 154)], "air")
    o += flow([(214, 199), (214, 184), (214, 176)], "gas")
    o += flow([(214, 46), (209, 58), (214, 70), (230, 79), (262, 83), (300, 84)], "gas")
    o += flow([(214, 152), (209, 142), (214, 130), (230, 121), (262, 117), (300, 116)], "gas")
    o += flow([(164, 30), (164, 44), (164, 62)], "oil", 5)
    o += flow([(164, 112), (164, 136), (164, 152)], "oil", 5)
    # ---------------- tip clearance (enlarged)
    bx, by, br = 266, 24, 17
    o += lens(bx, by, br, 231, 66)
    disc = _circ_pts(bx, by, br, 36)
    cas = clip_convex([(bx - 30, by - 30), (bx + 30, by - 30), (bx + 30, by - 4), (bx - 30, by + 6)], disc)
    o += section(cas, "w", 2.6, -45)
    bl = clip_convex([(bx - 30, by + 11), (bx + 30, by + 1), (bx + 30, by + 30), (bx - 30, by + 30)], disc)
    o += pg(bl, "gw")
    o += lens_rim(bx, by, br)
    return o


FIR = [(7.5, 0), (7.5, -2.5), (5.0, -5), (6.4, -7.5), (3.9, -10), (5.2, -12.5), (2.7, -15), (3.8, -17.5), (1.6, -20), (0, -21)]


def fir_profile(cx, shrink=0.0):
    """closed fir-tree profile (x,z) centred at cx, open side up (z=0)."""
    right = [(cx + max(0.4, x - shrink), z) for x, z in FIR[:-1]] + [(cx, FIR[-1][1] + shrink)]
    left = [(cx - max(0.4, x - shrink), z) for x, z in reversed(FIR[:-1])]
    return right + left


@part("marineaux.mxturb")
def _():
    o = shadow(110, 106, 100, 6) + shadow(236, 188, 62, 5)
    K, X0, Y0 = 1.2, 12, 56

    def S(x, y):
        return (X0 + (x - 14) * K, Y0 + (y - 104) * K)

    def SP(ps):
        return [S(x, y) for x, y in ps]

    def R(x0, y0, w, h, c):
        return pg(SP([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]), c)

    def L(x0, y0, x1, y1, c="o thin"):
        a, b = S(x0, y0), S(x1, y1)
        return line(a[0], a[1], b[0], b[1], c)
    ay = 104
    # ---------------- left: radial turbine rotor (side view, wheel in half section)
    segs = [(16, 30, 4.2, "w"), (30, 48, 5.6, "w"), (48, 52, 7, "w"), (52, 68, 8.2, "m"), (68, 92, 7, "w"), (92, 108, 8.2, "m"),
            (108, 122, 9, "w"), (122, 128.5, 11, "w")]
    for x0, x1, r, c in segs:
        o += R(x0, ay - r, x1 - x0, 2 * r, c)
    for k in range(6):                                                                    # thread
        o += L(17 + k * 2.2, ay - 4.2, 18.6 + k * 2.2, ay + 4.2)
    for k in range(6):                                                                    # labyrinth seal grooves
        o += L(110 + k * 2.2, ay - 9, 110 + k * 2.2, ay + 9)
    hub = [(140 + 36 * t, 7 + 24.5 * (1 - t) ** 1.5) for t in [k / 14 for k in range(15)]]
    shr = [(142 + 28 * t, 24 + 8 * (1 - t) ** 2) for t in [k / 14 for k in range(15)]]
    env_up = [(128.5, ay - 11), (134, ay - 11), (134, ay - 32), (142, ay - 32)] + [(x, ay - r) for x, r in shr] + [(170, ay - 9), (176, ay - 7), (176, ay)]
    env_dn = [(x, 2 * ay - y) for x, y in env_up]
    o += pg(SP(env_dn + [(128.5, ay)]), "gw")
    o += R(134, ay, 6, 32, "gw")                                                          # back disc (outside)
    for k in range(6):                                                                    # blades seen from outside
        f = k / 5.0
        a = (140 + 2, ay + 31.5 - 25 * f)
        bl = [(141, ay + 32 - 24 * f), (148, ay + 30.5 - 24 * f), (157, ay + 26 - 20 * f), (166, ay + 21 - 13 * f), (171, ay + 20 - 11 * f),
              (171, ay + 16.5 - 10 * f), (165, ay + 17.5 - 12 * f), (156, ay + 22 - 19 * f), (147, ay + 27 - 23 * f), (141, ay + 28.5 - 24 * f)]
        bl = [(x, min(y, ay + 32)) for x, y in bl]
        if f < 0.95:
            o += pg(SP(bl), "gws2" if k % 2 else "gws3") + path(P(SP(bl)), "o thin")
    # upper half: section (hub hatched, blade in meridional view)
    o += pg(SP([(134, ay - 32), (142, ay - 32)] + [(x, ay - r) for x, r in shr] + [(170, ay - 9)] + [(x, ay - r) for x, r in hub[::-1] if x < 171] + [(140, ay - 31.5)]), "gw")
    o += section(SP([(128.5, ay), (128.5, ay - 11), (134, ay - 11), (134, ay - 32.5), (140, ay - 32.5)] + [(x, ay - r) for x, r in hub] + [(176, ay)]), "gw", 2.4, 45)
    a, b = S(128.5, ay - 11.5), S(128.5, ay + 11.5)
    o += '<path class="o" style="stroke-width:2.6" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))   # friction weld
    a, b = S(10, ay), S(182, ay)
    o += line(a[0], a[1], b[0], b[1], "cl")
    # ---------------- right: axial turbine disc rim, fir-tree slots, blade sliding in
    def build(sc):
        ol = [(-46, -34), (46, -34), (46, 0)]
        for cx in (30, 0, -30):
            prof = fir_profile(cx)
            ol += [(cx + 7.5, 0)] + [(cx + x, z) for x, z in FIR[1:-1]] + [(cx, -21)] + [(cx - x, z) for x, z in reversed(FIR[1:-1])] + [(cx - 7.5, 0)]
        ol += [(-46, 0)]
        Y(sc, 30, 30, [(x, z, k) for k, (x, z) in enumerate(ol)], "w", dark=0)
        for cx, dy in ((0, 0), (-30, -20)):
            root = [(cx + x - 0.3 * (1 if x > 0 else -1), z) for x, z in [(7.5, 1.5)] + [(xx, zz) for xx, zz in FIR[1:-1]]] + [(cx, -20.6)] + \
                   [(cx - x + 0.3, z) for x, z in [(xx, zz) for xx, zz in reversed(FIR[1:-1])] + [(7.5, 1.5)]]
            Y(sc, 30 + dy, 30, [(x, z, k) for k, (x, z) in enumerate(root)], "gw", bias=-0.05)
            BOX(sc, cx - 14, 0 + dy, 1.5, 28, 30, 4, "gw")
            foil = []
            for k in range(11):
                t = k / 10
                foil.append((cx - 3 + 6.5 * math.sin(math.pi * t), dy + 2 + 26 * t))
            for k in range(11):
                t = 1 - k / 10
                foil.append((cx - 3 + 6.5 * math.sin(math.pi * t) - 2.6 * math.sin(math.pi * t) ** 0.7, dy + 2 + 26 * t))
            Z(sc, 5.5, 46, [(x, y, k // 3) for k, (x, y) in enumerate(foil)], "gw", smooth=True)

    def post(sc):
        a = sc.cam.xy((-30, -62, -9))
        b = sc.cam.xy((-30, -26, -9))
        return flow([a, b], "a", 7)

    o += fit_scene(build, -24, 26, area=(160, 96, 312, 186), sh=False, post=post)
    return o


def impeller3d(cam, R=50.0, H=50.0, zb=8.0, b2=7.0, Z=10, r0f=0.22, rs0f=0.62, wrap=(0.95, -0.42), mat="alu", nt=9, splitters=True,
               lean=0.3, back=True):
    """shaded centrifugal impeller (axis +z, inlet up). returns svg."""
    r0, rs0 = R * r0f, R * rs0f
    LV = GE.LIGHT
    D = cam.D

    def hub(t):
        th = t * math.pi / 2
        return (R - (R - r0) * math.cos(th), zb + (H - zb) * (1 - math.sin(th)))

    def shr(t):
        th = t * math.pi / 2
        return (R - (R - rs0) * math.cos(th), zb + b2 + (H - zb - b2) * (1 - math.sin(th)))

    def P3(r, z, ph):
        return (r * math.cos(ph), r * math.sin(ph), z)

    def nrm(a, b, c):
        u = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        v = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        return GE._norm(GE._cross(u, v))

    def cls_of(nv, two_sided=False, dark=0):
        if two_sided and GE._dot(nv, D) > 0:
            nv = (-nv[0], -nv[1], -nv[2])
            dark += 1
        return mat + "s%d" % min(4, GE.shade(nv) + dark)
    items = []
    # hub surface of revolution
    NTH = 44
    for i in range(NTH):
        p0, p1 = 2 * math.pi * i / NTH, 2 * math.pi * (i + 1) / NTH
        for k in range(nt):
            t0, t1 = k / nt, (k + 1) / nt
            (ra, za), (rb, zb_) = hub(t0), hub(t1)
            q = [P3(ra, za, p0), P3(ra, za, p1), P3(rb, zb_, p1), P3(rb, zb_, p0)]
            nv = nrm(q[0], q[1], q[3])
            if GE._dot(nv, (q[0][0], q[0][1], 0)) < 0:
                nv = (-nv[0], -nv[1], -nv[2])
            if GE._dot(nv, D) >= 0:
                continue
            items.append((sum(cam.P(p)[2] for p in q) / 4, cls_of(nv, dark=1), [cam.xy(p) for p in q], False))

    def blade(phi0, t_start):
        ns = 2
        for k in range(nt):
            t0 = t_start + (1 - t_start) * k / nt
            t1 = t_start + (1 - t_start) * (k + 1) / nt
            for j in range(ns):
                s0, s1 = j / ns, (j + 1) / ns
                pts_ = []
                for t, s_ in ((t0, s0), (t1, s0), (t1, s1), (t0, s1)):
                    (rh, zh), (rt, zt) = hub(t), shr(t)
                    r, z = rh + (rt - rh) * s_, zh + (zt - zh) * s_
                    ph = phi0 + wrap[0] * (1 - t) ** 2 + wrap[1] * t ** 2 + lean * s_ * (1 - t) ** 2
                    pts_.append(P3(r, z, ph))
                nv = nrm(pts_[0], pts_[1], pts_[3])
                tip = (j == ns - 1, k == 0)
                items.append((sum(cam.P(p)[2] for p in pts_) / 4 - 0.5, cls_of(nv, True), [cam.xy(p) for p in pts_], tip))
    for b in range(Z):
        blade(2 * math.pi * b / Z, 0.0)
        if splitters:
            blade(2 * math.pi * (b + 0.5) / Z, 0.4)
    items.sort(key=lambda it: -it[0])
    out = ""
    if back:
        out += GE.cyl(cam, (0, 0, 0), (0, 0, 1), R, zb, mat, seg=64)
    for dep, cls, ps, tip in items:
        out += '<path class="%s" d="%s"/>' % (cls, P(ps))
        if tip and tip[0]:
            out += '<path class="el" d="%s"/>' % P([ps[3], ps[2]], False)
        if tip and tip[1]:
            out += '<path class="el" d="%s"/>' % P([ps[0], ps[3]], False)
    return out


@part("marineaux.mxcomp")
def _():
    o = shadow(104, 178, 86, 8)
    cam = GE.Cam(104, 122, -18, 34, 1.5)
    o += impeller3d(cam, 50, 50, 8, 7, 10, wrap=(0.75, -0.38), lean=0.35)
    c = cam.xy((0, 0, 50))
    o += '<ellipse class="alu" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(c[0]), n(c[1]), n(9 * 1.5), n(9 * 1.5 * cam.se))
    o += '<ellipse class="bg" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(c[0]), n(c[1]), n(4.6 * 1.5), n(4.6 * 1.5 * cam.se))
    # ---- side half-section: hub hatched, blade thin at the tip, balance cuts on the back face
    px, py, pw, ph = 210, 12, 96, 84
    o += panel(px, py, pw, ph, 5)
    ax, by0, k = px + pw / 2, py + ph - 14, 0.86

    def M(r, z):
        return (ax + r * k, by0 - z * k)
    hubc = [(50 - 39 * math.cos(t * math.pi / 2), 8 + 42 * (1 - math.sin(t * math.pi / 2))) for t in [i / 14 for i in range(15)]]
    shrc = [(50 - 19 * math.cos(t * math.pi / 2), 15 + 35 * (1 - math.sin(t * math.pi / 2))) for t in [i / 14 for i in range(15)]]
    for sg in (-1, 1):
        env = [M(sg * 4.5, 0), M(sg * 50, 0), M(sg * 50, 15)] + [M(sg * r, z) for r, z in shrc[::-1]] + [M(sg * 11, 50), M(sg * 4.5, 50)]
        if sg < 0:
            o += pg(env, "alu")
        else:
            o += pg([M(50, 8), M(50, 15)] + [M(r, z) for r, z in shrc[::-1]] + [M(11, 50)] + [M(r, z) for r, z in hubc], "alu")
            o += section([M(4.5, 0), M(50, 0), M(50, 8)] + [M(r, z) for r, z in hubc[::-1]] + [M(11, 52), M(4.5, 52)], "alu", 2.4, 45)
    o += rect(ax - 4.5 * k, by0 - 52 * k, 9 * k, 52 * k, "void") + line(ax, by0 + 4, ax, py + 4, "cl")
    for r in (-40, -30, 30, 40):                                                      # balance cuts
        d = "M%s %s a%s %s 0 0 1 %s 0Z" % (n(M(r - 2.5, 0)[0]), n(M(0, 0)[1]), n(2.5 * k), n(2.2 * k), n(5 * k))
        o += path(d, "void") + path(d, "o")
    # blade thickness across the span: thick at the hub, a few mm at the tip
    w0 = [M(33, 26), M(42.5, 32.5)]
    o += pg([(w0[0][0] - 2.4, w0[0][1] + 1.2), (w0[0][0] + 2.4, w0[0][1] - 1.2), (w0[1][0] + 0.6, w0[1][1] - 0.3), (w0[1][0] - 0.6, w0[1][1] + 0.3)], "m3")
    # ---- 5-axis machining: ball end mill tilted into the passage between two blades
    qx, qy, qw, qh = 210, 104, 96, 84
    o += panel(qx, qy, qw, qh, 5)
    for dx, cls in ((0, "alu"), (40, "alu")):
        bl = [(qx + 12 + dx, qy + qh - 10), (qx + 22 + dx, qy + 50), (qx + 40 + dx, qy + 24), (qx + 44 + dx, qy + 25), (qx + 27 + dx, qy + 51),
              (qx + 19 + dx, qy + qh - 10)]
        o += path(smooth_d(bl, True), cls)
    o += rect(qx + 6, qy + qh - 10, qw - 12, 4, "alu")
    tx0, ty0, ang = qx + 46, qy + 64, math.radians(-62)
    ux, uy = math.cos(ang), math.sin(ang)
    o += rbar(tx0 + ux * 10, ty0 + uy * 10, tx0 + ux * 46, ty0 + uy * 46, 9, "m")        # holder / shank
    o += rbar(tx0, ty0, tx0 + ux * 12, ty0 + uy * 12, 6, "t")                           # flutes
    o += circ(tx0, ty0, 3, "t")
    o += rot(tx0 + ux * 40, ty0 + uy * 40, 12, 12, 120, 210)
    return o


def spring_section(x0, x1, y0, y1, r=1.9, pitch=4.4):
    """helical spring cut lengthwise: wire sections on both sides, x0/x1 wire centres."""
    o = ""
    k = 0
    y = y0 + r
    while y <= y1 - r + 0.01:
        o += circ(x0, y, r, "m") + circ(x1, y + pitch / 2 if y + pitch / 2 <= y1 - r else y, r, "m")
        y += pitch
        k += 1
    return o


def pump_stage(cx, top, spill):
    """barrel + plunger close-up: spill=False -> port covered (delivery), True -> helix at the port (spill)."""
    o = ""
    yt, yb = 26, 140
    for sg in (-1, 1):
        wall = [(cx + sg * 8.5, yt), (cx + sg * 18, yt), (cx + sg * 18, yb), (cx + sg * 8.5, yb)]
        o += section(wall, "w", 2.6, 45 * sg)
    o += rect(cx + 8.5, 66, 9.5, 8, "void") + line(cx + 8.5, 66, cx + 18, 66, "o") + line(cx + 8.5, 74, cx + 18, 74, "o")  # spill port
    o += rect(cx - 8.5, yt, 17, top - yt, "beamf")                                                    # fuel above the plunger
    pl = [(cx - 8, top), (cx + 8, top), (cx + 8, yb + 6), (cx - 8, yb + 6)]
    o += pg(pl, "m")
    hel = [(cx - 2, top + 9), (cx + 8, top + 26), (cx + 8, top + 44), (cx - 2, top + 27)]
    o += pg(hel, "w3")                                                                                # helix (lead) recess
    o += rect(cx - 3.5, top, 3, 12, "w3")                                                             # vertical groove
    if spill:
        o += rect(cx - 3.5, top, 3, 12, "beamf") + pg(hel, "beamf")
        o += flow([(cx + 6, 70), (cx + 16, 70), (cx + 30, 70)], "fuel", 5.5)
        o += rot(cx, yb - 4, 15, 5, 200, 340)
    else:
        o += flow([(cx, top - 4), (cx, yt + 2), (cx, yt - 12)], "fuel", 5.5)
    return o


@part("marineaux.mxpump")
def _():
    cx = 92
    o = shadow(cx, 197, 52, 3)
    # cam + roller tappet + return spring
    camp = cam_outline(22, 9, 90, 2.0, 48, 1.0)
    o += pg([(cx + u, 210 - v) for u, v, _ in camp], "w")
    for sg in (-1, 1):
        o += section([(cx + sg * 18, 128), (cx + sg * 28, 128), (cx + sg * 28, 190), (cx + sg * 18, 190)], "w", 3, 45 * sg)
    o += rect(cx - 17, 132, 34, 36, "m", 2)                                                           # tappet
    o += circ(cx, 170, 9.5, "m") + circ(cx, 170, 3, "m2")                                             # roller
    o += rect(cx - 4, 98, 8, 36, "m")                                                                 # plunger stem
    o += spring_section(cx - 12, cx + 12, 102, 128, 2.1, 4.6)
    o += rect(cx - 15, 128, 30, 4, "m2")                                                              # spring seat on the plunger foot
    # pump body, barrel, gallery, delivery valve
    body = [(cx - 34, 24), (cx + 34, 24), (cx + 34, 86), (cx - 34, 86)]
    o += section(body, "w", 3.2, 45)
    o += rect(cx - 21, 38, 42, 18, "beamf") + rect(cx - 21, 38, 42, 18, "o")                         # fuel gallery
    o += rect(cx + 21, 44, 13, 6, "beamf")
    for sg in (-1, 1):
        o += section([(cx + sg * 5.5, 32), (cx + sg * 13, 32), (cx + sg * 13, 86), (cx + sg * 5.5, 86)], "w", 2.4, -45 * sg)
    o += rect(cx - 13, 44, 7.5, 5, "beamf") + rect(cx + 5.5, 44, 7.5, 5, "beamf")                     # spill ports
    o += rect(cx - 5.5, 32, 11, 8, "beamf")                                                          # pressure chamber
    o += rect(cx - 5, 40, 10, 62, "m")                                                                # plunger
    o += pg([(cx - 1, 50), (cx + 5, 58), (cx + 5, 66), (cx - 1, 58)], "w3") + rect(cx - 2.6, 40, 2.4, 12, "w3")
    o += rect(cx - 13, 16, 26, 16, "w") + rect(cx - 13, 16, 26, 16, "o")                             # delivery valve seat body
    o += pg([(cx - 5, 30), (cx + 5, 30), (cx + 2, 25), (cx - 2, 25)], "m") + rect(cx - 1.2, 19, 2.4, 6, "m")
    o += rect(cx - 9, 5, 18, 12, "m", 2) + rect(cx - 2, 5, 4, 12, "beamf")                            # outlet fitting
    o += flow([(cx + 1, 16), (cx + 1, 9), (cx + 14, 4)], "fuel", 5)
    o += rect(cx + 34, 42, 12, 10, "m", 2)                                                           # inlet fitting
    o += flow([(cx + 62, 47), (cx + 48, 47), (cx + 38, 47)], "fuel", 5)
    # control sleeve + rack (rack runs in front of the sleeve)
    o += rect(cx - 16, 87, 32, 13, "m2", 2)
    for k in range(8):
        o += line(cx - 14 + k * 4, 89, cx - 14 + k * 4, 95, "o thin")
    o += faint(rect(cx - 40, 89, 92, 7, "w"), 0.85) + rect(cx - 40, 89, 92, 7, "o")
    for k in range(9):
        o += path("M%s 96 l2 2.4 l2 -2.4" % n(cx - 30 + k * 4), "o thin")
    o += arrow(cx + 28, 106, cx + 52, 106, both=True)
    # close-ups: delivery starts / spill ends injection
    o += panel(158, 14, 152, 150, 6)
    o += pump_stage(196, 66, False) + pump_stage(272, 50, True)
    o += flow([(228, 32), (238, 32)], "a", 5)
    return o


def nozzle_lower(cx, y0, s=1.0, fuel=True):
    """nozzle body + needle (section), from the holder face y0 down to the tip. returns (svg, tip_y)."""
    o = ""
    def T(ps):
        return [(cx + u * s, y0 + v * s) for u, v in ps]
    # cap nut and nozzle body
    for sg in (-1, 1):
        o += section(T([(sg * 8, -8), (sg * 12, -8), (sg * 12, 36), (sg * 9, 44), (sg * 8, 44)]), "w", 2.4, 45 * sg)
        o += section(T([(sg * 4.2, 0), (sg * 8, 0), (sg * 8, 44), (sg * 5, 56), (sg * 3.4, 62), (sg * 2.2, 64), (sg * 2.2, 54), (sg * 3, 44), (sg * 4.2, 30)]), "w", 2.0, -45 * sg)
    o += pg(T([(-2.2, 54), (2.2, 54), (2.2, 62), (0, 65), (-2.2, 62)]), "w")
    if fuel:
        o += pg(T([(-4.2, 22), (4.2, 22), (4.2, 28), (-4.2, 28)]), "beamf")                         # pressure chamber
        o += pg(T([(-4.2, 28), (4.2, 28), (3, 44), (2.2, 54), (-2.2, 54), (-3, 44)]), "beamf")
    o += pg(T([(-4, 0), (4, 0), (4, 22), (2.2, 26), (2, 50), (0, 56), (-2, 50), (-2.2, 26), (-4, 22)]), "m")   # needle
    return o, y0 + 64 * s


@part("marineaux.mxnozzle")
def _():
    o = shadow(60, 188, 30, 3) + shadow(272, 188, 26, 3)
    cx = 58
    # holder: top screw, spring chamber, push rod, inlet and deep fuel drilling
    o += rect(cx - 7, 8, 14, 10, "m", 2)
    for sg in (-1, 1):
        o += section([(cx + sg * 7, 18), (cx + sg * 12, 18), (cx + sg * 12, 118), (cx + sg * 7, 118)], "w", 2.8, 45 * sg)
    o += section([(cx - 12, 108), (cx + 12, 108), (cx + 12, 118), (cx - 12, 118)], "w", 2.8, 45)
    o += rect(cx - 7, 18, 14, 4, "m2")                                                                # adjusting shim
    o += spring_section(cx - 4.5, cx + 4.5, 22, 74, 1.9, 4.2)
    o += rect(cx - 6, 74, 12, 4, "m2") + rect(cx - 2.4, 78, 4.8, 30, "m")                              # seat + push rod
    o += rect(cx + 12, 34, 14, 10, "m", 2)                                                            # fuel inlet
    o += line(cx + 9.5, 39, cx + 9.5, 120, "fence").replace('class="fence"', 'class="fence" style="stroke-width:1.6"')
    o += line(cx + 12, 39, cx + 9.5, 39, "fence").replace('class="fence"', 'class="fence" style="stroke-width:1.6"')
    o += flow([(cx + 40, 39), (cx + 30, 39), (cx + 24, 39)], "fuel", 5)
    nz, tip = nozzle_lower(cx, 118, 1.02)
    o += nz
    o += '<path class="fence" style="stroke-width:1.6" d="M%s 118 L%s 146"/>' % (n(cx + 9.5), n(cx + 4))
    o += line(cx, 4, cx, tip + 4, "cl")
    # tip close-up: spray holes radiating from the sac, rounded inlets
    lx, ly, lr = 158, 112, 44
    o += lens(lx, ly, lr, cx, tip - 2)
    disc = _circ_pts(lx, ly, lr, 48)
    tipc = (lx, ly - 4)
    body = [(lx - 30, ly - 50), (lx + 30, ly - 50), (lx + 30, ly - 20), (lx + 22, ly + 2)] + \
           [(tipc[0] + 22 * math.cos(math.radians(a)), tipc[1] + 22 * math.sin(math.radians(a))) for a in range(20, 161, 10)] + \
           [(lx - 22, ly + 2), (lx - 30, ly - 20)]
    o += section(clip_convex(body, disc), "w", 3, 45)
    sac = [(tipc[0] + 9 * math.cos(math.radians(a)), tipc[1] + 9 * math.sin(math.radians(a))) for a in range(0, 181, 15)] + [(lx - 9, ly - 30), (lx + 9, ly - 30)]
    o += pg(clip_convex(sac, disc), "beamf") + path(P(clip_convex(sac, disc)), "o")
    o += pg(clip_convex([(lx - 9, ly - 60), (lx + 9, ly - 60), (lx + 9, ly - 30), (lx + 3, ly - 14), (lx - 3, ly - 14), (lx - 9, ly - 30)], disc), "m")
    for a in (35, 65, 90, 115, 145):
        t = math.radians(a)
        ux, uy = math.cos(t), math.sin(t)
        p0 = (tipc[0] + 7 * ux, tipc[1] + 7 * uy)
        p1 = (tipc[0] + 23 * ux, tipc[1] + 23 * uy)
        o += rbar(p0[0], p0[1], p1[0], p1[1], 3.4, "beamf")
        o += circ(p0[0], p0[1], 2.4, "beamf")
        sp = clip_convex([(p1[0], p1[1]), (p1[0] + 30 * math.cos(t - 0.16), p1[1] + 30 * math.sin(t - 0.16)),
                          (p1[0] + 30 * math.cos(t + 0.16), p1[1] + 30 * math.sin(t + 0.16))], disc)
        if len(sp) > 2:
            o += pg(sp, "beamf")
    o += lens_rim(lx, ly, lr)
    # electronically controlled injection valve (simplified)
    ex = 272
    o += rect(ex - 9, 10, 18, 9, "pcb", 2) + rect(ex - 5, 6, 3, 5, "cu") + rect(ex + 2, 6, 3, 5, "cu")   # connector
    for sg in (-1, 1):
        o += section([(ex + sg * 9, 19), (ex + sg * 15, 19), (ex + sg * 15, 118), (ex + sg * 9, 118)], "w", 2.8, 45 * sg)
    o += rect(ex - 9, 22, 6, 18, "cu") + rect(ex + 3, 22, 6, 18, "cu")                                 # solenoid coil
    o += rect(ex - 3, 20, 6, 22, "m2") + rect(ex - 8, 42, 16, 4, "m")                                  # core + armature
    o += circ(ex, 50, 2.6, "ball") + rect(ex - 9, 54, 18, 6, "beamf") + rect(ex - 9, 54, 18, 6, "o")   # control valve + chamber
    o += rect(ex - 2.4, 60, 4.8, 58, "m")
    o += spring_section(ex - 5, ex + 5, 64, 100, 1.7, 4)
    o += rect(ex + 15, 74, 12, 9, "m", 2)
    o += '<path class="fence" style="stroke-width:1.6" d="M%s 78.5 L%s 78.5 L%s 122"/>' % (n(ex + 15), n(ex + 12), n(ex + 12))
    nz2, tip2 = nozzle_lower(ex, 118, 1.02)
    o += nz2
    return o


def jacket_pipe(ps):
    """double-walled HP pipe along screen points: translucent jacket + inner high-pressure pipe."""
    d = smooth_d(ps)
    o = '<path class="tube1" style="stroke-width:12;opacity:.5" d="%s"/>' % d
    o += '<path class="tube2" style="stroke-width:10;opacity:.55" d="%s"/>' % d
    o += '<path class="pipe" style="stroke-width:3.6" d="%s"/>' % d
    o += '<path class="fence" style="stroke-width:1.1" d="%s"/>' % d
    return o


@part("marineaux.mxhpline")
def _():
    o = shadow(80, 192, 72, 4)
    # engine side (block + cylinder head) with pump and fuel valve
    o += rect(8, 56, 142, 132, "pt") + rect(8, 56, 142, 132, "o")                          # block side
    o += box(8, 150, 142, 8, 10, "pts2", "pt", "pts3")                                    # pump ledge
    o += box(76, 10, 74, 46, 14, "pt", "pt", "pts3")                                      # cylinder head
    for k in range(3):
        o += rect(84 + k * 22, 56, 8, 5, "m2", 1)                                         # head stud nuts
    o += box(18, 108, 34, 42, 12, "m2", "m", "m3")                                        # fuel injection pump
    o += box(26, 96, 18, 12, 8, "m2", "m", "m3")                                          # delivery valve holder
    o += rect(88, 46, 18, 12, "m", 2)                                                     # fuel valve inlet block on the head
    o += jacket_pipe([(35, 96), (35, 84), (44, 74), (64, 70), (86, 64), (97, 56)])
    o += rect(29, 88, 12, 9, "m2", 1.5) + rect(91, 51, 12, 9, "m2", 1.5)                  # end fittings
    # leak drain from the lower fitting to a leak detector
    o += '<path class="pipe" style="stroke-width:1.8" d="M29 92 L14 92 L14 168"/>'
    o += rect(8, 168, 13, 12, "m", 2) + circ(14.5, 174, 2.6, "sensor")
    o += flow([(14, 118), (14, 140), (14, 160)], "fuel", 4.5)
    # ---- fitting section: cone-head pipe pressed into the seat by the nut; jacket gap drains leaks
    px, py = 158, 10
    o += panel(px, py, 150, 88, 6)
    ay = py + 46
    body = [(px + 104, py + 14), (px + 146, py + 14), (px + 146, py + 80), (px + 104, py + 80), (px + 104, ay + 9), (px + 100, ay + 9),
            (px + 100, ay - 9), (px + 104, ay - 9)]
    o += section(body, "w", 3, 45)
    o += pg([(px + 100, ay - 9), (px + 116, ay - 3), (px + 146, ay - 3), (px + 146, ay + 3), (px + 116, ay + 3), (px + 100, ay + 9)], "beamf")
    for sg in (-1, 1):                                                                     # nut
        o += section([(px + 70, ay + sg * 10), (px + 104, ay + sg * 10), (px + 104, ay + sg * 22), (px + 70, ay + sg * 22)], "w", 3, -45)
    for sg in (-1, 1):                                                                     # HP pipe walls + cone head
        o += section([(px + 8, ay + sg * 3), (px + 92, ay + sg * 3), (px + 92, ay + sg * 9.5), (px + 8, ay + sg * 9.5)], "m", 2.2, 45 * sg)
        o += section([(px + 92, ay + sg * 3), (px + 112, ay + sg * 3), (px + 102, ay + sg * 10), (px + 92, ay + sg * 10)], "m", 2.2, 45 * sg)
    o += rect(px + 8, ay - 3, 104, 6, "beamf")
    for sg in (-1, 1):                                                                     # jacket tube (translucent) and gap
        o += faint(rect(px + 8, ay + (sg * 13 if sg > 0 else -16), 62, 3, "gl"), 0.9) + rect(px + 8, ay + (sg * 13 if sg > 0 else -16), 62, 3, "o")
    o += rect(px + 56, ay + 16, 5, 22, "void") + line(px + 56, ay + 16, px + 56, py + 84, "o") + line(px + 61, ay + 16, px + 61, py + 84, "o")
    o += flow([(px + 30, ay + 11.5), (px + 50, ay + 11.5), (px + 58.5, ay + 18), (px + 58.5, py + 84)], "fuel", 4.5)
    # ---- common rail: thick bar, central bore, side ports; cross-bore edge rounded
    qx, qy = 158, 104
    o += panel(qx, qy, 150, 88, 6)
    o += shaft(qx + 10, qy + 34, [(96, 11)], "w", "w2")
    o += line(qx + 12, qy + 34, qx + 106, qy + 34, "hid")
    for k in range(4):
        o += vcyl(qx + 24 + k * 22, qy + 14, 12, 5, 2.4, "w", "w2") + ell(qx + 24 + k * 22, qy + 14, 2, 1, "bg")
    lx, ly, lr = qx + 128, qy + 56, 19
    o += lens(lx, ly, lr, qx + 46, qy + 34)
    disc = _circ_pts(lx, ly, lr, 36)
    blk = [(lx - 30, ly - 30), (lx + 30, ly - 30), (lx + 30, ly + 30), (lx - 30, ly + 30)]
    o += section(clip_convex(blk, disc), "w", 2.6, 45)
    chan = [(lx - 30, ly + 3), (lx - 9, ly + 3)] + [(lx - 9 + 5 * math.sin(math.radians(a)), ly + 3 - 5 + 5 * math.cos(math.radians(a))) for a in range(0, 91, 15)] + \
           [(lx - 4, ly - 30), (lx + 4, ly - 30)] + [(lx + 9 - 5 * math.cos(math.radians(a)), ly - 2 + 5 * math.sin(math.radians(a))) for a in range(0, 91, 15)] + \
           [(lx + 30, ly + 3), (lx + 30, ly + 13), (lx - 30, ly + 13)]
    for poly_ in (chan,):
        cl = []
        for p in poly_:
            dx, dy = p[0] - lx, p[1] - ly
            dd = math.hypot(dx, dy)
            cl.append((lx + dx * min(1, (lr - 0.6) / dd), ly + dy * min(1, (lr - 0.6) / dd)) if dd > lr - 0.6 else p)
        o += pg(cl, "void") + pg(cl, "beamf") + path(P(cl), "o")
    o += lens_rim(lx, ly, lr)
    return o


@part("marineaux.mxscr")
def _():
    Wr, Hr = 100, 160
    win = [(14, 18), (86, 18), (86, 146), (14, 146)]
    layers = (26, 68, 110)

    def build(sc):
        cam = sc.cam
        BOX(sc, 0, 92, -6, Wr, 8, Hr + 6, "m")                                          # back wall
        BOX(sc, 0, 8, -6, 8, 84, Hr + 6, "m")                                           # left wall
        for z0 in layers:                                                               # catalyst layers (modules)
            BOX(sc, 8, 8, z0, 84, 84, 18, "gw")
        # front wall: cladding / insulation / inner plate, cut open
        hole = [(x, z, k) for k, (x, z) in enumerate(win)]
        for y0, t, mat in ((8, 2, "w"), (6, 4, "gw"), (2, 4, "gw"), (0, 2, "m")):
            sc.add(GE.prism(cam, (0, y0, 0), (0, -1, 0), [(0, -6, 0), (Wr, -6, 1), (Wr, Hr, 2), (0, Hr, 3)], t, mat, holes=[hole[::-1]]),
                   ((0, y0 - t, -6), (Wr, y0, Hr)), 0)
        BOX(sc, Wr - 8, 8, -6, 8, 84, Hr + 6, "m")                                      # right wall
        # inlet hood + pipe + mixing pipe (horizontal) with urea nozzle and mixer
        sc.add(GE.prism(cam, (Wr / 2, Wr / 2, Hr), (0, 0, 1), [(-50, -50, 0), (50, -50, 1), (50, 50, 2), (-50, 50, 3)], 26, "m",
                        scale=lambda t: 1 - 0.56 * t), ((0, 0, Hr), (Wr, Wr, Hr + 26)))
        CYL(sc, (Wr / 2, Wr / 2, Hr + 26), (0, 0, 1), 22, 26, "m", seg=28)
        CYL(sc, (-170, Wr / 2, Hr + 52 + 4), (1, 0, 0), 22, 198, "m", seg=28)
        CYL(sc, (-178, Wr / 2, Hr + 56), (1, 0, 0), 28, 8, "m", seg=28)                 # inlet flange
        CYL(sc, (-82, Wr / 2, Hr + 56), (1, 0, 0), 25, 28, "w", seg=28, bias=-0.1)        # mixer housing
        CYL(sc, (-128, Wr / 2 - 10, Hr + 92), (0.45, 0.25, -0.86), 4, 22, "m", seg=12)   # urea nozzle lance
        # outlet hood + pipe
        sc.add(GE.prism(cam, (Wr / 2, Wr / 2, -6), (0, 0, -1), [(-50, -50, 0), (50, -50, 1), (50, 50, 2), (-50, 50, 3)], 22, "m",
                        scale=lambda t: 1 - 0.58 * t), ((0, 0, -28), (Wr, Wr, -6)))
        CYL(sc, (Wr / 2, Wr / 2, -50), (1, 0, 0), 21, 130, "m", seg=28)
        CYL(sc, (Wr / 2 - 21, Wr / 2, -50), (1, 0, 0), 21, 21, "m", seg=28)
        # soot blowers above each layer, manhole, dp transmitter
        for z0 in layers:
            CYL(sc, (Wr, 30, z0 + 26), (1, 0, 0), 3.5, 16, "m", seg=12)
            CYL(sc, (Wr, 70, z0 + 26), (1, 0, 0), 3.5, 16, "m", seg=12)
        BOX(sc, Wr, 36, 150, 10, 26, 16, "w")

    def post(sc):
        cam = sc.cam
        o = ""
        # module grid on the catalyst tops and fronts (seen through the cut-out)
        winp = [cam.xy((x, 0, z)) for x, z in win]
        for z0 in layers:
            segs = []
            for k in range(1, 4):
                segs.append((cam.xy((8 + 21 * k, 8, z0 + 18)), cam.xy((8 + 21 * k, 92, z0 + 18))))
                segs.append((cam.xy((8, 8 + 21 * k, z0 + 18)), cam.xy((92, 8 + 21 * k, z0 + 18))))
                segs.append((cam.xy((8 + 21 * k, 8, z0)), cam.xy((8 + 21 * k, 8, z0 + 18))))
            o += lines_in(segs, winp, "o thin")
        # gas flow: in through the mixing pipe, down through the layers, out at the bottom
        a = cam.xy((-200, Wr / 2, Hr + 56))
        b = cam.xy((-150, Wr / 2, Hr + 56))
        o += flow([a, b], "gas", 7)
        for xx in (30, 70):
            p0, p1 = cam.xy((xx, 4, 140)), cam.xy((xx, 4, 100))
            o += flow([p0, p1], "gas", 6)
            p0, p1 = cam.xy((xx, 4, 60)), cam.xy((xx, 4, 24))
            o += flow([p0, p1], "gas", 6)
        c0, c1 = cam.xy((150, Wr / 2, -50)), cam.xy((200, Wr / 2, -50))
        o += flow([c0, c1], "grey", 7)
        # urea spray from the lance tip
        t = cam.xy((-118, Wr / 2 - 4, Hr + 73))
        for da in (-0.35, 0, 0.35):
            ang = math.radians(60) + da
            o += '<path class="fo" style="stroke-dasharray:2 2" d="M%s %sL%s %s"/>' % (n(t[0]), n(t[1]), n(t[0] + 16 * math.cos(ang)), n(t[1] + 16 * math.sin(ang)))
        o += '<path class="pipe" style="stroke-width:1.6" d="M%s %s L%s %s"/>' % (n(t[0] - 10), n(t[1] - 26), n(t[0] - 30), n(t[1] - 26))
        # mixer vanes (window in the mixer housing)
        mc = cam.xy((-68, Wr / 2 - 24, Hr + 56))
        o += ell(mc[0], mc[1], 6, 11, "gl")
        for k in range(5):
            o += line(mc[0] - 4, mc[1] - 8 + k * 4, mc[0] + 4, mc[1] - 6 + k * 4, "o thin")
        # instruments
        for p in ((-150, Wr / 2, Hr + 78), (120, Wr / 2, -28)):
            q = cam.xy(p)
            o += circ(q[0], q[1], 4, "m") + circ(q[0], q[1], 2.6, "void") + line(q[0], q[1], q[0] + 1.6, q[1] - 1.6, "o")
        # manhole on the right wall
        mh = circ3(cam, (Wr + 0.5, 50, 46), (1, 0, 0), 13, 24)
        o += pg(mh, "m2")
        return o

    out = fit_scene(build, -28, 22, area=(10, 8, 310, 186), sh_ry=10, post=post)
    # catalyst block end face (square cells)
    px, py, s_ = 14, 132, 54
    out += panel(px, py, s_, s_, 4)
    out += rect(px + 5, py + 5, s_ - 10, s_ - 10, "gw")
    for k in range(1, 11):
        v = px + 5 + (s_ - 10) * k / 11
        out += line(v, py + 5, v, py + s_ - 5, "o thin") + line(px + 5, py + 5 + (s_ - 10) * k / 11, px + s_ - 5, py + 5 + (s_ - 10) * k / 11, "o thin")
    return out


@part("marineaux.mxscrub")
def _():
    o = shadow(64, 186, 46, 4) + shadow(204, 186, 92, 4)
    # ---------------- outside view (left)
    cam = GE.Cam(66, 180, 0, 12, 1.0)
    R, Ht = 24, 146
    o += GE.cyl(cam, (-60, 0, 26), (1, 0, 0), 11, 34, "w", seg=24)                    # gas inlet
    o += GE.cyl(cam, (-64, 0, 26), (1, 0, 0), 14, 4, "w", seg=24)
    o += GE.cyl(cam, (0, 0, -4), (0, 0, 1), R * 0.8, 6, "w", seg=40, scale=lambda t: 0.8 + 0.2 * t)
    o += GE.cyl(cam, (0, 0, 2), (0, 0, 1), R, Ht, "w", seg=40)
    o += GE.cyl(cam, (0, 0, 2 + Ht), (0, 0, 1), R, 14, "w", seg=40, scale=lambda t: 1 - 0.55 * t)
    o += GE.cyl(cam, (0, 0, 16 + Ht), (0, 0, 1), R * 0.45, 14, "w", seg=24)
    for z in (40, 78, 116):                                                             # flange seams
        a = circ3(cam, (0, 0, z), (0, 0, 1), R + 0.6, 24, -90, 90)
        o += path(P(a, False), "o")
    for z in (2, 2 + Ht):
        o += path(P(circ3(cam, (0, 0, z), (0, 0, 1), R + 1.4, 24, -90, 90), False), "o")
    # ladder + platform
    lx0, lx1 = cam.xy((R + 3, -6, 0))[0], cam.xy((R + 9, -6, 0))[0]
    ytop, ybot = cam.xy((0, 0, Ht))[1], cam.xy((0, 0, 4))[1]
    o += line(lx0, ytop, lx0, ybot, "o") + line(lx1, ytop, lx1, ybot, "o")
    y = ybot - 4
    while y > ytop:
        o += line(lx0, y, lx1, y, "o thin")
        y -= 5
    o += person(112, ybot + 4, h=25.5)
    # ---------------- section (centre)
    cx, top, bot = 176, 22, 176
    r = 26
    o += pg([(cx - r, bot - 18), (cx + r, bot - 18), (cx + r, bot), (cx - r, bot)], "fl")              # sump water
    for sg in (-1, 1):
        o += section([(cx + sg * r, top + 18), (cx + sg * (r + 3.4), top + 18), (cx + sg * (r + 3.4), bot), (cx + sg * r, bot)], "w", 2.6, 45 * sg)
        o += section([(cx + sg * r, top + 18), (cx + sg * (r + 3.4), top + 18), (cx + sg * (r * 0.45 + 3.4), top + 4), (cx + sg * r * 0.45, top + 4)], "w", 2.6, 45 * sg)
        o += section([(cx + sg * r * 0.45, top + 4), (cx + sg * (r * 0.45 + 3.4), top + 4), (cx + sg * (r * 0.45 + 3.4), top - 12), (cx + sg * r * 0.45, top - 12)], "w", 2.6, 45 * sg)
    o += section([(cx - r - 3.4, bot), (cx + r + 3.4, bot), (cx + r + 3.4, bot + 3.4), (cx - r - 3.4, bot + 3.4)], "w", 2.6, 45)
    # inlet section (corrosion-resistant alloy) + inlet duct from the left
    o += section([(cx - r - 3.4, bot - 44), (cx - r, bot - 44), (cx - r, bot - 10), (cx - r - 3.4, bot - 10)], "gw", 2.6, 45)
    o += rect(cx - r - 26, bot - 40, 23, 4, "gw") + rect(cx - r - 26, bot - 18, 23, 4, "gw")
    o += rect(cx - r - 26, bot - 36, 26, 18, "void")
    # demister (wave plates)
    for k in range(3):
        o += path(P(zigzag(cx - r + 1, top + 24 + k * 4, cx + r - 1, top + 24 + k * 4, 1.6, 4.2), False), "o")
    # packing layer
    o += rect(cx - r, 104, 2 * r, 16, "void") + rect(cx - r, 104, 2 * r, 16, "o")
    o += lines_in([((cx - r + k * 6, 104), (cx - r + k * 6 + 16, 120)) for k in range(-3, 10)] +
                  [((cx - r + k * 6 + 16, 104), (cx - r + k * 6, 120)) for k in range(-3, 10)],
                  [(cx - r, 104), (cx + r, 104), (cx + r, 120), (cx - r, 120)], "o thin")
    # spray headers with downward sprays
    for yh in (56, 80, 128):
        o += rect(cx - r, yh - 2, 2 * r + 30, 4, "m")
        for k in range(4):
            nx = cx - r + 8 + k * 12
            o += rect(nx - 1.4, yh + 2, 2.8, 3, "m")
            o += spray_cone(nx, yh + 5, 90, 44, 11)
    # gas up (grey), water down (light blue)
    o += flow([(cx - r - 30, bot - 27), (cx - 12, bot - 27), (cx - 4, bot - 40), (cx - 4, 140)], "grey", 5.5)
    o += flow([(cx + 10, 100), (cx + 10, 88)], "grey", 5.5) + flow([(cx - 8, 76), (cx - 8, 62)], "grey", 5.5)
    o += flow([(cx, top + 18), (cx, top - 14)], "grey", 6)
    o += flow([(cx + 18, 136), (cx + 18, 150)], "water", 5) + flow([(cx - 18, 88), (cx - 18, 100)], "water", 5)
    # outside: circulation pump, risers, drain, instruments
    px, py = 268, 168
    o += '<path class="pipe" d="M%s %s L%s %s L%s %s"/>' % (n(cx + r + 3), n(bot - 6), n(px - 12), n(bot - 6), n(px - 12), n(py))
    o += circ(px, py + 4, 9, "w") + rect(px + 8, py - 2, 22, 12, "dk", 2)                                # pump + motor
    o += '<path class="pipe" d="M%s %s L%s %s L%s %s"/>' % (n(px), n(py - 5), n(px), n(56), n(cx + r + 30), n(56))
    for yh in (80, 128):
        o += '<path class="pipe" d="M%s %s L%s %s"/>' % (n(px), n(yh), n(cx + r + 30), n(yh))
    o += flow([(px + 6, 150), (px + 6, 120)], "water", 5)
    o += rect(px - 7, 100, 14, 10, "m", 2) + circ(px, 105, 2.6, "sensor")                            # flow / pH meter
    o += '<path class="pipe" style="stroke-width:3" d="M%s %s L%s %s"/>' % (n(cx), n(bot + 3), n(cx), n(196))   # drain
    o += rect(cx + 14, top - 10, 14, 10, "m", 2) + line(cx + 14, top - 5, cx + 6, top - 5, "o")          # gas analyser probe
    return o
