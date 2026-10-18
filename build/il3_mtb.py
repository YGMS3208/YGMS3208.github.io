"""v3 machine-tool atlas drawings (shaded metal, detailed): grinders, gear machines, EDM, laser.
cylindrical-grinder internal-grinder surface-grinder centerless-grinder gear-hobbing-machine
gear-grinding-machine gear-skiving-machine edm laser-machine.
Re-registers the same slugs as il_mt.py with the same notes (text, count, order)."""
import math
from il_mt import mt
from il3_mtlib import *

T20 = math.tan(math.radians(20))


# ------------------------------------------------------------------ local helpers
def grit(sc, O, A, r, h, k=90, caps=(1,), ri=0.0, bias=-0.6, kc=None):
    """abrasive speckle on the visible side of a wheel (and on visible end faces listed in caps: 0 start, 1 end)."""
    a = V(A)
    E1, E2, _ = GE.frame(a)

    def f(s_):
        cam, d = s_.cam, ""
        for i in range(k):
            t = 2 * math.pi * ((i * 0.618034 + .07) % 1)
            u = (i * 0.7548777 + .13) % 1
            nr = tuple(math.cos(t) * E1[j] + math.sin(t) * E2[j] for j in range(3))
            if GE._dot(nr, cam.D) < -0.22:
                q = cam.xy(tuple(O[j] + a[j] * (.03 + .94 * u) * h + r * 1.003 * nr[j] for j in range(3)))
                d += "M%s %sh.1" % (n(q[0]), n(q[1]))
        for cp in caps:
            nrm = a if cp else tuple(-v for v in a)
            if GE._dot(nrm, cam.D) > -0.05:
                continue
            C = add3(O, a, h * cp + (.3 if cp else -.3))
            for i in range(kc or int(k * .9)):
                t = 2 * math.pi * ((i * 0.618034 + .31) % 1)
                u = (i * 0.7548777 + .41) % 1
                rad = math.sqrt(ri * ri + (r * r * .92 - ri * ri) * u)
                q = cam.xy(tuple(C[j] + rad * (math.cos(t) * E1[j] + math.sin(t) * E2[j]) for j in range(3)))
                d += "M%s %sh.1" % (n(q[0]), n(q[1]))
        return path(d, "grit2") if d else ""
    lo, hi = _cbb(O, a, r, h)
    sc.add(f, (lo, hi), bias)


def wheel(sc, O, A, r, h, bias=0.0, k=90, caps=(1,), ri=0.0, seg=48, bands=14, dark=1, holes=()):
    """vitrified grinding wheel: banded 'gw' solid with abrasive speckle."""
    MCYL(sc, O, A, r, h, "gw", bias, seg=seg, bands=bands, dark=dark, holes=holes, wdeg=math.radians(3))
    grit(sc, O, A, r, h, k, caps, ri, bias - .6)


