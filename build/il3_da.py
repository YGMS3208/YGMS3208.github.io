"""v3 shaded-3D detail + process drawings (480x300) for engine.block, engine.head, engine.cam.
Replaces the flat drawings of il_d_block / il_d_engine (same ops, titles, notes and tolerances)."""
import math
import re
import il_gear as GE
from il_base import *
from il_detail import *
from il_dmap import dpart
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, arc3, arrow3
from il3_lib import P as P3, PI
import il3_engine as EN
import il_d_block as OB
import il_d_engine as OE

bore, row_union, poly3, shcls, sclip = EN.bore, EN.row_union, EN.poly3, EN.shcls, EN.clip


# =====================================================================================
# small helpers
# =====================================================================================
def hclip(pts, xc):
    """2D polygon [(x, y)] clipped to x >= xc."""
    def ix(a, b):
        t = (xc - a[0]) / (b[0] - a[0])
        return (xc, a[1] + t * (b[1] - a[1]))
    out = []
    for i in range(len(pts)):
        a, b = pts[i - 1], pts[i]
        if b[0] >= xc:
            if a[0] < xc:
                out.append(ix(a, b))
            out.append(b)
        elif a[0] >= xc:
            out.append(ix(a, b))
    return out


def pg(cam, pts3, c):
    return path(P3([cam.xy(p) for p in pts3]), c)


def cpoly(pts2, clipper, c):
    q = sclip(pts2, clipper)
    return path(P3(q), c) if len(q) > 2 else ""


def drill(sc, tip, A, r, L, mat="t", bias=0.0, cone=1.1):
    """twist-drill-like tool: cone at tip, body along A (unit, pointing from tip to shank)."""
    b = tuple(tip[i] + A[i] * r * cone for i in range(3))
    CYL(sc, b, tuple(-a for a in A), r, r * cone, mat, bias, seg=16, r1=r * .12, bands=6)
    CYL(sc, b, A, r, L, mat, bias, seg=16, bands=6)


def spindle(sc, O, A, r, L, bias=0.0):
    CYL(sc, O, A, r, L, "m", bias, seg=24, bands=8)


def fmill(sc, C, r, h=14, sp=60, bias=0.0):
    """face mill: cutter body (tool steel) under C+h, spindle nose above."""
    CYL(sc, C, (0, 0, 1), r, h, "t", bias, seg=36, bands=10)
    CYL(sc, (C[0], C[1], C[2] + h), (0, 0, 1), r * .55, sp, "m", bias, seg=24, bands=8)


def gmat(svg, cam, xc, o, k, u0, v0, flip_u=True):
    """map a flat 2D drawing (local u right, v down) onto the 3D plane x = xc:
    u -> y = (u0 - u) * k (or (u - u0) * k), v -> z = (v0 - v) * k. Strokes keep their width."""
    su = -1 if flip_u else 1
    p0 = cam.xy((xc, su * (0 - u0) * k, (v0 - 0) * k))
    pu = cam.xy((xc, su * (1 - u0) * k, (v0 - 0) * k))
    pv = cam.xy((xc, su * (0 - u0) * k, (v0 - 1) * k))
    a, b, c, d = pu[0] - p0[0], pu[1] - p0[1], pv[0] - p0[0], pv[1] - p0[1]
    svg = svg.replace("<path ", '<path vector-effect="non-scaling-stroke" ')
    svg = re.sub(r'([ML])(-?[\d.]+) (-?[\d.]+)', r'\1\2,\3', svg)   # keep local coords out of fit()'s extent scan
    return '<g transform="matrix(%s %s %s %s %s %s)">%s</g>' % (round(a, 4), round(b, 4), round(c, 4), round(d, 4), n(p0[0]), n(p0[1]), svg)


_DML = re.compile(r' d="([MLZ0-9. \-]+)"')
_TOK = re.compile(r'([MLZ])|(-?\d+(?:\.\d+)?)')


def rel(svg):
    """absolute M/L paths -> relative m/l (smaller output; same drawing)."""
    def one(m):
        toks = [c if c else float(v) for c, v in _TOK.findall(m.group(1))]
        out, cmd, cur, start, k, last = "", None, (0.0, 0.0), (0.0, 0.0), 0, None

        def f(v):
            t = ("%.1f" % v).rstrip("0").rstrip(".")
            return "0" if t in ("-0", "") else t
        while k < len(toks):
            t = toks[k]
            if t == "Z":
                out += "z"
                cur, last = start, "z"
                k += 1
                continue
            if isinstance(t, str):
                cmd = t
                k += 1
                continue
            x, y = round(toks[k], 1), round(toks[k + 1], 1)
            k += 2
            a, b = f(x - cur[0]), f(y - cur[1])
            if cmd == "M":
                out += "m" + a + (" " if not b.startswith("-") else "") + b
                start = (x, y)
                cmd = "L"
                last = "m"
            else:
                if last == "m":
                    out += "l"
                elif last == "n":
                    out += " " if not a.startswith("-") else ""
                out += a + (" " if not b.startswith("-") else "") + b
                last = "n"
            cur = (x, y)
        return ' d="%s"' % out
    return _DML.sub(one, svg)


def lab(x, y, t, a="middle", c="al"):
    return text(x, y, t, a, c)


# =====================================================================================
# engine.block — inline-4 aluminium block (same proportions as il3_engine.block)
#   x along the crank (0..380), y across (-y = front, intake side), z up (pan rail 0, deck 230)
# =====================================================================================
LB, WU, ZT, RB, ZC = 380, 80, 230, 40, 62
BX = [58, 146, 234, 322]
BK = [14, 102, 190, 278, 366]
SEC_AL = [(43.5, 230), (80, 230), (80, 100), (112, 10), (124, 10), (124, 0), (100, 0), (100, 10), (70, 100), (70, 115), (43.5, 115)]
CAV = [(-100, 0), (100, 0), (100, 10), (70, 100), (70, 115), (-70, 115), (-70, 100), (-100, 10)]
GAL = (-64, 122)


def blk(sc, xc=0, mat="w", cast=False, holes=True, liner=True, sec="cut", over=None, lite=False):
    """block solid from x = xc to LB. xc > 0: cut through bore 1 (section face drawn at x = xc)."""
    x0 = xc
    cut = xc > 0
    dk = 0 if mat == "h" else 1
    BOX(sc, x0 - (0 if cut else 4), -124, 0, LB + 4 - x0 + (0 if cut else 4), 248, 10, mat, dark=dk)
    X(sc, x0, LB - x0, [(-112, 10), (112, 10), (WU, 100), (-WU, 100)], mat, dark=dk)
    BOX(sc, x0, -WU, 100, LB - x0, 2 * WU, ZT - 100, mat, ch=0 if cut else 5)
    for x in (BK if not lite else ()):
        if x - 5 >= x0:
            X(sc, x - 5, 10, [(-112, 10), (-121, 10), (-121, 24), (-85, 100), (-WU, 100)], mat, -1, dark=dk)
    CYL(sc, (300, -WU, 160), (0, -1, 0), 26, 8, mat, -1, seg=28)
    CYL(sc, (300, -WU - 8, 160), (0, -1, 0), 20, 3, mat, -1, seg=28)
    if not cut:
        BOX(sc, 40, -WU - 10, 120, 50, 10, 40, mat, -1, ch=3)
    hot = mat == "h"

    def deck(s_):
        cam = s_.cam
        z = ZT + .05

        def P2(pts):
            q = hclip(pts, xc) if cut else pts
            return poly3(cam, [(x, y, z) for x, y in q], "") if False else [(x, y, z) for x, y in q]
        if lite:
            o = poly3(cam, P2(row_union(BX, 50, 0, 10)), "bg")
            for x in BX:
                o += poly3(cam, [(x + RB * math.cos(2 * PI * k / 16), RB * math.sin(2 * PI * k / 16), z) for k in range(16)], "hs3" if hot else "ms3")
            return o
        o = poly3(cam, P2(row_union(BX, 55, 0, 14)), "bg")
        o += poly3(cam, P2(row_union(BX, 46, 0, 14)), mat if not hot else "hs1")
        for x in BX:
            ring = [(x + 43.5 * math.cos(2 * PI * k / 24), 43.5 * math.sin(2 * PI * k / 24)) for k in range(24)]
            if liner:
                o += poly3(cam, P2(ring), "hs2" if hot else "ms1")
            if cut and x <= xc + 1:
                inner = [(x + RB * math.cos(2 * PI * k / 28), RB * math.sin(2 * PI * k / 28)) for k in range(28)]
                o += poly3(cam, P2(inner), "hs3" if hot else "ms3")
            else:
                o += bore(cam, (x, 0, z), (0, 0, 1), RB, 60, "hs3" if hot else "ms3", 24, ("hs4",) if hot else ("bg",))
        if holes:
            for x in BK:
                if x - 6 >= xc:
                    for y in (-66, 66):
                        o += hole3(cam, (x, y, z), (0, 0, 1), 5.5, "w3", 12) + hole3(cam, (x, y, z), (0, 0, 1), 4, "bg", 10)
            for x, y in ((20, 40), (370, -40), (190, 52), (102, -52), (278, -52)):
                if x - 4 >= xc:
                    o += hole3(cam, (x, y, z), (0, 0, 1), 3.2, "bg", 8)
        return o + (over(s_) if over else "")
    RAW(sc, deck, ((x0, -WU, ZT), (LB, WU, ZT + .1)), -3)
    if not cut and holes:
        def end(s_):
            cam = s_.cam
            x = -.1
            o = hole3(cam, (x, 0, ZC), (-1, 0, 0), 34, "w3") + hole3(cam, (x, 0, ZC), (-1, 0, 0), 28)
            for y, z in ((-60, 30), (60, 30), (-70, 120), (70, 120), (-62, 200), (62, 200), (0, 150), (-30, 205), (30, 205)):
                o += hole3(cam, (x, y, z), (-1, 0, 0), 3.4, "bg", 8)
            return o
        RAW(sc, end, ((-.2, -112, 0), (0, 112, ZT)), -2)
    if holes:
        def side(s_):
            cam = s_.cam
            y = -WU - 11.05
            return hole3(cam, (300, y, 160), (0, -1, 0), 8, "w3") + hole3(cam, (300, y, 160), (0, -1, 0), 5)
        RAW(sc, side, ((280, -WU - 11.2, 140), (320, -WU - 11.1, 180)), -3)
    if cut:
        RAW(sc, lambda s_: bsec(s_.cam, xc, hot, liner), ((xc - .3, -124, 0), (xc - .2, 124, ZT)), -3)


