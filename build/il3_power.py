"""v3 shaded-3D redraws for the power systems (genset / generator / dcpower / gasgen).
Only drawings that did not meet the v3 standard are re-registered here (same keys); the others
keep their il_parts_power*.py drawing."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P
from il3_pilot import lam_lines
from il_parts_power import person
from il_parts_power2 import loft

D2R = math.pi / 180


# =====================================================================================
# helpers
# =====================================================================================
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def uv(A, vecs):
    """3D offset vectors (perpendicular to A) -> prism outline (u, v, fid) in GE.frame(A)."""
    E1, E2, _ = GE.frame(A)
    return [(GE._dot(v, E1), GE._dot(v, E2), i) for i, v in enumerate(vecs)]


def bar(cam, a, b, w, h, side, mat="w", **kw):
    """rectangular bar from a to b; section w (along `side`) x h."""
    d = _sub(b, a)
    L = math.sqrt(GE._dot(d, d))
    u = GE._norm(d)
    s1 = GE._norm(_add(side, u, -GE._dot(side, u)))
    s2 = GE._cross(u, s1)
    vs = [_add(tuple(p * w / 2 * c for c in s1), s2, q * h / 2) for p, q in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return compact(GE.prism(cam, a, u, uv(u, vs), L, mat, **kw))


def dep(cam, p):
    return cam.P(p)[2]


def vis_band(cam, R, z0, z1, c="dks3", C=(0, 0, 0)):
    """dark band (vent duct / gap) on the visible half of a vertical cylinder."""
    a0 = math.degrees(math.atan2(-cam.D[1], -cam.D[0]))
    angs = range(int(a0) - 90, int(a0) + 91, 10)
    lo = [cam.xy((C[0] + R * math.cos(a * D2R), C[1] + R * math.sin(a * D2R), z0)) for a in angs]
    hi = [cam.xy((C[0] + R * math.cos(a * D2R), C[1] + R * math.sin(a * D2R), z1)) for a in angs]
    return path(P(lo + hi[::-1]), c)


def xband(cam, x0, x1, r, c="dks3"):
    """dark band on the visible half of a cylinder along x (radius r)."""
    E1, E2, _ = GE.frame((1, 0, 0))
    ac = math.atan2(-GE._dot(cam.D, E2), -GE._dot(cam.D, E1))
    pts = []
    for x in (x0, x1):
        row = []
        for k in range(19):
            a = ac - math.pi / 2 + math.pi * k / 18
            row.append(cam.xy((x, r * (math.cos(a) * E1[1] + math.sin(a) * E2[1]), r * (math.cos(a) * E1[2] + math.sin(a) * E2[2]))))
        pts.append(row)
    return path(P(pts[0] + pts[1][::-1]), c)


def xlines(cam, xs, r, c="gr"):
    """thin rings (lamination packets, tape edges) on the visible half of a cylinder along x."""
    E1, E2, _ = GE.frame((1, 0, 0))
    ac = math.atan2(-GE._dot(cam.D, E2), -GE._dot(cam.D, E1))
    d = ""
    for x in xs:
        d += P([cam.xy((x, r * (math.cos(a) * E1[1] + math.sin(a) * E2[1]), r * (math.cos(a) * E1[2] + math.sin(a) * E2[2])))
                for a in [ac - math.pi / 2 + math.pi * k / 16 for k in range(17)]], False)
    return path(d, c)


def slot_ring(ri, ns, sd, sw, off=0.0):
    """bore outline with ns open rectangular slots (depth sd, width sw)."""
    pts = []
    for k in range(ns):
        c = 2 * math.pi * (k + off) / ns
        h0, h1 = sw / 2 / ri, sw / 2 / (ri + sd)
        pts += [(ri * math.cos(c - h0), ri * math.sin(c - h0)), ((ri + sd) * math.cos(c - h1), (ri + sd) * math.sin(c - h1)),
                ((ri + sd) * math.cos(c + h1), (ri + sd) * math.sin(c + h1)), (ri * math.cos(c + h0), ri * math.sin(c + h0))]
    return [(-y, x, i) for i, (x, y) in enumerate(pts)]


def zpr(cam, z0, h, xy, mat="w", **kw):
    """outline [(x, y)] extruded along +z (manual-order drawing)."""
    return compact(GE.prism(cam, (0, 0, z0), (0, 0, 1), [(-p[1], p[0], p[2] if len(p) > 2 else i) for i, p in enumerate(xy)], h, mat, **kw))


def cyl(cam, O, A, r, h, mat="w", seg=32, bands=12, r1=None, holes=(), **kw):
    scale = (lambda t: 1 + (r1 / r - 1) * t) if r1 is not None else None
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, bands), h, mat, holes=list(holes),
                            smooth="outer" if holes else True, scale=scale, **kw))


def man(sc, p, mm_per_unit):
    """person silhouette standing at world point p (feet), 1.7 m tall."""
    x, y = sc.cam.xy(p)
    return person(x, y, 1700 / mm_per_unit * sc.cam.s * 0.92)


# =====================================================================================
# generator.gencore — stator core: lamination stack in packets with radial vent ducts,
# open slots at the bore, clamp plates with through-bolt nuts, outer key (building) bars
# =====================================================================================
def stator_core(cam, R=120, Ri=84, H=96, ns=48, sd=17, sw=6.5, ducts=4, keys=12, clamp=True, slots=True):
    o = ""
    bars = []
    for k in range(keys):
        a = 2 * math.pi * (k + .5) / keys
        c, s_ = math.cos(a), math.sin(a)
        b = zpr(cam, -6, H + 12, [(R * c - 4 * s_, R * s_ + 4 * c), ((R + 5) * c - 4 * s_, (R + 5) * s_ + 4 * c),
                                  ((R + 5) * c + 4 * s_, (R + 5) * s_ - 4 * c), (R * c + 4 * s_, R * s_ - 4 * c)], "w", dark=1)
        if c * cam.D[0] + s_ * cam.D[1] > 0:
            o += b
        else:
            bars.append((dep(cam, (R * c, R * s_, H / 2)), b))
    if clamp:
        o += cyl(cam, (0, 0, -6), (0, 0, 1), R - 2, 6, "m", seg=48, bands=12, caps=False)
    o += compact(GE.prism(cam, (0, 0, 0), (0, 0, 1), GE.circle_outline(R, 64, 16), H, "w", holes=[GE.circle_outline(Ri, 64, 16)], smooth="outer"))
    o += lam_lines(cam, R, H, 11)
    for j in range(1, ducts + 1):
        z = H * j / (ducts + 1)
        o += vis_band(cam, R, z - 1.3, z + 1.3)
    if slots:
        # slot mouths on the top face + slot grooves on the visible (far) bore wall, clipped by the near rim
        rim = [cam.xy((Ri * math.cos(2 * math.pi * k / 96), Ri * math.sin(2 * math.pi * k / 96), H)) for k in range(96)]
        cx = sum(p[0] for p in rim) / 96
        cy = sum(p[1] for p in rim) / 96
        low = sorted([p for p in rim if p[1] >= cy - 1e-6])

        def ylow(x):
            for (x0, y0), (x1, y1) in zip(low, low[1:]):
                if x0 <= x <= x1 and x1 > x0:
                    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            return cy
        d, g = "", ""
        for k in range(ns):
            a = 2 * math.pi * (k + .5) / ns
            c, s_ = math.cos(a), math.sin(a)
            h0, h1 = sw / 2 / Ri, sw / 2 / (Ri + sd)
            q = [(Ri * math.cos(a - h0), Ri * math.sin(a - h0)), ((Ri + sd) * math.cos(a - h1), (Ri + sd) * math.sin(a - h1)),
                 ((Ri + sd) * math.cos(a + h1), (Ri + sd) * math.sin(a + h1)), (Ri * math.cos(a + h0), Ri * math.sin(a + h0))]
            d += P([cam.xy((x, y, H + .05)) for x, y in q])
            if c * cam.D[0] + s_ * cam.D[1] > 0.15:          # far wall faces the viewer
                tx, ty = cam.xy((Ri * c, Ri * s_, H))
                bx, by = cam.xy((Ri * c, Ri * s_, 0))
                yb = min(by, ylow(tx))
                if yb > ty + 1:
                    hw = sw / 2 * cam.s * abs(c * cam.D[1] - s_ * cam.D[0]) ** .5
                    g += P([(tx - hw, ty), (tx + hw, ty), (tx + hw, yb), (tx - hw, yb)])
        o += path(g, "dks3") + path(d, "bg")
    if clamp:
        o += cyl(cam, (0, 0, H), (0, 0, 1), R - 2, 6, "m", seg=48, bands=12, holes=[GE.circle_outline(Ri + 20, 40, 10)])
        for k in range(16):
            a = 2 * math.pi * (k + .25) / 16
            o += hole3(cam, ((R - 10) * math.cos(a), (R - 10) * math.sin(a), H + 6.1), (0, 0, 1), 3.8, "dks2", 8)
    return o + "".join(b for _, b in sorted(bars, key=lambda t: -t[0]))


@part("generator.gencore")
def _():
    return fit(lambda sc: stator_core(sc.cam), -30, 30, (40, 10, 280, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


# =====================================================================================
# generator.genwinding — wound stator after VPI: core + form-wound end windings (two layers
# leaning opposite ways, flaring out), binding ring, phase and neutral leads with lugs
# =====================================================================================
@part("generator.genwinding")
def _():
    R, Ri, H, ns, hc = 120, 84, 70, 30, 40

    def fn(sc):
        cam = sc.cam
        o = cyl(cam, (0, 0, -16), (0, 0, 1), Ri + 22, 16, "cu", seg=48, bands=12, dark=1, holes=[GE.circle_outline(Ri + 1, 36, 9)])
        o += stator_core(cam, R, Ri, H, ns, 18, 7.5, 3, 0, clamp=False, slots=False)
        blocks = []
        dlt = 1.9 * 2 * math.pi / ns
        for k in range(ns):
            a = 2 * math.pi * (k + .5) / ns
            c, s_ = math.cos(a), math.sin(a)
            for r0, r1, sg in ((Ri + 1, Ri + 9, 1), (Ri + 9.5, Ri + 17.5, -1)):
                w = 3.6
                loop = [(r * c - q * w * s_, r * s_ + q * w * c, i) for i, (r, q) in enumerate(((r0, -1), (r1, -1), (r1, 1), (r0, 1)))]
                am = a + sg * dlt / 2
                rm = (r0 + r1) / 2 + 4
                blocks.append((dep(cam, (rm * math.cos(am), rm * math.sin(am), H + hc / 2)),
                               GE.prism(cam, (0, 0, H), (0, 0, 1), [(-v, u, f) for u, v, f in loop], hc, "cu",
                                        twist=sg * dlt, scale=lambda t: 1 + .14 * t, lines=False)))
        for j, ang in enumerate((62, 74, 86, 104, 116, 128)):
            a = ang * D2R
            c, s_ = math.cos(a), math.sin(a)
            rr = Ri + 14
            hgt = hc + 30 + (j % 3) * 4
            p0 = (rr * c, rr * s_, H + 4)
            p1 = (rr * c, rr * s_, H + hgt)
            b = bar(cam, p0, p1, 6, 3.4, (-s_, c, 0), "cu")
            b += bar(cam, p1, (rr * c, rr * s_, H + hgt + 9), 9, 2, (-s_, c, 0), "cu")
            blocks.append((dep(cam, (rr * c, rr * s_, H + 40)), b))
        o += "".join(b for _, b in sorted(blocks, key=lambda b: -b[0]))
        # binding ring tying the coil noses
        o += cyl(cam, (0, 0, H + hc - 12), (0, 0, 1), Ri + 30, 4, "m", seg=48, bands=12, holes=[GE.circle_outline(Ri + 24, 48, 12)])
        return o
    return fit(fn, -30, 30, (40, 8, 280, 180), sh_ry=8, sh_k=.5, sh_dy=-4)


# =====================================================================================
# generator.gencoil — one diamond (form-wound) coil: two slot legs in different layers (black
# semi-conductive tape), mica-taped diamond end turns with knuckles, two bare leads
# =====================================================================================
@part("generator.gencoil")
def _():
    L, S, E, dz, w, h = 220, 170, 70, 16, 13, 26

    def fn(sc):
        cam = sc.cam
        up = (0, 0, 1)
        a0, a1 = (-L / 2, 0, 0), (L / 2, 0, 0)
        b0, b1 = (-L / 2, S, -dz), (L / 2, S, -dz)
        ext = 16
        segs = [
            ((a0[0] - ext, 0, 0), a0, "dk"), (a1, (a1[0] + ext, 0, 0), "dk"),
            ((b0[0] - ext, S, -dz), b0, "dk"), (b1, (b1[0] + ext, S, -dz), "dk"),
            ((a1[0] + ext, 0, 0), (a1[0] + ext + E, S / 2 - 6, -dz / 2 + 4), "gw"),
            ((a1[0] + ext + E, S / 2 + 6, -dz / 2 - 4), (b1[0] + ext, S, -dz), "gw"),
            ((a0[0] - ext, 0, 0), (a0[0] - ext - E, S / 2 - 12, -dz / 2 + 4), "gw"),
            ((a0[0] - ext - E + 4, S / 2 + 12, -dz / 2 - 4), (b0[0] - ext, S, -dz), "gw"),
        ]
        items = []
        for p, q, m in segs:
            items.append((dep(cam, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, (p[2] + q[2]) / 2)), bar(cam, p, q, h, w, up, m)))
        # slot legs (main straight parts)
        items.append((dep(cam, (0, 0, 0)), bar(cam, a0, a1, h, w, up, "dk")))
        items.append((dep(cam, (0, S, -dz)), bar(cam, b0, b1, h, w, up, "dk")))
        # knuckles at the noses
        n1 = (a1[0] + ext + E + 3, S / 2, -dz / 2)
        items.append((dep(cam, n1), cyl(cam, (n1[0], n1[1] - 9, n1[2]), (0, 1, 0), 9, 18, "gw", seg=16, bands=8)))
        # leads at the left nose
        for yy, zz in ((S / 2 - 12, -dz / 2 + 4), (S / 2 + 12, -dz / 2 - 4)):
            p = (a0[0] - ext - E - 2, yy, zz)
            q = (a0[0] - ext - E - 34, yy, zz + 10)
            items.append((dep(cam, p) - 1, bar(cam, (p[0] + 6, yy, zz), q, 14, 5, up, "cu")))
        for x in (-L / 2 + 20, 0, L / 2 - 20):
            pass
        return "".join(s for _, s in sorted(items, key=lambda t: -t[0]))
    return fit(fn, -24, 40, (20, 16, 300, 178), sh_ry=7, sh_k=.5, sh_dy=-4)


# =====================================================================================
# generator.genrotor — 4-pole salient-pole rotor: polygonal spider hub, field coils (radial
# racetrack blocks), laminated pole shoes with damper end plates / bar ends, shaft ends
# =====================================================================================
def rotor_parts(cam, x0=0, Lc=150, phi0=45, Rs=110, Rc=92, hw=24):
    items = []
    Lx = Lc
    # hub (spider): square section with chamfered corners, faces under the coils
    hb = 46
    oct_ = []
    for k in range(4):
        p = (phi0 + 90 * k) * D2R
        for t in (-28, 28):
            a = math.atan2(t, hb)
            r = math.hypot(t, hb)
            oct_.append((r * math.cos(p + a), r * math.sin(p + a)))
    hubs = compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), [(y, z, i) for i, (y, z) in enumerate(sorted(oct_, key=lambda q: math.atan2(q[1], q[0])))],
                            Lx, "w", cap_mat="w3"))
    items.append((dep(cam, (x0 + Lx / 2, 0, 0)), hubs))
    for k in range(4):
        ph = phi0 + 90 * k
        p = ph * D2R
        rad = (0, math.cos(p), math.sin(p))
        tan = (0, -math.sin(p), math.cos(p))
        grp = []
        # coil: solid racetrack block with axis radial
        t, ex = 9, 9
        vs = []
        for cx, cy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            for a in range(4):
                an = (a / 3 * 90 + {(1, 1): 0, (-1, 1): 90, (-1, -1): 180, (1, -1): 270}[(cx, cy)]) * D2R
                xx = cx * (Lc / 2) + t * math.cos(an)
                tt = cy * hw + t * math.sin(an)
                vs.append((xx, 0, 0) if False else _add(_add((xx, 0, 0), tan, tt), (0, 0, 0)))
        r0, r1 = hb, Rc - 2
        O = _add((x0 + Lc / 2, 0, 0), rad, r0)
        coil = compact(GE.prism(cam, O, rad, banded(uv(rad, vs), 2), r1 - r0, "cu", smooth=True, grooves=5))
        grp.append((dep(cam, _add((x0 + Lc / 2, 0, 0), rad, (r0 + r1) / 2)), coil))
        # pole shoe (laminated) with damper bar holes; copper end plate on the near face
        sh = banded(hull(arc(0, 0, Rs, ph - 27, ph + 27, 8) + arc(0, 0, Rc - 2, ph - 25, ph + 25, 2)), 2)
        shoe = compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), sh, Lc, "w", smooth=True, cap_mat="w3"))
        plate = compact(GE.prism(cam, (x0 - 3, 0, 0), (1, 0, 0), sh, 3, "cu", smooth=True))
        for j in range(5):
            b = (ph - 20 + 10 * j) * D2R
            plate += hole3(cam, (x0 - 3.1, 0, 0) if False else (x0 - 3.1, (Rs - 6) * math.cos(b), (Rs - 6) * math.sin(b)), (-1, 0, 0), 3.2, "cus3")
        grp.append((dep(cam, _add((x0 + Lc / 2, 0, 0), rad, Rs - 8)), shoe + plate))
        grp.sort(key=lambda t: -t[0])
        items.append((grp[-1][0] if False else min(g[0] for g in grp), "".join(g[1] for g in grp)))
    return items


@part("generator.genrotor")
def _():
    Lc = 150

    def fn(sc):
        cam = sc.cam
        o = ""
        x = Lc + 11
        for L, r in ((24, 34), (60, 30), (40, 26)):
            o += cyl(cam, (x, 0, 0), (1, 0, 0), r, L, "w", seg=28, bands=10)
            x += L
        items = rotor_parts(cam, 0, Lc)
        # sort pole groups against the hub by their nearest member
        o += "".join(s for _, s in sorted(items, key=lambda t: -t[0]))
        x = -12
        for L, r in ((20, 34), (34, 30), (50, 25)):
            o += cyl(cam, (x - L, 0, 0), (1, 0, 0), r, L, "w", seg=28, bands=10) if False else ""
        # near shaft end (drawn last, toward the viewer)
        segs = [(-12, 12, 36), (-46, 34, 30), (-96, 50, 25)]
        for x0, L, r in segs:
            o += cyl(cam, (x0, 0, 0), (1, 0, 0), r, L, "w", seg=28, bands=10)
        o += path(P([cam.xy(p) for p in ((-92, -5, 25.1), (-56, -5, 25.1), (-56, 5, 25.1), (-92, 5, 25.1))]), "bg")
        o += hole3(cam, (-96.1, 0, 0), (-1, 0, 0), 6, "w3")
        return o
    return fit(fn, 30, 22, (22, 16, 298, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# generator.genshaft — stepped forged shaft for a single-bearing generator: flexible coupling
# discs (bolted to the engine flywheel) on a hub, fan seat, rotor-core seat with keyway,
# exciter seat, bearing journal
# =====================================================================================
@part("generator.genshaft")
def _():
    def fn(sc):
        cam = sc.cam
        # coupling: two flex discs with flywheel-bolt and hub-bolt circles
        hol = [GE.circle_outline(20, 20, 5)]
        for k in range(8):
            a = 2 * math.pi * (k + .5) / 8
            hol.append(GE.circle_outline(5, 12, 4, 100 * math.cos(a), 100 * math.sin(a)))
        CYL(sc, (0, 0, 0), (1, 0, 0), 112, 4, "w", seg=64, bands=16, holes=hol)
        CYL(sc, (4, 0, 0), (1, 0, 0), 70, 3, "dk", seg=40)
        CYL(sc, (7, 0, 0), (1, 0, 0), 112, 4, "w", seg=64, bands=16, holes=hol[:1])

        def bolts(s_):
            o = ""
            for k in range(8):
                a = 2 * math.pi * k / 8
                o += hole3(s_.cam, (-.1, 52 * math.cos(a), 52 * math.sin(a)), (-1, 0, 0), 5.5, "dks2", 6)
            return o
        RAW(sc, bolts, ((-.2, -60, -60), (0, 60, 60)), -2)
        x = 11
        steps = [(34, 48, "w"), (40, 40, "w"), (230, 50, "w"), (26, 44, "w"), (70, 36, "w"), (48, 32, "w"), (22, 26, "w")]
        for L, r, m in steps:
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, m, seg=32, bands=12)
            x += L
        # keyways on the core seat and exciter seat
        x0 = 11 + 34 + 40
        def kw(s_, a=x0 + 20, b=x0 + 210, r=50.1, w=7):
            return path(P([s_.cam.xy(p) for p in ((a, -w, r), (b, -w, r), (b, w, r), (a, w, r))]), "bg")
        RAW(sc, kw, ((x0, -8, 49), (x0 + 230, 8, 50.2)), -1)
        x1 = x0 + 230 + 26
        RAW(sc, lambda s_: kw(s_, x1 + 10, x1 + 60, 36.1, 5), ((x1, -6, 35), (x1 + 70, 6, 36.2)), -1)
    return fit(fn, 22, 20, (16, 30, 304, 172), sh_ry=6, sh_k=.5, sh_dy=-3)


# =====================================================================================
# generator.genexciter — brushless exciter set on the shaft end: rotating rectifier wheel
# (aluminium hub, diodes, varistors), exciter armature (laminated core + copper winding ends),
# exciter field stator drawn off along the axis, AVR module
# =====================================================================================
@part("generator.genexciter")
def _():
    def fn(sc):
        cam = sc.cam
        CYL(sc, (-60, 0, 0), (1, 0, 0), 16, 52, "w", seg=24, bands=10)            # shaft end beyond the wheel
        RING(sc, (-8, 0, 0), (1, 0, 0), 62, 16, 12, "alu", seg=48, bands=12)       # rectifier wheel
        def parts_(s_):
            o = ""
            for k in range(6):
                a = 2 * math.pi * (k + .3) / 6
                c, s2 = math.cos(a), math.sin(a)
                o += cyl(s_.cam, (-8, 42 * c, 42 * s2), (-1, 0, 0), 6.5, 4, "dk", seg=6, bands=6)
                o += cyl(s_.cam, (-12, 42 * c, 42 * s2), (-1, 0, 0), 2.6, 7, "cu", seg=10, bands=5, lines=False)
            for a in (math.pi * .05, math.pi * 1.05):
                o += cyl(s_.cam, (-8, 26 * math.cos(a), 26 * math.sin(a)), (-1, 0, 0), 8, 3, "gw", seg=16, bands=8)
            return o
        RAW(sc, parts_, ((-20, -62, -62), (-8, 62, 62)), -2)
        CYL(sc, (4, 0, 0), (1, 0, 0), 20, 18, "w", seg=24, bands=10)
        CYL(sc, (22, 0, 0), (1, 0, 0), 44, 10, "cu", seg=40, bands=10, dark=1)    # armature winding end
        CYL(sc, (32, 0, 0), (1, 0, 0), 56, 44, "w", seg=40, bands=12)             # armature core
        RAW(sc, lambda s_: xlines(s_.cam, [32 + 44 * j / 6 for j in range(1, 6)], 56), ((33, -56, -56), (75, 56, 56)), -1)
        CYL(sc, (76, 0, 0), (1, 0, 0), 44, 10, "cu", seg=40, bands=10, dark=1)
        CYL(sc, (86, 0, 0), (1, 0, 0), 20, 30, "w", seg=24, bands=10)
        # exciter field stator (drawn off the armature)
        ns = 8
        RING(sc, (124, 0, 0), (1, 0, 0), 96, 64, 46, "pt", seg=48, bands=12, dark=1)
        for k in range(ns):
            a = 2 * math.pi * (k + .5) / ns
            c, s2 = math.cos(a), math.sin(a)
            X(sc, 118, 6, [(r * c - q * 12 * s2, r * s2 + q * 12 * c) for r, q in ((76, -1), (60, -1), (60, 1), (76, 1))], "cu", -1)
    return fit(fn, 26, 20, (18, 18, 302, 176), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# generator.genassy — assembled single-bearing generator: fabricated octagonal frame with feet,
# SAE adapter showing the coupling disc, air outlet screens, NDE bracket + exciter cover,
# terminal box on top, lifting lugs
# =====================================================================================
def generator3(sc, x0=0, s=1.0, tb=True, disc=True, sg=1.0):
    """generator body along +x from x0, drive end (adapter) at x0. world units ~ 10 mm * s."""
    k = s
    oc = []
    for a, r in ((0, 1), ):
        pass
    h, c = 100 * k, 34 * k
    octo = [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]
    if disc:
        hol = [GE.circle_outline(14 * k, 16, 4)]
        for j in range(8):
            a = 2 * math.pi * (j + .5) / 8
            hol.append(GE.circle_outline(4.5 * k, 10, 4, 96 * k * math.cos(a), 96 * k * math.sin(a)))
        CYL(sc, (x0 + 18 * k, 0, 0), (1, 0, 0), 104 * k, 3 * k, "w", seg=56, bands=14, holes=hol)
    RING(sc, (x0, 0, 0), (1, 0, 0), 128 * k, 108 * k, 18 * k, "pt", seg=int(56 * sg), bands=14)        # SAE adapter flange
    CYL(sc, (x0 + 21 * k, 0, 0), (1, 0, 0), 118 * k, 34 * k, "pt", seg=int(48 * sg), bands=12, r1=104 * k)
    X(sc, x0 + 55 * k, 230 * k, octo, "pt", dark=1)
    X(sc, x0 + 285 * k, 16 * k, octo, "pt")                                                # NDE end bracket
    CYL(sc, (x0 + 301 * k, 0, 0), (1, 0, 0), 78 * k, 60 * k, "pt", seg=int(40 * sg), bands=12)        # exciter cover
    CYL(sc, (x0 + 361 * k, 0, 0), (1, 0, 0), 46 * k, 10 * k, "pt", seg=32, bands=10)
    BOX(sc, x0 + 70 * k, -126 * k, -h, 200 * k, 26 * k, 18 * k, "pt", 1)                   # feet
    BOX(sc, x0 + 70 * k, h, -h, 200 * k, 26 * k, 18 * k, "pt", 1)
    if tb:
        BOX(sc, x0 + 150 * k, -60 * k, h, 96 * k, 120 * k, 66 * k, "pt", ch=4 * k)

    def marks(s_):
        cam = s_.cam
        o = ""
        for j in range(5):                                       # air-outlet screens on the adapter
            a = (200 + j * 22) * D2R
            p = [(x0 + (24 + dx) * k, 112 * k * math.cos(a + da), 112 * k * math.sin(a + da)) for dx, da in ((0, -.13), (24, -.13), (24, .13), (0, .13))]
            o += path(P([cam.xy(q) for q in p]), "dks3")
        for xx in (x0 + 90 * k, x0 + 130 * k, x0 + 170 * k, x0 + 210 * k, x0 + 250 * k):   # frame stiffener seams
            o += path(P([cam.xy((xx, -h - .2, -h + c)), cam.xy((xx, -h - .2, h - c))], False), "gr")
        if tb:
            o += path(P([cam.xy(q) for q in ((x0 + 158 * k, -60.2 * k, h + 8 * k), (x0 + 238 * k, -60.2 * k, h + 8 * k),
                                                (x0 + 238 * k, -60.2 * k, h + 58 * k), (x0 + 158 * k, -60.2 * k, h + 58 * k))]), "o")
        return o
    RAW(sc, marks, ((x0, -130 * k, -h), (x0 + 1, -128 * k, h)), -3)


@part("generator.genassy")
def _():
    return fit(lambda sc: generator3(sc), 26, 20, (22, 14, 298, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# gasgen — gas turbine blades / disc / combustor / rotor, gas-engine pre-chamber
# =====================================================================================
def foil(c, m, tmax, n=9):
    """cambered airfoil loop (chord c, centred on mid-chord), cosine spacing."""
    up, lo = [], []
    for i in range(n + 1):
        x = (1 - math.cos(math.pi * i / n)) / 2
        yt = 5 * tmax * (0.2969 * math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3 - 0.1036 * x ** 4)
        yc = m * 4 * x * (1 - x)
        up.append(((x - .5) * c, (yc + yt) * c))
        lo.append(((x - .5) * c, (yc - yt) * c))
    return up + lo[-2:0:-1]


def blade_secs(sec, z0, z1, st0, st1, k1=1.0, nz=5, dx=0.0, dy=0.0, lean=0.0):
    out = []
    for j in range(nz):
        t = j / (nz - 1)
        th = (st0 + (st1 - st0) * t) * D2R
        k = 1 + (k1 - 1) * t
        z = z0 + (z1 - z0) * t
        out.append([(dx + k * (u * math.cos(th) - v * math.sin(th)), dy + lean * t + k * (u * math.sin(th) + v * math.cos(th)), z) for u, v in sec])
    return out


def surf_pts(cam, secs, idx, zf, c="bg", r=1.2):
    """small dark dots on a lofted surface at loop index idx, at height fractions zf (only if facing viewer)."""
    d = ""
    for f in zf:
        j = f * (len(secs) - 1)
        j0 = min(int(j), len(secs) - 2)
        t = j - j0
        A_, B_ = secs[j0], secs[j0 + 1]
        n_ = len(A_)
        p = tuple(A_[idx][q] + (B_[idx][q] - A_[idx][q]) * t for q in range(3))
        pa = A_[(idx - 1) % n_]
        pb = A_[(idx + 1) % n_]
        tg = (pb[0] - pa[0], pb[1] - pa[1], 0)
        nr = GE._norm((tg[1], -tg[0], 0))
        cen = (sum(q[0] for q in A_) / n_, sum(q[1] for q in A_) / n_)
        if (p[0] - cen[0]) * nr[0] + (p[1] - cen[1]) * nr[1] < 0:
            nr = (-nr[0], -nr[1], 0)
        if GE._dot(nr, cam.D) > -0.1:
            continue
        d += P(circ3(cam, _add(p, nr, .3), nr, r, 8))
    return path(d, c) if d else ""


@part("gasgen.gtblade")
def _():
    sec = foil(70, .19, .25)
    secs = blade_secs(sec, 0, 116, -22, -2, .92, 5)

    def fn(sc):
        cam = sc.cam
        ft = [(13, -6), (13, -26), (20, -31), (11, -37), (17, -42), (9, -47), (14, -52), (7, -57), (5, -60)]
        yz = ft + [(-y, z) for y, z in ft[::-1]]
        X(sc, -30, 60, yz, "w", dark=1, cap_mat="w3")
        BOX(sc, -38, -26, -6, 76, 52, 6, "w", ch=3)
        RAW(sc, lambda s_: loft(s_.cam, secs, "w", cap=True), ((-40, -40, 0), (40, 40, 120)))

        def holes(s_):
            o = ""
            n_ = len(sec)
            for idx in (0, 1, n_ - 1):          # showerhead rows at the leading edge
                o += surf_pts(s_.cam, secs, idx, [.08 + .085 * k for k in range(11)], "bg", 1.1)
            for idx in (n_ - 3, n_ - 5, 3):      # film-cooling rows on the flanks
                o += surf_pts(s_.cam, secs, idx, [.1 + .1 * k for k in range(9)], "bg", .9)
            return o
        RAW(sc, holes, ((-41, -41, 0), (41, 41, 121)), -3)
    return fit(fn, 34, 22, (70, 10, 250, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("gasgen.gtcomp")
def _():
    def fn(sc):
        x = 0
        for k, (sz, st0, st1) in enumerate(((1.0, -50, -14), (.66, -46, -18), (.44, -42, -22))):
            sec = foil(66 * sz, .1, .08, 9)
            secs = blade_secs(sec, 0, 150 * sz, st0, st1, .86, 5)
            w = 30 * sz
            X(sc, x - 28 * sz, 56 * sz, [(-11 * sz, -4 * sz), (11 * sz, -4 * sz), (17 * sz, -20 * sz), (-17 * sz, -20 * sz)], "w", dark=1, cap_mat="w3")
            BOX(sc, x - 30 * sz, -w / 2 - 6 * sz, -4 * sz, 60 * sz, w + 12 * sz, 4 * sz, "w", ch=2 * sz)
            RAW(sc, lambda s_, secs=secs, x=x: loft(s_.cam, [[(p[0] + x, p[1], p[2]) for p in q] for q in secs], "w", cap=True),
                ((x - 40 * sz, -40 * sz, 0), (x + 40 * sz, 40 * sz, 150 * sz)))
            x += 100 * sz + 30
    return fit(fn, 30, 20, (24, 12, 296, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("gasgen.gtdisk")
def _():
    R, Rr, Rw, Rh, Rb = 215, 172, 70, 64, 28
    A = (0, -1, 0)

    def fn(sc):
        cam = sc.cam
        o = cyl(cam, (0, 13, 0), A, Rr + 2, 26, "w", seg=64, bands=16)                           # web
        o += cyl(cam, (0, 28, 0), A, R, 56, "w", seg=72, bands=18, holes=[GE.circle_outline(Rr, 64, 16)])   # rim
        # fir-tree slots: on the rim face and across the visible outer surface
        E1, E2, _ = GE.frame(A)
        ns = 44
        d, g = "", ""
        ft = [(0, 4.4), (8, 4.4), (11, 7), (16, 3.6), (20, 6), (25, 3), (29, 5), (34, 2.4), (38, 2.4)]
        for k in range(ns):
            a = 2 * math.pi * (k + .5) / ns
            rd = (math.cos(a) * E1[0] + math.sin(a) * E2[0], math.cos(a) * E1[1] + math.sin(a) * E2[1], math.cos(a) * E1[2] + math.sin(a) * E2[2])
            tg = GE._cross(A, rd)
            loop = [(R - dr, w) for dr, w in ft] + [(R - dr, -w) for dr, w in ft[::-1]]
            d += P([cam.xy(_add(_add((0, -28.1, 0), rd, r_), tg, w)) for r_, w in loop])
            if GE._dot(rd, cam.D) < -0.1:
                g += P([cam.xy(_add(_add((0, yy, 0), rd, R + .2), tg, w)) for yy, w in ((-28, -4.4), (-28, 4.4), (28, 4.4), (28, -4.4))])
        o += path(g, "dks3") + path(d, "bg")
        o += path(P(circ3(cam, (0, -13.1, 0), A, Rr - 14, 56)), "gr")
        for k in range(12):                                                   # tie-bolt holes in the web
            a = 2 * math.pi * k / 12
            o += hole3(cam, _add((0, -13.1, 0), (math.cos(a) * E1[0] + math.sin(a) * E2[0], 0, math.cos(a) * E1[2] + math.sin(a) * E2[2]), 112), A, 7.5, "bg", 14)
        o += cyl(cam, (0, 36, 0), A, Rh, 72, "w", seg=48, bands=14, holes=[GE.circle_outline(Rb, 32, 8)], cap_mat="w")
        o += path(P(circ3(cam, (0, -36.1, 0), A, Rb + 10, 32)), "gr")
        return o
    return fit(fn, 38, 16, (54, 8, 266, 182), sh_ry=7, sh_k=.42, sh_dy=-2)


def _sstep(t):
    return t * t * (3 - 2 * t)


@part("gasgen.gtcomb")
def _():
    def tp_secs(n=24, ns=6, x0=206, x1=336):
        out = []
        for j in range(ns):
            t = j / (ns - 1)
            s_ = _sstep(t)
            p = 2 + 7 * s_
            a, b = 57 + 15 * s_, 57 - 29 * s_
            zc = -34 * s_
            row = []
            for i in range(n):
                th = 2 * math.pi * (i + .5) / n
                c, sn = math.cos(th), math.sin(th)
                row.append((x0 + (x1 - x0) * t, a * math.copysign(abs(c) ** (2 / p), c), zc + b * math.copysign(abs(sn) ** (2 / p), sn)))
            out.append(row)
        return out

    def fn(sc):
        cam = sc.cam
        CYL(sc, (-30, 0, 0), (1, 0, 0), 70, 14, "m", seg=48, bands=12)                     # end cover
        CYL(sc, (-16, 0, 0), (1, 0, 0), 62, 16, "w", seg=48, bands=12)                     # head-end ring / cap

        def nozzles(s_):
            o = ""
            pts = [(0, 0, 9)] + [(34 * math.cos(2 * math.pi * k / 6 + .3), 34 * math.sin(2 * math.pi * k / 6 + .3), 7.5) for k in range(6)]
            for y, z, r in sorted(pts, key=lambda q: -dep(s_.cam, (-30, q[0], q[1]))):
                o += cyl(s_.cam, (-30, y, z), (-1, 0, 0), r + 3, 4, "m", seg=6, bands=6)
                o += cyl(s_.cam, (-34, y, z), (-1, 0, 0), r, 14, "w", seg=16, bands=8)
                o += hole3(s_.cam, (-48.1, y, z), (-1, 0, 0), r * .55, "bg", 10)
            for k in range(16):
                a = 2 * math.pi * k / 16
                o += hole3(s_.cam, (-30.1, 63 * math.cos(a), 63 * math.sin(a)), (-1, 0, 0), 2.4, "dks2", 6)
            return o
        RAW(sc, nozzles, ((-49, -70, -70), (-30, 70, 70)), -2)
        CYL(sc, (0, 0, 0), (1, 0, 0), 54, 170, "w", seg=36, bands=12)
        CYL(sc, (170, 0, 0), (1, 0, 0), 52, 24, "w", seg=32, bands=10, dark=1)
        CYL(sc, (194, 0, 0), (1, 0, 0), 58, 12, "m", seg=36, bands=12)
        x = 206
        RAW(sc, lambda s_: "".join(xband(s_.cam, xx, xx + 3, 54.3, "ws3") for xx in (30, 64, 98, 132)), ((1, -55, -55), (169, 55, 55)), -1)
        def dil(s_):
            o = ""
            E1, E2, _ = GE.frame((1, 0, 0))
            for xx, nh, rr in ((116, 10, 6.5), (150, 10, 5)):
                for k in range(nh):
                    a = 2 * math.pi * (k + .5) / nh
                    nr = (0, math.cos(a), math.sin(a))
                    if GE._dot(nr, s_.cam.D) < -0.15:
                        o += hole3(s_.cam, (xx, 54.2 * nr[1], 54.2 * nr[2]), nr, rr, "bg", 12)
            return o
        RAW(sc, dil, ((100, -55, -55), (160, 55, 55)), -1)
        secs = tp_secs()
        RAW(sc, lambda s_: loft(s_.cam, secs, "w", cap=False), ((x, -72, -62), (336, 72, 57)))
        ex = secs[-1]
        o_ = [(p[1] * 1.14, (p[2] + 34) * 1.3 - 34, i // 3) for i, p in enumerate(ex)]
        hl = [(p[1], p[2], i) for i, p in enumerate(ex)]
        sc.add(compact(GE.prism(cam, (336, 0, 0), (1, 0, 0), o_, 8, "m", holes=[hl], smooth="outer")), ((336, -84, -72), (344, 84, 4)))
    return fit(fn, 30, 22, (18, 22, 302, 172), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("gasgen.gtrotor")
def _():
    def fn(sc):
        cam = sc.cam
        stages = []
        x = 0
        for k in range(8):
            stages.append((x, 17, 84 - 30 * k / 7, 0, 22))
            x += 24
        xc = x + 8
        x = xc + 34
        for k in range(3):
            stages.append((x, 20, 92 + 6 * k, 1, -30))
            x += 26
        xe = x
        o = cyl(cam, (xe, 0, 0), (1, 0, 0), 30, 40, "w", seg=28, bands=10)
        o += cyl(cam, (xe - 6, 0, 0), (1, 0, 0), 40, 26, "w", seg=28, bands=10)
        o += cyl(cam, (0, 0, 0), (1, 0, 0), 40, xc, "w", seg=32, bands=10, r1=50, dark=1, lines=False)
        o += cyl(cam, (xc, 0, 0), (1, 0, 0), 56, 34, "w", seg=36, bands=12)
        o += cyl(cam, (xc + 34, 0, 0), (1, 0, 0), 70, xe - xc - 34, "w", seg=36, bands=12, dark=1, lines=False)
        E1, E2, _ = GE.frame((1, 0, 0))
        ac = math.degrees(math.atan2(-GE._dot(cam.D, E2), -GE._dot(cam.D, E1)))
        for x0, L, rt, dk, tw in sorted(stages, key=lambda t: -t[0]):
            o += cyl(cam, (x0, 0, 0), (1, 0, 0), rt, L, "w", seg=28 if rt < 90 else 36, bands=10, dark=dk)
            d = ""
            for a in range(int(ac) - 84, int(ac) + 85, 11 if rt < 90 else 13):
                q = []
                for xx, aa in ((x0 + .5, a), (x0 + L - .5, a + tw * 14 / rt)):
                    r_ = rt + .2
                    q.append(cam.xy((xx, r_ * (math.cos(aa * D2R) * E1[1] + math.sin(aa * D2R) * E2[1]), r_ * (math.cos(aa * D2R) * E1[2] + math.sin(aa * D2R) * E2[2]))))
                d += P(q, False)
            o += path(d, "el")
        o += cyl(cam, (-20, 0, 0), (1, 0, 0), 38, 20, "w", seg=32, bands=10)
        o += cyl(cam, (-60, 0, 0), (1, 0, 0), 30, 40, "w", seg=28, bands=10)
        o += cyl(cam, (-70, 0, 0), (1, 0, 0), 56, 10, "w", seg=40, bands=12)
        for k in range(8):
            a = 2 * math.pi * (k + .5) / 8
            o += hole3(cam, (-70.1, 44 * math.cos(a), 44 * math.sin(a)), (-1, 0, 0), 3.6, "bg", 10)
        return o
    return fit(fn, 26, 20, (16, 24, 304, 174), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("gasgen.geprech")
def _():
    def fn(sc):
        cam = sc.cam
        # pre-chamber with spark plug (left)
        CYL(sc, (0, 0, -30), (0, 0, 1), 7, 8, "w", seg=20, bands=8)
        CYL(sc, (0, 0, -22), (0, 0, 1), 11, 4, "w", seg=24, bands=8)
        CYL(sc, (0, 0, -18), (0, 0, 1), 11, 18, "w", seg=28, bands=10, r1=22)
        CYL(sc, (0, 0, 0), (0, 0, 1), 22, 44, "w", seg=32, bands=10)
        CYL(sc, (0, 0, 44), (0, 0, 1), 32, 10, "w", seg=40, bands=12, dark=1)
        CYL(sc, (0, 0, 54), (0, 0, 1), 18, 18, "w", seg=28, bands=10)
        CYL(sc, (0, 0, 72), (0, 0, 1), 12, 12, "w", seg=6, bands=6)
        CYL(sc, (0, 0, 84), (0, 0, 1), 8, 34, "pt", seg=24, bands=8)
        CYL(sc, (0, 0, 118), (0, 0, 1), 3.4, 10, "m", seg=12, bands=6)

        def orif(s_):
            o = ""
            for k in range(6):
                a = 2 * math.pi * (k + .5) / 6
                nr = GE._norm((math.cos(a), math.sin(a), -.5))
                if GE._dot(nr, s_.cam.D) < -0.1:
                    o += hole3(s_.cam, (7.2 * math.cos(a), 7.2 * math.sin(a), -26), nr, 1.6, "bg", 8)
            return o
        RAW(sc, orif, ((-8, -8, -31), (8, 8, -21)), -2)
        # gas check valve on the side of the chamber
        CYL(sc, (-22, 0, 28), (-1, 0, 0), 8, 22, "w", seg=6, bands=6)
        CYL(sc, (-44, 0, 28), (-1, 0, 0), 5, 14, "w", seg=16, bands=8)
        # gas admission valve (right): valve body with flanges, solenoid on top, connector
        BOX(sc, 90, -24, -30, 64, 48, 40, "w", ch=4)
        CYL(sc, (122, -24, -10), (0, -1, 0), 16, 8, "w", seg=28, bands=10)
        CYL(sc, (122, 32, -10), (0, -1, 0), 16, 8, "w", seg=28, bands=10)
        CYL(sc, (122, 0, 10), (0, 0, 1), 22, 8, "w", seg=32, bands=10, dark=1)
        CYL(sc, (122, 0, 18), (0, 0, 1), 20, 48, "dk", seg=32, bands=10)
        BOX(sc, 110, -10, 66, 24, 20, 14, "dk", ch=2)

        def bolts(s_):
            o = ""
            for k in range(4):
                a = 2 * math.pi * (k + .5) / 4
                o += hole3(s_.cam, (122 + 11 * math.cos(a), -32.1, -10 + 11 * math.sin(a)), (0, -1, 0), 2, "dks2", 6)
            o += hole3(s_.cam, (122, -32.1, -10), (0, -1, 0), 7, "bg", 14)
            return o
        RAW(sc, bolts, ((106, -32.2, -26), (138, -32.1, 6)), -2)
    return fit(fn, -30, 22, (40, 10, 280, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# genset — V-type high-speed diesel, base frame, radiator, enclosure, day tank, exhaust,
# assembled set and load test. World unit = 10 mm.
# =====================================================================================
def xpr(cam, x0, L, yz, mat="pt", **kw):
    return compact(GE.prism(cam, (x0, 0, 0), (1, 0, 0), [(p[0], p[1], p[2] if len(p) > 2 else i) for i, p in enumerate(yz)], L, mat, **kw))


def vengine(cam, x0=0, n=8, pitch=40, detail=2, gas=False):
    """V-engine along +x from x0 (free end) to x0+L (flywheel end); crank axis at y=0, z=0."""
    L = n * pitch + 30
    near0 = cam.D[0] > 0                         # free end (x0) toward the viewer
    s30, c30 = .5, math.sqrt(3) / 2
    out = []
    # ends
    fw = cyl(cam, (x0 + L, 0, -8), (1, 0, 0), 96, 24, "pt", seg=40, bands=12, dark=1)
    fr = xpr(cam, x0 - 14, 14, [(-50, -50), (50, -50), (64, -10), (64, 40), (-64, 40), (-64, -10)], "pt")
    fr += cyl(cam, (x0 - 14, 0, -8), (-1, 0, 0), 30, 8, "m", seg=24, bands=8)
    fr += cyl(cam, (x0 - 22, 0, -8), (-1, 0, 0), 44, 18, "dk", seg=36, bands=10)
    fr += hole3(cam, (x0 - 40.1, 0, -8), (-1, 0, 0), 12, "w3") if near0 else ""

    def bank(s):
        d = (s * s30, c30)
        nn = (c30, -s * s30)

        def q(a, b):
            return (a * d[0] + b * nn[0], a * d[1] + b * nn[1])
        o = xpr(cam, x0, L - 6, [q(18, -32), q(18, 32), q(112, 32), q(112, -32)], "pt", dark=1)
        o += xpr(cam, x0 + 14, n * pitch, [q(112, -33), q(112, 33), q(132, 33), q(132, -33)], "m")
        heads = []
        for i in range(n):
            xa = x0 + 14 + i * pitch
            h = xpr(cam, xa + 4, pitch - 8, [q(132, -26), q(132, 26), q(146, 26), q(146, -26)], "pt", lines=detail > 1) if detail else ""
            if gas:
                p = q(146.2, 0)
                h += hole3(cam, (xa + pitch / 2, p[0], p[1]), (0, d[0], d[1]), 6, "dks2", 10)
            heads.append((dep(cam, (xa + pitch / 2, q(130, 0)[0], q(130, 0)[1])), h))
        o += "".join(h for _, h in sorted(heads, key=lambda t: -t[0]))
        return o

    def turbo(s):
        o = ""
        xt = x0 + 30
        for y0, y1, r, m in ((6, 30, 20, "dk"), (30, 36, 10, "m"), (36, 58, 25, "alu")):
            a, b = (y0, y1) if s > 0 else (-y0, -y1)
            o += cyl(cam, (xt, a, 158), (0, 1 if s > 0 else -1, 0), r, y1 - y0, m, seg=28, bands=8)
        o = xpr(cam, xt - 14, 28, [(s * 4, 108), (s * 26, 108), (s * 26, 140), (s * 4, 140)], "m", dark=1) + o
        return o
    body = zpr(cam, -95, 37, [(x0 + 18, -52), (x0 + L - 14, -52), (x0 + L - 14, 52), (x0 + 18, 52)], "pt", dark=1)
    feet = []
    for xf in (x0 + 30, x0 + L - 70):
        for s in (-1, 1):
            feet.append((s, zpr(cam, -42, 14, [(xf, s * 70), (xf + 46, s * 70), (xf + 46, s * 94), (xf, s * 94)], "pt", dark=1)))
    body += "".join(f for s, f in feet if s > 0)
    body += xpr(cam, x0, L, [(-60, -58), (60, -58), (72, -20), (72, 22), (-72, 22), (-72, -20)], "pt", dark=1)
    body += "".join(f for s, f in feet if s < 0)
    if detail > 1:
        for k, xx in enumerate((x0 + 120, x0 + 150)):
            body += cyl(cam, (xx, -84, -44), (0, 0, 1), 11, 40, "dk", seg=20, bands=8)
        body += cyl(cam, (x0 + L - 40, -76, -26), (1, 0, 0), 16, 44, "dk", seg=20, bands=8)       # starter
    body += bank(1)
    body += cyl(cam, (x0 + 12, 9, 92), (1, 0, 0), 9, L - 40, "alu", seg=20, bands=8)
    body += cyl(cam, (x0 + 12, -9, 92), (1, 0, 0), 9, L - 40, "alu", seg=20, bands=8)
    if detail > 1:
        body += turbo(1)
    body += bank(-1)
    if detail > 1:
        body += turbo(-1)
    return (fw + body + fr) if near0 else (fr + body + fw)


@part("genset.gsengine")
def _():
    def fn(sc):
        o = vengine(sc.cam)
        return o + man(sc, (480, -60, -95), 10)
    return fit(fn, 28, 20, (16, 14, 304, 180), sh_ry=7, sh_k=.46, sh_dy=-4)


def base3(sc, x0, x1, w=90, top=-60, ht=36, pads=()):
    """welded base frame: two channel rails, cross members, mounting pads."""
    z0 = top - ht
    for s in (-1, 1):
        y0, y1 = (w - 20, w) if s > 0 else (-w, -w + 20)
        BOX(sc, x0, min(y0, y1), z0, x1 - x0, 20, ht, "w", 0 if s < 0 else 0, dark=0 if s < 0 else 1)
    n_ = int((x1 - x0) / 120)
    for k in range(n_ + 1):
        xx = x0 + (x1 - x0 - 12) * k / n_
        BOX(sc, xx, -w + 20, z0 + 4, 12, 2 * w - 40, ht - 8, "w", dark=1)
    for xx, yy in pads:
        for s in (-1, 1):
            BOX(sc, xx, s * (w - 10) - 13, top, 26, 26, 4, "w")


@part("genset.gsbase")
def _():
    def fn(sc):
        base3(sc, 0, 640, 90, 0, 40, pads=[(60, 0), (200, 0), (300, 0), (430, 0), (560, 0)])
        for xx in (-14, 640):
            for s in (-1, 1):
                X(sc, xx, 14, [(s * 90 - 10, -30), (s * 90 + 10, -30), (s * 90 + 10, -6), (s * 90 - 10, -6)], "w", dark=1)

        def holes(s_):
            o = ""
            for xx in (60, 200, 300, 430, 560):
                for s in (-1, 1):
                    o += hole3(s_.cam, (xx + 13, s * 80, 4.1), (0, 0, 1), 4, "bg", 10)
            for s in (-1, 1):
                o += hole3(s_.cam, (-14.1, s * 90, -18), (-1, 0, 0), 5, "bg", 10)
            return o
        RAW(sc, holes, ((-15, -91, 4.1), (-14.1, 91, 4.2)), -3)
        return man(sc, (700, -110, -40), 10)
    return fit(fn, 24, 24, (16, 26, 304, 176), sh_ry=7, sh_k=.5, sh_dy=-3)


def fq(cam, pts, c="o"):
    return path(P([cam.xy(p) for p in pts]), c)


def yrect(cam, y, x0, z0, x1, z1, c="o"):
    """rectangle on the plane y = const (front faces)."""
    return fq(cam, ((x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)), c)


def xrect(cam, x, y0, z0, y1, z1, c="o"):
    return fq(cam, ((x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)), c)


def louvres(cam, y, x0, z0, x1, z1, n_):
    d = ""
    for k in range(n_):
        z = z0 + (z1 - z0) * (k + .5) / n_
        d += P([cam.xy((x0, y, z)), cam.xy((x1, y, z))], False)
    return yrect(cam, y, x0, z0, x1, z1, "dks3") + path(d, "el")


@part("genset.gsradiator")
def _():
    def fn(sc):
        cam = sc.cam
        o = zpr(cam, 0, 26, [(-136, -4), (136, -4), (136, 40), (-136, 40)], "pt", dark=1)          # bottom tank / skid
        o += zpr(cam, 26, 208, [(-136, 4), (136, 4), (136, 32), (-136, 32)], "w")                 # core block
        o += zpr(cam, 234, 26, [(-136, -2), (54, -2), (54, 38), (-136, 38)], "pt")                 # HT top tank
        o += zpr(cam, 234, 26, [(60, -2), (136, -2), (136, 38), (60, 38)], "pt")                   # LT top tank
        for xx, r in ((-90, 8), (96, 7)):
            o += cyl(cam, (xx, 18, 260), (0, 0, 1), r, 10, "m", seg=16, bands=6)
        for xx, r in ((-30, 14), (30, 14), (110, 10)):
            o += cyl(cam, (xx, 18, 260), (0, 0, 1), r, 22, "pt", seg=20, bands=8)
            o += cyl(cam, (xx, 18, 282), (0, 0, 1), r + 5, 4, "m", seg=20, bands=8)
        # fan side (toward viewer): shroud plate with venturi ring, fan, guard
        o += zpr(cam, 26, 208, [(-136, -8), (136, -8), (136, 4), (-136, 4)], "pt")
        C = (-30, -8, 128)
        o += path(P(circ3(cam, (C[0], -8.1, C[2]), (0, -1, 0), 96, 48)), "dks3")
        o += cyl(cam, (C[0], -8, C[2]), (0, -1, 0), 104, 18, "pt", seg=48, bands=12, holes=[GE.circle_outline(96, 48, 12)], dark=1)
        E1, E2, _ = GE.frame((0, -1, 0))
        bl = ""
        for k in range(7):
            a = 2 * math.pi * k / 7 + .3
            pts = []
            for r_, da in ((18, -.32), (90, -.18), (92, .12), (18, .2)):
                pts.append(cam.xy(_add(_add((C[0], -14, C[2]), E1, r_ * math.cos(a + da)), E2, r_ * math.sin(a + da))))
            bl += path(P(pts), "ms2")
        o += bl + cyl(cam, (C[0], -12, C[2]), (0, -1, 0), 20, 8, "dk", seg=24, bands=8)
        g = ""
        for r_ in (30, 52, 74, 96):
            g += P(circ3(cam, (C[0], -27, C[2]), (0, -1, 0), r_, 40))
        for k in range(8):
            a = 2 * math.pi * k / 8
            g += P([cam.xy(_add(_add((C[0], -27, C[2]), E1, r_ * math.cos(a)), E2, r_ * math.sin(a))) for r_ in (20, 98)], False)
        o += path(g, "el")
        o += yrect(cam, -8.1, 84, 40, 128, 220, "dks3")                                          # LT core section beside the fan
        o += path("".join(P([cam.xy((xx, -8.2, 42)), cam.xy((xx, -8.2, 218))], False) for xx in range(88, 128, 5)), "gr")
        return o
    return fit(fn, -26, 20, (40, 8, 280, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("genset.gsencl")
def _():
    L, W, H = 600, 240, 260

    def fn(sc):
        BOX(sc, -4, -4, -14, L + 8, W + 8, 14, "dk")
        BOX(sc, 0, 0, 0, L, W, H, "pt", ch=0)
        BOX(sc, 110, 80, H, 300, 80, 10, "m", dark=1)
        CYL(sc, (120, 120, H + 40), (1, 0, 0), 30, 240, "w", seg=32, bands=10)
        CYL(sc, (380, 120, H + 70), (0, 0, 1), 15, 60, "w", seg=20, bands=8)
        CYL(sc, (380, 120, H + 130), (0, 0, 1), 22, 6, "w", seg=20, bands=8, dark=1)
        BOX(sc, 470, 30, H, 110, 180, 8, "dk")

        def face(s_):
            cam = s_.cam
            o = louvres(cam, -.2, 20, 40, 130, 220, 12)
            o += louvres(cam, -.2, 150, 120, 240, 220, 8)
            for xx in (270, 360):
                o += yrect(cam, -.2, xx, 10, xx + 76, 214)
                o += yrect(cam, -.3, xx + 64, 104, xx + 69, 128, "dks2")
            o += yrect(cam, -.2, 460, 30, 580, 220)
            o += louvres(cam, -.3, 470, 140, 570, 210, 7)
            o += xrect(cam, L + .2, 30, 40, 210, 230, "dks3")
            d = ""
            for k in range(14):
                z = 50 + 170 * k / 13
                d += P([cam.xy((L + .3, 34, z)), cam.xy((L + .3, 206, z))], False)
            o += path(d, "el")
            return o
        RAW(sc, face, ((-.3, -.3, 0), (L + .3, -.2, H)), -3)
        return man(sc, (-40, -50, -14), 10)
    return fit(fn, -28, 20, (14, 14, 306, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("genset.gsdaytank")
def _():
    def fn(sc):
        BOX(sc, -90, -64, 0, 230, 128, 22, "w", dark=1)                                    # bund (oil pan)
        BOX(sc, -70, -42, 22, 120, 84, 130, "w", ch=4)                                      # tank
        BOX(sc, 70, -40, 22, 56, 36, 8, "m")                                                # pump base
        CYL(sc, (76, -22, 44), (1, 0, 0), 14, 22, "m", seg=20, bands=8)                     # pump
        CYL(sc, (98, -22, 44), (1, 0, 0), 15, 28, "pt", seg=24, bands=8)                    # motor
        CYL(sc, (-36, 0, 152), (0, 0, 1), 9, 14, "dk", seg=16, bands=6)                     # float switches
        CYL(sc, (-6, 0, 152), (0, 0, 1), 9, 14, "dk", seg=16, bands=6)
        CYL(sc, (30, 20, 152), (0, 0, 1), 5, 60, "w", seg=14, bands=6)                      # vent pipe
        CYL(sc, (30, 20, 212), (1, 0, 0), 6, 18, "w", seg=14, bands=6)
        CYL(sc, (50, -22, 60), (1, 0, 0), 5, 26, "w", seg=14, bands=6)                      # suction pipe to the pump

        def gauge(s_):
            cam = s_.cam
            o = yrect(cam, -42.3, -58, 34, -46, 144, "m")
            o += yrect(cam, -42.5, -55, 38, -49, 140, "gl")
            o += yrect(cam, -42.6, -55, 38, -49, 104, "fl")
            o += yrect(cam, -42.3, -10, 96, 30, 124, "o")
            return o
        RAW(sc, gauge, ((-70, -42.6, 22), (50, -42.2, 152)), -3)
    return fit(fn, -30, 22, (40, 12, 280, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("genset.gsexhaust")
def _():
    def fn(sc):
        cam = sc.cam
        BOX(sc, 90, -46, -76, 30, 92, 16, "pt", dark=1)
        BOX(sc, 280, -46, -76, 30, 92, 16, "pt", dark=1)
        CYL(sc, (-100, 0, 0), (1, 0, 0), 38, 8, "w", seg=32, bands=10)                      # inlet flange
        CYL(sc, (-92, 0, 0), (1, 0, 0), 27, 72, "w", seg=28, bands=10)                      # bellows
        RAW(sc, lambda s_: xlines(s_.cam, [-88 + 4 * k for k in range(17)], 27.4, "el"), ((-91, -28, -28), (-21, 28, 28)), -1)
        CYL(sc, (-20, 0, 0), (1, 0, 0), 38, 8, "w", seg=32, bands=10)
        CYL(sc, (-12, 0, 0), (1, 0, 0), 26, 32, "w", seg=28, bands=10)
        CYL(sc, (20, 0, 0), (1, 0, 0), 30, 8, "w", seg=28, bands=10)
        CYL(sc, (68, 0, 0), (-1, 0, 0), 62, 40, "w", seg=40, bands=12, r1=30)
        CYL(sc, (68, 0, 0), (1, 0, 0), 62, 260, "w", seg=48, bands=14)
        RAW(sc, lambda s_: xlines(s_.cam, (130, 200, 260), 62.4, "el"), ((69, -63, -63), (327, 63, 63)), -1)
        CYL(sc, (328, 0, 0), (1, 0, 0), 62, 34, "w", seg=40, bands=12, r1=34)
        CYL(sc, (300, 0, 50), (0, 0, 1), 24, 70, "w", seg=28, bands=10)
        CYL(sc, (300, 0, 120), (0, 0, 1), 34, 7, "w", seg=28, bands=10)
        return ""
    return fit(fn, 26, 22, (16, 16, 304, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


def genset_scene(sc, gas=False, rad=True, detail=1, gk=.7):
    """assembled set on its base: radiator (far, -x), engine, generator (near, +x). z: base top at -70."""
    n, pitch = 8, 40
    L = n * pitch + 30
    xg = L + 26
    base3(sc, -190 if rad else -40, xg + 380 * gk, 92, -70, 34, pads=())
    for xf in (30, L - 70):
        for s_ in (-1, 1):
            CYL(sc, (xf + 23, s_ * 82, -70), (0, 0, 1), 11, 28, "dk", seg=16, bands=6)
    RAW(sc, lambda s2: vengine(s2.cam, 0, n, pitch, detail, gas), ((-41, -95, -96), (L + 24, 95, 174)))
    generator3(sc, xg, gk, tb=True, disc=False, sg=.6)
    if rad:
        BOX(sc, -180, -120, -70, 30, 240, 250, "w")
        BOX(sc, -184, -124, 170, 38, 248, 18, "pt")
        BOX(sc, -150, -110, -60, 12, 220, 230, "pt", dark=1)
        CYL(sc, (-138, -30, 140), (1, 0, 0), 9, 100, "dk", seg=14, bands=6)
    if gas:
        for xx, L_ in ((-30, 80), (50, 260)):
            pass
        CYL(sc, (-30, -118, -40), (1, 0, 0), 7, 330, "gw", seg=16, bands=6)
        BOX(sc, 60, -128, -52, 34, 20, 26, "gw", ch=2)
        BOX(sc, 150, -128, -52, 34, 20, 26, "gw", ch=2)
        CYL(sc, (77, -118, -26), (0, 0, 1), 8, 22, "dk", seg=16, bands=6)
        CYL(sc, (167, -118, -26), (0, 0, 1), 8, 22, "dk", seg=16, bands=6)


@part("genset.gsassy")
def _():
    def fn(sc):
        genset_scene(sc)
        return man(sc, (720, -150, -104), 10)
    return fit(fn, -28, 20, (14, 12, 306, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("gasgen.geassy")
def _():
    def fn(sc):
        genset_scene(sc, gas=True, rad=False)
        return man(sc, (700, -160, -104), 10)
    return fit(fn, -28, 20, (14, 12, 306, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("genset.gstest")
def _():
    def fn(sc):
        genset_scene(sc, detail=0)
        # resistive load bank: container with side louvres and vertical discharge fans
        x0, y0 = 120, -520
        BOX(sc, x0, y0, -104, 360, 170, 190, "pt")
        BOX(sc, x0, y0, -118, 360, 170, 14, "dk")

        def lb(s_):
            cam = s_.cam
            o = louvres(cam, y0 - .2, x0 + 20, -80, x0 + 220, 60, 10)
            o += yrect(cam, y0 - .2, x0 + 250, -90, x0 + 340, 70)
            for xx in (x0 + 70, x0 + 180, x0 + 290):
                o += cyl(cam, (xx, y0 + 85, 86), (0, 0, 1), 44, 10, "m", seg=32, bands=8, dark=1)
                o += path(P(circ3(cam, (xx, y0 + 85, 96.2), (0, 0, 1), 38, 32)), "dks3")
                o += path(P(circ3(cam, (xx, y0 + 85, 96.4), (0, 0, 1), 10, 16)), "m")
            return o
        RAW(sc, lb, ((x0, y0 - .3, -104), (x0 + 360, y0 + 170, 106)), -3)

        def cables(s_):
            cam = s_.cam
            d = ""
            for k in range(3):
                a = cam.xy((L_tb[0] + 10 + k * 14, -40, 120))
                b = cam.xy((x0 + 300 - k * 14, y0 + 170, 0))
                d += "M%s %sC%s %s %s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] - 10), n(a[1] + 70), n(b[0] + 30), n(b[1] + 20), n(b[0]), n(b[1]))
            return '<path class="cable" d="%s"/>' % d
        return cables(sc)
    L_tb = (8 * 40 + 30 + 26 + 150 * .7,)
    return fit(fn, -28, 22, (14, 10, 306, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# dcpower — switchgear, breakers, transfer switch, paralleling panel, UPS, main fuel tank
# =====================================================================================
def dot(cam, p, r=2.2, c="dks2", A=(0, -1, 0)):
    return hole3(cam, p, A, r, c, 8)


def cubicles(sc, ws, d, h, x0=0):
    x = x0
    for w in ws:
        BOX(sc, x, 0, 0, w, d, h, "pt")
        x += w
    BOX(sc, x0, 2, -10, x - x0, d - 4, 10, "dk")
    return x


@part("dcpower.dclvswgr")
def _():
    ws = [90, 70, 70, 90]

    def fn(sc):
        X1 = cubicles(sc, ws, 100, 230)

        def face(s_):
            cam = s_.cam
            o = ""
            x = 0
            for i, w in enumerate(ws):
                y = -.2
                if i in (0, 3):
                    o += yrect(cam, y, x + 6, 200, x + w - 6, 224)
                    for k in range(2):
                        o += hole3(cam, (x + 24 + k * 30, -.3, 212), (0, -1, 0), 7, "w3", 16)
                    o += yrect(cam, y, x + 6, 70, x + w - 6, 194)
                    o += yrect(cam, -.3, x + 14, 96, x + w - 14, 170, "dks2")
                    o += yrect(cam, -.4, x + 22, 132, x + w - 22, 160, "m")
                    o += yrect(cam, -.5, x + 26, 140, x + 46, 152, "scrn")
                    o += dot(cam, (x + 30, -.4, 116), 4, "w3") + dot(cam, (x + 44, -.4, 116), 4, "w3")
                    o += yrect(cam, y, x + 6, 8, x + w - 6, 64)
                else:
                    for k in range(6):
                        z0 = 10 + k * 36
                        o += yrect(cam, y, x + 5, z0, x + w - 5, z0 + 33)
                        o += yrect(cam, -.3, x + w / 2 - 8, z0 + 8, x + w / 2 + 8, z0 + 25, "dks2")
                        o += yrect(cam, -.4, x + w / 2 - 2.5, z0 + 13, x + w / 2 + 2.5, z0 + 20, "m")
                x += w
            return o
        RAW(sc, face, ((0, -.5, 0), (X1, -.2, 230)), -3)
    return fit(fn, -28, 18, (40, 10, 280, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcmvswgr")
def _():
    ws = [90, 90, 90]

    def fn(sc):
        X1 = cubicles(sc, ws, 170, 240)
        BOX(sc, 0, 120, 240, X1, 50, 34, "pt", dark=1)                     # arc-gas duct on the roof
        for k in range(3):
            BOX(sc, 10 + k * 90, 20, 240, 70, 70, 5, "m")                   # pressure-relief flaps

        def face(s_):
            cam = s_.cam
            o = ""
            for k in range(3):
                x = k * 90
                o += yrect(cam, -.2, x + 6, 184, x + 84, 234)
                o += yrect(cam, -.3, x + 14, 210, x + 44, 226, "scrn")
                for j in range(4):
                    o += dot(cam, (x + 54 + j * 7, -.3, 218), 2.4, "dks2")
                o += yrect(cam, -.2, x + 6, 84, x + 84, 178)
                o += yrect(cam, -.3, x + 20, 112, x + 70, 160, "dks3")
                o += yrect(cam, -.4, x + 22, 114, x + 68, 158, "gl")
                o += dot(cam, (x + 45, -.3, 98), 4.5, "bg")
                o += yrect(cam, -.3, x + 76, 120, x + 80, 146, "dks2")
                o += yrect(cam, -.2, x + 6, 8, x + 84, 78)
                for zz in (16, 70):
                    o += dot(cam, (x + 12, -.3, zz), 1.6) + dot(cam, (x + 78, -.3, zz), 1.6)
            return o
        RAW(sc, face, ((0, -.5, 0), (X1, -.2, 240)), -3)
    return fit(fn, -30, 18, (40, 10, 280, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcvcb")
def _():
    def fn(sc):
        BOX(sc, -70, -44, 0, 140, 170, 18, "m", dark=1)                      # truck chassis
        for xx in (-74, 70):
            for yy in (-26, 104):
                CYL(sc, (xx, yy, 2), (1, 0, 0), 10, 4, "dk", seg=16, bands=6)
        BOX(sc, -64, -44, 18, 128, 56, 110, "pt", ch=3)                       # mechanism housing
        for xx in (-42, 0, 42):
            CYL(sc, (xx, 44, 18), (0, 0, 1), 19, 132, "dk", seg=28, bands=8)   # embedded poles (epoxy)
            CYL(sc, (xx, 44, 150), (0, 0, 1), 12, 6, "alu", seg=20, bands=6)
            for zz in (126, 52):
                CYL(sc, (xx, 63, zz), (0, 1, 0), 8, 60, "alu", seg=18, bands=6)
                CYL(sc, (xx, 123, zz), (0, 1, 0), 14, 24, "cu", seg=20, bands=6)

        def face(s_):
            cam = s_.cam
            o = yrect(cam, -44.2, -54, 70, 54, 120, "o")
            o += dot(cam, (-32, -44.3, 98), 6.5, "dks2") + dot(cam, (-10, -44.3, 98), 6.5, "w3")
            o += yrect(cam, -44.3, 10, 92, 30, 104, "w3") + yrect(cam, -44.3, 34, 92, 50, 104, "dks2")
            o += yrect(cam, -44.3, 14, 78, 44, 86, "scrn")
            o += dot(cam, (0, -44.3, 40), 5, "bg") + yrect(cam, -44.2, -54, 26, 54, 62, "o")
            return o
        RAW(sc, face, ((-64, -44.4, 18), (64, -44.2, 128)), -3)
    return fit(fn, -32, 20, (44, 10, 276, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcacb")
def _():
    def fn(sc):
        for k in range(3):
            for zz in (24, 84):
                BOX(sc, -42 + k * 34, 96, zz, 14, 40, 26, "cu")             # rear terminals
        BOX(sc, -64, 0, 0, 128, 96, 130, "dk", ch=3)                          # moulded body
        BOX(sc, -56, -16, 8, 112, 16, 112, "m", ch=2)                         # front fascia

        def face(s_):
            cam = s_.cam
            o = ""
            d = ""
            for k in range(6):                                                # arc-chute vents on the top
                xx = -50 + k * 20
                d += P([cam.xy(p) for p in ((xx, 18, 130.2), (xx + 12, 18, 130.2), (xx + 12, 80, 130.2), (xx, 80, 130.2))])
            o += path(d, "dks3")
            o += yrect(cam, -16.2, -46, 74, -4, 108, "dks2")                    # trip unit
            o += yrect(cam, -16.3, -40, 90, -12, 102, "scrn")
            for j in range(3):
                o += dot(cam, (-38 + j * 11, -16.3, 81), 2.4, "w3")
            o += dot(cam, (14, -16.3, 96), 7, "w3") + dot(cam, (34, -16.3, 96), 7, "dks2")       # ON / OFF
            o += yrect(cam, -16.3, 8, 74, 20, 82, "w3") + yrect(cam, -16.3, 28, 74, 40, 82, "w3")
            o += yrect(cam, -16.2, -30, 18, 30, 58, "dks2")                     # charging handle recess
            o += fq(cam, ((-8, -16.4, 24), (8, -16.4, 24), (6, -26, 52), (-6, -26, 52)), "ms2")
            return o
        RAW(sc, face, ((-56, -26, 8), (56, -16.2, 131)), -3)
    return fit(fn, -30, 22, (60, 10, 260, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcats")
def _():
    def fn(sc):
        BOX(sc, -160, -20, -10, 320, 140, 10, "m", dark=1)                    # mounting plate
        for x0 in (-150, 30):
            BOX(sc, x0, 0, 0, 120, 100, 96, "dk", ch=3)                       # source-N / source-E switch units
            for k in range(3):
                for zz in (10, 66):
                    BOX(sc, x0 + 14 + k * 36, -22, zz, 20, 22, 12, "cu")
        BOX(sc, -26, 10, 0, 52, 80, 124, "pt", ch=3)                          # transfer mechanism / operator
        CYL(sc, (-150, 50, 112), (1, 0, 0), 6, 300, "m", seg=14, bands=6)      # mechanical interlock bar
        CYL(sc, (0, 10, 92), (0, -1, 0), 8, 30, "m", seg=16, bands=6)          # manual operating shaft
        BOX(sc, -6, -36, 84, 12, 16, 40, "dk")

        def face(s_):
            cam = s_.cam
            o = yrect(cam, 9.8, -18, 40, 18, 62, "scrn")
            for k in range(3):
                o += dot(cam, (-12 + k * 12, 9.8, 30), 2.4, "dks2")
            d = ""
            for x0 in (-150, 30):
                for k in range(5):
                    xx = x0 + 12 + k * 22
                    d += P([cam.xy(p) for p in ((xx, 20, 96.2), (xx + 12, 20, 96.2), (xx + 12, 80, 96.2), (xx, 80, 96.2))])
            return o + path(d, "dks3")
        RAW(sc, face, ((-26, 9.7, 0), (26, 9.8, 124)), -3)
    return fit(fn, -30, 24, (24, 16, 296, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcsync")
def _():
    ws = [90, 90]

    def fn(sc):
        X1 = cubicles(sc, ws, 80, 230)

        def face(s_):
            cam = s_.cam
            o = yrect(cam, -.2, 6, 8, 84, 224) + yrect(cam, -.2, 96, 8, 174, 224)
            o += yrect(cam, -.3, 18, 168, 72, 204, "dks2") + yrect(cam, -.4, 21, 171, 69, 201, "scrn")
            for k in range(3):
                o += hole3(cam, (22 + k * 23, -.3, 146), (0, -1, 0), 9, "w3", 18)
                o += path(P([cam.xy((22 + k * 23, -.4, 146)), cam.xy((22 + k * 23 + 5, -.4, 152))], False), "el")
            for k in range(3):
                o += dot(cam, (24 + k * 21, -.3, 118), 4, "dks2")
                o += dot(cam, (24 + k * 21, -.3, 100), 4.5, "m")
                o += yrect(cam, -.4, 22 + k * 21, 98, 26 + k * 21, 108, "dks2")
            for r_ in range(4):
                for c_ in range(2):
                    x0, z0 = 106 + c_ * 34, 176 - r_ * 34
                    o += yrect(cam, -.3, x0, z0, x0 + 26, z0 + 28, "m")
                    o += yrect(cam, -.4, x0 + 4, z0 + 16, x0 + 22, z0 + 24, "scrn")
                    o += dot(cam, (x0 + 7, -.4, z0 + 8), 1.8) + dot(cam, (x0 + 13, -.4, z0 + 8), 1.8)
            o += yrect(cam, -.3, 80, 100, 83, 124, "dks2") + yrect(cam, -.3, 170, 100, 173, 124, "dks2")
            return o
        RAW(sc, face, ((0, -.5, 0), (X1, -.2, 230)), -3)
    return fit(fn, -28, 18, (50, 10, 270, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcups")
def _():
    ws = [110, 80, 80]

    def fn(sc):
        X1 = cubicles(sc, ws, 90, 200)

        def face(s_):
            cam = s_.cam
            o = yrect(cam, -.2, 6, 8, 104, 194)
            o += yrect(cam, -.3, 20, 150, 60, 176, "scrn")
            o += louvres(cam, -.3, 16, 20, 94, 130, 14)
            o += yrect(cam, -.2, 116, 8, 184, 194)
            o += louvres(cam, -.3, 124, 150, 176, 186, 5)
            o += yrect(cam, -.3, 178, 90, 181, 112, "dks2")
            o += yrect(cam, -.2, 194, 6, 266, 196, "dks3")                         # open battery cabinet
            for k in range(7):
                z0 = 12 + k * 26
                o += yrect(cam, -1, 198, z0, 262, z0 + 22, "m")
                o += yrect(cam, -1.1, 204, z0 + 8, 222, z0 + 14, "dks2")
                o += dot(cam, (252, -1.1, z0 + 11), 1.8, "w3")
            return o
        RAW(sc, face, ((0, -1.2, 0), (X1, -.2, 200)), -3)
    return fit(fn, -28, 18, (40, 10, 280, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("dcpower.dcfuel")
def _():
    def fn(sc):
        cam = sc.cam
        for xx in (60, 260):
            BOX(sc, xx, -50, 0, 30, 100, 26, "dk", dark=1)                     # saddles / foundation
        CYL(sc, (0, 0, 96), (-1, 0, 0), 84, 16, "pt", seg=48, bands=12, r1=58)
        CYL(sc, (0, 0, 96), (1, 0, 0), 84, 340, "pt", seg=56, bands=14)        # FRP outer shell
        CYL(sc, (340, 0, 96), (1, 0, 0), 84, 16, "pt", seg=48, bands=12, r1=58)
        RAW(sc, lambda s_: xlines(s_.cam, (60, 120, 180, 240, 300), 84.3, "gr"), ((1, -85, 10), (339, 85, 182)), -1)
        for xx in (90, 250):
            CYL(sc, (xx, 0, 170), (0, 0, 1), 26, 40, "pt", seg=28, bands=8)      # manhole risers
            CYL(sc, (xx, 0, 210), (0, 0, 1), 32, 6, "m", seg=32, bands=8)
        CYL(sc, (170, -30, 172), (0, 0, 1), 4, 56, "w", seg=12, bands=6)       # leak detector tube
        # transfer pump unit
        BOX(sc, 400, -80, 0, 130, 120, 10, "m", dark=1)
        for yy in (-50, 0):
            CYL(sc, (412, yy, 34), (1, 0, 0), 15, 40, "pt", seg=24, bands=8)
            CYL(sc, (452, yy, 34), (1, 0, 0), 13, 22, "m", seg=24, bands=8)
            BOX(sc, 410, yy - 14, 10, 70, 28, 10, "m")
        CYL(sc, (500, -66, 60), (0, 1, 0), 7, 100, "w", seg=14, bands=6)
        CYL(sc, (500, -30, 10), (0, 0, 1), 7, 50, "w", seg=14, bands=6)
        BOX(sc, 500, 30, 10, 26, 18, 60, "pt")
        return ""
    return fit(fn, -26, 22, (14, 18, 306, 178), sh_ry=7, sh_k=.5, sh_dy=-3)
