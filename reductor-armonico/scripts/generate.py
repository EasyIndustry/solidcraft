"""Genera los scripts JSON de SolidCraft del reductor armonico para NEMA 17.

Reductor de copa 40:1  (flexspline 80 dientes, circular spline 82, modulo 0.4).
Todas las piezas se modelan YA en su posicion de ensamblaje (mm, eje Z = eje del motor,
cara frontal del motor en Z=0, el eje del motor sube).
"""
import json, math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))

NF, NC = 80, 82            # dientes flexspline / circular spline
R_FLEX_ROOT, R_FLEX_TIP = 15.65, 16.35   # radio de raiz y de punta del flexspline
R_CS_TIP, R_CS_ROOT = 16.45, 17.15       # circular spline (dientes hacia dentro)
R_BORE = 14.85                            # radio interior de la copa (pared 0.8)
R_RING = 18.6                             # radio exterior anillo y tapa
LUG = 20.5                                # distancia de las orejas de fijacion (a 22.5 grados)
R_LUG = 2.9                               # radio de cada oreja
R_WALL = 15.6                             # radio exterior de la pared de la copa
CAM_A, CAM_B = 15.25, 14.45               # semiejes de la leva (a-b = 0.8 = 2*0.4)

def teeth(n, r_a, r_b, tip_half, base_half):
    """Poligono dentado: por diente raiz-izq, punta-izq, punta-der, raiz-der.
    r_a = radio de raiz, r_b = radio de punta (cualquiera de los dos puede ser el mayor)."""
    tau = 2 * math.pi / n
    pts = []
    for i in range(n):
        c = i * tau
        for r, k in ((r_a, -base_half), (r_b, -tip_half), (r_b, tip_half), (r_a, base_half)):
            a = c + k * tau
            pts.append([round(r * math.cos(a), 4), round(r * math.sin(a), 4)])
    return pts

def sk(name, plane_off):
    return {"command": "sketch.create", "params": {"plane": "XY", "name": name, "offset": str(plane_off)}}
FIN = {"command": "sketch.finish", "params": {}}
def circ(x, y, d):
    return {"command": "sketch.circle.center", "params": {"center": [x, y], "diameter": d}}
def ext(dist, name=None, op=None, body=None):
    p = {"distance": dist}
    if name: p["name"] = name
    if op: p["operation"] = op
    if body: p["body_name"] = body
    return {"command": "solid.extrude", "params": p}
def poly(pts):
    return {"command": "sketch.line", "params": {"points": pts, "closed": True}}
LUGS = [[round(LUG*math.cos(math.radians(22.5+90*k)),4), round(LUG*math.sin(math.radians(22.5+90*k)),4)] for k in range(4)]

# ---------------------------------------------------------------- piezas
def motor():
    return [
        {"command": "solid.box", "params": {"length": 42.3, "width": 42.3, "height": 40, "corner": [-21.15, -21.15, -40], "operation": "new", "body_name": "Motor NEMA17"}},
        {"command": "solid.chamfer", "params": {"edges": [[21.15, 21.15, -20], [-21.15, 21.15, -20], [21.15, -21.15, -20], [-21.15, -21.15, -20]], "distance": 3, "name": "Esquinas motor"}},
        {"command": "solid.cylinder", "params": {"radius": 11, "height": 2, "base": [0, 0, 0], "operation": "join", "name": "Pilote motor"}},
        sk("TornillosMotor", 0), *[circ(x, y, 3) for x in (15.5, -15.5) for y in (15.5, -15.5)], FIN,
        ext("-4", name="Roscas motor", op="cut"),
    ]

def eje():
    return [{"command": "solid.cylinder", "params": {"radius": 2.5, "height": 16, "base": [0, 0, 0], "operation": "new", "body_name": "Eje motor"}}]

def adaptador():
    holes_motor = [[x, y] for x in (15.5, -15.5) for y in (15.5, -15.5)]
    return [
        {"command": "solid.box", "params": {"length": 42.3, "width": 42.3, "height": 6, "center": [0, 0, 3], "operation": "new", "body_name": "Adaptador"}},
        {"command": "solid.fillet", "params": {"edges": [[21.15, 21.15, 3], [-21.15, 21.15, 3], [21.15, -21.15, 3], [-21.15, -21.15, 3]], "radius": 4, "name": "Esquinas adaptador"}},
        {"command": "solid.cylinder", "params": {"radius": 11.2, "height": 2.2, "base": [0, 0, 0], "operation": "cut", "name": "Alojamiento pilote"}},
        {"command": "solid.cylinder", "params": {"radius": 4.5, "height": 8, "base": [0, 0, -1], "operation": "cut", "name": "Paso eje"}},
        sk("TornillosMotorAdaptador", 6), *[{"command": "sketch.point", "params": {"point": p}} for p in holes_motor], FIN,
        {"command": "solid.hole", "params": {"sketch": "TornillosMotorAdaptador", "diameter": 3.4, "type": "counterbore", "cb_diameter": 6, "cb_depth": 3, "name": "Agujeros motor"}},
        sk("RoscasFijacion", 6), *[{"command": "sketch.point", "params": {"point": p}} for p in LUGS], FIN,
        {"command": "solid.hole", "params": {"sketch": "RoscasFijacion", "diameter": 2.5, "depth": 5, "name": "Roscas fijacion"}},
    ]

