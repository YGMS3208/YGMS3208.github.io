"""v3 (shaded 3D) detail + process drawings for chassis.alarm, chassis.hubbearing, chassis.disc (ops only),
chassis.caliper and chassis.hu. Replaces the flat drawings of il_d_chassis / il_d_ev via @dpart."""
import math
import re
from contextlib import contextmanager
import il_gear as GE
from il_base import *
from il_detail import title, bal, tol, fin, mf, cl, hid, loc
from il_pictos import chart
from il_dmap import dpart
import il3_lib as L
from il3_lib import compact, hull, banded, arc, circ3, hole3, P, arc3, arrow3
import il3_chassis as C3
from il3_chassis import pz, py, px, cy, ring, disc3, add, mul, hexagon
import il3_pilot as PI3
import il_d_chassis as OC
import il_d_ev as OV

PI = math.pi
X_, Y_, Z_ = (1, 0, 0), (0, 1, 0), (0, 0, 1)


# =====================================================================================
# common helpers
# =====================================================================================
_D = re.compile(r' d="([^"]*)"')
_TOK = re.compile(r'([MLZ])(?:(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?))?\s*')


def _f(v):
    """tenths (int) -> shortest decimal text."""
    s = "-" if v < 0 else ""
    v = abs(v)
    a, b = divmod(v, 10)
    if b == 0:
        return s + str(a)
    return s + (str(a) if a else "") + "." + str(b)


def _rel(m):
    d = m.group(1)
    toks = _TOK.findall(d)
    if "".join(t[0] + (t[1] + " " + t[2] if t[1] else "") for t in toks).replace(" ", "") != d.replace(" ", ""):
        return m.group(0)
    out, cx, cy_, sx, sy, last = [], 0, 0, 0, 0, ""
    for c, a, b in toks:
        if c == "Z":
            out.append("Z")
            cx, cy_, last = sx, sy, "Z"
            continue
        X, Y = int(round(float(a) * 10)), int(round(float(b) * 10))
        if c == "M":
            out.append("M" + _f(X) + " " + _f(Y))
            sx, sy, last = X, Y, "M"
        else:
            dx, dy = _f(X - cx), _f(Y - cy_)
            pre = "l" if last != "l" else ("" if dx.startswith("-") else " ")
            out.append(pre + dx + ("" if dy.startswith("-") else " ") + dy)
            last = "l"
        cx, cy_ = X, Y
    return ' d="' + "".join(out) + '"'


def rel(svg):
    """rewrite plain M/L/Z path data as relative moves (same drawing, ~40% fewer bytes)."""
    return _D.sub(_rel, svg)


def hot(svg):
    """workpiece material classes -> glowing hot."""
    svg = re.sub(r'class="w(s[1-4])"', r'class="h\1"', svg)
    return re.sub(r'class="w[23]?"', 'class="h"', svg)


@contextmanager
def turned(deg):
    """view the model from az+deg while keeping the light fixed relative to the viewer."""
    L0 = GE.LIGHT
    a = math.radians(-deg)
    GE.LIGHT = (L0[0] * math.cos(a) - L0[1] * math.sin(a), L0[0] * math.sin(a) + L0[1] * math.cos(a), L0[2])
    try:
        yield
    finally:
        GE.LIGHT = L0


def place(fn, az, el, area=(30, 38, 450, 266), **kw):
    """fit fn(scene) into area of the 480x300 canvas -> (svg, cam)."""
    s, sc = L.fit(fn, az, el, area, ret_scene=True, **kw)
    return s, sc.cam


def grab(mod, name, *a, **kw):
    """take the inner fn(scene) of an il3 part drawing (whose last step is fit(fn, az, el, ...))."""
    cap = {}
    old = mod.fit

    def f(fn, az, el, *aa, **kk):
        cap.update(fn=fn, az=az, el=el)
        return ""
    mod.fit = f
    try:
        getattr(mod, name)(*a, **kw)
    finally:
        mod.fit = old
    return cap["fn"], cap["az"], cap["el"]


def box(cam, x, y, z, sx, sy, sz, mat="m", **kw):
    return pz(cam, z, sz, [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)], mat, **kw)


def faces(cam, x, y, z, sx, sy, sz, cls="sand"):
    """box drawn with one flat class on its visible faces (sand mould, tank)."""
    V = [(x + i * sx, y + j * sy, z + k * sz) for k in (0, 1) for j in (0, 1) for i in (0, 1)]
    F = [((0, 1, 3, 2), (0, 0, -1)), ((4, 5, 7, 6), (0, 0, 1)), ((0, 1, 5, 4), (0, -1, 0)), ((2, 3, 7, 6), (0, 1, 0)),
         ((0, 2, 6, 4), (-1, 0, 0)), ((1, 3, 7, 5), (1, 0, 0))]
    o = ""
    for idx, nrm in F:
        if GE._dot(nrm, cam.D) < 0:
            o += path(P([cam.xy(V[i]) for i in idx]), cls)
    return o


def ring3(cam, C, A, r, c="mf", seg=32, a0=0, a1=360):
    """3D circle (or arc, degrees in GE.frame(A)) as an open/closed stroked path."""
    E1, E2, _ = GE.frame(A)
    full = a1 - a0 >= 360
    k = seg if full else seg + 1
    pts = [cam.xy(tuple(C[i] + r * (math.cos(math.radians(a0 + (a1 - a0) * j / seg)) * E1[i] +
                                     math.sin(math.radians(a0 + (a1 - a0) * j / seg)) * E2[i]) for i in range(3))) for j in range(k)]
    return path(P(pts, full), c)


