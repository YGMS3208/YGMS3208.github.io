from il_detail import *
import il_parts
from il_d_drive import base, gear_front, gear_sec, GEAR_F


def flipy(body):
    return '<g transform="scale(1 -1)">' + body + "</g>"


# ================================================================ KNUCKLE
def knuckle_detail():
    pl, s = base("chassis.knuckle", 40, 20, 1.3)
    notes = [("ハブ取付穴", "ハブベアリングが入る穴。径・位置"), ("ストラット取付部", "上側。ボルト穴2か所"),
             ("ロアアーム取付部", "下側。ボールジョイントのテーパ穴"), ("ナックルアーム", "タイロッドが付く。ステアリング操作を伝える"),
             ("キャリパ取付面", "ブレーキキャリパの取付座面とねじ")]
    s += bal(*pl(162, 104), 440, 60, 1) + bal(*pl(160, 36), 60, 50, 2) + bal(*pl(160, 164), 60, 270, 3)
    s += bal(*pl(264, 122), 440, 200, 4) + bal(*pl(110, 104), 40, 160, 5)
    return s, notes


def knuckle_ops():
    ops = []
    s = title("球状化処理した溶湯を生型に注湯")
    s += rect(60, 60, 360, 200, "sand") + dots(62, 62, 356, 196, 10, "grain") + line(60, 160, 420, 160, "o")
    s += Pl(120, 40, 0.8).g(path("M140 22 L178 22 L186 64 Q222 72 226 104 L276 112 L276 132 L222 132 Q210 148 186 150 L180 176 L142 176 L138 150 Q104 142 100 104 Q104 72 136 62Z", "h"))
    s += rect(232, 60, 16, 26, "h") + text(240, 290, "FCD450〜600・無枠自動造型ライン", "middle")
    ops.append(s)
    pl, s = base("chassis.knuckle", 60, 40, 1.1)
    s = title("砂を落とし、湯口を切り、ショットで仕上げる") + s
    s += dots(40, 260, 400, 30, 10, "grain") + circ(430, 80, 22, "m2") + text(430, 120, "ショット", "middle")
    ops.append(s)
    pl, s = base("chassis.knuckle", 20, 30, 1.1)
    s = title("球状化率（超音波）と内部欠陥（X線）、表面割れ（磁粉）を確認") + s
    s += rect(380, 60, 22, 200, "m2") + line(200, 150, 380, 80, "ray") + line(200, 150, 380, 240, "ray") if False else rect(420, 40, 22, 220, "m2")
    for k in range(5):
        s += line(20, 150, 420, 60 + k * 45, "ray")
    ops.append(s)
    pl, s = base("chassis.knuckle", 20, 30, 1.2)
    s = title("ハブ穴・アーム取付穴・キャリパ取付面を多面加工") + s
    s += circ(*pl(162, 104), 22 * 1.2, "mfo") + circ(*pl(264, 122), 5 * 1.2, "mfa") + circ(*pl(160, 164), 5 * 1.2, "mfa")
    x, y = pl(162, 104)
    s += rot(x, y, 38, 38, 200, 320) + text(x, y - 46, "ボーリング（手前から）", "middle", "al")
    s += tool("drill", *pl(264, 118), 90, 50, 8, spindle=True, feed=False)
    s += tol(300, 280, "ハブ穴径・テーパ穴・取付面")
    ops.append(s)
    pl, s = base("chassis.knuckle", 20, 30, 1.2)
    s = title("ハブ穴径と寸法・外観を確認") + s
    x, y = pl(162, 104)
    s += rect(x - 10, y - 80, 20, 60, "m2") + circ(x - 8, y - 20, 2.4, "fdot") + circ(x + 8, y - 20, 2.4, "fdot")
    s += rect(380, 40, 90, 50, "m", 4) + text(425, 70, "径 ±μm", "middle")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ HUB BEARING
HUB_UP = [
    (P([(0, 0), (0, -22), (40, -22), (40, -24), (80, -24), (80, -72), (90, -72), (90, -18), (98, -18), (98, 0)]), "cut"),
    (P([(0, -22), (22, -22), (22, -30), (0, -30)]), "w3"),
    (P([(4, -34), (76, -34), (76, -46), (44, -46), (44, -64), (32, -64), (32, -46), (4, -46)]), "cut"),
]


