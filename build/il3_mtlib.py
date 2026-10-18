"""Shared helpers for the v3 machine-tool atlas drawings (il3_mt*.py). Registers no keys.

A thin layer over il_mt.Scene (bounding-box ordering) and il_gear (camera, 4-step shading
<mat>s1..s4). Everything takes the Scene `sc` first and adds one or more ordered items to it;
`*_svg` variants return (svg, bbox) so several parts can be merged into one item.
World axes: x right, y away from the viewer, z up. Axis arguments are "x"/"y"/"z" or unit tuples.

    from il3_mtlib import *
    block(sc, -100, -50, 0, 200, 100, 60, "pt", ch=8, b=3, dark=1)   # painted casting
    MCYL(sc, (0, 0, 60), (0, 0, 1), 20, 50)                           # banded steel with a specular streak
    rail(sc, (-90, -20, 60), "x", 180, "z", carriages=[(40, 36)])     # linear guide + carriage
"""
import math
import il_gear as GE
from il_base import n, path
from il3_lib import compact, circ3, P, hole3

AX = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}
_IDX = {"x": 0, "y": 1, "z": 2}
_UV = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}       # world components used as (u, v) in a cross-section


# ------------------------------------------------------------------ small vector helpers
def V(a):
    """axis name or tuple -> unit tuple."""
    return AX[a] if isinstance(a, str) else GE._norm(a)


def add3(a, b, k=1.0):
    """a + k*b for 3-tuples."""
    return (a[0] + k * b[0], a[1] + k * b[1], a[2] + k * b[2])


def lin(p, *terms):
    """p + sum(k * vec) for terms given as (k, vec) pairs."""
    x, y, z = p
    for k, v in terms:
        x, y, z = x + k * v[0], y + k * v[1], z + k * v[2]
    return (x, y, z)


def _ax_char(a):
    a = V(a)
    i = max(range(3), key=lambda k: abs(a[k]))
    return "xyz"[i], (1 if a[i] > 0 else -1)


def bbox(pts_):
    """axis-aligned world bbox of 3D points."""
    return (tuple(min(p[i] for p in pts_) for i in range(3)), tuple(max(p[i] for p in pts_) for i in range(3)))


def bbu(*bbs):
    """union of bboxes."""
    return (tuple(min(b[0][i] for b in bbs) for i in range(3)), tuple(max(b[1][i] for b in bbs) for i in range(3)))


def poly3(cam, pts3, cls, close=True):
    """3D polyline/polygon -> svg path."""
    return path(P([cam.xy(p) for p in pts3], close), cls)


_SUB = __import__("re").compile(r"M([^ML]+)((?:L[^ML]+)*)")


def chain(d):
    """join line segments/polylines of a path that share end points into longer polylines (smaller svg)."""
    pls = []
    for m in _SUB.finditer(d):
        pts_ = [m.group(1).strip()] + [q.strip() for q in m.group(2).split("L") if q.strip()]
        if len(pts_) > 1:
            pls.append(pts_)
    out = []
    while pls:
        cur = pls.pop(0)
        grown = True
        while grown:
            grown = False
            for i, q in enumerate(pls):
                if q[0] == cur[-1]:
                    cur += q[1:]
                elif q[-1] == cur[-1]:
                    cur += q[::-1][1:]
                elif q[-1] == cur[0]:
                    cur = q + cur[1:]
                elif q[0] == cur[0]:
                    cur = q[::-1] + cur[1:]
                else:
                    continue
                pls.pop(i)
                grown = True
                break
        out.append("M" + "L".join(cur))
    return "".join(out)


def _chain_svg(svg):
    """chain the 'el'/'gr' line paths of an svg fragment."""
    return __import__("re").sub(r'<path class="(el|gr)" d="([^"]*)"/>', lambda m: '<path class="%s" d="%s"/>' % (m.group(1), chain(m.group(2))), svg)


