"""v3 principle drawings (shaded 3D style) for the second half of 「寸法・形状測定」 and the
appearance / paint inspections: roughness, shaft measuring, vision, in-line body measuring, gap & flush,
panel surface distortion, paint inspection, colour / gloss, glass distortion and weight sorting.
Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import PI, compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3

BIG = ((-1e4, -1e4, -1e4), (1e4, 1e4, 1e4))


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


class L:
    """painter's-order proxy for a Scene: everything added through it is drawn in call order."""

    def __init__(s, sc):
        s.sc, s.cam, s.k = sc, sc.cam, 0

    def add(s, svg, bb=None, bias=0.0, z=0):
        s.k += 1
        s.sc.add(svg, BIG, -s.k)

    def svg(s, v):
        s.add(v)


def P3(cam, pts, cls, close=True):
    return path(P([cam.xy(p) for p in pts], close), cls)


def YPR(sc, y0, L_, xz, mat="m", bias=0.0, **kw):
    """outline [(x, z), ...] extruded along +y from y0 (front face at y0 faces the viewer)."""
    loop = [(-p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L_, mat, **kw)),
           ((min(xs), y0, min(zs)), (max(xs), y0 + L_, max(zs))), bias)


def ball(cam, C, r, cls="probeball"):
    x, y = cam.xy(C)
    return circ(x, y, r * cam.s, cls)


def bar(cam, p0, p1, w, t, mat, rot=0.0, lines=True):
    """rectangular bar (w x t section) from p0 to p1."""
    A = tuple(p1[i] - p0[i] for i in range(3))
    h = math.sqrt(GE._dot(A, A))
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    ol = [(u * c - v * s_, u * s_ + v * c, k) for k, (u, v) in enumerate(((-w / 2, -t / 2), (w / 2, -t / 2), (w / 2, t / 2), (-w / 2, t / 2)))]
    return compact(GE.prism(cam, p0, A, ol, h, mat, lines=lines))


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


def seg2(a, b, c="o thin"):
    return "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))


