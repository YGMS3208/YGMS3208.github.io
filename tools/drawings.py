# -*- coding: utf-8 -*-
import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Scene

def jig_grinder():
    s = Scene(48, 156, k=0.92)
    s.shadow(95, 45, 92, 7)
    s.box(0, 0, 0, 200, 90, 14, "m")                 # bed
    s.box(18, 10, 14, 150, 70, 8, "pt")               # table
    s.box(30, 14, 22, 110, 56, 12, "w")              # workpiece plate
    for (hx, hy) in [(48, 30), (118, 30), (48, 58), (118, 58)]:
        s.disc_on_top(hx, hy, 34, 6.5, "dk")
    s.disc_on_top(84, 42, 34, 8, "dk")
    s.box(170, 60, 14, 26, 26, 128, "m", d=-200)      # column
    s.box(76, 70, 120, 110, 18, 22, "m", d=-150)       # head arm
    s.cyl((84, 42, 104), "z", 12, 38, "m", d=-120)     # spindle head
    s.cyl((84, 42, 58), "z", 3.5, 46, "m", cap=False, d=-110)  # quill
    s.cyl((84, 42, 32), "z", 5, 26, "t", d=-60)        # wheel in the hole
    s.arc((84, 42, 132), "z", 20, 3.4, 5.6)
    s.arc((84, 42, 66), "z", 9, -0.4, 1.6)
    s.arrow((214, 40, 104), (214, 40, 60), both=True)
    s.textp((214, 40, 82), "上下往復", anchor="start", cls="al", dx=8)
    s.textp((84, 42, 146), "遊星運動で穴径を広げる", anchor="middle", cls="al", dy=-6)
    s.textp((84, 42, 66), "砥石の自転", anchor="end", dx=-16, dy=2)
    s.textp((0, 0, 0), "焼入れした工作物", anchor="start", dx=4, dy=24)
    return s.svg("ジグ研削盤の原理図")

def profile_grinder():
    s = Scene(44, 154, k=0.95)
    s.shadow(110, 45, 100, 7)
    s.box(0, 0, 0, 220, 90, 14, "m")
    s.box(20, 12, 14, 170, 66, 8, "dk")               # magnetic chuck
    s.box(70, 34, 22, 60, 22, 30, "w")                # punch blank
    s.cyl((100, 18, 92), "y", 34, 10, "t", d=-30)
    s.cyl((100, 28, 92), "y", 30, 8, "t", d=-31)
    s.cyl((100, 36, 92), "y", 24, 6, "t", d=-32)
    s.box(196, 20, 22, 18, 30, 26, "pt")              # dresser block
    s.cyl((205, 35, 48), "z", 3, 14, "m")
    s.arrow((30, -14, 14), (180, -14, 14), both=True)
    s.arc((100, 18, 92), "y", 40, 2.2, 3.6)
    s.textp((100, 18, 132), "成形した砥石", anchor="middle", dy=-2)
    s.textp((58, 34, 64), "パンチ（工作物）", anchor="end")
    s.textp((205, 35, 66), "ドレッサ", anchor="middle", dy=-4)
    s.textp((205, 35, 66), "砥石の形をつくる", anchor="middle", cls="al", dy=-18)
    s.textp((105, -14, 14), "テーブル往復", anchor="middle", cls="al", dy=18)
    return s.svg("成形研削盤の原理図")

def vacuum_furnace():
    s = Scene(44, 150, k=0.9)
    s.shadow(110, 40, 110, 8)
    s.box(10, 20, 0, 210, 40, 10, "m")               # base
    s.cyl((0, 40, 50), "x", 40, 200, "m", cap=False, d=20)   # chamber shell
    s.cyl((200, 40, 50), "x", 40, 8, "dk", d=-40)            # door
    s.cyl((50, 40, 50), "x", 27, 110, "h", cap=False, d=-5)  # hot zone
    for i in range(3):
        s.box(66 + i * 30, 32, 34, 20, 18, 16, "w", d=-20 - i)
    s.textp((60, 40, 104), "真空中で加熱", anchor="middle", cls="al", dy=-4)
    s.textp((178, 40, 104), "窒素ガスで急冷", anchor="middle", cls="al", dy=-4)
    s.arrow((166, 40, 98), (166, 40, 74))
    s.arrow((188, 40, 98), (188, 40, 74))
    s.textp((96, 32, 34), "焼入れする部品", anchor="middle", dy=46)
    return s.svg("真空熱処理炉の原理図")

def lead_tester():
    s = Scene(36, 150, k=0.95)
    s.shadow(120, 40, 112, 7)
    s.box(0, 0, 0, 240, 80, 14, "m")
    s.box(10, 30, 14, 22, 22, 34, "m", d=10)
    s.box(196, 30, 14, 22, 22, 34, "m", d=5)
    s.cyl((32, 41, 40), "x", 8, 164, "w", d=0)
    for i in range(18):
        s.cyl((40 + i * 8.6, 41, 40), "x", 8.3, 1.6, "dk", cap=False, d=-1)
    s.box(40, 4, 14, 150, 8, 4, "pt", d=-30)
    s.box(104, 0, 18, 26, 16, 14, "pt", d=-35)
    s.box(114, 9, 32, 5, 4, 7, "t", d=-36)
    s.box(226, -2, 14, 12, 14, 14, "dk", d=-40)
    s.line((130, 7, 25), (226, 7, 25), "beam")
    s.arc((32, 41, 40), "x", 15, 1.0, 2.8)
    s.arrow((104, -14, 14), (150, -14, 14))
    s.textp((28, 41, 62), "1回転させる", anchor="middle", cls="al", dy=-6)
    s.textp((127, -14, 14), "1リード分の移動を測る", anchor="middle", cls="al", dy=18)
    s.textp((232, 5, 28), "レーザ測長器", anchor="end", dx=8, dy=-14)
    s.textp((120, 41, 50), "ボールねじ", anchor="middle", dy=-12)
    return s.svg("リード測定機の原理図")

