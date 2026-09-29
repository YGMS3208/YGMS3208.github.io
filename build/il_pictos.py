from il_base import *
import math

PICTOS = {}


def picto(key):
    def deco(fn):
        PICTOS[key] = fn
        return fn
    return deco


def lab(x, y, s, a="middle"):
    return text(x, y, s, a)


def gw(cx, cy, r, hub=0.28):
    return circ(cx, cy, r, "gw") + circ(cx, cy, r - 5, "grit") + circ(cx, cy, r * hub, "m2")


def insert(x, y, s=9, ang=0):
    """triangular cutting insert, tip at (x,y) pointing towards ang."""
    a = math.radians(ang)
    b1, b2 = a + math.radians(150), a - math.radians(150)
    return poly([(x, y), (x + s * 1.6 * math.cos(b1), y + s * 1.6 * math.sin(b1)), (x + s * 1.6 * math.cos(b2), y + s * 1.6 * math.sin(b2))], "t")


def chips(x, y, k=1):
    return path("M%s %s q%s -8 %s -2 q%s 4 %s -6" % (n(x), n(y), n(6 * k), n(10 * k), n(-4 * k), n(-2 * k)), "chip") + \
        path("M%s %s q%s -6 %s 0" % (n(x + 8 * k), n(y - 10), n(4 * k), n(8 * k)), "chip")


def chart(x, y, w, h, kind="sine", c="a"):
    s = rect(x, y, w, h, "m", 3)
    s += line(x + 6, y + h - 6, x + w - 6, y + h - 6, "o thin") + line(x + 6, y + 6, x + 6, y + h - 6, "o thin")
    x0, x1, ym, amp = x + 8, x + w - 8, y + h / 2, h * 0.28
    ps = []
    for i in range(41):
        t = i / 40
        xx = x0 + (x1 - x0) * t
        if kind == "sine":
            yy = ym + amp * math.sin(t * 4 * math.pi)
        elif kind == "rise":
            yy = y + h - 8 - (h - 16) * (1 - math.exp(-4 * t))
        elif kind == "ramp":
            yy = y + h - 8 - (h - 16) * min(1, t * 1.4) * (1 if t < 0.8 else 1)
        elif kind == "noise":
            yy = ym + amp * (0.6 * math.sin(t * 22) + 0.4 * math.sin(t * 57 + 1))
        elif kind == "peak":
            yy = y + h - 8 - (h - 16) * math.exp(-((t - 0.55) / 0.08) ** 2) - 3 * math.sin(t * 30) * 0.3
        elif kind == "step":
            yy = y + h - 8 - (h - 16) * (0.2 if t < 0.3 else 0.85 if t < 0.7 else 0.5)
        elif kind == "profile":
            yy = ym + amp * 0.35 * math.sin(t * 60) + amp * 0.2 * math.sin(t * 13)
        elif kind == "decay":
            yy = y + 10 + (h - 20) * (t * 0.15)
        else:
            yy = ym
        ps.append((xx, yy))
    s += pline(ps, c)
    return s


def dots(x, y, w, h, step=7, c="grain"):
    s = ""
    j = 0
    yy = y + step / 2
    while yy < y + h:
        xx = x + step / 2 + (step / 2 if j % 2 else 0)
        while xx < x + w:
            s += circ(xx, yy, 1.1, c)
            xx += step
        yy += step * 0.8
        j += 1
    return s


def bubbles(x, y, cnt=6, spread=30, hgt=40):
    s = ""
    for i in range(cnt):
        s += circ(x - spread / 2 + spread * ((i * 37) % 11) / 10, y - hgt * i / cnt, 2 + (i % 3), "bub")
    return s


def nozzle(x, y, ang=90, ln=18, w=8):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    ps = [(x - ux * ln + px * w / 2, y - uy * ln + py * w / 2), (x - ux * ln - px * w / 2, y - uy * ln - py * w / 2),
          (x - px * w / 5, y - py * w / 5), (x + px * w / 5, y + py * w / 5)]
    return poly(ps, "m3")


def ram(x, y, w, h):
    return rect(x, y, w, h, "m3")


def tank(x, y, w, h, level=0.7, c="fl"):
    s = rect(x, y + h * (1 - level), w, h * level, c)
    s += path("M%s %s L%s %s L%s %s L%s %s" % (n(x), n(y), n(x), n(y + h), n(x + w), n(y + h), n(x + w), n(y)), "tankw")
    return s


def furnace(x, y, w, h, door=True):
    s = rect(x, y, w, h, "m2", 4)
    s += rect(x + 8, y + 8, w - 16, h - 16, "hotin")
    return s


def conveyor(x, y, w, rolls=True):
    s = rect(x, y, w, 7, "m3", 3)
    if rolls:
        for xx in range(int(x) + 6, int(x + w) - 2, 14):
            s += circ(xx, y + 3.5, 2.2, "m")
    return s


def shaftpart(x, cy, ln, r):
    return shaft(x, cy, [(ln, r)], "w", "w2")


def lightning(x, y, s=1.0):
    return path("M%s %s l%s %s l%s 0 l%s %s l%s %s l%s 0Z" % (n(x), n(y), n(-6 * s), n(14 * s), n(6 * s), n(-4 * s), n(14 * s), n(12 * s), n(-18 * s), n(-6 * s)), "bolt")


def vcoil(cx, cy, L, r, turns):
    return '<g transform="translate(%s %s) rotate(90)">' % (n(cx), n(cy)) + coil(-L / 2, L / 2, 0, r, turns) + "</g>"


def body_block(x, y, w, h, d=30):
    return box(x, y, w, h, d, "w2", "w", "w3")


# ============================================================ turning / milling / drilling
@picto("turn")
def _():
    cy = 96
    s = rect(8, 40, 46, 118, "m2", 4) + lab(31, 172, "主軸台")
    s += rect(54, 56, 18, 80, "m", 2) + rect(58, 50, 10, 12, "m3") + rect(58, 130, 10, 12, "m3")
    s += shaft(72, cy, [(150, 28), (20, 18)], "w", "w2")
    s += rect(196, 136, 64, 22, "m3", 2) + insert(206, 125, 9, -100)
    s += chips(214, 124)
    s += rot(120, cy, 10, 38, -60, 60, "回転", 104, 150)
    s += arrow(276, 178, 226, 178, "送り", 251, 172)
    s += lab(240, 128, "バイト", "start")
    return s


@picto("vturn")
def _():
    s = ell(160, 164, 118, 24, "m2") + path("M42 164 L42 176 A118 24 0 0 0 278 176 L278 164", "m2")
    s += vcyl(160, 100, 58, 84, 20, "w", "w2") + ell(160, 100, 34, 8, "bg")
    s += rect(210, 20, 26, 60, "m3") + insert(222, 95, 9, 90)
    s += rot(160, 164, 132, 30, 150, 30, "テーブル回転", 160, 196)
    s += arrow(252, 30, 252, 70, "送り", 262, 52, "start")
    s += lab(82, 70, "工作物", "middle")
    return s


@picto("swiss")
def _():
    cy = 100
    s = rect(10, 60, 60, 80, "m2", 4) + lab(40, 158, "主軸（移動）")
    s += shaft(70, cy, [(170, 10)], "w", "w2")
    s += rect(150, 64, 26, 72, "m3", 2) + lab(163, 158, "ガイドブッシュ")
    s += insert(186, 88, 8, -90) + rect(180, 50, 12, 26, "m")
    s += arrow(30, 44, 80, 44, "Z軸送り", 55, 38)
    s += rot(214, cy, 6, 16, -60, 60)
    return s


@picto("oval")
def _():
    s = PICTOS["turn"]()
    s += arrow(236, 100, 236, 70, None, both=True) + lab(248, 84, "高速往復", "start")
    return s


@picto("crankmill")
def _():
    cy = 100
    s = shaft(10, cy, [(60, 14), (14, 30), (40, 12), (14, 30), (60, 14)], "w", "w2")
    s += circ(107, cy + 24, 56, "t") + circ(107, cy + 24, 40, "bg2")
    for k in range(10):
        a = 2 * math.pi * k / 10
        s += insert(107 + 40 * math.cos(a), cy + 24 + 40 * math.sin(a), 5, math.degrees(a) + 180)
    s += shaft(84, cy + 24, [(46, 12)], "w", "w2")
    s += rot(107, cy + 24, 66, 66, 200, 280, "カッタ回転", 60, 34)
    s += lab(240, 150, "ピンを追従加工", "middle")
    return s


@picto("mc_h")
def _():
    s = rect(10, 30, 70, 140, "m2", 4) + lab(45, 186, "コラム")
    s += rect(80, 74, 50, 36, "m3", 3)
    s += shaft(130, 92, [(22, 6)], "t", "t")
    s += ell(230, 176, 70, 14, "m3") + box(178, 70, 96, 100, 30, "m2", "m", "m3")
    s += box(186, 92, 60, 54, 24, "w2", "w", "w3")
    s += ell(186, 108, 5, 9, "bg") + chips(170, 110, -1)
    s += rot(140, 92, 7, 16, -70, 70, "主軸（水平）", 112, 64)
    s += rot(230, 176, 82, 18, 20, 160, "B軸（割出し）", 232, 198)
    s += lab(226, 62, "パレット")
    return s


@picto("mc_v")
def _():
    s = rect(20, 20, 60, 150, "m2", 4)
    s += rect(80, 26, 100, 40, "m3", 4) + rect(140, 66, 30, 22, "m2")
    s += shaft(150, 100, [(1, 1)], "o", "o") if False else ""
    s += rect(151, 88, 8, 30, "t")
    s += rect(96, 162, 190, 14, "m2") + box(120, 124, 110, 38, 24, "w2", "w", "w3")
    s += rot(155, 96, 16, 5, 200, 340, "主軸回転", 205, 94)
    s += arrow(110, 188, 280, 188, "X", 195, 184, both=True)
    s += chips(166, 124)
    return s


@picto("mc_5ax")
def _():
    s = rect(120, 14, 60, 40, "m3", 4) + rect(142, 54, 16, 34, "t")
    s += rect(40, 150, 240, 24, "m2", 3) + rect(60, 90, 26, 64, "m") + rect(234, 90, 26, 64, "m")
    s += rect(86, 120, 148, 18, "m3")
    s += ell(160, 118, 56, 14, "m") + gear(160, 106, 26, 44, 12, "w", 0, 0.34, 0.3) + ell(160, 104, 10, 4, "w2")
    s += rot(160, 128, 72, 20, 20, 160, "C軸", 160, 198)
    s += arrow(66, 76, 66, 110, "A軸（傾斜）", 60, 70, "middle", both=True)
    s += rot(150, 70, 14, 5, 200, 340, "主軸", 196, 72)
    return s


@picto("gantry")
def _():
    s = rect(20, 30, 24, 150, "m2") + rect(276, 30, 24, 150, "m2") + rect(14, 20, 292, 26, "m3", 3)
    s += rect(140, 46, 40, 44, "m2") + rect(154, 90, 12, 24, "t")
    s += rect(50, 166, 220, 12, "m3") + box(70, 124, 170, 42, 26, "w2", "w", "w3")
    s += path("M90 124 Q130 104 160 116 Q200 128 230 116", "o thin")
    s += arrow(60, 12, 260, 12, "門形フレーム上をヘッドが移動", 160, 8, both=True)
    return s


@picto("compact")
def _():
    s = PICTOS["mc_v"]()
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += circ(230 + 26 * math.cos(a), 44 + 10 * math.sin(a), 4, "t")
    s += lab(230, 76, "ATC（高速工具交換）")
    return s


@picto("gundrill")
def _():
    cy = 110
    s = shaft(150, cy, [(150, 34)], "w", "w2")
    s += path("M150 %s L240 %s" % (n(cy), n(cy)), "bgline2")
    s += rect(14, cy - 14, 40, 28, "m3", 3) + rect(54, cy - 3, 186, 6, "t")
    s += arrow(70, cy - 22, 130, cy - 22, "切削油（工具内部から高圧）", 100, cy - 30)
    s += arrow(140, cy + 20, 90, cy + 20, "切粉を排出", 115, cy + 36)
    s += arrow(20, 170, 110, 170, "送り", 65, 186)
    return s


@picto("transfer")
def _():
    s = rect(40, 20, 240, 50, "m3", 4) + lab(160, 50, "多軸ヘッド")
    for i in range(6):
        x = 64 + i * 38
        s += rect(x - 4, 70, 8, 40, "t")
    s += box(40, 126, 230, 40, 30, "w2", "w", "w3")
    for i in range(6):
        s += ell(64 + i * 38 + 9, 119, 5, 2.5, "bg")
    s += arrow(296, 40, 296, 100, "一括送り", 290, 116, "end")
    return s


@picto("finebore")
def _():
    s = rect(40, 60, 240, 110, "w") + rect(40, 92, 240, 46, "bg")
    s += rect(10, 108, 180, 14, "t") + insert(190, 106, 7, -90)
    s += rot(120, 115, 8, 22, -60, 60, "回転", 120, 184)
    s += arrow(200, 40, 250, 40, "送り", 225, 34)
    s += lab(250, 158, "穴（断面）")
    return s


@picto("edm")
def _():
    s = tank(30, 90, 260, 90, 0.8)
    s += rect(130, 20, 60, 30, "m3", 3) + rect(150, 50, 20, 60, "t")
    s += rect(60, 130, 200, 40, "w")
    s += sparks(160, 124, 8, 7, -170, -10)
    s += lab(214, 100, "放電", "start") + lab(60, 110, "加工液", "start") + lab(160, 16, "電極")
    return s


@picto("laser")
def _():
    s = path("M130 20 L190 20 L180 64 L140 64Z", "m3") + rect(150, 64, 20, 18, "m2")
    s += line(160, 82, 160, 128, "beam") + sparks(160, 132, 12, 7, -10, 190)
    s += poly([(30, 130), (290, 130), (300, 146), (40, 146)], "w") + poly([(40, 146), (300, 146), (300, 152), (40, 152)], "w3")
    s += path("M60 138 L160 138", "kerf")
    s += arrow(180, 176, 260, 176, "ヘッド移動", 220, 192)
    s += lab(196, 100, "レーザ光", "start")
    return s


# ============================================================ grinding
@picto("cyl_grind")
def _():
    cy = 120
    s = poly([(24, cy - 14), (52, cy), (24, cy + 14)], "m2") + poly([(296, cy - 14), (268, cy), (296, cy + 14)], "m2")
    s += shaft(52, cy, [(40, 16), (120, 24), (56, 16)], "w", "w2")
    s += gw(150, 52, 44)
    s += rot(150, 52, 54, 54, 200, 250, "砥石", 90, 22)
    s += rot(110, cy, 9, 34, 60, -60)
    s += arrow(220, 160, 170, 160, "切込み", 200, 176) if False else ""
    s += nozzle(208, 80, 140, 20) + drops(206, 82, 3, 20, 20, 140)
    s += lab(200, 180, "両センタで支持")
    return s


