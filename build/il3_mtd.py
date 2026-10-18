"""v3 machine-tool atlas drawings (shaded metal, detailed): automation and peripherals —
gantry-loader, robot-loading, pallet-changer, bar-feeder, in-process-gauging, chip-conveyor, fms-cell.
Re-registers the same slugs as il_mt.py with the same notes (text, count, order)."""
import math
from il_mt import mt
from il3_mtlib import *


# ------------------------------------------------------------------ shared pieces for this sheet
def machine(sc, x, y, w, d, h, bias=0.0, pnl=True, roof=False):
    """enclosed machine tool seen from the front (-y): dark toe kick, painted body with a name band,
    sliding door with window and handle, optional CNC panel at the right and a loading hatch on the roof."""
    block(sc, x + 8, y + 8, 0, w - 16, d - 16, 12, "dk", ch=6, b=0, dark=0, bias=bias + 20)
    block(sc, x, y, 12, w, d, h - 12, "pt", ch=10, b=3, bias=bias)
    block(sc, x + 16, y - 1.2, h - 30, w * .5, 1.2, 12, "dk", b=0, dark=0, bias=bias - 1)
    dx0, dx1, dz0, dz1 = x + w * .1, x + w * .72, h * .2, h * .84
    block(sc, dx0, y - 3, dz0, dx1 - dx0, 3, dz1 - dz0, "pt", b=1, dark=1, bias=bias - 2)
    block(sc, dx1 - 16, y - 8, h * .44, 5, 5, h * .2, "w", b=.8, bias=bias - 3)

    def win(s_):
        cam, yy = s_.cam, y - 3.2
        u0, u1, v0, v1 = dx0 + 12, dx1 - 26, dz0 + 18, dz1 - 14
        q = [cam.xy((u0, yy, v0)), cam.xy((u1, yy, v0)), cam.xy((u1, yy, v1)), cam.xy((u0, yy, v1))]
        o = path(P(q), "win")
        ln = ""
        for f0, f1 in ((.12, .42), (.3, .52)):
            a = cam.xy((u0 + (u1 - u0) * f0, yy, v1 - 2))
            b = cam.xy((u0 + (u1 - u0) * f1, yy, v0 + (v1 - v0) * .45))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return o + path(ln, "mgrid")
    sc.raw(win, ((dx0, y - 3.4, dz0), (dx1, y - 3.2, dz1)), bias - 2)
    if pnl:
        pw = min(46, w * .2)
        panel(sc, x + w - pw - 8, y - 14, h * .4, pw, 13, h * .32, bias=bias - 4)
    if roof:
        block(sc, x + w * .2, y + d * .25, h, w * .45, d * .45, 2, "dk", b=0, dark=0, bias=bias - 5)


def pallet(sc, x, y, z, sx, sy, th=12, bias=0.0, slots=4):
    """machine pallet: ground grey plate with T-slots along x."""
    block(sc, x, y, z, sx, sy, th, "m", ch=3, b=1.5, dark=1, bias=bias)

    def ts(s_):
        ln = ""
        for k in range(slots):
            yy = y + sy * (k + .5) / slots
            a, b = s_.P((x + 4, yy, z + th + .2)), s_.P((x + sx - 4, yy, z + th + .2))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return path(ln, "tslot")
    sc.raw(ts, ((x, y, z + th), (x + sx, y + sy, z + th + .3)), bias - .5)


def blanks(sc, pts_, r, h, bias=0.0):
    """steel workpieces (bright turned blanks) standing on a plate."""
    for p in sorted(pts_, key=lambda q: -sc.d(q)):
        MCYL(sc, p, (0, 0, 1), r, h, "w", dark=0, seg=20, bands=6, rings=(.7,), bias=bias)


def foot(sc, x, y, s, bias=0.0):
    """dark base plate with four anchor bolts, centred at (x, y)."""
    block(sc, x - s / 2, y - s / 2, 0, s, s, 8, "dk", ch=3, b=1, dark=0, bias=bias)
    k = s * .34
    bolts(sc, [(x + i * k, y + j * k, 8) for i in (-1, 1) for j in (-1, 1)], "z", s * .07, bias=bias - 1)


