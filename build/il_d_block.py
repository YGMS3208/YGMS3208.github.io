from il_detail import *

# ================================================================ CYLINDER BLOCK
BORES = (55, 125, 195, 265)


def block_side(flags=()):
    """elevation of block (intake side). local ~ 320 x 200. deck y=20, pan y=170, crank axis y=150."""
    f = set(flags)
    s = ""
    body = P([(10, 20), (310, 20), (310, 130), (304, 170), (16, 170), (10, 130)])
    if "cast" in f:
        # gates & overflows
        s += rect(138, 170, 44, 14, "w3") + rect(96, 184, 128, 9, "w3")
        for x in (30, 100, 170, 240, 290):
            s += rect(x - 7, 7, 14, 13, "w3", 3)
    s += path(body, "w" if "cast" not in f else "w2")
    s += line(10, 130, 310, 130, "o thin")
    for cx in BORES:
        s += hid("M%s 20 L%s 112 M%s 20 L%s 112" % (n(cx - 30), n(cx - 30), n(cx + 30), n(cx + 30)))
    s += cl(0, 150, 320, 150)
    if "gallery" in f:
        s += hid("M10 120 L310 120")
    for x in (18, 88, 158, 228, 302):   # bulkheads (hidden)
        s += hid("M%s 130 L%s 170" % (n(x - 6), n(x - 6))) if False else ""
    s += circ(160, 70, 14, "w2") + circ(160, 70, 5, "bg")
    s += circ(60, 96, 9, "w2")
    if "rough" in f or "cast" in f:
        s += roughen([(10, 20), (310, 20)]) + roughen([(16, 170), (304, 170)]) + roughen([(10, 30), (10, 128)])
    if "pan" in f:
        s += line(16, 170, 304, 170, "done")
    if "datum" in f:
        s += hid("M30 170 L30 152 M290 170 L290 152")
    if "deck" in f:
        s += line(10, 20, 310, 20, "done")
    if "threads" in f:
        for cx in BORES:
            for dx in (-36, 36):
                s += hid("M%s 20 L%s 58" % (n(cx + dx), n(cx + dx)))
    if "journal" in f:
        for x in (18, 88, 158, 228, 302):
            s += circ(x, 150, 3, "o")
    return s


FEAT_SIDE = {
    "deck": "M10 20 L310 20", "pan": "M16 170 L304 170", "gallery": "M10 120 L310 120",
    "datum": "M30 170 L30 152 M290 170 L290 152",
    "journal": "M10 150 L26 150 M80 150 L96 150 M150 150 L166 150 M220 150 L236 150 M294 150 L310 150",
    "threads": " ".join("M%s 20 L%s 58" % (n(cx + dx), n(cx + dx)) for cx in BORES for dx in (-36, 36)),
}


def block_end(mode="cut", liner=True):
    """cross-section through one bore, looking along crank axis. local 220 x 205."""
    c = "cut" if mode == "cut" else "h"
    s = ""
    # bulkhead behind the section plane
    s += path(P([(40, 150), (58, 122), (162, 122), (180, 150), (180, 178), (40, 178)]), "w" if mode == "cut" else "h")
    s += rect(70, 170, 80, 26, "w3" if mode == "cut" else "h")
    s += circ(110, 170, 28, "bg")
    s += line(70, 170, 82, 170, "o") + line(138, 170, 150, 170, "o")
    for piece in ([(20, 10), (34, 10), (34, 115), (20, 115)], [(34, 92), (44, 92), (44, 115), (34, 115)], [(44, 10), (52, 10), (52, 115), (44, 115)],
                  [(168, 10), (176, 10), (176, 115), (168, 115)], [(176, 92), (186, 92), (186, 115), (176, 115)], [(186, 10), (200, 10), (200, 115), (186, 115)],
                  [(20, 115), (58, 115), (58, 122), (40, 150), (28, 196), (8, 196)], [(200, 115), (162, 115), (162, 122), (180, 150), (192, 196), (212, 196)]):
        s += path(P(piece), c)
    if liner:
        s += rect(52, 10, 6, 105, "w3" if mode == "cut" else "h") + rect(162, 10, 6, 105, "w3" if mode == "cut" else "h")
    s += circ(188, 136, 5, "bg")
    s += hid("M27 10 L27 64 M193 10 L193 64")
    s += cl(110, 0, 110, 204)
    return s


