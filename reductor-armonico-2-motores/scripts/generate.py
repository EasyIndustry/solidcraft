"""Reductor armonico 26:1 impulsado por DOS motores NEMA 17 (mm, eje Z = eje del reductor).

Los motores van a +-D del eje, caras en Z=0, ejes hacia +Z. Cada uno lleva un pinon (modulo 1,
46 dientes) que engrana 1:1 con un engranaje central sobre el eje de entrada de la leva,
asi los torques se suman y la relacion total es la del reductor armonico: 26:1.
Pila (Z): placa base 0-6 | engranajes 8-16 | placa superior 17-23 | circular spline 23-33 |
tapa 33-40.5 | brida de salida 41-44.
"""
import json, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
MOD = 0.8                    # modulo del reductor armonico (dientes imprimibles con nozzle 0.4)
NF, NC = 52, 54              # dientes flexspline / circular spline -> relacion 26:1
RF, RC = MOD * NF / 2, MOD * NC / 2          # radios primitivos 20.8 / 21.6
R_FLEX_TIP, R_FLEX_ROOT = RF + 0.7, RF - 0.7  # diente de 1.4 mm de alto
R_CS_TIP, R_CS_ROOT = RC + 0.1, RC + 1.5
WALL_T, W0 = 1.2, MOD        # pared de la copa (3 perimetros) y deflexion radial
R_WALL = 20.05               # justo bajo la raiz (20.1) para evitar contacto tangente
R_BORE = R_WALL - WALL_T
R_RING = R_CS_ROOT + 2.5
LUG, R_LUG = 27.5, 2.9
CAM_A, CAM_B = R_BORE + W0, R_BORE - W0     # a - b = 1.6 mm = 2 * deflexion
DZ = 17                      # el reductor sube 17 mm respecto a la version de un motor
D = 46.0                     # distancia motor - eje
M, ZG = 1.0, 46              # modulo y dientes (pinones y engranaje central)
G0, GW = 8, 8                # engranajes entre Z=8 y Z=16
COLS = [[x, y] for x in (23.2, -23.2) for y in (27, -27)]

def teeth(n, r_a, r_b, tip_half, base_half):
    tau = 2 * math.pi / n
    pts = []
    for i in range(n):
        c = i * tau
        for r, k in ((r_a, -base_half), (r_b, -tip_half), (r_b, tip_half), (r_a, base_half)):
            a = c + k * tau
            pts.append([round(r * math.cos(a), 4), round(r * math.sin(a), 4)])
    return pts

def gear(z, m, rot, backlash=0.1, nflank=7):
    """Poligono de un engranaje cilindrico de evolvente (20 grados), centrado en el origen."""
    rp = m * z / 2; rb = rp * math.cos(math.radians(20)); ra = rp + m; rr = rp - 1.25 * m
    inv = lambda a: math.tan(a) - a
    th = lambda r: (math.pi * m / 2 - backlash) / (2 * rp) + inv(math.radians(20)) - inv(math.acos(min(1, rb / r)))
    assert rr > rb
    rs = [rr + (ra - rr) * j / (nflank - 1) for j in range(nflank)]
    tau = 2 * math.pi / z; pts = []
    for i in range(z):
        c = rot + i * tau
        for r in rs: pts.append((r, c - th(r)))
        for r in reversed(rs): pts.append((r, c + th(r)))
    return [[round(r * math.cos(a), 4), round(r * math.sin(a), 4)] for r, a in pts]

def sk(name, off): return {"command": "sketch.create", "params": {"plane": "XY", "name": name, "offset": str(off)}}
FIN = {"command": "sketch.finish", "params": {}}
def circ(x, y, d): return {"command": "sketch.circle.center", "params": {"center": [x, y], "diameter": d}}
def ext(dist, name=None, op=None, body=None):
    p = {"distance": dist}
    if name: p["name"] = name
    if op: p["operation"] = op
    if body: p["body_name"] = body
    return {"command": "solid.extrude", "params": p}
def poly(pts): return {"command": "sketch.line", "params": {"points": pts, "closed": True}}
def pt(p): return {"command": "sketch.point", "params": {"point": p}}
def cyl(r, h, base, op, name, body=None, targets=None):
    p = {"radius": r, "height": h, "base": base, "operation": op, "name": name}
    if body: p["body_name"] = body
    if targets: p["targets"] = targets
    return {"command": "solid.cylinder", "params": p}
