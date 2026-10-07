"""Principle drawings (320x200) for heavy-industry equipment: large machining, open-die forging,
large castings, HIP, heavy welding, sheet metal and on-site boring.
Imported after il_pictos; registers into the same PICTOS table."""
import math
from il_base import *
from il_pictos import picto, lab, chips, insert, dots


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def person(x, y, h=26):
    """small single-colour silhouette standing with feet at (x, y): scale cue for very large equipment."""
    k = h / 26.0
    body = [(-5, -19), (5, -19), (4.6, -9), (3.6, 0), (0.9, 0), (0, -8), (-0.9, 0), (-3.6, 0), (-4.6, -9)]
    return circ(x, y - 22.6 * k, 3.3 * k, "m3") + poly([(x + a * k, y + b * k) for a, b in body], "m3")


def hatch_rect(x, y, w, h, step=8):
    """sectioned material: cut fill with 45deg hatch lines clipped to the rectangle."""
    s = rect(x, y, w, h, "cut")
    t = step
    while t < w + h:
        x1, y1 = x + max(0, t - h), y + min(h, t)
        x2, y2 = x + min(w, t), y + max(0, t - w)
        s += line(x1, y1, x2, y2, "hatch")
        t += step
    return s


# ============================================================ large machining
@picto("hvlathe")
def _():
    cy = 94
    s = shadow(166, 170, 150, 5)
    s += rect(20, 146, 294, 14, "m2", 2) + rect(20, 160, 294, 8, "m3")          # long bed
    s += rect(166, 54, 7, 92, "m2")                                               # steady-rest hinge post (behind)
    s += rect(22, 40, 36, 106, "m2", 4)                                           # headstock
    s += rect(58, 44, 12, 100, "m3", 2)                                           # face plate
    s += shaft(72, cy, [(22, 20), (30, 25), (96, 21), (26, 25), (22, 16)], "w", "w2")
    s += rect(70, 64, 9, 12, "m") + rect(70, 112, 9, 12, "m")                    # jaws
    # steady rest: rollers above and below the shaft
    s += rect(140, 54, 33, 12, "m", 2) + circ(153, 69, 4, "m3")
    s += rect(140, 123, 33, 23, "m", 2) + circ(153, 119, 4, "m3")
    # tailstock with live centre
    s += rect(282, 60, 28, 86, "m2", 3) + rect(268, cy - 7, 16, 14, "m") + poly([(262, cy), (270, cy - 6), (270, cy + 6)], "m3")
    # carriage + heavy tool
    s += rect(182, 134, 54, 12, "m2", 2) + rect(196, 124, 24, 10, "m3") + insert(206, 116, 8, -95)
    s += chips(212, 114, 1.3)
    s += rot(108, cy, 9, 32, -70, 70, "回転", 108, 52)
    s += line(72, 30, 268, 30, "o thin") + line(72, 25, 72, 35, "o thin") + line(268, 25, 268, 35, "o thin")
    s += lab(170, 24, "長さ 数m〜十数m")
    s += lab(153, 48, "振れ止め") + lab(296, 54, "心押台") + lab(40, 186, "主軸台")
    s += arrow(262, 182, 206, 182, "送り", 234, 196)
    s += person(9, 168, 26)
    return s


@picto("hbm")
def _():
    cy = 88
    s = shadow(166, 172, 150, 5)
    s += rect(8, 160, 304, 10, "m3", 2)                                           # floor plate
    s += rect(22, 16, 46, 144, "m2", 3) + rect(62, 20, 4, 136, "m")             # column + way
    s += rect(56, 66, 58, 44, "m3", 4)                                           # headstock
    s += shaft(114, cy, [(22, 10)], "m", "m2")                                   # quill sleeve
    # work: large box casting on a rotary table, cut open along the bore
    s += rect(176, 148, 128, 12, "m2", 2)
    s += box(180, 60, 104, 88, 26, "w2", "w", "w3")
    s += rect(180, cy - 11, 104, 22, "bg")
    s += shaft(136, cy, [(126, 5)], "t", "t")                                    # long boring bar
    s += rect(250, cy - 5, 10, 10, "m") + insert(255, cy - 10, 5, -90)
    s += chips(246, cy - 12, -0.8)
    s += rot(126, cy, 6, 15, -70, 70)
    s += arrow(122, 106, 172, 106, None) + al(147, 124, "突き出し")
    s += arrow(92, 24, 92, 60, None, both=True) + lab(100, 46, "上下", "start")
    s += rot(240, 154, 70, 12, 25, 155) + lab(240, 190, "回転テーブル")
    s += lab(45, 186, "コラム") + lab(240, 40, "大型の箱物（断面）")
    s += person(306, 160, 24)
    return s


