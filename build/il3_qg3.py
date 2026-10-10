"""v3 principle drawings (shaded 3D) for heavy-electrical / test equipment, team qg3:
load bank, spin pit, stator core loop test, tensile & Charpy testers, hydrostatic test,
epoxy casting, form-wound coil spreader, laser tracker, autofrettage.
Overrides the older flat drawings in il_pictos_ind2.py / il_pictos_gear.py."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def P3(cam, pts, cls, close=True):
    return path(P([cam.xy(p) for p in pts], close), cls)


def bez(p0, p1, p2, p3, k=12):
    """points of a cubic Bezier in 3D."""
    o = []
    for i in range(k + 1):
        t = i / k
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        o.append(tuple(a * p0[j] + b * p1[j] + c * p2[j] + d * p3[j] for j in range(3)))
    return o


def cable(cam, pts, c="cable"):
    return path(P([cam.xy(p) for p in pts], False), c)


def gauge3(cam, C, A, r, ang=40):
    """round dial on a surface (centre C, normal A) with a needle; ang = needle angle from 12 o'clock."""
    E1, E2, _ = GE.frame(A)
    o = path(P(circ3(cam, C, A, r * 1.18, 24)), "m") + path(P(circ3(cam, C, A, r, 24)), "bg")
    a = math.radians(ang)
    up = (0, 0, 1)
    rt = GE._norm(GE._cross(up, A)) if abs(A[2]) < .9 else E1
    tip = tuple(C[i] + r * .78 * (math.cos(a) * up[i] + math.sin(a) * rt[i]) for i in range(3))
    a0, b0 = cam.xy(C)
    a1, b1 = cam.xy(tip)
    return o + line(a0, b0, a1, b1, "needle") + circ(a0, b0, 1.3, "d")


def bar(cam, p0, p1, w, h, mat, side=(0, 0, 1), lines=True):
    """rectangular-section bar from p0 to p1 (section w x h, h measured along `side`)."""
    A = tuple(p1[i] - p0[i] for i in range(3))
    L = math.sqrt(sum(a * a for a in A))
    E1, E2, An = GE.frame(A)
    sd = GE._norm(tuple(side[i] - GE._dot(side, An) * An[i] for i in range(3)))
    # side direction expressed in (E1, E2)
    su, sv = GE._dot(sd, E1), GE._dot(sd, E2)
    wu, wv = -sv, su
    loop = [(su * h / 2 * a + wu * w / 2 * b, sv * h / 2 * a + wv * w / 2 * b, k)
            for k, (a, b) in enumerate(((-1, -1), (-1, 1), (1, 1), (1, -1)))]
    return compact(GE.prism(cam, p0, An, loop, L, mat, lines=lines))


