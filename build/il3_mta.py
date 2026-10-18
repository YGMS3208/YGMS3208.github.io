"""v3 machine-tool atlas drawings (shaded metal, detailed), part A: vertical-turning-lathe, turn-mill,
swiss-type-lathe, horizontal-machining-center, 5-axis-machining-center, double-column-machining-center,
transfer-machine. Re-registers the same slugs as il_mt.py with the same notes (text, count, order)."""
import math
from il_mt import mt
from il3_mtlib import *


# il3_mtlib.cprism/abox report a flat bbox along the extrusion axis when only one end is bevelled
# (bbox of rings[1] + rings[-2]); these local versions add the solid with its true bbox.
def cprism(sc, axis, t0, L, uv, mat="pt", b0=0.0, b1=0.0, dark=0, bias=0.0, fmat=None, crease=55):
    s, _ = cprism_svg(sc.cam, axis, t0, L, uv, mat, b0, b1, dark, fmat, crease)
    iu, iv, it = _UV[axis][0], _UV[axis][1], _IDX[axis]
    lo, hi = [0.0] * 3, [0.0] * 3
    lo[iu], hi[iu] = min(p[0] for p in uv), max(p[0] for p in uv)
    lo[iv], hi[iv] = min(p[1] for p in uv), max(p[1] for p in uv)
    lo[it], hi[it] = t0, t0 + L
    bb = (tuple(lo), tuple(hi))
    sc.add(s, bb, bias)
    return bb


def block(sc, x, y, z, sx, sy, sz, mat="pt", ch=0.0, b=2.0, dark=1, bias=0.0, b0=0.0):
    return cprism(sc, "z", z, sz, rr(x, y, x + sx, y + sy, ch), mat, b0, b, dark, bias)


def tcover(sc, P0, ax, L, w, h, segs=4, step=2.0, nm="z", mat="w", bias=0.0):
    """telescopic way cover (as il3_mtlib.tcover, largest shell at the far end), true bboxes."""
    a, m, s = _frame(ax, nm)
    Ls = L / segs
    for k in range(segs):
        g = step * k
        ww, hh = w / 2 + g, h + g
        sec = [(-ww, 0), (ww, 0), (ww, hh * .62), (ww - ww * .22, hh), (-ww + ww * .22, hh), (-ww, hh * .62)]
        c, t0, LL, uv = _sec(lin(P0, (k * Ls, a)) if _ax_char(a)[1] > 0 else lin(P0, ((k + 1) * Ls, a)), a, m, s, Ls, sec)
        bl = (0.0, 1.2) if _ax_char(a)[1] > 0 else (1.2, 0.0)
        cprism(sc, c, t0, LL, uv, mat, bl[0], bl[1], dark=1, bias=bias)


def _rtslots(tc, z, angs, r0, r1):
    """radial T-slot lines on a round table top."""
    def f(s_):
        ln = ""
        for a in angs:
            c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
            p, q = s_.P((tc[0] + r0 * c, tc[1] + r0 * s, z)), s_.P((tc[0] + r1 * c, tc[1] + r1 * s, z))
            ln += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1]))
        return '<path class="tslot" d="%s"/>' % ln
    return f


def _xslots(x0, x1, ys, z):
    """straight T-slot lines along x on a table top."""
    def f(s_):
        ln = ""
        for y in ys:
            p, q = s_.P((x0, y, z)), s_.P((x1, y, z))
            ln += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(q[0]), n(q[1]))
        return '<path class="tslot" d="%s"/>' % ln
    return f