# =====================================================================================
@mt("gantry-loader", az=-30, el=24)
def _(sc):
    machine(sc, -330, -100, 220, 200, 260, bias=300, roof=True)
    machine(sc, -60, -100, 220, 200, 260, bias=300, roof=True)
    # work stocker: dark base, ground top plate, locating pins and blanks
    block(sc, 210, -90, 0, 140, 160, 12, "dk", ch=5, b=0, dark=0, bias=320)
    block(sc, 214, -86, 12, 132, 152, 96, "dk", ch=6, b=2, dark=0, bias=300)
    seams(sc, [[(250, -86.2, 24), (250, -86.2, 100)], [(310, -86.2, 24), (310, -86.2, 100)]], ((250, -87, 24), (310, -86, 100)), "mgrid", bias=299)
    block(sc, 206, -94, 108, 148, 168, 12, "m", ch=4, b=1.5, bias=250)
    blanks(sc, [(240 + i * 40, -60 + j * 50, 120) for i in range(3) for j in range(2)], 14, 24, bias=200)
    # posts on anchored foot plates, beam with two guide rails on its front face
    for x in (-360, 380):
        foot(sc, x, 135, 56, bias=260)
        block(sc, x - 16, 119, 8, 32, 32, 392, "pt", ch=5, b=2, bias=250)
    block(sc, -380, 100, 400, 790, 60, 50, "pt", ch=4, b=3, bias=120)
    for zr in (410, 432):
        rail(sc, (-372, 100, zr), "x", 774, (0, -1, 0), w=10, h=6, carriages=[(106, 58)], pitch=40, bias=100)
    cablechain(sc, (-40, 112, 465), "x", "z", 320, 440, 15, 34, bias=90)
    # carriage plate, X servo, ram housing, vertical ram (Z) and double hand over the stocker
    block(sc, 241, 62, 380, 78, 24, 104, "pt", ch=4, b=2, bias=60)
    servo(sc, (280, 74, 484), "z", 28, 38)
    block(sc, 255, 30, 392, 50, 32, 80, "pt", ch=4, b=2, bias=40)
    block(sc, 268, 34, 472, 24, 24, 50, "m", ch=3, b=1.5, bias=41)
    block(sc, 268, 34, 206, 24, 24, 186, "m", ch=3, b=1.5, bias=42)
    seams(sc, [[(280, 33.8, 214), (280, 33.8, 384)]], ((268, 33.5, 214), (292, 34, 384)), "gr", bias=41)
    block(sc, 245, 22, 182, 70, 48, 24, "dk", ch=4, b=1.2, dark=0, bias=30)
    for xh in (259, 301):
        MCYL(sc, (xh, 46, 182), (0, 0, -1), 13, 18, "dk", seg=20, bands=6, spec=False, bias=28)
        for ph in (90, 210, 330):
            c, s_ = math.cos(math.radians(ph)), math.sin(math.radians(ph))
            block(sc, xh + 9 * c - 3, 46 + 9 * s_ - 3, 148, 6, 6, 16, "w", b=.6, bias=26)
    MCYL(sc, (259, 46, 132), (0, 0, 1), 14, 20, "w", dark=0, seg=20, bands=6, rings=(.6,), bias=24)
    sc.axis((-200, 70, 490), (40, 70, 490), "走行")
    sc.axis((340, 46, 250), (340, 46, 330), "上下", off=(18, 0))
    sc.note((-320, 130, 450), "走行軸（ガントリ）", "機械の上を横切る梁。ハンドを横に運ぶ")
    sc.note((280, 22, 190), "ローダハンド", "工作物をつかみ、扉の上から機械に出し入れする")
    sc.note((-220, -100, 200), "工作機械1", "旋盤など。工程順に並べる")
    sc.note((50, -100, 200), "工作機械2", "")
    sc.note((280, -90, 140), "ワークストッカ", "素材と完成品を置く台")


# =====================================================================================
def robot_parts(cam, items, p1, p2, p3, J):
    """6-axis robot arm from shoulder p1 via elbow p2 to wrist p3, joint axis J (horizontal)."""
    def cyl(O, A, r, h, mat, dep=0.0, **kw):
        s, bb = MCYL_svg(cam, O, A, r, h, mat, **kw)
        c = tuple((bb[0][i] + bb[1][i]) / 2 for i in range(3))
        items.append((cam.P(c)[2] + dep, s, bb))

    def seg(pa, pb):
        d = tuple(pb[i] - pa[i] for i in range(3))
        return d, math.sqrt(sum(v * v for v in d))
    # shoulder housing (J2) + J2 motor on the near side
    cyl(add3(p1, J, -34), J, 30, 68, "pt", dep=4, seg=32, rings=(.15, .85))
    cyl(add3(p1, J, -56), J, 18, 22, "dk", dep=-30, seg=20, bands=6, rings=(.4,))
    d, L = seg(p1, p2)
    cyl(p1, d, 24, L, "pt", dep=0, seg=28, r1=19)
    cyl(add3(p2, J, -28), J, 25, 56, "pt", dep=-6, seg=28, rings=(.15, .85))
    cyl(add3(p2, J, 28), J, 17, 24, "dk", dep=10, seg=20, bands=6, rings=(.4,))   # J3 motor behind
    d, L = seg(p2, p3)
    cyl(add3(p2, d, -.12), d, 18, L * 1.04, "pt", dep=-12, seg=24, r1=13)
    wd = GE._norm((-1, 0, -.3))
    cyl(p3, wd, 14, 22, "dk", dep=-20, seg=20, bands=6)
    pw = add3(p3, wd, 22)
    cyl(pw, wd, 11, 6, "w", dep=-22, seg=18, bands=6)
    return add3(pw, wd, 6)


