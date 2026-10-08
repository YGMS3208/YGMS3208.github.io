"""v3 shaded-3D part drawings for the engine system (block, head, camshaft, con-rod, valves, turbo,
injector, common rail, catalyst, engine assembly) and the vehicle plant (press, body, paint, assembly,
inspection). engine.crank / engine.piston live in il3_pilot.py."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P


# =====================================================================================
# local helpers
# =====================================================================================
def _area2(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2


def clip(subj, clipper):
    """Sutherland-Hodgman: subj polygon clipped by a convex polygon (screen coords)."""
    if _area2(clipper) < 0:
        clipper = clipper[::-1]
    out = list(subj)
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        if not inp:
            break

        def ins(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

        def cut(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        s = inp[-1]
        for e in inp:
            if ins(e):
                if not ins(s):
                    out.append(cut(s, e))
                out.append(e)
            elif ins(s):
                out.append(cut(s, e))
            s = e
    return out


def bore(cam, C, A, r, depth, wall="ws2", seg=32, steps=("bg",)):
    """open bore seen at an angle: lit far wall, darkening with depth (each step clipped to the opening)."""
    top = circ3(cam, C, A, r, seg)
    o = path(P(top), wall)
    for k, c in enumerate(steps):
        d = depth * (k + 1) / len(steps)
        inner = clip(circ3(cam, tuple(C[i] - d * A[i] for i in range(3)), A, r, seg), top)
        if len(inner) > 2:
            o += path(P(inner), c)
    return o


def row_union(cs, r, y0, seg=36):
    """outline (x, y) of the union of equal circles centred on a row (x_i, y0)."""
    def inside(x, y, j):
        return any(k != j and (x - c) ** 2 + (y - y0) ** 2 < r * r - 1e-6 for k, c in enumerate(cs))
    up, lo = [], []
    for j, c in enumerate(cs):
        for k in range(seg + 1):
            a = math.pi - math.pi * k / seg
            x, y = c + r * math.cos(a), y0 + r * math.sin(a)
            if not inside(x, y, j):
                up.append((x, y))
    for j, c in reversed(list(enumerate(cs))):
        for k in range(seg + 1):
            a = -math.pi * k / seg
            x, y = c + r * math.cos(a), y0 + r * math.sin(a)
            if not inside(x, y, j):
                lo.append((x, y))
    return up + lo


def poly3(cam, pts, c):
    return path(P([cam.xy(p) for p in pts]), c)


def shcls(mat, nrm, dark=0):
    return "%ss%d" % (mat, min(4, GE.shade(nrm) + dark))


# =====================================================================================
# engine.block — inline-4 aluminium block: machined deck with 4 iron-liner bores, open-deck water
# jacket around the siamesed bores, 10 head-bolt holes; skirt with bulkhead ribs, pan rail,
# oil-filter boss on the side, crank seal bore and front-cover bolt holes on the timing end
# =====================================================================================
def block(az=27, el=31):
    L, Wu, zt = 380, 80, 230
    bx = [58 + 88 * i for i in range(4)]
    rb = 40

    def fn(sc):
        BOX(sc, -4, -124, 0, L + 8, 248, 10, "w", dark=1)                                  # pan rail
        X(sc, 0, L, [(-112, 10), (112, 10), (Wu, 100), (-Wu, 100)], "w", dark=1)          # skirt
        BOX(sc, 0, -Wu, 100, L, 2 * Wu, zt - 100, "w", ch=5)                              # cylinder section
        for x in (14, 102, 190, 278, 366):                                                # bulkhead ribs
            X(sc, x - 5, 10, [(-112, 10), (-121, 10), (-121, 24), (-85, 100), (-Wu, 100)], "w", -1, dark=1)
        CYL(sc, (300, -Wu, 160), (0, -1, 0), 26, 8, "w", -1, seg=32)                     # oil-filter boss
        CYL(sc, (300, -Wu - 8, 160), (0, -1, 0), 20, 3, "w", -1, seg=32)
        BOX(sc, 40, -Wu - 10, 120, 50, 10, 40, "w", -1, ch=3)                             # mount boss

        def deck(s_):
            cam = s_.cam
            z = zt + .05
            o = poly3(cam, [(x, y, z) for x, y in row_union(bx, 55, 0)], "bg")             # water jacket
            o += poly3(cam, [(x, y, z) for x, y in row_union(bx, 46, 0)], "w")             # siamesed walls
            for x in bx:
                o += path(P(circ3(cam, (x, 0, z), (0, 0, 1), rb + 3.5, 36)), "ms1")       # iron liner top
                o += bore(cam, (x, 0, z), (0, 0, 1), rb, 60, "ms3", 36, ("ms4", "bg"))
            for x in [14, 102, 190, 278, 366]:
                for y in (-66, 66):
                    o += hole3(cam, (x, y, z), (0, 0, 1), 5.5, "w3") + hole3(cam, (x, y, z), (0, 0, 1), 4)
            for x, y in ((20, 40), (370, -40), (190, 52), (102, -52), (278, -52)):        # oil / water holes
                o += hole3(cam, (x, y, z), (0, 0, 1), 3.2)
            return o
        RAW(sc, deck, ((0, -Wu, zt), (L, Wu, zt + .1)), -3)

        def end(s_):
            cam = s_.cam
            x = -.1
            o = hole3(cam, (x, 0, 62), (-1, 0, 0), 34, "w3") + hole3(cam, (x, 0, 62), (-1, 0, 0), 28)
            for y, z in ((-60, 30), (60, 30), (-70, 120), (70, 120), (-62, 200), (62, 200), (0, 150), (-30, 205), (30, 205)):
                o += hole3(cam, (x, y, z), (-1, 0, 0), 3.4)
            return o
        RAW(sc, end, ((-.2, -112, 0), (0, 112, zt)), -2)

        def side(s_):
            cam = s_.cam
            y = -Wu - 11.05
            return hole3(cam, (300, y, 160), (0, -1, 0), 8, "w3") + hole3(cam, (300, y, 160), (0, -1, 0), 5) + \
                hole3(cam, (300, y, 160 + 14), (0, -1, 0), 2.5)
        RAW(sc, side, ((280, -Wu - 11.2, 140), (320, -Wu - 11.1, 180)), -3)
    return fit(fn, az, el, (26, 12, 294, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("engine.block")
def _():
    return block()


# =====================================================================================
# engine.head — DOHC aluminium head, cam side up: rocker-cover rail, 5 cam bulkheads with bolted
# bearing caps (2 cam bores each), bucket-tappet bores in pairs, spark-plug tubes between the cams,
# 4 exhaust ports with manifold studs on the side, cam bores and bolt holes on the timing end
# =====================================================================================
def head(az=27, el=33):
    L, W, zf = 380, 85, 80
    cx = [58 + 88 * i for i in range(4)]
    bk = [14, 102, 190, 278, 366]
    yc, zc = 34, 112

    def fn(sc):
        BOX(sc, 0, -W, 0, L, 2 * W, zf, "w", ch=5)
        BOX(sc, 0, -W, zf, L, 9, 20, "w")                                  # rail: front
        BOX(sc, 0, W - 9, zf, L, 9, 20, "w")                               # rail: back
        BOX(sc, 0, -W + 9, zf, 9, 2 * W - 18, 20, "w")                     # rail: timing end
        BOX(sc, L - 9, -W + 9, zf, 9, 2 * W - 18, 20, "w")
        for i, x in enumerate(bk):
            x0 = max(9, x - 10)
            x1 = min(L - 9, x + 10)
            BOX(sc, x0, -yc - 22, zf, x1 - x0, 2 * yc + 44, zc - zf, "w", dark=1)        # bulkhead wall
            for y in (-yc, yc):
                BOX(sc, x0, y - 21, zc, x1 - x0, 42, 15, "w")                           # bearing cap

            def face(s_, x0=x0):
                cam = s_.cam
                o = ""
                xf = x0 - .05
                for y in (-yc, yc):
                    o += hole3(cam, (xf, y, zc), (-1, 0, 0), 13.5, "w3", 24) + hole3(cam, (xf, y, zc), (-1, 0, 0), 11, "bg", 24)
                    o += path(P([cam.xy((xf, y - 21, zc)), cam.xy((xf, y - 12, zc))], False) +
                              P([cam.xy((xf, y + 12, zc)), cam.xy((xf, y + 21, zc))], False), "el")
                    for dy in (-15, 15):
                        o += hole3(cam, (x0 + 10, y + dy, zc + 15.05), (0, 0, 1), 3.2)
                return o
            RAW(sc, face, ((x0 - .1, -yc - 22, zf), (x0, yc + 22, zc + 15)), -1)
        for x in cx:
            CYL(sc, (x, 0, zf), (0, 0, 1), 12, 30, "w", seg=24)                         # plug tube

        def floor(s_):
            cam = s_.cam
            o = ""
            for x in cx:
                for y in (-yc, yc):
                    for dx in (-21, 21):
                        o += bore(cam, (x + dx, y, zf), (0, 0, 1), 14.5, 22, "ws3", 24)
            return o
        RAW(sc, floor, ((9, -W + 9, zf - .05), (L - 9, W - 9, zf)), -1)

        def tops(s_):
            cam = s_.cam
            o = ""
            for x in cx:
                o += hole3(cam, (x, 0, zf + 30.05), (0, 0, 1), 8, "bg")
            return o
        RAW(sc, tops, ((0, -12, zf + 30), (L, 12, zf + 30.1)), -3)

        def side(s_):
            cam = s_.cam
            y = -W - .05
            o = ""
            for x in cx:
                pts = [(x + 14 * math.cos(math.radians(a)) + (12 if math.cos(math.radians(a)) > 0 else -12),
                        y, 40 + 13 * math.sin(math.radians(a))) for a in range(0, 360, 20)]
                o += poly3(cam, pts, "ws3") + poly3(cam, [(p[0] * .82 + x * .18, y, p[2] * .82 + 40 * .18 - 3) for p in pts], "bg")
                for dx in (-34, 34):
                    o += hole3(cam, (x + dx, y, 40), (0, -1, 0), 3)
            for x in (20, 150, 230, 360):
                o += hole3(cam, (x, y, 66), (0, -1, 0), 2.6)
            return o
        RAW(sc, side, ((0, -W - .1, 0), (L, -W, zf)), -2)

        def end(s_):
            cam = s_.cam
            o = ""
            for y, z in ((-60, 20), (60, 20), (-20, 55), (20, 55), (0, 25)):
                o += hole3(cam, (-.05, y, z), (-1, 0, 0), 4)
            return o
        RAW(sc, end, ((-.1, -W, 0), (0, W, zf)), -2)
    return fit(fn, az, el, (26, 14, 294, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("engine.head")
def _():
    return head()


# =====================================================================================
# engine.cam — assembled camshaft: steel tube with pressed-on lobes (2 per cylinder, phased by
# firing order 1-3-4-2), 5 ground journals, sprocket flange with dowel and centre bolt at the front
# =====================================================================================
def camshaft(az=24, el=22):
    rt, rj, rb_, rn, en = 10, 15, 17, 7, 13
    ph = [0, 270, 90, 180]

    def lobe(phi):
        a = math.radians(phi)
        pts = arc(0, 0, rb_, phi + 60, phi + 300, 10) + arc(en * math.cos(a), en * math.sin(a), rn, phi - 80, phi + 80, 6)
        return banded(hull(pts), 2)

    def fn(sc):
        def face(s_):
            o = hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 8, "w3") + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 5.5)
            return o + hole3(s_.cam, (-.1, 0, 15), (-1, 0, 0), 2.6)
        RAW(sc, face, ((-.2, -26, -26), (0, 26, 26)), -2)
        CYL(sc, (0, 0, 0), (1, 0, 0), 26, 8, "w", seg=36)
        CYL(sc, (8, 0, 0), (1, 0, 0), 13, 8, "w", seg=24, dark=1)
        x = 16
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, 16, "w", seg=20, bands=6)
        x += 16
        for c in range(4):
            for L, kind in ((7, "t"), (13, "l"), (16, "t"), (13, "l"), (7, "t"), (16, "j")):
                if kind == "t":
                    CYL(sc, (x, 0, 0), (1, 0, 0), rt, L, "w", seg=16, bands=6, dark=1)
                elif kind == "l":
                    X(sc, x, L, lobe(90 + ph[c]), "w", smooth=True, cap_mat="w2")
                else:
                    CYL(sc, (x, 0, 0), (1, 0, 0), rj, L, "w", seg=20, bands=6)
                x += L
        CYL(sc, (x, 0, 0), (1, 0, 0), 11, 10, "w", seg=20, dark=1)
    return fit(fn, az, el, (22, 40, 298, 166), sh_ry=6, sh_k=.46)


@part("engine.cam")
def _():
    return camshaft()


# =====================================================================================
# engine.conrod — forged rod lying on edge: big end (fracture-split cap: rough split line, bolts
# seated on spot faces), I-beam shank with recessed web, small end with oil hole
# =====================================================================================
def conrod(az=30, el=24, tilt=14):
    t, Ls, rbo, rso = 22, 150, 27, 11
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def R(u, v):
        return (u * ca - v * sa, u * sa + v * ca)

    def W(u, v, y):
        a, b = R(u, v)
        return (a, y, b)

    big = [(20, 30), (14, 47), (-26, 47), (-26, 34)] + arc(0, 0, 40, 122, 238, 10) + [(-26, -34), (-26, -47), (14, -47), (20, -30)]
    small = arc(Ls, 0, 18, 215, 505, 16)
    out = [R(u, v) for u, v in big + small]

    def fn(sc):
        cam = sc.cam
        loop = [(u, v, i) for i, (u, v) in enumerate(out)]
        holes = [[(*R(u, v), 0) for u, v in arc(0, 0, rbo, 0, 360, 36)[:-1]],
                 [(*R(u, v), 0) for u, v in arc(Ls, 0, rso, 0, 360, 20)[:-1]]]
        o = compact(GE.prism(cam, (0, t / 2, 0), (0, -1, 0), loop, t, "w", holes=holes, smooth="outer"))
        y = -t / 2 - .05
        web = [(44, 15), (128, 8.5), (128, -8.5), (44, -15)]
        o += poly3(cam, [W(u, v, y) for u, v in web], "ws3")
        o += path(P([cam.xy(W(u, v, y)) for u, v in ((44, 15), (128, 8.5))], False) +
                  P([cam.xy(W(u, v, y)) for u, v in ((44, -15), (128, -8.5))], False), "el")
        # fracture split line on the face and across the top, through the big-end centre
        jag = [(0, 47), (1.2, 44), (-.8, 41), (.9, 37), (-.6, 33), (.5, 29.5)]
        o += path(P([cam.xy(W(u, v, y)) for u, v in jag], False) + P([cam.xy(W(u, -v, y)) for u, v in jag], False), "el")
        o += path(P([cam.xy(W(u, 47, yy)) for u, yy in ((0, y), (1, -4), (-.8, 3), (0, t / 2))], False), "el")
        # oil hole on the small end
        cx, cz = R(Ls, 18)
        o += hole3(cam, (cx, 0, cz + .05), (-sa, 0, ca), 2.6)
        # bolt heads on the cap spot faces
        for v in (40.5, -40.5):
            bx, bz = R(-26, v)
            o += compact(GE.prism(cam, (bx, 0, bz), (-ca, 0, -sa), GE.circle_outline(6.5, 6, 6), 7, "m", smooth=False))
            hx, hz = R(-33.1, v)
            o += hole3(cam, (hx, 0, hz), (-ca, 0, -sa), 3, "ms3", 6)
        return o
    return fit(fn, az, el, (30, 22, 290, 176), sh_ry=7, sh_k=.5, sh_dy=-6)


@part("engine.conrod")
def _():
    return conrod()


# =====================================================================================
# engine.valve — intake (front, larger) and exhaust valves: flat face, margin, 45° seat, tulip
# fillet, long stem, collet grooves and hardened tip; friction-weld line on the exhaust stem
# =====================================================================================
def valves(az=32, el=24):
    def valve(sc, y, R, L, rs, weld=False):
        CYL(sc, (0, y, 0), (1, 0, 0), R, 2.2, "w", seg=36, bands=9)
        CYL(sc, (2.2, y, 0), (1, 0, 0), R, 3.6, "w", seg=36, r1=R - 3.6, bands=9)
        CYL(sc, (5.8, y, 0), (1, 0, 0), R - 3.6, 6, "w", seg=28, r1=R * .42, dark=1, bands=7)
        CYL(sc, (11.8, y, 0), (1, 0, 0), R * .42, 9, "w", seg=20, r1=rs * 1.5, dark=1, bands=5)
        CYL(sc, (20.8, y, 0), (1, 0, 0), rs * 1.5, 9, "w", seg=16, r1=rs, bands=4)
        x = 29.8
        segs = [(L - 16 - x, 0), (2.2, 2), (1.8, 0), (2.2, 2), (1.8, 0), (2.2, 2), (5.6, 0)]
        for ln, dk in segs:
            CYL(sc, (x, y, 0), (1, 0, 0), rs - (.9 if dk else 0), ln, "w", seg=12, bands=4, dark=dk)
            x += ln
        if weld:
            def wl(s_, y=y):
                return path(P([s_.cam.xy((62, y + rs * math.cos(a), rs * math.sin(a))) for a in [math.radians(k) for k in range(100, 265, 15)]], False), "el")
            RAW(sc, wl, ((61.9, y - rs, -rs), (62.1, y - rs + .1, rs)), -2)

        def face(s_, y=y):
            c = (-.1, y, 0)
            return path(P(circ3(s_.cam, c, (-1, 0, 0), R * .8, 32)), "gr") + path(P(circ3(s_.cam, c, (-1, 0, 0), R * .45, 24)), "gr")
        RAW(sc, face, ((-.2, y - R, -R), (0, y + R, R)), -2)

    def fn(sc):
        valve(sc, 46, 14.5, 108, 3.0, True)
        valve(sc, 0, 17.5, 112, 3.0)
    return fit(fn, az, el, (34, 30, 286, 170), sh_ry=6, sh_k=.42, sh_dy=-2)


@part("engine.valve")
def _():
    return valves()


# =====================================================================================
# engine.turbo — turbocharger: aluminium compressor scroll with axial inlet (compressor wheel seen
# inside) and tangential outlet, bearing (centre) housing with oil inlet, cast-iron turbine scroll
# with inlet flange, wastegate actuator can and rod
# =====================================================================================
def spiral(r0, r1, a0=200, span=330, seg=22):
    return banded(hull([(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
                        for r, a in ((r0 + (r1 - r0) * k / seg, a0 + span * k / seg) for k in range(seg + 1))]), 2)


def turbo(az=28, el=24):
    def fn(sc):
        cv = spiral(50, 66)
        X(sc, -9, 9, cv, "w", smooth=True, scale=lambda t: .84 + .16 * t)
        X(sc, 0, 28, cv, "w", smooth=True)
        X(sc, 28, 8, cv, "w", smooth=True, dark=1, scale=lambda t: 1 - .14 * t)
        RING(sc, (-34, 0, 0), (1, 0, 0), 34, 28.5, 25, "w", seg=36, bands=9)
        RING(sc, (-40, 0, 0), (1, 0, 0), 36, 28.5, 6, "w", seg=36, bands=9)

        def wheel(s_):
            cam = s_.cam
            x = -9
            o = path(P(circ3(cam, (x, 0, 0), (1, 0, 0), 28.5, 32)), "ms3")
            d = ""
            for k in range(10):
                a0 = 2 * math.pi * k / 10
                d += P([cam.xy((x - 3 * j, (6 + 4.4 * j) * math.cos(a0 + .16 * j), (6 + 4.4 * j) * math.sin(a0 + .16 * j))) for j in range(6)], False)
            o += path(d, "el") + path(P(circ3(cam, (x - 16, 0, 0), (1, 0, 0), 6, 12)), "m")
            return o
        RAW(sc, wheel, ((-9.1, -28, -28), (-9, 28, 28)), -1)
        CYL(sc, (14, -46, 30), (0, 0, 1), 17, 46, "w", -1, seg=28)                         # compressor outlet
        CYL(sc, (14, -46, 76), (0, 0, 1), 20, 5, "w", -1, seg=28)
        RAW(sc, lambda s_: hole3(s_.cam, (14, -46, 81.1), (0, 0, 1), 13, "bg"), ((-6, -66, 81), (34, -26, 81.2)), -2)
        CYL(sc, (36, 0, 0), (1, 0, 0), 30, 30, "m", seg=32, dark=1)                        # bearing housing
        CYL(sc, (51, 0, 26), (0, 0, 1), 8, 10, "m", -1, seg=16)
        RAW(sc, lambda s_: hole3(s_.cam, (51, 0, 36.1), (0, 0, 1), 4), ((43, -8, 36), (59, 8, 36.2)), -2)
        tv = spiral(44, 60, 160)
        X(sc, 66, 8, tv, "m", smooth=True, scale=lambda t: .84 + .16 * t)
        X(sc, 74, 32, tv, "m", smooth=True, dark=1)
        BOX(sc, 72, -56, -78, 40, 52, 10, "m", -1, ch=4)                                    # turbine inlet flange
        X(sc, 82, 20, [(-48, -68), (-12, -68), (-8, -40), (-44, -40)], "m", -1, dark=1)
        CYL(sc, (2, -66, -44), (1, 0, 0), 2.2, 84, "m", -1, seg=8, bands=4)                 # wastegate rod
        CYL(sc, (-14, -66, -44), (1, 0, 0), 17, 16, "m", -2, seg=28)                        # actuator can
    return fit(fn, az, el, (40, 12, 280, 180), sh_ry=7, sh_k=.5, sh_dy=-4)


@part("engine.turbo")
def _():
    return turbo()


# =====================================================================================
# engine.injector — gasoline direct injector lying on its side: multi-hole tip with combustion seal
# ring, slim nozzle body, mounting collar, solenoid housing with moulded connector, fuel inlet with
# O-ring
# =====================================================================================
def injector(az=30, el=24):
    def fn(sc):
        def tip(s_):
            cam = s_.cam
            o = ""
            for k in range(6):
                a = 2 * math.pi * k / 6
                o += hole3(cam, (-.05, 2.2 * math.cos(a), 2.2 * math.sin(a)), (-1, 0, 0), .55, "bg", 8)
            return o
        RAW(sc, tip, ((-.1, -4, -4), (0, 4, 4)), -2)
        x = 0
        for L, r, m, dk, r1 in ((4, 4, "w", 0, None), (3, 4.4, "w2", 0, None), (2, 3.6, "w", 2, None), (20, 4.6, "w", 0, None),
                                (6, 4.6, "w", 0, 7.5), (34, 7.5, "w", 0, None), (6, 11, "w", 0, None), (42, 13, "w", 0, None),
                                (6, 10, "w", 1, None), (8, 8.6, "w", 0, None), (4, 9.6, "dk", 0, None), (10, 8.6, "w", 0, None)):
            if m == "w2":
                CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "pt", seg=16, bands=6)
            else:
                CYL(sc, (x, 0, 0), (1, 0, 0), r, L, m, seg=28 if r > 6 else 16, bands=8 if r > 6 else 5, dark=dk, r1=r1)
            x += L
        BOX(sc, 92, -9, 12, 22, 18, 16, "dk", ch=3)                                          # connector stem
        BOX(sc, 84, -11, 28, 30, 22, 14, "dk", ch=3)                                         # connector shell
        RAW(sc, lambda s_: poly3(s_.cam, [(87, -6, 42.05), (111, -6, 42.05), (111, 6, 42.05), (87, 6, 42.05)], "bg"),
            ((84, -11, 42), (114, 11, 42.1)), -2)
    return fit(fn, az, el, (34, 28, 286, 172), sh_ry=6, sh_k=.42, sh_dy=-3)


@part("engine.injector")
def _():
    return injector()


# =====================================================================================
# engine.railpump — diesel common rail (forged tube, 4 injector outlets with pipe nuts, inlet,
# pressure sensor and pressure-limiting valve at the ends, mounting lugs) and the high-pressure
# supply pump in front (flange, drive shaft, pumping head with outlet)
# =====================================================================================
def railpump(az=28, el=26):
    def hexa(sc, O, A, r, h, mat="w", bias=0.0):
        a = GE._norm(A)
        sc.add(compact(GE.prism(sc.cam, O, a, [(r * math.cos(math.pi * k / 3 + .52), r * math.sin(math.pi * k / 3 + .52), k) for k in range(6)], h, mat)),
               ((O[0] - r, O[1] - r, O[2] - r), (O[0] + r + a[0] * h, O[1] + r + a[1] * h, O[2] + r + a[2] * h)), bias)

    def fn(sc):
        # rail
        hexa(sc, (-22, 0, 0), (1, 0, 0), 12, 8, "w")                                       # pressure sensor
        CYL(sc, (-32, 0, 0), (1, 0, 0), 9, 10, "dk", seg=20, bands=6)
        RAW(sc, lambda s_: hole3(s_.cam, (-32.05, 0, 0), (-1, 0, 0), 5.5, "bg", 14), ((-32.1, -9, -9), (-32, 9, 9)), -2)
        CYL(sc, (-14, 0, 0), (1, 0, 0), 12, 14, "w", seg=24, bands=8)
        CYL(sc, (0, 0, 0), (1, 0, 0), 16, 300, "w", seg=32, bands=10)
        CYL(sc, (300, 0, 0), (1, 0, 0), 12, 14, "w", seg=24, bands=8)
        hexa(sc, (314, 0, 0), (1, 0, 0), 12, 10, "w")                                      # pressure limiter
        for x in (45, 110, 175, 240):
            CYL(sc, (x, 0, 14), (0, 0, 1), 10, 10, "w", -1, seg=20, bands=6)
            hexa(sc, (x, 0, 24), (0, 0, 1), 10, 9, "w", -1)
            CYL(sc, (x, 0, 33), (0, 0, 1), 3.5, 22, "w", -1, seg=12, bands=4)
        CYL(sc, (276, -14, 0), (0, -1, 0), 9, 12, "w", -1, seg=20, bands=6)                 # inlet
        hexa(sc, (276, -26, 0), (0, -1, 0), 9, 8, "w", -1)
        for x in (78, 208):                                                                 # mounting lugs
            BOX(sc, x - 11, 10, -16, 22, 26, 12, "w", -1, dark=1)
        # supply pump (front)
        px, py, pz = 60, -130, -40
        CYL(sc, (px - 26, py, pz), (1, 0, 0), 9, 14, "w", seg=20, bands=6)                 # drive shaft
        RAW(sc, lambda s_: hole3(s_.cam, (px - 26.05, py, pz), (-1, 0, 0), 3, "bg", 10) +
            path(P([s_.cam.xy((px - 26.05, py - 2, pz + 9)), s_.cam.xy((px - 26.05, py + 2, pz + 9))], False), "el"),
            ((px - 26.1, py - 9, pz - 9), (px - 26, py + 9, pz + 9)), -2)
        CYL(sc, (px - 12, py, pz), (1, 0, 0), 44, 8, "w", seg=36, bands=9)                  # flange
        CYL(sc, (px - 4, py, pz), (1, 0, 0), 34, 70, "w", seg=36, bands=9, dark=1)           # body
        BOX(sc, px + 14, py - 22, pz + 24, 40, 44, 26, "w", ch=4)                            # pumping head
        CYL(sc, (px + 34, py, pz + 50), (0, 0, 1), 8, 8, "w", -1, seg=16, bands=5)
        hexa(sc, (px + 34, py, pz + 58), (0, 0, 1), 9, 8, "w", -1)

        def fl(s_):
            o = ""
            for k in range(3):
                a = 2 * math.pi * k / 3 + .3
                o += hole3(s_.cam, (px - 12.05, py + 38 * math.cos(a), pz + 38 * math.sin(a)), (-1, 0, 0), 3.4)
            return o
        RAW(sc, fl, ((px - 12.1, py - 44, pz - 44), (px - 12, py + 44, pz + 44)), -2)
    return fit(fn, az, el, (30, 14, 290, 180), sh_ry=7, sh_k=.5, sh_dy=-4)


@part("engine.railpump")
def _():
    return railpump()


# =====================================================================================
# engine.exhaust — catalytic converter: 2-bolt inlet flange, pipe, diffuser cone, stainless can
# with stiffening beads, outlet cone and pipe; the ceramic honeycomb substrate stands in front
# =====================================================================================
def exhaust(az=30, el=26):
    rp, rc = 16, 50

    def fn(sc):
        cam = sc.cam
        X(sc, -6, 6, banded(hull(arc(0, 0, 24, 0, 360, 16)[:-1] + arc(0, 38, 9, 0, 360, 8) + arc(0, -38, 9, 0, 360, 8)), 2), "w", smooth=True)

        def fl(s_):
            o = hole3(s_.cam, (-6.05, 0, 0), (-1, 0, 0), rp - 1.5, "bg", 20)
            for y in (-38, 38):
                o += hole3(s_.cam, (-6.05, y, 0), (-1, 0, 0), 4.4, "bg", 12)
            return o
        RAW(sc, fl, ((-6.1, -47, -24), (-6, 47, 24)), -2)
        CYL(sc, (0, 0, 0), (1, 0, 0), rp, 34, "w", seg=24, bands=8)
        CYL(sc, (34, 0, 0), (1, 0, 0), rp, 40, "w", seg=36, bands=10, r1=rc)
        x = 74
        for L, dk in ((40, 0), (5, 1), (60, 0), (5, 1), (40, 0)):
            CYL(sc, (x, 0, 0), (1, 0, 0), rc - (1.6 if dk else 0), L, "w", seg=40, bands=10, dark=dk)
            x += L
        CYL(sc, (x, 0, 0), (1, 0, 0), rc, 36, "w", seg=36, bands=10, r1=rp)
        CYL(sc, (x + 36, 0, 0), (1, 0, 0), rp, 44, "w", seg=24, bands=8)
        # ceramic substrate (honeycomb) standing in front
        Cx, Cy, R, H = 150, -122, 40, 52
        CYL(sc, (Cx, Cy, 0 - 50), (0, 0, 1), R, H, "pt", seg=40, bands=10)

        def honey(s_):
            cam = s_.cam
            z = H - 50 + .05
            d = ""
            st = 5.0
            k = -R + st / 2
            while k < R:
                h = math.sqrt(R * R - k * k) - .8
                d += P([cam.xy((Cx + k, Cy - h, z)), cam.xy((Cx + k, Cy + h, z))], False)
                d += P([cam.xy((Cx - h, Cy + k, z)), cam.xy((Cx + h, Cy + k, z))], False)
                k += st
            return path(d, "gr") + path(P(circ3(cam, (Cx, Cy, z), (0, 0, 1), R - 2, 36)), "gr")
        RAW(sc, honey, ((Cx - R, Cy - R, H - 50), (Cx + R, Cy + R, H - 49.9)), -2)
    return fit(fn, az, el, (30, 12, 290, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("engine.exhaust")
def _():
    return exhaust()


# =====================================================================================
# engine.engineassy — assembled inline-4: oil pan, block, head, head cover with 4 ignition coils
# and filler cap, timing cover with crank pulley, plastic intake manifold (plenum,
# 4 runners, throttle body) on the near side
# =====================================================================================
def engineassy(az=30, el=26):
    def fn(sc):
        BOX(sc, 14, -84, 0, 352, 168, 54, "w", dark=1, ch=8)                                 # oil pan
        BOX(sc, 6, -92, 54, 368, 184, 6, "w", dark=1)
        BOX(sc, 0, -96, 60, 380, 192, 176, "w", ch=6)                                      # block
        BOX(sc, 0, -92, 236, 380, 184, 70, "w", ch=6)                                      # head
        X(sc, 10, 360, banded(hull([(-78, 306), (78, 306)] + arc(-52, 322, 26, 90, 180, 4) + arc(52, 322, 26, 0, 90, 4)), 1),
          "dk", smooth=False)                                                              # head cover
        for x in (58, 146, 234, 322):
            CYL(sc, (x, 0, 348), (0, 0, 1), 13, 14, "dk", -1, seg=20, bands=6)               # coil tops
        CYL(sc, (300, -48, 342), (0, 0, 1), 16, 8, "m", -1, seg=24)                         # oil filler cap
        X(sc, -16, 16, banded(hull([(-80, 40), (80, 40), (88, 150), (70, 300), (-70, 300), (-88, 150)]), 1), "w", dark=1)   # timing cover
        CYL(sc, (-34, 0, 96), (1, 0, 0), 46, 18, "m", seg=40, bands=10)                      # crank pulley
        RAW(sc, lambda s_: hole3(s_.cam, (-34.05, 0, 96), (-1, 0, 0), 14, "ms2") + hole3(s_.cam, (-34.05, 0, 96), (-1, 0, 0), 6, "bg") +
            "".join(path(P(circ3(s_.cam, (-34.05, 0, 96), (-1, 0, 0), r, 36)), "gr") for r in (30, 38)), ((-34.1, -46, 50), (-34, 46, 142)), -2)
        # intake manifold (plastic): plenum along x, runners into the head side, throttle body
        CYL(sc, (24, -170, 196), (1, 0, 0), 34, 330, "dk", 1, seg=32, bands=8)
        for x in (58, 146, 234, 322):
            X(sc, x - 20, 40, [(-170, 210), (-150, 232), (-92, 284), (-92, 252), (-140, 196)], "dk", .5, dark=1)
        CYL(sc, (354, -170, 196), (1, 0, 0), 26, 24, "al", 1, seg=24)
    return fit(fn, az, el, (28, 10, 292, 182), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("engine.engineassy")
def _():
    return engineassy()


# =====================================================================================
# plant.press — press shop: a body-side outer panel (one stamping from A-pillar to rear quarter:
# door openings with drawn flanges, quarter-window hole, rear wheel arch) and the steel coil it
# starts from
# =====================================================================================
SIDE = [(140, 20), (140, 96), (150, 97), (225, 145), (330, 143), (405, 100), (420, 96), (440, 88), (440, 30), (420, 22), (394, 22)] + \
    arc(355, 30, 39, 12, 168, 10)[1:-1] + [(316, 22)]
DOOR_F = [(152, 30), (268, 30), (268, 136), (226, 137), (160, 99), (152, 96)]
DOOR_R = [(280, 30), (316, 30), (322, 66), (356, 98), (326, 136), (280, 136)]
QWIN = [(338, 131), (366, 103), (392, 103)]


def side_panel(cam, y0, t, mat="w", wins=True, dark=0):
    """car body side (x, z outline) as a thin stamped plate, outer face at y = y0 - t (faces -y)."""
    loop = [(u, v, i) for i, (u, v) in enumerate(SIDE)]
    holes = [[(u, v, 0) for u, v in h] for h in ((DOOR_F, DOOR_R, QWIN) if wins else ())]
    return compact(GE.prism(cam, (0, y0, 0), (0, -1, 0), loop, t, mat, holes=holes, dark=dark))


def press(az=24, el=20):
    def fn(sc):
        cam = sc.cam
        o = side_panel(cam, 10, 10)
        # steel coil in front (eye horizontal), wraps shown as rings on the end face
        C = (78, -120, 52)
        o += compact(GE.prism(cam, (C[0], C[1] + 36, C[2]), (0, -1, 0), GE.circle_outline(52, 48, 16, 0, 0), 72, "w",
                              holes=[GE.circle_outline(22, 32, 8)], smooth=True))
        fc = (C[0], C[1] - 36.05, C[2])
        for r in (28, 34, 40, 46):
            o += path(P(circ3(cam, fc, (0, -1, 0), r, 36)), "gr")
        o += path(P([cam.xy((C[0] + 52 * math.cos(a), C[1] - 36, C[2] + 52 * math.sin(a))) for a in (-.45, -.75)] +
                    [cam.xy((C[0] + 52 * math.cos(-.75), C[1] + 36, C[2] + 52 * math.sin(-.75)))], False), "el")
        return o
    return fit(fn, az, el, (20, 16, 300, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("plant.press")
def _():
    return press()


# =====================================================================================
# plant.body — body-in-white: two body sides (door openings, pillars, rear wheel arch), roof with
# headers, floor pan, dash panel, rear panel; front structure with side members, inner fender
# aprons, strut towers and radiator support. Bare steel, no doors / hood / fenders yet.
# =====================================================================================
def biw(az=32, el=24, Wd=88):
    def fn(sc):
        sc.add(side_panel(sc.cam, Wd, 4, dark=1), ((140, Wd - 4, 20), (440, Wd, 145)))           # far side
        sc.add(lambda s_: side_panel(s_.cam, -Wd + 4, 4), ((140, -Wd, 20), (440, -Wd + 4, 145)), -1)   # near side
        BOX(sc, 140, -Wd + 4, 20, 296, 2 * Wd - 8, 6, "w", dark=1)                               # floor pan
        BOX(sc, 140, -Wd + 4, 26, 6, 2 * Wd - 8, 70, "w", dark=1)                                # dash panel
        BOX(sc, 432, -Wd + 4, 30, 8, 2 * Wd - 8, 58, "w", dark=1)                                # rear panel
        BOX(sc, 300, -Wd + 4, 26, 30, 2 * Wd - 8, 12, "w", dark=1)                               # rear seat cross member
        Z(sc, 140, 5.5, [(222, -Wd), (334, -Wd), (334, Wd), (222, Wd)], "w")                    # roof
        BOX(sc, 146, -Wd + 4, 92, 8, 2 * Wd - 8, 6, "w", dark=1)                                 # cowl top
        for y in (-58, 46):
            BOX(sc, 0, y, 26, 140, 12, 18, "w", dark=1)                                         # front side members
        for y0 in (-Wd + 4, Wd - 8):
            BOX(sc, 30, y0, 44, 110, 4, 46, "w", dark=(1 if y0 > 0 else 0))                    # inner fender aprons
        for y in (-70, 70):
            CYL(sc, (96, y, 60), (0, 0, 1), 16, 34, "w", -.5, seg=24)                           # strut towers
            RAW(sc, lambda s_, y=y: hole3(s_.cam, (96, y, 94.05), (0, 0, 1), 6), ((86, y - 10, 94), (106, y + 10, 94.1)), -1)
        BOX(sc, 10, -62, 30, 6, 124, 8, "w")                                                    # radiator support
        BOX(sc, 10, -62, 76, 6, 124, 8, "w")
        BOX(sc, 10, -62, 38, 6, 8, 38, "w")
        BOX(sc, 10, 54, 38, 6, 8, 38, "w")
    return fit(fn, az, el, (22, 12, 298, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("plant.body")
def _():
    return biw()


# =====================================================================================
# car model for the plant drawings: convex lofts (lower body + greenhouse) drawn face by face,
# windows / lamps / seams as surface marks, wheels as shaded discs
# =====================================================================================
def loft(cam, st, mat, dark=0, crease=30):
    """st = [(x, [(y, z), ...]), ...] (same point count, convex overall). Returns svg, vertex grid."""
    V = [[(x, y, z) for y, z in sec] for x, sec in st]
    n_ = len(V[0])
    cen = tuple(sum(p[i] for r in V for p in r) / (len(V) * n_) for i in range(3))
    faces = []

    def add(pts, key):
        def sub(p, q):
            return (p[0] - q[0], p[1] - q[1], p[2] - q[2])
        nrm = (0.0, 0.0, 0.0)
        for i in range(len(pts)):                       # Newell normal (robust for slightly degenerate quads)
            p, q = pts[i], pts[(i + 1) % len(pts)]
            nrm = (nrm[0] + (p[1] - q[1]) * (p[2] + q[2]), nrm[1] + (p[2] - q[2]) * (p[0] + q[0]), nrm[2] + (p[0] - q[0]) * (p[1] + q[1]))
        ln = math.sqrt(GE._dot(nrm, nrm))
        if ln < 1e-6:
            return
        nrm = tuple(c / ln for c in nrm)
        fc = tuple(sum(p[i] for p in pts) / len(pts) for i in range(3))
        if GE._dot(nrm, GE._v(fc, cen, -1)) < 0:
            nrm = tuple(-c for c in nrm)
        faces.append((pts, nrm, key))
    for i in range(len(V) - 1):
        for j in range(n_):
            k = (j + 1) % n_
            add([V[i][j], V[i + 1][j], V[i + 1][k], V[i][k]], (i, j))
    add(V[0], "s0")
    add(V[-1][::-1], "s1")
    o, vis = "", {}
    for pts, nrm, key in faces:
        v = GE._dot(nrm, cam.D) < 0
        vis[key] = (v, nrm)
        if v:
            o += path(P([cam.xy(p) for p in pts]), shcls(mat, nrm, dark))
    # silhouette + crease lines
    d = ""
    for i in range(len(V) - 1):
        for j in range(n_):
            k = (j + 1) % n_
            a, na = vis.get((i, j), (False, (0, 0, 1)))
            for key, e in (((i, (j - 1) % n_), (V[i][j], V[i + 1][j])), ((i + 1, j) if i + 1 < len(V) - 1 else "s1", (V[i + 1][j], V[i + 1][k]))):
                if key not in vis or (i, j) not in vis:
                    continue
                if key not in vis:
                    continue
                b, nb = vis[key]
                if a != b or (a and GE._dot(na, nb) < math.cos(math.radians(crease))):
                    d += P([cam.xy(e[0]), cam.xy(e[1])], False)
            if i == 0 and "s0" in vis:
                b, nb = vis["s0"]
                if a != b or (a and GE._dot(na, nb) < math.cos(math.radians(crease))):
                    d += P([cam.xy(V[0][j]), cam.xy(V[0][k])], False)
    return o + path(d, "el"), V


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


LOW = [(0, 72, 28, 66), (12, 84, 20, 78), (60, 88, 18, 88), (150, 88, 18, 96), (330, 88, 18, 98), (420, 85, 22, 96), (440, 76, 30, 88)]
CAB = [(150, 80, 80, 96, 97.5), (226, 82, 66, 96, 145), (330, 82, 66, 97, 143), (408, 80, 72, 96, 100)]
WX = (86, 356)


def car(cam, mat="pt", glass="gl", wheels=True, lamps=True, seams=True, open_win=False):
    """returns (back svg: far wheels, body svg, front svg: near wheels) for a hatchback, nose at x=0, near side -y."""
    def lsec(w, zb, zt):
        return [(-w, zb + 10), (-w + 7, zb), (w - 7, zb), (w, zb + 10), (w, zt - 10), (w - 10, zt), (-w + 10, zt), (-w, zt - 10)]

    def csec(wb, wt, zb, zt):
        return [(-wb, zb), (wb, zb), (wt, zt - 5), (wt - 14, zt), (-wt + 14, zt), (-wt, zt - 5)]
    lo, VL = loft(cam, [(x, lsec(w, zb, zt)) for x, w, zb, zt in LOW], mat)
    cb, VC = loft(cam, [(x, csec(wb, wt, zb, zt)) for x, wb, wt, zb, zt in CAB], mat)
    body = lo
    # wheel arches on the near side
    for wx in WX:
        pts = [(wx + 38 * math.cos(a), -88.1, 30 + 38 * math.sin(a)) for a in [math.radians(t) for t in range(-10, 191, 12)]]
        body += poly3(cam, pts, "bg")
    if seams:
        d = ""
        for x in (152, 270, 362):
            d += P([cam.xy((x, -88.1, 26)), cam.xy((x, -88.1, 94))], False)
        d += P([cam.xy((152, -88.1, 26)), cam.xy((362, -88.1, 26))], False)
        d += P([cam.xy((40, -60, 86.5)), cam.xy((150, -60, 95.5))], False)
        body += path(d, "gr")
        for x in (232, 336):
            body += poly3(cam, [(x, -88.2, 84), (x + 16, -88.2, 84), (x + 16, -88.2, 87), (x, -88.2, 87)], "bg")
    if lamps:
        for sg in (-1, 1):
            body += poly3(cam, [(3, sg * 46, 70), (9, sg * 78, 74), (12, sg * 82, 70), (3, sg * 66, 62)] if sg < 0 else
                          [(3, 46, 70), (9, 78, 74), (12, 82, 70), (3, 66, 62)], "gl2")
        body += poly3(cam, [(.6, -34, 54), (.6, 34, 54), (.6, 30, 40), (.6, -30, 40)], "bg")
        body += poly3(cam, [(-.1, -20, 32), (-.1, 20, 32), (-.1, 20, 26), (-.1, -20, 26)], "bg")
    body += cb

    def Q(i, j0, j1, u, v):
        return lerp(lerp(VC[i][j0], VC[i + 1][j0], u), lerp(VC[i][j1], VC[i + 1][j1], u), v)
    wc = "bg" if open_win else glass
    # side glass (near side: section edge 5 -> 0), windshield, backlight
    wins = [[Q(1, 0, 5, u, v) for u, v in ((.03, .1), (.46, .1), (.46, .9), (.03, .9))],
            [Q(1, 0, 5, u, v) for u, v in ((.54, .1), (.97, .1), (.97, .9), (.54, .9))],
            [Q(0, 0, 5, u, v) for u, v in ((.3, .1), (.95, .1), (.95, .9))],
            [Q(2, 0, 5, u, v) for u, v in ((.05, .1), (.05, .9), (.6, .1))]]
    ws = [lerp(lerp(VC[0][5], VC[1][5], .08), lerp(VC[0][2], VC[1][2], .08), t) for t in (.06, .94)]
    wt_ = [lerp(lerp(VC[0][5], VC[1][5], .93), lerp(VC[0][2], VC[1][2], .93), t) for t in (.06, .94)]
    wins.append([ws[0], ws[1], wt_[1], wt_[0]])
    for w in wins:
        body += poly3(cam, w, wc)
    if seams:
        body += path(P([cam.xy(Q(1, 0, 5, .5, 0)), cam.xy(Q(1, 0, 5, .5, 1))], False), "gr")
    back = front = ""
    if wheels:
        for wx in WX:
            back += compact(GE.prism(cam, (wx, 84, 31), (0, -1, 0), GE.circle_outline(31, 32, 8), 22, "dk", smooth=True))
            front += wheel(cam, (wx, -64, 31))
    return back, body, front


def wheel(cam, C, r=31, w=24):
    O = (C[0], C[1], C[2])
    o = compact(GE.prism(cam, O, (0, -1, 0), GE.circle_outline(r, 32, 8), w, "dk", smooth=True))
    f = (C[0], C[1] - w - .05, C[2])
    o += path(P(circ3(cam, f, (0, -1, 0), r * .64, 28)), "ms2")
    for k in range(5):
        a = 2 * math.pi * k / 5 + .3
        pts = [(f[0] + rr * math.cos(a + da), f[1], f[2] + rr * math.sin(a + da)) for rr, da in ((r * .2, -.25), (r * .55, -.42), (r * .55, .42), (r * .2, .25))]
        o += poly3(cam, pts, "ms4")
    return o + hole3(cam, f, (0, -1, 0), r * .14, "m", 12)


# =====================================================================================
# plant.paint — painted body: doors and hood hung, glossy paint, window openings still empty (glass
# comes in assembly), carried on a conveyor skid
# =====================================================================================
def paint(az=32, el=22, mat="cu"):
    def fn(sc):
        cam = sc.cam
        o = ""
        for y in (52, -64):                                                               # skid runners
            o += compact(GE.prism(cam, (-10, y, -8), (1, 0, 0), [(0, 0, 0), (12, 0, 1), (12, 12, 2), (0, 12, 3)], 470, "dk"))
            if y < 0:
                for x in (60, 380):
                    o += compact(GE.prism(cam, (x, y + 6, 4), (0, 0, 1), GE.circle_outline(5, 12, 4), 14, "m", smooth=True))
        back, body, front = car(cam, mat, wheels=False, lamps=False, open_win=True)
        o += body
        return o
    return fit(fn, az, el, (20, 16, 300, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("plant.paint")
def _():
    return paint()


# =====================================================================================
# plant.assembly — "marriage": the trimmed body (glass fitted) is lowered onto the chassis module —
# engine and transmission, front sub-frame, rear axle, fuel tank, exhaust and the four wheels
# =====================================================================================
def assembly(az=32, el=22, mat="cu", lift=62):
    def fn(sc):
        cam = sc.cam
        o = ""
        for wx in WX:
            o += compact(GE.prism(cam, (wx, 84, 31), (0, -1, 0), GE.circle_outline(31, 32, 8), 22, "dk", smooth=True))
        Sc = __import__("il_mt").Scene
        s2 = Sc(0, 0, cam_az, cam_el, 1.0)
        s2.cam = cam
        BOX(s2, 50, -62, 22, 72, 124, 18, "m", dark=1)                                      # front sub-frame
        BOX(s2, 340, -62, 22, 32, 124, 16, "m", dark=1)                                     # rear axle beam
        BOX(s2, 34, -50, 40, 90, 70, 62, "w", ch=6)                                         # engine
        BOX(s2, 124, -26, 34, 60, 52, 46, "w", dark=1, ch=6)                                # transmission
        CYL(s2, (184, -10, 52), (1, 0, 0), 5, 150, "m", seg=10, bands=4)                    # propeller / exhaust
        BOX(s2, 270, -64, 30, 60, 100, 22, "dk", ch=6)                                      # fuel tank
        o += s2.render(shadow_=False)[0]
        for wx in WX:
            o += wheel(cam, (wx, -64, 31))
        cam.oy -= lift * cam.s * cam.ce
        back, body, front = car(cam, mat, wheels=False)
        cam.oy += lift * cam.s * cam.ce
        return o + body
    cam_az, cam_el = az, el
    return fit(fn, az, el, (24, 10, 296, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("plant.assembly")
def _():
    return assembly()


# =====================================================================================
# plant.inspection — the finished car on the chassis-dynamometer / brake tester: wheels sit between
# pairs of rollers set into the floor pit
# =====================================================================================
def inspection(az=32, el=24, mat="cu"):
    def fn(sc):
        cam = sc.cam
        o = compact(GE.prism(cam, (0, 0, -14), (0, 0, 1), [(-y, x, i) for i, (x, y) in enumerate(((-30, -130), (480, -130), (480, 130), (-30, 130)))], 14, "m", dark=1))
        for wx in WX:
            o += poly3(cam, [(wx - 44, -104, .05), (wx + 44, -104, .05), (wx + 44, 104, .05), (wx - 44, 104, .05)], "bg")
            for dx in (-21, 21):
                o += compact(GE.prism(cam, (wx + dx, 100, -11), (0, -1, 0), GE.circle_outline(13, 24, 6), 200, "m", smooth=True))
        d = ""
        for y in (-116, 116):
            d += P([cam.xy((-30, y, .05)), cam.xy((480, y, .05))], False)
        o += path(d, "gr")
        cam.oy += 6 * cam.s * cam.ce
        back, body, front = car(cam, mat)
        cam.oy -= 6 * cam.s * cam.ce
        return o + back + body + front
    return fit(fn, az, el, (18, 14, 302, 182), sh=False)


@part("plant.inspection")
def _():
    return inspection()