# ============================================================ forging / casting
@picto("openforge")
def _():
    s = shadow(160, 180, 130, 5)
    s += rect(56, 160, 208, 20, "m2", 3)                                          # base
    s += rect(84, 30, 12, 130, "m") + rect(224, 30, 12, 130, "m")               # columns
    s += rect(60, 16, 200, 24, "m3", 4)                                           # top crosshead
    s += rect(136, 40, 48, 16, "m2") + rect(150, 56, 20, 8, "m")                # cylinder + plunger
    s += rect(92, 62, 136, 18, "m2", 2)                                          # moving crosshead
    s += rect(128, 80, 64, 14, "t") + rect(128, 140, 64, 20, "t")               # flat dies
    # hot ingot: thick where not yet forged, squeezed under the die
    s += path("M56 84 L118 84 Q126 84 128 94 L256 94 Q266 94 266 102 L266 132 Q266 140 256 140 L128 140"
              " Q126 150 118 150 L56 150 Q48 150 48 142 L48 92 Q48 84 56 84Z", "h")
    s += heat(242, 90, 3, 8)
    # manipulator gripping the ingot
    s += rect(2, 100, 30, 48, "m3", 4) + circ(10, 152, 6, "m2") + circ(26, 152, 6, "m2")
    s += path("M30 116 L52 90", "arm2") + path("M30 132 L52 144", "arm2")
    s += rot(98, 117, 9, 40, -60, 60)
    s += arrow(278, 24, 278, 64, None) + al(284, 48, "加圧", "start")
    s += lab(4, 194, "マニプレータ", "start") + lab(170, 196, "平らな金敷で延ばす")
    s += person(296, 180, 26)
    return s


@picto("nobake")
def _():
    s = shadow(186, 176, 124, 5)
    # continuous mixer: pillar + swinging trough arm
    s += rect(20, 34, 16, 136, "m2") + rect(12, 166, 32, 8, "m3", 2)
    s += rect(14, 24, 186, 16, "m2", 4)
    s += path("M24 32 " + " ".join("L%d %d" % (30 + 8 * i, 28 if i % 2 else 36) for i in range(20)), "o thin")
    s += poly([(184, 40), (200, 40), (196, 52), (188, 52)], "m3")
    s += poly([(188, 52), (196, 52), (200, 88), (184, 88)], "sand") + dots(186, 56, 12, 30, 6, "grain")
    # flask (cut open) packed with resin sand around a large pattern
    s += rect(86, 96, 214, 76, "m3", 2)
    s += rect(94, 100, 198, 68, "sand") + dots(96, 102, 194, 64, 11, "grain")
    s += path("M136 100 Q192 78 246 100Z", "sand")
    s += path("M118 168 L118 140 L148 140 L156 122 L232 122 L240 140 L270 140 L270 168Z", "t")
    s += lab(104, 16, "連続混練機（砂＋樹脂＋硬化剤）")
    s += lab(193, 192, "鋳枠の中で模型のまわりに詰めて自然に硬化")
    s += person(62, 172, 26)
    return s


@picto("centrifugal")
def _():
    cy = 104
    s = shadow(160, 172, 130, 5)
    s += rect(56, 152, 210, 18, "m2", 3) + rect(266, 140, 32, 30, "m3", 3) + path("M266 150 L240 150", "belt")
    # rotating mould, cut open: wall / cast layer / hollow bore
    s += rect(60, 70, 196, 68, "m2")
    s += rect(60, 80, 196, 48, "h") + rect(60, 90, 196, 28, "bg")
    s += rect(54, 66, 8, 76, "m3", 2) + rect(254, 66, 8, 76, "m3", 2)
    for x in (92, 228):
        s += circ(x, 149, 11, "m3") + circ(x, 149, 3.5, "m")
    # ladle and pouring trough reaching into the bore
    s += '<g transform="rotate(28 30 48)">' + path("M8 30 L52 30 L46 66 L14 66Z", "m2") + rect(14, 34, 34, 14, "h") + "</g>"
    s += path("M46 50 Q50 62 44 74", "pour")
    s += path("M36 72 L132 100 L132 106 L34 78Z", "m3") + path("M44 76 L128 101", "pour")
    s += rot(200, cy, 10, 40, -60, 60) + al(200, 58, "高速回転")
    # end view: centrifugal force throws the metal against the wall
    ex, ey = 284, 36
    s += circ(ex, ey, 24, "m2") + circ(ex, ey, 19, "h") + circ(ex, ey, 13, "bg")
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        s += arrow(ex + 3 * math.cos(a), ey + 3 * math.sin(a), ex + 15 * math.cos(a), ey + 15 * math.sin(a), None)
    s += lab(284, 76, "遠心力") + lab(160, 192, "回転する金型の内面に固まる")
    return s


