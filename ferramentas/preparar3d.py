# Receita de 3D (ferramentas/receitas/<COD>.json) -> artes retas tiradas do próprio conceito aprovado + contornos de recorte
# + lotes2/<marca>/montagem.json para o gerador Blender da agência (tipo 'receita').
#   venv/bin/python preparar3d.py COD [COD ...]
# Numa chapa, "fonte" diz de onde vem a arte: quad = 4 cantos (sup. esq., sup. dir., inf. dir., inf. esq.) em pixels do conceito,
# l x a = medida real (cm) desse quadro; "estender" {topo, base, esq, dir} (cm) aumenta o quadro na mesma perspectiva.
# "forma" desenha o recorte em cm no quadro (origem no canto inferior esquerdo): ret [x0, z0, x1, z1, raio], circulo [cx, cz, r],
# poligono [[x, z], ...]; "fora" tira áreas; sem forma = o quadro inteiro. "mascara": "rembg" recorta pelo fundo.
import json, os, sys, shutil
import cv2, numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PX = 24          # pixels por cm na arte reta (limite 4096)
SIGLA = {'7B': '7belo', 'BT': 'butter-toffees', 'RK': 'rocklets', 'TG': 'tortuguita'}


def estender(q, l, a, e):
    q = np.array(q, float)
    tl, tr, br, bl = q
    up_l, up_r = (tl - bl) / a, (tr - br) / a          # 1 cm para cima em cada borda
    rt_t, rt_b = (tr - tl) / l, (br - bl) / l
    t, b, es, d = e.get('topo', 0), e.get('base', 0), e.get('esq', 0), e.get('dir', 0)
    tl = tl + up_l * t - rt_t * es; tr = tr + up_r * t + rt_t * d
    bl = bl - up_l * b - rt_b * es; br = br - up_r * b + rt_b * d
    return [tl, tr, br, bl], l + es + d, a + t + b


def retificar(img, quad, l, a):
    esc = min(PX, 4096 / max(l, a))
    W, H = int(round(l * esc)), int(round(a * esc))
    M = cv2.getPerspectiveTransform(np.float32(quad), np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
    return cv2.warpPerspective(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE), esc


def desenhar(forma, W, H, esc, valor, m):
    for f in forma:
        k, v = next(iter(f.items()))
        if k == 'ret':
            x0, z0, x1, z1 = v[:4]; r = v[4] if len(v) > 4 else 0
            p0, p1 = (int(x0 * esc), int(H - z1 * esc)), (int(x1 * esc), int(H - z0 * esc))
            if r:
                ri = int(r * esc)
                cv2.rectangle(m, (p0[0] + ri, p0[1]), (p1[0] - ri, p1[1]), valor, -1)
                cv2.rectangle(m, (p0[0], p0[1] + ri), (p1[0], p1[1] - ri), valor, -1)
                for cx, cy in ((p0[0] + ri, p0[1] + ri), (p1[0] - ri, p0[1] + ri), (p0[0] + ri, p1[1] - ri), (p1[0] - ri, p1[1] - ri)):
                    cv2.circle(m, (cx, cy), ri, valor, -1)
            else:
                cv2.rectangle(m, p0, p1, valor, -1)
        elif k == 'circulo':
            cv2.circle(m, (int(v[0] * esc), int(H - v[1] * esc)), int(v[2] * esc), valor, -1)
        elif k == 'elipse':
            cv2.ellipse(m, (int(v[0] * esc), int(H - v[1] * esc)), (int(v[2] * esc), int(v[3] * esc)), v[4] if len(v) > 4 else 0, 0, 360, valor, -1)
        elif k == 'poligono':
            cv2.fillPoly(m, [np.int32([[x * esc, H - z * esc] for x, z in v])], valor)


def contorno(m, esc, H, l):
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=cv2.contourArea)
    c = cv2.approxPolyDP(c, max(1.0, 0.0012 * cv2.arcLength(c, True)), True)[:, 0, :]
    pts = [[round(x / esc - l / 2, 2), round((H - y) / esc, 2)] for x, y in c]
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if area > 0 else pts[::-1]          # anti-horário visto da frente