# =====================================================================================
# q:loadbank — generator set under test: cables to a resistor load bank, fan blows the heat away
# =====================================================================================
@picto("loadbank")
def _():
    def fn(sc):
        BOX(sc, -170, -40, -50, 120, 80, 12, "dk")                          # skid
        CYL(sc, (-160, 0, 0), (1, 0, 0), 36, 92, "pt", seg=36, dark=1)       # generator frame
        CYL(sc, (-168, 0, 0), (1, 0, 0), 24, 8, "m", seg=28)                # end bracket
        CYL(sc, (-176, 0, 0), (1, 0, 0), 7, 8, "w", seg=16)                 # shaft end
        BOX(sc, -112, -18, 34, 34, 36, 18, "m", ch=2)                       # terminal box
        BOX(sc, -150, -30, -38, 12, 60, 2, "dk")                            # feet (hidden under frame)
        # load bank cabinet with a resistor window and cooling fan on the roof
        BOX(sc, 0, -46, -50, 150, 92, 108, "pt", dark=1, ch=3)
        CYL(sc, (75, 0, 58), (0, 0, 1), 34, 8, "dk", seg=36)                # fan shroud
        CYL(sc, (75, 0, 66), (0, 0, 1), 10, 3, "m", seg=16)                 # fan hub

        def face(s_):
            cam = s_.cam
            y = -46.2
            o = P3(cam, [(52, y, -36), (140, y, -36), (140, y, 46), (52, y, 46)], "bg")
            zz = ""
            for j in range(5):                                             # resistor grids (glowing zig-zags)
                z0 = -26 + j * 15
                pts = [(56 + 4 * k, y, z0 + (4 if k % 2 else -4)) for k in range(21)]
                zz += P([cam.xy(p) for p in pts], False)
            o += path(zz, "hl")
            # V/f recorder screen on the left panel
            x0, x1, z0, z1 = 10, 44, 10, 38
            o += P3(cam, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], "scrn")
            cv = []
            for k in range(17):
                t = k / 16
                v = 0 if t < .35 else -7 * math.exp(-(t - .35) * 9) * math.cos((t - .35) * 18)
                cv.append((x0 + 3 + (x1 - x0 - 6) * t, y, (z0 + z1) / 2 + 4 + v))
            o += path(P([cam.xy(p) for p in cv], False), "scrg")
            for k in range(3):
                o += hole3(cam, (16 + 11 * k, y, -20), (0, -1, 0), 3.2, "m")
            # fan blades seen through the guard
            for k in range(6):
                a = math.radians(k * 60 + 15)
                a2 = a + .5
                o += P3(cam, [(75 + 11 * math.cos(a), 30 * 0 + 11 * math.sin(a), 66.2), (75 + 31 * math.cos(a), 31 * math.sin(a), 66.2),
                              (75 + 31 * math.cos(a2), 31 * math.sin(a2), 66.2)], "ms3")
            return o
        RAW(sc, face, ((0, -46.4, -40), (150, -46.2, 66.3)), -3)

        def cab(s_):
            cam = s_.cam
            o = ""
            for k in range(3):
                d = (k - 1) * 9
                o += cable(cam, bez((-78, -2 + d, 44), (-30, -2 + d, 50), (-34, -34 + d, -48), (0, -30 + d * .6, -36 - k * 3)))
            return o
        RAW(sc, cab, ((-78, -50, -50), (0, 10, 52)), -5)
    s, sc = fit(fn, 22, 18, (24, 40, 300, 176), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += heat(*cam.xy((62, 0, 80)), cnt=3, gap=10)
    s += arrow3(cam, (110, 0, 74), (110, 0, 112))
    s += arc3(cam, (-176, 0, 0), (1, 0, 0), 16, 200, 330)
    g = cam.xy((-115, -40, -50))
    r = cam.xy((96, -46, -50))
    f = cam.xy((110, 0, 112))
    v = cam.xy((27, -46, 38))
    s += lab(g[0], g[1] + 18, "発電機") + lab(r[0], r[1] + 16, "抵抗器")
    s += al(f[0] + 6, f[1] + 4, "送風で放熱", "start") + lab(cam.xy((0, -46, 58))[0] - 4, cam.xy((0, -46, 58))[1] - 2, "電圧・周波数", "end")
    return s


# =====================================================================================
# q:spinpit — rotor spun over speed inside a vacuum pit (front half cut away), driven from the lid
# =====================================================================================
def half_ann(sc, z0, h, ro, ri, mat, bias=0.0, **kw):
    """back half (y >= 0) of an annulus, extruded along z: the cut-away wall of a round pit."""
    pts = arc(0, 0, ro, 0, 180, 16) + arc(0, 0, ri, 180, 0, 16)
    Z(sc, z0, h, banded(pts, 2), mat, bias, **kw)


@picto("spinpit")
def _():
    R, Ri, H = 92, 78, 108

    def fn(sc):
        Z(sc, -14, 14, banded(arc(0, 0, R + 8, -8, 188, 24), 3), "m", dark=1)      # base (cut along the front)
        half_ann(sc, 0, H, R, Ri, "m", dark=1)                                       # pit wall
        half_ann(sc, 20, 60, Ri, Ri - 9, "dk")                                      # containment ring
        lid = [(x, max(y, -26)) for x, y in arc(0, 0, R + 4, -20, 200, 24)]
        Z(sc, H, 12, banded(hull(lid), 3), "pt", dark=1)                            # lid
        CYL(sc, (0, 0, H + 12), (0, 0, 1), 24, 30, "dk", seg=32)                    # drive turbine
        CYL(sc, (0, 0, H + 42), (0, 0, 1), 14, 6, "m", seg=24)
        CYL(sc, (0, 0, 66), (0, 0, 1), 4, H - 66, "w", seg=16)                      # quill shaft
        # rotor: disc with a conical hub and radial blades
        CYL(sc, (0, 0, 38), (0, 0, 1), 52, 10, "w", seg=48)
        CYL(sc, (0, 0, 48), (0, 0, 1), 20, 18, "w", seg=28, r1=8)
        for k in range(12):
            a = math.radians(k * 30 + 8)
            c, s_ = math.cos(a), math.sin(a)
            pts = [(u * c - v * s_, u * s_ + v * c) for u, v in ((19, -1.4), (49, -1.4), (49, 1.4), (19, 1.4))]
            Z(sc, 48, 9, pts, "w", -.5, lines=False)
        # vacuum line and pump outside the pit
        BOX(sc, 120, 20, -14, 46, 40, 34, "pt", ch=3)
        CYL(sc, (R - 2, 40, 90), (1, 0, 0), 5, 52, "m", seg=16)
        CYL(sc, (142, 40, 20), (0, 0, 1), 5, 75, "m", seg=16)
    s, sc = fit(fn, 16, 26, (64, 22, 300, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 44), (0, 0, 1), 64, 200, 330)
    t = cam.xy((24, 0, H + 34))
    v = cam.xy((143, 20, -14))
    rr = cam.xy((-Ri + 4, 0, 50))
    w = cam.xy((0, -60, 38))
    s += lab(t[0] + 6, t[1] + 2, "駆動タービン", "start") + lab(v[0], v[1] + 18, "真空ポンプ")
    s += lab(rr[0] - 10, rr[1] + 2, "防護リング", "end") + al(w[0] + 30, w[1] + 28, "過回転", "start")
    return s


# =====================================================================================
# q:coreloop — stator core excited by a few turns of cable through the bore; an IR camera finds hot spots
# =====================================================================================
@picto("coreloop")
def _():
    R, Ri, H, N = 92, 60, 64, 24

    def fn(sc):
        hole = []
        for k in range(N):                                            # bore with open slots
            a0 = 2 * math.pi * k / N
            for da, r in ((-.055, Ri + 11), (.055, Ri + 11), (.055, Ri), (2 * math.pi / N - .055, Ri)):
                hole.append((r * math.cos(a0 + da), r * math.sin(a0 + da), len(hole)))
        CYL(sc, (0, 0, 0), (0, 0, 1), R, H, "m", seg=48, holes=[hole], bands=12, dark=.3)

        def marks(s_):
            cam = s_.cam
            o = ""
            for z in range(7, H, 7):                                 # lamination stack lines (front half)
                pts = [cam.xy((R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), z)) for a in range(190, 356, 12)]
                o += P(pts, False)
            o = path(o, "gr")
            # hot spot on the inner (back) wall
            o += path(P(circ3(cam, (Ri * math.cos(1.25), Ri * math.sin(1.25), 30), (-math.cos(1.25), -math.sin(1.25), 0), 6, 16)), "flash")
            o += path(P(circ3(cam, (Ri * math.cos(1.25), Ri * math.sin(1.25), 30), (-math.cos(1.25), -math.sin(1.25), 0), 2.6, 12)), "h")
            # excitation cable: turns over the top face and down the outside
            for k, a in enumerate((206, 216, 226)):
                c, s2 = math.cos(math.radians(a)), math.sin(math.radians(a))
                pts = [(Ri * c, Ri * s2, H - 4), ((Ri + 2) * c, (Ri + 2) * s2, H + 3), ((R + 3) * c, (R + 3) * s2, H + 3),
                       ((R + 5) * c, (R + 5) * s2, H - 6), ((R + 5) * c, (R + 5) * s2, 4)]
                pts += bez(pts[-1], ((R + 6) * c, (R + 6) * s2, -6), (-140, -10 - 8 * k, -6), (-150, -10 - 8 * k, 4), 8)[1:]
                o += cable(cam, pts)
            return o
        RAW(sc, marks, ((-R - 6, -R - 6, -6), (R + 6, R + 6, H + 6)), -40)
        BOX(sc, -190, -40, -6, 40, 44, 40, "pt", ch=3)                     # excitation power supply
        # IR camera on a post, looking into the bore
        CYL(sc, (150, 20, -6), (0, 0, 1), 4, 130, "m", seg=12)
        BOX(sc, 130, 6, 124, 40, 28, 22, "dk", ch=3)
        CYL(sc, (130, 20, 135), (-1, 0, 0), 9, 10, "m", seg=20)

        def src(s_):
            cam = s_.cam
            o = P3(cam, [(-182, -40.2, 6), (-158, -40.2, 6), (-158, -40.2, 24), (-182, -40.2, 24)], "scrn")
            pts = [(-180 + 20 * t / 12, -40.2, 15 + 5 * math.sin(t / 12 * 2 * math.pi)) for t in range(13)]
            return o + path(P([cam.xy(p) for p in pts], False), "scrg")
        RAW(sc, src, ((-190, -40.4, 0), (-150, -40.2, 30)), -2)
    s, sc = fit(fn, -18, 30, (16, 26, 304, 176), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    hs = (Ri * math.cos(1.25), Ri * math.sin(1.25), 30)
    a = cam.xy((120, 20, 135))
    b = cam.xy(hs)
    s += line(a[0], a[1], b[0] + 3, b[1] - 2, "ray") + line(a[0], a[1] + 5, b[0] - 3, b[1] + 3, "ray")
    s += arc3(cam, (0, 0, H + 1), (0, 0, 1), (R + Ri) / 2 + 4, -12, 70)
    m = max((cam.xy((R * math.cos(t / 20), R * math.sin(t / 20), H * .5)) for t in range(126)), key=lambda q: q[0])
    f = cam.xy((-170, -40, -6))
    c = cam.xy((150, 6, 146))
    s += al(m[0] + 8, m[1] - 14, "磁束", "start") + lab(f[0], f[1] + 16, "励磁電源")
    s += lab(c[0] - 6, c[1] - 14, "赤外線カメラ") + lab(b[0] - 8, cam.xy((0, R, H))[1] - 8, "発熱箇所", "end")
    return s


# =====================================================================================
# q:tensile_charpy — universal tester pulls a round specimen; Charpy pendulum breaks a notched bar
# =====================================================================================
@picto("tensile_charpy")
def _():
    piv = (88, 0, 150)
    L, th = 92, math.radians(116)
    hc = (piv[0] - L * math.sin(th), 0, piv[2] - L * math.cos(th))

    def fn(sc):
        # --- universal testing machine (left)
        BOX(sc, -170, -30, 0, 130, 60, 30, "pt", dark=1, ch=3)
        for x in (-155, -55):
            CYL(sc, (x, 0, 30), (0, 0, 1), 6, 150, "w", seg=16)
        BOX(sc, -170, -22, 180, 130, 44, 18, "pt", dark=1, ch=3)               # top crosshead
        BOX(sc, -166, -20, 118, 122, 40, 16, "pt", ch=3)                         # moving crosshead
        CYL(sc, (-105, 0, 108), (0, 0, 1), 10, 10, "m", seg=20)                 # load cell
        for x in (-117, -98):                                                    # wedge grips (jaws)
            BOX(sc, x, -9, 84, 10, 18, 24, "dk")
            BOX(sc, x, -9, 30, 10, 18, 26, "dk")
        segs = [(32, 5, 5, 24), (56, 3.4, 3.4, 12), (68, 3.4, 2.1, 5), (73, 2.1, 3.4, 5), (78, 3.4, 3.4, 10), (88, 5, 5, 22)]
        for z, r0, r1, h in segs:
            CYL(sc, (-102, 0, z), (0, 0, 1), r0, h, "w", seg=16, r1=r1, bias=-1)
        # --- Charpy impact tester (right)
        BOX(sc, 20, -30, 0, 130, 60, 22, "pt", dark=1, ch=3)
        BOX(sc, 80, 14, 22, 16, 14, 140, "pt", dark=1)                           # column
        CYL(sc, (88, 14, 150), (0, -1, 0), 6, 10, "m", seg=16)                  # pivot
        BOX(sc, 96, -26, 22, 10, 52, 8, "dk")                                    # support block
        for y in (-26, 16):
            BOX(sc, 96, y, 30, 10, 10, 12, "dk")                                 # anvils
        BOX(sc, 87, -28, 30, 9, 56, 9, "w")                                      # notched specimen

        def pend(s_):
            cam = s_.cam
            o = bar(cam, (piv[0], 4, piv[2]), (hc[0], 4, hc[2]), 6, 5, "m", side=(0, 1, 0))
            o += compact(GE.prism(cam, (hc[0], 9, hc[2]), (0, -1, 0), GE.circle_outline(20, 28, 10), 18, "m", smooth=True))
            lu, lv = math.cos(th), -math.sin(th)                       # leading direction of the swing
            wed = [(lu * p_ - lv * q_, lv * p_ + lu * q_, i) for i, (p_, q_) in enumerate(((7, 0), (-6, 5), (-6, -5)))]
            o += compact(GE.prism(cam, (hc[0] + 18 * lu, 6, hc[2] + 18 * lv), (0, -1, 0), wed, 12, "t"))
            return o
        RAW(sc, pend, ((hc[0] - 20, -9, piv[2] - 4), (piv[0] + 4, 9, hc[2] + 18)), -3)

        def notch(s_):
            cam = s_.cam
            return P3(cam, [(96.1, -2.5, 39.1), (92.5, 0, 39.1), (96.1, 2.5, 39.1)], "bg")
        RAW(sc, notch, ((87, -28, 39), (96, 28, 39.2)), -2)
    s, sc = fit(fn, 18, 12, (14, 22, 306, 172), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-30, 0, 120), (-30, 0, 156))
    s += arc3(cam, piv, (0, 1, 0), L * .74, 20, -62)
    a = cam.xy((-30, 0, 136))
    p = cam.xy(hc)
    sp = cam.xy((-94, 0, 70))
    nt = cam.xy((100, -28, 30))
    s += al(a[0] + 6, a[1] + 4, "引張", "start") + lab(sp[0] + 34, sp[1] + 4, "試験片", "start")
    s += lab(p[0] - 4, p[1] - 26, "振り子") + lab(nt[0] - 2, nt[1] + 22, "切欠き試験片")
    return s


