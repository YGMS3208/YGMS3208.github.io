from il_detail import *
import il_parts
from il_d_drive import base, gear_front, gear_sec, gear_ops


# ================================================================ e-Axle case
def ecase_sec(hot=False):
    c = "h" if hot else "cut"
    v = "h" if hot else "w"
    up = P([(0, -80), (170, -80), (170, -60), (190, -60), (190, -20), (170, -20), (170, -66), (12, -66), (12, -22), (0, -22)])
    s = path(up, c) + '<g transform="scale(1 -1)">' + path(up, v) + "</g>"
    if not hot:
        for x in range(30, 160, 30):
            s += rect(x, -76, 14, 6, "void") + rect(x, 70, 14, 6, "fl")
    s += cl(-10, 0, 200, 0)
    return s


EC_F = {"statorbore": "M12 -66 L170 -66 M12 66 L170 66", "bearing": "M0 -22 L12 -22 M0 22 L12 22", "flange": "M190 -60 L190 -20 M190 20 L190 60"}


def eaxlecase_detail():
    pl0, s = base("ev.eaxlecase", -8, 50, 0.88)
    pl = Pl(300, 150, 0.8)
    s += rect(280, 40, 190, 230, "m", 4) + text(375, 56, "断面", "middle", "sm") + pl.g(ecase_sec())
    notes = [("ステータ嵌合穴", "ステータを焼ばめする大径穴。軸受穴との同軸度"), ("冷却水路", "ハウジング外周の水路（鋳造で成形）"),
             ("軸受穴", "ロータ軸を支える"), ("減速機側フランジ", "ギヤケースとの合わせ面")]
    s += bal(*pl(90, -66), 300, 30, 1) + bal(*pl(37, -73), 460, 30, 2) + bal(*pl(6, -22), 300, 280, 3) + bal(*pl(190, 40), 460, 280, 4)
    return s, notes


def eaxlecase_ops():
    ops = []
    s = title("大型ケースを高圧ダイカスト（冷却水路も一体で成形）")
    s += rect(60, 40, 180, 230, "m2") + rect(240, 40, 180, 230, "m3") + Pl(140, 155, 1.0).g(ecase_sec(hot=True))
    s += text(240, 290, "型締力2,500〜4,000t", "middle")
    ops.append(s)
    s = title("水路・シール面の鋳巣をX線で確認")
    s += rect(20, 120, 50, 60, "m3", 4)
    for k in range(6):
        s += line(70, 150, 420, 50 + k * 40, "ray")
    pl = Pl(170, 150, 1.0)
    s += pl.g(ecase_sec()) + rect(424, 40, 22, 220, "m2")
    x, y = pl(66, -73)
    s += circ(x, y, 3, "poro") + circ(x, y, 12, "mfring")
    ops.append(s)
    pl = Pl(120, 150, 1.0)
    s = title("ステータ嵌合穴・軸受穴・合わせ面を加工（同軸度）")
    s += pl.g(ecase_sec()) + pl.g(mf(EC_F["statorbore"]) + mf(EC_F["bearing"]) + mf(EC_F["flange"]))
    x, y = pl(90, -66)
    s += tool("boring", pl(190, 0)[0] + 70, y + 8, 180, 250, 10, spindle=True, feed=False) if False else ""
    s += rect(pl(0, 0)[0] - 30, 146, 330, 8, "t") + rect(pl(300, 0)[0] - 50, 130, 60, 40, "m2", 4)
    for xx in (pl(90, 0)[0], pl(6, 0)[0]):
        s += poly([(xx - 3, 146), (xx + 3, 146), (xx, 142)], "ins")
    s += tol(40, 280, "ステータ穴と軸受穴の同軸度（ボーリングバーで一括）")
    ops.append(s)
    pl = Pl(140, 150, 1.0)
    s = title("洗浄し、冷却水路の漏れを確認")
    s += pl.g(ecase_sec()) + pl.g(path("M30 73 L160 73 M30 -73 L160 -73", "pres"))
    s += line(pl(190, 0)[0], 150, 420, 150, "cable") + circ(436, 130, 18, "m")
    ops.append(s)
    pl = Pl(140, 150, 1.0)
    s = title("ケースを加熱して膨らませ、ステータを焼ばめ")
    s += pl.g(ecase_sec()) + pl.g(rect(14, -64, 150, 128, "hotband"))
    s += '<g transform="translate(%s 150)">' % n(pl(20, 0)[0] - 150) + rect(0, -58, 130, 116, "m3") + rect(20, -30, 90, 60, "cu") + "</g>"
    s += arrow(40, 240, 160, 240, "挿入", 100, 256) + tol(300, 280, "しめしろ・位置")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ reducer (reuse gear sheets)
def reducer_detail():
    from il_d_drive import gear_detail
    return gear_detail()


def reducer_ops():
    g = gear_ops()
    s = title("低ひずみのため真空浸炭（減圧浸炭→高圧ガス冷却）")
    s += rect(40, 60, 400, 180, "m2", 80) + rect(80, 90, 320, 120, "hotin", 50)
    for i in range(4):
        s += gear(130 + i * 74, 150, 20, 28, 14, "w", 0, 1, 0.5)
    s += circ(240, 46, 18, "m") + tol(40, 280, "ひずみ・有効硬化層（粒界酸化なし）")
    vac = fin(s)
    return [g[0], g[2], g[3], vac, g[9], g[10], g[11]]


