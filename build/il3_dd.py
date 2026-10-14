"""v3 shaded-3D detail + process drawings (480x300) for drivetrain.gear, drivetrain.hypoid and ev.reducer.
Replaces the flat elevation/section op sheets of il_d_drive / il_d_ev; the gear-cutting scenes of il_gscene
(hobbing, chamfering, shaving, gear grinding, mesh test, hypoid cutting / lapping) are reused as they are."""
import math
import il_gear as GE
from il_base import *
from il_detail import title, bal, tol, lead, fin, Pl
from il_dmap import dpart
from il3_lib import fit, compact, circ3, hole3, arc3, arrow3, P
from il_pictos import chart
import il_d_drive as D
import il_d_ev as V

PI = math.pi
ZA = (0, 0, 1)


# =====================================================================================
# common helpers
# =====================================================================================
def S3(fn, az, el, area, **kw):
    """fit fn into area of the 480x300 canvas -> (svg, final camera)."""
    s, sc = fit(fn, az, el, area, ret_scene=True, **kw)
    return s, sc.cam


def wpt(O, A, u, v, t=0.0):
    E1, E2, A_ = GE.frame(A)
    return tuple(O[i] + u * E1[i] + v * E2[i] + t * A_[i] for i in range(3))


def oline(cam, O, A, loop, t=0.0, close=True):
    return P([cam.xy(wpt(O, A, u, v, t)) for u, v, *_ in loop], close)


def c3(cam, C, A, r, cls, seg=40):
    return path(P(circ3(cam, C, A, r, seg)), cls)


def arc_vis(cam, C, A, r, cls="mf", seg=48, side=1):
    """visible (front) half of a circle edge: points whose radial direction faces the camera (side=1)."""
    E1, E2, _ = GE.frame(A)
    pts_, best = [], []
    for k in range(seg + 1):
        t = 2 * PI * k / seg
        d = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
        if GE._dot(d, cam.D) * side < 0:
            best.append(cam.xy(tuple(C[i] + r * d[i] for i in range(3))))
        elif best:
            pts_.append(best)
            best = []
    if best:
        pts_.append(best)
    if len(pts_) > 1 and GE._dot((E1[0], E1[1], E1[2]), cam.D) * side < 0:
        pts_ = [pts_[-1] + pts_[0]] + pts_[1:-1]
    return "".join(path(P(p, False), cls) for p in pts_ if len(p) > 1)


def offset_loop(loop, d):
    """shift a closed outline inward by d (per-vertex normal)."""
    N = len(loop)
    out = []
    ar = sum(loop[i][0] * loop[(i + 1) % N][1] - loop[(i + 1) % N][0] * loop[i][1] for i in range(N))
    sg = 1 if ar > 0 else -1
    for i in range(N):
        (x0, y0), (x1, y1) = loop[i - 1][:2], loop[(i + 1) % N][:2]
        tx, ty = x1 - x0, y1 - y0
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L * sg, tx / L * sg          # inward normal for a CCW loop
        out.append((loop[i][0] + nx * d, loop[i][1] + ny * d))
    return out


def zbox(cam, x, y, z, sx, sy, sz, mat="pt", **kw):
    """axis-aligned box from corner (x, y, z) (no Scene)."""
    xy = [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)]
    return compact(GE.prism(cam, (0, 0, z), ZA, [(-q[1], q[0], i) for i, q in enumerate(xy)], sz, mat, **kw))


def disc(cam, O, A, r, h, mat="m", seg=36, feat=8, **kw):
    return compact(GE.prism(cam, O, A, GE.circle_outline(r, seg, feat), h, mat, smooth=True, **kw))


def front_ang(cam):
    """azimuth (rad) in the xy plane of the direction facing the camera."""
    return math.atan2(-cam.D[1], -cam.D[0])


