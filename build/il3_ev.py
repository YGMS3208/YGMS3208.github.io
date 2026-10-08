"""v3 shaded-3D part drawings: electrified drive unit (ev.*, except the stator in il3_pilot)
and electrical / electronics (electrical.*)."""
import math
import re
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P
from il3_pilot import lam_lines


# ------------------------------------------------------------------ local helpers (manual back-to-front drawing)
def zb(cam, x, y, z, sx, sy, sz, mat="w", ch=0, **kw):
    """axis-aligned box svg (no Scene ordering) from corner (x, y, z)."""
    c = ch
    xy = [(x, y), (x + sx, y), (x + sx, y + sy), (x, y + sy)] if not c else \
        [(x + c, y), (x + sx - c, y), (x + sx, y + c), (x + sx, y + sy - c), (x + sx - c, y + sy), (x + c, y + sy), (x, y + sy - c), (x, y + c)]
    return zp(cam, z, sz, xy, mat, **kw)


def zp(cam, z0, h, xy, mat="w", **kw):
    """(x, y) outline extruded up from z0 (no Scene)."""
    loop = [(-p[1], p[0], p[2] if len(p) > 2 else i) for i, p in enumerate(xy)]
    return compact(GE.prism(cam, (0, 0, z0), (0, 0, 1), loop, h, mat, **kw))


def cy(cam, O, A, r, h, mat="w", seg=24, bands=10, holes=(), **kw):
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, bands), h, mat, holes=list(holes),
                            smooth="outer" if holes else True, **kw))


def quad(cam, pts, c):
    """flat polygon through world points."""
    return path(P([cam.xy(p) for p in pts]), c)


def fx(cam, x, pts, c):
    """flat polygon on the plane x = const, pts as (y, z)."""
    return quad(cam, [(x, a, b) for a, b in pts], c)


def fy(cam, y, pts, c):
    """flat polygon on the plane y = const, pts as (x, z)."""
    return quad(cam, [(a, y, b) for a, b in pts], c)


def fz(cam, z, pts, c):
    """flat polygon on the plane z = const, pts as (x, y)."""
    return quad(cam, [(a, b, z) for a, b in pts], c)


def rect(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


_RUN = re.compile(r'(?:<path class="([^"]+)" d="[^"]*"/>)(?:<path class="\1" d="[^"]*"/>)+')
_PD = re.compile(r'd="([^"]*)"')


def mrg(svg):
    """join consecutive paths of the same class into one element (same paint order, fewer bytes)."""
    return _RUN.sub(lambda m: '<path class="%s" d="%s"/>' % (m.group(1), "".join(_PD.findall(m.group(0)))), svg)


def sgear(z, rp, phase=0.0, ra=None, rf=None, lite=False):
    """light-weight external gear outline: straight-flank teeth (4 points per tooth), teeth centred at phase."""
    m = 2.0 * rp / z
    ra = rp + m if ra is None else ra
    rf = rp - 1.25 * m if rf is None else rf
    hp = math.pi / (2 * z)
    pts = []
    for i in range(z):
        c = phase + 2 * math.pi * i / z
        fs = (0, 1, 1, 4) if lite else (0, 1, 2, 3)
        for (a, r), f in zip(((c - hp * 1.5, rf), (c - hp * .62, ra), (c + hp * .62, ra), (c + hp * 1.5, rf)), fs):
            pts.append((r * math.cos(a), r * math.sin(a), (4 * i + f) % (4 * z) if lite else 4 * i + f))
    return pts


def sring(z, rp, phase=0.0):
    """void outline of an internal gear (ring teeth centred at phase)."""
    m = 2.0 * rp / z
    return sgear(z, rp, phase + math.pi / z, rp + 1.25 * m, rp - .9 * m, lite=True)


def mesh2(z1, ph1, z2, th):
    """phase of an external gear z2 whose centre lies in direction th from gear z1 (phase ph1)."""
    return th + math.pi - (math.pi - z1 * (th - ph1)) / z2


def depth_sorted(cam, items):
    """items: [(world centre, svg)] -> svg drawn far to near."""
    return "".join(s for _, s in sorted(((cam.P(c)[2], s) for c, s in items), key=lambda t: -t[0]))


# =====================================================================================
# ev.rotor — IPM rotor: laminated core with V-shaped magnet pockets (8 poles) and flux-barrier holes,
# hollow shaft through it (bearing collar, spline end). Same view / touch as the stator.
# =====================================================================================
def rotor(az=-30, el=30, np_=8):
    R, H, rs = 86, 64, 21

    def fn(sc):
        cam = sc.cam
        o = cy(cam, (0, 0, -40), (0, 0, 1), rs - 3, 16, "w", seg=28)
        o += cy(cam, (0, 0, -24), (0, 0, 1), rs, 24, "w", seg=28)
        o += GE.prism(cam, (0, 0, 0), (0, 0, 1), GE.circle_outline(R, 64, 16), H, "w")
        o += lam_lines(cam, R, H, 9)
        # end face: magnet pockets (V per pole), magnets, flux barriers
        top = ""
        for k in range(np_):
            a = 2 * math.pi * k / np_ + math.radians(8)
            c, s_ = math.cos(a), math.sin(a)

            def w(u, v):
                return (u * c - v * s_, u * s_ + v * c, H + .05)
            for sg in (1, -1):
                p0, p1 = (42, sg * 5), (74, sg * 25)
                L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
                tu, tv = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
                nu, nv = -tv, tu

                def rc(cl, t, d0=0.0, d1=0.0):
                    e = 1
                    q = [(p0[0] + tu * (d0) + nu * e * (-t), p0[1] + tv * d0 + nv * e * (-t)),
                         (p0[0] + tu * (L + d1) + nu * e * (-t), p0[1] + tv * (L + d1) + nv * e * (-t)),
                         (p0[0] + tu * (L + d1) + nu * e * t, p0[1] + tv * (L + d1) + nv * e * t),
                         (p0[0] + tu * d0 + nu * e * t, p0[1] + tv * d0 + nv * e * t)]
                    return quad(cam, [w(*p) for p in q], cl)
                top += rc("bg", 3.6, -2.5, 3)
                top += rc("dk", 2.6, 1, -1)
            # flux-barrier / lightening hole between the poles
            b = a + math.pi / np_
            top += hole3(cam, (34 * math.cos(b), 34 * math.sin(b), H + .05), (0, 0, 1), 6.5, "bg", 16)
        o += top
        # shaft above the core: balancing-plate boss, bearing seat, spline end, hollow bore
        o += cy(cam, (0, 0, H), (0, 0, 1), 30, 4, "w", seg=40, dark=1, cap_mat="w2")
        o += cy(cam, (0, 0, H + 4), (0, 0, 1), rs, 22, "w", seg=28)
        o += cy(cam, (0, 0, H + 26), (0, 0, 1), rs - 3, 6, "w", seg=28, dark=1)
        o += compact(GE.prism(cam, (0, 0, H + 32), (0, 0, 1), GE.spline_outline(22, rs - 4, rs - 6), 20, "w"))
        o += hole3(cam, (0, 0, H + 52.05), (0, 0, 1), 9, "w3", 20) + hole3(cam, (0, 0, H + 52.1), (0, 0, 1), 7.4, "bg", 20)
        return o
    return fit(fn, az, el, (60, 8, 260, 178), sh_ry=8, sh_k=.56, sh_dy=-4)


@part("ev.rotor")
def _():
    return rotor()


# =====================================================================================
# ev.motorshaft — hollow rotor shaft: spline end with the oil bore, bearing seat, long rotor
# press-fit land with radial oil holes, stop collar, resolver rotor (lobed lamination stack),
# second bearing seat and threaded end. Feature end at x = 0, like the crankshaft.
# =====================================================================================
def motorshaft(az=22, el=20):
    def lobed(r, amp, lobes=4, seg=48):
        pts = []
        for k in range(seg):
            t = 2 * math.pi * k / seg
            rr = r + amp * math.cos(lobes * t)
            pts.append((rr * math.cos(t), rr * math.sin(t)))
        return banded(pts, 2)

    def fn(sc):
        def face(s_):
            return hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 9, "w3", 20) + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), 7, "bg", 20)
        RAW(sc, face, ((-.2, -16, -16), (0, 16, 16)), -2)
        X(sc, 0, 38, GE.spline_outline(20, 15, 12.8), "w")
        x = 38
        for L, r, kw in ((4, 12.5, {"dark": 2}), (22, 18, {}), (6, 22, {"dark": 1}), (112, 25, {}), (8, 31, {"dark": 1}),
                         (6, 21, {"dark": 1})):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=32, **kw)
            if L == 112:
                for xo, ph in ((x + 30, 130), (x + 82, 130)):
                    def oil(s_, xo=xo, ph=ph):
                        t = math.radians(ph)
                        nrm = (0, math.cos(t), math.sin(t))
                        return hole3(s_.cam, (xo, 25.1 * nrm[1], 25.1 * nrm[2]), nrm, 3)
                    RAW(sc, oil, ((xo - 3, -26, -26), (xo + 3, 26, 26)), -1)
            x += L
        # resolver rotor: lobed electrical-steel stack on its seat
        X(sc, x, 14, lobed(31, 3.2), "w", smooth=True, dark=1, cap_mat="w2")

        def lam(s_, x0=x):
            d = ""
            for j in range(1, 5):
                xx = x0 + 14 * j / 5
                d += P([s_.cam.xy((xx, 33 * math.cos(math.radians(a)), 33 * math.sin(math.radians(a)))) for a in range(-150, 35, 15)], False)
            return path(d, "gr")
        RAW(sc, lam, ((x, -35, -35), (x + 14, 35, 35)), -1)
        x += 14
        for L, r, kw in ((6, 18, {"dark": 1}), (22, 17, {}), (4, 12, {"dark": 2}), (16, 13, {"dark": 1})):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=28, **kw)
            x += L
    return fit(fn, az, el, (22, 40, 298, 166), sh_ry=7, sh_k=.46)