# =====================================================================================
# q:rough — stylus profilometer: the drive unit on the column pulls a fine diamond stylus across the
# surface; the up-and-down of the tip is the roughness / contour trace
# =====================================================================================
@picto("rough")
def _():
    zt = 10                                     # top of the work

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -116, -64, -42, 296, 128, 22, "pt", dark=1, ch=4)               # granite base
        BOX(l, 128, 8, -20, 34, 34, 176, "pt", dark=1, ch=3)                   # column
        BOX(l, -80, -34, -20, 140, 68, 30, "w", ch=3)                          # work (finished block)
        BOX(l, 112, 2, 48, 58, 46, 34, "m", ch=2)                              # carriage on the column
        BOX(l, 6, -13, 52, 106, 26, 26, "pt", ch=3)                            # drive unit / detector
        l.svg(bar(cam, (6, 0, 60), (-34, 0, 60), 6, 6, "m"))                   # pick-up arm
        l.svg(bar(cam, (-34, 0, 60), (-34, 0, zt + 2), 3, 3, "t"))            # stylus
    s, sc = fit(fn, -28, 26, (92, 18, 302, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += ball(cam, (-34, 0, zt + 1.5), 2.2)
    s += arrow3(cam, (30, -14, 96), (-30, -14, 96))
    # measured profile (one small trace)
    x0, y0, w = 18, 70, 92
    s += line(x0, y0 + 22, x0 + w, y0 + 22, "o thin")
    pr = [(x0 + w * k / 46, y0 + 6 * math.sin(k * 1.7) * math.cos(k * .43) + 3 * math.sin(k * 3.9 + 1)) for k in range(47)]
    s += path(P(pr, False), "a")
    a = cam.xy((0, -14, 96))
    t = cam.xy((-34, 0, zt))
    w_ = cam.xy((-80, -34, -20))
    s += al(a[0], a[1] - 8, "走査") + lab(t[0] - 10, t[1] - 4, "触針", "end")
    s += lab(w_[0] + 30, w_[1] + 20, "工作物") + lab(x0 + w / 2, y0 + 40, "粗さ曲線")
    return s


# =====================================================================================
# q:shaftmeas — shaft measuring machine: the cam / crank shaft turns between centres while a probe
# on a carriage travels along it, reading diameters, roundness, lobe profile and phase
# =====================================================================================
def lobe(e=12, rb=14, rn=8):
    return banded(hull(arc(0, 0, rb, 0, 360, 16) + arc(0, e + rb - rn, rn, 0, 180, 6)), 3)


@picto("shaftmeas")
def _():
    xp = 11                                     # lobe under the probe

    def fn(sc):
        BOX(sc, -140, -60, -66, 280, 100, 22, "pt", dark=1, ch=4)              # bed
        BOX(sc, -131, -22, -44, 30, 44, 58, "pt", ch=3)                        # headstock
        BOX(sc, 101, -22, -44, 30, 44, 58, "pt", ch=3)                         # tailstock
        CYL(sc, (-101, 0, 0), (1, 0, 0), 9, 12, "m", seg=16, r1=2)             # centres
        CYL(sc, (101, 0, 0), (-1, 0, 0), 9, 12, "m", seg=16, r1=2)
        BOX(sc, -96, -56, -44, 192, 12, 6, "m")                               # carriage rail
        BOX(sc, xp - 18, -60, -38, 36, 22, 26, "m", ch=2)                      # carriage
        # camshaft: journals and lobes stacked along x (bboxes touch exactly)
        x = -(18 * 2 + 20 * 2 + 30 + 12 * 6) / 2
        parts_ = [("j", 18), ("l", 12, 30), ("c", 10), ("l", 12, 150), ("j", 20), ("l", 12, 270), ("c", 10),
                  ("l", 12, 40), ("j", 20), ("l", 12, 160), ("c", 10), ("l", 12, 280), ("j", 18)]
        for p in parts_:
            if p[0] == "j":
                CYL(sc, (x, 0, 0), (1, 0, 0), 13, p[1], "w", seg=24, bands=8)
            elif p[0] == "c":
                CYL(sc, (x, 0, 0), (1, 0, 0), 9, p[1], "w", seg=16, bands=6, dark=1)
            else:
                ph = math.radians(p[2])
                ol = [(u * math.cos(ph) - v * math.sin(ph), u * math.sin(ph) + v * math.cos(ph), f) for u, v, f in lobe()]
                X(sc, x, p[1], ol, "w", smooth=True)
            x += p[1]
    s, sc = fit(fn, 24, 30, (24, 26, 296, 172), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    # probe arm from the carriage to the lobe it is reading (lobe at x 24..36 -> use the 4th lobe position)
    s += bar(cam, (xp, -48, -12), (xp, -48, 0), 6, 6, "m") + bar(cam, (xp, -48, 0), (xp, -17, 0), 5, 5, "t")
    s += ball(cam, (xp, -16, 0), 2.4)
    s += arc3(cam, (-80, 0, 0), (1, 0, 0), 30, 70, 175)
    s += arrow3(cam, (xp - 40, -76, -38), (xp + 50, -76, -38), both=True)
    r = cam.xy((-80, -30, 30))
    c = cam.xy((xp + 50, -76, -38))
    w = cam.xy((60, 0, 22))
    pb = cam.xy((xp - 18, -60, -12))
    s += al(r[0] - 4, r[1] - 8, "回転") + al(c[0] + 6, c[1] + 6, "移動", "start")
    s += lab(w[0], w[1] - 22, "カムシャフト") + lab(pb[0] - 6, pb[1] + 4, "測定子", "end")
    return s


# =====================================================================================
# q:camera — vision inspection (also AOI / SPI): a camera with a ring light looks down at the part on
# the conveyor; the image is judged for presence, position, size and surface defects
# =====================================================================================
@picto("camera")
def _():
    zc = 96                                     # bottom of the ring light

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, 70, 44, -40, 26, 26, 214, "pt", dark=1, ch=3)                   # post (behind)
        BOX(l, -150, 40, -40, 300, 8, 24, "pt", dark=1)                        # conveyor frame (back)
        BOX(l, -150, -40, -30, 300, 80, 10, "dk")                              # belt
        BOX(l, -150, -48, -40, 300, 8, 24, "pt", dark=1)                       # conveyor frame (front)
        CYL(l, (-100, 0, -20), (0, 0, 1), 26, 12, "w", seg=32)                 # next part
        CYL(l, (0, 0, -20), (0, 0, 1), 34, 14, "w", seg=40)                    # part under the camera
        CYL(l, (0, 0, -6), (0, 0, 1), 16, 10, "w", seg=28)
        l.svg(hole3(cam, (0, 0, 4.1), (0, 0, 1), 9))
        for k in range(6):
            a = math.radians(30 + 60 * k)
            l.svg(hole3(cam, (26 * math.cos(a), 26 * math.sin(a), -5.9), (0, 0, 1), 3))
        l.svg(bar(cam, (83, 57, zc + 60), (0, 0, zc + 60), 14, 10, "m"))       # arm
        RING(l, (0, 0, zc), (0, 0, 1), 40, 22, 9, "m", seg=40)                 # ring light
        CYL(l, (0, 0, zc - 4), (0, 0, 1), 13, 30, "dk", seg=24)                # lens
        BOX(l, -20, -20, zc + 26, 40, 40, 44, "dk", ch=3)                      # camera body
    s, sc = fit(fn, -26, 26, (96, 16, 300, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    p = cam.xy((0, 0, zc - 4))
    d = ""
    for k in range(4):
        a = math.radians(45 + 90 * k)
        q = cam.xy((40 * math.cos(a), 40 * math.sin(a), -6))
        d += seg2(p, q)
    s += path(d, "ray")
    s += arrow3(cam, (-60, -70, -30), (40, -70, -30))
    # small image / judgement screen
    x0, y0 = 22, 40
    s += rect(x0, y0, 76, 58, "scrn", 3) + circ(x0 + 38, y0 + 29, 21, "scrg") + circ(x0 + 38, y0 + 29, 7, "scrg")
    for k in range(6):
        a = math.radians(30 + 60 * k)
        s += circ(x0 + 38 + 15 * math.cos(a), y0 + 29 + 15 * math.sin(a), 2.2, "scrg")
    c = cam.xy((-20, -20, zc + 60))
    r = cam.xy((-40, 0, zc + 4))
    f = cam.xy((40, -70, -30))
    s += lab(c[0] - 8, c[1] + 4, "カメラ", "end") + lab(r[0] - 8, r[1] + 6, "照明", "end")
    s += al(f[0] + 6, f[1] + 12, "搬送", "start") + lab(x0 + 38, y0 + 76, "画像で判定")
    return s


# =====================================================================================
# q:bodymeas — in-line body measuring: as each body-in-white stops in the station, laser / vision
# sensors on a frame read its reference points (holes, edges, surfaces) — every car, every point
# =====================================================================================
def biw(l, cam, y0=0.0, W=100.0, mat="w", open_=True):
    """simplified body shell: lower body + narrower cabin, wheel arches and window openings."""
    lo = hull([(-130, 10), (130, 10), (137, 24), (133, 46), (62, 54), (-104, 56), (-130, 46), (-136, 26)])
    cab = hull([(-74, 54), (44, 54), (12, 94), (-52, 96), (-80, 62)])
    YPR(l, y0 + 8, W - 16, cab, mat, smooth=False)
    YPR(l, y0, W, lo, mat)
    o = ""
    for xw in (-88, 86):
        o += path(P([cam.xy((xw + 27 * math.cos(math.radians(a)), y0 - .2, 10 + 27 * math.sin(math.radians(a)))) for a in range(0, 181, 15)]), "bg")
    if open_:
        o += P3(cam, [(-70, y0 + 7.8, 58), (-18, y0 + 7.8, 58), (-18, y0 + 7.8, 88), (-50, y0 + 7.8, 90), (-72, y0 + 7.8, 64)], "bg")
        o += P3(cam, [(-10, y0 + 7.8, 58), (38, y0 + 7.8, 58), (10, y0 + 7.8, 88), (-10, y0 + 7.8, 88)], "bg")
    l.svg(o)


@picto("bodymeas")
def _():
    xf = 64                                     # measuring frame position

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, xf, 150, 0, 16, 16, 150, "pt", dark=1, ch=2)                    # back post
        for y in (14, 74):
            BOX(l, -150, y, 0, 300, 12, 10, "dk")                              # skid / conveyor rails
        biw(l, cam)
        BOX(l, xf, -66, 150, 16, 232, 14, "pt", dark=1)                        # top beam
        BOX(l, xf + 2, 42, 132, 12, 16, 18, "dk", ch=2)                        # roof sensor
        BOX(l, xf, -66, 0, 16, 16, 150, "pt", dark=1, ch=2)                    # front post
        for z in (30, 84):
            BOX(l, xf + 2, -50, z, 12, 14, 14, "dk", ch=2)                     # side sensors
    s, sc = fit(fn, -30, 22, (18, 20, 302, 178), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    tg = [((xf + 8, -36, 37), (-40, -.3, 38)), ((xf + 8, -36, 37), (112, -.3, 32)),
          ((xf + 8, -36, 91), (24, 7.5, 70)), ((xf + 8, 50, 132), (-20, 50, 95))]
    d = "".join(seg2(cam.xy(a), cam.xy(b)) for a, b in tg)
    s += path(d, "laserl")
    for _a, b in tg:
        q = cam.xy(b)
        s += circ(q[0], q[1], 3, "sensor")
    s += arrow3(cam, (-150, -40, 0), (-70, -40, 0))
    p = cam.xy((xf, -66, 164))
    b = cam.xy((-130, 0, 48))
    f = cam.xy((-110, -40, 0))
    s += lab(p[0] - 6, p[1] + 2, "センサ", "end") + lab(b[0] + 10, b[1] - 34, "車体", "end")
    s += al(f[0] - 4, f[1] + 16, "搬送")
    return s


# =====================================================================================
# q:gapmeas — gap & flush: a laser-line sensor lays a line across the joint between door and fender;
# the profile of that line gives the gap width and the step (flush) between the two panels
# =====================================================================================
@picto("gapmeas")
def _():
    g, st, H = 5.0, 3.0, 110.0                  # gap, step of the door (sits further in), panel height

    def yy(z):
        return -10 * math.sin(math.pi * z / H)

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        for x0, x1, dy in ((-130, -g / 2, 0), (g / 2, 130, st)):
            xe = x1 if x0 < 0 else x0
            l.svg(surf(cam, lambda u, v: (xe, yy(H * v) + dy + 14 * u, H * v), 1, 6, "w", dark=.6))   # flange return
        for x0, x1, dy in ((-130, -g / 2, 0), (g / 2, 130, st)):
            l.svg(surf(cam, lambda u, v: (x0 + (x1 - x0) * u, yy(H * v) + dy, H * v), 2, 8, "w", dark=.25))
        # character line running across both panels
        d = ""
        for x0, x1, dy in ((-130, -g / 2, 0), (g / 2, 130, st)):
            d += seg2(cam.xy((x0, yy(74) + dy - .3, 74)), cam.xy((x1, yy(74) + dy - .3, 74)))
        l.svg(path(d, "el"))
        l.svg(bar(cam, (0, -114, 80), (0, -114, 128), 12, 12, "m"))           # robot wrist / holder
        BOX(l, -18, -126, 50, 36, 24, 30, "dk", ch=3)                         # sensor head
    s, sc = fit(fn, -22, 16, (22, 20, 214, 178), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    zl = 52
    e = cam.xy((0, -104, 58))
    a, b = cam.xy((-36, yy(zl) - .4, zl)), cam.xy((36, yy(zl) + st - .4, zl))
    s += path(P([e, a, b]), "beamf")
    s += path(seg2(a, cam.xy((-g / 2, yy(zl) - .4, zl))) + seg2(cam.xy((g / 2, yy(zl) + st - .4, zl)), b), "beam")
    # measured profile: gap and step
    x0, y0 = 226, 62
    pr = [(x0, y0), (x0 + 30, y0), (x0 + 33, y0 + 22), (x0 + 37, y0 + 22), (x0 + 40, y0 + 7), (x0 + 70, y0 + 7)]
    s += rect(x0 - 8, y0 - 24, 86, 66, "scrn", 3) + path(P(pr, False), "scrg")
    s += line(x0 + 30, y0 - 10, x0 + 30, y0 - 3, "o thin") + line(x0 + 40, y0 - 10, x0 + 40, y0 - 3, "o thin")
    s += line(x0 + 74, y0, x0 + 74, y0 + 7, "o thin")
    sn = cam.xy((-18, -126, 50))
    s += lab(sn[0] - 6, sn[1] + 6, "センサ", "end") + lab(x0 + 35, y0 - 28, "隙間")
    s += lab(x0 + 35, y0 + 60, "段差") + al(e[0] + 44, e[1] - 30, "レーザ", "start")
    return s


# =====================================================================================
# q:surfinsp — panel surface distortion: parallel light tubes over an outer panel are mirrored in its
# surface as straight stripes; a tiny dent or bump bends the stripes, so it can be seen (and measured)
# =====================================================================================
def panel_F(u, v):
    return (-120 + 240 * u, -64 + 128 * v, 24 - 12 * (2 * u - 1) ** 2 - 14 * (2 * v - 1) ** 2)


def dent(u, v, uc=.62, vc=.46, k=.1):
    return k * math.exp(-((u - uc) ** 2 / .006 + (v - vc) ** 2 / .012))


@picto("surfinsp")
def _():
    zl = 150

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        for x in (-96, 84):
            BOX(l, x, -40, -40, 12, 80, 40 + panel_F(.5 + x / 240, .2)[2] - 18, "m")   # stand
        l.svg(surf(cam, panel_F, 8, 6, "w"))                                         # outer panel (hood)
        d = ""
        for j in range(6):
            v0 = .08 + j * .15
            top = [panel_F(i / 24, v0 + dent(i / 24, v0)) for i in range(25)]
            bot = [panel_F(i / 24, v0 + .065 + dent(i / 24, v0 + .065)) for i in range(24, -1, -1)]
            d += P([cam.xy((p[0], p[1], p[2] + .3)) for p in top + bot])
        l.svg(path(d, "dks3", 'opacity=".55"'))
        for x in (-128, 120):
            BOX(l, x, -76, zl, 8, 152, 10, "dk")                                    # light frame rails
        for j in range(6):
            y = -66 + j * 26.4
            l.svg(bar(cam, (-120, y, zl + 5), (120, y, zl + 5), 9, 7, "pt"))       # light tubes
    s, sc = fit(fn, -22, 30, (22, 14, 298, 180), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    c = cam.xy(panel_F(.62, .5))
    s += ell(c[0], c[1], 20, 11, "o thin")
    t = cam.xy((-128, -76, zl + 10))
    p = cam.xy(panel_F(0, 0))
    s += lab(t[0] - 4, t[1] + 4, "ゼブラ照明", "end") + lab(p[0] + 16, p[1] + 20, "外板パネル", "start")
    s += lab(c[0] + 26, c[1] - 12, "ひずみ", "start")
    return s


# =====================================================================================
# q:paintinsp — paint appearance inspection: the baked body passes a striped light; cameras watch the
# stripes mirrored in the paint, and a speck (ブツ), crater (ハジキ) or sag (タレ) breaks the pattern
# =====================================================================================
@picto("paintinsp")
def _():
    xc = 112                                     # camera post

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -110, 130, 0, 230, 12, 176, "pt", ch=3)                         # striped light panel
        d = ""
        for k in range(8):
            x0 = -100 + k * 27.5
            d += P([cam.xy((x0, 129.7, 8)), cam.xy((x0 + 12, 129.7, 8)), cam.xy((x0 + 12, 129.7, 168)), cam.xy((x0, 129.7, 168))])
        l.svg(path(d, "dks2"))
        for y in (14, 74):
            BOX(l, -150, y, 0, 300, 12, 10, "dk")                              # conveyor rails
        biw(l, cam, mat="pt")
        d = ""
        for k in range(5):                                                     # stripes mirrored on the door
            x0 = -66 + k * 26
            d += P([cam.xy((x0, -.4, 14)), cam.xy((x0 + 10, -.4, 14)), cam.xy((x0 + 12, -.4, 52)), cam.xy((x0 + 2, -.4, 52))])
        l.svg(path(d, "dks3", 'opacity=".45"'))
        BOX(l, xc, -84, 0, 14, 14, 150, "pt", dark=1, ch=2)                     # camera post
        for z in (36, 108):
            BOX(l, xc - 8, -70, z, 30, 20, 20, "dk", ch=2)                     # cameras
            CYL(l, (xc + 7, -50, z + 10), (0, 1, 0), 7, 8, "m", seg=16)
    s, sc = fit(fn, -30, 20, (18, 20, 302, 178), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    sp = (-6, -.5, 34)
    d = seg2(cam.xy((xc + 7, -42, 46)), cam.xy(sp)) + seg2(cam.xy((xc + 7, -42, 118)), cam.xy((10, 7.5, 72)))
    s += path(d, "ray")
    q = cam.xy(sp)
    s += circ(q[0], q[1], 2.4, "probeball") + circ(q[0], q[1], 9, "o thin")
    s += arrow3(cam, (-150, -40, 0), (-70, -40, 0))
    t = cam.xy((-110, 130, 176))
    c = cam.xy((xc + 7, -84, 150))
    f = cam.xy((-110, -40, 0))
    s += lab(t[0] + 4, t[1] - 6, "縞照明", "start") + lab(c[0] + 8, c[1] - 6, "カメラ", "start")
    u = cam.xy((sp[0], -40, 0))
    s += lab(u[0] + 10, u[1] + 18, "ブツ・タレ") + al(f[0] - 4, f[1] + 16, "搬送")
    return s


# =====================================================================================
# q:color — multi-angle colour / gloss meter: one lamp lights the paint at 45 deg; receivers at several
# angles from the mirror direction read colour (and gloss) as the metallic flakes look different
# =====================================================================================
@picto("color")
def _():
    C, R = (-56, 0, 0), 70
    RX = (60, 30, 20, 0, -30)                   # receivers (from the normal; mirror direction is +45)

    def on_arc(a):                              # angle from the surface normal, + = right
        t = math.radians(a)
        return (C[0] + R * math.sin(t), 0, R * math.cos(t))

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -150, -60, -12, 300, 120, 12, "pt")                             # painted panel
        BOX(l, 30, -32, 0, 100, 60, 34, "dk", ch=8)                             # hand-held meter
        l.svg(P3(cam, [(44, -20, 34.2), (90, -20, 34.2), (90, 18, 34.2), (44, 18, 34.2)], "scrn"))
        c = cam.xy(C)
        o = path(P([cam.xy(on_arc(a)) for a in range(-80, 81, 8)], False), "o thin")
        o += path(seg2(cam.xy(on_arc(-45)), c), "beam")
        t = math.radians(-46)
        o += bar(cam, (C[0] + (R + 16) * math.sin(t), 0, (R + 16) * math.cos(t)), on_arc(-46), 12, 12, "dk")   # lamp
        o += path("".join(seg2(c, cam.xy(on_arc(a))) for a in RX), "ray")
        for a in RX:
            q = cam.xy(on_arc(a))
            o += circ(q[0], q[1], 3.2, "sensor")
        return o + circ(c[0], c[1], 2.2, "probeball")
    s, sc = fit(fn, -22, 20, (22, 24, 298, 182), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a = cam.xy(on_arc(-62))
    r = cam.xy(on_arc(45))
    p = cam.xy((-150, -60, -12))
    m = cam.xy((80, -32, 34))
    s += lab(a[0] - 10, a[1] + 2, "光源", "end") + lab(r[0] + 10, r[1] - 4, "多角度で受光", "start")
    s += lab(p[0] + 30, p[1] + 18, "塗装面", "start") + lab(m[0] + 30, m[1] - 18, "測色計", "middle")
    return s


# =====================================================================================
# q:distort — optical distortion of glass: a camera looks at a grid board through the windshield; where
# the glass is uneven the straight lines appear bent (transmitted distortion / double image)
# =====================================================================================
def _inside(pt, poly):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


@picto("distort")
def _():
    tl = math.radians(34)

    def G(u, v):                                # windshield: trapezoid, bent across, leaning back
        w = 110 - 26 * v
        x = (2 * u - 1) * w
        return (x, -40 + 90 * v * math.sin(tl) - 16 * (2 * u - 1) ** 2, 34 + 90 * v * math.cos(tl))

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -150, 120, 0, 300, 10, 176, "pt", ch=3)                        # grid board
        rim = [cam.xy(G(i / 12, 0)) for i in range(13)] + [cam.xy(G(1, .5)), cam.xy(G(1, 1))] + \
              [cam.xy(G(i / 12, 1)) for i in range(12, -1, -1)] + [cam.xy(G(0, .5))]
        d = ""
        for k in range(13):                                                   # vertical lines
            x = -138 + k * 23
            pts_ = []
            for j in range(25):
                q = cam.xy((x, 119.7, 8 + 160 * j / 24))
                if _inside(q, rim):
                    q = (q[0] + 3.2 * math.sin(q[1] / 7 + x / 30), q[1])
                pts_.append(q)
            d += P(pts_, False)
        for j in range(8):                                                    # horizontal lines
            z = 10 + j * 22.5
            pts_ = []
            for k in range(31):
                q = cam.xy((-142 + 284 * k / 30, 119.7, z))
                if _inside(q, rim):
                    q = (q[0], q[1] + 3.2 * math.sin(q[0] / 9 + z / 40))
                pts_.append(q)
            d += P(pts_, False)
        l.svg(path(d, "el"))
        for x in (-80, 66):
            BOX(l, x, -50, 0, 14, 20, 30, "m", ch=2)                           # glass rests
        l.svg(path(P(rim), "gl") + path(P(rim), "el"))
        BOX(l, -10, -188, -30, 20, 20, 50, "pt", dark=1, ch=2)                 # camera stand
        BOX(l, -18, -196, 20, 36, 40, 28, "dk", ch=3)                         # camera
        CYL(l, (0, -156, 34), (0, 1, 0), 10, 12, "m", seg=18)                  # lens
    s, sc = fit(fn, -24, 18, (22, 16, 298, 180), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    b = cam.xy((150, 120, 176))
    g = cam.xy(G(1, 0))
    c = cam.xy((-18, -196, 34))
    s += lab(b[0] - 4, b[1] - 6, "格子板", "end") + lab(g[0] + 6, g[1] + 22, "ガラス", "start")
    s += lab(c[0] - 6, c[1] + 4, "カメラ", "end")
    return s


# =====================================================================================
# q:weigh — weight sorting: each part stops on a load-cell scale, is weighed, then pushed off the
# conveyor into the bin of its weight rank
# =====================================================================================
def piston(l, x, y, z0, r=16):
    """piston (crown up) with two ring grooves drawn on its visible half."""
    CYL(l, (x, y, z0), (0, 0, 1), r, 24, "w", seg=24, bands=6)
    cam = l.cam
    d = ""
    for z in (z0 + 15, z0 + 19.5):
        pts_ = [(math.cos(2 * PI * k / 24), math.sin(2 * PI * k / 24)) for k in range(25)]
        vis = [cam.xy((x + r * c, y + r * s_, z)) for c, s_ in pts_ if GE._dot((c, s_, 0), cam.D) < -.05]
        d += P(vis, False)
    l.svg(path(d, "el"))


@picto("weigh")
def _():
    zt = -8                                     # conveyor / pan top

    def fn(sc):
        l = L(sc)
        cam = sc.cam
        BOX(l, -40, 40, -50, 10, 10, 120, "pt", dark=1)                        # display post
        BOX(l, -58, 34, 52, 46, 14, 28, "dk", ch=2)                            # weight display
        l.svg(P3(cam, [(-52, 33.8, 58), (-10, 33.8, 58), (-10, 33.8, 74), (-52, 33.8, 74)], "scrn"))
        for x in (40, 90, 140):
            CYL(l, (x, 70, zt + 12), (0, -1, 0), 5, 34, "m", seg=12, bands=4)   # pushers
            CYL(l, (x, 36, zt + 12), (0, -1, 0), 10, 6, "dk", seg=16, bands=4)
        BOX(l, -176, -26, -50, 116, 52, 36, "pt", dark=1)                      # in conveyor
        BOX(l, -176, -24, -14, 116, 48, 6, "dk")
        BOX(l, -46, -18, -50, 42, 36, 36, "m")                                 # load cell
        BOX(l, -56, -26, -14, 62, 52, 6, "t")                                  # weighing pan
        BOX(l, 16, -26, -50, 160, 52, 36, "pt", dark=1)                        # out conveyor
        BOX(l, 16, -24, -14, 160, 48, 6, "dk")
        piston(l, -136, 0, zt)
        piston(l, -25, 0, zt)
        piston(l, 140, 0, zt)
        for x in (40, 90, 140):                                                # rank bins
            BOX(l, x - 22, -86, -50, 44, 44, 26, "m", ch=2)
            l.svg(P3(cam, [(x - 18, -82, -23.8), (x + 18, -82, -23.8), (x + 18, -46, -23.8), (x - 18, -46, -23.8)], "bg"))
        piston(l, 90, -64, -40, 15)
    s, sc = fit(fn, -26, 26, (18, 18, 302, 178), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-170, -40, -50), (-100, -40, -50))
    s += arrow3(cam, (90, 10, zt + 44), (90, -50, zt + 44))
    p = cam.xy((-56, -26, -14))
    b = cam.xy((176, -86, -50))
    d = cam.xy((-58, 34, 80))
    f = cam.xy((-170, -40, -50))
    s += lab(p[0] - 2, p[1] - 30, "計量", "end") + lab(b[0] - 4, b[1] + 16, "ランク分け", "end")
    s += lab(d[0] - 6, d[1] + 4, "重量表示", "end") + al(f[0] + 6, f[1] + 16, "搬送", "start")
    return s
