"""Part drawings for the marine sections: 2-stroke low-speed main engine (marine2) and propulsion
(propulsion). Same studio-lit metal style as il_parts.py: viewBox 0 0 320 200, theme classes only.

Material notes
- The page puts the part's material class (mt-fe / mt-cu / ...) on the <svg>; w/w2/w3 and the shaded
  solids (ws1..4) follow it. Where one drawing mixes materials, cast-iron pieces are wrapped in
  fe() (a nested group carrying the mt-fe class), copper-alloy pieces use the cu classes directly,
  white metal (bearing alloy) uses the light alu tones and nickel alloys the warm gw tones.
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
    """cast-iron colouring for a piece inside a drawing whose root material is steel."""
    return '<g class="ilu mt-fe">%s</g>' % s


def cug(s):
    """copper-alloy colouring for 2D w/w2/w3 shapes regardless of the root material class."""
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
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / seg))) for k in range(seg + 1)]


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
    # thin theme-aware rim so the figure stays visible on the dark theme
    return s + path(P(body), "o thin") + circ(hx, hy, 2.2 * k, "o thin")


def fit_scene(fn, az, el, area=(16, 14, 304, 172), sh=True, sh_ry=None):
    """run fn(scene) twice: probe extents with a unit camera, then fit into area (x0,y0,x1,y1)."""
    pr = Scene(0, 0, az, el, 1.0)
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
    return out + body


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


def circ3(cam, C, A, r, seg=28):
    """screen points of a circle (centre C, normal A, radius r) in 3D."""
    E1, E2, _ = GE.frame(A)
    return [cam.xy(tuple(C[i] + r * (math.cos(2 * math.pi * k / seg) * E1[i] + math.sin(2 * math.pi * k / seg) * E2[i]) for i in range(3)))
            for k in range(seg)]


def hole3(cam, C, A, r, c="bg", seg=None):
    seg = seg or max(10, min(24, int(r * 3)))
    return pg(circ3(cam, C, A, r, seg), c)


def sector(r0, r1, a0, a1, seg=8, cy=0.0, cz=0.0):
    """annular sector outline in a plane (u,v) around (cy,cz); angles in degrees, v up."""
    pts = [(cy + r1 * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), cz + r1 * math.sin(math.radians(a0 + (a1 - a0) * k / seg)), 0)
           for k in range(seg + 1)]
    pts += [(cy + r0 * math.cos(math.radians(a1 - (a1 - a0) * k / seg)), cz + r0 * math.sin(math.radians(a1 - (a1 - a0) * k / seg)), 2)
            for k in range(seg + 1)]
    pts[seg] = pts[seg][:2] + (1,)
    pts[-1] = pts[-1][:2] + (3,)
    return pts


# =====================================================================================
# marine2: 2-stroke low-speed main engine
# =====================================================================================
@part("marine2.m2bed")
def _():
    L, Wd, Hh = 600, 80, 100           # drawn length, half width, height
    xs = [70, 190, 310, 430]            # main bearing girders
    xt = 571                            # thrust girder centre

    def wave(y):
        return 10 + 9 * math.sin(y * 0.13)

    def foot(y0, y1):
        ys = [y0 + (y1 - y0) * k / 8 for k in range(9)]
        return [(L, y0), (L, y1)] + [(wave(y), y) for y in reversed(ys)]

    def notch(r, ztop, ylim, zbot):
        pts = [(-ylim, zbot, 0), (ylim, zbot, 1), (ylim, ztop, 2), (r, ztop, 3)]
        for k in range(1, 12):
            t = math.pi * k / 12
            pts.append((r * math.cos(t), ztop - r * math.sin(t), 4 + k // 2))
        pts += [(-r, ztop, 11), (-ylim, ztop, 12)]
        return pts

    def fn(sc):
        # bottom flanges + floor
        Z(sc, 0, 7, foot(-Wd - 16, -Wd), "w", 40)
        Z(sc, 0, 7, foot(Wd, Wd + 16), "w", 40)
        Z(sc, 0, 8, foot(-Wd + 32, Wd - 32), "w", 60)
        # back girder, transverse girders, front girder
        Z(sc, 0, Hh, foot(Wd - 32, Wd), "w", 30, cap_mat="alu")
        for xc in xs:
            X(sc, xc - 12, 24, notch(30, Hh, Wd - 32, 8), "w", 0, smooth=True, cap_mat="w")
            X(sc, xc - 12.5, 25, [(30 * math.cos(math.pi * k / 16), Hh - 30 * math.sin(math.pi * k / 16), k // 3) for k in range(17)] +
              [(25 * math.cos(math.pi * k / 16), Hh - 25 * math.sin(math.pi * k / 16), 9 + k // 3) for k in range(16, -1, -1)],
              "alu", -6, smooth=True)
        X(sc, xt - 23, 46, notch(30, Hh, Wd - 32, 8), "w", 0, smooth=True)
        X(sc, xt - 23.5, 47, [(30 * math.cos(math.pi * k / 16), Hh - 30 * math.sin(math.pi * k / 16), k // 3) for k in range(17)] +
          [(25 * math.cos(math.pi * k / 16), Hh - 25 * math.sin(math.pi * k / 16), 9 + k // 3) for k in range(16, -1, -1)],
          "alu", -6, smooth=True)
        # thrust pads on the aft face of the thrust girder
        for k in range(5):
            a0 = 196 + k * 30.5
            X(sc, xt + 23, 4, [(u, v + Hh, f) for u, v, f in sector(33, 54, a0, a0 + 25, 6)], "alu", -8)
        Z(sc, 0, Hh, foot(-Wd, -Wd + 32), "w", -20, cap_mat="alu")
        # one main bearing cap with studs
        xc = xs[2]
        cap = [(-44, Hh, 0), (-30, Hh, 1)] + [(30 * math.cos(math.pi - math.pi * k / 16), Hh + 30 * math.sin(math.pi - math.pi * k / 16), 2 + k // 3)
                                             for k in range(17)] + [(44, Hh, 9), (44, Hh + 26, 10), (36, Hh + 34, 11), (-36, Hh + 34, 12), (-44, Hh + 26, 13)]
        X(sc, xc - 12, 24, cap, "w", -10)
        X(sc, xc - 12.5, 25, [(30 * math.cos(math.pi - math.pi * k / 16), Hh + 30 * math.sin(math.pi - math.pi * k / 16), k // 3) for k in range(17)] +
          [(25 * math.cos(math.pi * k / 16), Hh + 25 * math.sin(math.pi * k / 16), 9 + k // 3) for k in range(17)], "alu", -11, smooth=True)
        for yy in (-38, 38):
            for dx in (-6, 6):
                CYL(sc, (xc + dx, yy, Hh + 34), (0, 0, 1), 3.2, 9, "w", -12)

        def marks(s_):
            cam = s_.cam
            o = ""
            for xc_ in xs + [xt]:
                for yy in (-64, 64):
                    for dx in (-7, 7):
                        o += hole3(cam, (xc_ + dx, yy, Hh + 0.2), (0, 0, 1), 3.2)
            for k in range(19):
                xx = 22 + k * 31
                o += hole3(cam, (xx, -Wd - 9, 7.2), (0, 0, 1), 2.6)
            return o
        sc.top.append(marks)

        def weld(pts3):
            def f(s_):
                q = [s_.cam.xy(p) for p in pts3]
                return '<path class="grit" d="%s"/>' % P(q, False)
            return f
        for xc_ in xs:
            RAW(sc, weld([(xc_ + 12.5, Wd - 32, Hh - 1), (xc_ + 12.5, Wd - 32, 9)]), ((xc_ + 12.5, Wd - 32, 9), (xc_ + 13, Wd - 31, Hh)), -1)
            for yy in (-Wd + 32, Wd - 32):
                RAW(sc, weld([(xc_ - 12, yy, Hh + .3), (xc_ + 12, yy, Hh + .3)]), ((xc_ - 12, yy, Hh), (xc_ + 12, yy + .5, Hh + .5)), -30)
        RAW(sc, weld([(wave(-Wd) + 6, -Wd - .3, 7.5), (L, -Wd - .3, 7.5)]), ((0, -Wd - 1, 7), (L, -Wd - .5, 8)), -40)

        def man(s_):
            fx, fy = s_.cam.xy((L + 70, -10, 0))
            hx, hy = s_.cam.xy((L + 70, -10, 68))
            return person(fx, fy, fy - hy)
        RAW(sc, man, ((L + 66, -14, 0), (L + 74, -6, 68)), -50)
    return fit_scene(fn, -40, 34, (10, 12, 312, 180))


def rrect(y0, z0, y1, z1, r, seg=4, fid0=0):
    """rounded rectangle outline in a plane (u,v), counter-clockwise, with fids per side/corner."""
    pts, f = [], fid0
    for cx, cy, a0 in ((y1 - r, z0 + r, -90), (y1 - r, z1 - r, 0), (y0 + r, z1 - r, 90), (y0 + r, z0 + r, 180)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a), f))
        f += 1
    return pts


class VS:
    """vertically convex screen region: x in [xa, xb], y between top(x) and bot(x)."""

    def __init__(s, xa, xb, top, bot):
        s.xa, s.xb, s.top, s.bot = xa, xb, top, bot

    @staticmethod
    def ell(cx, cy, rx, ry):
        def h(x):
            t = 1 - ((x - cx) / rx) ** 2
            return ry * math.sqrt(max(t, 0.0))
        return VS(cx - rx, cx + rx, lambda x: cy - h(x), lambda x: cy + h(x))

    def __and__(s, o):
        return VS(max(s.xa, o.xa), min(s.xb, o.xb), lambda x: max(s.top(x), o.top(x)), lambda x: min(s.bot(x), o.bot(x)))

    def poly(s, N=48):
        if s.xb <= s.xa:
            return []
        xs = [s.xa + (s.xb - s.xa) * k / N for k in range(N + 1)]
        ok = [x for x in xs if s.bot(x) - s.top(x) > 0.05]
        if len(ok) < 2:
            return []
        xa, xb = ok[0], ok[-1]
        # refine the ends where the region pinches off
        for _ in range(12):
            m = xa - (s.xb - s.xa) / N / 2 ** (_ + 1)
            if m >= s.xa and s.bot(m) - s.top(m) > 0.05:
                xa = m
            m2 = xb + (s.xb - s.xa) / N / 2 ** (_ + 1)
            if m2 <= s.xb and s.bot(m2) - s.top(m2) > 0.05:
                xb = m2
        xs = [xa + (xb - xa) * k / N for k in range(N + 1)]
        return [(x, s.top(x)) for x in xs] + [(x, s.bot(x)) for x in reversed(xs)]

    def svg(s, c):
        p = s.poly()
        return pg(p, c) if len(p) > 2 else ""


def hole_ell(cam, cx, cy, z, r):
    sx, sy = cam.xy((cx, cy, z))
    return VS.ell(sx, sy, r * cam.s, r * cam.s * cam.se)


def stepped_hole(cam, cx, cy, z, steps, last="bg"):
    """vertical stepped bore seen from above, steps = [(r, depth), ...] outer to inner.
    Everything is clipped to the rim, so it can be drawn on top of the top face."""
    o = ""
    clip = hole_ell(cam, cx, cy, z, steps[0][0])
    zz = z
    for i, (r, dep) in enumerate(steps):
        rim = hole_ell(cam, cx, cy, zz, r)
        clip = clip & rim
        o += clip.svg("w3")
        flo = hole_ell(cam, cx, cy, zz - dep, r)
        o += (clip & flo).svg(last if i == len(steps) - 1 else "w2")
        zz -= dep
    return o


@part("marine2.m2frame")
def _():
    L, Wd, Hh, t = 360, 90, 135, 10
    xp = [0, 120, 240, 360]

    def cut_edge():
        pts = [(242, Hh), (236, 118), (244, 96), (235, 76), (240, 58)]
        for k in range(1, 13):
            xx = 240 - k * 20
            pts.append((xx, 50 + 5 * math.sin(k * 1.7)))
        return pts

    def fn(sc):
        # back wall + its flanges
        BOX(sc, 0, Wd - t, 0, L, t, Hh, "w", 80)
        BOX(sc, 0, Wd - t, Hh, L, t + 10, 7, "w", 70, cap_mat="alu")
        BOX(sc, 0, Wd - t, -7, L, t + 10, 7, "w", 90)
        # transverse walls with guide strips
        for i, x0 in enumerate(xp):
            xa = min(max(x0 - 7, 0), L - 14)
            X(sc, xa, 14, [(-Wd + t, 0), (Wd - t, 0), (Wd - t, Hh), (-Wd + t, Hh)], "w", 20 - i, cap_mat="w")
            if x0 < L:
                BOX(sc, xa + 14, -13, 16, 5, 26, Hh - 30, "alu", 10 - i)
        # tie-rod tubes standing where the front wall is cut away
        for x0 in (7, 120):
            CYL(sc, (x0, -Wd + 5, 0), (0, 0, 1), 5, Hh, "w", -30)
        # front wall: full over the right cylinder, cut away (wavy) over the other two
        ce = cut_edge()
        Y(sc, -Wd + t, t, [(0, 0), (L, 0), (L, Hh)] + ce + [(0, ce[-1][1])], "w", -40)
        BOX(sc, 236, -Wd - 10, Hh, L - 236, t + 10, 7, "w", -45, cap_mat="alu")
        BOX(sc, 0, -Wd - 10, -7, L, t + 10, 7, "w", -45)
        # inspection door + relief valve on the remaining wall
        Y(sc, -Wd, 3, [(xx, zz, f) for xx, zz, f in rrect(266, 26, 334, 82, 10)], "w", -50)
        CYL(sc, (300, -Wd - 3, 106), (0, -1, 0), 13, 8, "w", -52)
        CYL(sc, (300, -Wd - 11, 106), (0, -1, 0), 9, 5, "w", -53)

        def marks(s_):
            cam = s_.cam
            o = ""
            for x0 in xp:
                for yy in (Wd - 5,):
                    o += hole3(cam, (min(max(x0, 8), L - 8), yy, Hh + 7.2), (0, 0, 1), 3.4)
            for k in range(12):
                xx = 15 + k * 30
                o += hole3(cam, (xx, Wd + 6, Hh + 7.2), (0, 0, 1), 2.2)
            for k in range(4):
                xx = 250 + k * 30
                o += hole3(cam, (xx, -Wd - 6, Hh + 7.2), (0, 0, 1), 2.2)
                o += hole3(cam, (xx, -Wd - 6, 0.2), (0, 0, 1), 2.2)
            for k in range(8):
                xx = 15 + k * 30
                o += hole3(cam, (xx, -Wd - 6, 0.2), (0, 0, 1), 2.2)
            # door bolts
            for k in range(8):
                a = 2 * math.pi * k / 8
                o += hole3(cam, (300 + 30 * math.cos(a), -Wd - 3.2, 54 + 22 * math.sin(a)), (0, -1, 0), 1.6, "m3")
            return o
        sc.top.append(marks)

        def guide_arrow(s_):
            a, b = s_.cam.xy((134, -16, 40)), s_.cam.xy((134, -16, 112))
            return arrow(a[0], a[1], b[0], b[1], both=True)
        sc.top.append(guide_arrow)
    return fit_scene(fn, -34, 26, (22, 12, 298, 180))


@part("marine2.m2cylfr")
def _():
    L, Wd, Hh = 330, 77, 110
    xc = [55, 165, 275]
    outer = rrect(-Wd, 0, Wd, Hh, 14, 4)
    inner = rrect(-Wd + 15, 14, Wd - 15, Hh - 15, 10, 4)

    def fn(sc):
        X(sc, 0, 12, outer, "w", 50)
        X(sc, 12, L - 12, outer, "w", 0, holes=[inner[::-1]])

        def top(s_):
            cam = s_.cam
            o = ""
            for x0 in xc:
                o += stepped_hole(cam, x0, 0, Hh, [(52, 7), (46, 90)])
            for x0 in xc:
                for k in range(10):
                    a = 2 * math.pi * (k + .5) / 10
                    o += hole3(cam, (x0 + 59 * math.cos(a), 59 * math.sin(a), Hh + .1), (0, 0, 1), 2.6)
            # scavenge air openings on the front side
            for x0 in xc:
                ov = [cam.xy((x0 + 34 * math.cos(2 * math.pi * k / 32), -Wd - .2, 52 + 17 * math.sin(2 * math.pi * k / 32))) for k in range(32)]
                o += pg(ov, "w3")
                ov2 = [cam.xy((x0 + 2 + 31 * math.cos(2 * math.pi * k / 32), -Wd - .2, 51 + 14 * math.sin(2 * math.pi * k / 32))) for k in range(32)]
                o += pg(ov2, "bg")
            # cut end: hatch the section of the casting wall
            ring_o = [cam.xy((L, u, v)) for u, v, f in outer]
            ring_i = [cam.xy((L, u, v)) for u, v, f in inner]
            o += hatch([ring_o, ring_i], 3.2, 45)
            return o
        RAW(sc, top, ((0, -Wd, Hh - 1), (L, Wd, Hh)), -100)
    return fit_scene(fn, -32, 30, (24, 14, 296, 176))


def hull(pts_):
    """convex hull (monotone chain), counter-clockwise."""
    p = sorted(set((round(x, 3), round(y, 3)) for x, y in pts_))
    if len(p) < 3:
        return p

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def CYLd(sc, O, A, r, h, mat="w", bias=0.0, dark=0, cap_mat=None, seg=32):
    a = GE._norm(A)
    p1 = tuple(O[i] + a[i] * h for i in range(3))
    lo = tuple(min(O[i], p1[i]) - (r if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (r if abs(a[i]) < .99 else 0) for i in range(3))
    sc.add(GE.prism(sc.cam, O, a, GE.circle_outline(r, seg, 16), h, mat, smooth=True, dark=dark, cap_mat=cap_mat), (lo, hi), bias)


def banded(loop, group=4):
    return [(p[0], p[1], i // group) for i, p in enumerate(loop)]


@part("marine2.m2crank")
def _():
    rj, rp, e, Rw, Rp, tw, lp, lj = 20, 19, 64, 40, 36, 16, 36, 32
    ang = [0, 144, 288, 72, 216]

    def pin_yz(th):
        t = math.radians(th)
        return (-e * math.sin(t), e * math.cos(t))

    def web(th):
        py, pz = pin_yz(th)
        pts_ = [(Rw * math.cos(2 * math.pi * k / 24), Rw * math.sin(2 * math.pi * k / 24)) for k in range(24)]
        pts_ += [(py + Rp * math.cos(2 * math.pi * k / 24), pz + Rp * math.sin(2 * math.pi * k / 24)) for k in range(24)]
        return banded(hull(pts_), 2)

    def fn(sc):
        # aft end on the left: turning-wheel flange, journal, thrust collar
        CYL(sc, (0, 0, 0), (1, 0, 0), 38, 12, "w")

        def bolts(s_):
            o = ""
            for k in range(8):
                a = 2 * math.pi * (k + .5) / 8
                o += hole3(s_.cam, (-.2, 29 * math.cos(a), 29 * math.sin(a)), (1, 0, 0), 3.2)
            return o + hole3(s_.cam, (-.2, 0, 0), (1, 0, 0), 8, "w2")
        RAW(sc, bolts, ((-.2, -38, -38), (0, 38, 38)), -5)
        x = 12
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, 26, "alu")
        x += 26
        CYL(sc, (x, 0, 0), (1, 0, 0), 58, 18, "w")
        x += 18
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, 30, "alu")
        x += 30
        for i, th in enumerate(ang):
            py, pz = pin_yz(th)

            def ring(xf_):
                def f(s_):
                    cam = s_.cam
                    o = pg(circ3(cam, (xf_ - .2, 0, 0), (1, 0, 0), rj + 4.5, 36), "o")
                    a = math.radians(115)
                    p1 = cam.xy((xf_ - .2, (rj + .5) * math.cos(a), (rj + .5) * math.sin(a)))
                    p2 = cam.xy((xf_ - .2, (rj + 9) * math.cos(a), (rj + 9) * math.sin(a)))
                    p3 = cam.xy((xf_ - 9, (rj + .3) * math.cos(a), (rj + .3) * math.sin(a)))
                    return o + '<path class="mfo" d="M%s %sL%s %sL%s %s"/>' % (n(p3[0]), n(p3[1]), n(p1[0]), n(p1[1]), n(p2[0]), n(p2[1]))
                return f
            RAW(sc, ring(x), ((x - .1, -Rw, -Rw), (x, Rw, Rw)))
            X(sc, x, tw, web(th), "w", 0, smooth=True, dark=1, cap_mat="w2")
            CYLd(sc, (x + tw, py, pz), (1, 0, 0), rp, lp, "w", 0, dark=1, cap_mat="w2")
            X(sc, x + tw + lp, tw, web(th), "w", 0, smooth=True, dark=1, cap_mat="w2")
            x += 2 * tw + lp
            CYL(sc, (x, 0, 0), (1, 0, 0), rj, lj if i < 4 else 34, "alu")
            x += lj if i < 4 else 34

    s = fit_scene(fn, 16, 12, (10, 22, 264, 182), sh_ry=7)
    # axial view: phase of the five throws
    cx, cy = 290, 44
    s += circ(cx, cy, 25, "o thin dash")
    for th in ang:
        t = math.radians(th)
        px, py = cx - 15 * math.sin(t), cy - 15 * math.cos(t)
        s += line(cx, cy, px, py, "o")
    s += circ(cx, cy, 6.5, "w")
    for th in ang:
        t = math.radians(th)
        s += circ(cx - 15 * math.sin(t), cy - 15 * math.cos(t), 5, "w2")
    return s


def c_outline(R, Ri, a0=0.0, a1=270.0, seg=36):
    """outline (u,v,fid) of an annular sector (a0..a1 deg, world angle from +x toward +y) for a prism
    along +z (frame: u = -y, v = x). Used for half-section (quarter removed) views."""
    pts_ = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        pts_.append((-R * math.sin(t), R * math.cos(t), 100 + min(k, seg - 1) * 12 // seg))
    for k in range(seg + 1):
        t = math.radians(a1 - (a1 - a0) * k / seg)
        pts_.append((-Ri * math.sin(t), Ri * math.cos(t), 200 + min(k, seg - 1) * 12 // seg))
    pts_[seg] = pts_[seg][:2] + (1,)
    pts_[-1] = pts_[-1][:2] + (2,)
    return pts_


def ctube(cam, z0, h, R, Ri, mat="w", a0=0.0, a1=270.0, **kw):
    return GE.prism(cam, (0, 0, z0), (0, 0, 1), c_outline(R, Ri, a0, a1), h, mat, smooth=True, **kw)


def cyl_pt(cam, r, th, z, cx=0.0, cy=0.0):
    t = math.radians(th)
    return cam.xy((cx + r * math.cos(t), cy + r * math.sin(t), z))


def cyl_patch(cam, r, th0, th1, z0, z1, seg=6):
    """screen polygon of a patch on a vertical cylinder surface."""
    a = [cyl_pt(cam, r, th0 + (th1 - th0) * k / seg, z1) for k in range(seg + 1)]
    b = [cyl_pt(cam, r, th1 - (th1 - th0) * k / seg, z0) for k in range(seg + 1)]
    return a + b


@part("marine2.m2liner")
def _():
    cam = GE.Cam(112, 182, 0, 16, 0.47)
    Ri = 40
    segs = [(0, 200, 47), (200, 110, 52), (310, 40, 65)]
    s = shadow(112, 186, 44, 6)
    for z0, h, R in segs:
        s += ctube(cam, z0, h, R, Ri, "w")
    # ---- interior (back-right quarter): honing cross-hatch, lube groove, ports
    hz0, hz1 = 78, 300
    d = ""
    for k in range(-6, 30):
        for sg in (1, -1):
            ps = []
            for j in range(0, 19):
                th = 5 * j
                z = hz0 + k * 9 + sg * th * 0.5
                if hz0 <= z <= hz1:
                    ps.append(cyl_pt(cam, Ri, th, z))
                elif ps:
                    break
            if len(ps) > 1:
                d += P(ps, False)
    s += '<path class="gr" d="%s"/>' % d
    s += pg(cyl_patch(cam, Ri, 2, 90, 213, 217, 10), "w3")
    for th in (22.5, 67.5):
        s += pg(circ3(cam, (Ri * math.cos(math.radians(th)), Ri * math.sin(math.radians(th)), 215),
                      (-math.cos(math.radians(th)), -math.sin(math.radians(th)), 0), 3.4, 14), "bg")
    for k in range(5):
        th = 9 + k * 18
        s += pg(cyl_patch(cam, Ri, th - 4.5, th + 4.5, 36, 70), "bg")
    # ---- exterior (front-left quarter): ports, lube quills, O-ring grooves
    for k in range(5):
        th = 189 + k * 18
        if th + 5 < 270:
            s += pg(cyl_patch(cam, 47, th - 4.5, min(th + 4.5, 269.5), 36, 70), "bg")
    for th in (180, 225):
        t = math.radians(th + 0.01)
        s += pg(circ3(cam, (52.2 * math.cos(t), 52.2 * math.sin(t), 215), (math.cos(t), math.sin(t), 0), 3.4, 14), "bg")
    for z in (9, 17, 25):
        s += pg(cyl_patch(cam, 47.3, 181, 269, z - 1.4, z + 1.4, 10), "w3")
    # ---- section face (plane y=0, x from Ri to R), drawn over the prism's cut face
    prof = [(Ri, 0), (47, 0), (47, 200), (52, 200), (52, 310), (61, 310), (65, 316), (65, 350), (Ri, 350)]
    sec = [cam.xy((x_, 0, z_)) for x_, z_ in prof]
    s += section(sec, "w", 3.0)
    for z in (9, 17, 25):
        s += pg([cam.xy((44.5, -0.1, z - 1.4)), cam.xy((47.2, -0.1, z - 1.4)), cam.xy((47.2, -0.1, z + 1.4)), cam.xy((44.5, -0.1, z + 1.4))], "void")
    s += pg([cam.xy((Ri - .2, -0.1, 213.5)), cam.xy((52.2, -0.1, 213.5)), cam.xy((52.2, -0.1, 216.5)), cam.xy((Ri - .2, -0.1, 216.5))], "void")
    for k in range(2):
        xa, za = 61 - k * 8, 311
        xb, zb = xa - 15, 343
        u = math.hypot(xb - xa, zb - za)
        nx, nz = -(zb - za) / u * 1.5, (xb - xa) / u * 1.5
        s += pg([cam.xy((xa + nx, -0.1, za + nz)), cam.xy((xb + nx, -0.1, zb + nz)), cam.xy((xb - nx, -0.1, zb - nz)), cam.xy((xa - nx, -0.1, za - nz))], "void")
    # cooling jacket around the collar (dotted)
    jk = [cam.xy((61, -0.1, 300)), cam.xy((76, -0.1, 300)), cam.xy((76, -0.1, 346)), cam.xy((66, -0.1, 346))]
    s += path(P(jk, False), "hid")
    jl = [cyl_pt(cam, 76, 180 + 3 * k, 300) for k in range(31)]
    s += path(P(jl, False), "hid") + line(*cam.xy((-76, 0, 300)), *cam.xy((-76, 0, 346)), "hid")
    # ---- inset: plan section through the scavenge ports (tangential ports -> swirl)
    cx, cy, ro, ri = 246, 134, 38, 27
    ins = '<path class="w" fill-rule="evenodd" d="%s%s"/>' % (P(arcpts(cx, cy, ro, ro, 0, 360, 48)), P(arcpts(cx, cy, ri, ri, 0, 360, 48)))
    for k in range(20):
        a = math.radians(k * 18)
        c0 = (math.cos(a), math.sin(a))
        c1 = (math.cos(a + 0.36), math.sin(a + 0.36))
        q0, q1 = (cx + ri * c0[0], cy + ri * c0[1]), (cx + ro * c1[0], cy + ro * c1[1])
        nx, ny = -(q1[1] - q0[1]), (q1[0] - q0[0])
        u = math.hypot(nx, ny)
        nx, ny = nx / u * 1.5, ny / u * 1.5

        def onr(px, py, r):
            m = math.hypot(px - cx, py - cy)
            return (cx + (px - cx) * r / m, cy + (py - cy) * r / m)
        ins += pg([onr(q0[0] - nx, q0[1] - ny, ri), onr(q1[0] - nx, q1[1] - ny, ro), onr(q1[0] + nx, q1[1] + ny, ro), onr(q0[0] + nx, q0[1] + ny, ri)], "void")
    s += ins + circ(cx, cy, ro, "o") + circ(cx, cy, ri, "o")
    # ---- inset: port edge, rounded (section through the wall at a port)
    mx, my, mr = 252, 50, 25
    s += line(*cyl_pt(cam, 47, 225, 53), mx - mr * .93, my + mr * .36, "leadl")
    s += circ(mx, my, mr, "void")
    s += section([(mx - 23, my - 7), (mx - 6, my - 7)] + [(mx - 6 + 4 * math.cos(math.radians(a)), my - 3 + 4 * math.sin(math.radians(a))) for a in range(-90, 1, 15)] +
                 [(mx - 2, my + 3)] + [(mx - 6 + 4 * math.cos(math.radians(a)), my + 3 + 4 * math.sin(math.radians(a))) for a in range(0, 91, 15)] + [(mx - 23, my + 7)], "w", 2.6)
    s += section([(mx + 23, my - 7), (mx + 6, my - 7)] + [(mx + 6 - 4 * math.cos(math.radians(a)), my - 3 + 4 * math.sin(math.radians(a))) for a in range(-90, 1, 15)] +
                 [(mx + 2, my + 3)] + [(mx + 6 - 4 * math.cos(math.radians(a)), my + 3 + 4 * math.sin(math.radians(a))) for a in range(0, 91, 15)] + [(mx + 23, my + 7)], "w", 2.6)
    s += circ(mx, my, mr, "o")
    s += rot(cx, cy, 18, 18, 200, 470)
    return s


def clip_rect(poly_, x0, y0, x1, y1):
    """Sutherland-Hodgman clip of a polygon to an axis-aligned rectangle."""
    def clip(pts_, inside, inter):
        out = []
        for i in range(len(pts_)):
            a, b = pts_[i - 1], pts_[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia:
                    out.append(inter(a, b))
                out.append(b)
            elif ia:
                out.append(inter(a, b))
        return out

    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / ((b[0] - a[0]) or 1e-9))

    def iy(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / ((b[1] - a[1]) or 1e-9), yc)
    p = list(poly_)
    for inside, inter in ((lambda q: q[0] >= x0, ix(x0)), (lambda q: q[0] <= x1, ix(x1)), (lambda q: q[1] >= y0, iy(y0)), (lambda q: q[1] <= y1, iy(y1))):
        if not p:
            break
        p = clip(p, inside, inter)
    return p


@part("marine2.m2piston")
def _():
    cam = GE.Cam(96, 184, 0, 15, 0.47)
    R, Ri_sk = 50, 41
    s = shadow(96, 188, 30, 5)
    # rod foot flange, rod (ground surface), crown + skirt with a quarter removed
    s += GE.cyl(cam, (0, 0, 0), (0, 0, 1), 28, 10, "w")
    for k in range(6):
        a = 2 * math.pi * (k + .5) / 6
        s += hole3(cam, (22 * math.cos(a), 22 * math.sin(a), 10.1), (0, 0, 1), 2.4)
    s += GE.cyl(cam, (0, 0, 10), (0, 0, 1), 15, 312, "alu")
    for xx in (-5, 5):
        s += line(*cam.xy((xx, 0, 14)), *cam.xy((xx, 0, 318)), "hid")
    s += line(*cam.xy((0, 0, 4)), *cam.xy((0, 0, 318)), "hid")
    s += fe(ctube(cam, 310, 20, 49, Ri_sk, "w"))
    s += ctube(cam, 330, 40, R, 0.6, "w")
    # Ni-base overlay on the combustion face (top cap, 3/4 pie)
    pie = [cam.xy((0, 0, 370.2))] + [cam.xy((40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a)), 370.2)) for a in range(0, 271, 10)]
    s += pg(pie, "gw")
    # ring grooves on the outside (front-left quarter)
    for z in (364, 358, 352, 346, 340):
        s += pg(cyl_patch(cam, R + .2, 181, 269.5, z - 1.2, z + 1.2, 10), "w3")

    # section on the plane y=0 (x from axis to R)
    def S(pts2):
        return [cam.xy((x_, -0.15, z_)) for x_, z_ in pts2]
    crown = [(0, 366), (14, 367.2), (28, 369), (38, 370), (48, 370), (50, 368)]
    for z in (364, 358, 352, 346, 340):
        crown += [(50, z + 1.3), (46, z + 1.3), (46, z - 1.3), (50, z - 1.3)]
    crown += [(50, 330), (40, 330), (40, 350), (20, 350), (20, 330), (0, 330)]
    s += section(S(crown), "w", 2.6)
    s += pg(S([(0, 366), (14, 367.2), (28, 369), (38, 370), (44, 370), (44, 372.2), (38, 372.2), (28, 371.2), (14, 369.4), (0, 368.2)]), "gw")
    for k in range(2):
        xa = 36 - k * 9
        s += pg(S([(xa - 1.6, 350), (xa + 1.4, 350), (xa + 8.4, 364), (xa + 5.4, 364)]), "void")
    s += section(S([(0, 322), (28, 322), (28, 330), (0, 330)]), "w", 2.6)
    s += pg(S([(0, 322), (5, 322), (5, 330), (0, 330)]), "void") + line(*cam.xy((2, -0.2, 322)), *cam.xy((2, -0.2, 340)), "hid")
    s += fe(section(S([(41, 310), (49, 310), (49, 330), (41, 330)]), "w", 2.6))
    s += pg(S([(43.6, 316), (46.4, 316), (46.4, 336), (43.6, 336)]), "w2")
    # magnified detail of the crown edge: ring grooves with hard-plated flanks, Ni overlay, cooling bores
    bx0, by0, bx1, by1 = 190, 40, 304, 154
    k_ = 3.35
    ox_, oy_ = bx0 - 22 * k_, by0 + 375 * k_

    def M(pts2):
        return [(ox_ + x_ * k_, oy_ - z_ * k_) for x_, z_ in pts2]
    s += line(*cam.xy((R, 0, 356)), bx0, by0 + 50, "leadl")
    s += rect(bx0, by0, bx1 - bx0, by1 - by0, "void", 6)
    cr = clip_rect(M(crown), bx0, by0, bx1, by1)
    s += section(cr, "w", 3.2)
    s += pg(clip_rect(M([(0, 366), (14, 367.2), (28, 369), (38, 370), (44, 370), (44, 372.2), (38, 372.2), (28, 371.2), (14, 369.4), (0, 368.2)]), bx0, by0, bx1, by1), "gw")
    for k in range(2):
        xa = 36 - k * 9
        s += pg(clip_rect(M([(xa - 1.6, 350), (xa + 1.4, 350), (xa + 8.4, 364), (xa + 5.4, 364)]), bx0, by0, bx1, by1), "void")
    for z in (364, 358, 352, 346, 340):
        s += pg(clip_rect(M([(50, z + 2.1), (45.3, z + 2.1), (45.3, z - 2.1), (50, z - 2.1)]), bx0, by0, bx1, by1), "m3")
        s += pg(clip_rect(M([(50.5, z + 1.3), (46, z + 1.3), (46, z - 1.3), (50.5, z - 1.3)]), bx0, by0, bx1, by1), "void")
    s += fe(section(clip_rect(M([(41, 310), (49, 310), (49, 330), (41, 330)]), bx0, by0, bx1, by1), "w", 3.2))
    s += rect(bx0, by0, bx1 - bx0, by1 - by0, "o", 6)
    return s


@part("marine2.m2xhead")
def _():
    rp, hl = 30, 90          # pin radius, half length
    sx, sy, sz = 40, 54, 72  # guide shoe block

    def fn(sc):
        # pin: plain ends, mirror-finished bearing surface in the middle
        CYL(sc, (-hl, 0, 0), (1, 0, 0), rp, 40, "w")
        CYL(sc, (-hl + 40, 0, 0), (1, 0, 0), rp, 2 * hl - 80, "alu")
        CYL(sc, (hl - 40, 0, 0), (1, 0, 0), rp, 40, "w")
        # piston-rod seat on top of the pin
        CYL(sc, (0, 0, 18), (0, 0, 1), 25, 14, "w", -5)

        def seat(s_):
            o = hole3(s_.cam, (0, 0, 32.2), (0, 0, 1), 6, "bg")
            for k in range(8):
                a = 2 * math.pi * (k + .5) / 8
                o += hole3(s_.cam, (18 * math.cos(a), 18 * math.sin(a), 32.2), (0, 0, 1), 2.2)
            return o
        RAW(sc, seat, ((-25, -25, 32), (25, 25, 32.3)), -8)
        # guide shoes with white-metal sliding faces (front and back)
        for x0 in (-hl - sx, hl):
            BOX(sc, x0, -sy / 2, -sz / 2, sx, sy, sz, "w", 0)
            BOX(sc, x0 + 3, -sy / 2 - 2.2, -sz / 2 + 4, sx - 6, 2.2, sz - 8, "alu", -2)

            def grooves(x0_):
                def f(s_):
                    d = ""
                    for k in range(5):
                        a = s_.cam.xy((x0_ + 6, -sy / 2 - 2.4, -sz / 2 + 10 + k * 12))
                        b = s_.cam.xy((x0_ + sx - 6, -sy / 2 - 2.4, -sz / 2 + 18 + k * 12))
                        d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
                    return '<path class="o thin" d="%s"/>' % d
                return f
            RAW(sc, grooves(x0), ((x0, -sy / 2 - 2.6, -sz / 2), (x0 + sx, -sy / 2 - 2.4, sz / 2)), -3)

        # oil passage inside the pin (end -> middle -> bearing surface)
        def oil(s_):
            a, b = s_.cam.xy((hl + sx, 0, 0)), s_.cam.xy((0, 0, 0))
            c = s_.cam.xy((0, 0, -rp))
            return '<path class="hid" d="M%s %sL%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]))
        sc.top.append(oil)

        # connecting rod top end (ghosted) holding the pin from below
        def rod(s_):
            cam = s_.cam
            ring = [(44 * math.cos(math.radians(a)), 44 * math.sin(math.radians(a)), a // 30) for a in range(180, 361, 10)]
            ring += [(31 * math.cos(math.radians(a)), 31 * math.sin(math.radians(a)), 20 + a // 30) for a in range(360, 179, -10)]
            o = GE.prism(cam, (-58, 0, 0), (1, 0, 0), ring, 116, "w", smooth=True)
            shank = [(-24, -44, 0), (24, -44, 1), (17, -118, 2), (-17, -118, 3)]
            o += GE.prism(cam, (-14, 0, 0), (1, 0, 0), shank, 28, "w")
            return faint(o, 0.3)
        RAW(sc, rod, ((-58, -44, -118), (58, 44, 0)), -60)

        def arr(s_):
            a, b = s_.cam.xy((hl + sx + 14, -sy / 2, -sz / 2 - 6)), s_.cam.xy((hl + sx + 14, -sy / 2, sz / 2 + 10))
            return arrow(a[0], a[1], b[0], b[1], both=True)
        sc.top.append(arr)
    return fit_scene(fn, -28, 26, (24, 10, 296, 184), sh=True)



def mirror(pts_):
    return [(-x_, y_) for x_, y_ in pts_]


@part("marine2.m2exv")
def _():
    cx, y0, k = 136, 10, 1.0

    def T(pts_):
        return [(cx + u * k, y0 + v * k) for u, v in pts_]

    def sec(pl, c="w", st=3.0):
        if isinstance(pl[0][0], (int, float)):
            pl = [pl]
        return section([T(q) for q in pl], c, st)
    s = shadow(cx + 8, 186, 66, 5)
    # --- hydraulic actuator (top) and air spring, steel
    s += sec([[(-15, 2), (15, 2), (15, 28), (-15, 28)], [(-9, 7), (9, 7), (9, 23), (-9, 23)]])
    s += pg(T([(9, 9), (15, 9), (15, 13), (9, 13)]), "void") + pg(T([(15, 8), (25, 8), (25, 14), (15, 14)]), "w2")
    s += pg(T([(-8.4, 15), (8.4, 15), (8.4, 22.6), (-8.4, 22.6)]), "w2")
    s += sec([[(-22, 28), (22, 28), (22, 58), (-22, 58)], [(-17, 32), (17, 32), (17, 54), (-17, 54)]])
    s += pg(T([(-16.4, 35), (16.4, 35), (16.4, 41), (-16.4, 41)]), "w2")
    s += pg(T([(22, 47), (30, 47), (30, 51), (22, 51)]), "w2")
    # --- valve housing (cast iron) with exhaust passage turning sideways and cooling-water channels
    outer = [(-20, 58), (20, 58), (20, 72), (34, 76), (34, 84), (58, 84), (58, 78), (66, 78), (66, 140), (58, 140), (58, 134), (36, 134),
             (34, 142), (-34, 142), (-34, 76), (-20, 72)]
    passage = [(-18, 142), (-18, 96), (-10, 88), (12, 88), (18, 92), (66, 92), (66, 126), (22, 126), (18, 132), (18, 142)]
    bore = [(-4, 58), (4, 58), (4, 88), (-4, 88)]
    s += fe(sec([outer, passage, bore], "w"))
    s += fe(pg(T([(-7, 61), (7, 61), (7, 85), (-7, 85)]), "w2"))
    for pl in ([(-30, 92), (-24, 92), (-24, 134), (-30, 134)], [(24, 136), (30, 136), (30, 140), (24, 140)], [(-14, 76), (-9, 76), (-9, 84), (-14, 84)],
               [(9, 76), (14, 76), (14, 84), (9, 84)], [(36, 80), (54, 80), (54, 86.5), (36, 86.5)]):
        s += pg(T(pl), "fl")
    for v in (82, 136):
        s += pg(T([(59.5, v - 1.6), (64.5, v - 1.6), (64.5, v + 1.6), (59.5, v + 1.6)]), "void")
    # --- bottom piece (seat ring), steel, with cooling channels and hard-faced seat
    bp = [(-36, 142), (-18, 142), (-18, 156), (-15, 158), (-20.5, 166), (-36, 166)]
    s += sec(bp) + sec(mirror(bp))
    for sg in (-1, 1):
        s += pg(T([(sg * 31, 147), (sg * 25, 147), (sg * 25, 159), (sg * 31, 159)]), "fl")
        s += pg(T([(sg * 15, 158), (sg * 20.5, 166), (sg * 22.6, 166), (sg * 16.6, 157.2)]), "gws4 x")
    # --- spindle + disc (nickel alloy), vanes
    s += pg(T([(-3, 18), (3, 18), (3, 146), (-3, 146)]), "gw")
    disc = [(-3, 144), (3, 144), (6, 151), (14.6, 158.4), (20.2, 166), (20.2, 169), (0, 170.5), (-20.2, 169), (-20.2, 166), (-14.6, 158.4), (-6, 151)]
    s += pg(T(disc), "gw")
    for sg in (-1, 1):
        s += pg(T([(sg * 14.6, 158.4), (sg * 20.2, 166), (sg * 18.6, 166.2), (sg * 13.4, 159.3)]), "gws3 x")
        s += pg(T([(sg * 3, 108), (sg * 10, 104), (sg * 10, 109), (sg * 3, 114)]), "gw")
    s += pg(T([(-16.4, 35), (16.4, 35), (16.4, 41), (-16.4, 41)]), "w2")
    # --- arrows: oil in (blue), open = down (hydraulic), close = up (air spring); exhaust out
    a, b = T([(46, 11)])[0], T([(27, 11)])[0]
    s += line(a[0], a[1], b[0] + 4, b[1], "fo") + head(b[0], b[1], math.pi).replace('class="af"', 'class="fdot"')
    a, b = T([(-34, 6)])[0], T([(-34, 40)])[0]
    s += arrow(a[0], a[1], b[0], b[1])
    a, b = T([(40, 64)])[0], T([(40, 30)])[0]
    s += arrow(a[0], a[1], b[0], b[1])
    a, b = T([(30, 109)])[0], T([(80, 109)])[0]
    s += line(a[0], a[1], b[0] - 5, b[1], "hotarc") + head(b[0], b[1], 0, 8).replace('class="af"', 'class="clamph"')
    return s


@part("marine2.m2cover")
def _():
    cam = GE.Cam(160, 118, -12, 30, 0.82)
    R, Rh, Hh = 100, 33, 72
    a0, a1 = 315, 585

    def W(r, th, z):
        t = math.radians(th)
        return cam.xy((r * math.cos(t), r * math.sin(t), z))
    s = shadow(160, 160, 104, 11)
    s += GE.prism(cam, (0, 0, 0), (0, 0, 1), c_outline(R, 70, a0, a1), 7, "w", smooth=True)
    s += GE.prism(cam, (0, 0, 7), (0, 0, 1), c_outline(R, Rh, a0, a1), Hh - 7, "w", smooth=True)

    # section faces on the two cut planes
    def dish(r):
        return 0 if r >= 70 else 8 * ((70 - r) / 37.0) ** 0.8
    for th in (225, 315):
        prof = [(Rh, Hh), (R, Hh), (R, 0)] + [(r, dish(r)) for r in range(70, Rh - 1, -3)] + [(Rh, dish(Rh))]
        s += section([W(r, th, z) for r, z in prof], "w", 3.0)
        # radial cooling bore just above the combustion face, stud hole
        s += pg([W(r, th, z) for r, z in ((40, 15), (R + .3, 13), (R + .3, 19), (40, 19.5))], "void")
        s += pg([W(r, th, z) for r, z in ((83, 34), (89, 34), (89, Hh + .2), (83, Hh + .2))], "void")
    # cooling-bore openings on the outer surface (plugged)
    for th in (192, 210, 330, 348, 6):
        t = math.radians(th)
        s += hole3(cam, (R * math.cos(t), R * math.sin(t), 16), (math.cos(t), math.sin(t), 0), 3, "bg")
    # top face: stud holes, fuel valves (3, inclined), starting valve, safety valve, indicator cock
    for k in range(12):
        th = 15 + 30 * k
        if 225 < th % 360 < 315 or th % 360 in (225, 315):
            continue
        t = math.radians(th)
        s += hole3(cam, (86 * math.cos(t), 86 * math.sin(t), Hh + .1), (0, 0, 1), 4.6)
    for th in (90, 210, 330):
        t = math.radians(th)
        c = (58 * math.cos(t), 58 * math.sin(t), Hh + .1)
        s += hole3(cam, c, (0, 0, 1), 9.5, "w3") + hole3(cam, (c[0] - 2.5 * math.cos(t), c[1] - 2.5 * math.sin(t), Hh + .1), (0, 0, 1), 6.5, "bg")
    for th, r, rr in ((150, 60, 8), (30, 62, 5), (0, 64, 3.6)):
        t = math.radians(th)
        s += hole3(cam, (r * math.cos(t), r * math.sin(t), Hh + .1), (0, 0, 1), rr, "bg")
    return s



@part("marine2.m2assy")
def _():
    cx = 150
    o = shadow(150, 194, 124, 6)
    # test bed + floor
    o += rect(54, 184, 214, 6, "m2") + rect(64, 190, 12, 4, "m3") + rect(156, 190, 12, 4, "m3") + rect(246, 190, 12, 4, "m3")
    # ---------------- stationary structure
    bed = [(96, 160), (cx - 14, 160)] + [(cx - 14 * math.cos(math.radians(a)), 162 + 14 * math.sin(math.radians(a))) for a in range(0, 181, 15)] + \
          [(cx + 14, 160), (204, 160), (208, 169), (208, 184), (92, 184), (92, 169)]
    o += pg(bed, "w2")
    o += pg([(cx - 22, 176), (cx + 22, 176), (cx + 22, 181), (cx - 22, 181)], "w3")
    frame_o = [(98, 96), (202, 96), (199, 160), (101, 160)]
    frame_i = [(110, 99), (190, 99), (187, 160), (113, 160)]
    o += pg(frame_o, "w") + pg(frame_i, "bg")
    for sg in (-1, 1):
        o += pg([(cx + sg * 17, 97), (cx + sg * 20.5, 97), (cx + sg * 20.5, 146), (cx + sg * 17, 146)], "alu")
    # cylinder frame (cast iron) with the scavenge-air space; stuffing box in the diaphragm
    cf_o = [(100, 54), (200, 54), (200, 96), (100, 96)]
    cf_i = [(106, 60), (194, 60), (194, 91), (106, 91)]
    o += fe(pg(cf_o, "w")) + pg(cf_i, "bg")
    o += pg([(cx - 7, 89), (cx + 7, 89), (cx + 7, 99), (cx - 7, 99)], "m2")
    # scavenge receiver, air cooler, turbocharger, exhaust receiver (exhaust side)
    o += pg([(80, 58), (100, 58), (100, 92), (80, 92)], "w2") + pg([(100, 68), (106, 68), (106, 82), (100, 82)], "bg")
    o += pg([(44, 98), (80, 98), (80, 132), (44, 132)], "m2")
    for k in range(8):
        o += line(48 + k * 4.4, 102, 48 + k * 4.4, 128, "o thin")
    o += path("M62 84 L62 98", "pipe") + path("M80 115 L90 115 L90 92", "pipe")
    o += circ(62, 64, 20, "m2") + circ(62, 64, 12.5, "m") + circ(62, 64, 3.5, "m3")
    o += pg([(30, 54), (42, 54), (42, 74), (30, 74)], "m2")
    for k in range(4):
        o += line(32, 58 + k * 4.4, 40, 58 + k * 4.4, "o thin")
    o += circ(90, 28, 13, "w2") + circ(90, 28, 8.5, "bg")
    o += path("M82 38 L74 46", "pipe")
    # ---------------- liner, cover, exhaust valve
    for sg in (-1, 1):
        wall = [(cx + sg * 12, 46), (cx + sg * 21, 46), (cx + sg * 21, 53), (cx + sg * 16, 53), (cx + sg * 16, 92), (cx + sg * 12, 92)]
        o += fe(section(wall, "w", 2.4))
        o += pg([(cx + sg * 12, 80), (cx + sg * 16, 80), (cx + sg * 16, 87), (cx + sg * 12, 87)], "bg")
    o += pg([(cx - 12, 46), (cx + 12, 46), (cx + 12, 60), (cx - 12, 60)], "bg")
    o += section([[(cx - 27, 36), (cx + 27, 36), (cx + 27, 46), (cx - 27, 46)], [(cx - 8, 36), (cx + 8, 36), (cx + 8, 46), (cx - 8, 46)]], "w", 2.4)
    o += pg([(cx - 12, 30), (101, 30), (101, 20), (cx - 12, 20)], "w")                # exhaust duct to the receiver
    for sg in (-1, 1):
        o += pg([(cx + sg * 19 - 2.4, 31), (cx + sg * 19 + 2.4, 31), (cx + sg * 19 + 2.4, 36), (cx + sg * 19 - 2.4, 36)], "w2")
    # hydraulic control unit (electronically controlled) on the camshaft side, oil pipe to the valve actuator
    o += pg([(202, 30), (218, 30), (218, 52), (202, 52)], "m2") + pg([(205, 34), (215, 34), (215, 40), (205, 40)], "m3")
    o += path("M202 36 L182 36 L182 10 L%s 10" % n(cx + 7), "o")
    o += pg([(cx - 12, 14), (cx + 12, 14), (cx + 12, 36), (cx - 12, 36)], "gw")
    o += pg([(cx - 7, 6), (cx + 7, 6), (cx + 7, 14), (cx - 7, 14)], "gw")
    o += pg([(cx - 2, 33), (cx + 2, 33), (cx + 2, 43), (cx - 2, 43)], "gw") + pg([(cx - 7, 42), (cx + 7, 42), (cx + 8.5, 45.5), (cx - 8.5, 45.5)], "gw")
    # ---------------- running gear (crank angle ~35 deg after TDC)
    a = math.radians(35)
    r_, L_ = 20, 44
    px, py = cx + r_ * math.sin(a), 162 - r_ * math.cos(a)
    xy = py - math.sqrt(L_ ** 2 - (px - cx) ** 2)
    pt = xy - 40 - 12
    o += pg([(cx - 12, pt), (cx + 12, pt), (cx + 12, pt + 8), (cx - 12, pt + 8)], "w")
    for k in range(3):
        o += line(cx - 12, pt + 2 + k * 2, cx + 12, pt + 2 + k * 2, "o thin")
    o += fe(pg([(cx - 11.5, pt + 8), (cx + 11.5, pt + 8), (cx + 11.5, pt + 12), (cx - 11.5, pt + 12)], "w"))
    o += pg([(cx - 2.6, pt + 12), (cx + 2.6, pt + 12), (cx + 2.6, xy), (cx - 2.6, xy)], "alu")
    web = hull([(cx + 14 * math.cos(2 * math.pi * k / 24), 162 + 14 * math.sin(2 * math.pi * k / 24)) for k in range(24)] +
               [(px + 10.5 * math.cos(2 * math.pi * k / 24), py + 10.5 * math.sin(2 * math.pi * k / 24)) for k in range(24)])
    o += pg(web, "w2") + circ(cx, 162, 9, "alu")
    dx, dy = px - cx, py - xy
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    rod = [(cx + nx * 3.6, xy + ny * 3.6), (px + nx * 5.8, py + ny * 5.8), (px - nx * 5.8, py - ny * 5.8), (cx - nx * 3.6, xy - ny * 3.6)]
    o += pg(rod, "w") + circ(px, py, 10, "w") + circ(px, py, 6.2, "w2")
    o += pg([(cx - 14, xy - 6.5), (cx + 14, xy - 6.5), (cx + 14, xy + 6.5), (cx - 14, xy + 6.5)], "w") + circ(cx, xy, 5, "w2")
    for sg in (-1, 1):
        o += pg([(cx + sg * 14, xy - 8), (cx + sg * 17, xy - 8), (cx + sg * 17, xy + 8), (cx + sg * 14, xy + 8)], "alu")
    # tie rods: bedplate -> top of the cylinder frame
    for sg in (-1, 1):
        x_ = cx + sg * 47
        o += pg([(x_ - 1.4, 54), (x_ + 1.4, 54), (x_ + 1.4, 183), (x_ - 1.4, 183)], "w3")
        o += pg([(x_ - 4, 48.5), (x_ + 4, 48.5), (x_ + 4, 54), (x_ - 4, 54)], "w2")
    # gas / air flow hints
    o += line(cx - 14, 25, 108, 25, "hotarc") + head(104, 25, math.pi, 7).replace('class="af"', 'class="clamph"')
    o += line(90, 75, 104, 75, "fo") + head(108, 75, 0, 6).replace('class="af"', 'class="fdot"')
    return '<g transform="translate(10 0)">%s</g>' % o + person(292, 193, 23)


# =====================================================================================
# propulsion: reduction gear, propellers, shafting, stern tube
# =====================================================================================
@part("propulsion.prgear")
def _():
    cam = GE.Cam(118, 110, 0, 36, 0.84)
    z1, z2, m = 64, 18, 2.88
    r1, r2 = z1 * m / 2, z2 * m / 2
    hw, psi = 50.0, 14.0                     # face width, helix angle
    beta = math.radians(-12)                 # pinion direction (slightly toward the viewer)
    C = ((r1 + r2) * math.cos(beta), (r1 + r2) * math.sin(beta))
    ph1 = beta + math.pi / 2 - math.pi / z1
    ph2 = beta - math.pi / 2
    s = shadow(146, 172, 128, 12)
    s += GE.cyl(cam, (0, 0, -hw / 2 - 26), (0, 0, 1), 15, 26, "w", seg=32)
    # gear: toothed rim with the web recessed below the face (lightening holes), boss and shaft
    s += GE.gear3(cam, (0, 0, -hw / 2), (0, 0, 1), z1, r1, hw, "w", helix=psi, phase=ph1, slices=1)
    rin, dep, zt = r1 - 13, 20, hw / 2
    s += stepped_hole(cam, 0, 0, zt, [(rin, dep)], last="w")
    rim = hole_ell(cam, 0, 0, zt, rin)
    for k in range(6):
        a = 2 * math.pi * k / 6 + .3
        s += (hole_ell(cam, 50 * math.cos(a), 50 * math.sin(a), zt - dep, 11) & rim).svg("bg")
    s += GE.cyl(cam, (0, 0, zt - dep), (0, 0, 1), 24, dep + 4, "w", seg=32)
    s += GE.cyl(cam, (0, 0, zt + 4), (0, 0, 1), 15, 22, "w", seg=32)
    # pinion, integral with its shaft (opposite hand)
    hp = hw + 6
    s += GE.cyl(cam, (C[0], C[1], -hp / 2 - 40), (0, 0, 1), 13, 40, "w", seg=32)
    s += GE.gear3(cam, (C[0], C[1], -hp / 2), (0, 0, 1), z2, r2, hp, "w", helix=-psi, phase=ph2, slices=1)
    s += GE.cyl(cam, (C[0], C[1], hp / 2), (0, 0, 1), 15, 10, "w", seg=32) + GE.cyl(cam, (C[0], C[1], hp / 2 + 10), (0, 0, 1), 13, 46, "w", seg=32)
    # inset: one tooth in section, carburised case following the profile
    ix, iy, k = 283, 52, 1.36
    s += rect(250, 10, 66, 64, "void", 6)
    out_ = [(-22, 14), (-22, 0), (-14, 0), (-11.5, -1.5), (-5.2, -25), (-3.5, -26.5), (3.5, -26.5), (5.2, -25), (11.5, -1.5), (14, 0), (22, 0), (22, 14)]
    in_ = [(-22, 14), (-22, 3), (-13.5, 3), (-9.0, 0.6), (-3.2, -21.9), (-2.3, -23.3), (2.3, -23.3), (3.2, -21.9), (9.0, 0.6), (13.5, 3), (22, 3), (22, 14)]
    s += section([(ix + x_ * k, iy + y_ * k) for x_, y_ in out_], "w3", 3)
    s += section([(ix + x_ * k, iy + y_ * k) for x_, y_ in in_], "w", 3)
    s += rect(250, 10, 66, 64, "o", 6)
    return s


def ring_yz(R, Ri, a0, a1, cy=0.0, cz=0.0, seg=28):
    """annular sector in the (y,z) plane (angles from +y toward +z), outline (y,z,fid) for X()."""
    pts_ = [(cy + R * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), cz + R * math.sin(math.radians(a0 + (a1 - a0) * k / seg)), 10 + k * 8 // seg)
            for k in range(seg + 1)]
    pts_ += [(cy + Ri * math.cos(math.radians(a1 - (a1 - a0) * k / seg)), cz + Ri * math.sin(math.radians(a1 - (a1 - a0) * k / seg)), 30 + k * 8 // seg)
             for k in range(seg + 1)]
    pts_[seg] = pts_[seg][:2] + (1,)
    pts_[-1] = pts_[-1][:2] + (2,)
    return pts_


@part("propulsion.prgbox")
def _():
    L, Wd, Hh, t = 240, 100, 220, 8
    zo, zi = 92, 92 + 84.7          # output (gear) and input (pinion) shaft heights
    z1, z2, m = 40, 11, 3.32
    r1, r2 = z1 * m / 2, z2 * m / 2

    def fn(sc):
        BOX(sc, 0, -Wd, 0, L, 2 * Wd, 10, "w", 200)                      # bottom
        BOX(sc, 0, Wd - t, 0, L, t, Hh, "w", 190)                        # back wall
        BOX(sc, L - t, -Wd, 0, t, 2 * Wd, Hh, "w", 180)                  # fore end wall (inside face visible)
        BOX(sc, 0, -Wd, 10, L, t, 26, "w", -30)                          # low front wall (sump)
        for zc, r in ((zo, 16), (zi, 12)):
            RING(sc, (L - t - 1.5, 0, zc), (1, 0, 0), r + 7, r, 1.5, "alu", -5)
        # output shaft + gear (with boss), thrust collar and pads (aft end, left)
        CYL(sc, (t, 0, zo), (1, 0, 0), 16, L - 2 * t, "w", 50)
        CYL(sc, (88, 0, zo), (1, 0, 0), 30, 64, "w", 20)
        sc.add(GE.gear3(sc.cam, (95, 0, zo), (1, 0, 0), z1, r1, 50, "w", helix=12, phase=math.pi / 2 - math.pi / z1, slices=1),
               ((95, -r1 - 3, zo - r1 - 3), (145, r1 + 3, zo + r1 + 3)), 10)
        # input shaft: pinion and multi-plate clutch (drum cut open), fore end on the right
        CYL(sc, (t, 0, zi), (1, 0, 0), 12, L - 2 * t, "w", 60)
        sc.add(GE.gear3(sc.cam, (90, 0, zi), (1, 0, 0), z2, r2, 58, "w", helix=-12, phase=3 * math.pi / 2, slices=1),
               ((90, -r2 - 3, zi - r2 - 3), (148, r2 + 3, zi + r2 + 3)), 8)
        X(sc, 218, 4, [(u, v, f) for u, v, f in ring_yz(36, 12, 0, 360, 0, zi, 24)], "w", 40, smooth=True)
        for k in range(5):
            X(sc, 210 - k * 7, 3, [(u, v, f) for u, v, f in ring_yz(31 if k % 2 else 27, 13 if k % 2 else 17, 0, 360, 0, zi, 24)],
              "cu" if k % 2 else "w", 30 + k, smooth=True)
        X(sc, 174, 44, ring_yz(36, 32, 180, 450, 0, zi), "w", 0, smooth=True)
        # aft end wall (outside face visible), bearings, split flange
        BOX(sc, 0, -Wd, 0, t, 2 * Wd, Hh, "w", -60)
        BOX(sc, -7, -Wd, zo - 4, 7, 2 * Wd, 8, "w", -70)
        for zc, r in ((zo, 16), (zi, 12)):
            RING(sc, (-1.5, 0, zc), (1, 0, 0), r + 7, r, 1.5, "alu", -72)
        # shaft ends outside: output flange (aft), input coupling (fore)
        CYL(sc, (-58, 0, zo), (1, 0, 0), 16, 58, "w", -74)
        CYL(sc, (-20, 0, zo), (1, 0, 0), 40, 9, "w", -75)              # thrust collar
        for k in range(8):
            a0 = k * 45 + 4
            X(sc, -25, 5, [(u, v + zo, f) for u, v, f in sector(19, 38, a0, a0 + 37, 6)], "alu", -77)
        CYL(sc, (-68, 0, zo), (1, 0, 0), 44, 10, "w", -80)
        CYL(sc, (L, 0, zi), (1, 0, 0), 12, 30, "w", 220)
        CYL(sc, (L + 30, 0, zi), (1, 0, 0), 26, 10, "w", 230)
        # lube oil pump with motor on the aft wall, piping to the top
        CYL(sc, (-18, -72, 32), (1, 0, 0), 11, 18, "w", -60)
        CYL(sc, (-44, -72, 32), (1, 0, 0), 13, 26, "dk", -62)

        def extras(s_):
            cam = s_.cam
            o = ""
            for k in range(8):
                a = 2 * math.pi * (k + .5) / 8
                o += hole3(cam, (-68.2, 32 * math.cos(a), zo + 32 * math.sin(a)), (1, 0, 0), 3.2)
            for k in range(9):
                yy = -Wd + 10 + k * 22.5
                o += hole3(cam, (-3.5, yy, zo + 4.1), (0, 0, 1), 1.8)
            a, b = cam.xy((-6, -72, 43)), cam.xy((-6, -72, Hh - 20))
            c = cam.xy((4, -72, Hh - 4))
            o += '<path class="pipe" d="M%s %sL%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]))
            wl = ""
            for p0, p1 in (((t, Wd - t, Hh - 2), (L - t, Wd - t, Hh - 2)), ((L - t - .5, Wd - t, 12), (L - t - .5, Wd - t, Hh - 2)),
                           ((t, -Wd + t, 10.5), (L - t, -Wd + t, 10.5)), ((-.3, -Wd + 1, 12), (-.3, -Wd + 1, Hh - 2))):
                a_, b_ = cam.xy(p0), cam.xy(p1)
                wl += "M%s %sL%s %s" % (n(a_[0]), n(a_[1]), n(b_[0]), n(b_[1]))
            return o + '<path class="grit" d="%s"/>' % wl
        sc.top.append(extras)
    return fit_scene(fn, 24, 28, (14, 10, 306, 182))


def _vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _clip_val(poly_, t, keep_ge=True):
    """clip polygon of (x, y, v) to v >= t (or v < t), interpolating along edges."""
    out = []
    for i in range(len(poly_)):
        a, b = poly_[i - 1], poly_[i]
        ia, ib = (a[2] >= t) == keep_ge, (b[2] >= t) == keep_ge
        if ib:
            if not ia:
                f = (t - a[2]) / ((b[2] - a[2]) or 1e-9)
                out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, t))
            out.append(b)
        elif ia:
            f = (t - a[2]) / ((b[2] - a[2]) or 1e-9)
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, t))
    return out


def shaded_grid(cam, G, mat="cu", LV=5, mid=0.35, span=0.75, amax=0.9, light=None):
    """smoothly shaded surface patch: G[i][j] grid of 3D points. Base fill = mat s2; lit areas get
    mat s1 bands, shaded areas mat s4 bands (contour-clipped, so band edges follow the shading)."""
    N, M = len(G) - 1, len(G[0]) - 1
    D = cam.D
    cn = [[None] * M for _ in range(N)]
    for i in range(N):
        for j in range(M):
            q = [G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1]]
            nr = GE._norm(GE._cross(_vsub(q[1], q[0]), _vsub(q[3], q[0])))
            if GE._dot(nr, D) > 0:
                nr = (-nr[0], -nr[1], -nr[2])
            cn[i][j] = nr
    val = [[0.0] * (M + 1) for _ in range(N + 1)]
    for i in range(N + 1):
        for j in range(M + 1):
            acc = [0.0, 0.0, 0.0]
            for a in (i - 1, i):
                for b in (j - 1, j):
                    if 0 <= a < N and 0 <= b < M:
                        acc = [acc[0] + cn[a][b][0], acc[1] + cn[a][b][1], acc[2] + cn[a][b][2]]
            nr = GE._norm(tuple(acc))
            val[i][j] = min(1.0, max(-1.0, (mid - GE._dot(nr, light or GE.LIGHT)) / span)) * LV
    S = [[cam.xy(G[i][j]) for j in range(M + 1)] for i in range(N + 1)]
    dark = [""] * (LV + 1)
    lite = [""] * (LV + 1)
    for i in range(N):
        for j in range(M):
            pl = [(S[i][j][0], S[i][j][1], val[i][j]), (S[i + 1][j][0], S[i + 1][j][1], val[i + 1][j]),
                  (S[i + 1][j + 1][0], S[i + 1][j + 1][1], val[i + 1][j + 1]), (S[i][j + 1][0], S[i][j + 1][1], val[i][j + 1])]
            lo, hi_ = min(p[2] for p in pl), max(p[2] for p in pl)
            for k in range(-LV, LV + 1):
                if k == 0 or k + 0.5 < lo or k - 0.5 > hi_:
                    continue
                q = pl
                if k > -LV:
                    q = _clip_val(q, k - 0.5, True)
                if k < LV and q:
                    q = _clip_val(q, k + 0.5, False)
                if len(q) > 2:
                    d_ = "M" + " L".join(n(x) + " " + n(y) for x, y, _ in q) + "Z"
                    if k > 0:
                        dark[k] += d_
                    else:
                        lite[-k] += d_
    rim = [S[i][0] for i in range(N + 1)] + [S[N][j] for j in range(M + 1)] + [S[i][M] for i in range(N, -1, -1)] + [S[0][j] for j in range(M, -1, -1)]
    o = '<path class="%ss2" d="%s"/>' % (mat, P(rim))
    for k in range(1, LV + 1):
        if lite[k]:
            o += '<path class="%ss1" opacity="%.2f" d="%s"/>' % (mat, k / LV * amax, lite[k])
        if dark[k]:
            o += '<path class="%ss4" opacity="%.2f" d="%s"/>' % (mat, k / LV * amax * 0.85, dark[k])
    return o, S

def prop_blades(cam, R, rh, Z=5, P_D=0.7, skew=30.0, th0=90.0, kc=1.15, N=14, M=7, mat="cu", y0=0.0, root=None):
    """Skewed propeller blades on a shaft along +y (forward = +y), disc in the x-z plane.
    Returns a list of (depth, svg) per blade, for depth sorting with the hub."""
    Pp = P_D * 2 * R
    k_ = Pp / (2 * math.pi)
    D = cam.D
    out = []
    r0 = root if root is not None else rh * 0.98

    def chord(x):
        return kc * R * (0.25 + 0.75 * x - 0.6 * x * x) * math.sqrt(max(0.0, 1 - x ** 4))

    def pt(b, r, s):
        x = (r - rh) / (R - rh)
        thm = math.radians(th0 + b * 360.0 / Z + skew * max(x, 0) ** 1.7)
        cosphi = 2 * math.pi * r / math.hypot(2 * math.pi * r, Pp)
        dl = chord(max(x, 0)) * cosphi / (2 * r)
        th = thm + s * dl
        return (r * math.cos(th), y0 + k_ * (thm - th), r * math.sin(th))
    rs = [r0 + (R - r0) * (1 - math.cos(math.pi * i / N / 2 * 1.0)) ** 1.0 for i in range(N + 1)]
    rs = [r0 + (R - r0) * (i / N) ** 0.9 for i in range(N + 1)]
    ss = [-1 + 2 * j / M for j in range(M + 1)]
    LB = GE._norm((-0.75, -0.3, 0.6))
    for b in range(Z):
        G = [[pt(b, r, s_) for s_ in ss] for r in rs]
        # blade thickness: the opposite face, offset forward, thick at the root and thin at the tip
        tk = [0.05 * R * (1 - (r - rh) / (R - rh)) ** 1.2 + 0.006 * R for r in rs]
        Gb = [[(p_[0], p_[1] + tk[i] * (1 - abs(ss[j]) ** 2 * 0.85), p_[2]) for j, p_ in enumerate(row)] for i, row in enumerate(G)]
        back = [cam.xy(Gb[i][0]) for i in range(N + 1)] + [cam.xy(Gb[N][j]) for j in range(M + 1)] + [cam.xy(Gb[i][M]) for i in range(N, -1, -1)]
        svg = '<path class="%ss4 x" d="%s"/>' % (mat, P(back))
        sv2, S = shaded_grid(cam, G, mat, light=LB)
        svg += sv2
        rim = [S[i][0] for i in range(N + 1)] + [S[N][j] for j in range(M + 1)] + [S[i][M] for i in range(N, -1, -1)]
        svg += '<path class="el" d="%s"/>' % P(rim, False)
        iso = ""
        for i in (4, 7, 10):
            if i < N:
                iso += P([cam.xy(G[i][j]) for j in range(M + 1)], False)
        svg += '<path class="gr" d="%s"/>' % iso
        cen = G[N // 2][M // 2]
        out.append((cam.P(cen)[2], svg))
    return out


@part("propulsion.prfpp")
def _():
    R = 91.0
    rh = R / 6.0
    hl = 1.2 * 2 * rh
    cam = GE.Cam(144, 97, -44, 18, 1.0)
    s = shadow(150, 188, 104, 9)
    hub = GE.cyl(cam, (0, -hl / 2, 0), (0, 1, 0), rh, hl, "cu", scale=lambda t: 0.9 + 0.2 * t)
    a = -hl / 2 - 0.2
    hub += hole3(cam, (0, a, 0), (0, -1, 0), rh * 0.66, "cus2 x") + hole3(cam, (0, a, 0), (0, -1, 0), rh * 0.42, "bg")
    hub += hole3(cam, (0, a + 1.0, 0), (0, -1, 0), rh * 0.38, "m3")
    hc = cam.P((0, 0, 0))[2]
    items = prop_blades(cam, R, rh, root=rh * 0.95)
    items.sort(key=lambda it: -it[0])
    for dep, svg in items:
        if dep > hc:
            s += svg
    s += hub
    for dep, svg in items:
        if dep <= hc:
            s += svg
    fx, fy = cam.xy((R * 1.3, R * 0.9, -R - 2))
    hx, hy = cam.xy((R * 1.3, R * 0.9, -R - 2 + 0.34 * R))
    s += person(fx, fy, fy - hy)
    return s


def wavy(x0, x1, y, amp=2.2, n_=4):
    """points of a wavy break line from x0 to x1 at height y."""
    return [(x0 + (x1 - x0) * k / (n_ * 6), y + amp * math.sin(math.pi * 2 * k / 6)) for k in range(n_ * 6 + 1)]


@part("propulsion.prcpp")
def _():
    y0 = 104
    hx0, hx1, hr, wt = 96, 210, 47, 9           # hub (x0..x1, radius, wall)
    bx = 146                                    # blade axis
    o = shadow(160, 190, 120, 6)
    # faint blades behind (other blades of the propeller)
    for sg in (-1, 1):
        a = math.radians(-38 if sg < 0 else 142)
        bl = []
        for k in range(40):
            t = 2 * math.pi * k / 40
            u, v = 17 * math.cos(t) * (1 - 0.25 * math.sin(t)), 58 * math.sin(t)
            bl.append((bx - 6 + (u * math.cos(a) - (v - 46) * math.sin(a)), y0 + (u * math.sin(a) + (v - 46) * math.cos(a))))
        o += faint(pg(bl, "cus3"), 0.4)
    # shaft (left) with the double oil tube inside, flange bolted to the hub
    o += rect(6, y0 - 14, 82, 28, "w") + rect(84, y0 - 36, 12, 72, "w2")
    for dy in (-27, 27):
        o += rect(80, y0 + dy - 2.5, 20, 5, "w3")
    o += rect(6, y0 - 6.5, 90, 13, "void") + rect(6, y0 - 3, 90, 6, "w2")
    # hub (section) with blade ports top and bottom; aft cone
    o += pg([(hx0, y0 - hr), (hx1, y0 - hr), (hx1, y0 + hr), (hx0, y0 + hr)], "void")
    for sg in (-1, 1):
        wall = [(hx0, y0 + sg * (hr - wt)), (bx - 30, y0 + sg * (hr - wt)), (bx - 30, y0 + sg * hr), (hx0, y0 + sg * hr)]
        o += section(wall, "w", 3)
        wall2 = [(bx + 30, y0 + sg * (hr - wt)), (hx1, y0 + sg * (hr - wt)), (hx1, y0 + sg * hr), (bx + 30, y0 + sg * hr)]
        o += section(wall2, "w", 3)
    o += section([(hx0, y0 - hr + wt), (hx0 + 8, y0 - hr + wt), (hx0 + 8, y0 - 7), (hx0, y0 - 7)], "w", 3)
    o += section([(hx0, y0 + 7), (hx0 + 8, y0 + 7), (hx0 + 8, y0 + hr - wt), (hx0, y0 + hr - wt)], "w", 3)
    cone = [(hx1, y0 - hr), (hx1 + 18, y0 - hr + 6), (hx1 + 44, y0 - 10), (hx1 + 50, y0), (hx1 + 44, y0 + 10), (hx1 + 18, y0 + hr - 6), (hx1, y0 + hr)]
    o += pg(cone, "w")
    # servo cylinder (aft part of the hub) with piston; piston rod -> yoke
    cyl_o = [(176, y0 - 30), (hx1, y0 - 30), (hx1, y0 + 30), (176, y0 + 30)]
    cyl_i = [(180, y0 - 25), (hx1 - 4, y0 - 25), (hx1 - 4, y0 + 25), (180, y0 + 25)]
    o += section([cyl_o, cyl_i], "w", 3)
    o += pg([(180, y0 - 25), (hx1 - 4, y0 - 25), (hx1 - 4, y0 + 25), (180, y0 + 25)], "void")
    o += pg([(189, y0 - 24.6), (199, y0 - 24.6), (199, y0 + 24.6), (189, y0 + 24.6)], "w2")       # servo piston
    o += pg([(bx - 6, y0 - 4.5), (192, y0 - 4.5), (192, y0 + 4.5), (bx - 6, y0 + 4.5)], "alu")       # piston rod
    o += pg([(bx - 12, y0 - 33), (bx + 12, y0 - 33), (bx + 12, y0 + 33), (bx - 12, y0 + 33)], "w2")  # yoke
    for sg in (-1, 1):
        o += pg([(bx + 5, y0 + sg * 33), (bx + 11, y0 + sg * 33), (bx + 11, y0 + sg * 22), (bx + 5, y0 + sg * 22)], "void")
    # crank rings with eccentric pins, blade flanges + bolts, blade roots
    for sg in (-1, 1):
        o += pg([(bx - 32, y0 + sg * (hr - wt)), (bx + 32, y0 + sg * (hr - wt)), (bx + 32, y0 + sg * (hr - wt - 9)), (bx - 32, y0 + sg * (hr - wt - 9))], "w")
        o += pg([(bx + 6, y0 + sg * (hr - wt - 9)), (bx + 10, y0 + sg * (hr - wt - 9)), (bx + 10, y0 + sg * 24), (bx + 6, y0 + sg * 24)], "w3")
        o += pg([(bx - 27, y0 + sg * hr), (bx + 27, y0 + sg * hr), (bx + 27, y0 + sg * (hr + 6)), (bx - 27, y0 + sg * (hr + 6))], "cu")
        for dx in (-19, 19):
            o += pg([(bx + dx - 2, y0 + sg * (hr + 8)), (bx + dx + 2, y0 + sg * (hr + 8)), (bx + dx + 2, y0 + sg * (hr - wt - 6)), (bx + dx - 2, y0 + sg * (hr - wt - 6))], "w3")
            o += pg([(bx + dx - 4, y0 + sg * (hr + 6)), (bx + dx + 4, y0 + sg * (hr + 6)), (bx + dx + 4, y0 + sg * (hr + 9)), (bx + dx - 4, y0 + sg * (hr + 9))], "w2")
        yt = y0 + sg * 92
        top = wavy(bx - 13, bx + 15, yt, 1.8, 2)
        root = [(bx - 21, y0 + sg * (hr + 6))] + [(bx - 16, y0 + sg * 66)] + top + [(bx + 20, y0 + sg * 66), (bx + 23, y0 + sg * (hr + 6))]
        o += pg(root, "cu")
        o += path(P([(bx - 2, y0 + sg * (hr + 8)), (bx + 1, yt)], False), "o thin dash")
    # oil supply: inner tube -> aft chamber (ahead), annulus -> fore chamber (astern)
    o += path("M12 %s L%s %s" % (n(y0), n(170), n(y0)), "uv") + head(176, y0, 0, 6)
    o += path("M12 %s L%s %s L%s %s" % (n(y0 - 5), n(176), n(y0 - 5), n(184), n(y0 - 18)), "fo dash")
    o += head(186, y0 - 21, math.radians(-60), 6).replace('class="af"', 'class="fdot"')
    o += path("M200 %s L%s %s" % (n(y0 + 14), n(202), n(y0 + 14)), "uv") + head(205, y0 + 14, 0, 6)
    # blade turns: arc arrow around the blade axis
    o += rot(bx + 1, 40, 26, 6, 200, 340)
    return o


@part("propulsion.prshaft")
def _():
    s = shadow(160, 190, 140, 7)
    r = 9.0
    A = (1, 0, 0)

    def cy(cam, x, rr, L_, mat="w", dk=0, **kw):
        return GE.prism(cam, (x, 0, 0), A, GE.circle_outline(rr, 32, 12), L_, mat, smooth=True, dark=dk, **kw)

    def bolts(cam, x, rr, nb=8, br=1.6):
        o = ""
        for k in range(nb):
            a = 2 * math.pi * (k + .5) / nb
            o += hole3(cam, (x - .2, rr * math.cos(a), rr * math.sin(a)), A, br)
        return o
    # ---- propeller shaft (top): coupling flange, journals, seal liner, coating, taper, thread
    cam = GE.Cam(160, 60, 16, 14, 1.0)
    x0 = -132
    s += cy(cam, x0, 16.5, 4.5) + bolts(cam, x0, 12.2)
    x = x0 + 4.5
    for L_, rr, mat, dk in ((36, r, "w", 1), (24, r + .3, "alu", 0), (60, r, "w", 1), (44, r + .3, "alu", 0), (16, r + 1.6, "alu", 0),
                            (14, r + .4, "gw", 0)):
        s += cy(cam, x, rr, L_, mat, dk)
        x += L_
    xt = x
    s += cy(cam, x, r, 22, "w", 1, scale=lambda t: 1 - 0.17 * t)
    x += 22
    s += cy(cam, x, 6.2, 13, "w", 1)
    d = ""
    for k in range(6):
        a, b = cam.xy((x + 1.5 + k * 2, -1, 6.2)), cam.xy((x + 2.6 + k * 2, -6.2, -1))
        d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    s += '<path class="thread" d="%s"/>' % d
    xe = x + 13
    a, b = cam.xy((x0 - 2, 0, 0)), cam.xy((xe + 2, 0, 0))
    s += line(a[0], a[1], b[0], b[1], "hid")
    # ---- intermediate shaft (bottom): flanges both ends, bearing journal
    cam2 = GE.Cam(124, 146, 16, 14, 1.0)
    x0 = -106
    s += cy(cam2, x0, 16.5, 4.5) + bolts(cam2, x0, 12.2)
    s += cy(cam2, x0 + 4.5, r, 84, "w", 1) + cy(cam2, x0 + 88.5, r + .3, 28, "alu") + cy(cam2, x0 + 116.5, r, 91, "w", 1)
    s += cy(cam2, x0 + 207.5, 16.5, 4.5) + bolts(cam2, x0 + 207.5, 12.2)
    # ---- inset: blue marking on the taper (contact along the generator lines)
    bx0, by0 = 240, 116
    s += rect(bx0, by0, 72, 56, "void", 6)
    tp = [(bx0 + 8, by0 + 13), (bx0 + 64, by0 + 18), (bx0 + 64, by0 + 38), (bx0 + 8, by0 + 43)]
    s += pg(tp, "w")
    hd = ""
    for k in range(12):
        xx = bx0 + 11 + k * 4.6
        f = (xx - bx0 - 8) / 56
        ya, yb = by0 + 13 + 5 * f + 3, by0 + 43 - 5 * f - 3
        yy = ya
        while yy < yb - 2:
            hd += "M%s %sL%s %s" % (n(xx), n(yy), n(xx + 0.4), n(min(yy + 4 + (k % 3), yb)))
            yy += 6 + (k * 7 % 5)
    s += '<path class="fo" d="%s"/>' % hd
    s += rect(bx0, by0, 72, 56, "o", 6)
    a = cam.xy((xt + 10, 0, -r))
    s += line(a[0], a[1] + 1, bx0 + 24, by0, "leadl")
    return s


@part("propulsion.prstern")
def _():
    y0 = 104
    o = ""
    # ---- hull structure (steel, cut): shell plating converging to the stern frame, aft-peak bulkhead
    up = [(30, 10), (214, 54), (214, 62), (30, 18)]
    lo = [(30, 198), (214, 154), (214, 146), (30, 190)]
    o += section(up, "m2", 3.2) + section(lo, "m2", 3.2)
    o += section([(50, 14), (58, 14), (58, y0 - 28), (50, y0 - 28)], "m2", 3.2) + section([(50, y0 + 28), (58, y0 + 28), (58, 194), (50, 194)], "m2", 3.2)
    o += section([(212, 50), (232, 50), (232, y0 - 28), (212, y0 - 28)], "m2", 3.2)
    o += section([(212, y0 + 28), (232, y0 + 28), (232, 158), (212, 158)], "m2", 3.2)
    # ---- stern tube (steel) with oil inside; bearings with cast-iron backing and white metal
    for sg in (-1, 1):
        o += section([(58, y0 + sg * 21), (212, y0 + sg * 21), (212, y0 + sg * 28), (58, y0 + sg * 28)], "m", 3.2)
    o += pg([(58, y0 - 21), (212, y0 - 21), (212, y0 + 21), (58, y0 + 21)], "fl")
    o += section([(58, y0 - 34), (64, y0 - 34), (64, y0 - 21), (58, y0 - 21)], "m", 3) + section([(58, y0 + 21), (64, y0 + 21), (64, y0 + 34), (58, y0 + 34)], "m", 3)
    for xa, xb in ((66, 94), (152, 212)):
        for sg in (-1, 1):
            o += fe(section([(xa, y0 + sg * 15), (xb, y0 + sg * 15), (xb, y0 + sg * 21), (xa, y0 + sg * 21)], "w", 2.6))
        o += pg([(xa, y0 - 15), (xb, y0 - 15), (xb, y0 - 13.2), (xa, y0 - 13.2)], "alu")
        if xa < 100:
            o += pg([(xa, y0 + 13.2), (xb, y0 + 13.2), (xb, y0 + 15), (xa, y0 + 15)], "alu")
    # slope-bored aft bearing: lower bore line falls toward the propeller (exaggerated)
    o += pg([(152, y0 + 13.2), (212, y0 + 15.6), (212, y0 + 17), (152, y0 + 15)], "alu")
    # ---- shaft (steel, ground) with the taper running into the propeller boss
    cam = GE.Cam(0, y0, 0, 0.01, 1.0)
    o += GE.cyl(cam, (0, 0, 0), (1, 0, 0), 13, 262, "m")
    o += GE.cyl(cam, (262, 0, 0), (1, 0, 0), 13, 60, "m", scale=lambda t: 1 - 0.14 * t)
    o += line(152, y0 + 13.2, 214, y0 + 13.2, "hid")
    # ---- liners (chrome steel) and lip seals (rubber): aft seal at the boss, forward seal inboard
    for sg in (-1, 1):
        o += pg([(226, y0 + sg * 13), (258, y0 + sg * 13), (258, y0 + sg * 15.5), (226, y0 + sg * 15.5)], "alu")
        o += section([(232, y0 + sg * 17), (254, y0 + sg * 17), (254, y0 + sg * 30), (232, y0 + sg * 30)], "m", 3)
        for k in range(4):
            xx = 235 + k * 5
            o += pg([(xx, y0 + sg * 23), (xx + 3.4, y0 + sg * 23), (xx + 3.4, y0 + sg * 18.2), (xx + 2.6, y0 + sg * 15.6), (xx + 1.4, y0 + sg * 18.2), (xx, y0 + sg * 18.2)], "rb")
        o += pg([(30, y0 + sg * 13), (56, y0 + sg * 13), (56, y0 + sg * 15.5), (30, y0 + sg * 15.5)], "alu")
        o += section([(34, y0 + sg * 17), (50, y0 + sg * 17), (50, y0 + sg * 30), (34, y0 + sg * 30)], "m", 3)
        for k in range(3):
            xx = 37 + k * 4.4
            o += pg([(xx, y0 + sg * 23), (xx + 3, y0 + sg * 23), (xx + 3, y0 + sg * 18.2), (xx + 2.2, y0 + sg * 15.6), (xx + 1.2, y0 + sg * 18.2), (xx, y0 + sg * 18.2)], "rb")
    # ---- propeller boss (copper alloy, cut) on the taper
    for sg in (-1, 1):
        bos = [(258, y0 + sg * 13), (320, y0 + sg * 11.2), (320, y0 + sg * 58), (270, y0 + sg * 58), (258, y0 + sg * 44)]
        o += cug(section(bos, "w", 3.2))
    return o


def hshaft(x0, x1, y, r, c="w"):
    """2D horizontal shaft with a cylindrical look (steel gradient + a highlight line)."""
    return rect(x0, y - r, x1 - x0, 2 * r, c) + line(x0 + 1, y - r * 0.45, x1 - 1, y - r * 0.45, "mgrid")


@part("propulsion.prinstall")
def _():
    ys = 66                                         # shaft centre line
    o = ""
    # ---------------- ship's after body (schematic longitudinal section)
    hull = [(6, 12), (304, 12), (304, 30), (284, 34), (262, 40), (246, 50), (240, 58), (240, 82), (226, 90), (196, 104), (6, 104)]
    o += pg(hull, "void")
    o += path("M%s %s Q 150 %s 300 %s" % (6, 105.5, 109, 105.5), "o thin dash")            # hull deflection (exaggerated)
    o += line(6, 96, 190, 96, "o thin") + line(176, 22, 176, 100, "tankw")                  # tank top, aft-peak bulkhead
    # stern frame boss, rudder
    o += section([(234, ys - 12), (244, ys - 12), (244, ys + 12), (234, ys + 12)], "m2", 2.6)
    o += pg([(292, 44), (304, 44), (306, 98), (296, 100)], "m2")
    # main engine (or gearbox) block
    o += pg([(18, 30), (82, 30), (86, 96), (14, 96)], "m2") + pg([(26, 20), (74, 20), (74, 30), (26, 30)], "m2")
    # shafting: intermediate shaft on two bearings, stern tube, propeller shaft, propeller
    o += hshaft(86, 176, ys, 4.2) + hshaft(176, 262, ys, 4.2)
    for xb in (110, 152):
        o += pg([(xb - 7, ys + 4), (xb + 7, ys + 4), (xb + 9, 96), (xb - 9, 96)], "w2")
    o += rect(176, ys - 7, 58, 14, "w2") + rect(176, ys - 4.2, 58, 8.4, "w")
    o += cug(pg([(252, ys - 9), (268, ys - 7), (268, ys + 7), (252, ys + 9)], "w"))
    o += cug(pg([(256, ys - 8), (252, ys - 34), (262, ys - 38), (266, ys - 8)], "w2") + pg([(256, ys + 8), (252, ys + 34), (262, ys + 38), (266, ys + 8)], "w"))
    for xf in (86, 131):
        o += rect(xf - 1.5, ys - 8, 3, 16, "w2")
    # laser tracker on its tripod, beam along the shaft centre line
    o += line(120, 30, 112, 50, "o") + line(120, 30, 128, 50, "o") + line(120, 30, 120, 50, "o")
    o += rect(115, 21, 10, 9, "m3", 2) + circ(120, 25.5, 2.2, "m")
    o += path("M120 30 L 120 %s" % n(ys), "laserl") + path("M 92 %s L 250 %s" % (n(ys), n(ys)), "laserl")
    # ---------------- inset A: portable line boring of the stern frame bore
    def frame_box(x, y, w=98, h=76):
        return rect(x, y, w, h, "void", 6)
    ax, ay = 6, 118
    a = frame_box(ax, ay)
    for xa in (ax + 18, ax + 60):
        a += section([(xa, ay + 12), (xa + 20, ay + 12), (xa + 20, ay + 30), (xa, ay + 30)], "m2", 2.6)
        a += section([(xa, ay + 46), (xa + 20, ay + 46), (xa + 20, ay + 64), (xa, ay + 64)], "m2", 2.6)
    a += pg([(ax + 12, ay + 30), (ax + 18, ay + 30), (ax + 18, ay + 46), (ax + 12, ay + 46)], "w2")   # bearing stands
    a += pg([(ax + 80, ay + 30), (ax + 86, ay + 30), (ax + 86, ay + 46), (ax + 80, ay + 46)], "w2")
    a += hshaft(ax + 4, ax + 94, ay + 38, 2.6)
    a += pg([(ax + 64, ay + 33), (ax + 72, ay + 33), (ax + 72, ay + 43), (ax + 64, ay + 43)], "w")    # tool head
    a += pg([(ax + 67, ay + 33), (ax + 70, ay + 33), (ax + 69.5, ay + 30.4), (ax + 67.5, ay + 30.4)], "t")
    a += rect(ax + 2, ay + 31, 8, 14, "dk", 2)                                                     # drive + feed
    a += path("M%s %s L%s %s" % (n(ax + 4), n(ay + 38), n(ax + 94), n(ay + 38)), "laserl")
    a += arrow(ax + 50, ay + 70, ax + 60, ay + 70)
    a += rect(ax, ay, 98, 76, "o", 6)
    o += a
    # ---------------- inset B: jack-up test at an intermediate bearing (+ load-lift graph)
    bx, by = 111, 118
    b = frame_box(bx, by)
    b += hshaft(bx + 4, bx + 94, by + 30, 5)
    b += pg([(bx + 40, by + 35), (bx + 56, by + 35), (bx + 59, by + 62), (bx + 37, by + 62)], "w2")
    b += rect(bx + 22, by + 46, 10, 16, "w") + rect(bx + 24, by + 35, 6, 11, "alu") + rect(bx + 16, by + 62, 66, 4, "m2")
    b += arrow(bx + 27, by + 56, bx + 27, by + 40)
    b += rect(bx + 24, by + 9, 7, 9, "m3", 3) + line(bx + 27.5, by + 18, bx + 27.5, by + 25, "o") + circ(bx + 27.5, by + 13.5, 2.4, "m")
    gx, gy = bx + 64, by + 5
    b += line(gx, gy + 16, gx + 28, gy + 16, "o") + line(gx, gy + 16, gx, gy, "o")
    b += path("M%s %s L%s %s L%s %s" % (n(gx), n(gy + 16), n(gx + 10), n(gy + 9), n(gx + 26), n(gy + 2)), "mfe")
    b += rect(bx, by, 98, 76, "o", 6)
    o += b
    # ---------------- inset C: propeller push-up with a hydraulic nut and oil injection
    cx, cy = 216, 118
    c = frame_box(cx, cy)
    c += pg([(cx + 4, cy + 33), (cx + 60, cy + 35), (cx + 60, cy + 41), (cx + 4, cy + 43)], "w")
    c += rect(cx + 60, cy + 35.5, 18, 5, "w")
    c += cug(section([(cx + 26, cy + 33.8), (cx + 58, cy + 34.9), (cx + 58, cy + 10), (cx + 30, cy + 10)], "w", 2.6))
    c += cug(section([(cx + 26, cy + 42.2), (cx + 58, cy + 41.1), (cx + 58, cy + 66), (cx + 30, cy + 66)], "w", 2.6))
    c += pg([(cx + 60, cy + 24), (cx + 74, cy + 24), (cx + 74, cy + 52), (cx + 60, cy + 52)], "w2")
    c += pg([(cx + 63, cy + 28), (cx + 71, cy + 28), (cx + 71, cy + 35), (cx + 63, cy + 35)], "fl")
    c += path("M%s %s L%s %s L%s %s" % (n(cx + 86), n(cy + 14), n(cx + 42), n(cy + 14), n(cx + 42), n(cy + 34)), "fo")
    c += head(cx + 42, cy + 34.4, math.pi / 2, 5).replace('class="af"', 'class="fdot"')
    c += arrow(cx + 52, cy + 72, cx + 30, cy + 72)
    c += rect(cx, cy, 98, 76, "o", 6)
    o += c
    return o
