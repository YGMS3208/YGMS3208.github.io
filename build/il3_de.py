"""v3 shaded-3D detail + op drawings (480x300) for drivetrain.valvebody / cvtpulley / diffcase / cvj and
chassis.knuckle. The 3D part models are the ones of the v3 part drawings (il3_drive / il3_chassis), reused by
capturing their inner scene function; titles, tolerance notes and detail notes follow the older sheets."""
import math
import re
import il_gear as GE
from il_base import *
from il_detail import *
from il_dmap import dpart
from il3_lib import compact, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3, svg_extent
from il_mt import Scene
from il_pictos import nozzle, dots, chart, conveyor
from il3_qb import sandify, stream
import il_d_drive as D
import il_d_chassis as DC
import il3_drive as PD
import il3_chassis as PC

PI = math.pi


# =====================================================================================
# infrastructure
# =====================================================================================
def grab(mod, f, *a, **k):
    """run a v3 part function with its module's fit() swapped out -> (scene fn, az, el)."""
    cap = {}
    old = mod.fit

    def fake(fn, az, el, *aa, **kk):
        cap.update(fn=fn, az=az, el=el)
        return ""
    mod.fit = fake
    try:
        f(*a, **k)
    finally:
        mod.fit = old
    return cap["fn"], cap["az"], cap["el"]


def _split(r):
    if isinstance(r, tuple):
        return r[0] or "", r[1] or ""
    return "", r or ""


def fit3(fn, az, el, area=(30, 40, 450, 272), sh=True, sh_k=.46, sh_ry=9, sh_dy=-3):
    """like il3_lib.fit, but fn(sc) may return (svg under the scene, svg over it). -> (svg, cam)"""
    pr = Scene(0, 0, az, el, 1.0)
    pre, post = _split(fn(pr))
    body, _ = pr.render(shadow_=False)
    x0, y0, x1, y1 = svg_extent(pre + body + post)
    L, T, R, B = area
    k = min((R - L) / (x1 - x0), (B - T) / (y1 - y0))
    ox = L + ((R - L) - (x1 - x0) * k) / 2 - x0 * k
    oy = T + ((B - T) - (y1 - y0) * k) / 2 - y0 * k
    sc = Scene(ox, oy, az, el, k)
    pre, post = _split(fn(sc))
    body, _ = sc.render(shadow_=False)
    out = ""
    if sh:
        ex = svg_extent(pre + body + post)
        out = shadow((ex[0] + ex[2]) / 2, ex[3] + sh_dy, (ex[2] - ex[0]) * sh_k, sh_ry)
    return out + pre + body + post, sc.cam


_HOT = {"w": "h", "ws1": "hs1", "ws2": "hs2", "ws3": "hs3", "ws4": "hs4", "w2": "hs2", "w3": "hs3"}


def hot(svg):
    return re.sub(r'class="(w|ws[1-4]|w2|w3)"', lambda m: 'class="%s"' % _HOT[m.group(1)], svg)


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def lab(cam, p, t, dx=0, dy=0, a="middle"):
    x, y = cam.xy(p)
    return al(x + dx, y + dy, t, a)


def poly3(cam, pts, cls, close=True):
    return path(P([cam.xy(p) for p in pts], close), cls)


def ring3(cam, C, A, r, cls="mf", seg=36):
    return path(P(circ3(cam, C, A, r, seg)), cls)


def cyl_s(cam, O, A, r, h, mat="t", seg=24, bands=8, r1=None, **kw):
    """stand-alone smooth cylinder svg (manual painter's order)."""
    a = GE._norm(A)
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, a, GE.circle_outline(r, seg, bands), h, mat, smooth=True, scale=scale, **kw))


def add3(p, a, k=1.0):
    return tuple(p[i] + a[i] * k for i in range(3))


def spindle(sc, tip, A, r, L, mat="t", rh=None, hl=22, nose=True, bias=0.0):
    """rotating tool from its tip along A (toward the machine): tool, taper holder, spindle nose."""
    a = GE._norm(A)
    rh = rh or max(r * 1.6, 9)
    CYL(sc, tip, a, r, L, mat, bias, seg=24, bands=8)
    p = add3(tip, a, L)
    CYL(sc, p, a, rh * .7, hl, "m", bias, seg=24, bands=8, r1=rh)
    if nose:
        CYL(sc, add3(p, a, hl), a, rh * 1.5, 14, "dk", bias, seg=28, bands=8)
    return add3(p, a, hl + 14)


def sheet(fn, az, el, ttl, area=(30, 40, 450, 272), extra=None, **kw):
    s, cam = fit3(fn, az, el, area, **kw)
    s = title(ttl) + s
    if extra:
        s += extra(cam)
    return fin(s)


def inset(x, y, w, h, cap, body):
    return rect(x, y, w, h, "m", 4) + text(x + w / 2, y + 16, cap, "middle", "sm") + body


# =====================================================================================
# drivetrain.valvebody — die-cast Al block (W 220 x D 130 x H 34): maze on the top (mating) face,
# spool bores along the -y face
# =====================================================================================
VB_W, VB_D, VB_H = 220, 130, 34
VB_FN, VB_AZ, VB_EL = grab(PD, PD.valve_body)
VB_BORES = list(range(24, VB_W - 10, 30))


def vb_top(cam, cls="mf", z=VB_H + .2):
    return poly3(cam, [(0, 0, z), (VB_W, 0, z), (VB_W, VB_D, z), (0, VB_D, z)], cls)


@dpart("drivetrain.valvebody", "detail")
def valvebody_detail3():
    s, cam = fit3(VB_FN, VB_AZ, VB_EL, (8, 60, 282, 272))
    pl = Pl(286, 92, 0.56)
    s += inset(290, 40, 182, 100, "断面（スプール穴）", pl.g(D.vb_sec()))
    notes = [("油路（迷路状）", "ダイカストで成形した複雑な油路"), ("スプール穴", "スプール弁が滑る穴。径公差数μm"),
             ("合わせ面", "セパレートプレートとの合わせ面。平面度0.02〜0.05mm"), ("交差穴", "油路とスプール穴の交差部。バリが固着の原因")]
    a1 = cam.xy((104, 32, VB_H))
    a2 = cam.xy((VB_BORES[2], 0, VB_H * .48))
    a3 = cam.xy((14, 120, VB_H))
    s += bal(a1[0], a1[1], 150, 44, 1) + bal(a2[0], a2[1], 150, 286, 2) + bal(a3[0], a3[1], 30, 56, 3)
    s += bal(*pl(108, 110), 440, 190, 4)
    return s, notes


def vb_ops0():
    """die casting: block (hot) between the moving and fixed die halves, shot sleeve + plunger."""
    def fn(sc):
        VB_FN(sc)
        BOX(sc, -26, -20, -46, VB_W + 52, VB_D + 40, 46, "m", dark=1)              # fixed die
        BOX(sc, -26, -20, VB_H + 70, VB_W + 52, VB_D + 40, 30, "m", ch=4)          # moving die (open)
        CYL(sc, (-120, VB_D / 2, -20), (1, 0, 0), 14, 94, "m", seg=24)             # shot sleeve
        CYL(sc, (-150, VB_D / 2, -20), (1, 0, 0), 8, 30, "dk", seg=20)             # plunger rod
    s, cam = fit3(fn, VB_AZ, VB_EL, (60, 36, 420, 270))
    s = hot(s)
    s += arrow3(cam, (VB_W / 2, VB_D / 2, VB_H + 170), (VB_W / 2, VB_D / 2, VB_H + 112))
    s += arrow3(cam, (-190, VB_D / 2, -20), (-152, VB_D / 2, -20))
    s += lab(cam, (VB_W + 26, -20, VB_H + 86), "可動型", 16, 0, "start") + lab(cam, (VB_W + 26, -20, -30), "固定型", 16, 4, "start")
    s += lab(cam, (-150, VB_D / 2, -20), "射出", 0, 20)
    return fin(title("薄肉で複雑な油路を持つブロックをダイカスト") + s + text(240, 290, "型締力800〜1,250t", "middle"))