# =====================================================================================
@mt("vertical-turning-lathe", az=-30, el=24)
def _(sc):
    tx, ty = -20, -70                                   # table centre
    # base (toe kick + casting) with cover seams
    block(sc, -272, -252, 0, 544, 484, 12, "dk", ch=10, b=0, dark=0, bias=950)
    block(sc, -280, -260, 12, 560, 500, 78, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-120, -260.2, 20), (-120, -260.2, 84)], [(140, -260.2, 20), (140, -260.2, 84)]], ((-120, -261, 20), (140, -260, 84)), "gr", bias=899)
    # table drive gearbox + motor at the back left
    block(sc, -272, 130, 90, 100, 100, 110, "dk", ch=6, b=2, dark=0, bias=700)
    finmotor(sc, (-222, 180, 200), (0, 0, 1), 30, 40, nf=12)
    # rotary table (chuck table) with radial T-slots and four jaws
    MCYL(sc, (tx, ty, 90), (0, 0, 1), 198, 8, "dk", seg=56, bands=14, bias=520)
    MCYL(sc, (tx, ty, 98), (0, 0, 1), 190, 30, "m", seg=56, bands=14, bias=510, rings=(.5,))
    sc.raw(_rtslots((tx, ty), 128.2, (0, 90, 180, 270), 40, 186), ((tx - 186, ty - 186, 128), (tx + 186, ty + 186, 128.5)), bias=505)
    for k in range(4):
        a = 45 + 90 * k
        radial(sc, "z", 128, 8, (tx, ty), a, 148, 192, 36, "dk", b=.8, dark=0)
        radial(sc, "z", 136, 26, (tx, ty), a, 150, 186, 26, "w", b=1.2)
    # work: large flange with a hub, bolt holes
    MRING(sc, (tx, ty, 128), (0, 0, 1), 148, 30, 28, "w", seg=56, dark=0, rings=(.5,))
    holes(sc, ring_pts((tx, ty, 156.1), (0, 0, 1), 124, 8, math.pi / 8), "z", 6)
    MRING(sc, (tx, ty, 156), (0, 0, 1), 100, 30, 38, "w", seg=48, dark=0)
    # column with guides for the cross rail, elevating servo on top, name band
    block(sc, -140, 160, 90, 240, 110, 520, "pt", ch=10, b=3, bias=300)
    for x in (-110, 70):
        rail(sc, (x, 160, 100), "z", 500, (0, -1, 0), w=16, h=8, bias=290)
    block(sc, -80, 158.6, 566, 120, 1.4, 22, "dk", b=0, dark=0, bias=289)
    servo(sc, (-20, 215, 610), "z", 34, 44, up=(0, -1, 0))
    # cross rail with X guides, screw and servo
    block(sc, -280, 96, 400, 500, 54, 76, "pt", ch=6, b=3, bias=200)
    for z in (412, 464):
        rail(sc, (-270, 96, z), "x", 480, (0, -1, 0), w=14, h=8, bias=190)
    ballscrew(sc, (-266, 91, 438), "x", 472, r=4, supports=False, nm=(0, -1, 0), bias=190)
    servo(sc, (220, 123, 438), "x", 36, 46)
    # saddle, ram, tool holder, tool
    block(sc, -80, 8, 376, 120, 78, 124, "pt", ch=6, b=3)
    seams(sc, [[(-60, 7.8, 390), (-60, 7.8, 486)], [(20, 7.8, 390), (20, 7.8, 486)]], ((-60, 7, 390), (20, 8, 486)), "gr", bias=-1)
    block(sc, -48, -48, 236, 56, 56, 284, "pt", ch=4, b=2.5)
    block(sc, -44, -49.4, 252, 48, 1.4, 16, "dk", b=0, dark=0, bias=-1)
    servo(sc, (-20, -20, 520), "z", 28, 36, up=(0, -1, 0))
    MCYL(sc, (-20, -20, 236), (0, 0, -1), 22, 10, "w", seg=24)
    block(sc, -32, -34, 206, 24, 28, 20, "w", b=1.5)
    block(sc, -27, -38, 194, 14, 18, 12, "t", b=0, dark=0)
    seams(sc, [[(30, 8, 384), (30, -36, 300), (-14, -44, 214)]], ((-14, -44, 214), (30, 8, 384)), "pipe", bias=-3)
    sc.rot((tx, ty, 132), (0, 0, 1), 222, "", 200, 320)
    sc.axis((-250, 80, 500), (-110, 80, 500), "X")
    sc.axis((60, -60, 230), (60, -60, 360), "Z", off=(14, 0))
    sc.note((tx - 120, ty - 120, 115), "テーブル（チャック）", "工作物を載せて回す")
    sc.note((tx + 70, ty - 110, 160), "工作物", "大径で重い円盤・リング状の部品")
    sc.note((-20, -48, 320), "ラム", "刃物台を上下（Z）に動かす")
    sc.note((-20, -38, 200), "工具", "バイトで端面・内外径を削る")
    sc.note((-200, 96, 470), "クロスレール", "刃物台を左右（X）に案内する横けた")
    sc.note((-20, 160, 580), "コラム", "クロスレールを支える柱")
    sc.note((200, -260, 40), "ベッド", "テーブルとコラムを支える土台")