def label(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


# =====================================================================================
# transmission gear model: helical tooth rim, recessed web, hub with spline (or plain) bore.
# axis A from base point O. Dimensions as the part drawing (il3_drive.tm_gear).
# =====================================================================================
GZ, GRP, GH, GHX, GRB, GZW, GHUB = 32, 96.0, 40.0, 21.0, 72.0, 24.0, 46.0
GTW = GH * math.tan(math.radians(GHX)) / GRP


GOUT = GE.gear_outline(GZ, GRP, nf=2, fillet=False)


def gear_svg(cam, O=(0, 0, 0), A=ZA, mat="w", teeth=True, spl=True, ro=101.0):
    if teeth:
        o = compact(GE.prism(cam, O, A, GOUT, GH, mat, holes=[GE.circle_outline(GRB, 32, 32)], twist=GTW))
    else:
        o = compact(GE.prism(cam, O, A, GE.circle_outline(ro, 64, 16), GH, mat, holes=[GE.circle_outline(GRB, 40, 40)], smooth="outer"))
    a = GE._norm(A)
    pw = tuple(O[i] + a[i] * GZW for i in range(3))
    pt_ = tuple(O[i] + a[i] * GH for i in range(3))
    ph = tuple(O[i] + a[i] * (GHUB + .1) for i in range(3))
    from il3_drive import clip_poly
    web = clip_poly(circ3(cam, pw, A, GRB, 40), circ3(cam, pt_, A, GRB, 40))
    if web:
        o += path(P(web), mat)
    o += compact(GE.prism(cam, pw, A, GE.circle_outline(44, 32, 8), GHUB - GZW, mat, smooth=True))
    if spl:
        o += path(oline(cam, ph, A, GE.spline_outline(20, 30, 26.5)), "bg")
    else:
        o += path(P(circ3(cam, ph, A, 28, 32)), "bg")
    return o


def top_outline(cam=None):
    """gear outline on the top face (z = GH), rotated by the helix twist."""
    return GE.rotate_outline(GOUT, GTW)


def root_segs(cam, loop, z, keep):
    """screen polylines along each tooth root (lower flank - root - lower flank) for teeth with keep(angle)."""
    N = len(loop)
    segs = []
    for i in range(N):
        if loop[i][2] % 4 == 3 and loop[i - 1][2] % 4 != 3:
            idx = [i - 2, i - 1, i, i + 1, i + 2, i + 3]
            q = [loop[j % N] for j in idx]
            a = math.atan2(q[2][1], q[2][0])
            if keep(a):
                segs.append([cam.xy((u, v, z)) for u, v, f in q])
    return segs


# =====================================================================================
# drivetrain.gear — detail
# =====================================================================================
@dpart("drivetrain.gear", "detail")
def gear_detail3():
    def fn(sc):
        return gear_svg(sc.cam)
    s, cam = S3(fn, -28, 36, (18, 40, 292, 272), sh_k=.48, sh_ry=9)
    pl = Pl(330, 150, 1.4)
    s += rect(300, 34, 150, 232, "m", 4) + text(375, 50, "断面", "middle", "sm")
    s += pl.g(D.gear_sec()) + pl.g(rect(12, 65, 36, 7, "hotband"))
    notes = [("歯（歯面）", "はすば歯。歯形・歯すじ誤差はJIS N4〜5級、研削・ホーニング仕上げ"),
             ("歯底・歯元", "曲げ疲労の起点。浸炭＋ショットピーニングで強化"),
             ("内径スプライン", "シャフトと結合。オーバーピン寸法を管理"),
             ("端面", "歯切り・研削の基準面。振れを管理"),
             ("浸炭硬化層", "有効硬化層0.6〜1.0mm、表面HRC58〜62")]
    fa = front_ang(cam)
    a1 = cam.xy((GRP * 1.01 * math.cos(fa + .55), GRP * 1.01 * math.sin(fa + .55), GH * .5))
    a2 = cam.xy((GRP * .9 * math.cos(fa - .9), GRP * .9 * math.sin(fa - .9), GH))
    a3 = cam.xy((27 * math.cos(fa), 27 * math.sin(fa), GHUB))
    s += bal(a1[0], a1[1], 286, 236, 1)
    s += bal(a2[0], a2[1], 30, 254, 2)
    s += bal(a3[0], a3[1], 160, 284, 3)
    s += bal(*pl(48, -50), 440, 80, 4)
    s += bal(*pl(30, 68), 440, 250, 5)
    return s, notes


# =====================================================================================
# drivetrain.gear — ops
# =====================================================================================
def g_forge():
    s = title("棒鋼を加熱して、ギヤブランクに型鍛造")

    def fn(sc):
        cam = sc.cam
        o = compact(GE.prism(cam, (-260, 0, -40), ZA, GE.circle_outline(26, 28, 8), 80, "h", smooth=True))
        o += disc(cam, (0, 0, -60), ZA, 132, 60, "t", seg=48, dark=.6)
        o += c3(cam, (0, 0, .2), ZA, 108, "ts3", 48)
        o += gear_svg(cam, (0, 0, 0), mat="h", teeth=False, spl=False, ro=104)
        o += disc(cam, (0, 0, 120), ZA, 132, 40, "t", seg=48, dark=.6)
        return o
    b, cam = S3(fn, -20, 30, (24, 44, 452, 266), sh_k=.5)
    s += b
    x, y = cam.xy((-260, 0, 40))
    s += heat(x - 12, y - 30, 3, 12, 14)
    s += arrow3(cam, (-215, 0, 0), (-150, 0, 0))
    bx, by = cam.xy((-260, -26, -40))
    s += text(bx, by + 30, "加熱ビレット", "middle")
    p0, p1 = cam.xy((150, 0, 200)), cam.xy((150, 0, 130))
    s += arrow(p0[0] + 40, p0[1], p1[0] + 40, p1[1], None) + label(p0[0] + 48, (p0[1] + p1[1]) / 2 + 4, "加圧", "start")
    return s


def g_anneal():
    s = title("被削性と熱処理ひずみの安定のため、等温焼鈍で組織を整える")

    def fn(sc):
        cam = sc.cam
        o = zbox(cam, -150, -70, -30, 380, 140, 140, "pt", dark=1)
        op = [(-150.2, -46, -6), (-150.2, 46, -6), (-150.2, 46, 64), (-150.2, -46, 64)]
        o += path(P([cam.xy(p) for p in op]), "bg") + path(P([cam.xy(p) for p in op]), "hotin")
        for x in (-80, 0, 80, 160):
            o += hole3(cam, (x, -70.2, 80), (0, -1, 0), 7, "ms3", 14)
        o += zbox(cam, -330, -52, -26, 180, 104, 12, "m", dark=1)
        for x in range(-322, -150, 22):
            o += compact(GE.prism(cam, (x, -50, -8), (0, 1, 0), GE.circle_outline(6, 14, 4), 100, "m", smooth=True, lines=False))
        for x in (-300, -244, -188):
            o += compact(GE.prism(cam, (x, 0, -2), ZA, GE.circle_outline(34, 32, 8), 16, "w", holes=[GE.circle_outline(13, 20, 20)], smooth=True))
        return o
    b, cam = S3(fn, 32, 24, (16, 40, 318, 262), sh_k=.5)
    s += b
    # isothermal annealing cycle
    x0, y0, w, h = 336, 62, 132, 120
    s += rect(x0, y0, w, h, "m", 4)
    s += line(x0 + 12, y0 + h - 16, x0 + w - 8, y0 + h - 16, "o thin") + line(x0 + 12, y0 + 10, x0 + 12, y0 + h - 16, "o thin")
    s += path("M%s %s L%s %s L%s %s L%s %s L%s %s L%s %s L%s %s" % (
        n(x0 + 12), n(y0 + h - 18), n(x0 + 30), n(y0 + 22), n(x0 + 52), n(y0 + 22), n(x0 + 60), n(y0 + 52),
        n(x0 + 98), n(y0 + 52), n(x0 + 120), n(y0 + h - 22), n(x0 + 124), n(y0 + h - 22)), "a")
    s += text(x0 + 40, y0 + 16, "加熱", "middle", "sm") + text(x0 + 80, y0 + 46, "等温保持", "middle", "sm")
    s += text(x0 + w - 8, y0 + h - 4, "時間", "end", "sm") + text(x0 + 16, y0 + h - 4, "温度", "start", "sm")
    s += tol(40, 286, "硬さ・フェライト＋パーライト組織の均一性")
    return s


def g_turn():
    s = title("内径・端面・外径を旋削し、歯切りの基準をつくる")
    A = (0, -1, 0)

    def jaw(cam, t):
        c, s_ = math.cos(math.radians(t)), math.sin(math.radians(t))
        loop = [(c * 101 - s_ * 9, s_ * 101 + c * 9, 0), (c * 101 + s_ * 9, s_ * 101 - c * 9, 1),
                (c * 124 + s_ * 9, s_ * 124 - c * 9, 2), (c * 124 - s_ * 9, s_ * 124 + c * 9, 3)]
        return compact(GE.prism(cam, (0, 0, 0), A, loop, 14, "dk"))

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 50, 0), A, 126, 50, "m", seg=48, dark=1)
        o += jaw(cam, 210) + jaw(cam, 330)
        o += gear_svg(cam, (0, 0, 0), A, teeth=False, spl=False)
        o += jaw(cam, 90)
        # boring bar in the bore, turning tool on the OD
        o += compact(GE.prism(cam, (40, -26, 104), ZA, [(-7, -7, 0), (7, -7, 1), (7, 7, 2), (-7, 7, 3)], 90, "t", dark=.5))
        o += compact(GE.prism(cam, (40, -26, 101), ZA, [(-8, -2, 0), (2, -9, 1), (9, 5, 2)], 5, "gw"))
        return o
    b, cam = S3(fn, 38, 16, (40, 36, 330, 270), sh_k=.5)
    s += b
    s += arc_vis(cam, (0, -40, 0), A, 101) + c3(cam, (0, -GHUB, 0), A, 28, "mfe", 28) + c3(cam, (0, -GHUB, 0), A, 44, "mfe", 36)
    s += arc_vis(cam, (0, -40, 0), A, 72, "mfe", side=-1)
    p0, p1 = cam.xy((60, -26, 150)), cam.xy((60, 10, 150))
    s += arrow(p0[0], p0[1], p1[0], p1[1], None) + label(p1[0] + 6, p1[1] - 4, "送り", "start")
    s += arc3(cam, (0, -50, 0), A, 118, 200, 250)
    fx, fy = cam.xy((0, -GHUB, 38 * .7))
    s += lead(fx + 10, fy - 10, 326, 130, "端面振れ（歯切りの基準）")
    s += tol(40, 290, "2主軸対向旋盤・ガントリーローダで自動化")
    return s