@mt("robot-loading", az=-30, el=24)
def _(sc):
    cam = sc.cam
    machine(sc, -320, 40, 240, 220, 270, bias=300)
    # parts table: dark stand, ground plate, blanks on locating pins
    block(sc, 152, -78, 0, 166, 136, 12, "dk", ch=5, b=0, dark=0, bias=320)
    block(sc, 156, -74, 12, 158, 128, 82, "dk", ch=6, b=2, dark=0, bias=300)
    block(sc, 146, -84, 94, 178, 148, 10, "m", ch=4, b=1.5, bias=250)
    blanks(sc, [(180 + i * 50, -50 + j * 60, 104) for i in range(3) for j in range(2)], 15, 22, bias=200)
    # robot riser + J1 base + turret
    b = (0, -60)
    foot(sc, b[0], b[1], 110, bias=180)
    MCYL(sc, (b[0], b[1], 8), (0, 0, 1), 44, 24, "dk", seg=36, rings=(.5,), bias=170)
    MCYL(sc, (b[0], b[1], 32), (0, 0, 1), 38, 30, "pt", seg=36, rings=(.2,), bias=160)
    MCYL(sc, (b[0], b[1], 62), (0, 0, 1), 30, 36, "pt", seg=32, bias=150)
    p1 = (b[0], b[1], 110)
    p2 = (b[0] - 40, b[1] + 50, 260)
    p3 = (b[0] - 150, b[1] + 80, 230)
    J = GE._norm((80, 150, 0))
    items = []
    fl = robot_parts(cam, items, p1, p2, p3, J)
    # gripper: dark body pointing down, two fingers, held blank
    g0 = (fl[0] - 2, fl[1], fl[2] - 4)
    s, bb = abox_svg(cam, (g0[0] - 16, g0[1] - 12, g0[2] - 20), (g0[0] + 16, g0[1] + 12, g0[2]), "dk", "z", 3, 1)
    items.append((cam.P(g0)[2] - 30, s, bb))
    for dy in (-10, 10):
        s, bb = abox_svg(cam, (g0[0] - 4, g0[1] + dy - 3, g0[2] - 44), (g0[0] + 4, g0[1] + dy + 3, g0[2] - 20), "w", "z", 0, .6)
        items.append((cam.P(g0)[2] - 40 - dy, s, bb))
    s, bb = MCYL_svg(cam, (g0[0], g0[1], g0[2] - 46), (0, 0, 1), 12, 18, "w", dark=0, seg=20, bands=6)
    items.append((cam.P(g0)[2] - 35, s, bb))
    items.sort(key=lambda q: -q[0])
    sc.add("".join(v for _, v, _ in items), bbu(*[q[2] for q in items]), 0)
    # safety fence: yellow posts and rails with wire mesh
    def fence(s_):
        o, m = "", ""
        for x in (-60, 60, 180, 300):
            a, c = s_.P((x, -200, 0)), s_.P((x, -200, 160))
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        for z in (14, 160):
            a, c = s_.P((-60, -200, z)), s_.P((300, -200, z))
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        for k in range(1, 36):
            x = -60 + 10 * k
            if x % 120 == 60:
                continue
            a, c = s_.P((x, -200, 14)), s_.P((x, -200, 160))
            m += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        for z in range(24, 160, 10):
            a, c = s_.P((-60, -200, z)), s_.P((300, -200, z))
            m += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        return path(m, "thread") + '<path class="fence" d="%s"/>' % o
    sc.raw(fence, ((-60, -201, 0), (300, -199, 160)), bias=-100)
    sc.note((p2[0], p2[1], p2[2] + 20), "ロボット", "6軸の多関節ロボット。工作物を出し入れする")
    sc.note((p3[0] - 30, p3[1], p3[2] - 40), "ハンド", "工作物に合わせた爪でつかむ")
    sc.note((-200, 40, 260), "工作機械", "ドアを自動で開け閉めする")
    sc.note((260, -80, 110), "ワークストッカ", "素材と完成品を並べる")
    sc.note((120, -200, 160), "安全柵", "人が近づくと止まるよう囲う（協働ロボットでは省けることもある）")


