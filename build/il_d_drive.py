from il_detail import *

# ================================================================ TRANSMISSION GEAR
GS = Rev([(12, 36), (36, 72), (12, 36)], bore=[(0, 60, 20)], teeth=[(12, 48)])


def gear_sec(hot=False, case=False, blank=False):
    rv = Rev([(12, 36), (36, 72 if not blank else 74), (12, 36)], bore=[(0, 60, 20)], teeth=() if blank else [(12, 48)])
    s = rv.svg(hot=hot)
    if not blank and not hot:
        for x in range(2, 58, 4):
            s += line(x, -20, x + 2, -23, "o thin")
    if case:
        s += rect(12, -72, 36, 7, "hotband") + rect(12, 65, 36, 7, "hotband")
    return s


GEAR_F = {"od": "M12 -72 L48 -72 M12 72 L48 72", "face": "M12 -72 L12 -36 L0 -36 L0 -20 M48 -72 L48 -36 L60 -36 L60 -20",
          "bore": "M0 -20 L60 -20 M0 20 L60 20", "teeth": "M12 -72 L48 -72 M12 72 L48 72"}


def gear_front(cx, cy, k=1.0, teeth=True, cls="w", partial=None):
    import il_gear as GE
    cam = GE.Cam(cx, cy, 0, 62, k)
    return GE.gear3(cam, (0, 0, -18), (0, 0, 1), 28, 69, 36, cls, helix=20, spline_bore=(16, 21, 17.5))


def gear_detail():
    import il_gear as GE
    cam = GE.Cam(150, 158, 0, 50, 1.02)
    s = GE.gear3(cam, (0, 0, -20), (0, 0, 1), 30, 96, 40, "w", helix=20, spline_bore=(18, 30, 25))
    cx, cy = cam.xy((0, 0, 20))
    s += '<ellipse class="thin o" cx="%s" cy="%s" rx="%s" ry="%s"/>' % (n(cx), n(cy), n(62 * 1.02), n(62 * 1.02 * cam.se))
    pl = Pl(330, 150, 1.4)
    s += rect(300, 34, 150, 232, "m", 4) + text(375, 50, "断面", "middle", "sm")
    s += pl.g(gear_sec())
    notes = [("歯（歯面）", "はすば歯。歯形・歯すじ誤差はJIS N4〜5級、研削・ホーニング仕上げ"),
             ("歯底・歯元", "曲げ疲労の起点。浸炭＋ショットピーニングで強化"),
             ("内径スプライン", "シャフトと結合。オーバーピン寸法を管理"),
             ("端面", "歯切り・研削の基準面。振れを管理"),
             ("浸炭硬化層", "有効硬化層0.6〜1.0mm、表面HRC58〜62")]
    a1 = cam.xy((96 * 0.72, -96 * 0.72, 20))
    a2 = cam.xy((-98 * 0.99, 96 * 0.1, 0))
    a3 = cam.xy((0, -27, 20))
    s += bal(a1[0], a1[1], 262, 64, 1)
    s += bal(a2[0], a2[1], 26, 250, 2)
    s += bal(a3[0], a3[1], 196, 272, 3)
    s += bal(*pl(48, -50), 440, 80, 4)
    s += bal(*pl(30, 68), 440, 250, 5)
    s += pl.g(rect(12, 65, 36, 7, "hotband"))
    return s, notes


def _peen_teeth():
    import il_gear as GE
    z, m = 40, 22.0
    rp = z * m / 2
    cx, cy = 240, 110 + rp
    pts = GE.gear_outline(z, rp, phase=-math.pi / 2)
    step = 2 * math.pi / z
    lo, hi = -math.pi / 2 - step * 2.5, -math.pi / 2 + step * 2.5
    sel = [(u, v, f) for u, v, f in pts if lo <= math.atan2(v, u) <= hi]
    sel.sort(key=lambda q: math.atan2(q[1], q[0]))
    rb = rp - 3.0 * m
    a0, a1 = math.atan2(sel[0][1], sel[0][0]), math.atan2(sel[-1][1], sel[-1][0])
    body = [(cx + u, cy + v) for u, v, f in sel]
    body += [(cx + rb * math.cos(a1 - k * (a1 - a0) / 16), cy + rb * math.sin(a1 - k * (a1 - a0) / 16)) for k in range(17)]
    out = path(P(body), "w")
    # root fillet highlight (feature 3 = fillet + root)
    segs, cur = [], []
    for u, v, f in sel:
        if f % 4 == 3:
            cur.append((cx + u, cy + v))
        elif cur:
            segs.append(cur); cur = []
    if cur:
        segs.append(cur)
    for sg in segs:
        if len(sg) > 1:
            out += path(P(sg, False), "mf")
    # compressive layer band just under the root surface
    return out, segs


