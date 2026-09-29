from il_base import *
import math

PARTS = {}


def part(key):
    def deco(fn):
        PARTS[key] = fn
        return fn
    return deco


# ---------------------------------------------------------------- plant
def press_frame(x, y, w, h, panel=True):
    s = rect(x, y + h - 16, w, 16, "m2")                      # bolster
    s += rect(x + 4, y + 20, 11, h - 36, "m")                  # uprights
    s += rect(x + w - 15, y + 20, 11, h - 36, "m")
    s += rect(x, y, w, 24, "m2", 3)                            # crown
    s += rect(x + 18, y + 34, w - 36, 16, "m3")                # slide
    s += rect(x + 20, y + 50, w - 40, 10, "t")                 # upper die
    s += rect(x + 20, y + h - 30, w - 40, 14, "t")             # lower die
    if panel:
        s += path("M%s %s q%s -10 %s 0" % (n(x + 22), n(y + h - 31), n((w - 44) / 2), n(w - 44)), "w")
    return s


@part("plant.press")
def _():
    s = shadow(160, 182, 150)
    for i, x in enumerate((14, 116, 218)):
        s += press_frame(x, 34, 88, 146)
    s += path("M104 150 l14 0", "a") + head(118, 150, 0) + path("M206 150 l14 0", "a") + head(220, 150, 0)
    return s


@part("plant.body")
def _():
    s = shadow(160, 180, 130)
    s += path(car_d(62, 166, 1.0, "sedan"), "w")
    for wp in ([(122, 122), (144, 106), (188, 105), (208, 120)],):
        s += poly(wp, "bg")
    s += path("M98 154 a18 18 0 0 1 36 0", "bg") + path("M205 154 a18 18 0 0 1 36 0", "bg")
    r1, (tx, ty) = robot(32, 186, 1.0, -70, 70)
    r2, (ux, uy) = robot(294, 186, 1.0, -112, -70)
    s += r1 + r2 + sparks(tx + 6, ty, 11) + sparks(ux - 4, uy, 11)
    return s


@part("plant.paint")
def _():
    s = shadow(170, 180, 120)
    s += car(70, 170, 1.0, "w", "sedan", wheels=False)
    r, (tx, ty) = robot(40, 186, 1.0, -84, 50)
    s += r
    s += path("M%s %s l10 -4 l0 12 z" % (n(tx), n(ty - 4)), "t")
    s += spray_cone(tx + 10, ty + 2, 10, 40, 48) + drops(tx + 12, ty + 2, 5, 34, 44, 10)
    return s


@part("plant.assembly")
def _():
    s = rect(8, 176, 304, 10, "m2")
    for x in range(14, 310, 18):
        s += line(x, 176, x, 186, "o thin")
    s += car(60, 176, 1.0, "w", "sedan")
    s += path("M24 190 l40 0", "a") + head(64, 190, 0)
    s += rect(262, 116, 14, 30, "m2", 3) + rect(266, 146, 6, 18, "m3")
    return s


@part("plant.inspection")
def _():
    s = rect(20, 168, 280, 16, "m2")
    s += car(62, 162, 1.0, "w", "sedan")
    for x in (97, 205):
        s += circ(x - 12, 168, 9, "m") + circ(x + 12, 168, 9, "m")
    s += circ(272, 44, 20, "t") + path("M262 44 l7 7 l13 -14", "a")
    return s


# ---------------------------------------------------------------- body
@part("body.hotstamp")
def _():
    s = shadow(160, 184, 60)
    s += path("M132 18 L188 18 L196 44 L192 146 L210 178 L110 178 L128 146 L124 44Z", "w3")
    s += path("M140 24 L180 24 L186 44 L183 146 L196 170 L124 170 L137 146 L134 44Z", "w2")
    s += path("M146 28 L174 28 L178 46 L175 144 L184 164 L136 164 L145 144 L142 46Z", "w")
    for y in (54, 86, 118):
        s += ell(160, y, 5, 7, "bg")
    s += ell(160, 152, 9, 5, "bg")
    return s


@part("body.hitenmember")
def _():
    s = shadow(170, 170, 140)
    s += poly([(34, 136), (300, 102), (304, 110), (38, 146)], "w3")
    s += poly([(56, 104), (286, 76), (292, 106), (58, 138)], "w2")
    s += poly([(38, 92), (262, 66), (286, 76), (56, 104)], "w")
    for i in range(5):
        x = 80 + i * 44
        y = 94 - i * 5.2
        s += ell(x, y, 7, 3.4, "bg")
    for i in range(4):
        x = 90 + i * 50
        s += ell(x, 125 - i * 6, 4, 4, "bg")
    return s


@part("body.alhood")
def _():
    s = shadow(160, 182, 136)
    s += path("M58 70 Q160 50 262 70 L296 158 Q160 176 24 158Z", "w2")
    s += path("M58 62 Q160 42 262 62 L296 150 Q160 168 24 150Z", "w")
    s += path("M84 76 Q160 62 236 76 L262 140 Q160 154 58 140Z", "o thin dash")
    s += path("M112 64 L96 146 M208 64 L224 146", "o thin")
    return s


@part("body.gigacast")
def _():
    s = shadow(160, 184, 140)
    outer = "M44 62 L276 62 L302 92 L302 150 L262 174 L58 174 L18 150 L18 92Z"
    s += path("M44 70 L276 70 L302 100 L302 158 L262 182 L58 182 L18 158 L18 100Z", "w3")
    s += path(outer, "w")
    xs = [44, 88, 132, 176, 220, 264]
    for i in range(len(xs) - 1):
        s += line(xs[i] + 10, 70, xs[i + 1] - 2, 166, "o thin") + line(xs[i + 1] - 2, 70, xs[i] + 10, 166, "o thin")
    s += line(26, 118, 296, 118, "o thin")
    for x, y in ((40, 96), (280, 96), (40, 150), (280, 150), (160, 90), (160, 148)):
        s += circ(x, y, 8, "w2") + circ(x, y, 3.2, "bg")
    return s


@part("body.fueltank")
def _():
    s = shadow(160, 180, 130)
    s += path("M34 96 Q36 64 90 62 L230 60 Q288 62 290 98 L290 150 Q288 168 256 168 L200 168 Q182 142 160 142 Q138 142 120 168 L66 168 Q34 168 34 146Z", "w2")
    s += path("M34 96 Q36 64 90 62 L230 60 Q288 62 290 98 Q280 90 230 90 L90 92 Q44 92 34 96Z", "w")
    s += vcyl(210, 70, 10, 22, 7, "m", "m2") + vcyl(96, 74, 8, 10, 4, "m", "m2")
    s += path("M232 68 q20 -26 50 -24", "cable")
    return s


# ---------------------------------------------------------------- engine
@part("engine.block")
def _():
    s = shadow(170, 184, 130)
    s += path("M60 150 L60 172 L230 172 L230 150", "w3")
    s += box(60, 78, 170, 76, 62, "w2", "w", "w3")
    for i in range(4):
        cx = 60 + 38 * 0.62 / 1 + 24 + i * 38
        cx = 92 + i * 38
        s += ell(cx + 19, 62, 16, 9, "m2") + ell(cx + 19, 62, 12.5, 6.8, "bg")
    for i in range(5):
        s += path("M%s 154 a12 10 0 0 1 24 0" % n(70 + i * 36), "bg")
    s += circ(92, 108, 11, "w2") + circ(92, 108, 5, "bg")
    for x in (120, 150, 180, 210):
        s += line(x, 84, x, 150, "o thin")
    return s