def chapa(cod, k, pt, img, saida):
    f = pt.pop('fonte')
    quad, l, a = f['quad'], f['l'], f['a']
    if f.get('estender'):
        quad, l, a = estender(quad, l, a, f['estender'])
    arte, esc = retificar(img, quad, l, a)
    H, W = arte.shape[:2]
    m = np.zeros((H, W), np.uint8)
    desenhar(f.get('forma') or ([] if f.get('mascara') == 'rembg' else [{'ret': [0, 0, l, a]}]), W, H, esc, 255, m)
    if f.get('mascara') == 'rembg':
        from rembg import remove
        r = np.array(remove(Image.fromarray(cv2.cvtColor(arte, cv2.COLOR_BGR2RGB))))[:, :, 3]
        r = cv2.morphologyEx((r > 128).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        if f.get('zona'):                       # o recorte automático só vale dentro da zona (cm)
            z = np.zeros((H, W), np.uint8); desenhar(f['zona'], W, H, esc, 255, z); r = cv2.bitwise_and(r, z)
        m = cv2.bitwise_or(m, r)
    if f.get('fora'):
        desenhar(f['fora'], W, H, esc, 0, m)
    nome = f'{cod}-{k}.png'
    cv2.imwrite(os.path.join(saida, nome), arte)
    cv2.imwrite(os.path.join(saida, f'{cod}-{k}-mascara.png'), m)
    pt['arte'] = os.path.join(saida, nome)
    pt['contorno'] = contorno(m, esc, H, l)
    pt['uv'] = [-l / 2, l / 2, 0, a]
    return pt


def preparar(cod):
    rc = json.load(open(os.path.join(RAIZ, 'ferramentas', 'receitas', f'{cod}.json')))
    mid = SIGLA[cod[:2]]
    n = int(cod[3:])
    conceito = sorted(f for f in os.listdir(os.path.join(RAIZ, 'conceitos', mid)) if f.startswith(f'{n:02d}-') and f.endswith('.png'))[0]
    pid = conceito[3:-4]
    img = cv2.imread(os.path.join(RAIZ, 'conceitos', mid, conceito))
    lote = os.path.join(RAIZ, 'lotes2', mid)
    saida = os.path.join(lote, 'texturas')
    os.makedirs(saida, exist_ok=True)
    partes = [chapa(cod, k, pt, img, saida) if pt['t'] == 'chapa' and 'fonte' in pt else pt for k, pt in enumerate(rc['partes'])]
    base = json.load(open(os.path.join(RAIZ, 'lotes', mid, 'montagem.json')))
    for pr in base['produtos'].values():          # texturas das embalagens (as mesmas imagens que já temos)
        for chave in ('textura', 'recorte'):
            if pr.get(chave) and not os.path.exists(os.path.join(saida, pr[chave])):
                shutil.copy(os.path.join(RAIZ, 'lotes', mid, 'texturas', pr[chave]), saida)
    arq = os.path.join(lote, 'montagem.json')
    mont = json.load(open(arq)) if os.path.exists(arq) else {k: base[k] for k in ('marca', 'cores', 'produtos')} | {'pecas': []}
    peca = {'id': pid, 'cod': cod, 'tipo': 'receita', 'nome': rc.get('nome', pid), 'produtos': list(base['produtos']), 'faces': {},
            'conceito': os.path.join(RAIZ, 'conceitos', mid, conceito), 'receita': {k: v for k, v in rc.items() if k != 'partes'} | {'partes': partes}}
    mont['pecas'] = [x for x in mont['pecas'] if x['id'] != pid] + [peca]
    json.dump(mont, open(arq, 'w'), ensure_ascii=False, indent=1)
    print(cod, mid, pid, len(partes), 'partes')


if __name__ == '__main__':
    for c in sys.argv[1:]:
        preparar(c)