FEAT_END = {
    "deck": "M20 10 L200 10", "bore": "M58 12 L58 115 M162 12 L162 115",
    "journal": "M82 170 A28 28 0 1 0 138 170 A28 28 0 1 0 82 170", "gallery": "M183 136 A5 5 0 1 0 193 136 A5 5 0 1 0 183 136",
    "pan": "M8 196 L28 196 M192 196 L212 196", "jacket": "M34 10 L34 92 L44 92 L44 10 M176 10 L176 92 L186 92 L186 10",
    "bolt": "M27 10 L27 64 M193 10 L193 64",
}


def block_iso():
    o = Ob(30, 122, 232, 108, 112)
    s = shadow(190, 262, 170, 12)
    s += poly([o.front(0, 0), o.front(232, 0), o.front(232, 108), o.front(0, 108)], "w")
    s += poly([o.front(232, 0), o.side(112, 0), o.side(112, 108), o.front(232, 108)], "w3")
    s += poly([o.top(0, 0), o.top(232, 0), o.top(232, 112), o.top(0, 112)], "w2")
    # water jacket (stadium) + siamese barrel + bores
    def stadium(r, u0=37, u1=195, vc=56, k=18):
        pts_ = []
        for i in range(k + 1):
            a = math.pi / 2 + math.pi * i / k
            pts_.append(o.top(u0 + r * math.cos(a), vc + r * math.sin(a)))
        for i in range(k + 1):
            a = -math.pi / 2 + math.pi * i / k
            pts_.append(o.top(u1 + r * math.cos(a), vc + r * math.sin(a)))
        return pts_
    s += poly(stadium(34), "bg") + poly(stadium(28), "w2")
    for i in range(4):
        uc = 37 + i * 52.7
        s += poly(o.circle("top", uc, 56, 24), "w3") + poly(o.circle("top", uc, 56, 20.5), "bg")
    for u in (6, 63.5, 116.5, 169, 226):
        for v in (10, 102):
            s += poly(o.circle("top", u, v, 4, 16), "bg")
    # front face details
    s += line(*o.front(0, 64), *o.front(232, 64), "o thin")
    for u in (37, 89.7, 142.4, 195):
        s += path("M%s %s L%s %s" % tuple(n(v) for v in (*o.front(u, 4), *o.front(u, 62))), "o thin")
    s += poly(o.circle("front", 118, 36, 13), "w2") + poly(o.circle("front", 118, 36, 5), "bg")
    s += poly(o.circle("front", 8, 76, 4.5, 16), "m")
    s += poly([o.front(0, 100), o.front(232, 100), o.front(232, 108), o.front(0, 108)], "w2")
    for u in range(14, 232, 28):
        s += poly(o.circle("front", u, 104, 2.2, 12), "bg")
    # rear face: crank journal bore + bolt pattern
    s += poly(o.circle("side", 56, 88, 17), "bg")
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += poly(o.circle("side", 56 + 38 * math.cos(a) * 0.9, 58 + 36 * math.sin(a) * 0.8, 3, 12), "bg")
    return s, o


