"""v3 machine-tool atlas drawings (shaded metal, detailed): cnc-lathe, vertical-machining-center, spindle.
Re-registers the same slugs as il_mt.py with the same notes (text, count, order)."""
import math
from il_mt import mt, on_slope, arc_shell
from il3_mtlib import *


# =====================================================================================
@mt("cnc-lathe", az=-24, el=21)
def _(sc):
    # slant bed at 30 deg: section point SP(s, h) = s along the slope from its front edge, h above it
    S0, E, NM = (-112, 89.6), (math.cos(math.radians(30)), math.sin(math.radians(30))), (-.5, math.cos(math.radians(30)))
    sl = (0, NM[0], NM[1])

    def SP(s_, h=0.0):
        return (S0[0] + s_ * E[0] + h * NM[0], S0[1] + s_ * E[1] + h * NM[1])

    def slab(x0, L, s0, s1, h0, h1, mat="pt", b=2, bias=0.0, dark=1):
        return cprism(sc, "x", x0, L, [SP(s0, h0), SP(s1, h0), SP(s1, h1), SP(s0, h1)], mat, b, b, dark=dark, bias=bias)
    yc, zc = -44, 212                                    # spindle centre line (72 above the slope)
    # base (dark toe kick), bed under the headstock, slant bed
    block(sc, -298, -120, 0, 596, 240, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -310, -130, 12, 620, 260, 52, "dk", ch=10, b=3, dark=0, bias=900)
    seams(sc, [[(-60, -130.2, 20), (-60, -130.2, 58)], [(150, -130.2, 20), (150, -130.2, 58)]], ((-60, -131, 20), (150, -130, 58)), "mgrid")
    block(sc, -300, -112, 64, 112, 224, 86, "pt", ch=6, b=2.5, bias=800)
    cprism(sc, "x", -188, 488, [(-112, 64), (112, 64), SP(258.6), S0], "pt", 3, 3, dark=1, bias=700)
    # linear guides with carriages under the saddle, ball screw between them
    for s_ in (55, 185):
        rail(sc, (-180, *SP(s_)), "x", 470, sl, w=16, h=10, carriages=[(250, 40)], bias=600)
    tcover(sc, (-186, *SP(120)), "x", 138, 186, 20, segs=4, step=2.5, nm=sl, bias=580)
    ya, za = SP(120, 13)
    ballscrew(sc, (-60, ya, za), "x", 350, r=6, nut=120, nut_len=34, nm=sl, bias=590)
    servo(sc, (300, ya, za), "x", 36, 54, up=sl)
    # headstock + spindle motor + nameplate band
    block(sc, -300, -118, 150, 112, 200, 190, "pt", ch=8, b=3, bias=500)
    block(sc, -292, -119.6, 296, 96, 1.6, 26, "dk", b=0, dark=0, bias=495)
    finmotor(sc, (-300, 40, 290), (-1, 0, 0), 30, 46, nf=12)
    # spindle nose, chuck, jaws, work
    MCYL(sc, (-188, yc, zc), (1, 0, 0), 56, 12, "w", bias=-10, seg=40)
    MCYL(sc, (-176, yc, zc), (1, 0, 0), 76, 44, "m", bias=-20, seg=40, bands=12, rings=(.22,))
    bolts(sc, ring_pts((-132, yc, zc), (1, 0, 0), 58, 3, math.radians(-30)), (1, 0, 0), 4.2, bias=-25)
    holes(sc, [(-132, yc, zc)], (1, 0, 0), 14, bias=-24)
    for ph, bi in ((90, -60), (210, -90), (330, -30)):
        radial(sc, "x", -132, 6, (yc, zc), ph, 30, 74, 22, "dk", b=.8, dark=0, bias=bi)
        radial(sc, "x", -126, 18, (yc, zc), ph, 37, 72, 16, "w", b=1.2, bias=bi - 1)
    MCYL(sc, (-132, yc, zc), (1, 0, 0), 36, 118, "w", bias=-40, dark=0, rings=(.96,))
    MCYL(sc, (-14, yc, zc), (1, 0, 0), 26, 62, "w", bias=-40, dark=0)
    # tailstock on the slant, quill and live centre
    cprism(sc, "x", 180, 90, [SP(30, 18), SP(170, 18), (SP(170, 18)[0], 262), (SP(30, 18)[0], 262)], "pt", 3, 3, dark=1, bias=-30)
    MCYL(sc, (180, yc, zc), (-1, 0, 0), 16, 50, "w", bias=-35)
    MCYL(sc, (130, yc, zc), (-1, 0, 0), 11, 16, "w", r1=2, bias=-36, seg=20)
    # saddle, cross slide and turret housing (all square to the slope), turret with tool holders
    slab(-46, 168, 30, 212, 18, 34, bias=100)
    slab(-40, 156, 118, 250, 34, 50, bias=95)
    slab(-36, 110, 178, 254, 50, 138, bias=90)
    seams(sc, [[(-36, *SP(178, 60)), (-36, *SP(178, 128))]], ((-37, -60, 150), (-36, 60, 300)), "gr", bias=89)
    ty, tz = SP(240, 112)
    R = 62
    poly = [(ty + R * math.cos(2 * math.pi * k / 12 + math.pi / 12), tz + R * math.sin(2 * math.pi * k / 12 + math.pi / 12)) for k in range(12)]
    cprism(sc, "x", -86, 50, poly, "m", 2.5, 2.5, dark=1, bias=50)
    for k in range(12):
        ang = 15 + 30 * k
        c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        if c < 0.3 and s_ < 0.5:
            radial(sc, "x", -82, 42, (ty, tz), ang, R - 2, R + 15, 22, "dk", b=1, dark=0, bias=40)
            if k != 7:
                radial(sc, "x", -70, 12, (ty, tz), ang, R + 15, R + 22, 10, "t", b=0, dark=0, bias=38)
    radial(sc, "x", -76, 14, (ty, tz), 225, R + 15, R + 29, 9, "t", b=.6, dark=0, bias=-60)
    servo(sc, (74, ty, tz), "x", 32, 46)
    tip = (ty + (R + 26) * math.cos(math.radians(225)), tz + (R + 26) * math.sin(math.radians(225)))
    seams(sc, [[(-30, *SP(176, 58)), (-46, *SP(150, 58)), (-60, tip[0] + 10, tip[1] + 22)]], ((-60, -40, 230), (-30, 20, 300)), "pipe", bias=-61)
    sc.axis((-80, -120, 352), (80, -120, 352), "Z")
    sc.axis((130, *SP(262, 150)), (130, *SP(182, 150)), "X", off=(14, 0))
    sc.rot((-150, yc, zc), (1, 0, 0), 98, "", 210, 330)
    sc.note((-250, -60, 340), "主軸", "工作物をつかんで回す。主軸台に軸受とモータが入る")
    sc.note((-150, yc - 30, zc - 56), "チャック", "爪で工作物を保持する")
    sc.note((-60, ty - 20, tz + R), "タレット", "工具を円周に並べ、割り出して使い分ける")
    sc.note((-69, *tip), "工具", "バイトで外径・端面・溝・ねじを削る")
    sc.note((236, *SP(185, 10)), "リニアガイド", "刃物台を案内するレール")
    sc.note((250, ya - 6, za), "ボールねじ", "モータの回転を直線の送りに変える")
    sc.note((336, ya, za + 32), "サーボモータ", "NCの指令どおりに送り軸を動かす")
    sc.note((250, SP(30, 18)[0], 168), "心押台", "長い工作物の先端をセンタで支える")
    sc.note((20, *SP(20, 0)), "ベッド", "機械の土台。傾斜させて切りくずを落とす")


