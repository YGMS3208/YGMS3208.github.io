"""Composite gear-manufacturing scenes built on il_gear (involute teeth, shaded 3D).
Each scene draws into screen space at origin (ox, oy) with scale s and returns svg.
`lab` controls whether in-drawing labels are added (pictos add their own)."""
import math
from il_gear import (Cam, prism, gear3, ring_gear3, hob, circle_outline, gear_outline, internal_outline, spline_outline,
                     rotate_outline, outline_d, rack_pts, render_items, frame, bevel_ring, cyl, PI, ALPHA, _pd)
from il_base import arrow, rot, text, line, path, circ, ell, rect, poly, pline, n


def al(x, y, t, a="middle"):
    return text(x, y, t, a, "al")


def sm(x, y, t, a="middle"):
    return text(x, y, t, a, "sm")


def leader(ax, ay, lx, ly, t, anchor="start"):
    s = circ(ax, ay, 2.2, "leadd") + line(ax, ay, lx, ly, "leadl")
    dx = 4 if anchor == "start" else (-4 if anchor == "end" else 0)
    return s + text(lx + dx, ly + 4, t, anchor)


def _ell_arc(cam, c, r, z, a0, a1):
    """rotation arrow drawn on a horizontal circle (radius r at height z) around world centre c. angles deg (world)."""
    cx, cy = cam.xy((c[0], c[1], z))
    s = cam.s
    ry = r * s * cam.se
    return rot(cx, cy, r * s, ry, a0, a1)


# ------------------------------------------------------------------ work gear helpers
def work_gear(cam, z, rp, width, helix=18, bore=None, cut_frac=None, hl="mfe", mat="w", phase=0.0, zc=0.0, hub=True):
    """vertical-axis work gear centred at height zc. cut_frac: fraction of face width already toothed (from top)."""
    m = 2 * rp / z
    ra = rp + m
    zt, zb = zc + width / 2, zc - width / 2
    bore = bore if bore is not None else rp * 0.34
    out = ""
    if cut_frac is not None and cut_frac < 1:
        zi = zt - width * cut_frac
        out += prism(cam, (0, 0, zb), (0, 0, 1), circle_outline(ra, 72, 24), zi - zb, mat,
                     holes=[circle_outline(bore, 40, 40)], smooth=True)
        out += gear3(cam, (0, 0, zi), (0, 0, 1), z, rp, zt - zi, mat, helix=helix, bore=bore, hl=hl, phase=phase)
    else:
        out += gear3(cam, (0, 0, zb), (0, 0, 1), z, rp, width, mat, helix=helix, bore=bore, hl=hl, phase=phase)
    if hub:
        # recessed web ring on the top face for realism
        cx, cy = cam.xy((0, 0, zt))
        rr = (rp - 2.4 * m) * cam.s
        out += '<ellipse class="thin o" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(cx), n(cy), n(rr), n(rr * cam.se))
    return out


# ------------------------------------------------------------------ scenes
def sc_hobbing(ox, oy, s=1.0, lab=True, z=30, rp=92, width=64, el=30, shaft=None, helix=18, hr=22, L=196, cut=0.5):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    zt = width / 2
    zi = zt - width * cut
    out = ""
    if shaft:
        sr, below, above = shaft
        out += cyl(cam, (0, 0, -width / 2 - below), (0, 0, 1), sr, below, "w")
    out += work_gear(cam, z, rp, width, cut_frac=cut, helix=helix, bore=0 if shaft else None, hub=not shaft)
    if shaft:
        out += cyl(cam, (0, 0, zt), (0, 0, 1), sr, above, "w")
    hx, hy = cam.xy((rp * 0.62 + (L - 196) * 0.3, -(rp + hr + 1.25 * m), zi - 3))
    ang = -5
    out += hob(hx, hy, L * s, hr * s, m * s, ang, "t", gashes=10, g0=0.15)
    # arrows
    out += _ell_arc(cam, (0, 0), ra + 18, zt, 196, 246)
    ex = hx + math.cos(math.radians(ang)) * (L / 2 + 58) * s
    ey = hy + math.sin(math.radians(ang)) * (L / 2 + 58) * s
    out += rot(ex, ey, 7 * s, (hr + 10) * s, -70, 70)
    fx = ox + (ra + 44) * s
    fy0 = cam.xy((0, 0, zt))[1] - 6 * s
    out += arrow(fx, fy0, fx, fy0 + 56 * s, None)
    if lab:
        out += al(ox - (ra - 10) * s, cam.xy((0, ra + 18, zt))[1] - 8 * s, "ワーク（同期回転）", "middle")
        out += al(ex - 14 * s, ey + (hr + 22) * s, "ホブ回転", "end")
        out += al(fx + 8 * s, fy0 + 32 * s, "送り", "start")
        a1 = cam.xy((-ra * 0.97, -ra * 0.2, zt - 10))
        b1 = cam.xy((-ra * 0.99, -ra * 0.1, zi - 14))
        out += leader(a1[0], a1[1], a1[0] - 26 * s, a1[1] - 34 * s, "創成された歯", "end")
        out += leader(b1[0], b1[1], b1[0] - 20 * s, b1[1] + 30 * s, "未加工部", "end")
    return out


