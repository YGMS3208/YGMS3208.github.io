"""v3 shaded-3D detail and process (ops) drawings, 480x300: chassis.eps, chassis.balljoint, ev.rotor,
ev.eaxlecase. Replaces the flat side-view sheets of il_d_chassis / il_d_ev (same titles, notes, op count)."""
import math
import il_gear as GE
from il_base import *
from il_detail import title, bal, tol, fin, loc, Pl
from il_dmap import dpart
from il_pictos import chart, lightning
from il3_lib import compact, fit, hull, banded, arc, circ3, hole3, P, arc3, arrow3
from il3_chassis import cy, px, py, pz, add, mul, hexagon, threads
from il3_pilot import lam_lines
from il3_ev import mrg
import il_d_chassis as C
import il_d_ev as V

PI = math.pi
XA, YA, ZA = (1, 0, 0), (0, 1, 0), (0, 0, 1)
OPA = (24, 42, 456, 266)          # op drawing area (below the title band, above the tol line)


# ------------------------------------------------------------------ small helpers
def pl3(cam, pts, c="mf", close=False):
    """polyline through world points."""
    return path(P([cam.xy(p) for p in pts], close), c)


def sil(cam, x0, x1, r, y=0.0, z=0.0, c="mf"):
    """the two silhouette generators of a cylinder along x (machined-surface outline)."""
    t = math.atan2(-cam.D[1], cam.D[2])
    d = ""
    for tt in (t, t + PI):
        a = cam.xy((x0, y + r * math.cos(tt), z + r * math.sin(tt)))
        b = cam.xy((x1, y + r * math.cos(tt), z + r * math.sin(tt)))
        d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    return path(d, c)


def ring3(cam, C_, A, r, c="mf", seg=28):
    return path(P(circ3(cam, C_, A, r, seg)), c)


def lb(cam, p, t, dx=0, dy=0, a="middle"):
    x, y = cam.xy(p)
    return text(x + dx, y + dy, t, a, "al")


def op(fn, az, el, area=OPA, **kw):
    """fit fn into the op area; fn(sc) draws everything (manual order) and may set sc.top for marks."""
    s, sc = fit(fn, az, el, area, ret_scene=True, **kw)
    return mrg(s), sc.cam


def bb(cam, x, y, z, sx, sy, sz, mat="m", ch=0, **kw):
    """axis-aligned box (manual order) from corner (x, y, z); ch = vertical-edge chamfer."""
    c = ch
    xy = [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)] if not c else \
        [(x + c, y), (x + sx - c, y), (x + sx, y + c), (x + sx, y + sy - c), (x + sx - c, y + sy), (x + c, y + sy), (x, y + sy - c), (x, y + c)]
    return pz(cam, z, sz, xy, mat, **kw)


# =====================================================================================
# chassis.eps — rack bar (teeth on top, ball-screw groove), light EPS assembly
# =====================================================================================
RL, RR, T0, T1, S0, S1, TP = 300, 12, 20, 150, 190, 260, 8.0


def rack(cam, teeth=True, screw=True, hot=None, ins=None, mat="w", L=RL):
    """rack bar along +x from 0 (x = 0 end faces the viewer at az > 0), drawn far (+x) -> near.
    ins: {x: svg} drawn when the sweep passes x (coil rings, centres ...)."""
    ins = dict(ins or {})
    br = sorted({0, L} | ({T0, T1} if teeth else set()) | (set(hot) if hot else set()) | set(k for k in ins if 0 < k < L))
    o = "".join(v for k, v in sorted(ins.items(), reverse=True) if k >= L)
    dbar = banded(hull(arc(0, 0, RR, 194.5, 345.5, 10)), 2)
    for a, b in reversed(list(zip(br, br[1:]))):
        m = "h" if hot and a >= hot[0] and b <= hot[1] else mat
        if teeth and a >= T0 and b <= T1:
            o += px(cam, a, b - a, dbar, m)
            o += rteeth(cam, a, b, m)
        else:
            o += cy(cam, (a, 0, 0), XA, RR, b - a, m, seg=24, bands=8)
            if screw and a >= S0 and b <= S1:
                o += threads(cam, a + 1, b, RR, 7)
        o += ins.get(a, "") if a < L else ""
    return o + "".join(v for k, v in sorted(ins.items(), reverse=True) if k < 0)


def rteeth(cam, a, b, m="w", w=9.4, z0=3, z1=7):
    """rack teeth across y = -w..w between x = a..b as four merged face paths (cheap; teeth seen from above)."""
    fl, tp, bk, fr = [], [], [], []
    x = T0
    while x + .8 * TP <= b + 1e-6:
        if x >= a - 1e-6:
            q = [(x, z0), (x + .2 * TP, z1), (x + .6 * TP, z1), (x + .8 * TP, z0)]
            bk.append([(q[2][0], -w, q[2][1]), (q[3][0], -w, q[3][1]), (q[3][0], w, q[3][1]), (q[2][0], w, q[2][1])])
            tp.append([(q[1][0], -w, z1), (q[2][0], -w, z1), (q[2][0], w, z1), (q[1][0], w, z1)])
            fl.append([(q[0][0], -w, z0), (q[1][0], -w, z1), (q[1][0], w, z1), (q[0][0], w, z0)])
            fr.append([(u, -w, v) for u, v in q])
        x += TP
    o = ""
    for faces, c in ((bk, "s3"), (tp, "s1"), (fl, "s2"), (fr, "s2")):
        if faces:
            o += path("".join(P([cam.xy(p) for p in f]) for f in faces), m + c)
    return o


def teeth_mf(cam, x0=T0, x1=T1):
    pts = []
    x = x0
    while x + .8 * TP <= x1 + 1e-6:
        pts += [(x, -9.4, 3), (x + .2 * TP, -9.4, 7), (x + .6 * TP, -9.4, 7), (x + .8 * TP, -9.4, 3)]
        x += TP
    return pl3(cam, pts)


def boot(cam, x0, x1, rmin=14, rmax=20, nc=2):
    o = ""
    L = (x1 - x0) / (2 * nc)
    for k in range(2 * nc - 1, -1, -1):
        a, b = (rmin, rmax) if k % 2 == 0 else (rmax, rmin)
        o += compact(GE.prism(cam, (x0 + k * L, 0, 0), XA, GE.circle_outline(a, 10, 3), L, "dk", smooth=True,
                              scale=lambda t, a=a, b=b: 1 + (b / a - 1) * t, lines=k % 2 == 0))
    return o


def rod(cam, x0, x1, sd):
    """tie rod: inner joint housing, rod, jam nut (outer end faces +x when sd > 0)."""
    if sd > 0:
        return (cy(cam, (x0 + 24, 0, 0), XA, 7, x1 - x0 - 24, "m", seg=10, bands=4) +
                px(cam, x1 - 50, 10, banded(hexagon(10, 30), 1), "m", dark=.2) + cy(cam, (x0, 0, 0), XA, 11, 24, "m", seg=12, bands=5))
    return (cy(cam, (x1 - 24, 0, 0), XA, 11, 24, "m", seg=12, bands=5) + cy(cam, (x0, 0, 0), XA, 7, x1 - x0 - 24, "m", seg=10, bands=4) +
            px(cam, x0 + 40, 10, banded(hexagon(10, 30), 1), "m", dark=.2))


