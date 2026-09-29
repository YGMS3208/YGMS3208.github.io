from il_detail import *

# ================================================================ CRANKSHAFT
CJ = [(30, 46), (82, 98), (134, 150), (186, 202), (238, 254)]
CP = [(56, 72, 22), (108, 124, -22), (160, 176, -22), (212, 228, 22)]
CW = [(46, 56, 22), (72, 82, 22), (98, 108, -22), (124, 134, -22), (150, 160, -22), (176, 186, -22), (202, 212, 22), (228, 238, 22)]


def crank_side(mode="w", flash=False):
    hot = mode == "hot"
    cw = "h" if hot else "w2"
    cj = "h" if hot else "w"
    s = ""
    if flash:
        s += rect(-6, -48, 290, 96, "flash", 10)
    for x0, x1, py in CW:
        sg = 1 if py > 0 else -1
        y_pin = py + sg * 16
        y_cw = -sg * 40
        s += rect(x0, min(y_pin, y_cw), x1 - x0, abs(y_pin - y_cw), cw, 4)
    s += rect(0, -7, 14, 14, cj) + rect(14, -10, 16, 20, cj)
    for x0, x1 in CJ:
        s += rect(x0, -13, x1 - x0, 26, cj)
    for x0, x1, py in CP:
        s += rect(x0, py - 12, x1 - x0, 24, cj)
        s += cl(x0 - 4, py, x1 + 4, py)
    s += rect(254, -36, 12, 72, cw, 3) + rect(266, -14, 10, 28, cj)
    s += cl(-10, 0, 290, 0)
    if not hot:
        s += hid("M92 -10 L66 18") + hid("M144 10 L118 -18") + hid("M196 10 L170 -18")
    return s


def crank_feat(kind, idx=None):
    if kind == "journal":
        js = CJ if idx is None else [CJ[idx]]
        return " ".join("M%s -13 L%s -13 M%s 13 L%s 13" % (n(a), n(b), n(a), n(b)) for a, b in js)
    if kind == "pin":
        ps = CP if idx is None else [CP[idx]]
        return " ".join("M%s %s L%s %s M%s %s L%s %s" % (n(a), n(p - 12), n(b), n(p - 12), n(a), n(p + 12), n(b), n(p + 12)) for a, b, p in ps)
    if kind == "flange":
        return "M254 -36 L266 -36 M254 36 L266 36 M266 -36 L266 36"
    if kind == "oil":
        return "M92 -10 L66 18 M144 10 L118 -18 M196 10 L170 -18"
    if kind == "snout":
        return "M0 -7 L14 -7 L14 -10 L30 -10 M0 7 L14 7 L14 10 L30 10"
    return ""


def crank_detail():
    s = ""
    pl = Pl(40, 150, 1.25)
    s += shadow(220, 262, 190, 12)
    s += pl.g(crank_side())
    notes = [("メインジャーナル", "5か所。軸受メタルで支持、真円度1〜3μm"),
             ("クランクピン", "コンロッドが付く偏心軸。ストローク・位相を管理"),
             ("カウンタウェイト", "回転のつり合いをとる。バランス修正の穴をあける"),
             ("フィレットR", "ピン・ジャーナル根元の隅R。疲労強度の要（焼入れ・ロール）"),
             ("油穴", "ジャーナルからピンへ油を送る斜め穴"),
             ("フランジ", "フライホイール取付面。振れ・ボルト穴位置"),
             ("前端（スナウト）", "プーリ・タイミングギヤの取付部")]
    s += bal(*pl(142, -13), 160, 60, 1)
    s += bal(*pl(116, -34), 108, 60, 2)
    s += bal(*pl(103, 36), 90, 250, 3)
    s += bal(*pl(124, -10), 244, 250, 4)
    s += bal(*pl(80, 5), 60, 250, 5)
    s += bal(*pl(260, 30), 400, 250, 6)
    s += bal(*pl(10, -8), 30, 60, 7)
    s += rect(380, 40, 94, 110, "m", 4) + text(427, 56, "ピン断面", "middle", "sm")
    s += circ(427, 100, 30, "w") + path("M397 100 A30 30 0 0 1 457 100 A30 30 0 0 1 397 100", "hotarc") + circ(427, 100, 4, "bg")
    s += text(427, 142, "表層を焼入れ", "middle", "sm")
    return s, notes