def sc_gear_grind(ox, oy, s=1.0, lab=True, z=30, rp=92, width=60, el=30, honing=False):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    zt = width / 2
    out = work_gear(cam, z, rp, width)
    wr = 34
    hx, hy = cam.xy((rp * 0.55, -(rp + wr + 1.25 * m), -4))
    L = 230
    ang = -5
    out += hob(hx, hy, L * s, wr * s, m * s, ang, "gw", grind=True)
    out += _ell_arc(cam, (0, 0), ra + 18, zt, 196, 246)
    ex = hx + math.cos(math.radians(ang)) * (L / 2 + 58) * s
    ey = hy + math.sin(math.radians(ang)) * (L / 2 + 58) * s
    out += rot(ex, ey, 7 * s, (wr + 10) * s, -70, 70)
    if lab:
        out += al(ox - (ra + 4) * s, cam.xy((0, ra + 18, zt))[1] - 8 * s, "ワーク（同期回転）")
        out += al(ex - 14 * s, ey + (wr + 22) * s, "砥石回転", "end")
        a1 = cam.xy((-ra * 0.97, -ra * 0.2, zt - 12))
        out += leader(a1[0], a1[1], a1[0] - 20 * s, a1[1] + 34 * s, "歯面", "end")
    return out


def sc_shaping(ox, oy, s=1.0, lab=True, z=30, rp=84, width=46, el=32):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    zt = width / 2
    zc = 18
    rc = m * zc / 2
    beta = math.radians(-28)
    a = rp + rc
    p1, p2 = beta + PI / z, beta + PI
    out = work_gear(cam, z, rp, width, helix=0, cut_frac=1, phase=p1)
    C = (a * math.cos(beta), a * math.sin(beta))
    # cutter: pinion-type cutter from zt-18 up, with spindle
    z0 = zt - 20
    out += gear3(cam, (C[0], C[1], z0), (0, 0, 1), zc, rc, 26, "t", phase=p2, bore=rc * 0.3)
    out += cyl(cam, (C[0], C[1], z0 + 26), (0, 0, 1), rc * 0.55, 18, "m")
    out += cyl(cam, (C[0], C[1], z0 + 44), (0, 0, 1), rc * 0.34, 58, "m")
    tx, ty = cam.xy((C[0], C[1], z0 + 26))
    ax_ = tx + (rc + 26) * s
    ay_ = cam.xy((C[0], C[1], z0 + 80))[1]
    out += arrow(ax_, ay_, ax_, ay_ + 64 * s, None, both=True)
    out += _ell_arc(cam, (0, 0), ra + 18, zt, 150, 205)
    out += _ell_arc(cam, C, rc + 14, z0 + 30, 200, 330)
    if lab:
        out += al(ax_ + 7 * s, ay_ + 36 * s, "上下往復", "start")
        out += al(tx - (rc * 0.5 + 12) * s, cam.xy((C[0], C[1], z0 + 90))[1], "ピニオンカッタ", "end")
        out += al(ox - (ra + 26) * s, cam.xy((0, 0, zt))[1] + 4 * s, "同期回転", "end")
    return out


