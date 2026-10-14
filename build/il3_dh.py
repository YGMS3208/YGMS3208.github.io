"""v3 shaded-3D redraws of the detail ("部位と断面") and process drawings (480x300) for
wheel.alwheel, thermal.ecomp, common.bolt and common.bearing.
Titles, labels, tol() notes and the notes lists are carried over from il_d_ev.py; only the pictures change.
The wheel / bearing / bolt meshes reuse il3_trim's mesh helpers (imported lazily at draw time so the
il3_* registration order of the build is not disturbed)."""
import math
import re
import il_gear as GE
from il_base import *
from il_detail import *
from il_detail import P as P2
from il_dmap import dpart
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, arc3, arrow3
from il3_lib import P
import il_d_ev as V

PI = math.pi


def _T():
    import il3_trim
    return il3_trim


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _cyl(cam, O, A, r, h, mat="w", seg=24, bands=10, holes=(), r1=None, **kw):
    """free-standing smooth cylinder (or frustum to radius r1) (svg) outside the Scene ordering."""
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, bands), h, mat, holes=list(holes),
                            smooth="outer" if holes else True, scale=scale, **kw))


def _box(cam, x, y, z, sx, sy, sz, mat="m", **kw):
    loop = [(-yy, xx, i) for i, (xx, yy) in enumerate([(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)])]
    return compact(GE.prism(cam, (0, 0, z), (0, 0, 1), loop, sz, mat, **kw))


def ring3(cam, C, A, r, c="mf", seg=40, a0=0, a1=360):
    """3D circle (or arc, degrees in GE.frame(A)) as a stroke: machined-face edge, etc."""
    E1, E2, _ = GE.frame(A)
    full = abs(a1 - a0) >= 360
    k = seg if full else seg + 1
    pts = [cam.xy(tuple(C[i] + r * (math.cos(math.radians(a0 + (a1 - a0) * q / seg)) * E1[i] +
                                     math.sin(math.radians(a0 + (a1 - a0) * q / seg)) * E2[i]) for i in range(3))) for q in range(k)]
    return path(P(pts, full), c)


def seg3(cam, pts, c="mf", close=False):
    return path(P([cam.xy(p) for p in pts], close), c)


def stage(fn, az, el, area, **kw):
    s, sc = fit(fn, az, el, area, ret_scene=True, **kw)
    return s, sc.cam


def inset(x, y, w, h, lab="断面"):
    return rect(x, y, w, h, "m", 4) + text(x + w / 2, y + 16, lab, "middle", "sm")


# =====================================================================================
# wheel.alwheel — light version of il3_trim.alwheel (fewer segments) usable at any axis / place
# =====================================================================================
W_OUT = [(105, -52), (108.5, -50), (108.5, -46), (101, -43), (100, -32), (89, -25), (88, -10), (88, 12), (91, 17), (100, 23), (101, 41),
         (108.5, 45), (108.5, 49.5)]
W_IN = [(96, 53.5), (96, 26), (85, 18), (84, -18), (95, -28), (96, -48), (103, -52.5), (105, -52)]
W_LIP = [(108.5, 49.5), (106, 53), (101, 54.5), (96, 54.5)]
W_HUB = [(40, 49), (38.5, 57), (35, 61), (19, 61.5), (16.5, 63.5), (10, 67.5), (0, 68.4)]
W_SEC = [(0, -24), (20, -8), (34, -8), (34, -18), (20, -26), (20, -80), (80, -84), (80, -106), (70, -106), (70, -90), (8, -96), (8, -110), (0, -110)]


def wpt(C, A, r, a, t):
    """point at radius r, angle a (rad, GE.frame(A)), axial t on a wheel of centre C / axis A."""
    E1, E2, A_ = GE.frame(A)
    return tuple(C[i] + r * (math.cos(a) * E1[i] + math.sin(a) * E2[i]) + t * A_[i] for i in range(3))


def wheel3(cam, C=(0, 0, 0), A=(0, -1, 0), mat="w", seg=24, ns=5, sp=4, holes=True):
    T = _T()
    o = T.render(T.lathe(cam, C, A, W_OUT, mat, seg, dark=.35) + T.lathe(cam, C, A, W_IN, mat, seg, dark=2, lines=False))
    it = []
    for k in range(ns):
        a = 2 * PI * k / ns + PI / 2
        for sg in (-1, 1):
            it += T.mesh_items(cam, T.spoke_rows(C, A, a + sg * .075, sg * .19, 34, 97, 57, 50, 13, 10, 20, sp), mat, auto=True)
    o += T.render(it)
    o += T.render(T.lathe(cam, C, A, W_HUB, mat, max(16, seg - 4)))
    if holes:
        A_ = GE._norm(A)
        for k in range(ns):
            c = wpt(C, A, 24, 2 * PI * (k + .5) / ns + PI / 2, 61.6)
            o += hole3(cam, c, A_, 5.2, mat + "3" if mat == "w" else "dk") + hole3(cam, c, A_, 3.6, "bg")
        o += hole3(cam, wpt(C, A, 0, 0, 68.5), A_, 10, "bg")
    o += T.render(T.lathe(cam, C, A, W_LIP, mat, seg + 4))
    return o


def wheel_sec_hl(keys):
    return V.wheel_sec() + "".join(mf(V.WH_F[k]) for k in keys)


@dpart("wheel.alwheel", "detail")
def alwheel_detail3():
    notes = [("リム", "タイヤがはまる部分。振れ・エア漏れ"), ("スポーク（意匠面）", "塗装＋ダイヤモンドカット"), ("ハブ穴・PCD", "ハブへの取付穴とボルト穴の配置"),
             ("フランジ・ビードシート", "タイヤのビードが当たる部分")]
    s, cam = stage(lambda sc: wheel3(sc.cam, seg=32), 26, 12, (24, 22, 316, 282), sh_ry=8, sh_k=.42, sh_dy=-2)
    pl = Pl(350, 150, 1.0)
    s += inset(330, 30, 140, 240) + pl.g(V.wheel_sec())
    s += bal(*pl(40, -93), 300, 290, 1)
    s += bal(*cam.xy(wpt((0, 0, 0), (0, -1, 0), 70, PI / 2 + .3, 56)), 60, 40, 2)
    s += bal(*cam.xy(wpt((0, 0, 0), (0, -1, 0), 24, 2 * PI * 1.5 / 5 + PI / 2, 62)), 220, 286, 3)
    s += bal(*pl(4, -108), 300, 30, 4)
    return slim(s), notes


def _melt_box(cam, x, y, z, sx, sy, sz, wall=8, mat="dk"):
    """open-top furnace / crucible: box with a molten top surface inset by the wall."""
    o = _box(cam, x, y, z, sx, sy, sz, mat, dark=1)
    q = [(x + wall, y + wall, z + sz + .1), (x + sx - wall, y + wall, z + sz + .1), (x + sx - wall, y + sy - wall, z + sz + .1), (x + wall, y + sy - wall, z + sz + .1)]
    return o + seg3(cam, q, "hs1", True)