# ================================================================ ROTOR
def rotor_sec():
    s = Rev([(40, 10), (10, 14), (150, 56), (10, 14), (70, 10)]).svg()
    for k in (-1, 1):
        s += rect(60, k * 38 - 6, 150, 12, "chipd")
    return s


def rotor_detail():
    pl0, s = base("ev.rotor", 0, 20, 1.0)
    pl = Pl(40, 250, 0.7)
    s += pl.g(rotor_sec())
    notes = [("積層コア", "電磁鋼板を数百枚積層（かしめ・接着）"), ("永久磁石", "ネオジム焼結磁石をコアの穴に埋め込み（IPM）"),
             ("シャフト", "軸受部を研削。コアに圧入・焼ばめ"), ("エンドプレート", "磁石の飛び出し防止・バランス修正部")]
    s += bal(*pl0(140, 60), 170, 30, 1) + bal(*pl(130, -38), 300, 220, 2) + bal(*pl0(270, 104), 440, 60, 3) + bal(*pl0(212, 70), 360, 30, 4)
    return s, notes


def rotor_ops():
    ops = []
    s = title("高速プレスで電磁鋼板を打ち抜き、型内でかしめ積層")
    s += rect(20, 110, 440, 14, "strip")
    for i in range(5):
        x = 60 + i * 90
        s += rect(x - 30, 40, 60, 50, "t") + circ(x, 117, 5 + i * 3, "bg" if i < 4 else "w")
    s += Pl(410, 200, 0.4).g(il_parts.PARTS["ev.rotor"]()) if False else ""
    for k in range(10):
        s += rect(360, 150 + k * 5, 80, 4, "w", 1)
    s += arrow(40, 280, 300, 280, "帯材送り（300〜600spm）", 170, 272) + text(400, 220, "積層", "middle")
    ops.append(s)
    pl = Pl(80, 150, 1.2)
    s = title("磁石をコアの穴に挿入し、樹脂充填で固定")
    s += pl.g(rotor_sec())
    x, y = pl(120, -38)
    s += rect(x - 30, 40, 60, 40, "m3", 4) + rect(x - 20, 80, 40, y - 86, "chipd") + arrow(x + 50, 40, x + 50, y - 10, None)
    s += text(x + 58, 60, "N/S の向き", "start", "al")
    ops.append(s)
    pl = Pl(40, 150, 1.2)
    s = title("シャフトを旋削・研削し、コアに圧入")
    s += pl.g(rotor_sec()) + pl.g(mf("M0 -10 L40 -10 M210 -10 L280 -10"))
    x, y = pl(245, -10)
    s += wheel(x, y - 40, 36)
    ops.append(s)
    pl = Pl(40, 150, 1.2)
    s = title("高回転に備えてアンバランスを修正")
    s += pl.g(rotor_sec()) + pl.g(circ(55, -40, 3, "mfa") + circ(215, 30, 3, "mfa"))
    for x in (20, 260):
        xx, yy = pl(x, 10)
        s += circ(xx - 8, yy + 8, 8, "m") + circ(xx + 8, yy + 8, 8, "m")
    s += rot(*pl(130, 0), 14, 72, -60, 60) + tol(300, 280, "1.5〜2万min⁻¹で回る")
    ops.append(s)
    s = title("パルス磁界で磁石を着磁し、表面磁束を確認")
    s += circ(160, 150, 100, "m2") + circ(160, 150, 70, "bg")
    s += Pl(160, 150, 1.0).g(circ(0, 0, 64, "w") + "".join(rect(52 * math.cos(2 * math.pi * k / 8) - 7, 52 * math.sin(2 * math.pi * k / 8) - 5, 14, 10, "chipd") for k in range(8)))
    for k in range(8):
        a = 2 * math.pi * k / 8
        s += rect(160 + 86 * math.cos(a) - 8, 150 + 86 * math.sin(a) - 8, 16, 16, "cu")
    s += lightning(310, 60, 1.4) + chart(330, 150, 140, 80, "sine") + text(400, 246, "表面磁束分布", "middle", "sm")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ TURBO
def tw_front(cx, cy, r, cls="w", hot=False):
    s = circ(cx, cy, r, "h" if hot else cls)
    for k in range(11):
        a = 2 * math.pi * k / 11
        s += path("M%s %s Q%s %s %s %s" % (n(cx + r * 0.25 * math.cos(a)), n(cy + r * 0.25 * math.sin(a)),
                                           n(cx + r * 0.7 * math.cos(a + 0.5)), n(cy + r * 0.7 * math.sin(a + 0.5)),
                                           n(cx + r * math.cos(a + 0.2)), n(cy + r * math.sin(a + 0.2))), "o")
    s += circ(cx, cy, r * 0.22, "w2")
    return s