EAP = GE._norm((.15, .45, 1))      # pinion (input) shaft axis
EPC = (-128, 0, 0)


def eps_m(cam, ends=True, motor=True, hm="alu", bore=False):
    """EPS rack-assist assembly (housing, belt case, motor + ECU behind, pinion boss, boots, tie rods)."""
    my, mz = 58, 6
    o = ""
    if motor:
        o += cy(cam, (-30, my, mz), XA, 25, 118, "m", seg=14, bands=5)
        o += compact(GE.prism(cam, (-56, my, mz), XA, banded(hull(arc(0, 0, 27, 0, 360, 8) + [(-29, 29), (29, 29), (-29, -25), (29, -25)]), 2), 26,
                              "dk", smooth=True))
        o += pz(cam, 22, 10, [(-50, my - 6), (-38, my - 6), (-38, my + 6), (-50, my + 6)], "dk")
    if ends:
        o += rod(cam, 166, 236, 1) + boot(cam, 128, 166)
    o += cy(cam, (96, 0, 0), XA, 18, 32, hm, seg=16, bands=6)
    o += compact(GE.prism(cam, (84, 0, 0), XA, banded(hull(arc(0, 0, 36, 0, 360, 10) + arc(my, mz, 29, 0, 360, 10)), 3), 14, hm, smooth=True))
    o += cy(cam, (30, 0, 0), XA, 33, 54, hm, seg=20, bands=7)
    o += cy(cam, (22, 0, 0), XA, 26, 8, hm, seg=16, r1=33, bands=5)
    o += cy(cam, (-150, 0, 0), XA, 22, 172, hm, seg=18, bands=7)
    o += cy(cam, EPC, EAP, 25, 38, hm, seg=18, bands=7)
    o += cy(cam, add(EPC, mul(EAP, 38)), EAP, 13, 7, "dk", seg=16, bands=6)
    if motor:
        o += cy(cam, add(EPC, mul(EAP, 45)), EAP, 9, 28, "m", seg=16, bands=6)
    if bore:
        o += hole3(cam, (-150.2, 0, 0), (-1, 0, 0), 15, "bg", 22)
    if ends:
        o += boot(cam, -188, -150) + rod(cam, -258, -188, -1)
    return o


@dpart("chassis.eps", "detail")
def eps_detail3():
    notes = [("ラック歯", "ピニオンと噛み合う歯。可変ギヤ比は鍛造"), ("ボールねじ溝", "モータのアシスト力を軸力に変える"),
             ("ラックハウジング", "アルミダイカスト"), ("アシストモータ・ECU", "トルクセンサの信号でアシスト")]
    s1, c1 = op(lambda sc: eps_m(sc.cam), 18, 30, (24, 16, 456, 168), sh_ry=6, sh_k=.42)
    s2, c2 = op(lambda sc: rack(sc.cam), 12, 40, (60, 196, 420, 266), sh_ry=4, sh_k=.4)
    s = s1 + s2
    a1, a2 = c2.xy((84, -6, 7)), c2.xy((225, -8, 9))
    a3, a4 = c1.xy((-80, -14, 18)), c1.xy((-44, 58, 34))
    s += bal(*a1, 150, 284, 1) + bal(*a2, 380, 286, 2) + bal(*a3, 120, 186, 3) + bal(*a4, 300, 30, 4)
    return s, notes


def _eps0():
    def fn(sc):
        cam = sc.cam
        o = ""
        for x in (250, 50):
            o += bb(cam, x - 14, -18, -44, 28, 36, 32, "m", dark=.4)
        o += cy(cam, (334, 0, 0), XA, RR, 30, "w", seg=24, bands=8)
        o += cy(cam, (317, 0, 30), XA, 46, 3, "t", seg=40, bands=10, holes=[GE.circle_outline(10, 16, 4)])
        o += rack(cam, False, False, L=316)
        o += bb(cam, 130, -16, 34, 32, 32, 46, "dk", ch=3) + bb(cam, 124, -20, 26, 44, 40, 8, "m")
        return o
    s, cam = op(fn, 26, 20)
    s += arrow3(cam, (146, 0, 128), (146, 0, 96)) + lb(cam, (146, -20, 104), "矯正", -26, 0, "end")
    s += lb(cam, (318, 0, 80), "切断", 0, -4)
    for x in (50, 250):
        a = cam.xy((x, -18, -12))
        s += loc(a[0], a[1] + 2, -90)
    return title("棒鋼を切断し、曲がりを矯正") + s


def _eps1():
    def fn(sc):
        cam = sc.cam
        o = bb(cam, -10, -24, -46, 320, 48, 30, "m", dark=.5)
        o += rack(cam, True, False) + teeth_mf(cam)
        o += bb(cam, -70, -12, 16, 420, 24, 16, "t", ch=2)
        d = []
        for k in range(52):
            x = -66 + k * 8
            d += [(x, -12, 16), (x + 4, -12, 11.5), (x + 8, -12, 16)]
        o += pl3(cam, d, "ts3", True)
        return o
    s, cam = op(fn, 24, 24)
    s += arrow3(cam, (-40, 0, 52), (330, 0, 52)) + lb(cam, (150, 0, 52), "ブローチを引く", 0, -10)
    return title("ラック歯をブローチで加工（可変ギヤ比は冷間鍛造）") + s


def _eps2():
    WA = GE._norm((1, .2, 0))
    wc = (226, 0, 12 + 48)

    def fn(sc):
        cam = sc.cam
        ins = {RL: bb(cam, RL + 26, -26, -30, 40, 52, 60, "pt", dark=1) + cy(cam, (RL, 0, 0), XA, 3, 26, "m", seg=16, bands=6, r1=11),
               -1: cy(cam, (-26, 0, 0), XA, 11, 26, "m", seg=16, bands=6, r1=3)}
        o = bb(cam, -76, -26, -30, 50, 52, 60, "pt", dark=1)
        o += rack(cam, True, True, ins=ins)
        o += sil(cam, S0, S1, RR)
        o += cy(cam, add(wc, mul(WA, -5)), WA, 48, 10, "gw", seg=40, bands=10, holes=[GE.circle_outline(14, 16, 4)])
        return o
    s, cam = op(fn, 30, 22)
    s += arc3(cam, add(wc, mul(WA, -8)), WA, 56, 100, 175)
    s += arrow3(cam, (S0, -34, -34), (S1 + 10, -34, -34))
    s += lb(cam, ((S0 + S1) / 2, -34, -34), "リードに合わせて送り", 0, 22)
    s += lb(cam, (wc[0], 0, wc[2] + 48), "砥石", 0, -8)
    return title("ラックアシスト式では、ボールねじ溝を研削で仕上げる") + s


