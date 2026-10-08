"""v3 shaded-3D part drawings: interior, exterior, wheel, thermal and common (fastener / bearing) parts.
Curved resin / glass / rubber parts are built as meshes (sweeps and lathes of a profile) so their surfaces
shade in soft bands; machined metal parts use the il3_lib prisms."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P

PI = math.pi


# =====================================================================================
# mesh helpers (own to this file): quads between rows of 3D points, back-face culled, shaded like
# GE.prism (mat s1..s4), runs of equal shade merged into one strip, outline = silhouette + border
# =====================================================================================
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def _nz(a):
    l = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    return (a[0] / l, a[1] / l, a[2] / l) if l > 1e-9 else (0.0, 0.0, 0.0)


def mesh_items(cam, rows, mat, dark=0, flip=False, closed=False, lines=True, crease=0.0, edge_rows=True, fmat=None, auto=False, grp=None):
    """rows: list of point lists (same length). Returns render items (depth, cls, d, ln).
    closed: each row wraps around. crease: draw a line where neighbour normals differ by more than this (cos)."""
    R, C = len(rows), len(rows[0])
    PP = [[cam.P(p) for p in r] for r in rows]
    NC = C if closed else C - 1
    D = cam.D
    q = {}
    if auto == "row":
        cen = [_mul(tuple(sum(p[k] for p in r) for k in range(3)), 1.0 / C) for r in rows]
    elif auto:
        cen = [_mul(tuple(sum(r[j][k] for r in rows[:-1]) for k in range(3)), 1.0 / (R - 1)) for j in range(C)]
    for i in range(R - 1):
        for j in range(NC):
            j1 = (j + 1) % C
            a, b, c, d = rows[i][j], rows[i][j1], rows[i + 1][j1], rows[i + 1][j]
            nm = _nz(GE._cross(_sub(c, a), _sub(d, b)))
            if flip:
                nm = _mul(nm, -1)
            if auto:      # normal away from the section centre (auto="row": rows are sections; else columns are)
                cc = _mul(_add(cen[i], cen[i + 1]), .5) if auto == "row" else _mul(_add(cen[j], cen[j1]), .5)
                qc = _mul(_add(_add(a, b), _add(c, d)), .25)
                if GE._dot(nm, _sub(qc, cc)) < 0:
                    nm = _mul(nm, -1)
            q[i, j] = (GE._dot(nm, D) < -1e-4, nm)
    shn = {}
    if grp:            # shade rows of one group with their averaged normal (prism-like aligned bands)
        acc = {}
        for (i, j), (v, nm) in q.items():
            g = (grp[i], j)
            a = acc.get(g, (0, 0, 0))
            acc[g] = _add(a, nm)
        shn = {(i, j): _nz(acc[grp[i], j]) for (i, j) in q}

    def shd(i, j):
        return min(4, GE.shade(shn.get((i, j), q[i, j][1]), dark))
    items = []

    def edge(i, j, k):
        """segment k (0 bottom row i, 1 right, 2 top row i+1, 3 left) of quad (i,j) as screen points"""
        j1 = (j + 1) % C
        e = ((i, j), (i, j1)) if k == 0 else ((i, j1), (i + 1, j1)) if k == 1 else ((i + 1, j1), (i + 1, j)) if k == 2 else ((i + 1, j), (i, j))
        return PP[e[0][0]][e[0][1]], PP[e[1][0]][e[1][1]]

    def nb(i, j, k):
        if k == 0:
            return (i - 1, j) if i > 0 else None
        if k == 2:
            return (i + 1, j) if i < R - 2 else None
        jj = j + (1 if k == 1 else -1)
        if closed:
            return (i, jj % C)
        return (i, jj) if 0 <= jj < NC else None

    runs = []                      # (i0, i1, run, sh, mat): rows i0..i1 share the same j-run and shade
    for i in range(R - 1):
        j = 0
        while j < NC:
            v, nm = q[i, j]
            if not v:
                j += 1
                continue
            sh = shd(i, j)
            run = [j]
            while j + 1 < NC and q[i, j + 1][0] and shd(i, j + 1) == sh:
                j += 1
                run.append(j)
            j += 1
            m = fmat(i, run[0]) if fmat else mat
            prev = next((r for r in runs if r[1] == i - 1 and r[2] == run and r[3] == sh and r[4] == m), None)
            if prev:
                runs[runs.index(prev)] = (prev[0], i, run, sh, m)
            else:
                runs.append((i, i, run, sh, m))
    for i0, i1, run, sh, m in runs:
        je = (run[-1] + 1) % C
        pts = [PP[i0][jj] for jj in run] + [PP[i][je] for i in range(i0, i1 + 2)] + \
              [PP[i1 + 1][jj] for jj in reversed(run)] + [PP[i][run[0]] for i in range(i1, i0, -1)]
        depth = sum(p[2] for p in pts) / len(pts)
        segs = []
        if lines:
            for i in range(i0, i1 + 1):
                for jj in run:
                    for k in range(4):
                        o = nb(i, jj, k)
                        draw = o is None and (edge_rows or k in (1, 3))
                        if o is not None:
                            ov, on = q[o]
                            draw = (not ov) or (crease and GE._dot(on, q[i, jj][1]) < crease)
                        if draw:
                            segs.append(edge(i, jj, k))
        items.append((depth, "%ss%d" % (m, sh), GE._pd(pts) + "Z", chain(segs)))
    return items


def chain(segs):
    """join 2-point screen segments into polylines (shared end points -> L)."""
    S = [(n(a[0]) + " " + n(a[1]), n(b[0]) + " " + n(b[1])) for a, b in segs]
    S = [s_ for s_ in S if s_[0] != s_[1]]
    adj = {}
    for k, (a, b) in enumerate(S):
        adj.setdefault(a, []).append(k)
        adj.setdefault(b, []).append(k)
    used = [False] * len(S)
    o = ""
    for k0 in range(len(S)):
        if used[k0]:
            continue
        used[k0] = True
        a, b = S[k0]
        line = [a, b]
        for end in (1, 0):            # grow forward from b, then backward from a
            cur = line[-1] if end else line[0]
            while True:
                nx = next((k for k in adj[cur] if not used[k]), None)
                if nx is None:
                    break
                used[nx] = True
                p_, q_ = S[nx]
                cur = q_ if p_ == cur else p_
                if end:
                    line.append(cur)
                else:
                    line.insert(0, cur)
        o += "M" + "L".join(line)
    return o


def render(items):
    """like GE.render_items, but outline segments become one path per item (class el)."""
    items = sorted(items, key=lambda it: -it[0])
    o = []
    for depth, cls, d, ln in items:
        o.append('<path class="%s" d="%s"/>' % (cls, d))
        if ln:
            o.append('<path class="el" d="%s"/>' % ln)
    return "".join(o)


def lathe_rows(C, A, prof, seg=48, a0=0.0, a1=360.0, ph=0.0):
    """rows for a surface of revolution: prof = [(r, t), ...] (t along A from C)."""
    E1, E2, A = GE.frame(A)
    full = abs(a1 - a0) >= 359.9
    nseg = seg if full else seg + 1
    angs = [math.radians(a0 + ph + (a1 - a0) * k / seg) for k in range(nseg)]
    cs = [(math.cos(a), math.sin(a)) for a in angs]
    return [[(C[0] + r * (c * E1[0] + s * E2[0]) + t * A[0], C[1] + r * (c * E1[1] + s * E2[1]) + t * A[1],
              C[2] + r * (c * E1[2] + s * E2[2]) + t * A[2]) for c, s in cs] for r, t in prof], full


def lathe(cam, C, A, prof, mat="w", seg=48, dark=0, flip=False, **kw):
    """prof points may carry a 3rd value = shading group of the segment that starts there."""
    """items of a revolved profile. prof ordered so that the solid is on the RIGHT going first->last
    when r is up and t is right (outer surface of a cylinder: [(R, 0), (R, h)]; its bore: [(r, h), (r, 0)])."""
    rows, full = lathe_rows(C, A, [p[:2] for p in prof], seg)
    if any(len(p) > 2 for p in prof) and "grp" not in kw:
        kw["grp"] = [p[2] if len(p) > 2 else 1000 + i for i, p in enumerate(prof[:-1])]
    return mesh_items(cam, rows, mat, dark, flip=flip, closed=full, **kw)


def newell(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    return _nz((nx, ny, nz))


def cap_item(cam, ring, away, mat, dark=0):
    """flat end face of a sweep (ring of 3D points), facing away from point `away`; None when hidden."""
    nm = newell(ring)
    c = _mul(tuple(sum(p[k] for p in ring) for k in range(3)), 1.0 / len(ring))
    if GE._dot(nm, _sub(c, away)) < 0:
        nm = _mul(nm, -1)
    if GE._dot(nm, cam.D) >= 0:
        return None
    pp = [cam.P(p) for p in ring]
    return (sum(p[2] for p in pp) / len(pp), "%ss%d" % (mat, min(4, GE.shade(nm, dark))), GE._pd(pp) + "Z", GE._pd(pp + pp[:1]))


def sweep(cam, stations, mat, dark=0, caps=True, **kw):
    """closed sections (lists of 3D points, same count) joined in order; flat caps at both ends."""
    it = mesh_items(cam, stations, mat, dark, closed=True, auto="row", **kw)
    if caps:
        for a, b in ((0, 1), (-1, -2)):
            c = cap_item(cam, stations[a], _mul(tuple(sum(p[k] for p in stations[b]) for k in range(3)), 1.0 / len(stations[b])), mat, dark)
            if c:
                it.append(c)
    return it


def soft_y(prof, y0, y1, mat, cam, r=6.0, dark=0, n_=3, axis="y", bow=None, **kw):
    """profile [(x, z)] (convex, closed) extruded along y from y0 to y1 with rounded ends: the section
    shrinks about its centre over the last r units (quarter-circle law) -> soft upholstered edges."""
    cx = sum(p[0] for p in prof) / len(prof)
    cz = sum(p[1] for p in prof) / len(prof)
    ext = max(max(abs(p[0] - cx), abs(p[1] - cz)) for p in prof)
    ys = []
    for k in range(n_ + 1):
        a = PI / 2 * k / n_
        ys.append((y0 + r * (1 - math.sin(a)), 1 - (r / ext) * (1 - math.cos(a))))
    ys = ys[::-1]
    mid = [(y0 + r + (y1 - y0 - 2 * r) * k / 10, 1) for k in range(1, 10)] if bow else []
    ys += mid + [(y1 - (y - y0), f) for y, f in reversed(ys)]
    if axis == "y":
        st = [[(cx + (x - cx) * f, y, cz + (z - cz) * f) for x, z in prof] for y, f in ys]
    else:       # axis x: prof is [(y, z)]
        st = [[(y, cx + (x - cx) * f + (bow(y) if bow else 0), cz + (z - cz) * f) for x, z in prof] for y, f in ys]
    return sweep(cam, st, mat, dark, **kw)


def ring_pts(C, A, r, seg=48, ph=0.0):
    E1, E2, A = GE.frame(A)
    return [_add(C, _add(_mul(E1, math.cos(2 * PI * k / seg + ph)), _mul(E2, math.sin(2 * PI * k / seg + ph))), r) for k in range(seg)]


def shade_cls(cam, nrm, mat, dark=0):
    sh = min(4, GE.shade(nrm, dark))
    return "%ss%d" % (mat, sh)


def poly3(cam, pts, cls):
    return path(GE._pd([cam.P(p) for p in pts]) + "Z", cls)


def facing(cam, nrm):
    return GE._dot(nrm, cam.D) < 0


# =====================================================================================
# wheel.tire — radial tyre standing on edge: rounded sidewalls (rim protector rib), shoulders,
# tread with 4 circumferential grooves and lateral shoulder grooves, bead and dark inner liner
# =====================================================================================
def tire_profile(R=150, rb=96, W=55):
    # outboard half, from the tread edge down to the bead: (r, t, shading group of the following segment)
    half = [(150, W - 18, 1), (148.6, W - 13, 1), (145.5, W - 8, 2), (140, W - 3.5, 2), (132, W - 1, 3), (122, W + 1.5, 3), (rb + 21, W, 4),
            (rb + 18, W + 2.5, 5), (rb + 14, W + 2.5, 6), (rb + 12, W, 7), (rb + 5, W - 1, 7), (rb, W - 5, 7)]
    back = [(r, -t, 10 + g) for r, t, g in reversed(half)]
    tread = []
    t = -W + 18
    for g in (-30, -11, 7, 26):
        tread += [(150, t, 0), (150, g - .5, 20), (142, g, 0), (142, g + 5, 21), (150, g + 5.5, 0)]
        t = g + 5.5
    return back[:-1] + [(150, -W + 18, 0)] + tread + half
def tire_items(cam, C=(0, 0, 0), A=(0, -1, 0), R=150, rb=96, W=55, seg=40, lug=True):
    it = lathe(cam, C, A, [(rb + .5, W - 5), (rb + .5, -W + 5)], "dk", seg=48, dark=1, lines=False)   # inner liner (bore)
    it += lathe(cam, C, A, tire_profile(R, rb, W), "dk", seg=seg)
    if lug:
        E1, E2, A_ = GE.frame(A)
        for k in range(44):
            a = 2 * PI * (k + .25) / 44
            rad = _add(_mul(E1, math.cos(a)), E2, math.sin(a))
            if GE._dot(rad, cam.D) > -0.12:
                continue
            for t0, t1 in ((-W + 9, -30.5), (30.5, W - 9)):
                pts = []
                for tt in (t0, (t0 + t1) / 2, t1):
                    r = R if abs(tt) < W - 18 else R - 4 - (abs(tt) - (W - 18)) * .45
                    da = (tt - t0) / (t1 - t0) * .035 * (1 if t0 < 0 else -1)
                    rr = _add(_mul(E1, math.cos(a + da)), E2, math.sin(a + da))
                    pts.append(cam.P(_add(_add(C, A_, tt), rr, r + .3)))
                it.append((min(p[2] for p in pts) - 1, "rbline", GE._pd(pts), ""))
    return it


def tire(az=38, el=14):
    def fn(sc):
        cam = sc.cam
        it = tire_items(cam)
        # rim-protector and sidewall rings (faint lines on the outboard sidewall)
        o = render(it)
        for r, t in ((124, -56.2), (108, -57.6)):
            o += path(P(circ3(cam, (0, t, 0), (0, -1, 0), r, 56)), "gr")
        return o
    return fit(fn, az, el, (50, 8, 270, 182), sh_ry=7, sh_k=.42, sh_dy=-2)


@part("wheel.tire")
def _():
    return tire()


# =====================================================================================
# wheel.alwheel — cast aluminium wheel: rim barrel (flanges, bead seats, drop well), 5 twin spokes
# with chamfered edges sweeping from a raised hub to the rim, 5 lug holes and centre cap
# =====================================================================================
def spoke_rows(C, A, a, da, r0, r1, t0, t1, w0, w1, dep, ns=7):
    E1, E2, A_ = GE.frame(A)
    rows = []
    for k in range(ns + 1):
        s_ = k / ns
        th = a + da * s_
        r = r0 + (r1 - r0) * s_
        t = t0 + (t1 - t0) * s_ + 3.5 * math.sin(PI * s_)
        rad = _add(_mul(E1, math.cos(th)), E2, math.sin(th))
        tan = _add(_mul(E1, -math.sin(th)), E2, math.cos(th))
        w = (w0 + (w1 - w0) * s_) / 2
        c0 = _add(_add(C, A_, t), rad, r)
        sec = [(-w * .7, -dep), (w * .7, -dep), (w + 1.2, -3.5), (w - .8, 0), (-w + .8, 0), (-w - 1.2, -3.5)]
        rows.append([_add(_add(c0, tan, u), A_, v) for u, v in sec])
    return tube(rows)


def tube(stations):
    """stations (list of section rings) -> rows for mesh_items(auto=True): one row per section vertex
    (closed by repeating the first), columns along the length -> flat faces merge into single strips."""
    m = len(stations[0])
    return [[st[v % m] for st in stations] for v in range(m + 1)]


def alwheel(az=26, el=12, ns=5):
    A = (0, -1, 0)
    outer = [(105, -52), (108.5, -50), (108.5, -46), (101, -43), (100, -32), (89, -25), (88, -10), (88, 12), (91, 17), (100, 23), (101, 41),
             (108.5, 45), (108.5, 49.5)]
    inner = [(96, 53.5), (96, 26), (85, 18), (84, -18), (95, -28), (96, -48), (103, -52.5), (105, -52)]
    lip = [(108.5, 49.5), (106, 53), (101, 54.5), (96, 54.5)]
    hub = [(40, 49), (38.5, 57), (35, 61), (19, 61.5), (16.5, 63.5), (10, 67.5), (0, 68.4)]

    def fn(sc):
        cam = sc.cam
        o = render(lathe(cam, (0, 0, 0), A, outer, "w", 36, dark=.35) + lathe(cam, (0, 0, 0), A, inner, "w", 36, dark=2, lines=False))
        sp = []
        for k in range(ns):
            a = 2 * PI * k / ns + PI / 2
            for sg in (-1, 1):
                rows = spoke_rows((0, 0, 0), A, a + sg * .075, sg * .19, 34, 97, 57, 50, 13, 10, 20, 4)
                sp += mesh_items(cam, rows, "w", auto=True)
        o += render(sp)
        o += render(lathe(cam, (0, 0, 0), A, hub, "w", 28))
        E1, E2, _ = GE.frame(A)
        for k in range(5):
            a = 2 * PI * (k + .5) / ns + PI / 2
            c = (24 * math.cos(a), -61.6, 24 * math.sin(a))
            c = _add(_mul(E1, 24 * math.cos(a)), E2, 24 * math.sin(a))
            c = _add(c, A, 61.6)
            o += hole3(cam, c, A, 5.2, "w3") + hole3(cam, c, A, 3.6, "bg")
        o += path(P(circ3(cam, (0, -66.6, 0), A, 13, 32)), "gr")
        o += render(lathe(cam, (0, 0, 0), A, lip, "w", 40))
        return o
    return fit(fn, az, el, (56, 8, 264, 182), sh_ry=7, sh_k=.42, sh_dy=-2)


@part("wheel.alwheel")
def _():
    return alwheel()


# =====================================================================================
# common.bearing — deep-groove ball bearing lying flat: outer / inner ring with raceway grooves and
# chamfers, 9 polished balls in the gap held by a riveted brass cage
# =====================================================================================
def bearing(az=-28, el=34, nb=9):
    R, ro, ri, rI, H, rp, rb = 100, 84, 56, 40, 36, 70, 13.4
    zc = H / 2
    ringA = [(85.5, H), (ro, H - 1.5), (ro, 27), (ro + 1.3, 24), (ro + 2, zc), (ro + 1.3, 12), (ro, 9), (ro, 1.5), (85.5, 0)]
    ringB = [(85.5, 0), (R - 1.5, 0), (R, 1.5, 1), (R, H - 1.5, 2), (R - 1.5, H, 3), (85.5, H)]
    inner = [(rI + 1.5, 0), (ri - 1.5, 0), (ri, 1.5, 1), (ri, 9, 1), (ri - 1.3, 12, 2), (ri - 2, zc, 3), (ri - 1.3, 24, 4), (ri, 27, 5),
             (ri, H - 1.5, 5), (ri - 1.5, H, 6), (rI + 1.5, H, 7), (rI, H - 1.5, 8), (rI, 1.5, 9), (rI + 1.5, 0)]
    Az = (0, 0, 1)

    def fn(sc):
        cam = sc.cam
        o = render(lathe(cam, (0, 0, 0), Az, ringA, "w", 48, dark=.6))
        o += path(P(circ3(cam, (0, 0, 2), Az, rp, 48)), "bg")            # gap seen between the rings
        small = []
        d0 = cam.P((0, 0, zc))[2]
        for k in range(nb):
            a = 2 * PI * k / nb
            c = (rp * math.cos(a), rp * math.sin(a), zc)
            x, y, d = cam.P(c)
            small.append((d, ell(x, y, rb * cam.s, rb * cam.s, "ball"), d > d0))
            a2 = a + PI / nb                                                # cage bridge between two balls
            da = .55 * PI / nb
            sect = [((rp + q) * math.cos(a2 + sg * da), (rp + q) * math.sin(a2 + sg * da)) for q, sg in ((-7, -1), (7, -1), (7, 1), (-7, 1))]
            sect = [(-v, u, i) for i, (u, v) in enumerate(sect)]
            cb = (rp * math.cos(a2), rp * math.sin(a2), zc)
            small.append((cam.P(cb)[2], compact(GE.prism(cam, (0, 0, zc - 5), Az, sect, 10, "gw")) +
                          hole3(cam, (cb[0], cb[1], zc + 5.1), Az, 2.4, "gw"), cam.P(cb)[2] > d0))
        small.sort(key=lambda t: -t[0])
        o += "".join(s_ for _, s_, far in small if far)
        o += render(lathe(cam, (0, 0, 0), Az, inner, "w", 40))
        o += "".join(s_ for _, s_, far in small if not far)
        o += render(lathe(cam, (0, 0, 0), Az, ringB, "w", 56))
        return o
    return fit(fn, az, el, (60, 12, 260, 178), sh_ry=8, sh_k=.5, sh_dy=-5)


@part("common.bearing")
def _():
    return bearing()


# =====================================================================================
# common.bolt — high-strength hex flange bolt: chamfered hex head, washer flange, plain shank,
# rolled thread (crest / root bands) with a chamfered lead-in point
# =====================================================================================
def bolt(az=24, el=20):
    def fn(sc):
        cam = sc.cam
        A = (1, 0, 0)
        hexo = [(15.5 * math.cos(PI / 6 + k * PI / 3), 15.5 * math.sin(PI / 6 + k * PI / 3), k) for k in range(6)]
        it = []
        # flange (washer face) and hex head; the head's top edge is chamfered (outline shrinks near the top)
        it += lathe(cam, (0, 0, 0), A, [(15, -.5), (20.5, 1.2), (20.5, 4), (19, 5.5)], "w", 40)
        o = render(it)
        o += compact(GE.prism(cam, (0, 0, 0), (-1, 0, 0), hexo, 15, "w", slices=3,
                              scale=lambda t: 1.0 if t < .67 else 1 - .2 * (t - .67) / .33, cap_mat="w"))
        o += hole3(cam, (-15.1, 0, 0), (-1, 0, 0), 11.5, "w2")              # chamfer circle on the head top
        # shank, thread run-out, thread bands, chamfered point
        o += render(lathe(cam, (0, 0, 0), A, [(9.4, 5.5), (9.4, 46), (9, 49)], "w", 32))
        L0, p_, nt = 49, 4.2, 21
        prof = []
        for k in range(nt):
            x = L0 + k * p_
            prof += [(9.6, x, 0), (8.1, x + .5 * p_, 1)]
        x = L0 + nt * p_
        prof += [(9.4, x, 2), (7.6, x + 3.4, 3), (6.2, x + 3.8)]
        o += render(lathe(cam, (0, 0, 0), A, prof, "w", 22, lines=False))
        D = cam.D
        th = math.atan2(-D[1], D[2])
        for sg in (1, -1):        # crest / root zigzag along the two silhouettes
            c_, s_ = sg * math.cos(th), sg * math.sin(th)
            o += path(P([cam.xy((t, r * c_, r * s_)) for r, t, *_ in [(9, 49)] + prof], False), "el")
        o += path(P(circ3(cam, (prof[-1][1], 0, 0), A, 6.2, 20)), "el")
        return o
    return fit(fn, az, el, (22, 40, 298, 166), sh_ry=6, sh_k=.42, sh_dy=-3)


@part("common.bolt")
def _():
    return bolt()


# =====================================================================================
# common.sintered — sintered (powder-metal) timing sprocket: roller-seat tooth form, raised hub
# boss, bore with keyway; matte pressed surfaces
# =====================================================================================
def sprocket_outline(z=24, rp=80.0, rs=7.4, ra=88.0):
    pts = []
    for k in range(z):
        f = 2 * PI * k / z
        cx, cy = rp * math.cos(f), rp * math.sin(f)
        for q in range(-4, 5):                       # roller seat: inner part of a circle around the pitch point
            a = f + PI + math.radians(q * 19)
            pts.append((cx + rs * math.cos(a), cy + rs * math.sin(a)))
        g = f + PI / z                                # tooth tip between two seats
        for d in (-.028, .028):
            pts.append((ra * math.cos(g + d), ra * math.sin(g + d)))
    pts.sort(key=lambda p: math.atan2(p[1], p[0]))
    return [(x, y, i // 2) for i, (x, y) in enumerate(pts)]


def sintered(az=-26, el=36):
    def fn(sc):
        cam = sc.cam
        Az = (0, 0, 1)
        bore = [(20 * math.cos(math.radians(a)), 20 * math.sin(math.radians(a)), 0) for a in range(-75, 256, 15)]
        bore = [(19.3, -5.2, 0), (24, -5.2, 1), (24, 5.2, 2), (19.3, 5.2, 3)] + [p for p in bore if not (-16 < math.degrees(math.atan2(p[1], p[0])) < 16)]
        bore.sort(key=lambda p: math.atan2(p[1], p[0]))
        bore = [(-y, x, f) for x, y, f in bore]
        ol = [(-y, x, f) for x, y, f in sprocket_outline()]
        o = GE.prism(cam, (0, 0, 0), Az, ol, 11, "w", holes=[bore], smooth="outer")
        o += path(P(circ3(cam, (0, 0, 11.05), Az, 60, 48)), "gr")
        o += compact(GE.prism(cam, (0, 0, 11), Az, GE.circle_outline(36, 40, 10), 10, "w", holes=[bore], smooth="outer"))
        o += path(P(circ3(cam, (0, 0, 21.05), Az, 31, 40)), "gr")
        return o
    return fit(fn, az, el, (62, 14, 258, 178), sh_ry=7, sh_k=.5, sh_dy=-5)


@part("common.sintered")
def _():
    return sintered()


# =====================================================================================
# interior.seat — front seat: cushion and seatback with raised side bolsters and lumbar bulge,
# headrest on two stays, recliner cover, steel slide rails and the slide release bar
# =====================================================================================
def seat(az=52, el=20, tilt=16):
    t = math.radians(tilt)
    U, F, pv = (math.sin(t), math.cos(t)), (-math.cos(t), math.sin(t)), (98, 40)

    def bk(ds):        # seatback local (d forward, s up) -> side-view (x, z)
        return [(pv[0] + s_ * U[0] + d * F[0], pv[1] + s_ * U[1] + d * F[1]) for d, s_ in ds]

    cush_in = hull(arc(13, 37, 13, 110, 260, 5) + [(34, 50), (70, 48.5), (95, 45), (101, 30), (97, 22), (16, 22)])
    cush_bo = hull(arc(15, 40, 15, 100, 260, 6) + [(38, 58), (70, 56), (94, 51), (101, 32), (97, 22), (16, 22)])
    back_in = hull(bk([(-26, 2), (-26, 142), (-20, 150), (-5, 150), (0, 140), (3, 90), (5, 45), (1, 12), (-8, 4)]))
    back_bo = hull(bk([(-26, 2), (-26, 130), (-19, 140), (-6, 138), (6, 112), (13, 72), (13, 30), (7, 8), (-8, 2)]))
    head = hull(bk([(-22, 160), (-22, 196)] + arc(-8, 196, 14, 0, 90, 4) + [(4, 166), (-2, 158)]))

    def fn(sc):
        cam = sc.cam
        it = []
        # slide rails + risers + front release bar (steel)
        for y in (-34, 30):
            it += sweep(cam, [[(x, y + a, b) for a, b in ((0, 6), (4, 6), (4, 14), (0, 14))] for x in (-4, 112)], "w", dark=.3)
            for x in (6, 84):
                it += sweep(cam, [[(x + a, y, b) for a, b in ((0, 14), (10, 14), (10, 22), (0, 22))] for y in (y + .5, y + 3.5)], "w", dark=.5)
        it += lathe(cam, (-6, -40, 12), (0, 1, 0), [(2.2, 0), (2.2, 74)], "w", 12)
        it += soft_y(cush_in, -26, 26, "m", cam, r=4, dark=.2)
        it += soft_y(back_in, -26, 26, "m", cam, r=4, dark=.2)
        for y0, y1 in ((-49, -25), (25, 49)):
            it += soft_y(cush_bo, y0, y1, "dk", cam, r=8)
            it += soft_y(back_bo, y0, y1, "dk", cam, r=8)
        # headrest stays and headrest
        for y in (-17, 17):
            p0 = bk([(-10, 146)])[0]
            it += lathe(cam, (p0[0], y, p0[1]), (U[0], 0, U[1]), [(2.4, 0), (2.4, 16)], "w", 12)
        it += soft_y(head, -36, 36, "dk", cam, r=10, n_=4)
        # recliner cover on the outboard side
        it += lathe(cam, (pv[0] - 2, -49, pv[1] - 4), (0, -1, 0), [(14, 0), (14, 3), (11, 6), (0, 6.5)], "dk", 24, dark=.4)
        o = render(it)
        # stitch lines where the insert meets the bolsters (visible faces only)
        for y in (-25.5, 25.5):
            for pr, sel in ((cush_in, lambda p: p[1] > 44), (back_in, lambda p: (p[0] - pv[0]) * F[0] + (p[1] - pv[1]) * F[1] > -1)):
                pts = [p for p in pr if sel(p)]
                pts.sort(key=lambda p: p[0] * U[0] + p[1] * U[1] if pr is back_in else p[0])
                o += path(P([cam.xy((x, y, z)) for x, z in pts], False), "gr")
        return o
    return fit(fn, az, el, (54, 6, 266, 182), sh_ry=7, sh_k=.42, sh_dy=-3)


@part("interior.seat")
def _():
    return seat()


# =====================================================================================
# interior.instpanel — instrument panel (cockpit side): two-tone upper pad / lower panel with soft
# ends, meter hood over the cluster on the driver side, centre stack with vents and a floating
# display, side vents, glovebox lid; the airbag tear line is hidden on the back (not drawn)
# =====================================================================================
def instpanel(az=-16, el=24):
    lower = hull([(22, 0), (-1, 20), (-5, 38), (-3, 50), (110, 50), (110, 0)])
    upper = hull(arc(-5, 59, 9, 90, 270, 5) + [(18, 72), (60, 75), (108, 67), (126, 57), (120, 50), (-4, 50)])
    hood = hull(arc(0, 78, 9, 100, 250, 4) + [(24, 86), (42, 82), (44, 70), (-4, 68)])
    stack = hull([(-14, 4), (-15, 46), (-12, 50), (6, 50), (6, 4)])
    bw = lambda x: 26 * (x / 150) ** 2

    def face_pt(x, z, prof=lower, dy=-.4):
        """point on the rear (cabin) face of a profile at height z (outline edge with smallest y)."""
        best = None
        for i in range(len(prof)):
            (y1, z1), (y2, z2) = prof[i], prof[(i + 1) % len(prof)]
            if min(z1, z2) <= z <= max(z1, z2) and z1 != z2:
                y = y1 + (y2 - y1) * (z - z1) / (z2 - z1)
                best = y if best is None else min(best, y)
        return (x, best + dy + (bw(x) if prof is not stack else 0), z)

    def fn(sc):
        cam = sc.cam
        o = render(soft_y(lower, -150, 150, "pt", cam, r=10, axis="x", dark=.25, bow=bw))
        o += render(soft_y(upper, -153, 153, "w", cam, r=12, axis="x", bow=bw))
        o += render(soft_y(stack, -34, 34, "w", cam, r=4, axis="x", dark=.2))
        o += render(soft_y(hood, 34, 118, "w", cam, r=9, axis="x", n_=3, bow=bw))
        # meter cluster opening under the hood
        o += poly3(cam, [(40, -11 + bw(40), 66), (112, -11 + bw(112), 66), (110, -9.5 + bw(110), 53), (42, -9.5 + bw(42), 53)], "bg")
        # floating centre display
        o += render(sweep(cam, [[(x, -6 + a, b) for a, b in ((-2, 74), (2, 74), (6, 104), (2, 104))] for x in (-38, 38)], "w", dark=.3))
        o += poly3(cam, [(-35, -8.4, 76), (35, -8.4, 76), (35, -4.4, 102), (-35, -4.4, 102)], "bg")
        # centre vents (on the stack) and side vents (at the ends), with louvres
        for x0, x1, yy, z0, z1, b_ in ((-28, -4, -15.3, 34, 44, 0), (4, 28, -15.3, 34, 44, 0), (-140, -116, -14.5, 54, 64, 1), (120, 144, -14.5, 54, 64, 1)):
            q = [(x0, yy + b_ * bw(x0), z0), (x1, yy + b_ * bw(x1), z0), (x1, yy - .4 + b_ * bw(x1), z1), (x0, yy - .4 + b_ * bw(x0), z1)]
            o += poly3(cam, q, "bg")
            o += path("".join(P([cam.xy(_add(q[0], _sub(q[3], q[0]), f)), cam.xy(_add(q[1], _sub(q[2], q[1]), f))], False) for f in (.33, .66)), "gr")
        # switch row on the stack, glovebox lid line and handle (passenger side)
        for k in range(5):
            x = -20 + k * 10
            o += poly3(cam, [face_pt(x - 3.5, 22, stack, -.5), face_pt(x + 3.5, 22, stack, -.5), face_pt(x + 3.5, 28, stack, -.5),
                             face_pt(x - 3.5, 28, stack, -.5)], "ms2")
        g = [face_pt(-128, 18), face_pt(-50, 18), face_pt(-50, 42), face_pt(-128, 42)]
        o += path(P([cam.xy(p) for p in g]), "el")
        o += poly3(cam, [face_pt(-98, 37), face_pt(-80, 37), face_pt(-80, 39.5), face_pt(-98, 39.5)], "bg")
        return o
    return fit(fn, az, el, (18, 26, 302, 172), sh_ry=7, sh_k=.46, sh_dy=-3)


@part("interior.instpanel")
def _():
    return instpanel()


# =====================================================================================
# interior.doortrim — door trim (cabin side): moulded PP base panel with soft edges, fabric insert,
# beltline upper trim, armrest with window-switch panel, inside handle bezel, speaker grille,
# map pocket
# =====================================================================================
def doortrim(az=22, el=14):
    base = [(2, 104), (0, 10), (10, 0), (226, 0), (240, 10), (252, 92), (246, 110), (10, 114)]
    upper = hull(arc(-8, 108, 8, 90, 260, 5) + [(0, 96), (0, 116)])
    arm = hull(arc(-22, 60, 8, 80, 280, 6) + [(0, 48), (0, 70), (-8, 70), (-10, 46)])
    pocket = hull([(0, 6), (0, 34), (-13, 34), (-15, 10), (-12, 6)])

    def fn(sc):
        cam = sc.cam
        o = render(soft_y(base, -9, 0, "w", cam, r=3))
        o += render(soft_y([(30, 70), (236, 70), (244, 96), (36, 96)], -10.5, -8.5, "pt", cam, r=1, dark=.2))
        o += render(soft_y(upper, 4, 248, "w", cam, r=6, axis="x"))
        o += render(soft_y(pocket, 112, 238, "w", cam, r=5, axis="x", dark=.2))
        o += poly3(cam, [(117, -9.5, 33.8), (233, -9.5, 33.8), (233, -12.5, 33.9), (117, -12.5, 33.9)], "bg")
        # speaker grille: dark disc with a dot pattern
        C, A = (60, -9.2, 32), (0, -1, 0)
        o += path(P(circ3(cam, C, A, 21, 32)), "ws3") + path(P(circ3(cam, C, A, 19, 32)), "bg")
        for i in range(-3, 4):
            for j in range(-3, 4):
                if i * i + j * j <= 10:
                    o += hole3(cam, (C[0] + i * 5.2, C[1] - .2, C[2] + j * 5.2), A, 1.3, "ms4")
        o += render(soft_y(arm, 40, 214, "w", cam, r=6, axis="x"))
        # window switch panel at the front of the armrest
        o += render(soft_y([(150, -20), (206, -20), (206, -8), (150, -8)], 70.1, 72, "dk", cam, r=.8, dark=.3, axis="y"))
        for k in range(4):
            x = 156 + k * 12.5
            o += poly3(cam, [(x, -16, 72.2), (x + 8, -16, 72.2), (x + 8, -11, 72.2), (x, -11, 72.2)], "ms3")
        # inside handle: recessed bezel and lever
        o += poly3(cam, [(184, -9.2, 78), (222, -9.2, 78), (222, -9.2, 90), (184, -9.2, 90)], "bg")
        o += render(soft_y(hull([(-1, 81), (-1, 87), (-5, 86.5), (-5, 81.5)]), 188, 214, "al", cam, r=2, axis="x"))
        return o
    return fit(fn, az, el, (34, 14, 286, 180), sh_ry=7, sh_k=.42, sh_dy=-2)


@part("interior.doortrim")
def _():
    return doortrim()


# =====================================================================================
# interior.airbag — driver airbag deployed: nylon cushion (front panel seam, vent holes) inflated
# from the module: retainer plate with studs and the disc-type inflator with its gas-port ring
# =====================================================================================
def airbag(az=48, el=18):
    bag = [(0, -83), (14, -86), (34, -88), (58, -84.5), (76, -76, 1), (87, -66, 1), (92, -56, 2), (89, -45, 2), (80, -34, 3), (66, -23, 3),
           (48, -13, 4), (33, -7, 4), (28, -3)]

    def fn(sc):
        cam = sc.cam
        A = (1, 0, 0)
        it = lathe(cam, (0, 0, 0), A, bag, "pt", 36)
        o = render(it)
        o += path(P(circ3(cam, (-56, 0, 0), A, 91.6, 40)), "gr")                  # seam of the front / rear panels
        for ps in (145, 195):                                                      # vent holes on the rear panel
            c, s_ = math.cos(math.radians(ps)), math.sin(math.radians(ps))
            o += hole3(cam, (-30, 77 * c, 77 * s_), _nz((.6, .8 * c, .8 * s_)), 6, "bg")
        # module: retainer plate with 4 studs, inflator disc with flange and gas ports, connector
        it = sweep(cam, [[(x, y, z) for y, z in ((-36, -32), (36, -32), (40, -28), (40, 28), (36, 32), (-36, 32), (-40, 28), (-40, -28))]
                         for x in (-2, 3)], "m", dark=.3)
        o += render(it)
        for y, z in ((-30, -24), (30, -24), (-30, 24), (30, 24)):
            o += render(lathe(cam, (3, y, z), A, [(2.4, 0), (2.4, 12), (1.8, 13)], "w", 10))
        o += render(lathe(cam, (3, 0, 0), A, [(33, 0), (33, 3, 1), (28, 3.5), (27, 4, 2), (27, 16, 2), (25, 19, 3), (14, 20.5), (0, 21)], "m", 32))
        for k in range(8):
            a = 2 * PI * k / 8
            nr = (0, math.cos(a), math.sin(a))
            if GE._dot(nr, cam.D) < -.2:
                o += hole3(cam, (12, 27.2 * nr[1], 27.2 * nr[2]), nr, 2.2, "bg")
        o += render(sweep(cam, [[(x, y, z) for y, z in ((-6, -5), (6, -5), (6, 5), (-6, 5))] for x in (24, 34)], "dk", dark=.3))
        return o
    return fit(fn, az, el, (42, 10, 278, 180), sh_ry=7, sh_k=.42, sh_dy=-3)


@part("interior.airbag")
def _():
    return airbag()


# =====================================================================================
# interior.seatbelt — 3-point belt: retractor (steel frame, wound webbing spool, spring cover,
# pretensioner tube and gas generator), webbing through the shoulder D-ring down to the tongue,
# and the buckle
# =====================================================================================
def belt_strip(cam, pts, w=40, th=2.2, mat="dk", dark=0):
    """webbing along a polyline, its broad face turned toward the viewer."""
    st = []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        d = _nz(_sub(b, a))
        W = _nz(GE._cross(d, _add(_mul(cam.D, -1), (0, 0, 1), .5)))
        nrm = _nz(GE._cross(W, d))
        st.append([_add(_add(p, nrm, u * th / 2), W, v * w / 2) for u, v in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    return sweep(cam, st, mat, dark)


def seatbelt(az=20, el=14):
    def fn(sc):
        cam = sc.cam
        o = ""
        # retractor frame: back plate + two side flanges (U), base tab
        it = sweep(cam, [[(x, y, z) for x, z in ((0, 0), (6, 0), (6, 70), (0, 70))] for y in (-30, 30)], "m", dark=.4)
        for y0 in (-30, 24):
            it += sweep(cam, [[(x, y, z) for x, z in ((0, 0), (52, 0), (52, 50), (40, 66), (0, 66))] for y in (y0, y0 + 6)], "m", dark=.1)
        o += render(it)
        # wound webbing on the spool between the flanges, spring cover on the outboard flange
        o += render(lathe(cam, (30, -24, 34), (0, 1, 0), [(24, 0), (24, 48)], "dk", 32))
        o += render(lathe(cam, (30, -30, 34), (0, -1, 0), [(25, 0), (25, 9, 1), (22, 12), (0, 12.5)], "dk", 32, dark=.2))
        # pretensioner: gas generator + tube up the side
        o += render(lathe(cam, (64, -14, 4), (0, 0, 1), [(7, 0), (7, 46), (5.5, 50)], "w", 16, dark=.3))
        o += render(lathe(cam, (64, -14, 4), (0, -1, 0), [(9, 0), (9, 18), (6, 20)], "m", 16))
        # webbing: spool -> D-ring -> tongue
        dr = (128, 0, 186)
        o += render(belt_strip(cam, [(54, 0, 36), (60, 0, 62), (dr[0] - 4, 0, dr[2] - 10)]))
        o += render(belt_strip(cam, [(dr[0] + 4, -1, dr[2] - 10), (210, -1, 86), (238, -1, 50)], dark=.15))
        # D-ring: anchor plate with a slot, bolt head
        ring = hull(arc(dr[0], dr[2] + 8, 26, 0, 180, 6) + [(dr[0] - 26, dr[2] - 8), (dr[0] + 26, dr[2] - 8), (dr[0], dr[2] - 20)])
        o += render(soft_y(ring, -30, -25, "al", cam, r=1.2))
        o += poly3(cam, [(dr[0] - 20, -30.3, dr[2] - 6), (dr[0] + 20, -30.3, dr[2] - 6), (dr[0] + 20, -30.3, dr[2] - 1), (dr[0] - 20, -30.3, dr[2] - 1)], "bg")
        o += render(lathe(cam, (dr[0], -30, dr[2] + 14), (0, -1, 0), [(9, 0), (9, 4, 1), (7, 6), (0, 6.3)], "m", 20))
        # tongue (latch plate) and buckle, along the lower webbing direction
        e = (238, 0, 50)
        d = _nz(_sub(e, (210, 0, 86)))
        W = _nz(GE._cross(d, _add(_mul(cam.D, -1), (0, 0, 1), .5)))
        nr = _nz(GE._cross(W, d))

        def blk(s0, s1, hw, ht, mat, dk=0, sec=((-1, -1), (1, -1), (1, 1), (-1, 1))):
            return render(sweep(cam, [[_add(_add(_add(e, d, s_), nr, u * ht), W, v * hw) for u, v in sec] for s_ in (s0, s1)], mat, dk))
        o += blk(-6, 16, 25, 4.5, "dk", .2)
        o += blk(16, 34, 13, 1.5, "al")
        o += blk(32, 96, 24, 12, "dk", 0, ((-1, -1), (1, -1), (1, -.5), (.6, 1), (-.6, 1), (-1, -.5)))
        bt = _add(e, d, 50)
        o += poly3(cam, [_add(_add(_add(bt, d, a_), W, c_), nr, 12.2) for a_, c_ in ((-8, -15), (8, -15), (8, 15), (-8, 15))], "ms3")   # release button
        return o
    return fit(fn, az, el, (30, 8, 290, 180), sh_ry=7, sh_k=.4, sh_dy=-3)


@part("interior.seatbelt")
def _():
    return seatbelt()


def face_y(prof, z):
    """smallest y of a closed (y, z) outline at height z (the face toward -y)."""
    best = None
    for i in range(len(prof)):
        (y1, z1), (y2, z2) = prof[i], prof[(i + 1) % len(prof)]
        if min(z1, z2) <= z <= max(z1, z2) and z1 != z2:
            y = y1 + (y2 - y1) * (z - z1) / (z2 - z1)
            best = y if best is None else min(best, y)
    return best


def on_face(prof, bow, x, z, dy=-.4):
    return (x, face_y(prof, z) + dy + bow(x), z)


# =====================================================================================
# exterior.bumper — painted PP front bumper fascia: face swept round the corners in plan, lower
# grille opening with louvres, fog-lamp bezels, air-curtain slits, chin spoiler lip
# =====================================================================================
def bumper(az=26, el=16):
    prof = hull(arc(10, 70, 12, 95, 200, 4) + arc(4, 30, 26, 160, 260, 5) + [(26, 82), (40, 80), (40, 4), (8, 2)])
    bw = lambda x: 64 * (abs(x) / 160) ** 3.2

    def fn(sc):
        cam = sc.cam
        o = render(soft_y(prof, -160, 160, "pt", cam, r=14, axis="x", n_=4, bow=bw))
        # chin spoiler lip (black)
        lip = hull([(0, 2), (-2, 6), (12, 6), (30, 3), (30, -1), (6, -1)])
        o += render(soft_y(lip, -120, 120, "dk", cam, r=6, axis="x", bow=lambda x: bw(x) + 4))

        def quad(x0, x1, z0, z1, cls, ins=0):
            pts = [on_face(prof, bw, x, z0) for x in (x0, (x0 + x1) / 2, x1)] + [on_face(prof, bw, x, z1) for x in (x1, (x0 + x1) / 2, x0)]
            if ins:
                pts = [pts[0], _add(pts[1], (0, 0, -ins)), pts[2], pts[3], _add(pts[4], (0, 0, ins)), pts[5]]
            return poly3(cam, pts, cls)
        o += quad(-84, 84, 12, 36, "bg", 2)
        for z in (19, 27):          # louvres in the lower opening
            o += path(P([cam.xy(on_face(prof, bw, x, z, -.6)) for x in range(-80, 81, 20)], False), "rbline")
        for sg in (-1, 1):
            xs = sorted((sg * 106, sg * 142))
            o += quad(xs[0], xs[1], 16, 30, "dk")
            o += quad(xs[0] + 4, xs[1] - 4, 19, 27, "bg")
            xs = sorted((sg * 112, sg * 136))
            o += quad(xs[0], xs[1], 44, 48, "bg")
        return o
    return fit(fn, az, el, (16, 30, 304, 168), sh_ry=7, sh_k=.46, sh_dy=-4)


@part("exterior.bumper")
def _():
    return bumper()


# =====================================================================================
# glass helpers: a curved pane as a grid; drawn as one translucent fill, a black ceramic frit band
# round the edge, light reflection streaks and the edge (thickness) lines
# =====================================================================================
def pane_grid(f, nu=12, nv=6):
    """f(u, v) -> 3D point, u, v in [0, 1]."""
    return [[f(i / nu, j / nv) for i in range(nu + 1)] for j in range(nv + 1)]


def pane_border(g):
    nv, nu = len(g) - 1, len(g[0]) - 1
    return g[0] + [g[j][nu] for j in range(1, nv + 1)] + g[nv][::-1][1:] + [g[j][0] for j in range(nv - 1, 0, -1)]


def glass(cam, f, frit=7.0, streaks=((.18, .34), (.4, .5)), th=4.0, nrm=(0, -1, 0), lam=False, bracket=None, nu=12, nv=6):
    """f(u, v) gives the outer surface; frit = band width (model units); streaks = (u at v=0) pairs.
    th: glass thickness shown along the bottom edge (offset along -nrm)."""
    g = pane_grid(f, nu, nv)
    bd = pane_border(g)
    o = ""
    # bottom edge thickness band (seen below the outer face)
    lo = g[0]
    back = [_add(p, nrm, -th) for p in lo]
    o += poly3(cam, lo + back[::-1], "gl")
    if lam:
        o += path(P([cam.xy(_add(p, nrm, -th / 2)) for p in lo], False), "gr")
    if bracket:
        o += bracket(cam)
    o += poly3(cam, bd, "gl")
    # frit band: outer border + inset border (evenodd)
    du, dv = frit / max(1e-6, _len(_sub(g[0][-1], g[0][0]))), frit / max(1e-6, _len(_sub(g[-1][0], g[0][0])))
    gi = pane_grid(lambda u, v: f(du + u * (1 - 2 * du), dv * 1.4 + v * (1 - 2.4 * dv)), nu, nv)
    ins = pane_border(gi)
    o += path(GE._pd([cam.P(p) for p in bd]) + "Z" + GE._pd([cam.P(p) for p in ins]) + "Z", "dks4", ' fill-rule="evenodd"')
    # reflection streaks (light, slanted)
    for u0, u1 in streaks:
        w = (u1 - u0) * .45
        pts = [f(min(.98, max(.02, u0 + .2 * v + (w if k else 0))), v) for k in (0, 1) for v in ((.08, .92) if k == 0 else (.92, .08))]
        o += poly3(cam, pts, "ms1")
    o += path(GE._pd([cam.P(p) for p in bd]) + "Z", "el")
    return o


def _len(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


# =====================================================================================
# exterior.windshield — laminated windscreen: raked pane curved across the width and slightly in
# height, black frit band with a dotted fade at the top centre, camera / mirror bracket seen through
# the glass, and the 2-ply + PVB edge
# =====================================================================================
def windshield(az=-24, el=24):
    W, Hh, rake = 300, 150, math.radians(58)

    def f(u, v):
        x = (u - .5) * (W - 34 * v)                       # narrower at the top
        z = v * Hh * math.sin(rake)
        y = v * Hh * math.cos(rake) + 46 * ((x / (W / 2)) ** 2) + 10 * math.sin(PI * v)
        y -= 6 * math.sin(PI * v) * (1 - (x / (W / 2)) ** 2)
        return (x, y, z)

    def bracket(cam):
        p = f(.5, .9)
        o = render(sweep(cam, [[_add(p, (a, 4, b)) for a, b in ((-14, -26), (14, -26), (16, 4), (-16, 4))] for _ in (0,)] +
                         [[_add(p, (a, 10, b)) for a, b in ((-14, -26), (14, -26), (16, 4), (-16, 4))]], "dk", dark=.3))
        return o

    def fn(sc):
        cam = sc.cam
        o = glass(cam, f, frit=8, streaks=((.16, .3), (.36, .44)), th=5, lam=True, bracket=bracket, nu=14)
        for k in range(9):                                   # frit dot fade at the top centre
            for j in range(2):
                p = f(.42 + k * .02, .86 - j * .035)
                o += hole3(cam, _add(p, (0, -.3, 0)), (0, -1, .3), 1.6 - j * .5, "dks4")
        return o
    return fit(fn, az, el, (26, 22, 294, 172), sh_ry=6, sh_k=.42, sh_dy=-2)


@part("exterior.windshield")
def _():
    return windshield()


# =====================================================================================
# exterior.sideglass — tempered glass: a curved backlite (rear window) with printed heater lines,
# bus bars and an antenna pattern, and a framed-door side glass standing behind it
# =====================================================================================
def sideglass(az=-22, el=22):
    def rear(u, v):
        x = (u - .5) * (250 - 60 * v) + 30
        y = 40 + v * 60 + 26 * (((x - 30) / 125) ** 2)
        z = v * 92
        return (x, y, z)

    def door(u, v):
        x0 = -150 + 30 * v
        x1 = -10 - 34 * v * v
        x = x0 + (x1 - x0) * u
        return (x, 150 + 8 * v * v, 34 + v * (96 - 24 * (2 * u - 1) ** 2))

    def fn(sc):
        cam = sc.cam
        o = glass(cam, door, frit=0.01, streaks=((.3, .4),), th=4, nrm=(0, -1, 0), nu=8, nv=4)
        o += glass(cam, rear, frit=7, streaks=((.14, .24), (.3, .36)), th=4, nu=12, nv=5)
        # heater lines between two bus bars, antenna pattern in the upper area
        d = ""
        for k in range(9):
            v = .14 + k * .062
            d += P([cam.xy(rear(u / 12, v)) for u in range(1, 12)], False)
        o += path(d, "wirebond", ' style="stroke-width:.8"')
        for u0, u1 in ((.07, .09), (.91, .93)):
            o += poly3(cam, [rear(u0, .1), rear(u1, .1), rear(u1, .66), rear(u0, .66)], "cus2")
        o += path(P([cam.xy(rear(u / 10, .76)) for u in range(2, 9)], False) + P([cam.xy(rear(u / 10, .83)) for u in range(3, 8)], False) +
                  P([cam.xy(rear(.5, .7)), cam.xy(rear(.5, .83))], False), "wirebond", ' style="stroke-width:.8"')
        return o
    return fit(fn, az, el, (24, 14, 296, 176), sh_ry=6, sh_k=.42, sh_dy=-2)


@part("exterior.sideglass")
def _():
    return sideglass()


# =====================================================================================
# exterior.weatherstrip — door-opening weatherstrip: U-shaped trim with a steel core carrier and
# gripping lips, hollow sponge bulb; a straight run with a cut end and a moulded 90-degree corner
# =====================================================================================
WS_PARTS = (     # convex pieces of the section (y, z); bulb = ring
    ("wall", [(4, 0), (9, 0), (9.5, 24), (4, 22)]),
    ("wall", [(-9, 0), (-4, 0), (-4, 22), (-9.5, 24)]),
    ("top", [(-9.5, 22), (9.5, 22), (8.5, 27), (-8.5, 27)]),
)


def ws_piece(cam, O, A, h, kind, loop):
    if kind == "bulb":
        return compact(GE.prism(cam, O, A, GE.circle_outline(11, 28, 7, -16, 30), h, "w", holes=[GE.circle_outline(7.5, 24, 6, -16, 30)],
                                smooth="outer"))
    return compact(GE.prism(cam, O, A, [(u, v, i) for i, (u, v) in enumerate(loop)], h, "w", smooth=False))


def weatherstrip(az=28, el=22, L=180, R=46, nk=6):
    def fn(sc):
        cam = sc.cam
        segs = []
        # corner: turns from +x toward +y around (L, R)
        for k in range(nk):
            a0, a1 = -PI / 2 + PI / 2 * k / nk, -PI / 2 + PI / 2 * (k + 1) / nk
            p0 = (L + R * math.cos(a0), R + R * math.sin(a0), 0)
            p1 = (L + R * math.cos(a1), R + R * math.sin(a1), 0)
            d = _sub(p1, p0)
            segs.append((p0, _nz(d), _len(d)))
        segs.append(((L, R, 0), (0, 1, 0), 110))
        segs.sort(key=lambda s_: -cam.P(_add(s_[0], s_[1], s_[2] / 2))[2])
        o = ""
        pieces = list(WS_PARTS) + [("bulb", None)]
        for O, A, h in segs:
            for kind, loop in pieces:
                o += ws_piece(cam, O, A, h, kind, loop)
        for kind, loop in pieces:           # straight run, cut end at x = 0
            o += ws_piece(cam, (0, 0, 0), (1, 0, 0), L, kind, loop)
        # cut face details: steel core (U) and the gripping lips inside the channel
        for q in (((-7.4, 2), (-5.8, 2), (-5.8, 23), (-7.4, 23)), ((5.8, 2), (7.4, 2), (7.4, 23), (5.8, 23)), ((-7.4, 23), (7.4, 23), (7.4, 24.6), (-7.4, 24.6))):
            o += poly3(cam, [(-.2, y, z) for y, z in q], "ms2")
        for sg in (-1, 1):
            for z in (7, 14):
                o += poly3(cam, [(-.2, sg * 4, z), (-.2, sg * .8, z + 2.5), (-.2, sg * 4, z + 4)], "ws2")
        return o
    return fit(fn, az, el, (30, 30, 290, 172), sh_ry=6, sh_k=.42, sh_dy=-3)


@part("exterior.weatherstrip")
def _():
    return weatherstrip()


# =====================================================================================
# exterior.grille — chrome-plated ABS radiator grille: trapezoidal plated surround (rounded section
# swept round the opening), black horizontal louvres with a plated top bar, dark backing
# =====================================================================================
def rrect_path(x0, x1, xt0, xt1, z0, z1, r, n_=4):
    """rounded trapezoid in the x-z plane (bottom x0..x1 at z0, top xt0..xt1 at z1), counter-clockwise."""
    cs = [((x1, z0), -90, 0), ((xt1, z1), 0, 90), ((xt0, z1), 90, 180), ((x0, z0), 180, 270)]
    cxz = [(x1 - r, z0 + r), (xt1 - r, z1 - r), (xt0 + r, z1 - r), (x0 + r, z0 + r)]
    pts = []
    for (cx, cz), (_, a0, a1) in zip(cxz, cs):
        pts += [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n_)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * k / n_))) for k in range(n_ + 1)]
    return pts


def grille(az=22, el=14):
    bw = lambda x: 18 * (x / 130) ** 2
    path2 = rrect_path(-104, 104, -128, 128, 0, 92, 16)
    ctr = (0, 46)
    sec = [(0, 1), (2, -6), (6, -10), (11, -10), (15, -5), (16, 2)]      # (outward, toward viewer)

    def fn(sc):
        cam = sc.cam
        N = len(path2)
        st = []
        for i in range(N + 1):
            p = path2[i % N]
            a, b = path2[(i - 1) % N], path2[(i + 1) % N]
            t = _nz((b[0] - a[0], 0, b[1] - a[1]))
            nO = (t[2], 0, -t[0])
            if nO[0] * (p[0] - ctr[0]) + nO[2] * (p[1] - ctr[1]) < 0:
                nO = _mul(nO, -1)
            base = (p[0], bw(p[0]), p[1])
            st.append([_add(_add(base, nO, u - 4), (0, 1, 0), -v) for u, v in sec])
        # backing (dark) and louvres
        inner = [(p[0] * .97, bw(p[0]) + 12, (p[1] - 46) * .96 + 46) for p in path2]
        o = poly3(cam, inner, "dks4")
        it = []
        for k in range(7):
            z = 10 + k * 11.5
            half = 104 + 24 * z / 92 - 6
            prof = hull([(0, z), (0, z + 3), (-7, z + 6.5), (-11, z + 5), (-9, z + 1)])
            it = soft_y(prof, -half, half, "al" if k == 6 else "w", cam, r=2, axis="x", bow=lambda x: bw(x) + 6, n_=2)
            o += render(it)
        o += render(sweep(cam, st, "al", caps=False))
        return o
    return fit(fn, az, el, (26, 26, 294, 170), sh_ry=6, sh_k=.44, sh_dy=-3)


@part("exterior.grille")
def _():
    return grille()