def turbo_detail():
    pl, s = base("engine.turbo", 0, 20, 1.3)
    notes = [("コンプレッサホイール", "アルミ。吸気を圧縮する翼（5軸削り出し）"), ("タービンホイール", "Ni基超合金の精密鋳造。900℃級の排気で回る"),
             ("センタハウジング", "軸受と潤滑油路。軸受穴の同軸度"), ("タービンハウジング", "耐熱鋳鋼。排気の渦巻き流路"), ("ウェイストゲート", "過給圧を逃がす弁")]
    s += bal(*pl(78, 90), 40, 40, 1) + bal(*pl(238, 104), 300, 280, 2) + bal(*pl(150, 104), 180, 280, 3)
    s += bal(*pl(214, 60), 440, 60, 4) + bal(*pl(276, 70), 440, 150, 5)
    return s, notes


def turbo_ops():
    ops = []
    s = title("ワックス模型をセラミックで覆い、真空中でNi基超合金を鋳込む")
    s += tw_front(110, 160, 60) + text(110, 244, "ワックス模型", "middle")
    s += arrow(180, 160, 220, 160, None)
    s += circ(290, 160, 72, "shell") + tw_front(290, 160, 58, hot=True) + text(290, 254, "シェル鋳型に注湯", "middle")
    s += path("M380 60 L430 60 L424 90 L386 90Z", "m2") + path("M406 90 Q400 110 330 110", "pour")
    s += tol(20, 290, "X線・蛍光浸透探傷で翼の欠陥を確認")
    ops.append(s)
    cy = 150
    s = title("タービンホイールと鋼製シャフトを摩擦圧接・電子ビーム溶接")
    s += Pl(40, cy, 1.0).g(Rev([(200, 10), (30, 14)]).svg()) + path("M270 110 L290 104 L290 196 L270 190Z", "w2") + ell(290, cy, 18, 46, "w")
    s += path("M268 %s q-6 18 0 36" % n(cy - 18), "hl") + heat(262, cy - 26, 2, 8)
    s += rot(140, cy, 10, 24, -60, 60, "回転", 140, cy + 52) + tol(300, 280, "接合強度・振れ")
    ops.append(s)
    s = title("アルミ鍛造ビレットから5軸加工で翼を削り出す")
    s += tw_front(200, 170, 90)
    s += '<g transform="rotate(-30 200 60)">' + rect(190, -40, 20, 110, "t") + rect(180, -90, 40, 50, "m2", 4) + "</g>"
    s += rot(200, 170, 104, 104, 20, 70) + text(320, 260, "C軸回転", "middle", "al") + text(320, 80, "工具傾斜（A軸）", "middle", "al")
    s += tol(20, 290, "翼厚・翼形状・面粗さ（三次元測定）")
    ops.append(s)
    pl, s = base("engine.turbo", 0, 20, 1.2)
    s = title("タービンハウジングを砂型鋳造し、フランジ面・取付穴を加工") + s
    x, y = pl(262, 60)
    s += tool("facemill", x + 18, y - 4, 90, 40, 40, spindle=True, feed=False)
    ops.append(s)
    pl = Pl(120, 150, 1.4)
    s = title("センタハウジングの軸受穴を精密加工・ホーニング")
    rv = Rev([(120, 50)], bore=[(0, 120, 16)])
    s += pl.g(rv.svg()) + pl.g(mf(rv.bore_d(0, 120)))
    s += tool("hone", *pl(100, 0), 180, 200, 30, spindle=True, feed=False)
    s += tol(40, 280, "軸受穴の真円度・同軸度・油路")
    ops.append(s)
    pl, s = base("engine.turbo", 0, 20, 1.2)
    s = title("回転体を組み、実回転域まで回してバランスを修正（VSR）") + s
    s += rot(*pl(150, 104), 30, 50, -60, 60) + chart(320, 200, 150, 80, "noise") + text(395, 294, "高速域の振動", "middle", "sm")
    ops.append(s)
    pl, s = base("engine.turbo", 0, 20, 1.2)
    s = title("ハウジングを組み、ウェイストゲートを調整・漏れを確認") + s
    s += arrow(*pl(290, 40), *pl(290, 70), None, both=True) + text(*pl(300, 40), "WG作動", "start", "al")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ INJECTOR
INJ = Rev([(40, 20), (60, 16), (10, 18), (100, 11), (40, 7)], bore=[(0, 250, 4)])


def injector_detail():
    pl = Pl(40, 150, 1.5)
    s = pl.g(INJ.svg())
    s += rect(420, 90, 54, 120, "m", 4) + text(447, 106, "先端拡大", "middle", "sm")
    s += path("M430 130 L462 130 L462 176 L446 196 L430 176Z", "cut") + line(446, 120, 446, 190, "stem") + circ(446, 196, 2.5, "bg")
    notes = [("ノズルボディ", "スイス型自動旋盤で加工"), ("噴孔", "φ0.1mm前後を複数。放電・レーザで加工"),
             ("シート", "ニードルが着座する円すい面。数μmのすき間"), ("ニードル", "ソレノイド／ピエゾで駆動"), ("燃料通路", "中心の細長い穴")]
    s += bal(*pl(150, -11), 160, 40, 1) + bal(446, 196, 440, 250, 2) + bal(452, 170, 460, 60, 3) + bal(*pl(120, 0), 200, 250, 4) + bal(*pl(60, 4), 80, 250, 5)
    return s, notes


