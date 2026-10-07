"""Part drawings for the data-centre power sections: emergency generator sets (genset) and the
electrical / control equipment around them (dcpower). Same studio-lit metal style as il_parts.py:
viewBox 0 0 320 200, theme classes only, no text (labels are hidden in every part view anyway).

Material notes
- The page puts the part's material class (mt-fe / mt-al / mt-cu / ...) on the <svg>; w/w2/w3 and the
  shaded solids (ws1..4) follow it, so "w" is used for the part's own main material only.
- Fixed tones used for the other materials, whatever the root class:
    steel (when the root is not steel) -> "m" family     cast iron -> fe() group
    aluminium -> "alu"                                   copper / brass -> "cu"
    resin, moulded parts, cable sheaths -> "gw"          epoxy castings -> "sand" (2D) / "t" darker shade
    ceramic (alumina) -> "pt"                            stainless -> "m" (bluish light silver)
    nickel alloy / heat-resisting steel -> "t"           insulation (glass / rock wool) -> "ins" + dots
    fuel -> "resin" (pale amber)                         glass -> "gl"
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
    """cast-iron colouring for 2D w/w2/w3 shapes or shaded solids."""
    return '<g class="ilu mt-fe">%s</g>' % s


def alg(s):
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


def srect(x, y, w, h, c="w", step=3.2, ang=45):
    """hatched section rectangle."""
    return section([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], c, step, ang)


def dots(x, y, w, h, step=3.2, r=0.55, cls="grain"):
    """deterministic stipple inside a rectangle (insulation wool, perforation)."""
    o = ""
    j = 0
    yy = y + step * 0.5
    while yy < y + h - 0.3:
        xx = x + step * (0.3 if j % 2 else 0.8)
        while xx < x + w - 0.3:
            o += '<circle class="%s" cx="%s" cy="%s" r="%s"/>' % (cls, n(xx), n(yy), n(r))
            xx += step
        yy += step * 0.8
        j += 1
    return o


def wool(x, y, w, h, step=3.0):
    """ochre insulation band (glass / rock wool) with stipple."""
    return rect(x, y, w, h, "ins") + dots(x, y, w, h, step, 0.5)


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


def scene_at(fn, az, el, ox, oy, k, post=None):
    """render a scene with a fixed camera (no fitting)."""
    sc = Scene(ox, oy, az, el, k)
    sc.k = k
    fn(sc)
    body, _ = sc.render(shadow_=False)
    return body + (post(sc) if post else "")


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
    "warm": ("spark", "stroke-width:2.2", "clamph"),
    "grey": ("done", "stroke-width:2", "d"),
    "fuel": ("fence", "stroke-width:2", "bolt"),
    "oil": ("chipc", "stroke-width:1.8", "t"),
    "a": ("a", "", "af"),
    "el": ("mfo", "stroke-width:2", "af"),
}


def flow(ps, kind="air", hs=6.5, smooth=True, w=None, both=False):
    """coloured flow arrow along screen points ps (head at the last point)."""
    lc, st, hc = FLOW[kind]
    if w:
        st = "stroke-width:%s" % n(w) + (";" + st.split(";", 1)[1] if ";" in st else "")
    x1, y1 = ps[-2]
    x2, y2 = ps[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    q = list(ps[:-1]) + [(x2 - hs * 0.55 * math.cos(ang), y2 - hs * 0.55 * math.sin(ang))]
    s = ""
    if both:
        xa, ya = ps[1]
        xb, yb = ps[0]
        a2 = math.atan2(yb - ya, xb - xa)
        q[0] = (xb - hs * 0.55 * math.cos(a2), yb - hs * 0.55 * math.sin(a2))
        s += head(xb, yb, a2, hs).replace('class="af"', 'class="%s"' % hc)
    d = smooth_d(q) if smooth and len(q) > 2 else P(q, False)
    s = '<path class="%s" style="fill:none;%s" d="%s"/>' % (lc, st, d) + s
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


def clipc(cid, cx, cy, r, body):
    """clip body to a circle (for magnifier insets)."""
    return ('<clipPath id="%s"><circle cx="%s" cy="%s" r="%s"/></clipPath><g clip-path="url(#%s)">%s</g>'
            % (cid, n(cx), n(cy), n(r), cid, body))


def clipr(cid, x, y, w, h, body, r=5):
    return ('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s" rx="%s"/></clipPath><g clip-path="url(#%s)">%s</g>'
            % (cid, n(x), n(y), n(w), n(h), n(r), cid, body))


def panel(x, y, w, h, r=6):
    return rect(x, y, w, h, "void", r) + rect(x, y, w, h, "o", r)


def leader(x0, y0, x1, y1):
    return line(x0, y0, x1, y1, "o thin dash") + circ(x0, y0, 2.2, "o")


def bolt_hex(cx, cy, r, c="w2"):
    ps = [(cx + r * math.cos(math.radians(30 + 60 * k)), cy + r * 0.9 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    return pg(ps, c)


def vstrips(x, y, w, h, cnt, cls="gr"):
    """thin vertical lines across a rectangle."""
    d = ""
    for k in range(1, cnt):
        xx = x + w * k / cnt
        d += "M%s %sL%s %s" % (n(xx), n(y), n(xx), n(y + h))
    return path(d, cls)


def hstrips(x, y, w, h, cnt, cls="gr"):
    d = ""
    for k in range(1, cnt):
        yy = y + h * k / cnt
        d += "M%s %sL%s %s" % (n(x), n(yy), n(x + w), n(yy))
    return path(d, cls)


def sine(x0, x1, y, amp, cycles, phase=0.0, seg=60):
    ps = [(x0 + (x1 - x0) * k / seg, y - amp * math.sin(phase + 2 * math.pi * cycles * k / seg)) for k in range(seg + 1)]
    return P(ps, False)


def gsym(cx, cy, r=7):
    """generator symbol: circle with a sine wave inside (no lettering)."""
    return circ(cx, cy, r, "void") + circ(cx, cy, r, "o") + path(sine(cx - r * 0.6, cx + r * 0.6, cy, r * 0.32, 1), "o")


def cbsym(cx, cy, s=4.2, c="m"):
    """circuit-breaker symbol for one-line diagrams: small square."""
    return rect(cx - s, cy - s, 2 * s, 2 * s, c)


def lamp(cx, cy, r, c="clamph"):
    return circ(cx, cy, r + 1, "m2") + circ(cx, cy, r, c)


def meter(cx, cy, r, ang=-40):
    a = math.radians(ang - 90)
    s = circ(cx, cy, r, "m2") + circ(cx, cy, r * 0.78, "m")
    s += path("M%s %s A%s %s 0 0 1 %s %s" % (n(cx - r * 0.55), n(cy + r * 0.1), n(r * 0.6), n(r * 0.6), n(cx + r * 0.55), n(cy + r * 0.1)), "o thin")
    return s + line(cx, cy + r * 0.25, cx + r * 0.62 * math.cos(a), cy + r * 0.25 + r * 0.62 * math.sin(a), "needle")


def louvre(x, y, w, h, cnt, c="m3"):
    o = rect(x, y, w, h, "m2", 1)
    for k in range(cnt):
        yy = y + 1 + (h - 2) * (k + 0.5) / cnt
        o += path("M%s %s L%s %s" % (n(x + 1.5), n(yy), n(x + w - 1.5), n(yy)), "o")
        o += path("M%s %s L%s %s" % (n(x + 1.5), n(yy + 0.9), n(x + w - 1.5), n(yy + 0.9)), "o thin")
    return o


# =====================================================================================
# genset: data-centre generator sets
# =====================================================================================
@part("genset.gsbase")
def _():
    L = 600
    pads = [(110, "e"), (290, "e"), (420, "g"), (520, "g")]

    def frame(sc, L=600, Wd=124, H=40, lugs=True, padz=True):
        fr = [(0, 0), (18, 0), (18, 5), (5, 5), (5, H - 5), (18, H - 5), (18, H), (0, H)]
        bk = [(Wd, 0), (Wd, H), (Wd - 18, H), (Wd - 18, H - 5), (Wd - 5, H - 5), (Wd - 5, 5), (Wd - 18, 5), (Wd - 18, 0)]
        X(sc, 0, L, bk, "w")
        for xc in (8, 120, 240, 360, 480, L - 22):                     # cross members (I-section)
            X(sc, xc, 14, [(18, 8), (Wd - 18, 8), (Wd - 18, H - 8), (18, H - 8)], "w", bias=0.5)
        X(sc, 0, L, fr, "w")
        if padz:
            for xp, kind in pads:
                for y0 in (1, Wd - 17):
                    BOX(sc, xp, y0, H, 46 if kind == "e" else 40, 16, 4, "alu")
        if lugs:
            lug = [(0, 10), (26, 10)] + [(13 + 13 * math.cos(math.radians(a)), 46 + 13 * math.sin(math.radians(a))) for a in range(0, 181, 20)]
            hole = [(13 + 5.5 * math.cos(math.radians(a)), 46 + 5.5 * math.sin(math.radians(a)), 0) for a in range(0, 360, 30)][::-1]
            for xo in (16, L - 42):
                Y(sc, Wd + 3, 3, [(xo + u, v) for u, v in lug], "w", holes=[[(xo + u, v, f) for u, v, f in hole]])
                Y(sc, 0, 3, [(xo + u, v) for u, v in lug], "w", holes=[[(xo + u, v, f) for u, v, f in hole]])

    def post(sc):
        cam = sc.cam
        o = ""
        for xp, kind in pads:                                           # bolt holes in the machined pads
            w_ = 46 if kind == "e" else 40
            for y0 in (1, 107):
                for dx in (9, w_ - 9):
                    o += hole3(cam, (xp + dx, y0 + 8, 44.05), (0, 0, 1), 3.2)
        a = cam.xy((110 + 23, 9, 44.2))
        b = cam.xy((520 + 20, 9, 44.2))
        o += '<path class="laserl" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        for xs in (200, 232, 380):                                      # cable / pipe pass-through holes in the web
            ps = circ3(cam, (xs, -0.1, 20), (0, -1, 0), 7, 18)
            o += pg(ps, "bg")
        return o

    out = fit_scene(frame, -21, 30, area=(10, 40, 310, 176), sh_ry=12, post=post)

    # sub-base tank variant (small, top right)
    def sub(sc):
        frame(sc, 600, 124, 40, lugs=False, padz=False)
        BOX(sc, 30, 14, -70, 540, 96, 70, "w", bias=1)                  # tank slung under the frame
        CYL(sc, (80, 60, 40), (0, 0, 1), 9, 14, "m", seg=20)            # fill neck
        CYL(sc, (80, 60, 54), (0, 0, 1), 12, 5, "m2", seg=20)
        CYL(sc, (540, 70, 40), (0, 0, 1), 4, 70, "m", seg=14)           # vent pipe
        CYL(sc, (540, 70, 110), (0, 0, 1), 9, 8, "m2", seg=16)

    o2 = panel(192, 4, 122, 66, 6)
    o2 += shadow(252, 58, 50, 4) + scene_at(sub, -21, 30, 205, 30, 0.16)
    out += o2

    # section through a mounting pad (bottom left lens)
    cx, cy, r = 46, 160, 32
    body = srect(cx - 34, cy + 2, 68, 9, "w2", 3)                     # flange plate of the beam
    body += srect(cx - 15, cy - 6, 30, 8, "w", 3)                      # raised pad, welded
    body += path("M%s %s l4 0 l-4 -4 Z M%s %s l-4 0 l4 -4 Z" % (n(cx - 15), n(cy + 2), n(cx + 15), n(cy + 2)), "d")
    body += line(cx - 15, cy - 6, cx + 15, cy - 6, "done")              # machined face
    body += rect(cx - 6, cy - 6, 3.4, 17, "bg") + rect(cx + 3, cy - 6, 3.4, 17, "bg")   # tapped holes
    body += '<path class="laserl" d="M%s %sL%s %s"/>' % (n(cx - 28), n(cy - 6), n(cx + 28), n(cy - 6))
    out += lens(cx, cy, r) + clipc("pw-gsb-l", cx, cy, r - 1, body) + lens_rim(cx, cy, r)
    return out


def vbank(side, D=78.0, half=24.0):
    """deck centre, cylinder axis and across-bank vector for a 60-degree V (side -1 = left / front bank)."""
    a = math.radians(30)
    d = (side * math.sin(a), math.cos(a))
    e = (d[1], -d[0]) if side < 0 else (-d[1], d[0])
    C = (d[0] * D, d[1] * D)
    return C, d, e


def bank_rect(C, d, e, u0, u1, v0, v1):
    return [(C[0] + u * e[0] + v * d[0], C[1] + u * e[1] + v * d[1]) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]


def v_engine(sc, L=300, ncyl=8, pitch=36, x0=8, turbos=True, fly=True, detail=True):
    """V-type high-speed diesel: crank axis along x at y=0,z=0. Root material = cast iron (w)."""
    BOX(sc, 12, -36, -66, L - 24, 72, 26, "w")                                  # oil pan
    BOX(sc, 0, -52, -40, L, 104, 60, "w")                                       # crankcase
    up = [(-52, 20), (-60, 55), (-18, 79), (0, 54), (18, 79), (60, 55), (52, 20)]
    X(sc, 0, L, up, "w")                                                        # V block
    CYL(sc, (0, 0, 76), (1, 0, 0), 9, L, "t", seg=18, bias=0.3)                 # exhaust manifold in the V
    for side in (-1, 1):
        C, d, e = vbank(side)
        for i in range(ncyl):
            xa = x0 + i * pitch
            X(sc, xa, pitch - 6, bank_rect(C, d, e, -23, 23, 0, 19), "w")         # cylinder head
            X(sc, xa + 3, pitch - 12, bank_rect(C, d, e, -18, 18, 19, 27), "m")   # rocker cover
    if detail:
        for side in (-1, 1):
            yy = side * 66
            CYL(sc, (4, yy, 44), (1, 0, 0), 7, L - 8, "alu", seg=16)               # charge air pipe (aluminium)
        for i in range(ncyl):
            Y(sc, -52, 2, [(x0 + 6 + i * pitch, -30), (x0 + pitch - 12 + i * pitch, -30), (x0 + pitch - 12 + i * pitch, 2), (x0 + 6 + i * pitch, 2)], "m", bias=-0.2)
    if fly:
        CYL(sc, (-14, 0, -6), (1, 0, 0), 74, 14, "m", seg=40)                   # flywheel housing
        CYL(sc, (-20, 0, -6), (1, 0, 0), 30, 6, "m", seg=28)                    # flywheel / coupling spigot
    if turbos:
        X(sc, L, 14, [(-52, -40), (52, -40), (52, 20), (60, 55), (-60, 55), (-52, 20)], "w")   # gear case, free end
        BOX(sc, L + 6, -14, 56, 40, 28, 40, "alu")                               # charge air cooler
        for yy in (-32, 32):
            CYL(sc, (L + 2, yy, 84), (1, 0, 0), 15, 13, "t", seg=26)             # turbine casing (heat resisting)
            CYL(sc, (L + 15, yy, 84), (1, 0, 0), 8, 8, "m", seg=16)              # bearing housing
            CYL(sc, (L + 23, yy, 84), (1, 0, 0), 17, 15, "alu", seg=26)          # compressor casing
            CYL(sc, (L + 8, yy, 96), (0, 0, 1), 7, 14, "t", seg=16)              # gas outlet
        for yy, r in ((-26, 14), (24, 11)):
            CYL(sc, (L + 14, yy, -26), (1, 0, 0), r, 22, "w", seg=24)            # water / oil pumps
    if detail:
        for xf in (58, 80, 102):
            CYL(sc, (xf, -62, -34), (0, 0, 1), 8.5, 40, "dk", seg=20)            # filters
            BOX(sc, xf - 9, -61, 6, 18, 9, 7, "w")
        CYL(sc, (2, -36, -54), (1, 0, 0), 11, 40, "dk", seg=20)                  # starter motor
        for xm in (40, L - 60):
            BOX(sc, xm, -64, -46, 26, 12, 8, "w")                                # mounting feet
            BOX(sc, xm, 52, -46, 26, 12, 8, "w")


@part("genset.gsengine")
def _():
    def build(sc):
        v_engine(sc)
        RAW(sc, lambda s_: person(*s_.P((-120, -40, -70)), h=90 * s_.k * s_.cam.ce), ((-130, -46, -70), (-110, -34, 20)))

    def post(sc):
        cam = sc.cam
        o = ""
        for k in range(12):                                                     # flywheel housing bolt circle
            a = 2 * math.pi * k / 12
            o += hole3(cam, (-14.2, 64 * math.cos(a), -6 + 64 * math.sin(a)), (-1, 0, 0), 2.6, "bg", 10)
        for k in range(8):
            a = 2 * math.pi * k / 8 + 0.2
            o += hole3(cam, (-20.2, 20 * math.cos(a), -6 + 20 * math.sin(a)), (-1, 0, 0), 2.2, "bg", 10)
        o += hole3(cam, (-20.2, 0, -6), (-1, 0, 0), 7, "m3", 16)
        # wiring harness (resin sheath) along the front bank
        ps = [cam.xy((20 + 36 * i, -57, 26)) for i in range(8)]
        o += '<path class="o" style="stroke:var(--il-gw);stroke-width:2.4;fill:none" d="%s"/>' % smooth_d(ps)
        o += '<path class="o thin" style="fill:none" d="%s"/>' % smooth_d(ps)
        return o

    out = fit_scene(build, 24, 22, area=(14, 44, 312, 192), sh_ry=11, post=post)

    # inset: block upside down, crankshaft lowered into the main bearing saddles
    x0, y0, w, h = 8, 6, 98, 62
    o = panel(x0, y0, w, h, 6)
    bx, by = x0 + 10, y0 + 36
    o += fe(rect(bx, by, 78, 20, "w"))                                          # inverted block
    for k in range(5):
        sx = bx + 4 + k * 17.5
        o += fe(rect(sx, by - 6, 10, 8, "w2"))                                  # bulkhead / saddle
        o += path("M%s %s a5 4 0 0 0 10 0" % (n(sx), n(by - 6)), "bg")
    o += rect(bx - 2, by + 20, 82, 4, "m2")                                     # turning stand
    cy_ = y0 + 20
    o += rect(bx + 2, cy_ - 2, 74, 4, "w") + path("M%s %s" % (n(bx), n(cy_)), "o")
    for k in range(4):                                                          # throws
        tx = bx + 10 + k * 17.5
        o += rect(tx, cy_ - 5 + (4 if k % 2 else -2), 7, 9, "w2")
    o += path("M%s %s L%s %s L%s %s M%s %s L%s %s" % (n(bx + 20), n(cy_ - 2), n(bx + 39), n(y0 + 6), n(bx + 58), n(cy_ - 2),
                                                      n(bx + 39), n(y0 + 6), n(bx + 39), n(y0 + 2)), "o")
    o += flow([(x0 + 92, y0 + 10), (x0 + 92, y0 + 28)], "grey", 5)
    out += o
    return out


class _TCam:
    """camera wrapper placing a sub-assembly at an offset, optionally mirrored in x (x' = mx - x)."""

    def __init__(self, cam, t, mirror=False):
        self.c, self.t, self.m = cam, t, mirror
        self.D = (-cam.D[0], cam.D[1], cam.D[2]) if mirror else cam.D

    def _w(self, p):
        return ((self.t[0] - p[0]) if self.m else (p[0] + self.t[0]), p[1] + self.t[1], p[2] + self.t[2])

    def P(self, p):
        return self.c.P(self._w(p))

    def xy(self, p):
        return self.c.xy(self._w(p))


class TScene:
    """scene proxy: geometry built in local coordinates lands at offset t (mirrored in x if asked)."""

    def __init__(self, sc, t, mirror=False, wrap=None):
        self.sc, self.cam, self.k = sc, _TCam(sc.cam, t, mirror), getattr(sc, "k", 1.0)
        self.wrap = wrap

    def add(self, svg, bb, bias=0.0, z=0):
        a, b = self.cam._w(bb[0]), self.cam._w(bb[1])
        if self.wrap and not callable(svg):
            svg = self.wrap(svg)
        self.sc.add(svg, (tuple(min(a[i], b[i]) for i in range(3)), tuple(max(a[i], b[i]) for i in range(3))), bias, z)

    def P(self, p):
        return self.cam.xy(p)


def vcoil(cx, ytop, ybot, r, turns=4):
    """vertical helical spring (side view) between ytop and ybot."""
    pitch = (ybot - ytop) / turns
    back, front = "", ""
    for i in range(turns):
        ya = ytop + i * pitch
        back += "M%s %s Q%s %s %s %s " % (n(cx + r), n(ya + pitch * 0.5), n(cx), n(ya + pitch * 0.25), n(cx - r), n(ya))
        front += "M%s %s Q%s %s %s %s " % (n(cx - r), n(ya), n(cx), n(ya + pitch * 0.75), n(cx + r), n(ya + pitch * 0.5))
        front += "M%s %s Q%s %s %s %s " % (n(cx + r), n(ya + pitch * 0.5), n(cx), n(ya + pitch * 1.25), n(cx - r), n(ya + pitch))
    return (path(back, "o thin") + '<path class="wire2" style="stroke-width:2.2" d="%s"/>' % front + path(front, "o thin"))


def isolator(cx, ytop, ybot, w=12):
    """spring vibration isolator: two plates and a coil."""
    h = ybot - ytop
    return (vcoil(cx, ytop + 2.2, ybot - 2.2, w * 0.32, 3) + rect(cx - w / 2, ytop, w, 2.4, "m2") + rect(cx - w / 2 - 1.5, ybot - 2.4, w + 3, 2.4, "m2"))


def genset_side(sc, rad=True, gen=True, cut=True, Lb=620):
    """generator set on its common base: radiator (x 14..70) - engine (100..414) - generator (430..606).
    Crank / rotor axis at y=70, z=120. Root material = steel."""
    # common base frame on spring isolators (isolators drawn as overlay)
    fr = [(0, 20), (18, 20), (18, 25), (5, 25), (5, 35), (18, 35), (18, 40), (0, 40)]
    X(sc, 0, Lb, [(140 - y, z) for y, z in fr], "w")
    for xc in (60, 230, 400, 520):
        X(sc, xc, 12, [(18, 24), (122, 24), (122, 36), (18, 36)], "w", bias=0.5)
    X(sc, 0, Lb, fr, "w")
    # engine (mirrored: output end toward +x), on pedestals
    te = TScene(sc, (400, 70, 120), mirror=True, wrap=fe)
    for xm in (110, 330):
        BOX(sc, xm, 4, 40, 28, 14, 34, "w")
        BOX(sc, xm, 122, 40, 28, 14, 34, "w")
    fe_eng = []
    v_engine(te, L=300, turbos=False, detail=True)
    # turbochargers + charge air cooler on top at the free end
    BOX(sc, 110, 52, 196, 46, 36, 30, "alu")
    for yy in (40, 100):
        CYL(sc, (106, yy, 238), (1, 0, 0), 15, 14, "t", seg=24)
        CYL(sc, (120, yy, 238), (1, 0, 0), 8, 8, "m", seg=14)
        CYL(sc, (128, yy, 238), (1, 0, 0), 16, 15, "alu", seg=24)
    # free end: fan drive bracket + fan + radiator
    if rad:
        BOX(sc, 76, 54, 120, 10, 32, 36, "w")                              # fan drive bracket
        CYL(sc, (66, 70, 150), (1, 0, 0), 6, 20, "m", seg=16)              # fan shaft
        RING(sc, (44, 70, 150), (1, 0, 0), 82, 76, 14, "w", seg=40)        # shroud ring
        CYL(sc, (60, 70, 150), (1, 0, 0), 12, 8, "alu", seg=18)            # fan hub
        BOX(sc, 14, 0, 50, 24, 140, 190, "w")                              # radiator frame + core
        BOX(sc, 8, 4, 40, 36, 10, 12, "w")                                  # feet
        BOX(sc, 8, 126, 40, 36, 10, 12, "w")
    if gen:
        CYL(sc, (414, 70, 120), (1, 0, 0), 66, 16, "w", seg=40)            # adaptor (coupling housing)
        CYL(sc, (430, 70, 120), (1, 0, 0), 74, 160, "w", seg=48)           # generator frame
        CYL(sc, (590, 70, 120), (1, 0, 0), 40, 12, "w", seg=32)            # NDE end bracket + bearing
        CYL(sc, (602, 70, 120), (1, 0, 0), 18, 8, "m", seg=20)
        BOX(sc, 466, 26, 192, 72, 88, 40, "w")                             # terminal box
        for xg in (444, 556):
            BOX(sc, xg, 2, 40, 30, 22, 26, "w")                             # feet
            BOX(sc, xg, 116, 40, 30, 22, 26, "w")


@part("genset.gsassy")
def _():
    def build(sc):
        genset_side(sc)

    def post(sc):
        cam = sc.cam
        o = ""
        # radiator core face (front side of the radiator box is the y=0 face) -> fins on the end face x=14
        a, b, c, d = cam.xy((14, 8, 58)), cam.xy((14, 132, 58)), cam.xy((14, 132, 232)), cam.xy((14, 8, 232))
        o += pg([a, b, c, d], "cu")
        seg = ""
        for k in range(1, 18):
            t = k / 18
            p0 = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            p1 = (d[0] + (c[0] - d[0]) * t, d[1] + (c[1] - d[1]) * t)
            seg += "M%s %sL%s %s" % (n(p0[0]), n(p0[1]), n(p1[0]), n(p1[1]))
        o += path(seg, "gr")
        # fan blades seen through the shroud
        for k in range(6):
            t = math.radians(k * 60 + 15)
            p0 = cam.xy((52, 70 + 12 * math.cos(t), 150 + 12 * math.sin(t)))
            p1 = cam.xy((52, 70 + 72 * math.cos(t + 0.25), 150 + 72 * math.sin(t + 0.25)))
            p2 = cam.xy((52, 70 + 72 * math.cos(t - 0.15), 150 + 72 * math.sin(t - 0.15)))
            o += pg([p0, p1, p2], "alu")
        # coupling cut-away: flywheel, flexible disc pack bolted to its rim, generator hub
        def R(x0_, z0_, x1_, z1_, c, y_=4):
            a_, b_ = cam.xy((x0_, y_, z0_)), cam.xy((x1_, y_, z1_))
            return rect(min(a_[0], b_[0]), min(a_[1], b_[1]), abs(b_[0] - a_[0]), abs(b_[1] - a_[1]), c)
        o += R(404, 62, 434, 178, "bg")
        o += R(404, 66, 413, 174, "m")                                          # flywheel
        o += R(398, 112, 404, 128, "m2")                                        # crank flange
        for k in range(3):
            o += R(414 + k * 2.4, 74, 415.4 + k * 2.4, 166, "alu")              # flexible discs
        o += R(413, 76, 422, 82, "m2") + R(413, 158, 422, 164, "m2")            # rim bolts
        o += R(421, 100, 430, 140, "w2")                                        # hub
        o += R(430, 108, 436, 132, "w")                                         # generator shaft
        # terminal box: open cover with copper bars
        t0, t1 = cam.xy((476, 25.9, 198)), cam.xy((528, 25.9, 226))
        o += rect(t0[0], t1[1], t1[0] - t0[0], t0[1] - t1[1], "bg", 1)
        for k in range(3):
            u0, u1 = cam.xy((484 + k * 15, 25.8, 200)), cam.xy((490 + k * 15, 25.8, 224))
            o += rect(u0[0], u1[1], u1[0] - u0[0], u0[1] - u1[1], "cu")
        # cooling-air outlet louvres near the drive end
        lv = ""
        for k in range(7):
            ang = math.radians(140 + k * 13)
            p0 = cam.xy((436, 70 + 74.5 * math.cos(ang), 120 + 74.5 * math.sin(ang)))
            p1 = cam.xy((470, 70 + 74.5 * math.cos(ang), 120 + 74.5 * math.sin(ang)))
            lv += "M%s %sL%s %s" % (n(p0[0]), n(p0[1]), n(p1[0]), n(p1[1]))
        o += '<path class="o" style="stroke-width:1.6;opacity:.55" d="%s"/>' % lv
        # spring isolators under the base
        for xi in (40, 160, 290, 410, 520, 600):
            p0, p1 = cam.xy((xi, -2, 20)), cam.xy((xi, -2, 0))
            o += isolator(p0[0], p0[1], p1[1], 11 * sc.k / 0.48)
        return o

    out = fit_scene(build, 10, 12, area=(6, 72, 314, 194), sh_ry=8, post=post)

    # inset: alignment principle (offset + angularity exaggerated, laser units, shim)
    x0, y0, w, h = 78, 3, 164, 64
    o = panel(x0, y0, w, h, 6)
    cy = y0 + 30
    o += shaft(x0 + 8, cy, [(58, 6)], "w", "w2")                              # engine side shaft
    gx, gy, ang = x0 + 90, cy - 10, -7
    ra = math.radians(ang)
    o += '<g transform="rotate(%s %s %s)">%s</g>' % (ang, n(gx), n(gy), shaft(gx, gy, [(60, 6)], "w", "w2"))
    o += line(x0 + 8, cy, x0 + 158, cy, "cl")
    o += line(gx - 22 * math.cos(ra), gy - 22 * math.sin(ra), gx + 66 * math.cos(ra), gy + 66 * math.sin(ra), "cl")
    o += rect(x0 + 54, cy - 17, 10, 10, "dk", 1.5) + circ(x0 + 64, cy - 12, 1.6, "clamph")         # laser transmitter
    o += '<g transform="rotate(%s %s %s)">%s</g>' % (ang, n(gx), n(gy), rect(gx + 2, gy - 17, 10, 10, "dk", 1.5) + rect(gx + 1, gy - 15, 2, 6, "gl"))
    o += '<path class="laserl" d="M%s %sL%s %s"/>' % (n(x0 + 65), n(cy - 12), n(gx + 1.5), n(gy - 13))
    xo = gx - 6                                                                # offset (parallel misalignment)
    o += flow([(xo, cy - 1), (xo, gy + 1)], "grey", 4, both=True, w=1.2)
    xe = gx + 64 * math.cos(ra)                                                # angularity
    o += path("M%s %s A62 62 0 0 0 %s %s" % (n(gx + 62), n(gy), n(gx + 62 * math.cos(ra)), n(gy + 62 * math.sin(ra))), "o")
    o += line(gx, gy, gx + 66, gy, "o thin dash")
    # generator foot + shim
    fx, fy = x0 + 112, y0 + 50
    o += rect(fx - 4, fy + 6, 40, 4, "m2") + rect(fx, fy - 6, 26, 9, "w") + rect(fx + 2, fy + 3, 22, 2.4, "alu")
    o += flow([(fx - 26, fy + 4), (fx - 2, fy + 4)], "grey", 5)
    out += o
    return out


@part("genset.gsradiator")
def _():
    # root material = copper (core); tanks / frame are steel -> "m" tones, fan aluminium
    o = shadow(70, 184, 60, 5) + shadow(186, 184, 40, 5)
    # ---------------- front view
    x0, x1, yt, yb = 20, 118, 40, 152
    yp = yb - (yb - yt) * 0.25                                                  # HT / LT partition
    o += rect(x0 - 8, 22, 8, 156, "m2", 1.5) + rect(x1, 22, 8, 156, "m2", 1.5)   # side channels
    o += rect(x0 - 12, 174, 22, 6, "m2", 1) + rect(x1 - 2, 174, 22, 6, "m2", 1)  # feet
    o += rect(x0, yt, x1 - x0, yb - yt, "w")                                    # core
    o += rect(x0, yt, x1 - x0, yp - yt, "warmin") + rect(x0, yp, x1 - x0, yb - yp, "coolin")
    o += hstrips(x0, yt, x1 - x0, yb - yt, 44, "fin")
    o += vstrips(x0, yt, x1 - x0, yb - yt, 24, "gr")
    o += line(x0, yp, x1, yp, "done")
    o += rect(x0 - 2, 24, x1 - x0 + 4, 17, "m", 4) + rect(x0 - 2, yb - 1, x1 - x0 + 4, 14, "m", 4)   # top / bottom tanks
    o += line(x0 + 2, yp, x1 - 2, yp, "o")
    o += vcyl(54, 16, 9, 6, 2.2, "m2", "m") + rect(51, 13, 6, 3, "m3", 1)         # filler cap
    o += shaft(x1 + 8, 32, [(14, 5)], "m", "m2")                                 # HT inlet (top tank)
    o += shaft(x1 + 8, 158, [(14, 5)], "m", "m2")                                # HT outlet (bottom tank)
    o += shaft(x0 - 22, yp + 8, [(14, 4)], "m", "m2")                            # LT inlet / outlet
    o += shaft(x0 - 22, yb - 6, [(14, 4)], "m", "m2")
    for yy in (30, 166):
        for xx in (x0 - 4, x1 + 4):
            o += circ(xx, yy, 1.6, "bg")
    # ---------------- side view (pusher fan on the engine side, air leaves through the core)
    cx0 = 150
    o += rect(cx0 - 3, 24, 16, 17, "m", 3) + rect(cx0 - 3, yb - 1, 16, 14, "m", 3)
    o += rect(cx0, yt, 10, yb - yt, "w") + hstrips(cx0, yt, 10, yb - yt, 30, "fin")
    o += rect(cx0 - 6, 22, 4, 156, "m2", 1) + rect(cx0 - 10, 174, 22, 6, "m2", 1)
    fcx, fcy, fr = 200, (yt + yb) / 2, 48
    o += pg([(cx0 + 10, yt - 4), (fcx - 8, fcy - fr - 3), (fcx - 8, fcy + fr + 3), (cx0 + 10, yb + 4)], "m2")   # shroud
    o += pg([(cx0 + 10, yt + 2), (fcx - 8, fcy - fr + 3), (fcx - 8, fcy + fr - 3), (cx0 + 10, yb - 2)], "m")
    o += pg([(cx0 + 10, yt + 2), (fcx - 8, fcy - fr + 3), (fcx - 8, fcy + fr - 3), (cx0 + 10, yb - 2)], "o thin")
    o += rect(fcx - 9, fcy - fr - 4, 12, 2 * fr + 8, "m", 2)                    # fan ring
    for k in range(7):                                                          # blades, edge-on
        yy = fcy + fr * 0.9 * math.sin(math.radians(-80 + k * 26.6))
        tw = 3.5 + 2.5 * abs(math.cos(math.radians(-80 + k * 26.6)))
        o += pg([(fcx - tw, yy - 3.5), (fcx + tw, yy + 2), (fcx + tw, yy + 4.5), (fcx - tw, yy - 1)], "alu")
    o += rect(fcx - 5, fcy - 8, 10, 16, "alu", 2) + shaft(fcx + 4, fcy, [(16, 3.5)], "m", "m2")
    gx = fcx + 10                                                               # guard
    o += rect(gx, fcy - fr - 2, 2.4, 2 * fr + 4, "m2")
    for k in range(9):
        yy = fcy - fr + k * fr / 4
        o += line(gx - 4, yy, gx + 6, yy, "o thin")
    for yy in (fcy - 30, fcy, fcy + 30):
        o += flow([(gx + 30, yy), (gx + 8, yy), (cx0 + 30, yy + (yy - fcy) * 0.25), (cx0 - 9, yy + (yy - fcy) * 0.3)], "air", 6)
    # ---------------- insets: (a) flat tube + corrugated fin, (b) round tube expanded into plate-fin collars
    ax, ay = 248, 8
    o += panel(ax, ay, 66, 86, 6)
    for k in range(3):
        tx = ax + 12 + k * 21
        o += rect(tx, ay + 18, 6, 60, "w2", 3)                                  # flat tubes (side)
        o += path("M%s %s a3 2 0 0 1 6 0 a3 2 0 0 1 -6 0Z" % (n(tx), n(ay + 14)), "w")   # tube ends (flat oval)
        o += rect(tx + 0.8, ay + 13.2, 4.4, 1.6, "bg", 0.8)
    for k in range(2):
        fx0 = ax + 18 + k * 21
        d = "M%s %s" % (n(fx0), n(ay + 20))
        for j in range(14):
            d += " L%s %s" % (n(fx0 + (15 if j % 2 == 0 else 0)), n(ay + 20 + (j + 1) * 4.1))
        o += '<path class="cu" style="fill:none;stroke-width:1.1" d="%s"/>' % d
    o += line(ax + 10, ay + 80, ax + 58, ay + 80, "done")                       # brazed / soldered joints
    bx, by = 248, 102
    o += panel(bx, by, 66, 90, 6)
    tcy = by + 46
    for k in range(7):                                                          # plate fins with collars
        fx = bx + 8 + k * 7.4
        o += rect(fx, by + 10, 1.6, 72, "alu")
        o += rect(fx, tcy - 9, 4.2, 2.2, "alu") + rect(fx, tcy + 6.8, 4.2, 2.2, "alu")
    xe = bx + 34                                                                # expansion front
    o += rect(bx + 4, tcy - 7.2, xe - bx - 4, 2.2, "cu") + rect(bx + 4, tcy + 5, xe - bx - 4, 2.2, "cu")     # expanded part
    o += rect(xe, tcy - 5.6, bx + 62 - xe, 2.2, "cu") + rect(xe, tcy + 3.4, bx + 62 - xe, 2.2, "cu")         # not yet
    o += path("M%s %s l8 -5 l0 10 Z" % (n(xe - 8), n(tcy)), "m") + pg([(xe - 8, tcy - 5), (xe - 4, tcy - 5), (xe - 4, tcy + 5), (xe - 8, tcy + 5)], "m")
    o += rect(xe, tcy - 1.4, bx + 70 - xe, 2.8, "m2")                           # expansion rod
    o += flow([(bx + 58, by + 86), (bx + 30, by + 86)], "grey", 5)
    return o


@part("genset.gsencl")
def _():
    L, Wd, Hh, cut0, cut1 = 480, 100, 120, 150, 330

    def wall3(sc, x0, x1, z0, z1):
        BOX(sc, x0, 0, z0, x1 - x0, 1.6, z1 - z0, "w")                         # outer skin
        BOX(sc, x0, 1.6, z0, x1 - x0, 7, z1 - z0, "t", bias=0.1)                # sound-absorbing wool
        BOX(sc, x0, 8.6, z0, x1 - x0, 1.6, z1 - z0, "m", bias=0.2)              # perforated inner sheet

    def build(sc):
        BOX(sc, -4, -4, -8, L + 8, Wd + 8, 8, "dk")                              # skid
        BOX(sc, 0, 90, 0, L, 10, Hh, "w")                                       # back wall
        BOX(sc, 0, 10, 0, 10, 80, Hh, "w")                                      # intake end (louvres on the far side)
        BOX(sc, 0, 10, 0, L, 80, 6, "m")                                        # floor
        # interior: generator set on its base
        BOX(sc, 70, 30, 6, 330, 40, 14, "w", bias=1)
        sc.add(fe(GE.prism(sc.cam, (190, 50, 20), (0, 0, 1), [(-20, -110, 0), (20, -110, 1), (20, 110, 2), (-20, 110, 3)], 50, "w")), ((80, 30, 20), (300, 70, 70)))
        for i in range(8):
            BOX(sc, 86 + i * 26, 26, 70, 22, 48, 12, "m")
        CYL(sc, (300, 50, 50), (1, 0, 0), 30, 80, "w", seg=32)                   # generator
        BOX(sc, 420, 14, 6, 16, 72, 100, "dk")                                  # radiator core
        BOX(sc, 404, 22, 30, 16, 56, 60, "m")                                   # fan shroud
        RAW(sc, lambda s_: '', ((cut0, 89.9, 6), (cut1, 90, 112)))
        # front wall with the cut-away (left part, right part, strips)
        wall3(sc, 0, cut0, 0, Hh)
        wall3(sc, cut1, L, 0, Hh)
        wall3(sc, cut0, cut1, 0, 12)
        # discharge end: opening with sound splitters
        BOX(sc, L - 10, 10, 0, 10, 80, 16, "w")
        BOX(sc, L - 10, 10, 104, 10, 80, 16, "w")
        BOX(sc, L - 10, 90, 0, 10, 10, Hh, "w")
        BOX(sc, L - 34, 12, 16, 4, 76, 88, "dk", bias=0.4)
        for k in range(7):
            BOX(sc, L - 30, 15 + k * 10.5, 16, 30, 4.5, 88, "m")
        BOX(sc, 0, 0, Hh, L, Wd, 6, "w")                                        # roof
        for xc in (0, L - 12):                                                  # corner castings
            for yc in (-1, Wd - 11):
                for zc in (-2, Hh - 4):
                    BOX(sc, xc, yc, zc, 12, 12, 10, "m", bias=-0.1)
        # exhaust silencer on the roof
        for xs in (90, 250):
            BOX(sc, xs, 38, Hh + 6, 10, 24, 18, "w")
        CYL(sc, (60, 50, Hh + 42), (1, 0, 0), 20, 230, "m", seg=28)
        CYL(sc, (70, 50, Hh + 6), (0, 0, 1), 7, 20, "m", seg=16)
        CYL(sc, (270, 50, Hh + 52), (0, 0, 1), 8, 50, "m", seg=16)
        CYL(sc, (270, 50, Hh + 102), (0, 0, 1), 11, 4, "m2", seg=18)
        RAW(sc, lambda s_: person(*s_.P((-60, -70, -8)), h=68 * s_.k * s_.cam.ce), ((-70, -76, -8), (-50, -64, 60)))

    def post(sc):
        cam = sc.cam
        o = ""
        # doors on the front wall: hinges + handle
        for xa in (24, 82, 352, 410):
            q = [cam.xy(p) for p in ((xa, -0.1, 8), (xa + 46, -0.1, 8), (xa + 46, -0.1, 106), (xa, -0.1, 106))]
            o += pg(q, "o")
            q2 = [cam.xy(p) for p in ((xa + 2, -0.1, 10), (xa + 44, -0.1, 10), (xa + 44, -0.1, 104), (xa + 2, -0.1, 104))]
            o += pg(q2, "o thin")
            for zz in (24, 90):
                h0, h1 = cam.xy((xa - 1, -0.2, zz)), cam.xy((xa - 1, -0.2, zz + 8))
                o += line(h0[0], h0[1], h1[0], h1[1], "needle")
            hd = cam.xy((xa + 40, -0.2, 58))
            o += rect(hd[0] - 1.2, hd[1] - 4, 2.4, 8, "m3", 1)
        # perforation on the inner sheet seen through the cut-away (back wall)
        d = ""
        for i in range(16):
            for j in range(3):
                if True:
                    c = cam.xy((cut0 + 10 + i * 11, 89.8, 88 + j * 9))
                    d += "M%s %sh0.01" % (n(c[0]), n(c[1]))
        o += '<path class="kerf" style="stroke-width:1.4;opacity:.6" d="%s"/>' % d
        # corner casting holes
        for xc in (L - 6,):
            for zc in (3, Hh + 1):
                o += hole3(cam, (xc, -1.1, zc), (0, -1, 0), 2.2, "bg", 10) + hole3(cam, (L + 0.1, 5, zc), (1, 0, 0), 2.2, "bg", 10)
        for zc in (3, Hh + 1):
            o += hole3(cam, (6, -1.1, zc), (0, -1, 0), 2.2, "bg", 10)
        # air: in at the far end, out through the splitters
        for zz in (40, 80):
            a = cam.xy((-60, 40, zz))
            b = cam.xy((-6, 40, zz))
            o += flow([a, b], "air", 6)
            c, e = cam.xy((L + 6, 50, zz)), cam.xy((L + 60, 50, zz))
            o += flow([c, e], "warm", 6)
        return o

    out = fit_scene(build, -24, 24, area=(10, 56, 312, 190), sh_ry=10, post=post)
    # inset: wall build-up (outer sheet / wool / perforated sheet) absorbing sound from inside
    x0, y0 = 8, 6
    o = panel(x0, y0, 96, 62, 6)
    o += rect(x0 + 10, y0 + 8, 6, 48, "w2") + wool(x0 + 16, y0 + 8, 26, 48) + rect(x0 + 42, y0 + 8, 4, 48, "m")
    for k in range(8):
        o += rect(x0 + 42, y0 + 11 + k * 6, 4, 2.2, "void")
    for k in range(3):
        yy = y0 + 18 + k * 14
        dd = "M%s %s" % (n(x0 + 90), n(yy))
        for j in range(12):
            amp = 3.2 * (1 - j / 14.0) if j < 8 else 3.2 * (1 - j / 14.0) * 0.4
            dd += " q%s %s %s 0" % (n(-1.8), n(-amp if j % 2 == 0 else amp), n(-3.6))
        o += '<path class="fo" style="fill:none;stroke-width:1.3" d="%s"/>' % dd
    out += o
    return out


@part("genset.gsdaytank")
def _():
    lv = 86                                                                      # fuel level

    def build(sc):
        BOX(sc, -24, -24, 0, 198, 148, 3, "w")                                  # bund floor
        BOX(sc, -24, 120, 3, 198, 4, 14, "w")                                   # bund walls
        BOX(sc, -24, -20, 3, 4, 140, 14, "w")
        BOX(sc, 170, -20, 3, 4, 140, 14, "w")
        for xl in (6, 136):
            for yl in (6, 86):
                BOX(sc, xl, yl, 3, 8, 8, 21, "m", bias=0.5)
        BOX(sc, 0, 0, 24, 150, 100, 100, "w")                                   # tank
        BOX(sc, -24, -24, 3, 198, 4, 14, "w", bias=-1)
        CYL(sc, (28, 30, 124), (0, 0, 1), 8, 12, "m", seg=18)                   # fill connection
        CYL(sc, (28, 30, 136), (0, 0, 1), 11, 4, "m2", seg=18)
        BOX(sc, 54, 58, 124, 26, 22, 16, "m")                                   # float switch box
        CYL(sc, (100, 32, 124), (0, 0, 1), 16, 4, "w", seg=24)                  # inspection hatch
        CYL(sc, (130, 80, 124), (0, 0, 1), 3.2, 62, "m", seg=12)                # vent pipe
        CYL(sc, (130, 80, 186), (0, 0, 1), 8, 9, "m", seg=16)                   # flame arrester
        CYL(sc, (130, 80, 195), (0, 0, 1), 10, 3, "m2", seg=16)
        CYL(sc, (34, 0, 34), (0, -1, 0), 4.2, 12, "m", seg=14)                  # supply outlet (stainless)
        CYL(sc, (34, -12, 34), (0, -1, 0), 7, 4, "m2", seg=16)
        CYL(sc, (12, 0, 112), (0, -1, 0), 3.5, 10, "m", seg=12)                 # return inlet
        CYL(sc, (80, 30, 24), (0, 0, -1), 3.5, 10, "m", seg=12)                 # drain
        BOX(sc, 74, 24, 6, 12, 12, 8, "m2")
        # transfer pump with motor + manual change-over valve
        BOX(sc, 192, 10, 0, 70, 34, 6, "w")
        CYL(sc, (226, 27, 22), (1, 0, 0), 14, 34, "dk", seg=22)
        CYL(sc, (198, 27, 22), (1, 0, 0), 11, 22, "w", seg=20)
        BOX(sc, 196, 70, 0, 18, 18, 30, "m")
        CYL(sc, (205, 79, 30), (0, 0, 1), 2, 10, "m3", seg=10)

    def post(sc):
        cam = sc.cam
        o = ""
        # transparent window in the front wall: baffle, fuel and control levels
        def F(x, z):
            return cam.xy((x, -0.1, z))
        win = [F(44, 30), F(120, 30), F(120, 118), F(44, 118)]
        o += pg(win, "w3")
        o += pg([F(44, 30), F(120, 30), F(120, lv), F(44, lv)], "resin")
        bf = [F(78, 38), F(84, 38), F(84, 122), F(78, 122)]
        o += pg(bf, "m2")
        o += pg([F(44, lv), F(120, lv)], "o")
        for z, c in ((108, "laserl"), (98, "o dash"), (64, "o dash"), (46, "laserl")):
            a, b = F(46, z), F(118, z)
            o += '<path class="%s" d="M%s %sL%s %s"/>' % (c, n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            t = F(120, z)
            o += path("M%s %s l5 -3 l0 6Z" % (n(t[0]), n(t[1])), "clamph" if c == "laserl" else "d")
        o += pg(win, "o")
        # glass-tube level gauge with scale
        g0, g1 = cam.xy((134, -6, 34)), cam.xy((134, -6, 118))
        o += rect(g0[0] - 2.4, g1[1], 4.8, g0[1] - g1[1], "gl", 2)
        gl = cam.xy((134, -6, lv))
        o += rect(g0[0] - 1.6, gl[1], 3.2, g0[1] - gl[1], "resin")
        for k in range(9):
            t = cam.xy((134, -6, 40 + k * 9.5))
            o += line(t[0] + 3, t[1], t[0] + (6 if k % 2 == 0 else 4.5), t[1], "o thin")
        for z in (34, 118):
            t = cam.xy((134, -2, z))
            o += rect(t[0] - 3.5, t[1] - 2, 7, 4, "m2")
        # warning plate (shape only) and pipework pump -> valve -> tank
        p = [cam.xy(q) for q in ((14, -0.1, 70), (36, -0.1, 70), (36, -0.1, 84), (14, -0.1, 84))]
        o += pg(p, "m") + pg(p, "o")
        pp = [cam.xy(q) for q in ((198, 27, 22), (186, 27, 22), (186, 79, 22), (196, 79, 22))]
        pp2 = [cam.xy(q) for q in ((214, 79, 22), (226, 79, 22), (226, 79, 140), (90, 79, 140), (90, 79, 124))]
        o += '<path class="pipe" style="stroke-width:3" d="%s"/>' % P(pp, False) + '<path class="pipe" style="stroke-width:3" d="%s"/>' % P(pp2, False)
        return o

    return fit_scene(build, -30, 26, area=(16, 10, 304, 190), sh_ry=10, post=post)


@part("genset.gsexhaust")
def _():
    o = shadow(130, 94, 110, 4)
    # ---------------- silencer: cut-away side view (3.5 : 1)
    x0, x1, yt, yb = 40, 232, 20, 78
    cy = (yt + yb) / 2
    o += shaft(4, cy, [(16, 9)], "m", "m2") + rect(18, cy - 15, 5, 30, "w2", 1)          # inlet pipe + flange
    o += path("M%s %s A16 %s 0 0 0 %s %s Z" % (n(x0), n(yt), n((yb - yt) / 2), n(x0), n(yb)), "w2")   # dished heads
    o += path("M%s %s A16 %s 0 0 1 %s %s Z" % (n(x1), n(yt), n((yb - yt) / 2), n(x1), n(yb)), "w2")
    o += rect(x1 + 14, cy - 15, 5, 30, "w2", 1) + shaft(x1 + 19, cy, [(16, 8)], "m", "m2")   # outlet flange + pipe
    o += rect(x0, yt, x1 - x0, yb - yt, "w")
    o += path("M%s %s L%s %s" % (n(x0), n(yb - 5), n(x1), n(yb - 5)), "o")                # longitudinal weld seam
    d = ""
    for k in range(int((x1 - x0) / 3)):
        d += "M%s %s l1.4 -1.6 l1.4 1.6" % (n(x0 + 1 + k * 3), n(yb - 4))
    o += path(d, "o thin")
    # cut-away window
    wx0, wx1, wy0, wy1 = 58, 226, yt + 3, yb - 9
    o += rect(wx0, wy0, wx1 - wx0, wy1 - wy0, "w3")
    o += srect(wx0, wy0 - 3, wx1 - wx0, 3, "w2", 2.4) + srect(wx0, wy1, wx1 - wx0, 2.4, "w2", 2.4)   # shell cut edges
    b1, b2 = 122, 172
    for bx in (b1, b2):
        o += srect(bx - 1.6, wy0, 3.2, wy1 - wy0, "w2", 2.4)                                     # baffles
    o += wool(b2 + 2, wy0, wx1 - b2 - 2, wy1 - wy0)                                              # absorptive chamber
    def ptube(xa, xb, yy, r=5.5):
        s_ = rect(xa, yy - r, xb - xa, 2 * r, "m")
        dd = ""
        for i in range(int((xb - xa) / 4)):
            for j in (-1, 1):
                dd += "M%s %sh0.01" % (n(xa + 2.5 + i * 4), n(yy + j * r * 0.45))
        return s_ + '<path class="kerf" style="stroke-width:1.5" d="%s"/>' % dd
    o += ptube(wx0, 96, cy, 6)                                                                    # inlet pipe, perforated end
    o += ptube(108, 150, wy0 + 11, 5)                                                             # cross-over tube 1
    o += ptube(150, b2 + 10, wy1 - 11, 5)                                                         # cross-over tube 2
    o += ptube(b2 + 10, wx1, cy - 1, 6.5)                                                         # absorptive perforated tube
    o += flow([(0, cy), (40, cy), (92, cy)], "gas", 5.5, w=1.8)
    o += flow([(98, cy + 9), (104, wy1 - 6), (114, wy0 + 11), (140, wy0 + 11)], "gas", 5, w=1.6)
    o += flow([(150, wy0 + 16), (160, wy1 - 11), (184, wy1 - 11)], "warm", 5, w=1.6)
    o += flow([(186, cy - 1), (wx1 + 4, cy - 1), (x1 + 40, cy - 14), (x1 + 50, cy - 14)], "warm", 5.5, w=1.8)
    # ---------------- expansion joint (bellows) 3/4 view
    ey, ex0, ex1, R = 148, 32, 128, 30
    o += shadow(84, 186, 56, 4)
    o += path("M%s %s A9 %s 0 0 0 %s %s" % (n(ex0), n(ey - R - 6), n(R + 6), n(ex0), n(ey + R + 6)), "w2")   # left flange
    o += rect(ex0, ey - R - 6, 8, 2 * R + 12, "w2")
    top = "M%s %s" % (n(ex0 + 8), n(ey - R + 2))
    bot = ""
    nc = 8
    pitch = (ex1 - ex0 - 22) / nc
    for k in range(nc):
        xa = ex0 + 10 + k * pitch
        top += " Q%s %s %s %s Q%s %s %s %s" % (n(xa + pitch * 0.25), n(ey - R - 3), n(xa + pitch * 0.5), n(ey - R - 3),
                                              n(xa + pitch * 0.75), n(ey - R - 3), n(xa + pitch), n(ey - R + 2))
    body = top + " L%s %s" % (n(ex1 - 10), n(ey + R - 2))
    for k in range(nc - 1, -1, -1):
        xa = ex0 + 10 + k * pitch
        body += " Q%s %s %s %s Q%s %s %s %s" % (n(xa + pitch * 0.75), n(ey + R + 3), n(xa + pitch * 0.5), n(ey + R + 3),
                                               n(xa + pitch * 0.25), n(ey + R + 3), n(xa), n(ey + R - 2))
    o += path(body + "Z", "m")
    for k in range(nc):
        xa = ex0 + 10 + (k + 0.5) * pitch
        o += path("M%s %s A6 %s 0 0 1 %s %s" % (n(xa), n(ey - R - 3), n(R + 3), n(xa), n(ey + R + 3)), "o thin")
    o += rect(ex1 - 10, ey - R - 6, 8, 2 * R + 12, "w2")
    o += ell(ex1 - 2, ey, 9, R + 6, "w") + ell(ex1 - 2, ey, 6, R - 4, "bg")
    for k in range(10):
        a = 2 * math.pi * k / 10
        o += ell(ex1 - 2 + 7.4 * math.cos(a), ey + (R + 1) * math.sin(a), 1.2, 1.6, "bg")
    o += path("M%s %s L%s %s M%s %s L%s %s" % (n(ex0 + 6), n(ey - R + 8), n(ex1 - 4), n(ey - R + 8), n(ex0 + 6), n(ey + R - 8), n(ex1 - 4), n(ey + R - 8)), "hid")
    o += flow([(ex0 + 14, ey - R - 14), (ex1 - 14, ey - R - 14)], "grey", 5, both=True, w=1.4)    # axial
    o += flow([(ex1 + 18, ey - 18), (ex1 + 18, ey + 18)], "grey", 5, both=True, w=1.4)            # lateral
    # ---------------- inset: three-roll bending of the shell plate (end view)
    cx, cy2, r = 250, 146, 42
    body2 = ""
    pcx, pcy, pr = 250, 112, 44
    pts_ = arcpts(pcx, pcy, pr, pr, 200, -20, 40)
    body2 += '<path class="sheet" style="stroke-width:4.4" d="%s"/>' % P(pts_, False)
    body2 += circ(250, 143, 10, "w") + circ(250, 143, 3, "m3")
    for bx in (228, 272):
        body2 += circ(bx, 160, 8.5, "w") + circ(bx, 160, 2.6, "m3")
    body2 += rot(250, 145, 15, 15, -60, 30) if False else ""
    out = o + lens(cx, cy2, r) + clipc("pw-gsx-l", cx, cy2, r - 1, body2) + lens_rim(cx, cy2, r)
    out += path("M%s %s A15 15 0 0 1 %s %s" % (n(238), n(129), n(262), n(129)), "o") + head(262.5, 129.5, math.radians(60), 4)
    return out


@part("genset.gstest")
def _():
    def build(sc):
        genset_side(sc)
        BOX(sc, 760, -10, 0, 160, 150, 150, "w")                                  # load bank
        for xf in (800, 880):
            CYL(sc, (xf, 65, 150), (0, 0, 1), 30, 6, "m", seg=28)
        BOX(sc, 760, 200, 0, 110, 90, 110, "w")                                   # reactor load
        BOX(sc, 360, -230, 0, 120, 50, 70, "w")                                   # measurement desk
        BOX(sc, 380, -205, 70, 80, 10, 54, "dk")                                  # recorder screen
        RAW(sc, lambda s_: person(*s_.P((300, -200, 0)), h=120 * s_.k * s_.cam.ce), ((290, -206, 0), (310, -194, 120)))

    def post(sc):
        cam = sc.cam
        o = ""
        # power cable generator terminal box -> load bank
        ps = [cam.xy(p) for p in ((520, 70, 226), (560, 70, 240), (650, 60, 20), (740, 40, 10), (760, 40, 40))]
        o += '<path class="cable3" style="stroke-width:5" d="%s"/>' % smooth_d(ps)
        ps2 = [cam.xy(p) for p in ((780, 140, 40), (790, 180, 20), (790, 200, 30))]
        o += '<path class="cable" d="%s"/>' % smooth_d(ps2)
        # resistor grid seen through the load-bank side, fan discs, hot air
        q = [cam.xy(p) for p in ((780, -10.1, 20), (900, -10.1, 20), (900, -10.1, 130), (780, -10.1, 130))]
        o += pg(q, "bg")
        for k in range(6):
            a, b = cam.xy((786 + k * 20, -10.2, 26)), cam.xy((786 + k * 20, -10.2, 124))
            o += '<path class="hotsheet" style="stroke-width:2.2" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        for k in range(5):
            a, b = cam.xy((782, -10.2, 34 + k * 22)), cam.xy((898, -10.2, 34 + k * 22))
            o += line(a[0], a[1], b[0], b[1], "o thin")
        for xf in (800, 880):
            o += hole3(cam, (xf, 65, 156.1), (0, 0, 1), 24, "bg", 24)
            c = cam.xy((xf, 65, 156.2))
            o += flow([c, (c[0], c[1] - 26)], "warm", 5, w=1.6)
        # reactor coil symbol on its side
        c0 = cam.xy((815, 199.8, 60))
        o += path("M%s %s c4 -10 8 -10 8 0 c0 -10 8 -10 8 0 c0 -10 8 -10 8 0" % (n(c0[0] - 12), n(c0[1])), "o")
        # recorder screen + signal line to the set
        sp = [cam.xy(p) for p in ((388, -205.1, 76), (452, -205.1, 76), (452, -205.1, 118), (388, -205.1, 118))]
        o += pg(sp, "scrn")
        m0, m1 = cam.xy((392, -205.2, 104)), cam.xy((448, -205.2, 104))
        o += '<path class="scrg" d="M%s %s l%s 0 q2 6 4 1 q3 -3 6 -1 l%s 0"/>' % (n(m0[0]), n(m0[1]), n((m1[0] - m0[0]) * 0.3), n((m1[0] - m0[0]) * 0.45))
        ss = [cam.xy(p) for p in ((420, -180, 70), (420, -60, 0), (480, 0, 60), (500, 26, 200))]
        o += '<path class="o dash" d="%s"/>' % smooth_d(ss)
        return o

    out = fit_scene(build, -34, 30, area=(8, 22, 172, 186), sh_ry=8, post=post)
    # ---------------- graph: frequency (upper) and voltage (lower) after a load step
    gx0, gx1 = 182, 310
    out += panel(176, 12, 138, 176, 6)
    t0 = 204
    for yb, dip, rec in ((54, 24, 52), (138, 30, 46)):
        out += line(gx0, yb - 36, gx0, yb + 36, "o") + line(gx0, yb + 36, gx1, yb + 36, "o")      # axes
        out += line(gx0, yb, gx1, yb, "cl")                                                       # rated
        out += line(gx0, yb - 5, gx1, yb - 5, "o thin dash") + line(gx0, yb + 5, gx1, yb + 5, "o thin dash")   # tolerance band
        ps = [(gx0, yb), (t0, yb)]
        for k in range(1, 60):
            t = k / 59.0
            x = t0 + t * (gx1 - t0)
            y = yb + dip * math.exp(-t * 4.2) * math.cos(t * 7.5) * (1 - math.exp(-t * 60))
            ps.append((x, y))
        out += '<path class="o" style="stroke-width:2;fill:none" d="%s"/>' % P(ps, False)
        out += line(t0, yb - 36, t0, yb + 36, "o thin dash")
        ymin = max(p[1] for p in ps)
        xmin = [p[0] for p in ps if p[1] == ymin][0]
        out += line(xmin - 4, ymin, xmin + 16, ymin, "o thin")
        out += flow([(xmin + 12, yb), (xmin + 12, ymin)], "grey", 4, both=True, w=1.1)            # dip depth
        out += flow([(t0, yb + 30), (t0 + rec, yb + 30)], "grey", 4, both=True, w=1.1)            # recovery time
        out += line(t0 + rec, yb + 4, t0 + rec, yb + 34, "o thin")
    return out


# =====================================================================================
# dcpower: switchgear, breakers, ATS, paralleling, UPS, bulk fuel
# =====================================================================================
def cab_door(x, y, w, h, hinge_left=True, louv=True):
    """front of one switchboard section: door edge, hinges, handle, bottom louvres."""
    o = rect(x, y, w, h, "w") + rect(x + 2, y + 2, w - 4, h - 4, "o thin")
    hx = x + 1 if hinge_left else x + w - 3
    for yy in (y + 12, y + h - 20):
        o += rect(hx, yy, 2, 8, "m3", 0.6)
    gx = x + w - 6 if hinge_left else x + 4
    o += rect(gx, y + h * 0.48, 2.4, 10, "m3", 1)
    if louv:
        o += louvre(x + 8, y + h - 16, w - 16, 10, 4)
    return o


def mccb(x, y, w=11, h=17):
    return rect(x, y, w, h, "gw", 1.5) + rect(x + w * 0.32, y + h * 0.36, w * 0.36, h * 0.3, "rb", 1) + rect(x + w * 0.38, y + h * 0.3, w * 0.24, h * 0.18, "m2", 0.6)


def acb_face(x, y, w, h):
    """front fascia of a draw-out air circuit breaker (no lettering)."""
    o = rect(x - 2, y - 2, w + 4, h + 4, "m3", 2) + rect(x, y, w, h, "gw", 2)
    o += rect(x + 4, y + 4, w * 0.36, h * 0.26, "scrn", 1)                       # trip unit window
    o += circ(x + w * 0.62, y + h * 0.18, 2.6, "okl") + circ(x + w * 0.8, y + h * 0.18, 2.6, "clamph")     # close / open buttons
    o += rect(x + w * 0.56, y + h * 0.36, 7, 4, "m") + rect(x + w * 0.74, y + h * 0.36, 7, 4, "yel" if False else "t")  # indicators
    o += rect(x + w * 0.42, y + h * 0.56, w * 0.16, h * 0.36, "rb", 2)            # charging handle
    o += rect(x + 4, y + h * 0.74, 8, 4, "m2") + rect(x + w - 12, y + h * 0.74, 8, 4, "m2")
    return o


@part("dcpower.dclvswgr")
def _():
    o = shadow(112, 182, 104, 5) + shadow(262, 182, 40, 5)
    y0, y1, pw = 52, 172, 50
    xs = [12 + k * pw for k in range(4)]
    o += rect(10, y1, 4 * pw + 4, 6, "dk")                                      # channel base
    for k, x in enumerate(xs):
        o += cab_door(x, y0, pw, y1 - y0, hinge_left=(k % 2 == 0))
        o += rect(x + 1, y0 - 5, pw - 2, 5, "m2") + vstrips(x + 6, y0 - 4, pw - 12, 3, 8, "o thin")   # roof vent
        o += meter(x + 14, y0 + 13, 7.5, -30 + k * 20) + meter(x + 34, y0 + 13, 7.5, 10 - k * 15)
        for j in range(3):
            o += lamp(x + 13 + j * 9, y0 + 28, 2.2, ("okl", "clamph", "t")[j])
    # incoming / generator section: two draw-out ACBs
    for yy in (y0 + 36, y0 + 72):
        o += acb_face(xs[0] + 7, yy, pw - 14, 30)
        o += rect(xs[0] + 4, yy + 4, 2, 24, "m3") + rect(xs[0] + pw - 6, yy + 4, 2, 24, "m3")
    # feeder sections: rows of moulded-case breakers
    for k in (1, 2, 3):
        rows = 3 if k == 1 else 4
        hh = 22 if k == 1 else 17
        ww = 15 if k == 1 else 11
        for r in range(rows):
            for c in range(2 if k == 1 else 3):
                cx = xs[k] + (9 + c * 18 if k == 1 else 6 + c * 13)
                o += mccb(cx, y0 + 38 + r * (hh + 5), ww, hh)
    # ---------------- side section of one section: breaker / busbar / cable compartments
    sx0, sx1 = 232, 300
    o += rect(sx0, y0, sx1 - sx0, y1 - y0, "m")                                 # interior
    pa, pb = 254, 276
    o += rect(sx0 + 4, y0 + 40, 18, 26, "gw", 2) + rect(sx0 + 4, y0 + 76, 18, 26, "gw", 2)   # breakers (outline only)
    for yy in (y0 + 46, y0 + 82):
        o += rect(sx0 + 22, yy, pa - sx0 - 22, 3, "cu") + rect(sx0 + 22, yy + 11, pa - sx0 - 22, 3, "cu")
    o += rect(sx0 + 2, y0 + 66, 22, 2, "m3") + rect(sx0 + 2, y0 + 102, 22, 2, "m3")       # draw-out rails
    for j in range(4):                                                          # main busbars (section) + support
        o += rect(pa + 7, y0 + 10 + j * 8, 8, 5, "cu")
    o += rect(pa + 4, y0 + 7, 3, 34, "gw", 1) + rect(pa + 15, y0 + 7, 3, 34, "gw", 1)
    o += rect(pa + 9, y0 + 40, 4, 66, "cu")                                     # vertical distribution bar
    for yy in (y0 + 46, y0 + 57, y0 + 82, y0 + 93):
        o += rect(pa + 1, yy, 9, 3, "cu")
    o += rect(pa + 4, y0 + 60, 12, 4, "gw", 1) + rect(pa + 4, y0 + 96, 12, 4, "gw", 1)
    for yy, cx in ((y0 + 50, pb + 8), (y0 + 86, pb + 14)):                      # outgoing cables from below
        o += rect(pb + 1, yy - 2, cx - pb + 2, 4, "cu")
        o += '<path class="cable3" style="stroke-width:5" d="M%s %s L%s %s Q%s %s %s %s"/>' % (n(cx), n(yy + 2), n(cx), n(y1 - 18), n(cx), n(y1 - 6), n(cx - 2), n(y1 + 4))
    o += rect(pa - 1.5, y0, 3, y1 - y0, "m3") + rect(pb - 1.5, y0, 3, y1 - y0, "m3")      # partitions
    o += rect(sx0 - 2, y0 - 2, 4, y1 - y0 + 4, "m2") + rect(sx1 - 2, y0 - 2, 4, y1 - y0 + 4, "m2")
    o += rect(sx0 - 2, y0 - 6, sx1 - sx0 + 4, 5, "m2") + rect(sx0 - 2, y1, sx1 - sx0 + 4, 6, "dk")
    o += rect(sx0 - 3, y1 - 18, 2, 12, "m3")
    # inset: bolted busbar joint with match marks (tin-plated contact area)
    cx, cy, r = 282, 26, 22
    body = rect(cx - 30, cy - 9, 34, 9, "cu") + rect(cx - 6, cy - 1, 36, 9, "cu") + rect(cx - 6, cy - 1, 10, 1.6, "alu")
    for bx in (cx - 2, cx + 8):
        body += rect(bx - 2, cy - 14, 4, 26, "m2") + bolt_hex(bx, cy - 13, 4.2, "m") + bolt_hex(bx, cy + 11, 4.2, "m")
    body += '<path class="clampl" style="stroke-width:1.4" d="M%s %sL%s %sM%s %sL%s %s"/>' % (n(cx - 4), n(cy - 20), n(cx - 1), n(cy - 7), n(cx + 6), n(cy - 20), n(cx + 9), n(cy - 7))
    o += leader(pa + 11, y0 + 24, cx - r * 0.6, cy + r * 0.8)
    o += lens(cx, cy, r) + clipc("pw-lv-l", cx, cy, r - 1, body) + lens_rim(cx, cy, r)
    return o


def vcb_truck(x, yb, s=1.0, out=False):
    """draw-out VCB on its truck, side view; x = front of truck, yb = rail level. returns svg."""
    o = rect(x, yb - 8 * s, 56 * s, 6 * s, "m2")                                 # truck frame
    for wx in (x + 8 * s, x + 46 * s):
        o += circ(wx, yb - 2 * s, 4.4 * s, "m3") + circ(wx, yb - 2 * s, 1.6 * s, "m")
    o += rect(x + 2 * s, yb - 62 * s, 30 * s, 54 * s, "m", 2)                     # operating mechanism box
    o += circ(x + 10 * s, yb - 50 * s, 2.4 * s, "okl") + circ(x + 18 * s, yb - 50 * s, 2.4 * s, "clamph")
    o += rect(x + 7 * s, yb - 40 * s, 14 * s, 6 * s, "m2") + rect(x + 7 * s, yb - 26 * s, 6 * s, 10 * s, "rb", 1)
    o += rect(x + 32 * s, yb - 74 * s, 14 * s, 66 * s, "sand", 3 * s)             # epoxy pole
    for yy in (yb - 66 * s, yb - 22 * s):                                        # contact arms + tulip contacts
        o += rect(x + 46 * s, yy, 26 * s, 5 * s, "cu") + rect(x + 70 * s, yy - 2 * s, 7 * s, 9 * s, "cu", 2)
    return o


@part("dcpower.dcmvswgr")
def _():
    o = shadow(104, 186, 92, 5)
    X0, X1, Y0, Y1 = 22, 186, 30, 180
    pv, ph, pl = 112, 90, 70                                                     # partitions: vertical, busbar floor, LV floor
    o += rect(X0, Y0, X1 - X0, Y1 - Y0, "m")                                     # interior (back sheet)
    # LV control compartment: relay + meter on the door, wiring
    o += rect(X0 + 4, Y0 + 8, 16, 12, "gw", 1.5) + rect(X0 + 6, Y0 + 10, 9, 5, "scrn")
    o += rect(X0 + 4, Y0 + 24, 12, 10, "gw", 1.5) + circ(X0 + 10, Y0 + 29, 3, "m")
    o += rect(X0 + 30, Y0 + 6, 30, 4, "gw") + rect(X0 + 30, Y0 + 12, 5, 24, "m2")
    for k in range(4):
        o += rect(X0 + 38 + k * 6, Y0 + 14, 4, 12, "gw", 1)
    o += path("M%s %s C%s %s %s %s %s %s M%s %s C%s %s %s %s %s %s" % (n(X0 + 16), n(Y0 + 14), n(X0 + 26), n(Y0 + 14), n(X0 + 30), n(Y0 + 30), n(X0 + 44), n(Y0 + 28),
                                                                      n(X0 + 16), n(Y0 + 29), n(X0 + 26), n(Y0 + 34), n(X0 + 34), n(Y0 + 36), n(X0 + 50), n(Y0 + 28)), "o thin")
    # breaker compartment: VCB on truck, rails, bushings + shutters (open)
    o += rect(X0, Y1 - 12, pv - X0, 3, "m3")                                     # rails
    o += vcb_truck(X0 + 8, Y1 - 12, 1.0)
    for yy in (Y1 - 80, Y1 - 36):
        o += pg([(pv - 8, yy - 6), (pv + 4, yy - 9), (pv + 4, yy + 14), (pv - 8, yy + 11)], "sand")      # spout bushing
        o += rect(pv - 6, yy + 0.5, 12, 4, "cu")
        o += rect(pv - 13, yy - 22, 3, 13, "m2") + rect(pv - 13, yy + 14, 3, 13, "m2")              # shutter halves (open)
    # busbar compartment (rear top): epoxy-coated main busbars across the line-up
    o += rect(pv + 4, Y1 - 82, 30, 5, "cu") + rect(pv + 30, Y0 + 30, 5, Y1 - 82 - Y0 - 25, "cu")
    for k in range(3):
        bx = pv + 22 + k * 18
        o += rect(bx - 6, Y0 + 14, 12, 18, "sand", 4) + rect(bx - 3.5, Y0 + 16.5, 7, 13, "cu", 2)
    o += rect(pv + 12, Y0 + 32, 56, 3, "sand") + rect(pv + 26, Y0 + 26, 8, 8, "sand", 2)
    # cable compartment (rear bottom): CTs, cable terminations from below
    o += rect(pv + 4, Y1 - 38, 24, 5, "cu") + rect(pv + 24, Y1 - 38, 5, 18, "cu")
    o += rect(pv + 17, Y1 - 64 + 30, 4, 6, "m3") + rect(pv + 32, Y1 - 64 + 30, 4, 6, "m3")
    for k, cx in enumerate((pv + 44, pv + 60)):
        o += rect(cx - 3, Y1 - 66, 6, 10, "cu") + pg([(cx - 6, Y1 - 56), (cx + 6, Y1 - 56), (cx + 4, Y1 - 30), (cx - 4, Y1 - 30)], "gw")
        o += '<path class="cable3" style="stroke-width:7" d="M%s %sL%s %s"/>' % (n(cx), n(Y1 - 30), n(cx), n(Y1 + 4))
        o += rect(cx - 7, Y1 - 52, 14, 5, "dk", 1.5)                               # CT ring (section)
    o += rect(pv + 26, Y1 - 46, 30, 3, "cu") + rect(pv + 52, Y1 - 70, 4, 27, "cu") + rect(pv + 38, Y1 - 70, 26, 4, "cu")
    # metal partitions (the point of metal-clad): thick
    o += rect(pv - 2, Y0, 4, Y1 - Y0, "m3")
    o += rect(pv, ph - 2, X1 - pv, 4, "m3")
    o += rect(X0, pl - 2, 64, 4, "m3")
    o += rect(X0 + 62, Y0, 4, pl - Y0, "m3")                                     # vent duct behind the LV compartment
    # enclosure, door, roof with pressure-relief flaps
    o += rect(X0 - 4, Y0 - 2, 5, Y1 - Y0 + 4, "m2") + rect(X1 - 1, Y0 - 2, 5, Y1 - Y0 + 4, "m2")
    o += rect(X0 - 6, Y0 + 70, 3, 18, "m3", 1)                                    # door handle
    o += rect(X0 - 4, Y1, X1 - X0 + 8, 6, "dk")
    for fx0, fx1, ang in ((X0 - 2, pv - 2, -13), (pv + 2, X1 + 2, -15)):
        o += rect(fx0 + 4, Y0 - 4, fx1 - fx0 - 8, 3, "m2")
        hx = fx1 - 4
        o += '<g transform="rotate(%s %s %s)">%s</g>' % (ang, n(fx0 + 4), n(Y0 - 4), rect(fx0 + 4, Y0 - 7, fx1 - fx0 - 10, 3, "w"))
    o += flow([(74, Y1 - 92), (99, pl + 8), (99, Y0 + 10), (96, Y0 - 18)], "gas", 6, w=2.2)
    o += flow([(150, Y0 + 40), (152, Y0 + 10), (158, Y0 - 20)], "gas", 6, w=2.2)
    # inset: withdrawn (test / disconnected) position, shutters closed
    ix, iy, iw, ih = 200, 46, 114, 110
    o += panel(ix, iy, iw, ih, 6)
    rb = iy + ih - 14
    o += rect(ix + 6, rb, iw - 12, 2.4, "m3")
    o += vcb_truck(ix + 4, rb, 0.78)
    wx = ix + iw - 14
    o += rect(wx, iy + 8, 4, ih - 22, "m3")
    for yy in (rb - 52, rb - 18):
        o += pg([(wx - 6, yy - 5), (wx + 2, yy - 7), (wx + 2, yy + 11), (wx - 6, yy + 9)], "sand")
        o += rect(wx - 11, yy - 9, 3, 22, "m2")                                   # shutter closed
    o += flow([(ix + 70, iy + 12), (ix + 30, iy + 12)], "grey", 5, w=1.6)
    o += line(ix + 62, rb - 50, wx - 12, rb - 50, "o thin dash")
    return o


def braze(x, y):
    return circ(x, y, 1.5, "t")


@part("dcpower.dcvcb")
def _():
    # root class is mt-al (alumina), so every material here is named explicitly
    cx = 86
    o = shadow(cx, 192, 44, 4)
    yt, yj, yb = 40, 92, 146                                                     # top plate, joint ring, bottom plate
    ri, ro = 30, 37                                                              # ceramic inner / outer half widths
    o += rect(cx - ri, yt, 2 * ri, yb - yt, "scrn")                              # vacuum
    for sgn in (-1, 1):                                                          # ceramic insulator (two sections)
        xa = cx + sgn * ri if sgn > 0 else cx - ro
        o += srect(xa, yt + 3, ro - ri, yj - yt - 5, "pt", 3)
        o += srect(xa, yj + 2, ro - ri, yb - yj - 5, "pt", 3)
    o += rect(cx - ro - 2, yj - 2, 2 * ro + 4, 4, "m")                           # joint ring + shield flange
    o += rect(cx - ro - 1, yt, 2 * ro + 2, 4, "m") + rect(cx - ro - 1, yb - 4, 2 * ro + 2, 4, "m")   # end plates
    o += rect(cx - 22, yt + 26, 2.6, 52, "m") + rect(cx + 19.4, yt + 26, 2.6, 52, "m")     # vapour shield
    o += rect(cx - 22, yj - 1.5, 44, 3, "m") if False else ""
    o += rect(cx - 7, 12, 14, yt + 2 - 12, "cu") + rect(cx - 7, yt + 4, 14, 32, "cu")      # fixed stem
    o += rect(cx - 12, 8, 24, 5, "cu", 1)
    gap_top, gap_bot = yt + 36, yt + 44
    o += rect(cx - 17, gap_top - 5, 34, 5, "cus3")                               # fixed contact (CuCr)
    o += rect(cx - 17, gap_bot, 34, 5, "cus3")                                   # moving contact
    o += rect(cx - 7, gap_bot + 5, 14, 190 - gap_bot - 5, "cu")                  # moving stem
    # bellows between moving stem and bottom plate
    bz0, bz1 = yt + 66, yb - 4
    dl, dr = "M%s %s" % (n(cx - 9), n(bz0)), "M%s %s" % (n(cx + 9), n(bz0))
    k = 0
    yy = bz0
    while yy < bz1 - 0.1:
        yy2 = min(bz1, yy + 3.4)
        w_ = 15 if k % 2 == 0 else 9
        dl += " L%s %s" % (n(cx - w_), n((yy + yy2) / 2)) + " L%s %s" % (n(cx - 9), n(yy2))
        dr += " L%s %s" % (n(cx + w_), n((yy + yy2) / 2)) + " L%s %s" % (n(cx + 9), n(yy2))
        yy = yy2
        k += 1
    o += path(dl, "o") + path(dr, "o")
    o += '<path class="m" d="%s"/>' % (dl.replace("M", "M", 1) + " L%s %s L%s %sZ" % (n(cx - 7), n(bz1), n(cx - 7), n(bz0)))
    o += '<path class="m" d="%s"/>' % (dr + " L%s %s L%s %sZ" % (n(cx + 7), n(bz1), n(cx + 7), n(bz0)))
    o += rect(cx - 13, bz0 - 3, 26, 3, "m")                                      # bellows shield cup
    o += rect(cx - 12, yb + 6, 24, 10, "m2", 2)                                  # guide
    for x_, y_ in ((cx - ro, yt + 3), (cx + ro, yt + 3), (cx - ro, yb - 3), (cx + ro, yb - 3), (cx - ro, yj), (cx + ro, yj),
                   (cx - 7, yt + 2), (cx + 7, yt + 2), (cx - 9, bz0), (cx + 9, bz0), (cx - 9, bz1), (cx + 9, bz1)):
        o += braze(x_, y_)
    # ---- breaker overall (3/4): three epoxy poles on the mechanism box
    def brk(sc):
        BOX(sc, 0, 0, 0, 150, 70, 70, "m")
        for k in range(3):
            CYL(sc, (25 + k * 50, 40, 70), (0, 0, 1), 15, 90, "t", seg=24)
            CYL(sc, (25 + k * 50, 40, 160), (0, 0, 1), 9, 8, "cu", seg=16)
            CYL(sc, (25 + k * 50, 55, 95), (0, 1, 0), 5, 30, "cu", seg=12)
            CYL(sc, (25 + k * 50, 55, 135), (0, 1, 0), 5, 30, "cu", seg=12)

    def brk_post(sc):
        cam = sc.cam
        s_ = ""
        for xb, c in ((30, "okl"), (52, "clamph")):
            s_ += hole3(cam, (xb, -0.2, 46), (0, -1, 0), 5, c, 14)
        q = [cam.xy(p) for p in ((80, -0.2, 40), (110, -0.2, 40), (110, -0.2, 54), (80, -0.2, 54))]
        s_ += pg(q, "m2")
        q = [cam.xy(p) for p in ((86, -0.2, 43), (104, -0.2, 43), (104, -0.2, 51), (86, -0.2, 51))]
        s_ += pg(q, "rb")
        d_ = ""
        for k in range(4):                                                      # closing spring seen through the box
            a, b = cam.xy((20 + k * 7, -0.2, 12)), cam.xy((24 + k * 7, -0.2, 30))
            d_ += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        s_ += path(d_, "o thin")
        return s_
    o += shadow(250, 104, 46, 4)
    o += scene_at(brk, -30, 24, 216, 92, 0.44, brk_post)
    # ---- spiral-contact face (top view)
    lx, ly, lr = 168, 160, 24
    o += lens(lx, ly, lr, cx + 14, gap_top - 3)
    o += circ(lx, ly, 18, "cus3") + circ(lx, ly, 5, "cu")
    for k in range(4):
        a0 = k * 90
        pts_ = [(lx + (5 + 12 * t) * math.cos(math.radians(a0 + 140 * t)), ly + (5 + 12 * t) * math.sin(math.radians(a0 + 140 * t))) for t in [i / 10 for i in range(11)]]
        o += '<path class="bgline" style="stroke-width:2.2" d="%s"/>' % P(pts_, False)
    # ---- arc while opening (small)
    ax, ay = 254, 126
    o += panel(ax - 34, ay, 92, 64, 6)
    o += rect(ax - 18, ay + 8, 36, 50, "scrn")
    o += rect(ax - 4, ay + 2, 8, 18, "cu") + rect(ax - 10, ay + 18, 20, 4, "cus3")
    o += rect(ax - 10, ay + 40, 20, 4, "cus3") + rect(ax - 4, ay + 44, 8, 18, "cu")
    o += ell(ax, ay + 31, 9, 8, "fl")
    o += '<path class="fo" style="stroke-width:3.2" d="M%s %s q-3 5 1 9 q3 4 -1 9"/>' % (n(ax), n(ay + 22))
    o += '<path class="m" style="stroke-width:.8" d="M%s %s q-3 5 1 9 q3 4 -1 9"/>' % (n(ax), n(ay + 22))
    o += flow([(ax + 30, ay + 36), (ax + 30, ay + 54)], "grey", 4.5, w=1.4)
    return o


@part("dcpower.dcacb")
def _():
    # root class is mt-cu (copper conductors): moulded parts gw, grids / springs steel ("m")
    def body(sc):
        BOX(sc, 0, 0, 0, 120, 90, 96, "gw")                                     # moulded frame
        for k in range(4):
            BOX(sc, 6 + k * 28, 24, 96, 24, 58, 24, "gw")                        # arc chutes per pole
        BOX(sc, 4, -10, 6, 112, 10, 84, "gw")                                    # front fascia
        for k in range(4):
            for zz in (16, 64):
                BOX(sc, 10 + k * 28, 90, zz, 12, 34, 9, "cu")                    # rear terminals

    def body_post(sc):
        cam = sc.cam
        s_ = ""
        for k in range(4):                                                      # chute slots
            d_ = ""
            for j in range(5):
                a, b = cam.xy((10 + k * 28 + j * 4, 30, 120.1)), cam.xy((10 + k * 28 + j * 4, 76, 120.1))
                d_ += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            s_ += path(d_, "o")
        def F(x, z, w, h, c):
            return pg([cam.xy(p) for p in ((x, -10.2, z), (x + w, -10.2, z), (x + w, -10.2, z + h), (x, -10.2, z + h))], c)
        s_ += F(12, 52, 34, 26, "scrn") + F(16, 56, 26, 8, "scrg" if False else "m2")       # trip unit (no digits)
        s_ += F(58, 62, 12, 8, "m") + F(76, 62, 12, 8, "t")                                  # open/closed + charged flags
        s_ += hole3(cam, (64, -10.3, 46), (0, -1, 0), 4.5, "okl", 14) + hole3(cam, (82, -10.3, 46), (0, -1, 0), 4.5, "clamph", 14)
        s_ += F(56, 12, 14, 26, "rb")                                                        # charging handle
        s_ += F(96, 40, 10, 30, "m2")
        return s_
    o = shadow(76, 182, 66, 6)
    o += fit_scene(body, -32, 24, area=(10, 22, 144, 178), sh=False, post=body_post)
    # ---------------- one pole, side section
    x0, x1, y0, y1 = 162, 312, 26, 184
    o += shadow(237, 188, 74, 4)
    o += rect(x0, y0 + 50, x1 - x0 - 30, y1 - y0 - 50, "gw", 4)                  # moulded frame
    o += rect(x0 + 4, y0 + 54, x1 - x0 - 38, y1 - y0 - 58, "void")
    cx0, cx1, cy0, cy1 = 214, 272, y0, y0 + 62                                   # arc chute
    o += rect(cx0, cy0, cx1 - cx0, cy1 - cy0, "gw", 3) + rect(cx0 + 3, cy0 + 3, cx1 - cx0 - 6, cy1 - cy0 - 3, "void")
    for k in range(13):
        yy = cy0 + 6 + k * 4.2
        o += pg([(cx0 + 4, yy), (cx0 + 22, yy), (cx0 + 29, yy + 2.6), (cx0 + 36, yy), (cx1 - 4, yy), (cx1 - 4, yy + 1.6),
                 (cx0 + 36, yy + 1.6), (cx0 + 29, yy + 4.2), (cx0 + 22, yy + 1.6), (cx0 + 4, yy + 1.6)], "m3")
    # fixed side: upper terminal from the rear, main + arcing contacts
    o += rect(268, 92, 44, 10, "cu") + rect(258, 82, 12, 30, "cu")
    o += rect(254, 94, 5, 9, "alu", 1) + rect(256, 80, 6, 6, "alu", 1) + rect(258, 66, 6, 16, "cu")
    # moving arm about its pivot, lower terminal + flexible braid
    px, py = 222, 156
    o += pg([(px - 4, py), (242, 98), (250, 92), (252, 106), (px + 6, py + 4)], "cu")
    o += rect(247, 94, 5, 9, "alu", 1) + pg([(248, 84), (252, 80), (254, 88), (250, 92)], "alu")
    o += circ(px, py, 5, "m") + circ(px, py, 1.8, "m3")
    o += '<path class="foilstrip" d="M%s %s c8 6 14 -6 22 0 s14 -6 22 0 s10 4 14 2"/>' % (n(px + 4), n(py + 6))
    o += rect(268, 156, 44, 10, "cu")
    # arc driven up into the grid and split into short arcs
    o += ell(244, 70, 8, 14, "h")
    for k in range(7):
        yy = cy0 + 10 + k * 6.3
        o += '<path class="spark" d="M%s %s q2 1.6 0 3.2"/>' % (n(cx0 + 29), n(yy))
    o += flow([(232, 80), (232, 30)], "warm", 5, w=1.6)
    # operating mechanism (front): closing spring, latch, shunt-trip coil
    o += coil(x0 + 10, x0 + 46, 110, 6, 5, "m")
    o += rect(x0 + 6, 104, 4, 12, "m2") + rect(x0 + 46, 104, 4, 12, "m2")
    o += pg([(x0 + 50, 124), (px - 8, 140), (px - 10, 146), (x0 + 50, 130)], "m2")             # link to the arm
    o += pg([(x0 + 18, 132), (x0 + 30, 132), (x0 + 30, 140), (x0 + 24, 140), (x0 + 24, 146), (x0 + 18, 146)], "m2")   # latch
    o += rect(x0 + 10, 154, 18, 16, "m2", 2)
    for k in range(5):
        o += line(x0 + 12 + k * 3.4, 156, x0 + 12 + k * 3.4, 168, "foil")
    return o


def pylon(cx, cy, s=1.0):
    """utility source symbol (transmission tower), no lettering."""
    d = "M%s %s L%s %s L%s %s M%s %s L%s %s M%s %s L%s %s M%s %s L%s %s" % (
        n(cx - 7 * s), n(cy + 10 * s), n(cx), n(cy - 10 * s), n(cx + 7 * s), n(cy + 10 * s),
        n(cx - 8 * s), n(cy - 4 * s), n(cx + 8 * s), n(cy - 4 * s), n(cx - 5 * s), n(cy + 2 * s), n(cx + 5 * s), n(cy + 2 * s),
        n(cx - 3.5 * s), n(cy - 4 * s), n(cx + 4 * s), n(cy + 2 * s))
    return path(d, "o")


def load_sym(cx, cy):
    return path("M%s %s l0 6" % (n(cx), n(cy - 6)), "o") + path("M%s %s l5 0 l-5 7 l-5 -7Z" % (n(cx), n(cy)), "d")


@part("dcpower.dcats")
def _():
    # root class mt-cu: moulded parts gw, frame steel "m"
    o = shadow(98, 178, 90, 5)
    x0, x1, y0, y1 = 14, 166, 32, 170
    o += rect(x0, y0, x1 - x0, y1 - y0, "m2", 3)                                 # steel frame
    o += rect(x0 + 4, y0 + 4, x1 - x0 - 8, y1 - y0 - 8, "m", 2)
    for row, (yt, up) in enumerate(((y0 + 10, True), (y1 - 48, False))):
        for k in range(4):
            px = x0 + 50 + k * 26
            o += rect(px, yt, 22, 38, "gw", 3)                                    # pole housing
            o += rect(px + 5, yt + 12, 12, 14, "void", 1)
            o += rect(px + 6, yt + 14, 10, 3.4, "alu", 1) + rect(px + 6, yt + 20.6, 10, 3.4, "alu", 1)   # contacts
            ty = yt - 12 if up else yt + 38
            o += rect(px + 7, ty, 8, 12, "cu") + circ(px + 11, ty + (4 if up else 8), 1.6, "m3")       # terminals
    # common load-side terminals between the rows (to the load)
    # mechanism: motor, single lever driving both rows, position flag
    my = (y0 + y1) / 2
    o += rect(x0 + 8, my - 16, 34, 32, "m2", 3) + circ(x0 + 25, my, 11, "dk") + circ(x0 + 25, my, 4, "m")
    o += rect(x0 + 50, y0 + 48, 100, 4, "m3") + rect(x0 + 50, y1 - 52, 100, 4, "m3")      # pole shafts
    o += pg([(x0 + 78, y0 + 50), (x0 + 84, y0 + 50), (x0 + 110, y1 - 50), (x0 + 104, y1 - 50)], "m3")   # lever
    o += circ(x0 + 94, my, 4.5, "m") + circ(x0 + 94, my, 1.6, "m3")
    for k, yy in enumerate((my - 9, my, my + 9)):                                 # position indicator: utility / off / generator
        o += circ(x0 + 66, yy, 2.4, "clamph" if k == 2 else "m2")
    o += path("M%s %s l7 -3 l0 6Z" % (n(x0 + 70), n(my + 9)), "d")
    # mechanical interlock bar (the point of the device)
    ix = x0 + 136
    o += rect(ix - 3.5, y0 + 50, 7, y1 - y0 - 100, "bolt", 2)
    o += flow([(ix + 9, my - 6), (ix + 9, y0 + 52)], "gas", 5, w=1.6) + flow([(ix + 9, my + 6), (ix + 9, y1 - 52)], "gas", 5, w=1.6)
    # controller (voltage / frequency monitoring, timers)
    cx0 = 172
    o += rect(cx0, 62, 34, 78, "gw", 3) + rect(cx0 + 4, 68, 26, 16, "scrn", 1.5)
    o += path(sine(cx0 + 6, cx0 + 28, 76, 3.6, 2), "scrg")
    for k in range(3):
        o += circ(cx0 + 9 + k * 8, 96, 3, "knob") + line(cx0 + 9 + k * 8, 96, cx0 + 9 + k * 8 + 2, 93.5, "needle")
    for k in range(3):
        o += lamp(cx0 + 9 + k * 8, 110, 1.8, ("okl", "t", "clamph")[k])
    o += '<path class="cable" style="stroke-width:2" d="M%s %s C%s %s %s %s %s %s"/>' % (n(cx0), n(128), n(cx0 - 6), n(132), n(x1 + 2), n(140), n(x1 - 4), n(148))
    # ---------------- one-line diagram
    lx = 268
    o += panel(222, 8, 90, 182, 6)
    o += pylon(244, 30) + gsym(292, 30, 9)
    o += path("M244 40 L244 76 M292 39 L292 76", "o")
    o += rect(234, 76, 68, 40, "void", 3) + rect(234, 76, 68, 40, "o", 3)
    o += circ(244, 80, 2, "d") + circ(292, 80, 2, "d") + circ(lx, 108, 2, "d")
    o += path("M%s %s L%s %s" % (n(lx), n(108), n(246), n(82)), "done")                    # blade: on utility
    o += path("M%s %s L%s %s" % (n(lx), n(108), n(290), n(82)), "o dash")                  # alternative position
    o += '<path class="spark" style="fill:none;stroke-width:2" d="M252 92 Q268 84 282 92"/>' + head(284, 93.5, math.radians(30), 5).replace('class="af"', 'class="clamph"')
    o += path("M%s %s L%s %s" % (n(lx), n(116), n(lx), n(160)), "o")
    o += load_sym(lx, 166)
    o += path("M%s %s l10 0 m-5 0 l0 0" % (n(lx - 5), n(176)), "o")
    return o


@part("dcpower.dcsync")
def _():
    o = shadow(76, 184, 68, 5)
    y0, y1, pw = 26, 178, 58
    xa, xb = 12, 70
    # panel 1, door closed: HMI, synchroscope, V / Hz meters, switches, lamps
    o += cab_door(xa, y0, pw, y1 - y0, True, louv=True)
    o += rect(xa + 10, y0 + 12, 38, 26, "scrn", 2)
    o += rect(xa + 14, y0 + 16, 12, 8, "scrl") + rect(xa + 30, y0 + 16, 14, 3, "scrl") + rect(xa + 30, y0 + 21, 10, 3, "scrl")
    for k in range(4):
        o += rect(xa + 15 + k * 7, y0 + 34 - 3 - k * 1.5, 4, 3 + k * 1.5, "scrl")
    sx, sy = xa + 29, y0 + 58                                                    # synchroscope
    o += circ(sx, sy, 12, "m2") + circ(sx, sy, 9.5, "m")
    for k in range(12):
        a = 2 * math.pi * k / 12
        o += line(sx + 7.5 * math.cos(a), sy + 7.5 * math.sin(a), sx + 9 * math.cos(a), sy + 9 * math.sin(a), "o thin")
    o += line(sx, sy, sx + 1.5, sy - 8, "needle") + circ(sx, sy, 1.6, "m3")
    o += meter(xa + 15, y0 + 84, 8, -20) + meter(xa + 43, y0 + 84, 8, 25)
    for k in range(3):
        o += circ(xa + 15 + k * 14, y0 + 104, 4, "knob") + line(xa + 15 + k * 14, y0 + 104, xa + 17 + k * 14, y0 + 101, "needle")
    for k in range(4):
        o += lamp(xa + 12 + k * 11, y0 + 118, 2.2, ("okl", "clamph", "t", "okl")[k])
    # panel 2, door open: mounting plate with PLC, relays, terminals, wiring ducts
    o += rect(xb, y0, pw, y1 - y0, "m2")
    o += rect(xb + 3, y0 + 3, pw - 6, y1 - y0 - 6, "m")
    def duct(x, y, w, h):
        s_ = rect(x, y, w, h, "gw")
        if w > h:
            s_ += vstrips(x, y, w, h * 0.35, int(w / 3), "o thin")
        else:
            s_ += hstrips(x, y, w * 0.35, h, int(h / 3), "o thin")
        return s_
    o += duct(xb + 6, y0 + 8, pw - 12, 6) + duct(xb + 6, y0 + 48, pw - 12, 6) + duct(xb + 6, y0 + 92, pw - 12, 6) + duct(xb + 6, y0 + 132, pw - 12, 6)
    o += duct(xb + 6, y0 + 8, 6, 130) + duct(xb + pw - 12, y0 + 8, 6, 130)
    o += rect(xb + 14, y0 + 18, 38, 24, "m2", 1)                                 # PLC rack
    for k in range(7):
        o += rect(xb + 16 + k * 5, y0 + 20, 4.2, 20, "gw", 0.8)
        o += circ(xb + 18.1 + k * 5, y0 + 23, 0.8, "okl" if k % 3 else "clamph")
    for k in range(2):                                                           # protective relays
        o += rect(xb + 15 + k * 19, y0 + 58, 16, 28, "gw", 1.5) + rect(xb + 18 + k * 19, y0 + 61, 10, 6, "scrn")
        o += circ(xb + 20 + k * 19, y0 + 76, 1.4, "okl") + circ(xb + 25 + k * 19, y0 + 76, 1.4, "t")
    for k in range(6):                                                           # auxiliary relays
        o += rect(xb + 15 + k * 6, y0 + 102, 5, 12, "gw", 1) + rect(xb + 15.8 + k * 6, y0 + 104, 3.4, 4, "fl")
    for k in range(14):                                                          # terminal blocks
        o += rect(xb + 15 + k * 2.6, y0 + 118, 2.4, 10, "gw" if k % 2 else "m2")
        o += circ(xb + 16.2 + k * 2.6, y0 + 120, 0.6, "cu")
    d = ""
    for k in range(6):
        d += "M%s %s q0 4 3 6" % (n(xb + 17 + k * 6), n(y0 + 114))
    o += path(d, "o thin")
    # open door seen edge-on with its inner face
    o += pg([(xb + pw, y0), (xb + pw + 14, y0 + 8), (xb + pw + 14, y1 + 2), (xb + pw, y1)], "w2")
    o += pg([(xb + pw + 3, y0 + 10), (xb + pw + 11, y0 + 15), (xb + pw + 11, y0 + 60), (xb + pw + 3, y0 + 56)], "gw")
    o += rect(xa - 2, y1, 2 * pw + 4, 5, "dk")
    # ---------------- one-line diagram: G1..G4 -> breakers -> common bus -> feeders; utility incomer
    o += panel(150, 8, 162, 182, 6)
    by = 104
    o += '<path class="o" style="stroke-width:3" d="M166 %s L304 %s"/>' % (n(by), n(by))
    gxs = [196, 226, 256, 286]
    for k, gx in enumerate(gxs):
        o += gsym(gx, 28, 8) + line(gx, 36, gx, by, "o") + cbsym(gx, 68)
    o += pylon(168, 30, 0.9) + line(168, 40, 168, by, "o") + cbsym(168, 68, 4.2, "m2")
    for fx in (178, 208, 238):
        o += line(fx, by, fx, 160, "o") + cbsym(fx, 128) + load_sym(fx, 168)
    # synchronising call-out on G2's breaker: two sine waves coming into phase
    o += leader(gxs[1] + 4.5, 68, 266, 136)
    o += panel(252, 122, 56, 44, 5)
    o += '<path class="o" style="stroke-width:1.6;fill:none" d="%s"/>' % sine(256, 304, 144, 12, 1.5)
    o += '<path class="fo" style="stroke-width:1.6;fill:none" d="%s"/>' % sine(256, 304, 144, 10.5, 1.5, 0.35)
    o += line(280, 126, 280, 162, "o thin dash")
    return o


def conv_box(x, y, w, h, ac_in=True):
    """converter block: diagonal split, sine on one side, DC bars on the other (no lettering)."""
    o = rect(x, y, w, h, "void", 2) + rect(x, y, w, h, "o", 2) + line(x + 2, y + h - 2, x + w - 2, y + 2, "o thin")
    sx0, sy0 = (x + 3, y + h * 0.3) if ac_in else (x + w * 0.5, y + h * 0.72)
    dx0, dy0 = (x + w * 0.52, y + h * 0.72) if ac_in else (x + 3, y + h * 0.3)
    o += path(sine(sx0, sx0 + w * 0.42, sy0, h * 0.12, 1), "o")
    o += line(dx0, dy0 - 1.6, dx0 + w * 0.4, dy0 - 1.6, "o") + '<path class="o dash" d="M%s %sL%s %s" style="stroke-dasharray:2 1.6"/>' % (n(dx0), n(dy0 + 1.6), n(dx0 + w * 0.4), n(dy0 + 1.6))
    return o


def battery_sym(cx, cy):
    o = ""
    for k in range(2):
        yy = cy + k * 7
        o += line(cx - 9, yy, cx + 9, yy, "o") + '<path class="o" style="stroke-width:2.6" d="M%s %sL%s %s"/>' % (n(cx - 5), n(yy + 3.5), n(cx + 5), n(yy + 3.5))
    return o


@part("dcpower.dcups")
def _():
    # root class mt-cu (busbars): cabinets steel "m", heat sink "alu", moulded / board parts "gw"
    o = shadow(160, 98, 150, 4)
    y0, y1, pw = 10, 92, 41
    xs = [12 + k * pw for k in range(7)]
    o += rect(10, y1, 7 * pw + 4, 4, "dk")
    for k, x in enumerate(xs):
        if k in (4, 5):                                                         # battery cabinets, doors open
            o += rect(x, y0, pw, y1 - y0, "m2") + rect(x + 2.5, y0 + 2.5, pw - 5, y1 - y0 - 5, "m")
            o += rect(x + 6, y0 + 4, pw - 12, 6, "m3", 1) + rect(x + 16, y0 + 5, 9, 4, "gw", 1)   # breaker on top shelf
            for r in range(10):
                yy = y0 + 13 + r * 6.6
                o += rect(x + 4, yy + 5.2, pw - 8, 1.2, "m3")
                o += rect(x + 5, yy, pw - 17, 5.2, "gw", 0.8) + rect(x + pw - 11, yy + 0.6, 6, 4.4, "pcb" if False else "m2", 0.8)
                o += circ(x + pw - 8, yy + 2.8, 0.8, "okl")
        else:
            o += rect(x, y0, pw, y1 - y0, "w" if False else "m") + rect(x + 1.5, y0 + 1.5, pw - 3, y1 - y0 - 3, "o thin")
            o += rect(x + pw - 5, y0 + 38, 2, 8, "m3", 1)
            if k in (1, 2):                                                      # UPS modules: fans, draw-out power units
                for fx in (x + 12, x + 29):
                    o += circ(fx, y0 + 10, 6, "m2") + circ(fx, y0 + 10, 4.5, "bg")
                    for j in range(4):
                        a = j * math.pi / 2 + 0.4
                        o += line(fx, y0 + 10, fx + 4 * math.cos(a), y0 + 10 + 4 * math.sin(a), "gridl")
                for r in range(4):
                    yy = y0 + 22 + r * 15
                    o += rect(x + 5, yy, pw - 10, 12, "m2", 1) + rect(x + pw / 2 - 6, yy + 8, 12, 2, "m3", 1)
                    o += vstrips(x + 8, yy + 2, pw - 16, 5, 7, "o thin")
                    o += circ(x + 9, yy + 9, 0.9, "okl")
            elif k == 0:
                o += meter(x + 12, y0 + 13, 6.5, -20) + meter(x + 29, y0 + 13, 6.5, 30)
                for j in range(3):
                    o += lamp(x + 12 + j * 8.5, y0 + 26, 1.8, ("okl", "clamph", "t")[j])
                o += louvre(x + 7, y1 - 16, pw - 14, 10, 4)
            elif k == 3:
                o += rect(x + 12, y0 + 18, 17, 17, "m2", 2) + circ(x + 20.5, y0 + 26.5, 5, "rb") + rect(x + 19.5, y0 + 19, 2, 8, "m", 1)
                o += lamp(x + 20.5, y0 + 44, 2.2, "t") + louvre(x + 7, y1 - 16, pw - 14, 10, 4)
            else:
                o += louvre(x + 7, y1 - 16, pw - 14, 10, 4)
        o += rect(x + 1, y0 - 3, pw - 2, 3, "m2")
    # ---------------- block diagram (normal path blue, on battery orange, bypass grey)
    bx, by = 8, 106
    o += panel(bx, by, 164, 86, 6)
    yl = by + 50
    o += conv_box(bx + 28, yl - 13, 28, 26, True) + conv_box(bx + 98, yl - 13, 28, 26, False)
    o += line(bx + 8, yl, bx + 28, yl, "o") + line(bx + 56, yl, bx + 98, yl, "o") + line(bx + 126, yl, bx + 156, yl, "o")
    o += circ(bx + 77, yl, 1.8, "d") + line(bx + 77, yl, bx + 77, yl + 12, "o") + battery_sym(bx + 77, yl + 14)
    o += path("M%s %s L%s %s L%s %s L%s %s" % (n(bx + 16), n(yl), n(bx + 16), n(by + 16), n(bx + 146), n(by + 16), n(bx + 146), n(yl)), "o")
    o += rect(bx + 70, by + 10, 16, 12, "void", 2) + rect(bx + 70, by + 10, 16, 12, "o", 2) + path("M%s %s l8 -4 m0 8 l-8 -4" % (n(bx + 74), n(by + 16)), "o thin")  # static bypass switch
    o += circ(bx + 146, yl, 1.8, "d") + circ(bx + 16, yl, 1.8, "d")
    o += flow([(bx + 10, yl + 5), (bx + 30, yl + 5)], "air", 4.5, w=1.4) + flow([(bx + 58, yl - 5), (bx + 96, yl - 5)], "air", 4.5, w=1.4)
    o += flow([(bx + 128, yl + 5), (bx + 158, yl + 5)], "air", 4.5, w=1.4)
    o += flow([(bx + 84, yl + 22), (bx + 88, yl + 4), (bx + 96, yl + 4)], "warm", 4.5, w=1.6)
    o += flow([(bx + 30, by + 10), (bx + 64, by + 10)], "grey", 4, w=1.1)
    # ---------------- power unit close-up (3/4)
    def pu(sc):
        BOX(sc, 0, 0, 0, 160, 90, 8, "alu")                                        # heat-sink base
        for k in range(12):
            BOX(sc, 3 + k * 13.2, 0, -34, 4, 90, 34, "alu")                        # fins
        for k in range(3):
            BOX(sc, 10 + k * 48, 18, 8, 40, 56, 12, "gw")                           # IGBT modules
        BOX(sc, 6, 14, 26, 146, 64, 2.4, "cu")                                      # laminated busbar: copper
        BOX(sc, 6, 14, 28.4, 146, 64, 1.6, "gw")                                    #   insulation film
        BOX(sc, 6, 14, 30, 146, 64, 2.4, "cu")                                      #   copper
        for k in range(4):
            CYL(sc, (24 + k * 36, 100, 0), (0, 0, 1), 12, 44, "gw", seg=22)          # film capacitors
        BOX(sc, 14, 24, 40, 130, 46, 3, "gw")                                       # gate driver board
        for k in range(3):
            BOX(sc, 26 + k * 44, 34, 43, 16, 12, 5, "dk")
            for j in range(2):
                CYL(sc, (52 + k * 44, 30 + j * 26, 26), (0, 0, 1), 3, 14, "m", seg=10)   # stand-offs

    def pu_post(sc):
        cam = sc.cam
        s_ = ""
        for k in range(3):
            for dx in (6, 34):
                for dy in (10, 46):
                    s_ += hole3(cam, (10 + k * 48 + dx, 18 + dy, 20.1), (0, 0, 1), 2.2, "m3", 10)
        return s_
    o += fit_scene(pu, -28, 30, area=(182, 104, 312, 194), sh_ry=5, post=pu_post)
    return o


@part("dcpower.dcfuel")
def _():
    o = ""
    # ---------------- buried double-wall tank, section
    gx0, gx1, gy = 6, 198, 76
    tx0, tx1, ty0, ty1 = 34, 180, 112, 158
    tcy = (ty0 + ty1) / 2
    soil = [(gx0, gy + 8), (gx1, gy + 8), (gx1, 192), (gx0, 192)]
    o += rect(gx0, gy + 8, gx1 - gx0, 192 - gy - 8, "sand") + hatch(soil, 5, 45)
    o += srect(gx0, gy, gx1 - gx0, 8, "m2", 2.5)                                  # concrete slab
    def capsule(x0_, x1_, y0_, y1_, c):
        r_ = (y1_ - y0_) / 2
        return path("M%s %s L%s %s A%s %s 0 0 1 %s %s L%s %s A%s %s 0 0 1 %s %sZ" % (
            n(x0_), n(y0_), n(x1_), n(y0_), n(r_ * 0.45), n(r_), n(x1_), n(y1_), n(x0_), n(y1_), n(r_ * 0.45), n(r_), n(x0_), n(y0_)), c)
    o += capsule(tx0 - 5, tx1 + 5, ty0 - 5, ty1 + 5, "gw")                        # FRP outer shell
    o += capsule(tx0 - 2.5, tx1 + 2.5, ty0 - 2.5, ty1 + 2.5, "void")              # interstitial (leak detection) space
    o += capsule(tx0, tx1, ty0, ty1, "w")                                         # steel inner shell
    o += capsule(tx0 + 2, tx1 - 2, ty0 + 2, ty1 - 2, "m")
    fl = ty0 + (ty1 - ty0) * 0.25
    o += path("M%s %s L%s %s L%s %s L%s %s A%s %s 0 0 1 %s %s L%s %s A%s %s 0 0 1 %s %sZ" % (
        n(tx0 + 2), n(fl), n(tx1 - 2), n(fl), n(tx1 - 2), n(fl), n(tx1 - 2), n(fl), n(9), n(tcy - fl + 22), n(tx1 - 2), n(ty1 - 2),
        n(tx0 + 2), n(ty1 - 2), n(9), n(tcy - fl + 22), n(tx0 + 2), n(fl)), "resin")
    o += line(tx0 + 2, fl, tx1 - 2, fl, "o")
    mx = 106
    o += rect(mx - 12, gy + 8, 24, ty0 - gy - 10, "w") + rect(mx - 15, ty0 - 6, 30, 4, "w2")   # manhole neck + cover
    o += srect(mx - 18, gy, 36, 8, "void", 6) + rect(mx - 18, gy - 3, 36, 3, "m2")             # manhole chamber lid
    pipes = ((mx - 8, 30, "fill"), (mx - 2, 18, "vent"), (mx + 4, 50, "gauge"), (mx + 9, 42, "suction"))
    for px, top, kind in pipes:
        o += '<path class="pipe" style="stroke-width:3" d="M%s %sL%s %s"/>' % (n(px), n(ty0 - 2), n(px), n(top))
    o += '<path class="pipe" style="stroke-width:3" d="M%s %sL%s %s"/>' % (n(mx + 9), n(ty0), n(mx + 9), n(ty1 - 6))   # suction to bottom
    o += rect(mx - 12, 26, 8, 6, "m2", 1)                                         # fill cap
    o += rect(mx - 7, 10, 10, 9, "m2", 2) + hstrips(mx - 7, 10, 10, 9, 4, "o thin")  # flame arrester on the vent
    o += rect(mx + 1, 44, 7, 7, "gw", 1)                                          # level gauge head
    o += '<path class="pipe" style="stroke-width:3" d="M%s %s L%s %s L%s %s"/>' % (n(mx + 9), n(42), n(mx + 9), n(36), n(212), n(36))   # to pump unit
    o += '<path class="o" style="stroke-width:1.4" d="M%s %s L%s %s L%s %s"/>' % (n(tx1 + 1), n(ty0 - 4), n(150), n(gy - 6), n(150), n(56))
    o += rect(144, 46, 14, 10, "gw", 1.5) + circ(151, 51, 2, "clamph")             # leak detector
    # ---------------- transfer pump unit (3/4)
    def pu(sc):
        BOX(sc, 0, 0, 0, 200, 100, 8, "w")                                           # common base
        for k, yy in enumerate((26, 74)):
            sc.add(fe(GE.cyl(sc.cam, (40, yy, 30), (1, 0, 0), 16, 30, "w", seg=22)), ((40, yy - 16, 14), (70, yy + 16, 46)))     # pump
            CYL(sc, (78, yy, 30), (1, 0, 0), 18, 56, "dk", seg=22)                    # motor
            BOX(sc, 72, yy - 14, 8, 64, 28, 6, "w")
            CYL(sc, (22, yy, 8), (0, 0, 1), 9, 34, "m", seg=18)                       # strainer
            CYL(sc, (22, yy, 42), (0, 0, 1), 11, 4, "m2", seg=18)
        CYL(sc, (-8, 10, 52), (0, 1, 0), 4, 80, "m", seg=12)                          # suction header
        CYL(sc, (46, 10, 52), (0, 1, 0), 4, 80, "m", seg=12)                          # discharge header (check valves)
        for yy in (26, 74):
            BOX(sc, 40, yy - 5, 48, 12, 10, 10, "m2")
        BOX(sc, 150, 70, 8, 40, 26, 70, "w")                                          # control box

    def pu_post(sc):
        cam = sc.cam
        s_ = ""
        for yy in (26, 74):
            c = cam.xy((14, yy, 62))
            s_ += ell(c[0], c[1], 5, 2.2, "o") + line(c[0], c[1], c[0], c[1] + 6, "o")
        q = [cam.xy(p) for p in ((154, 69.9, 30), (184, 69.9, 30), (184, 69.9, 70), (154, 69.9, 70))]
        s_ += pg(q, "m") + pg(q, "o")
        c = cam.xy((176, 69.8, 62))
        s_ += circ(c[0], c[1], 1.6, "okl")
        return s_
    o += fit_scene(pu, -30, 28, area=(206, 14, 312, 104), sh_ry=4, post=pu_post)
    # ---------------- flow: main tank -> pump unit -> day tanks, return lines
    fx, fy = 206, 116
    o += panel(fx, fy, 108, 74, 5)
    o += capsule(fx + 6, fx + 30, fy + 48, fy + 64, "w")
    o += rect(fx + 40, fy + 44, 16, 16, "m2", 2) + circ(fx + 48, fy + 52, 4, "dk")
    for k in range(4):
        dy = fy + 8 + k * 16
        o += rect(fx + 84, dy, 16, 11, "w", 1.5)
        o += flow([(fx + 56, fy + 50), (fx + 70, dy + 5), (fx + 83, dy + 5)], "fuel", 4, w=1.3, smooth=False)
        o += '<path class="o dash" style="fill:none" d="M%s %s L%s %s L%s %s"/>' % (n(fx + 84), n(dy + 9), n(fx + 66), n(dy + 9), n(fx + 30), n(fy + 50))
    o += flow([(fx + 30, fy + 56), (fx + 39, fy + 56)], "fuel", 4, w=1.3)
    return o
