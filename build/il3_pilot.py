"""v3 pilot drawings (shaded 3D style): engine crankshaft & piston, brake disc, e-motor stator,
NC lathe and horizontal machining centre principle drawings. Overrides the older flat drawings."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il_pictos import picto, lab, chips
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3


# =====================================================================================
# engine.crank — inline-4 crankshaft: 5 journals, 4 pins (1-4 / 2-3 opposed), 8 counterweights
# =====================================================================================
def crank(phi0=95, az=22, el=20, wcap="w3", jm="w", wd=1):
    rj, rp, e, tw, lj, lp, rl, rc = 26, 22.5, 45, 13, 24, 26, 28, 60

    def web(phi):
        py, pz = e * math.cos(math.radians(phi)), e * math.sin(math.radians(phi))
        pts = arc(py, pz, rl, phi - 90, phi + 90, 8) + arc(0, 0, rc, phi + 180 - 56, phi + 180 + 56, 8)
        return banded(hull(pts), 2)

    def fn(sc):
        # rear end (near, left): flywheel flange with bolt circle and pilot bore, oil-seal land
        def face(s_):
            o = hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 11, "w3")
            o += hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 7, "bg")
            for k in range(6):
                a = 2 * math.pi * (k + .5) / 6
                o += hole3(s_.cam, (-.1, 29 * math.cos(a), 29 * math.sin(a)), (-1, 0, 0), 3.4)
            return o
        RAW(sc, face, ((-.2, -42, -42), (0, 42, 42)), -2)
        CYL(sc, (0, 0, 0), (1, 0, 0), 42, 11, "w")
        CYL(sc, (11, 0, 0), (1, 0, 0), 30, 10, "w")
        x = 21
        phis = [phi0, phi0 + 180, phi0 + 180, phi0]
        for i, ph in enumerate(phis):
            CYL(sc, (x, 0, 0), (1, 0, 0), rj, lj, jm)
            x += lj
            py, pz = e * math.cos(math.radians(ph)), e * math.sin(math.radians(ph))
            X(sc, x, tw, web(ph), "w", smooth=True, dark=wd, cap_mat=wcap)
            x += tw
            CYL(sc, (x, py, pz), (1, 0, 0), rp, lp, jm)
            xo = x + lp / 2

            def oil(s_, xo=xo, py=py, pz=pz, ph=ph):
                a = math.radians(ph + 150)
                nrm = (0, math.cos(a), math.sin(a))
                return hole3(s_.cam, (xo, py + rp * nrm[1], pz + rp * nrm[2]), nrm, 2.6)
            RAW(sc, oil, ((x + 1, py - rp, pz - rp), (x + lp - 1, py + rp, pz + rp)), -1)
            x += lp
            X(sc, x, tw, web(ph), "w", smooth=True, dark=wd, cap_mat=wcap)
            x += tw
        CYL(sc, (x, 0, 0), (1, 0, 0), rj, lj, jm)
        x += lj
        # nose (front end, far right): pulley spigot, sprocket seat, seal surface
        for L, r in ((14, 19), (18, 16), (24, 13)):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=20, bands=10)
            x += L
    return fit(fn, az, el, (24, 30, 296, 172), sh_ry=7, sh_k=.46)


@part("engine.crank")
def _():
    return crank()



# =====================================================================================
# engine.piston — Al piston: crown with valve reliefs, 3 ring grooves (top / 2nd / oil with drain
# holes), slipper skirt on the thrust sides, pin boss with pin bore on the recessed pin side
# =====================================================================================
def piston(az=-30, el=28):
    R, zs, zp = 40, 34, 20
    yf = 0.8 * R

    def fn(sc):
        sk = arc(0, 0, R, -38, 38, 8) + [(0.42 * R, yf), (-0.42 * R, yf)] + arc(0, 0, R, 142, 218, 8) + [(-0.42 * R, -yf), (0.42 * R, -yf)]
        Z(sc, 0, zs, banded(sk, 2), "w", smooth="outer")
        # pin boss on the (front) pin side
        CYL(sc, (0, -yf, zp), (0, -1, 0), 13, 2.5, "w", seg=24)

        def bore(s_):
            c = (0, -yf - 2.6, zp)
            return hole3(s_.cam, c, (0, -1, 0), 10, "w3") + hole3(s_.cam, c, (0, -1, 0), 8.6, "bg")
        RAW(sc, bore, ((-13, -yf - 2.7, zp - 13), (13, -yf - 2.6, zp + 13)), -1)
        # ring belt: lands and grooves, bottom to top
        belt = [(zs, 40.5, R, 0), (40.5, 43.5, R - 2.4, 2), (43.5, 47.5, R, 0), (47.5, 49, R - 2.2, 2),
                (49, 53.5, R, 0), (53.5, 55, R - 2.2, 2), (55, 60, R - .3, 0)]
        for z0, z1, r, dk in belt:
            CYL(sc, (0, 0, z0), (0, 0, 1), r, z1 - z0, "w", seg=48, bands=16, dark=dk)

        def marks(s_):
            o = ""
            for a in (-112, -94, -76, -58):          # oil-return holes in the oil-ring groove
                t = math.radians(a)
                o += hole3(s_.cam, ((R - 2.3) * math.cos(t), (R - 2.3) * math.sin(t), 42), (math.cos(t), math.sin(t), 0), 1.1)
            for (x, y, r) in ((-15, 15, 8.5), (15, 15, 8.5), (-15, -15, 7.5), (15, -15, 7.5)):   # valve reliefs
                o += hole3(s_.cam, (x, y, 60.05), (0, 0, 1), r, "w2", 24)
            return o
        RAW(sc, marks, ((-R, -R, 60.1), (R, R, 60.2)), -3)
    return fit(fn, az, el, (70, 14, 250, 176), sh_ry=8, sh_k=.62, sh_dy=-6)


@part("engine.piston")
def _():
    return piston()


# =====================================================================================
# chassis.disc — ventilated brake disc: two friction rings joined by radial vanes, hat with
# wheel-bolt holes and pilot bore. Disc stands on edge, axis horizontal (outboard face toward -y).
# =====================================================================================
def disc(az=38, el=16, nv=40):
    R, Ri, t, g, rh, Hh = 150, 92, 11, 12, 84, 40
    A = (0, -1, 0)

    def fn(sc):
        cam = sc.cam
        o = compact(GE.prism(cam, (0, g / 2 + t, 0), A, GE.circle_outline(R, 64, 16), t, "w", holes=[GE.circle_outline(rh, 40, 10)],
                             smooth=True))
        o += compact(GE.prism(cam, (0, g / 2, 0), A, GE.circle_outline(R - 1.5, 64, 16), g, "w", smooth=True, caps=False, dark=2))
        vanes = []
        for k in range(nv):
            a = 2 * math.pi * (k + .5) / nv
            c, s_ = math.cos(a), math.sin(a)
            w = 2.6
            loop = [(r * c - q * w * s_, r * s_ + q * w * c, i) for i, (r, q) in enumerate(((Ri + 2, -1), (R - .5, -1), (R - .5, 1), (Ri + 2, 1)))]
            E1, E2, _ = GE.frame(A)
            rad = tuple(c * E1[j] + s_ * E2[j] for j in range(3))
            if GE._dot(rad, cam.D) > 0.05:      # vane end faces away: hidden between the plates
                continue
            mid = tuple((R - 10) * rad[j] for j in range(3))
            vanes.append((cam.P(mid)[2], GE.prism(cam, (0, g / 2, 0), A, loop, g, "w", caps=False, lines=False)))
        o += "".join(v for _, v in sorted(vanes, key=lambda v: -v[0]))
        o += compact(GE.prism(cam, (0, -g / 2, 0), A, GE.circle_outline(R, 64, 16), t, "w", holes=[GE.circle_outline(Ri, 48, 12)], smooth=True))
        y0 = -g / 2 - t
        # friction face: faint turning marks
        for r in (Ri + 14, Ri + 30, R - 12):
            o += path(P(circ3(cam, (0, y0 - .1, 0), A, r, 48)), "gr")
        # hat: wall, dark interior, top with wheel-bolt holes and pilot bore
        o += compact(GE.prism(cam, (0, y0 + 2, 0), A, GE.circle_outline(rh, 40, 14), Hh - 7 + 2, "w", holes=[GE.circle_outline(rh - 6, 40, 10)],
                              smooth=True, caps=False))
        o += path(P(circ3(cam, (0, y0 - Hh + 7, 0), A, rh - 6, 40)), "bg")
        holes = [GE.circle_outline(33, 28, 7)]
        for k in range(5):
            a = 2 * math.pi * k / 5 + math.pi / 2
            holes.append(GE.circle_outline(7.5, 14, 4, 57 * math.cos(a), 57 * math.sin(a)))
        o += compact(GE.prism(cam, (0, y0 - Hh + 7, 0), A, GE.circle_outline(rh, 40, 14), 7, "w", holes=holes, smooth=True))
        return o
    return fit(fn, az, el, (40, 10, 280, 182), sh_ry=7, sh_k=.42, sh_dy=-2)


@part("chassis.disc")
def _():
    return disc()


# =====================================================================================
# ev.stator — hairpin stator: laminated core (lamination lines, slots at the bore), weld-end
# crown of leaning hairpin legs (two rows leaning opposite ways), U-turn crown below, 3 phase leads
# =====================================================================================
def lam_lines(cam, R, H, n_, A=(0, 0, 1)):
    """lamination / stack lines on the visible half of a vertical cylinder (radius R, height H)."""
    d = ""
    a0 = math.degrees(math.atan2(-cam.D[1], -cam.D[0]))     # direction facing the viewer
    for j in range(1, n_):
        z = H * j / n_
        d += P([cam.xy((R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), z)) for a in range(int(a0) - 88, int(a0) + 89, 8)], False)
    return path(d, "gr")


def stator(az=-30, el=30, ns=36):
    R, Ri, H, hc = 110, 78, 58, 20
    rows = [(Ri + 2.5, Ri + 9, 1), (Ri + 10, Ri + 16.5, -1)]

    def fn(sc):
        cam = sc.cam
        o = GE.prism(cam, (0, 0, 0), (0, 0, 1), GE.circle_outline(R, 64, 16), H, "w", holes=[GE.circle_outline(Ri, ns * 2, ns)])
        o += lam_lines(cam, R, H, 9)
        blocks = []
        dlt = 1.5 * 2 * math.pi / ns
        for k in range(ns):
            a = 2 * math.pi * (k + .5) / ns
            c, s_ = math.cos(a), math.sin(a)
            for r0, r1, sg in rows:
                w = 2.4
                loop = [(r * c - q * w * s_, r * s_ + q * w * c, i) for i, (r, q) in enumerate(((r0, -1), (r1, -1), (r1, 1), (r0, 1)))]
                am = a + sg * dlt / 2
                rm = (r0 + r1) / 2
                dep = cam.P((rm * math.cos(am), rm * math.sin(am), H + hc / 2))[2]
                blocks.append((dep, GE.prism(cam, (0, 0, H), (0, 0, 1), [(-v, u, f) for u, v, f in loop], hc, "cu",
                                             twist=sg * dlt, lines=False)))
        # three phase leads standing up at the back
        for j in range(3):
            a = math.radians(70 + j * 12)
            c, s_ = math.cos(a), math.sin(a)
            loop = [(r * c - q * 3.2 * s_, r * s_ + q * 3.2 * c, i) for i, (r, q) in enumerate(((Ri + 4, -1), (Ri + 14, -1), (Ri + 14, 1), (Ri + 4, 1)))]
            dep = cam.P(((Ri + 9) * c, (Ri + 9) * s_, H + 30))[2]
            blocks.append((dep, GE.prism(cam, (0, 0, H), (0, 0, 1), [(-v, u, f) for u, v, f in loop], hc + 22, "cu")))
        o += "".join(b for _, b in sorted(blocks, key=lambda b: -b[0]))
        return o
    return fit(fn, az, el, (40, 10, 280, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("ev.stator")
def _():
    return stator()


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


# =====================================================================================
# q:turn — NC lathe: chuck spins the work, the tool (insert on a holder) feeds along the axis
# =====================================================================================
@picto("turn")
def _():
    xt = 104                                  # tool tip position along the axis

    def fn(sc):
        CYL(sc, (-46, 0, 0), (1, 0, 0), 32, 24, "dk", seg=32)               # spindle nose
        CYL(sc, (-22, 0, 0), (1, 0, 0), 48, 30, "m", seg=40)               # chuck body
        for k in range(3):                                                  # three jaws
            t = math.radians(90 + k * 120)
            c, s_ = math.cos(t), math.sin(t)
            X(sc, 8, 14, [(u * c - v * s_, u * s_ + v * c) for u, v in ((27, -7), (44, -7), (44, 7), (27, 7))], "dk", -1)
        # work: raw bar (left of the tool), turned diameter (right of the tool)
        CYL(sc, (8, 0, 0), (1, 0, 0), 26, xt - 8, "w", seg=32)
        CYL(sc, (xt, 0, 0), (1, 0, 0), 20, 160 - xt, "w", seg=32)
        # tool: square holder coming from the front, rhombic insert at the tip (rake face at centre height)
        BOX(sc, xt + 2, -104, -18, 24, 72, 14, "m", -3)
        ins = [(xt, -20.3), (xt + 15, -37), (xt + 29, -31), (xt + 14, -14.5)]
        Z(sc, -4, 4, ins, "t", -4)
    s, sc = fit(fn, -36, 20, (20, 26, 300, 168), sh_ry=6, sh_k=.4, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (46, 0, 0), (1, 0, 0), 34, 50, 160)
    s += arrow3(cam, (xt + 80, -64, -10), (xt + 34, -64, -10))
    tx, ty = cam.xy((xt + 1, -21, 0))
    s += chips(tx + 2, ty - 3, 1.0)
    a, b = cam.xy((46, 20, 34)), cam.xy((xt + 57, -64, -10))
    s += al(a[0] + 6, a[1] - 10, "回転", "start") + al(b[0] + 4, b[1] + 18, "送り")
    w = cam.xy((160, 0, 20))
    h = cam.xy((xt + 10, -100, -17))
    s += lab(w[0] - 4, w[1] - 34, "工作物") + lab(h[0] - 8, h[1] + 4, "バイト", "end")
    return s


# =====================================================================================
# q:mc_h — horizontal machining centre: horizontal spindle on the column feeds into a box part
# clamped on a pallet; the pallet indexes (B axis) so several faces are machined in one setup
# =====================================================================================
@picto("mc_h")
def _():
    zs = 52                                    # spindle height

    def fn(sc):
        BOX(sc, -60, -70, -66, 190, 140, 26, "pt", dark=1)                 # bed under the table
        BOX(sc, -170, -44, -66, 40, 88, 176, "pt", dark=1)                 # column
        BOX(sc, -130, -32, zs - 30, 58, 64, 58, "pt", ch=5)                 # spindle head
        CYL(sc, (-72, 0, zs), (1, 0, 0), 24, 12, "dk", seg=28)             # spindle nose
        CYL(sc, (-60, 0, zs), (1, 0, 0), 15, 16, "m", seg=24, r1=9)        # tool holder (taper)
        CYL(sc, (-44, 0, zs), (1, 0, 0), 7, 40, "t", seg=20)               # end mill / drill
        CYL(sc, (45, 0, -40), (0, 0, 1), 62, 26, "m", seg=48)              # rotary (B) table
        BOX(sc, -14, -62, -14, 118, 124, 14, "m")                          # pallet
        BOX(sc, -4, -46, 0, 98, 92, 100, "w", ch=6)                        # box-shaped work (casting)

        def marks(s_):
            o = ""
            for y, z, r in ((-22, 70, 9), (22, 70, 9), (0, 28, 12)):
                o += hole3(s_.cam, (-4.2, y, z), (-1, 0, 0), r)
            for x, y in ((24, -22), (66, -22), (24, 22), (66, 22)):
                o += hole3(s_.cam, (x, y, 100.2), (0, 0, 1), 5)
            return o
        RAW(sc, marks, ((-4.4, -46, 0), (-4.2, 46, 100.3)), -2)
    s, sc = fit(fn, 30, 20, (34, 30, 272, 168), sh_ry=7, sh_k=.44, ret_scene=True)
    cam = sc.cam
    s += arc3(cam, (-56, 0, zs), (1, 0, 0), 26, 100, 200)
    s += arrow3(cam, (-108, 0, zs + 44), (-58, 0, zs + 44))
    s += arc3(cam, (45, 0, -27), (0, 0, 1), 90, -70, 30)
    h = cam.xy((-108, 0, zs + 44))
    w = cam.xy((45, 0, 100))
    b = cam.xy((45, -90, -27))
    p = cam.xy((104, -62, -7))
    s += lab(h[0] - 30, h[1] - 12, "主軸（水平）", "middle") + lab(w[0], w[1] - 26, "工作物")
    s += al(b[0] + 10, b[1] + 27, "B軸割出し") + lab(p[0] + 8, p[1] + 4, "パレット", "start")
    return s