def vis_arc(cam, C, A, r, c="mf", seg=36, front=True):
    """the half of a 3D circle nearer to (front) or farther from the viewer."""
    E1, E2, _ = GE.frame(A)
    best, a0 = None, 0
    for j in range(72):
        a = j * 5
        p = tuple(C[i] + r * (math.cos(math.radians(a)) * E1[i] + math.sin(math.radians(a)) * E2[i]) for i in range(3))
        d = cam.P(p)[2]
        if best is None or (d < best if front else d > best):
            best, a0 = d, a
    return ring3(cam, C, A, r, c, seg // 2, a0 - 90, a0 + 90)


def drill(cam, tip, A, d=8, L=60, mat="t", hold=True):
    """twist drill / boring bar: cone tip at `tip`, body along A (A points from tip to shank)."""
    a = GE._norm(A)
    o = cy(cam, add(tip, mul(a, d * .55)), a, d / 2, L - d * .55, mat, seg=14, bands=5)
    o = cy(cam, tip, a, .4, d * .55, mat, seg=14, bands=5, r1=d / 2) + o if GE._dot(a, cam.D) < 0 else o + cy(cam, tip, a, .4, d * .55, mat, seg=14, bands=5, r1=d / 2)
    if hold:
        o += cy(cam, add(tip, mul(a, L)), a, d * 1.4, 30, "m", seg=20, bands=6)
    return o


def spindle(cam, p, A, r=22, h=40):
    return cy(cam, p, A, r, h, "m", seg=24, bands=8, dark=.3)


def label(cam, p, t, dx=0, dy=0, anchor="middle"):
    x, y = cam.xy(p)
    return text(x + dx, y + dy, t, anchor, "al")


def out(s):
    return fin(rel(s))


# =====================================================================================
# chassis.alarm — forged aluminium A-arm (same form as p:chassis.alarm, il3_chassis.alarm)
# =====================================================================================
AL_A = (-112, 0)
AL_EF, AL_EN = (104, 74), (104, -74)


def arm(cam, mat="w", bush=True, bj=True):
    A = AL_A

    def leg(E, w0, w1):
        dx, dy = E[0] - A[0], E[1] - A[1]
        Ln = math.hypot(dx, dy)
        ux, uy = dx / Ln, dy / Ln
        nx, ny = -uy, ux

        def q(t, s):
            w = w1 + (w0 - w1) * t
            return (A[0] + ux * Ln * t + nx * s * w / 2, A[1] + uy * Ln * t + ny * s * w / 2)

        def strip(s0, s1, t0=.12, t1=.97):
            return [q(t0, s0), q(t1, s0), q(t1, s1), q(t0, s1)]
        o = pz(cam, 8, 9, strip(-1, 1), mat, dark=.7)
        rims = [strip(-1, -.62), strip(.62, 1)]
        rims.sort(key=lambda st: -cam.P((st[0][0], st[0][1], 0))[2])
        for st in rims:
            o += pz(cam, 0, 26, st, mat, dark=.25)
        return o

    def eye(E):
        x, y = E
        o = ring(cam, (x, y + 18, 13), (0, -1, 0), 21, 15, 36, mat, seg=32)
        if bush:
            o += disc3(cam, (x, y - 16, 13), (0, -1, 0), 15, "dks2", 26)
            o += cy(cam, (x, y - 14, 13), (0, -1, 0), 7, 7, "m", seg=18)
            o += disc3(cam, (x, y - 21.1, 13), (0, -1, 0), 4.2, "bg", 14)
        return o
    Ef, En = AL_EF, AL_EN
    o = eye(Ef) + leg((Ef[0] - 2, Ef[1] - 6), 30, 36)
    o += eye(En) + leg((En[0] - 2, En[1] + 6), 30, 36)
    o += pz(cam, 0, 26, banded(hull(arc(A[0], A[1], 25, 90, 270, 8) + [(-58, 24), (-58, -24), (-46, 12), (-46, -12)]), 2), mat, dark=.25)
    if bj:
        o += cy(cam, (A[0], 0, 26), (0, 0, 1), 18, 4, mat, seg=28)
        o += cy(cam, (A[0], 0, 30), (0, 0, 1), 16, 11, "dk", seg=28, r1=9.5)
        o += cy(cam, (A[0], 0, 41), (0, 0, 1), 8, 18, "m", seg=20, r1=6.4)
        o += cy(cam, (A[0], 0, 59), (0, 0, 1), 5.8, 11, "m", seg=18)
    else:
        o += disc3(cam, (A[0], 0, 26.1), (0, 0, 1), 15, "bg", 24)
    return o


def isec(x, y, s=1.0):
    """I-section of the forged leg (rims + thin web), framed inset."""
    o = rect(x, y, 74 * s, 84 * s, "m", 4) + text(x + 37 * s, y + 14 * s, "断面", "middle", "sm")
    cx, cy0 = x + 37 * s, y + 52 * s
    w, h, t, wt = 26 * s, 50 * s, 7 * s, 8 * s
    pts_ = [(-w / 2, -h / 2), (-w / 2 + t, -h / 2), (-w / 2 + t, -wt / 2), (w / 2 - t, -wt / 2), (w / 2 - t, -h / 2), (w / 2, -h / 2),
            (w / 2, h / 2), (w / 2 - t, h / 2), (w / 2 - t, wt / 2), (-w / 2 + t, wt / 2), (-w / 2 + t, h / 2), (-w / 2, h / 2)]
    # rotated 90deg: rims are the vertical flanges of the leg seen end-on
    o += path(P([(cx + py_, cy0 + px_) for px_, py_ in [(b, a) for a, b in pts_]]), "cut")
    return o


@dpart("chassis.alarm", "detail")
def alarm_detail3():
    s, cam = place(lambda sc: arm(sc.cam), 30, 30, (24, 34, 384, 280), sh_k=.45)
    notes = [("アーム本体", "アルミ鍛造。I形断面で軽量化"), ("ブッシュ穴", "ゴムブッシュを圧入"), ("ボールジョイント穴", "ナックルとつながる"), ("リブ", "鍛造で成形する補強")]
    s += isec(396, 40)
    s += bal(*cam.xy((0, -40, 12)), 150, 270, 1)
    s += bal(*cam.xy((104, -92, 13)), 420, 270, 2)
    s += bal(*cam.xy((-112, -14, 30)), 40, 70, 3)
    s += bal(*cam.xy((-10, 40, 26)), 230, 50, 4)
    return rel(s), notes


def _alarm_cut():
    def fn(sc):
        cam = sc.cam
        o = ""
        # cut piece (far, right), saw blade, bar (near, left)
        o += cy(cam, (-28, 0, 22), X_, 22, 46, "w", seg=28)
        o += cy(cam, (-40, 0, 64), X_, 56, 4, "t", seg=40, dark=.2)
        o += disc3(cam, (-40.1, 0, 64), (-1, 0, 0), 12, "m", 16)
        o += cy(cam, (-250, 0, 22), X_, 22, 208, "w", seg=28)
        return o

    def fur(sc):
        cam = sc.cam
        o = box(cam, 30, -60, -8, 330, 120, 8, "m", dark=.4)                       # conveyor
        o += box(cam, 170, -70, 0, 160, 140, 110, "m", dark=.55)                   # furnace tunnel
        o += path(P([cam.xy(p) for p in ((170, -40, 0), (170, -40, 70), (170, 40, 70), (170, 40, 0))]), "hotin")
        o += cy(cam, (110, 0, 22), X_, 22, 46, "h", seg=28)
        o += cy(cam, (40, 0, 22), X_, 22, 46, "w", seg=28)
        return o
    return fur, fn


@dpart("chassis.alarm", "ops")
def alarm_ops3():
    ops = []
    # 0 cut + heat
    fur, saw = _alarm_cut()
    s, cam = place(lambda sc: fur(sc) + saw(sc), 30, 24, (24, 50, 456, 262))
    s = title("押出材・鋳造ビレットを切断し、加熱") + s
    s += arc3(cam, (-38, 0, 64), X_, 66, 110, 170)
    s += arrow3(cam, (60, -90, 0), (160, -90, 0))
    s += label(cam, (-40, 0, 140), "切断", 0, 0) + label(cam, (250, -70, 120), "加熱炉", 0, -8)
    ops.append(out(s))

    # 1 die forging
    def f1(sc):
        cam = sc.cam
        o = box(cam, -170, -120, -46, 330, 240, 46, "t", dark=.2)
        o += path(P([cam.xy((x, y, .2)) for x, y in hull(arc(-112, 0, 34, 90, 270, 6) + [(118, 92), (118, -92), (120, 70), (120, -70)])]), "ts3")
        o += hot(arm(cam, "w", bush=False, bj=False))
        o += box(cam, -160, -105, 150, 310, 210, 40, "t", dark=.2)
        return o
    s, cam = place(f1, 30, 28, (40, 36, 440, 272))
    s = title("前成形（ロール・ベンダ）後に型鍛造") + s
    s += arrow3(cam, (170, -105, 230), (170, -105, 180))
    s += label(cam, (170, -105, 230), "上型", 14, 0, "start") + label(cam, (170, -105, -20), "下型", 14, 0, "start")
    ops.append(out(s))

    # 2 trim flash
    def f2(sc):
        cam = sc.cam
        fl = hull(arc(-112, 0, 40, 90, 270, 8) + arc(104, 74, 34, -90, 120, 8) + arc(104, -74, 34, -120, 90, 8))
        o = pz(cam, 11, 3, banded(fl, 3), "w", dark=.6)
        o += arm(cam, bush=False, bj=False)
        inner = [(-40, 0), (84, 46), (84, -46)]
        o += path(P([cam.xy((x, y, 14.2)) for x, y in inner]), "cutframe")
        o += path(P([cam.xy((x, y, 14.2)) for x, y in hull(arc(-112, 0, 26, 90, 270, 8) + arc(104, 74, 22, -90, 120, 8) + arc(104, -74, 22, -120, 90, 8))]), "cutframe")
        o += pz(cam, 190, 22, banded(hull(arc(-112, 0, 26, 90, 270, 8) + arc(104, 74, 22, -90, 120, 8) + arc(104, -74, 22, -120, 90, 8)), 3), "t", dark=.2)
        return o
    s, cam = place(f2, 30, 30, (40, 36, 440, 272))
    s = title("バリを抜く") + s
    s += arrow3(cam, (-150, -40, 200), (-150, -40, 120))
    s += label(cam, (-150, -40, 200), "抜き型（パンチ）", -10, 0, "end")
    ops.append(out(s))

    # 3 T6 heat treatment: solution furnace -> hot arm on the hearth -> quench tank -> ageing furnace
    def f3(sc):
        cam = sc.cam
        o = box(cam, 560, -110, 0, 190, 220, 150, "m", dark=.55)
        o += path(P([cam.xy(p) for p in ((560, -80, 20), (560, -80, 120), (560, 80, 120), (560, 80, 20))]), "warmin")
        o += faces(cam, 290, -120, 0, 230, 240, 110, "tankw")
        o += box(cam, 292, -118, 0, 226, 236, 80, "fl")
        o += box(cam, -340, -130, 0, 170, 260, 170, "m", dark=.55)
        o += path(P([cam.xy(p) for p in ((-170.2, -100, 20), (-170.2, -100, 140), (-170.2, 100, 140), (-170.2, 100, 20))]), "hotin")
        o += box(cam, -170, -110, 0, 420, 220, 10, "m", dark=.2)
        cam2 = GE.Cam(*cam.xy((0, 0, 10)), 30, 30, cam.s)
        o += hot(arm(cam2, bush=False, bj=False))
        return o
    s, cam = place(f3, 30, 30, (30, 44, 450, 262))
    s = title("溶体化・焼入れ・時効（T6）で強度を出す") + s
    s += arrow3(cam, (240, -150, 60), (320, -150, 60))
    s += label(cam, (-255, -130, 0), "溶体化", 0, 18) + label(cam, (405, -120, 0), "焼入れ", 0, 18) + label(cam, (655, -110, 0), "時効", 0, 18)
    ops.append(out(s))

    # 4 bores
    def f4(sc):
        cam = sc.cam
        o = arm(cam, bush=False, bj=False)
        o += disc3(cam, (104, -92.1, 13), (0, -1, 0), 15, "bg", 22) + disc3(cam, (104, 55.9, 13), (0, -1, 0), 15, "bg", 22)
        o += ring3(cam, (104, -92.2, 13), Y_, 15, "mf", 28) + ring3(cam, (104, 55.8, 13), Y_, 15, "mf", 28)
        o += ring3(cam, (-112, 0, 26.2), Z_, 15, "mf", 28)
        o += drill(cam, (-112, 0, 40), Z_, 22, 70, hold=False) + spindle(cam, (-112, 0, 110), Z_, 26, 50)
        return o
    s, cam = place(f4, 30, 30, (40, 36, 440, 272))
    s = title("ブッシュ穴・ボールジョイント穴を加工") + s
    s += arc3(cam, (-112, 0, 95), Z_, 26, 200, 330)
    ops.append(out(s))

    # 5 fluorescent penetrant + measurement
    def f5(sc):
        cam = sc.cam
        o = arm(cam, bush=False, bj=False)
        o += disc3(cam, (104, -92.1, 13), (0, -1, 0), 15, "bg", 22)
        o += box(cam, -90, -40, 150, 120, 60, 22, "m", dark=.3)
        o += cy(cam, (104, -74, 34), Z_, 3, 90, "m", seg=12, bands=4) + box(cam, 84, -94, 124, 40, 40, 24, "m", dark=.3)
        return o
    s, cam = place(f5, 30, 30, (40, 36, 440, 272))
    s = title("蛍光浸透探傷で鍛造割れを確認し、寸法を測定") + s
    for p0, p1 in (((-70, -10, 150), (-80, -30, 26)), ((0, -10, 150), (20, 30, 26)), ((-30, 10, 150), (-40, 8, 26))):
        a, b = cam.xy(p0), cam.xy(p1)
        s += line(a[0], a[1], b[0], b[1], "uv")
    c0 = cam.xy((-60, 6, 26))
    s += path("M%s %sl6 3 4-2 7 4" % (n(c0[0]), n(c0[1])), "crack")
    pb = cam.xy((104, -74, 34))
    s += circ(pb[0], pb[1], 3.4, "probeball")
    s += label(cam, (-30, -10, 172), "紫外線灯", 0, -10) + label(cam, (104, -74, 148), "測定プローブ", 0, -10)
    ops.append(out(s))
    return ops


# =====================================================================================
# chassis.hubbearing — 3rd-generation hub unit (same form as il3_chassis.hubbearing; studs optional)
# =====================================================================================
def hub(cam, studs=True, mat="w", outer=True, inner_end=True):
    o = ""
    if inner_end:
        o += cy(cam, (84, 0, 0), X_, 32, 12, mat, seg=32, r1=27)
    if outer:
        o += cy(cam, (80, 0, 0), X_, 42, 4, "dk", seg=36)
        o += cy(cam, (36, 0, 0), X_, 46, 44, mat, seg=40, r1=43)
        holes = [[(u + 60 * math.cos(a), v + 60 * math.sin(a), f) for u, v, f in GE.circle_outline(6, 14, 4)]
                 for a in [PI / 4 + k * PI / 2 for k in range(4)]]
        ear = []
        for k in range(4):
            a = PI / 4 + k * PI / 2
            ear += arc(60 * math.cos(a), 60 * math.sin(a), 15, math.degrees(a) - 90, math.degrees(a) + 90, 6)
        o += compact(GE.prism(cam, (24, 0, 0), X_, banded(hull(ear), 2), 12, mat, holes=holes, smooth="outer", dark=.15))
        o += cy(cam, (14, 0, 0), X_, 44, 10, mat, seg=40)
        o += cy(cam, (19, 0, 0), X_, 45.5, 3, "dk", seg=40)
    else:
        o += cy(cam, (14, 0, 0), X_, 30, 70, mat, seg=32)
    lob = []
    for k in range(5):
        a = PI / 2 + 2 * PI * k / 5
        lob += arc(48 * math.cos(a), 48 * math.sin(a), 17, math.degrees(a) - 80, math.degrees(a) + 80, 6)
    holes = []
    if not studs:
        holes = [GE.circle_outline(5, 12, 4, 48 * math.cos(PI / 2 + 2 * PI * k / 5), 48 * math.sin(PI / 2 + 2 * PI * k / 5)) for k in range(5)]
    o += compact(GE.prism(cam, (0, 0, 0), X_, banded(hull(lob + arc(0, 0, 54, 0, 360, 30)), 2), 14, mat, smooth="outer" if holes else True,
                          holes=holes))
    items = [(cam.P((-8, 0, 0))[2], cy(cam, (-16, 0, 0), X_, 31, 16, mat, seg=36) + disc3(cam, (-16.1, 0, 0), (-1, 0, 0), 23, "w3", 28) +
              disc3(cam, (-16.2, 0, 0), (-1, 0, 0), 15, "bg", 18))]
    if studs:
        for k in range(5):
            a = PI / 2 + 2 * PI * k / 5
            yy, zz = 48 * math.cos(a), 48 * math.sin(a)
            st = cy(cam, (-34, yy, zz), (1, 0, 0), 6, 34, "m", seg=14, bands=6) + cy(cam, (-37, yy, zz), (1, 0, 0), 4.6, 3, "m", seg=14, r1=6)
            items.append((cam.P((-17, yy, zz))[2], st))
    o += "".join(s_ for _, s_ in sorted(items, key=lambda c: -c[0]))
    return o


class Sec:
    """framed section inset of the hub unit (old il_d_chassis.hub_sec, mirrored so the wheel flange is on the left like the 3D view)."""

    def __init__(self, x=304, y=40, w=166, h=232, k=1.12, dx=0):
        self.x, self.y, self.w, self.h, self.k = x, y, w, h, k
        self.x0, self.y0 = x + w / 2 + 44 * k + dx, y + h / 2 + 8

    def __call__(self, lx, ly):
        return (self.x0 - self.k * lx, self.y0 + self.k * ly)

    def g(self, body):
        return '<g transform="translate(%s %s) scale(%s %s)">%s</g>' % (n(self.x0), n(self.y0), n(-self.k), n(self.k), body)

    def frame(self, cap="断面"):
        return rect(self.x, self.y, self.w, self.h, "m", 4) + text(self.x + self.w / 2, self.y + 15, cap, "middle", "sm")


def _hub3(area=(18, 40, 296, 268), studs=False, extra=None, **kw):
    def fn(sc):
        o = hub(sc.cam, studs=studs, **kw)
        return o + (extra(sc.cam) if extra else "")
    return place(fn, 24, 18, area, sh_k=.42)


@dpart("chassis.hubbearing", "detail")
def hubbearing_detail3():
    s, cam = _hub3(studs=True)
    sec = Sec()
    s += sec.frame() + sec.g(OC.hub_sec())
    notes = [("ハブフランジ", "ホイール・ディスクの取付面。振れ管理"), ("外輪（車体取付フランジ）", "ナックルに締結する"),
             ("軌道面", "玉が転がる面。高周波焼入れ＋研削＋超仕上げ"), ("玉（2列）", "アンギュラ玉軸受。予圧を付与"),
             ("かしめ部", "内輪をハブ端部の揺動かしめで固定"), ("ハブボルト", "ホイールを締結")]
    s += bal(*cam.xy((7, 0, 62)), 60, 50, 1)
    s += bal(*cam.xy((30, -60 * .707, -60 * .707)), 200, 284, 2)
    s += bal(*sec(40, -34), 330, 286, 3) + bal(*sec(14, 29), 452, 286, 4) + bal(*sec(2, -26), 452, 64, 5)
    a = PI / 2 + 2 * PI * 2 / 5
    s += bal(*cam.xy((-36, 48 * math.cos(a), 48 * math.sin(a))), 30, 250, 6)
    return rel(s), notes


@dpart("chassis.hubbearing", "ops")
def hubbearing_ops3():
    ops = []

    # 0 hot forging of outer ring and hub
    def f0(sc):
        cam = sc.cam
        o = box(cam, -190, -100, -40, 380, 200, 40, "t", dark=.2)
        ear = []
        for k in range(4):
            a = PI / 4 + k * PI / 2
            ear += arc(60 * math.cos(a), 60 * math.sin(a), 15, math.degrees(a) - 90, math.degrees(a) + 90, 6)
        lob = []
        for k in range(5):
            a = PI / 2 + 2 * PI * k / 5
            lob += arc(48 * math.cos(a), 48 * math.sin(a), 17, math.degrees(a) - 80, math.degrees(a) + 80, 6)
        cam_r = GE.Cam(*cam.xy((95, 0, 0)), cam.ca and 30, 30, cam.s)
        cam_l = GE.Cam(*cam.xy((-95, 0, 0)), 30, 30, cam.s)
        o += pz(cam_r, 0, 14, banded(hull(lob + arc(0, 0, 54, 0, 360, 30)), 2), "h", smooth=True)
        o += cy(cam_r, (0, 0, 14), Z_, 30, 56, "h", seg=32)
        o += compact(GE.prism(cam_l, (0, 0, 0), Z_, banded(hull(ear), 2), 12, "h", smooth=True))
        o += ring(cam_l, (0, 0, 12), Z_, 46, 30, 44, "h", seg=36)
        o += box(cam, -190, -100, 140, 380, 200, 36, "t", dark=.2)
        return o
    s, cam = place(f0, 30, 28, (50, 36, 430, 272))
    s = title("外輪（フランジ付き）とハブ輪を熱間鍛造") + s
    s += arrow3(cam, (210, -100, 210), (210, -100, 165))
    s += label(cam, (-95, -80, 0), "外輪", 0, 22) + label(cam, (95, -80, 0), "ハブ輪", 0, 22)
    ops.append(out(s))

    # 1 turning the hub flange face
    def tool1(cam):
        o = box(cam, -96, -6, 38, 88, 12, 12, "t", dark=.1)
        o += px(cam, -8, 8, [(-7, 36), (7, 36), (7, 50), (-7, 50)], "t")
        return o
    s, cam = _hub3(extra=tool1, area=(30, 50, 330, 268))
    s = title("旋削で形状をつくる") + s
    s += ring3(cam, (-.3, 0, 0), X_, 40, "mf", 36)
    s += arc3(cam, (50, 0, 0), X_, 64, 200, 290) + label(cam, (50, 0, -64), "主軸回転", 10, 20, "start")
    s += arrow3(cam, (-70, 0, 56), (-70, 0, 78)) + label(cam, (-70, 0, 66), "送り", -8, 4, "end")
    ops.append(out(s))

    # 2 induction hardening of the raceways
    sec = Sec()
    s, cam = _hub3()
    s = title("軌道面とシール部を高周波焼入れ") + s + sec.frame() + sec.g(OC.hub_sec() + path(OC.HUB_F["race_o"], "coat") + path(OC.HUB_F["race_i"], "coat"))
    hx, hy = sec(60, -40)
    s += text(hx, sec.y + sec.h - 10, "硬化層", "middle", "al")
    s += tol(40, 284, "硬化層・焼割れ")
    ops.append(out(s))

    # 3 raceway grinding
    s, cam = _hub3()
    x, y = sec(62, -30)
    s = title("外輪軌道は内面研削、ハブ輪軌道はアンギュラ研削") + s + sec.frame()
    s += sec.g(OC.hub_sec() + mf(OC.HUB_F["race_o"]) + mf(OC.HUB_F["race_i"]))
    s += rect(x - 4, sec.y + 26, 8, y - sec.y - 34, "m3") + circ(x, y - 4, 7, "gw")
    s += rot(x, sec.y + 44, 12, 5, 200, 520) + text(x + 14, sec.y + 40, "砥石", "start", "al")
    s += arc3(cam, (50, 0, 0), X_, 64, 200, 290)
    s += tol(40, 284, "軌道径・真円度・溝R")
    ops.append(out(s))

    # 4 superfinishing
    s, cam = _hub3()
    x, y = sec(48, -24)
    s = title("砥石を揺動させて軌道面を超仕上げ") + s + sec.frame() + sec.g(OC.hub_sec() + mf(OC.HUB_F["race_i"]))
    s += rect(x - 8, sec.y + 40, 16, y - sec.y - 56, "m3") + rect(x - 8, y - 16, 16, 12, "gw")
    s += arrow(x - 34, sec.y + 32, x + 34, sec.y + 32, None, both=True) + text(x + 40, sec.y + 36, "揺動", "start", "al")
    s += arc3(cam, (50, 0, 0), X_, 64, 200, 290)
    ops.append(out(s))

    # 5 orbital forming of the hub end (preload)
    s, cam = _hub3()
    sec = Sec(dx=-26)
    x, y = sec(-4, 0)
    s = title("玉と内輪を組み込み、ハブ端を揺動かしめして予圧を与える") + s + sec.frame() + sec.g(OC.hub_sec() + mf("M0 -30 L0 -22"))
    s += '<g transform="rotate(8 %s %s)">' % (n(x), n(y)) + rect(x + 6, y - 40, 34, 80, "t", 4) + "</g>"
    s += arrow(x + 36, sec.y + 34, x + 30, y - 46, None) + text(x + 4, sec.y + sec.h - 10, "揺動かしめ", "middle", "al")
    s += tol(40, 284, "予圧・かしめ形状")
    ops.append(out(s))
    sec = Sec()

    # 6 rotation test + encoder check
    def sens(cam):
        return box(cam, 92, -60, 30, 22, 26, 30, "dk", dark=.2)
    s, cam = _hub3(studs=True, extra=sens, area=(24, 46, 300, 268))
    s = title("回転トルク・予圧・異音とセンサ用エンコーダを確認") + s
    s += arc3(cam, (40, 0, 0), X_, 72, 200, 300)
    s += label(cam, (103, -47, 60), "センサ", 0, -8)
    s += chart(320, 60, 146, 76, "noise") + text(393, 152, "音響・回転トルク", "middle", "sm")
    ops.append(out(s))
    return ops


# =====================================================================================
# chassis.disc — ventilated disc (same form as il3_pilot.disc), any axis: a = outboard (hat) direction
# =====================================================================================
DR, DRi, Dt, Dg, Drh, DHh = 150, 92, 11, 12, 84, 40


def bdisc(cam, C=(0, 0, 0), a=(0, -1, 0), mat="w", nv=32, holes=True, marks=False):
    R, Ri, t, g, rh, Hh = DR, DRi, Dt, Dg, Drh, DHh
    A = GE._norm(a)

    def O(y):
        return tuple(C[i] - y * A[i] for i in range(3))
    o = compact(GE.prism(cam, O(g / 2 + t), A, GE.circle_outline(R, 64, 16), t, mat, holes=[GE.circle_outline(rh, 40, 10)], smooth=True))
    o += compact(GE.prism(cam, O(g / 2), A, GE.circle_outline(R - 1.5, 64, 16), g, mat, smooth=True, caps=False, dark=2))
    vanes = []
    E1, E2, _ = GE.frame(A)
    for k in range(nv):
        an = 2 * PI * (k + .5) / nv
        c, s_ = math.cos(an), math.sin(an)
        w = 2.6
        loop = [(r * c - q * w * s_, r * s_ + q * w * c, i) for i, (r, q) in enumerate(((Ri + 2, -1), (R - .5, -1), (R - .5, 1), (Ri + 2, 1)))]
        rad = tuple(c * E1[j] + s_ * E2[j] for j in range(3))
        if GE._dot(rad, cam.D) > 0.05:
            continue
        mid = add(C, tuple((R - 10) * rad[j] for j in range(3)))
        vanes.append((cam.P(mid)[2], GE.prism(cam, O(g / 2), A, loop, g, mat, caps=False, lines=False)))
    o += "".join(v for _, v in sorted(vanes, key=lambda v: -v[0]))
    o += compact(GE.prism(cam, O(-g / 2), A, GE.circle_outline(R, 64, 16), t, mat, holes=[GE.circle_outline(Ri, 48, 12)], smooth=True))
    y0 = -g / 2 - t
    if marks:
        for r in (Ri + 14, Ri + 30, R - 12):
            o += path(P(circ3(cam, O(y0 - .1), A, r, 48)), "gr")
    o += compact(GE.prism(cam, O(y0 + 2), A, GE.circle_outline(rh, 40, 14), Hh - 7 + 2, mat, holes=[GE.circle_outline(rh - 6, 40, 10)],
                          smooth=True, caps=False))
    o += path(P(circ3(cam, O(y0 - Hh + 7), A, rh - 6, 40)), "bg")
    hs = [GE.circle_outline(33, 28, 7)]
    if holes:
        for k in range(5):
            an = 2 * PI * k / 5 + PI / 2
            hs.append(GE.circle_outline(7.5, 14, 4, 57 * math.cos(an), 57 * math.sin(an)))
    o += compact(GE.prism(cam, O(y0 - Hh + 7), A, GE.circle_outline(rh, 40, 14), 7, mat, holes=hs, smooth=True))
    return o


def bolt_c(k, C=(0, 0, 0), z=50):
    """centre of wheel-bolt hole k on the hat top of a flat disc (a = +z)."""
    E1, E2, _ = GE.frame(Z_)
    an = 2 * PI * k / 5 + PI / 2
    return tuple(C[i] + 57 * math.cos(an) * E1[i] + 57 * math.sin(an) * E2[i] + (z if i == 2 else 0) for i in range(3))


def shot_dots(cam, p0, p1, spread, cnt=34, r=1.6):
    """deterministic cone of shot pellets from p0 toward p1 (screen space)."""
    a, b = cam.xy(p0), cam.xy(p1)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    Ln = math.hypot(b[0] - a[0], b[1] - a[1])
    o = ""
    for i in range(cnt):
        t = ((i * 0.618) % 1) * .9 + .1
        q = (((i * 0.7548) % 1) - .5) * 2 * spread * t
        x = a[0] + math.cos(ang) * Ln * t - math.sin(ang) * q
        y = a[1] + math.sin(ang) * Ln * t + math.cos(ang) * q
        o += circ(x, y, r, "grain")
    return o


@dpart("chassis.disc", "ops")
def disc_ops3():
    ops = []
    FL = (0, 0, 1)

    # 0 green-sand mould with vent core, pour FC250
    def f0(sc):
        cam = sc.cam
        o = faces(cam, -200, -200, -110, 400, 400, 110, "sand")
        o += path(P([cam.xy((156 * math.cos(2 * PI * k / 40), 156 * math.sin(2 * PI * k / 40), .1)) for k in range(40)]), "w3")
        o += hot(bdisc(cam, (0, 0, -6), FL))
        o += faces(cam, -200, -200, 150, 400, 400, 60, "sand")
        o += cy(cam, (120, -80, 210), Z_, 24, 26, "sand", seg=20, bands=6, r1=34)
        return o
    s, cam = place(f0, 30, 26, (60, 36, 420, 262))
    s = title("生型にベンチ穴用の中子を組み、FC250を注湯") + s
    a, b = cam.xy((120, -80, 290)), cam.xy((120, -80, 236))
    s += line(a[0], a[1], b[0], b[1], "pour")
    q, r_ = cam.xy((200, -200, 180)), cam.xy((200, -200, -50))
    s += arrow(q[0] + 16, q[1] - 10, q[0] + 16, q[1] + 30, None) + text(q[0] + 24, q[1] + 14, "上型", "start", "al")
    s += text(r_[0] + 10, r_[1], "下型", "start", "al")
    s += text(240, 290, "中子ずれ＝ベンチ（通風路）の肉厚不良", "middle")
    ops.append(out(s))

    # 1 shake-out + shot blast
    def f1(sc):
        cam = sc.cam
        o = bdisc(cam, (0, 0, 0), (0, -1, 0), marks=False)
        o += cy(cam, (-420, -150, 70), GE._norm((380, 120, -70)), 12, 70, "m", seg=16, bands=5, r1=13)
        return o
    s, cam = place(f1, 38, 16, (60, 40, 420, 250))
    s = title("砂を落とし、ショットで表面を整える") + s
    s += shot_dots(cam, (-340, -125, 55), (-40, -30, 0), 34, 50, 2.2)
    s += label(cam, (-420, -150, 70), "ショット", 0, -18)
    for i in range(26):
        s += circ(70 + (i * 37) % 340, 262 + (i * 7) % 18, 1.6, "grain")
    ops.append(out(s))

    # 2 vertical twin-spindle lathe: both friction faces at once
    def f2(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -120), Z_, 60, 80, "m", seg=36, dark=.3)
        o += cy(cam, (0, 0, -40), Z_, 70, 23, "m", seg=36)
        o += box(cam, 128, -6, -36, 160, 12, 12, "t", dark=.1)
        o += bdisc(cam, (0, 0, 0), FL, marks=False)
        o += box(cam, 128, -6, 24, 160, 12, 12, "t", dark=.1)
        return o
    s, cam = place(f2, 30, 26, (30, 40, 400, 268))
    s = title("立形2主軸旋盤で摺動面の両面を同時に旋削") + s
    s += ring3(cam, (0, 0, 17.2), Z_, 149, "mf", 48) + vis_arc(cam, (0, 0, 17.2), Z_, 93, "mf", 40)
    s += vis_arc(cam, (0, 0, -17), Z_, 149, "mf", 48)
    s += arc3(cam, (0, 0, -60), Z_, 120, 120, 200)
    s += label(cam, (288, 0, 36), "上側バイト", 4, 4, "start") + label(cam, (288, 0, -24), "下側バイト", 4, 4, "start")
    s += tol(40, 284, "DTV 10μm以下・面振れ・粗さ")
    ops.append(out(s))

    # 3 wheel-bolt holes + pilot bore
    def f3(sc):
        cam = sc.cam
        o = bdisc(cam, (0, 0, 0), FL)
        p = bolt_c(3)
        o += drill(cam, add(p, (0, 0, 2)), Z_, 15, 70, hold=False) + spindle(cam, add(p, (0, 0, 72)), Z_, 26, 46)
        return o
    s, cam = place(f3, 30, 30, (60, 36, 420, 268))
    s = title("ハブボルト穴・センタ穴を加工") + s
    for k in range(5):
        s += ring3(cam, bolt_c(k, z=50.2), Z_, 7.5, "mf", 16)
    s += ring3(cam, (0, 0, 50.2), Z_, 33, "mf", 32)
    p = bolt_c(3)
    s += arc3(cam, add(p, (0, 0, 92)), Z_, 34, 200, 330)
    ops.append(out(s))

    # 4 balance: measure, then mill the rim
    def f4(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -110), Z_, 40, 90, "m", seg=32, dark=.3)
        o += bdisc(cam, (0, 0, 0), FL, marks=False)
        o += cy(cam, (166, 0, -8), Z_, 9, 50, "t", seg=16, bands=5) + spindle(cam, (166, 0, 42), Z_, 20, 40)
        return o
    s, cam = place(f4, 30, 26, (40, 36, 440, 268))
    s = title("アンバランスを測り、外周を削って修正") + s
    s += ring3(cam, (0, 0, 0), Z_, 151, "mf", 24, -16, 16)
    s += arc3(cam, (0, 0, -70), Z_, 110, 120, 200) + arc3(cam, (166, 0, 70), Z_, 30, 200, 330)
    s += label(cam, (166, 0, 82), "エンドミル", 30, -2, "start")
    ops.append(out(s))

    # 5 DTV / run-out measurement after rust prevention
    def f5(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -110), Z_, 40, 90, "m", seg=32, dark=.3)
        o += cy(cam, (128, 0, -26), X_, 3, 80, "m", seg=10, bands=4)
        o += bdisc(cam, (0, 0, 0), FL, marks=False)
        o += cy(cam, (128, 0, 26), X_, 3, 80, "m", seg=10, bands=4)
        o += box(cam, 208, -14, -40, 30, 28, 80, "m", dark=.3)
        return o
    s, cam = place(f5, 30, 26, (30, 40, 360, 268))
    s = title("防錆処理後、厚み差（DTV）と振れを全数測定") + s
    for z in (19, -19):
        q = cam.xy((128, 0, z))
        s += circ(q[0], q[1], 3, "probeball")
    s += arc3(cam, (0, 0, -70), Z_, 110, 120, 200)
    s += rect(370, 50, 96, 52, "m", 4) + text(418, 82, "DTV μm", "middle")
    ops.append(out(s))
    return ops


