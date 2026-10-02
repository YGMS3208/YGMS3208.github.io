"""Machine-tool atlas illustrations: anatomy views of whole machines, close-ups of components,
automation cells. Built on the orthographic 3D engine in il_gear (painted castings + steel + tools).

Each drawing returns (svg_body, notes) where notes = [(label, short description), ...] matching the
numbered balloons in the picture. Canvas is 640x400 unless stated."""
import math
import il_gear as GE
from il_base import n, text, line, circ, poly, path, arrow, shadow, rect, ell
from il_detail import bal

W, H = 640, 400
MT = {}


def mt(slug, az=-32, el=24, vb="0 0 640 400", margin=(76, 30, 76, 30)):
    def deco(fn):
        MT[slug] = (lambda: build(fn, az, el, margin), vb)
        return fn
    return deco


class Scene:
    """Collects primitives with world bounding boxes, orders them back-to-front with pairwise
    separating-axis tests (works well for axis-aligned machine parts), and fits the drawing
    into the canvas."""

    def __init__(s, ox=0, oy=0, az=-32, el=24, sc=1.0):
        s.cam = GE.Cam(ox, oy, az, el, sc)
        s.items, s.notes, s.top = [], [], []

    def P(s, p):
        return s.cam.xy(p)

    def d(s, p):
        return s.cam.P(p)[2]

    def add(s, svg, bb, bias=0.0, z=0):
        s.items.append({"svg": svg, "bb": bb, "bias": bias, "k": len(s.items), "z": z})

    # ---------------------------------------------------------- primitives
    def box(s, x, y, z, sx, sy, sz, mat="pt", bias=0.0, ch=0, **kw):
        if ch:
            c = ch
            xy = [(x + c, y), (x + sx - c, y), (x + sx, y + c), (x + sx, y + sy - c), (x + sx - c, y + sy), (x + c, y + sy), (x, y + sy - c), (x, y + c)]
            return s.zpr(z, sz, xy, mat, bias, **kw)
        loop = [(-sy / 2, -sx / 2, 0), (sy / 2, -sx / 2, 1), (sy / 2, sx / 2, 2), (-sy / 2, sx / 2, 3)]
        s.add(GE.prism(s.cam, (x + sx / 2, y + sy / 2, z), (0, 0, 1), loop, sz, mat, **kw), ((x, y, z), (x + sx, y + sy, z + sz)), bias)

    def xpr(s, x0, L, yz, mat="pt", bias=0.0, **kw):
        loop = [(u, v, i) for i, (u, v) in enumerate(yz)]
        ys, zs = [p[0] for p in yz], [p[1] for p in yz]
        s.add(GE.prism(s.cam, (x0, 0, 0), (1, 0, 0), loop, L, mat, **kw), ((min(x0, x0 + L), min(ys), min(zs)), (max(x0, x0 + L), max(ys), max(zs))), bias)

    def ypr(s, y0, L, xz, mat="pt", bias=0.0, **kw):
        """(x,z) outline extruded from y0 toward the viewer (−y) by L."""
        loop = [(u, v, i) for i, (u, v) in enumerate(xz)]
        xs, zs = [p[0] for p in xz], [p[1] for p in xz]
        s.add(GE.prism(s.cam, (0, y0, 0), (0, -1, 0), loop, L, mat, **kw), ((min(xs), y0 - L, min(zs)), (max(xs), y0, max(zs))), bias)

    def zpr(s, z0, L, xy, mat="pt", bias=0.0, **kw):
        loop = [(-y, x, i) for i, (x, y) in enumerate(xy)]
        xs, ys = [p[0] for p in xy], [p[1] for p in xy]
        s.add(GE.prism(s.cam, (0, 0, z0), (0, 0, 1), loop, L, mat, **kw), ((min(xs), min(ys), z0), (max(xs), max(ys), z0 + L)), bias)

    def _cbb(s, O, a, r, h):
        p1 = tuple(O[i] + a[i] * h for i in range(3))
        lo = [min(O[i], p1[i]) - (r if abs(a[i]) < .99 else 0) for i in range(3)]
        hi = [max(O[i], p1[i]) + (r if abs(a[i]) < .99 else 0) for i in range(3)]
        return (tuple(lo), tuple(hi))

    def cyl(s, O, A, r, h, mat="w", bias=0.0, **kw):
        a = GE._norm(A)
        s.add(GE.cyl(s.cam, O, a, r, h, mat, **kw), s._cbb(O, a, r, h), bias)

    def ring(s, O, A, r_out, r_in, h, mat="w", bias=0.0):
        a = GE._norm(A)
        s.add(GE.prism(s.cam, O, a, GE.circle_outline(r_out, 56, 14), h, mat, holes=[GE.circle_outline(r_in, 40, 40)], smooth="outer"), s._cbb(O, a, r_out, h), bias)

    def ring_gear(s, O, A, z, rp, r_out, h, mat="w", helix=0.0, bias=0.0):
        a = GE._norm(A)
        s.add(GE.ring_gear3(s.cam, O, a, z, rp, r_out, h, mat, helix=helix), s._cbb(O, a, r_out, h), bias)

    def gear(s, O, A, z, rp, h, mat="w", helix=0.0, bias=0.0, bore=0.0, **kw):
        a = GE._norm(A)
        s.add(GE.gear3(s.cam, O, a, z, rp, h, mat, helix=helix, bore=bore, **kw), s._cbb(O, a, rp * 1.1, h), bias)

    def poly_prism(s, O, A, outline, h, mat, r, bias=0.0, **kw):
        a = GE._norm(A)
        s.add(GE.prism(s.cam, O, a, outline, h, mat, **kw), s._cbb(O, a, r, h), bias)

    def raw(s, svg_fn, bb, bias=0.0):
        """svg_fn(scene) -> svg string, called at render time with the final camera."""
        s.add(svg_fn, bb, bias)

    # ---------------------------------------------------------- helpers
    def rails(s, x0, x1, y, z, w=10, h=8, mat="w", bias=0.0):
        s.box(x0, y - w / 2, z, x1 - x0, w, h, mat, bias)

    def screw(s, x0, x1, y, z, r=6, bias=0.0, pitch=9, A="x"):
        if A == "x":
            s.cyl((x0, y, z), (1, 0, 0), r, x1 - x0, "w", bias)
            def thr(sc):
                ln = ""
                for k in range(int((x1 - x0) / pitch)):
                    a = sc.P((x0 + k * pitch, y - r * .2, z + r))
                    b = sc.P((x0 + k * pitch + pitch * .55, y - r, z - r * .2))
                    ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
                return '<path class="thread" d="%s"/>' % ln
            s.raw(thr, ((x0, y - r, z - r), (x1, y - r + 1, z + r)), bias - 0.01)

    def motor(s, O, A=(1, 0, 0), r=18, L=44, bias=0.0):
        a = GE._norm(A)
        s.cyl(O, a, r, L, "dk", bias)
        s.cyl(tuple(O[i] + a[i] * L for i in range(3)), a, r * .62, 10, "dk", bias)

    def cover(s, x0, x1, y, z, w, h, segs=5, bias=0.0):
        """telescopic way cover along x: stepped steel shells."""
        L = (x1 - x0) / segs
        for k in range(segs):
            g = k * 1.2
            s.box(x0 + k * L, y - w / 2 - g, z, L + 2, w + 2 * g, h + g, "w", bias)

    # ---------------------------------------------------------- annotation
    def axis(s, p0, p1, label, both=True, off=(0, -10)):
        def f(sc):
            a, b = sc.P(p0), sc.P(p1)
            return arrow(a[0], a[1], b[0], b[1], None, both=both) + text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], label, "middle", "al")
        s.top.append(f)

    def rot(s, c, A, r, label, a0=20, a1=300, loff=(0, -8)):
        def f(sc):
            E1, E2, a = GE.frame(A)
            pts = [sc.P(tuple(c[i] + r * (math.cos(math.radians(a0 + (a1 - a0) * k / 24)) * E1[i] + math.sin(math.radians(a0 + (a1 - a0) * k / 24)) * E2[i]) for i in range(3))) for k in range(25)]
            from il_base import head
            d = "M" + " L".join("%s %s" % (n(x), n(y)) for x, y in pts)
            ang = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
            lp = pts[len(pts) // 3]
            return '<path class="a" fill="none" d="%s"/>' % d + head(pts[-1][0], pts[-1][1], ang) + (text(lp[0] + loff[0], lp[1] + loff[1], label, "middle", "al") if label else "")
        s.top.append(f)

    def note(s, p, label, desc=""):
        s.notes.append((p, label, desc))

    # ---------------------------------------------------------- ordering + render
    def _corners(s, bb):
        (x0, y0, z0), (x1, y1, z1) = bb
        return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]

    def extent(s):
        pts = [s.P(c) for it in s.items for c in s._corners(it["bb"])]
        return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)

    def order(s):
        D = s.cam.D
        its = s.items
        n_ = len(its)
        scr = []
        for it in its:
            ps = [s.P(c) for c in s._corners(it["bb"])]
            scr.append((min(p[0] for p in ps), min(p[1] for p in ps), max(p[0] for p in ps), max(p[1] for p in ps)))
            (x0, y0, z0), (x1, y1, z1) = it["bb"]
            it["dep"] = s.d(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)) + it["bias"]
        after = [set() for _ in range(n_)]   # after[j] = items that must be drawn before j
        eps = 0.01
        for i in range(n_):
            for j in range(i + 1, n_):
                a, b = scr[i], scr[j]
                if a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]:
                    continue
                A, B = its[i]["bb"], its[j]["bb"]
                verdict = None
                for k in range(3):
                    if A[1][k] <= B[0][k] + eps:          # A below B on axis k
                        verdict = "A" if D[k] < 0 else "B"   # which one is farther
                    elif B[1][k] <= A[0][k] + eps:
                        verdict = "B" if D[k] < 0 else "A"
                    if verdict:
                        break
                if its[i]["bias"] != its[j]["bias"] and verdict is None:
                    verdict = "A" if its[i]["dep"] > its[j]["dep"] else "B"
                if verdict is None:
                    verdict = "A" if its[i]["dep"] >= its[j]["dep"] else "B"
                if verdict == "A":
                    after[j].add(i)
                else:
                    after[i].add(j)
        done, out = set(), []
        while len(out) < n_:
            ready = [i for i in range(n_) if i not in done and after[i] <= done]
            if not ready:   # cycle: break it with the farthest remaining
                ready = [max((i for i in range(n_) if i not in done), key=lambda i: its[i]["dep"])]
            i = max(ready, key=lambda i: (its[i]["dep"], -its[i]["k"]))
            done.add(i)
            out.append(its[i])
        return out

    def render(s, shadow_=True):
        out = ""
        if shadow_:
            x0, y0, x1, y1 = s.extent()
            out += shadow((x0 + x1) / 2, y1 - 6, (x1 - x0) * .5, 16)
        for it in s.order():
            v = it["svg"]
            out += v(s) if callable(v) else v
        out += "".join(f(s) for f in s.top)
        pts = [s.P(p) for p, _, _ in s.notes]
        left = sorted([i for i, p in enumerate(pts) if p[0] < W * .5], key=lambda i: pts[i][1])
        right = sorted([i for i, p in enumerate(pts) if p[0] >= W * .5], key=lambda i: pts[i][1])
        place = {}
        for col, x in ((left, 24), (right, W - 24)):
            ys = [max(24, min(H - 24, pts[i][1])) for i in col]
            for k in range(1, len(ys)):
                ys[k] = max(ys[k], ys[k - 1] + 30)
            if ys and ys[-1] > H - 24:
                ys[-1] = H - 24
                for k in range(len(ys) - 2, -1, -1):
                    ys[k] = min(ys[k], ys[k + 1] - 30)
            for i, y in zip(col, ys):
                place[i] = (x, y)
        order = sorted(range(len(pts)), key=lambda i: (pts[i][0] >= W * .5, place[i][1]))
        num = {i: k + 1 for k, i in enumerate(order)}
        for i in range(len(pts)):
            out += bal(pts[i][0], pts[i][1], place[i][0], place[i][1], num[i])
        notes = [(s.notes[i][1], s.notes[i][2]) for i in order]
        return out, notes


def build(fn, az, el, margin=(76, 30, 76, 30)):
    """two passes: probe the extents with a unit camera, then fit into the canvas."""
    probe = Scene(0, 0, az, el, 1.0)
    fn(probe)
    x0, y0, x1, y1 = probe.extent()
    l, t, r, b = margin
    k = min((W - l - r) / (x1 - x0), (H - t - b) / (y1 - y0))
    ox = l + ((W - l - r) - (x1 - x0) * k) / 2 - x0 * k
    oy = t + ((H - t - b) - (y1 - y0) * k) / 2 - y0 * k
    sc = Scene(ox, oy, az, el, k)
    fn(sc)
    return sc.render()


def jaws3(sc, x, y, z, r0, r1, w, depth, mat="w", phase=90):
    """three chuck jaws on a face at x, extruded along +x."""
    for k in range(3):
        t = math.radians(phase + k * 120)
        c, s_ = math.cos(t), math.sin(t)
        pts = [(r0, -w / 2), (r1, -w / 2), (r1, w / 2), (r0, w / 2)]
        yz = [(y + u * c - v * s_, z + u * s_ + v * c) for u, v in pts]
        sc.xpr(x, depth, yz, mat, bias=-2)


def turret_disc(sc, x0, L, cy, cz, R, nside=12, tool_at=None, mat="w"):
    yz = [(cy + R * math.cos(2 * math.pi * k / nside + math.pi / nside), cz + R * math.sin(2 * math.pi * k / nside + math.pi / nside)) for k in range(nside)]
    sc.xpr(x0, L, yz, mat)




