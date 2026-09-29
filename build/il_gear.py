"""Gear geometry + a small orthographic 3D renderer for technical illustrations.

 - involute tooth outlines (external / internal), racks
 - prism(): extrudes an outline (with optional helical twist and holes) and renders
   it with back-face culling, painter's sort and 4-step lambert shading.
 - hob(): 2.5D side view of a gashed hob / threaded grinding worm.
Shading classes: <mat> for the lit cap, <mat>s1..s4 for side faces (light→dark).
"""
import math
from il_base import n

PI = math.pi
ALPHA = 20 * PI / 180


def inv(a):
    return math.tan(a) - a


# ------------------------------------------------------------------ 2D outlines
def gear_outline(z, rp, ra=None, rf=None, phase=0.0, nf=3, fillet=True):
    """External involute gear outline, CCW, list of (u, v, fid).
    rp pitch radius, ra tip radius, rf root radius. Teeth centred at phase + i*2pi/z."""
    m = 2.0 * rp / z
    ra = rp + m if ra is None else ra
    rf = rp - 1.25 * m if rf is None else rf
    rb = rp * math.cos(ALPHA)
    psi = PI / (2 * z) + inv(ALPHA)

    def half(r):
        if r <= rb:
            return psi
        return psi - inv(math.acos(rb / r))

    # keep a small top land
    while half(ra) < 0.18 * PI / z and ra > rp:
        ra -= 0.02 * m
    rs = max(rf + 0.28 * (ra - rf), min(rb, rp - 0.2 * m)) if fillet else rf
    rs = min(rs, rp - 0.15 * m)
    step = 2 * PI / z
    pts = []
    flank_r = [rs + (ra - rs) * (k / nf) ** 0.85 for k in range(nf + 1)]
    for i in range(z):
        c = phase + i * step
        base = i * 4
        # rising flank (lower angle side)
        for k, r in enumerate(flank_r[:-1]):
            a = c - half(r)
            pts.append((r * math.cos(a), r * math.sin(a), base))
        # tip land
        ht = half(ra)
        for k in range(2):
            a = c - ht + 2 * ht * k / 2
            pts.append((ra * math.cos(a), ra * math.sin(a), base + 1))
        # falling flank
        for r in flank_r[::-1][:-1]:
            a = c + half(r)
            pts.append((r * math.cos(a), r * math.sin(a), base + 2))
        # fillet + root to next tooth
        a0 = c + half(rs)
        a1 = c + step - half(rs)
        gap = a1 - a0
        d = min(gap * 0.32, 0.55 * m / max(rf, 1))
        if fillet:
            # quadratic fillet from (rs,a0) to (rf,a0+d) with control (rf,a0)
            for tt in (0.0, 0.55):
                r = (1 - tt) ** 2 * rs + 2 * (1 - tt) * tt * rf + tt * tt * rf
                a = (1 - tt) ** 2 * a0 + 2 * (1 - tt) * tt * a0 + tt * tt * (a0 + d)
                pts.append((r * math.cos(a), r * math.sin(a), base + 3))
            for tt in (0.0,):
                a = a0 + d + (gap - 2 * d) * tt
                pts.append((rf * math.cos(a), rf * math.sin(a), base + 3))
            for tt in (1.0, 0.55):
                r = (1 - tt) ** 2 * rs + 2 * (1 - tt) * tt * rf + tt * tt * rf
                a = (1 - tt) ** 2 * a1 + 2 * (1 - tt) * tt * a1 + tt * tt * (a1 - d)
                pts.append((r * math.cos(a), r * math.sin(a), base + 3))
        else:
            pts.append((rf * math.cos(a0), rf * math.sin(a0), base + 3))
            pts.append((rf * math.cos(a1), rf * math.sin(a1), base + 3))
    return pts


def internal_outline(z, rp, phase=0.0, nf=3):
    """Void boundary of an internal gear (teeth point inward). Returned CCW."""
    m = 2.0 * rp / z
    return gear_outline(z, rp, rp + 1.25 * m, rp - 0.9 * m, phase + PI / z, nf, fillet=False)