def block_detail():
    s, o = block_iso()
    notes = [("ボア（シリンダ）", "内径φ80前後。真円度・円筒度は数μm、ホーニングで仕上げる"),
             ("デッキ面", "ヘッドとの合わせ面。平面度0.05mm以下・面粗さ管理"),
             ("ウォータジャケット", "ボアを囲む冷却水路（オープンデッキ）"),
             ("ヘッドボルト穴", "めねじ M10〜11。塑性域締結に耐えるねじ精度"),
             ("クランクジャーナル穴", "5か所を一直線に共加工（同軸度 数μm）"),
             ("オイルギャラリ", "全長を貫く深穴の油路（ガンドリル）"),
             ("オイルパン合わせ面", "加工の基準面、液状ガスケットのシール面"),
             ("マウント取付ボス", "エンジンマウント・補機の取付座面とねじ")]
    bx = o.top(89.7, 56)
    s += bal(bx[0] - 6, bx[1] - 4, 70, 30, 1)
    d = o.top(160, 104)
    s += bal(d[0], d[1] + 2, 150, 30, 2) if False else bal(*o.top(140, 104), 132, 36, 2)
    j = o.top(210, 20)
    s += bal(j[0], j[1], 250, 30, 3)
    b = o.top(226, 102)
    s += bal(b[0], b[1], 300, 50, 4)
    jr = o.side(56, 88)
    s += bal(jr[0] + 4, jr[1], 322, 190, 5)
    g = o.front(8, 76)
    s += bal(g[0], g[1], 16, 170, 6)
    p = o.front(150, 108)
    s += bal(p[0], p[1] - 2, 150, 262, 7)
    m = o.front(118, 36)
    s += bal(m[0] + 8, m[1] + 6, 90, 250, 8)
    # section A-A
    pl = Pl(346, 92, 0.58)
    s += rect(338, 70, 136, 170, "m", 4) + text(406, 86, "断面A-A（ボア中心）", "middle", "sm")
    s += pl.g(block_end())
    for num, (lx, ly), (bx_, by_) in ((1, (60, 70), (390, 250)), (3, (39, 50), (352, 250)), (5, (110, 142), (428, 250)),
                                       (6, (188, 136), (464, 250)), (2, (140, 10), (464, 104))):
        ax, ay = pl(lx, ly)
        s += bal(ax, ay, bx_, by_ if by_ != 250 else 258, num) if False else line(ax, ay, bx_, by_, "leadl") + circ(ax, ay, 2, "leadd") + circ(bx_, by_, 8, "bal") + text(bx_, by_ + 4, str(num), "middle", "balt")
    return s, notes