def bsec(cam, xc, hot=False, liner=True, xb=None):
    """section face of the block at x = xc (through a bore centre), seen from -x."""
    xb = xb or xc + 44
    S = lambda y, z, x=xc: cam.xy((x, y, z))
    cav = [S(y, z) for y, z in CAV]
    o = path(P3(cav), "hs4" if hot else "ws3")
    # bulkhead behind the plane, with the crank bore
    fc = "hs2" if hot else shcls("w", (-1, 0, 0))
    o += cpoly([S(y, z, xb) for y, z in CAV], cav, fc)
    o += cpoly([S(28 * math.cos(2 * PI * k / 24), ZC + 28 * math.sin(2 * PI * k / 24), xb) for k in range(24)], cav, "hs4" if hot else "bg")
    o += path(P3([S(-70, ZC, xb), S(-28, ZC, xb)], False) + P3([S(28, ZC, xb), S(70, ZC, xb)], False), "el")
    # bore back wall (liner inside)
    m = "hs" if hot else "ms"
    o += path(P3([S(-RB, 108), S(RB, 108), S(RB, ZT), S(-RB, ZT)]), m + "2")
    o += path(P3([S(26, 108), S(RB, 108), S(RB, ZT), S(26, ZT)]), m + "1")
    o += path(P3([S(-RB, 108), S(-30, 108), S(-30, ZT), S(-RB, ZT)]), m + "3")
    c = "h" if hot else "cut"
    for sg in (1, -1):
        o += path(P3([S(sg * y, z) for y, z in (SEC_AL if sg > 0 else SEC_AL[::-1])]), c)
        o += path(P3([S(sg * 46, 150), S(sg * 55, 150), S(sg * 55, ZT), S(sg * 46, ZT)]), "void")
        if liner:
            o += path(P3([S(sg * 40, 108), S(sg * 43.5, 108), S(sg * 43.5, ZT), S(sg * 40, ZT)]), "hs2" if hot else "ms1")
    o += path(P3([S(GAL[0] + 5 * math.cos(2 * PI * k / 14), GAL[1] + 5 * math.sin(2 * PI * k / 14)) for k in range(14)]), "void")
    return o


def bfeat(cam, xc, name):
    """machined-surface highlight paths (class mf) on the section / solid."""
    S = lambda y, z, x=xc: cam.xy((x, y, z))
    if name == "bore":
        return path(P3([S(-RB, 112), S(-RB, ZT - 2)], False) + P3([S(RB, 112), S(RB, ZT - 2)], False), "mf")
    if name == "gallery":
        return path(P3([S(GAL[0] + 5 * math.cos(2 * PI * k / 14), GAL[1] + 5 * math.sin(2 * PI * k / 14)) for k in range(14)]), "mf")
    if name == "deck":
        return path(P3([cam.xy(p) for p in ((xc + 2, -WU, ZT), (LB - 3, -WU, ZT), (LB, -WU + 3, ZT))], False), "mf")
    return ""


def blk_pan(sc, caps=False, bar=False):
    """block upside down (pan face up) for datum machining / line boring. Interior seen through the pan opening."""
    H = ZT
    f = lambda pts: [(y, H - z) for y, z in pts][::-1]
    BOX(sc, -4, -124, H - 10, LB + 8, 248, 10, "w")
    X(sc, 0, LB, f([(-112, 10), (112, 10), (WU, 100), (-WU, 100)]), "w", dark=1)
    BOX(sc, 0, -WU, 0, LB, 2 * WU, 130, "w", ch=5, dark=1)
    for x in BK:
        X(sc, x - 5, 10, f([(-112, 10), (-121, 10), (-121, 24), (-85, 100), (-WU, 100)]), "w", -1, dark=1)
    zc = H - ZC

    def inside(s_):
        cam = s_.cam
        z = H + .05
        op = [cam.xy(p) for p in ((8, -100, z), (LB - 8, -100, z), (LB - 8, 100, z), (8, 100, z))]
        o = path(P3(op), "bg")
        o += path(P3([cam.xy(p) for p in ((8, 100, z), (LB - 8, 100, z), (LB - 8, 100, z - 60), (8, 100, z - 60))]), "ws4")
        for i in range(len(BK) - 1, -1, -1):
            x = BK[i] - 6
            if bar and i < len(BK) - 1:
                o += bar_seg(cam, BK[i] + 6, BK[i + 1] - 6, zc)
            face = [(x, -100, H - 10)] + [(x, 30 * math.cos(math.radians(a)), zc + 30 * math.sin(math.radians(a))) for a in range(180, 361, 15)] + \
                [(x, 100, H - 10), (x, 100, H - 150), (x, -100, H - 150)]
            o += cpoly([cam.xy(p) for p in face], op, "ws2")
            o += cpoly([cam.xy(p) for p in ((x, -100, H - 10), (x + 12, -100, H - 10), (x + 12, -30, H - 10), (x, -30, H - 10))], op, "ws1")
            o += cpoly([cam.xy(p) for p in ((x, 30, H - 10), (x + 12, 30, H - 10), (x + 12, 100, H - 10), (x, 100, H - 10))], op, "ws1")
            if caps:
                zt = zc + 44
                cf = [(x, -40, zt)] + [(x, 30 * math.cos(math.radians(a)), zc + 30 * math.sin(math.radians(a))) for a in range(180, -1, -15)] + [(x, 40, zt)]
                o += cpoly([cam.xy(p) for p in cf], op, "ws2")
                o += cpoly([cam.xy(p) for p in ((x, -40, zt), (x + 12, -40, zt), (x + 12, 40, zt), (x, 40, zt))], op, "ws1")
                for y in (-30, 30):
                    o += hole3(cam, (x + 6, y, zt + .05), (0, 0, 1), 4.5, "ms2")
                if bar:
                    o += path(P3(circ3(cam, (x - .05, 0, zc), (-1, 0, 0), 30, 24)), "mf")
                    o += path(P3(circ3(cam, (x - .1, 0, zc), (-1, 0, 0), 10, 16)), "ts2")
        if bar:
            o += bar_seg(cam, 8, BK[0] - 6, zc)
        o += path(P3([cam.xy(p) for p in ((-4, -124, z), (LB + 4, -124, z), (LB + 4, 124, z), (-4, 124, z))]) +
                  P3(op), "o") if False else ""
        return o
    RAW(sc, inside, ((-4, -124, H), (LB + 4, 124, H + .1)), -3)


def bar_seg(cam, x0, x1, zc, r=10):
    if x1 <= x0:
        return ""
    return compact(GE.prism(cam, (x0, 0, zc), (1, 0, 0), GE.circle_outline(r, 16, 6), x1 - x0, "t", smooth=True, caps=False))


# ------------------------------------------------------------------ fitted figures
AREA = (16, 40, 464, 288)


def bfig(fn, az=27, el=31, area=AREA, sh_k=.5):
    return fit(fn, az, el, area, ret_scene=True, sh_ry=8, sh_k=sh_k, sh_dy=-4)


@dpart("engine.block", "detail")
def block_detail3():
    notes = [("ボア（シリンダ）", "内径φ80前後。真円度・円筒度は数μm、ホーニングで仕上げる"),
             ("デッキ面", "ヘッドとの合わせ面。平面度0.05mm以下・面粗さ管理"),
             ("ウォータジャケット", "ボアを囲む冷却水路（オープンデッキ）"),
             ("ヘッドボルト穴", "めねじ M10〜11。塑性域締結に耐えるねじ精度"),
             ("クランクジャーナル穴", "5か所を一直線に共加工（同軸度 数μm）"),
             ("オイルギャラリ", "全長を貫く深穴の油路（ガンドリル）"),
             ("オイルパン合わせ面", "加工の基準面、液状ガスケットのシール面"),
             ("マウント取付ボス", "エンジンマウント・補機の取付座面とねじ")]
    s, sc = bfig(lambda sc: blk(sc, 58), az=38, el=28, area=(40, 34, 430, 282))
    cam = sc.cam
    P_ = lambda p: cam.xy(p)
    for num, p, b in ((1, (146, -30, ZT), (150, 46)), (2, (300, -60, ZT), (330, 46)), (3, (190, 52, ZT), (230, 40)),
                      (4, (366, -66, ZT), (430, 70)), (5, (102, 0, ZC + 24), (60, 250)), (6, (58, GAL[0], GAL[1]), (190, 280)),
                      (7, (240, -124, 0), (300, 288)), (8, (300, -WU - 11, 160), (440, 230))):
        a = P_(p)
        s += bal(a[0], a[1], b[0], b[1], num)
    return rel(s), notes