# =====================================================================================
# chassis.caliper — floating caliper (same form as il3_chassis.caliper). stage: "cast" | "mach" | "full"
# =====================================================================================
CZ = -12
CAL_EAR = [(-96, CZ - 4), (96, CZ - 4)]
CAL_BLEED = (20, -10, CZ + 30)
CAL_HOSE = (-18, -16, CZ + 30)


def calip(cam, stage="full", mat="w"):
    zc = CZ

    def pc(r, a):
        return (r * math.cos(math.radians(a)), -150 + r * math.sin(math.radians(a)))
    o = py(cam, 52, 52, banded(hull([pc(172, a) for a in range(62, 119, 4)] + [pc(126, a) for a in range(66, 115, 6)]), 2), mat,
           smooth=True, dark=.3, cap_mat="w3" if mat == "w" else None)
    win = [cam.xy((172.2 * math.cos(math.radians(a)), y, -150 + 172.2 * math.sin(math.radians(a))))
           for a, y in [(a, 14) for a in range(81, 100, 3)] + [(a, 38) for a in range(99, 80, -3)]]
    o += path(P(win), "bg")
    for sd in (-1, 1):
        x = sd * 96
        o += py(cam, 40, 32, banded(hull(arc(x, zc - 4, 15, 0, 360, 14) + [(sd * 66, 6), (sd * 66, -30)]), 2), mat, smooth=True, dark=.3,
                cap_mat="w3" if mat == "w" else None)
        if stage == "full":
            o += cy(cam, (x, 8, zc - 4), (0, -1, 0), 11, 16, "dk", seg=20, r1=8)
            for yy in (2, -3):
                o += path(P(circ3(cam, (x, yy, zc - 4), (0, -1, 0), 11 - (8 - yy) * .19, 18)[4:13], False), "gr")
            o += compact(GE.prism(cam, (x, -8, zc - 4), (0, -1, 0), banded(hexagon(9, 0), 1), 8, "m", dark=.2))
        elif stage == "mach":
            o += disc3(cam, (x, 7.9, zc - 4), (0, -1, 0), 8, "bg", 16)
    o += cy(cam, (0, 2, zc), (0, -1, 0), 38, 34, mat, seg=40, dark=.1)
    o += cy(cam, (0, -32, zc), (0, -1, 0), 38, 7, mat, seg=40, r1=31)
    o += disc3(cam, (0, -39.1, zc), (0, -1, 0), 20, "w3" if mat == "w" else mat, 28)
    o += cy(cam, (-18, -16, zc + 30), (0, 0, 1), 9, 9, mat, seg=18)
    if stage != "cast":
        o += disc3(cam, (-18, -16, zc + 39.1), (0, 0, 1), 4.5, "bg", 12)
    Ab = GE._norm((.15, .1, 1))
    b0 = CAL_BLEED
    o += cy(cam, b0, Ab, 7.5, 8, mat, seg=16)
    if stage == "full":
        o += compact(GE.prism(cam, add(b0, mul(Ab, 8)), Ab, banded(hexagon(6.5, 0), 1), 5, "m"))
        o += cy(cam, add(b0, mul(Ab, 13)), Ab, 3.6, 9, "m", seg=12, bands=6)
    elif stage == "mach":
        o += disc3(cam, add(b0, mul(Ab, 8.1)), Ab, 3.6, "bg", 12)
    return o