@picto("int_grind")
def _():
    s = rect(10, 50, 60, 110, "m2", 4) + rect(70, 64, 14, 82, "m")
    s += rect(84, 50, 110, 110, "w") + rect(84, 76, 110, 58, "bg")
    s += rect(150, 100, 150, 10, "m3") + circ(146, 105, 20, "gw")
    s += rot(146, 105, 26, 26, 200, 300)
    s += lab(230, 94, "小径砥石（クイル）", "middle") + lab(140, 178, "工作物（断面）")
    s += arrow(270, 130, 200, 130, "トラバース", 240, 146, both=True)
    return s


@picto("surf_grind")
def _():
    s = gw(160, 66, 44) + rect(140, 14, 40, 10, "m3")
    s += rect(40, 116, 240, 14, "w") + rect(30, 130, 260, 26, "m2") + lab(160, 147, "マグネットテーブル")
    s += arrow(60, 176, 260, 176, "テーブル往復", 160, 192, both=True)
    s += rot(160, 66, 54, 54, 200, 250)
    return s


@picto("dd_grind")
def _():
    s = rect(70, 40, 40, 130, "gw", 4) + rect(210, 40, 40, 130, "gw", 4)
    s += rect(20, 90, 50, 30, "m3") + rect(250, 90, 50, 30, "m3")
    for i, y in enumerate((50, 84, 118, 152)):
        s += rect(140, y, 40, 24, "w", 3)
    s += arrow(160, 20, 160, 44, None) + lab(160, 14, "工作物を通過させる")
    s += lab(90, 188, "砥石") + lab(230, 188, "砥石")
    return s


@picto("centerless")
def _():
    s = gw(90, 104, 66) + lab(90, 190, "研削砥石")
    s += circ(236, 112, 46, "rb") + circ(236, 112, 12, "m2") + lab(236, 190, "調整車")
    s += poly([(150, 128), (182, 128), (176, 150), (150, 150)], "m3") + lab(160, 166, "支持刃")
    s += circ(168, 114, 14, "w") + circ(168, 114, 3, "w2")
    s += rot(90, 104, 76, 76, -40, 10) + rot(236, 112, 56, 56, 200, 250) + rot(168, 114, 20, 20, 120, 60)
    return s


@picto("crank_grind")
def _():
    cy = 104
    s = shaft(10, cy, [(60, 14), (12, 34), (30, 12), (12, 34), (60, 14)], "w", "w2")
    s += circ(92, cy, 30, "o dash")
    s += gw(200, 70, 56)
    s += rot(92, cy, 40, 40, 20, 110, "ピンが公転", 60, 172)
    s += arrow(270, 150, 230, 120, "砥石台が追従", 272, 170, "middle", both=True)
    return s


@picto("cam_grind")
def _():
    s = ""
    ps = []
    for k in range(60):
        ph = 2 * math.pi * k / 60
        r = 36 + 26 * max(0.0, math.cos(ph)) ** 3
        ps.append((110 + r * math.cos(ph), 104 + r * math.sin(ph)))
    s += poly(ps, "w") + circ(110, 104, 10, "w2")
    s += gw(236, 104, 46)
    s += rot(110, 104, 70, 70, 200, 290, "回転", 70, 26)
    s += arrow(270, 176, 210, 176, "回転角に同期して前後", 240, 192, both=True)
    return s


@picto("thread_grind")
def _():
    cy = 120
    s = shaft(20, cy, [(280, 26)], "w", "w2")
    for x in range(30, 296, 10):
        s += line(x, cy - 26, x + 6, cy + 26, "o thin")
    s += "<g transform=\"rotate(-12 160 60)\">" + rect(110, 46, 100, 24, "gw", 4) + "</g>"
    s += arrow(40, 176, 280, 176, "リードに合わせて送り", 160, 192)
    return s


@picto("ball_groove")
def _():
    s = path("M60 40 L260 40 L260 170 L60 170Z", "w") + path("M100 40 Q160 150 220 40Z", "bg")
    s += circ(160, 120, 22, "gw") + rect(154, 20, 12, 96, "m3")
    s += lab(160, 190, "ボール溝（断面）")
    s += rot(160, 120, 30, 30, 200, 300)
    return s


@picto("ball_grind")
def _():
    s = rect(40, 40, 240, 34, "m2") + rect(40, 126, 240, 34, "m2")
    for i in range(7):
        x = 64 + i * 32
        s += circ(x, 100, 18, "ball")
    s += lab(160, 32, "回転盤（溝付き）") + lab(160, 180, "固定盤（溝付き）")
    s += rot(160, 57, 150, 20, 200, 230)
    return s


@picto("superfinish")
def _():
    cy = 126
    s = shaft(20, cy, [(260, 36)], "w", "w2")
    s += rect(130, 50, 60, 40, "t", 3) + rect(146, 20, 28, 30, "m3")
    s += arrow(110, 70, 210, 70, None, both=True) + lab(160, 44, "微小振動（オシレーション）") if False else arrow(100, 70, 120, 70, None) + arrow(220, 70, 200, 70, None)
    s += lab(160, 14, "砥石を低圧で押し当て揺動")
    s += rot(60, cy, 10, 40, -60, 60, "回転", 60, 186)
    return s


@picto("hone")
def _():
    s = rect(60, 60, 200, 130, "w") + rect(110, 60, 100, 130, "bg")
    for i in range(8):
        y = 70 + i * 15
        s += line(112, y, 208, y + 12, "hatch") + line(112, y + 12, 208, y, "hatch")
    s += rect(152, 10, 16, 110, "m3") + rect(128, 110, 64, 50, "m2", 4)
    s += rect(122, 116, 8, 38, "gwr") + rect(190, 116, 8, 38, "gwr")
    s += arrow(236, 40, 236, 90, None, both=True) + lab(244, 66, "往復", "start")
    s += rot(160, 36, 20, 6, 200, 340, "回転", 108, 32)
    s += lab(160, 196, "ボア（断面）：クロスハッチ")
    return s


@picto("lap")
def _():
    s = ell(160, 140, 130, 30, "m2") + path("M30 140 L30 150 A130 30 0 0 0 290 150 L290 140", "m2") + ell(160, 140, 130, 30, "m")
    s += dots(80, 128, 160, 20, 9, "grain")
    for x in (110, 160, 210):
        s += vcyl(x, 110, 22, 16, 5, "w", "w2")
    s += rot(160, 140, 144, 36, 20, 160, "ラップ盤（砥粒）", 160, 196)
    return s


@picto("deburr")
def _():
    s = rect(40, 80, 240, 90, "w") + rect(40, 112, 240, 18, "bg") + rect(150, 80, 18, 50, "bg")
    s += nozzle(159, 40, 90, 34, 10) + path("M159 40 L159 104", "jet")
    s += lab(190, 32, "高圧水・ブラシ", "start") + lab(160, 188, "交差穴のバリを除去")
    return s


@picto("fillet")
def _():
    cy = 104
    s = shaft(10, cy, [(80, 16), (14, 44), (80, 22), (14, 44), (80, 16)], "w", "w2")
    s += circ(112, 60, 12, "t") + circ(186, 60, 12, "t")
    s += arrow(112, 24, 112, 44, None) + arrow(186, 24, 186, 44, None)
    s += lab(150, 18, "隅Rにローラを押付け")
    return s


# ============================================================ gear
@picto("hob")
def _():
    s = gear3d(150, 132, 52, 62, 24, 6, -5, 0, "w", "w3", tw=0.5) + circ(150, 132, 18, "bg")
    s += "<g transform=\"rotate(-8 150 50)\">" + rect(70, 34, 160, 34, "t", 6)
    for x in range(78, 226, 9):
        s += line(x, 34, x + 6, 68, "o thin")
    s += rect(40, 44, 30, 14, "m3") + rect(230, 44, 30, 14, "m3") + "</g>"
    s += rot(150, 51, 86, 22, 200, 260, "ホブ回転", 60, 20)
    s += rot(150, 132, 70, 70, 20, 70, "同期回転", 250, 190)
    s += arrow(290, 90, 290, 150, "送り", 298, 124, "start")
    return s


@picto("shaper")
def _():
    s = gear3d(160, 138, 52, 62, 22, 6, -5, 0, "w", "w3", tw=0.5) + circ(160, 138, 16, "bg")
    s += gear(160, 44, 26, 34, 12, "t", 0, 0.34, 0.5) + rect(152, 6, 16, 36, "m3")
    s += arrow(206, 20, 206, 70, None, both=True) + lab(214, 48, "上下往復", "start")
    s += lab(96, 44, "ピニオンカッタ", "middle")
    return s


@picto("skive")
def _():
    s = circ(160, 104, 86, "w") + path(gear_d(160, 104, 70, 60, 36, 0, 0.5), "bg")
    s += "<g transform=\"rotate(20 190 104)\">" + gear(196, 104, 26, 34, 14, "t", 0, 0.9, 0.5) + "</g>"
    s += rot(160, 104, 96, 96, -30, 30, "高速同期回転", 250, 30)
    s += lab(160, 196, "内歯車を軸交差角付きカッタで創成")
    return s


@picto("gchamfer")
def _():
    s = gear3d(150, 110, 60, 74, 20, 6, -5, 0, "w", "w3", tw=0.5) + circ(150, 110, 20, "bg")
    s += gear(262, 60, 18, 26, 10, "t", 0.2, 1, 0.5)
    s += lab(262, 104, "転造面取り工具")
    s += arrow(228, 150, 200, 126, "歯端のエッジ", 250, 176)
    return s


@picto("shave")
def _():
    s = gear3d(150, 132, 52, 62, 24, 6, -5, 0, "w", "w3", tw=0.5) + circ(150, 132, 16, "bg")
    s += "<g transform=\"rotate(12 160 44)\">" + gear(160, 44, 34, 44, 18, "t", 0, 0.34, 0.5)
    for k in range(18):
        a = 2 * math.pi * k / 18
        s += line(160 + 36 * math.cos(a), 44 + 12 * math.sin(a), 160 + 42 * math.cos(a), 44 + 14 * math.sin(a), "o thin")
    s += "</g>"
    s += lab(250, 30, "シェービングカッタ", "middle") + lab(250, 190, "軸を交差させて噛み合わせる", "middle")
    return s


@picto("ggrind")
def _():
    s = gear3d(150, 140, 46, 56, 22, 6, -5, 0, "w", "w3", tw=0.5) + circ(150, 140, 14, "bg")
    s += "<g transform=\"rotate(-8 150 50)\">" + rect(50, 30, 200, 44, "gw", 8)
    for x in range(60, 244, 10):
        s += line(x, 30, x + 8, 74, "gline")
    s += "</g>"
    s += lab(150, 20, "ねじ状砥石（連続創成研削）")
    s += rot(150, 140, 66, 66, 20, 80, "同期回転", 260, 190)
    return s


@picto("ghone")
def _():
    s = circ(160, 104, 88, "gw") + path(gear_d(160, 104, 68, 60, 34, 0, 0.5), "bg")
    s += gear(160, 104, 42, 54, 24, "w", 0.07, 1, 0.5) + circ(160, 104, 14, "bg")
    s += lab(160, 12, "内歯形の砥石で歯面を仕上げ")
    s += rot(160, 104, 98, 98, 20, 70)
    return s


@picto("hypcut")
def _():
    cx, cy = 150, 130
    s = ell(cx + 6, cy + 4, 110, 42, "w3") + ell(cx, cy, 110, 42, "w") + ell(cx, cy, 70, 26, "bg")
    for k in range(40):
        a = 2 * math.pi * k / 40
        s += line(cx + 72 * math.cos(a), cy + 27 * math.sin(a), cx + 108 * math.cos(a + 0.05), cy + 41 * math.sin(a + 0.05), "o thin")
    s += vcyl(236, 40, 34, 44, 14, "t", "t")
    for k in range(10):
        a = 2 * math.pi * k / 10
        s += rect(236 + 36 * math.cos(a) - 2, 70 + 10 * math.sin(a), 4, 10, "m3")
    s += lab(236, 26, "カッタヘッド") + rot(236, 40, 54, 18, 200, 320)
    return s


@picto("hyplap")
def _():
    cx, cy = 190, 110
    s = ell(cx + 6, cy + 4, 100, 60, "w3") + ell(cx, cy, 100, 60, "w") + ell(cx, cy, 60, 36, "bg")
    for k in range(40):
        a = 2 * math.pi * k / 40
        s += line(cx + 62 * math.cos(a), cy + 37 * math.sin(a), cx + 98 * math.cos(a + 0.05), cy + 59 * math.sin(a + 0.05), "o thin")
    s += shaft(10, 150, [(60, 10)], "w", "w2") + path("M70 136 L100 126 L100 176 L70 164Z", "w2") + ell(100, 151, 8, 25, "w")
    s += dots(96, 128, 30, 30, 6, "grain") + lab(60, 110, "ラップ剤", "middle")
    s += rot(cx, cy, 110, 70, 20, 80, "ペアで回転", 280, 196)
    return s


@picto("broach")
def _():
    s = rect(110, 60, 100, 90, "w") + rect(110, 94, 100, 22, "bg")
    s += rect(10, 98, 300, 14, "t")
    for x in range(40, 300, 9):
        s += poly([(x, 98), (x + 5, 90 - (x - 40) * 0.02), (x + 7, 98)], "t")
    s += arrow(236, 170, 296, 170, "引き抜き", 266, 186)
    s += lab(160, 50, "1回の通過で形状を仕上げる")
    return s


@picto("rolling")
def _():
    cy = 104
    s = shaft(20, cy, [(280, 20)], "w", "w2")
    for x in range(120, 200, 6):
        s += line(x, cy - 20, x + 4, cy + 20, "o thin")
    s += circ(160, 50, 32, "t") + circ(160, 158, 32, "t")
    for k in range(24):
        a = 2 * math.pi * k / 24
        s += line(160 + 28 * math.cos(a), 50 + 28 * math.sin(a), 160 + 32 * math.cos(a), 50 + 32 * math.sin(a), "o thin")
        s += line(160 + 28 * math.cos(a), 158 + 28 * math.sin(a), 160 + 32 * math.cos(a), 158 + 32 * math.sin(a), "o thin")
    s += rot(160, 50, 40, 40, 200, 250) + rot(160, 158, 40, 40, 20, 70)
    s += lab(250, 36, "転造ダイス") + lab(60, 150, "塑性変形で歯・ねじを成形", "start")
    return s


# ============================================================ casting
@picto("melt")
def _():
    s = path("M40 60 L150 60 L140 176 L50 176Z", "m2") + path("M54 74 L136 74 L130 166 L60 166Z", "hotin")
    s += rect(58, 96, 72, 70, "h") + heat(80, 90, 3, 12)
    s += path("M200 110 L270 110 L262 160 L208 160Z", "m2") + rect(212, 124, 46, 34, "h")
    s += path("M136 80 Q170 70 204 108", "pour")
    s += lab(95, 192, "溶解炉") + lab(235, 180, "取鍋") + lab(160, 40, "約700℃（Al）／1,450℃（鋳鉄）")
    return s