def _eps3():
    def fn(sc):
        cam = sc.cam
        coil = compact(GE.prism(cam, (104, 0, 0), XA, GE.circle_outline(22, 28, 8), 12, "cu", holes=[GE.circle_outline(15, 20, 6)], smooth="outer"))
        jk = compact(GE.prism(cam, (40, 0, 0), XA, GE.circle_outline(22, 28, 8), 8, "m", holes=[GE.circle_outline(16, 20, 6)], smooth="outer"))
        o = rack(cam, True, True, hot=(64, 104), ins={104: coil, 40: jk})
        return o
    s, cam = op(fn, 26, 22)
    a = cam.xy((44, -14, -18))
    s += drops(a[0] + 4, a[1] + 2, 5, 50, 22, 100)
    h = cam.xy((70, 0, 18))
    s += heat(h[0], h[1] - 4, 3, 12)
    s += arrow3(cam, (100, 0, 46), (170, 0, 46)) + lb(cam, (135, 0, 46), "移動焼入れコイル", 0, -10)
    s += lb(cam, (44, -18, -22), "冷却液", 0, 34)
    return title("ラック歯とねじ溝を高周波で移動焼入れ") + s


def _eps4():
    def fn(sc):
        cam = sc.cam
        o = cy(cam, (70, 78, -6), XA, 58, 160, "gw", seg=40, bands=12)
        o += bb(cam, 0, -3, -44, 300, 6, 32, "m")
        o += rack(cam, True, True) + sil(cam, 0, RL, RR)
        o += cy(cam, (70, -70, -14), XA, 44, 160, "dk", seg=36, bands=10)
        return o
    s, cam = op(fn, 22, 36)
    s += arc3(cam, (66, 78, -6), XA, 64, 40, 100) + arc3(cam, (66, -70, -14), XA, 50, 100, 160)
    s += lb(cam, (150, 78, 52), "砥石", 0, -8) + lb(cam, (150, -70, -58), "調整車", 0, 30)
    return title("焼入れの曲がりを矯正し、外径をセンタレス研削") + s


def _eps5():
    """same hobbing scene as before, slimmed (8 teeth, shorter hob) to stay under 25KB."""
    import il_gscene as GS
    from il3_ev import mrg
    s = title("ピニオンをホブ切り→浸炭→歯面研削")
    s += mrg(GS.sc_hobbing(186, 158, 1.25, lab=False, z=8, rp=38, width=56, shaft=(12, 40, 34), helix=30, hr=20, L=104, cut=0.6))
    s += text(118, 76, "ピニオン（ワーク）", "middle", "al") + text(330, 262, "ホブ", "middle", "al")
    return s + tol(300, 290, "ねじれ角の大きいピニオン")


def _eps6():
    def fn(sc):
        cam = sc.cam
        o = bb(cam, -170, -40, -66, 300, 80, 22, "pt", dark=1)
        for x in (-110, 50):
            o += bb(cam, x - 10, -12, -44, 20, 24, 22, "dk")
        o += eps_m(cam, ends=False, motor=False, bore=True)
        o += ring3(cam, (-150.3, 0, 0), XA, 15)
        o += cy(cam, (-250, 0, 0), XA, 10, 96, "t", seg=16, bands=6)
        o += cy(cam, (-300, 0, 0), XA, 26, 50, "dk", seg=24, bands=8)
        return o
    s, cam = op(fn, 30, 22)
    s += arc3(cam, (-280, 0, 0), XA, 32, 100, 175) + arrow3(cam, (-250, -40, 40), (-196, -40, 40))
    s += lb(cam, (-226, -40, 40), "送り", 0, -8)
    return title("アルミダイカストのハウジングを加工（同軸度）") + s


def _eps7():
    s, cam = op(lambda sc: eps_m(sc.cam), 18, 30, (20, 36, 460, 182), sh_ry=6, sh_k=.42)
    top = add(EPC, mul(EAP, 70))
    s += arc3(cam, top, EAP, 16, 200, 330)
    s += arrow3(cam, (-280, 0, -40), (-230, 0, -40), both=True)
    s += chart(310, 196, 150, 80, "ramp") + text(300, 236, "作動トルク", "end", "sm")
    return title("モータ・ECU・トルクセンサを組み付け、作動トルク・異音を全数確認") + s


@dpart("chassis.eps", "ops")
def eps_ops3():
    return [fin(x) for x in (_eps0(), _eps1(), _eps2(), _eps3(), _eps4(), _eps5(), _eps6(), _eps7())]


# =====================================================================================
# chassis.balljoint — outer tie-rod end: forged housing (socket) + boot + cold-headed ball stud, arm
# =====================================================================================
def sphere(cam, C, r, mat="w", sl=7, seg=20, bands=6):
    k0 = .12

    def sc_(t):
        z = -(1 - k0) + 2 * (1 - k0) * t
        return max(.2, math.sqrt(max(0, 1 - z * z)))
    return compact(GE.prism(cam, (C[0], C[1], C[2] - r * (1 - k0)), ZA, GE.circle_outline(r, seg, bands), 2 * r * (1 - k0), mat,
                            slices=sl, smooth=True, scale=sc_))


def vthreads(cam, x, y, z0, z1, r, pitch=3.0):
    d = ""
    a0 = math.atan2(-cam.D[1], -cam.D[0])
    z = z0
    while z + pitch * .4 < z1:
        d += P([cam.xy((x + r * math.cos(a0 + t), y + r * math.sin(a0 + t), z + t * .4)) for t in [(-1.4 + 2.8 * j / 8) for j in range(9)]], False)
        z += pitch
    return path(d, "gr")


def bj_stud(cam, x, y, stage=3, mat="w"):
    """ball stud standing on its ball (centre at z = 0): 0 slug, 1 upset, 2 ball + taper, 3 finished + rolled thread."""
    if stage == 0:
        return cy(cam, (x, y, -13), ZA, 7.5, 44, mat, seg=16, bands=6)
    if stage == 1:
        return cy(cam, (x, y, -13), ZA, 11, 15, mat, seg=18, bands=6) + cy(cam, (x, y, 2), ZA, 7, 36, mat, seg=16, bands=6)
    o = cy(cam, (x, y, 8), ZA, 6.5, 12, mat, seg=16, bands=6) + sphere(cam, (x, y, 0), 13, mat)
    o += cy(cam, (x, y, 20), ZA, 9.5, 24, mat, seg=18, bands=6, r1=7.6)
    o += cy(cam, (x, y, 44), ZA, 6.6, 16, mat, seg=16, bands=6)
    return o + (vthreads(cam, x, y, 46, 59, 6.6) if stage == 3 else "")