class CSec:
    """framed section of the caliper cylinder: closed end left, bore open to the right (toward the disc)."""

    def __init__(self, x=320, y=44, w=150, h=170, k=1.25):
        self.x, self.y, self.w, self.h, self.k = x, y, w, h, k
        self.x0, self.y0 = x + 18, y + h / 2 + 8

    def __call__(self, lx, ly):
        return (self.x0 + self.k * lx, self.y0 + self.k * ly)

    def g(self, body):
        return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (n(self.x0), n(self.y0), n(self.k), body)

    def frame(self, cap="シリンダ断面"):
        return rect(self.x, self.y, self.w, self.h, "m", 4) + text(self.x + self.w / 2, self.y + 15, cap, "middle", "sm")

    @staticmethod
    def body(bleed=True):
        up = [(0, -38), (88, -38), (88, -31), (82, -31), (82, -27), (66, -27), (66, -31), (60, -31), (60, -27), (12, -27), (12, 0), (0, 0)]
        o = path(P(up), "cut") + path(P([(x, -y) for x, y in up]), "cut")
        if bleed:
            o += rect(16, -38, 5, 11, "bg")
        o += cl(-6, 0, 100, 0)
        return o

    BORE = "M12 -27 L60 -27 M66 -27 L82 -27 M12 27 L60 27 M66 27 L82 27"
    GROOVE = "M60 -27 L60 -31 L66 -31 L66 -27 M60 27 L60 31 L66 31 L66 27"

    @staticmethod
    def piston(x0=14):
        o = path(P([(x0, -26.4), (x0 + 74, -26.4), (x0 + 74, 26.4), (x0, 26.4)]), "w")
        o += path(P([(x0 + 12, -18), (x0 + 74, -18), (x0 + 74, 18), (x0 + 12, 18)]), "w3")
        return o

    @staticmethod
    def seal():
        return rect(60.5, -30.6, 5, 3.4, "dk") + rect(60.5, 27.2, 5, 3.4, "dk")


