"""v3 shaded-3D principle drawings (q:) for heavy-industry equipment: large lathe, horizontal boring
mill, open-die forging press, no-bake moulding, centrifugal casting, directional-solidification furnace,
HIP, submerged-arc welding, portable line boring and the long-profile machining centre.
Overrides the older flat drawings in il_pictos_ind.py / il_pictos_gear.py."""
import math
import re
import il_gear as GE
from il_base import *
from il_pictos import picto, lab, chips
from il_pictos_ind import person
from il3_lib import fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3, compact

PI = math.pi


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def Y(sc, y0, L, xz, mat="pt", bias=0.0, **kw):
    """outline [(x, z), ...] extruded along +y from y0."""
    loop = [(-p[0], p[1], i) for i, p in enumerate(xz)]
    xs, zs = [p[0] for p in xz], [p[1] for p in xz]
    sc.add(compact(GE.prism(sc.cam, (0, y0, 0), (0, 1, 0), loop, L, mat, **kw)),
           ((min(xs), y0, min(zs)), (max(xs), y0 + L, max(zs))), bias)


def face(cam, pts_, c):
    return path(P([cam.xy(p) for p in pts_]), c)


def man(cam, p, k, h_m=1.7):
    """person silhouette standing at world point p; k = scene units per metre."""
    x, y = cam.xy(p)
    return person(x, y, h_m * k * cam.s)


_SD = re.compile(r'<path class="sands(\d)((?: [\w-]+)*)"((?: fill-rule="evenodd")?) d="([^"]*)"/>')
_SOP = {"1": "", "2": ".1", "3": ".22", "4": ".38"}


def sandify(svg):
    """faces drawn with mat "sand" (no shaded classes) -> flat sand fill + faint shade overlay."""
    def f(m):
        o = '<path class="sand%s"%s d="%s"/>' % (m.group(2), m.group(3), m.group(4))
        op = _SOP[m.group(1)]
        return o + ('<path class="grain" opacity="%s"%s d="%s"/>' % (op, m.group(3), m.group(4)) if op else "")
    return _SD.sub(f, svg)


def sector(r0, r1, a0, a1, seg=4):
    """annular sector outline (x, y) in the plane, angles in degrees."""
    return arc(0, 0, r1, a0, a1, seg) + arc(0, 0, r0, a1, a0, seg)


def halfshell(sc, C, ro, ri, h, mat="pt", a0=-15, a1=195, n_=7, bias=0.0, **kw):
    """vertical tube cut open at the front: only the back part (angles a0..a1, 90 = +y) is drawn."""
    st = (a1 - a0) / n_
    for k in range(n_):
        b0, b1 = a0 + k * st, a0 + (k + 1) * st
        pts_ = [(C[0] + x, C[1] + y) for x, y in sector(ri, ro, b0, b1, 2)]
        Z(sc, C[2], h, pts_, mat, bias, cap_mat=kw.get("cap_mat"), dark=kw.get("dark", 0))