@dpart("wheel.alwheel", "ops")
def alwheel_ops3():
    ops = []
    Aw, Az = (0, -1, 0), (0, 0, 1)

    # 0 melting + rotary degassing ---------------------------------------------------------
    def f0(sc):
        cam = sc.cam
        o = _melt_box(cam, -200, -50, 0, 120, 100, 110, 10)                      # melting furnace
        o += heat(*cam.xy((-140, 0, 118)), 3, 14, 16)
        o += _cyl(cam, (0, 0, 0), Az, 62, 70, "dk", seg=32, dark=1)               # transfer ladle
        o += path(P(circ3(cam, (0, 0, 70.1), Az, 54, 32)), "hs1")
        p0, p1, p2 = cam.xy((-86, 0, 112)), cam.xy((-30, 0, 120)), cam.xy((-14, 0, 72))
        o += path("M%s %s Q%s %s %s %s" % (n(p0[0]), n(p0[1]), n(p1[0]), n(p1[1]), n(p2[0]), n(p2[1])), "pour")
        o += _cyl(cam, (22, 0, 160), (0, 0, -1), 4, 120, "t", seg=12)               # rotor shaft
        o += _cyl(cam, (22, 0, 44), (0, 0, -1), 11, 8, "t", seg=16)                  # rotor head
        o += _box(cam, 6, -14, 160, 32, 28, 26, "m", dark=1)                        # drive
        x, y = cam.xy((22, 0, 40))
        o += bubbles(x, y + 2, 9, 70, 52)
        return o
    s, cam = stage(f0, 20, 22, (30, 52, 340, 270))
    x, y = cam.xy((22, 14, 186))
    s += title("アルミを溶かして脱ガスし、保持炉へ") + text(x + 30, y - 4, "回転脱ガス", "start", "al") + tol(352, 150, "水素量・介在物")
    ops.append(s)

    # 1 low-pressure die casting: die cut open on its mid plane, hot wheel section in the cavity ----------
    def f1(sc):
        cam = sc.cam
        o = _box(cam, -160, -60, -90, 320, 120, 62, "dk", dark=1)                  # holding furnace
        o += _cyl(cam, (0, 0, -40), Az, 9, 76, "h", seg=16)                        # stem
        o += _box(cam, -140, 0, 30, 280, 60, 34, "m", dark=1)                      # lower die (back half)
        o += _box(cam, -150, 0, 64, 40, 60, 112, "m", dark=1) + _box(cam, 110, 0, 64, 40, 60, 112, "m", dark=1)   # side dies
        o += _box(cam, -110, 0, 156, 220, 60, 36, "m", dark=1)                     # upper die
        o += _box(cam, -12, 0, 192, 24, 60, 40, "m", dark=2)                       # ram
        # cut face (y = 0): die section + cavity filled with melt
        o += seg3(cam, [(-150, -.2, 30), (150, -.2, 30), (150, -.2, 192), (-150, -.2, 192)], "cut", True)
        for sg in (-1, 1):
            o += seg3(cam, [(sg * -q[1] * 1.2, -.4, 64 + q[0] * 1.1) for q in W_SEC], "h", True)
        o += seg3(cam, [(-9, -.4, 34), (9, -.4, 34), (9, -.4, 92), (-9, -.4, 92)], "h", True)
        o += seg3(cam, [(-140, -60.2, -80), (140, -60.2, -80), (140, -60.2, -50), (-140, -60.2, -50)], "h", True)   # melt seen through a cut window
        return o
    s, cam = stage(f1, 0, 12, (150, 40, 440, 288), sh=False)
    a, b = cam.xy((-24, -70, -10)), cam.xy((-24, -70, 50))
    c = cam.xy((-160, -60, -40))
    s += title("下から静かに溶湯を押し上げて金型に充填（低圧鋳造）") + arrow(a[0], a[1], b[0], b[1], None)
    s += text(c[0] - 6, c[1] - 40, "空気圧で押し上げ", "end", "al")
    ops.append(s)

    # 2 X-ray inspection -------------------------------------------------------------------
    def f2(sc):
        cam = sc.cam
        o = _box(cam, -230, -30, -20, 40, 50, 44, "dk", dark=1)                    # X-ray tube
        o += _box(cam, 170, -100, -110, 14, 200, 220, "m", dark=1)                 # detector panel
        o += wheel3(cam, seg=22, sp=3)
        return o
    s, cam = stage(f2, 26, 12, (20, 40, 460, 284))
    src = cam.xy((-190, 0, 2))
    for tz in (-100, 100):
        q = cam.xy((170, 0, tz))
        s += line(src[0], src[1], q[0], q[1], "beam")
    x, y = cam.xy(wpt((0, 0, 0), Aw, 40, PI / 2 + .1, 56))
    s += circ(x, y, 3, "poro") + circ(x, y, 12, "mfring") + title("全数を自動X線検査（スポーク根元の引け巣）")
    ops.append(s)

    # 3 T6: solution heat treatment, water quench, ageing --------------------------------------
    def f3(sc):
        cam = sc.cam
        o = _box(cam, -150, 20, 0, 190, 130, 150, "dk", dark=1)                    # furnace (front open)
        q = [(-138, 19.8, 12), (28, 19.8, 12), (28, 19.8, 138), (-138, 19.8, 138)]
        o += seg3(cam, q, "hotin", True)
        o += _box(cam, 90, 0, 0, 150, 130, 90, "m", dark=1)                        # quench tank
        o += seg3(cam, [(98, 8, 80), (232, 8, 80), (232, 122, 80), (98, 122, 80)], "fl", True)
        return o
    s, cam = stage(f3, 0, 18, (24, 46, 456, 260))
    # wheels in the furnace (drawn small with a separate camera, on the hot interior)
    x, y = cam.xy((-58, 20, 72))
    s += '<g transform="translate(%s %s) scale(%s)">%s</g>' % (n(x), n(y), n(cam.s * .5), _wheel_tile())
    a, b = cam.xy((10, 0, 160)), cam.xy((150, 0, 120))
    s += arrow(a[0], a[1], b[0], b[1], None)
    l1, l2 = cam.xy((-55, 150, 150)), cam.xy((165, 0, 100))
    s += text(l1[0], l1[1] - 6, "溶体化", "middle", "al") + text(l2[0], l2[1] + 30, "水冷", "middle", "al")
    s += text(240, 290, "→ 時効（低温で保持）", "middle", "al")
    s += title("溶体化・水冷・時効（T6）で強度を出す")
    ops.append(s)

    # 4 vertical lathe, two set-ups -----------------------------------------------------------
    s = title("立形旋盤で表・裏の2工程に分けて旋削") + _vl_turn("rim")
    pl = Pl(372, 156, .78)
    s += inset(340, 44, 130, 220) + pl.g(wheel_sec_hl(["rim", "face"])) + tol(346, 280, "リム形状・振れ")
    ops.append(s)

    # 5 hub bore, PCD holes, valve hole ----------------------------------------------------------
    s = title("ハブ穴・ボルト穴（PCD）・バルブ穴を加工") + _vl_turn("pcd")
    pl = Pl(372, 156, .78)
    s += inset(340, 44, 130, 220) + pl.g(wheel_sec_hl(["hub", "pcd"]))
    ops.append(s)

    # 6 helium leak test ----------------------------------------------------------------------
    def f6(sc):
        cam = sc.cam
        x0, x1, y0, y1, z0, z1 = -150, 150, -90, 90, -125, 135
        o = seg3(cam, [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], "glp", True)
        o += _box(cam, x0, y0, z0 - 12, x1 - x0, y1 - y0, 12, "m", dark=1)        # base plate
        o += wheel3(cam, seg=22, sp=3)
        fr = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]
        o += seg3(cam, fr, "o", True) + seg3(cam, [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], "o")
        o += seg3(cam, [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], "o")
        return o
    s, cam = stage(f6, 26, 12, (40, 40, 400, 286))
    q = cam.xy((150, 0, 40))
    s += dots(60, 46, 330, 24, 14, "he") + _box(cam, 150, -20, 20, 40, 40, 40, "dk", dark=1) + text(q[0] + 40, q[1] - 30, "He検出", "middle", "al")
    s += title("チャンバ内でヘリウムを使い、リムの漏れを確認")
    ops.append(s)

    # 7 paint, then diamond-cut the design face ----------------------------------------------------
    s = title("塗装し、意匠面をダイヤモンドバイトで削り出して光らせる") + _vl_turn("face")
    ops.append(s)

    # 8 run-out / appearance, sampled bending & impact tests ----------------------------------------
    def f8(sc):
        cam = sc.cam
        o = _cyl(cam, (0, 140, 0), (0, -1, 0), 26, 72, "m", seg=24)                 # test spindle
        o += wheel3(cam, seg=22, sp=3)
        o += _box(cam, 128, -20, -15, 50, 30, 30, "dk", dark=1)                     # dial gauge body
        o += _cyl(cam, (128, -5, 0), (-1, 0, 0), 2, 19, "t", seg=8)                 # stylus to the rim
        return o
    s, cam = stage(f8, 26, 12, (30, 40, 320, 286))
    s += arc3(cam, (0, 70, 0), (0, -1, 0), 130, 200, 290)
    x, y = cam.xy((153, -5, 30))
    s += text(x, y, "振れ", "middle", "al") + chart(330, 190, 140, 80, "sine")
    s += title("振れ・外観を確認し、抜取で回転曲げ・衝撃試験")
    ops.append(s)
    return [slim(fin(x)) for x in ops]


