import os as _os
_B = _os.path.dirname(_os.path.abspath(__file__))
_D = _os.path.join(_os.path.dirname(_B), "data")

import json, glob
from parse import parse, KINDS
import il_parts, il_pictos, il_pictos_gear
from il_map import CATMAP, SYS_HERO, OPPIC
from il_dmap import build as dbuild
import pt

KMETA = {
 "素材": (75, .05, "材", "材料の受入・切断・混合・製織など、加工に入る前の準備工程。"),
 "鋳造": (45, .10, "鋳", "溶かした金属を型に流し込んで形をつくる。複雑な中空形状を一度につくれる。"),
 "鍛造": (62, .15, "鍛", "金属をたたき・押しつぶして形をつくる。転造・引抜き・曲げ・コイリングなどの塑性加工も含む。"),
 "プレス": (250, .09, "プ", "板材を金型で打ち抜き・曲げ・絞って形をつくる。"),
 "切削": (200, .11, "削", "刃物で削って寸法と形状を出す。旋削・フライス・穴あけ・ボーリング・レーザ加工を含む。"),
 "研削": (300, .13, "研", "砥石で削り、μm単位の寸法と面粗さに仕上げる。ホーニング・超仕上げ・ラッピングを含む。"),
 "歯車": (330, .14, "歯", "歯車・スプライン・ラック歯をつくる歯切りと、焼入れ後の歯面仕上げ。"),
 "熱処理": (25, .16, "熱", "加熱と冷却で金属の硬さ・強さ・組織を変える。"),
 "表面処理": (118, .10, "表", "洗浄・めっき・コーティング・ショットピーニングなどで表面の性質を整える。"),
 "接合": (92, .13, "接", "溶接・ろう付け・接着・機械的接合で部品同士をつなぐ。"),
 "成形": (155, .12, "成", "樹脂・ゴム・ガラス・粉末などを型や熱で成形する。"),
 "塗装": (355, .14, "塗", "防錆と外観のための塗膜をつくる。"),
 "巻線": (178, .10, "巻", "モータの銅線をコアに組み込む。"),
 "組立": (235, .04, "組", "部品を組み付け、締結・圧入・かしめ・充填で製品にまとめる。"),
 "電子": (220, .12, "電", "電子部品の実装と、半導体の組立（後工程）。"),
 "化学": (135, .12, "化", "電池の電極づくりなど、材料の化学的・物理的な処理が中心の工程。"),
 "検査": (268, .15, "検", "寸法・内部欠陥・機能を確かめ、品質を保証する。"),
 "物流": (240, .0, "物", "材料・部品・完成車の受入・搬送・出荷。"),
 "保全": (60, .03, "保", "金型や設備の維持・補修。"),
}
MATS = [
 {"n": "鋼板", "s": "冷延・熱延・めっき鋼板、ハイテン、ボロン鋼", "a": "板", "kw": ["鋼板", "ハイテン", "ボロン鋼"]},
 {"n": "棒鋼・線材", "s": "炭素鋼・肌焼鋼・ばね鋼・軸受鋼・耐熱鋼", "a": "棒", "kw": ["炭素鋼", "肌焼鋼", "機械構造用", "ばね鋼", "軸受鋼", "耐熱鋼", "合金鋼", "非調質鋼", "炭素工具鋼", "マルエージング", "ステンレス", "高合金鋼", "S45C"]},
 {"n": "鋳鉄", "s": "ねずみ鋳鉄・ダクタイル鋳鉄", "a": "Fe", "kw": ["鋳鉄", "FCD", "FC250"]},
 {"n": "アルミ", "s": "鋳造用・展伸用アルミ合金", "a": "Al", "kw": ["アルミ", "ADC12", "Al-Si"]},
 {"n": "樹脂・ゴム", "s": "PP・PC・PA・ウレタン・EPDM・天然ゴム", "a": "樹", "kw": ["PP", "ポリカーボネート", "PA", "PBT", "ABS", "HDPE", "樹脂", "ウレタン", "ゴム", "EPDM", "ナイロン", "ポリエステル"]},
 {"n": "ガラス", "s": "フロートガラスと中間膜", "a": "硝", "kw": ["フロートガラス"]},
 {"n": "電子・電池材料", "s": "半導体・電子部品・電池材料・電磁鋼板・銅線", "a": "電", "kw": ["電子部品", "半導体", "NCM", "電磁鋼板", "銅", "LED", "イメージセンサ", "セル"]},
]

