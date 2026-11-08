# Reductor armónico 40:1 para NEMA 17

Reductor de copa (strain wave gear) modelado con SolidCraft. Las piezas están en `piezas/`
(`.sc`, `.step`, `.stl`), el ensamblaje en `ensamblaje/` y los scripts que lo generan en `scripts/`.

| | |
|---|---|
| Relación | 40:1 (flexspline 80 dientes, circular spline 82, módulo 0,4) |
| Entrada | eje del motor Ø5, leva elíptica 30,5 × 28,9 mm (a − b = 0,8 mm = 2 × la deflexión de 0,4 mm) |
| Salida | brida Ø20 de la flexspline, 4 agujeros Ø3,2 en círculo de Ø14 |
| Fijación | adaptador 42,3 mm al motor (4 × M3 a 31 mm) y 4 tornillos pasantes M3 de adaptador, circular spline y tapa |
| Altura | motor + 24 mm sobre la cara del motor |

## Piezas

1. `01_motor_nema17`: motor de referencia (42,3 × 42,3 × 40, pilote Ø22).
2. `02_eje_motor`: eje Ø5 × 16 mm (acortado para no chocar con el fondo de la copa).
3. `03_adaptador`: placa con alojamiento del pilote, paso del eje y avellanados para los tornillos del motor.
4. `04_circular_spline`: anillo fijo con 82 dientes interiores y 4 orejas de fijación.
5. `05_flexspline`: copa con 80 dientes exteriores, pared de 0,75 mm, buje y brida de salida.
6. `06_generador_onda`: leva elíptica con cuellos para el eje.
7. `07_tapa`: tapa con guía de la salida.

## Ensamblaje y movimiento

El motor está fijo y el adaptador, el circular spline y la tapa van rígidos a él. El eje gira (`Entrada`), la leva va rígida al eje, y la flexspline gira (`Salida`) con un vínculo `Salida = −Entrada / 40`.

Verificado: 90° de entrada dan −2,25° de salida, y 720° dan −18°. Sin conflictos ni piezas flotantes.
`motion.interference` en los pasos 0 a 76 de 80 solo marca flexspline contra leva (0,42 mm), que es la deflexión.

El GIF `ensamblaje/reductor_armonico.gif` se arma con 72 cortes a Z=10 (`snapshot --section`) y 73 cuadros del exterior (`motion.export_animation`), compuestos con `scripts/componer_gif.py`.

## Límites de este modelo (leer antes de imprimir o fabricar)

- **Cuerpos rígidos.** SolidCraft no deforma piezas: la flexspline está sin deformar y la leva la solapa 0,4 mm en el eje mayor. El engrane real no se simula; el GIF muestra la cinemática y la relación, no los dientes entrando y saliendo.
- **Primera aproximación.** Perfil de diente trapezoidal, sin optimizar. Pared de 0,75 mm, material, juego y vida a fatiga no están calculados ni probados.
- **Falta** el rodamiento flexible entre leva y flexspline, el plano en el eje (D) o prisionero, los tornillos y la lubricación.
- El eje del motor se acorta a 16 mm; un NEMA 17 comercial trae 22–24 mm.
