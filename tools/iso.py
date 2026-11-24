# -*- coding: utf-8 -*-
"""Tiny isometric drawing kit that emits the same face classes as the site's illustrations."""
import math

EX = (0.985, 0.180)    # +x : right, slightly down
EY = (0.792, -0.608)   # +y : depth, up-right
VIEW = (0.30, -0.80, 0.52)          # toward the viewer (+x, -y, +z visible)
LIGHT = (-0.35, -0.55, 0.76)

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

class Scene:
    def __init__(s, ox, oy, k=1.0, dy=0.55):
        s.ox, s.oy, s.k, s.dy = ox, oy, k, dy
        s.items = []          # (depth, svg)
        s.over = []           # drawn last (arrows, text)
        s.under = []          # drawn first (shadows)
    def p(s, x, y, z):
        k = s.k
        return (s.ox + k * (x * EX[0] + y * s.dy * EY[0]), s.oy + k * (x * EX[1] + y * s.dy * EY[1] - z))
    def pts(s, P): return " ".join(f"{f(a)},{f(b)}" for a, b in P)
    def path(s, P, cls, extra=""):
        d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in P) + "Z"
        return f'<path class="{cls}"{extra} d="{d}"/>'
    def depth(s, x, y, z):  # larger = farther from viewer
        return -(x * VIEW[0] + y * VIEW[1] + z * VIEW[2])
    def add(s, d, svg): s.items.append((d, svg))

    # --- solids ---
    def box(s, x, y, z, dx, dy, dz, mat, d=None):
        P = s.p
        front = [P(x, y, z), P(x + dx, y, z), P(x + dx, y, z + dz), P(x, y, z + dz)]
        right = [P(x + dx, y, z), P(x + dx, y + dy, z), P(x + dx, y + dy, z + dz), P(x + dx, y, z + dz)]
        top = [P(x, y, z + dz), P(x + dx, y, z + dz), P(x + dx, y + dy, z + dz), P(x, y + dy, z + dz)]
        svg = s.path(front, f"{mat}s2 x") + s.path(right, f"{mat}s4 x") + s.path(top, mat, ' fill-rule="evenodd"')
        s.add(d if d is not None else s.depth(x + dx / 2, y + dy / 2, z + dz / 2), svg)

    def cyl(s, c, axis, r, L, mat, n=28, d=None, cap=True, hole=0, holemat="dk", r2=None):
        """cylinder from centre c along axis ('x','y','z') of length L; r2 = radius at far end (frustum)."""
        r2 = r if r2 is None else r2
        ax = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
        u, v = {"x": ((0, 1, 0), (0, 0, 1)), "y": ((1, 0, 0), (0, 0, 1)), "z": ((1, 0, 0), (0, 1, 0))}[axis]
        def ring(t, rr):
            out = []
            for i in range(n):
                a = 2 * math.pi * i / n
                ca, sa = math.cos(a), math.sin(a)
                out.append(tuple(c[j] + ax[j] * t + rr * (ca * u[j] + sa * v[j]) for j in range(3)))
            return out
        A, B = ring(0, r), ring(L, r2)
        faces = []
        for i in range(n):
            j = (i + 1) % n
            a = 2 * math.pi * (i + .5) / n
            nv = [math.cos(a) * u[q] + math.sin(a) * v[q] for q in range(3)]
            vis = sum(nv[q] * VIEW[q] for q in range(3))
            if vis <= 0.02: continue
            lum = sum(nv[q] * LIGHT[q] for q in range(3))
            sfx = 1 if lum > .45 else 2 if lum > .05 else 3 if lum > -.35 else 4
            quad = [s.p(*A[i]), s.p(*A[j]), s.p(*B[j]), s.p(*B[i])]
            faces.append(s.path(quad, f"{mat}s{sfx}"))
        # visible cap: the end whose outward normal faces the viewer
        vis_end = sum(ax[q] * VIEW[q] for q in range(3)) > 0
        capring, rr, t = (B, r2, L) if vis_end else (A, r, 0)
        svg = "".join(faces)
        outline_a = [s.p(*q) for q in A]; outline_b = [s.p(*q) for q in B]
        if cap:
            svg += s.path([s.p(*q) for q in capring], mat, ' fill-rule="evenodd"')
            if hole:
                hr = []
                for i in range(n):
                    a = 2 * math.pi * i / n
                    hr.append(s.p(*[c[j] + ax[j] * t + hole * (math.cos(a) * u[j] + math.sin(a) * v[j]) for j in range(3)]))
                svg += s.path(hr, holemat)
        mid = [c[q] + ax[q] * L / 2 for q in range(3)]
        s.add(d if d is not None else s.depth(*mid), svg)

    def disc_on_top(s, cx, cy, z, r, cls="dk", n=24, d=None):
        P = [s.p(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
        s.add(d if d is not None else s.depth(cx, cy, z) - .01, s.path(P, cls))

    def shadow(s, cx, cy, rx, ry):
        x, y = s.p(cx, cy, 0)
        s.under.append(f'<ellipse class="sh" cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}"/>')

    # --- annotations ---
    def arrow(s, a, b, both=False):
        (x1, y1), (x2, y2) = s.p(*a), s.p(*b)
        out = [f'<line class="a" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>']
        def head(xa, ya, xb, yb):
            L = math.hypot(xb - xa, yb - ya) or 1; ux, uy = (xb - xa) / L, (yb - ya) / L
            tip = (xb + ux * 3.5, yb + uy * 3.5); bx, by = xb - ux * 3, yb - uy * 3
            return f'<polygon class="af" points="{f(tip[0])},{f(tip[1])} {f(bx - uy * 3.6)},{f(by + ux * 3.6)} {f(bx + uy * 3.6)},{f(by - ux * 3.6)}"/>'
        out.append(head(x1, y1, x2, y2))
        if both: out.append(head(x2, y2, x1, y1))
        s.over.append("".join(out))
    def arc(s, c, axis, r, a0, a1, n=18):
        ax = {"x": ((0, 1, 0), (0, 0, 1)), "y": ((1, 0, 0), (0, 0, 1)), "z": ((1, 0, 0), (0, 1, 0))}[axis]
        u, v = ax
        P = [s.p(*[c[j] + r * (math.cos(a) * u[j] + math.sin(a) * v[j]) for j in range(3)]) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]
        d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in P)
        (xa, ya), (xb, yb) = P[-2], P[-1]
        L = math.hypot(xb - xa, yb - ya) or 1; ux, uy = (xb - xa) / L, (yb - ya) / L
        tip = (xb + ux * 3.5, yb + uy * 3.5); bx, by = xb - ux * 2.5, yb - uy * 2.5
        s.over.append(f'<path class="a" d="{d}"/><polygon class="af" points="{f(tip[0])},{f(tip[1])} {f(bx - uy * 3.6)},{f(by + ux * 3.6)} {f(bx + uy * 3.6)},{f(by - ux * 3.6)}"/>')
    def line(s, a, b, cls="hl"):
        (x1, y1), (x2, y2) = s.p(*a), s.p(*b)
        s.over.append(f'<line class="{cls}" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"/>')
    def text(s, x, y, t, anchor="middle", cls=""):
        c = f' class="{cls}"' if cls else ""
        s.over.append(f'<text x="{f(x)}" y="{f(y)}" text-anchor="{anchor}"{c}>{t}</text>')
    def textp(s, P3, t, dx=0, dy=0, anchor="middle", cls=""):
        x, y = s.p(*P3); s.text(x + dx, y + dy, t, anchor, cls)

    def svg(s, label, w=320, h=200):
        body = "".join(s.under) + "".join(v for _, v in sorted(s.items, key=lambda t: -t[0])) + "".join(s.over)
        return f'<svg class="ilu " viewBox="0 0 {w} {h}" role="img" aria-label="{label}">{body}</svg>'
