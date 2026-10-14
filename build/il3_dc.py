"""v3 (shaded 3D) redraws of the detail sheets and process drawings (480x300) for
engine.valve, engine.turbo, engine.injector, drivetrain.shaft, drivetrain.tmcase.
The solid models follow the v3 part drawings in il3_engine.py / il3_drive.py and are reused
across the detail sheet and every op drawing of the part. Process count, order, titles and
tolerance notes are those of the older flat drawings (il_d_engine / il_d_ev / il_d_drive)."""
import math
import il_gear as GE
from il_base import *
from il_detail import title, bal, tol, fin, lead
from il_dmap import dpart
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3
from il_pictos import chart, lightning
import il_d_engine as E
import il_d_ev as V
import il_d_drive as D

PI = math.pi
AREA = (22, 38, 458, 266)          # op drawings: below the title band, above the tol line


# =====================================================================================
# shared helpers
# =====================================================================================
def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def lb(x, y, t, a="middle"):
    return text(x, y, t, a)


def opfit(fn, az, el, area=AREA, **kw):
    kw.setdefault("sh_ry", 7)
    kw.setdefault("sh_k", .42)
    s, sc = fit(fn, az, el, area, ret_scene=True, **kw)
    return s, sc.cam


def _v(a, b, k=1.0):
    return tuple(a[i] + b[i] * k for i in range(3))


def sil(cam, C0, C1, r, c="mf", r1=None):
    """both silhouette lines of a cylinder / frustum between centres C0 and C1."""
    A = GE._norm(tuple(C1[i] - C0[i] for i in range(3)))
    u = GE._norm(GE._cross(A, cam.D))
    r1 = r if r1 is None else r1
    d = ""
    for sg in (1, -1):
        d += P([cam.xy(_v(C0, u, sg * r)), cam.xy(_v(C1, u, sg * r1))], False)
    return path(d, c)


def rim_pts(cam, C, A, r, front=True, seg=36):
    E1, E2, _ = GE.frame(A)
    pts = []
    for k in range(seg + 1):
        t = 2 * PI * k / seg
        u = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
        if front and GE._dot(u, cam.D) > 0.02:
            continue
        pts.append((t, cam.xy(_v(C, u, r))))
    if front and pts:                       # start the arc at the gap so the polyline is continuous
        ts = [t for t, _ in pts]
        gaps = [(ts[(i + 1) % len(ts)] - ts[i]) % (2 * PI) for i in range(len(ts))]
        g = max(range(len(gaps)), key=lambda i: gaps[i])
        pts = pts[g + 1:] + pts[:g + 1]
    return [p for _, p in pts]


def rim(cam, C, A, r, c="mf", front=True, seg=36):
    return path(P(rim_pts(cam, C, A, r, front, seg), False), c)


def band(cam, C0, r0, C1, r1, A, c="mfa", seg=36):
    """front half of the conical / cylindrical band between two circles (a highlighted surface)."""
    a = rim_pts(cam, C0, A, r0, True, seg)
    b = rim_pts(cam, C1, A, r1, True, seg)
    return path(P(a + b[::-1]), c)


def lbl(cam, p, t, dx=0, dy=0, a="middle", c=""):
    x, y = cam.xy(p)
    return text(x + dx, y + dy, t, a, c)


def balp(cam, p, bx, by, num):
    x, y = cam.xy(p)
    return bal(x, y, bx, by, num)


def chuck3(sc, x, r=26, L=18, jaw=None, A=1, bias=0.0, yz=(0, 0)):
    """3-jaw chuck whose face is at x, body extending away from the work (A=+1: body on +x side)."""
    y0, z0 = yz
    x0 = x if A > 0 else x - L
    CYL(sc, (x0, y0, z0), (1, 0, 0), r, L, "m", bias, seg=32, bands=9)
    CYL(sc, (x0 + (L if A > 0 else -10), y0, z0), (1, 0, 0), r * .7, 10, "dk", bias, seg=24, bands=7)
    jaw = jaw or r * .3
    for k in range(3):
        t = math.radians(90 + k * 120)
        c, s_ = math.cos(t), math.sin(t)
        X(sc, x0 - (8 if A > 0 else -L), 8, [(y0 + u * c - v * s_, z0 + u * s_ + v * c) for u, v in ((jaw, -4), (r * .9, -4), (r * .9, 4), (jaw, 4))],
          "dk", bias - 1)


# =====================================================================================
# ENGINE.VALVE — exhaust valve along +x: face at x=0 (looking -x), seat, tulip fillet, stem,
# collet grooves, tip at x=L. Reused by every op drawing.
# =====================================================================================
VR, VL, VS = 17.5, 112, 3.0


def valve3(sc, O=(0, 0, 0), A=(1, 0, 0), mat="w", head_mat=None, weld=True, R=VR, L=VL, rs=VS, face=True, upto=None, simple=False):
    """upto: stop the model at that length (stem cut off by a holder)."""
    hm = head_mat or mat
    pt = lambda x: _v(O, A, x)
    segs = [(0, 2.2, R, None, 0, hm, 36), (2.2, 3.6, R, R - 3.6, 0, hm, 36), (5.8, 6, R - 3.6, R * .42, 1, hm, 28),
            (11.8, 9, R * .42, rs * 1.5, 1, hm, 20), (20.8, 9, rs * 1.5, rs, 0, mat, 16)]
    x = 29.8
    for ln, dk in [(L - 16 - x, 0), (2.2, 2), (1.8, 0), (2.2, 2), (1.8, 0), (2.2, 2), (5.6, 0)]:
        segs.append((x, ln, rs - (.9 if dk else 0), None, dk, mat, 12))
        x += ln
    if simple:
        segs = [(0, 2.2, R, None, 0, hm, 20), (2.2, 3.6, R, R - 3.6, 0, hm, 20), (5.8, 15, R - 3.6, rs, 1, hm, 16), (20.8, L - 20.8, rs, None, 0, mat, 10)]
    for x0, ln, r, r1, dk, m, sg in segs:
        if upto is not None and x0 >= upto:
            break
        if upto is not None:
            ln = min(ln, upto - x0)
        CYL(sc, pt(x0), A, r, ln, m, seg=sg, r1=r1, dark=dk, bands=min(9, sg // 4))
    if weld and mat == "w":
        def wl(s_):
            return path(P([s_.cam.xy(_v(pt(62), u, rs)) for u in _ring_u(A, 100, 265)], False), "el")
        RAW(sc, wl, (tuple(min(pt(61.9)[i], pt(62.1)[i]) - (rs if abs(A[i]) < .9 else 0) for i in range(3)),
                     tuple(max(pt(61.9)[i], pt(62.1)[i]) + (rs if abs(A[i]) < .9 else 0) for i in range(3))), -2)
    if face:
        def fc(s_):
            c = _v(O, A, -.1)
            nA = tuple(-a for a in A)
            return path(P(circ3(s_.cam, c, nA, R * .8, 32)), "gr") + path(P(circ3(s_.cam, c, nA, R * .45, 24)), "gr")
        RAW(sc, fc, (tuple(O[i] - (R if abs(A[i]) < .9 else .2) for i in range(3)), tuple(O[i] + (R if abs(A[i]) < .9 else 0) for i in range(3))), -2)


def _ring_u(A, a0, a1, step=15):
    E1, E2, _ = GE.frame(A)
    out = []
    for k in range(a0, a1 + 1, step):
        t = math.radians(k)
        out.append(tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3)))
    return out


@dpart("engine.valve", "detail")
def valve_detail3():
    s, cam = opfit(lambda sc: valve3(sc), 24, 18, (40, 46, 420, 250), sh_k=.45)
    notes = [("傘部（フェース）", "燃焼室側。排気側は耐熱鋼・Ni基合金"),
             ("シート面（45°）", "バルブシートに当たる面。ステライト肉盛り＋研削"),
             ("軸部（ステム）", "ガイドを往復する。径公差数μm・窒化/めっき"),
             ("コッター溝", "リテーナとコッターで保持する溝"),
             ("軸端", "ロッカー・リフタが当たる。端面焼入れ"),
             ("摩擦圧接部", "傘部材と軸部材の接合位置（異材）")]
    s += balp(cam, (-.1, 0, -6), 30, 262, 1) + balp(cam, (4, -10, 12), 60, 44, 2) + balp(cam, (45, -VS, 0), 150, 262, 3)
    s += balp(cam, (VL - 9, 0, VS), 380, 60, 4) + balp(cam, (VL, 0, 0), 450, 200, 5) + balp(cam, (62, 0, VS), 250, 62, 6)
    return s, notes


def _v_fw():
    s = title("傘部用の耐熱鋼と軸部用の鋼を摩擦圧接")

    def fn(sc):
        chuck3(sc, -46, 24, 18, A=-1)
        CYL(sc, (-46, 0, 0), (1, 0, 0), 4.4, 44, "w", seg=20, bands=6)               # head-side bar (SUH35)
        CYL(sc, (-2, 0, 0), (1, 0, 0), 6.2, 2, "h", seg=20, bands=6)                  # flash ring
        CYL(sc, (0, 0, 0), (1, 0, 0), 3.6, 92, "w", seg=16, bands=5)                  # stem bar (SUH11)
        BOX(sc, 70, -12, -12, 30, 24, 24, "dk", ch=3)                                  # sliding clamp
        BOX(sc, 100, -18, -16, 18, 36, 32, "m", ch=3)
    s1, cam = opfit(fn, 22, 18, (24, 70, 410, 240))
    s += s1 + heat(*cam.xy((-1, 0, 9)), 2, 8)
    s += arc3(cam, (-60, 0, 0), (1, 0, 0), 30, 40, 150)
    a, b = cam.xy((152, 0, 0)), cam.xy((122, 0, 0))
    s += arrow(a[0], a[1], b[0], b[1], None)
    s += lbl(cam, (150, 0, 0), "押し付け", 0, -12, "middle", "al") + lbl(cam, (-60, 0, -36), "回転", 0, 14, "middle", "al")
    s += lbl(cam, (-24, 0, -6), "SUH35（傘部側）", 0, 26) + lbl(cam, (40, 0, 10), "SUH11（軸部側）", 0, -14)
    s += lbl(cam, (-1, 0, -10), "接合部（バリ）", 0, 22, "middle", "sm")
    return s