def g_broach():
    s = title("内径スプラインをブローチで加工")
    spl = GE.spline_outline(20, 30, 26.5)

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 0, -150), ZA, 20, 130, "t", seg=20, feat=6)
        o += disc(cam, (0, 0, -168), ZA, 28, 22, "m", seg=20, feat=6)
        o += disc(cam, (0, 0, -22), ZA, 128, 22, "m", dark=.8)
        o += gear_svg(cam, (0, 0, 0))
        o += disc(cam, (0, 0, GHUB - 20), ZA, 22, 120, "t", seg=20, feat=6)
        o += disc(cam, (0, 0, GHUB + 100), ZA, 30, 30, "m", seg=20, feat=6)
        return o
    b, cam = S3(fn, -28, 32, (40, 36, 300, 282), sh=False)
    s += b
    s += path(oline(cam, (0, 0, GHUB + .2), ZA, spl), "mfe")
    p0, p1 = cam.xy((0, 0, -60)), cam.xy((0, 0, -140))
    s += arrow(p0[0] + 60, p0[1], p1[0] + 60, p1[1], None) + label(p0[0] + 68, (p0[1] + p1[1]) / 2 + 4, "引き抜き", "start")
    tx, ty = cam.xy((0, 0, GHUB + 60))
    s += text(tx + 30, ty, "ブローチ", "start", "al")
    cx, cy = 404, 96
    s += circ(cx, cy, 40, "w") + path(GE.outline_d(GE.spline_outline(20, 26, 20.5), cx, cy), "bg") + \
        path(GE.outline_d(GE.spline_outline(20, 26, 20.5), cx, cy), "mfo")
    s += text(cx, cy + 58, "加工後の内スプライン", "middle", "sm") + tol(20, 290, "オーバーピン寸法・ねじれ")
    return s


