"""v3 machine-tool atlas drawings, components (team mtc1): ball-screw, linear-guide, slideway, servo-motor,
cnc, atc. Re-registers the same slugs as il_mt.py with the same notes (text, count, order).
Cut-away views show the rolling elements / windings inside; metal parts are banded steel (il3_mtlib)."""
import math
import il_gear as GE
from il_mt import mt, arc_shell
from il3_mtlib import *
from il3_mtlib import _UV, _IDX, _ax_char


# ------------------------------------------------------------------ local helpers
# il3_mtlib.cprism_svg returns a flat bbox when only one end is bevelled (rings[1] is rings[-2]); these local
# versions compute the full bbox so the scene orders bevelled blocks correctly (the shared lib is left as is).
def cprism(sc, axis, t0, L, uv, mat="pt", b0=0.0, b1=0.0, dark=0, bias=0.0, fmat=None, crease=55):
    s, _ = cprism_svg(sc.cam, axis, t0, L, uv, mat, b0, b1, dark, fmat, crease)
    iu, iv, it = _UV[axis][0], _UV[axis][1], _IDX[axis]
    lo, hi = [0.0] * 3, [0.0] * 3
    lo[iu], hi[iu] = min(p[0] for p in uv), max(p[0] for p in uv)
    lo[iv], hi[iv] = min(p[1] for p in uv), max(p[1] for p in uv)
    lo[it], hi[it] = min(t0, t0 + L), max(t0, t0 + L)
    bb = (tuple(lo), tuple(hi))
    sc.add(s, bb, bias)
    return bb


def abox(sc, lo, hi, mat="pt", axis="z", ch=0.0, b=0.0, b0=None, dark=0, bias=0.0, fmat=None):
    iu, iv, it = _UV[axis][0], _UV[axis][1], _IDX[axis]
    return cprism(sc, axis, lo[it], hi[it] - lo[it], rr(lo[iu], lo[iv], hi[iu], hi[iv], ch), mat,
                  b if b0 is None else b0, b, dark, bias, fmat)


def block(sc, x, y, z, sx, sy, sz, mat="pt", ch=0.0, b=2.0, dark=1, bias=0.0, b0=0.0):
    return abox(sc, (x, y, z), (x + sx, y + sy, z + sz), mat, "z", ch, b, b0, dark, bias)


def radial(sc, axis, t0, L, C2, ang, r0, r1, w, mat="w", b=1.0, dark=1, bias=0.0):
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    uv = [(C2[0] + p * c - q * s_, C2[1] + p * s_ + q * c) for p, q in ((r0, -w / 2), (r1, -w / 2), (r1, w / 2), (r0, w / 2))]
    return cprism(sc, axis, t0, L, uv, mat, b, b, dark, bias)


def servo(sc, P0, ax, s=36, L=60, mat="dk", bias=0.0, up="z", flange=True):
    """il3_mtlib.servo with the bbox-correct abox above."""
    a = V(ax)
    c, sg = _ax_char(a)
    u = V(up)
    it = _IDX[c]
    fl = s * .14 if flange else 0

    def seg(t0, ln, half, chm, dk, m_=mat, bb_=1.2):
        lo = list(add3(P0, a, t0))
        hi = list(add3(P0, a, t0 + ln))
        for i in range(3):
            if i != it:
                lo[i], hi[i] = P0[i] - half, P0[i] + half
        abox(sc, tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3)), m_, c, chm, bb_, dark=dk, bias=bias)
    if flange:
        seg(0, fl, s * .6, s * .1, 0)
    seg(fl, L * .66, s / 2, s * .16, 0)
    seg(fl + L * .66, L * .34 - fl, s * .42, s * .14, 1, bb_=2.5)
    cx = add3(P0, a, fl + L * .42)
    lo = add3(add3(cx, u, s / 2), a, -s * .12)
    lo = tuple(lo[i] - (s * .14 if i != it and abs(u[i]) < .5 else 0) for i in range(3))
    hi = add3(add3(cx, u, s / 2 + s * .16), a, s * .12)
    hi = tuple(hi[i] + (s * .14 if i != it and abs(u[i]) < .5 else 0) for i in range(3))
    abox(sc, tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3)), mat, c, 0, .8, dark=0, bias=bias - .5)


def spheres(sc, centers, rb, bias=0.0, cls="ball"):
    """steel balls (class ball = radial gradient with a highlight), drawn far to near as one item."""
    def f(s_):
        cam, o = s_.cam, ""
        R = rb * cam.s
        for C in sorted(centers, key=lambda p: -cam.P(p)[2]):
            x, y = cam.xy(C)
            o += '<circle class="%s" cx="%s" cy="%s" r="%s"/>' % (cls, n(x), n(y), n(R))
        return o
    lo, hi = bbox(centers)
    sc.add(f, (tuple(v - rb for v in lo), tuple(v + rb for v in hi)), bias)


def zsect(sc, rects, z, bias=0.0):
    """section faces on a horizontal cut plane z: rects [(x0, x1, y0, y1, cls)]."""
    def f(s_):
        return "".join(path(P([s_.cam.xy(p) for p in ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))]), c)
                       for x0, x1, y0, y1, c in rects)
    lo = (min(r[0] for r in rects), min(r[2] for r in rects), z - .5)
    hi = (max(r[1] for r in rects), max(r[3] for r in rects), z)
    sc.add(f, (lo, hi), bias)


def ysect(sc, polys, y, bb, bias=0.0):
    """section polygons on the plane y (lists of (x, z) points with a class)."""
    def f(s_):
        return "".join(path(P([s_.cam.xy((x, y, z)) for x, z in pts_]), c) for pts_, c in polys)
    sc.add(f, bb, bias)