@part("engine.head")
def _():
    s = shadow(170, 178, 130)
    s += box(52, 104, 190, 50, 64, "w2", "w", "w3")
    for i in range(4):
        x = 76 + i * 42
        s += rect(x, 118, 26, 20, "bg", 6)
    for i in range(5):
        bx = 90 + i * 36
        s += poly([(bx, 88), (bx + 18, 88), (bx + 26, 82), (bx + 8, 82)], "w") + poly([(bx + 18, 88), (bx + 26, 82), (bx + 26, 76), (bx + 18, 82)], "w3")
        s += poly([(bx, 88), (bx + 18, 88), (bx + 18, 82), (bx, 82)], "w2")
    for i in range(4):
        s += ell(108 + i * 36 + 12, 80, 4, 2.4, "bg")
    return s


@part("engine.crank")
def _():
    s = shadow(160, 176, 150)
    cy = 104
    s += shaft(14, cy, [(18, 7), (14, 10)], "w", "w2")
    x = 46
    pins = [1, -1, -1, 1]
    for i in range(4):
        s += shaft(x, cy, [(14, 11)], "w", "w2")       # journal
        x += 14
        off = 26 * pins[i]
        s += rect(x, cy - 30 - (0 if off > 0 else 6), 9, 66, "w2", 4) if False else ""
        # web 1 (counterweight opposite pin)
        s += path("M%s %s l9 0 l0 %s q-4 %s -9 0Z" % (n(x), n(cy + off), n(-off - 44 * pins[i]), n(-10 * pins[i])), "w3")
        s += shaft(x + 9, cy + off, [(16, 10)], "w", "w2")  # pin
        s += path("M%s %s l9 0 l0 %s q-4 %s -9 0Z" % (n(x + 25), n(cy + off), n(-off - 44 * pins[i]), n(-10 * pins[i])), "w3")
        x += 34
    s += shaft(x, cy, [(14, 11), (8, 16)], "w", "w2")
    s += ell(x + 30, cy, 12, 40, "w3") + ell(x + 26, cy, 12, 40, "w") + ell(x + 26, cy, 4, 10, "bg")
    return s


@part("engine.cam")
def _():
    s = shadow(160, 170, 150)
    cy = 104
    s += shaft(20, cy, [(30, 12), (250, 7)], "w", "w2")
    for i in range(8):
        x = 70 + i * 26 + (8 if i % 2 else 0)
        th = math.radians((i * 90 + 30) % 360)
        for dx, c in ((5, "w3"), (0, "w")):
            ps = []
            for k in range(36):
                ph = 2 * math.pi * k / 36
                r = 13 + 9 * max(0.0, math.cos(ph - th)) ** 3
                ps.append((x + dx + r * math.cos(ph) * 0.34, cy + r * math.sin(ph)))
            s += poly(ps, c)
    s += ell(270, cy, 2.4, 7, "w2")
    return s


@part("engine.conrod")
def _():
    s = shadow(160, 186, 70)
    for dx, dy, c in ((8, -6, "w3"), (0, 0, "w")):
        s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(146 + dx), n(52 + dy), n(174 + dx), n(52 + dy), n(186 + dx), n(116 + dy), n(134 + dx), n(116 + dy)), c)
        s += circ(160 + dx, 42 + dy, 20, c)
        s += circ(160 + dx, 136 + dy, 42, c)
    s += path("M152 62 L168 62 L176 108 L144 108Z", "w2")
    s += circ(160, 42, 10, "bg") + circ(160, 136, 27, "bg")
    s += line(114, 136, 206, 136, "o")
    s += rect(112, 132, 12, 18, "m2", 2) + rect(196, 132, 12, 18, "m2", 2)
    return s


@part("engine.piston")
def _():
    s = shadow(160, 176, 70)
    s += vcyl(160, 42, 120, 58, 16, "w", "w2")
    for y in (60, 70, 80):
        s += path("M102 %s A58 16 0 0 0 218 %s" % (y, y), "o")
    s += path("M102 118 L102 162 A58 16 0 0 0 218 162 L218 118", "w")
    s += path("M116 124 L116 160 A44 10 0 0 0 204 160 L204 124 A44 10 0 0 1 116 124Z", "w2")
    s += circ(160, 120, 16, "w3") + circ(160, 120, 9, "bg")
    s += ell(140, 42, 12, 4, "w3") + ell(180, 42, 12, 4, "w3")
    return s


@part("engine.valve")
def _():
    s = shadow(160, 172, 140)
    cy = 104
    s += shaft(22, cy, [(8, 5), (4, 4), (6, 5), (196, 5)], "w", "w2")
    s += path("M236 99 Q256 99 268 70 L276 70 L276 138 L268 138 Q256 109 236 109Z", "w")
    s += ell(276, cy, 9, 34, "w2") + ell(276, cy, 5, 26, "w")
    s += line(28, 96, 28, 112, "o thin") + line(36, 96, 36, 112, "o thin")
    return s


@part("engine.turbo")
def _():
    s = shadow(160, 182, 140)
    # compressor housing (left)
    s += path("M40 104 A52 56 0 1 1 92 160 L92 176 L66 176 L66 156 A52 56 0 0 1 40 104Z", "w")
    s += ell(78, 104, 20, 30, "bg")
    for k in range(6):
        a = math.radians(k * 60 + 15)
        s += path("M78 104 q%s %s %s %s" % (n(8 * math.cos(a) - 6 * math.sin(a)), n(10 * math.sin(a) + 6 * math.cos(a)), n(18 * math.cos(a)), n(26 * math.sin(a))), "o thin")
    s += circ(78, 104, 4, "w3")
    # center housing
    s += shaft(126, 104, [(50, 20)], "w2", "w3")
    # turbine housing (right)
    s += path("M190 104 A48 52 0 1 1 238 156 L240 176 L214 176 L214 150 A48 52 0 0 1 190 104Z", "w3")
    s += ell(238, 104, 30, 36, "w2") + ell(238, 104, 16, 20, "bg")
    s += rect(262, 60, 32, 22, "w2", 3)
    return s


@part("engine.injector")
def _():
    s = shadow(160, 160, 140)
    cy = 104
    s += box(18, 80, 34, 46, 14, "m2", "m", "m3")
    s += shaft(52, cy, [(26, 18), (60, 15), (10, 17), (80, 11), (40, 6)], "w", "w2")
    s += spray_cone(270, cy, 0, 30, 40) + drops(270, cy, 5, 30, 36, 0)
    s += rect(98, 88, 24, 32, "m3", 3)
    return s


@part("engine.engineassy")
def _():
    s = shadow(170, 186, 136)
    s += box(64, 118, 168, 54, 58, "w2", "w", "w3")                # block
    s += box(66, 90, 164, 30, 58, "w2", "w", "w3")                 # head
    s += box(74, 68, 150, 18, 52, "m2", "m", "m3")                 # cam cover
    s += path("M70 172 L78 184 L226 184 L234 172Z", "m2")          # oil pan
    s += circ(52, 130, 20, "m2") + circ(52, 130, 8, "m3") + circ(46, 96, 12, "m2")
    s += path("M52 110 L46 84 M40 96 L34 128 L52 150", "belt")
    return s


# ---------------------------------------------------------------- drivetrain
@part("drivetrain.gear")
def _():
    import il_gear as GE
    s = shadow(160, 176, 100, 12)
    cam = GE.Cam(160, 100, 0, 44, 0.78)
    s += GE.gear3(cam, (0, 0, -18), (0, 0, 1), 32, 96, 38, "w", helix=20, spline_bore=(18, 29, 24.5))
    cx, cy = cam.xy((0, 0, 20))
    s += '<ellipse class="thin o" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(cx), n(cy), n(60 * 0.78), n(60 * 0.78 * cam.se))
    return s


