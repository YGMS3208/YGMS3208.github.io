"""v3 principle drawings (shaded 3D style), group qd2: resin/rubber/glass forming (second half)
and assembly / handling equipment. Overrides the older flat drawings with the same keys."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def poly3(cam, pts, c):
    return path(P([cam.xy(p) for p in pts]), c)


def stadium(p0, r0, p1, r1, seg=10):
    """convex outline around two circles (x, z) -> points"""
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    return arc(p0[0], p0[1], r0, a + 90, a + 270, seg) + arc(p1[0], p1[1], r1, a - 90, a + 90, seg)


def YL(sc, y0, th, pts_xz, mat="pt", bias=0.0, **kw):
    """convex outline in the x-z plane extruded along +y from y0 (robot links, frames seen side-on)."""
    loop = banded(hull([(-x, z) for x, z in pts_xz]), 2)
    xs, zs = [p[0] for p in pts_xz], [p[1] for p in pts_xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, th, mat, smooth=True, **kw)),
           ((min(xs), y0, min(zs)), (max(xs), y0 + th, max(zs))), bias)


def TCYL(sc, O, A, r, h, mat="t", bias=0.0, seg=28, **kw):
    """cylinder on a tilted axis (bbox from both end discs)."""
    a = GE._norm(A)
    E1, E2, _ = GE.frame(a)
    pts = []
    for t in (0, h):
        for k in range(8):
            c, s_ = math.cos(k * PI / 4) * r, math.sin(k * PI / 4) * r
            pts.append(tuple(O[i] + a[i] * t + c * E1[i] + s_ * E2[i] for i in range(3)))
    bb = (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))
    sc.add(compact(GE.prism(sc.cam, O, a, GE.circle_outline(r, seg, 8), h, mat, smooth=True, **kw)), bb, bias)


PI = math.pi


def hexo(r, rot=30):
    return [(r * math.cos(math.radians(rot + 60 * k)), r * math.sin(math.radians(rot + 60 * k)), k) for k in range(6)]


def mini_chart(x, y, w, h, pts_, lbl=None):
    """small instrument display: frame, axes and one curve (pts_ in 0..1)."""
    s = rect(x, y, w, h, "m", 3)
    s += line(x + 6, y + h - 6, x + w - 6, y + h - 6, "o thin") + line(x + 6, y + 5, x + 6, y + h - 6, "o thin")
    s += pline([(x + 7 + (w - 14) * u, y + h - 7 - (h - 13) * v) for u, v in pts_], "a")
    return s


# =====================================================================================
# q:robot — 6-axis articulated robot: base (J1 swivel), lower arm (J2), upper arm (J3), wrist (J4-J6)
# and a gripper that carries a part onto a table
# =====================================================================================
@picto("robot")
def _():
    J2, J3, W = (0, 96), (34, 226), (196, 226)

    def fn(sc):
        BOX(sc, -52, -52, 0, 104, 104, 10, "dk", ch=8)                              # base plate
        CYL(sc, (0, 0, 10), (0, 0, 1), 40, 34, "pt", seg=36, dark=1)                 # J1 base
        CYL(sc, (0, 0, 44), (0, 0, 1), 36, 16, "m", seg=36)                          # J1 swivel ring
        YL(sc, -26, 52, stadium((0, 60), 34, J2, 30), "pt")                         # turret / shoulder
        CYL(sc, (J2[0], 26, J2[1]), (0, 1, 0), 20, 20, "dk", seg=24)                 # J2 motor (back)
        YL(sc, -44, 18, stadium(J2, 27, J3, 21), "pt", -1)                           # lower arm (near side)
        CYL(sc, (J2[0], -50, J2[1]), (0, 1, 0), 15, 6, "m", seg=24, bias=-2)         # J2 cap
        YL(sc, -24, 48, stadium((J3[0] - 6, J3[1]), 26, (J3[0] + 30, J3[1] + 4), 24), "pt")   # J3 housing
        CYL(sc, (J3[0] + 56, 0, J3[1] + 2), (1, 0, 0), 19, W[0] - J3[0] - 70, "pt", seg=28, r1=15)  # upper arm (J4 roll)
        CYL(sc, (W[0] - 14, 0, W[1] + 2), (1, 0, 0), 15, 6, "m", seg=24)            # J4 joint ring
        YL(sc, -16, 32, stadium((W[0] - 8, W[1] + 2), 15, (W[0] + 8, W[1] - 14), 13), "pt")   # wrist (J5)
        CYL(sc, (W[0] + 8, 0, W[1] - 40), (0, 0, 1), 11, 16, "dk", seg=24)           # J6 flange
        BOX(sc, W[0] - 12, -16, W[1] - 54, 40, 32, 14, "m")                          # gripper body
        for y in (-16, 10):
            BOX(sc, W[0] - 6, y, W[1] - 82, 28, 6, 28, "t")                          # fingers
        BOX(sc, W[0] - 14, -10, W[1] - 86, 44, 20, 34, "w", ch=3)                    # carried part
        BOX(sc, 150, -56, 0, 120, 112, 50, "m", dark=1)                              # table
        BOX(sc, 168, -22, 50, 44, 20, 34, "w", ch=3, bias=-1)                        # placed part
    s, sc = fit(fn, -30, 18, (30, 18, 292, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 30), (0, 0, 1), 60, -70, 40)
    s += arc3(cam, (J3[0], -50, J3[1]), (0, -1, 0), 40, 100, 30)
    s += arrow3(cam, (W[0] + 44, 0, W[1] - 60), (W[0] + 44, 0, W[1] - 120))
    a = cam.xy((0, -60, 30))
    b = cam.xy((J3[0], -50, J3[1] + 40))
    c = cam.xy((W[0] + 44, 0, W[1] - 90))
    h = cam.xy((W[0] + 30, 0, W[1] - 40))
    s += al(a[0] - 8, a[1] + 22, "旋回") + al(b[0] - 6, b[1] - 8, "関節")
    s += al(c[0] + 8, c[1] + 4, "搭載", "start") + lab(h[0] + 12, h[1] - 4, "ハンド", "start")
    return s


# =====================================================================================
# q:nutrunner — spindle with a socket on the bolt head: it turns the bolt to a set torque and angle
# and records the curve; a second, already tightened bolt shows the head the socket hides
# =====================================================================================
@picto("nutrunner")
def _():
    zp = 28                                    # joint top (two plates)
    xb = 0

    def fn(sc):
        BOX(sc, -100, -50, 0, 160, 100, 14, "w", dark=1, ch=4)                     # lower part (flange)
        BOX(sc, -90, -40, 14, 140, 80, 14, "w", ch=4)                              # upper part (bracket)
        for x in (-56, xb):
            CYL(sc, (x, 0, zp), (0, 0, 1), 17, 3, "m", seg=28)                     # washer face
            Z(sc, zp + 3, 11, [(p[0] + x, p[1], p[2]) for p in hexo(14)], "w")     # hex head
        CYL(sc, (xb, 0, zp + 8), (0, 0, 1), 19, 26, "t", seg=32)                    # socket on the head
        CYL(sc, (xb, 0, zp + 34), (0, 0, 1), 10, 18, "m", seg=24)                   # socket adaptor / extension
        CYL(sc, (xb, 0, zp + 52), (0, 0, 1), 24, 16, "dk", seg=32)                  # spindle nose (torque sensor)
        CYL(sc, (xb, 0, zp + 68), (0, 0, 1), 27, 50, "pt", seg=32, dark=1)         # gear unit + motor
    s, sc = fit(fn, -26, 26, (30, 16, 214, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (xb, 0, zp + 22), (0, 0, 1), 32, -70, 60)
    s += mini_chart(222, 58, 86, 60, [(0, 0), (.15, .04), (.35, .18), (.75, .78), (.92, .82), (1, .82)])
    a = cam.xy((xb + 32, 0, zp + 22))
    b = cam.xy((-56, -14, zp))
    s += al(a[0] + 6, a[1] + 4, "回転", "start")
    s += lab(cam.xy((xb + 27, 0, zp + 60))[0] + 8, cam.xy((xb, 0, zp + 60))[1] + 4, "ソケット", "start")
    s += lab(b[0] - 30, b[1] + 46, "ボルト", "middle")
    s += lab(265, 136, "トルク・角度")
    return s


# =====================================================================================
# q:pressfit — servo press: ram + load cell push a seat ring into the bore of the part;
# load vs. stroke is monitored for OK/NG
# =====================================================================================
@picto("pressfit")
def _():
    zt = 50

    def fn(sc):
        BOX(sc, -80, -54, 0, 160, 108, zt, "w", ch=6)                             # part (head casting)
        RAW(sc, lambda s_: hole3(s_.cam, (0, 0, zt + .1), (0, 0, 1), 23, "w3") + hole3(s_.cam, (0, 0, zt + .1), (0, 0, 1), 19, "bg")
            + hole3(s_.cam, (-52, 0, zt + .1), (0, 0, 1), 16, "w3") + hole3(s_.cam, (52, 0, zt + .1), (0, 0, 1), 16, "w3"),
            ((-70, -24, zt), (70, 24, zt + .2)), -1)
        RING(sc, (0, 0, zt), (0, 0, 1), 21, 14, 11, "gw", seg=36)                  # seat ring entering the bore
        CYL(sc, (0, 0, zt + 11), (0, 0, 1), 14, 12, "t", seg=24)                    # pilot / punch tip
        CYL(sc, (0, 0, zt + 23), (0, 0, 1), 22, 20, "t", seg=32)                    # punch
        CYL(sc, (0, 0, zt + 43), (0, 0, 1), 24, 14, "dk", seg=32)                   # load cell
        CYL(sc, (0, 0, zt + 57), (0, 0, 1), 18, 70, "m", seg=28)                    # ram
    s, sc = fit(fn, -28, 26, (30, 14, 210, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((40, -30, zt + 110)), cam.xy((40, -30, zt + 62))
    s += arrow(a[0], a[1], b[0], b[1])
    s += mini_chart(222, 50, 86, 60, [(0, 0), (.2, .06), (.3, .42), (.8, .58), (.9, .62), (.92, 1)])
    s += al(a[0] + 8, (a[1] + b[1]) / 2 + 4, "圧入", "start")
    c = cam.xy((-24, 0, zt + 50))
    s += lab(c[0] - 8, c[1] + 4, "ロードセル", "end")
    d = cam.xy((-22, 0, zt + 8))
    s += lab(d[0] - 16, d[1] + 4, "シート", "end")
    s += lab(265, 128, "荷重−変位")
    return s


# =====================================================================================
# q:caulk — orbital (wobble) riveting: a punch tilted a few degrees orbits around the shaft end,
# spreading it into a head that locks the part
# =====================================================================================
@picto("caulk")
def _():
    zt, tilt = 40, math.radians(10)
    A = (math.sin(tilt), 0, math.cos(tilt))

    def fn(sc):
        BOX(sc, -86, -50, -20, 172, 100, 20, "m", dark=1, ch=4)                     # fixture
        BOX(sc, -76, -40, 0, 152, 80, 16, "w", ch=6)                               # plate (arm)
        CYL(sc, (0, 0, 16), (0, 0, 1), 30, zt - 16, "w", seg=40, dark=1)            # boss / housing
        CYL(sc, (0, 0, zt), (0, 0, 1), 13, 6, "w", seg=32)                           # shaft end
        CYL(sc, (0, 0, zt + 6), (0, 0, 1), 15, 7, "w", seg=32, r1=21)                # head being spread
        base = (0, 0, zt + 15.5)
        TCYL(sc, base, A, 17, 16, "t", -1)                                           # punch (tilted)
        TCYL(sc, (A[0] * 16, 0, base[2] + 16 * A[2]), A, 26, 56, "pt", -1, dark=1)  # spindle head (tilted)
    s, sc = fit(fn, -28, 24, (30, 16, 290, 180), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, zt + 46), (0, 0, 1), 52, -40, 80)
    a, b = cam.xy((-80, 0, zt + 110)), cam.xy((-80, 0, zt + 60))
    s += arrow(a[0], a[1], b[0], b[1])
    s += al(a[0] - 6, (a[1] + b[1]) / 2 + 4, "加圧", "end")
    c = cam.xy((52, 0, zt + 46))
    s += al(c[0] + 10, c[1] + 12, "揺動", "start")
    d = cam.xy((21, -10, zt + 10))
    s += lab(d[0] + 40, d[1] + 22, "かしめ部", "start")
    return s


# =====================================================================================
# q:conveyor — floor slat conveyor: steel slats on a chain driven by an end sprocket carry the body
# at line speed so workers ride along with it
# =====================================================================================
@picto("conveyor")
def _():
    from il3_engine import car
    x0, x1, wy = -90, 560, 118

    def fn(sc):
        BOX(sc, x0, -wy, -10, x1 - x0, 2 * wy, 10, "m")                           # slat deck
        for y in (-wy - 12, wy):
            BOX(sc, x0 + 10, y, -40, x1 - x0 - 20, 12, 36, "dk")                    # side frames
        CYL(sc, (x0 + 24, -wy - 12, -26), (0, -1, 0), 28, 8, "m", seg=28, dark=1)  # head sprocket

        def seams(s_):
            d = "".join(P([s_.cam.xy((x, -wy, .1)), s_.cam.xy((x, wy, .1))], False) for x in range(x0 + 26, x1, 26))
            d += "".join(P([s_.cam.xy((x, -wy - .1, -10)), s_.cam.xy((x, -wy - .1, 0))], False) for x in range(x0 + 26, x1, 26))
            o = path(d, "gr")
            for k in range(10):
                a = 2 * PI * k / 10
                o += hole3(s_.cam, (x0 + 24 + 20 * math.cos(a), -wy - 20.1, -26 + 20 * math.sin(a)), (0, -1, 0), 2.6, "dk", 8)
            return o
        RAW(sc, seams, ((x0, -wy - 21, -10), (x1, wy, .2)), -3)
        cam = sc.cam
        dx, dy = cam.xy((50, 0, 0)), cam.xy((0, 0, 0))
        cam.ox += dx[0] - dy[0]
        cam.oy += dx[1] - dy[1]
        back, body, front = car(cam, "pt")
        cam.ox -= dx[0] - dy[0]
        cam.oy -= dx[1] - dy[1]
        return back + body + front
    s, sc = fit(fn, 28, 22, (22, 20, 298, 174), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (150, -wy - 40, -20), (380, -wy - 40, -20))
    a = cam.xy((265, -wy - 40, -20))
    s += al(a[0] + 6, a[1] + 18, "同期送り")
    b = cam.xy((x0, -wy, -10))
    s += lab(b[0] + 8, b[1] + 26, "スラット", "start")
    c = cam.xy((300, 0, 150))
    s += lab(c[0], c[1] - 10, "車体")
    return s


# =====================================================================================
# q:agv — low automated guided vehicle under a pallet load, following the guide tape on the floor
# =====================================================================================
@picto("agv")
def _():
    def fn(sc):
        RAW(sc, lambda s_: poly3(s_.cam, [(-210, -6, 0), (330, -6, 0), (330, 6, 0), (-210, 6, 0)], "ins")
            + path("".join(P([s_.cam.xy((x, -6, 0)), s_.cam.xy((x + 5, 6, 0))], False) for x in range(-200, 330, 18)), "gr"),
            ((-210, -6, -1), (330, 6, 0)), 60)
        for x in (-60, 60):
            for y in (-40, 40):
                CYL(sc, (x, y, 0), (0, 0, 1), 7, 6, "dk", seg=16)                  # casters
        BOX(sc, -86, -52, 6, 172, 104, 28, "pt", ch=10)                    # chassis
        CYL(sc, (0, -52, 15), (0, -1, 0), 15, 6, "dk", seg=24)                      # drive wheel (near)
        BOX(sc, 86, -46, 10, 6, 92, 16, "dk")                                        # bumper (front)
        CYL(sc, (68, -36, 34), (0, 0, 1), 8, 9, "dk", seg=20)                        # laser scanner
        CYL(sc, (-20, 0, 34), (0, 0, 1), 26, 6, "m", seg=28)                         # lift table
        BOX(sc, -96, -60, 40, 192, 120, 12, "m", dark=1)                             # pallet
        BOX(sc, -80, -50, 52, 160, 100, 34, "w", ch=3)                               # parts box
    s, sc = fit(fn, -30, 24, (24, 22, 296, 172), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (140, 0, 0), (250, 0, 0))
    a = cam.xy((200, 0, 0))
    s += al(a[0] - 2, a[1] - 12, "走行")
    b = cam.xy((-210, -6, 0))
    s += lab(b[0] + 2, b[1] - 12, "誘導テープ", "start")
    c = cam.xy((40, -52, 6))
    s += lab(c[0] + 4, c[1] + 22, "無人搬送車", "middle")
    d = cam.xy((-46, 0, 86))
    s += lab(d[0] - 10, d[1] - 18, "搬送物", "middle")
    return s


# =====================================================================================
# q:crimp — crimp applicator: the crimper comes down on the open barrel of the terminal and folds it
# around the stripped wire end on the anvil (top-left kept clear: q:crimpmon puts a chart there)
# =====================================================================================
@picto("crimp")
def _():
    def fn(sc):
        CYL(sc, (-170, 0, 0), (1, 0, 0), 7.5, 152, "dk", seg=20)                    # insulated wire
        CYL(sc, (-18, 0, 0), (1, 0, 0), 4.6, 32, "cu", seg=16)                      # stripped conductor
        BOX(sc, -12, -26, -50, 34, 52, 40, "dk", ch=3)                             # anvil
        X(sc, -10, 30, [(-8, -10), (8, -10), (8, -7), (-8, -7)], "cu", -1)          # barrel floor
        for y in (-8, 6):
            X(sc, -10, 30, [(y, -7), (y + 2, -7), (y + 2, 9), (y, 9)], "cu", -1)    # open barrel walls
        BOX(sc, 20, -8, -10, 46, 16, 16, "cu", ch=1)                               # box contact
        BOX(sc, -12, -20, 22, 34, 40, 36, "t", ch=3)                               # crimper
        BOX(sc, -34, -34, 58, 78, 68, 54, "pt", dark=1, ch=6)                       # ram
    s, sc = fit(fn, 28, 20, (34, 40, 300, 178), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((70, -30, 100)), cam.xy((70, -30, 40))
    s += arrow(a[0], a[1], b[0], b[1])
    s += al(a[0] + 8, (a[1] + b[1]) / 2 + 4, "圧着", "start")
    c = cam.xy((44, -8, -10))
    s += lab(c[0] + 6, c[1] + 22, "端子", "start")
    d = cam.xy((-130, 0, -8))
    s += lab(d[0], d[1] + 22, "電線")
    return s


# =====================================================================================
# q:mass — mass-centring machine: the forged crankshaft spins on roller supports, the unbalance gives
# its mass axis, and centre holes are drilled on that axis (not the geometric one)
# =====================================================================================
@picto("mass")
def _():
    rj, rp, e = 15, 13, 30
    xs = [0, 92, 184]                          # journals (x start), length 22

    def web(phi):
        py, pz = e * math.cos(math.radians(phi)), e * math.sin(math.radians(phi))
        return banded(hull(arc(py, pz, 18, phi - 90, phi + 90, 4) + arc(0, 0, 40, phi + 180 - 60, phi + 180 + 60, 6)), 2)

    def fn(sc):
        CYL(sc, (-30, 0, 0), (1, 0, 0), 10, 30, "w", seg=24, dark=1)               # front nose
        for i, x in enumerate(xs):
            CYL(sc, (x, 0, 0), (1, 0, 0), rj, 22, "w", seg=20, bands=8)
            if i < 2:
                for j, phi in enumerate((90, 270)):
                    xw = x + 22 + j * 46
                    X(sc, xw, 12, web(phi), "w", smooth=True, dark=1, cap_mat="w3")
                    py, pz = e * math.cos(math.radians(phi)), e * math.sin(math.radians(phi))
                    sc.add(compact(GE.prism(sc.cam, (xw + 12, py, pz), (1, 0, 0), GE.circle_outline(rp, 18, 6), 22, "w", smooth=True)),
                           ((xw + 12, py - rp, pz - rp), (xw + 34, py + rp, pz + rp)))
        CYL(sc, (206, 0, 0), (1, 0, 0), 30, 14, "w", seg=24, dark=1)                # flange
        for x in (0, 184):
            for y in (-20, 20):
                CYL(sc, (x - 2, y, -rj - 9), (1, 0, 0), 9, 26, "m", seg=12, bands=6, bias=1)  # support rollers
            BOX(sc, x - 4, -34, -78, 30, 68, 45, "dk", bias=1)                       # roller stands
        CYL(sc, (-74, 0, 3), (1, 0, 0), 3, 26, "t", seg=12)                          # centre drill
        CYL(sc, (-110, 0, 3), (1, 0, 0), 12, 36, "m", seg=24)                        # drill spindle
    s, sc = fit(fn, 24, 18, (26, 24, 296, 172), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((-130, 0, 3)), cam.xy((240, 0, 3))
    s += path(P([a, b], False), "o cutl")
    s += arc3(cam, (110, 0, 0), (1, 0, 0), 56, 150, 250)
    c = cam.xy((-92, 0, 15))
    s += lab(c[0], c[1] - 14, "センタ穴")
    s += al(a[0] + 2, a[1] + 20, "質量中心軸", "start")
    d = cam.xy((110, 0, 56))
    s += al(d[0] + 4, d[1] - 10, "回転")
    return s


# =====================================================================================
# q:assy — dedicated assembly machine (piston insertion): the piston with rings is pushed through a
# tapered ring-compressor guide into the cylinder bore of the block
# =====================================================================================
@picto("assy")
def _():
    zt, xs = 60, (-75, -25, 25, 75)

    def fn(sc):
        BOX(sc, -110, -46, 0, 220, 92, zt, "w", ch=6)                             # cylinder block
        def bores(s_):
            o = ""
            for i, x in enumerate(xs):
                if i != 0:
                    o += hole3(s_.cam, (x, 0, zt + .1), (0, 0, 1), 20, "w3") + hole3(s_.cam, (x, 0, zt + .1), (0, 0, 1), 18, "bg")
            return o
        RAW(sc, bores, ((-100, -20, zt), (100, 20, zt + .2)), -1)
        x = xs[0]
        CYL(sc, (x, 0, zt), (0, 0, 1), 25, 22, "t", seg=32, r1=20)                  # ring-compressor guide (taper)
        CYL(sc, (x, 0, zt + 22), (0, 0, 1), 19, 8, "w", seg=28, dark=2)             # ring belt (grooves)
        CYL(sc, (x, 0, zt + 30), (0, 0, 1), 19, 6, "w", seg=28)
        CYL(sc, (x, 0, zt + 36), (0, 0, 1), 19, 4, "w", seg=28, dark=2)
        CYL(sc, (x, 0, zt + 40), (0, 0, 1), 19, 6, "w", seg=28)                     # crown
        CYL(sc, (x, 0, zt + 46), (0, 0, 1), 9, 46, "m", seg=20)                     # pusher
        BOX(sc, x - 34, -26, zt + 92, 68, 52, 26, "pt", dark=1, ch=4)               # head
    s, sc = fit(fn, -28, 24, (34, 16, 286, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((xs[0] + 50, 0, zt + 110)), cam.xy((xs[0] + 50, 0, zt + 50))
    s += arrow(a[0], a[1], b[0], b[1])
    s += al(a[0] + 8, (a[1] + b[1]) / 2, "挿入", "start")
    c = cam.xy((xs[0] - 19, -10, zt + 36))
    s += lab(c[0] - 8, c[1] + 4, "ピストン", "end")
    d = cam.xy((xs[0] - 25, -10, zt + 8))
    s += lab(d[0] - 8, d[1] + 6, "ガイド", "end")
    f = cam.xy((110, -46, 0))
    s += lab(f[0] - 30, f[1] + 18, "シリンダブロック", "middle")
    return s


# =====================================================================================
# q:fill — fluid filling: the filling head seals on the filler neck, evacuates the circuit,
# then meters coolant / brake fluid / refrigerant in from the filling unit
# =====================================================================================
@picto("fill")
def _():
    def fn(sc):
        BOX(sc, -180, -40, 0, 70, 80, 130, "pt", dark=1, ch=5)                     # filling unit
        BOX(sc, -170, -40.5, 92, 34, 1, 22, "dk", bias=-1)                         # display
        BOX(sc, 20, -40, 0, 120, 80, 70, "w", ch=8)                                # reservoir tank
        RAW(sc, lambda s_: poly3(s_.cam, [(28, -40.2, 6), (132, -40.2, 6), (132, -40.2, 42), (28, -40.2, 42)], "fl"),
            ((28, -40.3, 6), (132, -40.2, 42)), -1)
        CYL(sc, (60, 0, 70), (0, 0, 1), 15, 14, "w", seg=28)                        # filler neck
        CYL(sc, (60, 0, 84), (0, 0, 1), 22, 24, "t", seg=32)                        # filling head (seal)
        CYL(sc, (60, 0, 108), (0, 0, 1), 13, 16, "m", seg=24)                       # valve block

        def hoses(s_):
            o = ""
            for dz in (0, 18):
                pts_ = [(60, 0, 124 + dz * .2), (60, 0, 150 + dz), (-20, 0, 160 + dz), (-80, 0, 130 + dz * .3), (-110, 0, 100 + dz * .5)]
                o += '<path class="cable" d="%s"/>' % P([s_.cam.xy(p) for p in pts_], False)
            return o
        RAW(sc, hoses, ((-110, -2, 100), (60, 2, 180)), -2)
    s, sc = fit(fn, -26, 22, (30, 26, 290, 172), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((10, 0, 196)), cam.xy((-50, 0, 184))
    s += arrow(a[0], a[1], b[0], b[1])
    s += al((a[0] + b[0]) / 2, min(a[1], b[1]) - 8, "真空引き")
    c, d = cam.xy((-60, 0, 108)), cam.xy((0, 0, 126))
    s += arrow(c[0], c[1], d[0], d[1])
    s += al((c[0] + d[0]) / 2 + 4, max(c[1], d[1]) + 16, "定量充填")
    e = cam.xy((82, 0, 96))
    s += lab(e[0] + 12, e[1], "充填ヘッド", "start")
    return s


# =====================================================================================
# q:crane — coil handling: an overhead crane trolley lifts a steel coil with a C-hook through its eye
# =====================================================================================
@picto("crane")
def _():
    zc = 52                                    # coil axis height

    def fn(sc):
        BOX(sc, -170, -16, 214, 340, 32, 30, "pt", dark=1)                       # girder
        BOX(sc, -36, -32, 244, 72, 64, 24, "dk", ch=4)                            # trolley
        CYL(sc, (-26, 0, 268), (1, 0, 0), 14, 52, "m", seg=24)                    # hoist drum
        BOX(sc, -60, -12, 150, 34, 24, 22, "m", ch=3)                             # hook block
        BOX(sc, -96, -11, 128, 62, 22, 18, "pt", dark=.5)                         # C-hook upper arm
        BOX(sc, -96, -11, zc - 8, 18, 22, 80, "pt", dark=.5)                      # C-hook back
        BOX(sc, -78, -11, zc - 8, 78, 22, 16, "pt", dark=.5)                      # C-hook lower arm (outside)
        BOX(sc, 0, -11, zc - 8, 66, 22, 16, "pt", 6)                              # lower arm inside the eye
        RING(sc, (0, 0, zc), (1, 0, 0), 56, 22, 80, "w", seg=48)                  # steel coil

        def ropes(s_):
            d = ""
            for x in (-52, -34):
                for y in (-6, 6):
                    d += P([s_.cam.xy((x, y, 214)), s_.cam.xy((x, y, 172))], False)
            return path(d, "o")
        RAW(sc, ropes, ((-52, -6, 172), (-34, 6, 214)), -1)
    s, sc = fit(fn, 30, 20, (40, 16, 280, 176), sh_ry=7, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (40, -16, 250), (130, -16, 250), both=True)
    a, b = cam.xy((-120, -12, 190)), cam.xy((-120, -12, 120))
    s += arrow(a[0], a[1], b[0], b[1], both=True)
    c = cam.xy((85, -16, 250))
    s += al(c[0], c[1] - 10, "横行")
    s += al(a[0] - 6, (a[1] + b[1]) / 2 + 4, "巻上げ", "end")
    d = cam.xy((80, -56, zc - 30))
    s += lab(d[0] + 10, d[1] + 4, "コイル", "start")
    e = cam.xy((-96, -12, zc + 20))
    s += lab(e[0] - 8, e[1] + 4, "Cフック", "end")
    return s


# =====================================================================================
# q:sew — industrial sewing machine: the needle goes up and down through the layered fabric
# while the feed dog moves it on, leaving the seam behind
# =====================================================================================
@picto("sew")
def _():
    xn = -112                                  # needle x

    def fn(sc):
        BOX(sc, -160, -56, 0, 300, 112, 24, "pt", ch=6)                          # bed
        BOX(sc, 84, -26, 24, 52, 52, 92, "pt", ch=8)                              # pillar
        BOX(sc, -90, -22, 116, 226, 44, 34, "pt", ch=8)                           # arm
        BOX(sc, -140, -26, 70, 50, 52, 80, "pt", ch=8)                            # head
        CYL(sc, (136, 0, 133), (1, 0, 0), 26, 12, "dk", seg=32)                   # hand wheel
        CYL(sc, (xn, 0, 44), (0, 0, 1), 3.5, 26, "m", seg=12)                     # needle bar
        CYL(sc, (xn, 0, 28.5), (0, 0, 1), 1.3, 16, "t", seg=8, bias=-1)            # needle
        CYL(sc, (xn + 14, 0, 40), (0, 0, 1), 2.5, 30, "m", seg=10)                # presser bar
        BOX(sc, xn - 6, -10, 29, 26, 20, 4, "m", -1)                              # presser foot
        BOX(sc, -190, -80, 24, 130, 150, 2.5, "dk")                               # fabric (lower)
        BOX(sc, -186, -76, 26.5, 122, 142, 2.5, "w", ch=0)                        # fabric (upper)

        def seam(s_):
            return path(P([s_.cam.xy((xn, 0, 29.1)), s_.cam.xy((xn, 66, 29.1))], False), "o dash")
        RAW(sc, seam, ((xn, 0, 29), (xn, 66, 29.2)), -2)
    s, sc = fit(fn, -24, 24, (30, 16, 290, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((xn - 46, -26, 84)), cam.xy((xn - 46, -26, 44))
    s += arrow(a[0], a[1], b[0], b[1], both=True)
    s += al(a[0] - 6, (a[1] + b[1]) / 2 + 4, "上下", "end")
    c, d = cam.xy((xn + 40, -66, 29)), cam.xy((xn + 40, 10, 29))
    s += arrow(c[0], c[1], d[0], d[1])
    s += al(c[0] + 8, c[1] + 10, "送り", "start")
    e = cam.xy((xn, -10, 40))
    s += lab(e[0] - 12, e[1] + 6, "針", "end")
    f = cam.xy((xn, 66, 29))
    s += lab(f[0] + 6, f[1] - 4, "縫い目", "start")
    return s


# =====================================================================================
# q:cutting — automatic (CAD) cutter: a reciprocating knife on an X-Y gantry cuts the pattern pieces
# out of a stack of fabric layers held down by vacuum
# =====================================================================================
@picto("cutting")
def _():
    zt = 56                                    # stack top

    def fn(sc):
        BOX(sc, -170, -96, 0, 340, 192, 40, "pt", dark=1)                        # table (bristle bed)
        BOX(sc, -150, -76, 40, 300, 152, 16, "w")                                 # fabric stack

        def marks(s_):
            cm = s_.cam
            d = "".join(P([cm.xy((-150, -76.1, z)), cm.xy((150, -76.1, z))], False) for z in range(43, 56, 3))
            o = path(d, "gr")
            for x0, y0, w, h in ((-130, -56, 70, 46), (-130, 4, 70, 56), (-44, -56, 64, 112)):
                o += path(P([cm.xy((x0, y0, zt + .1)), cm.xy((x0 + w, y0, zt + .1)), cm.xy((x0 + w - 8, y0 + h, zt + .1)), cm.xy((x0 + 8, y0 + h, zt + .1))]), "o dash")
            o += path(P([cm.xy((60, 40, zt + .1)), cm.xy((60, -50, zt + .1)), cm.xy((120, -50, zt + .1)), cm.xy((128, 40, zt + .1))], False), "a")
            return o
        RAW(sc, marks, ((-150, -76.2, 40), (150, 76, zt + .2)), -1)
        for y in (-116, 96):
            BOX(sc, 128, y, 0, 26, 20, 112, "pt", ch=3)                           # gantry legs
        BOX(sc, 128, -116, 112, 26, 232, 24, "pt")                                # gantry beam
        BOX(sc, 96, 18, 72, 32, 44, 60, "m", ch=4)                                # cutting head
        BOX(sc, 108, 37, zt, 7, 6, 16, "t", -1)                                   # knife
    s, sc = fit(fn, 30, 26, (26, 28, 294, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (141, -30, 150), (141, 60, 150), both=True)
    s += arrow3(cam, (170, -130, 0), (240, -130, 0))
    a = cam.xy((141, 15, 150))
    s += al(a[0], a[1] - 10, "ヘッド移動")
    b = cam.xy((-170, -96, 0))
    s += lab(b[0] - 2, b[1] + 18, "積層した生地", "start")
    c = cam.xy((96, 40, zt + 10))
    s += lab(c[0] - 8, c[1] - 6, "ナイフ", "end")
    d = cam.xy((240, -130, 0))
    s += al(d[0] - 10, d[1] + 18, "門形走行", "end")
    return s


def solid(cam, O, A, outline, h, mat, **kw):
    return compact(GE.prism(cam, O, GE._norm(A), outline, h, mat, **kw))


def rect_o(w, h):
    return [(-w / 2, -h / 2, 0), (w / 2, -h / 2, 1), (w / 2, h / 2, 2), (-w / 2, h / 2, 3)]


def face(cam, pts, nrm, mat):
    """flat polygon shaded by its normal (skipped when facing away)."""
    if GE._dot(nrm, cam.D) > 0:
        return ""
    return poly3(cam, pts, mat + "s%d" % GE.shade(GE._norm(nrm)))


# =====================================================================================
# q:harnessboard — wire-harness assembly board: the bundle is laid out full size along fork jigs
# on an inclined board, then wrapped with tape (taping machine)
# =====================================================================================
@picto("harnessboard")
def _():
    t = math.radians(28)
    n_ = (0, -math.cos(t), math.sin(t))
    z0 = 70

    def F(u, v, off=0.0):
        return (u + n_[0] * off, v * math.sin(t) + n_[1] * off, z0 + v * math.cos(t) + n_[2] * off)
    trunk = [(-150, 74), (-60, 72), (0, 75), (60, 78), (104, 79), (150, 80)]
    br = [[(-60, 72), (-74, 132)], [(0, 75), (8, 18)], [(60, 78), (84, 136)], [(104, 79), (134, 22)]]
    jigs = [(-120, 73), (-30, 73), (30, 76), (-68, 108), (6, 40), (74, 112), (122, 45)]
    ends = [(-150, 74), (-74, 132), (8, 18), (84, 136), (134, 22), (150, 80)]

    def fn(sc):
        for x in (-130, 110):
            BOX(sc, x, 20, 0, 20, 20, z0 + 20, "dk")                               # legs
        BOX(sc, -150, -10, 0, 300, 50, 6, "dk")                                    # foot
        cam = sc.cam
        U0, U1, V1, th = -170, 170, 160, 10
        o = ""
        bk = [F(U0, 0, -th), F(U1, 0, -th), F(U1, V1, -th), F(U0, V1, -th)]
        fr = [F(U0, 0), F(U1, 0), F(U1, V1), F(U0, V1)]
        o += face(cam, [fr[3], fr[2], bk[2], bk[3]], (0, math.sin(t), math.cos(t)), "pt")
        o += face(cam, [fr[1], fr[2], bk[2], bk[1]], (1, 0, 0), "pt")
        o += face(cam, [fr[0], fr[3], bk[3], bk[0]], (-1, 0, 0), "pt")
        o += face(cam, [fr[0], fr[1], bk[1], bk[0]], (0, -math.sin(t), -math.cos(t)), "pt")
        o += face(cam, fr, n_, "pt")
        # grid printed on the board (the full-size drawing)
        d = "".join(P([cam.xy(F(u, 6)), cam.xy(F(u, V1 - 6))], False) for u in range(-150, 151, 50))
        d += "".join(P([cam.xy(F(U0 + 6, v)), cam.xy(F(U1 - 6, v))], False) for v in range(30, 151, 40))
        o += path(d, "gline")
        for u, v in ends:                                                          # connectors / clips
            o += solid(cam, F(u, v, 0), n_, rect_o(16, 12), 12, "dk", lines=False)
        o += '<path class="cable3" d="%s"/>' % P([cam.xy(F(u, v, 8)) for u, v in trunk], False)
        for b in br:
            o += '<path class="cable" d="%s"/>' % P([cam.xy(F(u, v, 8)) for u, v in b], False)
        # tape wrapped on part of the trunk (spiral)
        d = ""
        for k in range(9):
            u = -40 + k * 7
            d += P([cam.xy(F(u - 2, 73.5 - 4.5, 8)), cam.xy(F(u + 2, 74 + 4.5, 8))], False)
        o += path(d, "o")
        for u, v in jigs:                                                          # fork jigs
            for du in (-5, 5):
                o += solid(cam, F(u + du, v, 0), n_, GE.circle_outline(1.8, 8, 4), 16, "m", lines=False, smooth=True)
        # taping head around the trunk
        A = (1, 0, .01)
        o += solid(cam, F(26, 76.5, 8), (1, 0, .01), GE.circle_outline(22, 28, 8), 14, "t", holes=[GE.circle_outline(9, 20, 20)], smooth="outer")
        return o
    s, sc = fit(fn, -18, 26, (52, 28, 262, 176), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, F(34, 76.5, 8), (1, 0, 0), 30, 120, 330)
    a = cam.xy(F(30, 160))
    s += al(a[0], a[1] - 8, "テープ巻き")
    b = cam.xy(F(-170, 160))
    s += lab(b[0] + 6, b[1] - 8, "図板", "start")
    c = cam.xy(F(-170, 73))
    s += lab(c[0] - 6, c[1] + 4, "治具", "end")
    e = cam.xy(F(170, 80, 0))
    s += lab(e[0] + 6, e[1] + 4, "コネクタ", "start")
    return s


# =====================================================================================
# q:loom — loom: heddle frames lift and lower alternate warp yarns to open the shed, the weft is shot
# across (air jet), the reed beats it in and the cloth is wound on the cloth beam
# =====================================================================================
@picto("loom")
def _():
    W, zf = 110, 92                            # half width, cloth fell height
    xs = [-W + 10 + 20 * k for k in range(11)]

    def fn(sc):
        cam = sc.cam
        o = solid(cam, (-W - 10, 160, 52), (1, 0, 0), GE.circle_outline(30, 32, 10), 2 * W + 20, "w", smooth=True, dark=1)   # warp beam
        o += solid(cam, (-W - 22, 160, 52), (1, 0, 0), GE.circle_outline(40, 32, 10), 12, "m", smooth=True)               # beam flange (left)
        up = lambda i: i % 2 == 0
        d1 = d2 = ""
        for i, x in enumerate(xs):
            zh = 112 if up(i) else 76
            d1 += P([cam.xy((x, 160, 82)), cam.xy((x, 76, zh))], False)
            d2 += P([cam.xy((x, 64, zh)), cam.xy((x, 6, zf))], False)
        o += path(d1, "o")
        for y, dz, sel in ((76, 16, False), (64, -16, True)):                       # two heddle frames
            zb, ztp = 62 + dz, 128 + dz
            for z in (zb, ztp):
                o += solid(cam, (-W - 14, y, z), (1, 0, 0), rect_o(5, 6), 2 * W + 28, "m", lines=False)
            dd = "".join(P([cam.xy((x, y, zb + 3)), cam.xy((x, y, ztp - 3))], False) for i, x in enumerate(xs) if up(i) == sel)
            o += path(dd, "gline")
        o += path(d2, "o")
        # reed (comb) at the front of the shed
        o += solid(cam, (-W - 14, 22, zf - 30), (1, 0, 0), rect_o(5, 6), 2 * W + 28, "dk", lines=False)
        o += solid(cam, (-W - 14, 22, zf + 26), (1, 0, 0), rect_o(5, 6), 2 * W + 28, "dk", lines=False)
        o += path("".join(P([cam.xy((x, 22, zf - 27)), cam.xy((x, 22, zf + 23))], False) for x in range(-W - 8, W + 9, 9)), "gline")
        # main nozzle (air jet) at the left
        o += solid(cam, (-W - 50, 14, zf + 2), (1, 0, 0), GE.circle_outline(4, 12, 4), 30, "t", smooth=True)
        # woven cloth and cloth beam
        cl = [(-W, 6, zf), (W, 6, zf), (W, -56, zf), (-W, -56, zf)]
        o += face(cam, cl, (0, 0, 1), "w")
        o += path("".join(P([cam.xy((-W, y, zf)), cam.xy((W, y, zf))], False) for y in range(0, -56, -5)), "gline")
        o += solid(cam, (-W - 10, -78, zf - 24), (1, 0, 0), GE.circle_outline(24, 32, 10), 2 * W + 20, "w", smooth=True)
        return o
    s, sc = fit(fn, -58, 24, (30, 26, 290, 172), sh_ry=6, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-W - 14, 12, zf + 4), (W + 30, 12, zf + 4))
    a, b = cam.xy((W + 26, 70, 150)), cam.xy((W + 26, 70, 108))
    s += arrow(a[0], a[1], b[0], b[1], both=True)
    s += arc3(cam, (-W - 10, -78, zf - 24), (1, 0, 0), 32, 200, 300)
    c = cam.xy((W + 30, 12, zf + 4))
    s += al(c[0] + 4, c[1] + 14, "緯糸", "start")
    s += lab(a[0], a[1] - 8, "綜絖")
    e = cam.xy((W, 160, 90))
    s += lab(e[0] + 4, e[1] - 6, "経糸", "start")
    f = cam.xy((W, -56, zf))
    s += lab(f[0] + 6, f[1] + 10, "布", "start")
    return s


def xsec(cam, x0, L, pieces):
    """profiles (y, z) extruded along +x from x0, seen from the -x side: all side strips depth-sorted
    together, then every front cap (they share the plane x0, so the caps read as a cut section)."""
    items, caps = [], ""
    for loop, mat, kw in pieces:
        lp = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(loop)]
        caps += GE.prism(cam, (x0, 0, 0), (1, 0, 0), lp, L, mat, collect=items, **kw)
    return compact(GE.render_items(items)) + caps


def rq(y0, z0, y1, z1):
    return [(y0, z0), (y1, z0), (y1, z1), (y0, z1)]


def ann(cy, cz, r0, r1, a0, a1):
    """one convex piece of an annulus (angles in degrees, y-z plane)."""
    return arc(cy, cz, r1, a0, a1, 3) + arc(cy, cz, r0, a1, a0, 3)


# =====================================================================================
# q:slush — powder slush moulding (cut view): the heated nickel shell mould is clamped on the powder
# box and the pair is rotated; powder melts on the hot mould face and builds up the skin
# =====================================================================================
@picto("slush")
def _():
    cz, R = 34, 84

    def fn(sc):
        cam = sc.cam
        pcs = [(rq(-92, -40, 92, -30), "m", {"dark": 1}), (rq(-92, -30, -82, 54), "m", {"dark": 1}),
               (rq(82, -30, 92, 54), "m", {"dark": 1}),
               (rq(-80, -30, 80, -10) [:2] + [(62, 14), (-62, 14)], "w", {"cap_mat": "w3"})]
        for k in range(6):
            a0, a1 = 18 + k * 24, 18 + (k + 1) * 24
            pcs.append((ann(0, cz, R, R + 8, a0, a1), "h", {}))
            pcs.append((ann(0, cz, R - 4, R, a0, a1), "w", {}))
        pcs += [(rq(-100, 54, -76, 60), "dk", {}), (rq(76, 54, 100, 60), "dk", {})]
        o = xsec(cam, 0, 90, pcs)

        def dots():
            d = ""
            for i in range(26):
                y, z = -54 + (i * 37) % 108, -4 + (i * 13) % 24 - 12
                if abs(y) < 76 - (z + 10) * .5:
                    p = cam.xy((-.2, y, z))
                    d += "M%s %sh1.6" % (n(p[0]), n(p[1]))
            return path(d, "o")
        return o + dots()
    s, sc = fit(fn, 34, 14, (60, 24, 250, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-10, 0, cz - 20), (1, 0, 0), 126, 110, 190)
    p = cam.xy((0, -40, cz + R + 8))
    s += heat(p[0] - 14, p[1] - 6, 3, 14)
    a = cam.xy((90, -R - 8, cz + 10))
    s += lab(a[0] + 6, a[1], "加熱した型", "start")
    b = cam.xy((90, -92, -20))
    s += lab(b[0] + 6, b[1] + 4, "パウダー", "start")
    c = cam.xy((0, R, cz + 30))
    s += lab(c[0] - 6, c[1], "表皮", "end")
    d = cam.xy((-10, -126 * math.cos(math.radians(40)), cz - 20 + 126 * math.sin(math.radians(140))))
    s += al(d[0] - 10, d[1] + 30, "反転", "end")
    return s


# =====================================================================================
# q:tmold — transfer moulding (cut view): the resin tablet melts in the heated pot and the plunger
# pushes it through the runners into the cavities over the lead frame
# =====================================================================================
@picto("tmold")
def _():
    def fn(sc):
        cam = sc.cam
        pcs = [(rq(-110, -50, -14, 0), "t", {"dark": 1}), (rq(14, -50, 110, 0), "t", {"dark": 1}),     # lower mould + pot
               (rq(-110, 14, 110, 52), "t", {}),                                                       # upper mould
               (rq(-110, 2, -86, 14), "t", {}), (rq(-38, 6, 38, 14), "t", {}), (rq(86, 2, 110, 14), "t", {}),
               (rq(-104, 0, -14, 2), "cu", {}), (rq(14, 0, 104, 2), "cu", {}),                        # lead frame
               (rq(-86, 2, -38, 14), "dk", {}), (rq(38, 2, 86, 14), "dk", {}),                        # packages (cavities)
               (rq(-38, 2, 38, 6), "dk", {}), (rq(-14, -16, 14, 2), "dk", {}),                        # runner + cull
               (rq(-13, -76, 13, -16), "m", {})]                                                       # plunger
        return xsec(cam, 0, 70, pcs)
    s, sc = fit(fn, 34, 14, (60, 20, 262, 172), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((-4, 0, -100)), cam.xy((-4, 0, -74))
    s += arrow(a[0], a[1] + 4, b[0], b[1])
    p = cam.xy((60, -60, 52))
    s += heat(p[0], p[1] - 8, 3, 12)
    s += al(a[0] + 8, a[1] + 2, "プランジャ", "start")
    c = cam.xy((0, 110, 36))
    s += lab(c[0] - 6, c[1] + 4, "上型", "end")
    d = cam.xy((0, 110, -26))
    s += lab(d[0] - 6, d[1] + 4, "下型", "end")
    e = cam.xy((0, -62, -50))
    s += lab(e[0] + 10, e[1] + 18, "封止樹脂", "start")
    return s


# =====================================================================================
# q:hotpress — multi-daylight hot press: heated platens close on the moulds (brake pads:
# backplate + friction material) and hold heat and pressure while the material cures
# =====================================================================================
@picto("hotpress")
def _():
    def fn(sc):
        BOX(sc, -110, -60, -30, 220, 120, 30, "pt", dark=1)                    # base
        CYL(sc, (0, 0, 0), (0, 0, 1), 34, 14, "m", seg=32)                     # ram
        for x in (-110, 90):
            BOX(sc, x, -60, 0, 20, 120, 186, "pt", dark=1)                      # side housings
        BOX(sc, -110, -60, 186, 220, 120, 28, "pt", dark=1)                    # crown
        zs = [14, 66, 118, 170]
        for i, z in enumerate(zs):
            BOX(sc, -88, -50, z, 176, 100, 14 if i < 3 else 16, "m", ch=2)      # heated platens
            if i < 3:
                for x in (-70, -16, 38):
                    BOX(sc, x, -26, z + 14, 32, 52, 6, "w")                     # backplate
                    BOX(sc, x + 3, -22, z + 20, 26, 44, 12, "dk")               # friction material
    s, sc = fit(fn, -26, 18, (40, 16, 270, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((-130, -60, 30)), cam.xy((-130, -60, 90))
    s += arrow(a[0] - 6, a[1], b[0] - 6, b[1])
    s += al(a[0] - 12, (a[1] + b[1]) / 2 + 4, "加圧", "end")
    for z in (66, 118):
        p = cam.xy((88, -50, z + 7))
        s += heat(p[0] + 22, p[1] + 2, 2, 8)
    c = cam.xy((88, -50, 125))
    s += lab(c[0] + 30, c[1] - 30, "熱板", "start")
    d = cam.xy((-38, -26, 32))
    s += lab(d[0], d[1] + 46, "ブレーキパッド", "middle")
    return s


# =====================================================================================
# q:cutter — ultrasonic cutter on a robot wrist: the blade, vibrating ~20-40 kHz along its axis,
# trims the moulded resin part along the trim line (water-jet cutting works the same way with a jet)
# =====================================================================================
@picto("cutter")
def _():
    xb, yc = 30, 20                             # blade position, trim line y

    def fn(sc):
        BOX(sc, -140, -70, -40, 280, 140, 30, "m", dark=1)                      # fixture
        X(sc, -130, 260, rq(-60, -10, 60, -4), "w")                              # moulded resin part
        X(sc, -130, 260, [(-60, -10), (-56, -10), (-70, -36), (-74, -36)], "w")  # front flange
        CYL(sc, (xb, yc, -4), (0, 0, 1), 2.5, 12, "t", seg=8)                    # blade (in the cut)
        CYL(sc, (xb, yc, 8), (0, 0, 1), 6, 26, "t", seg=20, r1=11)               # horn (taper)
        CYL(sc, (xb, yc, 34), (0, 0, 1), 13, 22, "dk", seg=24)                   # booster
        CYL(sc, (xb, yc, 56), (0, 0, 1), 18, 40, "pt", seg=28, dark=1)           # transducer
        CYL(sc, (xb, yc, 96), (0, 0, 1), 22, 12, "m", seg=28)                    # robot flange

        def cut(s_):
            cm = s_.cam
            o = path(P([cm.xy((-130, yc, -3.9)), cm.xy((xb, yc, -3.9))], False), "o")
            o += path(P([cm.xy((xb, yc, -3.9)), cm.xy((130, yc, -3.9))], False), "o cutl")
            return o
        RAW(sc, cut, ((-130, yc - 1, -4), (130, yc + 1, -3.8)), -1)
    s, sc = fit(fn, 30, 26, (30, 16, 290, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (xb + 30, yc - 40, 0), (xb + 100, yc - 40, 0))
    a, b = cam.xy((xb - 34, yc, 60)), cam.xy((xb - 34, yc, 26))
    s += arrow(a[0], a[1], b[0], b[1], both=True)
    s += al(a[0] - 8, (a[1] + b[1]) / 2 + 4, "超音波振動", "end")
    c = cam.xy((xb + 65, yc - 40, 0))
    s += al(c[0] + 4, c[1] + 16, "送り", "middle")
    d = cam.xy((130, yc, -4))
    s += lab(d[0] - 4, d[1] - 10, "トリム線", "end")
    return s


# =====================================================================================
# q:glasscut — glass cutting: a carbide wheel on the X-Y head scribes the outline (score) on the sheet,
# the sheet is broken along it, and a diamond wheel grinds the edges
# =====================================================================================
@picto("glasscut")
def _():
    zt = 4
    shape = [(-110, -50), (110, -50), (96, 50), (-96, 50)]

    def fn(sc):
        BOX(sc, -160, -90, -30, 320, 180, 30, "m", dark=1)                      # cutting table
        BOX(sc, -150, -80, 0, 300, 160, zt, "fl")                               # glass sheet

        def score(s_):
            cm = s_.cam
            pts_ = [cm.xy((x, y, zt + .1)) for x, y in shape]
            return path(P(pts_[:3], False), "o") + path(P(pts_[2:] + pts_[:1], False), "o cutl")
        RAW(sc, score, ((-150, -80, zt), (150, 80, zt + .2)), -1)
        for y in (-104, 90):
            BOX(sc, 70, y, -30, 20, 14, 120, "pt")                               # gantry legs
        BOX(sc, 70, -104, 90, 20, 208, 16, "pt")                                 # beam
        BOX(sc, 52, 32, 40, 18, 30, 56, "m", ch=3)                               # head carriage
        CYL(sc, (96, 50, zt + 30), (0, 0, 1), 5, 10, "m", seg=12)                # holder
        CYL(sc, (96, 46, zt + 9), (0, 1, 0), 9, 5, "t", seg=20)                  # cutter wheel
        BOX(sc, 84, 44, zt + 16, 24, 9, 20, "m")                                 # fork
        CYL(sc, (176, -40, -6), (0, 0, 1), 20, 14, "t", seg=32)                  # diamond grinding wheel
        CYL(sc, (176, -40, 8), (0, 0, 1), 6, 30, "m", seg=16)                    # wheel spindle
    s, sc = fit(fn, -28, 28, (26, 22, 294, 174), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (176, -40, 0), (0, 0, 1), 30, -40, 80)
    a = cam.xy((-160, -90, -30))
    s += al(a[0] + 4, a[1] + 18, "切筋（スコア）", "start")
    b = cam.xy((96, 44, zt + 30))
    s += lab(b[0] - 26, b[1] - 26, "カッタホイール", "middle")
    c = cam.xy((196, -40, 0))
    s += lab(c[0] - 6, c[1] + 26, "エッジ研削", "middle")
    return s


# =====================================================================================
# q:glassbend — bending & tempering line: the sheet is heated near its softening point in the roller
# furnace, pressed to shape on the bending mould, then quenched by air jets from both sides
# =====================================================================================
@picto("glassbend")
def _():
    xe = 0                                      # furnace exit

    def fn(sc):
        for x in range(-196, 200, 26):
            CYL(sc, (x, -66, -6), (0, 1, 0), 6, 132, "m", seg=12, bands=6)          # rollers
        BOX(sc, -210, -80, -30, 210, 160, 100, "pt", dark=1)                     # furnace housing
        RAW(sc, lambda s_: poly3(s_.cam, [(xe + .2, -60, 2), (xe + .2, 60, 2), (xe + .2, 60, 26), (xe + .2, -60, 26)], "h"),
            ((xe, -60, 2), (xe + .3, 60, 26)), -1)
        BOX(sc, xe + 4, -50, 0, 50, 100, 3, "h")                                 # hot sheet leaving the furnace
        # bent sheet under the press (curved across y)
        pcs = []
        for k in range(6):
            pcs.append((ann(0, -150, 160, 164, 72 + k * 6, 72 + (k + 1) * 6), "fl", {}))
        RAW(sc, lambda s_: xsec(s_.cam, 100, 70, pcs), ((100, -50, 0), (170, 50, 14)), 0)
        BOX(sc, 92, -62, 40, 86, 124, 30, "m", dark=1)                           # upper quench box / press
        BOX(sc, 92, -62, -46, 86, 124, 30, "m", dark=1)                          # lower quench box

        def jets(s_):
            o = ""
            for x in (108, 135, 162):
                for y in (-40, 0, 40):
                    o += hole3(s_.cam, (x, y, 39.9), (0, 0, -1), 3, "dk", 8)
            return o
        RAW(sc, jets, ((92, -62, 39.8), (178, 62, 40)), -1)
    s, sc = fit(fn, -30, 22, (26, 22, 294, 172), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    for x in (112, 158):
        a, b = cam.xy((x, -70, 40)), cam.xy((x, -70, 18))
        s += arrow(a[0], a[1], b[0], b[1])
    c = cam.xy((-100, -80, 70))
    s += lab(c[0], c[1] - 10, "加熱炉")
    d = cam.xy((135, 0, 70))
    s += al(d[0], d[1] - 12, "風冷強化")
    e = cam.xy((30, -50, 0))
    s += lab(e[0], e[1] + 24, "ガラス")
    f = cam.xy((178, -62, -46))
    s += lab(f[0] + 6, f[1] + 12, "曲げ型", "start")
    return s


# =====================================================================================
# q:autoclave — autoclave: a horizontal pressure vessel; racks of laminated glass roll in on rails,
# the door is closed and the load is held at about 130-140 degC and 1.2-1.3 MPa
# =====================================================================================
@picto("autoclave")
def _():
    R, x0, L, zc = 66, 0, 230, 78

    def fn(sc):
        for x in (40, 180):
            BOX(sc, x, -44, 0, 26, 88, zc - R + 10, "dk")                          # saddles
        RING(sc, (x0, 0, zc), (1, 0, 0), R + 8, R - 8, 14, "m", seg=48)           # door flange
        CYL(sc, (x0 + 14, 0, zc), (1, 0, 0), R, L - 14, "pt", seg=48, dark=.5)    # shell
        CYL(sc, (x0 + L, 0, zc), (1, 0, 0), R, 22, "pt", seg=48, r1=R * .7, dark=.5)   # dished end
        RAW(sc, lambda s_: hole3(s_.cam, (x0 - .1, 0, zc), (-1, 0, 0), R - 8, "bg", 40), ((x0 - .2, -R, zc - R), (x0, R, zc + R)), -1)
        for y in (-30, 30):
            BOX(sc, -200, y - 3, 0, 200, 6, 4, "m")                                # rails
        BOX(sc, -170, -40, 6, 110, 80, 10, "m", dark=1)                           # cart
        for k in range(6):
            BOX(sc, -160 + k * 16, -34, 16, 4, 68, 64, "fl")                       # laminated glass sheets
        for x in (-160, -76):
            BOX(sc, x, -38, 16, 6, 4, 70, "dk")                                    # rack posts
    s, sc = fit(fn, 32, 18, (30, 26, 292, 174), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-50, -50, 40), (-6, -50, 40))
    a = cam.xy((120, 0, zc + R))
    s += al(a[0], a[1] - 12, "加熱・加圧")
    b = cam.xy((-110, -40, 6))
    s += lab(b[0], b[1] + 24, "合わせガラス")
    c = cam.xy((x0 + L, -R, zc - R))
    s += lab(c[0] - 4, c[1] + 22, "圧力容器", "end")
    return s
