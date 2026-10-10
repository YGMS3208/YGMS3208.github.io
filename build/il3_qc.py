"""v3 principle drawings (shaded 3D) for press / sheet metal, heat treatment, surface treatment
and painting equipment. Overrides the older flat drawings with the same keys."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


# ------------------------------------------------------------------ local helpers
def Y(sc, y0, L, xz, mat="pt", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded from y0 toward the viewer (-y) by L (front cap at y0-L)."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, -1, 0), loop, L, mat, **kw)),
           ((min(xs), y0 - L, min(zs)), (max(xs), y0, max(zs))), bias)


def R(x0, z0, x1, z1):
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def shell(sc, x0, x1, y0, y1, z0, z1, t=8, mat="pt", roof=True, ends=(1, 1), dark=1):
    """cut-away chamber: the front wall (y0 side) is removed, wall sections at y0 are hatched."""
    L = y1 - y0
    kw = dict(cap_mat="cut", dark=dark)
    Y(sc, y1, L, R(x0, z0, x1, z0 + t), mat, **kw)                         # floor
    BOX(sc, x0 + (t if ends[0] else 0), y1 - t, z0 + t, x1 - x0 - (t if ends[0] else 0) - (t if ends[1] else 0),
        t, z1 - z0 - 2 * t, mat, dark=dark)                                # back wall
    if roof:
        Y(sc, y1, L, R(x0, z1 - t, x1, z1), mat, **kw)
    if ends[0]:
        Y(sc, y1, L, R(x0, z0 + t, x0 + t, z1 - t), mat, **kw)
    if ends[1]:
        Y(sc, y1, L, R(x1 - t, z0 + t, x1, z1 - t), mat, **kw)


def tank(sc, x0, x1, y0, y1, z0, z1, lev, t=5, mat="pt", liq="fl", lb=-1):
    """open-top tank cut at the front, filled with (translucent) liquid up to lev; lb<-1 draws the
    liquid over parts dipped in it."""
    shell(sc, x0, x1, y0, y1, z0, z1 + t, t, mat, roof=False)
    Y(sc, y1 - t, y1 - t - y0, R(x0 + t, z0 + t, x1 - t, lev), liq, lb)


def RNG(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=36, **kw):
    """ring with a cheap smooth bore (few strips) instead of il3_lib.RING's per-segment bore."""
    CYL(sc, O, A, ro, h, mat, bias, seg, holes=[GE.circle_outline(ri, seg, 6)], **kw)


def cutq(cam, pts_):
    return path(P([cam.xy(p) for p in pts_]), "cut")


def rbox(x0, z0, x1, z1, r, seg=4):
    """rounded rectangle outline (x, z)."""
    return banded(arc(x1 - r, z1 - r, r, 0, 90, seg) + arc(x0 + r, z1 - r, r, 90, 180, seg) +
                  arc(x0 + r, z0 + r, r, 180, 270, seg) + arc(x1 - r, z0 + r, r, 270, 360, seg), 1)


def gear_pts(z, ra, rf):
    p = []
    for k in range(z):
        a, w = 2 * math.pi * k / z, math.pi / z
        for da, r in ((-w * .6, rf), (-w * .32, ra), (w * .32, ra), (w * .6, rf)):
            p.append((r * math.cos(a + da), r * math.sin(a + da)))
    return p


def GEAR(sc, O, z, ra, h, mat="w", bias=0.0, bore=0.0, seg=18):
    """light-weight vertical gear: smooth cylinder side + toothed top face (keeps files small)."""
    cam = sc.cam

    def f(s_):
        o = compact(GE.prism(s_.cam, O, (0, 0, 1), GE.circle_outline(ra * .95, seg, 8), h, mat, smooth=True, caps=False))
        top = [(O[0] + x, O[1] + y, O[2] + h) for x, y in gear_pts(z, ra, ra * .82)]
        o += path(P([s_.cam.xy(q) for q in top]), mat)
        if bore:
            o += hole3(s_.cam, (O[0], O[1], O[2] + h), (0, 0, 1), bore)
        return o
    RAW(sc, f, ((O[0] - ra, O[1] - ra, O[2]), (O[0] + ra, O[1] + ra, O[2] + h)), bias)


def gas(cam, pts_, c="a"):
    """curved flow arrow through 3D points (gas / air / liquid circulation)."""
    q = [cam.xy(p) for p in pts_]
    ang = math.atan2(q[-1][1] - q[-2][1], q[-1][0] - q[-2][0])
    d = "M%s %s" % (n(q[0][0]), n(q[0][1]))
    for i in range(1, len(q) - 1):
        mx, my = (q[i][0] + q[i + 1][0]) / 2, (q[i][1] + q[i + 1][1]) / 2
        if i == len(q) - 2:
            mx, my = q[-1][0] - 4 * math.cos(ang), q[-1][1] - 4 * math.sin(ang)
        d += " Q%s %s %s %s" % (n(q[i][0]), n(q[i][1]), n(mx), n(my))
    if len(q) == 2:
        d += " L%s %s" % (n(q[1][0] - 4 * math.cos(ang)), n(q[1][1] - 4 * math.sin(ang)))
    return path(d, c) + head(q[-1][0], q[-1][1], ang)


def down(cam, p, L=26):
    return arrow3(cam, (p[0], p[1], p[2] + L), p)


