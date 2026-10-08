"""Shared helpers for the v3 shaded-3D drawings (il3_*.py). Registers no keys.

Built on il_gear (Cam / prism: orthographic projection, back-face culling, 4-step shading
<mat>s1..s4) and il_mt.Scene (bounding-box ordering of many solids).

Typical part drawing:
    def fn(sc):                       # sc is an il_mt.Scene; sc.cam is the il_gear.Cam
        CYL(sc, (0, 0, 0), (1, 0, 0), 20, 40)          # add solids to the scene ...
        return extra_svg                               # ... and/or return svg drawn on top
    return fit(fn, az=-30, el=24)                      # probe -> scale/centre into the canvas
"""
import math
import re
import il_gear as GE
from il_base import n, shadow, path
from il_mt import Scene

PI = math.pi
_ML = re.compile(r'[ML](-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)')


# ------------------------------------------------------------------ fitting
def svg_extent(svg):
    """screen bbox of every M/L point in the engine's paths (exact, unlike Scene.extent's bbox corners)."""
    xs, ys = [], []
    for a, b in _ML.findall(svg):
        xs.append(float(a))
        ys.append(float(b))
    return min(xs), min(ys), max(xs), max(ys)


def fit(fn, az, el, area=(30, 18, 290, 174), sh=True, sh_ry=8, sh_k=0.5, sh_dy=-3, ret_scene=False):
    """Draw fn(scene) twice: once with a unit camera to measure, then scaled+centred into area
    (x0, y0, x1, y1). fn may add Scene items and/or return svg drawn on top of the scene.
    A soft ground shadow is put under the drawing's bottom edge (sh_k: width fraction)."""
    pr = Scene(0, 0, az, el, 1.0)
    extra = fn(pr) or ""
    body, _ = pr.render(shadow_=False)
    x0, y0, x1, y1 = svg_extent(body + extra)
    L, T, R, B = area
    k = min((R - L) / (x1 - x0), (B - T) / (y1 - y0))
    ox = L + ((R - L) - (x1 - x0) * k) / 2 - x0 * k
    oy = T + ((B - T) - (y1 - y0) * k) / 2 - y0 * k
    sc = Scene(ox, oy, az, el, k)
    sc.k = k
    extra = fn(sc) or ""
    body, _ = sc.render(shadow_=False)
    out = ""
    if sh:
        ex = svg_extent(body + extra)
        out = shadow((ex[0] + ex[2]) / 2, ex[3] + sh_dy, (ex[2] - ex[0]) * sh_k, sh_ry)
    out += body + extra
    return (out, sc) if ret_scene else out


# ------------------------------------------------------------------ solids added to a Scene
_EL = re.compile(r'<path class="(el|gr)" d="([^"]*)"/>')


def compact(svg):
    """merge one solid's edge-line paths into a single path drawn after its faces (saves ~30% bytes).
    Safe for a single convex-ish prism, whose side strips never overlap each other."""
    ds = {"el": [], "gr": []}

    def keep(m):
        ds[m.group(1)].append(m.group(2))
        return ""
    body = _EL.sub(keep, svg)
    # caps come last in prism output; put the lines before the caps' fill would hide them -> after everything
    return body + "".join('<path class="%s" d="%s"/>' % (c, "".join(v)) for c, v in ds.items() if v)


def _bb(O, a, r, h):
    p1 = tuple(O[i] + a[i] * h for i in range(3))
    lo = tuple(min(O[i], p1[i]) - (r if abs(a[i]) < .99 else 0) for i in range(3))
    hi = tuple(max(O[i], p1[i]) + (r if abs(a[i]) < .99 else 0) for i in range(3))
    return lo, hi


def CYL(sc, O, A, r, h, mat="w", bias=0.0, seg=24, r1=None, holes=(), dark=0, cap_mat=None, bands=12, **kw):
    """smooth-shaded cylinder (or frustum when r1 is given) from O along A."""
    a = GE._norm(A)
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    svg = GE.prism(sc.cam, O, a, GE.circle_outline(r, seg, bands), h, mat, holes=list(holes), smooth="outer" if holes else True,
                   scale=scale, dark=dark, cap_mat=cap_mat, **kw)
    sc.add(compact(svg), _bb(O, a, max(r, r1 or 0), h), bias)


def RING(sc, O, A, ro, ri, h, mat="w", bias=0.0, seg=40, dark=0, **kw):
    CYL(sc, O, A, ro, h, mat, bias, seg, holes=[GE.circle_outline(ri, seg, seg)], dark=dark, **kw)


