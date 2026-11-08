# Compone el GIF: exterior (motion.export_animation), corte Z=12 de la etapa de engranajes y corte Z=28 del reductor
# (solidcraft-cli snapshot --section). Los cuadros salen de /tmp/claude-0/ext2 y /tmp/claude-0/f2; ver README.md.
from PIL import Image, ImageDraw, ImageFont
def font(sz, bold=False):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""), sz)
    except Exception: return ImageFont.load_default(size=sz)
W, H = 1480, 800
frames = []
for k in range(72):
    ext = Image.open(f"/tmp/claude-0/ext2/frame-{k+1:04d}.png").convert("RGB").crop((40, 90, 860, 700)).resize((640, 476), Image.LANCZOS)
    gear = Image.open(f"/tmp/claude-0/f2/g{k:02d}.png").convert("RGB").crop((60, 30, 1140, 530)).resize((780, 361), Image.LANCZOS)
    red = Image.open(f"/tmp/claude-0/f2/r{k:02d}.png").convert("RGB").crop((20, 20, 780, 780)).resize((260, 260), Image.LANCZOS)
    im = Image.new("RGB", (W, H), (246, 247, 250)); d = ImageDraw.Draw(im)
    im.paste(ext, (20, 120)); im.paste(gear, (680, 120)); im.paste(red, (680, 500))
    d.text((20, 14), "Reductor armonico 26:1 con 2 motores NEMA 17", font=font(26, True), fill=(30, 34, 44))
    d.text((20, 54), f"Motores: {-5*k:5d} grados     Entrada de la leva: {5*k:4d} grados     Salida: {-5*k/26:6.2f} grados", font=font(19), fill=(30, 34, 44))
    d.text((20, 94), "Vista exterior", font=font(15), fill=(90, 96, 110))
    d.text((680, 94), "Corte Z=12: pinon A, engranaje central y pinon B (1:1, modulo 1, 46 dientes)", font=font(15), fill=(90, 96, 110))
    d.text((970, 520), "Corte Z=28:", font=font(15, True), fill=(30, 34, 44))
    for i, t in enumerate(["leva eliptica (rojo)", "flexspline, 52 dientes (oliva)", "circular spline, 54 dientes (naranja)", "", "Los dos motores giran juntos", "y suman su par en la leva."]):
        d.text((970, 548 + 24 * i), t, font=font(15), fill=(60, 66, 80))
    d.text((20, H - 26), "Cuerpos rigidos: la flexspline se muestra sin deformar y la leva la solapa 0,8 mm, que es la deflexion real.", font=font(14), fill=(90, 96, 110))
    frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
frames[0].save("/home/user/solidcraft/reductor-armonico-2-motores/ensamblaje/reductor_2_motores.gif", save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True, disposal=1)