# =====================================================================================
@mt("vertical-machining-center", az=-34, el=22)
def _(sc):
    # bed (dark toe kick + casting), Y rails, saddle, X rails, table
    block(sc, -222, -182, 0, 444, 394, 12, "dk", ch=8, b=0, dark=0, bias=950)
    block(sc, -230, -190, 12, 460, 410, 80, "pt", ch=12, b=3, bias=900)
    for x in (-110, 110):
        rail(sc, (x, -170, 92), "y", 260, "z", w=16, h=10, carriages=[(30, 40)], pitch=52, bias=600)
    tcover(sc, (0, -160, 92), (0, -1, 0), 26, 250, 10, segs=3, step=2, bias=590)
    block(sc, -150, -160, 108, 300, 230, 36, "pt", ch=6, b=2.5, bias=500)          # saddle (Y)
    for y in (-118, 18):
        rail(sc, (-160, y, 144), "x", 320, "z", w=14, h=9, carriages=[(240, 36)], pitch=64, bias=400)
    block(sc, -215, -146, 158, 430, 192, 30, "m", ch=4, b=2, bias=300)              # table (X)

    def tslots(s_):
        ln = ""
        for k in range(5):
            y = -126 + k * 38
            a, b = s_.P((-207, y, 188.2)), s_.P((207, y, 188.2))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return '<path class="tslot" d="%s"/>' % ln
    sc.raw(tslots, ((-207, -126, 188), (207, 26, 188.5)), bias=290)
    # vise + work (aluminium block with a pocket)
    block(sc, -96, -112, 188, 192, 112, 18, "dk", ch=3, b=1.5, dark=0)
    block(sc, -88, -6, 206, 176, 14, 30, "w", b=1.5, bias=-1)                      # fixed jaw
    block(sc, -88, -112, 206, 176, 14, 30, "w", b=1.5, bias=-1)                    # moving jaw
    MCYL(sc, (0, -112, 197), (0, -1, 0), 5, 26, "w", seg=14, bands=6, bias=-2)
    block(sc, -76, -98, 206, 152, 92, 40, "alu", b=1.5, dark=0)
    seams(sc, [[(-50, -78, 246.2), (40, -78, 246.2), (40, -24, 246.2), (-50, -24, 246.2), (-50, -78, 246.2)]],
          ((-50, -78, 246), (40, -24, 246.5)), "alus4", bias=-1)
    servo(sc, (215, -50, 173), "x", 30, 44)                                         # X servo
    # column with Z rails, bellows below the head, Z servo + screw on top
    block(sc, -125, 100, 92, 250, 150, 440, "pt", ch=10, b=3, bias=200)
    for x in (-82, 82):
        rail(sc, (x, 100, 140), "z", 380, (0, -1, 0), w=16, h=8, carriages=[(196, 46), (262, 46)], bias=150)
    bellows(sc, (-62, 92, 140), (62, 100, 330), "z", folds=14, bias=160)
    ballscrew(sc, (0, 94, 480), "z", 48, r=6, supports=False, nm=(0, -1, 0), bias=160)
    servo(sc, (0, 94, 528), "z", 34, 44, up=(0, -1, 0))
    # spindle head: casting, dark name band, motor, spindle nose, holder, end mill
    block(sc, -78, -36, 316, 156, 128, 150, "pt", ch=8, b=3)
    block(sc, -70, -37.4, 436, 140, 1.4, 18, "dk", b=0, dark=0, bias=-1)
    bolts(sc, [(-60 + 24 * k, -40, 466) for k in range(6)], "z", 3.2, bias=-1)
    finmotor(sc, (0, 30, 466), (0, 0, 1), 34, 44, nf=14)
    MCYL(sc, (0, 0, 316), (0, 0, -1), 40, 10, "pt", rings=())
    MCYL(sc, (0, 0, 306), (0, 0, -1), 32, 14, "w", rings=(.5,))
    MCYL(sc, (0, 0, 292), (0, 0, -1), 26, 9, "w", dark=0, rings=(.5,))
    MCYL(sc, (0, 0, 283), (0, 0, -1), 18, 14, "w", r1=13)
    MCYL(sc, (0, 0, 269), (0, 0, -1), 14, 8, "w", seg=20, bands=8)
    MCYL(sc, (0, 0, 261), (0, 0, -1), 8, 36, "t", seg=18, bands=8, dark=0)

    def flutes(s_):
        return helix(s_.cam, (0, 0, 228), (0, 0, 1), 8, 30, 22, "hobt", per=12)
    sc.raw(flutes, ((-8, -8.5, 228), (8, -8, 258)), bias=-3)
    # ATC magazine on the column side: disc + 12 pots with holders
    MCYL(sc, (125, 175, 420), (1, 0, 0), 88, 20, "pt", seg=40, rings=())
    for k in range(12):
        t = 2 * math.pi * k / 12
        MCYL(sc, (145, 175 + 72 * math.cos(t), 420 + 72 * math.sin(t)), (1, 0, 0), 10, 10, "w", seg=12, bands=4, spec=False, bias=-1)
    holes(sc, [(155.2, 175 + 72 * math.cos(2 * math.pi * k / 12), 420 + 72 * math.sin(2 * math.pi * k / 12)) for k in range(12)], (1, 0, 0), 4.5, bias=-2)
    # NC operation panel on a pendant stand
    MCYL(sc, (300, -40, 0), (0, 0, 1), 7, 262, "m", seg=14, bands=6)
    panel(sc, 262, -78, 262, 84, 26, 104)
    sc.axis((-230, -180, 230), (-110, -180, 230), "X")
    sc.axis((-250, -170, 110), (-250, -60, 110), "Y", off=(-12, 0))
    sc.axis((100, -40, 350), (100, -40, 450), "Z", off=(14, 0))
    sc.note((0, -36, 420), "主軸", "工具を回転させる。ビルトインモータ主軸が多い")
    sc.note((0, -8, 250), "工具", "ツールホルダで主軸テーパに取り付ける")
    sc.note((147, 175, 508), "ATC", "工具マガジンと交換アームで工具を自動交換")
    sc.note((-200, -146, 188), "テーブル", "工作物を載せてX方向に動く")
    sc.note((-150, -160, 124), "サドル", "テーブルを載せてY方向に動く")
    sc.note((-125, 100, 470), "コラム", "主軸頭を支え、Z方向に案内する")
    sc.note((82, 92, 250), "リニアガイド", "各軸を案内するレール")
    sc.note((300, -78, 330), "NC装置", "加工プログラムで全軸を制御する")
    sc.note((-200, -190, 50), "ベッド", "機械全体の土台")


