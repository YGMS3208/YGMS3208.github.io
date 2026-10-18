"""v3 machine-tool atlas drawings, components (team mtc2): tool-holder, chuck, turret, coolant, bed,
thermal-displacement. Re-registers the same slugs as il_mt.py with the same notes (text, count, order)."""
import math
import il_gear as GE
from il_mt import mt
from il3_mtlib import *


# ------------------------------------------------------------------ local helpers (cut-away models)
def _sbb(x0, x1, ro, ri, a0, a1, cy, cz, r1=None):
    """world bbox of an annular sector (angles deg, 0 = +y, 90 = +z) along x."""
    angs = [a0, a1] + [a for a in range(-720, 721, 90) if a0 < a < a1]
    R = max(ro, r1 or 0)
    ys, zs = [], []
    for a in angs:
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        for r in (R, ri * min(1, (r1 or ro) / ro)):
            ys.append(cy + r * c)
            zs.append(cz + r * s_)
    return ((x0, min(ys), min(zs)), (x1, max(ys), max(zs)))


def shell(sc, x0, L, ro, ri, a0=-90, a1=90, mat="w", dark=1, bias=0.0, seg=20, cy=0.0, cz=0.0, r1=None):
    """annular sector of a tube along x from x0 (angles a0..a1 deg; 0 = +y, 90 = +z) with an exact bbox.
    r1: outer radius at x0+L (the whole section scales -> tapers)."""
    o = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((ro * math.cos(t), ro * math.sin(t), k // 3))
    for k in range(seg, -1, -1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((ri * math.cos(t), ri * math.sin(t), 100 + k // 3))
    scl = (lambda t: 1 + (r1 / ro - 1) * t) if r1 else None
    sv = GE.prism(sc.cam, (x0, cy, cz), (1, 0, 0), o, L, mat, smooth=True, dark=dark, scale=scl)
    sc.add(_chain_svg(compact(sv)), _sbb(x0, x0 + L, ro, ri, a0, a1, cy, cz, r1), bias)


def xcut(sc, polys, ang, bias=0.0, cy=0.0, cz=0.0, bb=None):
    """flat section faces in the half plane through the x axis at angle ang (deg): polys [([(x, r)], cls)]."""
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def w(x, r):
        return (x, cy + r * c, cz + r * s_)

    def f(sc_):
        by = {}
        for pts_, cls in polys:
            by[cls] = by.get(cls, "") + P([sc_.cam.xy(w(x, r)) for x, r in pts_])
        return "".join(path(d, k) for k, d in by.items())
    sc.add(f, bb or bbox([w(x, r) for pl, _ in polys for x, r in pl]), bias)


def face(sc, pts3, cls, bb=None, bias=0.0):
    """flat polygon (cut faces, liquid surfaces, windows) drawn with one class."""
    sc.add(lambda s_: path(P([s_.cam.xy(p) for p in pts3]), cls), bb or bbox(pts3), bias)


# =====================================================================================
_TH = (-240, 420)          # HSK holder placed behind/above the BT holder (compact, larger fit)


@mt("tool-holder", az=-24, el=16)
def _(sc):
    """BT holder (exterior, front) and HSK holder cut in half (back half kept, section on y=60)."""
    X = (1, 0, 0)
    x0, yb = -260, -60
    # --- BT: pull stud, 7/24 taper, flange with V groove, collet chuck body, nut, end mill
    MCYL(sc, (x0 - 40, yb, 0), X, 6, 7, "w", r1=9, seg=18, bands=6, spec=False)
    MCYL(sc, (x0 - 33, yb, 0), X, 6.5, 6, "w", seg=18, bands=6, spec=False)
    MCYL(sc, (x0 - 27, yb, 0), X, 10, 12, "w", seg=20, bands=8, rings=(.5,))
    cprism(sc, "x", x0 - 15, 9, [(yb + 13 * math.cos(math.pi / 3 * k + math.pi / 6), 13 * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)], "w", .8, .8, dark=1)
    MCYL(sc, (x0 - 6, yb, 0), X, 8, 6, "w", seg=18, bands=6, spec=False)
    MCYL(sc, (x0, yb, 0), X, 22, 70, "w", r1=40, seg=36, bands=14)
    MCYL(sc, (x0 + 70, yb, 0), X, 48, 6, "w", r1=56, seg=40, bands=12, spec=False)
    MCYL(sc, (x0 + 76, yb, 0), X, 56, 6, "w", seg=40, bands=12)
    MCYL(sc, (x0 + 82, yb, 0), X, 56, 5, "w", r1=47, seg=40, bands=12, dark=2, spec=False)
    MCYL(sc, (x0 + 87, yb, 0), X, 47, 5, "w", r1=56, seg=40, bands=12, spec=False)
    MCYL(sc, (x0 + 92, yb, 0), X, 56, 8, "w", seg=40, bands=12)
    holes(sc, [(x0 + 100.2, yb + 40 * math.cos(t), 40 * math.sin(t)) for t in (math.radians(200), math.radians(340))], X, 3.4)
    MCYL(sc, (x0 + 100, yb, 0), X, 36, 10, "w", r1=32, seg=32, bands=12)
    MCYL(sc, (x0 + 110, yb, 0), X, 30, 34, "w", r1=28, seg=32, bands=12, rings=(.15,))
    MCYL(sc, (x0 + 144, yb, 0), X, 33, 18, "m", seg=32, bands=12, rings=(.5,))
    for t in (200, 250):
        a = math.radians(t)
        holes(sc, [(x0 + 153, yb + 33.2 * math.cos(a), 33.2 * math.sin(a))], (0, math.cos(a), math.sin(a)), 3.2)
    MCYL(sc, (x0 + 162, yb, 0), X, 22, 6, "m", r1=17, seg=24, bands=8, spec=False)
    MCYL(sc, (x0 + 168, yb, 0), X, 12, 62, "t", seg=20, bands=8, dark=0)
    sc.raw(lambda s_: helix(s_.cam, (x0 + 180, yb, 0), X, 12, 50, 36, "hobt", per=14),
           ((x0 + 180, yb - 12.5, -12), (x0 + 230, yb - 12, 12)), bias=-3)

    # --- HSK: back half of the hollow short taper holder, section faces on y = yh
    x1, yh = _TH
    shell(sc, x1, 48, 29, 26, mat="w", r1=33, bias=300, seg=20, cy=yh)
    shell(sc, x1 + 48, 8, 50, 22, mat="w", bias=300, seg=24, cy=yh)
    shell(sc, x1 + 56, 10, 44, 22, mat="w", dark=2, bias=300, seg=24, cy=yh)
    shell(sc, x1 + 66, 14, 50, 12, mat="w", bias=300, seg=24, cy=yh)
    shell(sc, x1 + 80, 60, 30, 12, mat="w", r1=26, bias=300, seg=20, cy=yh)
    prof = [(x1, 22), (x1, 29), (x1 + 48, 33), (x1 + 48, 50), (x1 + 56, 50), (x1 + 61, 44), (x1 + 66, 50),
            (x1 + 80, 50), (x1 + 80, 30), (x1 + 140, 26), (x1 + 140, 12), (x1 + 82, 12), (x1 + 82, 6), (x1 + 60, 6),
            (x1 + 60, 22), (x1 + 50, 22), (x1 + 46, 27), (x1 + 16, 27), (x1 + 11, 22)]
    for ang in (90, 270):
        xcut(sc, [(prof, "cut")], ang, bias=200, cy=yh, bb=((x1, yh - .5, -50), (x1 + 140, yh, 50)))
    # drawbar + clamping segments of the spindle, pulling from inside
    MCYL(sc, (x1 - 40, yh, 0), X, 9, 56, "w", seg=18, bands=6, bias=100, rings=(.3,))
    MCYL(sc, (x1 + 16, yh, 0), X, 16, 24, "dk", r1=13, seg=24, bands=8, dark=0, bias=95)
    MCYL(sc, (x1 + 14, yh, 0), X, 24, 30, "dk", seg=24, bands=10, dark=0, bias=99,
         holes=[GE.circle_outline(17, 24, 24)])
    # tool shrunk into the bore, sticking out of the nose
    MCYL(sc, (x1 + 82, yh, 0), X, 12, 128, "t", seg=20, bands=8, dark=0, bias=90)
    sc.raw(lambda s_: helix(s_.cam, (x1 + 160, yh, 0), X, 12, 50, 36, "hobt", per=14),
           ((x1 + 160, yh - 12.5, -12), (x1 + 210, yh - 12, 12)), bias=-3)
    sc.note((x0 - 30, -60, 9), "プルスタッド", "主軸のクランプ機構が引き込む（BT）")
    sc.note((x0 + 30, -60, 30), "テーパ部（7/24）", "主軸の内テーパに入って芯を合わせる")
    sc.note((x0 + 85, -60, 52), "フランジ（V溝）", "ATCのアームがつかむ溝")
    sc.note((x0 + 200, -60, 12), "工具", "エンドミル・ドリルなど")
    sc.note((x1 + 20, yh, 31), "中空短テーパ（HSK）", "内側から引き込み、テーパと端面の2面で固定する")
    sc.note((x1 + 50, yh, 50), "端面拘束", "高速回転でも抜けにくく、振れが小さい")


# =====================================================================================
def qcut(sc, x0, L, ro, ri, mat="w", r1=None, back=500, front=100, seg=20, dark=1):
    """tube along x with the front-top quadrant removed: back half + front-bottom quadrant."""
    shell(sc, x0, L, ro, ri, -90, 90, mat, dark, back, seg, r1=r1)
    shell(sc, x0, L, ro, ri, -180, -90, mat, dark, front, max(6, seg // 2), r1=r1)


@mt("chuck", az=-30, el=20)
def _(sc):
    """3-jaw power chuck + rotary hydraulic cylinder, front-top quadrant cut away (sections on y=0 and z=0)."""
    X = (1, 0, 0)
    # rotary cylinder: housing, piston; oil distributor at the back (stationary)
    MCYL(sc, (-236, 0, 0), X, 38, 36, "dk", seg=28, bands=10, dark=0, rings=(.5,))
    for t in (110, 160):
        a = math.radians(t)
        MCYL(sc, (-222, 38 * math.cos(a) * .9, 38 * math.sin(a) * .9), (0, math.cos(a), math.sin(a)), 6, 16, "w", seg=14, bands=5, spec=False, bias=-1)
    qcut(sc, -200, 10, 70, 26, "dk", dark=0)
    qcut(sc, -190, 40, 70, 60, "dk", dark=0, seg=24)
    qcut(sc, -150, 10, 70, 26, "dk", dark=0)
    qcut(sc, -178, 14, 60, 24, "w", back=450, front=150)
    cyl_p = [(-200, 26), (-200, 70), (-140, 70), (-140, 26), (-150, 26), (-150, 60), (-190, 60), (-190, 26)]
    pis_p = [(-178, 24), (-178, 60), (-164, 60), (-164, 24)]
    oil = [[(-190, 24), (-190, 60), (-178, 60), (-178, 24)], [(-164, 24), (-164, 60), (-150, 60), (-150, 24)]]
    # chuck body (bored for the wedge plunger)
    qcut(sc, -80, 10, 120, 30, "m", seg=36)
    qcut(sc, -70, 56, 120, 50, "m", seg=36)
    qcut(sc, -14, 14, 120, 30, "m", seg=36)
    body_p = [(-80, 30), (-80, 120), (0, 120), (0, 30), (-14, 30), (-14, 50), (-70, 50), (-70, 30)]
    for ang, bi in ((90, 400), (180, 90)):
        polys = [(cyl_p, "cut"), (pis_p, "cut"), (body_p, "cut")] + [(o, "fl") for o in oil]
        bb = ((-200, -.5, 0), (0, 0, 120)) if ang == 90 else ((-200, -120, 0), (0, 0, .5))
        xcut(sc, polys, ang, bias=bi, bb=bb)
    # draw tube + wedge plunger (whole: moving parts)
    MCYL(sc, (-200, 0, 0), X, 24, 136, "w", seg=24, bands=8, bias=300, rings=(.2,))
    MCYL(sc, (-66, 0, 0), X, 46, 48, "w", seg=32, bands=12, bias=290, rings=(.3, .7))
    # jaws: master jaw (steel) + soft top jaw (aluminium) with two cap screws; the top one is cut in half
    for ang in (210, 330):
        bi = -20 if ang == 210 else 20
        radial(sc, "x", 0, 20, (0, 0), ang, 34, 104, 30, "w", b=1, bias=bi)
        radial(sc, "x", 20, 34, (0, 0), ang, 38, 92, 26, "alu", b=1.2, dark=0, bias=bi - 1)
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        bolts(sc, [(54, r * c, r * s_) for r in (54, 78)], X, 4.4, bias=bi - 2)
    cprism(sc, "x", 0, 20, [(0, 34), (15, 34), (15, 104), (0, 104)], "w", 1, 1, dark=1, bias=250)
    cprism(sc, "x", 20, 34, [(0, 38), (13, 38), (13, 92), (0, 92)], "alu", 1.2, 1.2, dark=0, bias=249)
    mj = [(-36, 50), (-36, 100), (0, 100), (0, 104), (20, 104), (20, 34), (0, 34), (0, 50)]
    tj = [(20, 38), (20, 92), (54, 92), (54, 38)]
    xcut(sc, [(mj, "cut"), (tj, "cut")], 90, bias=240, bb=((-36, -.5, 34), (54, 0, 104)))
    # face: centre bore, mounting bolts between the jaws
    holes(sc, [(0.2, 0, 0)], X, 30, bias=-30)
    bolts(sc, [(0, 100 * math.cos(math.radians(a)), 100 * math.sin(math.radians(a))) for a in (30, 270)], X, 4.2, bias=-30)
    # workpiece gripped on its outside diameter
    MCYL(sc, (20, 0, 0), X, 36, 150, "w", seg=36, bands=14, dark=0, bias=-60, rings=(.97,))
    sc.axis((37, -10, 166), (37, -10, 112), "把握", both=False, off=(22, 0))
    sc.note((-40, -100, 0), "チャック本体", "主軸の先端に取り付ける")
    sc.note((10, 8, 100), "マスタージョー", "本体の溝を半径方向に動く")
    sc.note((40, 0, 70), "生爪（トップジョー）", "工作物に合わせて削って使う柔らかい爪")
    sc.note((150, 0, 36), "工作物", "爪で外径をつかむ")
    sc.note((-170, 0, -70), "油圧シリンダ", "ドローチューブを引いて爪を閉じる")


# =====================================================================================
def balls(sc, pts3, A, r, bias=0.0):
    """rolling elements seen in a section (flat discs, class ball)."""
    def f(s_):
        return path("".join(P(circ3(s_.cam, C, A, r, 14)) for C in pts3), "ball")
    lo, hi = bbox(pts3)
    sc.add(f, (tuple(v - r for v in lo), tuple(v + r for v in hi)), bias)


@mt("turret", az=-34, el=18)
def _(sc):
    """12-station turret with driven tools; the housing's front-top quadrant is cut away (planes y=0, z=0)."""
    X = (1, 0, 0)
    # housing: back half (y>0) and front-bottom block (y<0, z<0)
    block(sc, -260, 0, -130, 180, 120, 250, "pt", ch=0, b=3, bias=600)
    servo(sc, (-260, 70, 80), (-1, 0, 0), 44, 50, up="z")
    # section of the housing walls on y=0 (upper half) and z=0 (front half); dark cavity inside
    wall_y = [[(-260, 0, 108), (-80, 0, 108), (-80, 0, 120), (-260, 0, 120)],
              [(-260, 0, 0), (-248, 0, 0), (-248, 0, 108), (-260, 0, 108)],
              [(-92, 0, 62), (-80, 0, 62), (-80, 0, 108), (-92, 0, 108)]]
    cav_y = [(-248, 0, 0), (-92, 0, 0), (-92, 0, 108), (-248, 0, 108)]
    face(sc, [(-248, -.2, 0), (-92, -.2, 0), (-92, -.2, 108), (-248, -.2, 108)], "dks4", bias=500)
    for w_ in wall_y:
        face(sc, [(x, -.2, z) for x, _, z in w_], "cut", bias=499)
    # shaft, index gear, front bearing (cut), clamp piston for the coupling
    MCYL(sc, (-248, 0, 0), X, 30, 168, "w", seg=24, bands=10, bias=300, rings=(.25,))
    sc.gear((-206, 0, 0), X, 24, 62, 22, "w", bias=290)
    MCYL(sc, (-212, 0, 0), X, 40, 6, "w", seg=28, bands=8, spec=False, bias=289)
    qcut(sc, -108, 28, 62, 30, "w", back=320, front=110, seg=16)
    for ang in (90, 180):
        xcut(sc, [([(-108, 30), (-108, 40), (-80, 40), (-80, 30)], "cut"), ([(-108, 52), (-108, 62), (-80, 62), (-80, 52)], "cut"),
                  ([(-104, 40), (-104, 52), (-84, 52), (-84, 40)], "dks4")], ang, bias=280 if ang == 90 else 80,
             bb=((-108, -.5, 30), (-80, 0, 62)) if ang == 90 else ((-108, -62, 0), (-80, -30, .5)))
    balls(sc, [(-94, -.3, 46), (-94, -46, .3)], (0, 1, 0), 5.5, bias=279)
    block(sc, -260, -120, -130, 180, 120, 130, "pt", ch=0, b=0, bias=100)
    wall_z = [[(-260, -120), (-80, -120), (-80, -108), (-260, -108)], [(-260, -108), (-248, -108), (-248, 0), (-260, 0)],
              [(-92, -108), (-80, -108), (-80, -62), (-92, -62)]]
    face(sc, [(-248, -108, .2), (-92, -108, .2), (-92, 0, .2), (-248, 0, .2)], "dks3", bias=90)
    for w_ in wall_z:
        face(sc, [(x, y, .2) for x, y in w_], "cut", bias=89)
    # curvic coupling: fixed ring + turning ring with face teeth (zigzag joint)
    MCYL(sc, (-80, 0, 0), X, 98, 8, "m", seg=48, bands=14, spec=False)
    MCYL(sc, (-72, 0, 0), X, 96, 8, "w", seg=48, bands=14)

    def teeth(s_):
        E1, E2, _ = GE.frame(X)
        pts_ = []
        for k in range(97):
            t = 2 * math.pi * k / 96
            nr = (0, math.cos(t), math.sin(t))
            if GE._dot(nr, s_.cam.D) < 0:
                pts_.append(s_.cam.xy((-72 + (2.6 if k % 2 else -2.6), 97 * nr[1], 97 * nr[2])))
            elif len(pts_) > 1:
                break
        return path(P(pts_, False), "el")
    sc.raw(teeth, ((-75, -98, -98), (-69, 98, 98)), bias=-1)
    # turret disc (12 faces) + centre cap
    R = 112
    poly = [(R * math.cos(2 * math.pi * k / 12 + math.pi / 12), R * math.sin(2 * math.pi * k / 12 + math.pi / 12)) for k in range(12)]
    cprism(sc, "x", -64, 60, poly, "m", 3, 3, dark=1)
    bolts(sc, [(-4, 100 * math.cos(math.pi * k / 6), 100 * math.sin(math.pi * k / 6)) for k in range(0, 12, 2)], X, 3.2, bias=-1)
    MCYL(sc, (-4, 0, 0), X, 34, 8, "w", seg=28, bands=10, rings=(.5,))
    bolts(sc, ring_pts((4, 0, 0), X, 22, 6), X, 3.4, bias=-2)
    # stations: driven-tool units (every 3rd) and turning holders with inserts
    for k in range(12):
        t = 2 * math.pi * k / 12 + math.pi / 12
        y, z = 92 * math.cos(t), 92 * math.sin(t)
        if k % 3 == 0:
            MCYL(sc, (-4, y, z), X, 16, 30, "dk", seg=16, bands=6, dark=0, rings=(.3,))
            MCYL(sc, (26, y, z), X, 12, 8, "w", seg=14, bands=5, spec=False)
            MCYL(sc, (34, y, z), X, 6, 40, "t", seg=14, bands=6, dark=0)
            sc.raw(lambda s_, y=y, z=z: helix(s_.cam, (44, y, z), X, 6, 30, 16, "hobt", per=10), ((44, y - 6.5, z - 6), (74, y - 6, z + 6)), bias=-3)
        else:
            ang = math.degrees(t)
            cprism(sc, "x", -4, 34, [(y - 13, z - 13), (y + 13, z - 13), (y + 13, z + 13), (y - 13, z + 13)], "w", 0, 1.5, dark=1)
            cprism(sc, "x", 30, 18, [(y - 6, z - 6), (y + 6, z - 6), (y + 6, z + 6), (y - 6, z + 6)], "dk", .8, 0, dark=0)
            cprism(sc, "x", 48, 6, [(y - 7, z - 7), (y + 7, z - 7), (y, z + 7)] if ang % 180 < 90 else [(y - 7, z + 7), (y + 7, z + 7), (y, z - 7)], "t", 0, 1.2, dark=0)
    sc.rot((70, 0, 0), X, 150, "割出し", 200, 300)
    sc.note((-34, 0, 112), "タレット本体", "12角などの割出し盤。周囲に工具を並べる")
    sc.note((41, 92 * math.cos(math.pi / 12 + math.pi / 6), 92 * math.sin(math.pi / 12 + math.pi / 6)), "工具ホルダ・バイト", "旋削用の工具を固定する")
    sc.note((50, 92 * math.cos(math.pi / 12), 92 * math.sin(math.pi / 12)), "回転工具", "ドリル・エンドミルを回す（複合化）")
    sc.note((-76, -96, -40), "カップリング", "歯形の噛み合いで割出し位置を固定する")
    sc.note((-290, 70, 90), "割出しモータ", "タレットを回して工具を選ぶ")
    sc.note((-200, -120, 60), "タレット台", "X・Z軸で動く刃物台本体")


# =====================================================================================
@mt("coolant", az=-30, el=22)
def _(sc):
    """coolant circuit: tank (front wall cut away) with weir, submerged pump, filter, nozzle at the tool."""
    Z = (0, 0, 1)
    # tank shell: bottom, back/left/right walls, front wall cut down (corner kept), lid at the back
    block(sc, -310, -130, 0, 360, 240, 10, "pt", b=0, bias=900)
    block(sc, -310, 100, 10, 360, 10, 140, "pt", b=1.5, bias=880)
    block(sc, -310, -130, 10, 10, 230, 140, "pt", b=1.5, bias=870)
    # weir plate and submerged pump column with strainer (seen through the coolant)
    block(sc, -150, -120, 10, 8, 220, 120, "pt", b=1, dark=0, bias=500)
    MCYL(sc, (-200, 40, 34), Z, 11, 116, "w", seg=16, bands=6, bias=500)
    MCYL(sc, (-200, 40, 12), Z, 20, 22, "m", seg=20, bands=6, spec=False, bias=501)
    seams(sc, [[(-200 + 20 * math.cos(t), 40 + 20 * math.sin(t), 14), (-200 + 20 * math.cos(t), 40 + 20 * math.sin(t), 32)]
               for t in [math.radians(a) for a in range(190, 360, 20)]], ((-220, 20, 12), (-180, 60, 34)), "gr", bias=499)
    for x0, x1 in ((-300, -150), (-142, 40)):
        abox(sc, (x0, -120, 10), (x1, 100, 120), "fl", dark=0, bias=400)
    block(sc, 40, -130, 10, 10, 230, 140, "pt", b=1.5, bias=100)
    block(sc, -300, -130, 10, 340, 10, 40, "pt", b=0, bias=100)
    block(sc, -300, -130, 50, 60, 10, 100, "pt", b=1.5, bias=100)
    face(sc, [(-240, -130, 50.2), (40, -130, 50.2), (40, -120, 50.2), (-240, -120, 50.2)], "cut", bias=99)
    face(sc, [(-239.8, -130, 50), (-239.8, -120, 50), (-239.8, -120, 150), (-239.8, -130, 150)], "cut", bias=99)
    block(sc, -300, 0, 150, 340, 100, 8, "pt", ch=0, b=1.5, dark=0, bias=300)
    bolts(sc, [(-280 + 40 * k, 8, 158) for k in range(9) if k not in (2,)], Z, 3, bias=299)
    # pump: flange, cooling-fin motor, discharge elbow
    MCYL(sc, (-200, 40, 158), Z, 30, 10, "dk", seg=28, bands=8, dark=0, bias=200)
    finmotor(sc, (-200, 40, 168), Z, 25, 62, nf=14, bias=200)
    MCYL(sc, (-178, 40, 186), (1, 0, 0), 9, 26, "m", seg=14, bands=5, spec=False, bias=190)
    # filter unit with a cartridge canister
    block(sc, 70, -60, 0, 100, 120, 120, "pt", ch=6, b=3, bias=300)
    seams(sc, [[(78, -60.2, 20), (162, -60.2, 20), (162, -60.2, 100), (78, -60.2, 100), (78, -60.2, 20)]], ((78, -61, 20), (162, -60, 100)), "gr", bias=299)
    MCYL(sc, (120, 10, 120), Z, 30, 44, "m", seg=28, bands=10, rings=(.5,), bias=200)
    MCYL(sc, (120, 10, 164), Z, 34, 8, "w", seg=28, bands=8, bias=199)
    # machine side: pedestal, table with T-slots, workpiece, spindle nose, holder, end mill
    block(sc, 200, -110, 0, 120, 120, 160, "pt", ch=6, b=2, bias=150)
    block(sc, 170, -130, 160, 160, 160, 20, "m", ch=3, b=2, bias=120)
    seams(sc, [[(176, y, 180.2), (324, y, 180.2)] for y in (-118, 18)], ((176, -118, 180), (324, 18, 180.5)), "tslot", bias=119)
    block(sc, 180, -120, 180, 130, 130, 60, "alu", b=1.5, dark=0, bias=100)
    seams(sc, [[(200, -100, 240.2), (230, -100, 240.2), (230, -60, 240.2)]], ((200, -100, 240), (230, -60, 240.5)), "alus4", bias=99)
    MCYL(sc, (240, -40, 360), (0, 0, -1), 34, 30, "w", seg=28, bands=10, rings=(.5,))
    MCYL(sc, (240, -40, 330), (0, 0, -1), 24, 12, "w", seg=24, bands=8)
    MCYL(sc, (240, -40, 318), (0, 0, -1), 16, 18, "w", r1=11, seg=20, bands=8)
    MCYL(sc, (240, -40, 300), (0, 0, -1), 8, 55, "t", seg=16, bands=6, dark=0)
    sc.raw(lambda s_: helix(s_.cam, (240, -40, 248), Z, 8, 40, 24, "hobt", per=10), ((232, -48.5, 248), (248, -48, 288)), bias=-3)
    # piping (pump -> nozzle manifold; table -> filter -> tank) and the nozzle
    seams(sc, [[(-152, 40, 186), (-140, 40, 186), (-140, 40, 350), (150, 40, 350), (196, -40, 350), (204, -40, 334)]],
          ((-152, -40, 186), (204, 40, 350)), "pipe", bias=-5)
    seams(sc, [[(170, -20, 166), (120, -20, 166), (120, -20, 176)], [(70, 10, 80), (50, 10, 80)]], ((50, -20, 80), (170, 10, 176)), "pipe", bias=-4)
    MCYL(sc, (204, -40, 334), (0.45, 0, -0.89), 5, 30, "m", seg=12, bands=4, spec=False, bias=-6)
    MCYL(sc, (217.5, -40, 307.3), (0.45, 0, -0.89), 5, 16, "dk", r1=3, seg=12, bands=4, spec=False, dark=0, bias=-7)

    def spray(s_):
        a = s_.P((225, -40, 293))
        b = s_.P((240, -40, 248))
        o = ""
        for k in range(-3, 4):
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0] + k * 5), n(b[1] + abs(k) * 2))
        return path(o, "spray")
    sc.raw(spray, ((222, -42, 246), (242, -38, 296)), bias=-50)

    def chips(s_):
        o = ""
        for k in range(14):
            p = s_.P((190 + (k * 37) % 110, -110 + (k * 53) % 120, 241))
            o += '<path class="chipc" d="M%s %sq4 -6 8 0q4 6 8 0"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(chips, ((190, -110, 241), (300, 10, 241.5)), bias=40)
    sc.note((222, -40, 296), "ノズル", "刃先に切削油を吹き付け、冷却・潤滑・切りくず排出をする")
    sc.note((260, -110, 250), "切りくず", "クーラントで流してコンベヤへ送る")
    sc.note((-120, -120, 100), "クーラントタンク", "使った切削油を回収してためる")
    sc.note((-200, 40, 200), "ポンプ", "加圧して刃先や主軸の中へ送る")
    sc.note((130, -60, 110), "ろ過装置", "細かい切りくずを除いて再利用する")


# =====================================================================================
@mt("bed", az=-32, el=30)
def _(sc):
    """box-section cast bed: top flanges with ground guideway faces, rib grid seen through the central
    opening and a front-right cut-away of the outer wall (section hatched)."""
    L, Wd, Hh, t = 560, 300, 120, 14
    xa, xb = -L / 2, L / 2
    XC, ZC = 40, 34                      # cut-away: front wall above ZC and the front flange for x > XC
    block(sc, xa, -Wd / 2, 0, L, Wd, t, "pt", b=0, bias=900)
    block(sc, xa, Wd / 2 - t, t, L, t, Hh - t, "pt", b=0, bias=880)
    block(sc, xa, -Wd / 2, t, t, Wd - t, Hh - t, "pt", b=0, bias=870)
    # rib grid: transverse ribs + longitudinal ribs split between them (lightening holes on the front faces)
    xs = [-200, -110, -20, 70, 160]
    for x in xs:
        block(sc, x - 5, -Wd / 2 + t, t, 10, Wd - 2 * t, Hh - 6 - t, "pt", b=0, bias=500)
    edges = [xa + t] + [v for x in xs for v in (x - 5, x + 5)] + [xb - t]
    for y in (-50, 50):
        for x0, x1 in zip(edges[0::2], edges[1::2]):
            block(sc, x0, y - 5, t, x1 - x0, 10, Hh - 16 - t, "pt", b=0, bias=500)
            if y < 0:
                holes(sc, [((x0 + x1) / 2, y - 5.2, 62)], (0, -1, 0), 17, "dks4", bias=499)
    block(sc, xb - t, -Wd / 2, t, t, Wd - t, Hh - t, "pt", b=0, bias=100)
    block(sc, xa + t, -Wd / 2, t, XC - xa - t, t, Hh - t, "pt", b=0, bias=100)
    block(sc, XC, -Wd / 2, t, xb - t - XC, t, ZC - t, "pt", b=0, bias=100)
    # top flanges (front one cut at XC) + ground mounting faces with tapped holes
    block(sc, xa, 80, Hh, L, Wd / 2 - 80, 14, "pt", ch=0, b=2, bias=80)
    block(sc, xa, -Wd / 2, Hh, XC - xa, Wd / 2 - 80, 14, "pt", ch=0, b=2, bias=80)
    for y0, x1 in ((94, xb - 10), (-126, XC)):
        block(sc, xa + 10, y0, Hh + 14, x1 - xa - 10, 32, 6, "w", b=1, dark=0, bias=60)
        holes(sc, [(x, y0 + 16, Hh + 20.2) for x in range(int(xa + 40), int(x1) - 10, 60)], "z", 3.6, bias=59)
    sec = [[(XC, -Wd / 2, ZC + .2), (xb - t, -Wd / 2, ZC + .2), (xb - t, -Wd / 2 + t, ZC + .2), (XC, -Wd / 2 + t, ZC + .2)]]
    face(sc, [(XC + .2, -Wd / 2, ZC), (XC + .2, -Wd / 2 + t, ZC), (XC + .2, -Wd / 2 + t, Hh), (XC + .2, -80, Hh), (XC + .2, -80, Hh + 14), (XC + .2, -Wd / 2, Hh + 14)], "cut", bias=40)
    face(sc, [(XC + .2, -126, Hh + 14), (XC + .2, -94, Hh + 14), (XC + .2, -94, Hh + 20), (XC + .2, -126, Hh + 20)], "cut", bias=39)
    face(sc, sec[0], "cut", bias=99)
    # core-hole covers on the front wall
    for x in (-200, -60):
        MCYL(sc, (x, -Wd / 2, 66), (0, -1, 0), 22, 3, "dk", seg=24, bands=6, dark=0, spec=False, bias=-1)
        bolts(sc, ring_pts((x, -Wd / 2 - 3, 66), (0, -1, 0), 16, 4, math.pi / 4), (0, -1, 0), 2.4, bias=-2)
    # feet with levelling bolts (lock nut on top, pad underneath)
    for x in (xa + 30, xb - 30):
        for y in (-Wd / 2 - 16, Wd / 2 + 16):
            yy0 = -Wd / 2 - 34 if y < 0 else Wd / 2
            block(sc, x - 24, yy0, t, 48, 34, 26, "pt", ch=4, b=1.5, bias=700 if y > 0 else 20)
            cprism(sc, "z", t + 26, 8, [(x + 11 * math.cos(math.pi / 3 * k), y + 11 * math.sin(math.pi / 3 * k)) for k in range(6)], "w", 0, 1, dark=0, bias=700 if y > 0 else 10)
            MCYL(sc, (x, y, t + 34), "z", 6, 10, "w", seg=12, bands=4, spec=False, bias=700 if y > 0 else 9)
            MCYL(sc, (x, y, -22), "z", 6, 22 + t, "w", seg=12, bands=4, spec=False, bias=700 if y > 0 else 30)
            MCYL(sc, (x, y, -34), "z", 18, 12, "m", seg=20, bands=6, bias=700 if y > 0 else 30)
    sc.note((xa, -Wd / 2, 60), "外壁", "鋳物の箱形。断面を閉じてねじれに強くする")
    sc.note((70, 0, Hh - 6), "リブ（補強）", "格子状の壁で、軽くしながら剛性を上げる")
    sc.note((0, -110, Hh + 20), "案内面の取付面", "リニアガイドやすべり案内面を載せる精密な面")
    sc.note((xb - 30, -Wd / 2 - 16, -30), "レベリングボルト", "据付時に水平を出し、ねじれを抑える")
    sc.note((xb, 0, 60), "鋳物（FC材）", "振動を吸収しやすいねずみ鋳鉄が多い")


# =====================================================================================
@mt("thermal-displacement", az=-26, el=18)
def _(sc):
    """vertical machining centre with the spindle head cut open (front-right quadrant): hot bearings and
    motor inside, heat haze, exaggerated column tilt and temperature sensors."""
    Z = (0, 0, 1)
    block(sc, -252, -152, 0, 504, 304, 10, "dk", ch=8, b=0, dark=0, bias=900)
    block(sc, -260, -160, 10, 520, 320, 60, "pt", ch=10, b=3, bias=880)
    for y in (-110, -10):
        rail(sc, (-230, y, 70), "x", 460, "z", w=14, h=9, carriages=[(150, 36)], pitch=58, bias=600)
    block(sc, -180, -130, 82, 360, 170, 24, "m", ch=3, b=2, bias=500)
    seams(sc, [[(-172, y, 106.2), (172, y, 106.2)] for y in (-110, -70, -30, 10)], ((-172, -110, 106), (172, 10, 106.5)), "tslot", bias=499)
    block(sc, -60, -104, 106, 120, 92, 34, "alu", b=1.5, dark=0, bias=490)
    # column with Z rails, servo on top
    block(sc, -90, 60, 70, 180, 110, 380, "pt", ch=8, b=3, bias=700)
    for x in (-60, 60):
        rail(sc, (x, 60, 120), "z", 320, (0, -1, 0), w=14, h=8, carriages=[(184, 40), (244, 40)], bias=650)
    servo(sc, (0, 115, 450), "z", 44, 50, up=(0, -1, 0))
    # spindle head: back part, cut faces, spindle cartridge (hot bearings, motor), front-left part
    block(sc, -70, 0, 300, 140, 46, 120, "pt", ch=0, b=3, bias=300)
    face(sc, [(34, -.2, 300), (70, -.2, 300), (70, -.2, 420), (34, -.2, 420)], "cut", bias=299)
    face(sc, [(0, -.2, 300), (34, -.2, 300), (34, -.2, 420), (0, -.2, 420)], "dks4", bias=299.5)
    MCYL(sc, (0, 0, 300), Z, 30, 120, "w", seg=28, bands=10, bias=200)
    for z0, h_, m_ in ((304, 14, "h"), (322, 14, "h"), (356, 46, "cu"), (402, 12, "h")):
        MCYL(sc, (0, 0, z0), Z, 30.6, h_, m_, seg=28, bands=8, spec=m_ != "h", dark=0, bias=190)
    block(sc, -70, -40, 300, 70, 40, 120, "pt", ch=0, b=3, bias=100)
    face(sc, [(.2, -40, 300), (.2, -34, 300), (.2, -34, 420), (.2, -40, 420)], "cut", bias=99)
    face(sc, [(.2, -34, 300), (.2, 0, 300), (.2, 0, 420), (.2, -34, 420)], "dks3", bias=99.5)
    block(sc, -64, -41, 404, 58, 1, 10, "dk", b=0, dark=0, bias=95)
    # spindle nose, holder, tool
    MCYL(sc, (0, 0, 300), (0, 0, -1), 26, 14, "w", seg=24, bands=8, rings=(.5,))
    MCYL(sc, (0, 0, 286), (0, 0, -1), 18, 10, "w", r1=12, seg=20, bands=8)
    MCYL(sc, (0, 0, 276), (0, 0, -1), 8, 40, "t", seg=16, bands=6, dark=0)
    sc.raw(lambda s_: helix(s_.cam, (0, 0, 238), Z, 8, 28, 22, "hobt", per=10), ((-8, -8.5, 238), (8, -8, 266)), bias=-3)

    def heat(s_):
        p = s_.P((0, -40, 360))
        q = s_.P((0, 60, 200))
        o = '<ellipse class="heatg" cx="%s" cy="%s" rx="70" ry="54"/>' % (n(p[0]), n(p[1]))
        o += '<ellipse class="heatg2" cx="%s" cy="%s" rx="44" ry="80"/>' % (n(q[0]), n(q[1]))
        pts_ = [s_.P(v) for v in ((-90, 60, 70), (-90, 60, 450), (90, 60, 470), (90, 60, 70))]
        bend = [(x + (k in (1, 2)) * 18, y) for k, (x, y) in enumerate(pts_)]
        o += '<path class="ghost" d="M%s"/>' % " L".join("%s %s" % (n(x), n(y)) for x, y in bend)
        return o
    sc.raw(heat, ((-90, -40, 70), (90, 60, 470)), bias=-20)
    sc.axis((0, -40, 250), (0, -40, 220), "伸び", both=False, off=(20, 4))
    sc.axis((100, 60, 470), (140, 60, 470), "傾き", both=False, off=(0, -8))
    # temperature sensors: small probe bodies with a blue sensing tip
    sens = [(-90, 100, 200), (-90, 100, 380), (-70, -10, 380)]
    for p in sens:
        MCYL(sc, p, (-1, 0, 0), 4.5, 10, "dk", seg=10, bands=4, spec=False, dark=0, bias=-25)

    def dots(s_):
        o = ""
        for p in sens:
            q = s_.P((p[0] - 10, p[1], p[2]))
            o += '<circle class="sensor" cx="%s" cy="%s" r="4.5"/>' % (n(q[0]), n(q[1]))
        return o
    sc.raw(dots, ((-101, -10, 200), (-80, 100, 380)), bias=-30)
    sc.note((-20, -40, 400), "熱源（主軸・モータ）", "回転による発熱で主軸頭が膨張する")
    sc.note((0, -40, 236), "主軸の伸び", "Z方向の寸法がずれる")
    sc.note((90, 60, 470), "コラムの傾き", "前後の温度差で構造が反る（誇張して表示）")
    sc.note((-100, 100, 380), "温度センサ", "各部の温度を測り、NCが補正量を計算する")
    sc.note((-180, -130, 94), "テーブル・工作物", "環境温度の変化でも伸び縮みする")
