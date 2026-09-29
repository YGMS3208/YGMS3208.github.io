"""Gear-manufacturing equipment pictos (320x200) rebuilt on the involute/3D gear engine.
Imported after il_pictos so these override the older flat drawings."""
import math
from il_pictos import PICTOS, picto, lab, chart, dots
from il_base import rect, circ, ell, line, path, poly, text, arrow, rot, n
import il_gscene as G
from il_gear import Cam, gear_outline, internal_outline, spline_outline, outline_d, rack_pts, PI, ALPHA


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


@picto("hob")
def _():
    s = G.sc_hobbing(128, 104, 0.6, lab=False)
    s += lab(58, 26, "ワーク") + al(268, 190, "ホブ", "middle")
    return s


@picto("ggrind")
def _():
    s = G.sc_gear_grind(128, 100, 0.6, lab=False)
    s += lab(58, 22, "ワーク") + al(262, 194, "ねじ状砥石", "middle")
    return s


@picto("shaper")
def _():
    s = G.sc_shaping(120, 116, 0.62, lab=False)
    s += al(290, 70, "往復", "middle") + lab(236, 18, "ピニオンカッタ", "middle")
    return s


@picto("skive")
def _():
    s = G.sc_skiving(150, 112, 0.6, lab=False)
    s += al(236, 22, "カッタ（軸交差）", "middle") + lab(60, 190, "内歯車", "middle")
    return s


@picto("shave")
def _():
    s = G.sc_shaving(104, 112, 0.6, lab=False)
    s += al(230, 30, "シェービングカッタ", "middle") + lab(56, 186, "ワーク", "middle")
    return s


@picto("ghone")
def _():
    s = G.sc_honing(152, 108, 0.64, lab=False)
    s += al(256, 190, "内歯砥石", "middle")
    return s


@picto("gchamfer")
def _():
    s = G.sc_chamfer(120, 104, 0.62, lab=False)
    s += al(250, 30, "面取り工具", "middle") + lab(70, 190, "歯端のエッジ", "middle")
    return s


@picto("hypcut")
def _():
    s = G.sc_hypoid_cut(136, 118, 0.62, lab=False)
    s += al(236, 20, "カッタヘッド", "middle")
    return s


@picto("hyplap")
def _():
    s = G.sc_hypoid_pair(184, 112, 0.6, lab=False)
    s += dots(96, 96, 34, 26, 6, "grain") + lab(62, 150, "ラップ剤", "middle")
    return s


@picto("gearmesh")
def _():
    s = G.sc_mesh(118, 112, 0.6, lab=False)
    s += chart(226, 14, 88, 50, "noise") + lab(62, 192, "ワーク") + lab(206, 192, "マスタギヤ")
    return s


@picto("gearmeas")
def _():
    s = G.sc_measure(110, 110, 0.6, lab=False)
    s += chart(226, 118, 88, 58, "profile") + lab(270, 194, "歯形・歯すじ")
    return s


@picto("rolling")
def _():
    s = G.sc_spline_roll(160, 100, 0.62, lab=False)
    s += al(160, 194, "ラック（丸）ダイスで歯を押し出す")
    return s


def broach_bar(x0, x1, cy, core, h0, h1, pt=9, cls="t", rows=(1, -1), n_cut=None):
    """side view of a spline broach: saw teeth rising from h0 to h1 along x (pull direction = +x... teeth rake faces at left)."""
    out = ""
    cnt = int((x1 - x0) / pt)
    n_cut = n_cut or int(cnt * 0.7)
    for sg in rows:
        ps = [(x0, cy)]
        for i in range(cnt):
            x = x0 + i * pt
            h = h0 + (h1 - h0) * min(1.0, i / max(1, n_cut))
            y_b = cy - sg * core
            y_t = cy - sg * (core + h)
            ps += [(x, y_b), (x + 0.8, y_t), (x + pt * 0.32, y_t), (x + pt, y_b)]
        ps += [(x0 + cnt * pt, cy)]
        out += poly(ps, cls)
    out += rect(x0, cy - core, cnt * pt, core * 2, cls)
    return out


@picto("broach")
def _():
    s = ""
    # work (sectioned hub) with internal spline being cut
    s += rect(120, 42, 70, 44, "cut") + rect(120, 118, 70, 44, "cut")
    for k in range(8):
        s += line(122 + k * 9, 84, 130 + k * 9, 44, "hatch") + line(122 + k * 9, 160, 130 + k * 9, 120, "hatch")
    s += broach_bar(18, 300, 102, 10, 2, 7, 8)
    s += rect(300, 96, 16, 12, "m3")
    s += arrow(250, 180, 306, 180, None) + al(278, 196, "引き抜き")
    s += lab(155, 34, "ワーク（断面）")
    # end-view inset of internal spline
    cx, cy = 58, 42
    s += circ(cx, cy, 30, "w") + path(outline_d(spline_outline(18, 19, 14, 0.0), cx, cy) , "bg")
    s += lab(58, 86, "内スプライン")
    return s


# ---------------------------------------------------------------- new equipment (EV / diesel / exhaust)
from il_base import box, shaft, vcyl, heat, shadow


@picto("profile")
def _():
    s = rect(14, 150, 292, 14, "m3") + rect(20, 164, 280, 18, "m2")
    s += box(28, 116, 250, 30, 30, "w2", "w", "w3")
    for x in (40, 70, 100):
        s += rect(x, 122, 20, 18, "bg", 2)
    s += rect(150, 20, 60, 26, "m2", 3) + rect(170, 46, 20, 30, "m") + rect(176, 76, 8, 30, "t")
    s += rect(120, 12, 120, 10, "m3")
    s += arrow(40, 196, 280, 196, "コラムが長尺ワーク上を移動", 160, 192, both=True) if False else arrow(60, 40, 130, 40, None, both=True)
    s += lab(95, 32, "移動コラム") + lab(210, 196, "中空の押出形材")
    return s


@picto("autofrettage")
def _():
    s = circ(120, 104, 62, "w") + circ(120, 104, 22, "fl")
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += arrow(120 + 8 * math.cos(a), 104 + 8 * math.sin(a), 120 + 34 * math.cos(a), 104 + 34 * math.sin(a), None)
    s += circ(120, 104, 30, "mfring")
    s += rect(210, 80, 60, 50, "m2", 4) + circ(240, 58, 16, "m") + line(240, 58, 248, 50, "o") + path("M182 104 L210 104", "tube1")
    s += lab(120, 186, "内面に圧縮残留応力") + lab(240, 150, "超高圧ポンプ")
    return s


@picto("canning")
def _():
    s = rect(40, 76, 100, 56, "w2", 4)
    for x in range(46, 136, 8):
        s += line(x, 80, x, 128, "o thin")
    s += rect(36, 72, 108, 64, "mesh", 6)
    s += rect(170, 66, 120, 76, "m", 6) + ell(170, 104, 10, 38, "bg")
    s += arrow(146, 104, 166, 104, None) + rect(8, 90, 28, 28, "m3", 3)
    s += lab(90, 158, "担体＋保持マット") + lab(230, 158, "ステンレス外筒") + text(160, 40, "押し込んで縮径", "middle", "al")
    return s