def slope_slab(sc, x0, L, p0, p1, th, mat="pt", bias=0.0, inset=0.0):
    """a plate lying on the slant line p0→p1 (in y,z), thickness th along its normal, extruded along x."""
    (y0, z0), (y1, z1) = p0, p1
    dy, dz = y1 - y0, z1 - z0
    m = math.hypot(dy, dz)
    ny, nz = -dz / m, dy / m
    if nz < 0:
        ny, nz = -ny, -nz
    a = (y0 + dy * inset, z0 + dz * inset)
    b = (y1 - dy * inset, z1 - dz * inset)
    sc.xpr(x0, L, [a, b, (b[0] + ny * th, b[1] + nz * th), (a[0] + ny * th, a[1] + nz * th)], mat, bias)


def on_slope(p0, p1, t, h=0.0):
    (y0, z0), (y1, z1) = p0, p1
    dy, dz = y1 - y0, z1 - z0
    m = math.hypot(dy, dz)
    ny, nz = -dz / m, dy / m
    if nz < 0:
        ny, nz = -ny, -nz
    return (y0 + dy * t + ny * h, z0 + dz * t + nz * h)


# =====================================================================================
# machines
# =====================================================================================
@mt("cnc-lathe", az=-24, el=21)
def _(sc):
    S0, S1 = (-96, 150), (80, 256)                       # slant face of the bed (y,z)
    yc, zc = -44, 212                                    # spindle centre line
    sc.box(-310, -130, 0, 620, 260, 64, "pt", ch=10, bias=900)     # base
    sc.box(-300, -112, 64, 600, 224, 86, "pt", bias=800)            # bed lower block
    sc.xpr(-120, 420, [(-96, 150), (112, 150), (112, 266), (80, 266), S1, S0], "pt", bias=700)   # slant wedge
    for t in (0.2, 0.8):
        a, b = on_slope(S0, S1, t - .05), on_slope(S0, S1, t + .05)
        slope_slab(sc, -116, 412, a, b, 8, "w", bias=600)
    ya, za = on_slope(S0, S1, .5, 9)
    sc.screw(-110, 292, ya, za, 6, bias=590)
    sc.motor((296, ya, za), (1, 0, 0), 20, 40)
    # headstock + spindle + chuck + work
    sc.box(-300, -118, 150, 112, 200, 190, "pt", ch=8, bias=500)
    sc.motor((-300, 30, 300), (-1, 0, 0), 22, 26)
    sc.cyl((-188, yc, zc), (1, 0, 0), 52, 12, "pt", bias=-10)
    sc.cyl((-176, yc, zc), (1, 0, 0), 74, 44, "w", bias=-20)
    def bolts(s_):
        o = ""
        for k in range(6):
            t = math.radians(30 + k * 60)
            p = s_.P((-132, yc + 50 * math.cos(t), zc + 50 * math.sin(t)))
            o += '<circle class="bolt" cx="%s" cy="%s" r="2.6"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(bolts, ((-132, yc - 50, zc - 50), (-131, yc + 50, zc + 50)), bias=-25)
    jaws3(sc, -132, yc, zc, 22, 66, 18, 22)
    sc.cyl((-132, yc, zc), (1, 0, 0), 36, 118, "w", bias=-40)
    sc.cyl((-14, yc, zc), (1, 0, 0), 26, 62, "w", bias=-40)
    # tailstock (right end, on the flat part of the bed front)
    sc.box(180, -116, 150, 90, 100, 112, "pt", ch=6, bias=-30)
    sc.cyl((180, yc, zc), (-1, 0, 0), 15, 52, "w", bias=-35)
    # carriage on the slant, turret behind/above the centre line
    slope_slab(sc, -50, 160, on_slope(S0, S1, .2, 8), on_slope(S0, S1, .98, 8), 24, "pt", bias=100)
    sc.box(-36, 18, 262, 150, 92, 72, "pt", ch=6, bias=90)
    ty, tz, R = 40, 292, 60
    turret_disc(sc, -84, 48, ty, tz, R, 12, mat="w")
    sc.items[-1]["bias"] = 50
    for k in range(12):
        t = 2 * math.pi * k / 12 + math.pi / 12
        if math.cos(t) < 0.3 and math.sin(t) < 0.5:
            cy, cz = ty + (R + 7) * math.cos(t), tz + (R + 7) * math.sin(t)
            sc.box(-80, cy - 7, cz - 7, 40, 14, 14, "w", bias=40)
    sc.box(-72, -14, 230, 18, 34, 12, "t", bias=-60)
    sc.motor((114, 62, 300), (1, 0, 0), 18, 34)
    sc.axis((-80, -120, 352), (80, -120, 352), "Z")
    sc.axis((150, 96, 330), (150, 0, 262), "X", off=(14, 0))
    sc.rot((-150, yc, zc), (1, 0, 0), 98, "", 210, 330)
    sc.note((-250, -60, 340), "主軸", "工作物をつかんで回す。主軸台に軸受とモータが入る")
    sc.note((-150, yc - 30, zc - 56), "チャック", "爪で工作物を保持する")
    sc.note((-60, ty - 20, tz + R), "タレット", "工具を円周に並べ、割り出して使い分ける")
    sc.note((-63, -14, 236), "工具", "バイトで外径・端面・溝・ねじを削る")
    sc.note((230, *on_slope(S0, S1, .82, 8)), "リニアガイド", "刃物台を案内するレール")
    sc.note((250, ya - 6, za), "ボールねじ", "モータの回転を直線の送りに変える")
    sc.note((336, ya, za + 18), "サーボモータ", "NCの指令どおりに送り軸を動かす")
    sc.note((236, -116, 236), "心押台", "長い工作物の先端をセンタで支える")
    sc.note((40, -112, 110), "ベッド", "機械の土台。傾斜させて切りくずを落とす")


@mt("vertical-machining-center", az=-34, el=22)
def _(sc):
    sc.box(-230, -190, 0, 460, 410, 92, "pt", ch=12, bias=900)          # base
    sc.box(-150, -160, 92, 300, 230, 40, "pt", ch=6, bias=500)          # saddle (Y)
    for x in (-110, 110):
        sc.box(x - 8, -150, 132, 16, 200, 6, "w", bias=400)
    sc.box(-215, -140, 138, 430, 180, 34, "pt", ch=4, bias=300)         # table (X)
    def tslots(s_):
        ln = ""
        for k in range(5):
            y = -124 + k * 37
            a, b = s_.P((-205, y, 172)), s_.P((205, y, 172))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return '<path class="tslot" d="%s"/>' % ln
    sc.raw(tslots, ((-205, -124, 172), (205, 24, 172.5)), bias=290)
    sc.box(-92, -108, 172, 184, 112, 24, "dk", ch=3)                    # vise
    sc.box(-72, -98, 196, 144, 92, 44, "alu")                            # work
    sc.motor((215, -50, 155), (1, 0, 0), 15, 34)                         # X servo
    sc.box(-125, 100, 92, 250, 150, 440, "pt", ch=10, bias=200)         # column
    for x in (-82, 82):
        sc.box(x - 8, 92, 150, 16, 8, 360, "w", bias=150)               # Z guides
    sc.box(-78, -36, 316, 156, 128, 150, "pt", ch=8)                     # spindle head
    sc.motor((0, 28, 466), (0, 0, 1), 34, 30)
    sc.cyl((0, 0, 316), (0, 0, -1), 34, 24, "w")
    sc.cyl((0, 0, 292), (0, 0, -1), 17, 22, "w")
    sc.cyl((0, 0, 270), (0, 0, -1), 8, 30, "t")
    sc.motor((0, 175, 532), (0, 0, 1), 18, 30)                           # Z servo
    sc.cyl((125, 175, 420), (1, 0, 0), 86, 22, "pt")                     # ATC magazine
    for k in range(12):
        t = 2 * math.pi * k / 12
        sc.cyl((147, 175 + 72 * math.cos(t), 420 + 72 * math.sin(t)), (1, 0, 0), 8, 12, "w")
    sc.box(300, -40, 120, 16, 16, 150, "dk")                             # pendant arm
    sc.box(290, -70, 260, 26, 76, 96, "dk", ch=4)                        # NC panel
    sc.axis((-230, -180, 230), (-110, -180, 230), "X")
    sc.axis((-250, -170, 110), (-250, -60, 110), "Y", off=(-12, 0))
    sc.axis((100, -40, 350), (100, -40, 450), "Z", off=(14, 0))
    sc.note((0, -36, 420), "主軸", "工具を回転させる。ビルトインモータ主軸が多い")
    sc.note((0, 0, 280), "工具", "ツールホルダで主軸テーパに取り付ける")
    sc.note((140, 175, 500), "ATC", "工具マガジンと交換アームで工具を自動交換")
    sc.note((-200, -140, 172), "テーブル", "工作物を載せてX方向に動く")
    sc.note((-150, -160, 110), "サドル", "テーブルを載せてY方向に動く")
    sc.note((-125, 100, 470), "コラム", "主軸頭を支え、Z方向に案内する")
    sc.note((82, 92, 250), "リニアガイド", "各軸を案内するレール")
    sc.note((303, -70, 320), "NC装置", "加工プログラムで全軸を制御する")
    sc.note((-200, -190, 40), "ベッド", "機械全体の土台")


@mt("cylindrical-grinder", az=-26, el=20)
def _(sc):
    yc, zc = -70, 206
    sc.box(-310, -160, 0, 620, 350, 108, "pt", ch=12, bias=900)         # bed
    sc.box(-270, -140, 108, 540, 130, 28, "pt", ch=4, bias=500)         # table
    sc.box(-262, -132, 136, 524, 114, 16, "pt", bias=400)               # swivel table
    sc.box(-262, -126, 152, 96, 104, 96, "pt", ch=6)                    # work head
    sc.motor((-214, -74, 248), (0, 0, 1), 18, 22)
    sc.cyl((-166, yc, zc), (1, 0, 0), 26, 8, "w")
    sc.cyl((-158, yc, zc), (1, 0, 0), 20, 316, "w", bias=-30)           # work
    sc.cyl((-74, yc, zc), (1, 0, 0), 30, 90, "w", bias=-40)
    sc.box(158, -118, 152, 84, 96, 76, "pt", ch=6)                      # tailstock
    R = 104
    wy = yc + 30 + R
    # wheel head sits to the right of the wheel, both on the cross slide behind the table
    sc.box(-120, 34, 108, 330, 150, 26, "pt", ch=4, bias=600)           # cross slide
    sc.box(-10, 46, 134, 200, 130, 130, "pt", ch=8, bias=-5)            # wheel head
    sc.cyl((-14, wy, zc), (1, 0, 0), 22, 8, "w")
    sc.cyl((-62, wy, zc), (1, 0, 0), R, 46, "gw")
    guard = []
    for k in range(25):
        a = math.radians(-40 + 215 * k / 24)
        guard.append((wy + (R + 12) * math.cos(a), zc + (R + 12) * math.sin(a)))
    for k in range(24, -1, -1):
        a = math.radians(-40 + 215 * k / 24)
        guard.append((wy + (R + 2) * math.cos(a), zc + (R + 2) * math.sin(a)))
    sc.xpr(-68, 58, guard, "pt", bias=-2)
    sc.motor((190, 110, 200), (1, 0, 0), 26, 40)
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


@mt("vertical-turning-lathe", az=-30, el=24)
def _(sc):
    sc.box(-280, -260, 0, 560, 500, 90, "pt", ch=14, bias=900)          # base
    tc = (-20, -70)
    sc.cyl((tc[0], tc[1], 90), (0, 0, 1), 190, 34, "w", bias=500)       # chuck table
    for k in range(4):
        t = math.radians(45 + 90 * k)
        cx, cy = tc[0] + 160 * math.cos(t), tc[1] + 160 * math.sin(t)
        sc.box(cx - 14, cy - 14, 124, 28, 28, 26, "w")
    sc.ring((tc[0], tc[1], 124), (0, 0, 1), 132, 82, 74, "w")           # work (ring/flange)
    sc.box(-140, 160, 90, 240, 110, 520, "pt", ch=10, bias=300)         # column
    sc.box(-280, 96, 400, 500, 64, 76, "pt", ch=6, bias=200)            # cross rail
    for z in (412, 460):
        sc.box(-270, 92, z - 4, 480, 4, 8, "w", bias=190)
    sc.box(-70, -40, 380, 100, 136, 110, "pt", ch=6)                    # saddle
    sc.box(-48, -48, 200, 56, 56, 290, "pt", ch=4)                      # ram
    sc.box(-36, -60, 168, 32, 40, 34, "w")
    sc.box(-28, -64, 150, 16, 30, 20, "t")                              # tool
    sc.motor((-20, 0, 490), (0, 0, 1), 20, 34)
    sc.motor((220, 128, 438), (1, 0, 0), 18, 34)
    sc.box(-230, 60, 90, 120, 90, 120, "dk", ch=6)                      # table drive housing
    sc.rot((tc[0], tc[1], 128), (0, 0, 1), 220, "", 200, 320)
    sc.axis((-250, 80, 500), (-110, 80, 500), "X")
    sc.axis((60, -60, 230), (60, -60, 360), "Z", off=(14, 0))
    sc.note((tc[0] - 120, tc[1] - 120, 110), "テーブル（チャック）", "工作物を載せて回す")
    sc.note((tc[0] + 60, tc[1] - 100, 190), "工作物", "大径で重い円盤・リング状の部品")
    sc.note((-20, -48, 300), "ラム", "刃物台を上下（Z）に動かす")
    sc.note((-20, -64, 150), "工具", "バイトで端面・内外径を削る")
    sc.note((-200, 96, 470), "クロスレール", "刃物台を左右（X）に案内する横けた")
    sc.note((-20, 160, 560), "コラム", "クロスレールを支える柱")
    sc.note((200, -260, 40), "ベッド", "テーブルとコラムを支える土台")