def ashell(sc, O, A, L, ro, ri, a0, a1, mat="pt", dark=1, bias=0.0, seg=22):
    """arc segment of a tube along A (angles a0..a1 deg in GE.frame(A): 0 = E1, 90 = E2): wheel guards."""
    a = V(A)
    E1, E2, _ = GE.frame(a)
    o = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((ro * math.cos(t), ro * math.sin(t), k // 3))
    for k in range(seg, -1, -1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((ri * math.cos(t), ri * math.sin(t), 100 + k // 3))
    sv = GE.prism(sc.cam, O, a, o, L, mat, smooth=True, dark=dark)
    pts_ = []
    for u, v, _ in o:
        for s_ in (0, L):
            pts_.append(tuple(O[j] + u * E1[j] + v * E2[j] + s_ * a[j] for j in range(3)))
    sc.add(_chain_svg(compact(sv)), bbox(pts_), bias)


def handwheel(sc, C, axis, r=20, bias=-1.0):
    """hand wheel on a face: hub, three spokes and a rim, axis = outward face normal ('x'/'y'/'z' char or (0,-1,0) style)."""
    a = V(axis)
    c, sg = _ax_char(a)
    MRING(sc, C, a, r, r - 4, 5, "w", bias, seg=28, bands=8, spec=False)
    MCYL(sc, C, a, r * .28, 9, "w", bias - .5, seg=14, bands=5, spec=False)
    it = _IDX[c]
    iu, iv = _UV[c]
    for k in range(3):
        radial(sc, c, C[it] + (0 if sg > 0 else -3), 3, (C[iu], C[iv]), 90 + 120 * k, r * .25, r - 3, 3.5, "w", b=0, bias=bias - .2)


def gearw(sc, O, A, z, rp, h, mat="w", helix=0.0, bore=0.0, bias=0.0, slices=None, **kw):
    """work gear (light outline: 2 points per flank, no fillet) as one compacted item."""
    a = V(A)
    tw = h * math.tan(math.radians(helix)) / rp if helix else 0.0
    s = GE.prism(sc.cam, O, a, GE.gear_outline(z, rp, None, None, 0.0, nf=2, fillet=False), h, mat,
                 holes=[GE.circle_outline(bore, 32, 32)] if bore else [], twist=tw, slices=slices or (2 if helix else 1), **kw)
    sc.add(_chain_svg(compact(s)), _cbb(O, a, rp * 1.08, h), bias)


def hob3_svg(cam, O, A, L, rr, m, ng=10, mat="t", land=.7, g0=0.0, lines=True, vis=0.35, steps=2, wt=None, wr=None, gr=False):
    """hob (or threaded wheel with land=1, many ng) along A from O: root cylinder + rack-profile teeth placed on a
    single-start helix, cut into ng gashes. Teeth are convex solids sorted far -> near."""
    a = V(A)
    E1, E2, _ = GE.frame(a)
    p = math.pi * m
    ra = rr + 2.25 * m
    wt = wt if wt is not None else p / 2 - 2 * m * T20
    wr = wr if wr is not None else p / 2 + 2.5 * m * T20

    def W(s_, rad, t):
        return tuple(O[j] + a[j] * s_ + rad * (math.cos(t) * E1[j] + math.sin(t) * E2[j]) for j in range(3))
    root, _ = MCYL_svg(cam, O, a, rr, L, mat, seg=32, bands=10, dark=2, spec=False)
    teeth = []
    gs = 2 * math.pi / ng
    for g in range(ng):
        ta = g0 + g * gs + gs * (1 - land) / 2
        tb = ta + gs * land
        tm = (ta + tb) / 2
        nr = (math.cos(tm), math.sin(tm))
        nrm = tuple(nr[0] * E1[j] + nr[1] * E2[j] for j in range(3))
        if GE._dot(nrm, cam.D) > vis:
            continue
        ts = [ta + (tb - ta) * q / steps for q in range(steps + 1)]
        for k in range(-2, int(L / p) + 3):
            sm = k * p + p * tm / (2 * math.pi)
            if sm - wr / 2 - p * (tb - ta) / (4 * math.pi) < 0 or sm + wr / 2 + p * (tb - ta) / (4 * math.pi) > L:
                continue
            cr, rt = [], []
            for t in ts:
                s_ = k * p + p * t / (2 * math.pi)
                cr.append((W(s_ - wt / 2, ra, t), W(s_ + wt / 2, ra, t)))
                rt.append((W(s_ - wr / 2, rr, t), W(s_ + wr / 2, rr, t)))
            faces = [[cr[0][0], cr[0][1], rt[0][1], rt[0][0]], [cr[-1][0], cr[-1][1], rt[-1][1], rt[-1][0]]]
            for q in range(steps):
                faces.append([cr[q][0], cr[q + 1][0], cr[q + 1][1], cr[q][1]])          # crest
                faces.append([cr[q][0], cr[q + 1][0], rt[q + 1][0], rt[q][0]])          # flank -
                faces.append([cr[q][1], cr[q + 1][1], rt[q + 1][1], rt[q][1]])          # flank +
                faces.append([rt[q][0], rt[q + 1][0], rt[q + 1][1], rt[q][1]])          # root (hidden)
            sv = cvx_svg(cam, faces, mat, 0, crease=40)
            if not lines:
                sv = __import__("re").sub(r'<path class="(el|gr)" d="[^"]*"/>', "", sv)
            elif not gr:
                sv = __import__("re").sub(r'<path class="gr" d="[^"]*"/>', "", sv)
            teeth.append((cam.P(W(sm, (rr + ra) / 2, tm))[2], sv))
    teeth.sort(key=lambda q: -q[0])
    return root + "".join(v for _, v in teeth), _cbb(O, a, ra, L)


def hob3(sc, O, A, L, rr, m, bias=0.0, **kw):
    s, bb = hob3_svg(sc.cam, O, A, L, rr, m, **kw)
    sc.add(s, bb, bias)
    return bb


# =====================================================================================
@mt("cylindrical-grinder", az=-26, el=20)
def _(sc):
    yc, zc = -70, 206
    # bed: dark toe kick + casting, panel seams, hand wheel (table traverse)
    block(sc, -300, -150, 0, 600, 330, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -310, -160, 12, 620, 350, 96, "pt", ch=12, b=3, bias=900)
    seams(sc, [[(-120, -160.2, 22), (-120, -160.2, 100)], [(150, -160.2, 22), (150, -160.2, 100)]], ((-120, -161, 22), (150, -160, 100)), "gr")
    handwheel(sc, (-210, -160, 62), (0, -1, 0), 22)
    # table + swivel table (ground top with a T-slot)
    block(sc, -270, -140, 108, 540, 130, 28, "pt", ch=4, b=2, bias=500)
    block(sc, -262, -132, 136, 524, 114, 16, "m", ch=2, b=1.5, bias=400)
    seams(sc, [[(-160, -75, 152.2), (150, -75, 152.2)]], ((-160, -76, 152), (150, -74, 152.4)), "tslot", bias=390)
    seams(sc, [[(-6, -132.2, 140), (-6, -132.2, 148)], [(0, -132.2, 138), (0, -132.2, 150)], [(6, -132.2, 140), (6, -132.2, 148)]],
          ((-6, -133, 138), (6, -132, 150)), "el", bias=390)
    # work head: casting, name band, drive motor, drive plate + dog, centre
    block(sc, -262, -126, 152, 96, 104, 96, "pt", ch=6, b=2.5)
    block(sc, -254, -127.4, 222, 80, 1.4, 14, "dk", b=0, dark=0, bias=-1)
    servo(sc, (-214, -74, 248), "z", 34, 40, up=(0, -1, 0))
    MCYL(sc, (-166, yc, zc), (1, 0, 0), 36, 10, "w", rings=(.5,), seg=32)
    block(sc, -156, yc - 30, zc + 14, 8, 10, 14, "dk", b=.8, dark=0, bias=-2)
    MCYL(sc, (-156, yc, zc), (1, 0, 0), 11, 6, "w", r1=7, seg=18, bands=6, bias=-3)
    # work (stepped shaft, bright ground journals)
    for x0, r, L in ((-150, 17, 20), (-130, 22, 56), (-74, 30, 90), (16, 24, 60), (76, 17, 74)):
        MCYL(sc, (x0, yc, zc), (1, 0, 0), r, L, "w", bias=-30, dark=0, seg=32, bands=12, rings=(.5,) if r == 30 else ())
    # tailstock: casting, quill, live centre, lever
    block(sc, 166, -118, 152, 76, 96, 76, "pt", ch=6, b=2.5)
    MCYL(sc, (166, yc, zc), (-1, 0, 0), 16, 8, "w", seg=24, bias=-5)
    MCYL(sc, (158, yc, zc), (-1, 0, 0), 11, 8, "w", r1=7, seg=18, bands=6, bias=-6)
    MCYL(sc, (204, yc, 228), (0, 0, 1), 12, 8, "w", seg=18, bands=6)
    MCYL(sc, (204, yc, 236), (0, 0, 1), 3, 26, "w", seg=10, bands=4, spec=False)
    MCYL(sc, (204, yc, 262), (0, 0, 1), 6, 8, "dk", seg=14, bands=4, spec=False)
    # cross slide + wheel head, wheel with guard, spindle motor
    R = 104
    wy = yc + 30 + R
    block(sc, -120, 34, 108, 330, 150, 26, "pt", ch=4, b=2, bias=600)
    block(sc, -10, 46, 134, 200, 130, 130, "pt", ch=8, b=3, bias=-5)
    block(sc, 10, 44.6, 236, 150, 1.4, 16, "dk", b=0, dark=0, bias=-6)
    bolts(sc, [(30 + 22 * k, 46, 150) for k in range(6)], (0, -1, 0), 3.2, bias=-6)
    MCYL(sc, (-16, wy, zc), (1, 0, 0), 40, 6, "w", seg=32, rings=())
    wheel(sc, (-62, wy, zc), (1, 0, 0), R, 46, k=140, caps=(1,), ri=40)
    xshell(sc, -68, 58, R + 12, R + 2, -40, 172, "pt", bias=-2, seg=24, cy=wy, cz=zc)
    seams(sc, [[(-40, wy - 112, zc + 30), (-40, wy - 120, zc + 14), (-40, -50, zc + 6)]], ((-41, -60, zc), (-39, -40, zc + 32)), "pipe", bias=-8)
    finmotor(sc, (190, 110, 200), (1, 0, 0), 28, 44, nf=12)
    sc.axis((-250, -175, 290), (-110, -175, 290), "Z")
    sc.axis((250, 250, 300), (250, 130, 300), "X", off=(12, 0))
    sc.rot((-40, wy, zc), (1, 0, 0), R * .6, "", 120, 230)
    sc.note((-20, wy - R * .6, zc - R * .3), "砥石", "高速で回転し、工作物の外径を削る")
    sc.note((-220, -126, 230), "主軸台", "工作物を回す。センタで支持する")
    sc.note((210, -118, 210), "心押台", "反対側のセンタで支える")
    sc.note((100, yc, zc), "工作物", "軸受部の径を数μmで仕上げる")
    sc.note((-230, -140, 125), "テーブル", "工作物ごと軸方向に往復する")
    sc.note((160, 60, 250), "砥石台", "砥石を切り込み方向（X）に送る")
    sc.note((-40, wy - 20, zc + R + 12), "砥石カバー", "砥石の破損に備える覆い")
    sc.note((-290, -160, 60), "ベッド", "振動を抑える重い土台")


# =====================================================================================
@mt("internal-grinder", az=-26, el=20)
def _(sc):
    yc, zc = -30, 200
    yq, zq = yc - 7.2, zc - 9.6                       # wheel axis offset so the wheel touches the bore wall
    block(sc, -310, -140, 0, 620, 280, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -320, -150, 12, 640, 300, 88, "pt", ch=12, b=3, bias=900)
    seams(sc, [[(-100, -150.2, 22), (-100, -150.2, 92)], [(150, -150.2, 22), (150, -150.2, 92)]], ((-100, -151, 22), (150, -150, 92)), "gr")
    # work head on its base
    block(sc, -300, -130, 100, 200, 220, 30, "pt", ch=4, b=2, bias=600)
    block(sc, -290, -110, 130, 150, 160, 130, "pt", ch=8, b=3, bias=300)
    block(sc, -280, -111.4, 232, 120, 1.4, 14, "dk", b=0, dark=0, bias=299)
    servo(sc, (-215, -20, 260), "z", 34, 40, up=(0, -1, 0))
    # chuck, jaws, ring work (bore visible from +x)
    MCYL(sc, (-140, yc, zc), (1, 0, 0), 64, 34, "m", bias=-20, seg=40, rings=(.3,))
    bolts(sc, ring_pts((-106, yc, zc), (1, 0, 0), 46, 6, math.pi / 6), (1, 0, 0), 3.4, bias=-21)
    for ph, bi in ((90, -40), (210, -60), (330, -30)):
        radial(sc, "x", -106, 30, (yc, zc), ph, 56, 78, 18, "w", b=1.2, bias=bi)
    MRING(sc, (-106, yc, zc), (1, 0, 0), 56, 34, 36, "w", bias=-45, seg=40, dark=0)
    # rails + ball screw on the bed for the wheel-head slide (Z)
    for y in (-100, 40):
        rail(sc, (-96, y, 100), "x", 396, "z", w=16, h=10, bias=650)
    ballscrew(sc, (-90, -30, 112), "x", 380, r=6, nut=None, bias=640)
    servo(sc, (300, -30, 112), "x", 30, 40)
    # wheel-head slide (Z) with X rails, wheel head
    block(sc, -20, -130, 110, 320, 220, 30, "pt", ch=4, b=2, bias=600)
    for x in (90, 230):
        rail(sc, (x, -128, 140), "y", 216, "z", w=14, h=8, bias=550)
    block(sc, 60, -110, 150, 200, 160, 132, "pt", ch=8, b=3, bias=-10)
    block(sc, 70, -111.4, 256, 150, 1.4, 14, "dk", b=0, dark=0, bias=-11)
    bolts(sc, [(80 + 26 * k, -110, 170) for k in range(6)], (0, -1, 0), 3.2, bias=-11)
    finmotor(sc, (260, -30, 210), (1, 0, 0), 24, 38, nf=10)
    # wheel spindle cartridge, quill, small wheel inside the bore
    MCYL(sc, (60, yq, zq), (-1, 0, 0), 30, 26, "w", bias=-20, seg=32, rings=(.4,))
    MCYL(sc, (34, yq, zq), (-1, 0, 0), 16, 10, "w", bias=-21, seg=24)
    MCYL(sc, (24, yq, zq), (-1, 0, 0), 9, 86, "w", bias=-30, seg=20, bands=8)
    wheel(sc, (-62, yq, zq), (-1, 0, 0), 22, 34, bias=-35, k=40, caps=(0,), seg=28, bands=8)
    seams(sc, [[(-30, yc - 40, zc + 80), (-40, yc - 40, zc + 54), (-60, yc - 24, zc + 20)]], ((-61, yc - 41, zc + 20), (-29, yc - 23, zc + 80)), "pipe", bias=-50)
    sc.axis((-20, -160, 300), (120, -160, 300), "Z")
    sc.axis((200, 130, 280), (200, 30, 280), "X", off=(14, 0))
    sc.note((-200, -110, 270), "主軸台", "工作物をチャックでつかんで回す")
    sc.note((-80, yc - 58, zc + 20), "工作物（穴）", "ギヤの内径や軸受の内輪を仕上げる")
    sc.note((-94, yc, zc - 22), "砥石", "穴より小さい砥石を高速で回す")
    sc.note((40, yc + 9, zc + 9), "砥石軸（クイル）", "細長い軸。たわみが精度を左右する")
    sc.note((160, -110, 260), "砥石台", "砥石を軸方向（Z）と切り込み（X）に送る")
    sc.note((-250, -150, 50), "ベッド", "機械の土台")


# =====================================================================================
@mt("surface-grinder", az=-30, el=24)
def _(sc):
    block(sc, -320, -150, 0, 640, 310, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -330, -160, 12, 660, 330, 88, "pt", ch=12, b=3, bias=900)
    handwheel(sc, (-230, -160, 58), (0, -1, 0), 22)
    handwheel(sc, (210, -160, 58), (0, -1, 0), 18)
    # saddle (Y), table (X) with stop dogs, magnetic chuck
    block(sc, -180, -140, 100, 360, 260, 30, "pt", ch=4, b=2, bias=700)
    block(sc, -320, -120, 130, 640, 200, 30, "pt", ch=4, b=2, bias=600)
    for x in (-250, 230):
        block(sc, x, -126, 136, 16, 6, 16, "dk", b=.8, dark=0, bias=590)
    block(sc, -260, -110, 160, 520, 180, 20, "dk", ch=2, b=1, dark=0, bias=500)
    block(sc, -256, -106, 180, 512, 172, 4, "m", b=1, bias=490)

    def poles(s_):
        ln = ""
        for k in range(1, 32):
            x = -256 + k * 16
            a, b = s_.P((x, -106, 184.1)), s_.P((x, 66, 184.1))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return path(ln, "gr")
    sc.raw(poles, ((-256, -106, 184), (256, 66, 184.3)), bias=485)
    MCYL(sc, (220, -110, 170), (0, -1, 0), 4, 10, "w", seg=10, bands=4, spec=False, bias=480)
    MCYL(sc, (220, -120, 170), (0, -1, 0), 7, 6, "dk", seg=12, bands=4, spec=False, bias=479)
    block(sc, -150, -80, 184, 90, 70, 36, "w", b=1.5, dark=0)                       # workpieces
    block(sc, -40, -80, 184, 90, 70, 36, "w", b=1.5, dark=0)
    # column with Z rails, bellows, Z servo
    block(sc, -90, 150, 100, 180, 150, 420, "pt", ch=10, b=3, bias=400)
    for x in (-62, 62):
        rail(sc, (x, 150, 116), "z", 396, (0, -1, 0), w=16, h=8, carriages=[(200, 46)], bias=350)
    bellows(sc, (-42, 142, 116), (42, 150, 290), "z", folds=12, bias=360)
    servo(sc, (0, 225, 520), "z", 34, 40, up=(0, -1, 0))
    # wheel head, spindle motor, wheel (axis along y) with flange nut, guard
    R, zw = 92, 314
    block(sc, -80, 20, 290, 160, 116, 130, "pt", ch=8, b=3, bias=100)
    block(sc, -70, 18.6, 392, 140, 1.4, 14, "dk", b=0, dark=0, bias=99)
    finmotor(sc, (80, 80, 360), (1, 0, 0), 26, 40, nf=12)
    wheel(sc, (0, 20, zw), (0, -1, 0), R, 34, bias=-20, k=120, caps=(1,), ri=30)
    MCYL(sc, (0, -14, zw), (0, -1, 0), 30, 6, "w", bias=-22, seg=32, rings=())
    MCYL(sc, (0, -20, zw), (0, -1, 0), 14, 8, "w", bias=-23, seg=6, bands=6, spec=False)
    bolts(sc, ring_pts((0, -20, zw), (0, -1, 0), 22, 6, 0.3), (0, -1, 0), 2.6, bias=-24)
    ashell(sc, (0, 26, zw), (0, -1, 0), 46, R + 12, R + 2, -10, 190, "pt", bias=-25)
    ashell(sc, (0, -20, zw), (0, -1, 0), 4, R + 12, R - 12, -10, 190, "pt", bias=-26)
    seams(sc, [[(70, 0, 340), (96, -30, 300), (70, -30, 236)]], ((69, -31, 236), (97, 0, 340)), "pipe", bias=-30)
    sc.axis((-320, -150, 250), (-180, -150, 250), "X")
    sc.axis((-330, -150, 140), (-330, -40, 140), "Y", off=(-12, 0))
    sc.axis((130, 40, 330), (130, 40, 430), "Z", off=(14, 0))
    sc.note((0, -14, 228), "砥石", "外周で平面を削る（横軸形）")
    sc.note((-80, 20, 400), "砥石頭", "砥石を上下（Z）に送って切り込む")
    sc.note((-160, -110, 190), "マグネットチャック", "鋼の工作物を磁力で吸着する")
    sc.note((-110, -14, 220), "工作物", "平面度・平行度を出して仕上げる")
    sc.note((-280, -120, 145), "テーブル", "左右（X）に往復する")
    sc.note((-90, 150, 500), "コラム", "砥石頭を支える")
    sc.note((300, -160, 50), "ベッド", "機械の土台")


# =====================================================================================
@mt("centerless-grinder", az=-22, el=26)
def _(sc):
    zc = 270                                          # both wheel centres; work centre 8 above
    R1, R2 = 130, 80
    y1, y2 = 132, -106
    yw, zw, rw = -12, 278, 14
    block(sc, -250, -250, 0, 500, 500, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -260, -260, 12, 520, 520, 98, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-60, -260.2, 22), (-60, -260.2, 102)], [(120, -260.2, 22), (120, -260.2, 102)]], ((-60, -261, 22), (120, -260, 102)), "gr")
    handwheel(sc, (-180, -260, 62), (0, -1, 0), 22)
    # grinding wheel head (behind): low base, spindle housing, motor, wheel, guard
    block(sc, -120, 40, 110, 240, 220, 20, "pt", ch=4, b=2, bias=500)
    block(sc, 80, 50, 130, 120, 200, 200, "pt", ch=8, b=3, bias=300)
    block(sc, 90, 48.6, 290, 100, 1.4, 14, "dk", b=0, dark=0, bias=299)
    finmotor(sc, (200, y1, zc), (1, 0, 0), 30, 46, nf=12)
    MCYL(sc, (70, y1, zc), (1, 0, 0), 44, 10, "w", seg=32, rings=(), bias=200)
    wheel(sc, (-80, y1, zc), (1, 0, 0), R1, 150, bias=200, k=170, caps=(1,), ri=44)
    xshell(sc, -86, 162, R1 + 12, R1 + 2, 20, 125, "pt", bias=150, seg=20, cy=y1, cz=zc)
    # regulating wheel head (front): slide, housing, servo, rubber-bond wheel
    block(sc, -120, -240, 110, 240, 150, 40, "pt", ch=4, b=2, bias=500)
    block(sc, 80, -230, 150, 110, 120, 180, "pt", ch=8, b=3, bias=-20)
    block(sc, 88, -231.4, 300, 94, 1.4, 14, "dk", b=0, dark=0, bias=-21)
    servo(sc, (190, y2, zc), "x", 36, 46)
    MCYL(sc, (70, y2, zc), (1, 0, 0), 34, 10, "w", seg=28, rings=(), bias=-10)
    MCYL(sc, (-80, y2, zc), (1, 0, 0), R2, 150, "dk", bias=-10, seg=40, bands=12, dark=0)
    # blade holder + blade with sloped top, through-feed work train
    block(sc, -110, -22, 110, 220, 24, 130, "pt", ch=2, b=1.5, bias=-25)
    cprism(sc, "x", -110, 220, [(-20, 240), (0, 240), (0, 262), (-20, 268)], "w", 1.5, 1.5, dark=0, bias=-26)
    for k in range(5):
        MCYL(sc, (-250 + k * 102, yw, zw), (1, 0, 0), rw, 92, "w", bias=-60, dark=0, seg=24, bands=10)
    seams(sc, [[(-10, 60, zc + R1 + 12), (-10, 20, zc + 60), (-10, 2, zw + 22)]], ((-11, 0, zw + 20), (-9, 62, zc + 145)), "pipe", bias=-70)
    sc.rot((70, y1, zc), (1, 0, 0), R1 * .7, "", 140, 220)
    sc.axis((-250, yw, zc + 50), (-100, yw, zc + 50), "送り", both=False)
    sc.note((-20, y1, zc + R1), "研削砥石", "大径の砥石で外周を削る")
    sc.note((-20, y2, zc - R2), "調整車", "ゴム系の車で工作物を回し、送りを与える")
    sc.note((-90, -20, 250), "ブレード（受け板）", "工作物を下から支える")
    sc.note((200, yw, zw), "工作物", "センタで支えずに連続して通す")
    sc.note((-230, -260, 60), "ベッド", "2つの砥石台を支える土台")


# =====================================================================================
@mt("gear-hobbing-machine", az=-30, el=22)
def _(sc):
    block(sc, -290, -190, 0, 580, 380, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -300, -200, 12, 600, 400, 88, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-80, -200.2, 22), (-80, -200.2, 92)], [(140, -200.2, 22), (140, -200.2, 92)]], ((-80, -201, 22), (140, -200, 92)), "gr")
    tc = (-70, -40)
    # work table, fixture, work gear (upper half already hobbed), arbor
    MCYL(sc, (tc[0], tc[1], 100), (0, 0, 1), 124, 14, "pt", bias=600, seg=48, rings=())
    MCYL(sc, (tc[0], tc[1], 114), (0, 0, 1), 110, 26, "m", bias=590, seg=48, rings=(.5,))

    def tslots(s_):
        d = ""
        for k in range(6):
            t = math.radians(15 + 60 * k)
            a = s_.P((tc[0] + 40 * math.cos(t), tc[1] + 40 * math.sin(t), 140.2))
            b = s_.P((tc[0] + 104 * math.cos(t), tc[1] + 104 * math.sin(t), 140.2))
            d += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return path(d, "tslot")
    sc.raw(tslots, ((tc[0] - 104, tc[1] - 104, 140), (tc[0] + 104, tc[1] + 104, 140.4)), bias=585)
    MCYL(sc, (tc[0], tc[1], 140), (0, 0, 1), 36, 12, "w", seg=32, rings=(), bias=500)
    MCYL(sc, (tc[0], tc[1], 152), (0, 0, 1), 24, 18, "w", seg=28, bias=495)
    z_, rp = 34, 78
    m = 2 * rp / z_
    MCYL(sc, (tc[0], tc[1], 170), (0, 0, 1), rp + m, 23, "w", seg=56, bands=14, dark=0, rings=(), bias=150)
    gearw(sc, (tc[0], tc[1], 193), (0, 0, 1), z_, rp, 23, "w", bore=18, bias=100)
    MCYL(sc, (tc[0], tc[1], 216), (0, 0, 1), 22, 8, "w", seg=6, bands=6, spec=False, bias=-20)
    MCYL(sc, (tc[0], tc[1], 224), (0, 0, 1), 14, 126, "w", bias=-30, seg=24, bands=8)
    # outboard support: column, arm, bearing boss
    block(sc, -200, 120, 100, 240, 60, 360, "pt", ch=8, b=3, bias=400)
    seams(sc, [[(-80, 119.8, 120), (-80, 119.8, 370)]], ((-81, 119, 120), (-79, 120, 370)), "gr", bias=399)
    block(sc, -100, -76, 380, 60, 196, 48, "pt", ch=4, b=2.5, bias=-40)
    MCYL(sc, (tc[0], tc[1], 380), (0, 0, -1), 26, 30, "pt", seg=32, rings=(.5,), bias=-35)
    # main column with name band, Z servo on top, main motor on the side
    block(sc, 150, -10, 100, 140, 200, 470, "pt", ch=10, b=3, bias=300)
    block(sc, 160, -11.4, 520, 120, 1.4, 18, "dk", b=0, dark=0, bias=299)
    servo(sc, (220, 90, 570), "z", 36, 44, up=(0, -1, 0))
    finmotor(sc, (290, 90, 420), (1, 0, 0), 26, 40, nf=12)
    # hob head on the column face, spindle housing behind the hob, hob on its arbor
    block(sc, 100, -40, 150, 50, 100, 120, "pt", ch=6, b=2.5, bias=200)
    bolts(sc, [(112 + 26 * k, -40, 166) for k in range(2)] + [(112 + 26 * k, -40, 254) for k in range(2)], (0, -1, 0), 3, bias=199)
    hz, hy0, hl = 194, -100, 120
    block(sc, 38, 30, 176, 66, 30, 36, "pt", ch=3, b=1.5, bias=160)
    MCYL(sc, (38, 26, hz), (0, 1, 0), 26, 34, "pt", seg=32, rings=(.5,), bias=155)
    MCYL(sc, (38, hy0 - 14, hz), (0, 1, 0), 10, hl + 40, "w", seg=20, bands=8, bias=150)
    MCYL(sc, (38, hy0 - 6, hz), (0, 1, 0), 18, 6, "w", seg=24, bias=148)
    MCYL(sc, (38, hy0 - 16, hz), (0, 1, 0), 14, 8, "w", seg=6, bands=6, spec=False, bias=147)
    MCYL(sc, (38, hy0 + hl, hz), (0, 1, 0), 18, 6, "w", seg=24, bias=149)
    hob3(sc, (38, hy0, hz), (0, 1, 0), hl, 24, m, ng=8, steps=1, vis=.2, bias=140)
    seams(sc, [[(100, -30, 262), (70, -70, 252), (50, -72, 232)]], ((49, -73, 232), (101, -29, 263)), "pipe", bias=-60)
    sc.rot((tc[0], tc[1], 216), (0, 0, 1), 112, "", 200, 320)
    sc.rot((38, hy0 - 14, hz), (0, 1, 0), 44, "", 200, 330)
    sc.axis((150, -130, 200), (150, -130, 300), "Z", off=(14, 0))
    sc.note((40, hy0 + 20, hz + 30), "ホブ", "ねじ状の切れ刃を持つ工具。工作物と同期回転する")
    sc.note((tc[0] - 50, tc[1] - 60, 200), "工作物（歯車）", "ホブとかみ合いながら歯が創成される")
    sc.note((tc[0] - 90, tc[1] - 60, 120), "ワークテーブル", "工作物を載せて回す")
    sc.note((110, -40, 250), "ホブヘッド", "ホブを回し、歯幅方向（Z）に送る")
    sc.note((210, -10, 520), "コラム", "ホブヘッドを支える")
    sc.note((-80, 120, 430), "サポート", "アーバ上端を支え、たわみを防ぐ")
    sc.note((260, -200, 50), "ベッド", "機械の土台")