def g_carb():
    s = title("浸炭焼入れで歯の表面だけを硬くする（930℃前後）")
    out = top_outline()

    def fn(sc):
        return gear_svg(sc.cam)
    b, cam = S3(fn, -28, 36, (16, 40, 254, 270), sh_k=.48)
    s += b
    inner = offset_loop(out, 5.5)
    s += '<path class="hotband" fill-rule="evenodd" d="%s%s"/>' % (oline(cam, (0, 0, GH), ZA, out), oline(cam, (0, 0, GH), ZA, inner[::-1]))
    fa = front_ang(cam)
    ax, ay = cam.xy((GRP * math.cos(fa - 1.2), GRP * math.sin(fa - 1.2), GH))
    s += lead(ax, ay, 60, 54, "浸炭層（歯部）", "start")
    s += rect(268, 64, 196, 170, "m", 4) + text(366, 82, "硬さ分布（イメージ）", "middle", "sm")
    s += line(286, 212, 452, 212, "o") + line(286, 94, 286, 212, "o")
    s += path("M288 104 L328 106 Q358 114 378 162 L448 182", "a") + line(286, 152, 448, 152, "o thin dash")
    s += text(288, 228, "表面", "start", "sm") + text(450, 228, "深さ", "end", "sm") + text(372, 146, "有効硬化層", "start", "sm")
    s += tol(20, 290, "表面HRC58〜62・有効硬化層・熱処理ひずみ")
    return s


