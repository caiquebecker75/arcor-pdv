# Grade de coordenadas sobre o conceito, para marcar os cantos das faces que viram arte reta no 3D.
#   python3 grade.py <imagem> <saida.jpg> [x0 y0 x1 y1] [passo]   (coordenadas em pixels da imagem original)
import sys
from PIL import Image, ImageDraw, ImageFont

im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = map(int, sys.argv[3:7]) if len(sys.argv) >= 7 else (0, 0, *im.size)
passo = int(sys.argv[7]) if len(sys.argv) >= 8 else 50
F = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 13)
c = im.crop((x0, y0, x1, y1))
esc = min(1400 / c.width, 1000 / c.height)
c = c.resize((int(c.width * esc), int(c.height * esc)))
d = ImageDraw.Draw(c)
for x in range((x0 // passo + 1) * passo, x1, passo):
    X = (x - x0) * esc; forte = x % (passo * 2) == 0
    d.line((X, 0, X, c.height), fill=(0, 255, 255) if forte else (255, 0, 255), width=1)
    if forte: d.text((X + 2, 2), str(x), fill='yellow', font=F, stroke_width=2, stroke_fill='black')
for y in range((y0 // passo + 1) * passo, y1, passo):
    Y = (y - y0) * esc; forte = y % (passo * 2) == 0
    d.line((0, Y, c.width, Y), fill=(0, 255, 255) if forte else (255, 0, 255), width=1)
    if forte: d.text((2, Y + 2), str(y), fill='yellow', font=F, stroke_width=2, stroke_fill='black')
c.save(sys.argv[2], quality=80)