def _v_upset():
    s = title("軸端を通電加熱して据え込み、傘部を型鍛造")

    def up(sc):
        CYL(sc, (-12, 0, 0), (1, 0, 0), 7.5, 12, "h", seg=24, bands=7, r1=4.4)         # upset bulb (hot)
        CYL(sc, (-20, 0, 0), (1, 0, 0), 12, 8, "cu", seg=24, bands=7)                  # anvil electrode
        CYL(sc, (0, 0, 0), (1, 0, 0), 3.6, 70, "w", seg=16, bands=5)
        BOX(sc, 6, -10, 3.6, 16, 20, 10, "cu", -1, ch=2)                                # clamp electrodes
        BOX(sc, 6, -10, -13.6, 16, 20, 10, "cu", -1, ch=2)
    s1, c1 = opfit(up, 24, 20, (20, 70, 236, 236), sh_k=.36)

    def die(sc):
        BOX(sc, -30, -30, -22, 60, 60, 20, "t", ch=3)                                   # lower die
        valve3(sc, (0, 0, -16), (0, 0, 1), head_mat="h", mat="w", weld=False, face=False, upto=34)
        BOX(sc, -30, -30, 52, 60, 60, 20, "t", ch=3)                                    # upper die (open)
    s2, c2 = opfit(die, -28, 26, (282, 46, 458, 250), sh_k=.4)
    s += s1 + s2
    s += lbl(c1, (14, 0, -14), "電極", 0, 30) + lbl(c1, (-14, 0, 10), "通電加熱", 0, -14, "middle", "al")
    s += arrow(234, 156, 278, 156, None)
    a, b = c2.xy((40, 0, 70)), c2.xy((40, 0, 40))
    s += arrow(a[0], a[1], b[0], b[1], None) + text(385, 280, "傘部の型鍛造", "middle")
    return s


def _v_heat():
    s = title("材料に応じて溶体化・時効や焼入れ焼戻し")

    def fn(sc):
        BOX(sc, -100, 20, -10, 200, 12, 110, "m", dark=1)                                # back wall
        BOX(sc, -112, -40, -10, 12, 72, 110, "m", dark=1)                               # side walls
        BOX(sc, 100, -40, -10, 12, 72, 110, "m", dark=1)
        BOX(sc, -112, -40, -22, 224, 72, 12, "m")                                       # hearth
        BOX(sc, -112, -40, 100, 224, 72, 10, "m")                                       # roof
        for z in (24, 76):                                                           # heaters on the back wall
            CYL(sc, (-96, 16, z), (1, 0, 0), 2.4, 192, "h", -1, seg=10, bands=4)
        BOX(sc, -80, -24, -10, 160, 32, 6, "dk", -1)                                     # tray
        for k in range(5):
            valve3(sc, (-64 + k * 32, -8, -4), (0, 0, 1), weld=False, face=False, R=11, L=86, rs=2.2, simple=True)
    s1, cam = opfit(fn, -20, 16, (60, 36, 420, 262))
    s += s1 + heat(*cam.xy((0, -40, 104)), 3, 12)
    s += tol(40, 288, "硬さ・組織")
    return s


def _v_pta():
    s = title("排気バルブのシート面にステライトをプラズマ粉体肉盛り")
    tA = GE._norm((.55, -.25, .8))
    tip = (6, -6, 17)

    def fn(sc):
        chuck3(sc, 70, 18, 14)
        valve3(sc, upto=84)
        CYL(sc, _v(tip, tA, 6), tA, 5, 14, "t", -2, seg=16, bands=5, r1=8)              # nozzle
        CYL(sc, _v(tip, tA, 20), tA, 10, 34, "m", -2, seg=20, bands=6)                  # torch body
    s1, cam = opfit(fn, 26, 18, (40, 40, 440, 262))
    s += s1 + band(cam, (2.2, 0, 0), VR, (5.8, 0, 0), VR - 3.6, (1, 0, 0), "coat")
    a, b = cam.xy(_v(tip, tA, 6)), cam.xy((3.5, -3, 15.5))
    s += line(a[0], a[1], b[0], b[1], "beam") + sparks(b[0], b[1], 9, 5, -170, -20)
    s += arc3(cam, (40, 0, 0), (1, 0, 0), 12, 100, 200) + lbl(cam, (40, -12, -12), "回転", 0, 20, "middle", "al")
    s += lbl(cam, _v(tip, tA, 54), "プラズマトーチ（粉体供給）", 22, 4, "start")
    s += tol(300, 288, "肉盛り厚・希釈率・割れ")
    return s


def _v_turn():
    s = title("傘部と軸部を旋削")

    def fn(sc):
        chuck3(sc, 70, 18, 14)
        valve3(sc, upto=84)
        BOX(sc, 1, -66, -5, 12, 42, 8, "m", -3)                                          # tool holder from the front
        Z(sc, -2, 4, [(1.5, -16.6), (5, -24.5), (11, -24.5), (6.5, -15)], "t", -4)        # insert at the seat
    s1, cam = opfit(fn, 26, 18, (40, 40, 440, 262))
    s += s1 + band(cam, (2.2, 0, 0), VR, (5.8, 0, 0), VR - 3.6, (1, 0, 0), "mfa")
    s += rim(cam, (0, 0, 0), (-1, 0, 0), VR, "mf", False) + sil(cam, (30, 0, 0), (66, 0, 0), VS)
    s += arc3(cam, (40, 0, 0), (1, 0, 0), 12, 100, 200) + lbl(cam, (40, -12, -12), "回転", 0, 20, "middle", "al")
    s += arrow3(cam, (-4, -58, -12), (-4, -58, 14)) + lbl(cam, (-4, -58, -12), "送り", -4, 14, "end", "al")
    return s


def _v_grind():
    s = title("軸部をセンタレス研削、シート面をアンギュラ研削")
    gA = GE._norm((1, 0, 1))

    def fn(sc):
        valve3(sc)
        CYL(sc, (34, 38, -6), (1, 0, 0), 34, 64, "gw", 2, seg=40, bands=10)              # grinding wheel (behind)
        CYL(sc, (34, -26, -14), (1, 0, 0), 20, 64, "dk", 1, seg=32, bands=8)              # regulating wheel (front)
        BOX(sc, 34, -4, -12, 64, 8, 9, "m", 1)                                           # work rest blade
        CYL(sc, (0.2, 0, 21), gA, 13, 7, "gw", -2, seg=28, bands=8)                       # angular wheel on the seat
    s1, cam = opfit(fn, 18, 34, (40, 40, 440, 262))
    s += s1 + sil(cam, (30, 0, 0), (34, 0, 0), VS) + band(cam, (2.2, 0, 0), VR, (5.8, 0, 0), VR - 3.6, (1, 0, 0), "mfa")
    s += sil(cam, (98, 0, 0), (VL - 16, 0, 0), VS)
    s += lbl(cam, (66, 38, 28), "研削砥石", 0, -6, "middle", "al") + lbl(cam, (98, -26, -14), "調整車", 10, 4, "start")
    s += lbl(cam, (0, 0, 36), "アンギュラ砥石", -14, -4, "end", "al")
    s += tol(40, 288, "軸径 数μm・シート振れ")
    return s


def _v_bath():
    s = title("軸部を窒化・硬質クロムめっきして耐摩耗性を上げる")

    def fn(sc):
        BOX(sc, -110, 30, -60, 220, 8, 70, "m", dark=1)                                 # tank back
        BOX(sc, -118, -40, -60, 8, 78, 70, "m", dark=1)
        BOX(sc, 110, -40, -60, 8, 78, 70, "m", dark=1)
        BOX(sc, -118, -40, -68, 236, 78, 8, "m")
        BOX(sc, -110, -40, -60, 220, 70, 56, "fl", -.5)                                 # bath
        CYL(sc, (-120, -6, 66), (1, 0, 0), 3, 240, "m", -1, seg=12, bands=4)            # hanger bar
        for k in range(7):
            x = -84 + k * 28
            CYL(sc, (x, -6, -4), (0, 0, 1), 2.2, 70, "w", -1, seg=12, bands=4)          # stems dipped (heads below)
            BOX(sc, x - 3, -9, 62, 6, 6, 4, "dk", -1)
    s1, cam = opfit(fn, -18, 22, (50, 40, 430, 262))
    s += s1
    s += lbl(cam, (0, -40, -4), "処理液（めっき浴）・窒化", 0, 18, "middle", "sm")
    s += tol(40, 288, "窒化層深さ・めっき膜厚")
    return s