# =====================================================================================
def alu_work(sc, x, y, z, sx, sy, sz, bias=0.0):
    """aluminium workpiece block with a machined pocket outline on top."""
    block(sc, x, y, z, sx, sy, sz, "alu", b=1.2, dark=0, bias=bias)
    i, j = sx * .2, sy * .25
    seams(sc, [[(x + i, y + j, z + sz + .2), (x + sx - i, y + j, z + sz + .2), (x + sx - i, y + sy - j, z + sz + .2), (x + i, y + sy - j, z + sz + .2), (x + i, y + j, z + sz + .2)]],
          ((x + i, y + j, z + sz), (x + sx - i, y + sy - j, z + sz + .3)), "alus4", bias=bias - .5)


@mt("pallet-changer", az=-30, el=26)
def _(sc):
    machine(sc, -340, 40, 260, 260, 320, bias=300)
    # rotary changer: base, turning column, two pallets on dark receivers, fixture + work on the outer one
    block(sc, -54, 46, 0, 228, 248, 12, "dk", ch=6, b=0, dark=0, bias=300)
    block(sc, -60, 40, 12, 240, 260, 48, "pt", ch=6, b=2.5, bias=280)
    MCYL(sc, (55, 115, 60), (0, 0, 1), 18, 6, "m", seg=24, bands=6, bias=260)
    for x0 in (-40, 70):
        block(sc, x0 + 10, 80, 60, 70, 70, 4, "dk", b=0, dark=0, bias=230)
        pallet(sc, x0, 70, 64, 90, 90, 12, bias=200)
    block(sc, -26, 98, 76, 62, 34, 10, "dk", ch=2, b=1, dark=0, bias=160)
    alu_work(sc, -20, 102, 86, 50, 26, 50, bias=150)
    alu_work(sc, 90, 92, 76, 50, 44, 28, bias=150)
    # pallet stocker: steel frame (posts, shelf beams) holding pallets on three levels
    for xp in (200, 344):
        for yp in (-60, 264):
            block(sc, xp, yp, 0, 16, 16, 330, "pt", ch=2, b=1.5, bias=420 if yp > 0 else 340)
    for k in range(3):
        zk = 30 + k * 100
        for xb in (216, 334):
            block(sc, xb - (0 if xb < 300 else 10), -44, zk, 10, 308, 10, "dk", b=.8, dark=0, bias=380 - k)
        pallet(sc, 226, -30, zk + 10, 98, 100, 10, bias=360 - k, slots=3)
        pallet(sc, 226, 150, zk + 10, 98, 100, 10, bias=370 - k, slots=3)
        if k < 2:
            alu_work(sc, 246, -10, zk + 20, 52, 50, 24 + 8 * k, bias=355 - k)
    for yp in (-60, 264):
        block(sc, 216, yp + 3, 314, 128, 10, 16, "pt", b=1.5, bias=345 if yp < 0 else 425)
    # transfer cart on a floor track
    for yr in (-148, -76):
        rail(sc, (-60, yr, 0), "x", 240, "z", w=12, h=8, pitch=40, bias=120)
    block(sc, -20, -160, 14, 140, 100, 40, "pt", ch=6, b=2, bias=90)
    for xw in (-6, 106):
        MCYL(sc, (xw, -160.2, 20), (0, -1, 0), 9, 4, "dk", seg=16, bands=4, spec=False, bias=85)
    block(sc, -14, -154, 54, 128, 88, 6, "dk", b=0, dark=0, bias=86)
    pallet(sc, 0, -150, 60, 100, 80, 12, bias=80)
    # setup station: base, pallet with a fixture, push-button box on a post
    block(sc, -324, -174, 0, 168, 128, 12, "dk", ch=5, b=0, dark=0, bias=160)
    block(sc, -330, -180, 12, 180, 140, 78, "pt", ch=6, b=2.5, bias=150)
    pallet(sc, -310, -170, 90, 120, 100, 12, bias=140)
    block(sc, -280, -140, 102, 60, 40, 10, "dk", ch=2, b=1, dark=0, bias=130)
    alu_work(sc, -274, -136, 112, 48, 32, 30, bias=125)
    MCYL(sc, (-160, -190, 90), (0, 0, 1), 4, 36, "m", seg=12, bands=4, spec=False, bias=118)
    block(sc, -172, -200, 126, 24, 18, 26, "dk", ch=2, b=1, dark=0, bias=115)
    sc.note((-210, 40, 330), "工作機械", "横形マシニングセンタなど")
    sc.note((40, 90, 120), "パレット", "治具ごと工作物を載せる台。機械の外で段取りできる")
    sc.note((260, -60, 300), "パレットストッカ", "複数のパレットを棚に置き、夜間も連続運転する")
    sc.note((50, -160, 70), "搬送台車", "パレットを棚と機械の間で運ぶ")
    sc.note((-250, -180, 100), "段取りステーション", "作業者が工作物を付け外しする場所")