# ------------------------------------------------------------------ convex solids (painted castings, blocks, rails)
def cvx_svg(cam, faces, mat="pt", dark=0, fmat=None, crease=55):
    """convex solid from planar faces (lists of 3D points, any winding): visible faces shaded <mat>s1..4,
    silhouette in 'el', sharp creases (> crease deg) in 'gr'. fmat: {face index: material} overrides."""
    D = cam.D
    allp = [p for f in faces for p in f]
    c = tuple(sum(p[i] for p in allp) / len(allp) for i in range(3))
    info, body = [], {}
    for k, f in enumerate(faces):
        nx = ny = nz = 0.0
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            nx += (a[1] - b[1]) * (a[2] + b[2])
            ny += (a[2] - b[2]) * (a[0] + b[0])
            nz += (a[0] - b[0]) * (a[1] + b[1])
        nrm = GE._norm((nx, ny, nz)) if (nx or ny or nz) else (0, 0, 1)
        fc = tuple(sum(p[i] for p in f) / len(f) for i in range(3))
        if GE._dot(nrm, (fc[0] - c[0], fc[1] - c[1], fc[2] - c[2])) < 0:
            nrm = (-nrm[0], -nrm[1], -nrm[2])
        vis = GE._dot(nrm, D) < -1e-4
        info.append((nrm, vis))
        if vis:
            m = (fmat or {}).get(k, mat)
            dk = dark(nrm) if callable(dark) else dark
            cl = "%ss%d" % (m, min(4, GE.shade(nrm) + dk))
            body[cl] = body.get(cl, "") + P([cam.xy(p) for p in f])
    edges = {}
    for k, f in enumerate(faces):
        for i in range(len(f)):
            a, b = f[i], f[(i + 1) % len(f)]
            ka, kb = tuple(round(v, 2) for v in a), tuple(round(v, 2) for v in b)
            if ka == kb:
                continue
            edges.setdefault((min(ka, kb), max(ka, kb)), []).append(k)
    el, gr = "", ""
    cc = math.cos(math.radians(crease))
    for (a, b), fs in edges.items():
        if len(fs) != 2:
            continue
        v0, v1 = info[fs[0]][1], info[fs[1]][1]
        if v0 == v1 and (not v0 or GE._dot(info[fs[0]][0], info[fs[1]][0]) > cc):
            continue
        pa, pb = cam.xy(a), cam.xy(b)
        s = "M%s %sL%s %s" % (n(pa[0]), n(pa[1]), n(pb[0]), n(pb[1]))
        if v0 != v1:
            el += s
        else:
            gr += s
    body = "".join(path(d, c) for c, d in body.items())   # visible faces of a convex solid never overlap
    return body + (path(chain(gr), "gr") if gr else "") + (path(chain(el), "el") if el else "")


def _inset(poly, d):
    """inset a convex CCW polygon [(u, v)] by d."""
    m, out = len(poly), []
    for i in range(m):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % m]
        e1 = GE._norm((p1[0] - p0[0], p1[1] - p0[1], 0))
        e2 = GE._norm((p2[0] - p1[0], p2[1] - p1[1], 0))
        n1, n2 = (-e1[1], e1[0]), (-e2[1], e2[0])
        k = 1 + n1[0] * n2[0] + n1[1] * n2[1]
        out.append((p1[0] + d * (n1[0] + n2[0]) / k, p1[1] + d * (n1[1] + n2[1]) / k))
    return out


def cprism_svg(cam, axis, t0, L, uv, mat="pt", b0=0.0, b1=0.0, dark=0, fmat=None, crease=55):
    """convex outline uv [(u, v)] in the cross-section of axis ("x": (y,z), "y": (x,z), "z": (x,y)),
    extruded from t0 to t0+L with 45-degree bevels b0/b1 at the two ends -> (svg, bbox)."""
    uv = [(p[0], p[1]) for p in uv]
    ar = sum(uv[i - 1][0] * uv[i][1] - uv[i][0] * uv[i - 1][1] for i in range(len(uv)))
    if ar < 0:
        uv = uv[::-1]
    iu, iv = _UV[axis]
    it = _IDX[axis]

    def w(p, t):
        q = [0.0, 0.0, 0.0]
        q[iu], q[iv], q[it] = p[0], p[1], t
        return tuple(q)
    rings = []
    if b0:
        rings.append([w(p, t0) for p in _inset(uv, b0)])
    rings.append([w(p, t0 + b0) for p in uv])
    rings.append([w(p, t0 + L - b1) for p in uv])
    if b1:
        rings.append([w(p, t0 + L) for p in _inset(uv, b1)])
    m = len(uv)
    faces = [rings[0][::-1], rings[-1]]
    for ra, rb in zip(rings, rings[1:]):
        for i in range(m):
            j = (i + 1) % m
            faces.append([ra[i], ra[j], rb[j], rb[i]])
    return cvx_svg(cam, faces, mat, dark, fmat, crease), bbox(rings[1] + rings[-2])