@picto("degas")
def _():
    s = path("M70 70 L250 70 L240 180 L80 180Z", "m2") + rect(86, 90, 148, 86, "h")
    s += rect(154, 20, 12, 120, "m3") + rect(134, 134, 52, 12, "t", 3)
    s += bubbles(160, 124, 8, 90, 34)
    s += arrow(200, 30, 170, 30, "不活性ガス", 230, 26)
    s += rot(160, 140, 36, 8, 20, 160)
    s += lab(160, 196, "回転脱ガスで水素・介在物を除去")
    return s


@picto("hpdc")
def _():
    s = rect(150, 30, 34, 140, "m2") + rect(184, 30, 34, 140, "m3")
    s += path("M178 70 L190 70 L190 130 L178 130Z", "h")
    s += rect(40, 128, 110, 20, "m") + rect(60, 132, 70, 12, "h")
    s += rect(20, 130, 40, 16, "m3")
    s += arrow(20, 168, 110, 168, "高速射出", 65, 184)
    s += lab(167, 22, "固定型") + lab(201, 22, "可動型")
    s += arrow(290, 100, 230, 100, "型締め", 262, 92)
    s += lab(96, 118, "スリーブ")
    return s


@picto("lpdc")
def _():
    s = rect(60, 118, 200, 70, "m2", 4) + rect(74, 132, 172, 50, "h")
    s += rect(154, 60, 12, 80, "m3") + path("M157 64 L163 64 L163 130 L157 130Z", "h")
    s += rect(90, 30, 140, 30, "m3") + path("M130 44 L190 44 L184 56 L136 56Z", "h")
    s += arrow(96, 110, 96, 140, None) + lab(100, 106, "空気圧", "start")
    s += arrow(172, 120, 172, 72, "下から静かに充填", 230, 96)
    return s


@picto("gravity")
def _():
    s = "<g transform=\"rotate(-14 180 120)\">" + rect(140, 70, 120, 100, "m2") + path("M170 90 L230 90 L220 150 L180 150Z", "h") + "</g>"
    s += path("M40 40 L110 40 L102 90 L48 90Z", "m2") + rect(52, 52, 46, 34, "h")
    s += path("M104 58 Q140 50 168 84", "pour")
    s += lab(76, 106, "取鍋") + lab(200, 190, "金型を傾けながら注湯")
    return s


@picto("sand")
def _():
    s = rect(40, 60, 240, 110, "sand") + dots(42, 62, 236, 106, 8, "grain")
    s += line(40, 115, 280, 115, "o")
    s += path("M90 100 L230 100 Q240 115 230 130 L90 130 Q80 115 90 100Z", "h")
    s += rect(150, 60, 14, 40, "h")
    s += path("M120 20 L180 20 L172 50 L128 50Z", "m2") + path("M160 50 Q160 56 157 60", "pour")
    s += lab(290, 90, "上型", "end") + lab(290, 150, "下型", "end") + lab(60, 190, "生砂の鋳型", "start")
    return s


@picto("core")
def _():
    s = rect(60, 40, 200, 40, "m3") + lab(160, 64, "ブローヘッド")
    s += rect(60, 90, 96, 80, "m2") + rect(164, 90, 96, 80, "m2")
    s += path("M100 110 Q160 96 220 110 L220 150 Q160 164 100 150Z", "sand") + dots(100, 104, 120, 56, 8, "grain")
    for x in (120, 160, 200):
        s += arrow(x, 76, x, 100, None)
    s += lab(160, 190, "砂を吹き込み、ガス・熱で固める")
    return s


@picto("invest")
def _():
    s = rect(150, 20, 20, 30, "m2")
    s += rect(156, 50, 8, 110, "shell")
    for y in (70, 100, 130):
        for d in (-1, 1):
            s += path("M%s %s l%s -6 l%s 14 l%s 6" % (n(160 + 4 * d), n(y), n(24 * d), n(10 * d), n(-30 * d)), "shell")
            s += circ(160 + 44 * d, y + 4, 12, "shell")
    s += path("M80 16 L130 16 L126 40 L84 40Z", "m2") + path("M126 26 Q146 22 158 40", "pour")
    s += lab(160, 186, "セラミックシェル（ワックスを溶出）") + lab(60, 60, "真空溶解", "middle")
    return s


@picto("trim")
def _():
    s = rect(110, 16, 100, 30, "m3") + rect(120, 46, 80, 20, "t")
    s += rect(80, 110, 160, 16, "w") + rect(40, 114, 40, 8, "w2") + rect(240, 114, 40, 8, "w2")
    s += rect(90, 126, 140, 30, "t") + rect(60, 156, 200, 20, "m2")
    s += arrow(160, 70, 160, 104, "打ち抜き", 200, 90)
    s += lab(60, 104, "湯口・バリ", "middle")
    return s


@picto("shakeout")
def _():
    s = path("M40 110 L280 110", "gridbar")
    for x in range(50, 280, 16):
        s += line(x, 106, x, 114, "o")
    s += rect(110, 70, 100, 40, "w") + dots(40, 130, 240, 50, 9, "grain")
    s += arrow(40, 90, 60, 80, None, both=True) + arrow(280, 90, 260, 80, None, both=True)
    s += lab(160, 50, "振動で中子砂を落とす")
    return s


@picto("blast")
def _():
    s = circ(80, 70, 34, "m2") + circ(80, 70, 10, "m3")
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += line(80 + 12 * math.cos(a), 70 + 12 * math.sin(a), 80 + 32 * math.cos(a), 70 + 32 * math.sin(a), "o")
    for i in range(14):
        t = i / 14
        s += circ(120 + 110 * t + (i % 3) * 4, 90 + 40 * t + (i % 2) * 8, 2.2, "shot")
    s += box(200, 120, 80, 50, 20, "w2", "w", "w3")
    s += rot(80, 70, 44, 44, 200, 300, "インペラ", 80, 130)
    s += lab(210, 70, "投射材（鋼球）", "middle")
    return s


# ============================================================ forging & forming
@picto("hotforge")
def _():
    s = rect(80, 14, 160, 30, "m3") + rect(96, 44, 128, 30, "t")
    s += rect(96, 136, 128, 30, "t") + rect(80, 166, 160, 20, "m2")
    s += path("M100 110 Q120 96 160 98 Q200 96 220 110 L240 114 L240 120 L220 124 Q200 136 160 134 Q120 136 100 124 L80 120 L80 114Z", "h")
    s += heat(150, 92, 3, 10)
    s += arrow(270, 20, 270, 80, "打撃・加圧", 262, 100, "end")
    s += lab(60, 118, "バリ", "end") + lab(160, 196, "約1,200℃の素材を金型で成形")
    return s


@picto("coldforge")
def _():
    s = rect(128, 10, 64, 20, "m3") + rect(142, 30, 36, 60, "t")
    s += path("M90 90 L142 90 L142 150 L150 150 L150 190 L170 190 L170 150 L178 150 L178 90 L230 90 L230 190 L90 190Z", "m2")
    s += rect(142, 96, 36, 54, "w") + rect(150, 150, 20, 36, "w")
    s += arrow(210, 20, 210, 70, "加圧", 220, 48, "start")
    s += arrow(186, 160, 186, 186, None) + lab(196, 176, "押出し", "start")
    s += lab(60, 140, "常温", "middle")
    return s


@picto("header")
def _():
    s = rect(10, 60, 300, 90, "m2", 4)
    stages = [(18, 12, 20), (18, 16, 18), (22, 22, 16), (26, 22, 14), (30, 26, 12)]
    for i, (hw, hh, sw_) in enumerate(stages):
        x = 40 + i * 56
        s += rect(x - 18, 70, 36, 70, "m", 3)
        s += rect(x - 4, 100, 8, 36, "w") + rect(x - hw / 2, 100 - hh / 2 - 6, hw, hh / 2 + 6, "w")
    s += shaft(0, 40, [(40, 5)], "w", "w2") + lab(56, 32, "線材", "start")
    s += arrow(40, 170, 280, 170, "多段で順に成形（毎分100個以上）", 160, 190)
    return s


@picto("indheat")
def _():
    cy = 104
    s = shaft(20, cy, [(280, 24)], "h", "h")
    for x in range(100, 220, 12):
        s += path("M%s %s a6 34 0 0 1 0 68" % (n(x), n(cy - 34)), "coilcu")
    s += heat(130, 60, 4, 14)
    s += arrow(30, 160, 110, 160, "素材を送る", 70, 178)
    s += lab(160, 186, "高周波コイル") if False else lab(250, 160, "誘導コイル", "middle")
    return s


@picto("saw")
def _():
    cy = 118
    s = shaft(20, cy, [(260, 26)], "w", "w2")
    s += circ(170, 70, 54, "t")
    for k in range(36):
        a = 2 * math.pi * k / 36
        s += poly([(170 + 54 * math.cos(a), 70 + 54 * math.sin(a)), (170 + 60 * math.cos(a + 0.05), 70 + 60 * math.sin(a + 0.05)), (170 + 54 * math.cos(a + 0.12), 70 + 54 * math.sin(a + 0.12))], "t")
    s += circ(170, 70, 12, "m2")
    s += rot(170, 70, 68, 68, 200, 260) + arrow(250, 20, 250, 60, "切込み", 258, 44, "start")
    return s


@picto("upset")
def _():
    cy = 110
    s = shaft(10, cy, [(170, 8)], "w", "w2")
    s += rect(120, 80, 20, 60, "cu") + lab(130, 156, "電極")
    s += ell(210, cy, 30, 26, "h") + rect(250, 70, 30, 80, "m3")
    s += arrow(20, 60, 90, 60, "押し込み", 55, 52)
    s += lab(210, 60, "通電加熱で据え込み")
    return s


@picto("ringroll")
def _():
    s = circ(160, 104, 70, "h") + circ(160, 104, 46, "bg")
    s += circ(160, 104 - 58, 10, "m3") + lab(186, 44, "マンドレル", "start")
    s += circ(160, 104 + 110, 44, "t")
    s += rot(160, 104, 80, 80, 200, 250, "リング回転しながら径が拡大", 160, 18)
    s += arrow(160, 30, 160, 44, None)
    return s


@picto("straighten")
def _():
    cy = 116
    s = path("M30 %s Q160 %s 290 %s" % (n(cy - 6), n(cy + 10), n(cy - 6)), "tube1") + path("M30 %s Q160 %s 290 %s" % (n(cy - 6), n(cy + 10), n(cy - 6)), "tube2")
    s += poly([(50, 134), (70, 134), (60, 122)], "m2") + poly([(250, 134), (270, 134), (260, 122)], "m2")
    s += rect(140, 40, 40, 50, "m3") + arrow(160, 20, 160, 100, None)
    s += rect(210, 140, 30, 30, "m", 3) + line(225, 140, 225, 124, "o")
    s += lab(160, 188, "振れを測って曲がりをプレスで戻す")
    return s


@picto("draw")
def _():
    cy = 104
    s = shaft(10, cy, [(130, 18)], "w", "w2")
    s += path("M130 60 L170 60 L170 %s L150 %s L150 %s L170 %s L170 148 L130 148 L130 %s L140 %s L140 %s L130 %sZ" % (
        n(cy - 12), n(cy - 10), n(cy + 10), n(cy + 12), n(cy + 20), n(cy + 18), n(cy - 18), n(cy - 20)), "t")
    s += shaft(170, cy, [(130, 10)], "w", "w2")
    s += arrow(230, 150, 300, 150, "引き抜き", 265, 168)
    s += lab(150, 50, "ダイス")
    return s


@picto("bend")
def _():
    s = circ(150, 110, 50, "t") + circ(150, 110, 10, "m3")
    s += path("M20 60 L150 60 A50 50 0 0 1 200 110 L200 190", "tube1") + path("M20 60 L150 60 A50 50 0 0 1 200 110 L200 190", "tube2")
    s += rect(80, 44, 50, 12, "m3")
    s += rot(150, 110, 70, 70, -60, 20, "曲げ型が回転", 250, 60)
    return s


@picto("coiling")
def _():
    s = circ(40, 80, 14, "m2") + circ(40, 128, 14, "m2")
    s += path("M10 104 L120 104", "wire") + rect(120, 88, 14, 32, "m3")
    s += coil(150, 290, 104, 40, 4)
    s += arrow(20, 170, 110, 170, "線材送り", 65, 186)
    s += lab(210, 30, "コイリングピンで曲げる")
    return s


@picto("setting")
def _():
    s = rect(80, 20, 160, 20, "m3") + rect(80, 170, 160, 16, "m2")
    s += vcoil(160, 104, 124, 44, 6)
    s += arrow(270, 40, 270, 100, "押し縮める", 262, 118, "end")
    return s


@picto("finform")
def _():
    s = circ(110, 60, 36, "t") + circ(110, 150, 36, "t")
    for k in range(20):
        a = 2 * math.pi * k / 20
        s += line(110 + 32 * math.cos(a), 60 + 32 * math.sin(a), 110 + 40 * math.cos(a), 60 + 40 * math.sin(a), "o")
        s += line(110 + 32 * math.cos(a), 150 + 32 * math.sin(a), 110 + 40 * math.cos(a), 150 + 40 * math.sin(a), "o")
    s += path("M10 105 L80 105", "wire2")
    ps = [(140 + i * 8, 105 + (10 if i % 2 else -10)) for i in range(20)]
    s += pline([(80, 105)] + ps, "wire2")
    s += lab(240, 150, "波形フィン")
    return s


@picto("rollform")
def _():
    s = ""
    for i in range(5):
        x = 50 + i * 55
        s += circ(x, 80, 20, "t") + circ(x, 128, 20, "t")
    s += path("M10 104 L300 104", "wire2")
    s += lab(160, 170, "段階的に曲げて断面をつくる")
    s += arrow(30, 186, 290, 186, None)
    return s


# ============================================================ press
@picto("blankline")
def _():
    s = circ(40, 90, 30, "w2") + circ(40, 90, 10, "m2") + lab(40, 140, "コイル")
    s += path("M40 60 Q80 60 90 90 L130 90", "strip")
    for i in range(3):
        s += circ(100 + i * 12, 82, 5, "m") + circ(106 + i * 12, 98, 5, "m")
    s += lab(112, 118, "レベラ")
    s += rect(150, 30, 70, 20, "m3") + rect(160, 50, 50, 14, "t") + rect(160, 94, 50, 12, "t") + rect(150, 106, 70, 20, "m2")
    s += path("M130 90 L220 90", "strip")
    for i in range(4):
        s += poly([(240, 140 - i * 6), (300, 140 - i * 6), (296, 146 - i * 6), (244, 146 - i * 6)], "w")
    s += lab(270, 170, "ブランク")
    return s