@mt("turn-mill", az=-26, el=22)
def _(sc):
    yc, zc = -40, 210
    sc.box(-320, -130, 0, 640, 260, 64, "pt", ch=10, bias=900)
    sc.box(-310, -112, 64, 620, 224, 86, "pt", bias=800)
    sc.box(-300, -118, 150, 104, 200, 180, "pt", ch=8, bias=500)        # main headstock
    sc.cyl((-196, yc, zc), (1, 0, 0), 64, 40, "w", bias=-20)
    jaws3(sc, -156, yc, zc, 20, 58, 16, 20)
    sc.cyl((-156, yc, zc), (1, 0, 0), 34, 170, "w", bias=-40)
    sc.box(200, -118, 150, 100, 170, 160, "pt", ch=8, bias=-30)         # sub spindle
    sc.cyl((200, yc, zc), (-1, 0, 0), 50, 34, "w", bias=-35)
    jaws3(sc, 166, yc, zc, 16, 44, 13, 16)
    sc.items[-1]["bias"] = sc.items[-2]["bias"] = sc.items[-3]["bias"] = -38
    # milling head on a column that rides at the back (X/Y/Z) with a B-axis swivel
    sc.box(-150, 60, 150, 300, 60, 40, "pt", bias=400)
    sc.box(-70, 70, 190, 150, 90, 230, "pt", ch=8, bias=300)            # column
    sc.box(-50, -10, 330, 110, 90, 90, "pt", ch=8, bias=100)            # ram / B-axis body
    sc.cyl((5, -12, 375), (0, -1, 0), 40, 10, "dk")                     # B-axis ring
    a = (math.sin(math.radians(35)), 0, -math.cos(math.radians(35)))
    o = (5 + a[0] * 30, -40, 330 + a[2] * 30)
    sc.cyl((5, -40, 340), a, 26, 60, "w", bias=-50)                     # milling spindle
    tip = (5 + a[0] * 60, -40, 340 + a[2] * 60)
    sc.cyl(tip, a, 12, 22, "w", bias=-55)
    tip2 = (tip[0] + a[0] * 22, -40, tip[2] + a[2] * 22)
    sc.cyl(tip2, a, 6, 26, "t", bias=-60)
    sc.motor((5, 120, 420), (0, 0, 1), 22, 30)
    sc.rot((5, -40, 375), (0, 1, 0), 70, "B", 200, 330)
    sc.axis((-120, -130, 440), (60, -130, 440), "Z")
    sc.note((-250, -60, 330), "主軸（第1主軸）", "工作物を回して旋削する")
    sc.note((250, -118, 300), "第2主軸", "工作物を持ち替えて裏側も加工する")
    sc.note((5, -50, 300), "ミーリング主軸", "回転工具で穴あけ・フライス加工をする")
    sc.note((40, -12, 412), "B軸", "主軸頭を傾けて斜めの穴や面を加工する")
    sc.note((-40, yc - 30, zc), "工作物", "1台で旋削とミーリングを済ませる")
    sc.note((-120, -112, 110), "ベッド", "主軸台とコラムを支える土台")


@mt("swiss-type-lathe", az=-24, el=22)
def _(sc):
    yc, zc = -30, 210
    sc.box(-340, -120, 0, 680, 240, 70, "pt", ch=10, bias=900)
    sc.box(-330, -100, 70, 660, 200, 80, "pt", bias=800)
    for y in (-60, 20):
        sc.box(-320, y - 6, 150, 260, 12, 8, "w", bias=700)
    sc.box(-300, -90, 158, 150, 170, 110, "pt", ch=8, bias=300)          # sliding headstock
    sc.cyl((-560, yc, zc), (1, 0, 0), 9, 260, "w", bias=850)             # bar stock from feeder
    sc.cyl((-150, yc, zc), (1, 0, 0), 26, 16, "w")
    sc.box(-40, -100, 150, 60, 190, 150, "pt", ch=6, bias=200)           # guide bushing support
    sc.cyl((-46, yc, zc), (1, 0, 0), 9, 70, "w", bias=-50)               # bar through bushing
    sc.cyl((20, yc, zc), (1, 0, 0), 16, 10, "dk", bias=-20)              # bushing nose
    sc.box(30, -150, 150, 70, 90, 30, "pt", bias=150)                    # gang tool slide
    for k in range(5):
        sc.box(40 + k * 12, -130, 180, 8, 50, 16, "w", bias=-30)
    sc.box(64, -84, 196, 8, 46, 10, "t", bias=-70)
    sc.box(200, -100, 150, 110, 180, 120, "pt", ch=8, bias=-10)          # back spindle
    sc.cyl((200, yc, zc), (-1, 0, 0), 22, 26, "w", bias=-15)
    sc.axis((-300, -110, 300), (-170, -110, 300), "Z")
    sc.axis((80, -170, 260), (80, -110, 200), "X", off=(14, 0))
    sc.note((-230, -90, 268), "主軸台（Z移動）", "棒材をつかんだまま前後に動き、Z送りをする")
    sc.note((-10, -100, 280), "ガイドブッシュ", "刃物のすぐ近くで棒材を支え、たわみを防ぐ")
    sc.note((70, -140, 210), "くし刃刃物台", "工具を一列に並べ、X・Y方向に動かす")
    sc.note((250, -100, 260), "背面主軸", "切り離した部品を受け取り裏側を加工する")
    sc.note((-380, yc, zc), "棒材", "バーフィーダから送られる長い材料")
    sc.note((-200, -100, 110), "ベッド", "機械の土台")


@mt("horizontal-machining-center", az=-36, el=24)
def _(sc):
    sc.box(-300, -330, 0, 600, 640, 80, "pt", ch=14, bias=900)          # bed (T shape simplified)
    sc.box(-260, 60, 80, 520, 230, 40, "pt", bias=700)                  # column bed (X)
    for x in (-200, 200):
        sc.box(x - 8, 70, 120, 16, 210, 6, "w", bias=650)
    sc.box(-150, 120, 120, 300, 150, 470, "pt", ch=12, bias=400)        # column
    for x in (-90, 90):
        sc.box(x - 8, 112, 160, 16, 8, 400, "w", bias=350)
    sc.box(-90, 30, 280, 180, 90, 150, "pt", ch=8, bias=200)            # spindle head (Y)
    sc.cyl((0, 30, 355), (0, -1, 0), 40, 26, "w", bias=100)
    sc.cyl((0, 4, 355), (0, -1, 0), 18, 22, "w", bias=90)
    sc.cyl((0, -18, 355), (0, -1, 0), 8, 34, "t", bias=80)
    sc.box(-120, -240, 80, 240, 210, 50, "pt", ch=6, bias=500)          # table saddle (Z)
    sc.cyl((0, -135, 130), (0, 0, 1), 100, 26, "w", bias=400)           # rotary table (B)
    sc.box(-90, -225, 156, 180, 180, 22, "w", ch=4, bias=300)           # pallet
    sc.box(-70, -165, 178, 140, 60, 230, "alu", bias=50)                # tombstone fixture
    for z in (220, 320):
        sc.box(-56, -110, z, 112, 18, 60, "w", bias=40)                 # workpieces on the back face
    # pallet changer in front
    sc.box(-110, -330, 80, 220, 90, 70, "dk", ch=6, bias=150)
    sc.box(-90, -320, 150, 180, 70, 18, "w", ch=4, bias=140)
    sc.box(170, 160, 80, 120, 140, 420, "dk", ch=8, bias=100)           # chain magazine
    sc.motor((0, 160, 590), (0, 0, 1), 20, 30)
    sc.rot((0, -135, 160), (0, 0, 1), 130, "B", 200, 330)
    sc.axis((-250, 40, 480), (-110, 40, 480), "X")
    sc.axis((130, 40, 300), (130, 40, 420), "Y", off=(14, 0))
    sc.axis((200, -240, 120), (200, -100, 120), "Z", off=(14, 0))
    sc.note((0, 0, 400), "主軸（水平）", "工具を水平に向けて回す。切りくずが下に落ちる")
    sc.note((-150, 120, 560), "コラム", "主軸頭を上下（Y）に案内する")
    sc.note((-90, -135, 140), "回転テーブル（B軸）", "割り出して4面を順に加工する")
    sc.note((-70, -165, 360), "イケール（治具）", "複数の工作物を立てて固定する")
    sc.note((-90, -320, 168), "パレットチェンジャ", "加工中に次のパレットを段取りする")
    sc.note((230, 160, 470), "工具マガジン", "チェーン式で多数の工具を収納する")
    sc.note((260, -330, 40), "ベッド", "コラムとテーブルを支える土台")


@mt("5-axis-machining-center", az=-32, el=24)
def _(sc):
    sc.box(-260, -230, 0, 520, 470, 90, "pt", ch=14, bias=900)
    sc.box(-230, -200, 90, 60, 220, 190, "pt", ch=6, bias=300)          # trunnion supports
    sc.box(170, -200, 90, 60, 220, 190, "pt", ch=6, bias=-10)
    cy, cz = -90, 230
    sc.xpr(-170, 340, [(cy - 90, cz - 70), (cy + 90, cz - 70), (cy + 90, cz - 20), (cy - 90, cz - 20)], "pt", bias=200)   # cradle (A)
    sc.cyl((-230, cy, cz), (1, 0, 0), 40, 60, "dk", bias=310)
    sc.cyl((0, cy, cz - 20), (0, 0, 1), 90, 24, "w", bias=150)          # rotary table (C)
    # workpiece: impeller-like hub with blades
    sc.cyl((0, cy, cz + 4), (0, 0, 1), 46, 56, "alu", bias=50)
    sc.cyl((0, cy, cz + 60), (0, 0, 1), 20, 26, "alu", bias=40)
    sc.box(-120, 120, 90, 240, 120, 460, "pt", ch=10, bias=400)         # column
    sc.box(-70, 20, 330, 140, 110, 150, "pt", ch=8, bias=100)           # spindle head
    sc.motor((0, 80, 480), (0, 0, 1), 28, 28)
    sc.cyl((0, 64, 330), (0, 0, -1), 28, 20, "w", bias=20)
    sc.cyl((0, 64, 310), (0, 0, -1), 13, 18, "w", bias=10)
    sc.cyl((0, 64, 292), (0, 0, -1), 6, 28, "t", bias=0)
    sc.rot((-260, cy, cz), (1, 0, 0), 110, "A", 200, 320)
    sc.rot((0, cy, cz + 4), (0, 0, 1), 112, "C", 200, 330)
    sc.axis((90, 20, 350), (90, 20, 450), "Z", off=(14, 0))
    sc.note((0, 30, 420), "主軸", "工具を回す。X・Y・Zの3軸で動く")
    sc.note((-200, cy, cz - 40), "傾斜テーブル（A軸）", "工作物を前後に傾ける")
    sc.note((80, cy, cz - 10), "回転テーブル（C軸）", "工作物を水平に回す")
    sc.note((40, cy - 30, cz + 40), "工作物", "インペラなど曲面の多い部品")
    sc.note((-120, 120, 520), "コラム", "主軸頭を支える柱")
    sc.note((200, -230, 40), "ベッド", "機械の土台")


def threads(sc, O, A, r, L, pitch=8, bias=0.0, cls="thread"):
    """helical thread lines drawn on the visible side of a cylinder."""
    a = GE._norm(A)
    E1, E2, _ = GE.frame(a)
    def f(s_):
        ln = ""
        for k in range(int(L / pitch)):
            pts = []
            for q in range(7):
                t = math.radians(-60 + 120 * q / 6)
                along = k * pitch + pitch * q / 6
                pts.append(s_.P(tuple(O[i] + a[i] * along + r * (math.cos(t) * (-s_.cam.D[0] if False else 0) * 0 + math.cos(t) * E1[i] + math.sin(t) * E2[i]) for i in range(3))))
            ln += "M" + " L".join("%s %s" % (n(x), n(y)) for x, y in pts)
        return '<path class="%s" d="%s"/>' % (cls, ln)
    sc.raw(f, sc._cbb(O, a, r, L), bias)


