"""v3 shaded-3D principle drawings: performance / function testing (second half) —
damper, flow, engine & motor dynos, NVH bench, battery / hi-pot / ICT / continuity / power-semi testers,
environmental chamber, camera calibration, airbag deployment, bearing noise, tyre uniformity and the
end-of-line vehicle checks (alignment, headlamp aim, ADAS aiming, roller dyno, exhaust gas, shower, noise)."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def Y(sc, y0, L, xz, mat="pt", bias=0.0, **kw):
    """outline [(x, z), ...] extruded along +y from y0."""
    loop = [(-p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L, mat, **kw)),
           ((min(xs), y0, min(zs)), (max(xs), y0 + L, max(zs))), bias)


def fpoly(cam, pts3, c):
    """flat polygon given by 3D points (marks on a face)."""
    return path(P([cam.xy(p) for p in pts3]), c)


def fline(cam, pts3, c="o"):
    return path(P([cam.xy(p) for p in pts3], False), c)


def bez3(p0, p1, p2, k=10):
    """quadratic Bezier through 3D control points (for cables / hoses)."""
    return [tuple((1 - t) ** 2 * p0[i] + 2 * (1 - t) * t * p1[i] + t * t * p2[i] for i in range(3))
            for t in (j / k for j in range(k + 1))]


def visible(cam, nrm):
    return GE._dot(GE._norm(nrm), cam.D) < -0.02


def screen_y(cam, x0, x1, z0, z1, y, kind="wave"):
    """small display on a -y facing panel: dark glass + one trace."""
    o = fpoly(cam, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], "scrn")
    w, h = x1 - x0, z1 - z0
    pts = []
    for i in range(25):
        t = i / 24
        if kind == "wave":
            v = .5 + .3 * math.sin(t * 4 * PI_)
        elif kind == "step":
            v = .2 + .6 * (1 - math.exp(-t * 6))
        elif kind == "spec":
            v = .15 + .7 * math.exp(-((t - .3) / .05) ** 2) + .4 * math.exp(-((t - .62) / .04) ** 2)
        elif kind == "cycle":
            v = .5 + .32 * max(-1, min(1, 2.2 * math.sin(t * 4 * PI_)))
        elif kind == "loop":
            a = t * 2 * PI_
            pts.append((x0 + w * (.5 + .38 * math.cos(a)), y - .1, z0 + h * (.5 + .3 * math.sin(a) + .08 * math.sin(2 * a))))
            continue
        else:   # pulse
            v = .2 + (.6 if (.2 < t < .45 or .6 < t < .75) else 0)
        pts.append((x0 + w * (.1 + .8 * t), y - .1, z0 + h * (.12 + .76 * v)))
    return o + fline(cam, pts, "scrg")


PI_ = math.pi


def cabinet(sc, x, y, z, sx, sy, sz, kind="wave", mat="pt", bias=0.0, scr=(0.15, 0.85, 0.5, 0.88)):
    """instrument cabinet with a display on its -y face."""
    BOX(sc, x, y, z, sx, sy, sz, mat, bias, ch=2, dark=1)
    a, b, c, d = scr
    RAW(sc, lambda s_: screen_y(s_.cam, x + sx * a, x + sx * b, z + sz * c, z + sz * d, y - .05, kind),
        ((x, y - .2, z), (x + sx, y - .05, z + sz)), bias - 1)


def glass_cyl(cam, C, r, h, level=0.4):
    """transparent graduated vessel (vertical axis) with liquid up to level*h."""
    bot = circ3(cam, C, (0, 0, 1), r, 28)
    top = circ3(cam, (C[0], C[1], C[2] + h), (0, 0, 1), r, 28)
    lv = circ3(cam, (C[0], C[1], C[2] + h * level), (0, 0, 1), r * .97, 28)
    o = path(P(hull(bot + top)), "gl") + path(P(hull(bot + lv)), "fl") + path(P(lv), "fo")
    for k in range(1, 6):
        a = cam.xy((C[0] - r * .5, C[1] - r * .87, C[2] + h * k / 6))
        o += line(a[0], a[1], a[0] + 5, a[1] - 1.5, "o thin")
    return o + path(P(top), "o")


def RING2(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=40, **kw):
    """ring with a lightly segmented bore (fewer edge lines than il3_lib.RING)."""
    CYL(sc, O, A, ro, h, mat, bias, seg, holes=[GE.circle_outline(ri, seg, 10)], **kw)


def cable3(cam, p0, p1, p2, c="cable"):
    return fline(cam, bez3(p0, p1, p2, 12), c)


# =====================================================================================
# a simple, elegant car (front at x=0 looking towards -x; flip=True puts the front at x=200)
# length 200, width 84 (y -42..42), wheels r18 at x 42 / 158
# =====================================================================================
CAR_L = 200


def car(sc, flip=False, mat="pt", lamps=True, ox=0.0, oz=0.0):
    fx = (lambda x: CAR_L - x + ox) if flip else (lambda x: x + ox)
    body = [(2, 13), (0, 24), (3, 31), (14, 37), (62, 42), (170, 42), (196, 39), (200, 30), (199, 16), (194, 12), (8, 12)]
    cab = [(64, 42), (98, 63), (150, 64), (176, 42)]
    Y(sc, -42, 84, [(fx(x), z + oz) for x, z in body], mat, dark=.5)
    Y(sc, -36, 72, [(fx(x), z + oz) for x, z in cab], mat, dark=.5)
    for xw in (42, 158):
        X_ = fx(xw)
        CYL(sc, (X_, -44, 18 + oz), (0, 1, 0), 18, 14, "dk", -40, seg=28, bands=8)
        CYL(sc, (X_, 30, 18 + oz), (0, 1, 0), 18, 14, "dk", 40, seg=28, bands=8)

        def arch(s_, X_=X_):
            pts = [(X_ + 21.5 * math.cos(math.radians(a)), -42.05, 18 + oz + 21.5 * math.sin(math.radians(a))) for a in range(-17, 200, 12)]
            return fpoly(s_.cam, pts, "dks3")
        RAW(sc, arch, ((X_ - 22, -42.2, oz), (X_ + 22, -42.05, oz + 40)), -20)

        def hub(s_, X_=X_):
            return hole3(s_.cam, (X_, -44.05, 18 + oz), (0, -1, 0), 11, "m2") + hole3(s_.cam, (X_, -44.1, 18 + oz), (0, -1, 0), 4, "m3")
        RAW(sc, hub, ((X_ - 12, -44.2, oz + 6), (X_ + 12, -44.05, oz + 30)), -41)

    def glass(s_):
        cam = s_.cam
        o = ""
        y = -36.05
        for ws in ([(70, 45), (97, 61), (118, 61.3), (118, 45)], [(122, 45), (122, 61.4), (148, 61.6), (169, 45)]):
            o += fpoly(cam, [(fx(x), y, z + oz) for x, z in ws], "win")
        # windscreen (front slope) and rear window (rear slope) if facing the camera
        sg = -1 if flip else 1
        for (xa, za), (xb, zb) in (((64, 42), (98, 63)), ((150, 64), (176, 42))):
            if not visible(cam, (-sg * (zb - za), 0, xb - xa)):
                continue
            q = []
            for t, yy in ((.1, -31), (.1, 31), (.9, 29), (.9, -29)):
                q.append((fx(xa + (xb - xa) * t), yy, za + (zb - za) * t + oz + .3))
            o += fpoly(cam, q, "win")
        return o
    RAW(sc, glass, ((fx(60) if not flip else fx(180), -36.3, oz + 42), (fx(180) if not flip else fx(60), -36.05, oz + 65)), -2)
    if lamps:
        def lamp(s_):
            o = ""
            sg = -1 if flip else 1
            for front, cls in ((True, "ts1"), (False, "hs2")):
                if not visible(s_.cam, (-sg if front else sg, 0, 0)):
                    continue
                for yy in (-1, 1):
                    q = []
                    for y_, z_ in ((24 * yy, 25), (37 * yy, 25), (36 * yy, 30.5), (24 * yy, 31)):
                        xl = (z_ - 24) * 3 / 7 - .4 if front else CAR_L - (z_ - 16) * .07 + .4
                        q.append((fx(xl), y_, z_ + oz))
                    o += fpoly(s_.cam, q, cls)
            return o
        RAW(sc, lamp, ((ox - .5, -38, oz + 24), (ox + CAR_L + .5, 38, oz + 32)), -3)


# =====================================================================================
# q:engine — engine dynamometer: engine on its stands, flywheel coupled by a drive shaft to the
# dynamometer; the dyno casing is trunnion-mounted and its torque arm presses on a load cell
# =====================================================================================
@picto("engine")
def _():
    zc = 58

    def fn(sc):
        BOX(sc, -150, -62, -14, 312, 124, 14, "pt", dark=1)                      # iron bedplate
        for x in (-124, -62):
            BOX(sc, x, -36, 0, 12, 72, 24, "m")                                 # engine stands
        BOX(sc, -132, -30, 24, 92, 60, 64, "w", ch=4)                           # cylinder block (+ pan)
        BOX(sc, -130, -27, 88, 88, 54, 14, "w", ch=3)                           # cylinder head
        BOX(sc, -126, -21, 102, 80, 42, 9, "dk", ch=6)                          # head cover
        CYL(sc, (-40, 0, zc), (1, 0, 0), 32, 14, "w", seg=32, r1=26)            # bell housing
        CYL(sc, (-26, 0, zc), (1, 0, 0), 12, 6, "m", seg=24)                    # coupling flange
        CYL(sc, (-20, 0, zc), (1, 0, 0), 6, 56, "m", seg=16)                    # drive shaft
        CYL(sc, (36, 0, zc), (1, 0, 0), 12, 6, "m", seg=24)                     # flange
        for x in (42, 142):
            BOX(sc, x, -22, 0, 12, 44, zc - 10, "pt", dark=1)                   # trunnion pedestals
        CYL(sc, (54, 0, zc), (1, 0, 0), 38, 88, "pt", seg=40, dark=1.2)         # dynamometer casing
        BOX(sc, 96, -84, zc - 4, 10, 46, 8, "dk")                               # torque arm
        BOX(sc, 94, -86, 0, 14, 12, 16, "m")                                    # load-cell base
        CYL(sc, (101, -80, 16), (0, 0, 1), 4, zc - 20, "t", seg=12)             # load cell link

        def marks(s_):
            o = ""
            for k in range(4):                                                  # ignition coils
                o += hole3(s_.cam, (-114 + 20 * k, 0, 111.1), (0, 0, 1), 4.5, "m3")
            return o
        RAW(sc, marks, ((-126, -21, 111), (-46, 21, 111.2)), -1)
    s, sc = fit(fn, 28, 22, (24, 30, 300, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (8, 0, zc), (1, 0, 0), 16, 120, 250)
    s += arrow3(cam, (101, -80, zc + 30), (101, -80, zc + 8))
    e, d, t = cam.xy((-86, 0, 111)), cam.xy((98, 0, zc + 38)), cam.xy((101, -80, zc + 30))
    s += lab(e[0], e[1] - 14, "エンジン") + lab(d[0] + 10, d[1] - 14, "動力計")
    s += al(t[0] + 6, t[1] - 2, "トルク", "start")
    r = cam.xy((8, -16, zc + 16))
    s += al(r[0] - 4, r[1] - 12, "回転")
    return s


# =====================================================================================
# q:alignment — wheel alignment: the car stands on floating plates; non-contact laser heads beside
# each wheel read toe and camber, which are then adjusted
# =====================================================================================
@picto("alignment")
def _():
    def fn(sc):
        for y in (-58, 22):
            BOX(sc, -16, y, -10, 232, 36, 10, "pt", dark=1)                     # runway
        for x in (42, 158):
            CYL(sc, (x, -40, -.01), (0, 0, 1), 20, .01 + 1, "m", seg=28)       # floating plate
            BOX(sc, x - 13, -108, -10, 26, 18, 26, "dk", ch=3)                  # laser head on the floor
        car(sc, flip=True)

        def beams(s_):
            o = ""
            for x in (42, 158):
                src = (x, -90, 6)
                for dz in (-11, 0, 11):
                    o += fline(s_.cam, [src, (x - 9, -44.5, 18 + dz)], "laserl")
                    o += fline(s_.cam, [src, (x + 9, -44.5, 18 + dz)], "laserl")
            return o
        RAW(sc, beams, ((20, -90, 6), (180, -45, 32)), -60)
    s, sc = fit(fn, 30, 22, (20, 30, 300, 172), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (158, -37, 2), (0, 0, 1), 30, 270, 350)
    s += arc3(cam, (158, -37, 18), (1, 0, 0), 30, 60, 110)
    a, b, c = cam.xy((186, -50, 0)), cam.xy((158, -48, 46)), cam.xy((42, -108, -10))
    s += al(a[0] + 8, a[1] + 8, "トー", "start") + al(b[0] + 30, b[1] - 6, "キャンバ", "start")
    s += lab(c[0], c[1] + 16, "レーザ計測")
    return s


# =====================================================================================
# q:dampertest — damper dyno: a servo-hydraulic actuator strokes the shock absorber from below while
# a load cell on the crosshead reads the damping force (force-velocity loop on the screen)
# =====================================================================================
@picto("dampertest")
def _():
    def fn(sc):
        BOX(sc, -70, -40, 0, 140, 80, 26, "pt", dark=1, ch=3)                    # base (actuator inside)
        for x in (-52, 52):
            CYL(sc, (x, 0, 26), (0, 0, 1), 6, 150, "m", seg=16)                 # columns
        BOX(sc, -68, -22, 176, 136, 44, 22, "pt", dark=1, ch=3)                 # crosshead
        CYL(sc, (0, 0, 26), (0, 0, 1), 17, 8, "dk", seg=28)                     # actuator piston
        CYL(sc, (0, 0, 34), (0, 0, 1), 8, 14, "m", seg=16)                      # lower adapter
        CYL(sc, (0, 0, 48), (0, 0, 1), 15, 72, "w", seg=32)                     # damper body
        CYL(sc, (0, 0, 120), (0, 0, 1), 9, 4, "w", seg=20)                      # rod guide cap
        CYL(sc, (0, 0, 124), (0, 0, 1), 4, 38, "m", seg=12)                     # piston rod
        CYL(sc, (0, 0, 162), (0, 0, 1), 12, 14, "t", seg=24)                    # load cell
        cabinet(sc, 96, -22, 0, 52, 40, 80, "loop")
    s, sc = fit(fn, -26, 18, (40, 22, 286, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-30, -40, 30), (-30, -40, 70), both=True)
    a, b, c = cam.xy((-30, -40, 50)), cam.xy((58, 0, 168)), cam.xy((-58, 0, 100))
    s += al(a[0] - 8, a[1] + 4, "加振", "end") + lab(b[0] + 6, b[1] + 4, "荷重計", "start")
    s += lab(c[0] - 6, c[1] + 4, "ダンパ", "end")
    return s


# =====================================================================================
# q:flowtest — injector flow test: the injector fires into a graduated vessel / flow meter; the
# delivered quantity and the spray pattern are checked
# =====================================================================================
@picto("flowtest")
def _():
    def fn(sc):
        BOX(sc, -64, -40, 0, 124, 80, 12, "pt", dark=1, ch=3)                    # base
        BOX(sc, -54, 18, 12, 14, 14, 116, "m")                                  # column
        BOX(sc, -54, -16, 128, 72, 34, 14, "m", ch=2)                           # holder arm
        CYL(sc, (0, 0, 96), (0, 0, 1), 7, 32, "w", seg=20)                      # injector body
        BOX(sc, -19, -5, 108, 12, 10, 12, "dk")                                 # connector
        CYL(sc, (0, 0, 86), (0, 0, 1), 3.5, 10, "m", seg=14, r1=4.5)            # nozzle tip
        RAW(sc, lambda s_: glass_cyl(s_.cam, (0, 0, 12), 24, 62, .3), ((-24, -24, 12), (24, 24, 74)), 0)
        cabinet(sc, 76, -24, 0, 50, 40, 76, "step")
    s, sc = fit(fn, -26, 22, (40, 24, 290, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    tip = cam.xy((0, 0, 86))
    for k in range(7):
        a = 2 * PI_ * k / 7
        e = cam.xy((15 * math.cos(a), 15 * math.sin(a), 38))
        s += line(tip[0], tip[1], e[0], e[1], "spray")
    s += cable3(cam, (101, -4, 76), (101, 0, 160), (18, 0, 135))
    s += arrow3(cam, (60, 0, 148), (34, 0, 141))
    a, b, c = cam.xy((-54, 0, 135)), cam.xy((-24, -24, 50)), cam.xy((101, -24, 0))
    s += lab(a[0] - 6, a[1] + 4, "インジェクタ", "end") + al(b[0] - 6, b[1], "噴霧", "end")
    s += lab(c[0] + 6, c[1] + 16, "流量計")
    return s


# =====================================================================================
# q:motortest — motor test bench: motor under test -> torque meter -> load (absorbing) motor
# =====================================================================================
@picto("motortest")
def _():
    zc = 50

    def fn(sc):
        BOX(sc, -140, -56, -12, 290, 112, 12, "pt", dark=1)                     # bedplate
        BOX(sc, -122, -26, 0, 66, 52, 20, "m")                                  # motor stand
        CYL(sc, (-130, 0, zc), (1, 0, 0), 30, 76, "w", seg=36)                  # motor under test
        CYL(sc, (-54, 0, zc), (1, 0, 0), 22, 6, "w", seg=28)                    # end shield
        BOX(sc, -112, -14, zc + 30, 34, 28, 10, "w", ch=2)                      # terminal box
        CYL(sc, (-48, 0, zc), (1, 0, 0), 5, 30, "m", seg=14)                    # shaft
        BOX(sc, -14, -10, 0, 12, 20, zc - 17, "m")                              # torque meter stand
        CYL(sc, (-18, 0, zc), (1, 0, 0), 17, 20, "t", seg=28)                   # torque meter
        CYL(sc, (2, 0, zc), (1, 0, 0), 5, 26, "m", seg=14)                      # shaft
        BOX(sc, 36, -28, 0, 72, 56, zc - 34, "m")                               # dyno stand
        CYL(sc, (28, 0, zc), (1, 0, 0), 34, 90, "pt", seg=36, dark=1.2)         # load motor

    s, sc = fit(fn, 28, 22, (24, 34, 300, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-36, 0, zc), (1, 0, 0), 13, 120, 250)
    a, b, c = cam.xy((-92, 0, zc + 42)), cam.xy((-8, 0, zc + 17)), cam.xy((73, 0, zc + 34))
    s += lab(a[0] - 4, a[1] - 10, "供試モータ") + lab(b[0] + 4, b[1] - 16, "トルク計") + lab(c[0] + 10, c[1] - 12, "負荷モータ")
    r = cam.xy((-36, -13, zc - 6))
    s += al(r[0] - 4, r[1] + 16, "回転")
    return s


# =====================================================================================
# q:nvh — transmission NVH bench: drive motor -> transmission -> load motor; a microphone and an
# accelerometer pick up gear whine for order analysis
# =====================================================================================
@picto("nvh")
def _():
    zc = 52

    def fn(sc):
        BOX(sc, -160, -58, -12, 330, 116, 12, "pt", dark=1)                     # bedplate
        BOX(sc, -146, -24, 0, 52, 48, 22, "m")
        CYL(sc, (-154, 0, zc), (1, 0, 0), 30, 64, "pt", seg=36, dark=1.2)       # drive motor
        CYL(sc, (-90, 0, zc), (1, 0, 0), 5, 26, "m", seg=14)
        CYL(sc, (-64, 0, zc), (1, 0, 0), 40, 22, "w", seg=40)                   # bell housing
        CYL(sc, (-42, 0, zc), (1, 0, 0), 33, 70, "w", seg=36, r1=24)            # gear case
        CYL(sc, (28, 0, zc), (1, 0, 0), 12, 14, "w", seg=20)                    # extension
        BOX(sc, -50, -18, 0, 40, 36, 18, "m")                                   # case support
        BOX(sc, -26, -6, zc + 31, 9, 9, 8, "t")                                 # accelerometer
        CYL(sc, (42, 0, zc), (1, 0, 0), 5, 30, "m", seg=14)
        BOX(sc, 76, -24, 0, 52, 48, 22, "m")
        CYL(sc, (72, 0, zc), (1, 0, 0), 30, 64, "pt", seg=36, dark=1.2)         # load motor
        CYL(sc, (14, -104, -12), (0, 0, 1), 2, 76, "m", seg=10)                 # microphone stand
        CYL(sc, (14, -106, 64), (0, 1, 0), 4.5, 22, "dk", seg=14, bias=-2)      # microphone
    s, sc = fit(fn, 26, 22, (22, 30, 300, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    m, g = cam.xy((14, -84, 64)), cam.xy((-10, -30, zc + 6))
    th = math.atan2(m[1] - g[1], m[0] - g[0])
    for r in (8, 14, 20):
        p0 = (g[0] + r * math.cos(th - .5), g[1] + r * math.sin(th - .5))
        p1 = (g[0] + r * math.cos(th + .5), g[1] + r * math.sin(th + .5))
        s += path("M%s %s A%s %s 0 0 1 %s %s" % (n(p0[0]), n(p0[1]), n(r), n(r), n(p1[0]), n(p1[1])), "wave")
    s += arc3(cam, (-78, 0, zc), (1, 0, 0), 12, 120, 250)
    a, b, c, d = cam.xy((14, -104, 30)), cam.xy((-30, 0, zc + 36)), cam.xy((-122, 0, zc + 30)), cam.xy((104, 0, zc + 30))
    s += lab(a[0] + 6, a[1], "マイク", "start") + lab(b[0] - 6, b[1] - 18, "変速機")
    s += lab(c[0], c[1] - 12, "入力") + lab(d[0], d[1] - 12, "出力")
    return s


# =====================================================================================
# q:aim — headlamp aim tester: a lens unit in front of the lamp catches the beam and measures its
# direction and intensity distribution; it travels on a rail to each lamp
# =====================================================================================
@picto("aim")
def _():
    def fn(sc):
        BOX(sc, 262, -112, -6, 20, 170, 6, "m")                                 # rail
        BOX(sc, 266, -38, 0, 14, 14, 12, "m")
        BOX(sc, 262, -50, 12, 34, 38, 32, "pt", dark=1, ch=3)                   # tester head
        CYL(sc, (262, -31, 28), (-1, 0, 0), 15, 12, "dk", seg=28, cap_mat="m")  # lens barrel
        RAW(sc, lambda s_: hole3(s_.cam, (249.9, -31, 28), (-1, 0, 0), 12, "lens"), ((249.8, -44, 15), (249.9, -18, 41)), -1)
        car(sc, flip=True)

        def beam(s_):
            c = s_.cam
            src = [c.xy((200.5, -31 + dy, 28)) for dy in (-5, 5)]
            return path(P(hull(src + circ3(c, (249.8, -31, 28), (-1, 0, 0), 12, 20))), "beamf")
        RAW(sc, beam, ((200.5, -44, 15), (249.8, -18, 41)), 0)
    s, sc = fit(fn, 30, 20, (20, 34, 300, 174), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (290, -70, -6), (290, -110, -6), both=True)
    a, b, c = cam.xy((279, -31, 44)), cam.xy((228, -31, 40)), cam.xy((290, -112, -6))
    s += lab(a[0], a[1] - 12, "光軸テスタ") + al(b[0] - 6, b[1] - 10, "光軸", "end") + lab(c[0] - 6, c[1] + 6, "移動", "end")
    return s


# =====================================================================================
# q:adas — ADAS aiming: a target board in front of the car calibrates the windscreen camera,
# a corner reflector the front radar
# =====================================================================================
@picto("adas")
def _():
    def fn(sc):
        BOX(sc, 304, -52, -6, 14, 104, 6, "m")                                  # board base
        for y in (-34, 34):
            CYL(sc, (311, y, 0), (0, 0, 1), 2.5, 34, "m", seg=10)
        BOX(sc, 304, -50, 34, 7, 100, 72, "pt", ch=1)                           # target board

        def pattern(s_):
            o = ""
            for i in range(5):
                for j in range(4):
                    if (i + j) % 2:
                        continue
                    y0, z0 = -45 + i * 18, 38 + j * 16
                    o += fpoly(s_.cam, [(303.9, y0, z0), (303.9, y0 + 18, z0), (303.9, y0 + 18, z0 + 16), (303.9, y0, z0 + 16)], "rb")
            return o
        RAW(sc, pattern, ((303.8, -45, 38), (303.9, 45, 102)), -1)
        CYL(sc, (262, 0, -6), (0, 0, 1), 2.5, 20, "m", seg=10)                  # reflector post

        def refl(s_):
            c = s_.cam
            V, A, B, C = (272, 0, 26), (254, 0, 44), (254, -16, 18), (254, 16, 18)
            return fpoly(c, [V, A, B], "ms2") + fpoly(c, [V, B, C], "ms3") + fpoly(c, [V, C, A], "ms1")
        RAW(sc, refl, ((254, -16, 14), (272, 16, 44)), 0)
        car(sc, flip=True)
    s, sc = fit(fn, 32, 20, (20, 26, 300, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    cm = (106, 0, 61)
    for p in ((303, -45, 102), (303, 45, 38)):
        s += fline(cam, [cm, p], "ray")
    s += fline(cam, [(200, 0, 22), (256, 0, 26)], "ray")
    a, b, c = cam.xy((304, -50, 106)), cam.xy((262, 0, -6)), cam.xy(cm)
    s += lab(a[0] + 20, a[1] - 14, "ターゲット") + lab(b[0] + 8, b[1] + 16, "リフレクタ", "start")
    s += al(c[0] - 6, c[1] - 12, "カメラ", "end")
    return s


# =====================================================================================
# q:drum — roller dyno (speed / brake tester): the car's wheels sit between twin rollers in the floor;
# the rollers measure speedometer reading, braking force, ABS and 4WD function
# =====================================================================================
@picto("drum")
def _():
    rz = 18 - math.sqrt(28 ** 2 - 14 ** 2)

    def fn(sc):
        for x0, x1 in ((-20, 18), (66, 134), (182, 220)):
            BOX(sc, x0, -62, -8, x1 - x0, 124, 8, "pt", dark=1)                 # floor
        for xw in (42, 158):
            BOX(sc, xw - 24, -62, -30, 48, 124, 4, "dk")                        # pit bottom
            for dx in (-14, 14):
                CYL(sc, (xw + dx, -58, rz), (0, 1, 0), 10, 116, "m", seg=24)    # twin rollers
        car(sc, flip=True)
    s, sc = fit(fn, 30, 24, (20, 30, 300, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (28, -58.5, rz), (0, -1, 0), 15, 200, 320)
    s += arc3(cam, (158, -44.5, 18), (0, -1, 0), 26, 110, 200)
    a, b = cam.xy((28, -66, rz - 10)), cam.xy((158, -44, 46))
    s += lab(a[0] - 8, a[1] + 14, "ローラ", "end") + al(b[0], b[1] - 16, "速度・制動")
    return s


# =====================================================================================
# q:emission — exhaust gas analysis: a sampling probe in the tailpipe feeds the analyzer
# =====================================================================================
@picto("emission")
def _():
    def fn(sc):
        car(sc, flip=True)
        CYL(sc, (7, -26, 12), (-1, 0, 0), 3.5, 13, "m", seg=14, bias=-3)          # tailpipe
        CYL(sc, (-6, -26, 12), (-1, 0, 0), 5, 14, "dk", seg=14, bias=-3)          # probe holder
        cabinet(sc, -150, -120, 0, 46, 40, 84, "step")

        def hose(s_):
            return cable3(s_.cam, (-20, -26, 12), (-60, -40, 0), (-104, -100, 50))
        RAW(sc, hose, ((-104, -100, 0), (-20, -26, 50)), -5)
    s, sc = fit(fn, 30, 22, (20, 30, 300, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    p = cam.xy((-20, -26, 12))
    for k in range(3):
        s += path("M%s %s c-6 -4 -2 -9 -9 -12" % (n(p[0] - 4 - k * 6), n(p[1] - 6 - k * 2)), "o thin")
    a, b, c = cam.xy((-127, -120, 84)), cam.xy((-20, -26, 12)), cam.xy((-10, -26, 44))
    s += lab(a[0], a[1] - 10, "分析計") + lab(b[0] + 4, b[1] + 22, "採取プローブ", "start")
    s += al(c[0] + 2, c[1] - 6, "排ガス", "start")
    return s


# =====================================================================================
# q:battery — cell tester: spring probes (4-wire) land on both terminals of a prismatic cell and
# the meter reads open-circuit voltage and internal resistance
# =====================================================================================
@picto("battery")
def _():
    def fn(sc):
        BOX(sc, -60, -30, -12, 120, 60, 12, "m", ch=2)                           # tray
        BOX(sc, -44, -15, 0, 88, 30, 96, "alu", ch=2)                           # prismatic cell (Al can)
        BOX(sc, -34, -8, 96, 14, 16, 5, "alu")                                  # + terminal
        BOX(sc, 20, -8, 96, 14, 16, 5, "cu")                                    # - terminal
        RAW(sc, lambda s_: hole3(s_.cam, (0, 0, 96.1), (0, 0, 1), 5, "m2"), ((-5, -5, 96), (5, 5, 96.2)), -1)
        for xc in (-27, 27):
            for dx in (-3, 3):
                CYL(sc, (xc + dx, 0, 101), (0, 0, 1), 1.6, 27, "t", seg=10)     # spring probes
        BOX(sc, -48, -12, 128, 96, 24, 12, "dk", ch=2)                          # probe head
        cabinet(sc, 92, -20, -12, 50, 40, 70, "step")

        def wires(s_):
            return cable3(s_.cam, (40, 0, 140), (90, 0, 170), (117, 0, 58))
        RAW(sc, wires, ((40, 0, 58), (117, 0, 170)), -3)
    s, sc = fit(fn, -26, 22, (36, 22, 292, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-56, -12, 176), (-56, -12, 144))
    a, b, c = cam.xy((-44, -15, 50)), cam.xy((-48, -12, 134)), cam.xy((117, -20, -12))
    s += lab(a[0] - 6, a[1], "電池セル", "end") + lab(b[0] - 18, b[1] + 4, "プローブ", "end")
    s += al(c[0] + 4, c[1] + 16, "電圧・抵抗")
    return s


# =====================================================================================
# q:hipot — insulation / hi-pot test: high voltage between the winding leads and the grounded core
# =====================================================================================
@picto("hipot")
def _():
    def fn(sc):
        BOX(sc, -80, -76, -12, 160, 152, 12, "pt", dark=1, ch=3)                 # insulated bench
        RING2(sc, (0, 0, 0), (0, 0, 1), 64, 44, 58, "w", seg=40)                # stator core
        RING2(sc, (0, 0, 58), (0, 0, 1), 58, 46, 14, "cu", seg=40)              # end winding
        for k in range(3):
            a = math.radians(200 + 22 * k)
            CYL(sc, (52 * math.cos(a), 52 * math.sin(a), 72), (0, 0, 1), 2.4, 20, "cu", seg=10)
        cabinet(sc, 96, -40, -12, 56, 44, 84, "step")

        def leads(s_):
            c = s_.cam
            a = math.radians(222)
            top = (52 * math.cos(a), 52 * math.sin(a), 92)
            return cable3(c, top, (40, -70, 140), (110, -40, 60), "beam") + cable3(c, (64, -8, 20), (90, -20, 0), (110, -40, 40))
        RAW(sc, leads, ((-50, -70, 0), (110, -8, 140)), -60)
    s, sc = fit(fn, -24, 26, (36, 24, 292, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    p = cam.xy((-30, -40, 120))
    s += path("M%s %s l6 -10 l-4 0 l6 -10" % (n(p[0] + 4), n(p[1] + 4)), "hl")
    a, b, c = cam.xy((-64, 0, 30)), cam.xy((-38, -40, 92)), cam.xy((86, -64, 0))
    s += lab(a[0] - 6, a[1], "ステータ", "end") + al(b[0] - 10, b[1] - 12, "高電圧", "end")
    s += lab(c[0] - 2, c[1] + 16, "アース", "end")
    return s


# =====================================================================================
# q:ict — in-circuit tester: the board is pressed down onto a bed of spring probes, each touching a
# test pad, and every component value / joint is measured
# =====================================================================================
@picto("ict")
def _():
    def fn(sc):
        BOX(sc, -84, -54, 0, 168, 108, 22, "pt", dark=1, ch=3)                   # fixture (probe plate)
        BOX(sc, -70, -42, 44, 140, 84, 3, "m")                                  # PCB substrate

        def board(s_):
            c = s_.cam
            return fpoly(c, [(-70, -42, 47.05), (70, -42, 47.05), (70, 42, 47.05), (-70, 42, 47.05)], "pcb")
        RAW(sc, board, ((-70, -42, 47), (70, 42, 47.05)), -1)
        BOX(sc, -46, -20, 47.05, 34, 34, 5, "dk", -2, ch=1)                     # ICs
        BOX(sc, 6, 4, 47.05, 26, 20, 4, "dk", -2)
        BOX(sc, 6, -30, 47.05, 18, 10, 4, "m", -2)
        CYL(sc, (48, 12, 47.05), (0, 0, 1), 7, 12, "alu", -2, seg=18)           # capacitor

        def pins(s_):
            c = s_.cam
            o = ""
            for i in range(7):
                for j in range(4):
                    x, y = -60 + i * 20, -30 + j * 20
                    o += fline(c, [(x, y, 22), (x, y, 44)], "needle")
            return o
        RAW(sc, pins, ((-60, -30, 22), (60, 30, 44)), 0)
        for x in (-60, 60):
            for y in (-34, 34):
                CYL(sc, (x, y, 47.05), (0, 0, 1), 2.5, 68, "m", seg=10)        # press rods
        BOX(sc, -76, -46, 115, 152, 92, 10, "m", ch=2)                          # press plate
    s, sc = fit(fn, -26, 22, (40, 24, 288, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, -46, 150), (0, -46, 128))
    a, b, c = cam.xy((76, 0, 80)), cam.xy((-84, -54, 30)), cam.xy((0, -46, 150))
    s += lab(a[0] + 8, a[1] + 4, "基板", "start") + lab(b[0] - 4, b[1] - 6, "プローブ", "end")
    s += al(c[0] + 10, c[1] + 2, "押え", "start")
    return s


# =====================================================================================
# q:continuity — harness checker: every connector of the harness is plugged into a test socket on
# the layout board; the tester checks continuity / mis-wiring of all circuits
# =====================================================================================
@picto("continuity")
def _():
    ends = [(-110, -44), (-110, 36), (104, -44), (104, 30), (10, -56)]

    def fn(sc):
        BOX(sc, -130, -66, -10, 260, 132, 10, "pt", dark=1, ch=3)                # layout board
        for x, y in ends:
            sx = 18 if abs(x) > 50 else 14
            BOX(sc, x - sx / 2 - (6 if x < -50 else -6 if x > 50 else 0), y - 7, 0, sx, 14, 14, "dk", -1)      # test sockets
        for x in (-60, 0, 60):
            for y in (-10, 10):
                CYL(sc, (x, y, 0), (0, 0, 1), 2, 16, "m", seg=10)               # harness forks
        cabinet(sc, 60, 80, -10, 60, 34, 76, "pulse")

        def harness(s_):
            c = s_.cam
            o = fline(c, [(-80, 0, 8), (70, 0, 8)], "cable3")
            for x, y in ends:
                xm = -80 if x < -50 else 70 if x > 50 else 10
                o += cable3(c, (xm, 0, 8), ((xm + x) / 2, y * .6, 8), (x, y, 7))
            return o
        RAW(sc, harness, ((-112, -56, 6), (106, 36, 10)), -3)
        for x, y in ends:
            off = 8 if x < -50 else -8 if x > 50 else 0
            BOX(sc, x - 6 + off * .4, y - 5, 4, 12, 10, 8, "w", -4)            # harness connectors
    s, sc = fit(fn, -24, 30, (24, 26, 296, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b, c = cam.xy((-20, 0, 10)), cam.xy((104, -50, 0)), cam.xy((90, 80, 66))
    s += lab(a[0], a[1] - 12, "ハーネス") + lab(b[0] - 2, b[1] + 18, "検査コネクタ")
    s += al(c[0] - 34, c[1] - 6, "導通・誤配線", "end")
    return s


# =====================================================================================
# q:semitest — power-semiconductor tester: contact probes on the module's power terminals, a hot
# plate sets the junction temperature, the screen shows the double-pulse switching waveform
# =====================================================================================
@picto("semitest")
def _():
    def fn(sc):
        BOX(sc, -80, -52, 0, 160, 104, 18, "pt", dark=1, ch=3)                   # hot plate stage
        BOX(sc, -54, -32, 18, 108, 64, 4, "cu")                                 # Cu base plate
        BOX(sc, -48, -26, 22, 96, 52, 18, "dk", ch=2)                           # module housing
        for x in (-38, -8, 22):
            BOX(sc, x, -9, 40, 16, 18, 2, "cu")                                 # power terminals
            CYL(sc, (x + 8, 0, 42), (0, 0, 1), 3, 48, "m", seg=12)              # contact probes
        BOX(sc, -50, -16, 90, 100, 32, 12, "cu", ch=2)                          # bus bar head
        cabinet(sc, 100, -28, 0, 56, 44, 80, "pulse")
    s, sc = fit(fn, -26, 24, (36, 26, 292, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b, c = cam.xy((-48, -26, 28)), cam.xy((-50, -16, 96)), cam.xy((128, -28, 0))
    s += lab(a[0] - 6, a[1] + 6, "モジュール", "end") + lab(b[0] - 6, b[1] + 4, "プローブ", "end")
    s += al(c[0], c[1] + 16, "スイッチング")
    return s


# =====================================================================================
# q:env — environmental (temperature / humidity) chamber, door open: ECUs on the shelf are cycled
# hot / cold following the programme on the panel
# =====================================================================================
@picto("env")
def _():
    def fn(sc):
        BOX(sc, 0, 0, 0, 120, 90, 26, "pt", dark=1)                              # machine base
        BOX(sc, 0, 0, 108, 120, 90, 14, "pt", dark=1)                            # top
        BOX(sc, 0, 0, 26, 10, 90, 82, "pt", dark=1)                              # left wall
        BOX(sc, 110, 0, 26, 10, 90, 82, "pt", dark=1)                            # right wall
        BOX(sc, 10, 82, 26, 100, 8, 82, "m")                                    # back wall
        BOX(sc, 10, 6, 64, 100, 76, 3, "m")                                     # shelf
        BOX(sc, 22, 22, 67, 32, 26, 8, "w", ch=1)                               # ECUs
        BOX(sc, 64, 26, 67, 32, 26, 8, "w", ch=1)
        BOX(sc, 34, 30, 26, 32, 26, 8, "w", ch=1)
        BOX(sc, 120, -84, 4, 8, 84, 112, "pt", dark=1, ch=1)                     # door (open 90deg)
        RAW(sc, lambda s_: screen_y(s_.cam, 66, 112, 6, 22, -.05, "cycle"), ((60, -.2, 4), (114, -.05, 24)), -1)
    s, sc = fit(fn, 22, 20, (40, 22, 284, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    p, q = cam.xy((30, 4, 104)), cam.xy((30, 4, 42))
    s += heat(p[0], p[1] + 20, 3, 9, 14)
    for k in range(3):
        s += path("M%s %s l0 10 M%s %s l-4 3 M%s %s l4 3" % (n(q[0] + 10 + 10 * k), n(q[1] - 6), n(q[0] + 10 + 10 * k), n(q[1] + 4),
                                                              n(q[0] + 10 + 10 * k), n(q[1] + 4)), "fo")
    a, b, c = cam.xy((0, 0, 60)), cam.xy((89, 0, 6)), cam.xy((0, 0, 110))
    s += lab(a[0] - 6, a[1] + 4, "製品", "end") + al(b[0], b[1] + 18, "温度サイクル")
    s += lab(c[0] - 6, c[1], "恒温槽", "end")
    return s


# =====================================================================================
# q:calib — camera calibration: the camera on a positioning stage images a calibrated chart; lens
# distortion and optical axis are computed from the pattern
# =====================================================================================
@picto("calib")
def _():
    def fn(sc):
        BOX(sc, -40, -36, 0, 64, 72, 26, "pt", dark=1, ch=3)                     # stage base
        CYL(sc, (-8, 0, 26), (0, 0, 1), 26, 8, "m", seg=36)                     # rotary stage
        BOX(sc, -22, -14, 34, 26, 28, 22, "dk", ch=2)                           # camera module
        CYL(sc, (4, 0, 45), (1, 0, 0), 8, 9, "m", seg=20)                       # lens
        BOX(sc, 190, -70, -6, 14, 140, 6, "m")                                  # chart stand base
        for y in (-50, 50):
            CYL(sc, (197, y, 0), (0, 0, 1), 2.5, 14, "m", seg=10)
        BOX(sc, 194, -72, 14, 6, 144, 96, "pt", ch=1)                           # chart board

        def chart(s_):
            o = ""
            for i in range(8):
                for j in range(5):
                    if (i + j) % 2:
                        continue
                    y0, z0 = -64 + i * 16, 20 + j * 17
                    o += fpoly(s_.cam, [(193.9, y0, z0), (193.9, y0 + 16, z0), (193.9, y0 + 16, z0 + 17), (193.9, y0, z0 + 17)], "rb")
            return o
        RAW(sc, chart, ((193.8, -64, 20), (193.9, 64, 105)), -1)
    s, sc = fit(fn, 30, 20, (24, 30, 298, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    for p in ((193, -64, 105), (193, 64, 105), (193, 64, 20), (193, -64, 20)):
        s += fline(cam, [(13, 0, 45), p], "ray")
    s += arc3(cam, (-8, 0, 30), (0, 0, 1), 34, 200, 290)
    a, b, c = cam.xy((-9, -14, 56)), cam.xy((194, 0, 110)), cam.xy((100, 0, 18))
    s += lab(a[0], a[1] - 12, "カメラ") + lab(b[0], b[1] - 10, "チャート")
    s += al(c[0], c[1] + 26, "歪み・光軸")
    return s


# =====================================================================================
# q:deploy — airbag deployment test: the module on a rigid fixture is fired; a high-speed camera
# records how the cushion unfolds
# =====================================================================================
@picto("deploy")
def _():
    zc = 80

    def fn(sc):
        BOX(sc, -50, 40, 0, 100, 40, 16, "pt", dark=1, ch=3)                     # fixture base
        BOX(sc, -14, 52, 16, 28, 20, zc - 16, "pt", dark=1)                      # post
        CYL(sc, (0, 48, zc), (0, -1, 0), 14, 8, "m", seg=24)                    # module housing
        R = 48

        def bag(s_):
            sc_ = lambda t: .32 + .68 * math.sin(PI_ * (.12 + .8 * t)) ** .7
            return compact(GE.prism(s_.cam, (0, 40, zc), (0, -1, 0), GE.circle_outline(R, 28, 7), 74, "w", scale=sc_, slices=6, smooth=True))
        RAW(sc, bag, ((-R, -34, zc - R), (R, 40, zc + R)), 0)
        BOX(sc, -184, -50, 0, 20, 20, 60, "m")                                  # camera stand
        BOX(sc, -190, -54, 60, 32, 28, 20, "dk", ch=2)                          # high-speed camera
        CYL(sc, (-158, -40, 70), GE._norm((1, .5, .1)), 8, 12, "m", seg=16)
    s, sc = fit(fn, 24, 18, (24, 22, 296, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (56, 30, zc + 30), (56, -30, zc + 30))
    for p in ((-40, -10, zc + 36), (-40, -10, zc - 36)):
        s += fline(cam, [(-147, -35, 71), p], "ray")
    a, b, c = cam.xy((0, -34, zc + 48)), cam.xy((-174, -54, 80)), cam.xy((56, 0, zc + 30))
    s += lab(a[0], a[1] - 10, "エアバッグ") + lab(b[0], b[1] - 10, "高速カメラ") + al(c[0] + 8, c[1] - 4, "展開", "start")
    return s


# =====================================================================================
# q:bnoise — bearing noise / vibration tester: the inner ring is spun on a precision spindle under an
# axial load; a pickup on the outer ring listens for defects (Anderon value)
# =====================================================================================
@picto("bnoise")
def _():
    zc = 50

    def fn(sc):
        BOX(sc, -60, -46, -12, 200, 92, 12, "pt", dark=1)                       # base
        BOX(sc, 50, -26, 0, 74, 52, 20, "m")
        CYL(sc, (42, 0, zc), (1, 0, 0), 30, 86, "pt", seg=32, dark=1.2)         # spindle housing
        CYL(sc, (30, 0, zc), (1, 0, 0), 14, 12, "m", seg=20)                    # spindle nose
        CYL(sc, (-20, 0, zc), (1, 0, 0), 9, 50, "m", seg=16)                    # arbor
        RING2(sc, (-12, 0, zc), (1, 0, 0), 40, 31, 18, "w", -1, seg=40)         # outer ring
        CYL(sc, (-11, 0, zc), (1, 0, 0), 31, 16, "dk", seg=32)                  # gap (cage)
        RING2(sc, (-12, 0, zc), (1, 0, 0), 22, 9, 18, "w", -2, seg=32)          # inner ring

        def balls(s_):
            o = ""
            for k in range(9):
                a = 2 * PI_ * (k + .3) / 9
                o += hole3(s_.cam, (-11.1, 26.5 * math.cos(a), zc + 26.5 * math.sin(a)), (-1, 0, 0), 4.2, "ws1")
            return o
        RAW(sc, balls, ((-11.2, -31, zc - 31), (-11.1, 31, zc + 31)), -3)
        CYL(sc, (-3, 0, zc + 40), (0, 0, 1), 3, 26, "t", seg=12)                # pickup stylus
        BOX(sc, -15, -12, zc + 66, 24, 24, 22, "dk", ch=2)                      # pickup
        cabinet(sc, -120, 0, -12, 44, 40, 70, "wave")
    s, sc = fit(fn, 30, 20, (24, 24, 298, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-16, 0, zc), (1, 0, 0), 15, 200, 320)
    a, b, c = cam.xy((-3, 0, zc + 88)), cam.xy((-12, -40, zc - 30)), cam.xy((-20, -10, zc - 20))
    s += lab(a[0], a[1] - 8, "ピックアップ") + lab(b[0] + 4, b[1] + 22, "軸受")
    s += al(c[0] - 18, c[1] + 18, "回転", "end")
    return s


# =====================================================================================
# q:uniformity — tyre uniformity machine: the tyre spins on a rim, a load wheel presses on the tread
# and its load cells read the force variation (RFV / LFV)
# =====================================================================================
@picto("uniformity")
def _():
    def fn(sc):
        BOX(sc, -90, -80, -40, 260, 160, 14, "pt", dark=1, ch=3)                 # base
        CYL(sc, (0, 0, -26), (0, 0, 1), 12, 26, "m", seg=20)                    # spindle
        RING2(sc, (0, 0, 0), (0, 0, 1), 66, 40, 26, "dk", seg=48)               # tyre
        CYL(sc, (0, 0, 3), (0, 0, 1), 40, 20, "m", seg=40)                      # rim
        CYL(sc, (0, 0, 23), (0, 0, 1), 14, 8, "m", seg=24)                      # chuck / hub
        CYL(sc, (118, 0, -10), (0, 0, 1), 52, 38, "pt", seg=48, dark=1)         # load wheel
        BOX(sc, 140, -24, -26, 34, 48, 16, "m")                                 # carriage
        CYL(sc, (118, 0, 28), (0, 0, 1), 10, 8, "t", seg=18)                    # load cell
    s, sc = fit(fn, -24, 28, (30, 24, 290, 178), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 26), (0, 0, 1), 80, 120, 200)
    s += arrow3(cam, (214, 0, 34), (180, 0, 34))
    a, b, c = cam.xy((-66, 0, 26)), cam.xy((118, 0, 36)), cam.xy((214, 0, 34))
    s += lab(a[0] - 6, a[1], "タイヤ", "end") + lab(b[0], b[1] - 12, "負荷ドラム")
    s += al(c[0] - 6, c[1] - 10, "荷重")
    return s


# =====================================================================================
# q:shower — water-leak (shower) test: the car drives through a booth of high-pressure nozzles,
# the interior is then checked for leaks
# =====================================================================================
@picto("shower")
def _():
    def fn(sc):
        BOX(sc, -20, -70, -8, 240, 140, 8, "m")                                  # grating floor
        for x in (30, 100, 170):
            for y in (-66, 62):
                CYL(sc, (x, y, 0), (0, 0, 1), 3, 100, "m", seg=10, bias=-30 if y < 0 else 30)
            CYL(sc, (x, -66, 100), (0, 1, 0), 3, 132, "m", seg=10, bias=30)
        car(sc, flip=True)
    s, sc = fit(fn, 30, 22, (24, 26, 298, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    for x in (30, 100, 170):
        for z in (30, 60, 90):
            p = cam.xy((x, -63, z))
            q = cam.xy((x + 6, -44, z - 12))
            s += line(p[0], p[1], q[0], q[1], "spray")
        for y in (-30, 0, 30):
            p, q = cam.xy((x, y, 97)), cam.xy((x + 4, y, 74))
            s += line(p[0], p[1], q[0], q[1], "spray")
    a, b = cam.xy((100, 0, 104)), cam.xy((170, -66, 0))
    s += lab(a[0], a[1] - 18, "散水ノズル") + al(b[0] + 6, b[1] + 16, "高圧散水", "start")
    return s


# =====================================================================================
# q:noise — noise & vibration diagnosis: accelerometers on the machine and a microphone feed an
# analyzer; the frequency spectrum shows the abnormal peak
# =====================================================================================
@picto("noise")
def _():
    def fn(sc):
        BOX(sc, -110, -56, -12, 190, 112, 12, "pt", dark=1)                     # test base
        for x in (-90, -10):
            BOX(sc, x, -36, 0, 16, 72, 14, "dk")                                # rubber mounts
        BOX(sc, -96, -30, 14, 96, 60, 62, "w", ch=4)                            # engine block
        BOX(sc, -94, -27, 76, 92, 54, 14, "w", ch=3)                            # head
        BOX(sc, -90, -21, 90, 84, 42, 8, "dk", ch=6)                            # cover
        BOX(sc, -60, -38, 46, 9, 8, 9, "t", -2)                                 # accelerometers
        BOX(sc, -20, -10, 98, 9, 9, 8, "t", -2)
        CYL(sc, (40, -100, -12), (0, 0, 1), 2, 72, "m", seg=10)                # microphone stand
        CYL(sc, (40, -100, 60), GE._norm((-1, .7, 0)), 4.5, 20, "dk", seg=14)
        cabinet(sc, 96, -20, -12, 56, 44, 82, "spec")

        def cables(s_):
            c = s_.cam
            return cable3(c, (-56, -38, 50), (20, -70, 20), (110, -20, 40), "cable") + cable3(c, (-16, -6, 106), (40, -10, 130), (110, -20, 60), "cable")
        RAW(sc, cables, ((-60, -70, 20), (110, -6, 130)), -40)
    s, sc = fit(fn, -24, 22, (24, 24, 296, 176), sh_ry=7, sh_k=.5, ret_scene=True)
    cam = sc.cam
    a, b, c = cam.xy((40, -100, -12)), cam.xy((-96, -30, 50)), cam.xy((124, -20, -12))
    s += lab(a[0], a[1] + 16, "マイク") + lab(b[0] - 8, b[1] + 4, "振動センサ", "end") + al(c[0], c[1] + 16, "周波数分析")
    return s