def _melt():
    def fn(sc):
        BOX(sc, 0, 0, 0, 90, 90, 190, "pt", dark=1, ch=6)
        for i, (x, z) in enumerate(((20, 230), (50, 244), (34, 262))):
            BOX(sc, x, 30, z, 24, 30, 10, "w", ch=2)
        CYL(sc, (210, 45, 0), (0, 0, 1), 52, 80, "m", seg=32, r1=44)
        CYL(sc, (210, 45, 80), (0, 0, 1), 6, 120, "t", seg=12, bands=4)
        CYL(sc, (350, 45, 0), (0, 0, 1), 26, 34, "m", seg=24, r1=22)

        def top(s_):
            cam = s_.cam
            o = pg(cam, [(4, -.1, 110), (86, -.1, 110), (86, -.1, 176), (4, -.1, 176)], "hotin")
            o += pg(cam, [(4, -.1, 20), (86, -.1, 20), (86, -.1, 100), (4, -.1, 100)], "h")
            return o
        RAW(sc, top, ((0, -.2, 0), (90, -.1, 190)), -2)
        RAW(sc, lambda s_: path(P3(circ3(s_.cam, (210, 45, 74), (0, 0, 1), 46, 28)), "h") + path(P3(circ3(s_.cam, (210, 45, 74), (0, 0, 1), 9, 12)), "ts2"),
            ((160, 0, 80), (260, 90, 80.1)), -2)
        RAW(sc, lambda s_: path(P3(circ3(s_.cam, (350, 45, 30), (0, 0, 1), 22, 20)), "h"), ((330, 25, 34), (370, 65, 34.1)), -2)
    s, sc = bfig(fn, az=-18, el=24, area=(30, 70, 420, 262), sh_k=.55)
    cam = sc.cam
    a = cam.xy((90, 0, 120))
    b = cam.xy((160, 45, 90))
    s += path("M%s %s Q%s %s %s %s" % (n(a[0]), n(a[1]), n((a[0] + b[0]) / 2), n(a[1] - 18), n(b[0]), n(b[1])), "pour")
    r = cam.xy((210, 45, 20))
    s += bubbles(r[0], r[1] + 4, 8, 50, 40)
    t = cam.xy((45, 45, 300))
    s += arrow(t[0], t[1] - 24, t[0], t[1] + 6, None) + text(t[0] + 10, t[1] - 16, "地金・リターン材", "start", "al")
    f = cam.xy((45, 0, 0))
    s += heat(f[0] - 14, f[1] - 70, 4, 10) if False else ""
    s += text(f[0], f[1] + 18, "タワー溶解炉", "middle")
    g = cam.xy((210, 45, 200))
    s += text(g[0], g[1] - 8, "回転脱ガス（Ar・N₂）", "middle", "al")
    g = cam.xy((210, 0, 0))
    s += text(g[0] - 10, g[1] + 20, "取鍋で溶湯処理", "middle")
    a2, b2 = cam.xy((270, 45, 40)), cam.xy((318, 45, 30))
    s += arrow(a2[0], a2[1], b2[0], b2[1], None)
    g = cam.xy((350, 45, 0))
    s += text(g[0] + 10, g[1] - 52, "減圧凝固試験・成分分析", "middle")
    s += tol(320, 70, "溶湯温度 700〜720℃") + tol(320, 88, "水素量・介在物を管理")
    return s


def _hpdc():
    def fn(sc):
        BOX(sc, -70, -150, -20, 60, 300, 290, "m", dark=1)                 # fixed die (left)
        BOX(sc, LB + 50, -150, -20, 60, 300, 290, "m")                # moving die (right, opened)
        blk(sc, 58, "h", holes=False)
        CYL(sc, (120, -170, 6), (1, 0, 0), 16, 120, "m", seg=20, bands=6)  # shot sleeve under the runner
        CYL(sc, (80, -170, 6), (1, 0, 0), 9, 40, "t", seg=14, bands=4)     # plunger rod
    s, sc = bfig(fn, az=34, el=26, area=(16, 44, 310, 262))
    cam = sc.cam
    a, b = cam.xy((40, -170, 6)), cam.xy((150, -170, 6))
    s += arrow(a[0] - 30, a[1] + 26, b[0] - 30, b[1] + 26, "高速射出 4〜6m/s", (a[0] + b[0]) / 2 - 30, max(a[1], b[1]) + 46)
    c = cam.xy((LB + 50, -150, 40))
    s += arrow(c[0] + 34, c[1] + 26, c[0] - 6, c[1] + 26, None)
    f1, f2 = cam.xy((-40, -150, 270)), cam.xy((LB + 80, -150, 270))
    s += text(f1[0], f1[1] - 6, "固定型", "middle") + text(f2[0], f2[1] - 6, "可動型", "middle")
    s += lead(*cam.xy((58, 42, 180)), 334, 70, "鋳鉄ライナー（鋳ぐるみ）")
    s += lead(*cam.xy((58, 0, 200)), 334, 100, "ボア部は金型（中子）")
    s += lead(*cam.xy((58, -50, 210)), 334, 130, "水路も金型で成形")
    s += text(c[0] + 14, c[1] + 46, "型締め 2,500〜4,000t", "middle", "al")
    s += tol(334, 190, "真空ダイカストで") + tol(334, 206, "巻込みガスを低減")
    return s


def _trim():
    ovx = (36, 119, 202, 285, 345)

    def fn(sc):
        blk(sc, 0, cast=True, holes=False)
        for x in ovx:
            BOX(sc, x - 9, -WU - 16, ZT - 22, 18, 16, 20, "w", -2, ch=3)
        BOX(sc, 150, -152, 0, 60, 28, 10, "w", -2)
        BOX(sc, 100, -172, 0, 160, 20, 12, "w", -2)
        BOX(sc, 40, -180, -46, 300, 360, 30, "m", dark=1)
    s, sc = bfig(fn, az=24, el=28, area=(20, 40, 320, 274))
    cam = sc.cam
    for x in ovx:
        a, b = cam.xy((x - 13, -WU - 1, ZT - 24)), cam.xy((x + 13, -WU - 1, ZT - 24))
        s += line(a[0], a[1], b[0], b[1], "cutl")
    a, b = cam.xy((146, -124.5, 4)), cam.xy((214, -124.5, 4))
    s += line(a[0], a[1], b[0], b[1], "cutl")
    s += lead(*cam.xy((345, -WU - 16, ZT - 10)), 330, 50, "オーバーフロー")
    s += lead(*cam.xy((240, -172, 6)), 330, 250, "湯口（ランナー）")
    t = cam.xy((340, -180, -46))
    s += arrow(t[0] - 40, t[1] + 26, t[0] - 40, t[1] + 4, None) + text(t[0] - 30, t[1] + 22, "トリミング型", "start")
    s += tol(330, 140, "破線部で切断") + tol(330, 158, "→ ショットブラストで") + tol(330, 174, "酸化皮膜・バリを除去")
    return s


def mini(area, mat="w", az=27, el=31):
    return fit(lambda sc: blk(sc, 0, mat, holes=False, lite=True), az, el, area, sh=False)


def _ht():
    def fn(sc):
        BOX(sc, 0, 0, 0, 120, 100, 150, "pt", dark=1, ch=5)
        BOX(sc, 310, 0, 0, 120, 100, 150, "pt", dark=1, ch=5)
        BOX(sc, 160, 0, 0, 110, 100, 80, "m", dark=1)

        def faces(s_):
            cam = s_.cam
            o = ""
            for x0, c in ((0, "hotin"), (310, "warmin")):
                o += pg(cam, [(x0 + 12, -.1, 14), (x0 + 108, -.1, 14), (x0 + 108, -.1, 130), (x0 + 12, -.1, 130)], "bg")
                o += pg(cam, [(x0 + 12, -.1, 14), (x0 + 108, -.1, 14), (x0 + 108, -.1, 130), (x0 + 12, -.1, 130)], c)
            o += pg(cam, [(166, 6, 80.1), (264, 6, 80.1), (264, 94, 80.1), (166, 94, 80.1)], "fl")
            return o
        RAW(sc, faces, ((0, -.2, 0), (430, -.1, 150)), -2)
    s, sc = bfig(fn, az=-6, el=18, area=(20, 60, 460, 236), sh_k=.55)
    cam = sc.cam
    for x0 in (0, 310):
        a, b = cam.xy((x0 + 18, -.1, 120)), cam.xy((x0 + 102, -.1, 24))
        s += mini((a[0], a[1] + 2, b[0], b[1] - 2), "h" if x0 == 0 else "w")
    a, b = cam.xy((166, -.1, 150)), cam.xy((264, -.1, 50))
    s += mini((a[0] + 4, a[1], b[0] - 4, b[1]))
    s += pg(cam, [(160, -.2, 0), (270, -.2, 0), (270, -.2, 72), (160, -.2, 72)], "fl")
    s += heat(*cam.xy((60, -.1, 150)), 3, 12) if False else ""
    for x0, x1 in ((124, 156), (274, 306)):
        a, b = cam.xy((x0, -.1, 60)), cam.xy((x1, -.1, 60))
        s += arrow(a[0], a[1], b[0], b[1], None)
    for x, t in ((60, "溶体化 約500℃"), (215, "水焼入れ"), (370, "時効 約200℃")):
        a = cam.xy((x, -.1, 0))
        s += text(a[0], a[1] + 22, t, "middle")
    s += tol(20, 280, "硬さ（HB）とひずみを管理。T5の場合は時効のみ")
    return s


def _xray():
    def fn(sc):
        BOX(sc, 150, -40, 420, 80, 80, 60, "m", ch=4)
        CYL(sc, (190, 0, 420), (0, 0, -1), 16, 14, "m", seg=16, r1=8)
        blk(sc, 58)
        BOX(sc, -20, -160, -30, LB + 40, 320, 14, "m", dark=1)
    s, sc = bfig(fn, az=40, el=24, area=(30, 34, 360, 270))
    cam = sc.cam
    a = cam.xy((190, 0, 404))
    rays = ""
    for x, y in ((-10, -150), (90, -160), (200, -160), (330, -160), (LB + 10, -150), (LB + 10, 0), (LB + 10, 150)):
        b = cam.xy((x, y, -16))
        rays += line(a[0], a[1], b[0], b[1], "ray")
    s = s.replace('<path class="ray"', '<path class="ray"')
    s = rays + s
    pp = [cam.xy((58, y, z)) for y, z in ((60, 136), (63, 128), (-62, 196))]
    for x, y in pp[:2]:
        s += circ(x, y, 2.6, "poro")
    s += circ(pp[2][0], pp[2][1], 2.2, "poro")
    c = ((pp[0][0] + pp[1][0]) / 2, (pp[0][1] + pp[1][1]) / 2)
    s += circ(c[0], c[1], 10, "mfring") + lead(c[0] - 10, c[1], 24, 200, "鋳巣", "start")
    t = cam.xy((230, 0, 450))
    s += text(t[0] + 40, t[1], "X線源", "start")
    t = cam.xy((LB + 20, -160, -30))
    s += text(t[0] + 6, t[1] + 4, "検出器", "start")
    s += rect(396, 100, 70, 80, "xim") + circ(420, 134, 4, "ximd") + text(431, 196, "透過画像", "middle", "sm")
    return s