@mt("double-column-machining-center", az=-34, el=24)
def _(sc):
    sc.box(-360, -130, 0, 720, 260, 70, "pt", ch=12, bias=900)          # bed
    sc.box(-340, -110, 70, 680, 220, 40, "pt", ch=4, bias=800)          # table (X)
    def tslots(s_):
        ln = ""
        for k in range(5):
            y = -88 + k * 44
            a, b = s_.P((-330, y, 110), ), s_.P((330, y, 110))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return '<path class="tslot" d="%s"/>' % ln
    sc.raw(tslots, ((-330, -88, 110), (330, 88, 110.5)), bias=790)
    sc.box(-230, -90, 110, 300, 180, 90, "w", ch=8, bias=500)           # workpiece (press die)
    sc.box(-40, 160, 0, 90, 80, 470, "pt", ch=8, bias=600)              # back column
    sc.box(-40, -240, 0, 90, 80, 470, "pt", ch=8, bias=-200)            # front column
    sc.box(50, -250, 380, 70, 500, 80, "pt", ch=6, bias=100)            # cross rail (Y)
    for z in (392, 444):
        sc.box(120, -240, z - 4, 4, 480, 8, "w", bias=90)
    sc.box(124, -60, 340, 70, 120, 150, "pt", ch=6, bias=-10)           # saddle
    sc.box(130, -30, 190, 56, 60, 300, "pt", ch=4, bias=-20)            # ram (Z)
    sc.cyl((158, 0, 190), (0, 0, -1), 22, 20, "w", bias=-30)
    sc.cyl((158, 0, 170), (0, 0, -1), 10, 30, "t", bias=-40)
    sc.motor((158, 0, 490), (0, 0, 1), 20, 30)
    sc.axis((-330, -130, 160), (-170, -130, 160), "X")
    sc.axis((210, -200, 470), (210, -60, 470), "Y", off=(14, 0))
    sc.axis((220, 40, 240), (220, 40, 340), "Z", off=(14, 0))
    sc.note((-80, -90, 200), "工作物", "プレス金型など大きく重い部品")
    sc.note((-300, -110, 110), "テーブル", "工作物を載せて前後（X）に動く")
    sc.note((5, -240, 300), "コラム（左右2本）", "門の柱。クロスレールを両側で支える")
    sc.note((85, 200, 460), "クロスレール", "サドルを左右（Y）に案内する横けた")
    sc.note((158, -30, 260), "ラム", "主軸を上下（Z）に動かす")
    sc.note((158, 0, 150), "主軸・工具", "ラム先端で工具を回す")
    sc.note((300, -130, 30), "ベッド", "テーブルを支える長い土台")


@mt("internal-grinder", az=-26, el=20)
def _(sc):
    yc, zc = -30, 200
    sc.box(-320, -150, 0, 640, 300, 100, "pt", ch=12, bias=900)
    sc.box(-300, -130, 100, 200, 220, 30, "pt", bias=600)               # work-head slide
    sc.box(-290, -110, 130, 150, 160, 130, "pt", ch=8, bias=300)        # work head
    sc.motor((-290, 20, 230), (-1, 0, 0), 18, 24)
    sc.cyl((-140, yc, zc), (1, 0, 0), 60, 34, "w", bias=-20)           # chuck
    jaws3(sc, -106, yc, zc, 30, 56, 14, 12)
    sc.ring((-106, yc, zc), (1, 0, 0), 62, 34, 46, "w")                 # ring workpiece (gear / race)
    sc.items[-1]["bias"] = -40
    sc.box(-20, -130, 100, 320, 220, 30, "pt", bias=600)                # wheel-head slide (Z/X)
    sc.box(60, -110, 130, 200, 160, 130, "pt", ch=8, bias=-10)          # wheel head
    sc.motor((260, -30, 200), (1, 0, 0), 22, 34)
    sc.cyl((60, yc, zc), (-1, 0, 0), 24, 40, "w", bias=-20)             # spindle nose
    sc.cyl((20, yc, zc), (-1, 0, 0), 9, 100, "w", bias=-30)             # quill
    sc.cyl((-80, yc, zc), (-1, 0, 0), 22, 26, "gw", bias=-35)           # small wheel inside the bore
    sc.axis((-20, -160, 300), (120, -160, 300), "Z")
    sc.axis((200, 130, 280), (200, 30, 280), "X", off=(14, 0))
    sc.note((-200, -110, 270), "主軸台", "工作物をチャックでつかんで回す")
    sc.note((-80, yc - 58, zc + 20), "工作物（穴）", "ギヤの内径や軸受の内輪を仕上げる")
    sc.note((-94, yc, zc - 22), "砥石", "穴より小さい砥石を高速で回す")
    sc.note((40, yc + 9, zc + 9), "砥石軸（クイル）", "細長い軸。たわみが精度を左右する")
    sc.note((160, -110, 260), "砥石台", "砥石を軸方向（Z）と切り込み（X）に送る")
    sc.note((-250, -150, 50), "ベッド", "機械の土台")


@mt("surface-grinder", az=-30, el=24)
def _(sc):
    sc.box(-330, -160, 0, 660, 330, 100, "pt", ch=12, bias=900)
    sc.box(-180, -140, 100, 360, 260, 30, "pt", bias=700)               # saddle (Y)
    sc.box(-320, -120, 130, 640, 200, 30, "pt", ch=4, bias=600)         # table (X)
    sc.box(-260, -110, 160, 520, 180, 24, "dk", bias=500)               # magnetic chuck
    def grid(s_):
        ln = ""
        for k in range(1, 26):
            x = -260 + k * 20
            a, b = s_.P((x, -110, 184), ), s_.P((x, 70, 184))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return '<path class="mgrid" d="%s"/>' % ln
    sc.raw(grid, ((-260, -110, 184), (260, 70, 184.5)), bias=490)
    sc.box(-120, -80, 184, 90, 70, 36, "w")                             # workpieces
    sc.box(10, -80, 184, 90, 70, 36, "w")
    sc.box(-90, 150, 100, 180, 150, 420, "pt", ch=10, bias=400)         # column
    sc.box(-80, 20, 300, 160, 130, 130, "pt", ch=8, bias=100)           # wheel head (Z)
    R = 92
    sc.cyl((0, 20, 300 - 20), (0, -1, 0), R, 34, "gw", bias=-20)        # wheel (axis along y)
    sc.items[-1]["bb"] = ((-R, -14, 188), (R, 20, 372))
    guard = []
    for k in range(25):
        a = math.radians(-10 + 200 * k / 24)
        guard.append(((R + 12) * math.cos(a), 280 + (R + 12) * math.sin(a)))
    for k in range(24, -1, -1):
        a = math.radians(-10 + 200 * k / 24)
        guard.append(((R + 2) * math.cos(a), 280 + (R + 2) * math.sin(a)))
    sc.ypr(24, 42, guard, "pt", bias=-25)
    sc.motor((80, 85, 380), (1, 0, 0), 22, 36)
    sc.axis((-320, -150, 250), (-180, -150, 250), "X")
    sc.axis((-330, -150, 140), (-330, -40, 140), "Y", off=(-12, 0))
    sc.axis((130, 40, 330), (130, 40, 430), "Z", off=(14, 0))
    sc.note((0, -14, 200), "砥石", "外周で平面を削る（横軸形）")
    sc.note((-80, 20, 400), "砥石頭", "砥石を上下（Z）に送って切り込む")
    sc.note((-160, -110, 190), "マグネットチャック", "鋼の工作物を磁力で吸着する")
    sc.note((-75, -80, 220), "工作物", "平面度・平行度を出して仕上げる")
    sc.note((-280, -120, 145), "テーブル", "左右（X）に往復する")
    sc.note((-90, 150, 500), "コラム", "砥石頭を支える")
    sc.note((300, -160, 50), "ベッド", "機械の土台")


@mt("centerless-grinder", az=-22, el=26)
def _(sc):
    zc = 220
    sc.box(-260, -260, 0, 520, 520, 110, "pt", ch=14, bias=900)
    R1, R2 = 130, 80
    y1, y2 = 120, -110
    sc.box(-120, 40, 110, 240, 220, 40, "pt", bias=500)                 # grinding wheel head base
    sc.box(80, 50, 150, 120, 200, 160, "pt", ch=8, bias=300)
    sc.cyl((-80, y1, zc), (1, 0, 0), R1, 150, "gw", bias=200)           # grinding wheel
    sc.box(-120, -240, 110, 240, 150, 40, "pt", bias=500)               # regulating wheel slide
    sc.box(80, -230, 150, 110, 120, 120, "pt", ch=8, bias=-20)
    sc.cyl((-80, y2, zc - 10), (1, 0, 0), R2, 150, "dk", bias=-10)      # regulating wheel (rubber bond)
    sc.box(-110, -26, 110, 220, 30, 90, "w", bias=-30)                  # work rest blade
    sc.cyl((-250, -12, zc - 6), (1, 0, 0), 14, 500, "w", bias=-60)      # work (through-feed bar)
    sc.motor((200, y1, zc), (1, 0, 0), 26, 40)
    sc.motor((190, y2, zc - 10), (1, 0, 0), 18, 30)
    sc.rot((70, y1, zc), (1, 0, 0), R1 * .7, "", 140, 220)
    sc.axis((-250, -40, 300), (-100, -40, 300), "送り", both=False)
    sc.note((-20, y1, zc + R1), "研削砥石", "大径の砥石で外周を削る")
    sc.note((-20, y2, zc - 10 - R2), "調整車", "ゴム系の車で工作物を回し、送りを与える")
    sc.note((-90, -26, 190), "ブレード（受け板）", "工作物を下から支える")
    sc.note((200, -12, zc - 6), "工作物", "センタで支えずに連続して通す")
    sc.note((-230, -260, 60), "ベッド", "2つの砥石台を支える土台")


@mt("gear-hobbing-machine", az=-30, el=22)
def _(sc):
    sc.box(-300, -200, 0, 600, 400, 100, "pt", ch=14, bias=900)
    tc = (-70, -40)
    sc.cyl((tc[0], tc[1], 100), (0, 0, 1), 110, 40, "pt", bias=600)    # work table
    sc.cyl((tc[0], tc[1], 140), (0, 0, 1), 30, 30, "w", bias=500)      # arbor base
    sc.gear((tc[0], tc[1], 170), (0, 0, 1), 34, 78, 46, "w", helix=20, bore=18)
    sc.items[-1]["bias"] = 100
    sc.cyl((tc[0], tc[1], 216), (0, 0, 1), 16, 150, "w", bias=-30)     # arbor
    sc.box(-200, 120, 100, 240, 60, 360, "pt", ch=8, bias=400)          # outboard support column
    sc.box(-100, -10, 380, 60, 140, 50, "pt", ch=4, bias=-40)           # support arm
    sc.box(140, -10, 100, 140, 200, 470, "pt", ch=10, bias=300)         # main column (behind)
    sc.box(64, -110, 150, 76, 170, 120, "pt", ch=6, bias=200)           # hob head (Z slide)
    hy0, hl, hz = -100, 120, 194
    sc.cyl((40, hy0 - 12, hz), (0, 1, 0), 10, hl + 24, "w", bias=150)  # hob arbor
    sc.cyl((40, hy0, hz), (0, 1, 0), 30, hl, "t", bias=140)            # hob
    threads(sc, (40, hy0, hz), (0, 1, 0), 30, hl, 9, bias=139, cls="hobt")
    sc.motor((280, 90, 420), (1, 0, 0), 22, 34)
    sc.rot((tc[0], tc[1], 216), (0, 0, 1), 112, "", 200, 320)
    sc.rot((40, hy0 - 14, hz), (0, 1, 0), 44, "", 200, 330)
    sc.axis((150, -130, 200), (150, -130, 300), "Z", off=(14, 0))
    sc.note((40, hy0 + 20, hz + 30), "ホブ", "ねじ状の切れ刃を持つ工具。工作物と同期回転する")
    sc.note((tc[0] - 50, tc[1] - 60, 200), "工作物（歯車）", "ホブとかみ合いながら歯が創成される")
    sc.note((tc[0] - 90, tc[1] - 60, 120), "ワークテーブル", "工作物を載せて回す")
    sc.note((100, -110, 250), "ホブヘッド", "ホブを回し、歯幅方向（Z）に送る")
    sc.note((210, -10, 520), "コラム", "ホブヘッドを支える")
    sc.note((-80, 120, 430), "サポート", "アーバ上端を支え、たわみを防ぐ")
    sc.note((260, -200, 50), "ベッド", "機械の土台")


@mt("gear-grinding-machine", az=-50, el=20)
def _(sc):
    sc.box(-300, -200, 0, 600, 400, 100, "pt", ch=14, bias=900)
    tc = (-80, -40)
    sc.cyl((tc[0], tc[1], 100), (0, 0, 1), 100, 40, "pt", bias=600)
    sc.cyl((tc[0], tc[1], 140), (0, 0, 1), 28, 30, "w", bias=500)
    sc.gear((tc[0], tc[1], 170), (0, 0, 1), 32, 72, 40, "w", helix=20, bore=16)
    sc.items[-1]["bias"] = 100
    sc.cyl((tc[0], tc[1], 210), (0, 0, 1), 14, 120, "w", bias=-30)
    sc.box(150, -10, 100, 140, 200, 470, "pt", ch=10, bias=300)         # column
    sc.box(84, -140, 140, 66, 230, 120, "pt", ch=6, bias=200)           # wheel head
    gy0, gl, gz, R = -120, 170, 192, 52
    sc.cyl((26, gy0, gz), (0, 1, 0), R, gl, "gw", bias=140)             # threaded wheel
    threads(sc, (26, gy0, gz), (0, 1, 0), R, gl, 8, bias=139, cls="gwt")
    sc.cyl((26, gy0 - 14, gz), (0, 1, 0), 12, 14, "w", bias=150)
    sc.box(-10, 100, 250, 70, 60, 50, "dk", ch=4, bias=-20)             # dresser unit
    sc.cyl((26, 104, 262), (0, -1, 0), 22, 8, "w", bias=-30)            # diamond roll
    sc.motor((26, 70, gz), (0, 1, 0), 22, 30) if False else None
    sc.rot((tc[0], tc[1], 210), (0, 0, 1), 104, "", 200, 320)
    sc.rot((26, gy0 - 16, gz), (0, 1, 0), 70, "", 200, 330)
    sc.axis((170, -170, 200), (170, -170, 300), "Z", off=(14, 0))
    sc.note((26, gy0 + 30, gz + R), "ねじ状砥石", "ねじの形の砥石を回し、歯面を連続して創成研削する")
    sc.note((tc[0] - 50, tc[1] - 60, 200), "工作物（焼入れ後の歯車）", "砥石と同期回転しながら歯面を仕上げる")
    sc.note((tc[0] - 80, tc[1] - 60, 120), "ワークテーブル", "工作物を回す")
    sc.note((120, -140, 250), "砥石頭", "砥石を回し、歯幅方向に送る")
    sc.note((26, 104, 280), "ドレッサ", "ダイヤモンドロールで砥石の形を整える")
    sc.note((220, -10, 520), "コラム", "砥石頭を支える")
    sc.note((260, -200, 50), "ベッド", "機械の土台")