@part("drivetrain.shaft")
def _():
    import il_gear as GE
    s = shadow(160, 170, 150, 10)
    cam = GE.Cam(160, 104, -20, 20, 1.0)
    A = (1, 0, 0)
    x = -150
    segs = [(40, 11, "spl"), (26, 15, None), (14, 20, None), (36, 0, "gear"), (46, 18, None), (12, 22, None), (56, 14, None), (26, 10, None)]
    out = ""
    for L, r, kind in segs:
        if kind == "gear":
            out += GE.gear3(cam, (x, 0, 0), A, 17, 30, L, "w", helix=24)
        elif kind == "spl":
            out += GE.prism(cam, (x, 0, 0), A, GE.spline_outline(18, r, r - 2.2), L, "w")
        else:
            out += GE.cyl(cam, (x, 0, 0), A, r, L, "w")
        x += L
    return s + out


@part("drivetrain.tmcase")
def _():
    s = shadow(170, 184, 130)
    s += path("M70 34 L250 60 Q284 70 284 104 L284 136 Q282 170 250 170 L70 176Z", "w2")
    s += ell(70, 105, 34, 72, "w3") + ell(66, 105, 34, 72, "w") + ell(66, 105, 22, 52, "bg")
    for k in range(8):
        a = math.radians(k * 45 + 20)
        s += circ(66 + 28 * math.cos(a), 105 + 62 * math.sin(a), 3, "bg")
    for x, y in ((170, 92), (236, 104)):
        s += ell(x, y, 14, 18, "w") + ell(x, y, 7, 9, "bg")
    s += path("M120 52 L120 172 M200 64 L204 170", "o thin")
    return s


@part("drivetrain.valvebody")
def _():
    s = shadow(160, 180, 136)
    s += box(40, 128, 220, 30, 96, "w", "w2", "w3")
    dx, dy = 0.62, -0.5
    def P(u, v):  # u along width, v along depth
        return (40 + u + v * dx, 128 + v * dy)
    for v0 in (14, 36, 58, 80):
        ps = [P(14, v0), P(60, v0), P(60, v0 + 10), P(110, v0 + 10), P(110, v0 - 4), P(160, v0 - 4), P(160, v0 + 6), P(206, v0 + 6)]
        s += pline(ps, "chan")
    for i in range(6):
        s += circ(62 + i * 34, 143, 5.5, "bg")
    return s


@part("drivetrain.cvtpulley")
def _():
    s = shadow(160, 178, 130)
    cy = 104
    s += shaft(18, cy, [(274, 12)], "w", "w2")
    s += path("M70 %s L70 %s L150 %s L150 %sZ" % (n(cy - 70), n(cy + 70), n(cy + 16), n(cy - 16)), "w2")
    s += ell(70, cy, 20, 70, "w")
    s += path("M250 %s L250 %s L170 %s L170 %sZ" % (n(cy - 70), n(cy + 70), n(cy + 16), n(cy - 16)), "w3")
    s += ell(250, cy, 20, 70, "w2") + ell(250, cy, 8, 22, "w")
    s += path("M142 %s L178 %s L178 %s L142 %sZ" % (n(cy - 50), n(cy - 50), n(cy - 38), n(cy - 38)), "m3")
    return s


@part("drivetrain.cvtbelt")
def _():
    s = shadow(160, 184, 140)
    s += rect(30, 50, 260, 116, "w2", 58)
    s += rect(48, 66, 224, 84, "bg", 42)
    for i in range(0, 64):
        t = i / 64.0
        per = 2 * (224 - 84) + math.pi * 84
        d = t * per
        # walk the stadium centreline (radius 50) and draw a radial tick
        L = 260 - 116
        r0, r1 = 42, 58
        if d < L:
            x, y, a = 88 + d, 108 - 50, -math.pi / 2
        elif d < L + math.pi * 50:
            a = -math.pi / 2 + (d - L) / 50
            x, y = 232 + 50 * math.cos(a), 108 + 50 * math.sin(a)
        elif d < 2 * L + math.pi * 50:
            x, y, a = 232 - (d - L - math.pi * 50), 158, math.pi / 2
        else:
            a = math.pi / 2 + (d - 2 * L - math.pi * 50) / 50
            x, y = 88 + 50 * math.cos(a), 108 + 50 * math.sin(a)
        s += line(x - 8 * math.cos(a), y - 8 * math.sin(a), x + 8 * math.cos(a), y + 8 * math.sin(a), "o thin")
    s += rect(30, 50, 260, 116, "o", 58)
    return s


@part("drivetrain.torqueconv")
def _():
    s = shadow(160, 186, 110)
    s += ell(176, 104, 70, 82, "w3")
    s += path("M160 22 L176 22 L176 186 L160 186Z", "w3")
    s += ell(160, 104, 70, 82, "w") + ell(160, 104, 52, 62, "w2") + ell(160, 104, 30, 36, "w")
    s += ell(160, 104, 14, 16, "w3") + ell(160, 104, 7, 8, "bg")
    for k in range(6):
        a = math.radians(k * 60 + 30)
        s += circ(160 + 62 * math.cos(a), 104 + 73 * math.sin(a), 4, "bg")
    return s


@part("drivetrain.hypoid")
def _():
    import il_gscene as GS
    return shadow(176, 176, 120, 12) + GS.sc_hypoid_pair(190, 106, 0.62, lab=False)


@part("drivetrain.diffcase")
def _():
    s = shadow(160, 184, 110)
    s += shaft(20, 104, [(50, 20)], "w", "w2")
    s += ell(96, 104, 16, 70, "w3") + ell(92, 104, 16, 70, "w")
    for k in range(10):
        a = 2 * math.pi * k / 10
        s += circ(92 + 11 * math.cos(a), 104 + 58 * math.sin(a), 2.6, "bg")
    s += circ(170, 104, 62, "w")
    s += path("M150 70 Q176 60 196 78 L200 124 Q176 142 150 132Z", "bg")
    s += shaft(232, 104, [(56, 20)], "w", "w2")
    s += circ(168, 104, 10, "w3")
    return s


@part("drivetrain.cvj")
def _():
    s = shadow(160, 172, 150)
    cy = 104
    s += path("M16 %s Q16 %s 48 %s L48 %s Q16 %s 16 %sZ" % (n(cy - 30), n(cy - 40), n(cy - 40), n(cy + 40), n(cy + 40), n(cy + 30)), "w")
    s += shaft(4, cy, [(12, 12)], "w", "w2")
    bel = "M48 %s " % n(cy - 34)
    for i in range(5):
        x = 48 + i * 11
        r = 34 - i * 5
        bel += "L%s %s L%s %s " % (n(x + 5.5), n(cy - r - 4), n(x + 11), n(cy - r + 2))
    bel += "L103 %s L103 %s " % (n(cy - 9), n(cy + 9))
    for i in range(4, -1, -1):
        x = 48 + i * 11
        r = 34 - i * 5
        bel += "L%s %s L%s %s " % (n(x + 11), n(cy + r - 2), n(x + 5.5), n(cy + r + 4))
    bel += "L48 %sZ" % n(cy + 34)
    s += path(bel, "rb")
    s += shaft(100, cy, [(110, 7)], "w", "w2")
    bel2 = bel.replace("", "")
    s += "<g transform=\"translate(320 0) scale(-1 1)\">" + path(bel, "rb") + "</g>"
    s += path("M304 %s L304 %s L272 %s L272 %sZ" % (n(cy - 30), n(cy + 30), n(cy + 38), n(cy - 38)), "w")
    s += ell(304, cy, 8, 30, "w2") + ell(304, cy, 4, 12, "w")
    return s