@picto("drawpress")
def _():
    s = rect(110, 10, 100, 24, "m3") + path("M126 34 L194 34 L194 96 Q194 110 180 110 L140 110 Q126 110 126 96Z", "t")
    s += rect(60, 110, 60, 16, "m2") + rect(200, 110, 60, 16, "m2")
    s += path("M40 126 L112 126 Q122 126 122 136 L122 170 L198 170 L198 136 Q198 126 208 126 L280 126 L280 186 L40 186Z", "t")
    s += path("M40 108 L118 108 Q126 108 126 118 L126 164 L194 164 L194 118 Q194 108 202 108 L280 108", "sheet")
    s += arrow(236, 20, 236, 70, "パンチ下降", 244, 46, "start")
    s += lab(90, 102, "しわ押さえ") + lab(160, 198, "ダイ")
    return s


@picto("transferpress")
def _():
    s = rect(10, 20, 300, 24, "m3") + rect(10, 160, 300, 24, "m2")
    shapes = ["M0 0 L40 0", "M0 0 Q20 16 40 0", "M0 0 L6 0 L10 14 L30 14 L34 0 L40 0", "M0 0 L6 0 L10 16 L30 16 L34 0 L40 0"]
    for i in range(4):
        x = 30 + i * 72
        s += rect(x, 44, 50, 22, "t") + rect(x, 136, 50, 24, "t")
        s += "<g transform=\"translate(%s 116)\">" % n(x + 5) + path(shapes[i], "sheet") + "</g>"
    s += arrow(40, 100, 280, 100, "トランスファで次工程へ搬送", 160, 94)
    s += lab(60, 196, "1台の中で絞り→トリム→曲げを連続", "start")
    return s


@picto("progressive")
def _():
    s = rect(20, 96, 280, 18, "strip")
    for i in range(5):
        x = 44 + i * 52
        if i == 0:
            s += circ(x, 105, 5, "bg")
        elif i < 4:
            s += rect(x - 10, 99, 20, 12, "w") + circ(x, 105, 4, "bg")
        else:
            s += rect(x - 12, 99, 24, 12, "bg")
        s += rect(x - 16, 40, 32, 40, "t")
    s += rect(20, 20, 280, 20, "m3") + rect(20, 130, 280, 24, "t") + rect(20, 154, 280, 18, "m2")
    s += arrow(40, 186, 280, 186, "帯材を送りながら順に加工", 160, 200)
    return s


@picto("fineblank")
def _():
    s = rect(40, 70, 90, 22, "t") + rect(190, 70, 90, 22, "t") + lab(85, 62, "板押さえ（V突起）")
    s += poly([(118, 92), (124, 92), (121, 98)], "t") + poly([(196, 92), (202, 92), (199, 98)], "t")
    s += rect(40, 98, 280, 14, "sheet2")
    s += rect(130, 50, 60, 48, "t") + lab(160, 44, "パンチ")
    s += rect(40, 112, 90, 40, "t") + rect(190, 112, 90, 40, "t") + rect(132, 112, 56, 30, "m2") + lab(160, 170, "逆押さえ")
    s += arrow(300, 30, 300, 90, None) + lab(292, 24, "3動作", "end")
    return s


@picto("hotstamp")
def _():
    s = rect(10, 60, 130, 70, "m2", 4) + rect(18, 68, 114, 54, "hotin") + rect(30, 100, 90, 8, "h")
    s += lab(75, 146, "加熱炉 900〜950℃")
    s += arrow(140, 104, 176, 104, None)
    s += rect(190, 20, 110, 22, "m3") + rect(200, 42, 90, 30, "t") + rect(200, 118, 90, 30, "t") + rect(190, 148, 110, 22, "m2")
    s += path("M202 96 Q245 80 288 96", "hotsheet")
    for x in range(212, 290, 16):
        s += circ(x, 57, 3, "fdot") + circ(x, 133, 3, "fdot")
    s += lab(245, 190, "水冷金型で成形＋焼入れ")
    return s


@picto("hem")
def _():
    s = path("M40 140 L260 140 L260 150 L40 150Z", "w") + path("M60 128 L250 128", "sheet")
    s += path("M250 128 Q268 128 268 140", "sheet")
    s += circ(248, 90, 22, "t") + rect(230, 30, 36, 40, "m3")
    s += arrow(290, 60, 272, 100, None)
    s += arrow(120, 100, 200, 100, "ローラが沿って移動", 160, 90)
    s += lab(150, 176, "アウターの縁を内側へ折り返す")
    return s


@picto("powder")
def _():
    s = rect(80, 40, 36, 150, "t") + rect(204, 40, 36, 150, "t")
    s += rect(122, 20, 76, 50, "t") + rect(122, 140, 76, 50, "t")
    s += rect(122, 70, 76, 70, "sand") + dots(122, 72, 76, 66, 6, "grain")
    s += arrow(260, 20, 260, 60, None) + arrow(260, 190, 260, 150, None) + lab(270, 106, "上下から圧縮", "start")
    s += lab(160, 12, "上パンチ")
    return s


# ============================================================ heat treatment
@picto("carb")
def _():
    s = rect(10, 40, 190, 110, "m2", 4) + rect(20, 50, 170, 90, "hotin")
    for i in range(4):
        s += gear(48 + i * 40, 110, 12, 17, 10, "w", 0, 1, 0.5)
    s += heat(40, 76, 6, 24) + lab(105, 170, "浸炭（930℃前後・炭素を拡散）")
    s += tank(220, 90, 90, 70, 0.75) + lab(265, 180, "油焼入れ")
    s += arrow(196, 110, 236, 110, None)
    return s


@picto("vac")
def _():
    s = rect(40, 50, 220, 110, "m2", 50) + rect(70, 70, 160, 70, "hotin", 30)
    for i in range(4):
        s += gear(100 + i * 34, 110, 10, 14, 8, "w", 0, 1, 0.5)
    s += circ(150, 36, 16, "m") + lab(180, 30, "冷却ファン", "start")
    for x in (100, 150, 200):
        s += arrow(x, 76, x, 92, None)
    s += lab(150, 184, "減圧して浸炭 → 高圧ガスで冷却")
    return s


@picto("induction")
def _():
    cy = 90
    s = shaft(20, cy, [(280, 24)], "w", "w2")
    s += rect(130, cy - 24, 40, 48, "h")
    for x in (134, 146, 158):
        s += path("M%s %s a6 34 0 0 1 0 68" % (n(x), n(cy - 34)), "coilcu")
    s += nozzle(210, 150, -120, 16) + drops(208, 148, 4, 30, 30, -110)
    s += lab(150, 150, "コイル", "middle") + lab(240, 176, "急冷（水・ポリマー）", "middle")
    s += arrow(40, 186, 110, 186, "移動焼入れ", 75, 178)
    return s


@picto("contfurnace")
def _():
    s = rect(60, 50, 200, 90, "m2", 4) + rect(70, 60, 180, 70, "hotin")
    s += conveyor(10, 124, 300)
    for x in (30, 90, 140, 190, 240, 286):
        s += rect(x - 10, 110, 20, 14, "w", 2)
    s += heat(110, 96, 5, 22)
    s += arrow(40, 160, 280, 160, "連続搬送", 160, 180)
    return s


@picto("solution")
def _():
    s = rect(10, 50, 110, 90, "m2", 4) + rect(18, 58, 94, 74, "hotin") + rect(40, 110, 50, 16, "w")
    s += lab(65, 158, "溶体化 約500℃")
    s += tank(135, 80, 60, 60, 0.7) + lab(165, 158, "水焼入れ")
    s += rect(210, 50, 100, 90, "m2", 4) + rect(218, 58, 84, 74, "warmin") + rect(236, 110, 50, 16, "w")
    s += lab(260, 158, "時効 約200℃")
    s += arrow(118, 100, 134, 100, None) + arrow(196, 100, 210, 100, None)
    return s


@picto("pressquench")
def _():
    s = tank(40, 90, 240, 90, 0.8)
    s += rect(100, 60, 120, 30, "t") + rect(100, 124, 120, 20, "t")
    s += ell(160, 112, 58, 10, "w")
    s += arrow(160, 20, 160, 56, "金型で拘束", 206, 36)
    s += lab(160, 196, "拘束したまま焼入れ（ひずみを抑える）")
    return s


@picto("resheat")
def _():
    cy = 104
    s = shaft(30, cy, [(260, 14)], "h", "h")
    s += rect(30, cy - 26, 20, 52, "cu") + rect(270, cy - 26, 20, 52, "cu")
    s += heat(130, cy - 24, 5, 14)
    s += lab(40, 60, "＋", "middle") + lab(280, 60, "−", "middle") + lab(160, 170, "直接通電して加熱")
    return s


# ============================================================ surface / washing / coating
@picto("wash")
def _():
    s = rect(20, 30, 280, 140, "m", 6) + conveyor(30, 140, 260)
    s += box(120, 100, 80, 40, 20, "w2", "w", "w3")
    for x in (90, 160, 230):
        s += nozzle(x, 60, 90, 16) + drops(x, 60, 3, 30, 30, 90)
    s += lab(160, 190, "シャワー・高圧水・浸漬・乾燥")
    return s


@picto("plating")
def _():
    s = tank(30, 60, 260, 120, 0.8)
    s += rect(60, 70, 14, 96, "cu") + rect(246, 70, 14, 96, "cu")
    s += rect(150, 30, 20, 60, "m3") + rect(130, 90, 60, 60, "w")
    s += lab(67, 60, "＋") + lab(253, 60, "＋") + lab(160, 22, "− 製品") + lab(60, 196, "陽極", "middle")
    for x in (96, 110, 210, 224):
        s += circ(x, 120, 2, "fdot")
    return s


@picto("dip")
def _():
    s = tank(20, 90, 280, 100, 0.8)
    s += car(70, 160, 0.9, "w", "sedan", wheels=False, windows=False)
    s += path("M100 60 L160 30 L220 60", "o") + line(160, 10, 160, 30, "o")
    s += lab(160, 196, "車体ごと浸漬")
    return s


@picto("ed")
def _():
    s = PICTOS["dip"]()
    s += rect(24, 110, 10, 70, "cu") + rect(286, 110, 10, 70, "cu") + lab(29, 104, "＋") + lab(291, 104, "＋")
    s += lab(160, 70, "−（車体）")
    return s


@picto("impreg")
def _():
    s = rect(60, 40, 200, 140, "m2", 20) + rect(76, 90, 168, 80, "fl")
    s += box(120, 110, 80, 40, 20, "w2", "w", "w3")
    s += arrow(160, 30, 160, 6, None) + lab(170, 20, "真空", "start")
    s += lab(160, 196, "減圧→加圧で鋳巣に樹脂を浸透")
    return s


@picto("tspray")
def _():
    s = rect(40, 40, 240, 130, "w") + rect(110, 40, 100, 130, "bg")
    s += rect(152, 10, 16, 110, "m3") + nozzle(152, 110, 180, 10, 8)
    s += spray_cone(150, 110, 180, 40, 36, "hl")
    s += rot(160, 30, 20, 6, 200, 340, "回転", 110, 24)
    s += lab(160, 196, "ボア内面に金属を溶射")
    return s


@picto("clad")
def _():
    s = rect(30, 130, 260, 40, "w")
    s += path("M40 130 Q60 118 80 130 Q100 118 120 130 Q140 118 160 130", "bead")
    s += path("M160 40 L200 40 L190 110 L170 110Z", "m3") + line(180, 110, 180, 126, "beam")
    s += dots(170, 112, 20, 14, 5, "grain")
    s += arrow(240, 100, 190, 100, None) + lab(250, 96, "金属粉", "start")
    s += arrow(140, 186, 60, 186, "移動", 100, 180)
    return s


@picto("vapor")
def _():
    s = path("M60 180 L60 80 Q60 30 160 30 Q260 30 260 80 L260 180Z", "m")
    s += rect(40, 176, 240, 12, "m2")
    s += rect(140, 150, 40, 14, "cu")
    for k in range(5):
        a = math.radians(-150 + k * 30)
        s += arrow(160 + 20 * math.cos(a), 150 + 20 * math.sin(a), 160 + 60 * math.cos(a), 150 + 60 * math.sin(a), None)
    for x in (90, 130, 190, 230):
        s += path("M%s 70 q10 -12 20 0" % n(x - 10), "w")
    s += lab(160, 196, "真空中でアルミを蒸発させて付着")
    return s


@picto("hardcoat")
def _():
    s = path("M60 130 Q160 70 260 130", "lens") + nozzle(160, 60, 90, 16) + path("M160 60 L160 100", "jet2")
    s += rect(230, 30, 60, 16, "m2") + lab(260, 60, "UV照射")
    for x in (240, 256, 272):
        s += line(x, 46, x - 10, 90, "uv")
    s += lab(120, 176, "フローコート")
    return s


@picto("webcoat")
def _():
    s = circ(40, 110, 26, "w2") + circ(40, 110, 8, "m2")
    s += path("M40 84 L120 84 L140 110 L300 110", "strip")
    s += circ(130, 130, 18, "t") + tank(100, 140, 60, 30, 0.8)
    s += rect(180, 70, 110, 60, "m2", 4) + rect(186, 76, 98, 48, "warmin")
    s += lab(130, 190, "塗工") + lab(235, 146, "乾燥")
    return s


@picto("dipspin")
def _():
    s = tank(90, 100, 140, 80, 0.8) + rect(120, 60, 80, 70, "basket")
    for i in range(3):
        for j in range(2):
            s += rect(130 + i * 22, 74 + j * 24, 12, 16, "w", 2)
    s += rect(154, 20, 12, 40, "m3") + rot(160, 44, 30, 8, 200, 340, "遠心で振り切り", 230, 30)
    s += arrow(40, 80, 40, 130, "浸漬", 36, 150, "end")
    return s


@picto("flame")
def _():
    s = path("M40 150 Q160 110 280 150 L280 170 Q160 130 40 170Z", "w")
    s += rect(140, 30, 40, 30, "m3")
    for x in (150, 160, 170):
        s += flame(x, 104, 1.6)
    s += lab(160, 190, "表面を活性化して塗料の密着を上げる")
    return s


@picto("screen")
def _():
    s = rect(40, 130, 240, 20, "w") + rect(30, 110, 260, 10, "mesh")
    s += poly([(150, 60), (170, 60), (180, 108), (160, 108)], "t") + rect(146, 40, 28, 20, "m3")
    s += path("M100 108 Q120 100 140 108", "paste")
    s += arrow(200, 90, 270, 90, "スキージ", 235, 82)
    s += lab(160, 176, "版を通してペーストを印刷")
    return s


# ============================================================ welding & joining
@picto("spot")
def _():
    s = rect(40, 96, 240, 10, "w") + rect(40, 106, 240, 10, "w2")
    s += rect(150, 20, 20, 60, "cu") + poly([(150, 80), (170, 80), (164, 96), (156, 96)], "cu")
    s += rect(150, 140, 20, 50, "cu") + poly([(150, 140), (170, 140), (164, 116), (156, 116)], "cu")
    s += ell(160, 106, 14, 6, "h")
    s += arrow(200, 30, 200, 80, "加圧", 208, 56, "start") + lab(96, 60, "電極チップ", "middle")
    s += lab(210, 134, "ナゲット（溶融部）", "start")
    s += lightning(118, 110, 1)
    return s