def injector_ops():
    ops = []
    pl = Pl(80, 150, 1.4)
    s = title("小径の長物をスイス型自動旋盤で加工")
    s += rect(pl(-60, 0)[0], 100, 60, 100, "m2", 4) + pl.g(INJ.svg())
    s += rect(pl(110, 0)[0], 110, 30, 80, "m3", 3) + text(pl(125, 0)[0], 212, "ガイドブッシュ", "middle")
    s += tool("turn", *pl(150, -11), 90, 50, 14, spindle=False, rotarr=False, feed=False)
    s += arrow(40, 70, 140, 70, "主軸が材料を送る", 90, 62)
    ops.append(s)
    s = title("φ0.1mm前後の噴孔を放電（またはレーザ）で加工")
    s += path("M180 60 L300 60 L300 200 L240 260 L180 200Z", "cut") + line(240, 60, 240, 240, "stem")
    s += rect(236, 262, 8, 30, "t")
    for a in (-30, 0, 30):
        r = math.radians(a + 90)
        s += line(240, 258, 240 + 60 * math.cos(r), 258 + 60 * math.sin(r), "hid")
    s += sparks(240, 262, 10, 6, -170, -10) + tol(320, 250, "噴孔径・角度・入口R")
    ops.append(s)
    s = title("真空焼入れ・浸炭で耐摩耗性を持たせる")
    s += rect(40, 70, 400, 150, "m2", 60) + rect(70, 90, 340, 110, "hotin", 40)
    for i in range(4):
        s += Pl(90, 110 + i * 22, 0.9).g(INJ.svg())
    ops.append(s)
    s = title("シート部を内面研削し、ニードルを外径研削・ラッピング")
    s += path("M60 60 L200 60 L200 200 L130 270 L60 200Z", "cut") + rect(110, 60, 40, 180, "void") + circ(130, 230, 12, "gw") + rect(126, 40, 8, 190, "m3")
    s += rot(130, 230, 20, 20, 200, 320)
    s += Pl(260, 150, 1.0).g(Rev([(180, 8)]).svg()) + rect(270, 100, 120, 30, "gw", 4)
    s += tol(40, 290, "すき間 数μm・真円度（サブμm）")
    ops.append(s)
    pl = Pl(60, 150, 1.4)
    s = title("ソレノイド（またはピエゾ）を組み付け、全周レーザ溶接")
    s += pl.g(INJ.svg()) + rect(*pl(40, -26), 60 * 1.4, 52 * 1.4, "cu")
    x, y = pl(100, -16)
    s += line(x, y - 60, x, y - 4, "beam") + path("M%s %s L%s %s" % (n(x - 20), n(y - 100), n(x + 20), n(y - 100)), "o") + rect(x - 20, y - 110, 40, 40, "m3")
    s += rot(*pl(120, 0), 10, 30, -60, 60)
    ops.append(s)
    s = title("静的・動的流量、噴霧形状、漏れを全数確認")
    s += '<g transform="rotate(90 240 110)">' + Pl(140, 110, 0.7).g(INJ.svg()) + "</g>"
    s += spray_cone(240, 190, 90, 40, 60) + drops(240, 192, 5, 40, 56, 90) + tank(170, 230, 140, 50, 0.4)
    s += chart(330, 60, 140, 80, "step") + text(400, 156, "流量", "middle", "sm")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ ALUMINUM WHEEL
def wheel_sec(hot=False):
    c = "h" if hot else "cut"
    up = P([(0, -110), (8, -110), (8, -96), (70, -90), (70, -106), (80, -106), (80, -84), (20, -80), (20, -26), (34, -18), (34, -8), (20, -8), (0, -24)])
    s = path(up, c) + '<g transform="scale(1 -1)">' + path(up, "h" if hot else "w") + "</g>"
    s += cl(-10, 0, 100, 0)
    return s


WH_F = {"rim": "M8 -96 L70 -90 M0 -110 L8 -110 M70 -106 L80 -106", "face": "M0 -24 L0 -110", "hub": "M20 -8 L34 -8", "pcd": "M20 -18 L34 -18"}


def alwheel_detail():
    pl0, s = base("wheel.alwheel", -20, 20, 1.2)
    pl = Pl(350, 150, 1.0)
    s += rect(330, 30, 140, 240, "m", 4) + text(400, 46, "断面", "middle", "sm") + pl.g(wheel_sec())
    notes = [("リム", "タイヤがはまる部分。振れ・エア漏れ"), ("スポーク（意匠面）", "塗装＋ダイヤモンドカット"), ("ハブ穴・PCD", "ハブへの取付穴とボルト穴の配置"),
             ("フランジ・ビードシート", "タイヤのビードが当たる部分")]
    s += bal(*pl(40, -93), 470, 280, 1) if False else bal(*pl(40, -93), 300, 290, 1)
    s += bal(*pl0(160, 60), 60, 40, 2) + bal(*pl0(160, 100), 220, 280, 3) + bal(*pl(4, -108), 300, 30, 4)
    return s, notes


