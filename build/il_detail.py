"""Detailed part drawings (480x300) and process-sheet style op drawings for machined parts."""
from il_base import *
from il_pictos import bubbles, tank, nozzle, dots, chart, conveyor, lightning
import math

DETAIL = {}   # part key -> (svg_body, notes[(name, note)])
OPDRAW = {}   # "sys.part.N" -> svg_body


def P(pts_, close=True):
    d = "M" + " L".join(n(x) + " " + n(y) for x, y in pts_)
    return d + ("Z" if close else "")


class Ob:
    """oblique projection of a box: width W along x, height H down, depth D back-right."""
    def __init__(self, x0, y0, W, H, D, kx=0.62, ky=-0.5):
        self.x0, self.y0, self.W, self.H, self.D, self.kx, self.ky = x0, y0, W, H, D, kx, ky

    def top(self, u, v):
        return (self.x0 + u + self.kx * v, self.y0 + self.ky * v)

    def front(self, u, h):
        return (self.x0 + u, self.y0 + h)

    def side(self, v, h):
        return (self.x0 + self.W + self.kx * v, self.y0 + h + self.ky * v)

    def circle(self, plane, a, b, r, k=40):
        f = getattr(self, plane)
        return [f(a + r * math.cos(2 * math.pi * i / k), b + r * math.sin(2 * math.pi * i / k)) for i in range(k)]

    def rect(self, plane, a, b, w, h):
        f = getattr(self, plane)
        return [f(a, b), f(a + w, b), f(a + w, b + h), f(a, b + h)]


class Pl:
    """placement of a local drawing into the 480x300 canvas."""
    def __init__(self, x, y, s=1.0):
        self.x, self.y, self.s = x, y, s

    def __call__(self, px, py):
        return (self.x + px * self.s, self.y + py * self.s)

    def g(self, body):
        return '<g transform="translate(%s %s) scale(%s)">%s</g>' % (n(self.x), n(self.y), n(self.s), body)


# ---------------------------------------------------------------- drafting marks
def loc(x, y, ang=-90, s=7):
    """locator: filled triangle, tip at (x,y) pointing along ang (deg) into the part."""
    a = math.radians(ang)
    b1, b2 = a + math.radians(150), a - math.radians(150)
    return poly([(x, y), (x + s * 1.5 * math.cos(b1), y + s * 1.5 * math.sin(b1)), (x + s * 1.5 * math.cos(b2), y + s * 1.5 * math.sin(b2))], "loc")


def clamp(x, y, ang=90, L=26):
    """clamp arrow pointing at (x,y) along ang."""
    a = math.radians(ang)
    x1, y1 = x - L * math.cos(a), y - L * math.sin(a)
    return line(x1, y1, x - 6 * math.cos(a), y - 6 * math.sin(a), "clampl") + head(x, y, a, 8).replace('class="af"', 'class="clamph"')


def lead(ax, ay, lx, ly, t, anchor="start"):
    s = circ(ax, ay, 2.2, "leadd") + line(ax, ay, lx, ly, "leadl")
    dx = 4 if anchor == "start" else (-4 if anchor == "end" else 0)
    return s + text(lx + dx, ly + 4, t, anchor)


def bal(ax, ay, bx, by, num):
    return line(ax, ay, bx, by, "leadl") + circ(ax, ay, 2.2, "leadd") + circ(bx, by, 9, "bal") + text(bx, by + 4, str(num), "middle", "balt")


def tol(x, y, t, anchor="start"):
    return text(x, y, t, anchor, "tol")