# =====================================================================================
@mt("turn-mill", az=-26, el=22)
def _(sc):
    yc, zc = -40, 210
    # base, bed, sub-spindle guides and screw on the bed top
    block(sc, -310, -120, 0, 620, 240, 12, "dk", ch=8, b=0, dark=0, bias=950)
    block(sc, -320, -130, 12, 640, 260, 52, "pt", ch=10, b=3, bias=920)
    block(sc, -310, -112, 64, 620, 224, 86, "pt", ch=6, b=2.5, bias=800)
    seams(sc, [[(-60, -112.2, 72), (-60, -112.2, 144)], [(150, -112.2, 72), (150, -112.2, 144)]], ((-60, -113, 72), (150, -112, 144)), "gr", bias=799)
    for y in (-84, 20):
        rail(sc, (-40, y, 150), "x", 350, "z", w=14, h=9, bias=600)
    ballscrew(sc, (-40, -32, 156), "x", 350, r=5, supports=False, bias=600)
    # main headstock: casting, name band, motor, chuck with jaws, work
    block(sc, -300, -118, 150, 104, 200, 180, "pt", ch=8, b=3, bias=500)
    block(sc, -292, -119.6, 296, 88, 1.6, 22, "dk", b=0, dark=0, bias=495)
    finmotor(sc, (-300, 40, 282), (-1, 0, 0), 28, 40, nf=12)
    MCYL(sc, (-196, yc, zc), (1, 0, 0), 54, 10, "w", bias=-10, seg=40)
    MCYL(sc, (-186, yc, zc), (1, 0, 0), 70, 38, "m", bias=-20, seg=40, rings=(.22,))
    bolts(sc, ring_pts((-148, yc, zc), (1, 0, 0), 54, 3, math.radians(-30)), (1, 0, 0), 4, bias=-25)
    for ph, bi in ((90, -60), (210, -90), (330, -30)):
        radial(sc, "x", -148, 6, (yc, zc), ph, 28, 68, 20, "dk", b=.8, dark=0, bias=bi)
        radial(sc, "x", -142, 16, (yc, zc), ph, 35, 66, 15, "w", b=1.2, bias=bi - 1)
    MCYL(sc, (-148, yc, zc), (1, 0, 0), 34, 118, "w", bias=-40, dark=0, rings=(.97,))
    MCYL(sc, (-30, yc, zc), (1, 0, 0), 26, 64, "w", bias=-40, dark=0)
    # sub spindle (faces the main spindle) on its guides
    block(sc, 200, -118, 165, 100, 170, 150, "pt", ch=8, b=3, bias=-30)
    block(sc, 208, -119.6, 284, 84, 1.6, 20, "dk", b=0, dark=0, bias=-31)
    MCYL(sc, (200, yc, zc), (-1, 0, 0), 44, 10, "w", bias=-35, seg=36)
    MCYL(sc, (190, yc, zc), (-1, 0, 0), 50, 26, "m", bias=-36, seg=36, rings=(.25,))
    for ph, bi in ((90, -40), (210, -44), (330, -38)):
        radial(sc, "x", 158, 6, (yc, zc), ph, 20, 48, 18, "dk", b=.6, dark=0, bias=bi)
        radial(sc, "x", 146, 12, (yc, zc), ph, 25, 46, 13, "w", b=1, bias=bi - 1)
    # X column bed with guides, column, Y guides, ram (Y slide), servo on top
    block(sc, -190, 56, 150, 380, 56, 40, "pt", ch=4, b=2, bias=420)
    rail(sc, (-185, 72, 190), "x", 370, "z", w=12, h=8, carriages=[(155, 40), (255, 40)], bias=410)
    rail(sc, (-185, 100, 190), "x", 370, "z", w=12, h=8, bias=412)
    block(sc, -40, 66, 198, 150, 90, 222, "pt", ch=8, b=3, bias=300)
    for x in (-34, 104):
        rail(sc, (x, 66, 206), "z", 208, (0, -1, 0), w=12, h=6, bias=290)
    block(sc, -20, -12, 320, 110, 72, 100, "pt", ch=6, b=3, bias=150)
    servo(sc, (35, 111, 420), "z", 34, 40, up=(0, -1, 0))
    # B-axis swivel disc and the milling head turned 35 deg (spindle points down-left at the work)
    MCYL(sc, (35, -12, 370), (0, -1, 0), 56, 10, "dk", seg=36, bias=140)
    ca, sa = math.cos(math.radians(35)), math.sin(math.radians(35))
    A2, B2 = (-sa, -ca), (ca, -sa)                     # spindle axis / across, in the (x, z) plane

    def hp(t, w):
        return (35 + t * A2[0] + w * B2[0], 370 + t * A2[1] + w * B2[1])
    cprism(sc, "y", -82, 60, [hp(-50, -34), hp(-40, -44), hp(70, -44), hp(80, -34), hp(80, 34), hp(70, 44), hp(-40, 44), hp(-50, 34)],
           "pt", 3, 0, dark=1, bias=-140)
    cprism(sc, "y", -83.4, 1.4, [hp(-40, -30), hp(-12, -30), hp(-12, 30), hp(-40, 30)], "dk", dark=0, bias=-141)
    A3 = (-sa, 0, -ca)
    s0 = hp(80, 0)
    O = (s0[0], -52, s0[1])
    for L, r, r1, mat, dk, bi, kw in ((14, 30, None, "w", 1, -130, {"rings": (.5,)}), (10, 22, None, "w", 0, -120, {}),
                                      (18, 18, 12, "w", 1, -110, {}), (34, 6, None, "t", 0, -100, {"seg": 16, "bands": 6})):
        MCYL(sc, O, A3, r, L, mat, bias=bi, dark=dk, r1=r1, **kw)
        O = add3(O, A3, L)
    T0 = add3(O, A3, -34)

    def flutes(s_):
        return helix(s_.cam, add3(T0, A3, 8), A3, 6, 26, 18, "hobt", per=12)
    sc.raw(flutes, bbox([add3(T0, A3, 8), O]), bias=-101)
    sc.rot((35, -90, 370), (0, 1, 0), 70, "B", 200, 330)
    sc.axis((-120, -130, 440), (60, -130, 440), "Z")
    sc.note((-250, -60, 330), "主軸（第1主軸）", "工作物を回して旋削する")
    sc.note((250, -118, 300), "第2主軸", "工作物を持ち替えて裏側も加工する")
    sc.note((s0[0] - 4, -80, s0[1] - 8), "ミーリング主軸", "回転工具で穴あけ・フライス加工をする")
    sc.note((75, -22, 408), "B軸", "主軸頭を傾けて斜めの穴や面を加工する")
    sc.note((-60, yc - 34, zc), "工作物", "1台で旋削とミーリングを済ませる")
    sc.note((-120, -112, 110), "ベッド", "主軸台とコラムを支える土台")