def _cal3(stage="full", area=(16, 40, 312, 262), extra=None, mat="w"):
    def fn(sc):
        return calip(sc.cam, stage, mat) + (extra(sc.cam) if extra else "")
    return place(fn, 26, 24, area, sh_k=.46)


@dpart("chassis.caliper", "detail")
def caliper_detail3():
    s, cam = _cal3()
    cs = CSec(y=50, h=200)
    s += cs.frame() + cs.g(CSec.body() + CSec.seal())
    notes = [("シリンダ穴", "ピストンが入る穴。径・粗さ"), ("ピストンシール溝", "シールの変形で戻り量をつくる"), ("ブリーダ穴", "エア抜き用のねじ穴"),
             ("取付穴", "ナックルへの取付"), ("ディスク通過部", "ディスクをまたぐブリッジ")]
    s += bal(*cs(36, -27), 360, 278, 1) + bal(*cs(63, 31), 440, 278, 2)
    s += bal(*cam.xy(add(CAL_BLEED, (2, 0, 22))), 240, 50, 3)
    s += bal(*cam.xy((-96, -8, CZ - 16)), 40, 250, 4)
    s += bal(*cam.xy((0, 30, 22)), 130, 50, 5)
    return rel(s), notes


@dpart("chassis.caliper", "ops")
def caliper_ops3():
    ops = []

    # 0 casting
    def f0(sc):
        cam = sc.cam
        o = faces(cam, -170, -140, -140, 340, 280, 112, "sand")
        o += hot(calip(cam, "cast"))
        o += faces(cam, -170, -140, 150, 340, 280, 50, "sand")
        o += cy(cam, (110, -70, 200), Z_, 18, 20, "sand", seg=20, bands=6, r1=26)
        return o
    s, cam = place(f0, 26, 26, (60, 36, 420, 268))
    s = title("鋳鉄は生型、アルミは重力・低圧鋳造") + s
    a, b = cam.xy((110, -70, 270)), cam.xy((110, -70, 226))
    s += line(a[0], a[1], b[0], b[1], "pour")
    q = cam.xy((170, -140, 180))
    s += arrow(q[0] + 16, q[1] - 14, q[0] + 16, q[1] + 26, None) + text(q[0] + 24, q[1] + 10, "上型", "start", "al")
    ops.append(out(s))

    # 1 machining: cylinder bore + seal groove (section), bleeder, hose and mounting holes
    def tl1(cam):
        tip = add(CAL_BLEED, mul(GE._norm((.15, .1, 1)), 9))
        return drill(cam, tip, GE._norm((.15, .1, 1)), 7, 60, hold=False) + spindle(cam, add(tip, mul(GE._norm((.15, .1, 1)), 60)), GE._norm((.15, .1, 1)), 16, 30)
    s, cam = _cal3("mach", extra=tl1)
    cs = CSec(y=50, h=200)
    s = title("シリンダ穴・シール溝・ブリーダ穴・取付穴を加工") + s + cs.frame()
    s += cs.g(CSec.body() + mf(CSec.BORE) + mf(CSec.GROOVE) + rect(50, -5, 52, 10, "t") + rect(54, -29, 7, 24, "t"))
    x, y = cs(70, 40)
    s += arrow(x + 20, y, x - 14, y, None) + text(x + 2, y + 18, "ボーリング", "middle", "al")
    for x_, _ in CAL_EAR:
        s += ring3(cam, (x_, 7.8, CZ - 4), Y_, 8, "mf", 16)
    s += ring3(cam, (-18, -16, CZ + 39.2), Z_, 4.5, "mf", 12)
    s += tol(320, 284, "シリンダ径・粗さ・シール溝寸法")
    ops.append(out(s))

    # 2 zinc plating (no plating inside the cylinder)
    def f2(sc):
        cam = sc.cam
        o = faces(cam, -200, -120, -170, 400, 240, 270, "tankw")
        o += box(cam, -40, -10, 92, 80, 20, 70, "m", dark=.2)
        o += calip(cam, "mach")
        o += box(cam, -198, -118, -168, 396, 236, 200, "fl")
        o += box(cam, -260, -10, 162, 520, 20, 14, "m", dark=.2)
        return o
    s, cam = place(f2, 26, 24, (60, 40, 420, 270))
    s = title("防錆のため亜鉛系めっき（シリンダ内は付着させない）") + s
    s += label(cam, (200, -120, -150), "めっき液", 10, 0, "start")
    ops.append(out(s))

    # 3 steel piston: turn, grind, hard chrome
    def f3(sc):
        cam = sc.cam
        o = cy(cam, (34, 56, 56), X_, 52, 30, "gw", seg=40)
        o += cy(cam, (100, 0, 0), X_, 46, 40, "m", seg=36, dark=.4)
        o += cy(cam, (0, 0, 0), X_, 27, 100, "w", seg=40)
        o += cy(cam, (8, 0, 0), X_, 28.5, 5, "w", seg=40, dark=.4)
        o += disc3(cam, (-.1, 0, 0), (-1, 0, 0), 20, "bg", 28)
        return o
    s, cam = place(f3, 22, 20, (50, 50, 430, 262))
    s = title("鋼ピストンを旋削・研削し、硬質クロムめっき") + s
    a0, a1 = cam.xy((20, 0, 27.3)), cam.xy((100, 0, 27.3))
    b0, b1 = cam.xy((20, -27, 0)), cam.xy((100, -27, 0))
    s += line(a0[0], a0[1], a1[0], a1[1], "mf") + line(b0[0], b0[1], b1[0], b1[1], "mf")
    s += arc3(cam, (50, 0, 0), X_, 40, 200, 300) + arc3(cam, (49, 56, 56), X_, 64, 40, 110)
    s += label(cam, (49, 56, 124), "砥石", 0, -6) + label(cam, (50, 0, -40), "外径を研削 → 硬質クロムめっき", 0, 26)
    ops.append(out(s))

    # 4 assembly
    s, cam = _cal3("full")
    cs = CSec(y=50, h=200)
    s = title("シール・ピストン・ブーツ・ブリーダを組み付け") + s + cs.frame()
    s += cs.g(CSec.body(False) + CSec.seal() + CSec.piston(40) + rect(82, -36, 10, 9, "dk") + rect(82, 27, 10, 9, "dk"))
    x, y = cs(60, -48)
    s += arrow(x + 20, y, x - 20, y, None) + text(x, y - 8, "ピストン挿入", "middle", "al")
    s += arrow3(cam, add(CAL_BLEED, (0, 0, 70)), add(CAL_BLEED, (0, 0, 36))) + label(cam, add(CAL_BLEED, (0, 0, 70)), "ブリーダ", 0, -8)
    ops.append(out(s))

    # 5 leak + drag (piston start pressure) test
    s, cam = _cal3("full", area=(16, 70, 300, 268))
    s = title("気密と、ピストンが動き出す圧力（引きずり）を確認") + s
    h0 = cam.xy((-18, -16, CZ + 40))
    s += path("M%s %s C%s %s %s %s %s %s" % (n(h0[0]), n(h0[1]), n(h0[0]), n(h0[1] - 40), n(h0[0] + 140), n(70), n(330), n(70)), "cable")
    s += circ(350, 70, 20, "m") + line(350, 70, 360, 58, "a") + text(350, 104, "圧力", "middle", "sm")
    s += chart(320, 160, 150, 80, "ramp")
    ops.append(out(s))
    return ops


