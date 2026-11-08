# Reductor armónico 26:1 con 2 motores NEMA 17 (pensado para impresión 3D)

Dos NEMA 17 empujan la leva del reductor a través de una etapa de engranajes 1:1. Los pares se suman.
Piezas en `piezas/` (`.sc`, `.step`, `.stl`), ensamblaje en `ensamblaje/`, generadores en `scripts/`.

| | |
|---|---|
| Relación | 26:1 (flexspline 52 dientes, circular spline 54, módulo 0,8) |
| Etapa de motores | piñón A y B (módulo 1, 46 dientes) ↔ engranaje central (46 dientes), 1:1, motores a ±46 mm del eje |
| Salida | brida Ø30 de la flexspline, 4 agujeros Ø3,2 en círculo de Ø22 |
| Alto total | de Z = −40 (base de los motores) a Z = 44 (brida de salida) |

## Cambios respecto a la versión de 1 motor (`../reductor-armonico`) y por qué

La versión de 1 motor (módulo 0,4) **no se imprimía bien**: la punta del diente medía 0,4 mm, igual que un nozzle estándar, y la pared de la copa 0,75 mm.

| | 1 motor | 2 motores |
|---|---|---|
| Módulo | 0,4 | 0,8 |
| Diente flexspline | punta 0,4 mm, base 0,75, alto 0,7 | punta 0,8 mm, base 1,5, alto 1,4 |
| Pared de la copa | 0,75 mm | 1,2 mm (3 perímetros con nozzle 0,4) |
| Deflexión de la leva (a − b) | 0,8 mm | 1,6 mm |
| Ancho de dientes | 7,5 / 8 mm | 9 / 10 mm |
| Diafragma | 1 mm | 1,5 mm |

Para imprimir: orientar cada pieza con su eje de giro en Z para que las capas queden en el plano de los dientes (los dientes se imprimen con el perfil completo en cada capa), y empezar por la flexspline, que es la pieza crítica.

## Verificado

- Volúmenes de las piezas contra un cálculo independiente (coinciden).
- 90° de motor → −3,46° de salida, y 360° → −13,85° (1/26). Los dos motores giran a la vez.
- Sin conflictos ni piezas flotantes.
- Interferencia: los piñones engranan con el engranaje central sin chocar en un paso de diente completo (27 pares). Entre el reductor y la tapa o las placas no hay choques; solo flexspline contra leva (0,82 mm = la deflexión).
- Los ejes dentro de sus agujeros aparecen con 0,03 mm y volumen 0,0 (redondeo del mallado).

## Límites

- **Cuerpos rígidos.** La flexspline está sin deformar y la leva la solapa 0,8 mm. El GIF muestra la cinemática, no los dientes engranando.
- **Sin validar mecánicamente.** Material y espesor de la copa, juego de los dientes (0,1 mm en los engranajes) y fatiga no están calculados.
- **Falta** el rodamiento flexible entre leva y flexspline, el plano o prisionero en los ejes, los tornillos, y cojinetes en los apoyos (los ejes giran en agujeros lisos).
- **Sincronía eléctrica.** Los dos motores deben recibir la misma señal de paso, con dos drivers y la misma dirección. Si no, uno frena al otro.
- El engrane no tiene carcasa ni lubricación.