@picto("arc")
def _():
    s = poly([(20, 150), (160, 150), (160, 170), (20, 170)], "w") + poly([(160, 150), (300, 150), (300, 170), (160, 170)], "w2")
    s += path("M40 150 Q50 140 60 150 Q70 140 80 150 Q90 140 100 150 Q110 140 120 150 Q130 140 140 150", "bead")
    s += "<g transform=\"rotate(30 170 90)\">" + rect(160, 30, 20, 70, "m3") + rect(165, 100, 10, 10, "cu") + "</g>"
    s += sparks(160, 146, 12, 7, -170, -10) + line(166, 118, 160, 146, "beam")
    s += arrow(240, 120, 190, 120, None) + lab(250, 116, "溶接ワイヤ・アーク", "start")
    s += arrow(140, 190, 60, 190, "溶接方向", 100, 184)
    return s


@picto("laserweld")
def _():
    s = rect(30, 130, 130, 26, "w") + rect(160, 130, 130, 26, "w2")
    s += path("M130 20 L190 20 L178 70 L142 70Z", "m3") + line(160, 70, 160, 138, "beam")
    s += path("M154 130 L160 150 L166 130", "h")
    s += lab(210, 90, "キーホール溶接", "start") + lab(160, 180, "低ひずみ・高速")
    return s


@picto("ebw")
def _():
    s = rect(20, 30, 280, 150, "m", 8) + lab(40, 50, "真空室", "start")
    s += rect(140, 40, 40, 40, "m3") + line(160, 80, 160, 124, "ebeam")
    s += shaftpart(80, 136, 160, 16)
    s += rot(160, 136, 10, 20, -60, 60)
    s += lab(210, 70, "電子ビーム", "start")
    return s


@picto("friction")
def _():
    cy = 104
    s = shaft(20, cy, [(120, 26)], "w", "w2") + shaft(146, cy, [(140, 22)], "w2", "w3")
    s += path("M140 76 q-6 28 0 56 q10 -28 0 -56", "h") + heat(136, 72, 2, 8)
    s += rot(70, cy, 10, 36, -60, 60, "回転", 70, 168)
    s += arrow(300, 60, 250, 60, "押し付け", 276, 52)
    s += lab(140, 190, "摩擦熱で接合（バリが出る）")
    return s


@picto("fsw")
def _():
    s = poly([(20, 130), (160, 130), (160, 160), (20, 160)], "w") + poly([(160, 130), (300, 130), (300, 160), (160, 160)], "w2")
    s += path("M40 130 Q60 126 80 130 Q100 126 120 130 Q140 126 150 130", "bead")
    s += vcyl(160, 60, 64, 20, 6, "t", "t") + rect(156, 124, 8, 18, "t")
    s += rot(160, 70, 30, 9, 200, 340, "回転ツール", 220, 60)
    s += arrow(120, 186, 40, 186, "移動（溶かさず攪拌）", 80, 180)
    return s


@picto("ultrasonic")
def _():
    s = rect(60, 140, 200, 30, "m2") + lab(160, 188, "アンビル")
    for i in range(6):
        s += line(90, 132 - i * 3, 230, 132 - i * 3, "foil")
    s += rect(120, 60, 80, 54, "t") + rect(140, 20, 40, 40, "m3")
    s += arrow(90, 88, 116, 88, None) + arrow(230, 88, 204, 88, None) + lab(160, 50, "ホーン（超音波振動）")
    s += lab(250, 124, "箔・電線", "start")
    return s


@picto("projection")
def _():
    s = rect(60, 118, 200, 12, "w")
    s += box(130, 92, 60, 26, 14, "w2", "w", "w3")
    s += rect(120, 20, 80, 50, "cu") + rect(120, 150, 80, 40, "cu")
    s += arrow(230, 30, 230, 80, "加圧・通電", 238, 56, "start")
    s += lab(80, 100, "突起部に電流を集中", "middle")
    return s


@picto("spr")
def _():
    s = rect(40, 100, 240, 14, "w") + rect(40, 114, 240, 14, "w2")
    s += rect(140, 20, 40, 50, "m3") + path("M150 70 L170 70 L170 104 L150 104Z", "t")
    s += path("M130 128 L190 128 L180 150 L140 150Z", "m2")
    s += arrow(220, 30, 220, 90, "リベット打込み", 228, 60, "start")
    s += lab(160, 176, "片側から貫通させずに締結")
    return s


@picto("sealer")
def _():
    s = poly([(20, 150), (300, 120), (300, 136), (20, 166)], "w") + poly([(20, 166), (300, 136), (300, 150), (20, 180)], "w3")
    s += path("M40 148 L180 133", "bead2")
    s += nozzle(186, 124, 60, 40, 12)
    s += arrow(230, 80, 280, 74, "ロボットで軌跡を描く", 250, 64)
    return s


@picto("plweld")
def _():
    s = path("M60 40 L260 40 L260 80 L60 80Z", "w") + path("M60 130 L260 130 L260 170 L60 170Z", "w2")
    s += rect(40, 96, 240, 16, "hplate") + heat(140, 94, 3, 14)
    s += arrow(290, 40, 290, 70, None) + arrow(290, 170, 290, 140, None)
    s += lab(150, 128, "熱板で溶かして押し付け") if False else lab(160, 196, "熱板・赤外線・レーザで樹脂を溶かして接合")
    return s


@picto("fracture")
def _():
    s = circ(160, 110, 62, "w") + circ(160, 110, 40, "bg")
    s += path("M96 110 L224 110", "crack")
    s += poly([(140, 110), (180, 110), (160, 150)], "t")
    s += arrow(80, 60, 80, 20, None) + arrow(240, 160, 240, 196, None)
    s += lab(160, 30, "くさびで大端部を破断分割")
    return s


@picto("framing")
def _():
    s = rect(10, 170, 300, 10, "m2")
    s += path(car_d(62, 160, 1.0, "sedan"), "w")
    for x in (60, 140, 220):
        s += rect(x, 40, 12, 130, "m3")
    s += rect(40, 30, 240, 12, "m3")
    for x, y in ((72, 110), (152, 60), (232, 110), (152, 150)):
        s += rect(x, y, 14, 10, "t")
    s += lab(160, 20, "総組治具で拘束して溶接")
    return s


# ============================================================ molding (resin / rubber / glass)
@picto("injection")
def _():
    s = rect(150, 40, 20, 120, "m2") + rect(170, 40, 20, 120, "m3") + path("M168 70 L178 70 L178 130 L168 130Z", "resin")
    s += rect(40, 90, 110, 22, "m") + path("M50 101 L140 101", "screw")
    for x in range(52, 140, 10):
        s += line(x, 92, x + 6, 110, "o thin")
    s += poly([(56, 60), (86, 60), (78, 90), (64, 90)], "m2") + lab(71, 52, "ホッパ")
    s += arrow(40, 140, 120, 140, "射出", 80, 156)
    s += arrow(290, 100, 200, 100, "型締め", 250, 92)
    s += lab(170, 180, "金型")
    return s


@picto("blow")
def _():
    s = rect(130, 10, 60, 30, "m2") + lab(210, 28, "押出ヘッド", "start")
    s += path("M140 40 L140 150 Q160 176 180 150 L180 40", "parison")
    s += rect(40, 60, 70, 110, "m3") + rect(210, 60, 70, 110, "m3")
    s += arrow(20, 115, 40, 115, None) + arrow(300, 115, 280, 115, None)
    s += arrow(160, 190, 160, 150, "空気で膨らませる", 230, 190)
    return s


@picto("extrude")
def _():
    s = rect(20, 80, 170, 30, "m") + path("M28 95 L180 95", "screw")
    for x in range(30, 180, 12):
        s += line(x, 82, x + 7, 108, "o thin")
    s += poly([(40, 50), (72, 50), (64, 80), (48, 80)], "m2")
    s += rect(190, 70, 24, 50, "m3") + lab(202, 136, "ダイ")
    s += path("M214 88 L300 88 L300 104 L214 104Z", "rbx")
    s += arrow(230, 60, 290, 60, "断面形状が連続して出る", 250, 50)
    return s


@picto("cvulc")
def _():
    s = rect(60, 60, 200, 80, "m2", 4) + rect(68, 68, 184, 64, "warmin")
    s += path("M10 104 L310 104", "rbstrip")
    for x in (100, 140, 180, 220):
        s += path("M%s 76 q6 6 0 12 q-6 6 0 12" % n(x), "uvwave")
    s += lab(160, 160, "マイクロ波・熱風で連続加硫")
    return s


@picto("mixer")
def _():
    s = rect(90, 60, 140, 110, "m2", 10) + rect(146, 20, 28, 50, "m3") + lab(186, 32, "ラム", "start")
    s += circ(130, 120, 32, "rbx") + circ(190, 120, 32, "rbx")
    for cx, d in ((130, 1), (190, -1)):
        s += path("M%s 96 Q%s 120 %s 144" % (n(cx - 10), n(cx + 20 * d), n(cx + 10)), "o")
        s += rot(cx, 120, 40, 40, 200 if d > 0 else -20, 280 if d > 0 else -100)
    s += lab(160, 190, "2本のロータで練る")
    return s


@picto("calender")
def _():
    s = ""
    for i, (x, y) in enumerate(((110, 50), (110, 110), (190, 80), (190, 140))):
        s += circ(x, y, 26, "m2") + circ(x, y, 6, "m3")
    s += path("M20 80 L84 80", "rbstrip") + path("M216 140 L310 140", "rbstrip")
    for x in range(230, 300, 10):
        s += line(x, 136, x, 144, "cordl")
    s += lab(160, 190, "コードにゴムを被覆してシート化")
    return s


@picto("tirebuild")
def _():
    s = shaft(40, 104, [(200, 60)], "m", "m2")
    for i, c in enumerate(("rbx", "rb2", "rbx")):
        s += path("M%s 44 L%s 164" % (n(80 + i * 40), n(80 + i * 40)), "o")
    s += path("M60 44 L240 44", "rbstrip") + path("M60 164 L240 164", "rbstrip")
    s += rot(140, 104, 12, 64, -60, 60, "ドラム回転", 140, 196)
    s += lab(290, 104, "部材を順に貼る", "end")
    return s


@picto("beadform")
def _():
    s = circ(160, 104, 70, "o") + circ(160, 104, 64, "beadw") + circ(160, 104, 58, "o")
    s += circ(40, 40, 16, "m2") + path("M56 40 Q120 30 150 36", "wire2")
    s += rot(160, 104, 84, 84, -40, 20)
    s += lab(160, 196, "鋼線を巻いてリング状に")
    return s


@picto("tirecure")
def _():
    s = rect(60, 20, 200, 60, "m3", 6) + rect(60, 130, 200, 60, "m3", 6)
    s += ell(160, 105, 110, 36, "rbx") + ell(160, 105, 60, 18, "t")
    s += heat(110, 26, 5, 24) + lab(160, 110, "ブラダ", "middle")
    s += arrow(290, 30, 290, 70, None) + lab(282, 24, "約170℃", "end")
    return s


@picto("foam")
def _():
    s = rect(130, 20, 60, 40, "m3") + lab(210, 36, "ミキシングヘッド", "start")
    s += path("M160 60 L160 100", "pourf")
    s += path("M40 110 L280 110 L280 170 L40 170Z", "m2") + path("M56 120 L264 120 L264 160 L56 160Z", "foamf")
    s += bubbles(100, 150, 5, 50, 28) + bubbles(220, 150, 5, 50, 28)
    s += lab(160, 190, "2液を混合して注入・発泡")
    return s


@picto("slush")
def _():
    s = "<g transform=\"rotate(-18 160 100)\">" + path("M60 60 L260 60 L260 140 L60 140Z", "m2") + path("M76 76 L244 76 L244 124 L76 124Z", "hotin")
    s += path("M78 122 Q160 110 242 122", "skin") + "</g>"
    s += dots(90, 110, 140, 40, 7, "grain")
    s += rot(160, 100, 130, 60, 150, 210, "型を反転", 40, 30)
    s += lab(160, 190, "加熱した型にパウダーを流して溶かす")
    return s


@picto("tmold")
def _():
    s = rect(70, 50, 180, 36, "m3") + rect(70, 110, 180, 36, "m2")
    s += rect(100, 90, 120, 16, "resin")
    for x in (120, 160, 200):
        s += rect(x - 8, 92, 16, 6, "chipd")
    s += rect(150, 10, 20, 40, "t") + arrow(190, 12, 190, 46, "プランジャ", 198, 30, "start")
    s += lab(160, 176, "樹脂を加熱して金型に押し込み封止")
    return s


@picto("hotpress")
def _():
    s = rect(60, 30, 200, 30, "m3") + heat(100, 76, 5, 30) + rect(60, 140, 200, 30, "m3")
    s += rect(100, 110, 120, 12, "m2") + rect(110, 90, 100, 20, "padm")
    s += arrow(280, 30, 280, 80, "加熱・加圧", 272, 100, "end")
    return s


@picto("cutter")
def _():
    s = poly([(30, 140), (290, 140), (300, 156), (40, 156)], "w")
    s += nozzle(160, 40, 90, 40, 12) + line(160, 40, 160, 138, "jet")
    s += path("M60 148 L160 148", "kerf")
    s += arrow(180, 180, 260, 180, "移動", 220, 196)
    s += lab(210, 70, "ウォータジェット／超音波刃", "start")
    return s


@picto("glasscut")
def _():
    s = poly([(20, 130), (300, 130), (300, 146), (20, 146)], "glp")
    s += circ(140, 110, 16, "m") + rect(132, 60, 16, 44, "m3")
    s += path("M40 130 L140 130", "kerf")
    s += circ(250, 100, 30, "gw") + lab(250, 150, "エッジ研削")
    s += lab(140, 50, "切筋を入れる") + arrow(90, 176, 30, 176, None)
    return s


@picto("glassbend")
def _():
    s = rect(20, 30, 280, 150, "m2", 6) + rect(30, 40, 260, 130, "hotin")
    s += path("M70 90 Q160 130 250 90", "glsheet")
    s += rect(70, 120, 180, 10, "m3")
    s += heat(100, 70, 5, 30)
    s += lab(160, 196, "600℃超で自重・プレスで曲げる")
    return s


@picto("autoclave")
def _():
    s = rect(30, 50, 250, 110, "m2", 55) + ell(280, 105, 22, 55, "m3")
    for x in range(80, 250, 22):
        s += path("M%s 70 Q%s 105 %s 140" % (n(x), n(x + 10), n(x)), "glsheet")
    s += lab(150, 184, "加熱・加圧で中間膜を接着") + lab(150, 40, "オートクレーブ")
    return s


# ============================================================ paint
@picto("paintrobot")
def _():
    s = car(120, 170, 0.95, "w", "sedan", wheels=False)
    r, (tx, ty) = robot(46, 190, 1.0, -84, 60)
    s += r + path("M%s %s l12 -5 l0 14 z" % (n(tx), n(ty - 4)), "t")
    s += spray_cone(tx + 12, ty + 2, 20, 40, 50) + drops(tx + 14, ty + 2, 5, 34, 44, 20)
    s += lab(250, 30, "回転霧化ベル＋静電")
    return s