@part("drivetrain.tmassy")
def _():
    s = PARTS["drivetrain.tmcase"]()
    s += box(150, 160, 110, 14, 30, "m2", "m", "m3")
    s += box(220, 40, 30, 20, 16, "m2", "m", "m3") + path("M248 40 q20 -24 40 -20", "cable")
    return s


# ---------------------------------------------------------------- chassis
@part("chassis.lowerarm")
def _():
    s = shadow(160, 180, 130)
    body = "M60 84 L96 70 L268 104 L268 120 L112 156 L84 150 L78 118Z"
    s += path("M60 92 L96 78 L268 112 L268 128 L112 164 L84 158 L78 126Z", "w3")
    s += path(body, "w")
    s += path("M92 90 L230 112 L112 138Z", "w2")
    for x, y in ((62, 90), (98, 158)):
        s += ell(x, y, 22, 17, "w2") + ell(x, y, 15, 11, "rb") + ell(x, y, 6, 5, "m")
    s += vcyl(266, 100, 22, 16, 7, "w2", "w") + vcyl(266, 86, 14, 6, 3, "m", "m2")
    return s


@part("chassis.knuckle")
def _():
    s = shadow(160, 184, 90)
    body = "M140 22 L178 22 L186 64 Q222 72 226 104 L276 112 L276 132 L222 132 Q210 148 186 150 L180 176 L142 176 L138 150 Q104 142 100 104 Q104 72 136 62Z"
    s += "<g transform=\"translate(7 -5)\">" + path(body, "w3") + "</g>" + path(body, "w")
    s += circ(162, 104, 36, "w2") + circ(162, 104, 22, "bg")
    for x, y in ((152, 36), (170, 36), (160, 164), (264, 122)):
        s += circ(x, y, 5, "bg")
    return s


@part("chassis.alarm")
def _():
    s = shadow(160, 176, 136)
    body = "M40 110 Q60 76 110 70 Q170 62 220 84 Q256 98 282 94 L286 120 Q250 124 214 108 Q168 90 112 96 Q70 102 58 128Z"
    s += "<g transform=\"translate(6 -5)\">" + path(body, "w3") + "</g>" + path(body, "w")
    s += path("M70 104 Q110 82 170 80 Q214 84 250 104", "o thin")
    s += ell(46, 118, 22, 20, "w2") + ell(46, 118, 14, 13, "rb") + ell(46, 118, 5, 5, "m")
    s += ell(286, 106, 18, 18, "w2") + ell(286, 106, 11, 11, "rb") + ell(286, 106, 4, 4, "m")
    return s


@part("chassis.spring")
def _():
    s = shadow(160, 170, 130)
    s += coil(44, 276, 104, 50, 6)
    s += ell(44, 104, 8, 50, "o thin")
    return s


@part("chassis.damper")
def _():
    s = shadow(160, 172, 150)
    cy = 104
    s += shaft(20, cy, [(12, 10)], "w", "w2")
    s += circ(26, cy, 14, "w") + circ(26, cy, 6, "bg")
    s += shaft(40, cy, [(150, 22), (8, 20)], "w", "w2")
    s += ell(150, cy, 12, 46, "w3") + ell(146, cy, 12, 46, "w")
    s += shaft(198, cy, [(70, 7)], "cr", "w2")
    s += shaft(268, cy, [(16, 15)], "rb", "rb")
    s += shaft(284, cy, [(20, 6)], "w", "w2")
    return s


@part("chassis.stabilizer")
def _():
    s = shadow(160, 176, 136)
    d = "M36 166 L64 80 Q72 58 100 60 L220 60 Q248 58 256 80 L284 166"
    s += path(d, "tube1") + path(d, "tube2")
    for x in (30, 290):
        s += circ(x, 170, 11, "w") + circ(x, 170, 4.5, "bg")
    s += rect(114, 52, 20, 16, "rb", 3) + rect(186, 52, 20, 16, "rb", 3)
    return s


@part("chassis.subframe")
def _():
    s = shadow(160, 184, 140)
    outer = "M40 70 L280 70 L300 150 L20 150Z M84 86 L236 86 L250 136 L70 136Z"
    s += "<g transform=\"translate(0 10)\">" + path(outer, "w3", ' fill-rule="evenodd"') + "</g>"
    s += path(outer, "w", ' fill-rule="evenodd"')
    for x, y in ((40, 76), (280, 76), (30, 146), (290, 146)):
        s += ell(x, y, 13, 9, "rb") + ell(x, y, 5, 3.5, "m")
    s += rect(130, 96, 60, 10, "w2", 2)
    return s


@part("chassis.hubbearing")
def _():
    s = shadow(160, 184, 110)
    s += shaft(40, 104, [(60, 40)], "w3", "w2")
    s += path("M112 38 L140 30 L140 178 L112 170Z", "w3")
    s += ell(140, 104, 34, 76, "w2")
    s += shaft(140, 104, [(20, 72)], "w", "w2")
    s += ell(160, 104, 22, 72, "w")
    s += shaft(160, 104, [(30, 32)], "w", "w2")
    for k in range(5):
        a = math.radians(k * 72 - 90)
        x, y = 160 + 16 * math.cos(a), 104 + 52 * math.sin(a)
        s += shaft(x, y, [(34, 5)], "m", "m2")
    return s


@part("chassis.disc")
def _():
    s = shadow(160, 186, 110)
    cx, cy = 150, 104
    s += ell(cx + 18, cy, 44, 84, "w3")
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(cx), n(cy - 84), n(cx + 18), n(cy - 84), n(cx + 18), n(cy + 84), n(cx), n(cy + 84)), "w3")
    for k in range(18):
        a = math.radians(-90 + k * 10)
        y = cy + 84 * math.sin(a)
        s += line(cx + 44 * math.cos(a) + 4, y, cx + 44 * math.cos(a) + 14, y, "o thin")
    s += ell(cx, cy, 44, 84, "w")
    s += ell(cx, cy, 24, 46, "w2")
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(cx - 2), n(cy - 44), n(cx - 18), n(cy - 40), n(cx - 18), n(cy + 40), n(cx - 2), n(cy + 44)), "w3")
    s += ell(cx - 18, cy, 20, 40, "w") + ell(cx - 18, cy, 9, 18, "bg")
    for k in range(5):
        a = math.radians(k * 72 - 90)
        s += ell(cx - 18 + 14 * math.cos(a), cy + 29 * math.sin(a), 2.4, 4.4, "bg")
    return s


@part("chassis.caliper")
def _():
    s = shadow(160, 184, 120)
    s += path("M40 180 A150 150 0 0 1 280 180 L250 180 A120 120 0 0 0 70 180Z", "w3")
    body = "M70 94 Q84 50 160 44 Q236 50 250 94 L262 136 Q240 124 222 128 L210 104 Q160 92 110 104 L98 128 Q80 124 58 136Z"
    s += "<g transform=\"translate(6 -6)\">" + path(body, "w3") + "</g>" + path(body, "w")
    s += ell(122, 76, 20, 12, "w2") + ell(198, 76, 20, 12, "w2")
    s += vcyl(160, 52, 10, 5, 2.4, "m", "m2")
    for x in (64, 256):
        s += circ(x, 132, 8, "w2") + circ(x, 132, 3.5, "bg")
    return s