def crank_ops():
    ops = []
    # OP10 cut & heat
    s = title("棒鋼を定寸に切断し、誘導加熱で1,200℃前後に加熱")
    rv = Rev([(160, 26)])
    pl = Pl(20, 110, 1.0)
    s += pl.g(rv.svg())
    s += circ(186, 50, 44, "t") + circ(186, 50, 10, "m2") + rot(186, 50, 54, 54, 200, 250)
    s += line(180, 84, 180, 136, "cutl")
    s += text(100, 160, "棒鋼（S45C・非調質鋼）", "middle")
    for k in range(4):
        s += rect(250 + k * 50, 200, 40, 40, "h" if k < 3 else "w", 4)
    for x in range(252, 440, 12):
        s += path("M%s 190 a5 30 0 0 1 0 60" % n(x), "coilcu")
    s += arrow(236, 276, 440, 276, "コイル内を順送り", 338, 292)
    s += heat(270, 186, 3, 40) + tol(250, 170, "約1,200〜1,250℃")
    ops.append(s)
    # OP20 hot forging
    s = title("荒打ち→仕上げ打ちの型鍛造でクランク形状をつくる")
    s += rect(40, 34, 400, 30, "m3") + rect(60, 64, 360, 50, "t")
    s += rect(60, 212, 360, 50, "t") + rect(40, 262, 400, 26, "m2")
    pl = Pl(95, 162, 1.05)
    s += pl.g(crank_side("hot", flash=True))
    s += arrow(462, 40, 462, 110, "加圧", 456, 128, "end")
    s += heat(200, 118, 4, 24)
    s += lead(*pl(282, 30), 440, 180, "バリ", "middle")
    s += tol(40, 292, "4,000〜8,000t メカニカル鍛造プレス")
    ops.append(s)
    # OP30 trimming
    s = title("バリを抜き、必要に応じてひねり・コイニングで形を整える")
    pl = Pl(95, 150, 1.05)
    s += pl.g(rect(-6, -48, 290, 96, "w3", 10) + crank_side())
    s += pl.g(rect(-6, -48, 290, 96, "cutframe", 10))
    s += rect(80, 30, 330, 30, "m3") + arrow(245, 40, 245, 90, "抜き", 262, 70)
    s += lead(*pl(-2, -44), 40, 270, "バリ（除去）", "start")
    ops.append(s)
    # OP40 controlled cooling
    s = title("非調質鋼は衝風で冷却速度を制御して強度を出す → ショット")
    s += conveyor(20, 220, 440)
    for i, cls in enumerate(("h", "h", "w", "w")):
        pl = Pl(40 + i * 108, 196, 0.34)
        s += pl.g(crank_side("hot" if cls == "h" else "w"))
    for x in (90, 200, 310):
        s += circ(x, 70, 20, "m") + circ(x, 70, 6, "m3") + arrow(x, 96, x, 160, None)
    s += text(240, 270, "冷却速度 → 硬さ・組織", "middle") + tol(330, 120, "送風量を制御")
    ops.append(s)
    # OP50 MPI
    s = title("蛍光磁粉探傷で鍛造割れ・かぶりを検出し、硬さを確認")
    pl = Pl(95, 150, 1.05)
    s += pl.g(crank_side())
    s += rect(60, 40, 12, 170, "cu") + rect(406, 40, 12, 170, "cu") + line(66, 40, 412, 40, "cable")
    s += text(240, 56, "通電・磁化", "middle", "al")
    x, y = pl(117, -12)
    s += path("M%s %s l4 6 l-3 6" % (n(x), n(y)), "indic") + circ(x + 2, y + 6, 12, "mfring")
    s += rect(200, 240, 80, 20, "m3") + line(220, 240, 230, 176, "uv") + line(260, 240, 250, 176, "uv")
    s += text(240, 280, "UVライトで観察", "middle") + lead(x + 12, y + 6, 380, 250, "割れの指示模様")
    ops.append(s)
    # OP60 mass centering
    s = title("質量中心を測ってセンタ穴を加工し、バランス修正量を減らす")
    pl = Pl(100, 150, 1.0)
    s += pl.g(crank_side())
    for x in (38, 246):
        xx, yy = pl(x, 13)
        s += circ(xx - 8, yy + 8, 8, "m") + circ(xx + 8, yy + 8, 8, "m")
    s += rot(*pl(140, 0), 12, 52, -60, 60)
    s += tool("drill", *pl(0, 0), 0, 50, 8, spindle=True, rotarr=False, feed=False)
    s += tool("drill", *pl(276, 0), 180, 50, 8, spindle=True, rotarr=False, feed=False)
    s += tol(120, 270, "回転させて質量中心軸を求め、両端にセンタ穴") + text(240, 60, "慣性主軸", "middle", "al")
    s += line(*pl(-10, -3), *pl(290, 3), "a")
    ops.append(s)
    # OP70 end & flange turning
    s = title("前端・フランジ・ジャーナル端面を旋削")
    pl = Pl(80, 150, 1.05)
    s += chuck(*pl(30, 0), 34)
    s += pl.g(crank_side())
    s += pl.g(mf(crank_feat("flange")) + mf(crank_feat("snout")))
    s += tool("turn", *pl(262, -36), 90, 60, 16, spindle=False, rotarr=False, feedlab="送り")
    s += tool("turn", *pl(266, 0), 180, 60, 16, spindle=False, rotarr=False, feed=False)
    s += lead(*pl(260, 36), 420, 260, "フランジ（外径・端面）", "middle") + lead(*pl(8, 8), 60, 260, "前端", "middle")
    s += rot(*pl(140, 0), 12, 52, -60, 60)
    ops.append(s)
    # OP80 crank miller
    s = title("リング状カッタでピンを追従加工（クランクシャフトミラー）")
    pl = Pl(80, 160, 1.1)
    s += pl.g(crank_side())
    s += pl.g(mf(crank_feat("pin", 1)))
    x0, y0 = pl(116, -22)
    s += rect(x0 - 16, y0 - 70, 32, 140, "t", 6) + rect(x0 - 12, y0 - 50, 24, 100, "void", 4)
    for k in range(5):
        s += poly([(x0 - 12, y0 - 40 + k * 20), (x0 - 6, y0 - 36 + k * 20), (x0 - 12, y0 - 32 + k * 20)], "ins")
    s += circ(*pl(116, 0), 22 * 1.1, "orbit")
    s += arrow(x0 + 30, y0 - 60, x0 + 30, y0 + 20, None, both=True) + text(x0 + 38, y0 - 24, "ピン位置に追従", "start", "al")
    s += tol(40, 280, "内刃式ミーリング：ジャーナル・ピンを順に荒加工")
    ops.append(s)
    # OP90 oil holes
    s = title("ジャーナルからピンへ通じる斜め油穴をガンドリルで加工")
    pl = Pl(80, 150, 1.1)
    s += pl.g(crank_side())
    s += pl.g(path(crank_feat("oil"), "mf"))
    x, y = pl(66, 18)
    ang = math.degrees(math.atan2(18 + 10, 66 - 92))
    s += tool("gundrill", x, y, ang, 150, 5, spindle=False, rotarr=False, feed=False)
    s += lead(*pl(144, 10), 330, 262, "油穴（交差部のバリに注意）")
    ops.append(s)
    # OP100 induction hardening
    s = title("ピン・ジャーナル・フィレットを高周波焼入れ")
    pl = Pl(80, 160, 1.1)
    s += pl.g(crank_side())
    for x0, x1, py in CP:
        xa, ya = pl(x0 - 2, py - 12)
        xb, yb = pl(x1 + 2, py + 12)
        s += rect(xa, ya, xb - xa, yb - ya, "hotband")
    x0, y0 = pl(108, -34)
    s += path("M%s %s a18 14 0 0 1 36 0" % (n(x0 - 2), n(y0)), "coilcu") + rect(x0 + 8, y0 - 44, 16, 30, "cu")
    s += nozzle(x0 + 60, y0 - 10, 140, 18) + drops(x0 + 60, y0 - 10, 3, 24, 22, 140)
    s += lead(x0 + 16, y0 - 30, 330, 70, "半開放式コイル（ピン追従）")
    s += tol(40, 280, "硬化層深さ・硬化パターン・焼割れを管理（渦流で全数判定）")
    ops.append(s)
    # OP110 straightening
    s = title("焼入れで生じた曲がりを測定し、プレスで矯正")
    pl = Pl(90, 150, 1.05)
    s += pl.g(crank_side())
    for x in (38, 246):
        xx, yy = pl(x, 13)
        s += poly([(xx - 14, yy + 18), (xx + 14, yy + 18), (xx, yy)], "m2")
    x, y = pl(142, -13)
    s += rect(x - 16, 40, 32, y - 44, "m3") + arrow(x + 30, 50, x + 30, y - 10, None) + text(x + 38, 76, "押し", "start", "al")
    xx, yy = pl(194, 13)
    s += rect(xx - 10, yy + 20, 20, 30, "m", 3) + line(xx, yy + 20, xx, yy + 2, "o") + text(xx, yy + 66, "振れ測定", "middle")
    ops.append(s)
    # OP120 grinding
    s = title("CBN砥石でピン・ジャーナルを研削（ピン追従研削）")
    pl = Pl(70, 180, 1.1)
    s += center(*pl(-10, 0), False) + center(*pl(286, 0), True)
    s += pl.g(crank_side())
    s += pl.g(mf(crank_feat("pin", 1)) + mf(crank_feat("journal")))
    x, y = pl(116, -34)
    s += wheel(x, y - 56, 56, "CBN砥石")
    s += circ(*pl(116, 0), 22 * 1.1, "orbit")
    s += arrow(x + 80, y - 30, x + 80, y + 10, None, both=True) + text(x + 88, y - 10, "砥石台が追従", "start", "al")
    s += tol(40, 290, "真円度 1〜3μm・ストローク・位相。インプロセスゲージで定寸")
    ops.append(s)
    # OP130 fillet roll
    s = title("フィレットにローラを押し付け、圧縮残留応力で疲労強度を上げる")
    pl = Pl(40, 170, 1.4)
    s += pl.g(crank_side())
    for x in (108, 124):
        xx, yy = pl(x, -34)
        s += circ(xx, yy - 6, 9, "t") + arrow(xx, yy - 50, xx, yy - 18, None)
    s += tol(300, 60, "ローラ荷重を制御") + tol(300, 76, "焼入れの代わりに使う場合も")
    ops.append(s)
    # OP140 micro finishing
    s = title("テープ・砥石でジャーナル・ピン表面を仕上げ（マイクロフィニッシュ）")
    pl = Pl(80, 160, 1.1)
    s += pl.g(crank_side())
    s += pl.g(mf(crank_feat("journal", 2)))
    x, y = pl(142, 0)
    s += rect(x - 14, y - 50, 28, 30, "m2", 4) + rect(x - 14, y + 20, 28, 30, "m2", 4)
    s += rect(x - 10, y - 20, 20, 4, "gw") + rect(x - 10, y + 16, 20, 4, "gw")
    s += arrow(x - 40, y - 64, x + 40, y - 64, None, both=True) + text(x, y - 72, "揺動", "middle", "al")
    s += tol(40, 280, "面粗さ Ra0.1〜0.2μm。油膜の安定と焼付き防止")
    ops.append(s)
    # OP150 balancing
    s = title("回転アンバランスを測り、カウンタウェイトに穴をあけて修正")
    pl = Pl(90, 150, 1.05)
    s += pl.g(crank_side())
    for x in (38, 246):
        xx, yy = pl(x, 13)
        s += circ(xx - 8, yy + 8, 8, "m") + circ(xx + 8, yy + 8, 8, "m")
    s += pl.g(circ(103, 32, 3.5, "mfa") + circ(155, -34, 3.5, "mfa"))
    x, y = pl(103, 38)
    s += tool("drill", x, y, -90, 60, 8, spindle=True, rotarr=False, feed=False)
    s += rot(*pl(150, 0), 12, 52, -60, 60)
    s += lead(*pl(155, -34), 330, 60, "修正穴") + tol(300, 270, "残留アンバランスを規格内に")
    ops.append(s)
    # OP160 final inspection
    s = title("洗浄後、径・真円度・ストローク・位相を全数自動測定")
    pl = Pl(80, 170, 1.1)
    s += center(*pl(-10, 0), False) + center(*pl(286, 0), True)
    s += pl.g(crank_side())
    for x in (38, 90, 142, 194, 246):
        xx, yy = pl(x, -13)
        s += rect(xx - 4, 50, 8, yy - 52, "m3") + circ(xx, yy - 2, 3, "t")
    s += tol(40, 40, "シャフト形状測定機（全数）") + tol(300, 40, "磁粉探傷で最終確認")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CAMSHAFT