def hub_sec(hot=False):
    s = ""
    for d, c in HUB_UP:
        cc = "h" if hot else c
        s += path(d, cc)
    lower = "".join(path(d, "h" if hot else "w") for d, c in HUB_UP)
    s += flipy(lower)
    if not hot:
        for x, y in ((14, -29), (60, -29)):
            s += circ(x, y, 5.5, "ball") + circ(x, -y, 5.5, "ball")
        s += rect(76, -62, 30, 6, "m") + rect(76, 56, 30, 6, "m")
    s += cl(-10, 0, 110, 0)
    return s


HUB_F = {"race_o": "M6 -34 L22 -34 M52 -34 L74 -34", "race_i": "M26 -24 L70 -24", "flange": "M80 -72 L80 -24",
         "od": "M4 -46 L32 -46"}


def hubbearing_detail():
    pl = Pl(80, 150, 1.8)
    s = pl.g(hub_sec())
    notes = [("ハブフランジ", "ホイール・ディスクの取付面。振れ管理"), ("外輪（車体取付フランジ）", "ナックルに締結する"),
             ("軌道面", "玉が転がる面。高周波焼入れ＋研削＋超仕上げ"), ("玉（2列）", "アンギュラ玉軸受。予圧を付与"),
             ("かしめ部", "内輪をハブ端部の揺動かしめで固定"), ("ハブボルト", "ホイールを締結")]
    s += bal(*pl(85, -60), 330, 40, 1) + bal(*pl(38, -60), 120, 30, 2) + bal(*pl(60, -34), 250, 40, 3)
    s += bal(*pl(14, 29), 60, 280, 4) + bal(*pl(2, -26), 30, 90, 5) + bal(*pl(100, 59), 360, 280, 6)
    return s, notes


def hubbearing_ops():
    ops = []
    s = title("外輪（フランジ付き）とハブ輪を熱間鍛造")
    s += rect(60, 40, 360, 34, "t") + rect(60, 226, 360, 34, "t")
    s += Pl(180, 150, 1.4).g(hub_sec(hot=True))
    s += arrow(440, 44, 440, 110, None)
    ops.append(s)
    pl = Pl(160, 150, 1.8)
    s = title("旋削で形状をつくる")
    s += chuck(*pl(0, 0), 60) + pl.g(hub_sec()) + pl.g(mf("M80 -72 L90 -72 M90 -72 L90 -18"))
    s += tool("turn", *pl(85, -72), 90, 60, 16, spindle=False, rotarr=False, feedlab="送り")
    ops.append(s)
    pl = Pl(160, 150, 1.8)
    s = title("軌道面とシール部を高周波焼入れ")
    s += pl.g(hub_sec())
    for d in (HUB_F["race_o"], HUB_F["race_i"]):
        s += pl.g(path(d, "coat"))
    s += tol(40, 280, "硬化層・焼割れ")
    ops.append(s)
    pl = Pl(150, 150, 1.8)
    s = title("外輪軌道は内面研削、ハブ輪軌道はアンギュラ研削")
    s += pl.g(hub_sec()) + pl.g(mf(HUB_F["race_o"]) + mf(HUB_F["race_i"]))
    x, y = pl(62, -30)
    s += circ(x, y, 9, "gw") + rect(x, y - 4, 200, 8, "m3") + rot(x, y, 16, 16, 200, 320)
    s += tol(40, 280, "軌道径・真円度・溝R")
    ops.append(s)
    pl = Pl(150, 150, 1.8)
    s = title("砥石を揺動させて軌道面を超仕上げ")
    s += pl.g(hub_sec()) + pl.g(mf(HUB_F["race_i"]))
    x, y = pl(48, -24)
    s += rect(x - 10, y - 90, 20, 70, "m3") + rect(x - 10, y - 20, 20, 16, "gw")
    s += arrow(x - 40, y - 100, x + 40, y - 100, None, both=True) + text(x, y - 108, "揺動", "middle", "al")
    ops.append(s)
    pl = Pl(150, 150, 1.8)
    s = title("玉と内輪を組み込み、ハブ端を揺動かしめして予圧を与える")
    s += pl.g(hub_sec()) + pl.g(mf("M0 -30 L0 -22"))
    x, y = pl(-4, 0)
    s += '<g transform="rotate(-8 %s %s)">' % (n(x), n(y)) + rect(x - 60, y - 40, 50, 80, "t", 4) + "</g>"
    s += arrow(x - 110, y, x - 70, y, None) + text(x - 90, y - 50, "揺動かしめ", "middle", "al")
    s += tol(300, 280, "予圧・かしめ形状")
    ops.append(s)
    pl = Pl(150, 150, 1.8)
    s = title("回転トルク・予圧・異音とセンサ用エンコーダを確認")
    s += pl.g(hub_sec()) + rot(*pl(50, 0), 20, 140, -60, 60)
    s += chart(330, 40, 140, 70, "noise") + text(400, 126, "音響・回転トルク", "middle", "sm")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ BRAKE DISC
