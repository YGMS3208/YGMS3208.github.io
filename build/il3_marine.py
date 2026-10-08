"""v3 shaded-3D part drawings for the marine systems (marine2 / marine4 / marineaux / propulsion).
Re-draws the keys whose older drawings (il_parts_marine*.py) had insets, arrows, labels or were too heavy.
Keys not re-drawn here keep their il_parts_marine* drawings."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P
import il_parts_marine as OM


def person_at(cam, W, h_units):
    """human silhouette standing at world point W (feet), h_units tall in world units (1.7 m)."""
    fx, fy = cam.xy(W)
    hx, hy = cam.xy((W[0], W[1], W[2] + h_units))
    return OM.person(fx, fy, fy - hy)


def bolts(cam, C, A, rb, n_, r, c="bg", a0=0.5):
    o = ""
    E1, E2, _ = GE.frame(A)
    for k in range(n_):
        a = 2 * math.pi * (k + a0) / n_
        o += hole3(cam, tuple(C[i] + rb * (math.cos(a) * E1[i] + math.sin(a) * E2[i]) for i in range(3)), A, r, c)
    return o


# =====================================================================================
# marine2.m2frame — same frame box as before, without the guide arrow
# =====================================================================================
@part("marine2.m2frame")
def _():
    L, Wd, Hh, t = 360, 90, 135, 10
    xp = [0, 120, 240, 360]
    BX, Y_, rrect = OM.BOX, OM.Y, OM.rrect

    def cut_edge():
        pts = [(242, Hh), (236, 118), (244, 96), (235, 76), (240, 58)]
        for k in range(1, 13):
            xx = 240 - k * 20
            pts.append((xx, 50 + 5 * math.sin(k * 1.7)))
        return pts

    def fn(sc):
        BX(sc, 0, Wd - t, 0, L, t, Hh, "w", 80)
        BX(sc, 0, Wd - t, Hh, L, t + 10, 7, "w", 70, cap_mat="alu")
        BX(sc, 0, Wd - t, -7, L, t + 10, 7, "w", 90)
        for i, x0 in enumerate(xp):
            xa = min(max(x0 - 7, 0), L - 14)
            OM.X(sc, xa, 14, [(-Wd + t, 0), (Wd - t, 0), (Wd - t, Hh), (-Wd + t, Hh)], "w", 20 - i, cap_mat="w")
            if x0 < L:
                BX(sc, xa + 14, -13, 16, 5, 26, Hh - 30, "alu", 10 - i)
        for x0 in (7, 120):
            OM.CYL(sc, (x0, -Wd + 5, 0), (0, 0, 1), 5, Hh, "w", -30)
        ce = cut_edge()
        Y_(sc, -Wd + t, t, [(0, 0), (L, 0), (L, Hh)] + ce + [(0, ce[-1][1])], "w", -40)
        BX(sc, 236, -Wd - 10, Hh, L - 236, t + 10, 7, "w", -45, cap_mat="alu")
        BX(sc, 0, -Wd - 10, -7, L, t + 10, 7, "w", -45)
        Y_(sc, -Wd, 3, [(xx, zz, f) for xx, zz, f in rrect(266, 26, 334, 82, 10)], "w", -50)
        OM.CYL(sc, (300, -Wd - 3, 106), (0, -1, 0), 13, 8, "w", -52)
        OM.CYL(sc, (300, -Wd - 11, 106), (0, -1, 0), 9, 5, "w", -53)

        def marks(s_):
            cam = s_.cam
            o = ""
            for x0 in xp:
                o += hole3(cam, (min(max(x0, 8), L - 8), Wd - 5, Hh + 7.2), (0, 0, 1), 3.4)
            for k in range(12):
                o += hole3(cam, (15 + k * 30, Wd + 6, Hh + 7.2), (0, 0, 1), 2.2)
            for k in range(4):
                xx = 250 + k * 30
                o += hole3(cam, (xx, -Wd - 6, Hh + 7.2), (0, 0, 1), 2.2)
                o += hole3(cam, (xx, -Wd - 6, 0.2), (0, 0, 1), 2.2)
            for k in range(8):
                o += hole3(cam, (15 + k * 30, -Wd - 6, 0.2), (0, 0, 1), 2.2)
            for k in range(8):
                a = 2 * math.pi * k / 8
                o += hole3(cam, (300 + 30 * math.cos(a), -Wd - 3.2, 54 + 22 * math.sin(a)), (0, -1, 0), 1.6, "m3")
            return o
        sc.top.append(marks)
    return OM.fit_scene(fn, -34, 26, (22, 12, 298, 180))


# =====================================================================================
# crankshafts (axis x, aft flange at x=0 facing the light, az > 0)
# =====================================================================================
def crankshaft(phases, rj, rp, e, tw, lj, lp, web, front, aft, az=22, el=20, area=(20, 30, 300, 172), seg=18, man=None):
    """web(phi) -> (y,z) outline; front/aft: lists of (L, r) cylinders before/after the throws.
    aft is drawn first from x=0 (the lit flange end); man=(units tall,) adds a person."""
    def fn(sc):
        x = 0
        for i, (L, r) in enumerate(aft):
            if i == 0:
                def face(s_, r=r):
                    return hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), r * .3, "w3") + bolts(s_.cam, (-.1, 0, 0), (-1, 0, 0), r * .78, 10, r * .07)
                RAW(sc, face, ((-.2, -r, -r), (0, r, r)), -2)
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=32 if r > rj * 1.4 else seg, bands=10)
            x += L
        for ph in phases:
            CYL(sc, (x, 0, 0), (1, 0, 0), rj, lj, "w", seg=seg, bands=8)
            x += lj
            py, pz = e * math.cos(math.radians(ph)), e * math.sin(math.radians(ph))
            X(sc, x, tw, web(ph), "w", smooth=True, dark=1, cap_mat="w3")
            x += tw
            CYL(sc, (x, py, pz), (1, 0, 0), rp, lp, "w", seg=seg, bands=8)
            x += lp
            X(sc, x, tw, web(ph), "w", smooth=True, dark=1, cap_mat="w3")
            x += tw
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, lj, "w", seg=seg, bands=10)
        x += lj
        for L, r in front:
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=seg, bands=10)
            x += L
        if man:
            zg = -max(e + rp, max(r for _, r in aft)) - 4
            return person_at(sc.cam, (x + 30, 60, zg), man)
    return fit(fn, az, el, area, sh_ry=7, sh_k=.46)


@part("marine2.m2crank")
def _():
    # semi-built: 6 throws (pin + two stadium webs), shrink-fitted journals, thrust collar + coupling flange aft
    rj, rp, e = 26, 27, 52

    def web(ph):
        py, pz = e * math.cos(math.radians(ph)), e * math.sin(math.radians(ph))
        return banded(hull(arc(py, pz, 37, 0, 360, 14) + arc(0, 0, 40, 0, 360, 14)), 2)
    order = [0, 240, 120, 180, 60, 300]
    return crankshaft(order, rj, rp, e, 15, 20, 30, web, front=[(14, 22)], aft=[(12, 54), (16, 28), (12, 62), (16, 28)],
                      az=20, el=20, man=70)


@part("marine4.m4crank")
def _():
    # one-piece forged inline-6: pins 1-6 / 2-5 / 3-4 at 120 deg, webs with counterweights, flange aft
    rj, rp, e = 24, 22, 40

    def web(ph):
        py, pz = e * math.cos(math.radians(ph)), e * math.sin(math.radians(ph))
        return banded(hull(arc(py, pz, 28, ph - 90, ph + 90, 8) + arc(0, 0, 58, ph + 180 - 52, ph + 180 + 52, 8)), 2)
    return crankshaft([0, 240, 120, 120, 240, 0], rj, rp, e, 12, 20, 22, web, front=[(10, 18), (16, 15)], aft=[(10, 44), (12, 30)],
                      az=22, el=20)


def RG(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=48, feat=10, **kw):
    """tube with a lightly-banded bore (few edge lines). Not compacted: the bore's far wall must not
    get its edge lines drawn over the near outer wall."""
    a = GE._norm(A)
    from il3_lib import _bb
    sc.add(GE.prism(sc.cam, O, a, GE.circle_outline(ro, seg, kw.pop("bands", 12)), h, mat, holes=[GE.circle_outline(ri, seg, feat)],
                    smooth="outer", **kw), _bb(O, a, ro, h), bias)


def vis(cam, nrm, m=-0.05):
    return GE._dot(nrm, cam.D) < m


def holes_on_cyl(cam, axis, x, R, r, n_, c="bg", a_off=0.0):
    """small holes on the visible side of a cylinder surface; axis 'x' (ring at x) or 'z' (ring at height x)."""
    o = ""
    for k in range(n_):
        a = 2 * math.pi * (k + a_off) / n_
        if axis == "x":
            nrm, C = (0, math.cos(a), math.sin(a)), (x, R * math.cos(a), R * math.sin(a))
        else:
            nrm, C = (math.cos(a), math.sin(a), 0), (R * math.cos(a), R * math.sin(a), x)
        if vis(cam, nrm, -0.25):
            o += hole3(cam, C, nrm, r, c, 12)
    return o


def ports_x(cam, x0, x1, R, n_, w, c="bg", skew=0.0):
    """rectangular ports through a cylinder wall along x (visible side only)."""
    o = ""
    for k in range(n_):
        a = 2 * math.pi * (k + .5) / n_
        if not vis(cam, (0, math.cos(a), math.sin(a)), -0.2):
            continue
        q = []
        for xx, da in ((x0, -w), (x1, -w + skew), (x1, w + skew), (x0, w)):
            q.append(cam.xy((xx, R * math.cos(a + da), R * math.sin(a + da))))
        o += path(P(q), c)
    return o


# =====================================================================================
# marine4.m4cam — segmented camshaft: per cylinder inlet / exhaust / (larger) fuel cam,
# bearing journals larger than the cams, segments bolted together by flanges
# =====================================================================================
@part("marine4.m4cam")
def _():
    def lobe(rb, d, rn, ph):
        c, s_ = math.cos(math.radians(ph)), math.sin(math.radians(ph))
        return banded(hull(arc(0, 0, rb, 0, 360, 12) + arc(d * c, d * s_, rn, ph - 80, ph + 80, 5)), 2)

    def fn(sc):
        x = 0

        def face(s_):
            return hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 9, "w3") + bolts(s_.cam, (-.1, 0, 0), (-1, 0, 0), 23, 8, 2.4)
        RAW(sc, face, ((-.2, -30, -30), (0, 30, 30)), -2)

        def C_(L, r, dark=0, seg=18):
            nonlocal x
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=seg, bands=10, dark=dark)
            x += L
        C_(8, 30, seg=36)
        C_(8, 13)
        C_(14, 25, seg=28)
        for cyl_ in range(3):
            ph = 90 + cyl_ * 120
            for k, (rb, d, rn, tw, dp) in enumerate(((15, 10, 10, 7, 0), (15, 10, 10, 7, 110), (17, 12, 12, 12, 200))):
                C_(4, 11)
                X(sc, x, tw, lobe(rb, d, rn, ph + dp), "w", smooth=True, cap_mat="w")
                x += tw
            C_(4, 11)
            if cyl_ == 1:
                def fl(s_, x0=x):
                    return bolts(s_.cam, (x0 - .1, 0, 0), (-1, 0, 0), 23, 8, 2.2)
                C_(5, 29, dark=1, seg=36)
                RAW(sc, fl, ((x - .2, -29, -29), (x, 29, 29)), -2)
                C_(5, 29, dark=1, seg=36)
            else:
                C_(14, 25, seg=28)
        C_(10, 12)
    return fit(fn, 20, 20, (14, 40, 306, 166), sh_ry=7, sh_k=.46)


# =====================================================================================
# liners
# =====================================================================================
@part("marine2.m2liner")
def _():
    # long 2-stroke liner lying on its side: thick collar (bore-cooling holes), lubricating quills
    # halfway, scavenge ports round the lower end
    R, Ri = 58, 47

    def fn(sc):
        RG(sc, (0, 0, 0), (1, 0, 0), 76, Ri, 46, "w", seg=56, bands=14)
        RG(sc, (46, 0, 0), (1, 0, 0), 66, Ri, 12, "w", seg=56, bands=14, dark=1)
        RG(sc, (58, 0, 0), (1, 0, 0), R, Ri, 342, "w", seg=56, bands=14)

        def marks(s_):
            cam = s_.cam
            o = holes_on_cyl(cam, "x", 26, 76, 2.6, 36)
            o += holes_on_cyl(cam, "x", 190, R, 2.2, 10, "w3", .25)
            o += ports_x(cam, 300, 344, R + .2, 22, math.radians(4.6), "bg", math.radians(3))
            return o
        RAW(sc, marks, ((0, -76, -76), (400, 76, 76)), -4)
    return fit(fn, 24, 20, (22, 22, 298, 176), sh_ry=7, sh_k=.46)


@part("marine4.m4liner")
def _():
    # medium-speed wet liner standing up: thick collar with cooling bores, O-ring grooves at the foot
    R, Ri = 44, 36

    def fn(sc):
        stack = [(0, 12, R + 2, 0), (12, 4, R, 2), (16, 114, R, 0), (130, 8, R + 6, 1), (138, 34, R + 10, 0)]
        for z0, h, r, dk in stack:
            RG(sc, (0, 0, z0), (0, 0, 1), r, Ri, h, "w", seg=40, bands=12, dark=dk, feat=8)

        def marks(s_):
            return holes_on_cyl(s_.cam, "z", 152, R + 10, 2.1, 30)
        RAW(sc, marks, ((-R - 10, -R - 10, 140), (R + 10, R + 10, 160)), -3)
    return fit(fn, -30, 26, (80, 12, 240, 178), sh_ry=8, sh_k=.6, sh_dy=-6)


# =====================================================================================
# pistons
# =====================================================================================
@part("marine2.m2piston")
def _():
    # crown with ring belt (lit, facing -x), short skirt, long piston rod ending in the crosshead foot flange
    R = 60

    def fn(sc):
        def face(s_):
            cam = s_.cam
            return (hole3(cam, (-.1, 0, 0), (-1, 0, 0), R * .86, "w2", 40) + hole3(cam, (-.15, 0, 0), (-1, 0, 0), R * .55, "w3", 36))
        RAW(sc, face, ((-.2, -R, -R), (0, R, R)), -2)
        belt = [(0, 8, R, 0), (8, 3.5, R - 2.4, 2), (11.5, 5, R, 0), (16.5, 3.5, R - 2.4, 2), (20, 5, R, 0), (25, 3.5, R - 2.4, 2),
                (28.5, 5, R, 0), (33.5, 3.5, R - 2.4, 2), (37, 13, R, 0)]
        for x0, L, r, dk in belt:
            CYL(sc, (x0, 0, 0), (1, 0, 0), r, L, "w", seg=48, bands=14, dark=dk)
        CYL(sc, (50, 0, 0), (1, 0, 0), R - 1, 24, "w", seg=48, bands=14, dark=1)
        CYL(sc, (74, 0, 0), (1, 0, 0), 30, 10, "w", seg=32)
        CYL(sc, (84, 0, 0), (1, 0, 0), 15, 250, "w", seg=24)
        CYL(sc, (334, 0, 0), (1, 0, 0), 22, 8, "w", seg=28)
        CYL(sc, (342, 0, 0), (1, 0, 0), 34, 12, "w", seg=32)
    return fit(fn, 22, 20, (22, 26, 298, 176), sh_ry=7, sh_k=.46)


@part("marine4.m4piston")
def _():
    # composite piston: forged-steel crown (3 ring grooves, shallow bowl), bolted iron skirt with
    # oil-ring groove and gudgeon-pin bore
    R = 40

    def fn(sc):
        st = [(0, 30, R - .4, 1), (30, 3, R - 2.4, 2), (33, 5, R - .4, 1), (38, 2.5, R - 3, 2), (40.5, 9.5, R, 0),
              (50, 3, R - 2.4, 2), (53, 4.5, R, 0), (57.5, 3, R - 2.4, 2), (60.5, 4.5, R, 0), (65, 3, R - 2.4, 2), (68, 7, R - .3, 0)]
        for z0, h, r, dk in st:
            CYL(sc, (0, 0, z0), (0, 0, 1), r, h, "w", seg=48, bands=16, dark=dk)

        def marks(s_):
            cam = s_.cam
            o = hole3(cam, (0, 0, 75.05), (0, 0, 1), R * .8, "w2", 36) + hole3(cam, (0, 0, 75.1), (0, 0, 1), R * .55, "w3", 32)
            o += hole3(cam, (0, 0, 75.15), (0, 0, 1), R * .2, "w2", 20)
            c = (0, -R + 1.2, 15)
            o += hole3(cam, c, (0, -1, 0), 12, "w3") + hole3(cam, c, (0, -1, 0), 9.5, "bg")
            for a in (-120, -100, -80, -60):
                t = math.radians(a)
                o += hole3(cam, ((R - 2.3) * math.cos(t), (R - 2.3) * math.sin(t), 31.5), (math.cos(t), math.sin(t), 0), 1.0)
            return o
        RAW(sc, marks, ((-R, -R, 75.2), (R, R, 75.3)), -3)
    return fit(fn, -30, 28, (74, 14, 246, 176), sh_ry=8, sh_k=.62, sh_dy=-6)


def Y(sc, y0, L, xz, mat="w", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded from y0 toward the viewer (-y) by L."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, -1, 0), loop, L, mat, **kw)), ((min(xs), y0 - L, min(zs)), (max(xs), y0, max(zs))), bias)


def rr(x0, z0, x1, z1, r, seg=3):
    return [(u, v) for u, v, f in OM.rrect(x0, z0, x1, z1, r, seg)]


# =====================================================================================
# marine2.m2xhead — crosshead: big pin, piston-rod foot on top, guide shoes with white-metal faces
# =====================================================================================
@part("marine2.m2xhead")
def _():
    def fn(sc):
        for s in (-1, 1):
            x0 = 80 if s > 0 else -112
            BOX(sc, x0, -44, -42, 32, 88, 84, "w", ch=4)                       # shoe body
            BOX(sc, x0 + 2, -48, -38, 28, 4, 76, "alu")                        # white-metal face, front
            BOX(sc, x0 + 2, 44, -38, 28, 4, 76, "alu")
        CYL(sc, (-80, 0, 0), (1, 0, 0), 30, 160, "w", seg=40, bands=12)        # crosshead pin (ground)
        BOX(sc, -34, -30, 30, 68, 60, 18, "w", ch=6)                           # piston-rod foot
        CYL(sc, (0, 0, 48), (0, 0, 1), 20, 8, "w", seg=28)
        CYL(sc, (0, 0, 56), (0, 0, 1), 13, 70, "w", seg=24)                   # piston rod

        def marks(s_):
            cam = s_.cam
            o = ""
            for x in (-24, 24):
                for y in (-20, 20):
                    o += hole3(cam, (x, y, 48.1), (0, 0, 1), 3.4, "m3")
            for s in (-1, 1):
                x0 = 96 if s > 0 else -96
                o += hole3(cam, (x0, -48.2, 26), (0, -1, 0), 2.2) + path(P([cam.xy((x0 - 10, -48.2, z)) for z in (-30, 30)] +
                                                                           [cam.xy((x0 + 10, -48.2, z)) for z in (30, -30)]), "gr")
            return o
        RAW(sc, marks, ((-112, -48.4, -42), (112, -48.2, 48.2)), -4)
        return ""
    return fit(fn, -30, 22, (30, 14, 290, 178), sh_ry=8, sh_k=.5)


# =====================================================================================
# marine2.m2exv — hydraulically operated exhaust valve: spindle disc under the bottom piece (seat),
# cast housing with the side gas outlet, air-spring / hydraulic actuator on top
# =====================================================================================
@part("marine2.m2exv")
def _():
    def fn(sc):
        CYL(sc, (0, 0, 0), (0, 0, 1), 36, 7, "w", seg=40, r1=30)               # valve disc (spindle head)
        CYL(sc, (0, 0, 7), (0, 0, 1), 8, 5, "w", seg=20)
        RG(sc, (0, 0, 12), (0, 0, 1), 44, 30, 16, "w", seg=40, dark=1)          # bottom piece / seat
        CYL(sc, (0, 0, 28), (0, 0, 1), 58, 10, "w", seg=48)                    # housing flange
        CYL(sc, (0, 0, 38), (0, 0, 1), 46, 78, "w", seg=40)                    # housing
        CYL(sc, (0, 0, 116), (0, 0, 1), 52, 8, "w", seg=40)
        CYL(sc, (0, 0, 124), (0, 0, 1), 34, 34, "dk", seg=32)                  # air spring
        CYL(sc, (0, 0, 158), (0, 0, 1), 24, 38, "m", seg=28)                   # hydraulic actuator
        CYL(sc, (0, 0, 196), (0, 0, 1), 30, 8, "m", seg=28)
        CYL(sc, (0, -40, 82), (0, -1, 0), 30, 44, "w", -2, seg=36)             # gas outlet
        CYL(sc, (0, -84, 82), (0, -1, 0), 40, 9, "w", -3, seg=40)

        def m1(s_):
            cam = s_.cam
            return (hole3(cam, (0, -93.1, 82), (0, -1, 0), 26, "w3", 32) + hole3(cam, (0, -93.2, 82), (0, -1, 0), 22, "bg", 32) +
                    bolts(cam, (0, -93.2, 82), (0, -1, 0), 33, 10, 2.2))
        RAW(sc, m1, ((-40, -93.4, 42), (40, -93.2, 122)), -5)
        RAW(sc, lambda s_: bolts(s_.cam, (0, 0, 38.1), (0, 0, 1), 52, 12, 2.4), ((-58, -58, 38.05), (58, 58, 38.1)), -1)
    return fit(fn, -30, 22, (60, 10, 260, 180), sh_ry=8, sh_k=.6, sh_dy=-4)


# =====================================================================================
# marine4.m4head — cylinder head: 2 inlet + 2 exhaust valves round a central injector,
# heavy hydraulically tightened studs, exhaust / inlet port flanges on the sides
# =====================================================================================
@part("marine4.m4head")
def _():
    a = 62

    def fn(sc):
        BOX(sc, -a, -a, 0, 2 * a, 2 * a, 84, "w", ch=12)
        Y(sc, -a, 8, rr(-36, 20, 36, 62, 10), "w", -2)                         # exhaust port flange (front)
        X(sc, -a - 8, 8, [(u, v) for u, v in rr(-34, 22, 34, 60, 10)], "w", -2)  # inlet flange (left)
        for x, y in ((-24, -24), (24, -24), (-24, 24), (24, 24)):
            CYL(sc, (x, y, 84), (0, 0, 1), 11, 16, "w", seg=24, dark=1)        # valve springs
            CYL(sc, (x, y, 100), (0, 0, 1), 8, 4, "w", seg=20)
        CYL(sc, (0, 0, 84), (0, 0, 1), 9, 30, "w", seg=24)                     # injector
        CYL(sc, (0, 0, 114), (0, 0, 1), 13, 6, "dk", seg=24)
        for x, y in ((-52, -52), (52, -52), (-52, 52), (52, 52)):
            CYL(sc, (x, y, 84), (0, 0, 1), 7, 22, "w", seg=20)                 # studs + nuts
            CYL(sc, (x, y, 84), (0, 0, 1), 11, 10, "dk", seg=6)

        def marks(s_):
            cam = s_.cam
            o = hole3(cam, (0, -a - 8.1, 41), (0, -1, 0), 15, "bg", 24) + hole3(cam, (-a - 8.1, 0, 41), (-1, 0, 0), 14, "bg", 24)
            for c, A in (((0, -a - 8.1, 41), (0, -1, 0)), ((-a - 8.1, 0, 41), (-1, 0, 0))):
                for d in (-27, 27):
                    o += hole3(cam, tuple(c[i] + d * (1 if A[1] else 0) * (i == 0) + d * (1 if A[0] else 0) * (i == 1) for i in range(3)), A, 2.6)
            for x, y in ((0, -44), (-44, 0), (40, 40)):
                o += hole3(cam, (x, y, 84.1), (0, 0, 1), 4, "w3")
            return o
        RAW(sc, marks, ((-a - 8.2, -a - 8.2, 0), (a, a, 84.2)), -6)
    return fit(fn, 30, 28, (60, 10, 260, 180), sh_ry=8, sh_k=.6, sh_dy=-4)


# =====================================================================================
# marine4.m4conrod — marine-type connecting rod lying flat: small eye, shank, flange bolted to the
# split big-end bearing housing (bearing shells in the bore)
# =====================================================================================
@part("marine4.m4conrod")
def _():
    def fn(sc):
        sc.add(GE.prism(sc.cam, (0, 0, 8), (0, 0, 1), GE.circle_outline(34, 28, 10), 44, "w", holes=[GE.circle_outline(20, 28, 6)],
                        smooth="outer"), ((-34, -34, 8), (34, 34, 52)))                                          # small eye
        Z(sc, 12, 36, [(32, -15), (238, -22), (238, 22), (32, 15)], "w", dark=1)                                     # shank
        Z(sc, 4, 52, [(238, -62), (258, -62), (258, 62), (238, 62)], "w")                                         # flange
        bh = banded(hull(arc(330, 0, 72, -90, 90, 14) + [(258, -72), (258, 72)]), 2)
        loop = [(-p[1], p[0], p[2]) for p in bh]
        sc.add(GE.prism(sc.cam, (0, 0, 0), (0, 0, 1), loop, 60, "w", holes=[GE.circle_outline(46, 40, 8, 0, 330)], smooth="outer"),
               ((258, -72, 0), (402, 72, 60)))                                                                    # big-end housing

        def marks(s_):
            cam = s_.cam
            o = hole3(cam, (0, 0, 52.05), (0, 0, 1), 20, "alu", 28) + hole3(cam, (0, 0, 52.1), (0, 0, 1), 17, "bg", 28)
            o += hole3(cam, (330, 0, 60.05), (0, 0, 1), 46, "alu", 40) + hole3(cam, (330, 0, 60.1), (0, 0, 1), 42, "bg", 40)
            o += path(P([cam.xy((330, -72, 60.1)), cam.xy((330, -46, 60.1))], False) + P([cam.xy((330, 46, 60.1)), cam.xy((330, 72, 60.1))], False), "el")
            o += path(P([cam.xy((258, -72, 60.1)), cam.xy((258, 72, 60.1))], False), "el")
            for y in (-46, 46):
                for z in (16, 44):
                    o += hole3(cam, (237.9, y, z), (-1, 0, 0), 6.5, "m3", 6)
            return o
        RAW(sc, marks, ((0, -72, 60.1), (330, 72, 60.2)), -6)
    return fit(fn, 24, 30, (22, 22, 298, 176), sh_ry=7, sh_k=.46)


# =====================================================================================
# marine4.m4bearing — main-bearing half shell lying as a cradle: steel back, lining (light),
# oil groove + oil hole, locating lug; layers visible on the near end face
# =====================================================================================
@part("marine4.m4bearing")
def _():
    Ro, Ri, Lx = 66, 56, 120

    def fn(sc):
        cam = sc.cam
        out_ = [(Ro * math.cos(math.radians(a)), Ro * math.sin(math.radians(a)), 1 + k // 3) for k, a in enumerate(range(180, 361, 10))]
        in_ = [(Ri * math.cos(math.radians(a)), Ri * math.sin(math.radians(a)), 100 + k // 3) for k, a in enumerate(range(360, 179, -10))]
        o = compact(GE.prism(cam, (0, 0, 0), (1, 0, 0), out_ + in_, Lx, "w", smooth=True, fid_mat=lambda f: "gw" if f >= 100 else "w"))
        # lining layer on the lit end face, groove + hole on the inner face
        band = [cam.xy((-.1, r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))) for r, rng in ((Ri + 3.2, range(180, 361, 10)), (Ri, range(360, 179, -10))) for a in rng]
        o += path(P(band), "gws2")
        av = [a for a in range(186, 355, 6) if vis(cam, (0, -math.cos(math.radians(a)), -math.sin(math.radians(a))), -0.08)]
        g = [cam.xy((Lx / 2 + d, (Ri - .2) * math.cos(math.radians(a)), (Ri - .2) * math.sin(math.radians(a)))) for d, rng in ((-1.6, av), (1.6, av[::-1])) for a in rng]
        o += path(P(g), "bg")
        o += hole3(cam, (Lx / 2, 0, -Ri + 0.3), (0, 0, 1), 5, "bg")
        o += compact(GE.prism(cam, (12, -Ro + 1, -1), (0, 0, 1), [(-4, -6, 0), (4, -6, 1), (4, 6, 2), (-4, 6, 3)], 6, "w"))
        return o
    return fit(fn, 26, 32, (40, 20, 280, 176), sh_ry=8, sh_k=.5)


def rrect_y(cam, y, x0, z0, x1, z1, r, c):
    """rounded rectangle drawn on a face of constant y."""
    return path(P([cam.xy((u, y, v)) for u, v in rr(x0, z0, x1, z1, r, 3)]), c)


# =====================================================================================
# marine4.m4block — inline-6 medium-speed cylinder block (one casting): liner bores and stud holes
# on the deck, camshaft housing along the side, crankcase openings, main-bearing bore at the end
# =====================================================================================
@part("marine4.m4block")
def _():
    L, pitch = 420, 66

    def fn(sc):
        BOX(sc, -4, -72, 0, L + 8, 144, 10, "w")
        BOX(sc, 0, -64, 10, L, 128, 140, "w")
        BOX(sc, 0, -70, 150, L, 140, 16, "w")
        X(sc, 0, L, [(-84, 98), (-64, 98), (-64, 140), (-84, 140)], "w", -1)

        def deck(s_):
            cam = s_.cam
            o = ""
            for i in range(6):
                xc = 45 + i * pitch
                o += hole3(cam, (xc, 0, 166.1), (0, 0, 1), 28, "w3", 32) + hole3(cam, (xc, 0, 166.15), (0, 0, 1), 24, "bg", 32)
                for dx, dy in ((-30, -40), (30, -40), (-30, 40), (30, 40)):
                    o += hole3(cam, (xc + dx, dy, 166.1), (0, 0, 1), 4.2, "bg", 12)
                o += hole3(cam, (xc, -54, 166.1), (0, 0, 1), 3, "w3", 10)
            return o
        RAW(sc, deck, ((0, -70, 166.05), (L, 70, 166.1)), -2)

        def side(s_):
            cam = s_.cam
            o = ""
            for i in range(6):
                xc = 45 + i * pitch
                o += rrect_y(cam, -64.1, xc - 22, 26, xc + 22, 86, 10, "w3") + rrect_y(cam, -64.2, xc - 17, 31, xc + 17, 81, 7, "bg")
            return o
        RAW(sc, side, ((0, -64.3, 20), (L, -64.1, 90)), -2)

        def end(s_):
            cam = s_.cam
            o = hole3(cam, (-.1, 0, 52), (-1, 0, 0), 32, "w3", 32) + hole3(cam, (-.15, 0, 52), (-1, 0, 0), 27, "bg", 32)
            o += hole3(cam, (-.1, -74, 119), (-1, 0, 0), 12, "w3", 20) + hole3(cam, (-.15, -74, 119), (-1, 0, 0), 9, "bg", 20)
            for y, z in ((-40, 110), (40, 110), (0, 128), (-44, 30), (44, 30)):
                o += hole3(cam, (-.1, y, z), (-1, 0, 0), 4, "bg", 12)
            return o
        RAW(sc, end, ((-.2, -84, 0), (0, 70, 166)), -3)
    return fit(fn, 30, 26, (18, 14, 302, 180), sh_ry=8, sh_k=.5)


# =====================================================================================
# assembled engines on the test bed
# =====================================================================================
@part("marine2.m2assy")
def _():
    # 6-cyl crosshead engine: bedplate, frame box with doors, cylinder frame + scavenge receiver,
    # covers with exhaust valves, exhaust receiver, turbocharger at the end; person for scale
    def fn(sc):
        BOX(sc, -110, -150, -12, 720, 260, 12, "dk", dark=1)                      # test-bed plate
        BOX(sc, 0, -80, 0, 560, 160, 50, "pt", dark=1)                           # bedplate
        BOX(sc, 10, -70, 50, 540, 140, 150, "pt")                                # frame box
        BOX(sc, 10, -62, 200, 540, 124, 70, "pt", dark=1)                        # cylinder frame
        CYL(sc, (10, -88, 228), (1, 0, 0), 26, 540, "pt", -1, seg=28)             # scavenge-air receiver
        CYL(sc, (560, 0, 70), (1, 0, 0), 64, 16, "m", seg=40)                     # turning wheel
        for i in range(6):
            xc = 60 + i * 88
            Y(sc, -70, 3, rr(xc - 24, 70, xc + 24, 170, 8, 2), "pt", -2)          # doors
            CYL(sc, (xc, 0, 270), (0, 0, 1), 36, 18, "w", seg=24, bands=8)       # cylinder cover
            CYL(sc, (xc, 0, 288), (0, 0, 1), 15, 36, "pt", seg=16, bands=6)      # exhaust valve
            CYL(sc, (xc, 0, 324), (0, 0, 1), 11, 10, "dk", seg=14, bands=6)
        CYL(sc, (10, 64, 336), (1, 0, 0), 30, 540, "pt", seg=32)                  # exhaust receiver
        BOX(sc, -64, -36, 236, 74, 72, 54, "pt", dark=1)                          # TC bracket
        CYL(sc, (-30, 36, 330), (0, -1, 0), 32, 26, "m", seg=32)                  # turbine casing
        CYL(sc, (-30, 10, 330), (0, -1, 0), 40, 30, "alu", seg=36)                # compressor casing
        CYL(sc, (-30, -20, 330), (0, -1, 0), 34, 40, "dk", seg=32)                # air filter / silencer
        return person_at(sc.cam, (590, -130, 0), 48)
    return fit(fn, 28, 24, (14, 12, 306, 182), sh=False)


@part("marine4.m4assy")
def _():
    # inline-6 medium-speed engine on the test bed: oil sump, block with doors, heads + rocker covers,
    # insulated exhaust manifold, turbocharger at the free end, flywheel and water brake
    def fn(sc):
        BOX(sc, -110, -110, -12, 680, 210, 12, "dk", dark=1)
        BOX(sc, 0, -60, 0, 420, 120, 40, "pt", dark=1)
        BOX(sc, 10, -56, 40, 400, 112, 130, "pt")
        for i in range(6):
            xc = 50 + i * 64
            Y(sc, -56, 3, rr(xc - 20, 60, xc + 20, 110, 8), "pt", -2)
            BOX(sc, xc - 28, -40, 170, 56, 82, 38, "pt", ch=6)
            BOX(sc, xc - 22, -30, 208, 44, 60, 16, "dk", ch=4)
        CYL(sc, (14, -60, 190), (1, 0, 0), 20, 392, "alu", -1, seg=24)           # insulated exhaust manifold
        CYL(sc, (14, 58, 186), (1, 0, 0), 18, 392, "pt", seg=24)                 # charge-air receiver
        BOX(sc, -70, -40, 120, 80, 80, 60, "pt", dark=1)                          # TC bracket
        CYL(sc, (-30, 30, 222), (0, -1, 0), 30, 24, "m", seg=32)
        CYL(sc, (-30, 6, 222), (0, -1, 0), 38, 28, "alu", seg=36)
        CYL(sc, (-30, -22, 222), (0, -1, 0), 32, 36, "dk", seg=32)
        CYL(sc, (420, 0, 90), (1, 0, 0), 72, 18, "m", seg=48)                     # flywheel
        BOX(sc, 438, -46, 0, 70, 92, 110, "m", ch=6)                             # water brake (dyno)
        return person_at(sc.cam, (470, -110, 0), 100)
    return fit(fn, 28, 24, (14, 12, 306, 182), sh=False)


def clip_poly(subj, clip):
    """Sutherland-Hodgman clip of a screen polygon by a convex screen polygon."""
    def side(a, b, p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    sg = 1 if sum(side(clip[i], clip[(i + 1) % len(clip)], clip[(i + 2) % len(clip)]) for i in range(len(clip))) > 0 else -1
    out = subj
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(a, b, p) * sg, side(a, b, q) * sg
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        if not out:
            break
    return out


# =====================================================================================
# propulsion.prgear — reduction gear: large helical wheel lying flat (recessed web, hub) with the
# opposite-hand pinion on its shaft meshing behind
# =====================================================================================
@part("propulsion.prgear")
def _():
    zw, rpw, h, hx, rb = 44, 100, 30, 14, 82
    zp, rpp = 14, rpw * 14 / 44

    def fn(sc):
        cam = sc.cam
        a = math.radians(32)
        C = ((rpw + rpp) * math.cos(a), (rpw + rpp) * math.sin(a), 0)
        o = compact(GE.gear3(cam, C, (0, 0, 1), zp, rpp, h, "w", helix=-hx, phase=0.5, slices=1))
        o += compact(GE.prism(cam, (C[0], C[1], h), (0, 0, 1), GE.circle_outline(17, 24, 8), 70, "w", smooth=True))
        o += compact(GE.gear3(cam, (0, 0, 0), (0, 0, 1), zw, rpw, h, "w", helix=hx, bore=rb, slices=1))
        zt = h - 9
        web = clip_poly(circ3(cam, (0, 0, zt), (0, 0, 1), rb, 48), circ3(cam, (0, 0, h), (0, 0, 1), rb, 48))
        o += path(P(web), "w")
        for k in range(6):
            t = 2 * math.pi * (k + .5) / 6
            o += hole3(cam, (58 * math.cos(t), 58 * math.sin(t), zt + .05), (0, 0, 1), 12, "w3", 20)
            o += hole3(cam, (58 * math.cos(t), 58 * math.sin(t), zt + .1), (0, 0, 1), 10, "bg", 20)
        o += GE.prism(cam, (0, 0, zt), (0, 0, 1), GE.circle_outline(34, 32, 10), h + 8 - zt, "w", holes=[GE.circle_outline(20, 28, 6)],
                      smooth="outer")
        o += path(P(circ3(cam, (0, 0, h + 8.05), (0, 0, 1), 34 - 3, 32)), "gr")
        return o
    return fit(fn, -30, 30, (34, 10, 286, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


# =====================================================================================
# propulsion.prgbox — reduction gearbox: horizontally split welded casing (split flange + bolts),
# input pinion shaft and output coupling flange in the split plane, bearing bosses, top cover, feet
# =====================================================================================
@part("propulsion.prgbox")
def _():
    L, zs = 230, 120

    def fn(sc):
        BOX(sc, -10, -108, 0, L + 20, 216, 14, "pt", dark=1)                     # feet / foundation flange
        BOX(sc, 0, -90, 14, L, 180, zs - 14, "pt")                               # lower half
        BOX(sc, -6, -100, zs, L + 12, 200, 12, "pt", dark=1)                    # split flange
        X(sc, 0, L, banded(hull([(-90, zs + 12), (90, zs + 12), (90, zs + 60), (60, zs + 108), (-40, zs + 120), (-90, zs + 80)]), 1), "pt")
        BOX(sc, 70, -30, zs + 114, 90, 54, 8, "pt", -1, dark=1)                 # inspection cover
        # output (wheel) shaft: boss + coupling flange toward -x; input pinion shaft out of +x
        CYL(sc, (0, 30, zs + 6), (-1, 0, 0), 56, 14, "pt", -1, seg=40)
        CYL(sc, (-14, 30, zs + 6), (-1, 0, 0), 20, 16, "w", -2, seg=24)
        CYL(sc, (-30, 30, zs + 6), (-1, 0, 0), 50, 14, "w", -3, seg=40)
        CYL(sc, (0, -56, zs + 6), (-1, 0, 0), 30, 10, "pt", -1, seg=28)
        CYL(sc, (L, -56, zs + 6), (1, 0, 0), 30, 10, "pt", seg=28)
        CYL(sc, (L + 10, -56, zs + 6), (1, 0, 0), 15, 60, "w", seg=24)
        CYL(sc, (60, -90, 50), (0, -1, 0), 16, 18, "m", -1, seg=24)             # oil pump

        def marks(s_):
            cam = s_.cam
            o = bolts(cam, (-44.1, 30, zs + 6), (-1, 0, 0), 38, 10, 3.2) + hole3(cam, (-44.1, 30, zs + 6), (-1, 0, 0), 12, "w3")
            o += bolts(cam, (-10.1, -56, zs + 6), (-1, 0, 0), 22, 6, 2.2)
            for k in range(11):
                x = 6 + k * 22
                o += hole3(cam, (x, -96, zs + 12.1), (0, 0, 1), 2.6, "m3", 10)
            for k in range(5):
                o += hole3(cam, (8 + k * 54, -100, 14.1), (0, 0, 1), 3.4, "m3", 10)
            return o
        RAW(sc, marks, ((-44.3, -110, 0), (L, -96, zs + 12.2)), -6)
    return fit(fn, 30, 24, (30, 12, 290, 180), sh_ry=8, sh_k=.5)


# =====================================================================================
# propulsion.prshaft — propeller shaft: forward coupling flange, bearing journals with sleeves,
# aft taper for the keyless propeller fit and the nut thread
# =====================================================================================
@part("propulsion.prshaft")
def _():
    def fn(sc):
        def face(s_):
            return hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 9, "bg") + bolts(s_.cam, (-.1, 0, 0), (-1, 0, 0), 31, 8, 3.2)
        RAW(sc, face, ((-.2, -42, -42), (0, 42, 42)), -2)
        x = 0
        for L, r, m, dk in ((12, 42, "w", 0), (12, 25, "w", 0), (90, 20, "w", 0), (40, 22, "gw", 0), (170, 20, "w", 0), (56, 22, "gw", 0),
                            (8, 20, "w", 0)):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, m, seg=28 if r > 30 else 22, bands=10, dark=dk)
            x += L
        CYL(sc, (x, 0, 0), (1, 0, 0), 20, 56, "w", seg=22, bands=10, r1=15.5)
        x += 56
        CYL(sc, (x, 0, 0), (1, 0, 0), 12.5, 24, "w", seg=20, bands=8, dark=2)
    return fit(fn, 16, 18, (14, 50, 306, 156), sh_ry=6, sh_k=.46)


def xcradle(cam, x0, L, Ro, Ri, mat="w", lin=None, tl=0.0):
    """lower half shell along x (cut model): outer radius Ro, bore Ri; lin = lining class on the bore."""
    out_ = [(Ro * math.cos(math.radians(a)), Ro * math.sin(math.radians(a)), 1 + k // 3) for k, a in enumerate(range(180, 361, 10))]
    in_ = [(Ri * math.cos(math.radians(a)), Ri * math.sin(math.radians(a)), 100 + k // 3) for k, a in enumerate(range(360, 179, -10))]
    return compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), out_ + in_, L, mat, smooth=True,
                            fid_mat=(lambda f: lin if f >= 100 else mat) if lin else None))


# =====================================================================================
# propulsion.prstern — stern-tube bearings and seals, cut model: tube and white-metal bushes cut
# open along the top, shaft resting in them, seal ring stacks at both ends, propeller taper aft
# =====================================================================================
@part("propulsion.prstern")
def _():
    def fn(sc):
        cam = sc.cam
        o = compact(GE.prism(cam, (310, 0, 0), (1, 0, 0), GE.circle_outline(20, 22, 8), 50, "w", smooth=True))
        for x0, L, r, m in ((290, 8, 46, "w"), (298, 6, 42, "dk"), (304, 8, 46, "w")):
            o += compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), GE.circle_outline(r, 36, 10), L, m, smooth=True))
        o += xcradle(cam, 0, 290, 58, 46, "w", dark=0) if False else xcradle(cam, 0, 290, 58, 46, "w")
        o += xcradle(cam, 16, 130, 46, 25, "w", "alu")
        o += xcradle(cam, 200, 70, 46, 25, "w", "alu")
        o += compact(GE.prism(cam, (-30, 0, 0), (1, 0, 0), GE.circle_outline(24, 28, 10), 320, "w", smooth=True))
        for x0, L, r, m in ((-12, 12, 60, "w"), (-20, 8, 52, "w"), (-24, 4, 48, "dk"), (-32, 8, 52, "w"), (-36, 4, 48, "dk"), (-44, 8, 52, "w")):
            o += compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), GE.circle_outline(r, 36, 10), L, m, smooth=True))
        o += bolts(cam, (-44.1, 0, 0), (-1, 0, 0), 44, 10, 2.4, "m3")
        o += compact(GE.prism(cam, (-44, 0, 0), (-1, 0, 0), GE.circle_outline(25, 28, 10), 26, "w", smooth=True))
        o += compact(GE.prism(cam, (-70, 0, 0), (-1, 0, 0), GE.circle_outline(25, 28, 10), 50, "w", smooth=True, scale=lambda t: 1 - .22 * t))
        return o
    return fit(fn, 24, 30, (18, 26, 302, 174), sh_ry=7, sh_k=.46)


# =====================================================================================
# propulsion.prcpp — controllable-pitch propeller: large hub (blade carriers / palms visible),
# 4 bolted blades, aft hub cone, hollow shaft flange forward; person for scale
# =====================================================================================
@part("propulsion.prcpp")
def _():
    R = 88.0
    rh = R * .3
    hl = 1.25 * 2 * rh
    cam = GE.Cam(146, 96, -44, 18, 1.0)
    s = shadow(150, 188, 100, 9)
    s += GE.cyl(cam, (0, hl / 2, 0), (0, 1, 0), rh * .5, R * .7, "w", seg=24)
    s += GE.cyl(cam, (0, hl / 2 - 2, 0), (0, 1, 0), rh * .78, 8, "w", seg=32)
    hub = compact(GE.prism(cam, (0, -hl / 2, 0), (0, 1, 0), GE.circle_outline(rh, 40, 12), hl, "w", smooth=True, slices=4,
                           scale=lambda t: .9 + .1 * math.sin(math.pi * t)))
    th0 = 90.0
    for b in range(4):
        t = math.radians(th0 + b * 90 + 8)
        nrm = (math.cos(t), 0, math.sin(t))
        if vis(cam, nrm, -0.1):
            C = (rh * .99 * nrm[0], -2, rh * .99 * nrm[2])
            hub += path(P(circ3(cam, C, nrm, rh * .52, 24)), "cu") + path(P(circ3(cam, C, nrm, rh * .52, 24)), "el x")
    hub += compact(GE.prism(cam, (0, -hl / 2, 0), (0, -1, 0), GE.circle_outline(rh * .9, 36, 10), rh * 1.0, "w", smooth=True,
                            scale=lambda t: 1 - .62 * t))
    hc = cam.P((0, 0, 0))[2]
    items = OM.prop_blades(cam, R, rh, Z=4, skew=18, root=rh * .95, N=12, M=6, th0=th0, kc=1.25)
    items.sort(key=lambda it: -it[0])
    for dep, svg in items:
        if dep > hc:
            s += svg
    s += hub
    for dep, svg in items:
        if dep <= hc:
            s += svg
    s += person_at(cam, (R * 1.3, R * .9, -R - 2), .34 * R)
    return s


# =====================================================================================
# propulsion.prinstall — shaft line installed in the ship: propeller, stern boss with the stern
# tube, propeller shaft, intermediate shafts on their bearings over the tank top, engine coupling
# =====================================================================================
@part("propulsion.prinstall")
def _():
    R = 62

    def fn(sc):
        BOX(sc, -80, 150, -64, 160, 430, 8, "dk", dark=1)                      # tank top (double bottom)
        Z(sc, -64, 92, [(-30, 30), (30, 30), (30, 150), (-30, 150)], "pt", dark=1)   # stern boss / skeg end
        CYL(sc, (0, 150, 0), (0, 1, 0), 22, 10, "w", seg=28)                    # stern-tube flange (fwd seal)
        CYL(sc, (0, 160, 0), (0, 1, 0), 10, 100, "w", seg=20)                   # propeller shaft
        for y0 in (260, 410):
            CYL(sc, (0, y0, 0), (0, 1, 0), 20, 8, "w", seg=28)                  # coupling flanges
            CYL(sc, (0, y0 + 8, 0), (0, 1, 0), 20, 8, "w", seg=28)
        CYL(sc, (0, 276, 0), (0, 1, 0), 10, 134, "w", seg=20)                   # intermediate shaft
        for y0 in (210, 330):
            BOX(sc, -20, y0 - 12, -56, 40, 24, 44, "m", ch=4)                   # bearing pedestals
            CYL(sc, (0, y0 - 12, 0), (0, 1, 0), 14, 24, "m", 1, seg=24)
        BOX(sc, -70, 426, -56, 140, 150, 170, "pt", dark=1)                     # main engine (aft end)
        CYL(sc, (0, 426, 0), (0, -1, 0), 34, 8, "m", -1, seg=36)               # engine coupling / turning wheel

        def prop(s_):
            cam = s_.cam
            o = compact(GE.prism(cam, (0, -16, 0), (0, 1, 0), GE.circle_outline(12, 24, 8), 44, "cu", smooth=True, scale=lambda t: .85 + .2 * t))
            hc = cam.P((0, 0, 0))[2]
            items = sorted(OM.prop_blades(cam, R, 12, Z=4, N=8, M=4, root=11.4), key=lambda it: -it[0])
            return "".join(v for d, v in items if d > hc) + o + "".join(v for d, v in items if d <= hc)
        RAW(sc, prop, ((-R, -20, -R), (R, 28, R)), -2)
        return person_at(sc.cam, (60, 370, -56), 26)
    return fit(fn, -58, 20, (12, 14, 308, 182), sh_ry=8, sh_k=.5)


# =====================================================================================
# radial wheels (axis x, inducer / exducer face toward -x = lit side)
# =====================================================================================
def wheel(cam, nb, mat, hub, shroud, theta, t0s=(0.0,), R2=70, back=6, N=5, M=2, LV=2, thk=2.2):
    """hub(t)/shroud(t) -> (x, r) meridional contours, theta(t, s) -> wrap angle (deg) of the blade
    surface; t0s: start of the blade per family (main 0, splitter 0.4 …), families interleaved."""
    items = []
    o = compact(GE.prism(cam, (hub(1)[0], 0, 0), (1, 0, 0), GE.circle_outline(R2, 56, 14), back, mat, smooth=True))
    hb = compact(GE.prism(cam, (0, 0, 0), (1, 0, 0), GE.circle_outline(hub(0)[1], 32, 10), hub(1)[0], mat, smooth=True, slices=5,
                          scale=lambda t: hub(t)[1] / hub(0)[1]))
    nf = len(t0s)
    dth = math.radians(thk)
    for j in range(nb * nf):
        fam = j % nf
        a0 = 360.0 * j / (nb * nf)
        t0 = t0s[fam]
        G = []
        for i in range(N + 1):
            t = t0 + (1 - t0) * i / N
            row = []
            for k in range(M + 1):
                s_ = k / M
                (xh, rh), (xs, rs) = hub(t), shroud(t)
                x, r = xh + (xs - xh) * s_, rh + (rs - rh) * s_
                th = math.radians(a0 + theta(t, s_))
                row.append((x, r * math.cos(th), r * math.sin(th)))
            G.append(row)
        Gb = [[(q[0], q[1] * math.cos(dth) - q[2] * math.sin(dth), q[1] * math.sin(dth) + q[2] * math.cos(dth)) for q in row] for row in G]
        bk = [cam.xy(Gb[i][0]) for i in range(N + 1)] + [cam.xy(Gb[N][k]) for k in range(M + 1)] + [cam.xy(Gb[i][M]) for i in range(N, -1, -1)]
        svg, S = OM.shaded_grid(cam, G, mat, LV=LV)
        svg = path(P(bk), mat + "s4") + svg
        rim = [S[i][0] for i in range(N + 1)] + [S[N][k] for k in range(M + 1)] + [S[i][M] for i in range(N, -1, -1)] + [S[0][k] for k in range(M, -1, -1)]
        svg += path(P(rim), "el x")
        items.append((cam.P(G[N // 2][M])[2], svg))
    hc = cam.P((hub(.5)[0], 0, 0))[2]
    items.sort(key=lambda it: -it[0])
    return o + "".join(v for d, v in items if d > hc) + hb + "".join(v for d, v in items if d <= hc)


@part("marineaux.mxcomp")
def _():
    # compressor impeller: inducer with swept leading edges, main + splitter blades, backswept exit
    def fn(sc):
        cam = sc.cam
        o = compact(GE.prism(cam, (46, 0, 0), (1, 0, 0), GE.circle_outline(22, 24, 8), 30, "w", smooth=True))
        o += wheel(cam, 8, "w", lambda t: (40 * t, 13 + 57 * t ** 2.2), lambda t: (33 * t ** 1.3, 44 + 26 * t ** 2.4),
                   lambda t, s: 46 * (1 - t) ** 2 * (.25 + .75 * s) - 28 * t ** 3, t0s=(0.0, 0.42))
        o += compact(GE.prism(cam, (0, 0, 0), (-1, 0, 0), GE.circle_outline(12, 6, 6), 10, "m", smooth=False))
        o += hole3(cam, (-10.1, 0, 0), (-1, 0, 0), 5, "m3", 12)
        return o
    return fit(fn, 26, 22, (50, 10, 270, 178), sh_ry=8, sh_k=.55, sh_dy=-4)


@part("marineaux.mxturb")
def _():
    # radial turbine wheel (cast, Ni alloy) with radial inducer blades and curved exducer, welded
    # to the rotor shaft (bearing journals, thrust collar, compressor-end seat)
    def fn(sc):
        cam = sc.cam
        o = ""
        x = 46
        segs = ((16, 18, 0), (26, 16, 0), (14, 13, 1), (60, 12, 0), (8, 20, 0), (26, 13, 0), (30, 9, 0), (10, 7, 2))
        tot = sum(L for L, _, _ in segs)
        xe = x + tot
        for L, r, dk in reversed(segs):
            xe -= L
            o += compact(GE.prism(cam, (xe, 0, 0), (1, 0, 0), GE.circle_outline(r, 22, 8), L, "w", smooth=True, dark=dk))
        o += wheel(cam, 11, "w", lambda t: (40 * t, 16 + 50 * t ** 2.0), lambda t: (22 * t ** 1.6, 42 + 26 * t ** 1.8),
                   lambda t, s: 38 * (1 - t) ** 2.4 * s, t0s=(0.0,), R2=66, back=6)
        o += hole3(cam, (-.1, 0, 0), (-1, 0, 0), 8, "w3", 14)
        return o
    return fit(fn, 26, 22, (24, 24, 296, 172), sh_ry=7, sh_k=.5)


# =====================================================================================
# marineaux.mxtcassy — turbocharger: air inlet + aluminium compressor volute with the delivery
# branch, bearing housing on its foot, turbine casing with the gas inlet on top, axial gas outlet
# =====================================================================================
@part("marineaux.mxtcassy")
def _():
    def fn(sc):
        CYL(sc, (-56, 0, 0), (1, 0, 0), 46, 8, "alu", seg=40)                    # inlet flange
        CYL(sc, (-48, 0, 0), (1, 0, 0), 40, 28, "alu", seg=36)                   # inlet casing
        CYL(sc, (-20, 0, 0), (1, 0, 0), 70, 40, "alu", seg=48, bands=14)         # compressor volute
        CYL(sc, (-10, -60, 34), (0, -1, 0), 22, 34, "alu", -2, seg=28)           # delivery branch
        CYL(sc, (-10, -94, 34), (0, -1, 0), 30, 7, "alu", -3, seg=28)
        CYL(sc, (20, 0, 0), (1, 0, 0), 40, 46, "w", seg=36)                      # bearing housing
        BOX(sc, 24, -50, -76, 38, 100, 40, "w", ch=4)                            # foot
        BOX(sc, -70, -80, -88, 230, 160, 12, "dk", dark=1)                       # base plate
        CYL(sc, (66, 0, 0), (1, 0, 0), 74, 52, "w", seg=48, bands=14, dark=1)    # turbine casing
        CYL(sc, (92, 0, 60), (0, 0, 1), 30, 40, "w", -2, seg=28)                 # gas inlet
        CYL(sc, (92, 0, 100), (0, 0, 1), 40, 8, "w", -3, seg=32)
        CYL(sc, (118, 0, 0), (1, 0, 0), 60, 34, "w", seg=40)                     # gas outlet
        CYL(sc, (152, 0, 0), (1, 0, 0), 68, 8, "w", seg=40)

        def m1(s_):
            cam = s_.cam
            return (hole3(cam, (-56.1, 0, 0), (-1, 0, 0), 32, "bg", 36) + hole3(cam, (-56.15, 0, 0), (-1, 0, 0), 12, "alus2", 20) +
                    bolts(cam, (-56.1, 0, 0), (-1, 0, 0), 40, 12, 2))
        RAW(sc, m1, ((-56.3, -46, -46), (-56.1, 46, 46)), -4)

        def m2(s_):
            cam = s_.cam
            return (hole3(cam, (-10, -101.1, 34), (0, -1, 0), 18, "bg", 24) + bolts(cam, (-10, -101.1, 34), (0, -1, 0), 25, 8, 1.8) +
                    hole3(cam, (92, 0, 108.1), (0, 0, 1), 24, "bg", 28) + bolts(cam, (92, 0, 108.1), (0, 0, 1), 34, 10, 2))
        RAW(sc, m2, ((-40, -101.3, 26), (132, -101.1, 108.2)), -6)
    return fit(fn, 30, 22, (24, 12, 296, 180), sh_ry=8, sh_k=.5)


# =====================================================================================
# marineaux.mxpump — jerk-type injection pump: roller-tappet housing, forged body with the fuel
# rack, delivery-valve holder on top; beside it the matched plunger / barrel element
# =====================================================================================
@part("marineaux.mxpump")
def _():
    def fn(sc):
        CYL(sc, (0, 0, -70), (0, 0, 1), 34, 70, "w", seg=32, dark=1)             # tappet housing
        BOX(sc, -52, -52, 0, 104, 104, 14, "w", ch=10)                           # mounting flange
        BOX(sc, -40, -40, 14, 80, 80, 92, "w", ch=12)                            # pump body
        CYL(sc, (0, 0, 106), (0, 0, 1), 26, 16, "w", seg=32)
        CYL(sc, (0, 0, 122), (0, 0, 1), 20, 18, "w", seg=6, bands=6)             # delivery-valve holder (hex)
        CYL(sc, (0, 0, 140), (0, 0, 1), 10, 14, "w", seg=20)                     # HP outlet
        CYL(sc, (-40, -14, 60), (-1, 0, 0), 12, 10, "w", -1, seg=24)             # rack housing
        CYL(sc, (-50, -14, 60), (-1, 0, 0), 6, 34, "w", -2, seg=16)              # fuel rack
        CYL(sc, (0, -40, 40), (0, -1, 0), 11, 12, "w", -1, seg=20)               # fuel inlet
        # element: barrel (flanged, spill ports) and plunger drawn half out of it
        x = 120
        CYL(sc, (x, -10, -78), (0, 0, 1), 15, 6, "w", seg=24)                    # plunger foot
        CYL(sc, (x, -10, -72), (0, 0, 1), 8, 82, "w", seg=20)                    # plunger
        CYL(sc, (x, -10, 10), (0, 0, 1), 18, 84, "w", seg=28)                    # barrel
        CYL(sc, (x, -10, 94), (0, 0, 1), 27, 12, "w", seg=32)

        def m(s_):
            cam = s_.cam
            o = ""
            for dx, dy in ((-44, -44), (44, -44), (-44, 44), (44, 44)):
                o += hole3(cam, (dx, dy, 14.1), (0, 0, 1), 3.4, "bg", 10)
            o += hole3(cam, (0, -52.1, 40), (0, -1, 0), 5, "bg", 12) + hole3(cam, (0, 0, 154.1), (0, 0, 1), 3, "bg", 10)
            o += hole3(cam, (x, -10, 106.1), (0, 0, 1), 7, "bg", 14)
            # helix edge on the plunger + spill ports on the barrel
            hx = [cam.xy((x + 8.1 * math.cos(math.radians(a)), -10 + 8.1 * math.sin(math.radians(a)), -20 + a * .1)) for a in range(-200, 1, 20)]
            o += path(P(hx, False), "el")
            for a in (-130, -60):
                t = math.radians(a)
                o += hole3(cam, (x + 18 * math.cos(t), -10 + 18 * math.sin(t), 70), (math.cos(t), math.sin(t), 0), 3, "bg", 10)
            return o
        RAW(sc, m, ((-52, -60, 14.1), (150, 40, 154.2)), -6)
    return fit(fn, -30, 22, (40, 10, 280, 180), sh_ry=8, sh_k=.55)


# =====================================================================================
# marineaux.mxnozzle — fuel valve lying with its tip toward the viewer: atomiser tip with the spray
# holes, nozzle cap nut, valve body, clamp flange, inlet connection and the solenoid head
# =====================================================================================
@part("marineaux.mxnozzle")
def _():
    def fn(sc):
        cam = sc.cam
        o = ""
        segs = [(0, 8, 5.5, 7.5, "w"), (8, 22, 9, 9, "w"), (30, 20, 12, 17, "w"), (50, 8, 17, 17, "w"), (58, 110, 17, 17, "w"),
                (168, 16, 25, 25, "w"), (184, 34, 17, 17, "w"), (218, 34, 21, 21, "dk"), (252, 8, 12, 12, "m")]
        for x0, L, r0, r1, m in reversed(segs):
            o += compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), GE.circle_outline(r1, 26, 8), L, m, smooth=True, scale=lambda t, a=r0 / r1: a + (1 - a) * t))
            if x0 == 184:
                o += compact(GE.prism(cam, (200, -17, 0), (0, -1, 0), GE.circle_outline(8, 18, 6), 16, "w", smooth=True))
                o += compact(GE.prism(cam, (200, -33, 0), (0, -1, 0), GE.circle_outline(11, 6, 6), 8, "w"))
                o += hole3(cam, (200, -41.1, 0), (0, -1, 0), 4, "bg", 10)
        o += compact(GE.prism(cam, (0, 0, 0), (-1, 0, 0), GE.circle_outline(5.5, 20, 6), 3, "w", smooth=True, scale=lambda t: 1 - .55 * t))
        for k in range(8):
            a = 2 * math.pi * (k + .5) / 8
            nrm = GE._norm((-.6, math.cos(a), math.sin(a)))
            if vis(cam, nrm, -0.1):
                o += hole3(cam, (-1.6, 3.8 * math.cos(a), 3.8 * math.sin(a)), nrm, .7, "bg", 8)
        o += hole3(cam, (167.9, 0, 21), (-1, 0, 0), 3, "bg", 10) + hole3(cam, (167.9, 0, -21), (-1, 0, 0), 3, "bg", 10)
        return o
    return fit(fn, 20, 20, (16, 40, 304, 166), sh_ry=6, sh_k=.46)


# =====================================================================================
# marineaux.mxhpline — common rail with branch bosses and double-walled (jacketed) high-pressure
# pipes; the cut pipe end shows the inner pipe inside the jacket
# =====================================================================================
@part("marineaux.mxhpline")
def _():
    def fn(sc):
        CYL(sc, (-10, 0, 0), (1, 0, 0), 30, 10, "w", seg=32)
        CYL(sc, (0, 0, 0), (1, 0, 0), 24, 300, "w", seg=32, bands=12)
        CYL(sc, (300, 0, 0), (1, 0, 0), 30, 10, "w", seg=32)
        for i, xb in enumerate((45, 120, 195, 270)):
            CYL(sc, (xb, 0, 22), (0, 0, 1), 12, 12, "w", seg=18, bands=6)
            CYL(sc, (xb, 0, 34), (0, 0, 1), 14, 12, "w", seg=6, bands=6)
            CYL(sc, (xb, 0, 46), (0, 0, 1), 8, 54, "w", seg=16, bands=6)
            BOX(sc, xb - 10, -10, 100, 20, 20, 20, "w", ch=3)
            CYL(sc, (xb, -10, 110), (0, -1, 0), 8, 50, "w", -1, seg=16, bands=6)
            CYL(sc, (xb, -60, 110), (0, -1, 0), 12, 12, "w", -2, seg=6, bands=6)
            CYL(sc, (xb, -72, 110), (0, -1, 0), 8, 14, "w", -3, seg=20, bands=8)
            CYL(sc, (xb, -86, 110), (0, -1, 0), 4.2, 16, "w", -4, seg=16)

        RAW(sc, lambda s_: hole3(s_.cam, (-10.1, 0, 0), (-1, 0, 0), 22, "w3", 28) + bolts(s_.cam, (-10.1, 0, 0), (-1, 0, 0), 25, 6, 2),
            ((-10.3, -30, -30), (-10.1, 30, 30)), -2)
        for xb in (45, 120, 195, 270):
            RAW(sc, lambda s_, xb=xb: hole3(s_.cam, (xb, -86.1, 110), (0, -1, 0), 6.6, "bg", 12) + hole3(s_.cam, (xb, -102.1, 110), (0, -1, 0), 1.8, "bg", 8),
                ((xb - 8, -102.3, 102), (xb + 8, -86.1, 118)), -6)
    return fit(fn, -26, 24, (20, 12, 300, 180), sh_ry=7, sh_k=.5)


# =====================================================================================
# marineaux.mxscr — SCR reactor with the front wall cut away: three tiers of honeycomb catalyst
# blocks, inlet transition + urea injection on top, outlet hopper below; person for scale
# =====================================================================================
@part("marineaux.mxscr")
def _():
    W, D, H = 150, 120, 200

    def fn(sc):
        BOX(sc, 0, D - 4, 0, W, 4, H, "w", dark=1)                               # back wall
        BOX(sc, -4, 0, 0, 4, D, H, "w", -1)                                      # left wall (cut edge in front)
        BOX(sc, W, 0, 0, 4, D, H, "w")
        BOX(sc, -4, -4, 170, W + 8, 4, 30, "w", -2)                              # front wall, top strip
        BOX(sc, -4, -4, 0, W + 8, 4, 36, "w", -2)                                # front wall, bottom strip
        for z0 in (52, 92, 132):
            BOX(sc, 0, 0, z0, W, D - 4, 26, "alu")

        def cat(s_):
            cam = s_.cam
            o = ""
            for z0 in (52, 92, 132):
                for k in range(1, 4):
                    o += path(P([cam.xy((k * W / 4, -.1, z0)), cam.xy((k * W / 4, -.1, z0 + 26))], False), "el")
                d = ""
                for k in range(1, 30):
                    d += P([cam.xy((k * W / 30, -.1, z0 + 1)), cam.xy((k * W / 30, -.1, z0 + 25))], False)
                for k in range(1, 6):
                    d += P([cam.xy((1, -.1, z0 + k * 26 / 6)), cam.xy((W - 1, -.1, z0 + k * 26 / 6))], False)
                o += path(d, "gr")
            return o
        RAW(sc, cat, ((0, -.2, 52), (W, -.1, 158)), -3)
        Z(sc, H, 46, [(-4, -4), (W + 4, -4), (W + 4, D), (-4, D)], "w", -1, scale=lambda t: 1 - .62 * t)   # inlet transition
        CYL(sc, (W / 2, D / 2 - 2, H + 46), (0, 0, 1), 30, 40, "w", seg=28)
        CYL(sc, (W / 2, D / 2 - 2, H + 86), (0, 0, 1), 36, 6, "w", seg=28)
        CYL(sc, (W / 2, D / 2 - 32, H + 66), (0, -1, 0), 4, 26, "m", -2, seg=12)                   # urea injection lance
        Z(sc, -40, 40, [(-4, -4), (W + 4, -4), (W + 4, D), (-4, D)], "w", scale=lambda t: .38 + .62 * t)  # outlet hopper
        CYL(sc, (W / 2, D / 2 - 2, -80), (0, 0, 1), 28, 40, "w", seg=28)
        return person_at(sc.cam, (W + 40, -30, -80), 34)
    return fit(fn, -30, 20, (40, 8, 280, 182), sh_ry=8, sh_k=.55)


# =====================================================================================
# marineaux.mxscrub — SOx scrubber tower: tall shell with stiffening rings, gas inlet low on the
# side, wash-water spray inlets at three levels, top cone to the outlet; person for scale
# =====================================================================================
@part("marineaux.mxscrub")
def _():
    R = 56

    def fn(sc):
        CYL(sc, (0, 0, -30), (0, 0, 1), 26, 30, "w", seg=28)                     # drain / sump outlet
        CYL(sc, (0, 0, 0), (0, 0, 1), R, 30, "w", seg=36, bands=10, dark=1)
        z = 30
        for h in (70, 70, 70, 50):
            CYL(sc, (0, 0, z), (0, 0, 1), R, h - 4, "w", seg=32, bands=8)
            CYL(sc, (0, 0, z + h - 4), (0, 0, 1), R + 3, 4, "w", seg=32, bands=6, dark=1)
            z += h
        CYL(sc, (0, 0, z), (0, 0, 1), R, 40, "w", seg=36, bands=10, r1=24)
        CYL(sc, (0, 0, z + 40), (0, 0, 1), 24, 40, "w", seg=28)
        CYL(sc, (0, 0, z + 80), (0, 0, 1), 30, 6, "w", seg=28)
        CYL(sc, (0, -R + 6, 62), (0, -1, 0), 26, 60, "w", -2, seg=28)             # gas inlet
        CYL(sc, (0, -R - 54, 62), (0, -1, 0), 32, 6, "w", -3, seg=28)
        for zz in (150, 210, 262):
            CYL(sc, (-R + 6, -20, zz), (-1, 0, 0), 5, 24, "m", -2, seg=12)        # spray-water inlets
            CYL(sc, (-R - 18, -20, zz), (-1, 0, 0), 9, 4, "m", -3, seg=16)

        def m(s_):
            cam = s_.cam
            return hole3(cam, (0, -R - 60.1, 62), (0, -1, 0), 21, "bg", 24) + bolts(cam, (0, -R - 60.1, 62), (0, -1, 0), 27, 10, 1.6)
        RAW(sc, m, ((-32, -R - 60.3, 30), (32, -R - 60.1, 94)), -5)
        return person_at(sc.cam, (R + 50, -40, -30), 26)
    return fit(fn, -30, 18, (60, 8, 260, 184), sh_ry=8, sh_k=.6)