@part("ev.motorshaft")
def _():
    return motorshaft()


# =====================================================================================
# ev.cell — prismatic Li-ion cell, aluminium can, cut open at the lower front-left corner:
# wound jelly roll (layers turning round at the bottom), copper foil edge and tab, can wall
# section; top cap with negative (Cu) and positive (Al) terminals on gaskets, burst vent, fill plug.
# =====================================================================================
def cell(az=30, el=22):
    W, T, H, hc, xc = 150, 36, 100, 15, 50
    t2, wl = T / 2, 1.6

    def fn(sc):
        cam = sc.cam
        zc = H - hc
        o = zp(cam, 0, zc, [(xc, 0), (W, 0), (W, T), (0, T), (0, t2), (xc, t2)], "w")
        # cut face A (x = xc): can wall section + jelly-roll layers turning at the bottom
        o += fx(cam, xc, rect(0, 0, t2, zc), "cut")
        z0, z1 = wl + 2, zc - 1
        o += fx(cam, xc, rect(wl, z0, t2, z1), "dks2")
        d = ""
        for i in range(8):
            r = t2 - wl - 1.2 - i * 1.95
            if r < 1:
                break
            pts = [(xc, t2 - r, z1), (xc, t2 - r, z0 + (t2 - wl))] + [(xc, t2 - r * math.cos(math.radians(a)), z0 + (t2 - wl) - r * math.sin(math.radians(a)))
                                                                      for a in range(15, 91, 15)]
            d += P([cam.xy(p) for p in pts], False)
        o += path(d, "fin")
        # cut face B (y = T/2): electrode surface, bare copper foil edge, tab rising to the terminal
        o += fy(cam, t2, rect(0, 0, xc, zc), "cut")
        o += fy(cam, t2, rect(wl, z0, xc, z1), "dks3")
        o += fy(cam, t2, rect(wl + 1, z0, wl + 9, z1), "cus2")
        o += fy(cam, t2, [(wl + 1, zc - 12), (34, zc - 12), (34, zc), (wl + 1, zc)], "cus1")
        dl = ""
        for z in range(int(z0) + 6, int(z1) - 2, 7):
            dl += P([cam.xy((wl + 9.5, t2, z)), cam.xy((xc - .5, t2, z))], False)
        o += path(dl, "gr")
        # upper can + cap plate
        o += zb(cam, 0, 0, zc, W, T, hc, "w")
        o += path(P([cam.xy((0, 0, H - 4)), cam.xy((W, 0, H - 4)), cam.xy((W, T, H - 4))], False), "gr")
        # terminals on insulating gaskets
        for x0, mat in ((14, "cu"), (W - 40, "w")):
            o += zb(cam, x0 - 3, 7, H, 32, T - 14, 2.5, "dk", ch=3)
            o += zb(cam, x0, 9.5, H + 2.5, 26, T - 19, 6, mat, ch=2)
            o += hole3(cam, (x0 + 13, t2, H + 8.6), (0, 0, 1), 4.2, "w3" if mat == "w" else "gw", 14)
        # burst vent (obround with score line) and sealed fill port
        vx = W / 2 - 4
        ov = arc(vx + 9, t2, 7, -90, 90, 8) + arc(vx - 9, t2, 7, 90, 270, 8)
        o += path(P([cam.xy((a, b, H + .1)) for a, b in ov]), "w3")
        ov2 = arc(vx + 9, t2, 4.6, -90, 90, 8) + arc(vx - 9, t2, 4.6, 90, 270, 8)
        o += path(P([cam.xy((a, b, H + .15)) for a, b in ov2]), "w2")
        o += cy(cam, (vx + 30, t2, H), (0, 0, 1), 3.4, 1.6, "m", seg=16)
        return o
    return fit(fn, az, el, (52, 8, 268, 180), sh_ry=7, sh_k=.5, sh_dy=-4)


@part("ev.cell")
def _():
    return cell()


