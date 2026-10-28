# Gera no ChatGPT (Codex do app, conta do Caique) a embalagem, o logo e a arte plana da face principal de cada peça,
# e prepara a arte na proporção exata da face (recorte da faixa ou repetição do módulo).
#   python3 chatgpt.py [marca ...]        (2 em paralelo; pula o que já existe; para a marca se o limite do dia bater)
import json, os, subprocess, sys, time, glob, shutil
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODEX = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex'
GEN = os.path.expanduser('~/.codex/generated_images')
CAT = json.load(open(os.path.join(RAIZ, 'catalogo.json')))
LIMITE = {'bateu': False}
FMT = {'paisagem': (1.5, 'paisagem 3:2 (1536x1024)'), 'retrato': (2 / 3, 'retrato 2:3 (1024x1536)'), 'quadrada': (1.0, 'quadrada 1:1 (1024x1024)')}


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def formato(A):
    if A >= 1.2: return 'paisagem'
    if A <= 0.83: return 'retrato'
    return 'quadrada'


def plano(A):
    """(formato, modo, fração da faixa). modo: corte (só recorte), faixa (conteúdo numa faixa), repete (módulo repetido)."""
    f = formato(A)
    r = FMT[f][0]
    if A > 5: return f, 'repete', 0.34
    if f == 'paisagem' and A > r * 1.08: return f, 'faixa', r / A
    if f == 'retrato' and A < r / 1.08: return f, 'faixa', A / r
    return f, 'corte', 1.0


SSH = ['ssh', '-i', os.path.expanduser('~/.ssh/agencia_motor'), '-o', 'ServerAliveInterval=30', 'motor@187.77.253.75']
RAW = 'https://raw.githubusercontent.com/caiquebecker75/arcor-pdv/main/kv/'


def rodar_servidor(prompt, ref, destino, proporcao):
    """ChatGPT da agência (chatgpt.com pela estação, Codex do servidor de reserva). Referência por link público."""
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    t0 = time.time()
    nome = os.path.basename(os.path.dirname(destino)) + '-' + os.path.basename(destino) + '.json'
    corpo = json.dumps({'prompt': prompt, 'proporcao': proporcao, 'referencias': [RAW + os.path.basename(ref)] if ref else []}, ensure_ascii=False)
    subprocess.run(SSH + [f'cat > tmp/arcor/pedidos/{nome}'], input=corpo, text=True, timeout=60)
    try:
        r = subprocess.run(SSH + [f'cd agencia/motor && npx tsx zz_arcor_img.ts ~/tmp/arcor/pedidos/{nome} 2>&1 | grep -E "^(URL|ERRO)" | tail -1'],
                           capture_output=True, text=True, timeout=1500)
        saida = r.stdout.strip()
    except subprocess.TimeoutExpired:
        saida = 'ERRO timeout'
    if saida.startswith('URL '):
        url = saida.split()[1]
        subprocess.run(['curl', '-sL', '-o', destino + '.tmp', url], timeout=300)
        try:
            Image.open(destino + '.tmp').convert('RGB').save(destino)
        except Exception as e:
            saida = f'ERRO download {e}'
        if os.path.exists(destino + '.tmp'): os.remove(destino + '.tmp')
    if 'limite' in saida.lower() or 'limit' in saida.lower():
        LIMITE['bateu'] = True
    ok = os.path.exists(destino)
    log('ok' if ok else 'FALHOU', os.path.basename(os.path.dirname(destino)), os.path.basename(destino), f'{time.time() - t0:.0f}s', '' if ok else saida[-240:])
    return ok