_TILE = {}


def _wheel_tile():
    """a small stand-alone wheel (face forward) at the origin, for repeated placement."""
    if "w" not in _TILE:
        cam = GE.Cam(0, 0, 26, 12, 1.0)
        _TILE["w"] = wheel3(cam, seg=16, sp=2, holes=False)
    return _TILE["w"]


def _vl_turn(what):
    """wheel lying face-up on a vertical-lathe chuck; what = rim (turning) / pcd (drilling) / face (diamond cut)."""
    Az = (0, 0, 1)
    C = (0, 0, 92)

    def fn(sc):
        cam = sc.cam
        o = _cyl(cam, (0, 0, 0), Az, 150, 34, "m", seg=48, dark=1)                  # chuck table
        jaws = []
        for k in range(3):
            a = 2 * PI * k / 3 + PI / 6
            cx, cy = 122 * math.cos(a), 122 * math.sin(a)
            ca, sa = math.cos(a), math.sin(a)
            q = [(u * ca - v * sa, u * sa + v * ca) for u, v in ((-12, -10), (12, -10), (12, 10), (-12, 10))]
            j = compact(GE.prism(cam, (cx, cy, 34), Az, [(-y_, x_, i) for i, (x_, y_) in enumerate(q)], 26, "dk"))
            jaws.append((cam.P((cx, cy, 40))[2], j))
        jaws.sort(key=lambda t: -t[0])
        d0 = cam.P(C)[2]
        o += "".join(j for d, j in jaws if d > d0)
        o += wheel3(cam, C, Az, "w", 24, sp=3)
        o += "".join(j for d, j in jaws if d <= d0)
        if what == "rim":
            o += ring3(cam, (0, 0, C[2] + 47), Az, 108.5, "mf", 30, -100, 100) + ring3(cam, (0, 0, C[2] + 30), Az, 100.5, "mf", 30, -100, 100)
            tp = (-112, 0, C[2] + 36)
            o += _box(cam, -200, -8, C[2] + 30, 86, 16, 12, "t") + _box(cam, -200, -22, C[2] + 42, 30, 44, 130, "m", dark=1)
        elif what == "pcd":
            for k in range(5):
                c = wpt(C, Az, 24, 2 * PI * (k + .5) / 5 + PI / 2, 61.7)
                o += hole3(cam, c, Az, 3.8, "mfa")
            o += ring3(cam, (0, 0, C[2] + 68.6), Az, 10, "mf", 24)
            c = wpt(C, Az, 24, 2 * PI * 2.5 / 5 + PI / 2, 62)
            o += _cyl(cam, _add(c, Az, 4), Az, 3.6, 60, "t", seg=10) + _cyl(cam, _add(c, Az, 64), Az, 12, 50, "m", seg=20, dark=1)
        else:
            for r in (60, 90):
                o += ring3(cam, (0, 0, C[2] + 57), Az, r, "mf", 40, 120, 300)
            o += _box(cam, -10, -86, C[2] + 58, 12, 12, 10, "t") + _box(cam, -12, -88, C[2] + 68, 16, 16, 120, "m", dark=1)
        return o
    s, cam = stage(fn, -24, 34, (24, 40, 330, 290))
    s += arc3(cam, (0, 0, 20), Az, 175, 200, 300)
    if what == "rim":
        a, b = cam.xy((-150, 0, C[2] + 100)), cam.xy((-150, 0, C[2] + 40))
        s += arrow(a[0] - 26, a[1], b[0] - 26, b[1], None) + text(a[0] - 30, a[1] - 6, "送り", "middle", "al")
    elif what == "pcd":
        c = wpt(C, Az, 24, 2 * PI * 2.5 / 5 + PI / 2, 62)
        a, b = cam.xy(_add(c, Az, 120)), cam.xy(_add(c, Az, 80))
        s += arrow(a[0] + 22, a[1], b[0] + 22, b[1], None)
    else:
        a = cam.xy((-4, -80, C[2] + 188))
        s += spray_cone(352, 76, 150, 30, 56) + rect(352, 64, 44, 20, "m3", 3) + text(374, 100, "塗装", "middle", "al")
        s += text(a[0], a[1] - 6, "ダイヤモンドバイト", "middle", "al")
    return s


# ------------------------------------------------------------------ byte diet for the path data
_D = re.compile(r' d="([^"]*)"')
_NUM = re.compile(r'-?\d+\.\d+')


def slim(s, nd=0):
    """implicit line-tos (drop 'L') and coarser numbers inside d="..." only."""
    def num(m):
        v = round(float(m.group(0)), nd)
        return n(v) if nd else str(int(v))

    def fd(m):
        d = _NUM.sub(num, m.group(1))
        d = re.sub(r' ?L', ' ', d)
        return ' d="%s"' % d
    return _D.sub(fd, s)


# =====================================================================================
# common.bearing — deep-groove ball bearing (after il3_trim.bearing), any axis, optional parts
# =====================================================================================
B_R, B_RO, B_RI, B_RIN, B_H, B_RP, B_RB = 100, 84, 56, 40, 36, 70, 13.4
B_RA = [(85.5, B_H), (B_RO, B_H - 1.5), (B_RO, 27), (B_RO + 1.3, 24), (B_RO + 2, 18), (B_RO + 1.3, 12), (B_RO, 9), (B_RO, 1.5), (85.5, 0)]
B_RB_ = [(85.5, 0), (B_R - 1.5, 0), (B_R, 1.5, 1), (B_R, B_H - 1.5, 2), (B_R - 1.5, B_H, 3), (85.5, B_H)]
B_IN = [(B_RIN + 1.5, 0), (B_RI - 1.5, 0), (B_RI, 1.5, 1), (B_RI, 9, 1), (B_RI - 1.3, 12, 2), (B_RI - 2, 18, 3), (B_RI - 1.3, 24, 4), (B_RI, 27, 5),
        (B_RI, B_H - 1.5, 5), (B_RI - 1.5, B_H, 6), (B_RIN + 1.5, B_H, 7), (B_RIN, B_H - 1.5, 8), (B_RIN, 1.5, 9), (B_RIN + 1.5, 0)]