def vb_ops1():
    def fn(sc):
        VB_FN(sc)
        spindle(sc, (150, 60, VB_H + 2), (0, 0, 1), 56, 14, "t", rh=26, hl=24)
        return "", vb_top(sc.cam)
    s, cam = fit3(fn, VB_AZ, VB_EL, (60, 36, 420, 268))
    s += arc3(cam, (150, 60, VB_H + 34), (0, 0, 1), 70, 120, 230)
    s += arrow3(cam, (-20, -30, VB_H + 10), (60, -30, VB_H + 10))
    s += lab(cam, (150, 60, VB_H + 70), "正面フライス", 50, 0, "start")
    return fin(title("セパレートプレートとの合わせ面を平らに仕上げ") + s + tol(40, 280, "平面度0.02〜0.05mm"))


def vb_ops2():
    x = VB_BORES[2]

    def fn(sc):
        VB_FN(sc)
        spindle(sc, (x, -2, VB_H * .48), (0, -1, 0), 6.8, 70, "t", rh=12)
        return "", ring3(sc.cam, (x, -.3, VB_H * .48), (0, -1, 0), 9.5, "mf", 28)
    s, cam = fit3(fn, VB_AZ, VB_EL, (40, 36, 440, 268))
    s += arc3(cam, (x, -60, VB_H * .48), (0, -1, 0), 20, 30, 300)
    s += lab(cam, (x, -96, VB_H * .48), "リーマ（手前から）", 30, 24, "start")
    s += arrow3(cam, (x + 34, -80, VB_H * .48), (x + 34, -30, VB_H * .48))
    return fin(title("ドリル→リーマ→ボーリングでスプール穴を精密に仕上げ") + s + tol(40, 280, "穴径公差 数μm・真円度・同軸度"))