DISC_UP = [
    (P([(18, -12), (26, -12), (26, -38), (60, -38), (60, -44), (18, -44)]), "cut"),
    (P([(60, -112), (68, -112), (68, -40), (60, -40)]), "cut"),
    (P([(78, -112), (86, -112), (86, -40), (78, -40)]), "cut"),
    (P([(68, -108), (78, -108), (78, -44), (68, -44)]), "w2"),
]


def disc_sec(hot=False):
    s = ""
    for d, c in DISC_UP:
        s += path(d, "h" if hot else c)
    s += flipy("".join(path(d, "h" if hot else ("w" if c != "w2" else "w2")) for d, c in DISC_UP))
    s += cl(0, 0, 100, 0)
    return s


DISC_F = {"faces": "M60 -112 L60 -40 M86 -112 L86 -40 M60 112 L60 40 M86 112 L86 40", "hub": "M18 -12 L18 -44", "rim": "M60 -112 L86 -112"}


def disc_detail():
    pl0, s = base("chassis.disc", -20, 20, 1.3)
    pl = Pl(360, 150, 1.0)
    s += rect(340, 30, 130, 240, "m", 4) + text(405, 46, "断面", "middle", "sm") + pl.g(disc_sec())
    notes = [("摺動面", "パッドが当たる両面。厚み差（DTV）10μm以下"), ("ベンチ（通風）穴", "中子で形づくる冷却の通風路"),
             ("ハット部", "ハブへの取付部。ボルト穴・センタ穴"), ("外周", "バランス修正で削る部分")]
    s += bal(*pl(60, -80), 300, 60, 1) + bal(*pl(73, -80), 470, 80, 2) if False else bal(*pl(60, -80), 300, 60, 1) + bal(*pl(73, 80), 460, 290, 2)
    s += bal(*pl(22, -30), 300, 150, 3) + bal(*pl(73, -112), 460, 40, 4)
    return s, notes


