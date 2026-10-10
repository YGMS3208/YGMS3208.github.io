"""v3 principle drawings (shaded 3D style), team qd1: welding & joining, and the first half of
plastics / rubber / glass forming. Overrides the older flat drawings in il_pictos.py."""
import math
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def half_disc(r, seg=12, y0=0.0):
    """(y, z) outline of the back half (y >= y0) of a disc: for cutaway prisms along x."""
    return banded(arc(y0, 0, r, -90, 90, seg), 2)


def shell_x(sc, x0, L, ro, ri, mat="m", n_=4, bias=0.0, **kw):
    """back half of a tube along x (cut at y=0), split into convex sectors."""
    for k in range(n_):
        a0, a1 = -90 + 180 * k / n_, -90 + 180 * (k + 1) / n_
        out = arc(0, 0, ro, a0, a1, 4)
        inn = [(ri * math.cos(math.radians(a1)), ri * math.sin(math.radians(a1))), (ri * math.cos(math.radians(a0)), ri * math.sin(math.radians(a0)))]
        X(sc, x0, L, [(p[0], p[1], i // 2 if i < 5 else 10 + i) for i, p in enumerate(out + inn)], mat, bias, smooth=False)


def face_y(cam, pts_xz, y=-0.15, c="h"):
    """flat polygon drawn on a cut face at y (points given as (x, z))."""
    return path(P([cam.xy((x, y, z)) for x, z in pts_xz]), c)


# =====================================================================================
# q:spot — resistance spot welding: a servo C-gun clamps two steel sheets between copper
# electrode tips and passes a large current; the spot melts into a nugget
# =====================================================================================
@picto("spot")
def _():
    def fn(sc):
        BOX(sc, -150, -26, -4, 180, 52, 4, "w")                             # lower sheet
        BOX(sc, -150, -20, 0, 180, 40, 4, "w")                              # upper sheet (flange)
        CYL(sc, (0, 0, 4), (0, 0, 1), 4.5, 10, "cu", seg=24, r1=8)          # upper cap tip
        CYL(sc, (0, 0, 14), (0, 0, 1), 8, 36, "cu", seg=24)                 # upper shank
        CYL(sc, (0, 0, 50), (0, 0, 1), 12, 16, "dk", seg=24)                # holder / servo rod end
        BOX(sc, -18, -14, 66, 152, 28, 18, "pt", ch=3)                      # upper arm
        CYL(sc, (0, 0, 84), (0, 0, 1), 19, 38, "pt", seg=28, dark=.3)       # servo actuator
        CYL(sc, (0, 0, 122), (0, 0, 1), 13, 12, "dk", seg=24)               # motor
        BOX(sc, 134, -14, -84, 22, 28, 168, "pt", dark=1, ch=3)             # C-frame back
        BOX(sc, -18, -14, -84, 152, 28, 18, "pt", dark=1, ch=3)             # lower arm
        CYL(sc, (0, 0, -66), (0, 0, 1), 12, 16, "dk", seg=24)
        CYL(sc, (0, 0, -50), (0, 0, 1), 8, 36, "cu", seg=24)                # lower shank
        CYL(sc, (0, 0, -14), (0, 0, 1), 8, 10, "cu", seg=24, r1=4.5)        # lower cap tip

        def marks(s_):
            o = hole3(s_.cam, (0, 0, 4.05), (0, 0, 1), 9, "h")              # heated spot under the tip
            for x in (-45, -90, -135):                                      # earlier weld spots
                o += hole3(s_.cam, (x, 0, 4.05), (0, 0, 1), 6, "w3") + hole3(s_.cam, (x, 0, 4.1), (0, 0, 1), 3.6, "w2")
            return o
        RAW(sc, marks, ((-150, -20, 4), (30, 20, 4.2)), -1)
    s, sc = fit(fn, 25, 16, (30, 16, 290, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-36, 0, 62), (-36, 0, 22))
    a = cam.xy((-36, 0, 50))
    s += al(a[0] - 6, a[1], "加圧", "end")
    e = cam.xy((12, 0, 26))
    s += lab(e[0] + 4, e[1], "電極チップ", "start")
    w = cam.xy((-150, -26, -4))
    s += lab(w[0] + 6, w[1] + 22, "鋼板2枚", "start")
    p = cam.xy((-90, 20, 4))
    s += lab(p[0], p[1] - 10, "打点", "middle")
    return s


# =====================================================================================
# q:injection — injection moulding machine, cut away at the centre plane: the screw melts
# pellets from the hopper and rams the melt through the nozzle into the clamped mould
# =====================================================================================
@picto("injection")
def _():
    def fn(sc):
        BOX(sc, -250, -20, -22, 40, 40, 44, "dk", ch=3)                      # injection drive
        shell_x(sc, -210, 196, 24, 15, "m", bias=4)                          # barrel (back half)
        CYL(sc, (-14, 0, 0), (1, 0, 0), 13, 14, "m", seg=24, r1=6)          # nozzle
        # screw: root + flights (tilted discs read as a helix), drawn far (+x) to near
        CYL(sc, (-206, 0, 0), (1, 0, 0), 8, 166, "w", seg=20)
        for k in range(9):
            x = -194 + k * 17
            CYL(sc, (x, 0, 0), (1, 0, .18), 14.5, 3, "w", seg=20, bands=8, bias=-1, lines=False)
        CYL(sc, (-40, 0, 0), (1, 0, 0), 12, 11, "w", seg=24, r1=3)          # screw tip
        X(sc, -29, 15, half_disc(15), "h", bias=2)                           # metered melt
        # hopper with pellets
        CYL(sc, (-180, 0, 24), (0, 0, 1), 9, 34, "pt", seg=28, r1=24, dark=.4)
        # fixed platen, mould halves, moving platen, clamp cylinder: back halves (cut at y=0)
        BOX(sc, 0, 0, -66, 18, 66, 132, "pt", dark=1, cap_mat="pt")
        BOX(sc, 18, 0, -44, 44, 44, 88, "t")
        BOX(sc, 62, 0, -44, 44, 44, 88, "t", bias=.5)
        BOX(sc, 106, 0, -66, 18, 66, 132, "pt", dark=1)
        X(sc, 124, 42, half_disc(28), "dk", smooth=True)
        X(sc, 166, 10, half_disc(32), "dk", smooth=True)
        for z in (-52, 52):                                                  # tie bars (rear pair)
            CYL(sc, (-6, 52, z), (1, 0, 0), 6, 182, "m", seg=12, bands=6)

        def cav(s_):
            c = s_.cam
            o = face_y(c, [(18, -2.5), (58, -2.5), (58, 2.5), (18, 2.5)])                       # sprue
            o += face_y(c, [(56, -32), (86, -32), (86, -26), (62, -26), (62, 26), (86, 26), (86, 32), (56, 32)])
            o += path(P([c.xy((62, -.2, -44)), c.xy((62, -.2, 44))], False), "o thin")             # parting line
            for x, y in ((-186, -6), (-176, 4), (-182, 8), (-172, -8), (-188, 2), (-178, -2)):
                o += hole3(c, (x, y, 58.2), (0, 0, 1), 2.6, "w3")
            return o
        RAW(sc, cav, ((-200, -1, -44), (90, 0, 60)), -6)
    s, sc = fit(fn, 14, 18, (16, 30, 304, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-120, 0, 0), (1, 0, 0), 20, 200, 320)
    s += arrow3(cam, (-150, 0, 52), (-80, 0, 52))
    s += arrow3(cam, (186, 0, 84), (136, 0, 84))
    a = cam.xy((-115, 0, 56))
    s += al(a[0], a[1] - 8, "射出")
    b = cam.xy((161, 0, 84))
    s += al(min(b[0], 282), b[1] - 9, "型締め")
    m = cam.xy((62, 22, 44))
    s += lab(m[0], m[1] - 10, "金型")
    w = cam.xy((-130, 0, -26))
    s += lab(w[0], w[1] + 22, "スクリュ")
    return s


def _add(p, u, k):
    return tuple(p[i] + u[i] * k for i in range(3))


def cone2d(cam, C, A, r, apex, seg=16):
    """screen hull of a cone (base circle centre C, normal A, radius r) with its apex: beams, sprays."""
    return P(hull(circ3(cam, C, A, r, seg) + [cam.xy(apex)]))


# =====================================================================================
# q:arc — arc welding robot: the torch on the robot wrist feeds wire into an arc that melts
# the wire and the plates; a fillet bead is laid along the T-joint as the torch travels
# =====================================================================================
@picto("arc")
def _():
    u = GE._norm((-.3, -.62, .72))                 # torch axis (from the arc up to the wrist)
    v = GE._norm((-.8, .25, .55))                  # forearm direction
    C = (0, -2, 2)                                 # arc point at the joint root
    N = _add(C, u, 13)                             # nozzle end

    def fn(sc):
        BOX(sc, -150, -72, -12, 240, 92, 12, "w")                           # flange plate
        BOX(sc, -150, 0, 0, 240, 12, 72, "w", dark=.2)                      # web plate (T-joint)
        bead = banded(hull(arc(0, 0, 11, 90, 180, 6) + [(0, 0)]), 2)
        X(sc, -150, 138, bead, "w", dark=.7, smooth=True)                   # finished fillet bead
        X(sc, -12, 10, bead, "h", smooth=True)                              # molten pool
        CYL(sc, N, u, 5, 22, "cu", seg=24, r1=8.5)                         # gas nozzle
        CYL(sc, _add(N, u, 22), u, 6.5, 46, "dk", seg=20)                  # torch body
        W = _add(N, u, 68)
        CYL(sc, W, u, 15, 24, "pt", seg=28)                                 # wrist flange
        CYL(sc, _add(_add(W, u, 12), v, 12), v, 13, 70, "pt", seg=24, dark=.4)   # forearm
    s, sc = fit(fn, -24, 22, (30, 22, 290, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy(C), cam.xy(_add(N, u, 2))
    s += line(a[0], a[1], b[0], b[1], "o")                                 # wire stick-out
    s += circ(a[0], a[1], 5, "flash") + sparks(a[0], a[1], 11, 5, -170, -10)
    s += arrow3(cam, (20, -54, 0), (80, -54, 0))
    t = cam.xy((50, -54, 0))
    s += al(t[0], t[1] + 18, "溶接方向")
    k = cam.xy((-110, -72, -12))
    s += lab(k[0], k[1] + 18, "ビード")
    o = cam.xy(_add(_add(_add(N, u, 80), v, 82), (0, 0, 1), 14))
    s += lab(o[0], o[1] - 4, "トーチ")
    return s


# =====================================================================================
# q:projection — projection welding of a weld nut: the current flows only through the small
# projections on the nut, which melt and collapse as the upper electrode presses down
# =====================================================================================
@picto("projection")
def _():
    gap = 16

    def fn(sc):
        CYL(sc, (0, 0, -48), (0, 0, 1), 30, 44, "cu", seg=36)              # lower electrode
        BOX(sc, -80, -48, -4, 160, 96, 4, "w")                              # steel sheet
        hexo = [(24 * math.cos(math.radians(30 + 60 * k)), 24 * math.sin(math.radians(30 + 60 * k)), k) for k in range(6)]
        sc.add(compact(GE.prism(sc.cam, (0, 0, 5), (0, 0, 1), hexo, 16, "w", holes=[GE.circle_outline(11, 24, 6)])),
               ((-24, -24, 5), (24, 24, 21)))                           # weld nut
        for k in range(3):                                                  # projections
            t = math.radians(-90 + 120 * k)
            CYL(sc, (16 * math.cos(t), 16 * math.sin(t), 0), (0, 0, 1), 1.6, 5, "w", seg=12, r1=4.6, lines=False)
        z0 = 21 + gap
        CYL(sc, (0, 0, z0), (0, 0, 1), 27, 34, "cu", seg=36)               # upper electrode
        CYL(sc, (0, 0, z0 + 34), (0, 0, 1), 30, 14, "dk", seg=36)          # holder
        CYL(sc, (0, 0, z0 + 48), (0, 0, 1), 13, 34, "m", seg=24)           # ram
    s, sc = fit(fn, -28, 13, (40, 18, 280, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-46, 0, 80), (-46, 0, 46))
    a = cam.xy((-46, 0, 64))
    s += al(a[0] - 6, a[1], "加圧", "end")
    e = cam.xy((28, 0, 56))
    s += lab(e[0] + 8, e[1], "電極", "start")
    n_ = cam.xy((26, -6, 14))
    s += lab(n_[0] + 8, n_[1] + 4, "ナット", "start")
    p = cam.xy((-16, -12, 0))
    s += lab(p[0] - 14, p[1] + 26, "鋼板", "end")
    return s


# =====================================================================================
# q:laserweld — laser welding: the focused beam from the laser head melts a narrow keyhole
# along the butt joint of two sheets (here a tailored blank of two thicknesses)
# =====================================================================================
@picto("laserweld")
def _():
    def fn(sc):
        BOX(sc, -130, -64, -6, 200, 64, 6, "w")                              # thick sheet
        BOX(sc, -130, 0, -6, 200, 64, 4, "w")                                # thin sheet
        bd = banded(hull([(-4, 0), (4, -2), (4, -.6), (2.4, .9), (-.8, 1.3), (-3.2, .7)]), 2)
        X(sc, -130, 124, bd, "w", dark=.6, smooth=True)                     # weld bead
        X(sc, -6, 6, bd, "h", smooth=True)                                  # melt at the keyhole
        CYL(sc, (0, 0, 56), (0, 0, 1), 7, 16, "dk", seg=24, r1=13)          # focusing nozzle
        BOX(sc, -28, -24, 72, 56, 48, 44, "pt", ch=5)                        # laser head (optics)
        CYL(sc, (0, 0, 116), (0, 0, 1), 8, 18, "dk", seg=20)                # fibre connector
    s, sc = fit(fn, -26, 24, (36, 20, 286, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += path(cone2d(cam, (0, 0, 56), (0, 0, 1), 6.5, (0, 0, .4)), "beamf")
    s += line(*cam.xy((0, 0, 56)), *cam.xy((0, 0, .4)), "laserl")
    f = cam.xy((0, 0, .4))
    s += circ(f[0], f[1], 4.5, "flash")
    s += arrow3(cam, (18, -76, -6), (68, -76, -6))
    t = cam.xy((43, -76, -6))
    s += al(t[0], t[1] + 18, "溶接方向")
    h = cam.xy((-28, -24, 96))
    s += lab(h[0] - 6, h[1], "レーザヘッド", "end")
    b = cam.xy((0, 0, 28))
    s += lab(b[0] + 12, b[1] + 4, "レーザ", "start")
    k = cam.xy((-100, -64, -6))
    s += lab(k[0], k[1] + 18, "ビード（板厚違い）")
    return s


# =====================================================================================
# q:ebw — electron beam welding: in a vacuum chamber the gun fires a focused beam into the
# joint while the part turns under it (deep, narrow circumferential weld)
# =====================================================================================
@picto("ebw")
def _():
    zc = 40                                        # work axis height

    def fn(sc):
        BOX(sc, -150, -64, -22, 280, 128, 14, "m", dark=.4)                # chamber floor
        BOX(sc, -150, 64, -22, 280, 12, 186, "m", dark=.9)                 # back wall
        BOX(sc, -150, -26, 150, 280, 102, 14, "m", dark=.2)                # roof (front cut away)
        CYL(sc, (0, 0, 164), (0, 0, 1), 22, 46, "pt", seg=32)              # gun column
        CYL(sc, (0, 0, 210), (0, 0, 1), 12, 18, "dk", seg=20)              # HV insulator / cable
        CYL(sc, (0, 0, 132), (0, 0, 1), 15, 18, "cu", seg=28)              # focusing coil
        BOX(sc, -140, -30, -8, 40, 60, 24, "pt", dark=.6)                   # headstock base
        CYL(sc, (-128, 0, zc), (1, 0, 0), 28, 22, "dk", seg=32)            # rotating chuck
        CYL(sc, (-106, 0, zc), (1, 0, 0), 11, 106, "w", seg=28)            # shaft
        CYL(sc, (0, 0, zc), (1, 0, 0), 20, 26, "w", seg=32)                # wheel hub
        CYL(sc, (26, 0, zc), (1, 0, 0), 40, 12, "w", seg=40, dark=.2)      # wheel disc
    s, sc = fit(fn, 22, 16, (30, 14, 290, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((0, 0, 132)), cam.xy((0, 0, zc + 12))
    s += line(a[0], a[1], b[0], b[1], "ebeam")
    s += circ(b[0], b[1], 4, "flash")
    s += arc3(cam, (-60, 0, zc), (1, 0, 0), 20, 30, 160)
    r = cam.xy((-60, -14, zc - 24))
    s += al(r[0], r[1] + 16, "回転")
    g = cam.xy((22, 0, 190))
    s += lab(g[0] + 6, g[1], "電子銃", "start")
    e = cam.xy((0, 0, 100))
    s += lab(e[0] + 10, e[1], "電子ビーム", "start")
    v = cam.xy((-150, 64, 140))
    s += lab(v[0] + 8, v[1] + 4, "真空室", "start")
    return s


# =====================================================================================
# q:friction — friction welding: one bar spins in the chuck, the other is pushed against it;
# friction heats the faces, upset pressure forges them together and squeezes out a flash ring
# =====================================================================================
@picto("friction")
def _():
    def fn(sc):
        BOX(sc, -196, -42, -52, 40, 84, 104, "pt", dark=1, ch=4)            # spindle head
        CYL(sc, (-156, 0, 0), (1, 0, 0), 34, 28, "m", seg=36)               # rotating chuck
        CYL(sc, (-128, 0, 0), (1, 0, 0), 14, 112, "w", seg=28)              # rotating bar
        CYL(sc, (-16, 0, 0), (1, 0, 0), 14, 11, "h", seg=28)                # heated zone
        CYL(sc, (-5, 0, 0), (1, 0, 0), 14, 5, "h", seg=28, r1=21)           # flash (curls out)
        CYL(sc, (0, 0, 0), (1, 0, 0), 21, 5, "h", seg=28, r1=14)
        CYL(sc, (5, 0, 0), (1, 0, 0), 14, 11, "h", seg=28)
        CYL(sc, (16, 0, 0), (1, 0, 0), 12, 100, "w", seg=28, dark=.15)      # stationary bar (other material)
        BOX(sc, 116, -34, -34, 36, 68, 68, "m", ch=4)                       # clamp (no rotation)
        BOX(sc, 152, -42, -52, 40, 84, 104, "pt", dark=1, ch=4)             # upset slide
    s, sc = fit(fn, 20, 18, (24, 26, 296, 168), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-80, 0, 0), (1, 0, 0), 24, 30, 160)
    s += arrow3(cam, (104, 0, 44), (54, 0, 44))
    r = cam.xy((-80, 0, 26))
    s += al(r[0], r[1] - 8, "回転")
    p = cam.xy((79, 0, 44))
    s += al(p[0], p[1] - 9, "加圧")
    f = cam.xy((0, -21, -14))
    s += lab(f[0], f[1] + 24, "バリ（摩擦熱）")
    return s


# =====================================================================================
# q:fsw — friction stir welding: the spinning tool's pin is plunged into the butt joint and
# the shoulder rides on the surface; the stirred metal joins without melting
# (the near plate is cut at the tool to show the pin and the stirred zone)
# =====================================================================================
@picto("fsw")
def _():
    def fn(sc):
        BOX(sc, -140, -66, -22, 250, 132, 12, "m", dark=.5)                 # backing plate
        BOX(sc, -140, -60, -10, 140, 60, 10, "alu")                         # near plate (cut at x=0)
        BOX(sc, -140, 0, -10, 240, 60, 10, "alu")                           # far plate
        CYL(sc, (0, 0, -8), (0, 0, 1), 3.2, 8, "t", seg=16, r1=4.6, bias=-2)  # pin (probe)
        CYL(sc, (0, 0, 0), (0, 0, 1), 15, 34, "t", seg=32)                  # shoulder + tool body
        CYL(sc, (0, 0, 34), (0, 0, 1), 22, 22, "dk", seg=32)                # holder
        CYL(sc, (0, 0, 56), (0, 0, 1), 28, 34, "pt", seg=36)                # spindle

        def marks(s_):
            c = s_.cam
            o = ""
            for k in range(1, 9):                                            # ripple marks behind the tool
                x = -k * 11
                o += path(P([c.xy((x + 6 * math.cos(math.radians(a)), 14 * math.sin(math.radians(a)), .1)) for a in range(-90, 91, 30)], False), "o thin")
            o += path(P([c.xy((0, -.1, z)) for z in (-.1, -4, -8.5)] + [c.xy((0.1, y, -9)) for y in ()], False), "o thin")
            return o
        RAW(sc, marks, ((-100, -15, 0), (0, 15, .2)), -1)

        def zone(s_):                                                        # stirred zone on the cut face
            c = s_.cam
            pts = [(0.1, -14 + 28 * k / 12, -.1 - 9.6 * math.sin(math.pi * k / 12) ** .7) for k in range(13)]
            return path(P([c.xy(p) for p in pts]), "flash")
        RAW(sc, zone, ((0, -15, -10), (0.2, 0, 0)), -3)
    s, sc = fit(fn, -30, 26, (30, 18, 290, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, 0, 22), (0, 0, 1), 24, 120, 300)
    s += arrow3(cam, (30, -70, -10), (80, -70, -10))
    t = cam.xy((55, -70, -10))
    s += al(t[0], t[1] + 18, "送り")
    h = cam.xy((-28, 0, 76))
    s += lab(h[0] - 8, h[1], "回転ツール", "end")
    z = cam.xy((0, -14, -10))
    s += lab(z[0] - 8, z[1] + 20, "攪拌部", "end")
    return s


# =====================================================================================
# q:ultrasonic — ultrasonic welding: the horn presses the stack of foils / wires onto the
# knurled anvil and vibrates along the surface (20-40 kHz); the layers bond without melting
# =====================================================================================
@picto("ultrasonic")
def _():
    zt = -4 + 6 * 1.6                              # top of the foil stack

    def fn(sc):
        BOX(sc, -36, -30, -64, 72, 60, 54, "m", dark=.5, ch=3)             # anvil
        BOX(sc, -14, -14, -10, 28, 28, 6, "dk")                             # knurled anvil tip
        for k in range(6):                                                  # foil stack
            BOX(sc, -118 + 4 * k, -18, -4 + 1.6 * k, 160 - 4 * k, 36, 1.6, "cu", lines=False)
        BOX(sc, -14, -14, zt, 28, 28, 10, "t")                              # horn tip
        BOX(sc, -20, -18, zt + 10, 40, 150, 26, "t", ch=4)                  # horn (along y)
        CYL(sc, (0, 132, zt + 23), (0, 1, 0), 18, 36, "m", seg=28)          # booster
        CYL(sc, (0, 168, zt + 23), (0, 1, 0), 24, 46, "pt", seg=32)         # converter
    s, sc = fit(fn, -26, 22, (30, 16, 290, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (34, -40, zt + 12), (34, 10, zt + 12), both=True)
    s += arrow3(cam, (-34, -18, zt + 74), (-34, -18, zt + 40))
    v = cam.xy((34, 10, zt + 12))
    s += al(v[0] + 10, v[1] + 6, "振動", "start")
    p = cam.xy((-34, -18, zt + 60))
    s += al(p[0] - 8, p[1], "加圧", "end")
    h = cam.xy((-20, 70, zt + 36))
    s += lab(h[0] - 6, h[1] - 6, "ホーン", "end")
    f = cam.xy((-110, -18, 0))
    s += lab(f[0], f[1] + 22, "多層箔", "middle")
    return s


def half_ring_z(sc, z0, L, ro, ri, mat="m", n_=3, cx=0.0, bias=0.0, **kw):
    """back half (y >= 0) of a ring/tube along z, cut at y=0, as convex sectors."""
    for k in range(n_):
        a0, a1 = 180 * k / n_, 180 * (k + 1) / n_
        pts = arc(cx, 0, ro, a0, a1, 4) + [(cx + ri * math.cos(math.radians(a)), ri * math.sin(math.radians(a))) for a in (a1, a0)]
        Z(sc, z0, L, [(p[0], p[1], i // 2 if i < 5 else 10 + i) for i, p in enumerate(pts)], mat, bias, **kw)


def half_cyl_z(sc, z0, L, r, mat="m", cx=0.0, bias=0.0, **kw):
    Z(sc, z0, L, banded(arc(cx, 0, r, 0, 180, 12), 2), mat, bias, **kw)


# =====================================================================================
# q:spr — self-piercing riveting (cut at the centre): the punch drives a semi-tubular rivet
# through the upper sheet; its legs flare inside the lower sheet against the die, which never
# gets pierced (one-sided joint for aluminium / mixed materials)
# =====================================================================================
@picto("spr")
def _():
    def fn(sc):
        half_cyl_z(sc, -46, 30, 26, "m", dark=.3)                            # die
        BOX(sc, -54, 0, -16, 108, 40, 8, "alu")                              # lower sheet (back half)
        BOX(sc, -54, 0, -8, 108, 40, 8, "alu")                               # upper sheet
        half_ring_z(sc, 1.5, 30, 21, 11, "m")                                # blank holder (nose)
        half_cyl_z(sc, 1.5, 46, 9.5, "t", bias=-1)                           # punch

        def sec(s_):
            c = s_.cam
            o = face_y(c, [(-54, 0), (-12, 0), (-6, -2.5), (0, -3.5), (6, -2.5), (12, 0), (54, 0), (54, -8), (12, -8.5), (0, -12), (-12, -8.5), (-54, -8)], -.2, "cut")
            o += face_y(c, [(-54, -8), (-12, -8.5), (0, -12), (12, -8.5), (54, -8), (54, -16), (14, -16), (11, -21.5), (0, -23), (-11, -21.5), (-14, -16), (-54, -16)], -.2, "w2")
            o += face_y(c, [(-14, -16), (-11, -21.5), (0, -23), (11, -21.5), (14, -16)], -.15, "o")
            o += face_y(c, [(-9.5, 1.5), (9.5, 1.5), (9.5, 0), (5.5, -1), (5.5, -9), (10.5, -16), (7.5, -17), (3.4, -10), (3.4, -1.2),
                            (-3.4, -1.2), (-3.4, -10), (-7.5, -17), (-10.5, -16), (-5.5, -9), (-5.5, -1), (-9.5, 0)], -.25, "w3")
            return o
        RAW(sc, sec, ((-54, -.3, -24), (54, 0, 2)), -8)
    s, sc = fit(fn, -24, 18, (50, 22, 270, 176), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-34, 0, 50), (-34, 0, 24))
    a = cam.xy((-34, 0, 40))
    s += al(a[0] - 6, a[1], "加圧", "end")
    r = cam.xy((10, 0, 3))
    s += lab(r[0] + 40, r[1] - 22, "リベット", "start")
    d = cam.xy((26, 0, -34))
    s += lab(d[0] + 8, d[1] + 4, "ダイ", "start")
    p = cam.xy((-54, 0, -16))
    s += lab(p[0] + 4, p[1] + 20, "アルミ板2枚", "start")
    return s


# =====================================================================================
# q:sealer — sealer / adhesive dispensing robot: the nozzle on the robot wrist lays a bead
# of sealer along a fixed path on the panel flange
# =====================================================================================
@picto("sealer")
def _():
    u = GE._norm((-.25, -.45, .86))
    v = GE._norm((-.85, .3, .45))
    T = (0, -10, 4.5)                               # nozzle tip

    def fn(sc):
        BOX(sc, -150, -64, -6, 240, 110, 6, "w")                            # panel
        BOX(sc, -150, 4, 0, 240, 34, 5, "w", dark=.15)                       # stiffener flange
        bd = banded(hull(arc(-10, 0, 5, 0, 180, 8)), 2)
        X(sc, -150, 148, bd, "dk", smooth=True)                              # applied bead
        CYL(sc, T, u, 2.2, 26, "t", seg=16, r1=5)                            # nozzle
        CYL(sc, _add(T, u, 26), u, 11, 44, "m", seg=24)                      # dispensing gun
        W = _add(T, u, 70)
        CYL(sc, W, u, 15, 22, "pt", seg=28)                                  # wrist
        CYL(sc, _add(_add(W, u, 11), v, 12), v, 13, 70, "pt", seg=24, dark=.4)
    s, sc = fit(fn, -24, 24, (30, 20, 290, 174), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    g = cam.xy(_add(T, u, 50))
    gx = cam.xy(_add(_add(T, u, 50), (1, 0, 0), 60))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(g[0] + 8), n(g[1]), n(g[0] + 40), n(g[1] - 6), n(gx[0]), n(gx[1] - 40), n(gx[0] + 20), n(gx[1] - 60)), "cable")
    s += arrow3(cam, (20, -76, -6), (76, -76, -6))
    t = cam.xy((48, -76, -6))
    s += al(t[0], t[1] + 18, "塗布方向")
    k = cam.xy((-110, -64, -6))
    s += lab(k[0], k[1] + 18, "シーラー（ビード）")
    o = cam.xy(_add(T, u, 30))
    s += lab(o[0] - 26, o[1] + 4, "ノズル", "end")
    return s


# =====================================================================================
# q:plweld — hot-plate welding of plastic parts: a heated plate melts the joining edges of
# both parts, swings out, and the parts are pressed together while the melt is still soft
# =====================================================================================
@picto("plweld")
def _():
    def fn(sc):
        BOX(sc, -96, -54, -60, 192, 108, 40, "dk", ch=8)                     # lower part (housing)
        BOX(sc, -96, -54, -20, 192, 108, 3, "h", ch=8)                       # melted edge
        BOX(sc, -120, -66, 4, 240, 132, 9, "h", dark=.3)                     # hot plate
        BOX(sc, 120, -14, 4, 60, 28, 9, "m")                                 # plate arm
        BOX(sc, -96, -54, 30, 192, 108, 30, "w", ch=8, dark=.2)              # upper part (cover / lens)
    s, sc = fit(fn, -26, 22, (30, 16, 290, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-120, 0, 100), (-120, 0, 66))
    s += arrow3(cam, (128, 30, 30), (176, 30, 30))
    a = cam.xy((-120, 0, 84))
    s += al(a[0] - 6, a[1], "加圧", "end")
    b = cam.xy((176, 30, 30))
    s += al(b[0], b[1] - 8, "退避", "middle")
    h = cam.xy((-120, -66, 10))
    s += lab(h[0] - 6, h[1] - 2, "熱板", "end")
    m = cam.xy((-96, -54, -20))
    s += lab(m[0] - 6, m[1] + 14, "溶融面", "end")
    return s


def Y(sc, y0, L, xz, mat="w", bias=0.0, **kw):
    """outline [(x, z[, fid]), ...] extruded from y0 toward the viewer (-y) by L (face at y0-L is lit)."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, -1, 0), loop, L, mat, **kw)), ((min(xs), y0 - L, min(zs)), (max(xs), y0, max(zs))), bias)


def ysec(sc, a0, a1, ro, ri, y0, L, mat="w", cx=0.0, cz=0.0, n_=2, bias=0.0, **kw):
    """sector of a ring whose axis is y (face toward the viewer), from angle a0 to a1 (deg, x->z)."""
    for k in range(n_):
        b0, b1 = a0 + (a1 - a0) * k / n_, a0 + (a1 - a0) * (k + 1) / n_
        pts = arc(cx, cz, ro, b0, b1, 4) + [(cx + ri * math.cos(math.radians(b)), cz + ri * math.sin(math.radians(b))) for b in (b1, b0)]
        Y(sc, y0, L, [(p[0], p[1], i // 2 if i < 5 else 10 + i) for i, p in enumerate(pts)], mat, bias, **kw)


# =====================================================================================
# q:fracture — con-rod fracture splitting: a wedge is driven into the split mandrel in the
# big-end bore; the mandrel halves spread and crack the big end along the notched line
# =====================================================================================
@picto("fracture")
def _():
    g = 4                                           # opened crack

    def fn(sc):
        ysec(sc, -90, 90, 42, 27, 12, 24, "w", n_=3)                         # rod-side half of the big end
        ysec(sc, 90, 270, 42, 27, 12, 24, "w", cx=-g, n_=3)                  # cap half (split off)
        Y(sc, 7, 14, [(42, -14), (150, -9), (150, 9), (42, 14)], "w", dark=.2)   # beam
        Y(sc, 8, 16, GE.circle_outline(22, 28, 7, 170, 0), "w", holes=[GE.circle_outline(11, 20, 20, 170, 0)], smooth="outer")
        Y(sc, 26, 52, banded(arc(1, 0, 25, -90, 90, 10), 2), "t", -2)       # mandrel halves
        Y(sc, 26, 52, banded(arc(-1 - g, 0, 25, 90, 270, 10), 2), "t", -2)
        Y(sc, -26, 32, [(-g / 2 - 7, -12), (-g / 2 + 7, -12), (-g / 2 + 7, 12), (-g / 2 - 7, 12)], "dk", -3,
               scale=lambda t: .45 + .55 * t)                               # wedge
    s, sc = fit(fn, -18, 20, (30, 24, 290, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    for z0, z1 in ((27, 42), (-42, -27)):
        pts = [cam.xy((-g / 2 + (1.2 if k % 2 else -1.2), -12.2, z0 + (z1 - z0) * k / 5)) for k in range(6)]
        s += path(P(pts, False), "crack")
    s += arrow3(cam, (-g / 2, -80, 40), (-g / 2, -62, 22))
    s += arrow3(cam, (-24, -12, -54), (-64, -12, -54))
    w = cam.xy((-g / 2, -80, 40))
    s += al(w[0] - 8, w[1] - 4, "くさび", "end")
    c = cam.xy((-50, -12, -54))
    s += lab(c[0], c[1] + 20, "キャップ")
    r = cam.xy((100, -7, 14))
    s += lab(r[0], r[1] - 10, "コンロッド本体")
    k = cam.xy((-g / 2, -12, 42))
    s += al(k[0] + 8, k[1] - 6, "破断", "start")
    return s


# =====================================================================================
# q:framing — body framing jig: gates on both sides of the line close in and clamp the
# underbody, side panels and roof in their exact positions while robots weld them together
# =====================================================================================
@picto("framing")
def _():
    prof = [(-118, 2), (118, 2), (118, 30), (72, 36), (36, 76), (-50, 78), (-86, 40), (-118, 36)]
    wins = [[(-78, 44, 0), (-8, 44, 1), (-8, 72, 2), (-46, 73, 3)], [(0, 44, 0), (58, 44, 1), (32, 71, 2), (0, 72, 3)]]

    def fn(sc):
        BOX(sc, -134, -66, -24, 268, 132, 14, "m", dark=.4)                  # body pallet
        BOX(sc, -118, -44, -10, 236, 88, 12, "w", dark=.2)                   # underbody
        Y(sc, -44, 4, prof, "w", holes=wins)                                 # near side panel
        Y(sc, 48, 4, prof, "w", holes=wins)                                  # far side panel
        BOX(sc, -50, -44, 72, 86, 88, 5, "w")                                # roof
        for x in (-96, 70):                                                  # near-side clamp units on the pallet
            BOX(sc, x, -62, -10, 18, 14, 22, "dk")
            BOX(sc, x, -62, 12, 18, 14, 6, "dk", bias=-1)
        BOX(sc, -150, 84, -24, 16, 14, 150, "pt", dark=.6, ch=3)            # far gate
        BOX(sc, 134, 84, -24, 16, 14, 150, "pt", dark=.6, ch=3)
        BOX(sc, -150, 84, 126, 300, 14, 16, "pt", dark=.6)
        for x in (-80, 10):                                                  # gate clamp arms onto the roof rail
            BOX(sc, x, 86, 84, 10, 10, 42, "dk")
            BOX(sc, x, 50, 78, 10, 36, 8, "dk")
    s, sc = fit(fn, -28, 20, (24, 22, 296, 174), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (0, -110, 24), (0, -66, 24))
    s += arrow3(cam, (162, 120, 60), (162, 92, 60))
    g = cam.xy((0, 84, 142))
    s += lab(g[0], g[1] - 15, "総組治具（ゲート）")
    c = cam.xy((0, -110, 24))
    s += al(c[0] - 6, c[1] + 10, "クランプ", "end")
    b = cam.xy((-134, -66, -24))
    s += lab(b[0] + 6, b[1] + 18, "車体（溶接前）", "start")
    return s


# =====================================================================================
# q:blow — extrusion blow moulding: the head extrudes a hot tube (parison) between the
# open mould halves; the mould closes, pinches it and air blown inside presses it to the cavity
# =====================================================================================
@picto("blow")
def _():
    def fn(sc):
        BOX(sc, -40, -34, 108, 80, 68, 42, "pt", ch=5)                       # extrusion head
        CYL(sc, (40, 0, 130), (1, 0, 0), 15, 90, "m", seg=24)               # extruder barrel
        CYL(sc, (0, 0, 96), (0, 0, 1), 19, 12, "dk", seg=28)                # die ring
        CYL(sc, (0, 0, -12), (0, 0, 1), 15, 108, "h", seg=28)               # parison
        CYL(sc, (0, 0, -44), (0, 0, 1), 5, 32, "m", seg=16)                 # blow pin
        BOX(sc, -122, -54, -24, 62, 108, 112, "t", ch=4)                     # mould half (left)
        BOX(sc, 60, -54, -24, 62, 108, 112, "t", ch=4)                       # mould half (right)
        BOX(sc, -150, -40, -24, 28, 80, 112, "pt", dark=1)                   # platens
        BOX(sc, 122, -40, -24, 28, 80, 112, "pt", dark=1)

        def cav(s_):                                                         # cavity on the right half's inner face
            c = s_.cam
            pts = [(60 - .1, 38 * math.cos(math.radians(a)) * (1 if abs(a) < 90 else 1), 34 + 46 * math.sin(math.radians(a)))
                   for a in range(0, 360, 20)]
            pts = [(x, max(-36, min(36, y * 1.2)), max(-8, min(76, z))) for x, y, z in pts]
            return path(P([c.xy(p) for p in pts]), "bg")
        RAW(sc, cav, ((59.8, -54, -24), (60, 54, 88)), -1)
    s, sc = fit(fn, 30, 14, (30, 14, 290, 178), sh_ry=6, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-196, -20, 40), (-154, -20, 40))
    s += arrow3(cam, (196, -20, 40), (154, -20, 40))
    s += arrow3(cam, (0, -20, -56), (0, -20, -22))
    h = cam.xy((-40, -34, 136))
    s += lab(h[0] - 6, h[1], "押出ヘッド", "end")
    p = cam.xy((-6, -15, -30))
    s += lab(p[0] - 30, p[1] + 16, "パリソン", "end")
    m = cam.xy((122, -54, -24))
    s += lab(m[0] - 10, m[1] + 18, "金型")
    a = cam.xy((0, -20, -56))
    s += al(a[0] + 8, a[1] + 4, "空気", "start")
    return s


# =====================================================================================
# q:extrude — extruder (cut away at the centre plane): the screw melts / plasticises the
# material from the hopper and pushes it through the die, giving an endless constant section
# =====================================================================================
@picto("extrude")
def _():
    prof = [(-24, -6), (24, -6), (17, 7), (-17, 7)]                          # tread-like section

    def fn(sc):
        BOX(sc, -262, -22, -24, 42, 44, 48, "dk", ch=3)                       # drive
        shell_x(sc, -220, 200, 24, 15, "m", bias=4)                           # barrel (back half)
        CYL(sc, (-216, 0, 0), (1, 0, 0), 8, 190, "w", seg=20)                 # screw root
        for k in range(10):
            CYL(sc, (-204 + k * 17, 0, 0), (1, 0, .18), 14.5, 3, "w", seg=20, bands=8, bias=-1, lines=False)
        X(sc, -26, 6, half_disc(15), "h", bias=2)
        CYL(sc, (-190, 0, 24), (0, 0, 1), 9, 34, "pt", seg=28, r1=24, dark=.4)   # hopper
        BOX(sc, -20, -34, -34, 40, 68, 68, "pt", ch=5)                        # die head
        BOX(sc, 20, -28, -28, 10, 56, 56, "dk")                               # die plate
        X(sc, 30, 136, prof, "dk")                                            # extrudate
        for x in (66, 110, 154):                                              # take-off rollers
            CYL(sc, (x, -32, -14), (0, 1, 0), 8, 64, "m", seg=20)
    s, sc = fit(fn, 14, 18, (16, 30, 304, 170), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-130, 0, 0), (1, 0, 0), 20, 200, 320)
    s += arrow3(cam, (70, 0, 32), (140, 0, 32))
    t = cam.xy((105, 0, 32))
    s += al(t[0], t[1] - 9, "押出し")
    d = cam.xy((10, 0, 34))
    s += lab(d[0], d[1] - 12, "ダイ")
    w = cam.xy((-140, 0, -26))
    s += lab(w[0], w[1] + 22, "スクリュ")
    p = cam.xy((110, -32, -22))
    s += lab(p[0], p[1] + 18, "押出品")
    return s


# =====================================================================================
# q:cvulc — continuous vulcanising line (front walls cut away): the extruded rubber profile
# runs through a microwave (UHF) tunnel that heats it from inside, then a hot-air tunnel
# =====================================================================================
@picto("cvulc")
def _():
    prof = banded(hull(arc(0, 8, 7, 0, 360, 12) + [(-10, 0), (10, 0)]), 2)

    def fn(sc):
        for x0, L in ((-140, 120), (-4, 150)):
            BOX(sc, x0, -30, -26, L, 60, 6, "pt", dark=.6)                    # floor / conveyor bed
            BOX(sc, x0, 24, -20, L, 6, 64, "pt", dark=.9)                     # back wall
            BOX(sc, x0, 0, 44, L, 30, 8, "pt", dark=.2)                       # roof (back half)
        BOX(sc, -180, -16, -26, 40, 32, 6, "m")                               # infeed bed
        X(sc, -180, 360, [(p[0], p[1] - 20, p[2]) for p in prof], "dk", smooth=True)   # rubber profile

        def marks(s_):
            c = s_.cam
            o = ""
            for k in range(3):                                                # microwave field on the back wall
                z = 2 + k * 12
                o += path(P([c.xy((-126 + 3 * j, 23.9, z + 3 * math.sin(j * 0.9))) for j in range(31)], False), "uvwave")
            return o
        RAW(sc, marks, ((-130, 23.8, -10), (-20, 24, 40)), -1)
    s, sc = fit(fn, -26, 24, (22, 26, 298, 168), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    for x in (20, 60, 100, 140):
        p = cam.xy((x, 10, 40))
        s += heat(p[0], p[1] + 2, 1)
    s += arrow3(cam, (156, 0, -6), (190, 0, -6))
    a = cam.xy((-80, 15, 52))
    s += lab(a[0], a[1] - 10, "マイクロ波")
    b = cam.xy((71, 15, 52))
    s += lab(b[0], b[1] - 10, "熱風")
    c = cam.xy((-150, -16, -26))
    s += lab(c[0] + 10, c[1] + 20, "押出したゴム", "start")
    return s


# =====================================================================================
# q:mixer — internal (Banbury) mixer, cut at the front: two counter-rotating winged rotors
# knead rubber, carbon black and chemicals in a closed chamber under the ram
# =====================================================================================
@picto("mixer")
def _():
    xr = 27                                         # rotor centres at x = +-xr, z = 0

    def fn(sc):
        hole = [(-12, 64), (-12, 27)] + [(-xr + 30 * math.cos(math.radians(t)), 30 * math.sin(math.radians(t))) for t in range(64, 297, 16)] + \
               [(xr + 30 * math.cos(math.radians(t)), 30 * math.sin(math.radians(t))) for t in range(-116, 117, 16)] + [(12, 27), (12, 64)]
        Y(sc, 64, 64, [(-74, -52), (74, -52), (74, 64), (-74, 64)], "pt", dark=.5, cap_mat="cut",
          holes=[[(x, z, k + 10) for k, (x, z) in enumerate(hole)]])                       # chamber body (back half)
        ell = banded([(22 * math.cos(2 * math.pi * k / 24), 12 * math.sin(2 * math.pi * k / 24)) for k in range(24)], 2)
        for sx, tw in ((-1, .7), (1, -.7)):
            sc.add(compact(GE.prism(sc.cam, (sx * xr, 60, 0), (0, -1, 0), [(p[0], p[1], p[2]) for p in ell], 66, "w",
                                    twist=tw, slices=4, smooth=True)), ((sx * xr - 22, -6, -22), (sx * xr + 22, 60, 22)), -2)
            CYL(sc, (sx * xr, 60, 0), (0, 1, 0), 8, 30, "m", seg=16)                       # rotor shafts (rear)
        BOX(sc, -11, 0, 66, 22, 60, 10, "dk")                                              # ram (in the throat)
        BOX(sc, -11, 0, 76, 22, 60, 34, "m", dark=.3)                                      # ram rod / weight
        BOX(sc, -16, 0, -64, 32, 64, 12, "m", dark=.5)                                     # drop door

        def batch(s_):
            c = s_.cam
            o = ""
            for x, z, r in ((0, 18, 7), (-6, -22, 6), (8, -24, 5), (-48, 20, 5), (50, -18, 5)):
                o += path(P(circ3(c, (x, -6.5, z), (0, 1, 0), r, 12)), "rb")
            return o
        RAW(sc, batch, ((-60, -7, -30), (60, -6.2, 30)), -6)
    s, sc = fit(fn, -14, 14, (40, 16, 280, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-xr, -8, 0), (0, 1, 0), 36, 50, 125)
    s += arc3(cam, (xr, -8, 0), (0, 1, 0), 36, 130, 55)
    s += arrow3(cam, (-30, 0, 128), (-30, 0, 96))
    a = cam.xy((-30, 0, 118))
    s += al(a[0] - 6, a[1], "ラム加圧", "end")
    r = cam.xy((74, -6, -40))
    s += lab(r[0] + 4, r[1] + 4, "2本のロータ", "start")
    b = cam.xy((0, 0, -64))
    s += lab(b[0], b[1] + 18, "ゴム＋カーボン")
    return s


# =====================================================================================
# q:calender — 4-roll calender (topping): the steel / textile cords run through the middle
# nip while the outer roll pairs form thin rubber sheets that are pressed onto both sides
# =====================================================================================
@picto("calender")
def _():
    R, L = 25, 110
    zs = (79, 26, -26, -79)

    def fn(sc):
        for z in zs:
            CYL(sc, (0, L / 2, z), (0, -1, 0), R, L, "m", seg=40, dark=.1)                 # rolls
            CYL(sc, (0, L / 2 + 16, z), (0, -1, 0), 9, 16, "dk", seg=16)                   # journals
        BOX(sc, -16, L / 2 + 16, -112, 32, 14, 222, "pt", dark=1)                           # frame (rear)
        BOX(sc, -170, -L / 2 + 4, -1, 144, L - 8, 2, "w", lines=False)                      # cords (bare)
        BOX(sc, 25, -L / 2 + 4, -3, 145, L - 8, 6, "dk")                                    # rubber-coated ply

        def cords(s_):
            c = s_.cam
            o = ""
            for k in range(9):
                y = -L / 2 + 10 + k * (L - 20) / 8
                o += line(*c.xy((-170, y, 1.1)), *c.xy((-26, y, 1.1)), "o thin")
            for z in (52.5, -52.5):                                                         # rubber banks at the nips
                o += path(P(circ3(c, (-14, -L / 2 - .5, z), (0, 1, 0), 7, 12)), "rb")
            return o
        RAW(sc, cords, ((-170, -L / 2 - 1, -60), (-14, L / 2, 60)), -3)
    s, sc = fit(fn, -24, 14, (20, 14, 300, 180), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (0, -L / 2 - 2, zs[1]), (0, 1, 0), R + 6, 200, 280)
    s += arc3(cam, (0, -L / 2 - 2, zs[2]), (0, 1, 0), R + 6, 160, 80)
    s += arrow3(cam, (70, -L / 2 - 20, -3), (130, -L / 2 - 20, -3))
    a = cam.xy((-130, -L / 2, 0))
    s += lab(a[0], a[1] + 22, "コード")
    b = cam.xy((100, -L / 2 - 20, -3))
    s += lab(b[0], b[1] + 22, "ゴム被覆シート")
    r = cam.xy((R, 0, zs[0]))
    s += lab(r[0] + 10, r[1] - 6, "ロール", "start")
    return s


# =====================================================================================
# q:tirebuild — tyre building machine: inner liner, carcass plies, bead rings, belts and the
# tread are wound one after another onto the rotating building drum -> green tyre
# =====================================================================================
@picto("tirebuild")
def _():
    def fn(sc):
        BOX(sc, 100, -50, -86, 50, 100, 150, "pt", dark=1, ch=4)                           # drive head
        CYL(sc, (80, 0, 0), (1, 0, 0), 16, 20, "dk", seg=20)                               # main shaft
        CYL(sc, (-80, 0, 0), (1, 0, 0), 50, 6, "m", seg=40, bias=-3)                          # building drum
        CYL(sc, (-74, 0, 0), (1, 0, 0), 54, 148, "dk", seg=40, bias=-.5)                         # liner + carcass ply
        for x in (-74, 66):
            CYL(sc, (x, 0, 0), (1, 0, 0), 59, 8, "w", seg=40, bias=-1)                 # bead rings
        CYL(sc, (-48, 0, 0), (1, 0, 0), 61, 96, "dk", seg=40, dark=.2, bias=-1)        # belt + tread band
        BOX(sc, -48, -170, -67, 96, 170, 6, "dk")                                           # tread strip on the servicer
        CYL(sc, (-60, -120, -75), (1, 0, 0), 8, 120, "m", seg=16)                           # servicer roller
        RAW(sc, lambda s_: hole3(s_.cam, (-80.2, 0, 0), (-1, 0, 0), 18, "dk") + hole3(s_.cam, (-80.3, 0, 0), (-1, 0, 0), 8, "bg"),
            ((-80.4, -18, -18), (-80.1, 18, 18)), -4)                                       # drum hub
    s, sc = fit(fn, 22, 16, (30, 16, 290, 178), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-90, 0, 0), (1, 0, 0), 68, 30, 150)
    s += arrow3(cam, (-62, -150, -52), (-62, -90, -52))
    r = cam.xy((-90, -30, 68))
    s += al(r[0] - 10, r[1] - 8, "回転", "end")
    d = cam.xy((-80, -40, -50))
    s += lab(d[0] - 8, d[1] + 10, "成形ドラム", "end")
    t = cam.xy((48, -150, -67))
    s += lab(t[0] + 8, t[1] + 4, "トレッド", "start")
    b = cam.xy((-74, 0, 59))
    s += lab(b[0] + 26, b[1] - 8, "ビード", "start")
    return s


# =====================================================================================
# q:beadform — bead winding: steel wire is coated with rubber in a small crosshead and wound
# turn after turn onto a rotating former, building the ring-shaped bead bundle
# =====================================================================================
@picto("beadform")
def _():
    zt = 76                                          # top of the bead ring

    def fn(sc):
        BOX(sc, -40, 48, -110, 80, 30, 120, "pt", dark=1, ch=4)                             # drive stand
        CYL(sc, (0, 48, 0), (0, -1, 0), 14, 18, "dk", seg=20)                               # spindle
        CYL(sc, (0, 30, 0), (0, -1, 0), 70, 24, "m", seg=56)                                # former (winding drum)
        RING(sc, (0, 6, 0), (0, -1, 0), zt, 66, 10, "dk", seg=56)                           # bead bundle
        BOX(sc, 112, -14, zt - 12, 40, 28, 26, "pt", ch=4)                                   # coating crosshead
        CYL(sc, (152, 1, zt + 1), (1, 0, 0), 9, 26, "dk", seg=16)                           # rubber feed

        def turns(s_):
            c = s_.cam
            return "".join(path(P(circ3(c, (0, -4.1, 0), (0, 1, 0), r, 48)), "o thin") for r in (69.3, 72.6))
        RAW(sc, turns, ((-76, -4.3, -76), (76, -4.1, 76)), -2)
    s, sc = fit(fn, -18, 14, (30, 22, 290, 176), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((112, 1, zt - 4)), cam.xy((0, 1, zt - 4))
    s += line(a[0], a[1], b[0], b[1], "wire2")                                              # coated wire onto the ring
    c, d = cam.xy((205, 1, zt + 6)), cam.xy((178, 1, zt + 6))
    s += line(c[0], c[1], d[0], d[1], "o")                                                  # bare steel wire in
    s += arc3(cam, (0, -8, 0), (0, 1, 0), 88, 150, 40)
    r = cam.xy((-80, -8, 50))
    s += al(r[0] - 4, r[1], "回転", "end")
    h = cam.xy((132, -14, zt + 14))
    s += lab(h[0], h[1] - 10, "ゴム被覆")
    w = cam.xy((196, 1, zt + 6))
    s += lab(w[0], w[1] + 18, "鋼線")
    k = cam.xy((50, -6, -60))
    s += lab(k[0] + 10, k[1] + 12, "ビード", "start")
    return s


# =====================================================================================
# q:tirecure — bladder-type curing press (cut at the centre): the green tyre is closed in the
# heated mould and the bladder, filled with steam / hot water, presses it into the tread pattern
# =====================================================================================
@picto("tirecure")
def _():
    def fn(sc):
        BOX(sc, -140, 0, -72, 280, 80, 20, "pt", dark=.6)                                   # lower platen (back half)
        half_cyl_z(sc, -52, 104, 110, "t", dark=.2)                                         # mould (back half)
        BOX(sc, -140, 0, 52, 280, 80, 18, "pt")                                             # upper platen
        CYL(sc, (0, 40, 70), (0, 0, 1), 26, 40, "m", seg=28)                                # press ram

        def sec(s_):
            c = s_.cam
            o = face_y(c, [(-110, 0), (110, 0)], -.1, "o thin")                             # parting line
            for m in (1, -1):
                tyre = [(52, -22), (70, -24), (80, -16), (83, 0), (80, 16), (70, 24), (52, 22), (52, 15), (64, 14), (69, 0), (64, -14), (52, -15)]
                o += face_y(c, [(m * x, z) for x, z in tyre], -.2, "rb")
                for k in range(5):                                                          # tread grooves
                    z = -16 + 8 * k
                    o += face_y(c, [(m * 83.2, z - 1.5), (m * 79, z - 1.5), (m * 79, z + 1.5), (m * 83.2, z + 1.5)], -.25, "bg")
            bl = [(-12, -13), (-50, -14), (-62, -12), (-67, 0), (-62, 12), (-50, 14), (-12, 13),
                  (12, 13), (50, 14), (62, 12), (67, 0), (62, -12), (50, -14), (12, -13)]
            o += face_y(c, bl, -.3, "h")                                                    # bladder (steam inside)
            o += face_y(c, [(-10, -52), (10, -52), (10, 52), (-10, 52)], -.35, "m2")        # centre post
            return o
        RAW(sc, sec, ((-110, -.4, -52), (110, 0, 52)), -6)
    s, sc = fit(fn, -14, 20, (30, 26, 290, 172), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (-100, 40, 110), (-100, 40, 76))
    for m in (1, -1):
        s += arrow3(cam, (m * 30, -.5, 0), (m * 58, -.5, 0))
    a = cam.xy((-100, 40, 96))
    s += al(a[0] - 6, a[1], "型締め", "end")
    b = cam.xy((0, 0, -14))
    s += lab(b[0], b[1] + 24, "ブラダ（蒸気）")
    t = cam.xy((83, 0, 24))
    s += lab(t[0] + 30, t[1] - 4, "タイヤ", "start")
    m_ = cam.xy((110, 0, -40))
    s += lab(m_[0] + 6, m_[1], "金型", "start")
    return s


# =====================================================================================
# q:foam — polyurethane foaming: the high-pressure mixing head impinges polyol and isocyanate,
# pours the mixture into the open mould, the lid closes and the foam rises to fill the cavity
# =====================================================================================
@picto("foam")
def _():
    def fn(sc):
        BOX(sc, -130, -80, -50, 260, 160, 16, "pt", dark=.6)                                # carrier (turntable)
        outer = [(-110, -64), (110, -64), (110, 64), (-110, 64)]
        inner = []
        for cx, cy, a0 in ((84, -40, -90), (84, 40, 0), (-84, 40, 90), (-84, -40, 180)):
            inner += arc(cx, cy, 10, a0, a0 + 90, 3)
        sc.add(compact(GE.prism(sc.cam, (0, 0, -34), (0, 0, 1), [(-y, x, k) for k, (x, y) in enumerate(outer)], 44, "t",
                                holes=[[(-y, x, 10 + k) for k, (x, y) in enumerate(inner)]])), ((-110, -64, -34), (110, 64, 10)))  # lower mould
        Z(sc, -34, 20, [(x * .995, y * .99) for x, y in inner], "gw", -1)                    # foam rising in the cavity
        BOX(sc, -110, 64, 10, 220, 14, 110, "t", dark=.6, ch=3)                              # lid (opened, hinged at the back)
        CYL(sc, (30, -10, 74), (0, 0, 1), 7, 14, "dk", seg=16)                               # nozzle
        CYL(sc, (30, -10, 88), (0, 0, 1), 18, 40, "pt", seg=28)                              # mixing head
    s, sc = fit(fn, -24, 26, (30, 22, 290, 176), sh_ry=6, sh_k=.42, ret_scene=True)
    cam = sc.cam
    a, b = cam.xy((30, -10, 74)), cam.xy((30, -10, -14))
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(a[0] - 2.5), n(a[1]), n(a[0] + 2.5), n(a[1]), n(b[0] + 4), n(b[1]), n(b[0] - 4), n(b[1])), "fl")
    h = cam.xy((48, -10, 116))
    for dx, dy in ((70, -26), (74, 8)):
        s += path("M%s %s C%s %s %s %s %s %s" % (n(h[0]), n(h[1]), n(h[0] + 30), n(h[1] - 4), n(h[0] + dx - 20), n(h[1] + dy), n(h[0] + dx), n(h[1] + dy)), "cable")
    s += arrow3(cam, (-60, -10, -16), (-60, -10, 18))
    s += arrow3(cam, (-10, -90, -34), (60, -90, -34))
    r = cam.xy((-60, -10, 8))
    s += al(r[0] - 26, r[1] + 4, "発泡", "end")
    m = cam.xy((12, -18, 120))
    s += lab(m[0] - 6, m[1], "混合ヘッド", "end")
    k = cam.xy((48, -10, 116))
    s += lab(k[0] + 78, k[1] - 32, "2液", "middle")
    w = cam.xy((-110, -64, -34))
    s += lab(w[0] + 2, w[1] + 22, "金型", "start")
    return s