def _datum():
    def fn(sc):
        blk_pan(sc)
        fmill(sc, (250, 0, ZT + 36), 64, 16, 50, bias=-6)
        drill(sc, (20, -112, ZT + 18), (0, 0, 1), 6, 60, bias=-6)
        RAW(sc, lambda s_: hole3(s_.cam, (20, -112, ZT + .05), (0, 0, 1), 6) + hole3(s_.cam, (LB - 20, 112, ZT + .05), (0, 0, 1), 6) +
            path(P3([s_.cam.xy(p) for p in ((-4, -124, ZT), (LB + 4, -124, ZT), (LB + 4, 124, ZT), (-4, 124, ZT))]), "mf"),
            ((-4, -124, ZT), (LB + 4, 124, ZT + .1)), -4)
    s, sc = bfig(fn, az=26, el=40, area=(30, 40, 330, 262))
    cam = sc.cam
    for x in (40, 190, 340):
        p = cam.xy((x, -WU, 0))
        s += loc(p[0], p[1] + 1, -90)
    p = cam.xy((-4, -60, 120))
    s += clamp(p[0], p[1], 0)
    q = cam.xy((LB, 60, 120))
    s += clamp(q[0], q[1], 180)
    s += arc3(cam, (250, 0, ZT + 70), (0, 0, 1), 46, 200, 320)
    s += lead(*cam.xy((120, -124, ZT)), 340, 250, "基準面（パン面）")
    s += lead(*cam.xy((LB - 20, 112, ZT)), 340, 214, "基準穴×2")
    s += lead(*cam.xy((340, -WU, 0)), 340, 280, "鋳肌3点で位置決め")
    s += lead(q[0], q[1], 400, 120, "クランプ") if False else text(q[0] + 2, q[1] - 30, "クランプ", "middle")
    s += text(20, 292, "鋳肌を基準に最初の加工面をつくる", "start", "sm")
    return s


def _rough():
    def fn(sc):
        blk(sc, 58, holes=False)
        CYL(sc, (58, 0, 150), (0, 0, 1), 9, ZT + 70 - 150, "t", -6, seg=16, bands=6)
        CYL(sc, (58, 0, 150), (0, 0, 1), 34, 14, "t", -6, seg=28, bands=8)
        spindle(sc, (58, 0, ZT + 70), (0, 0, 1), 22, 40, -6)
        drill(sc, (58, GAL[0], GAL[1]), (-1, 0, 0), 4, 120, bias=-6)
        spindle(sc, (-66, GAL[0], GAL[1]), (-1, 0, 0), 14, 30, -6)
        drill(sc, (102, -66, ZT + 2), (0, 0, 1), 5, 60, bias=-6)
    s, sc = bfig(fn, az=46, el=26, area=(110, 36, 400, 262))
    cam = sc.cam
    s += bfeat(cam, 58, "bore") + bfeat(cam, 58, "gallery")
    s += path(P3(circ3(cam, (102, -66, ZT + .1), (0, 0, 1), 7, 16)), "mf")
    s += arc3(cam, (58, 0, ZT + 40), (0, 0, 1), 20, 200, 330)
    a = cam.xy((58, 0, ZT + 60))
    s += arrow(a[0] + 46, a[1] - 10, a[0] + 46, a[1] + 26, None) + text(a[0] + 54, a[1] + 14, "送り", "start", "al")
    for x in (120, 330):
        p = cam.xy((x, -124, 0))
        s += loc(p[0], p[1] + 1, -90)
    s += lead(*cam.xy((58, 30, 150)), 16, 120, "ボア荒加工", "start")
    s += lead(*cam.xy((10, GAL[0], GAL[1])), 400, 150, "オイルギャラリ（ガンドリル）", "middle") if False else \
        lead(*cam.xy((20, GAL[0], GAL[1])), 300, 236, "オイルギャラリ（ガンドリル）")
    s += lead(*cam.xy((102, -66, ZT + 30)), 16, 70, "ボルト下穴", "start")
    s += lead(*cam.xy((330, -124, 0)), 300, 284, "パン面・基準穴で位置決め")
    return s