def bj_arm(cam, L=70):
    """forged neck from the housing along +x (far side at az > 0), optional threaded shank / rod / inner joint."""
    o = ""
    if L > 128:
        o += cy(cam, (250, 0, 0), XA, 17, 34, "w", seg=24, bands=8) + px(cam, 236, 14, banded(hexagon(14.5, 30), 1), "w", dark=.2)
        o += cy(cam, (128, 0, 0), XA, 8.5, 108, "w", seg=14, bands=6)
    if L > 80:
        o += cy(cam, (80, 0, 0), XA, 8, 48, "w", seg=14, bands=6) + threads(cam, 82, 126, 8, 3.6)
        o += px(cam, 70, 11, banded(hexagon(14, 30), 1), "w", dark=.2)
    o += cy(cam, (40, 0, 0), XA, 13, 30, "w", seg=20, bands=7)
    o += px(cam, 10, 32, banded(hull(arc(0, 0, 13, 0, 360, 10) + [(-9, 15), (9, 15), (-9, -15), (9, -15)]), 2), "w",
            smooth=True, dark=.4, cap_mat="w3", scale=lambda t: 1 - .15 * t)
    return o


def bj_head(cam, flip=False, boot=True, stud=True, arm=70, bore=False):
    """housing (z -16..14) with boot and stud on top; flip puts the stud below and the caulked mouth on top."""
    o = bj_arm(cam, arm) if arm else ""
    if not flip:
        o += cy(cam, (0, 0, -16), ZA, 22, 30, "w", seg=28, dark=.2)
        o += cy(cam, (0, 0, 14), ZA, 22.5, 3, "w", seg=28, bands=8)
        if bore:
            o += hole3(cam, (0, 0, 17.05), ZA, 13, "w3", 20) + hole3(cam, (0, 0, 17.1), ZA, 10.5, "bg", 20)
        if boot:
            o += cy(cam, (0, 0, 17), ZA, 20, 8, "dk", seg=24, bands=6, r1=17) + cy(cam, (0, 0, 25), ZA, 17, 6, "dk", seg=24, bands=6, r1=10.5)
        if stud:
            o += cy(cam, (0, 0, 31), ZA, 9.5, 24, "w", seg=18, bands=6, r1=7.6) + cy(cam, (0, 0, 55), ZA, 6.6, 16, "w", seg=16, bands=6)
            o += vthreads(cam, 0, 0, 57, 70, 6.6)
        return o
    s_ = ""
    if stud:
        s_ += cy(cam, (0, 0, -55), ZA, 6.6, 16, "w", seg=16, bands=6) + cy(cam, (0, 0, -55), ZA, 7.6, 24, "w", seg=18, bands=6, r1=9.5)
    if boot:
        s_ += cy(cam, (0, 0, -31), ZA, 10.5, 6, "dk", seg=24, bands=6, r1=17) + cy(cam, (0, 0, -25), ZA, 17, 8, "dk", seg=24, bands=6, r1=20)
    o = s_ + o
    o += cy(cam, (0, 0, -17), ZA, 22.5, 3, "w", seg=28, bands=8) + cy(cam, (0, 0, -14), ZA, 22, 30, "w", seg=28, dark=.2)
    return o + cy(cam, (0, 0, 16), ZA, 16, 1.5, "w", seg=24, bands=6, dark=1)


def bj_sec(x, y, k=1.0, boot=True):
    """small 2D section of the joint: housing (cut), resin seat, ball stud, boot."""
    def R(a, b, w, h, c):
        return rect(x + a * k, y + b * k, w * k, h * k, c)
    s = R(-24, -16, 48, 34, "cut") + circ(x, y, 17 * k, "dk") + R(-16, 14, 32, 6, "w") + circ(x, y, 13 * k, "w")
    s += R(-9, -30, 18, 22, "bg") + R(-6.5, -60, 13, 50, "w")
    if boot:
        s += path(P([(x - 22 * k, y - 16 * k), (x - 18 * k, y - 30 * k), (x - 9 * k, y - 34 * k), (x - 7 * k, y - 28 * k)]), "dk")
        s += path(P([(x + 22 * k, y - 16 * k), (x + 18 * k, y - 30 * k), (x + 9 * k, y - 34 * k), (x + 7 * k, y - 28 * k)]), "dk")
    return s


@dpart("chassis.balljoint", "detail")
def balljoint_detail3():
    notes = [("ボールスタッド", "冷間圧造。ボール部を焼入れ・研削"), ("ソケット", "樹脂シートを介してボールを保持"), ("ねじ部", "転造ねじ"), ("ダストブーツ", "泥水の浸入を防ぐ")]
    s, cam = op(lambda sc: bj_head(sc.cam, arm=284), 22, 22, (16, 30, 352, 236), sh_ry=7, sh_k=.46)
    s += rect(362, 70, 108, 150, "m", 4) + text(416, 86, "断面", "middle", "sm") + bj_sec(416, 168, 1.5)
    a1, a2, a3, a4 = cam.xy((-7, -6, 40)), cam.xy((-16, -14, -4)), cam.xy((104, -6, 6)), cam.xy((-12, -12, 24))
    s += bal(*a1, 60, 40, 1) + bal(*a2, 60, 250, 2) + bal(*a3, 200, 272, 3) + bal(*a4, 150, 30, 4)
    s += bal(416, 168, 392, 250, 1).replace("leadd", "leadd") if False else ""
    return s, notes


def _bj0():
    xs = (-150, -50, 50, 150)

    def fn(sc):
        cam = sc.cam
        o = ""
        for i in (3, 2, 1, 0):
            x = xs[i]
            o += bb(cam, x - 26, -26, -43, 52, 52, 30, "m", ch=3, dark=.3)
            if i == 3:
                o += bb(cam, x + 8, -12, 40, 5, 24, 22, "t")
            o += bj_stud(cam, x, 0, i)
            if i == 3:
                o += bb(cam, x - 13, -12, 40, 5, 24, 22, "t")
        return o
    s, cam = op(fn, 22, 20)
    s += arrow3(cam, (-190, -40, -60), (190, -40, -60)) + lb(cam, (0, -40, -60), "多段で成形", 0, 22)
    s += lb(cam, (150, 0, 70), "ねじ転造", 0, -6)
    return title("線材を冷間圧造でボールスタッドにし、ねじを転造") + s


def _bj1():
    def fn(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -30), ZA, 12, 17, "m", seg=18, bands=6)
        o += bj_stud(cam, 0, 0, 3)
        o += cy(cam, (48, 10, 0), (0, -1, 0), 34, 20, "gw", seg=36, bands=10, holes=[GE.circle_outline(9, 14, 4)])
        return o
    s, cam = op(fn, 18, 18, (60, 44, 420, 262))
    c = cam.xy((0, 0, 0))
    r = 13 * cam.s
    s += circ(c[0], c[1], r + 1, "mf")
    s += path("M%s %s A%s %s 0 0 1 %s %s" % (n(c[0] - r - 5), n(c[1]), n(r + 5), n(r + 5), n(c[0]), n(c[1] - r - 5)), "hotarc")
    s += arc3(cam, (0, 0, 64), ZA, 14, 120, 260) + arc3(cam, (48, -12, 0), YA, 40, 300, 360)
    s += lb(cam, (-14, 0, 8), "焼入れ層", -14, 0, "end") + lb(cam, (48, -10, 34), "砥石", 0, -10)
    return title("ボール部を高周波焼入れし、球面を研削") + s + tol(40, 284, "真球度・粗さ")