# =====================================================================================
# q:hydrotest — water passages of a casting filled and pumped above working pressure, held, checked for leaks
# =====================================================================================
def drop3(x, y, k=1.0):
    return path("M%s %s q%s %s 0 %s q%s %s 0 %sZ" % (n(x), n(y), n(3.2 * k), n(5 * k), n(8 * k), n(-3.2 * k), n(-3 * k), n(-8 * k)), "fl")


@picto("hydrotest")
def _():
    def fn(sc):
        # casting with the upper-front corner cut away to show the filled water passage
        BOX(sc, 0, -40, 0, 80, 80, 70, "w")
        BOX(sc, 80, 0, 0, 80, 40, 70, "w")
        BOX(sc, 80, -40, 0, 80, 14, 34, "w")
        BOX(sc, 80, -12, 0, 80, 12, 34, "w")
        BOX(sc, 80, -26, 0, 80, 14, 18, "w")
        BOX(sc, 80, -26, 18, 80, 14, 13, "fl")

        def cut(s_):
            cam = s_.cam
            o = P3(cam, [(112, -0.2, 34), (126, -0.2, 34), (126, -0.2, 62), (112, -0.2, 62)], "fl")
            o += P3(cam, [(140, -0.2, 40), (152, -0.2, 40), (152, -0.2, 54), (140, -0.2, 54)], "fl")
            return o
        RAW(sc, cut, ((80, -0.4, 34), (160, -0.2, 70)), -1)
        # blind plates bolted over the openings
        BOX(sc, -7, -26, 14, 7, 52, 42, "dk", ch=2)
        BOX(sc, 18, -22, 70, 44, 44, 6, "dk", ch=2)

        def bolts(s_):
            cam = s_.cam
            o = ""
            for y, z in ((-20, 20), (20, 20), (-20, 50), (20, 50)):
                o += hole3(cam, (-7.2, y, z), (-1, 0, 0), 2.6, "m")
            for x, y in ((24, -16), (56, -16), (24, 16), (56, 16)):
                o += hole3(cam, (x, y, 76.2), (0, 0, 1), 2.6, "m")
            return o
        RAW(sc, bolts, ((-7.4, -26, 14), (62, 26, 76.4)), -3)
        CYL(sc, (-7, 0, 35), (-1, 0, 0), 5, 10, "m", seg=16)                       # inlet fitting
        # hand / motor pump unit with pressure gauge
        BOX(sc, -150, -60, -2, 64, 44, 40, "pt", ch=3)
        CYL(sc, (-118, -38, 38), (0, 0, 1), 3, 24, "m", seg=12)
        CYL(sc, (-118, -38, 62), (0, -1, 0), 14, 6, "m", seg=24)

        def gg(s_):
            return gauge3(s_.cam, (-118, -44.2, 62), (0, -1, 0), 11, 50)
        RAW(sc, gg, ((-132, -44.4, 48), (-104, -44.2, 76)), -3)

        def hose(s_):
            cam = s_.cam
            return cable(cam, bez((-86, -38, 18), (-50, -38, 18), (-50, 0, 35), (-17, 0, 35)), "pres")
        RAW(sc, hose, ((-86, -40, 16), (-17, 0, 37)), -4)
    s, sc = fit(fn, 24, 22, (18, 30, 302, 170), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-70, -50, 46), (-30, -50, 46))
    for p in ((60, -40, 0), (130, -40, 0)):
        x, y = cam.xy(p)
        s += drop3(x, y + 4, .9)
    g = cam.xy((-118, -44, 76))
    pm = cam.xy((-118, -60, -2))
    bp = cam.xy((40, 22, 76))
    lk = cam.xy((100, -40, 0))
    a = cam.xy((-50, -50, 46))
    s += lab(g[0], g[1] - 18, "圧力計") + lab(pm[0], pm[1] + 18, "加圧ポンプ")
    s += al(a[0] - 4, a[1] - 14, "水圧") + lab(lk[0] + 10, lk[1] + 24, "漏れ確認")
    s += lab(bp[0], bp[1] - 12, "閉止板")
    return s