@part("chassis.pad")
def _():
    s = shadow(160, 176, 130)
    for off in (0, 1):
        dx, dy = off * 30, off * -26
        plate = "M%s %s Q%s %s %s %s Q%s %s %s %s L%s %s Q%s %s %s %s Q%s %s %s %sZ" % tuple(n(v) for v in (
            40 + dx, 110 + dy, 50 + dx, 76 + dy, 100 + dx, 70 + dy, 160 + dx, 64 + dy, 220 + dx, 70 + dy,
            250 + dx, 110 + dy, 240 + dx, 144 + dy, 160 + dx, 150 + dy, 60 + dx, 144 + dy, 40 + dx, 110 + dy))
        s += path(plate, "m3" if off == 0 else "m2")
        if off == 1:
            fr = "M%s %s Q%s %s %s %s L%s %s Q%s %s %s %sZ" % tuple(n(v) for v in (
                84 + dx, 86 + dy, 160 + dx, 74 + dy, 236 + dx, 86 + dy, 228 + dx, 128 + dy, 160 + dx, 138 + dy, 92 + dx, 128 + dy))
            s += path(fr, "w2") + line(160 + dx, 76 + dy, 160 + dx, 137 + dy, "bgline")
    s += path("M84 100 Q160 88 236 100 L228 132 Q160 142 92 132Z", "w")
    return s


@part("chassis.hu")
def _():
    s = shadow(160, 184, 120)
    s += box(80, 96, 140, 80, 70, "w2", "w", "w3")
    for i in range(4):
        for j in range(2):
            x = 104 + i * 30 + j * 22
            y = 88 - j * 18
            s += vcyl(x, y - 16, 16, 9, 3.5, "m", "m2")
    s += shaft(18, 140, [(62, 26)], "m", "m2")
    for i in range(4):
        s += circ(110 + i * 28, 136, 6, "bg")
    return s


@part("chassis.eps")
def _():
    s = shadow(160, 168, 150)
    cy = 108
    s += shaft(40, cy, [(236, 14)], "w", "w2")
    for side in (0, 1):
        bx = 22 if side == 0 else 276
        s += shaft(bx, cy, [(22, 11)], "rb", "rb")
    s += shaft(2, cy, [(20, 5)], "w", "w2") + shaft(298, cy, [(20, 5)], "w", "w2")
    s += shaft(150, cy, [(70, 30)], "w2", "w3")
    s += box(170, 50, 46, 30, 24, "m2", "m", "m3")
    s += shaft(96, cy - 30, [(20, 10)], "w", "w2")
    s += path("M100 80 L90 40", "tube2")
    return s


@part("chassis.balljoint")
def _():
    s = shadow(160, 172, 140)
    cy = 120
    s += shaft(20, cy, [(170, 9)], "w", "w2")
    for x in range(26, 90, 5):
        s += line(x, cy - 9, x + 3, cy + 9, "o thin")
    s += circ(226, cy, 34, "w")
    s += path("M204 96 Q226 78 248 96 L240 84 Q226 76 212 84Z", "rb")
    s += path("M216 88 L220 30 L232 30 L236 88Z", "w2")
    s += shaft(214, 30, [(24, 6)], "w", "w2")
    return s


# ---------------------------------------------------------------- ev
@part("ev.cell")
def _():
    s = shadow(170, 184, 90)
    s += box(96, 66, 118, 112, 40, "w2", "w", "w3")
    s += box(112, 50, 22, 10, 12, "cu", "cu", "cu") + box(176, 50, 22, 10, 12, "m", "m", "m2")
    s += ell(163, 56, 8, 3.5, "bg")
    s += rect(116, 100, 78, 34, "w2", 3)
    return s


@part("ev.pack")
def _():
    s = shadow(160, 186, 150)
    s += box(20, 136, 240, 40, 104, "m2", "w2", "w3")
    dx, dy = 0.62, -0.5
    for r in (1, 0):
        for c in range(4):
            u = 18 + c * 56
            v = 18 + r * 44
            x = 20 + u + v * dx
            y = 136 + v * dy - 16
            s += box(x, y, 46, 16, 32, "w", "w2", "w3")
    return s


@part("ev.stator")
def _():
    s = shadow(160, 186, 100)
    cx, cy = 160, 110
    s += ell(cx + 16, cy - 10, 96, 70, "w3")
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(cx), n(cy - 70), n(cx + 16), n(cy - 80), n(cx + 16), n(cy + 60), n(cx), n(cy + 70)), "w3")
    s += ell(cx, cy, 96, 70, "w")
    for k in range(36):
        a = 2 * math.pi * k / 36
        s += line(cx + 60 * math.cos(a), cy + 44 * math.sin(a), cx + 88 * math.cos(a), cy + 64 * math.sin(a), "o thin")
    for k in range(24):
        a = 2 * math.pi * k / 24
        x, y = cx + 72 * math.cos(a), cy + 52 * math.sin(a)
        s += path("M%s %s q4 -16 10 0" % (n(x - 5), n(y)), "cuwire")
    s += ell(cx, cy, 56, 40, "bg")
    return s


@part("ev.rotor")
def _():
    s = shadow(160, 176, 150)
    cy = 104
    s += shaft(12, cy, [(40, 10), (10, 14)], "w", "w2")
    s += shaft(62, cy, [(150, 56)], "w", "w2")
    for x in range(70, 212, 8):
        s += path("M%s %s A18 56 0 0 1 %s %s" % (n(x), n(cy - 56), n(x), n(cy + 56)), "o thin")
    for k in range(8):
        a = 2 * math.pi * k / 8
        x, y = 212 + 11 * math.cos(a), cy + 38 * math.sin(a)
        s += ell(x, y, 3, 8, "bg")
    s += ell(212, cy, 5, 14, "w2")
    s += shaft(212, cy, [(10, 14), (70, 10)], "w", "w2")
    return s


@part("ev.eaxlecase")
def _():
    s = shadow(160, 186, 140)
    s += shaft(24, 112, [(150, 62)], "w", "w2")
    s += ell(174, 112, 20, 62, "bg")
    s += path("M180 50 L270 58 Q296 62 296 90 L296 150 Q294 172 268 172 L180 174Z", "w2")
    for x, y in ((236, 92), (262, 140)):
        s += ell(x, y, 14, 18, "w") + ell(x, y, 7, 9, "bg")
    for x in (60, 100, 140):
        s += line(x, 52, x, 172, "o thin")
    return s


@part("ev.powermodule")
def _():
    s = shadow(160, 176, 130)
    s += box(52, 112, 200, 34, 90, "w2", "w", "w3")
    for i in range(3):
        x = 88 + i * 50
        s += box(x, 76, 22, 22, 14, "cu", "cu", "cu")
    for x in (220, 238):
        for j in range(3):
            s += rect(x + j * 4, 70 - j * 3, 2.4, 14, "m3")
    for x, y in ((66, 104), (252, 60)):
        s += ell(x + 12, y, 6, 3, "bg")
    return s


@part("ev.inverter")
def _():
    s = shadow(160, 184, 130)
    s += box(48, 96, 196, 76, 76, "w2", "w", "w3")
    for i in range(3):
        s += shaft(8, 116 + i * 20, [(40, 7)], "m", "m2")
    s += vcyl(120, 42, 14, 14, 6, "m", "m2") + vcyl(160, 34, 14, 14, 6, "m", "m2")
    s += shaft(244, 150, [(30, 7)], "m", "m2") + shaft(262, 120, [(30, 7)], "m", "m2")
    return s