def cprism(sc, axis, t0, L, uv, mat="pt", b0=0.0, b1=0.0, dark=0, bias=0.0, fmat=None, crease=55):
    """add a bevelled convex prism (see cprism_svg) to the scene."""
    s, bb = cprism_svg(sc.cam, axis, t0, L, uv, mat, b0, b1, dark, fmat, crease)
    sc.add(s, bb, bias)
    return bb


def rr(u0, v0, u1, v1, c=0.0):
    """rectangle [(u, v)] with corners cut by c (octagon); c=0 -> plain rectangle."""
    if not c:
        return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    return [(u0 + c, v0), (u1 - c, v0), (u1, v0 + c), (u1, v1 - c), (u1 - c, v1), (u0 + c, v1), (u0, v1 - c), (u0, v0 + c)]


def abox_svg(cam, lo, hi, mat="pt", axis="z", ch=0.0, b=0.0, b0=None, dark=0, fmat=None):
    """axis-aligned box lo..hi extruded along axis; ch = chamfer of the section corners, b = end bevels."""
    iu, iv = _UV[axis]
    it = _IDX[axis]
    return cprism_svg(cam, axis, lo[it], hi[it] - lo[it], rr(lo[iu], lo[iv], hi[iu], hi[iv], ch), mat,
                      b if b0 is None else b0, b, dark, fmat)


def abox(sc, lo, hi, mat="pt", axis="z", ch=0.0, b=0.0, b0=None, dark=0, bias=0.0, fmat=None):
    """add an axis-aligned bevelled box (corner lo, corner hi)."""
    s, bb = abox_svg(sc.cam, lo, hi, mat, axis, ch, b, b0, dark, fmat)
    sc.add(s, bb, bias)
    return bb


def block(sc, x, y, z, sx, sy, sz, mat="pt", ch=0.0, b=2.0, dark=1, bias=0.0, b0=0.0):
    """painted casting: box from corner (x,y,z), vertical edges chamfered ch, top edges bevelled b
    (a lit highlight line), bottom bevel b0. dark=1 keeps big pale faces off the background."""
    return abox(sc, (x, y, z), (x + sx, y + sy, z + sz), mat, "z", ch, b, b0, dark, bias)


# ------------------------------------------------------------------ metal cylinders
def _spec(cam, O, a, r, h, r1, wdeg):
    """screen polygon of the specular streak on a cylinder side (where the normal is closest to the half vector)."""
    E1, E2, _ = GE.frame(a)
    Hh = GE._norm(add3(GE.LIGHT, cam.D, -1.0))
    best, bt = -9, 0.0
    for k in range(180):
        t = 2 * math.pi * k / 180
        nr = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
        if GE._dot(nr, cam.D) > -0.15:
            continue
        d = GE._dot(nr, Hh)
        if d > best:
            best, bt = d, t
    if best < -1:
        return ""
    r1 = r if r1 is None else r1
    pts_ = []
    for t, rad, s in ((bt - wdeg, r, 0), (bt + wdeg, r, 0), (bt + wdeg, r1, 1), (bt - wdeg, r1, 1)):
        pts_.append(cam.xy(tuple(O[i] + rad * (math.cos(t) * E1[i] + math.sin(t) * E2[i]) + s * h * a[i] for i in range(3))))
    return pts_