LOBES = [(46, -1), (70, 1), (112, 1), (136, -1), (178, -1), (202, 1), (244, 1), (268, -1)]
JOURN = [(20, 32), (88, 100), (154, 166), (220, 232)]


def cam_side(tube_only=False):
    s = Rev([(290, 7)], bore=[(0, 290, 3.5)]).svg()
    if tube_only:
        return s
    for x0, x1 in JOURN:
        s += rect(x0, -11, x1 - x0, 22, "w")
    for x, sg in LOBES:
        s += path("M%s -13 L%s -13 L%s 13 L%s 13Z" % (n(x), n(x + 10), n(x + 10), n(x)), "w2")
        s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(x + 1), n(sg * 13), n(x + 9), n(sg * 13), n(x + 7), n(sg * 22), n(x + 3), n(sg * 22)), "w2")
    return s


def cam_lobe_front(cx, cy, k=1.0, cls="w", ang=-90):
    th = math.radians(ang)
    ps = []
    for i in range(72):
        ph = 2 * math.pi * i / 72
        r = (26 + 16 * max(0.0, math.cos(ph - th)) ** 3) * k
        ps.append((cx + r * math.cos(ph), cy + r * math.sin(ph)))
    return poly(ps, cls)


def cam_detail():
    s = shadow(220, 250, 190, 10)
    pl = Pl(40, 150, 1.25)
    s += pl.g(cam_side())
    notes = [("カムロブ", "バルブを押し開く偏心輪郭。プロフィール誤差・位相を管理"),
             ("ジャーナル", "ヘッドの軸受で支持。径・真円度"),
             ("中空パイプ（組立式）", "鋼管にロブを拡管・圧入で固定して軽量化"),
             ("ベース円", "バルブが閉じている区間。すき間調整の基準")]
    s += bal(*pl(75, -20), 90, 60, 1) + bal(*pl(94, 11), 130, 250, 2) + bal(*pl(150, 0), 200, 250, 3)
    s += rect(360, 40, 110, 120, "m", 4) + text(415, 56, "ロブ正面", "middle", "sm")
    s += cam_lobe_front(415, 108, 1.0) + circ(415, 108, 7, "bg")
    s += bal(398, 126, 380, 190, 4)
    return s, notes


def cam_ops():
    ops = []
    s = title("鋼管を定寸に切断し、端部を加工")
    pl = Pl(90, 150, 1.0)
    s += chuck(*pl(0, 0), 20) + pl.g(cam_side(tube_only=True)) + pl.g(mf(Rev([(290, 7)]).face(290)))
    s += tool("turn", *pl(291, 0), 180, 60, 14, spindle=False, rotarr=False, feed=False)
    s += tol(90, 240, "全長・端面の直角度") + rot(*pl(100, 0), 8, 22, -60, 60)
    ops.append(s)
    s = title("カムロブを鍛造（または焼結）でつくり、カム面を焼入れ")
    s += rect(50, 50, 120, 40, "t") + rect(50, 190, 120, 40, "t") + cam_lobe_front(110, 140, 1.1, "h")
    s += arrow(30, 60, 30, 120, None) + text(110, 262, "冷間鍛造・焼結", "middle")
    s += cam_lobe_front(330, 140, 1.1) + circ(330, 140, 8, "bg")
    s += path("M296 96 A40 40 0 0 1 364 96", "hotarc") + path("M300 90 a30 30 0 0 1 60 0", "coilcu")
    s += text(330, 262, "カム面を高周波焼入れ", "middle") + arrow(190, 140, 270, 140, None)
    ops.append(s)
    s = title("位相を合わせてロブを通し、鋼管を内側から拡げて固定")
    pl = Pl(90, 150, 1.0)
    s += pl.g(cam_side())
    s += rect(pl(-60, 0)[0], 147, 200, 6, "m3") + arrow(pl(-60, 0)[0], 176, pl(80, 0)[0], 176, "マンドレルで拡管", pl(10, 0)[0], 192)
    s += tol(90, 60, "カム位相・締結強度（すべりトルク）を管理")
    ops.append(s)
    s = title("ジャーナルを円筒研削（複数ジャーナル同時）")
    pl = Pl(90, 170, 1.0)
    s += center(*pl(-4, 0), False) + center(*pl(294, 0), True) + pl.g(cam_side())
    for x0, x1 in JOURN[1::2]:
        s += pl.g(mf("M%s -11 L%s -11" % (n(x0), n(x1))))
        xx, yy = pl((x0 + x1) / 2, -11)
        s += wheel(xx, yy - 40, 40)
    s += tol(90, 280, "径・真円度・振れ")
    ops.append(s)
    s = title("主軸の回転角に砥石台の送りを同期させてカム形状を研削")
    s += cam_lobe_front(170, 160, 1.9) + circ(170, 160, 13, "bg")
    ps = []
    for i in range(72):
        ph = 2 * math.pi * i / 72
        r = (26 + 16 * max(0.0, math.cos(ph + math.pi / 2)) ** 3) * 1.9
        ps.append((170 + r * math.cos(ph), 160 + r * math.sin(ph)))
    s += pline(ps[45:66], "mf")
    s += wheel(360, 150, 64, "CBN砥石")
    s += arrow(300, 250, 420, 250, None, both=True) + text(360, 270, "回転角に同期して前後", "middle", "al")
    s += rot(170, 160, 100, 100, 200, 250) + text(90, 60, "回転", "middle", "al")
    s += tol(20, 290, "プロフィール誤差・位相・研削焼け")
    ops.append(s)
    s = title("カム・ジャーナル面を超仕上げし、洗浄")
    s += cam_lobe_front(200, 160, 1.9) + circ(200, 160, 13, "bg")
    s += rect(300, 120, 50, 40, "m2", 4) + rect(290, 130, 10, 20, "gw") + arrow(370, 110, 370, 170, None, both=True)
    s += text(360, 190, "テープラップ", "middle") + rot(200, 160, 100, 100, 200, 250)
    ops.append(s)
    s = title("カムプロフィール・位相を全数測定し、研削焼けを確認")
    pl = Pl(90, 190, 1.0)
    s += center(*pl(-4, 0), False) + center(*pl(294, 0), True) + pl.g(cam_side())
    for x, sg in LOBES[:4]:
        xx, yy = pl(x + 5, -24)
        s += rect(xx - 3, 80, 6, yy - 82, "m3") + circ(xx, yy - 2, 3, "t")
    s += chart(300, 40, 160, 80, "profile") + text(380, 136, "プロフィール誤差", "middle", "sm")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ VALVE