def flats_circle(r, zf, seg=32):
    """circle of radius r in (y, z) with flats at z = +-zf (round flange with two flats)."""
    pts_ = []
    for k in range(seg):
        t = 2 * math.pi * k / seg
        y, z = r * math.cos(t), r * math.sin(t)
        if abs(z) > zf:
            z = math.copysign(zf, z)
            y = math.copysign(min(abs(y), r), y) if abs(y) > 1e-6 else y
        pts_.append((y, z))
    out = []
    for p in pts_:
        if not out or abs(out[-1][0] - p[0]) > .01 or abs(out[-1][1] - p[1]) > .01:
            out.append(p)
    return out


# =====================================================================================
@mt("ball-screw", az=-28, el=22)
def _(sc):
    """ball screw with the nut cut open (front-top quarter removed): balls in the helical groove + return tube."""
    LEAD, RS, RB, RP = 20.0, 30, 6.2, 31.5          # lead, shaft radius, ball radius, ball pitch radius
    # ---- supports (fixed side left, free side right): foot + housing + lock nut
    for x0, w in ((-350, 56), (230, 44)):
        block(sc, x0 - 6, -66, -88, w + 12, 132, 20, "pt", ch=4, b=1.5, bias=40)
        block(sc, x0, -52, -68, w, 104, 124, "pt", ch=7, b=2.5, bias=40)
        bolts(sc, [(x0 + w / 2, -48, -68), (x0 + w / 2, 48, -68)], "z", 5, bias=39)
        bolts(sc, [(x0 + w / 2, y, 56) for y in (-30, 30)], "z", 4.4, bias=39)
    MRING(sc, (-294, 0, 0), (1, 0, 0), 30, 18, 12, "dk", seg=28, bands=8, rings=(.5,))      # lock nut
    MRING(sc, (274, 0, 0), (1, 0, 0), 26, 16, 10, "dk", seg=28, bands=8)
    # ---- shaft: journals, threaded part with a helical groove (dark edge + light edge)
    MCYL(sc, (-430, 0, 0), (1, 0, 0), 16, 80, "w", seg=24, bands=8)
    MCYL(sc, (-282, 0, 0), (1, 0, 0), 22, 12, "w", seg=24, bands=8)
    MCYL(sc, (-270, 0, 0), (1, 0, 0), RS, 490, "w", seg=36, bands=14, bias=10)

    def groove(s_):
        return helix(s_.cam, (-270, 0, 0), (1, 0, 0), RS + .2, 490, LEAD, "thread", per=10) + \
            helix(s_.cam, (-270 + LEAD * .32, 0, 0), (1, 0, 0), RS + .2, 490 - LEAD, LEAD, "mgrid", per=10)
    sc.raw(groove, ((-270, -RS - .5, -RS), (220, RS, RS)), bias=9)
    MCYL(sc, (220, 0, 0), (1, 0, 0), 22, 10, "w", seg=24, bands=8)
    # ---- motor + coupling (left)
    MCYL(sc, (-418, 0, 0), (1, 0, 0), 28, 50, "m", seg=28, bands=10, rings=(.18, .5, .82))
    bolts(sc, [(-405, 0, 28), (-381, 0, 28)], "z", 3.4, bias=-1)
    servo(sc, (-424, 0, 0), (-1, 0, 0), 104, 132, up="z")
    # ---- nut: flange (round with two flats), body cut open, wiper seal, return tube
    X0, X1, RO, RI = -44, 96, 54, RS + 3
    cprism(sc, "x", -64, 20, flats_circle(88, 62, 40), "w", 2, 2, dark=1, bias=-5)
    holes(sc, [(-43.8, y, z) for y in (-64, 64) for z in (-30, 30)], (1, 0, 0), 6.5, "dks4", bias=-6)
    xshell(sc, X0, X1 - X0, RO, RI, -90, 90, "w", dark=1, bias=60, seg=20)                  # back half
    xshell(sc, X0, X1 - X0, RO, RI, 180, 270, "w", dark=1, bias=-40, seg=10)               # front-bottom quarter
    xshell(sc, X1, 4, RO - 3, RI, 180, 270, "dk", dark=0, bias=-41, seg=10)
    xshell(sc, X1, 4, RO - 3, RI, -90, 90, "dk", dark=0, bias=59, seg=20)
    ysect(sc, [([(X0, RI), (X1, RI), (X1, RO), (X0, RO)], "cut")], 0, ((X0, -.5, RI), (X1, 0, RO)), bias=50)
    zsect(sc, [(X0, X1, -RO, -RI, "cut")], 0, bias=-39)
    # balls on the helix, visible in the open quarter (angle 90..180 deg from +y toward +z, then front)
    cs = []
    for k in range(-1, 8):
        for j in range(6):
            ph = 90 + j * 18
            x = X0 + 4 + k * LEAD + LEAD * (ph - 90) / 360
            if X0 + RB < x < X1 - RB:
                t = math.radians(ph)
                cs.append((x, RP * math.cos(t), RP * math.sin(t)))
    spheres(sc, cs, RB, bias=-10)
    # return tube over the back of the nut (balls come back through it) + clamp plate
    ty = 18
    for x in (-24, 60):
        MCYL(sc, (x, ty, RO - 6), (0, 0, 1), 6, 18, "w", seg=14, bands=5, spec=False)
    MCYL(sc, (-30, ty, RO + 12), (1, 0, 0), 6, 96, "w", seg=16, bands=6, bias=-1)
    block(sc, 4, ty - 12, RO + 16, 22, 24, 5, "dk", b=.8, dark=0, bias=-2)
    bolts(sc, [(8, ty, RO + 21), (22, ty, RO + 21)], "z", 2.6, bias=-3)
    sc.axis((-40, -110, 128), (130, -110, 128), "直線運動")
    sc.rot((-200, 0, 0), (1, 0, 0), 46, "", 200, 330)
    sc.note((170, -RS, 10), "ねじ軸", "らせん状の溝を持つ軸。モータで回す")
    sc.note((60, -RO, -20), "ナット", "回転を直線運動に変える。テーブルなどに固定する")
    sc.note((40, -22, 24), "ボール（鋼球）", "溝の中を転がり、循環して戻る。摩擦が小さい")
    sc.note((-54, -40, 70), "フランジ", "ナットを可動部に取り付ける")
    sc.note((-322, -52, 30), "サポート軸受", "ねじ軸を両端で支え、軸方向の力を受ける")
    sc.note((-490, -40, 40), "サーボモータ", "カップリングでねじ軸を回す")


