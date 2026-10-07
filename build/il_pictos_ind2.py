"""Principle drawings (320x200) for heavy electrical / heavy-industry equipment and test rigs:
coil spreading, large overhead cranes, laser trackers, load banks, manual arc welding,
hydraulic bolt tensioning, material testing, hydrostatic testing, spin testing,
shaft alignment, epoxy casting and stator core loop testing.
Imported after il_pictos; registers into the same PICTOS table."""
import math
from il_base import *
from il_pictos import picto, lab, tank, bubbles


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def sm(x, y, t, a="middle"):
    return text(x, y, t, a, "sm")


def person(x, y, h=26):
    """small single-colour silhouette with feet at (x, y): scale cue for very large equipment."""
    k = h / 26.0
    body = [(-5, -19), (5, -19), (4.6, -9), (3.6, 0), (0.9, 0), (0, -8), (-0.9, 0), (-3.6, 0), (-4.6, -9)]
    return circ(x, y - 22.6 * k, 3.3 * k, "m3") + poly([(x + a * k, y + b * k) for a, b in body], "m3")


def hatch(x, y, w, h, step=7):
    """sectioned material: cut fill with 45deg hatch lines clipped to the rectangle."""
    s = rect(x, y, w, h, "cut")
    t = step
    while t < w + h:
        x1, y1 = x + max(0, t - h), y + min(h, t)
        x2, y2 = x + min(w, t), y + max(0, t - w)
        s += line(x1, y1, x2, y2, "hatch")
        t += step
    return s


def gauge(cx, cy, r, ang=-40):
    a = math.radians(ang - 90)
    return circ(cx, cy, r, "bg") + line(cx, cy, cx + r * 0.75 * math.cos(a), cy + r * 0.75 * math.sin(a), "needle") + \
        circ(cx, cy, 1.4, "d")


def nut(x, y, w, h):
    """hex nut seen from the side (three flats)."""
    return rect(x, y, w, h, "w2", 1) + line(x + w * 0.25, y, x + w * 0.25, y + h, "o thin") + \
        line(x + w * 0.75, y, x + w * 0.75, y + h, "o thin")


def zig(x, y, w, amp, cnt, c="hl"):
    ps = [(x, y)]
    for i in range(cnt):
        ps.append((x + w * (i + 0.5) / cnt, y + (amp if i % 2 == 0 else -amp)))
    ps.append((x + w, y))
    return pline(ps, c)


# ------------------------------------------------------------ 形巻コイル成形機（コイルスプレッダ）
@picto("coilspread")
def _():
    s = rect(10, 168, 300, 12, "m2", 2) + shadow(160, 184, 140, 4)
    s += rect(12, 56, 22, 112, "m", 2) + rect(286, 56, 22, 112, "m", 2)
    # spread coil: two straight legs (slot parts) joined by the V-shaped ends and noses
    def hexa(k):
        return [(44 + k, 112), (106 + k * 0.4, 70 + k), (214 - k * 0.4, 70 + k), (276 - k, 112), (214 - k * 0.4, 154 - k),
                (106 + k * 0.4, 154 - k)]
    for k, c in ((0, "cuwire2"), (6, "cuwire2")):
        hp = hexa(k)
        s += path("M" + " L".join(n(a) + " " + n(b) for a, b in hp) + "Z", c)
    s += path("M" + " L".join(n(a) + " " + n(b) for a, b in hexa(3)) + "Z", "o thin")
    # nose holders on the end heads
    for x, d in ((44, -1), (276, 1)):
        s += rect(min(x, x + 14 * d), 104, 14, 16, "m3", 2) + circ(x, 112, 5, "m2")
    # leg clamps: upper pair on a lifting beam, lower pair fixed on the bed
    s += rect(100, 38, 120, 9, "m2", 2) + rect(118, 47, 6, 14, "m2") + rect(196, 47, 6, 14, "m2")
    for x in (112, 190):
        s += rect(x, 61, 18, 18, "m3", 2) + rect(x, 145, 18, 18, "m3", 2)
    s += rect(118, 163, 6, 5, "m2") + rect(196, 163, 6, 5, "m2")
    s += arrow(160, 36, 160, 14, "広げる", 168, 26, "start")
    s += arrow(80, 29, 100, 29, None)
    # before: the wound loop
    s += path("M22 22 L66 22 A7 7 0 0 1 66 36 L22 36 A7 7 0 0 1 22 22Z", "cuwire2")
    s += sm(46, 13, "巻いたループ") + lab(160, 112, "亀甲形に成形")
    s += lab(160, 197, "直線部をつかんで広げ、エンドを形づける")
    return s