def disc_ops():
    ops = []
    s = title("生型にベンチ穴用の中子を組み、FC250を注湯")
    s += rect(40, 40, 400, 230, "sand") + dots(42, 42, 396, 226, 10, "grain")
    s += '<g transform="translate(240 155) rotate(90)">' + '<g transform="scale(1.2) translate(-52 0)">' + disc_sec(hot=True) + "</g></g>"
    s += text(240, 290, "中子ずれ＝ベンチ（通風路）の肉厚不良", "middle")
    ops.append(s)
    s = title("砂を落とし、ショットで表面を整える")
    s += Pl(100, 150, 1.2).g(disc_sec()) + dots(40, 260, 400, 30, 10, "grain") + circ(420, 80, 22, "m2")
    ops.append(s)
    pl = Pl(160, 150, 1.2)
    s = title("立形2主軸旋盤で摺動面の両面を同時に旋削")
    s += pl.g(disc_sec()) + pl.g(mf(DISC_F["faces"]))
    s += tool("turn", *pl(59, -80), 0, 60, 16, spindle=False, rotarr=False, feed=False)
    s += tool("turn", *pl(87, -80), 180, 60, 16, spindle=False, rotarr=False, feed=False)
    s += rot(*pl(73, 0), 30, 150, -40, 40) + tol(40, 280, "DTV 10μm以下・面振れ・粗さ")
    ops.append(s)
    pl = Pl(180, 150, 1.2)
    s = title("ハブボルト穴・センタ穴を加工")
    s += pl.g(disc_sec()) + pl.g(mf("M18 -30 L26 -30 M18 30 L26 30"))
    s += tool("drill", *pl(26, -30), 180, 60, 8, spindle=True, feed=False)
    ops.append(s)
    pl = Pl(180, 150, 1.2)
    s = title("アンバランスを測り、外周を削って修正")
    s += pl.g(disc_sec()) + pl.g(mf(DISC_F["rim"]))
    s += tool("endmill", *pl(73, -112), 90, 50, 14, spindle=True, feed=False)
    s += rot(*pl(73, 0), 30, 150, -40, 40)
    ops.append(s)
    pl = Pl(180, 150, 1.2)
    s = title("防錆処理後、厚み差（DTV）と振れを全数測定")
    s += pl.g(disc_sec())
    for x, sg in ((60, -1), (86, 1)):
        xx, yy = pl(x, -80)
        s += rect(xx + sg * 6 if sg > 0 else xx - 46, yy - 4, 40, 8, "m3") + circ(xx + sg * 2, yy, 3, "t")
    s += rect(360, 40, 100, 50, "m", 4) + text(410, 70, "DTV μm", "middle")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ CALIPER
def caliper_detail():
    pl, s = base("chassis.caliper", 0, 20, 1.3)
    notes = [("シリンダ穴", "ピストンが入る穴。径・粗さ"), ("ピストンシール溝", "シールの変形で戻り量をつくる"), ("ブリーダ穴", "エア抜き用のねじ穴"),
             ("取付穴", "ナックルへの取付"), ("ディスク通過部", "ディスクをまたぐブリッジ")]
    s += bal(*pl(122, 76), 60, 40, 1) + bal(*pl(198, 80), 440, 40, 2) + bal(*pl(160, 52), 300, 30, 3)
    s += bal(*pl(64, 132), 40, 250, 4) + bal(*pl(160, 120), 250, 280, 5)
    return s, notes


def caliper_ops():
    ops = []
    s = title("鋳鉄は生型、アルミは重力・低圧鋳造")
    s += rect(40, 40, 400, 230, "sand") + dots(42, 42, 396, 226, 10, "grain")
    s += Pl(80, 30, 1.0).g(path("M70 94 Q84 50 160 44 Q236 50 250 94 L262 136 Q240 124 222 128 L210 104 Q160 92 110 104 L98 128 Q80 124 58 136Z", "h"))
    ops.append(s)
    pl, s = base("chassis.caliper", 0, 20, 1.3)
    s = title("シリンダ穴・シール溝・ブリーダ穴・取付穴を加工") + s
    s += ell(*pl(122, 76), 20 * 1.3, 12 * 1.3, "mfo") + ell(*pl(198, 76), 20 * 1.3, 12 * 1.3, "mfo")
    x, y = pl(122, 76)
    s += tool("boring", x, y, 90, 70, 16, spindle=True, feed=False)
    s += tol(300, 280, "シリンダ径・粗さ・シール溝寸法")
    ops.append(s)
    s = title("防錆のため亜鉛系めっき（シリンダ内は付着させない）")
    s += tank(40, 70, 400, 180, 0.8)
    for i in range(3):
        s += Pl(60 + i * 130, 100, 0.4).g(il_parts.PARTS["chassis.caliper"]())
    ops.append(s)
    pl = Pl(150, 150, 2.0)
    s = title("鋼ピストンを旋削・研削し、硬質クロムめっき")
    rv = Rev([(60, 26)], bore=[(10, 60, 20)])
    s += chuck(*pl(0, 0), 110) + pl.g(rv.svg()) + pl.g(mf(rv.od(0, 60)))
    s += wheel(*pl(30, -26 - 30), 44)
    ops.append(s)
    pl, s = base("chassis.caliper", 0, 20, 1.3)
    s = title("シール・ピストン・ブーツ・ブリーダを組み付け") + s
    x, y = pl(122, 76)
    s += rect(x - 12, y - 90, 24, 50, "m3") + arrow(x + 30, y - 90, x + 30, y - 40, None) + text(x + 36, y - 66, "ピストン挿入", "start", "al")
    ops.append(s)
    pl, s = base("chassis.caliper", 0, 20, 1.3)
    s = title("気密と、ピストンが動き出す圧力（引きずり）を確認") + s
    x, y = pl(160, 52)
    s += line(x, y - 20, x + 160, y - 20, "cable") + circ(x + 176, y - 36, 18, "m")
    s += chart(320, 170, 150, 80, "ramp")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ ABS/ESC HU