# =====================================================================================
# q:epoxycast — resin mixed and degassed under vacuum, cast into a heated mould (APG: pressed in)
# =====================================================================================
@picto("epoxycast")
def _():
    def fn(sc):
        # vacuum mixer on legs
        for a in (200, 320, 80):
            c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
            CYL(sc, (-130 + 26 * c, 26 * s_, -40), (0, 0, 1), 3.5, 30, "m", seg=10, bands=4)
        CYL(sc, (-130, 0, -16), (0, 0, 1), 12, 6, "m", seg=20, r1=34, bands=6)               # cone bottom
        CYL(sc, (-130, 0, -10), (0, 0, 1), 34, 70, "pt", seg=28, dark=1, bands=10)
        CYL(sc, (-130, 0, 60), (0, 0, 1), 34, 12, "pt", seg=28, r1=22, bands=8)
        CYL(sc, (-130, 0, 72), (0, 0, 1), 11, 22, "dk", seg=16, bands=6)                     # stirrer motor

        def win(s_):
            cam = s_.cam
            C = (-130 + 34 * math.cos(math.radians(250)), 34 * math.sin(math.radians(250)), 30)
            o = path(P(circ3(cam, C, (math.cos(math.radians(250)), math.sin(math.radians(250)), 0), 10, 20)), "m")
            o += path(P(circ3(cam, C, (math.cos(math.radians(250)), math.sin(math.radians(250)), 0), 7.5, 20)), "resin")
            for k, (dx, dz) in enumerate(((-3, -2), (2, 2), (0, 4), (4, -3))):
                p = cam.xy((C[0] + dx, C[1] - .5, C[2] + dz))
                o += circ(p[0], p[1], .9 + .3 * (k % 2), "fdot")
            return o
        RAW(sc, win, ((-148, -34, 18), (-130, -30, 42)), -3)
        # heated two-part mould: lower half with the cast insulator, upper half lifted by the press
        BOX(sc, -40, -44, -40, 160, 88, 44, "m", dark=1)
        BOX(sc, -40, -44, 66, 160, 88, 34, "m", dark=1)
        CYL(sc, (40, 0, 100), (0, 0, 1), 16, 26, "dk", seg=20, bands=8)

        def heaters(s_):
            cam = s_.cam
            o = ""
            for x in (-20, 20, 60, 100):
                o += hole3(cam, (x, -44.2, -18), (0, -1, 0), 3.2, "h") + hole3(cam, (x, -44.2, 83), (0, -1, 0), 3.2, "h")
            return o
        RAW(sc, heaters, ((-40, -44.4, -24), (120, -44.2, 88)), -3)
        # post insulator: metal inserts at both ends, epoxy body with sheds
        x = -26
        CYL(sc, (x, 0, 22), (1, 0, 0), 12, 16, "m", seg=16, bands=6)
        x += 16
        for k in range(3):
            CYL(sc, (x, 0, 22), (1, 0, 0), 11, 13, "gw", seg=16, bands=6)
            CYL(sc, (x + 13, 0, 22), (1, 0, 0), 20, 12, "gw", seg=22, bands=8)
            x += 25
        CYL(sc, (x, 0, 22), (1, 0, 0), 11, 13, "gw", seg=16, bands=6)
        CYL(sc, (x + 13, 0, 22), (1, 0, 0), 12, 16, "m", seg=16, bands=6)

        def pipe(s_):
            cam = s_.cam
            return cable(cam, [(-130, 0, -16), (-130, 0, -30)] + bez((-130, 0, -30), (-130, 0, -56), (-60, -20, -56), (-40, -20, -30), 8)[1:], "rail")
        RAW(sc, pipe, ((-132, -22, -56), (-40, 2, -16)), 2)
    s, sc = fit(fn, 20, 20, (16, 28, 304, 170), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (40, 0, 150), (40, 0, 130))
    s += arc3(cam, (-130, 0, 96), (0, 0, 1), 18, 200, 330)
    s += arrow3(cam, (-100, -24, -58), (-62, -22, -58))
    p = cam.xy((40, 0, 140))
    t = cam.xy((-130, -34, -40))
    m = cam.xy((70, -44, -40))
    w = cam.xy((120, 0, 40))
    s += al(p[0] + 8, p[1] + 4, "加圧", "start") + lab(t[0], t[1] + 18, "真空混合")
    s += lab(m[0], m[1] + 18, "加熱金型") + lab(w[0] + 4, w[1] + 4, "絶縁物", "start")
    return s