LUGS = [[round(LUG * math.cos(math.radians(22.5 + 90 * k)), 4), round(LUG * math.sin(math.radians(22.5 + 90 * k)), 4)] for k in range(4)]
SQ = lambda cx, cy, z: [[cx + sx * 21.15, cy + sy * 21.15, z] for sx in (1, -1) for sy in (1, -1)]

# ------------------------------------------------------------------ piezas
def motor(tag, cx):
    n = f"Motor {tag}"
    return [
        {"command": "solid.box", "params": {"length": 42.3, "width": 42.3, "height": 40, "corner": [cx - 21.15, -21.15, -40], "operation": "new", "body_name": n}},
        {"command": "solid.chamfer", "params": {"edges": SQ(cx, 0, -20), "distance": 3, "name": f"Esquinas motor {tag}"}},
        cyl(11, 2, [cx, 0, 0], "join", f"Pilote motor {tag}"),
        sk(f"TornillosMotor{tag}", 0), *[circ(cx + x, y, 3) for x in (15.5, -15.5) for y in (15.5, -15.5)], FIN,
        ext("-4", name=f"Roscas motor {tag}", op="cut"),
    ]
def eje_motor(tag, cx): return [cyl(2.5, 18, [cx, 0, 0], "new", f"Eje motor {tag}", body=f"Eje motor {tag}")]
def pinon(tag, cx):
    return [sk(f"Pinon{tag}", G0), poly([[cx + x, y] for x, y in gear(ZG, M, math.pi / ZG)]), circ(cx, 0, 5.04), FIN,
            ext(GW, name=f"Pinon {tag}", body=f"Pinon {tag}")]
def engranaje_central():
    return [sk("EngranajeCentral", G0), poly(gear(ZG, M, 0.0)), circ(0, 0, 5.04), FIN, ext(GW, name="Engranaje central", body="Engranaje central")]
def eje_entrada(): return [cyl(2.5, 35.5, [0, 0, 0.5], "new", "Eje entrada", body="Eje entrada")]
def placa_base():
    mx = [[sx * D + x, y] for sx in (1, -1) for x in (15.5, -15.5) for y in (15.5, -15.5)]
    return [
        {"command": "solid.box", "params": {"length": 140, "width": 62, "height": 6, "center": [0, 0, 3], "operation": "new", "body_name": "Placa base"}},
        {"command": "solid.fillet", "params": {"edges": [[sx * 70, sy * 31, 3] for sx in (1, -1) for sy in (1, -1)], "radius": 5, "name": "Esquinas placa base"}},
        *[cyl(11.2, 2.2, [sx * D, 0, 0], "cut", f"Alojamiento pilote {i}") for i, sx in enumerate((1, -1))],
        *[cyl(4.5, 8, [sx * D, 0, -1], "cut", f"Paso eje {i}") for i, sx in enumerate((1, -1))],
        cyl(2.6, 8, [0, 0, -1], "cut", "Apoyo eje entrada"),
        sk("TornillosMotorBase", 6), *[pt(p) for p in mx], FIN,
        {"command": "solid.hole", "params": {"sketch": "TornillosMotorBase", "diameter": 3.4, "type": "counterbore", "cb_diameter": 6, "cb_depth": 3, "name": "Agujeros motores"}},
        sk("TornillosColumnasBase", 0), *[pt(p) for p in COLS], FIN,
        {"command": "solid.hole", "params": {"sketch": "TornillosColumnasBase", "diameter": 3.4, "type": "counterbore", "cb_diameter": 6, "cb_depth": 3, "name": "Agujeros columnas"}},
    ]
def columnas():
    c = []
    for i, (x, y) in enumerate(COLS, 1):
        c += [cyl(4, 11, [x, y, 6], "new", f"Columna {i}", body=f"Columna {i}"),
              cyl(1.25, 11, [x, y, 6], "cut", f"Rosca columna {i}", targets=[f"Columna {i}"])]
    return c