def circle_outline(r, seg=48, feat=6, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(2 * PI * k / seg), cy + r * math.sin(2 * PI * k / seg), k * feat // seg) for k in range(seg)]


def spline_outline(z, r_out, r_in, phase=0.0, duty=0.5):
    """Straight-sided / short involute spline (external)."""
    step = 2 * PI / z
    pts = []
    for i in range(z):
        c = phase + i * step
        hw_o = step * duty * 0.42
        hw_i = step * duty * 0.5
        for a, r, f in ((c - hw_i, r_in, 0), (c - hw_o, r_out, 1), (c + hw_o, r_out, 2), (c + hw_i, r_in, 3)):
            pts.append((r * math.cos(a), r * math.sin(a), i * 4 + f))
    return pts


def rotate_outline(pts, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [(u * c - v * s, u * s + v * c, f) for u, v, f in pts]


def outline_d(pts, cx, cy, sy=1.0, close=True):
    d = "M" + " L".join(n(cx + u) + " " + n(cy + v * sy) for u, v, *_ in pts)
    return d + ("Z" if close else "")


def rack_pts(x0, x1, y, m, up=True, phase=0.0):
    """Rack profile polyline along x (screen). Teeth point up (y decreasing) if up."""
    p = PI * m
    ha, hf = m, 1.25 * m
    t = math.tan(ALPHA)
    sg = -1 if up else 1
    pts = []
    k = math.floor((x0 - phase) / p) - 1
    while True:
        xc = phase + k * p  # tooth centre
        # tooth: root-left, tip-left, tip-right, root-right
        seq = [(xc - p / 4 - hf * t, y - sg * hf * 0), (xc - p / 4 + ha * t, y + sg * ha), (xc + p / 4 - ha * t, y + sg * ha),
               (xc + p / 4 + hf * t, y)]
        # measure relative to pitch line y: root at y - sg*hf? keep pitch line = y
        seq = [(xc - p / 4 - hf * t, y - sg * hf), (xc - p / 4 + ha * t, y + sg * ha), (xc + p / 4 - ha * t, y + sg * ha),
               (xc + p / 4 + hf * t, y - sg * hf)]
        pts += seq
        if xc - p / 2 > x1:
            break
        k += 1
    # clip x to [x0, x1]
    out = []
    for i in range(len(pts)):
        xx, yy = pts[i]
        if x0 <= xx <= x1:
            out.append((xx, yy))
    return out


# ------------------------------------------------------------------ 3D
def _v(a, b, s=1.0):
    return (a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    l = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


LIGHT = _norm((-0.5, -0.45, 0.75))


def frame(A):
    """orthonormal E1, E2 with E1 x E2 = A"""
    A = _norm(A)
    ref = (0, 0, 1) if abs(A[2]) < 0.9 else (1, 0, 0)
    E1 = _norm(_cross(ref, A))
    E2 = _cross(A, E1)
    return E1, E2, A


class Cam:
    """orthographic camera. world: x right, y away from viewer, z up. az rotates about z, el tilts down."""

    def __init__(self, ox, oy, az=0.0, el=25.0, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s
        a, e = math.radians(az), math.radians(el)
        self.ca, self.sa, self.ce, self.se = math.cos(a), math.sin(a), math.cos(e), math.sin(e)
        self.D = (self.ce * self.sa, self.ce * self.ca, -self.se)

    def P(self, p):
        x, y, z = p
        x1 = x * self.ca - y * self.sa
        y1 = x * self.sa + y * self.ca
        return (self.ox + self.s * x1, self.oy - self.s * (y1 * self.se + z * self.ce), y1 * self.ce - z * self.se)

    def xy(self, p):
        q = self.P(p)
        return q[0], q[1]


def shade(nrm, dark=0.0):
    i = _dot(nrm, LIGHT) - dark
    if i > 0.55:
        return 1
    if i > 0.2:
        return 2
    if i > -0.2:
        return 3
    return 4


def _pd(ps):
    return "M" + " L".join(n(x) + " " + n(y) for x, y, *_ in ps)


def _area(loop):
    a = 0.0
    for i in range(len(loop)):
        u1, v1 = loop[i][0], loop[i][1]
        u2, v2 = loop[(i + 1) % len(loop)][0], loop[(i + 1) % len(loop)][1]
        a += u1 * v2 - u2 * v1
    return a / 2


def prism(cam, O, A, outline, h, mat="w", holes=(), twist=0.0, slices=1, cap_mat=None, lines=True, caps=True,
          collect=None, hl=None, fid_mat=None, smooth=False, scale=None, bands=False, dark=0, grooves=0):
    """Extrude `outline` (list of (u,v,fid) in plane E1,E2 at O) by h along A.
    twist: rotation (rad) of the outline over the full height (helical teeth).
    Returns svg. If collect is a list, side strips are appended there (for joint sorting) and only caps are returned.
    hl: optional svg class to overlay the visible cap outline (e.g. machined-surface highlight).
    fid_mat: optional function fid -> material override for side strips."""
    E1, E2, A = frame(A)
    loops = [(outline, False)] + [(hh, True) for hh in holes]
    items = []

    def world(u, v, t):
        return (O[0] + u * E1[0] + v * E2[0] + t * h * A[0],
                O[1] + u * E1[1] + v * E2[1] + t * h * A[1],
                O[2] + u * E1[2] + v * E2[2] + t * h * A[2])

    def at(loop, t):
        L = loop if twist == 0 else rotate_outline(loop, twist * t)
        if scale:
            k = scale(t)
            L = [(u * k, v * k, f) for u, v, f in L]
        return L

    D = cam.D
    merge = not bands and not smooth
    for loop, is_hole in loops:
        ar = _area(loop)
        sgn = 1 if ar > 0 else -1
        if is_hole:
            sgn = -sgn
        N = len(loop)
        Ls = [at(loop, q / slices) for q in range(slices + 1)]
        groups = [(0, slices)] if merge else [(k, k + 1) for k in range(slices)]
        for (k0, k1) in groups:
            # per-edge normal averaged over the slices in this group
            vis, nrm = [], []
            for i in range(N):
                j = (i + 1) % N
                acc = [0.0, 0.0, 0.0]
                for k in range(k0, k1):
                    t0, t1 = k / slices, (k + 1) / slices
                    L0, L1 = Ls[k], Ls[k + 1]
                    p0 = world(L0[i][0], L0[i][1], t0)
                    p1 = world(L0[j][0], L0[j][1], t0)
                    q0 = world(L1[i][0], L1[i][1], t1)
                    q1 = world(L1[j][0], L1[j][1], t1)
                    e = (p1[0] - p0[0] + q1[0] - q0[0], p1[1] - p0[1] + q1[1] - q0[1], p1[2] - p0[2] + q1[2] - q0[2])
                    ax = (q0[0] - p0[0] + q1[0] - p1[0], q0[1] - p0[1] + q1[1] - p1[1], q0[2] - p0[2] + q1[2] - p1[2])
                    c = _norm(_cross(e, ax))
                    acc = [acc[0] + c[0], acc[1] + c[1], acc[2] + c[2]]
                nw = _norm((acc[0] * sgn, acc[1] * sgn, acc[2] * sgn))
                nrm.append(nw)
                vis.append(_dot(nw, D) < -1e-4)
            start = 0
            for i in range(N):
                j = (i - 1) % N
                if vis[i] != vis[j] or loop[i][2] != loop[j][2]:
                    start = i
                    break
            i = 0
            t0, t1 = k0 / slices, k1 / slices
            L0, L1 = Ls[k0], Ls[k1]
            while i < N:
                a = (start + i) % N
                if not vis[a]:
                    i += 1
                    continue
                run = [a]
                fid = loop[a][2]
                while i + 1 < N:
                    b = (start + i + 1) % N
                    if vis[b] and loop[b][2] == fid:
                        run.append(b)
                        i += 1
                    else:
                        break
                i += 1
                idx = run + [(run[-1] + 1) % N]
                front = [cam.P(world(L0[q][0], L0[q][1], t0)) for q in idx]
                back = [cam.P(world(L1[q][0], L1[q][1], t1)) for q in idx]
                # intermediate helix points along the two side edges
                midR = [cam.P(world(Ls[k][idx[-1]][0], Ls[k][idx[-1]][1], k / slices)) for k in range(k0 + 1, k1)]
                midL = [cam.P(world(Ls[k][idx[0]][0], Ls[k][idx[0]][1], k / slices)) for k in range(k0 + 1, k1)]
                nn = _norm((sum(nrm[q][0] for q in run), sum(nrm[q][1] for q in run), sum(nrm[q][2] for q in run)))
                depth = sum(p[2] for p in front + back) / (2 * len(front))
                sh = min(4, shade(nn) + dark + (1 if bands and k0 % 2 else 0))
                cls = (fid_mat(fid) if fid_mat else mat) + "s%d" % sh
                d = _pd(front + midR + back[::-1] + midL[::-1]) + "Z"
                ln = ""
                if merge and lines:
                    cls += " x"
                    for g in range(1, grooves):
                        tg = g / grooves
                        kk = tg * slices
                        # interpolate outline at tg
                        Lg = at(loop, tg)
                        ln += _pd([cam.P(world(Lg[q][0], Lg[q][1], tg)) for q in idx])
                elif lines:
                    pa = (run[0] - 1) % N
                    pb = (run[-1] + 1) % N
                    sm = smooth is True or (smooth == "outer" and not is_hole)
                    if not sm or not vis[pa]:
                        ln += "M%s %sL%s %s" % (n(front[0][0]), n(front[0][1]), n(back[0][0]), n(back[0][1]))
                    if not sm or not vis[pb]:
                        ln += "M%s %sL%s %s" % (n(front[-1][0]), n(front[-1][1]), n(back[-1][0]), n(back[-1][1]))
                    if k1 == slices:
                        ln += _pd(back)
                    if k0 == 0:
                        ln += _pd(front)
                items.append((depth, cls, d, ln))
    out = ""
    if collect is not None:
        collect.extend(items)
    else:
        out += render_items(items)
    if caps:
        for t, sgn_c in ((0.0, -1), (1.0, 1)):
            nC = (A[0] * sgn_c, A[1] * sgn_c, A[2] * sgn_c)
            if _dot(nC, D) < 0:
                d = ""
                for loop, is_hole in loops:
                    L = at(loop, t)
                    d += _pd([cam.P(world(p[0], p[1], t)) for p in L]) + "Z"
                cm = cap_mat or mat
                sh = shade(nC)
                ccls = cm if sh <= 2 else cm + "s%d" % sh
                out += '<path class="%s" fill-rule="evenodd" d="%s"/>' % (ccls, d)
                if hl:
                    L = at(outline, t)
                    out += '<path class="%s" d="%s"/>' % (hl, _pd([cam.P(world(p[0], p[1], t)) for p in L]) + "Z")
    return out


def render_items(items):
    items.sort(key=lambda it: -it[0])
    out = []
    for depth, cls, d, ln in items:
        out.append('<path class="%s" d="%s"/>' % (cls, d))
        if ln:
            out.append('<path class="%s" d="%s"/>' % ("gr" if " x" in cls else "el", ln))
    return "".join(out)


def cyl(cam, O, A, r, h, mat="w", seg=48, holes_r=None, hl=None, cap_mat=None, scale=None, caps=True, collect=None):
    holes = [circle_outline(holes_r, seg, seg)] if holes_r else []
    return prism(cam, O, A, circle_outline(r, seg, 16), h, mat, holes=holes, hl=hl, cap_mat=cap_mat, smooth=True,
                 scale=scale, caps=caps, collect=collect, slices=1)


def gear3(cam, O, A, z, rp, h, mat="w", helix=0.0, bore=0.0, phase=0.0, slices=None, hl=None, ra=None, rf=None,
          hub=None, spline_bore=None, cap_mat=None, bands=False, scale=None, collect=None, caps=True, grooves=0):
    """Helical/spur gear solid. helix in degrees. hub=(r, extra_h_top) adds a boss on top."""
    twist = h * math.tan(math.radians(helix)) / rp if helix else 0.0
    sl = slices or (1 if not helix else max(2, int(abs(twist) / 0.06) + 1))
    holes = []
    if spline_bore:
        zz, ro, ri = spline_bore
        holes = [spline_outline(zz, ro, ri)]
    elif bore:
        holes = [circle_outline(bore, 40, 40)]
    return prism(cam, O, A, gear_outline(z, rp, ra, rf, phase), h, mat, holes=holes, twist=twist, slices=sl, hl=hl,
                 cap_mat=cap_mat, bands=bands, scale=scale, collect=collect, caps=caps, grooves=grooves)


def ring_gear3(cam, O, A, z, rp, r_out, h, mat="w", helix=0.0, phase=0.0, hl=None):
    twist = h * math.tan(math.radians(helix)) / rp if helix else 0.0
    sl = 1 if not helix else max(2, int(abs(twist) / 0.06) + 1)
    return prism(cam, O, A, circle_outline(r_out, 64, 16), h, mat, holes=[internal_outline(z, rp, phase)], twist=twist, slices=sl, hl=hl,
                 smooth="outer")


def mesh_phase(z1, z2, beta, phase1_space=True):
    """phases so that gear1 (z1) at c1 and gear2 (z2) at c2 mesh along direction beta (c1->c2, rad, in outline plane)."""
    p1 = beta + PI / z1  # space of gear1 at beta
    p2 = beta + PI      # tooth of gear2 pointing back at gear1
    return p1, p2


# ------------------------------------------------------------------ hob / threaded wheel (2.5D side view)
def hob(cx, cy, L, r_root, m, ang=0.0, mat="t", gashes=12, g0=0.2, lead=1, arbor=True, ends=True, grind=False):
    """Side view of a single-start hob (or threaded grinding wheel if grind=True), axis along local x.
    ang: rotation of the whole tool (deg). Returns svg group."""
    p = PI * m
    ra = r_root + 2.25 * m
    t20 = math.tan(ALPHA)
    wt = p / 2 - 2 * m * t20        # crest width
    wr = p / 2 + 2 * 1.25 * m * t20  # width at root
    x0, x1 = -L / 2, L / 2
    s = []
    # arbor & collars
    if arbor:
        s.append('<rect class="m3" x="%s" y="%s" width="%s" height="%s"/>' % (n(x0 - 46), n(-r_root * 0.42), n(L + 92), n(r_root * 0.84)))
        s.append('<rect class="m2" x="%s" y="%s" width="%s" height="%s" rx="2"/>' % (n(x0 - 12), n(-r_root * 0.8), n(12), n(r_root * 1.6)))
        s.append('<rect class="m2" x="%s" y="%s" width="%s" height="%s" rx="2"/>' % (n(x1), n(-r_root * 0.8), n(12), n(r_root * 1.6)))
    # root cylinder, banded shading
    bands = 7
    for b in range(bands):
        th0 = -PI / 2 + PI * b / bands
        th1 = -PI / 2 + PI * (b + 1) / bands
        y0, y1 = r_root * math.sin(th0), r_root * math.sin(th1)
        nrm = _norm((0, -math.sin((th0 + th1) / 2), math.cos((th0 + th1) / 2)))
        sh = shade((0, -nrm[2], -nrm[1]))  # map: screen-up = world z, toward viewer = -y
        s.append('<rect class="%ss%d" x="%s" y="%s" width="%s" height="%s"/>' % (mat, min(4, sh + (1 if grind else 2)), n(x0), n(y0), n(L), n(y1 - y0 + 0.4)))
    s.append('<rect class="o" x="%s" y="%s" width="%s" height="%s"/>' % (n(x0), n(-r_root), n(L), n(2 * r_root)))

    def xc(th, k):
        return k * p + lead * p * th / (2 * PI)

    items = []
    if grind:
        lands = [(-PI / 2, PI / 2)]
    else:
        gs = 2 * PI / gashes
        lands = []
        for j in range(-gashes, gashes):
            a = g0 + j * gs + gs * 0.14
            b = g0 + (j + 1) * gs - gs * 0.14
            a, b = max(a, -PI / 2), min(b, PI / 2)
            if b > a:
                lands.append((a, b))
    kmin = int(math.floor((x0 - p) / p)) - 1
    kmax = int(math.ceil((x1 + p) / p)) + 1
    for (a, b) in lands:
        nseg = max(1, int((b - a) / 0.32))
        ths = [a + (b - a) * q / nseg for q in range(nseg + 1)]
        for k in range(kmin, kmax + 1):
            xm = xc((a + b) / 2, k)
            if xm - wr / 2 < x0 + 1 or xm + wr / 2 > x1 - 1:
                # partial tooth at ends: clip by skipping
                if xc(a, k) - wr / 2 < x0 or xc(b, k) + wr / 2 > x1 or xc(a, k) + wr / 2 > x1 or xc(b, k) - wr / 2 < x0:
                    continue
            # subdivide land for shading
            for q in range(nseg):
                t0, t1 = ths[q], ths[q + 1]
                tm = (t0 + t1) / 2
                depth = -ra * math.cos(tm)
                nz = math.cos(tm)
                # land (crest)
                land = [(xc(t0, k) - wt / 2, ra * math.sin(t0)), (xc(t1, k) - wt / 2, ra * math.sin(t1)),
                        (xc(t1, k) + wt / 2, ra * math.sin(t1)), (xc(t0, k) + wt / 2, ra * math.sin(t0))]
                # flanks (between crest and root edges)
                fl = [(xc(t0, k) - wr / 2, r_root * math.sin(t0)), (xc(t1, k) - wr / 2, r_root * math.sin(t1)),
                      (xc(t1, k) - wt / 2, ra * math.sin(t1)), (xc(t0, k) - wt / 2, ra * math.sin(t0))]
                fr = [(xc(t0, k) + wt / 2, ra * math.sin(t0)), (xc(t1, k) + wt / 2, ra * math.sin(t1)),
                      (xc(t1, k) + wr / 2, r_root * math.sin(t1)), (xc(t0, k) + wr / 2, r_root * math.sin(t0))]
                # shading: light from upper-left-front
                ln_ = (0.0, -math.sin(tm), math.cos(tm))  # (x, screen-up, toward viewer)
                il = -0.5 * 0 + 0.75 * (-math.sin(tm)) * 0.8 + 0.6 * math.cos(tm)
                shl = 1 if il > 0.62 else 2 if il > 0.3 else 3 if il > 0.0 else 4
                items.append((depth + 0.2, "%ss%d" % (mat, min(4, shl + 1)), fl, True))
                items.append((depth + 0.2, "%ss%d" % (mat, min(4, shl + 2)), fr, True))
                items.append((depth, "%ss%d" % (mat, shl), land, False))
            if not grind:
                # gash faces (cutting faces) visible on the side facing the viewer
                for th, vis in ((a, math.sin(a) > 0.05), (b, math.sin(b) < -0.05)):
                    if not vis:
                        continue
                    face = [(xc(th, k) - wt / 2, ra * math.sin(th)), (xc(th, k) + wt / 2, ra * math.sin(th)),
                            (xc(th, k) + wr / 2, r_root * math.sin(th)), (xc(th, k) - wr / 2, r_root * math.sin(th))]
                    items.append((-r_root * math.cos(th) - 0.5, "%ss4" % mat, face, True))
    items.sort(key=lambda it: -it[0])
    for depth, cls, ps, edge in items:
        s.append('<path class="%s" d="%sZ"/>' % (cls, _pd(ps)))
    # outline strokes of crest edges for crispness
    edges = []
    for (a, b) in lands:
        nseg = max(1, int((b - a) / 0.32))
        ths = [a + (b - a) * q / nseg for q in range(nseg + 1)]
        for k in range(kmin, kmax + 1):
            if xc(a, k) - wr / 2 < x0 or xc(b, k) + wr / 2 > x1 or xc(a, k) + wr / 2 > x1 or xc(b, k) - wr / 2 < x0:
                continue
            for sg in (-1, 1):
                edges.append(_pd([(xc(t, k) + sg * wt / 2, ra * math.sin(t)) for t in ths]))
            if not grind:
                edges.append(_pd([(xc(a, k) - wt / 2, ra * math.sin(a)), (xc(a, k) + wt / 2, ra * math.sin(a))]))
                edges.append(_pd([(xc(b, k) - wt / 2, ra * math.sin(b)), (xc(b, k) + wt / 2, ra * math.sin(b))]))
    s.append('<path class="el" d="%s"/>' % "".join(edges))
    if grind:
        # abrasive speckle
        sp = []
        for i in range(90):
            xx = x0 + 4 + ((i * 37.3) % (L - 8))
            yy = -ra * 0.9 + ((i * 53.7) % (1.8 * ra))
            sp.append("M%s %sh.1" % (n(xx), n(yy)))
        s.append('<path class="grit2" d="%s"/>' % "".join(sp))
    g = '<g transform="translate(%s %s) rotate(%s)">%s</g>' % (n(cx), n(cy), n(ang), "".join(s))
    return g


# ------------------------------------------------------------------ bevel / hypoid ring gear (3D, face teeth)
def bevel_ring(cam, O, r_in, r_out, h, z, mat="w", spiral=0.55, face_rise=0.0, hl=None, bore=None, back_h=None):
    """Spiral-bevel ring gear lying with axis vertical. Teeth on the top face as curved radial ridges.
    Body = annulus r_in..r_out of height h (top at O.z + h). Teeth height ~ tooth depth on top."""
    Ax = (0, 0, 1)
    out = prism(cam, O, Ax, circle_outline(r_out, 72, 24), h, mat, holes=[circle_outline(bore or r_in * 0.7, 48, 48)], caps=False,
                smooth=True)
    # top: teeth strips (ridges) between r_in and r_out, spiral (circular arc approx: angle offset grows with r)
    tz = O[2] + h
    dep = (r_out - r_in) * 0.16
    step = 2 * PI / z
    items = []
    D = cam.D
    # cap annulus under the teeth (root)
    root = []
    for k in range(72):
        a = 2 * PI * k / 72
        root.append(cam.P((O[0] + r_out * math.cos(a), O[1] + r_out * math.sin(a), tz)))
    rin_pts = []
    for k in range(72):
        a = 2 * PI * k / 72
        rin_pts.append(cam.P((O[0] + r_in * math.cos(a), O[1] + r_in * math.sin(a), tz)))
    capd = _pd(root) + "Z" + _pd(rin_pts[::-1]) + "Z"
    s = out + '<path class="%ss3" fill-rule="evenodd" d="%s"/>' % (mat, capd)
    # inner face ring (r_in down to bore) as cap
    bo = bore or r_in * 0.7
    inner = [cam.P((O[0] + r_in * math.cos(2 * PI * k / 60), O[1] + r_in * math.sin(2 * PI * k / 60), tz)) for k in range(60)]
    bor = [cam.P((O[0] + bo * math.cos(2 * PI * k / 60), O[1] + bo * math.sin(2 * PI * k / 60), tz)) for k in range(60)]
    s += '<path class="%s" fill-rule="evenodd" d="%sZ%sZ"/>' % (mat, _pd(inner), _pd(bor[::-1]))
    rh = (r_in + bo) / 2
    for k in range(10):
        a = 2 * PI * (k + 0.5) / 10
        hc = [cam.P((O[0] + rh * math.cos(a) + 4.2 * math.cos(2 * PI * q / 16), O[1] + rh * math.sin(a) + 4.2 * math.sin(2 * PI * q / 16), tz)) for q in range(16)]
        s += '<path class="bg" d="%sZ"/>' % _pd(hc)
    nr = 6
    for i in range(z):
        c = i * step
        tw = step * 0.26

        def pt(r, sgn, top):
            frac = (r - r_in) / (r_out - r_in)
            a = c + spiral * (frac - 0.5) ** 2 * 2.2 + spiral * frac * 0.9 + sgn * tw * (0.8 + 0.4 * frac) * (r_in + (r_out - r_in) * 0.5) / r
            zz = tz + (dep if top else 0)
            return (O[0] + r * math.cos(a), O[1] + r * math.sin(a), zz)
        rs = [r_in + (r_out - r_in) * q / nr for q in range(nr + 1)]
        topL = [pt(r, -0.55, True) for r in rs]
        topR = [pt(r, 0.55, True) for r in rs]
        botL = [pt(r, -1.0, False) for r in rs]
        botR = [pt(r, 1.0, False) for r in rs]
        mid = pt((r_in + r_out) / 2, 0, True)
        dmid = cam.P(mid)[2]
        # flank L, flank R, top land, outer end face
        for poly_, cls_shift, nvec in ((botL + topL[::-1], 2, None), (topR + botR[::-1], 3, None)):
            P2 = [cam.P(q) for q in poly_]
            # visibility via signed area in screen
            ar = _area([(q[0], q[1]) for q in P2])
            items.append((dmid + 0.3, "%ss%d" % (mat, cls_shift), P2))
        land = [cam.P(q) for q in topL + topR[::-1]]
        items.append((dmid, "%ss1" % mat, land))
        # outer heel face
        heel = [cam.P(botL[-1]), cam.P(topL[-1]), cam.P(topR[-1]), cam.P(botR[-1])]
        a_h = c
        if _dot((math.cos(a_h), math.sin(a_h), 0), D) < 0:
            items.append((cam.P(botL[-1])[2] - 0.5, "%ss2" % mat, heel))
    items.sort(key=lambda it: -it[0])
    for dd, cls, ps in items:
        s += '<path class="%s" d="%sZ"/>' % (cls, _pd(ps))
    return s