def g_peen():
    s = title("歯元に投射材を打ち付け、圧縮残留応力で曲げ疲労強度を上げる")
    out = top_outline()
    N = (-.5, .3, -.81)

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 0, -24), ZA, 120, 24, "m", dark=.8)
        o += gear_svg(cam)
        o += compact(GE.prism(cam, (120, -60, 200), N, GE.circle_outline(14, 20, 6), 60, "t", smooth=True))
        o += compact(GE.prism(cam, (150, -78, 250), N, GE.circle_outline(22, 24, 8), 60, "m", smooth=True, dark=.5))
        return o
    b, cam = S3(fn, -28, 36, (30, 36, 330, 270), sh_k=.45)
    s += b
    fa = front_ang(cam)
    segs = root_segs(cam, out, GH, lambda a: abs(math.atan2(math.sin(a - fa), math.cos(a - fa))) < 1.3)
    s += "".join(path(P(sg, False), "mf") for sg in segs)
    # shot stream from the nozzle onto the teeth
    nx, ny = cam.xy((120, -60, 200))
    tx, ty = cam.xy((GRP * math.cos(fa + .2), GRP * math.sin(fa + .2), GH))
    for i in range(30):
        t = ((i * 37) % 29) / 29 * .9 + .08
        sp = ((i * 53) % 21 - 10) / 10
        x = nx + (tx - nx) * t + sp * 26 * t
        y = ny + (ty - ny) * t + sp * 10 * t
        s += circ(x, y, 2.4, "shot")
    s += arrow(nx - 4, ny + 8, nx + (tx - nx) * .5 - 8, ny + (ty - ny) * .5, None)
    s += arc3(cam, (0, 0, 0), ZA, 136, 200, 260)
    if segs:
        r0 = segs[len(segs) // 2]
        mx, my = r0[len(r0) // 2]
        s += lead(mx, my, 300, 250, "歯元R（圧縮残留応力を付与）", "start")
    s += tol(20, 290, "カバレージ・アークハイト")
    return s


def g_bore():
    s = title("歯面を基準にチャックし、内径と端面を研削")
    out = top_outline()

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 0, -34), ZA, 122, 34, "m", dark=.8)
        o += gear_svg(cam)
        # pitch-circle pins in the tooth spaces (top ends seen above the face)
        fa = front_ang(cam)
        pins = []
        for k in range(GZ):
            a = GTW + 2 * PI * (k + .5) / GZ
            pins.append((GE._dot((math.cos(a), math.sin(a), 0), cam.D), a))
        for d, a in sorted(pins, reverse=True)[1::5]:
            o += compact(GE.prism(cam, (GRP * .97 * math.cos(a), GRP * .97 * math.sin(a), GH), ZA, GE.circle_outline(4.2, 10, 3), 8, "dk",
                                  smooth=True, lines=False))
        o += compact(GE.prism(cam, (10, 6, GHUB - 4), ZA, GE.circle_outline(16, 24, 8), 16, "gw", smooth=True))
        o += compact(GE.prism(cam, (10, 6, GHUB + 12), ZA, GE.circle_outline(7, 16, 4), 110, "t", smooth=True))
        o += compact(GE.prism(cam, (10, 6, GHUB + 122), ZA, GE.circle_outline(30, 28, 8), 60, "m", smooth=True, dark=.5))
        return o
    b, cam = S3(fn, -28, 36, (60, 34, 330, 272), sh_k=.45)
    s += b
    s += c3(cam, (0, 0, GHUB), ZA, 44, "mfe", 36) + arc_vis(cam, (0, 0, GHUB), ZA, 28, "mf", side=-1)
    s += arc3(cam, (10, 6, GHUB + 30), ZA, 30, 230, 330)
    s += arc3(cam, (0, 0, 0), ZA, 140, 200, 260)
    fa = front_ang(cam)
    best = max(range(GZ), key=lambda k: math.cos(GTW + 2 * PI * (k + .5) / GZ - fa - .9))
    a = GTW + 2 * PI * (best + .5) / GZ
    px, py = cam.xy((GRP * .97 * math.cos(a), GRP * .97 * math.sin(a), GH + 8))
    s += lead(px, py, 24, 262, "ピッチ円チャック（歯溝にピン）", "start")
    gx, gy = cam.xy((10, 6, GHUB + 80))
    s += text(gx + 10, gy + 4, "内研砥石", "start", "al")
    s += tol(300, 286, "内径と歯面の同軸度・端面振れ")
    return s


@dpart("drivetrain.gear", "ops")
def gear_ops3():
    old = D.gear_ops()
    new = [g_forge(), g_anneal(), g_turn(), None, None, None, g_broach(), g_carb(), g_peen(), g_bore(), None, None]
    return [fin(x) if x is not None else old[i] for i, x in enumerate(new)]


# =====================================================================================
# drivetrain.hypoid — ring gear lying flat + drive pinion (model as il3_drive.hypoid)
# =====================================================================================
HTH = -28


def _hrot(x, y, z):
    c, s_ = math.cos(math.radians(HTH)), math.sin(math.radians(HTH))
    return (x * c - y * s_, x * s_ + y * c, z)


H_TZ = -16 + 26 + (118 - 70) * .16
H_A = GE._norm(_hrot(-1, 0, -.3))
H_O = _hrot(134, -30, H_TZ + 37)


