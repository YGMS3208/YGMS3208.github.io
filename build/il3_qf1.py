"""v3 shaded-3D principle drawings (q:) for inspection / test equipment: non-destructive testing
(X-ray, CT, UT, eddy current, magnetic particle, penetrant), leak tests, material tests,
balancing machine, functional / load / fatigue test rigs. Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab
from il3_lib import fit, CYL, RING, X, Z, BOX, RAW, hull, circ3, hole3, P, arc3, arrow3

PI = math.pi


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def pv(cam, p):
    x, y = cam.xy(p)
    return x, y


def poly3(cam, pts_, c):
    return path(P([cam.xy(p) for p in pts_]), c)


def wave_mini(x, y, w, h, kind="peak", c="wave"):
    """tiny screen with a trace (one per drawing at most)."""
    s = rect(x, y, w, h, "scrn", 2)
    ps = []
    for i in range(33):
        t = i / 32
        if kind == "peak":
            v = .85 * math.exp(-((t - .12) / .03) ** 2) + .5 * math.exp(-((t - .55) / .04) ** 2) + .7 * math.exp(-((t - .86) / .03) ** 2)
        elif kind == "sine":
            v = .5 + .4 * math.sin(t * 4 * math.pi)
        elif kind == "crimp":
            v = .9 * math.exp(-((t - .55) / .16) ** 4) + .05
        elif kind == "ramp":
            v = .1 + .8 * min(1, t * 1.6)
        else:
            v = .5
        ps.append((x + 4 + (w - 8) * t, y + h - 4 - (h - 8) * v))
    return s + path("M" + " L".join(n(a) + " " + n(b) for a, b in ps), c)


# =====================================================================================
# q:xray / q:ct — X-ray tube (focal spot) -> cone beam through the casting -> flat-panel detector
# with the transmission image (pores show as dark spots); CT turns the part on a rotary table
# =====================================================================================
def xray(ct=False):
    xs, xd, zc = -150, 120, 40                  # focal spot x, detector face x, beam centre height

    def fn(sc):
        # X-ray tube: housing cylinder across the beam, window nose toward +x
        CYL(sc, (xs - 18, -46, zc), (0, 1, 0), 24, 92, "pt", seg=36, dark=1)
        CYL(sc, (xs + 4, 0, zc), (1, 0, 0), 11, 12, "dk", seg=24, bias=-1)
        BOX(sc, xs - 40, -30, -50, 44, 60, 66, "pt", dark=1)                   # tube stand
        # beam cone (drawn behind the part, in front of the detector)
        def cone(s_):
            cam = s_.cam
            f = cam.xy((xs + 16, 0, zc))
            cs = [cam.xy((xd, y, z)) for y in (-58, 58) for z in (zc - 52, zc + 52)]
            return path(P(hull([f] + cs)), "beamf")
        RAW(sc, cone, ((xs + 16, -58, zc - 52), (xd - 1, 58, zc + 52)), 1)
        # flat-panel detector on its stand
        BOX(sc, xd, -66, zc - 62, 12, 132, 124, "dk")
        BOX(sc, xd + 12, -20, -50, 18, 40, 56, "pt", dark=1)

        def img(s_):
            cam = s_.cam
            q = [cam.xy((xd - .3, y, z)) for y, z in ((-50, zc - 46), (50, zc - 46), (50, zc + 46), (-50, zc + 46))]
            o = path(P(q), "xim")
            # projected part silhouette + two pores
            pq = [cam.xy((xd - .4, y, z)) for y, z in ((-34, zc - 30), (34, zc - 30), (34, zc + 22), (-34, zc + 22))]
            o += path(P(pq), "w2")
            o += hole3(cam, (xd - .5, 8, zc - 2), (-1, 0, 0), 5, "xim") + hole3(cam, (xd - .5, -14, zc + 8), (-1, 0, 0), 3, "xim")
            return o
        RAW(sc, img, ((xd - .6, -60, zc - 60), (xd - .2, 60, zc + 60)), -1)
        # work: casting block with bosses, on a stage / rotary table
        if ct:
            CYL(sc, (0, 0, -18), (0, 0, 1), 46, 10, "m", seg=40)
            CYL(sc, (0, 0, -50), (0, 0, 1), 18, 32, "dk", seg=24)
        else:
            BOX(sc, -44, -44, -18, 88, 88, 10, "m")
            BOX(sc, -14, -14, -50, 28, 28, 32, "dk")
        BOX(sc, -30, -30, -8, 60, 60, 58, "w", ch=6)
        CYL(sc, (0, 0, 50), (0, 0, 1), 16, 14, "w", seg=28)

        def bore(s_):
            return hole3(s_.cam, (0, 0, 64.2), (0, 0, 1), 9) + hole3(s_.cam, (-30.2, 0, 20), (-1, 0, 0), 9)
        RAW(sc, bore, ((-30.4, -16, 20), (16, 16, 64.4)), -2)
    s, sc = fit(fn, 24, 16, (22, 26, 298, 166), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a = cam.xy((xs - 18, 0, -50))
    d = cam.xy((xd + 20, 0, -50))
    w = cam.xy((0, 0, 64))
    s += lab(a[0], a[1] + 22, "X線源") + lab(d[0] + 2, d[1] + 22, "検出器")
    if ct:
        s += arc3(cam, (0, 0, -8), (0, 0, 1), 58, 200, 330)
        b = cam.xy((-58, 0, -8))
        s += al(b[0] - 6, b[1] + 4, "回転", "end") + lab(w[0], w[1] - 22, "3D再構成")
    else:
        s += lab(w[0], w[1] - 22, "工作物")
    return s


@picto("xray")
def _():
    return xray(False)


@picto("ct")
def _():
    return xray(True)


# =====================================================================================
# q:balance — rotor on two soft-bearing pedestals (V-rollers), end-drive spindle, vibration
# pickups on the pedestals; correction by drilling at the measured angle
# =====================================================================================
@picto("balance")
def _():
    rs, R, xp = 10, 44, 92

    def fn(sc):
        BOX(sc, -150, -40, -96, 290, 80, 18, "pt", dark=1)                    # bed
        for x in (-xp, xp):
            BOX(sc, x - 13, -24, -78, 26, 48, 50, "pt", ch=4)                   # pedestal (soft bearing)
            BOX(sc, x - 10, -18, -28, 20, 36, 10, "m")                          # roller carrier
            for y in (-11, 11):
                CYL(sc, (x - 7, y, -14), (1, 0, 0), 7, 14, "dk", seg=20)        # V-roller pair
            CYL(sc, (x, -24, -54), (0, -1, 0), 5, 12, "dk", seg=16, bias=-1)   # vibration pickup
        CYL(sc, (-122, 0, 0), (1, 0, 0), rs, 244, "w", seg=24)                 # rotor shaft journals
        CYL(sc, (-52, 0, 0), (1, 0, 0), R, 104, "w", seg=48, bias=-1)          # rotor body
        CYL(sc, (-150, 0, 0), (1, 0, 0), 15, 18, "m", seg=24)                  # end-drive coupling
        BOX(sc, -176, -26, -78, 26, 52, 98, "pt", dark=1)                       # drive head

        def mark(s_):
            o = ""
            for k, th in enumerate((118, 132)):
                a = math.radians(th)
                o += hole3(s_.cam, (12 + k * 14, R * math.cos(a) * 1.002, R * math.sin(a) * 1.002), (0, math.cos(a), math.sin(a)), 6)
            return o
        RAW(sc, mark, ((10, -R, 0), (32, -R + 1, R)), -2)
    s, sc = fit(fn, 22, 20, (22, 30, 298, 168), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-40, 0, 0), (1, 0, 0), R + 8, 40, 150)
    # pickup cables + labels
    for x in (-xp, xp):
        p = cam.xy((x, -36, -54))
        s += path("M%s %s q-4 10 -14 14" % (n(p[0]), n(p[1])), "cable")
    r = cam.xy((-40, 0, R + 8))
    pk = cam.xy((xp, -36, -54))
    h = cam.xy((xp + 14, 0, 30))
    s += al(r[0] - 2, r[1] - 16, "回転") + lab(pk[0] + 12, pk[1] + 30, "振動センサ", "start")
    s += lab(h[0], h[1], "修正穴", "start")
    b = cam.xy((-xp, -24, -40))
    s += lab(b[0] - 18, b[1] + 46, "支持ローラ")
    return s


def ring3(cam, C, A, r, a0, a1, c="wave", seg=16):
    """open 3D circle arc (no head): eddy currents, field lines."""
    E1, E2, _ = GE.frame(A)
    pts_ = [cam.xy(tuple(C[i] + r * (math.cos(math.radians(a0 + (a1 - a0) * k / seg)) * E1[i] +
                                      math.sin(math.radians(a0 + (a1 - a0) * k / seg)) * E2[i]) for i in range(3))) for k in range(seg + 1)]
    return path(P(pts_, False), c)


def face_y(cam, y, x0, x1, z0, z1, c="cut"):
    return poly3(cam, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], c)


# =====================================================================================
# q:ut — contact probe on couplant; the front face is a section: sound beam into the steel,
# echo from a flaw before the back wall; small A-scan (pulse / flaw echo / back-wall echo)
# =====================================================================================
@picto("ut")
def _():
    xp, yf = -30, -46

    def fn(sc):
        BOX(sc, -110, yf, -46, 220, 92, 46, "w")
        CYL(sc, (xp, yf + 15, 0), (0, 0, 1), 16, 2, "fl", seg=28)              # couplant
        CYL(sc, (xp, yf + 15, 2), (0, 0, 1), 15, 30, "dk", seg=28)             # probe
        CYL(sc, (xp, yf + 15, 32), (0, 0, 1), 6, 8, "m", seg=16)               # connector

        def sec(s_):
            cam = s_.cam
            y = yf - .2
            o = face_y(cam, y, -110, 110, -46, 0)
            o += poly3(cam, [(xp - 13, y, 0), (xp + 13, y, 0), (xp + 20, y, -46), (xp - 20, y, -46)], "beamf")
            for r in (9, 17, 25):
                o += path(P([cam.xy((xp + r * math.cos(math.radians(a)), y, -r * math.sin(math.radians(a)) * .9)) for a in range(55, 126, 10)], False), "wave")
            o += hole3(cam, (xp + 8, y, -31), (0, -1, 0), 6, "bg")
            return o
        RAW(sc, sec, ((-110, yf - .4, -46), (110, yf - .2, 0)), -1)
    s, sc = fit(fn, -16, 22, (16, 56, 250, 180), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    c = cam.xy((xp, yf + 15, 40))
    s += path("M%s %s c0 -18 30 -26 54 -22" % (n(c[0]), n(c[1])), "cable")
    s += wave_mini(206, 14, 100, 48, "peak")
    p = cam.xy((xp - 16, yf, 26))
    d = cam.xy((xp + 8, yf, -46))
    s += lab(p[0] - 18, p[1] - 8, "探触子", "end") + lab(d[0] + 18, d[1] + 18, "欠陥のエコー", "start")
    s += lab(256, 76, "エコー波形")
    return s


# =====================================================================================
# q:eddy — encircling coil: the AC field induces eddy currents in the shaft surface; a crack or
# a change of hardened layer alters the coil impedance as the shaft passes through
# =====================================================================================
@picto("eddy")
def _():
    xc = -20

    def fn(sc):
        CYL(sc, (-150, 0, 0), (1, 0, 0), 15, 24, "w", seg=24)
        CYL(sc, (-126, 0, 0), (1, 0, 0), 22, 252, "w", seg=32)
        CYL(sc, (126, 0, 0), (1, 0, 0), 15, 24, "w", seg=24)
        BOX(sc, xc - 18, -30, -84, 36, 60, 30, "pt", dark=1)                  # coil stand
        RING(sc, (xc - 14, 0, 0), (1, 0, 0), 46, 28, 28, "dk", seg=40)          # coil housing
        RING(sc, (xc - 15, 0, 0), (1, 0, 0), 36, 28, 30, "cu", seg=40, bias=-1)  # windings (inner)

        def sf(s_):
            cam = s_.cam
            o = ""
            for x in (xc + 26, xc + 38):
                o += ring3(cam, (x, 0, 0), (1, 0, 0), 22.3, 70, 250)
            o += path(P([cam.xy((76 + d, -22 * math.cos(math.radians(a)), 22 * math.sin(math.radians(a))))
                         for d, a in ((0, 96), (4, 108), (-2, 120), (3, 134), (-1, 148), (2, 160))], False), "crack")
            return o
        RAW(sc, sf, ((xc + 20, -23, -23), (100, -22, 23)), -2)
    s, sc = fit(fn, 20, 20, (20, 34, 300, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (130, 0, 40), (70, 0, 40))
    c = cam.xy((xc, 0, 46))
    e = cam.xy((xc + 32, -22, -22))
    k = cam.xy((80, -18, 26))
    f = cam.xy((100, 0, 40))
    s += lab(c[0] - 6, c[1] - 10, "検出コイル", "end") + al(e[0] + 22, e[1] + 26, "渦電流", "start")
    s += lab(k[0], k[1] - 22, "割れ") + al(f[0] + 34, f[1] + 4, "送り", "start")
    return s


# =====================================================================================
# q:mpi — wet horizontal bench: current through the shaft between copper contact heads makes a
# circular field; fluorescent particles sprayed on gather at the crack, seen under UV light
# =====================================================================================
@picto("mpi")
def _():
    def fn(sc):
        BOX(sc, -176, -36, -64, 352, 72, 16, "pt", dark=1)                    # bed
        BOX(sc, -176, -30, -48, 40, 60, 76, "pt", ch=4)                        # head
        BOX(sc, 136, -30, -48, 40, 60, 76, "pt", ch=4)                         # tail
        CYL(sc, (-136, 0, 0), (1, 0, 0), 24, 8, "cu", seg=28)                  # contact pads
        CYL(sc, (128, 0, 0), (1, 0, 0), 24, 8, "cu", seg=28)
        CYL(sc, (-128, 0, 0), (1, 0, 0), 14, 30, "w", seg=24)
        CYL(sc, (-98, 0, 0), (1, 0, 0), 26, 16, "w", seg=32)
        CYL(sc, (-82, 0, 0), (1, 0, 0), 18, 164, "w", seg=28)
        CYL(sc, (82, 0, 0), (1, 0, 0), 26, 16, "w", seg=32)
        CYL(sc, (98, 0, 0), (1, 0, 0), 14, 30, "w", seg=24)
        BOX(sc, 10, -20, 96, 66, 40, 14, "dk", ch=3)                            # UV lamp
        CYL(sc, (-74, -10, 84), (.5, 0, -.45), 5, 30, "m", seg=16)            # particle-bath nozzle

        def sf(s_):
            cam = s_.cam
            o = ""
            for x in (-56, -36):
                o += ring3(cam, (x, 0, 0), (1, 0, 0), 25, 40, 250)
            pa = [cam.xy((x, -18 * math.cos(math.radians(116)), 18 * math.sin(math.radians(116)))) for x in (34, 56)]
            o += path(P(pa, False), "indic")
            return o
        RAW(sc, sf, ((-60, -19, -26), (60, -18, 26)), -2)
    s, sc = fit(fn, 18, 20, (18, 22, 302, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (20, 66):
        a, b = cam.xy((x, 0, 96)), cam.xy((x * .3 + 31, -8, 18))
        s += line(a[0], a[1], b[0], b[1], "uv")
    s += arrow3(cam, (-100, -30, -36), (60, -30, -36))
    no = cam.xy((-50, -10, 62))
    s += drops(no[0] + 2, no[1] + 6, 4, 14, 26, 70)
    u = cam.xy((76, 0, 110))
    c = cam.xy((-20, -30, -36))
    s += lab(u[0] + 6, u[1] - 4, "UV灯", "start") + al(c[0], c[1] + 24, "通電→磁化")
    s += lab(no[0] - 26, no[1] - 12, "磁粉液", "end")
    k = cam.xy((150, -30, -64))
    s += lab(k[0], k[1] + 22, "割れに集まる")
    return s


# =====================================================================================
# q:pt — penetrant in the crack (section on the front face), white developer on the surface
# draws it out; the fluorescent indication glows under UV light
# =====================================================================================
@picto("pt")
def _():
    xk = 16

    def fn(sc):
        BOX(sc, -40, -50, -70, 80, 100, 14, "pt", dark=1)                    # bench
        BOX(sc, -110, -40, -56, 220, 80, 56, "w")
        BOX(sc, -16, -16, 92, 64, 32, 14, "dk", ch=3)                           # UV lamp

        def sf(s_):
            cam = s_.cam
            y = -40.2
            o = face_y(cam, y, -110, 110, -56, 0)
            o += poly3(cam, [(xk - 2.4, y, 0), (xk + 2.4, y, 0), (xk + 3, y, -12), (xk + 1, y, -32), (xk - .8, y, -14)], "poro")
            dots_ = ""
            for i in range(26):
                for j in range(6):
                    x = -104 + i * 8.2 + (j % 2) * 4
                    yy = -34 + j * 13
                    p = cam.xy((x, yy, .2))
                    dots_ += "M%s %sh1.4v1.2h-1.4z" % (n(p[0]), n(p[1]))
            o += path(dots_, "grain")
            pa = [cam.xy((xk + .8 * math.sin(t), -40 + t * 7, .3)) for t in range(0, 11)]
            o += path(P(pa, False), "indic")
            return o
        RAW(sc, sf, ((-110, -40.4, -56), (110, 40, .4)), -2)
    s, sc = fit(fn, -18, 26, (24, 20, 296, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    for x in (-6, 38):
        a, b = cam.xy((x, 0, 92)), cam.xy((xk + (x - 16) * .3, -6, 2))
        s += line(a[0], a[1], b[0], b[1], "uv")
    u = cam.xy((48, 0, 106))
    k = cam.xy((xk, -40, -32))
    d = cam.xy((-110, 0, 0))
    s += lab(u[0] + 8, u[1] + 2, "UV灯", "start") + lab(k[0] + 34, k[1] + 34, "割れに浸透液", "start")
    s += lab(d[0] + 6, d[1] - 18, "現像剤", "start")
    return s


# =====================================================================================
# q:leak — sealed casting pressurised with air; a differential-pressure sensor compares it with a
# leak-free master over a hold time
# =====================================================================================
@picto("leak")
def _():
    def fn(sc):
        BOX(sc, -90, -54, -16, 180, 108, 16, "pt", dark=1)                    # fixture base
        BOX(sc, -70, -40, 0, 140, 80, 64, "w", ch=5)                           # casting (block)
        BOX(sc, -78, -46, 64, 156, 92, 10, "dk")                                 # sealing head
        for x in (-40, 40):
            CYL(sc, (x, 0, 74), (0, 0, 1), 6, 26, "m", seg=16)                 # cylinder rods
        BOX(sc, -60, -22, 100, 120, 44, 22, "pt", ch=4)                         # press beam
        BOX(sc, -80, -24, 10, 10, 48, 42, "dk")                                 # side seal
        BOX(sc, 110, -30, -16, 56, 60, 70, "pt", ch=4)                          # tester
        CYL(sc, (190, 0, -16), (0, 0, 1), 16, 52, "m", seg=24)                 # master

        def g(s_):
            cam = s_.cam
            o = hole3(cam, (138, -30.2, 32), (0, -1, 0), 15, "m")
            o += hole3(cam, (138, -30.3, 32), (0, -1, 0), 12, "scrn")
            a, b = cam.xy((138, -30.4, 32)), cam.xy((146, -30.4, 40))
            return o + line(a[0], a[1], b[0], b[1], "hl")
        RAW(sc, g, ((122, -30.4, 16), (154, -30.2, 48)), -2)
    s, sc = fit(fn, -20, 22, (16, 34, 304, 168), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    a, b, c = cam.xy((-85, -10, 31)), cam.xy((-85, -10, -40)), cam.xy((110, -10, -10))
    s += path("M%s %s L%s %s L%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1])), "cable")
    m1, m2 = cam.xy((166, 0, 20)), cam.xy((176, 0, 20))
    s += line(m1[0], m1[1], m2[0], m2[1], "cable")
    s += arrow3(cam, (-40, -60, -40), (40, -60, -40))
    t = cam.xy((138, -30, 54))
    m = cam.xy((190, 0, 36))
    w = cam.xy((0, 0, 122))
    p = cam.xy((0, -60, -40))
    s += lab(t[0] + 6, t[1] - 22, "差圧センサ") + lab(m[0] + 18, m[1] + 10, "マスタ", "start")
    s += lab(w[0], w[1] - 8, "ワーク密封") + al(p[0], p[1] + 15, "エア加圧")
    return s


# =====================================================================================
# q:he — vacuum-chamber helium test: the part filled with He sits in an evacuated chamber; He
# escaping through a leak is pumped to the mass-spectrometer leak detector
# =====================================================================================
@picto("he")
def _():
    def fn(sc):
        BOX(sc, -100, -60, -70, 200, 120, 8, "pt", dark=1)                   # floor
        BOX(sc, -100, 54, -62, 200, 6, 112, "pt", dark=1)                    # back wall
        BOX(sc, 94, -60, -62, 6, 114, 112, "pt")                              # right wall
        BOX(sc, -100, -60, -62, 6, 114, 112, "pt")                            # left wall
        BOX(sc, -60, -30, -62, 10, 60, 14, "dk")
        BOX(sc, 40, -30, -62, 10, 60, 14, "dk")
        BOX(sc, -74, -36, -48, 140, 72, 56, "w", ch=12)                        # tank-like part
        CYL(sc, (-30, 0, 8), (0, 0, 1), 9, 26, "m", seg=20)                    # fill adapter
        BOX(sc, 130, -34, -70, 60, 68, 78, "pt", ch=4)                         # leak detector
        CYL(sc, (100, 20, -20), (1, 0, 0), 7, 30, "m", seg=16)                 # pump line
    s, sc = fit(fn, -22, 24, (18, 24, 302, 166), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    o = ""
    for i, (x, y, z) in enumerate(((70, -10, -10), (78, -4, -4), (84, 4, -16), (90, 10, -8), (76, 8, -22), (88, -8, -26))):
        p = cam.xy((x, y, z))
        o += circ(p[0], p[1], 2.4 - (i % 2) * .6, "he")
    s += o
    f = cam.xy((-30, 0, 34))
    s += path("M%s %s c0 -26 -40 -30 -70 -26" % (n(f[0]), n(f[1])), "cable")
    s += wave_mini(*[round(v, 1) for v in (cam.xy((150, -34, 4))[0] - 20, cam.xy((150, -34, 4))[1] - 2)], 40, 24, "ramp")
    c = cam.xy((-100, -60, -70))
    d = cam.xy((160, -34, -70))
    s += lab(f[0] - 56, f[1] - 30, "He充填", "end") + lab(c[0] + 50, c[1] + 22, "真空チャンバ")
    s += lab(d[0] + 4, d[1] + 22, "リーク検出器")
    return s


def Y(sc, y0, L, xz, mat="w", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded along +y from y0."""
    from il3_lib import compact
    loop = [(-p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L, mat, **kw)), ((min(xs), y0, min(zs)), (max(xs), y0 + L, max(zs))), bias)