def valve_side(hot_head=False):
    s = Rev([(6, 5), (3, 4), (4, 5), (3, 4), (180, 5)]).svg()
    head_ = "M196 -5 Q222 -6 232 -26 L240 -26 L240 26 L232 26 Q222 6 196 5Z"
    s += path(head_, "h" if hot_head else "w")
    s += path("M196 -5 Q222 -6 232 -26 L240 -26 L240 0 L196 0Z", "h" if hot_head else "cut")
    s += line(232, -26, 238, -20, "o") + line(232, 26, 238, 20, "o")
    return s


VALVE_FEAT = {"stem": "M16 -5 L196 -5 M16 5 L196 5", "seat": "M232 -26 L240 -18 M232 26 L240 18",
              "tip": "M0 -5 L0 5", "face": "M240 -26 L240 26", "groove": "M6 -4 L9 -4 M13 -4 L16 -4"}


def valve_detail():
    s = shadow(240, 240, 190, 8)
    pl = Pl(40, 150, 1.6)
    s += pl.g(valve_side())
    notes = [("傘部（フェース）", "燃焼室側。排気側は耐熱鋼・Ni基合金"),
             ("シート面（45°）", "バルブシートに当たる面。ステライト肉盛り＋研削"),
             ("軸部（ステム）", "ガイドを往復する。径公差数μm・窒化/めっき"),
             ("コッター溝", "リテーナとコッターで保持する溝"),
             ("軸端", "ロッカー・リフタが当たる。端面焼入れ"),
             ("摩擦圧接部", "傘部材と軸部材の接合位置（異材）")]
    s += bal(*pl(240, 10), 440, 220, 1) + bal(*pl(236, -23), 400, 70, 2) + bal(*pl(100, 5), 180, 250, 3)
    s += bal(*pl(10, -4), 60, 70, 4) + bal(*pl(0, 3), 40, 250, 5) + bal(*pl(120, -5), 240, 70, 6)
    return s, notes


def valve_ops():
    ops = []
    s = title("傘部用の耐熱鋼と軸部用の鋼を摩擦圧接")
    s += Pl(40, 150, 1.0).g(Rev([(120, 8)]).svg()) + Pl(170, 150, 1.0).g(Rev([(140, 6)]).svg())
    s += path("M160 138 q-6 12 0 24 q8 -12 0 -24", "h") + heat(156, 132, 2, 8)
    s += rot(90, 150, 8, 22, -60, 60, "回転", 90, 190) + arrow(360, 150, 314, 150, "押し付け", 340, 140)
    s += text(100, 120, "SUH35（傘部側）", "middle") + text(240, 120, "SUH11（軸部側）", "middle")
    ops.append(s)
    s = title("軸端を通電加熱して据え込み、傘部を型鍛造")
    s += Pl(40, 150, 1.0).g(Rev([(170, 6)]).svg()) + ell(236, 150, 26, 30, "h")
    s += rect(150, 120, 14, 60, "cu") + text(157, 200, "電極", "middle")
    s += rect(330, 60, 110, 60, "t") + rect(330, 180, 110, 60, "t") + path("M300 150 Q340 140 360 118 L372 118 L372 182 L360 182 Q340 160 300 150Z", "h")
    s += arrow(268, 150, 296, 150, None) + text(385, 262, "傘部の型鍛造", "middle")
    ops.append(s)
    s = title("材料に応じて溶体化・時効や焼入れ焼戻し")
    s += rect(60, 70, 360, 150, "m2", 6) + rect(70, 80, 340, 130, "hotin")
    for k in range(5):
        s += Pl(110, 100 + k * 22, 0.9).g(valve_side())
    s += tol(60, 250, "硬さ・組織")
    ops.append(s)
    s = title("排気バルブのシート面にステライトをプラズマ粉体肉盛り")
    pl = Pl(-120, 150, 1.6)
    s += pl.g(valve_side())
    x, y = pl(236, -24)
    s += path("M%s %s L%s %s L%s %s L%s %sZ" % (n(x + 30), n(y - 90), n(x + 60), n(y - 90), n(x + 30), n(y - 16), n(x + 18), n(y - 24)), "m3")
    s += line(x + 20, y - 18, x + 8, y - 2, "beam") + pl.g(path(VALVE_FEAT["seat"], "coat"))
    s += rot(*pl(220, 0), 14, 50, -60, 60, "回転", pl(220, 0)[0], 250)
    s += tol(300, 250, "肉盛り厚・希釈率・割れ")
    ops.append(s)
    s = title("傘部と軸部を旋削")
    pl = Pl(40, 150, 1.6)
    s += chuck(*pl(0, 0), 20) + pl.g(valve_side()) + pl.g(mf("M232 -26 L240 -26 L240 26"))
    s += tool("turn", *pl(236, -26), 90, 60, 16, spindle=False, rotarr=False, feedlab="送り")
    ops.append(s)
    s = title("軸部をセンタレス研削、シート面をアンギュラ研削")
    pl = Pl(40, 130, 1.6)
    s += pl.g(valve_side()) + pl.g(mf(VALVE_FEAT["stem"]) + mf(VALVE_FEAT["seat"]))
    s += rect(pl(40, 0)[0], 64, 200, 50, "gw", 6) + text(pl(100, 0)[0], 58, "研削砥石", "middle", "al")
    s += rect(pl(40, 0)[0], 146, 200, 34, "rbx", 6) + text(pl(100, 0)[0], 198, "調整車", "middle")
    x, y = pl(236, -26)
    s += wheel(x - 10, y - 30, 24)
    s += tol(40, 280, "軸径 数μm・シート振れ")
    ops.append(s)
    s = title("軸部を窒化・硬質クロムめっきして耐摩耗性を上げる")
    s += tank(40, 70, 400, 170, 0.8)
    for k in range(4):
        s += Pl(70, 110 + k * 30, 1.3).g(valve_side())
    s += tol(40, 270, "窒化層深さ・めっき膜厚")
    ops.append(s)
    s = title("軸径・全長・シート振れと外観を全数検査")
    pl = Pl(40, 160, 1.6)
    s += pl.g(valve_side())
    for x in (60, 140):
        xx, yy = pl(x, -5)
        s += rect(xx - 4, 60, 8, yy - 62, "m3") + circ(xx, yy - 2, 3, "t")
    x, y = pl(240, 0)
    s += rect(x - 10, y - 110, 50, 40, "m3", 4) + line(x + 5, y - 70, x - 4, y - 20, "o thin dash") + text(x + 15, y - 118, "画像検査", "middle")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CYLINDER HEAD