# ---------- product images ----------
def precision_jig():
    s = Scene(60, 140, k=1.0)
    s.shadow(100, 45, 100, 8)
    s.box(0, 0, 0, 200, 90, 16, "w")                  # base plate (ground)
    s.box(20, 14, 16, 120, 60, 10, "w")               # sub plate
    for (hx, hy) in [(32, 24), (128, 24), (32, 64), (128, 64)]:
        s.disc_on_top(hx, hy, 26, 4, "dk")
    s.cyl((58, 44, 26), "z", 5, 16, "t", d=-5)        # round locating pin
    s.cyl((108, 44, 26), "z", 5, 16, "t", d=-6)       # diamond pin
    s.cyl((84, 26, 26), "z", 7, 4, "m", hole=4, d=-7)  # drill bushing
    s.cyl((84, 62, 26), "z", 7, 4, "m", hole=4, d=-8)
    s.box(156, 18, 16, 24, 16, 22, "dk", d=-20)        # clamps
    s.box(156, 56, 16, 24, 16, 22, "dk", d=-25)
    s.box(146, 22, 38, 34, 8, 6, "m", d=-21)
    s.box(146, 60, 38, 34, 8, 6, "m", d=-26)
    s.box(4, 70, 16, 12, 16, 12, "m", d=-40)          # stopper
    return s.svg("高精度治具の模式図")

def press_die():
    s = Scene(56, 152, k=1.0)
    s.shadow(104, 42, 104, 8)
    s.box(0, 0, 0, 210, 84, 20, "m")                  # lower die set
    s.box(30, 14, 20, 150, 56, 12, "w")               # die plate
    for i in range(4):
        s.disc_on_top(62 + i * 30, 40, 32, 5.5, "dk")
    s.box(14, 22, 32, 40, 36, 1.5, "cu", d=-2)        # strip (entering)
    for (gx, gy) in [(12, 10), (198, 10), (12, 74), (198, 74)]:
        s.cyl((gx, gy, 20), "z", 5, 70, "t", d=-(gy) - 10)
    s.box(0, 0, 90, 210, 84, 18, "m", d=-150)
    for i in range(4):
        s.cyl((62 + i * 30, 40, 52), "z", 5, 38, "w", d=-60 - i)
    s.arrow((-8, 20, 70), (-8, 20, 40))
    return s.svg("精密プレス金型（順送）の模式図")

def forming_rolls():
    s = Scene(52, 156, k=1.0)
    s.shadow(110, 40, 108, 8)
    s.box(0, 0, 0, 220, 80, 12, "m")
    s.box(0, 22, 12, 20, 36, 112, "m", d=30)
    s.box(200, 22, 12, 20, 36, 112, "m", d=-10)
    s.cyl((20, 40, 40), "x", 6, 180, "m", cap=False, d=5)
    s.cyl((56, 40, 40), "x", 18, 28, "w", d=0)
    s.cyl((84, 40, 40), "x", 18, 26, "w", r2=30, d=-1)
    s.cyl((110, 40, 40), "x", 30, 24, "w", r2=18, d=-1.5)
    s.cyl((134, 40, 40), "x", 18, 28, "w", d=-2)
    s.cyl((20, 40, 100), "x", 6, 180, "m", cap=False, d=-3)
    s.cyl((56, 40, 100), "x", 24, 28, "w", d=-4)
    s.cyl((84, 40, 100), "x", 24, 26, "w", r2=12, d=-5)
    s.cyl((110, 40, 100), "x", 12, 24, "w", r2=24, d=-5.5)
    s.cyl((134, 40, 100), "x", 24, 28, "w", d=-6)
    return s.svg("フォーミングロールの模式図")

ALL = {
 "jig-grinder": jig_grinder, "profile-grinder": profile_grinder,
 "vacuum-heat-treatment-furnace": vacuum_furnace, "lead-measuring-machine": lead_tester,
 "precision-jig": precision_jig, "precision-press-die": press_die, "roll-forming-rolls": forming_rolls,
}

if __name__ == "__main__":
    import re
    import os; site = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    idx = open(site + "/index.html", encoding="utf-8").read()
    style = re.search(r"<style>(.*?)</style>", idx, re.S).group(1)
    body = idx[idx.index("<body"):]
    defs = re.search(r"<svg[^>]*>.*?</svg>", body, re.S).group(0)
    cells = "".join(f'<figure class="stage" style="width:480px;display:inline-block;margin:8px">{fn()}<figcaption>{k}</figcaption></figure>' for k, fn in ALL.items())
    out = f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><link rel="stylesheet" href="/assets/fonts.e4e64f28e6.css"><style>{style}</style></head><body style="padding:10px;background:var(--bg)">{defs}{cells}</body></html>'
    open(site + "/_preview_draw.html", "w", encoding="utf-8").write(out)
    print("ok")