def diamond(cam, C, r, c="bg"):
    return poly3(cam, [(C[0] - r, C[1], C[2]), (C[0], C[1] - r, C[2]), (C[0] + r, C[1], C[2]), (C[0], C[1] + r, C[2])], c)


# =====================================================================================
# q:hardness — tester frame, diamond pyramid indenter pressed into the specimen on the anvil;
# hardness from the size / depth of the indentation
# =====================================================================================
@picto("hardness")
def _():
    def fn(sc):
        BOX(sc, -70, -56, -120, 140, 116, 34, "pt", dark=1)                   # base
        BOX(sc, -34, 30, -86, 68, 34, 176, "pt", dark=1)                       # column
        BOX(sc, -44, -36, 46, 88, 66, 44, "pt", ch=5)                          # head
        CYL(sc, (0, -6, 16), (0, 0, 1), 9, 30, "m", seg=20)                    # indenter holder
        Z(sc, 0, 16, [(-7, -13), (7, -13), (7, 1), (-7, 1)], "t", scale=lambda t: .06 + .94 * t)
        CYL(sc, (0, -6, -86), (0, 0, 1), 13, 54, "m", seg=20)                  # elevating screw
        CYL(sc, (0, -6, -32), (0, 0, 1), 24, 14, "m", seg=32)                  # anvil
        CYL(sc, (0, -6, -18), (0, 0, 1), 40, 18, "w", seg=40)                  # specimen

        def ind(s_):
            return diamond(s_.cam, (-20, -22, .2), 4.5) + diamond(s_.cam, (22, -18, .2), 4.5) + diamond(s_.cam, (0, -6, .2), 3, "bg")
        RAW(sc, ind, ((-26, -28, 0), (28, 6, .3)), -2)
    s, sc = fit(fn, -24, 24, (40, 12, 280, 182), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (58, -40, 64), (58, -40, 18))
    a = cam.xy((58, -40, 40))
    i = cam.xy((-10, -6, 8))
    w = cam.xy((-40, -6, -10))
    d = cam.xy((22, -18, 0))
    s += al(a[0] + 8, a[1], "荷重", "start") + lab(i[0] - 40, i[1] - 14, "圧子", "end")
    s += lab(w[0] - 12, w[1] + 4, "試験片", "end") + lab(d[0] + 30, d[1] + 22, "くぼみの大きさ", "start")
    return s