def hu_detail():
    pl, s = base("chassis.hu", 0, 20, 1.3)
    notes = [("アルミブロック", "数十の穴と交差油路を持つ押出材の削り出し"), ("ソレノイドバルブ", "かしめで固定する増減圧弁"),
             ("ポンプ・モータ", "還流ポンプを駆動"), ("配管ポート", "マスタシリンダ・各輪への接続ねじ")]
    s += bal(*pl(150, 140), 250, 280, 1) + bal(*pl(134, 72), 60, 40, 2) + bal(*pl(40, 140), 40, 280, 3) + bal(*pl(138, 136), 440, 250, 4)
    return s, notes


def hu_ops():
    ops = []
    s = title("アルミ押出材（6061）を定寸に切断")
    s += Pl(20, 190, 1.0).g(Rev([(280, 40)]).svg()) + circ(330, 110, 56, "t") + circ(330, 110, 12, "m2") + line(300, 140, 300, 236, "cutl")
    ops.append(s)
    pl, s = base("chassis.hu", 0, 20, 1.3)
    s = title("6面から弁穴・ポンプ穴・交差油路を加工") + s
    for i in range(4):
        s += circ(*pl(110 + i * 28, 136), 6 * 1.3, "mfa")
    s += tool("drill", *pl(138, 130), 90, 60, 8, spindle=True, feed=False)
    s += tol(300, 280, "穴位置・径、交差部のバリ")
    ops.append(s)
    pl, s = base("chassis.hu", 0, 20, 1.3)
    s = title("交差穴のバリを高圧水で取り、精密洗浄") + s
    x, y = pl(166, 136)
    s += tool("nozzle", x, y, 0, 60, 10, spindle=False, rotarr=False, feed=False) + path("M%s %s l40 0" % (n(x), n(y)), "jet")
    ops.append(s)
    s = title("アルマイト処理で耐食性を持たせる")
    s += tank(40, 70, 400, 180, 0.8)
    for i in range(3):
        s += Pl(60 + i * 130, 110, 0.38).g(il_parts.PARTS["chassis.hu"]())
    ops.append(s)
    pl, s = base("chassis.hu", 0, 30, 1.3)
    s = title("ソレノイドバルブをかしめ固定し、ポンプ・モータを圧入") + s
    x, y = pl(134, 66)
    s += rect(x - 14, y - 70, 28, 40, "t", 3) + arrow(x + 30, y - 70, x + 30, y - 20, None) + text(x + 36, y - 44, "塑性流動かしめ", "start", "al")
    ops.append(s)
    pl, s = base("chassis.hu", 0, 20, 1.3)
    s = title("制御ECUを結合し、液圧特性と漏れを全数確認") + s
    s += chart(330, 180, 140, 80, "step") + tol(330, 280, "液圧・応答特性")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ EPS RACK
RACK = Rev([(20, 12), (160, 14), (80, 14), (20, 12)], thread=[(190, 260)])


def rack_svg():
    import il_gear as GE
    s = RACK.svg()
    pts = GE.rack_pts(32, 168, -14.8, 1.9, up=True)
    body = [(32, -10)] + pts + [(168, -10)]
    s += path(P(body), "w")
    s += path(P(pts, False), "o")
    return s