def head_end(mode="cut", valves=False):
    c = "cut" if mode == "cut" else "h"
    s = path(P([(10, 170), (230, 170), (230, 40), (212, 28), (28, 28), (10, 40)]), c)
    ports = [[(10, 84), (40, 84), (80, 116), (98, 152), (82, 160), (64, 132), (34, 118), (10, 118)],
             [(230, 84), (200, 84), (160, 116), (142, 152), (158, 160), (176, 132), (206, 118), (230, 118)]]
    cls_void = "void" if mode == "cut" else "sand"
    for pp in ports:
        s += path(P(pp), cls_void)
    s += path(P([(64, 170), (120, 146), (176, 170)]), "void" if mode == "cut" else c)
    for pp in ([(98, 58), (111, 58), (111, 130), (98, 118)], [(129, 58), (142, 58), (142, 118), (129, 130)],
               [(16, 128), (30, 128), (30, 162), (16, 162)], [(210, 128), (224, 128), (224, 162), (210, 162)]):
        s += path(P(pp), cls_void)
    if mode == "cut":
        s += rect(114, 40, 12, 108, "void")
        for sx, ang in ((1, -106), (-1, -74)):
            cx, cy = (120 - sx * 50, 104)
            s += '<g transform="translate(%s %s) rotate(%s)">%s</g>' % (n(cx), n(cy), n(ang + 90), rect(-4, -22, 8, 44, "w3"))
        s += '<g transform="translate(89 157) rotate(-16)">' + rect(-10, -3, 20, 6, "w3") + "</g>"
        s += '<g transform="translate(151 157) rotate(16)">' + rect(-10, -3, 20, 6, "w3") + "</g>"
        for cx in (62, 178):
            s += rect(cx - 18, 14, 36, 20, "w3") + circ(cx, 34, 12, "void") + line(cx - 18, 34, cx + 18, 34, "o thin")
        s += hid("M88 157 L60 60 M152 157 L180 60")
    if valves:
        for sx, ang in ((1, -106), (-1, -74)):
            x0, y0 = (88, 157) if sx == 1 else (152, 157)
            x1, y1 = (58, 52) if sx == 1 else (182, 52)
            s += line(x0, y0, x1, y1, "stem")
            s += '<g transform="translate(%s %s) rotate(%s)">' % (n(x0), n(y0 + 2), n(ang + 90)) + path("M-14 2 L14 2 L6 -6 L-6 -6Z", "w") + "</g>"
            mx, my = (x0 + x1) / 2 - 2 * sx, (y0 + y1) / 2 - 20
            s += '<g transform="translate(%s %s) rotate(%s)">%s</g>' % (n(mx), n(my), n(ang), coil(-22, 22, 0, 10, 4))
    s += cl(120, 10, 120, 180)
    return s


HEAD_F = {"deck": "M10 170 L230 170", "seat": "M80 160 L98 152 M142 152 L160 160",
          "guide": "M80 128 L66 78 M160 128 L174 78", "camj": "M50 34 A12 12 0 0 0 74 34 M166 34 A12 12 0 0 0 190 34",
          "ports": "M10 84 L40 84 L80 116 L98 152 M230 84 L200 84 L160 116 L142 152", "jacket": "M98 58 L111 58 L111 130 L98 118Z M129 58 L142 58 L142 118 L129 130Z"}


def head_side(done=()):
    s = rect(10, 20, 300, 90, "w")
    for x in (30, 95, 160, 225, 290):
        s += rect(x - 12, 8, 24, 14, "w3") + hid("M%s 30 m-10 0 a10 10 0 1 0 20 0 a10 10 0 1 0 -20 0" % n(x))
    for i in range(4):
        x = 62 + i * 65
        s += rect(x - 16, 56, 32, 26, "void", 8)
        s += hid("M%s 110 Q%s 96 %s 110" % (n(x - 22), n(x), n(x + 22)))
    s += cl(0, 30, 320, 30)
    if "deck" in done:
        s += line(10, 110, 310, 110, "done")
    return s


HEAD_S = {"deck": "M10 110 L310 110", "camline": " ".join("M%s 30 L%s 30" % (n(x - 12), n(x + 12)) for x in (30, 95, 160, 225, 290)),
          "cover": "M10 20 L310 20"}


def head_detail():
    s = ""
    o = Ob(40, 140, 220, 60, 100)
    s += shadow(190, 262, 170, 10)
    s += poly([o.front(0, 0), o.front(220, 0), o.front(220, 60), o.front(0, 60)], "w")
    s += poly([o.front(220, 0), o.side(100, 0), o.side(100, 60), o.front(220, 60)], "w3")
    s += poly([o.top(0, 0), o.top(220, 0), o.top(220, 100), o.top(0, 100)], "w2")
    for i in range(5):
        u = 12 + i * 49
        for v in (26, 74):
            s += poly([o.top(u - 7, v - 9), o.top(u + 7, v - 9), o.top(u + 7, v + 9), o.top(u - 7, v + 9)], "w3")
    for i in range(4):
        u = 36 + i * 49
        s += poly(o.circle("top", u, 50, 6, 20), "bg")
        s += poly([o.front(u - 16, 16), o.front(u + 16, 16), o.front(u + 16, 40), o.front(u - 16, 40)], "bg")
    s += poly(o.circle("side", 26, 30, 10), "bg") + poly(o.circle("side", 74, 30, 10), "bg")
    notes = [("燃焼室・デッキ面", "ブロックとの合わせ面。平面度管理"), ("吸気ポート", "砂中子で形づくる曲がった流路"),
             ("バルブシート", "焼結合金を圧入。シート当たり幅を管理"), ("バルブガイド", "シートと同軸に仕上げる（数μm）"),
             ("カムジャーナル", "カムシャフトの軸受。キャップと共加工"), ("ウォータジャケット", "燃焼室まわりを冷やす水路"),
             ("点火プラグ穴", "燃焼室中央へ通じるねじ穴")]
    pl = Pl(300, 70, 0.72)
    s += rect(292, 50, 182, 190, "m", 4) + text(383, 66, "断面（吸排気バルブ中心）", "middle", "sm")
    s += pl.g(head_end())
    s += bal(*o.front(110, 60), 120, 270, 1)
    s += bal(*o.front(85, 28), 30, 90, 2)
    s += bal(*pl(89, 157), 340, 262, 3)
    s += bal(*pl(72, 100), 300, 262, 4)
    s += bal(*o.top(110, 26), 150, 40, 5)
    s += bal(*pl(104, 90), 380, 262, 6)
    s += bal(*pl(120, 90), 420, 262, 7)
    return s, notes