# =====================================================================================
# q:micro — metallurgical microscope over a mounted, polished section; the round field of view
# shows grains / case depth
# =====================================================================================
@picto("micro")
def _():
    def fn(sc):
        BOX(sc, -60, -54, -100, 120, 120, 20, "pt", dark=1)                   # base
        BOX(sc, -22, 30, -80, 44, 30, 170, "pt", dark=1)                       # pillar
        BOX(sc, -16, -16, -80, 32, 46, 46, "dk")                               # focus block
        BOX(sc, -52, -44, -34, 104, 74, 8, "m")                                # stage
        CYL(sc, (0, -8, -26), (0, 0, 1), 20, 16, "dk", seg=32)                 # resin mount
        BOX(sc, -34, -34, 50, 68, 64, 34, "pt", ch=5)                          # arm / head
        CYL(sc, (0, -8, 34), (0, 0, 1), 20, 16, "m", seg=32)                   # revolver
        CYL(sc, (0, -8, 4), (0, 0, 1), 6, 30, "t", seg=20, r1=10)              # objective
        CYL(sc, (0, -24, 72), (0, -.55, .83), 9, 46, "dk", seg=20, bias=-1)    # eyepiece tube

        def face(s_):
            cam = s_.cam
            return hole3(cam, (0, -8, -9.8), (0, 0, 1), 17, "w")
        RAW(sc, face, ((-18, -26, -10), (18, 10, -9.6)), -2)
    s, sc = fit(fn, -22, 22, (130, 16, 300, 174), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    # field of view: grains (fixed pseudo-random polygon net)
    cx, cy, r = 64, 92, 46
    s += circ(cx, cy, r + 3, "m") + circ(cx, cy, r, "w")
    d = ""
    pts_ = [(cx - 40, cy - 10), (cx - 18, cy - 30), (cx + 8, cy - 22), (cx + 30, cy - 34), (cx - 26, cy + 10), (cx + 2, cy + 6),
            (cx + 26, cy - 2), (cx - 10, cy + 32), (cx + 18, cy + 30), (cx + 42, cy + 18)]
    for a, b in ((0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (2, 5), (3, 6), (5, 6), (4, 5), (4, 7), (5, 8), (6, 8), (6, 9), (7, 8), (8, 9), (2, 6)):
        d += "M%s %sL%s %s" % (n(pts_[a][0]), n(pts_[a][1]), n(pts_[b][0]), n(pts_[b][1]))
    s += path(d, "o")
    s += path("M%s %sh%s" % (n(cx - 36), n(cy + 16), n(16)), "o thin")
    o = cam.xy((-10, -8, 14))
    t = cam.xy((-20, -44, -34))
    s += lab(cx, cy + r + 20, "断面の組織")
    s += lab(o[0] + 60, o[1] - 2, "対物レンズ", "start") + lab(t[0] + 6, t[1] + 74, "研磨した試料")
    return s


# =====================================================================================
# q:resid — X-ray diffraction: tube and detector on a goniometer arc aimed at one spot on the
# shot-peened surface; the shift of the diffraction peak gives the residual stress
# =====================================================================================
@picto("resid")
def _():
    R0, R1 = 112, 124

    def dirv(a):
        return (math.cos(math.radians(a)), 0, math.sin(math.radians(a)))

    def fn(sc):
        BOX(sc, -100, -46, -36, 200, 92, 36, "w")
        for k in range(6):                                                     # goniometer arc
            a0, a1 = 25 + k * 21.7, 25 + (k + 1) * 21.7
            q = [(R0 * math.cos(math.radians(a)), R0 * math.sin(math.radians(a))) for a in (a0, a1)] + \
                [(R1 * math.cos(math.radians(a)), R1 * math.sin(math.radians(a))) for a in (a1, a0)]
            Y(sc, 14, 10, q, "pt", dark=1)
        BOX(sc, -10, 14, R0 - 6, 20, 10, 12, "pt")
        d = dirv(140)
        CYL(sc, tuple(66 * v for v in d), d, 13, 48, "pt", seg=24)            # X-ray tube
        CYL(sc, tuple(52 * v for v in d), d, 7, 14, "dk", seg=16)              # collimator
        d = dirv(40)
        CYL(sc, tuple(56 * v for v in d), d, 14, 36, "dk", seg=24)             # detector

        def sf(s_):
            cam = s_.cam
            dd = ""
            for i in range(24):
                for j in range(7):
                    p = cam.xy((-96 + i * 8.3 + (j % 2) * 4, -40 + j * 13, .2))
                    dd += "M%s %sh1.3v1.2h-1.3z" % (n(p[0]), n(p[1]))
            return path(dd, "grain")
        RAW(sc, sf, ((-100, -46, 0), (100, 46, .3)), -2)
    s, sc = fit(fn, -14, 18, (30, 16, 290, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    o = cam.xy((0, 0, 0))
    a = cam.xy(tuple(52 * v for v in dirv(140)))
    b = cam.xy(tuple(56 * v for v in dirv(40)))
    s += line(a[0], a[1], o[0], o[1], "beam") + line(o[0], o[1], b[0], b[1], "ray")
    t = cam.xy(tuple(114 * v for v in dirv(140)))
    e = cam.xy(tuple(92 * v for v in dirv(40)))
    w = cam.xy((-100, -46, -36))
    s += lab(t[0] - 10, t[1] + 6, "X線管", "end") + lab(e[0] + 16, e[1] + 6, "検出器", "start")
    s += lab(w[0] + 8, w[1] + 22, "ショット面", "start") + al(o[0] + 40, o[1] + 4, "回折", "start")
    return s


# =====================================================================================
# q:destruct — chisel test: the chisel is driven between two spot-welded sheets; a sound weld
# tears out of the upper sheet as a nugget button
# =====================================================================================
@picto("destruct")
def _():
    t_ = 3.0

    def fn(sc):
        BOX(sc, -130, -50, -t_, 250, 100, t_, "w")                              # lower sheet
        # upper sheet: flat (welded) + bend + peeled-up flange
        cl = [(-130, t_ / 2), (-20, t_ / 2)]
        for k in range(1, 6):
            a = math.radians(6 * k)
            cl.append((-20 + 40 * math.sin(a), t_ / 2 + 40 * (1 - math.cos(a))))
        a = math.radians(30)
        cl.append((cl[-1][0] + 120 * math.cos(a), cl[-1][1] + 120 * math.sin(a)))
        for i in range(len(cl) - 1):
            (x0, z0), (x1, z1) = cl[i], cl[i + 1]
            L = math.hypot(x1 - x0, z1 - z0)
            nx, nz = -(z1 - z0) / L * t_ / 2, (x1 - x0) / L * t_ / 2
            Y(sc, -50, 100, [(x0 - nx, z0 - nz), (x1 - nx, z1 - nz), (x1 + nx, z1 + nz), (x0 + nx, z0 + nz)], "w", bias=-.5)
        CYL(sc, (52, -30, 0), (0, 0, 1), 8, 4, "w", seg=24, dark=1)             # nugget button (torn out)
        x5, z5 = cl[5]
        hc = (x5 + 46 * math.cos(a) - t_ / 2 * math.sin(a), -30, z5 + 46 * math.sin(a) + t_ / 2 * math.cos(a))
        RAW(sc, lambda s_: hole3(s_.cam, hc, (-math.sin(a), 0, math.cos(a)), 8, "bg"), ((hc[0] - 6, -38, hc[2] - 4), (hc[0] + 6, -22, hc[2] + 4)), -3)
        Y(sc, -8, 16, [(28, .2), (62, .2), (62, 14)], "t")                      # chisel wedge
        CYL(sc, (62, 0, 7), (1, 0, 0), 7, 70, "t", seg=20)                    # chisel rod
        CYL(sc, (132, 0, 7), (1, 0, 0), 9, 10, "m", seg=20)                   # striking end

        def mk(s_):
            o = ""
            for y in (-20, 20):
                o += hole3(s_.cam, (-80, y, t_ + .2), (0, 0, 1), 7, "w3")
            return o
        RAW(sc, mk, ((-88, -28, t_), (-72, 28, t_ + .3)), -3)
    s, sc = fit(fn, -24, 26, (20, 22, 300, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (190, 0, 7), (150, 0, 7))
    c = cam.xy((100, -7, 0))
    b = cam.xy((52, -30, 0))
    p = cam.xy((70, 0, 60))
    w = cam.xy((-80, -50, 0))
    s += lab(c[0] + 10, c[1] + 32, "たがね") + lab(b[0] - 12, b[1] + 30, "ナゲット", "end")
    s += al(p[0] - 4, p[1] - 28, "剥離", "end") + lab(w[0] - 4, w[1] + 30, "スポット溶接部")
    return s


# =====================================================================================
# q:clean — the part is rinsed, the liquid is filtered through a membrane; the residue on the
# membrane is weighed and its particles sized (ISO 16232 style)
# =====================================================================================
@picto("clean")
def _():
    def fn(sc):
        CYL(sc, (0, 0, -80), (0, 0, 1), 34, 56, "m", seg=36)                   # filtrate flask
        CYL(sc, (0, 0, -24), (0, 0, 1), 15, 16, "dk", seg=24)                  # filter holder
        CYL(sc, (0, 0, -8), (0, 0, 1), 10, 40, "m", seg=32, r1=46, cap_mat="fl")  # funnel with rinse liquid
        BOX(sc, -38, -28, 66, 76, 56, 38, "w", ch=5)                           # part being rinsed
        CYL(sc, (-80, -10, 128), (.62, 0, -.5), 5, 24, "m", seg=16)            # spray nozzle
        BOX(sc, 90, -40, -80, 90, 80, 34, "pt", ch=4)                          # balance
        CYL(sc, (135, 0, -46), (0, 0, 1), 30, 4, "m", seg=36)                  # pan
        CYL(sc, (135, 0, -42), (0, 0, 1), 24, 1.5, "pt", seg=36)               # membrane

        def sf(s_):
            cam = s_.cam
            o = ""
            for x, y, r in ((128, -8, 2.2), (142, 4, 1.6), (134, 10, 1.2), (146, -10, 2.8), (122, 6, 1.4), (138, -2, 1)):
                o += hole3(cam, (x, y, -40.3), (0, 0, 1), r, "d")
            q = [cam.xy((x, -40.3, z)) for x, z in ((104, -58), (136, -58), (136, -70), (104, -70))]
            return o + path(P(q), "scrn")
        RAW(sc, sf, ((100, -40.4, -70), (160, 30, -40.2)), -2)
    s, sc = fit(fn, -16, 22, (20, 20, 300, 176), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    no = cam.xy((-60, -10, 112))
    s += drops(no[0] + 6, no[1] + 6, 4, 16, 26, 40)
    a = cam.xy((-80, -10, 128))
    f = cam.xy((-15, -15, -16))
    b = cam.xy((135, -40, -80))
    s += lab(a[0] - 4, a[1] - 8, "洗浄液", "middle") + lab(f[0] - 24, f[1] + 4, "ろ過", "end")
    s += lab(b[0], b[1] + 22, "異物の重量・粒径")
    return s


# =====================================================================================
# q:meltq — a sample is taken from the melt and solidified under reduced pressure; the cut
# sample shows hydrogen pores (density index); spectrometer / thermal analysis use similar cups
# =====================================================================================
@picto("meltq")
def _():
    def fn(sc):
        CYL(sc, (-30, 0, -80), (0, 0, 1), 44, 56, "dk", seg=40, cap_mat="h")   # holding furnace / ladle
        CYL(sc, (-20, -14, -8), (0, 0, 1), 12, 12, "m", seg=24, cap_mat="h")     # sample spoon
        CYL(sc, (-8, -14, -2), (1, 0, .5), 3, 70, "m", seg=12)                  # spoon handle
        BOX(sc, 70, -40, -80, 80, 80, 26, "pt", ch=4)                           # RPT base
        CYL(sc, (110, 0, -54), (0, 0, 1), 28, 50, "m", seg=36)                 # vacuum bell
        CYL(sc, (110, 0, -4), (0, 0, 1), 8, 8, "dk", seg=16)
        # cut, solidified sample with pores
        CYL(sc, (180, -10, -80), (0, 0, 1), 18, 26, "w", seg=28)

        def sf(s_):
            cam = s_.cam
            o = hole3(cam, (110, -40.2, -67), (0, -1, 0), 9, "scrn")
            a, b = cam.xy((110, -40.4, -67)), cam.xy((115, -40.4, -61))
            o += line(a[0], a[1], b[0], b[1], "hl")
            for x, y, r in ((174, -14, 2.4), (184, -4, 1.8), (178, -2, 1.4), (188, -14, 1.2), (180, -18, 1)):
                o += hole3(cam, (x, y, -53.8), (0, 0, 1), r, "bg")
            return o
        RAW(sc, sf, ((100, -40.4, -80), (200, 10, -53.6)), -2)
    s, sc = fit(fn, -18, 24, (18, 30, 302, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (30, -14, 46), (84, -6, 46))
    t = cam.xy((84, -6, 46))
    v = cam.xy((110, -40, -80))
    p = cam.xy((180, -10, -80))
    f = cam.xy((-30, -44, -80))
    s += al(t[0] + 8, t[1] + 5, "採取", "start") + lab(v[0], v[1] + 22, "減圧凝固")
    s += lab(p[0] + 4, p[1] + 22, "気泡を見る") + lab(f[0], f[1] + 22, "溶湯")
    return s


# =====================================================================================
# q:receive — steel coil with its strip end; thickness checked with a micrometer, results and
# coating / surface compared with the mill sheet
# =====================================================================================
@picto("receive")
def _():
    def fn(sc):
        BOX(sc, -60, -14, -66, 110, 20, 6, "dk")                                # skid
        RING(sc, (-50, 0, 0), (1, 0, 0), 60, 26, 90, "w", seg=48)              # coil (eye horizontal)
        BOX(sc, -50, -150, -63, 90, 150, 3, "w", bias=.5)                       # strip end
        BOX(sc, -30, -112, -80, 50, 34, 17, "pt", dark=1)                       # support under the strip
        # micrometer at the strip edge (frame in the y-z plane)
        X(sc, -60, 8, [(-176, -90), (-168, -90), (-168, -34), (-176, -34)], "dk")
        X(sc, -60, 8, [(-168, -40), (-140, -40), (-140, -34), (-168, -34)], "dk")
        X(sc, -60, 8, [(-168, -90), (-140, -90), (-140, -84), (-168, -84)], "dk")
        CYL(sc, (-56, -146, -60), (0, 0, 1), 3, 20, "m", seg=12)                # spindle
        CYL(sc, (-56, -146, -84), (0, 0, 1), 3, 21, "m", seg=12)                # anvil
        BOX(sc, 70, -130, -80, 80, 100, 1.5, "pt")                              # mill sheet

        def sf(s_):
            cam = s_.cam
            o = ""
            for r in (36, 46):
                o += path(P(circ3(cam, (-50.2, 0, 0), (-1, 0, 0), r, 32)), "o thin")
            d = ""
            for k in range(6):
                a, b = cam.xy((80, -118 + k * 14, -78.4)), cam.xy((126, -118 + k * 14, -78.4))
                d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
            o += path(d, "o thin")
            q = [cam.xy(p) for p in ((132, -104, -78.4), (136, -110, -78.4), (144, -94, -78.4))]
            return o + path(P(q, False), "a")
        RAW(sc, sf, ((-50.4, -130, -78.5), (150, 46, 46)), -3)
    s, sc = fit(fn, 24, 24, (24, 18, 296, 176), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    c = cam.xy((-5, 0, 60))
    m = cam.xy((-60, -176, -60))
    p = cam.xy((110, -130, -80))
    s += lab(c[0], c[1] - 10, "鋼板コイル") + lab(m[0] - 6, m[1], "板厚", "end")
    s += lab(p[0], p[1] + 22, "ミルシート照合")
    return s


# =====================================================================================
# q:crimpmon — crimp press: the ram drives the crimper onto the terminal barrel on the anvil;
# a load cell records the force curve of every crimp and rejects abnormal waveforms
# =====================================================================================
@picto("crimpmon")
def _():
    def fn(sc):
        BOX(sc, -70, -50, -70, 140, 110, 20, "pt", dark=1)                     # base
        BOX(sc, -50, 34, -50, 100, 26, 190, "pt", dark=1)                      # frame
        BOX(sc, -16, -12, -50, 32, 24, 36, "t")                                 # anvil
        BOX(sc, -10, -36, -14, 20, 60, 6, "gw")                                 # terminal (barrel strip)
        CYL(sc, (0, -100, -6), (0, 1, 0), 6, 72, "dk", seg=20)                 # wire insulation
        CYL(sc, (0, -28, -6), (0, 1, 0), 4, 30, "cu", seg=16)                  # stripped conductor
        BOX(sc, -16, -12, 14, 32, 24, 34, "t")                                  # crimper
        CYL(sc, (0, 0, 48), (0, 0, 1), 16, 14, "dk", seg=28)                   # load cell
        BOX(sc, -30, -24, 62, 60, 58, 70, "pt", ch=4)                           # ram
    s, sc = fit(fn, -26, 20, (30, 30, 210, 182), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (40, -24, 70), (40, -24, 26))
    s += wave_mini(208, 24, 96, 56, "crimp")
    a = cam.xy((40, -24, 48))
    l = cam.xy((-16, 0, 55))
    t = cam.xy((-10, -100, -6))
    s += al(a[0] + 8, a[1], "圧着", "start") + lab(l[0] - 10, l[1], "荷重センサ", "end")
    s += lab(t[0] - 4, t[1] + 30, "電線と端子") + lab(256, 98, "荷重波形")
    return s


# =====================================================================================
# q:slurrymeas — rotational viscometer: the spindle turns in the slurry, the torque gives the
# viscosity (solid content / particle size measured on samples of the same batch)
# =====================================================================================
@picto("slurrymeas")
def _():
    def fn(sc):
        BOX(sc, -80, -60, -110, 160, 120, 14, "pt", dark=1)                    # base
        CYL(sc, (-60, 30, -96), (0, 0, 1), 8, 200, "m", seg=16)                # pillar
        CYL(sc, (0, 0, -96), (0, 0, 1), 44, 74, "m", seg=40, cap_mat="slurry") # beaker with slurry
        CYL(sc, (0, 0, -22), (0, 0, 1), 3, 74, "m", seg=12, bias=-1)           # spindle shaft
        BOX(sc, -72, -26, 52, 104, 52, 46, "pt", ch=6)                          # viscometer head
        CYL(sc, (0, 0, 46), (0, 0, 1), 9, 6, "dk", seg=20)

        def sc_(s_):
            q = [s_.cam.xy(p) for p in ((-40, -26.2, 62), (0, -26.2, 62), (0, -26.2, 86), (-40, -26.2, 86))]
            return path(P(q), "scrn")
        RAW(sc, sc_, ((-40, -26.4, 62), (0, -26.2, 86)), -2)
    s, sc = fit(fn, -22, 26, (60, 16, 260, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, -16), (0, 0, 1), 18, 200, 340)
    r = cam.xy((18, 0, -16))
    b = cam.xy((44, -10, -60))
    h = cam.xy((32, 0, 80))
    s += al(r[0] + 18, r[1] - 2, "回転", "start") + lab(b[0] + 12, b[1] + 4, "スラリー", "start")
    s += lab(h[0] + 12, h[1], "粘度計", "start")
    return s


# =====================================================================================
# q:magcheck — the magnetised rotor turns slowly; a Hall probe at a fixed gap scans the surface
# flux, giving the N/S distribution around the circumference
# =====================================================================================
@picto("magcheck")
def _():
    R = 54

    def fn(sc):
        BOX(sc, -80, -70, -94, 230, 140, 14, "pt", dark=1)                     # base
        CYL(sc, (0, 0, -80), (0, 0, 1), 34, 20, "m", seg=32)                   # rotary spindle
        CYL(sc, (0, 0, -60), (0, 0, 1), R, 76, "w", seg=48)                    # rotor core
        CYL(sc, (0, 0, 16), (0, 0, 1), 13, 40, "w", seg=20)                    # shaft
        BOX(sc, 96, -20, -80, 40, 40, 64, "pt", ch=4)                           # probe stand
        CYL(sc, (96, 0, -24), (-1, 0, 0), 5, 36, "dk", seg=16, bias=-1)         # Hall probe

        def sf(s_):
            cam = s_.cam
            o = ""
            for k in range(8):                                                  # pole boundaries
                a = math.radians(-100 + k * 45)
                p0, p1 = cam.xy((R * math.cos(a), R * math.sin(a), -60)), cam.xy((R * math.cos(a), R * math.sin(a), 16))
                if math.sin(a) < .3:
                    o += line(p0[0], p0[1], p1[0], p1[1], "o thin")
            return o
        RAW(sc, sf, ((-R, -R, -60), (R, 0, 16)), -2)
    s, sc = fit(fn, 16, 24, (20, 22, 220, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 22), (0, 0, 1), 34, 150, 250)
    s += wave_mini(214, 22, 92, 50, "sine")
    p = cam.xy((114, 0, -16))
    r = cam.xy((-R, 0, 0))
    a = cam.xy((-34, 0, 30))
    s += lab(p[0] + 10, p[1] - 30, "ホール素子", "middle") + lab(r[0] - 6, r[1] + 46, "ロータ", "end")
    s += al(a[0] - 6, a[1] - 8, "回転", "end") + lab(260, 90, "表面磁束")
    return s


# =====================================================================================
# q:func — functional test bench: drive motor -> torque meter -> assembled unit under test
# (gearbox / diff / pulley / valve body with its oil supply) -> load; torque, pressure, response
# =====================================================================================
@picto("func")
def _():
    def fn(sc):
        BOX(sc, -200, -54, -70, 380, 108, 14, "pt", dark=1)                    # bed plate
        BOX(sc, -196, -30, -56, 70, 60, 26, "pt")                               # motor foot
        CYL(sc, (-200, 0, 0), (1, 0, 0), 30, 74, "dk", seg=36)                 # drive motor
        CYL(sc, (-126, 0, 0), (1, 0, 0), 6, 116, "m", seg=16)                  # drive shaft
        CYL(sc, (-112, 0, 0), (1, 0, 0), 13, 12, "m", seg=24)                  # coupling
        BOX(sc, -84, -14, -56, 28, 28, 34, "pt")                                # torque meter stand
        CYL(sc, (-86, 0, 0), (1, 0, 0), 24, 32, "pt", seg=36)                  # torque meter
        BOX(sc, -10, -40, -56, 90, 80, 96, "w", ch=10)                          # unit under test
        CYL(sc, (80, 0, 0), (1, 0, 0), 6, 50, "m", seg=16)                     # output shaft
        CYL(sc, (130, 0, 0), (1, 0, 0), 30, 46, "dk", seg=36)                  # load (brake / motor)
        BOX(sc, 134, -30, -56, 38, 60, 26, "pt")
        CYL(sc, (24, -10, 40), (0, 0, 1), 6, 12, "m", seg=16)                  # oil port

    s, sc = fit(fn, 18, 22, (16, 34, 304, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-150, 0, 0), (1, 0, 0), 40, 40, 150)
    o = cam.xy((24, -10, 52))
    s += path("M%s %s c0 -24 40 -30 70 -26" % (n(o[0]), n(o[1])), "cable")
    m = cam.xy((-165, 0, -70))
    t = cam.xy((-70, 0, 24))
    u = cam.xy((35, -40, -70))
    l = cam.xy((153, 0, -70))
    s += lab(m[0], m[1] + 22, "駆動") + lab(t[0], t[1] - 14, "トルク計")
    s += lab(u[0], u[1] + 22, "供試品") + lab(l[0], l[1] + 22, "負荷")
    return s


# =====================================================================================
# q:load — spring load tester: the crosshead compresses the coil spring between platens to a set
# height; the load cell reads the spring force (also pad compression, jack-up load)
# =====================================================================================
@picto("load")
def _():
    def fn(sc):
        BOX(sc, -90, -50, -104, 180, 100, 24, "pt", dark=1)                    # base
        for x in (-70, 70):
            CYL(sc, (x, 0, -80), (0, 0, 1), 7, 214, "m", seg=16)               # columns
        BOX(sc, -84, -18, 104, 168, 36, 26, "pt", ch=4)                         # crosshead
        CYL(sc, (0, 0, 84), (0, 0, 1), 15, 20, "dk", seg=28)                   # load cell
        CYL(sc, (0, 0, 74), (0, 0, 1), 44, 10, "m", seg=40)                    # upper platen
        CYL(sc, (0, 0, -80), (0, 0, 1), 44, 10, "m", seg=40)                   # lower platen

        def spring(s_):
            from il3_chassis import tube_chunks
            cam = s_.cam
            seg, turns, R, r, z0, z1 = 16, 5, 30, 5.6, -70, 74
            N = int(turns * seg)
            pts_ = [(R * math.cos(2 * PI * i / seg), R * math.sin(2 * PI * i / seg), z0 + r + (z1 - z0 - 2 * r) * i / N) for i in range(N + 1)]
            D = cam.D
            ch = tube_chunks(cam, pts_, r, "w", split=lambda i: GE._dot((pts_[i][0], pts_[i][1], 0), D) < 0,
                             caps=True, nb=3, uniform=True, dark=.1)
            return "".join(v for _, v in sorted(ch, key=lambda c: -c[0]))
        RAW(sc, spring, ((-36, -36, -70), (36, 36, 74)), 0)
    s, sc = fit(fn, -20, 18, (50, 14, 250, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (100, -18, 130), (100, -18, 84))
    a = cam.xy((100, -18, 108))
    l = cam.xy((-15, 0, 94))
    sp = cam.xy((-36, 0, 0))
    s += al(a[0] + 8, a[1], "圧縮", "start") + lab(l[0] - 40, l[1] + 4, "ロードセル", "end")
    s += lab(sp[0] - 24, sp[1] + 4, "ばね", "end")
    return s


# =====================================================================================
# q:fatigue — servo-hydraulic fatigue frame: the actuator in the base pushes and pulls the
# specimen held between grips; the load cell under the crosshead measures the cyclic load
# =====================================================================================
@picto("fatigue")
def _():
    def fn(sc):
        BOX(sc, -96, -50, -120, 192, 100, 40, "pt", dark=1)                    # base (actuator inside)
        for x in (-70, 70):
            CYL(sc, (x, 0, -80), (0, 0, 1), 8, 216, "m", seg=16)               # columns
        BOX(sc, -88, -22, 112, 176, 44, 30, "pt", ch=4)                         # crosshead
        CYL(sc, (0, 0, 92), (0, 0, 1), 15, 20, "dk", seg=28)                   # load cell
        BOX(sc, -16, -16, 60, 32, 32, 32, "dk", ch=3)                           # upper grip
        CYL(sc, (0, 0, 22), (0, 0, 1), 7, 38, "w", seg=20)                     # specimen gauge
        CYL(sc, (0, 0, 12), (0, 0, 1), 11, 10, "w", seg=20, r1=7)
        CYL(sc, (0, 0, -10), (0, 0, 1), 11, 22, "w", seg=20)
        BOX(sc, -16, -16, -42, 32, 32, 32, "dk", ch=3)                          # lower grip
        CYL(sc, (0, 0, -80), (0, 0, 1), 9, 38, "m", seg=20)                    # actuator rod
    s, sc = fit(fn, -20, 18, (40, 14, 220, 182), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (34, -20, -70), (34, -20, -20), both=True)
    s += wave_mini(220, 26, 88, 44, "sine")
    a = cam.xy((34, -20, -45))
    l = cam.xy((-15, 0, 102))
    w = cam.xy((-11, 0, 0))
    b = cam.xy((0, -50, -120))
    s += al(a[0] + 10, a[1] + 4, "繰返し荷重", "start") + lab(l[0] - 64, l[1] + 4, "ロードセル", "end")
    s += lab(w[0] - 64, w[1] + 4, "試験片", "end") + lab(b[0], b[1] + 15, "油圧サーボ")
    return s
