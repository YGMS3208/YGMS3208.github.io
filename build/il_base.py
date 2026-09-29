"""SVG drawing helpers for the process atlas illustrations.
All drawings use viewBox 0 0 320 200 and theme classes defined in the page CSS:
 o  outline only          m/m2/m3  machine greys (light→dark)
 w/w2/w3  workpiece tones  t  tool (accent tint)   h/hl  hot fill / hot line
 fl/fo fluid fill / line  a/af accent arrow line / head   sh shadow   d dark fill
"""
import math

W, H = 320, 200


def n(v):
    s = "%.1f" % v
    return s[:-2] if s.endswith(".0") else s


def pts(ps):
    return " ".join(n(x) + "," + n(y) for x, y in ps)


def path(d, c="o", extra=""):
    return '<path class="%s" d="%s"%s/>' % (c, d, extra)


def rect(x, y, w, h, c="m", rx=0):
    r = ' rx="%s"' % n(rx) if rx else ""
    return '<rect class="%s" x="%s" y="%s" width="%s" height="%s"%s/>' % (c, n(x), n(y), n(w), n(h), r)


def ell(cx, cy, rx, ry, c="w"):
    return '<ellipse class="%s" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (c, n(cx), n(cy), n(rx), n(ry))


def circ(cx, cy, r, c="w"):
    return '<circle class="%s" cx="%s" cy="%s" r="%s"/>' % (c, n(cx), n(cy), n(r))


def line(x1, y1, x2, y2, c="o"):
    return '<line class="%s" x1="%s" y1="%s" x2="%s" y2="%s"/>' % (c, n(x1), n(y1), n(x2), n(y2))


def poly(ps, c="w"):
    return '<polygon class="%s" points="%s"/>' % (c, pts(ps))


def pline(ps, c="o"):
    return '<polyline class="%s" points="%s"/>' % (c, pts(ps))


def text(x, y, s, a="middle", c=""):
    cl = ' class="%s"' % c if c else ""
    return '<text x="%s" y="%s" text-anchor="%s"%s>%s</text>' % (n(x), n(y), a, cl, s)


def head(x, y, ang, s=7):
    """arrow head with tip at (x,y) pointing along ang (radians)."""
    a1, a2 = ang + math.pi * 0.83, ang - math.pi * 0.83
    return poly([(x, y), (x + s * math.cos(a1), y + s * math.sin(a1)), (x + s * math.cos(a2), y + s * math.sin(a2))], "af")


def arrow(x1, y1, x2, y2, label=None, lx=None, ly=None, anchor="middle", both=False, c="a"):
    ang = math.atan2(y2 - y1, x2 - x1)
    s = line(x1, y1, x2 - 4 * math.cos(ang), y2 - 4 * math.sin(ang), c) + head(x2, y2, ang)
    if both:
        s += head(x1, y1, ang + math.pi)
    if label:
        if lx is None:
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 - 6
        s += text(lx, ly, label, anchor, "al")
    return s