def alwheel_ops():
    ops = []
    from il_d_block import block_ops
    s = title("アルミを溶かして脱ガスし、保持炉へ")
    s += rect(40, 90, 120, 170, "m2", 6) + rect(54, 170, 92, 80, "h") + heat(70, 160, 4, 14)
    s += path("M160 180 Q200 170 226 200", "pour") + path(P([(210, 196), (300, 196), (292, 266), (218, 266)]), "m2") + rect(222, 210, 66, 52, "h")
    s += rect(250, 120, 10, 106, "m3") + bubbles(255, 256, 8, 50, 40) + text(255, 112, "回転脱ガス", "middle", "al")
    s += tol(320, 150, "水素量・介在物")
    ops.append(s)
    s = title("下から静かに溶湯を押し上げて金型に充填（低圧鋳造）")
    s += rect(40, 40, 400, 150, "m2") + Pl(240, 110, 0.6).g('<g transform="rotate(90)">' + wheel_sec(hot=True) + "</g>")
    s += rect(80, 206, 320, 80, "m2", 6) + rect(94, 220, 292, 60, "h") + rect(232, 170, 16, 60, "h")
    s += arrow(206, 260, 206, 200, None) + text(200, 234, "空気圧で押し上げ", "end", "al")
    ops.append(s)
    pl0, s = base("wheel.alwheel", 60, 30, 1.0)
    s = title("全数を自動X線検査（スポーク根元の引け巣）") + s
    s += rect(10, 120, 40, 50, "m3", 4) + rect(440, 30, 22, 240, "m2")
    x, y = pl0(160, 40)
    s += circ(x, y, 3, "poro") + circ(x, y, 12, "mfring")
    ops.append(s)
    s = title("溶体化・水冷・時効（T6）で強度を出す")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin")
    for i in range(3):
        s += Pl(70 + i * 125, 90, 0.36).g(il_parts.PARTS["wheel.alwheel"]())
    ops.append(s)
    pl = Pl(180, 150, 1.1)
    s = title("立形旋盤で表・裏の2工程に分けて旋削")
    s += pl.g(wheel_sec()) + pl.g(mf(WH_F["rim"]) + mf(WH_F["face"]))
    s += tool("turn", *pl(40, -94), 90, 50, 14, spindle=False, rotarr=False, feedlab="送り")
    s += rect(pl(-20, 0)[0] - 20, 270, 170, 14, "m2") + rot(*pl(40, 0), 90, 18, 20, 160) if False else rot(*pl(40, 140), 80, 14, 20, 160)
    s += tol(320, 150, "リム形状・振れ")
    ops.append(s)
    pl = Pl(180, 150, 1.1)
    s = title("ハブ穴・ボルト穴（PCD）・バルブ穴を加工")
    s += pl.g(wheel_sec()) + pl.g(mf(WH_F["hub"]) + mf(WH_F["pcd"]))
    s += tool("drill", *pl(34, -18), 180, 60, 8, spindle=True, feed=False)
    ops.append(s)
    pl0, s = base("wheel.alwheel", 60, 30, 1.0)
    s = title("チャンバ内でヘリウムを使い、リムの漏れを確認") + s
    s += rect(40, 20, 400, 270, "o", 20) + dots(60, 40, 360, 30, 14, "he") + rect(440, 120, 30, 60, "m3")
    ops.append(s)
    pl0, s = base("wheel.alwheel", 40, 30, 1.0)
    s = title("塗装し、意匠面をダイヤモンドバイトで削り出して光らせる") + s
    x, y = pl0(160, 30)
    s += tool("turn", x, y, 90, 50, 14, spindle=False, rotarr=False, feed=False) + spray_cone(420, 80, 150, 30, 60)
    s += rect(420, 70, 40, 20, "m3")
    ops.append(s)
    pl0, s = base("wheel.alwheel", 40, 30, 1.0)
    s = title("振れ・外観を確認し、抜取で回転曲げ・衝撃試験") + s
    s += rect(380, 60, 12, 60, "m3") + circ(386, 124, 4, "t") + chart(330, 200, 140, 80, "sine")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ BEARING
def bearing_sec():
    up = [(P([(0, -60), (40, -60), (40, -48), (0, -48)]), "cut"), (P([(0, -34), (40, -34), (40, -22), (0, -22)]), "cut")]
    s = "".join(path(d, c) for d, c in up) + circ(20, -41, 9, "ball")
    s += '<g transform="scale(1 -1)">' + "".join(path(d, "w") for d, c in up) + circ(20, -41, 9, "ball") + "</g>"
    s += rect(-2, -50, 4, 18, "rbx") + rect(38, -50, 4, 18, "rbx")
    s += cl(-10, 0, 50, 0)
    return s


def bearing_detail():
    pl0, s = base("common.bearing", -20, 20, 1.2)
    pl = Pl(380, 150, 1.8)
    s += rect(330, 30, 140, 240, "m", 4) + text(400, 46, "断面", "middle", "sm") + pl.g(bearing_sec())
    notes = [("外輪", "軌道面を研削・超仕上げ"), ("内輪", "軸にはまる。内径公差数μm"), ("鋼球", "真球度0.1μm級の等級品"), ("シール・グリース", "ゴムシールでグリースを封入")]
    s += bal(*pl(20, -54), 350, 280, 1) + bal(*pl(20, -28), 460, 280, 2) + bal(*pl(20, -41), 460, 90, 3) + bal(*pl(0, -41), 350, 90, 4)
    return s, notes