def eps_detail():
    pl0, s = base("chassis.eps", 0, 10, 1.2)
    pl = Pl(30, 250, 1.4)
    s += pl.g(rack_svg())
    notes = [("ラック歯", "ピニオンと噛み合う歯。可変ギヤ比は鍛造"), ("ボールねじ溝", "モータのアシスト力を軸力に変える"),
             ("ラックハウジング", "アルミダイカスト"), ("アシストモータ・ECU", "トルクセンサの信号でアシスト")]
    s += bal(*pl(100, -18), 150, 200, 1) + bal(*pl(220, -14), 380, 210, 2)
    s += bal(*pl0(80, 108), 40, 40, 3) + bal(*pl0(190, 64), 330, 30, 4)
    return s, notes


def eps_ops():
    ops = []
    pl = Pl(80, 150, 1.4)
    s = title("棒鋼を切断し、曲がりを矯正")
    s += pl.g(RACK.svg()) + poly([(pl(20, 0)[0] - 14, 190), (pl(20, 0)[0] + 14, 190), (pl(20, 0)[0], 170)], "m2") + poly([(pl(260, 0)[0] - 14, 190), (pl(260, 0)[0] + 14, 190), (pl(260, 0)[0], 170)], "m2")
    s += rect(pl(140, 0)[0] - 16, 60, 32, 64, "m3") + arrow(pl(140, 0)[0] + 30, 60, pl(140, 0)[0] + 30, 120, None)
    ops.append(s)
    pl = Pl(80, 150, 1.4)
    s = title("ラック歯をブローチで加工（可変ギヤ比は冷間鍛造）")
    s += pl.g(rack_svg()) + pl.g(mf("M30 -19 L170 -19"))
    import il_pictos_gear as PG
    s += PG.broach_bar(pl(10, 0)[0], pl(10, 0)[0] + 300, 96, 10, 1.5, 6, 9, rows=(-1,))
    s += rect(pl(10, 0)[0] + 300, 88, 18, 16, "m3")
    s += arrow(80, 60, 330, 60, "ブローチを引く", 205, 52)
    ops.append(s)
    pl = Pl(40, 150, 1.4)
    s = title("ラックアシスト式では、ボールねじ溝を研削で仕上げる")
    s += pl.g(rack_svg()) + pl.g(mf(RACK.od(190, 260).split(" M")[0]))
    x, y = pl(225, -14)
    s += '<g transform="rotate(-10 %s %s)">' % (n(x), n(y - 40)) + rect(x - 16, y - 80, 32, 76, "gw", 4) + "</g>"
    s += arrow(pl(190, 0)[0], 250, pl(260, 0)[0], 250, None) + text(pl(225, 0)[0], 270, "リードに合わせて送り", "middle", "al")
    ops.append(s)
    pl = Pl(40, 150, 1.4)
    s = title("ラック歯とねじ溝を高周波で移動焼入れ")
    s += induction_on(RACK, pl, 30, 170, "移動焼入れコイル")
    ops.append(s)
    pl = Pl(40, 150, 1.4)
    s = title("焼入れの曲がりを矯正し、外径をセンタレス研削")
    s += pl.g(rack_svg()) + pl.g(mf(RACK.od(20, 180).split(" M")[1]))
    s += rect(pl(40, 0)[0], 178, 200, 40, "gw", 6) + rect(pl(40, 0)[0], 90, 200, 30, "rbx", 6)
    ops.append(s)
    s = title("ピニオンをホブ切り→浸炭→歯面研削")
    import il_gscene as GS
    s += GS.sc_hobbing(186, 158, 1.25, lab=False, z=9, rp=38, width=70, shaft=(12, 40, 34), helix=30, hr=20, L=150, cut=0.6)
    s += text(118, 76, "ピニオン（ワーク）", "middle", "al") + text(330, 262, "ホブ", "middle", "al")
    s += tol(300, 290, "ねじれ角の大きいピニオン")
    ops.append(s)
    pl0, s = base("chassis.eps", 0, 30, 1.2)
    s = title("アルミダイカストのハウジングを加工（同軸度）") + s
    s += tool("boring", *pl0(40, 108), 0, 120, 14, spindle=True, feed=False)
    ops.append(s)
    pl0, s = base("chassis.eps", 0, 30, 1.2)
    s = title("モータ・ECU・トルクセンサを組み付け、作動トルク・異音を全数確認") + s
    s += chart(320, 190, 150, 80, "ramp")
    ops.append(s)
    return [fin(x) for x in ops]