def _lineb():
    zc = ZT - ZC

    def fn(sc):
        blk_pan(sc, caps=True, bar=True)
        RAW(sc, lambda s_: hole3(s_.cam, (-.1, 0, zc), (-1, 0, 0), 30, "ws3") + hole3(s_.cam, (-.1, 0, zc), (-1, 0, 0), 24),
            ((-.2, -40, zc - 40), (0, 40, zc + 40)), -3)
        CYL(sc, (-70, 0, zc), (1, 0, 0), 10, 70, "t", seg=16, bands=6)
        CYL(sc, (LB, 0, zc), (1, 0, 0), 10, 60, "t", seg=16, bands=6)
        BOX(sc, LB + 60, -50, zc - 50, 80, 100, 100, "m", ch=6)
    s, sc = bfig(fn, az=24, el=48, area=(20, 40, 460, 250))
    cam = sc.cam
    a, b = cam.xy((LB + 120, -50, zc - 60)), cam.xy((LB + 40, -50, zc - 60))
    s += arrow(a[0], a[1] + 14, b[0], b[1] + 14, None) + text((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2 + 32, "送り", "middle", "al")
    s += lead(*cam.xy((190, 0, zc + 44)), 300, 270, "軸受キャップ（仮組み）")
    s += tol(20, 262, "同軸度 数μm〜10μm・真円度") + tol(20, 278, "ガイドパッド付きラインボーリングバー")
    return s


def _deck():
    def fn(sc):
        blk(sc, 0)
        fmill(sc, (318, 0, ZT + 8), 72, 16, 50)
        drill(sc, (14, -66, ZT + 2), (0, 0, 1), 4.5, 66)
    s, sc = bfig(fn, az=27, el=31, area=(20, 38, 330, 262))
    cam = sc.cam
    s += path(P3([cam.xy(p) for p in ((0, 80, ZT), (0, -WU, ZT), (246, -WU, ZT))], False), "mf")
    for x in BK[:2]:
        for y in (-66, 66):
            s += path(P3(circ3(cam, (x, y, ZT + .1), (0, 0, 1), 7, 14)), "mf")
    s += arc3(cam, (318, 0, ZT + 50), (0, 0, 1), 52, 190, 320)
    t = cam.xy((318, -52, ZT + 50))
    s += text(t[0] + 22, t[1] + 4, "回転", "start", "al") if False else ""
    for x in (60, 330):
        p = cam.xy((x, -124, 0))
        s += loc(p[0], p[1] + 1, -90)
    s += lead(*cam.xy((200, -WU, ZT)), 400, 60, "デッキ面", "middle") if False else lead(*cam.xy((200, -WU, ZT)), 350, 80, "デッキ面")
    s += lead(*cam.xy((14, -66, ZT + 30)), 30, 290, "ヘッドボルト穴（タップ）", "start") if False else lead(*cam.xy((14, -66, ZT + 40)), 30, 56, "ヘッドボルト穴（タップ）", "start")
    s += text(*cam.xy((318, 60, ZT + 90)), "回転", "middle", "al") if False else ""
    s += tol(330, 290, "平面度0.05mm以下・面粗さ")
    return s


def _spray():
    def fn(sc):
        blk(sc, 58, holes=False, liner=False)
        CYL(sc, (58, 0, 160), (0, 0, 1), 7, ZT + 60 - 160, "t", -6, seg=14, bands=4)
        CYL(sc, (58, 0, 150), (0, 0, 1), 12, 18, "t", -6, seg=16, bands=6)
        spindle(sc, (58, 0, ZT + 60), (0, 0, 1), 18, 34, -6)
    s, sc = bfig(fn, az=46, el=26, area=(120, 36, 400, 262))
    cam = sc.cam
    S = lambda y, z: cam.xy((58, y, z))
    s += path(P3([S(-RB, 112), S(-RB, ZT - 2)], False) + P3([S(RB, 112), S(RB, ZT - 2)], False), "coat")
    x, y = cam.xy((58, 0, 159))
    s += spray_cone(x, y, 180, 24, 32, "hl") + spray_cone(x, y, 0, 24, 32, "hl")
    s += arc3(cam, (58, 0, ZT + 30), (0, 0, 1), 18, 200, 330)
    t = cam.xy((58, -60, ZT + 30))
    s += arrow(t[0] + 30, t[1] - 30, t[0] + 30, t[1] + 50, None, both=True) + text(t[0] + 38, t[1] + 10, "上下に移動", "start", "al")
    s += text(t[0] - 30, t[1] - 44, "回転", "middle", "al")
    s += lead(*S(RB - 2, 140), 20, 160, "溶射皮膜（数百μm）", "start")
    s += tol(350, 230, "密着強度・気孔率") + tol(350, 246, "→ ホーニングで仕上げ")
    return s


def _hone():
    def fn(sc):
        blk(sc, 58, holes=False)
        CYL(sc, (58, 0, 140), (0, 0, 1), 24, 60, "t", -6, seg=24, bands=8)
        for a in (210, 250, 290, 330):
            r = math.radians(a)
            BOX(sc, 58 + 24 * math.sin(r) - 3, 24 * math.cos(r) - 3, 144, 6, 6, 52, "gw", -7)
        CYL(sc, (58, 0, 200), (0, 0, 1), 8, ZT + 70 - 200, "t", -6, seg=14, bands=4)
        spindle(sc, (58, 0, ZT + 70), (0, 0, 1), 18, 34, -6)
    s, sc = bfig(fn, az=46, el=26, area=(120, 36, 400, 262))
    cam = sc.cam
    S = lambda y, z: cam.xy((58.5, y, z))
    h = ""
    for k in range(7):
        z0 = 118 + k * 15
        for y0, y1 in ((RB - 1, 28), (-26, -RB + 1)):
            a, b, c, d = S(y0, z0), S(y1, z0 + 9), S(y0, z0 + 9), S(y1, z0)
            h += line(a[0], a[1], b[0], b[1], "hatchx") + line(c[0], c[1], d[0], d[1], "hatchx")
    s += h + bfeat(cam, 58, "bore")
    s += arc3(cam, (58, 0, ZT + 36), (0, 0, 1), 18, 200, 330)
    t = cam.xy((58, -60, ZT + 30))
    s += arrow(t[0] + 30, t[1] - 30, t[0] + 30, t[1] + 50, None, both=True) + text(t[0] + 38, t[1] + 10, "往復", "start", "al")
    s += text(t[0] - 30, t[1] - 50, "回転", "middle", "al")
    s += lead(*S(34, 190), 20, 110, "クロスハッチ 40〜60°", "start")
    s += tol(330, 200, "荒→中→仕上げの3段") + tol(330, 216, "真円度・円筒度 数μm") + tol(330, 232, "プラトー粗さ（Rk・Rpk）")
    s += text(400, 284, "エアゲージで全数計測", "middle", "sm")
    return s


def _wash():
    def fn(sc):
        blk(sc, 0)
        for x in (60, 190, 320):
            CYL(sc, (x, -20, ZT + 50), (0, 0, 1), 6, 30, "t", seg=12, bands=4)
        CYL(sc, (LB + 4, GAL[0], GAL[1]), (1, 0, 0), 5, 80, "t", seg=12, bands=4)
        spindle(sc, (LB + 84, GAL[0], GAL[1]), (1, 0, 0), 12, 30)
    s, sc = bfig(fn, az=27, el=31, area=(20, 40, 400, 262))
    cam = sc.cam
    a, b = cam.xy((0, GAL[0], GAL[1])), cam.xy((LB, GAL[0], GAL[1]))
    s += line(a[0], a[1], b[0], b[1], "jetl")
    for x in (60, 190, 320):
        p = cam.xy((x, -20, ZT + 50))
        s += drops(p[0], p[1], 4, 30, 24, 90)
    s += lead(*cam.xy((LB + 50, GAL[0], GAL[1])), 420, 250, "高圧水ノズル", "middle")
    s += tol(40, 290, "残留異物の重量・最大粒径を管理（ISO 16232）")
    return s


def _leak():
    def fn(sc):
        blk(sc, 58, holes=False)
        BOX(sc, 58, -WU - 6, ZT, LB - 58 + 6, 2 * WU + 12, 12, "m", -4)
        BOX(sc, 58, -128, -12, LB - 58 + 4, 256, 12, "m", -4, dark=1)
    s, sc = bfig(fn, az=46, el=26, area=(110, 44, 340, 246))
    cam = sc.cam
    S = lambda y, z: cam.xy((58, y, z))
    for sg in (1, -1):
        s += path(P3([S(sg * 46, ZT), S(sg * 46, 150), S(sg * 55, 150), S(sg * 55, ZT)], False), "pres")
    s += path(P3([S(GAL[0] + 5 * math.cos(2 * PI * k / 14), GAL[1] + 5 * math.sin(2 * PI * k / 14)) for k in range(14)]), "pres")
    x, y = cam.xy((LB, -128, 0))
    s += line(x, y, x + 50, y, "cable") + circ(x + 68, y - 20, 22, "m") + line(x + 68, y - 20, x + 78, y - 32, "a")
    s += text(x + 68, y + 20, "差圧計", "middle")
    s += lead(*S(50, 200), 20, 100, "ウォータジャケット", "start") + lead(*S(GAL[0], GAL[1]), 380, 260, "オイルギャラリ")
    t = cam.xy((200, 0, ZT + 12))
    s += text(t[0] + 40, t[1] - 22, "シール治具で密閉", "middle", "sm")
    s += tol(20, 260, "リーク量 cc/min で判定") + tol(20, 276, "温度変化による偽不良に注意")
    return s


def _cmm():
    def fn(sc):
        BOX(sc, -60, -170, -40, LB + 120, 340, 40, "m", dark=1, ch=4)
        blk(sc, 0)
        for x in (-50, LB + 30):
            BOX(sc, x, 120, 0, 20, 30, 330, "pt", dark=1)
        BOX(sc, -50, 120, 330, LB + 100, 30, 30, "pt")
        BOX(sc, 110, 60, 320, 40, 90, 40, "pt")
        CYL(sc, (130, 80, 270), (0, 0, 1), 9, 60, "m", seg=14, bands=4)
        CYL(sc, (130, 80, ZT + 30), (0, 0, 1), 2.5, 10, "t", seg=10, bands=3)
    s, sc = bfig(fn, az=27, el=26, area=(30, 36, 420, 270))
    cam = sc.cam
    b = cam.xy((130, 80, ZT + 28))
    s += circ(b[0], b[1], 4, "t")
    sq = ""
    for i in range(4):
        for j in range(4):
            if (i * 3 + j) % 2 == 0:
                x0, z0 = 236 + i * 5, 196 - j * 5
                sq += pg(cam, [(x0, -WU - .1, z0), (x0 + 5, -WU - .1, z0), (x0 + 5, -WU - .1, z0 - 5), (x0, -WU - .1, z0 - 5)], "d")
    s += sq + lead(*cam.xy((246, -WU, 186)), 400, 200, "2次元コード")
    s += tol(240, 290, "ボア位置・デッキ高さ・ジャーナル位置")
    return s


@dpart("engine.block", "ops")
def block_ops3():
    ops = [_melt(), _hpdc(), _trim(), _ht(), _xray(), _datum(), _rough(), _lineb(), _deck(), _spray(), _hone(), _wash(), _leak(), _cmm()]
    titles = [t for t in (__import__("re").findall(r'class="ttl">([^<]*)<', o)[0] for o in OB.block_ops())]
    return [rel(fin(title(t) + s)) for t, s in zip(titles, ops)]


# =====================================================================================
# engine.head — DOHC aluminium head. Cross-section = the old head_end() art mapped onto the cut plane
#   u -> y = (120 - u) * KH, v -> z = (170 - v) * KH ; deck z = 0, cam side up
# =====================================================================================
KH = 85 / 110
LH = 380
HCX = [58, 146, 234, 322]
HBK = [14, 102, 190, 278, 366]
HYC, HZT, HZJ, HRJ = 44.8, 109.8, 105.1, 9.3
H_OUT = [(85, 0), (-85, 0), (-85, 100.5), (-71.1, HZT), (71.1, HZT), (85, 100.5)]


def uv(u, v, x=58):
    return (x, (120 - u) * KH, (170 - v) * KH)


def hd(sc, xc=0, mat="w", sec=None, flip=False, extra=None):
    """head solid from x = xc to LH. sec: svg (head_end art) mapped onto the cut face at x = xc."""
    cut = xc > 0
    dk = 0 if mat == "h" else 1
    if flip:
        X(sc, xc, LH - xc, [(y, HZT - z) for y, z in H_OUT][::-1], mat, dark=0)

        def deck(s_):
            cam = s_.cam
            z = HZT + .05
            o = ""
            for x in HCX:
                o += path(P3(circ3(cam, (x, 0, z), (0, 0, 1), 40, 28)), "ws3")
                for dx, y, r in ((-17, 18, 13), (17, 18, 13), (-16, -19, 11), (16, -19, 11)):
                    o += hole3(cam, (x + dx, y, z), (0, 0, 1), r, "ms2", 16) + hole3(cam, (x + dx, y, z), (0, 0, 1), r - 3, "bg", 14)
                o += hole3(cam, (x, 0, z), (0, 0, 1), 5, "bg", 10)
            for x in HBK:
                for y in (-66, 66):
                    o += hole3(cam, (x, y, z), (0, 0, 1), 5.5, "bg", 10)
                o += hole3(cam, (x, 50, z), (0, 0, 1), 3, "bg", 8) + hole3(cam, (x, -50, z), (0, 0, 1), 3, "bg", 8)
            return o
        RAW(sc, deck, ((xc, -85, HZT), (LH, 85, HZT + .1)), -3)
        return
    X(sc, xc, LH - xc, H_OUT, mat, dark=0)
    for x in HBK:
        if x - 10 >= xc:
            for y in (-HYC, HYC):
                BOX(sc, x - 10, y - 14, HZT, 20, 28, 11, mat, -1)
    for x in HCX:
        if x - 12 >= xc:
            CYL(sc, (x, 0, HZT), (0, 0, 1), 10, 14, mat, -1, seg=20)

    def top(s_):
        cam = s_.cam
        z = HZT + .05
        o = ""
        for x in HCX:
            for y in (-HYC, HYC):
                for dx in (-21, 21):
                    if x + dx - 13 >= xc:
                        o += bore(cam, (x + dx, y, z), (0, 0, 1), 12, 20, "hs3" if mat == "h" else "ws3", 20)
        for x in HBK:
            if x - 10 >= xc:
                for y in (-HYC, HYC):
                    o += pg(cam, [(x - 10.05, y + HRJ * math.cos(math.radians(a)), HZT + HRJ * math.sin(math.radians(a))) for a in range(0, 181, 30)], "bg")
        return o
    RAW(sc, top, ((xc, -85, HZT), (LH, 85, HZT + .1)), -3)

    def plugs(s_):
        return "".join(hole3(s_.cam, (x, 0, HZT + 14.05), (0, 0, 1), 6, "bg", 12) for x in HCX if x - 12 >= xc)
    RAW(sc, plugs, ((xc, -10, HZT + 14), (LH, 10, HZT + 14.1)), -4)

    def side(s_):
        cam = s_.cam
        y = -85.05
        o = ""
        for x in HCX:
            if x - 30 < xc:
                continue
            pts = [(x + 13 * math.cos(math.radians(a)) + (11 if math.cos(math.radians(a)) > 0 else -11), y, 53 + 12 * math.sin(math.radians(a))) for a in range(0, 360, 30)]
            o += poly3(cam, pts, "hs3" if mat == "h" else "ws3") + poly3(cam, [(p[0] * .8 + x * .2, y, p[2] * .8 + 53 * .2 - 2) for p in pts], "bg")
            for dx in (-34, 34):
                o += hole3(cam, (x + dx, y, 53), (0, -1, 0), 3, "bg", 8)
        return o
    RAW(sc, side, ((xc, -85.1, 0), (LH, -85, HZT)), -2)
    if not cut:
        def end(s_):
            cam = s_.cam
            o = ""
            for y in (-HYC, HYC):
                o += pg(cam, [(-.05, y + HRJ * math.cos(math.radians(a)), HZT + HRJ * math.sin(math.radians(a))) for a in range(0, 181, 30)], "bg")
            for y, z in ((-60, 20), (60, 20), (-20, 55), (20, 55)):
                o += hole3(cam, (-.05, y, z), (-1, 0, 0), 4, "bg", 8)
            return o
        RAW(sc, end, ((-.1, -85, 0), (0, 85, HZT)), -2)
    if cut:
        RAW(sc, lambda s_: gmat(sec if sec is not None else OE.head_end(), s_.cam, xc, None, KH, 120, 170, flip_u=False) + (extra(s_) if extra else ""),
            ((xc - .3, -85, 0), (xc - .2, 85, HZT + 11)), -3)


def hfig(fn, az=48, el=28, area=AREA, sh_k=.5):
    return fit(fn, az, el, area, ret_scene=True, sh_ry=8, sh_k=sh_k, sh_dy=-4)


@dpart("engine.head", "detail")
def head_detail3():
    notes = [("燃焼室・デッキ面", "ブロックとの合わせ面。平面度管理"), ("吸気ポート", "砂中子で形づくる曲がった流路"),
             ("バルブシート", "焼結合金を圧入。シート当たり幅を管理"), ("バルブガイド", "シートと同軸に仕上げる（数μm）"),
             ("カムジャーナル", "カムシャフトの軸受。キャップと共加工"), ("ウォータジャケット", "燃焼室まわりを冷やす水路"),
             ("点火プラグ穴", "燃焼室中央へ通じるねじ穴")]
    s, sc = hfig(lambda sc: hd(sc, 58), az=44, el=28, area=(40, 40, 440, 270))
    cam = sc.cam
    for num, p, b in ((1, (200, -85, 0), (240, 290)), (2, (146, -85, 53), (300, 270)), (3, uv(89, 157), (40, 250)),
                      (4, uv(72, 100), (40, 60)), (5, (102, -HYC, HZT + 11), (200, 40)), (6, uv(104, 90), (110, 40)),
                      (7, uv(120, 60), (150, 36))):
        a = cam.xy(p)
        s += bal(a[0], a[1], b[0], b[1], num)
    return rel(s), notes


def hmini(area, mat="w"):
    """light-weight head for small thumbnails: body, cam caps, plug towers, port openings (no bores)."""
    def fn(sc):
        X(sc, 0, LH, H_OUT, mat)
        for x in HBK:
            for y in (-HYC, HYC):
                BOX(sc, x - 10, y - 14, HZT, 20, 28, 11, mat, -1)

        def side(s_):
            cam = s_.cam
            return "".join(poly3(cam, [(x + 13 * math.cos(math.radians(a)) + (11 if math.cos(math.radians(a)) > 0 else -11), -85.05,
                                         53 + 12 * math.sin(math.radians(a))) for a in range(0, 360, 45)], "bg") for x in HCX)
        RAW(sc, side, ((0, -85.1, 0), (LH, -85, HZT)), -2)
    return fit(fn, 27, 31, area, sh=False)


def _cores():
    def fn(sc):
        for x0 in (0, 230):
            BOX(sc, x0, 0, 0, 170, 120, 60, "m", dark=1, ch=4)
        BOX(sc, -10, 10, 140, 420, 100, 26, "pt", ch=4)

        def cav(s_):
            cam = s_.cam
            o = ""
            for x0, pts in ((0, [(70, 110), (120, 110), (170, 150), (190, 196), (170, 200), (150, 170), (110, 150), (70, 150)]),
                            (230, [(410, 110), (360, 110), (310, 150), (290, 196), (310, 200), (330, 170), (370, 150), (410, 150)])):
                q = [(x0 + (u - (60 if x0 == 0 else 250)) * .95, 112 - (v - 100) * 1.0, 60.05) for u, v in pts]
                o += pg(cam, q, "sand")
                for k in range(0, len(q) - 1, 2):
                    p = cam.xy(((q[k][0] + q[-k - 1][0]) / 2, (q[k][1] + q[-k - 1][1]) / 2, 60.1))
                    o += circ(p[0], p[1], 1.1, "grain") + circ(p[0] + 5, p[1] + 2, 1.1, "grain")
            return o
        RAW(sc, cav, ((0, 0, 60), (400, 120, 60.1)), -2)
    s, sc = bfig(fn, az=-4, el=34, area=(40, 40, 440, 236), sh_k=.55)
    cam = sc.cam
    t = cam.xy((200, 10, 153))
    s += text(t[0], t[1] + 4, "ブローヘッド", "middle")
    for x in (85, 200, 315):
        a, b = cam.xy((x, 60, 136)), cam.xy((x, 60, 76))
        s += arrow(a[0], a[1], b[0], b[1], None)
    for x, t in ((85, "吸気ポート中子"), (315, "排気ポート中子")):
        a = cam.xy((x, 0, 0))
        s += text(a[0], a[1] + 20, t, "middle")
    s += tol(60, 278, "コールドボックス／無機バインダ。強度・ガス発生量を管理")
    return s


def _lpdc():
    def fn(sc):
        hd(sc, 58, "h", sec=OE.head_end("hot"))
        BOX(sc, 30, -120, -40, LH - 10, 240, 40, "m", dark=1)
        BOX(sc, 58, 85, 0, LH - 58, 36, HZT + 30, "m", dark=1)
        BOX(sc, 70, -100, HZT + 40, LH - 70, 186, 34, "m")
        CYL(sc, (200, 0, -150), (0, 0, 1), 14, 110, "h", seg=16, bands=6)
    s, sc = hfig(fn, az=40, el=24, area=(30, 40, 330, 240))
    cam = sc.cam
    a, b = cam.xy((200, -40, -140)), cam.xy((200, -40, -60))
    s += arrow(a[0], a[1], b[0], b[1], None) + text(a[0] + 8, (a[1] + b[1]) / 2, "下から充填", "start", "al")
    s += text(240, 274, "燃焼室側（下型）で急冷 → 組織を細かく", "middle")
    s += lead(*cam.xy(uv(30, 100)), 420, 60, "砂中子（ポート）", "middle")
    return s


def _shake():
    def fn(sc):
        hd(sc, 58)
        BOX(sc, 200, -20, HZT, 60, 40, 34, "w", -2, ch=3)
    s, sc = hfig(fn, az=44, el=26, area=(60, 44, 400, 236))
    cam = sc.cam
    a, b = cam.xy((190, -24, HZT + 4)), cam.xy((270, -24, HZT + 4))
    s += line(a[0], a[1], b[0], b[1], "cutl") + text(b[0] + 8, b[1] - 6, "押湯を切断", "start", "al")
    a, b = cam.xy((58, 85, 0)), cam.xy((LH, -85, 0))
    s += dots(min(a[0], b[0]), 244, abs(b[0] - a[0]), 26, 8, "grain")
    for x, d in ((40, 1), (440, -1)):
        s += arrow(x, 130, x + 20 * d, 120, None, both=True)
    s += text(240, 292, "ポート・水路の中の砂を確実に落とす（エンジン内の異物になる）", "middle", "sm")
    return s


def _hht():
    def fn(sc):
        BOX(sc, 0, 0, 0, 420, 100, 150, "pt", dark=1, ch=6)
        RAW(sc, lambda s_: pg(s_.cam, [(14, -.1, 14), (406, -.1, 14), (406, -.1, 136), (14, -.1, 136)], "bg") +
            pg(s_.cam, [(14, -.1, 14), (406, -.1, 14), (406, -.1, 136), (14, -.1, 136)], "hotin"), ((0, -.2, 0), (420, -.1, 150)), -2)
    s, sc = bfig(fn, az=-4, el=16, area=(40, 56, 440, 236), sh_k=.55)
    cam = sc.cam
    for i in range(3):
        a, b = cam.xy((24 + i * 130, -.1, 110)), cam.xy((136 + i * 130, -.1, 30))
        s += hmini((a[0], a[1], b[0], b[1]), "h")
    s += tol(40, 262, "硬さ・ひずみ・焼入れ割れ")
    return s


def _hxray():
    def fn(sc):
        BOX(sc, 160, -40, 300, 80, 80, 50, "m", ch=4)
        CYL(sc, (200, 0, 300), (0, 0, -1), 16, 14, "m", seg=16, r1=8)
        hd(sc, 58)
        BOX(sc, 0, -130, -30, LH + 30, 260, 14, "m", dark=1)
    s, sc = hfig(fn, az=44, el=24, area=(30, 34, 380, 270))
    cam = sc.cam
    a = cam.xy((200, 0, 286))
    rays = ""
    for x, y in ((0, -130), (120, -130), (250, -130), (LH + 30, -130), (LH + 30, 0), (LH + 30, 130)):
        b = cam.xy((x, y, -16))
        rays += line(a[0], a[1], b[0], b[1], "ray")
    s = rays + s
    x, y = cam.xy(uv(70, 150))
    s += circ(x, y, 2.4, "poro") + circ(x + 4, y - 3, 2, "poro") + circ(x + 2, y, 10, "mfring") + lead(x - 10, y, 40, 250, "鋳巣", "start")
    return s


def _hdeck():
    def fn(sc):
        hd(sc, 0, flip=True)
        fmill(sc, (300, 0, HZT + 6), 70, 16, 50, bias=-6)
    s, sc = hfig(fn, az=27, el=34, area=(30, 40, 360, 250))
    cam = sc.cam
    s += path(P3([cam.xy(p) for p in ((LH, 85, HZT), (0, 85, HZT), (0, -85, HZT), (232, -85, HZT))], False), "mf")
    s += arc3(cam, (300, 0, HZT + 46), (0, 0, 1), 48, 190, 320)
    for x in (30, 330):
        p = cam.xy((x, -85, 0))
        s += loc(p[0], p[1] + 1, -90)
    s += lead(*cam.xy((120, -85, HZT)), 40, 280, "デッキ面（燃焼室側）", "start")
    s += tol(370, 60, "平面度・穴位置")
    return s


def vax(side=0):
    """valve axis in the section: (seat point, unit vector toward the cam side) in 3D."""
    s0, s1 = ((89, 157), (58, 52)) if side == 0 else ((151, 157), (182, 52))
    a, b = uv(*s0), uv(*s1)
    d = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in d))
    return a, tuple(v / L for v in d)