# =====================================================================================
@mt("spindle", az=-30, el=22)
def _(sc):
    """built-in motor spindle, housing/stator/bearings cut away (back half kept, section on y=0)."""
    RO, RI = 126, 104
    # housing back half + covers
    xshell(sc, -240, 476, RO, RI, mat="pt", bias=500, seg=24)
    xshell(sc, -262, 22, RO, 30, mat="pt", bias=480, seg=24)
    xshell(sc, 236, 14, RO, 48, mat="pt", bias=480, seg=24)
    # stator: laminated core + copper coil ends (back half)
    xshell(sc, -120, 200, RI, 76, mat="m", bias=300)
    for x0 in (-142, 80):
        xshell(sc, x0, 22, 98, 80, mat="cu", dark=0, bias=300)
    # bearings (back half): outer race, cage, inner race
    brg = [(150, 30), (186, 30), (-234, 28)]
    for x0, w in brg:
        xshell(sc, x0, w, RI, 88, mat="w", bias=250, seg=20)
        xshell(sc, x0 + w * .2, w * .6, 86, 58, mat="dk", dark=0, bias=252, seg=16)
        xshell(sc, x0, w, 56, 40, mat="w", bias=250, seg=14)
    # section faces on the cut plane
    R = []
    for sg in (1, -1):
        def zz(a, b):
            return (min(a * sg, b * sg), max(a * sg, b * sg))
        R += [(-240, 236, *zz(RI, RO), "cut"), (-262, -240, *zz(30, RO), "cut"), (236, 250, *zz(48, RO), "cut")]
        R += [(-80 + 34 * k, -66 + 34 * k, *zz(110, 118), "fl") for k in range(6)]        # cooling channels
        R += [(-120, 80, *zz(76, RI), "cut"), (-142, -120, *zz(80, 98), "cus2"), (80, 102, *zz(80, 98), "cus2")]
        for x0, w in brg:
            R += [(x0, x0 + w, *zz(88, RI), "cut"), (x0, x0 + w, *zz(56, 88), "dks4"), (x0, x0 + w, *zz(40, 56), "cut")]
            R += [(x0 + w / 2 - 13, x0 + w / 2 + 13, *zz(59, 85), "ball")]
    sect(sc, R, ((-262, -0.5, -RO), (250, 0, RO)), bias=220)

    def lams(s_):
        o = ""
        for k in range(1, 20):
            x = -120 + 10 * k
            o += P([s_.cam.xy((x, -0.3, 77)), s_.cam.xy((x, -0.3, 103))], False) + P([s_.cam.xy((x, -0.3, -77)), s_.cam.xy((x, -0.3, -103))], False)
        return path(o, "gr")
    sc.raw(lams, ((-120, -0.6, -RI), (80, -0.3, RI)), bias=219)
    # shaft (whole), rotor on it, rear encoder
    MCYL(sc, (-300, 0, 0), (1, 0, 0), 26, 38, "w", bias=200, seg=24)
    MCYL(sc, (-262, 0, 0), (1, 0, 0), 40, 512, "w", bias=200, seg=32, rings=(.09, .8))
    MCYL(sc, (-112, 0, 0), (1, 0, 0), 70, 184, "dk", bias=150, seg=36, dark=0)

    def rlam(s_):
        return "".join(cline(s_.cam, (-112 + 184 * k / 12, 0, 0), (1, 0, 0), 70.3, "mgrid", 28) for k in range(1, 12))
    sc.raw(rlam, ((-112, -70.5, -70), (72, 70, 70)), bias=149)
    MCYL(sc, (-336, 0, 0), (1, 0, 0), 24, 36, "dk", bias=210, seg=24, rings=(.5,))
    # spindle nose, tool holder (flange with V groove, taper), collet nut, end mill
    MCYL(sc, (250, 0, 0), (1, 0, 0), 56, 20, "w", seg=36, rings=(.5,))
    bolts(sc, ring_pts((270, 0, 0), (1, 0, 0), 47, 6, math.pi / 6), (1, 0, 0), 3.6)
    MCYL(sc, (270, 0, 0), (1, 0, 0), 30, 8, "w", r1=26, seg=28)
    MCYL(sc, (278, 0, 0), (1, 0, 0), 44, 18, "w", seg=32, rings=(.35, .65), dark=0)
    MCYL(sc, (296, 0, 0), (1, 0, 0), 26, 30, "w", r1=18, seg=28, dark=0)
    MCYL(sc, (326, 0, 0), (1, 0, 0), 22, 14, "w", seg=24)
    MCYL(sc, (340, 0, 0), (1, 0, 0), 12, 70, "t", seg=20, bands=8, dark=0)

    def flutes(s_):
        return helix(s_.cam, (350, 0, 0), (1, 0, 0), 12, 60, 40, "hobt", per=14)
    sc.raw(flutes, ((350, -12.5, -12), (410, -12, 12)), bias=-3)
    sc.rot((330, 0, 0), (1, 0, 0), 60, "", 200, 330)
    sc.note((-282, 0, 26), "主軸（シャフト）", "工具や工作物を取り付けて回す軸")
    sc.note((183, 0, 80), "主軸軸受（前側）", "アンギュラ玉軸受を組み合わせ、予圧をかけて剛性を出す")
    sc.note((-220, 0, -72), "主軸軸受（後側）", "熱による伸びを逃がす側の軸受")
    sc.note((-20, 0, 92), "ステータ", "ビルトインモータの固定子（巻線）")
    sc.note((-20, -30, -62), "ロータ", "主軸と一体で回るモータの回転子")
    sc.note((300, 0, 25), "主軸テーパ", "ツールホルダを引き込んで固定する")
    sc.note((390, 0, -12), "工具", "ツールホルダに保持された切削工具")
    sc.note((-170, 92, -58), "ハウジング", "軸受とモータを収める外筒（切断して表示）")