# =====================================================================================
@mt("bar-feeder", az=-24, el=22)
def _(sc):
    # bar feeder: stands on foot plates, long body, dark rounded cover, nose guide
    for xs in (-350, -200, -50):
        foot(sc, xs, 0, 60, bias=340)
        block(sc, xs - 14, -14, 8, 28, 28, 62, "dk", ch=3, b=1, dark=0, bias=330)
    block(sc, -380, -50, 70, 360, 100, 80, "pt", ch=6, b=2.5, bias=300)
    seams(sc, [[(x, -50.2, 78), (x, -50.2, 144)] for x in (-260, -140)], ((-260, -51, 78), (-140, -50, 144)), "gr", bias=299)
    cprism(sc, "x", -378, 356, [(-46, 150), (46, 150), (46, 168), (30, 186), (-30, 186), (-46, 168)], "dk", 3, 3, dark=0, bias=250)
    for x in (-330, -250, -170, -90):
        block(sc, x, -48, 150, 14, 2, 8, "w", b=.5, bias=240)
    panel(sc, -372, -64, 84, 44, 14, 58, bias=200)
    # material rack: inclined plate on brackets, bars rolling toward the feeder
    for xb in (-350, -230, -110):
        block(sc, xb, -132, 70, 10, 82, 48, "dk", b=.8, dark=0, bias=280)
    cprism(sc, "x", -372, 290, [(-140, 118), (-56, 132), (-56, 138), (-140, 126)], "pt", 2, 2, dark=1, bias=270)
    cprism(sc, "x", -372, 290, [(-142, 126), (-136, 126), (-136, 140), (-142, 140)], "pt", 1, 1, dark=1, bias=265)
    for k in range(5):
        t = (k + .5) / 5.4
        MCYL(sc, (-366, -132 + 70 * t, 134.5 + 12 * t), (1, 0, 0), 6, 280, "w", seg=16, bands=6, bias=240 - k)
    # bar leaving the feeder nose into the spindle; spindle-end cylinder at the lathe side
    MCYL(sc, (-20, 0, 168), (1, 0, 0), 12, 14, "dk", seg=20, bands=6, bias=60)
    MCYL(sc, (-6, 0, 168), (1, 0, 0), 6, 44, "w", seg=16, bands=6, bias=55)
    MCYL(sc, (22, 0, 168), (1, 0, 0), 26, 18, "dk", seg=28, rings=(.5,), bias=50)
    machine(sc, 40, -100, 300, 220, 280, bias=200)
    sc.axis((-300, -60, 215), (-120, -60, 215), "送り", both=False)
    sc.note((-200, -46, 186), "バーフィーダ", "長い棒材を主軸の後ろから押し出して送る")
    sc.note((-250, -110, 140), "材料ラック", "次に使う棒材を並べ、自動で補給する")
    sc.note((6, 0, 174), "棒材", "主軸の中を通って加工位置まで送られる")
    sc.note((150, -100, 200), "工作機械", "NC旋盤や主軸移動形自動旋盤")


