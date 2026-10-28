# Folha de revisão por marca: para cada peça, a arte do ChatGPT, a mesma arte aplicada no 3D (poster) e a foto na loja (hero).
#   python3 revisao.py [marca ...]  -> revisao/<marca>.jpg (e uma versão pequena para conferência rápida)
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RAIZ, 'catalogo.json')))
F = ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc', 22, index=0)
CW, CH = 420, 420


def caber(arq, fundo=(242, 242, 242)):
    c = Image.new('RGB', (CW, CH), fundo)
    if os.path.exists(arq):
        im = Image.open(arq).convert('RGBA'); im.thumbnail((CW - 10, CH - 10))
        c.paste(im, ((CW - im.width) // 2, (CH - im.height) // 2), im)
    else:
        ImageDraw.Draw(c).text((20, CH // 2), 'pendente', fill=(180, 0, 0), font=F)
    return c


def marca(mid):
    m = CAT['marcas'][mid]
    pecas = m['pecas']
    folha = Image.new('RGB', (3 * CW + 40 + 260, len(pecas) * (CH + 10) + 60), 'white')
    d = ImageDraw.Draw(folha)
    d.text((10, 15), f"{m['nome']}: arte do ChatGPT | arte aplicada no 3D (poster) | 3D na loja (hero)", fill='black', font=F)
    for i, p in enumerate(pecas):
        y = 60 + i * (CH + 10)
        s = os.path.join(RAIZ, 'lotes', mid, 'saida', p['id'])
        d.text((10, y + 10), p['nome'].replace(' ' + m['nome'], ''), fill='black', font=F)
        d.text((10, y + 40), f"{p['larguraCm']:g}x{p['alturaCm']:g}x{p['profundidadeCm']:g} cm", fill=(90, 90, 90), font=F)
        for j, arq in enumerate((p['arteChatgpt'], os.path.join(s, 'poster.png'), os.path.join(s, 'hero.jpg'))):
            folha.paste(caber(arq), (260 + j * (CW + 10), y))
    os.makedirs(os.path.join(RAIZ, 'revisao'), exist_ok=True)
    folha.save(os.path.join(RAIZ, 'revisao', f'{mid}.jpg'), quality=85)
    pq = folha.copy(); pq.thumbnail((900, 4000)); pq.save(os.path.join(RAIZ, 'revisao', f'{mid}-pequena.jpg'), quality=70)


if __name__ == '__main__':
    for mid in (sys.argv[1:] or list(CAT['marcas'])):
        marca(mid)