@picto("booth")
def _():
    s = PICTOS["paintrobot"]()
    for x in (40, 120, 200, 280):
        s += arrow(x, 6, x, 30, None)
    s += lab(160, 196, "温湿度とゴミを管理したブース")
    return s


@picto("oven")
def _():
    s = rect(10, 40, 300, 120, "m2", 6) + rect(20, 50, 280, 100, "warmin")
    s += car(60, 150, 0.9, "w", "sedan", wheels=False, windows=False)
    s += heat(110, 70, 5, 24) + lab(160, 184, "焼付乾燥（140〜180℃）")
    return s


@picto("powdercoat")
def _():
    s = vcoil(230, 104, 150, 34, 5)
    s += rect(20, 90, 60, 20, "m3") + poly([(80, 94), (100, 90), (100, 110), (80, 106)], "m2")
    s += spray_cone(100, 100, 0, 30, 60) + dots(110, 90, 50, 22, 6, "pwd")
    s += lab(50, 80, "静電ガン", "middle") + lab(120, 150, "粉体塗料", "middle")
    return s


@picto("polish")
def _():
    s = path("M20 140 Q160 110 300 140 L300 170 L20 170Z", "w")
    s += ell(160, 118, 40, 8, "t") + rect(150, 60, 20, 56, "m3")
    s += rot(160, 118, 50, 12, 20, 160, "研磨", 230, 100)
    return s


# ============================================================ assembly
@picto("assy")
def _():
    s = rect(40, 160, 240, 14, "m2") + box(90, 120, 140, 40, 26, "w2", "w", "w3")
    s += ell(176, 107, 22, 8, "bg")
    s += rect(150, 20, 40, 30, "m3") + rect(160, 50, 20, 20, "m2") + rect(154, 70, 6, 16, "m3") + rect(180, 70, 6, 16, "m3")
    s += vcyl(170, 80, 14, 12, 4, "t", "t")
    s += arrow(230, 60, 230, 100, "組み付け", 238, 84, "start")
    s += lab(160, 196, "位置決めして部品を組み込む")
    return s


@picto("conveyor")
def _():
    s = rect(0, 176, 320, 10, "m2")
    s += car(60, 176, 1.0, "w", "sedan")
    s += path("M40 12 L280 12", "rail") + line(100, 12, 100, 40, "o") + line(200, 12, 200, 40, "o")
    s += arrow(40, 196, 120, 196, "タクト送り", 80, 192)
    return s


@picto("agv")
def _():
    s = rect(80, 120, 160, 40, "m2", 6) + circ(110, 164, 10, "m3") + circ(210, 164, 10, "m3")
    s += box(110, 80, 100, 40, 20, "w2", "w", "w3")
    s += path("M20 180 L300 180", "rail") + arrow(250, 140, 300, 140, None)
    s += lab(160, 110, "ユニット", "middle")
    return s


@picto("robot")
def _():
    r, (tx, ty) = robot(90, 186, 1.2, -70, 80)
    s = r + rect(tx - 8, ty, 16, 10, "m3") + box(tx - 20, ty + 10, 40, 24, 10, "w2", "w", "w3")
    s += arrow(tx + 30, ty + 20, tx + 80, ty + 20, "搬送・搭載", tx + 60, ty + 12)
    s += rect(220, 150, 80, 30, "m2")
    return s


@picto("nutrunner")
def _():
    s = rect(140, 10, 40, 80, "m3", 6) + rect(152, 90, 16, 30, "m2")
    s += poly([(146, 120), (174, 120), (170, 132), (150, 132)], "t")
    s += rect(60, 150, 200, 20, "w") + line(160, 132, 160, 170, "o")
    s += rot(160, 110, 30, 10, 200, 340)
    s += chart(210, 30, 100, 70, "ramp") + lab(260, 116, "トルク・角度を記録")
    return s


@picto("pressfit")
def _():
    s = rect(140, 10, 40, 50, "m3") + rect(146, 60, 28, 30, "t")
    s += ell(160, 96, 30, 8, "w2") + rect(130, 96, 60, 14, "w2")
    s += rect(70, 120, 180, 60, "w") + rect(130, 120, 60, 40, "bg")
    s += arrow(110, 20, 110, 90, "押し込み", 100, 56, "end")
    s += chart(210, 20, 100, 70, "rise") + lab(260, 106, "荷重－変位を監視")
    return s


@picto("caulk")
def _():
    s = rect(80, 110, 160, 70, "w") + rect(130, 90, 60, 30, "w2")
    s += path("M120 110 L128 90", "sheet") + path("M200 110 L192 90", "sheet")
    s += rect(100, 30, 120, 40, "t") + arrow(260, 30, 260, 80, "塑性変形で固定", 252, 100, "end")
    return s


@picto("fill")
def _():
    s = box(100, 110, 140, 60, 30, "w2", "w", "w3") + rect(150, 84, 20, 18, "m2")
    s += rect(146, 20, 28, 64, "m3") + path("M160 84 L160 104", "jet2")
    s += arrow(200, 40, 250, 40, "真空引き", 225, 32) + arrow(100, 40, 146, 40, None) + lab(60, 44, "液", "middle")
    s += lab(160, 196, "真空引き→定量充填")
    return s


@picto("harnessboard")
def _():
    s = rect(20, 30, 280, 150, "board", 4)
    for x, y in ((60, 80), (120, 110), (180, 90), (240, 120), (100, 150), (220, 60)):
        s += path("M%s %s l0 -10 M%s %s l6 -8 M%s %s l-6 -8" % (n(x), n(y), n(x), n(y), n(x), n(y)), "o")
    s += path("M40 110 C100 110 140 90 180 90 S240 120 290 120", "cable3") + path("M120 110 L100 150 M180 90 L220 60", "cable")
    s += lab(160, 196, "実物大の図板で配索・テーピング")
    return s


@picto("sew")
def _():
    s = rect(30, 140, 260, 20, "m2") + poly([(40, 130), (280, 130), (280, 140), (40, 140)], "w")
    s += path("M60 30 L220 30 L220 70 L200 70 L200 60 L80 60 L80 130 L60 130Z", "m")
    s += line(170, 60, 170, 134, "needle")
    s += path("M40 135 L160 135", "stitch")
    return s


@picto("cutting")
def _():
    for i in range(6):
        s = "" if i == 0 else s
    s = ""
    for i in range(6):
        s += poly([(40, 150 - i * 5), (280, 150 - i * 5), (284, 154 - i * 5), (44, 154 - i * 5)], "w" if i % 2 else "w2")
    s += rect(150, 30, 20, 60, "m3") + poly([(156, 90), (164, 90), (160, 124)], "t")
    s += arrow(200, 176, 280, 176, "CADデータどおりに裁断", 240, 192)
    return s


@picto("loom")
def _():
    s = ""
    for i in range(14):
        y = 50 + i * 8
        s += line(30, y, 290, y, "thread")
    s += rect(150, 40, 16, 130, "m3")
    s += path("M30 50 L30 154", "thread2") + arrow(60, 186, 260, 186, "よこ糸を打ち込む", 160, 180)
    return s


@picto("crimp")
def _():
    s = path("M10 110 L150 110", "cable3") + rect(150, 102, 40, 16, "cu") + rect(190, 104, 60, 12, "cu")
    s += rect(140, 30, 60, 50, "m3") + poly([(150, 80), (190, 80), (184, 98), (156, 98)], "t")
    s += rect(140, 128, 60, 30, "m2")
    s += arrow(230, 40, 230, 90, "圧着", 238, 66, "start")
    s += lab(80, 96, "電線", "middle") + lab(220, 140, "端子", "middle")
    return s


@picto("crane")
def _():
    s = rect(10, 20, 300, 14, "m3") + rect(140, 34, 40, 20, "m2") + line(160, 54, 160, 90, "o")
    s += path("M150 90 L170 90 L170 104 L150 104Z", "m3")
    s += circ(160, 140, 40, "w2") + circ(160, 140, 14, "m2")
    s += lab(160, 196, "鋼板コイル（5〜20t）")
    return s


# ============================================================ battery / electronics / motor
@picto("slurrymix")
def _():
    s = path("M80 60 L240 60 L230 180 L90 180Z", "m2") + rect(96, 90, 128, 84, "slurry")
    s += rect(130, 20, 20, 120, "m3") + rect(170, 20, 20, 120, "m3")
    s += path("M120 140 Q140 120 160 140 Q180 160 200 140", "o")
    s += rot(160, 150, 50, 12, 20, 160, "自転・公転", 160, 198)
    return s


@picto("coater")
def _():
    s = circ(30, 110, 20, "m2") + path("M30 90 L100 90 L110 110 L310 110", "foilstrip")
    s += rect(100, 70, 30, 30, "t") + lab(115, 64, "ダイ")
    s += path("M126 108 L310 108", "slurryl")
    s += rect(160, 70, 150, 60, "m2", 4) + rect(166, 76, 138, 48, "warmin")
    s += lab(235, 150, "乾燥炉（溶剤回収）") + lab(40, 150, "金属箔")
    return s


@picto("rollpress")
def _():
    s = circ(160, 56, 44, "m2") + circ(160, 152, 44, "m2")
    s += path("M10 102 L160 102", "slurryl2") + path("M160 104 L310 104", "slurryl")
    s += rot(160, 56, 54, 54, 40, 140) + rot(160, 152, 54, 54, 220, 320)
    s += lab(60, 90, "圧延前", "middle") + lab(260, 90, "高密度化", "middle")
    return s


@picto("slitter")
def _():
    s = poly([(20, 120), (220, 120), (240, 90), (40, 90)], "slurryp")
    for x in (80, 130, 180):
        s += circ(x + 20, 104, 22, "t")
    s += poly([(220, 120), (300, 120), (310, 110), (230, 110)], "slurryp") + poly([(220, 100), (300, 100), (316, 88), (236, 88)], "slurryp")
    s += lab(120, 150, "丸刃で製品幅に切断") + lab(270, 140, "バリ管理")
    return s


@picto("winder")
def _():
    s = ell(200, 104, 34, 56, "m2")
    for r in range(6):
        s += ell(200, 104, 38 + r * 6, 60 + r * 5, "windl" + str(r % 3))
    s += path("M10 60 L200 48", "windl0") + path("M10 80 L200 52", "windl1") + path("M10 100 L200 56", "windl2")
    s += lab(60, 130, "正極・セパレータ・負極", "middle")
    s += rot(200, 104, 80, 96, -60, 0, "巻回", 300, 60)
    return s


@picto("efill")
def _():
    s = box(110, 90, 100, 90, 30, "w2", "w", "w3") + rect(155, 60, 14, 30, "m3")
    s += path("M162 90 L162 130", "jet2") + rect(116, 130, 88, 46, "fl")
    s += arrow(230, 60, 290, 60, "真空・加圧", 260, 52)
    s += lab(160, 196, "ドライルーム内で電解液を注入")
    return s


@picto("dryroom")
def _():
    s = rect(30, 40, 260, 140, "m", 6) + path("M30 40 L160 10 L290 40", "o")
    s += rect(60, 110, 80, 60, "m2") + rect(180, 80, 80, 40, "m3") + lab(220, 104, "除湿機", "middle")
    s += lab(160, 196, "露点 −40℃以下")
    return s


@picto("formation")
def _():
    s = rect(20, 30, 180, 150, "m", 4)
    for r in range(3):
        for c in range(4):
            s += rect(34 + c * 42, 44 + r * 44, 30, 36, "w", 2)
    s += rect(220, 60, 80, 100, "m3", 4) + lab(260, 176, "充放電器")
    for r in range(3):
        s += path("M200 %s L220 %s" % (n(62 + r * 44), n(80 + r * 20)), "cable")
    return s


@picto("hairpin")
def _():
    s = ell(180, 140, 110, 34, "w2") + ell(180, 140, 70, 20, "bg")
    for k in range(24):
        a = 2 * math.pi * k / 24
        s += line(180 + 72 * math.cos(a), 140 + 21 * math.sin(a), 180 + 108 * math.cos(a), 140 + 33 * math.sin(a), "o thin")
    s += path("M60 30 L60 90 Q60 100 70 100 L90 100 Q100 100 100 90 L100 30", "cuwire2")
    s += arrow(80, 110, 120, 130, "スロットへ挿入", 60, 150)
    return s


@picto("winding")
def _():
    s = rect(120, 60, 80, 100, "w2") + rect(140, 60, 40, 100, "m")
    for y in range(66, 156, 8):
        s += line(136, y, 184, y + 4, "cuwire")
    s += nozzle(220, 90, 180, 30, 8) + path("M220 90 L184 96", "cuwire")
    s += rot(160, 110, 70, 60, -40, 40, "ノズルが周回", 250, 40)
    return s


@picto("magnetize")
def _():
    s = circ(160, 104, 86, "m2") + circ(160, 104, 56, "bg")
    s += shaft(110, 104, [(100, 44)], "w", "w2")
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += rect(160 + 70 * math.cos(a) - 6, 104 + 70 * math.sin(a) - 6, 12, 12, "cu")
    s += lightning(270, 30, 1.2) + lab(280, 80, "パルス磁界", "middle")
    return s


@picto("mounter")
def _():
    s = rect(30, 150, 260, 12, "pcb") + rect(20, 20, 280, 20, "m3") + rect(130, 40, 60, 30, "m2")
    for i in range(4):
        s += rect(138 + i * 12, 70, 6, 40 + (i % 2) * 20, "m3")
    s += rect(150, 136, 14, 10, "chipd") + rect(60, 142, 16, 8, "chipd") + rect(230, 140, 20, 10, "chipd")
    s += arrow(290, 60, 220, 60, "高速で位置決め", 250, 54)
    return s


@picto("reflow")
def _():
    s = rect(20, 50, 280, 90, "m2", 6)
    zones = ["warmin", "warmin", "hotin", "hotin", "coolin"]
    for i, z in enumerate(zones):
        s += rect(28 + i * 54, 58, 50, 74, z)
    s += conveyor(10, 120, 300) + rect(130, 110, 60, 8, "pcb")
    s += chart(40, 146, 240, 46, "peak")
    return s


@picto("selsolder")
def _():
    s = rect(30, 70, 260, 12, "pcb") + rect(150, 40, 20, 30, "m2")
    s += path("M140 110 Q160 84 180 110", "h") + rect(136, 110, 48, 50, "m3")
    s += lab(160, 186, "はんだ噴流で局所的に接合")
    return s


@picto("dispense")
def _():
    s = rect(140, 10, 40, 60, "m3") + rect(156, 70, 8, 40, "m2")
    s += path("M160 110 L160 128", "jet2") + rect(40, 140, 240, 30, "pcb")
    s += path("M60 134 Q100 128 140 134 Q170 138 160 134", "bead3")
    s += arrow(240, 100, 180, 100, "計量吐出", 250, 96, "start")
    return s