@picto("dsfurnace")
def _():
    s = shadow(86, 186, 74, 5)
    s += rect(14, 10, 144, 170, "m2", 10) + rect(22, 18, 128, 154, "bg", 6)      # vacuum vessel
    # heater zone (top), baffle, cooling zone (bottom)
    s += rect(30, 24, 112, 82, "warmin") + rect(30, 24, 12, 82, "h") + rect(130, 24, 12, 82, "h") + rect(30, 24, 112, 8, "h")
    s += rect(24, 106, 52, 6, "m3") + rect(96, 106, 52, 6, "m3")
    # ceramic mould shell with blade: molten above the baffle, solid (columnar) below
    s += poly([(74, 128), (98, 128), (98, 94), (104, 92), (100, 40), (72, 40), (68, 92), (74, 94)], "shell")
    s += poly([(77, 92), (95, 92), (98, 44), (74, 44)], "h")
    s += rect(72, 92, 28, 4, "h")
    s += rect(78, 98, 16, 10, "h") + rect(78, 108, 16, 8, "w")
    for x in (81, 85, 89):
        s += line(x, 109, x, 116, "o thin")
    s += path("M86 126 c-6 -2 -6 -6 0 -6 c6 0 6 -4 0 -4", "wire2")
    s += rect(60, 128, 52, 8, "m3") + line(64, 132, 108, 132, "fo")
    s += rect(78, 136, 16, 50, "m")
    s += arrow(118, 140, 118, 168, None)
    s += lab(164, 64, "加熱帯", "start") + lab(164, 136, "水冷板", "start") + al(164, 166, "引き抜き", "start")
    # inset: grain structures
    for i, (cx, kind, name) in enumerate(((222, 0, "普通"), (258, 1, "一方向"), (294, 2, "単結晶"))):
        s += poly([(cx - 9, 70), (cx + 9, 70), (cx + 7, 22), (cx - 6, 20)], "w") + rect(cx - 12, 70, 24, 10, "w2")
        if kind == 0:
            for (a, b, c, d) in ((-8, 36, 6, 30), (-7, 50, 7, 46), (-6, 62, 8, 58), (-2, 22, 0, 70), (3, 24, 4, 52)):
                s += line(cx + a, b, cx + c, d, "o thin")
        elif kind == 1:
            for dx in (-4, 0, 4):
                s += line(cx + dx, 22, cx + dx, 70, "o thin")
        s += text(cx, 94, name, "middle", "sm")
    return s


@picto("hip")
def _():
    s = shadow(93, 184, 70, 5)
    s += rect(36, 40, 114, 118, "m2") + rect(30, 22, 126, 18, "m3", 3) + rect(30, 158, 126, 18, "m3", 3)
    s += rect(48, 40, 90, 118, "bg") + rect(48, 40, 90, 118, "warmin")
    for x in (54, 132):
        s += path("M%d 46 " % x + " ".join("L%d %d" % (x + (3 if i % 2 else -3), 52 + 6 * i) for i in range(17)), "hl")
    # casting with internal pores on a rack
    s += rect(66, 136, 54, 6, "m") + path("M74 136 L74 112 L68 112 L68 96 L80 84 L106 84 L118 96 L118 112 L112 112 L112 136Z", "w")
    for (x, y) in ((84, 100), (100, 110), (90, 122), (104, 94)):
        s += circ(x, y, 2.2, "bg")
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += arrow(93 + 40 * math.cos(a), 108 + 40 * math.sin(a), 93 + 28 * math.cos(a), 108 + 28 * math.sin(a), None)
    # gas supply
    s += path("M150 150 L190 150", "pipe") + rect(190, 132, 40, 34, "m3", 3) + path("M230 150 L254 150", "pipe")
    s += vcyl(266, 126, 40, 11, 4, "m", "m2")
    s += lab(210, 182, "圧縮機") + lab(266, 182, "Arガス")
    # inset: pores closed
    s += rect(180, 22, 44, 40, "w") + rect(254, 22, 44, 40, "w")
    for (x, y) in ((190, 32), (206, 40), (196, 52), (214, 30), (214, 54)):
        s += circ(x, y, 2.4, "bg")
    s += arrow(228, 42, 250, 42, None)
    s += lab(202, 78, "空隙") + lab(276, 78, "緻密")
    s += lab(93, 16, "高圧容器") + lab(238, 98, "高温・高圧ガスで")
    s += lab(238, 112, "四方から均一に加圧")
    return s