def bearing3(cam, C=(0, 0, 0), A=(0, 0, 1), seg=32, outer=True, inner=True, balls=True, cage=True, mat="w", nb=9, seal=False):
    """C = centre of the bottom face, A = axis. Returns svg (painter-ordered by hand)."""
    T = _T()
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    zc = B_H / 2
    o = ""
    if outer:
        o += T.render(T.lathe(cam, C, A, B_RA, mat, seg, dark=.6))
    if outer and inner:
        o += path(P(circ3(cam, _add(C, A, 2), A, B_RP, seg)), "bg")
    small = []
    d0 = cam.P(_add(C, A, zc))[2]
    for k in range(nb if balls else 0):
        a = 2 * PI * k / nb
        c = wpt(C, A, B_RP, a, zc)
        x, y, d = cam.P(c)
        small.append((d, ell(x, y, B_RB * cam.s, B_RB * cam.s, "ball"), d > d0))
        if cage:
            a2, da = a + PI / nb, .55 * PI / nb
            sect = [((B_RP + q) * math.cos(a2 + sg * da), (B_RP + q) * math.sin(a2 + sg * da), i)
                    for i, (q, sg) in enumerate(((-7, -1), (7, -1), (7, 1), (-7, 1)))]
            cb = wpt(C, A, B_RP, a2, zc)
            small.append((cam.P(cb)[2], compact(GE.prism(cam, _add(C, A, zc - 5), A, sect, 10, "gw")) +
                          hole3(cam, _add(cb, A, 5.1), A, 2.4, "gw"), cam.P(cb)[2] > d0))
    small.sort(key=lambda t: -t[0])
    o += "".join(s_ for _, s_, far in small if far)
    if inner:
        o += T.render(T.lathe(cam, C, A, B_IN, mat, seg))
    o += "".join(s_ for _, s_, far in small if not far)
    if outer:
        o += T.render(T.lathe(cam, C, A, B_RB_, mat, seg + 8))
    if seal:
        o += compact(GE.prism(cam, _add(C, A, B_H - 2.5), A, GE.circle_outline(B_RO + 1, seg, 8), 2, "dk",
                              holes=[GE.circle_outline(B_RI - 1, seg, seg)], smooth="outer"))
    return o


@dpart("common.bearing", "detail")
def bearing_detail3():
    notes = [("外輪", "軌道面を研削・超仕上げ"), ("内輪", "軸にはまる。内径公差数μm"), ("鋼球", "真球度0.1μm級の等級品"), ("シール・グリース", "ゴムシールでグリースを封入")]
    s, cam = stage(lambda sc: bearing3(sc.cam, seg=40), -28, 34, (24, 40, 316, 270), sh_ry=8, sh_k=.5, sh_dy=-5)
    pl = Pl(380, 150, 1.8)
    s += inset(330, 30, 140, 240) + pl.g(V.bearing_sec())
    s += bal(*cam.xy(wpt((0, 0, 0), (0, 0, 1), 100, PI * 1.15, 22)), 40, 280, 1)
    s += bal(*cam.xy(wpt((0, 0, 0), (0, 0, 1), 48, PI * .85, 36)), 180, 40, 2)
    s += bal(*cam.xy(wpt((0, 0, 0), (0, 0, 1), B_RP, 0, 18)), 60, 40, 3)
    s += bal(*pl(0, -41), 350, 90, 4)
    return slim(s), notes


def _rings_row(cam, xs, y, z, hot_upto, s_=0.42):
    """bearing rings (outer-ring blanks) standing on a belt, hot ones inside the furnace."""
    o = ""
    for x in sorted(xs, key=lambda x: -cam.P((x, y, z))[2]):
        m = "h" if x < hot_upto else "w"
        o += compact(GE.prism(cam, (x, y, z), (0, 0, 1), GE.circle_outline(B_R * s_, 24, 8), B_H * s_, m,
                              holes=[GE.circle_outline(B_RO * s_, 24, 24)], smooth="outer"))
    return o