# =====================================================================================
@mt("gear-grinding-machine", az=-50, el=20)
def _(sc):
    block(sc, -290, -190, 0, 580, 380, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -300, -200, 12, 600, 400, 88, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-60, -200.2, 22), (-60, -200.2, 92)]], ((-61, -201, 22), (-59, -200, 92)), "gr")
    tc = (-80, -40)
    MCYL(sc, (tc[0], tc[1], 100), (0, 0, 1), 112, 14, "pt", bias=600, seg=48, rings=())
    MCYL(sc, (tc[0], tc[1], 114), (0, 0, 1), 100, 26, "m", bias=590, seg=48, rings=(.5,))
    bolts(sc, ring_pts((tc[0], tc[1], 140), (0, 0, 1), 84, 6, .2), "z", 3.4, bias=585)
    MCYL(sc, (tc[0], tc[1], 140), (0, 0, 1), 32, 12, "w", seg=32, rings=(), bias=500)
    MCYL(sc, (tc[0], tc[1], 152), (0, 0, 1), 22, 18, "w", seg=28, bias=495)
    z_, rp = 32, 72
    m = 2 * rp / z_
    gearw(sc, (tc[0], tc[1], 170), (0, 0, 1), z_, rp, 40, "w", helix=20, bore=16, slices=2, bias=100)
    MCYL(sc, (tc[0], tc[1], 210), (0, 0, 1), 20, 8, "w", seg=6, bands=6, spec=False, bias=-20)
    MCYL(sc, (tc[0], tc[1], 218), (0, 0, 1), 12, 90, "w", bias=-30, seg=20, bands=8)
    MCYL(sc, (tc[0], tc[1], 308), (0, 0, 1), 12, 12, "w", r1=4, bias=-31, seg=20, bands=6)
    # column + wheel head with swivel plate, tilted spindle housing, threaded wheel
    block(sc, 170, -10, 100, 140, 200, 470, "pt", ch=10, b=3, bias=300)
    block(sc, 180, -11.4, 520, 120, 1.4, 18, "dk", b=0, dark=0, bias=299)
    servo(sc, (240, 90, 570), "z", 36, 44, up=(0, -1, 0))
    block(sc, 30, 70, 120, 140, 110, 180, "pt", ch=6, b=2.5, bias=200)
    block(sc, 40, 68.6, 268, 120, 1.4, 16, "dk", b=0, dark=0, bias=199)
    tl = math.radians(20)
    A = (0, math.cos(tl), math.sin(tl))
    WC, R, WL = (40, -45, 190), 52 - 2.25 * m, 150
    w0 = lin(WC, (-WL / 2, A))
    MCYL(sc, lin(WC, (WL / 2 + 4, A)), A, 34, 56, "pt", seg=32, rings=(.6,), bias=170)
    MCYL(sc, lin(WC, (WL / 2, A)), A, 20, 4, "w", seg=24, bias=168)
    MCYL(sc, lin(w0, (-10, A)), A, 16, 10, "w", seg=24, bias=165)
    MCYL(sc, lin(w0, (-36, A)), A, 24, 26, "pt", seg=28, rings=(.5,), bias=164)
    # low C-frame of the head: front upright under the outboard bearing, arm along the right side
    block(sc, 20, -150, 104, 130, 24, 24, "pt", ch=3, b=1.5, bias=180)
    block(sc, 106, -126, 104, 44, 196, 24, "pt", ch=3, b=1.5, bias=180)
    s, bb = hob3_svg(sc.cam, w0, A, WL, R, m, ng=12, land=1.0, mat="gw", steps=1, lines=False, vis=.2)
    sc.add(s, bb, 160)
    grit(sc, w0, A, R + 2.25 * m, WL, 90, caps=(), bias=158)

    def crest(s_):
        return helix(s_.cam, lin(w0, (-.25 * math.pi * m, A)), A, R + 2.25 * m + .3, WL - 2, math.pi * m, "gwt", per=16) + \
            helix(s_.cam, lin(w0, (.25 * math.pi * m, A)), A, R + 2.25 * m + .3, WL - 2, math.pi * m, "gwt", per=16)
    sc.raw(crest, bb, 157)
    # dresser on the head: spindle and diamond roll touching the rear end of the wheel
    RC = lin(WC, (WL / 2 - 26, A), (R + 2.25 * m + 22, (1, 0, 0)))
    MCYL(sc, lin(RC, (6, A)), A, 12, 66, "dk", seg=24, dark=0, bias=150)
    MCYL(sc, lin(RC, (-6, A)), A, 22, 12, "w", seg=28, rings=(.5,), bias=140)
    sc.rot((tc[0], tc[1], 210), (0, 0, 1), 104, "", 200, 320)
    sc.rot(lin(w0, (-14, A)), A, 66, "", 200, 330)
    sc.axis((170, -170, 200), (170, -170, 300), "Z", off=(14, 0))
    sc.note((40, -60, 190 + 54), "ねじ状砥石", "ねじの形の砥石を回し、歯面を連続して創成研削する")
    sc.note((tc[0] - 50, tc[1] - 60, 200), "工作物（焼入れ後の歯車）", "砥石と同期回転しながら歯面を仕上げる")
    sc.note((-75, -139, 128), "ワークテーブル", "工作物を回す")
    sc.note((40, -137, 180), "砥石頭", "砥石を回し、歯幅方向に送る")
    sc.note((RC[0], RC[1], RC[2] + 22), "ドレッサ", "ダイヤモンドロールで砥石の形を整える")
    sc.note((220, -10, 520), "コラム", "砥石頭を支える")
    sc.note((260, -200, 50), "ベッド", "機械の土台")