# ------------------------------------------------------------ 天井クレーン（大型）
@picto("ohcrane")
def _():
    s = rect(8, 46, 12, 140, "m") + rect(300, 46, 12, 140, "m")
    s += rect(4, 40, 22, 8, "m3") + rect(294, 40, 22, 8, "m3")
    s += box(12, 26, 296, 14, 10, "m2", "m3", "m3")
    s += circ(20, 41, 3.5, "m2") + circ(300, 41, 3.5, "m2")
    s += box(128, 10, 64, 16, 10, "m", "m2", "m3") + circ(146, 18, 5, "m3") + circ(174, 18, 5, "m3")
    for x in (148, 154, 166, 172):
        s += line(x, 40, x, 88, "o")
    s += rect(140, 86, 40, 18, "m3", 3) + circ(152, 95, 5, "m2") + circ(168, 95, 5, "m2")
    s += path("M160 104 L160 112 Q160 120 153 120 Q147 120 147 114", "rail")
    s += line(158, 118, 118, 132, "o") + line(162, 118, 206, 128, "o")
    s += box(112, 134, 92, 36, 22, "w2", "w", "w3")
    s += rect(86, 176, 154, 10, "m2", 2) + shadow(160, 188, 96, 3)
    s += person(270, 186, 24)
    s += arrow(206, 54, 262, 54, None, both=True) + lab(234, 68, "横行")
    s += arrow(30, 82, 54, 62, None, both=True) + lab(58, 80, "走行", "start")
    s += arrow(240, 96, 240, 140, None, both=True) + lab(248, 122, "巻上げ", "start")
    s += lab(104, 160, "数十〜数百t", "end")
    return s


# ------------------------------------------------------------ レーザトラッカ
@picto("lasertrack")
def _():
    s = shadow(62, 186, 34, 3) + shadow(232, 184, 76, 4)
    for x in (34, 62, 90):
        s += line(62, 118, x, 184, "rail")
    s += rect(56, 104, 12, 18, "m2")
    s += rect(42, 94, 40, 12, "m3", 2)
    s += rect(44, 58, 7, 38, "m2", 2) + rect(73, 58, 7, 38, "m2", 2)
    s += circ(62, 72, 13, "m") + circ(70, 72, 4, "gl")
    s += box(162, 140, 128, 42, 26, "w2", "w", "w3")
    for x, y in ((186, 132), (214, 128), (270, 129), (290, 125)):
        s += circ(x, y, 2.2, "loc")
    s += line(74, 73, 240, 126, "laserl")
    s += circ(242, 125, 6.5, "t") + circ(242, 125, 2.5, "d")
    s += rot(62, 106, 30, 7, 30, 150) + rot(62, 72, 22, 22, -150, -60)
    s += lab(74, 30, "水平・垂直に回って追尾")
    s += lab(248, 106, "反射球", "start")
    s += arrow(110, 50, 222, 86, None, both=True) + lab(184, 54, "〜数十m", "start")
    s += lab(160, 198, "距離と2つの角度から3次元座標")
    return s