@dpart("common.bearing", "ops")
def bearing_ops3():
    ops = []
    Az = (0, 0, 1)

    # 0 ring blank (hot forged / ring rolled) -> turning on a chuck --------------------------------
    def f0(sc):
        cam = sc.cam
        o = _cyl(cam, (-260, 0, 0), Az, B_R * .9, B_H * 1.2, "h", seg=28, holes=[GE.circle_outline(B_RO * .8, 28, 28)])
        o += _cyl(cam, (0, 0, -60), Az, 140, 60, "m", seg=48, dark=1)
        o += bearing3(cam, (0, 0, 0), Az, 36, inner=False, balls=False)
        o += ring3(cam, (0, 0, B_H), Az, B_R - 1.5, "mf", 30, -100, 100) + ring3(cam, (0, 0, B_H), Az, 86, "mf", 30, -100, 100)
        for k in range(3):
            a = 2 * PI * k / 3 + PI / 3
            c = (118 * math.cos(a), 118 * math.sin(a), 0)
            o += _box(cam, c[0] - 9, c[1] - 9, 0, 18, 18, 22, "dk") if cam.P(c)[2] > 0 else ""
        o += _box(cam, 60, -18, B_H + 2, 120, 16, 14, "t") + _box(cam, 150, -30, B_H + 16, 40, 40, 90, "m", dark=1)
        for k in range(3):
            a = 2 * PI * k / 3 + PI / 3
            c = (118 * math.cos(a), 118 * math.sin(a), 0)
            o += _box(cam, c[0] - 9, c[1] - 9, 0, 18, 18, 22, "dk") if cam.P(c)[2] <= 0 else ""
        return o
    s, cam = stage(f0, -20, 32, (20, 50, 460, 280))
    a, b = cam.xy((-150, 0, 20)), cam.xy((-115, 0, 20))
    s += arrow(a[0], a[1], b[0] + 10, b[1], None) + arc3(cam, (0, 0, -60), Az, 160, 200, 300)
    q = cam.xy((-260, 100, 60))
    s += text(q[0], q[1] - 8, "リングローリング", "middle", "al")
    s += title("熱間鍛造・リングローリングで素材をつくり、旋削")
    ops.append(s)

    # 1 through hardening + tempering on a mesh-belt furnace ------------------------------------
    def f1(sc):
        cam = sc.cam
        o = _box(cam, -260, -60, -14, 560, 120, 10, "m", dark=1)                     # belt
        o += _box(cam, -150, -70, -40, 300, 150, 150, "dk", dark=1)                 # furnace (front cut)
        o += seg3(cam, [(-140, -70.2, 0), (140, -70.2, 0), (140, -70.2, 96), (-140, -70.2, 96)], "hotin", True)
        o += _rings_row(cam, [-230, -170, -100, -30, 40, 110, 190, 250], -10, -4, 150)
        return o
    s, cam = stage(f1, -12, 22, (16, 56, 464, 270))
    s += title("ずぶ焼入れ・焼戻し")
    ops.append(s)

    # 2 double-disc grinding of both faces (then centreless OD, raceway / bore) -------------------
    Ax = (1, 0, 0)

    def f2(sc):
        cam = sc.cam
        o = _cyl(cam, (B_H + 40, 0, 0), Ax, 130, 50, "gw", seg=48)                  # right wheel (behind)
        o += _cyl(cam, (B_H + 90, 0, 0), Ax, 40, 60, "m", seg=24)
        o += bearing3(cam, (0, 0, 0), Ax, 36, inner=False, balls=False)
        o += ring3(cam, (B_H, 0, 0), Ax, B_R - 1, "mf", 36, 0, 360) + ring3(cam, (0, 0, 0), Ax, B_R - 1, "mf", 36, 20, 160)
        o += _cyl(cam, (-40, 0, 0), (-1, 0, 0), 130, 50, "gw", seg=48)              # left wheel (front)
        o += _cyl(cam, (-90, 0, 0), (-1, 0, 0), 40, 60, "m", seg=24)
        return o
    s, cam = stage(f2, 14, 22, (40, 40, 440, 262))
    for x0, x1 in ((-120, -50), (B_H + 120, B_H + 50)):
        a, b = cam.xy((x0, 0, 150)), cam.xy((x1, 0, 150))
        s += arrow(a[0], a[1], b[0], b[1], None)
    s += text(240, 282, "両頭平面研削（幅面）", "middle") + tol(24, 292, "寸法・真円度")
    s += title("幅面（両頭）→外径（センタレス）→軌道・内径を研削")
    ops.append(s)

    # 3 superfinishing the raceway ---------------------------------------------------------
    def f3(sc):
        cam = sc.cam
        o = _cyl(cam, (-40, 0, 0), Ax, B_RIN - 1, 110, "m", seg=24)                 # arbor
        o += bearing3(cam, (0, 0, 0), Ax, 36, outer=False, balls=False)
        o += ring3(cam, (18, 0, 0), Ax, B_RI - 2, "mf", 30, 200, 340)
        o += _box(cam, 8, -9, B_RI - 6, 20, 18, 20, "gw") + _box(cam, 12, -6, B_RI + 14, 12, 12, 70, "m", dark=1)
        return o
    s, cam = stage(f3, 30, 18, (60, 70, 420, 280))
    a, b = cam.xy((-30, 0, B_RI + 60)), cam.xy((66, 0, B_RI + 60))
    s += arrow(a[0], a[1], b[0], b[1], None, both=True) + text(b[0] + 8, b[1] + 4, "揺動", "start", "al")
    s += arc3(cam, (110, 0, 0), Ax, 70, 100, 200)
    s += title("軌道面を超仕上げ")
    ops.append(s)

    # 4 steel balls: heading -> flashing -> heat treat -> grind -> lap (between grooved plates) ------
    def f4(sc):
        cam = sc.cam
        o = _cyl(cam, (0, 0, -40), Az, 170, 40, "m", seg=48, dark=1)
        o += path(P(circ3(cam, (0, 0, .2), Az, 120, 48)), "bg")
        bl = []
        for k in range(14):
            a = 2 * PI * k / 14
            x, y, d = cam.P((120 * math.cos(a), 120 * math.sin(a), 9))
            bl.append((d, ell(x, y, 11 * cam.s, 11 * cam.s, "ball")))
        o += "".join(b for d, b in sorted(bl, key=lambda t: -t[0]))
        o += _cyl(cam, (0, 0, 70), Az, 170, 36, "m", seg=48, dark=1)               # upper plate (lifted)
        return o
    s, cam = stage(f4, -20, 26, (60, 40, 420, 262))
    s += arc3(cam, (0, 0, -40), Az, 200, 200, 300)
    s += tol(40, 284, "真球度・等級（径のばらつき）")
    s += title("鋼球：冷間圧造→フラッシング→熱処理→研削→ラッピング")
    ops.append(s)

    # 5 assembly: rings + balls + cage, then grease and seals -----------------------------------
    def f5(sc):
        cam = sc.cam
        o = bearing3(cam, (0, 0, 0), Az, 36)
        o += _cyl(cam, (-150, -10, 110), (1, .07, -.75), 6, 70, "t", seg=12) + _cyl(cam, (-200, -14, 150), (1, .07, -.75), 14, 60, "m", seg=16)
        o += compact(GE.prism(cam, (180, 0, 70), Az, GE.circle_outline(B_RO + 1, 32, 8), 3, "dk",
                              holes=[GE.circle_outline(B_RI - 1, 32, 32)], smooth="outer"))
        return o
    s, cam = stage(f5, -28, 34, (30, 46, 450, 270))
    q = cam.xy((-96, -6, 70))
    s += text(q[0] - 10, q[1] + 4, "グリース", "end", "al")
    q = cam.xy((180, -100, 70))
    s += text(q[0], q[1] + 22, "シール", "middle", "al")
    s += title("内外輪・鋼球・保持器を組み、グリースとシールを入れる")
    ops.append(s)

    # 6 rotate and measure vibration (Anderon) ----------------------------------------------------
    def f6(sc):
        cam = sc.cam
        o = _cyl(cam, (-120, 0, 0), Ax, 60, 80, "m", seg=24, dark=1)                 # spindle head
        o += _cyl(cam, (-40, 0, 0), Ax, B_RIN - 1, 50, "m", seg=24)
        o += bearing3(cam, (0, 0, 0), Ax, 28, seal=True)
        o += _cyl(cam, (18, 0, B_R + 40), (0, 0, -1), 3, 40, "t", seg=10) + _box(cam, 6, -12, B_R + 40, 24, 24, 50, "dk", dark=1)
        return o
    s, cam = stage(f6, 30, 16, (20, 50, 310, 280))
    s += arc3(cam, (60, 0, 0), Ax, 120, 100, 200) + chart(330, 60, 140, 80, "noise")
    s += title("回して振動・音を測り、異音品を除く（アンデロン値）")
    ops.append(s)
    return [slim(fin(x)) for x in ops]


# =====================================================================================
# common.bolt — hex flange bolt (after il3_trim.bolt) along any axis, scalable, with forming stages
# =====================================================================================
def bolt3(cam, C=(0, 0, 0), A=(1, 0, 0), k=1.0, stage=5, mat="w", seg=28, fine=True, thread_cls="el"):
    """head face at C, shank along +A. stage 0 = sheared wire, 1 = upset, 2 = round head + flange, 3+ = hex flange bolt;
    thread rolled when stage >= 3 (and k * seg big enough to show it, fine=True)."""
    T = _T()
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    L0, p_, nt = 49, 4.2, 21
    Lend = L0 + nt * p_ + 3.8
    if stage == 0:
        return T.render(T.lathe(cam, C, A, [(0, 0), (9.4 * k, 0), (9.4 * k, (Lend + 15) * k), (0, (Lend + 15) * k)], mat, seg))
    o = ""
    if stage == 1:
        o += T.render(T.lathe(cam, C, A, [(0, -14 * k), (13 * k, -14 * k), (13 * k, 0), (9.4 * k, 0)], mat, seg))
    elif stage == 2:
        o += T.render(T.lathe(cam, C, A, [(0, -15 * k), (12 * k, -15 * k), (15.5 * k, -12 * k), (15.5 * k, 0), (20.5 * k, 1.2 * k), (20.5 * k, 4 * k), (19 * k, 5.5 * k)], mat, seg))
    else:
        o += T.render(T.lathe(cam, C, A, [(15 * k, -.5 * k), (20.5 * k, 1.2 * k), (20.5 * k, 4 * k), (19 * k, 5.5 * k)], mat, seg + 8))
        hexo = [(15.5 * k * math.cos(PI / 6 + q * PI / 3), 15.5 * k * math.sin(PI / 6 + q * PI / 3), q) for q in range(6)]
        o += compact(GE.prism(cam, C, (-A[0], -A[1], -A[2]), hexo, 15 * k, mat, slices=3,
                              scale=lambda t: 1.0 if t < .67 else 1 - .2 * (t - .67) / .33, cap_mat=mat if mat == "w" else None))
        if fine:
            o += hole3(cam, _add(C, A, -15.1 * k), A, 11.5 * k, "w2" if mat == "w" else mat + "s2")
    if stage < 3 or not fine:
        o += T.render(T.lathe(cam, C, A, [(9.4 * k, 5.5 * k if stage >= 2 else 0), (9.4 * k, (Lend - 3) * k), (6.6 * k, Lend * k), (0, Lend * k)], mat, seg))
        if stage >= 3:
            o += T.render(T.lathe(cam, C, A, [(9.6 * k, L0 * k), (9.6 * k, (Lend - 4) * k)], mat, seg, dark=1, lines=False))
        return o
    o += T.render(T.lathe(cam, C, A, [(9.4 * k, 5.5 * k), (9.4 * k, 46 * k), (9 * k, 49 * k)], mat, seg))
    prof = []
    for q in range(nt):
        x = L0 + q * p_
        prof += [(9.6 * k, x * k, 0), (8.1 * k, (x + .5 * p_) * k, 1)]
    x = L0 + nt * p_
    prof += [(9.4 * k, x * k, 2), (7.6 * k, (x + 3.4) * k, 3), (6.2 * k, (x + 3.8) * k)]
    o += T.render(T.lathe(cam, C, A, prof, mat, max(16, seg - 8), lines=False))
    D = cam.D
    # silhouette directions: the two radial unit vectors normal to both A and the view
    sv = GE._norm(GE._cross(A, D))
    for sg in (1, -1):
        o += path(P([cam.xy(_add(_add(C, A, t), sv, sg * r)) for r, t, *_ in [(9 * k, 49 * k)] + prof], False), thread_cls)
    o += path(P(circ3(cam, _add(C, A, prof[-1][1]), A, 6.2 * k, 20)), "el")
    return o