# ============================================================ welding / sheet metal
@picto("subarc")
def _():
    s = shadow(160, 178, 150, 5)
    s += box(10, 136, 290, 30, 16, "w2", "w", "w3")                               # thick plate
    # flux hopper -> flux heap covering the joint; head with contact tip; wire spool
    s += rect(132, 6, 184, 10, "m3", 2)
    s += poly([(70, 30), (112, 30), (98, 58), (84, 58)], "m2") + path("M91 58 L122 116", "pipe")
    s += path("M96 133 Q110 121 132 119 L192 119 Q208 121 216 133Z", "sand") + dots(104, 122, 108, 10, 6, "grain")
    s += rect(150, 16, 6, 18, "m2") + rect(144, 34, 40, 26, "m3", 3) + rect(158, 60, 12, 40, "m")
    s += poly([(158, 100), (170, 100), (167, 114), (161, 114)], "cu") + line(164, 114, 164, 122, "wire2")
    s += ell(166, 130, 9, 3, "flash")
    s += line(232, 16, 232, 22, "o") + circ(232, 40, 18, "m2") + circ(232, 40, 12, "cu") + circ(232, 40, 4, "m3")
    s += path("M214 42 Q198 44 184 44", "wire2")
    # slag crust then exposed bead behind the head
    s += path("M216 133 Q226 125 240 125 L262 125 Q268 127 272 133Z", "rb")
    s += path("M272 132 Q288 124 304 131", "bead")
    s += lab(91, 24, "フラックス") + lab(232, 74, "ワイヤ") + lab(242, 116, "スラグ") + lab(290, 116, "ビード")
    # inset: thick plates with a V groove filled in layers
    s += poly([(8, 62), (30, 62), (38, 84), (38, 88), (8, 88)], "w") + poly([(70, 62), (48, 62), (42, 84), (42, 88), (70, 88)], "w")
    s += poly([(30, 62), (48, 62), (42, 86), (38, 86)], "w3") + path("M28 62 Q39 55 50 62", "w3")
    s += line(33, 70, 45, 70, "o thin") + line(35, 78, 44, 78, "o thin")
    s += lab(39, 104, "厚板の開先")
    s += arrow(140, 184, 64, 184, None) + al(102, 198, "溶接方向")
    s += lab(236, 196, "アークはフラックスの下")
    return s


@picto("pressbrake")
def _():
    s = shadow(200, 188, 110, 4)
    s += path("M100 14 L300 14 L300 186 L100 186 L100 150 L246 150 L246 58 L100 58Z", "m2")      # C-shaped side frame
    s += rect(112, 2, 28, 14, "m") + rect(106, 52, 40, 30, "m3", 2) + rect(116, 82, 20, 8, "m")
    s += poly([(116, 90), (136, 90), (126, 115)], "t")                                           # punch
    s += rect(106, 132, 40, 54, "m3") + rect(104, 116, 44, 16, "t") + poly([(116, 116), (136, 116), (126, 128)], "bg")
    s += rect(222, 96, 8, 26, "m") + rect(228, 108, 18, 6, "m3")                                   # back gauge
    s += path("M30 77 L116 115 L126 120 L136 115 L222 77", "sheet")                                # sheet being bent
    s += arrow(90, 18, 90, 50, None) + al(84, 38, "加圧", "end")
    s += lab(150, 76, "パンチ", "start") + lab(100, 128, "ダイ", "end") + lab(196, 142, "突当て")
    # product: bent enclosure panel
    s += poly([(14, 178), (70, 178), (86, 168), (30, 168)], "sheet2")
    s += poly([(14, 178), (30, 168), (30, 148), (14, 158)], "w3") + poly([(70, 178), (86, 168), (86, 148), (70, 158)], "w")
    s += lab(50, 196, "筐体パネル")
    return s