def vb_ops3():
    p = (110, 70, VB_H)

    def fn(sc):
        VB_FN(sc)
        CYL(sc, add3(p, (0, 0, 1), 34), (0, 0, 1), 3.5, 40, "t", seg=16)
        CYL(sc, add3(p, (0, 0, 1), 74), (0, 0, 1), 9, 40, "m", seg=20)
        cam = sc.cam
        a, b = cam.xy(add3(p, (0, 0, 1), 34)), cam.xy(add3(p, (0, 0, 1), 2))
        return "", path("M%s %s L%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1])), "jet") + ring3(cam, add3(p, (0, 0, 1), .3), (0, 0, 1), 9, "mfring")
    s, cam = fit3(fn, VB_AZ, VB_EL, (30, 36, 300, 268))
    s += lab(cam, add3(p, (0, 0, 1), 100), "高圧水", 14, 0, "start")
    pl = Pl(312, 120, 0.46)
    x, y = pl(108, 110)
    s += inset(300, 50, 170, 104, "断面（交差穴）", pl.g(D.vb_sec()) + circ(x, y, 6, "mfring"))
    return fin(title("交差穴のバリを高圧水で除去") + s + tol(40, 280, "バリはスプールの固着の原因"))


def vb_ops4():
    def fn(sc):
        VB_FN(sc)
        BOX(sc, -60, -30, -16, VB_W + 120, VB_D + 60, 16, "m")                    # conveyor bed
        for xx in (-30, 50, 130, 210, 290):
            CYL(sc, (xx, -32, -8), (0, 1, 0), 7, VB_D + 64, "dk", seg=16, bias=-1)
        for xx in (40, 110, 180):
            CYL(sc, (xx, VB_D / 2, VB_H + 70), (0, 0, 1), 6, 50, "m", seg=16)
    s, cam = fit3(fn, VB_AZ, VB_EL, (40, 36, 440, 268))
    for xx in (40, 110, 180):
        x, y = cam.xy((xx, VB_D / 2, VB_H + 70))
        s += drops(x, y + 2, 4, 40, 34, 90)
    s += arrow3(cam, (-60, -50, -8), (40, -50, -8))
    return fin(title("洗浄し、残留異物を管理") + s)


def vb_ops5():
    x = VB_BORES[2]

    def fn(sc):
        VB_FN(sc)
        CYL(sc, (x, -76, VB_H * .48), (0, 1, 0), 6.6, 62, "t", seg=20)            # spool (being inserted)
        for yy in (-70, -50, -30):
            CYL(sc, (x, yy, VB_H * .48), (0, 1, 0), 7.2, 6, "t", seg=20, dark=.4)  # lands
        BOX(sc, VB_BORES[4] - 22, -46, 2, 44, 40, 30, "dk", ch=4)                  # solenoid
        CYL(sc, (VB_BORES[4], -6, VB_H * .48), (0, 1, 0), 8, 6, "m", seg=20)
        return "", ring3(sc.cam, (x, -.3, VB_H * .48), (0, -1, 0), 9.5, "mfo", 28)
    s, cam = fit3(fn, VB_AZ, VB_EL, (40, 36, 440, 268))
    s += arrow3(cam, (x - 30, -110, VB_H * .48), (x - 30, -60, VB_H * .48))
    s += lab(cam, (x, -96, VB_H * .48), "スプール", -14, -14, "end") + lab(cam, (VB_BORES[4], -46, 2), "ソレノイド", 0, 20)
    return fin(title("径ランクに合わせたスプールとソレノイドを組み付け") + s + tol(40, 280, "すき間 数μm（選択組付け）"))


def vb_ops6():
    def fn(sc):
        VB_FN(sc)
        BOX(sc, -20, -20, -24, VB_W + 40, VB_D + 40, 24, "pt", dark=1)            # test plate
        for xx in (30, 110, 190):
            CYL(sc, (xx, -40, -14), (0, 1, 0), 5, 30, "dk", seg=16)                # pressure ports
    s, cam = fit3(fn, VB_AZ, VB_EL, (24, 44, 318, 262))
    s += chart(330, 40, 140, 90, "step") + text(400, 146, "油圧特性", "middle", "sm")
    s += line(340, 180, 400, 180, "jet2") + lab(cam, (110, -40, -14), "油圧", 0, 22)
    return fin(title("実際に油を流して各弁の油圧特性と漏れを確認") + s + tol(40, 280, "スティック（固着）がないこと"))


@dpart("drivetrain.valvebody", "ops")
def valvebody_ops3():
    return [vb_ops0(), vb_ops1(), vb_ops2(), vb_ops3(), vb_ops4(), vb_ops5(), vb_ops6()]


# =====================================================================================
# drivetrain.cvtpulley — fixed sheave integral with its shaft (axis x). The conical sheave face looks
# toward -x (lit with az > 0); the ball-spline portion (r 21, 3 grooves) on which the movable sheave
# slides runs toward -x; splined end at +x.
# =====================================================================================
CV_R = 82
CV_SEG = [("c", 16, 12), ("c", 22, 17), ("c", 70, 21), ("k", 16, (22, CV_R)), ("c", 5, CV_R), ("c", 20, 17), ("s", 28, 13)]
CV_XK = 108                       # cone from x=108 (r 22) to x=124 (r R)
CV_GR = (100, 220, 340)           # ball-spline groove angles (0 = +y, 90 = up)


def pt3(C, A, r, ang):
    E1, E2, _ = GE.frame(A)
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    return tuple(C[i] + r * (c * E1[i] + s_ * E2[i]) for i in range(3))


def cv_shaft(sc, O=(0, 0, 0), mat="w", grooves=True, lo=False):
    big, bb = (36, 10) if lo else (56, 14)
    x = 0.0
    A = (1, 0, 0)
    for kind, L, r in CV_SEG:
        p = add3(O, A, x)
        if kind == "s" and lo:
            CYL(sc, p, A, r, L, mat, seg=16)
        elif kind == "s":
            sc.add(compact(GE.prism(sc.cam, p, A, GE.spline_outline(16, r, r - 2), L, mat)), ((p[0], p[1] - r, p[2] - r), (p[0] + L, p[1] + r, p[2] + r)))
        elif kind == "k":
            CYL(sc, p, A, r[0], L, mat, seg=big, bands=bb, r1=r[1])
        else:
            CYL(sc, p, A, r, L, mat, seg=big if r > 40 else (16 if lo else 24), bands=bb if r > 40 else 8, dark=.4 if r == CV_R else 0)
        x += L
    if grooves:
        def gv(s_):
            cam = s_.cam
            o = ""
            for g in CV_GR:
                q = [pt3(add3(O, A, x), A, 21.15, g + d) for x, d in ((42, -5), (104, -5), (104, 5), (42, 5))]
                o += poly3(cam, q, "w3")
            return o
        RAW(sc, gv, (add3(O, (40, -21.2, -21.2)), add3(O, (106, 21.2, 21.2))), -2)


def cv_face(cam, O=(0, 0, 0), cls="mfo"):
    """machined sheave face: rim circle + inner circle."""
    return ring3(cam, add3(O, (CV_XK + 16.1, 0, 0)), (-1, 0, 0), CV_R, cls, 56) + ring3(cam, add3(O, (CV_XK - .1, 0, 0)), (-1, 0, 0), 23, cls, 28)


CV_AZ, CV_EL = 36, 20


@dpart("drivetrain.cvtpulley", "detail")
def pulley_detail3():
    s, cam = fit3(lambda sc: cv_shaft(sc), CV_AZ, CV_EL, (40, 36, 440, 270))
    notes = [("シーブ面", "ベルトを挟む円すい面。角度・粗さが伝達効率を決める"), ("軸部", "軸受部の径・振れ"),
             ("ボールスプライン溝", "可動シーブが軸方向に滑る溝")]
    a1 = cam.xy(pt3((116, 0, 0), (1, 0, 0), 56, 130))
    a2 = cam.xy(pt3((26, 0, 0), (1, 0, 0), 17, 170))
    a3 = cam.xy(pt3((74, 0, 0), (1, 0, 0), 21, 220))
    s += bal(a1[0], a1[1], 300, 44, 1) + bal(a2[0], a2[1], 60, 270, 2) + bal(a3[0], a3[1], 200, 280, 3)
    return s, notes


def cv_ops0():
    def fn(sc):
        cv_shaft(sc, grooves=False)
        BOX(sc, -20, -100, -150, 220, 200, 50, "m", dark=1)
        BOX(sc, -20, -100, 130, 220, 200, 44, "m", ch=4)
    s, cam = fit3(fn, CV_AZ, CV_EL, (90, 36, 400, 272))
    s = hot(s) + arrow3(cam, (90, -100, 230), (90, -100, 180))
    return fin(title("軸と一体のシーブを熱間鍛造") + s)


def cv_ops1():
    def fn(sc):
        cv_shaft(sc)
        CYL(sc, (156, 0, 0), (1, 0, 0), 52, 34, "m", seg=40, dark=.3)                 # chuck
        for k in range(3):
            p = pt3((146, 0, 0), (1, 0, 0), 26, 90 + 120 * k)
            CYL(sc, p, (1, 0, 0), 9, 10, "dk", seg=12, bias=-.5)
        X(sc, 106, 14, [(-138, -7), (-62, -7), (-62, 7), (-138, 7)], "dk")           # tool shank (from the front)
        X(sc, 110, 6, [(-62, -5), (-48, -2), (-48, 2), (-62, 5)], "t", bias=-1)     # insert
        return "", cv_face(sc.cam)
    s, cam = fit3(fn, CV_AZ, CV_EL)
    s += arc3(cam, (60, 0, 0), (1, 0, 0), 44, 120, 210)
    s += lab(cam, (113, -138, 0), "バイト", -8, 4, "end")
    return fin(title("シーブ面・軸部を旋削") + s)


def cv_ops2():
    g = pt3((70, 0, 0), (1, 0, 0), 21, CV_GR[0])

    def fn(sc):
        cv_shaft(sc)
        spindle(sc, add3(g, (0, 0, 1), .5), (0, 0, 1), 5, 40, "t", rh=12)
        a, b = pt3((44, 0, 0), (1, 0, 0), 21.2, CV_GR[0]), pt3((102, 0, 0), (1, 0, 0), 21.2, CV_GR[0])
        return "", poly3(sc.cam, [a, b], "mf", False)
    s, cam = fit3(fn, CV_AZ, CV_EL)
    s += arrow3(cam, (50, -30, 90), (100, -30, 90)) + lab(cam, (75, -30, 90), "送り", 0, -8)
    return fin(title("可動シーブが滑るボールスプライン溝を加工") + s)


def cv_ops3():
    def fn(sc):
        BOX(sc, -40, -60, -150, 280, 300, 34, "m", dark=.6)                          # hearth / tray
        BOX(sc, -40, 240, -150, 280, 20, 240, "pt", dark=1)                          # back wall
        for y in (0, 160):
            cv_shaft(sc, (0, y, -34), grooves=False, lo=True)
    s, cam = fit3(fn, CV_AZ, CV_EL, (60, 36, 420, 272))
    s = hot(s)
    x, y = cam.xy((100, 240, 60))
    s += heat(x - 20, y, 4, 12, 16)
    return fin(title("浸炭焼入れで表面を硬化") + s)


CV_G = GE._norm((16, 0, 60))              # cone generator (top)
CV_N = GE._norm((-60, 0, 16))             # sheave-face normal (top)


def cv_ops4():
    Rw = 54
    c = add3((116, 0, 52), CV_N, Rw)

    def fn(sc):
        cv_shaft(sc, lo=True)
        CYL(sc, add3(c, CV_G, -18), CV_G, Rw, 36, "gw", seg=36, bands=10)
        CYL(sc, add3(c, CV_G, 18), CV_G, 18, 40, "m", seg=24)
        for x, a in ((-30, 1), (207, -1)):
            CYL(sc, (x, 0, 0), (a, 0, 0), 10, 20, "m", seg=20, r1=2)            # centres
            CYL(sc, (x - 40 if a > 0 else x, 0, 0), (1, 0, 0), 18, 40, "m", seg=24, bias=.5)
        return "", cv_face(sc.cam)
    s, cam = fit3(fn, CV_AZ, CV_EL)
    s += arc3(cam, add3(c, CV_G, -24), CV_G, Rw + 8, 200, 290) + lab(cam, add3(c, CV_N, Rw), "アンギュラ砥石", 0, -10)
    s += arc3(cam, (40, 0, 0), (1, 0, 0), 34, 120, 210)
    return fin(title("シーブ面をアンギュラ研削し、軸部を仕上げ") + s + tol(24, 290, "シーブ角度・振れ・研削焼け"))


def cv_ops5():
    p0, p1 = add3((108, 0, 22), CV_G, 24), add3((108, 0, 22), CV_G, 46)
    q0, q1 = add3(p0, CV_N, 14), add3(p1, CV_N, 14)

    def fn(sc):
        cv_shaft(sc)
        xz = [(p[0], p[2]) for p in (p0, p1, q1, q0)]
        sc.ypr(10, 20, xz, "gw", bias=-1)
        r0, r1 = add3(q0, CV_G, 4), add3(q1, CV_G, -4)
        sc.ypr(8, 16, [(p[0], p[2]) for p in (r0, r1, add3(r1, CV_N, 40), add3(r0, CV_N, 40))], "dk", bias=-1)
        return "", cv_face(sc.cam)
    s, cam = fit3(fn, CV_AZ, CV_EL)
    a, b = add3(add3(q0, CV_N, 50), (0, -14, 0)), add3(add3(q1, CV_N, 50), (0, -14, 0))
    s += arrow3(cam, a, b, both=True) + lab(cam, add3(q1, CV_N, 56), "揺動", 10, 0, "start")
    s += lab(cam, add3(q0, CV_N, 10), "砥石", -16, 16, "end")
    s += arc3(cam, (40, 0, 0), (1, 0, 0), 34, 120, 210)
    return fin(title("ベルト接触面を超仕上げして表面粗さを制御") + s + tol(24, 290, "粗さ＝摩擦係数に直結"))


def cv_ops6():
    def fn(sc):
        cv_shaft(sc)
        A = (1, 0, 0)
        CYL(sc, (40, 0, 0), A, 66, 26, "w", seg=56, bands=14, dark=.4, holes=[GE.circle_outline(21, 24, 8)])
        CYL(sc, (66, 0, 0), A, CV_R, 6, "w", seg=56, bands=14, dark=.4)
        CYL(sc, (72, 0, 0), A, CV_R, 16, "w", seg=56, bands=14, r1=26)
    s, cam = fit3(fn, CV_AZ, CV_EL)
    s += arrow3(cam, (30, -10, CV_R + 26), (80, -10, CV_R + 26), both=True) + lab(cam, (55, -10, CV_R + 26), "可動シーブ", 0, -10)
    return fin(title("固定シーブと可動シーブを組み、作動を確認") + s)


@dpart("drivetrain.cvtpulley", "ops")
def pulley_ops3():
    return [cv_ops0(), cv_ops1(), cv_ops2(), cv_ops3(), cv_ops4(), cv_ops5(), cv_ops6()]


# =====================================================================================
# drivetrain.diffcase — ductile-iron differential case (axis x): bearing journals 0..26 / 138..164,
# ring-gear flange x 32..44 (r 94), spherical body with a side window (front), pinion-shaft boss on top
# =====================================================================================
DF_BODY = [(44, 64), (52, 69), (66, 72), (84, 72), (100, 68), (114, 58), (124, 46), (130, 32)]
DF_AZ, DF_EL = 30, 22
DF_LO = [(44, 64), (58, 71), (92, 71), (116, 57), (130, 32)]


def DF_FN(sc):
    """lighter copy of il3_drive.diff_case's model (fewer facets: the op sheets add tools around it)."""
    A = (1, 0, 0)
    body = DF_BODY
    CYL(sc, (0, 0, 0), A, 22, 26, "w", seg=24, bands=8)
    CYL(sc, (26, 0, 0), A, 27, 6, "w", seg=24, bands=8, dark=.5)
    CYL(sc, (32, 0, 0), A, 94, 12, "w", seg=40, bands=10, dark=.4)
    for (x0, r0), (x1, r1) in zip(DF_LO, DF_LO[1:]):
        CYL(sc, (x0, 0, 0), A, r0, x1 - x0, "w", seg=28, bands=8, r1=r1, dark=.5, caps=x0 == 44)
    CYL(sc, (130, 0, 0), A, 24, 8, "w", seg=24, bands=8, dark=.5)
    CYL(sc, (138, 0, 0), A, 22, 26, "w", seg=24, bands=8)
    CYL(sc, (164, 0, 0), A, 17, 8, "w", seg=20, bands=8)
    CYL(sc, (86, 0, 66), (0, 0, 1), 15, 10, "w", seg=20, bands=8, dark=.3, bias=-1)

    def marks(s_):
        cam = s_.cam
        o = hole3(cam, (-.1, 0, 0), (-1, 0, 0), 15, "w3", 20) + hole3(cam, (-.1, 0, 0), (-1, 0, 0), 11, "bg", 18)
        for k in range(12):
            t = 2 * PI * (k + .5) / 12
            o += hole3(cam, (31.9, 80 * math.cos(t), 80 * math.sin(t)), (-1, 0, 0), 4.2, "bg", 8)
        return o

    def window(s_):
        cam = s_.cam
        win, inn = [], []
        for k in range(28):
            t = 2 * PI * k / 28
            u, v = math.cos(t), math.sin(t)
            u, v = math.copysign(abs(u) ** .6, u), math.copysign(abs(v) ** .6, v)
            x = 90 + 16 * u
            th = math.radians(162 + 30 * v)
            r = PD._interp(body, x) + .3
            win.append(cam.xy((x, r * math.cos(th), r * math.sin(th))))
            th2 = math.radians(162 + 26 * v)
            inn.append(cam.xy((90 + 14 * u + 4, (r - 14) * math.cos(th2) + 6, (r - 14) * math.sin(th2))))
        return path(P(win), "bg") + path(P(PD.clip_poly(inn, win)), "w3")
    RAW(sc, lambda s_: hole3(s_.cam, (86, 0, 76.1), (0, 0, 1), 8.5, "bg", 16), ((76, -10, 76), (96, 10, 76.2)), -2)
    RAW(sc, marks, ((-.2, -95, -95), (32, 95, 95)), -2)
    RAW(sc, window, ((72, -73, 10), (108, -60, 40)), -2)


def box_s(cam, x, y, z, sx, sy, sz, mat="pt", **kw):
    xy = [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)]
    loop = [(-p[1], p[0], i) for i, p in enumerate(xy)]
    return compact(GE.prism(cam, (0, 0, z), (0, 0, 1), loop, sz, mat, **kw))