def bolt_tile(stage=5, mat="w"):
    """a small bolt lying along +x (az 24, el 20) at the origin, cached; place with translate/scale."""
    key = ("b", stage, mat)
    if key not in _TILE:
        cam = GE.Cam(0, 0, 24, 20, 1.0)
        _TILE[key] = bolt3(cam, (-70, 0, 0), (1, 0, 0), 1.0, stage, mat, seg=12, fine=False)
    return _TILE[key]


def tile(svg_, x, y, s_):
    return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (n(x), n(y), n(s_), svg_)


@dpart("common.bolt", "detail")
def bolt_detail3():
    notes = [("頭部（六角・フランジ）", "冷間圧造で成形"), ("首下R", "応力集中を避ける丸み"), ("転造ねじ", "繊維状組織が切れず強い"), ("表面処理", "亜鉛フレークで防錆・摩擦係数を管理")]
    Ax = (1, 0, 0)
    s, cam = stage(lambda sc: bolt3(sc.cam, seg=32), 24, 20, (30, 70, 450, 250), sh_ry=7, sh_k=.42, sh_dy=-3)
    s += bal(*cam.xy((-8, 0, 15.5)), 60, 40, 1)
    s += bal(*cam.xy((7, 0, 10)), 160, 40, 2)
    s += bal(*cam.xy((110, 0, 9.6)), 360, 60, 3)
    s += bal(*cam.xy((30, -9, 0)), 260, 270, 4)
    return slim(s), notes


@dpart("common.bolt", "ops")
def bolt_ops3():
    ops = []
    Az, Ax = (0, 0, 1), (1, 0, 0)

    # 0 spheroidise-anneal coils, then draw the wire through a die ------------------------------
    def coil(cam, x, y, z):
        o = _cyl(cam, (x, y, z), Az, 70, 60, "w", seg=32, holes=[GE.circle_outline(40, 32, 32)])
        return o

    def f0(sc):
        cam = sc.cam
        o = _box(cam, -330, -10, -30, 340, 170, 200, "dk", dark=1)
        o += seg3(cam, [(-320, -10.2, -20), (0, -10.2, -20), (0, -10.2, 160), (-320, -10.2, 160)], "hotin", True)
        o += coil(cam, -235, 70, -20) + coil(cam, -85, 70, -20)
        o += _cyl(cam, (60, 60, 20), Ax, 13, 130, "w", seg=16)                         # wire in
        o += _box(cam, 190, 30, -20, 34, 60, 80, "t")                                   # drawing die
        o += _cyl(cam, (224, 60, 20), Ax, 9, 120, "w", seg=16)                          # wire out
        return o
    s, cam = stage(f0, 10, 18, (20, 56, 460, 262))
    q = cam.xy((207, 30, -30))
    s += text(q[0], q[1] + 22, "伸線ダイス", "middle")
    a, b = cam.xy((110, 40, 50)), cam.xy((170, 40, 50))
    s += arrow(a[0], a[1], b[0], b[1], None)
    s += title("線材を球状化焼鈍して柔らかくし、伸線で径を整える")
    ops.append(s)

    # 1 parts former: multi-stage cold heading -------------------------------------------------------
    def f1(sc):
        cam = sc.cam
        o = _box(cam, -60, 0, -120, 520, 80, 120, "m", dark=1)                         # die block
        for i in range(4):
            x = 20 + i * 120
            o += path(P(circ3(cam, (x, 0 - .2, -60), (0, -1, 0), 24, 24)), "ms3")
            o += bolt3(cam, (x, -40, 0), (0, 0, -1), 1.3, i, "w", 20, fine=False) if i < 3 else \
                bolt3(cam, (x, -40, 0), (0, 0, -1), 1.3, 3, "w", 20, fine=False)
        return o
    s, cam = stage(f1, -10, 14, (30, 44, 450, 236), sh=False)
    s += arrow(40, 262, 440, 262, "毎分100個以上", 240, 284)
    s += title("パーツフォーマで頭部とフランジを多段に冷間圧造")
    ops.append(s)

    # 2 thread rolling between flat dies ------------------------------------------------------------
    def f2(sc):
        cam = sc.cam
        o = _box(cam, 44, -80, -42, 100, 160, 20, "t", dark=1)                        # lower die (fixed)
        o += bolt3(cam, (0, 0, 0), Ax, 1.0, 5, "w", 28, thread_cls="mf")
        o += _box(cam, 44, -80, 22, 100, 160, 20, "t", dark=1)                        # upper die (moving)
        return o
    s, cam = stage(f2, 24, 8, (20, 44, 440, 280))
    for z, y0, y1 in ((32, 60, -60), (-32, -60, 60)):
        a, b = cam.xy((160, y0, z)), cam.xy((160, y1, z))
        s += arrow(a[0], a[1], b[0], b[1], None)
    s += title("平ダイスで挟んで転がし、ねじを転造")
    ops.append(s)

    # 3 hardening + tempering in a mesh-belt furnace ------------------------------------------------
    def f3(sc):
        cam = sc.cam
        o = _box(cam, -260, -60, -14, 560, 120, 10, "m", dark=1)
        o += _box(cam, -150, -70, -40, 300, 150, 150, "dk", dark=1)
        o += seg3(cam, [(-140, -70.2, 0), (140, -70.2, 0), (140, -70.2, 96), (-140, -70.2, 96)], "hotin", True)
        return o
    s, cam = stage(f3, -12, 22, (16, 56, 464, 240))
    for i, xb in enumerate((-230, -150, -70, 10, 90, 170, 250)):
        x, y = cam.xy((xb, -20, -2))
        s += tile(bolt_tile(5, "h" if -150 < xb < 150 else "w"), x, y, cam.s * .42)
    s += tol(40, 270, "硬さ・脱炭・遅れ破壊")
    s += title("メッシュベルト炉で焼入れ焼戻し")
    ops.append(s)

    # 4 zinc-flake coating, dip-spin ----------------------------------------------------------------
    def f4(sc):
        cam = sc.cam
        o = _box(cam, -150, -110, -150, 300, 220, 120, "m", dark=1)                   # tank
        o += seg3(cam, [(-138, -98, -30), (138, -98, -30), (138, 98, -30), (-138, 98, -30)], "fl", True)
        o += _cyl(cam, (0, 0, -60), Az, 80, 110, "dk", seg=32, dark=1, holes=[GE.circle_outline(72, 32, 32)])  # basket
        hd = []
        for q in range(9):
            a, r = q * 2.4, 22 + 6 * q
            c = (r * math.cos(a) * .9, r * math.sin(a) * .9, 40)
            if r < 70:
                hd.append(hole3(cam, c, Az, 9, "w") + hole3(cam, (c[0], c[1], 40.5), Az, 5, "w3"))
        o += "".join(hd)
        o += _cyl(cam, (0, 0, 50), Az, 6, 80, "t", seg=12) + _box(cam, -30, -30, 130, 60, 60, 36, "m", dark=1)
        return o
    s, cam = stage(f4, -20, 30, (90, 44, 390, 286))
    s += arc3(cam, (0, 0, 100), Az, 50, 200, 340)
    a, b = cam.xy((150, 0, 60)), cam.xy((150, 0, -10))
    s += arrow(a[0] + 30, a[1], b[0] + 30, b[1], None, both=True) + text(b[0] + 38, (a[1] + b[1]) / 2, "浸漬・遠心", "start", "al")
    s += title("亜鉛フレーク塗装（ディップスピン）で防錆")
    ops.append(s)

    # 5 rotating glass table, camera sorting --------------------------------------------------------
    def f5(sc):
        cam = sc.cam
        o = _cyl(cam, (0, 0, -40), Az, 24, 30, "m", seg=16)
        o += _cyl(cam, (0, 0, -10), Az, 220, 8, "fl", seg=36)                          # glass disc
        bl = []
        for q in range(8):
            a = 2 * PI * q / 8 - PI / 2
            c = (170 * math.cos(a), 170 * math.sin(a), 13 * .7 - 2)
            bl.append((cam.P(c)[2], bolt3(cam, c, Az, .7, 5, "w", 10, fine=False)))
        o += "".join(b for d, b in sorted(bl, key=lambda t: -t[0]))
        o += _box(cam, -30, -200, 210, 60, 60, 40, "dk", dark=1)                       # camera
        return o
    s, cam = stage(f5, -20, 28, (50, 40, 430, 262))
    a, b = cam.xy((0, -170, 210)), cam.xy((0, -170, 120))
    s += line(a[0], a[1], b[0], b[1], "o thin dash") + arc3(cam, (0, 0, -10), Az, 250, 200, 300)
    s += tol(40, 290, "異品・寸法不良の流出防止")
    s += title("回転ガラステーブル上で寸法・外観を全数選別")
    ops.append(s)
    return [slim(fin(x)) for x in ops]