# =====================================================================================
@mt("swiss-type-lathe", az=-24, el=22)
def _(sc):
    yc, zc = -30, 210
    block(sc, -330, -110, 0, 660, 220, 12, "dk", ch=8, b=0, dark=0, bias=950)
    block(sc, -340, -120, 12, 680, 240, 58, "pt", ch=10, b=3, bias=920)
    block(sc, -330, -100, 70, 660, 200, 80, "pt", ch=6, b=2.5, bias=800)
    seams(sc, [[(-200, -100.2, 78), (-200, -100.2, 144)], [(130, -100.2, 78), (130, -100.2, 144)]], ((-200, -101, 78), (130, -100, 144)), "gr", bias=799)
    # sliding headstock on its Z guides, screw between them
    for y in (-60, 20):
        rail(sc, (-320, y, 150), "x", 260, "z", w=14, h=9, carriages=[(30, 40), (100, 40)], bias=700)
    ballscrew(sc, (-320, -20, 156), "x", 250, r=5, supports=False, bias=690)
    block(sc, -300, -90, 166, 150, 170, 110, "pt", ch=8, b=3, bias=300)
    block(sc, -290, -91.4, 250, 130, 1.4, 16, "dk", b=0, dark=0, bias=295)
    MCYL(sc, (-150, yc, zc), (1, 0, 0), 30, 12, "w", seg=32, bias=-5)
    MCYL(sc, (-138, yc, zc), (1, 0, 0), 20, 14, "m", seg=24, rings=(.5,), bias=-6)
    # bar stock: from the bar feeder, through the spindle and the guide bushing
    MCYL(sc, (-470, yc, zc), (1, 0, 0), 9, 170, "w", seg=16, bands=6, dark=0, bias=850)
    MCYL(sc, (-124, yc, zc), (1, 0, 0), 9, 84, "w", seg=16, bands=6, dark=0, bias=-6)
    # guide bushing support (fixed) and bushing
    block(sc, -40, -100, 150, 60, 190, 150, "pt", ch=6, b=3, bias=200)
    MCYL(sc, (20, yc, zc), (1, 0, 0), 26, 8, "w", seg=28, bias=-10)
    MCYL(sc, (28, yc, zc), (1, 0, 0), 16, 10, "dk", seg=24, dark=0, rings=(.5,), bias=-12)
    MCYL(sc, (38, yc, zc), (1, 0, 0), 9, 16, "w", seg=16, bands=6, dark=0, bias=-14)
    MCYL(sc, (54, yc, zc), (1, 0, 0), 6, 10, "w", seg=14, bands=5, dark=0, spec=False, bias=-16)
    # gang tool slide: base, dark holder plate, a row of square-shank tools (first one cutting)
    block(sc, 34, -118, 150, 94, 56, 30, "pt", ch=4, b=2, bias=150)
    block(sc, 38, -114, 180, 86, 40, 16, "dk", b=1, dark=0, bias=140)
    for k in range(5):
        x0 = 42 + 16 * k
        block(sc, x0, -112, 196, 10, 52 if k else 62, 10, "w", b=.8, bias=-30)
    block(sc, 43, -50, 197, 8, 10, 8, "t", b=0, dark=0, bias=-32)
    # back spindle on its own guides
    for y in (-60, 20):
        rail(sc, (130, y, 150), "x", 190, "z", w=14, h=9, bias=600)
    block(sc, 200, -100, 166, 110, 180, 120, "pt", ch=8, b=3, bias=-10)
    block(sc, 208, -101.4, 258, 94, 1.4, 16, "dk", b=0, dark=0, bias=-11)
    MCYL(sc, (200, yc, zc), (-1, 0, 0), 26, 10, "w", seg=28, bias=-15)
    MCYL(sc, (190, yc, zc), (-1, 0, 0), 18, 12, "m", seg=24, rings=(.5,), bias=-16)
    sc.axis((-300, -110, 300), (-170, -110, 300), "Z")
    sc.axis((80, -170, 260), (80, -110, 200), "X", off=(14, 0))
    sc.note((-230, -90, 268), "主軸台（Z移動）", "棒材をつかんだまま前後に動き、Z送りをする")
    sc.note((14, -100, 284), "ガイドブッシュ", "刃物のすぐ近くで棒材を支え、たわみを防ぐ")
    sc.note((80, -114, 190), "くし刃刃物台", "工具を一列に並べ、X・Y方向に動かす")
    sc.note((250, -100, 260), "背面主軸", "切り離した部品を受け取り裏側を加工する")
    sc.note((-380, yc, zc), "棒材", "バーフィーダから送られる長い材料")
    sc.note((-200, -100, 110), "ベッド", "機械の土台")


