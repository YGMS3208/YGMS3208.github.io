"""v3 principle drawings (shaded 3D style) for the equipment groups 「電子・電池・モータ」 and
「寸法・形状測定」: electrode making (mix / coat / press / slit / wind), cell assembly, e-motor winding,
electronics assembly, and dimension / shape / appearance measurement. Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3

BIG = ((-1e4, -1e4, -1e4), (1e4, 1e4, 1e4))


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


class L:
    """painter's-order proxy for a Scene: everything added through it is drawn in call order
    (all items share one bbox, so the Scene falls back to the bias, which decreases per call)."""

    def __init__(s, sc):
        s.sc, s.cam, s.k = sc, sc.cam, 0

    def add(s, svg, bb=None, bias=0.0, z=0):
        s.k += 1
        s.sc.add(svg, BIG, -s.k)

    def svg(s, v):
        s.add(v)


def P3(cam, pts, cls, close=True):
    return path(P([cam.xy(p) for p in pts], close), cls)


def strip(cam, prs, mat, dark=0, edge=True):
    """thin strip (foil / electrode / film / glass) given as a list of (left, right) 3D edge-point pairs
    along its length. Each segment is shaded by the side that faces the camera."""
    segs = []
    for (a0, b0), (a1, b1) in zip(prs, prs[1:]):
        u = tuple(a1[i] - a0[i] for i in range(3))
        v = tuple(b0[i] - a0[i] for i in range(3))
        nr = GE._norm(GE._cross(u, v))
        if GE._dot(nr, cam.D) > 0:
            nr = tuple(-c for c in nr)
        sh = GE.shade(nr, dark)
        c = tuple((a0[i] + a1[i] + b0[i] + b1[i]) / 4 for i in range(3))
        segs.append((cam.P(c)[2], P3(cam, [a0, a1, b1, b0], "%ss%d" % (mat, sh))))
    o = "".join(v for _, v in sorted(segs, key=lambda t: -t[0]))
    if edge:
        o += path(P([cam.xy(p[0]) for p in prs], False) + P([cam.xy(p[1]) for p in prs], False), "el")
    return o


def band(cam, pts, y0, y1, mat, dark=0, edge=True):
    """strip running in the x-z plane through pts [(x, z) or (x, z, y0, y1)], spanning y0..y1."""
    pp = [(p[0], p[1], p[2], p[3]) if len(p) > 2 else (p[0], p[1], y0, y1) for p in pts]
    return strip(cam, [((x, a, z), (x, b, z)) for x, z, a, b in pp], mat, dark, edge)


def bandx(cam, pts, x0, x1, mat, dark=0, edge=True):
    """strip running in the y-z plane through pts [(y, z) or (y, z, x0, x1)], spanning x0..x1."""
    pp = [(p[0], p[1], p[2], p[3]) if len(p) > 2 else (p[0], p[1], x0, x1) for p in pts]
    return strip(cam, [((a, y, z), (b, y, z)) for y, z, a, b in pp], mat, dark, edge)


def YPR(sc, y0, L_, xz, mat="m", bias=0.0, **kw):
    """outline [(x, z), ...] extruded along +y from y0 (front face at y0 faces the viewer)."""
    loop = [(-p[0], p[1], i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L_, mat, **kw)),
           ((min(xs), y0, min(zs)), (max(xs), y0 + L_, max(zs))), bias)


def ball(cam, C, r, cls="probeball"):
    x, y = cam.xy(C)
    return circ(x, y, r * cam.s, cls)


def wave_mark(x, y, w=26, h=6, k=3):
    """small zig-zag (ultrasonic / signal) mark."""
    pts_ = [(x + w * i / (4 * k), y + (h if i % 2 else -h) * (0 if i in (0, 4 * k) else 1)) for i in range(4 * k + 1)]
    return path(P(pts_, False), "a")


def stad(a, r, cx=0.0, cz=0.0, seg=10):
    """flat-oval (stadium) outline: half-length a between the arc centres, radius r."""
    return arc(cx + a, cz, r, -90, 90, seg) + arc(cx - a, cz, r, 90, 270, seg)




# =====================================================================================
# q:coater — slot-die coating on a backing roll, then into the drying oven
# =====================================================================================
@picto("coater")
def _():
    R, W = 24, 70

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        CYL(l, (-110, -8, 0), (0, 1, 0), 8, W + 16, "dk", seg=20)               # unwind core shaft
        CYL(l, (-110, 0, 0), (0, 1, 0), R, W, "alu", seg=40, dark=.3)                    # foil coil
        CYL(l, (0, -8, 0), (0, 1, 0), R, W + 16, "m", seg=40)                   # backing roll
        l.svg(band(cam, [(-110, R), (190, R)], 0, W, "alu"))                    # bare foil
        l.svg(band(cam, [(0, R + .3), (190, R + .3)], 6, W - 6, "dk"))          # coated layer
        YPR(l, 2, W - 4, [(-15, 60), (-15, 42), (-3, R + 5), (3, R + 5), (15, 42), (15, 60)], "t")   # slot die
        CYL(l, (0, W / 2, 60), (0, 0, 1), 5, 20, "m", seg=16)                    # slurry feed
        BOX(l, 84, -14, -16, 110, W + 28, 82, "pt", dark=1)                     # drying oven
        l.svg(P3(cam, [(84, 0, R - 3), (84, W, R - 3), (84, W, R + 4), (84, 0, R + 4)], "bg"))
    s, sc = fit(fn, 22, 22, (16, 26, 304, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-110, -2, 0), (0, 1, 0), R + 9, 110, 20)
    s += arrow3(cam, (-74, -6, R + 2), (-26, -6, R + 2))
    for x in (116, 160):
        a = cam.xy((x, 20, 70))
        s += heat(a[0], a[1] - 4, 1)
    d = cam.xy((-15, 0, 56))
    o = cam.xy((140, -14, -16))
    c = cam.xy((-110, -8, -R))
    s += lab(d[0] - 10, d[1] - 10, "スロットダイ", "end") + lab(o[0], o[1] + 16, "乾燥炉")
    s += lab(c[0], c[1] + 16, "金属箔")
    return s


# =====================================================================================
# q:cmm — bridge-type coordinate measuring machine: bridge (Y), carriage (X), ram (Z), touch probe
# =====================================================================================
@picto("cmm")
def _():
    yb, xc = 6, -14

    def fn(sc):
        BOX(sc, -110, -70, -54, 220, 140, 30, "pt", dark=1)                    # stand
        BOX(sc, -118, -78, -24, 236, 156, 24, "dk", ch=3)                      # granite table
        BOX(sc, -64, -36, 0, 100, 74, 34, "w", ch=4)                           # work
        for x in (-104, 84):                                                   # bridge legs
            BOX(sc, x, yb - 13, 0, 20, 26, 132, "pt", dark=1)
        BOX(sc, -112, yb - 12, 132, 224, 24, 22, "pt")                         # bridge beam
        BOX(sc, xc - 18, yb - 26, 122, 36, 13, 40, "m", ch=2)                  # carriage
        BOX(sc, xc - 7, yb - 25, 66, 14, 12, 56, "pt")                         # Z ram
        CYL(sc, (xc, yb - 19, 54), (0, 0, 1), 7, 12, "dk", seg=20)             # probe head
        CYL(sc, (xc, yb - 19, 41), (0, 0, 1), 1.6, 13, "t", seg=10)            # stylus

        def holes(s_):
            return hole3(s_.cam, (-34, 4, 34.2), (0, 0, 1), 11) + hole3(s_.cam, (6, -14, 34.2), (0, 0, 1), 5)
        RAW(sc, holes, ((-64, -36, 34), (36, 38, 34.3)), -1)
    s, sc = fit(fn, 26, 20, (40, 30, 270, 176), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += ball(cam, (xc, yb - 19, 38), 3.2)
    s += arrow3(cam, (-60, yb - 12, 170), (40, yb - 12, 170), both=True)
    s += arrow3(cam, (118, -40, 0), (118, 50, 0), both=True)
    s += arrow3(cam, (xc + 22, yb - 25, 70), (xc + 22, yb - 25, 112), both=True)
    a = cam.xy((-10, yb - 12, 170))
    b = cam.xy((118, 56, 0))
    c = cam.xy((xc + 22, yb - 25, 92))
    p = cam.xy((xc - 9, yb - 25, 70))
    s += al(a[0], a[1] - 8, "X") + al(b[0] + 8, b[1] + 4, "Y", "start") + al(c[0] + 8, c[1] + 4, "Z", "start")
    s += lab(p[0] - 6, p[1] + 2, "プローブ", "end")
    return s


# =====================================================================================
# q:rollpress — calender: the coated electrode is squeezed between two large rolls
# =====================================================================================
@picto("rollpress")
def _():
    R, W, t0, t1 = 36, 80, 6, 3.2           # roll radius, web width, half-thickness in / out

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -64, W + 14, -R * 2 - 26, 128, 16, R * 4 + 40, "pt", dark=1)      # housing (behind)
        for z in (-R - t1, R + t1):
            CYL(l, (0, W + 10, z), (0, 1, 0), 18, 6, "dk", seg=24)              # bearing caps
        CYL(l, (0, -10, -R - t1), (0, 1, 0), R, W + 20, "m", seg=48)          # lower roll
        xs = range(32, -1, -4)
        top = [(-180, t0)] + [(-x, max(t1, R + t1 - math.sqrt(R * R - x * x))) for x in xs if R + t1 - math.sqrt(R * R - x * x) < t0] + [(180, t1)]
        l.svg(band(cam, top, 0, W, "dk"))
        # front edge: the coated foil in section, thick before the nip and thinner after it
        l.svg(P3(cam, [(x, 0, z) for x, z in top] + [(x, 0, -z) for x, z in top[::-1]], "dk"))
        l.svg(P3(cam, [(-180, 0, .8), (180, 0, .8), (180, 0, -.8), (-180, 0, -.8)], "alu"))
        CYL(l, (0, -10, R + t1), (0, 1, 0), R, W + 20, "m", seg=48)           # upper roll
        BOX(l, -22, W / 2 - 34, R * 2 + t1 + 34, 44, 40, 30, "pt", ch=3)        # press cylinder
        CYL(l, (0, W / 2 - 14, R * 2 + t1 + 4), (0, 0, 1), 9, 30, "dk", seg=20)   # rod
    s, sc = fit(fn, 22, 16, (22, 22, 300, 182), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-40, -14, R * 2 + 64), (-40, -14, R * 2 + 18))
    s += arc3(cam, (0, -12, R + t1), (0, 1, 0), R + 8, 130, 200)
    s += arc3(cam, (0, -12, -R - t1), (0, 1, 0), R + 8, 50, -20)
    a = cam.xy((-40, -14, R * 2 + 44))
    b = cam.xy((-180, 0, -t0))
    c = cam.xy((180, 0, t1))
    s += al(a[0] - 8, a[1] + 4, "加圧", "end")
    s += lab(b[0] + 2, b[1] - 36, "塗工した電極", "start") + lab(c[0] - 2, c[1] + 20, "薄く・高密度に", "end")
    return s


# =====================================================================================
# q:slitter — rotary shear slitting: upper disc knives against the lower knife roll cut the web into
# lanes (web runs towards the viewer)
# =====================================================================================
@picto("slitter")
def _():
    W, R, cuts, g = 96, 26, (32, 64), 6

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        CYL(l, (-14, 0, -R), (1, 0, 0), R, W + 28, "m", seg=40)                 # lower knife roll
        l.svg(bandx(cam, [(150, 0), (0, 0)], 0, W, "alu", edge=False))
        l.svg(bandx(cam, [(150, .3), (0, .3)], 5, W - 5, "dk"))
        lanes = [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], W)]
        for i, (a, b) in enumerate(lanes):
            d = (i - 1) * g
            a2, b2 = max(a, 5), min(b, W - 5)
            l.svg(bandx(cam, [(0, 0, a, b), (-40, 0, a + d, b + d), (-130, 0, a + d, b + d)], 0, 0, "alu"))
            l.svg(bandx(cam, [(0, .3, a2, b2), (-40, .3, a2 + d, b2 + d), (-130, .3, a2 + d, b2 + d)], 0, 0, "dk", edge=False))
        CYL(l, (-14, 0, R - 4), (1, 0, 0), 6, W + 28, "dk", seg=16)             # upper knife shaft
        for x in cuts:
            CYL(l, (x - 10, 0, R - 4), (1, 0, 0), 14, 8, "m", seg=28)           # knife hub
            CYL(l, (x - 1.5, 0, R - 4), (1, 0, 0), R + 2, 3, "t", seg=48)       # disc knife
    s, sc = fit(fn, 34, 26, (20, 28, 300, 176), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (W + 18, 0, R - 4), (1, 0, 0), R + 4, 20, -70)
    s += arrow3(cam, (W + 14, 130, 2), (W + 14, 70, 2))
    k = cam.xy((cuts[0], 0, 2 * R + 6))
    o = cam.xy((-14, 0, -2 * R))
    e = cam.xy((W + 6, -130, 0))
    s += lab(k[0] - 10, k[1] - 14, "丸刃") + lab(o[0] - 6, o[1] + 6, "下刃ロール", "end")
    s += lab(e[0] + 4, e[1] + 20, "製品幅に", "end")
    return s


# =====================================================================================
# q:winder — flat winding: cathode, separator, anode, separator are wound onto a flat mandrel
# =====================================================================================
@picto("winder")
def _():
    a, r = 34, 22
    tip = (-a, r)

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        l.svg(band(cam, [(-160, 6), tip], -4, 72, "w", dark=.35))                    # separator (lower)
        l.svg(band(cam, [(-160, 34), tip], -12, 64, "cu"))                             # anode (copper)
        l.svg(band(cam, [(-160, 34.6), (tip[0], tip[1] + .5)], 4, 64, "dk", edge=False))
        l.svg(band(cam, [(-160, 62), tip], -4, 72, "w", dark=.35))                   # separator
        l.svg(band(cam, [(-160, 90), tip], 6, 80, "alu"))                             # cathode (aluminium)
        l.svg(band(cam, [(-160, 90.6), (tip[0], tip[1] + .6)], 6, 66, "dk", edge=False))
        # jelly roll: aluminium foil bundle at the back end, separator wrap, copper bundle at the front end
        YPR(l, 66, 14, banded(stad(a, r - 3), 2), "alu", smooth=True)
        YPR(l, -4, 70, banded(stad(a, r), 2), "w", smooth=True, dark=.2)
        YPR(l, -12, 8, banded(stad(a, r - 3), 2), "cu", smooth=True)
        YPR(l, -26, 14, [(-a + 6, -4), (a - 6, -4), (a - 6, 4), (-a + 6, 4)], "dk")   # flat mandrel
    s, sc = fit(fn, 24, 20, (14, 22, 292, 180), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -14, 0), (0, 1, 0), a + r + 10, 70, -60)
    p = cam.xy((-160, 6, 90))
    q = cam.xy((-160, -4, 62))
    n_ = cam.xy((-160, -12, 34))
    m = cam.xy((a, -26, -r))
    s += lab(p[0] + 4, p[1] - 6, "正極", "start") + lab(q[0] + 2, q[1] - 4, "セパレータ", "start")
    s += lab(n_[0] + 2, n_[1] + 14, "負極", "start") + al(m[0] + 10, m[1] + 14, "巻回", "start")
    return s


# =====================================================================================
# q:thick — inline areal-weight / thickness gauge: beta / X-ray source above, detector below,
# the O-frame head traverses across the moving electrode
# =====================================================================================
@picto("thick")
def _():
    W, yh = 100, 40

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -18, W + 22, -62, 36, 18, 124, "pt", dark=1)                     # back post
        BOX(l, -18, -40, -62, 36, W + 80, 18, "pt", dark=1)                     # lower beam
        BOX(l, -15, yh - 14, -44, 30, 28, 34, "dk", ch=3)                       # detector
        l.svg(band(cam, [(-150, 0), (150, 0)], 0, W, "alu"))
        l.svg(band(cam, [(-150, .3), (150, .3)], 6, W - 6, "dk", edge=False))
        BOX(l, -18, -40, 44, 36, W + 80, 18, "pt", dark=1)                      # upper beam
        BOX(l, -15, yh - 14, 14, 30, 28, 30, "m", ch=3)                         # source head
        CYL(l, (0, yh, 9), (0, 0, 1), 7, 5, "dk", seg=16)                        # window
        l.svg(path(P([cam.xy((0, yh, 9)), cam.xy((0, yh, .4))], False), "ray"))
        BOX(l, -18, -40, -44, 36, 18, 88, "pt", dark=1)                          # front post
    s, sc = fit(fn, 26, 22, (22, 26, 298, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, 2, 76), (0, W + 30, 76), both=True)
    s += arrow3(cam, (-140, -10, 4), (-80, -10, 4))
    t = cam.xy((0, W + 30, 76))
    so = cam.xy((-15, yh - 14, 34))
    de = cam.xy((-15, yh - 14, -38))
    e = cam.xy((150, 0, 0))
    s += al(t[0] + 8, t[1] + 2, "走査", "start") + lab(so[0] - 8, so[1] + 2, "線源", "end")
    s += lab(de[0] - 6, de[1] + 8, "検出器", "end") + lab(e[0] - 6, e[1] + 18, "電極", "end")
    return s


def twisted(cam, C, z0, h, u0, u1, w, tw, mat="t", slices=6):
    """bar of section (u0..u1) x (-w..w) around the vertical axis through C, twisted by tw (rad) over h."""
    ol = [(u0, -w, 0), (u1, -w, 1), (u1, w, 2), (u0, w, 3)]
    return compact(GE.prism(cam, (C[0], C[1], z0), (0, 0, 1), ol, h, mat, twist=tw, slices=slices))


def half_ring(cam, C, z0, h, ro, ri, mat, a0=180, a1=360, seg=18, dark=0):
    """front half of a thin-walled vessel (angles in the x-y plane, 270 = towards the viewer)."""
    pts_ = [(C[0] + ro * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), C[1] + ro * math.sin(math.radians(a0 + (a1 - a0) * k / seg))) for k in range(seg + 1)]
    pin = [(C[0] + ri * math.cos(math.radians(a1 - (a1 - a0) * k / seg)), C[1] + ri * math.sin(math.radians(a1 - (a1 - a0) * k / seg))) for k in range(seg + 1)]
    ol = [(-y, x, i // 3) for i, (x, y) in enumerate(pts_ + pin)]
    return compact(GE.prism(cam, (0, 0, z0), (0, 0, 1), ol, h, mat, smooth=True, dark=dark))


# =====================================================================================
# q:slurrymix — planetary mixer: two twisted blades spin on their own axes while revolving in the bowl
# =====================================================================================
@picto("slurrymix")
def _():
    Ro, Ri, H, lv = 62, 57, 72, 50

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        CYL(l, (0, 0, -14), (0, 0, 1), 46, 14, "pt", seg=40, dark=1)            # base
        RING(l, (0, 0, 0), (0, 0, 1), Ro, Ri, H, "m", seg=36)                   # bowl
        l.svg(path(P(circ3(cam, (0, 0, lv), (0, 0, 1), Ri, 40)), "dks3"))       # slurry surface
        for bx, ph in ((-24, 0.0), (24, 1.6)):
            for sg in (1, -1):
                l.svg(twisted(cam, (bx, 0), lv, 112 - lv, 6 * sg, 15 * sg, 2.6, 2.4 * sg if bx < 0 else -2.4 * sg))
            CYL(l, (bx, 0, 112), (0, 0, 1), 5, 16, "m", seg=16)
        l.svg(half_ring(cam, (0, 0), 0, H, Ro, Ri, "m"))                        # front wall over the slurry
        BOX(l, -44, -12, 128, 88, 24, 16, "pt", ch=4)                            # planetary arm
        CYL(l, (0, 0, 144), (0, 0, 1), 18, 30, "dk", seg=28)                    # drive
    s, sc = fit(fn, -28, 26, (40, 18, 280, 180), sh_ry=7, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 136), (0, 0, 1), 66, 200, 330)
    s += arc3(cam, (24, 0, 92), (0, 0, 1), 22, -20, 200)
    a = cam.xy((66 * math.cos(math.radians(210)), 66 * math.sin(math.radians(210)), 136))
    b = cam.xy((46, 0, 96))
    c = cam.xy((Ro, 0, 10))
    s += al(a[0] - 6, a[1] + 4, "公転", "end") + al(b[0] + 14, b[1] + 4, "自転", "start")
    s += lab(c[0] + 8, c[1] + 4, "スラリー", "start")
    return s


# =====================================================================================
# q:efill — electrolyte filling: the nozzle seals on the fill port, then vacuum and pressure
# cycles drive the electrolyte into the wound electrodes (front of the can cut away)
# =====================================================================================
@picto("efill")
def _():
    a, d, h = 46, 16, 96

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -a - 10, -d - 10, -10, 2 * a + 20, 2 * d + 20, 10, "pt", dark=1)     # pallet
        BOX(l, -a, -d, 0, 2 * a, 2 * d, h, "alu", ch=3)                             # can
        # cut-away window on the front face: jelly roll inside, electrolyte rising
        y = -d - .2
        l.svg(P3(cam, [(-a + 8, y, 8), (a - 8, y, 8), (a - 8, y, h - 10), (-a + 8, y, h - 10)], "bg"))
        l.svg(P3(cam, [(-a + 12, y, 10), (a - 12, y, 10), (a - 12, y, h - 14), (-a + 12, y, h - 14)], "ws2"))
        for k in range(1, 6):
            xx = -a + 12 + k * (2 * a - 24) / 6
            l.svg(path(P([cam.xy((xx, y, 10)), cam.xy((xx, y, h - 14))], False), "gr"))
        l.svg(P3(cam, [(-a + 8, y, 8), (a - 8, y, 8), (a - 8, y, 46), (-a + 8, y, 46)], "fl"))
        for x, m in ((-30, "alu"), (30, "cu")):
            BOX(l, x - 8, -7, h, 16, 14, 6, m)                                       # terminals
        CYL(l, (0, 0, h), (0, 0, 1), 9, 6, "dk", seg=20)                             # seal cup
        CYL(l, (0, 0, h + 6), (0, 0, 1), 6, 26, "t", seg=16)                          # nozzle
        BOX(l, -22, -16, h + 32, 44, 32, 30, "pt", ch=3)                             # valve block
        CYL(l, (22, 0, h + 47), (1, 0, 0), 5, 46, "m", seg=14)                        # vacuum / pressure line
        CYL(l, (0, 0, h + 62), (0, 0, 1), 5, 26, "m", seg=14)                         # electrolyte line
    s, sc = fit(fn, -26, 22, (40, 18, 266, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    e = cam.xy((68, 0, h + 47))
    s += arrow(e[0] + 4, e[1], e[0] + 36, e[1], None, both=True)
    f = cam.xy((0, 0, h + 88))
    s += arrow(f[0] - 14, f[1] - 6, f[0] - 14, f[1] + 30, None)
    w = cam.xy((-a, -d, 26))
    c = cam.xy((a, -d, 4))
    s += al(e[0] + 20, e[1] - 10, "真空⇄加圧") + lab(f[0] - 20, f[1] + 4, "電解液", "end")
    s += lab(w[0] - 6, w[1], "電極", "end") + lab(c[0] + 8, c[1] + 6, "電池缶", "start")
    return s


# =====================================================================================
# q:formation — formation / charge-discharge: probe pins contact every cell's terminals,
# a multi-channel power unit charges and discharges them
# =====================================================================================
@picto("formation")
def _():
    nx, cw, cd, ch = 6, 13, 44, 54

    def fn(sc):
        BOX(sc, -8, -32, -10, nx * 18 + 16, 2 * cd + 30, 10, "dk")                 # tray
        for j, y0 in enumerate((-26, cd - 10)):
            for i in range(nx):
                x0 = i * 18
                BOX(sc, x0, y0, 0, cw, cd - 6, ch, "alu")
                for yy, m in ((y0 + 6, "alu"), (y0 + cd - 18, "cu")):
                    BOX(sc, x0 + 2.5, yy, ch, 8, 6, 3, m)
        def pins(s_):
            o = ""
            for y0 in (-26, cd - 10):
                for i in range(nx):
                    for yy in (y0 + 9, y0 + cd - 15):
                        a, b = s_.cam.xy((i * 18 + 6.5, yy, ch + 3)), s_.cam.xy((i * 18 + 6.5, yy, ch + 36))
                        o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            return path(o, "probe")
        RAW(sc, pins, ((-8, -32, ch + 3), (nx * 18 + 8, 2 * cd, ch + 36)))
        BOX(sc, -12, -36, ch + 36, nx * 18 + 24, 2 * cd + 38, 12, "pt", ch=3)          # probe plate
        BOX(sc, nx * 18 + 60, -20, -10, 64, 74, 120, "pt", dark=1, ch=3)               # power unit

        def scr(s_):
            cam = s_.cam
            x0, x1, z0, z1, y = nx * 18 + 70, nx * 18 + 114, 64, 98, -20.2
            o = P3(cam, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], "scrn")
            cv = [(x0 + 4 + (x1 - x0 - 8) * k / 10, y, z0 + 6 + 24 * (1 - math.exp(-k / 3))) for k in range(11)]
            o += path(P([cam.xy(p) for p in cv], False), "scrg")
            for k in range(3):
                o += P3(cam, [(x0 + 4 + 14 * k, y, 30), (x0 + 12 + 14 * k, y, 30), (x0 + 12 + 14 * k, y, 46), (x0 + 4 + 14 * k, y, 46)], "dks2")
            return o
        RAW(sc, scr, ((nx * 18 + 60, -20.3, 20), (nx * 18 + 124, -20.2, 100)), -2)
    s, sc = fit(fn, -24, 26, (16, 30, 304, 174), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a = cam.xy((nx * 18 + 12, 10, ch + 42))
    b = cam.xy((nx * 18 + 60, 10, ch + 42))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] + 20), n(a[1] - 18), n(b[0] - 12), n(b[1] - 30), n(b[0]), n(b[1] - 22)), "cable")
    m = cam.xy(((nx * 18 + 60 + nx * 18 + 124) / 2, -20, 120))
    s += arrow(m[0] - 30, m[1] - 10, m[0] + 30, m[1] - 10, None, both=True)
    p = cam.xy((-12, -36, ch + 40))
    c = cam.xy((0, -26, 10))
    s += al(m[0], m[1] - 24, "充電⇄放電") + lab(p[0] - 4, p[1] - 4, "プローブ", "end")
    s += lab(c[0] - 6, c[1] + 6, "セル", "end")
    return s


def bar(cam, p0, p1, w, t, mat, rot=0.0, lines=True):
    """rectangular bar (w x t section) from p0 to p1; rot turns the section about the bar axis (deg)."""
    A = tuple(p1[i] - p0[i] for i in range(3))
    h = math.sqrt(GE._dot(A, A))
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    ol = [(u * c - v * s_, u * s_ + v * c, k) for k, (u, v) in enumerate(((-w / 2, -t / 2), (w / 2, -t / 2), (w / 2, t / 2), (-w / 2, t / 2)))]
    return compact(GE.prism(cam, p0, A, ol, h, mat, lines=lines))


def pol(r, a, z):
    return (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)


# =====================================================================================
# q:dryroom — low-dew-point room: a desiccant-rotor dehumidifier feeds very dry air into the room
# =====================================================================================
@picto("dryroom")
def _():
    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -110, -60, -8, 230, 160, 8, "pt", dark=1)                        # floor
        BOX(l, -110, 100, 0, 230, 8, 112, "pt", dark=1)                         # back wall
        BOX(l, -190, 30, -8, 56, 64, 96, "pt", ch=3)                            # dehumidifier
        CYL(l, (-162, 30, 46), (0, -1, 0), 22, 5, "dk", seg=32)                 # desiccant rotor
        l.svg(path(P(circ3(cam, (-162, 24.8, 46), (0, -1, 0), 15, 20)), "gr") + path(P(circ3(cam, (-162, 24.8, 46), (0, -1, 0), 7, 14)), "gr"))
        BOX(l, -170, 48, 88, 16, 16, 34, "m")                                    # riser
        BOX(l, -170, 48, 122, 250, 16, 14, "m")                                  # supply duct
        for x in (-50, 30):
            CYL(l, (x, 56, 110), (0, 0, 1), 9, 12, "m", seg=16)                 # diffusers
        BOX(l, -60, 10, 0, 130, 54, 40, "m", ch=2)                              # workbench
        for i in range(4):
            BOX(l, -48 + i * 20, 26, 40, 12, 22, 30, "alu")                     # cells
        CYL(l, (40, 20, 52), (0, 1, 0), 12, 30, "alu", seg=24)                  # electrode roll
        BOX(l, 112, -60, 0, 8, 168, 112, "pt", dark=1)                          # side wall
    s, sc = fit(fn, 24, 22, (18, 30, 302, 176), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (-50, 30):
        s += arrow3(cam, (x, 56, 104), (x, 56, 76))
    s += arrow3(cam, (-150, 56, 146), (-90, 56, 146))
    u = cam.xy((-162, 30, -8))
    d = cam.xy((-120, 56, 146))
    r = cam.xy((10, 100, 112))
    s += lab(u[0], u[1] + 16, "除湿機") + al(d[0], d[1] - 10, "乾燥空気")
    s += lab(r[0] + 50, r[1] - 26, "露点 −40℃以下")
    return s


# =====================================================================================
# q:hairpin — hairpin stator: U-shaped rectangular-wire pins are inserted into the core slots,
# then the leg ends under the core are twisted and welded in pairs
# =====================================================================================
@picto("hairpin")
def _():
    Ro, Ri, H, rs, ns = 72, 46, 40, 55, 30

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        RING(l, (0, 0, 0), (0, 0, 1), Ro, Ri, H, "m", seg=48)                    # laminated core

        def top(s_):
            o = ""
            for k in range(ns):
                a = 360 * k / ns
                if k in (20, 22):
                    continue
                for rr in (rs - 4, rs + 4):
                    c = pol(rr, a, H + .2)
                    o += P([s_.cam.xy((c[0] + dx, c[1] + dy, c[2])) for dx, dy in ((-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8))])
            return path(o, "cus2")
        l.svg(top(sc))
        # twisted leg ends under the core (front half only)
        for k in range(ns):
            a = 360 * k / ns
            if not 196 < a < 344:
                continue
            for rr, da in ((rs - 4, 7), (rs + 4, -7)):
                l.svg(bar(cam, pol(rr, a, 0), pol(rr, a + da, -13), 3.2, 2.2, "cu", rot=a, lines=False))
        # one hairpin on its way in: two legs and the crown
        a1, a2 = 240, 264
        p1, p2 = pol(rs, a1, H + 12), pol(rs, a2, H + 12)
        q1, q2 = pol(rs, a1, H + 70), pol(rs, a2, H + 70)
        apx = pol(rs + 2, (a1 + a2) / 2, H + 92)
        for p, q in ((p1, q1), (p2, q2)):
            l.svg(bar(cam, p, q, 4, 2.6, "cu", rot=(a1 + a2) / 2))
        l.svg(bar(cam, q1, apx, 4, 2.6, "cu", rot=(a1 + a2) / 2))
        l.svg(bar(cam, q2, apx, 4, 2.6, "cu", rot=(a1 + a2) / 2))
    s, sc = fit(fn, -20, 28, (60, 18, 260, 178), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    p = cam.xy(pol(rs, 300, H + 80))
    s += arrow(p[0] + 18, p[1] - 10, p[0] + 18, p[1] + 26, None)
    s += arc3(cam, (0, 0, -24), (0, 0, 1), Ro + 12, 300, 240)
    h = cam.xy(pol(rs, 230, H + 80))
    c = cam.xy((Ro, 0, 20))
    t = cam.xy(pol(Ro + 12, 240, -24))
    s += lab(h[0] - 8, h[1], "ヘアピン", "end") + al(p[0] + 26, p[1] + 10, "挿入", "start")
    s += lab(c[0] + 8, c[1] - 20, "ステータコア", "start") + al(t[0] - 6, t[1] - 6, "ツイスト", "end")
    return s


# =====================================================================================
# q:winding — coil winding: the former turns, the wire is laid under tension by a traversing guide
# =====================================================================================
@picto("winding")
def _():
    a, r, L0, L1 = 30, 16, -40, 40

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, 70, -40, -70, 60, 80, 120, "pt", dark=1, ch=4)                   # spindle head
        CYL(l, (50, 0, 0), (1, 0, 0), 8, 20, "dk", seg=16)                      # spindle
        X(l, L1, 10, banded(stad(a + 4, r + 18), 2), "m", smooth=True)          # back flange
        X(l, L0, L1 - L0, banded(stad(a, r + 11), 2), "cu", smooth=True)         # wound coil
        X(l, L0 - 10, 10, banded(stad(a + 4, r + 18), 2), "m", smooth=True)     # front flange
        CYL(l, (L0 - 30, 0, 0), (1, 0, 0), 6, 20, "dk", seg=14)                 # tail centre

        def turns(s_):
            o = ""
            for x in range(L0 + 4, L1, 6):
                o += P([s_.cam.xy((x, y, z)) for y, z in stad(a, r + 11.2)], False)
            return path(o, "gr")
        l.svg(turns(sc))
        CYL(l, (10, 18, r + 74), (0, 1, 0), 12, 6, "m", seg=24)                  # guide pulley
        BOX(l, 4, 24, r + 60, 12, 10, 50, "pt")                                   # traverse arm
        g, t = cam.xy((10 - 12, 18, r + 74)), cam.xy((6, 0, r + 11))
        l.svg(path("M%s %s L%s %s" % (n(g[0]), n(g[1]), n(t[0]), n(t[1])), "cuwire"))
        k = cam.xy((10, 18, r + 86))
        l.svg(path("M%s %s L%s %s" % (n(k[0]), n(k[1]), n(k[0] + 70 * cam.s), n(k[1] - 20 * cam.s)), "cuwire"))
    s, sc = fit(fn, 26, 18, (34, 22, 286, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (L0 - 14, 0, 0), (1, 0, 0), a + r + 26, 170, 60)
    s += arrow3(cam, (-30, 0, r + 110), (30, 0, r + 110), both=True)
    c = cam.xy((L0, -a - r - 11, -8))
    w = cam.xy((10, 18, r + 86))
    tr = cam.xy((30, 0, r + 110))
    s += lab(c[0] - 8, c[1] + 10, "コイル", "end") + lab(w[0] + 72 * cam.s, w[1] - 6 * cam.s, "線材", "start")
    s += al(cam.xy((-30, 0, r + 110))[0] - 6, tr[1] - 2, "トラバース", "end")
    return s


# =====================================================================================
# q:magnetize — pulse magnetizing: the rotor is set in a yoke whose coil gets a huge current pulse
# =====================================================================================
@picto("magnetize")
def _():
    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, 110, -30, -30, 70, 70, 110, "pt", dark=1, ch=3)                  # capacitor / pulse unit
        Z(l, -30, 74, [(-60, -60), (60, -60), (60, 60), (-60, 60)], "m",
          holes=[GE.circle_outline(30, 40, 10)], smooth="outer")                # yoke
        def top(s_):
            o = ""
            for k in range(4):
                a = 45 + 90 * k
                o += P3(s_.cam, [pol(r_, a + d, 44.2) for r_, d in ((34, -16), (52, -12), (52, 12), (34, 16))], "cus2")
            return o
        l.svg(top(sc))
        CYL(l, (0, 0, 64), (0, 0, 1), 7, 70, "w", seg=16)                       # shaft
        CYL(l, (0, 0, 72), (0, 0, 1), 27, 46, "w", seg=40)                      # rotor core

        def mags(s_):
            o = ""
            for k in range(8):
                a = 22.5 + 45 * k
                for d in (-9, 9):
                    c = pol(19, a + d, 118.2)
                    o += P3(s_.cam, [(c[0] + dx, c[1] + dy, c[2]) for dx, dy in ((-2.2, -2.2), (2.2, -2.2), (2.2, 2.2), (-2.2, 2.2))], "dks2")
            return o
        l.svg(mags(sc))
        cam_ = cam
        x0, x1, z0, z1, y = 118, 172, 40, 66, -30.2
        o = P3(cam_, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], "scrn")
        cv = [(x0 + 4, y, z0 + 4), (x0 + 16, y, z0 + 4), (x0 + 19, y, z1 - 3), (x0 + 26, y, z0 + 9), (x1 - 4, y, z0 + 4)]
        o += path(P([cam_.xy(p) for p in cv], False), "scrg")
        l.svg(o)
    s, sc = fit(fn, -24, 26, (40, 18, 286, 178), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    a = cam.xy((60, -30, 20))
    b = cam.xy((110, -30, 20))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] + 14), n(a[1] + 10), n(b[0] - 14), n(b[1] + 10), n(b[0]), n(b[1])), "cable")
    p = cam.xy((-40, 0, 130))
    s += arrow(p[0], p[1] - 14, p[0], p[1] + 18, None)
    r = cam.xy((-27, 0, 96))
    y = cam.xy((0, -60, -30))
    u = cam.xy((145, -30, -30))
    s += lab(r[0] - 26, r[1] - 4, "ロータ", "end") + lab(y[0] - 10, y[1] + 18, "着磁ヨーク")
    s += lab(u[0], u[1] + 16, "パルス電源")
    return s


def pcb(sc, x0, y0, sx, sy, z0=0, t=4):
    """circuit board: thin dark slab with the green solder-mask top."""
    BOX(sc, x0, y0, z0, sx, sy, t, "dk")

    def top(s_):
        return P3(s_.cam, [(x0, y0, z0 + t + .1), (x0 + sx, y0, z0 + t + .1), (x0 + sx, y0 + sy, z0 + t + .1), (x0, y0 + sy, z0 + t + .1)], "okl")
    RAW(sc, top, ((x0, y0, z0 + t), (x0 + sx, y0 + sy, z0 + t + .2)))


def pads(cam, pts_, z, w=3.2, cls="ms1"):
    o = ""
    for x, y in pts_:
        o += P([cam.xy((x + dx, y + dy, z)) for dx, dy in ((-w, -w * .6), (w, -w * .6), (w, w * .6), (-w, w * .6))])
    return path(o, cls)


# =====================================================================================
# q:mounter — chip mounter: the head picks parts from the tape feeder with suction nozzles and
# places them on the board at high speed (X-Y gantry, Z nozzles)
# =====================================================================================
@picto("mounter")
def _():
    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -130, 64, -10, 260, 10, 14, "m")                                 # rail (back)
        pcb(l, -100, -40, 190, 100)
        l.svg(pads(cam, [(-60 + 16 * i, 20) for i in range(4)] + [(30, -20), (46, -20)], 4.2))
        for x, y, sx, sy, sz in ((-80, -24, 34, 34, 6), (-20, 30, 24, 16, 5), (50, 24, 22, 22, 5), (-60, 16, 7, 8, 3), (-44, 16, 7, 8, 3)):
            BOX(l, x, y, 4, sx, sy, sz, "dk")                                    # parts already placed
        BOX(l, -130, -52, -10, 260, 10, 14, "m")                                # rail (front)
        BOX(l, -40, -130, -10, 70, 50, 26, "pt", dark=1)                        # tape feeder
        l.svg(P3(cam, [(-20, -130, 16.2), (10, -130, 16.2), (10, -80, 16.2), (-20, -80, 16.2)], "ws2"))
        for k in range(4):
            BOX(l, -9, -122 + 11 * k, 16, 8, 6, 3, "dk")                         # parts in the tape
        BOX(l, -150, 0, 120, 300, 22, 18, "pt", dark=1)                          # gantry beam (X)
        BOX(l, 20, -18, 82, 60, 22, 56, "m", ch=3)                               # head
        for i, z in enumerate((40, 18, 40)):
            CYL(l, (30 + 20 * i, -7, z + 12), (0, 0, 1), 3.2, 82 - z - 12, "t", seg=12)
            CYL(l, (30 + 20 * i, -7, z + 2), (0, 0, 1), 1.6, 10, "dk", seg=10)
        BOX(l, 45, -12, 14, 10, 10, 6, "dk")                                     # part on the nozzle
    s, sc = fit(fn, -26, 28, (24, 26, 300, 182), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-110, -4, 148), (-40, -4, 148), both=True)
    s += arrow3(cam, (100, -40, 100), (100, 30, 100), both=True)
    s += arrow3(cam, (70, -18, 36), (70, -18, 14))
    h = cam.xy((50, -18, 138))
    f = cam.xy((-40, -130, -10))
    b = cam.xy((90, -40, 0))
    s += lab(h[0] + 30, h[1] - 6, "ヘッド", "start") + lab(f[0] - 4, f[1] + 8, "フィーダ", "end")
    s += lab(b[0] + 6, b[1] + 14, "基板", "start")
    return s


# =====================================================================================
# q:reflow — reflow oven: boards ride a conveyor through preheat, reflow (peak) and cooling zones
# (front of the tunnel cut away)
# =====================================================================================
@picto("reflow")
def _():
    xs = (-160, -40, 60, 160)

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -160, 40, -30, 320, 8, 96, "pt", dark=1)                          # back wall
        BOX(l, -160, -40, -30, 320, 80, 26, "pt", dark=1)                        # lower heaters
        # hot glow of the reflow zone (between the heater plates)
        l.svg(P3(cam, [(xs[1] + 4, 40, -4), (xs[2] - 4, 40, -4), (xs[2] - 4, 40, 40), (xs[1] + 4, 40, 40)], "hotband"))
        for k in range(4):
            x = -150 + 82 * k
            pcb(l, x, -26, 50, 52, 6, 3)
            BOX(l, x + 8, -14, 9, 14, 14, 3, "dk")
            BOX(l, x + 30, 0, 9, 10, 18, 3, "dk")
        BOX(l, -160, -40, 4, 320, 6, 4, "m")                                    # conveyor rail (front)
        BOX(l, -160, -40, 40, 320, 80, 26, "pt")                                 # upper heaters
        for x in xs[1:3]:
            l.svg(P3(cam, [(x, -40.2, 40), (x, -40.2, 66), (x, -40.2, 66), (x, -40.2, 40)], "el")
                  + path(P([cam.xy((x, -40.2, 40)), cam.xy((x, -40.2, 66))], False) + P([cam.xy((x, -40.2, -30)), cam.xy((x, -40.2, -4))], False), "el"))
    s, sc = fit(fn, -22, 22, (12, 46, 308, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for k, (a, b) in enumerate(zip(xs, xs[1:])):
        c = cam.xy(((a + b) / 2, -40, 66))
        s += lab(c[0], c[1] - 8, ("予熱", "リフロー", "冷却")[k])
    s += arrow3(cam, (-150, -40, -48), (-60, -40, -48))
    # small temperature profile above
    x0, y0 = 220, 24
    pr = [(0, 14), (16, 6), (34, 4), (42, -6), (48, -10), (54, -4), (70, 14)]
    s += path(P([(x0 + u, y0 + v) for u, v in pr], False), "a")
    a = cam.xy((-105, -40, -48))
    s += al(a[0], a[1] + 16, "搬送")
    return s


def surf(cam, F, nu, nv, mat, dark=0, edge=True):
    """curved sheet: F(u, v) -> world point for u, v in 0..1; quads shaded by the side facing the camera."""
    G = [[F(i / nu, j / nv) for j in range(nv + 1)] for i in range(nu + 1)]
    segs = []
    for i in range(nu):
        for j in range(nv):
            a, b, c, d = G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1]
            nr = GE._norm(GE._cross(tuple(c[k] - a[k] for k in range(3)), tuple(d[k] - b[k] for k in range(3))))
            if GE._dot(nr, cam.D) > 0:
                nr = tuple(-x for x in nr)
            m = tuple((a[k] + c[k]) / 2 for k in range(3))
            segs.append((cam.P(m)[2], P3(cam, [a, b, c, d], "%ss%d" % (mat, GE.shade(nr, dark)))))
    o = "".join(v for _, v in sorted(segs, key=lambda t: -t[0]))
    if edge:
        rim = [G[i][0] for i in range(nu + 1)] + [G[nu][j] for j in range(nv + 1)] + \
              [G[i][nv] for i in range(nu, -1, -1)] + [G[0][j] for j in range(nv, -1, -1)]
        o += path(P([cam.xy(p) for p in rim]), "el")
    return o


# =====================================================================================
# q:selsolder — selective soldering: a small solder fountain under the board solders only the
# leads of through-hole parts, moving from joint to joint
# =====================================================================================
@picto("selsolder")
def _():
    zb = 70

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -40, -36, -40, 120, 72, 40, "pt", dark=1, ch=3)                  # solder pot
        l.svg(P3(cam, [(-34, -30, .2), (74, -30, .2), (74, 30, .2), (-34, 30, .2)], "ms2"))   # bath surface
        CYL(l, (0, 0, 0), (0, 0, 1), 9, zb - 14, "t", seg=20)                   # nozzle
        CYL(l, (0, 0, zb - 14), (0, 0, 1), 9, 6, "m", seg=20, r1=4.5)           # solder fountain
        for x in (-6, 0, 6, 12, 18, 24):                                        # leads through the board
            BOX(l, x - 1, -1, zb - 9, 2, 2, 9, "m")
        pcb(l, -110, -60, 220, 120, zb, 4)
        BOX(l, -12, -14, zb + 4, 44, 28, 18, "dk", ch=2)                         # through-hole connector
        BOX(l, -84, -30, zb + 4, 26, 26, 5, "dk")                                 # SMD parts (already done)
        BOX(l, 50, 16, zb + 4, 30, 18, 5, "dk")
    s, sc = fit(fn, -24, 14, (24, 22, 296, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (30, -40, 30), (80, -40, 30), both=True)
    u = cam.xy((-2, 0, zb - 22))
    s += arrow(u[0] - 26, u[1] + 14, u[0] - 26, u[1] - 12, None)
    b = cam.xy((110, -60, zb + 4))
    p = cam.xy((80, -36, -40))
    c = cam.xy((32, -14, zb + 22))
    s += lab(b[0] - 30, b[1] + 16, "基板", "end") + lab(p[0], p[1] + 14, "はんだ槽", "end")
    s += lab(u[0] - 32, u[1] + 4, "噴流ノズル", "end") + lab(c[0] + 6, c[1] - 6, "挿入部品", "start")
    return s


# =====================================================================================
# q:dispense — dispensing / potting: metered two-part resin flows from the needle into the case
# around the board (front wall of the case shown low)
# =====================================================================================
@picto("dispense")
def _():
    a, b, h, t, lv = 80, 50, 40, 5, 22

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -a, -b, -6, 2 * a, 2 * b, 6, "alu")                              # case bottom
        BOX(l, -a, b - t, 0, 2 * a, t, h, "alu")                                # back wall
        BOX(l, -a, -b + t, 0, t, 2 * b - 2 * t, h, "alu")                       # left wall
        BOX(l, -40, 10, 0, 22, 18, lv + 12, "dk")                               # tall parts sticking out
        CYL(l, (24, 18, 0), (0, 0, 1), 9, lv + 16, "alu", seg=20)               # capacitor
        l.svg(P3(cam, [(-a + t, -b + t, lv), (a - t, -b + t, lv), (a - t, b - t, lv), (-a + t, b - t, lv)], "resin"))
        BOX(l, -40, 10, lv, 22, 18, 12, "dk")
        CYL(l, (24, 18, lv), (0, 0, 1), 9, 16, "alu", seg=20)
        BOX(l, a - t, -b + t, 0, t, 2 * b - 2 * t, h, "alu")                    # right wall
        BOX(l, -a, -b, 0, 2 * a, t, h, "alu")                                   # front wall
        # resin thread from the needle, landing on the surface
        tip, land = cam.xy((-10, -18, 80)), cam.xy((-10, -18, lv))
        w = 1.6 * cam.s
        l.svg(poly([(tip[0] - w, tip[1]), (tip[0] + w, tip[1]), (land[0] + w * 1.6, land[1]), (land[0] - w * 1.6, land[1])], "resin"))
        CYL(l, (-10, -18, 80), (0, 0, 1), 1.8, 18, "t", seg=10)                  # needle
        CYL(l, (-10, -18, 98), (0, 0, 1), 6, 8, "dk", seg=16, r1=2.5)          # mixer tip
        CYL(l, (-10, -18, 106), (0, 0, 1), 11, 52, "m", seg=24)                  # dispensing valve body
        BOX(l, -30, -26, 158, 40, 16, 14, "pt")                                  # head bracket
    s, sc = fit(fn, -26, 26, (40, 18, 280, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (20, -18, 124), (66, -18, 124), both=True)
    v = cam.xy((-21, -18, 132))
    r = cam.xy((a - 30, -b, lv + 10))
    c = cam.xy((a, -b, -6))
    s += lab(v[0] - 6, v[1], "ディスペンサ", "end") + lab(c[0] + 6, c[1] + 4, "ケース", "start")
    s += al(cam.xy((66, -18, 124))[0] + 6, cam.xy((66, -18, 124))[1] + 4, "移動", "start")
    s += lab(r[0] + 40, r[1] - 34, "樹脂", "start")
    return s


# =====================================================================================
# q:dicing — dicing saw: a thin spinning diamond blade cuts the wafer on tape into chips, street by street
# =====================================================================================
@picto("dicing")
def _():
    Rw, pitch, yl, Rb = 62, 14, 7, 30

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        CYL(l, (0, 0, -16), (0, 0, 1), 84, 14, "m", seg=48)                     # chuck table
        RING(l, (0, 0, -2), (0, 0, 1), 96, 78, 3, "pt", seg=48)                  # wafer frame
        l.svg(path(P(circ3(cam, (0, 0, -1.8), (0, 0, 1), 78, 40)), "gl"))       # dicing tape
        CYL(l, (0, 0, 0), (0, 0, 1), Rw, 2.5, "alu", seg=48)                     # wafer

        def streets(s_):
            o, d = "", ""
            for k in range(-4, 5):
                c = k * pitch + yl - pitch * 0       # streets along x (some already cut) and along y
                for ax in (0, 1):
                    v = k * pitch + (yl if ax == 0 else 0)
                    if abs(v) >= Rw - 2:
                        continue
                    h = math.sqrt(Rw * Rw - v * v) - 1
                    p0, p1 = ((-h, v, 2.6), (h, v, 2.6)) if ax == 0 else ((v, -h, 2.6), (v, h, 2.6))
                    if ax == 0 and v > yl:
                        continue                                    # not yet cut
                    if ax == 0 and v == yl:
                        p1 = (14, v, 2.6)                           # being cut now
                    seg_ = "M%s %sL%s %s" % tuple(n(q) for q in s_.cam.xy(p0) + s_.cam.xy(p1))
                    if ax == 0:
                        o += seg_
                    else:
                        d += seg_
            return path(d, "gr") + path(o, "x")
        l.svg(streets(sc))
        BOX(l, 14 - 10, yl + 16, Rb - 12, 20, 70, 24, "pt", dark=1)              # spindle housing (behind)
        CYL(l, (14, yl - 6, Rb - 3), (0, 1, 0), 13, 12, "m", seg=24)             # flanges
        CYL(l, (14, yl - .8, Rb - 3), (0, 1, 0), Rb, 1.6, "t", seg=48)           # blade
        BOX(l, -8, yl - 14, Rb + 12, 44, 8, 22, "m", ch=2)                       # blade cover
    s, sc = fit(fn, 30, 30, (30, 20, 290, 180), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (14, yl - 4, Rb - 3), (0, 1, 0), Rb + 8, 170, 250)
    s += arrow3(cam, (20, -Rw - 30, 0), (-40, -Rw - 30, 0))
    for dx in (-10, 10):
        p = cam.xy((14 + dx * 1.4, yl - 6, 8))
        q = cam.xy((14 + dx * 0.5, yl - 6, 3))
        s += path("M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1])), "spray")
    b = cam.xy((14, yl, 2 * Rb + 6))
    w = cam.xy((-Rw, 0, 0))
    f = cam.xy((-10, -Rw - 30, 0))
    s += lab(b[0] + 30, b[1] - 6, "ブレード", "start") + lab(w[0] + 12, w[1] + 30, "ウェハ")
    s += al(f[0], f[1] + 18, "切断送り")
    return s


# =====================================================================================
# q:diebond — die bonder (pressure sintering): the bond head presses the chip onto silver paste on the
# copper pattern of the substrate while the stage heats it
# =====================================================================================
@picto("diebond")
def _():
    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -110, -60, -30, 220, 120, 24, "m", ch=3)                          # heated stage
        l.svg(P3(cam, [(-110, -60.2, -24), (110, -60.2, -24), (110, -60.2, -12), (-110, -60.2, -12)], "hotband"))
        BOX(l, -90, -46, -6, 180, 92, 6, "pt")                                   # ceramic substrate
        for x0, y0, sx, sy in ((-80, -36, 74, 72), (2, -36, 78, 72)):
            BOX(l, x0, y0, 0, sx, sy, 4, "cu")                                   # copper pattern
        for x0, y0 in ((-70, -22), (-42, 4), (16, -22)):
            BOX(l, x0, y0, 4, 22, 22, 1.2, "m")                                  # sintered silver layer
            BOX(l, x0 + 1, y0 + 1, 5.2, 20, 20, 3, "dk")                         # bonded chips
        BOX(l, 44, 4, 4, 24, 24, 1.4, "m")                                       # printed silver paste (next site)
        BOX(l, 45, 5, 34, 22, 22, 3, "dk")                                       # chip held by the collet
        BOX(l, 42, 2, 37, 28, 28, 10, "t", ch=2)                                 # collet / press tool
        CYL(l, (56, 16, 47), (0, 0, 1), 9, 46, "m", seg=20)                      # head shaft
        BOX(l, 30, -10, 93, 52, 52, 30, "pt", dark=1, ch=4)                      # bond head
    s, sc = fit(fn, -24, 26, (30, 18, 290, 178), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    p = cam.xy((92, 16, 70))
    s += arrow(p[0] + 6, p[1] - 16, p[0] + 6, p[1] + 14, None)
    st = cam.xy((-110, -60, -24))
    ch_ = cam.xy((-70, -22, 10))
    pa = cam.xy((68, 4, 4))
    s += al(p[0] + 12, p[1] + 2, "加圧", "start") + lab(st[0] - 2, st[1] + 22, "加熱ステージ", "start")
    s += lab(ch_[0] - 10, ch_[1] - 22, "チップ", "end") + lab(pa[0] + 12, pa[1] + 14, "銀焼結材", "start")
    return s


def loop3(cam, p0, p1, hgt, seg=14):
    """wire loop between two 3D points, rising hgt above the higher end."""
    pts_ = []
    for k in range(seg + 1):
        t = k / seg
        z = p0[2] + (p1[2] - p0[2]) * t + (hgt + max(0, p1[2] - p0[2]) * (1 - t)) * math.sin(math.pi * t) ** .8
        pts_.append(cam.xy((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t, z)))
    return P(pts_, False)


# =====================================================================================
# q:wirebond — heavy-wire bonder: the wedge tool presses aluminium wire onto the chip pads with
# ultrasonic vibration, then loops it over to the copper terminal
# =====================================================================================
@picto("wirebond")
def _():
    xs = (-24, -8, 8, 24)
    yt = 70

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -90, -50, -8, 180, 150, 8, "pt")                                   # ceramic substrate
        BOX(l, -80, -40, 0, 160, 78, 4, "cu")                                     # copper pattern (die)
        BOX(l, -80, 50, 0, 160, 40, 4, "cu")                                      # copper pattern (terminal)
        BOX(l, -40, -24, 4, 80, 48, 5, "dk")                                      # chip
        l.svg(P3(cam, [(-34, -18, 9.1), (34, -18, 9.1), (34, 18, 9.1), (-34, 18, 9.1)], "ms3"))   # top metal
        d = ""
        for x in xs:
            d += loop3(cam, (x, 0, 9), (x, yt, 4), 26)
        l.svg(path(d, "probe"))
        l.svg(path(loop3(cam, (40, 0, 9), (40, 30, 30), 8, 8), "probe"))          # wire being drawn out
        # wedge tool (inclined) over the newest bond
        l.svg(bar(cam, (40, 30, 31), (40, 54, 120), 7, 5, "t"))
        BOX(l, 20, 50, 120, 44, 30, 26, "pt", dark=1, ch=3)                        # bond head / transducer
        l.svg(bar(cam, (40, 52, 133), (40, -26, 133), 8, 8, "m"))                   # ultrasonic horn
    s, sc = fit(fn, 28, 28, (34, 18, 284, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    h = cam.xy((40, -30, 133))
    s += arrow(h[0] - 14, h[1] + 14, h[0] + 14, h[1] + 14, None, both=True)
    c = cam.xy((-40, -24, 4))
    w = cam.xy((-24, yt / 2, 38))
    t = cam.xy((40, 54, 120))
    s += al(h[0], h[1] + 30, "超音波") + lab(c[0] - 4, c[1] + 12, "チップ", "end")
    s += lab(w[0] - 10, w[1] - 6, "アルミ線", "end") + lab(t[0] + 40, t[1] + 34, "ウェッジツール", "start")
    return s


# =====================================================================================
# q:align — active alignment: the lens is held over the powered image sensor, moved in 6 axes while
# the camera images a test chart, then the adhesive is cured with UV light in the best position
# =====================================================================================
@picto("align")
def _():
    zl = 34

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -70, -50, -20, 140, 100, 14, "m", ch=3)                           # stage
        pcb(l, -36, -30, 72, 60, -6, 4)                                          # sensor board
        BOX(l, -12, -12, -2, 24, 24, 3, "dk")                                    # image sensor
        RING(l, (0, 0, 1), (0, 0, 1), 22, 15, 10, "dk", seg=32)                  # holder (with adhesive)
        l.svg(path(P(circ3(cam, (0, 0, 11.2), (0, 0, 1), 18.5, 28)), "resin"))  # adhesive bead
        CYL(l, (0, 0, 12), (0, 0, 1), 13, zl, "dk", seg=28)                      # lens barrel
        l.svg(path(P(circ3(cam, (0, 0, 12 + zl + .2), (0, 0, 1), 9, 24)), "lens"))
        BOX(l, -27, -8, 22, 14, 16, 16, "t")                                     # gripper jaws
        BOX(l, 13, -8, 22, 14, 16, 16, "t")
        BOX(l, -40, -10, 38, 80, 20, 14, "pt", ch=3)                             # gripper body
        for sg in (-1, 1):                                                       # UV lamps
            l.svg(bar(cam, (sg * 70, -36, 50), (sg * 34, -14, 24), 12, 12, "dk"))
        BOX(l, -60, -20, 96, 120, 10, 44, "pt")                                  # test chart (above)

        def chart(s_):
            o = ""
            for cx, cz in ((-40, 106), (40, 106), (0, 118), (-40, 130), (40, 130)):
                o += P3(s_.cam, [(cx - 5, -20.2, cz - 5), (cx + 5, -20.2, cz - 5), (cx + 5, -20.2, cz + 5), (cx - 5, -20.2, cz + 5)], "dks1")
            return o
        l.svg(chart(sc))
    s, sc = fit(fn, -22, 22, (40, 14, 280, 182), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    for sg in (-1, 1):
        a, b = cam.xy((sg * 34, -14, 24)), cam.xy((sg * 18, -4, 12))
        s += path("M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1])), "uv")
    s += arc3(cam, (0, 0, 30), (0, 0, 1), 40, 200, 320)
    c = cam.xy((60, -20, 126))
    u = cam.xy((70, -36, 50))
    w = cam.xy((-40, -10, 52))
    st = cam.xy((-36, -30, -6))
    s += lab(c[0] + 6, c[1], "テストチャート", "start") + al(u[0] + 8, u[1] + 4, "UV硬化", "start")
    s += lab(w[0] - 4, w[1] - 6, "レンズ", "end") + lab(st[0] + 10, st[1] + 30, "撮像素子基板", "end")
    return s


# =====================================================================================
# q:scan3d — fringe-projection 3D scanner: the projector throws stripe patterns on the panel, two
# cameras see how the stripes bend and turn it into a point cloud of the whole surface
# =====================================================================================
@picto("scan3d")
def _():
    def F(u, v):
        x, y = -110 + 220 * u, -50 + 110 * v
        return (x, y, 26 * math.sin(math.pi * u) * (1 - .25 * v) + 10 * v)

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        for x in (-80, 70):
            BOX(l, x, -20, -30, 12, 40, 30 + F((x + 116) / 220, .27)[2] - 8, "m")   # supports
        l.svg(surf(cam, F, 12, 4, "w"))                                              # pressed panel
        d = ""
        for k in range(1, 16):
            u = k / 16
            d += P([cam.xy(F(u, j / 8)) for j in range(9)], False)
        l.svg(path(d, "fringe"))
        BOX(l, -70, -6, 150, 140, 22, 22, "pt", ch=4)                                # scanner bar
        for x in (-58, 58):
            CYL(l, (x, 5, 150), (0, 0, -1), 8, 8, "dk", seg=18)                      # cameras
        CYL(l, (0, 5, 150), (0, 0, -1), 11, 10, "m", seg=20)                         # projector
    s, sc = fit(fn, -22, 26, (30, 18, 290, 178), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    p = cam.xy((0, 5, 140))
    d = ""
    for u, v in ((.1, .1), (.9, .1), (.9, .9), (.1, .9)):
        q = cam.xy(F(u, v))
        d += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1]))
    s += path(d, "ray")
    pr = cam.xy((11, -6, 172))
    c = cam.xy((-66, -6, 160))
    w = cam.xy(F(1, 0))
    s += lab(pr[0] + 30, pr[1] - 8, "縞パターン投影", "start") + lab(c[0] - 6, c[1] + 4, "カメラ", "end")
    s += lab(w[0] - 4, w[1] + 18, "パネル（点群→CAD比較）", "end")
    return s


# =====================================================================================
# q:gauge — air micrometer: air blows from the jets of a plug gauge onto the bore wall; the back
# pressure / flow tells the gap, i.e. the bore diameter (work shown cut in half)
# =====================================================================================
@picto("gauge")
def _():
    Rb, Hb, rp = 28, 64, 25

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -70, Rb, 0, 140, 34, Hb, "w")                                       # back of the work
        l.svg(surf(cam, lambda u, v: (Rb * math.cos(math.pi * u), Rb * math.sin(math.pi * u), Hb * v), 10, 1, "w", dark=.4))
        BOX(l, -70, 0, 0, 70 - Rb, Rb, Hb, "w")                                    # left half
        BOX(l, Rb, 0, 0, 70 - Rb, Rb, Hb, "w")                                     # right half
        for x0, x1 in ((-70, -Rb), (Rb, 70)):
            l.svg(P3(cam, [(x0, -.2, 0), (x1, -.2, 0), (x1, -.2, Hb), (x0, -.2, Hb)], "cut"))
        CYL(l, (0, 0, 8), (0, 0, 1), rp, Hb + 8, "t", seg=32)                      # air plug
        for z in (24, 48):
            for sg in (-1, 1):
                l.svg(hole3(cam, (sg * rp * .7, -rp * .72, z), (sg * .7, -.72, 0), 2.6))
        CYL(l, (0, 0, Hb + 16), (0, 0, 1), 10, 34, "m", seg=20)                    # handle
    s, sc = fit(fn, 24, 20, (30, 20, 220, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    for z in (24, 48):
        for sg in (-1, 1):
            a = cam.xy((sg * (rp - 1), -2, z))
            b = cam.xy((sg * (Rb + 0.5), -2, z))
            s += arrow(a[0], a[1], b[0] + sg * 6, b[1], None)
    # hose to the gauge unit with a bar display
    h = cam.xy((0, 0, Hb + 50))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(h[0]), n(h[1]), n(h[0]), n(h[1] - 20), n(250), n(h[1] - 30), n(262), n(70)), "pipe")
    s += rect(240, 70, 46, 82, "m2", 4) + rect(250, 80, 12, 62, "scrn") + rect(252, 108, 8, 32, "scrl")
    s += line(266, 80, 266, 142, "thin o") + line(266, 104, 272, 104, "o")
    w = cam.xy((70, 0, 0))
    p = cam.xy((-10, 0, Hb + 50))
    s += lab(w[0] - 4, w[1] + 16, "ワーク（穴）", "end") + lab(p[0] - 6, p[1], "エアプラグ", "end")
    s += lab(263, 168, "表示器") + al(cam.xy((-Rb, -2, 36))[0] - 8, cam.xy((-Rb, -2, 36))[1] + 2, "空気", "end")
    return s


# =====================================================================================
# q:inprocess — in-process gauging: two fingers ride on the diameter being ground and stop the
# wheel infeed exactly at the target size
# =====================================================================================
@picto("inprocess")
def _():
    r, Rw, xg = 22, 62, 40

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        CYL(l, (-60, r + Rw - 2, 0), (1, 0, 0), 20, 130, "dk", seg=20)           # wheel spindle
        CYL(l, (-40, r + Rw - 2, 0), (1, 0, 0), Rw, 44, "gw", seg=48)            # grinding wheel
        CYL(l, (-140, 0, 0), (1, 0, 0), 10, 16, "m", seg=16, r1=3)             # centre (headstock side)
        CYL(l, (-124, 0, 0), (1, 0, 0), r - 6, 24, "w", seg=28)
        CYL(l, (-100, 0, 0), (1, 0, 0), r, 200, "w", seg=36)                    # work (journal being ground)
        CYL(l, (100, 0, 0), (1, 0, 0), r - 6, 24, "w", seg=28)
        CYL(l, (140, 0, 0), (1, 0, 0), 10, 16, "m", seg=16, r1=3)
        l.svg(bar(cam, (xg, -70, -r - 4), (xg, -2, -r - 4), 8, 6, "m"))          # lower finger
        l.svg(bar(cam, (xg, -2, -r - 4), (xg, -2, -r + 1), 6, 6, "t"))
        BOX(l, xg - 18, -110, -40, 36, 40, 80, "pt", ch=4)                       # gauge head
        l.svg(bar(cam, (xg, -70, r + 4), (xg, -2, r + 4), 8, 6, "m"))            # upper finger
        l.svg(bar(cam, (xg, -2, r + 4), (xg, -2, r - 1), 6, 6, "t"))
    s, sc = fit(fn, 26, 22, (20, 22, 300, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-110, 0, 0), (1, 0, 0), r + 10, 60, 170)
    s += arrow3(cam, (-18, r + Rw + 24, Rw + 4), (-18, r + Rw - 14, Rw + 4))
    w = cam.xy((4, r + Rw, Rw + 4))
    g = cam.xy((xg + 18, -110, -40))
    k = cam.xy((-100, -r, -r))
    s += lab(w[0] + 18, w[1] - 4, "砥石", "start") + lab(g[0] + 44, g[1] + 14, "定寸ヘッド", "end")
    s += lab(k[0] - 4, k[1] + 16, "工作物", "start") + al(cam.xy((-18, r + Rw + 24, Rw + 4))[0] - 6, cam.xy((-18, r + Rw + 24, Rw + 4))[1] + 4, "切込み", "end")
    return s


# =====================================================================================
# q:roundness — roundness / cylindricity tester: an ultra-precise turntable spins the part, a stylus on
# the column reads the radius change around the circle (polar plot), at several heights
# =====================================================================================
@picto("roundness")
def _():
    rw, hw, zp = 26, 78, 52

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -80, -70, -40, 240, 140, 26, "pt", dark=1, ch=4)                 # base
        BOX(l, 110, -14, -14, 34, 34, 160, "pt", dark=1, ch=3)                  # column
        CYL(l, (0, 0, -14), (0, 0, 1), 52, 16, "m", seg=48)                     # turntable
        CYL(l, (0, 0, 2), (0, 0, 1), 34, 8, "dk", seg=40)                        # centring / levelling stage
        CYL(l, (0, 0, 10), (0, 0, 1), rw + 8, 18, "w", seg=40)                   # part: flange
        CYL(l, (0, 0, 28), (0, 0, 1), rw, hw - 18, "w", seg=40)                  # part: measured diameter
        BOX(l, 96, -20, zp - 12, 26, 40, 30, "m", ch=2)                          # carriage on the column
        l.svg(bar(cam, (96, 0, zp), (rw + 14, 0, zp), 10, 8, "pt"))             # horizontal arm
        l.svg(bar(cam, (rw + 14, 0, zp), (rw + 3, 0, zp), 3, 3, "t"))           # stylus
    s, sc = fit(fn, -30, 24, (70, 22, 300, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += ball(cam, (rw + 2, 0, zp), 2.4)
    s += arc3(cam, (0, 0, -6), (0, 0, 1), 64, 200, 330)
    s += arrow3(cam, (150, -24, zp + 50), (150, -24, zp - 10), both=True)
    # polar plot of the measured profile
    cx, cy, R = 40, 60, 26
    s += circ(cx, cy, R, "o thin") + circ(cx, cy, R * .6, "o thin")
    pr = [(cx + (R * .8 + 2.2 * math.sin(3 * t) + 1.2 * math.sin(7 * t + 1)) * math.cos(t),
           cy + (R * .8 + 2.2 * math.sin(3 * t) + 1.2 * math.sin(7 * t + 1)) * math.sin(t)) for t in [2 * math.pi * k / 48 for k in range(48)]]
    s += path(P(pr), "a")
    t = cam.xy((0, -52, -14))
    d = cam.xy((96, -20, zp + 18))
    s += lab(t[0] + 4, t[1] + 26, "回転テーブル") + lab(d[0] - 2, d[1] - 8, "検出器", "end")
    s += lab(cx, cy + R + 16, "真円度")
    return s
