"""v3 shaded-3D 'parts & sections' (detail) and process drawings (ops) for engine.crank,
engine.conrod and engine.piston. Replaces the flat side views of il_d_engine.py; process count,
order, titles, notes and tolerances are kept from the old drawings."""
import math
import re
import il_gear as GE
from il_base import *
from il_detail import title, bal, tol, lead, fin, Pl
from il_dmap import dpart
from il3_lib import compact, fit, CYL, RING, X, Z, BOX, RAW, hull, banded, arc, circ3, hole3, P, arc3, arrow3, _bb
import il_d_engine as E

OPA = (14, 40, 466, 266)      # default drawing area of a process drawing (480x300, title band on top)


# =====================================================================================
# shared helpers
# =====================================================================================
def V(a, b, k=1.0):
    return tuple(a[i] + k * b[i] for i in range(3))


def SQ(sc, O, A, a, b, L, mat="m", bias=0.0, **kw):
    """rectangular bar 2a x 2b from O along A (bar of a tool holder, ram, arm...)."""
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    loop = [(-a, -b, 0), (a, -b, 1), (a, b, 2), (-a, b, 3)]
    svg = compact(GE.prism(sc.cam, O, A, loop, L, mat, **kw))
    cs = [tuple(O[i] + u * E1[i] + v * E2[i] + t * A[i] for i in range(3)) for u in (-a, a) for v in (-b, b) for t in (0, L)]
    sc.add(svg, (tuple(min(c[i] for c in cs) for i in range(3)), tuple(max(c[i] for c in cs) for i in range(3))), bias)


def PR(sc, O, A, loop2, L, mat="m", bias=0.0, **kw):
    """any (convex) outline [(u, v)] in GE.frame(A) extruded from O along A."""
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    loop = [(p[0], p[1], i) for i, p in enumerate(loop2)]
    svg = compact(GE.prism(sc.cam, O, A, loop, L, mat, **kw))
    cs = [tuple(O[i] + u * E1[i] + v * E2[i] + t * A[i] for i in range(3)) for u, v in loop2 for t in (0, L)]
    sc.add(svg, (tuple(min(c[i] for c in cs) for i in range(3)), tuple(max(c[i] for c in cs) for i in range(3))), bias)


def sil(cam, C, A, r, L):
    """the two silhouette generators of a cylinder (screen path d)."""
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    t = math.atan2(GE._dot(E1, cam.D), -GE._dot(E2, cam.D))
    d = ""
    for tt in (t, t + math.pi):
        nv = tuple(math.cos(tt) * E1[i] + math.sin(tt) * E2[i] for i in range(3))
        p0 = V(C, nv, r)
        d += P([cam.xy(p0), cam.xy(V(p0, A, L))], False)
    return d


def MFC(sc, C, A, r, L, c="mf", bias=-0.3):
    """mark a machined cylindrical surface (blue silhouette lines), ordered with the solid."""
    a = GE._norm(A)
    RAW(sc, lambda s_: path(sil(s_.cam, C, a, r, L), c), _bb(C, a, r, L), bias)


def MFO(sc, C, A, r, c="mf", bias=-0.4, seg=32):
    """mark a machined circular edge / face rim."""
    a = GE._norm(A)
    RAW(sc, lambda s_: path(P(circ3(s_.cam, C, a, r, seg)), c), _bb(C, a, r, 0.01), bias)


def drill3(sc, tip, A, r=4, L=46, sp=16, spL=40, mat="t", bias=0.0):
    """drill / center drill: cone tip at `tip`, body along A (away from the work), spindle nose."""
    a = GE._norm(A)
    CYL(sc, V(tip, a, r * 1.2), a, r, L, mat, bias, seg=12, bands=4)
    CYL(sc, tip, a, 0.6, r * 1.2, mat, bias, seg=12, r1=r, bands=4)
    CYL(sc, V(tip, a, r * 1.2 + L), a, sp, spL, "m", bias, seg=20, bands=6, dark=1)


def ttool(sc, tip, A, L=56, w=6, mat="t", bias=0.0):
    """turning / grooving tool: insert at tip, square shank along A."""
    a = GE._norm(A)
    SQ(sc, V(tip, a, 3), a, 3.2, 3.2, 9, mat, bias)
    SQ(sc, V(tip, a, 12), a, w, w, L, "m", bias, dark=1)


_DML = re.compile(r' d="([MLZ0-9 .\-]+)"')
_TOK = re.compile(r'([MLZ])|(-?\d+(?:\.\d+)?)')


def _num(v):
    """tenths -> shortest text ('-.8', '12', '3.4')."""
    s = ("%.1f" % (v / 10)).rstrip("0").rstrip(".")
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return "0" if s in ("", "-0", "-") else s


def _jn(a, b):
    sb = _num(b)
    return _num(a) + ("" if sb.startswith("-") else " ") + sb


def _mini_d(d):
    out, cur, start, cmd, nums = [], (0, 0), (0, 0), None, []
    toks = _TOK.findall(d)
    i = 0
    items = []
    for c, v in toks:
        if c:
            items.append(c)
        else:
            items.append(int(round(float(v) * 10)))
    k = 0
    last = None
    while k < len(items):
        t = items[k]
        if t == "Z":
            out.append("z")
            cur = start
            last = None
            k += 1
            continue
        if t in ("M", "L"):
            cmd = t
            k += 1
            continue
        x, y = items[k], items[k + 1]
        k += 2
        if cmd == "M":
            out.append(("M" if not out else "m") + _jn(x, y) if not out else "M" + _jn(x, y))
            start = cur = (x, y)
            last = "M"
            cmd = "L"
        else:
            seg = _jn(x - cur[0], y - cur[1])
            if last == "l":
                out.append((" " if not seg.startswith("-") else "") + seg)
            else:
                out.append("l" + seg)
            last = "l"
            cur = (x, y)
    return "".join(out)


def mini(svg):
    """shorten M/L path data: relative moves, tenths, implicit repeats (about -40% bytes)."""
    return _DML.sub(lambda m: ' d="%s"' % _mini_d(m.group(1)), svg)