# =====================================================================================
# q:hvlathe — heavy lathe: a long shaft between the face-plate chuck and the tailstock centre,
# carried by a steady rest; the carriage feeds the tool along the shaft
# =====================================================================================
@picto("hvlathe")
def _():
    xt = 300                                    # tool position along the axis
    R0, R1 = 30, 26                             # raw / turned radius

    def fn(sc):
        BOX(sc, -110, -60, -96, 640, 120, 32, "pt", dark=1)                    # long bed
        BOX(sc, -110, -56, -64, 64, 112, 120, "pt", dark=1, ch=6)              # headstock
        CYL(sc, (-46, 0, 0), (1, 0, 0), 62, 14, "dk", seg=40)                  # face plate
        for k in range(4):                                                      # jaws
            t = math.radians(45 + k * 90)
            c, s_ = math.cos(t), math.sin(t)
            X(sc, -32, 18, [(u * c - v * s_, u * s_ + v * c) for u, v in ((R0, -7), (R0 + 20, -7), (R0 + 20, 7), (R0, 7))], "m", -1)
        CYL(sc, (-32, 0, 0), (1, 0, 0), 22, 20, "w", seg=28)                    # chucked end
        CYL(sc, (-12, 0, 0), (1, 0, 0), R1, 182, "w", seg=36)                   # finished journal
        CYL(sc, (170, 0, 0), (1, 0, 0), R0 + 18, 26, "pt", seg=40, dark=1)      # steady-rest ring
        BOX(sc, 166, -34, -64, 34, 68, 34, "pt", dark=1)                        # steady-rest foot
        CYL(sc, (196, 0, 0), (1, 0, 0), R1, xt - 196, "w", seg=36)              # turned part
        CYL(sc, (xt, 0, 0), (1, 0, 0), R0, 448 - xt, "w", seg=36)               # raw part (to be turned)
        CYL(sc, (448, 0, 0), (1, 0, 0), 6, 12, "dk", seg=16, r1=1)              # centre point
        CYL(sc, (460, 0, 0), (1, 0, 0), 16, 30, "m", seg=24)                    # quill
        BOX(sc, 490, -46, -64, 40, 92, 96, "pt", dark=1, ch=5)                  # tailstock
        # carriage + tool post + holder from the front, insert at centre height
        BOX(sc, xt - 30, -96, -64, 80, 60, 20, "pt", dark=1)
        BOX(sc, xt - 6, -84, -44, 40, 34, 30, "m", -1)
        BOX(sc, xt + 2, -78, -14, 22, 44, 12, "dk", -2)
        Z(sc, -3, 4, [(xt, -R0 + 2), (xt + 14, -40), (xt + 24, -36), (xt + 12, -R0 + 1)], "t", -3)
    s, sc = fit(fn, -24, 20, (24, 38, 296, 172), sh_ry=6, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (70, 0, 0), (1, 0, 0), R1 + 12, 40, 150)
    s += arrow3(cam, (xt + 120, -96, -64), (xt + 64, -96, -64))
    tx, ty = cam.xy((xt + 2, -R0, 2))
    s += chips(tx + 2, ty - 2, 1.0)
    a = cam.xy((70, 0, R1 + 12))
    f = cam.xy((xt + 92, -96, -64))
    r = cam.xy((183, 0, R0 + 18))
    t = cam.xy((510, 0, 32))
    s += al(a[0], a[1] - 9, "回転") + al(f[0] + 4, f[1] + 16, "送り")
    s += lab(r[0], r[1] - 8, "振れ止め") + lab(t[0], t[1] - 10, "心押台")
    s += man(cam, (560, -70, -96), 50)
    return s