# =====================================================================================
# HEAT TREATMENT
# =====================================================================================
# q:carb — continuous gas carburizing: trays of gears pushed through a 930 C furnace with radiant
# tubes and a circulating fan, then dropped into a quench-oil tank
@picto("carb")
def _():
    xs = (22, 70, 118, 166)

    def fn(sc):
        shell(sc, 0, 200, 0, 70, 0, 84)
        for x in (46, 94, 142):                                            # radiant tubes (glowing)
            CYL(sc, (x, 54, 14), (0, 0, 1), 5, 62, "h", seg=12, bands=6)
        CYL(sc, (100, 35, 84), (0, 0, 1), 14, 10, "dk", seg=16)             # fan motor on the roof
        CYL(sc, (100, 35, 94), (0, 0, 1), 10, 14, "m", seg=16)
        Y(sc, 50, 32, R(4, 8, 196, 12), "m", -1)                           # hearth rails
        for x in xs:
            BOX(sc, x - 20, 18, 12, 40, 34, 4, "m", -1)                    # tray
            GEAR(sc, (x, 35, 16), 14, 16, 16, "h", bore=5)
        # quench oil tank with an elevator lowering a tray
        tank(sc, 212, 292, 0, 70, -46, 44, 22)
        BOX(sc, 228, 18, 52, 48, 34, 4, "m")
        GEAR(sc, (252, 35, 56), 14, 16, 16, "h", bore=5)
        BOX(sc, 248, 50, 60, 8, 8, 40, "dk")
    s, sc = fit(fn, 18, 22, (14, 30, 306, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (20, -6, -2), (180, -6, -2))
    s += down(cam, (252, 0, 46), 30)
    s += gas(cam, [(60, 6, 40), (100, 6, 62), (140, 6, 40)])
    a, b, c = cam.xy((36, 0, 84)), cam.xy((252, 0, 100)), cam.xy((100, -6, -2))
    s += lab(a[0], a[1] - 10, "浸炭 930℃") + lab(b[0] + 18, b[1] - 6, "油焼入れ")
    s += al(c[0], c[1] + 16, "トレイを順送り")
    return s


def pl3(cam, pts_):
    """polyline arrow through 3D points (sharp corners): transfer motion, flow paths."""
    q = [cam.xy(p) for p in pts_]
    ang = math.atan2(q[-1][1] - q[-2][1], q[-1][0] - q[-2][0])
    e = (q[-1][0] - 4 * math.cos(ang), q[-1][1] - 4 * math.sin(ang))
    return path(P(q[:-1] + [e], False), "a") + head(q[-1][0], q[-1][1], ang)


def bolt(sc, x, y, z, mat="w", L=16):
    """small bolt lying along y (round end toward the viewer, hex head at the back)."""
    CYL(sc, (x, y + L, z + 3.4), (0, -1, 0), 3.4, L, mat, seg=10, bands=5)
    CYL(sc, (x, y + L + 5, z + 5.2), (0, -1, 0), 5.6, 5, mat, seg=6, bands=6)


# q:contfurnace — continuous (mesh-belt) furnace: small parts ride a mesh belt through a heated
# tunnel and drop into a quench tank at the exit (also tempering / annealing / sintering / brazing)
@picto("contfurnace")
def _():
    def fn(sc):
        shell(sc, 0, 200, 0, 64, 0, 62, ends=(0, 0))
        for x0 in (0, 192):                                                # end walls above the belt
            Y(sc, 64, 64, R(x0, 30, x0 + 8, 54), "pt", cap_mat="cut", dark=1)
        for x in (36, 82, 128, 174):                                       # heaters under the roof
            CYL(sc, (x, 56, 46), (0, -1, 0), 4, 50, "h", seg=10, bands=5)
        Y(sc, 56, 46, R(-56, 14, 236, 17), "m", -1)                        # mesh belt
        for x in (-56, 236):
            CYL(sc, (x, 56, 9), (0, -1, 0), 8, 46, "dk", seg=16, bands=8)

        def mesh(s_):
            o = ""
            for k in range(25):
                x = -50 + 12 * k
                a, b = s_.cam.xy((x, 10, 17.1)), s_.cam.xy((x, 56, 17.1))
                o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            return path(o, "gline")
        RAW(sc, mesh, ((-56, 10, 17), (236, 56, 17.2)), -2)
        for i, (x, y) in enumerate(((-40, 18), (-22, 30), (20, 22), (46, 32), (72, 18), (98, 30), (124, 22), (150, 32), (176, 20), (214, 26))):
            bolt(sc, x, y, 17, "h" if 0 < x < 200 else "w")
        tank(sc, 214, 290, 0, 64, -66, 2, -14)
    s, sc = fit(fn, 18, 22, (10, 30, 310, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-50, 4, 8), (0, 4, 8))
    s += down(cam, (250, 30, 0), 26)
    a, b, c = cam.xy((100, 30, 62)), cam.xy((252, 0, 0)), cam.xy((-30, 0, 8))
    s += lab(a[0], a[1] - 12, "加熱ゾーン") + lab(b[0] + 6, b[1] - 34, "焼入れ") + lab(c[0], c[1] + 18, "メッシュベルト")
    return s


# q:vac — vacuum carburizing: a load of gears is heated by graphite elements in a low-pressure
# chamber (acetylene pulses), then moved to a chamber where high-pressure gas and a fan cool it
@picto("vac")
def _():
    zc, ro, ri = 55, 50, 44

    def half(sc, x0, x1):
        for k in range(6):
            t0, t1 = math.radians(-90 + 30 * k), math.radians(-60 + 30 * k)
            X(sc, x0, x1 - x0, [(ri * math.cos(t0), zc + ri * math.sin(t0)), (ro * math.cos(t0), zc + ro * math.sin(t0)),
                                (ro * math.cos(t1), zc + ro * math.sin(t1)), (ri * math.cos(t1), zc + ri * math.sin(t1))], "pt", dark=1)

        def cut(s_):
            o = ""
            for za, zb in ((zc + ri, zc + ro), (zc - ro, zc - ri)):
                o += path(P([s_.cam.xy(p) for p in ((x0, 0, za), (x1, 0, za), (x1, 0, zb), (x0, 0, zb))]), "cut")
            return o
        RAW(sc, cut, ((x0, -.2, zc - ro), (x1, 0, zc + ro)), -3)

    def fn(sc):
        X(sc, -8, 8, arc(0, zc, ro, -90, 90, 8), "pt", dark=1)              # dished end (left)
        half(sc, 0, 120)
        X(sc, 120, 10, arc(0, zc, ro, -90, 90, 8), "dk")                     # inner door
        half(sc, 130, 230)
        X(sc, 230, 8, arc(0, zc, ro, -90, 90, 8), "pt", dark=1)
        CYL(sc, (238, 0, zc), (1, 0, 0), 18, 22, "dk", seg=20)               # cooling fan motor
        for y, z in ((30, 88), (40, 55), (30, 22)):                         # graphite heating elements
            CYL(sc, (6, y, z), (1, 0, 0), 3, 108, "h", seg=8, bands=4)
        for x0 in (22, 150):
            BOX(sc, x0, 8, 22, 76, 34, 4, "m")
        for x in (36, 60, 84):                                              # load in the heating chamber
            GEAR(sc, (x, 25, 26), 12, 11, 12, "h", bore=4, seg=14)
        for x in (164, 188, 212):                                           # load being gas-cooled
            GEAR(sc, (x, 25, 26), 12, 11, 12, "w", bore=4, seg=14)
    s, sc = fit(fn, 16, 20, (16, 32, 304, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += pl3(cam, ((96, 0, 14), (156, 0, 14)))
    for x in (166, 210):
        s += gas(cam, [(x, 6, 92), (x + (12 if x < 190 else -12), 6, 70), (x, 6, 46)])
    a, b = cam.xy((60, 0, zc + ro)), cam.xy((180, 0, zc + ro))
    s += lab(a[0], a[1] - 8, "減圧浸炭（加熱室）") + lab(b[0], b[1] - 8, "高圧ガス冷却")
    return s


# =====================================================================================
# PRESS / SHEET METAL
# =====================================================================================
# q:progressive — progressive die: a strip from the coil advances one pitch per stroke; each station
# pierces, notches, bends and finally cuts off the part while the carrier holds the rest together
@picto("progressive")
def _():
    def fn(sc):
        BOX(sc, 10, -40, -24, 230, 80, 24, "m", dark=1)                    # lower die
        Z(sc, 0, 2.5, [(-30, -22), (250, -22), (250, 22), (-30, 22)], "w")  # strip

        def marks(s_):
            o = ""
            for x in (40, 80, 120, 160, 200, 240):
                o += hole3(s_.cam, (x, 15, 2.6), (0, 0, 1), 2.6)
            for x in (80, 120, 160):
                o += hole3(s_.cam, (x - 3 if x == 160 else x, -2, 2.6), (0, 0, 1), 5)
            for x0 in (104, 144):
                for y0 in (-15, 9):
                    o += path(P([s_.cam.xy((x, y, 2.6)) for x, y in ((x0, y0), (x0 + 32, y0), (x0 + 32, y0 + 3), (x0, y0 + 3))]), "bg")
            o += path(P([s_.cam.xy((x, y, 2.6)) for x, y in ((184, -15), (216, -15), (216, 12), (184, 12))]), "bg")
            return o
        RAW(sc, marks, ((-30, -22, 2.5), (250, 22, 2.7)), -2)
        for x in (145, 172):                                               # bent tabs
            BOX(sc, x, -12, 2.5, 3, 21, 12, "w")
        BOX(sc, 30, -30, 52, 200, 54, 10, "pt", dark=1)                     # upper die plate
        CYL(sc, (40, 15, 24), (0, 0, 1), 2.6, 28, "t", seg=10, bands=5)
        CYL(sc, (80, -2, 22), (0, 0, 1), 5, 30, "t", seg=14, bands=6)
        BOX(sc, 106, -14, 20, 28, 26, 32, "t")
        BOX(sc, 150, -12, 20, 20, 22, 32, "t")
        BOX(sc, 186, -14, 20, 28, 26, 32, "t")
        # finished part (U-shaped bracket) dropped in front of the die
        BOX(sc, 222, -78, -24, 30, 24, 3, "w")
        BOX(sc, 222, -78, -21, 3, 24, 12, "w")
        BOX(sc, 249, -78, -21, 3, 24, 12, "w")
    s, sc = fit(fn, 20, 28, (10, 30, 306, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-30, -30, 2), (8, -30, 2))
    s += arrow3(cam, (130, 0, 96), (130, 0, 68))
    a, b = cam.xy((-30, -30, 2)), cam.xy((237, -78, -24))
    s += lab(a[0] + 12, a[1] + 16, "帯板を送る") + lab(b[0], b[1] + 14, "製品")
    for x, t in ((70, "穴抜き"), (160, "曲げ")):
        p = cam.xy((x, -40, -24))
        s += lab(p[0], p[1] + 15, t)
    return s


# q:transferpress — transfer press: several dies in one press; transfer bars with fingers lift each
# part, advance it one station and set it down while the slide is up (blank -> draw -> redraw -> trim)
@picto("transferpress")
def _():
    st = (0, 100, 200)

    def fn(sc):
        BOX(sc, -140, -56, -26, 380, 112, 16, "m", dark=1)                 # bolster
        for x in st:
            BOX(sc, x - 34, -34, -10, 68, 68, 18, "t", ch=4)               # lower dies
            BOX(sc, x - 34, -34, 104, 68, 68, 16, "t", ch=4)               # upper dies
        BOX(sc, -60, -40, 120, 320, 80, 14, "pt", dark=1)                   # slide (raised)
        CYL(sc, (-100, 0, 8), (0, 0, 1), 30, 2, "w", seg=32)               # blank waiting
        CYL(sc, (0, 0, 8), (0, 0, 1), 30, 2, "w", seg=32)                  # 1: shallow draw (upside-down cup)
        CYL(sc, (0, 0, 10), (0, 0, 1), 20, 12, "w", seg=28)
        CYL(sc, (100, 0, 8), (0, 0, 1), 25, 2, "w", seg=32)                # 2: redraw
        CYL(sc, (100, 0, 10), (0, 0, 1), 15, 26, "w", seg=24)
        CYL(sc, (200, 0, 8), (0, 0, 1), 19, 2, "w", seg=28)                # 3: trimmed flange, pierced
        CYL(sc, (200, 0, 10), (0, 0, 1), 15, 26, "w", seg=24)

        def holes(s_):
            o = hole3(s_.cam, (200, 0, 36.1), (0, 0, 1), 5)
            return o
        RAW(sc, holes, ((195, -5, 36), (205, 5, 36.2)), -2)
        for y in (-60, 46):                                                # transfer bars + fingers
            BOX(sc, -150, y, -6, 400, 6, 8, "dk")
            for x in (-100, 0, 100, 200):
                BOX(sc, x - 5, (y + 6 if y < 0 else 30), -4, 10, (24 if y < 0 else 16), 5, "dk")
    s, sc = fit(fn, -18, 30, (8, 26, 312, 174), sh_ry=6, sh_k=.45, ret_scene=True)
    cam = sc.cam
    s += pl3(cam, ((0, -36, 22), (0, -36, 64), (100, -36, 64), (100, -36, 42)))
    s += arrow3(cam, (262, -40, 164), (262, -40, 134))
    a, b = cam.xy((50, -36, 64)), cam.xy((262, -40, 164))
    s += al(a[0], a[1] - 6, "持上げ→送り→下ろす")
    s += lab(b[0] - 4, b[1] - 6, "スライド", "end")
    for x, t in ((0, "絞り"), (100, "再絞り"), (200, "トリム")):
        p = cam.xy((x, -56, -26))
        s += lab(p[0], p[1] + 16, t)
    return s


# q:drawpress — drawing die in the press (cut model): the upper die comes down, clamps the blank on
# the blank holder and pushes it over the punch; the flange flows in to make a deep panel
@picto("drawpress")
def _():
    L = 120

    def top(x0, x1, z0, z1, r):                                            # block with rounded top edges
        return hull([(x0, z0), (x1, z0)] + arc(x1 - r, z1 - r, r, 0, 90, 4) + arc(x0 + r, z1 - r, r, 90, 180, 4))

    def fn(sc):
        kw = dict(cap_mat="cut")
        F = lambda pts_, mat, **k: Y(sc, L, L, pts_, mat, **k)
        F([(-96, -14), (96, -14), (96, 0), (-96, 0)], "m", dark=1)          # bolster
        F(top(-34, 34, 0, 44, 10), "t", **kw)                               # punch
        F([(-92, 0), (-40, 0), (-40, 18), (-92, 18)], "m", **kw)            # blank holder (binder)
        F([(40, 0), (92, 0), (92, 18), (40, 18)], "m", **kw)
        t = 3                                                               # sheet: flange -> wall -> nose
        F([(-92, 18), (-46, 18), (-46, 18 + t), (-92, 18 + t)], "w")
        F([(-46, 18), (-37, 22), (-37, 44 + t), (-46, 18 + t)], "w")
        F([(46, 18), (92, 18), (92, 18 + t), (46, 18 + t)], "w")
        F([(37, 22), (46, 18), (46, 18 + t), (37, 44 + t)], "w")
        F([(-37, 38), (-26, 44), (26, 44), (37, 38), (37, 44 + t), (-37, 44 + t)], "w")
        F([(-92, 18 + t), (-50, 18 + t), (-42, 26), (-42, 76), (-92, 76)], "t", **kw)   # upper die
        F([(50, 18 + t), (92, 18 + t), (92, 76), (42, 76), (42, 26)], "t", **kw)
        F([(-42, 62), (42, 62), (42, 76), (-42, 76)], "t", **kw)
        F([(-96, 76), (96, 76), (96, 92), (-96, 92)], "pt", dark=1)        # slide
    s, sc = fit(fn, -22, 22, (40, 30, 280, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, L * .5, 134), (0, L * .5, 100))
    s += arrow3(cam, (-90, -1, 30), (-60, -1, 30)) + arrow3(cam, (90, -1, 30), (60, -1, 30))
    a, b, c, d = cam.xy((-96, 0, 84)), cam.xy((-96, 0, 9)), cam.xy((0, 0, 20)), cam.xy((0, L * .5, 134))
    e = cam.xy((96, 0, 30))
    s += lab(a[0] - 6, a[1] + 4, "ダイ", "end") + lab(b[0] - 6, b[1] + 4, "しわ押さえ", "end")
    s += al(d[0] + 8, d[1] + 4, "下降", "start") + al(e[0] + 6, e[1] + 4, "材料流入", "start")
    s += lab(c[0], c[1] + 4, "パンチ")
    return s


# q:blankline — blanking line: uncoiler -> leveler (staggered rolls flatten the strip) -> blanking
# press -> stacked blanks
@picto("blankline")
def _():
    def fn(sc):
        RING(sc, (0, 26, 52), (0, -1, 0), 42, 14, 52, "w", seg=40)           # coil on the mandrel
        CYL(sc, (0, 40, 52), (0, -1, 0), 14, 14, "dk", seg=20)

        def turns(s_):
            o = ""
            for r in (22, 30, 37):
                o += P(circ3(s_.cam, (0, -26.1, 52), (0, -1, 0), r, 28))
            return path(o, "gline")
        RAW(sc, turns, ((-42, -26.2, 10), (42, -26, 94)), -2)
        Z(sc, 7, 3, [(0, -22), (236, -22), (236, 22), (0, 22)], "w")         # strip
        for i, x in enumerate(range(72, 136, 12)):                          # leveler rolls
            z = 16 if i % 2 == 0 else 1
            CYL(sc, (x, 26, z), (0, -1, 0), 6, 52, "m", seg=14, bands=7)
        BOX(sc, 62, 26, -6, 84, 10, 40, "pt", dark=1)                       # leveler frame (rear)
        BOX(sc, 176, -34, -16, 64, 68, 23, "t", ch=3)                       # lower die
        BOX(sc, 176, -34, 34, 64, 68, 24, "t", ch=3)                        # upper die
        BOX(sc, 168, -40, 58, 80, 80, 14, "pt", dark=1)                     # slide
        for k in range(5):                                                  # stacked blanks
            Z(sc, -16 + 3.2 * k, 3, [(262, -22), (306, -22), (314, 22), (256, 22)], "w")
    s, sc = fit(fn, 18, 26, (8, 24, 312, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -30, 52), (0, -1, 0), 48, 120, 210)
    s += arrow3(cam, (150, -30, 10), (176, -30, 10))
    s += arrow3(cam, (208, 0, 96), (208, 0, 74))
    for p, t, dy in (((0, 0, -4), "コイル", 22), ((104, 0, -6), "レベラ", 22), ((208, 0, 96), "プレス", -8), ((285, 0, -16), "ブランク", 22)):
        q = cam.xy(p)
        s += lab(q[0], q[1] + dy, t)
    return s


# q:fineblank — fine blanking (cut model): the V-ring holder and the counter punch clamp the strip,
# then the punch shears the part with a fully smooth (burnished) edge
@picto("fineblank")
def _():
    L = 90

    def fn(sc):
        kw = dict(cap_mat="cut")
        F = lambda pts_, mat, **k: Y(sc, L, L, pts_, mat, **k)
        F(R(-96, -12, 96, 0), "m", dark=1)
        F(R(-92, 0, -32, 40), "m", **kw)                                    # die
        F(R(32, 0, 92, 40), "m", **kw)
        F(R(-14, -12, 14, 26), "dk", **kw)                                  # counter-punch rod
        F(R(-31, 26, 31, 34), "t", **kw)                                    # counter punch
        F(R(-92, 40, -32, 50), "w")                                         # strip (scrap web)
        F(R(32, 40, 92, 50), "w")
        F(R(-31, 34, 31, 44), "w")                                          # part being sheared
        F(R(-31, 44, 31, 100), "t", **kw)                                   # punch
        F(R(-92, 50, -33, 80), "m", **kw)                                   # V-ring plate (blank holder)
        F(R(33, 50, 92, 80), "m", **kw)

        def vring(s_):
            o = ""
            for x in (-48, 48):
                o += path(P([s_.cam.xy((x + dx, -.1, z)) for dx, z in ((-7, 50.4), (7, 50.4), (0, 43))]), "m")
            return o
        RAW(sc, vring, ((-55, -.2, 43), (55, 0, 50.4)), -3)
    s, sc = fit(fn, -20, 20, (96, 30, 262, 170), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, L * .5, 134), (0, L * .5, 104))
    s += arrow3(cam, (62, L * .5, 108), (62, L * .5, 84))
    s += arrow3(cam, (0, -2, -40), (0, -2, -16))
    a, b, c, d = cam.xy((-92, 0, 64)), cam.xy((-92, 0, 20)), cam.xy((0, -2, -40)), cam.xy((0, L * .5, 134))
    e = cam.xy((-92, 0, 45))
    s += lab(a[0] - 6, a[1] + 4, "Vリング押さえ", "end") + lab(b[0] - 6, b[1] + 4, "ダイ", "end")
    s += lab(e[0] - 6, e[1] + 4, "板材", "end")
    s += lab(c[0] + 10, c[1] + 6, "逆押さえ", "start") + lab(d[0] - 10, d[1] + 4, "パンチ", "end")
    return s


# q:hotstamp — hot stamping: the blank is heated to ~900 C in a roller-hearth furnace, carried to the
# press and formed and quenched at once between water-cooled dies
@picto("hotstamp")
def _():
    L = 70

    def fn(sc):
        shell(sc, 0, 124, 0, 70, 0, 56, ends=(1, 0))
        for x in range(14, 124, 14):
            CYL(sc, (x, 64, 12), (0, -1, 0), 4, 58, "m", seg=10, bands=5)   # hearth rollers
        Z(sc, 16, 2.5, [(26, 14), (104, 14), (104, 54), (26, 54)], "h")     # glowing blank
        kw = dict(cap_mat="cut")
        F = lambda pts_, mat, **k: Y(sc, L, L, pts_, mat, **k)
        F(R(160, -6, 280, 12), "t", **kw)                                   # lower die
        F(hull([(186, 12), (254, 12)] + arc(246, 30, 8, 0, 90, 3) + arc(194, 30, 8, 90, 180, 3)), "t", **kw)
        F(R(160, 12, 182, 15), "h")                                         # hot blank formed over the punch
        F(R(258, 12, 280, 15), "h")
        F([(182, 12), (186, 12), (186, 41), (182, 38)], "h")
        F([(254, 12), (258, 12), (258, 38), (254, 41)], "h")
        F(R(186, 38, 254, 41), "h")
        F(R(160, 52, 180, 92), "t", **kw)                                   # upper die (raised)
        F(R(260, 52, 280, 92), "t", **kw)
        F(R(180, 72, 260, 92), "t", **kw)

        def water(s_):
            o = ""
            for x, z in ((170, 2), (220, 2), (270, 2), (220, 24), (170, 80), (270, 80), (200, 82), (240, 82)):
                o += hole3(s_.cam, (x, -.1, z), (0, -1, 0), 3.4, "fl")
            return o
        RAW(sc, water, ((160, -.2, -6), (280, 0, 92)), -3)
    s, sc = fit(fn, -18, 22, (10, 28, 310, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += pl3(cam, ((100, 0, 64), (140, 0, 64), (176, 0, 48)))
    s += arrow3(cam, (220, L * .5, 126), (220, L * .5, 100))
    a, b, c = cam.xy((62, 0, 56)), cam.xy((220, 0, -6)), cam.xy((220, L * .5, 126))
    s += lab(a[0], a[1] - 10, "加熱炉 約900℃") + lab(b[0], b[1] + 18, "水冷金型")
    s += al(c[0] + 8, c[1] + 4, "成形＋焼入れ", "start")
    return s


# q:hem — roller hemming: a roller on a robot folds the outer panel's flange over the inner panel in
# passes (90 deg -> 45 deg -> flat)
@picto("hem")
def _():
    def fn(sc):
        Y(sc, 120, 120, R(-44, -20, 34, 0), "m", dark=1)                    # anvil (hemming bed)
        Y(sc, 120, 120, R(-37, 0, 34, 3), "w")                              # outer panel
        Y(sc, 120, 120, R(-30, 3, 34, 7), "w", dark=1)                      # inner panel
        Y(sc, 120, 44, R(-40, 0, -37, 28), "w")                             # flange still upright
        Y(sc, 76, 38, [(-40, 0), (-37, 0), (-20, 19), (-24, 22)], "w")      # pre-hem 45 deg
        Y(sc, 38, 38, R(-40, 0, -37, 10), "w")                              # final hem: bend + flat flange
        Y(sc, 38, 38, R(-37, 7, -16, 10), "w")
        CYL(sc, (-48, 44, 22), (1, 0, 0), 12, 24, "t", seg=24)              # hemming roller
        CYL(sc, (-24, 44, 22), (1, 0, 0), 3, 22, "m", seg=10, bands=5)      # axle
        BOX(sc, -2, 36, 12, 12, 16, 34, "dk", ch=2)                         # arm to the robot wrist
        BOX(sc, -2, 30, 46, 40, 28, 14, "dk", ch=2)
    s, sc = fit(fn, 32, 26, (44, 26, 276, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-36, 64, 52), (-36, 20, 52))
    s += arc3(cam, (-50, 44, 22), (1, 0, 0), 17, 110, 200)
    for y, t in ((100, "90°"), (58, "45°"), (8, "ヘム")):
        q = cam.xy((-40, y, 6))
        s += lab(q[0] - 8, q[1] + 4, t, "end")
    a, b = cam.xy((-62, 44, 22)), cam.xy((34, 0, -20))
    s += lab(b[0], b[1] + 16, "アウター＋インナー", "end")
    return s


# q:powder — powder compaction press (cut model): the feed shoe fills the die with metal powder,
# upper and lower punches squeeze it into a green compact, which is then ejected
@picto("powder")
def _():
    L = 70

    def fn(sc):
        kw = dict(cap_mat="cut")
        F = lambda pts_, mat, **k: Y(sc, L, L, pts_, mat, **k)
        F(R(-84, 0, -30, 56), "m", **kw)                                    # die
        F(R(30, 0, 84, 56), "m", **kw)
        F(R(-29, -36, 29, 18), "t", **kw)                                   # lower punch
        F(R(-29, 18, 29, 40), "w", **kw)                                    # compact being pressed
        F(R(-29, 40, 29, 100), "t", **kw)                                   # upper punch
        BOX(sc, 84, 4, 56, 40, 50, 16, "pt", dark=1)                        # feed shoe
        CYL(sc, (104, 29, 72), (0, 0, 1), 8, 30, "m", seg=14, bands=7)      # powder hose
        GEAR(sc, (160, 34, 0), 16, 20, 18, "w", bore=7)                     # ejected green compact

        def pwd(s_):
            o = ""
            for i in range(26):
                x, z = -26 + (i * 37) % 53, 21 + (i * 11) % 16
                q = s_.cam.xy((x, -.1, z))
                o += circ(q[0], q[1], 1, "pwd")
            return o
        RAW(sc, pwd, ((-29, -.2, 18), (29, 0, 40)), -3)
    s, sc = fit(fn, -20, 22, (40, 26, 290, 172), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, L * .5, 136), (0, L * .5, 106))
    s += arrow3(cam, (0, -2, -70), (0, -2, -42))
    a, b, c, d = cam.xy((-29, 0, 80)), cam.xy((-84, 0, 28)), cam.xy((29, 0, -30)), cam.xy((160, 0, 0))
    s += lab(a[0] - 6, a[1], "上パンチ", "end") + lab(b[0] - 6, b[1] + 4, "金型", "end")
    s += lab(c[0] + 8, c[1] + 4, "下パンチ", "start") + lab(d[0], d[1] + 18, "圧粉体")
    return s


# q:induction — induction hardening: a copper coil fed with high-frequency current heats only the
# surface of the rotating journal, which is then quenched by a water spray
@picto("induction")
def _():
    def fn(sc):
        for x0, x1, r in ((0, 30, 12), (30, 64, 18), (64, 190, 22), (190, 220, 15)):
            CYL(sc, (x0, 0, 0), (1, 0, 0), r, x1 - x0, "w", seg=32)
        CYL(sc, (84, 0, 0), (1, 0, 0), 22.6, 60, "h", seg=32, bias=-1)       # glowing surface layer
        RING(sc, (104, 0, 0), (1, 0, 0), 34, 26, 20, "cu", seg=36, bias=-2)  # coil
        BOX(sc, 106, -5, 32, 6, 10, 40, "cu")                               # leads
        BOX(sc, 116, -5, 32, 6, 10, 40, "cu")
        BOX(sc, 92, -24, 72, 48, 48, 26, "dk", ch=3)                        # HF transformer
        CYL(sc, (150, 0, 44), (0, 0, 1), 5, 4, "m", seg=12)
        CYL(sc, (150, 0, 34), (0, 0, 1), 4, 12, "m", seg=12)                # quench nozzle
    s, sc = fit(fn, 20, 20, (20, 26, 300, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (30, 0, 0), (1, 0, 0), 26, 20, 150)
    q = cam.xy((150, 0, 30))
    s += drops(q[0], q[1], 5, 34, 14, 90)
    a, b, c, d = cam.xy((116, 0, 98)), cam.xy((114, 0, -34)), cam.xy((150, 0, 48)), cam.xy((30, 0, 26))
    s += lab(a[0], a[1] - 6, "高周波電源") + lab(b[0], b[1] + 16, "コイル（加熱部）")
    s += lab(c[0] + 10, c[1] - 4, "冷却水", "start") + al(d[0] - 6, d[1] - 6, "回転", "end")
    return s


# q:solution — T6 heat treatment of aluminium castings: solution treatment (~500 C) -> water quench
# -> artificial ageing (~200 C)
@picto("solution")
def _():
    def casting(sc, x, y, z, mat="alu"):
        BOX(sc, x, y, z, 34, 22, 16, mat, ch=3)

        def f(s_):
            return "".join(hole3(s_.cam, (x + 8 + 9 * k, y + 11, z + 16.1), (0, 0, 1), 3.2) for k in range(3))
        RAW(sc, f, ((x, y, z + 16), (x + 34, y + 22, z + 16.2)), -2)

    def fn(sc):
        shell(sc, 0, 104, 0, 60, 0, 70)
        BOX(sc, 12, 12, 8, 80, 40, 4, "m")
        casting(sc, 14, 22, 12)
        casting(sc, 56, 22, 12)
        tank(sc, 116, 186, 0, 60, -40, 30, 18, lb=-6)
        BOX(sc, 126, 12, -8, 50, 40, 4, "m")
        casting(sc, 134, 22, -4)
        shell(sc, 198, 290, 0, 60, 0, 60)
        BOX(sc, 208, 12, 8, 72, 40, 4, "m")
        casting(sc, 212, 22, 12)
        casting(sc, 246, 22, 12)
    s, sc = fit(fn, 16, 22, (10, 34, 310, 166), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x0, y0 in ((30, 44), (238, 40)):
        q = cam.xy((x0, 30, y0))
        s += heat(q[0], q[1], 4, 10)
    s += pl3(cam, ((96, -4, 74), (150, -4, 74), (150, -4, 40)))
    s += pl3(cam, ((168, -4, 40), (168, -4, 64), (214, -4, 64)))
    for x, z, t in ((52, 70, "溶体化 約500℃"), (151, 30, "水冷"), (244, 60, "時効 約200℃")):
        q = cam.xy((x, 0, z if x != 151 else -40))
        s += lab(q[0], q[1] + (-14 if x != 151 else 18), t)
    return s


# q:pressquench — press quenching: the red-hot ring gear is clamped between dies (expander in the
# bore, pressure ring on the face) while quench oil flows through, so it cannot warp
@picto("pressquench")
def _():
    def fn(sc):
        CYL(sc, (0, 0, -34), (0, 0, 1), 86, 12, "dk", seg=36)               # base
        RNG(sc, (0, 0, -22), (0, 0, 1), 72, 34, 22, "m", seg=36)          # lower die
        RNG(sc, (0, 0, 0), (0, 0, 1), 64, 42, 16, "h", seg=36)            # hot ring gear

        def teeth(s_):
            o = ""
            for k in range(36):
                a = 2 * math.pi * k / 36
                c, si = math.cos(a), math.sin(a)
                if s_.cam.P((60 * c, 60 * si, 16))[2] > s_.cam.P((0, 0, 16))[2] + 40:
                    continue
                p, q = s_.cam.xy((46 * c, 46 * si, 16.1)), s_.cam.xy((63 * c, 63 * si, 16.1))
                o += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1]))
            return path(o, "hl")
        RAW(sc, teeth, ((-64, -64, 16), (64, 64, 16.2)), -2)
        CYL(sc, (0, 0, 36), (0, 0, 1), 41, 30, "t", seg=40, r1=30)          # expander cone (bore)
        RNG(sc, (0, 0, 40), (0, 0, 1), 66, 46, 12, "t", seg=36)            # pressure ring (face)
        CYL(sc, (0, 0, 66), (0, 0, 1), 84, 14, "pt", seg=36, dark=1)        # upper platen
    s, sc = fit(fn, -24, 30, (40, 26, 280, 168), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, 0, 118), (0, 0, 88))
    for x in (-80, 80):
        q = cam.xy((x, -40, -6))
        s += drops(q[0], q[1], 4, 30, 16, 90 + (25 if x < 0 else -25))
    a, b, c = cam.xy((0, 0, 118)), cam.xy((0, -86, -34)), cam.xy((-80, -40, -6))
    s += al(a[0] + 8, a[1] + 4, "金型で拘束", "start") + lab(b[0] + 30, b[1] + 22, "赤熱リングギヤ", "start")
    s += lab(c[0] - 8, c[1] + 34, "焼入れ油", "end")
    return s


# q:cooling — controlled cooling after forging: hot crankshafts ride a conveyor under blowers; the
# air blast sets the cooling rate so non-heat-treated (micro-alloyed) steel gets its strength
@picto("cooling")
def _():
    def crank(sc, x, mat):
        zc = 22
        segs = [("j", 76, 86), ("w", 70, 76, 1), ("p", 60, 70, 1), ("w", 54, 60, 1), ("j", 44, 54), ("w", 38, 44, -1),
                ("p", 28, 38, -1), ("w", 22, 28, -1), ("j", 12, 22)]
        for sg in segs:
            k, y0, y1 = sg[0], sg[1], sg[2]
            if k == "j":
                CYL(sc, (x, y1, zc), (0, -1, 0), 7, y1 - y0, mat, seg=12, bands=4)
            elif k == "p":
                CYL(sc, (x, y1, zc + 13 * sg[3]), (0, -1, 0), 6, y1 - y0, mat, seg=12, bands=4)
            else:
                zz = zc + 13 * sg[3]
                Y(sc, y1, y1 - y0, banded(hull(arc(x, zz, 9, 0, 360, 6) + arc(x, zc - 4 * sg[3], 13, 0, 360, 6)), 3), mat, dark=1)

    def fn(sc):
        BOX(sc, -20, 0, 0, 300, 96, 6, "m", dark=1)                          # conveyor deck
        for y in (-6, 96):
            BOX(sc, -20, y, -4, 300, 6, 12, "dk")
        for x, m in ((20, "h"), (110, "h"), (220, "w")):
            crank(sc, x, m)
        for x in (65, 165):                                                  # blowers
            CYL(sc, (x, 48, 92), (0, 0, 1), 30, 14, "pt", seg=24, dark=1, bands=8)
    s, sc = fit(fn, -34, 30, (14, 30, 306, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (65, 165):
        for dx in (-16, 16):
            s += arrow3(cam, (x + dx, 30, 84), (x + dx, 30, 52))
    s += arrow3(cam, (200, -14, 6), (270, -14, 6))
    a, b, c = cam.xy((115, 48, 106)), cam.xy((40, -6, -4)), cam.xy((236, -14, 6))
    s += al(a[0], a[1] - 4, "衝風で冷却速度を制御") + lab(b[0], b[1] + 18, "鍛造直後のクランク")
    s += lab(c[0], c[1] + 18, "コンベヤ")
    return s


# q:resheat — direct resistance heating of a stabilizer bar: current from a transformer flows through
# the bar between two clamping electrodes and heats it uniformly before quenching
@picto("resheat")
def _():
    r = 7

    def fn(sc):
        CYL(sc, (20, 0, 0), (1, 0, 0), r, 200, "h", seg=20)                 # straight centre
        for sgn, x in ((-1, 20), (1, 220)):
            d = GE._norm((sgn, -1, 0))
            CYL(sc, (x, 0, 0), d, r, 22, "h", seg=20)                       # bend
            e = (x + sgn * 15.6, -15.6, 0)
            CYL(sc, e, (0, -1, 0), r, 64, "h", seg=20)                      # arm
            BOX(sc, e[0] - 13, -86, -14, 26, 14, 28, "cu", ch=2)             # electrode clamp
        BOX(sc, 84, 40, -30, 72, 46, 44, "dk", ch=3)                         # transformer
    s, sc = fit(fn, -20, 26, (24, 24, 296, 160), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    o = ""
    for x in (4.4, 235.6):
        a, b = cam.xy((x, -80, 14)), cam.xy((120 + (x - 120) * .3, 40, 14))
        o += "M%s %sC%s %s %s %s %s %s" % (n(a[0]), n(a[1]), n(a[0]), n(a[1] - 40), n(b[0]), n(b[1] - 30), n(b[0]), n(b[1]))
    s = path(o, "cable") + s
    s += arrow3(cam, (60, -12, 14), (180, -12, 14))
    a, b, c = cam.xy((4.4, -86, -14)), cam.xy((120, 63, 14)), cam.xy((120, -12, -8))
    s += lab(a[0], a[1] + 18, "電極") + lab(b[0], b[1] - 16, "変圧器")
    s += al(c[0], c[1] + 18, "電流で直接加熱")
    return s


# =====================================================================================
# SURFACE TREATMENT / CLEANING
# =====================================================================================
# q:wash — parts washer (cut model): the work turns on a table under shower / high-pressure
# nozzles; the wash liquid drains to a tank below and is filtered and re-used
@picto("wash")
def _():
    def fn(sc):
        shell(sc, 0, 200, 0, 90, 0, 124)
        tank(sc, 10, 190, 0, 90, -56, -14, -24)
        CYL(sc, (100, 46, 8), (0, 0, 1), 44, 8, "m", seg=36)                 # turn table
        BOX(sc, 68, 24, 16, 64, 44, 46, "w", ch=4)                           # work (engine block)

        def bores(s_):
            return "".join(hole3(s_.cam, (82 + 18 * k, 46, 62.1), (0, 0, 1), 7) for k in range(3))
        RAW(sc, bores, ((68, 24, 62), (132, 68, 62.2)), -2)
        CYL(sc, (14, 40, 104), (1, 0, 0), 4, 172, "m", seg=12, bands=6)      # shower header
        CYL(sc, (24, 40, 20), (0, 0, 1), 4, 84, "m", seg=12, bands=6)        # side header
        for x in (60, 100, 140):
            CYL(sc, (x, 40, 94), (0, 0, 1), 3, 10, "dk", seg=8, bands=4)
        for z in (36, 56):
            CYL(sc, (28, 40, z), (1, 0, 0), 3, 8, "dk", seg=8, bands=4)
    s, sc = fit(fn, 18, 22, (40, 22, 280, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    for x in (60, 100, 140):
        q = cam.xy((x, 40, 94))
        s += spray_cone(q[0], q[1], 90, 34, 30 * sc.k * 1.0)
    for z in (36, 56):
        q = cam.xy((36, 40, z))
        s += spray_cone(q[0], q[1], -4, 30, 30 * sc.k)
    s += arc3(cam, (100, 46, 12), (0, 0, 1), 54, 60, 150)
    a, b, c = cam.xy((100, 40, 124)), cam.xy((100, 0, -56)), cam.xy((200, 0, 60))
    s += lab(a[0], a[1] - 10, "シャワー・高圧ノズル") + lab(b[0], b[1] + 16, "洗浄液タンク")
    s += lab(c[0] + 8, c[1], "ワーク", "start")
    return s


# q:plating — electroplating: parts hang from the cathode bar in the plating bath; the rectifier
# drives current from the anodes through the solution, depositing metal on the parts
@picto("plating")
def _():
    def fn(sc):
        tank(sc, 0, 220, 0, 80, 0, 92, 76, lb=-6)
        for x in (12, 196):
            BOX(sc, x, 16, 14, 12, 50, 84, "dk", ch=2)                        # anodes
        CYL(sc, (-10, 40, 122), (1, 0, 0), 5, 236, "cu", seg=14, bands=7)     # cathode bus bar
        for x in (70, 110, 150):
            BOX(sc, x - 1.5, 38.5, 92, 3, 3, 28, "dk")
            CYL(sc, (x, 40, 22), (0, 0, 1), 7, 70, "w", seg=20)               # parts (e.g. piston rods)
        BOX(sc, 240, 20, 0, 54, 44, 52, "dk", ch=3)                           # rectifier
    s, sc = fit(fn, 18, 22, (20, 26, 300, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x0, x1 in ((28, 60), (194, 160)):
        s += arrow3(cam, (x0, 0, 46), (x1, 0, 46))
    a, b, c, d = cam.xy((18, 40, 128)), cam.xy((110, 40, 128)), cam.xy((110, 0, 0)), cam.xy((267, 20, 0))
    s += lab(a[0], a[1] - 8, "陽極（＋）") + lab(b[0] + 10, b[1] - 8, "製品（−）")
    s += lab(c[0], c[1] + 16, "めっき液") + lab(d[0], d[1] + 16, "整流器")
    return s


# q:dip — pretreatment by dipping (degreasing / conversion coating): the car body is carried into
# the bath and turned over on its long axis (RoDip) so air pockets escape and every cavity is wetted
@picto("dip")
def _():
    def fn(sc):
        tank(sc, 0, 270, 0, 96, -66, 30, 16, lb=-6)
        Y(sc, 84, 74, banded(hull([(64, -34), (214, -34), (220, -16), (216, 2), (184, 6), (166, 26), (114, 28), (96, 8), (66, 4), (58, -16)]), 1), "w")

        def win(s_):
            o = ""
            for pts_ in (((102, 8), (116, 24), (138, 25), (138, 8)), ((144, 8), (144, 25), (156, 24), (170, 8))):
                o += path(P([s_.cam.xy((x, 9.9, z)) for x, z in pts_]), "dk")
            for x in (88, 190):
                o += path(P([s_.cam.xy((x + 16 * math.cos(a), 9.9, -34 + 16 * math.sin(a))) for a in [k * math.pi / 8 for k in range(9)]]), "dk")
            return o
        RAW(sc, win, ((72, 9.8, -34), (206, 10, 25)), -2)
        CYL(sc, (24, 46, -4), (1, 0, 0), 4, 230, "dk", seg=10, bands=5)       # rotating carrier shaft
        for x in (24, 250):
            BOX(sc, x - 3, 43, -4, 6, 6, 80, "dk")
        BOX(sc, 10, 40, 76, 254, 12, 8, "m")                                 # overhead conveyor
    s, sc = fit(fn, 16, 22, (14, 24, 306, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (256, 46, -4), (1, 0, 0), 30, 40, 170)
    s += arrow3(cam, (40, 0, 92), (100, 0, 92))
    a, b, c = cam.xy((70, 0, 92)), cam.xy((135, 0, -66)), cam.xy((256, 0, 30))
    s += al(a[0], a[1] - 8, "車体を回転させて浸漬") + lab(b[0], b[1] + 16, "脱脂・化成処理液")
    s += al(c[0] + 6, c[1] - 6, "回転", "start")
    return s


def half_tank(sc, cx, z0, z1, ro, ri, mat="pt", n_=6, floor=True):
    """vertical cylindrical vessel with its front half (y<0) cut away; section faces hatched."""
    for k in range(n_):
        t0, t1 = math.radians(180 * k / n_), math.radians(180 * (k + 1) / n_)
        Z(sc, z0, z1 - z0, [(cx + ri * math.cos(t0), ri * math.sin(t0)), (cx + ro * math.cos(t0), ro * math.sin(t0)),
                            (cx + ro * math.cos(t1), ro * math.sin(t1)), (cx + ri * math.cos(t1), ri * math.sin(t1))], mat, dark=1)
    if floor:
        Z(sc, z0 - 6, 6, arc(cx, 0, ro, 0, 180, 10), mat, dark=1)

    def cut(s_):
        return "".join(cutq(s_.cam, ((xa, 0, z0), (xb, 0, z0), (xb, 0, z1), (xa, 0, z1))) for xa, xb in ((cx - ro, cx - ri), (cx + ri, cx + ro)))
    RAW(sc, cut, ((cx - ro, -.2, z0), (cx + ro, 0, z1)), -3)


# q:impreg — vacuum pressure impregnation (cut model): the vessel is evacuated so air leaves the
# casting pores / winding gaps, resin floods in, then pressure drives it deep inside
@picto("impreg")
def _():
    def fn(sc):
        half_tank(sc, 0, 0, 110, 72, 66)
        RNG(sc, (0, 30, 6), (0, 0, 1), 30, 18, 44, "m", seg=32, dark=1)     # stator core
        RNG(sc, (0, 30, 50), (0, 0, 1), 26, 19, 8, "cu", seg=28)            # coil end turns
        Z(sc, 0, 64, arc(0, 0, 66, 0, 180, 12), "fl", -6)                   # resin
        CYL(sc, (0, 0, 136), (0, 0, 1), 76, 8, "pt", seg=40, dark=1)        # lid (lifted)
        CYL(sc, (-40, 0, 144), (0, 0, 1), 5, 24, "m", seg=10, bands=5)      # vacuum / pressure ports
        CYL(sc, (40, 0, 144), (0, 0, 1), 5, 24, "m", seg=10, bands=5)
    s, sc = fit(fn, -20, 26, (60, 24, 260, 170), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-40, 0, 170), (-40, 0, 196))
    s += arrow3(cam, (40, 0, 198), (40, 0, 172))
    a, b, c, d = cam.xy((-40, 0, 198)), cam.xy((40, 0, 198)), cam.xy((-72, 0, 30)), cam.xy((0, 30, 72))
    s += al(a[0] - 8, a[1] + 6, "① 真空", "end") + al(b[0] + 8, b[1] + 6, "③ 加圧", "start")
    s += lab(c[0] - 6, c[1], "② 樹脂", "end") + lab(d[0] + 50, d[1] + 4, "ステータ", "start")
    return s


# q:tspray — thermal spraying of a cylinder bore (cut model): a rotating gun travels down the bore
# and sprays molten metal droplets that build an iron-based coating on the aluminium wall
@picto("tspray")
def _():
    W, D, H, rb = 60, 44, 110, 34

    def rr(t):
        c, s_ = math.cos(t), math.sin(t)
        d = min(W / abs(c) if abs(c) > 1e-6 else 1e9, D / s_ if s_ > 1e-6 else 1e9)
        return d * c, d * s_

    def fn(sc):
        cor = [(math.atan2(D, W), (W, D)), (math.atan2(D, -W), (-W, D))]
        for k in range(6):
            t0, t1 = math.radians(30 * k), math.radians(30 * k + 30)
            pts_ = [(rb * math.cos(t0), rb * math.sin(t0)), rr(t0)] + [p for a, p in cor if t0 < a < t1] + \
                   [rr(t1), (rb * math.cos(t1), rb * math.sin(t1))]
            Z(sc, 0, H, pts_, "alu", dark=1)
            Z(sc, 0, 70, [(31 * math.cos(t0), 31 * math.sin(t0)), (rb * math.cos(t0), rb * math.sin(t0)),
                          (rb * math.cos(t1), rb * math.sin(t1)), (31 * math.cos(t1), 31 * math.sin(t1))], "w", -1)

        def cut(s_):
            o = "".join(cutq(s_.cam, ((xa, 0, 0), (xb, 0, 0), (xb, 0, H), (xa, 0, H))) for xa, xb in ((-W, -rb), (rb, W)))
            for xa, xb in ((-rb, -31), (31, rb)):
                o += path(P([s_.cam.xy(p) for p in ((xa, 0, 0), (xb, 0, 0), (xb, 0, 70), (xa, 0, 70))]), "w")
            return o
        RAW(sc, cut, ((-W, -.2, 0), (W, 0, H)), -3)
        CYL(sc, (0, 0, 70), (0, 0, 1), 9, 16, "dk", seg=18)                 # gun head
        CYL(sc, (0, 0, 86), (0, 0, 1), 5, 80, "m", seg=12, bands=6)         # lance
    s, sc = fit(fn, -22, 24, (70, 26, 250, 172), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    o = ""
    for k in range(7):
        t = math.radians(25 + 130 * k / 6)
        for dz in (-6, 6):
            a, b = cam.xy((7 * math.cos(t), 7 * math.sin(t), 78)), cam.xy((30 * math.cos(t), 30 * math.sin(t), 78 + dz))
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    s += path(o, "hl")
    s += arc3(cam, (0, 0, 110), (0, 0, 1), 18, 200, 340)
    s += arrow3(cam, (24, 0, 150), (24, 0, 120))
    a, b, c = cam.xy((0, 0, 166)), cam.xy((W, 0, 34)), cam.xy((-W, 0, 90))
    s += lab(a[0] + 10, a[1] + 4, "回転ガン", "start") + lab(b[0] + 6, b[1], "溶射皮膜", "start")
    s += lab(c[0] - 6, c[1], "ボア（アルミ）", "end")
    return s


# q:clad — laser cladding (also PTA overlay): metal powder blown coaxially into the laser focus melts
# into a pool and solidifies as an overlay bead; tracks are laid side by side
@picto("clad")
def _():
    xp = 120

    def fn(sc):
        BOX(sc, 0, 0, 0, 210, 90, 24, "w", dark=1)                          # base metal
        for y, x1 in ((22, 210), (36, 210), (50, xp)):                       # overlay beads
            CYL(sc, (x1, y, 22), (-1, 0, 0), 7, x1 - (xp if x1 == xp else 0) if x1 != xp else xp, "w", seg=16, bands=8, bias=-1)
        CYL(sc, (xp, 50, 23), (0, 0, 1), 8, 4, "h", seg=16, bias=-2)          # melt pool
        CYL(sc, (xp, 50, 46), (0, 0, 1), 6, 30, "m", seg=24, r1=17)          # coaxial powder nozzle
        CYL(sc, (xp, 50, 76), (0, 0, 1), 17, 44, "dk", seg=24)               # laser head
        CYL(sc, (xp + 30, 50, 60), (-1, 0, 0), 3, 14, "m", seg=10, bands=5)  # powder feed hose stub
    s, sc = fit(fn, -24, 26, (24, 24, 296, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((xp, 50, 46)), cam.xy((xp, 50, 27))
    s += line(a[0], a[1], b[0], b[1], "beam")
    for dx in (-5, 5):
        p = cam.xy((xp + dx, 50, 46))
        s += line(p[0], p[1], b[0] + dx * .2, b[1] - 1, "fo dash")
    s += arrow3(cam, (xp - 10, -8, 24), (xp - 70, -8, 24))
    c, d, e = cam.xy((xp, 50, 120)), cam.xy((xp + 44, 50, 60)), cam.xy((40, 0, 30))
    s += lab(c[0], c[1] - 8, "レーザ") + lab(d[0] + 6, d[1] + 4, "金属粉", "start")
    s += lab(e[0], e[1] - 14, "肉盛りビード") + al(cam.xy((xp - 40, -8, 24))[0], cam.xy((xp - 40, -8, 24))[1] + 18, "送り")
    return s


# q:vapor — vacuum metallizing (cut model): in high vacuum, aluminium on a hot filament evaporates and
# the vapour condenses as a mirror film on the reflectors turning on the rack (PVD / sputtering alike)
@picto("vapor")
def _():
    def fn(sc):
        half_tank(sc, 0, 0, 120, 80, 74)
        CYL(sc, (0, 40, -40), (0, 0, 1), 16, 34, "dk", seg=20)               # vacuum pump
        CYL(sc, (0, 40, -6), (0, 0, 1), 7, 6, "m", seg=12)
        CYL(sc, (0, 20, 6), (0, 0, 1), 3, 54, "m", seg=10, bands=5)          # filament post
        for z in (34, 82):                                                    # reflectors on the rack
            for k in range(5):
                t = math.radians(18 + 36 * k)
                c, si = math.cos(t), math.sin(t)
                CYL(sc, (60 * c, 20 + 52 * si, z), (-c, -si, 0), 12, 3, "alu", seg=16, bands=6)
    s, sc = fit(fn, -18, 22, (70, 24, 254, 168), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    f = cam.xy((0, 20, 60))
    s += circ(f[0], f[1], 3.4, "h")
    o = ""
    for z in (34, 82):
        for k in range(5):
            t = math.radians(18 + 36 * k)
            q = cam.xy((52 * math.cos(t), 20 + 46 * math.sin(t), z))
            o += "M%s %sL%s %s" % (n(f[0]), n(f[1]), n(q[0]), n(q[1]))
    s = s.replace(circ(f[0], f[1], 3.4, "h"), path(o, "ray") + circ(f[0], f[1], 3.4, "h"))
    s += arc3(cam, (0, 20, 124), (0, 0, 1), 40, 60, 160)
    s += arrow3(cam, (24, 40, -24), (56, 40, -24))
    a, b, c = cam.xy((0, 20, 60)), cam.xy((-80, 0, 100)), cam.xy((56, 40, -24))
    s += lab(a[0], a[1] + 18, "Al蒸発") + lab(b[0] - 6, b[1], "リフレクタ", "end")
    s += lab(c[0] + 6, c[1] + 4, "真空排気", "start")
    return s


# q:hardcoat — hard coating of a resin headlamp lens: the coat liquid flows down over the lens (flow
# coat / dip) in a clean booth, then UV lamps cure it into a scratch-resistant film
@picto("hardcoat")
def _():
    def lens(sc, x, wet):
        Y(sc, 40, 12, banded(hull(arc(x + 30, 30, 14, -40, 90, 5) + arc(x - 30, 30, 14, 90, 220, 5) + [(x - 40, 0), (x + 40, 0)]), 2), "fl")
        BOX(sc, x - 4, 34, 44, 8, 8, 24, "dk")                               # hanger
    def fn(sc):
        lens(sc, 0, 1)
        lens(sc, 150, 0)
        CYL(sc, (-10, 36, 76), (1, 0, 0), 4, 20, "m", seg=10, bands=5)       # coat nozzle
        BOX(sc, 100, 0, 96, 100, 46, 18, "dk", ch=3)                         # UV lamp house
        BOX(sc, -60, 52, -30, 270, 6, 20, "m", dark=1)                       # catch pan rear lip
        BOX(sc, -60, 0, -36, 270, 58, 6, "m", dark=1)
    s, sc = fit(fn, -16, 20, (24, 26, 296, 168), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    o = ""
    for dx in (-6, 0, 6):
        a, b = cam.xy((dx, 28, 72)), cam.xy((dx * 3, 27.8, 4))
        o += "M%s %sQ%s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] + dx), n((a[1] + b[1]) / 2), n(b[0]), n(b[1]))
    s += path(o, "jet")
    o = ""
    for dx in (-30, 0, 30):
        a, b = cam.xy((150 + dx, 10, 96)), cam.xy((150 + dx * 1.2, 26, 50))
        o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    s += path(o, "uv")
    a, b, c = cam.xy((0, 28, 84)), cam.xy((150, 0, 114)), cam.xy((150, 28, -36))
    s += lab(a[0], a[1] - 8, "フローコート") + lab(b[0] + 64, b[1] + 8, "UV硬化", "start")
    s += lab(c[0], c[1] + 18, "樹脂レンズ")
    return s


def car_side(x0, z0, k=1.0):
    """convex car-body side profile (x, z), length ~156*k."""
    return banded(hull([(x0 + k * x, z0 + k * z) for x, z in ((6, 0), (150, 0), (156, 18), (152, 36), (120, 40), (102, 60),
                                                               (50, 62), (32, 42), (2, 38), (0, 18))]), 1)


def car_marks(cam, x0, z0, y, k=1.0, c="dk"):
    """windows and wheel arches on the near side of car_side()."""
    o = ""
    for pts_ in (((38, 42), (54, 58), (76, 59), (76, 42)), ((82, 42), (82, 59), (98, 58), (114, 42))):
        o += path(P([cam.xy((x0 + k * x, y, z0 + k * z)) for x, z in pts_]), c)
    for x in (30, 124):
        o += path(P([cam.xy((x0 + k * (x + 15 * math.cos(a)), y, z0 + k * 15 * math.sin(a))) for a in [i * math.pi / 8 for i in range(9)]]), c)
    return o


# q:webcoat — web coating: fabric / film from the unwind roll passes a knife coater (coating pool in
# front of the blade), a drying oven and is wound up again
@picto("webcoat")
def _():
    zt = 40

    def fn(sc):
        RNG(sc, (0, 70, 20), (0, -1, 0), 24, 8, 70, "w", seg=32, dark=1)        # unwind roll
        CYL(sc, (84, 70, zt - 13), (0, -1, 0), 13, 70, "m", seg=20, bands=10)  # backing roll
        Y(sc, 64, 58, R(0, zt, 290, zt + 1.5), "w")                            # web
        Y(sc, 64, 58, R(88, zt + 1.5, 290, zt + 3), "fl", -1)                 # wet coat
        Y(sc, 64, 58, [(70, zt + 1.5), (86, zt + 1.5), (86, zt + 10), (76, zt + 8)], "fl", -1)  # coating pool
        Y(sc, 66, 62, [(86, zt + 3), (90, zt + 3), (96, zt + 34), (86, zt + 34)], "t")  # knife blade
        shell(sc, 130, 236, -4, 70, 0, 86)                                     # drying oven
        RNG(sc, (290, 70, 18), (0, -1, 0), 22, 8, 70, "w", seg=32)             # rewind roll
    s, sc = fit(fn, 16, 22, (10, 30, 310, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -8, 20), (0, -1, 0), 30, 200, 120)
    s += arrow3(cam, (30, -6, zt + 12), (64, -6, zt + 12))
    for x in (160, 200):
        q = cam.xy((x, 30, 64))
        s += heat(q[0] - 9, q[1], 3, 9)
    a, b, c, d = cam.xy((0, 0, -4)), cam.xy((92, 0, zt + 40)), cam.xy((183, 0, 86)), cam.xy((290, 0, -4))
    s += lab(a[0], a[1] + 18, "基布") + lab(b[0], b[1] - 8, "ナイフ塗布")
    s += lab(c[0], c[1] - 8, "乾燥炉") + lab(d[0], d[1] + 18, "巻取り")
    return s


# q:dipspin — dip-spin coating of small parts: a basket of bolts is dipped in the coating, lifted and
# spun so centrifugal force throws off the excess (zinc-flake coating)
@picto("dipspin")
def _():
    def fn(sc):
        tank(sc, -80, 80, -40, 70, -80, -20, -36)
        RNG(sc, (0, 14, 0), (0, 0, 1), 36, 32, 40, "m", seg=32)               # mesh basket
        CYL(sc, (0, 14, -4), (0, 0, 1), 36, 4, "m", seg=32)
        for k in range(7):                                                    # bolt heads in the basket
            a = 2 * math.pi * k / 7
            r = 0 if k == 0 else 20
            CYL(sc, (r * math.cos(a), 14 + r * math.sin(a), 30), (0, 0, 1), 6, 4, "w", seg=6, bands=6)
        CYL(sc, (0, 14, 40), (0, 0, 1), 4, 50, "m", seg=10, bands=5)          # spindle
        CYL(sc, (0, 14, 90), (0, 0, 1), 16, 30, "dk", seg=20)                 # spin motor

        def grid(s_):
            o = ""
            for k in range(14):
                a = math.pi * (1.05 + 0.9 * k / 13)
                p, q = s_.cam.xy((36 * math.cos(a), 14 + 36 * math.sin(a), 0)), s_.cam.xy((36 * math.cos(a), 14 + 36 * math.sin(a), 40))
                o += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1]))
            return path(o, "gline")
        RAW(sc, grid, ((-36, -22.2, 0), (36, -22, 40)), -3)
    s, sc = fit(fn, -20, 24, (50, 24, 270, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 14, 50), (0, 0, 1), 44, 30, 140)
    for x in (-40, 40):
        q = cam.xy((x, 0, 20))
        s += drops(q[0], q[1], 4, 30, 22, 180 if x < 0 else 0)
    s += arrow3(cam, (-58, 0, 34), (-58, 0, -14), both=True)
    a, b, c = cam.xy((0, 0, 50)), cam.xy((-58, 0, 10)), cam.xy((0, 0, -80))
    s += al(a[0] + 40, a[1] - 20, "回転で振切り", "start") + al(b[0] - 8, b[1] + 4, "浸漬", "end")
    s += lab(c[0], c[1] + 18, "塗料（亜鉛フレーク）")
    return s


def tongue(a, b, w, c="h"):
    """flame / jet tongue from screen point a to tip b, half width w at the base."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w, dx / L * w
    return path("M%s %sQ%s %s %s %sQ%s %s %s %sZ" % (n(a[0] + nx), n(a[1] + ny), n(a[0] + dx * .6 + nx * .8), n(a[1] + dy * .6 + ny * .8),
                                                   n(b[0]), n(b[1]), n(a[0] + dx * .6 - nx * .8), n(a[1] + dy * .6 - ny * .8),
                                                   n(a[0] - nx), n(a[1] - ny)), c)


# q:flame — flame (or atmospheric plasma) treatment of a PP bumper before painting: a line burner
# sweeps the surface and oxidises it so the paint will adhere
@picto("flame")
def _():
    def fn(sc):
        X(sc, 0, 230, banded(hull([(44, 0), (10, 2), (0, 18), (4, 36), (44, 40)]), 1), "dk")   # PP bumper
        BOX(sc, 90, -86, 8, 50, 14, 26, "m", ch=3)                             # line burner
        BOX(sc, 101, -86, 34, 28, 14, 40, "pt", dark=1)                        # robot wrist
    s, sc = fit(fn, -36, 22, (16, 26, 304, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (96, 107, 118, 129):
        for z in (14, 27):
            s += tongue(cam.xy((x, -72, z)), cam.xy((x + 2, -4, z + 1)), 2.6)
    s += arrow3(cam, (150, -86, 60), (210, -86, 60))
    a, b, c = cam.xy((90, -86, 8)), cam.xy((20, 44, 40)), cam.xy((150, -86, 60))
    s += lab(a[0], a[1] + 18, "ラインバーナ") + lab(b[0], b[1] - 10, "PPバンパー", "start")
    s += al(c[0], c[1] - 10, "炎で表面を活性化", "start")
    return s


# q:screen — screen printing: the squeegee pushes paste through the open mesh of the screen (stencil)
# onto the glass / part below; the printed band appears behind it
@picto("screen")
def _():
    def fn(sc):
        BOX(sc, -20, -10, -14, 260, 160, 10, "m", dark=1)                     # table
        Z(sc, -4, 4, [(0, 0), (220, 0), (220, 140), (0, 140)], "fl")          # glass
        for x0, y0, sx, sy in ((-14, -6, 248, 10), (-14, 136, 248, 10), (-14, 4, 10, 132), (224, 4, 10, 132)):
            BOX(sc, x0, y0, 6, sx, sy, 8, "dk")                               # screen frame

        def scr(s_):
            o = path(P([s_.cam.xy((x, y, 6.5)) for x, y in ((-4, 4), (224, 4), (224, 136), (-4, 136))]), "mesh")
            for pts_ in (((150, 14), (206, 14), (206, 126), (150, 126), (150, 112), (192, 112), (192, 28), (150, 28)),):
                o += path(P([s_.cam.xy((x, y, .1)) for x, y in pts_]), "dk")
            return o
        RAW(sc, scr, ((-4, 4, 0), (224, 136, 6.6)), -3)
        Y(sc, 130, 120, [(126, 6.6), (132, 6.6), (122, 36), (114, 36)], "t", -4)   # squeegee blade
        Y(sc, 134, 128, R(108, 36, 128, 52), "pt", -4, dark=1)                     # holder
    s, sc = fit(fn, -24, 34, (24, 26, 296, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((116, 12, 9)), cam.xy((116, 128, 9))
    s += line(a[0], a[1], b[0], b[1], "paste")
    s += arrow3(cam, (100, -16, 46), (40, -16, 46))
    c, d, e, f = cam.xy((118, 0, 52)), cam.xy((0, 140, 14)), cam.xy((220, 0, -14)), cam.xy((80, -16, 46))
    g = cam.xy((116, 12, 9))
    s += lab(c[0] + 30, c[1] - 4, "スキージ", "start") + lab(d[0], d[1] - 8, "スクリーン（版）")
    s += lab(e[0] - 4, e[1] + 18, "印刷面（ガラス）", "end") + lab(g[0] + 10, g[1] + 18, "ペースト", "start")
    return s


# =====================================================================================
# PAINTING
# =====================================================================================
# q:ed — cationic electrodeposition: the body (cathode, -) is fully immersed in the paint bath; DC from
# the rectifier drives paint particles from the anodes onto every surface, cavities included
@picto("ed")
def _():
    def fn(sc):
        tank(sc, 0, 280, 0, 100, -84, 16, 8, lb=-6)
        Y(sc, 88, 76, car_side(62, -70), "pt", dark=1)                       # body under the paint
        RAW(sc, lambda s_: car_marks(s_.cam, 62, -70, 11.9), ((62, 11.8, -70), (218, 12, -8)), -2)
        for x in (12, 262):
            BOX(sc, x, 20, -74, 6, 60, 70, "dk")                              # anodes
        for x in (90, 190):
            BOX(sc, x - 3, 47, -10, 6, 6, 70, "dk")                           # hangers
        BOX(sc, 0, 44, 60, 280, 12, 8, "m")                                    # conveyor
        BOX(sc, 296, 30, -84, 40, 40, 50, "dk", ch=3)                         # rectifier
    s, sc = fit(fn, 16, 22, (10, 26, 310, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x0, x1 in ((22, 54), (258, 226)):
        s += arrow3(cam, (x0, 0, -40), (x1, 0, -40))
    a, b, c, d = cam.xy((15, 0, 26)), cam.xy((140, 50, 68)), cam.xy((140, 0, -84)), cam.xy((316, 30, -84))
    s += lab(a[0], a[1] - 12, "陽極（＋）") + lab(b[0], b[1] - 8, "車体（−）")
    s += lab(c[0], c[1] + 16, "電着塗料の槽") + lab(d[0], d[1] + 16, "整流器")
    return s


# q:paintrobot — painting robot with a rotary bell: the cup spins at tens of thousands of rpm, the paint
# film breaks into fine mist at its edge and the electrostatic charge pulls it onto the body
@picto("paintrobot")
def _():
    sh, el, wr = (0, 0, 40), (24, 0, 132), (112, 0, 126)
    dv = GE._norm((0.3, 0, -1))
    b0 = tuple(wr[i] + 14 * dv[i] for i in range(3))
    rim = tuple(b0[i] + 10 * dv[i] for i in range(3))
    C = (rim[0] + dv[0] * 30, 0, 6)

    def fn(sc):
        BOX(sc, 40, -80, -6, 220, 160, 12, "m", ch=6)                         # body panel (hood)

        def painted(s_):
            return path(P([s_.cam.xy((x, y, 6.1)) for x, y in ((44, -42), (C[0], -42), (C[0], 42), (44, 42))]), "pt")
        RAW(sc, painted, ((40, -42, 6), (C[0], 42, 6.2)), -2)
        CYL(sc, (0, 0, -40), (0, 0, 1), 26, 14, "dk", seg=28)                # base
        CYL(sc, (0, 0, -26), (0, 0, 1), 18, 66, "pt", seg=24)                # turret
        d1 = tuple(el[i] - sh[i] for i in range(3))
        CYL(sc, sh, d1, 10, math.sqrt(sum(v * v for v in d1)), "pt", seg=20)  # upper arm
        CYL(sc, (el[0], -12, el[2]), (0, 1, 0), 14, 24, "dk", seg=20)        # elbow
        CYL(sc, el, (1, 0, -.07), 8, 88, "pt", seg=20)                        # forearm
        CYL(sc, wr, dv, 7, 14, "dk", seg=16)                                  # wrist
        CYL(sc, b0, dv, 6, 10, "t", seg=20, r1=14)                            # bell cup
    s, sc = fit(fn, -24, 22, (20, 24, 300, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    E1, E2, _ = GE.frame(dv)
    o = ""
    for i in range(70):
        u = ((i * 37) % 70) / 70
        a = 2 * math.pi * ((i * 0.618) % 1)
        rr_ = (14 + 30 * u) * ((i * 53) % 10 + 4) / 13
        p = tuple(rim[j] + (C[j] - rim[j]) * u + rr_ * (math.cos(a) * E1[j] + math.sin(a) * E2[j]) for j in range(3))
        q = cam.xy(p)
        o += circ(q[0], q[1], 1.1, "fdot")
    s += o
    s += arc3(cam, rim, dv, 20, 200, 340)
    s += arrow3(cam, (C[0] + 50, -70, 10), (C[0] + 100, -70, 10))
    a, b, c = cam.xy(rim), cam.xy((0, 0, -40)), cam.xy((C[0] + 75, -70, 10))
    s += lab(a[0] + 26, a[1] - 8, "回転霧化ベル＋静電", "start") + lab(b[0], b[1] + 18, "塗装ロボット")
    s += al(c[0], c[1] + 18, "車体")
    return s


# q:booth — paint booth (cut model): filtered, temperature/humidity-controlled air falls straight down
# (down-draft) past the body and through the grating, carrying overspray mist to the scrubber below
@picto("booth")
def _():
    def fn(sc):
        shell(sc, 0, 260, 0, 110, -46, 150)
        Y(sc, 102, 94, R(8, 0, 252, 3), "m", -1)                              # grating floor
        Y(sc, 102, 94, R(8, -38, 252, -28), "fl", -1)                         # scrubber water
        Y(sc, 88, 70, car_side(52, 4), "pt")
        RAW(sc, lambda s_: car_marks(s_.cam, 52, 4, 17.9), ((52, 17.8, 4), (208, 18, 66)), -2)

        def grid(s_):
            o = ""
            for k in range(1, 21):
                x = 8 + 244 * k / 21
                a, b = s_.cam.xy((x, 8, 3.1)), s_.cam.xy((x, 102, 3.1))
                o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            f = path(P([s_.cam.xy((x, y, 126)) for x, y in ((8, 0), (252, 0), (252, 102), (8, 102))]), "mesh")
            return path(o, "gline") + f
        RAW(sc, grid, ((8, 8, 3), (252, 102, 3.2)), -2)
    s, sc = fit(fn, 14, 18, (34, 22, 286, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    for x in (30, 230):
        s += arrow3(cam, (x, 20, 118), (x, 20, 20))
    for x in (100, 160):
        s += arrow3(cam, (x, 20, 118), (x, 20, 90))
    s += arrow3(cam, (240, 50, -16), (290, 50, -16))
    a, b, c = cam.xy((130, 0, 150)), cam.xy((130, 0, -46)), cam.xy((290, 50, -16))
    s += lab(a[0], a[1] - 8, "給気フィルタ（温湿度管理）") + lab(b[0], b[1] + 16, "グレーチング下で塗料ミスト捕集")
    s += al(c[0] - 4, c[1] - 8, "排気", "end")
    return s


# q:oven — paint baking oven (cut model): the body passes through a long tunnel where heated air is
# blown from ducts along the walls; the film cures at 140-180 C for about 20-30 minutes
@picto("oven")
def _():
    def fn(sc):
        shell(sc, 0, 290, 0, 110, 0, 112)
        BOX(sc, 8, 92, 10, 274, 10, 22, "m", dark=1)                           # hot-air duct (rear, low)
        BOX(sc, 8, 92, 78, 274, 10, 18, "m", dark=1)                           # hot-air duct (rear, high)
        BOX(sc, 110, 30, 112, 70, 50, 26, "dk", ch=3)                          # burner + circulation fan
        CYL(sc, (145, 55, 138), (0, 0, 1), 14, 10, "m", seg=18)
        for y in (24, 84):
            BOX(sc, 8, y, 8, 274, 6, 6, "dk")                                  # conveyor rails
        BOX(sc, 70, 26, 14, 160, 64, 4, "m")                                   # skid
        Y(sc, 84, 64, car_side(72, 18), "pt")
        RAW(sc, lambda s_: car_marks(s_.cam, 72, 18, 19.9), ((72, 19.8, 18), (228, 20, 80)), -2)
    s, sc = fit(fn, 16, 20, (16, 24, 304, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (40, 250):
        s += gas(cam, [(x, 90, 30), (x + (12 if x < 100 else -12), 40, 56), (x + (24 if x < 100 else -24), 10, 40)])
    for x in (110, 170):
        q = cam.xy((x, 50, 88))
        s += heat(q[0], q[1], 3, 9)
    s += arrow3(cam, (100, -6, 0), (190, -6, 0))
    a, b, c = cam.xy((145, 0, 140)), cam.xy((145, -6, 0)), cam.xy((40, 0, 112))
    s += lab(a[0] - 60, a[1] - 4, "熱風循環", "end") + lab(b[0], b[1] + 18, "焼付 140〜180℃ × 20〜30分")
    return s


# q:powdercoat — electrostatic powder coating: the gun charges the powder (-), the grounded spring
# attracts it, even round to the back (wrap-around); the powder is then melted and cured in an oven
@picto("powdercoat")
def _():
    def fn(sc):
        def spring(s_):
            cam = s_.cam
            N = 5 * 24
            pts_ = [(30 * math.cos(2 * math.pi * i / 24), 30 * math.sin(2 * math.pi * i / 24), 6 + 100 * i / N) for i in range(N + 1)]
            front = [cam.P(p)[2] < cam.P((0, 0, p[2]))[2] for p in pts_]
            w = 11 * cam.s
            o = {True: "", False: ""}
            run = [pts_[0]]
            for i in range(1, N + 1):
                if front[i] != front[i - 1]:
                    o[front[i - 1]] += P([cam.xy(q) for q in run + [pts_[i]]], False)
                    run = [pts_[i]]
                else:
                    run.append(pts_[i])
            o[front[-1]] += P([cam.xy(q) for q in run], False)
            ex = 'stroke-width="%s" stroke-linecap="round" fill="none"' % n(w + 2)
            ex2 = 'stroke-width="%s" stroke-linecap="round" fill="none"' % n(w)
            ex3 = 'stroke-width="%s" stroke-linecap="round" fill="none"' % n(w * .3)
            return (path(o[False], "o", ex) + path(o[False], "sheet", ex2) + path(o[True], "o", ex) +
                    path(o[True], "strip", ex2) + path(o[True], "gline", ex3))
        RAW(sc, spring, ((-36, -36, 0), (36, 36, 112)), 0)
        BOX(sc, -3, -3, 112, 6, 6, 40, "dk")                                    # hanger (ground)
        CYL(sc, (-150, 0, 56), (1, 0, 0), 12, 50, "dk", seg=18)                # powder gun
        CYL(sc, (-100, 0, 56), (1, 0, 0), 8, 14, "t", seg=16, r1=4)            # nozzle + charging electrode
        CYL(sc, (-150, 0, 30), (0, 0, 1), 6, 26, "dk", seg=12, bands=6)        # grip
    s, sc = fit(fn, -18, 20, (24, 26, 296, 170), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    o = ""
    for i in range(80):
        u = ((i * 29) % 80) / 80
        a = 2 * math.pi * ((i * 0.618) % 1)
        r = (4 + 36 * u) * (((i * 47) % 9) + 3) / 11
        q = cam.xy((-86 + 76 * u, r * math.cos(a) * .6, 56 + r * math.sin(a)))
        o += circ(q[0], q[1], 1.2, "pwd")
    s = s + o
    s += gas(cam, [(-10, -30, 90), (10, 50, 104), (36, 46, 92)]) + gas(cam, [(-10, -30, 22), (10, 50, 10), (36, 46, 22)])
    a, b, c = cam.xy((-150, 0, 30)), cam.xy((0, 0, 152)), cam.xy((-60, 0, 100))
    s += lab(a[0], a[1] + 16, "静電粉体ガン（−）") + lab(b[0] + 8, b[1] + 4, "ばね（アース）", "start")
    s += lab(c[0], c[1] - 8, "粉体塗料")
    return s


# q:polish — paint repair: a dust nib in the clear coat is sanded flat, then the spot is polished back
# to gloss with a rotating foam pad (hand tool or robot)
@picto("polish")
def _():
    def fn(sc):
        BOX(sc, 0, 0, -10, 240, 150, 10, "pt", ch=8)                           # painted panel

        def spots(s_):
            o = hole3(s_.cam, (170, 74, .1), (0, 0, 1), 16, "m")              # sanded (matt) patch
            o += hole3(s_.cam, (170, 74, .2), (0, 0, 1), 3, "dk")             # dust nib
            return o
        RAW(sc, spots, ((150, 54, 0), (190, 94, .3)), -2)
        CYL(sc, (80, 70, 0), (0, 0, 1), 30, 8, "t", seg=32)                     # foam pad
        CYL(sc, (80, 70, 8), (0, 0, 1), 26, 5, "dk", seg=28)                    # backing plate
        CYL(sc, (80, 70, 13), (0, 0, 1), 13, 40, "dk", seg=20)                  # motor
        BOX(sc, 64, 56, 53, 32, 28, 24, "pt", dark=1, ch=3)                     # robot wrist
    s, sc = fit(fn, -22, 30, (34, 26, 286, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (80, 70, 4), (0, 0, 1), 42, 20, 130)
    s += arrow3(cam, (118, 70, 2), (148, 72, 2))
    a, b, c = cam.xy((170, 74, 0)), cam.xy((80, 70, 77)), cam.xy((80, 26, 0))
    s += lab(a[0] + 18, a[1] - 10, "ブツ（異物）", "start") + lab(b[0], b[1] - 8, "ポリッシャ")
    s += al(c[0] - 4, c[1] + 22, "研ぎ→磨き")
    return s