@picto("busbar")
def _():
    s = shadow(160, 180, 146, 5)
    s += rect(22, 142, 276, 34, "m3", 3) + rect(14, 128, 292, 14, "m2", 2)
    for cx, name in ((70, "穴あけ"), (150, "切断"), (236, "曲げ")):
        s += rect(cx - 30, 44, 10, 84, "m2") + rect(cx - 30, 40, 58, 22, "m3", 3) + rect(cx - 14, 112, 28, 16, "m")
        s += lab(cx, 32, name) + arrow(cx + 20, 66, cx + 20, 94, None)
    s += rect(66, 62, 8, 36, "t")                                                                   # punch
    s += poly([(138, 62), (160, 62), (160, 92), (138, 99)], "t")                                    # shear blade
    s += poly([(226, 62), (246, 62), (246, 82), (236, 97), (226, 82)], "t") + poly([(228, 112), (244, 112), (236, 122)], "bg")
    # copper bar: punched holes, sheared end; bent piece in the third station
    s += poly([(10, 104), (150, 104), (155, 100), (15, 100)], "cu") + rect(10, 104, 140, 8, "cu")
    for x in (28, 46):
        s += ell(x, 102, 3.4, 1.4, "bg")
    s += path("M206 102 L236 116 L266 102", "cuwire2")
    s += arrow(12, 88, 48, 88, None) + al(30, 82, "送り")
    s += lab(160, 196, "銅・アルミの帯板（ブスバー）を加工")
    return s


@picto("plasma")
def _():
    s = shadow(160, 178, 150, 5)
    s += rect(8, 168, 304, 6, "m3")                                                                # rails
    s += rect(40, 134, 240, 34, "m2", 2)                                                          # scrap tank
    for x in range(48, 276, 12):
        s += rect(x, 122, 4, 12, "m3")                                                            # grate slats
    s += box(46, 110, 228, 12, 14, "w2", "w", "w3")                                               # plate
    s += path("M64 106 L150 106", "kerf") + ell(106, 106, 18, 3.6, "o") + ell(106, 106, 18, 3.6, "kerf")
    s += rect(18, 30, 16, 138, "m2") + rect(286, 30, 16, 138, "m2") + rect(10, 18, 300, 16, "m3", 3)
    s += rect(146, 34, 28, 22, "m2", 2) + rect(154, 56, 12, 32, "m") + poly([(154, 88), (166, 88), (162, 98), (158, 98)], "cu")
    s += line(160, 98, 160, 108, "jet2") + sparks(160, 124, 16, 7, 60, 120)
    s += arrow(76, 46, 136, 46, None, both=True) + lab(106, 62, "トーチ移動")
    s += lab(150, 80, "トーチ", "end")
    # inset: bevel cut with a tilted torch
    s += rect(194, 38, 86, 62, "tbg", 4) + rect(194, 38, 86, 62, "o thin", 4)
    s += poly([(200, 68), (231, 68), (245, 94), (200, 94)], "cut") + poly([(274, 68), (239, 68), (253, 94), (274, 94)], "cut")
    s += '<g transform="rotate(-28.6 233 64.5)">' + rect(228, 36, 10, 24, "m") + poly([(228, 60), (238, 60), (235, 64.5), (231, 64.5)], "cu") + "</g>"
    s += line(234, 66, 247, 90, "jet2")
    s += lab(246, 54, "開先", "start")
    s += lab(160, 192, "格子の定盤（切断くずを受ける）")
    return s


@picto("rollbend")
def _():
    s = shadow(160, 178, 90, 5)
    s += rect(92, 150, 136, 26, "m3", 3)
    s += path("M14 117 L100 117 Q122 117 138 124.6 A104 104 0 0 0 258 59", "sheet")
    s += circ(160, 104, 20, "m2") + circ(160, 104, 6, "m3")
    for x in (120, 200):
        s += circ(x, 138, 16, "m") + circ(x, 138, 5, "m3")
    s += rot(160, 104, 27, 27, 200, 250) + rot(120, 138, 22, 22, 20, 70) + rot(200, 138, 22, 22, 20, 70)
    s += arrow(160, 54, 160, 78, None) + al(168, 68, "押込み", "start")
    s += arrow(24, 104, 74, 104, None) + al(49, 98, "送り")
    # rolled shell: seam still open
    s += shaft(14, 40, [(60, 22)], "w", "w2") + ell(74, 40, 4.5, 14, "bg")
    s += poly([(70, 17), (78, 17), (78, 25), (70, 25)], "bg") + line(14, 20, 74, 20, "o")
    s += lab(8, 80, "巻いた円筒", "start")
    s += lab(160, 194, "ロールの間で板を往復させて曲げる")
    return s