def lab(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


# =====================================================================================
# engine.crank — model shared by the detail and the 16 process drawings
# inline-4: 5 journals, 4 pins (1-4 / 2-3 opposed), 8 webs with counterweights,
# flywheel flange at x=0 (near end), nose (pulley / sprocket seats) at the far end
# =====================================================================================
RJ, RP, EC, TW, LJ, LP, RL, RC = 26, 22.5, 45, 13, 24, 26, 28, 60
CLEN = 405


def cgeo(phi0=95):
    J, PN, W = [], [], []
    x = 21
    for ph in (phi0, phi0 + 180, phi0 + 180, phi0):
        J.append(x)
        x += LJ
        W.append((x, ph))
        x += TW
        PN.append((x, ph))
        x += LP
        W.append((x, ph))
        x += TW
    J.append(x)
    return J, PN, W


def pinc(x0, ph, dx=LP / 2):
    return (x0 + dx, EC * math.cos(math.radians(ph)), EC * math.sin(math.radians(ph)))


def crank3(sc, phi0=95, mat="w", pinm=None, jm=None, lod=1, oil=True, face=True, rot=None, O=(0, 0, 0), nose=True):
    """add a crankshaft to scene sc. rot='y' lays the shaft along +y (flange nearest the viewer)."""
    hot = mat == "h"
    pinm, jm = pinm or mat, jm or mat
    seg, bnd, aseg = (18, 6, 5) if lod else (10, 3, 2)

    def T(p):
        q = (-p[1], p[0], p[2]) if rot == "y" else p
        return V(O, q)
    AX = T((1, 0, 0))
    AX = tuple(AX[i] - O[i] for i in range(3))
    E1, E2, _ = GE.frame(AX)

    def cyl(x, y, z, r, L, m, **kw):
        if not lod:
            kw["lines"] = False
        CYL(sc, T((x, y, z)), AX, r, L, m, seg=kw.pop("seg", seg), bands=kw.pop("bands", bnd), **kw)

    def web(x, ph):
        py, pz = EC * math.cos(math.radians(ph)), EC * math.sin(math.radians(ph))
        pts = arc(py, pz, RL, ph - 90, ph + 90, aseg) + arc(0, 0, RC, ph + 180 - 56, ph + 180 + 56, aseg)
        loop = []
        for i, (u, v) in enumerate(hull(pts)):
            w = T((0, u, v))
            w = tuple(w[k] - O[k] for k in range(3))
            loop.append((GE._dot(w, E1), GE._dot(w, E2), i // 2))
        o = T((x, 0, 0))
        svg = compact(GE.prism(sc.cam, o, AX, loop, TW, mat, smooth=True, dark=0 if hot else 1, cap_mat=None if hot else "w3"))
        cs = [T((xx, u, v)) for xx in (x, x + TW) for u, v in pts]
        sc.add(svg, (tuple(min(c[i] for c in cs) for i in range(3)), tuple(max(c[i] for c in cs) for i in range(3))))

    if face and not hot:
        def fc(s_):
            nrm = tuple(-a for a in AX)
            c = T((-.1, 0, 0))
            o = hole3(s_.cam, c, nrm, 11, "w3") + hole3(s_.cam, c, nrm, 7, "bg")
            for k in range(6):
                a = 2 * math.pi * (k + .5) / 6
                o += hole3(s_.cam, T((-.1, 29 * math.cos(a), 29 * math.sin(a))), nrm, 3.4)
            return o
        cs = [T((-.2, -42, -42)), T((0, 42, 42))]
        RAW(sc, fc, (tuple(min(c[i] for c in cs) for i in range(3)), tuple(max(c[i] for c in cs) for i in range(3))), -2)
    cyl(0, 0, 0, 42, 11, mat, seg=seg + 6)
    if lod:
        cyl(11, 0, 0, 30, 10, mat)
    J, PN, W = cgeo(phi0)
    for x in J:
        cyl(x if lod or x != 21 else 11, 0, 0, RJ, LJ if lod or x != 21 else LJ + 10, jm)
    for x, ph in W:
        web(x, ph)
    for x, ph in PN:
        c = pinc(x, ph, 0)
        cyl(x, c[1], c[2], RP, LP, pinm)
        if oil and lod:
            a = math.radians(ph + 150)
            nrm = (0, math.cos(a), math.sin(a))
            p = (x + LP / 2, c[1] + RP * nrm[1], c[2] + RP * nrm[2])
            tn = T(nrm)
            tn = tuple(tn[i] - O[i] for i in range(3))
            cs = [T((x + 1, c[1] - RP, c[2] - RP)), T((x + LP - 1, c[1] + RP, c[2] + RP))]
            RAW(sc, lambda s_, p=p, tn=tn: hole3(s_.cam, T(p), tn, 2.6),
                (tuple(min(q[i] for q in cs) for i in range(3)), tuple(max(q[i] for q in cs) for i in range(3))), -1)
    if nose and not lod:
        cyl(J[-1] + LJ, 0, 0, 16, 40, mat, seg=10, bands=3)
    elif nose:
        x = J[-1] + LJ
        for L, r in ((14, 19), (18, 16), (24, 13)):
            cyl(x, 0, 0, r, L, mat, seg=seg - 4 if lod else 10, bands=bnd - 2)
            x += L
    return J, PN, W


def jc(J, i):
    return (J[i] + LJ / 2, 0, 0)


_TT = {}


def otitle(fn, i):
    """title band text of the old process drawing i (kept verbatim)."""
    import re
    if fn not in _TT:
        _TT[fn] = [re.search(r'class="ttl">([^<]*)<', x).group(1) for x in fn()]
    return _TT[fn][i]


def ctitle(i):
    return otitle(E.crank_ops, i)


# ------------------------------------------------------------------ detail
@dpart("engine.crank", "detail")
def crank_detail3():
    _, notes = E.crank_detail()
    ph0 = 95

    def fn(sc):
        crank3(sc, ph0)
    s, sc = fit(fn, 22, 20, (8, 70, 372, 232), ret_scene=True, sh_ry=8, sh_k=.46)
    cam = sc.cam
    J, PN, W = cgeo(ph0)
    xy = cam.xy
    s += bal(*xy((J[2] + 12, 0, RJ)), 150, 52, 1)
    s += bal(*xy(V(pinc(*PN[0]), (0, 0, RP))), 96, 52, 2)
    s += bal(*xy((W[3][0] + 6, -RC * .55, -RC * .8)), 150, 262, 3)
    s += bal(*xy((PN[3][0] + LP - 1, -8, EC * math.sin(math.radians(ph0)) + RP - 3)), 262, 52, 4)
    s += bal(*xy(V(pinc(*PN[1]), (0, -RP * .8, RP * .5))), 210, 262, 5)
    s += bal(*xy((0, -20, -30)), 40, 236, 6)
    s += bal(*xy((CLEN - 12, -10, 8)), 350, 236, 7)
    # inset: pin section with the hardened layer
    s += rect(380, 40, 94, 110, "m", 4) + text(427, 56, "ピン断面", "middle", "sm")
    s += circ(427, 100, 30, "w") + path("M397 100 A30 30 0 0 1 457 100 A30 30 0 0 1 397 100", "hotarc") + circ(427, 100, 4, "bg")
    s += text(427, 142, "表層を焼入れ", "middle", "sm")
    return mini(s), notes


# ------------------------------------------------------------------ process drawings
def c_op0():
    s = title(ctitle(0))
    R = 26

    def fn(sc):
        CYL(sc, (-60, 0, 0), (1, 0, 0), R, 150, "w", seg=24, bands=8)
        CYL(sc, (93, 0, 64), (1, 0, 0), 70, 3, "t", seg=48, bands=12)
        CYL(sc, (86, 0, 64), (1, 0, 0), 14, 7, "m", seg=16, bands=5)
        CYL(sc, (98, 0, 0), (1, 0, 0), R, 56, "w", seg=24, bands=8)
        xs = [200 + k * 64 for k in range(4)]
        for k, x in enumerate(xs):
            CYL(sc, (x, 0, 0), (1, 0, 0), R, 56, "w" if k == 3 else "h", seg=24, bands=8)

        def coil(s_, side):
            cam = s_.cam
            d = ""
            for k in range(24):
                x0 = 194 + k * 11
                pts = []
                for j in range(9):
                    a = (side * 180 + 180 * j / 8)
                    t = math.radians(a)
                    pts.append(cam.xy((x0 + 11 * (a % 360) / 360, 38 * math.cos(t), 38 * math.sin(t))))
                d += P(pts, False)
            return path(d, "coilcu")
        RAW(sc, lambda s_: coil(s_, 0), ((190, 0, -40), (460, 40, 40)), 80)
        RAW(sc, lambda s_: coil(s_, 1), ((190, -40, -40), (460, 0, 40)), -80)
        cam = sc.cam
        return arc3(cam, (90, 0, 64), (1, 0, 0), 84, 120, 60) + arrow3(cam, (200, -40, -64), (450, -40, -64))
    o, sc = fit(fn, 24, 20, (20, 50, 460, 250), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    x, y = cam.xy((0, -R, -R))
    s += text(x, y + 24, "棒鋼（S45C・非調質鋼）", "middle")
    a = cam.xy((325, -40, -64))
    s += lab(a[0], a[1] + 18, "コイル内を順送り")
    h = cam.xy((300, 0, 46))
    s += heat(h[0] - 30, h[1] - 6, 3, 30) + tol(h[0] - 50, h[1] - 34, "約1,200〜1,250℃")
    return s


def frame_loop(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def c_op1():
    s = title(ctitle(1))

    def fn(sc):
        crank3(sc, 0, "h", oil=False)
        hole = [(-y, x, i) for i, (x, y) in enumerate(frame_loop(-4, 409, -76, 76))]
        outl = [(-y, x, i) for i, (x, y) in enumerate(frame_loop(-18, 423, -100, 100))]
        sc.add(compact(GE.prism(sc.cam, (0, 0, -1.5), (0, 0, 1), outl, 3, "h", holes=[hole[::-1]], dark=1)),
               ((-18, -100, -1.5), (423, 100, 1.5)), 300)
        BOX(sc, -30, -110, -90, 465, 220, 30, "t", dark=1)
        BOX(sc, -30, -110, 150, 465, 220, 26, "t", dark=1)
        cam = sc.cam
        return arrow3(cam, (448, -110, 230), (448, -110, 180))
    o, sc = fit(fn, 22, 22, (20, 36, 440, 270), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    a = cam.xy((448, -110, 230))
    s += text(a[0] + 4, a[1] - 6, "加圧", "end", "al")
    s += heat(*cam.xy((200, 0, 70)), 4, 24)
    s += lead(*cam.xy((415, -88, 0)), 452, 216, "バリ", "middle")
    s += tol(40, 292, "4,000〜8,000t メカニカル鍛造プレス")
    return s


def c_op2():
    s = title(ctitle(2))

    def fn(sc):
        crank3(sc, 0, oil=False)
        hole = [(-y, x, i) for i, (x, y) in enumerate(frame_loop(-4, 409, -76, 76))]
        outl = [(-y, x, i) for i, (x, y) in enumerate(frame_loop(-18, 423, -100, 100))]
        sc.add(compact(GE.prism(sc.cam, (0, 0, -64), (0, 0, 1), outl, 3, "w", holes=[hole[::-1]], dark=2)),
               ((-18, -100, -64), (423, 100, -61)), 0)
        for xx in (60, 190, 330):
            SQ(sc, (xx, 0, 76), (0, 0, 1), 14, 30, 50, "m", dark=1)
        BOX(sc, -20, -60, 126, 440, 120, 20, "m", dark=1)

        def cf(s_):
            pts = [s_.cam.xy((x, y, 0)) for x, y in frame_loop(-4, 409, -76, 76)]
            return path(P(pts), "cutframe")
        RAW(sc, cf, ((-4, -76, -.1), (409, 76, .1)), 200)
        return arrow3(sc.cam, (440, -60, 200), (440, -60, 140))
    o, sc = fit(fn, 22, 28, (20, 36, 450, 268), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    a = cam.xy((440, -60, 170))
    s += lab(a[0] + 22, a[1], "抜き")
    s += lead(*cam.xy((-14, -96, -62)), 40, 286, "バリ（除去）", "start")
    return s


def c_op3():
    s = title(ctitle(3))

    def fn(sc):
        BOX(sc, -30, -90, -96, 470, 520, 18, "m", dark=1)
        for k, m in enumerate(("h", "h", "w")):
            crank3(sc, 95, m, lod=0, oil=False, face=False, O=(0, (2 - k) * 150, -10))
        for x in (90, 300):
            CYL(sc, (x, 300, 150), (0, 0, 1), 26, 22, "m", seg=20, bands=6)
            CYL(sc, (x, 300, 172), (0, 0, 1), 9, 16, "m", seg=12, bands=4, dark=1)
        cam = sc.cam
        o = ""
        for x in (90, 300):
            o += arrow3(cam, (x, 300, 140), (x, 300, 84))
        return o
    o, sc = fit(fn, 22, 34, (20, 34, 460, 266), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    s += arrow(*cam.xy((450, 380, -78)), *cam.xy((450, -40, -78)), None)
    s += text(240, 288, "冷却速度 → 硬さ・組織", "middle")
    b = cam.xy((300, 300, 172))
    s += tol(b[0] + 30, b[1] + 4, "送風量を制御")
    return s


def c_op4():
    s = title(ctitle(4))
    J, PN, W = cgeo(95)

    def fn(sc):
        crank3(sc, 95)
        CYL(sc, (-30, 0, 0), (1, 0, 0), 36, 30, "cu", seg=24, bands=8)
        CYL(sc, (CLEN, 0, 0), (1, 0, 0), 26, 30, "cu", seg=24, bands=8)
        SQ(sc, (-24, 0, 36), (0, 0, 1), 8, 8, 70, "cu")
        SQ(sc, (CLEN + 18, 0, 26), (0, 0, 1), 8, 8, 80, "cu")
        SQ(sc, (150, -170, -130), (0, 0, 1), 40, 14, 22, "m")
    o, sc = fit(fn, 22, 22, (20, 50, 460, 250), ret_scene=True, sh_k=.45)
    cam = sc.cam
    s += o
    a, b = cam.xy((-24, 0, 106)), cam.xy((CLEN + 18, 0, 106))
    s += path(P([a, (a[0], a[1] - 10), (b[0], a[1] - 10), b], False), "cable")
    s += text((a[0] + b[0]) / 2, a[1] - 16, "通電・磁化", "middle", "al")
    x, y = cam.xy((PN[1][0] + 2, -10, EC * math.sin(math.radians(275)) + RP))
    lamp = cam.xy((150, -170, -108))
    s += line(lamp[0] - 20, lamp[1], x - 8, y, "uv") + line(lamp[0] + 20, lamp[1], x + 8, y, "uv")
    s += path("M%s %s l4 6 l-3 6" % (n(x - 2), n(y - 4)), "indic") + circ(x, y + 2, 12, "mfring")
    s += text(lamp[0], lamp[1] + 36, "UVライトで観察", "middle")
    s += lead(x + 12, y + 4, 330, 272, "割れの指示模様")
    return s


def rollers(sc, J, idx=(0, 4)):
    for i in idx:
        for yy in (-24, 24):
            CYL(sc, (J[i] + 2, yy, -RJ - 12), (1, 0, 0), 12, LJ - 4, "m", seg=16, bands=5)
        BOX(sc, J[i] - 4, -40, -RJ - 62, LJ + 8, 80, 38, "m", dark=1)


def c_op5():
    s = title(ctitle(5))
    J, PN, W = cgeo(95)

    def fn(sc):
        crank3(sc, 95)
        rollers(sc, J)
        drill3(sc, (-1, 0, 0), (-1, 0, 0), 4, 30, 18, 40)
        drill3(sc, (CLEN + 1, 0, 0), (1, 0, 0), 4, 30, 18, 40)
        cam = sc.cam
        return arc3(cam, (200, 0, 0), (1, 0, 0), 80, 70, 150)
    o, sc = fit(fn, 22, 20, (20, 40, 460, 252), ret_scene=True, sh_k=.45)
    cam = sc.cam
    s += o
    a, b = cam.xy((-90, 0, -6)), cam.xy((CLEN + 90, 0, 6))
    s += path(P([a, b], False), "a")
    s += text(240, 52, "慣性主軸", "middle", "al")
    s += tol(120, 286, "回転させて質量中心軸を求め、両端にセンタ穴")
    return s


def c_op6():
    s = title(ctitle(6))
    J, PN, W = cgeo(95)
    nx = J[-1] + LJ

    def fn(sc):
        crank3(sc, 95)
        CYL(sc, (J[2] + 2, 0, 0), (1, 0, 0), 84, LJ - 4, "m", -3, seg=40, bands=10, holes=[GE.circle_outline(RJ, 24, 24)])
        ttool(sc, (5, 0, 42), (0, 0, 1), 50)
        ttool(sc, (-1, -30, 10), (0, -1, 0), 50)
        ttool(sc, (nx + 24, 0, 16), (0, 0, 1), 50)
        MFC(sc, (0, 0, 0), (1, 0, 0), 42, 11)
        MFO(sc, (-.1, 0, 0), (-1, 0, 0), 42)
        MFC(sc, (nx, 0, 0), (1, 0, 0), 19, 56)
        cam = sc.cam
        return arc3(cam, (J[2] + LJ / 2, 0, 0), (1, 0, 0), 100, 60, 140) + arrow3(cam, (-10, 0, 112), (40, 0, 112))
    o, sc = fit(fn, 22, 20, (20, 44, 460, 256), ret_scene=True, sh_k=.45)
    cam = sc.cam
    s += o
    s += lab(*cam.xy((15, 0, 124)), "送り")
    s += lead(*cam.xy((4, -10, -40)), 110, 284, "フランジ（外径・端面）", "middle")
    s += lead(*cam.xy((nx + 30, -8, -14)), 390, 284, "前端", "middle")
    s += text(*cam.xy((J[2] + 12, 0, -100)), "センタドライブ", "middle", "sm")
    return s


def c_op7():
    s = title(ctitle(7))
    J, PN, W = cgeo(95)
    x0, ph = PN[0]
    pc = pinc(x0, ph, 0)

    def fn(sc):
        crank3(sc, 95)
        CYL(sc, (x0 + 2, pc[1], pc[2]), (1, 0, 0), 112, LP - 4, "t", -2, seg=48, bands=12, holes=[GE.circle_outline(76, 40, 40)])

        def ins(s_):
            o = ""
            for k in range(14):
                a = 2 * math.pi * k / 14
                c, sn = math.cos(a), math.sin(a)
                q = [(x0 + 1.9, pc[1] + r * c - w * sn, pc[2] + r * sn + w * c) for r, w in ((76, -5), (76, 5), (84, 5), (84, -5))]
                o += path(P([s_.cam.xy(p) for p in q]), "ts3")
            return o
        RAW(sc, ins, ((x0 + 1.8, pc[1] - 112, pc[2] - 112), (x0 + 1.9, pc[1] + 112, pc[2] + 112)), -3)
        MFC(sc, (x0, pc[1], pc[2]), (1, 0, 0), RP, LP, bias=-1)
        cam = sc.cam
        return path(P(circ3(cam, (x0 + LP / 2, 0, 0), (1, 0, 0), EC, 32)), "orbit")
    o, sc = fit(fn, 22, 20, (100, 40, 464, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    s += arrow(36, 90, 36, 190, None, both=True) + lab(44, 130, "ピン位置", "start") + lab(44, 146, "に追従", "start")
    s += tol(40, 286, "内刃式ミーリング：ジャーナル・ピンを順に荒加工")
    return s


def c_op8():
    s = title(ctitle(8))
    J, PN, W = cgeo(95)

    def holes(J, PN):
        out = []
        for ji, pi_ in ((1, 0), (2, 1), (3, 2)):
            pcn = pinc(*PN[pi_])
            sgn = 1 if pcn[2] > 0 else -1
            jp = (J[ji] + LJ / 2, -RJ * .7, -sgn * RJ * .7)
            pp = (pcn[0], pcn[1] + RP * .5, pcn[2] + sgn * RP * .8)
            out.append((jp, pp))
        return out
    hs = holes(J, PN)

    def fn(sc):
        crank3(sc, 95)
        jp, pp = hs[1]
        d = GE._norm(tuple(jp[i] - pp[i] for i in range(3)))
        CYL(sc, V(jp, d, 1), d, 3, 120, "t", -6, seg=10, bands=3)
        CYL(sc, V(jp, d, 121), d, 14, 40, "m", -6, seg=18, bands=5, dark=1)
        for jp_, pp_ in hs:
            RAW(sc, lambda s_, a=jp_, b=pp_: path(P([s_.cam.xy(a), s_.cam.xy(b)], False), "mf"),
                ((min(jp_[0], pp_[0]), -30, -30), (max(jp_[0], pp_[0]), 30, 30)), -50)
    o, sc = fit(fn, 22, 20, (20, 40, 460, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    s += lead(*cam.xy(hs[2][0]), 330, 280, "油穴（交差部のバリに注意）")
    return s


def c_op9():
    s = title(ctitle(9))
    J, PN, W = cgeo(95)
    x0, ph = PN[0]
    pc = pinc(x0, ph, 0)

    def fn(sc):
        crank3(sc, 95, pinm="h", jm="h", oil=False)
        loop = arc(0, 0, RP + 12, 10, 170, 8)
        Lp = [(pc[1] + u, pc[2] + v) for u, v in loop]
        PR(sc, (x0 + 4, 0, 0), (1, 0, 0), hull(Lp), LP - 8, "cu", -4)
        SQ(sc, (x0 + LP / 2, pc[1], pc[2] + RP + 10), (0, 0, 1), 7, 9, 70, "cu", -4)
        CYL(sc, (x0 + 60, -60, pc[2] + 50), (0, 1, -1), 7, 30, "m", -4, seg=12, bands=4)
    o, sc = fit(fn, 22, 20, (20, 50, 440, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    nz = cam.xy((x0 + 60, -60, pc[2] + 50))
    s += drops(nz[0] - 4, nz[1] + 8, 3, 24, 22, 120)
    s += lead(*cam.xy((x0 + LP / 2, pc[1], pc[2] + RP + 60)), 300, 60, "半開放式コイル（ピン追従）")
    s += tol(40, 286, "硬化層深さ・硬化パターン・焼割れを管理（渦流で全数判定）")
    return s


def c_op10():
    s = title(ctitle(10))
    J, PN, W = cgeo(95)

    def fn(sc):
        crank3(sc, 95)
        for i in (0, 4):
            PR(sc, (J[i] + 2, 0, 0), (1, 0, 0), [(-22, -RJ - 34), (22, -RJ - 34), (0, -RJ)], LJ - 4, "m", dark=1)
        SQ(sc, (J[2] + LJ / 2, 0, RJ), (0, 0, 1), 10, 14, 90, "m", -3)
        SQ(sc, (J[3] + LJ / 2, -RJ - 4, -RJ - 50), (0, 0, 1), 8, 4, 30, "m", -3)
    o, sc = fit(fn, 22, 20, (20, 40, 440, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    a, b = cam.xy((J[2] + LJ / 2, -40, RJ + 90)), cam.xy((J[2] + LJ / 2, -40, RJ + 20))
    s += arrow(a[0] + 22, a[1], b[0] + 22, b[1], None) + lab(a[0] + 30, a[1] + 20, "押し", "start")
    g = cam.xy((J[3] + LJ / 2, -RJ - 4, -RJ - 20))
    t = cam.xy((J[3] + LJ / 2, -RJ - 4, -RJ))
    s += line(g[0], g[1], t[0], t[1], "o")
    s += text(g[0], g[1] + 36, "振れ測定", "middle")
    return s


def centers(sc):
    CYL(sc, (-2, 0, 0), (-1, 0, 0), 1, 22, "m", seg=16, r1=16, bands=5)
    CYL(sc, (-24, 0, 0), (-1, 0, 0), 22, 30, "m", seg=20, bands=6, dark=1)
    CYL(sc, (CLEN + 2, 0, 0), (1, 0, 0), 1, 22, "m", seg=16, r1=14, bands=5)
    CYL(sc, (CLEN + 24, 0, 0), (1, 0, 0), 20, 30, "m", seg=20, bands=6, dark=1)


def c_op11():
    s = title(ctitle(11))
    J, PN, W = cgeo(95)
    x0, ph = PN[0]
    pc = pinc(x0, ph, 0)
    RW = 110

    def fn(sc):
        crank3(sc, 95)
        centers(sc)
        CYL(sc, (x0 + 3, pc[1] + RP + RW, pc[2]), (1, 0, 0), RW, LP - 6, "t", seg=56, bands=14)
        CYL(sc, (x0 - 6, pc[1] + RP + RW, pc[2]), (1, 0, 0), 26, 9, "m", seg=20, bands=6)
        MFC(sc, (x0, pc[1], pc[2]), (1, 0, 0), RP, LP)
        for x in J:
            MFC(sc, (x, 0, 0), (1, 0, 0), RJ, LJ)
        cam = sc.cam
        return path(P(circ3(cam, (x0 + LP / 2, 0, 0), (1, 0, 0), EC, 32)), "orbit") + \
            arc3(cam, (x0, pc[1] + RP + RW, pc[2]), (1, 0, 0), RW + 12, 60, 120)
    o, sc = fit(fn, 22, 20, (20, 34, 460, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    T = cam.xy((x0 + LP, pc[1] + RP + RW, pc[2] + RW))
    s += lab(T[0] + 12, T[1] + 6, "CBN砥石", "start")
    s += arrow(T[0] + 24, T[1] + 30, T[0] + 104, T[1] + 30, None, both=True) + lab(T[0] + 64, T[1] + 48, "砥石台が追従")
    s += tol(40, 290, "真円度 1〜3μm・ストローク・位相。インプロセスゲージで定寸")
    return s


def c_op12():
    s = title(ctitle(12))
    J, PN, W = cgeo(95)
    x0, ph = PN[0]
    pc = pinc(x0, ph, 0)

    def fn(sc):
        crank3(sc, 95)
        SQ(sc, (x0 + LP / 2, pc[1], pc[2] + RP + 16), (0, 0, 1), 18, 10, 70, "m", -6)
        for xx, sg in ((x0 + 3, -1), (x0 + LP - 3, 1)):
            a = GE._norm((sg, 0, 1))
            CYL(sc, (xx - sg * 2, pc[1], pc[2] + RP + 2), a, 9, 5, "t", -7, seg=16, bands=5)
    o, sc = fit(fn, 22, 20, (20, 40, 400, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    a, b = cam.xy((x0 + LP / 2, pc[1] - 40, pc[2] + RP + 90)), cam.xy((x0 + LP / 2, pc[1] - 40, pc[2] + RP + 30))
    s += arrow(a[0], a[1], b[0], b[1], None)
    s += lead(*cam.xy((x0 + 2, pc[1] - 8, pc[2] + RP)), 120, 284, "フィレット（ローラ加圧）", "middle")
    s += tol(320, 60, "ローラ荷重を制御") + tol(320, 76, "焼入れの代わりに使う場合も")
    return s


def c_op13():
    s = title(ctitle(13))
    J, PN, W = cgeo(95)
    xj = J[2]

    def fn(sc):
        crank3(sc, 95)
        for sg in (1, -1):
            SQ(sc, (xj + LJ / 2, 0, sg * (RJ + 4)), (0, 0, sg), LJ / 2 - 3, 12, 50, "m", -5)
            SQ(sc, (xj + LJ / 2, 0, sg * (RJ + .5)), (0, 0, sg), LJ / 2 - 4, 13, 3.5, "gw", -6)
        MFC(sc, (xj, 0, 0), (1, 0, 0), RJ, LJ)
    o, sc = fit(fn, 22, 20, (20, 40, 460, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    a, b = cam.xy((xj - 50, 0, RJ + 64)), cam.xy((xj + LJ + 50, 0, RJ + 64))
    s += arrow(a[0], a[1], b[0], b[1], None, both=True) + lab((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 8, "揺動")
    s += lead(*cam.xy((xj + LJ / 2, -8, -RJ - 2)), 330, 250, "テープ（砥粒）", "start")
    s += tol(40, 286, "面粗さ Ra0.1〜0.2μm。油膜の安定と焼付き防止")
    return s


def c_op14():
    s = title(ctitle(14))
    J, PN, W = cgeo(95)
    ups = [(x, ph) for x, ph in W if math.sin(math.radians(ph)) < 0]
    a95 = math.radians(95)
    up = (0, math.cos(a95), math.sin(a95))

    def fn(sc):
        crank3(sc, 95)
        rollers(sc, J)
        xd = ups[0][0] + TW / 2
        drill3(sc, (xd, up[1] * (RC + 2), up[2] * (RC + 2)), up, 4, 34, 15, 36)

        def marks(s_):
            o = ""
            for x, _ in ups[1:]:
                for a in (80, 100):
                    t = math.radians(a)
                    nv = (0, math.cos(t), math.sin(t))
                    o += hole3(s_.cam, (x + TW / 2, nv[1] * (RC + .1), nv[2] * (RC + .1)), nv, 3.6, "mfa")
            return o
        RAW(sc, marks, ((ups[1][0], -RC, RC - 10), (ups[-1][0] + TW, RC, RC + .2)), -20)
        return arc3(sc.cam, (200, 0, 0), (1, 0, 0), 84, 200, 280)
    o, sc = fit(fn, 22, 22, (20, 40, 440, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    x, _ = ups[2]
    s += lead(*cam.xy((x + TW / 2, -RC * .1, RC)), 330, 60, "修正穴") + tol(300, 286, "残留アンバランスを規格内に")
    return s


def c_op15():
    s = title(ctitle(15))
    J, PN, W = cgeo(95)

    def fn(sc):
        crank3(sc, 95)
        centers(sc)
        for x in J:
            CYL(sc, (x + LJ / 2, 0, RJ + 1), (0, 0, 1), 3, 50, "m", -5, seg=10, bands=3)
            CYL(sc, (x + LJ / 2, 0, RJ + .2), (0, 0, 1), 4.5, 1.6, "t", -6, seg=12, bands=3)
        BOX(sc, J[0] - 10, -14, RJ + 51, J[4] + LJ - J[0] + 20, 28, 16, "m", -5, dark=1)
    o, sc = fit(fn, 22, 20, (20, 50, 460, 262), ret_scene=True, sh_k=.4)
    s += o
    s += tol(40, 44, "シャフト形状測定機（全数）") + tol(300, 44, "磁粉探傷で最終確認")
    return s


C_OPS = [c_op0, c_op1, c_op2, c_op3, c_op4, c_op5, c_op6, c_op7, c_op8, c_op9, c_op10, c_op11, c_op12, c_op13, c_op14, c_op15]


@dpart("engine.crank", "ops")
def crank_ops3():
    return [mini(fin(f())) for f in C_OPS]


# =====================================================================================
# engine.conrod — forged rod lying flat (thickness along z): big end at the origin with the
# fracture-split cap toward -x, I-beam shank with recessed web, small end at x=LS
# =====================================================================================
RT, LS, RBO, RSO = 22, 150, 27, 11
_BIG = [(20, 30), (14, 47), (-26, 47), (-26, 34)] + arc(0, 0, 40, 122, 238, 10) + [(-26, -34), (-26, -47), (14, -47), (20, -30)]
_SML = arc(LS, 0, 18, 215, 505, 16)


def _zl(pts):
    return [(-y, x, i) for i, (x, y) in enumerate(pts)]


def _zadd(sc, pts, z0, L, mat, holes=(), bias=0.0, dx=0.0, **kw):
    pts = [(x + dx, y) for x, y in pts]
    hs = [[(-y, x + dx, i * 5 // len(h)) for i, (x, y) in enumerate(h)] for h in holes]
    svg = compact(GE.prism(sc.cam, (0, 0, z0), (0, 0, 1), _zl(pts), L, mat, holes=hs, **kw))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    sc.add(svg, ((min(xs), min(ys), z0), (max(xs), max(ys), z0 + L)), bias)


def rod3(sc, mat="w", split=False, gap=0.0, bolts=True, z0=0.0, marks=True):
    """add the rod; split=True draws body and cap as two solids (cap moved -x by gap)."""
    hsm = arc(LS, 0, RSO, 360, 0, 20)[:-1]
    if not split:
        _zadd(sc, _BIG + _SML, z0, RT, mat, [arc(0, 0, RBO, 360, 0, 32)[:-1], hsm], smooth="outer")
    else:
        body = [(0, -47), (14, -47), (20, -30)] + _SML + [(20, 30), (14, 47), (0, 47)] + arc(0, 0, RBO, 90, -90, 14)
        cap = [(0, 47), (-26, 47), (-26, 34)] + arc(0, 0, 40, 122, 238, 10) + [(-26, -34), (-26, -47), (0, -47)] + arc(0, 0, RBO, 270, 90, 14)
        _zadd(sc, body, z0, RT, mat, [hsm], smooth="outer")
        _zadd(sc, cap, z0, RT, mat, dx=-gap, smooth="outer")
    zt = z0 + RT + .05

    def face(s_):
        cam = s_.cam
        o = path(P([cam.xy((x, y, zt)) for x, y in [(44, 15), (128, 8.5), (128, -8.5), (44, -15)]]), "ws2")
        o += path(P([cam.xy((44, 15, zt)), cam.xy((128, 8.5, zt))], False) + P([cam.xy((44, -15, zt)), cam.xy((128, -8.5, zt))], False), "el")
        if marks and not gap:
            jag = [(0, 47), (1.2, 44), (-.8, 41), (.9, 37), (-.6, 33), (.5, 29.5), (0, 27)]
            o += path(P([cam.xy((x, y, zt)) for x, y in jag], False) + P([cam.xy((x, -y, zt)) for x, y in jag], False), "el")
            o += path(P([cam.xy((x, -47 - .05, z)) for x, z in ((0, zt), (1, z0 + 15), (-.8, z0 + 8), (0, z0))], False), "el")
        cx = LS + 18
        o += hole3(cam, (cx + .05, 0, z0 + RT / 2), (1, 0, 0), 2.6)
        return o
    RAW(sc, face, ((-26, -47, zt), (LS + 18, 47, zt + .1)), -1)
    if bolts:
        for v in (40.5, -40.5):
            CYL(sc, (-26 - gap, v, z0 + RT / 2), (-1, 0, 0), 6.5, 7, "m", -.5, seg=6, bands=6)
            RAW(sc, lambda s_, v=v: hole3(s_.cam, (-33.1 - gap, v, z0 + RT / 2), (-1, 0, 0), 3, "ms3", 6),
                ((-33.2 - gap, v - 3, z0 + 8), (-33.1 - gap, v + 3, z0 + 14)), -1)


def rtitle(i):
    return otitle(E.rod_ops, i)


@dpart("engine.conrod", "detail")
def rod_detail3():
    _, notes = E.rod_detail()

    def fn(sc):
        rod3(sc)
    o, sc = fit(fn, 24, 36, (20, 50, 330, 250), ret_scene=True, sh_k=.42)
    cam = sc.cam
    s = o
    xy = cam.xy
    s += bal(*xy((-20, -40, RT)), 40, 70, 1)
    s += bal(*xy((LS + 8, 10, RT)), 300, 70, 2)
    s += bal(*xy((90, 0, RT)), 200, 60, 3)
    s += bal(*xy((0, -44, RT * .6)), 120, 262, 4)
    s += bal(*xy((-33, -40.5, RT / 2)), 40, 240, 5)
    s += rect(340, 110, 130, 110, "m", 4) + text(405, 126, "ビーム断面", "middle", "sm")
    s += path(P([(380, 140), (430, 140), (430, 150), (412, 150), (412, 182), (430, 182), (430, 192), (380, 192), (380, 182), (398, 182), (398, 150), (380, 150)]), "cut")
    return mini(s), notes


def r_op0():
    s = title(rtitle(0))

    def fn(sc):
        rod3(sc, "h", bolts=False, marks=False)
        hole = _zl(frame_loop(-46, 172, -52, 52))[::-1]
        sc.add(compact(GE.prism(sc.cam, (0, 0, 9.5), (0, 0, 1), _zl(frame_loop(-66, 192, -74, 74)), 3, "h", holes=[hole], dark=1)),
               ((-66, -74, 9.5), (192, 74, 12.5)), 300)
        BOX(sc, -80, -90, -40, 286, 180, 30, "t", dark=1)
        BOX(sc, -80, -90, 90, 286, 180, 26, "t", dark=1)
        return arrow3(sc.cam, (220, -90, 170), (220, -90, 120))
    o, sc = fit(fn, 24, 30, (40, 36, 440, 270), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    a = cam.xy((220, -90, 170))
    s += text(a[0] + 4, a[1] - 6, "加圧", "end", "al")
    s += heat(*cam.xy((60, 0, 40)), 3, 20)
    s += lead(*cam.xy((180, -70, 11)), 420, 210, "バリ", "middle")
    s += tol(40, 290, "1,600〜2,500t")
    return s


def r_op1():
    s = title(rtitle(1))

    def fn(sc):
        rod3(sc, bolts=False, marks=False)
        hole = _zl(frame_loop(-46, 172, -52, 52))[::-1]
        sc.add(compact(GE.prism(sc.cam, (0, 0, -30), (0, 0, 1), _zl(frame_loop(-66, 192, -74, 74)), 3, "w", holes=[hole], dark=2)),
               ((-66, -74, -30), (192, 74, -27)), 0)
        CYL(sc, (250, 40, 120), GE._norm((-1, 0, -1)), 16, 24, "m", seg=16, bands=5)

        def cf(s_):
            return path(P([s_.cam.xy((x, y, RT / 2)) for x, y in _BIG + _SML]), "cutframe")
        RAW(sc, cf, ((-40, -47, RT / 2), (168, 47, RT / 2 + .1)), -20)
    o, sc = fit(fn, 24, 32, (40, 40, 440, 262), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    nz = cam.xy((230, 40, 100))
    for i in range(12):
        s += circ(nz[0] - 14 - (i % 4) * 12 - (i // 4) * 8, nz[1] + 14 + (i // 4) * 12 + (i % 4) * 4, 2.2, "shot")
    s += text(nz[0] + 20, nz[1] - 20, "ショット", "middle")
    s += lead(*cam.xy((-60, -70, -28)), 60, 270, "バリ", "start")
    return s


def r_op2():
    s = title(rtitle(2))
    RW = 140

    def fn(sc):
        rod3(sc, bolts=False)
        CYL(sc, (60, 230, -1), (0, 0, -1), RW, 40, "gw", seg=56, bands=14)
        CYL(sc, (60, 230, RT + 1), (0, 0, 1), RW, 40, "gw", seg=56, bands=14)

        def mf_(s_):
            return path(P([s_.cam.xy((x, y, RT)) for x, y in _BIG + _SML]), "mf")
        RAW(sc, mf_, ((-40, -47, RT), (168, 47, RT + .1)), -5)
        return arrow3(sc.cam, (60, -110, RT / 2), (60, -60, RT / 2))
    o, sc = fit(fn, 24, 26, (40, 40, 440, 270), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    a = cam.xy((60, -110, RT / 2))
    s += lab(a[0], a[1] + 18, "通過・送り")
    for z in (RT + 41, -41):
        p = cam.xy((60 + RW, 230, z))
        s += text(p[0] + 8, p[1] + 4, "砥石", "start")
    s += tol(40, 290, "厚さ・平行度")
    return s


def r_op3():
    s = title(rtitle(3))

    def fn(sc):
        rod3(sc, split=False, bolts=False)
        BOX(sc, -60, -70, -24, 250, 140, 24, "m", dark=1)
        CYL(sc, (0, 0, RT + 30), (0, 0, 1), 20, 40, "t", -2, seg=20, bands=6)
        CYL(sc, (0, 0, RT + 2), (0, 0, 1), 6, 28, "t", -2, seg=12, bands=4)
        CYL(sc, (LS, 0, RT + 26), (0, 0, 1), 12, 40, "t", -2, seg=16, bands=5)
        CYL(sc, (LS, 0, RT + 2), (0, 0, 1), 4, 24, "t", -2, seg=10, bands=3)
        drill3(sc, (-27, -40.5, RT / 2), (-1, 0, 0), 3.5, 30, 12, 30)
        MFO(sc, (0, 0, RT), (0, 0, 1), RBO)
        MFO(sc, (LS, 0, RT), (0, 0, 1), RSO, seg=20)
        MFO(sc, (-26.1, 40.5, RT / 2), (-1, 0, 0), 4, seg=12)
        MFO(sc, (-26.1, -40.5, RT / 2), (-1, 0, 0), 4, seg=12)
        cam = sc.cam
        return arc3(cam, (0, 0, RT + 50), (0, 0, 1), 30, 200, 320) + arc3(cam, (LS, 0, RT + 46), (0, 0, 1), 20, 200, 320)
    o, sc = fit(fn, 24, 32, (30, 40, 330, 270), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    s += lead(*cam.xy((RBO * .7, -RBO * .7, RT)), 340, 200, "大端穴（ボーリング）")
    s += lead(*cam.xy((LS + 8, -8, RT)), 340, 80, "小端穴")
    s += lead(*cam.xy((-26, -44, RT / 2)), 340, 250, "ボルト穴・ねじ")
    return s


def r_op4():
    s = title(rtitle(4))
    G = 10

    def fn(sc):
        rod3(sc, split=True, gap=G)
        PR(sc, (-12, -22, RT + 2), (0, 1, 0), [(-12, 60), (12, 60), (0, -8)], 44, "t", -6)

        def cr(s_):
            cam = s_.cam
            return path(P([cam.xy((0, 27, RT)), cam.xy((0, 47, RT))], False) + P([cam.xy((0, -27, RT)), cam.xy((0, -47, RT))], False)
                        + P([cam.xy((0, -47, RT)), cam.xy((0, -47, 0))], False), "crack")
        RAW(sc, cr, ((0, -47, 0), (.1, 47, RT)), -8)
    o, sc = fit(fn, 24, 32, (40, 50, 400, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    a, b = cam.xy((0, 0, RT + 120)), cam.xy((0, 0, RT + 70))
    s += arrow(a[0], a[1], b[0], b[1], None) + lab(a[0] + 10, a[1] + 14, "くさび", "start")
    nt = cam.xy((0, -RBO, RT))
    s += line(nt[0] - 70, nt[1] - 70, nt[0], nt[1], "beam") + text(nt[0] - 74, nt[1] - 76, "レーザノッチ", "end", "al")
    c = cam.xy((-40 - G, -60, 0))
    s += arrow(c[0] + 10, c[1], c[0] - 30, c[1] + 8, None) + lab(c[0] - 20, c[1] + 26, "分離")
    s += tol(466, 284, "破断面の凹凸で再組付けの位置が決まる", "end")
    return s


def r_op5():
    s = title(rtitle(5))

    def fn(sc):
        rod3(sc)
        for v in (40.5, -40.5):
            CYL(sc, (-34, v, RT / 2), (-1, 0, 0), 10, 40, "m", -2, seg=16, bands=5)
            CYL(sc, (-74, v, RT / 2), (-1, 0, 0), 13, 30, "m", -2, seg=16, bands=5, dark=1)
        CYL(sc, (0, 0, -8), (0, 0, 1), 24, RT + 70, "m", -3, seg=20, bands=6)
        for a in (-60, 60, 180):
            t = math.radians(a)
            RAW(sc, lambda s_, t=t: path(P([s_.cam.xy((24.2 * math.cos(t) + d * math.sin(t), 24.2 * math.sin(t) - d * math.cos(t), z))
                                             for d, z in ((-4, RT + 8), (4, RT + 8), (4, RT + 40), (-4, RT + 40))]), "gw"),
                ((-25, -25, RT), (25, 25, RT + 40)), -4)
        MFO(sc, (0, 0, RT), (0, 0, 1), RBO, bias=-2.5)
        return arc3(sc.cam, (0, 0, RT + 60), (0, 0, 1), 40, 200, 330)
    o, sc = fit(fn, 24, 30, (30, 40, 320, 262), ret_scene=True, sh_k=.4)
    cam = sc.cam
    s += o
    s += lead(*cam.xy((-80, -40.5, RT / 2 + 10)), 60, 280, "ナットランナーで塑性域角度締め", "start")
    s += tol(330, 60, "真円度・中心間距離") + tol(330, 76, "大小端の平行度・ねじれ")
    s += lab(*cam.xy((0, 0, RT + 108)), "ホーニング")
    return s


def r_op6():
    s = title(rtitle(6))

    def fn(sc):
        rod3(sc, z0=40)
        for x in (0, LS):
            CYL(sc, (x, 0, 30), (0, 0, 1), 14, 10, "m", seg=16, bands=5)
            BOX(sc, x - 24, -24, 6, 48, 48, 24, "m", dark=1)
        BOX(sc, -60, -60, -10, 270, 120, 16, "m", dark=1)
    o, sc = fit(fn, 24, 28, (30, 50, 330, 262), ret_scene=True, sh_k=.4)
    s += o
    s += rect(350, 110, 100, 64, "m", 4) + text(400, 138, "大端 g", "middle") + text(400, 160, "小端 g", "middle")
    return s


R_OPS = [r_op0, r_op1, r_op2, r_op3, r_op4, r_op5, r_op6]


@dpart("engine.conrod", "ops")
def rod_ops3():
    return [mini(fin(f())) for f in R_OPS]


# =====================================================================================
# engine.piston — Al piston standing crown-up: slipper skirt on the thrust sides (±x), recessed
# pin side (−y) with boss and pin bore, ring belt (top / 2nd / oil groove), crown with valve
# reliefs; Ni-resist ring carrier around the top groove (iron colour)
# =====================================================================================
PR_, PZS, PZP, PTOP = 40, 34, 20, 60
PYF = 0.8 * PR_


def piston3(sc, O=(0, 0, 0), mat="w", lod=1, grooves=True, carrier=True, holes_=True):
    R, zs, zp, yf = PR_, PZS, PZP, PYF
    ox, oy, oz = O
    seg, bnd = (40, 10) if lod else (24, 6)

    def T(x, y, z):
        return (ox + x, oy + y, oz + z)
    sk = arc(0, 0, R, -38, 38, 6 if lod else 3) + [(0.42 * R, yf), (-0.42 * R, yf)] + arc(0, 0, R, 142, 218, 6 if lod else 3) + \
        [(-0.42 * R, -yf), (0.42 * R, -yf)]
    sk = [(x + ox, y + oy) for x, y in sk]
    Z(sc, oz, zs, banded(sk, 2), mat, smooth="outer")
    CYL(sc, T(0, -yf, zp), (0, -1, 0), 13, 2.5, mat, seg=20, bands=5)
    if holes_:
        def bore(s_):
            c = T(0, -yf - 2.6, zp)
            return hole3(s_.cam, c, (0, -1, 0), 10, "w3") + hole3(s_.cam, c, (0, -1, 0), 8.6, "bg")
        RAW(sc, bore, (T(-13, -yf - 2.7, zp - 13), T(13, -yf - 2.6, zp + 13)), -1)
    cm = "t" if carrier and mat != "h" else mat
    if grooves:
        belt = [(zs, 40.5, R, 0, mat), (40.5, 43.5, R - 2.4, 2, mat), (43.5, 47.5, R, 0, mat), (47.5, 49, R - 2.2, 2, mat),
                (49, 52, R, 0, mat), (52, 53.5, R, 0, cm), (53.5, 55, R - 2.2, 2, cm), (55, 56.5, R, 0, cm), (56.5, 60, R - .3, 0, mat)]
    else:
        belt = [(zs, 52, R, 0, mat), (52, 56.5, R, 0, cm), (56.5, 60, R - .3, 0, mat)]
    if not lod:
        belt = [(zs, 60, R, 0, mat)]
    for z0, z1, r, dk, m in belt:
        CYL(sc, T(0, 0, z0), (0, 0, 1), r, z1 - z0, m, seg=seg, bands=bnd, dark=dk)

    def marks(s_):
        o = ""
        if lod and grooves:
            for a in (-112, -94, -76, -58):
                t = math.radians(a)
                o += hole3(s_.cam, T((R - 2.3) * math.cos(t), (R - 2.3) * math.sin(t), 42), (math.cos(t), math.sin(t), 0), 1.1)
        if not lod:
            o += path(vis_arc(s_.cam, T(0, 0, 42), (0, 0, 1), R) + vis_arc(s_.cam, T(0, 0, 48.5), (0, 0, 1), R) +
                      vis_arc(s_.cam, T(0, 0, 54.5), (0, 0, 1), R), "el")
        for (x, y, r) in ((-15, 15, 8.5), (15, 15, 8.5), (-15, -15, 7.5), (15, -15, 7.5)):
            o += hole3(s_.cam, T(x, y, 60.05), (0, 0, 1), r, "w2" if mat != "h" else "hs2", 20)
        return o
    RAW(sc, marks, (T(-R, -R, 60.1), T(R, R, 60.2)), -3)


def vis_arc(cam, C, A, r, seg=40):
    """screen path of the half of a circle (radial normal) that faces the camera."""
    A = GE._norm(A)
    E1, E2, _ = GE.frame(A)
    t = math.atan2(GE._dot(E1, cam.D), -GE._dot(E2, cam.D))

    def nv(a):
        return tuple(math.cos(a) * E1[i] + math.sin(a) * E2[i] for i in range(3))
    if GE._dot(nv(t + math.pi / 2), cam.D) > 0:
        t += math.pi
    h = seg // 2
    return P([cam.xy(V(C, nv(t + math.pi * k / h), r)) for k in range(h + 1)], False)


def MFA(sc, C, A, r, c="mf", bias=-6):
    a = GE._norm(A)
    RAW(sc, lambda s_: path(vis_arc(s_.cam, C, a, r), c), _bb(C, a, r, 0.01), bias)


def ptitle(i):
    return otitle(E.piston_ops, i)


@dpart("engine.piston", "detail")
def piston_detail3():
    _, notes = E.piston_detail()

    def fn(sc):
        piston3(sc)
    o, sc = fit(fn, -30, 28, (60, 44, 290, 262), ret_scene=True, sh_k=.6, sh_dy=-6)
    cam = sc.cam
    xy = cam.xy
    s = o
    s += bal(*xy((5, 25, 60)), 230, 50, 1)
    s += bal(*xy((-PR_ * .9, -PR_ * .44, 48.2)), 40, 120, 2)
    s += bal(*xy((-PR_ * .85, -PR_ * .53, 54.5)), 40, 70, 3)
    s += bal(*xy((0, -PYF - 2.6, PZP + 9)), 60, 262, 4)
    s += bal(*xy((PR_ * .95, -PR_ * .3, 16)), 310, 230, 5)
    s += rect(340, 100, 130, 110, "m", 4) + text(405, 116, "スカート断面（誇張）", "middle", "sm")
    s += ell(405, 160, 44, 34, "w") + circ(405, 160, 39, "o dash")
    s += text(405, 204, "長径／短径 数十〜百数十μm", "middle", "sm")
    return mini(s), notes


def p_op0():
    s = title(ptitle(0))

    def fn(sc):
        piston3(sc, mat="h", grooves=False, holes_=False)
        BOX(sc, -110, -60, -10, 60, 130, 90, "m", dark=1)
        BOX(sc, 50, -60, -10, 60, 130, 90, "m", dark=1)
        BOX(sc, -120, -70, -24, 240, 150, 14, "m", dark=1)
        CYL(sc, (-120, 0, 150), GE._norm((1, 0, -.5)), 26, 36, "m", seg=20, bands=6)
    o, sc = fit(fn, -30, 26, (60, 40, 400, 262), ret_scene=True, sh=False)
    cam = sc.cam
    s += o
    a = cam.xy((-88, 0, 138))
    b = cam.xy((0, 0, 64))
    s += path("M%s %s Q%s %s %s %s" % (n(a[0]), n(a[1]), n(a[0] + 30), n(a[1] - 6), n(b[0]), n(b[1])), "pour")
    s += lead(*cam.xy((-PR_ * .8, -PR_ * .6, 54)), 40, 262, "耐摩環（ニレジスト）", "start")
    s += text(*cam.xy((80, -60, 30)), "金型", "middle", "sm")
    return s


def p_op1():
    s = title(ptitle(1))

    def fn(sc):
        BOX(sc, -70, -70, -24, 500, 150, 14, "m", dark=1)
        BOX(sc, -70, 80, -24, 500, 14, 150, "m", dark=1)
        for k in range(4):
            piston3(sc, (k * 120, 0, -10), lod=0)
        BOX(sc, -70, -70, -36, 500, 170, 12, "m", dark=2)
    o, sc = fit(fn, -24, 26, (30, 54, 450, 262), ret_scene=True, sh=False)
    cam = sc.cam
    pts = [cam.xy(p) for p in ((-70, 80, -10), (430, 80, -10), (430, 80, 126), (-70, 80, 126))]
    s = s + path(P(pts), "hotin") + o
    for k in range(4):
        x, y = cam.xy((k * 120, 0, 70))
        s += heat(x - 8, y - 4, 2, 16)
    return s


def p_op2():
    s = title(ptitle(2))
    t = math.radians(-24)
    tip = (PR_ * math.cos(t), PR_ * math.sin(t), 50)

    def fn(sc):
        piston3(sc, grooves=False, carrier=True)
        CYL(sc, (0, 0, -60), (0, 0, 1), 34, 60, "m", seg=32, bands=8, dark=1)
        ttool(sc, tip, (math.cos(t), math.sin(t), 0), 60)
        MFC(sc, (0, 0, 0), (0, 0, 1), PR_, 60, bias=-2)
        MFA(sc, (0, 0, 60), (0, 0, 1), PR_ - .3)
        cam = sc.cam
        return arc3(cam, (0, 0, -30), (0, 0, 1), 52, 200, 330) + arrow3(cam, V(tip, (0, 0, 1), 16), V(tip, (0, 0, 1), -40))
    o, sc = fit(fn, -30, 26, (60, 40, 400, 266), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    a = cam.xy(V(tip, (0, 0, 1), -20))
    s += lab(a[0] + 16, a[1], "送り", "start")
    s += lab(*cam.xy((0, -60, -46)), "回転")
    return s


def p_op3():
    s = title(ptitle(3))

    def fn(sc):
        piston3(sc)
        CYL(sc, (0, -PYF - 2.6, PZP), (0, -1, 0), 6.5, 70, "t", -4, seg=14, bands=4)
        CYL(sc, (0, -PYF - 72, PZP), (0, -1, 0), 16, 40, "m", -4, seg=20, bands=6, dark=1)
        MFO(sc, (0, -PYF - 2.65, PZP), (0, -1, 0), 10, bias=-3.5, seg=24)
        cam = sc.cam
        return arc3(cam, (0, -PYF - 92, PZP), (0, -1, 0), 26, 200, 330)
    o, sc = fit(fn, -30, 26, (60, 40, 400, 262), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    a, b = cam.xy((0, -PYF - 60, PZP - 34)), cam.xy((0, -PYF - 20, PZP - 34))
    s += arrow(a[0], a[1], b[0], b[1], None) + lab(a[0] - 6, a[1] + 16, "送り", "end")
    s += tol(40, 286, "穴径・真円度1〜2μm・穴形状（ラッパ形状）")
    return s


def p_op4():
    s = title(ptitle(4))
    t = math.radians(-24)
    tip = (PR_ * math.cos(t), PR_ * math.sin(t), 18)

    def fn(sc):
        piston3(sc)
        CYL(sc, (0, 0, -60), (0, 0, 1), 34, 60, "m", seg=32, bands=8, dark=1)
        ttool(sc, tip, (math.cos(t), math.sin(t), 0), 60)
        MFC(sc, (0, 0, 0), (0, 0, 1), PR_, PZS, bias=-2)
    o, sc = fit(fn, -30, 26, (40, 40, 330, 266), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    e = cam.xy(V(tip, (math.cos(t), math.sin(t), 0), 70))
    s += arrow(e[0] - 30, e[1] + 30, e[0] + 10, e[1] + 30, None, both=True) + lab(e[0] - 10, e[1] + 48, "高速往復")
    s += ell(420, 110, 36, 28, "w") + circ(420, 110, 32, "o dash") + text(420, 156, "断面：楕円", "middle", "sm")
    return s


def p_op5():
    s = title(ptitle(5))
    t = math.radians(-24)
    tip = ((PR_ - 2.2) * math.cos(t), (PR_ - 2.2) * math.sin(t), 48.25)

    def fn(sc):
        piston3(sc)
        CYL(sc, (0, 0, -60), (0, 0, 1), 34, 60, "m", seg=32, bands=8, dark=1)
        SQ(sc, tip, (math.cos(t), math.sin(t), 0), 1.2, .7, 14, "t", -8)
        SQ(sc, V(tip, (math.cos(t), math.sin(t), 0), 14), (math.cos(t), math.sin(t), 0), 6, 6, 50, "m", -8, dark=1)
        cam = sc.cam
        return arc3(cam, (0, 0, -30), (0, 0, 1), 52, 200, 330) + \
            "".join(path(vis_arc(cam, (0, 0, z), (0, 0, 1), PR_ + .5), "mf") for z in (42, 48.25, 54.25))
    o, sc = fit(fn, -30, 26, (60, 40, 400, 262), ret_scene=True, sh_k=.5)
    s += o
    s += tol(40, 286, "溝幅・側面平行度・側面粗さ")
    return s


def p_op6():
    s = title(ptitle(6))

    def fn(sc):
        piston3(sc)

        def coat(s_):
            cam = s_.cam
            top = [cam.xy((PR_ * math.cos(math.radians(a)), PR_ * math.sin(math.radians(a)), 30)) for a in range(-38, 39, 8)]
            bot = [cam.xy((PR_ * math.cos(math.radians(a)), PR_ * math.sin(math.radians(a)), 4)) for a in range(38, -39, -8)]
            o = path(P(top + bot), "hotband")
            o += path(vis_arc(cam, (0, 0, 54.25), (0, 0, 1), PR_ - 2.2), "coat")
            return o
        RAW(sc, coat, ((PR_ - 1, -PR_, 0), (PR_, PR_, 60)), -6)
    o, sc = fit(fn, -30, 26, (40, 40, 300, 262), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    x, y = cam.xy((PR_, 0, 18))
    s += rect(x + 16, y - 60, 14, 120, "mesh") + poly([(x + 36, y - 10), (x + 56, y - 20), (x + 56, y + 20)], "t")
    s += text(x + 66, y - 70, "スクリーン印刷", "start", "al") + lead(*cam.xy((-PR_ * .8, -PR_ * .6, 54.25)), 40, 60, "硬質アルマイト", "start")
    return s


def p_op7():
    s = title(ptitle(7))

    def fn(sc):
        piston3(sc)
        for sg in (1, -1):
            SQ(sc, (sg * (PR_ + 3), 0, 20), (sg, 0, 0), 8, 10, 40, "m", -2)
        BOX(sc, 150, -40, -12, 90, 80, 12, "m", dark=1)
        BOX(sc, 160, -30, 0, 70, 60, 6, "m")
        piston3(sc, (195, 0, 6), lod=0)
        BOX(sc, 150, 50, -12, 90, 18, 70, "m", dark=1)
    o, sc = fit(fn, -30, 26, (40, 40, 450, 250), ret_scene=True, sh_k=.5)
    cam = sc.cam
    s += o
    for sg in (1, -1):
        x, y = cam.xy((sg * (PR_ + 1), 0, 20))
        s += circ(x, y, 2.5, "fdot")
    d = cam.xy((195, 59, 34))
    s += text(d[0], d[1] + 4, "g", "middle")
    s += text(*cam.xy((0, 0, -30)), "エアマイクロで外径ランク", "middle")
    return s


P_OPS = [p_op0, p_op1, p_op2, p_op3, p_op4, p_op5, p_op6, p_op7]


@dpart("engine.piston", "ops")
def piston_ops3():
    return [mini(fin(f())) for f in P_OPS]