# =====================================================================================
# chassis.hu — ABS/ESC hydraulic unit (form of il3_chassis.hu) + solenoid valves on the -x (ECU) face
# stage: "blank" | "mach" | "valve" | "ecu"
# =====================================================================================
HU_PORTS = ((-38, -16, 9.5), (-38, 16, 9.5), (-6, -22, 7.5), (-6, 4, 7.5), (22, -22, 7.5), (22, 4, 7.5))
HU_PLUGS = ((-44, 56, 4.5), (-24, 56, 3.5), (-4, 56, 4.5), (16, 56, 3.5), (38, 56, 4.5), (-34, 34, 5.5), (-10, 34, 3.5),
            (12, 34, 5.5), (36, 34, 3.5), (-44, 14, 3.5), (-20, 14, 4.5), (6, 14, 3.5), (30, 14, 4.5))
HU_VALVES = [(y, z) for z in (54, 24) for y in (-24, 0, 24)]


def hublock(cam, stage="valve", motor=True, mat="w"):
    o = ""
    if motor and stage in ("valve", "ecu"):
        o += cy(cam, (52, 0, 26), X_, 34, 52, "m", seg=36)
        o += cy(cam, (104, 0, 26), X_, 31, 10, "dk", seg=32)
        o += pz(cam, 50, 14, [(108, -10), (118, -10), (118, 10), (108, 10)], "dk")
        o += cy(cam, (48, 0, 26), X_, 38, 6, "m", seg=36)
    o += pz(cam, 0, 76, [(-60, -40), (56, -40), (60, -36), (60, 40), (-56, 40), (-60, 36)], mat, dark=.05)
    if stage == "blank":
        return o
    for x, y, r in HU_PORTS:
        o += disc3(cam, (x, y, 76.1), (0, 0, 1), r, "w3", 20) + disc3(cam, (x, y, 76.1), (0, 0, 1), r * .55, "bg", 14)
    for x, z, r in HU_PLUGS:
        o += disc3(cam, (x, -40.1, z), (0, -1, 0), r, "w3", 14)
        o += disc3(cam, (x, -40.2, z), (0, -1, 0), r * .55, "w2" if stage != "mach" else "bg", 10)
    for y, z in HU_VALVES:
        o += disc3(cam, (-60.1, y, z), (-1, 0, 0), 8.5, "w3", 18)
        if stage == "mach":
            o += disc3(cam, (-60.2, y, z), (-1, 0, 0), 6, "bg", 14)
    if stage in ("valve", "ecu"):
        o += valves(cam)
    if stage == "ecu":
        o += box(cam, -96, -44, 2, 34, 88, 72, "dk", dark=.1)
        o += box(cam, -108, -16, 46, 12, 32, 20, "dk", dark=.3)
    return o