# =====================================================================================
# ev.pack — battery module: 12 prismatic cells stacked between end plates, steel side straps,
# series bus bars (Cu) laser-welded across alternating terminals, module terminals, cell vents,
# voltage-sensing FPC with the monitoring board, liquid cooling plate with ports underneath.
# =====================================================================================
def pack(az=30, el=30, N=12):
    tc, hy, H = 12, 38, 56
    L = N * tc

    def fn(sc):
        BOX(sc, -16, -hy - 6, -9, L + 32, 2 * hy + 12, 9, "alu", dark=1)                      # cooling plate
        for yy in (-22, 22):
            CYL(sc, (-30, yy, -4.5), (1, 0, 0), 3.4, 14, "m", seg=16)                       # coolant ports
        for x0 in (-12, L):
            BOX(sc, x0, -hy - 3, 0, 12, 2 * hy + 6, H + 4, "m", ch=2)                        # end plates
        for i in range(N):
            BOX(sc, i * tc, -hy, 0, tc, 2 * hy, H, "w", ch=.8)
        for z0 in (10, 36):
            BOX(sc, -12, -hy - 4, z0, L + 24, 1, 8, "m", -1)                                  # side straps

        def tops(s_):
            cam = s_.cam
            o = ""
            for i in range(N):
                cx = i * tc + tc / 2
                o += hole3(cam, (cx, 0, H + .05), (0, 0, 1), 3, "w3", 12)
            for x0 in (-12, L):                                                               # end plate bolts
                for yy in (-hy + 6, hy - 6):
                    o += hole3(cam, (x0 + 6, yy, H + 4.05), (0, 0, 1), 2.6, "bg", 10)
            return o
        RAW(sc, tops, ((0, -hy, H), (L, hy, H + .1)), -1)
        # bus bars: series connection, alternating sides
        for i in range(0, N, 2):
            BOX(sc, i * tc + 1.5, -hy + 8, H, 2 * tc - 3, 15, 3, "cu", -2, ch=1.5)
        for i in range(1, N - 1, 2):
            BOX(sc, i * tc + 1.5, hy - 23, H, 2 * tc - 3, 15, 3, "cu", -2, ch=1.5)
        BOX(sc, 1.5, hy - 23, H, tc - 3, 15, 3, "cu", -2)
        BOX(sc, -10, hy - 21, H + 3, 14, 11, 3, "cu", -3)                                  # module terminal (-)
        BOX(sc, L - tc + 1.5, hy - 23, H, tc - 3, 15, 3, "cu", -2)
        BOX(sc, L - 4, hy - 21, H + 3, 14, 11, 3, "cu", -3)                                # module terminal (+)
        BOX(sc, 2, 2, H, L - 4, 8, 1.2, "dk", -2)                                           # sensing FPC
        Z(sc, H + 4, 6, [(L + 1, -24), (L + 11, -24), (L + 11, 18), (L + 1, 18)], "dk", -3, cap_mat="pcb")  # monitoring board
    return fit(fn, az, el, (24, 14, 296, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("ev.pack")
def _():
    return pack()


# =====================================================================================
# ev.eaxlecase / ev.eaxleassy — e-Axle: die-cast motor housing (ribbed cylinder with water-jacket
# ports, bolted flange) joined to the lobed gear case (split flange, drive-shaft boss); the assembly
# adds the end cover, the inverter on top (HV and signal connectors) and the drive-shaft stub.
# =====================================================================================
def eaxle(assy=False, az=30, el=22):
    Rm, Lm, xg, Lg = 66, 170, 170, 64
    dy, dz = -26, -96

    def gc_outline(gro=0.0):
        pts = arc(0, 0, Rm + 14 + gro, 0, 360, 20) + arc(dy, dz, 62 + gro, 0, 360, 20)
        return banded(hull(pts), 3)

    def fn(sc):
        cam = sc.cam
        # flange at the open end (x = 0) with bolt ears
        fl = []
        for k in range(40):
            t = 2 * math.pi * k / 40
            r = Rm + 9 + (6 if k % 5 == 2 else 0)
            fl.append((r * math.cos(t), r * math.sin(t)))
        X(sc, 0, 9, banded(hull(fl), 3), "w", smooth=True)
        if not assy:
            def face(s_):
                o = hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), Rm - 2, "w3", 48) + hole3(s_.cam, (-.1, 0, 0), (-1, 0, 0), Rm - 7, "bg", 48)
                for k in range(8):
                    t = 2 * math.pi * (k + .5) / 8
                    o += hole3(s_.cam, (-.1, (Rm + 11) * math.cos(t), (Rm + 11) * math.sin(t)), (-1, 0, 0), 2.6, "bg", 10)
                return o
            RAW(sc, face, ((-.2, -Rm - 15, -Rm - 15), (0, Rm + 15, Rm + 15)), -2)
        else:
            CYL(sc, (-12, 0, 0), (1, 0, 0), Rm + 9, 12, "w", seg=48, dark=1)                 # end cover
            CYL(sc, (-24, 0, 0), (1, 0, 0), 30, 12, "w", seg=32)                            # resolver cover

            def bolts(s_):
                o = ""
                for k in range(8):
                    t = 2 * math.pi * (k + .5) / 8
                    o += hole3(s_.cam, (-12.1, (Rm + 3) * math.cos(t), (Rm + 3) * math.sin(t)), (-1, 0, 0), 3.2, "m", 10)
                return o
            RAW(sc, bolts, ((-12.2, -Rm - 9, -Rm - 9), (-12.1, Rm + 9, Rm + 9)), -2)
        # ribbed motor housing
        x = 9
        for L, r in ((50, Rm), (5, Rm + 4), (52, Rm), (5, Rm + 4), (Lm - 9 - 112, Rm)):
            CYL(sc, (x, 0, 0), (1, 0, 0), r, L, "w", seg=40, bands=10, dark=0 if r == Rm else 1)
            x += L
        if not assy:
            for xx in (34, 140):                                                             # water-jacket ports
                CYL(sc, (xx, -20, 62), (0, 0, 1), 6, 16, "w", seg=20)

                def bore(s_, xx=xx):
                    return hole3(s_.cam, (xx, -20, 78.05), (0, 0, 1), 3.6, "bg", 12)
                RAW(sc, bore, ((xx - 6, -26, 78), (xx + 6, -14, 78.1)), -1)
        # gear case: two halves with a split flange
        X(sc, xg, 30, gc_outline(), "w", smooth=True)
        X(sc, xg + 30, 6, gc_outline(3), "w", smooth=True, dark=1)
        X(sc, xg + 36, Lg - 36, gc_outline(), "w", smooth=True)
        CYL(sc, (xg - 18, dy, dz), (1, 0, 0), 30, 18, "w", seg=32)                          # drive-shaft boss
        if not assy:
            def seal(s_):
                c = (xg - 18.1, dy, dz)
                return hole3(s_.cam, c, (-1, 0, 0), 20, "w3", 24) + hole3(s_.cam, c, (-1, 0, 0), 15, "bg", 24)
            RAW(sc, seal, ((xg - 18.2, dy - 30, dz - 30), (xg - 18.1, dy + 30, dz + 30)), -2)
        else:
            X(sc, xg - 70, 52, [(u + dy, v + dz, f) for u, v, f in GE.spline_outline(14, 13, 11)], "w")                          # drive-shaft stub
            CYL(sc, (xg - 84, dy, dz), (1, 0, 0), 16, 14, "w", seg=24, dark=1)

            def gb(s_):
                return hole3(s_.cam, (xg - 84.1, dy, dz), (-1, 0, 0), 7, "bg", 14)
            RAW(sc, gb, ((xg - 84.2, dy - 16, dz - 16), (xg - 84.1, dy + 16, dz + 16)), -2)
            # inverter on top: case, lid, HV connectors, signal connector
            sc.add(zb(cam, 18, -52, 44, 136, 96, 40, "w", ch=6), ((18, -52, Rm + 4), (154, 44, 84)), 0)
            sc.add(zb(cam, 22, -48, 84, 128, 88, 5, "w", ch=5, dark=1, cap_mat="w2"), ((22, -48, 84), (150, 40, 89)), 0)
            for yy in (-30, -10):
                sc.add(cy(cam, (18, yy, 62), (-1, 0, 0), 8, 14, "dk", seg=20), ((4, yy - 8, Rm + 4.1), (18, yy + 8, 70)), -1)
            sc.add(zb(cam, 100, -60, 56, 30, 8, 16, "dk", ch=1), ((100, -60, Rm + 4.1), (130, -52, 72)), -1)
            for xx in (60, 120):                                                            # lid screws
                sc.add(lambda s_, xx=xx: hole3(s_.cam, (xx, -40, 89.05), (0, 0, 1), 2.4, "m", 10) + hole3(s_.cam, (xx, 32, 89.05), (0, 0, 1), 2.4, "m", 10),
                       ((xx - 3, -43, 89), (xx + 3, 35, 89.1)), -1)
    area = (34, 8, 286, 176) if assy else (40, 8, 280, 178)
    return fit(fn, az, el, area, sh_ry=7, sh_k=.5, sh_dy=-4)