# =====================================================================================
@mt("gear-skiving-machine", az=-30, el=26)
def _(sc):
    block(sc, -290, -210, 0, 580, 420, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -300, -220, 12, 600, 440, 88, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-80, -220.2, 22), (-80, -220.2, 92)], [(120, -220.2, 22), (120, -220.2, 92)]], ((-80, -221, 22), (120, -220, 92)), "gr")
    tc = (-60, -60)
    MCYL(sc, (tc[0], tc[1], 100), (0, 0, 1), 162, 14, "pt", bias=600, seg=56, rings=())
    MCYL(sc, (tc[0], tc[1], 114), (0, 0, 1), 150, 26, "m", bias=590, seg=56, rings=(.5,))
    for k in range(6):
        radial(sc, "z", 140, 26, tc, 30 + 60 * k, 141, 150, 16, "dk", b=1, dark=0, bias=400 if math.sin(math.radians(30 + 60 * k)) > 0 else 250)
    # internal ring gear (work)
    z_, rp = 60, 108
    s = GE.prism(sc.cam, (tc[0], tc[1], 140), (0, 0, 1), GE.circle_outline(140, 64, 16), 56, "w",
                 holes=[GE.internal_outline(z_, rp, nf=2)], smooth="outer")
    sc.add(_chain_svg(compact(s)), ((tc[0] - 140, tc[1] - 140, 140), (tc[0] + 140, tc[1] + 140, 196)), 300)
    # column, name band, servo; spindle head with swivel disc and motor
    block(sc, 130, -20, 100, 160, 220, 480, "pt", ch=10, b=3, bias=400)
    block(sc, 140, -21.4, 530, 140, 1.4, 18, "dk", b=0, dark=0, bias=399)
    servo(sc, (210, 90, 580), "z", 36, 44, up=(0, -1, 0))
    block(sc, -40, -70, 310, 170, 140, 130, "pt", ch=8, b=3, bias=100)
    MCYL(sc, (40, -70, 375), (0, -1, 0), 50, 8, "pt", seg=36, rings=(), bias=95)
    bolts(sc, ring_pts((40, -78, 375), (0, -1, 0), 42, 8, .2), (0, -1, 0), 2.6, bias=94)
    finmotor(sc, (60, 0, 440), (0, 0, 1), 30, 44, nf=12)
    # tilted tool spindle (axis crossing angle 22 deg) and skiving cutter at the far side of the ring
    ang = math.radians(22)
    up = (math.sin(ang), 0, math.cos(ang))
    C0 = (tc[0], tc[1] + 64, 176)
    C1 = lin(C0, (22, up))
    gearw(sc, C0, up, 26, 44, 22, "t", bore=0, bias=-10)
    MCYL(sc, C1, up, 22, 8, "w", seg=6, bands=6, spec=False, bias=-11)
    MCYL(sc, lin(C1, (8, up)), up, 18, 30, "w", seg=24, bias=-12, rings=(.5,))
    MCYL(sc, lin(C1, (38, up)), up, 30, 104, "pt", seg=32, bias=-13, rings=(.15,))
    # axis crossing angle: work-parallel line, tool axis, arc between them

    def xang(s_):
        P0 = C1
        a = s_.P(P0)
        b = s_.P(lin(P0, (150, (0, 0, 1))))
        c = s_.P(lin(P0, (150, up)))
        arc_ = [s_.P(lin(P0, (90 * math.sin(math.radians(t)), (1, 0, 0)), (90 * math.cos(math.radians(t)), (0, 0, 1)))) for t in range(0, 23, 2)]
        return path("M%s %sL%s %sM%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(a[0]), n(a[1]), n(c[0]), n(c[1])), "cl") + \
            path(P(arc_, False), "a")
    sc.top.append(xang)
    sc.rot((tc[0], tc[1], 200), (0, 0, 1), 160, "", 200, 320)
    sc.rot(lin(C1, (60, up)), up, 46, "", 200, 320)
    sc.note((tc[0], tc[1] + 64 - 44, 186), "スカイビングカッタ", "歯車形の工具を傾けて高速で同期回転させる")
    sc.note((tc[0] - 99, tc[1] - 99, 168), "工作物（内歯車）", "リングギヤの内歯を連続して削る")
    sc.note(lin(C1, (90 * math.sin(math.radians(11)), (1, 0, 0)), (90 * math.cos(math.radians(11)), (0, 0, 1))), "軸交差角", "工具軸を傾けることで歯すじ方向に滑りが生まれ、削れる")
    sc.note((80, -70, 420), "主軸頭", "工具を回し、歯幅方向に送る")
    sc.note((210, -20, 560), "コラム", "主軸頭を支える")
    sc.note((260, -220, 50), "ベッド", "機械の土台")


# =====================================================================================
@mt("edm", az=-30, el=24)
def _(sc):
    block(sc, -270, -210, 0, 540, 420, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -280, -220, 12, 560, 440, 78, "pt", ch=14, b=3, bias=900)
    seams(sc, [[(-60, -220.2, 20), (-60, -220.2, 84)]], ((-61, -221, 20), (-59, -220, 84)), "gr")
    # XY table: saddle + table, tank (back/left walls full, front/right cut low), work stands, work
    block(sc, -195, -205, 90, 320, 290, 14, "pt", ch=4, b=1.5, bias=800)
    block(sc, -205, -198, 104, 340, 276, 16, "m", ch=2, b=1.5, bias=790)
    block(sc, -190, -190, 120, 310, 270, 6, "dk", b=0, dark=0, bias=700)
    block(sc, -190, 70, 126, 310, 10, 120, "dk", b=1, dark=0, bias=690)
    block(sc, -190, -190, 126, 10, 260, 120, "dk", b=1, dark=0, bias=680)
    block(sc, 110, -190, 126, 10, 260, 20, "dk", b=1, dark=0, bias=660)
    block(sc, -180, -190, 126, 290, 8, 20, "dk", b=1, dark=0, bias=650)
    for y in (-118, -24):
        block(sc, -170, y, 126, 270, 12, 44, "m", b=1, bias=600)
    block(sc, -110, -120, 170, 150, 110, 60, "w", b=1.5, dark=0, bias=200)

    def kerf(s_):
        q = [s_.P(p) for p in ((-80, -90, 230.2), (-80, -51, 230.2), (-30, -51, 230.2))]
        h = s_.P((-80, -90, 230.2))
        return path(P(q, False), "kerf") + '<circle class="bg" cx="%s" cy="%s" r="%s"/>' % (n(h[0]), n(h[1]), n(2.6 * s_.cam.s))
    sc.raw(kerf, ((-80, -90, 230), (-30, -51, 230.4)), bias=190)
    # lower arm through the low right wall, lower nozzle
    block(sc, -48, -61, 148, 178, 20, 16, "pt", ch=2, b=1.5, bias=150)
    MCYL(sc, (-30, -51, 164), (0, 0, 1), 8, 6, "w", seg=16, bands=6, bias=140)
    # dielectric water (translucent, drawn over the submerged work)
    abox(sc, (-180, -182, 126), (110, 70, 236), "fl", "z", bias=100)
    # column, upper arm, upper head (U/V) and nozzle, wire spool and power supply
    block(sc, 130, -60, 90, 140, 240, 470, "pt", ch=10, b=3, bias=400)
    block(sc, 140, -61.4, 500, 120, 1.4, 16, "dk", b=0, dark=0, bias=399)
    block(sc, -60, -80, 306, 190, 60, 50, "pt", ch=6, b=2.5, bias=100)
    block(sc, -56, -78, 246, 50, 54, 60, "pt", ch=4, b=2, bias=90)
    servo(sc, (-6, -51, 276), "x", 24, 30)
    MCYL(sc, (-30, -51, 246), (0, 0, -1), 9, 8, "w", seg=16, bands=6, bias=80)
    MCYL(sc, (-30, -51, 238), (0, 0, -1), 9, 2, "w", r1=5, seg=16, bands=6, bias=79)

    def wire(s_):
        a, b = s_.P((-30, -51, 236)), s_.P((-30, -51, 170))
        return '<path class="wire" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    sc.raw(wire, ((-31, -52, 170), (-29, -50, 236)), bias=50)

    def sparks(s_):
        p = s_.P((-30, -51, 231))
        o = ""
        for k in range(7):
            t = math.radians(k * 51 + 10)
            o += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(p[0] + 8 * math.cos(t)), n(p[1] + 5 * math.sin(t)))
        return path(o, "spark")
    sc.raw(sparks, ((-34, -55, 230), (-26, -47, 232)), bias=40)
    MCYL(sc, (150, 40, 520), (1, 0, 0), 46, 40, "cu", bias=-20, seg=36, bands=12, dark=0, rings=(.5,))
    MCYL(sc, (140, 40, 520), (1, 0, 0), 54, 10, "pt", bias=-19, seg=36, rings=())
    MCYL(sc, (190, 40, 520), (1, 0, 0), 54, 6, "pt", bias=-21, seg=36, rings=())
    block(sc, -260, 120, 90, 120, 100, 240, "dk", ch=6, b=2, dark=0, bias=600)

    def vents(s_):
        o = ""
        for k in range(8):
            z = 120 + 10 * k
            a, b = s_.P((-250, 119.8, z)), s_.P((-150, 119.8, z))
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        q = [s_.P(p) for p in ((-245, 119.7, 270), (-175, 119.7, 270), (-175, 119.7, 310), (-245, 119.7, 310))]
        return path(o, "mgrid") + path(P(q), "scrn")
    sc.raw(vents, ((-250, 119, 120), (-150, 120, 310)), bias=590)
    sc.axis((-200, -210, 260), (-60, -210, 260), "X")
    sc.axis((-230, -200, 160), (-230, -80, 160), "Y", off=(-12, 0))
    sc.note((-30, -51, 260), "ワイヤ電極", "細い真ちゅう線などに電圧をかけ、放電で金属を溶かす")
    sc.note((-30, -76, 400), "上ガイド（上アーム）", "ワイヤを位置決めし、傾けてテーパも切れる")
    sc.note((40, -61, 160), "下アーム", "ワイヤの下側を支える")
    sc.note((-100, -120, 200), "工作物", "焼入れ鋼や超硬でも、通電すれば加工できる")
    sc.note((-180, -190, 200), "加工槽", "絶縁性の加工液（水・油）に浸して加工する")
    sc.note((170, 40, 560), "ワイヤボビン", "ワイヤを連続して送り出す")
    sc.note((-200, 120, 300), "加工電源", "放電のパルスをつくる電源")


