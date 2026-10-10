"""v3 principle drawings (shaded 3D style) for the turning / machining / grinding equipment groups.
Overrides the older flat drawings of the same keys."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3

PI = math.pi


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def grit(sc, C, A, r, bias=-1.0):
    """dotted ring on a grinding wheel's visible face (centre C, outward normal A)."""
    a = GE._norm(A)

    def f(s_):
        return path(P(circ3(s_.cam, C, a, r, 40)), "grit")
    lo = tuple(C[i] - (r if abs(a[i]) < .99 else .3) for i in range(3))
    hi = tuple(C[i] + (r if abs(a[i]) < .99 else .3) for i in range(3))
    RAW(sc, f, (lo, hi), bias)


def RG(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=48, **kw):
    """ring with a smooth (few-band) bore: much smaller than il3_lib.RING."""
    CYL(sc, O, A, ro, h, mat, bias, seg, holes=[GE.circle_outline(ri, seg, 8)], **kw)


def pt3(C, A, r, ang):
    """point on a circle around axis A through C at angle ang (deg, GE.frame(A))."""
    E1, E2, _ = GE.frame(A)
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return tuple(C[i] + r * (c * E1[i] + s_ * E2[i]) for i in range(3))


# =====================================================================================
# q:vturn — vertical lathe: the chuck table turns the heavy work about a vertical axis,
# the tool on the ram feeds down / across
# =====================================================================================
@picto("vturn")
def _():
    zt = 30                                     # top of the work

    def fn(sc):
        CYL(sc, (0, 0, -40), (0, 0, 1), 100, 18, "m", seg=64, dark=.3)     # chuck table
        for k in range(4):                                                  # jaws
            t = math.radians(45 + 90 * k)
            c, s_ = math.cos(t), math.sin(t)
            Z(sc, -22, 16, [(u * c - v * s_, u * s_ + v * c) for u, v in ((70, -8), (90, -8), (90, 8), (70, 8))], "dk", -.5)
        RG(sc, (0, 0, -22), (0, 0, 1), 74, 34, 10, "w", seg=56)        # flange
        RG(sc, (0, 0, -12), (0, 0, 1), 60, 34, zt + 12, "w", seg=56)   # hub / housing
        # ram + tool holder from above, insert on the outer diameter
        tx, ty = 60 * math.cos(math.radians(-20)), 60 * math.sin(math.radians(-20))
        BOX(sc, tx - 6, ty - 13, zt + 22, 30, 26, 64, "pt", -2, ch=4, dark=1)
        BOX(sc, tx - 2, ty - 8, zt + 2, 18, 16, 20, "m", -2)
        Z(sc, zt - 6, 8, [(tx - 1, ty - 5), (tx + 8, ty - 7), (tx + 8, ty + 5), (tx - 1, ty + 3)], "t", -3)
    s, sc = fit(fn, -30, 26, (30, 22, 290, 176), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, -31), (0, 0, 1), 110, -70, 30)
    tx, ty = 60 * math.cos(math.radians(-20)), 60 * math.sin(math.radians(-20))
    s += arrow3(cam, (tx + 40, ty, zt + 70), (tx + 40, ty, zt + 30))
    c = cam.xy((tx, ty, zt - 2))
    s += chips(c[0] - 8, c[1] + 2, -0.9)
    a = cam.xy(pt3((0, 0, -31), (0, 0, 1), 110, 30))
    b = cam.xy((tx + 40, ty, zt + 50))
    w = cam.xy((-50, 30, zt + 12))
    r = cam.xy((tx + 24, ty - 13, zt + 80))
    s += al(a[0] + 6, a[1] + 4, "回転", "start") + al(b[0] + 8, b[1] + 4, "送り", "start")
    s += lab(w[0] - 20, w[1] - 12, "工作物") + lab(r[0] + 6, r[1], "ラム", "start")
    return s


# =====================================================================================
# q:cyl_grind — cylindrical grinder: work turns between centres, the wheel (behind) spins
# the same way (surfaces meet in opposite directions), plunges in and the table traverses
# =====================================================================================
@picto("cyl_grind")
def _():
    rw, Rg, xg, Lg = 20, 62, 92, 30          # work journal radius, wheel radius, wheel face x, width
    yw = rw + Rg

    def fn(sc):
        BOX(sc, -40, -22, -40, 26, 44, 64, "pt", ch=4, dark=1)              # headstock
        CYL(sc, (-14, 0, 0), (1, 0, 0), 9, 14, "m", seg=20, r1=1.5)         # dead centre
        BOX(sc, 204, -22, -40, 28, 44, 60, "pt", ch=4, dark=1)              # tailstock
        CYL(sc, (204, 0, 0), (-1, 0, 0), 9, 14, "m", seg=20, r1=1.5)
        CYL(sc, (0, 0, 0), (1, 0, 0), 15, 70, "w", seg=32)
        CYL(sc, (70, 0, 0), (1, 0, 0), rw, 76, "w", seg=36)                 # ground journal
        CYL(sc, (146, 0, 0), (1, 0, 0), 15, 44, "w", seg=32)
        CYL(sc, (xg - 10, yw, 0), (1, 0, 0), 22, 10, "dk", seg=28)          # wheel flange
        CYL(sc, (xg, yw, 0), (1, 0, 0), Rg, Lg, "t", seg=64)                # grinding wheel
        grit(sc, (xg - .2, yw, 0), (-1, 0, 0), Rg - 7)
    s, sc = fit(fn, 18, 34, (22, 14, 298, 164), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (xg - 2, yw, 0), (1, 0, 0), Rg - 16, 110, 200)          # wheel rotation
    s += arc3(cam, (170, 0, 0), (1, 0, 0), 24, 100, 210)                     # work rotation (same sense)
    s += arrow3(cam, (xg + Lg + 26, yw + 30, 0), (xg + Lg + 26, yw - 22, 0))  # infeed
    s += arrow3(cam, (70, -36, -30), (146, -36, -30), both=True)           # traverse
    g = cam.xy(pt3((xg, yw, 0), (1, 0, 0), Rg, 100))
    i = cam.xy((xg + Lg + 26, yw + 4, 0))
    w = cam.xy((176, -rw, -20))
    t = cam.xy((108, -36, -30))
    s += lab(g[0] - 30, g[1] + 2, "砥石", "end") + al(i[0] + 8, i[1] - 2, "切込み", "start")
    s += lab(w[0] + 10, w[1] + 18, "工作物", "start") + al(t[0], t[1] + 18, "トラバース")
    return s

# =====================================================================================
# q:swiss — Swiss-type automatic lathe: the headstock slides the turning bar through the
# guide bush; the tool cuts right at the bush, so long slender parts stay rigid
# =====================================================================================
@picto("swiss")
def _():
    xt = 30                                    # tool position (just past the bush face at x=12)

    def fn(sc):
        BOX(sc, -170, -30, -36, 80, 60, 70, "pt", ch=4, dark=1)            # sliding headstock
        CYL(sc, (-90, 0, 0), (1, 0, 0), 20, 12, "dk", seg=28)               # spindle nose / collet
        CYL(sc, (-200, 0, 0), (1, 0, 0), 8, 30, "w", seg=20)                # bar entering from behind
        CYL(sc, (-78, 0, 0), (1, 0, 0), 8, 58, "w", seg=20)                 # bar between collet and bush
        BOX(sc, -20, -34, -58, 30, 68, 100, "pt", ch=4, dark=1)             # guide-bush support
        CYL(sc, (10, 0, 0), (1, 0, 0), 15, 4, "dk", seg=28)                 # guide bush
        CYL(sc, (14, 0, 0), (1, 0, 0), 8, xt - 14, "w", seg=20)             # bar out of the bush
        CYL(sc, (xt, 0, 0), (1, 0, 0), 5, 34, "w", seg=20)                  # turned slender part
        BOX(sc, xt + 2, -84, -14, 14, 60, 10, "m", -3)                      # tool holder (gang slide)
        Z(sc, -4, 4, [(xt, -5.6), (xt + 9, -16), (xt + 17, -13), (xt + 8, -4.2)], "t", -4)
    s, sc = fit(fn, -30, 18, (18, 30, 302, 164), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-170, 0, 50), (-100, 0, 50), both=True)
    s += arc3(cam, (xt + 20, 0, 0), (1, 0, 0), 14, 40, 170)
    s += arrow3(cam, (xt + 30, -70, -9), (xt + 30, -36, -9))
    h = cam.xy((-135, 0, 50))
    g = cam.xy((-5, 0, 42))
    w = cam.xy((-195, 0, 8))
    t = cam.xy((xt + 9, -84, -14))
    s += al(h[0], h[1] - 10, "主軸台が移動") + lab(g[0] + 6, g[1] - 8, "ガイドブッシュ")
    s += lab(w[0] - 4, w[1] - 12, "棒材") + lab(t[0] - 8, t[1] + 8, "バイト", "end")
    return s