@mt("gear-skiving-machine", az=-30, el=26)
def _(sc):
    sc.box(-300, -220, 0, 600, 440, 100, "pt", ch=14, bias=900)
    tc = (-60, -60)
    sc.cyl((tc[0], tc[1], 100), (0, 0, 1), 150, 40, "pt", bias=600)
    sc.ring_gear((tc[0], tc[1], 140), (0, 0, 1), 60, 108, 140, 56, "w", helix=0)
    sc.items[-1]["bias"] = 300
    sc.box(130, -20, 100, 160, 220, 480, "pt", ch=10, bias=400)         # column
    sc.box(30, -120, 300, 110, 150, 150, "pt", ch=8, bias=100)          # spindle head
    ang = math.radians(22)
    a = (-math.sin(ang), 0, -math.cos(ang))
    c0 = (40, -60, 320)
    sc.cyl(c0, a, 26, 70, "w", bias=0)                                   # tilted spindle
    tip = tuple(c0[i] + a[i] * 70 for i in range(3))
    sc.gear(tip, a, 26, 44, 22, "t", helix=0)                           # skiving cutter
    sc.items[-1]["bias"] = -10
    sc.motor((85, 30, 450), (0, 0, 1), 26, 30)
    sc.rot((tc[0], tc[1], 200), (0, 0, 1), 160, "", 200, 320)
    sc.rot(c0, a, 46, "", 200, 320)
    sc.note((tip[0] - 20, -60, tip[2] - 10), "スカイビングカッタ", "歯車形の工具を傾けて高速で同期回転させる")
    sc.note((tc[0] - 110, tc[1] - 60, 190), "工作物（内歯車）", "リングギヤの内歯を連続して削る")
    sc.note((-30, -60, 360), "軸交差角", "工具軸を傾けることで歯すじ方向に滑りが生まれ、削れる")
    sc.note((80, -120, 440), "主軸頭", "工具を回し、歯幅方向に送る")
    sc.note((210, -20, 560), "コラム", "主軸頭を支える")
    sc.note((260, -220, 50), "ベッド", "機械の土台")


@mt("edm", az=-30, el=24)
def _(sc):
    sc.box(-280, -220, 0, 560, 440, 90, "pt", ch=14, bias=900)
    sc.box(-200, -200, 90, 330, 290, 30, "pt", bias=700)                # XY table
    sc.box(-190, -190, 120, 310, 270, 110, "dk", bias=500)              # work tank (frame)
    sc.box(-180, -180, 120, 290, 250, 96, "fl", bias=490)               # dielectric water
    sc.box(-110, -120, 140, 150, 110, 60, "w", bias=200)                # workpiece (die plate)
    sc.box(130, -60, 90, 140, 240, 470, "pt", ch=10, bias=400)          # column
    sc.box(-60, -80, 400, 200, 80, 60, "pt", ch=6, bias=100)            # upper arm
    sc.box(-50, -76, 330, 40, 50, 70, "pt", ch=4, bias=90)              # upper head (U/V, Z)
    sc.box(-60, 0, 150, 200, 60, 40, "pt", ch=4, bias=450)              # lower arm (behind work)
    def wire(s_):
        a, b = s_.P((-30, -51, 330)), s_.P((-30, -51, 150))
        return '<path class="wire" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
    sc.raw(wire, ((-31, -52, 150), (-29, -50, 330)), bias=50)
    def sparks(s_):
        p = s_.P((-30, -51, 205))
        o = ""
        for k in range(7):
            t = math.radians(k * 51)
            o += '<path class="spark" d="M%s %sL%s %s"/>' % (n(p[0]), n(p[1]), n(p[0] + 9 * math.cos(t)), n(p[1] + 9 * math.sin(t)))
        return o
    sc.raw(sparks, ((-32, -53, 203), (-28, -49, 207)), bias=40)
    sc.cyl((150, 40, 520), (1, 0, 0), 46, 40, "cu", bias=-20)           # wire spool
    sc.box(-260, 120, 90, 120, 100, 240, "dk", ch=6, bias=600)          # power supply
    sc.axis((-200, -210, 260), (-60, -210, 260), "X")
    sc.axis((-230, -200, 160), (-230, -80, 160), "Y", off=(-12, 0))
    sc.note((-30, -51, 260), "ワイヤ電極", "細い真ちゅう線などに電圧をかけ、放電で金属を溶かす")
    sc.note((-30, -76, 400), "上ガイド（上アーム）", "ワイヤを位置決めし、傾けてテーパも切れる")
    sc.note((40, 0, 170), "下アーム", "ワイヤの下側を支える")
    sc.note((-100, -120, 200), "工作物", "焼入れ鋼や超硬でも、通電すれば加工できる")
    sc.note((-180, -190, 200), "加工槽", "絶縁性の加工液（水・油）に浸して加工する")
    sc.note((170, 40, 560), "ワイヤボビン", "ワイヤを連続して送り出す")
    sc.note((-200, 120, 300), "加工電源", "放電のパルスをつくる電源")


@mt("laser-machine", az=-32, el=28)
def _(sc):
    sc.box(-320, -200, 0, 640, 400, 120, "pt", ch=12, bias=900)         # frame
    sc.box(-300, -180, 120, 600, 360, 16, "dk", bias=700)               # pallet
    def slats(s_):
        ln = ""
        for k in range(1, 30):
            x = -300 + k * 20
            a, b = s_.P((x, -180, 136)), s_.P((x, 180, 136))
            ln += "M%s %sL%s %s" % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return '<path class="mgrid" d="%s"/>' % ln
    sc.raw(slats, ((-300, -180, 136), (300, 180, 136.5)), bias=690)
    sc.box(-250, -140, 136, 420, 270, 4, "w", bias=600)                 # sheet
    for y in (-200, 200):
        sc.box(-320, y - 10, 120, 640, 20, 30, "pt", bias=650)          # X rails
    sc.box(20, -230, 150, 60, 460, 60, "pt", ch=6, bias=300)            # gantry beam (moves X)
    sc.box(80, -30, 160, 50, 80, 120, "pt", ch=4, bias=100)             # Z carriage
    sc.cyl((105, 10, 160), (0, 0, -1), 14, 18, "w", bias=50)
    sc.cyl((105, 10, 142), (0, 0, -1), 6, 6, "cu", bias=40)             # nozzle
    def beam(s_):
        p = s_.P((105, 10, 136))
        o = ""
        for k in range(9):
            t = math.radians(-160 + k * 15)
            o += '<path class="spark" d="M%s %sL%s %s"/>' % (n(p[0]), n(p[1]), n(p[0] + 14 * math.cos(t)), n(p[1] + 14 * math.sin(t) * .6))
        return o
    sc.raw(beam, ((104, 9, 136), (106, 11, 137)), bias=30)
    def kerf(s_):
        pts = [s_.P((x, 10 + 40 * math.sin((x + 200) / 60), 140)) for x in range(-200, 106, 6)]
        return '<path class="kerf" d="M%s"/>' % " L".join("%s %s" % (n(x), n(y)) for x, y in pts)
    sc.raw(kerf, ((-200, -30, 140), (105, 50, 140.5)), bias=590)
    sc.box(-340, 220, 0, 160, 120, 200, "dk", ch=8, bias=800)           # laser oscillator
    sc.axis((-150, -240, 220), (0, -240, 220), "X")
    sc.axis((170, -120, 220), (170, 60, 220), "Y", off=(14, 0))
    sc.note((105, 10, 150), "加工ヘッド", "レンズで光を集め、ノズルからアシストガスを吹く")
    sc.note((50, -230, 210), "ガントリ", "ヘッドを載せてX・Y方向に動く門形の梁")
    sc.note((-120, -60, 140), "加工中の板材", "光の熱で溶かし、ガスで吹き飛ばして切る")
    sc.note((-260, 220, 150), "レーザ発振器", "ファイバレーザなどで光をつくる")
    sc.note((-300, -180, 128), "パレット", "剣山状の受けで板を支える")
    sc.note((280, -200, 60), "フレーム", "機械の土台")


@mt("transfer-machine", az=-30, el=26)
def _(sc):
    sc.box(-380, -120, 0, 760, 220, 90, "pt", ch=10, bias=900)          # line base
    sc.box(-380, -60, 90, 760, 60, 20, "w", bias=800)                   # transfer rail
    xs = [-300, -100, 100, 300]
    for k, x in enumerate(xs):
        sc.box(x - 50, -80, 110, 100, 90, 14, "w", bias=700)            # pallet
        sc.box(x - 38, -72, 124, 76, 74, 56, "alu", bias=300)           # work
    # horizontal units from the back
    for k, x in enumerate(xs[:3]):
        sc.box(x - 70, 120, 0, 140, 200, 120, "pt", ch=6, bias=600)     # wing base
        sc.box(x - 60, 40, 120, 120, 150, 110, "pt", ch=6, bias=200)    # slide unit
        sc.box(x - 50, 10, 130, 100, 30, 90, "dk", ch=3, bias=150)      # multi-spindle head
        for i in range(3):
            for j in range(2):
                sc.cyl((x - 30 + i * 30, 10, 152 + j * 40), (0, -1, 0), 4, 26, "t", bias=100)
    # vertical unit at the last station
    sc.box(240, 40, 90, 120, 120, 380, "pt", ch=8, bias=400)
    sc.box(250, -80, 300, 100, 120, 110, "pt", ch=6, bias=100)
    sc.box(256, -70, 260, 88, 80, 40, "dk", ch=3, bias=60)
    for i in range(3):
        sc.cyl((276 + i * 24, -32, 260), (0, 0, -1), 4, 26, "t", bias=20)
    sc.axis((-360, -120, 200), (-200, -120, 200), "搬送", both=False)
    sc.note((-100, 40, 230), "加工ユニット", "1つの工程だけを受け持つ専用の加工部")
    sc.note((-100, 10, 220), "多軸ヘッド", "複数の工具を同時に回して一度に穴をあける")
    sc.note((-300, -72, 180), "工作物", "パレットに載って順番に送られる")
    sc.note((-200, -60, 110), "搬送装置", "全ステーションの工作物を同時に1ピッチ送る")
    sc.note((300, -70, 410), "立形ユニット", "上から加工するステーション")
    sc.note((330, -120, 40), "ベース", "ライン全体の土台")


