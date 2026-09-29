import il_d_block as B, il_d_engine as E, il_d_drive as D, il_d_chassis as C, il_d_ev as V
DMAP = {
 "engine.block": (B.block_detail, B.block_ops), "engine.head": (E.head_detail, E.head_ops), "engine.crank": (E.crank_detail, E.crank_ops),
 "engine.cam": (E.cam_detail, E.cam_ops), "engine.conrod": (E.rod_detail, E.rod_ops), "engine.piston": (E.piston_detail, E.piston_ops),
 "engine.valve": (E.valve_detail, E.valve_ops), "engine.turbo": (V.turbo_detail, V.turbo_ops), "engine.injector": (V.injector_detail, V.injector_ops),
 "drivetrain.gear": (D.gear_detail, D.gear_ops), "drivetrain.shaft": (D.shaft_detail, D.shaft_ops), "drivetrain.tmcase": (D.tmcase_detail, D.tmcase_ops),
 "drivetrain.valvebody": (D.valvebody_detail, D.valvebody_ops), "drivetrain.cvtpulley": (D.pulley_detail, D.pulley_ops),
 "drivetrain.hypoid": (D.hypoid_detail, D.hypoid_ops), "drivetrain.diffcase": (D.diffcase_detail, D.diffcase_ops), "drivetrain.cvj": (D.cvj_detail, D.cvj_ops),
 "chassis.knuckle": (C.knuckle_detail, C.knuckle_ops), "chassis.alarm": (V.alarm_detail, V.alarm_ops), "chassis.hubbearing": (C.hubbearing_detail, C.hubbearing_ops),
 "chassis.disc": (C.disc_detail, C.disc_ops), "chassis.caliper": (C.caliper_detail, C.caliper_ops), "chassis.hu": (C.hu_detail, C.hu_ops),
 "chassis.eps": (C.eps_detail, C.eps_ops), "chassis.balljoint": (V.balljoint_detail, V.balljoint_ops),
 "ev.rotor": (V.rotor_detail, V.rotor_ops), "ev.eaxlecase": (V.eaxlecase_detail, V.eaxlecase_ops), "ev.reducer": (V.reducer_detail, V.reducer_ops),
 "wheel.alwheel": (V.alwheel_detail, V.alwheel_ops), "thermal.ecomp": (V.ecomp_detail, V.ecomp_ops),
 "common.bolt": (V.bolt_detail, V.bolt_ops), "common.bearing": (V.bearing_detail, V.bearing_ops),
}


def build():
    det, ops = {}, {}
    for k, (fd, fo) in DMAP.items():
        body, notes = fd()
        det[k] = {"svg": body, "notes": notes}
        ops[k] = fo()
    return det, ops