@part("ev.reducer")
def _():
    import il_gear as GE
    s = shadow(160, 178, 130, 12)
    cam = GE.Cam(150, 104, 0, 38, 0.72)
    z1, z2, m = 44, 17, 4.2
    r1, r2 = z1 * m / 2, z2 * m / 2
    beta = math.radians(-8)
    C = ((r1 + r2) * math.cos(beta), (r1 + r2) * math.sin(beta))
    s += GE.gear3(cam, (0, 0, -16), (0, 0, 1), z1, r1, 32, "w", helix=22, bore=30, phase=beta + math.pi / z1)
    s += GE.cyl(cam, (0, 0, 16), (0, 0, 1), 30, 4, "w")
    s += GE.gear3(cam, (C[0], C[1], -22), (0, 0, 1), z2, r2, 44, "w", helix=-22, phase=beta + math.pi)
    s += GE.cyl(cam, (C[0], C[1], 22), (0, 0, 1), 14, 30, "w")
    return s


@part("ev.eaxleassy")
def _():
    s = shadow(160, 188, 150)
    s += shaft(20, 124, [(150, 56)], "w", "w2")
    s += path("M170 64 L262 72 Q288 76 288 104 L288 160 Q286 180 262 180 L170 180Z", "w2")
    s += shaft(288, 150, [(22, 14)], "m", "m2")
    s += box(40, 52, 120, 20, 40, "m2", "m", "m3")
    s += shaft(2, 124, [(18, 16)], "m", "m2")
    return s


# ---------------------------------------------------------------- electrical
@part("electrical.harness")
def _():
    s = ""
    trunk = "M20 120 C80 116 120 90 170 96 S260 130 300 118"
    s += path(trunk, "cable3")
    for d in ("M110 96 C116 70 110 52 96 40", "M170 96 C180 126 176 150 186 170", "M232 116 C240 90 256 70 268 54", "M70 114 C66 140 56 156 42 170"):
        s += path(d, "cable")
    for x, y, a in ((20, 120, 0), (300, 118, 0), (96, 40, 0), (186, 170, 0), (268, 54, 0), (42, 170, 0)):
        s += rect(x - 10, y - 8, 20, 16, "w", 3)
    for x, y in ((140, 92), (206, 104), (80, 114)):
        s += rect(x - 6, y - 7, 12, 14, "m2", 2)
    return s


@part("electrical.ecu")
def _():
    s = shadow(160, 180, 120)
    s += box(60, 90, 180, 80, 70, "w2", "w", "w3")
    for i in range(9):
        x = 60 + 20 + i * 16
        s += line(x + 43.4 * 0.2, 90 - 35 * 0.2, x + 43.4 * 0.9, 90 - 35 * 0.9, "o thin")
    s += rect(90, 116, 110, 34, "m3", 4)
    for i in range(10):
        s += rect(98 + i * 10, 126, 6, 14, "bg", 1)
    for x in (48, 244):
        s += rect(x, 150, 14, 10, "w2", 2)
    return s


@part("electrical.headlamp")
def _():
    s = shadow(160, 180, 130)
    s += path("M24 70 Q60 44 180 48 Q280 52 298 108 Q296 150 256 158 L60 150 Q20 138 24 70Z", "w3")
    s += path("M30 72 Q64 50 180 54 Q274 58 290 108 Q288 142 254 150 L62 144 Q28 134 30 72Z", "gl")
    s += circ(110, 100, 30, "m2") + circ(110, 100, 20, "gl2")
    s += circ(200, 104, 26, "m2") + circ(200, 104, 17, "gl2")
    s += path("M52 128 Q160 136 270 124", "led")
    return s


@part("electrical.adascam")
def _():
    s = shadow(160, 180, 110)
    s += path("M40 52 L280 36 L280 50 L40 66Z", "gl")
    s += box(96, 90, 130, 60, 60, "w2", "w", "w3")
    s += circ(160, 118, 22, "m3") + circ(160, 118, 13, "gl2") + circ(156, 114, 4, "o")
    s += path("M112 90 L120 56 M214 90 L220 50", "tube2")
    return s


@part("electrical.connector")
def _():
    s = shadow(160, 182, 110)
    s += box(70, 72, 160, 96, 60, "w2", "w", "w3")
    for r in range(3):
        for c in range(6):
            s += rect(88 + c * 22, 88 + r * 24, 14, 14, "bg", 2)
    for c in range(6):
        s += shaft(232, 96 + c * 12, [(40, 2.6)], "cu", "cu")
    s += rect(110, 60, 70, 8, "w2", 2)
    return s


# ---------------------------------------------------------------- interior
@part("interior.seat")
def _():
    s = shadow(160, 188, 120)
    s += rect(66, 170, 170, 8, "m2", 2) + rect(80, 160, 14, 12, "m") + rect(210, 160, 14, 12, "m")
    s += path("M70 148 Q66 124 96 120 L220 118 Q246 120 244 146 Q242 162 222 164 L90 166 Q70 164 70 148Z", "w")
    s += path("M200 124 Q196 60 214 30 Q224 18 240 24 Q258 30 256 58 L248 128 Q242 140 224 138Z", "w2")
    s += path("M218 22 Q220 4 240 6 Q260 10 258 24 L256 34 Q240 28 220 30Z", "w")
    s += line(236, 30, 234, 40, "m3") + line(248, 30, 246, 40, "m3")
    s += path("M96 130 Q160 124 214 128", "o thin dash")
    return s


@part("interior.instpanel")
def _():
    s = shadow(160, 182, 146)
    s += path("M14 96 Q30 60 110 56 L210 56 Q290 60 306 96 L306 124 Q300 152 262 158 L58 158 Q20 152 14 124Z", "w2")
    s += path("M14 96 Q30 60 110 56 L210 56 Q290 60 306 96 Q260 86 160 88 Q60 86 14 96Z", "w")
    s += path("M70 90 Q70 64 110 64 L150 64 Q164 66 164 92Z", "w3")
    s += rect(80, 74, 72, 16, "bg", 3)
    s += rect(176, 94, 60, 36, "bg", 4)
    for x in (30, 270):
        s += rect(x, 108, 24, 12, "m3", 3)
    return s


@part("interior.doortrim")
def _():
    s = shadow(160, 186, 130)
    s += path("M34 40 L270 30 Q292 30 292 60 L286 170 Q284 180 270 180 L56 182 Q38 180 36 164Z", "w2")
    s += path("M40 46 L268 38 Q284 38 284 60 L280 88 L44 96Z", "w")
    s += path("M120 110 L262 104 Q276 104 276 118 L274 126 Q272 134 260 134 L124 138 Q112 138 112 126Z", "w3")
    s += rect(210, 56, 40, 12, "m", 5)
    s += circ(90, 144, 22, "w3")
    for k in range(3):
        for j in range(3):
            s += circ(82 + k * 8, 136 + j * 8, 1.6, "bg")
    return s


@part("interior.airbag")
def _():
    s = shadow(160, 184, 120)
    s += box(70, 148, 120, 26, 40, "m2", "m", "m3")
    s += path("M90 150 Q60 120 70 80 Q82 30 160 26 Q250 26 268 76 Q282 124 240 150 Q200 164 160 150 Q126 162 90 150Z", "w")
    s += path("M112 60 Q160 44 222 62 M100 100 Q160 88 250 104", "o thin dash")
    s += circ(214, 104, 7, "w2") + circ(120, 76, 7, "w2")
    return s


@part("interior.seatbelt")
def _():
    s = shadow(160, 186, 130)
    s += box(34, 120, 50, 60, 22, "m2", "m", "m3")
    s += circ(59, 150, 12, "m3")
    web = "M60 124 L70 40 Q72 30 84 32 L260 110"
    s += path(web, "web")
    s += poly([(252, 104), (282, 118), (276, 132), (246, 118)], "m")
    s += rect(250, 136, 44, 22, "w3", 5) + rect(262, 142, 20, 8, "rb", 2)
    s += path("M84 32 L96 26 L100 38 L90 42Z", "m")
    return s