def _bj2():
    def fn(sc):
        cam = sc.cam
        o = bb(cam, -40, -40, -40, 80, 80, 24, "pt", dark=1)
        o += bj_head(cam, boot=False, stud=False, bore=True)
        o += ring3(cam, (0, 0, 17.1), ZA, 13)
        o += cy(cam, (0, 0, 40), ZA, 6, 60, "t", seg=14, bands=5) + cy(cam, (0, 0, 100), ZA, 18, 26, "dk", seg=20, bands=6)
        return o
    s, cam = op(fn, 22, 26, (40, 40, 320, 268))
    s += arc3(cam, (0, 0, 60), ZA, 12, 120, 260) + arrow3(cam, (-34, 0, 96), (-34, 0, 54))
    s += lb(cam, (-34, 0, 76), "送り", -8, 0, "end")
    s += rect(340, 60, 126, 170, "m", 4) + text(403, 76, "断面", "middle", "sm")
    x, y = 403, 160
    s += rect(x - 36, y - 24, 72, 51, "cut") + circ(x, y, 25, "void") + rect(x - 14, y - 46, 28, 30, "void") + rect(x - 22, y + 14, 44, 13, "void")
    s += path("M%s %s A25 25 0 0 1 %s %s" % (n(x - 23), n(y + 10), n(x - 12), n(y - 22)), "mf")
    s += path("M%s %s A25 25 0 0 0 %s %s" % (n(x + 23), n(y + 10), n(x + 12), n(y - 22)), "mf")
    return title("ソケットを鍛造・旋削し、内面を仕上げる") + s


def _bj3():
    def fn(sc):
        cam = sc.cam
        o = bj_head(cam, flip=True)
        o += ring3(cam, (0, 0, 16.2), ZA, 21.6)
        o += cy(cam, (0, 0, 34), ZA, 27, 22, "t", seg=28, bands=8, holes=[GE.circle_outline(15, 16, 4)])
        return o
    s, cam = op(fn, 22, 26, (60, 40, 420, 268))
    s += arrow3(cam, (-40, 0, 76), (-40, 0, 44))
    s += lb(cam, (-40, 0, 60), "口元かしめ", -12, 4, "end")
    return title("樹脂シートとスタッドを入れ、口元をかしめる") + s


def _bj4():
    s, cam = op(lambda sc: bj_head(sc.cam, arm=128), 22, 22, (24, 44, 300, 268), sh_ry=6, sh_k=.46)
    s += arc3(cam, (0, 0, 46), ZA, 16, 120, 300)
    s += arc3(cam, (0, 0, 0), YA, 92, 62, 118)
    s += lb(cam, (16, 0, 46), "回転", 8, 4, "start") + lb(cam, (-44, 0, 82), "揺動", -6, 0, "end")
    s += chart(320, 170, 140, 80, "ramp") + text(390, 266, "トルク・ガタ", "middle", "sm")
    return title("揺動トルク・回転トルク・ガタを確認") + s


@dpart("chassis.balljoint", "ops")
def balljoint_ops3():
    return [fin(x) for x in (_bj0(), _bj1(), _bj2(), _bj3(), _bj4())]


# =====================================================================================
# ev.rotor — IPM rotor (same model as p:ev.rotor): laminated core, V magnet pockets, hollow shaft
# =====================================================================================
RO_R, RO_H, RO_S, RO_NP = 86, 64, 21, 8


def lam_at(cam, C, R, H, n_):
    d = ""
    a0 = math.degrees(math.atan2(-cam.D[1], -cam.D[0]))
    for j in range(1, n_):
        z = C[2] + H * j / n_
        d += P([cam.xy((C[0] + R * math.cos(math.radians(a)), C[1] + R * math.sin(math.radians(a)), z)) for a in range(int(a0) - 88, int(a0) + 89, 8)], False)
    return path(d, "gr")


def ro_pocket(k, sg, t, d0=0.0, d1=0.0, z=RO_H + .05):
    """world quad of the magnet pocket (pole k, leg sg) on the core end face, half-thickness t."""
    a = 2 * PI * k / RO_NP + math.radians(8)
    c, s_ = math.cos(a), math.sin(a)
    p0, p1 = (42, sg * 5), (74, sg * 25)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    tu, tv = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    q = [(p0[0] + tu * d0 + tv * t, p0[1] + tv * d0 - tu * t), (p0[0] + tu * (L + d1) + tv * t, p0[1] + tv * (L + d1) - tu * t),
         (p0[0] + tu * (L + d1) - tv * t, p0[1] + tv * (L + d1) + tu * t), (p0[0] + tu * d0 - tv * t, p0[1] + tv * d0 + tu * t)]
    return [(u * c - v * s_, u * s_ + v * c, z) for u, v in q]


def ro_core(cam, mags=None, z0=0.0, holes=True, shaft_bore=False):
    """laminated core with end-face pockets; mags = set of poles that already hold magnets (None = all)."""
    o = GE.prism(cam, (0, 0, z0), ZA, GE.circle_outline(RO_R, 64, 16), RO_H, "w", holes=[GE.circle_outline(RO_S, 28, 7)] if shaft_bore else [])
    o += lam_lines(cam, RO_R, RO_H, 9) if z0 == 0 else ""
    top = []
    for k in range(RO_NP):
        for sg in (1, -1):
            top.append(P([cam.xy((x, y, z + z0)) for x, y, z in ro_pocket(k, sg, 3.6, -2.5, 3)]))
    o += path("".join(top), "bg")
    mg = [P([cam.xy((x, y, z + z0)) for x, y, z in ro_pocket(k, sg, 2.6, 1, -1)]) for k in range(RO_NP) for sg in (1, -1)
          if mags is None or k in mags]
    if mg:
        o += path("".join(mg), "dk")
    if holes:
        hb = ""
        for k in range(RO_NP):
            b = 2 * PI * k / RO_NP + math.radians(8) + PI / RO_NP
            hb += P(circ3(cam, (34 * math.cos(b), 34 * math.sin(b), RO_H + .05 + z0), ZA, 6.5, 14))
        o += path(hb, "bg")
    return o


def ro_shaft_low(cam, z=0.0):
    return cy(cam, (0, 0, z - 40), ZA, RO_S - 3, 16, "w", seg=24, bands=8) + cy(cam, (0, 0, z - 24), ZA, RO_S, 24, "w", seg=24, bands=8)