def head_ops():
    ops = []
    s = title("吸排気ポート・ウォータジャケットの形を砂中子でつくる")
    s += rect(60, 60, 170, 150, "m2") + rect(250, 60, 170, 150, "m2")
    for pp in ([(70, 110), (120, 110), (170, 150), (190, 196), (170, 200), (150, 170), (110, 150), (70, 150)],):
        s += path(P(pp), "sand")
    s += path(P([(410, 110), (360, 110), (310, 150), (290, 196), (310, 200), (330, 170), (370, 150), (410, 150)]), "sand")
    s += dots(70, 110, 120, 90, 9, "grain") + dots(290, 110, 120, 90, 9, "grain")
    s += rect(60, 34, 360, 22, "m3") + text(240, 50, "ブローヘッド", "middle")
    for x in (150, 240, 330):
        s += arrow(x, 58, x, 90, None)
    s += text(145, 232, "吸気ポート中子", "middle") + text(335, 232, "排気ポート中子", "middle")
    s += tol(60, 270, "コールドボックス／無機バインダ。強度・ガス発生量を管理")
    ops.append(s)
    s = title("金型に砂中子を組み込み、低圧で下から注湯")
    s += rect(80, 40, 320, 200, "m2")
    pl = Pl(120, 50, 1.0)
    s += pl.g(head_end("hot"))
    s += rect(110, 222, 260, 18, "m3") + text(240, 256, "燃焼室側（下型）で急冷 → 組織を細かく", "middle")
    s += rect(232, 240, 16, 40, "h") + arrow(206, 290, 206, 250, None) + text(214, 284, "下から充填", "start", "al")
    s += lead(*pl(40, 100), 430, 90, "砂中子（ポート）", "end") if False else lead(*pl(30, 100), 420, 60, "砂中子（ポート）", "middle")
    ops.append(s)
    s = title("振動・加熱で中子砂を落とし、湯口・押湯を切断")
    pl = Pl(120, 60, 1.0)
    s += pl.g(head_end())
    s += dots(pl(10, 0)[0] - 10, 240, 250, 40, 8, "grain")
    for x in (100, 380):
        s += arrow(x, 120, x + 20 if x < 200 else x - 20, 110, None, both=True)
    s += rect(200, 30, 80, 20, "w3") + line(196, 52, 284, 52, "cutl") + text(290, 44, "押湯を切断", "start", "al")
    s += text(240, 292, "ポート・水路の中の砂を確実に落とす（エンジン内の異物になる）", "middle", "sm")
    ops.append(s)
    s = title("溶体化・焼入れ・時効（T6）で強度を出す")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin")
    for i in range(3):
        s += Pl(60 + i * 124, 110, 0.48).g(head_end())
    s += tol(40, 250, "硬さ・ひずみ・焼入れ割れ")
    ops.append(s)
    s = title("燃焼室・ポートまわりの鋳巣をX線で確認")
    s += rect(20, 120, 50, 60, "m3", 4)
    for k in range(7):
        s += line(70, 150, 390, 50 + k * 34, "ray")
    pl = Pl(130, 60, 1.0)
    s += pl.g(head_end())
    x, y = pl(70, 150)
    s += circ(x, y, 3, "poro") + circ(x + 6, y - 4, 2.4, "poro") + circ(x + 2, y, 13, "mfring")
    s += rect(392, 40, 22, 220, "m2") + lead(x - 13, y, 40, 250, "鋳巣", "start")
    ops.append(s)
    s = title("デッキ面・カバー面・ボルト穴・インジェクタ／プラグ穴を加工")
    pl = Pl(80, 90, 1.0)
    s += pl.g(head_side())
    s += pl.g(mf(HEAD_S["deck"]))
    s += tool("facemill", *pl(200, 111), -90, 50, 80)
    for x in (30, 290):
        s += loc(*pl(x, 20), 90)
    s += lead(*pl(80, 110), 40, 280, "デッキ面（燃焼室側）", "start")
    s += tol(300, 40, "平面度・穴位置")
    ops.append(s)
    s = title("バルブシートとガイドを冷やしばめ・圧入")
    pl = Pl(120, 60, 1.0)
    s += pl.g(head_end())
    s += pl.g(mf(HEAD_F["seat"]) + mf(HEAD_F["guide"]))
    x, y = pl(60, 60)
    s += '<g transform="translate(%s %s) rotate(-16)">' % (n(x - 4), n(y - 30)) + rect(-8, -60, 16, 60, "m3") + "</g>"
    s += arrow(x - 30, y - 70, x - 10, y - 10, "圧入", x - 36, y - 76)
    s += lead(*pl(89, 157), 40, 280, "シートリング（焼結合金）", "start")
    s += tol(320, 272, "液体窒素で冷やして挿入") + tol(320, 288, "荷重・変位を監視")
    ops.append(s)
    s = title("シート面とガイド穴を1本の複合工具で同時に仕上げ（同軸）")
    pl = Pl(120, 40, 1.0)
    s += pl.g(head_end())
    s += pl.g(mf(HEAD_F["seat"].split(" M")[0]) + mf("M80 128 L66 78"))
    x, y = pl(88, 157)
    s += '<g transform="translate(%s %s) rotate(%s)">' % (n(x), n(y), n(-106)) + rect(0, -3, 110, 6, "t") + rect(-4, -12, 10, 24, "t") + rect(-60, -14, 56, 28, "m2", 4) + "</g>"
    s += lead(*pl(66, 90), 40, 60, "リーマ（ガイド穴）", "start") + lead(*pl(84, 160), 40, 270, "フォームツール（シート面）", "start")
    s += tol(320, 262, "シートとガイドの同軸度") + tol(320, 278, "数μm・当たり幅")
    ops.append(s)
    s = title("カムキャップと共加工でカムジャーナル穴を一直線に仕上げ")
    pl = Pl(80, 110, 1.0)
    s += pl.g(head_side())
    s += pl.g(mf(HEAD_S["camline"]))
    y = pl(0, 30)[1]
    s += rect(pl(-10, 0)[0], y - 4, 330, 8, "t") + rect(pl(320, 0)[0], y - 18, 60, 36, "m2", 4)
    s += arrow(pl(330, 0)[0], y + 30, pl(270, 0)[0], y + 30, "送り", pl(300, 0)[0], y + 46)
    s += tol(80, 270, "同軸度・真円度（ラインボーリング）")
    ops.append(s)
    s = title("洗浄後、水路・油路・燃焼室の漏れを確認")
    pl = Pl(120, 60, 1.0)
    s += pl.g(head_end())
    s += pl.g(path(HEAD_F["jacket"], "pres") + path(HEAD_F["ports"], "pres"))
    s += pl.g(rect(0, 170, 240, 10, "m3") + rect(0, 80, 10, 44, "m3") + rect(230, 80, 10, 44, "m3"))
    s += line(370, 150, 420, 150, "cable") + circ(438, 130, 20, "m") + line(438, 130, 448, 118, "a")
    s += text(438, 170, "差圧計", "middle") + tol(40, 280, "シール治具でポート・デッキを塞いで加圧")
    ops.append(s)
    s = title("バルブ・スプリング・リテーナ・コッターを組み付け")
    pl = Pl(120, 60, 1.0)
    s += pl.g(head_end(valves=True))
    x, y = pl(58, 52)
    s += rect(x - 14, y - 60, 28, 44, "m3", 3) + arrow(x + 24, y - 60, x + 24, y - 14, None) + text(x + 30, y - 40, "圧縮・コッター挿入", "start", "al")
    s += tol(320, 280, "コッターの有無・着座を画像で確認")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CONNECTING ROD