def df_sec(x0, y0, k=1.0):
    """2D half-section of the case (axis horizontal): cut wall, spherical inside, bores."""
    prof = [(0, 22), (26, 22), (26, 27), (32, 27), (32, 94), (44, 94), (44, 64), (66, 72), (84, 72), (100, 68), (114, 58),
            (124, 46), (130, 32), (130, 24), (138, 24), (138, 22), (164, 22)]
    up = [(x0 + x * k, y0 - r * k) for x, r in prof]
    lo = [(x0 + x * k, y0 + r * k) for x, r in reversed(prof)]
    s = path(P(up + lo), "cut")
    s += circ(x0 + 86 * k, y0, 52 * k, "void") + rect(x0, y0 - 13 * k, 164 * k, 26 * k, "void")
    s += rect(x0 + 78 * k, y0 - 74 * k, 16 * k, 30 * k, "void") + cl(x0 - 8, y0, x0 + 172 * k, y0)
    return s


@dpart("drivetrain.diffcase", "detail")
def diffcase_detail3():
    s, cam = fit3(DF_FN, DF_AZ, DF_EL, (10, 52, 300, 272))
    pl0 = (318, 140)
    s += inset(306, 44, 168, 196, "断面", df_sec(pl0[0], pl0[1], .8))
    notes = [("球状の内面", "サイドギヤ・ピニオンの背面が当たる球面"), ("窓", "内部加工とギヤ組付けのための開口"),
             ("フランジ", "リングギヤの取付面。振れ・ボルト穴"), ("軸受部", "デフ軸受の圧入部")]
    a1 = (pl0[0] + 86 * .8 + 52 * .8 * math.cos(math.radians(-50)), pl0[1] + 52 * .8 * math.sin(math.radians(-50)))
    a2 = cam.xy((90, -68, 22))
    a3 = cam.xy((38, -60, 72))
    a4 = cam.xy((150, -20, 10))
    s += bal(a1[0], a1[1], 440, 70, 1) + bal(a2[0], a2[1], 200, 286, 2) + bal(a3[0], a3[1], 150, 40, 3) + bal(a4[0], a4[1], 290, 286, 4)
    return s, notes