def X(sc, x0, L, yz, mat="w", bias=0.0, **kw):
    """outline [(y, z[, fid]), ...] extruded along +x from x0."""
    loop = [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(yz)]
    ys, zs = [p[0] for p in yz], [p[1] for p in yz]
    sc.add(compact(GE.prism(sc.cam, (x0, 0, 0), (1, 0, 0), loop, L, mat, **kw)),
           ((min(x0, x0 + L), min(ys), min(zs)), (max(x0, x0 + L), max(ys), max(zs))), bias)


def Z(sc, z0, L, xy, mat="w", bias=0.0, **kw):
    """outline [(x, y[, fid]), ...] extruded along +z from z0."""
    loop = [(-p[1], p[0], p[2] if len(p) > 2 else i) for i, p in enumerate(xy)]
    xs, ys = [p[0] for p in xy], [p[1] for p in xy]
    sc.add(compact(GE.prism(sc.cam, (0, 0, z0), (0, 0, 1), loop, L, mat, **kw)), ((min(xs), min(ys), z0), (max(xs), max(ys), z0 + L)), bias)


def BOX(sc, x, y, z, sx, sy, sz, mat="pt", bias=0.0, ch=0, **kw):
    """axis-aligned box from corner (x, y, z); ch = vertical-edge chamfer (adds a soft lit facet)."""
    c = ch
    xy = [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)] if not c else \
        [(x + c, y), (x + sx - c, y), (x + sx, y + c), (x + sx, y + sy - c), (x + sx - c, y + sy), (x + c, y + sy), (x, y + sy - c), (x, y + c)]
    Z(sc, z, sz, xy, mat, bias, **kw)


def RAW(sc, fn, bb, bias=0.0):
    """fn(scene) -> svg, evaluated at render time with the final camera, ordered like a solid of bbox bb."""
    sc.add(fn, bb, bias)


# ------------------------------------------------------------------ outlines (2D, for prism / X / Z)
def hull(pts_):
    """convex hull (monotone chain), counter-clockwise."""
    p = sorted(set((round(x, 3), round(y, 3)) for x, y in pts_))
    if len(p) < 3:
        return p

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def banded(loop, group=3):
    """give consecutive points shared face ids -> fewer, wider shading bands on curved sides."""
    return [(p[0], p[1], i // group) for i, p in enumerate(loop)]


def arc(cx, cy, r, a0, a1, seg=12):
    """points on a circle arc, angles in degrees (CCW)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / seg)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / seg)))
            for k in range(seg + 1)]


# ------------------------------------------------------------------ surface marks (svg, drawn in screen space)
def circ3(cam, C, A, r, seg=28):
    """screen points of a 3D circle (centre C, normal A, radius r)."""
    E1, E2, _ = GE.frame(A)
    return [cam.xy(tuple(C[i] + r * (math.cos(2 * PI * k / seg) * E1[i] + math.sin(2 * PI * k / seg) * E2[i]) for i in range(3)))
            for k in range(seg)]


def P(pts_, close=True):
    return "M" + " L".join(n(x) + " " + n(y) for x, y in pts_) + ("Z" if close else "")


def hole3(cam, C, A, r, c="bg", seg=None):
    """flat dark disc on a surface: drilled hole / oil hole / bolt hole seen at an angle."""
    seg = seg or max(10, min(24, int(r * cam.s * 2)))
    return path(P(circ3(cam, C, A, r, seg)), c)


# ------------------------------------------------------------------ motion arrows in 3D (call after fit, with the final camera)
def arc3(cam, C, A, r, a0, a1, seg=20):
    """rotation arrow on a 3D circle around axis A through C, from angle a0 to a1 (deg, in GE.frame(A))."""
    from il_base import head
    E1, E2, _ = GE.frame(A)
    pts = [cam.xy(tuple(C[i] + r * (math.cos(math.radians(a0 + (a1 - a0) * k / seg)) * E1[i] +
                                     math.sin(math.radians(a0 + (a1 - a0) * k / seg)) * E2[i]) for i in range(3))) for k in range(seg + 1)]
    ang = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0])
    return path(P(pts[:-1], False), "a") + head(pts[-1][0], pts[-1][1], ang)


def arrow3(cam, p0, p1, both=False):
    from il_base import arrow
    a, b = cam.xy(p0), cam.xy(p1)
    return arrow(a[0], a[1], b[0], b[1], None, both=both)