systems = parse(sorted(glob.glob(_D + "/[0-9]*.txt")))
cats, groups, cidx = [], [], {}
for l in open(_D + "/cats.txt", encoding="utf-8"):
    if not l.strip():
        continue
    n, g, d = [x.strip() for x in l.rstrip("\n").split(" | ")]
    if g not in groups:
        groups.append(g)
    cidx[n] = len(cats)
    cats.append({"n": n, "g": groups.index(g), "d": d, "pi": CATMAP[n]})

used = set()
kidx = {k: i for i, k in enumerate(KINDS)}
out_sys = []
for s in systems:
    os_ = {"id": s["id"], "name": s["name"], "sub": s["sub"], "desc": s["desc"], "hero": SYS_HERO[s["id"]], "parts": []}
    for p in s["parts"]:
        op = {"id": p["id"], "name": p["name"], "mat": p["mat"], "desc": p["desc"], "ops": []}
        for o in p["ops"]:
            m = [[cidx[c], sp, mk] for c, sp, mk in o["m"]]
            x = [[cidx[c], sp, mk] for c, sp, mk in o["i"]]
            for r in m + x:
                used.add(r[0])
            od = {"n": o["name"], "k": kidx[o["kind"]], "d": o["desc"], "m": m, "x": x, "kp": o["k"]}
            ok = "%s.%s.%d" % (s["id"], p["id"], len(op["ops"]) + 1)
            if ok in OPPIC:
                od["pic"] = OPPIC[ok]
            op["ops"].append(od)
        os_["parts"].append(op)
    out_sys.append(os_)

unused = [c["n"] for i, c in enumerate(cats) if i not in used]
assert not unused, unused

kinds = [{"n": k, "h": KMETA[k][0], "c": KMETA[k][1], "a": KMETA[k][2], "d": KMETA[k][3]} for k in KINDS]
DET, DOPS = dbuild()
pool, pidx = [], {}
OIDX = {}
for k, lst in DOPS.items():
    ids = []
    for svg_ in lst:
        if svg_ not in pidx:
            pidx[svg_] = len(pool)
            pool.append(svg_)
        ids.append(pidx[svg_])
    OIDX[k] = ids
import il_gscene as GS
HERO = {"hob": GS.sc_hobbing(318, 228, 1.42, lab=False), "grind": GS.sc_gear_grind(318, 222, 1.42, lab=False),
        "pair": GS.sc_hypoid_pair(372, 212, 1.2, lab=False), "mesh": GS.sc_mesh(318, 226, 1.3, lab=False)}
ill = {"h": HERO, "p": {k: f() for k, f in il_parts.PARTS.items()}, "q": {k: f() for k, f in il_pictos.PICTOS.items()}, "d": DET, "o": OIDX, "pool": pool}
data = {"kinds": kinds, "cats": cats, "groups": groups, "mats": MATS, "systems": out_sys, "ill": ill, "pt": pt.build(systems)}
js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
tpl = open(_B + "/template.html", encoding="utf-8").read().replace("/*__ILCSS__*/", open(_B + "/il.css", encoding="utf-8").read())
tpl = tpl.replace("<!--ILDEFS-->", open(_B + "/il_defs.svg", encoding="utf-8").read())
html = tpl.replace("__DATA__", js)
open(_B + "/auto-atlas.html", "w", encoding="utf-8").write(html)
print("bytes", len(html.encode()), "groups", groups)
for mi, m in enumerate(MATS):
    n = [p["name"] for s in out_sys for p in s["parts"] if any(w in p["mat"] for w in m["kw"])]
    print(m["n"], len(n))