# =====================================================================================
# thermal.ecomp — e-compressor (simplified from il3_zfix's part drawing) and a 3D scroll
# =====================================================================================
def ecomp_scene(sc, inv=True, inv_dz=0, head=True, ears=True):
    """housing on the x axis (discharge head at x = 0, facing -x), inverter on top (lifted by inv_dz)."""
    R = 50
    if head:
        CYL(sc, (0, 0, 0), (1, 0, 0), 44, 8, "w", seg=32, bands=10, r1=50)
    CYL(sc, (8, 0, 0), (1, 0, 0), 52, 36, "w", seg=32, bands=12)
    CYL(sc, (44, 0, 0), (1, 0, 0), 57, 8, "w", seg=32, bands=10, dark=1)
    x = 52
    for L in (40, 4, 40, 4, 38):
        CYL(sc, (x, 0, 0), (1, 0, 0), R + (3 if L == 4 else 0), L, "w", seg=32, bands=10 if L == 4 else 12, dark=2 if L == 4 else 1)
        x += L
    CYL(sc, (x, 0, 0), (1, 0, 0), R, 10, "w", seg=32, bands=10, r1=42, dark=1)
    if ears:
        for xe in (30, 160):
            CYL(sc, (xe, -62, -40), (0, 1, 0), 9, 124, "w", seg=16, dark=1)

    def hd(s_):
        cam = s_.cam
        o = hole3(cam, (-.1, 0, 0), (-1, 0, 0), 22, "w3") + hole3(cam, (-.2, 0, 0), (-1, 0, 0), 12, "w2")
        for k in range(6):
            a = 2 * PI * (k + .5) / 6
            c = (-.2, 35 * math.cos(a), 35 * math.sin(a))
            o += hole3(cam, c, (-1, 0, 0), 4.2, "w3") + hole3(cam, c, (-1, 0, 0), 2.2, "bg")
        return o
    if head:
        RAW(sc, hd, ((-.3, -44, -44), (-.1, 44, 44)), -2)

    def top(s_):
        cam = s_.cam
        dz = inv_dz
        o = ""
        if not dz:
            o += compact(GE.prism(cam, (60, 0, 0), (1, 0, 0), [(-36, 48, 0), (-30, 30, 1), (30, 30, 2), (36, 48, 3)], 100, "w", dark=1))
        o += _box(cam, 62, -38, 46 + dz, 96, 76, 20, "w")
        o += _box(cam, 66, -34, 66 + dz, 88, 68, 5, "w", dark=1, cap_mat="w2")
        o += path("".join(P([cam.xy((72, yy, 71.2 + dz)), cam.xy((148, yy, 71.2 + dz))], False) for yy in (-22, -10, 2, 14, 26)), "gr")
        o += _box(cam, 84, -52, 48 + dz, 28, 14, 16, "dk")
        o += hole3(cam, (92, -52.2, 56 + dz), (0, -1, 0), 3.2, "bg") + hole3(cam, (104, -52.2, 56 + dz), (0, -1, 0), 3.2, "bg")
        o += _box(cam, 12, -14, 44, 26, 28, 16, "w", cap_mat="w2")
        o += hole3(cam, (22, -2, 60.1), (0, 0, 1), 6.5, "w3") + hole3(cam, (22, -2, 60.2), (0, 0, 1), 4.6, "bg")
        return o
    if inv:
        RAW(sc, top, ((10, -52, 44), (160, 40, 72)), -1)