def rot(cx, cy, rx, ry, a0, a1, label=None, lx=None, ly=None, anchor="middle"):
    """elliptical arc arrow from angle a0 to a1 (degrees, screen coords, cw positive)."""
    r0, r1 = math.radians(a0), math.radians(a1)
    x0, y0 = cx + rx * math.cos(r0), cy + ry * math.sin(r0)
    x1, y1 = cx + rx * math.cos(r1), cy + ry * math.sin(r1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    d = "M%s %s A%s %s 0 %d %d %s %s" % (n(x0), n(y0), n(rx), n(ry), large, sweep, n(x1), n(y1))
    # tangent direction at end
    tx, ty = -rx * math.sin(r1), ry * math.cos(r1)
    if sweep == 0:
        tx, ty = -tx, -ty
    s = path(d, "a") + head(x1 + tx * 0.02, y1 + ty * 0.02, math.atan2(ty, tx))
    if label:
        s += text(lx, ly, label, anchor, "al")
    return s


def gear_d(cx, cy, rr, rt, z, phase=0.0, tw=0.42, sy=1.0):
    """involute gear outline path. rr root radius, rt tip radius (rt < rr gives internal teeth).
    sy squashes vertically for oblique views. tw is kept for call compatibility."""
    import il_gear as G
    if rt >= rr:
        rp = rr + (rt - rr) * 1.25 / 2.25
        pts = G.gear_outline(z, rp, rt, rr, phase)
    else:
        rp = (rr + rt) / 2
        pts = G.gear_outline(z, rp, rr, rt, phase + math.pi / z, fillet=False)
    return G.outline_d(pts, cx, cy, sy)


def gear(cx, cy, rr, rt, z, c="w", phase=0.0, sy=1.0, tw=0.42):
    return path(gear_d(cx, cy, rr, rt, z, phase, tw, sy), c)


def gear3d(cx, cy, rr, rt, z, dx=6, dy=-5, bore=0, c="w", c2="w2", phase=0.0, sy=1.0, tw=0.42, helix=0.0):
    """shaded 3D gear seen nearly face-on; (dx,dy) is the screen offset of the back face."""
    import il_gear as G
    el = 22.0
    se = math.sin(math.radians(el))
    h = math.sqrt(dx * dx + (dy / se) ** 2) or 1.0
    az = math.degrees(math.atan2(-dx / h, -dy / (h * se)))
    cam = G.Cam(cx, cy, az, el, 1.0)
    rp = rr + (rt - rr) * 1.25 / 2.25
    mat = "t" if c == "t" else ("gw" if c == "gw" else "w")
    holes = [G.circle_outline(bore, 40, 40)] if bore else []
    # visible cap lies in the plane y=0 so the face centre lands on (cx, cy)
    return G.prism(cam, (0, h, 0), (0, -1, 0), G.gear_outline(z, rp, rt, rr, phase + math.pi / 2), h, mat, holes=holes,
                   twist=(h * math.tan(math.radians(helix)) / rp if helix else 0.0), slices=1 if not helix else 3)


def shaft(x, cy, segs, c="w", fc="w2", k=0.32):
    """oblique horizontal shaft. segs = [(length, radius), ...]; right end faces visible."""
    out = []
    for ln, r in segs:
        e = r * k
        d = "M%s %s L%s %s A%s %s 0 0 1 %s %s L%s %s A%s %s 0 0 1 %s %sZ" % (
            n(x), n(cy - r), n(x + ln), n(cy - r), n(e), n(r), n(x + ln), n(cy + r), n(x), n(cy + r), n(e), n(r), n(x), n(cy - r))
        out.append(path(d, c))
        out.append(ell(x + ln, cy, e, r, fc))
        x += ln
    return "".join(out)


def vcyl(cx, top, h, rx, ry, c="w", tc="w2"):
    """vertical cylinder seen from above-front; top ellipse visible."""
    d = "M%s %s L%s %s A%s %s 0 0 0 %s %s L%s %sZ" % (
        n(cx - rx), n(top), n(cx - rx), n(top + h), n(rx), n(ry), n(cx + rx), n(top + h), n(cx + rx), n(top))
    return path(d, c) + ell(cx, top, rx, ry, tc)


def box(x, y, w, h, d, ct="w2", cf="w", cs="w3", k=(0.62, -0.5)):
    """oblique box: front face (x,y,w,h); depth d projects up-right."""
    dx, dy = d * k[0], d * k[1]
    s = poly([(x, y), (x + w, y), (x + w + dx, y + dy), (x + dx, y + dy)], ct)
    s += poly([(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h)], cs)
    s += rect(x, y, w, h, cf)
    return s


def shadow(cx, cy, rx, ry=None):
    return ell(cx, cy, rx, ry or rx * 0.12, "sh")


def heat(x, y, cnt=3, gap=9, hgt=14):
    s = ""
    for i in range(cnt):
        xx = x + i * gap
        s += path("M%s %s c-3 -3 3 -5 0 -8 c-3 -3 3 -5 0 -8" % (n(xx), n(y)), "hl")
    return s


def flame(x, y, s=1.0):
    return path("M%s %s c-%s -%s %s -%s %s -%s c%s %s %s %s -%s %sZ" % (
        n(x), n(y), n(6 * s), n(8 * s), n(1 * s), n(12 * s), n(2 * s), n(20 * s), n(3 * s), n(6 * s), n(9 * s), n(10 * s), n(2 * s), n(20 * s)), "h")


def sparks(x, y, r=10, cnt=6, a0=-150, a1=-30):
    s = ""
    for i in range(cnt):
        a = math.radians(a0 + (a1 - a0) * i / max(cnt - 1, 1))
        s += line(x + 3 * math.cos(a), y + 3 * math.sin(a), x + r * math.cos(a), y + r * math.sin(a), "hl")
    return s


def drops(x, y, cnt=5, spread=40, length=26, ang=90):
    s = ""
    for i in range(cnt):
        a = math.radians(ang - spread / 2 + spread * i / max(cnt - 1, 1))
        for t in (0.35, 0.7, 1.0):
            s += circ(x + length * t * math.cos(a), y + length * t * math.sin(a), 1.4, "fdot")
    return s


def spray_cone(x, y, ang, spread=36, length=40, c="fo"):
    a1, a2 = math.radians(ang - spread / 2), math.radians(ang + spread / 2)
    return path("M%s %s L%s %s M%s %s L%s %s" % (n(x), n(y), n(x + length * math.cos(a1)), n(y + length * math.sin(a1)),
                                                 n(x), n(y), n(x + length * math.cos(a2)), n(y + length * math.sin(a2))), c + " dash")


def coil(x1, x2, cy, r, turns, c="w", k=0.35):
    """side view helical spring between x1 and x2."""
    pitch = (x2 - x1) / turns
    s = ""
    for i in range(turns):
        xa = x1 + i * pitch
        # back half (thin)
        s += path("M%s %s Q%s %s %s %s" % (n(xa + pitch * 0.5), n(cy - r), n(xa + pitch * 0.25), n(cy), n(xa), n(cy + r)), "o thin")
    for i in range(turns):
        xa = x1 + i * pitch
        s += path("M%s %s Q%s %s %s %s" % (n(xa), n(cy + r), n(xa + pitch * 0.75), n(cy), n(xa + pitch * 0.5), n(cy - r)), "wire")
        s += path("M%s %s Q%s %s %s %s" % (n(xa + pitch * 0.5), n(cy - r), n(xa + pitch * 1.25), n(cy), n(xa + pitch), n(cy + r)), "o thin")
    return s


def car_d(x, y, s=1.0, kind="sedan"):
    """side silhouette of a car; (x,y) = front-bottom-left origin at ground left, length ~200*s."""
    def P(px, py):
        return n(x + px * s) + " " + n(y + py * s)
    if kind == "hatch":
        pts_ = [(0, -18), (2, -30), (14, -36), (52, -42), (78, -66), (140, -68), (172, -52), (182, -46), (184, -20), (182, -12),
                (160, -12)]
    else:
        pts_ = [(0, -18), (2, -30), (14, -36), (54, -42), (80, -64), (130, -66), (156, -46), (190, -42), (198, -34), (198, -18),
                (194, -12), (170, -12)]
    d = "M" + P(*pts_[0])
    for p in pts_[1:]:
        d += " L" + P(*p)
    # rear wheel arch
    rear = 150 if kind == "hatch" else 160
    d += " A%s %s 0 0 0 %s" % (n(18 * s), n(18 * s), P(rear - 34, -12))
    d += " L" + P(52, -12)
    d += " A%s %s 0 0 0 %s" % (n(18 * s), n(18 * s), P(18, -12))
    d += " L" + P(4, -12) + "Z"
    return d


def car(x, y, s=1.0, c="w", kind="sedan", wheels=True, windows=True):
    out = path(car_d(x, y, s, kind), c)
    rear = (150 if kind == "hatch" else 160) - 17
    if windows:
        if kind == "hatch":
            wp = [(58, -44), (80, -62), (136, -63), (160, -48)]
        else:
            wp = [(60, -44), (82, -60), (126, -61), (146, -46)]
        out += poly([(x + a * s, y + b * s) for a, b in wp], "gl")
        mid = (wp[1][0] + wp[2][0]) / 2
        out += line(x + mid * s, y + (wp[1][1] - 1) * s, x + mid * s, y + (wp[0][1]) * s, "o")
    if wheels:
        for wx in (35, rear):
            out += circ(x + wx * s, y - 12 * s, 14 * s, "m3") + circ(x + wx * s, y - 12 * s, 7 * s, "m")
    return out


def robot(bx, by, s=1.0, a1=-60, a2=40, tool=None, c="m"):
    """simple 2-link robot arm from base (bx,by). returns (svg, (tx,ty))."""
    out = rect(bx - 16 * s, by - 8 * s, 32 * s, 8 * s, "m2")
    out += rect(bx - 9 * s, by - 20 * s, 18 * s, 12 * s, c)
    jx, jy = bx, by - 20 * s
    l1, l2 = 46 * s, 40 * s
    r1 = math.radians(a1)
    ex, ey = jx + l1 * math.cos(r1), jy + l1 * math.sin(r1)
    r2 = math.radians(a1 + a2)
    tx, ty = ex + l2 * math.cos(r2), ey + l2 * math.sin(r2)
    out += path("M%s %s L%s %s" % (n(jx), n(jy), n(ex), n(ey)), "arm")
    out += path("M%s %s L%s %s" % (n(ex), n(ey), n(tx), n(ty)), "arm2")
    out += circ(jx, jy, 6 * s, "m2") + circ(ex, ey, 5 * s, "m2")
    return out, (tx, ty)


def svg(body, label):
    return '<svg class="ilu" viewBox="0 0 320 200" role="img" aria-label="%s">%s</svg>' % (label, body)