def sc_skiving(ox, oy, s=1.0, lab=True, z=60, rp=110, width=40, el=38):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    r_out = rp + 22
    out = ring_gear3(cam, (0, 0, -width / 2), (0, 0, 1), z, rp, r_out, width, "w", hl="mfe")
    zc = 22
    rc = m * zc / 2
    beta = math.radians(90)
    a = rp - rc
    C = (a * math.cos(beta), a * math.sin(beta))
    sig = math.radians(22)
    A = (math.sin(sig), 0, math.cos(sig))
    zb = width / 2 - 10
    O = (C[0] - A[0] * 0, C[1], zb)
    out += gear3(cam, O, A, zc, rc, 16, "t", helix=22, phase=beta + PI)
    top = (O[0] + A[0] * 16, O[1], O[2] + A[2] * 16)
    out += cyl(cam, top, A, rc * 0.42, 40, "m")
    out += _ell_arc(cam, (0, 0), r_out + 16, width / 2, 20, 80)
    cx, cy = cam.xy((top[0] + A[0] * 26, top[1], top[2] + A[2] * 26))
    out += rot(cx, cy, (rc * 0.42 + 14) * s, (rc * 0.42 + 14) * s * 0.34, 200, 330)
    if lab:
        out += al(cx + (rc + 10) * s, cy - 10 * s, "スカイビングカッタ", "start")
        out += sm(cx + (rc + 10) * s, cy + 6 * s, "軸を傾けて同期回転", "start")
        rx, ry = cam.xy((r_out * 0.7, -r_out * 0.7, width / 2))
        out += al(rx + 12 * s, ry + 30 * s, "ワーク回転", "start")
        ix, iy = cam.xy((-rp * 0.86, rp * 0.3, width / 2 - 6))
        out += leader(ix, iy, ix - 14 * s, iy - 40 * s, "内歯", "end")
    return out


def sc_shaving(ox, oy, s=1.0, lab=True, z=30, rp=84, width=44, el=30):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    zt = width / 2
    zc = 37
    rc = m * zc / 2
    beta = math.radians(-8)
    a = rp + rc
    C = (a * math.cos(beta), a * math.sin(beta))
    p1, p2 = beta + PI / z, beta + PI
    out = work_gear(cam, z, rp, width, helix=18, phase=p1)
    sig = math.radians(15)
    A = (math.sin(sig) * math.sin(beta), -math.sin(sig) * math.cos(beta) * 0 + 0, math.cos(sig))
    A = (math.sin(sig) * -math.sin(beta), math.sin(sig) * math.cos(beta), math.cos(sig))
    wc = 30
    O = (C[0] - A[0] * wc / 2, C[1] - A[1] * wc / 2, -A[2] * wc / 2)
    out += gear3(cam, O, A, zc, rc, wc, "t", helix=-3, phase=p2, bore=rc * 0.3, slices=3, grooves=7)
    out += _ell_arc(cam, (0, 0), ra + 18, zt, 150, 205)
    out += _ell_arc(cam, C, rc + 14, wc / 2, 20, 70)
    if lab:
        cx, cy = cam.xy((C[0], C[1], wc / 2))
        out += al(cx, cy - (rc * 0.5 + 30) * s, "シェービングカッタ", "middle")
        out += sm(cx, cy - (rc * 0.5 + 16) * s, "歯面の溝（セレーション）が刃", "middle")
        out += al(ox - (ra + 26) * s, cam.xy((0, 0, zt))[1] + 4 * s, "ワーク", "end")
    return out