def ro_shaft_top(cam, z=RO_H, boss=True):
    H = z
    o = cy(cam, (0, 0, H), ZA, 30, 4, "w", seg=32, bands=10, dark=1, cap_mat="w2") if boss else ""
    o += cy(cam, (0, 0, H + 4), ZA, RO_S, 22, "w", seg=24, bands=8)
    o += cy(cam, (0, 0, H + 26), ZA, RO_S - 3, 6, "w", seg=24, bands=8, dark=1)
    o += compact(GE.prism(cam, (0, 0, H + 32), ZA, GE.spline_outline(22, RO_S - 4, RO_S - 6), 20, "w"))
    return o + hole3(cam, (0, 0, H + 52.05), ZA, 9, "w3", 18) + hole3(cam, (0, 0, H + 52.1), ZA, 7.4, "bg", 18)


def silz(cam, x, y, z0, z1, r, c="mf"):
    t = math.atan2(-cam.D[0], cam.D[1])
    d = ""
    for tt in (t, t + PI):
        a, b = cam.xy((x + r * math.cos(tt), y + r * math.sin(tt), z0)), cam.xy((x + r * math.cos(tt), y + r * math.sin(tt), z1))
        d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    return path(d, c)


def ro_plate(cam, z=RO_H, gap=95):
    """end plate (thin disc) with a sector left open toward the viewer to show the magnets."""
    av = math.degrees(math.atan2(-cam.D[1], -cam.D[0]))
    items = []
    for a0, a1 in ((av + gap / 2, av + 180), (av + 180, av + 360 - gap / 2)):
        xy = [(0, 0)] + arc(0, 0, RO_R - 4, a0, a1, 14)
        c = ((RO_R / 2) * math.cos(math.radians((a0 + a1) / 2)), (RO_R / 2) * math.sin(math.radians((a0 + a1) / 2)), z)
        items.append((cam.P(c)[2], pz(cam, z, 3, banded(xy, 2), "w", dark=.3)))
    return "".join(s for _, s in sorted(items, key=lambda t: -t[0]))


@dpart("ev.rotor", "detail")
def rotor_detail3():
    notes = [("積層コア", "電磁鋼板を数百枚積層（かしめ・接着）"), ("永久磁石", "ネオジム焼結磁石をコアの穴に埋め込み（IPM）"),
             ("シャフト", "軸受部を研削。コアに圧入・焼ばめ"), ("エンドプレート", "磁石の飛び出し防止・バランス修正部")]
    s, cam = op(lambda sc: ro_shaft_low(sc.cam) + ro_core(sc.cam) + ro_plate(sc.cam) + ro_shaft_top(sc.cam, RO_H + 3, False), -30, 30,
                (20, 26, 280, 276), sh_ry=8, sh_k=.56, sh_dy=-4)
    pl = Pl(316, 150, .52)
    s += rect(298, 70, 172, 160, "m", 4) + text(384, 86, "断面", "middle", "sm") + pl.g(V.rotor_sec())
    m = ro_pocket(6, 1, 0)
    a1, a2, a3, a4 = cam.xy((-60, -60, 30)), pl(130, -38), cam.xy((-14, -14, RO_H + 30)), cam.xy((40, 50, RO_H + 3))
    s += bal(*a1, 40, 250, 1) + bal(*a2, 400, 260, 2) + bal(*a3, 60, 40, 3) + bal(*a4, 270, 40, 4)
    return s, notes


def _ro0():
    xs = (-170, -100, -30, 40)

    def fn(sc):
        cam = sc.cam
        o = cy(cam, (190, 0, -60), ZA, 44, 50, "w", seg=40, bands=12) + lam_at(cam, (190, 0, -60), 44, 50, 8)
        o += bb(cam, -220, -60, -40, 300, 120, 34, "m", dark=.4)
        o += bb(cam, -240, -52, -6, 310, 104, 1.6, "w")
        mk = ""
        for i, x in enumerate(xs):
            for yy in (-38, 38):
                mk += P(circ3(cam, (x, yy, -4.3), ZA, 3, 10))
            if i >= 1:
                mk += P(circ3(cam, (x, 0, -4.3), ZA, 10, 16))
            if i >= 2:
                for k in range(8):
                    a = 2 * PI * k / 8
                    mk += P(circ3(cam, (x + 30 * math.cos(a), 30 * math.sin(a), -4.3), ZA, 3.4, 8))
            if i == 3:
                mk += P(circ3(cam, (x, 0, -4.3), ZA, 44, 36))
        o += path(mk, "bg")
        for x in reversed(xs):
            o += cy(cam, (x, 0, 16), ZA, 10 if x < 40 else 40, 54, "t", seg=20 if x < 40 else 32, bands=6)
        return o
    s, cam = op(fn, 18, 26)
    s += arrow3(cam, (-230, -70, -40), (60, -70, -40)) + lb(cam, (-90, -70, -40), "帯材送り（300〜600spm）", 0, 20)
    s += lb(cam, (190, -44, -60), "積層", 0, 20) + arrow3(cam, (40, -80, 0), (150, -80, -40))
    return title("高速プレスで電磁鋼板を打ち抜き、型内でかしめ積層") + s


def _ro1():
    def fn(sc):
        cam = sc.cam
        o = ro_core(cam, mags={0, 1, 2, 3, 4, 7})
        q = ro_pocket(6, 1, 2.6, 1, -1, 0)
        q2 = ro_pocket(6, -1, 2.6, 1, -1, 0)
        for qq in (q, q2):
            o += pl3(cam, [(x, y, RO_H + .1) for x, y, _ in ro_pocket(6, 1 if qq is q else -1, 3.6, -2.5, 3)], "mf", True)
        for qq in sorted((q, q2), key=lambda qq: -cam.P(qq[0])[2]):
            o += pz(cam, RO_H + 34, 30, [(x, y) for x, y, _ in qq], "dk")
        return o
    s, cam = op(fn, -30, 34, (60, 40, 400, 268))
    c = ro_pocket(6, 1, 0, 0, 0, RO_H + 64)
    s += arrow3(cam, (c[0][0] + 30, c[0][1], RO_H + 64), (c[0][0] + 30, c[0][1], RO_H + 10))
    s += lb(cam, (c[0][0] + 30, c[0][1], RO_H + 50), "N/S の向き", 10, 0, "start")
    s += lb(cam, (-80, -40, 10), "樹脂充填", -10, 0, "end")
    return title("磁石をコアの穴に挿入し、樹脂充填で固定") + s


def _ro2():
    zs = RO_H + 30

    def fn(sc):
        cam = sc.cam
        o = ro_core(cam, shaft_bore=True)
        o += ro_shaft_low(cam, zs) + ro_shaft_top(cam, zs, False)
        o += silz(cam, 0, 0, zs - 24, zs, RO_S) + silz(cam, 0, 0, zs + 4, zs + 26, RO_S)
        o += cy(cam, (64, 0, zs + 4), ZA, 40, 22, "gw", seg=36, bands=10)
        return o
    s, cam = op(fn, -30, 30, (60, 40, 420, 268))
    s += arrow3(cam, (-34, 0, zs + 60), (-34, 0, zs + 26)) + lb(cam, (-34, 0, zs + 60), "圧入", 0, -6)
    s += arc3(cam, (64, 0, zs + 30), ZA, 46, 200, 300) + lb(cam, (64, 0, zs + 26), "砥石", 54, 0, "start")
    return title("シャフトを旋削・研削し、コアに圧入") + s


