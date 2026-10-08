"""v3 shaded-3D part drawings: drivetrain (gears, shafts, cases, CVT, converter, CVJ) and body parts
(hot stamped pillar, high-tensile member, Al hood, giga casting, plastic fuel tank).
Overrides the older flat drawings in il_parts.py with the same keys."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P

PI = math.pi


# =====================================================================================
# helpers: free-form quad meshes (sheet metal, swept sections), depth-sorted with edge lines
# =====================================================================================
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def quad_item(cam, q, mat, two_sided=False, dark=0, ln_edges=(), cls=None):
    """q: list of world points (planar-ish polygon). Returns (depth, cls, d, ln) or None if back-facing.
    ln_edges: indices i of edges q[i]->q[i+1] to stroke as crease / outline lines."""
    nrm = GE._norm(GE._cross(_sub(q[1], q[0]), _sub(q[-1], q[0])))
    if len(q) > 3:
        n2 = GE._norm(GE._cross(_sub(q[2], q[1]), _sub(q[0], q[1])))
        nrm = GE._norm((nrm[0] + n2[0], nrm[1] + n2[1], nrm[2] + n2[2]))
    back = GE._dot(nrm, cam.D) > 0
    if back:
        if not two_sided:
            return None
        nrm = (-nrm[0], -nrm[1], -nrm[2])
    pp = [cam.P(p) for p in q]
    dep = sum(p[2] for p in pp) / len(pp)
    sh = min(4, GE.shade(nrm, dark) + (1 if back and two_sided else 0))
    c = cls or "%ss%d" % (mat, sh)
    ln = "".join("M%s %sL%s %s" % (n(pp[i][0]), n(pp[i][1]), n(pp[(i + 1) % len(pp)][0]), n(pp[(i + 1) % len(pp)][1])) for i in ln_edges)
    return (dep, c, "M" + " L".join(n(x) + " " + n(y) for x, y, _ in pp) + "Z", ln)


def render_q(items):
    """paint far -> near; consecutive line-less fills of one class are merged into a single path."""
    items = [it for it in items if it]
    items.sort(key=lambda it: -it[0])
    o, cur, buf = "", None, ""
    for _, c, d, ln in items:
        if c != cur and buf:
            o += '<path class="%s" d="%s"/>' % (cur, buf)
            buf = ""
        cur = c
        buf += d
        if ln:
            o += '<path class="%s" d="%s"/><path class="el" d="%s"/>' % (c, buf, ln)
            buf = ""
    if buf:
        o += '<path class="%s" d="%s"/>' % (cur, buf)
    return o


def gsvg(svg):
    return compact(svg)


# =====================================================================================
# drivetrain.gear — helical transmission gear: tooth rim, recessed web, hub with spline bore
# =====================================================================================
def clip_poly(subj, clip):
    """Sutherland-Hodgman: convex clip polygon (screen points, CCW or CW consistent)."""
    def side(a, b, p):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    sg = 1 if sum(side(clip[i], clip[(i + 1) % len(clip)], clip[(i + 2) % len(clip)]) for i in range(len(clip))) > 0 else -1
    out = subj
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            sp, sq = side(a, b, p) * sg, side(a, b, q) * sg
            if sp >= 0:
                out.append(p)
            if (sp >= 0) != (sq >= 0):
                t = sp / (sp - sq)
                out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        if not out:
            break
    return out


def tm_gear(az=-28, el=36):
    z, rp, h, hx, rb = 32, 96, 40, 21, 72
    zw = 24                                     # web top level

    def fn(sc):
        cam = sc.cam
        o = GE.gear3(cam, (0, 0, 0), (0, 0, 1), z, rp, h, "w", helix=hx, bore=rb, slices=2)
        # recessed web seen through the rim opening (web disc clipped to the rim's top bore)
        web = clip_poly(circ3(cam, (0, 0, zw), (0, 0, 1), rb, 48), circ3(cam, (0, 0, h), (0, 0, 1), rb, 48))
        o += path(P(web), "w")
        o += GE.prism(cam, (0, 0, zw), (0, 0, 1), GE.circle_outline(44, 40, 10), h + 6 - zw, "w", holes=[GE.spline_outline(20, 30, 26.5)],
                      smooth=True)
        o += path(P(circ3(cam, (0, 0, h + 6.05), (0, 0, 1), 40, 40)), "gr")
        o += path(P(circ3(cam, (0, 0, zw + .05), (0, 0, 1), 60, 40)), "gr")
        return gsvg(o)
    return fit(fn, az, el, (40, 12, 280, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


@part("drivetrain.gear")
def _():
    return tm_gear()


# =====================================================================================
# drivetrain.hypoid — spiral-bevel ring gear lying flat; drive pinion on a long stem meshing on
# the face below the ring centre line (hypoid offset)
# =====================================================================================
def ring_lite(cam, O, r_in, r_out, h, z, mat="w", spiral=.6, nholes=10):
    """lean spiral-bevel ring gear, axis vertical, teeth as curved ridges on the top face (after GE.bevel_ring)."""
    o = compact(GE.prism(cam, O, (0, 0, 1), GE.circle_outline(r_out, 64, 16), h, mat, caps=False, smooth=True))
    tz = O[2] + h
    dep = (r_out - r_in) * .16
    bo = r_in * .62
    ring = lambda r, zz, k=56: [cam.xy((O[0] + r * math.cos(2 * PI * q / k), O[1] + r * math.sin(2 * PI * q / k), zz)) for q in range(k)]
    o += '<path class="%ss3" fill-rule="evenodd" d="%s%s"/>' % (mat, P(ring(r_out, tz)), P(ring(r_in, tz)[::-1]))
    o += '<path class="%s" fill-rule="evenodd" d="%s%s"/>' % (mat, P(ring(r_in, tz)), P(ring(bo, tz)[::-1]))
    rh = (r_in + bo) / 2
    for k in range(nholes):
        a = 2 * PI * (k + .5) / nholes
        o += hole3(cam, (O[0] + rh * math.cos(a), O[1] + rh * math.sin(a), tz + .05), (0, 0, 1), 4.4, "bg", 12)
    step = 2 * PI / z
    nr = 3
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
            nrm = GE._norm(GE._cross(_sub(top[-1], top[0]), _sub(top[1], bot[1])))
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
    return o + render_q(items)


def hypoid(az=24, el=34, th=-28):
    def fn(sc):
        cam = sc.cam
        o = ring_lite(cam, (0, 0, -16), 70, 118, 26, 37, "w")
        tz = -16 + 26 + (118 - 70) * .16
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        rot_ = lambda x, y, z: (x * c - y * s_, x * s_ + y * c, z)
        A = GE._norm(rot_(-1, 0, -.3))
        O = rot_(134, -30, tz + 37)
        B = (-A[0], -A[1], -A[2])
        stem = ""
        for L, r, x0 in ((16, 12, 92), (72, 16, 20), (20, 22, 0)):
            stem += gsvg(GE.cyl(cam, tuple(O[i] + B[i] * x0 for i in range(3)), B, r, L, "w", seg=24))
        head = GE.prism(cam, O, A, GE.gear_outline(11, 34, phase=.1), 50, "w", twist=.75, slices=4,
                        scale=lambda t: 1 - .38 * t)
        return o + stem + gsvg(head)
    return fit(fn, az, el, (30, 14, 290, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


@part("drivetrain.hypoid")
def _():
    return hypoid()


# =====================================================================================
# drivetrain.shaft — counter shaft: rolled spline, bearing journals, two integral helical gears,
# snap-ring groove, centre hole in the end face
# =====================================================================================
def tm_shaft(az=20, el=20):
    def fn(sc):
        cam = sc.cam
        A = (1, 0, 0)
        x = 0.0
        segs = [("spl", 36, 15), ("c", 3, 12.5), ("c", 22, 18), ("c", 7, 24), ("g", 36, (19, 34, 24)),
                ("c", 48, 20), ("g", 28, (13, 23, -26)), ("c", 46, 17), ("c", 14, 12)]
        for kind, L, r in segs:
            if kind == "spl":
                svg = GE.prism(cam, (x, 0, 0), A, GE.spline_outline(18, r, r - 2.3), L, "w")
                sc.add(compact(svg), ((x, -r, -r), (x + L, r, r)))
            elif kind == "g":
                zz, rp, hx = r
                svg = GE.gear3(cam, (x, 0, 0), A, zz, rp, L, "w", helix=hx, slices=3 if zz > 15 else 2)
                ra = rp * (1 + 2.0 / zz)
                sc.add(compact(svg), ((x, -ra, -ra), (x + L, ra, ra)))
            else:
                CYL(sc, (x, 0, 0), A, r, L, "w", seg=24 if r > 16 else 20, bands=8, dark=2 if L <= 3 else 0)
            x += L

        def face(s_):
            return hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 4.5, "w3") + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 2.6, "bg")
        RAW(sc, face, ((-.2, -15, -15), (0, 15, 15)), -2)

        def oil(s_):
            return hole3(s_.cam, (128, -20 * .6, -20 * .8), (0, -.6, -.8), 2.4)
        RAW(sc, oil, ((106, -20, -20), (150, 20, 20)), -1)
    return fit(fn, az, el, (22, 30, 298, 170), sh_ry=7, sh_k=.46)


@part("drivetrain.shaft")
def _():
    return tm_shaft()


# =====================================================================================
# drivetrain.tmcase — die-cast transaxle case (ADC12): converter bell with bolt flange, pear-shaped
# outline reaching down to the differential lobe; inside: bulkhead with input/pump boss and the
# differential bearing bore; the narrower gear case continues to the rear; outer ribs
# =====================================================================================
def _pear(k=1.0, off=0.0):
    pts = arc(0, 8, (100 + off) * k, 0, 360, 22) + arc(-58 * k, -70 * k, (52 + off) * k, 0, 360, 14)
    return banded(hull(pts), 2)


def case_svg(cam, inside=None, before=None, phs=(60, 95, 130, 165)):
    """case axis along +y (bell face toward the viewer at y=0); outline coords (u, v) -> world (-u, y, v)."""
    sk = .74
    Ay = (0, 1, 0)
    W = lambda t, u, v: (-u, t, v)
    if True:
        sc_ = lambda t: 1 - (1 - sk) * t
        o = before(cam) if before else ""
        o += compact(GE.prism(cam, (0, 70, 0), Ay, [(u * .72, v * .72 - 4, f) for u, v, f in _pear()], 104, "w", smooth=True,
                              scale=lambda t: 1 - .1 * t, dark=1))
        for vv, uu in ((76, 0), (62, 40)):                  # ribs on the rear case
            o += compact(GE.prism(cam, (0, 70, 0), Ay, [(uu - 2, vv - 6, 0), (uu + 2, vv - 6, 1), (uu + 2, vv + 6, 2), (uu - 2, vv + 6, 3)],
                                  96, "w", scale=lambda t: 1 - .1 * t, dark=1))
        o += compact(GE.prism(cam, (10, 130, 70), (0, 0, 1), GE.circle_outline(12, 20, 6), 12, "w", smooth=True, dark=.5))
        cav = _pear(1, -12)
        o += path(P([cam.xy(W(70, u * sk, v * sk)) for u, v, f in cav]), "w3")
        for (u, v, r, rb_) in ((0, 14, 30, 17), (-28, 58, 18, 11), (-58, -70, 34, 25)):
            o += compact(GE.prism(cam, W(70, u * sk, v * sk), (0, -1, 0), GE.circle_outline(r, 24, 8), 10, "w", smooth=True,
                                  holes=[GE.circle_outline(rb_, 20, 20)]))
        o += compact(GE.prism(cam, (0, 10, 0), Ay, _pear(.97), 60, "w", holes=[cav], caps=False, smooth=True, scale=sc_, dark=1.2))
        o += compact(GE.prism(cam, (0, 10, 0), Ay, _pear(.97), 60, "w", caps=False, smooth=True, scale=sc_, dark=.6))
        fins = []
        for ph in phs:
            c, s_ = math.cos(math.radians(ph)), math.sin(math.radians(ph))
            vc = 8 * .97
            loop = [(r * c - q * 2 * s_, vc + r * s_ + q * 2 * c, i) for i, (r, q) in enumerate(((92, -1), (106, -1), (106, 1), (92, 1)))]
            dep = cam.P(W(40, 100 * c, 100 * s_))[2]
            fins.append((dep, compact(GE.prism(cam, (0, 10, 0), Ay, loop, 60, "w", scale=sc_, dark=.6))))
        o += "".join(f for _, f in sorted(fins, key=lambda f: -f[0]))
        if inside:
            o += inside(cam)
        o += compact(GE.prism(cam, (0, 0, 0), Ay, _pear(1.0, 8), 10, "w", holes=[cav], smooth="outer"))
        pts = _pear(1.0, 1)
        for k in range(14):
            u, v, _ = pts[int(k * len(pts) / 14)]
            o += hole3(cam, W(-.1, u, v), (0, -1, 0), 3.2, "bg", 10)
        return o


def tm_case(az=30, el=24):
    return fit(lambda sc: case_svg(sc.cam), az, el, (34, 12, 286, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("drivetrain.tmcase")
def _():
    return tm_case()


# =====================================================================================
# drivetrain.valvebody — AT valve body (die-cast Al): maze of oil channels on the mating face,
# spool-valve bores in a row along the side face (spool ends / plugs), bolt holes
# =====================================================================================
MAZE = [[(14, 22), (60, 22), (60, 44), (104, 44), (104, 20), (150, 20)],
        [(14, 58), (40, 58), (40, 78), (86, 78), (86, 62), (128, 62), (128, 40), (176, 40), (176, 22), (206, 22)],
        [(18, 104), (64, 104), (64, 92), (112, 92), (112, 112), (160, 112), (160, 84), (204, 84)],
        [(150, 62), (196, 62), (196, 112)], [(30, 120), (30, 92)], [(140, 20), (140, 6)]]


def valve_body(az=-26, el=38):
    W, D, H, d = 220, 130, 34, 5

    def fn(sc):
        BOX(sc, 0, 0, 0, W, D, H, "w", ch=3)

        def marks(s_):
            cam = s_.cam
            ops, fls = "", ""
            for pl in MAZE:
                for (x0, y0), (x1, y1) in zip(pl, pl[1:]):
                    a, b = (min(x0, x1) - 3.5, min(y0, y1) - 3.5), (max(x0, x1) + 3.5, max(y0, y1) + 3.5)
                    rect_ = [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])]
                    op = [cam.xy((x, y, H + .05)) for x, y in rect_]
                    fl = [cam.xy((x, y, H - d)) for x, y in rect_]
                    ops += P(op)
                    c = clip_poly(fl, op)
                    if len(c) > 2:
                        fls += P(c)
            o = path(ops, "ws2") + path(fls, "w3")
            for x, y in ((8, 8), (W - 8, 8), (W - 8, D - 8), (8, D - 8), (110, 70), (60, 120), (190, 100)):
                o += hole3(cam, (x, y, H + .05), (0, 0, 1), 3.4, "bg", 12)
            for x, y in ((80, 26), (150, 100), (46, 86)):
                o += hole3(cam, (x, y, H + .05), (0, 0, 1), 4.6, "w3", 14)
            # spool bores on the -y face: bore, spool land, retainer plugs
            for i, x in enumerate(range(24, W - 10, 30)):
                c = (x, -.05, H * .48)
                o += hole3(cam, c, (0, -1, 0), 9, "w3", 18) + hole3(cam, c, (0, -1, 0), 7.4, "bg", 16)
                if i % 3 != 1:
                    o += hole3(cam, (x, -.06, H * .48), (0, -1, 0), 5.6, "w", 14)
            return o
        RAW(sc, marks, ((0, -.2, 0), (W, D, H + .2)), -2)
    return fit(fn, az, el, (30, 14, 290, 178), sh_ry=8, sh_k=.52, sh_dy=-4)


@part("drivetrain.valvebody")
def _():
    return valve_body()


# =====================================================================================
# drivetrain.cvtpulley — CVT primary pulley: fixed sheave integral with the shaft, movable sheave
# (conical face toward the belt groove) backed by the hydraulic piston drum; splined shaft ends
# =====================================================================================
def cvt_pulley(az=16, el=24, R=82):
    def fn(sc):
        A = (1, 0, 0)
        x = 0.0
        tc = math.tan(math.radians(15))
        segs = [("spl", 28, 13), ("c", 20, 17), ("c", 5, R), ("k", (R - 22) * tc, (R, 22)), ("c", 14, 21),
                ("k", (R - 22) * tc, (22, R)), ("c", 6, R), ("c", 4, 64), ("c", 28, 70), ("c", 6, 58), ("c", 22, 17), ("c", 16, 12)]
        for kind, L, r in segs:
            if kind == "spl":
                sc.add(compact(GE.prism(sc.cam, (x, 0, 0), A, GE.spline_outline(16, r, r - 2), L, "w")), ((x, -r, -r), (x + L, r, r)))
            elif kind == "k":
                CYL(sc, (x, 0, 0), A, r[0], L, "w", seg=56, bands=14, r1=r[1])
            else:
                CYL(sc, (x, 0, 0), A, r, L, "w", seg=56 if r > 40 else 22, bands=14 if r > 40 else 8, dark=.4 if r in (64, 70, 58) else 0)
            x += L

        def face(s_):
            cam = s_.cam
            o = hole3(cam, (-.1, 0, 0), (-1, 0, 0), 4.5, "w3") + hole3(cam, (-.1, 0, 0), (-1, 0, 0), 2.6, "bg")
            o += path(P(circ3(cam, (47.9, 0, 0), (-1, 0, 0), R - 8, 48)) + P(circ3(cam, (47.9, 0, 0), (-1, 0, 0), 30, 32)), "gr")
            return o
        RAW(sc, face, ((-.2, -15, -15), (0, 15, 15)), -2)
    return fit(fn, az, el, (40, 12, 280, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("drivetrain.cvtpulley")
def _():
    return cvt_pulley()


# =====================================================================================
# drivetrain.cvtbelt — push belt: several hundred V-flanked steel elements threaded on two packs of
# thin maraging-steel rings; shown running over a large and a small pulley radius (loop in x-z plane)
# =====================================================================================
def belt_path(a, r1, r2, d1=8):
    """open-belt loop around circles (-a,0) r1 and (a,0) r2 in the x-z plane: [(x, z, nx, nz)] CCW."""
    be = math.asin((r1 - r2) / (2 * a))
    pts = []
    t0, t1 = -(PI / 2 - be), PI / 2 - be
    k = max(2, int((t1 - t0) / math.radians(d1)))
    pts += [(a + r2 * math.cos(t0 + (t1 - t0) * i / k), r2 * math.sin(t0 + (t1 - t0) * i / k), math.cos(t0 + (t1 - t0) * i / k),
             math.sin(t0 + (t1 - t0) * i / k)) for i in range(k + 1)]
    t0, t1 = PI / 2 - be, 3 * PI / 2 + be
    k = max(2, int((t1 - t0) / math.radians(d1)))
    pts += [(-a + r1 * math.cos(t0 + (t1 - t0) * i / k), r1 * math.sin(t0 + (t1 - t0) * i / k), math.cos(t0 + (t1 - t0) * i / k),
             math.sin(t0 + (t1 - t0) * i / k)) for i in range(k + 1)]
    return pts


def sweep(cam, loop, sec, mat, dark=0, edges=False, skip=()):
    """sweep a closed (a, b) section (a = outward along the loop normal, b = lateral y) around a closed loop."""
    ar = sum(sec[i][0] * sec[(i + 1) % len(sec)][1] - sec[(i + 1) % len(sec)][0] * sec[i][1] for i in range(len(sec)))
    sg = 1 if ar > 0 else -1
    W = lambda p, a, b: (p[0] + a * p[2], b, p[1] + a * p[3])
    items = []
    N = len(loop)
    for j in range(len(sec)):
        if j in skip:
            continue
        (a0, b0), (a1, b1) = sec[j], sec[(j + 1) % len(sec)]
        la = math.hypot(a1 - a0, b1 - b0)
        na, nb = sg * (b1 - b0) / la, -sg * (a1 - a0) / la
        for i in range(N):
            p, q = loop[i], loop[(i + 1) % N]
            if abs(p[0] - q[0]) + abs(p[1] - q[1]) < 1e-6:
                continue
            mx, mz = (p[2] + q[2]) / 2, (p[3] + q[3]) / 2
            nrm = GE._norm((na * mx, nb, na * mz))
            if GE._dot(nrm, cam.D) > -1e-3:
                continue
            pts = [cam.P(W(p, a0, b0)), cam.P(W(q, a0, b0)), cam.P(W(q, a1, b1)), cam.P(W(p, a1, b1))]
            ln = ""
            if edges:
                ln = "M%s %sL%s %sM%s %sL%s %s" % (n(pts[0][0]), n(pts[0][1]), n(pts[1][0]), n(pts[1][1]),
                                                   n(pts[2][0]), n(pts[2][1]), n(pts[3][0]), n(pts[3][1]))
            items.append((sum(t[2] for t in pts) / 4, "%ss%d" % (mat, min(4, GE.shade(nrm, dark))),
                          "M" + " L".join(n(x) + " " + n(y) for x, y, _ in pts) + "Z", ln))
    return items


def cvt_belt(az=-24, el=26):
    a, r1, r2 = 76, 56, 34
    body = [(-7, -11), (-7, 11), (3, 15), (3, -15)]
    rl = [(3, -15), (3, -8), (6.5, -8), (6.5, -15)]
    rr = [(3, 8), (3, 15), (6.5, 15), (6.5, 8)]
    head = [(6.5, -8), (6.5, 8), (11, 8), (11, -8)]

    def fn(sc):
        cam = sc.cam
        lp = belt_path(a, r1, r2, 12)
        items = sweep(cam, lp, body, "w", skip=(2,)) + sweep(cam, lp, head, "w", skip=(0,)) + \
            sweep(cam, lp, rl, "w", dark=-.2, skip=(0,)) + sweep(cam, lp, rr, "w", dark=-.2, skip=(0,))
        o = render_q(items)
        W = lambda p, aa, b: (p[0] + aa * p[2], b, p[1] + aa * p[3])
        o += path("".join(P([cam.xy(W(m, aa, b)) for m in lp]) for aa, b in ((-7, -11), (3, -15), (6.5, -15))), "el")
        # element joints on the near flank, ring-layer lines on the near ring pack
        W = lambda p, aa, b: (p[0] + aa * p[2], b, p[1] + aa * p[3])
        L = sum(math.hypot(lp[i][0] - lp[i - 1][0], lp[i][1] - lp[i - 1][1]) for i in range(1, len(lp)))
        ne, d, acc = 130, "", 0.0
        step = L / ne
        for i in range(1, len(lp) + 1):
            p, q = lp[i - 1], lp[i % len(lp)]
            seg = math.hypot(q[0] - p[0], q[1] - p[1])
            while acc < seg:
                t = acc / seg
                m = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t, p[3] + (q[3] - p[3]) * t)
                u0, u1 = cam.xy(W(m, -7, -11)), cam.xy(W(m, 3, -15))
                d += "M%s %sL%s %s" % (n(u0[0]), n(u0[1]), n(u1[0]), n(u1[1]))
                acc += step
            acc -= seg
        o += path(d, "gr")
        ll = ""
        for aa in (3.9, 4.8, 5.7):
            ll += P([cam.xy(W(m, aa, -15.02)) for m in lp])
        o += path(ll, "gr")
        return o
    return fit(fn, az, el, (26, 22, 294, 174), sh_ry=8, sh_k=.56, sh_dy=-4)


@part("drivetrain.cvtbelt")
def _():
    return cvt_belt()


# =====================================================================================
# drivetrain.torqueconv — torque converter: pressed front cover with welded drive lugs and pilot
# boss, full-circumference seal weld bead, toroidal impeller shell, hub sleeve with drive notches
# =====================================================================================
def torque_conv(az=36, el=18):
    prof = [(-70, 100), (-66, 112), (-58, 119), (-48, 123), (-44, 125.5), (-40, 123.5), (-26, 121), (-10, 108),
            (4, 88), (12, 62), (16, 30)]

    def fn(sc):
        A = (0, 1, 0)
        for (y0, r0), (y1, r1) in zip(prof, prof[1:]):
            dk = 1.6 if r0 > 124 or r1 > 124 else 0
            CYL(sc, (0, y0, 0), A, r0, y1 - y0, "w", seg=56, bands=14, r1=r1, dark=dk, caps=False if y0 > -70 else True)
        CYL(sc, (0, 16, 0), A, 28, 40, "w", seg=32, bands=10)
        CYL(sc, (0, -70, 0), (0, -1, 0), 22, 9, "w", seg=32, bands=10, bias=-1)
        CYL(sc, (0, -79, 0), (0, -1, 0), 15, 5, "w", seg=28, bands=8, bias=-2)
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            x, z = 86 * math.cos(t), 86 * math.sin(t)
            hexo = [(x + 9 * math.cos(t + PI / 6 + j * PI / 3), z + 9 * math.sin(t + PI / 6 + j * PI / 3), j) for j in range(6)]
            sc.add(compact(GE.prism(sc.cam, (0, -70, 0), (0, -1, 0), [(-u, v, f) for u, v, f in hexo], 8, "w")),
                   ((x - 9, -78, z - 9), (x + 9, -70, z + 9)), -1)

        RAW(sc, lambda s_: path(P(circ3(s_.cam, (0, -70.1, 0), (0, -1, 0), 62, 48)) + P(circ3(s_.cam, (0, -70.1, 0), (0, -1, 0), 40, 40)), "gr"),
            ((-70, -70.2, -70), (70, -70.1, 70)), -.5)
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            c = (86 * math.cos(t), -78.1, 86 * math.sin(t))
            RAW(sc, lambda s_, c=c: hole3(s_.cam, c, (0, -1, 0), 4.2, "bg", 12), ((c[0] - 9, -78.3, c[2] - 9), (c[0] + 9, -78.2, c[2] + 9)), -2)
    return fit(fn, az, el, (50, 10, 270, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("drivetrain.torqueconv")
def _():
    return torque_conv()


# =====================================================================================
# drivetrain.diffcase — ductile-iron differential case: ring-gear flange with bolt holes, rounded
# body with a side window (machined spherical inside), pinion-shaft boss, bearing journals
# =====================================================================================
def _interp(prof, x):
    for (x0, r0), (x1, r1) in zip(prof, prof[1:]):
        if x0 <= x <= x1:
            return r0 + (r1 - r0) * (x - x0) / (x1 - x0)
    return prof[-1][1]


def diff_case(az=30, el=22):
    body = [(44, 64), (52, 69), (66, 72), (84, 72), (100, 68), (114, 58), (124, 46), (130, 32)]

    def fn(sc):
        A = (1, 0, 0)
        CYL(sc, (0, 0, 0), A, 22, 26, "w", seg=28, bands=8)
        CYL(sc, (26, 0, 0), A, 27, 6, "w", seg=32, bands=8, dark=.5)
        CYL(sc, (32, 0, 0), A, 94, 12, "w", seg=64, bands=16, dark=.4)
        for (x0, r0), (x1, r1) in zip(body, body[1:]):
            CYL(sc, (x0, 0, 0), A, r0, x1 - x0, "w", seg=48, bands=14, r1=r1, dark=.5, caps=x0 == 44)
        CYL(sc, (130, 0, 0), A, 24, 8, "w", seg=28, bands=8, dark=.5)
        CYL(sc, (138, 0, 0), A, 22, 26, "w", seg=28, bands=8)
        CYL(sc, (164, 0, 0), A, 17, 8, "w", seg=24, bands=8)
        CYL(sc, (86, 0, 66), (0, 0, 1), 15, 10, "w", seg=24, bands=8, dark=.3, bias=-1)

        def marks(s_):
            cam = s_.cam
            o = hole3(cam, (-.1, 0, 0), (-1, 0, 0), 15, "w3", 20) + hole3(cam, (-.1, 0, 0), (-1, 0, 0), 11, "bg", 18)
            for k in range(12):
                t = 2 * PI * (k + .5) / 12
                o += hole3(cam, (31.9, 80 * math.cos(t), 80 * math.sin(t)), (-1, 0, 0), 4.2, "bg", 12)
            return o

        def window(s_):
            cam = s_.cam
            o = ""
            # side window toward the viewer: dark opening, lit crescent of the machined spherical inside
            win, inn = [], []
            for k in range(36):
                t = 2 * PI * k / 36
                u, v = math.cos(t), math.sin(t)
                u, v = math.copysign(abs(u) ** .6, u), math.copysign(abs(v) ** .6, v)
                x = 90 + 16 * u
                th = math.radians(162 + 30 * v)
                r = _interp(body, x) + .3
                win.append(cam.xy((x, r * math.cos(th), r * math.sin(th))))
                th2 = math.radians(162 + 26 * v)
                inn.append(cam.xy((90 + 14 * u + 4, (r - 14) * math.cos(th2) + 6, (r - 14) * math.sin(th2))))
            o += path(P(win), "bg") + path(P(clip_poly(inn, win)), "w3")
            return o
        RAW(sc, lambda s_: hole3(s_.cam, (86, 0, 76.1), (0, 0, 1), 8.5, "bg", 16), ((76, -10, 76), (96, 10, 76.2)), -2)
        RAW(sc, marks, ((-.2, -95, -95), (32, 95, 95)), -2)
        RAW(sc, window, ((72, -73, 10), (108, -60, 40)), -2)
    return fit(fn, az, el, (30, 12, 290, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("drivetrain.diffcase")
def _():
    return diff_case()


# =====================================================================================
# drivetrain.cvj — drive shaft: inboard tripod-joint housing with rubber boot, bar shaft, outboard
# ball-type CVJ shown without its boot: outer race mouth with cage, inner race and six balls,
# splined stub with threaded end. Coaxial along x, drawn far (+x) to near.
# =====================================================================================
def cy(cam, x, r, L, mat="w", r1=None, seg=32, bands=10, dark=0, caps=True, A=(1, 0, 0), O=None):
    sc_ = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O or (x, 0, 0), A, GE.circle_outline(r, seg, bands), L, mat, smooth=True, scale=sc_, dark=dark, caps=caps))


def cvj(az=24, el=20):
    def fn(sc):
        cam = sc.cam
        o = ""
        # outboard stub (far end first)
        o += cy(cam, 356, 10, 16, seg=20, bands=8)
        o += compact(GE.prism(cam, (330, 0, 0), (1, 0, 0), GE.spline_outline(12, 15, 13), 26, "w"))
        o += cy(cam, 314, 19, 16, seg=24, bands=8)
        # outer race (bell), mouth toward -x
        for x0, r0, x1, r1 in ((302, 44, 314, 26), (278, 49, 302, 44), (262, 46, 278, 49)):
            o += cy(cam, x0, r0, x1 - x0, r1=r1, seg=36, bands=12, dark=.3, caps=x0 == 262)
        m = 261.9
        o += hole3(cam, (m, 0, 0), (-1, 0, 0), 37, "bg", 40)
        o += path(P(circ3(cam, (m, 0, 0), (-1, 0, 0), 46, 48)), "gr")
        o += hole3(cam, (m + 6, 0, 0), (-1, 0, 0), 34, "w3", 40) + hole3(cam, (m + 6, 0, 0), (-1, 0, 0), 30, "bg", 36)
        o += hole3(cam, (m + 2, 0, 0), (-1, 0, 0), 22, "w2", 32)
        balls = []
        for k in range(6):
            t = 2 * PI * (k + .5) / 6
            c = (m + 3, 30 * math.cos(t), 30 * math.sin(t))
            bx, by = cam.xy(c)
            r = 8.2 * cam.s
            balls.append((cam.P(c)[2], '<circle class="ball" cx="%s" cy="%s" r="%s"/>' % (n(bx), n(by), n(r)) +
                          '<circle class="w" cx="%s" cy="%s" r="%s" opacity=".7"/>' % (n(bx - r * .3), n(by - r * .35), n(r * .3))))
        o += "".join(b for _, b in sorted(balls, key=lambda b: -b[0]))
        # bar shaft, then the inboard boot (convolutions), tripod housing, splined stem
        o += cy(cam, 140, 11, 128, seg=20, bands=8)
        bel = [(92, 33), (101, 36), (110, 27), (119, 30), (128, 21), (136, 23), (146, 13)]
        for (x0, r0), (x1, r1) in reversed(list(zip(bel, bel[1:]))):
            o += cy(cam, x0, r0, x1 - x0, "dk", r1=r1, seg=24, bands=8, caps=False)
        o += cy(cam, 88, 37, 4, "dk", seg=32, bands=10, dark=-.4)
        o += cy(cam, 46, 38, 42, seg=36, bands=12, dark=.2)
        o += cy(cam, 38, 18, 8, r1=38, seg=32, bands=10)
        o += cy(cam, 26, 17, 12, seg=24, bands=8)
        o += compact(GE.prism(cam, (0, 0, 0), (1, 0, 0), GE.spline_outline(12, 14, 12), 26, "w"))
        o += hole3(cam, (-.1, 0, 0), (-1, 0, 0), 3.4, "bg", 12)
        return o
    return fit(fn, az, el, (20, 34, 300, 168), sh_ry=7, sh_k=.46)


@part("drivetrain.cvj")
def _():
    return cvj()


# =====================================================================================
# drivetrain.tmassy — assembled transaxle on the test-stand pallet: torque converter seated in the
# bell, output shaft coupled to the absorbing dynamometer side, locating blocks on the pallet
# =====================================================================================
def tm_assy(az=30, el=24):
    def inside(cam):
        o = cy(cam, 0, 76, 19, seg=36, bands=10, A=(0, -1, 0), O=(0, 33, 10), dark=.2)
        o += cy(cam, 0, 16, 7, seg=24, bands=8, A=(0, -1, 0), O=(0, 11, 10))
        o += path(P(circ3(cam, (0, 10.9, 10), (0, -1, 0), 50, 40)), "gr")
        for k in range(4):
            t = 2 * PI * (k + .25) / 4
            o += hole3(cam, (62 * math.cos(t), 10.9, 10 + 62 * math.sin(t)), (0, -1, 0), 5, "w3", 12)
        return o

    def fn(sc):
        cam = sc.cam
        o = ""
        # pallet and locating blocks (behind/below the case)
        BOX_ = lambda x, y, z, sx, sy, sz, mat, dk=0: compact(GE.prism(cam, (0, 0, z), (0, 0, 1),
                                                                        [(-yy, xx, i) for i, (xx, yy) in enumerate(((x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)))],
                                                                        sz, mat, dark=dk))
        o += BOX_(-118, -14, -166, 250, 200, 18, "m", 1)
        o += BOX_(20, 120, -148, 60, 40, 18, "dk") + BOX_(-80, 120, -148, 50, 40, 18, "dk")
        # output shaft -> coupling -> dyno shaft (right side, far)
        o += cy(cam, 0, 16, 40, "m", seg=24, bands=8, O=(166, 110, -54), dark=.5)
        o += cy(cam, 0, 34, 12, "m", seg=36, bands=10, O=(154, 110, -54))
        o += cy(cam, 0, 13, 78, seg=20, bands=8, O=(76, 110, -54))
        o += BOX_(-60, 6, -148, 80, 30, 18, "dk")
        o += case_svg(cam, inside, phs=(80, 130))
        return o
    return fit(fn, az, el, (30, 10, 290, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("drivetrain.tmassy")
def _():
    return tm_assy()


# =====================================================================================
# body parts — sheet metal as quad strips between stations (each station = one cross-section)
# =====================================================================================
def strips(cam, st, mat, crease=(), dark=0, two_sided=False, faces=None, dk=None):
    """st: list of stations, each a list of world points (same count). Quad between point j..j+1 of
    consecutive stations. crease: point indices whose lines along the length are stroked.
    dk(i, j) -> extra darkness for a quad (beads, recesses)."""
    items = []
    for i in range(len(st) - 1):
        A_, B_ = st[i], st[i + 1]
        for j in range(len(A_) - 1):
            if faces is not None and j not in faces:
                continue
            q = [A_[j], B_[j], B_[j + 1], A_[j + 1]]
            le = []
            if j in crease:
                le.append(0)
            if j + 1 in crease:
                le.append(2)
            items.append(quad_item(cam, q, mat, two_sided, dark + (dk(i, j) if dk else 0), le))
    return items


def end_cap(cam, sec, mat="w", cls=None):
    return path(P([cam.xy(p) for p in sec]), cls or mat)


def hat(w, H, F, draft=14, flange=True):
    W = w + 2 * H * math.tan(math.radians(draft))
    pts = [(-W / 2, 0), (-w / 2, H), (w / 2, H), (W / 2, 0)]
    if flange:
        pts = [(-W / 2 - F, 0)] + pts + [(W / 2 + F, 0)]
    return pts


# body.hotstamp — B-pillar (hot stamped): hat section lying on its side, T-shaped roof-rail joint at
# one end, flared rocker joint at the other, gentle bow, flanges all round, holes and a bead
def b_pillar(az=34, el=40):
    L, N = 300, 26

    def prof(t):
        """width of the top face, wall height, flange width, z-bow; t in 0..1 along the pillar (0 = roof end)."""
        w = 40 + 64 * (1 - _smooth(0, .16, t)) + 50 * _smooth(.66, 1, t)
        H = 24 - 8 * t
        F = 9 + 10 * (1 - _smooth(0, .12, t)) + 8 * _smooth(.8, 1, t)
        z = 20 * math.sin(PI * t)
        return w, H, F, z

    def fn(sc):
        cam = sc.cam
        st = []
        for i in range(N + 1):
            t = i / N
            t = t ** 1.15
            w, H, F, z = prof(t)
            x = L * t
            hs = hat(w, H, F)
            bw, bh = w * .22, 5 * _smooth(.08, .2, t) * (1 - _smooth(.8, .92, t))
            sec = hs[:3] + [(-bw - 3, H), (-bw, H + bh), (bw, H + bh), (bw + 3, H)] + hs[3:]
            st.append([(x, y, z + zz) for y, zz in sec])
        o = render_q(strips(cam, st, "w", crease=tuple(range(10)), dk=lambda i, j: (.1, .45, 0, .2, .05, .5, 0, .45, .1)[j]))
        o += end_cap(cam, [(p[0] - .01, p[1], p[2] - 1.6) for p in st[0]][::-1] + st[0], "w", "w3")
        marks = ""
        for t, r in ((.3, 6), (.46, 8), (.62, 6)):
            w, H, F, z = prof(t)
            marks += hole3(cam, (L * t, 0, z + H + 5.05), (0, 0, 1), r, "bg", 16)
        w, H, F, z = prof(.9)
        marks += hole3(cam, (L * .9, -34, z + H + .05), (0, 0, 1), 8, "bg", 18) + hole3(cam, (L * .9, 34, z + H + .05), (0, 0, 1), 5, "bg", 12)
        w, H, F, z = prof(.03)
        marks += hole3(cam, (L * .03, -40, z + H + .05), (0, 0, 1), 4, "bg", 12) + hole3(cam, (L * .03, 40, z + H + .05), (0, 0, 1), 4, "bg", 12)
        return o + marks
    return fit(fn, az, el, (24, 30, 296, 172), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("body.hotstamp")
def _():
    return b_pillar()


# body.hitenmember — front side member (cold-stamped high-tensile): hat section closed by a flat plate,
# spot-weld flanges on both sides, kick-up toward the dash, crush beads near the front, open front end
def _smooth(a, b, t):
    u = min(1, max(0, (t - a) / (b - a)))
    return u * u * (3 - 2 * u)


def side_member(az=24, el=28):
    L, N, w, H, F, d = 320, 32, 42, 46, 13, 8
    beads = {3: (1, 2, 3), 5: (2,), 7: (1, 2, 3)}

    def fn(sc):
        cam = sc.cam
        st, pl = [], []
        for i in range(N + 1):
            t = i / N
            x, z, y = L * t, 40 * _smooth(.45, .78, t), 22 * _smooth(.55, .95, t)
            st.append([(x, y + yy, z + zz) for yy, zz in hat(w, H, F, d)])
            W2 = st[-1][-1][1] - y
            pl.append([(x, y - W2, z), (x, y - W2, z - 2.4)])
        dk = lambda i, j: (.7 if i in beads and j in beads[i] else 0) + (.12, .42, 0, .42, .12)[j]
        items = strips(cam, st, "w", crease=(0, 1, 2, 3, 4, 5), dk=dk) + strips(cam, pl, "w", dark=.4)
        o = render_q(items)
        # open front end: dark interior of the closed box section, sheet edges
        sec = st[0]
        o += path(P([cam.xy(p) for p in sec[1:5]]), "bg")
        o += path(P([cam.xy(p) for p in sec], False) + P([cam.xy(pl[0][0]), cam.xy((0, -pl[0][0][1], -2.4))], False), "el")
        for t, zz, r in ((.22, .5, 7), (.36, .45, 9), (.88, .5, 6)):
            x, z, y = L * t, 40 * _smooth(.45, .78, t), 22 * _smooth(.55, .95, t)
            Wb = (w + 2 * H * math.tan(math.radians(d))) / 2
            yw = -Wb + (Wb - w / 2) * zz
            o += hole3(cam, (x, y + yw - .3, z + H * zz), (0, -.97, .24), r, "bg", 16)
        return o
    return fit(fn, az, el, (22, 26, 298, 174), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("body.hitenmember")
def _():
    return side_member()


# body.alhood — aluminium hood outer panel: crowned, doubly curved skin rising toward the windscreen,
# two character lines, hemmed edge turned down all round
def al_hood(az=-30, el=38):
    nx, ny = 18, 10
    Wf, Wr, Lh = 250, 300, 190

    def surf(u, v):
        """u -1..1 across, v 0 (front) .. 1 (rear)"""
        half = (Wf + (Wr - Wf) * v) / 2
        x = u * half
        y = -Lh / 2 + Lh * v - 10 * (1 - u * u) * (1 - v)      # front edge bows forward in the middle
        z = 30 * v + 34 * (1 - u * u) * (.75 + .25 * v) - 16 * (1 - v) ** 3
        for c in (-.42, .42):                                    # character lines (soft ridge)
            z += 3.2 * max(0, 1 - abs(u - c) / .08)
        return (x, y, z)

    def fn(sc):
        cam = sc.cam
        us = sorted(set([-1 + 2 * i / nx for i in range(nx + 1)] + [c + e for c in (-.42, .42) for e in (-.08, 0, .08)]))
        st = [[surf(u, v / ny) for v in range(ny + 1)] for u in us]
        cre = {}
        items = strips(cam, st, "w", crease=(), dark=.06)
        # hem: edge turned down 7 units along front and both sides
        hem = []
        rim = [surf(-1, v / ny) for v in range(ny, -1, -1)] + [surf(u, 0) for u in us[1:]] + [surf(1, v / ny) for v in range(1, ny + 1)]
        for p in rim:
            hem.append([(p[0], p[1], p[2] - 7), p])
        items += strips(cam, hem, "w", dark=.3)
        o = render_q(items)
        o += path(P([cam.xy(p) for p in rim], False), "el")
        for c in (-.42, .42):
            o += path(P([cam.xy(surf(c, v / ny)) for v in range(ny + 1)], False), "gr")
        return o
    return fit(fn, az, el, (30, 18, 290, 176), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("body.alhood")
def _():
    return al_hood()


# body.gigacast — one-piece rear underbody casting (seen from the ribbed side): floor web, deep side
# rails, rear cross wall, shock towers, diagonal rib lattice with bosses at the nodes
def giga_cast(az=-30, el=42):
    def fn(sc):
        cam = sc.cam
        out = [(-150, -100), (-112, -128), (112, -128), (150, -100), (150, 110), (-150, 110)]
        o = compact(GE.prism(cam, (0, 0, -8), (0, 0, 1), [(-y, x, i) for i, (x, y) in enumerate(out)], 8, "w", dark=.2))
        parts = []

        def wall(p0, p1, h, t, mat="w", dk=.1, z0=0):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy)
            nx_, ny_ = -dy / L * t / 2, dx / L * t / 2
            q = [(p0[0] + nx_, p0[1] + ny_), (p1[0] + nx_, p1[1] + ny_), (p1[0] - nx_, p1[1] - ny_), (p0[0] - nx_, p0[1] - ny_)]
            ar = sum(q[i][0] * q[(i + 1) % 4][1] - q[(i + 1) % 4][0] * q[i][1] for i in range(4))
            if ar < 0:
                q = q[::-1]
            its = [quad_item(cam, [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z0 + h), (a[0], a[1], z0 + h)], mat, dark=dk)
                   for a, b in zip(q, q[1:] + q[:1])]
            its.append(quad_item(cam, [(a[0], a[1], z0 + h) for a in q], mat, dark=dk, ln_edges=(0, 2) if t < 8 else (0, 1, 2, 3)))
            c = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, h / 2)
            parts.append((cam.P(c)[2], render_q(its)))

        def boss(x, y, r, h, hole=0, dk=0):
            svg = cy(cam, 0, r, h, seg=16 if r < 10 else 32, bands=6 if r < 10 else 10, A=(0, 0, 1), O=(x, y, 0), dark=dk)
            if hole:
                svg += hole3(cam, (x, y, h + .05), (0, 0, 1), hole, "bg", 12 if r < 10 else 24)
            parts.append((cam.P((x, y, h / 2))[2] - .5, svg))
        # rails along both sides (split for ordering), rear wall, front lip
        for xs in (-139, 139):
            wall((xs, -100), (xs, 110), 46, 22, dk=.25)
        wall((-128, 104), (128, 104), 40, 10)
        for a, b in (((-150, -100), (-112, -128)), ((-112, -128), (112, -128)), ((112, -128), (150, -100))):
            wall(a, b, 16, 4)
        # rib lattice
        xs, ys = [-96, -48, 0, 48, 96], [-84, -8, 68]
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                if i + 1 < len(xs):
                    wall((x, y), (xs[i + 1], y), 20, 3)
                if j + 1 < len(ys):
                    wall((x, y), (x, ys[j + 1]), 20, 3)
                if i + 1 < len(xs) and j + 1 < len(ys):
                    if (i + j) % 2:
                        wall((x, y), (xs[i + 1], ys[j + 1]), 16, 3)
                    else:
                        wall((xs[i + 1], y), (x, ys[j + 1]), 16, 3)
                boss(x, y, 6.5, 26, 2.8 if (i + j) % 2 == 0 else 0)
        for x in (-110, 110):
            boss(x, 74, 24, 66, 15, .1)
        o += "".join(p_ for _, p_ in sorted(parts, key=lambda p_: -p_[0]))
        return o
    return fit(fn, az, el, (26, 10, 294, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("body.gigacast")
def _():
    return giga_cast()


# body.fueltank — blow-moulded multilayer HDPE tank: saddle section straddling the tunnel, pinch-off
# flange along the parting line, strap grooves, pump-module lock ring and lid, filler pipe
def fuel_tank(az=46, el=30):
    L, zp, tp = 150, 44, 2.6

    def rnd(cx, cy_, r, a0, a1, k=4):
        return arc(cx, cy_, r, a0, a1, k)
    low = [(-110, zp)] + rnd(-100, 10, 10, 180, 270) + [(-44, 0)] + rnd(-44, 6, 6, 270, 360, 3)[1:] + [(-32, 30)] + \
        rnd(-22, 32, 10, 180, 90, 3) + rnd(22, 32, 10, 90, 0, 3) + [(32, 30)] + rnd(36, 6, 6, 180, 270, 3)[1:] + [(100, 0)] + rnd(100, 10, 10, 270, 360) + [(110, zp)]
    up = [(110, zp + tp)] + rnd(92, 62, 18, 0, 90, 5) + rnd(-92, 62, 18, 90, 180, 5) + [(-110, zp + tp)]

    def fn(sc):
        X(sc, 0, L, low, "w", smooth=True)
        BOX(sc, -5, -115, zp, L + 10, 230, tp, "w", dark=.6)
        X(sc, 0, L, up, "w", smooth=True)
        CYL(sc, (84, 46, 80), (0, 0, 1), 32, 4, "dk", seg=40, bands=10)
        CYL(sc, (84, 46, 84), (0, 0, 1), 25, 8, "dk", seg=36, bands=10, dark=-.3)
        CYL(sc, (84, 46, 92), (0, 0, 1), 9, 7, "dk", seg=20, bands=6, dark=-.3)

        def top(s_):
            cam = s_.cam
            o = ""
            for yg in (-60, ):                     # strap groove along the top
                o += path(P([cam.xy((x, yg + dy, 80.05)) for x, dy in ((4, -6), (L - 4, -6), (L - 4, 6), (4, 6))]), "ws3")
            for k in range(8):
                t = 2 * PI * k / 8
                o += hole3(cam, (84 + 28.5 * math.cos(t), 46 + 28.5 * math.sin(t), 84.1), (0, 0, 1), 1.5, "bg", 8)
            return o
        RAW(sc, top, ((0, -110, 80), (L, 110, 80.1)), -1)
        # filler pipe leaving the left side, rising outward
        d = GE._norm((.2, -.75, .62))
        o0 = (100, -104, 58)
        CYL(sc, o0, d, 12, 60, "w", seg=24, bands=8, bias=-2)
        CYL(sc, tuple(o0[i] + d[i] * 60 for i in range(3)), d, 16, 10, "w", seg=24, bands=8, bias=-3)
    return fit(fn, az, el, (30, 14, 290, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("body.fueltank")
def _():
    return fuel_tank()