def sc_honing(ox, oy, s=1.0, lab=True, z=30, rp=70, el=40):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    zr = 44
    rr = m * zr / 2
    r_out = rr + 26
    wr = 30
    out = ring_gear3(cam, (0, 0, -wr / 2), (0, 0, 1), zr, rr, r_out, wr, "gw")
    beta = math.radians(90)
    a = rr - rp
    C = (a * math.cos(beta), a * math.sin(beta))
    sig = math.radians(12)
    A = (math.sin(sig), 0, math.cos(sig))
    ww = 34
    O = (C[0] - A[0] * ww * 0.4, C[1], wr / 2 - ww * 0.75)
    out += gear3(cam, O, A, z, rp, ww, "w", helix=18, phase=beta + PI / z + PI, bore=rp * 0.34, hl="mfe")
    out += _ell_arc(cam, (0, 0), r_out + 16, wr / 2, 20, 80)
    if lab:
        rx, ry = cam.xy((r_out * 0.72, -r_out * 0.72, wr / 2))
        out += al(rx + 6 * s, ry + 30 * s, "内歯砥石", "start")
        wx, wy = cam.xy((C[0], C[1], wr / 2 + ww * 0.5))
        out += al(wx, wy - (rp * 0.5 + 16) * s, "ワーク（軸交差）", "middle")
    return out


def sc_chamfer(ox, oy, s=1.0, lab=True, z=30, rp=84, width=44, el=34):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    zt, zb = width / 2, -width / 2
    zc = 26
    rc = m * zc / 2
    beta = math.radians(-12)
    a = rp + rc
    C = (a * math.cos(beta), a * math.sin(beta))
    p1, p2 = beta + PI / z, beta + PI
    out = work_gear(cam, z, rp, width, helix=0, phase=p1, hl=None)
    # chamfer band along the top tooth edges
    cx, cy = cam.xy((0, 0, zt))
    d = outline_d([(u * s, v * s, 0) for u, v, f in gear_outline(z, rp, phase=p1)], cx, cy, cam.se)
    out += '<path class="chbd" d="%s"/><path class="mfe" d="%s"/>' % (d, d)
    # two roll-chamfer tools (top and bottom edge)
    out += gear3(cam, (C[0], C[1], zt - 8), (0, 0, 1), zc, rc, 12, "t", phase=p2, bore=rc * 0.3,
                 scale=lambda t: 1.0 - 0.1 * t)
    out += cyl(cam, (C[0], C[1], zt + 4), (0, 0, 1), rc * 0.3, 30, "m")
    if lab:
        tx, ty = cam.xy((C[0] + rc * 0.4, C[1], zt + 2))
        out += al(tx, ty - (rc * 0.5 + 26) * s, "面取り工具", "middle")
        ex, ey = cam.xy((-ra * 0.72, -ra * 0.7, zt))
        out += leader(ex, ey, ex - 16 * s, ey + 48 * s, "歯端のエッジ", "end")
    return out


def sc_mesh(ox, oy, s=1.0, lab=True, z=30, rp=84, width=40, el=34, master_z=20, test="mesh"):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    rc = m * master_z / 2
    beta = math.radians(-10)
    a = rp + rc
    C = (a * math.cos(beta), a * math.sin(beta))
    p1, p2 = beta + PI / z, beta + PI
    out = work_gear(cam, z, rp, width, helix=18, phase=p1, hl=None)
    out += gear3(cam, (C[0], C[1], -width / 2), (0, 0, 1), master_z, rc, width, "t", helix=-18, phase=p2, bore=rc * 0.3)
    out += cyl(cam, (C[0], C[1], width / 2), (0, 0, 1), rc * 0.3, 26, "m")
    cx, cy = cam.xy((C[0], C[1], width / 2))
    if lab:
        out += al(cx, cy - (rc * 0.5 + 40) * s, "マスタギヤ", "middle")
        out += al(ox - (ra + 20) * s, cam.xy((0, 0, width / 2))[1] + 4 * s, "ワーク", "end")
    return out


def sc_measure(ox, oy, s=1.0, lab=True, z=30, rp=84, width=40, el=34):
    cam = Cam(ox, oy, 0, el, s)
    m = 2 * rp / z
    ra = rp + m
    out = cyl(cam, (0, 0, -width / 2 - 26), (0, 0, 1), ra + 22, 16, "m")
    out += cyl(cam, (0, 0, -width / 2 - 10), (0, 0, 1), rp * 0.3, 10, "m")
    ph = -PI / 2 + PI / z
    out += work_gear(cam, z, rp, width, helix=18, hl=None, phase=ph)
    # probe from front-right touching a flank
    tip = (rp * 0.99 * math.cos(-0.5), rp * 0.99 * math.sin(-0.5), 0)
    px, py = cam.xy((tip[0], tip[1], width / 2 + 2))
    out += path("M%s %s L%s %s L%s %s" % (n(px), n(py - 4 * s), n(px + 40 * s), n(py - 40 * s), n(px + 110 * s), n(py - 40 * s)), "probe")
    out += circ(px, py - 2 * s, 4 * s, "ball") + rect(px + 104 * s, py - 60 * s, 40 * s, 40 * s, "m2", 2)
    out += _ell_arc(cam, (0, 0), ra + 34, -width / 2 - 18, 200, 250)
    if lab:
        out += al(px + 70 * s, py - 70 * s, "測定子（倣い）", "middle")
        out += al(ox - (ra + 20) * s, cam.xy((0, 0, -width / 2 - 18))[1] + 30 * s, "回転テーブル", "end")
    return out


