"""v3 principle drawings (shaded 3D style), team qg2: sheet-metal & plate work (press brake, busbar
machine, plasma/gas cutting, bending roll, turret punch), arc welding, overhead crane, hydraulic bolt
tensioner, shaft alignment and catalyst canning. Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il_pictos_ind import person
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def Y(sc, y0, L, xz, mat="pt", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded along +y from y0."""
    loop = [(-p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L, mat, **kw)),
           ((min(xs), min(y0, y0 + L), min(zs)), (max(xs), max(y0, y0 + L), max(zs))), bias)


def cyl_svg(cam, O, A, r, h, mat, r1=None, seg=20):
    """cylinder / frustum drawn directly (outside the Scene ordering), for items drawn on top."""
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, 10), h, mat, smooth=True, scale=scale))


def ring2(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=28, r1=None, **kw):
    CYL(sc, O, A, ro, h, mat, bias, seg, r1=r1, holes=[GE.circle_outline(ri, seg, 6)], bands=7, **kw)


def strip_x(sc, x0, L, pts, t, mat="w", bias=0.0, **kw):
    """thin plate along x whose (y, z) centre line is pts; split into convex quads (one per segment)."""
    for (y1, z1), (y2, z2) in zip(pts, pts[1:]):
        d = math.hypot(y2 - y1, z2 - z1)
        ny, nz = -(z2 - z1) / d * t / 2, (y2 - y1) / d * t / 2
        X(sc, x0, L, [(y1 - ny, z1 - nz), (y2 - ny, z2 - nz), (y2 + ny, z2 + nz), (y1 + ny, z1 + nz)], mat, bias, **kw)


# =====================================================================================
# q:pressbrake — the ram pushes a long punch into a V die; the sheet's two flanges rise
# =====================================================================================
@picto("pressbrake")
def _():
    zc, k = -5.0, 0.32                          # underside of the sheet on the bend line, flange slope

    def fn(sc):
        # lower beam (bed) + die holder + V die (two convex halves)
        BOX(sc, -150, -14, -96, 300, 28, 62, "pt", dark=1)
        BOX(sc, -140, -16, -34, 280, 32, 12, "m")
        X(sc, -130, 260, [(-16, -22), (0, -22), (0, -11), (-7, 0), (-16, 0)], "t")
        X(sc, -130, 260, [(0, -22), (16, -22), (16, 0), (7, 0), (0, -11)], "t")
        # sheet: two flanges meeting on the bend line
        strip_x(sc, -112, 224, [(-110, zc + 110 * k + 1.5), (0, zc + 1.5)], 3, "w", -1)
        strip_x(sc, -112, 224, [(0, zc + 1.5), (110, zc + 110 * k + 1.5)], 3, "w", -1)
        # punch, holder and ram
        X(sc, -130, 260, [(0, -2), (9, 16), (9, 54), (-9, 54), (-9, 16)], "t", -1)
        BOX(sc, -140, -15, 54, 280, 30, 14, "m")
        BOX(sc, -150, -16, 68, 300, 32, 50, "pt", dark=1)
        for x in (-110, 110):
            CYL(sc, (x, 0, 118), (0, 0, 1), 18, 34, "dk", seg=24)                  # hydraulic cylinders
        # back gauge: rail + two fingers behind the sheet
        BOX(sc, -60, 118, 34, 200, 14, 12, "m")
        for x in (-30, 80):
            BOX(sc, x, 110, 46, 20, 22, 16, "dk")
    s, sc = fit(fn, 40, 26, (40, 26, 284, 180), sh_ry=7, sh_k=.45, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-40, 0, 178), (-40, 0, 128))
    s += arc3(cam, (-120, 0, zc), (1, 0, 0), 120, 172, 148)
    a = cam.xy((-40, 0, 165))
    p = cam.xy((-150, 16, 80))
    d = cam.xy((-130, -16, -14))
    g = cam.xy((80, 132, 70))
    w = cam.xy((-112, -110, zc + 110 * k))
    s += al(a[0] - 7, a[1] + 4, "加圧", "end")
    s += lab(p[0] - 8, p[1] + 2, "パンチ", "end") + lab(d[0] - 10, d[1] + 6, "ダイ", "end")
    s += lab(g[0] + 12, g[1] - 8, "突当て", "start")
    return s