# ---------------------------------------------------------------- exterior
@part("exterior.bumper")
def _():
    s = shadow(160, 176, 146)
    s += path("M12 80 Q20 56 60 54 L260 54 Q300 56 308 80 L310 140 Q306 162 280 164 L40 164 Q14 162 10 140Z", "w2")
    s += path("M12 80 Q20 56 60 54 L260 54 Q300 56 308 80 Q290 72 160 72 Q30 72 12 80Z", "w")
    s += path("M92 104 Q96 94 110 94 L210 94 Q224 94 228 104 L232 140 L88 140Z", "bg")
    for x in range(98, 226, 12):
        s += line(x, 96, x - 4, 140, "o thin")
    s += rect(30, 116, 38, 18, "bg", 8) + rect(252, 116, 38, 18, "bg", 8)
    return s


@part("exterior.windshield")
def _():
    s = shadow(160, 184, 150)
    s += path("M64 34 Q160 24 256 34 Q284 104 304 170 Q160 184 16 170 Q36 104 64 34Z", "gl")
    s += path("M64 34 Q160 24 256 34 Q284 104 304 170 Q160 184 16 170 Q36 104 64 34Z", "frit")
    s += rect(146, 34, 28, 22, "m3", 3)
    s += path("M40 120 Q160 110 280 120", "o thin dash")
    return s


@part("exterior.sideglass")
def _():
    s = shadow(160, 180, 140)
    s += path("M26 160 L40 70 Q110 30 230 34 Q282 36 296 60 L294 160Z", "gl")
    s += path("M26 160 L40 70 Q110 30 230 34 Q282 36 296 60 L294 160Z", "o")
    s += path("M70 70 Q150 50 250 58", "o thin dash")
    return s


@part("exterior.weatherstrip")
def _():
    s = ""
    s += path("M40 60 L150 60 L150 160 L40 160 L40 140 L64 136 L64 150 L128 150 L128 70 L64 70 L64 84 L40 80Z", "rb")
    s += path("M72 76 L120 76 L120 144 L72 144", "zig")
    s += circ(214, 110, 52, "rb2") + circ(214, 110, 38, "bg")
    s += path("M150 90 Q164 88 166 92 L166 126 Q164 132 150 130Z", "rb")
    s += path("M40 148 L20 176 M40 74 L22 46", "rbline")
    return s


@part("exterior.grille")
def _():
    s = shadow(160, 176, 146)
    s += path("M20 60 Q24 44 60 44 L260 44 Q296 44 300 60 L288 150 Q284 164 260 164 L60 164 Q36 164 32 150Z", "cr")
    s += path("M40 64 L280 64 L270 146 L50 146Z", "bg")
    def clip(x1, y1, x2, y2, xl=52, xr=270):
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        if x2 < xl or x1 > xr:
            return ""
        k = (y2 - y1) / (x2 - x1)
        if x1 < xl:
            y1 += k * (xl - x1); x1 = xl
        if x2 > xr:
            y2 -= k * (x2 - xr); x2 = xr
        return line(x1, y1, x2, y2, "gridl")
    for i in range(-4, 16):
        x = 40 + i * 18
        s += clip(x, 64, x + 60, 146) + clip(x + 60, 64, x, 146)
    s += path("M40 64 L280 64 L270 146 L50 146Z", "o")
    s += circ(160, 104, 16, "cr")
    return s


# ---------------------------------------------------------------- wheel
@part("wheel.tire")
def _():
    s = shadow(160, 190, 110)
    cx, cy = 150, 104
    s += ell(cx + 40, cy, 66, 84, "rb")
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(cx), n(cy - 84), n(cx + 40), n(cy - 84), n(cx + 40), n(cy + 84), n(cx), n(cy + 84)), "rb")
    for k in range(16):
        a = math.radians(-80 + k * 10)
        y = cy + 84 * math.sin(a)
        x0 = cx + 66 * math.cos(a)
        s += line(x0 + 6, y, x0 + 34, y + 3, "rbline")
    s += ell(cx, cy, 66, 84, "rb2")
    s += ell(cx, cy, 42, 54, "m2") + ell(cx, cy, 34, 44, "bg")
    return s


@part("wheel.alwheel")
def _():
    s = shadow(160, 190, 90)
    cx, cy = 160, 100
    s += circ(cx + 6, cy - 4, 86, "w3")
    s += circ(cx, cy, 86, "w") + circ(cx, cy, 74, "bg")
    for k in range(5):
        a = math.radians(k * 72 - 90)
        b1, b2 = a - 0.16, a + 0.16
        c1, c2 = a - 0.3, a + 0.3
        ps = [(cx + 20 * math.cos(b1), cy + 20 * math.sin(b1)), (cx + 76 * math.cos(c1), cy + 76 * math.sin(c1)),
              (cx + 76 * math.cos(c2), cy + 76 * math.sin(c2)), (cx + 20 * math.cos(b2), cy + 20 * math.sin(b2))]
        s += poly(ps, "w")
    s += circ(cx, cy, 26, "w2") + circ(cx, cy, 10, "m")
    for k in range(5):
        a = math.radians(k * 72 - 54)
        s += circ(cx + 17 * math.cos(a), cy + 17 * math.sin(a), 3, "bg")
    return s


# ---------------------------------------------------------------- thermal
@part("thermal.radiator")
def _():
    s = shadow(160, 184, 146)
    s += rect(40, 40, 240, 130, "w2")
    for x in range(46, 276, 5):
        s += line(x, 42, x, 168, "o thin")
    for y in range(52, 168, 14):
        s += line(40, y, 280, y, "fin")
    s += rect(14, 32, 28, 146, "w3", 4) + rect(278, 32, 28, 146, "w3", 4)
    s += shaft(0, 60, [(14, 7)], "m", "m2") + shaft(306, 150, [(14, 7)], "m", "m2")
    return s


@part("thermal.ecomp")
def _():
    s = shadow(160, 184, 140)
    cy = 116
    s += shaft(30, cy, [(200, 54)], "w", "w2")
    ps = []
    for k in range(120):
        t = k / 120 * 5 * math.pi
        r = 4 + t * 2.6
        ps.append((230 + r * math.cos(t) * 0.34, cy + r * math.sin(t)))
    s += pline(ps, "o")
    s += box(60, 48, 120, 20, 30, "m2", "m", "m3")
    s += shaft(96, 172, [(20, 8)], "m", "m2") + shaft(150, 172, [(20, 8)], "m", "m2")
    return s


# ---------------------------------------------------------------- common
@part("common.bolt")
def _():
    s = shadow(160, 160, 140)
    cy = 104
    s += poly([(40, 70), (62, 60), (62, 150), (40, 140)], "w3")
    s += poly([(62, 60), (86, 62), (86, 148), (62, 150)], "w2")
    s += ell(92, cy, 10, 46, "w")
    s += shaft(92, cy, [(190, 18)], "w", "w2")
    for x in range(160, 282, 6):
        s += line(x, cy - 18, x + 4, cy + 18, "o thin")
    return s


@part("common.sintered")
def _():
    s = shadow(160, 186, 90)
    s += gear3d(160, 104, 62, 80, 20, 7, -6, 0, "w", "w3", tw=0.34)
    s += circ(160, 104, 32, "w2") + circ(160, 104, 18, "bg")
    for k in range(4):
        a = math.radians(k * 90 + 45)
        s += circ(160 + 46 * math.cos(a), 104 + 46 * math.sin(a), 6, "bg")
    return s