# ------------------------------------------------------------ 負荷試験装置（ロードバンク）
def vfchart(x, y, w, h):
    s = rect(x, y, w, h, "m", 3)
    s += line(x + 6, y + h - 6, x + w - 6, y + h - 6, "o thin") + line(x + 6, y + 6, x + 6, y + h - 6, "o thin")
    ym = y + h * 0.45
    ps, ld = [], []
    for i in range(51):
        t = i / 50
        xx = x + 8 + (w - 16) * t
        yy = ym
        if t > 0.35:
            u = (t - 0.35) * 14
            yy = ym + h * 0.32 * math.exp(-u) * math.cos(u * 1.3)
        ps.append((xx, yy))
    s += pline(ps, "a")
    xs = x + 8 + (w - 16) * 0.35
    s += pline([(x + 8, y + h - 10), (xs, y + h - 10), (xs, y + h - 18), (x + w - 8, y + h - 18)], "o thin dash")
    return s


@picto("loadbank")
def _():
    s = shadow(64, 162, 54, 3) + shadow(214, 172, 74, 4)
    s += rect(12, 148, 104, 12, "m2", 2)
    s += shaft(16, 118, [(80, 30), (16, 9)], "m", "m2")
    s += rect(36, 78, 30, 12, "m3", 2)
    for i in range(3):
        d = i * 5
        s += path("M%d 80 C%d 50 %d 52 %d 70" % (44 + d, 44 + d, 120 + d, 160 + d), "cable")
    s += box(150, 72, 112, 98, 22, "m2", "m", "m3")
    s += rect(160, 84, 92, 56, "bg", 2)
    for j in range(4):
        s += zig(166, 94 + j * 13, 80, 3.5, 14)
    for i in range(4):
        s += rect(166 + i * 22, 148, 14, 12, "m3", 2)
    s += ell(220, 62, 16, 5, "m3")
    s += heat(210, 52, 3, 10)
    s += lab(234, 30, "送風で放熱", "start")
    s += vfchart(10, 8, 112, 58) + sm(66, 20, "電圧・周波数")
    s += lab(64, 180, "発電機") + lab(206, 192, "抵抗器で負荷をつくる")
    return s


# ------------------------------------------------------------ アーク溶接機（半自動・TIG）
@picto("mig_tig")
def _():
    s = shadow(66, 162, 50, 3) + shadow(162, 160, 54, 3)
    s += path("M14 44 L14 158 A10 3 0 0 0 34 158 L34 44Z", "m2") + ell(24, 44, 10, 3, "m3") + rect(20, 32, 8, 10, "m3", 1)
    s += path("M28 40 C44 40 46 70 54 84", "o")
    s += box(40, 110, 56, 50, 16, "m2", "m", "m3")
    s += rect(48, 118, 22, 10, "bg", 1) + circ(84, 123, 4, "m3") + circ(84, 140, 4, "m3") + rect(48, 136, 22, 14, "m3", 2)
    s += box(44, 84, 44, 24, 12, "m2", "m", "m3") + circ(60, 96, 9, "m2") + circ(60, 96, 5, "cu")
    s += path("M88 100 C122 118 120 72 148 78", "cable")
    s += path("M146 74 L160 92", "arm2") + path("M158 89 Q170 100 170 120", "arm2")
    s += poly([(165, 118), (176, 118), (175, 132), (166, 132)], "t")
    s += line(171, 132, 172, 140, "o")
    s += spray_cone(170, 130, 90, 54, 16, "fo")
    s += rect(108, 144, 64, 12, "w") + rect(172, 144, 40, 12, "w2")
    s += path("M114 144 Q119 138 124 144 Q129 138 134 144 Q139 138 144 144 Q149 138 154 144 Q159 138 164 144", "bead")
    s += ell(172, 144, 6, 2.5, "h") + sparks(172, 142, 10, 6, -165, -15)
    s += lab(68, 178, "溶接電源") + lab(66, 76, "ワイヤ送給") + lab(140, 60, "トーチ")
    s += lab(132, 128, "ガス", "end") + al(10, 16, "半自動（CO2・MAG）", "start")
    # TIG
    s += rect(222, 10, 92, 182, "o thin", 8) + al(268, 28, "TIG")
    s += rect(262, 40, 14, 44, "m3", 3) + poly([(260, 84), (278, 84), (274, 100), (264, 100)], "bg")
    s += rect(267.5, 100, 3, 14, "t") + line(269, 114, 269, 124, "hl") + line(267, 114, 264, 124, "hl") + line(271, 114, 274, 124, "hl")
    s += rect(230, 126, 78, 12, "w") + ell(269, 126, 7, 2.6, "h")
    s += line(236, 96, 260, 122, "strip")
    s += sm(242, 90, "溶加棒") + sm(268, 154, "タングステン電極") + sm(268, 168, "薄板・ステンレス")
    return s