def _v_insp():
    s = title("軸径・全長・シート振れと外観を全数検査")

    def fn(sc):
        valve3(sc)
        for x in (44, 92):
            BOX(sc, x - 6, -10, -26, 12, 20, 23, "m")                                     # V-blocks
            CYL(sc, (x, 0, VS), (0, 0, 1), 2, 22, "t", -2, seg=10, bands=4)               # gauge probes
            BOX(sc, x - 6, -6, VS + 22, 12, 12, 22, "dk", -2, ch=2)
        BOX(sc, -26, -12, 52, 22, 24, 20, "dk", -3, ch=3)                                 # camera over the face
        CYL(sc, (-15, 0, 46), (0, 0, 1), 6, 6, "m", -3, seg=16, bands=5)
    s1, cam = opfit(fn, 26, 22, (40, 40, 440, 262))
    s += s1
    a, b = cam.xy((-15, 0, 46)), cam.xy((-6, 0, 10))
    s += line(a[0], a[1], b[0], b[1], "o thin dash") + lbl(cam, (-15, 0, 72), "画像検査", -30, 0, "end")
    s += lbl(cam, (68, 0, 48), "外径ゲージ", 0, -6, "middle", "sm")
    return s


@dpart("engine.valve", "ops")
def valve_ops3():
    return [fin(f()) for f in (_v_fw, _v_upset, _v_heat, _v_pta, _v_turn, _v_grind, _v_bath, _v_insp)]