def MCYL_svg(cam, O, A, r, h, mat="w", seg=28, bands=12, dark=1, spec=True, r1=None, holes=(), cap_mat=None,
             rings=(), wdeg=None, lines=True):
    """banded metal cylinder/frustum with a narrow s1 specular streak and optional circumferential lines
    at fractions `rings` of its length -> (svg, bbox)."""
    a = V(A)
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    s = GE.prism(cam, O, a, GE.circle_outline(r, seg, bands), h, mat, holes=list(holes),
                 smooth="outer" if holes else True, scale=scale, dark=dark, cap_mat=cap_mat, lines=lines)
    s = _chain_svg(compact(s))
    extra = ""
    if spec:
        q = _spec(cam, O, a, r, h, r1, wdeg or math.radians(5.5 if r * cam.s > 12 else 8))
        if q:
            extra += path(P(q), mat + "s1")
    for f in rings:
        extra += cline(cam, add3(O, a, f * h), a, r if r1 is None else r + (r1 - r) * f)
    # streak/rings go between faces and the merged edge lines
    i = s.rfind('<path class="el"')
    s = s[:i] + extra + s[i:] if i >= 0 else s + extra
    p1 = add3(O, a, h)
    R = max(r, r1 or 0)
    lo = tuple(min(O[i], p1[i]) - (R if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (R if abs(a[i]) < .99 else 0) for i in range(3))
    return s, (lo, hi)


def MCYL(sc, O, A, r, h, mat="w", bias=0.0, **kw):
    """add a banded metal cylinder (see MCYL_svg); mat 'w' steel, 'm' machined grey, 'dk' black, 't' tool."""
    s, bb = MCYL_svg(sc.cam, O, A, r, h, mat, **kw)
    sc.add(s, bb, bias)
    return bb


def MRING(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=36, **kw):
    """metal ring (bore ri) with banded outside."""
    return MCYL(sc, O, A, ro, h, mat, bias, seg=seg, holes=[GE.circle_outline(ri, seg, seg)], **kw)


def xshell(sc, x0, L, ro, ri, a0=-90, a1=90, mat="pt", dark=1, bias=0.0, seg=20, cy=0.0, cz=0.0):
    """part of a tube along x (angles a0..a1 deg in the (y,z) plane, 0 = +y): cut-away housings/races.
    Keep the back half with a0=-90, a1=90; the cut faces lie on the plane y=cy (draw them with sect())."""
    o = []
    for k in range(seg + 1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((cy + ro * math.cos(t), cz + ro * math.sin(t), k // 3))
    for k in range(seg, -1, -1):
        t = math.radians(a0 + (a1 - a0) * k / seg)
        o.append((cy + ri * math.cos(t), cz + ri * math.sin(t), 100 + k // 3))
    loop = [(p[0], p[1], p[2]) for p in o]
    sv = GE.prism(sc.cam, (x0, 0, 0), (1, 0, 0), loop, L, mat, smooth=True, dark=dark)
    sc.add(_chain_svg(compact(sv)), ((x0, cy + min(0, ro * min(math.cos(math.radians(a)) for a in (a0, a1))), cz - ro), (x0 + L, cy + ro, cz + ro)), bias)


def sect(sc, rects, bb, bias=0.0, y=0.0):
    """section faces on the cut plane y: rects [(x0, x1, z0, z1, cls)] drawn flat (cls 'cut' for metal,
    'fl' coolant, 'ball' rolling elements, 'dks4' deep gaps). bb: bbox for ordering."""
    def f(s_):
        o = ""
        for x0, x1, z0, z1, c in rects:
            if c == "ball":
                cx, cz, r = (x0 + x1) / 2, (z0 + z1) / 2, min(x1 - x0, z1 - z0) / 2
                o += path(P(circ3(s_.cam, (cx, y, cz), (0, 1, 0), r, 16)), c)
            else:
                o += path(P([s_.cam.xy(p) for p in ((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1))]), c)
        return o
    sc.add(f, bb, bias)


def cline(cam, C, A, r, cls="gr", seg=36):
    """visible half of a circle on a cylinder surface (shoulder, groove, joint line)."""
    E1, E2, a = GE.frame(A)
    out, run = "", []
    for k in range(seg + 1):
        t = 2 * math.pi * k / seg
        nr = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
        if GE._dot(nr, cam.D) < 0:
            run.append(cam.xy(tuple(C[i] + r * nr[i] for i in range(3))))
        else:
            if len(run) > 1:
                out += P(run, False)
            run = []
    if len(run) > 1:
        out += P(run, False)
    return path(out, cls) if out else ""


def helix(cam, O, A, r, L, pitch, cls="thread", per=8):
    """visible strokes of a thread helix on a cylinder (ball screw, lead screw)."""
    E1, E2, a = GE.frame(A)
    out, run = "", []
    N = int(L / pitch * per)
    for k in range(N + 1):
        s = L * k / N
        t = 2 * math.pi * s / pitch
        nr = tuple(math.cos(t) * E1[i] + math.sin(t) * E2[i] for i in range(3))
        if GE._dot(nr, cam.D) < -0.1:
            run.append(cam.xy(tuple(O[i] + a[i] * s + r * nr[i] for i in range(3))))
        else:
            if len(run) > 1:
                out += P(run, False)
            run = []
    if len(run) > 1:
        out += P(run, False)
    return path(out, cls)


def finmotor(sc, O, A, r, L, nf=18, fin=None, mat="dk", bias=0.0, cap=True):
    """cooling-fin motor (spindle / pump motor): finned body along A from O, plain end cap and shaft boss."""
    a = V(A)
    f = fin or r * 0.16
    out = []
    for k in range(nf * 2):
        t0 = 2 * math.pi * k / (nf * 2)
        rr_ = r if k % 2 == 0 else r - f
        for j in (0.15, 0.85):
            t = t0 + j * 2 * math.pi / (nf * 2)
            out.append((rr_ * math.cos(t), rr_ * math.sin(t), k))
    s = compact(GE.prism(sc.cam, O, a, out, L * .82, mat, dark=0))
    p1 = add3(O, a, L * .82)
    sc.add(s, _cbb(O, a, r, L * .82), bias)
    if cap:
        MCYL(sc, p1, a, r * .9, L * .18, mat, bias, dark=1, seg=28)


def _cbb(O, a, r, h):
    p1 = add3(O, a, h)
    lo = tuple(min(O[i], p1[i]) - (r if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (r if abs(a[i]) < .99 else 0) for i in range(3))
    return lo, hi


def radial(sc, axis, t0, L, C2, ang, r0, r1, w, mat="w", b=1.0, dark=1, bias=0.0):
    """block standing radially on a disc/face: in the cross-section of axis, centred on C2=(u,v), at angle
    ang (deg, from +u toward +v), from radius r0 to r1, width w; extruded t0..t0+L (chuck jaws, turret holders)."""
    c, s_ = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    uv = [(C2[0] + p * c - q * s_, C2[1] + p * s_ + q * c) for p, q in ((r0, -w / 2), (r1, -w / 2), (r1, w / 2), (r0, w / 2))]
    return cprism(sc, axis, t0, L, uv, mat, b, b, dark, bias)


# ------------------------------------------------------------------ local frames for rails/screws on any face
def _frame(ax, nm):
    a, m = V(ax), V(nm)
    s = GE._cross(m, a)
    return a, m, s


def _sec(P0, a, m, s, axis_len, pts2):
    """local (side, normal) section points -> (axis char, t0, L, uv) for cprism along a."""
    c, sg = _ax_char(a)
    iu, iv = _UV[c]
    it = _IDX[c]
    uv = []
    for sd, nn in pts2:
        q = lin(P0, (sd, s), (nn, m))
        uv.append((q[iu], q[iv]))
    t0 = P0[it] if sg > 0 else P0[it] - axis_len
    return c, t0, axis_len, uv


def rail_svg(cam, P0, ax, L, nm="z", w=14, h=11, mat="w", carriages=(), cw=None, ch=None, cmat="w", smat="dk", pitch=None):
    """linear-guide rail from P0 along ax (length L) standing on a face with normal nm, plus carriages
    [(pos, length)] with dark end seals and counterbored bolt holes on the rail top -> (svg, bbox)."""
    a, m, s = _frame(ax, nm)
    c = w * .14
    sec = [(-w / 2, 0), (w / 2, 0), (w / 2, h - c), (w / 2 - c, h), (-w / 2 + c, h), (-w / 2, h - c)]
    k, t0, LL, uv = _sec(P0, a, m, s, L, sec)
    out, bb = cprism_svg(cam, k, t0, LL, uv, mat, 0, 0, 1)
    pitch = pitch or w * 2.6
    hs = ""
    for i in range(int(L / pitch)):
        C = lin(P0, ((i + .5) * pitch + (L % pitch) / 2, a), (h + .1, m))
        hs += P(circ3(cam, C, m, w * .2, 8))
    out += path(hs, "bg")
    out += poly3(cam, [lin(P0, (0, a), (w / 2 + .1, s), (h * .55, m)), lin(P0, (L, a), (w / 2 + .1, s), (h * .55, m))], "gr", False) \
        + poly3(cam, [lin(P0, (0, a), (-w / 2 - .1, s), (h * .55, m)), lin(P0, (L, a), (-w / 2 - .1, s), (h * .55, m))], "gr", False)
    cw, ch = cw or w * 2.3, ch or h * 1.05
    parts, bbs = [], [bb]
    for pos, cl in carriages:
        csec = [(-cw / 2, h * .3), (cw / 2, h * .3), (cw / 2, h + ch * .45), (cw / 2 - ch * .25, h + ch * .7), (-cw / 2 + ch * .25, h + ch * .7), (-cw / 2, h + ch * .45)]
        k2, t2, L2, uv2 = _sec(lin(P0, (pos, a)) if _ax_char(ax)[1] > 0 else lin(P0, (pos + cl, a)), a, m, s, cl, csec)
        sv, b2 = cprism_svg(cam, k2, t2, L2, uv2, cmat, 0, 0, 1, fmat={0: smat, 1: smat})   # end faces = dark seals
        cen = tuple((b2[0][i] + b2[1][i]) / 2 for i in range(3))
        parts.append((cam.P(cen)[2], sv))
        bbs.append(b2)
    for _, sv in sorted(parts, key=lambda q: -q[0]):
        out += sv
    return out, bbu(*bbs)


def rail(sc, P0, ax, L, nm="z", bias=0.0, **kw):
    """add a linear-guide rail (+carriages) as one ordered item; see rail_svg."""
    s, bb = rail_svg(sc.cam, P0, ax, L, nm, **kw)
    sc.add(s, bb, bias)
    return bb


def ballscrew(sc, P0, ax, L, r=6, nut=None, nut_len=None, supports=True, sup=None, nm="z", pitch=None, bias=0.0, smat="pt"):
    """ball screw from P0 along ax: banded shaft with helix, flanged nut at distance `nut`, bearing support
    blocks at both ends standing on the face with normal nm. One ordered item."""
    cam = sc.cam
    a, m, s = _frame(ax, nm)
    pitch = pitch or r * 2
    items = []
    sv, bb = MCYL_svg(cam, P0, a, r, L, "w", seg=20, bands=8, dark=1)
    sv += helix(cam, P0, a, r, L, pitch)
    bbs = [bb]
    items.append((None, sv))
    if nut is not None:
        nl = nut_len or r * 5
        for p0, ln, rad, mt_, dk in ((nut, nl * .22, r * 2.5, "w", 1), (nut + nl * .22, nl * .78, r * 1.75, "w", 1)):
            sv2, b2 = MCYL_svg(cam, lin(P0, (p0, a)), a, rad, ln, mt_, seg=24, bands=10, dark=dk, rings=(.5,) if ln > nl * .5 else ())
            cen = tuple((b2[0][i] + b2[1][i]) / 2 for i in range(3))
            items.append((cam.P(cen)[2], sv2))
            bbs.append(b2)
    sups = []
    if supports:
        sw = sup or r * 3.2
        sec = rr(-r * 2.6, -r * 2.2, r * 2.6, r * 2.2, r * .5)
        for p0 in (0, L):
            c, t0, LL, uv = _sec(lin(P0, (p0 - sw / 2, a)) if _ax_char(a)[1] > 0 else lin(P0, (p0 + sw / 2, a)), a, m, s, sw, sec)
            sv3, b3 = cprism_svg(cam, c, t0, LL, uv, smat, r * .25, r * .25, 1)
            cen = tuple((b3[0][i] + b3[1][i]) / 2 for i in range(3))
            sups.append((cam.P(cen)[2], sv3))
            bbs.append(b3)
    sups.sort(key=lambda q: -q[0])
    nuts = sorted([it for it in items if it[0] is not None], key=lambda q: -q[0])
    out = (sups[0][1] if sups else "") + items[0][1] + "".join(v for _, v in nuts) + (sups[1][1] if len(sups) > 1 else "")
    sc.add(out, bbu(*bbs), bias)


def servo(sc, P0, ax, s=36, L=60, mat="dk", bias=0.0, up="z", flange=True):
    """AC servo motor: square flange at P0, chamfered square body along ax, stepped encoder cap and a
    connector box on the `up` side. Separate solids abutting along ax (scene orders them)."""
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
        lo2 = tuple(min(lo[i], hi[i]) for i in range(3))
        hi2 = tuple(max(lo[i], hi[i]) for i in range(3))
        abox(sc, lo2, hi2, m_, c, chm, bb_, dark=dk, bias=bias)
    if flange:
        seg(0, fl, s * .6, s * .1, 0)
    seg(fl, L * .66, s / 2, s * .16, 0)
    seg(fl + L * .66, L * .34 - fl, s * .42, s * .14, 1, bb_=2.5)
    # connector box on the up side of the body
    cx = add3(P0, a, fl + L * .42)
    lo = add3(add3(cx, u, s / 2), a, -s * .12)
    lo = tuple(lo[i] - (s * .14 if i != it and abs(u[i]) < .5 else 0) for i in range(3))
    hi = add3(add3(cx, u, s / 2 + s * .16), a, s * .12)
    hi = tuple(hi[i] + (s * .14 if i != it and abs(u[i]) < .5 else 0) for i in range(3))
    abox(sc, tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3)), mat, c, 0, .8, dark=0, bias=bias - .5)


# ------------------------------------------------------------------ sheet metal: covers, bellows, cable chain
def tcover(sc, P0, ax, L, w, h, segs=4, step=2.0, nm="z", mat="w", bias=0.0, grow=1):
    """telescopic way cover from P0 along ax: `segs` nested sheet-steel shells with sloped shoulders,
    each `step` larger than the last (grow=-1 -> largest at P0)."""
    a, m, s = _frame(ax, nm)
    Ls = L / segs
    for k in range(segs):
        g = step * (k if grow > 0 else segs - 1 - k)
        ww, hh = w / 2 + g, h + g
        sec = [(-ww, 0), (ww, 0), (ww, hh * .62), (ww - ww * .22, hh), (-ww + ww * .22, hh), (-ww, hh * .62)]
        c, t0, LL, uv = _sec(lin(P0, (k * Ls, a)) if _ax_char(a)[1] > 0 else lin(P0, ((k + 1) * Ls, a)), a, m, s, Ls, sec)
        bl = (0.0, 1.2) if grow > 0 else (1.2, 0.0)
        if _ax_char(a)[1] < 0:
            bl = bl[::-1]
        cprism(sc, c, t0, LL, uv, mat, bl[0], bl[1], dark=1, bias=bias)


def bellows(sc, lo, hi, axis="z", folds=12, mat="dk", bias=0.0):
    """accordion bellows cover in box lo..hi, folds across `axis` (light fold lines on a dark box)."""
    s, bb = abox_svg(sc.cam, lo, hi, mat, axis, 0, 0, dark=0)
    it = _IDX[axis]
    ln = ""
    for k in range(1, folds):
        t = lo[it] + (hi[it] - lo[it]) * k / folds
        if axis == "z":
            q = [(lo[0], lo[1], t), (hi[0], lo[1], t), (hi[0], hi[1], t)]
        elif axis == "y":
            q = [(lo[0], t, hi[2]), (hi[0], t, hi[2]), (hi[0], t, lo[2])]
        else:
            q = [(t, hi[1], hi[2]), (t, lo[1], hi[2]), (t, lo[1], lo[2])]
        ln += P([sc.cam.xy(p_) for p_ in q], False)
    sc.add(s + path(ln, "mgrid"), bb, bias)


def cablechain(sc, P0, ax, up, L_top, L_bot, R, w, th=None, mat="dk", bias=0.0):
    """cable carrier: bend of radius R centred at P0 in the plane (ax, up), upper run L_top and lower run
    L_bot along +ax, width w toward +y side; links shown by light separators."""
    cam = sc.cam
    a, u = V(ax), V(up)
    sd = GE._cross(u, a)
    th = th or R * .32
    cen = []
    for k in range(13):
        t = math.pi / 2 + math.pi * k / 12
        cen.append((math.cos(t), math.sin(t)))
    # centre line param: upper run (from far end to bend), bend, lower run
    def pt(c2, rad, off=0.0):
        return lin(P0, (c2[0] * rad, a), (c2[1] * rad, u), (off, sd))
    outer, inner = [], []
    outer.append(lin(P0, (L_top, a), (R, u)))
    inner.append(lin(P0, (L_top, a), (R - th, u)))
    for c2 in cen:
        outer.append(pt(c2, R))
        inner.append(pt(c2, R - th))
    outer.append(lin(P0, (L_bot, a), (-R, u)))
    inner.append(lin(P0, (L_bot, a), (-R + th, u)))
    # which side face is visible
    sgn = -1 if GE._dot(sd, cam.D) > 0 else 1
    off = 0 if sgn < 0 else w
    O_ = [lin(p, (off, sd)) for p in outer]
    I_ = [lin(p, (off, sd)) for p in inner]
    top = [lin(P0, (L_top, a), (R, u)), lin(P0, (0, a), (R, u)), lin(P0, (0, a), (R, u), (w, sd)), lin(P0, (L_top, a), (R, u), (w, sd))]
    out = poly3(cam, top, mat + "s2") + poly3(cam, O_ + I_[::-1], mat + "s3")
    ln = ""
    nl = int(L_top / (th * 1.1))
    for k in range(1, nl):
        f = k / nl
        ln += P([cam.xy(lin(O_[0], (-f * L_top, a))), cam.xy(lin(I_[0], (-f * L_top, a)))], False)
        ln += P([cam.xy(lin(top[0], (-f * L_top, a))), cam.xy(lin(top[3], (-f * L_top, a)))], False)
    for k in range(1, 13):
        ln += P([cam.xy(O_[k]), cam.xy(I_[k])], False)
    nb = int(L_bot / (th * 1.1))
    for k in range(1, nb):
        f = k / nb
        ln += P([cam.xy(lin(O_[-1], (-f * L_bot, a))), cam.xy(lin(I_[-1], (-f * L_bot, a)))], False)
    out += path(ln, "mgrid") + poly3(cam, O_ + I_[::-1], "el")
    pts_ = outer + inner + [lin(p, (w, sd)) for p in outer]
    sc.add(out, bbox(pts_), bias)


# ------------------------------------------------------------------ face details
def bolts(sc, centers, A, r=3.0, h=None, bias=-0.5):
    """row of socket-head cap screws standing on a face with normal A (steel head + dark hex socket)."""
    a = V(A)
    h = r * .7 if h is None else h

    def f(s_):
        cam, o = s_.cam, ""
        seg = 10 if r * cam.s < 4 else 14
        for C in sorted(centers, key=lambda p: -cam.P(p)[2]):
            o += path(P(circ3(cam, C, a, r, seg)), "ws4")
            o += path(P(circ3(cam, add3(C, a, h), a, r, seg)), "ws2")
            E1, E2, _ = GE.frame(a)
            hx = [cam.xy(tuple(C[i] + a[i] * (h + .05) + r * .48 * (math.cos(k * math.pi / 3) * E1[i] + math.sin(k * math.pi / 3) * E2[i]) for i in range(3))) for k in range(6)]
            o += path(P(hx), "bg")
        return o
    ps = [add3(c, a, h) for c in centers] + list(centers)
    lo, hi = bbox(ps)
    lo = tuple(lo[i] - (r if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(hi[i] + (r if abs(a[i]) < .99 else 0) for i in range(3))
    sc.add(f, (lo, hi), bias)


def holes(sc, centers, A, r, cls="bg", bias=-0.5):
    """dark holes / tapped holes flush on a face with normal A."""
    a = V(A)

    def f(s_):
        return path("".join(P(circ3(s_.cam, C, a, r, 12)) for C in centers), cls)
    lo, hi = bbox(centers)
    sc.add(f, (tuple(lo[i] - (r if abs(a[i]) < .99 else 0) for i in range(3)),
               tuple(hi[i] + (r if abs(a[i]) < .99 else 0) for i in range(3))), bias)


def ring_pts(C, A, r, k, phase=0.0):
    """k points evenly on a circle (bolt circle) around axis A."""
    E1, E2, _ = GE.frame(V(A))
    return [tuple(C[i] + r * (math.cos(phase + 2 * math.pi * j / k) * E1[i] + math.sin(phase + 2 * math.pi * j / k) * E2[i]) for i in range(3)) for j in range(k)]


def seams(sc, segs, bb, cls="gr", bias=-0.5):
    """panel joints / cover seams: list of 3D polylines drawn as thin lines over the face bbox bb."""
    def f(s_):
        return path("".join(P([s_.cam.xy(p) for p in pl], False) for pl in segs), cls)
    sc.add(f, bb, bias)


def panel(sc, x, y, z, w, d, h, mat="dk", bias=0.0):
    """CNC operation panel: dark cabinet with screen, soft keys, key pad, MPG and e-stop on its -y face."""
    block(sc, x, y, z, w, d, h, mat, ch=min(w, d) * .08, b=1.5, dark=0, bias=bias)

    def f(s_):
        cam = s_.cam
        yy = y - .2

        def q(u0, v0, u1, v1):
            return [cam.xy((x + u0 * w, yy, z + v0 * h)), cam.xy((x + u1 * w, yy, z + v0 * h)),
                    cam.xy((x + u1 * w, yy, z + v1 * h)), cam.xy((x + u0 * w, yy, z + v1 * h))]
        o = path(P(q(.08, .5, .92, .92)), "scrn")
        o += path(P(q(.14, .78, .6, .84)) + P(q(.14, .66, .48, .71)) + P(q(.14, .56, .7, .6)), "scrl")
        kb = ""
        for i in range(5):
            for j in range(3):
                kb += P(q(.1 + i * .12, .12 + j * .1, .18 + i * .12, .19 + j * .1))
        o += path(kb, "kbtn")
        c = cam.xy((x + .8 * w, yy, z + .3 * h))
        rr_ = w * .1 * cam.s
        o += '<ellipse class="mpg" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(c[0]), n(c[1]), n(rr_), n(rr_ * 1.1))
        c = cam.xy((x + .8 * w, yy, z + .12 * h))
        o += '<circle class="estop" cx="%s" cy="%s" r="%s"/>' % (n(c[0]), n(c[1]), n(max(1.5, w * .055 * cam.s)))
        return o
    sc.add(f, ((x, y - .5, z), (x + w, y, z + h)), bias - 1)


__all__ = [k for k in dir() if not k.startswith("__")]