# =====================================================================================
# q:rollbend — 3-roll pyramid: the top roll presses down, the bottom rolls drive the plate
# back and forth; the plate curls into a shell that wraps around the top roll
# =====================================================================================
@picto("rollbend")
def _():
    R, t = 110.0, 6.0
    cz = 4.24 + R                               # centre of the rolled shell (plate underside radius R)
    rb, yb, rt, zt = 24.0, 70.0, 30.0, 40.2

    def fn(sc):
        # roll housing (right end) and base
        BOX(sc, 150, -110, -70, 34, 220, 120, "pt", dark=1)
        BOX(sc, -170, -110, -100, 354, 220, 30, "pt", dark=1)
        for yy, zz, r in ((-yb, 0, rb), (yb, 0, rb), (0, zt, rt)):
            CYL(sc, (-150, yy, zz), (1, 0, 0), r * .45, 20, "m", seg=20)            # journal
            CYL(sc, (-130, yy, zz), (1, 0, 0), r, 280, "m", seg=40)                # roll
        # plate: straight lead-in tangent to the front roll, then the rolled arc around the top roll
        Rm = R - t / 2
        z0 = cz - Rm                                                               # mid-plane under the top roll
        z1 = rb + t / 2
        sl = (z1 - z0) / yb
        strip_x(sc, -100, 200, [(-yb - 80, z1 + sl * 80), (-yb, z1), (0, z0)], t, "w")
        pts = []
        for k in range(14):
            a = 270 + k * 12                                                       # around the back, up to the top
            pts.append((Rm * math.cos(math.radians(a)), cz + Rm * math.sin(math.radians(a))))
        strip_x(sc, -100, 200, pts, t, "w")
    s, sc = fit(fn, 52, 16, (30, 16, 292, 176), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-140, 0, zt + 90), (-140, 0, zt + 40))
    s += arc3(cam, (-131, -yb, 0), (1, 0, 0), rb + 10, 230, 150)
    a = cam.xy((-140, 0, zt + 90))
    b = cam.xy((-131, -yb, -rb - 10))
    w = cam.xy((-100, 40, cz + R))
    s += al(a[0] - 6, a[1] + 4, "押込み", "end") + al(b[0], b[1] + 16, "回転")
    s += lab(w[0] + 10, w[1] - 8, "胴板（円筒）", "start")
    return s