# =====================================================================================
# ENGINE.TURBO — model of il3_engine.turbo split into parts (compressor scroll x<36, bearing
# housing 36..66, turbine scroll 66..106, wastegate), plus exposed wheels for the rotor ops.
# =====================================================================================
def spiral(r0, r1, a0=200, span=330, seg=22):
    return banded(hull([(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
                        for r, a in ((r0 + (r1 - r0) * k / seg, a0 + span * k / seg) for k in range(seg + 1))]), 2)


def _shc(mat, nrm, dark=0):
    return "%ss%d" % (mat, min(4, GE.shade(nrm, dark)))


def wheel_svg(cam, Cb, A, L, rb, rn, rtb, rtn, nb=11, sweep=40, mat="w", hub_mat=None, back=2.0, seg=32, lines=True):
    """bladed wheel (compressor / turbine): back disc at Cb, hub narrowing to the nose along A."""
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    hm = hub_mat or mat

    def W(a, r, th):
        return tuple(Cb[i] + A[i] * (back + a * L) + r * (math.cos(th) * E1[i] + math.sin(th) * E2[i]) for i in range(3))
    dep0 = cam.P(_v(Cb, A, back + L * .4))[2]
    pre, post = [], []
    for k in range(nb):
        th0 = 2 * PI * k / nb
        hub, tip = [], []
        nj = 6 if lines else 4
        for j in range(nj):
            a = j / (nj - 1)
            th = th0 + math.radians(sweep) * a * a
            hub.append(W(a, rn + (rb * .92 - rn) * (1 - a) ** 2, th))
            tip.append(W(a * .96, rtb + (rtn - rtb) * a, th))
        poly_ = hub + tip[::-1]
        nx = ny = nz = 0.0
        for i in range(len(poly_)):
            p, q = poly_[i], poly_[(i + 1) % len(poly_)]
            nx += (p[1] - q[1]) * (p[2] + q[2])
            ny += (p[2] - q[2]) * (p[0] + q[0])
            nz += (p[0] - q[0]) * (p[1] + q[1])
        nrm = GE._norm((nx, ny, nz))
        if GE._dot(nrm, cam.D) > 0:
            nrm = tuple(-v for v in nrm)
        c = tip[nj // 2]
        sv = path(P([cam.xy(p) for p in poly_]), _shc(mat, nrm)) + (path(P([cam.xy(p) for p in tip], False), "el") if lines else "")
        (pre if cam.P(c)[2] > dep0 else post).append((cam.P(c)[2], sv))
    o = "".join(v for _, v in sorted(pre, key=lambda t: -t[0]))
    o += compact(GE.prism(cam, Cb, A, GE.circle_outline(rb, seg, 10), back, hm, smooth=True))
    o += compact(GE.prism(cam, _v(Cb, A, back), A, GE.circle_outline(rb * .92, seg, 10), L, hm, smooth=True,
                          scale=lambda t: 1 - (1 - rn / (rb * .92)) * (1 - (1 - t) ** 2)))
    o += "".join(v for _, v in sorted(post, key=lambda t: -t[0]))
    return o


def _bbx(C, A, r, h):
    lo = tuple(min(C[i], C[i] + A[i] * h) - (r if abs(A[i]) < .9 else 0) for i in range(3))
    hi = tuple(max(C[i], C[i] + A[i] * h) + (r if abs(A[i]) < .9 else 0) for i in range(3))
    return lo, hi


def comp_wheel(sc, Cb=(-6, 0, 0), A=(-1, 0, 0), s=1.0, mat="w", bias=0, nb=11, seg=32):
    RAW(sc, lambda s_: wheel_svg(s_.cam, Cb, A, 18 * s, 26 * s, 5 * s, 26 * s, 17 * s, nb, -55, mat, seg=seg, lines=nb > 9),
        _bbx(Cb, A, 26 * s, 20 * s), bias)


def turb_wheel(sc, Cb=(72, 0, 0), A=(1, 0, 0), s=1.0, mat="w", bias=0, nb=11, seg=32):
    RAW(sc, lambda s_: wheel_svg(s_.cam, Cb, A, 20 * s, 24 * s, 6 * s, 24 * s, 19 * s, nb, 35, mat, seg=seg, lines=nb > 9),
        _bbx(Cb, A, 24 * s, 22 * s), bias)


def comp_housing(sc, wheel=True, lite=False):
    cv = spiral(50, 66, seg=16)
    X(sc, -9, 9, cv, "w", smooth=True, scale=lambda t: .84 + .16 * t)
    X(sc, 0, 28, cv, "w", smooth=True)
    X(sc, 28, 8, cv, "w", smooth=True, dark=1, scale=lambda t: 1 - .14 * t)
    if lite:
        CYL(sc, (-40, 0, 0), (1, 0, 0), 35, 31, "w", seg=28, bands=8, holes=[GE.circle_outline(28.5, 20, 5)])
    else:
        CYL(sc, (-34, 0, 0), (1, 0, 0), 34, 25, "w", seg=32, bands=8, holes=[GE.circle_outline(28.5, 24, 6)])
        CYL(sc, (-40, 0, 0), (1, 0, 0), 36, 6, "w", seg=32, bands=8, holes=[GE.circle_outline(28.5, 24, 6)])
    if wheel:
        def wl(s_):
            cam = s_.cam
            x = -9
            o = path(P(circ3(cam, (x, 0, 0), (1, 0, 0), 28.5, 32)), "ms3")
            d = ""
            nbl = 7 if lite else 10
            for k in range(nbl):
                a0 = 2 * math.pi * k / nbl
                d += P([cam.xy((x - 3 * j, (6 + 4.4 * j) * math.cos(a0 + .16 * j), (6 + 4.4 * j) * math.sin(a0 + .16 * j))) for j in range(6)], False)
            return o + path(d, "el") + path(P(circ3(cam, (x - 16, 0, 0), (1, 0, 0), 6, 12)), "m")
        RAW(sc, wl, ((-9.1, -28, -28), (-9, 28, 28)), -1)
    if lite:
        CYL(sc, (14, -46, 30), (0, 0, 1), 18, 51, "w", -1, seg=24, bands=7)
    else:
        CYL(sc, (14, -46, 30), (0, 0, 1), 17, 46, "w", -1, seg=28)
        CYL(sc, (14, -46, 76), (0, 0, 1), 20, 5, "w", -1, seg=28)
    RAW(sc, lambda s_: hole3(s_.cam, (14, -46, 81.1), (0, 0, 1), 13, "bg"), ((-6, -66, 81), (34, -26, 81.2)), -2)


def bearing_housing(sc, bias=0):
    CYL(sc, (36, 0, 0), (1, 0, 0), 30, 30, "m", bias, seg=32, dark=1)
    CYL(sc, (51, 0, 26), (0, 0, 1), 8, 10, "m", bias - 1, seg=16)
    RAW(sc, lambda s_: hole3(s_.cam, (51, 0, 36.1), (0, 0, 1), 4), ((43, -8, 36), (59, 8, 36.2)), bias - 2)


def turb_housing(sc, wg=True, lite=False):
    tv = spiral(44, 60, 160)
    X(sc, 66, 8, tv, "m", smooth=True, scale=lambda t: .84 + .16 * t)
    X(sc, 74, 32, tv, "m", smooth=True, dark=1)
    BOX(sc, 72, -56, -78, 40, 52, 10, "m", -1, ch=4)
    X(sc, 82, 20, [(-48, -68), (-12, -68), (-8, -40), (-44, -40)], "m", -1, dark=1)
    if wg:
        CYL(sc, (2, -66, -44), (1, 0, 0), 2.2, 84, "m", -1, seg=8, bands=4)
        CYL(sc, (-14, -66, -44), (1, 0, 0), 17, 16, "m", -2, seg=20 if lite else 28, bands=6 if lite else 12)


def turbo_all(sc, lite=False):
    comp_housing(sc, lite=lite)
    bearing_housing(sc)
    turb_housing(sc, lite=lite)


def rotor(sc, housing=False, nb=11, seg=32):
    """compressor wheel - shaft - turbine wheel (axis x), optionally in the bearing housing."""
    comp_wheel(sc, (12, 0, 0), nb=nb, seg=seg)
    if housing:
        CYL(sc, (12, 0, 0), (1, 0, 0), 4, 24, "w", seg=16, bands=5)
        bearing_housing(sc)
        CYL(sc, (66, 0, 0), (1, 0, 0), 4, 6, "w", seg=16, bands=5)
    else:
        CYL(sc, (12, 0, 0), (1, 0, 0), 4, 60, "w", seg=16, bands=5)
    turb_wheel(sc, (72, 0, 0), nb=nb, seg=seg)


@dpart("engine.turbo", "detail")
def turbo_detail3():
    s, cam = opfit(lambda sc: turbo_all(sc, True), 28, 24, (24, 36, 300, 258), sh_k=.45)
    s2, c2 = opfit(lambda sc: rotor(sc, nb=8, seg=20), 28, 20, (318, 150, 470, 262), sh_k=.4)
    s += s2 + text(394, 284, "回転体（ロータ）", "middle", "sm")
    notes = [("コンプレッサホイール", "アルミ。吸気を圧縮する翼（5軸削り出し）"), ("タービンホイール", "Ni基超合金の精密鋳造。900℃級の排気で回る"),
             ("センタハウジング", "軸受と潤滑油路。軸受穴の同軸度"), ("タービンハウジング", "耐熱鋳鋼。排気の渦巻き流路"), ("ウェイストゲート", "過給圧を逃がす弁")]
    s += balp(c2, (4, 0, 20), 340, 60, 1) + balp(c2, (84, 0, 18), 456, 120, 2)
    s += balp(cam, (51, -10, -28), 150, 284, 3) + balp(cam, (90, -40, 40), 300, 44, 4) + balp(cam, (-14, -82, -44), 40, 270, 5)
    return s, notes


def _t_cast():
    s = title("ワックス模型をセラミックで覆い、真空中でNi基超合金を鋳込む")
    s1, c1 = opfit(lambda sc: turb_wheel(sc, (0, 0, 0), (0, 0, 1), mat="pt"), -30, 30, (40, 90, 170, 220), sh_k=.4)

    def mold(sc):
        CYL(sc, (0, 0, 0), (0, 0, 1), 34, 40, "pt", seg=32, bands=8, dark=.5)          # ceramic shell
        CYL(sc, (0, 0, 40), (0, 0, 1), 12, 10, "pt", seg=20, bands=6, r1=6)
        CYL(sc, (0, 0, 50), (0, 0, 1), 9, 12, "pt", seg=20, bands=6, r1=16)             # pouring cup
        RAW(sc, lambda s_: hole3(s_.cam, (0, 0, 62.1), (0, 0, 1), 12, "h"), ((-16, -16, 62), (16, 16, 62.2)), -2)
        CYL(sc, (34, 0, 96), GE._norm((-1, 0, -.6)), 18, 34, "m", -3, seg=24, bands=7)   # tilted crucible
    s2, c2 = opfit(mold, -30, 24, (230, 40, 440, 262), sh_k=.4)
    s += s1 + s2 + arrow(186, 160, 226, 160, None)
    a, b = c2.xy((10, 0, 82)), c2.xy((0, 0, 62))
    s += path("M%s %s Q%s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] - 6), n((a[1] + b[1]) / 2), n(b[0]), n(b[1])), "pour")
    s += text(105, 244, "ワックス模型", "middle") + lbl(c2, (0, -34, 0), "シェル鋳型に注湯", 0, 34)
    s += lbl(c2, (40, 0, 120), "真空溶解", 20, -6, "start", "sm")
    s += tol(20, 290, "X線・蛍光浸透探傷で翼の欠陥を確認")
    return s


def _t_weld():
    s = title("タービンホイールと鋼製シャフトを摩擦圧接・電子ビーム溶接")

    def fn(sc):
        chuck3(sc, -40, 26, 16, A=-1)
        CYL(sc, (-40, 0, 0), (1, 0, 0), 5, 120, "w", seg=18, bands=6)
        CYL(sc, (80, 0, 0), (1, 0, 0), 8, 2, "h", seg=20, bands=6)                     # weld bead / flash
        turb_wheel(sc, (82, 0, 0), s=1.3)
        BOX(sc, 112, -20, -20, 26, 40, 40, "dk", ch=4)                                   # wheel holder
    s1, cam = opfit(fn, 26, 20, (30, 50, 400, 248))
    s += s1 + heat(*cam.xy((81, 0, 10)), 2, 8)
    s += arc3(cam, (10, 0, 0), (1, 0, 0), 16, 100, 210) + lbl(cam, (10, 0, -16), "回転", 0, 22, "middle", "al")
    a, b = cam.xy((168, 0, 0)), cam.xy((142, 0, 0))
    s += arrow(a[0], a[1], b[0], b[1], None) + lbl(cam, (82, 0, 30), "接合部", 0, -10, "middle", "sm")
    s += tol(300, 288, "接合強度・振れ")
    return s


def _t_5ax():
    s = title("アルミ鍛造ビレットから5軸加工で翼を削り出す")
    tA = GE._norm((-.6, -.2, .78))
    tip = (12, -4, 22)

    def fn(sc):
        CYL(sc, (0, 0, -30), (0, 0, 1), 46, 20, "m", seg=40, bands=10)                  # C-axis table
        CYL(sc, (0, 0, -10), (0, 0, 1), 30, 8, "dk", seg=32, bands=8)
        comp_wheel(sc, (0, 0, -2), (0, 0, 1), s=1.4)
        CYL(sc, tip, tA, 3, 34, "t", -3, seg=12, bands=4)                                # ball end mill
        CYL(sc, _v(tip, tA, 34), tA, 9, 30, "m", -3, seg=20, bands=6, r1=12)            # holder
    s1, cam = opfit(fn, -30, 30, (60, 38, 400, 262))
    s += s1 + arc3(cam, (0, 0, -20), (0, 0, 1), 54, -40, 50)
    s += lbl(cam, (54, 0, -20), "C軸回転", 20, 10, "start", "al") + lbl(cam, _v(tip, tA, 64), "工具傾斜（A軸）", 14, 0, "start", "al")
    s += tol(20, 288, "翼厚・翼形状・面粗さ（三次元測定）")
    return s


def _t_house():
    s = title("タービンハウジングを砂型鋳造し、フランジ面・取付穴を加工")

    def fn(sc):
        tv = spiral(44, 60, 160)
        flip = [(u, -v, f) for u, v, f in tv][::-1]
        X(sc, 66, 8, flip, "w", smooth=True, scale=lambda t: .84 + .16 * t)
        X(sc, 74, 32, flip, "w", smooth=True, dark=1)
        X(sc, 82, 20, [(-48, 40), (-44, 68), (-8, 68), (-12, 40)], "w", -1, dark=1)
        BOX(sc, 72, -56, 68, 40, 52, 10, "w", -1, ch=4)                                  # inlet flange (face up)

        def holes(s_):
            o = ""
            for x, y in ((78, -50), (106, -50), (78, -10), (106, -10)):
                o += hole3(s_.cam, (x, y, 78.1), (0, 0, 1), 2.6)
            return o + hole3(s_.cam, (92, -30, 78.1), (0, 0, 1), 14, "w3") + hole3(s_.cam, (92, -30, 78.1), (0, 0, 1), 11.5, "bg")
        RAW(sc, holes, ((72, -56, 78), (112, -4, 78.2)), -2)
        CYL(sc, (104, -20, 82), (0, 0, 1), 22, 10, "t", -3, seg=28, bands=8)             # face mill
        CYL(sc, (104, -20, 92), (0, 0, 1), 12, 26, "m", -3, seg=20, bands=6)
    s1, cam = opfit(fn, -30, 26, (60, 38, 420, 262))
    pts = [(72, -56, 78.1), (112, -56, 78.1), (112, -4, 78.1)]
    s += s1 + path(P([cam.xy(p) for p in pts], False), "mf")
    s += arc3(cam, (104, -20, 108), (0, 0, 1), 18, -30, 80) + lbl(cam, (104, -20, 118), "正面フライス", 30, -4, "start", "al")
    s += lbl(cam, (90, -60, 0), "耐熱鋳鋼（砂型鋳造）", -30, 30, "end", "sm")
    return s


def _t_hone():
    s = title("センタハウジングの軸受穴を精密加工・ホーニング")

    def fn(sc):
        RING(sc, (36, 0, 0), (1, 0, 0), 30, 9, 30, "w", seg=40, bands=10, dark=1)
        CYL(sc, (51, 0, 26), (0, 0, 1), 8, 10, "w", -1, seg=16)
        RAW(sc, lambda s_: hole3(s_.cam, (51, 0, 36.1), (0, 0, 1), 4), ((43, -8, 36), (59, 8, 36.2)), -2)
        CYL(sc, (-60, 0, 0), (1, 0, 0), 5, 66, "t", -1, seg=14, bands=4)                 # hone bar
        CYL(sc, (6, 0, 0), (1, 0, 0), 8.6, 30, "gw", -1, seg=20, bands=6)                 # stones (entering)
        CYL(sc, (-90, 0, 0), (1, 0, 0), 14, 30, "m", -1, seg=24, bands=7)                 # spindle
    s1, cam = opfit(fn, 30, 20, (40, 46, 440, 250))
    s += s1 + rim(cam, (36, 0, 0), (1, 0, 0), 9, "mf", False)
    s += arc3(cam, (-40, 0, 0), (1, 0, 0), 12, 100, 210) + lbl(cam, (-40, 0, -12), "回転", 0, 22, "middle", "al")
    s += arrow3(cam, (-30, 0, 20), (6, 0, 20), True) + lbl(cam, (-12, 0, 20), "往復", 0, -8, "middle", "al")
    s += tol(40, 284, "軸受穴の真円度・同軸度・油路")
    return s


def _t_vsr():
    s = title("回転体を組み、実回転域まで回してバランスを修正（VSR）")
    s1, cam = opfit(lambda sc: rotor(sc, True), 28, 20, (20, 50, 310, 250))
    s += s1 + arc3(cam, (51, 0, 0), (1, 0, 0), 40, 60, 170)
    s += chart(320, 190, 150, 80, "noise") + text(395, 290, "高速域の振動", "middle", "sm")
    s += lbl(cam, (51, 0, 40), "センタハウジングごと回す", 0, -14, "middle", "sm")
    return s


def _t_wg():
    s = title("ハウジングを組み、ウェイストゲートを調整・漏れを確認")
    s1, cam = opfit(turbo_all, 28, 24, (60, 36, 420, 262))
    s += s1 + arrow3(cam, (30, -66, -64), (60, -66, -64), True)
    s += lbl(cam, (45, -66, -64), "WG作動", 0, 18, "middle", "al")
    return s


@dpart("engine.turbo", "ops")
def turbo_ops3():
    return [fin(f()) for f in (_t_cast, _t_weld, _t_5ax, _t_house, _t_hone, _t_vsr, _t_wg)]


# =====================================================================================
# ENGINE.INJECTOR — model of il3_engine.injector (tip at x=0 looking -x, fuel inlet at x=145).
# vertical=True stands it tip-down (model x -> world z).
# =====================================================================================
INJ_SEG = ((4, 4, "w", 0, None), (3, 4.4, "pt", 0, None), (2, 3.6, "w", 2, None), (20, 4.6, "w", 0, None),
           (6, 4.6, "w", 0, 7.5), (34, 7.5, "w", 0, None), (6, 11, "w", 0, None), (42, 13, "w", 0, None),
           (6, 10, "w", 1, None), (8, 8.6, "w", 0, None), (4, 9.6, "dk", 0, None), (10, 8.6, "w", 0, None))
INJ_L = 145


def _imap(p, vertical, O):
    x, y, z = p
    q = (-z, y, x) if vertical else (x, y, z)
    return (O[0] + q[0], O[1] + q[1], O[2] + q[2])


def injector3(sc, O=(0, 0, 0), vertical=False, upto=None, bias=0, mat="w"):
    A = (0, 0, 1) if vertical else (1, 0, 0)
    M = lambda p: _imap(p, vertical, O)

    def tip(s_):
        o = ""
        for k in range(6):
            a = 2 * PI * k / 6
            o += hole3(s_.cam, M((-.05, 2.2 * math.cos(a), 2.2 * math.sin(a))), tuple(-v for v in A), .55, "bg", 8)
        return o
    lo, hi = M((-.1, -4, -4)), M((0, 4, 4))
    RAW(sc, tip, (tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3))), bias - 2)
    x = 0
    for L, r, m, dk, r1 in INJ_SEG:
        if upto is not None and x >= upto:
            return
        m = mat if m == "w" else m
        CYL(sc, M((x, 0, 0)), A, r, L, m, bias, seg=28 if r > 6 else 16, bands=8 if r > 6 else 5, dark=dk, r1=r1)
        x += L
    for (x0, y0, z0, sx, sy, sz) in ((92, -9, 12, 22, 18, 16), (84, -11, 28, 30, 22, 14)):
        a, b = M((x0, y0, z0)), M((x0 + sx, y0 + sy, z0 + sz))
        c = tuple(min(a[i], b[i]) for i in range(3))
        d = tuple(max(a[i], b[i]) - c[i] for i in range(3))
        BOX(sc, *c, *d, "dk", bias, ch=3)
    if not vertical:
        RAW(sc, lambda s_: path(P([s_.cam.xy(M(p)) for p in ((87, -6, 42.05), (111, -6, 42.05), (111, 6, 42.05), (87, 6, 42.05))]), "bg"),
            (M((84, -11, 42)), M((114, 11, 42.1))), bias - 2)


def inj_inset(x0=372, y0=56, w=96, h=214, lab=True):
    """2D section of the nozzle tip (body, fuel passage, needle, seat, spray holes)."""
    cx = x0 + w / 2
    s = rect(x0, y0, w, h, "m", 4) + (text(cx, y0 + 16, "先端の断面", "middle", "sm") if lab else "")
    yt, yb = y0 + 28, y0 + h - 30                          # body top / seat apex
    ro, rb = 34, 10
    s += path(P([(cx - ro, yt), (cx - rb, yt), (cx - rb, yb - 24), (cx, yb - 12), (cx + rb, yb - 24), (cx + rb, yt), (cx + ro, yt),
                 (cx + ro, yb - 40), (cx + 12, yb + 2), (cx - 12, yb + 2), (cx - ro, yb - 40)]), "cut")
    s += path(P([(cx - rb, yt), (cx - rb, yb - 24), (cx, yb - 12), (cx + rb, yb - 24), (cx + rb, yt)]), "void")
    s += path(P([(cx - 6, yt - 10), (cx + 6, yt - 10), (cx + 6, yb - 30), (cx, yb - 22), (cx - 6, yb - 30)]), "w")
    for a in (-35, 0, 35):
        r = math.radians(a + 90)
        s += line(cx, yb - 10, cx + 24 * math.cos(r), yb - 10 + 24 * math.sin(r), "hid")
    return s, (cx, yb - 12), (cx + 7.5, yb - 26), (cx, yt + 40), (cx + 8, yt + 70)


@dpart("engine.injector", "detail")
def injector_detail3():
    s, cam = opfit(lambda sc: injector3(sc), 30, 24, (24, 40, 350, 262), sh_k=.45)
    t, hole, seat, ndl, bore = inj_inset()
    s += t
    notes = [("ノズルボディ", "スイス型自動旋盤で加工"), ("噴孔", "φ0.1mm前後を複数。放電・レーザで加工"),
             ("シート", "ニードルが着座する円すい面。数μmのすき間"), ("ニードル", "ソレノイド／ピエゾで駆動"), ("燃料通路", "中心の細長い穴")]
    s += balp(cam, (40, 0, 7.5), 130, 50, 1) + bal(hole[0], hole[1] + 4, 400, 288, 2) + bal(seat[0], seat[1], 456, 160, 3)
    s += bal(ndl[0], ndl[1], 352, 120, 4) + bal(bore[0] + 1, bore[1], 456, 90, 5)
    return s, notes


def _i_swiss():
    s = title("小径の長物をスイス型自動旋盤で加工")

    def fn(sc):
        BOX(sc, -136, -30, -30, 30, 60, 60, "pt", dark=1, ch=4)                           # headstock
        CYL(sc, (-110, 0, 0), (1, 0, 0), 4.6, 104, "w", seg=16, bands=5)                  # bar stock
        BOX(sc, -30, -26, -30, 20, 52, 60, "m", ch=4)                                      # guide bushing support
        CYL(sc, (-10, 0, 0), (1, 0, 0), 12, 4, "dk", -1, seg=24, bands=7)                  # guide bushing
        x = -6
        for L, r in ((8, 4.6), (16, 3.6), (6, 4.4), (20, 3.2)):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=16, bands=5)
            x += L
        BOX(sc, -2, -56, -3, 8, 46, 6, "m", -3)                                            # tool from the front
        Z(sc, -1.5, 3, [(-1, -4.2), (3, -10), (7, -10), (5, -4.2)], "t", -4)
    s1, cam = opfit(fn, 24, 22, (24, 60, 456, 250))
    s += s1 + rim(cam, (2, 0, 0), (1, 0, 0), 4.6, "mf")
    s += arrow3(cam, (-100, 0, 52), (-40, 0, 52)) + lbl(cam, (-70, 0, 52), "主軸が材料を送る", 0, -10, "middle", "al")
    s += lbl(cam, (-20, -26, -30), "ガイドブッシュ", 0, 22) + arc3(cam, (-70, 0, 0), (1, 0, 0), 12, 100, 210)
    s += lbl(cam, (2, -56, -3), "バイト", -8, 14, "end", "sm")
    return s