# =====================================================================================
@mt("laser-machine", az=-32, el=28)
def _(sc):
    block(sc, -310, -190, 0, 620, 380, 12, "dk", ch=8, b=0, dark=0, bias=920)
    block(sc, -320, -200, 12, 640, 400, 108, "pt", ch=12, b=3, bias=900)
    seams(sc, [[(-100, -200.2, 22), (-100, -200.2, 112)], [(120, -200.2, 22), (120, -200.2, 112)]], ((-100, -201, 22), (120, -200, 112)), "gr")
    # X rails with the gantry carriages, pallet with serrated slats, sheet with finished cut-outs
    for y in (-192, 192):
        rail(sc, (-318, y, 120), "x", 636, "z", w=16, h=12, carriages=[(338, 62)], pitch=60, bias=700)
    block(sc, -300, -180, 120, 600, 360, 16, "dk", b=1, dark=0, bias=650)

    def slats(s_):
        d = ""
        for k in range(1, 30):
            x = -300 + k * 20
            q = [s_.P((x, -178 + 6 * j, 136 + (4 if j % 2 else 0))) for j in range(60)]
            d += P(q, False)
        return path(d, "mgrid")
    sc.raw(slats, ((-300, -180, 136), (300, 180, 140.5)), bias=640)
    block(sc, -250, -140, 141, 420, 270, 3, "w", b=0, dark=0, bias=600)

    def cut(s_):
        o = ""
        for x0, y0 in ((-220, -110), (-140, -110), (-220, 10)):
            q = [s_.P((x0 + dx, y0 + dy, 144.2)) for dx, dy in ((6, 0), (54, 0), (60, 6), (60, 84), (54, 90), (6, 90), (0, 84), (0, 6))]
            o += P(q)
        k = [s_.P((x, 10 + 40 * math.sin((x + 200) / 60), 144.2)) for x in range(-60, 112, 6)]
        return path(o, "dks4") + path(P(k, False), "kerf")
    sc.raw(cut, ((-220, -110, 144), (110, 100, 144.4)), bias=590)
    # gantry: legs on the carriages, beam, Y rail, Z carriage, cutting head, nozzle
    for y in (-226, 182):
        block(sc, 22, y, 134, 56, 44, 56, "pt", ch=3, b=2, bias=300)
    block(sc, 20, -232, 190, 60, 464, 56, "pt", ch=6, b=3, bias=280)
    rail(sc, (80, -210, 214), "y", 420, (1, 0, 0), w=14, h=8, carriages=[(184, 50)], pitch=60, bias=250)
    block(sc, 92, -22, 196, 44, 64, 104, "pt", ch=4, b=2, bias=100)
    servo(sc, (114, 10, 300), "z", 26, 34, up=(1, 0, 0))
    MCYL(sc, (108, 10, 196), (0, 0, -1), 15, 34, "dk", seg=24, dark=0, rings=(.3,), bias=80)
    MCYL(sc, (108, 10, 162), (0, 0, -1), 13, 10, "w", seg=24, bias=70)
    MCYL(sc, (108, 10, 152), (0, 0, -1), 9, 7, "cu", r1=4, seg=20, bands=6, dark=0, bias=60)

    def beam(s_):
        p = s_.P((108, 10, 144.5))
        o = ""
        for k in range(9):
            t = math.radians(-170 + k * 20)
            o += "M%s %sL%s %s" % (n(p[0]), n(p[1]), n(p[0] + 13 * math.cos(t)), n(p[1] + 7 * math.sin(t)))
        return path(o, "spark")
    sc.raw(beam, ((104, 6, 144), (112, 14, 145)), bias=30)
    # laser oscillator with vents
    block(sc, -340, 220, 0, 160, 120, 200, "dk", ch=8, b=2, dark=0, bias=800)

    def vents(s_):
        o = ""
        for k in range(10):
            z = 40 + 12 * k
            a, b = s_.P((-330, 219.8, z)), s_.P((-250, 219.8, z))
            o += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return path(o, "mgrid")
    sc.raw(vents, ((-330, 219, 40), (-250, 220, 160)), bias=790)
    sc.axis((-150, -240, 220), (0, -240, 220), "X")
    sc.axis((170, -120, 220), (170, 60, 220), "Y", off=(14, 0))
    sc.note((108, 10, 175), "加工ヘッド", "レンズで光を集め、ノズルからアシストガスを吹く")
    sc.note((50, -232, 240), "ガントリ", "ヘッドを載せてX・Y方向に動く門形の梁")
    sc.note((-120, -60, 144), "加工中の板材", "光の熱で溶かし、ガスで吹き飛ばして切る")
    sc.note((-260, 220, 150), "レーザ発振器", "ファイバレーザなどで光をつくる")
    sc.note((-300, -180, 128), "パレット", "剣山状の受けで板を支える")
    sc.note((280, -200, 60), "フレーム", "機械の土台")