# =====================================================================================
# q:busbar — one machine, three stations: punch holes, shear to length, bend (copper bar)
# =====================================================================================
@picto("busbar")
def _():
    sx = (-110, 0, 110)                          # station centres along x
    bw, bt = 13, 5                               # bar half-width (y), thickness (z)

    def fn(sc):
        BOX(sc, -200, -40, -60, 400, 80, 54, "pt", dark=1)                     # machine base / table
        BOX(sc, -196, -36, -6, 392, 72, 6, "m")                               # table top
        for c in sx:                                                          # C-shaped heads
            BOX(sc, c - 18, 24, 0, 36, 22, 96, "pt", dark=1)
            BOX(sc, c - 18, -22, 96, 36, 68, 26, "pt", dark=1)
            BOX(sc, c - 11, -15, 80, 22, 30, 16, "dk")                         # ram
        # station 1: round punch over a die button
        CYL(sc, (sx[0], 0, 80), (0, 0, -1), 5, 62, "t", seg=20)
        # station 2: shear blade (inclined edge)
        Y(sc, -20, 40, [(-3, 26), (3, 26), (3, 80), (-3, 80)], "t", -1)
        # station 3: V punch + V die, bent bar piece between them
        c = sx[2]
        Y(sc, -20, 40, [(c, 16), (c + 10, 32), (c + 10, 80), (c - 10, 80), (c - 10, 32)], "t", -1)
        Y(sc, -20, 40, [(c - 24, 0), (c, 0), (c, 4), (c - 7, 14), (c - 24, 14)], "t")
        Y(sc, -20, 40, [(c, 0), (c + 24, 0), (c + 24, 14), (c + 7, 14), (c, 4)], "t")
        for sgn in (-1, 1):
            p0, p1 = (c, 9.5), (c + sgn * 46, 9.5 + 46 * .62)
            d = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            nx, nz = -(p1[1] - p0[1]) / d * bt / 2 * sgn, (p1[0] - p0[0]) / d * bt / 2 * sgn
            Y(sc, -bw, 2 * bw, [(p0[0] - nx, p0[1] - nz), (p1[0] - nx, p1[1] - nz), (p1[0] + nx, p1[1] + nz), (p0[0] + nx, p0[1] + nz)],
              "cu", -1)
        # copper bar fed from the left up to the shear
        X(sc, -230, 230, [(-bw, 0), (bw, 0), (bw, bt), (-bw, bt)], "cu", -1)

        def holes(s_):
            o = ""
            for x in (-200, -164, -128):
                o += hole3(s_.cam, (x, 0, bt + .2), (0, 0, 1), 4.6, "bg")
            return o
        RAW(sc, holes, ((-206, -6, bt + .1), (-122, 6, bt + .3)), -2)
    s, sc = fit(fn, -24, 22, (16, 34, 304, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for c, name in zip(sx, ("穴あけ", "切断", "曲げ")):
        p = cam.xy((c, -22, 140))
        s += lab(p[0], p[1] - 4, name)
    s += arrow3(cam, (-236, -30, 22), (-190, -30, 22))
    f = cam.xy((-213, -30, 22))
    s += al(f[0], f[1] + 22, "送り")
    return s


# =====================================================================================
# q:plasma — gantry cutting machine: the torch melts through a thick plate on a grate table;
# the gantry travels along the rails (X) and the torch carriage across the bridge (Y)
# =====================================================================================
@picto("plasma")
def _():
    gx, ty = 40, -10                              # gantry position, torch position across

    def fn(sc):
        BOX(sc, -160, -86, -70, 300, 172, 44, "pt", dark=1)                   # water / fume table
        for k in range(12):                                                   # grate slats
            BOX(sc, -130 + k * 22, -80, -26, 4, 160, 22, "dk")
        BOX(sc, -140, -66, -4, 260, 132, 10, "w")                              # thick steel plate
        for y in (-122, 108):                                                 # rails
            BOX(sc, -190, y, -70, 360, 14, 12, "m")
        # gantry: two end trucks + bridge beam
        for y in (-128, 96):
            BOX(sc, gx - 26, y, -58, 52, 32, 30, "pt", ch=4)
            BOX(sc, gx - 14, y + 6, -28, 28, 20, 134, "pt", dark=1)
        BOX(sc, gx - 18, -128, 106, 36, 256, 30, "pt")
        # torch carriage on the front (-x) face of the bridge, torch down to the plate
        BOX(sc, gx - 40, ty - 18, 80, 22, 36, 64, "m", -1)

        def marks(s_):
            cam = s_.cam
            zt = 6.3
            o = ""
            # a finished part (kerf all round) and the kerf being cut now
            pr = [(-120, -50), (-40, -50), (-40, 50), (-120, 50)]
            o += path(P([cam.xy((x, y, zt)) for x, y in pr]), "kerf")
            o += hole3(cam, (-80, 0, zt), (0, 0, 1), 18, "kerf")
            o += path(P([cam.xy((x, y, zt)) for x, y in ((gx - 30, -50), (gx - 30, ty))], False), "kerf")
            return o
        RAW(sc, marks, ((-140, -66, 6.1), (120, 66, 6.4)), -1)
        return cyl_svg(sc.cam, (gx - 30, ty, 80), (0, 0, -1), 7, 46, "dk") + cyl_svg(sc.cam, (gx - 30, ty, 34), (0, 0, -1), 7, 18, "cu", r1=3.4)
    s, sc = fit(fn, 30, 26, (24, 24, 296, 176), sh_ry=7, sh_k=.45, ret_scene=True)
    cam = sc.cam
    tx, tyy = cam.xy((gx - 30, ty, 16))
    px, py = cam.xy((gx - 30, ty, 6))
    s += path("M%s %s L%s %s" % (n(tx), n(tyy), n(px), n(py + 4)), "jet2") + sparks(px, py + 2, 12, 7, -170, -10)
    s += arrow3(cam, (gx - 60, -150, -58), (gx + 50, -150, -58), both=True)
    s += arrow3(cam, (gx - 22, -80, 150), (gx - 22, 60, 150), both=True)
    a = cam.xy((gx - 5, -150, -58))
    b = cam.xy((gx - 22, -10, 150))
    c = cam.xy((gx - 40, ty, 110))
    s += al(a[0], a[1] + 18, "走行") + al(b[0], b[1] - 10, "横行")
    s += lab(c[0] - 10, c[1] + 4, "トーチ", "end")
    w = cam.xy((-140, 66, 6))
    s += lab(w[0] - 4, w[1] - 6, "厚板", "end")
    return s


# =====================================================================================
# q:turretpunch — the sheet, gripped by clamps, moves in X/Y between an upper turret of punches
# and a lower turret of dies; the striker hits the punch under it, the turrets index
# =====================================================================================
@picto("turretpunch")
def _():
    rt, rr = 80, 62                               # turret radius, tool circle radius

    def fn(sc):
        # frame: lower body + upper arm reaching over the turrets (throat open to the front)
        BOX(sc, -110, -40, -110, 220, 160, 70, "pt", dark=1)
        BOX(sc, -60, 96, -40, 120, 34, 180, "pt", dark=1)
        BOX(sc, -60, -86, 104, 120, 216, 36, "pt", dark=1)
        # lower turret (dies) and upper turret (punches)
        CYL(sc, (0, 0, -30), (0, 0, 1), rt, 30, "m", seg=44)
        CYL(sc, (0, 0, 60), (0, 0, 1), rt, 24, "m", seg=44)
        for k in range(8):
            a = math.radians(-90 + k * 45)
            x, y = rr * math.cos(a), rr * math.sin(a)
            CYL(sc, (x, y, 36 if k else 3), (0, 0, 1), 8, 24 if k else 57, "t", seg=14, bands=6, bias=-.5)
        # striker over the front tool station
        BOX(sc, -12, -rr - 12, 84, 24, 24, 20, "dk", -1)
        # sheet + carriage with two clamps on its front edge
        BOX(sc, -230, -150, 0, 300, 190, 3, "w", -1)
        BOX(sc, -240, -176, -6, 320, 20, 16, "m", -1)
        for x in (-180, -60):
            BOX(sc, x, -160, -2, 28, 22, 10, "dk", -2)

        def marks(s_):
            cam = s_.cam
            o = ""
            for i in range(4):
                for j in range(3):
                    x, y = -190 + i * 30, -100 + j * 40
                    if j == 0:
                        o += hole3(cam, (x, y, 3.2), (0, 0, 1), 6, "bg")
                    elif j == 1:
                        o += path(P([cam.xy((x + u, y + v, 3.2)) for u, v in ((-7, -7), (7, -7), (7, 7), (-7, 7))]), "bg")
                    else:
                        o += path(P([cam.xy((x + u, y + v, 3.2)) for u, v in ((-9, -3), (9, -3), (9, 3), (-9, 3))]), "bg")
            return o
        RAW(sc, marks, ((-200, -110, 3.1), (-90, 30, 3.3)), -3)
    s, sc = fit(fn, -30, 28, (20, 22, 300, 178), sh_ry=7, sh_k=.45, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 84), (0, 0, 1), rt + 12, 200, 290)
    s += arrow3(cam, (0, -rr, 150), (0, -rr, 112))
    s += arrow3(cam, (-230, -196, -6), (-130, -196, -6), both=True)
    s += arrow3(cam, (-252, -160, -6), (-252, -90, -6), both=True)
    a = cam.xy((0, -rr, 150))
    b = cam.xy((-rt - 12, 0, 84))
    c = cam.xy((-180, -196, -6))
    s += al(a[0] + 6, a[1] + 2, "打抜き", "start") + al(b[0] - 12, b[1] + 8, "割出し", "end")
    s += al(c[0], c[1] + 18, "板をX・Y移動")
    return s


def hexnut(sc, c, z0, h, r, mat="w", bias=0.0, rot=0.0):
    pts = [(c[0] + r * math.cos(math.radians(rot + 60 * k)), c[1] + r * math.sin(math.radians(rot + 60 * k))) for k in range(6)]
    Z(sc, z0, h, pts, mat, bias)


def unit(v):
    d = math.sqrt(sum(a * a for a in v))
    return tuple(a / d for a in v)


def add(p, v, k=1.0):
    return tuple(p[i] + v[i] * k for i in range(3))


# =====================================================================================
# q:mig_tig — semi-automatic arc welding: power source + wire feeder, hose to the torch,
# the arc melts the wire into a fillet bead along the joint (TIG: tungsten + filler rod)
# =====================================================================================
@picto("mig_tig")
def _():
    tip = (62, -9, 17)
    u1 = unit((.55, -.45, .70))                   # nozzle axis (tip -> back)
    u2 = unit((.75, -.2, .63))                    # neck
    u3 = unit((.95, 0, .3))                       # handle

    def fn(sc):
        BOX(sc, -80, -66, -50, 220, 110, 50, "m", dark=1)                     # welding table
        BOX(sc, -70, -50, 0, 200, 80, 8, "w")                                   # base plate
        BOX(sc, -70, 0, 8, 200, 8, 58, "w")                                     # web plate (T-joint)
        X(sc, -70, 128, banded(hull([(0, 8), (-1, 8)] + arc(0, 8, 8, 180, 270, 2) + arc(0, 8, 8, 90, 180, 2) +
                                [(-6, 8 + 6 * .4), (-3, 11.6)]), 2), "w", -1, smooth=True, dark=1)    # fillet bead
        # power source with the wire feeder (spool) on top
        BOX(sc, -230, -44, -50, 92, 88, 120, "pt", ch=5)
        BOX(sc, -226, -40, 70, 84, 80, 46, "pt", ch=4, dark=1)
        CYL(sc, (-184, -40, 93), (0, -1, 0), 18, 4, "dk", seg=28, bias=-1)
        CYL(sc, (-184, -44, 93), (0, -1, 0), 12, 3, "cu", seg=24, bias=-1.5)
        # torch: nozzle, gooseneck, handle
        CYL(sc, tip, u1, 5, 26, "cu", seg=18, r1=8.5, bias=-3)
        n1 = add(tip, u1, 26)
        CYL(sc, n1, u2, 5.5, 28, "dk", seg=16, bias=-3)
        n2 = add(n1, u2, 28)
        CYL(sc, n2, u3, 9, 60, "dk", seg=18, bias=-3)

        def marks(s_):
            cam = s_.cam
            o = ""
            for x, z in ((-210, 40), (-210, 18)):
                o += hole3(cam, (x, -44.3, z), (0, -1, 0), 6, "m")
            o += path(P([cam.xy((-226, -44.3, z)) for z in (-10, -10)] + [cam.xy((-160, -44.3, -10))], False), "o")
            return o
        RAW(sc, marks, ((-230, -44.4, -20), (-138, -44.2, 60)), -2)
    s, sc = fit(fn, -22, 22, (14, 30, 304, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    tip_s = cam.xy(tip)
    a0 = cam.xy((62, -4, 9))
    s += ell(a0[0], a0[1], 6, 2.6, "h") + sparks(a0[0], a0[1] - 1, 11, 7, -170, -10)
    h_end = cam.xy(add(add(add(tip, u1, 26), u2, 28), u3, 60))
    f = cam.xy((-184, -50, 112))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(h_end[0]), n(h_end[1]), n(h_end[0] + 24), n(h_end[1] - 10),
                                              n(f[0] + 70), n(f[1] - 40), n(f[0] + 34), n(f[1] + 2)), "cable")
    s += arrow3(cam, (20, -40, 30), (56, -40, 30))
    p = cam.xy((-184, -44, -50))
    w = cam.xy((-184, -44, 128))
    b = cam.xy((-74, -6, 12))
    s += lab(p[0], p[1] + 16, "溶接電源") + lab(w[0], w[1] - 6, "ワイヤ送給")
    s += lab(h_end[0] + 4, h_end[1] + 22, "トーチ", "start") + lab(b[0] - 6, b[1] + 4, "ビード", "end")
    return s


# =====================================================================================
# q:ohcrane — bridge on two runway girders (travel), trolley across the bridge (traverse),
# hoist drum lowers the hook; a heavy load hangs in slings; small figure for scale
# =====================================================================================
@picto("ohcrane")
def _():
    yb, xt, zl = 10, 30, 70                       # bridge position, trolley position, load top

    def fn(sc):
        BOX(sc, -190, -110, -6, 380, 220, 6, "m", dark=1)                      # shop floor (slab)
        for x in (-178, 162):
            for y in (-100, 84):
                BOX(sc, x, y, 0, 16, 16, 200, "pt", dark=1)                     # columns
            BOX(sc, x - 2, -110, 200, 20, 220, 18, "pt", dark=1)                # runway girders
        for x in (-182, 158):
            BOX(sc, x, yb - 28, 218, 24, 56, 18, "dk")                          # end trucks
        for y in (yb - 24, yb + 12):
            BOX(sc, -170, y, 222, 340, 12, 30, "pt")                            # box girders
        BOX(sc, xt - 34, yb - 30, 252, 68, 60, 22, "pt", dark=1)                # trolley
        CYL(sc, (xt - 24, yb - 31, 263), (0, -1, 0), 9, 4, "m", seg=18, bias=-1)
        BOX(sc, xt - 12, yb - 8, 112, 24, 16, 22, "dk")                          # hook block
        # load: heavy fabricated block on blocks, lifted clear of the floor
        BOX(sc, xt - 70, yb - 46, zl - 64, 140, 92, 64, "w", ch=6)

        def ropes(s_):
            cam = s_.cam
            o = ""
            for dx in (-6, 6):
                a, b = cam.xy((xt + dx, yb, 222)), cam.xy((xt + dx, yb, 134))
                o += line(a[0], a[1], b[0], b[1], "rail")
            return o
        RAW(sc, ropes, ((xt - 7, yb - 1, 134), (xt + 7, yb + 1, 222)))

        def slings(s_):
            cam = s_.cam
            h = cam.xy((xt, yb, 104))
            o = path("M%s %s q0 8 -5 8" % (n(h[0]), n(h[1] + 8)), "rail")
            for dx, dy in ((-60, -40), (60, -40)):
                b = cam.xy((xt + dx, yb + dy, zl))
                o += line(h[0], h[1] + 4, b[0], b[1], "o")
            return o
        RAW(sc, slings, ((xt - 60, yb - 41, zl), (xt + 60, yb - 39, 112)), -2)
    s, sc = fit(fn, -26, 16, (26, 14, 296, 184), sh=False, ret_scene=True)
    cam = sc.cam
    f = cam.xy((0, 0, -6))
    s = shadow(f[0], f[1] + 18, 120, 6) + s
    s += arrow3(cam, (xt - 80, yb - 40, 290), (xt + 80, yb - 40, 290), both=True)
    s += arrow3(cam, (-210, -90, 236), (-210, 80, 236), both=True)
    s += arrow3(cam, (xt + 96, yb - 40, 160), (xt + 96, yb - 40, 100), both=True)
    a = cam.xy((xt, yb - 40, 290))
    b = cam.xy((-210, -90, 236))
    c = cam.xy((xt + 96, yb - 40, 130))
    s += al(a[0], a[1] - 6, "横行") + al(b[0] - 2, b[1] + 16, "走行")
    s += al(c[0] + 6, c[1] + 4, "巻上げ", "start")
    g = cam.xy((xt + 130, -90, 0))
    s += person(g[0], g[1], 15)
    w = cam.xy((xt - 74, yb - 46, zl - 40))
    s += lab(w[0] - 12, w[1] + 4, "数十〜数百t", "end")
    return s


# =====================================================================================
# q:tensioner — jack pulls the stud up (stretch), the nut is turned down onto its seat
# through the bridge window, then the oil pressure is released
# =====================================================================================
@picto("tensioner")
def _():
    def fn(sc):
        BOX(sc, -110, -60, -70, 220, 120, 50, "pt", dark=1, ch=4)                # lower member (housing)
        BOX(sc, -100, -54, -20, 200, 108, 40, "m", ch=4)                         # clamped cap
        for x in (-62, 62):                                                       # neighbouring studs with nuts
            hexnut(sc, (x, 18), 20, 16, 15, "w", rot=30)
            CYL(sc, (x, 18, 36), (0, 0, 1), 8.5, 40, "w", seg=18)
        hexnut(sc, (0, 0), 24, 18, 18, "w", -1, rot=30)                           # nut, lifted 4 from the seat
        for k in range(3):                                                        # bridge legs around the nut
            a = math.radians(90 + 120 * k)
            CYL(sc, (34 * math.cos(a), 34 * math.sin(a), 20), (0, 0, 1), 6, 64, "m", seg=14, bias=-.5)
        CYL(sc, (0, 0, 84), (0, 0, 1), 46, 50, "pt", seg=44, dark=1)              # hydraulic cylinder
        CYL(sc, (0, 0, 134), (0, 0, 1), 32, 10, "m", seg=36)                     # piston
        hexnut(sc, (0, 0), 144, 18, 20, "dk", rot=30)                             # puller nut
        CYL(sc, (0, 0, 162), (0, 0, 1), 10, 10, "w", seg=20)                     # stud end
        CYL(sc, (0, 0, 42), (0, 0, 1), 10, 42, "w", seg=20, bias=.5)             # stud (seen in the window)
        BOX(sc, 150, -30, -70, 70, 60, 50, "pt", ch=4)                            # pump unit
    s, sc = fit(fn, -26, 24, (30, 26, 290, 178), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    h0, h1 = cam.xy((46, -6, 104)), cam.xy((150, -10, -20))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(h0[0]), n(h0[1]), n(h0[0] + 40), n(h0[1]), n(h1[0] - 10), n(h1[1] - 50),
                                              n(h1[0] + 8), n(h1[1])), "cable")
    gx, gy = cam.xy((185, -30, -36))
    s += circ(gx, gy, 7, "m") + line(gx, gy, gx + 4, gy - 4, "o")
    s += arrow3(cam, (0, 0, 176), (0, 0, 216))
    s += arc3(cam, (0, 0, 33), (0, 0, 1), 28, 40, -30)
    a = cam.xy((0, 0, 206))
    j = cam.xy((-46, 0, 110))
    t = cam.xy((-110, -60, 40))
    s += al(a[0] + 8, a[1] + 4, "引っ張る", "start") + lab(j[0] - 8, j[1] + 4, "油圧ジャッキ", "end")
    s += al(t[0] - 4, t[1] + 4, "回す", "end")
    p = cam.xy((185, 0, -70))
    s += lab(p[0], p[1] + 16, "油圧ポンプ")
    return s