def _half_tube(sc, z0, L, ri, ro, mat="w", bias=0, seg=16):
    """back half of a tube along z (cut along the x-z plane, cut faces toward the viewer)."""
    out = arc(0, 0, ro, 0, 180, seg)
    inn = arc(0, 0, ri, 180, 0, seg // 2)
    Z(sc, z0, L, [(x, y, i // 2) for i, (x, y) in enumerate(out)] + [(x, y, 100 + i) for i, (x, y) in enumerate(inn)], mat, bias)


def _i_edm():
    s = title("φ0.1mm前後の噴孔を放電（またはレーザ）で加工")
    eA = GE._norm((.5, -.3, -.81))

    def fn(sc):
        injector3(sc, (0, 0, 0), True, upto=40)
        CYL(sc, _v((1.4, -1, -1.2), eA, -2), tuple(-v for v in eA), .5, 26, "t", -3, seg=8, bands=3)   # electrode
        CYL(sc, _v((1.4, -1, -1.2), eA, -28), tuple(-v for v in eA), 3, 14, "m", -3, seg=12, bands=4)  # holder
    s1, cam = opfit(fn, -30, 14, (40, 40, 280, 262))
    p = cam.xy(_v((1.4, -1, -1.2), eA, -2))
    s += s1 + sparks(p[0], p[1], 8, 5, -160, -20)
    # small section of the tip with the hole axes
    s += rect(300, 60, 160, 170, "m", 4) + text(380, 76, "先端断面", "middle", "sm")
    s += path("M330 90 L430 90 L430 170 L392 206 L368 206 L330 170Z", "cut") + path("M368 90 L392 90 L392 176 L380 188 L368 176Z", "void")
    for a in (-30, 0, 30):
        r = math.radians(a + 90)
        s += line(380, 190, 380 + 34 * math.cos(r), 190 + 34 * math.sin(r), "hid")
    s += line(380, 206, 380, 222, "mf")
    s += tol(300, 254, "噴孔径・角度・入口R")
    s += lbl(cam, _v((1.4, -1, -1.2), eA, -42), "電極（放電）", -10, 4, "end", "al")
    return s


def _i_heat():
    s = title("真空焼入れ・浸炭で耐摩耗性を持たせる")

    def fn(sc):
        CYL(sc, (-120, 60, 0), (1, 0, 0), 84, 240, "m", 2, seg=40, bands=10, dark=1.4, caps=False)  # chamber (inner wall)
        BOX(sc, -100, -50, -50, 200, 100, 8, "dk")                                         # tray
        for k in range(4):
            for j in range(3):
                CYL(sc, (-80 + j * 64, -36 + k * 24, -36), (1, 0, 0), 6, 50, "w", -1, seg=16, bands=5)
        for z in (-40, 40):
            CYL(sc, (-110, 50, z), (1, 0, 0), 2.4, 220, "h", 1, seg=10, bands=4)
    s1, cam = opfit(fn, -22, 24, (60, 40, 420, 262))
    s += s1 + lbl(cam, (0, -50, -50), "真空炉", 0, 28)
    return s


def _i_grind():
    s = title("シート部を内面研削し、ニードルを外径研削・ラッピング")

    def body(sc):
        _half_tube(sc, 0, 70, 7, 18, "w")
        Z(sc, -14, 14, [(x, y, i // 2) for i, (x, y) in enumerate(arc(0, 0, 18, 0, 180, 16))], "w", 0, scale=lambda t: .55 + .45 * t)
        CYL(sc, (0, 3, 16), (0, 0, 1), 5, 6, "gw", -2, seg=16, bands=5)                   # small internal wheel at the seat
        CYL(sc, (0, 3, 22), (0, 0, 1), 1.6, 70, "t", -2, seg=8, bands=3)                    # quill
    s1, c1 = opfit(body, -24, 18, (40, 40, 210, 262), sh_k=.4)
    # cut faces with the seat cone (section on the plane y=0)
    for sg in (1, -1):
        prof = [(7, 70), (18, 70), (18, 0), (10, -14), (2.5, -14), (2.5, -6), (7, 6)]
        s1 += path(P([c1.xy((sg * u, -.05, z)) for u, z in prof]), "cut")
    s1 += path(P([c1.xy((7, -.06, 6)), c1.xy((2.5, -.06, -6))], False) + P([c1.xy((-7, -.06, 6)), c1.xy((-2.5, -.06, -6))], False), "mf")
    s1 += arc3(c1, (0, 3, 50), (0, 0, 1), 10, -40, 60)

    def needle(sc):
        CYL(sc, (0, 0, 0), (1, 0, 0), 3, 100, "w", seg=16, bands=5)
        CYL(sc, (-6, 0, 0), (1, 0, 0), .8, 6, "w", seg=12, bands=4, r1=3)
        CYL(sc, (20, 40, -6), (1, 0, 0), 34, 50, "gw", 2, seg=36, bands=9)                 # OD wheel behind
        BOX(sc, 20, -5, -10, 50, 10, 7, "m", 1)                                            # rest
    s2, c2 = opfit(needle, 20, 30, (230, 60, 460, 250), sh_k=.4)
    s += s1 + s2 + sil(c2, (0, 0, 0), (20, 0, 0), 3) + sil(c2, (70, 0, 0), (100, 0, 0), 3)
    s += lbl(c1, (0, 0, -14), "ノズルボディ（内面研削）", 0, 22, "middle", "sm") + lbl(c2, (50, 0, -20), "ニードル（外径研削）", 0, 30, "middle", "sm")
    s += tol(250, 290, "すき間 数μm・真円度（サブμm）")
    return s


def _i_laser():
    s = title("ソレノイド（またはピエゾ）を組み付け、全周レーザ溶接")
    xw = 69

    def fn(sc):
        injector3(sc)
        BOX(sc, xw - 12, -12, 50, 24, 24, 24, "m", -3, ch=3)                               # laser head
        CYL(sc, (xw, 0, 50), (0, 0, -1), 5, 6, "dk", -3, seg=14, bands=4)
    s1, cam = opfit(fn, 30, 24, (40, 40, 440, 262))
    a, b = cam.xy((xw, 0, 44)), cam.xy((xw, 0, 11))
    s += s1 + line(a[0], a[1], b[0], b[1], "beam") + rim(cam, (xw, 0, 0), (1, 0, 0), 11, "mf") + sparks(b[0], b[1], 7, 4, -170, -10)
    s += arc3(cam, (20, 0, 0), (1, 0, 0), 12, 100, 210) + lbl(cam, (xw, 0, 74), "レーザ", 0, -6, "middle", "al")
    s += lbl(cam, (100, -12, -20), "ソレノイド部", 0, 30, "middle", "sm")
    return s


def _i_test():
    s = title("静的・動的流量、噴霧形状、漏れを全数確認")

    def fn(sc):
        injector3(sc, (0, 0, 0), True)
        BOX(sc, -40, -40, -88, 80, 80, 6, "m")
        CYL(sc, (0, 0, -82), (0, 0, 1), 34, 30, "fl", 1, seg=32, bands=8)                 # collecting vessel
    s1, cam = opfit(fn, -30, 18, (40, 36, 300, 262), sh_k=.36)
    x, y = cam.xy((0, 0, -1))
    yb = cam.xy((0, 0, -50))[1]
    s += s1 + spray_cone(x, y, 90, 40, yb - y) + drops(x, y + 2, 5, 30, (yb - y) * .9, 90)
    s += chart(320, 70, 140, 80, "step") + text(390, 166, "流量", "middle", "sm")
    s += chart(320, 182, 140, 64, "noise") + text(390, 262, "噴霧・漏れ", "middle", "sm")
    return s


@dpart("engine.injector", "ops")
def injector_ops3():
    return [fin(f()) for f in (_i_swiss, _i_edm, _i_heat, _i_grind, _i_laser, _i_test)]


# =====================================================================================
# DRIVETRAIN.SHAFT — counter shaft of il3_drive.tm_shaft along +x: spline 0-36, journal 39-61,
# shoulder 61-68, helical gear 68-104, body 104-152, small gear 152-180, journal 180-226, end 226-240
# =====================================================================================
SH_SEG = [("spl", 36, 15), ("c", 3, 12.5), ("c", 22, 18), ("c", 7, 24), ("g", 36, (19, 34, 24)),
          ("c", 48, 20), ("g", 28, (13, 23, -26)), ("c", 46, 17), ("c", 14, 12)]
SH_L = 240


def shaft3(sc, mats=None, upto=None, gears=True, spline=True, bias=0, gq="lo"):
    """mats: {segment index: material} (e.g. hot band); gears/spline False = plain blanks (before cutting)."""
    cam = sc.cam
    A = (1, 0, 0)
    x = 0.0
    for i, (kind, L, r) in enumerate(SH_SEG):
        if upto is not None and x >= upto:
            break
        m = (mats or {}).get(i, "w")
        if kind == "spl" and spline:
            sc.add(compact(GE.prism(cam, (x, 0, 0), A, GE.spline_outline(18, r, r - 2.3), L, m)), ((x, -r, -r), (x + L, r, r)), bias)
        elif kind == "g" and gears and (gq if isinstance(gq, str) else gq[i > 5]) != "fake":
            zz, rp, hx = r
            ra = rp * (1 + 2.0 / zz)
            sl = 1
            sc.add(compact(GE.gear3(cam, (x, 0, 0), A, zz, rp, L, m, helix=hx, slices=sl)), ((x, -ra, -ra), (x + L, ra, ra)), bias)
        elif kind == "g" and gears:
            zz, rp, hx = r
            ra = rp * (1 + 1.4 / zz)
            CYL(sc, (x, 0, 0), A, ra, L, m, bias, seg=32, bands=9)

            def teeth(s_, x=x, L=L, ra=ra, zz=zz, hx=hx):
                d = ""
                tw = L * math.tan(math.radians(hx)) / ra
                for k in range(zz):
                    t0 = 2 * PI * k / zz
                    ps = []
                    for j in range(4):
                        t = t0 + tw * j / 3
                        u = (0, math.cos(t), math.sin(t))
                        if GE._dot(u, s_.cam.D) > -0.12:
                            ps = []
                            break
                        ps.append(s_.cam.xy((x + L * j / 3, ra * u[1], ra * u[2])))
                    if ps:
                        d += P(ps, False)
                return path(d, "gr")
            RAW(sc, teeth, ((x, -ra, -ra), (x + L, ra, ra)), bias - .5)
        else:
            rr = r if kind == "c" else (r if kind == "spl" else r[1] * (1 + 2.0 / r[0]))
            CYL(sc, (x, 0, 0), A, rr, L, m, bias, seg=24 if rr > 16 else 20, bands=8, dark=2 if L <= 3 else 0)
        x += L
    face = lambda s_: hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 4.5, "w3") + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 2.6, "bg")
    RAW(sc, face, ((-.2, -15, -15), (0, 15, 15)), bias - 2)
    if upto is None:
        RAW(sc, lambda s_: hole3(s_.cam, (128, -20 * .6, -20 * .8), (0, -.6, -.8), 2.4), ((106, -20, -20), (150, 20, 20)), bias - 1)


def sh_x(i):
    return sum(L for _, L, _ in SH_SEG[:i])


@dpart("drivetrain.shaft", "detail")
def shaft_detail3():
    s, cam = opfit(lambda sc: shaft3(sc, gq=("lo", "fake")), 20, 20, (30, 40, 450, 250), sh_k=.45)
    a, b = cam.xy((0, 0, 0)), cam.xy((SH_L, 0, 0))
    s += path(P([a, b], False), "hid")
    notes = [("スプライン", "転造で成形。ギヤ・クラッチと結合"), ("一体ギヤ", "軸と一体の歯車。ホブ切り→研削"),
             ("軸受部", "玉軸受・針状ころが付く。径公差数μm"), ("段付き端面", "ギヤ・軸受の位置決め面"), ("油穴", "軸心からギヤへの潤滑油路")]
    s += balp(cam, (18, 0, 15), 60, 60, 1) + balp(cam, (86, 0, 37), 200, 46, 2) + balp(cam, (50, -6, -17), 110, 270, 3)
    s += balp(cam, (61, -16, 16), 40, 150, 4) + balp(cam, (128, -12, -16), 300, 270, 5)
    return s, notes


def _s_forge():
    s = title("段付き形状を冷間鍛造で押し出し、取り代を減らす")
    prof = [(16, 60), (16, 0), (10, 0), (10, -50), (40, -50), (40, 60)]          # die bore (r, z) on the cut plane

    def fn(sc):
        BOX(sc, -40, 0, -50, 80, 40, 110, "m", dark=.5)                                  # die, back half
        CYL(sc, (0, 0, 60), (0, 0, 1), 16, 40, "w", -1, seg=24, bands=7)                 # billet top (above the die)
        CYL(sc, (0, 0, 100), (0, 0, 1), 15, 30, "t", -2, seg=24, bands=7)                # punch
        CYL(sc, (0, 0, 130), (0, 0, 1), 26, 14, "m", -2, seg=28, bands=8)
    s1, cam = opfit(fn, -26, 20, (120, 36, 360, 262), sh_k=.4)

    def cutf(s_):
        o = ""
        for sg in (1, -1):
            o += path(P([cam.xy((sg * r, -.05, z)) for r, z in prof]), "cut")
        # formed work inside the die bore, seen on the cut plane
        o += path(P([cam.xy(p) for p in ((-16, -.1, 60), (16, -.1, 60), (16, -.1, 0), (10, -.1, 0), (10, -.1, -40), (-10, -.1, -40), (-10, -.1, 0), (-16, -.1, 0))]), "w")
        return o
    s += s1 + cutf(None)
    s += arrow3(cam, (34, 0, 170), (34, 0, 140)) + lbl(cam, (34, 0, 160), "加圧", 10, 0, "start", "al")
    s += text(80, 200, "常温で成形", "middle") + lbl(cam, (40, 0, -50), "ダイ", 20, 0, "start", "sm")
    return s


def _s_turn():
    s = title("外径・端面・溝を旋削し、センタ穴を加工")

    def fn(sc):
        chuck3(sc, 0, 30, 20, A=-1)
        shaft3(sc, gears=False, spline=False)
        CYL(sc, (SH_L + 2, 0, 0), (1, 0, 0), 2, 12, "m", -1, seg=12, bands=4, r1=9)       # tail centre
        CYL(sc, (SH_L + 14, 0, 0), (1, 0, 0), 12, 24, "m", -1, seg=20, bands=6)
        BOX(sc, 140, -70, -4, 10, 52, 8, "m", -3)                                          # tool from the front
        Z(sc, -2, 4, [(140, -17.5), (144, -24), (150, -24), (147, -17)], "t", -4)
    s1, cam = opfit(fn, 20, 20, (30, 46, 450, 262))
    s += s1 + sil(cam, (61, 0, 0), (68, 0, 0), 24) + sil(cam, (104, 0, 0), (152, 0, 0), 20) + sil(cam, (180, 0, 0), (226, 0, 0), 17)
    s += arrow3(cam, (170, -50, -12), (130, -50, -12)) + lbl(cam, (150, -50, -12), "送り", 0, 16, "middle", "al")
    s += arc3(cam, (20, 0, 0), (1, 0, 0), 22, 100, 200)
    s += tol(40, 284, "同軸度・振れ")
    return s


def _s_ih():
    s = title("浸炭焼入れまたは高周波焼入れで表面を硬化")
    xi = 196

    def fn(sc):
        shaft3(sc, mats={7: "h"}, gq="fake")
        CYL(sc, (xi, 0, 0), (1, 0, 0), 26, 10, "cu", -2, seg=32, bands=8, holes=[GE.circle_outline(20, 24, 6)])   # coil
        CYL(sc, (xi + 3, 0, 26), (0, 0, 1), 3, 30, "cu", -3, seg=10, bands=3)
        CYL(sc, (xi + 7, 0, 26), (0, 0, 1), 3, 30, "cu", -3, seg=10, bands=3)
    s1, cam = opfit(fn, 20, 20, (30, 46, 450, 262))
    s += s1 + arrow3(cam, (xi + 16, 0, 46), (xi - 30, 0, 46)) + lbl(cam, (xi, 0, 56), "高周波コイル（移動焼入れ）", -10, -6, "end")
    s += heat(*cam.xy((xi + 18, 0, 20)), 2, 8)
    s += tol(40, 284, "硬化層深さ・曲がり")
    return s


def _s_grind():
    s = title("軸受部・端面をアンギュラ研削、ギヤ部を歯面研削")

    def fn(sc):
        CYL(sc, (-26, 0, 0), (1, 0, 0), 12, 20, "m", -1, seg=20, bands=6)
        CYL(sc, (-6, 0, 0), (1, 0, 0), 9, 6, "m", -1, seg=12, bands=4, r1=2)
        shaft3(sc, gq="fake")
        CYL(sc, (SH_L, 0, 0), (1, 0, 0), 2, 6, "m", -1, seg=12, bands=4, r1=9)
        CYL(sc, (SH_L + 6, 0, 0), (1, 0, 0), 12, 20, "m", -1, seg=20, bands=6)
        CYL(sc, (186, 58, 6), (1, 0, 0), 40, 34, "gw", 2, seg=40, bands=10)                # wheel behind the journal
    s1, cam = opfit(fn, 20, 26, (30, 40, 450, 262))
    s += s1 + sil(cam, (180, 0, 0), (226, 0, 0), 17) + rim(cam, (180, 0, 0), (-1, 0, 0), 17)
    s += arc3(cam, (220, 58, 6), (1, 0, 0), 44, 20, 80) + lbl(cam, (220, 58, 6), "研削砥石", 0, 70, "middle", "al")
    s += tol(40, 290, "軸受部径（数μm）・振れ。インプロセスゲージで定寸")
    return s


def _s_gun():
    s = title("軸心の油穴をガンドリルで加工し、形状を全数測定")

    def fn(sc):
        shaft3(sc, gq="fake")
        CYL(sc, (SH_L, 0, 0), (1, 0, 0), 1.6, 70, "t", -2, seg=10, bands=3)               # gun drill
        CYL(sc, (SH_L + 70, 0, 0), (1, 0, 0), 9, 20, "m", -2, seg=20, bands=6)
        for x in (50, 128):
            r = 18 if x == 50 else 20
            CYL(sc, (x, 0, r), (0, 0, 1), 1.6, 20, "t", -2, seg=10, bands=3)               # gauge probes
            BOX(sc, x - 6, -6, r + 20, 12, 12, 20, "dk", -2, ch=2)
    s1, cam = opfit(fn, 20, 20, (30, 46, 450, 262))
    s += s1 + path(P([cam.xy((0, 0, 0)), cam.xy((SH_L, 0, 0))], False), "mf")
    s += lbl(cam, (SH_L + 60, 0, 0), "ガンドリル", 0, 24, "middle", "al") + lbl(cam, (90, 0, 46), "測定", 0, -6, "middle", "sm")
    return s


@dpart("drivetrain.shaft", "ops")
def shaft_ops3():
    old = D.shaft_ops()
    return [fin(_s_forge()), fin(_s_turn()), old[2], old[3], fin(_s_ih()), fin(_s_grind()), fin(_s_gun())]


# =====================================================================================
# DRIVETRAIN.TMCASE — die-cast transaxle case of il3_drive.case_svg (axis +y, bell face at y=0
# toward the viewer; outline (u, v) -> world (-u, y, v)); bulkhead bosses/bores at y=60..70
# =====================================================================================
import il3_drive as DR
import re as _re
CASE_BB = ((-110, 0, -122), (110, 174, 108))
CASE_BORES = [((0, 14), 17), ((-28, 58), 11), ((-58, -70), 25)]     # (u, v) before x .74, bore radius


def case_world(u, v, y):
    return (-u, y, v)


def bore_c(i, y=60):
    (u, v), r = CASE_BORES[i]
    return (-u * .74, y, v * .74), r


def case_raw(sc, hot=False, bias=0):
    def f(s_):
        o = DR.case_svg(s_.cam)
        if hot:
            o = _re.sub(r'class="w(s\d)?"', lambda m: 'class="h%s"' % (m.group(1) or ""), o).replace('class="w3"', 'class="h"')
        return o
    RAW(sc, f, CASE_BB, bias)


def flange_pts(cam, y=-.1, off=8):
    return [cam.xy(case_world(u, v, y)) for u, v, f in DR._pear(1.0, off)]


@dpart("drivetrain.tmcase", "detail")
def tmcase_detail3():
    s, cam = opfit(lambda sc: case_raw(sc), 30, 24, (60, 34, 400, 270), sh_k=.45)
    notes = [("合わせ面（フランジ）", "エンジン・ケース同士の合わせ面。平面度とシール"), ("軸受穴", "シャフトを支える穴。位置度±0.02〜0.03mm"),
             ("ボルト穴", "締結用。位置と深さ"), ("リブ", "薄肉の剛性を補う（鋳造で成形）"), ("油路", "内部の潤滑油路。鋳巣が漏れにつながる")]
    pts = DR._pear(1.0, 1)
    u, v, _ = pts[int(3 * len(pts) / 14)]
    c, r = bore_c(0)
    s += balp(cam, case_world(104, 30, 0), 30, 60, 1) + balp(cam, _v(c, (1, 0, 0), r), 456, 150, 2) + balp(cam, case_world(u, v, 0), 60, 280, 3)
    s += balp(cam, (55, 40, 74), 330, 44, 4) + balp(cam, (10, 130, 82), 456, 70, 5)
    return s, notes


def _c_hpdc():
    s = title("大型の薄肉ケースを高圧ダイカストで鋳造")

    def fn(sc):
        BOX(sc, -230, -30, -150, 90, 220, 280, "m", dark=.5, ch=6)                        # fixed die
        BOX(sc, 140, -30, -150, 90, 220, 280, "m", dark=1, ch=6)                          # moving die
        case_raw(sc, hot=True)
        CYL(sc, (-290, 80, -100), (1, 0, 0), 22, 60, "m", -1, seg=24, bands=7)            # shot sleeve
    s1, cam = opfit(fn, 30, 20, (30, 36, 450, 258))
    s += s1 + arrow3(cam, (300, -30, 140), (240, -30, 140)) + lbl(cam, (270, -30, 140), "型締", 0, -8, "middle", "al")
    s += arrow3(cam, (-360, 80, -100), (-300, 80, -100)) + lbl(cam, (-330, 80, -100), "射出", 0, 18, "middle", "al")
    s += text(240, 290, "型締力2,500〜4,000t・真空ダイカスト", "middle")
    return s


GATES = [(-20, -138, 40, 16), (96, -40, 14, 30), (-118, 40, 14, 30)]           # (x, z, sx, sz) tabs on the flange


def _c_trim():
    s = title("湯口・バリを除き、ショットで表面を整える")

    def fn(sc):
        case_raw(sc)
        for x, z, sx, sz in GATES:
            BOX(sc, x, 0, z, sx, 10, sz, "w", -1, dark=1)
    s1, cam = opfit(fn, 30, 24, (40, 38, 380, 268))
    s += s1
    for x, z, sx, sz in GATES:
        if sx > sz:
            a, b = cam.xy((x, -.2, z + sz)), cam.xy((x + sx, -.2, z + sz))
        else:
            a, b = (cam.xy((x + sx, -.2, z)), cam.xy((x + sx, -.2, z + sz))) if x > 0 else (cam.xy((x, -.2, z)), cam.xy((x, -.2, z + sz)))
        s += line(a[0], a[1], b[0], b[1], "cutl")
    x, y = cam.xy((0, 5, -138))
    s += lead(x, y, 330, 280, "湯口・オーバーフロー") + tol(380, 60, "変形・バリ残り")
    return s


def _c_xray():
    s = title("加工面・シール面近傍の鋳巣をX線で確認")

    def fn(sc):
        case_raw(sc)
        BOX(sc, -260, 40, -40, 40, 60, 60, "m", ch=4)                                      # X-ray tube
        BOX(sc, 180, -40, -150, 10, 240, 280, "m", dark=1)                                 # detector panel
    s1, cam = opfit(fn, 30, 24, (30, 38, 450, 266))
    src = cam.xy((-220, 70, 10))
    rays = ""
    for k in range(7):
        q = cam.xy((180, -40 + 240 * k / 6, -150 + 280 * k / 6 if k % 2 else 110 - 260 * k / 6))
        rays += line(src[0], src[1], q[0], q[1], "ray")
    c, r = bore_c(2)
    p = cam.xy(_v(c, (0, 0, 1), r + 10))
    s = s + s1 + rays + circ(p[0], p[1], 3, "poro") + circ(p[0], p[1], 11, "mfring")
    s += lead(p[0] - 11, p[1], 40, 284, "鋳巣（軸受穴の近く）", "start") + lbl(cam, (-240, 70, 20), "X線", 0, -30, "middle", "al")
    return s


def _c_hmc():
    s = title("合わせ面・軸受穴・ボルト穴・油路を横形MCで加工")
    c0, r0 = bore_c(0)

    def fn(sc):
        case_raw(sc)
        CYL(sc, (-96, -12, 40), (0, -1, 0), 40, 12, "t", -2, seg=32, bands=8)             # face mill on the flange
        CYL(sc, (-96, -24, 40), (0, -1, 0), 24, 30, "m", -2, seg=24, bands=7)
        CYL(sc, (c0[0], 40, c0[2]), (0, -1, 0), 6, 120, "t", -3, seg=14, bands=4)          # boring bar into the main bore
        CYL(sc, (c0[0], -80, c0[2]), (0, -1, 0), 14, 30, "m", -3, seg=20, bands=6)
    s1, cam = opfit(fn, 30, 24, (40, 36, 440, 262))
    s += s1 + path(P(flange_pts(cam)), "mf")
    for i in (0, 1, 2):
        c, r = bore_c(i)
        s += rim(cam, c, (0, -1, 0), r, "mf", False)
    s += arc3(cam, (-96, -40, 40), (0, -1, 0), 30, 200, 300)
    s += tol(250, 288, "軸受穴の位置度 ±0.02〜0.03mm")
    return s


def _c_wash():
    s = title("高圧水でバリを取り、切粉・油を洗浄")

    def fn(sc):
        case_raw(sc)
        for x in (-70, 10, 90):
            CYL(sc, (x, 40, 170), (0, 0, -1), 4, 26, "t", -3, seg=12, bands=4)
            CYL(sc, (x, 40, 196), (0, 0, 1), 7, 10, "m", -3, seg=14, bands=4)
        CYL(sc, (-100, 40, 206), (1, 0, 0), 5, 200, "m", -3, seg=12, bands=4)
    s1, cam = opfit(fn, 30, 24, (60, 36, 420, 266))
    s += s1
    for x in (-70, 10, 90):
        a = cam.xy((x, 40, 170))
        s += drops(a[0], a[1], 4, 30, 34, 90)
    s += tol(40, 288, "清浄度（残留異物）を管理")
    return s


def _c_imp():
    s = title("微細な鋳巣に樹脂を真空含浸して漏れを止める")
    W0, W1, Y0, Y1, Z0, Z1, ZL = -150, 150, -60, 230, -150, 150, 120

    def fn(sc):
        BOX(sc, W0, Y1, Z0, W1 - W0, 10, Z1 - Z0, "m", 2, dark=1)
        BOX(sc, W0 - 10, Y0, Z0, 10, Y1 - Y0 + 10, Z1 - Z0, "m", 2, dark=1)
        BOX(sc, W0 - 10, Y0, Z0 - 10, W1 - W0 + 20, Y1 - Y0 + 10, 10, "m", 2)
        case_raw(sc)
        BOX(sc, W1, Y0, Z0, 10, Y1 - Y0 + 10, Z1 - Z0, "m", -3, dark=1)
    s1, cam = opfit(fn, 30, 24, (60, 36, 420, 266))
    s += s1
    fr = [cam.xy(p) for p in ((W0, Y0, Z0), (W1, Y0, Z0), (W1, Y0, ZL), (W0, Y0, ZL))]
    tp = [cam.xy(p) for p in ((W0, Y0, ZL), (W1, Y0, ZL), (W1, Y1, ZL), (W0, Y1, ZL))]
    s += path(P(fr), "fl") + path(P(tp), "fl")
    s += arrow(446, 100, 446, 50, None) + text(440, 120, "真空→加圧", "end", "al")
    s += lbl(cam, (0, Y0, Z0), "含浸液（樹脂）", 0, 20, "middle", "sm")
    return s


def _c_leak():
    s = title("油路をエアで加圧して漏れを確認し、三次元測定機で寸法を抜取")

    def fn(sc):
        case_raw(sc)
        sc.add(lambda s_: compact(GE.prism(s_.cam, (0, -12, 0), (0, 1, 0), [(-u, v, f) for u, v, f in DR._pear(1.0, 8)], 10, "m", smooth="outer")),
               ((-110, -12, -130), (110, -2, 116)), -2)
        BOX(sc, 150, 40, -150, 30, 30, 330, "pt", dark=1)                                   # CMM column
        BOX(sc, -60, 40, 160, 240, 30, 24, "pt", dark=1)                                   # bridge
        CYL(sc, (10, 55, 160), (0, 0, -1), 3, 40, "t", -1, seg=10, bands=3)                # probe
    s1, cam = opfit(fn, 30, 24, (40, 36, 430, 262))
    s += s1
    a = cam.xy((-60, -12, -60))
    s += path("M%s %s Q%s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] - 30), n(a[1] + 40), n(36), n(250)), "cable") + circ(36, 236, 13, "m") + line(36, 236, 42, 228, "o")
    s += text(36, 266, "リーク試験", "middle", "sm") + lbl(cam, (10, 55, 200), "三次元測定機", 0, -6, "middle", "sm")
    s += tol(250, 290, "リーク量・軸受穴の位置")
    return s


@dpart("drivetrain.tmcase", "ops")
def tmcase_ops3():
    return [fin(f()) for f in (_c_hpdc, _c_trim, _c_xray, _c_hmc, _c_wash, _c_imp, _c_leak)]