def sc_spline_roll(ox, oy, s=1.0, lab=True, zs=24, r=36, el=18, az=-24):
    """rack-die spline rolling seen along the shaft axis."""
    cam = Cam(ox, oy, az, el, s)
    m = 2 * r / zs
    L = 70
    out = ""
    # shaft (axis toward viewer = -y)
    A = (0, -1, 0)
    out += cyl(cam, (0, L * 0.9, 0), A, r * 0.82, L * 0.9, "w")
    out += gear3(cam, (0, 0, 0), (0, -1, 0), zs, r, L * 0.001 + 1, "w", caps=False) if False else ""
    out += prism(cam, (0, L * 0.4, 0), A, gear_outline(zs, r, phase=PI / 2), L * 0.4, "w", hl="mfe")
    # rack dies: plate below and above with teeth
    th = 22
    for side in (1, -1):
        pts = rack_pts(-120, 120, 0, m, up=(side > 0), phase=PI * m / 2 if side > 0 else 0)
        hf = 1.25 * m * side
        poly_ = pts + [(120, hf), (120, hf + th * side), (-120, hf + th * side), (-120, hf)]
        loop = [(x, r * side + v, i // 4) for i, (x, v) in enumerate(poly_)]
        out += prism(cam, (0, L * 0.55, 0), (0, -1, 0), loop, L * 0.62, "t")
    tx, ty = cam.xy((0, 0, r + 40))
    bx, by = cam.xy((0, 0, -r - 40))
    out += arrow(ox + 60 * s, ty - 18 * s, ox + 130 * s, ty - 18 * s, None)
    out += arrow(ox - 60 * s, by + 22 * s, ox - 130 * s, by + 22 * s, None)
    if lab:
        out += al(ox + 136 * s, ty - 14 * s, "ラックダイス", "start")
        out += al(ox - 136 * s, by + 26 * s, "逆方向に移動", "end")
    return out


def face_gear_2d(cx, cy, z, rp, cls="w", phase=0.0, bore=None, sy=1.0, s=1.0):
    pts = [(u * s, v * s, f) for u, v, f in gear_outline(z, rp, phase=phase)]
    out = '<path class="%s" d="%s"/>' % (cls, outline_d(pts, cx, cy, sy))
    if bore:
        out += ell(cx, cy, bore * s, bore * s * sy, "bg")
    return out


def tooth_section(x, y, m, nteeth=4, s=1.0, cls="w", hl_root=False, shots=False):
    """a few teeth of a large gear, seen along the axis (profile view), teeth pointing up. Returns svg."""
    z = 60
    rp = m * z / 2
    pts = gear_outline(z, rp, phase=-PI / 2)
    step = 2 * PI / z
    lo, hi = -PI / 2 - step * (nteeth / 2 + 0.02), -PI / 2 + step * (nteeth / 2 + 0.02)
    sel = [(u, v) for u, v, f in pts if lo <= math.atan2(v, u) <= hi]
    sel.sort(key=lambda p: math.atan2(p[1], p[0]))
    cyc = y + rp * s
    ps = [(x + u * s, cyc + v * s) for u, v in sel]
    rb = rp - 3.2 * m
    a0, a1 = math.atan2(sel[0][1], sel[0][0]), math.atan2(sel[-1][1], sel[-1][0])
    bottom = [(x + rb * s * math.cos(a1 - k * (a1 - a0) / 12), cyc + rb * s * math.sin(a1 - k * (a1 - a0) / 12)) for k in range(13)]
    d = "M" + " L".join(n(px) + " " + n(py) for px, py in ps + bottom) + "Z"
    out = '<path class="%s" d="%s"/>' % (cls, d)
    return out, ps


def box3(cam, c, sx, sy, sz, mat="m", collect=None):
    """axis-aligned box centred at c (x,y,z-bottom)."""
    loop = [(-sx / 2, -sy / 2, 0), (sx / 2, -sy / 2, 1), (sx / 2, sy / 2, 2), (-sx / 2, sy / 2, 3)]
    return prism(cam, c, (0, 0, 1), loop, sz, mat, collect=collect)


def pinion_bevel(cam, O, A, z, r0, L, mat="w", taper=0.45, spiral=0.5, hl=None, shaft_len=0, shaft_r=None):
    """conical (bevel / hypoid) pinion: gear outline extruded along A, shrinking and twisting."""
    out = ""
    if shaft_len:
        E = (O[0] - A[0] * shaft_len, O[1] - A[1] * shaft_len, O[2] - A[2] * shaft_len)
        out += cyl(cam, E, A, shaft_r or r0 * 0.5, shaft_len, mat)
    out += prism(cam, O, A, gear_outline(z, r0, phase=0.1), L, mat, twist=spiral, slices=6,
                 scale=lambda t: 1 - taper * t, hl=hl)
    return out


def sc_hypoid_cut(ox, oy, s=1.0, lab=True, el=36):
    cam = Cam(ox, oy, 0, el, s)
    out = bevel_ring(cam, (0, 0, -16), 70, 118, 26, 41, "w")
    # face-hobbing cutter head over the right side of the face
    C = (96, -14, 30)
    sig = math.radians(14)
    A = (-math.sin(sig), 0, math.cos(sig))
    out_blades = []
    rh = 46
    for k in range(16):
        a = 2 * PI * k / 16
        bx, by = C[0] + rh * math.cos(a) * 0.98, C[1] + rh * math.sin(a)
        out_blades.append(box3(cam, (bx, by, C[2] - 16), 5, 9, 18, "m"))
    back = "".join(b for k, b in enumerate(out_blades) if math.sin(2 * PI * k / 16) > 0)
    front = "".join(b for k, b in enumerate(out_blades) if math.sin(2 * PI * k / 16) <= 0)
    out += back
    out += cyl(cam, (C[0], C[1], C[2]), (0, 0, 1), rh + 6, 16, "t")
    out += cyl(cam, (C[0], C[1], C[2] + 16), (0, 0, 1), 18, 40, "m")
    out += front
    cx, cy = cam.xy((C[0], C[1], C[2] + 16))
    out += rot(cx, cy, (rh + 18) * s, (rh + 18) * s * cam.se, 200, 320)
    out += _ell_arc(cam, (0, 0), 132, 10, 110, 160)
    if lab:
        out += al(cx + 12 * s, cy - (rh * cam.se + 58) * s, "カッタヘッド（ブレード多数）", "middle")
        lx, ly = cam.xy((-80, -80, 10))
        out += leader(lx, ly, lx - 20 * s, ly + 40 * s, "まがりばかさ歯", "end")
    return out


def sc_hypoid_pair(ox, oy, s=1.0, lab=True, el=34, lap=True):
    cam = Cam(ox, oy, 0, el, s)
    out = ""
    # pinion behind-left? put pinion in front-left, axis toward ring centre with hypoid offset (below centre)
    out += bevel_ring(cam, (0, 0, -16), 70, 118, 26, 41, "w")
    tz = -16 + 26 + 19
    out += pinion_bevel(cam, (-150, -34, tz + 26), (1, 0.0, -0.06), 11, 30, 44, "w", taper=0.38, spiral=0.8,
                        shaft_len=70, shaft_r=14)
    if lab:
        px, py = cam.xy((-190, -34, tz + 26))
        out += al(px, py - 42 * s, "ドライブピニオン", "middle")
        rx, ry = cam.xy((80, 90, 10))
        out += al(rx + 20 * s, ry - 16 * s, "リングギヤ", "start")
    return out