def block_ops():
    ops = []
    # OP10 melt
    s = title("地金・リターン材を溶解し、脱ガスして清浄な溶湯にする")
    s += rect(30, 90, 120, 170, "m2", 6) + rect(44, 176, 92, 70, "h") + rect(44, 104, 92, 72, "hotin")
    for x in (60, 88, 116):
        s += rect(x - 10, 60 + (x % 3) * 4, 22, 12, "w3", 2)
    s += arrow(90, 44, 90, 84, None) + text(98, 52, "地金・リターン材", "start", "al")
    s += heat(70, 170, 4, 14) + text(90, 278, "タワー溶解炉", "middle")
    s += path("M150 190 Q190 176 214 206", "pour")
    s += path(P([(200, 200), (290, 200), (282, 270), (208, 270)]), "m2") + rect(212, 214, 66, 52, "h")
    s += rect(240, 120, 10, 110, "m3") + rect(226, 226, 38, 8, "t", 2) + bubbles(245, 262, 8, 50, 40)
    s += text(245, 112, "回転脱ガス（Ar・N₂）", "middle", "al") + text(245, 290, "取鍋で溶湯処理", "middle")
    s += path(P([(360, 214), (400, 214), (396, 250), (364, 250)]), "m2") + rect(366, 224, 28, 22, "h")
    s += arrow(300, 230, 352, 230, None) + text(380, 270, "減圧凝固試験・成分分析", "middle")
    s += tol(330, 150, "溶湯温度 700〜720℃") + tol(330, 168, "水素量・介在物を管理")
    ops.append(s)
    # OP20 HPDC
    s = title("鋳鉄ライナーを金型にセットし、アルミを高速射出して鋳ぐるむ")
    s += rect(80, 40, 130, 220, "m2") + rect(210, 40, 130, 220, "m3")
    pl = Pl(100, 52, 1.0)
    s += pl.g(block_end("hot"))
    s += pl.g(rect(58, 10, 104, 110, "m") + rect(34, 10, 10, 82, "m") + rect(176, 10, 10, 82, "m"))
    s += line(210, 40, 210, 260, "o")
    s += rect(0, 234, 100, 22, "m") + rect(10, 238, 80, 14, "h")
    s += arrow(8, 280, 90, 280, "高速射出 4〜6m/s", 50, 296)
    s += arrow(470, 272, 350, 272, "型締め 2,500〜4,000t", 410, 262)
    s += text(145, 52, "固定型", "middle") + text(275, 52, "可動型", "middle")
    s += lead(*pl(55, 60), 350, 70, "鋳鉄ライナー（鋳ぐるみ）")
    s += lead(*pl(110, 90), 350, 100, "ボア部は金型（中子）")
    s += lead(*pl(39, 50), 350, 130, "水路も金型で成形")
    s += tol(350, 190, "真空ダイカストで") + tol(350, 206, "巻込みガスを低減")
    ops.append(s)
    # OP30 trim & shot
    s = title("湯口・オーバーフローを切り落とし、ショットで表面を整える")
    pl = Pl(20, 70, 0.9)
    s += pl.g(block_side(("cast",)))
    s += rect(120, 262, 100, 16, "m3") + arrow(170, 296, 170, 268, None)
    for x in (30, 100, 170, 240, 290):
        xx, yy = pl(x, 20)
        s += line(xx - 10, yy, xx + 10, yy, "cutl")
    xx, yy = pl(138, 170)
    s += line(xx - 4, yy, xx + 48, yy, "cutl")
    s += lead(*pl(290, 12), 330, 50, "オーバーフロー")
    s += lead(*pl(200, 188), 330, 250, "湯口（ランナー）")
    s += text(240, 290, "トリミング型", "start")
    s += tol(330, 140, "破線部で切断") + tol(330, 158, "→ ショットブラストで") + tol(330, 174, "酸化皮膜・バリを除去")
    ops.append(s)
    # OP40 heat treatment
    s = title("溶体化→水冷→時効（T6）で強度と寸法安定性を出す")
    for i, (x, t, cls) in enumerate(((20, "溶体化 約500℃", "hotin"), (330, "時効 約200℃", "warmin"))):
        s += rect(x, 70, 130, 150, "m2", 6) + rect(x + 10, 80, 110, 130, cls)
        for k in range(2):
            pl = Pl(x + 20, 110 + k * 50, 0.28)
            s += pl.g(block_side())
        s += text(x + 65, 244, t, "middle")
    s += tank(185, 120, 110, 100, 0.75) + Pl(200, 150, 0.26).g(block_side()) + text(240, 244, "水焼入れ", "middle")
    s += arrow(152, 150, 182, 150, None) + arrow(298, 150, 328, 150, None)
    s += tol(20, 280, "硬さ（HB）とひずみを管理。T5の場合は時効のみ")
    ops.append(s)
    # OP50 X-ray
    s = title("X線で内部の鋳巣を確認（シール面・ボア周辺を重点）")
    s += rect(20, 120, 50, 60, "m3", 4) + text(45, 200, "X線源", "middle")
    for k in range(7):
        s += line(70, 150, 380, 50 + k * 34, "ray")
    pl = Pl(160, 50, 0.95)
    s += pl.g(block_end())
    for (px, py) in ((47, 70), (49, 82), (171, 58), (40, 132)):
        x, y = pl(px, py)
        s += circ(x, y, 3, "poro")
    x, y = pl(48, 76)
    s += circ(x, y, 14, "mfring") + lead(x - 14, y, 90, 70, "鋳巣", "end")
    s += rect(380, 40, 22, 220, "m2") + text(391, 278, "検出器", "middle")
    s += rect(412, 110, 60, 80, "xim") + circ(432, 140, 4, "ximd") + text(442, 206, "透過画像", "middle", "sm")
    ops.append(s)
    # OP60 datum machining
    s = title("オイルパン面と基準穴2か所を加工（以降の全工程の基準）")
    pl = Pl(30, 44, 0.85)
    s += pl.g(block_side(("rough",)))
    s += pl.g(mf(FEAT_SIDE["pan"]) + mf(FEAT_SIDE["datum"]))
    for x in (40, 160, 280):
        s += loc(*pl(x, 20), 90)
    s += clamp(*pl(10, 80), 0) + clamp(*pl(310, 80), 180)
    s += tool("facemill", *pl(200, 172), -90, 50, 70)
    s += tool("drill", *pl(30, 172), -90, 44, 9, spindle=False, rotarr=False)
    s += lead(*pl(250, 170), 330, 250, "基準面（パン面）")
    s += lead(*pl(290, 160), 330, 220, "基準穴×2")
    s += lead(*pl(280, 20), 330, 60, "鋳肌3点で位置決め")
    s += lead(*pl(310, 80), 330, 110, "クランプ")
    s += text(20, 292, "鋳肌を基準に最初の加工面をつくる", "start", "sm")
    ops.append(s)
    # OP70 rough machining
    s = title("基準面・基準穴で位置決めし、ボア荒・穴あけ・深穴を加工")
    pl = Pl(120, 68, 1.0)
    s += pl.g(block_end())
    s += pl.g(mf(FEAT_END["bore"]) + mf(FEAT_END["gallery"]) + mf(FEAT_END["bolt"]))
    s += tool("boring", *pl(110, 100), 90, 110, 40, feedlab="送り")
    s += tool("gundrill", *pl(188, 136), 180, 110, 6, spindle=False, rotarr=False, feed=False)
    s += tool("drill", *pl(27, 64), 90, 70, 8, spindle=False, rotarr=False, feed=False)
    s += loc(*pl(18, 196), -90) + loc(*pl(202, 196), -90)
    s += lead(*pl(58, 90), 40, 120, "ボア荒加工", "end") if False else lead(*pl(58, 90), 20, 150, "ボア荒加工", "start")
    s += lead(*pl(188, 130), 400, 150, "オイルギャラリ（ガンドリル）")
    s += lead(*pl(27, 30), 20, 60, "ボルト下穴", "start")
    s += lead(*pl(110, 196), 300, 290, "パン面・基準穴で位置決め")
    ops.append(s)
    # OP80 line boring
    s = title("軸受キャップを組み付けたまま、ジャーナル穴5か所を共加工")
    pl = Pl(70, 40, 1.0)
    s += pl.g(block_side(("pan", "datum", "gallery", "journal")))
    for x in (18, 88, 158, 228, 302):
        s += pl.g(rect(x - 9, 164, 18, 14, "w3", 2))
    s += pl.g(mf(FEAT_SIDE["journal"]))
    y = pl(0, 150)[1]
    s += rect(pl(-10, 0)[0], y - 5, 330, 10, "t") + rect(pl(320, 0)[0], y - 20, 70, 40, "m2", 4)
    for x in (18, 88, 158, 228, 302):
        xx = pl(x, 0)[0]
        s += poly([(xx - 3, y - 5), (xx + 3, y - 5), (xx, y - 11)], "ins")
    s += arrow(pl(330, 0)[0], y + 34, pl(270, 0)[0], y + 34, "送り", pl(300, 0)[0], y + 50)
    s += lead(*pl(158, 170), 300, 270, "軸受キャップ（仮組み）")
    s += tol(250, 262, "同軸度 数μm〜10μm・真円度") if False else tol(20, 262, "同軸度 数μm〜10μm・真円度") + tol(20, 278, "ガイドパッド付きラインボーリングバー")
    ops.append(s)
    # OP90 finishing deck & threads
    s = title("デッキ面を正面フライスで仕上げ、ヘッドボルト穴をねじ立て")
    pl = Pl(80, 90, 1.0)
    s += pl.g(block_side(("pan", "datum", "gallery", "journal")))
    s += pl.g(mf(FEAT_SIDE["deck"]) + mf(FEAT_SIDE["threads"]))
    s += tool("facemill", *pl(190, 20), 90, 50, 90, rotlab="回転")
    s += tool("tap", *pl(19, 20), 90, 40, 8, spindle=False, rotarr=False, feed=False)
    s += loc(*pl(30, 170), -90) + loc(*pl(290, 170), -90)
    s += lead(*pl(290, 20), 400, 60, "デッキ面")
    s += lead(*pl(19, 50), 30, 290, "ヘッドボルト穴（タップ）", "start")
    s += tol(330, 290, "平面度0.05mm以下・面粗さ")
    ops.append(s)
    # OP100 bore thermal spray
    s = title("ライナーレス仕様：ボア内面に鉄系の溶射皮膜をつける")
    pl = Pl(130, 70, 1.0)
    s += pl.g(block_end(liner=False))
    s += pl.g(path(FEAT_END["bore"], "coat"))
    x, y = pl(110, 60)
    s += tool("spray", x, y, 90, 110, 16, feed=False, rotlab="回転")
    s += spray_cone(x, y, 180, 26, 50, "hl") + spray_cone(x, y, 0, 26, 50, "hl")
    s += arrow(x + 40, y - 70, x + 40, y + 20, None, both=True) + text(x + 48, y - 20, "上下に移動", "start", "al")
    s += lead(*pl(58, 100), 30, 160, "溶射皮膜（数百μm）", "start")
    s += tol(350, 230, "密着強度・気孔率") + tol(350, 246, "→ ホーニングで仕上げ")
    ops.append(s)
    # OP110 honing
    s = title("ボアをホーニングで仕上げ、油を保持するクロスハッチを付ける")
    pl = Pl(130, 70, 1.0)
    s += pl.g(block_end())
    s += pl.g(mf(FEAT_END["bore"]))
    for k in range(8):
        y0 = 18 + k * 12
        s += pl.g(line(60, y0, 72, y0 + 8, "hatchx") + line(60, y0 + 8, 72, y0, "hatchx") + line(148, y0, 160, y0 + 8, "hatchx") + line(148, y0 + 8, 160, y0, "hatchx"))
    x, y = pl(110, 80)
    s += tool("hone", x, y, 90, 150, 98, feed=False, rotlab="回転")
    s += arrow(x + 70, y - 110, x + 70, y - 40, None, both=True) + text(x + 78, y - 70, "往復", "start", "al")
    s += lead(*pl(58, 40), 30, 110, "クロスハッチ 40〜60°", "start")
    s += tol(20, 240, "荒→中→仕上げの3段") + tol(20, 256, "真円度・円筒度 数μm") + tol(20, 272, "プラトー粗さ（Rk・Rpk）")
    s += text(400, 280, "エアゲージで全数計測", "middle", "sm")
    ops.append(s)
    # OP120 washing & deburring
    s = title("交差穴のバリを高圧水で除去し、切粉・油を洗い流す")
    pl = Pl(60, 70, 1.0)
    s += pl.g(block_side(("pan", "datum", "gallery", "journal", "deck", "threads")))
    s += pl.g(path(FEAT_SIDE["gallery"], "jetl"))
    s += tool("nozzle", *pl(312, 120), 180, 70, 10, spindle=False, rotarr=False, feed=False)
    for x in (60, 160, 260):
        xx, yy = pl(x, 0)
        s += nozzle(xx, yy - 6, 90, 20, 8) + drops(xx, yy - 6, 4, 34, 26, 90)
    s += lead(*pl(312, 120), 420, 250, "高圧水（数十MPa）", "middle") if False else lead(*pl(330, 120), 420, 200, "高圧水ノズル", "middle")
    s += tol(40, 280, "残留異物の重量・最大粒径を管理（ISO 16232）")
    ops.append(s)
    # OP130 leak test
    s = title("水路・油路を密閉してエアを加圧し、差圧で漏れを検出")
    pl = Pl(130, 70, 1.0)
    s += pl.g(block_end())
    s += pl.g(path(FEAT_END["jacket"], "pres") + path(FEAT_END["gallery"], "pres"))
    s += pl.g(rect(14, 2, 40, 10, "m3") + rect(166, 2, 40, 10, "m3"))
    x, y = pl(200, 136)
    s += line(x, y, x + 90, y, "cable") + circ(x + 108, y - 20, 22, "m") + line(x + 108, y - 20, x + 118, y - 32, "a")
    s += text(x + 108, y + 20, "差圧計", "middle")
    s += lead(*pl(39, 50), 30, 100, "ウォータジャケット", "start") + lead(*pl(188, 136), 380, 260, "オイルギャラリ")
    s += text(*pl(110, -6), "シール治具", "middle") if False else text(pl(110, 0)[0], pl(0, 0)[1] - 8, "シール治具で密閉", "middle", "sm")
    s += tol(20, 260, "リーク量 cc/min で判定") + tol(20, 276, "温度変化による偽不良に注意")
    ops.append(s)
    # OP140 final inspection
    s = title("三次元測定機で全寸法を抜取測定し、2次元コードで履歴を残す")
    pl = Pl(80, 100, 0.95)
    s += rect(40, 280, 400, 12, "m2") + rect(50, 40, 16, 240, "m") + rect(414, 40, 16, 240, "m") + rect(40, 30, 400, 16, "m3")
    s += pl.g(block_side(("pan", "datum", "gallery", "journal", "deck", "threads")))
    x, y = pl(125, 20)
    s += rect(x - 12, 46, 24, y - 70, "m2") + line(x, y - 24, x, y - 4, "o") + circ(x, y - 2, 4, "t")
    xx, yy = pl(240, 90)
    for i in range(4):
        for j in range(4):
            if (i * 3 + j) % 2 == 0:
                s += rect(xx + i * 5, yy + j * 5, 5, 5, "d")
    s += lead(xx + 20, yy + 10, 400, 150, "2次元コード")
    s += tol(250, 70, "ボア位置・デッキ高さ・ジャーナル位置")
    ops.append(s)
    return [fin(x) for x in ops]
