"""Part drawings for the power-generation sections: synchronous generators (generator) and gas turbines /
gas engines (gasgen). Same studio-lit metal style as il_parts.py: viewBox 0 0 320 200, theme classes only,
no text. Shaded solids use il_gear prisms with a hand-ordered painter (far -> near).

Material notes (the page sets mt-* on the <svg> from the first material named in the part spec)
- "w"/ws*  : the part's own metal (steel; cast iron on gtcasing / genassy; copper on gencoil)
- "dk"     : electrical-steel laminations, black resin / semiconductive tape
- "cu"     : copper windings, damper bars;  "t"/ts* : mica tape, amber insulation
- "gw"/gws*: thermal-barrier coating, ceramic, insulating paper;  "m"/ms* : machined / stainless bright metal
- "alu"    : aluminium fans and rectifier hubs;  "pt": painted housings
"""
import math
import il_gear as GE
from il_base import *
from il_parts import part


# =====================================================================================
# helpers
# =====================================================================================
class RCam(GE.Cam):
    """camera that records the screen extent of everything it projects (for fitting)."""

    def __init__(s, ox=0, oy=0, az=-30, el=24, k=1.0):
        GE.Cam.__init__(s, ox, oy, az, el, k)
        s.bb = [1e9, 1e9, -1e9, -1e9]

    def P(s, p):
        q = GE.Cam.P(s, p)
        b = s.bb
        b[0], b[1], b[2], b[3] = min(b[0], q[0]), min(b[1], q[1]), max(b[2], q[0]), max(b[3], q[1])
        return q


def fit(fn, az, el, area=(16, 12, 304, 180), sh=True, shy=9):
    """run fn(cam) with a probe camera, then again with a camera fitted into area. returns (svg, cam)."""
    pr = RCam(0, 0, az, el, 1.0)
    fn(pr)
    x0, y0, x1, y1 = pr.bb
    L, T, R, B = area
    k = min((R - L) / max(x1 - x0, 1e-6), (B - T) / max(y1 - y0, 1e-6))
    ox = L + ((R - L) - (x1 - x0) * k) / 2 - x0 * k
    oy = T + ((B - T) - (y1 - y0) * k) / 2 - y0 * k
    cam = RCam(ox, oy, az, el, k)
    body = fn(cam)
    x0, y0, x1, y1 = cam.bb
    s = shadow((x0 + x1) / 2, y1 - 2, (x1 - x0) * 0.52, shy) if sh else ""
    return s + body, cam


def P(ps, close=True):
    return "M" + " L".join(n(x) + " " + n(y) for x, y in ps) + ("Z" if close else "")


def pg(ps, c="w"):
    return path(P(ps), c)


def sty(s, st):
    """add an inline style (CSS variables only) to the first element of s."""
    return s.replace("/>", ' style="%s"/>' % st, 1)


def stroke(ps, var, w, dash=None, edge=True):
    """screen polyline drawn as a tube: dark edge + coloured core (colour from a CSS variable)."""
    d = P(ps, False)
    o = ""
    if edge:
        o += '<path d="%s" style="fill:none;stroke:var(--il-edge);stroke-width:%s;stroke-linecap:round;stroke-linejoin:round"/>' % (d, n(w + 1.3))
    o += '<path d="%s" style="fill:none;stroke:var(%s);stroke-width:%s;stroke-linecap:round;stroke-linejoin:round%s"/>' % (
        d, var, n(w), ";stroke-dasharray:" + dash if dash else "")
    return o


def arcl(r, a0, a1, seg, f0=0, band=16):
    """arc points (u,v,fid) from a0 to a1 (deg); fids banded by absolute angle for smooth shading."""
    out = []
    for k in range(seg + 1):
        a = a0 + (a1 - a0) * k / seg
        out.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), f0 + int((a % 360) * band / 360)))
    return out


def sector(ro, ri, a0, a1, seg=36):
    """annular sector outline (ro outer, ri inner) from a0 to a1 degrees (a1 > a0)."""
    o = arcl(ro, a0, a1, seg, 0)
    o[-1] = (o[-1][0], o[-1][1], 90)                       # radial cut face at a1
    i = arcl(ri, a1, a0, seg, 40)
    i[-1] = (i[-1][0], i[-1][1], 91)                       # radial cut face at a0
    return o + i