def df_ops0():
    def fn(sc):
        CYL(sc, (0, 0, 0), (0, 0, 1), 60, 150, "pt", seg=36, dark=1)                 # induction furnace
        CYL(sc, (0, 0, 150), (0, 0, 1), 46, 1, "h", seg=36, bias=-1)
        CYL(sc, (230, 0, 0), (0, 0, 1), 46, 96, "m", seg=36, dark=.5, r1=54)           # treatment ladle
        CYL(sc, (230, 0, 96), (0, 0, 1), 46, 1, "h", seg=36, bias=-1)
        return "", stream(sc.cam, (52, 0, 160), (200, 0, 110), 4)
    s, cam = fit3(fn, 30, 24, (60, 60, 330, 262))
    x, y = cam.xy((230, 0, 97))
    s += sparks(x, y - 4, 22, 9, -170, -10)
    a, b = cam.xy((0, 0, 0)), cam.xy((230, 0, 0))
    s += text(a[0], 280, "誘導炉", "middle") + text(b[0], 280, "球状化処理（Mg）・接種", "middle")
    s += tol(340, 120, "成分・球状化率") + tol(340, 136, "熱分析で確認")
    return fin(title("鋳鉄を溶解し、マグネシウム処理で黒鉛を球状化") + s)


def df_ops1():
    x0, x1, y0, y1 = -30, 200, -110, 110

    def fn(sc):
        cam = sc.cam
        pre = sandify(box_s(cam, x0, y0, -120, x1 - x0, y1 - y0, 120, "sand"))
        DF_FN(sc)
        CYL(sc, (86, 0, 150), (0, 0, 1), 12, 90, "h", seg=20)                          # sprue in the cope
        BOX(sc, x0, y0, 150, x1 - x0, y1 - y0, 90, "sand", bias=1)                     # cope (lifted)
        front = poly3(cam, [(x0, y0, -120), (x1, y0, -120), (x1, y0, 0), (x0, y0, 0)], "sand") + \
            poly3(cam, [(x0, y0, -120), (x1, y0, -120), (x1, y0, 0), (x0, y0, 0)], "grain")
        return pre, front
    s, cam = fit3(fn, DF_AZ, DF_EL, (70, 34, 410, 270), sh=False)
    s = sandify(hot(s))
    s += arrow3(cam, (x1 + 20, y0, 220), (x1 + 20, y0, 160)) + lab(cam, (x1 + 20, y0, 190), "上型", 8, 0, "start")
    s += lab(cam, (x1, y0, -60), "下型", 8, 0, "start")
    return fin(title("生型に中子を組み、注湯して鋳造") + s + text(240, 290, "上型・下型の生砂鋳型＋シェル中子", "middle"))


def df_ops2():
    def fn(sc):
        DF_FN(sc)
        CYL(sc, (60, -170, 150), GE._norm((0, 1, -.8)), 12, 50, "m", seg=20)           # shot nozzle
    s, cam = fit3(fn, DF_AZ, DF_EL, (60, 40, 420, 250))
    a, b = cam.xy(add3((60, -170, 150), GE._norm((0, 1, -.8)), -6)), cam.xy((70, -60, 60))
    for k in range(18):
        t = (k * .37) % 1
        s += circ(a[0] + (b[0] - a[0]) * t + ((k * 7) % 11 - 5), a[1] + (b[1] - a[1]) * t + ((k * 5) % 9 - 4), 1.6, "shot")
    s += dots(60, 262, 360, 24, 16, "grain") + text(a[0], a[1] - 30, "ショット", "middle")
    return fin(title("砂を落とし、ショットとグラインダで仕上げる") + s)