def _ro3():
    def fn(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -84), ZA, 60, 20, "pt", seg=36, bands=10, dark=1) + cy(cam, (0, 0, -64), ZA, 14, 24, "m", seg=20, bands=6)
        o += ro_shaft_low(cam) + ro_core(cam) + ro_plate(cam, gap=0.01) + ro_shaft_top(cam, RO_H + 3, False)
        mk = ""
        for a in (200, 240):
            mk += P(circ3(cam, (66 * math.cos(math.radians(a)), 66 * math.sin(math.radians(a)), RO_H + 3.1), ZA, 4, 12))
        o += path(mk, "mfa")
        x, y = 66 * math.cos(math.radians(240)), 66 * math.sin(math.radians(240))
        o += cy(cam, (x, y, RO_H + 16), ZA, 3.4, 30, "t", seg=12, bands=4) + cy(cam, (x, y, RO_H + 46), ZA, 12, 24, "dk", seg=18, bands=6)
        return o
    s, cam = op(fn, -30, 30, (60, 40, 420, 268))
    s += arc3(cam, (0, 0, 20), ZA, 100, 200, 330)
    s += lb(cam, (66 * math.cos(math.radians(240)), 66 * math.sin(math.radians(240)), RO_H + 3), "修正穴", 14, 22, "start")
    return title("高回転に備えてアンバランスを修正") + s + tol(300, 284, "1.5〜2万min⁻¹で回る")


def _ro4():
    def fn(sc):
        cam = sc.cam
        items = []
        for k in range(8):
            a = 2 * PI * k / 8 + math.radians(8)
            xy = arc(0, 0, 124, math.degrees(a) - 15, math.degrees(a) + 15, 3) + arc(0, 0, 92, math.degrees(a) + 15, math.degrees(a) - 15, 2)
            blk = pz(cam, 0, RO_H, banded(xy, 1), "m", dark=.3)
            cu = pz(cam, 20, 24, banded(arc(0, 0, 128, math.degrees(a) - 17, math.degrees(a) + 17, 3) +
                                        arc(0, 0, 100, math.degrees(a) + 17, math.degrees(a) - 17, 2), 1), "cu", lines=False)
            items.append((cam.P((108 * math.cos(a), 108 * math.sin(a), 30))[2], blk + cu))
        items.append((0.0, ro_core(cam) + ro_shaft_top(cam)))
        return "".join(s for _, s in sorted(items, key=lambda t: -t[0]))
    s, cam = op(fn, -30, 34, (24, 40, 300, 268))
    s += lightning(300, 66, 1.4) + chart(320, 140, 140, 80, "sine") + text(390, 236, "表面磁束分布", "middle", "sm")
    s += lb(cam, (0, -128, 0), "着磁ヨーク（コイル）", 0, 26)
    return title("パルス磁界で磁石を着磁し、表面磁束を確認") + s


@dpart("ev.rotor", "ops")
def rotor_ops3():
    return [fin(x) for x in (_ro0(), _ro1(), _ro2(), _ro3(), _ro4())]


# =====================================================================================
# ev.eaxlecase — motor housing + gear case (same shape as p:ev.eaxlecase), built in a Scene
# =====================================================================================
from il3_lib import CYL, X, RAW, BOX

EM, EL, EG, ELG, EDY, EDZ = 66, 170, 170, 64, -26, -96


def ec_build(sc, mat="w", face=True, ports=True):
    """add the case to Scene sc (open motor end with the stator bore at x = 0, gear case at +x)."""
    def gc(gro=0.0):
        return banded(hull(arc(0, 0, EM + 14 + gro, 0, 360, 16) + arc(EDY, EDZ, 62 + gro, 0, 360, 16)), 3)
    fl = []
    for k in range(32):
        t = 2 * PI * k / 32
        r = EM + 9 + (6 if k % 4 == 2 else 0)
        fl.append((r * math.cos(t), r * math.sin(t)))
    X(sc, 0, 9, banded(hull(fl), 3), mat, smooth=True)
    if face:
        def fc(s_):
            o = hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), EM - 2, mat + "3" if mat == "w" else "hs3", 40) + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), EM - 7, "bg", 40)
            for k in range(8):
                t = 2 * PI * (k + .5) / 8
                o += hole3(s_.cam, (-.1, (EM + 11) * math.cos(t), (EM + 11) * math.sin(t)), (-1, 0, 0), 2.6, "bg", 8)
            return o
        RAW(sc, fc, ((-.2, -EM - 15, -EM - 15), (0, EM + 15, EM + 15)), -2)
    x = 9
    for L, r in ((50, EM), (5, EM + 4), (52, EM), (5, EM + 4), (EL - 9 - 112, EM)):
        CYL(sc, (x, 0, 0), XA, r, L, mat, seg=32, bands=8, dark=0 if r == EM else 1)
        x += L
    if ports:
        for xx in (34, 140):
            CYL(sc, (xx, -20, 62), ZA, 6, 16, mat, seg=14, bands=5)
            RAW(sc, lambda s_, xx=xx: hole3(s_.cam, (xx, -20, 78.05), ZA, 3.6, "bg", 10), ((xx - 6, -26, 78), (xx + 6, -14, 78.1)), -1)
    X(sc, EG, 30, gc(), mat, smooth=True)
    X(sc, EG + 30, 6, gc(3), mat, smooth=True, dark=1)
    X(sc, EG + 36, ELG - 36, gc(), mat, smooth=True)
    CYL(sc, (EG - 18, EDY, EDZ), XA, 30, 18, mat, seg=24, bands=8)
    RAW(sc, lambda s_: hole3(s_.cam, (EG - 18.1, EDY, EDZ), (-1, 0, 0), 20, "w3" if mat == "w" else "hs3", 20) +
        hole3(s_.cam, (EG - 18.1, EDY, EDZ), (-1, 0, 0), 15, "bg", 20), ((EG - 18.2, EDY - 30, EDZ - 30), (EG - 18.1, EDY + 30, EDZ + 30)), -2)


@dpart("ev.eaxlecase", "detail")
def eaxlecase_detail3():
    notes = [("ステータ嵌合穴", "ステータを焼ばめする大径穴。軸受穴との同軸度"), ("冷却水路", "ハウジング外周の水路（鋳造で成形）"),
             ("軸受穴", "ロータ軸を支える"), ("減速機側フランジ", "ギヤケースとの合わせ面")]
    s, cam = op(ec_build, 30, 22, (16, 24, 270, 276), sh_ry=7, sh_k=.5, sh_dy=-4)
    pl = Pl(300, 150, 0.8)
    s += rect(280, 40, 190, 230, "m", 4) + text(375, 56, "断面", "middle", "sm") + pl.g(V.ecase_sec())
    a1, a4 = cam.xy((-.2, -20, EM - 4)), cam.xy((EG + 33, -EM, -40))
    s += bal(*a1, 40, 40, 1) + bal(*pl(37, -73), 460, 30, 2) + bal(*pl(6, -22), 300, 280, 3) + bal(*a4, 250, 286, 4)
    return s, notes