# ------------------------------------------------------------ 油圧ボルトテンショナ
@picto("tensioner")
def _():
    s = shadow(160, 190, 112, 3)
    # clamped parts (section) with the stud passing through
    s += hatch(60, 120, 90, 22) + hatch(170, 120, 90, 22)
    s += hatch(60, 142, 90, 44) + hatch(170, 142, 90, 44)
    s += line(60, 142, 260, 142, "o")
    s += rect(150, 28, 20, 152, "w")
    for y in range(32, 178, 6):
        if y < 46 or y > 100:
            s += line(150, y, 170, y + 2, "o thin")
    # nut lifted off its seat while the stud is stretched
    s += nut(136, 98, 48, 16)
    s += sm(110, 117, "すき間", "end")
    # bridge with window for the tommy bar
    s += rect(114, 84, 14, 36, "m2") + rect(192, 84, 14, 12, "m2") + rect(192, 114, 14, 6, "m2")
    # hydraulic cylinder, piston, puller nut
    s += rect(108, 46, 104, 40, "m3", 3) + rect(122, 52, 76, 22, "m2", 2) + rect(122, 74, 76, 7, "fl")
    s += rect(150, 46, 20, 40, "w")
    s += nut(138, 30, 44, 16)
    s += arrow(160, 28, 160, 6, "引っ張る", 170, 18, "start")
    # tommy bar
    s += line(184, 106, 250, 106, "rail")
    s += arrow(248, 92, 228, 92, "回す", 252, 96, "start")
    # hose and pump
    s += path("M212 70 C240 70 244 44 262 44", "cable")
    s += rect(262, 34, 48, 30, "m2", 3) + gauge(286, 20, 9)
    s += lab(286, 78, "油圧ポンプ")
    s += lab(4, 70, "油圧ジャッキ", "start") + lab(4, 112, "ナット", "start") + lab(4, 166, "締付け部材", "start")
    return s


# ------------------------------------------------------------ 材料試験機（引張・衝撃）
@picto("tensile_charpy")
def _():
    s = shadow(80, 186, 70, 3) + shadow(250, 186, 64, 3)
    # universal testing machine: frame, load cell, wedge grips, necked round specimen
    s += rect(14, 166, 132, 18, "m2", 2) + rect(26, 30, 10, 136, "m") + rect(124, 30, 10, 136, "m")
    s += rect(20, 18, 120, 14, "m3", 2) + rect(66, 32, 28, 10, "m2", 2)
    s += rect(20, 146, 120, 12, "m3", 2)
    s += poly([(68, 42), (92, 42), (88, 60), (72, 60)], "m3") + poly([(72, 130), (88, 130), (92, 146), (68, 146)], "m3")
    sp = [(74, 56), (86, 56), (86, 74), (84, 78), (84, 90), (82.5, 96), (84, 102), (84, 114), (86, 118), (86, 134),
          (74, 134), (74, 118), (76, 114), (76, 102), (77.5, 96), (76, 90), (76, 78), (74, 74)]
    s += poly(sp, "w")
    s += arrow(104, 86, 104, 60, None) + arrow(104, 108, 104, 134, None) + lab(104, 101, "引張")
    s += lab(80, 198, "引張強さ・伸び")
    s += line(160, 16, 160, 184, "o thin dash")
    # Charpy impact tester: raised pendulum, swing path, anvil with notched specimen
    s += rect(176, 168, 136, 12, "m2", 2) + rect(292, 24, 12, 144, "m") + rect(236, 22, 68, 10, "m3", 2)
    s += rot(250, 32, 92, 92, 152, 52)
    s += circ(250, 124, 13, "hid")
    s += rect(262, 128, 22, 40, "m2") + rect(263, 118, 9, 10, "w")
    s += path("M250 32 L170 70", "arm2") + circ(167, 72, 14, "m3") + poly([(176, 80), (182, 74), (186, 86)], "t")
    s += circ(250, 32, 5, "m2")
    s += lab(204, 20, "振り子", "start")
    # inset: specimen seen from above, notch on the far side from the blow
    s += rect(184, 140, 52, 8, "w") + path("M206 148 L210 142 L214 148Z", "bg")
    s += rect(184, 148, 7, 5, "m3") + rect(229, 148, 7, 5, "m3")
    s += arrow(210, 124, 210, 138, None) + sm(222, 162, "切欠き", "start")
    s += lab(240, 198, "吸収エネルギー（ねばさ）")
    return s