# =====================================================================================
@mt("in-process-gauging", az=-28, el=20)
def _(sc):
    # machine table with T-slots on a painted saddle
    block(sc, -230, -140, -30, 460, 280, 30, "pt", ch=6, b=0, dark=1, bias=650)
    block(sc, -260, -160, 0, 520, 320, 40, "m", ch=4, b=2, bias=600)

    def ts(s_):
        ln = ""
        for k in range(6):
            y = -135 + k * 54
            a, b = s_.P((-252, y, 40.2)), s_.P((252, y, 40.2))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return path(ln, "tslot")
    sc.raw(ts, ((-252, -135, 40), (252, 135, 40.3)), bias=590)
    # workpiece: machined aluminium housing with a bore and a pocket, held by two strap clamps
    block(sc, -160, -100, 40, 240, 180, 110, "alu", ch=3, b=2, dark=0, bias=400)
    seams(sc, [[(-140, -80, 150.2), (-60, -80, 150.2), (-60, 60, 150.2), (-140, 60, 150.2), (-140, -80, 150.2)]],
          ((-140, -80, 150), (-60, 60, 150.3)), "alus4", bias=390)
    holes(sc, [(10, -10, 150.2)], "z", 40, "alus4", bias=389)
    holes(sc, [(10, -10, 150.4)], "z", 32, "bg", bias=388)
    for x0 in (-200, 80):
        block(sc, x0 + 6, -28, 40, 28, 36, 60, "dk", ch=2, b=1, dark=0, bias=420 if x0 < 0 else 380)
        block(sc, x0, -30, 100, 42 if x0 > 0 else 40, 40, 12, "dk", ch=2, b=1, dark=0, bias=410 if x0 < 0 else 370)
        bolts(sc, [(x0 + 20, -10, 112)], "z", 6, bias=405 if x0 < 0 else 365)
    # spindle head (cropped), nose, holder, touch probe with stylus
    block(sc, -100, -80, 382, 140, 140, 70, "pt", ch=8, b=3, bias=300)
    block(sc, -90, -81.2, 430, 120, 1.2, 12, "dk", b=0, dark=0, bias=299)
    MCYL(sc, (-30, -10, 382), (0, 0, -1), 40, 30, "w", seg=36, rings=(.4,), bias=200)
    bolts(sc, ring_pts((-30, -10, 352), (0, 0, 1), 33, 6, math.pi / 6), (0, 0, -1), 2.6, bias=199)
    MCYL(sc, (-30, -10, 352), (0, 0, -1), 26, 16, "w", seg=28, rings=(.5,), dark=0, bias=195)
    MCYL(sc, (-30, -10, 336), (0, 0, -1), 17, 18, "w", r1=13, seg=24, bias=190)
    MCYL(sc, (-30, -10, 318), (0, 0, -1), 22, 50, "dk", seg=28, rings=(.2, .6), dark=0, bias=185)

    def led(s_):
        return cline(s_.cam, (-30, -10, 300), (0, 0, 1), 22.4, "scrg", 28)
    sc.raw(led, ((-52.5, -32.5, 299), (-7.5, 12.5, 301)), bias=184)
    MCYL(sc, (-30, -10, 268), (0, 0, -1), 22, 16, "dk", r1=7, seg=24, dark=0, bias=180)
    MCYL(sc, (-30, -10, 252), (0, 0, -1), 3, 78, "w", seg=12, bands=4, bias=175)

    def tip(s_):
        p = s_.P((-30, -10, 170))
        return '<circle class="probeball" cx="%s" cy="%s" r="%s"/>' % (n(p[0]), n(p[1]), n(max(3, 7 * s_.cam.s)))
    sc.raw(tip, ((-37, -17, 163), (-23, -3, 177)), bias=160)
    # tool setter: dark body, neck, steel contact pad
    block(sc, 150, -60, 40, 70, 70, 56, "dk", ch=6, b=1.5, dark=0, bias=300)
    MCYL(sc, (185, -25, 96), (0, 0, 1), 9, 10, "dk", seg=16, bands=4, spec=False, bias=290)
    MCYL(sc, (185, -25, 106), (0, 0, 1), 18, 8, "w", seg=24, bands=8, rings=(.5,), bias=285)
    # receiver on a post at the back corner, optical signal path
    MCYL(sc, (-230, 155, 40), (0, 0, 1), 5, 262, "m", seg=12, bands=4, spec=False, bias=120)
    block(sc, -260, 140, 300, 60, 30, 50, "dk", ch=4, b=1.5, dark=0, bias=100)

    def lens(s_):
        c = s_.P((-230, 139.6, 325))
        o = '<ellipse class="scrn" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(c[0]), n(c[1]), n(16 * s_.cam.s), n(14 * s_.cam.s))
        a, b = s_.P((-34, -18, 300)), s_.P((-226, 139, 322))
        return o + '<path class="ghost" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    sc.raw(lens, ((-246, 139, 311), (-214, 139.6, 339)), bias=-200)
    sc.note((-30, -10, 270), "タッチプローブ", "主軸に付けて工作物に触れ、位置や寸法を測る")
    sc.note((-30, -10, 168), "スタイラス", "先端の球が触れた瞬間に信号を出す")
    sc.note((-100, -100, 120), "工作物", "加工の前後に測り、座標や補正量を自動で直す")
    sc.note((185, -60, 115), "工具長測定器", "工具の長さや折損を測る")
    sc.note((-230, 140, 340), "受信機", "プローブの信号を無線・光でNCに伝える")


