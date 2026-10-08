"""v3 shaded-3D part drawings for the chassis system (suspension arms, knuckle, spring, damper,
stabilizer, subframe, hub bearing, caliper, pad, ABS unit, EPS, tie-rod end).
p:chassis.disc lives in il3_pilot.py. Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P

PI = math.pi


# =====================================================================================
# local helpers (manual painter's order: each returns svg, caller concatenates far -> near)
# =====================================================================================
def _fid(pts):
    return [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(pts)]


def pz(cam, z0, h, xy, mat="w", **kw):
    """(x, y) outline extruded along +z from z0."""
    return compact(GE.prism(cam, (0, 0, z0), (0, 0, 1), [(-p[1], p[0], f) for p, (_, _, f) in zip(xy, _fid(xy))], h, mat, **kw))


def py(cam, y0, h, xz, mat="w", **kw):
    """(x, z) outline extruded from y0 toward the viewer (-y) by h."""
    return compact(GE.prism(cam, (0, y0, 0), (0, -1, 0), _fid(xz), h, mat, **kw))


def px(cam, x0, h, yz, mat="w", **kw):
    """(y, z) outline extruded along +x from x0."""
    return compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), _fid(yz), h, mat, **kw))


def cy(cam, O, A, r, h, mat="w", seg=24, bands=10, r1=None, holes=(), **kw):
    a = GE._norm(A)
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, a, GE.circle_outline(r, seg, bands), h, mat, holes=list(holes),
                            smooth="outer" if holes else True, scale=scale, **kw))


def ring(cam, O, A, ro, ri, h, mat="w", seg=32, **kw):
    a = GE._norm(A)
    return compact(GE.prism(cam, O, a, GE.circle_outline(ro, seg, 10), h, mat, holes=[GE.circle_outline(ri, seg, 6)], smooth=True, **kw))


def disc3(cam, C, A, r, c, seg=None):
    """flat filled circle (face / recess) in 3D."""
    return hole3(cam, C, A, r, c, seg)


def add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def mul(a, k):
    return tuple(v * k for v in a)


def offset(poly, d):
    """outward offset of a closed polygon (either winding) by d (miter, fine for gentle corners)."""
    ar = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    sg = 1 if ar > 0 else -1
    out = []
    N = len(poly)
    for i in range(N):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % N]
        n1 = (sg * (b[1] - a[1]), -sg * (b[0] - a[0]))
        n2 = (sg * (c[1] - b[1]), -sg * (c[0] - b[0]))
        l1, l2 = math.hypot(*n1) or 1, math.hypot(*n2) or 1
        m = (n1[0] / l1 + n2[0] / l2, n1[1] / l1 + n2[1] / l2)
        lm = math.hypot(*m) or 1
        cs = max(0.5, (m[0] / lm) * (n1[0] / l1) + (m[1] / lm) * (n1[1] / l1))
        out.append((b[0] + m[0] / lm * d / cs, b[1] + m[1] / lm * d / cs))
    return out


def tube(cam, pts, r, mat="w", nb=4, cap0=False, cap1=False, dark=0, line=True, uniform=False):
    """round bar / wire swept along a 3D polyline, shaded in nb bands across the visible half.
    One chunk: the caller orders chunks (e.g. half coil turns) far -> near."""
    D = cam.D
    N = len(pts)
    frames = []
    for i in range(N):
        a, b = pts[max(0, i - 1)], pts[min(N - 1, i + 1)]
        T = GE._norm(tuple(b[k] - a[k] for k in range(3)))
        S = GE._cross(T, D)
        if GE._dot(S, S) < 1e-6:
            S = GE._cross(T, (0, 0, 1))
        S = GE._norm(S)
        V = GE._norm(GE._cross(S, T))
        if GE._dot(V, D) > 0:
            V = mul(V, -1)
        frames.append((T, S, V))

    def bp(i, th):
        T, S, V = frames[i]
        t = math.radians(th)
        nrm = tuple(math.cos(t) * V[k] + math.sin(t) * S[k] for k in range(3))
        return cam.xy(add(pts[i], mul(nrm, r))), nrm
    ths = [-90 + 180 * k / nb for k in range(nb + 1)]
    B = [[bp(i, th)[0] for th in ths] for i in range(N)]
    o = ""
    for k in range(nb):
        thm = (ths[k] + ths[k + 1]) / 2
        shs = []
        for i in range(N - 1):
            n1 = bp(i, thm)[1]
            n2 = bp(i + 1, thm)[1]
            shs.append(GE.shade(GE._norm(add(n1, n2)), dark))
        if uniform:
            acc = (0, 0, 0)
            for i in range(N):
                acc = add(acc, bp(i, thm)[1])
            shs = [GE.shade(GE._norm(acc), dark)] * (N - 1)
        i0 = 0
        while i0 < N - 1:
            i1 = i0
            while i1 + 1 < N - 1 and shs[i1 + 1] == shs[i0]:
                i1 += 1
            poly = [B[i][k] for i in range(i0, i1 + 2)] + [B[i][k + 1] for i in range(i1 + 1, i0 - 1, -1)]
            o += path(P(poly), "%ss%d" % (mat, shs[i0]))
            i0 = i1 + 1
    for end, flag in ((0, cap0), (N - 1, cap1)):
        if flag:
            T = frames[end][0]
            if end == 0:
                T = mul(T, -1)
            if GE._dot(T, D) < 0:
                cs = GE.shade(T, dark)
                o += path(P(circ3(cam, pts[end], T, r, 16)), "%ss%d" % (mat, cs) if cs > 2 else (mat if mat != "w" else "w2"))
    if line:
        o += path(P([b[0] for b in B], False) + P([b[-1] for b in B], False), "el")
    return o


def tube_chunks(cam, pts, r, mat="w", split=None, **kw):
    """split a polyline tube where split(i) changes value; returns [(depth, svg)]."""
    out, cur = [], [0]
    for i in range(1, len(pts)):
        cur.append(i)
        if split and i < len(pts) - 1 and split(i) != split(i + 1):
            out.append(cur)
            cur = [i]
    out.append(cur)
    res = []
    for j, idx in enumerate(out):
        seg = [pts[i] for i in idx]
        dep = sum(cam.P(p)[2] for p in seg) / len(seg)
        res.append((dep, tube(cam, seg, r, mat, cap0=(j == 0 and kw.get("caps", False)),
                              cap1=(j == len(out) - 1 and kw.get("caps", False)), dark=kw.get("dark", 0),
                              nb=kw.get("nb", 4), uniform=kw.get("uniform", False))))
    return res


def threads(cam, x0, x1, r, pitch, y=0.0, z=0.0):
    """thread crest lines on the visible side of a rod along x."""
    d = ""
    a0 = math.atan2(-cam.D[2], -cam.D[1])
    k = 0
    x = x0
    while x + pitch * .6 < x1:
        p = []
        for j in range(9):
            t = a0 - PI / 2 + PI * j / 8
            p.append(cam.xy((x + pitch * .6 * j / 8, y + r * math.cos(t), z + r * math.sin(t))))
        d += P(p, False)
        x += pitch
        k += 1
    return path(d, "gr")


def hexagon(r, rot=0):
    return [(r * math.cos(math.radians(rot + 60 * k)), r * math.sin(math.radians(rot + 60 * k))) for k in range(6)]


# =====================================================================================
# chassis.lowerarm — pressed-steel L-arm: two shells welded at a flange (monaka), ball joint at
# the outer end, horizontal front bush and vertical rear (G) bush pressed into welded collars
# =====================================================================================
def lowerarm(az=30, el=30):
    BJ, RB = (-112, -44), (96, 86)
    body = (arc(BJ[0], BJ[1], 23, 95, 265, 8) +
            [(-60, -68), (100, -68), (108, -58), (118, 60)] + arc(RB[0], RB[1], 26, -20, 160, 8) +
            [(70, 64), (44, 14), (10, -14), (-30, -21), (-84, -22)])

    def fn(sc):
        cam = sc.cam
        hole = [(-(6 + v), 76 + u, f) for u, v, f in GE.circle_outline(11, 16, 4)]
        o = pz(cam, 0, 9, body, "w", holes=[hole], dark=.1)
        o += pz(cam, 9, 2.4, offset(body, 3.2), "w", holes=[[(-(6 + v), 76 + u, f) for u, v, f in GE.circle_outline(14, 16, 4)]], dark=.3)
        o += pz(cam, 11.4, 9.6, body, "w", holes=[hole])
        # embossed bead along the main beam
        o += pz(cam, 21, 2.2, [(-82, -50), (60, -52), (66, -46), (60, -40), (-82, -38), (-88, -44)], "w")
        # rear (vertical) bush: collar, rubber with kidney voids, inner sleeve
        cx, cyy = RB
        o += ring(cam, (cx, cyy, -6), (0, 0, 1), 29, 25, 30, "w", seg=36)
        o += disc3(cam, (cx, cyy, 22), (0, 0, 1), 25, "dks2", 32)
        for a0 in (0, 180):
            pts = [cam.xy((cx + r * math.cos(math.radians(a)), cyy + r * math.sin(math.radians(a)), 22.1))
                   for r, a1, a2 in ((21, a0 + 30, a0 + 150), (15, a0 + 150, a0 + 30)) for a in
                   [a1 + (a2 - a1) * j / 8 for j in range(9)]]
            o += path(P(pts), "bg")
        o += ring(cam, (cx, cyy, -8), (0, 0, 1), 11, 7, 33, "w", seg=24)
        # front (horizontal) bush, axis along y
        fx, fz = 114, 10
        o += ring(cam, (fx, -28, fz), (0, -1, 0), 18, 14.5, 52, "w", seg=32)
        o += disc3(cam, (fx, -78, fz), (0, -1, 0), 14.5, "dks2", 28)
        o += cy(cam, (fx, -76, fz), (0, -1, 0), 7.5, 9, "w", seg=20)
        o += disc3(cam, (fx, -85.1, fz), (0, -1, 0), 4.6, "bg", 16)
        # ball joint: housing, boot, tapered stud with thread
        bx, by = BJ
        o += cy(cam, (bx, by, -4), (0, 0, 1), 19, 28, "w", seg=32)
        o += disc3(cam, (bx, by, 24.1), (0, 0, 1), 15, "w3", 28)
        o += cy(cam, (bx, by, 24), (0, 0, 1), 17, 11, "dk", seg=28, r1=10)
        o += cy(cam, (bx, by, 35), (0, 0, 1), 8.5, 20, "w", seg=20, r1=6.8)
        o += cy(cam, (bx, by, 55), (0, 0, 1), 6, 12, "w", seg=20)
        return o
    return fit(fn, az, el, (28, 16, 292, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


@part("chassis.lowerarm")
def _():
    return lowerarm()


# =====================================================================================
# chassis.spring — coil spring lying on its side: closed end turns (pitch = wire dia), open
# working coils, wire ends cut square
# =====================================================================================
def spring(az=22, el=18):
    R, r, Nt, L = 58, 8.5, 6.4, 262
    pe, ne = 2 * r + .6, .9                       # end pitch (closed), turns at each end

    def fn(sc):
        cam = sc.cam
        seg = 26
        Np = int(Nt * seg)
        # pitch profile -> x(t), scaled to the free length L
        ps = []
        for i in range(Np):
            t = (i + .5) / seg
            e = min(t, Nt - t)
            w = 0 if e < ne * .5 else 1 if e > ne else (e - ne * .5) / (ne * .5)
            w = w * w * (3 - 2 * w)
            ps.append(w)
        mid = (L - 2 * r - pe * Nt) / (sum(ps) / seg)
        xs, x = [r], r
        for w in ps:
            x += (pe + w * mid) / seg
            xs.append(x)
        pts = []
        for i in range(Np + 1):
            a = 2 * PI * i / seg + PI * .5
            pts.append((xs[i], R * math.cos(a), R * math.sin(a)))
        D = cam.D

        def front(i):
            return GE._dot((0, pts[i][1], pts[i][2]), D) < 0
        ch = tube_chunks(cam, pts, r, "w", split=front, caps=True, nb=5, uniform=True, dark=.12)
        return "".join(s for _, s in sorted(ch, key=lambda c: -c[0]))
    return fit(fn, az, el, (30, 18, 290, 176), sh_ry=7, sh_k=.46, sh_dy=-4)


@part("chassis.spring")
def _():
    return spring()


# =====================================================================================
# chassis.knuckle — cast steering knuckle (outboard face toward the viewer): machined hub-bearing
# boss with bore and 4 bolt holes; cast arms: strut clamp pad (2 bolt holes) up, ball-joint boss
# down, steering arm with tie-rod taper hole to the rear, two caliper-mount ears to the front
# =====================================================================================
def knuckle(az=32, el=20):
    def fn(sc):
        cam = sc.cam
        C = dict(dark=1, cap_mat="w3", smooth=True)
        o = ""
        # steering arm (rear, +x) and its tie-rod boss
        o += py(cam, 32, 20, banded(hull([(30, 18), (34, -30), (126, -2), (124, -26)] + arc(124, -14, 12, -90, 90, 6)), 2), "w", **C)
        o += cy(cam, (124, 22, -26), (0, 0, 1), 14, 24, "w", seg=24, dark=.6)
        o += disc3(cam, (124, 22, -1.9), (0, 0, 1), 7, "bg", 16)
        # upper arm to the strut clamp pad
        o += py(cam, 30, 20, banded(hull([(-32, 20), (32, 20), (-26, 118), (26, 118)]), 2), "w", **C)
        o += py(cam, 34, 28, banded(hull(arc(0, 132, 30, 0, 180, 10) + [(-30, 102), (30, 102)]), 2), "w", dark=.4, smooth=True)
        for z in (112, 146):
            o += disc3(cam, (0, 5.9, z), (0, -1, 0), 9, "w3", 20) + disc3(cam, (0, 5.8, z), (0, -1, 0), 7, "bg", 18)
        # lower arm and ball-joint boss
        o += py(cam, 30, 22, banded(hull([(-30, -18), (28, -24), (-4, -96), (18, -96)]), 2), "w", **C)
        o += cy(cam, (6, 19, -112), (0, 0, 1), 19, 24, "w", seg=28, dark=.6)
        o += disc3(cam, (6, 19, -87.9), (0, 0, 1), 9, "bg", 18)
        # caliper-mount ears (front, -x)
        for zc in (46, -48):
            o += py(cam, 30, 26, banded(hull(arc(-74, zc, 13, 90, 270, 8) + [(-30, zc * .5 + 14), (-30, zc * .5 - 14)]), 2), "w", **C)
            o += disc3(cam, (-74, 3.9, zc), (0, -1, 0), 6.5, "bg", 16)
        # hub-bearing boss: machined face, bore, 4 bolt holes
        o += ring(cam, (0, 34, 0), (0, -1, 0), 56, 34, 40, "w", seg=48)
        o += disc3(cam, (0, -6.05, 0), (0, -1, 0), 44, "w2", 40)
        o += disc3(cam, (0, -6.1, 0), (0, -1, 0), 34, "bg", 40)
        for k in range(4):
            a = PI / 4 + k * PI / 2
            o += disc3(cam, (49 * math.cos(a), -6.1, 49 * math.sin(a)), (0, -1, 0), 4.2, "bg", 14)
        return o
    return fit(fn, az, el, (40, 12, 280, 180), sh_ry=7, sh_k=.42, sh_dy=-3)


@part("chassis.knuckle")
def _():
    return knuckle()


# =====================================================================================
# chassis.alarm — forged aluminium A-arm: two I-section legs (rims + thin web), bush eyes with
# press-fit rubber bushes at the inner ends, solid apex with a pressed-in ball joint
# =====================================================================================
def alarm(az=30, el=30):
    A = (-112, 0)

    def leg(cam, E, w0, w1):
        dx, dy = E[0] - A[0], E[1] - A[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux

        def q(t, s):
            w = w1 + (w0 - w1) * t
            return (A[0] + ux * L * t + nx * s * w / 2, A[1] + uy * L * t + ny * s * w / 2)

        def strip(s0, s1, t0=.12, t1=.97):
            return [q(t0, s0), q(t1, s0), q(t1, s1), q(t0, s1)]
        o = pz(cam, 8, 9, strip(-1, 1), "w", dark=.7)
        rims = [strip(-1, -.62), strip(.62, 1)]
        rims.sort(key=lambda st: -cam.P((st[0][0], st[0][1], 0))[2])
        for st in rims:
            o += pz(cam, 0, 26, st, "w", dark=.25)
        return o

    def eye(cam, E):
        x, y = E
        o = ring(cam, (x, y + 18, 13), (0, -1, 0), 21, 15, 36, "w", seg=32)
        o += disc3(cam, (x, y - 16, 13), (0, -1, 0), 15, "dks2", 26)
        o += cy(cam, (x, y - 14, 13), (0, -1, 0), 7, 7, "m", seg=18)
        o += disc3(cam, (x, y - 21.1, 13), (0, -1, 0), 4.2, "bg", 14)
        return o

    def fn(sc):
        cam = sc.cam
        Ef, En = (104, 74), (104, -74)
        o = eye(cam, Ef) + leg(cam, (Ef[0] - 2, Ef[1] - 6), 30, 36)
        o += eye(cam, En) + leg(cam, (En[0] - 2, En[1] + 6), 30, 36)
        # solid apex
        o += pz(cam, 0, 26, banded(hull(arc(A[0], A[1], 25, 90, 270, 8) + [(-58, 24), (-58, -24), (-46, 12), (-46, -12)]), 2), "w", dark=.25)
        # ball joint pressed into the apex: housing lip, boot, tapered stud, thread
        o += cy(cam, (A[0], 0, 26), (0, 0, 1), 18, 4, "w", seg=28)
        o += cy(cam, (A[0], 0, 30), (0, 0, 1), 16, 11, "dk", seg=28, r1=9.5)
        o += cy(cam, (A[0], 0, 41), (0, 0, 1), 8, 18, "m", seg=20, r1=6.4)
        o += cy(cam, (A[0], 0, 59), (0, 0, 1), 5.8, 11, "m", seg=18)
        return o
    return fit(fn, az, el, (30, 16, 290, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


@part("chassis.alarm")
def _():
    return alarm()


# =====================================================================================
# chassis.damper — twin-tube shock absorber lying along x: lower eye with rubber bush, outer
# tube, spring seat, rod guide cap, hard-chromed piston rod, bump stopper, upper mount stack
# =====================================================================================
def damper(az=20, el=18):
    def fn(sc):
        cam = sc.cam
        X_ = (1, 0, 0)
        o = ""
        # upper mount (far end, drawn first): thread, nut, washers, rubber cushions
        o += cy(cam, (300, 0, 0), X_, 5.5, 16, "m", seg=16)
        o += threads(cam, 302, 315, 5.5, 3.2)
        o += px(cam, 291, 9, banded(hexagon(11.5, 30), 1), "m", dark=.2)
        o += cy(cam, (288, 0, 0), X_, 22, 3, "w", seg=32)
        o += cy(cam, (276, 0, 0), X_, 18, 12, "dk", seg=28)
        o += cy(cam, (273, 0, 0), X_, 22, 3, "w", seg=32)
        o += cy(cam, (262, 0, 0), X_, 18, 11, "dk", seg=28)
        o += cy(cam, (259, 0, 0), X_, 24, 3, "w", seg=32)
        # rod with bump stopper
        o += cy(cam, (222, 0, 0), X_, 15, 37, "dk", seg=24, r1=12)
        for x in (230, 240, 250):
            o += path(P(circ3(cam, (x, 0, 0), X_, 15 - (x - 222) * 3 / 37, 20)[3:14], False), "gr")
        o += cy(cam, (196, 0, 0), X_, 8.5, 26, "w", seg=20)
        # rod guide / oil seal cap
        o += cy(cam, (190, 0, 0), X_, 15, 6, "w", seg=24)
        o += cy(cam, (182, 0, 0), X_, 24, 8, "w", seg=32, r1=21)
        # outer tube (behind the spring seat), spring seat, outer tube (in front)
        o += cy(cam, (126, 0, 0), X_, 24, 56, "w", seg=32)
        o += cy(cam, (122, 0, 0), X_, 50, 4, "w", seg=48, dark=.1)
        o += cy(cam, (110, 0, 0), X_, 27, 12, "w", seg=32, r1=46)
        o += cy(cam, (28, 0, 0), X_, 24, 82, "w", seg=32)
        o += cy(cam, (14, 0, 0), X_, 15, 14, "w", seg=24, r1=24)
        # lower eye: welded ring, rubber bush, inner sleeve
        o += ring(cam, (0, 19, 0), (0, -1, 0), 18, 13.5, 38, "w", seg=32)
        o += disc3(cam, (0, -17, 0), (0, -1, 0), 13.5, "dks2", 24)
        o += cy(cam, (0, -16, 0), (0, -1, 0), 6.8, 7, "m", seg=16)
        o += disc3(cam, (0, -23.1, 0), (0, -1, 0), 4.2, "bg", 14)
        return o
    return fit(fn, az, el, (24, 30, 296, 170), sh_ry=7, sh_k=.46, sh_dy=-3)


@part("chassis.damper")
def _():
    return damper()


# =====================================================================================
# chassis.stabilizer — U-shaped torsion bar: straight centre with a dog-leg, two rubber bushes
# held by clamp brackets, bent arms ending in flattened eyes for the stabilizer links
# =====================================================================================
def _polyline_fillet(ctrl, rad, seg=8):
    """polyline through 3D control points with circular-ish fillets of radius rad at the corners."""
    out = [ctrl[0]]
    for i in range(1, len(ctrl) - 1):
        a, b, c = ctrl[i - 1], ctrl[i], ctrl[i + 1]
        u = GE._norm(tuple(a[k] - b[k] for k in range(3)))
        v = GE._norm(tuple(c[k] - b[k] for k in range(3)))
        p0, p1 = add(b, mul(u, rad)), add(b, mul(v, rad))
        for j in range(seg + 1):
            t = j / seg
            q = tuple((1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * b[k] + t * t * p1[k] for k in range(3))
            out.append(q)
    out.append(ctrl[-1])
    return out


def _densify(pts, step):
    out = [pts[0]]
    for i in range(1, len(pts)):
        a, b = pts[i - 1], pts[i]
        L = math.dist(a, b)
        k = max(1, int(L / step))
        for j in range(1, k + 1):
            out.append(tuple(a[m] + (b[m] - a[m]) * j / k for m in range(3)))
    return out


def stabilizer(az=22, el=34):
    r = 9

    def fn(sc):
        cam = sc.cam
        ctrl = [(-150, -118, -6), (-150, -40, -6), (-124, 0, 0),
                (124, 0, 0), (150, -40, -6), (150, -118, -6)]
        pts = _densify(_polyline_fillet(ctrl, 22, 6), 14)

        def zone(i):
            x, y = pts[i][0], pts[i][1]
            if y < -30:
                return 0 if x < 0 else 6
            if x < -88:
                return 1
            if x < -62:
                return 2
            if x < 62:
                return 3
            if x < 88:
                return 4
            return 5
        items = tube_chunks(cam, pts, r, "w", split=zone, nb=5, dark=.1, uniform=True)
        for xb in (-75, 75):
            dep = cam.P((xb, 0, 0))[2]
            o = pz(cam, -14, 3, [(xb - 13, -34), (xb + 13, -34), (xb + 13, 34), (xb - 13, 34)], "w", dark=.2)
            o += cy(cam, (xb - 17, 0, 0), (1, 0, 0), 15, 34, "dk", seg=28)
            o += px(cam, xb - 12, 24, banded(hull(arc(0, 0, 18.5, 0, 180, 10) + [(-18.5, -11), (18.5, -11)]), 2), "w", dark=.2)
            for yy in (-26, 26):
                o += disc3(cam, (xb, yy, -10.9), (0, 0, 1), 3.2, "bg", 12)
            items.append((dep - 1, o))
        for xe in (-150, 150):
            dep = cam.P((xe, -120, 0))[2]
            o = pz(cam, -10, 7, banded(hull(arc(xe, -132, 14, 0, 360, 16) + [(xe - 9, -104), (xe + 9, -104)]), 2), "w")
            o += disc3(cam, (xe, -132, -2.9), (0, 0, 1), 6, "bg", 14)
            items.append((dep - 5, o))
        return "".join(s_ for _, s_ in sorted(items, key=lambda c: -c[0]))
    return fit(fn, az, el, (26, 22, 294, 176), sh_ry=7, sh_k=.48, sh_dy=-4)


@part("chassis.stabilizer")
def _():
    return stabilizer()


# =====================================================================================
# chassis.subframe — welded front suspension member: box-section side rails and cross members,
# body-mount collars with rubber at the four corners, paired lower-arm brackets with bolt holes,
# steering-gear mounting pads on the rear cross member, lightening holes
# =====================================================================================
def subframe(az=28, el=30):
    def collar(cam, x, y, z0, toward):
        o = pz(cam, z0 + 10, 16, banded(hull(arc(x, y, 16, 0, 360, 12) + toward), 3), "w", dark=.2)
        o += ring(cam, (x, y, z0 - 4), (0, 0, 1), 15, 11.5, 40, "w", seg=22)
        o += disc3(cam, (x, y, z0 + 32), (0, 0, 1), 11.5, "dks2", 18)
        o += cy(cam, (x, y, z0 + 32), (0, 0, 1), 6.5, 4, "m", seg=14, bands=6)
        o += disc3(cam, (x, y, z0 + 36.1), (0, 0, 1), 4, "bg", 10)
        return o

    def bracket(cam, sd):
        o = ""
        for y in ((-54, -24) if sd > 0 else (-24, -54)):
            o += pz(cam, -6, 38, [(sd * 116, y), (sd * 152, y), (sd * 152, y + 4), (sd * 116, y + 4)], "w", dark=.15)
            o += disc3(cam, (sd * 140, y - .1, 16), (0, -1, 0), 5.5, "bg", 14)
        o += ring(cam, (sd * 134, 16, -8), (0, 0, 1), 15, 10, 38, "w", seg=22)
        o += disc3(cam, (sd * 134, 16, 28), (0, 0, 1), 10, "dks2", 18)
        o += disc3(cam, (sd * 134, 16, 30.1), (0, 0, 1), 4.5, "bg", 12)
        return o

    def side(cam, xs):
        x0, x1 = min(xs * 86, xs * 120), max(xs * 86, xs * 120)
        o = pz(cam, 0, 26, [(x0, -80), (x1, -80), (x1, 10), (x0, 10)], "w", dark=.15)
        o += px(cam, x0, x1 - x0, [(10, 0), (62, 30), (62, 56), (10, 26)], "w", dark=.15)
        o += disc3(cam, (xs * 103, -30, 26.1), (0, 0, 1), 8, "bg", 16)
        return o

    def fn(sc):
        cam = sc.cam
        o = collar(cam, 128, 104, 26, [(108, 84), (120, 84)]) + collar(cam, -128, 104, 26, [(-108, 84), (-120, 84)])
        o += pz(cam, 30, 26, [(-130, 62), (130, 62), (130, 90), (-130, 90)], "w", dark=.15)
        for x in (-56, 56):
            o += pz(cam, 56, 5, banded(hull(arc(x - 12, 76, 9, 90, 270, 6) + arc(x + 12, 76, 9, -90, 90, 6)), 2), "w")
            for dx in (-12, 12):
                o += disc3(cam, (x + dx, 76, 61.1), (0, 0, 1), 4, "bg", 12)
        o += bracket(cam, 1) + side(cam, 1) + side(cam, -1)
        o += pz(cam, 0, 28, [(-134, -96), (134, -96), (134, -62), (-134, -62)], "w", dark=.15)
        for x in (-78, -26, 26, 78):
            o += disc3(cam, (x, -79, 28.1), (0, 0, 1), 9, "bg", 18)
        o += bracket(cam, -1)
        o += collar(cam, 132, -112, 0, [(112, -90), (126, -90)]) + collar(cam, -132, -112, 0, [(-112, -90), (-126, -90)])
        return o
    return fit(fn, az, el, (26, 14, 294, 178), sh_ry=8, sh_k=.5, sh_dy=-6)


@part("chassis.subframe")
def _():
    return subframe()


# =====================================================================================
# chassis.hubbearing — 3rd-generation hub unit, wheel side toward the viewer: lobed hub flange with
# 5 pressed-in wheel studs, pilot spigot with spline bore; outer ring with 4-ear knuckle flange
# and bolt holes; seal, orbital-formed (caulked) inner end with encoder seal
# =====================================================================================
def hubbearing(az=24, el=18):
    def fn(sc):
        cam = sc.cam
        X_ = (1, 0, 0)
        o = cy(cam, (84, 0, 0), X_, 32, 12, "w", seg=32, r1=27)
        o += cy(cam, (80, 0, 0), X_, 42, 4, "dk", seg=36)
        o += cy(cam, (36, 0, 0), X_, 46, 44, "w", seg=40, r1=43)
        holes = [[(u + 60 * math.cos(a), v + 60 * math.sin(a), f) for u, v, f in GE.circle_outline(6, 14, 4)]
                 for a in [PI / 4 + k * PI / 2 for k in range(4)]]
        ear = []
        for k in range(4):
            a = PI / 4 + k * PI / 2
            ear += arc(60 * math.cos(a), 60 * math.sin(a), 15, math.degrees(a) - 90, math.degrees(a) + 90, 6)
        o += compact(GE.prism(cam, (24, 0, 0), X_, banded(hull(ear), 2), 12, "w", holes=holes, smooth="outer", dark=.15))
        o += cy(cam, (14, 0, 0), X_, 44, 10, "w", seg=40)
        o += cy(cam, (19, 0, 0), X_, 45.5, 3, "dk", seg=40)
        lob = []
        for k in range(5):
            a = PI / 2 + 2 * PI * k / 5
            lob += arc(48 * math.cos(a), 48 * math.sin(a), 17, math.degrees(a) - 80, math.degrees(a) + 80, 6)
        o += compact(GE.prism(cam, (0, 0, 0), X_, banded(hull(lob + arc(0, 0, 54, 0, 360, 30)), 2), 14, "w", smooth=True))
        items = []
        items.append((cam.P((-8, 0, 0))[2], cy(cam, (-16, 0, 0), X_, 31, 16, "w", seg=36) +
                      disc3(cam, (-16.1, 0, 0), (-1, 0, 0), 23, "w3", 28) +
                      path(P([cam.xy((-16.2, 15 * math.cos(2 * PI * j / 36 + PI / 36 * (j % 2)) * (1 if j % 2 else 1.18) / 1.18 * 1.18,
                                      15 * math.sin(2 * PI * j / 36) * (1 if j % 2 else 1.18) / 1.18 * 1.18)) for j in range(36)]), "bg")))
        for k in range(5):
            a = PI / 2 + 2 * PI * k / 5
            yy, zz = 48 * math.cos(a), 48 * math.sin(a)
            st = cy(cam, (-34, yy, zz), (1, 0, 0), 6, 34, "m", seg=14, bands=6) + cy(cam, (-37, yy, zz), (1, 0, 0), 4.6, 3, "m", seg=14, r1=6)
            items.append((cam.P((-17, yy, zz))[2], st))
        o += "".join(s_ for _, s_ in sorted(items, key=lambda c: -c[0]))
        return o
    return fit(fn, az, el, (40, 12, 280, 180), sh_ry=7, sh_k=.42, sh_dy=-3)


@part("chassis.hubbearing")
def _():
    return hubbearing()


# =====================================================================================
# chassis.caliper — floating caliper seen from the inboard side: cylinder housing with closed end,
# bridge over the disc with the pad inspection window, guide-pin ears with rubber boots and pin
# bolts, bleeder screw and hose inlet on top of the cylinder
# =====================================================================================
def caliper(az=26, el=24):
    zc = -12

    def pc(r, a):
        return (r * math.cos(math.radians(a)), -150 + r * math.sin(math.radians(a)))

    def fn(sc):
        cam = sc.cam
        o = py(cam, 52, 52, banded(hull([pc(172, a) for a in range(62, 119, 4)] + [pc(126, a) for a in range(66, 115, 6)]), 2), "w",
               smooth=True, dark=.3, cap_mat="w3")
        win = [cam.xy((172.2 * math.cos(math.radians(a)), y, -150 + 172.2 * math.sin(math.radians(a))))
               for a, y in [(a, 14) for a in range(81, 100, 3)] + [(a, 38) for a in range(99, 80, -3)]]
        o += path(P(win), "bg")
        for sd in (-1, 1):
            x = sd * 96
            o += py(cam, 40, 32, banded(hull(arc(x, zc - 4, 15, 0, 360, 14) + [(sd * 66, 6), (sd * 66, -30)]), 2), "w", smooth=True, dark=.3,
                    cap_mat="w3")
            o += cy(cam, (x, 8, zc - 4), (0, -1, 0), 11, 16, "dk", seg=20, r1=8)
            for yy in (2, -3):
                o += path(P(circ3(cam, (x, yy, zc - 4), (0, -1, 0), 11 - (8 - yy) * .19, 18)[4:13], False), "gr")
            o += compact(GE.prism(cam, (x, -8, zc - 4), (0, -1, 0), banded(hexagon(9, 0), 1), 8, "m", dark=.2))
        o += cy(cam, (0, 2, zc), (0, -1, 0), 38, 34, "w", seg=40, dark=.1)
        o += cy(cam, (0, -32, zc), (0, -1, 0), 38, 7, "w", seg=40, r1=31)
        o += disc3(cam, (0, -39.1, zc), (0, -1, 0), 20, "w3", 28)
        # hose inlet boss and bleeder screw on top of the cylinder housing
        o += cy(cam, (-18, -16, zc + 30), (0, 0, 1), 9, 9, "w", seg=18)
        o += disc3(cam, (-18, -16, zc + 39.1), (0, 0, 1), 4.5, "bg", 12)
        Ab = GE._norm((.15, .1, 1))
        b0 = (20, -10, zc + 30)
        o += cy(cam, b0, Ab, 7.5, 8, "w", seg=16)
        o += compact(GE.prism(cam, add(b0, mul(Ab, 8)), Ab, banded(hexagon(6.5, 0), 1), 5, "m"))
        o += cy(cam, add(b0, mul(Ab, 13)), Ab, 3.6, 9, "m", seg=12, bands=6)
        return o
    return fit(fn, az, el, (36, 16, 284, 178), sh_ry=7, sh_k=.46, sh_dy=-4)


@part("chassis.caliper")
def _():
    return caliper()


# =====================================================================================
# chassis.pad — brake pad lying friction-side up: steel backing plate with abutment tabs,
# moulded friction material split by a centre slot, chamfered ends
# =====================================================================================
def pad(az=-20, el=34):
    def pc(r, a):
        return (r * math.cos(math.radians(a)), 150 - r * math.sin(math.radians(a)))

    def fn(sc):
        cam = sc.cam
        o = ""
        main = [pc(170, a) for a in range(60, 121, 4)] + [pc(106, a) for a in range(62, 119, 7)]
        ears = [[pc(r, a) for r in (130, 148) for a in (116, 126)], [pc(r, a) for r in (130, 148) for a in (54, 64)]]
        ears.sort(key=lambda e: -cam.P((e[0][0], e[0][1], 0))[2])
        for e in ears:
            o += pz(cam, 0, 6, hull(e), "w", dark=.35)
        o += pz(cam, 0, 6, banded(hull(main), 2), "w", smooth=True, dark=.35)
        halves = [[pc(163, a) for a in range(92, 115, 2)] + [pc(114, a) for a in (110, 100, 92)] + [pc(150, 115.5), pc(126, 113)],
                  [pc(163, a) for a in range(66, 89, 2)] + [pc(114, a) for a in (70, 80, 88)] + [pc(150, 64.5), pc(126, 67)]]
        halves.sort(key=lambda h: -cam.P((h[0][0], h[0][1], 0))[2])
        for h in halves:
            o += pz(cam, 6, 14, banded(hull(h), 2), "dk", smooth=True)
        return o
    return fit(fn, az, el, (30, 26, 290, 172), sh_ry=7, sh_k=.5, sh_dy=-4)


@part("chassis.pad")
def _():
    return pad()


# =====================================================================================
# chassis.hu — ABS/ESC hydraulic unit: machined aluminium block with brake-line ports on top,
# ball-plugged drillings on the faces, pump motor flanged to the side with its connector
# =====================================================================================
def hu(az=28, el=26):
    def fn(sc):
        cam = sc.cam
        X_ = (1, 0, 0)
        o = cy(cam, (52, 0, 26), X_, 34, 52, "m", seg=36)
        o += cy(cam, (104, 0, 26), X_, 31, 10, "dk", seg=32)
        o += pz(cam, 50, 14, [(108, -10), (118, -10), (118, 10), (108, 10)], "dk")
        o += cy(cam, (48, 0, 26), X_, 38, 6, "m", seg=36)
        o += pz(cam, 0, 76, [(-60, -40), (56, -40), (60, -36), (60, 40), (-56, 40), (-60, 36)], "w", dark=.05)

        def port(c, r):
            return disc3(cam, c, (0, 0, 1), r, "w3", 20) + disc3(cam, c, (0, 0, 1), r * .55, "bg", 14)
        for x, y, r in ((-38, -16, 9.5), (-38, 16, 9.5), (-6, -22, 7.5), (-6, 4, 7.5), (22, -22, 7.5), (22, 4, 7.5)):
            o += port((x, y, 76.1), r)
        for x, z, r in ((-44, 56, 4.5), (-24, 56, 3.5), (-4, 56, 4.5), (16, 56, 3.5), (38, 56, 4.5), (-34, 34, 5.5), (-10, 34, 3.5),
                        (12, 34, 5.5), (36, 34, 3.5), (-44, 14, 3.5), (-20, 14, 4.5), (6, 14, 3.5), (30, 14, 4.5)):
            o += disc3(cam, (x, -40.1, z), (0, -1, 0), r, "w3", 14) + disc3(cam, (x, -40.2, z), (0, -1, 0), r * .55, "w2", 10)
        for y, z, r in ((-20, 52, 4), (8, 52, 5), (24, 30, 3.5), (-14, 22, 5)):
            o += disc3(cam, (-60.1, y, z), (-1, 0, 0), r, "w3", 14)
        return o
    return fit(fn, az, el, (50, 14, 270, 178), sh_ry=7, sh_k=.46, sh_dy=-4)


@part("chassis.hu")
def _():
    return hu()


# =====================================================================================
# chassis.eps — rack-assist electric power steering: aluminium rack housing with a cut-away
# window showing the rack teeth, pinion housing with splined input shaft, ball-screw housing with
# belt case and parallel assist motor + ECU, rubber bellows boots, inner joints, tie rods
# =====================================================================================
def eps(az=18, el=30):
    X_ = (1, 0, 0)

    def boot(cam, x0, x1, rmin=14, rmax=20, nc=3):
        """rubber bellows: alternating frusta (no edge lines, few bands to stay small)."""
        o = ""
        L = (x1 - x0) / (2 * nc)
        for k in range(2 * nc - 1, -1, -1):
            a, b = (rmin, rmax) if k % 2 == 0 else (rmax, rmin)
            o += compact(GE.prism(cam, (x0 + k * L, 0, 0), X_, GE.circle_outline(a, 12, 4), L, "dk", smooth=True,
                                  scale=lambda t, a=a, b=b: 1 + (b / a - 1) * t, lines=k % 2 == 0))
        return o

    def rod(cam, x0, x1, sd):
        """tie rod: threaded outer end with jam nut, plain rod, inner joint housing."""
        o = ""
        if sd > 0:
            o += cy(cam, (x1 - 40, 0, 0), X_, 6.5, 40, "m", seg=14, bands=6)
            o += px(cam, x1 - 50, 10, banded(hexagon(10, 30), 1), "m", dark=.2)
            o += cy(cam, (x0 + 24, 0, 0), X_, 7.5, x1 - 50 - x0 - 24, "m", seg=14, bands=6)
            o += cy(cam, (x0, 0, 0), X_, 11, 24, "m", seg=16, bands=8)
        else:
            o += cy(cam, (x1 - 24, 0, 0), X_, 11, 24, "m", seg=16, bands=8)
            o += cy(cam, (x0 + 50, 0, 0), X_, 7.5, x1 - 24 - x0 - 50, "m", seg=14, bands=6)
            o += px(cam, x0 + 40, 10, banded(hexagon(10, 30), 1), "m", dark=.2)
            o += cy(cam, (x0, 0, 0), X_, 6.5, 40, "m", seg=14, bands=6)
        return o

    def fn(sc):
        cam = sc.cam
        o = ""
        # assist motor behind the rack (parallel), ECU on its end
        my, mz = 58, 6
        o += cy(cam, (-30, my, mz), X_, 25, 118, "m", seg=20, bands=8)
        o += compact(GE.prism(cam, (-56, my, mz), X_, banded(hull(arc(0, 0, 27, 0, 360, 12) + [(-29, 29), (29, 29), (-29, -25), (29, -25)]), 2), 26,
                              "dk", smooth=True))
        o += pz(cam, 22, 10, [(-50, my - 6), (-38, my - 6), (-38, my + 6), (-50, my + 6)], "dk")
        # right side: tie rod, boot, housing tube
        o += rod(cam, 166, 236, 1)
        o += boot(cam, 128, 166)
        o += cy(cam, (96, 0, 0), X_, 18, 32, "alu", seg=20)
        # belt case linking rack axis and motor axis, ball-screw housing
        o += compact(GE.prism(cam, (84, 0, 0), X_, banded(hull(arc(0, 0, 36, 0, 360, 12) + arc(my, mz, 29, 0, 360, 12)), 3), 14, "alu", smooth=True))
        o += cy(cam, (30, 0, 0), X_, 33, 54, "alu", seg=24)
        o += cy(cam, (22, 0, 0), X_, 26, 8, "alu", seg=20, r1=33)
        # rack housing tube (in front of the window)
        o += ring(cam, (-40, 0, 0), X_, 22, 16, 62, "alu", seg=20)
        # cut-away window: interior back wall, rack with teeth
        x0, x1 = -104, -40
        tv = math.atan2(cam.se, -cam.ca * cam.ce)
        back = [cam.xy((x0, 16 * math.cos(tv + PI / 2 + PI * j / 10), 16 * math.sin(tv + PI / 2 + PI * j / 10))) for j in range(11)]
        back += [cam.xy((x1, 16 * math.cos(tv + PI / 2 + PI * j / 10), 16 * math.sin(tv + PI / 2 + PI * j / 10))) for j in range(10, -1, -1)]
        o += path(P(back), "alus4")
        o += cy(cam, (x0, 0, 0), X_, 11, x1 - x0, "m", seg=18, bands=8)
        for k in range(9, -1, -1):
            x = x0 + 3 + k * 6.2
            o += py(cam, 8, 16, [(x, 6), (x + 4.6, 6), (x + 3.4, 11.5), (x + 1.2, 11.5)], "m", lines=False)
        rim = [cam.xy((x, 22 * math.cos(tv + PI / 2), 22 * math.sin(tv + PI / 2))) for x in (x0, x1)]
        rim2 = [cam.xy((x, 16 * math.cos(tv + PI / 2), 16 * math.sin(tv + PI / 2))) for x in (x1, x0)]
        o += path(P(rim + rim2), "cut")
        # pinion housing with the tilted input shaft (spline)
        o += cy(cam, (-150, 0, 0), X_, 22, 46, "alu", seg=20)
        Ap = GE._norm((.15, .45, 1))
        pc0 = (-128, 0, 0)
        o += cy(cam, pc0, Ap, 25, 38, "alu", seg=22)
        o += cy(cam, add(pc0, mul(Ap, 38)), Ap, 13, 7, "dk", seg=18)
        o += cy(cam, add(pc0, mul(Ap, 45)), Ap, 9, 28, "m", seg=16, bands=8)
        sp = ""
        E1, E2, _ = GE.frame(Ap)
        for j in range(12):
            t = 2 * PI * j / 12
            nrm = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
            if GE._dot(nrm, cam.D) < -.1:
                a = add(add(pc0, mul(Ap, 58)), mul(nrm, 9.1))
                sp += P([cam.xy(a), cam.xy(add(a, mul(Ap, 14)))], False)
        o += path(sp, "gr")
        # left side: boot, tie rod
        o += boot(cam, -188, -150)
        o += rod(cam, -258, -188, -1)
        return o
    return fit(fn, az, el, (14, 24, 306, 172), sh_ry=6, sh_k=.44, sh_dy=-3)


@part("chassis.eps")
def _():
    return eps()


# =====================================================================================
# chassis.balljoint — outer tie-rod end and tie rod: forged housing with rubber boot and
# cold-headed tapered ball stud (thread on top), neck with threaded shank, jam nut, tie rod
# with adjusting thread, inner (axial) ball-joint housing
# =====================================================================================
def balljoint(az=22, el=22):
    X_ = (1, 0, 0)

    def fn(sc):
        cam = sc.cam
        o = cy(cam, (250, 0, 0), X_, 17, 34, "w", seg=28)
        o += px(cam, 236, 14, banded(hexagon(14.5, 30), 1), "w", dark=.2)
        o += cy(cam, (128, 0, 0), X_, 8.5, 108, "w", seg=18, bands=8)
        o += cy(cam, (80, 0, 0), X_, 8, 48, "w", seg=18, bands=8) + threads(cam, 82, 126, 8, 3.6)
        o += px(cam, 70, 11, banded(hexagon(14, 30), 1), "w", dark=.2)
        o += cy(cam, (40, 0, 0), X_, 13, 30, "w", seg=24)
        o += px(cam, 10, 32, banded(hull(arc(0, 0, 13, 0, 360, 12) + [(-9, 15), (9, 15), (-9, -15), (9, -15)]), 2), "w",
                smooth=True, dark=.4, cap_mat="w3", scale=lambda t: 1 - .15 * t)
        # housing with boot and ball stud
        o += cy(cam, (0, 0, -16), (0, 0, 1), 22, 30, "w", seg=32, dark=.2)
        o += cy(cam, (0, 0, 14), (0, 0, 1), 22.5, 3, "w", seg=32)
        o += cy(cam, (0, 0, 17), (0, 0, 1), 20, 8, "dk", seg=28, r1=17)
        o += cy(cam, (0, 0, 25), (0, 0, 1), 17, 6, "dk", seg=28, r1=10.5)
        o += cy(cam, (0, 0, 31), (0, 0, 1), 9.5, 24, "w", seg=20, r1=7.6)
        o += cy(cam, (0, 0, 55), (0, 0, 1), 6.6, 16, "w", seg=18, bands=8)
        d = ""
        a0 = math.atan2(-cam.D[1], -cam.D[0])
        for z in range(57, 70, 3):
            d += P([cam.xy((6.6 * math.cos(a0 + t), 6.6 * math.sin(a0 + t), z + t * .4)) for t in [(-1.4 + 2.8 * j / 8) for j in range(9)]], False)
        o += path(d, "gr")
        return o
    return fit(fn, az, el, (28, 22, 292, 176), sh_ry=7, sh_k=.46, sh_dy=-4)


@part("chassis.balljoint")
def _():
    return balljoint()