# ------------------------------------------------------------ 水圧試験装置
def drop(x, y, k=1.0):
    return path("M%s %s q%s %s 0 %s q%s %s 0 %sZ" % (n(x), n(y), n(3.5 * k), n(5 * k), n(8 * k), n(-3.5 * k), n(-3 * k), n(-8 * k)), "fl")


@picto("hydrotest")
def _():
    s = shadow(140, 172, 100, 3)
    s += hatch(50, 64, 180, 104)
    s += rect(70, 84, 140, 62, "fl") + rect(50, 102, 20, 26, "fl") + rect(130, 64, 22, 20, "fl") + rect(210, 104, 20, 22, "fl")
    # blind plates bolted over the openings
    s += rect(38, 94, 12, 42, "m3", 1) + rect(32, 98, 20, 4, "m2") + rect(32, 128, 20, 4, "m2")
    s += rect(120, 52, 42, 12, "m3", 1) + rect(124, 48, 4, 18, "m2") + rect(154, 48, 4, 18, "m2")
    s += rect(230, 96, 12, 38, "m3", 1) + rect(228, 100, 20, 4, "m2") + rect(228, 126, 20, 4, "m2")
    for x2, y2 in ((140, 92), (140, 138), (96, 115), (184, 115)):
        s += arrow(140 + (x2 - 140) * 0.25, 115 + (y2 - 115) * 0.25, x2, y2, None)
    # pump, pipe and gauge
    s += path("M242 115 L282 115 L282 132", "pres") + path("M262 115 L262 92", "pres")
    s += gauge(262, 80, 13, 30)
    s += box(256, 132, 50, 34, 10, "m2", "m", "m3") + circ(281, 149, 7, "m3")
    s += lab(281, 182, "加圧ポンプ") + lab(262, 58, "圧力計")
    # pressure-hold chart
    s += rect(8, 8, 104, 40, "m", 3) + line(14, 42, 106, 42, "o thin")
    s += pline([(16, 41), (34, 18), (100, 18)], "a") + sm(64, 34, "一定時間保持")
    # seepage on the outer surface
    s += drop(176, 170) + drop(186, 176, 0.8) + drop(54, 150, 0.8)
    s += lab(140, 194, "外面のにじみ・漏れを目で確かめる")
    return s