def rod_front(mode="w", split=False, gap=0):
    c = "h" if mode == "hot" else "w"
    s = ""
    beam = P([(-12, -104), (12, -104), (26, -34), (-26, -34)])
    s += path(beam, c)
    s += path(P([(-6, -96), (6, -96), (14, -44), (-14, -44)]), "w2" if mode != "hot" else "h")
    s += circ(0, -120, 22, c)
    upper = "M-44 0 A44 44 0 0 1 44 0 L52 0 L52 -18 L38 -18 L38 -30 L-38 -30 L-38 -18 L-52 -18 L-52 0Z"
    s += path("M-44 0 A44 44 0 0 1 44 0Z", c) + rect(-52, -18, 14, 18, c) + rect(38, -18, 14, 18, c)
    s += '<g transform="translate(0 %s)">' % n(gap) + path("M-44 0 A44 44 0 0 0 44 0Z", c) + rect(-52, 0, 14, 22, c) + rect(38, 0, 14, 22, c) + "</g>"
    if mode != "hot":
        s += circ(0, -120, 12, "bg") + circ(0, 0, 29, "bg")
        if gap:
            s += rect(-30, 0, 60, gap, "void")
        s += hid("M-45 -18 L-45 22 M45 -18 L45 22")
    s += cl(0, -150, 0, 56)
    if split and not gap:
        s += line(-52, 0, 52, 0, "o")
    return s


ROD_F = {"big": "M-29 0 A29 29 0 1 0 29 0 A29 29 0 1 0 -29 0", "small": "M-12 -120 A12 12 0 1 0 12 -120 A12 12 0 1 0 -12 -120",
         "bolt": "M-45 -18 L-45 22 M45 -18 L45 22", "split": "M-52 0 L-29 0 M29 0 L52 0"}


def rod_detail():
    pl = Pl(170, 200, 1.2)
    s = shadow(170, 272, 80, 8) + pl.g(rod_front(split=True))
    notes = [("大端部", "クランクピンに付く。破断分割したキャップとボルト締結"), ("小端部", "ピストンピンが通る。ブッシュ圧入の場合も"),
             ("I形ビーム", "軽量で曲げに強い断面"), ("破断面", "割った凹凸で位置決め（ピン不要）"), ("コンロッドボルト", "塑性域角度締めで締結")]
    s += bal(*pl(30, 20), 290, 250, 1) + bal(*pl(10, -128), 280, 40, 2) + bal(*pl(8, -70), 290, 110, 3)
    s += bal(*pl(-40, 0), 60, 170, 4) + bal(*pl(-45, 12), 60, 240, 5)
    s += rect(340, 110, 130, 110, "m", 4) + text(405, 126, "ビーム断面", "middle", "sm")
    s += path(P([(380, 140), (430, 140), (430, 150), (412, 150), (412, 182), (430, 182), (430, 192), (380, 192), (380, 182), (398, 182), (398, 150), (380, 150)]), "cut")
    return s, notes