def bearing_ops():
    ops = []
    Y = 172
    pl = Pl(170, Y, 2.0)
    s = title("熱間鍛造・リングローリングで素材をつくり、旋削")
    s += chuck(*pl(0, 0), 150) + pl.g(bearing_sec()) + pl.g(mf("M40 -60 L40 -48"))
    s += tool("turn", *pl(41, -54), 180, 60, 14, spindle=False, rotarr=False, feed=False)
    s += rot(*pl(20, 0), 14, 130, -60, 60)
    ops.append(s)
    s = title("ずぶ焼入れ・焼戻し")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin") + conveyor(20, 200, 440)
    for i in range(6):
        s += circ(80 + i * 64, 176, 22, "w") + circ(80 + i * 64, 176, 14, "bg")
    ops.append(s)
    pl = Pl(190, Y, 2.0)
    s = title("幅面（両頭）→外径（センタレス）→軌道・内径を研削")
    s += pl.g(bearing_sec()) + pl.g(mf("M0 -60 L0 -48 M40 -60 L40 -48"))
    s += rect(pl(-40, 0)[0], 44, 70, 76, "gw", 4) + rect(pl(44, 0)[0], 44, 70, 76, "gw", 4)
    s += text(pl(20, 0)[0], 290, "両頭平面研削（幅面）", "middle") + tol(40, 290, "寸法・真円度")
    ops.append(s)
    pl = Pl(190, Y, 2.0)
    s = title("軌道面を超仕上げ")
    s += pl.g(bearing_sec()) + pl.g(mf("M8 -34 A12 8 0 0 0 32 -34"))
    x, y = pl(20, -30)
    s += rect(x - 10, y, 20, 16, "gw") + rect(x - 6, y + 16, 12, 60, "m3") + arrow(x - 50, y + 90, x + 50, y + 90, None, both=True) + text(x + 60, y + 94, "揺動", "start", "al")
    ops.append(s)
    s = title("鋼球：冷間圧造→フラッシング→熱処理→研削→ラッピング")
    s += rect(40, 60, 400, 36, "m2") + rect(40, 184, 400, 36, "m2")
    for i in range(8):
        s += circ(70 + i * 48, 140, 22, "ball")
    s += tol(40, 270, "真球度・等級（径のばらつき）")
    ops.append(s)
    pl = Pl(190, Y, 2.0)
    s = title("内外輪・鋼球・保持器を組み、グリースとシールを入れる")
    s += pl.g(bearing_sec()) + nozzle(*pl(-4, -41), 0, 50, 10) + text(pl(-4, 0)[0] - 30, pl(0, -41)[1] - 16, "グリース", "end", "al")
    ops.append(s)
    pl = Pl(170, Y, 2.0)
    s = title("回して振動・音を測り、異音品を除く（アンデロン値）")
    s += pl.g(bearing_sec()) + rot(*pl(20, 0), 14, 130, -60, 60) + chart(330, 60, 140, 80, "noise")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ E-COMP (scroll)
def scroll(cx, cy, r0=8, k=2.8, turns=3.2, cls="w", th=7):
    pts1, pts2 = [], []
    for i in range(160):
        t = i / 160 * turns * 2 * math.pi
        r = r0 + k * t
        pts1.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        pts2.append((cx + (r + th) * math.cos(t), cy + (r + th) * math.sin(t)))
    return path("M" + " L".join(n(x) + " " + n(y) for x, y in pts1 + pts2[::-1]) + "Z", cls)


def ecomp_detail():
    pl0, s = base("thermal.ecomp", -10, 20, 1.1)
    s += rect(330, 60, 140, 140, "m", 4) + text(400, 76, "固定スクロール", "middle", "sm") + circ(400, 136, 56, "w2") + scroll(400, 136, 4, 2.2, 3.0, "w", 6)
    notes = [("スクロール（渦巻き）", "壁厚・高さ数μm。可動と固定の2枚で圧縮"), ("モータ部", "インバータ一体の駆動モータ"), ("ハウジング", "アルミダイカスト。冷媒の吸入・吐出")]
    s += bal(430, 120, 460, 260, 1) + bal(*pl0(120, 116), 120, 280, 2) + bal(*pl0(230, 116), 280, 280, 3)
    return s, notes


def ecomp_ops():
    ops = []
    s = title("アルミを鍛造（または鋳造）してスクロール素材をつくる")
    s += rect(100, 40, 280, 40, "t") + rect(100, 220, 280, 40, "t") + ell(240, 150, 90, 40, "h")
    ops.append(s)
    s = title("渦巻き状の壁を高速輪郭加工")
    s += circ(200, 170, 100, "w2") + scroll(200, 170, 6, 3.4, 3.2, "w", 9)
    s += rect(262, 40, 12, 110, "t") + rect(248, 20, 40, 30, "m2") + rot(268, 60, 18, 6, 200, 340)
    s += arrow(320, 150, 360, 110, None) + text(366, 106, "輪郭に沿って移動", "start", "al")
    s += tol(320, 270, "壁厚・高さ 数μm・壁面粗さ")
    ops.append(s)
    pl0, s = base("thermal.ecomp", -10, 30, 1.1)
    s = title("ハウジングを多面加工（同軸度）") + s
    s += tool("boring", *pl0(230, 116), 180, 120, 12, spindle=True, feed=False)
    ops.append(s)
    pl0, s = base("thermal.ecomp", -10, 30, 1.1)
    s = title("モータとインバータを組み付け（絶縁・締付け）") + s
    x, y = pl0(120, 48)
    s += arrow(x, y - 60, x, y - 10, None)
    ops.append(s)
    pl0, s = base("thermal.ecomp", -10, 30, 1.1)
    s = title("冷媒で性能を確認し、ヘリウムで漏れを検査") + s
    s += dots(40, 40, 400, 20, 14, "he") + chart(330, 210, 140, 70, "rise")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ ALUMINUM FORGED ARM