def circ_o(r, seg=48, f0=0):
    return [(r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), f0 + k * 16 // seg) for k in range(seg)]


def ringx(c, x0, L, ro, ri, mat="w", a0=None, a1=None, seg=None, at=(0, 0), **kw):
    """ring / tube along +x (u -> y, v -> z). optional sector a0..a1 (angles in the y-z plane, 90 = top, 180 = front).
    at = (y, z) of the axis."""
    O = (x0, at[0], at[1])
    seg = seg or (48 if ro > 24 else 32 if ro > 12 else 20)
    if a0 is not None:
        return GE.prism(c, O, (1, 0, 0), sector(ro, ri, a0, a1, seg), L, mat, smooth=True, **kw)
    holes = [circ_o(ri, seg, 40)] if ri else []
    return GE.prism(c, O, (1, 0, 0), circ_o(ro, seg), L, mat, holes=holes, smooth=True, **kw)


def ringz(c, z0, L, ro, ri, mat="w", seg=48, cx=0, cy=0, **kw):
    holes = [circ_o(ri, seg, 40)] if ri else []
    return GE.prism(c, (cx, cy, z0), (0, 0, 1), circ_o(ro, seg), L, mat, holes=holes, smooth=True, **kw)


def yz(r, a):
    return r * math.cos(math.radians(a)), r * math.sin(math.radians(a))


def c3(c, C, A, r, a0=0, a1=360, seg=28):
    """screen points of a 3D circle / arc (centre C, normal A)."""
    E1, E2, _ = GE.frame(A)
    full = abs(a1 - a0) >= 359.9
    cnt = seg if full else seg + 1
    out = []
    for k in range(cnt):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        out.append(c.xy(tuple(C[i] + r * (math.cos(t) * E1[i] + math.sin(t) * E2[i]) for i in range(3))))
    return out


def xarc(c, x, r, a0, a1, seg=24):
    """screen points of an arc of radius r at axial position x (axis along x, angles in the y-z plane)."""
    return [c.xy((x,) + yz(r, a0 + (a1 - a0) * k / seg)) for k in range(seg + 1)]


def lam_x(c, x0, x1, r, step, at=(0, 0), cls="gr"):
    """lamination lines: visible half-arcs on a cylinder along x."""
    D = c.D
    tc = math.degrees(math.atan2(-D[2], -D[1]))
    d = ""
    x = x0 + step
    while x < x1 - 0.5:
        d += P([c.xy((x, at[0] + yy, at[1] + zz)) for yy, zz in (yz(r, tc - 86 + 172 * k / 20) for k in range(21))], False)
        x += step
    return path(d, cls)


def lam_z(c, z0, z1, r, step, cls="gr"):
    D = c.D
    ac = math.degrees(math.atan2(-D[1], -D[0]))
    d = ""
    z = z0 + step
    while z < z1 - 0.5:
        d += P([c.xy((xx, yy, z)) for xx, yy in (yz(r, ac - 86 + 172 * k / 20) for k in range(21))], False)
        z += step
    return path(d, cls)


def hole(c, C, A, r, cl="bg", seg=14):
    return pg(c3(c, C, A, r, seg=seg), cl)


def quad(c, ps, cl="w"):
    return pg([c.xy(p) for p in ps], cl)


def boxp(c, x, y, z, sx, sy, sz, mat="w", **kw):
    loop = [(-y, x, 0), (-y, x + sx, 1), (-y - sy, x + sx, 2), (-y - sy, x, 3)]
    return GE.prism(c, (0, 0, z), (0, 0, 1), loop, sz, mat, **kw)


def depth(c, p):
    return GE.Cam.P(c, p)[2]


def clip(cid, ps, body):
    return '<clipPath id="%s"><path d="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (cid, P(ps), cid, body)


def panel(x, y, w, h, r=6):
    return rect(x, y, w, h, "void", r) + rect(x, y, w, h, "o", r)


def lens(cx, cy, r, tx=None, ty=None):
    s = ""
    if tx is not None:
        a = math.atan2(ty - cy, tx - cx)
        s += line(cx + r * math.cos(a), cy + r * math.sin(a), tx, ty, "o thin dash") + circ(tx, ty, 2.2, "o")
    return s + circ(cx, cy, r, "void") + circ(cx, cy, r, "o")


def clipc(cid, cx, cy, r, body):
    return '<clipPath id="%s"><circle cx="%s" cy="%s" r="%s"/></clipPath><g clip-path="url(#%s)">%s</g>' % (cid, n(cx), n(cy), n(r), cid, body)


def hatch(polys, step=3.4, ang=45, cls="hatch"):
    """section hatching clipped to polygon(s) (even-odd)."""
    if polys and isinstance(polys[0][0], (int, float)):
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
        xs = sorted(u1 + (v - w1) / (w2 - w1) * (u2 - u1) for (u1, w1), (u2, w2) in edges if (w1 <= v < w2) or (w2 <= v < w1))
        for k in range(0, len(xs) - 1, 2):
            ua, ub = xs[k], xs[k + 1]
            d += "M%s %sL%s %s" % (n(ua * ca - v * sa), n(ua * sa + v * ca), n(ub * ca - v * sa), n(ub * sa + v * ca))
        v += step
    return path(d, cls) if d else ""


def section(polys, c="w", step=3.4, ang=45):
    if polys and isinstance(polys[0][0], (int, float)):
        polys = [polys]
    return '<path class="%s" fill-rule="evenodd" d="%s"/>' % (c, "".join(P(p) for p in polys)) + hatch(polys, step, ang)


def srect(x, y, w, h, c="w", step=3.2, ang=45):
    return section([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], c, step, ang)


def flow(ps, kind="air", w=1.8, hs=5.5):
    """coloured flow arrow through screen points (head at the end)."""
    lc, hc = {"air": ("fo", "fdot"), "gas": ("clampl", "clamph"), "fuel": ("fence", "bolt"), "a": ("a", "af")}[kind]
    x1, y1 = ps[-2]
    x2, y2 = ps[-1]
    ang = math.atan2(y2 - y1, x2 - x1)
    q = list(ps[:-1]) + [(x2 - hs * 0.6 * math.cos(ang), y2 - hs * 0.6 * math.sin(ang))]
    s = '<path class="%s" style="fill:none;stroke-width:%s" d="%s"/>' % (lc, n(w), smooth_d(q))
    return s + head(x2, y2, ang, hs).replace('class="af"', 'class="%s"' % hc)


def smooth_d(ps, close=False):
    if len(ps) < 3:
        return P(ps, close)
    q = [ps[0]] + list(ps) + [ps[-1]]
    d = "M%s %s" % (n(q[1][0]), n(q[1][1]))
    for i in range(1, len(q) - 2):
        p0, p1, p2, p3 = q[i - 1], q[i], q[i + 1], q[i + 2]
        d += " C%s %s %s %s %s %s" % (n(p1[0] + (p2[0] - p0[0]) / 6), n(p1[1] + (p2[1] - p0[1]) / 6),
                                      n(p2[0] - (p3[0] - p1[0]) / 6), n(p2[1] - (p3[1] - p1[1]) / 6), n(p2[0]), n(p2[1]))
    return d


def person(x, y, h=26, c="m3"):
    k = h / 26.0

    def q(px, py):
        return (x + px * k, y - py * k)
    body = [q(-2.2, 0), q(-1.2, 11.5), q(1.2, 11.5), q(2.2, 0), q(3.4, 0), q(2.8, 12.5), q(3.6, 19.6), q(4.6, 12.6), q(5.6, 12.8),
            q(4.6, 20.4), q(3.0, 21.6), q(-3.0, 21.6), q(-4.6, 20.4), q(-5.6, 12.8), q(-4.6, 12.6), q(-3.6, 19.6), q(-2.8, 12.5), q(-3.4, 0)]
    hx, hy = q(0, 23.9)
    return pg(body, c) + circ(hx, hy, 2.2 * k, c)


def loft(c, secs, mat="w", cap=True, dark=0, cap_mat=None, edges=True):
    """skin through closed 3D sections (same point count). back faces culled, faces depth-sorted.
    returns svg (side faces + optional end caps)."""
    D = c.D
    items = []
    m = len(secs[0])
    for j in range(len(secs) - 1):
        A_, B_ = secs[j], secs[j + 1]
        for i in range(m):
            i2 = (i + 1) % m
            p0, p1, q1, q0 = A_[i], A_[i2], B_[i2], B_[i]
            e = (p1[0] - p0[0] + q1[0] - q0[0], p1[1] - p0[1] + q1[1] - q0[1], p1[2] - p0[2] + q1[2] - q0[2])
            ax = (q0[0] - p0[0] + q1[0] - p1[0], q0[1] - p0[1] + q1[1] - p1[1], q0[2] - p0[2] + q1[2] - p1[2])
            nr = GE._norm(GE._cross(ax, e))
            items.append((nr, (p0, p1, q1, q0)))
    # orientation: make normals point outward (compare with centroid direction)
    cen = [sum(p[k] for s_ in secs for p in s_) / (len(secs) * m) for k in range(3)]
    flip = 0
    for nr, qd in items[:m]:
        mid = [sum(p[k] for p in qd) / 4 for k in range(3)]
        flip += GE._dot(nr, (mid[0] - cen[0], mid[1] - cen[1], mid[2] - cen[2]))
    sg = -1 if flip < 0 else 1
    out = []
    vis = []
    for nr, qd in items:
        nr = (nr[0] * sg, nr[1] * sg, nr[2] * sg)
        v = GE._dot(nr, D) < 0
        vis.append(v)
        if not v:
            continue
        sp = [c.P(p) for p in qd]
        dep = sum(p[2] for p in sp) / 4
        cls = "%ss%d" % (mat, min(4, GE.shade(nr) + dark))
        out.append((dep, '<path class="%s" d="%s"/>' % (cls, P([(p[0], p[1]) for p in sp]))))
    # silhouette edges between visible / hidden neighbours, plus visible end edges
    ed = ""
    nsec = len(secs) - 1
    for j in range(nsec):
        for i in range(m):
            a = vis[j * m + i]
            b = vis[j * m + (i + 1) % m]
            if a != b:
                p, q = secs[j][(i + 1) % m], secs[j + 1][(i + 1) % m]
                ed += "M%s %sL%s %s" % tuple(n(v) for v in c.xy(p) + c.xy(q))
            for jj, sec in ((0, secs[0]), (nsec - 1, secs[-1])):
                if a and j == jj:
                    p, q = sec[i], sec[(i + 1) % m]
                    ed += "M%s %sL%s %s" % tuple(n(v) for v in c.xy(p) + c.xy(q))
    out.sort(key=lambda t: -t[0])
    s = "".join(o for _, o in out) + ('<path class="el" d="%s"/>' % ed if ed and edges else "")
    if cap:
        for sec, sgn in ((secs[0], -1), (secs[-1], 1)):
            a, b, cc = sec[0], sec[m // 3], sec[2 * m // 3]
            nr = GE._norm(GE._cross((b[0] - a[0], b[1] - a[1], b[2] - a[2]), (cc[0] - a[0], cc[1] - a[1], cc[2] - a[2])))
            other = secs[1] if sgn < 0 else secs[-2]
            v = (sec[0][0] - other[0][0], sec[0][1] - other[0][1], sec[0][2] - other[0][2])
            if GE._dot(nr, v) < 0:
                nr = (-nr[0], -nr[1], -nr[2])
            if GE._dot(nr, D) < 0:
                s += pg([c.xy(p) for p in sec], cap_mat or mat)
    return s


def seg3(c, a, b, w, h, mat="w", ext=0.0, **kw):
    """rectangular bar from 3D point a to b (cross-section w x h), optionally extended at both ends."""
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    L = math.sqrt(GE._dot(d, d))
    u = GE._norm(d)
    O = (a[0] - u[0] * ext, a[1] - u[1] * ext, a[2] - u[2] * ext)
    loop = [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 1), (w / 2, h / 2, 2), (-w / 2, h / 2, 3)]
    return GE.prism(c, O, u, loop, L + 2 * ext, mat, **kw)


# =====================================================================================
# generator: synchronous generator
# =====================================================================================
@part("generator.genframe")
def _():
    R, Ri, L = 52, 47, 86

    def foot(c, yc):
        o = boxp(c, 2, yc - 9, -64, L - 4, 18, 6, "w")
        o += boxp(c, 6, yc - 1.6, -58, L - 12, 3.2, 22, "w")
        for x in (12, L / 2, L - 12):
            o += hole(c, (x, yc + (-5 if yc < 0 else 5), -58), (0, 0, 1), 2.2)
        return o

    def lug(c, x):
        loop = [(x - 7, 50, 0), (x + 7, 50, 1), (x + 5, 60, 2)] + [(x + 5 * math.cos(math.radians(a)), 60 + 5 * math.sin(math.radians(a)), 3) for a in range(20, 180, 20)] + [(x - 5, 60, 4)]
        return GE.prism(c, (0, 1.8, 0), (0, -1, 0), loop, 3.6, "w", holes=[GE.circle_outline(2.2, 12, 12, x, 60)])

    def sc(c):
        o = foot(c, 34)
        o += ringx(c, 0, 7, 56, 41, "w")                                     # far end plate
        o += ringx(c, 7, L - 14, R, Ri, "w")                                  # shell
        for x in (7, L - 7):                                                 # weld beads
            o += path(P(xarc(c, x, R + 0.4, 62, 244), False), "o")
        # interior through the near opening: axial ribs, tips machined
        ribs = []
        for k in range(12):
            a = 15 + 30 * k
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            pts_ = [(41 * ca - 1.7 * sa, 41 * sa + 1.7 * ca, 0), (47.5 * ca - 1.7 * sa, 47.5 * sa + 1.7 * ca, 1),
                    (47.5 * ca + 1.7 * sa, 47.5 * sa - 1.7 * ca, 2), (41 * ca + 1.7 * sa, 41 * sa - 1.7 * ca, 3)]
            ribs.append((depth(c, (L / 2, 44 * ca, 44 * sa)),
                         GE.prism(c, (7, 0, 0), (1, 0, 0), pts_, L - 14, "w", fid_mat=lambda f: "m" if f == 3 else "w")))
        ribs.sort(key=lambda t: -t[0])
        o += clip("pw2-frame-in", xarc(c, L - 7, Ri, 0, 360, 40), "".join(r for _, r in ribs))
        # near end plate, a quarter cut away, with the machined spigot
        o += ringx(c, L - 7, 7, 56, 41, "w", 172, 458)
        o += ringx(c, L, 3, 45.5, 41, "m", 172, 458)
        for a in (215, 262, 309, 356, 43):                                    # vent windows
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            o += quad(c, [(L, 48 * ca - 4 * sa, 48 * sa + 4 * ca), (L, 54 * ca - 4 * sa, 54 * sa + 4 * ca),
                          (L, 54 * ca + 4 * sa, 54 * sa - 4 * ca), (L, 48 * ca + 4 * sa, 48 * sa - 4 * ca)], "bg")
        # terminal-box seat + lifting lugs
        o += boxp(c, 30, -13, 47, 22, 22, 7, "w")
        o += quad(c, [(34, -9, 54.1), (48, -9, 54.1), (48, 5, 54.1), (34, 5, 54.1)], "bg")
        o += lug(c, 16) + lug(c, L - 16)
        o += foot(c, -34)
        return o
    return fit(sc, -34, 22, (22, 10, 298, 182))[0]


def slot_hole(ri, ns, sd, sw, mouth=None, seg_t=1):
    """inner boundary of a stator lamination with ns rectangular slots (depth sd, width sw).
    mouth: optional narrower mouth width (semi-closed slot)."""
    out = []
    step = 360.0 / ns
    hs = math.degrees(math.asin(sw / 2 / ri))
    for k in range(ns):
        a = k * step
        # tooth tip arc from previous slot to this one
        for j in range(seg_t + 1):
            aa = a - step + hs + (step - 2 * hs) * j / seg_t
            out.append((ri * math.cos(math.radians(aa)), ri * math.sin(math.radians(aa)), 1000 + k))
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        r0 = math.sqrt(ri * ri - sw * sw / 4)
        for i, (r, t) in enumerate(((r0, -sw / 2), (ri + sd, -sw / 2), (ri + sd, sw / 2), (r0, sw / 2))):
            out.append((r * ca - t * sa, r * sa + t * ca, k * 4 + i))
    return out


@part("generator.gencore")
def _():
    Ro, Ri, NS = 50, 33, 36
    inner = slot_hole(Ri, NS, 7, 2.6)
    outer = circ_o(Ro, 48)

    def sc(c):
        o = ""
        z = 0
        o += ringz(c, -4, 4, Ro, 41, "w")                                       # lower clamping plate
        packs = [(0, 20), (22.5, 19), (44, 20)]
        for i, (z0, h) in enumerate(packs):
            if i:                                                               # ventilation duct + duct pieces
                o += ringz(c, z0 - 2.5, 2.5, Ro - 5, 0, "dk", dark=1)
                for k in range(18):
                    a = k * 20 + 10
                    if not (190 <= a <= 390 or a <= 30):
                        continue
                    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                    lp = [(-(r * sa + t * ca), r * ca - t * sa, j) for j, (r, t) in enumerate(((Ro - 7, -0.8), (Ro, -0.8), (Ro, 0.8), (Ro - 7, 0.8)))]
                    o += GE.prism(c, (0, 0, z0 - 2.5), (0, 0, 1), lp, 2.5, "w")
            o += GE.prism(c, (0, 0, z0), (0, 0, 1), [(-v, u, f) for u, v, f in outer], h, "dk",
                          holes=[[(-v, u, f) for u, v, f in inner]])
            o += lam_z(c, z0, z0 + h, Ro, 2.6)
            z = z0 + h
        # pressing fingers on the teeth, upper clamping plate
        for k in range(NS):
            a = (k + 0.5) * 360 / NS
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            lp = [(-(r * sa + t * ca), r * ca - t * sa, j) for j, (r, t) in enumerate(((Ri + 0.6, -0.9), (43, -0.9), (43, 0.9), (Ri + 0.6, 0.9)))]
            o += GE.prism(c, (0, 0, z), (0, 0, 1), lp, 1.6, "w")
        o += ringz(c, z + 1.6, 4, Ro, 42, "w")
        # key bars welded on the back of the stack
        kb = []
        for a in (210, 270, 330, 30):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            lp = [(-(r * sa + t * ca), r * ca - t * sa, j) for j, (r, t) in enumerate(((Ro - 0.5, -2.2), (Ro + 2.6, -2.2), (Ro + 2.6, 2.2), (Ro - 0.5, 2.2)))]
            kb.append((depth(c, (Ro * ca, Ro * sa, 30)), GE.prism(c, (0, 0, -4), (0, 0, 1), lp, z + 9.6, "w")))
        o += "".join(s_ for _, s_ in sorted(kb, key=lambda t: -t[0]))
        # one lamination lifted off the stack
        o += GE.prism(c, (0, 0, z + 34), (0, 0, 1), [(-v, u, f) for u, v, f in outer], 1.6, "dk",
                      holes=[[(-v, u, f) for u, v, f in inner]])
        return o
    s, c = fit(sc, -30, 36, (18, 8, 236, 184))
    # inset: open slot (form-wound coils) vs semi-closed slot (random-wound)
    s += panel(246, 112, 66, 72)
    for x0, mouth in ((250, None), (281, 2.4)):
        y0, sw, m = 120, 9, x0 + 13.5
        s += rect(x0, y0, 27, 56, "dk")
        s += hatch([(x0, y0), (x0 + 27, y0), (x0 + 27, y0 + 56), (x0, y0 + 56)], 4, 0, "gr")
        if mouth:
            sl = [(m - sw / 2, y0 + 10), (m + sw / 2, y0 + 10), (m + sw / 2, y0 + 47), (m + mouth / 2, y0 + 51), (m + mouth / 2, y0 + 56.5),
                  (m - mouth / 2, y0 + 56.5), (m - mouth / 2, y0 + 51), (m - sw / 2, y0 + 47)]
        else:
            sl = [(m - sw / 2, y0 + 8), (m + sw / 2, y0 + 8), (m + sw / 2, y0 + 56.5), (m - sw / 2, y0 + 56.5)]
        s += pg(sl, "void")
    return s


@part("generator.gencoil")
def _():
    Lh, Wh, E = 52, 25, 30

    def sc(c):
        bars = []

        def add(a, b, mat, w=4.2, h=9):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
            bars.append((depth(c, mid), seg3(c, a, b, w, h, mat, ext=1.6)))
        for sx in (-1, 1):
            xa, xn = sx * Lh, sx * (Lh + E)
            A, B = (xa, -Wh, 0), (xa, Wh, 10)
            N1, N2 = (xn, -3.5, 5), (xn, 3.5, 5)
            add(A, N1, "t")
            add(N1, N2, "t")
            add(N2, B, "t")
        for y, z in ((-Wh, 0), (Wh, 10)):                     # straight (slot) parts: grading tape + semiconductive tape
            add((-Lh, y, z), (-Lh + 9, y, z), "m")
            add((-Lh + 9, y, z), (Lh - 9, y, z), "dk")
            add((Lh - 9, y, z), (Lh, y, z), "m")
        bars.sort(key=lambda t: -t[0])
        o = "".join(s_ for _, s_ in bars)
        xn = Lh + E                                            # two leads out of one end
        for y in (-1.6, 1.6):
            o += seg3(c, (xn - 3, y, 8), (xn - 3, y, 26), 2.2, 2.2, "cu")
        return o
    s, c = fit(sc, -28, 34, (14, 22, 306, 176))
    # forming steps: wound oval loop -> spread into the diamond shape
    s += panel(186, 6, 126, 38)
    s += path("M198 25 a6 6 0 0 1 6 -6 h22 a6 6 0 0 1 0 12 h-22 a6 6 0 0 1 -6 -6Z", "coilcu")
    s += arrow(242, 25, 256, 25)
    s += path("M262 25 L272 16 L290 16 L300 25 L290 34 L272 34Z", "coilcu")
    # conductor cross-section of the slot part: strands, mica wall, semiconductive layer
    s += panel(8, 118, 76, 76)
    s += rect(18, 124, 56, 64, "rb", 5) + rect(21.5, 127.5, 49, 57, "t", 4)
    for col in range(2):
        for row in range(6):
            s += rect(29 + col * 17.5, 133 + row * 8, 16, 6.6, "cu", 0.8)
    return s


@part("generator.genwinding")
def _():
    Ro, Ri, Lc, NS = 50, 33, 92, 36
    inner = slot_hole(Ri, NS, 9, 3.2)

    def ends(c, x0, sgn, front):
        """basket of coil ends leaving the core at x0 toward sgn (+1 / -1)."""
        items = []
        for k in range(24):
            a = k * 15
            for lay, (r0, r1, tw, var) in enumerate(((Ri + 2.5, Ri + 9, 26, "--cu4"), (Ri + 6.5, Ri + 13, -26, "--cu3"))):
                ps3 = [(x0 + sgn * 15 * t, ) + yz(r0 + (r1 - r0) * math.sin(t * math.pi / 2), a + tw * t) for t in (0, .33, .67, 1)]
                d = sum(depth(c, p) for p in ps3) / 4
                items.append((d, lay, [c.xy(p) for p in ps3], var))
        items.sort(key=lambda t: (-t[0]))
        n_ = len(items)
        sel = items[:n_ // 2] if not front else items[n_ // 2:]
        return "".join(stroke(ps, var, 3.2, edge=front or sgn > 0) for _, _, ps, var in sel)

    def sc(c):
        o = ends(c, 0, -1, False) + ends(c, 0, -1, True)
        o += GE.prism(c, (0, 0, 0), (1, 0, 0), circ_o(Ro, 48), Lc, "dk", holes=[inner]) + lam_x(c, 0, Lc, Ro, 4.6)
        # coil sides and wedges in the slots, seen on the end face
        for k in range(NS):
            a = k * 360 / NS
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))

            def q(r0, r1, t, cl):
                return quad(c, [(Lc + 0.2, r * ca - tt * sa, r * sa + tt * ca) for r, tt in ((r0, -t), (r1, -t), (r1, t), (r0, t))], cl)
            o += q(Ri + 5.2, Ri + 8.6, 1.5, "cu") + q(Ri + 1.4, Ri + 4.8, 1.5, "cu") + q(Ri + 0.2, Ri + 1.2, 1.6, "pcb")
        # wedges along the bore (seen through the near opening)
        wl = ""
        for k in range(NS):
            a = k * 360 / NS
            if -120 < ((a + 180) % 360) - 180 < 66:
                wl += path(P([c.xy((x,) + yz(Ri + 0.3, a)) for x in (0, Lc)], False), "o thin")
        o += clip("pw2-wind-bore", xarc(c, Lc, Ri, 0, 360, 40), wl)
        o += ends(c, Lc, 1, False)
        o += path(P(xarc(c, Lc + 13, Ri + 12.5, 0, 360, 48)), "o").replace('class="o"', 'style="fill:none;stroke:var(--ts3);stroke-width:3.4"')
        o += ends(c, Lc, 1, True)
        for a in (100, 160, 220, 280, 340, 40):                  # cord ties
            o += stroke([c.xy((Lc + 9,) + yz(Ri + 8, a)), c.xy((Lc + 9,) + yz(Ri + 15, a + 3))], "--gs2", 1.6)
        # lead bundle
        for i in range(3):
            p0 = c.xy((Lc + 8, ) + yz(Ri + 14, 96 + i * 8))
            o += path(smooth_d([p0, (p0[0] + 6, p0[1] - 16), (p0[0] + 22 - i * 3, p0[1] - 26 + i * 2)]), "cable")
        return o
    s, c = fit(sc, -36, 20, (10, 16, 222, 184))
    # VPI tank: vacuum -> resin in -> pressure
    s += panel(230, 6, 82, 92)
    s += vcyl(270, 26, 50, 16, 5, "w", "w2") + ell(270, 26, 16, 5, "w3") + rect(264, 52, 12, 18, "dk", 2)
    s += rect(257, 76, 26, 6, "resin")
    s += circ(242, 40, 7, "m2") + circ(242, 40, 3, "m3") + vcyl(300, 52, 26, 8, 3, "resin", "w2")
    s += path("M249 40 L254 40 L254 30 L258 30", "pipe") + path("M300 50 L300 44 L292 44 L292 66 L286 66", "pipe")
    s += arrow(256, 36, 246, 36) + flow([(296, 58), (290, 60), (284, 70)], "fuel", 1.6, 4.5)
    s += arrow(270, 10, 270, 19)
    # slot sections: low-voltage random winding / high-voltage form-wound coils
    s += panel(230, 104, 82, 90)
    for x0, hv in ((236, False), (274, True)):
        s += rect(x0, 112, 32, 74, "dk")
        s += rect(x0 + 9, 116, 14, 66, "void")
        if hv:
            s += rect(x0 + 9.5, 118, 13, 28, "cu", 1) + rect(x0 + 9.5, 148, 13, 2.5, "gw") + rect(x0 + 9.5, 151.5, 13, 26, "cu", 1)
            s += rect(x0 + 11.5, 120, 9, 24, "o thin") + rect(x0 + 11.5, 153.5, 9, 22, "o thin")
        else:
            s += path("M%s 116 L%s 177 L%s 177 L%s 116" % (n(x0 + 9.4), n(x0 + 9.4), n(x0 + 22.6), n(x0 + 22.6)), "o").replace('class="o"', 'style="fill:none;stroke:var(--gs2);stroke-width:1.4"')
            for j in range(30):
                s += circ(x0 + 12 + (j % 3) * 4 + (1 if (j // 3) % 2 else 0), 119.5 + (j // 3) * 5.6, 1.9, "cu")
        s += rect(x0 + 9, 177.5, 14, 4, "pcb")
    return s


# ---- salient-pole rotor (4 poles): union section of iron + field coils, shared by genrotor / genassy
POLE = dict(a=16, bw=6, cw=12, rs=24, rt=27, ht=13.5)


def pole_outline(phi0=20.0, k=1.0):
    """CCW outline (u=y, v=z, fid) of the 4-pole section; fids 100p+i, copper on coil faces."""
    g = POLE
    out = []
    cu = set()
    for p in range(4):
        ph = math.radians(phi0 + 90 * p)
        er, et = (math.cos(ph), math.sin(ph)), (-math.sin(ph), math.cos(ph))
        loc = [(g["a"], -g["a"]), (g["a"], -g["cw"]), (g["rs"], -g["cw"]), (g["rs"], -g["ht"]), (g["rt"], -g["ht"])]
        R_ = math.hypot(g["rt"], g["ht"])
        a0 = math.atan2(g["ht"], g["rt"])
        loc += [(R_ * math.cos(a0 * (1 - 2 * j / 6)), -R_ * math.sin(a0 * (1 - 2 * j / 6))) for j in range(1, 6)]
        loc += [(g["rt"], g["ht"]), (g["rs"], g["ht"]), (g["rs"], g["cw"]), (g["a"], g["cw"])]
        for i, (r, t) in enumerate(loc):
            f = p * 100 + i
            if i in (1, len(loc) - 2):
                cu.add(f)
            out.append(((r * er[0] + t * et[0]) * k, (r * er[1] + t * et[1]) * k, f))
    return out, cu


def pole_local(phi, r, t, k=1.0):
    ph = math.radians(phi)
    return ((r * math.cos(ph) - t * math.sin(ph)) * k, (r * math.sin(ph) + t * math.cos(ph)) * k)


def rotor_body(c, x0, Lc, phi0=20.0, k=1.0, bars=True):
    """salient-pole rotor core along x (x0..x0+Lc) with field-coil end turns and damper-bar ends."""
    ol, cu = pole_outline(phi0, k)
    g = POLE

    def endturns(xa):
        its = []
        for p in range(4):
            ph = phi0 + 90 * p
            lp = [pole_local(ph, r, t, k) + (j,) for j, (r, t) in enumerate(((g["a"] + .4, -g["cw"]), (g["rs"] - .4, -g["cw"]), (g["rs"] - .4, g["cw"]), (g["a"] + .4, g["cw"])))]
            yy, zz = pole_local(ph, 20, 0, k)
            its.append((depth(c, (xa + 2.5 * k, yy, zz)), GE.prism(c, (xa, 0, 0), (1, 0, 0), lp, 5 * k, "cu")))
        its.sort(key=lambda t: -t[0])
        return "".join(s_ for _, s_ in its)
    o = endturns(x0 - 5 * k)
    o += GE.prism(c, (x0, 0, 0), (1, 0, 0), ol, Lc, "dk", fid_mat=lambda f: "cu" if f in cu else "dk", grooves=7)
    o += endturns(x0 + Lc)
    if bars:
        its = []
        for p in range(4):
            for t in (-10, -5, 0, 5, 10):
                yy, zz = pole_local(phi0 + 90 * p, 28.3 - abs(t) * 0.06, t, k)
                its.append((depth(c, (x0 + Lc, yy, zz)), pg(c3(c, (x0 + Lc + 1.2 * k, yy, zz), (1, 0, 0), 1.15 * k, seg=10), "cu")))
        its.sort(key=lambda t: -t[0])
        o += "".join(s_ for _, s_ in its)
    return o


def slot_outer(ro, ns, sd, sw, f0=0):
    out = []
    step = 360.0 / ns
    for k in range(ns):
        a = k * step
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        for i, (r, t) in enumerate(((ro, -step * math.pi / 180 * ro / 2 + 0.01), (ro, -sw / 2), (ro - sd, -sw / 2), (ro - sd, sw / 2), (ro, sw / 2))):
            out.append((r * ca - t * sa, r * sa + t * ca, f0 + k * 5 + i))
    return out


@part("generator.genrotor")
def _():
    def sc(c):
        o = ""
        # engine side: coupling disc pack (bolt circle) and hub
        for i in range(5):
            o += ringx(c, -50 + i * 1.7, 1.0, 33, 9, "w", seg=36)
        for k in range(12):
            o += hole(c, (-41.4, ) + yz(28.5, k * 30 + 15), (1, 0, 0), 1.4, seg=10)
        o += ringx(c, -41.5, 10, 12, 0, "w")
        # radial cooling fan (aluminium)
        o += ringx(c, -26, 1.6, 29, 0, "alu")
        fan = []
        for k in range(14):
            a = k * 360 / 14
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            fan += [(10 * ca - 1 * sa, 10 * sa + 1 * ca, 4 * k), (28 * ca - 1 * sa, 28 * sa + 1 * ca, 4 * k + 1),
                    (28 * ca + 1 * sa, 28 * sa - 1 * ca, 4 * k + 2), (10 * math.cos(math.radians(a + 360 / 14 - 4)), 10 * math.sin(math.radians(a + 360 / 14 - 4)), 4 * k + 3)]
        o += GE.prism(c, (-24.4, 0, 0), (1, 0, 0), fan, 7, "alu")
        o += ringx(c, -31.5, 24, 10.5, 0, "w")
        o += rotor_body(c, 0, 72)
        # anti-drive end: shaft, bearing journal, exciter armature, rotating rectifier
        o += ringx(c, 72, 14, 10, 0, "w") + ringx(c, 86, 13, 8.6, 0, "m") + ringx(c, 99, 8, 7.8, 0, "w")
        o += ringx(c, 106, 2.5, 13.5, 7, "cu")
        o += GE.prism(c, (108.5, 0, 0), (1, 0, 0), slot_outer(16.5, 24, 3, 1.6), 12, "dk", holes=[circ_o(7.8, 24, 40)], grooves=5)
        o += ringx(c, 120.5, 2.5, 13.5, 7, "cu")
        o += ringx(c, 123, 5, 7.6, 0, "w")
        o += ringx(c, 128, 3, 18, 7, "alu") + ringx(c, 131, 2, 14, 7, "alu")
        for k in range(6):
            a = k * 60 + 30
            hx = [(1.9 * math.cos(math.radians(j * 60)), 1.9 * math.sin(math.radians(j * 60)), j) for j in range(6)]
            y0, z0 = yz(15.8 if k % 2 else 11.3, a)
            o += GE.prism(c, (133, 0, 0), (1, 0, 0), [(u + y0, v + z0, f) for u, v, f in hx], 2.6, "dk")
        o += ringx(c, 133, 7, 5.6, 0, "w")
        return o
    s, c = fit(sc, -22, 17, (70, 8, 314, 156), shy=8)
    # section: four salient poles, field coils, damper bars, interpolar wedges; N/S as flux arrows
    cx, cy, k = 46, 154, 1.1
    s += panel(6, 116, 80, 78)
    ol, cu = pole_outline(45, k)
    s += pg([(cx + u, cy - v) for u, v, _ in ol], "dk")
    g = POLE
    for p in range(4):
        ph = 45 + 90 * p
        for sgn in (-1, 1):
            q = [pole_local(ph, r, t * sgn, k) for r, t in ((g["a"], g["bw"]), (g["rs"], g["bw"]), (g["rs"], g["cw"]), (g["a"], g["cw"]))]
            s += pg([(cx + u, cy - v) for u, v in q], "cu")
            for j in range(3):
                y1 = g["a"] + (j + 1) * (g["rs"] - g["a"]) / 4
                a_, b_ = pole_local(ph, y1, g["bw"] * sgn, k), pole_local(ph, y1, g["cw"] * sgn, k)
                s += line(cx + a_[0], cy - a_[1], cx + b_[0], cy - b_[1], "o thin")
        for t in (-10, -5, 0, 5, 10):
            u, v = pole_local(ph, 28.3 - abs(t) * 0.06, t, k)
            s += circ(cx + u, cy - v, 1.3, "cu")
        u, v = pole_local(ph + 45, 23.2, 0, k)
        s += pg([(cx + u + 2.6 * math.cos(math.radians(ph + 45 + d)), cy - v - 2.6 * math.sin(math.radians(ph + 45 + d))) for d in (0, 90, 180, 270)], "m")
        r0, r1 = (15, 29) if p % 2 == 0 else (29, 15)
        a_, b_ = pole_local(ph, r0, 0, k), pole_local(ph, r1, 0, k)
        s += arrow(cx + a_[0], cy - a_[1], cx + b_[0], cy - b_[1])
    s += circ(cx, cy, 8 * k, "w") + circ(cx, cy, 8 * k, "o")
    return s


@part("generator.genshaft")
def _():
    segs = [(6, 14, "w"), (20, 10.5, "w"), (104, 12.5, "w"), (8, 11, "w"), (22, 9, "m"), (40, 7.5, "w"), (30, 5.5, "w")]

    def sc(c):
        o = ""
        x = 0
        for L, r, m in segs:
            o += ringx(c, x, L, r, 0, m, seg=56)
            if L == 104:                                          # key ways on the core seat
                for a in (118, ):
                    ps = [(x + 14, a - 6), (x + L - 14, a - 6), (x + L - 14, a + 6), (x + 14, a + 6)]
                    o += quad(c, [(px, ) + yz(r + 0.05, pa) for px, pa in ps], "bg")
            x += L
        for k in range(8):                                        # coupling bolt holes + centre hole
            o += hole(c, (-0.05, ) + yz(10.6, k * 45 + 22.5), (1, 0, 0), 1.5, seg=10)
        o += hole(c, (-0.05, 0, 0), (1, 0, 0), 2.6, "m3", seg=14) + hole(c, (-0.1, 0, 0), (1, 0, 0), 1.1, "bg", seg=10)
        return o
    s, c = fit(sc, 22, 16, (12, 66, 308, 178), shy=7)
    # forging: billet -> open-die forged stepped blank -> finished shaft
    s += panel(70, 6, 180, 44)
    s += rect(80, 16, 26, 24, "h", 4)
    s += arrow(110, 28, 122, 28)
    s += path("M126 22 L134 22 L134 20 L164 20 L164 23 L176 23 L176 25 L186 25 L186 31 L176 31 L176 33 L164 33 L164 36 L134 36 L134 34 L126 34Z", "h")
    s += arrow(190, 28, 202, 28)
    s += path("M206 24 L208 24 L208 25.5 L226 25.5 L226 26 L234 26 L234 27 L244 27 L244 29 L234 29 L234 30 L226 30 L226 30.5 L208 30.5 L208 32 L206 32Z", "w")
    return s


@part("generator.genexciter")
def _():
    def sc(c):
        o = ""
        # exciter field (stationary): ring with inward salient poles and field coils
        hole_ = []
        for p in range(10):
            ph = p * 36
            for j, (r, t) in enumerate(((26, -2.6), (19.5, -2.6), (19.5, -4.4), (16.5, -4.4), (16.5, 4.4), (19.5, 4.4), (19.5, 2.6), (26, 2.6))):
                hole_.append(pole_local(ph, r, t) + (p * 20 + j,))
            for j in range(1, 4):
                a = ph + 6 + 24 * j / 4
                hole_.append(yz(26, a) + (p * 20 + 10,))
        o += GE.prism(c, (0, 0, 0), (1, 0, 0), circ_o(34, 56), 10, "w", holes=[hole_], grooves=4)
        cs = []
        for p in range(10):
            ph = p * 36
            lp = [pole_local(ph, r, t) + (j,) for j, (r, t) in enumerate(((20, -5.2), (25.4, -5.2), (25.4, 5.2), (20, 5.2)))]
            yy, zz = pole_local(ph, 22, 0)
            cs.append((depth(c, (11, yy, zz)), GE.prism(c, (10, 0, 0), (1, 0, 0), lp, 2.6, "cu")))
        o += "".join(s_ for _, s_ in sorted(cs, key=lambda t: -t[0]))
        o += path(P([c.xy((x, 0, 0)) for x in (-6, 104)], False), "o thin dash")
        # armature (rotating): slotted core + three-phase coil ends
        o += ringx(c, 32, 2.6, 13.8, 6, "cu")
        o += GE.prism(c, (34.6, 0, 0), (1, 0, 0), slot_outer(15, 24, 3, 1.6), 11, "dk", holes=[circ_o(6, 24, 40)], grooves=5)
        o += ringx(c, 45.6, 2.6, 13.8, 6, "cu")
        # rotating rectifier: finned aluminium hub, + and - plates with three diodes each, varistor
        o += ringx(c, 62, 4, 18, 5, "alu", grooves=3) + ringx(c, 66, 2, 15.5, 5, "alu")
        for a0, a1 in ((14, 166), (194, 346)):
            o += ringx(c, 68, 2.4, 15, 8, "alu", a0, a1, 24)
        ds = []
        for k in range(6):
            a = 30 + k * 26 if k < 3 else 210 + (k - 3) * 26 + 4
            y0, z0 = yz(11.6, a + 10)
            hx = [(1.9 * math.cos(math.radians(j * 60)) + y0, 1.9 * math.sin(math.radians(j * 60)) + z0, j) for j in range(6)]
            ds.append(GE.prism(c, (70.4, 0, 0), (1, 0, 0), hx, 2.2, "dk") + GE.cyl(c, (72.6, y0, z0), (1, 0, 0), 0.9, 2.2, "m", seg=10))
        o += "".join(ds)
        y0, z0 = yz(12, 180)
        o += GE.cyl(c, (70.4, y0, z0), (1, 0, 0), 3, 1.4, "dk", seg=16)
        # optional PMG at the shaft end (model dependent)
        o += path(P(xarc(c, 92, 13, 0, 360, 32)), "hid") + path(P(xarc(c, 100, 13, 0, 360, 32)), "hid")
        return o
    s, c = fit(sc, -40, 16, (10, 4, 262, 132), shy=6)
    # AVR: box with the circuit board seen through
    s += box(262, 78, 40, 34, 18, "dk", "dk", "dk")
    s += rect(266, 82, 32, 26, "pcb", 2)
    for i in range(4):
        s += rect(269 + i * 7, 86, 5, 4, "rb") + rect(269 + i * 7, 96, 4, 6, "cu")
    # block diagram: stationary (blue band) / rotating (warm band)
    s += rect(8, 140, 84, 54, "coolin", 6) + rect(96, 140, 128, 54, "warmin", 6) + rect(228, 140, 84, 54, "coolin", 6)
    s += rect(20, 152, 26, 20, "dk", 2) + rect(23, 155, 20, 14, "pcb", 1)          # AVR
    s += path("M60 162 c0 -10 6 -10 6 0 c0 -10 6 -10 6 0 c0 -10 6 -10 6 0", "coilcu")   # exciter field
    for i in range(3):                                                             # armature: 3-phase AC
        s += path("M102 %s q4 -6 8 0 t8 0 t8 0" % n(154 + i * 8), "o")
    for i in range(3):                                                             # diode bridge
        for j, yy in enumerate((154, 170)):
            x = 140 + i * 12
            s += poly([(x - 3.5, yy - 3), (x + 3.5, yy - 3), (x, yy + 3)], "d") + line(x - 3.5, yy + 3, x + 3.5, yy + 3, "o")
        s += line(140 + i * 12, 151, 140 + i * 12, 173, "o thin")
    s += path("M186 162 c0 -10 6 -10 6 0 c0 -10 6 -10 6 0 c0 -10 6 -10 6 0", "coilcu")   # main field
    s += circ(252, 162, 12, "void") + circ(252, 162, 12, "o") + path("M243 162 q4.5 -7 9 0 t9 0", "o")   # main armature
    s += arrow(48, 162, 58, 162) + arrow(80, 162, 98, 162) + arrow(128, 162, 136, 162) + arrow(166, 162, 184, 162) + arrow(206, 162, 238, 162)
    s += arrow(266, 162, 304, 162)
    s += path("M284 162 L284 186 L33 186 L33 176", "a") + head(33, 173, -math.pi / 2)
    return s


@part("generator.genassy")
def _():
    L, R, Ri = 100, 50, 46

    def sc(c):
        o = ""
        # engine-side adapter (cone) and back foot
        o += boxp(c, 2, 32, -56, L - 4, 16, 6, "w") + boxp(c, 6, 38.4, -50, L - 12, 3.2, 20, "w")
        o += GE.prism(c, (-16, 0, 0), (1, 0, 0), circ_o(60, 56), 16, "w", holes=[circ_o(55, 56, 40)], smooth=True,
                      scale=lambda t: 1 - t * (1 - 50.5 / 60))
        o += ringx(c, -19, 3, 63, 55, "w")
        # frame with the upper-front quarter cut away
        o += ringx(c, 0, L, R, Ri, "w", 180, 450)
        inner = ""
        inner += ringx(c, 4, 10, 44, 35, "cu", 180, 450, dark=1)                    # far coil end
        inner += ringx(c, 14, 72, Ri, 33, "dk", 270, 450, grooves=8)                 # core (back part)
        inner += ringx(c, -20, 150, 8, 0, "w")                                      # shaft
        inner += rotor_body(c, 14, 72, 20, 1.0, bars=False)
        inner += ringx(c, 14, 72, Ri, 33, "dk", 180, 270, grooves=8)                 # core (front part)
        inner += ringx(c, 86, 10, 44, 35, "cu", 180, 450, dark=1)                   # near coil end
        for x in (88.5, 91, 93.5):
            inner += path(P(xarc(c, x, 44.1, 175, 452, 30), False), "o thin")
        ps = [c.xy((0, -Ri, 0))] + xarc(c, L, Ri, 180, 90, 10) + xarc(c, 0, Ri, 90, 180, 10)
        o += clip("pw2-assy-in", ps, inner)
        # air gap (exaggerated): arrows at the bore
        for r0, r1 in ((20, 30.2), (42, 33)):
            a_, b_ = c.xy((87, ) + yz(r0, 112)), c.xy((87, ) + yz(r1, 112))
            o += arrow(a_[0], a_[1], b_[0], b_[1])
        # anti-drive end bracket with bearing housing, exciter and rotating rectifier
        o += ringx(c, L, 5, R + 1, 0, "w") + ringx(c, L + 5, 8, 15, 0, "w") + ringx(c, L + 13, 8, 18, 0, "w")
        for a in (200, 245, 290, 335, 20):
            q = [(L + 5.1, ) + pole_local(a, r, t) for r, t in ((32, -6), (44, -6), (44, 6), (32, 6))]
            o += quad(c, q, "bg")
        o += ringx(c, L + 21, 3, 15, 0, "cu") + ringx(c, L + 24, 9, 17, 0, "dk", grooves=4) + ringx(c, L + 33, 3, 15, 0, "cu")
        o += ringx(c, L + 38, 3, 16, 0, "alu") + ringx(c, L + 41, 6, 6, 0, "w")
        # terminal box with three main terminals + neutral, lifting lugs, front foot
        o += boxp(c, 30, 2, 44, 32, 24, 18, "w")
        for i in range(4):
            o += GE.cyl(c, (35 + i * 7.5, 12, 62), (0, 0, 1), 2.2, 5, "gw", seg=12) + GE.cyl(c, (35 + i * 7.5, 12, 67), (0, 0, 1), 1, 3, "cu", seg=10)
        o += boxp(c, 2, -48, -56, L - 4, 16, 6, "w") + boxp(c, 6, -41.6, -50, L - 12, 3.2, 20, "w")
        for x in (10, L / 2, L - 10):
            o += hole(c, (x, -44, -50), (0, 0, 1), 2.2)
        return o
    s, c = fit(sc, -32, 22, (8, 6, 250, 160), shy=8)
    # factory test: drive motor -> test bearing pedestal -> generator -> load bank + metering
    s += panel(186, 150, 126, 44)
    s += rect(192, 164, 18, 14, "dk", 3) + rect(214, 166, 10, 12, "w") + line(208, 171, 232, 171, "o")
    s += rect(230, 162, 22, 18, "w", 4) + path("M252 171 L262 171", "cable")
    s += rect(262, 158, 22, 26, "m2", 2)
    for i in range(4):
        s += line(265, 162 + i * 5, 281, 162 + i * 5, "o thin")
    s += rect(288, 160, 18, 22, "m", 2) + circ(297, 167, 4, "w2") + rect(292, 174, 10, 4, "pcb")
    s += path("M284 170 L288 170", "cable")
    return s


# =====================================================================================
# gasgen: gas turbine / gas engine
# =====================================================================================
def airfoil(ch, th, cb, nn=10):
    """closed airfoil loop (x along chord, centred at 40 % chord; y: suction side +)."""
    up, lo = [], []
    for i in range(nn + 1):
        s_ = (1 - math.cos(math.pi * i / nn)) / 2
        yc = cb * 4 * s_ * (1 - s_) * ch
        t = 5 * th * ch * (0.2969 * math.sqrt(s_) - 0.126 * s_ - 0.3516 * s_ ** 2 + 0.2843 * s_ ** 3 - 0.1036 * s_ ** 4) + 0.15
        x = (s_ - 0.4) * ch
        up.append((x, yc + t))
        lo.append((x, yc - t))
    return up + lo[::-1][1:-1]


def af_point(ch, th, cb, s_, side):
    yc = cb * 4 * s_ * (1 - s_) * ch
    t = 5 * th * ch * (0.2969 * math.sqrt(s_) - 0.126 * s_ - 0.3516 * s_ ** 2 + 0.2843 * s_ ** 3 - 0.1036 * s_ ** 4) + 0.15
    return ((s_ - 0.4) * ch, yc + side * t)


def rotxy(p, g):
    cg, sg = math.cos(math.radians(g)), math.sin(math.radians(g))
    return (p[0] * cg - p[1] * sg, p[0] * sg + p[1] * cg)


def blade_secs(ch, th, cb, H, g0, g1, x0=0, y0=0, z0=0, ns=6, taper=1.0, nn=10):
    secs = []
    for j in range(ns + 1):
        f = j / ns
        k = 1 - (1 - taper) * f
        g = g0 + (g1 - g0) * f
        secs.append([(x0 + q[0], y0 + q[1], z0 + H * f) for q in (rotxy((u * k, v * k), g) for u, v in airfoil(ch, th, cb, nn))])
    return secs


def comp_blade(c, ch, H, x0=0, y0=0, root=True):
    """compressor rotor blade: twisted thin airfoil, platform, axial dovetail root."""
    o = ""
    if root:
        o += GE.prism(c, (x0 - 0.5 * ch, y0, 0), (1, 0, 0), [(-0.16 * ch, -0.05 * ch, 0), (0.16 * ch, -0.05 * ch, 1), (0.3 * ch, -0.36 * ch, 2), (-0.3 * ch, -0.36 * ch, 3)], ch, "w")
    o += boxp(c, x0 - 0.56 * ch, y0 - 0.42 * ch, -0.06 * ch, 1.12 * ch, 0.84 * ch, 0.06 * ch, "w")
    o += loft(c, blade_secs(ch, 0.075, 0.08, H, 8, -28, x0, y0, 0, 6, 0.9), "w")
    return o


@part("gasgen.gtcomp")
def _():
    s, c = fit(lambda c: comp_blade(c, 26, 78), -30, 24, (10, 8, 150, 190), shy=6)
    # rear-stage blade (about 1/5 of the front stage), drawn at the same scale
    c2 = RCam(178, 150, -30, 24, c.s)
    s += shadow(178, 166, 24, 4) + comp_blade(c2, 10, 16)
    # stator vane: short untwisted airfoil with an outer T-hook and an inner foot
    c3_ = RCam(250, 132, -30, 24, c.s * 0.95)
    v = boxp(c3_, -9, -5, -3, 18, 10, 3, "w")
    v += loft(c3_, blade_secs(16, 0.08, 0.1, 40, 16, 16, 0, 0, 0, 2), "w")
    v += boxp(c3_, -7, -4, 40, 14, 8, 4, "w") + boxp(c3_, -11, -6, 44, 22, 12, 3, "w")
    s += shadow(250, 138, 22, 4) + v
    # sections at root / mid / tip, stacked: the stagger turns with height
    s += panel(196, 150, 116, 44)
    for g, cl in ((8, "w3"), (-10, "w2"), (-28, "w")):
        s += pg([(256 + p[0] * 2.6, 172 - p[1] * 2.6) for p in (rotxy(q, g) for q in airfoil(26, 0.075, 0.08, 12))], cl)
    return s


@part("gasgen.gtblade")
def _():
    ch, H = 30, 46
    th, cb = 0.18, 0.14
    fir = [(4, -14), (7.4, -16.8), (4.8, -19.2), (6.6, -21.6), (4.2, -24), (5.8, -26.4), (3.6, -28.8), (2.6, -31)]
    fir_loop = [(y, z, i) for i, (y, z) in enumerate(fir)] + [(-y, z, 20 + i) for i, (y, z) in enumerate(fir[::-1])]
    holes_ = []

    def sc(c):
        o = GE.prism(c, (-0.42 * ch, 0, 0), (1, 0, 0), fir_loop, 0.84 * ch, "w")              # fir-tree root
        o += boxp(c, -0.36 * ch, -3.2, -14, 0.72 * ch, 6.4, 11, "w")                          # shank
        o += boxp(c, -0.56 * ch, -0.42 * ch, -3, 1.12 * ch, 0.84 * ch, 3, "w", cap_mat="gw")  # platform, coated top
        secs = blade_secs(ch, th, cb, H, 14, 6, 0, 0, 0, 5, 0.94, 12)
        o += loft(c, secs, "gw")
        # cooling holes: leading-edge showerhead, pressure-side rows, trailing-edge slots, tip holes
        D = c.D
        for z in range(6, H - 2, 4):
            f = z / H
            g = 14 - 8 * f
            k = 1 - 0.06 * f
            for s_, side, r in ((0.004, -1, 0.75), (0.03, -1, 0.75), (0.03, 1, 0.75), (0.3, -1, 0.7), (0.5, -1, 0.7)):
                p = rotxy(tuple(v * k for v in af_point(ch, th, cb, s_, side)), g)
                nrm = rotxy((0, side), g)
                if s_ < 0.01:
                    nrm = rotxy((-1, 0), g)
                if nrm[0] * D[0] + nrm[1] * D[1] < 0.05:
                    q = c.xy((p[0], p[1], z))
                    o += circ(q[0], q[1], r * c.s * 0.6, "bg")
            if z < H - 4:
                a_ = c.xy(rotxy(tuple(v * k for v in af_point(ch, th, cb, 0.93, -1)), g) + (z,))
                b_ = c.xy(rotxy(tuple(v * k for v in af_point(ch, th, cb, 0.93, -1)), g) + (z + 2.4,))
                o += line(a_[0], a_[1], b_[0], b_[1], "kerf")
        for s_ in (0.2, 0.45, 0.7):
            p = rotxy(tuple(v * 0.94 for v in af_point(ch, th, cb, s_, 0)), 6)
            q = c.xy(p + (H,))
            o += circ(q[0], q[1], 0.5 * c.s, "bg")
        holes_.append(c.xy(rotxy(tuple(v * 0.97 for v in af_point(ch, th, cb, 0.55, -1)), 10) + (H * 0.55,)))
        return o
    s, c = fit(sc, -46, 22, (6, 8, 178, 192), shy=6)
    # longitudinal section: serpentine cooling passages with turbulators
    s += panel(184, 6, 70, 124)
    out = [(196, 18), (240, 14), (246, 70), (192, 70)]
    s += pg(out, "gw") + pg([(197, 20), (239, 16.5), (244.5, 69), (193.5, 69)], "w")
    s += rect(186, 70, 64, 4, "w") + rect(202, 74, 32, 16, "w")
    s += pg([(202, 90)] + [(218 + x * (1 if i < 8 else -1), y) for i, (x, y) in enumerate([(16, 90), (19, 94), (16, 98), (18.5, 102), (15.5, 106), (17.5, 110), (14.5, 114), (13, 118)] + [(13, 118), (14.5, 114), (17.5, 110), (15.5, 106), (18.5, 102), (16, 98), (19, 94), (16, 90)])][1:], "w")
    for x0, x1 in ((199, 210), (213, 224), (227, 238)):
        s += rect(x0, 21, x1 - x0, 46, "coolin")
        for y in range(26, 64, 6):
            s += line(x0 + 1, y + 2, x1 - 1, y - 1, "o thin")
    s += rect(199, 21, 25, 4, "coolin") + rect(213, 63, 25, 4, "coolin")
    s += rect(204, 67, 6, 50, "coolin")
    s += flow([(207, 124), (207, 96), (205, 60), (205, 28)], "air", 1.6, 4.5)
    s += flow([(214, 24), (218, 30), (218, 58)], "air", 1.6, 4.5) + flow([(228, 62), (233, 40), (234, 26)], "air", 1.6, 4.5)
    for y in (26, 38, 50, 62):
        s += flow([(239, y), (250, y - 1)], "air", 1.2, 3.5)
    for y in (30, 46):
        s += flow([(198, y), (188, y - 2)], "air", 1.2, 3.5)
    # coating build-up (lens): substrate / bond coat / columnar ceramic top coat
    if holes_:
        hx, hy = holes_[-1]
        s += lens(286, 52, 24, hx, hy)
        body = rect(262, 60, 48, 20, "w") + rect(262, 56, 48, 4, "m2") + rect(262, 40, 48, 16, "gw")
        for x in range(264, 310, 4):
            body += line(x, 41, x + 0.6, 55, "o thin")
        body += rect(262, 26, 48, 14, "hotband")
        s += clipc("pw2-blade-tbc", 286, 52, 24, body) + circ(286, 52, 24, "o")
    # grain structures: equiaxed / directionally solidified / single crystal
    s += panel(184, 136, 128, 58)
    for i in range(3):
        x0, y0 = 190 + i * 41, 142
        s += rect(x0, y0, 36, 46, "w", 2)
        if i == 0:
            d = ""
            for r in range(4):
                for k in range(3):
                    xx = x0 + 6 + k * 12 + (3 if r % 2 else 0) + 2 * math.sin(r * 3.1 + k * 1.7)
                    yy = y0 + 6 + r * 11 + 2 * math.cos(r * 2.3 + k * 2.9)
                    d += "M%s %s l%s %s l%s %s M%s %s l%s %s" % (n(xx), n(yy), n(7), n(3), n(1), n(7), n(xx), n(yy), n(-5), n(5))
            s += path(d, "o thin")
        elif i == 1:
            for k in range(1, 6):
                xx = x0 + k * 6
                s += path("M%s %s q2 12 0 23 q-2 12 1 23" % (n(xx + math.sin(k) * 1.5), n(y0)), "o thin")
    return s


def firtree_slot(R, k, a, w=1.0):
    """fir-tree slot notch (local r, t) points for slot k at angle a (deg)."""
    loc = [(R, -1.9), (R - 1.6, -1.9), (R - 2.8, -3.1), (R - 4.2, -1.7), (R - 5.4, -2.7), (R - 6.8, -1.4), (R - 7.8, -2.0), (R - 9.2, 0)]
    loc = loc + [(r, -t) for r, t in loc[::-1][1:]]
    return [pole_local(a, r, t * w) for r, t in loc]


@part("gasgen.gtdisk")
def _():
    R, NS = 60, 48

    def sc(c):
        ol = []
        for k in range(NS):
            a = k * 360 / NS
            for j, p in enumerate(firtree_slot(R, k, a)):
                ol.append(p + (k * 20 + j,))
            for j in range(1, 3):
                ol.append(yz(R, a + 360 / NS * j / 3) + (k * 20 + 18,))
        o = GE.prism(c, (0, 6, 0), (0, -1, 0), ol, 12, "w", holes=[circ_o(50, 64, 40)])
        hs = [GE.circle_outline(2.4, 14, 14, *yz(34, k * 30 + 15)) for k in range(12)]
        hs = [[(u, v, 200 + i * 20 + f) for u, v, f in h] for i, h in enumerate(hs)]
        o += GE.prism(c, (0, 2, 0), (0, -1, 0), circ_o(50.5, 64), 4, "w", holes=[circ_o(19, 40, 40)] + hs)
        o += GE.prism(c, (0, 7, 0), (0, -1, 0), circ_o(20, 48), 14, "w", holes=[circ_o(11, 40, 40)])
        for k in range(12):                                                 # cooling-air holes
            o += pg([c.xy((u, -2.05, v)) for u, v in [yz(44, k * 30 + d) for d in (-1.4, 1.4)]] +
                    [c.xy((u, -2.05, v)) for u, v in [yz(42, k * 30 + d) for d in (1.4, -1.4)]], "bg")
        return o

    s, c = fit(sc, -16, 12, (8, 8, 206, 192), shy=6)
    # half section from bore to rim (bone shape) with curvic coupling teeth
    s += panel(212, 6, 100, 92)
    prof = [(236, 92), (262, 92), (262, 76), (254, 70), (251, 60), (251, 34), (258, 28), (260, 12), (230, 12), (232, 28), (239, 34), (239, 60), (236, 70), (230, 76), (230, 92)]
    s += section(prof, "w", 3.0)
    s += line(220, 92, 306, 92, "cl")
    s += pg([(262, 78)] + [(262 + (3 if i % 2 == 0 else 0), 79 + i * 1.6) for i in range(9)] + [(262, 92)], "w")
    s += rect(242, 46, 6, 6, "void") + rect(242, 46, 6, 6, "o thin")
    # rim close-up: blade root locked in the fir-tree slot, centrifugal load outward
    cx, cy = 262, 150
    body = rect(cx - 50, cy - 10, 100, 60, "w")
    sl = [(cx + t * 4.2, cy + 10 - (60 - r) * 4.2) for r, t in [(60 + 0.1, -1.9)] + [(rr, tt) for rr, tt in [(60, -1.9), (58.4, -1.9), (57.2, -3.1), (55.8, -1.7), (54.6, -2.7), (53.2, -1.4), (52.2, -2.0), (50.8, 0)]] + [(rr, -tt) for rr, tt in [(52.2, -2.0), (53.2, -1.4), (54.6, -2.7), (55.8, -1.7), (57.2, -3.1), (58.4, -1.9), (60, -1.9)]]]
    root = [(x, y) for x, y in sl]
    body += pg(root, "w3") + rect(cx - 11, cy - 30, 22, 20, "w3") + rect(cx - 26, cy - 34, 52, 6, "gw")
    body += line(cx - 50, cy + 10, cx + 50, cy + 10, "o")
    s += lens(cx, cy, 40)
    s += clipc("pw2-disk-rim", cx, cy, 40, body) + circ(cx, cy, 40, "o")
    s += arrow(cx + 26, cy + 20, cx + 26, cy - 14)
    return s


@part("gasgen.gtcomb")
def _():
    X0, X1, X2 = 10, 86, 134            # liner start, transition-piece start, exit

    def tp_sec(t, x, nn=36):
        """transition piece section: circle (t=0) -> curved rectangular sector (t=1), shifted down."""
        e = t * t * (3 - 2 * t)
        r0 = 15.0
        out = []
        for k in range(nn):
            a = 2 * math.pi * k / nn
            ca, sa = math.cos(a), math.sin(a)
            rr = min(19.0 / max(abs(ca), 1e-6), 8.5 / max(abs(sa), 1e-6))
            y1, z1 = rr * ca, rr * sa - 0.012 * (rr * ca) ** 2 * 1.0
            y, z = (1 - e) * r0 * ca + e * y1, (1 - e) * r0 * sa + e * z1 - 9 * e
            out.append((x, y, z))
        return out

    def sc(c):
        o = ""
        fm = lambda f: "gw" if 40 <= f < 60 else "w"
        # head end: end cover, fuel nozzle with swirl vanes
        o += ringx(c, 0, 4, 22, 0, "w")
        o += ringx(c, 4, 5, 18.6, 0, "w", 180, 360)
        o += ringx(c, 4, 10, 4.2, 0, "m")
        vn = []
        for k in range(10):
            a = k * 36
            p = [c.xy((12.6, ) + yz(4.6, a)), c.xy((13.4, ) + yz(9.6, a + 18))]
            vn.append((depth(c, (13, ) + yz(7, a)), line(p[0][0], p[0][1], p[1][0], p[1][1], "o")))
        o += ringx(c, 11, 3, 10, 9.2, "m") + "".join(v for _, v in sorted(vn, key=lambda t: -t[0]))
        # liner: lower half (upper half cut away), coated inside
        o += GE.prism(c, (X0, 0, 0), (1, 0, 0), sector(18, 17, 180, 360, 36), 52, "w", fid_mat=fm, smooth=True)
        o += GE.prism(c, (X0 + 52, 0, 0), (1, 0, 0), sector(18, 17, 180, 360, 36), X1 - X0 - 52, "w", fid_mat=fm, smooth=True,
                      scale=lambda t: 1 - 0.17 * t)
        # flame from the nozzle
        fl = [c.xy((x, -w * 0.3, w)) for x, w in ((13, 3), (24, 7), (40, 9), (58, 8), (76, 5), (88, 0))]
        fl += [c.xy((x, w * 0.3, -w * 0.7)) for x, w in ((76, 5), (58, 8), (40, 9), (24, 7), (13, 3))]
        o += path(smooth_d(fl, True) + "Z", "h")
        # cooling holes (dots) and circumferential weld seams on the outside
        for x in range(X0 + 4, X1 - 2, 4):
            k = 1 - 0.17 * max(0, (x - X0 - 52) / (X1 - X0 - 52))
            for a in range(194, 266, 10):
                q = c.xy((x + (a // 10 % 2) * 2, ) + yz(18.1 * k, a))
                o += circ(q[0], q[1], 0.55 * c.s, "bg")
        for x in (X0 + 22, X0 + 44):
            o += path(P(xarc(c, x, 18.2, 180, 300, 16), False), "o")
        # transition piece (round -> sector-shaped exit) and exit frame
        secs = [tp_sec(j / 6, X1 + (X2 - X1) * j / 6) for j in range(7)]
        o += loft(c, secs, "w", cap=False)
        ex = [(x + 0.1, y * 1.18, (z + 9) * 1.4 - 9) for x, y, z in secs[-1]]
        o += loft(c, [secs[-1], [(X2, y, z) for _, y, z in ex], [(X2 + 3, y, z) for _, y, z in ex]], "w")
        o += pg([c.xy(p) for p in secs[-1]], "bg")
        o += path(P([c.xy(s_[27]) for s_ in secs], False), "o thin")                         # side weld seam
        # cooling air entering the wall holes
        for x in (30, 48, 66):
            a_, b_ = c.xy((x, ) + yz(30, 230)), c.xy((x, ) + yz(20, 230))
            o += flow([a_, b_], "air", 1.5, 4.5)
        return o
    s, c = fit(sc, -24, 30, (8, 22, 312, 186), shy=7)
    # can-annular layout seen along the shaft: cans around the turbine axis
    s += panel(8, 6, 66, 62)
    s += circ(41, 37, 26, "w3") + circ(41, 37, 22, "void") + circ(41, 37, 8, "w2")
    for k in range(10):
        a = math.radians(k * 36 - 90)
        s += circ(41 + 15 * math.cos(a), 37 + 15 * math.sin(a), 4.6, "w") + circ(41 + 15 * math.cos(a), 37 + 15 * math.sin(a), 2, "h")
    return s


@part("gasgen.gtcasing")
def _():
    L, ri0, t, fw, ft = 150, 40, 5, 12, 7
    sc_ = lambda u: 1 + 0.3 * u

    def half(top):
        """outline of one casing half with its horizontal joint flanges (u=y, v=z)."""
        ro = ri0 + t
        sg = 1 if top else -1
        out = [(-(ro + fw), 0, 0), (-(ro + fw), sg * ft, 1)]
        a0 = math.degrees(math.asin(ft / ro))
        rng = (180 + a0, 360 - a0) if not top else (180 - a0, a0)
        out += [(p[0], p[1], 10 + p[2]) for p in arcl(ro, rng[0], rng[1], 30)]
        out += [((ro + fw), sg * ft, 2), ((ro + fw), 0, 3), (ri0, 0, 4)]
        rng2 = (360, 180) if not top else (0, 180)
        out += [(p[0], p[1], 40 + p[2]) for p in arcl(ri0, rng2[0], rng2[1], 30)][1:-1]
        out += [(-ri0, 0, 5)]
        return out

    def sc(c):
        G = 46
        fm = lambda f: "m" if f in (0, 4) else "w"
        o = ""
        o += GE.prism(c, (0, 0, 0), (1, 0, 0), sector(ri0 + 14, ri0 + t - 1, 180, 360, 30), 6, "w")       # end flanges
        o += GE.prism(c, (0, 0, 0), (1, 0, 0), half(False), L, "w", fid_mat=fm, scale=sc_)
        # stator-vane grooves on the inner face
        for x in range(14, L - 8, 11):
            k = sc_(x / L)
            o += path(P(xarc(c, x, ri0 * k + 0.2, 214, 352, 18), False), "o")
        # bolt holes along both joint flanges, dowel holes
        for x in range(10, L - 4, 14):
            k = sc_(x / L)
            for yy in (-1, 1):
                o += hole(c, (x, yy * (ri0 + t + fw / 2) * k, 0.05), (0, 0, 1), 1.9 * k, seg=10)
        o += GE.prism(c, (L - 6, 0, 0), (1, 0, 0), [(u * 1.3, v * 1.3, f) for u, v, f in sector(ri0 + 14, ri0 + t - 1, 180, 360, 30)], 6, "w")
        # upper half, lifted
        o += GE.prism(c, (0, 0, G), (1, 0, 0), sector(ri0 + 14, ri0 + t - 1, 0, 180, 30), 6, "w")
        o += GE.prism(c, (0, 0, G), (1, 0, 0), half(True), L, "w", scale=sc_)
        for x in range(10, L - 4, 14):
            k = sc_(x / L)
            for yy in (-1, 1):
                o += hole(c, (x, yy * (ri0 + t + fw / 2) * k, G + ft * k + 0.05), (0, 0, 1), 1.9 * k, seg=10)
        o += GE.prism(c, (L - 6, 0, G), (1, 0, 0), [(u * 1.3, v * 1.3, f) for u, v, f in sector(ri0 + 14, ri0 + t - 1, 0, 180, 30)], 6, "w")
        # bosses: borescope ports and a bleed flange on the upper half
        for x, a, r, h in ((40, 118, 2.6, 5), (70, 118, 2.6, 5), (104, 112, 6, 6)):
            k = sc_(x / L)
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            base = (x, (ri0 + t - 1) * k * ca, G + (ri0 + t - 1) * k * sa)
            o += GE.cyl(c, base, (0, ca, sa), r, h + 1, "w", seg=16)
            if r > 4:
                o += GE.cyl(c, (x, base[1] + ca * (h + 1), base[2] + sa * (h + 1)), (0, ca, sa), r + 3, 2, "w", seg=20)
        return o
    return fit(sc, -30, 24, (10, 6, 310, 190))[0]


@part("gasgen.gtrotor")
def _():
    cy = 92

    def r_case(x):                       # inner casing radius along the machine
        pts_ = [(14, 46), (40, 34), (132, 23), (140, 30), (168, 30), (176, 27), (214, 38), (252, 52)]
        for (x0, r0), (x1, r1) in zip(pts_, pts_[1:]):
            if x <= x1:
                return r0 + (r1 - r0) * (x - x0) / (x1 - x0)
        return pts_[-1][1]

    def r_hub(x):
        pts_ = [(14, 6), (40, 12), (132, 18.5), (140, 14), (168, 14), (176, 19), (214, 20), (252, 14)]
        for (x0, r0), (x1, r1) in zip(pts_, pts_[1:]):
            if x <= x1:
                return r0 + (r1 - r0) * (x - x0) / (x1 - x0)
        return 14
    s = shadow(140, 160, 128, 6)
    # gas path colours: air -> combustion -> hot gas
    xs = list(range(14, 253, 4))
    for sgn in (-1, 1):
        s += pg([(x, cy + sgn * r_hub(x)) for x in xs] + [(x, cy + sgn * r_case(x)) for x in xs[::-1]], "coolin")
        s += pg([(x, cy + sgn * r_hub(x)) for x in xs if x >= 168] + [(x, cy + sgn * r_case(x)) for x in xs[::-1] if x >= 168], "hotband")
    # casing (section, dark) and inner hub/drum
    for sgn in (-1, 1):
        outer = [(x, cy + sgn * (r_case(x) + (6 if x < 140 or x > 168 else 24) + (0 if x < 214 else 2))) for x in xs]
        s += section([(x, cy + sgn * r_case(x)) for x in xs] + outer[::-1], "w3", 3.6, 45 * sgn)
    # rotor: disks stacked on tie bolts, compressor + turbine blades, stator vanes
    for i in range(12):
        x = 44 + i * 7.4
        rh, rc = r_hub(x), r_case(x)
        for sgn in (-1, 1):
            s += rect(x, cy - rh if sgn < 0 else cy + 6, 4.6, rh - 6, "w2")
            y0, y1 = cy + sgn * rh, cy + sgn * (rc - 1.2)
            s += rect(x + 0.4, min(y0, y1), 2.8, abs(y1 - y0), "w")
            y2, y3 = cy + sgn * (rh + 1.2), cy + sgn * rc
            s += rect(x + 4.4, min(y2, y3), 2.2, abs(y3 - y2), "w3")
    for i in range(3):
        x = 178 + i * 12
        rh, rc = r_hub(x), r_case(x)
        for sgn in (-1, 1):
            y2, y3 = cy + sgn * (rh + 1), cy + sgn * rc
            s += rect(x, min(y2, y3), 4, abs(y3 - y2), "gw")
            y0, y1 = cy + sgn * rh, cy + sgn * (rc - 1.4)
            s += rect(x + 5.4, min(y0, y1), 4.6, abs(y1 - y0), "gw")
            s += rect(x + 4.6, cy - rh if sgn < 0 else cy + 5, 6.2, rh - 5, "w")
    s += rect(30, cy - 5, 196, 10, "w") + line(36, cy - 2.4, 222, cy - 2.4, "o thin") + line(36, cy + 2.4, 222, cy + 2.4, "o thin")
    for x in (26, 222):                                                      # bearings
        s += rect(x, cy - 9, 10, 4, "t") + rect(x, cy + 5, 10, 4, "t")
    # combustors (one above, one below), flames
    for sgn in (-1, 1):
        s += path("M136 %s L160 %s L172 %s L168 %s L140 %s Z" % (n(cy + sgn * 46), n(cy + sgn * 38), n(cy + sgn * 26), n(cy + sgn * 22), n(cy + sgn * 34)), "w")
        s += path("M142 %s Q156 %s 168 %s" % (n(cy + sgn * 40), n(cy + sgn * 36), n(cy + sgn * 26)), "hl")
        s += path("M140 %s q10 %s 24 %s q-12 %s -24 %s" % (n(cy + sgn * 40), n(-sgn * 1), n(-sgn * 8), n(sgn * 6), n(-sgn * -2)), "h")
    # flow arrows: air in, hot gas out
    s += flow([(6, cy - 30), (22, cy - 28), (38, cy - 22)], "air", 2, 5) + flow([(6, cy + 30), (22, cy + 28), (38, cy + 22)], "air", 2, 5)
    s += flow([(226, cy - 30), (246, cy - 40), (262, cy - 46)], "gas", 2, 5) + flow([(226, cy + 30), (246, cy + 40), (262, cy + 46)], "gas", 2, 5)
    # driven package beyond the cold end: gearbox + generator outlines only
    s += rect(270, cy - 14, 16, 28, "o dash") + rect(290, cy - 22, 24, 44, "o dash") + line(252, cy, 270, cy, "o dash")
    # blade-tip clearance (lens) on a turbine blade
    tx, ty = 184.6, cy - r_case(184.6) + 1
    s += lens(222, 26, 18, tx, ty)
    body = rect(204, 8, 40, 10, "w3") + hatch([(204, 8), (244, 8), (244, 18), (204, 18)], 3, 45) + rect(212, 22, 18, 30, "gw")
    s += clipc("pw2-gt-tip", 222, 26, 18, body) + circ(222, 26, 18, "o")
    s += arrow(236, 30, 236, 22.4) + arrow(236, 10, 236, 17.6)
    # spin pit: rotor hung from the drive into a buried vacuum vessel
    s += panel(8, 146, 100, 48)
    s += rect(12, 160, 92, 2, "m3")
    s += section([(30, 162), (36, 162), (36, 190), (78, 190), (78, 162), (84, 162), (84, 194), (30, 194)], "m2", 3)
    s += rect(28, 158, 58, 4, "m2") + rect(48, 148, 18, 10, "dk", 2) + line(57, 162, 57, 176, "o")
    for i in range(3):
        s += rect(41, 170 + i * 5, 32, 4, "gw" if i == 2 else "w")
    s += circ(96, 176, 5, "m2") + line(84, 176, 91, 176, "o")
    return s


@part("gasgen.geprech")
def _():
    s = ""
    fe = lambda b: '<g class="ilu mt-fe">%s</g>' % b
    # ---- left: cylinder head with prechamber, main chamber, piston
    head_out = [(10, 18), (154, 18), (154, 96), (10, 96)]
    bore_ = [(70, 18), (94, 18), (94, 100), (70, 100)]
    vl = [(26, 96), (58, 96), (52, 74), (32, 74)]
    vr = [(106, 96), (138, 96), (132, 74), (112, 74)]
    s += fe(section([head_out, bore_, vl, vr], "w", 3.4))
    for x0 in (30, 110):                                                     # valves
        s += path("M%s 92 L%s 92 L%s 86 L%s 72 L%s 20 L%s 20 L%s 72 L%s 86Z" % (n(x0 - 4), n(x0 + 28), n(x0 + 18), n(x0 + 15), n(x0 + 15), n(x0 + 9), n(x0 + 9), n(x0 + 6)), "w")
    s += fe(srect(10, 96, 8, 64, "w", 3) + srect(146, 96, 8, 64, "w", 3))
    s += rect(18, 96, 128, 54, "beamf")                                      # lean main charge
    s += path("M18 150 L146 150 L146 186 L18 186Z", "w") + path("M40 150 Q82 162 124 150", "w2")
    # prechamber body with rich mixture, spark plug, gas check valve, nozzle holes
    s += path("M70 40 L94 40 L94 100 Q94 114 82 114 Q70 114 70 100Z", "m")
    s += path("M76 56 L88 56 L88 100 Q88 108 82 108 Q76 108 76 100Z", "hotin")
    s += rect(74, 30, 16, 10, "w") + rect(78, 10, 8, 20, "gw", 2) + rect(80.5, 6, 3, 5, "w") + line(82, 52, 82, 58, "o") + line(80, 58, 84, 58, "o")
    s += rect(74, 40, 16, 16, "w2")
    s += rect(94, 46, 18, 10, "m") + circ(100, 51, 2.4, "w2") + path("M112 51 L154 51", "fence")
    for a in (-60, -30, 0, 30, 60):
        r = math.radians(a + 90)
        x0, y0 = 82 + 9 * math.cos(r), 105 + 9 * math.sin(r)
        x1, y1 = 82 + 34 * math.cos(r), 105 + 32 * math.sin(r)
        s += path("M%s %s Q%s %s %s %s Q%s %s %s %s Z" % (n(x0 - 2), n(y0), n((x0 + x1) / 2 - 4), n((y0 + y1) / 2), n(x1), n(y1),
                                                       n((x0 + x1) / 2 + 4), n((y0 + y1) / 2), n(x0 + 2), n(y0)), "h")
    # ---- right: electronically controlled gas admission valve (section)
    hx0, hx1 = 186, 290
    body = [(hx0, 30), (hx1, 30), (hx1, 150), (hx0, 150)]
    cav = [(hx0 + 8, 76), (hx1 - 8, 76), (hx1 - 8, 122), (hx0 + 8, 122)]
    outlet = [(220, 122), (256, 122), (256, 150), (220, 150)]
    inlet = [(hx0, 84), (hx0 + 8, 84), (hx0 + 8, 96), (hx0, 96)]
    s += section([body, cav, outlet, [(hx0 + 4, 34), (hx1 - 4, 34), (hx1 - 4, 72), (hx0 + 4, 72)], inlet], "w", 3.4)
    s += rect(hx0 + 4, 34, hx1 - hx0 - 8, 38, "rb")                           # potted solenoid
    for x0 in (hx0 + 10, hx1 - 32):
        s += rect(x0, 40, 22, 28, "cu")
        for k in range(1, 7):
            s += line(x0, 40 + k * 4, x0 + 22, 40 + k * 4, "o thin")
    s += rect(228, 34, 20, 40, "w2") + path("M234 40 L242 44 L234 48 L242 52 L234 56 L242 60 L234 64 L242 68", "o")
    s += rect(220, 78, 36, 12, "w2", 2)                                       # armature
    s += rect(hx0 + 10, 96, hx1 - hx0 - 20, 6, "m")                           # moving slotted plate
    s += rect(hx0 + 8, 110, hx1 - hx0 - 16, 8, "w")                           # seat plate
    for k in range(6):
        s += rect(hx0 + 16 + k * 14, 96, 5, 6, "void") + rect(hx0 + 23 + k * 14, 110, 5, 8, "void")
    s += rect(226, 22, 24, 8, "dk", 2)
    s += flow([(160, 90), (182, 90), (198, 92)], "fuel", 2.2, 5.5)
    for x in (218, 238, 258):
        s += flow([(x, 104), (x + 2, 114), (x - 0, 130)], "fuel", 1.6, 4.5)
    s += flow([(238, 132), (238, 146), (238, 166)], "fuel", 2.4, 6)
    return s


@part("gasgen.geassy")
def _():
    V = [(-20, 10), (20, 10), (20, 52), (31, 72), (12, 81), (4, 64), (-4, 64), (-12, 81), (-31, 72), (-20, 52)]

    def sc(c):
        o = ""
        # exhaust heat-recovery boiler beyond the free end, exhaust pipe from the turbocharger
        o += boxp(c, -64, 4, 0, 34, 40, 62, "w") + boxp(c, -60, 10, 62, 26, 28, 10, "w")
        o += stroke([c.xy((-8, 2, 96)), c.xy((-20, 14, 100)), c.xy((-40, 22, 72))], "--ms2", 6)
        # turbocharger on the free end
        o += GE.cyl(c, (-6, -6, 88), (0, 1, 0), 8, 6, "alu") + GE.cyl(c, (-6, 2, 88), (0, 1, 0), 4, 4, "w") + GE.cyl(c, (-6, 6, 88), (0, 1, 0), 8, 6, "w")
        # common base frame
        o += boxp(c, -10, -34, 0, 262, 68, 10, "w")
        # V engine block with heads
        o += GE.prism(c, (6, 0, 0), (1, 0, 0), [(u, v, i) for i, (u, v) in enumerate(V)], 148, "w")
        o += boxp(c, 10, -6, 64, 140, 12, 7, "w")                                  # intake manifold in the V
        o += stroke([c.xy((12, 0, 74)), c.xy((150, 0, 74))], "--il-yel", 3)       # gas rail
        for side in (1, -1):                                                       # back bank first
            nrm = (0, side * 0.42, 0.91)
            for i in range(8):
                x = 20 + i * 17
                b = (x, side * 21.5, 76.5)
                o += GE.cyl(c, b, nrm, 2.8, 9, "dk", seg=12)
                tip = (b[0], b[1] + nrm[1] * 9, b[2] + nrm[2] * 9)
                q0, q1 = c.xy(tip), c.xy((x, side * 9, 84))
                o += path("M%s %s Q%s %s %s %s" % (n(q0[0]), n(q0[1]), n((q0[0] + q1[0]) / 2), n(q1[1] - 4), n(q1[0]), n(q1[1])), "o")
                o += GE.cyl(c, (x - 4, side * 6, 71), (0, 0, 1), 2, 4, "m", seg=10)  # gas admission valves
            o += stroke([c.xy((14, side * 9, 84)), c.xy((150, side * 9, 84))], "--il-rb", 2.2)
        for i in range(8):                                                         # knock sensors
            o += GE.cyl(c, (22 + i * 17, -20, 34), (0, -1, 0), 2, 3, "m", seg=10)
        # coupling housing with laser shaft-alignment heads, generator
        A = (0, 40)
        o += ringx(c, 154, 10, 22, 6, "w", at=A)
        o += ringx(c, 164, 6, 5, 0, "m", at=A)
        for x in (165, 169):
            o += boxp(c, x - 1.4, -4, 44, 2.8, 8, 8, "dk")
        o += ringx(c, 170, 10, 24, 0, "w", at=A, scale=lambda t: 1 + 0.25 * t)
        o += boxp(c, 180, -24, 10, 64, 48, 6, "w")
        o += ringx(c, 180, 64, 30, 0, "w", at=A, grooves=0)
        o += boxp(c, 196, -10, 66, 30, 22, 14, "w")
        o += ringx(c, 244, 4, 30, 0, "w", at=A) + ringx(c, 248, 8, 12, 0, "w", at=A)
        # gas train in front: filter, two shut-off valves, pressure regulator (yellow = fuel gas)
        y = -46
        o += stroke([c.xy((10, y, 14)), c.xy((130, y, 14)), c.xy((140, y, 14)), c.xy((140, -26, 14)), c.xy((146, -26, 60))], "--il-yel", 4.5)
        o += GE.cyl(c, (28, y, 8), (0, 0, 1), 5, 18, "w", seg=16)
        for x in (52, 74):
            o += boxp(c, x - 5, y - 4, 10, 10, 8, 8, "dk") + GE.cyl(c, (x, y, 18), (0, 0, 1), 3.4, 8, "dk", seg=14)
        o += GE.cyl(c, (100, y, 10), (0, 0, 1), 5, 6, "m", seg=16) + GE.cyl(c, (100, y, 16), (0, 0, 1), 8, 3, "m", seg=18)
        return o
    s, c = fit(sc, -30, 24, (8, 8, 290, 188), shy=8)
    a_, b_ = c.xy((165, -4, 52)), c.xy((169, -4, 52))
    s += line(a_[0], a_[1], b_[0], b_[1], "laserl")
    q = c.xy((262, -40, 0))
    s += person(min(q[0] + 8, 304), q[1] + 2, 42 * c.s)
    return s
