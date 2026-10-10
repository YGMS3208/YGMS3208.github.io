"""v3 shaded-3D redraws of the last six weak part drawings (radiator, e-compressor, gas-turbine
compressor blades / turbine blade, form-wound generator coil, aluminium hood).
Loaded last (file-name order), so these registrations override the same keys in other il3_*.py."""
import math
import il_gear as GE
from il_base import *
from il_parts import part
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P
from il3_power import foil, blade_secs, surf_pts

D2R = math.pi / 180


def _cyl(cam, O, A, r, h, mat="w", seg=24, bands=10, **kw):
    """free-standing smooth cylinder (svg), for parts drawn by hand outside the Scene ordering."""
    return compact(GE.prism(cam, O, GE._norm(A), GE.circle_outline(r, seg, bands), h, mat, smooth=True, **kw))


def _bar(cam, a, b, w, h, up=(0, 0, 1), mat="w", ext=0.0, **kw):
    """rectangular bar a->b: section w (in-plane) x h (along the part of `up` normal to the bar)."""
    d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    L = math.sqrt(GE._dot(d, d))
    u = GE._norm(d)
    k = GE._dot(up, u)
    s2 = GE._norm((up[0] - u[0] * k, up[1] - u[1] * k, up[2] - u[2] * k))
    s1 = GE._cross(s2, u)
    E1, E2, _ = GE.frame(u)
    vs = [tuple(p * w / 2 * s1[i] + q * h / 2 * s2[i] for i in range(3)) for p, q in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    loop = [(GE._dot(v, E1), GE._dot(v, E2), j) for j, v in enumerate(vs)]
    O = (a[0] - u[0] * ext, a[1] - u[1] * ext, a[2] - u[2] * ext)
    return compact(GE.prism(cam, O, u, loop, L + 2 * ext, mat, **kw))


def _lv(i, th):
    """4-step shade from light intensity i with custom thresholds th (descending)."""
    return 1 if i > th[0] else 2 if i > th[1] else 3 if i > th[2] else 4


def loft2(cam, secs, mat="w", q=(.3, .65, .9), cap_mat=None, cap=True):
    """lofted skin like il_parts_power2.loft, but shaded per chordwise column, the 4 steps cut at quantiles of the
    columns' light intensity (q: fraction of columns at or above each cut) -> metallic bands on thin foils."""
    D = cam.D
    m = len(secs[0])
    cen = [sum(p[k] for s_ in secs for p in s_) / (len(secs) * m) for k in range(3)]
    faces = []
    s0 = secs[0]
    wnd = 1 if sum(s0[i][0] * s0[(i + 1) % m][1] - s0[(i + 1) % m][0] * s0[i][1] for i in range(m)) > 0 else -1
    for j in range(len(secs) - 1):
        A_, B_ = secs[j], secs[j + 1]
        for i in range(m):
            i2 = (i + 1) % m
            qd = (A_[i], A_[i2], B_[i2], B_[i])
            e = tuple(qd[1][k] - qd[0][k] + qd[2][k] - qd[3][k] for k in range(3))
            ax = tuple(qd[3][k] - qd[0][k] + qd[2][k] - qd[1][k] for k in range(3))
            nr = GE._norm(GE._cross(ax, e))
            ex, ey = (A_[i2][0] - A_[i][0]) * wnd, (A_[i2][1] - A_[i][1]) * wnd      # outward = (ey, -ex) for a CCW loop
            if nr[0] * ey - nr[1] * ex < 0:
                nr = (-nr[0], -nr[1], -nr[2])
            faces.append((nr, qd, GE._dot(nr, D) < 0))
    nsec = len(secs) - 1
    # one shade per chordwise column (mean light over its visible faces) -> clean spanwise bands
    col = []
    for i in range(m):
        v = [GE._dot(faces[j * m + i][0], GE.LIGHT) for j in range(nsec) if faces[j * m + i][2]]
        col.append(sum(v) / len(v) if v else None)
    its = sorted((c for c in col if c is not None), reverse=True)
    th = [its[min(len(its) - 1, int(f * len(its)))] - 1e-9 for f in q] if its else (.55, .2, -.2)
    out = []
    for i in range(m):
        if col[i] is None:
            continue
        cls = "%ss%d" % (mat, _lv(col[i], th))
        j = 0
        while j < nsec:
            if not faces[j * m + i][2]:
                j += 1
                continue
            k = j
            while k + 1 < nsec and faces[(k + 1) * m + i][2]:
                k += 1
            pts = [secs[t][i] for t in range(j, k + 2)] + [secs[t][(i + 1) % m] for t in range(k + 1, j - 1, -1)]
            sp = [cam.P(p) for p in pts]
            out.append((sum(p[2] for p in sp) / len(sp), '<path class="%s" d="%s"/>' % (cls, P([(p[0], p[1]) for p in sp]))))
            j = k + 1
    ed = ""
    for j in range(nsec):
        for i in range(m):
            a, b = faces[j * m + i][2], faces[j * m + (i + 1) % m][2]
            if a != b:
                p, r = secs[j][(i + 1) % m], secs[j + 1][(i + 1) % m]
                ed += P([cam.xy(p), cam.xy(r)], False)
    for i in range(m):
        if faces[(nsec - 1) * m + i][2]:
            ed += P([cam.xy(secs[-1][i]), cam.xy(secs[-1][(i + 1) % m])], False)
    out.sort(key=lambda t: -t[0])
    o = "".join(t for _, t in out) + path(ed, "el")
    if cap:
        sec = secs[-1]
        o += path(P([cam.xy(p) for p in sec]), cap_mat or mat)
    return o


# =====================================================================================
# thermal.radiator — cross-flow radiator: brazed aluminium core (flat tubes + corrugated fins),
# crimped header plates, PA66-GF side tanks, inlet hose spigot (upper left), outlet (lower right),
# filler neck and rubber-mounted locating pins.
# =====================================================================================
@part("thermal.radiator")
def _():
    W, T, H, nt = 236, 22, 128, 16

    def fn(sc):
        # core block (its front face is overdrawn with tubes and fins below)
        BOX(sc, 0, 0, 0, W, T, H, "w")

        def face(s_):
            cam = s_.cam
            o = path(P([cam.xy(q) for q in ((0, -.1, 0), (W, -.1, 0), (W, -.1, H), (0, -.1, H))]), "ws3")
            # fin crests: fine vertical lines over the whole face (tubes are drawn over them)
            a, b = cam.xy((0, -.1, 0)), cam.xy((0, -.1, H))
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = ""
            x = 1.6
            while x < W:
                p = cam.xy((x, -.1, 0))
                d += "M%s %sl%s %s" % (n(p[0]), n(p[1]), n(dx), n(dy))
                x += 2.5
            o += path(d, "gr")
            # flat tubes
            pt = H / nt
            for i in range(nt + 1):
                z = i * pt
                z0, z1 = max(0, z - 1.3), min(H, z + 1.3)
                o += path(P([cam.xy(q) for q in ((0, -.2, z0), (W, -.2, z0), (W, -.2, z1), (0, -.2, z1))]), "ws1")
            return o
        RAW(sc, face, ((0, -.3, 0), (W, -.1, H)), -1)
        # top / bottom side plates (channel)
        BOX(sc, 0, -1.5, H, W, T + 3, 4, "w", dark=1)
        BOX(sc, 0, -1.5, -4, W, T + 3, 4, "w", dark=1)
        # header plates and side tanks
        for xh, xt in ((-4, -26), (W, W + 4)):
            BOX(sc, xh, -3, -9, 4, T + 6, H + 18, "w", dark=1)
            tk = banded(hull(arc(xt + 7, 4, 7, 180, 270, 4) + arc(xt + 15, 4, 7, 270, 360, 4) +
                             arc(xt + 15, T - 4, 7, 0, 90, 4) + arc(xt + 7, T - 4, 7, 90, 180, 4)), 2)
            Z(sc, -14, H + 28, tk, "dk", smooth=True)
        # inlet spigot on the left tank (pointing -x), bead near the end
        zi = H - 26
        CYL(sc, (-26, T / 2, zi), (-1, 0, 0), 10, 10, "dk", seg=24)
        CYL(sc, (-36, T / 2, zi), (-1, 0, 0), 12, 3, "dk", seg=24)
        CYL(sc, (-39, T / 2, zi), (-1, 0, 0), 10, 14, "dk", seg=24)

        def bore(s_):
            c = (-53.1, T / 2, zi)
            return hole3(s_.cam, c, (-1, 0, 0), 7.4, "bg")
        RAW(sc, bore, ((-53.3, T / 2 - 10, zi - 10), (-53.1, T / 2 + 10, zi + 10)), -1)
        # filler neck + cap on the left tank
        CYL(sc, (-15, T / 2, H + 14), (0, 0, 1), 8, 8, "dk", seg=24)
        CYL(sc, (-15, T / 2, H + 22), (0, 0, 1), 12, 6, "w", seg=28, dark=1)
        # outlet spigot on the right tank, pointing forward (-y)
        CYL(sc, (W + 15, -3, 24), (0, -1, 0), 10, 10, "dk", seg=24)
        CYL(sc, (W + 15, -13, 24), (0, -1, 0), 12, 3, "dk", seg=24)
        CYL(sc, (W + 15, -16, 24), (0, -1, 0), 10, 12, "dk", seg=24)
        RAW(sc, lambda s_: hole3(s_.cam, (W + 15, -28.1, 24), (0, -1, 0), 7.4, "bg"), ((W + 5, -28.3, 14), (W + 25, -28.1, 34)), -1)
        # locating pins under the tanks
        for xc in (-15, W + 15):
            CYL(sc, (xc, T / 2, -14), (0, 0, -1), 5, 10, "dk", seg=16)
    return fit(fn, 24, 20, (22, 14, 298, 176), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# thermal.ecomp — electric scroll compressor: die-cast aluminium housing on a horizontal axis.
# Near end: scroll section (fixed-scroll head with bolted rear cover, discharge port block),
# bolted flange joint, ribbed motor housing with suction port, inverter box with HV connector on
# top, mounting bosses (through-bolt ears) on the housing.
# =====================================================================================
@part("thermal.ecomp")
def _():
    R = 50

    def fn(sc):
        CYL(sc, (0, 0, 0), (1, 0, 0), 44, 8, "w", seg=36, bands=10, r1=50)       # rear cover (discharge head)
        CYL(sc, (8, 0, 0), (1, 0, 0), 52, 36, "w", seg=40, bands=12)             # fixed-scroll housing
        CYL(sc, (44, 0, 0), (1, 0, 0), 57, 8, "w", seg=40, bands=10, dark=1)     # flange joint
        x = 52
        for L in (40, 4, 40, 4, 38):                                              # motor housing with ribs
            CYL(sc, (x, 0, 0), (1, 0, 0), R + (3 if L == 4 else 0), L, "w", seg=40, bands=10 if L == 4 else 12, dark=2 if L == 4 else 1)
            x += L
        CYL(sc, (x, 0, 0), (1, 0, 0), R, 10, "w", seg=36, bands=10, r1=42, dark=1)       # rear end bell

        def head(s_):
            cam = s_.cam
            o = hole3(cam, (-.1, 0, 0), (-1, 0, 0), 22, "w3") + hole3(cam, (-.2, 0, 0), (-1, 0, 0), 12, "w2")
            for k in range(6):
                a = 2 * math.pi * (k + .5) / 6
                c = (-.2, 35 * math.cos(a), 35 * math.sin(a))
                o += hole3(cam, c, (-1, 0, 0), 4.2, "w3") + hole3(cam, c, (-1, 0, 0), 2.2, "bg")
            for k in range(10):                                                     # flange bolts
                a = 2 * math.pi * (k + .5) / 10
                c = (43.8, 54.5 * math.cos(a), 54.5 * math.sin(a))
                o += hole3(cam, c, (-1, 0, 0), 2.2, "bg") if GE._dot((0, math.cos(a), math.sin(a)), cam.D) < .3 else ""
            return o
        RAW(sc, head, ((-.3, -44, -44), (-.1, 44, 44)), -2)

        def top(s_):
            cam = s_.cam
            o = ""
            # inverter: saddle + cast box + cover with ribs, HV connector at the front
            o += compact(GE.prism(cam, (60, 0, 0), (1, 0, 0), [(-36, 48, 0), (-30, 30, 1), (30, 30, 2), (36, 48, 3)], 100, "w", dark=1))
            box = [(62, -38), (158, -38), (158, 38), (62, 38)]
            loop = [(-y_, x_, i) for i, (x_, y_) in enumerate(box)]
            o += compact(GE.prism(cam, (0, 0, 46), (0, 0, 1), loop, 20, "w"))
            loop2 = [(-y_, x_, i) for i, (x_, y_) in enumerate([(66, -34), (154, -34), (154, 34), (66, 34)])]
            o += compact(GE.prism(cam, (0, 0, 66), (0, 0, 1), loop2, 5, "w", dark=1, cap_mat="w2"))
            d = ""
            for yy in (-22, -10, 2, 14, 26):                                      # cover stiffening ribs
                d += P([cam.xy((72, yy, 71.2)), cam.xy((148, yy, 71.2))], False)
            o += path(d, "gr")
            for xx, yy in ((70, -30), (150, -30), (70, 30), (150, 30)):
                o += hole3(cam, (xx, yy, 71.2), (0, 0, 1), 2.4, "w3")
            # HV connector + LV connector on the inverter's front face
            hv = [(-y_, x_, i) for i, (x_, y_) in enumerate([(84, -52), (112, -52), (112, -38), (84, -38)])]
            o += compact(GE.prism(cam, (0, 0, 48), (0, 0, 1), hv, 16, "dk", dark=0))
            o += hole3(cam, (92, -52.2, 56), (0, -1, 0), 3.2, "bg") + hole3(cam, (104, -52.2, 56), (0, -1, 0), 3.2, "bg")
            lv = [(-y_, x_, i) for i, (x_, y_) in enumerate([(124, -46), (140, -46), (140, -38), (124, -38)])]
            o += compact(GE.prism(cam, (0, 0, 50), (0, 0, 1), lv, 10, "dk"))
            # discharge port block on the scroll section (pad with tapped hole and refrigerant bore)
            pb = [(-y_, x_, i) for i, (x_, y_) in enumerate([(12, -14), (38, -14), (38, 14), (12, 14)])]
            o += compact(GE.prism(cam, (0, 0, 44), (0, 0, 1), pb, 16, "w", cap_mat="w2"))
            o += hole3(cam, (22, -2, 60.1), (0, 0, 1), 6.5, "w3") + hole3(cam, (22, -2, 60.2), (0, 0, 1), 4.6, "bg")
            o += hole3(cam, (33, 7, 60.2), (0, 0, 1), 2.2, "bg")
            return o
        RAW(sc, top, ((10, -52, 44), (160, 40, 72)), -1)

        def front(s_):
            cam = s_.cam
            parts = []
            # suction port block on the motor housing (front side)
            blk = compact(GE.prism(cam, (0, -40, 18), (0, -1, 0), [(z_, x_ - 163, i) for i, (x_, z_) in
                                                                    enumerate([(150, -13), (176, -13), (176, 13), (150, 13)])], 18, "w"))
            blk += hole3(cam, (160, -58.1, 18), (0, -1, 0), 7, "w3") + hole3(cam, (160, -58.2, 18), (0, -1, 0), 5, "bg")
            blk += hole3(cam, (171, -58.2, 9), (0, -1, 0), 2.2, "bg")
            parts.append((cam.P((163, -50, 18))[2], blk))
            # mounting ears (through-bolt bosses along y) at the bottom front, plus one at the top rear
            for xc, zc in ((26, -38), (120, -38), (176, -38)):
                ear = _cyl(cam, (xc, -26, zc - 6), (0, -1, 0), 9, 22, "w", seg=20, bands=8)
                ear += hole3(cam, (xc, -48.1, zc - 6), (0, -1, 0), 4.4, "bg")
                parts.append((cam.P((xc, -37, zc - 6))[2], ear))
            return "".join(p for _, p in sorted(parts, key=lambda p: -p[0]))
        RAW(sc, front, ((10, -60, -60), (180, -48, 30)), -3)
    return fit(fn, 26, 22, (30, 12, 290, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# gasgen.gtcomp — axial-compressor blading: three rotor blades of falling size (thin twisted
# airfoil, platform, axial dovetail root) and one stator vane (base with hook rails, inner shroud).
# =====================================================================================
def span_lines(cam, secs, idx, c="gr"):
    """spanwise iso-lines on a lofted airfoil, drawn only where the surface faces the viewer."""
    d = ""
    m = len(secs[0])
    s0 = secs[0]
    wnd = 1 if sum(s0[i][0] * s0[(i + 1) % m][1] - s0[(i + 1) % m][0] * s0[i][1] for i in range(m)) > 0 else -1
    for i in idx:
        run = []
        for j, s_ in enumerate(secs):
            p, a, b = s_[i], s_[(i - 1) % m], s_[(i + 1) % m]
            q = secs[min(j + 1, len(secs) - 1)][i] if j < len(secs) - 1 else p
            r = secs[j - 1][i] if j else p
            sp = (q[0] - r[0], q[1] - r[1], q[2] - r[2])
            nr = GE._cross((b[0] - a[0], b[1] - a[1], b[2] - a[2]), sp)
            ex, ey = (b[0] - a[0]) * wnd, (b[1] - a[1]) * wnd
            if nr[0] * ey - nr[1] * ex < 0:
                nr = (-nr[0], -nr[1], -nr[2])
            if GE._dot(GE._norm(nr), cam.D) < -0.05:
                run.append(cam.xy(p))
            else:
                if len(run) > 1:
                    d += P(run, False)
                run = []
        if len(run) > 1:
            d += P(run, False)
    return path(d, c) if d else ""


def cblade(sc, x, sz, st0, st1, stator=False):
    c, hs = 62 * sz, 150 * sz
    sec = foil(c, .12, .075, 12)
    secs = blade_secs(sec, 0, hs, st0, st1, .74, 9)
    secs = [[(p[0] + x, p[1], p[2]) for p in q] for q in secs]
    if not stator:
        # dovetail (flared, axial) + neck + platform
        X(sc, x - 26 * sz, 52 * sz, [(-17 * sz, -24 * sz), (17 * sz, -24 * sz), (11 * sz, -12 * sz), (-11 * sz, -12 * sz)], "w",
          dark=1, cap_mat="w3")
        X(sc, x - 26 * sz, 52 * sz, [(-8 * sz, -12 * sz), (8 * sz, -12 * sz), (8 * sz, -5 * sz), (-8 * sz, -5 * sz)], "w", dark=1, cap_mat="w3")
        X(sc, x - 30 * sz, 60 * sz, [(-19 * sz, -5 * sz), (19 * sz, -5 * sz), (19 * sz, 0), (-19 * sz, 0)], "w", cap_mat="w2")
    else:
        # vane base with hook rails (sits in the casing), small inner shroud on the tip
        X(sc, x - 30 * sz, 60 * sz, [(-20 * sz, -16 * sz), (20 * sz, -16 * sz), (20 * sz, -9 * sz), (-20 * sz, -9 * sz)], "w", dark=1, cap_mat="w3")
        X(sc, x - 30 * sz, 60 * sz, [(-14 * sz, -9 * sz), (14 * sz, -9 * sz), (14 * sz, -5 * sz), (-14 * sz, -5 * sz)], "w", dark=1, cap_mat="w3")
        X(sc, x - 34 * sz, 68 * sz, [(-22 * sz, -5 * sz), (22 * sz, -5 * sz), (22 * sz, 0), (-22 * sz, 0)], "w", cap_mat="w2")
        X(sc, x - 28 * sz, 56 * sz, [(-14 * sz, hs), (14 * sz, hs), (14 * sz, hs + 6 * sz), (-14 * sz, hs + 6 * sz)], "w", cap_mat="w2", bias=-1)
    m = len(sec)
    RAW(sc, lambda s_: loft2(s_.cam, secs, "w", (.2, .5, .8), cap=not stator, cap_mat="w2") + span_lines(s_.cam, secs, (3, m // 2 - 2, m - 4)),
        ((x - 36 * sz, -36 * sz, 0), (x + 36 * sz, 36 * sz, hs)))


@part("gasgen.gtcomp")
def _():
    def fn(sc):
        cblade(sc, 0, 1.0, -66, -8)
        cblade(sc, 96, .8, -66, -54, stator=True)
        cblade(sc, 172, .62, -64, -12)
        cblade(sc, 230, .46, -62, -16)
    return fit(fn, 28, 18, (24, 10, 296, 180), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# gasgen.gtblade — cooled turbine rotor blade: thick cambered airfoil with thermal-barrier coating
# (slightly warm tone), showerhead holes on the leading edge and film rows, trailing-edge slots,
# squealer tip, platform, shank and three-lobe fir-tree root (bare Ni superalloy).
# =====================================================================================
@part("gasgen.gtblade")
def _():
    sec = foil(74, .2, .26, 14)
    secs = blade_secs(sec, 0, 118, -26, -2, .9, 9)
    m = len(sec)

    def fn(sc):
        ft = [(10, -14), (10, -26), (18, -31), (18, -35), (9, -39), (15, -44), (15, -47), (8, -51), (12, -55), (12, -58), (5, -62)]
        yz = ft + [(-y, z) for y, z in ft[::-1]]
        X(sc, -30, 60, yz, "w", dark=1, cap_mat="w3")                                          # fir-tree root
        X(sc, -32, 64, [(-13, -14), (13, -14), (16, -6), (-16, -6)], "w", dark=1, cap_mat="w3")  # shank
        BOX(sc, -40, -27, -6, 80, 54, 6, "gw", ch=3)                                            # platform (coated top)
        RAW(sc, lambda s_: loft2(s_.cam, secs, "gw", (.35, .75, .95), cap_mat="gws3") + span_lines(s_.cam, secs, (m // 2 - 3, m - 3)),
            ((-42, -42, 0), (42, 42, 118)))

        def holes(s_):
            cam = s_.cam
            o = ""
            for idx in (0, 1, m - 1):          # showerhead rows at the leading edge
                o += surf_pts(cam, secs, idx, [.08 + .085 * k for k in range(11)], "bg", 1.2)
            for idx in (m - 4, m - 7, 4):      # film-cooling rows on the flanks
                o += surf_pts(cam, secs, idx, [.1 + .1 * k for k in range(9)], "bg", 1.0)
            for idx in (m // 2 - 1, m // 2 + 1):   # trailing-edge slots
                o += surf_pts(cam, secs, idx, [.08 + .09 * k for k in range(10)], "bg", .9)
            return o
        RAW(sc, holes, ((-43, -43, 0), (43, 43, 119)), -3)
    return fit(fn, 32, 22, (60, 8, 260, 182), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# generator.gencoil — one high-voltage form-wound (diamond) coil: two straight slot legs in
# different layers (semi-conductive armour tape, dark), involute end arms crossing over at the
# knuckle (mica tape, half-lap taping lines), and two leads with bare copper ends.
# =====================================================================================
@part("generator.gencoil")
def _():
    L, E, Pw, dz, w, h = 220, 74, 62, 36, 15, 30

    def fn(sc):
        cam = sc.cam
        pts_end = [(L, -Pw, 0), (L + E - 16, -13, dz * .32), (L + E, 0, dz * .5), (L + E - 16, 13, dz * .68), (L, Pw, dz)]
        segs = [((0, -Pw, 0), (L, -Pw, 0), "dk", 0), ((L, Pw, dz), (0, Pw, dz), "dk", 0)]
        segs += [(pts_end[i], pts_end[i + 1], "gw", 1) for i in range(4)]
        # near end: both sides run in to the nose, then turn out as the two leads
        for sg, z0, z1 in ((-1, 0, dz * .38), (1, dz, dz * .62)):
            p0, p1 = (0, sg * Pw, z0), (-E + 16, sg * 12, z1)
            p2 = (-E - 22, sg * 12, z1 + 4)
            segs += [(p0, p1, "gw", 1), (p1, p2, "gw", 1), (p2, (-E - 38, sg * 12, z1 + 4), "cu", 2)]
        parts = []
        for a, b, mat, kind in segs:
            ww, hh = (w, h) if kind < 2 else (w * .8, h * .55)
            s = _bar(cam, a, b, ww, hh, (0, 0, 1), mat, ext=(w / 2 if kind == 1 else 0))
            if kind == 1:                       # taping lines across the top face
                d = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
                Ln = math.sqrt(GE._dot(d, d))
                u = GE._norm(d)
                k = GE._dot((0, 0, 1), u)
                s2 = GE._norm((-u[0] * k, -u[1] * k, 1 - u[2] * k))
                s1 = GE._cross(s2, u)
                if GE._dot(s2, cam.D) < 0:
                    dd = ""
                    t = 4.0
                    while t < Ln - 4:
                        q0 = tuple(a[i] + u[i] * t + s2[i] * h / 2 - s1[i] * w / 2 for i in range(3))
                        q1 = tuple(a[i] + u[i] * (t + 4) + s2[i] * h / 2 + s1[i] * w / 2 for i in range(3))
                        dd += P([cam.xy(q0), cam.xy(q1)], False)
                        t += 6
                    s += path(dd, "gr")
            mid = tuple((a[i] + b[i]) / 2 for i in range(3))
            parts.append((cam.P(mid)[2], s))
        return "".join(p for _, p in sorted(parts, key=lambda p: -p[0]))
    return fit(fn, 24, 34, (22, 12, 298, 178), sh_ry=7, sh_k=.5, sh_dy=-3)


# =====================================================================================
# body.alhood — aluminium bonnet, shown exploded: the doubly curved outer skin (crowned, rising
# toward the windscreen, two soft character ridges, hemmed edge) lifted above the inner panel,
# a pressed frame with large lightening holes, hinge and latch reinforcements.
# =====================================================================================
def _hood_xy(u, v, k=1.0):
    hw = (126 + 20 * v) * k
    yf, yr = -92 + 16 * u * u, 92 - 4 * u * u
    return u * hw, (yf + (yr - yf) * v) * k


def _hood_z(u, v):
    r = 3.2 * math.exp(-((abs(u) - .46) / .09) ** 2) * (.3 + .7 * v)
    return 22 * (1 - u * u) * (.55 + .45 * v) + 16 * v - 14 * (1 - v) ** 3 + r


def _surf(cam, G, q=(.3, .62, .88), mat="w"):
    """height-field quad grid G[j][i] (3D points), shaded per lateral column (mean light over the
    column, 4 steps cut at quantiles q) -> long fore-aft highlight bands like a painted panel."""
    col = []
    for i in range(len(G[0]) - 1):
        acc = 0.0
        for j in range(len(G) - 1):
            a, b, c, d = G[j][i], G[j][i + 1], G[j + 1][i + 1], G[j + 1][i]
            nr = GE._norm(GE._cross((c[0] - a[0], c[1] - a[1], c[2] - a[2]), (d[0] - b[0], d[1] - b[1], d[2] - b[2])))
            acc += abs(GE._dot(nr, GE.LIGHT)) if nr[2] >= 0 else -GE._dot(nr, GE.LIGHT)
        col.append(acc / (len(G) - 1))
    its = sorted(col, reverse=True)
    th = [its[min(len(its) - 1, int(f * len(its)))] - 1e-9 for f in q]
    o = ""
    for i, c in enumerate(col):
        pts = [cam.xy(G[j][i]) for j in range(len(G))] + [cam.xy(G[j][i + 1]) for j in range(len(G) - 1, -1, -1)]
        o += path(P(pts), "%ss%d" % (mat, _lv(c, th)))
    return o


@part("body.alhood")
def _():
    nu, nv = 32, 12
    zl, yl, ah = 12, 0, 15 * D2R      # outer skin: hinged at its rear edge, front lifted by ah

    def fn(sc):
        cam = sc.cam
        o = ""
        # ---- inner panel: pressed frame with lightening holes
        per = [(-1 + 2 * i / 16, 0) for i in range(17)] + [(1, j / 6) for j in range(1, 7)] + \
              [(1 - 2 * i / 16, 1) for i in range(1, 17)] + [(-1, 1 - j / 6) for j in range(1, 6)]
        outl = hull([_hood_xy(u, v, .97) for u, v in per])
        loop = [(-y, x, f) for x, y, f in banded(outl, 3)]

        def rr(cx, cy, a, b, r=9):
            pts = arc(cx + a - r, cy + b - r, r, 0, 90, 3) + arc(cx - a + r, cy + b - r, r, 90, 180, 3) + \
                arc(cx - a + r, cy - b + r, r, 180, 270, 3) + arc(cx + a - r, cy - b + r, r, 270, 360, 3)
            return [(-y, x, i // 4) for i, (x, y) in enumerate(pts)]
        holes = [rr(cx, cy, 30, 24) for cx in (-74, 0, 74) for cy in (-36, 34)]
        holes += [rr(cx, 0, 12, 7, 6) for cx in (-112, 112)]
        o += compact(GE.prism(cam, (0, 0, -8), (0, 0, 1), loop, 8, "w", holes=holes, dark=1, cap_mat="w2", smooth="outer"))
        for x0, y0, sx, sy in ((-120, 68, 26, 16), (94, 68, 26, 16), (-14, -86, 28, 12)):   # hinge / latch reinforcements
            o += compact(GE.prism(cam, (0, 0, 0), (0, 0, 1), [(-y, x, i) for i, (x, y) in
                                                               enumerate([(x0, y0), (x0 + sx, y0), (x0 + sx, y0 + sy), (x0, y0 + sy)])], 4, "w", dark=1))
        # ---- outer skin, lifted: hemmed skirt first, then the curved surface
        yh, zh = 92, _hood_z(0, 1) + zl

        def lift(x, y, z):
            dy, dz_ = y - yh, z - zh
            return (x, yh + dy * math.cos(ah) + dz_ * math.sin(ah), zh + dz_ * math.cos(ah) - dy * math.sin(ah))

        def S(u, v):
            x, y = _hood_xy(u, v)
            return lift(x, y + yl, _hood_z(u, v) + zl)
        G = [[S(-1 + 2 * i / nu, j / nv) for i in range(nu + 1)] for j in range(nv + 1)]
        ring = G[0] + [G[j][-1] for j in range(1, nv + 1)] + G[-1][::-1][1:] + [G[j][0] for j in range(nv - 1, 0, -1)]
        cx = sum(p[0] for p in ring) / len(ring)
        cy = sum(p[1] for p in ring) / len(ring)
        sk = ""
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            a2, b2 = (a[0], a[1] + 6 * math.sin(ah), a[2] - 6 * math.cos(ah)), (b[0], b[1] + 6 * math.sin(ah), b[2] - 6 * math.cos(ah))
            nr = GE._norm((b[1] - a[1], -(b[0] - a[0]), 0))
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if nr[0] * (mx - cx) + nr[1] * (my - cy) < 0:
                nr = (-nr[0], -nr[1], 0)
            if GE._dot(nr, cam.D) < 0:
                sk += path(P([cam.xy(a), cam.xy(b), cam.xy(b2), cam.xy(a2)]), "ws%d" % min(4, GE.shade(nr) + 1))
        o += sk + _surf(cam, G)
        o += path(P([cam.xy(p) for p in ring]), "el")
        # character ridges
        d = ""
        for us in (-.46, .46):
            d += P([cam.xy(S(us, j / nv)) for j in range(nv + 1)], False)
        o += path(d, "gr")
        return o
    return fit(fn, 22, 34, (26, 10, 294, 180), sh_ry=7, sh_k=.5, sh_dy=-3)