def roughen(pts_list, step=9):
    """dot texture along polylines to indicate as-cast / as-forged surfaces."""
    s = ""
    for (x1, y1), (x2, y2) in zip(pts_list, pts_list[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        k = max(1, int(L / step))
        for i in range(k):
            t = (i + 0.5) / k
            s += circ(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, 1.1, "rgh")
    return s


def cl(x1, y1, x2, y2):
    return line(x1, y1, x2, y2, "cl")


def hid(d):
    return path(d, "hid")


def mf(d):
    return path(d, "mf")


# ---------------------------------------------------------------- tools (tip at 0,0 pointing +x)
def _tool_local(kind, L, d, extra=None):
    s = ""
    if kind == "drill":
        s += rect(-L, -d / 2, L - d * 0.55, d, "t") + poly([(-d * 0.55, -d / 2), (0, 0), (-d * 0.55, d / 2)], "t")
        for x in range(int(-L + 6), int(-d * 0.6), 7):
            s += line(x, -d / 2, x + 5, d / 2, "o thin")
    elif kind == "endmill":
        s += rect(-L, -d / 2, L, d, "t")
        for x in range(int(-L * 0.55), -2, 6):
            s += line(x, -d / 2, x + 5, d / 2, "o thin")
    elif kind == "facemill":
        s += rect(-L, -9, L - 16, 18, "m3") + rect(-16, -d / 2, 16, d, "t", 2)
        for k in range(5):
            yy = -d / 2 + 4 + k * (d - 8) / 4
            s += rect(-3, yy - 3, 5, 6, "ins")
    elif kind == "boring":
        s += rect(-L, -d / 2, L, d, "t") + poly([(-2, -d / 2), (4, -d / 2 - 6), (-6, -d / 2 - 6)], "ins")
    elif kind == "reamer":
        s += rect(-L, -d / 2, L, d, "t")
        for x in range(int(-L * 0.4), -2, 4):
            s += line(x, -d / 2, x, d / 2, "o thin")
    elif kind == "tap":
        s += rect(-L, -d / 2, L, d, "t")
        for x in range(int(-L * 0.45), -2, 4):
            s += line(x, -d / 2 - 1, x + 3, d / 2 + 1, "o thin")
    elif kind == "gundrill":
        s += rect(-L, -d / 2, L, d, "t") + rect(-L, -d / 2 - 5, 30, d + 10, "m3")
    elif kind == "hone":
        s += rect(-L, -4, L - 40, 8, "m3") + rect(-40, -d / 2, 40, d, "m2", 3)
        s += rect(-34, -d / 2 - 3, 28, 5, "gw") + rect(-34, d / 2 - 2, 28, 5, "gw")
    elif kind == "nozzle":
        s += rect(-L, -d / 2, L - 8, d, "m3") + poly([(-8, -d / 2), (0, -2), (0, 2), (-8, d / 2)], "m3")
    elif kind == "spray":
        s += rect(-L, -d / 2, L, d, "m3") + rect(-12, -d / 2 - 3, 12, d + 6, "m2")
    elif kind == "turn":
        s += rect(-L, -d / 2, L - 10, d, "m3") + poly([(0, 0), (-12, -d / 2), (-12, d / 2 - 2)], "ins")
    elif kind == "probe":
        s += rect(-L, -3, L - 8, 6, "m3") + circ(-4, 0, 4, "t")
    elif kind == "gauge":
        s += rect(-L, -d / 2, L, d, "m2") + circ(-6, -d / 2, 2.5, "fdot") + circ(-6, d / 2, 2.5, "fdot")
    return s


def tool(kind, tx, ty, ang=90, L=70, d=16, spindle=True, rotarr=True, feed=True, feedlab=None, rotlab=None):
    """ang = direction the tool points (deg, screen coords). 90 = pointing down."""
    body = _tool_local(kind, L, d)
    if spindle:
        body = rect(-L - 46, -20, 46, 40, "m2", 4) + rect(-L - 10, -12, 10, 24, "m3") + body
    s = '<g transform="translate(%s %s) rotate(%s)">%s</g>' % (n(tx), n(ty), n(ang), body)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    if rotarr:
        cx, cy = tx - ux * L * 0.55, ty - uy * L * 0.55
        # rotation arrow drawn as small ellipse arc perpendicular to the axis
        r1 = d / 2 + 9
        x0, y0 = cx - px * r1, cy - py * r1
        x1, y1 = cx + px * r1, cy + py * r1
        mx, my = cx - ux * 8, cy - uy * 8
        s += path("M%s %s Q%s %s %s %s" % (n(x0), n(y0), n(mx + (mx - cx)), n(my + (my - cy)), n(x1), n(y1)), "a")
        s += head(x1, y1, math.atan2(y1 - (my + (my - cy)), x1 - (mx + (mx - cx))), 6)
        if rotlab:
            s += text(x1 + px * 8 + 2, y1 + py * 8 + 4, rotlab, "start", "al")
    if feed:
        off = d / 2 + 22
        fx0, fy0 = tx - ux * (L * 0.2 + 38) + px * off, ty - uy * (L * 0.2 + 38) + py * off
        fx1, fy1 = tx - ux * (L * 0.2) + px * off, ty - uy * (L * 0.2) + py * off
        s += arrow(fx0, fy0, fx1, fy1, None)
        if feedlab:
            s += text(fx1 + px * 10, fy1 + py * 10 + 4, feedlab, "middle", "al")
    return s


def wheel(cx, cy, r, lab=None, rot_dir=1):
    s = circ(cx, cy, r, "gw") + circ(cx, cy, r - 5, "grit") + circ(cx, cy, r * 0.3, "m2")
    s += rot(cx, cy, r + 8, r + 8, 200 if rot_dir > 0 else 340, 250 if rot_dir > 0 else 290)
    if lab:
        s += text(cx, cy - r - 12, lab, "middle", "al")
    return s


def table(x, y, w, h=12):
    return rect(x, y, w, h, "m2")


def chuck(x, cy, h=70):
    return rect(x - 30, cy - h / 2 - 10, 30, h + 20, "m2", 3) + rect(x, cy - h / 2, 12, 14, "m3") + rect(x, cy + h / 2 - 14, 12, 14, "m3")


def center(x, cy, right=True):
    if right:
        return poly([(x, cy), (x + 20, cy - 10), (x + 20, cy + 10)], "m2") + rect(x + 20, cy - 16, 30, 32, "m2", 3)
    return poly([(x, cy), (x - 20, cy - 10), (x - 20, cy + 10)], "m2") + rect(x - 50, cy - 16, 30, 32, "m2", 3)


def coolant(x, y, ang, L=26):
    a = math.radians(ang)
    s = ""
    for k in (-1, 0, 1):
        b = a + math.radians(10 * k)
        s += line(x, y, x + L * math.cos(b), y + L * math.sin(b), "cool")
    return s


def title(t):
    return "<!--T-->" + rect(0, 0, 480, 28, "tbg") + line(0, 28, 480, 28, "tbl") + text(12, 19, t, "start", "ttl") + "<!--/T-->"


def fin(s):
    """move the title band to the end so it sits above tools that reach the top edge."""
    import re
    m = re.search(r"<!--T-->(.*?)<!--/T-->", s, re.S)
    if m:
        s = s.replace(m.group(0), "") + m.group(1)
    return s


def svgD(body, label):
    return '<svg class="ilu" viewBox="0 0 480 300" role="img" aria-label="%s">%s</svg>' % (label, body)


# ================================================================ revolved parts (turned / ground shafts, discs)
class Rev:
    """stepped revolved part drawn in elevation: axis along +x at y=0, upper half in section, lower half as view.
    segs: [(length, R)], bore: [(x0, x1, r)], teeth/spline/thread: [(x0, x1)]"""
    def __init__(self, segs, bore=(), teeth=(), spline=(), thread=(), grooves=()):
        self.segs, self.bore, self.teeth, self.spline, self.thread, self.grooves = segs, bore, teeth, spline, thread, grooves
        self.xs = [0]
        for ln, r in segs:
            self.xs.append(self.xs[-1] + ln)
        self.L = self.xs[-1]

    def R(self, x):
        for i, (ln, r) in enumerate(self.segs):
            if self.xs[i] - 1e-6 <= x <= self.xs[i + 1] + 1e-6:
                return r
        return self.segs[-1][1]

    def rin(self, x):
        for x0, x1, r in self.bore:
            if x0 - 1e-6 <= x <= x1 + 1e-6:
                return r
        return 0

    def top_pts(self, x0=None, x1=None, sign=-1):
        x0 = 0 if x0 is None else x0
        x1 = self.L if x1 is None else x1
        pts_ = []
        for i, (ln, r) in enumerate(self.segs):
            a, b = max(self.xs[i], x0), min(self.xs[i + 1], x1)
            if a < b - 1e-6:
                pts_ += [(a, sign * r), (b, sign * r)]
        return pts_

    def od(self, x0, x1, both=True):
        d = "M" + " L".join(n(x) + " " + n(y) for x, y in self.top_pts(x0, x1, -1))
        if both:
            d += " M" + " L".join(n(x) + " " + n(y) for x, y in self.top_pts(x0, x1, 1))
        return d

    def face(self, x):
        r = max(self.R(x - 0.1), self.R(x + 0.1))
        return "M%s %s L%s %s" % (n(x), n(-r), n(x), n(r))

    def bore_d(self, x0, x1):
        r = self.rin((x0 + x1) / 2)
        return "M%s %s L%s %s M%s %s L%s %s" % (n(x0), n(-r), n(x1), n(-r), n(x0), n(r), n(x1), n(r))

    def svg(self, hot=False, rough=False):
        up = self.top_pts(sign=-1)
        lo = self.top_pts(sign=1)
        cu = "h" if hot else "cut"
        cw = "h" if hot else "w"
        s = path(P([(0, 0)] + up + [(self.L, 0)]), cu)
        s += path(P([(0, 0)] + lo + [(self.L, 0)]), cw)
        for x0, x1, r in self.bore:
            s += rect(x0, -r, x1 - x0, r, "void") + hid("M%s %s L%s %s" % (n(x0), n(r), n(x1), n(r)))
        for i in range(1, len(self.segs)):
            x = self.xs[i]
            rr = min(self.segs[i - 1][1], self.segs[i][1])
            s += line(x, 0, x, rr, "o thin")
        for x0, x1 in self.teeth:
            r = self.R((x0 + x1) / 2)
            s += line(x0, r - 4, x1, r - 4, "cl")
            for x in range(int(x0) + 2, int(x1) - 1, 4):
                s += line(x, r - 7, x + 2, r, "o thin")
        for x0, x1 in self.spline:
            r = self.R((x0 + x1) / 2)
            for x in range(int(x0) + 2, int(x1) - 1, 3):
                s += line(x, r - 4, x, r, "o thin")
        for x0, x1 in self.thread:
            r = self.R((x0 + x1) / 2)
            for x in range(int(x0) + 1, int(x1) - 1, 3):
                s += line(x, r - 2.5, x + 1.5, r, "o thin")
        for x0, w, dep in self.grooves:
            r = self.R(x0)
            s += rect(x0, r - dep, w, dep, "void")
        if rough:
            s += roughen(up) + roughen(lo)
        s += cl(-12, 0, self.L + 12, 0)
        return s


def lathe(rv, pl, tool_x, where="od", hl=(), chuck_len=True, tail=False, lab=None, rot_lab="主軸回転"):
    s = chuck(*pl(0, 0), rv.R(0) * pl.s * 2 + 6)
    if tail:
        s += center(*pl(rv.L, 0), True)
    s += pl.g(rv.svg())
    for d in hl:
        s += pl.g(mf(d))
    x, y = pl(tool_x, -rv.R(tool_x))
    if where == "od":
        s += tool("turn", x, y - 1, 90, 60, 18, spindle=False, rotarr=False, feedlab="送り")
    elif where == "face":
        s += tool("turn", x + 1, y + 4, 180, 60, 18, spindle=False, rotarr=False, feedlab="送り")
    cx, cy = pl(rv.L * 0.35, 0)
    s += rot(cx, cy, 10, rv.R(rv.L * 0.35) * pl.s + 12, -60, 60)
    s += text(cx, cy + rv.R(rv.L * 0.35) * pl.s + 30, rot_lab, "middle", "al")
    return s


def grind(rv, pl, x0, x1, wr=46, hl=None, centers=True, lab="砥石"):
    s = ""
    if centers:
        s += center(*pl(0, 0), False) + center(*pl(rv.L, 0), True)
    s += pl.g(rv.svg())
    s += pl.g(mf(hl if hl else rv.od(x0, x1)))
    xm = (x0 + x1) / 2
    x, y = pl(xm, -rv.R(xm))
    s += wheel(x, y - wr, wr, lab)
    s += coolant(x + wr * 0.8, y - 10, 160)
    return s


def induction_on(rv, pl, x0, x1, lab="加熱コイル"):
    s = pl.g(rv.svg())
    for x in (x0, x1):
        pass
    xa, ya = pl(x0, -rv.R((x0 + x1) / 2))
    xb, yb = pl(x1, rv.R((x0 + x1) / 2))
    s += rect(xa, ya, xb - xa, yb - ya, "hotband")
    s += rect(xa - 4, ya - 16, xb - xa + 8, 12, "cu", 2) + rect(xa - 4, yb + 4, xb - xa + 8, 12, "cu", 2)
    s += heat(xa + 6, ya - 20, 3, (xb - xa) / 3)
    s += text((xa + xb) / 2, ya - 44, lab, "middle", "al")
    return s