def placa_superior():
    return [
        {"command": "solid.box", "params": {"length": 66, "width": 66, "height": 6, "center": [0, 0, 17 + 3], "operation": "new", "body_name": "Placa superior"}},
        {"command": "solid.fillet", "params": {"edges": [[sx * 33, sy * 33, 20] for sx in (1, -1) for sy in (1, -1)], "radius": 5, "name": "Esquinas placa superior"}},
        cyl(2.6, 8, [0, 0, 16], "cut", "Apoyo eje superior"),
        sk("TornillosColumnasSup", 23), *[pt(p) for p in COLS], FIN,
        {"command": "solid.hole", "params": {"sketch": "TornillosColumnasSup", "diameter": 3.4, "name": "Agujeros columnas sup"}},
        sk("RoscasFijacion", 23), *[pt(p) for p in LUGS], FIN,
        {"command": "solid.hole", "params": {"sketch": "RoscasFijacion", "diameter": 2.5, "depth": 5, "name": "Roscas fijacion"}},
    ]
def circular_spline():
    return [sk("PerfilCS", 6 + DZ), circ(0, 0, 2 * R_RING), poly(teeth(NC, R_CS_ROOT, R_CS_TIP, 0.16, 0.30)),
            *[circ(x, y, 2 * R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS], FIN,
            ext(10, name="Circular spline", body="Circular spline")]
def flexspline():
    holes = [[round(11 * math.cos(math.radians(45 + 90 * k)), 4), round(11 * math.sin(math.radians(45 + 90 * k)), 4)] for k in range(4)]
    z0 = 6 + DZ
    return [
        sk("DientesFS", z0 + 0.5), poly(teeth(NF, R_FLEX_ROOT, R_FLEX_TIP, 0.16, 0.30)), circ(0, 0, 2 * R_BORE), FIN, ext(9, name="Banda dentada", body="Flexspline"),
        sk("ParedFS", z0 + 9.5), circ(0, 0, 2 * R_WALL), circ(0, 0, 2 * R_BORE), FIN, ext(4, name="Pared copa", op="join"),
        sk("FondoFS", z0 + 13.5), circ(0, 0, 2 * R_WALL), FIN, ext(1.5, name="Fondo copa", op="join"),
        sk("BujeFS", z0 + 15), circ(0, 0, 12), FIN, ext(3, name="Buje salida", op="join"),
        sk("BridaFS", z0 + 18), circ(0, 0, 30), FIN, ext(3, name="Brida salida", op="join"),
        sk("AgujerosBrida", z0 + 18), *[circ(x, y, 3.2) for x, y in holes], FIN, ext(3, name="Agujeros brida", op="cut"),
    ]
def onda():
    z0 = 6 + DZ
    return [
        sk("Leva", z0 + 1), {"command": "sketch.ellipse", "params": {"center": [0, 0], "major": [CAM_A, 0], "minor_radius": CAM_B, "axes": False}}, circ(0, 0, 5.04), FIN,
        ext(8.5, name="Leva eliptica", body="Generador de onda"),
        sk("CuelloInf", z0 + 0.2), circ(0, 0, 10), circ(0, 0, 5.04), FIN, ext(0.8, name="Cuello inferior", op="join"),
        sk("CuelloSup", z0 + 9.5), circ(0, 0, 10), circ(0, 0, 5.04), FIN, ext(2.5, name="Cuello superior", op="join"),
    ]
def tapa():
    z0 = 6 + DZ
    return [
        sk("ParedTapa", z0 + 10), circ(0, 0, 2 * R_RING), circ(0, 0, 2 * (R_CS_ROOT + 0.1)),
        *[circ(x, y, 2 * R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS], FIN, ext(5.5, name="Cuerpo tapa", body="Tapa"),
        sk("PlacaTapa", z0 + 15.5), circ(0, 0, 2 * R_RING), circ(0, 0, 12.4),
        *[circ(x, y, 2 * R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS], FIN, ext(2, name="Placa tapa", op="join"),
    ]

PARTS = {
    "01_placa_base": placa_base, "02_motor_A": lambda: motor("A", D), "03_motor_B": lambda: motor("B", -D),
    "04_eje_motor_A": lambda: eje_motor("A", D), "05_eje_motor_B": lambda: eje_motor("B", -D),
    "06_pinon_A": lambda: pinon("A", D), "07_pinon_B": lambda: pinon("B", -D),
    "08_engranaje_central": engranaje_central, "09_eje_entrada": eje_entrada, "10_columnas": columnas,
    "11_placa_superior": placa_superior, "12_circular_spline": circular_spline, "13_flexspline": flexspline,
    "14_generador_onda": onda, "15_tapa": tapa,
}
COMPS = [  # componente, cuerpos, color, opacidad
    ("PlacaBase", ["Placa base"], "#5b7a99", 1), ("MotorA", ["Motor A"], "#3a3d42", 1), ("MotorB", ["Motor B"], "#3a3d42", 1),
    ("EjeMotorA", ["Eje motor A"], "#c9ced6", 1), ("EjeMotorB", ["Eje motor B"], "#c9ced6", 1),
    ("PinonA", ["Pinon A"], "#4aa3a2", 1), ("PinonB", ["Pinon B"], "#4aa3a2", 1), ("EngranajeCentral", ["Engranaje central"], "#2f8f8e", 1),
    ("EjeEntrada", ["Eje entrada"], "#e9edf2", 1), ("Columnas", [f"Columna {i}" for i in range(1, 5)], "#8a94a0", 1),
    ("PlacaSuperior", ["Placa superior"], "#5b7a99", 1), ("CircularSpline", ["Circular spline"], "#d9822b", 1),
    ("Flexspline", ["Flexspline"], "#e0b93a", 1), ("GeneradorOnda", ["Generador de onda"], "#d62f1f", 1), ("Tapa", ["Tapa"], "#aab4c0", 1)]

def ensamblaje():
    c = []
    for comp, bodies, col, op in COMPS:
        c += [{"command": "component.create", "params": {"name": comp, "parent": "root", "activate": False}},
              {"command": "component.move_bodies", "params": {"bodies": bodies, "component": comp}},
              {"command": "appearance.assign", "params": {"components": [comp], "color": col, "opacity": op}}]
    Z = [0, 0, 1]
    o = lambda occ, x=0: {"occurrence": occ, "point": [x, 0, 0], "z": Z}
    c += [
        {"command": "occurrence.ground", "params": {"occurrence": "PlacaBase:1", "grounded": True}},
        {"command": "joint.rigid_group", "params": {"occurrences": ["PlacaBase:1", "MotorA:1", "MotorB:1", "Columnas:1", "PlacaSuperior:1", "CircularSpline:1", "Tapa:1"]}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Motor A", "flip": True, "a": o("PlacaBase", D), "b": o("EjeMotorA", D)}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Motor B", "flip": True, "a": o("PlacaBase", -D), "b": o("EjeMotorB", -D)}},
        {"command": "joint.as_built", "params": {"type": "rigid", "a": "EjeMotorA", "b": "PinonA", "name": "Eje A-pinon", "at": o("EjeMotorA", D)}},
        {"command": "joint.as_built", "params": {"type": "rigid", "a": "EjeMotorB", "b": "PinonB", "name": "Eje B-pinon", "at": o("EjeMotorB", -D)}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Entrada", "flip": True, "a": o("PlacaBase"), "b": o("EjeEntrada")}},
        {"command": "joint.as_built", "params": {"type": "rigid", "a": "EjeEntrada", "b": "EngranajeCentral", "name": "Eje-engranaje", "at": o("EjeEntrada")}},
        {"command": "joint.as_built", "params": {"type": "rigid", "a": "EjeEntrada", "b": "GeneradorOnda", "name": "Eje-leva", "at": o("EjeEntrada")}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Salida", "flip": True, "a": o("PlacaBase"), "b": o("Flexspline")}},
        {"command": "joint.gear", "params": {"a": "Motor A", "b": "Entrada", "ra": M * ZG / 2, "rb": M * ZG / 2}},
        {"command": "joint.motion_link", "params": {"a": "Motor A", "b": "Motor B", "ratio": 1}},
        {"command": "joint.motion_link", "params": {"a": "Entrada", "b": "Salida", "ratio": -(NC - NF) / NF}},
        {"command": "motion.study", "params": {"name": "Giro", "steps": 72, "keys": [{"joint": "Motor A", "points": [[0, 0], [72, -360]]}]}},
    ]
    return c

def write(path, cmds):
    with open(path, "w") as f: json.dump({"commands": cmds}, f, indent=1)

if __name__ == "__main__":
    allc = []
    for n, fn in PARTS.items():
        cm = fn(); write(os.path.join(OUT, n + ".json"), cm); allc += cm
    write(os.path.join(OUT, "..", "ensamblaje", "ensamblaje.json"), allc + ensamblaje())
    print(len(PARTS), "piezas;", len(allc), "comandos")