# =====================================================================================
# components
# =====================================================================================
def arc_shell(r_out, r_in, a0, a1, cy=0.0, cz=0.0, seg=28):
    pts = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        pts.append((cy + r_out * math.cos(t), cz + r_out * math.sin(t)))
    for k in range(seg, -1, -1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        pts.append((cy + r_in * math.cos(t), cz + r_in * math.sin(t)))
    return pts


def cone(sc, O, A, r0, r1, h, mat="w", bias=0.0):
    a = GE._norm(A)
    sc.add(GE.cyl(sc.cam, O, a, r0, h, mat, scale=lambda t: (r0 + (r1 - r0) * t) / r0), sc._cbb(O, a, max(r0, r1), h), bias)


@mt("spindle", az=-30, el=22)
def _(sc):
    # housing cut open: keep the back half (y>0)
    sc.xpr(-260, 520, arc_shell(120, 104, -90, 90), "pt", bias=500)
    sc.cyl((-300, 0, 0), (1, 0, 0), 40, 560, "w", bias=200)              # shaft
    for x in (150, 186):                                                  # front bearing pair
        sc.ring((x, 0, 0), (1, 0, 0), 104, 40, 30, "w", bias=100)
    sc.ring((-220, 0, 0), (1, 0, 0), 96, 40, 28, "w", bias=100)          # rear bearing
    sc.xpr(-120, 200, arc_shell(104, 74, -90, 90), "cu", bias=300)        # stator (back half)
    sc.cyl((-110, 0, 0), (1, 0, 0), 70, 180, "dk", bias=150)             # rotor on the shaft
    cone(sc, (260, 0, 0), (1, 0, 0), 44, 30, 34, "w", bias=50)           # nose / taper
    sc.cyl((294, 0, 0), (1, 0, 0), 46, 16, "w", bias=40)                 # holder flange
    sc.cyl((310, 0, 0), (1, 0, 0), 22, 40, "w", bias=30)
    sc.cyl((350, 0, 0), (1, 0, 0), 12, 70, "t", bias=20)
    sc.rot((330, 0, 0), (1, 0, 0), 60, "", 200, 330)
    sc.note((-280, 0, 40), "主軸（シャフト）", "工具や工作物を取り付けて回す軸")
    sc.note((168, 0, 104), "主軸軸受（前側）", "アンギュラ玉軸受を組み合わせ、予圧をかけて剛性を出す")
    sc.note((-220, 0, -96), "主軸軸受（後側）", "熱による伸びを逃がす側の軸受")
    sc.note((-20, 60, 100), "ステータ", "ビルトインモータの固定子（巻線）")
    sc.note((-20, 0, -70), "ロータ", "主軸と一体で回るモータの回転子")
    sc.note((270, 0, 40), "主軸テーパ", "ツールホルダを引き込んで固定する")
    sc.note((380, 0, -12), "工具", "ツールホルダに保持された切削工具")
    sc.note((-160, 120, -60), "ハウジング", "軸受とモータを収める外筒（切断して表示）")


@mt("ball-screw", az=-28, el=22)
def _(sc):
    sc.box(-330, -60, -60, 50, 120, 120, "pt", ch=6, bias=200)            # fixed-side support
    sc.box(300, -60, -60, 50, 120, 120, "pt", ch=6, bias=-10)             # support (free side)
    sc.cyl((-360, 0, 0), (1, 0, 0), 16, 700, "w", bias=150)
    sc.cyl((-300, 0, 0), (1, 0, 0), 30, 600, "w", bias=140)               # screw shaft
    threads(sc, (-300, 0, 0), (1, 0, 0), 30, 600, 16, bias=139)
    sc.cyl((-30, 0, 0), (1, 0, 0), 52, 120, "w", bias=50)                 # nut
    sc.xpr(-50, 22, [(-80, -50), (80, -50), (80, 50), (-80, 50)], "w", bias=40)   # flange
    def balls(s_):
        o = ""
        for k in range(9):
            p = s_.P((-14 + k * 12, -36, 24))
            o += '<circle class="ball" cx="%s" cy="%s" r="5.6"/>' % (n(p[0]), n(p[1]))
        a, b, c = s_.P((-22, -48, 6)), s_.P((96, -48, 6)), s_.P((96, -48, 44))
        o = '<path class="cutw" d="M%s %sL%s %sL%s %sL%s %sZ"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]), n(s_.P((-22, -48, 44))[0]), n(s_.P((-22, -48, 44))[1])) + o
        return o
    sc.raw(balls, ((-22, -52, 6), (96, -48, 44)), bias=-20)
    sc.motor((-440, 0, 0), (-1, 0, 0), 40, 60)
    sc.cyl((-400, 0, 0), (1, 0, 0), 26, 40, "w", bias=160)                # coupling
    sc.axis((-60, -90, 80), (110, -90, 80), "直線運動")
    sc.rot((-200, 0, 0), (1, 0, 0), 46, "", 200, 330)
    sc.note((180, 0, 30), "ねじ軸", "らせん状の溝を持つ軸。モータで回す")
    sc.note((20, -52, 0), "ナット", "回転を直線運動に変える。テーブルなどに固定する")
    sc.note((40, -40, 30), "ボール（鋼球）", "溝の中を転がり、循環して戻る。摩擦が小さい")
    sc.note((-40, -50, 50), "フランジ", "ナットを可動部に取り付ける")
    sc.note((-305, -60, 40), "サポート軸受", "ねじ軸を両端で支え、軸方向の力を受ける")
    sc.note((-480, 0, 30), "サーボモータ", "カップリングでねじ軸を回す")


@mt("linear-guide", az=-34, el=26)
def _(sc):
    rail = [(-22, 0), (22, 0), (22, 30), (18, 34), (22, 38), (22, 52), (-22, 52), (-22, 38), (-18, 34), (-22, 30)]
    sc.xpr(-320, 640, rail, "w", bias=200)
    def holes(s_):
        o = ""
        for k in range(8):
            p = s_.P((-280 + k * 80, 0, 52))
            o += '<ellipse class="bolt" cx="%s" cy="%s" rx="6" ry="3.2"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(holes, ((-280, -6, 52), (280, 6, 52.5)), bias=190)
    blk = [(-60, 16), (-26, 16), (-26, 38), (-22, 42), (-22, 56), (22, 56), (22, 42), (26, 38), (26, 16), (60, 16), (60, 90), (-60, 90)]
    sc.xpr(-60, 150, blk, "w", bias=50)                                   # block (carriage)
    sc.xpr(90, 10, blk, "dk", bias=40)                                    # end seal
    sc.xpr(-70, 10, blk, "dk", bias=60)
    def ballc(s_):
        o = ""
        for y, z in ((-40, 50), (40, 50), (-40, 30), (40, 30)):
            p = s_.P((100, y, z))
            o += '<circle class="ball" cx="%s" cy="%s" r="5"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(ballc, ((100, -45, 25), (101, 45, 55)), bias=30)
    sc.axis((-40, -80, 120), (120, -80, 120), "直線運動")
    sc.note((260, 0, 40), "レール", "機械のベッドやコラムにボルトで固定する")
    sc.note((0, -60, 90), "ブロック（キャリッジ）", "テーブルなどを載せてレールの上を動く")
    sc.note((100, 40, 50), "転動体（ボール）", "ブロック内を循環し、転がって摩擦を減らす")
    sc.note((95, -60, 60), "エンドシール", "切りくずやクーラントの侵入を防ぐ")
    sc.note((-200, 0, 52), "取付穴", "レールを固定するボルト穴")


@mt("slideway", az=-30, el=26)
def _(sc):
    bed = [(-200, 0), (200, 0), (200, 80), (150, 80), (120, 110), (90, 80), (-100, 80), (-100, 104), (-150, 104), (-150, 80), (-200, 80)]
    sc.xpr(-320, 640, bed, "pt", bias=300)
    def scrape(s_):
        o = ""
        for i in range(30):
            for j in range(2):
                x = -300 + i * 20 + (j * 10)
                y = -142 + j * 16
                p = s_.P((x, y, 104))
                o += '<path class="scr" d="M%s %sq4 -3 8 0"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(scrape, ((-300, -150, 104), (300, -100, 104.5)), bias=290)
    car = [(-210, 110), (-150, 110), (-150, 104), (-100, 104), (-100, 110), (92, 110), (120, 138), (148, 110), (210, 110), (210, 190), (-210, 190)]
    sc.xpr(-120, 240, car, "pt", bias=50)                                 # carriage
    sc.xpr(-120, 240, [(-150, 104), (-100, 104), (-100, 110), (-150, 110)], "dk", bias=60)  # liner
    sc.axis((-100, -230, 220), (100, -230, 220), "往復")
    sc.note((-125, -150, 104), "案内面（平形）", "平らな面で荷重を受ける")
    sc.note((120, 120, 105), "案内面（V形）", "V字の面で横方向の位置を決める")
    sc.note((0, -210, 170), "テーブル（往復台）", "案内面の上を滑って動く")
    sc.note((-125, -150, 108), "すべり材", "摩擦が小さく、焼付きにくい樹脂シート")
    sc.note((-250, -150, 104), "きさげ模様", "手作業で削った細かなくぼみ。油をため、当たりを整える")
    sc.note((-280, -200, 40), "ベッド", "案内面を一体で削り出した鋳物")


@mt("servo-motor", az=-30, el=22)
def _(sc):
    sc.box(-260, -60, -60, 30, 120, 120, "dk", ch=8, bias=100)            # flange
    sc.cyl((-230, 0, 0), (1, 0, 0), 56, 180, "dk", bias=90)               # body
    sc.cyl((-50, 0, 0), (1, 0, 0), 44, 40, "dk", bias=80)                 # encoder cover
    sc.cyl((-290, 0, 0), (1, 0, 0), 12, 30, "w", bias=110)                # shaft
    sc.box(-70, -70, 40, 30, 26, 22, "dk", bias=70)                       # connector
    # linear motor
    for k in range(10):
        sc.box(80 + k * 30, -50, -70, 26, 100, 14, "cu" if k % 2 else "dk", bias=300)
    sc.box(60, -60, -84, 320, 120, 14, "w", bias=320)                      # yoke plate
    sc.box(150, -46, -54, 160, 92, 40, "pt", ch=6, bias=50)               # coil slider
    sc.axis((150, -80, 10), (310, -80, 10), "直線運動")
    sc.note((-140, 0, 56), "サーボモータ", "回転角と速度を正確に制御するモータ")
    sc.note((-30, 0, 44), "エンコーダ", "回転位置を検出してNCに返す")
    sc.note((-300, 0, 0), "出力軸", "カップリングでボールねじや主軸につなぐ")
    sc.note((230, -46, -14), "リニアモータ（可動子）", "コイルに電流を流して直接まっすぐ動く")
    sc.note((340, -50, -60), "磁石（固定子）", "N極とS極を交互に並べた板")


@mt("cnc", az=-18, el=10)
def _(sc):
    sc.box(-200, 0, 0, 400, 60, 300, "dk", ch=10, bias=100)
    def face(s_):
        def q(x0, z0, x1, z1, cls, y=-0.5):
            a, b, c, d = s_.P((x0, y, z0)), s_.P((x1, y, z0)), s_.P((x1, y, z1)), s_.P((x0, y, z1))
            return '<path class="%s" d="M%s %sL%s %sL%s %sL%s %sZ"/>' % (cls, n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]), n(d[0]), n(d[1]))
        o = q(-180, 120, 40, 280, "scrn")
        for i in range(6):
            o += q(-170, 252 - i * 22, -60, 256 - i * 22, "scrl")
        o += q(-40, 250, 30, 260, "scrl") + q(-40, 140, 30, 220, "scrg")
        for r in range(4):
            for c in range(6):
                o += q(56 + c * 22, 250 - r * 22, 72 + c * 22, 264 - r * 22, "key")
        for c in range(8):
            o += q(-176 + c * 26, 92, -156 + c * 26, 106, "key")
        for c in range(5):
            o += q(-176 + c * 30, 30, -152 + c * 30, 70, "kbtn")
        p = s_.P((120, -1, 60))
        o += '<ellipse class="mpg" cx="%s" cy="%s" rx="26" ry="25"/><ellipse class="mpg2" cx="%s" cy="%s" rx="17" ry="16"/>' % (n(p[0]), n(p[1]), n(p[0]), n(p[1]))
        p = s_.P((176, -1, 50))
        o += '<circle class="estop" cx="%s" cy="%s" r="15"/>' % (n(p[0]), n(p[1]))
        p = s_.P((176, -1, 110))
        o += '<circle class="knob" cx="%s" cy="%s" r="12"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(face, ((-200, -1, 0), (200, 0, 300)), bias=0)
    sc.note((-70, 0, 200), "表示画面", "プログラム・座標・負荷などを表示する")
    sc.note((110, 0, 220), "操作キー", "プログラムの入力・編集をする")
    sc.note((120, 0, 60), "手動パルス発生器", "ハンドルを回して軸を少しずつ動かす")
    sc.note((176, 0, 50), "非常停止", "押すと機械をすぐに止める")
    sc.note((-120, 0, 50), "運転ボタン", "自動運転の起動・停止、モード切替")
    sc.note((176, 0, 110), "オーバライド", "送り速度や主軸回転を運転中に調整する")


@mt("atc", az=-30, el=20)
def _(sc):
    sc.cyl((-200, 0, 160), (1, 0, 0), 150, 26, "pt", bias=300)           # magazine disc
    for k in range(16):
        t = 2 * math.pi * k / 16
        y, z = 128 * math.cos(t), 160 + 128 * math.sin(t)
        sc.cyl((-174, y, z), (1, 0, 0), 13, 18, "w", bias=250)            # pots
        if math.cos(t) < -0.3:
            sc.cyl((-156, y, z), (1, 0, 0), 6, 30, "t", bias=240)
    sc.box(-40, 80, -40, 200, 160, 120, "pt", ch=8, bias=200)             # spindle head (cut)
    sc.cyl((40, 120, 80), (0, 0, -1), 30, 30, "w", bias=100)              # spindle nose
    # double arm swinging between pot and spindle
    sc.box(-140, -30, 120, 200, 60, 20, "w", ch=4, bias=50)
    sc.cyl((-40, 0, 110), (0, 0, 1), 24, 40, "dk", bias=40)
    sc.cyl((-130, 0, 100), (0, 0, -1), 14, 50, "w", bias=30)              # tool in gripper
    sc.cyl((50, 0, 100), (0, 0, -1), 14, 50, "w", bias=30)
    sc.rot((-40, 0, 140), (0, 0, 1), 80, "", 200, 330)
    sc.note((-200, -150, 280), "工具マガジン", "多数の工具をポットに収納して回る")
    sc.note((-174, -128, 160), "工具ポット", "ツールホルダを1本ずつ保持する")
    sc.note((-60, -30, 140), "交換アーム", "両端で新旧の工具をつかみ、回って入れ替える")
    sc.note((40, 120, 50), "主軸", "交換時は決まった向きで止まる（オリエンテーション）")
    sc.note((50, 0, 60), "ツールホルダ", "工具を保持し、主軸テーパに入る")


@mt("tool-holder", az=-24, el=16)
def _(sc):
    # BT holder (left): 7/24 taper + flange with V-groove + pull stud
    x0 = -260
    sc.cyl((x0 - 40, -60, 0), (1, 0, 0), 9, 40, "w", bias=100)          # pull stud
    cone(sc, (x0, -60, 0), (1, 0, 0), 22, 40, 70, "w", bias=90)          # taper
    sc.cyl((x0 + 70, -60, 0), (1, 0, 0), 56, 30, "w", bias=80)           # flange
    sc.ring((x0 + 84, -60, 0), (1, 0, 0), 57, 48, 6, "dk", bias=75)      # V-groove
    sc.cyl((x0 + 100, -60, 0), (1, 0, 0), 30, 60, "w", bias=70)
    sc.cyl((x0 + 160, -60, 0), (1, 0, 0), 12, 70, "t", bias=60)
    # HSK holder (right): short hollow taper + flange face contact
    x1 = 60
    sc.ring((x1, 60, 0), (1, 0, 0), 34, 22, 50, "w")
    sc.items[-1]["bias"] = 50
    cone(sc, (x1, 60, 0), (1, 0, 0), 30, 36, 50, "w", bias=45)
    sc.cyl((x1 + 50, 60, 0), (1, 0, 0), 50, 30, "w", bias=40)
    sc.cyl((x1 + 80, 60, 0), (1, 0, 0), 28, 60, "w", bias=30)
    sc.cyl((x1 + 140, 60, 0), (1, 0, 0), 12, 70, "t", bias=20)
    sc.note((x0 - 30, -60, 9), "プルスタッド", "主軸のクランプ機構が引き込む（BT）")
    sc.note((x0 + 30, -60, 30), "テーパ部（7/24）", "主軸の内テーパに入って芯を合わせる")
    sc.note((x0 + 85, -60, 56), "フランジ（V溝）", "ATCのアームがつかむ溝")
    sc.note((x0 + 200, -60, 12), "工具", "エンドミル・ドリルなど")
    sc.note((x1 + 20, 60, 34), "中空短テーパ（HSK）", "内側から引き込み、テーパと端面の2面で固定する")
    sc.note((x1 + 52, 60, 50), "端面拘束", "高速回転でも抜けにくく、振れが小さい")