def _press():
    seat, A = vax(0)

    def fn(sc):
        hd(sc, 58, sec=OE.head_end() + mf(OE.HEAD_F["seat"]) + mf(OE.HEAD_F["guide"]))
        c = tuple(seat[i] + A[i] * 120 for i in range(3))
        CYL(sc, (c[0] - 1, c[1], c[2]), A, 7, 50, "m", -8, seg=16, bands=6)
    s, sc = hfig(fn, az=48, el=26, area=(60, 40, 380, 250))
    cam = sc.cam
    a = cam.xy(tuple(seat[i] + A[i] * 180 for i in range(3)))
    b = cam.xy(tuple(seat[i] + A[i] * 128 for i in range(3)))
    s += arrow(a[0] - 26, a[1], b[0] - 26, b[1], "圧入", a[0] - 40, a[1] - 6)
    s += lead(*cam.xy(seat), 30, 280, "シートリング（焼結合金）", "start")
    s += tol(320, 272, "液体窒素で冷やして挿入") + tol(320, 288, "荷重・変位を監視")
    return s


def _seatfin():
    seat, A = vax(0)

    def fn(sc):
        hd(sc, 58, sec=OE.head_end() + mf(OE.HEAD_F["seat"].split(" M")[0]) + mf("M80 128 L66 78"))
        CYL(sc, (seat[0] - 1, seat[1], seat[2]), A, 2.4, 150, "t", -8, seg=10, bands=3)
        CYL(sc, (seat[0] - 1, seat[1], seat[2]), A, 9, 8, "t", -9, seg=16, r1=6, bands=6)
        c = tuple(seat[i] + A[i] * 150 for i in range(3))
        CYL(sc, (c[0] - 1, c[1], c[2]), A, 14, 44, "m", -8, seg=20, bands=6)
    s, sc = hfig(fn, az=48, el=26, area=(70, 36, 400, 256))
    cam = sc.cam
    s += lead(*cam.xy(uv(66, 90)), 20, 60, "リーマ（ガイド穴）", "start") + lead(*cam.xy(uv(84, 160)), 20, 274, "フォームツール（シート面）", "start")
    s += arc3(cam, tuple(seat[i] + A[i] * 170 for i in range(3)), A, 20, 200, 330)
    s += tol(330, 262, "シートとガイドの同軸度") + tol(330, 278, "数μm・当たり幅")
    return s