def scroll3(cam, C=(0, 0, 0), R=100, base=12, hw=30, th=6.0, r0=10, turns=3.4, k=4.0, seg=26):
    """fixed scroll: base plate + Archimedean spiral wall (ribbon sides depth-sorted, top in chunks)."""
    o = _cyl(cam, C, (0, 0, 1), R, base, "w", seg=48, dark=.5)
    z0, z1 = C[2] + base, C[2] + base + hw
    N = int(turns * seg)
    pts = []
    for i in range(N + 1):
        t = i / seg * 2 * PI
        r = r0 + k * t
        c, s_ = math.cos(t), math.sin(t)
        pts.append(((r + th / 2) * c, (r + th / 2) * s_, (r - th / 2) * c, (r - th / 2) * s_, c, s_))
    pieces = []
    D = cam.D
    for side in (0, 1):
        run, cur = [], None
        for i in range(N):
            a, b = pts[i], pts[i + 1]
            cx, cy = (a[4] + b[4]) / 2, (a[5] + b[5]) / 2
            nm = (cx, cy, 0) if side == 0 else (-cx, -cy, 0)
            vis = GE._dot(nm, D) < -1e-3
            sh = GE.shade(GE._norm(nm), .3) if vis else None
            if sh != cur and run:
                pieces.append((side, cur, run))
                run = []
            cur = sh
            run.append(i)
        if run:
            pieces.append((side, cur, run))
    items = []
    for side, sh, run in pieces:
        if sh is None:
            continue
        j = 0 if side == 0 else 2
        bot = [(pts[i][j] + C[0], pts[i][j + 1] + C[1], z0) for i in run + [run[-1] + 1]]
        top = [(x, y, z1) for x, y, _ in bot]
        poly3 = bot + top[::-1]
        pp = [cam.P(p) for p in poly3]
        items.append((sum(p[2] for p in pp) / len(pp), path(P([(p[0], p[1]) for p in pp]), "ws%d" % min(4, sh)) + path(P([(p[0], p[1]) for p in pp]), "el")))
    step = seg // 4
    for i0 in range(0, N, step):
        i1 = min(N, i0 + step)
        outer = [(pts[i][0] + C[0], pts[i][1] + C[1], z1) for i in range(i0, i1 + 1)]
        inner = [(pts[i][2] + C[0], pts[i][3] + C[1], z1) for i in range(i1, i0 - 1, -1)]
        pp = [cam.P(p) for p in outer + inner]
        items.append((sum(p[2] for p in pp) / len(pp) - 2, path(P([(p[0], p[1]) for p in pp]), "ws1")))
    items.sort(key=lambda t: -t[0])
    o += "".join(s_ for _, s_ in items)
    o += path(P([cam.xy((p[0] + C[0], p[1] + C[1], z1)) for p in pts], False) + P([cam.xy((p[2] + C[0], p[3] + C[1], z1)) for p in pts], False), "el")
    return o


def spiral_pt(i, seg=26, r0=10, k=4.0, z=0):
    t = i / seg * 2 * PI
    r = r0 + k * t
    return (r * math.cos(t), r * math.sin(t), z)


@dpart("thermal.ecomp", "detail")
def ecomp_detail3():
    notes = [("スクロール（渦巻き）", "壁厚・高さ数μm。可動と固定の2枚で圧縮"), ("モータ部", "インバータ一体の駆動モータ"), ("ハウジング", "アルミダイカスト。冷媒の吸入・吐出")]
    s, cam = stage(lambda sc: ecomp_scene(sc), 28, 22, (16, 40, 316, 262))
    s += inset(330, 60, 140, 150, "固定スクロール")
    s2, c2 = stage(lambda sc: scroll3(sc.cam, seg=22), -20, 44, (340, 84, 460, 200), sh=False)
    s += s2
    s += bal(*c2.xy(spiral_pt(40, 22, z=42)), 460, 260, 1)
    s += bal(*cam.xy((120, -30, -40)), 120, 280, 2)
    s += bal(*cam.xy((26, -40, -32)), 280, 280, 3)
    return slim(s), notes


@dpart("thermal.ecomp", "ops")
def ecomp_ops3():
    ops = []
    Az = (0, 0, 1)

    # 0 forge (or cast) the aluminium scroll blank -----------------------------------------------
    def f0(sc):
        BOX(sc, -150, -90, -100, 300, 180, 60, "t", dark=1)
        CYL(sc, (0, 0, -40), Az, 90, 30, "h", seg=40)
        BOX(sc, -150, -90, 60, 300, 180, 60, "t", dark=1)
        CYL(sc, (0, 0, 120), Az, 40, 60, "m", seg=24, dark=1)
    s, cam = stage(f0, -20, 22, (90, 46, 390, 280))
    a, b = cam.xy((200, 0, 140)), cam.xy((200, 0, 80))
    s += arrow(a[0], a[1], b[0], b[1], None)
    s += title("アルミを鍛造（または鋳造）してスクロール素材をつくる")
    ops.append(s)

    # 1 high-speed contour milling of the spiral wall -------------------------------------------
    sg = 26
    ip = int(2.6 * sg)
    tp = spiral_pt(ip, sg, z=12)

    def f1(sc):
        cam = sc.cam
        o = _cyl(cam, (0, 0, -30), Az, 120, 30, "m", seg=48, dark=1)
        o += scroll3(cam, seg=sg)
        o += _cyl(cam, (tp[0], tp[1], 22), Az, 5, 70, "t", seg=12) + _cyl(cam, (tp[0], tp[1], 92), Az, 14, 30, "t", seg=16, r1=9)
        o += _cyl(cam, (tp[0], tp[1], 122), Az, 30, 60, "m", seg=24, dark=1)
        return o
    s, cam = stage(f1, -20, 40, (40, 36, 330, 262))
    # wall top edges just milled: blue along the last half turn before the cutter
    s += path(P([cam.xy(_add(spiral_pt(i, sg, z=42), (math.cos(i / sg * 2 * PI), math.sin(i / sg * 2 * PI), 0), 3)) for i in range(ip - sg // 2, ip + 1)], False), "mf")
    s += arc3(cam, (tp[0], tp[1], 160), Az, 40, 200, 340)
    e, a = cam.xy(spiral_pt(ip + 2, sg, z=60)), cam.xy(spiral_pt(ip, sg, z=60))
    L = math.hypot(e[0] - a[0], e[1] - a[1]) or 1
    s += arrow(a[0] + 14, a[1] + 6, a[0] + 14 + (e[0] - a[0]) / L * 40, a[1] + 6 + (e[1] - a[1]) / L * 40, None)
    s += text(344, 92, "輪郭に沿って移動", "start", "al")
    s += tol(320, 276, "壁厚・高さ 数μm・壁面粗さ")
    s += title("渦巻き状の壁を高速輪郭加工")
    ops.append(s)

    # 2 multi-face machining of the housing (coaxial bores) ------------------------------------------
    def f2(sc):
        ecomp_scene(sc, inv=False, head=False)
        CYL(sc, (8, 0, 0), (-1, 0, 0), 9, 110, "t", seg=12)
        CYL(sc, (-102, 0, 0), (-1, 0, 0), 22, 50, "m", seg=24, dark=1)

        def bore(s_):
            cam = s_.cam
            return hole3(cam, (7.9, 0, 0), (-1, 0, 0), 44, "w3") + hole3(cam, (7.8, 0, 0), (-1, 0, 0), 38, "bg") + \
                ring3(cam, (7.7, 0, 0), (-1, 0, 0), 44, "mf", 32)
        RAW(sc, bore, ((7.7, -44, -44), (7.9, 44, 44)), -2)
    s, cam = stage(f2, 28, 22, (40, 44, 440, 280))
    a, b = cam.xy((-60, 0, 40)), cam.xy((-20, 0, 40))
    s += arrow(a[0], a[1] - 20, b[0], b[1] - 20, None) + arc3(cam, (-60, 0, 0), (1, 0, 0), 34, 100, 200)
    s += title("ハウジングを多面加工（同軸度）")
    ops.append(s)

    # 3 install motor and inverter (insulation, tightening) -------------------------------------------
    s, cam = stage(lambda sc: ecomp_scene(sc, inv_dz=70), 28, 22, (40, 40, 440, 280))
    for xx in (80, 140):
        a, b = cam.xy((xx, -46, 120)), cam.xy((xx, -46, 72))
        s += arrow(a[0], a[1] + 30, b[0], b[1] + 30, None)
    s += title("モータとインバータを組み付け（絶縁・締付け）")
    ops.append(s)

    # 4 performance test with refrigerant, helium leak test ---------------------------------------------
    s, cam = stage(lambda sc: ecomp_scene(sc), 28, 22, (30, 56, 320, 280))
    s += dots(30, 40, 420, 24, 14, "he") + chart(330, 200, 140, 74, "rise")
    s += title("冷媒で性能を確認し、ヘリウムで漏れを検査")
    ops.append(s)
    return [slim(fin(x)) for x in ops]
