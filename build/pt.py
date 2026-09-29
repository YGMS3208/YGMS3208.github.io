"""Powertrain comparison model.
Quantity of each part per vehicle for five representative powertrains.
Parts not listed are fitted once to every vehicle. 0 = not fitted.
Values are typical configurations for a passenger car, used as rough guides only."""

TYPES = [
    {"id": "gas", "s": "ガソリン", "n": "ガソリン車", "en": "GASOLINE", "spec": "2.0L 直列4気筒（自然吸気）・8速AT・前輪駆動",
     "note": "エンジンと多段ATの部品が中心。歯車・軸・ケースの機械加工が最も多い基準の構成。"},
    {"id": "diesel", "s": "ディーゼル", "n": "ディーゼル車", "en": "DIESEL", "spec": "2.2L 直列4気筒ターボ・8速AT・4WD（SUV）",
     "note": "高圧燃料系（コモンレール）とターボ、DPF・SCRの排気後処理が加わる。4WDで後輪のデフも増える。"},
    {"id": "hev", "s": "ハイブリッド", "n": "ハイブリッド車", "en": "HYBRID", "spec": "1.8L 直列4気筒＋モータ2基・電気式無段変速",
     "note": "エンジンを残したまま、モータ・インバータ・電池を追加。ATの代わりに遊星歯車の動力分割機構を使う。"},
    {"id": "kei", "s": "軽", "n": "軽自動車", "en": "KEI CAR", "spec": "660cc 直列3気筒・CVT・前輪駆動",
     "note": "構成はガソリン車と同じだが、3気筒で部品数が減り、変速機はCVT。後輪はドラムブレーキが多い。"},
    {"id": "bev", "s": "EV", "n": "電気自動車", "en": "ELECTRIC", "spec": "モータ1基（e-Axle）・電池 約60kWh・前輪駆動",
     "note": "エンジン・変速機・燃料系・排気系が無くなり、電池・モータ・インバータ・e-Axleに置き換わる。"},
]

# order: gas, diesel, hev, kei, bev
ICE = [1, 1, 1, 1, 0]
Q = {
    # body
    "body.alhood": [1, 1, 1, 0, 1],
    "body.gigacast": [0, 0, 0, 0, 1],
    "body.fueltank": [1, 1, 1, 1, 0],
    # engine
    "engine.block": ICE, "engine.head": ICE, "engine.crank": ICE, "engine.engineassy": ICE,
    "engine.cam": [2, 2, 2, 2, 0],
    "engine.conrod": [4, 4, 4, 3, 0],
    "engine.piston": [4, 4, 4, 3, 0],
    "engine.valve": [16, 16, 16, 12, 0],
    "engine.turbo": [0, 1, 0, 0, 0],
    "engine.injector": [4, 4, 4, 3, 0],
    "engine.railpump": [0, 1, 0, 0, 0],
    "engine.exhaust": [1, 1, 1, 1, 0],
    # drivetrain
    "drivetrain.gear": [10, 10, 4, 4, 0],
    "drivetrain.shaft": [3, 3, 2, 2, 0],
    "drivetrain.tmcase": [1, 1, 1, 1, 0],
    "drivetrain.valvebody": [1, 1, 0, 1, 0],
    "drivetrain.cvtpulley": [0, 0, 0, 2, 0],
    "drivetrain.cvtbelt": [0, 0, 0, 1, 0],
    "drivetrain.torqueconv": [1, 1, 0, 1, 0],
    "drivetrain.hypoid": [0, 1, 0, 0, 0],
    "drivetrain.diffcase": [1, 2, 1, 1, 1],
    "drivetrain.cvj": [2, 4, 2, 2, 2],
    "drivetrain.tmassy": [1, 1, 1, 1, 0],
    # chassis
    "chassis.lowerarm": [2, 2, 2, 2, 2],
    "chassis.knuckle": [2, 2, 2, 2, 2],
    "chassis.alarm": [2, 2, 2, 0, 2],
    "chassis.spring": [4, 4, 4, 4, 4],
    "chassis.damper": [4, 4, 4, 4, 4],
    "chassis.hubbearing": [4, 4, 4, 4, 4],
    "chassis.disc": [4, 4, 4, 2, 4],
    "chassis.caliper": [4, 4, 4, 2, 4],
    "chassis.pad": [8, 8, 8, 4, 8],
    "chassis.balljoint": [2, 2, 2, 2, 2],
    # electrified
    "ev.cell": [0, 0, 1, 0, 1],
    "ev.pack": [0, 0, 1, 0, 1],
    "ev.batcase": [0, 0, 0, 0, 1],
    "ev.stator": [0, 0, 2, 0, 1],
    "ev.rotor": [0, 0, 2, 0, 1],
    "ev.motorshaft": [0, 0, 2, 0, 1],
    "ev.eaxlecase": [0, 0, 0, 0, 1],
    "ev.powermodule": [0, 0, 1, 0, 1],
    "ev.inverter": [0, 0, 1, 0, 1],
    "ev.planetary": [0, 0, 1, 0, 0],
    "ev.reducer": [0, 0, 0, 0, 3],
    "ev.eaxleassy": [0, 0, 0, 0, 1],
    # electrical / exterior / wheel / thermal
    "electrical.headlamp": [2, 2, 2, 2, 2],
    "exterior.bumper": [2, 2, 2, 2, 2],
    "wheel.tire": [4, 4, 4, 4, 4],
    "wheel.alwheel": [4, 4, 4, 4, 4],
    "thermal.ecomp": [0, 0, 1, 0, 1],
}


# display-only quantities (calculations use Q)
QD = {"ev.cell": ["", "", "約60セル", "", "約100セル"]}


def build(systems):
    keys = [s["id"] + "." + p["id"] for s in systems for p in s["parts"]]
    for k in Q:
        assert k in keys, k
    return {"types": TYPES, "q": {k: Q.get(k, [1, 1, 1, 1, 1]) for k in keys}, "qd": QD}