@mt("chuck", az=-30, el=20)
def _(sc):
    sc.cyl((-200, 0, 0), (1, 0, 0), 70, 60, "dk", bias=200)               # hydraulic cylinder
    sc.cyl((-140, 0, 0), (1, 0, 0), 30, 60, "w", bias=190)                # draw tube
    sc.cyl((-80, 0, 0), (1, 0, 0), 120, 80, "w", bias=150)                # chuck body
    def bolts(s_):
        o = ""
        for k in range(6):
            t = math.radians(k * 60)
            p = s_.P((0, 96 * math.cos(t), 96 * math.sin(t)))
            o += '<circle class="bolt" cx="%s" cy="%s" r="3.4"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(bolts, ((0, -96, -96), (0.5, 96, 96)), bias=140)
    jaws3(sc, 0, 0, 0, 34, 104, 30, 20)                                   # master jaws
    for it in sc.items[-3:]:
        it["bias"] = 100
    jaws3(sc, 20, 0, 0, 38, 92, 26, 34, "alu")                            # soft top jaws
    for it in sc.items[-3:]:
        it["bias"] = 60
    sc.cyl((20, 0, 0), (1, 0, 0), 36, 150, "w", bias=0)                   # workpiece
    sc.axis((-60, -140, 120), (-60, -140, 40), "把握", both=False)
    sc.note((-40, -110, 60), "チャック本体", "主軸の先端に取り付ける")
    sc.note((10, 70, 60), "マスタージョー", "本体の溝を半径方向に動く")
    sc.note((40, -50, 70), "生爪（トップジョー）", "工作物に合わせて削って使う柔らかい爪")
    sc.note((150, 0, 36), "工作物", "爪で外径をつかむ")
    sc.note((-170, 0, -70), "油圧シリンダ", "ドローチューブを引いて爪を閉じる")


@mt("turret", az=-34, el=18)
def _(sc):
    sc.box(-260, -120, -130, 180, 240, 250, "pt", ch=10, bias=400)        # turret housing (behind)
    sc.motor((-260, 70, 80), (-1, 0, 0), 22, 34)
    sc.ring((-80, 0, 0), (1, 0, 0), 96, 70, 16, "dk", bias=300)          # curvic coupling
    turret_disc(sc, -64, 60, 0, 0, 112, 12, mat="w")
    sc.items[-1]["bias"] = 200
    def faceplate(s_):
        o = ""
        for k in range(12):
            t = 2 * math.pi * k / 12 + math.pi / 12
            p = s_.P((-4, 84 * math.cos(t), 84 * math.sin(t)))
            o += '<circle class="bolt" cx="%s" cy="%s" r="3"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(faceplate, ((-4, -84, -84), (-3.5, 84, 84)), bias=150)
    for k in range(12):
        t = 2 * math.pi * k / 12 + math.pi / 12
        y, z = 92 * math.cos(t), 92 * math.sin(t)
        if k % 3 == 0:
            sc.cyl((-4, y, z), (1, 0, 0), 15, 34, "dk", bias=100)        # driven-tool unit
            sc.cyl((30, y, z), (1, 0, 0), 6, 40, "t", bias=90)
        else:
            sc.box(-4, y - 11, z - 11, 34, 22, 22, "w", bias=100)        # turning holder
            sc.box(30, y - 5, z - 5, 22, 10, 10, "t", bias=90)
    sc.rot((70, 0, 0), (1, 0, 0), 150, "割出し", 200, 300)
    sc.note((-34, 0, 112), "タレット本体", "12角などの割出し盤。周囲に工具を並べる")
    sc.note((41, 92 * math.cos(math.pi / 12 + math.pi / 6), 92 * math.sin(math.pi / 12 + math.pi / 6)), "工具ホルダ・バイト", "旋削用の工具を固定する")
    sc.note((50, 92 * math.cos(math.pi / 12), 92 * math.sin(math.pi / 12)), "回転工具", "ドリル・エンドミルを回す（複合化）")
    sc.note((-80, -96, -40), "カップリング", "歯形の噛み合いで割出し位置を固定する")
    sc.note((-290, 70, 90), "割出しモータ", "タレットを回して工具を選ぶ")
    sc.note((-200, -120, 60), "タレット台", "X・Z軸で動く刃物台本体")


@mt("coolant", az=-30, el=22)
def _(sc):
    sc.box(-300, -120, 0, 340, 220, 140, "fl", bias=400)                  # tank (water level)
    sc.box(-310, -130, 0, 360, 240, 150, "pt", ch=8, bias=420)            # tank shell drawn first
    sc.box(-300, -120, 140, 340, 220, 4, "fl", bias=380)
    sc.box(80, -60, 0, 100, 120, 160, "pt", ch=6, bias=300)               # filter unit
    sc.cyl((-200, 0, 150), (0, 0, 1), 26, 60, "dk", bias=200)             # pump
    sc.cyl((-200, 0, 210), (0, 0, 1), 18, 30, "dk", bias=190)
    def pipe(s_):
        pts = [s_.P(p) for p in ((-200, 0, 240), (-200, 0, 330), (60, 0, 330), (180, -40, 330), (230, -40, 300))]
        return '<path class="pipe" d="M%s"/>' % " L".join("%s %s" % (n(x), n(y)) for x, y in pts)
    sc.raw(pipe, ((-200, -40, 240), (230, 0, 330)), bias=150)
    sc.cyl((240, -40, 330), (0, 0, -1), 22, 40, "w", bias=100)            # spindle nose
    sc.cyl((240, -40, 290), (0, 0, -1), 8, 50, "t", bias=90)              # tool
    sc.box(170, -120, 180, 150, 140, 60, "alu", bias=120)                 # workpiece
    def spray(s_):
        a = s_.P((230, -40, 300))
        b = s_.P((240, -40, 245))
        o = ""
        for k in range(-3, 4):
            o += '<path class="spray" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0] + k * 5), n(b[1] + abs(k) * 2))
        return o
    sc.raw(spray, ((228, -42, 240), (242, -38, 302)), bias=50)
    def chips(s_):
        o = ""
        for k in range(14):
            p = s_.P((190 + (k * 37) % 110, -110 + (k * 53) % 120, 241))
            o += '<path class="chipc" d="M%s %sq4 -6 8 0q4 6 8 0"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(chips, ((190, -110, 241), (300, 10, 241.5)), bias=40)
    sc.note((240, -40, 280), "ノズル", "刃先に切削油を吹き付け、冷却・潤滑・切りくず排出をする")
    sc.note((260, -110, 250), "切りくず", "クーラントで流してコンベヤへ送る")
    sc.note((-120, -120, 100), "クーラントタンク", "使った切削油を回収してためる")
    sc.note((-200, 0, 180), "ポンプ", "加圧して刃先や主軸の中へ送る")
    sc.note((130, -60, 120), "ろ過装置", "細かい切りくずを除いて再利用する")


@mt("bed", az=-32, el=30)
def _(sc):
    L, Wd, Hh, t = 560, 300, 120, 14
    sc.box(-L / 2, -Wd / 2, 0, L, Wd, 14, "pt", bias=600)                 # bottom plate
    sc.box(-L / 2, Wd / 2 - t, 0, L, t, Hh, "pt", bias=500)                # back wall
    sc.box(-L / 2, -Wd / 2 + t, 0, t, Wd - 2 * t, Hh, "pt", bias=480)      # left wall
    for k in range(1, 6):                                                  # transverse ribs
        x = -L / 2 + k * L / 6
        sc.box(x - 5, -Wd / 2 + t, 0, 10, Wd - 2 * t, Hh - 10, "pt", bias=400 - k)
    for y in (-50, 50):                                                    # longitudinal ribs
        sc.box(-L / 2 + t, y - 5, 0, L - 2 * t, 10, Hh - 10, "pt", bias=420)
    sc.box(L / 2 - t, -Wd / 2 + t, 0, t, Wd - 2 * t, Hh, "pt", bias=100)   # right wall
    sc.box(-L / 2, -Wd / 2, 0, L, t, Hh, "pt", bias=50)                    # front wall
    for y in (-110, 110):
        sc.box(-L / 2 + 10, y - 16, Hh, L - 20, 32, 10, "w", bias=40)      # guideway mounting faces
    for x in (-L / 2 + 30, L / 2 - 30):
        for y in (-Wd / 2 - 16, Wd / 2 + 16):
            sc.cyl((x, y, -20), (0, 0, 1), 12, 30, "dk", bias=700)         # leveling bolts
    sc.note((-L / 2, -Wd / 2, 60), "外壁", "鋳物の箱形。断面を閉じてねじれに強くする")
    sc.note((-L / 2 + 3 * L / 6, 0, Hh - 10), "リブ（補強）", "格子状の壁で、軽くしながら剛性を上げる")
    sc.note((0, -110, Hh + 10), "案内面の取付面", "リニアガイドやすべり案内面を載せる精密な面")
    sc.note((L / 2 - 30, -Wd / 2 - 16, 0), "レベリングボルト", "据付時に水平を出し、ねじれを抑える")
    sc.note((L / 2, 0, 60), "鋳物（FC材）", "振動を吸収しやすいねずみ鋳鉄が多い")


@mt("thermal-displacement", az=-26, el=18)
def _(sc):
    sc.box(-260, -160, 0, 520, 320, 70, "pt", ch=10, bias=600)
    sc.box(-90, 60, 70, 180, 110, 380, "pt", ch=8, bias=300)              # column
    sc.box(-70, -40, 300, 140, 110, 120, "pt", ch=8, bias=100)            # spindle head
    sc.cyl((0, 0, 300), (0, 0, -1), 26, 24, "w", bias=50)
    sc.cyl((0, 0, 276), (0, 0, -1), 8, 40, "t", bias=40)
    sc.box(-180, -130, 70, 360, 170, 30, "pt", bias=200)                  # table
    def heat(s_):
        p = s_.P((0, -40, 360))
        q = s_.P((0, 60, 200))
        o = '<ellipse class="heatg" cx="%s" cy="%s" rx="70" ry="54"/>' % (n(p[0]), n(p[1]))
        o += '<ellipse class="heatg2" cx="%s" cy="%s" rx="44" ry="80"/>' % (n(q[0]), n(q[1]))
        # deformed outline of the column (exaggerated)
        pts = [s_.P(v) for v in ((-90, 60, 70), (-90, 60, 450), (90, 60, 470), (90, 60, 70))]
        bend = [(x + (k in (1, 2)) * 18, y) for k, (x, y) in enumerate(pts)]
        o += '<path class="ghost" d="M%s"/>' % " L".join("%s %s" % (n(x), n(y)) for x, y in bend)
        return o
    sc.raw(heat, ((-90, -40, 70), (90, 60, 470)), bias=-20)
    sc.axis((0, -40, 250), (0, -40, 220), "伸び", both=False, off=(20, 4))
    sc.axis((100, 60, 470), (140, 60, 470), "傾き", both=False, off=(0, -8))
    def sensors(s_):
        o = ""
        for p in ((-90, 20, 200), (-90, 20, 380), (-70, -40, 380)):
            q = s_.P(p)
            o += '<circle class="sensor" cx="%s" cy="%s" r="5"/>' % (n(q[0]), n(q[1]))
        return o
    sc.raw(sensors, ((-91, -40, 200), (-70, 20, 380)), bias=-30)
    sc.note((0, -40, 400), "熱源（主軸・モータ）", "回転による発熱で主軸頭が膨張する")
    sc.note((0, -40, 236), "主軸の伸び", "Z方向の寸法がずれる")
    sc.note((90, 60, 470), "コラムの傾き", "前後の温度差で構造が反る（誇張して表示）")
    sc.note((-90, 20, 380), "温度センサ", "各部の温度を測り、NCが補正量を計算する")
    sc.note((-180, -130, 90), "テーブル・工作物", "環境温度の変化でも伸び縮みする")


# =====================================================================================
# automation
# =====================================================================================
def lathe_box(sc, x, y, w=220, d=200, h=260, door=True, bias=0.0):
    sc.box(x, y, 0, w, d, h, "pt", ch=10, bias=bias)
    if door:
        def dr(s_):
            a, b, c, dd = (s_.P((x + w * .18, y - .5, h * .3)), s_.P((x + w * .82, y - .5, h * .3)), s_.P((x + w * .82, y - .5, h * .85)), s_.P((x + w * .18, y - .5, h * .85)))
            return '<path class="win" d="M%s %sL%s %sL%s %sL%s %sZ"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]), n(c[0]), n(c[1]), n(dd[0]), n(dd[1]))
        sc.raw(dr, ((x, y - 1, h * .3), (x + w, y, h * .85)), bias - .01)


