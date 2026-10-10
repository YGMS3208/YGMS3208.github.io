"""v3 shaded-3D principle drawings (q:keys) for casting and forging / forming equipment:
melting, melt treatment, die casting (high-pressure / low-pressure / gravity), sand moulding and cores,
investment casting, trimming, shake-out, shot blasting, hot / cold forging, heading, induction heating,
billet cutting, upsetting, ring rolling, straightening, drawing, bending, spring coiling / setting,
fin forming and roll forming. Molten metal is class h, dies / tools t, castings / forgings w."""
import math
import re
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il_mt import Scene  # noqa: F401
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3

PI = math.pi


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


# ------------------------------------------------------------------ local helpers
def Y(sc, y0, L, xz, mat="w", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded along +y from y0."""
    loop = [(-p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L, mat, **kw)),
           ((min(xs), min(y0, y0 + L), min(zs)), (max(xs), max(y0, y0 + L), max(zs))), bias)


def zprism(cam, C, z0, h, xy, mat, **kw):
    """svg of outline [(x, y)] (relative to C) extruded along +z: for hand-ordered drawings."""
    loop = [(-p[1], p[0], p[2] if len(p) > 2 else i) for i, p in enumerate(xy)]
    return compact(GE.prism(cam, (C[0], C[1], z0), (0, 0, 1), loop, h, mat, **kw))


def cut_vessel(cam, C, ro, ri, z0, h, mat, fill=None, fill_h=0, floor=0, n=6, dark=0, fill_dark=0):
    """vertical cylindrical vessel cut open on the plane y=C.y (front half removed):
    back half of the wall (segments, inner face visible), optional floor, optional contents (fill class)."""
    o = ""
    E = cam.D
    segs = []
    for k in range(n):
        a0, a1 = 180.0 * k / n, 180.0 * (k + 1) / n
        q = [(ri * math.cos(math.radians(a0)), ri * math.sin(math.radians(a0))),
             (ro * math.cos(math.radians(a0)), ro * math.sin(math.radians(a0))),
             (ro * math.cos(math.radians(a1)), ro * math.sin(math.radians(a1))),
             (ri * math.cos(math.radians(a1)), ri * math.sin(math.radians(a1)))]
        am = math.radians((a0 + a1) / 2)
        dep = cam.P((C[0] + ro * math.cos(am), C[1] + ro * math.sin(am), z0 + h / 2))[2]
        segs.append((dep, q))
    segs.sort(key=lambda t: -t[0])
    for _, q in segs:
        o += zprism(cam, C, z0, h, [(x, y, i) for i, (x, y) in enumerate(q)], mat, dark=dark, lines=False)
    if floor:
        o += zprism(cam, C, z0, floor, banded(arc(0, 0, ri, 0, 180, 12), 2), mat, dark=dark, lines=False)
    if fill:
        o += zprism(cam, C, z0 + floor, fill_h - floor, banded(arc(0, 0, ri, 0, 180, 12), 2), fill, dark=fill_dark)
    # rim and cut-face edges
    rim = [cam.xy((C[0] + x, C[1] + y, z0 + h)) for x, y in arc(0, 0, ro, 0, 180, 18)]
    rin = [cam.xy((C[0] + x, C[1] + y, z0 + h)) for x, y in arc(0, 0, ri, 0, 180, 18)]
    o += path(P(rim, False) + P(rin, False), "el")
    for sx in (-1, 1):
        f = [cam.xy((C[0] + sx * ri, C[1], z0 + floor)), cam.xy((C[0] + sx * ri, C[1], z0 + h)),
             cam.xy((C[0] + sx * ro, C[1], z0 + h)), cam.xy((C[0] + sx * ro, C[1], z0))]
        o += path(P(f, False), "el")
    bot = [cam.xy((C[0] - ro, C[1], z0)), cam.xy((C[0] + ro, C[1], z0))]
    o += path(P(bot, False), "el")
    return o


_SD = re.compile(r'<path class="sands(\d)((?: [\w-]+)*)"((?: fill-rule="evenodd")?) d="([^"]*)"/>')
_SOP = {"1": "", "2": ".1", "3": ".22", "4": ".38"}


def sandify(svg):
    """prism faces drawn with mat "sand" (no shaded classes exist) -> flat sand fill + a faint shade overlay."""
    def f(m):
        o = '<path class="sand%s"%s d="%s"/>' % (m.group(2), m.group(3), m.group(4))
        op = _SOP[m.group(1)]
        return o + ('<path class="grain" opacity="%s"%s d="%s"/>' % (op, m.group(3), m.group(4)) if op else "")
    return _SD.sub(f, svg)


def stream(cam, p0, p1, r=3.2):
    """falling molten metal: a thin hot column between two world points."""
    a, b = cam.xy(p0), cam.xy(p1)
    w = r * cam.s
    return path("M%s %sL%s %sL%s %sL%s %sZ" % (n(a[0] - w), n(a[1]), n(a[0] + w), n(a[1]), n(b[0] + w * .8), n(b[1]), n(b[0] - w * .8), n(b[1])), "h")


# =====================================================================================
# q:hpdc — high-pressure die casting: the plunger shoots melt from the shot sleeve
# horizontally into the closed die between the fixed and the moving platen
# =====================================================================================
@picto("hpdc")
def _():
    zs = -22                                                     # shot sleeve height

    def fn(sc):
        BOX(sc, 0, -70, -72, 22, 140, 156, "pt", dark=1)                       # fixed platen
        BOX(sc, 22, -46, -46, 26, 92, 104, "t", -1)                            # fixed die half
        BOX(sc, 48, -46, -46, 26, 92, 104, "t", -1)                            # moving die half
        BOX(sc, 74, -70, -72, 22, 140, 156, "pt", dark=1)                      # moving platen
        for y in (-56, 56):
            for z in (-58, 70):
                CYL(sc, (-6, y, z), (1, 0, 0), 6.5, 176, "m", seg=16, bias=-.5)   # tie bars
        CYL(sc, (96, 0, 6), (1, 0, 0), 24, 46, "dk", seg=28)                  # clamping cylinder
        CYL(sc, (-96, 0, zs), (1, 0, 0), 12, 96, "m", seg=24)                 # shot sleeve
        CYL(sc, (-150, 0, zs), (1, 0, 0), 5, 54, "w", seg=16)                 # plunger rod
        CYL(sc, (-196, 0, zs), (1, 0, 0), 17, 46, "dk", seg=28)               # shot cylinder
        hx = -76

        def pour(s_):
            cam = s_.cam
            o = hole3(cam, (hx, 0, zs + 12.2), (0, 0, 1), 6)
            o += stream(cam, (hx - 2, 0, zs + 62), (hx, 0, zs + 12), 3)
            return o
        RAW(sc, pour, ((hx - 6, -6, zs + 12), (hx + 6, 6, zs + 64)), -2)
        # ladle above the pour hole, tipped toward +x
        a = math.radians(38)
        A = (math.sin(a), 0, math.cos(a))
        O = (hx - 30, 0, zs + 64)
        sc.add(compact(GE.prism(sc.cam, O, A, GE.circle_outline(15, 28, 8), 22, "dk", smooth=True, cap_mat="h",
                                scale=lambda t: 1 + .25 * t)), ((O[0] - 18, -18, O[2] - 6), (O[0] + 30, 18, O[2] + 30)), -3)
    s, sc = fit(fn, 14, 20, (16, 24, 304, 170), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-150, -30, zs - 34), (-60, -30, zs - 34))
    s += arrow3(cam, (190, 0, 92), (120, 0, 92))
    a = cam.xy((-105, -30, zs - 34))
    b = cam.xy((155, 0, 92))
    d = cam.xy((48, -70, -72))
    s += al(a[0], a[1] + 16, "高速射出") + al(b[0], b[1] - 8, "型締め")
    s += lab(d[0], d[1] + 16, "金型")
    return s


# =====================================================================================
# q:lpdc — low-pressure casting: air pressure on the sealed furnace pushes the melt up the
# stalk into the die above, slowly and from below
# =====================================================================================
@picto("lpdc")
def _():
    def fn(sc):
        cam = sc.cam

        def furnace(s_):
            c = s_.cam
            o = cut_vessel(c, (0, 0), 80, 64, -110, 96, "pt", "h", 64, floor=12, dark=1)
            o += cut_vessel(c, (0, 0), 13, 8, -96, 92, "m", "h", 92, n=4)        # stalk tube (melt inside)
            return o
        RAW(sc, furnace, ((-80, 0, -110), (80, 80, -14)), 0)
        BOX(sc, -96, -80, -14, 192, 160, 14, "pt", dark=1)                      # lower platen / furnace lid
        BOX(sc, -46, -40, 0, 46, 80, 52, "t", ch=3)                            # side dies
        BOX(sc, 0, -40, 0, 46, 80, 52, "t", ch=3)
        BOX(sc, -50, -44, 52, 100, 88, 14, "t")                                # top die
        BOX(sc, -72, -60, 66, 144, 120, 14, "pt", dark=1)                      # upper platen
        CYL(sc, (0, 0, 80), (0, 0, 1), 14, 34, "dk", seg=24)                   # ejector / upper cylinder
        for x in (-80, 80):
            CYL(sc, (x, -52, 0), (0, 0, 1), 5, 66, "m", seg=14)
            CYL(sc, (x, 52, 0), (0, 0, 1), 5, 66, "m", seg=14)
        CYL(sc, (-80, -40, -40), (-1, 0, 0), 4.5, 30, "m", seg=14, bias=-1)   # air inlet pipe
    s, sc = fit(fn, -24, 16, (40, 16, 280, 174), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-40, -2, -18), (-40, -2, -44))
    s += arrow3(cam, (-48, -2, -18), (-48, -2, -44))
    s += arrow3(cam, (22, -2, -84), (22, -2, -20))
    a = cam.xy((-110, -40, -40))
    b = cam.xy((20, -2, -60))
    d = cam.xy((72, -60, 74))
    m = cam.xy((70, -4, -80))
    s += al(a[0] - 2, a[1] - 8, "空気圧", "end") + al(b[0] + 6, b[1] + 4, "押上げ", "start")
    s += lab(d[0] + 8, d[1], "金型", "start") + lab(m[0] - 4, m[1] + 14, "溶湯", "end")
    return s


# =====================================================================================
# q:gravity — gravity die casting: the ladle pours melt from above into the sprue of the die
# =====================================================================================
@picto("gravity")
def _():
    def fn(sc):
        BOX(sc, -110, -60, -64, 220, 120, 16, "pt", dark=1)                    # machine base
        BOX(sc, -60, -36, -48, 60, 72, 86, "t", ch=3)                          # die halves (split at x=0)
        BOX(sc, 0, -36, -48, 60, 72, 86, "t", ch=3)
        BOX(sc, -100, -24, -40, 40, 48, 50, "dk")                              # die-open cylinders
        BOX(sc, 60, -24, -40, 40, 48, 50, "dk")
        CYL(sc, (-100, 0, -15), (-1, 0, 0), 8, 10, "m", seg=16)
        CYL(sc, (100, 0, -15), (1, 0, 0), 8, 10, "m", seg=16)

        def cup(s_):
            c = s_.cam
            o = hole3(c, (14, -6, 38.2), (0, 0, 1), 11, "bg")
            o += hole3(c, (14, -6, 38.3), (0, 0, 1), 6.5, "h")
            o += stream(c, (10, -6, 101), (14, -6, 39), 3.4)
            return o
        RAW(sc, cup, ((2, -18, 38), (26, 6, 100)), -3)
        # ladle tipped toward +x over the sprue
        a = math.radians(40)
        A = (math.sin(a), 0, math.cos(a))
        O = (-30, -6, 96)
        sc.add(compact(GE.prism(sc.cam, O, A, GE.circle_outline(22, 28, 8), 30, "dk", smooth=True, cap_mat="h",
                                scale=lambda t: 1 + .2 * t)), ((O[0] - 26, -30, O[2] - 14), (O[0] + 40, 18, O[2] + 34)), -4)
        CYL(sc, (-46, -6, 112), (-1, 0, .45), 4, 64, "m", seg=12, bias=-4)    # handle
    s, sc = fit(fn, -30, 20, (50, 14, 270, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-28, -6, 110), (0, 1, 0), 52, 75, 130)
    a = cam.xy((-60, -6, 140))
    s += al(a[0] - 4, a[1] - 2, "傾けて注湯", "end")
    p = cam.xy((14, -6, 70))
    d = cam.xy((0, -60, -64))
    s += lab(p[0] + 14, p[1] + 2, "溶湯", "start") + lab(d[0], d[1] + 16, "金型")
    return s


# =====================================================================================
# q:melt — melting furnace (induction crucible, cut open): ingots charged from above melt in the
# crucible; the water-cooled copper coil in the wall heats the metal itself
# =====================================================================================
@picto("melt")
def _():
    def fn(sc):
        def body(s_):
            c = s_.cam
            o = cut_vessel(c, (0, 0), 78, 54, -70, 112, "pt", "h", 86, floor=16, dark=1)
            for sx in (-1, 1):                                                 # coil cross-sections in the wall
                for k in range(7):
                    o += hole3(c, (sx * 66, -.2, -54 + k * 13.5), (0, -1, 0), 4.4, "cu")
            o += heat(*c.xy((-14, 30, 30)), cnt=3, gap=12, hgt=14)
            return o
        RAW(sc, body, ((-78, 0, -70), (78, 78, 42)), 0)
        BOX(sc, -92, -86, -86, 184, 172, 16, "pt", dark=1)                     # base
        for k, (x, z, r) in enumerate(((-26, 78, 0), (8, 104, 14), (38, 82, -10))):   # ingots coming in
            a = math.radians(r)
            pts = [(-22, -9), (22, -9), (18, 9), (-18, 9)]
            Y(sc, -12, 26, [(x + u * math.cos(a) - v * math.sin(a), z + u * math.sin(a) + v * math.cos(a)) for u, v in pts], "w", -1, dark=0)
    s, sc = fit(fn, -26, 22, (60, 12, 262, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-62, -20, 112), (-62, -20, 60))
    a = cam.xy((-62, -20, 90))
    b = cam.xy((80, -2, 0))
    c = cam.xy((-78, -2, -30))
    s += lab(a[0] - 8, a[1], "地金", "end") + lab(b[0] + 8, b[1] - 6, "溶湯", "start")
    s += lab(c[0] - 8, c[1] + 4, "コイル", "end")
    return s


# =====================================================================================
# q:degas — rotary degassing: a spinning graphite rotor breaks inert gas into fine bubbles that
# carry hydrogen and oxides up out of the melt in the ladle (cut open)
# =====================================================================================
@picto("degas")
def _():
    def fn(sc):
        def ladle(s_):
            c = s_.cam
            return cut_vessel(c, (0, 0), 72, 58, -80, 120, "m", "h", 92, floor=14, dark=1)
        RAW(sc, ladle, ((-72, 0, -80), (72, 72, 40)), 0)
        CYL(sc, (0, 0, -52), (0, 0, 1), 7, 150, "dk", seg=16, bias=-2)        # shaft
        CYL(sc, (0, 0, -62), (0, 0, 1), 20, 12, "dk", seg=24, bias=-2.2)       # rotor

        def bub(s_):
            c = s_.cam
            o = ""
            for k, (x, z, r) in enumerate(((-30, -50, 2.4), (28, -46, 2.2), (-40, -24, 3), (36, -20, 2.8), (-18, -34, 2),
                                           (20, -30, 2.2), (-50, 0, 3.2), (46, 6, 3), (-26, 4, 2.6), (14, -6, 2.4), (32, 14, 2))):
                X0, Y0 = c.xy((x, -1, z))
                o += circ(X0, Y0, r * c.s * 1.3, "bub")
            return o
        RAW(sc, bub, ((-60, -2, -60), (60, -1, 20)), -3)
        BOX(sc, -26, -22, 98, 52, 44, 30, "pt", dark=1)                        # drive unit
        CYL(sc, (26, 0, 113), (1, 0, 0), 14, 26, "dk", seg=20)                 # motor
    s, sc = fit(fn, -26, 22, (70, 12, 256, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 60), (0, 0, 1), 22, 200, 340)
    s += arrow3(cam, (-50, 0, 120), (-14, 0, 104))
    a = cam.xy((-50, 0, 120))
    r = cam.xy((22, 0, 60))
    m = cam.xy((76, -2, -10))
    s += al(a[0] - 4, a[1] - 4, "不活性ガス", "end") + al(r[0] + 10, r[1] + 4, "回転", "start")
    s += lab(m[0] + 8, m[1] + 4, "溶湯", "start")
    return s


# =====================================================================================
# q:sand — green-sand moulding: the squeeze head compacts sand in the flask over the pattern;
# the finished mould half carries the cavity imprint
# =====================================================================================
@picto("sand")
def _():
    def fn(sc):
        BOX(sc, -84, -60, -40, 168, 120, 12, "m")                              # pattern plate
        for x0, sx in ((-70, 8), (62, 8)):                                     # flask walls
            BOX(sc, x0, -52, -28, sx, 104, 60, "dk")
        BOX(sc, -62, 44, -28, 124, 8, 60, "dk")
        BOX(sc, -62, -52, -28, 124, 8, 60, "dk", -.5)
        BOX(sc, -62, -44, -28, 124, 88, 56, "sand")                            # rammed sand
        BOX(sc, -62, -44, 50, 124, 88, 12, "m")                                # squeeze plate
        CYL(sc, (0, 0, 62), (0, 0, 1), 16, 44, "dk", seg=24)                    # squeeze ram
        # finished mould half on the line (cavity facing up)
        BOX(sc, 128, -52, -40, 136, 104, 60, "dk", ch=0)
        BOX(sc, 136, -44, 20, 120, 88, 0.01, "sand")

        def cav(s_):
            c = s_.cam
            o = hole3(c, (196, 0, 20.2), (0, 0, 1), 28, "bg")
            o += hole3(c, (196, 0, 20.3), (0, 0, 1), 10, "sand")
            ch = [c.xy(p) for p in ((150, -4, 20.2), (168, -4, 20.2), (168, 4, 20.2), (150, 4, 20.2))]
            o += path(P(ch), "bg") + hole3(c, (146, 0, 20.3), (0, 0, 1), 7, "bg")
            return o
        RAW(sc, cav, ((136, -44, 20), (256, 44, 20.4)), -2)
    s, sc = fit(fn, -24, 26, (14, 16, 306, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    s = sandify(s)
    cam = sc.cam
    s += arrow3(cam, (86, -44, 112), (86, -44, 66))
    a = cam.xy((86, -44, 94))
    b = cam.xy((-62, -44, 0))
    d = cam.xy((196, -52, -40))
    s += al(a[0] + 10, a[1], "加圧", "start") + lab(b[0] + 6, b[1] + 50, "生砂", "start")
    s += lab(d[0], d[1] + 16, "鋳型（下型）")
    return s


# =====================================================================================
# q:core — core shooter: resin-bonded sand is blown into the closed core box and hardened by gas
# (cold box) or heat (shell); the finished sand core forms the hollow passages of the casting
# =====================================================================================
@picto("core")
def _():
    def fn(sc):
        BOX(sc, -96, -60, -60, 192, 120, 14, "pt", dark=1)                     # machine table
        BOX(sc, -66, -40, -46, 64, 80, 70, "t", ch=3)                           # core box halves
        BOX(sc, 2, -40, -46, 64, 80, 70, "t", ch=3)
        BOX(sc, -54, -34, 40, 108, 68, 10, "m")                                 # blow plate
        BOX(sc, -40, -26, 50, 80, 52, 50, "pt", dark=1)                         # sand magazine / shooting head
        CYL(sc, (-102, 0, -13), (1, 0, 0), 8, 36, "m", seg=16)                  # box clamp rods
        CYL(sc, (66, 0, -13), (1, 0, 0), 8, 36, "m", seg=16)
        # finished core in front: a curved port-like passage core
        CYL(sc, (130, -10, -46), (0, 0, 1), 13, 40, "sand", seg=24)
        CYL(sc, (130, -10, -6), (1, 0, 0), 13, 70, "sand", seg=24, bias=-.2)
        CYL(sc, (186, -10, -46), (0, 0, 1), 10, 40, "sand", seg=24, bias=.2)
    s, sc = fit(fn, -28, 22, (24, 16, 300, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    s = sandify(s)
    cam = sc.cam
    for x in (-18, 18):
        s += arrow3(cam, (x, -20, 58), (x, -20, 26))
    a = cam.xy((-40, -26, 100))
    b = cam.xy((-66, -40, -46))
    d = cam.xy((158, -10, 30))
    s += al(a[0] - 6, a[1] + 4, "砂を吹込み", "end") + lab(b[0] - 4, b[1] + 4, "中子型", "end")
    s += lab(d[0], d[1] - 6, "砂中子")
    return s


# =====================================================================================
# q:invest — investment (lost-wax) casting: wax patterns on a tree are dipped into ceramic
# slurry; the wax is melted out and metal is poured into the hollow shell
# =====================================================================================
def _tree(sc, x0, mat, r0=0, bias=0.0):
    CYL(sc, (x0, 0, -40), (0, 0, 1), 7 + r0, 100, mat, seg=12, bias=bias, bands=4)          # sprue
    CYL(sc, (x0, 0, 60), (0, 0, 1), 9 + r0, 20, mat, seg=20, r1=20 + r0, bias=bias, bands=4)  # pour cup
    for z in (-20, 28):
        for sx in (-1, 1):
            CYL(sc, (x0 + sx * 7, 0, z), (sx, 0, 0), 3 + r0, 10, mat, seg=10, bias=bias, bands=4)          # gate
            CYL(sc, (x0 + sx * 17, -6 - r0, z), (0, 1, 0), 15 + r0, 12 + 2 * r0, mat, seg=16, bias=bias, bands=4)  # wheel


@picto("invest")
def _():
    def fn(sc):
        BOX(sc, -50, -30, -50, 100, 60, 10, "m")                               # wax-tree stand
        _tree(sc, 0, "pt")
        BOX(sc, 110, -30, -50, 100, 60, 10, "m")
        _tree(sc, 160, "m", r0=2.5)

        def pour(s_):
            c = s_.cam
            o = hole3(c, (160, 0, 80.2), (0, 0, 1), 18, "bg") + hole3(c, (160, 0, 80.3), (0, 0, 1), 12, "h")
            o += stream(c, (158, 0, 128), (160, 0, 81), 3.6)
            return o
        RAW(sc, pour, ((140, -20, 80), (180, 20, 130)), -3)
        a = math.radians(42)
        A = (math.sin(a), 0, math.cos(a))
        O = (124, 0, 118)
        sc.add(compact(GE.prism(sc.cam, O, A, GE.circle_outline(17, 28, 8), 24, "dk", smooth=True, cap_mat="h",
                                scale=lambda t: 1 + .15 * t)), ((O[0] - 20, -22, O[2] - 12), (O[0] + 32, 22, O[2] + 28)), -4)
    s, sc = fit(fn, -20, 18, (30, 14, 290, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (52, -30, 20), (104, -30, 20))
    a = cam.xy((78, -30, 20))
    w = cam.xy((0, -30, -50))
    h = cam.xy((160, -30, -50))
    s += al(a[0], a[1] - 10, "脱ロウ") + lab(w[0], w[1] + 18, "ワックス模型") + lab(h[0], h[1] + 18, "セラミック殻に鋳込み")
    return s


# =====================================================================================
# q:trim — trimming press: the slide brings the trim die down; overflows, runners and flash
# around the casting are sheared off against the lower die
# =====================================================================================
@picto("trim")
def _():
    def fn(sc):
        BOX(sc, -100, -64, -54, 200, 128, 20, "pt", dark=1)                   # bolster
        BOX(sc, -62, -44, -34, 124, 88, 30, "t")                               # lower die
        BOX(sc, -58, -40, -4, 116, 80, 30, "w", ch=6)                          # casting
        BOX(sc, -86, -52, -4, 172, 104, 3, "w", .3)                            # flash / overflow web
        for x in (-78, -40, 0, 40):
            BOX(sc, x, -52, -1, 18, 10, 8, "w", -.2)                           # overflows (front)
        CYL(sc, (86, 0, -4), (0, 0, 1), 18, 12, "w", seg=24, bias=.1)          # biscuit / runner
        BOX(sc, -66, -48, 60, 132, 96, 26, "t")                                # upper trim die
        BOX(sc, -90, -64, 86, 180, 128, 30, "pt", dark=1)                      # slide

        def holes(s_):
            o = ""
            for x, y in ((-30, -14), (0, 10), (30, -14)):
                o += hole3(s_.cam, (x, y, 26.2), (0, 0, 1), 7)
            return o
        RAW(sc, holes, ((-40, -24, 26), (40, 20, 26.3)), -2)
    s, sc = fit(fn, -28, 22, (40, 14, 280, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (118, -40, 110), (118, -40, 66))
    a = cam.xy((118, -40, 90))
    b = cam.xy((-86, -52, -4))
    d = cam.xy((-66, -48, 73))
    s += al(a[0] + 8, a[1], "下降", "start") + lab(b[0] - 4, b[1] + 4, "バリ・湯口", "end")
    s += lab(d[0] - 6, d[1] + 4, "抜き型", "end")
    return s


# =====================================================================================
# q:shakeout — shake-out: the vibrating grid shakes the sand off the casting (it falls through);
# the riser / sprue is then cut off with an abrasive wheel
# =====================================================================================
@picto("shakeout")
def _():
    def fn(sc):
        BOX(sc, -120, -66, -78, 240, 132, 14, "pt", dark=1)                    # base frame
        for x in (-92, 92):
            for y in (-44, 44):
                CYL(sc, (x, y, -64), (0, 0, 1), 9, 30, "dk", seg=16)           # springs
        BOX(sc, -116, -62, -34, 232, 124, 12, "m")                             # vibrating grid

        def grid(s_):
            o = ""
            for k in range(9):
                x = -100 + k * 25
                o += path(P([s_.cam.xy(p) for p in ((x, -54, -21.8), (x + 8, -54, -21.8), (x + 8, 54, -21.8), (x, 54, -21.8))]), "bg")
            return o
        RAW(sc, grid, ((-116, -62, -22), (116, 62, -21.7)), -1)
        BOX(sc, -70, -40, -22, 100, 80, 52, "w", ch=5)                         # casting
        CYL(sc, (10, 0, 30), (0, 0, 1), 12, 34, "w", seg=20)                   # riser / sprue
        for (x, y, z, sx, sy, sz) in ((-70, -40, 30, 40, 34, 10), (-60, -6, 30, 30, 30, 14), (-20, 10, 30, 20, 30, 8)):
            BOX(sc, x, y, z, sx, sy, sz, "sand", -.5)                          # sand clinging to the top
        CYL(sc, (52, -4, 50), (0, 1, 0), 34, 5, "t", seg=40, bias=-1)         # cut-off wheel
        CYL(sc, (52, 1, 50), (0, 1, 0), 9, 16, "m", seg=16, bias=-.8)

        def fall(s_):
            o = ""
            for k, (x, y) in enumerate(((-80, -30), (-50, 0), (-20, -40), (10, 20), (40, -10), (70, -40), (-60, 30), (30, -50))):
                for j in range(2):
                    X0, Y0 = s_.cam.xy((x + j * 6, y, -44 - (k % 3) * 6 - j * 10))
                    o += circ(X0, Y0, 1.6, "sand")
            return o
        RAW(sc, fall, ((-90, -50, -70), (80, 30, -40)), 0)
    s, sc = fit(fn, -26, 24, (34, 16, 286, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    s = sandify(s)
    cam = sc.cam
    t = cam.xy((18, -4, 34))
    s += sparks(t[0] + 4, t[1] + 2, 12, 5, -10, 70)
    s += arrow3(cam, (-140, -62, -28), (-104, -62, -28), both=True)
    s += arc3(cam, (52, -6, 50), (0, 1, 0), 42, 20, 90)
    a = cam.xy((-122, -62, -28))
    b = cam.xy((72, -4, 96))
    d = cam.xy((-60, -40, 40))
    s += al(a[0], a[1] + 18, "振動") + lab(b[0] + 6, b[1] - 4, "湯口切断", "start") + lab(d[0] - 10, d[1] - 8, "砂", "end")
    return s


# =====================================================================================
# q:blast — shot blasting: the turbine wheel flings steel shot at the casting / forging turning
# on its hanger; scale, sand and burrs are knocked off
# =====================================================================================
@picto("blast")
def _():
    def fn(sc):
        BOX(sc, -150, -40, 20, 70, 80, 70, "pt", dark=1)                        # wheel housing
        CYL(sc, (-80, 0, 55), (1, 0, 0), 26, 12, "dk", seg=28)                 # throwing mouth
        CYL(sc, (-150, 0, 55), (-1, 0, 0), 16, 24, "dk", seg=20)               # motor
        CYL(sc, (60, 0, 120), (0, 0, -1), 4, 60, "m", seg=12)                  # hanger rod
        CYL(sc, (60, 0, 50), (0, 0, 1), 30, 10, "w", seg=36)                   # work: flanged hub
        CYL(sc, (60, 0, 20), (0, 0, 1), 44, 30, "w", seg=40)
        CYL(sc, (60, 0, -10), (0, 0, 1), 22, 30, "w", seg=28)
        BOX(sc, -60, -70, -40, 200, 140, 10, "m")                               # floor grating

        def shot(s_):
            o = ""
            c = s_.cam
            for k in range(26):
                t = (k * 0.618) % 1
                u = (k * 0.381) % 1
                p = (-64 + 100 * t, -20 + 30 * u - 10, 55 + (u - .5) * 70 * t)
                X0, Y0 = c.xy(p)
                o += circ(X0, Y0, 1.6, "shot")
            return o
        RAW(sc, shot, ((-66, -40, 0), (20, -20, 100)), -3)
    s, sc = fit(fn, -24, 20, (24, 16, 296, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (60, 0, 12), (0, 0, 1), 58, -40, 60)
    s += arc3(cam, (-74, 0, 55), (1, 0, 0), 34, 60, 160)
    a = cam.xy((60, -58, 0))
    b = cam.xy((-115, -40, 90))
    d = cam.xy((-30, -30, 10))
    s += al(a[0] + 8, a[1] + 16, "回転", "start") + lab(b[0], b[1] - 8, "インペラ")
    s += lab(d[0], d[1] + 18, "投射材（鋼球）")
    return s


# =====================================================================================
# q:hotforge — hot forging press: the slide drives the upper die onto a white-hot billet on the
# lower die; excess metal squeezes out as flash between the dies
# =====================================================================================
@picto("hotforge")
def _():
    rod = hull(arc(-46, 0, 26, 90, 270, 10) + arc(46, 0, 15, -90, 90, 8))
    fl = hull(arc(-46, 0, 36, 90, 270, 10) + arc(46, 0, 25, -90, 90, 8))

    def fn(sc):
        BOX(sc, -130, 40, -70, 26, 40, 220, "pt", dark=1)                       # press frame (behind)
        BOX(sc, 104, 40, -70, 26, 40, 220, "pt", dark=1)
        BOX(sc, -130, -60, -70, 260, 100, 20, "pt", dark=1)                     # bolster
        BOX(sc, -92, -50, -50, 184, 90, 34, "t")                                # lower die
        Z(sc, -16, 3, banded(fl, 2), "h", .2)                                   # flash
        Z(sc, -13, 14, banded(rod, 2), "h", -.2)                                # hot forging
        BOX(sc, -92, -50, 46, 184, 90, 34, "t")                                 # upper die
        BOX(sc, -112, -56, 80, 224, 96, 34, "pt", dark=1)                       # slide
    s, sc = fit(fn, -26, 22, (40, 10, 280, 176), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    h = cam.xy((-10, 0, 10))
    s += heat(h[0] - 12, h[1] - 6, 3, 12, 14)
    s += arrow3(cam, (150, -56, 130), (150, -56, 76))
    a = cam.xy((150, -56, 104))
    b = cam.xy((-92, -50, 63))
    d = cam.xy((-92, -50, -33))
    f = cam.xy((80, -40, -14))
    s += al(a[0] + 8, a[1], "加圧", "start") + lab(b[0] - 6, b[1] + 4, "上型", "end") + lab(d[0] - 6, d[1] + 4, "下型", "end")
    s += lab(f[0] + 4, f[1] + 44, "約1,200℃の素材", "start")
    return s


def lathe(sc, x0, prof, mat="w", A=(0, 0, 1), C=(0, 0), seg=24, bias=0.0, **kw):
    """stack of cylinders along A (z or x) from x0: prof = [(r, L), ...] (r1 via (r, L, r1))."""
    p = x0
    for it in prof:
        r, L = it[0], it[1]
        O = (C[0], C[1], p) if A == (0, 0, 1) else (p, C[0], C[1])
        CYL(sc, O, A, r, L, mat, bias, seg, r1=it[2] if len(it) > 2 else None, **kw)
        p += L


# =====================================================================================
# q:coldforge — cold forging: at room temperature the punch pushes the slug into the die
# (extrusion / upsetting); several stages turn a slug into a near-net shaft
# =====================================================================================
@picto("coldforge")
def _():
    def fn(sc):
        BOX(sc, -70, -60, -50, 270, 120, 14, "pt", dark=1)                      # bolster
        BOX(sc, -50, -46, -36, 100, 92, 50, "m", ch=6)                          # die case
        CYL(sc, (0, 0, 14), (0, 0, 1), 30, 4, "t", seg=32, holes=[GE.circle_outline(11, 24, 24)])  # die insert face

        def bore(s_):
            return hole3(s_.cam, (0, 0, 18.2), (0, 0, 1), 11, "bg")
        RAW(sc, bore, ((-11, -11, 18), (11, 11, 18.3)), -1)
        CYL(sc, (0, 0, 18), (0, 0, 1), 10.5, 16, "w", seg=24, bias=-1.2)        # slug being pushed in
        CYL(sc, (0, 0, 50), (0, 0, 1), 10, 50, "t", seg=24)                     # punch
        CYL(sc, (0, 0, 100), (0, 0, 1), 26, 20, "m", seg=28)                   # punch holder
        BOX(sc, -50, -46, 120, 100, 92, 26, "pt", dark=1)                       # ram
        # stages: slug -> forward extruded -> upset head
        lathe(sc, -36, [(11, 26)], C=(100, 0), seg=20, bands=6)
        lathe(sc, -36, [(6.5, 46), (11, 16)], C=(140, 0), seg=16, bands=6)
        lathe(sc, -36, [(6.5, 46), (11, 6), (19, 7), (11, 12)], C=(180, 0), seg=16, bands=6)
    s, sc = fit(fn, -24, 22, (36, 12, 290, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-74, 0, 140), (-74, 0, 70))
    a = cam.xy((-74, 0, 110))
    t = cam.xy((10, 0, 70))
    d = cam.xy((-50, -46, -10))
    w = cam.xy((140, -20, -36))
    s += al(a[0] - 6, a[1], "常温で加圧", "end") + lab(t[0] + 14, t[1], "パンチ", "start")
    s += lab(d[0] - 6, d[1] + 4, "ダイ", "end") + lab(w[0], w[1] + 30, "素材 → 押出し → 据込み")
    return s


# =====================================================================================
# q:header — parts former (cold header): wire is cut into slugs and transferred through several
# die stations; the reciprocating ram's punches head them step by step (bolts, balls, studs)
# =====================================================================================
@picto("header")
def _():
    st = (-66, -22, 22, 66)

    def fn(sc):
        BOX(sc, 0, -92, -40, 40, 184, 80, "t")                                  # die block (stations along y)
        BOX(sc, 40, -100, -60, 30, 200, 120, "pt", dark=1)                      # frame behind the dies
        BOX(sc, -150, -86, -22, 26, 172, 44, "pt", dark=1)                      # ram
        for y in st:
            CYL(sc, (-124, y, 0), (1, 0, 0), 14, 12, "m", seg=14)               # punch holders
            CYL(sc, (-112, y, 0), (1, 0, 0), 8, 40, "t", seg=14)                # punches
        CYL(sc, (40, -130, 0), (0, 1, 0), 5, 38, "w", seg=12, bias=.5)          # wire fed in from the side
        CYL(sc, (40, -170, 0), (0, 1, 0), 5, 40, "w", seg=12, bias=.5)

        def holes(s_):
            o = ""
            for y in st:
                o += hole3(s_.cam, (-.2, y, 0), (-1, 0, 0), 9, "bg")
            return o
        RAW(sc, holes, ((-.3, -80, -10), (-.1, 80, 10)), -1)
        # part progression sticking out of each die
        lathe(sc, -14, [(6, 14)], A=(1, 0, 0), C=(st[0], 0), seg=12, bias=-2)
        lathe(sc, -14, [(8.5, 8, 6), (6, 6)], A=(1, 0, 0), C=(st[1], 0), seg=12, bias=-2)
        lathe(sc, -12, [(12, 7, 8), (6, 5)], A=(1, 0, 0), C=(st[2], 0), seg=14, bias=-2)
        X(sc, -16, 9, banded([(st[3] + 13 * math.cos(math.radians(30 + 60 * k)), 13 * math.sin(math.radians(30 + 60 * k)))
                               for k in range(6)], 1), "w", -2)
        CYL(sc, (-7, st[3], 0), (1, 0, 0), 15, 4, "w", seg=18, bias=-2)
    s, sc = fit(fn, 36, 24, (20, 18, 300, 170), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-170, 0, 44), (-110, 0, 44), both=True)
    a = cam.xy((-140, 0, 44))
    w = cam.xy((40, -180, 0))
    d = cam.xy((20, 92, 40))
    s += al(a[0], a[1] - 10, "往復（圧造）") + lab(w[0] - 4, w[1] + 18, "線材", "start")
    s += lab(d[0], d[1] - 8, "多段ダイ")
    return s


# =====================================================================================
# q:indheat — induction billet heater: billets pushed through a water-cooled copper coil are
# heated from inside by eddy currents (cold in, glowing out)
# =====================================================================================
def _helix(cam, C, A, r, x0, x1, turns, front, cls="coilcu", w=6.5):
    """screen path of the visible (front) or hidden (back) halves of a helix about the x axis."""
    o = ""
    seg = 14
    for k in range(int(turns * 2)):
        a0 = 90.0 + k * 180.0                       # k even: the half with y < 0 (toward the viewer)
        pts = []
        for j in range(seg + 1):
            a = math.radians(a0 + 180.0 * j / seg)
            x = x0 + (x1 - x0) * (k * 180.0 + 180.0 * j / seg) / (turns * 360.0)
            pts.append(cam.xy((x, C[0] + r * math.cos(a), C[1] + r * math.sin(a))))
        if (k % 2 == 0) == front:
            d = P(pts, False)
            o += path(d, "o", ' style="stroke-width:%s"' % n(w + 1.6)) + path(d, cls, ' style="stroke-width:%s"' % n(w))
    return o


@picto("indheat")
def _():
    xs = [-190, -140, -90, -40, 10, 60, 110, 160]
    cls = ["w", "w", "w", "w", "h", "h", "h", "h"]
    x0, x1, turns = -70, 120, 7

    def fn(sc):
        BOX(sc, -220, -26, -40, 440, 52, 14, "m")                               # guide rail
        for x, c in zip(xs, cls):
            CYL(sc, (x, 0, 0), (1, 0, 0), 15, 46, c, seg=24)
        CYL(sc, (-250, 0, 0), (1, 0, 0), 9, 60, "m", seg=16)                    # pusher
        RAW(sc, lambda s_: _helix(s_.cam, (0, 0), (1, 0, 0), 24, x0, x1, turns, False), ((x0, 20, -24), (x1, 24, 24)), 0)
        BOX(sc, -10, 40, -60, 60, 40, 30, "dk")                                 # HF power leads (behind)
        return _helix(sc.cam, (0, 0), (1, 0, 0), 24, x0, x1, turns, True)
    s, sc = fit(fn, -18, 22, (14, 30, 306, 166), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-250, -30, 30), (-200, -30, 30))
    a = cam.xy((-225, -30, 30))
    c = cam.xy((25, 0, 30))
    h = cam.xy((185, 0, -16))
    s += al(a[0], a[1] - 10, "送り") + lab(c[0], c[1] - 14, "誘導コイル")
    s += lab(h[0] - 14, h[1] + 26, "約1,200℃")
    return s


# =====================================================================================
# q:saw — billet cutting: the bar is clamped and the circular saw feeds down through it,
# cutting billets to a set length
# =====================================================================================
@picto("saw")
def _():
    R, zc, xc = 62, 66, 0
    teeth = []
    N = 44
    for k in range(N):
        for j, rr in ((0, R), (0.7, R - 5)):
            a = 2 * PI * (k + j) / N
            teeth.append((xc + rr * math.cos(a), zc + rr * math.sin(a)))
    blade = [(x, max(z, 17)) for x, z in teeth]
    blade = [p for i, p in enumerate(blade) if not (p[1] == 17 and blade[i - 1][1] == 17 and blade[(i + 1) % len(blade)][1] == 17)]

    def fn(sc):
        BOX(sc, -170, -40, -40, 250, 80, 16, "m")                               # roller table
        CYL(sc, (-180, 0, 0), (1, 0, 0), 18, 172, "w", seg=28)                  # bar
        CYL(sc, (-8, 0, 0), (1, 0, 0), 18, 16, "w", seg=28, bias=.1)
        BOX(sc, -48, -40, -24, 30, 18, 42, "dk", -.5)                           # vice jaws
        BOX(sc, -48, 22, -24, 30, 18, 42, "dk", .5)
        Y(sc, -2, 4, [(x, z, i // 2) for i, (x, z) in enumerate(blade)], "t", -1, lines=False)
        CYL(sc, (0, -8, zc), (0, 1, 0), 16, 5, "m", seg=20, bias=-1.2)          # flange / arbor
        CYL(sc, (0, -1, zc), (0, 1, 0), 30, 40, "pt", seg=24, bias=1, dark=1)   # gear head behind
        CYL(sc, (24, 0, -10), (1, 0, 0), 18, 52, "w", seg=28, bias=.3)          # cut billets
        CYL(sc, (92, 10, -10), (1, 0, 0), 18, 52, "w", seg=28, bias=.3)
    s, sc = fit(fn, -24, 20, (20, 12, 300, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -4, zc), (0, -1, 0), R + 10, 100, 170)
    s += arrow3(cam, (-90, -40, 150), (-90, -40, 100))
    a = cam.xy((-90, -40, 120))
    b = cam.xy((-150, -18, -16))
    d = cam.xy((118, -6, -28))
    s += al(a[0] - 6, a[1], "送り", "end") + lab(b[0], b[1] + 22, "棒鋼") + lab(d[0], d[1] + 22, "定寸に切断")
    return s


# =====================================================================================
# q:upset — electric upsetting: current through the bar end between clamp and anvil electrodes
# heats it; pushing the bar in gathers the hot metal into a bulb (engine-valve head)
# =====================================================================================
@picto("upset")
def _():
    def bulb(t):
        return 1 + 1.9 * math.sin(PI * min(1, t * 1.15)) ** .8 if t < .87 else 1 + 1.9 * .75

    def fn(sc):
        CYL(sc, (-200, 0, 0), (1, 0, 0), 9, 170, "w", seg=20)                   # bar
        CYL(sc, (-30, 0, 0), (1, 0, 0), 9, 20, "h", seg=20)
        sc.add(compact(GE.prism(sc.cam, (-10, 0, 0), (1, 0, 0), GE.circle_outline(9, 24, 8), 46, "h", smooth=True, scale=bulb)),
               ((-10, -26, -26), (36, 26, 26)), 0)
        BOX(sc, -110, -30, 9, 50, 60, 24, "cu")                                 # clamp electrodes
        BOX(sc, -110, -30, -33, 50, 60, 24, "cu")
        BOX(sc, 36, -46, -50, 30, 92, 100, "cu")                                # anvil electrode
        BOX(sc, 66, -50, -54, 40, 100, 108, "pt", dark=1)
        CYL(sc, (-250, 0, 0), (1, 0, 0), 22, 50, "dk", seg=24)                  # push cylinder
    s, sc = fit(fn, -26, 20, (20, 26, 300, 168), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-190, -40, -40), (-130, -40, -40))
    a = cam.xy((-160, -40, -40))
    e = cam.xy((-85, -30, 33))
    h = cam.xy((10, -26, 26))
    s += al(a[0], a[1] + 18, "押込み") + lab(e[0], e[1] - 22, "電極")
    h = cam.xy((0, -26, -30))
    s += lab(h[0], h[1] + 18, "通電で加熱")
    return s


def _sorted(cam, items):
    """items: [(world centre, svg)] -> svg drawn far to near (for hand-ordered assemblies)."""
    return "".join(s for _, s in sorted(((cam.P(c)[2], s) for c, s in items), key=lambda t: -t[0]))


def _cyl_svg(cam, O, A, r, h, mat, seg=24, r1=None, **kw):
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, 12), h, mat, smooth=True, scale=scale, **kw))


# =====================================================================================
# q:ringroll — ring rolling: the hot pierced ring is squeezed between the driven main roll
# (outside) and the mandrel (inside); its wall thins and the diameter grows, while the conical
# axial rolls hold the height
# =====================================================================================
@picto("ringroll")
def _():
    ro, ri, hr = 72, 52, 30
    a20 = math.radians(20)

    def fn(sc):
        def draw(s_):
            cam = s_.cam
            items = []
            N = 16
            for k in range(N):
                a0, a1 = 360.0 * k / N, 360.0 * (k + 1) / N
                q = [(rr * math.cos(math.radians(a)), rr * math.sin(math.radians(a))) for rr, a in ((ri, a0), (ro, a0), (ro, a1), (ri, a1))]
                am = math.radians((a0 + a1) / 2)
                items.append(((ro * math.cos(am), ro * math.sin(am), hr / 2), zprism(cam, (0, 0), 0, hr, q, "h", lines=False)))
            items.append(((-ri + 13, 0, hr / 2), _cyl_svg(cam, (-ri + 13, 0, -26), (0, 0, 1), 12, 90, "t", 20)))      # mandrel
            items.append(((-ro - 40, 0, hr / 2), _cyl_svg(cam, (-ro - 40, 0, -40), (0, 0, 1), 40, 110, "t", 36)))   # main roll
            r0 = 8
            for sz in (1, -1):                                                                        # axial cones
                A = (math.cos(a20), 0, sz * math.sin(a20))
                O = (40 - r0 * math.sin(a20), 0, (hr + 1 + r0 * math.cos(a20)) if sz > 0 else (-1 - r0 * math.cos(a20)))
                items.append(((O[0] + 35, 0, O[2]), _cyl_svg(cam, O, A, r0, 80, "t", 24, r1=r0 + 80 * math.tan(a20))))
            return _sorted(cam, items)
        RAW(sc, draw, ((-155, -72, -40), (120, 72, 70)), 0)
    s, sc = fit(fn, -30, 24, (30, 14, 290, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, hr), (0, 0, 1), ro + 12, 20, 80)
    s += arrow3(cam, (-ri + 28, -30, 88), (-ri - 4, -30, 88))
    m = cam.xy((-ro - 40, -40, 70))
    d = cam.xy((-ri + 12, -30, 88))
    w = cam.xy((50, -ro, 0))
    s += lab(m[0], m[1] - 16, "主ロール") + lab(d[0] + 22, d[1] - 4, "マンドレル", "start")
    s += al(w[0] + 2, w[1] + 22, "径が広がる", "start")
    return s


# =====================================================================================
# q:straighten — straightening: the shaft turns on two supports while a probe reads its runout;
# the press pushes the high spot down until the shaft is straight
# =====================================================================================
@picto("straighten")
def _():
    def fn(sc):
        BOX(sc, -170, -40, -76, 340, 80, 14, "pt", dark=1)                      # bed
        for x in (-120, 120):
            Y(sc, -24, 48, [(x - 18, -62), (x + 18, -62), (x + 18, -22), (x + 8, -12), (x - 8, -12), (x - 18, -22)], "dk")   # V-block supports
        lathe(sc, -170, [(12, 30), (16, 70), (18, 140), (16, 70), (12, 30)], A=(1, 0, 0), C=(0, 0), seg=28)          # shaft
        BOX(sc, -40, -34, 64, 80, 68, 60, "pt", dark=1)                           # press ram
        Y(sc, -14, 28, [(-12, 18), (12, 18), (18, 34), (18, 64), (-18, 64), (-18, 34)], "t", -.5)    # pressing tip
        CYL(sc, (64, -16, -62), (0, 0, 1), 3, 44, "t", seg=10, bias=-.5)          # probe
        BOX(sc, 54, -26, -62, 20, 20, 22, "m", -.4)
    s, sc = fit(fn, -24, 18, (24, 18, 296, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-62, -34, 130), (-62, -34, 84))
    s += arc3(cam, (176, 0, 0), (1, 0, 0), 22, 110, 220)
    a = cam.xy((-62, -34, 108))
    p = cam.xy((64, -26, -50))
    r = cam.xy((176, -22, 0))
    s += al(a[0] - 6, a[1], "押して矯正", "end") + lab(p[0] + 16, p[1] + 32, "振れ測定", "start")
    s += al(r[0], r[1] + 26, "回転")
    return s


# =====================================================================================
# q:draw — wire drawing: the capstan pulls the wire through a carbide die; it comes out thinner
# (the die hole is smaller than the incoming wire)
# =====================================================================================
@picto("draw")
def _():
    def fn(sc):
        BOX(sc, -60, -40, -46, 300, 120, 12, "pt", dark=1)                       # bench
        CYL(sc, (-200, 0, 0), (1, 0, 0), 7, 190, "w", seg=20)                    # incoming wire (thick)
        BOX(sc, -10, -34, -34, 40, 68, 68, "m", ch=4)                            # die box
        CYL(sc, (-11, 0, 0), (1, 0, 0), 20, 1, "t", seg=28, bias=-.3)            # die nib face
        CYL(sc, (30, 0, 0), (1, 0, 0), 4, 100, "w", seg=16)                      # drawn wire (thin)
        CYL(sc, (130, 50, -34), (0, 0, 1), 52, 68, "m", seg=48)                  # capstan drum
        CYL(sc, (130, 50, 34), (0, 0, 1), 60, 6, "m", seg=48)
        CYL(sc, (130, 50, -40), (0, 0, 1), 60, 6, "dk", seg=48)

        def turns(s_):
            o = ""
            c = s_.cam
            for k in range(7):
                z = -26 + k * 8.4
                pts = [c.xy((130 + 54 * math.cos(math.radians(a)), 50 + 54 * math.sin(math.radians(a)), z)) for a in range(180, 361, 12)]
                o += path(P(pts, False), "o", ' style="stroke-width:5.6"') + path(P(pts, False), "strip", ' style="stroke-width:4"')
            return o
        RAW(sc, turns, ((76, -4, -30), (184, -3, 30)), -2)

        def nib(s_):
            return hole3(s_.cam, (-11.2, 0, 0), (-1, 0, 0), 7.5, "bg") + hole3(s_.cam, (-11.3, 0, 0), (-1, 0, 0), 4.4, "w")
        RAW(sc, nib, ((-11.4, -8, -8), (-11.2, 8, 8)), -1)
    s, sc = fit(fn, 26, 20, (18, 20, 302, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-130, -20, 22), (-70, -20, 22))
    s += arc3(cam, (130, 50, 46), (0, 0, 1), 70, 250, 330)
    d = cam.xy((10, -34, 34))
    w = cam.xy((-170, 0, -10))
    c = cam.xy((150, 0, -46))
    s += lab(d[0] - 6, d[1] - 8, "ダイス") + lab(w[0], w[1] + 20, "線材") + lab(c[0] + 10, c[1] + 22, "キャプスタン（巻取り）")
    a = cam.xy((-100, -20, 22))
    s += al(a[0], a[1] - 10, "引抜き")
    return s


# =====================================================================================
# q:bend — CNC pipe bender (rotary draw): the clamp holds the pipe to the grooved bend die,
# which turns and draws the pipe around it; the pressure die backs the straight side
# =====================================================================================
@picto("bend")
def _():
    Rc, rp = 58, 9

    def fn(sc):
        def draw(s_):
            cam = s_.cam
            items = []
            items.append(((0, 0, 0), _cyl_svg(cam, (0, 0, -26), (0, 0, 1), Rc - rp + 1, 52, "t", 28)
                          + _cyl_svg(cam, (0, 0, rp), (0, 0, 1), Rc + 10, 8, "t", 36)))
            items.append(((0, 0, -30), _cyl_svg(cam, (0, 0, -30), (0, 0, 1), Rc + 10, 21, "t", 36)))
            items.append(((0, 0, 60), _cyl_svg(cam, (0, 0, 17), (0, 0, 1), 16, 30, "m", 20)))
            for x0 in (-200, -150, -100, -50):                                       # straight, fed in +x
                items.append(((x0 + 25, -Rc, 0), _cyl_svg(cam, (x0, -Rc, 0), (1, 0, 0), rp, 50, "w", 14)))
            K = 9
            for k in range(K):                                                       # bent part around the die
                a0 = -90 + 90.0 * k / K
                a1 = -90 + 90.0 * (k + 1) / K
                p0 = (Rc * math.cos(math.radians(a0)), Rc * math.sin(math.radians(a0)), 0)
                p1 = (Rc * math.cos(math.radians(a1)), Rc * math.sin(math.radians(a1)), 0)
                A = tuple(p1[i] - p0[i] for i in range(3))
                L = math.sqrt(sum(a * a for a in A))
                items.append((tuple((p0[i] + p1[i]) / 2 for i in range(3)), _cyl_svg(cam, p0, A, rp, L + .6, "w", 14, lines=k == K - 1)))
            items.append(((Rc, 40, 0), _cyl_svg(cam, (Rc, 0, 0), (0, 1, 0), rp, 80, "w", 14)))
            items.append(((Rc + 26, 34, 0), zprism(cam, (0, 0), -14, 28, [(Rc + rp, 4), (Rc + rp + 22, 4), (Rc + rp + 22, 64), (Rc + rp, 64)], "dk")))
            items.append(((-90, -Rc - rp - 12, 0), zprism(cam, (0, 0), -14, 22, [(-140, -Rc - rp - 22), (-30, -Rc - rp - 22), (-30, -Rc - rp - 1), (-140, -Rc - rp - 1)], "dk")))
            return _sorted(cam, items)
        RAW(sc, draw, ((-200, -95, -30), (90, 80, 47)), 0)
    s, sc = fit(fn, -26, 30, (20, 16, 300, 176), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 20), (0, 0, 1), Rc + 22, 10, 100)
    s += arrow3(cam, (-200, -Rc, 24), (-150, -Rc, 24))
    a = cam.xy((-175, -Rc, 24))
    r = cam.xy((49, -85, 0))
    d = cam.xy((-20, Rc + 10, 20))
    w = cam.xy((Rc + 12, 80, 12))
    s += al(a[0], a[1] - 10, "送り") + al(r[0] + 4, r[1] + 14, "曲げ", "start")
    s += lab(d[0] - 4, d[1] - 8, "曲げ型", "end") + lab(w[0] + 4, w[1] - 6, "パイプ", "start")
    return s


def _spring(cam, C, A, r, L, turns, near, rw=4.0, cls="strip"):
    """helix wire (radius r, length L along A from C) as a stroked tube: only the runs on the near
    (near=True) or far side of the axis, so solids can be drawn between the two passes."""
    E1, E2, A = GE.frame(A)
    N = int(turns * 24)
    w = 2 * rw * cam.s
    runs, cur, flag = [], [], None
    for k in range(N + 1):
        a = 2 * PI * turns * k / N
        R = tuple(math.cos(a) * E1[i] + math.sin(a) * E2[i] for i in range(3))
        f = GE._dot(R, cam.D) < 0
        p = cam.xy(tuple(C[i] + A[i] * L * k / N + r * R[i] for i in range(3)))
        if flag is not None and f != flag:
            cur.append(p)
            runs.append((flag, cur))
            cur = []
        cur.append(p)
        flag = f
    runs.append((flag, cur))
    o = ""
    for f, pts in runs:
        if f == near and len(pts) > 1:
            d = P(pts, False)
            o += path(d, "o", ' style="stroke-width:%s;stroke-linecap:round"' % n(w + 1.4)) + path(d, cls, ' style="stroke-width:%s;stroke-linecap:round"' % n(w))
    return o


# =====================================================================================
# q:coiling — spring coiling: feed rolls push the wire through a guide against the coiling
# point, which curls it into a helix; CNC moves the tools to vary diameter and pitch
# =====================================================================================
@picto("coiling")
def _():
    xc, zc, R = 40, -30, 30

    def fn(sc):
        BOX(sc, -200, 30, -80, 300, 20, 130, "pt", dark=1)                        # machine face plate (behind)
        CYL(sc, (-210, 0, 0), (1, 0, 0), 4, 150, "w", seg=12)                     # wire in
        CYL(sc, (-10, 0, 0), (1, 0, 0), 4, 50, "w", seg=12, bias=.2)              # wire to the coil
        for x in (-160, -100):
            CYL(sc, (x, -14, 24), (0, 1, 0), 20, 28, "t", seg=28)                 # feed rolls
            CYL(sc, (x, -14, -24), (0, 1, 0), 20, 28, "t", seg=28)
            CYL(sc, (x, 14, 24), (0, 1, 0), 7, 16, "m", seg=14)
            CYL(sc, (x, 14, -24), (0, 1, 0), 7, 16, "m", seg=14)
        BOX(sc, -60, -12, -12, 50, 24, 24, "m", ch=3)                            # wire guide
        BOX(sc, xc + R + 6, -10, zc - 8, 16, 20, 16, "t", .3)                    # coiling point
        RAW(sc, lambda s_: _spring(s_.cam, (xc, 0, zc), (0, -1, 0), R, 66, 3.4, False), ((xc - R, -66, zc - R), (xc + R, 0, zc + R)), .5)
        return _spring(sc.cam, (xc, 0, zc), (0, -1, 0), R, 66, 3.4, True)
    s, sc = fit(fn, -30, 20, (22, 16, 300, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-160, -16, 24), (0, -1, 0), 26, 200, 300)
    s += arrow3(cam, (-90, -20, 58), (-40, -20, 58))
    a = cam.xy((-65, -20, 58))
    f = cam.xy((-130, -14, 50))
    w = cam.xy((-200, 0, -6))
    c = cam.xy((xc, -66, zc - R))
    s += al(a[0], a[1] - 10, "送り") + lab(f[0], f[1] - 26, "送りロール")
    s += lab(w[0], w[1] + 22, "線材") + lab(c[0], c[1] + 22, "コイルばね")
    return s


# =====================================================================================
# q:setting — spring setting (presetting): the coil spring is pressed beyond its working load
# so that the permanent sag happens now, not in the car
# =====================================================================================
@picto("setting")
def _():
    R, H = 34, 76

    def fn(sc):
        BOX(sc, -90, -70, -30, 180, 140, 16, "pt", dark=1)                        # bed
        CYL(sc, (0, 0, -14), (0, 0, 1), 46, 10, "m", seg=40)                      # lower seat
        RAW(sc, lambda s_: _spring(s_.cam, (0, 0, -.5), (0, 0, 1), R, H, 6.0, False, rw=5), ((-R, -R + 2, -4), (R, R, H)), 0)
        RAW(sc, lambda s_: _spring(s_.cam, (0, 0, -.5), (0, 0, 1), R, H, 6.0, True, rw=5), ((-R, -R, -4), (R, -R + 1, H)), -1)
        CYL(sc, (0, 0, H + 4), (0, 0, 1), 46, 10, "m", seg=40)                    # pressing plate
        CYL(sc, (0, 0, H + 14), (0, 0, 1), 16, 30, "dk", seg=24)                  # ram rod
        BOX(sc, -70, -50, H + 44, 140, 100, 30, "pt", dark=1)                     # ram head
        for x in (-78, 78):
            CYL(sc, (x, 52, -14), (0, 0, 1), 7, H + 88, "m", seg=14)              # guide posts (behind)
    s, sc = fit(fn, -24, 18, (60, 12, 262, 176), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (96, -50, H + 70), (96, -50, H + 20))
    a = cam.xy((96, -50, H + 44))
    w = cam.xy((-R - 6, -R, H / 2))
    s += al(a[0] + 8, a[1], "押し縮める", "start") + lab(w[0] - 8, w[1] + 4, "コイルばね", "end")
    return s


# =====================================================================================
# q:finform — fin forming: a thin aluminium strip runs between two toothed forming rolls and
# comes out corrugated (louvers are slit into the flanks at the same time)
# =====================================================================================
@picto("finform")
def _():
    Z_, rp, W = 12, 36, 64

    def fn(sc):
        sc.gear((0, -W / 2, rp + 1), (0, 1, 0), Z_, rp, W, "t", phase=PI / 2 + PI / Z_)          # upper roll
        sc.gear((0, -W / 2, -rp - 1), (0, 1, 0), Z_, rp, W, "t", phase=PI / 2)                   # lower roll
        for sz in (1, -1):
            CYL(sc, (0, W / 2, sz * (rp + 1)), (0, 1, 0), 9, 30, "m", seg=16)                     # shafts
        Y(sc, -30, 60, [(-210, -.7), (-36, -.7), (-36, .7), (-210, .7)], "al")                   # flat strip in
        pts = []
        x, k = 36, 0
        while x < 200:
            pts.append((x, 7 if k % 2 else -7))
            x += 7
            k += 1
        for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
            Y(sc, -30, 60, [(x0, z0 - .7), (x1, z1 - .7), (x1, z1 + .7), (x0, z0 + .7)], "al", lines=False)
    s, sc = fit(fn, -26, 20, (18, 18, 302, 174), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -W / 2 - 4, rp + 1), (0, 1, 0), rp + 16, 135, 45)
    s += arc3(cam, (0, -W / 2 - 4, -rp - 1), (0, 1, 0), rp + 16, 225, 315)
    s += arrow3(cam, (110, -34, 26), (160, -34, 26))
    r = cam.xy((0, -W / 2, 2 * rp + 18))
    a = cam.xy((-160, -30, -2))
    f = cam.xy((150, -30, -10))
    s += lab(r[0], r[1] - 8, "成形ロール") + lab(a[0], a[1] + 22, "アルミ薄板") + lab(f[0], f[1] + 26, "コルゲートフィン")
    return s


# =====================================================================================
# q:rollform — roll forming: a strip passes through a row of roll stands; each pair of rolls
# bends the edges a little further until the full section (channel / flat tube) is formed
# =====================================================================================
@picto("rollform")
def _():
    th = (0, 30, 60, 88)
    L, x0, b, f, t = 64, -130, 14, 17, 1.8

    def sect(a):
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        web = [(-b, 0), (b, 0), (b, t), (-b, t)]
        lf = [(-b, 0), (-b, t), (-b - f * c + t * s_, f * s_ + t * c), (-b - f * c, f * s_)]
        rf = [(-y, z) for y, z in lf]
        return web, lf, rf

    def fn(sc):
        for k, a in enumerate(th):
            web, lf, rf = sect(a)
            X(sc, x0 + k * L, L, web, "w")
            X(sc, x0 + k * L, L, lf, "w", lines=a > 0)
            X(sc, x0 + k * L, L, rf, "w", lines=a > 0)
        for k in range(1, len(th)):
            xb = x0 + k * L
            CYL(sc, (xb, -b + 1, t + 16), (0, 1, 0), 16, 2 * b - 2, "t", seg=20)          # upper roll (between the flanges)
            CYL(sc, (xb, -36, -16), (0, 1, 0), 16, 72, "t", seg=20)                        # lower roll
            CYL(sc, (xb, b - 1, t + 16), (0, 1, 0), 5, 61 - b, "m", seg=10)               # upper shaft (to the back)
            CYL(sc, (xb, 36, -16), (0, 1, 0), 5, 24, "m", seg=10)
            BOX(sc, xb - 12, 60, -50, 24, 14, 90, "pt", dark=1)                            # stand housing (back)
    s, sc = fit(fn, -24, 26, (16, 22, 304, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (x0 - 10, -40, 20), (x0 + 40, -40, 20))
    a = cam.xy((x0 + 15, -40, 20))
    w = cam.xy((x0 + 20, -b, 0))
    r = cam.xy((x0 + 2 * L, -36, -34))
    e = cam.xy((x0 + 4 * L, 0, 20))
    s += al(a[0], a[1] - 10, "送り") + lab(w[0], w[1] + 30, "帯板") + lab(r[0], r[1] + 22, "成形ロール（多段）")
    s += lab(e[0] + 10, e[1] - 20, "成形品", "end")
    return s