@picto("dicing")
def _():
    s = ell(160, 130, 120, 34, "wafer")
    for x in range(60, 260, 24):
        s += line(x, 106, x + 10, 154, "o thin")
    s += circ(160, 70, 40, "t") + circ(160, 70, 12, "m2")
    s += rot(160, 70, 50, 50, 200, 250, "ブレード", 90, 30)
    return s


@picto("diebond")
def _():
    s = rect(40, 150, 240, 20, "cu") + rect(60, 136, 200, 14, "m")
    s += rect(140, 20, 40, 60, "m3") + rect(146, 80, 28, 30, "m2") + rect(144, 110, 32, 10, "chipd")
    s += arrow(200, 90, 200, 126, "接合（はんだ／焼結）", 208, 110, "start")
    return s


@picto("wirebond")
def _():
    s = rect(40, 150, 240, 16, "m") + rect(80, 128, 80, 22, "chipd")
    for i in range(3):
        s += path("M%s 128 Q%s 70 %s 150" % (n(96 + i * 20), n(150 + i * 20), n(200 + i * 20)), "wirebond")
    s += poly([(236, 40), (252, 40), (246, 90), (242, 90)], "m3")
    s += lab(250, 110, "キャピラリ", "middle")
    return s


@picto("align")
def _():
    s = rect(120, 140, 80, 20, "pcb") + rect(140, 130, 40, 10, "chipd")
    s += rect(130, 70, 60, 40, "m2") + circ(160, 90, 14, "gl2")
    s += arrow(110, 90, 80, 90, None, both=True) + arrow(160, 60, 160, 30, None, both=True)
    s += rot(160, 90, 50, 16, 200, 340)
    s += lab(250, 90, "撮像しながら6軸で調芯", "middle")
    return s


# ============================================================ inspection
@picto("cmm")
def _():
    s = rect(20, 170, 280, 14, "m2") + rect(40, 40, 16, 130, "m") + rect(264, 40, 16, 130, "m") + rect(30, 30, 260, 16, "m3")
    s += rect(150, 46, 20, 70, "m2") + line(160, 116, 160, 134, "o") + circ(160, 136, 3.5, "t")
    s += box(110, 138, 110, 32, 20, "w2", "w", "w3")
    s += arrow(240, 80, 240, 120, "Z", 248, 104, "start") + arrow(70, 60, 130, 60, "X・Y", 100, 54)
    return s


@picto("scan3d")
def _():
    s = rect(120, 20, 80, 24, "m3") + circ(160, 32, 8, "t")
    s += rect(50, 30, 30, 20, "m2") + rect(240, 30, 30, 20, "m2")
    for i in range(7):
        s += line(130 + i * 10, 44, 90 + i * 24, 150, "fringe")
    s += path("M80 150 Q160 110 250 150 L250 170 L80 170Z", "w")
    s += line(65, 50, 120, 140, "o thin dash") + line(255, 50, 200, 140, "o thin dash")
    s += lab(160, 190, "縞模様を投影して全面の形状を取得")
    return s


@picto("gauge")
def _():
    s = rect(60, 100, 200, 80, "w") + rect(130, 100, 60, 80, "bg")
    s += rect(140, 40, 40, 100, "m2") + circ(142, 120, 3, "fdot") + circ(178, 120, 3, "fdot")
    s += arrow(128, 120, 116, 120, None) + arrow(192, 120, 204, 120, None)
    s += rect(220, 20, 80, 50, "m", 4) + lab(260, 50, "径 ±1μm", "middle")
    s += path("M180 60 L220 44", "cable")
    return s


@picto("inprocess")
def _():
    s = PICTOS["cyl_grind"]()
    s += rect(100, 150, 40, 30, "m3") + line(112, 150, 112, 144, "o") + line(128, 150, 128, 144, "o")
    s += lab(60, 176, "定寸装置", "middle")
    return s


@picto("roundness")
def _():
    s = ell(110, 170, 80, 16, "m2") + vcyl(110, 90, 70, 50, 12, "w", "w2")
    s += rect(180, 40, 16, 130, "m") + rect(160, 110, 40, 10, "m3") + line(160, 115, 162, 115, "o")
    s += circ(250, 70, 40, "o") + path(" ".join(("M" if k == 0 else "L") + n(250 + (34 + 3 * math.sin(k * 0.6)) * math.cos(k * 0.157)) + " " + n(70 + (34 + 3 * math.sin(k * 0.6)) * math.sin(k * 0.157)) for k in range(41)), "a")
    s += rot(110, 170, 92, 20, 20, 160)
    return s


@picto("rough")
def _():
    s = rect(30, 130, 260, 40, "w")
    s += path("M30 130 " + " ".join("L%s %s" % (n(30 + i * 5), n(130 + 2.5 * math.sin(i * 1.3) + 1.5 * math.sin(i * 3.1))) for i in range(53)), "o")
    s += rect(120, 60, 60, 30, "m3") + line(170, 90, 180, 128, "o")
    s += arrow(200, 110, 280, 110, "触針でなぞる", 240, 102)
    s += chart(20, 20, 90, 60, "profile")
    return s


@picto("shaftmeas")
def _():
    cy = 110
    s = poly([(20, cy - 12), (44, cy), (20, cy + 12)], "m2") + poly([(300, cy - 12), (276, cy), (300, cy + 12)], "m2")
    s += shaft(44, cy, [(40, 16), (20, 30), (40, 16), (20, 30), (60, 16), (52, 14)], "w", "w2")
    for x in (64, 144, 230):
        s += rect(x - 4, 40, 8, 50, "m3") + rect(x - 4, 130, 8, 50, "m3")
    s += lab(160, 20, "径・真円度・位相を全数自動測定")
    return s


@picto("gearmeas")
def _():
    s = gear(120, 120, 60, 76, 16, "w", 0.2, 1, 0.5) + circ(120, 120, 20, "bg")
    s += rect(200, 40, 14, 60, "m3") + line(207, 100, 190, 60, "o") + circ(190, 60, 3, "t") if False else rect(196, 30, 14, 50, "m3") + line(203, 80, 190, 58 + 0, "o")
    s += chart(220, 110, 90, 70, "profile") + lab(265, 196, "歯形・歯すじ")
    return s


@picto("gearmesh")
def _():
    s = gear3d(110, 110, 50, 60, 20, 5, -4, 0, "w", "w3", tw=0.5) + circ(110, 110, 14, "bg")
    s += gear3d(214, 110, 36, 46, 15, 5, -4, 0, "t", "t", 0.2, tw=0.5) + circ(214, 110, 10, "m2")
    s += lab(110, 190, "製品") + lab(214, 190, "マスタギヤ")
    s += chart(210, 10, 100, 50, "noise")
    return s


@picto("camera")
def _():
    s = rect(135, 16, 50, 36, "m3", 4) + rect(148, 52, 24, 12, "m2")
    s += ell(160, 80, 50, 10, "ring")
    s += line(160, 64, 110, 150, "o thin dash") + line(160, 64, 210, 150, "o thin dash")
    s += box(100, 140, 120, 30, 20, "w2", "w", "w3")
    s += lab(250, 40, "カメラ＋照明", "middle") + lab(160, 196, "外観・有無・寸法を判定")
    return s


@picto("paintinsp")
def _():
    s = path("M20 170 Q160 120 300 170", "w")
    for i in range(6):
        x = 40 + i * 48
        s += rect(x, 20, 20, 60, "ring")
    s += rect(150, 90, 30, 20, "m3") + lab(160, 196, "縞照明の反射でブツ・ハジキを検出")
    for i in range(5):
        s += path("M%s 150 Q%s 140 %s 150" % (n(50 + i * 50), n(70 + i * 50), n(90 + i * 50)), "o thin")
    return s


@picto("bodymeas")
def _():
    s = rect(10, 176, 300, 8, "m2") + path(car_d(62, 170, 1.0, "sedan"), "w")
    r1, (a, b) = robot(30, 186, 0.9, -80, 60)
    r2, (c, d) = robot(290, 186, 0.9, -100, -60)
    s += r1 + r2 + line(a, b, 110, 110, "laserl") + line(c, d, 230, 110, "laserl")
    s += lab(160, 20, "センサで基準点を全数計測")
    return s


@picto("gapmeas")
def _():
    s = path("M20 60 L150 60 L150 180 L20 180Z", "w") + path("M160 60 L300 60 L300 180 L160 180Z", "w2")
    s += rect(130, 10, 60, 24, "m3") + line(140, 34, 155, 120, "laserl") + line(180, 34, 155, 120, "laserl")
    s += arrow(150, 190, 160, 190, None, both=True) + lab(200, 196, "隙間・段差", "start")
    return s


@picto("thick")
def _():
    s = rect(40, 140, 240, 30, "m2") + rect(40, 128, 240, 12, "w") + rect(40, 120, 240, 8, "t")
    s += rect(140, 40, 40, 70, "m3") + rect(150, 110, 20, 10, "m")
    s += arrow(290, 120, 290, 140, None, both=True) + lab(284, 110, "膜厚", "end")
    return s


@picto("color")
def _():
    s = path("M20 160 Q160 130 300 160 L300 180 L20 180Z", "w")
    for a in (-60, -30, 0, 30):
        r = math.radians(a - 90)
        s += line(160, 148, 160 + 110 * math.cos(r), 148 + 110 * math.sin(r), "o thin dash")
    s += rect(130, 20, 60, 30, "m3") + lab(160, 196, "多角度で色・光沢・肌を測る")
    return s


@picto("distort")
def _():
    s = rect(20, 30, 80, 140, "zebra")
    for y in range(36, 170, 12):
        s += rect(20, y, 80, 6, "d")
    s += path("M140 30 Q160 100 140 170", "glsheet")
    s += rect(250, 90, 50, 30, "m3") + line(250, 105, 110, 105, "o thin dash")
    s += lab(160, 196, "ガラス越しの縞の歪みを測る")
    return s


@picto("weigh")
def _():
    s = rect(80, 140, 160, 20, "m2") + rect(100, 160, 120, 20, "m3") + rect(130, 90, 60, 50, "w")
    s += rect(240, 100, 60, 34, "m", 4) + lab(270, 122, "g", "middle")
    return s


@picto("xray")
def _():
    s = rect(20, 80, 50, 50, "m3", 4) + lab(45, 146, "X線源")
    for k in range(5):
        y = 70 + k * 18
        s += line(70, 105, 270, y, "ray")
    s += box(130, 80, 70, 60, 20, "w2", "w", "w3") + circ(162, 112, 6, "bg")
    s += rect(270, 50, 20, 110, "m2") + lab(280, 176, "検出器")
    return s


@picto("ct")
def _():
    s = PICTOS["xray"]()
    s += ell(172, 150, 50, 10, "m2") + rot(172, 150, 60, 14, 20, 160, "回転して3D再構成", 172, 196)
    return s


@picto("ut")
def _():
    s = rect(30, 110, 260, 60, "w") + ell(200, 146, 16, 5, "bg")
    s += rect(120, 70, 40, 40, "m3") + rect(124, 104, 32, 6, "fl")
    for i in range(3):
        s += path("M%s %s Q140 %s %s %s" % (n(122 - i * 6), n(118 + i * 12), n(126 + i * 12), n(158 + i * 6), n(118 + i * 12)), "wave")
    s += chart(190, 20, 110, 60, "peak") + lab(245, 96, "エコー波形")
    return s


@picto("eddy")
def _():
    s = shaftpart(20, 140, 280, 24)
    s += rect(140, 40, 40, 60, "m3")
    for r in range(3):
        s += ell(160, 118 + r * 6, 30 - r * 6, 6, "wave")
    s += lab(250, 60, "渦電流の変化で割れ・焼入れ状態を判定", "middle")
    return s


@picto("mpi")
def _():
    s = rect(40, 120, 240, 40, "w") + path("M150 120 L158 138 L154 160", "crack")
    s += path("M90 120 L90 60 L230 60 L230 120", "yoke") + lab(160, 50, "磁化")
    s += dots(140, 118, 30, 10, 4, "pwd")
    s += lab(160, 186, "割れに磁粉が集まる")
    return s


@picto("pt")
def _():
    s = rect(40, 120, 240, 40, "w") + path("M150 120 L158 140", "indic")
    s += rect(120, 30, 80, 30, "m3") + line(140, 60, 150, 116, "uv") + line(180, 60, 160, 116, "uv")
    s += lab(160, 186, "蛍光浸透液をUVで観察")
    return s


@picto("leak")
def _():
    s = box(80, 90, 150, 70, 30, "w2", "w", "w3") + rect(70, 110, 14, 30, "m3") + rect(226, 110, 14, 30, "m3")
    s += path("M240 124 L280 124 L280 60", "cable") + circ(280, 46, 18, "m") + line(280, 46, 290, 38, "a")
    s += arrow(20, 124, 70, 124, "エア加圧", 44, 116)
    s += lab(160, 196, "圧力変化から漏れを測る")
    return s


@picto("he")
def _():
    s = rect(40, 40, 200, 140, "m", 10) + box(90, 100, 100, 50, 20, "w2", "w", "w3")
    s += dots(60, 60, 160, 30, 12, "he")
    s += rect(250, 90, 50, 60, "m3") + path("M240 120 L250 120", "cable") + lab(275, 170, "質量分析")
    s += lab(140, 196, "ヘリウムで微小漏れを検出")
    return s


@picto("hardness")
def _():
    s = rect(60, 130, 200, 40, "w") + rect(150, 40, 20, 60, "m3") + poly([(150, 100), (170, 100), (160, 124)], "t")
    s += poly([(152, 130), (168, 130), (160, 140)], "bg")
    s += arrow(200, 50, 200, 110, "圧子を押込み", 208, 80, "start")
    return s


@picto("micro")
def _():
    s = rect(120, 160, 120, 16, "m2") + rect(200, 40, 16, 120, "m3") + rect(150, 30, 60, 30, "m2") + rect(166, 60, 16, 50, "m3")
    s += rect(150, 130, 50, 14, "w")
    s += circ(70, 80, 46, "m") + path("M40 70 Q60 60 80 76 Q96 88 110 70", "o") + dots(34, 50, 70, 60, 10, "grain")
    s += lab(70, 146, "断面の組織")
    return s


@picto("resid")
def _():
    s = rect(40, 140, 240, 30, "w")
    s += "<g transform=\"rotate(30 110 80)\">" + rect(80, 60, 60, 30, "m3") + "</g>"
    s += "<g transform=\"rotate(-30 210 80)\">" + rect(180, 60, 60, 30, "m2") + "</g>"
    s += line(130, 100, 160, 138, "ray") + line(160, 138, 190, 100, "ray")
    s += lab(160, 196, "X線回折で表面の残留応力を測る")
    return s


@picto("destruct")
def _():
    s = path("M40 140 L280 140 L280 152 L40 152Z", "w") + path("M40 130 L160 130 Q200 110 250 70", "sheet")
    s += poly([(160, 136), (230, 80), (240, 90)], "t")
    s += ell(150, 136, 10, 4, "h")
    s += lab(160, 186, "たがねで剥がしてナゲットを確認")
    return s