# =====================================================================================
# q:oval — piston (oval) turning: the tool darts in and out in step with the spindle angle,
# leaving a non-round (elliptical) skirt
# =====================================================================================
@picto("oval")
def _():
    xt, ry, rz = 22, 34, 27                   # tool x, skirt ellipse half-axes (exaggerated)

    def fn(sc):
        ell_ = [(ry * math.cos(a), rz * math.sin(a)) for a in [2 * PI * k / 32 for k in range(32)]]
        X(sc, 0, 70, banded(ell_, 2), "w", smooth=True)                     # oval skirt (open end at -x)
        CYL(sc, (70, 0, 0), (1, 0, 0), 32, 4, "w", seg=40, dark=1)          # ring lands / grooves
        CYL(sc, (74, 0, 0), (1, 0, 0), 30, 4, "w", seg=40, dark=2)
        CYL(sc, (78, 0, 0), (1, 0, 0), 32, 4, "w", seg=40, dark=1)
        CYL(sc, (82, 0, 0), (1, 0, 0), 30, 4, "w", seg=40, dark=2)
        CYL(sc, (86, 0, 0), (1, 0, 0), 32, 10, "w", seg=40)                 # crown
        CYL(sc, (96, 0, 0), (1, 0, 0), 22, 12, "m", seg=32)                 # crown-side fixture
        CYL(sc, (108, 0, 0), (1, 0, 0), 32, 26, "dk", seg=32)               # spindle nose

        def ref(s_):                                                        # skirt bore + true circle for comparison
            o = path(P([s_.cam.xy((-.2, .8 * u, .76 * v)) for u, v in ell_]), "bg")
            return o + path(P(circ3(s_.cam, (-.3, 0, 0), (-1, 0, 0), ry, 36)), "o thin dash")
        RAW(sc, ref, ((-.5, -ry, -ry), (-.2, ry, ry)), -2)
        # fast tool: insert on a short holder driven by a linear-motor actuator
        BOX(sc, xt - 7, -88, -9, 14, 48, 8, "m", -3)
        Z(sc, -2, 4, [(xt, -ry - 1), (xt - 9, -ry - 11), (xt - 3, -ry - 18), (xt + 7, -ry - 8)], "t", -4)
        BOX(sc, xt - 15, -122, -22, 30, 34, 30, "dk", -2, ch=3)
    s, sc = fit(fn, 28, 20, (28, 30, 292, 166), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (50, 0, 0), (1, 0, 0), 40, 60, 170)
    s += arrow3(cam, (xt + 34, -116, -34), (xt + 34, -62, -34), both=True)
    a = cam.xy((50, 20, 40))
    b = cam.xy((xt + 34, -62, -34))
    w = cam.xy((96, 0, 32))
    m = cam.xy((xt, -122, -22))
    s += al(a[0] + 10, a[1] - 10, "回転", "start") + al(b[0] + 16, b[1] + 10, "高速往復", "start")
    s += lab(w[0] + 8, w[1] - 8, "ピストン", "start") + lab(m[0] - 18, m[1] + 6, "リニアモータ", "end")
    return s

# =====================================================================================
# q:mc_v — vertical machining centre: vertical spindle on the column, the table moves X/Y,
# the spindle head feeds down (Z)
# =====================================================================================
def vmc(sc, zs, col=150):
    BOX(sc, -110, -62, -70, 220, 124, 26, "pt", dark=1)                     # bed / saddle
    BOX(sc, -120, -46, -44, 240, 92, 14, "m")                               # table
    BOX(sc, -44, 66, -70, 88, 60, zs + col - 30, "pt", dark=1)              # column
    BOX(sc, -32, -32, zs, 64, 98, 56, "pt", ch=5)                           # spindle head
    CYL(sc, (0, 0, zs), (0, 0, -1), 22, 10, "dk", seg=28)                   # spindle nose
    CYL(sc, (0, 0, zs - 10), (0, 0, -1), 14, 16, "m", seg=24, r1=8)         # holder (taper)


@picto("mc_v")
def _():
    zs, zt = 80, 8

    def fn(sc):
        vmc(sc, zs, 100)
        BOX(sc, -80, -38, -30, 160, 76, 38, "w", ch=5)                      # work (plate)
        CYL(sc, (0, 0, zs - 26), (0, 0, -1), 10, zs - 26 - zt - 10, "t", seg=24)
        CYL(sc, (0, 0, zt + 10), (0, 0, -1), 26, 10, "t", seg=36)           # face mill
    s, sc = fit(fn, 30, 22, (36, 18, 280, 176), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, zs - 40), (0, 0, 1), 22, 200, 330)
    s += arrow3(cam, (-62, -40, zs + 40), (-62, -40, zs))
    s += arrow3(cam, (-110, -74, -44), (110, -74, -44), both=True)
    h = cam.xy((32, -32, zs + 56))
    w = cam.xy((-80, -38, 0))
    t = cam.xy((120, -46, -44))
    z = cam.xy((-62, -40, zs + 20))
    s += lab(h[0] + 8, h[1] + 4, "主軸（垂直）", "start") + lab(w[0] - 6, w[1] + 4, "工作物", "end")
    s += al(t[0] + 6, t[1] + 12, "テーブル", "start") + al(z[0] - 8, z[1] + 4, "送り", "end")
    return s


@picto("compact")
def _():
    zs, zt = 84, 14

    def fn(sc):
        BOX(sc, -86, -52, -70, 172, 104, 24, "pt", dark=1)                  # bed
        BOX(sc, -96, -40, -46, 192, 80, 12, "m")                            # table
        BOX(sc, -34, 56, -70, 68, 50, zs + 90, "pt", dark=1)                # column
        BOX(sc, -24, -24, zs, 48, 84, 52, "pt", ch=5)                       # spindle head
        CYL(sc, (0, 0, zs), (0, 0, -1), 16, 8, "dk", seg=24)
        CYL(sc, (0, 0, zs - 8), (0, 0, -1), 10, 10, "m", seg=20, r1=6)
        CYL(sc, (0, 0, zs - 18), (0, 0, -1), 3.5, zs - 18 - zt + 6, "t", seg=12)   # drill / tap
        # turret tool magazine around the head (tools hang in pots on its rim)
        CYL(sc, (0, 24, zs + 60), (0, 0, 1), 58, 10, "m", seg=40, dark=.4)
        for k in range(12):
            a = 2 * PI * k / 12
            x, y = 50 * math.sin(a), 24 - 50 * math.cos(a)
            if -28 < x < 28 and y < 20 or y > 30:
                continue
            CYL(sc, (x, y, zs + 60), (0, 0, -1), 5, 14, "dk", seg=10, lines=False)
            CYL(sc, (x, y, zs + 46), (0, 0, -1), 2.2, 12, "t", seg=8, lines=False)
        BOX(sc, -50, -34, -34, 100, 68, 48, "w", ch=4)                      # small aluminium block

        def holes(s_):
            o = ""
            for i in range(4):
                for j in range(2):
                    o += hole3(s_.cam, (-30 + 20 * i, -12 + 24 * j, zt + .2), (0, 0, 1), 4)
            return o
        RAW(sc, holes, ((-46, -30, zt), (46, 30, zt + .3)), -1)
    s, sc = fit(fn, 30, 22, (44, 20, 270, 174), sh_ry=7, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, zs - 30), (0, 0, 1), 14, 200, 340)
    s += arc3(cam, (0, 24, zs + 74), (0, 0, 1), 72, 220, 320)
    h = cam.xy((-58, 24, zs + 70))
    w = cam.xy((-46, -30, 0))
    t = cam.xy((0, -40, zs - 30))
    s += lab(h[0] - 14, h[1] - 2, "工具マガジン", "end") + lab(w[0] - 6, w[1], "工作物", "end")
    s += al(t[0] - 20, t[1] + 8, "高速主軸", "end")
    return s



# =====================================================================================
# crankshaft segment (axis x) shared by crankmill / crank_grind / fillet
# =====================================================================================
CR = dict(rj=22, rp=19, e=36, tw=12, rl=27, rc=52)


def crank_web(phi):
    e, rl, rc = CR["e"], CR["rl"], CR["rc"]
    py, pz = e * math.cos(math.radians(phi)), e * math.sin(math.radians(phi))
    pts = arc(py, pz, rl, phi - 90, phi + 90, 8) + arc(0, 0, rc, phi + 180 - 56, phi + 180 + 56, 8)
    return banded(hull(pts), 2)


def crank(sc, segs, x=0.0, split=None):
    """segs: ('j', L) journal | ('w', phi) web | ('p', phi, L) pin. split: {pin_index: [x cuts]}."""
    e, tw = CR["e"], CR["tw"]
    pins = []
    pi_ = 0
    for sg in segs:
        if sg[0] == "j":
            CYL(sc, (x, 0, 0), (1, 0, 0), CR["rj"], sg[1], "w", seg=28)
            x += sg[1]
        elif sg[0] == "w":
            X(sc, x, tw, crank_web(sg[1]), "w", smooth=True, dark=1, cap_mat="w3")
            x += tw
        else:
            phi, L = sg[1], sg[2]
            C = (0, e * math.cos(math.radians(phi)), e * math.sin(math.radians(phi)))
            cuts = [x] + [x + c for c in (split or {}).get(pi_, [])] + [x + L]
            for a, b in zip(cuts, cuts[1:]):
                CYL(sc, (a, C[1], C[2]), (1, 0, 0), CR["rp"], b - a, "w", seg=24)
            pins.append((x, C))
            pi_ += 1
            x += L
    return pins