def valves(cam, skip=()):
    o = ""
    order = sorted(HU_VALVES, key=lambda v: -cam.P((-70, v[0], v[1]))[2])
    for y, z in order:
        if (y, z) in skip:
            continue
        o += cy(cam, (-60, y, z), (-1, 0, 0), 7, 6, "w", seg=14, bands=4)
        o += cy(cam, (-66, y, z), (-1, 0, 0), 9.5, 8, "dk", seg=16, bands=4)
        o += cy(cam, (-74, y, z), (-1, 0, 0), 3.5, 5, "m", seg=10, bands=3)
    return o


def _hu3(stage="valve", area=(40, 40, 330, 266), extra=None, pre=None, motor=True, **kw):
    def fn(sc):
        return (pre(sc.cam) if pre else "") + hublock(sc.cam, stage, motor) + (extra(sc.cam) if extra else "")
    return place(fn, 28, 26, area, sh_k=.46, **kw)


@dpart("chassis.hu", "detail")
def hu_detail3():
    s, cam = _hu3("valve", area=(40, 40, 400, 272))
    notes = [("アルミブロック", "数十の穴と交差油路を持つ押出材の削り出し"), ("ソレノイドバルブ", "かしめで固定する増減圧弁"),
             ("ポンプ・モータ", "還流ポンプを駆動"), ("配管ポート", "マスタシリンダ・各輪への接続ねじ")]
    s += bal(*cam.xy((20, -40, 4)), 240, 284, 1) + bal(*cam.xy((-82, -24, 24)), 40, 240, 2)
    s += bal(*cam.xy((80, 0, 60)), 440, 120, 3) + bal(*cam.xy((-38, -16, 80)), 120, 50, 4)
    return rel(s), notes