@picto("turretpunch")
def _():
    s = shadow(124, 176, 90, 5)
    # lower turret (dies) under the sheet
    s += vcyl(124, 134, 12, 74, 18, "m2", "m")
    s += ell(124, 148, 7, 2.6, "t")
    # sheet moved in X/Y by clamps
    s += poly([(20, 118), (232, 118), (300, 84), (88, 84)], "sheet2")
    s += poly([(20, 118), (232, 118), (232, 121), (20, 121)], "w3") + poly([(232, 118), (300, 84), (300, 87), (232, 121)], "w3")
    for i in range(4):
        for j in range(3):
            u, v = 0.58 + 0.09 * i, 0.25 + 0.25 * j
            x, y = 20 + 212 * u + 68 * v, 118 - 34 * v
            if j == 0:
                s += ell(x, y, 3.6, 1.6, "bg")
            elif j == 1:
                s += poly([(x - 3, y + 1.5), (x + 3, y + 1.5), (x + 5, y - 1.5), (x - 1, y - 1.5)], "bg")
            else:
                s += path("M%s %s q4 -4 8 0" % (n(x - 4), n(y + 1)), "o")
    for x in (44, 84):
        s += rect(x - 6, 114, 12, 10, "m3", 2)
    s += rect(30, 122, 70, 5, "m3")
    # upper turret (punches) + striker
    s += vcyl(124, 40, 12, 74, 18, "m2", "m")
    for k in range(10):
        a = 2 * math.pi * k / 10 + math.pi / 2
        x, y = 124 + 56 * math.cos(a), 40 + 13.5 * math.sin(a)
        if k == 0:
            continue
        s += ell(x, y, 5, 2.2, "t") if k % 2 else poly([(x - 4, y + 2), (x + 4, y + 2), (x + 5, y - 2), (x - 3, y - 2)], "t")
    s += rect(118, 2, 190, 14, "m3", 3) + rect(118, 16, 12, 36, "m3") + rect(120, 52, 8, 50, "t") + ell(124, 104, 4, 1.8, "bg")
    s += arrow(104, 2, 104, 20, None) + al(98, 14, "打抜き", "end")
    s += lab(46, 44, "タレット", "end")
    s += arrow(14, 160, 58, 160, None, both=True) + arrow(16, 182, 40, 170, None, both=True) + lab(48, 186, "XY", "start")
    # inset: punched sheet close-up
    s += rect(222, 128, 90, 58, "sheet2", 3)
    for i in range(4):
        s += circ(236 + 20 * i, 140, 4, "bg") + rect(232 + 20 * i, 152, 8, 8, "bg")
        s += path("M%d 176 Q%d 166 %d 176Z" % (229 + 20 * i, 236 + 20 * i, 243 + 20 * i), "w3")
    s += text(267, 198, "丸穴・角穴・ルーバ", "middle", "sm")
    return s


# ============================================================ on-site machining
@picto("portbore")
def _():
    cy = 104
    s = ""
    for x in (76, 196):                                                                           # two bosses of a structure, sectioned
        s += hatch_rect(x, 50, 46, 41) + hatch_rect(x, 117, 46, 41) + rect(x, 91, 46, 26, "bg")
    s += path("M76 50 Q160 36 242 50", "o") + path("M76 158 Q160 172 242 158", "o")
    s += rect(58, 84, 18, 40, "m2", 2) + rect(242, 84, 18, 40, "m2", 2)                           # bearing supports bolted on
    for x in (67, 251):
        s += circ(x, 89, 2.2, "m3") + circ(x, 119, 2.2, "m3")
    s += rect(4, 86, 36, 36, "m3", 3) + rect(40, 96, 14, 16, "m")                                 # rotation + feed drive
    s += shaft(46, cy, [(246, 6)], "t", "t")                                                      # long boring bar
    s += rect(212, 97, 12, 14, "m") + insert(218, 92, 5, -90)                                     # tool holder + bit
    s += line(20, cy, 312, cy, "laserl") + rect(300, 98, 14, 12, "m3", 2)
    s += rot(134, cy, 6, 15, -70, 70)
    s += arrow(136, 132, 186, 132, None) + al(161, 148, "送り")
    s += lab(166, 82, "中ぐり棒") + lab(4, 78, "駆動・送り", "start") + lab(276, 140, "軸受台")
    s += lab(160, 26, "船尾の骨材の穴（断面）") + lab(160, 192, "軸心はレーザで合わせる")
    return s