def _ec0():
    def fn(sc):
        ec_build(sc, "h", face=True, ports=False)
        BOX(sc, 250, -130, -190, 70, 260, 290, "pt", dark=1)
        BOX(sc, -230, -130, -190, 70, 260, 290, "pt", dark=1)
    s, cam = op(fn, 30, 18, (40, 36, 440, 262))
    s += arrow3(cam, (-150, -130, 40), (-60, -130, 40)) + lb(cam, (-150, -130, 40), "型締め", -6, 4, "end")
    s += lb(cam, (285, -130, -190), "固定型", 0, 16) + lb(cam, (-195, -130, -190), "可動型", 0, 16)
    return title("大型ケースを高圧ダイカスト（冷却水路も一体で成形）") + s + text(240, 290, "型締力2,500〜4,000t", "middle")


def _ec1():
    def fn(sc):
        ec_build(sc)
        BOX(sc, 150, 160, -150, 200, 10, 250, "m", dark=.5)
        BOX(sc, -170, -150, 0, 50, 50, 50, "dk")
    s, cam = op(fn, 30, 22, (30, 40, 450, 268))
    a = cam.xy((-120, -125, 25))
    d = ""
    for k in range(6):
        b = cam.xy((150, 160, -140 + k * 46))
        d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    s += path(d, "ray")
    p = cam.xy((70, -30, 60))
    s += circ(p[0], p[1], 3, "poro") + circ(p[0], p[1], 12, "mfring")
    s += lb(cam, (-145, -150, 50), "X線源", 0, -8) + lb(cam, (250, 160, 100), "検出器", 0, -8)
    return title("水路・シール面の鋳巣をX線で確認") + s


def _ec2():
    def fn(sc):
        BOX(sc, -10, -90, -200, 250, 180, 20, "pt", dark=1)
        ec_build(sc)

        def mk(s_):
            return ring3(s_.cam, (-.3, 0, 0), XA, EM - 2, "mf", 40) + ring3(s_.cam, (-.3, 0, 0), XA, EM + 12, "mf", 40)
        RAW(sc, mk, ((-.5, -EM - 15, -EM - 15), (-.3, EM + 15, EM + 15)), -3)
    s, cam = op(fn, 30, 20, (150, 40, 460, 262))
    c = cam
    s += cy(c, (-230, 0, 0), XA, 30, 50, "dk", seg=24, bands=8) + cy(c, (-180, 0, 0), XA, 9, 200, "t", seg=16, bands=6)
    s += cy(c, (-112, 0, 0), XA, EM - 9, 8, "t", seg=32, bands=8)
    s += arc3(c, (-206, 0, 0), XA, 36, 100, 175) + arrow3(c, (-180, -80, 70), (-110, -80, 70))
    s += lb(c, (-180, -80, 70), "ボーリングバー", -6, 4, "end")
    for xx in (40, 150):
        a = c.xy((xx, -60, -84))
        s += loc(a[0], a[1] + 1, -90)
    return title("ステータ嵌合穴・軸受穴・合わせ面を加工（同軸度）") + s + tol(40, 286, "ステータ穴と軸受穴の同軸度（ボーリングバーで一括）")


def _ec3():
    def fn(sc):
        ec_build(sc)
        BOX(sc, 250, -140, -170, 90, 70, 110, "m", ch=4)
    s, cam = op(fn, 30, 22, (40, 40, 440, 262))
    g = cam.xy((295, -140, -95))
    s += circ(g[0] - 4, g[1] - 4, 14, "w") + line(g[0] - 4, g[1] - 4, g[0] + 4, g[1] - 12, "o")
    d = ""
    for xx in (34, 140):
        a, b = cam.xy((xx, -20, 80)), cam.xy((300, -110, -60))
        d += "M%s %sC%s %s %s %s %s %s" % (n(a[0]), n(a[1]), n(a[0]), n(a[1] - 50), n(b[0]), n(b[1] - 80), n(b[0]), n(b[1]))
    s += path(d, "cable")
    p = cam.xy((60, 0, 70))
    s += drops(p[0] - 40, p[1] - 50, 6, 50, 26, 100) + text(p[0] - 50, p[1] - 56, "洗浄", "end", "al")
    s += lb(cam, (295, -140, -170), "リークテスタ（圧力降下）", 0, 18)
    return title("洗浄し、冷却水路の漏れを確認") + s


def _ec4():
    def fn(sc):
        ec_build(sc, ports=False)
    s, cam = op(fn, 30, 22, (200, 40, 460, 262))
    st = ""
    xs = -150
    st += cy(cam, (xs + 100, 0, 0), XA, EM - 22, 14, "cu", seg=28, bands=8, holes=[GE.circle_outline(EM - 34, 20, 5)])
    st += cy(cam, (xs, 0, 0), XA, EM - 4, 100, "m", seg=36, bands=10, holes=[GE.circle_outline(EM - 32, 24, 6)])
    st += cy(cam, (xs - 14, 0, 0), XA, EM - 22, 14, "cu", seg=28, bands=8, holes=[GE.circle_outline(EM - 34, 20, 5)])
    s += st + lam_x(cam, xs, xs + 100, EM - 4, 10)
    for xx in (30, 100):
        h = cam.xy((xx, 0, EM + 8))
        s += heat(h[0], h[1] - 4, 3, 10)
    s += arrow3(cam, (-140, -90, -40), (-30, -90, -40)) + lb(cam, (-85, -90, -40), "挿入", 0, 20)
    s += lb(cam, (60, 0, EM + 30), "ケースを加熱", 0, -8) + lb(cam, (xs + 50, 0, EM), "ステータ", 0, -12)
    return title("ケースを加熱して膨らませ、ステータを焼ばめ") + s + tol(300, 286, "しめしろ・位置")


def lam_x(cam, x0, x1, r, n_):
    """stack lines on the visible side of a cylinder along x."""
    d = ""
    a0 = math.atan2(-cam.D[2], -cam.D[1])
    for j in range(1, n_):
        x = x0 + (x1 - x0) * j / n_
        d += P([cam.xy((x, r * math.cos(a0 + t), r * math.sin(a0 + t))) for t in [(-1.5 + 3 * k / 10) for k in range(11)]], False)
    return path(d, "gr")


@dpart("ev.eaxlecase", "ops")
def eaxlecase_ops3():
    return [fin(x) for x in (_ec0(), _ec1(), _ec2(), _ec3(), _ec4())]