# =====================================================================================
@mt("chip-conveyor", az=-26, el=24)
def _(sc):
    cam = sc.cam
    # coolant tank: toe kick, body, level gauge, pump with delivery pipe on the back strip
    block(sc, -362, -82, 0, 424, 204, 10, "dk", ch=5, b=0, dark=0, bias=560)
    block(sc, -370, -90, 10, 440, 220, 90, "pt", ch=6, b=2.5, bias=520)

    def gauge(s_):
        q = lambda x, z: s_.P((x, -90.3, z))
        return path(P([q(-48, 26), q(-30, 26), q(-30, 86), q(-48, 86)]), "dks2") + path(P([q(-45, 30), q(-33, 30), q(-33, 64), q(-45, 64)]), "fls1")
    sc.raw(gauge, ((-48, -90.4, 26), (-30, -90.3, 86)), bias=510)
    finmotor(sc, (20, 100, 100), (0, 0, 1), 18, 40, nf=10)
    seams(sc, [[(20, 100, 140), (20, 100, 170), (-60, 100, 170), (-60, 100, 100)]], ((-60, 95, 100), (20, 105, 170)), "pipe", bias=5)
    # conveyor: casing, side walls, hinge belt (horizontal + inclined), head with discharge chute
    zt = lambda x: 132 if x <= 60 else 132 + (x - 60) * 200 / 180
    parts = []

    def pr(y0, L, uv, mat, dark=1, b=0):
        s, bb = cprism_svg(cam, "y", y0, L, uv, mat, b, b, dark)
        parts.append(s)
        return bb
    bbs = [pr(-60, 120, [(60, 100), (240, 300), (240, 332), (60, 132)], "pt"),
           pr(-60, 120, [(-310, 100), (60, 100), (60, 132), (-310, 132)], "pt")]
    for y0 in (60,):
        bbs.append(pr(y0, 6, [(60, 100), (240, 300), (240, 362), (60, 162)], "pt"))
        bbs.append(pr(y0, 6, [(-310, 100), (60, 100), (60, 146), (-310, 146)], "pt"))
    pr(-60, 120, [(60, 132), (240, 332), (240, 334), (60, 134)], "w", dark=1)
    pr(-60, 120, [(-310, 132), (60, 132), (60, 134), (-310, 134)], "w", dark=0)
    ln = ""
    for k in range(29):
        x = -300 + k * 18
        if x > 236:
            break
        a, b = cam.xy((x, -60, zt(x) + 2.2)), cam.xy((x, 60, zt(x) + 2.2))
        ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    parts.append(path(ln, "tslot"))
    ch = ""
    for k in range(34):
        x = -280 + (k * 37) % 500
        if x > 225:
            continue
        p = cam.xy((x, -48 + (k * 29) % 96, zt(x) + 3))
        ch += "M%s %sq3 -5 6 0q3 5 6 0" % (n(p[0]), n(p[1]))
    parts.append(path(ch, "chipc"))
    bbs.append(pr(-66, 6, [(60, 100), (240, 300), (240, 362), (60, 162)], "pt"))
    bbs.append(pr(-66, 6, [(-310, 100), (60, 100), (60, 146), (-310, 146)], "pt"))
    bbs.append(pr(-70, 140, [(232, 292), (292, 292), (292, 344), (272, 360), (240, 360), (232, 350)], "pt", b=2))
    bbs.append(pr(-50, 100, [(246, 236), (286, 236), (292, 292), (240, 292)], "dk", dark=0))
    sc.add("".join(parts), bbu(*bbs), 0)
    servo(sc, (262, 70, 326), "y", 30, 40, up="z")
    seams(sc, [[(x, -66.2, 104), (x, -66.2, 142)] for x in (-190, -70)], ((-190, -67, 104), (-70, -66, 142)), "gr", bias=-1)
    # chip bucket on casters, chips heaped inside
    block(sc, 236, -84, 14, 148, 168, 146, "dk", ch=8, b=2, dark=0, bias=200)
    for x in (256, 364):
        MCYL(sc, (x, -80, 0), (0, 1, 0), 7, 10, "w", seg=14, bands=4, spec=False, bias=210)
        MCYL(sc, (x, 60, 0), (0, 1, 0), 7, 10, "w", seg=14, bands=4, spec=False, bias=230)
    block(sc, 252, -84.6, 40, 116, 0.6, 14, "dk", b=0, dark=1, bias=199)
    for yl in (-78, 68):
        block(sc, 194, yl, 0, 12, 10, 252, "dk", ch=2, b=0, dark=0, bias=-20 if yl < 0 else 40)
    block(sc, 194, -68, 40, 12, 136, 8, "dk", b=0, dark=0, bias=30)

    def pile(s_):
        q = [s_.P(p) for p in ((242, -78, 160.3), (378, -78, 160.3), (378, 78, 160.3), (242, 78, 160.3))]
        o = path(P(q), "dks4")
        o2 = ""
        for k in range(22):
            x, y = 250 + (k * 41) % 120, -70 + (k * 53) % 140
            p = s_.P((x, y, 160.5))
            o2 += "M%s %sq3 -5 6 0q3 5 6 0" % (n(p[0]), n(p[1]))
        return o + path(o2, "chipc")
    sc.raw(pile, ((250, -70, 160), (370, 70, 161)), bias=150)
    sc.axis((-200, -110, 200), (0, -110, 200), "搬送", both=False)
    sc.note((-100, -60, 140), "チップコンベヤ", "ヒンジ板やスクレーパで切りくずを運び出す")
    sc.note((140, 0, 230), "切りくず", "機械の外へ連続して排出する")
    sc.note((-300, -90, 60), "クーラントタンク", "切削油をためて機械に戻す")
    sc.note((300, -90, 120), "回収箱", "切りくずを集めて運び出す")