def alarm_detail():
    pl, s = base("chassis.alarm", 0, 20, 1.3)
    notes = [("アーム本体", "アルミ鍛造。I形断面で軽量化"), ("ブッシュ穴", "ゴムブッシュを圧入"), ("ボールジョイント穴", "ナックルとつながる"), ("リブ", "鍛造で成形する補強")]
    s += bal(*pl(160, 84), 180, 30, 1) + bal(*pl(46, 118), 40, 280, 2) + bal(*pl(286, 106), 440, 280, 3) + bal(*pl(190, 90), 300, 40, 4)
    return s, notes


def alarm_ops():
    ops = []
    s = title("押出材・鋳造ビレットを切断し、加熱")
    s += Pl(20, 140, 1.0).g(Rev([(260, 26)]).svg()) + circ(300, 80, 50, "t") + line(290, 106, 290, 170, "cutl")
    s += rect(120, 220, 240, 40, "m2", 4) + rect(130, 228, 220, 24, "hotin")
    ops.append(s)
    pl, s = base("chassis.alarm", 0, 60, 1.3)
    s = title("前成形（ロール・ベンダ）後に型鍛造") + '<g class="hotgrp">' + s + "</g>"
    s += rect(20, 40, 440, 30, "t") + rect(20, 250, 440, 30, "t")
    ops.append(s)
    pl, s = base("chassis.alarm", 0, 40, 1.3)
    s = title("バリを抜く") + s + '<g transform="translate(0 40) scale(1.3)">' + path("M30 60 Q60 50 110 50 Q170 40 230 60 Q270 80 300 76 L300 140 Q250 144 214 128 Q168 110 112 116 Q70 122 40 150Z", "cutframe") + "</g>"
    ops.append(s)
    s = title("溶体化・焼入れ・時効（T6）で強度を出す")
    s += rect(40, 70, 400, 150, "m2", 6) + rect(50, 80, 380, 130, "hotin")
    for i in range(3):
        s += Pl(60 + i * 124, 110, 0.38).g(il_parts.PARTS["chassis.alarm"]())
    ops.append(s)
    pl, s = base("chassis.alarm", 0, 40, 1.3)
    s = title("ブッシュ穴・ボールジョイント穴を加工") + s
    s += ell(*pl(46, 118), 14 * 1.3, 13 * 1.3, "mfo") + ell(*pl(286, 106), 11 * 1.3, 11 * 1.3, "mfo")
    s += tool("boring", *pl(46, 118), 90, 60, 14, spindle=True, feed=False)
    ops.append(s)
    pl, s = base("chassis.alarm", 0, 40, 1.3)
    s = title("蛍光浸透探傷で鍛造割れを確認し、寸法を測定") + s
    s += rect(200, 20, 80, 24, "m3") + line(220, 44, 230, 130, "uv") + line(260, 44, 250, 130, "uv")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ BALL JOINT
def balljoint_detail():
    pl, s = base("chassis.balljoint", 0, 20, 1.3)
    notes = [("ボールスタッド", "冷間圧造。ボール部を焼入れ・研削"), ("ソケット", "樹脂シートを介してボールを保持"), ("ねじ部", "転造ねじ"), ("ダストブーツ", "泥水の浸入を防ぐ")]
    s += bal(*pl(226, 120), 440, 200, 1) + bal(*pl(226, 150), 360, 280, 2) + bal(*pl(60, 120), 60, 280, 3) + bal(*pl(226, 90), 440, 60, 4)
    return s, notes