def circular_spline():
    return [
        sk("PerfilCS", 6),
        circ(0, 0, 2 * R_RING),
        poly(teeth(NC, R_CS_ROOT, R_CS_TIP, 0.16, 0.30)),
        *[circ(x, y, 2*R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS],
        FIN, ext(8, name="Circular spline", body="Circular spline"),
    ]

def flexspline():
    holes = [[round(7 * math.cos(math.radians(45 + 90 * k)), 4), round(7 * math.sin(math.radians(45 + 90 * k)), 4)] for k in range(4)]
    return [
        sk("DientesFS", 6.5), poly(teeth(NF, R_FLEX_ROOT, R_FLEX_TIP, 0.16, 0.30)), circ(0, 0, 2 * R_BORE),
        FIN, ext(7.5, name="Banda dentada", body="Flexspline"),
        sk("ParedFS", 14), circ(0, 0, 2 * R_WALL), circ(0, 0, 2 * R_BORE), FIN, ext(3, name="Pared copa", op="join"),
        sk("FondoFS", 17), circ(0, 0, 2 * R_WALL), FIN, ext(1, name="Fondo copa", op="join"),
        sk("BujeFS", 18), circ(0, 0, 10), FIN, ext(3, name="Buje salida", op="join"),
        sk("BridaFS", 21), circ(0, 0, 20), FIN, ext(3, name="Brida salida", op="join"),
        sk("AgujerosBrida", 21), *[circ(x, y, 3.2) for x, y in holes], FIN, ext(3, name="Agujeros brida", op="cut"),
    ]

def onda():
    return [
        sk("Leva", 7), {"command": "sketch.ellipse", "params": {"center": [0, 0], "major": [CAM_A, 0], "minor_radius": CAM_B, "axes": False}},
        circ(0, 0, 5.04), FIN, ext(6.5, name="Leva eliptica", body="Generador de onda"),
        sk("CuelloInf", 6.2), circ(0, 0, 10), circ(0, 0, 5.04), FIN, ext(0.8, name="Cuello inferior", op="join"),
        sk("CuelloSup", 13.5), circ(0, 0, 10), circ(0, 0, 5.04), FIN, ext(2.5, name="Cuello superior", op="join"),
    ]

def tapa():
    return [
        sk("ParedTapa", 14), circ(0, 0, 2 * R_RING), circ(0, 0, 34.4),
        *[circ(x, y, 2*R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS],
        FIN, ext(4.5, name="Cuerpo tapa", body="Tapa"),
        sk("PlacaTapa", 18.5), circ(0, 0, 2 * R_RING), circ(0, 0, 10.4),
        *[circ(x, y, 2*R_LUG) for x, y in LUGS], *[circ(x, y, 3.4) for x, y in LUGS],
        FIN, ext(2, name="Placa tapa", op="join"),
    ]


def ensamblaje():
    comps = [("Motor", "Motor NEMA17", "#3a3d42", 1), ("Eje", "Eje motor", "#c9ced6", 1),
             ("Adaptador", "Adaptador", "#5b7a99", 1), ("CircularSpline", "Circular spline", "#d9822b", 0.45),
             ("Flexspline", "Flexspline", "#e0b93a", 1), ("GeneradorOnda", "Generador de onda", "#c0392b", 1),
             ("Tapa", "Tapa", "#9aa5b1", 0.30)]
    c = []
    for comp, body, col, op in comps:
        c += [{"command": "component.create", "params": {"name": comp, "parent": "root", "activate": False}},
              {"command": "component.move_bodies", "params": {"bodies": [body], "component": comp}},
              {"command": "appearance.assign", "params": {"components": [comp], "color": col, "opacity": op}}]
    Z = [0, 0, 1]
    o = lambda occ: {"occurrence": occ, "point": [0, 0, 0], "z": Z}
    c += [
        {"command": "occurrence.ground", "params": {"occurrence": "Motor:1", "grounded": True}},
        {"command": "joint.rigid_group", "params": {"occurrences": ["Motor:1", "Adaptador:1", "CircularSpline:1", "Tapa:1"]}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Entrada", "flip": True, "a": o("Motor"), "b": o("Eje")}},
        {"command": "joint.as_built", "params": {"type": "rigid", "a": "Eje", "b": "GeneradorOnda", "name": "Eje-leva", "at": o("Eje")}},
        {"command": "joint.create", "params": {"type": "revolute", "name": "Salida", "flip": True, "a": o("Motor"), "b": o("Flexspline")}},
        {"command": "joint.motion_link", "params": {"a": "Entrada", "b": "Salida", "ratio": -NC_NF_RATIO}},
        {"command": "motion.study", "params": {"name": "Giro", "steps": 80, "keys": [{"joint": "Entrada", "points": [[0, 0], [80, 720]]}]}},
    ]
    return c
NC_NF_RATIO = (NC - NF) / NF     # 1/40

PARTS = {"01_motor_nema17": motor, "02_eje_motor": eje, "03_adaptador": adaptador,
         "04_circular_spline": circular_spline, "05_flexspline": flexspline,
         "06_generador_onda": onda, "07_tapa": tapa}

def write(name, cmds):
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump({"commands": cmds}, f, indent=1)

if __name__ == "__main__":
    allc = []
    for n, fn in PARTS.items():
        c = fn(); write(n, c); allc += c
    write("_todas_las_piezas", allc)
    json.dump({"commands": allc + ensamblaje()}, open(os.path.join(OUT, "..", "ensamblaje", "ensamblaje.json"), "w"), indent=1)
    print({n: len(fn()) for n, fn in PARTS.items()})