# =====================================================================================
@mt("fms-cell", az=-30, el=36)
def _(sc):
    for k in range(3):
        x = -380 + k * 250
        machine(sc, x, 100, 210, 200, 230, bias=300, pnl=False)
        # pallet changer station in front of each machine: pallet, tombstone fixture, work
        block(sc, x + 49, 34, 0, 112, 62, 10, "dk", ch=4, b=0, dark=0, bias=270)
        block(sc, x + 45, 30, 10, 120, 70, 50, "pt", ch=5, b=2, bias=250)
        pallet(sc, x + 55, 40, 60, 100, 50, 10, bias=240, slots=3)
        if k != 1:
            block(sc, x + 85, 52, 70, 40, 26, 46, "dk", ch=2, b=1, dark=0, bias=230)
            alu_work(sc, x + 88, 44, 76, 34, 8, 34, bias=225)
    # RGV track and cart
    block(sc, -420, -50, 0, 860, 40, 6, "dk", b=0, dark=0, bias=420)
    for yr in (-42, -18):
        rail(sc, (-416, yr, 6), "x", 852, "z", w=8, h=6, pitch=48, bias=400)
    block(sc, -60, -70, 16, 140, 80, 36, "pt", ch=6, b=2, bias=200)
    for xw in (-44, 64):
        MCYL(sc, (xw, -70.2, 22), (0, -1, 0), 8, 4, "dk", seg=14, bands=4, spec=False, bias=195)
    block(sc, -54, -64, 52, 128, 68, 4, "dk", b=0, dark=0, bias=196)
    pallet(sc, -40, -60, 56, 100, 60, 10, bias=190, slots=3)
    block(sc, -10, -40, 66, 40, 26, 40, "dk", ch=2, b=1, dark=0, bias=185)
    alu_work(sc, -7, -48, 72, 34, 8, 30, bias=180)
    # pallet rack: steel posts, shelf beams, pallets on two levels
    for xp in (-420, -284, -148, -12):
        for yp in (-260, -122):
            block(sc, xp, yp, 0, 12, 12, 150, "pt", ch=2, b=1.2, bias=180 if yp < -200 else 230)
    for lv in range(2):
        zk = 30 + lv * 70
        for yb in (-256, -130):
            block(sc, -408, yb, zk, 396, 4, 8, "dk", b=0, dark=0, bias=170 - lv if yb < -200 else 220 - lv)
        for j in range(3):
            pallet(sc, -402 + j * 136, -250, zk + 8, 112, 120, 9, bias=200 - lv, slots=3)
            if (j + lv) % 2 == 0:
                alu_work(sc, -376 + j * 136, -224, zk + 17, 60, 60, 26 - lv * 10, bias=195 - lv)
    for yp in (-260, -122):
        block(sc, -420, yp, 150, 420, 12, 10, "pt", b=1.2, bias=160 if yp < -200 else 210)
    # loading station with a pallet, fixture and work, push-button box
    block(sc, 166, -244, 0, 158, 128, 10, "dk", ch=4, b=0, dark=0, bias=170)
    block(sc, 160, -250, 10, 170, 140, 80, "pt", ch=6, b=2.5, bias=150)
    pallet(sc, 185, -230, 90, 120, 100, 10, bias=140)
    block(sc, 225, -196, 100, 40, 30, 40, "dk", ch=2, b=1, dark=0, bias=130)
    alu_work(sc, 228, -204, 106, 34, 8, 30, bias=125)
    block(sc, 300, -262, 60, 24, 12, 24, "dk", ch=2, b=1, dark=0, bias=120)
    # cell controller cabinet with a screen
    block(sc, 400, -2, 0, 54, 80, 180, "dk", ch=4, b=2, dark=0, bias=120)

    def scr(s_):
        q = lambda x, z: s_.P((x, -2.3, z))
        o = path(P([q(406, 120), q(448, 120), q(448, 166), q(406, 166)]), "scrn")
        o += path(P([q(410, 150), q(436, 150), q(436, 158), q(410, 158)]) + P([q(410, 134), q(442, 134), q(442, 142), q(410, 142)]), "scrl")
        a, b = s_.P((404, -2.3, 40)), s_.P((404, -2.3, 104))
        return o + path("M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1])), "mgrid")
    sc.raw(scr, ((404, -2.4, 40), (448, -2.3, 166)), bias=119)
    sc.note((-275, 100, 230), "工作機械", "同じ機種を並べ、どの機械でも同じ工程を加工できる")
    sc.note((10, -70, 50), "搬送台車（RGV）", "レール上を走り、パレットを運ぶ")
    sc.note((-300, -260, 150), "パレットラック", "治具付きのパレットを多数ためる")
    sc.note((245, -250, 100), "段取りステーション", "人が工作物を付け外しする")
    sc.note((427, -2, 110), "セル制御盤", "加工の順番と搬送を管理する")