# =====================================================================================
@mt("horizontal-machining-center", az=-36, el=24)
def _(sc):
    block(sc, -292, -322, 0, 584, 624, 12, "dk", ch=10, b=0, dark=0, bias=950)
    block(sc, -300, -330, 12, 600, 640, 68, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-120, -330.2, 20), (-120, -330.2, 74)], [(120, -330.2, 20), (120, -330.2, 74)]], ((-120, -331, 20), (120, -330, 74)), "gr", bias=899)
    # column bed with X guides (carriages visible under the column)
    block(sc, -260, 60, 80, 420, 230, 40, "pt", ch=6, b=2.5, bias=700)
    rail(sc, (-250, 145, 120), "x", 400, "z", w=16, h=10, carriages=[(105, 46), (349, 46)], bias=650)
    rail(sc, (-250, 245, 120), "x", 400, "z", w=16, h=10, bias=660)
    # column, Y guides, bellows above/below the head, Y servo
    block(sc, -150, 120, 137, 300, 150, 453, "pt", ch=12, b=3, bias=400)
    for x in (-100, 100):
        rail(sc, (x, 120, 150), "z", 430, (0, -1, 0), w=16, h=8, bias=350)
    bellows(sc, (-80, 104, 150), (80, 112, 280), "z", folds=8, bias=360)
    bellows(sc, (-80, 104, 430), (80, 112, 580), "z", folds=9, bias=360)
    servo(sc, (0, 195, 590), "z", 36, 44, up=(0, -1, 0))
    # spindle head + horizontal spindle, holder, end mill
    block(sc, -90, 30, 280, 180, 82, 150, "pt", ch=8, b=3, bias=200)
    block(sc, -80, 28.6, 404, 160, 1.4, 16, "dk", b=0, dark=0, bias=199)
    y = 30
    for L, r, r1, mat, dk, kw in ((12, 46, None, "pt", 1, {}), (12, 36, None, "w", 1, {"rings": (.5,)}), (8, 28, None, "w", 0, {}),
                                  (8, 24, None, "w", 0, {"rings": (.5,)}), (14, 18, 13, "w", 1, {}), (10, 12, None, "w", 1, {"seg": 20, "bands": 8}),
                                  (36, 8, None, "t", 0, {"seg": 18, "bands": 8})):
        MCYL(sc, (0, y, 355), (0, -1, 0), r, L, mat, dark=dk, r1=r1, bias=100, **kw)
        y -= L

    def flutes(s_):
        return helix(s_.cam, (0, -70, 355), (0, 1, 0), 8, 28, 22, "hobt", per=12)
    sc.raw(flutes, ((-8, -70, 347), (8, -42, 363)), bias=99)
    # Z guides on the bed, telescopic cover, saddle, B table, pallet
    for x in (-90, 90):
        rail(sc, (x, -240, 80), "y", 200, "z", w=16, h=10, carriages=[(40, 46)], bias=600)
    tcover(sc, (0, -40, 80), (0, 1, 0), 100, 190, 14, segs=3, step=2, bias=590)
    block(sc, -130, -245, 97, 260, 205, 40, "pt", ch=6, b=3, bias=500)
    MCYL(sc, (0, -140, 137), (0, 0, 1), 106, 6, "dk", seg=48, bias=480)
    MCYL(sc, (0, -140, 143), (0, 0, 1), 100, 22, "m", seg=48, bands=14, rings=(.5,), bias=470)
    block(sc, -90, -230, 165, 180, 180, 22, "m", ch=4, b=2, bias=460)
    # tombstone (angle-plate fixture) with parts on both faces
    block(sc, -60, -165, 187, 120, 60, 220, "m", ch=4, b=2, bias=300)
    for z in (225, 320):
        block(sc, -50, -185, z, 100, 20, 62, "alu", b=1.5, dark=0, bias=280)
        block(sc, -50, -105, z, 100, 30, 62, "alu", b=1.5, dark=0, bias=320)
        seams(sc, [[(-34, -185.2, z + 14), (34, -185.2, z + 14), (34, -185.2, z + 48), (-34, -185.2, z + 48), (-34, -185.2, z + 14)]],
              ((-34, -186, z + 14), (34, -185, z + 48)), "alus4", bias=279)
    bolts(sc, [(-40 + 20 * k, -165, 303.5) for k in range(5)], (0, -1, 0), 3.2, bias=279)
    # pallet changer with the next pallet
    block(sc, -120, -330, 80, 240, 80, 56, "dk", ch=6, b=2, dark=0, bias=150)
    MCYL(sc, (0, -290, 136), (0, 0, 1), 22, 14, "w", seg=24, bias=145)
    block(sc, -90, -325, 150, 180, 70, 18, "m", ch=4, b=2, bias=140)
    sc.raw(_xslots(-86, 86, (-310, -290, -270), 168.2), ((-86, -310, 168), (86, -270, 168.5)), bias=139)
    # chain tool magazine beside the column: frame + pots on a racetrack
    block(sc, 175, 170, 80, 110, 100, 420, "dk", ch=6, b=2, dark=0, bias=100)
    pots = [(202, 170, 150 + 30 * k) for k in range(11)] + [(258, 170, 150 + 30 * k) for k in range(11)]
    pots += [(230 + 28 * math.cos(math.radians(a)), 170, 450 + 28 * math.sin(math.radians(a))) for a in (45, 135)]
    pots += [(230 + 28 * math.cos(math.radians(a)), 170, 150 - 28 * math.sin(math.radians(a))) for a in (45, 135)]
    bolts(sc, pots, (0, -1, 0), 9, h=5, bias=99)
    sc.rot((0, -140, 175), (0, 0, 1), 130, "B", 200, 330)
    sc.axis((-250, 40, 480), (-110, 40, 480), "X")
    sc.axis((130, 40, 300), (130, 40, 420), "Y", off=(14, 0))
    sc.axis((200, -240, 120), (200, -100, 120), "Z", off=(14, 0))
    sc.note((0, 0, 383), "主軸（水平）", "工具を水平に向けて回す。切りくずが下に落ちる")
    sc.note((-150, 120, 560), "コラム", "主軸頭を上下（Y）に案内する")
    sc.note((-95, -170, 154), "回転テーブル（B軸）", "割り出して4面を順に加工する")
    sc.note((-60, -165, 400), "イケール（治具）", "複数の工作物を立てて固定する")
    sc.note((-90, -320, 168), "パレットチェンジャ", "加工中に次のパレットを段取りする")
    sc.note((230, 170, 470), "工具マガジン", "チェーン式で多数の工具を収納する")
    sc.note((260, -330, 40), "ベッド", "コラムとテーブルを支える土台")