# =====================================================================================
@mt("linear-guide", az=-34, el=26)
def _(sc):
    """profile rail + block; the front flange of the block is cut away over its front half to show the
    loaded ball row in the rail groove, the return row and the turn-around in the end plate."""
    sec = [(-22, 0), (22, 0), (22, 46), (16, 52), (-16, 52), (-22, 46)]
    GZ0, GZ1 = 28, 36                                       # side ball groove on the rail

    def rail_seg(x0, x1, bias, hl=True):
        s, _ = cprism_svg(sc.cam, "x", x0, x1 - x0, sec, "w", 0, 1.2 if x1 >= 320 else 0, dark=1)
        bb = ((x0, -22, 0), (x1, 22, 52))
        q = lambda x, z: sc.cam.xy((x, -22.1, z))
        s += path(P([q(x0, GZ0), q(x1, GZ0), q(x1, GZ1), q(x0, GZ1)]), "ws4")
        s += path(P([q(x0, GZ1 + 1.2), q(x1, GZ1 + 1.2)], False), "mgrid")
        c = [sc.cam.xy((x, y, z)) for x, y, z in ((x0, -19, 52.1), (x1, -19, 52.1), (x1, -22.1, 46), (x0, -22.1, 46))]
        s += path(P(c), "ws3")
        sc.add(s, bb, bias)
    # machine bed under the rail (painted casting with a reference shoulder at the back)
    block(sc, -336, -84, -28, 672, 168, 28, "pt", ch=0, b=2, bias=300)
    block(sc, -336, 34, 0, 672, 50, 14, "pt", ch=0, b=1.5, bias=290)
    rail_seg(-320, -70, 200)
    rail_seg(-70, 110, 100)
    rail_seg(110, 320, -100)
    hx = [x for x in range(-290, 321, 60) if not -90 < x < 128]
    hc = [(x, 0, 52.1) for x in hx]
    holes(sc, hc, "z", 8, "dks4", bias=-101)
    holes(sc, hc, "z", 5.6, "ws3", bias=-102)
    holes(sc, hc, "z", 2.2, "dks4", bias=-103)

    # block body, end plates, seals: top part + legs (front leg only where not cut)
    def part(x0, x1, mat, front=True, b=0.0, bias=0.0):
        abox(sc, (x0, -60, 58), (x1, 60, 90), mat, "x", 0, b, dark=1, bias=bias)
        abox(sc, (x0, 26, 16), (x1, 60, 58), mat, "x", 0, b, dark=1, bias=bias + 1)
        if front:
            abox(sc, (x0, -60, 16), (x1, -26, 58), mat, "x", 0, b, dark=1, bias=bias)
    part(-68, -62, "dk", bias=50)
    part(-62, -50, "m", bias=50)
    part(-50, 90, "w", front=False, bias=50)
    abox(sc, (-50, -60, 16), (10, -26, 58), "w", "x", 0, 0, dark=1, bias=40)
    part(90, 102, "m", front=False, bias=50)
    part(102, 108, "dk", front=False, bias=50)
    # cut face of the front flange: return hole and groove
    def cutf(s_):
        q = lambda y, z: s_.cam.xy((10.1, y, z))
        o = path(P([q(-60, 16), q(-26, 16), q(-26, 58), q(-60, 58)]), "cut")
        o += path(P(circ3(s_.cam, (10.2, -46, 37), (1, 0, 0), 6.2, 14)), "dks4")
        return o
    sc.add(cutf, ((10, -60, 16), (10.2, -26, 58)), bias=39)
    holes(sc, [(x, y, 90.1) for x in (-26, 66) for y in (-38, 38)], "z", 5.5, "ws4", bias=-1)
    holes(sc, [(x, y, 90.1) for x in (-26, 66) for y in (-38, 38)], "z", 3.6, "dks4", bias=-2)
    MCYL(sc, (108, 0, 74), (1, 0, 0), 5, 4, "gw", seg=6, bands=6, spec=False)
    MCYL(sc, (112, 0, 74), (1, 0, 0), 3, 9, "gw", seg=14, bands=5)
    # balls: loaded row in the groove, return row, turn-around in the end plate
    RB = 5.0
    cs = [(x, -23, 32) for x in range(16, 90, 10)] + [(x, -46, 37) for x in range(16, 90, 10)]
    for k in range(1, 6):
        t = math.pi * k / 6
        cs.append((91 + 11.5 * math.sin(t), -34.5 + 11.5 * math.cos(t), 34.5))
    spheres(sc, cs, RB, bias=-5)
    sc.axis((-40, -80, 112), (120, -80, 112), "直線運動")
    sc.note((250, 0, 40), "レール", "機械のベッドやコラムにボルトで固定する")
    sc.note((-20, -60, 84), "ブロック（キャリッジ）", "テーブルなどを載せてレールの上を動く")
    sc.note((50, -46, 40), "転動体（ボール）", "ブロック内を循環し、転がって摩擦を減らす")
    sc.note((108, 30, 17), "エンドシール", "切りくずやクーラントの侵入を防ぐ")
    sc.note((-230, 0, 52), "取付穴", "レールを固定するボルト穴")