@part("common.bearing")
def _():
    s = shadow(160, 186, 100)
    cx, cy = 160, 104
    s += ell(cx + 18, cy - 6, 84, 80, "w3")
    s += ell(cx, cy, 84, 80, "w") + ell(cx, cy, 64, 60, "w2")
    for k in range(9):
        a = 2 * math.pi * k / 9
        s += circ(cx + 52 * math.cos(a), cy + 49 * math.sin(a), 11, "ball")
    s += ell(cx, cy, 42, 40, "w") + ell(cx, cy, 30, 28, "bg")
    return s


def part_svg(key, label):
    fn = PARTS.get(key)
    if not fn:
        return ""
    return svg(fn(), label)


# ---------------------------------------------------------------- added: EV / hybrid / diesel
def _gear_mod():
    import il_gear as GE
    return GE


@part("ev.batcase")
def _():
    GE = _gear_mod()
    s = shadow(160, 176, 150, 12)
    cam = GE.Cam(160, 100, -28, 34, 0.78)
    W, Dp, Hh, t = 300, 190, 34, 9
    x0, y0 = -W / 2, -Dp / 2

    def boxp(cx, cy, cz, sx, sy, sz, mat="alu"):
        # frame(0,0,1): u -> -y, v -> +x
        loop = [(-sy / 2, -sx / 2, 0), (sy / 2, -sx / 2, 1), (sy / 2, sx / 2, 2), (-sy / 2, sx / 2, 3)]
        return GE.prism(cam, (cx, cy, cz), (0, 0, 1), loop, sz, mat)
    out = boxp(0, 0, -6, W + 18, Dp + 18, 6)                          # floor plate + flange
    out += boxp(0, Dp / 2 - t / 2, 0, W, t, Hh)                         # back wall
    out += boxp(-W / 2 + t / 2, 0, 0, t, Dp - 2 * t, Hh)                # left wall
    for k in range(1, 4):                                                # cross members
        yy = Dp / 2 - t - (Dp - 2 * t) * k / 4
        out += boxp(0, yy, 0, W - 2 * t, 7, Hh * 0.7)
    # longitudinal centre rail
    out += boxp(0, 0, 0, 7, Dp - 2 * t, Hh * 0.7)
    out += boxp(W / 2 - t / 2, 0, 0, t, Dp - 2 * t, Hh)                 # right wall
    out += boxp(0, -Dp / 2 + t / 2, 0, W, t, Hh)                        # front wall
    # hollow extrusion cells visible on the front wall's cut end? -> ribs on outer face
    for k in range(13):
        xa = x0 + 16 + k * 21.5
        pts = [cam.P((xa, y0 - 0.2, 6)), cam.P((xa + 14, y0 - 0.2, 6)), cam.P((xa + 14, y0 - 0.2, Hh - 7)), cam.P((xa, y0 - 0.2, Hh - 7))]
        out += '<path class="bg" opacity=".55" d="M%s %sL%s %sL%s %sL%s %sZ"/>' % tuple(n(v) for q in pts for v in q[:2])
    # bolt holes along the front and right flange
    for k in range(12):
        xa = x0 + 4 + k * (W - 8) / 11
        c = cam.P((xa, y0 - 5, 0))
        out += '<ellipse class="bg" cx="%s" cy="%s" rx="2" ry="1.2"/>' % (n(c[0]), n(c[1]))
    for k in range(7):
        ya = y0 + 6 + k * (Dp - 12) / 6
        c = cam.P((W / 2 + 5, ya, 0))
        out += '<ellipse class="bg" cx="%s" cy="%s" rx="1.6" ry="1.2"/>' % (n(c[0]), n(c[1]))
    return s + out


@part("ev.motorshaft")
def _():
    GE = _gear_mod()
    s = shadow(160, 170, 150, 10)
    cam = GE.Cam(160, 104, -22, 18, 1.0)
    A = (1, 0, 0)
    x = -150
    out = ""
    for L, r, kind in [(34, 12, "spl"), (22, 16, None), (60, 22, None), (20, 27, "res"), (70, 22, None), (18, 16, None), (40, 13, None)]:
        if kind == "spl":
            out += GE.prism(cam, (x, 0, 0), A, GE.spline_outline(20, r, r - 2), L, "w", holes=[GE.circle_outline(6, 24, 24)])
        elif kind == "res":
            lob = [((r + 3 * math.cos(4 * 2 * math.pi * k / 48)) * math.cos(2 * math.pi * k / 48), (r + 3 * math.cos(4 * 2 * math.pi * k / 48)) * math.sin(2 * math.pi * k / 48), k // 6) for k in range(48)]
            out += GE.prism(cam, (x, 0, 0), A, lob, L, "cu", smooth=True)
        else:
            out += GE.cyl(cam, (x, 0, 0), A, r, L, "w")
        x += L
    return s + out


@part("ev.planetary")
def _():
    GE = _gear_mod()
    s = shadow(160, 178, 120, 12)
    cam = GE.Cam(160, 100, 0, 52, 0.62)
    z_r, z_s, z_p, m = 60, 24, 18, 3.0
    rr, rs, rp = z_r * m / 2, z_s * m / 2, z_p * m / 2
    s += GE.ring_gear3(cam, (0, 0, -18), (0, 0, 1), z_r, rr, rr + 20, 36, "w")
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        c = ((rs + rp) * math.cos(a), (rs + rp) * math.sin(a))
        s += GE.gear3(cam, (c[0], c[1], -14), (0, 0, 1), z_p, rp, 28, "w", phase=a + math.pi, bore=7)
    s += GE.gear3(cam, (0, 0, -14), (0, 0, 1), z_s, rs, 30, "w", phase=0.3 + math.pi / z_s, bore=12)
    return s


@part("engine.railpump")
def _():
    GE = _gear_mod()
    s = shadow(160, 170, 150, 10)
    cam = GE.Cam(150, 110, -24, 24, 1.0)
    out = GE.cyl(cam, (-150, 0, 0), (1, 0, 0), 13, 250, "w")
    out += GE.cyl(cam, (-160, 0, 0), (1, 0, 0), 8, 10, "w") + GE.cyl(cam, (100, 0, 0), (1, 0, 0), 9, 20, "w")
    for k in range(4):
        x = -110 + k * 62
        out += GE.cyl(cam, (x, 0, 8), (0, 0, 1), 9, 22, "w") + GE.cyl(cam, (x, 0, 30), (0, 0, 1), 6, 10, "w")
    out += GE.prism(cam, (40, -40, -58), (0, 0, 1), [(-38, -26, 0), (38, -26, 1), (38, 26, 2), (-38, 26, 3)], 44, "alu")
    out += GE.cyl(cam, (40, -40, -14), (0, 0, 1), 16, 12, "alu")
    return s + out


@part("engine.exhaust")
def _():
    GE = _gear_mod()
    s = shadow(160, 172, 150, 10)
    cam = GE.Cam(160, 106, -26, 20, 1.0)
    oval = [(34 * math.cos(2 * math.pi * k / 48), 24 * math.sin(2 * math.pi * k / 48), k // 4) for k in range(48)]
    out = GE.cyl(cam, (-170, 0, 0), (1, 0, 0), 10, 70, "w")
    out += GE.prism(cam, (-100, 0, 0), (1, 0, 0), [(u * 0.4, v * 0.4, f) for u, v, f in oval], 24, "w", smooth=True,
                    scale=lambda t: 1 + 1.5 * t)
    out += GE.prism(cam, (-76, 0, 0), (1, 0, 0), oval, 130, "w", smooth=True)
    out += GE.prism(cam, (54, 0, 0), (1, 0, 0), oval, 24, "w", smooth=True, scale=lambda t: 1 - 0.6 * t)
    out += GE.cyl(cam, (78, 0, 0), (1, 0, 0), 10, 70, "w")
    return s + out