# =====================================================================================
# q:hbm — floor-type horizontal boring mill: the headstock rides up and down the column and
# pushes its boring spindle out into a large box part set on a rotary table
# =====================================================================================
@picto("hbm")
def _():
    zs = 70                                     # spindle height

    def fn(sc):
        BOX(sc, -230, -90, -40, 470, 180, 14, "pt", dark=1)                    # floor plate
        BOX(sc, -230, -50, -26, 56, 100, 230, "pt", dark=1, ch=6)              # column
        BOX(sc, -176, -40, zs - 36, 64, 80, 72, "pt", ch=5)                    # headstock (rides on the column)
        CYL(sc, (-112, 0, zs), (1, 0, 0), 22, 18, "dk", seg=28)               # quill sleeve
        CYL(sc, (-94, 0, zs), (1, 0, 0), 11, 74, "m", seg=24)                 # boring spindle (pushed out)
        CYL(sc, (-20, 0, zs), (1, 0, 0), 7, 22, "t", seg=20)                  # boring bar / tool
        CYL(sc, (90, 0, -26), (0, 0, 1), 110, 22, "m", seg=56)                # rotary table
        BOX(sc, 10, -80, -4, 160, 160, 150, "w", ch=8)                         # large box casting

        def marks(s_):
            o = ""
            for z, r in ((zs, 16), (zs - 50, 11)):
                o += hole3(s_.cam, (9.8, 0, z), (-1, 0, 0), r * 1.18, "w3") + hole3(s_.cam, (9.6, 0, z), (-1, 0, 0), r)
            for x, y in ((40, -50), (140, -50), (40, 50), (140, 50)):
                o += hole3(s_.cam, (x, y, 146.2), (0, 0, 1), 7)
            return o
        RAW(sc, marks, ((9.4, -60, 0), (9.8, 60, 146.3)), -2)
    s, sc = fit(fn, 30, 20, (30, 30, 290, 170), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    tx, ty = cam.xy((2, -6, zs + 6))
    s += chips(tx + 2, ty - 2, -0.9)
    s += arc3(cam, (-60, 0, zs), (1, 0, 0), 22, 100, 200)
    s += arrow3(cam, (-90, 0, zs + 46), (-30, 0, zs + 46))
    s += arrow3(cam, (-150, -46, zs + 50), (-150, -46, zs - 50), both=True)
    s += arc3(cam, (90, 0, -12), (0, 0, 1), 132, -60, 20)
    p = cam.xy((-60, 0, zs + 46))
    v = cam.xy((-150, -46, zs - 50))
    b = cam.xy((90, -132, -12))
    s += al(p[0], p[1] - 8, "突き出し") + al(v[0] - 12, v[1] + 6, "上下", "end")
    s += al(b[0] + 6, b[1] + 22, "回転テーブル")
    s += man(cam, (230, -60, -26), 34)
    return s


# =====================================================================================
# q:openforge — open-die forging press: the moving crosshead squeezes the hot ingot between flat
# dies; the manipulator grips the end, turns and pushes it through between strokes
# =====================================================================================
@picto("openforge")
def _():
    def oct_(ry, rz):
        return [(ry * math.cos(math.radians(22.5 + 45 * k)) / math.cos(math.radians(22.5)),
                 rz * math.sin(math.radians(22.5 + 45 * k)) / math.cos(math.radians(22.5))) for k in range(8)]

    def fn(sc):
        BOX(sc, -120, -86, -110, 240, 172, 40, "pt", dark=1)              # base
        BOX(sc, -46, -54, -70, 92, 108, 36, "t")                               # lower flat die
        BOX(sc, -46, -54, 32, 92, 108, 30, "t")                                # upper flat die
        BOX(sc, -104, -84, 62, 208, 168, 38, "pt", ch=6)                       # moving crosshead
        BOX(sc, -120, -92, 196, 240, 184, 44, "pt", dark=1, ch=6)              # top crosshead
        CYL(sc, (0, 0, 100), (0, 0, 1), 26, 96, "m", seg=20, bands=5)                   # plunger
        CYL(sc, (0, 0, 240), (0, 0, 1), 50, 34, "pt", seg=28, dark=1, bands=7)          # main cylinder
        for x in (-84, 84):                                                    # four columns
            for y in (-66, 66):
                CYL(sc, (x, y, -70), (0, 0, 1), 13, 132, "m", seg=14, bands=4, caps=False)
                CYL(sc, (x, y, 100), (0, 0, 1), 13, 96, "m", seg=14, bands=4, caps=False)
        # hot ingot: round where not yet forged, squeezed flat under the dies and behind them
        CYL(sc, (-250, 0, 0), (1, 0, 0), 42, 204, "h", seg=28, bands=7)
        X(sc, -46, 92, oct_(52, 32), "h")
        X(sc, 46, 110, oct_(46, 30), "h")
        # manipulator: body on wheels, arm and tongs gripping the ingot end
        BOX(sc, -420, -54, -100, 96, 108, 96, "pt", dark=1, ch=6)
        for x in (-404, -340):
            CYL(sc, (x, -54, -94), (0, -1, 0), 14, 10, "dk", seg=20)
        CYL(sc, (-324, 0, -6), (1, 0, 0), 22, 36, "m", seg=24)
        CYL(sc, (-288, 0, -6), (1, 0, 0), 30, 12, "dk", seg=28)
        for z0 in (34, -60):
            BOX(sc, -276, -14, z0, 34, 28, 20, "dk", -1)
    s, sc = fit(fn, 24, 18, (20, 18, 290, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (130, -100, 160), (130, -100, 100))
    s += arc3(cam, (-200, 0, 0), (1, 0, 0), 56, 60, 170)
    p = cam.xy((130, -100, 130))
    r = cam.xy((-200, 0, 56))
    m = cam.xy((-372, -54, -104))
    d = cam.xy((0, -86, -110))
    s += al(p[0] + 8, p[1] + 4, "加圧", "start") + al(r[0], r[1] - 8, "回転")
    s += lab(m[0], m[1] + 16, "マニプレータ") + lab(d[0] + 10, d[1] + 18, "平らな金敷")
    s += man(cam, (200, -80, -110), 34)
    return s


# =====================================================================================
# q:nobake — self-hardening (no-bake) sand moulding: a swinging continuous mixer pours resin-coated
# sand into a large flask around the pattern, where it hardens by itself
# =====================================================================================
@picto("nobake")
def _():
    xs = 50                                     # spout position

    def fn(sc):
        th = 9
        BOX(sc, -130, 70 - th, -60, 260, th, 80, "m", dark=.5)                  # flask: back wall
        BOX(sc, -130, -70 + th, -60, th, 140 - 2 * th, 80, "m", dark=.5)        # left wall
        BOX(sc, 130 - th, -70 + th, -60, th, 140 - 2 * th, 80, "m", dark=.5)    # right wall
        BOX(sc, -130 + th, -70 + th, -60, 260 - 2 * th, 140 - 2 * th, 66, "sand")  # sand packed so far
        BOX(sc, -130, -70, -60, 260, th, 80, "m", dark=.5)                      # front wall
        BOX(sc, -100, -34, 6, 84, 68, 22, "t", ch=4)                            # pattern sticking out
        X(sc, -100, 84, banded(arc(0, 28, 22, 0, 180, 8), 2), "t")
        CYL(sc, (xs, 4, 6), (0, 0, 1), 30, 14, "sand", seg=16, r1=3, bands=3, lines=False)             # heap under the stream
        # mixer: pillar, swinging arm (trough with screw), spout
        CYL(sc, (-220, 20, -70), (0, 0, 1), 34, 12, "dk", seg=28)
        CYL(sc, (-220, 20, -58), (0, 0, 1), 15, 210, "pt", seg=24, dark=.6)
        BOX(sc, -244, 4, 152, xs + 262, 32, 26, "pt", ch=4)
        CYL(sc, (xs, 20, 152), (0, 0, -1), 13, 20, "m", seg=20, r1=7)
        CYL(sc, (-230, 20, 178), (0, 0, 1), 22, 22, "dk", seg=20)               # drive motor

    def stream(cam):
        a, b = cam.xy((xs, 20, 132)), cam.xy((xs, 4, 18))
        w = 4.5 * cam.s
        return path("M%s %sL%s %sL%s %sL%s %sZ" % (n(a[0] - w), n(a[1]), n(a[0] + w), n(a[1]), n(b[0] + w * 1.5), n(b[1]), n(b[0] - w * 1.5), n(b[1])), "sand")
    s, sc = fit(fn, -26, 24, (26, 18, 296, 178), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s = sandify(s) + stream(cam)
    s += arc3(cam, (-220, 20, 150), (0, 0, 1), 46, -60, 40)
    m = cam.xy((-60, 20, 236))
    f = cam.xy((0, -70, -60))
    t = cam.xy((-58, 0, 56))
    g = cam.xy((-266, -4, 150))
    s += lab(m[0], m[1] - 8, "混練機（砂＋樹脂）") + lab(f[0], f[1] + 18, "鋳枠")
    s += lab(t[0], t[1] - 8, "模型") + al(g[0] - 4, g[1] + 4, "旋回", "end")
    s += man(cam, (170, -70, -60), 50)
    return s


# =====================================================================================
# q:centrifugal — horizontal centrifugal casting: the mould spins on rollers; melt poured in through a
# trough is thrown against the inner wall and freezes as a dense tube
# =====================================================================================
@picto("centrifugal")
def _():
    RO, RL, RB = 56, 44, 30                     # mould outside / cast layer outside / bore

    def fn(sc):
        BOX(sc, -10, -80, -112, 330, 160, 22, "pt", dark=1)                    # base frame
        segs = ((0, 40), (60, 190), (270, 30))
        for x0, L in segs:
            CYL(sc, (x0, 0, 0), (1, 0, 0), RO, L, "m", seg=32, bands=8)                 # mould
        for x0 in (40, 250):
            CYL(sc, (x0, 0, 0), (1, 0, 0), RO + 10, 20, "dk", seg=40)          # riding tyres
            CYL(sc, (x0 - 4, -50, -62), (1, 0, 0), 22, 28, "pt", -1, seg=24)    # front support rollers
            BOX(sc, x0 - 6, -70, -90, 32, 40, 20, "pt", dark=1)
        CYL(sc, (300, 0, 0), (1, 0, 0), 30, 22, "dk", seg=28)                  # drive end
        BOX(sc, 322, -40, -90, 60, 80, 70, "pt", dark=.5, ch=5)                # motor

        def endface(s_):
            c = s_.cam
            return hole3(c, (-0.2, 0, 0), (-1, 0, 0), RL, "h", 40) + hole3(c, (-0.3, 0, 0), (-1, 0, 0), RB, "bg", 40)
        RAW(sc, endface, ((-0.4, -RL, -RL), (-0.2, RL, RL)), -1)
        # pouring trough reaching into the bore, ladle tipping melt into it
        X(sc, -120, 118, [(-9, -20), (9, -20), (12, -8), (-12, -8)], "dk", -3)
        CYL(sc, (-200, 0, 40), (0.2, 0, 0.98), 24, 50, "dk", -2, seg=28, bands=14, r1=32, cap_mat="h")
    s, sc = fit(fn, 26, 16, (24, 22, 296, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    lip = (-200 + 0.2 * 50 + 0.98 * 32, 0, 40 + 0.98 * 50 - 0.2 * 32)
    a, b = cam.xy(lip), cam.xy((-100, 0, -9))
    w = 3.2 * cam.s
    s += path("M%s %sQ%s %s %s %sL%s %sQ%s %s %s %sZ" % (n(a[0] - w), n(a[1]), n(a[0] + 4), n(b[1] - 10), n(b[0] - w), n(b[1]),
              n(b[0] + w), n(b[1]), n(a[0] + 10), n(b[1] - 12), n(a[0] + w), n(a[1])), "h")
    s += face(cam, [(-118, -8, -8.2), (-2, -8, -8.2), (-2, 8, -8.2), (-118, 8, -8.2)], "h")
    s += arc3(cam, (150, 0, 0), (1, 0, 0), RO + 16, 40, 150)
    c = cam.xy((0, 0, 0))
    for ang in (-30, 150):
        u, v = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        s += arrow(c[0] + 6 * u, c[1] + 6 * v, c[0] + 22 * u, c[1] + 22 * v, None)
    r = cam.xy((150, 0, RO + 16))
    d = cam.xy((-200, 0, 110))
    m = cam.xy((150, -80, -112))
    s += al(r[0], r[1] - 8, "高速回転") + lab(c[0] - 6, c[1] - RO * cam.s - 12, "遠心力")
    s += lab(d[0], d[1] - 6, "溶湯") + lab(m[0], m[1] + 16, "回転する金型")
    return s


# =====================================================================================
# q:dsfurnace — directional solidification / single-crystal furnace (Bridgman): in vacuum the shell
# mould is lowered on a water-cooled chill plate out of the heater, past the baffle, so the blade
# freezes from the bottom up as columnar / single-crystal grains
# =====================================================================================
@picto("dsfurnace")
def _():
    zb = 20                                     # baffle level = solidification front

    def fn(sc):
        CYL(sc, (0, 0, -150), (0, 0, 1), 124, 10, "pt", seg=48, dark=1)        # vessel floor
        halfshell(sc, (0, 0, -140), 124, 116, 300, "pt", dark=1)                # vacuum vessel (front cut away)
        halfshell(sc, (0, 0, zb + 8), 74, 64, 120, "h")                         # heater
        halfshell(sc, (0, 0, zb), 76, 24, 8, "dk")                              # baffle
        # ceramic shell mould (front half cut away)
        Z(sc, zb + 8, 104, [(18 * math.cos(math.radians(a)), 12 * math.sin(math.radians(a))) for a in range(0, 181, 30)], "pt")
        Z(sc, -36, 56, [(18 * math.cos(math.radians(a)), 12 * math.sin(math.radians(a))) for a in range(0, 181, 30)], "pt")
        CYL(sc, (0, 0, -48), (0, 0, 1), 34, 12, "cu", seg=32)                   # water-cooled chill plate
        CYL(sc, (0, 0, -140), (0, 0, 1), 9, 92, "m", seg=20)                    # withdrawal ram

        def cut(s_):
            c = s_.cam
            o = face(c, [(-18, 0, zb), (18, 0, zb), (18, 0, zb + 112), (-18, 0, zb + 112)], "cut")
            o += face(c, [(-14, 0, zb), (14, 0, zb), (12, 0, zb + 106), (-12, 0, zb + 106)], "h")
            o += face(c, [(-18, 0, -36), (18, 0, -36), (18, 0, zb), (-18, 0, zb)], "cut")
            o += face(c, [(-14, 0, -24), (14, 0, -24), (14, 0, zb), (-14, 0, zb)], "w")
            o += face(c, [(-2, 0, -36), (2, 0, -36), (2, 0, -24), (-2, 0, -24)], "w")
            for x in (-8, -3, 2, 7, 11):
                a, b = c.xy((x, 0, -22)), c.xy((x * .95, 0, zb - 1))
                o += line(a[0], a[1], b[0], b[1], "o thin")
            return o
        RAW(sc, cut, ((-18, -0.2, -36), (18, 0, zb + 112)), -3)
    s, sc = fit(fn, 20, 18, (40, 16, 220, 182), sh_ry=7, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (40, -40, -60), (40, -40, -120))
    h = cam.xy((124, 0, 110))
    c = cam.xy((124, 0, -42))
    d = cam.xy((124, 0, -100))
    g = cam.xy((124, 0, 0))
    s += lab(h[0] + 8, h[1], "加熱帯", "start") + lab(g[0] + 8, g[1], "凝固界面", "start")
    s += lab(c[0] + 8, c[1], "水冷板", "start") + al(d[0] + 8, d[1] + 4, "引き抜き", "start")
    return s


# =====================================================================================
# q:hip — hot isostatic pressing: parts sit inside a heater in a thick-walled pressure vessel;
# compressed argon at high temperature presses on every surface equally and closes inner pores
# =====================================================================================
@picto("hip")
def _():
    def fn(sc):
        CYL(sc, (0, 0, -150), (0, 0, 1), 92, 30, "pt", seg=40, dark=1, bands=10)   # bottom closure
        halfshell(sc, (0, 0, -120), 92, 64, 210, "pt", dark=.6)                     # thick vessel wall (cut open)
        halfshell(sc, (0, 0, -112), 58, 52, 190, "h")                               # heater
        CYL(sc, (0, 0, 90), (0, 0, 1), 92, 30, "pt", seg=40, dark=1, bands=10)      # top closure
        CYL(sc, (0, 0, -106), (0, 0, 1), 40, 6, "m", seg=28)                        # tray
        CYL(sc, (0, 0, -100), (0, 0, 1), 30, 30, "w", seg=28, bands=8)              # casting: flange
        CYL(sc, (0, 0, -70), (0, 0, 1), 18, 56, "w", seg=24, bands=6)               #          body
        # gas supply: pipe -> compressor -> argon bottle
        CYL(sc, (92, 0, -136), (1, 0, 0), 5, 60, "m", seg=12, bands=3)
        BOX(sc, 152, -36, -150, 70, 72, 64, "pt", ch=5)
        CYL(sc, (222, 0, -136), (1, 0, 0), 5, 30, "m", seg=12, bands=3)
        CYL(sc, (272, 0, -150), (0, 0, 1), 20, 110, "dk", seg=20, bands=5)
        CYL(sc, (272, 0, -40), (0, 0, 1), 20, 14, "dk", seg=20, r1=8)

        def pores(s_):
            o = ""
            for x, z in ((-8, -40), (6, -28), (-4, -56), (10, -84)):
                o += hole3(s_.cam, (x, -18 if abs(x) < 9 else -14, z), (0, -1, 0), 2.2)
            return o
        RAW(sc, pores, ((-14, -18.2, -90), (14, -18, -20)), -2)
    s, sc = fit(fn, 20, 18, (24, 16, 296, 180), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    c = cam.xy((0, 0, -60))
    k = cam.s
    for ang in (0, 90, 180, 270):
        u, v = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        r0, r1 = (52 if ang % 180 == 0 else 64) * k, (30 if ang % 180 == 0 else 48) * k
        s += arrow(c[0] + r0 * u, c[1] + r0 * v, c[0] + r1 * u, c[1] + r1 * v, None)
    v = cam.xy((-40, 92, 120))
    g = cam.xy((272, -20, -150))
    s += lab(v[0], v[1] - 8, "高圧容器") + lab(g[0] - 10, g[1] + 16, "Arガス")
    t = cam.xy((230, 0, 70))
    s += al(t[0], t[1] - 10, "高温・高圧で") + al(t[0], t[1] + 6, "四方から加圧")
    return s


# =====================================================================================
# q:subarc — submerged-arc welding of thick plates: the head runs along the V groove, laying granular
# flux ahead of the wire; the arc burns hidden under the flux, leaving slag over the bead behind
# =====================================================================================
@picto("subarc")
def _():
    xh = 150                                    # wire / contact tip position
    G = [(-2, -24), (-16, 0)]                   # groove half: root, top edge (y, z)

    def plate(sg):
        o = [(sg * 2, -40), (sg * 96, -40), (sg * 96, 0), (sg * 16, 0), (sg * 2, -24)]
        return o if sg > 0 else o[::-1]

    def fn(sc):
        for sg in (-1, 1):
            X(sc, 0, 320, plate(sg), "w", dark=.2)                               # thick plates with V groove
        X(sc, 0, 320, [(-2, -40), (2, -40), (2, -24), (-2, -24)], "w", .5)        # root (tack/backing)
        # flux heap ahead of and around the tip, slag crust and bead behind
        heap = banded(arc(0, -2, 26, 0, 180, 8), 2)
        X(sc, 70, xh + 40 - 70, heap, "sand")
        X(sc, xh + 40, 50, [(-16, 0), (16, 0), (14, 6), (0, 9), (-14, 6)], "dk", dark=.3)  # slag crust
        X(sc, xh + 90, 230 - 90 - xh + 90, [(-16, 0), (16, 0), (13, 4), (0, 6), (-13, 4)], "w", dark=-.1)  # bead
        # welding head: carriage, contact tube, flux hopper, wire spool
        BOX(sc, 90, -30, 130, 150, 60, 34, "pt", dark=.6, ch=5)
        CYL(sc, (xh, 0, 30), (0, 0, 1), 8, 100, "cu", seg=16, bands=4)
        CYL(sc, (xh, 0, 10), (0, 0, 1), 4, 20, "cu", seg=12, bands=3, r1=7)
        CYL(sc, (96, 0, 90), (0, 0, 1), 8, 40, "pt", seg=24, r1=30, dark=.4, bands=6)  # hopper (cone)
        CYL(sc, (96, 0, 130), (0, 0, 1), 30, 10, "pt", seg=24, dark=.4, bands=6)
        CYL(sc, (210, 30, 200), (0, -1, 0), 34, 22, "dk", seg=32, bands=8, cap_mat="cu")  # wire spool

        def tube(s_):
            c = s_.cam
            a, b = c.xy((96, 0, 90)), c.xy((118, 0, 30))
            return path("M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1])), "pipe")
        RAW(sc, tube, ((96, -2, 30), (118, 2, 90)), -1)
    s, sc = fit(fn, 24, 18, (20, 22, 300, 168), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s = sandify(s)
    a, b = cam.xy((198, -10, 190)), cam.xy((xh + 6, 0, 130))
    s += path("M%s %sQ%s %s %s %s" % (n(a[0]), n(a[1]), n(b[0] + 6), n(a[1]), n(b[0]), n(b[1])), "wire2")
    s += arrow3(cam, (60, -110, -40), (0, -110, -40))
    h = cam.xy((96, 0, 140))
    w = cam.xy((210, 0, 238))
    d = cam.xy((30, -110, -40))
    bd = cam.xy((290, 0, 6))
    s += lab(h[0] - 30, h[1] - 6, "フラックス", "end") + lab(w[0] + 10, w[1] - 4, "ワイヤ", "start")
    s += al(d[0], d[1] + 18, "溶接方向") + lab(bd[0] + 4, bd[1] - 14, "ビード")
    return s


# =====================================================================================
# q:portbore — portable line boring on site: bearing supports bolted to the two bosses of a large
# structure carry a long boring bar; the drive unit turns the bar and feeds the cutter along the bore
# =====================================================================================
@picto("portbore")
def _():
    xt = 196                                    # cutter position (entering the second boss)

    def fn(sc):
        BOX(sc, -10, -80, -120, 290, 160, 26, "w", dark=.3)                     # structure (shell plate)
        for x0 in (0, 230):
            BOX(sc, x0, -70, -94, 40, 140, 170, "w", dark=.1, ch=4)            # bosses to be bored
        BOX(sc, -26, -46, -46, 26, 92, 92, "pt", ch=4)                         # bearing support (bolted on)
        CYL(sc, (-46, 0, 0), (1, 0, 0), 26, 20, "dk", seg=28, bands=7)
        BOX(sc, 270, -46, -46, 26, 92, 92, "pt", ch=4)
        CYL(sc, (296, 0, 0), (1, 0, 0), 26, 20, "dk", seg=28, bands=7)
        BOX(sc, -150, -44, -44, 70, 88, 88, "pt", dark=.4, ch=5)               # drive + feed unit
        CYL(sc, (-128, 0, 44), (0, 0, 1), 20, 46, "dk", seg=20, bands=5)        # motor
        CYL(sc, (-80, 0, 0), (1, 0, 0), 11, 34, "m", seg=20, bands=5)           # bar (visible pieces)
        CYL(sc, (40, 0, 0), (1, 0, 0), 11, xt - 40, "m", seg=20, bands=5)
        CYL(sc, (316, 0, 0), (1, 0, 0), 11, 40, "m", seg=20, bands=5)
        CYL(sc, (xt, 0, 0), (1, 0, 0), 18, 22, "dk", -1, seg=24, bands=6)       # cutter head
        BOX(sc, xt + 6, -5, 18, 10, 10, 12, "t", -2)                           # cutting bit

        def bores(s_):
            c = s_.cam
            o = ""
            for x0 in (0, 230):
                o += hole3(c, (x0 - .2, 0, 0), (-1, 0, 0), 34, "w3", 36) + hole3(c, (x0 - .3, 0, 0), (-1, 0, 0), 30, "bg", 36)
            return o
        RAW(sc, bores, ((229.4, -34, -34), (229.8, 34, 34)), -.5)
    s, sc = fit(fn, 26, 18, (24, 30, 296, 172), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (110, 0, 0), (1, 0, 0), 26, 40, 150)
    s += arrow3(cam, (90, -86, -94), (170, -86, -94))
    r = cam.xy((110, 0, 26))
    f = cam.xy((130, -86, -94))
    b = cam.xy((356, 0, 0))
    br = cam.xy((300, 0, 50))
    s += al(r[0], r[1] - 8, "回転") + al(f[0], f[1] + 18, "送り")
    s += lab(b[0] - 4, b[1] + 22, "中ぐり棒") + lab(br[0] + 4, br[1] - 8, "軸受台")
    return s


# =====================================================================================
# q:profile — long-profile machining centre: a travelling column runs along the bed beside a long
# hollow aluminium extrusion clamped in fixtures; its vertical spindle drills and machines it
# =====================================================================================
@picto("profile")
def _():
    xs = 40                                     # spindle position

    def fn(sc):
        BOX(sc, -300, -54, -62, 600, 108, 30, "pt", dark=1)                    # long bed
        for x in (-250, -130, -10, 110, 230):                                  # fixtures / clamps
            BOX(sc, x, -40, -32, 24, 80, 8, "dk")
            BOX(sc, x, -40, -24, 24, 10, 16, "dk", -1)
        BOX(sc, -290, -24, -24, 570, 48, 34, "w")                               # hollow extrusion
        for y in (60, 120):
            BOX(sc, -300, y - 6, -62, 600, 12, 8, "m")                          # column rails
        BOX(sc, xs - 34, 62, -54, 68, 66, 200, "pt", dark=.8, ch=5)            # travelling column
        BOX(sc, xs - 22, -14, 96, 44, 76, 40, "pt", ch=4)                       # ram / spindle head
        CYL(sc, (xs, 0, 60), (0, 0, 1), 15, 36, "dk", seg=24, bands=6)          # spindle
        CYL(sc, (xs, 0, 46), (0, 0, 1), 9, 14, "m", seg=20, bands=5, r1=13)     # holder
        CYL(sc, (xs, 0, 10), (0, 0, 1), 4.5, 36, "t", seg=16, bands=4)          # drill

        def marks(s_):
            c = s_.cam
            o = face(c, [(-290.2, -18, -18), (-290.2, -2, -18), (-290.2, -2, 4), (-290.2, -18, 4)], "bg")
            o += face(c, [(-290.2, 2, -18), (-290.2, 18, -18), (-290.2, 18, 4), (-290.2, 2, 4)], "bg")
            for x in range(-250, xs - 30, 50):
                o += hole3(c, (x, 0, 10.2), (0, 0, 1), 4.5)
            return o
        RAW(sc, marks, ((-290.4, -24, -24), (280, 24, 10.4)), -1)
    s, sc = fit(fn, 26, 22, (20, 20, 300, 176), sh_ry=7, sh_k=.46, ret_scene=True)
    cam = sc.cam
    s += arrow3(cam, (xs - 70, 60, 168), (xs + 70, 60, 168), both=True)
    s += arc3(cam, (xs, 0, 78), (0, 0, 1), 24, -70, 40)
    c = cam.xy((xs, 60, 168))
    w = cam.xy((-200, -24, -62))
    s += al(c[0], c[1] - 9, "コラムが移動") + lab(w[0], w[1] + 20, "長尺の押出形材")
    return s