def rodar_codex(prompt, ref, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    t0 = time.time()
    cmd = [CODEX, 'exec', '--skip-git-repo-check', '-s', 'workspace-write', '-C', os.path.dirname(destino)]
    if ref: cmd += ['-i', ref]
    try:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=900)
        saida = (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        saida = 'timeout'
    if any(k in saida for k in ('usage_limit', 'out of credits', 'Usage limit', 'rate_limit')):
        LIMITE['bateu'] = True
        log('LIMITE do Codex:', saida[-300:].replace('\n', ' '))
    if not os.path.exists(destino):
        novos = [f for f in glob.glob(GEN + '/**/*.png', recursive=True) if os.path.getmtime(f) > t0]
        if novos:
            shutil.copy(max(novos, key=os.path.getmtime), destino)
    ok = os.path.exists(destino)
    log('ok' if ok else 'FALHOU', os.path.basename(os.path.dirname(destino)), os.path.basename(destino), f'{time.time() - t0:.0f}s', '' if ok else saida[-200:].replace('\n', ' '))
    return ok


def sem_fundo_branco(caminho, tol=28):
    im = Image.open(caminho).convert('RGB')
    marca = im.copy()
    w, h = marca.size
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(marca.getpixel(xy)) > 690:
            ImageDraw.floodfill(marca, xy, (255, 0, 255), thresh=tol)
    rgba = im.convert('RGBA')
    px, pm = rgba.load(), marca.load()
    for y in range(h):
        for x in range(w):
            if pm[x, y] == (255, 0, 255):
                px[x, y] = (255, 255, 255, 0)
    bb = rgba.getbbox()
    rgba.crop(bb).save(caminho)


def preparar_face(p):
    """Arte do ChatGPT -> PNG na proporção exata da face principal (lotes/<marca>/entrada/<id>-<face>.png)."""
    fw, fh = p['faceCm']
    A = fw / fh
    f, modo, frac = plano(A)
    im = Image.open(p['arteChatgpt']).convert('RGB')
    W, H = im.size
    if modo == 'repete':
        bh = int(H * frac); tile = im.crop((0, (H - bh) // 2, W, (H - bh) // 2 + bh))
        th = 600; tw = int(tile.width * th / tile.height); tile = tile.resize((tw, th), Image.LANCZOS)
        out_w = int(th * A); out = Image.new('RGB', (out_w, th))
        n = -(-out_w // tw)
        x0 = (out_w - n * tw) // 2
        for i in range(n): out.paste(tile, (x0 + i * tw, 0))
    else:
        if W / H > A: cw, ch = int(H * A), H
        else: cw, ch = W, int(W / A)
        out = im.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch))
    os.makedirs(os.path.dirname(p['arteFace']), exist_ok=True)
    out.save(p['arteFace'])


BASE = ('Use a imagem anexada, que é o KEY VISUAL OFICIAL da marca {marca} (Arcor), como referência obrigatória de marca: '
        'mesmo logo, mesma embalagem, mesmas cores, mesma tipografia e mesma linguagem visual ({visual}). ')
REGRA_TEXTO = ('Textos permitidos, exatamente assim e em português (nenhum outro texto, nenhum preço, nenhuma letra inventada): {textos}. '
               'Se algum texto não puder sair perfeito, deixe sem esse texto em vez de inventar letras. ')


def prompt_peca(m, p):
    fw, fh = p['faceCm']
    f, modo, frac = plano(fw / fh)
    if modo == 'faixa':
        eixo = 'horizontal centralizada ocupando {:.0f}% da ALTURA da imagem'.format(frac * 100) if f == 'paisagem' else 'vertical centralizada ocupando {:.0f}% da LARGURA da imagem'.format(frac * 100)
        comp = (f'Composição obrigatória: todo o conteúdo (logo, embalagem, frase) fica DENTRO de uma faixa {eixo}; fora da faixa só a '
                'continuação do fundo da arte, sem nenhum elemento, porque a imagem será recortada exatamente nessa faixa. ')
    elif modo == 'repete':
        comp = ('Composição obrigatória: MÓDULO DE REPETIÇÃO de régua, dentro de uma faixa horizontal centralizada ocupando 34% da altura da '
                'imagem: logo grande à esquerda, frase curta no meio e a embalagem à direita, fundo que continua igual nas bordas esquerda e '
                'direita para emendar lado a lado; fora da faixa só fundo liso. ')
    else:
        comp = 'Composição: a arte ocupa a imagem inteira, com margem de segurança de 5% nas bordas para textos e logo. '
    if p['tipo'] == 'fachada_loja':
        comp += ('IMPORTANTE: é a parede da fachada e no CENTRO fica uma porta de vidro com 30% da largura e 80% da altura, apoiada no chão: '
                 'deixe essa área central só com fundo, e distribua logo e frase à esquerda e embalagem à direita da porta. ')
    if p['tipo'] in ('display_chao', 'display_balcao', 'ponta_gondola', 'ilha', 'portal_corredor'):
        comp += 'É o HEADER (testeira) da peça: logo e frase grandes, legíveis a 3 metros. '
    return (BASE.format(marca=m['nome'], visual=m['visual']) +
            f"Crie a ARTE PLANA DE IMPRESSÃO da face principal de um(a) {p['nome']} para ponto de venda de supermercado "
            f"(face de {fw:.0f} x {fh:.0f} cm; função: {p['funcao'].lower()}). Arte chapada de ponta a ponta em vista frontal ortográfica: "
            'SEM mockup, SEM perspectiva, SEM peça em 3D, SEM loja, SEM sombra externa, SEM moldura e SEM marcas de corte. '
            'A embalagem aparece como no KV, sem redesenhar o rótulo. ' + comp +
            REGRA_TEXTO.format(textos=' | '.join(m['textos'])) +
            f"Formato {FMT[f][1]}.")


def prompt_packshot(m, destino):
    return (BASE.format(marca=m['nome'], visual=m['visual']) +
            f"Gere o PACKSHOT de estúdio da embalagem {m['produto']} exatamente como aparece no KV: uma única embalagem, totalmente frontal e reta "
            '(sem inclinação, sem perspectiva), inteira e centralizada, sobre fundo BRANCO PURO liso, sem sombra, sem reflexo, sem outros objetos. '
            'Não redesenhe o rótulo: copie logo, cores e textos da embalagem do KV; onde um texto não puder sair perfeito, deixe a área lisa. '
            'Formato retrato 2:3 (1024x1536).')


def prompt_logo(m, destino):
    return (BASE.format(marca=m['nome'], visual=m['visual']) +
            f"Recorte e reproduza SOMENTE o logotipo {m['nome']} exatamente como está no KV (mesmo desenho de letras, cores, contorno e efeitos), "
            'plano e de frente, centralizado, sobre fundo BRANCO PURO liso, sem nenhum outro elemento, sem sombra projetada. '
            'Formato paisagem 3:2 (1536x1024).')


def marca(mid):
    m = CAT['marcas'][mid]
    ref = os.path.join(RAIZ, 'kv', f'{mid}-ref.jpg')
    pasta = os.path.join(RAIZ, 'chatgpt', mid)
    tarefas = []
    for nome, fn, prop in (('packshot.png', prompt_packshot, 'retrato'), ('logo.png', prompt_logo, 'paisagem')):
        d = os.path.join(pasta, nome)
        if not os.path.exists(d): tarefas.append((fn(m, d), d, True, prop))
    for p in m['pecas']:
        fw, fh = p['faceCm']
        if not os.path.exists(p['arteChatgpt']): tarefas.append((prompt_peca(m, p), p['arteChatgpt'], False, plano(fw / fh)[0]))

    def uma(t):
        pr, d, recorta, prop = t
        for tentativa in range(2):
            if LIMITE['bateu']: return False
            if rodar_servidor(pr, ref, d, prop):
                if recorta: sem_fundo_branco(d)
                return True
        return False
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(uma, tarefas))
    for p in m['pecas']:
        if os.path.exists(p['arteChatgpt']) and not os.path.exists(p['arteFace']):
            preparar_face(p)
    falta = [p['id'] for p in m['pecas'] if not os.path.exists(p['arteFace'])]
    log(mid, 'pronta' if not falta else f'faltam {falta}')
    return not falta


if __name__ == '__main__':
    for mid in (sys.argv[1:] or list(CAT['marcas'])):
        marca(mid)
        if LIMITE['bateu']:
            log('parando: limite do Codex'); sys.exit(3)