@mt("gantry-loader", az=-30, el=24)
def _(sc):
    lathe_box(sc, -330, -100, bias=300)
    lathe_box(sc, -60, -100, bias=300)
    sc.box(210, -90, 0, 140, 160, 120, "dk", ch=6, bias=300)              # work stocker
    for i in range(3):
        for j in range(2):
            sc.cyl((240 + i * 40, -60 + j * 50, 120), (0, 0, 1), 14, 24, "w", bias=200)
    for x in (-360, 380):
        sc.box(x - 15, 120, 0, 30, 30, 420, "pt", bias=250)               # posts
    sc.box(-380, 100, 400, 790, 60, 50, "pt", ch=4, bias=100)              # travelling beam
    sc.box(100, 50, 360, 70, 120, 120, "pt", ch=4, bias=50)                # carriage
    sc.box(122, 70, 180, 26, 26, 200, "w", bias=40)                        # vertical arm
    sc.box(110, 58, 160, 50, 50, 24, "dk", bias=30)                        # hand
    sc.axis((-200, 70, 480), (40, 70, 480), "走行")
    sc.axis((180, 80, 240), (180, 80, 320), "上下", off=(18, 0))
    sc.note((-320, 130, 450), "走行軸（ガントリ）", "機械の上を横切る梁。ハンドを横に運ぶ")
    sc.note((135, 58, 160), "ローダハンド", "工作物をつかみ、扉の上から機械に出し入れする")
    sc.note((-220, -100, 200), "工作機械1", "旋盤など。工程順に並べる")
    sc.note((50, -100, 200), "工作機械2", "")
    sc.note((280, -90, 140), "ワークストッカ", "素材と完成品を置く台")


@mt("robot-loading", az=-30, el=24)
def _(sc):
    lathe_box(sc, -320, 40, 240, 220, 270, bias=300)
    sc.box(150, -80, 0, 170, 140, 100, "dk", ch=6, bias=300)              # parts table
    for i in range(3):
        for j in range(2):
            sc.cyl((180 + i * 50, -50 + j * 60, 100), (0, 0, 1), 15, 22, "w", bias=200)
    # 6-axis robot
    b = (0, -60)
    sc.cyl((b[0], b[1], 0), (0, 0, 1), 46, 30, "pt", bias=150)
    sc.cyl((b[0], b[1], 30), (0, 0, 1), 36, 60, "pt", bias=140)
    a1 = math.radians(60)
    p1 = (b[0], b[1], 110)
    p2 = (b[0] - 40, b[1] + 50, 260)
    p3 = (b[0] - 150, b[1] + 80, 230)
    def link(pa, pb, r, mat, bias):
        d = [pb[i] - pa[i] for i in range(3)]
        L = math.sqrt(sum(v * v for v in d))
        sc.cyl(pa, d, r, L, mat, bias)
    link(p1, p2, 22, "pt", 100)
    sc.cyl((p2[0] - 26, p2[1], p2[2]), (1, 0, 0), 26, 52, "pt", bias=90)
    link(p2, p3, 17, "pt", 80)
    sc.cyl(p3, (-1, 0, -0.3), 14, 30, "dk", bias=60)
    sc.cyl((p3[0] - 30, p3[1], p3[2] - 9), (0, 0, -1), 10, 30, "w", bias=50)
    def fence(s_):
        o = ""
        for x in (-60, 60, 180, 300):
            a, c = s_.P((x, -200, 0)), s_.P((x, -200, 160))
            o += '<path class="fence" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        a, c = s_.P((-60, -200, 160)), s_.P((300, -200, 160))
        o += '<path class="fence" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(c[0]), n(c[1]))
        return o
    sc.raw(fence, ((-60, -201, 0), (300, -199, 160)), bias=-100)
    sc.note((p2[0], p2[1], p2[2] + 20), "ロボット", "6軸の多関節ロボット。工作物を出し入れする")
    sc.note((p3[0] - 30, p3[1], p3[2] - 40), "ハンド", "工作物に合わせた爪でつかむ")
    sc.note((-200, 40, 260), "工作機械", "ドアを自動で開け閉めする")
    sc.note((260, -80, 110), "ワークストッカ", "素材と完成品を並べる")
    sc.note((120, -200, 160), "安全柵", "人が近づくと止まるよう囲う（協働ロボットでは省けることもある）")


@mt("pallet-changer", az=-30, el=26)
def _(sc):
    sc.box(-340, 40, 0, 260, 260, 320, "pt", ch=12, bias=300)            # HMC
    sc.box(-60, 40, 0, 240, 260, 60, "pt", ch=6, bias=280)                # changer base
    sc.box(-40, 70, 60, 90, 90, 14, "w", ch=3, bias=200)
    sc.box(70, 70, 60, 90, 90, 14, "w", ch=3, bias=200)
    sc.box(-20, 90, 74, 50, 40, 70, "alu", bias=150)
    sc.box(200, -60, 0, 160, 340, 330, "pt", ch=6, bias=400)              # pallet stocker rack
    for k in range(3):
        sc.box(196, -40, 30 + k * 100, 120, 300, 12, "w", bias=350 - k)
    sc.box(-60, -170, 0, 240, 120, 40, "dk", ch=6, bias=100)              # transfer cart rail
    sc.box(-20, -160, 40, 140, 100, 30, "pt", ch=4, bias=90)              # cart
    sc.box(0, -150, 70, 100, 80, 12, "w", ch=3, bias=80)                  # pallet on cart
    sc.box(-330, -180, 0, 180, 140, 90, "pt", ch=6, bias=150)             # setup station
    sc.box(-310, -170, 90, 120, 100, 12, "w", ch=3, bias=140)
    sc.note((-210, 40, 330), "工作機械", "横形マシニングセンタなど")
    sc.note((40, 90, 120), "パレット", "治具ごと工作物を載せる台。機械の外で段取りできる")
    sc.note((260, -60, 300), "パレットストッカ", "複数のパレットを棚に置き、夜間も連続運転する")
    sc.note((50, -160, 70), "搬送台車", "パレットを棚と機械の間で運ぶ")
    sc.note((-250, -180, 100), "段取りステーション", "作業者が工作物を付け外しする場所")


@mt("bar-feeder", az=-24, el=22)
def _(sc):
    sc.box(-380, -60, 0, 360, 120, 150, "pt", ch=8, bias=300)             # bar feeder body
    sc.box(-380, -60, 150, 360, 120, 40, "dk", ch=4, bias=250)            # cover
    for k in range(5):
        sc.cyl((-370, -110 - k * 4, 160 + k * 12), (1, 0, 0), 6, 300, "w", bias=320 + k)   # bars in rack
    sc.box(-380, -140, 120, 300, 70, 10, "pt", bias=330)                  # magazine rack
    sc.cyl((-20, 0, 190), (1, 0, 0), 6, 120, "w", bias=-50)               # bar into the spindle
    lathe_box(sc, 0, -100, 300, 220, 280, bias=200)
    sc.axis((-300, -60, 230), (-120, -60, 230), "送り", both=False)
    sc.note((-200, -60, 190), "バーフィーダ", "長い棒材を主軸の後ろから押し出して送る")
    sc.note((-250, -120, 170), "材料ラック", "次に使う棒材を並べ、自動で補給する")
    sc.note((40, 0, 190), "棒材", "主軸の中を通って加工位置まで送られる")
    sc.note((150, -100, 200), "工作機械", "NC旋盤や主軸移動形自動旋盤")


@mt("in-process-gauging", az=-28, el=20)
def _(sc):
    sc.box(-260, -160, 0, 520, 320, 40, "pt", bias=600)                   # table
    sc.box(-160, -100, 40, 240, 180, 110, "alu", bias=400)                # workpiece
    sc.cyl((-40, -10, 150), (0, 0, -1), 50, 20, "w", bias=300) if False else None
    sc.box(-40, -40, 150, 80, 80, 1, "dk", bias=390) if False else None
    sc.cyl((-30, -10, 350), (0, 0, -1), 40, 30, "w", bias=200)            # spindle nose
    sc.cyl((-30, -10, 320), (0, 0, -1), 20, 30, "w", bias=190)            # holder
    sc.cyl((-30, -10, 290), (0, 0, -1), 22, 50, "dk", bias=180)           # probe body
    sc.cyl((-30, -10, 240), (0, 0, -1), 3, 70, "w", bias=170)             # stylus
    def tip(s_):
        p = s_.P((-30, -10, 168))
        return '<circle class="probeball" cx="%s" cy="%s" r="5"/>' % (n(p[0]), n(p[1]))
    sc.raw(tip, ((-31, -11, 166), (-29, -9, 170)), bias=160)
    sc.box(150, -60, 40, 70, 70, 70, "dk", ch=6, bias=300)                # tool setter
    sc.box(165, -45, 110, 40, 40, 8, "w", bias=290)
    sc.box(-260, 140, 300, 60, 30, 50, "dk", ch=4, bias=100)              # receiver
    sc.note((-30, -10, 270), "タッチプローブ", "主軸に付けて工作物に触れ、位置や寸法を測る")
    sc.note((-30, -10, 168), "スタイラス", "先端の球が触れた瞬間に信号を出す")
    sc.note((-100, -100, 120), "工作物", "加工の前後に測り、座標や補正量を自動で直す")
    sc.note((185, -60, 115), "工具長測定器", "工具の長さや折損を測る")
    sc.note((-230, 140, 340), "受信機", "プローブの信号を無線・光でNCに伝える")


@mt("chip-conveyor", az=-26, el=24)
def _(sc):
    sc.box(-360, -80, 0, 420, 160, 90, "fl", bias=500)
    sc.box(-370, -90, 0, 440, 180, 100, "pt", ch=6, bias=520)             # coolant tank
    sc.box(-360, -80, 90, 420, 160, 4, "fl", bias=480)
    # inclined hinge belt conveyor
    sl = [(-300, 100), (60, 100), (240, 300), (240, 330), (60, 130), (-300, 130)]
    sc.ypr(60, 120, sl, "w", bias=300)
    def hinge(s_):
        o = ""
        for k in range(26):
            x = -290 + k * 20
            z = 130 if x < 60 else 130 + (x - 60) * (200 / 180)
            if x > 240:
                break
            a, b = s_.P((x, -60, z)), s_.P((x, 60, z))
            o += '<path class="tslot" d="M%s %sL%s %s"/>' % (n(a[0]), n(a[1]), n(b[0]), n(b[1]))
        return o
    sc.raw(hinge, ((-290, -60, 130), (240, 60, 330)), bias=290)
    def chips(s_):
        o = ""
        for k in range(26):
            x = -260 + (k * 37) % 480
            z = 132 if x < 60 else 132 + (x - 60) * (200 / 180)
            if x > 230:
                continue
            p = s_.P((x, -40 + (k * 29) % 80, z))
            o += '<path class="chipc" d="M%s %sq4 -6 8 0q4 6 8 0"/>' % (n(p[0]), n(p[1]))
        return o
    sc.raw(chips, ((-260, -40, 132), (230, 40, 330)), bias=280)
    sc.box(220, -90, 0, 160, 180, 160, "dk", ch=8, bias=100)              # chip bucket
    sc.box(-340, -80, 100, 60, 160, 50, "pt", bias=200) if False else None
    sc.axis((-200, -110, 200), (0, -110, 200), "搬送", both=False)
    sc.note((-100, -60, 140), "チップコンベヤ", "ヒンジ板やスクレーパで切りくずを運び出す")
    sc.note((140, 0, 230), "切りくず", "機械の外へ連続して排出する")
    sc.note((-300, -90, 60), "クーラントタンク", "切削油をためて機械に戻す")
    sc.note((300, -90, 120), "回収箱", "切りくずを集めて運び出す")


@mt("fms-cell", az=-30, el=36)
def _(sc):
    for k in range(3):
        sc.box(-380 + k * 250, 100, 0, 210, 200, 230, "pt", ch=10, bias=300)    # HMCs
        sc.box(-335 + k * 250, 30, 0, 120, 70, 60, "pt", ch=4, bias=250)       # pallet changers
        sc.box(-325 + k * 250, 40, 60, 100, 50, 10, "w", bias=240)
    sc.box(-420, -50, 0, 860, 40, 10, "dk", bias=400)                          # rail
    sc.box(-60, -70, 10, 140, 80, 40, "pt", ch=4, bias=200)                    # RGV cart
    sc.box(-40, -60, 50, 100, 60, 10, "w", bias=190)
    sc.box(-420, -260, 0, 420, 150, 150, "pt", ch=6, bias=150)                 # pallet rack (low)
    for k in range(2):
        for j in range(3):
            sc.box(-410 + j * 136, -250, 30 + k * 70, 120, 130, 10, "w", bias=140 - k)
    sc.box(160, -250, 0, 170, 140, 90, "pt", ch=6, bias=150)                   # loading station
    sc.box(185, -230, 90, 120, 100, 10, "w", bias=140)
    sc.box(400, -40, 0, 50, 80, 180, "dk", ch=4, bias=120)                     # cell controller
    sc.note((-275, 100, 230), "工作機械", "同じ機種を並べ、どの機械でも同じ工程を加工できる")
    sc.note((10, -70, 50), "搬送台車（RGV）", "レール上を走り、パレットを運ぶ")
    sc.note((-300, -260, 150), "パレットラック", "治具付きのパレットを多数ためる")
    sc.note((245, -250, 100), "段取りステーション", "人が工作物を付け外しする")
    sc.note((425, -40, 180), "セル制御盤", "加工の順番と搬送を管理する")
