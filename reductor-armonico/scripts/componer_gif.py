# Compone el GIF a partir de los cortes (snapshot --section z=10) y del exterior (motion.export_animation).
# Los cuadros se generan antes en /tmp/claude-0/frames y /tmp/claude-0/ext; ver README.md.
from PIL import Image, ImageDraw, ImageFont
import glob
def font(sz, bold=False):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),):
        try: return ImageFont.truetype(p, sz)
        except Exception: pass
    return ImageFont.load_default(size=sz)
W,H,P=1160,720,560
frames=[]
for k in range(72):
    sec=Image.open(f"/tmp/claude-0/frames/s{k:02d}.png").convert("RGB").crop((30,30,870,870)).resize((P,P),Image.LANCZOS)
    ext=Image.open(f"/tmp/claude-0/ext/frame-{k+1:04d}.png").convert("RGB").crop((110,150,790,830)).resize((P,P),Image.LANCZOS)
    im=Image.new("RGB",(W,H),(246,247,250)); d=ImageDraw.Draw(im)
    im.paste(ext,(20,110)); im.paste(sec,(580,110))
    d.text((20,16),"Reductor armonico 40:1 para NEMA 17",font=font(26,True),fill=(30,34,44))
    d.text((20,54),f"Entrada (motor): {10*k:4d} grados      Salida: {-10*k/40:6.2f} grados",font=font(20),fill=(30,34,44))
    d.text((20,84),"Vista exterior",font=font(16),fill=(90,96,110))
    d.text((580,84),"Corte a Z=10: leva (rojo), flexspline 80 dientes (oliva), circular spline 82 (naranja)",font=font(14),fill=(90,96,110))
    d.text((20,H-34),"Modelo de cuerpos rigidos: la flexspline se muestra sin deformar; la leva la solapa 0,4 mm, que es la deflexion real.",font=font(14),fill=(90,96,110))
    frames.append(im.quantize(colors=128,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE))
frames[0].save("/home/user/solidcraft/reductor-armonico/ensamblaje/reductor_armonico.gif",save_all=True,append_images=frames[1:],duration=70,loop=0,optimize=True,disposal=1)