# =====================================================================================
@mt("5-axis-machining-center", az=-32, el=24)
def _(sc):
    cy, cz = -90, 230                                   # A (tilt) axis: along x through (cy, cz)
    block(sc, -252, -222, 0, 504, 454, 12, "dk", ch=10, b=0, dark=0, bias=950)
    block(sc, -260, -230, 12, 520, 470, 78, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-90, -230.2, 20), (-90, -230.2, 84)], [(90, -230.2, 20), (90, -230.2, 84)]], ((-90, -231, 20), (90, -230, 84)), "gr", bias=899)
    # trunnion supports, A drive (bearing cap + finned motor) on the right
    block(sc, -230, -200, 90, 60, 220, 190, "pt", ch=6, b=3, bias=300)
    block(sc, 170, -200, 90, 60, 220, 190, "pt", ch=6, b=3, bias=-10)
    MCYL(sc, (230, cy, cz), (1, 0, 0), 46, 12, "w", seg=36, bias=-12)
    bolts(sc, ring_pts((242, cy, cz), (1, 0, 0), 38, 6, math.pi / 6), (1, 0, 0), 3, bias=-13)
    finmotor(sc, (242, cy, cz), (1, 0, 0), 30, 44, nf=12, bias=-14)
    # cradle: two side discs + curved bottom plate (machined grey)
    arm = [(cy + 80 * math.cos(math.radians(a)), cz + 80 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    arm += [(cy - 80, cz - 60), (cy - 56, cz - 84), (cy + 56, cz - 84), (cy + 80, cz - 60)]
    cprism(sc, "x", -170, 20, arm, "m", 2, 2, dark=1, bias=250)
    cprism(sc, "x", 150, 20, arm, "m", 2, 2, dark=1, bias=40)
    cprism(sc, "x", -150, 300, [(cy - 80, cz - 22), (cy + 80, cz - 22), (cy + 80, cz - 60), (cy + 56, cz - 84), (cy - 56, cz - 84), (cy - 80, cz - 60)],
           "m", 0, 0, dark=1, bias=200)
    # C table with T-slots
    MCYL(sc, (0, cy, cz - 22), (0, 0, 1), 94, 8, "dk", seg=48, bias=160)
    MCYL(sc, (0, cy, cz - 14), (0, 0, 1), 90, 18, "m", seg=48, bands=14, rings=(.5,), bias=150)
    sc.raw(_rtslots((0, cy), cz + 4.2, range(0, 360, 45), 60, 86), ((-86, cy - 86, cz + 4), (86, cy + 86, cz + 4.5)), bias=149)
    # work: impeller (disc, conical hub, swept blades)
    MCYL(sc, (0, cy, cz + 4), (0, 0, 1), 58, 10, "alu", seg=40, dark=0, bias=60)
    MCYL(sc, (0, cy, cz + 14), (0, 0, 1), 30, 40, "alu", r1=12, seg=32, dark=0, bias=50)
    for k in range(9):
        a0 = math.radians(40 * k + 10)
        a1 = a0 + math.radians(24)
        p, q = (30 * math.cos(a0), cy + 30 * math.sin(a0)), (56 * math.cos(a1), cy + 56 * math.sin(a1))
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        nx, ny = -(q[1] - p[1]) / L * 2.4, (q[0] - p[0]) / L * 2.4
        cprism(sc, "z", cz + 14, 22, [(p[0] - nx, p[1] - ny), (q[0] - nx, q[1] - ny), (q[0] + nx, q[1] + ny), (p[0] + nx, p[1] + ny)], "alu", 0, .8, dark=0, bias=55)
    # column, Z guides, Y ram, spindle head, servo
    block(sc, -120, 120, 90, 240, 120, 460, "pt", ch=10, b=3, bias=400)
    for x in (-80, 80):
        rail(sc, (x, 120, 110), "z", 430, (0, -1, 0), w=16, h=8, bias=350)
    servo(sc, (0, 180, 550), "z", 34, 40, up=(0, -1, 0))
    block(sc, -60, -30, 410, 120, 142, 90, "pt", ch=6, b=3, bias=200)
    block(sc, -70, -150, 366, 140, 120, 150, "pt", ch=8, b=3, bias=100)
    block(sc, -62, -151.4, 482, 124, 1.4, 16, "dk", b=0, dark=0, bias=99)
    finmotor(sc, (0, cy, 516), (0, 0, 1), 30, 34, nf=12)
    z = 366
    for L, r, r1, mat, dk, kw in ((10, 46, None, "pt", 1, {}), (12, 36, None, "w", 1, {"rings": (.5,)}), (8, 28, None, "w", 0, {}),
                                  (8, 22, None, "w", 0, {"rings": (.5,)}), (14, 16, 11, "w", 1, {}), (8, 10, None, "w", 1, {"seg": 20, "bands": 8}),
                                  (20, 5, None, "t", 0, {"seg": 14, "bands": 6})):
        MCYL(sc, (0, cy, z), (0, 0, -1), r, L, mat, dark=dk, r1=r1, bias=20, **kw)
        z -= L
    seams(sc, [[(44, -140, 366), (44, -130, 344), (12, -104, 300)]], ((12, -140, 300), (44, -104, 366)), "pipe", bias=0)
    sc.rot((-260, cy, cz), (1, 0, 0), 110, "A", 200, 320)
    sc.rot((0, cy, cz + 4), (0, 0, 1), 112, "C", 200, 330)
    sc.axis((90, -90, 380), (90, -90, 480), "Z", off=(14, 0))
    sc.note((70, -50, 440), "主軸", "工具を回す。X・Y・Zの3軸で動く")
    sc.note((-160, cy - 80, cz - 40), "傾斜テーブル（A軸）", "工作物を前後に傾ける")
    sc.note((88, cy, cz - 4), "回転テーブル（C軸）", "工作物を水平に回す")
    sc.note((30, cy - 30, cz + 28), "工作物", "インペラなど曲面の多い部品")
    sc.note((-120, 120, 520), "コラム", "主軸頭を支える柱")
    sc.note((200, -230, 40), "ベッド", "機械の土台")


# =====================================================================================
@mt("double-column-machining-center", az=-34, el=24)
def _(sc):
    block(sc, -352, -122, 0, 704, 244, 12, "dk", ch=10, b=0, dark=0, bias=950)
    block(sc, -360, -130, 12, 720, 260, 58, "pt", ch=12, b=3, bias=900)
    seams(sc, [[(-120, -130.2, 20), (-120, -130.2, 64)], [(120, -130.2, 20), (120, -130.2, 64)]], ((-120, -131, 20), (120, -130, 64)), "gr", bias=899)
    # table (X) with T-slots
    block(sc, -340, -110, 70, 680, 220, 40, "m", ch=4, b=2, bias=800)
    sc.raw(_xslots(-336, 336, (-88, -44, 0, 44, 88), 110.2), ((-336, -88, 110), (336, 88, 110.5)), bias=790)
    # work: press-die block with a raised, pocketed face, guide-post holes, clamps
    block(sc, -100, -90, 110, 350, 180, 70, "w", ch=4, b=2, bias=500)
    block(sc, 60, -60, 180, 180, 120, 22, "w", ch=6, b=1.5, bias=490)
    pk = [(110, -36), (170, -36), (186, -20), (186, 20), (170, 36), (110, 36), (94, 20), (94, -20), (110, -36)]
    seams(sc, [[(x, y, 202.2) for x, y in pk]], ((94, -36, 202), (186, 36, 202.5)), "gr", bias=489)
    holes(sc, [(-76, -66, 180.1), (-76, 66, 180.1), (36, -66, 180.1), (36, 66, 180.1)], "z", 9)
    for x in (-60, 170):
        block(sc, x, -112, 110, 30, 22, 44, "dk", ch=2, b=1, dark=0, bias=480)
    # portal: two columns, crown, W guides on the columns
    block(sc, -40, 160, 0, 90, 80, 470, "pt", ch=8, b=3, bias=600)
    block(sc, -40, -240, 0, 90, 80, 470, "pt", ch=8, b=3, bias=-200)
    block(sc, -40, -240, 470, 90, 480, 30, "pt", ch=4, b=2, bias=150)
    for y in (-200, 200):
        rail(sc, (50, y, 80), "z", 390, (1, 0, 0), w=16, h=8, bias=-150 if y < 0 else 550)
    # cross rail with Y guides, screw and servo
    block(sc, 58, -250, 380, 70, 500, 80, "pt", ch=6, b=3, bias=100)
    for z in (392, 444):
        rail(sc, (128, -240, z), "y", 480, (1, 0, 0), w=14, h=8, bias=90)
    ballscrew(sc, (132, -236, 418), "y", 472, r=4, supports=False, nm=(1, 0, 0), bias=90)
    servo(sc, (93, -250, 420), (0, -1, 0), 34, 44)
    # saddle, ram, spindle, ball end mill
    block(sc, 136, -60, 340, 50, 120, 150, "pt", ch=6, b=3, bias=-10)
    block(sc, 186, -28, 262, 56, 56, 258, "pt", ch=4, b=2.5, bias=-20)
    block(sc, 190, -29.4, 440, 48, 1.4, 16, "dk", b=0, dark=0, bias=-21)
    servo(sc, (214, 0, 520), "z", 30, 36, up=(0, -1, 0))
    z = 262
    for L, r, r1, mat, dk, kw in ((8, 26, None, "w", 1, {"rings": (.5,)}), (8, 20, None, "w", 0, {}), (12, 15, 10, "w", 1, {}),
                                  (8, 9, None, "w", 1, {"seg": 18, "bands": 6}), (24, 7, None, "t", 0, {"seg": 16, "bands": 6})):
        MCYL(sc, (214, 0, z), (0, 0, -1), r, L, mat, dark=dk, r1=r1, bias=-30, **kw)
        z -= L
    sc.axis((-330, -130, 160), (-170, -130, 160), "X")
    sc.axis((270, -200, 470), (270, -60, 470), "Y", off=(14, 0))
    sc.axis((270, 40, 260), (270, 40, 360), "Z", off=(14, 0))
    sc.note((-80, -90, 170), "工作物", "プレス金型など大きく重い部品")
    sc.note((-300, -110, 110), "テーブル", "工作物を載せて前後（X）に動く")
    sc.note((5, -240, 300), "コラム（左右2本）", "門の柱。クロスレールを両側で支える")
    sc.note((93, 200, 460), "クロスレール", "サドルを左右（Y）に案内する横けた")
    sc.note((214, -28, 330), "ラム", "主軸を上下（Z）に動かす")
    sc.note((214, -6, 236), "主軸・工具", "ラム先端で工具を回す")
    sc.note((300, -130, 30), "ベッド", "テーブルを支える長い土台")


# =====================================================================================
@mt("transfer-machine", az=-30, el=26)
def _(sc):
    block(sc, -372, -112, 0, 744, 204, 12, "dk", ch=8, b=0, dark=0, bias=950)
    block(sc, -380, -120, 12, 760, 220, 78, "pt", ch=10, b=3, bias=900)
    seams(sc, [[(x, -120.2, 20), (x, -120.2, 84)] for x in (-200, 0, 200)], ((-200, -121, 20), (200, -120, 84)), "gr", bias=899)
    # transfer bar, pallets and work (aluminium housings)
    block(sc, -380, -62, 90, 760, 64, 14, "m", b=1.5, bias=800)
    xs = [-300, -100, 100, 300]
    for x in xs:
        block(sc, x - 50, -84, 104, 100, 94, 14, "m", ch=3, b=1.5, bias=700)
        block(sc, x - 38, -76, 118, 76, 76, 56, "alu", b=1.5, dark=0, bias=300)
    holes(sc, [(x + d, -38, 174.1) for x in xs[1:] for d in (-24, 24)], "z", 5, cls="alus4", bias=290)
    # horizontal units: wing base with guides, slide unit, drive motor, multi-spindle head with drills
    for x in xs[:3]:
        block(sc, x - 70, 110, 0, 140, 190, 120, "pt", ch=6, b=3, bias=600)
        for dx in (-40, 40):
            rail(sc, (x + dx, 110, 120), "y", 190, "z", w=12, h=8, bias=590)
        block(sc, x - 60, 50, 128, 120, 150, 96, "pt", ch=6, b=3, bias=200)
        finmotor(sc, (x, 200, 176), (0, 1, 0), 28, 44, nf=8, bias=180)
        block(sc, x - 50, 18, 124, 100, 32, 86, "dk", ch=3, b=1.5, dark=0, bias=150)
        for i in (-1, 0, 1):
            for zz in (138, 162):
                MCYL(sc, (x + 24 * i, 18, zz), (0, -1, 0), 7, 6, "w", seg=10, bands=3, spec=False, bias=120)
                MCYL(sc, (x + 24 * i, 12, zz), (0, -1, 0), 3.5, 24, "t", seg=8, bands=2, spec=False, dark=0, bias=330)
    # vertical unit at the last station
    block(sc, 240, 104, 0, 120, 110, 470, "pt", ch=8, b=3, bias=400)
    for x in (262, 338):
        rail(sc, (x, 104, 200), "z", 260, (0, -1, 0), w=14, h=8, bias=390)
    servo(sc, (300, 159, 470), "z", 30, 36, up=(0, -1, 0))
    block(sc, 250, -80, 250, 100, 176, 130, "pt", ch=6, b=3, bias=100)
    block(sc, 256, -81.4, 350, 88, 1.4, 16, "dk", b=0, dark=0, bias=99)
    block(sc, 256, -74, 226, 88, 80, 24, "dk", ch=3, b=1.5, dark=0, bias=60)
    for i in (-1, 0, 1):
        MCYL(sc, (300 + 24 * i, -38, 226), (0, 0, -1), 7, 6, "w", seg=12, bands=4, spec=False, bias=40)
        MCYL(sc, (300 + 24 * i, -38, 220), (0, 0, -1), 3.5, 50, "t", seg=10, bands=3, spec=False, dark=0, bias=30)
    sc.axis((-360, -120, 200), (-200, -120, 200), "搬送", both=False)
    sc.note((-100, 50, 224), "加工ユニット", "1つの工程だけを受け持つ専用の加工部")
    sc.note((-100, 18, 200), "多軸ヘッド", "複数の工具を同時に回して一度に穴をあける")
    sc.note((-300, -76, 170), "工作物", "パレットに載って順番に送られる")
    sc.note((-200, -62, 100), "搬送装置", "全ステーションの工作物を同時に1ピッチ送る")
    sc.note((300, -80, 370), "立形ユニット", "上から加工するステーション")
    sc.note((330, -120, 40), "ベース", "ライン全体の土台")