# =====================================================================================
# q:coilspread — wound loop gripped at its two straight legs and spread into a diamond coil;
# the end heads hold the noses and move in as the legs move apart
# =====================================================================================
@picto("coilspread")
def _():
    xl, xn, W, Hc = 58, 104, 34, 44
    A0, A1 = (-xl, -W, 0), (xl, -W, 0)                 # lower (front) leg
    B0, B1 = (-xl, W, Hc), (xl, W, Hc)                 # upper (back) leg
    N0, N1 = (-xn, 0, Hc / 2), (xn, 0, Hc / 2)          # noses
    segs = [(A0, A1, (0, 0, 1)), (B0, B1, (0, 0, 1)), (A0, N0, (0, 0, 1)), (B0, N0, (0, 0, 1)),
            (A1, N1, (0, 0, 1)), (B1, N1, (0, 0, 1))]

    def ext(p, q, e):
        d = [q[i] - p[i] for i in range(3)]
        L = math.sqrt(sum(c * c for c in d))
        return tuple(p[i] - d[i] / L * e for i in range(3)), tuple(q[i] + d[i] / L * e for i in range(3))

    def fn(sc):
        BOX(sc, -150, -70, -66, 300, 140, 16, "pt", dark=1)                          # bed
        for p, q, sd in segs:
            p2, q2 = ext(p, q, 4)

            def f(s_, p2=p2, q2=q2, sd=sd):
                return bar(s_.cam, p2, q2, 8, 18, "cu", side=sd)
            lo = tuple(min(p2[i], q2[i]) - 9 for i in range(3))
            hi = tuple(max(p2[i], q2[i]) + 9 for i in range(3))
            RAW(sc, f, (lo, hi))
        # leg clamps: lower pair fixed on posts, upper pair on the spreading carriage
        for x in (-30, 22):
            BOX(sc, x, -W - 8, -26, 8 + 0, 16, 16, "dk")
            BOX(sc, x, -W - 8, -50, 8, 16, 24, "m")
            BOX(sc, x, W - 8, Hc + 10, 8, 16, 14, "dk")
        BOX(sc, -44, W - 10, Hc + 24, 88, 20, 14, "pt", ch=2)                         # carriage beam
        BOX(sc, -8, W + 10, -50, 16, 14, Hc + 88, "pt", dark=1)                       # carriage column
        # end heads with nose pins
        for x, d in ((-xn, -1), (xn, 1)):
            BOX(sc, x + (0 if d > 0 else -22) + 4 * d, -14, -50, 22, 28, 50 + Hc / 2 - 12, "m")
            CYL(sc, (x + 6 * d, 0, Hc / 2 - 12), (0, 0, 1), 5, 24, "t", seg=14)
    s, sc = fit(fn, -20, 26, (20, 34, 300, 172), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, W, Hc + 40), (0, W + 30, Hc + 64))
    s += arrow3(cam, (-xn - 50, 0, Hc / 2 + 20), (-xn - 24, 0, Hc / 2 + 20))
    s += arrow3(cam, (xn + 50, 0, Hc / 2 + 20), (xn + 24, 0, Hc / 2 + 20))
    a = cam.xy((0, W + 30, Hc + 64))
    nz = cam.xy((xn, 0, -50))
    lg = cam.xy((-4, -W - 8, -50))
    c = cam.xy((-xl, W, Hc + 38))
    s += al(a[0] + 8, a[1] + 6, "広げる", "start") + lab(nz[0] + 6, nz[1] + 22, "ノーズ")
    s += lab(lg[0], lg[1] + 30, "直線部") + lab(c[0] - 12, c[1] - 4, "銅コイル", "end")
    return s