@part("ev.eaxlecase")
def _():
    return eaxle(False)


@part("ev.eaxleassy")
def _():
    return eaxle(True)


# =====================================================================================
# ev.powermodule — 6-in-1 power module, lid off: copper base with pin-fin cooler underneath,
# resin frame, three ceramic (DBC) substrates with Cu pads, SiC/IGBT dies and bond wires,
# DC+/DC- lugs on the near side, three AC lugs behind, gold signal pins.
# =====================================================================================
def powermodule(az=28, el=34):
    Lx, Ly, Hf = 150, 96, 16

    def fn(sc):
        cam = sc.cam
        fins = []
        for i in range(15):                                         # pin-fin cooler (only the visible edge rows)
            for j in range(9):
                if i and j:
                    continue
                c = (5 + 10 * i, 5 + 10.75 * j, -9)
                fins.append((c, cy(cam, c, (0, 0, 1), 2.2, 9, "w", seg=8, bands=4, lines=False, dark=1)))
        o = depth_sorted(cam, fins)
        o += zb(cam, 0, 0, 0, Lx, Ly, 4, "w", ch=3)
        o += zb(cam, 0, Ly - 6, 4, Lx, 6, Hf, "dk") + zb(cam, Lx - 6, 6, 4, 6, Ly - 12, Hf, "dk")
        d = ""
        for x0 in (11, 56, 101):                                    # DBC substrates, Cu pads, dies, bond wires
            o += zb(cam, x0, 11, 4, 38, Ly - 22, 1.5, "pt")
            for y0 in (50, 14):
                o += zb(cam, x0 + 3, y0, 5.5, 32, 32, .9, "cu", lines=False)
                for dx, dy in ((4, 19), (19, 19), (4, 5), (19, 5)):
                    x, y = x0 + 3 + dx, y0 + dy
                    o += zb(cam, x, y, 6.4, 8, 8, .8, "dk" if dx == 4 else "m", lines=False)
                    for k in range(3):
                        yy = y + 1.8 + k * 2.2
                        p0, p1, p2 = cam.xy((x + 6, yy, 7.2)), cam.xy((x + 10, yy, 13)), cam.xy((x + 14.5, yy, 6.4))
                        d += "M%s %sQ%s %s %s %s" % (n(p0[0]), n(p0[1]), n(p1[0]), n(p1[1]), n(p2[0]), n(p2[1]))
        o += '<path class="wirebond" style="stroke-width:.9" d="%s"/>' % d
        for x0 in (12, 62, 112):                                    # AC lugs over the far wall
            o += zb(cam, x0, Ly - 6, 4 + Hf, 26, 22, 2.5, "cu", ch=2)
            o += hole3(cam, (x0 + 13, Ly + 8, 6.55 + Hf), (0, 0, 1), 4, "bg", 14)
        o += zb(cam, 0, 6, 4, 6, Ly - 12, Hf, "dk") + zb(cam, 0, 0, 4, Lx, 6, Hf, "dk")
        for x0 in (16, 50):                                         # DC+ / DC- lugs over the near wall
            o += zb(cam, x0, -16, 4 + Hf, 26, 22, 2.5, "cu", ch=2)
            o += hole3(cam, (x0 + 13, -8, 6.55 + Hf), (0, 0, 1), 4, "bg", 14)
        pins = []
        for k in range(8):                                          # gate / sense pins
            c = (92 + 6.5 * k + (6 if k > 3 else 0), 3, 4 + Hf)
            pins.append((c, cy(cam, c, (0, 0, 1), 1, 10, "gw", seg=8, bands=3, lines=False)))
        return o + depth_sorted(cam, pins)
    return fit(fn, az, el, (32, 10, 288, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("ev.powermodule")
def _():
    return powermodule()


# =====================================================================================
# ev.inverter — inverter with the cover off: die-cast case with integrated cooler, power module,
# film DC-link capacitor joined by a laminated bus bar, three AC bus bars through a current sensor
# to the output terminal block, control / gate-driver board on stand-offs, HV input and coolant ports.
# =====================================================================================
def inverter(az=30, el=36):
    Lx, Ly, Hw, tw, fl = 184, 124, 50, 5, 14

    def fn(sc):
        BOX(sc, 0, 0, 0, Lx, Ly, fl, "w", ch=4)                                           # floor / cooler
        for (x, y, sx, sy) in ((0, Ly - tw, Lx, tw), (Lx - tw, tw, tw, Ly - 2 * tw)):
            BOX(sc, x, y, fl, sx, sy, Hw - fl, "w")
        for (x, y, sx, sy) in ((0, 0, Lx, tw), (0, tw, tw, Ly - 2 * tw)):                 # near walls cut away
            BOX(sc, x, y, fl, sx, sy, 6, "w", cap_mat="cut")
        for yy in (26, 54):                                                                 # coolant ports
            CYL(sc, (0, yy, 7), (-1, 0, 0), 4.5, 14, "w", seg=16)
        CYL(sc, (0, 96, 11), (-1, 0, 0), 8, 16, "dk", seg=24)                             # HV DC input connector

        def ports(s_):
            o = hole3(s_.cam, (-16.1, 96, 11), (-1, 0, 0), 4.5, "bg", 16)
            for yy in (26, 54):
                o += hole3(s_.cam, (-14.1, yy, 7), (-1, 0, 0), 2.6, "bg", 10)
            return o
        RAW(sc, ports, ((-16.2, 20, 0), (-14, 108, 44)), -2)
        # power module on the cooler
        BOX(sc, 14, 12, fl, 72, 52, 12, "dk", ch=2)
        BOX(sc, 20, 18, fl + 12, 60, 40, .5, "cu")
        # film capacitor + laminated bus bar
        BOX(sc, 12, 80, fl, 104, 36, 30, "m", ch=3)
        BOX(sc, 22, 66, fl + 30, 80, 18, 2.5, "cu", -1)
        BOX(sc, 22, 64, fl + 12, 80, 2, 20.5, "cu")
        # AC bus bars -> current sensor -> terminal block
        for k in range(3):
            BOX(sc, 86, 20 + 14 * k, fl + 8, 82, 7, 2.5, "cu")
        BOX(sc, 124, 14, fl, 16, 48, 18, "dk", -1)
        BOX(sc, 166, 12, fl, 13, 52, 22, "dk")
        # control / gate-driver board on stand-offs (over the right half)
        for (x, y) in ((100, 74), (172, 74), (172, 112)):
            CYL(sc, (x, y, fl), (0, 0, 1), 2.4, 20, "m", seg=10, bands=4, lines=False)
        Z(sc, fl + 20, 2, [(96, 70), (176, 70), (176, 116), (96, 116)], "dk", -1, cap_mat="pcb")
        for (x, y, sx, sy, h) in ((106, 80, 16, 16, 2), (130, 78, 10, 10, 2), (148, 82, 20, 8, 5), (130, 98, 30, 10, 6)):
            BOX(sc, x, y, fl + 22, sx, sy, h, "dk", -2)
    return fit(fn, az, el, (30, 10, 290, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("ev.inverter")
def _():
    return inverter()


# =====================================================================================
# ev.batcase — battery-pack tray: hollow extruded side rails (chambers seen at the cut ends) with
# bolted mounting flanges, end rails, cross members dividing the module bays, floor panels joined
# by friction-stir welds, coolant ports.
# =====================================================================================
def batcase(az=26, el=34):
    L, Wd, Hr, tr = 300, 176, 28, 16

    def rail(flip=False):
        o = [(-14, 0), (0, 0), (tr, 0), (tr, Hr), (0, Hr), (0, 5), (-14, 5)]
        if flip:
            o = [(Wd - u, v) for u, v in o][::-1]
        return o

    def chambers(flip=False):
        hs = []
        for z0, z1 in ((3.5, 12.5), (15.5, 24.5)):
            q = [(3, z0), (tr - 3, z0), (tr - 3, z1), (3, z1)]
            if flip:
                q = [(Wd - u, v) for u, v in q][::-1]
            hs.append([(u, v, i) for i, (u, v) in enumerate(q)][::-1])
        return hs

    def fn(sc):
        BOX(sc, tr, tr, 0, L - 2 * tr, Wd - 2 * tr, 3, "w")
        X(sc, 0, L, rail(), "w", holes=chambers())
        X(sc, 0, L, rail(True), "w", holes=chambers(True))
        BOX(sc, 0, tr, 0, tr, Wd - 2 * tr, Hr, "w")
        BOX(sc, L - tr, tr, 0, tr, Wd - 2 * tr, Hr, "w")
        for xc in (L / 3, 2 * L / 3):
            BOX(sc, xc - 6, tr, 3, 12, Wd - 2 * tr, 19, "w", dark=1, cap_mat="w2")
        for yy in (60, 92):
            CYL(sc, (0, yy, 13), (-1, 0, 0), 4.6, 12, "w", seg=16)

        def floor(s_):
            cam = s_.cam
            o = ""
            for y in (60, 104, 148 - 2):
                for x0, x1 in ((tr, L / 3 - 6), (L / 3 + 6, 2 * L / 3 - 6), (2 * L / 3 + 6, L - tr)):
                    o += quad(cam, [(x0, y - 1.6, 3.05), (x1, y - 1.6, 3.05), (x1, y + 1.6, 3.05), (x0, y + 1.6, 3.05)], "w3")
            for yy in (60, 92):
                o += hole3(cam, (-12.1, yy, 13), (-1, 0, 0), 2.6, "bg", 10)
            for x in (20, 90, 160, 230, 290):
                o += hole3(cam, (x, -7, 5.05), (0, 0, 1), 3, "bg", 12) + hole3(cam, (x, Wd + 7, 5.05), (0, 0, 1), 3, "bg", 12)
            return o
        RAW(sc, floor, ((tr, tr, 3), (L - tr, Wd - tr, 3.1)), -1)
    return fit(fn, az, el, (20, 16, 300, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("ev.batcase")
def _():
    return batcase()


# =====================================================================================
# ev.planetary — power-split planetary set: helical internal ring gear, sun gear on its splined
# shaft, four pinions held by the carrier (spider plate with pinion pins on top).
# =====================================================================================
def planetary(az=-28, el=42):
    m, zs, zp_, zr, beta = 4.6, 13, 11, 35, 18
    rs, rp, rr = m * zs / 2, m * zp_ / 2, m * zr / 2
    a, Ro, H = rs + rp, rr + 12, 28
    ths = [k * 2 * math.pi / 3 + math.pi / 2 for k in range(3)]
    phs = math.pi / zs
    php = [mesh2(zs, phs, zp_, th) for th in ths]
    phr = ths[0] - (math.pi + zp_ * (ths[0] - php[0])) / zr

    def W(u, v, z):                    # outline plane (u, v) of axis +z -> world
        return (v, -u, z)

    def go(z, r, ph):
        return sgear(z, r, ph, lite=True)

    def fn(sc):
        cam = sc.cam
        tw = math.tan(math.radians(beta))
        ring_tw = -H * tw / rr
        rin = sring(zr, rr, phr)
        o = GE.prism(cam, (0, 0, 0), (0, 0, 1), GE.circle_outline(Ro, 48, 16), H, "w", holes=[rin], twist=ring_tw, smooth="outer", lines=False)
        gears = []
        for th, ph in zip(ths, php):
            c = W(a * math.cos(th), a * math.sin(th), 2)
            gears.append((c, GE.prism(cam, c, (0, 0, 1), go(zp_, rp, ph), H - 4, "w", twist=-(H - 4) * tw / rp)))
        gears.append(((0, 0, 1), GE.prism(cam, (0, 0, 1), (0, 0, 1), go(zs, rs, phs), H - 2, "w", twist=(H - 2) * tw / rs)))
        o += depth_sorted(cam, gears)
        # ring: front half again, over the pinions
        a0 = math.degrees(math.atan2(-cam.D[1], -cam.D[0]))

        def wang(p):
            x, y, _ = W(p[0], p[1], 0)
            return (math.degrees(math.atan2(y, x)) - a0 + 540) % 360 - 180
        outer = [(Ro * math.cos(math.radians(t)), Ro * math.sin(math.radians(t))) for t in range(0, 360, 6)]
        outer = sorted([p for p in outer if abs(wang(p)) <= 92], key=wang)
        inner = sorted([p for p in rin if abs(wang(p)) <= 92], key=lambda p: -wang(p))
        seg_ = [(u, v, i // 2) for i, (u, v) in enumerate(outer)] + [(u, v, 100 + i) for i, (u, v, _) in enumerate(inner)]
        o += GE.prism(cam, (0, 0, 0), (0, 0, 1), seg_, H, "w", twist=ring_tw, smooth="outer")
        # carrier spider: arms to the pinion pins, hub; pin heads; sun shaft with spline
        arms = []
        for th in ths:
            pu, pv = a * math.cos(th), a * math.sin(th)
            out = banded(hull(arc(pu, pv, 10, 0, 360, 12) + arc(0, 0, 14, 0, 360, 12)), 2)
            arms.append((W(pu * .6, pv * .6, H + 4), compact(GE.prism(cam, (0, 0, H + 1), (0, 0, 1), out, 7, "w", smooth=True, dark=1, cap_mat="w2"))))
        o += depth_sorted(cam, arms)
        o += cy(cam, (0, 0, H + 1), (0, 0, 1), 24, 8, "w", seg=32, dark=1, cap_mat="w2")
        for th in ths:
            o += hole3(cam, W(a * math.cos(th), a * math.sin(th), H + 8.05), (0, 0, 1), 5.5, "w3", 16)
        o += cy(cam, (0, 0, H + 9), (0, 0, 1), 17, 10, "w", seg=28)
        o += compact(GE.prism(cam, (0, 0, H + 19), (0, 0, 1), GE.spline_outline(14, 14, 12), 20, "w"))
        o += hole3(cam, (0, 0, H + 39.05), (0, 0, 1), 6, "bg", 16)
        return mrg(o)
    return fit(fn, az, el, (50, 8, 270, 178), sh_ry=8, sh_k=.56, sh_dy=-4)


@part("ev.planetary")
def _():
    return planetary()


# =====================================================================================
# ev.reducer — two-stage e-Axle reduction: input shaft pinion (spline to the motor) driving the
# counter-shaft gear, counter pinion driving the final (differential ring) gear. Helical teeth,
# axes horizontal; the final gear carries its bolt circle and the differential case hub.
# =====================================================================================
def reducer(az=30, el=20):
    m, beta = 3.4, 20
    zi, zc, zcp, zf = 17, 49, 15, 54
    ri, rc, rcp, rf_ = m * zi / 2, m * zc / 2, m * zcp / 2, m * zf / 2
    A = (0, -1, 0)
    b1 = math.radians(152)
    pi_ = ((ri + rc) * math.cos(b1), (ri + rc) * math.sin(b1))
    b2 = math.radians(-50)
    pf = ((rcp + rf_) * math.cos(b2), (rcp + rf_) * math.sin(b2))
    ph_c = 0.0
    ph_i = mesh2(zc, ph_c, zi, b1)
    ph_cp = 0.0
    ph_f = mesh2(zcp, ph_cp, zf, b2)
    tw = math.tan(math.radians(beta))

    def G(cx, cz, y0, h, z, r, ph, hand, holes=()):
        return GE.prism(cam_[0], (cx, y0 + h, cz), A, sgear(z, r, ph, lite=True), h, "w", twist=hand * h * tw / r, holes=list(holes))

    cam_ = [None]

    def fn(sc):
        cam = cam_[0] = sc.cam
        o = ""
        # rear layer (y 26..56): final gear + counter pinion
        o += cy(cam, (pf[0], 90, pf[1]), A, 30, 34, "w", seg=32)                                     # diff case (rear)
        o += G(pf[0], pf[1], 26, 30, zf, rf_, ph_f, 1)
        o += G(0, 0, 26, 30, zcp, rcp, ph_cp, -1)
        for k in range(10):
            t = 2 * math.pi * k / 10
            o += hole3(cam, (pf[0] + 52 * math.cos(t), 25.9, pf[1] + 52 * math.sin(t)), A, 4.2, "bg", 12)
        o += cy(cam, (pf[0], 26, pf[1]), A, 34, 16, "w", seg=32, dark=1, cap_mat="w2")                   # diff case hub
        o += hole3(cam, (pf[0], 9.9, pf[1]), A, 16, "w3", 24) + hole3(cam, (pf[0], 9.8, pf[1]), A, 12, "bg", 20)
        # front layer (y 0..24): counter gear + input pinion
        o += cy(cam, (pi_[0], 70, pi_[1]), A, 13, 70, "w", seg=24)                                     # input shaft (rear)
        o += G(0, 0, 0, 24, zc, rc, ph_c, 1)
        o += G(pi_[0], pi_[1], 0, 24, zi, ri, ph_i, -1)
        o += cy(cam, (0, 0, 0), A, 30, 8, "w", seg=32, dark=1, cap_mat="w2")                             # counter gear hub
        o += cy(cam, (0, -8, 0), A, 18, 14, "w", seg=28)                                               # bearing seat
        o += cy(cam, (pi_[0], 0, pi_[1]), A, 15, 12, "w", seg=24)                                       # input bearing seat
        o += compact(GE.prism(cam, (pi_[0], -12, pi_[1]), A, GE.spline_outline(14, 12, 10), 34, "w"))  # spline to the motor
        o += hole3(cam, (pi_[0], -46.1, pi_[1]), A, 5, "bg", 14)
        return mrg(o)
    return fit(fn, az, el, (34, 8, 286, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("ev.reducer")
def _():
    return reducer()


# =====================================================================================
# electrical.harness — wire harness on the floor: taped trunk with a corrugated-tube section,
# branches ending in connectors of different sizes (cavity grids on the mating faces, lock levers),
# fir-tree clips on the trunk.
# =====================================================================================
def harness(az=-18, el=42):
    def fn(sc):
        cam = sc.cam
        items = []

        def tube(pts, r, mat="dk", corr=None):
            for p0, p1 in zip(pts, pts[1:]):
                d = [p1[i] - p0[i] for i in range(3)]
                L = math.sqrt(sum(v * v for v in d))
                if corr and p0 == corr:
                    k = int(L // 5)
                    for j in range(k):
                        q0 = tuple(p0[i] + d[i] * j / k for i in range(3))
                        rr = r + (1.6 if j % 2 == 0 else .4)
                        items.append((tuple(p0[i] + d[i] * (j + .5) / k for i in range(3)),
                                      cy(cam, q0, d, rr, L / k, "dk", seg=16, bands=6, lines=False)))
                    continue
                items.append((tuple((p0[i] + p1[i]) / 2 for i in range(3)), cy(cam, p0, d, r, L, mat, seg=16, bands=6)))

        def conn(c, sx, sy, sz, face, grid, mat="pt"):
            x, y = c[0] - sx / 2, c[1] - sy / 2
            o = zb(cam, x, y, 0, sx, sy, sz, mat, ch=1.5)
            o += zb(cam, c[0] - sx * .18, c[1] - sy * .18, sz, sx * .36, sy * .36, 3, mat, ch=1)
            nx, ny = face
            nu, nv = grid
            for i in range(nu):
                for j in range(nv):
                    t = (i + .5) / nu - .5
                    zz = sz * ((j + .5) / nv)
                    if nx:
                        p = (c[0] + nx * (sx / 2 + .1), c[1] + t * sy * .8, zz)
                    else:
                        p = (c[0] + t * sx * .8, c[1] + ny * (sy / 2 + .1), zz)
                    o += hole3(cam, p, (nx, ny, 0), min(sx, sy, sz) * .09 + .8, "bg", 8)
            items.append(((c[0], c[1], sz / 2), o))
        r = 7
        tube([(-150, 10, r), (-60, 0, r), (10, 10, r), (130, -6, r)], r, corr=(-60, 0, r))
        tube([(-60, 0, 5), (-86, -40, 5), (-92, -64, 5)], 4.5)
        tube([(10, 10, 5), (34, 52, 5), (40, 80, 5)], 4.5)
        tube([(60, 4, 4), (74, -40, 4), (76, -62, 4)], 3.6)
        conn((-170, 10), 40, 34, 22, (-1, 0), (4, 2))
        conn((150, -6), 40, 30, 20, (1, 0), (3, 2), "m")
        conn((-92, -80), 30, 32, 18, (0, -1), (3, 2))
        conn((40, 94), 26, 28, 16, (0, 1), (2, 2), "m")
        conn((76, -74), 20, 24, 14, (0, -1), (2, 1))
        for x, y in ((-104, 5), (100, -2)):                                          # fir-tree clips
            items.append(((x, y - 12, 4), zb(cam, x - 6, y - 16, 0, 12, 10, 3, "pt", ch=2) + cy(cam, (x, y - 11, 0), (0, 0, -1), 2.2, 8, "pt", seg=10)))
        return depth_sorted(cam, items)
    return fit(fn, az, el, (20, 10, 300, 180), sh_ry=8, sh_k=.56, sh_dy=-6)


@part("electrical.harness")
def _():
    return harness()


# =====================================================================================
# electrical.ecu — ECU with the cover off: die-cast base with mounting ears, PCB with the
# microcontroller (QFP), power ICs, electrolytic capacitors, inductor and crystal, and the
# two-part connector header (cavity grids) through the near wall.
# =====================================================================================
def ecu(az=28, el=36):
    Lx, Ly, Hw = 170, 120, 16

    def fn(sc):
        cam = sc.cam
        o = ""
        for x, y in ((Lx - 4, 14), (Lx - 4, Ly - 30)):                             # far ears
            o += zb(cam, x, y, 0, 18, 16, 4, "w", ch=3)
            o += hole3(cam, (x + 11, y + 8, 4.05), (0, 0, 1), 3.4, "bg", 12)
        o += zb(cam, 0, 0, 0, Lx, Ly, Hw - 6, "w", ch=4)
        o += zb(cam, 0, Ly - 4, Hw - 6, Lx, 4, 6, "w") + zb(cam, Lx - 4, 4, Hw - 6, 4, Ly - 8, 6, "w")
        o += zb(cam, 8, 8, Hw - 6, Lx - 16, Ly - 16, 1.6, "dk", cap_mat="pcb", lines=False)
        z0 = Hw - 4.4
        o += zb(cam, 80, 54, z0, 34, 34, .5, "m", lines=False)                     # QFP lead frame
        o += zb(cam, 83, 57, z0 + .5, 28, 28, 2.4, "dk", ch=1)                    # microcontroller
        o += hole3(cam, (88, 62, z0 + 2.95), (0, 0, 1), 1.4, "m", 8)
        for (x, y, sx, sy, h) in ((126, 60, 16, 16, 2.2), (126, 86, 12, 9, 2), (40, 96, 14, 10, 2.4), (58, 96, 14, 10, 2.4), (128, 36, 10, 6, 2)):
            o += zb(cam, x, y, z0, sx, sy, h, "dk", ch=.6)
        o += zb(cam, 16, 52, z0, 18, 18, 10, "dk", ch=3)                          # inductor
        o += zb(cam, 50, 64, z0, 10, 5, 3.5, "m", ch=1.5)                          # crystal
        caps = []
        for x, y in ((24, 88), (40, 82), (148, 98)):
            c = cy(cam, (x, y, z0), (0, 0, 1), 6, 13, "m", seg=20)
            tp = cam.xy((x - 4, y, z0 + 13.05)), cam.xy((x + 4, y, z0 + 13.05)), cam.xy((x, y - 4, z0 + 13.05)), cam.xy((x, y + 4, z0 + 13.05))
            c += path("M%s %sL%s %sM%s %sL%s %s" % (n(tp[0][0]), n(tp[0][1]), n(tp[1][0]), n(tp[1][1]), n(tp[2][0]), n(tp[2][1]), n(tp[3][0]), n(tp[3][1])), "gr")
            caps.append(((x, y, z0), c))
        o += depth_sorted(cam, caps)
        # connector header through the near wall
        for x0, sx in ((22, 64), (94, 56)):
            o += zb(cam, x0, -14, 2, sx, 30, 30, "dk", ch=2)
            o += fy(cam, -14.1, [(x0 + 4, 6), (x0 + sx - 4, 6), (x0 + sx - 4, 28), (x0 + 4, 28)], "bg")
            for i in range(int(sx // 7)):
                for j in range(3):
                    o += hole3(cam, (x0 + 7 + i * 7, -14.2, 10 + j * 7), (0, -1, 0), 1.2, "gw", 6)
        for x, y in ((-14, 14), (-14, Ly - 30)):                                    # near ears
            o += zb(cam, x, y, 0, 18, 16, 4, "w", ch=3)
            o += hole3(cam, (x + 7, y + 8, 4.05), (0, 0, 1), 3.4, "bg", 12)
        return o
    return fit(fn, az, el, (28, 10, 292, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("electrical.ecu")
def _():
    return ecu()


# =====================================================================================
# electrical.headlamp — LED headlamp: black housing with mounting tabs, clear outer lens over a
# chrome bezel, two projector modules (lens + reflector ring), DRL light guide and turn-signal strip.
# =====================================================================================
def headlamp(az=-22, el=22):
    H, O = 62, (120, 112)
    plan = [(0, 0), (200, 34), (232, 54), (246, 82), (238, 120), (8, 114)]
    k = lambda t: 1 - .1 * t

    def F(i, s_, t):
        (x0, y0), (x1, y1) = plan[i], plan[i + 1]
        x, y = x0 + (x1 - x0) * s_, y0 + (y1 - y0) * s_
        return (O[0] + (x - O[0]) * k(t), O[1] + (y - O[1]) * k(t), H * t)

    def nrm(i, s_, t):
        a, b, c = F(i, s_, t), F(i, s_ + .01, t), F(i, s_, t + .01)
        return GE._norm(GE._cross(tuple(c[j] - a[j] for j in range(3)), tuple(b[j] - a[j] for j in range(3))))

    def off(p, nv, d):
        return tuple(p[j] + nv[j] * d for j in range(3))

    def fn(sc):
        cam = sc.cam
        o = ""
        for x, y in ((40, 96), (200, 100)):                                          # mounting tabs (behind)
            o += zb(cam, x, y, H - 12, 16, 14, 18, "dk", ch=2)
            o += hole3(cam, (x + 8, y + 3, H + 6.05), (0, 0, 1), 3, "bg", 10)
        o += compact(GE.prism(cam, (O[0], O[1], 0), (0, 0, 1), [(-(y - O[1]), x - O[0], i) for i, (x, y) in enumerate(plan)], H, "dk",
                              scale=k))
        n0 = nrm(0, .5, .5)
        o += quad(cam, [off(F(0, s_, t), n0, .2) for s_, t in ((.03, .1), (.98, .1), (.98, .9), (.03, .9))], "m")       # bezel
        o += quad(cam, [off(F(0, s_, t), n0, .3) for s_, t in ((.08, .12), (.42, .12), (.42, .22), (.08, .22))], "gw")  # turn signal
        for s_ in (.36, .68):                                                        # projector modules
            c = F(0, s_, .55)
            o += hole3(cam, off(c, n0, .4), n0, 22, "t", 32)
            o += hole3(cam, off(c, n0, .5), n0, 17.5, "dk", 32)
            o += hole3(cam, off(c, n0, .6), n0, 14.5, "lens", 32)
            o += hole3(cam, off(F(0, s_ - .02, .64), n0, .7), n0, 4.5, "gl2", 12)
        drl = [F(0, s_, .88) for s_ in (.04, .5, .97)] + [F(1, .6, .84), F(2, .5, .7), F(2, .9, .4)]
        o += path(P([cam.xy(off(p, n0, .8)) for p in drl], False), "led")
        for i in range(3):                                                           # outer lens over the three front faces
            o += quad(cam, [F(i, 0, 0), F(i, 1, 0), F(i, 1, 1), F(i, 0, 1)], "lens")
        o += path(P([cam.xy(F(0, s_, .96)) for s_ in (.1, .9)] + [cam.xy(F(1, .5, .95))], False), "fin")
        return o
    return fit(fn, az, el, (24, 14, 296, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


@part("electrical.headlamp")
def _():
    return headlamp()


# =====================================================================================
# electrical.adascam — forward ADAS camera: housing with cooling fins and bracket clips, lens barrel
# (front element, retaining ring), stray-light hood in front of the lens, rear coax connector.
# =====================================================================================
def adascam(az=-30, el=24):
    def fn(sc):
        cam = sc.cam
        o = ""
        o += cy(cam, (40, 50, 18), (1, 0, 0), 6, 14, "gw", seg=16)                                      # coax connector (side, rear)
        o += zb(cam, -48, 0, 0, 96, 64, 34, "dk", ch=4)                                                  # housing
        fins = []
        for k in range(7):                                                                               # fins on the top
            x = -36 + k * 12
            fins.append(((x, 32, 37), zb(cam, x - 1.6, 18, 34, 3.2, 40, 6, "m")))
        o += depth_sorted(cam, fins)
        for x in (-40, 32):                                                                              # bracket clips
            o += zb(cam, x, 4, 34, 8, 10, 7, "m", ch=1)
        # hood: floor plate and two side walls flaring forward
        o += zp(cam, 4, 2.5, [(-12, 0), (12, 0), (44, -62), (-44, -62)], "dk")
        o += zp(cam, 6.5, 9, [(-13, 0), (-11, 0), (-42, -62), (-45, -62)], "dk")
        o += zp(cam, 6.5, 9, [(11, 0), (13, 0), (45, -62), (42, -62)], "dk")
        # lens barrel
        o += cy(cam, (0, 0, 22), (0, -1, 0), 12, 10, "dk", seg=28)
        o += cy(cam, (0, -10, 22), (0, -1, 0), 10, 6, "m", seg=28)
        o += hole3(cam, (0, -16.1, 22), (0, -1, 0), 7.6, "dk", 24) + hole3(cam, (0, -16.2, 22), (0, -1, 0), 6.4, "lens", 24)
        o += hole3(cam, (-2, -16.3, 24), (0, -1, 0), 2.2, "gl2", 10)
        return o
    return fit(fn, az, el, (50, 12, 270, 178), sh_ry=8, sh_k=.5, sh_dy=-4)


@part("electrical.adascam")
def _():
    return adascam()


# =====================================================================================
# electrical.connector — sealed connector housing (cavity grid on the mating face, lock lever) with
# two stamped terminals about to be inserted: box contact with lance, crimped conductor and
# insulation barrels, wire.
# =====================================================================================
def connector(az=34, el=24):
    def fn(sc):
        cam = sc.cam
        o = zb(cam, 0, -30, 0, 52, 60, 30, "pt", ch=3)
        o += zb(cam, 12, -9, 30, 30, 18, 4, "pt", ch=2)                                                   # lock lever
        o += zb(cam, 4, -9, 33, 10, 18, 3, "pt", ch=1)
        for y in (-21, -7, 7, 21):
            for z in (8.5, 21.5):
                o += fx(cam, -.1, rect(y - 4.6, z - 4.6, y + 4.6, z + 4.6), "pts2")
                o += fx(cam, -.2, rect(y - 3.2, z - 3.2, y + 3.2, z + 3.2), "bg")
        terms = []
        for y, z in ((-21, 21.5), (7, 21.5)):
            t = ""
            t += cy(cam, (-112, y, z), (1, 0, 0), 3.4, 42, "dk", seg=16, bands=6)                     # wire
            t += cy(cam, (-70, y, z), (1, 0, 0), 4.2, 9, "w", seg=16, bands=6)                         # insulation barrel
            t += cy(cam, (-61, y, z - .4), (1, 0, 0), 3.2, 4, "w", seg=12, bands=4, dark=1)
            t += cy(cam, (-57, y, z - .6), (1, 0, 0), 3.4, 10, "w", seg=16, bands=6)                    # conductor barrel
            t += zb(cam, -47, y - 2.4, z - 3.4, 10, 4.8, 1.2, "w")                                       # transition
            t += zb(cam, -37, y - 3.4, z - 3.4, 26, 6.8, 6.8, "w")                                       # box contact
            t += zp(cam, z + 3.4, 1.6, [(-31, y - 1.6), (-21, y - 1.6), (-21, y + 1.6), (-31, y + 1.6)], "w")
            terms.append(((-50, y, z), t))
        o += depth_sorted(cam, terms)
        return o
    return fit(fn, az, el, (24, 20, 296, 176), sh_ry=7, sh_k=.5, sh_dy=-4)


@part("electrical.connector")
def _():
    return connector()