def df_ops3():
    def fn(sc):
        DF_FN(sc)
        CYL(sc, (38, -60, 72), (-1, 0, 0), 10, 6, "fl", seg=16)
        CYL(sc, (32, -60, 72), (-1, 0, 0), 9, 40, "dk", seg=16)
    s, cam = fit3(fn, DF_AZ, DF_EL, (20, 40, 330, 272))
    s += lab(cam, (-8, -60, 72), "超音波探触子", -34, -6, "end")
    s += rect(360, 150, 110, 110, "m", 4) + circ(415, 205, 44, "m")
    for k in range(9):
        s += circ(385 + (k % 3) * 30, 180 + (k // 3) * 24, 5, "d")
    s += text(415, 276, "球状黒鉛（顕微鏡）", "middle", "sm")
    return fin(title("超音波の音速で球状化率を判定し、硬さを確認") + s)


def df_ops4():
    def fn(sc):
        CYL(sc, (176, 0, 0), (1, 0, 0), 56, 30, "m", seg=36, dark=.3)                  # chuck (holds the right journal)
        for k in range(3):
            CYL(sc, pt3((164, 0, 0), (1, 0, 0), 30, 90 + 120 * k), (1, 0, 0), 8, 12, "dk", seg=12)
        DF_FN(sc)
        X(sc, 8, 12, [(-130, -6), (-28, -6), (-28, 6), (-130, 6)], "dk")             # tool shank (from the front)
        X(sc, 10, 8, [(-28, -4), (-22.5, -1.5), (-22.5, 1.5), (-28, 4)], "t", bias=-1)
        cam = sc.cam
        mf_ = poly3(cam, [(0, -22 * .2, 22 * .98), (26, -22 * .2, 22 * .98)], "mf", False)
        return "", ring3(cam, (31.8, 0, 0), (-1, 0, 0), 92, "mfo", 56) + mf_
    s, cam = fit3(fn, DF_AZ, DF_EL, (40, 40, 440, 270))
    s += arc3(cam, (60, 0, 0), (1, 0, 0), 106, 110, 170)
    s += arrow3(cam, (-50, -60, 0), (0, -60, 0)) + lab(cam, (-25, -60, 0), "送り", 0, -8)
    return fin(title("外形・フランジ・軸受部を旋削") + s)


def df_ops5():
    W = (90, -70, 22)
    U = GE._norm((0, -1, -.25))

    def fn(sc):
        DF_FN(sc)
        CYL(sc, add3(W, U, -26), U, 7, 110, "t", seg=16, bias=-2)                     # boring bar through the window
        spindle(sc, (86, 0, 78), (0, 0, 1), 4, 40, "t", rh=10)                        # drill on the pinion-shaft boss
        return "", ring3(sc.cam, (86, 0, 76.2), (0, 0, 1), 9, "mf", 20)
    s, cam = fit3(fn, DF_AZ, DF_EL, (20, 40, 320, 270))
    s += arc3(cam, add3(W, U, 40), U, 14, 30, 300) + lab(cam, add3(W, U, 84), "ボーリングバー", 0, 20)
    s += lab(cam, (86, 0, 160), "穴あけ", 18, 4, "start")
    s += inset(330, 44, 144, 150, "断面", df_sec(342, 132, .7))
    s += path("M%s %s A%s %s 0 0 1 %s %s" % (n(342 + 86 * .7 - 36.4 * .866), n(132 - 36.4 * .5), n(36.4), n(36.4),
                                              n(342 + 86 * .7 + 36.4 * .866), n(132 - 36.4 * .5)), "mf")
    return fin(title("窓から工具を入れて内球面を加工し、ピニオン軸穴をあける") + s + tol(300, 280, "内球面の形状・穴位置"))


@dpart("drivetrain.diffcase", "ops")
def diffcase_ops3():
    return [df_ops0(), df_ops1(), df_ops2(), df_ops3(), df_ops4(), df_ops5()]


# =====================================================================================
# drivetrain.cvj — drive shaft (axis x), after il3_drive.cvj with fewer facets. Outer race: mouth at
# x=262 looking toward -x, bell to x=314, splined stub to x=372.
# =====================================================================================
CJ_AZ, CJ_EL = 24, 20
CJ_M = 261.9
cy = PD.cy


def cj_outer(cam, mat="w", inner=False, stub_mat=None, grooves=True):
    sm = stub_mat or mat
    o = cy(cam, 356, 10, 16, sm, seg=16, bands=6)
    o += compact(GE.prism(cam, (330, 0, 0), (1, 0, 0), GE.spline_outline(12, 15, 13), 26, sm))
    o += cy(cam, 314, 19, 16, sm, seg=20, bands=6)
    for x0, r0, x1, r1 in ((302, 44, 314, 26), (278, 49, 302, 44), (262, 46, 278, 49)):
        o += cy(cam, x0, r0, x1 - x0, mat, r1=r1, seg=28, bands=8, dark=.3, caps=x0 == 262)
    m = CJ_M
    o += hole3(cam, (m, 0, 0), (-1, 0, 0), 37, "bg", 28)
    o += path(P(circ3(cam, (m, 0, 0), (-1, 0, 0), 46, 32)), "gr")
    if inner:
        o += hole3(cam, (m + 6, 0, 0), (-1, 0, 0), 34, "w3", 24) + hole3(cam, (m + 6, 0, 0), (-1, 0, 0), 30, "bg", 24)
        o += hole3(cam, (m + 2, 0, 0), (-1, 0, 0), 22, "w2", 20)
        balls = []
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            c = (m + 3, 30 * math.cos(t), 30 * math.sin(t))
            bx, by = cam.xy(c)
            r = 8.2 * cam.s
            balls.append((cam.P(c)[2], '<circle class="ball" cx="%s" cy="%s" r="%s"/>' % (n(bx), n(by), n(r))))
        o += "".join(b for _, b in sorted(balls, key=lambda b: -b[0]))
    elif grooves:
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            o += hole3(cam, (m, 33 * math.cos(t), 33 * math.sin(t)), (-1, 0, 0), 8, "bg", 14)
    return o


def cj_full(cam):
    o = cj_outer(cam, inner=True)
    o += cy(cam, 140, 11, 128, seg=14, bands=5)
    bel = [(92, 33), (101, 36), (110, 27), (119, 30), (128, 21), (136, 23), (146, 13)]
    for (x0, r0), (x1, r1) in reversed(list(zip(bel, bel[1:]))):
        o += cy(cam, x0, r0, x1 - x0, "dk", r1=r1, seg=16, bands=5, caps=False)
    o += cy(cam, 88, 37, 4, "dk", seg=24, bands=6, dark=-.4)
    o += cy(cam, 46, 38, 42, seg=24, bands=8, dark=.2)
    o += cy(cam, 38, 18, 8, r1=38, seg=24, bands=6)
    o += cy(cam, 26, 17, 12, seg=20, bands=6)
    o += compact(GE.prism(cam, (0, 0, 0), (1, 0, 0), GE.spline_outline(12, 14, 12), 26, "w"))
    o += hole3(cam, (-.1, 0, 0), (-1, 0, 0), 3.4, "bg", 12)
    return o


def cj_sheet(fn, ttl, area=(30, 40, 450, 270), az=CJ_AZ, el=CJ_EL, **kw):
    return fit3(fn, az, el, area, **kw)


@dpart("drivetrain.cvj", "detail")
def cvj_detail3():
    s, cam = fit3(lambda sc: cj_full(sc.cam), CJ_AZ, CJ_EL, (14, 40, 466, 180))
    notes = [("外輪（アウターレース）", "ボール溝を持つカップ。冷間しごき＋焼入れ＋研削"), ("ブーツ", "グリースを封入し泥水を防ぐ樹脂ベローズ"),
             ("シャフト", "両端スプライン。高周波焼入れ"), ("内側ジョイント", "伸縮を吸収するトリポード型など"), ("ボール・ケージ・内輪", "角度がついても等速で回転を伝える")]
    a1 = cam.xy(pt3((290, 0, 0), (1, 0, 0), 48, 100))
    a2 = cam.xy(pt3((110, 0, 0), (1, 0, 0), 27, 120))
    a3 = cam.xy(pt3((200, 0, 0), (1, 0, 0), 11, 150))
    a4 = cam.xy(pt3((66, 0, 0), (1, 0, 0), 38, 110))
    a5 = cam.xy((CJ_M + 3, 30 * math.cos(PI * 7 / 6), 30 * math.sin(PI * 7 / 6)))
    s += bal(a1[0], a1[1], 420, 40, 1) + bal(a2[0], a2[1], 150, 40, 2) + bal(a3[0], a3[1], 200, 250, 3)
    s += bal(a4[0], a4[1], 50, 40, 4) + bal(a5[0], a5[1], 290, 250, 5)
    pl = Pl(344, 236, 0.95)
    s += inset(330, 190, 140, 104, "外輪断面", pl.g(D.outer_race()))
    return s, notes


def cj_ops0():
    def fn(sc):
        cam = sc.cam
        o = box_s(cam, 230, -80, -110, 160, 160, 40, "m", dark=1)
        return o + hot(cj_outer(cam, grooves=False)), box_s(cam, 230, -80, 80, 160, 160, 36, "m")
    s, cam = fit3(fn, CJ_AZ, CJ_EL + 6, (110, 36, 380, 272))
    s += arrow3(cam, (310, -80, 170), (310, -80, 120)) + lab(cam, (310, -80, 150), "成形", 10, 0, "start")
    return fin(title("外輪を熱間鍛造し、冷間しごきでボール溝をほぼ最終形状に") + s)


def cj_ops1():
    def fn(sc):
        cam = sc.cam
        die = [compact(GE.prism(cam, (332, 0, z), (1, 0, 0), GE.spline_outline(24, 24, 22), 22, "t", smooth=False)) for z in (40, -40)]
        o = cj_outer(cam) + poly3(cam, [(314, -19, 0), (330, -19, 0)], "mf", False)
        return die[1], o + die[0]
    s, cam = fit3(fn, CJ_AZ, CJ_EL, (60, 44, 400, 262))
    s += arc3(cam, (343, 0, 40), (1, 0, 0), 30, 120, 200) + arc3(cam, (343, 0, -40), (1, 0, 0), 30, 300, 20)
    s += lab(cam, (332, 0, 66), "転造ダイス", -10, 0, "end")
    return fin(title("軸部を旋削し、スプラインを転造") + s + tol(300, 280, "オーバーピン寸法・振れ"))


def cj_ops2():
    def fn(sc):
        cam = sc.cam
        o = cj_outer(cam, stub_mat="h")
        coil = cy(cam, 200, 24, 66, "cu", seg=20, bands=6)
        lead_ = cy(cam, 160, 8, 40, "cu", seg=12, bands=4)
        o += lead_ + coil + path(P(circ3(cam, (CJ_M + 2, 0, 0), (-1, 0, 0), 36, 32)), "hotband")
        return "", o
    s, cam = fit3(fn, CJ_AZ, CJ_EL, (40, 36, 440, 268))
    s += lab(cam, (200, 0, -24), "内側コイル", 0, 24)
    return fin(title("ボール溝と軸部を高周波焼入れ") + s)


def cj_ops3():
    g = (CJ_M + 10, 33 * math.cos(PI * 7 / 6), 33 * math.sin(PI * 7 / 6))

    def fn(sc):
        cam = sc.cam
        o = cj_outer(cam)
        o += cy(cam, 150, 5, 110, "m", seg=12, bands=4, O=(150, g[1] * .7, g[2] * .7))
        o += cy(cam, 0, 10, 16, "gw", seg=20, bands=6, O=(CJ_M - 6, g[1] * .7, g[2] * .7))
        o += hole3(cam, (CJ_M - .2, g[1], g[2]), (-1, 0, 0), 8, "mf", 14)
        return "", o
    s, cam = fit3(fn, CJ_AZ, CJ_EL, (40, 36, 440, 268))
    s += arc3(cam, (CJ_M - 30, g[1] * .7, g[2] * .7), (1, 0, 0), 18, 30, 300) + lab(cam, (180, g[1] * .7, g[2] * .7), "砥石", 0, 22)
    return fin(title("ボール溝を研削（またはハードミーリング）で仕上げ") + s + tol(300, 280, "溝ピッチ・溝形状（三次元測定）"))


def cj_ops4():
    def fn(sc):
        cam = sc.cam
        A = (0, 0, 1)
        o = compact(GE.prism(cam, (0, 0, 0), A, GE.circle_outline(48, 36, 10), 34, "w", smooth="outer",
                             holes=[GE.spline_outline(18, 20, 17.5)]))
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            nr = (math.cos(t), math.sin(t), 0)
            if GE._dot(nr, cam.D) > -.1:
                continue
            q = [(48.2 * math.cos(t + d), 48.2 * math.sin(t + d), z) for d, z in ((-.13, 0), (.13, 0), (.13, 34), (-.13, 34))]
            o += poly3(cam, q, "w3")
        cx = 190
        o += compact(GE.prism(cam, (cx, 0, 0), A, GE.circle_outline(64, 40, 12), 30, "w", smooth="outer",
                              holes=[GE.circle_outline(56, 40, 12)]))
        for k in range(6):
            t = 2 * PI * k / 6
            nr = (math.cos(t), math.sin(t), 0)
            if GE._dot(nr, cam.D) > -.1:
                continue
            q = [(cx + 64.2 * math.cos(t + d), 64.2 * math.sin(t + d), z) for d, z in ((-.2, 8), (.2, 8), (.2, 22), (-.2, 22))]
            o += poly3(cam, q, "bg")
        return "", o
    s, cam = fit3(fn, -20, 34, (40, 50, 440, 236))
    a, b = cam.xy((0, -48, 0)), cam.xy((190, -64, 0))
    s += text(a[0], 256, "内輪（溝＋スプライン）", "middle") + text(b[0], 256, "ケージ（窓抜き）", "middle")
    return fin(title("内輪は鍛造→旋削→焼入れ→研削、ケージは鋼管→窓抜き→研削") + s)


def cj_ops5():
    def fn(sc):
        cam = sc.cam
        o = cy(cam, 0, 120, 26, "m", seg=48, bands=12, A=(0, 0, 1), O=(0, 0, -26), dark=.4)
        o += path(P(circ3(cam, (0, 0, .2), (0, 0, 1), 80, 40)) + P(circ3(cam, (0, 0, .2), (0, 0, 1), 64, 36)), "gr")
        bl = []
        for k in range(14):
            t = 2 * PI * k / 14
            c = (72 * math.cos(t), 72 * math.sin(t), 7)
            x, y = cam.xy(c)
            bl.append((cam.P(c)[2], '<circle class="ball" cx="%s" cy="%s" r="%s"/>' % (n(x), n(y), n(7.5 * cam.s))))
        o += "".join(b for _, b in sorted(bl, key=lambda b: -b[0]))
        o2 = cy(cam, 0, 120, 22, "m", seg=48, bands=12, A=(0, 0, 1), O=(0, 0, 70), dark=.2)
        return "", o + o2
    s, cam = fit3(fn, -20, 30, (90, 40, 390, 236))
    s += arc3(cam, (0, 0, 104), (0, 0, 1), 130, 200, 300) + arrow3(cam, (140, 0, 150), (140, 0, 100))
    s += text(240, 256, "溝付き定盤で真球に仕上げる", "middle") + tol(40, 290, "真球度・径のばらつき（等級）")
    return fin(title("線材を冷間圧造で球にし、熱処理後に研削・ラッピング") + s)


def cj_ops6():
    def fn(sc):
        cam = sc.cam
        o = cj_full(cam)
        o += cy(cam, 0, 4, 40, "m", seg=8, bands=3, A=GE._norm((-1, 0, 1)), O=(240, 0, 46))
        o += cy(cam, 0, 40, 4, "m", seg=18, bands=4, O=(89, 0, 0), dark=.3)
        return "", o
    s, cam = fit3(fn, CJ_AZ, CJ_EL, (20, 50, 460, 236))
    s += arrow3(cam, (90, 0, 110), (90, 0, 52)) + lab(cam, (90, 0, 100), "バンド締付け", -8, 0, "end")
    s += lab(cam, add3((240, 0, 46), GE._norm((-1, 0, 1)), 46), "グリース封入", 0, -8)
    return fin(title("ボールを組み込み、グリースを定量封入し、ブーツをバンドで締付け") + s)


def cj_ops7():
    def fn(sc):
        return "", cj_full(sc.cam)
    s, cam = fit3(fn, CJ_AZ, CJ_EL, (20, 40, 310, 180))
    s += arc3(cam, (190, 0, 0), (1, 0, 0), 24, 100, 240)
    a, b = cam.xy((330, 0, 60)), cam.xy((330, 0, -60))
    s += path("M%s %s Q%s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] + 14), n((a[1] + b[1]) / 2), n(b[0]), n(b[1])), "a") + head(b[0], b[1], math.atan2(b[1] - a[1], b[0] - a[0] - 14))
    s += lab(cam, (330, 0, 60), "作動角", 0, -8)
    s += chart(320, 190, 150, 80, "ramp")
    return fin(title("作動角をつけて回転させ、トルク・ガタを確認") + s)


@dpart("drivetrain.cvj", "ops")
def cvj_ops3():
    return [cj_ops0(), cj_ops1(), cj_ops2(), cj_ops3(), cj_ops4(), cj_ops5(), cj_ops6(), cj_ops7()]


# =====================================================================================
# chassis.knuckle — cast knuckle (il3_chassis.knuckle): hub boss face toward -y (y=-6) with bore r34,
# strut pad up (bolt holes z 112/146), ball-joint boss down (6, 19, -112), steering arm to +x with
# tie-rod boss (124, 22), caliper ears at x=-74, z=46/-48
# =====================================================================================
KN_FN, KN_AZ, KN_EL = grab(PC, PC.knuckle)


def kn(sc):
    return KN_FN(sc) or ""


@dpart("chassis.knuckle", "detail")
def knuckle_detail3():
    s, cam = fit3(lambda sc: ("", kn(sc)), KN_AZ, KN_EL, (100, 36, 380, 274))
    notes = [("ハブ取付穴", "ハブベアリングが入る穴。径・位置"), ("ストラット取付部", "上側。ボルト穴2か所"),
             ("ロアアーム取付部", "下側。ボールジョイントのテーパ穴"), ("ナックルアーム", "タイロッドが付く。ステアリング操作を伝える"),
             ("キャリパ取付面", "ブレーキキャリパの取付座面とねじ")]
    a1 = cam.xy((24, -6, -10))
    a2 = cam.xy((0, 6, 146))
    a3 = cam.xy((6, 19, -112))
    a4 = cam.xy((124, 22, -2))
    a5 = cam.xy((-74, 4, 46))
    s += bal(a1[0], a1[1], 360, 280, 1) + bal(a2[0], a2[1], 60, 50, 2) + bal(a3[0], a3[1], 60, 270, 3)
    s += bal(a4[0], a4[1], 440, 110, 4) + bal(a5[0], a5[1], 40, 160, 5)
    return s, notes


def kn_ops0():
    def fn(sc):
        cam = sc.cam
        pre = sandify(box_s(cam, -130, 34, -160, 300, 80, 360, "sand", dark=0))
        o = hot(kn(sc))
        o += stream(cam, (0, 20, 240), (0, 20, 168), 6)
        return pre, o
    s, cam = fit3(fn, KN_AZ, KN_EL, (120, 36, 380, 272), sh=False)
    s += lab(cam, (170, 34, 120), "鋳型（生砂）", 8, 0, "start") + lab(cam, (0, 20, 240), "注湯", 12, 6, "start")
    return fin(title("球状化処理した溶湯を生型に注湯") + s + text(240, 290, "FCD450〜600・無枠自動造型ライン", "middle"))


def kn_ops1():
    U = GE._norm((-.4, 1, -.6))
    p0 = (-60, -150, 200)

    def fn(sc):
        return "", kn(sc) + cy(sc.cam, 0, 14, 60, "m", seg=16, bands=5, A=U, O=add3(p0, U, -60))
    s, cam = fit3(fn, KN_AZ, KN_EL, (80, 40, 400, 252))
    a, b = cam.xy(p0), cam.xy((0, -6, 40))
    for k in range(18):
        t = (k * .37) % 1
        s += circ(a[0] + (b[0] - a[0]) * t + ((k * 7) % 11 - 5), a[1] + (b[1] - a[1]) * t + ((k * 5) % 9 - 4), 1.6, "shot")
    s += dots(60, 264, 360, 22, 16, "grain") + text(a[0] + 30, a[1] - 4, "ショット", "start")
    return fin(title("砂を落とし、湯口を切り、ショットで仕上げる") + s)


def kn_ops2():
    src = (-260, -40, 20)

    def fn(sc):
        cam = sc.cam
        pre = box_s(cam, -150, 70, -150, 300, 14, 320, "m", dark=.6)                 # detector panel (behind)
        o = cy(cam, 0, 18, 50, "dk", seg=16, bands=5, A=(1, 0, 0), O=(-310, -40, 20))
        return pre, kn(sc) + o
    s, cam = fit3(fn, KN_AZ, KN_EL, (30, 36, 450, 272))
    a = cam.xy(src)
    for p in ((150, 70, 150), (150, 70, 20), (150, 70, -130), (-150, 70, 160), (-150, 70, -140)):
        b = cam.xy(p)
        s += line(a[0], a[1], b[0], b[1], "ray")
    s += lab(cam, (-290, -40, 40), "X線", 0, -10) + lab(cam, (150, 70, -150), "検出器", 10, 14, "start")
    return fin(title("球状化率（超音波）と内部欠陥（X線）、表面割れ（磁粉）を確認") + s)


def kn_ops3():
    def fn(sc):
        cam = sc.cam
        o = kn(sc)
        bar = cy(cam, 0, 14, 120, "t", seg=16, bands=5, A=(0, -1, 0), O=(0, -20, 0))
        bar += cy(cam, 0, 22, 30, "m", seg=20, bands=5, A=(0, -1, 0), O=(0, -140, 0))
        drill = cy(cam, 0, 4, 60, "t", seg=10, bands=4, A=(0, 0, 1), O=(124, 22, 4))
        drill += cy(cam, 0, 10, 26, "m", seg=16, bands=5, A=(0, 0, 1), O=(124, 22, 64))
        mk = ring3(cam, (0, -6.2, 0), (0, -1, 0), 34, "mfo", 32) + hole3(cam, (124, 22, -1.8), (0, 0, 1), 7, "mfa", 14)
        mk += hole3(cam, (6, 19, -87.8), (0, 0, 1), 9, "mfa", 14)
        for zc in (46, -48):
            mk += hole3(cam, (-74, 3.8, zc), (0, -1, 0), 10, "mfa", 14)
        return "", o + mk + drill + bar
    s, cam = fit3(fn, KN_AZ, KN_EL, (60, 36, 420, 272))
    s += arc3(cam, (0, -90, 0), (0, -1, 0), 26, 30, 300) + lab(cam, (0, -170, -30), "ボーリング（手前から）", 0, 30)
    return fin(title("ハブ穴・アーム取付穴・キャリパ取付面を多面加工") + s + tol(24, 290, "ハブ穴径・テーパ穴・取付面"))


def kn_ops4():
    def fn(sc):
        cam = sc.cam
        o = kn(sc)
        o += cy(cam, 0, 30, 44, "m", seg=24, bands=6, A=(0, -1, 0), O=(0, -10, 0))
        o += cy(cam, 0, 12, 50, "dk", seg=16, bands=5, A=(0, -1, 0), O=(0, -54, 0))
        for z in (-12, 12):
            o += hole3(cam, (0, -54.2, z), (0, -1, 0), 2.6, "fdot", 8)
        return "", o
    s, cam = fit3(fn, KN_AZ, KN_EL, (60, 36, 360, 272))
    s += rect(380, 40, 90, 50, "m", 4) + text(425, 70, "径 ±μm", "middle")
    s += lab(cam, (0, -104, -20), "エアゲージ", 0, 30)
    return fin(title("ハブ穴径と寸法・外観を確認") + s)


@dpart("chassis.knuckle", "ops")
def knuckle_ops3():
    return [kn_ops0(), kn_ops1(), kn_ops2(), kn_ops3(), kn_ops4()]