# =====================================================================================
# q:shaftalign — laser units clamped on both shafts measure offset & angle across the coupling;
# shims under the generator feet correct it
# =====================================================================================
@picto("shaftalign")
def _():
    zs, dz = 60, 4                                 # shaft height, generator offset (exaggerated)

    def fn(sc):
        BOX(sc, -230, -70, -14, 460, 140, 14, "m", dark=1)                       # common base
        BOX(sc, -220, -52, 0, 120, 104, 116, "pt", dark=1, ch=6)                 # engine
        CYL(sc, (-100, 0, zs), (1, 0, 0), 13, 74, "w", seg=24)                   # engine shaft
        CYL(sc, (-26, 0, zs), (1, 0, 0), 32, 20, "m", seg=36)                    # coupling half
        CYL(sc, (8, 0, zs + dz), (1, 0, 0), 32, 20, "m", seg=36)                 # coupling half (generator)
        CYL(sc, (28, 0, zs + dz), (1, 0, 0), 13, 54, "w", seg=24)                # generator shaft
        BOX(sc, 82, -48, 10, 128, 96, 104, "pt", ch=6)                           # generator
        for x in (92, 170):
            for y in (-60, 40):
                BOX(sc, x, y, 3, 30, 20, 7, "pt", dark=1)                          # feet
                BOX(sc, x - 2, y - 2, 0, 34, 24, 3, "t", -1)                       # shims
        for x, z in ((-70, zs), (58, zs + dz)):                                   # laser units on brackets
            CYL(sc, (x - 7, 0, z), (1, 0, 0), 17, 14, "dk", seg=20)
            BOX(sc, x - 4, -4, z + 16, 8, 8, 30, "dk")
            BOX(sc, x - 12, -14, z + 46, 24, 28, 22, "dk", ch=3)
    s, sc = fit(fn, -24, 20, (20, 30, 300, 172), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((-58, -4, zs + 57)), cam.xy((46, -4, zs + dz + 57))
    s += line(a[0], a[1], b[0], b[1], "beam") + circ(a[0], a[1], 2.6, "gl") + circ(b[0], b[1], 2.6, "gl")
    s += arrow3(cam, (100, -110, 1.5), (100, -66, 1.5))
    m = cam.xy((-6, -4, zs + 76))
    e = cam.xy((-160, -52, 116))
    g = cam.xy((146, -48, 114))
    h = cam.xy((100, -110, 1.5))
    s += lab(m[0], m[1] - 6, "レーザ") + lab(e[0], e[1] - 8, "機関") + lab(g[0], g[1] - 8, "発電機")
    s += al(h[0] - 6, h[1] + 6, "シム", "end")
    return s


# =====================================================================================
# q:canning — catalyst substrate wrapped in a holding mat is pushed through a cone into the
# stainless shell, then the shell is sized down (diameter reduced) to grip it
# =====================================================================================
@picto("canning")
def _():
    xs = -70                                       # substrate front (left) face

    def fn(sc):
        BOX(sc, -150, -60, -76, 380, 120, 16, "m", dark=1)                       # bed
        for x in (40, 170):
            BOX(sc, x - 10, -30, -60, 20, 60, 14, "dk")                          # shell supports
        ring2(sc, (xs, 0, 0), (1, 0, 0), 40, 33, 130, "pt", dark=1)       # holding mat
        CYL(sc, (xs, 0, 0), (1, 0, 0), 33, 130, "w", seg=28, bias=.5, bands=8)   # ceramic substrate
        ring2(sc, (10, 0, 0), (1, 0, 0), 54, 40.5, 22, "t", -.5, r1=46)          # stuffing cone
        ring2(sc, (32, 0, 0), (1, 0, 0), 46, 43, 110, "w")                        # shell
        ring2(sc, (142, 0, 0), (1, 0, 0), 46, 43, 10, "w", r1=42)
        ring2(sc, (152, 0, 0), (1, 0, 0), 42, 39, 60, "w")                        # sized (reduced) section

        def face(s_):
            cam = s_.cam
            o = ""
            for k in range(-3, 4):                                               # honeycomb cells on the end face
                v = k * 9.0
                h = math.sqrt(max(0, 33 ** 2 - v * v)) - 1
                p0, p1 = cam.xy((xs - .3, v, -h)), cam.xy((xs - .3, v, h))
                q0, q1 = cam.xy((xs - .3, -h, v)), cam.xy((xs - .3, h, v))
                o += line(p0[0], p0[1], p1[0], p1[1], "o thin") + line(q0[0], q0[1], q1[0], q1[1], "o thin")
            return o
        RAW(sc, face, ((xs - .4, -33, -33), (xs - .2, 33, 33)), -2)
    s, sc = fit(fn, 30, 16, (24, 34, 296, 170), sh_ry=6, sh_k=.45, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-140, 0, 0), (-90, 0, 0))
    for z in (1, -1):
        s += arrow3(cam, (180, -10, z * 78), (180, -10, z * 50))
    a = cam.xy((-130, 0, 0))
    m = cam.xy((-10, 0, 46))
    sh = cam.xy((90, 0, 46))
    r = cam.xy((180, -10, 78))
    s += al(a[0], a[1] + 18, "押込み") + lab(m[0] - 4, m[1] - 10, "担体＋保持マット", "end")
    s += lab(sh[0] + 2, sh[1] - 10, "外筒") + al(r[0] + 8, r[1] - 2, "縮径", "start")
    return s
