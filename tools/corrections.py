#!/usr/bin/env python3
"""Corrections found in the expert review (2026-11). Text that lives only in the generated pages (from the base commit)
is fixed here; text that has a data file is fixed in that file instead. Every entry must still match, so a stale entry fails loudly."""
import glob, os, re
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(SITE)

FIX = [
 # cutting tools: PCD is for high-silicon cast aluminium in volume; most aluminium is cut with uncoated or DLC-coated carbide
 ("methods/machining/index.html",
  "一般に、アルミ合金にはダイヤモンド焼結体の工具、焼入れ鋼にはCBN工具が使われる。",
  "アルミ合金は刃先の鋭い無被覆またはDLC被覆の超硬工具が主流で、シリコンの多い鋳造アルミを量産で削る場合にダイヤモンド焼結体（PCD）の工具を使う。焼入れ鋼の仕上げにはCBN工具が使われる。"),
 # servo: quadrant glitches come from friction at reversal; mismatched following lag distorts a circle into an ellipse
 ("machine-tools/components/servo-motor/index.html",
  "複数の軸を同時に動かすとき、各軸の追従の遅れがそろわないと円弧がゆがみ、移動方向が反転する所に象限突起（小さな段差状の突起）が出る。これはNC装置の加減速制御や摩擦の補正で抑える。",
  "複数の軸を同時に動かすとき、各軸の追従の遅れ（サーボゲイン）がそろわないと、円弧は斜め45°方向につぶれた楕円になる。これとは別に、軸の移動方向が反転する所では、静止摩擦やロストモーション（バックラッシ・ねじれ）のために一瞬遅れが出て、象限突起（小さな段差状の突起）が残る。前者はゲインの調整で、後者はNC装置の反転時の補正（摩擦補正・バックラッシ補正）で抑える。"),
 ("machine-tools/components/servo-motor/index.html",
  "電池で位置を保持するアブソリュートエンコーダでは、電池が切れると原点の情報が失われるため、定期的に交換する。",
  "電池で位置を保持するアブソリュートエンコーダでは、電池が切れると原点の情報が失われるため、定期的に交換する。交換は取扱説明書に従い、多くの機種では制御電源を入れたまま行う（電源を切って外すと原点を失い、気付かずに動かすと衝突につながる）。"),
 ("machine-tools/components/cnc/index.html",
  "メモリ保持用の電池は、取扱説明書の手順に従って定期的に交換する。",
  "メモリ保持用の電池は、取扱説明書の手順に従って定期的に交換する。多くの機種では、データが消えないよう制御電源を入れたまま交換する。交換の前にバックアップを取る。"),
 # ball screw: growing compensation is a wear signal, not a fix
 ("machine-tools/components/ball-screw/index.html",
  "の補正機能でも打ち消す。",
  "の補正機能でも打ち消す。ただし、補正量が前回の測定より増えていくのは、ねじや支持軸受が摩耗しているサインである。補正を上乗せし続けて摩耗を隠さず、増え方を記録して交換の時期を判断する。"),
 # spindle: only for bearings not meant to be re-greased
 ("machine-tools/components/spindle/index.html",
  "グリース封入の軸受への追加給脂は発熱の原因になる。",
  "補給を想定していないグリース封入の軸受に追加で給脂すると、量が多すぎて発熱の原因になる。長く止めた後や軸受を交換した後は、回転数を段階的に上げるならし運転（各段10〜15分程度、メーカーの手順に従う）をしてから使う。"),
 # grinding: wheel speeds
 ("machine-tools/cylindrical-grinder/index.html",
  "砥石の周速は一般砥石で毎秒30〜45m程度が目安で、CBN（立方晶窒化ホウ素）砥石はそれより速い周速で使うことが多い。",
  "砥石の周速は一般砥石で毎秒30〜45m程度（量産機では45〜60m）が目安で、CBN（立方晶窒化ホウ素）砥石はビトリファイドボンドで毎秒60〜120m程度と、さらに速い周速で使うことが多い。使える上限は砥石に表示された最高使用周速度で決まる。"),
 # accuracy: standards are revised; cite the series without a stale year
 ("machine-tools/guide/machine-accuracy/index.html",
  "JIS B 6190-4:2008 工作機械試験方法通則－第4部：数値制御による円運動精度試験",
  "JIS B 6190-4 工作機械試験方法通則－第4部：数値制御による円運動精度試験（改正されることがあるため、最新版を確認する）"),
 # inspection: calibration (bias) and repeatability are different things
 ("methods/inspection/index.html",
  "定期的に校正し、繰り返し測ったときのばらつきを評価する。",
  "測定器は定期的に校正して偏り（真の値とのずれ）を確かめ、それとは別に、同じものを繰り返し測ったときのばらつき（繰返し性・再現性、%GRR）を評価する。%GRRは公差の10%以下なら良好、30%を超えると使えないとされることが多い。"),
]
# training: the "check it with the power on" note belongs only to the correct checks, not to the forbidden options
NOTE = "（動作は電源を入れてから確かめる）"

n = 0
for path, old, new in FIX:
    s = open(path, encoding="utf-8").read()
    if old not in s:
        raise SystemExit(f"corrections: not found in {path}: {old[:30]}")
    s = s.replace(old, new); open(path, "w", encoding="utf-8").write(s); n += 1
for path in glob.glob("machine-tools/*/training/index.html"):
    s = open(path, encoding="utf-8").read()
    s2 = re.sub(r'(\{"t":"[^"]*?)' + re.escape(NOTE) + r'("[^}]*?"req":false)', r"\1\2", s)
    # the same option also appears in the plain-text summary after the quiz
    if s2 != s: open(path, "w", encoding="utf-8").write(s2); n += 1
# equipment count: the list links 283 pages (the 4 added later were not counted in the old headings)
real = len([p for p in glob.glob("equipment/*/index.html") if "移動しました" not in open(p, encoding="utf-8").read()[:3000]])
for path in ["index.html", "equipment/index.html", "llms.txt"]:
    s = open(path, encoding="utf-8").read()
    s2 = s.replace("279種類", f"{real}種類").replace('<h2 class="d2">279の', f'<h2 class="d2">{real}の')
    if s2 != s: open(path, "w", encoding="utf-8").write(s2); n += 1
print("corrections:", n, "| equipment pages:", real)