# =====================================================================================
@mt("slideway", az=-30, el=26)
def _(sc):
    """flat + V slideway, bed and carriage sliced at x = XC (hatched sections: hollow cast bed, slide liners,
    T-slots); scraping marks on the exposed ways."""
    XB, XC, XT = -340, 140, -110                           # bed start, common cut plane, carriage start
    LB, LT = XC - XB, XC - XT
    # bed: base, flat way (rib + machined strip), V way (rib + machined V)
    cprism(sc, "x", XB, LB, [(-200, 0), (200, 0), (200, 80), (-194, 80), (-200, 74)], "pt", 0, 0, dark=1, bias=300)
    cprism(sc, "x", XB, LB, rr(-160, 80, -96, 100), "pt", 0, 0, dark=1, bias=250)
    cprism(sc, "x", XB, LB, rr(-160, 100, -96, 104), "w", 0, 0, dark=1, bias=240)
    cprism(sc, "x", XB, LB, rr(80, 80, 160, 92), "pt", 0, 0, dark=1, bias=250)
    cprism(sc, "x", XB, LB, [(88, 92), (152, 92), (120, 124)], "w", 0, 0, dark=1, bias=240)
    # scraping marks (flaking) on the exposed flat way and the front V face
    def scrape(s_):
        cam, o = s_.cam, ""
        for i in range(15):
            x = XB + 10 + i * 14.6
            for j in range(4):
                y = -154 + j * 16 + (i % 2) * 4
                d = 1 if (i + j) % 2 else -1
                a, b, c = cam.xy((x - 4, y - 4 * d, 104.1)), cam.xy((x + 1, y + 3 * d, 104.1)), cam.xy((x + 4, y + 4 * d, 104.1))
                o += "M%s %sQ%s %s %s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]))
            for j in range(3):
                u = .2 + j * .28 + (i % 2) * .08
                y, z = 88 + 32 * u - .1, 92 + 32 * u + .1
                d = 1 if (i + j) % 2 else -1
                a, b, c = cam.xy((x - 4, y - 3 * d, z - 3 * d)), cam.xy((x + 1, y + 2 * d, z + 2 * d)), cam.xy((x + 4, y + 3 * d, z + 3 * d))
                o += "M%s %sQ%s %s %s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]))
        return path(o, "scr")
    sc.raw(scrape, ((XB, -160, 104), (XT - 6, -96, 104.5)), bias=230)
    # carriage (table): two convex halves around the V groove, slide liners under it
    VA = 129.6
    cprism(sc, "x", XT, LT, [(-180, 110), (100.4, 110), (120, VA), (120, 190), (-180, 190)], "pt", 0, 0, dark=1, bias=100)
    cprism(sc, "x", XT, LT, [(120, VA), (139.6, 110), (214, 110), (214, 190), (120, 190)], "pt", 0, 0, dark=1, bias=100)
    cprism(sc, "x", XT, LT, rr(-160, 104, -96, 110), "dk", 0, 0, dark=0, bias=110)
    cprism(sc, "x", XT, LT, [(103.2, 107.2), (120, 124), (120, VA), (100.4, 110)], "dk", 0, 0, dark=0, bias=110)
    cprism(sc, "x", XT, LT, [(136.8, 107.2), (120, 124), (120, VA), (139.6, 110)], "dk", 0, 0, dark=0, bias=110)
    TS = (-110, 0, 110)                                    # T-slots on the table top

    def tslots(s_):
        o = ""
        for y in TS:
            o += P([s_.cam.xy(p) for p in ((XT, y - 10, 190.1), (XC, y - 10, 190.1), (XC, y + 10, 190.1), (XT, y + 10, 190.1))])
        return path(o, "dks4")
    sc.raw(tslots, ((XT, -180, 190), (XC, 214, 190.5)), bias=90)
    MCYL(sc, (-40, -180, 150), (0, -1, 0), 5, 4, "gw", seg=6, bands=6, spec=False)
    MCYL(sc, (-40, -184, 150), (0, -1, 0), 3, 9, "gw", seg=14, bands=5)
    bolts(sc, [(x, -180, 124) for x in (-90, 10, 110)], (0, -1, 0), 4.5, bias=-1)

    # sections on the cut plane x = XC
    def secs(s_):
        q = lambda pts_: P([s_.cam.xy((XC + .1, y, z)) for y, z in pts_])
        bed = [(-200, 0), (200, 0), (200, 80), (160, 80), (160, 92), (152, 92), (120, 124), (88, 92), (80, 92), (80, 80),
               (-96, 80), (-96, 104), (-160, 104), (-160, 80), (-194, 80), (-200, 74)]
        o = path(q(bed), "cut") + path(q(rr(-178, 16, -16, 62, 6)) + q(rr(16, 16, 178, 62, 6)), "dks4")
        car = [(-180, 110), (100.4, 110), (120, VA), (139.6, 110), (214, 110), (214, 190), (-180, 190)]
        o += path(q(car), "cut")
        ts = ""
        for y in TS:
            ts += q([(y - 10, 190), (y - 10, 178), (y - 20, 178), (y - 20, 164), (y + 20, 164), (y + 20, 178), (y + 10, 178), (y + 10, 190)])
        o += path(ts, "bg")
        o += path(q(rr(-160, 104, -96, 110)) + q([(103.2, 107.2), (120, 124), (136.8, 107.2), (139.6, 110), (120, VA), (100.4, 110)]), "dks2")
        return o
    sc.add(secs, ((XC, -200, 0), (XC + .2, 214, 190)), bias=-50)
    sc.axis((-100, -230, 222), (100, -230, 222), "往復")
    sc.note((-130, -160, 82), "案内面（平形）", "平らな面で荷重を受ける")
    sc.note((XC, 120, 120), "案内面（V形）", "V字の面で横方向の位置を決める")
    sc.note((-40, -180, 176), "テーブル（往復台）", "案内面の上を滑って動く")
    sc.note((-60, -160, 108), "すべり材", "摩擦が小さく、焼付きにくい樹脂シート")
    sc.note((-300, -110, 104), "きさげ模様", "手作業で削った細かなくぼみ。油をため、当たりを整える")
    sc.note((-300, -200, 36), "ベッド", "案内面を一体で削り出した鋳物")