def _hline():
    def fn(sc):
        hd(sc, 0)
        CYL(sc, (-70, -HYC, HZT), (1, 0, 0), 5, LH + 130, "t", -6, seg=12, bands=4)
        BOX(sc, LH + 60, -HYC - 36, HZT - 36, 70, 72, 72, "m", ch=5)

        def rings(s_):
            return "".join(path(P3([s_.cam.xy((x - 10.1, -HYC + HRJ * math.cos(math.radians(a)), HZT + HRJ * math.sin(math.radians(a)))) for a in range(0, 181, 20)], False), "mf") for x in HBK)
        RAW(sc, rings, ((0, -HYC - 10, HZT), (LH, -HYC + 10, HZT + 11)), -7)
    s, sc = hfig(fn, az=24, el=32, area=(20, 44, 460, 250))
    cam = sc.cam
    a, b = cam.xy((LH + 120, -HYC - 36, HZT - 40)), cam.xy((LH + 40, -HYC - 36, HZT - 40))
    s += arrow(a[0], a[1] + 16, b[0], b[1] + 16, None) + text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 34, "送り", "middle", "al")
    s += tol(80, 280, "同軸度・真円度（ラインボーリング）")
    return s


def _hleak():
    def fn(sc):
        hd(sc, 58, sec=OE.head_end() + path(OE.HEAD_F["jacket"], "pres") + path(OE.HEAD_F["ports"], "pres"))
        BOX(sc, 58, -96, -12, LH - 58 + 6, 192, 12, "m", -4, dark=1)
        BOX(sc, 58, -97, 26, LH - 58, 12, 54, "m", -4)
    s, sc = hfig(fn, az=46, el=26, area=(60, 40, 340, 250))
    cam = sc.cam
    x, y = cam.xy((LH, -97, 50))
    s += line(x, y, x + 40, y, "cable") + circ(x + 58, y - 20, 20, "m") + line(x + 58, y - 20, x + 68, y - 32, "a")
    s += text(x + 58, y + 20, "差圧計", "middle") + tol(40, 284, "シール治具でポート・デッキを塞いで加圧")
    return s


def _vasm():
    seat, A = vax(0)

    def fn(sc):
        hd(sc, 58, sec=OE.head_end(valves=True))
        c = tuple(seat[i] + A[i] * 130 for i in range(3))
        CYL(sc, (c[0] - 1, c[1], c[2]), A, 13, 40, "m", -8, seg=20, bands=6)
    s, sc = hfig(fn, az=48, el=26, area=(70, 40, 380, 256))
    cam = sc.cam
    a = cam.xy(tuple(seat[i] + A[i] * 190 for i in range(3)))
    b = cam.xy(tuple(seat[i] + A[i] * 136 for i in range(3)))
    s += arrow(a[0] + 30, a[1], b[0] + 30, b[1], None) + text(a[0] + 38, (a[1] + b[1]) / 2, "圧縮・コッター挿入", "start", "al")
    s += tol(320, 284, "コッターの有無・着座を画像で確認")
    return s


def _titles(fn):
    return re.findall(r'class="ttl">([^<]*)<', "".join(fn()))


@dpart("engine.head", "ops")
def head_ops3():
    ops = [_cores(), _lpdc(), _shake(), _hht(), _hxray(), _hdeck(), _press(), _seatfin(), _hline(), _hleak(), _vasm()]
    return [rel(fin(title(t) + s)) for t, s in zip(_titles(OE.head_ops), ops)]


# =====================================================================================
# engine.cam — assembled camshaft (same geometry as il3_engine.camshaft), axis x
# =====================================================================================
CRT, CRJ, CRB, CRN, CEN = 10, 15, 17, 7, 13
CPH = [0, 270, 90, 180]


def lobe_ol(phi, k=1.0, lite=False):
    a = math.radians(phi)
    big = k > 1.5
    pts = arc(0, 0, CRB * k, phi + 60, phi + 300, 24 if big else 8) + arc(CEN * k * math.cos(a), CEN * k * math.sin(a), CRN * k, phi - 80, phi + 80, 12 if big else 5)
    return banded(hull(pts), 3 if (big or lite) else 2)


def cam_layout():
    """[(kind, x0, L, cyl)] along the shaft; kinds f (flange), n (neck), j (journal), t (tube), l (lobe), e (end)."""
    out = [("f", 0, 8, -1), ("n", 8, 8, -1), ("j", 16, 16, -1)]
    x = 32
    for c in range(4):
        for L, k in ((7, "t"), (13, "l"), (16, "t"), (13, "l"), (7, "t"), (16, "j")):
            out.append((k, x, L, c))
            x += L
    out.append(("e", x, 10, -1))
    return out


CLAY = cam_layout()
CJ = [x for k, x, L, c in CLAY if k == "j"]
CL = [x for k, x, L, c in CLAY if k == "l"]
CLEN = CLAY[-1][1] + 10


def camsh(sc, mat="w", tube_only=False, bias=0.0, lite=False):
    if tube_only:
        CYL(sc, (0, 0, 0), (1, 0, 0), CRT, 300, mat, bias, seg=20, bands=6, holes=[GE.circle_outline(6.5, 16, 8)])
        return
    RAW(sc, lambda s_: hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 8, "w3", 16) + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 5.5, "bg", 12) +
        hole3(s_.cam, (-.1, 0, 15), (-1, 0, 0), 2.6, "bg", 8), ((-.2, -26, -26), (0, 26, 26)), bias - 2)
    for k, x, L, c in CLAY:
        if k == "f":
            CYL(sc, (x, 0, 0), (1, 0, 0), 26, L, mat, bias, seg=24, bands=8)
        elif k == "n":
            CYL(sc, (x, 0, 0), (1, 0, 0), 13, L, mat, bias, seg=16, dark=1, lines=False)
        elif k == "j":
            CYL(sc, (x, 0, 0), (1, 0, 0), CRJ, L, mat, bias, seg=16, bands=5 if not lite else 4, lines=not lite)
        elif k == "t":
            CYL(sc, (x, 0, 0), (1, 0, 0), CRT, L, mat, bias, seg=12, bands=4, dark=1, lines=False)
        elif k == "l":
            X(sc, x, L, lobe_ol(90 + CPH[c], lite=lite), mat, bias, smooth=True, cap_mat="w2")
        else:
            CYL(sc, (x, 0, 0), (1, 0, 0), 11, L, mat, bias, seg=16, dark=1)


def LOBE(sc, C, phi, k, w, mat="w", bias=0.0, bore=True):
    """single lobe standing with its axis along -y (front face toward the viewer)."""
    ol = lobe_ol(phi, k)
    holes = [GE.circle_outline(7 * k, 20, 6)] if bore else []
    svg = GE.prism(sc.cam, C, (0, -1, 0), ol, w, mat, holes=holes, smooth="outer" if bore else True, cap_mat="w2" if mat == "w" else None)
    xs = [p[0] for p in ol]
    zs = [p[1] for p in ol]
    sc.add(compact(svg), ((C[0] + min(xs), C[1] - w, C[2] + min(zs)), (C[0] + max(xs), C[1], C[2] + max(zs))), bias)