# ------------------------------------------------------------ スピン試験装置
@picto("spinpit")
def _():
    s = shadow(150, 190, 100, 3)
    s += hatch(60, 56, 20, 120) + hatch(220, 56, 20, 120) + hatch(60, 174, 180, 14) + hatch(50, 42, 200, 14)
    s += rect(80, 56, 140, 118, "bg2")
    s += rect(80, 108, 9, 48, "m3") + rect(211, 108, 9, 48, "m3")
    s += rect(128, 12, 64, 30, "m2", 4) + rect(140, 6, 40, 6, "m3", 2)
    s += rect(158, 42, 4, 76, "w")
    s += vcyl(160, 128, 6, 46, 12, "w", "w2")
    for i in range(10):
        a = math.radians(i * 36 + 10)
        x1, y1 = 160 + 12 * math.cos(a), 128 + 3.2 * math.sin(a)
        x2, y2 = 160 + 44 * math.cos(a + 0.6), 128 + 11.5 * math.sin(a + 0.6)
        xm, ym = 160 + 30 * math.cos(a + 0.15), 128 + 8 * math.sin(a + 0.15)
        s += path("M%s %s Q%s %s %s %s" % (n(x1), n(y1), n(xm), n(ym), n(x2), n(y2)), "o")
    s += vcyl(160, 116, 12, 11, 3, "w", "w2")
    s += rot(160, 134, 56, 16, 30, 150)
    s += rect(198, 124, 13, 6, "m3") + circ(198, 127, 2.5, "sensor")
    s += rect(170, 66, 13, 6, "m3") + rect(183, 64, 37, 3, "m3")
    s += path("M240 162 L268 162", "rail") + rect(262, 148, 50, 28, "m2", 3) + circ(287, 162, 8, "m3")
    s += sm(110, 82, "真空") + lab(287, 192, "真空ポンプ")
    s += lab(198, 28, "駆動タービン", "start")
    s += lab(246, 74, "回転計", "start") + lab(246, 130, "変位センサ", "start")
    s += lab(56, 134, "防護", "end") + lab(56, 148, "リング", "end")
    return s


# ------------------------------------------------------------ 軸芯出し装置
@picto("shaftalign")
def _():
    s = shadow(70, 160, 64, 3) + shadow(262, 160, 54, 3)
    s += rect(8, 150, 124, 10, "m3") + rect(212, 150, 102, 10, "m3")
    s += rect(10, 48, 52, 102, "m2", 4)
    s += shaft(62, 96, [(20, 50), (16, 10), (36, 22)], "m", "m2")
    s += shaft(150, 96, [(24, 22), (60, 11)], "w", "w2")
    s += shaft(232, 96, [(78, 44)], "m", "m2") + rect(242, 138, 60, 8, "m2") + rect(256, 146, 22, 4, "t")
    # laser units on brackets
    s += rect(115, 54, 6, 22, "m3") + rect(100, 36, 32, 18, "m3", 3) + circ(128, 45, 3.5, "gl")
    s += rect(193, 56, 6, 30, "m3") + rect(180, 36, 32, 18, "m3", 3) + circ(184, 45, 3.5, "gl")
    s += line(132, 45, 180, 45, "beam")
    s += lab(156, 24, "レーザ") + lab(36, 40, "機関") + lab(270, 40, "発電機")
    s += arrow(298, 176, 278, 151, None) + sm(300, 186, "シム", "end")
    # exaggerated misalignment: offset and angle
    s += line(20, 176, 66, 176, "rail") + line(70, 184, 116, 184, "rail") + sm(68, 196, "偏心")
    s += line(150, 182, 196, 182, "rail") + line(198, 182, 242, 170, "rail") + sm(196, 196, "面の倒れ")
    return s