def balljoint_ops():
    ops = []
    s = title("線材を冷間圧造でボールスタッドにし、ねじを転造")
    s += rect(10, 80, 460, 100, "m2", 4)
    for i in range(4):
        x = 70 + i * 110
        s += rect(x - 24, 92, 48, 76, "m", 3) + rect(x - 5, 110, 10, 50, "w") + circ(x, 110, 6 + i * 3, "w")
    s += arrow(40, 220, 440, 220, "多段で成形", 240, 240)
    ops.append(s)
    s = title("ボール部を高周波焼入れし、球面を研削")
    s += circ(200, 150, 70, "w") + rect(186, 210, 28, 80, "w") + path("M130 150 A70 70 0 0 1 270 150", "hotarc")
    s += wheel(360, 150, 50) + tol(40, 280, "真球度・粗さ")
    ops.append(s)
    s = title("ソケットを鍛造・旋削し、内面を仕上げる")
    s += path("M120 80 L320 80 L320 240 L120 240Z", "cut") + circ(220, 170, 56, "void") + rect(200, 80, 40, 40, "void")
    s += tool("boring", 220, 170, 90, 120, 12, spindle=True, feed=False)
    ops.append(s)
    pl, s = base("chassis.balljoint", 0, 30, 1.3)
    s = title("樹脂シートとスタッドを入れ、口元をかしめる") + s
    x, y = pl(226, 150)
    s += rect(x - 50, y + 36, 100, 18, "t") + arrow(x - 70, y + 45, x - 52, y + 45, None) + text(x - 76, y + 49, "口元かしめ", "end", "al")
    ops.append(s)
    pl, s = base("chassis.balljoint", 0, 30, 1.3)
    s = title("揺動トルク・回転トルク・ガタを確認") + s
    s += rot(*pl(226, 60), 20, 30, 200, 320) + chart(330, 190, 140, 80, "ramp")
    ops.append(s)
    return [fin(x) for x in ops]


# ================================================================ BOLT
def bolt_side(stage=5, hot=False):
    c = "h" if hot else "w"
    if stage == 0:
        return Rev([(200, 12)]).svg(hot=hot)
    s = Rev([(200, 12)], thread=[(110, 200)] if stage >= 3 else ()).svg(hot=hot)
    s = '<g transform="translate(40 0)">' + s + "</g>"
    s += rect(0, -30, 30, 60, c) + rect(30, -38, 10, 76, c)
    s += line(10, -30, 10, 30, "o thin") + line(20, -30, 20, 30, "o thin")
    return s


def bolt_detail():
    pl = Pl(40, 150, 1.6)
    s = pl.g(bolt_side())
    notes = [("頭部（六角・フランジ）", "冷間圧造で成形"), ("首下R", "応力集中を避ける丸み"), ("転造ねじ", "繊維状組織が切れず強い"), ("表面処理", "亜鉛フレークで防錆・摩擦係数を管理")]
    s += bal(*pl(15, -30), 60, 40, 1) + bal(*pl(40, -12), 160, 40, 2) + bal(*pl(170, -12), 360, 60, 3) + bal(*pl(120, 12), 260, 260, 4)
    return s, notes


def bolt_ops():
    ops = []
    s = title("線材を球状化焼鈍して柔らかくし、伸線で径を整える")
    s += rect(40, 60, 220, 110, "m2", 6) + rect(50, 70, 200, 90, "hotin") + circ(110, 115, 30, "w2") + circ(190, 115, 30, "w2")
    s += Pl(280, 220, 1.0).g(Rev([(80, 10)]).svg()) + rect(360, 196, 20, 48, "t") + Pl(380, 220, 1.0).g(Rev([(80, 7)]).svg())
    s += text(370, 270, "伸線ダイス", "middle")
    ops.append(s)
    s = title("パーツフォーマで頭部とフランジを多段に冷間圧造")
    s += rect(10, 60, 460, 150, "m2", 4)
    for i in range(4):
        x = 70 + i * 112
        hw = 14 + i * 6
        s += rect(x - 30, 76, 60, 120, "m", 3) + rect(x - 6, 110, 12, 80, "w") + rect(x - hw / 2, 100 - i * 3, hw, 12 + i * 3, "w")
    s += arrow(40, 240, 440, 240, "毎分100個以上", 240, 262)
    ops.append(s)
    pl = Pl(80, 150, 1.6)
    s = title("平ダイスで挟んで転がし、ねじを転造")
    s += pl.g(bolt_side(3)) + pl.g(mf("M150 -12 L240 -12"))
    x0, _ = pl(150, 0)
    s += rect(x0, 100, 160, 26, "t") + rect(x0, 174, 160, 26, "t") + arrow(x0 + 170, 110, x0 + 110, 110, None) + arrow(x0 + 20, 190, x0 + 80, 190, None)
    ops.append(s)
    s = title("メッシュベルト炉で焼入れ焼戻し")
    s += rect(40, 70, 400, 120, "m2", 6) + rect(50, 80, 380, 100, "hotin") + conveyor(20, 170, 440)
    for i in range(7):
        s += Pl(60 + i * 56, 160, 0.22).g(bolt_side())
    s += tol(40, 250, "硬さ・脱炭・遅れ破壊")
    ops.append(s)
    s = title("亜鉛フレーク塗装（ディップスピン）で防錆")
    s += tank(120, 140, 240, 120, 0.8) + rect(160, 80, 160, 100, "basket")
    for i in range(5):
        s += Pl(170, 100 + i * 16, 0.3).g(bolt_side())
    s += rect(232, 30, 16, 50, "m3") + rot(240, 60, 40, 10, 200, 340)
    ops.append(s)
    s = title("回転ガラステーブル上で寸法・外観を全数選別")
    s += ell(240, 200, 200, 40, "glp")
    for i in range(6):
        s += Pl(90 + i * 56, 196, 0.2).g(bolt_side())
    s += rect(200, 40, 80, 40, "m3", 4) + line(240, 80, 240, 180, "o thin dash") + tol(40, 290, "異品・寸法不良の流出防止")
    ops.append(s)
    return [fin(x) for x in ops]