@picto("clean")
def _():
    s = circ(100, 104, 60, "m") + circ(100, 104, 50, "filt")
    for (x, y, r) in ((80, 90, 3), (110, 120, 2), (120, 84, 4), (90, 126, 2), (70, 110, 2)):
        s += circ(x, y, r, "d")
    s += rect(200, 40, 80, 120, "m2", 4) + lab(240, 176, "重量・粒径を分析")
    return s


@picto("meltq")
def _():
    s = path("M40 60 L130 60 L122 150 L48 150Z", "m2") + rect(52, 80, 66, 66, "h")
    s += path("M200 110 L250 110 L246 150 L204 150Z", "m2") + rect(208, 120, 34, 26, "h")
    s += arrow(130, 90, 196, 116, "採取", 164, 90)
    s += lab(225, 176, "減圧凝固・成分分析")
    return s


@picto("receive")
def _():
    s = circ(110, 110, 60, "w2") + circ(110, 110, 20, "m2")
    s += rect(210, 50, 80, 110, "m", 4)
    for y in (74, 94, 114, 134):
        s += line(222, y, 278, y, "o thin")
    s += path("M226 70 l4 4 l8 -8", "a")
    s += lab(250, 180, "ミルシート照合")
    return s


@picto("crimpmon")
def _():
    s = PICTOS["crimp"]()
    s += chart(10, 10, 110, 60, "peak")
    return s


@picto("slurrymeas")
def _():
    s = path("M100 90 L220 90 L214 180 L106 180Z", "m2") + rect(110, 110, 100, 66, "slurry")
    s += rect(152, 20, 16, 120, "m3") + rect(140, 130, 40, 14, "t")
    s += rot(160, 137, 30, 8, 20, 160, "粘度", 230, 140)
    return s


@picto("magcheck")
def _():
    s = shaft(60, 104, [(150, 50)], "w", "w2")
    s += rect(240, 60, 16, 40, "m3") + line(248, 100, 222, 104, "o")
    s += chart(10, 10, 100, 50, "sine")
    return s


# ============================================================ tests
@picto("balance")
def _():
    cy = 100
    s = rect(40, 150, 240, 20, "m2") + rect(70, cy + 10, 20, 40, "m") + rect(230, cy + 10, 20, 40, "m")
    s += shaft(50, cy, [(40, 10), (140, 44), (40, 10)], "w", "w2")
    s += arrow(160, cy, 190, cy - 50, "アンバランス", 210, 40)
    s += rot(120, cy, 14, 48, -60, 60)
    s += lab(160, 190, "測って穴あけ・切削で修正")
    return s


@picto("func")
def _():
    s = rect(20, 150, 280, 20, "m2") + box(110, 90, 100, 60, 24, "w2", "w", "w3")
    s += shaft(30, 120, [(50, 22), (30, 8)], "m", "m2") + shaft(226, 120, [(30, 8), (30, 14)], "m", "m2")
    s += lab(55, 84, "駆動", "middle") + lab(270, 84, "トルク計", "middle")
    s += chart(120, 10, 100, 60, "ramp")
    return s


@picto("load")
def _():
    s = rect(80, 20, 160, 20, "m3") + rect(140, 40, 40, 16, "m2") + lab(200, 52, "ロードセル", "start")
    s += vcoil(160, 108, 100, 38, 5)
    s += rect(80, 160, 160, 20, "m2")
    return s


@picto("fatigue")
def _():
    s = rect(40, 170, 240, 16, "m2") + rect(60, 30, 16, 140, "m") + rect(244, 30, 16, 140, "m") + rect(50, 20, 220, 16, "m3")
    s += rect(150, 36, 20, 30, "m2") + rect(146, 66, 28, 70, "w") + rect(140, 136, 40, 34, "t")
    s += arrow(200, 150, 200, 110, None, both=True) + lab(210, 134, "繰返し荷重", "start")
    s += chart(210, 40, 90, 50, "sine")
    return s


@picto("dampertest")
def _():
    s = rect(40, 170, 240, 16, "m2") + rect(60, 30, 16, 140, "m") + rect(244, 30, 16, 140, "m") + rect(50, 20, 220, 16, "m3")
    s += shaft(152, 40, [(1, 1)], "o", "o") if False else rect(155, 36, 10, 50, "cr") + rect(146, 86, 28, 60, "w") + rect(140, 146, 40, 24, "t")
    s += arrow(200, 150, 200, 110, None, both=True) + lab(210, 134, "加振", "start")
    s += chart(210, 40, 90, 50, "sine")
    return s


@picto("flowtest")
def _():
    s = rect(140, 10, 40, 60, "m3") + poly([(150, 70), (170, 70), (164, 90), (156, 90)], "m2")
    s += spray_cone(160, 90, 90, 40, 50) + drops(160, 92, 5, 40, 44, 90)
    s += tank(110, 120, 100, 70, 0.4)
    s += lab(250, 150, "流量・噴霧形状", "middle")
    return s


@picto("engine")
def _():
    s = rect(10, 160, 300, 16, "m2")
    s += box(40, 80, 110, 80, 40, "w2", "w", "w3") + box(44, 60, 102, 20, 36, "m2", "m", "m3")
    s += shaft(150, 124, [(60, 8)], "m", "m2") + rect(210, 90, 80, 70, "m3", 6) + lab(250, 130, "ダイナモ", "middle")
    s += lab(95, 190, "エンジン") + chart(210, 10, 100, 60, "rise")
    return s


@picto("motortest")
def _():
    s = rect(10, 160, 300, 16, "m2") + shaft(30, 124, [(110, 36)], "w", "w2")
    s += shaft(140, 124, [(70, 8)], "m", "m2") + rect(210, 90, 80, 70, "m3", 6) + lab(250, 130, "負荷装置", "middle")
    s += chart(40, 10, 110, 60, "rise")
    return s


@picto("nvh")
def _():
    s = rect(10, 160, 300, 16, "m2") + PICTOS["func"]() if False else rect(10, 160, 300, 16, "m2")
    s += box(100, 90, 120, 70, 24, "w2", "w", "w3") + shaft(20, 124, [(80, 10)], "m", "m2") + shaft(234, 124, [(70, 10)], "m", "m2")
    s += rect(240, 40, 12, 30, "m3") + circ(246, 36, 8, "m") + lab(262, 30, "マイク", "start")
    s += chart(20, 10, 110, 60, "noise")
    return s


@picto("battery")
def _():
    s = box(80, 70, 90, 110, 30, "w2", "w", "w3") + rect(96, 56, 18, 12, "cu") + rect(140, 56, 18, 12, "m")
    s += path("M105 56 L105 30 L230 30 L230 60", "cable") + path("M149 56 L149 40 L250 40 L250 60", "cable")
    s += rect(210, 60, 90, 70, "m", 4) + lab(255, 90, "OCV", "middle") + lab(255, 110, "内部抵抗", "middle")
    return s


@picto("hipot")
def _():
    s = shaft(60, 120, [(160, 50)], "w", "w2")
    s += lightning(250, 40, 1.4) + rect(230, 110, 70, 50, "m3", 4) + lab(265, 180, "高電圧印加")
    s += path("M230 130 L200 130", "cable")
    return s


@picto("ict")
def _():
    s = rect(40, 70, 240, 14, "pcb")
    for x in range(56, 270, 16):
        s += line(x, 90, x, 140, "o") + circ(x, 88, 2.4, "t")
    s += rect(40, 140, 240, 24, "m3") + lab(160, 186, "ピンで各回路に接触して測る")
    s += arrow(160, 20, 160, 60, None)
    return s


@picto("continuity")
def _():
    s = rect(20, 120, 280, 60, "board", 4) + path("M60 140 C120 120 200 160 260 140", "cable3")
    s += rect(40, 132, 24, 18, "w", 2) + rect(256, 132, 24, 18, "w", 2)
    s += rect(120, 30, 90, 60, "m", 4) + circ(165, 60, 10, "okl") + lab(165, 20, "全回路の導通・誤配線")
    return s


@picto("semitest")
def _():
    s = box(60, 110, 140, 30, 50, "w2", "w", "w3") + rect(40, 140, 180, 20, "m2")
    s += chart(210, 30, 100, 70, "step") + lab(160, 190, "静特性・スイッチング特性")
    return s


@picto("env")
def _():
    s = rect(60, 20, 200, 160, "m", 8) + rect(80, 40, 160, 110, "coolin")
    s += box(130, 90, 60, 40, 16, "w2", "w", "w3")
    s += rect(270, 40, 14, 100, "m2") + rect(274, 70, 6, 66, "h") + lab(277, 160, "−40〜125℃")
    return s


@picto("calib")
def _():
    s = rect(20, 30, 120, 120, "m")
    for i in range(6):
        for j in range(6):
            if (i + j) % 2 == 0:
                s += rect(20 + i * 20, 30 + j * 20, 20, 20, "d")
    s += rect(220, 80, 60, 40, "m3") + circ(220, 100, 12, "gl2")
    s += line(208, 100, 140, 60, "o thin dash") + line(208, 100, 140, 140, "o thin dash")
    s += lab(250, 150, "チャートを撮像して校正", "middle")
    return s


@picto("deploy")
def _():
    s = box(120, 150, 80, 24, 20, "m2", "m", "m3")
    s += path("M130 150 Q80 110 110 60 Q150 20 200 50 Q250 90 200 150Z", "w")
    s += lab(250, 40, "展開挙動を確認", "middle")
    return s


@picto("bnoise")
def _():
    s = shaft(20, 110, [(120, 12)], "m", "m2") + ell(150, 110, 16, 50, "w") + ell(150, 110, 8, 24, "w2")
    s += rect(190, 60, 12, 40, "m3") + line(196, 100, 166, 104, "o")
    s += chart(210, 110, 100, 70, "noise")
    return s


@picto("uniformity")
def _():
    s = circ(110, 104, 76, "rbx") + circ(110, 104, 40, "m2")
    s += circ(254, 104, 60, "m") + circ(254, 104, 10, "m3")
    s += arrow(300, 30, 250, 30, "荷重", 276, 24)
    s += rot(110, 104, 86, 86, 200, 260) + lab(160, 196, "回転中の力の変動を測る")
    return s


@picto("alignment")
def _():
    s = circ(120, 110, 70, "rbx") + circ(120, 110, 40, "m2")
    s += rect(240, 40, 50, 30, "m3") + rect(240, 150, 50, 30, "m3")
    s += line(240, 55, 180, 80, "laserl") + line(240, 165, 180, 140, "laserl")
    s += lab(160, 20, "トー・キャンバを非接触で計測")
    return s


@picto("aim")
def _():
    s = rect(20, 90, 60, 40, "m2", 10) + circ(70, 110, 14, "gl2")
    s += poly([(84, 104), (240, 60), (240, 150), (84, 116)], "beamf")
    s += rect(240, 30, 60, 150, "m") + path("M240 110 L270 110 L290 96", "a")
    s += lab(270, 196, "カットオフライン")
    return s


@picto("adas")
def _():
    s = car(10, 170, 0.8, "w", "sedan")
    s += rect(230, 40, 70, 100, "m")
    for i in range(3):
        for j in range(5):
            if (i + j) % 2 == 0:
                s += rect(236 + i * 20, 46 + j * 18, 18, 16, "d")
    s += line(150, 116, 230, 90, "o thin dash")
    s += lab(265, 160, "ターゲット")
    return s


@picto("drum")
def _():
    s = rect(10, 170, 300, 14, "m2") + car(60, 164, 1.0, "w", "sedan")
    for x in (95, 203):
        s += circ(x - 12, 172, 10, "m") + circ(x + 12, 172, 10, "m")
    s += lab(160, 20, "ローラ上で速度計・ブレーキを試験")
    return s


@picto("emission")
def _():
    s = car(100, 170, 1.0, "w", "sedan") + path("M100 160 L60 160", "cable") + rect(10, 130, 50, 50, "m3", 4)
    s += lab(35, 120, "分析計", "middle")
    return s


@picto("shower")
def _():
    s = car(60, 176, 1.0, "w", "sedan")
    for x in (60, 110, 160, 210, 260):
        s += nozzle(x, 30, 90, 14) + drops(x, 30, 3, 30, 40, 90)
    s += lab(160, 196, "高圧散水で雨漏りを確認")
    return s


@picto("noise")
def _():
    s = car(20, 170, 0.9, "w", "sedan") + circ(250, 70, 14, "m") + rect(246, 84, 8, 30, "m3")
    s += chart(200, 120, 110, 60, "noise")
    return s


@picto("mass")
def _():
    return PICTOS["balance"]()


@picto("surfinsp")
def _():
    s = path("M20 150 Q160 100 300 150 L300 170 Q160 120 20 170Z", "w")
    for i in range(5):
        s += path("M%s %s Q160 %s %s %s" % (n(40), n(126 + i * 6 - 20), n(100 + i * 6 - 20), n(280), n(126 + i * 6 - 20)), "o thin")
    s += lab(160, 196, "照明の映り込みで微小な凹凸を見る")
    return s


@picto("cooling")
def _():
    s = conveyor(10, 140, 300)
    for x in (40, 100, 160, 220, 280):
        s += rect(x - 16, 118, 32, 22, "h", 3)
    for x in (70, 160, 250):
        s += circ(x, 40, 18, "m") + circ(x, 40, 5, "m3")
        s += arrow(x, 62, x, 106, None)
    s += lab(160, 186, "送風で冷却速度を制御（非調質鋼）")
    return s


def hanger_parts(y=40):
    s = line(40, y, 280, y, "rail")
    for x in (90, 160, 230):
        s += line(x, y, x, y + 40, "o") + rect(x - 24, y + 40, 48, 30, "w", 3)
    return s


@picto("ed_part")
def _():
    s = tank(20, 90, 280, 100, 0.8) + hanger_parts(30)
    s += rect(26, 110, 10, 70, "cu") + rect(284, 110, 10, 70, "cu") + lab(31, 104, "＋") + lab(289, 104, "＋")
    s += lab(160, 22, "−（部品）") + lab(160, 196, "部品をハンガーに掛けて電着")
    return s


@picto("dip_part")
def _():
    s = tank(20, 90, 280, 100, 0.8) + hanger_parts(30)
    s += lab(160, 196, "部品を浸漬して防錆皮膜をつくる")
    return s


@picto("paintpart")
def _():
    s = path("M150 110 Q156 80 190 78 L290 78 Q300 80 300 100 L300 150 Q298 162 286 162 L170 162 Q152 160 150 140Z", "w")
    s += rect(160, 162, 130, 10, "m2")
    r, (tx, ty) = robot(46, 190, 1.0, -80, 58)
    s += r + path("M%s %s l12 -5 l0 14 z" % (n(tx), n(ty - 4)), "t")
    s += spray_cone(tx + 12, ty + 2, 25, 40, 50) + drops(tx + 14, ty + 2, 5, 34, 44, 25)
    s += lab(236, 60, "バンパー（治具に固定）")
    return s