# =====================================================================================
# q:crankmill — crankshaft miller (internal type): a ring cutter with inserts on its inside
# edge surrounds the pin and follows it while the crank turns slowly
# =====================================================================================
@picto("crankmill")
def _():
    segs = [("j", 30), ("w", 90), ("p", 90, 30), ("w", 90), ("j", 30), ("w", -90), ("p", -90, 30), ("w", -90), ("j", 26)]
    ri, ro, wc = 31, 74, 12
    off = ri - CR["rp"]                        # cutter centre offset from the pin centre (cuts at the top)
    teeth = [((ri + (3 if k % 2 else 0)) * math.cos(2 * PI * k / 24), (ri + (3 if k % 2 else 0)) * math.sin(2 * PI * k / 24), k)
             for k in range(24)]

    def fn(sc):
        pins = crank(sc, segs, split={0: [9, 9 + wc]})
        x0, C = pins[0]
        O = (x0 + 9, C[1], C[2] - off)
        CYL(sc, O, (1, 0, 0), ro, wc, "t", seg=40, holes=[[(u, v, k) for u, v, k in teeth]], bands=10)
        sc.Oc = O
    s, sc = fit(fn, 24, 20, (34, 22, 286, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    O = sc.Oc
    s += arc3(cam, (O[0] - 1, O[1], O[2]), (1, 0, 0), ro + 8, 110, 200)
    s += arc3(cam, (208, 0, 0), (1, 0, 0), 30, 100, 180)
    s += arrow3(cam, (O[0] - 30, O[1] - ro - 10, O[2] - 40), (O[0] - 30, O[1] - ro - 10, O[2] + 30), both=True)
    c = cam.xy(pt3(O, (1, 0, 0), ro, 120))
    f = cam.xy((O[0] - 30, O[1] - ro - 10, O[2] - 40))
    w = cam.xy((216, 0, -CR["rj"]))
    r = cam.xy(pt3((208, 0, 0), (1, 0, 0), 30, 100))
    s += lab(c[0] - 8, c[1] - 6, "内刃カッタ", "end") + al(f[0] - 6, f[1] + 14, "ピン追従")
    s += lab(w[0] + 2, w[1] + 22, "クランク軸") + al(r[0] + 8, r[1] - 6, "低速回転", "start")
    return s


# =====================================================================================
# q:crank_grind — crankshaft pin grinder: the crank turns on its journal axis; the CBN wheel
# head moves in and out in step so the wheel stays on the orbiting pin
# =====================================================================================
@picto("crank_grind")
def _():
    segs = [("j", 30), ("w", 60), ("p", 60, 30), ("w", 60), ("j", 30), ("w", -120), ("p", -120, 30), ("w", -120), ("j", 26)]
    Rg, wg = 64, 22

    def fn(sc):
        pins = crank(sc, segs)
        x0, C = pins[0]
        O = (x0 + 4, C[1] + CR["rp"] + Rg, C[2])
        CYL(sc, (O[0] - 8, O[1], O[2]), (1, 0, 0), 20, 8, "dk", seg=24)
        CYL(sc, O, (1, 0, 0), Rg, wg, "t", seg=56)
        grit(sc, (O[0] - .2, O[1], O[2]), (-1, 0, 0), Rg - 6)
        sc.Oc = O
    s, sc = fit(fn, 22, 32, (36, 22, 284, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    O = sc.Oc
    s += arc3(cam, (O[0] - 2, O[1], O[2]), (1, 0, 0), Rg - 16, 110, 200)
    s += arc3(cam, (208, 0, 0), (1, 0, 0), 30, 100, 180)
    s += arrow3(cam, (O[0] + wg + 16, O[1] + 30, O[2] + Rg), (O[0] + wg + 16, O[1] - 30, O[2] + Rg), both=True)
    g = cam.xy(pt3(O, (1, 0, 0), Rg, 100))
    f = cam.xy((O[0] + wg + 16, O[1], O[2] + Rg))
    w = cam.xy((216, 0, -CR["rj"]))
    r = cam.xy(pt3((208, 0, 0), (1, 0, 0), 30, 100))
    s += lab(g[0] - 24, g[1] + 4, "CBN砥石", "end") + al(f[0] + 14, f[1] - 2, "ピン追従", "start")
    s += lab(w[0] + 2, w[1] + 22, "クランク軸") + al(r[0] + 8, r[1] - 6, "回転", "start")
    return s


# =====================================================================================
# q:fillet — fillet rolling: small rollers are pressed into the corner radii (fillets) of a
# journal while the crank turns, leaving compressive stress there
# =====================================================================================
@picto("fillet")
def _():
    segs = [("j", 24), ("w", 90), ("p", 90, 26), ("w", 90), ("j", 44), ("w", -90), ("p", -90, 26), ("w", -90), ("j", 24)]
    xj0, xj1 = 24 + 12 + 26 + 12, 24 + 12 + 26 + 12 + 44     # middle journal
    rj = CR["rj"]

    def fn(sc):
        crank(sc, segs)
        # rolling tool from above: holder + two inclined rollers pressed into the two fillets
        rr, wr = 9, 5
        for xc, sg in ((xj0, 1), (xj1, -1)):
            b = GE._norm((sg, 0, 1))                    # bisector of the corner
            a = GE._norm((-sg, 0, 1)) if sg > 0 else GE._norm((1, 0, 1))
            C = (xc + b[0] * rr * .9, 0, rj + b[2] * rr * .9)
            CYL(sc, tuple(C[i] - a[i] * wr / 2 for i in range(3)), a, rr, wr, "t", -3, seg=20)
        BOX(sc, xj0 + 6, -9, rj + 16, xj1 - xj0 - 12, 18, 20, "dk", -2, ch=2)
        BOX(sc, xj0 + 12, -14, rj + 36, xj1 - xj0 - 24, 28, 54, "dk", -2, ch=3)
    s, sc = fit(fn, 24, 24, (34, 20, 286, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    xm = (xj0 + xj1) / 2
    s += arc3(cam, (xj1 + 70, 0, 0), (1, 0, 0), 30, 100, 180)
    s += arrow3(cam, (xm + 40, -14, rj + 90), (xm + 40, -14, rj + 44))
    t = cam.xy((xj0 + 12, -14, rj + 80))
    f = cam.xy((xm + 40, -14, rj + 70))
    w = cam.xy((xm, -rj, -CR["rc"]))
    r = cam.xy(pt3((xj1 + 70, 0, 0), (1, 0, 0), 30, 100))
    s += lab(t[0] - 8, t[1] + 4, "ローラ", "end") + al(f[0] + 8, f[1] + 4, "押付け", "start")
    s += lab(w[0], w[1] + 22, "フィレット（隅R）を押し固める") + al(r[0] + 8, r[1] - 6, "回転", "start")
    return s



# =====================================================================================
# q:centerless — centerless grinder: the work rests on a blade between the grinding wheel and
# the (rubber) regulating wheel; both wheels turn the same way, the work the other way,
# and the slightly tilted regulating wheel pushes the bar through (through-feed)
# =====================================================================================
@picto("centerless")
def _():
    Rg, Rr, rw, zw = 70, 46, 11, 8
    xg = -math.sqrt((Rg + rw) ** 2 - zw ** 2)
    xr = math.sqrt((Rr + rw) ** 2 - zw ** 2)

    def fn(sc):
        CYL(sc, (xg, 0, 0), (0, 1, 0), Rg, 56, "t", seg=64)                # grinding wheel
        grit(sc, (xg, -.2, 0), (0, -1, 0), Rg - 7)
        CYL(sc, (xg, -6, 0), (0, 1, 0), 18, 6, "m", seg=24, bias=-.5)
        CYL(sc, (xr, 0, 0), (0, 1, 0), Rr, 56, "dk", seg=48)                # regulating wheel
        CYL(sc, (xr, -6, 0), (0, 1, 0), 14, 6, "m", seg=24, bias=-.5)
        Z(sc, -56, zw - rw + 56, [(-4, -8), (4, -8), (4, 62), (-4, 62)], "m", .5)   # work-rest blade
        CYL(sc, (0, -66, zw), (0, 1, 0), rw, 160, "w", seg=28, bias=-1)    # bar, through-fed
    s, sc = fit(fn, -16, 16, (30, 24, 290, 166), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (xg, -1, 0), (0, 1, 0), Rg - 18, 20, 100)
    s += arc3(cam, (xr, -1, 0), (0, 1, 0), Rr - 14, 20, 100)
    s += arrow3(cam, (0, -20, zw + rw + 18), (0, -80, zw + rw + 18))
    g = cam.xy((xg, 0, -Rg))
    r = cam.xy((xr, 0, -Rr))
    b = cam.xy((0, -8, -56))
    f = cam.xy((0, -50, zw + rw + 18))
    s += lab(g[0], g[1] + 18, "研削砥石") + lab(r[0] + 6, r[1] + 18, "調整車")
    s += lab(b[0] + 4, b[1] + 16, "支持刃") + al(f[0] + 14, f[1] - 14, "通し送り", "start")
    return s


# =====================================================================================
# q:int_grind — internal grinder: the chuck turns the ring, a small wheel on a long quill spins
# fast inside the bore and strokes in and out
# =====================================================================================
@picto("int_grind")
def _():
    ro, ri, L = 50, 28, 40
    rg = 13

    def fn(sc):
        CYL(sc, (L + 22, 0, 0), (1, 0, 0), 36, 30, "dk", seg=32)            # spindle
        CYL(sc, (L, 0, 0), (1, 0, 0), 62, 22, "m", seg=48)                  # chuck
        for k in range(3):
            t = math.radians(90 + k * 120)
            c, s_ = math.cos(t), math.sin(t)
            X(sc, L - 14, 14, [(u * c - v * s_, u * s_ + v * c) for u, v in ((ro, -7), (ro + 14, -7), (ro + 14, 7), (ro, 7))], "dk", -.5)
        RG(sc, (0, 0, 0), (1, 0, 0), ro, ri, L, "w", seg=48)               # ring (gear blank / bearing race)
        Y = ri - rg - 1
        CYL(sc, (-150, Y - 26, -26), (1, 0, 0), 30, 50, "dk", -3, seg=28)   # wheel head
        CYL(sc, (-100, Y, 0), (1, 0, 0), 6, 92, "m", -3, seg=16)            # quill
        CYL(sc, (-8, Y, 0), (1, 0, 0), rg, 24, "t", -4, seg=24)             # small wheel entering the bore
    s, sc = fit(fn, 30, 20, (24, 24, 296, 166), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-60, ri - rg - 1, 0), (1, 0, 0), 14, 100, 200)
    s += arrow3(cam, (-96, ri - rg - 1 - 30, -34), (-36, ri - rg - 1 - 30, -34), both=True)
    s += arc3(cam, (L + 4, 0, 0), (1, 0, 0), 72, 100, 170)
    g = cam.xy((-60, ri - 14, 14))
    o = cam.xy((-66, ri - 44, -34))
    w = cam.xy((0, 0, -ro))
    r = cam.xy(pt3((L + 4, 0, 0), (1, 0, 0), 72, 100))
    s += al(g[0], g[1] - 12, "高速回転") + al(o[0], o[1] + 18, "往復")
    s += lab(w[0] + 8, w[1] + 22, "工作物") + lab(r[0] + 16, r[1] - 4, "チャック", "start")
    return s


# =====================================================================================
# q:cam_grind — cam grinder: spindle angle (C) and wheel-head position (X) are synchronised
# so the wheel follows the lobe profile
# =====================================================================================
def cam_lobe(phi, rb=19, lift=10, nr=10):
    c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    d = rb + lift - nr
    return banded(hull(arc(0, 0, rb, 0, 360, 20) + arc(d * c, d * s_, nr, phi - 90, phi + 90, 6)), 2)


@picto("cam_grind")
def _():
    Rg, wg = 66, 22
    lobes = [(10, 90), (52, 180), (94, 300), (136, 30)]          # (x, nose angle)

    def fn(sc):
        CYL(sc, (-20, 0, 0), (1, 0, 0), 16, 20, "w", seg=28)               # front journal
        xs = [0] + [x for x, _ in lobes] + [x + 16 for x, _ in lobes] + [170]
        CYL(sc, (0, 0, 0), (1, 0, 0), 10, 10, "w", seg=20)
        for i, (x, phi) in enumerate(lobes):
            X(sc, x, 16, cam_lobe(phi), "w", smooth=True)
            CYL(sc, (x + 16, 0, 0), (1, 0, 0), 10, 26 if i < 3 else 20, "w", seg=16)
        CYL(sc, (156, 0, 0), (1, 0, 0), 16, 20, "w", seg=28)
        x0, phi = lobes[1]
        O = (x0 - 2, 19 + Rg, 0)                                            # wheel on the base circle side
        CYL(sc, (O[0] - 8, O[1], 0), (1, 0, 0), 20, 8, "dk", seg=24)
        CYL(sc, O, (1, 0, 0), Rg, wg - 2, "t", seg=48)
        grit(sc, (O[0] - .2, O[1], 0), (-1, 0, 0), Rg - 6)
        sc.Oc = O
    s, sc = fit(fn, 22, 30, (36, 18, 284, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    O = sc.Oc
    s += arc3(cam, (O[0] - 2, O[1], 0), (1, 0, 0), Rg - 16, 110, 200)
    s += arc3(cam, (176, 0, 0), (1, 0, 0), 26, 100, 190)
    s += arrow3(cam, (O[0] + wg + 22, O[1] + 34, -30), (O[0] + wg + 22, O[1] - 30, -30), both=True)
    g = cam.xy(pt3(O, (1, 0, 0), Rg, 100))
    f = cam.xy((O[0] + wg + 22, O[1] + 2, -30))
    w = cam.xy((150, 0, -30))
    r = cam.xy(pt3((176, 0, 0), (1, 0, 0), 26, 100))
    s += lab(g[0] - 24, g[1] + 4, "砥石", "end") + al(f[0] + 10, f[1] + 4, "同期して前後", "start")
    s += lab(w[0], w[1] + 20, "カム") + al(r[0] + 8, r[1] - 6, "回転", "start")
    return s


def SEMI(sc, O, A, r, h, mat, a0=0, a1=180, bias=0.0, seg=24, **kw):
    """half (or partial) disc prism: arc a0..a1 (deg, GE.frame(A)) closed by its chord."""
    a = GE._norm(A)
    loop = banded(arc(0, 0, r, a0, a1, seg), 2)
    lo, hi = [], []
    for k in range(seg + 1):
        for t in (0, h):
            p = pt3(tuple(O[i] + a[i] * t for i in range(3)), a, r, a0 + (a1 - a0) * k / seg)
            lo.append(p)
    xs, ys, zs = zip(*lo)
    sc.add(compact(GE.prism(sc.cam, O, a, loop, h, mat, smooth=True, **kw)), ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))), bias)


# =====================================================================================
# q:surf_grind — surface grinder: the wheel (horizontal spindle) spins over a plate held on
# the magnetic chuck; the table reciprocates left-right and steps across between strokes
# =====================================================================================
@picto("surf_grind")
def _():
    Rg, wg, xw = 58, 26, -10

    def fn(sc):
        BOX(sc, -110, -62, -70, 220, 124, 28, "pt", dark=1)                 # saddle
        BOX(sc, -140, -50, -42, 280, 100, 16, "m")                          # reciprocating table
        BOX(sc, -112, -42, -26, 224, 84, 12, "dk")                          # magnetic chuck
        BOX(sc, -84, -30, -14, 150, 60, 14, "w", ch=2)                      # work plate
        CYL(sc, (xw, -wg / 2, Rg), (0, 1, 0), Rg, wg, "t", seg=56)          # wheel (axis front-back)
        grit(sc, (xw, -wg / 2 - .2, Rg), (0, -1, 0), Rg - 7)
        CYL(sc, (xw, wg / 2, Rg), (0, 1, 0), 18, 70, "dk", seg=24)          # spindle housing
        SEMI(sc, (xw, -wg / 2 - 6, Rg), (0, 1, 0), Rg + 7, wg + 12, "pt", 15, 165, dark=1)  # wheel guard (upper part)
    s, sc = fit(fn, -26, 22, (24, 18, 296, 172), sh_ry=7, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (xw, -wg / 2 - 1, Rg), (0, 1, 0), Rg - 16, 10, 60)
    s += arrow3(cam, (-140, -64, -42), (140, -64, -42), both=True)
    s += arrow3(cam, (150, 30, -34), (150, -30, -34))
    c = cam.xy((xw + 2, -wg / 2, 0))
    s += sparks(c[0] + 2, c[1], 14, 5, -40, 40)
    g = cam.xy(pt3((xw, -wg / 2, Rg), (0, 1, 0), Rg + 7, 160))
    w = cam.xy((-84, -30, -8))
    t = cam.xy((0, -64, -42))
    y = cam.xy((150, -30, -34))
    s += lab(g[0] - 8, g[1] - 4, "砥石", "end") + lab(w[0] - 14, w[1] + 4, "工作物", "end")
    s += al(t[0] - 30, t[1] + 18, "テーブル往復") + al(y[0] + 4, y[1] + 18, "横送り", "start")
    return s


# =====================================================================================
# q:dd_grind — double-disc grinder: two facing wheels grind both faces of the parts at once
# as a carrier feeds them through the gap
# =====================================================================================
@picto("dd_grind")
def _():
    Rg, wg, gap, zp, rr = 64, 30, 26, 30, 20

    def fn(sc):
        for sg in (-1, 1):
            x0 = -gap / 2 - wg if sg < 0 else gap / 2
            CYL(sc, (x0, 0, 0), (1, 0, 0), Rg, wg, "t", seg=44, holes=[GE.circle_outline(18, 24, 6)])
            xs = x0 - 40 if sg < 0 else x0 + wg
            CYL(sc, (xs, 0, 0), (1, 0, 0), 26, 40, "dk", seg=22)            # spindle heads
        grit(sc, (-gap / 2 - wg - .2, 0, 0), (-1, 0, 0), Rg - 7)
        for k, y in enumerate((-150, -100, -50)):                           # rings fed through the gap
            RG(sc, (-gap / 2, y, zp), (1, 0, 0), rr, 10, gap, "w", seg=22)
        BOX(sc, -gap / 2 - 2, -176, zp - rr - 8, gap + 4, 140, 6, "m", .5)  # guide
    s, sc = fit(fn, 34, 18, (24, 22, 296, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-gap / 2 - wg - 1, 0, 0), (1, 0, 0), Rg - 14, 100, 190)
    s += arrow3(cam, (-gap / 2 - 30, -170, zp + 34), (-gap / 2 - 30, -100, zp + 34))
    g = cam.xy((-gap / 2 - wg, 0, -Rg))
    f = cam.xy((-gap / 2 - 30, -170, zp + 34))
    w = cam.xy((-gap / 2, -150, zp - rr))
    s += lab(g[0] + 30, g[1] + 20, "対向する2枚の砥石") + al(f[0] - 4, f[1] + 14, "送り込み", "end")
    s += lab(w[0] + 30, w[1] + 22, "工作物", "start")
    return s


# =====================================================================================
# q:thread_grind — thread grinder: a thin profiled wheel tilted to the lead angle grinds the
# helical groove while the work turns and the table advances one lead per turn
# =====================================================================================
@picto("thread_grind")
def _():
    r, L, pitch, Rg, wg, lam = 20, 200, 16, 62, 10, 9

    def helix(s_):
        D = s_.cam.D
        o = ""
        for k in range(int(L / pitch) + 1):
            seg_, cur = [], []
            for j in range(0, 37):
                th = 2 * PI * j / 36
                x = k * pitch + pitch * j / 36 - pitch / 2
                if x < 2 or x > L - 6:
                    continue
                nn = (0, math.cos(th), math.sin(th))
                if GE._dot(nn, D) < -.05:
                    cur.append(x)
                    cur.append(th)
                elif cur:
                    seg_.append(cur)
                    cur = []
            if cur:
                seg_.append(cur)
            for c in seg_:
                pts = [(c[i], c[i + 1]) for i in range(0, len(c), 2)]
                if len(pts) < 2:
                    continue
                a = [s_.cam.xy((x, r * math.cos(t), r * math.sin(t))) for x, t in pts]
                b = [s_.cam.xy((x + 5, r * math.cos(t), r * math.sin(t))) for x, t in reversed(pts)]
                o += path(P(a + b), "w3")
        return o

    def fn(sc):
        BOX(sc, -36, -22, -44, 24, 44, 70, "pt", ch=4, dark=1)              # headstock
        CYL(sc, (-12, 0, 0), (1, 0, 0), 9, 12, "m", seg=20, r1=1.5)
        BOX(sc, L + 12, -22, -44, 24, 44, 64, "pt", ch=4, dark=1)           # tailstock
        CYL(sc, (L + 12, 0, 0), (-1, 0, 0), 9, 12, "m", seg=20, r1=1.5)
        CYL(sc, (0, 0, 0), (1, 0, 0), r, L, "w", seg=36)                    # screw shaft
        RAW(sc, helix, ((0, -r - .3, -r), (L, -r, r)), -1)
        xg = 112
        a = (math.cos(math.radians(lam)), math.sin(math.radians(lam)), 0)
        O = (xg, r - 3 + Rg, 0)
        CYL(sc, tuple(O[i] - a[i] * wg / 2 for i in range(3)), a, Rg, wg, "t", seg=56, r1=None)
        CYL(sc, tuple(O[i] - a[i] * (wg / 2 + 8) for i in range(3)), a, 20, 8, "dk", seg=24)
        sc.Oc = O
    s, sc = fit(fn, 20, 32, (24, 18, 296, 166), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    O = sc.Oc
    s += arc3(cam, (O[0] - 6, O[1], O[2]), (1, 0, 0), Rg - 14, 110, 200)
    s += arc3(cam, (30, 0, 0), (1, 0, 0), 28, 100, 200)
    s += arrow3(cam, (60, -36, -36), (150, -36, -36))
    g = cam.xy(pt3(O, (1, 0, 0), Rg, 100))
    w = cam.xy((180, -r, -18))
    t = cam.xy((105, -36, -36))
    c = cam.xy(pt3((30, 0, 0), (1, 0, 0), 28, 100))
    s += lab(g[0] - 22, g[1] + 2, "砥石（傾斜）", "end") + lab(w[0] + 4, w[1] + 24, "ねじ軸")
    s += al(t[0], t[1] + 18, "1回転で1リード送る") + al(c[0] - 8, c[1] - 6, "回転", "end")
    return s


# =====================================================================================
# q:superfinish — superfinishing: a fine stone is pressed lightly on the turning work and
# oscillated a few mm along the axis (tape-lapping works the same way with abrasive film)
# =====================================================================================
@picto("superfinish")
def _():
    r = 24

    def fn(sc):
        CYL(sc, (-40, 0, 0), (1, 0, 0), 34, 26, "dk", seg=32)               # spindle nose / chuck
        CYL(sc, (-14, 0, 0), (1, 0, 0), 16, 30, "w", seg=28)
        CYL(sc, (16, 0, 0), (1, 0, 0), r, 90, "w", seg=40)                  # finished journal
        CYL(sc, (106, 0, 0), (1, 0, 0), 16, 50, "w", seg=28)
        # stone + holder from above
        BOX(sc, 46, -9, r - 1, 30, 18, 16, "t", -1, ch=1)                   # fine stone
        BOX(sc, 40, -14, r + 15, 42, 28, 18, "dk", -1, ch=2)
        BOX(sc, 50, -10, r + 33, 22, 20, 70, "dk", -1, ch=2)                # oscillating ram
    s, sc = fit(fn, 24, 24, (40, 18, 280, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (130, 0, 0), (1, 0, 0), 28, 100, 200)
    s += arrow3(cam, (40, -16, r + 74), (82, -16, r + 74), both=True)
    s += arrow3(cam, (100, -12, r + 96), (100, -12, r + 52))
    st = cam.xy((46, -9, r + 4))
    o = cam.xy((61, -16, r + 74))
    p = cam.xy((100, -12, r + 80))
    w = cam.xy((80, 0, -r))
    s += lab(st[0] - 10, st[1] + 6, "砥石", "end") + al(o[0] - 26, o[1] - 2, "揺動", "end")
    s += al(p[0] + 8, p[1] + 4, "低圧で押付け", "start") + lab(w[0], w[1] + 24, "工作物（回転）")
    return s


# =====================================================================================
# q:ball_groove — CV-joint outer race: a small wheel on a quill enters the bell and grinds one
# ball groove along its arc, then the race indexes to the next groove
# =====================================================================================
@picto("ball_groove")
def _():
    R, rb, rg, ng = 50, 26, 8.5, 6

    def mouth():
        pts = []
        for k in range(72):
            a = 2 * PI * k / 72
            # bore with 6 semicircular ball grooves
            d = min(abs(((a - PI / 2) % (2 * PI / ng)) - 0), abs(((a - PI / 2) % (2 * PI / ng)) - 2 * PI / ng))
            rr = rb + max(0.0, rg * math.cos(min(PI / 2, d * rb / rg)))
            pts.append((rr * math.cos(a), rr * math.sin(a), k // 6))
        return pts

    def fn(sc):
        X(sc, 0, 40, banded(arc(0, 0, R, 0, 360, 40)[:-1], 2), "w", smooth="outer",
          holes=[[(z, y, k) for y, z, k in [(p[1], p[0], p[2]) for p in mouth()]]], dark=0)   # bell wall
        CYL(sc, (40, 0, 0), (1, 0, 0), R, 16, "w", seg=40, dark=.5)        # bell bottom
        CYL(sc, (56, 0, 0), (1, 0, 0), 20, 70, "w", seg=28)                 # stem
        CYL(sc, (126, 0, 0), (1, 0, 0), 34, 30, "dk", seg=32)               # work spindle
        zq = rb + rg - 9
        CYL(sc, (-120, 0, zq), (1, 0, 0), 22, 40, "dk", -3, seg=28)         # wheel spindle
        CYL(sc, (-80, 0, zq), (1, 0, 0), 5, 74, "m", -3, seg=14)            # quill
        CYL(sc, (-8, 0, zq), (1, 0, 0), 9, 16, "t", -4, seg=20)             # small wheel in the top groove
    s, sc = fit(fn, 32, 18, (26, 22, 294, 168), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    zq = rb + rg - 9
    s += arc3(cam, (-50, 0, zq), (1, 0, 0), 11, 100, 200)
    s += arrow3(cam, (-74, 0, zq + 26), (-24, 0, zq + 26), both=True)
    s += arc3(cam, (-2, 0, 0), (1, 0, 0), R + 10, 140, 230)
    g = cam.xy((-50, 0, zq + 26))
    w = cam.xy((60, 0, -R))
    ix = cam.xy(pt3((-2, 0, 0), (1, 0, 0), R + 10, 230))
    s += al(g[0], g[1] - 10, "溝に沿って送る") + lab(w[0] + 10, w[1] + 18, "等速ジョイント外輪", "start")
    s += al(ix[0] - 8, ix[1] + 12, "60°ずつ割出し", "end")
    return s


# =====================================================================================
# q:ball_grind — ball grinding / lapping: balls roll in concentric grooves between a fixed
# plate and a rotating plate under load (upper plate cut away at the front)
# =====================================================================================
@picto("ball_grind")
def _():
    R, rb, grooves = 96, 6.5, (34, 50, 66, 82)

    def fn(sc):
        CYL(sc, (0, 0, -60), (0, 0, 1), 40, 40, "dk", seg=32)              # drive
        CYL(sc, (0, 0, -20), (0, 0, 1), R, 18, "m", seg=64)                 # rotating plate

        def balls(s_):
            o = ""
            for g in grooves:
                o += path(P(circ3(s_.cam, (0, 0, -1.8), (0, 0, 1), g, 48)), "gr")
            bs = []
            for g in grooves:
                nb = int(2 * PI * g / 15)
                for k in range(nb):
                    a = 2 * PI * (k + .3 * g) / nb
                    x, y = g * math.sin(a), -g * math.cos(a)
                    if y > -4:
                        continue
                    bs.append(s_.cam.P((x, y, rb - 3)))
            for X_, Y_, d in sorted(bs, key=lambda b: -b[2]):
                rr = rb * s_.cam.s
                o += circ(X_, Y_, rr, "ball") + circ(X_ - rr * .35, Y_ - rr * .35, rr * .3, "w")
            return o
        RAW(sc, balls, ((-R, -R, -2), (R, 0, 2 * rb - 3)), -1)
        SEMI(sc, (0, 0, 2 * rb - 4), (0, 0, 1), R, 18, "pt", 90, 270, dark=1)   # fixed upper plate (back half)
    s, sc = fit(fn, -24, 30, (30, 22, 290, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, -11), (0, 0, 1), R + 10, -70, 30)
    s += arrow3(cam, (0, 40, 2 * rb + 70), (0, 40, 2 * rb + 26))
    u = cam.xy((-R, 30, 2 * rb + 14))
    lo = cam.xy((R, 0, -20))
    b = cam.xy((-60, -58, 0))
    p = cam.xy((0, 40, 2 * rb + 56))
    s += lab(u[0] + 2, u[1] - 8, "固定定盤", "end") + lab(lo[0] + 2, lo[1] + 22, "回転定盤", "start")
    s += lab(b[0] - 8, b[1] + 18, "鋼球", "end") + al(p[0] + 8, p[1], "加圧", "start")
    return s


# =====================================================================================
# q:hone — honing: an expanding head with abrasive sticks turns and strokes up and down in
# the bore, leaving the cross-hatch (block cut away through the bore axis)
# =====================================================================================
@picto("hone")
def _():
    Rb, H, W, Dp = 34, 96, 200, 60
    zb = 0

    def fn(sc):
        out = [(-W / 2, 0), (-Rb, 0)] + arc(0, 0, Rb, 180, 0, 16)[1:-1] + [(Rb, 0), (W / 2, 0), (W / 2, Dp), (-W / 2, Dp)]
        out = out[::-1]
        Z(sc, zb, H, [(x, y, i if i < 2 or i > 16 else 2 + (i - 2) // 3) for i, (x, y) in enumerate(out)], "w", dark=0)

        def hatch(s_):                                   # cross-hatch on the cut-open bore wall
            o = ""
            for sgn in (1, -1):
                for k in range(-6, 9):
                    pts = []
                    for j in range(13):
                        a = math.radians(180 - 180 * j / 12)
                        z = zb + 8 + k * 11 + sgn * (j - 6) * 6.5
                        if 6 < z < H - 4:
                            pts.append(s_.cam.xy((Rb * math.cos(a) * .995, Rb * math.sin(a) * .995, z)))
                    if len(pts) > 1:
                        o += path(P(pts, False), "gr")
            return o
        RAW(sc, hatch, ((-Rb, 0, zb), (Rb, Rb, zb + H)), -.5)
        # honing head (partly in the bore) on its shaft
        zh = zb + 30
        CYL(sc, (0, 0, zh), (0, 0, 1), Rb - 5, 46, "dk", -3, seg=28)
        for k in range(6):
            a = 2 * PI * (k + .5) / 6
            if math.cos(a) * 0 - math.sin(a) > -.2 and -math.cos(a) < .9:
                pass
            c, s_ = math.sin(a), -math.cos(a)
            if s_ > .3:
                continue
            Z(sc, zh + 6, 34, [(c * (Rb - 6) - s_ * 4, s_ * (Rb - 6) + c * 4), (c * Rb - s_ * 4, s_ * Rb + c * 4),
                               (c * Rb + s_ * 4, s_ * Rb - c * 4), (c * (Rb - 6) + s_ * 4, s_ * (Rb - 6) - c * 4)], "t", -4)
        CYL(sc, (0, 0, zh + 46), (0, 0, 1), 9, 110, "m", -3, seg=18)
    s, sc = fit(fn, -24, 24, (40, 14, 280, 174), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, zb + 150), (0, 0, 1), 22, -70, 60)
    s += arrow3(cam, (-40, -10, zb + 176), (-40, -10, zb + 116), both=True)
    r = cam.xy(pt3((0, 0, zb + 150), (0, 0, 1), 22, 60))
    u = cam.xy((-40, -10, zb + 146))
    st = cam.xy((Rb + 2, -6, zb + 50))
    w = cam.xy((W / 2, 0, zb + 20))
    s += al(r[0] + 8, r[1] + 2, "回転", "start") + al(u[0] - 8, u[1] + 4, "上下往復", "end")
    s += lab(st[0] + 34, st[1] - 54, "拡張する砥石", "start") + lab(w[0] - 4, w[1] + 34, "シリンダボア（断面）", "end")
    return s


# =====================================================================================
# q:lap — lapping: parts held in carrier rings ride on a turning lap plate fed with abrasive
# slurry; a light load presses them down and the rings turn on their own
# =====================================================================================
@picto("lap")
def _():
    R = 100

    def fn(sc):
        CYL(sc, (0, 0, -20), (0, 0, 1), R, 20, "m", seg=48)                 # lap plate
        for (cx, cy) in ((-46, -40), (54, -24), (0, 52)):
            CYL(sc, (cx, cy, 0), (0, 0, 1), 36, 4, "dk", seg=32)        # conditioning / carrier ring
            for k in range(3):
                a = 2 * PI * k / 3 + .4
                CYL(sc, (cx + 16 * math.sin(a), cy - 16 * math.cos(a), 4), (0, 0, 1), 12, 10, "w", -.5, seg=14, bands=5)
        def grooves(s_):
            return "".join(path(P(circ3(s_.cam, (0, 0, 0), (0, 0, 1), rr, 48)), "gr") for rr in (30, 80))
        RAW(sc, grooves, ((-R, -R, -.3), (R, R, 0)), -1)
    s, sc = fit(fn, -24, 30, (40, 26, 280, 170), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, -10), (0, 0, 1), R + 10, -70, 30)
    s += arc3(cam, (-46, -40, 16), (0, 0, 1), 40, 140, 230)
    d = cam.xy((70, 30, 44))
    s += path("M%s %s L%s %s" % (n(d[0]), n(d[1] - 26), n(d[0]), n(d[1] - 6)), "o") + drops(d[0], d[1] - 4, 3, 20, 16, 100)
    p = cam.xy(pt3((0, 0, -10), (0, 0, 1), R + 10, 30))
    c = cam.xy((-46, -40, 22))
    w = cam.xy((54, -24, 22))
    s += lab(p[0] + 6, p[1] + 14, "ラップ定盤", "start") + al(c[0] - 40, c[1] - 14, "自転", "end")
    s += lab(d[0] + 8, d[1] - 18, "砥粒液", "start") + lab(w[0] + 30, w[1] - 20, "工作物", "start")
    return s


# =====================================================================================
# q:deburr — deburring: a turning brush rubs the burrs off the hole edges while a high-pressure
# water jet blasts burrs and chips out of the cross holes
# =====================================================================================
@picto("deburr")
def _():
    def fn(sc):
        BOX(sc, -110, -60, -50, 220, 120, 14, "m")                          # fixture plate
        BOX(sc, -80, -44, -36, 160, 88, 70, "w", ch=4)                      # valve-body-like block

        def holes(s_):
            o = ""
            for i in range(5):
                o += hole3(s_.cam, (-56 + 26 * i, -44.2, 4), (0, -1, 0), 6)
            for i in range(3):
                o += hole3(s_.cam, (-50 + 40 * i, 10, 34.2), (0, 0, 1), 8)
            return o
        RAW(sc, holes, ((-80, -44.3, -36), (80, -44, 34.3)), -1)
        # rotating cup brush above the top face
        CYL(sc, (30, 10, 40), (0, 0, 1), 26, 14, "dk", -1, seg=28)
        CYL(sc, (30, 10, 54), (0, 0, 1), 18, 16, "m", -1, seg=24)
        CYL(sc, (30, 10, 70), (0, 0, 1), 7, 40, "m", -1, seg=16)

        def bristle(s_):
            o = ""
            for k in range(14):
                a = PI * (k + .5) / 14 + PI
                x, y = 30 + 25 * math.cos(a), 10 + 25 * math.sin(a)
                p0, p1 = s_.cam.xy((x, y, 40)), s_.cam.xy((x * 1.0, y, 34.6))
                o += line(p0[0], p0[1], p1[0], p1[1], "gr")
            return o
        RAW(sc, bristle, ((4, -16, 34.4), (56, 36, 40)), -2)
        # high-pressure water nozzle aimed at the front holes
        CYL(sc, (-120, -110, 4), GE._norm((1, .9, 0)), 7, 40, "m", -1, seg=16)
    s, sc = fit(fn, -24, 24, (34, 20, 286, 172), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    a = cam.xy(tuple((-120, -110, 4)[i] + GE._norm((1, .9, 0))[i] * 40 for i in range(3)))
    b = cam.xy((-56 + 26, -44.2, 4))
    s += path("M%s %s L%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1])), "fl") + drops(b[0], b[1], 4, 50, 14, 200)
    s += arc3(cam, (30, 10, 60), (0, 0, 1), 32, -70, 40)
    br = cam.xy((56, 10, 50))
    nz = cam.xy((-120, -110, 4))
    w = cam.xy((80, -44, -36))
    s += lab(br[0] + 16, br[1] - 6, "回転ブラシ", "start") + lab(nz[0] - 4, nz[1] + 16, "高圧水", "middle")
    s += lab(w[0] + 4, w[1] + 18, "工作物（穴の縁のバリ）", "end")
    return s


def PR(sc, O, A, outline, h, mat, bias=0.0, **kw):
    """generic prism along any axis A; bbox from the outline's world points."""
    a = GE._norm(A)
    E1, E2, _ = GE.frame(a)
    ps = []
    for u, v, *_ in outline:
        for t in (0, h):
            ps.append(tuple(O[i] + u * E1[i] + v * E2[i] + t * a[i] for i in range(3)))
    xs, ys, zs = zip(*ps)
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(outline)]
    sc.add(compact(GE.prism(sc.cam, O, a, loop, h, mat, **kw)), ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))), bias)


# =====================================================================================
# q:mc_5ax — 5-axis machining centre (trunnion type): the cradle tilts (A) and the round table
# turns (C) so the tool reaches the blades of an impeller from any angle in one setup
# =====================================================================================
@picto("mc_5ax")
def _():
    t = math.radians(28)
    A = (0, -math.sin(t), math.cos(t))

    def rot(y, z):
        return (y * math.cos(t) - z * math.sin(t), y * math.sin(t) + z * math.cos(t))

    def W(y, z):
        yy, zz = rot(y, z)
        return (0, yy, zz)

    def fn(sc):
        for x0 in (-98, 70):                                                # trunnion supports
            BOX(sc, x0, -36, -90, 28, 72, 96, "pt", ch=3, dark=1)
        X(sc, -70, 140, [rot(y, z) for y, z in ((-52, -34), (52, -34), (52, -16), (-52, -16))], "m", dark=.3)   # cradle
        C = W(0, -16)
        CYL(sc, C, A, 48, 10, "m", seg=48)                                  # C table
        top = tuple(C[i] + A[i] * 10 for i in range(3))
        CYL(sc, top, A, 40, 8, "w", seg=40)                                 # impeller back plate
        hub = tuple(top[i] + A[i] * 8 for i in range(3))
        CYL(sc, hub, A, 14, 44, "w", seg=24, r1=8)                          # hub
        E1, E2, _ = GE.frame(A)
        for k in range(7):                                                  # twisted blades
            a = 2 * PI * k / 7
            c, s_ = math.cos(a), math.sin(a)
            bl = [(u * c - v * s_, u * s_ + v * c) for u, v in ((12, -1.8), (39, -1.8), (39, 1.8), (12, 1.8))]
            PR(sc, hub, A, bl, 36, "w", -.2, twist=.7, scale=lambda q: 1 - .45 * q)
        # spindle from above with a ball-nose end mill
        zt = hub[2] + 30
        BOX(sc, -32, -56, zt + 54, 64, 64, 46, "pt", ch=5)
        CYL(sc, (0, -24, zt + 54), (0, 0, -1), 16, 8, "dk", seg=24)
        CYL(sc, (0, -24, zt + 46), (0, 0, -1), 10, 14, "m", seg=20, r1=6)
        CYL(sc, (0, -24, zt + 32), (0, 0, -1), 4, 30, "t", seg=14)
        sc.zt = zt
    s, sc = fit(fn, 28, 22, (40, 14, 280, 172), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    zt = sc.zt
    s += arc3(cam, (-102, 0, -25), (1, 0, 0), 46, 60, 150)
    s += arc3(cam, W(0, -11), A, 60, -60, 40)
    s += arc3(cam, (0, -24, zt + 40), (0, 0, 1), 14, 200, 330)
    a = cam.xy(pt3((-102, 0, -25), (1, 0, 0), 46, 150))
    c = cam.xy(pt3(W(0, -11), A, 60, 40))
    h = cam.xy((32, -56, zt + 90))
    w = cam.xy(pt3(W(0, 30), A, 44, 200))
    s += al(a[0] - 6, a[1] + 14, "A軸（傾斜）", "end") + al(c[0] + 16, c[1] + 22, "C軸（回転）", "start")
    s += lab(h[0] + 8, h[1], "主軸", "start") + lab(w[0] - 8, w[1] - 10, "工作物（翼車）", "end")
    return s


# =====================================================================================
# q:gantry — gantry (portal) machining centre: two columns and a cross rail span the long table;
# the spindle head runs along the rail and the table (or gantry) travels lengthwise
# =====================================================================================
@picto("gantry")
def _():
    zr = 120

    def fn(sc):
        BOX(sc, -100, -170, -70, 200, 340, 30, "pt", dark=1)                # bed
        BOX(sc, -90, -160, -40, 180, 320, 16, "m")                          # long table
        BOX(sc, -70, -120, -24, 140, 220, 50, "w", ch=4)                    # large die / casting
        for x0 in (-150, 116):                                              # columns
            BOX(sc, x0, 50, -70, 34, 44, zr + 30 + 70, "pt", ch=3, dark=1)
        BOX(sc, -150, 44, zr, 300, 50, 32, "pt", ch=3, dark=1)              # cross rail
        BOX(sc, -4, 14, 40, 40, 30, zr + 50 - 40, "pt", ch=4)               # ram / spindle head
        CYL(sc, (16, 29, 40), (0, 0, -1), 13, 8, "dk", seg=24)
        CYL(sc, (16, 29, 32), (0, 0, -1), 6, 6, "t", seg=16)

        def cav(s_):                                                        # machined pocket on the die
            o = path(P([s_.cam.xy(p) for p in ((-40, -80, 26.2), (30, -80, 26.2), (40, -10, 26.2), (40, 50, 26.2), (-40, 50, 26.2))]), "w3")
            return o
        RAW(sc, cav, ((-40, -80, 26), (40, 50, 26.3)), -1)
    s, sc = fit(fn, 28, 22, (30, 14, 292, 176), sh_ry=7, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-60, 30, zr + 48), (100, 30, zr + 48), both=True)
    s += arrow3(cam, (110, -150, -40), (110, -40, -40), both=True)
    s += arrow3(cam, (52, 14, 130), (52, 14, 80))
    r = cam.xy((-150, 50, 30))
    h = cam.xy((52, 14, 104))
    w = cam.xy((-70, -120, -10))
    t = cam.xy((110, -95, -40))
    s += lab(r[0] - 6, r[1], "門形フレーム", "end") + al(h[0] + 8, h[1] + 4, "主軸頭", "start")
    s += lab(w[0] - 6, w[1], "大物工作物", "end") + al(t[0] + 16, t[1] + 20, "テーブル", "start")
    return s


# =====================================================================================
# q:transfer — transfer machine: parts step from station to station along the line; at each
# station a multi-spindle head drills many holes at once
# =====================================================================================
@picto("transfer")
def _():
    xs, zt = (-120, 0, 120), 30

    def fn(sc):
        BOX(sc, -180, -50, -60, 360, 100, 30, "pt", dark=1)                 # base / transfer bar
        BOX(sc, -180, 54, -60, 360, 40, 230, "pt", dark=1)                  # back frame
        for k, x in enumerate(xs):
            BOX(sc, x - 44, -36, -30, 88, 72, 10, "m")                      # pallet
            BOX(sc, x - 34, -28, -20, 68, 56, 50, "w", ch=3)                # part
            BOX(sc, x - 40, -30, zt + 54, 80, 70, 34, "dk", ch=3)           # multi-spindle head
            for j in range(4):
                px = x - 24 + 16 * j
                CYL(sc, (px, -6, zt + 54), (0, 0, -1), 4, 8, "m", -.5, seg=12, lines=False)
                if k > 0 or j < 0:
                    pass
                CYL(sc, (px, -6, zt + 46), (0, 0, -1), 2.2, 30 if k == 1 else 16, "t", -.5, seg=10, lines=False)

            def holes(s_, x=x, k=k):
                o = ""
                if k == 2:
                    for j in range(4):
                        o += hole3(s_.cam, (x - 24 + 16 * j, -6, zt + .2), (0, 0, 1), 3)
                return o
            RAW(sc, holes, ((x - 34, -28, zt), (x + 34, 28, zt + .3)), -1)
    s, sc = fit(fn, -24, 22, (22, 18, 298, 172), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-150, -60, -44), (150, -60, -44))
    s += arrow3(cam, (-60, -30, zt + 100), (-60, -30, zt + 60))
    h = cam.xy((-160, -30, zt + 88))
    t = cam.xy((0, -60, -44))
    f = cam.xy((-60, -30, zt + 80))
    s += lab(h[0] - 2, h[1] - 8, "多軸ヘッド", "start") + al(t[0], t[1] + 20, "搬送（ステーション順送り）")
    s += al(f[0] + 6, f[1] + 4, "送り", "start")
    return s


# =====================================================================================
# q:gundrill — gun drilling: a long single-lip drill, started in a guide bush, is fed with
# high-pressure oil through its body; oil and chips flush back along the V-flute
# =====================================================================================
@picto("gundrill")
def _():
    rd, depth = 5, 150

    def fn(sc):
        BOX(sc, 0, -40, -40, 180, 80, 80, "w", ch=4)                        # work (block / shaft)
        BOX(sc, -26, -30, -40, 18, 60, 66, "dk", ch=2)                      # guide-bush holder
        CYL(sc, (-26.3, 0, 0), (1, 0, 0), 9, .3, "m", -.5, seg=20)
        CYL(sc, (-200, 0, 0), (1, 0, 0), rd, 174, "t", -1, seg=14)           # long gun-drill shank
        BOX(sc, -260, -26, -30, 50, 52, 60, "dk", ch=4)                     # drill spindle / oil inlet
        CYL(sc, (-212, 0, 0), (1, 0, 0), 12, 12, "m", seg=20)

        def hole(s_):                                                       # the deep hole (hidden lines)
            o = ""
            for sg in (-1, 1):
                a, b = s_.cam.xy((0, 0, sg * rd)), s_.cam.xy((depth, 0, sg * rd))
                o += line(a[0], a[1], b[0], b[1], "o thin dash")
            c = s_.cam.xy((depth, 0, 0))
            return o + circ(c[0], c[1], 2.2, "fdot")
        RAW(sc, hole, ((-.5, -40, -40), (0, 40, 40)), -2)
    s, sc = fit(fn, 30, 20, (20, 28, 300, 168), sh_ry=7, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-120, 0, 0), (1, 0, 0), 11, 100, 200)
    s += arrow3(cam, (-150, 0, 26), (-90, 0, 26))
    p = cam.xy((-236, -10, 30))
    s += path("M%s %s L%s %s" % (n(p[0]), n(p[1] - 26), n(p[0]), n(p[1] - 2)), "fl") + drops(p[0], p[1] - 30, 3, 30, 10, -90)
    e = cam.xy((-8, -20, -30))
    s += drops(e[0], e[1], 4, 50, 16, 110)
    o = cam.xy((-236, -10, 30))
    w = cam.xy((90, -40, -40))
    d = cam.xy((depth / 2, -40, 40))
    f = cam.xy((-120, 0, 26))
    s += lab(o[0] + 8, o[1] - 34, "高圧切削油", "start") + lab(w[0], w[1] + 20, "工作物")
    s += lab(d[0] + 10, d[1] - 16, "深い穴（L/D 50以上も）", "middle") + al(f[0], f[1] + 30, "送り")
    return s


# =====================================================================================
# q:finebore — fine boring: a rigid bar with one diamond / carbide tip turns and feeds slowly
# through the piston-pin holes, finishing them to a micron-level roundness
# =====================================================================================
@picto("finebore")
def _():
    Rp, H, zp, rh = 46, 84, 34, 13

    def fn(sc):
        BOX(sc, -70, -60, -26, 140, 120, 16, "m")                           # fixture plate
        CYL(sc, (0, 0, -10), (0, 0, 1), Rp, H, "w", seg=48)                 # piston (crown down)
        CYL(sc, (0, 0, -10 + H), (0, 0, 1), Rp - 1, .2, "w", seg=48, holes=[GE.circle_outline(Rp - 7, 40, 8)])

        def marks(s_):
            o = hole3(s_.cam, (0, 0, -10 + H + .3), (0, 0, 1), Rp - 7, "bg")
            for k in range(3):                                              # ring grooves near the crown
                o += path(P([s_.cam.xy((Rp * .999 * math.sin(a), -Rp * .999 * math.cos(a), 4 + 7 * k))
                             for a in [math.radians(-70 + 140 * j / 16) for j in range(17)]], False), "gr")
            return o
        RAW(sc, marks, ((-Rp, -Rp, -10), (Rp, 0, -10 + H + .4)), -1)
        # pin hole on the -x side (tangent patch) and the boring bar entering it
        RAW(sc, lambda s_: hole3(s_.cam, (-Rp - .2, 0, zp), (-1, 0, 0), rh, "bg"), ((-Rp - .4, -rh, zp - rh), (-Rp - .2, rh, zp + rh)), -1.5)
        CYL(sc, (-170, 0, zp), (1, 0, 0), 24, 34, "dk", -2, seg=28)          # spindle
        CYL(sc, (-136, 0, zp), (1, 0, 0), 9, 92, "m", -2, seg=20)            # boring bar
        Z(sc, zp + 6, 4, [(-50, -4), (-44, -4), (-44, 3), (-50, 3)], "t", -3)  # diamond tip
    s, sc = fit(fn, 30, 24, (24, 18, 296, 172), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-110, 0, zp), (1, 0, 0), 16, 100, 200)
    s += arrow3(cam, (-120, 0, zp + 30), (-70, 0, zp + 30))
    r = cam.xy(pt3((-110, 0, zp), (1, 0, 0), 16, 200))
    f = cam.xy((-95, 0, zp + 30))
    t = cam.xy((-47, 0, zp - 12))
    w = cam.xy((Rp, -Rp, 0))
    s += al(r[0], r[1] + 26, "回転") + al(f[0], f[1] - 10, "送り")
    s += lab(t[0] + 20, t[1] + 34, "単刃（ダイヤモンド）", "middle") + lab(w[0] + 4, w[1] + 18, "ピストン（ピン穴）", "start")
    return s


# =====================================================================================
# q:edm — (small-hole) EDM: sparks between a rotating pipe electrode and the work melt the
# metal away in a dielectric (water / oil); no cutting force, so hard metals are no problem
# =====================================================================================
@picto("edm")
def _():
    zt = 30

    def fn(sc):
        BOX(sc, -110, -70, -60, 220, 140, 20, "m")                          # table
        BOX(sc, -76, -46, -40, 152, 92, zt + 40, "w", ch=4)                 # work
        BOX(sc, -26, 30, zt + 76, 52, 60, 70, "dk", ch=4)                   # electrode head
        BOX(sc, -14, -8, zt + 20, 28, 16, 10, "m", -1)                      # electrode guide
        CYL(sc, (0, 0, zt + 76), (0, 0, -1), 2.4, 76, "cu", -1, seg=10)     # pipe electrode

        def done(s_):
            o = ""
            for i, (x, y) in enumerate(((-50, -20), (-30, -20), (-50, 10), (-30, 10), (34, -24), (50, 14))):
                o += hole3(s_.cam, (x, y, zt + .2), (0, 0, 1), 2.6)
            return o
        RAW(sc, done, ((-76, -46, zt), (76, 46, zt + .3)), -.5)
    s, sc = fit(fn, -26, 24, (40, 18, 280, 172), sh_ry=7, sh_k=.42, ret_scene=True)
    cam = sc.cam
    tip = cam.xy((0, 0, zt))
    s += sparks(tip[0], tip[1] - 1, 9, 5, -170, -10)
    s += arrow3(cam, (-30, -8, zt + 66), (-30, -8, zt + 30))
    s += arc3(cam, (0, 0, zt + 60), (0, 0, 1), 10, 200, 340)
    # generator: wires to the electrode head and to the work
    g = cam.xy((-130, -60, zt + 20))
    hd = cam.xy((-26, 30, zt + 110))
    wk = cam.xy((-76, -46, -10))
    s += rect(g[0] - 22, g[1] - 14, 44, 26, "dk", 3)
    s += path("M%s %s L%s %s" % (n(g[0] + 22), n(g[1] - 4), n(hd[0]), n(hd[1])), "o thin")
    s += path("M%s %s L%s %s" % (n(g[0]), n(g[1] + 12), n(wk[0]), n(wk[1])), "o thin")
    e = cam.xy((0, 0, zt + 46))
    w = cam.xy((76, -46, -20))
    f = cam.xy((-30, -8, zt + 48))
    s += lab(g[0], g[1] + 30, "電源") + lab(e[0] + 12, e[1] + 4, "パイプ電極", "start")
    s += lab(w[0] - 10, w[1] + 22, "工作物（放電で溶かす）", "end") + al(f[0] - 8, f[1] + 4, "送り", "end")
    return s


# =====================================================================================
# q:laser — laser cutting (3D): a nozzle head on a 5-axis arm follows the trim line of a formed
# part; the focused beam melts the steel and assist gas blows it out of the kerf
# =====================================================================================
@picto("laser")
def _():
    t = 3
    prof = [(-110, 0), (-60, 0), (-40, 50), (40, 50), (60, 0), (110, 0)]      # hat section (y, z)

    def fn(sc):
        for (y0, z0), (y1, z1) in zip(prof, prof[1:]):                      # thin sheet, one flat strip each
            dy, dz = y1 - y0, z1 - z0
            L_ = math.hypot(dy, dz)
            ny, nz = -dz / L_ * t, dy / L_ * t
            X(sc, -130, 260, [(y0, z0), (y1, z1), (y1 + ny, z1 + nz), (y0 + ny, z0 + nz)], "w")

        def kerf(s_):                                                       # cut line already made + cut-out hole
            pts = [s_.cam.xy((x, -20, 53.2)) for x in (-110, 10)]
            o = line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], "o")
            return o + path(P([s_.cam.xy((-60 + 14 * math.cos(a), 20 + 9 * math.sin(a), 53.2)) for a in [2 * PI * k / 20 for k in range(20)]]), "bg")
        RAW(sc, kerf, ((-130, -40, 53), (130, 40, 53.3)), -1)
        # head: body + nozzle cone, tilted slightly
        CYL(sc, (10, -20, 70), (0, 0, 1), 7, 18, "m", -2, seg=20, r1=16)    # nozzle
        CYL(sc, (10, -20, 88), (0, 0, 1), 18, 60, "dk", -2, seg=24)         # head body
    s, sc = fit(fn, -26, 26, (24, 18, 296, 172), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((10, -20, 70)), cam.xy((10, -20, 53.4))
    s += line(a[0], a[1], b[0], b[1], "beam") + sparks(b[0], b[1] + 2, 8, 5, 20, 160)
    s += arrow3(cam, (30, -50, 60), (100, -50, 60))
    s += arc3(cam, (10, -20, 120), (0, 1, 0), 34, 60, 120)
    h = cam.xy((10, -20, 148))
    k = cam.xy((-80, -20, 53))
    w = cam.xy((110, -110, 0))
    f = cam.xy((65, -50, 60))
    s += lab(h[0] + 24, h[1] + 4, "加工ヘッド（5軸）", "start") + lab(k[0], k[1] - 10, "切断線")
    s += lab(w[0], w[1] + 22, "成形した鋼板部品", "end") + al(f[0] + 4, f[1] + 18, "レーザ光で切る")
    return s