def ring_lean(cam, O, r_in, r_out, h, z, mat="w", spiral=.6, nholes=10, nr=2):
    """il3_drive.ring_lite with fewer radial facets per tooth (same look, smaller svg)."""
    import il3_drive as DR
    o = compact(GE.prism(cam, O, (0, 0, 1), GE.circle_outline(r_out, 56, 14), h, mat, caps=False, smooth=True))
    tz = O[2] + h
    dep = (r_out - r_in) * .16
    bo = r_in * .62
    ring = lambda r, zz, k=48: [cam.xy((O[0] + r * math.cos(2 * PI * q / k), O[1] + r * math.sin(2 * PI * q / k), zz)) for q in range(k)]
    o += '<path class="%ss3" fill-rule="evenodd" d="%s%s"/>' % (mat, P(ring(r_out, tz)), P(ring(r_in, tz)[::-1]))
    o += '<path class="%s" fill-rule="evenodd" d="%s%s"/>' % (mat, P(ring(r_in, tz)), P(ring(bo, tz)[::-1]))
    rh = (r_in + bo) / 2
    for k in range(nholes):
        a = 2 * PI * (k + .5) / nholes
        o += hole3(cam, (O[0] + rh * math.cos(a), O[1] + rh * math.sin(a), tz + .05), (0, 0, 1), 4.4, "bg", 10)
    step = 2 * PI / z
    items = []
    for i in range(z):
        c = i * step
        tw = step * .26

        def pt(r, sg, top):
            fr = (r - r_in) / (r_out - r_in)
            a = c + spiral * (fr - .5) ** 2 * 2.2 + spiral * fr * .9 + sg * tw * (.8 + .4 * fr) * (r_in + (r_out - r_in) * .5) / r
            return (O[0] + r * math.cos(a), O[1] + r * math.sin(a), tz + (dep if top else 0))
        rs = [r_in + (r_out - r_in) * q / nr for q in range(nr + 1)]
        tL, tR = [pt(r, -.55, 1) for r in rs], [pt(r, .55, 1) for r in rs]
        bL, bR = [pt(r, -1, 0) for r in rs], [pt(r, 1, 0) for r in rs]
        cm = c + spiral * .45
        tg = (-math.sin(cm), math.cos(cm), 0)
        for top, bot, sg in ((tL, bL, -1), (tR, bR, 1)):
            nrm = GE._norm(GE._cross(DR._sub(top[-1], top[0]), DR._sub(top[1], bot[1])))
            if GE._dot(nrm, tg) * sg < 0:
                nrm = (-nrm[0], -nrm[1], -nrm[2])
            if GE._dot(nrm, cam.D) > 0:
                continue
            pp = [cam.P(q) for q in bot + top[::-1]]
            items.append((sum(p[2] for p in pp) / len(pp) + .3, "%ss%d" % (mat, max(2, GE.shade(nrm))), "M" + " L".join(n(x) + " " + n(y) for x, y, _ in pp) + "Z", ""))
        pp = [cam.P(q) for q in tL + tR[::-1]]
        items.append((sum(p[2] for p in pp) / len(pp), mat + "s1", "M" + " L".join(n(x) + " " + n(y) for x, y, _ in pp) + "Z", ""))
        if GE._dot((math.cos(c), math.sin(c), 0), cam.D) < 0:
            pp = [cam.P(q) for q in (bL[-1], tL[-1], tR[-1], bR[-1])]
            items.append((pp[0][2] - .5, mat + "s2", "M" + " L".join(n(x) + " " + n(y) for x, y, _ in pp) + "Z", ""))
    return o + DR.render_q(items)


def hyp_svg(cam, mat="w", pinion=True, O=(0, 0, -16), nholes=10):
    o = ring_lean(cam, O, 70, 118, 26, 37, mat, nholes=nholes)
    if pinion:
        B = (-H_A[0], -H_A[1], -H_A[2])
        for L, r, x0 in ((16, 12, 92), (72, 16, 20), (20, 22, 0)):
            o += disc(cam, tuple(H_O[i] + B[i] * x0 for i in range(3)), B, r, L, mat, seg=20)
        o += compact(GE.prism(cam, H_O, H_A, GE.gear_outline(11, 34, phase=.1, nf=2), 50, mat, twist=.75, slices=3, scale=lambda t: 1 - .38 * t))
    return o


def pin_pt(d, r=0.0):
    """point on the pinion axis at distance d behind the head base (stem side), lifted by r toward +z."""
    return (H_O[0] - H_A[0] * d, H_O[1] - H_A[1] * d, H_O[2] - H_A[2] * d + r)


@dpart("drivetrain.hypoid", "detail")
def hypoid_detail3():
    def fn(sc):
        return hyp_svg(sc.cam)
    s, cam = S3(fn, 24, 34, (30, 40, 440, 280), sh_k=.48)
    notes = [("リングギヤ歯面", "まがりばかさ歯。歯当たり・歯面トポグラフィを管理"), ("ドライブピニオン", "軸がリングギヤ中心からずれた（オフセット）ハイポイド歯"),
             ("取付面・ボルト穴", "デフケースへの取付。振れ・平面度"), ("ピニオン軸受部", "プリロードを掛けて支持"), ("内径（はめ合い）", "デフケースに圧入・ボルト締結")]
    a1 = cam.xy((-60, -86, H_TZ + 2))
    a2 = cam.xy(tuple(H_O[i] + H_A[i] * 22 for i in range(2)) + (H_O[2] + H_A[2] * 22 + 20,))
    rh = (70 + 70 * .62) / 2
    t = 2 * PI * 7.5 / 10
    a3 = cam.xy((rh * math.cos(t), rh * math.sin(t), 10))
    a4 = cam.xy(pin_pt(50, 16))
    a5 = cam.xy((-43.4 * .7, 43.4 * .7, 10))
    s += bal(a1[0], a1[1], 60, 250, 1) + bal(a2[0], a2[1], 300, 56, 2) + bal(a3[0], a3[1], 200, 274, 3)
    s += bal(a4[0], a4[1], 452, 56, 4) + bal(a5[0], a5[1], 120, 52, 5)
    return s, notes