def gear_ops():
    import il_gscene as GS
    import il_pictos_gear as PG
    ops = []
    s = title("棒鋼を加熱して、ギヤブランクに型鍛造")
    s += rect(60, 90, 50, 70, "h", 4) + arrow(120, 125, 160, 125, None) + heat(70, 84, 3, 14)
    s += rect(190, 36, 250, 44, "t") + rect(190, 196, 250, 44, "t")
    pl = Pl(290, 138, 0.8)
    s += '<g transform="translate(315 138) rotate(90)">' + '<g transform="scale(0.8) translate(-30 0)">' + gear_sec(hot=True, blank=True) + "</g></g>"
    s += arrow(460, 40, 460, 110, "加圧", 452, 126, "end") + text(85, 186, "加熱ビレット", "middle")
    ops.append(s)
    s = title("被削性と熱処理ひずみの安定のため、等温焼鈍で組織を整える")
    s += rect(40, 70, 400, 130, "m2", 6) + rect(50, 80, 380, 110, "hotin") + conveyor(20, 180, 440)
    for i in range(6):
        s += rect(60 + i * 64, 150, 44, 30, "w", 3)
    s += tol(40, 240, "硬さ・フェライト＋パーライト組織の均一性")
    ops.append(s)
    s = title("内径・端面・外径を旋削し、歯切りの基準をつくる")
    pl = Pl(180, 150, 1.4)
    s += chuck(*pl(0, 0), 110) + pl.g(gear_sec(blank=True)) + pl.g(mf(GEAR_F["bore"].split(" M")[0]) + mf("M60 -36 L60 -20 M48 -74 L48 -36 L60 -36 M12 -74 L48 -74"))
    s += tool("turn", *pl(30, -74), 90, 60, 18, spindle=False, rotarr=False, feedlab="送り")
    s += tool("boring", *pl(60, -20), 180, 110, 12, spindle=False, rotarr=False, feed=False)
    s += lead(*pl(48, -60), 380, 200, "端面振れ（歯切りの基準）") + tol(40, 290, "2主軸対向旋盤・ガントリーローダで自動化")
    ops.append(s)
    s = title("ホブとギヤを同期回転させ、歯を創成（ホブ切り）")
    s += GS.sc_hobbing(196, 150, 1.0)
    s += tol(300, 290, "ドライカット・高速ホブ")
    ops.append(s)
    s = title("歯端のエッジを面取りし、バリを除く")
    s += GS.sc_chamfer(188, 160, 1.0)
    s += tol(24, 290, "浸炭時の過剰浸炭・打痕を防ぐ（C0.3〜0.5程度）")
    ops.append(s)
    s = title("熱処理前に歯面を薄く削って仕上げ、クラウニングを付ける")
    s += GS.sc_shaving(160, 172, 1.0)
    s += tol(24, 290, "軸交差角をつけて噛み合わせ、熱処理ひずみを見込んだ形状に")
    ops.append(s)
    s = title("内径スプラインをブローチで加工")
    pl = Pl(210, 150, 1.4)
    s += pl.g(gear_sec()) + pl.g(mf(GEAR_F["bore"]))
    s += PG.broach_bar(12, 462, 150, 17, 3, 10, 10)
    s += rect(462, 142, 14, 16, "m3")
    s += arrow(380, 272, 460, 272, "引き抜き", 420, 264)
    cx, cy = 400, 74
    import il_gear as GE
    s += circ(cx, cy, 40, "w") + path(GE.outline_d(GE.spline_outline(20, 26, 20.5), cx, cy), "void") + path(GE.outline_d(GE.spline_outline(20, 26, 20.5), cx, cy), "mfo")
    s += text(cx - 50, cy + 4, "加工後の内スプライン", "end", "sm") + tol(20, 290, "オーバーピン寸法・ねじれ")
    ops.append(s)
    s = title("浸炭焼入れで歯の表面だけを硬くする（930℃前後）")
    pl = Pl(80, 150, 1.4)
    s += pl.g(gear_sec(case=True))
    s += rect(260, 60, 190, 170, "m", 4) + text(355, 78, "硬さ分布（イメージ）", "middle", "sm")
    s += line(280, 210, 430, 210, "o") + line(280, 90, 280, 210, "o")
    s += path("M282 100 L320 102 Q350 110 370 160 L430 180", "a") + line(280, 150, 430, 150, "o thin dash")
    s += text(282, 226, "表面", "start", "sm") + text(430, 226, "深さ", "end", "sm") + text(350, 144, "有効硬化層", "start", "sm")
    s += lead(*pl(30, -68), 160, 40, "浸炭層（歯部）", "start")
    s += tol(20, 280, "表面HRC58〜62・有効硬化層・熱処理ひずみ")
    ops.append(s)
    s = title("歯元に投射材を打ち付け、圧縮残留応力で曲げ疲労強度を上げる")
    body, segs = _peen_teeth()
    s += body
    for i in range(34):
        x = 60 + (i * 37) % 360
        y = 40 + (i * 23) % 62
        s += circ(x, y, 2.6, "shot")
    for x in (126, 236, 346):
        s += arrow(x, 42, x + 10, 96, None)
    if segs:
        r0 = segs[len(segs) // 2]
        mx, my = r0[len(r0) // 2]
        s += lead(mx, my + 2, 330, 250, "歯元R（圧縮残留応力を付与）", "start")
    s += tol(20, 290, "カバレージ・アークハイト")
    ops.append(s)
    s = title("歯面を基準にチャックし、内径と端面を研削")
    pl = Pl(160, 150, 1.4)
    s += pl.g(gear_sec()) + pl.g(mf(GEAR_F["bore"].split(" M")[0]) + mf("M60 -36 L60 -20"))
    for y in (-74, 74):
        s += circ(*pl(30, y + (6 if y < 0 else -6)), 6, "m3")
    x, y = pl(30, -12)
    s += rect(x, y - 4, 230, 8, "m3") + circ(x, y, 12, "gw")
    s += lead(*pl(30, -80), 60, 40, "ピッチ円チャック（歯溝にピン）", "start")
    s += tol(300, 280, "内径と歯面の同軸度・端面振れ")
    ops.append(s)
    s = title("ねじ状砥石で歯面を連続創成研削（歯形・歯すじを修整）")
    s += GS.sc_gear_grind(180, 150, 1.0)
    s += chart(352, 40, 116, 64, "profile") + text(410, 118, "歯形・歯すじ誤差", "middle", "sm")
    ops.append(s)
    s = title("洗浄後、マスタギヤと噛み合わせて騒音・打痕を全数判定")
    s += GS.sc_mesh(166, 170, 1.0)
    s += chart(330, 196, 140, 64, "noise") + text(400, 276, "かみあい誤差・騒音", "middle", "sm")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ SHAFT
SH = Rev([(46, 11), (30, 15), (16, 20), (36, 30), (52, 18), (12, 22), (60, 14), (28, 10)], spline=[(4, 44)], teeth=[(92, 128)])


def shaft_detail():
    pl = Pl(40, 150, 1.4)
    s = shadow(240, 240, 190, 8) + pl.g(SH.svg())
    notes = [("スプライン", "転造で成形。ギヤ・クラッチと結合"), ("一体ギヤ", "軸と一体の歯車。ホブ切り→研削"),
             ("軸受部", "玉軸受・針状ころが付く。径公差数μm"), ("段付き端面", "ギヤ・軸受の位置決め面"), ("油穴", "軸心からギヤへの潤滑油路")]
    s += bal(*pl(20, -11), 60, 60, 1) + bal(*pl(110, -30), 180, 50, 2) + bal(*pl(80, 15), 140, 250, 3)
    s += bal(*pl(92, -20), 120, 40, 4) + pl.g(hid("M0 0 L220 0")) + bal(*pl(200, 0), 340, 250, 5)
    return s, notes


def shaft_ops():
    ops = []
    s = title("段付き形状を冷間鍛造で押し出し、取り代を減らす")
    s += rect(190, 30, 100, 30, "m3") + rect(214, 60, 52, 70, "t")
    s += path(P([(150, 130), (214, 130), (214, 200), (226, 200), (226, 280), (254, 280), (254, 200), (266, 200), (266, 130), (330, 130), (330, 290), (150, 290)]), "m2")
    s += rect(214, 130, 52, 70, "w") + rect(226, 200, 28, 76, "w")
    s += arrow(320, 40, 320, 110, None) + text(328, 80, "加圧", "start", "al") + text(100, 200, "常温で成形", "middle")
    ops.append(s)
    pl = Pl(80, 150, 1.4)
    s = title("外径・端面・溝を旋削し、センタ穴を加工")
    s += chuck(*pl(0, 0), 30) + pl.g(SH.svg()) + center(*pl(SH.L, 0), True)
    s += pl.g(mf(SH.od(76, 92) + " " + SH.od(128, 180)))
    s += tool("turn", *pl(150, -18), 90, 60, 16, spindle=False, rotarr=False, feedlab="送り")
    s += tol(40, 280, "同軸度・振れ")
    ops.append(s)
    s = title("ラックダイス（または丸ダイス）でスプラインを転造")
    import il_gscene as GS
    s += GS.sc_spline_roll(236, 150, 1.0)
    s += tol(24, 290, "オーバーピン寸法・歯すじ。切削より強い（繊維状組織が切れない）")
    ops.append(s)
    s = title("一体ギヤ部をホブ切り")
    s += GS.sc_hobbing(196, 164, 1.0, z=22, rp=66, width=56, shaft=(15, 60, 46), helix=24, hr=22, L=170)
    s += tol(300, 290, "長物対応ホブ盤（心押し支持）")
    ops.append(s)
    s = title("浸炭焼入れまたは高周波焼入れで表面を硬化")
    pl = Pl(80, 150, 1.4)
    s += induction_on(SH, pl, 128, 180, "高周波コイル（移動焼入れ）")
    s += tol(40, 280, "硬化層深さ・曲がり")
    ops.append(s)
    s = title("軸受部・端面をアンギュラ研削、ギヤ部を歯面研削")
    pl = Pl(80, 170, 1.4)
    s += grind(SH, pl, 128, 180, 44)
    s += tol(40, 290, "軸受部径（数μm）・振れ。インプロセスゲージで定寸")
    ops.append(s)
    s = title("軸心の油穴をガンドリルで加工し、形状を全数測定")
    pl = Pl(80, 170, 1.4)
    s += pl.g(SH.svg()) + pl.g(path("M0 0 L220 0", "mf"))
    s += tool("gundrill", *pl(220, 0), 180, 120, 5, spindle=False, rotarr=False, feed=False)
    for x in (60, 150):
        xx, yy = pl(x, -SH.R(x))
        s += rect(xx - 4, 40, 8, yy - 42, "m3") + circ(xx, yy - 2, 3, "t")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ TRANSMISSION CASE
def case_side(hot=False, cast=False, done=()):
    c = "h" if hot else "w"
    s = path("M30 20 L60 20 L60 36 L290 60 Q312 64 312 90 L312 150 Q310 176 290 178 L60 190 L60 206 L30 206Z", c)
    s += path("M30 20 L60 20 L60 206 L30 206Z", "h" if hot else "w2")
    if not hot:
        for (x, y, r) in ((150, 100, 22), (240, 116, 18), (150, 160, 14)):
            s += circ(x, y, r, "w2") + circ(x, y, r * 0.6, "bg")
        for y in range(34, 206, 24):
            s += circ(45, y, 3, "bg")
        s += line(110, 40, 110, 186, "o thin") + line(200, 50, 204, 182, "o thin")
    if cast:
        s += rect(160, 190, 40, 14, "w3") + rect(290, 70, 14, 10, "w3", 2) + rect(290, 150, 14, 10, "w3", 2)
        s += roughen([(60, 36), (290, 60)]) + roughen([(60, 190), (290, 178)])
    return s


CASE_F = {"flange": "M30 20 L30 206", "bores": "M136 100 A14 14 0 1 0 164 100 A14 14 0 1 0 136 100 M229 116 A11 11 0 1 0 251 116 A11 11 0 1 0 229 116 M142 160 A8 8 0 1 0 158 160 A8 8 0 1 0 142 160"}


def tmcase_detail():
    s = shadow(200, 260, 160, 10)
    pl = Pl(40, 30, 1.1)
    s += pl.g(case_side())
    notes = [("合わせ面（フランジ）", "エンジン・ケース同士の合わせ面。平面度とシール"), ("軸受穴", "シャフトを支える穴。位置度±0.02〜0.03mm"),
             ("ボルト穴", "締結用。位置と深さ"), ("リブ", "薄肉の剛性を補う（鋳造で成形）"), ("油路", "内部の潤滑油路。鋳巣が漏れにつながる")]
    s += bal(*pl(30, 60), 20, 30, 1) + bal(*pl(150, 100), 410, 60, 2) + bal(*pl(45, 106), 20, 270, 3)
    s += bal(*pl(110, 120), 170, 280, 4) + bal(*pl(240, 116), 440, 200, 5)
    return s, notes


def tmcase_ops():
    ops = []
    s = title("大型の薄肉ケースを高圧ダイカストで鋳造")
    s += rect(40, 34, 200, 240, "m2") + rect(240, 34, 200, 240, "m3")
    s += Pl(80, 44, 1.0).g(case_side(hot=True))
    s += arrow(470, 150, 450, 150, None) + text(240, 292, "型締力2,500〜4,000t・真空ダイカスト", "middle")
    ops.append(s)
    s = title("湯口・バリを除き、ショットで表面を整える")
    pl = Pl(60, 40, 1.0)
    s += pl.g(case_side(cast=True))
    s += pl.g(line(156, 190, 204, 190, "cutl") + line(290, 66, 290, 84, "cutl") + line(290, 146, 290, 164, "cutl"))
    s += lead(*pl(180, 200), 380, 270, "湯口・オーバーフロー") + tol(380, 60, "変形・バリ残り")
    ops.append(s)
    s = title("加工面・シール面近傍の鋳巣をX線で確認")
    s += rect(20, 120, 50, 60, "m3", 4)
    for k in range(7):
        s += line(70, 150, 420, 40 + k * 36, "ray")
    pl = Pl(100, 40, 0.95)
    s += pl.g(case_side())
    x, y = pl(150, 124)
    s += circ(x, y, 3, "poro") + circ(x, y, 12, "mfring") + rect(424, 30, 22, 240, "m2")
    s += lead(x - 12, y, 40, 270, "鋳巣（軸受穴の近く）", "start")
    ops.append(s)
    s = title("合わせ面・軸受穴・ボルト穴・油路を横形MCで加工")
    pl = Pl(90, 40, 1.0)
    s += pl.g(case_side()) + pl.g(mf(CASE_F["flange"]) + mf(CASE_F["bores"]))
    s += tool("facemill", *pl(29, 110), 0, 50, 90, spindle=True, feed=False)
    s += tool("boring", *pl(164, 100), 180, 150, 14, spindle=True, feed=False, rotarr=True)
    s += tol(250, 280, "軸受穴の位置度 ±0.02〜0.03mm")
    ops.append(s)
    s = title("高圧水でバリを取り、切粉・油を洗浄")
    pl = Pl(80, 60, 0.95)
    s += pl.g(case_side())
    for x in (120, 220, 320):
        s += nozzle(x, 40, 90, 20, 8) + drops(x, 40, 4, 34, 30, 90)
    s += tol(40, 280, "清浄度（残留異物）を管理")
    ops.append(s)
    s = title("微細な鋳巣に樹脂を真空含浸して漏れを止める")
    s += rect(60, 40, 360, 220, "m2", 30) + rect(76, 110, 328, 140, "fl")
    s += Pl(120, 100, 0.7).g(case_side())
    s += arrow(440, 100, 440, 50, None) + text(434, 120, "真空→加圧", "end", "al")
    ops.append(s)
    s = title("油路をエアで加圧して漏れを確認し、三次元測定機で寸法を抜取")
    pl = Pl(70, 50, 0.95)
    s += pl.g(case_side()) + pl.g(rect(20, 14, 12, 198, "m3"))
    s += line(80, 130, 20, 130, "cable") + circ(20, 100, 14, "m")
    s += rect(380, 40, 16, 200, "m") + rect(360, 30, 100, 14, "m3") + rect(330, 44, 16, 80, "m2") + circ(338, 128, 4, "t")
    s += tol(40, 290, "リーク量・軸受穴の位置")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ VALVE BODY
def vb_top(done=()):
    s = rect(20, 40, 300, 170, "w", 6)
    for v0 in (60, 96, 132, 168):
        ps = [(34, v0), (90, v0), (90, v0 + 14), (160, v0 + 14), (160, v0 - 6), (230, v0 - 6), (230, v0 + 8), (300, v0 + 8)]
        s += pline(ps, "chan")
    return s


def vb_sec(done=()):
    """section across spool bores."""
    s = rect(20, 30, 300, 110, "cut")
    for i in range(5):
        x = 50 + i * 58
        s += circ(x, 80, 16, "void") + circ(x, 120, 6, "void") + line(x, 96, x, 114, "o thin")
    return s


def valvebody_detail():
    s = shadow(130, 200, 110, 8)
    pt = Pl(10, 20, 0.75)
    s += pt.g(vb_top())
    pl = Pl(250, 70, 0.72)
    s += rect(242, 48, 232, 130, "m", 4) + text(358, 64, "断面（スプール穴）", "middle", "sm") + pl.g(vb_sec())
    notes = [("油路（迷路状）", "ダイカストで成形した複雑な油路"), ("スプール穴", "スプール弁が滑る穴。径公差数μm"),
             ("合わせ面", "セパレートプレートとの合わせ面。平面度0.02〜0.05mm"), ("交差穴", "油路とスプール穴の交差部。バリが固着の原因")]
    s += bal(*pt(160, 110), 120, 250, 1) + bal(*pl(50, 80), 300, 230, 2)
    s += bal(*pt(20, 60), 30, 250, 3) + bal(*pl(108, 110), 420, 230, 4)
    return s, notes


def valvebody_ops():
    ops = []
    s = title("薄肉で複雑な油路を持つブロックをダイカスト")
    s += rect(40, 40, 400, 110, "m2") + rect(40, 150, 400, 110, "m3")
    s += Pl(70, 60, 1.1).g(rect(20, 40, 300, 170, "h", 6)) if False else Pl(70, 90, 1.1).g(rect(20, 20, 300, 100, "h", 6))
    s += text(240, 290, "型締力800〜1,250t", "middle")
    ops.append(s)
    s = title("セパレートプレートとの合わせ面を平らに仕上げ")
    pl = Pl(70, 110, 1.0)
    s += pl.g(vb_sec()) + pl.g(mf("M20 30 L320 30"))
    s += tool("facemill", *pl(170, 30), 90, 50, 110)
    s += tol(40, 280, "平面度0.02〜0.05mm")
    ops.append(s)
    s = title("ドリル→リーマ→ボーリングでスプール穴を精密に仕上げ")
    pl = Pl(70, 110, 1.0)
    s += pl.g(vb_sec()) + pl.g(mf("M34 80 A16 16 0 1 0 66 80 A16 16 0 1 0 34 80"))
    x, y = pl(50, 80)
    s += rot(x, y, 26, 26, 200, 320) + text(x, y - 40, "リーマ（手前から）", "middle", "al")
    s += tol(40, 280, "穴径公差 数μm・真円度・同軸度")
    ops.append(s)
    s = title("交差穴のバリを高圧水で除去")
    pl = Pl(70, 110, 1.0)
    s += pl.g(vb_sec())
    x, y = pl(108, 110)
    s += circ(x, y, 8, "mfring") + nozzle(x, y - 90, 90, 30, 10) + path("M%s %s L%s %s" % (n(x), n(y - 90), n(x), n(y - 20)), "jet")
    s += tol(40, 280, "バリはスプールの固着の原因")
    ops.append(s)
    s = title("洗浄し、残留異物を管理")
    s += rect(20, 40, 440, 200, "m", 6) + conveyor(40, 200, 400) + Pl(120, 110, 0.8).g(vb_sec())
    for x in (140, 240, 340):
        s += nozzle(x, 70, 90, 16) + drops(x, 70, 3, 30, 26, 90)
    ops.append(s)
    s = title("径ランクに合わせたスプールとソレノイドを組み付け")
    pl = Pl(70, 110, 1.0)
    s += pl.g(vb_sec())
    x, y = pl(50, 80)
    s += rect(x - 40, y - 6, 80, 12, "cr") + rect(x - 30, y - 60, 60, 40, "m3", 4) + arrow(x + 50, y - 60, x + 50, y - 20, None)
    s += tol(40, 280, "すき間 数μm（選択組付け）")
    ops.append(s)
    s = title("実際に油を流して各弁の油圧特性と漏れを確認")
    s += Pl(60, 130, 0.9).g(vb_sec()) + chart(330, 40, 140, 90, "step") + text(400, 146, "油圧特性", "middle", "sm")
    s += line(340, 180, 400, 180, "jet2") + tol(40, 280, "スティック（固着）がないこと")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CVT PULLEY
def pulley_side(hot=False):
    c = "h" if hot else "w"
    s = Rev([(260, 12)]).svg(hot=hot)
    s += path(P([(60, -70), (70, -70), (130, -16), (130, 16), (70, 70), (60, 70)]), c)
    s += path(P([(60, -70), (70, -70), (130, -16), (130, 0), (60, 0)]), "cut" if not hot else c)
    return s


def pulley_detail():
    pl = Pl(40, 150, 1.4)
    s = shadow(220, 262, 180, 8) + pl.g(pulley_side())
    notes = [("シーブ面", "ベルトを挟む円すい面。角度・粗さが伝達効率を決める"), ("軸部", "軸受部の径・振れ"),
             ("ボールスプライン溝", "可動シーブが軸方向に滑る溝")]
    s += bal(*pl(100, -40), 200, 50, 1) + bal(*pl(200, -12), 360, 60, 2) + bal(*pl(170, 12), 300, 250, 3)
    return s, notes


def pulley_ops():
    ops = []
    s = title("軸と一体のシーブを熱間鍛造")
    s += rect(60, 40, 360, 40, "t") + rect(60, 220, 360, 40, "t") + Pl(110, 150, 1.0).g(pulley_side(hot=True))
    ops.append(s)
    pl = Pl(70, 150, 1.2)
    s = title("シーブ面・軸部を旋削")
    s += chuck(*pl(0, 0), 30) + pl.g(pulley_side()) + pl.g(mf("M70 -70 L130 -16"))
    s += tool("turn", *pl(100, -44), 45, 60, 16, spindle=False, rotarr=False, feed=False)
    ops.append(s)
    s = title("可動シーブが滑るボールスプライン溝を加工")
    pl = Pl(70, 150, 1.2)
    s += pl.g(pulley_side()) + pl.g(mf("M160 -12 L230 -12"))
    s += tool("endmill", *pl(195, -12), 90, 50, 12)
    ops.append(s)
    s = title("浸炭焼入れで表面を硬化")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin")
    for i in range(3):
        s += Pl(70 + i * 125, 150, 0.4).g(pulley_side())
    ops.append(s)
    s = title("シーブ面をアンギュラ研削し、軸部を仕上げ")
    pl = Pl(70, 170, 1.2)
    s += center(*pl(0, 0), False) + pl.g(pulley_side()) + pl.g(mf("M70 -70 L130 -16"))
    x, y = pl(100, -43)
    s += '<g transform="rotate(42 %s %s)">' % (n(x), n(y)) + wheel(x, y - 46, 44) + "</g>"
    s += tol(300, 270, "シーブ角度・振れ・研削焼け")
    ops.append(s)
    s = title("ベルト接触面を超仕上げして表面粗さを制御")
    pl = Pl(70, 170, 1.2)
    s += pl.g(pulley_side()) + pl.g(mf("M70 -70 L130 -16"))
    x, y = pl(100, -43)
    s += '<g transform="rotate(-48 %s %s)">' % (n(x), n(y)) + rect(x - 30, y - 30, 60, 22, "gw", 3) + "</g>"
    s += tol(300, 270, "粗さ＝摩擦係数に直結")
    ops.append(s)
    s = title("固定シーブと可動シーブを組み、作動を確認")
    pl = Pl(60, 150, 1.2)
    s += pl.g(pulley_side())
    s += pl.g(path(P([(200, -70), (190, -70), (130, -16), (130, 16), (190, 70), (200, 70)]), "w2"))
    s += arrow(*pl(230, -84), *pl(260, -84), None, both=True) + text(*pl(245, -92), "摺動", "middle", "al") if False else arrow(*pl(220, -84), *pl(260, -84), None, both=True)
    ops.append(s)
    return [fin(x) for x in ops]


import il_parts


def base(key, x, y, s):
    pl = Pl(x, y, s)
    return pl, pl.g(il_parts.PARTS[key]())


# ================================================================ HYPOID
def hypoid_detail():
    import il_gscene as GS
    import il_gear as GE
    s = GS.sc_hypoid_pair(262, 150, 1.05, lab=False)
    cam = GE.Cam(262, 150, 0, 34, 1.05)
    notes = [("リングギヤ歯面", "まがりばかさ歯。歯当たり・歯面トポグラフィを管理"), ("ドライブピニオン", "軸がリングギヤ中心からずれた（オフセット）ハイポイド歯"),
             ("取付面・ボルト穴", "デフケースへの取付。振れ・平面度"), ("ピニオン軸受部", "プリロードを掛けて支持"), ("内径（はめ合い）", "デフケースに圧入・ボルト締結")]
    a1 = cam.xy((70, -70, 29))
    a2 = cam.xy((-130, -34, 36))
    a3 = cam.xy((-50, 40, 10))
    a4 = cam.xy((-215, -34, 36))
    a5 = cam.xy((0, 48, 10))
    s += bal(a1[0], a1[1], 440, 70, 1) + bal(a2[0], a2[1], 150, 272, 2) + bal(a3[0], a3[1], 250, 40, 3)
    s += bal(a4[0], a4[1], 40, 236, 4) + bal(a5[0], a5[1], 360, 36, 5)
    return s, notes


def hypoid_ops():
    import il_gscene as GS
    import il_gear as GE
    ops = []
    s = title("リングギヤ素材をリングローリング、ピニオンを熱間鍛造")
    s += circ(160, 160, 80, "h") + circ(160, 160, 50, "bg") + circ(160, 58, 14, "m3") + circ(160, 300, 44, "t")
    s += rot(160, 160, 92, 92, 200, 250) + text(160, 40, "マンドレル", "middle")
    s += rect(300, 60, 140, 34, "t") + rect(300, 220, 140, 34, "t") + Pl(310, 157, 1.0).g(Rev([(60, 12), (40, 26)]).svg(hot=True))
    s += text(370, 280, "ピニオン鍛造", "middle")
    ops.append(s)
    s = title("取付面・内径・外周を旋削")
    cam = GE.Cam(220, 160, 0, 34, 1.05)
    s += GE.prism(cam, (0, 0, -16), (0, 0, 1), GE.circle_outline(118, 72, 24), 36, "w", holes=[GE.circle_outline(49, 48, 48)],
                  smooth=True, hl="mfe")
    x, y = cam.xy((0, -118, 20))
    s += tool("turn", x + 30, y - 4, 90, 60, 16, spindle=False, rotarr=False, feedlab="送り")
    s += GS._ell_arc(cam, (0, 0), 134, 20, 150, 205)
    s += tol(24, 290, "取付面の振れ・平面度が歯当たりの基準")
    ops.append(s)
    s = title("カッタヘッドでまがりばかさ歯を歯切り（フェースホビング）")
    s += GS.sc_hypoid_cut(210, 168, 1.05)
    s += tol(24, 290, "ドライカット。歯当たり・歯面形状を測定して補正")
    ops.append(s)
    s = title("浸炭焼入れ。リングギヤはプレスクエンチでひずみを抑える")
    s += tank(40, 120, 400, 140, 0.8) + rect(100, 90, 280, 40, "t") + rect(100, 196, 280, 30, "t")
    s += ell(240, 176, 130, 20, "w") + ell(240, 176, 80, 12, "bg")
    s += arrow(240, 40, 240, 86, None) + text(250, 64, "金型で拘束", "start", "al") + tol(40, 290, "平面度・真円度のひずみ")
    ops.append(s)
    s = title("リングとピニオンをかみ合わせてラッピング（ペア仕上げ）")
    s += GS.sc_hypoid_pair(262, 150, 1.05)
    s += dots(96, 150, 50, 36, 6, "grain") + lead(120, 168, 60, 250, "ラップ剤", "start")
    cam = GE.Cam(262, 150, 0, 34, 1.05)
    s += GS._ell_arc(cam, (0, 0), 136, 10, 20, 70)
    s += tol(300, 290, "歯当たり・騒音をペアで作り込む")
    ops.append(s)
    s = title("片歯面かみあい試験で騒音を判定し、ペアに刻印")
    s += GS.sc_hypoid_pair(250, 160, 1.0)
    s += chart(330, 196, 140, 64, "noise") + text(400, 276, "伝達誤差・構造音", "middle", "sm")
    ops.append(s)
    pl, s = base("drivetrain.diffcase", 0, 30, 1.1)
    s = title("デフケースにリングギヤを締結し、シムで予圧とバックラッシを調整") + s
    s += tool("tap", *pl(92, 40), -90, 50, 12, spindle=True, rotarr=True, feed=False)
    s += rect(*pl(66, 120), 10, 40, "m3") + lead(*pl(70, 130), 30, 280, "シム（自動選択）", "start")
    s += tol(300, 280, "プリロード・バックラッシ・歯当たり")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ DIFF CASE
def diffcase_detail():
    pl, s = base("drivetrain.diffcase", 0, 20, 1.2)
    notes = [("球状の内面", "サイドギヤ・ピニオンの背面が当たる球面"), ("窓", "内部加工とギヤ組付けのための開口"),
             ("フランジ", "リングギヤの取付面。振れ・ボルト穴"), ("軸受部", "デフ軸受の圧入部")]
    s += bal(*pl(168, 104), 300, 40, 1) + bal(*pl(176, 80), 360, 80, 2) + bal(*pl(92, 60), 60, 40, 3) + bal(*pl(260, 104), 440, 240, 4)
    return s, notes


def diffcase_ops():
    ops = []
    s = title("鋳鉄を溶解し、マグネシウム処理で黒鉛を球状化")
    s += rect(40, 90, 120, 170, "m2", 6) + rect(54, 150, 92, 100, "h") + text(100, 280, "誘導炉", "middle")
    s += path("M160 150 Q200 130 230 170", "pour") + path(P([(220, 160), (320, 160), (310, 260), (230, 260)]), "m2") + rect(236, 180, 68, 76, "h")
    s += sparks(270, 176, 18, 9, -170, -10) + text(270, 280, "球状化処理（Mg）・接種", "middle")
    s += tol(340, 120, "成分・球状化率") + tol(340, 136, "熱分析で確認")
    ops.append(s)
    s = title("生型に中子を組み、注湯して鋳造")
    s += rect(60, 60, 360, 200, "sand") + dots(62, 62, 356, 196, 10, "grain") + line(60, 160, 420, 160, "o")
    s += circ(240, 160, 70, "h") + circ(240, 160, 40, "sand") + rect(130, 150, 40, 20, "h") + rect(310, 150, 40, 20, "h")
    s += rect(232, 60, 16, 30, "h") + text(240, 290, "上型・下型の生砂鋳型＋シェル中子", "middle")
    ops.append(s)
    pl, s = base("drivetrain.diffcase", 20, 30, 1.1)
    s = title("砂を落とし、ショットとグラインダで仕上げる") + s
    s += dots(40, 250, 400, 40, 10, "grain") + circ(420, 70, 22, "m2") + text(420, 110, "ショット", "middle")
    ops.append(s)
    pl, s = base("drivetrain.diffcase", 0, 30, 1.1)
    s = title("超音波の音速で球状化率を判定し、硬さを確認") + s
    x, y = pl(170, 42)
    s += rect(x - 16, y - 50, 32, 36, "m3") + rect(x - 12, y - 14, 24, 6, "fl")
    s += rect(360, 150, 110, 110, "m", 4) + circ(415, 205, 44, "m")
    for k in range(9):
        s += circ(385 + (k % 3) * 30, 180 + (k // 3) * 24, 5, "d")
    s += text(415, 276, "球状黒鉛（顕微鏡）", "middle", "sm")
    ops.append(s)
    pl, s = base("drivetrain.diffcase", 10, 40, 1.1)
    s = title("外形・フランジ・軸受部を旋削") + s
    s += '<g transform="translate(%s %s) scale(1.1)">' % (n(pl.x), n(pl.y)) + path("M232 84 L288 84 M232 124 L288 124", "mf") + path("M100 34 L100 174", "mf") + "</g>"
    x, y = pl(260, 84)
    s += tool("turn", x, y - 1, 90, 50, 14, spindle=False, rotarr=False, feedlab="送り")
    ops.append(s)
    pl, s = base("drivetrain.diffcase", 0, 40, 1.1)
    s = title("窓から工具を入れて内球面を加工し、ピニオン軸穴をあける") + s
    x, y = pl(170, 104)
    s += circ(x, y, 50, "mfo") + tool("boring", x, y, 90, 150, 10, spindle=True, feed=False)
    s += tol(300, 280, "内球面の形状・穴位置")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CVJ
OUTER = Rev([(56, 14), (12, 20), (52, 42)], bore=[(68, 120, 30)], spline=[(4, 40)])


def outer_race(hot=False):
    s = OUTER.svg(hot=hot)
    if not hot:
        s += path("M84 -30 A8 8 0 0 1 100 -30Z", "void") if False else ell(96, -30, 10, 6, "void")
    return s


def cvj_detail():
    pl, s = base("drivetrain.cvj", 0, 20, 1.2)
    notes = [("外輪（アウターレース）", "ボール溝を持つカップ。冷間しごき＋焼入れ＋研削"), ("ブーツ", "グリースを封入し泥水を防ぐ樹脂ベローズ"),
             ("シャフト", "両端スプライン。高周波焼入れ"), ("内側ジョイント", "伸縮を吸収するトリポード型など"), ("ボール・ケージ・内輪", "角度がついても等速で回転を伝える")]
    s += bal(*pl(30, 80), 40, 40, 1) + bal(*pl(72, 104), 120, 280, 2) + bal(*pl(160, 104), 220, 40, 3)
    s += bal(*pl(290, 104), 440, 60, 4)
    s += rect(330, 150, 140, 120, "m", 4) + text(400, 166, "外輪断面", "middle", "sm") + Pl(344, 216, 0.95).g(outer_race())
    s += bal(430, 186, 450, 280, 5) if False else bal(*Pl(344, 216, 0.95)(96, -30), 460, 290, 5)
    return s, notes


def cvj_ops():
    ops = []
    s = title("外輪を熱間鍛造し、冷間しごきでボール溝をほぼ最終形状に")
    s += rect(80, 40, 300, 36, "t") + rect(80, 224, 300, 36, "t")
    s += Pl(150, 150, 1.4).g(outer_race(hot=True))
    s += arrow(420, 44, 420, 110, None) + text(428, 80, "成形", "start", "al")
    ops.append(s)
    pl = Pl(90, 150, 1.8)
    s = title("軸部を旋削し、スプラインを転造")
    s += pl.g(outer_race()) + chuck(*pl(120, 0), 150) if False else pl.g(outer_race())
    s += pl.g(mf(OUTER.od(0, 56)))
    x, y = pl(24, -14)
    s += gear3d(x, y - 44, 30, 38, 26, 4, -3, 8, "t") + gear3d(x, y + 94, 30, 38, 26, 4, -3, 8, "t", phase=0.12)
    s += rot(x, y - 44, 48, 48, 200, 250) + rot(x, y + 94, 48, 48, 20, 70) + text(x + 56, y - 70, "転造ダイス", "start", "al")
    s += tol(300, 280, "オーバーピン寸法・振れ")
    ops.append(s)
    pl = Pl(90, 150, 1.8)
    s = title("ボール溝と軸部を高周波焼入れ")
    s += pl.g(outer_race())
    x0, y0 = pl(68, -30)
    x1, y1 = pl(120, 30)
    s += rect(x0, y0, x1 - x0, 10, "hotband") + rect(x0, y1 - 10, x1 - x0, 10, "hotband")
    s += rect(x0 + 6, y0 + 12, x1 - x0 - 6, y1 - y0 - 24, "cu", 4) + text((x0 + x1) / 2, y1 + 60, "内側コイル", "middle", "al")
    ops.append(s)
    pl = Pl(80, 150, 1.8)
    s = title("ボール溝を研削（またはハードミーリング）で仕上げ")
    s += pl.g(outer_race()) + pl.g(mf("M86 -30 A10 6 0 0 0 106 -30"))
    x, y = pl(96, -18)
    s += circ(x, y, 12, "gw") + rect(x - 4, y, 8, 170, "m3") + rot(x, y, 20, 20, 200, 320)
    s += tol(300, 280, "溝ピッチ・溝形状（三次元測定）")
    ops.append(s)
    s = title("内輪は鍛造→旋削→焼入れ→研削、ケージは鋼管→窓抜き→研削")
    s += circ(130, 160, 70, "w") + circ(130, 160, 30, "bg")
    for k in range(6):
        a = 2 * math.pi * k / 6
        s += circ(130 + 58 * math.cos(a), 160 + 58 * math.sin(a), 10, "void")
    s += path(gear_d(130, 160, 30, 26, 18, 0, 0.5), "w2") + text(130, 256, "内輪（溝＋スプライン）", "middle")
    s += circ(340, 160, 74, "w") + circ(340, 160, 60, "void")
    for k in range(6):
        a = 2 * math.pi * k / 6
        s += rect(340 + 67 * math.cos(a) - 8, 160 + 67 * math.sin(a) - 8, 16, 16, "void", 3)
    s += text(340, 256, "ケージ（窓抜き）", "middle")
    ops.append(s)
    s = title("線材を冷間圧造で球にし、熱処理後に研削・ラッピング")
    s += rect(40, 60, 400, 40, "m2") + rect(40, 180, 400, 40, "m2")
    for i in range(8):
        s += circ(70 + i * 48, 140, 22, "ball")
    s += rot(240, 80, 200, 26, 200, 230) + text(240, 250, "溝付き定盤で真球に仕上げる", "middle") + tol(40, 290, "真球度・径のばらつき（等級）")
    ops.append(s)
    pl, s = base("drivetrain.cvj", 0, 30, 1.2)
    s = title("ボールを組み込み、グリースを定量封入し、ブーツをバンドで締付け") + s
    x, y = pl(100, 104)
    s += rect(x - 6, y - 70, 12, 24, "m3") + arrow(x + 20, y - 80, x + 20, y - 46, None) + text(x + 26, y - 64, "バンド締付け", "start", "al")
    x, y = pl(20, 60)
    s += nozzle(x, y, 60, 30, 10) + text(x - 6, y - 36, "グリース封入", "middle", "al")
    ops.append(s)
    pl, s = base("drivetrain.cvj", 0, 30, 1.2)
    s = title("作動角をつけて回転させ、トルク・ガタを確認") + s
    s += chart(320, 190, 150, 80, "ramp") + rot(*pl(160, 104), 20, 30, -60, 60)
    s += arrow(*pl(10, 150), *pl(30, 180), None, both=True) + text(*pl(40, 190), "作動角", "start", "al")
    ops.append(s)
    return [fin(x) for x in ops]