# =====================================================================================
# q:lasertrack — tracker head turns in azimuth & elevation to follow a reflector; distance + 2 angles = XYZ
# =====================================================================================
@picto("lasertrack")
def _():
    hz = 0                                         # elevation axis height
    smr = (210, 16, -54)

    def fn(sc):
        # tripod
        top = (0, 0, -40)
        for a in (100, 220, 340):
            ft = (34 * math.cos(math.radians(a)), 34 * math.sin(math.radians(a)), -130)
            d = tuple(ft[i] - top[i] for i in range(3))
            L = math.sqrt(sum(c * c for c in d))
            CYL(sc, top, d, 2.6, L, "m", seg=10, bands=4)
        CYL(sc, (0, 0, -48), (0, 0, 1), 9, 10, "dk", seg=16)
        CYL(sc, (0, 0, -38), (0, 0, 1), 18, 12, "dk", seg=28)                 # azimuth base
        BOX(sc, -12, -18, -26, 24, 36, 6, "pt")                               # yoke
        for y in (-18, 12):
            BOX(sc, -10, y, -20, 20, 6, 32, "pt", ch=2)
        CYL(sc, (0, -12, hz), (0, 1, 0), 11, 24, "m", seg=24)                  # tracking head
        # workpiece: long welded bedplate with bearing saddles
        BOX(sc, 70, -40, -130, 210, 96, 60, "w", ch=3)
        for x in (110, 170, 230):
            BOX(sc, x, -40, -70, 18, 96, 10, "w")

        def bores(s_):
            o = ""
            for x in (110, 170, 230):
                o += hole3(s_.cam, (x + 9, -40.2, -70), (0, -1, 0), 7, "bg")
            return o
        RAW(sc, bores, ((110, -40.4, -77), (248, -40.2, -63)), -2)
        CYL(sc, (smr[0], smr[1], -70), (0, 0, 1), 6, 9, "m", seg=16)           # nest

        def ball(s_):
            x, y = s_.cam.xy(smr)
            r = 7 * s_.cam.s
            return circ(x, y, r, "ms2") + circ(x - r * .3, y - r * .3, r * .45, "ms1") + circ(x, y, r * .3, "d")
        RAW(sc, ball, ((smr[0] - 7, smr[1] - 7, -61), (smr[0] + 7, smr[1] + 7, -47)), -1)
    s, sc = fit(fn, -24, 18, (24, 32, 300, 170), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((11, 0, hz)), cam.xy(smr)
    s += line(a[0], a[1], b[0], b[1], "laserl")
    s += arc3(cam, (0, 0, -32), (0, 0, 1), 30, -40, 70)
    s += arc3(cam, (0, -14, hz), (0, 1, 0), 24, 100, 190)
    h = cam.xy((-24, 0, 20))
    z = cam.xy((30, 0, -40))
    m = cam.xy(((smr[0] + 11) / 2, 0, (hz + smr[2]) / 2))
    s += al(h[0] - 4, h[1] - 6, "垂直角", "end") + al(z[0] - 50, z[1] + 4, "水平角", "end")
    s += al(m[0] + 6, m[1] - 10, "距離", "start") + lab(b[0] + 10, b[1] - 12, "反射球", "start")
    return s


# =====================================================================================
# q:autofrettage — ultra-high pressure from an intensifier yields the bore: compressive residual stress
# =====================================================================================
@picto("autofrettage")
def _():
    R, rb, L = 36, 10, 130

    def fn(sc):
        CYL(sc, (0, 0, 0), (1, 0, 0), R, L, "w", seg=40, holes=[GE.circle_outline(rb, 24, 24)], cap_mat="w2")
        for x in (34, 82):
            CYL(sc, (x, 0, R - 3), (0, 0, 1), 10, 14, "w", seg=20)              # outlet bosses
        CYL(sc, (L, 0, 0), (1, 0, 0), 16, 14, "m", seg=24)                     # pressure plug / adapter
        # intensifier pump
        BOX(sc, 150, 50, -60, 110, 70, 50, "pt", dark=1, ch=3)
        CYL(sc, (176, 85, -10), (1, 0, 0), 20, 50, "dk", seg=28)              # low-pressure (large) cylinder
        CYL(sc, (226, 85, -10), (1, 0, 0), 9, 30, "m", seg=20)                # high-pressure (small) plunger

        def face(s_):
            cam = s_.cam
            o = path(P(circ3(cam, (-.2, 0, 0), (-1, 0, 0), rb, 24)), "fl")
            o += path(P(circ3(cam, (-.2, 0, 0), (-1, 0, 0), rb * 2.1, 32)), "mfring")
            return o
        RAW(sc, face, ((-.4, -R, -R), (-.2, R, R)), -4)

        def line_(s_):
            cam = s_.cam
            return cable(cam, bez((L + 14, 0, 0), (L + 50, 0, 0), (250, 60, -10), (256, 85, -10)), "pres")
        RAW(sc, line_, ((L + 14, 0, -12), (256, 85, 0)), 5)
    s, sc = fit(fn, 24, 18, (22, 34, 300, 168), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    for k in range(4):
        a = math.radians(45 + 90 * k)
        c, s_ = math.cos(a), math.sin(a)
        s += arrow3(cam, (-.4, rb * .55 * c, rb * .55 * s_), (-.4, rb * 2.0 * c, rb * 2.0 * s_))
    f = cam.xy((0, -R, R))
    p = cam.xy((205, 50, -60))
    hp = cam.xy((L + 40, 0, 0))
    z = cam.xy((0, -R, -R))
    s += al(hp[0] + 10, hp[1] + 18, "超高圧", "start") + lab(p[0], p[1] + 18, "増圧ポンプ")
    s += lab(z[0] - 2, z[1] + 20, "圧縮残留応力", "start")
    return s