# ------------------------------------------------------------ エポキシ注形設備（真空注形・APG）
@picto("epoxycast")
def _():
    s = shadow(56, 134, 44, 3) + shadow(195, 160, 70, 3) + shadow(290, 188, 22, 2)
    s += tank(18, 42, 74, 86, 0.6, "resin")
    s += rect(14, 34, 82, 8, "m3", 2) + rect(44, 14, 22, 20, "m2", 3)
    s += line(55, 34, 55, 110, "stem") + poly([(36, 106), (74, 106), (70, 114), (40, 114)], "m3")
    s += bubbles(55, 100, 5, 40, 22)
    s += path("M88 34 L88 22 L108 22", "rail") + sm(112, 25, "真空", "start")
    s += path("M55 128 L55 146 L118 146 L118 116 L136 116", "rail")
    # heated two-part mould with an insulator cavity around a metal insert
    s += rect(132, 56, 126, 8, "m3", 2) + rect(132, 148, 126, 8, "m3", 2)
    s += rect(138, 64, 114, 44, "m2") + rect(138, 108, 114, 40, "m2")
    prof = [(156, 14), (162, 14), (164, 24), (170, 24), (172, 14), (182, 14), (184, 24), (190, 24), (192, 14), (202, 14),
            (204, 24), (210, 24), (212, 14), (222, 14), (224, 24), (230, 24), (232, 14), (238, 14)]
    top = [(x, 108 - r) for x, r in prof]
    bot = [(x, 108 + r) for x, r in reversed(prof)]
    s += poly(top + bot, "resin")
    s += rect(142, 104, 106, 8, "cu")
    for y in (72, 142):
        s += line(146, y, 244, y, "hl dash")
    s += line(138, 108, 252, 108, "o thin")
    s += arrow(195, 22, 195, 52, "加圧（APG）", 204, 38, "start")
    s += sm(195, 170, "加熱金型・インサート（導体）")
    # finished post insulator
    s += rect(281, 112, 18, 10, "w") + rect(281, 174, 18, 10, "w") + rect(284, 122, 12, 52, "resin")
    for y in (130, 142, 154, 166):
        s += ell(290, y, 13, 3.5, "resin")
    s += sm(290, 106, "支持碍子")
    s += lab(56, 168, "真空混合・脱泡")
    return s


# ------------------------------------------------------------ 鉄心試験装置（ループ試験）
@picto("coreloop")
def _():
    cx = 124
    s = shadow(cx, 162, 84, 4)
    s += vcyl(cx, 64, 80, 72, 18, "m2", "m")
    for y in range(70, 144, 5):
        s += path("M%s %s A72 18 0 0 0 %s %s" % (n(cx - 72), n(y), n(cx + 72), n(y)), "o thin")
    s += ell(cx, 64, 46, 11, "m3")
    s += rot(cx, 64, 59, 14.5, 205, 335)
    s += lab(cx + 4, 36, "磁束")
    # excitation cable: a few turns through the bore and back outside
    for i, x in enumerate((cx - 22, cx - 8, cx + 6)):
        s += path("M%s 168 L%s 82 Q%s 66 %s 66" % (n(x), n(x), n(x), n(x + 8)), "cable")
    s += path("M%s 168 Q%s 176 70 176 L44 176" % (n(cx - 22), n(cx - 22)), "cable")
    s += path("M%s 168 Q%s 184 70 184 L44 184" % (n(cx + 6), n(cx + 6)), "cable")
    s += box(8, 150, 36, 40, 8, "m2", "m", "m3")
    s += path("M14 170 q4 -8 8 0 q4 8 8 0", "o")
    s += sm(28, 140, "交流電源")
    # hot spot and IR camera
    s += circ(cx - 34, 66, 4, "h") + circ(cx - 34, 66, 8, "flash")
    s += rect(234, 18, 40, 22, "m3", 3) + rect(226, 23, 9, 12, "m2", 2) + rect(250, 40, 6, 12, "m2")
    s += line(226, 26, cx - 30, 60, "ray") + line(226, 33, cx - 26, 72, "ray")
    s += sm(254, 12, "赤外線カメラ") + sm(78, 42, "発熱箇所")
    # inset: burr bridging two laminations, eddy current loop
    s += rect(220, 104, 94, 88, "o thin", 6)
    for j in range(4):
        s += rect(230, 118 + j * 12, 62, 8, "m")
    s += path("M292 130 q5 6 0 12", "h") + circ(294, 136, 3, "h")
    s += path("M240 128 L286 128 L286 144 L240 144Z", "hl dash")
    s += head(286, 138, math.pi / 2, 6)
    s += sm(266, 174, "バリで短絡→渦電流") + sm(266, 186, "→局部発熱")
    return s