def h_forge():
    s = title("リングギヤ素材をリングローリング、ピニオンを熱間鍛造")

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (118, 0, -20), ZA, 36, 80, "t", seg=32, dark=.4)
        o += compact(GE.prism(cam, (0, 0, 0), ZA, GE.circle_outline(80, 56, 14), 40, "h", holes=[GE.circle_outline(50, 40, 40)], smooth="outer"))
        o += disc(cam, (38, 0, 18), ZA, 11, 90, "m", seg=20)
        # pinion forging (right)
        o += zbox(cam, 250, -60, -40, 170, 120, 40, "t", dark=.4)
        o += compact(GE.cyl(cam, (262, 0, 16), (1, 0, 0), 15, 76, "h", seg=24))
        o += compact(GE.prism(cam, (338, 0, 16), (1, 0, 0), GE.circle_outline(30, 32, 8), 50, "h", smooth=True, scale=lambda t: 1 - .3 * t))
        o += zbox(cam, 250, -60, 70, 170, 120, 40, "t", dark=.4)
        return o
    b, cam = S3(fn, 24, 30, (24, 40, 456, 262), sh_k=.55)
    s += b
    s += arc3(cam, (0, 0, 20), ZA, 98, 150, 230) + arc3(cam, (118, 0, 60), ZA, 44, 300, 360)
    mx, my = cam.xy((38, 0, 108))
    s += label(mx, my - 8, "マンドレル")
    p0, p1 = cam.xy((420, -60, 170)), cam.xy((420, -60, 116))
    s += arrow(p0[0] + 16, p0[1], p1[0] + 16, p1[1], None)
    px, py = cam.xy((335, -60, -40))
    s += text(px, py + 30, "ピニオン鍛造", "middle")
    rx, ry = cam.xy((0, -80, 0))
    s += text(rx, ry + 34, "リングローリング", "middle")
    return s


def h_turn():
    s = title("取付面・内径・外周を旋削")

    def jaw(cam, t):
        c, s_ = math.cos(math.radians(t)), math.sin(math.radians(t))
        xy = [(c * 30 - s_ * 8, s_ * 30 + c * 8), (c * 30 + s_ * 8, s_ * 30 - c * 8), (c * 48 + s_ * 8, s_ * 48 - c * 8), (c * 48 - s_ * 8, s_ * 48 + c * 8)]
        return compact(GE.prism(cam, (0, 0, -16), ZA, [(-q[1], q[0], i) for i, q in enumerate(xy)], 58, "dk"))

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 0, -40), ZA, 128, 24, "m", seg=48, dark=.8)
        o += compact(GE.prism(cam, (0, 0, -16), ZA, GE.circle_outline(118, 64, 16), 36, "w", holes=[GE.circle_outline(49, 40, 40)], smooth="outer"))
        o += jaw(cam, 60) + jaw(cam, 180) + jaw(cam, 300)
        o += zbox(cam, 92, -60, 24, 18, 18, 120, "t", dark=.4)
        o += compact(GE.prism(cam, (100, -52, 20), ZA, [(-6, -8, 0), (8, -2, 1), (2, 8, 2)], 5, "gw"))
        return o
    b, cam = S3(fn, 24, 34, (60, 36, 400, 270), sh_k=.5)
    s += b
    s += c3(cam, (0, 0, 20), ZA, 118, "mfe", 64) + c3(cam, (0, 0, 20), ZA, 49, "mfe", 40) + arc_vis(cam, (0, 0, -16), ZA, 118, "mf")
    s += arc3(cam, (0, 0, -16), ZA, 140, 200, 250)
    p0, p1 = cam.xy((160, -51, 150)), cam.xy((160, -51 + 50, 150))
    s += arrow(p0[0], p0[1], p1[0], p1[1], None) + label(p1[0] + 6, p1[1] + 4, "送り", "start")
    s += tol(24, 290, "取付面の振れ・平面度が歯当たりの基準")
    return s


def h_quench():
    s = title("浸炭焼入れ。リングギヤはプレスクエンチでひずみを抑える")

    def fn(sc):
        cam = sc.cam
        o = zbox(cam, -170, -150, -130, 340, 300, 100, "m", dark=1)
        q = [(-160, -140, -30.1), (160, -140, -30.1), (160, 140, -30.1), (-160, 140, -30.1)]
        o += path(P([cam.xy(p) for p in q]), "fl")
        o += disc(cam, (0, 0, -60), ZA, 112, 44, "t", seg=48, dark=.5)
        o += hyp_svg(cam, "h", pinion=False)
        o += disc(cam, (0, 0, 70), ZA, 112, 34, "t", seg=48, dark=.5)
        o += disc(cam, (0, 0, 104), ZA, 30, 60, "m", seg=24)
        return o
    b, cam = S3(fn, 24, 30, (60, 36, 380, 274), sh_k=.5)
    s += b
    p0, p1 = cam.xy((150, -100, 170)), cam.xy((150, -100, 110))
    s += arrow(p0[0] + 20, p0[1], p1[0] + 20, p1[1], None) + label(p0[0] + 28, (p0[1] + p1[1]) / 2 + 4, "金型で拘束", "start")
    ox, oy = cam.xy((-170, -150, -80))
    s += text(ox - 6, oy, "焼入れ油", "end", "sm")
    s += tol(40, 290, "平面度・真円度のひずみ")
    return s