@dpart("chassis.hu", "ops")
def hu_ops3():
    ops = []

    # 0 cut extruded bar
    def f0(sc):
        cam = sc.cam
        o = box(cam, -50, -40, 0, 116, 80, 76, "w", dark=.05)
        o += cy(cam, (-58, 0, 100), X_, 80, 4, "t", seg=48, dark=.2)
        o += disc3(cam, (-58.1, 0, 100), (-1, 0, 0), 18, "m", 18)
        o += box(cam, -340, -40, 0, 280, 80, 76, "w", dark=.05)
        return o
    s, cam = place(f0, 28, 22, (40, 40, 440, 262))
    s = title("アルミ押出材（6061）を定寸に切断") + s
    s += arc3(cam, (-56, 0, 100), X_, 92, 110, 170) + label(cam, (-56, -80, 150), "丸のこ", -10, 0, "end")
    ops.append(out(s))

    # 1 drilling valve, pump and port bores + cross passages (hidden lines)
    def tl(cam):
        x, y, r = HU_PORTS[4]
        return drill(cam, (x, y, 77), Z_, 13, 64, hold=False) + spindle(cam, (x, y, 141), Z_, 24, 40)
    s, cam = _hu3("mach", extra=tl, motor=False, area=(60, 40, 400, 268))
    s = title("6面から弁穴・ポンプ穴・交差油路を加工") + s
    for a_, b_ in (((-38, -16, 76), (-38, -16, 34)), ((-38, -16, 34), (36, -16, 34)), ((-6, -22, 76), (-6, -22, 56)),
                   ((-60, -24, 54), (-6, -24, 54)), ((-60, 0, 24), (30, 0, 24)), ((60, 0, 26), (20, 0, 26))):
        p0, p1 = cam.xy(a_), cam.xy(b_)
        s += hid("M%s %s L%s %s" % (n(p0[0]), n(p0[1]), n(p1[0]), n(p1[1])))
    for y, z in HU_VALVES:
        s += ring3(cam, (-60.3, y, z), X_, 8.5, "mf", 16)
    x, y, r = HU_PORTS[4]
    s += ring3(cam, (x, y, 76.3), Z_, r, "mf", 16)
    s += arc3(cam, (x, y, 120), Z_, 26, 200, 330)
    s += tol(300, 284, "穴位置・径、交差部のバリ")
    ops.append(out(s))

    # 2 deburr cross holes with high-pressure water, precision wash
    def nz(cam):
        return cy(cam, (-10, -150, 60), GE._norm((14, 110, -26)), 5, 70, "t", seg=12, bands=4) + \
            cy(cam, (-10, -150, 60), GE._norm((-14, -110, 26)), 12, 40, "m", seg=16, bands=5)
    s, cam = _hu3("mach", extra=nz, motor=False, area=(70, 36, 410, 268))
    s = title("交差穴のバリを高圧水で取り、精密洗浄") + s
    tip = add((-10, -150, 60), mul(GE._norm((14, 110, -26)), 70))
    p0, p1 = cam.xy(tip), cam.xy((-4, -40, 56))
    s += line(p0[0], p0[1], p1[0], p1[1], "jet")
    s += drops(p1[0] - 8, p1[1] + 20, 5, 30, 18)
    s += label(cam, (-10, -150, 60), "高圧水", 0, 24)
    ops.append(out(s))

    # 3 anodizing
    def f3(sc):
        cam = sc.cam
        o = faces(cam, -140, -110, -60, 280, 220, 200, "tankw")
        o += box(cam, -4, -4, 76, 8, 8, 80, "m")
        o += hublock(cam, "mach", False)
        o += box(cam, -138, -108, -58, 276, 216, 170, "fl")
        o += box(cam, -200, -10, 156, 400, 20, 12, "m", dark=.2)
        return o
    s, cam = place(f3, 28, 24, (70, 40, 410, 270))
    s = title("アルマイト処理で耐食性を持たせる") + s
    s += label(cam, (140, -110, -40), "電解液", 10, 0, "start")
    ops.append(out(s))

    # 4 caulk solenoid valves, press in pump motor
    def tl4(cam):
        y, z = HU_VALVES[0]
        o = valves(cam, skip=((y, z),))
        o += cy(cam, (-60, y, z), (-1, 0, 0), 7, 6, "w", seg=18, bands=6)
        o += cy(cam, (-66, y, z), (-1, 0, 0), 12, 50, "t", seg=20, bands=6)
        return o

    def pre4(cam):
        return cy(cam, (110, 0, 26), X_, 34, 52, "m", seg=36) + cy(cam, (106, 0, 26), X_, 38, 6, "m", seg=36)
    s, cam = place(lambda sc: pre4(sc.cam) + hublock(sc.cam, "mach", False).replace('"bg"', '"w3"') + tl4(sc.cam), 28, 26, (60, 40, 420, 266), sh_k=.46)
    s = title("ソレノイドバルブをかしめ固定し、ポンプ・モータを圧入") + s
    y, z = HU_VALVES[0]
    s += arrow3(cam, (-150, y, z + 34), (-118, y, z + 34)) + label(cam, (-134, y, z + 34), "塑性流動かしめ", 0, -12)
    s += arrow3(cam, (170, 0, 80), (120, 0, 80)) + label(cam, (170, 0, 80), "圧入", 6, 4, "start")
    ops.append(out(s))

    # 5 join ECU, check pressure response and leakage
    s, cam = _hu3("ecu", area=(30, 60, 300, 268))
    s = title("制御ECUを結合し、液圧特性と漏れを全数確認") + s
    for x, y, r in HU_PORTS[:4]:
        a_ = cam.xy((x, y, 77))
        s += path("M%s %s C%s %s %s %s %s %s" % (n(a_[0]), n(a_[1]), n(a_[0]), n(a_[1] - 40), n(300), n(70 + x * .2), n(330), n(70 + x * .2)), "cable")
    s += rect(326, 52, 26, 34, "m", 3)
    s += chart(330, 160, 140, 80, "step") + tol(330, 284, "液圧・応答特性")
    ops.append(out(s))
    return ops