def rod_ops():
    ops = []
    s = title("棒鋼を加熱し、コンロッド形状に型鍛造")
    s += rect(120, 36, 240, 40, "t") + rect(120, 240, 240, 40, "t")
    pl = Pl(240, 190, 0.95)
    s += pl.g(path("M-70 -150 L70 -150 L70 40 L-70 40Z", "flash") + rod_front("hot"))
    s += arrow(400, 40, 400, 110, "加圧", 392, 126, "end") + tol(40, 290, "1,600〜2,500t")
    ops.append(s)
    s = title("バリを抜き、ショットで整え、蛍光磁粉で割れを確認")
    pl = Pl(200, 200, 0.95)
    s += pl.g(path("M-70 -150 L70 -150 L70 40 L-70 40Z", "w3") + rod_front() + path("M-66 -146 L66 -146 L66 36 L-66 36Z", "cutframe"))
    for i in range(12):
        s += circ(330 + (i % 4) * 14, 90 + (i // 4) * 16, 2.2, "shot")
    s += circ(420, 60, 22, "m2") + text(420, 100, "ショット", "middle") + lead(*pl(-66, -60), 60, 250, "バリ", "start")
    ops.append(s)
    s = title("大端・小端の両面を対向砥石で同時研削（厚さ・平行度）")
    s += rect(150, 40, 60, 230, "gw", 6) + rect(270, 40, 60, 230, "gw", 6)
    s += rect(212, 60, 56, 70, "w", 4) + rect(214, 150, 52, 90, "w", 4)
    s += line(212, 60, 212, 240, "mf") + line(268, 60, 268, 240, "mf")
    s += arrow(240, 290, 240, 250, None) + text(250, 286, "通過・送り", "start", "al")
    s += text(180, 32, "砥石", "middle") + text(300, 32, "砥石", "middle") + tol(20, 150, "厚さ・平行度")
    ops.append(s)
    s = title("大端・小端穴を荒加工し、ボルト穴とねじを加工")
    pl = Pl(200, 200, 0.95)
    s += pl.g(rod_front(split=True))
    s += pl.g(mf(ROD_F["big"]) + mf(ROD_F["small"]) + mf(ROD_F["bolt"]))
    s += tool("drill", *pl(-45, 22), -90, 60, 8, spindle=False, rotarr=False, feed=False)
    for (px, py, r) in ((0, 0, 29), (0, -120, 12)):
        x, y = pl(px, py)
        s += rot(x, y, r + 10, r + 10, 200, 320)
    s += lead(*pl(29, 0), 330, 200, "大端穴（ボーリング）") + lead(*pl(12, -120), 330, 70, "小端穴") + lead(*pl(45, 10), 330, 250, "ボルト穴・ねじ")
    ops.append(s)
    s = title("大端部にレーザでノッチを入れ、くさびで破断してキャップを分ける")
    pl = Pl(200, 190, 1.0)
    s += pl.g(rod_front(gap=10))
    s += pl.g(path("M-52 0 L-29 0 M29 0 L52 0", "crack"))
    x, y = pl(0, 5)
    s += poly([(x - 16, y - 20), (x + 16, y - 20), (x, y + 20)], "t") + arrow(x, y - 80, x, y - 28, "くさび", x + 10, y - 60)
    s += line(pl(-29, 0)[0] - 30, y - 50, pl(-29, 0)[0], y - 4, "beam") + text(pl(-29, 0)[0] - 36, y - 56, "レーザノッチ", "end", "al")
    s += arrow(x + 90, y - 10, x + 90, y + 30, None) + text(x + 98, y + 16, "分離", "start", "al")
    s += tol(300, 270, "破断面の凹凸で再組付けの位置が決まる")
    ops.append(s)
    s = title("キャップを締結し、大端・小端穴をホーニングで仕上げ")
    pl = Pl(200, 190, 1.0)
    s += pl.g(rod_front(split=True))
    s += pl.g(mf(ROD_F["big"]))
    for sx in (-45, 45):
        s += tool("tap", *pl(sx, 22), -90, 50, 12, spindle=False, rotarr=False, feed=False)
    x, y = pl(0, 0)
    s += rect(x - 26, y - 6, 52, 12, "m2", 3) + rect(x - 30, y - 5, 6, 10, "gw") + rect(x + 24, y - 5, 6, 10, "gw")
    s += rot(x, y, 36, 36, 200, 320)
    s += lead(*pl(52, 20), 330, 260, "ナットランナーで塑性域角度締め") + tol(330, 60, "真円度・中心間距離") + tol(330, 76, "大小端の平行度・ねじれ")
    ops.append(s)
    s = title("大端・小端の重量を測ってランク分け（バランス取りの代わり）")
    pl = Pl(160, 180, 0.9)
    s += '<g transform="rotate(90 200 150)">' + pl.g(rod_front(split=True)) + "</g>"
    s += rect(90, 200, 60, 20, "m2") + rect(250, 200, 60, 20, "m2") + rect(60, 220, 280, 16, "m3")
    s += rect(360, 120, 90, 60, "m", 4) + text(405, 146, "大端 g", "middle") + text(405, 166, "小端 g", "middle")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ PISTON
def piston_sec(mode="w", carrier=False):
    c = "cut" if mode == "w" else "h"
    v = "w" if mode == "w" else "h"
    s = rect(0, 0, 45, 110, v)
    for y in (8, 16, 24):
        s += line(0, y + 2, 45, y + 2, "o thin")
    s += circ(22, 58, 9, "bg")
    s += path(P([(-45, 0), (0, 0), (0, 14), (-37, 14), (-37, 44), (-17, 44), (-17, 72), (-37, 72), (-37, 110), (-45, 110)]), c)
    for y in (7, 15, 23):
        s += rect(-45, y, 5, 3.5, "void")
    s += rect(-37, 52, 20, 12, "void")
    if carrier:
        s += rect(-45, 5, 7, 8, "w3")
    s += cl(0, -8, 0, 118) + cl(-50, 58, 50, 58)
    return s


PIS_F = {"od": "M-45 0 L-45 110 M45 0 L45 110", "pin": "M-37 52 L-17 52 M-37 64 L-17 64", "grooves": "M-45 7 L-40 7 L-40 10.5 L-45 10.5 M-45 15 L-40 15 L-40 18.5 L-45 18.5 M-45 23 L-40 23 L-40 26.5 L-45 26.5",
         "skirt": "M45 36 L45 110", "crown": "M-45 0 L45 0"}


def piston_detail():
    pl = Pl(150, 60, 1.7)
    s = shadow(150, 262, 90, 8) + pl.g(piston_sec(carrier=True))
    notes = [("冠面（クラウン）", "燃焼圧を受ける面。バルブリセスを持つ"), ("リング溝", "3本。溝幅・側面平行度・粗さを管理"),
             ("耐摩環", "トップリング溝のニレジスト（ディーゼル・高負荷）"), ("ピン穴", "ピストンピンが通る。真円度1〜2μm"),
             ("スカート", "楕円・樽形のプロフィール。固体潤滑コート")]
    s += bal(*pl(20, 0), 320, 60, 1) + bal(*pl(-45, 17), 40, 80, 2) + bal(*pl(-41, 9), 40, 40, 3)
    s += bal(*pl(-27, 58), 40, 200, 4) + bal(*pl(45, 90), 330, 230, 5)
    s += rect(340, 100, 130, 110, "m", 4) + text(405, 116, "スカート断面（誇張）", "middle", "sm")
    s += ell(405, 160, 44, 34, "w") + circ(405, 160, 39, "o dash")
    s += text(405, 204, "長径／短径 数十〜百数十μm", "middle", "sm")
    return s, notes


def piston_ops():
    ops = []
    s = title("金型に注湯して鋳造（トップ溝には耐摩環を鋳ぐるみ）")
    s += rect(120, 40, 120, 220, "m2") + rect(240, 40, 120, 220, "m3")
    pl = Pl(240, 70, 1.6)
    s += pl.g(piston_sec("hot", carrier=True))
    s += path("M60 30 L110 30 L104 60 L66 60Z", "m2") + path("M104 40 Q150 30 180 70", "pour")
    s += lead(*pl(-41, 9), 60, 250, "耐摩環（ニレジスト）", "start")
    ops.append(s)
    s = title("溶体化・時効（T6・T7）で強度と寸法安定性を出す")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin")
    for i in range(4):
        s += Pl(100 + i * 90, 100, 0.8).g(piston_sec())
    ops.append(s)
    s = title("外径・冠面・内側を粗加工")
    pl = Pl(260, 90, 1.5)
    s += rect(pl(-60, 0)[0] - 10, 70, 60, 200, "m2", 4) + pl.g(piston_sec())
    s += pl.g(mf(PIS_F["od"].split(" M")[1] if False else "M45 0 L45 110"))
    s += tool("turn", *pl(45, 30), 180, 70, 18, spindle=False, rotarr=False, feedlab="送り")
    s += rot(*pl(0, 80), 70, 14, 20, 160) + text(*pl(0, 132), "回転", "middle", "al") if False else rot(*pl(0, 100), 70, 14, 20, 160)
    ops.append(s)
    s = title("ダイヤモンド工具でピン穴を精密ボーリング")
    pl = Pl(200, 70, 1.6)
    s += pl.g(piston_sec()) + pl.g(mf(PIS_F["pin"]))
    x, y = pl(-17, 58)
    s += tool("boring", pl(50, 58)[0], y, 180, 200, 12, spindle=True, feedlab="送り")
    s += tol(40, 270, "穴径・真円度1〜2μm・穴形状（ラッパ形状）")
    ops.append(s)
    s = title("主軸回転に同期して刃物を高速往復し、楕円・樽形のスカートを削る")
    pl = Pl(180, 70, 1.6)
    s += pl.g(piston_sec()) + pl.g(mf(PIS_F["skirt"]))
    x, y = pl(45, 80)
    s += tool("turn", x + 1, y, 180, 70, 18, spindle=False, rotarr=False, feed=False)
    s += arrow(x + 90, y - 30, x + 90, y + 30, None) + arrow(x + 40, y + 50, x + 80, y + 50, None, both=True) + text(x + 60, y + 70, "高速往復", "middle", "al")
    s += ell(420, 110, 36, 28, "w") + circ(420, 110, 32, "o dash") + text(420, 156, "断面：楕円", "middle", "sm")
    ops.append(s)
    s = title("ピストンリング溝を溝入れ加工")
    pl = Pl(200, 60, 1.7)
    s += pl.g(piston_sec()) + pl.g(mf(PIS_F["grooves"]))
    x, y = pl(-45, 16)
    s += tool("turn", x - 1, y, 0, 70, 12, spindle=False, rotarr=False, feed=False)
    s += tol(40, 270, "溝幅・側面平行度・側面粗さ")
    ops.append(s)
    s = title("スカートに固体潤滑樹脂を印刷し、トップ溝を硬質アルマイト")
    pl = Pl(200, 70, 1.6)
    s += pl.g(piston_sec())
    s += pl.g(path("M45 40 L45 108", "coat") + path("M-45 7 L-40 7 L-40 10.5 L-45 10.5", "coat"))
    x, y = pl(45, 74)
    s += rect(x + 10, y - 60, 14, 120, "mesh") + poly([(x + 30, y - 10), (x + 50, y - 20), (x + 50, y + 20)], "t")
    s += text(x + 60, y - 70, "スクリーン印刷", "start", "al") + lead(*pl(-43, 9), 60, 40, "硬質アルマイト", "start")
    ops.append(s)
    s = title("外径・ピン穴を全数測定し、重量でランク分け")
    pl = Pl(160, 70, 1.6)
    s += pl.g(piston_sec())
    x, y = pl(0, 80)
    s += rect(x - 90, y - 10, 16, 20, "m2") + rect(x + 74, y - 10, 16, 20, "m2") + circ(x - 76, y, 2.5, "fdot") + circ(x + 76, y, 2.5, "fdot")
    s += rect(330, 200, 110, 20, "m2") + rect(350, 170, 70, 30, "m", 4) + text(385, 190, "g", "middle")
    s += text(x, 270, "エアマイクロで外径ランク", "middle")
    ops.append(s)
    return [fin(x) for x in ops]