def h_assy():
    s = title("デフケースにリングギヤを締結し、シムで予圧とバックラッシを調整")
    rh = (70 + 70 * .62) / 2
    bolt = 2 * PI * 8.5 / 10

    def fn(sc):
        cam = sc.cam
        o = disc(cam, (0, 0, -126), ZA, 64, 110, "w", seg=32, dark=.5, scale=lambda t: .55 + .45 * t)
        o += hyp_svg(cam, pinion=False, nholes=0)
        for k in range(10):
            t = 2 * PI * (k + .5) / 10
            o += c3(cam, (rh * math.cos(t), rh * math.sin(t), 10.2), ZA, 5.6, "dk", 10)
        o += disc(cam, (0, 0, 10), ZA, 40, 12, "w", seg=28, dark=.4)
        o += disc(cam, (0, 0, 22), ZA, 24, 34, "w", seg=28)
        o += compact(GE.prism(cam, (0, 0, 82), ZA, GE.circle_outline(32, 28, 7), 4, "dk", holes=[GE.circle_outline(24, 24, 6)], smooth=True))
        bx, by = rh * math.cos(bolt), rh * math.sin(bolt)
        o += disc(cam, (bx, by, 15), ZA, 8, 30, "t", seg=16)
        o += disc(cam, (bx, by, 45), ZA, 18, 80, "m", seg=24)
        return o
    b, cam = S3(fn, 24, 34, (80, 36, 400, 274), sh_k=.45)
    s += b
    s += arrow3(cam, (0, 0, 120), (0, 0, 92))
    sx, sy = cam.xy((-32, 0, 84))
    s += lead(sx, sy, 40, 120, "シム（自動選択）", "start")
    bx, by = rh * math.cos(bolt), rh * math.sin(bolt)
    s += arc3(cam, (bx, by, 100), ZA, 30, 200, 330)
    s += tol(300, 286, "プリロード・バックラッシ・歯当たり")
    return s


@dpart("drivetrain.hypoid", "ops")
def hypoid_ops3():
    old = D.hypoid_ops()
    new = [h_forge(), h_turn(), None, h_quench(), None, None, h_assy()]
    return [fin(x) if x is not None else old[i] for i, x in enumerate(new)]


# =====================================================================================
# ev.reducer — same gear sheets (as before) + vacuum carburizing furnace
# =====================================================================================
@dpart("ev.reducer", "detail")
def reducer_detail3():
    return gear_detail3()


def r_vac():
    s = title("低ひずみのため真空浸炭（減圧浸炭→高圧ガス冷却）")
    A = (0, -1, 0)
    sm_g = GE.gear_outline(15, 26, nf=1, fillet=False)

    def fn(sc):
        cam = sc.cam
        from il3_drive import clip_poly
        o = zbox(cam, -110, 20, -160, 220, 200, 34, "m", dark=1)
        mouth = circ3(cam, (0, -.1, 0), A, 106, 36)
        o += path(P(mouth), "ms3")
        back = clip_poly(circ3(cam, (0, 239, 0), A, 106, 36), mouth)
        if back:
            o += path(P(back), "bg") + path(P(back), "hotin")
        o += zbox(cam, -72, 30, -76, 144, 170, 8, "m")
        for x, y in ((-50, 100), (0, 100), (50, 100)):
            o += compact(GE.prism(cam, (x, y, -68), ZA, sm_g, 16, "h"))
            o += hole3(cam, (x, y, -51.9), ZA, 8, "hs3", 12)
        o += compact(GE.prism(cam, (0, 240, 0), A, GE.circle_outline(124, 44, 11), 240, "m", caps=False, smooth=True, dark=.6))
        sh = GE.shade((0, -1, 0), .6)
        cls = "m" if sh <= 2 else "ms%d" % sh
        o += '<path class="%s" fill-rule="evenodd" d="%s%s"/>' % (cls, P(circ3(cam, (0, -.1, 0), A, 124, 44)), P(mouth[::-1]))
        o += path(P(mouth), "el")
        o += disc(cam, (0, 120, 118), ZA, 26, 34, "m", seg=24)
        return o
    b, cam = S3(fn, 24, 20, (70, 36, 400, 270), sh_k=.5)
    s += b
    px, py = cam.xy((0, 120, 152))
    s += label(px + 34, py + 4, "真空ポンプ", "start")
    s += tol(40, 290, "ひずみ・有効硬化層（粒界酸化なし）")
    return s


@dpart("ev.reducer", "ops")
def reducer_ops3():
    g = gear_ops3()
    return [g[0], g[2], g[3], fin(r_vac()), g[9], g[10], g[11]]