# =====================================================================================
def rsect(sc, feats, bias_y, bias_z, xr):
    """radial section features [(x0, x1, r0, r1, cls)] of a body of revolution about the x axis, drawn on the
    two faces of a front-top quarter cut: the plane y=0 (z = r) and the plane z=0 (y = -r)."""
    def mk(f3):
        def f(s_):
            o = ""
            for x0, x1, r0, r1, c in feats:
                if c == "ball":
                    rc, rb = (r0 + r1) / 2, (r1 - r0) / 2
                    o += path(P([s_.cam.xy(f3((x0 + x1) / 2 + rb * math.cos(t), rc + rb * math.sin(t)))
                                 for t in [2 * math.pi * k / 14 for k in range(14)]]), "ball")
                else:
                    o += path(P([s_.cam.xy(f3(x, r)) for x, r in ((x0, r0), (x1, r0), (x1, r1), (x0, r1))]), c)
            return o
        return f
    R = max(f[3] for f in feats)
    sc.add(mk(lambda x, r: (x, -.1, r)), ((xr[0], -.5, 0), (xr[1], 0, R)), bias_y)
    sc.add(mk(lambda x, r: (x, -r, .1)), ((xr[0], -R, 0), (xr[1], 0, .5)), bias_z)


def qbox(sc, x0, L, h, c, mat="dk", bias_back=100, bias_front=-100, dark=1):
    """square-section body along x (half width h, corner chamfer c) with its front-top quarter removed:
    back half (y>0) + front-bottom quarter (y<0, z<0)."""
    cprism(sc, "x", x0, L, [(0, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (0, h)], mat, 0, 0, dark=dark, bias=bias_back)
    cprism(sc, "x", x0, L, [(-h, 0), (-h, -h + c), (-h + c, -h), (0, -h), (0, 0)], mat, 0, 0, dark=dark, bias=bias_front)


@mt("servo-motor", az=-30, el=22)
def _(sc):
    """AC servo motor cut open (front-top quarter): stator core + windings, magnet rotor, bearings, encoder disc;
    linear motor on the right: magnet track + forcer with its coils exposed at the front."""
    # ---- rotary servo motor, axis x, output shaft to the left
    xshell(sc, -258, 6, 40, 14, -90, 90, "w", dark=1, bias=130, seg=14)
    xshell(sc, -258, 6, 40, 14, 180, 270, "w", dark=1, bias=-130, seg=6)
    qbox(sc, -252, 16, 64, 6, "dk", 120, -120)                 # square flange
    qbox(sc, -236, 158, 56, 10, "dk", 110, -110)               # frame (incl. rear bracket)
    qbox(sc, -78, 48, 48, 8, "dk", 100, -100)                  # encoder cover
    F = [(-258, -252, 14, 40, "cut"), (-252, -236, 18, 64, "cut"),
         (-250, -238, 17, 23, "dks4"), (-250, -238, 23, 26, "cut"), (-250, -238, 14, 17, "cut"), (-247, -241, 17, 23, "ball"),
         (-236, -78, 51, 56, "cut"), (-236, -92, 14, 51, "dks4"),
         (-206, -114, 37, 51, "ms2"), (-206, -114, 39, 45, "cus2"),
         (-226, -206, 39, 49, "cus1"), (-114, -96, 39, 49, "cus1"),
         (-92, -78, 24, 51, "cut"), (-90, -80, 17, 21, "dks4"), (-90, -80, 21, 24, "cut"), (-90, -80, 14, 17, "cut"), (-88, -82, 17, 21, "ball"),
         (-78, -34, 44, 48, "cut"), (-34, -30, 0, 44, "cut"), (-78, -34, 14, 44, "dks4"), (-44, -40, 10, 38, "pcb")]
    rsect(sc, F, 90, -140, (-258, -30))

    def lams(s_):
        o = ""
        for k in range(1, 15):
            x = -206 + k * 92 / 15
            o += P([s_.cam.xy((x, -.2, 45.5)), s_.cam.xy((x, -.2, 51))], False) + P([s_.cam.xy((x, -45.5, .2)), s_.cam.xy((x, -51, .2))], False)
        return path(o, "gr")
    sc.add(lams, ((-206, -51, 0), (-114, -.2, 51)), -141)
    # shaft with key, magnet rotor, encoder disc (front-top quarter), read head
    MCYL(sc, (-306, 0, 0), (1, 0, 0), 14, 268, "w", seg=24, bands=10, rings=(.17,))
    abox(sc, (-300, -4, 11), (-272, 4, 16.5), "dk", "x", 0, 1, dark=0, bias=-2)
    MCYL(sc, (-206, 0, 0), (1, 0, 0), 35, 92, "dk", seg=32, bands=12, dark=0, bias=-5)

    def poles(s_):
        o = ""
        for k in range(16):
            t = 2 * math.pi * (k + .5) / 16
            nr = (0, math.cos(t), math.sin(t))
            if GE._dot(nr, s_.cam.D) < -.05:
                o += P([s_.cam.xy((-205, 35.2 * nr[1], 35.2 * nr[2])), s_.cam.xy((-115, 35.2 * nr[1], 35.2 * nr[2]))], False)
        return path(o, "mgrid")
    sc.add(poles, ((-206, -35.5, -35), (-114, 0, 35)), -6)
    DX = -58

    def disc(s_):
        cam = s_.cam
        q = [cam.xy((DX, 0, 0))] + [cam.xy((DX, -31 * math.cos(t), 31 * math.sin(t))) for t in [math.radians(90 - 90 * k / 12) for k in range(13)]]
        o = path(P(q), "ws2")
        tk = ""
        for k in range(25):
            t = math.radians(90 - 90 * k / 24)
            tk += P([cam.xy((DX + .1, -26 * math.cos(t), 26 * math.sin(t))), cam.xy((DX + .1, -30 * math.cos(t), 30 * math.sin(t)))], False)
        return o + path(tk, "thread") + path(P(circ3(cam, (DX + .2, 0, 0), (1, 0, 0), 15, 16)), "dks2")
    sc.add(disc, ((DX, -31, 0), (DX + .3, 0, 31)), -20)
    abox(sc, (DX + 1, -26, 16), (DX + 9, -16, 30), "dk", "x", 0, .6, dark=0, bias=-21)
    # connectors on top, name plate on the front
    block(sc, -152, 8, 56, 34, 36, 9, "dk", ch=3, b=1, dark=0, bias=50)
    MCYL(sc, (-135, 26, 65), (0, 0, 1), 12, 14, "m", seg=20, bands=8, rings=(.4,), bias=49)
    MCYL(sc, (-56, 22, 48), (0, 0, 1), 8, 12, "m", seg=16, bands=6, rings=(.4,), bias=49)

    def plate(s_):
        q = lambda x, z: s_.cam.xy((x, -56.2, z))
        return path(P([q(-212, -44), q(-130, -44), q(-130, -16), q(-212, -16)]), "ws1") + \
            path(P([q(-206, -24), q(-160, -24)], False) + P([q(-206, -31), q(-150, -31)], False) + P([q(-206, -38), q(-170, -38)], False), "gr")
    sc.add(plate, ((-212, -56.5, -44), (-130, -56.2, -16)), -150)
    # ---- linear motor: magnet track + forcer (coils exposed at the front)
    block(sc, 60, -64, -88, 320, 128, 14, "m", b=1.5, dark=1, bias=60)
    for k in range(10):
        block(sc, 64 + 32 * k, -52, -74, 28, 104, 8, "dk" if k % 2 else "m", b=.8, dark=0, bias=40)
    block(sc, 150, -38, -58, 168, 84, 17, "dk", b=0, dark=0, bias=20)            # iron core behind the coils
    for k in range(6):
        block(sc, 154 + 27 * k, -46, -58, 23, 80, 17, "cu", b=1, dark=0, bias=10)

    def turns(s_):
        o = ""
        for k in range(6):
            for z in (-54.5, -51, -47.5, -44):
                o += P([s_.cam.xy((155 + 27 * k, -46.1, z)), s_.cam.xy((176 + 27 * k, -46.1, z))], False)
        return path(o, "gr")
    sc.add(turns, ((154, -46.2, -58), (312, -46.1, -41)), 9)
    for x0 in (146, 318):
        block(sc, x0, -54, -58, 4, 108, 18, "al", b=0, dark=1, bias=5)
    block(sc, 146, -54, -40, 176, 108, 14, "al", b=1.5, dark=1, bias=0)
    for k in range(9):
        block(sc, 156, -48 + 12 * k - 2, -26, 130, 4, 12, "al", b=0, dark=1, bias=-1 - k * .01)
    MCYL(sc, (304, 24, -26), (0, 0, 1), 7, 12, "dk", seg=16, bands=6)

    def cable(s_):
        a, b, c = s_.cam.xy((304, 24, -14)), s_.cam.xy((304, 24, 16)), s_.cam.xy((380, 24, 30))
        return '<path class="cable" d="M%s %sQ%s %s %s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]))
    sc.add(cable, ((304, 24, -14), (380, 24, 30)), -3)
    sc.axis((150, -100, 0), (318, -100, 0), "直線運動")
    sc.note((-170, 30, 56), "サーボモータ", "回転角と速度を正確に制御するモータ")
    sc.note((DX, -18, 22), "エンコーダ", "回転位置を検出してNCに返す")
    sc.note((-296, -10, 8), "出力軸", "カップリングでボールねじや主軸につなぐ")
    sc.note((220, -46, -50), "リニアモータ（可動子）", "コイルに電流を流して直接まっすぐ動く")
    sc.note((350, -52, -70), "磁石（固定子）", "N極とS極を交互に並べた板")


# =====================================================================================
@mt("cnc", az=-18, el=10)
def _(sc):
    """CNC operation panel: display unit (bezel, screen with position/program/tool-path windows, soft keys,
    key pad) over the machine operator panel (cycle buttons, override dials, MPG, emergency stop)."""
    block(sc, -200, 0, 0, 400, 60, 300, "dk", ch=6, b=2.5, dark=0, bias=100)
    abox(sc, (-190, -4, 112), (48, 0, 290), "m", "y", 0, 0, dark=1, bias=60)           # screen bezel

    def face(s_):
        cam = s_.cam

        def q(x0, z0, x1, z1, y=-4.2):
            return P([cam.xy((x0, y, z0)), cam.xy((x1, y, z0)), cam.xy((x1, y, z1)), cam.xy((x0, y, z1))])
        o = path(q(-180, 132, 38, 282), "scrn")
        o += path(q(-176, 270, 34, 278), "scrl")
        bars = ""
        for i in range(3):                                   # position read-out (axis + value)
            z = 236 - i * 26
            bars += q(-172, z, -160, z + 16) + q(-152, z, -86, z + 16)
        for i in range(8):                                   # program list
            z = 258 - i * 9
            bars += q(-70, z, -70 + (60, 42, 70, 36, 54, 66, 30, 48)[i], z + 4)
        bars += q(-172, 142, 34, 150)
        o += path(bars, "scrl")
        g = [cam.xy((x, -4.3, z)) for x, z in ((-72, 160), (-50, 160), (-50, 182), (-20, 182), (-6, 196), (-6, 172), (28, 172))]
        o += path(q(-74, 156, 34, 202), "scrg") + path(P(g, False), "scrg")
        ks = ""
        for c in range(8):                                   # soft keys under the screen
            ks += q(-176 + c * 27, 116, -156 + c * 27, 126, -4.2)
        for r in range(5):                                   # key pad
            for c in range(5):
                ks += q(64 + c * 26, 268 - r * 26, 84 + c * 26, 284 - r * 26, -.2)
        for c in range(5):                                   # mode / jog keys
            ks += q(-180 + c * 28, 70, -160 + c * 28, 86, -.2)
        o += path(ks, "key")
        cb = q(-180, 28, -144, 56, -.2) + q(-136, 28, -100, 56, -.2) + q(-92, 28, -56, 56, -.2)
        o += path(cb, "kbtn") + path(q(-176, 50, -148, 53, -.3), "scrg") + path(q(-132, 50, -104, 53, -.3), "scrl")
        o += path(q(-200, 104, 200, 104.6, -.2), "mgrid")
        # dial scales printed around the override knobs
        tk = ""
        for cx in (70, 150):
            for k in range(11):
                t = math.radians(225 - 27 * k)
                tk += P([cam.xy((cx + 22 * math.cos(t), -.3, 120 + 22 * math.sin(t))), cam.xy((cx + 27 * math.cos(t), -.3, 120 + 27 * math.sin(t)))], False)
        for k in range(40):
            t = 2 * math.pi * k / 40
            tk += P([cam.xy((80 + 34 * math.cos(t), -.3, 46 + 34 * math.sin(t))), cam.xy((80 + 38 * math.cos(t), -.3, 46 + 38 * math.sin(t)))], False)
        o += path(tk, "mgrid")
        c = cam.xy((164, -.4, 44))
        o += '<circle class="estop" cx="%s" cy="%s" r="%s"/>' % (n(c[0]), n(c[1]), n(21 * cam.s))
        return o
    sc.add(face, ((-200, -4.3, 0), (200, -.1, 300)), 50)
    bolts(sc, [(x, 0, z) for x in (-190, 190) for z in (112, 290)], (0, -1, 0), 3.2, bias=40)
    for cx in (70, 150):                                     # override dials
        MCYL(sc, (cx, 0, 120), (0, -1, 0), 17, 4, "dk", seg=24, bands=8, dark=0, spec=False, bias=30)
        MCYL(sc, (cx, -4, 120), (0, -1, 0), 13, 12, "m", seg=24, bands=10, bias=29)
        abox(sc, (cx - 1.6, -16.4, 120), (cx + 1.6, -16, 131), "dk", "y", 0, 0, dark=0, bias=28)
    MCYL(sc, (80, 0, 46), (0, -1, 0), 30, 6, "dk", seg=36, bands=12, dark=0, bias=30)    # MPG
    MCYL(sc, (80, -6, 46), (0, -1, 0), 24, 8, "m", seg=36, bands=12, rings=(.5,), bias=29)
    MCYL(sc, (96, -14, 54), (0, -1, 0), 5, 14, "dk", seg=14, bands=6, dark=0, bias=20)
    MCYL(sc, (164, -.4, 44), (0, -1, 0), 14, 9, "h", seg=24, bands=8, bias=25)           # e-stop mushroom
    sc.note((-70, -4, 210), "表示画面", "プログラム・座標・負荷などを表示する")
    sc.note((115, 0, 230), "操作キー", "プログラムの入力・編集をする")
    sc.note((80, -14, 52), "手動パルス発生器", "ハンドルを回して軸を少しずつ動かす")
    sc.note((164, -9, 38), "非常停止", "押すと機械をすぐに止める")
    sc.note((-118, 0, 42), "運転ボタン", "自動運転の起動・停止、モード切替")
    sc.note((150, -16, 124), "オーバライド", "送り速度や主軸回転を運転中に調整する")


# =====================================================================================
def holder_v(sc, x, y, zf, tool=60, bias=0.0, flutes=True):
    """BT tool holder hanging vertically: V-groove flange top at zf, collet body, nut, end mill below."""
    MCYL(sc, (x, y, zf), (0, 0, -1), 30, 14, "w", seg=28, bands=10, rings=(.5,), bias=bias)
    MCYL(sc, (x, y, zf - 14), (0, 0, -1), 21, 26, "w", r1=16, seg=24, bands=8, dark=0, bias=bias)
    MCYL(sc, (x, y, zf - 40), (0, 0, -1), 18, 10, "w", seg=20, bands=6, bias=bias)
    MCYL(sc, (x, y, zf - 50), (0, 0, -1), 8, tool, "t", seg=14, bands=5, dark=0, bias=bias)
    if flutes:
        sc.raw(lambda s_: helix(s_.cam, (x, y, zf - 50 - tool), (0, 0, 1), 8, tool * .7, 24, "hobt", per=12),
               ((x - 8, y - 8.5, zf - 50 - tool), (x + 8, y - 8, zf - 50 - tool * .3)), bias - .5)


def claw(sc, C, z0, h, a_open, bias_back, bias_front, mat="m"):
    """C-shaped gripper (r 31..41) around a vertical holder at C, open toward angle a_open (deg, 0 = +x)."""
    for k in range(4):
        a0 = a_open + 30 + k * 75
        a1 = a0 + 75
        pts_ = [(C[0] + r * math.cos(math.radians(a)), C[1] + r * math.sin(math.radians(a)))
                for r, aa in ((41, (a0, a1)), (31, (a1, a0))) for a in [aa[0] + (aa[1] - aa[0]) * j / 3 for j in range(4)]]
        back = math.sin(math.radians((a0 + a1) / 2)) > 0
        cprism(sc, "z", z0, h, pts_, mat, 0, 0, dark=1, bias=bias_back if back else bias_front)


@mt("atc", az=-30, el=20)
def _(sc):
    """automatic tool changer: drum magazine with pots (the change pot swung down), double arm gripping the
    holders in the pot and in the spindle, spindle head with its nose."""
    ZC, RM, XD = 330, 120, -226
    # magazine disc + hub + pots (horizontal, +x), holders and tools in them
    MCYL(sc, (XD - 24, 0, ZC), (1, 0, 0), 150, 24, "pt", seg=56, bands=16, rings=(), bias=300)
    MCYL(sc, (XD, 0, ZC), (1, 0, 0), 44, 12, "dk", seg=28, bands=10, dark=0, bias=290)
    bolts(sc, ring_pts((XD + 12, 0, ZC), (1, 0, 0), 32, 6), (1, 0, 0), 3.2, bias=289)
    for k in range(12):
        t = math.radians(30 * k)
        if k == 9:
            continue                                         # the change pot is swung down
        y, z = RM * math.cos(t), ZC + RM * math.sin(t)
        b = 250 - 10 * math.cos(t)
        MCYL(sc, (XD, y, z), (1, 0, 0), 18, 30, "dk", seg=12, bands=4, dark=0, spec=False, bias=b)
        MCYL(sc, (XD + 30, y, z), (1, 0, 0), 15, 8, "w", seg=12, bands=4, spec=False, bias=b - 1)
        MCYL(sc, (XD + 38, y, z), (1, 0, 0), 11, 14, "w", r1=9, seg=10, bands=3, spec=False, bias=b - 2)
        if k not in (2, 3, 4):
            MCYL(sc, (XD + 52, y, z), (1, 0, 0), 5.5, 36 if k % 2 else 26, "t", seg=8, bands=3, spec=False, dark=0, bias=b - 3)
    # change pot swung down (hinge link to the rim) holding a holder vertically
    XP = -160
    abox(sc, (XD, -10, 196), (XP - 10, 10, 214), "dk", "x", 0, 1, dark=0, bias=150)
    MCYL(sc, (XP, 0, 230), (0, 0, -1), 22, 58, "dk", seg=24, bands=8, dark=0, rings=(.2,), bias=140)
    # spindle head (casting, name band) + quill + nose
    XS = 100
    block(sc, 30, -60, 196, 170, 170, 150, "pt", ch=10, b=3, bias=200)
    block(sc, 44, -61.5, 316, 142, 1.5, 16, "dk", b=0, dark=0, bias=199)
    MCYL(sc, (XS, 0, 196), (0, 0, -1), 54, 18, "pt", seg=36, bands=12, bias=120)
    MCYL(sc, (XS, 0, 178), (0, 0, -1), 42, 12, "w", seg=32, bands=12, rings=(.5,), bias=119)
    # holders gripped by the arm (in the spindle and in the change pot)
    ZF = 166
    holder_v(sc, XS, 0, ZF, 52, bias=0)
    holder_v(sc, XP, 0, ZF, 52, bias=0)
    # ATC unit: cam box above the arm, drive motor on top, hub shaft, double arm with C grippers
    XA = (XS + XP) / 2
    block(sc, XA - 48, -42, 236, 96, 96, 84, "pt", ch=6, b=2.5, bias=180)
    servo(sc, (XA, 6, 320), "z", 44, 50, up=(0, -1, 0))
    MCYL(sc, (XA, 0, 236), (0, 0, -1), 14, 50, "w", seg=20, bands=8, bias=60)
    cprism(sc, "x", XP + 41, XS - XP - 82, rr(-15, ZF - 18, 15, ZF, 3), "m", 0, 0, dark=1, bias=40)
    MCYL(sc, (XA, 0, ZF + 6), (0, 0, -1), 26, 28, "dk", seg=28, bands=10, dark=0, rings=(.5,), bias=30)
    claw(sc, (XS, 0), ZF - 15, 15, 270, 10, -10)
    claw(sc, (XP, 0), ZF - 15, 15, 270, 10, -10)
    sc.rot((XA, 0, ZF - 4), (0, 0, 1), 92, "", 205, 330)
    sc.note((XD, -40, ZC + 145), "工具マガジン", "多数の工具をポットに収納して回る")
    sc.note((XD + 14, -RM * .87, ZC - 60), "工具ポット", "ツールホルダを1本ずつ保持する")
    sc.note((XA - 50, -13, ZF - 4), "交換アーム", "両端で新旧の工具をつかみ、回って入れ替える")
    sc.note((XS + 30, -40, 190), "主軸", "交換時は決まった向きで止まる（オリエンテーション）")
    sc.note((XS + 12, -18, ZF - 30), "ツールホルダ", "工具を保持し、主軸テーパに入る")