def lobe_front(cam, C, phi, k, a0, a1, w):
    """screen points of the lobe outline on its front face between polar angles a0..a1 (deg)."""
    out = []
    for u, v, _ in lobe_ol(phi, k):
        a = math.degrees(math.atan2(v, u))
        if a0 <= a <= a1:
            out.append((a, cam.xy((C[0] + u, C[1] - w - .1, C[2] + v))))
    return [p for a, p in sorted(out)]


def cfig(fn, az=24, el=22, area=AREA, sh_k=.46):
    return fit(fn, az, el, area, ret_scene=True, sh_ry=6, sh_k=sh_k, sh_dy=-4)


@dpart("engine.cam", "detail")
def cam_detail3():
    notes = [("カムロブ", "バルブを押し開く偏心輪郭。プロフィール誤差・位相を管理"),
             ("ジャーナル", "ヘッドの軸受で支持。径・真円度"),
             ("中空パイプ（組立式）", "鋼管にロブを拡管・圧入で固定して軽量化"),
             ("ベース円", "バルブが閉じている区間。すき間調整の基準")]
    s, sc = cfig(lambda sc: camsh(sc), area=(16, 70, 344, 230))
    cam = sc.cam
    s += rect(360, 40, 110, 130, "m", 4) + text(415, 56, "ロブ正面", "middle", "sm")
    s2, sc2 = fit(lambda sc: LOBE(sc, (0, 0, 0), 90, 1.0, 12), 20, 14, (372, 66, 458, 160), ret_scene=True, sh=False)
    s += s2
    for num, p, b in ((1, (CL[2] + 6, 0, CEN + CRN), (110, 50)), (2, (CJ[1] + 8, 0, -CRJ), (90, 262)), (3, (CL[5] - 8, 0, -CRT), (230, 262))):
        a = cam.xy(p)
        s += bal(a[0], a[1], b[0], b[1], num)
    a = sc2.cam.xy((-CRB * .7, -12.1, -CRB * .7))
    s += bal(a[0], a[1], 380, 200, 4)
    return rel(s), notes


def _ctube():
    def fn(sc):
        camsh(sc, tube_only=True)
        CYL(sc, (300, 0, 0), (1, 0, 0), 40, 30, "m", seg=32)
        for a in (90, 210, 330):
            r = math.radians(a)
            BOX(sc, 286, 18 * math.cos(r) - 7, 18 * math.sin(r) - 7, 14, 14, 14, "dk", -1)
        BOX(sc, -46, -8, -4, 36, 16, 8, "t", -2)
    s, sc = cfig(fn, az=24, el=22, area=(40, 70, 440, 220))
    cam = sc.cam
    s += path(P3(circ3(cam, (-.2, 0, 0), (-1, 0, 0), CRT, 20)), "mf")
    s += arc3(cam, (120, 0, 0), (1, 0, 0), 22, 120, 240)
    a, b = cam.xy((-70, 0, 0)), cam.xy((-40, 0, 0))
    s += arrow(a[0], a[1] + 16, b[0], b[1] + 16, None)
    s += tol(90, 250, "全長・端面の直角度")
    return s


def _clobe():
    def fn(sc):
        LOBE(sc, (0, 0, 0), 90, 2.0, 16, "h", bore=False)
        BOX(sc, -50, -30, 52, 100, 46, 34, "t")
        BOX(sc, -50, -30, -70, 100, 46, 34, "t", dark=1)
        LOBE(sc, (230, 0, 0), 90, 2.0, 16)
        RING(sc, (230, 4, 28), (0, -1, 0), 34, 30, 6, "cu", -3, seg=28)
    s, sc = cfig(fn, az=16, el=14, area=(50, 44, 430, 240), sh_k=.6)
    cam = sc.cam
    a, b = cam.xy((-70, -30, 80)), cam.xy((-70, -30, 40))
    s += arrow(a[0], a[1], b[0], b[1], None)
    p = cam.xy((0, 0, -70))
    s += text(p[0], p[1] + 30, "冷間鍛造・焼結", "middle")
    q = lobe_front(cam, (230, 0, 0), 90, 2.0, 40, 140, 16)
    s += pline(q, "hotarc")
    p = cam.xy((230, 0, -70))
    s += text(p[0], p[1] + 30, "カム面を高周波焼入れ", "middle")
    a, b = cam.xy((70, -8, 0)), cam.xy((150, -8, 0))
    s += arrow(a[0], a[1], b[0], b[1], None)
    return s


def _casm():
    def fn(sc):
        camsh(sc, lite=True)
        CYL(sc, (-150, 0, 0), (1, 0, 0), 5, 150, "m", -3, seg=12, bands=4)
        CYL(sc, (-170, 0, 0), (1, 0, 0), 14, 20, "m", -3, seg=16)
    s, sc = cfig(fn, area=(20, 90, 460, 230))
    cam = sc.cam
    a, b = cam.xy((-150, 0, -40)), cam.xy((0, 0, -40))
    s += arrow(a[0], a[1], b[0], b[1], "マンドレルで拡管", (a[0] + b[0]) / 2, max(a[1], b[1]) + 18)
    s += tol(90, 60, "カム位相・締結強度（すべりトルク）を管理")
    return s


def centers(sc):
    CYL(sc, (-22, 0, 0), (1, 0, 0), 9, 22, "m", -1, seg=16, r1=1.5)
    BOX(sc, -90, -24, -24, 68, 48, 48, "m", ch=4)
    CYL(sc, (CLEN + 22, 0, 0), (-1, 0, 0), 9, 22, "m", -1, seg=16, r1=1.5)
    BOX(sc, CLEN + 22, -24, -24, 68, 48, 48, "m", ch=4)


def _cjgrind():
    def fn(sc):
        centers(sc)
        camsh(sc, lite=True)
        for x in (CJ[1], CJ[3]):
            CYL(sc, (x - 4, 0, CRJ + 46), (1, 0, 0), 46, 24, "gw", -2, seg=28, bands=6)
            CYL(sc, (x + 20, 0, CRJ + 46), (1, 0, 0), 12, 20, "m", -2, seg=16)
    s, sc = cfig(fn, area=(20, 40, 460, 250))
    cam = sc.cam
    for x in (CJ[1], CJ[3]):
        a, b = cam.xy((x + 1, -CRJ * .5, CRJ * .87)), cam.xy((x + 15, -CRJ * .5, CRJ * .87))
        s += line(a[0], a[1], b[0], b[1], "mf")
        s += arc3(cam, (x - 6, 0, CRJ + 46), (1, 0, 0), 54, 130, 200)
    s += tol(90, 280, "径・真円度・振れ")
    return s


def _cgrind():
    def fn(sc):
        LOBE(sc, (0, 0, 0), 90, 3.6, 30)
        CYL(sc, (-6, 0, 0), (0, -1, 0), 6, 50, "m", -2, seg=16)
        CYL(sc, (172, 0, -10), (0, -1, 0), 100, 40, "gw", seg=48, bands=12, holes=[GE.circle_outline(28, 24, 6)])
        CYL(sc, (172, 10, -10), (0, -1, 0), 26, 10, "m", 1, seg=24)
    s, sc = cfig(fn, az=14, el=14, area=(40, 40, 440, 250), sh_k=.6)
    cam = sc.cam
    s += pline(lobe_front(cam, (0, 0, 0), 90, 3.6, -40, 25, 30), "mf")
    a, b = cam.xy((110, -40, -125)), cam.xy((250, -40, -125))
    s += arrow(a[0], a[1], b[0], b[1], None, both=True) + text((a[0] + b[0]) / 2, a[1] + 20, "回転角に同期して前後", "middle", "al")
    s += arc3(cam, (0, -30, 0), (0, -1, 0), 90, 110, 160)
    p = cam.xy((-70, -30, 80))
    s += text(p[0] - 10, p[1], "回転", "middle", "al")
    p = cam.xy((172, -40, 92))
    s += text(p[0], p[1] - 8, "CBN砥石", "middle", "al")
    s += tol(20, 290, "プロフィール誤差・位相・研削焼け")
    return s


def _csuper():
    def fn(sc):
        LOBE(sc, (0, 0, 0), 90, 3.6, 30)
        CYL(sc, (-6, 0, 0), (0, -1, 0), 6, 50, "m", -2, seg=16)
        BOX(sc, 74, -40, -20, 16, 50, 40, "gw", -1)
        BOX(sc, 90, -46, -40, 60, 62, 80, "m", ch=5)
    s, sc = cfig(fn, az=14, el=14, area=(80, 50, 400, 250), sh_k=.6)
    cam = sc.cam
    p = cam.xy((170, -46, 0))
    s += arrow(p[0] + 4, p[1] - 40, p[0] + 4, p[1] + 40, None, both=True)
    p = cam.xy((120, -46, -40))
    s += text(p[0], p[1] + 22, "テープラップ", "middle")
    s += arc3(cam, (0, -30, 0), (0, -1, 0), 90, 110, 160)
    return s


def _cmeas():
    def fn(sc):
        centers(sc)
        camsh(sc, lite=True)
        for x in CL[:4]:
            CYL(sc, (x + 6.5, 0, CEN + CRN + 6), (0, 0, 1), 3, 60, "m", -2, seg=10, bands=3)
    s, sc = cfig(fn, area=(16, 100, 330, 284))
    cam = sc.cam
    for x in CL[:4]:
        p = cam.xy((x + 6.5, 0, CEN + CRN + 3))
        s += circ(p[0], p[1], 3, "t")
    s += chart(300, 40, 160, 80, "profile") + text(380, 136, "プロフィール誤差", "middle", "sm")
    return s


@dpart("engine.cam", "ops")
def cam_ops3():
    ops = [_ctube(), _clobe(), _casm(), _cjgrind(), _cgrind(), _csuper(), _cmeas()]
    return [rel(fin(title(t) + s)) for t, s in zip(_titles(OE.cam_ops), ops)]
