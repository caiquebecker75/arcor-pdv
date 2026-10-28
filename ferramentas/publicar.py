# Publica tudo: páginas de AR (repo ar, uma por marca), catálogo (repo arcor-pdv, GitHub Pages) e pasta do Drive
# (servidor da agência, dentro de PEÇAS de cada marca).
#   python3 publicar.py [ar] [site] [drive]   (sem argumento = tudo)
import json, os, re, shutil, subprocess, sys, time, html
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RAIZ, 'catalogo.json')))
AR = os.path.expanduser('~/ar-75lab')
V = int(time.time()) % 100000
PAREDE = {'regua', 'wobbler', 'stopper', 'testeira', 'clipstrip'}
SSH = ['ssh', '-i', os.path.expanduser('~/.ssh/agencia_motor'), 'motor@187.77.253.75']
URL_AR = 'https://projetos.75lab.com.br/ar/arcor-{}/'
URL_SITE = 'https://projetos.75lab.com.br/arcor-pdv/'


def sh(*c, cwd=None):
    r = subprocess.run(c, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def saida(mid, pid):
    return os.path.join(RAIZ, 'lotes', mid, 'saida', pid)


def pronto(mid, p):
    s = saida(mid, p['id'])
    return all(os.path.exists(os.path.join(s, a)) for a in ('modelo.glb', 'modelo.usdz', 'poster.png'))


def curto(p, m):
    return p['nome'].replace(' ' + m['nome'], '')


def jpg(src, dst, lado=1400, q=84):
    if not os.path.exists(src): return False
    im = Image.open(src).convert('RGB'); im.thumbnail((lado, lado)); im.save(dst, quality=q); return True


def ar():
    modelo = open(os.path.join(AR, 'semp-split-hw', 'index.html'), encoding='utf-8').read()
    for mid, m in CAT['marcas'].items():
        d = os.path.join(AR, f'arcor-{mid}'); os.makedirs(d, exist_ok=True)
        itens = []
        for p in m['pecas']:
            if not pronto(mid, p): continue
            s = saida(mid, p['id'])
            shutil.copy(os.path.join(s, 'modelo.glb'), os.path.join(d, f"{p['id']}.glb"))
            shutil.copy(os.path.join(s, 'modelo.usdz'), os.path.join(d, f"{p['id']}.usdz"))
            im = Image.open(os.path.join(s, 'poster.png')); im.thumbnail((1200, 1200)); im.save(os.path.join(d, f"{p['id']}-poster.webp"), quality=82)
            it = {'id': p['id'], 'nome': curto(p, m), 'alt': f"{p['nome']} em 3D", 'src': f"{p['id']}.glb?v={V}", 'ios': f"{p['id']}.usdz?v={V}", 'poster': f"{p['id']}-poster.webp?v={V}"}
            if p['id'] in PAREDE: it['posicionamento'] = 'wall'
            itens.append(it)
        if not itens: continue
        h = re.sub(r'(<script type="application/json" id="modelos">)(.*?)(</script>)', lambda x: x.group(1) + '\n' + json.dumps(itens, ensure_ascii=False, indent=1) + '\n' + x.group(3), modelo, flags=re.S)
        for a, b in (('semp-split-hw', f'arcor-{mid}'), ('SEMP · Lançamento Split HW', f"Arcor · {m['nome']}"), ('Projeto 75 LAB para SEMP', 'Projeto 75 LAB para Arcor'),
                     ('do lançamento SEMP Split HW', f"de {m['nome']}"), ('SEMP Split HW', m['nome']), ('quinze peças', 'quinze peças')):
            h = h.replace(a, b)
        h = re.sub(r'og\.jpg\?v=\d+', f'og.jpg?v={V}', h)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(h)
        hero = next((os.path.join(saida(mid, p['id']), 'hero.jpg') for p in m['pecas'] if os.path.exists(os.path.join(saida(mid, p['id']), 'hero.jpg'))), None)
        if hero:
            im = Image.open(hero).convert('RGB'); w, hh = im.size; c = im.crop((0, (hh - w * 630 // 1200) // 2, w, (hh - w * 630 // 1200) // 2 + w * 630 // 1200)).resize((1200, 630)); c.save(os.path.join(d, 'og.jpg'), quality=85)
        sh('node', os.path.join(AR, 'tools', 'qr-png.mjs'), URL_AR.format(mid), os.path.join(d, 'qr.png'), cwd=os.path.join(AR, 'tools'))
    readme = os.path.join(AR, 'README.md'); t = open(readme, encoding='utf-8').read()
    if 'arcor-7belo' not in t:
        linhas = ''.join(f"| `arcor-{mid}/` | Arcor, {m['nome']}: 15 peças de PDV (leves, médias e pesadas) numa página, 3D e arte do ChatGPT | de 15 x 15 cm (wobbler) a 400 x 320 cm (fachada) |\n" for mid, m in CAT['marcas'].items())
        t = t.replace('| `codice-displays/`', linhas + '| `codice-displays/`', 1); open(readme, 'w', encoding='utf-8').write(t)
    sh('git', 'add', 'README.md', *[f'arcor-{mid}' for mid in CAT['marcas'] if os.path.isdir(os.path.join(AR, f'arcor-{mid}'))], cwd=AR)
    print(sh('git', 'commit', '-m', 'Arcor: peças de PDV em AR (7Belo, Butter Toffees, Rocklets, Tortuguita)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>', cwd=AR)[1][-200:])
    print(sh('git', 'push', '-q', cwd=AR)[1][-300:])


CSS = '''
:root{--fundo:#F5F5F0;--tinta:#141414;--suave:#6b6b66;--linha:#dcdcd4;--cartao:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--fundo);color:var(--tinta);font:15px/1.5 Lexend,system-ui,sans-serif}
header{padding:40px 24px 8px;max-width:1280px;margin:auto}h1{font:400 clamp(34px,5vw,64px)/1 Anton,sans-serif;margin:0 0 10px;letter-spacing:.5px}
.sub{color:var(--suave);max-width:760px}nav{position:sticky;top:0;background:var(--fundo);border-bottom:1px solid var(--linha);z-index:5}
nav div{max-width:1280px;margin:auto;padding:10px 24px;display:flex;gap:8px;overflow-x:auto}nav a{white-space:nowrap;padding:8px 14px;border:1px solid var(--linha);border-radius:999px;color:inherit;text-decoration:none;background:#fff}
section{max-width:1280px;margin:auto;padding:28px 24px}h2{font:400 40px/1 Anton,sans-serif;margin:24px 0 4px}h3{font-weight:600;font-size:14px;letter-spacing:1.5px;text-transform:uppercase;color:var(--suave);margin:28px 0 12px}
.marca-topo{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:center}.marca-topo img{width:100%;border-radius:10px}
.grade{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px}
.cartao{background:var(--cartao);border:1px solid var(--linha);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.fotos{display:grid;grid-template-columns:1fr 1fr;gap:2px;background:var(--linha)}.fotos img{width:100%;aspect-ratio:4/5;object-fit:cover;background:#eee;display:block}
.fotos .arte{object-fit:contain;background:#fafafa}.info{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}
.info b{font-size:16px}.info small{color:var(--suave)}.acoes{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:6px}
.acoes a{font-size:13px;padding:6px 10px;border-radius:8px;border:1px solid var(--tinta);color:var(--tinta);text-decoration:none}.acoes a.ar{background:var(--tinta);color:#fff}
.leg{font-size:11px;color:var(--suave);display:grid;grid-template-columns:1fr 1fr;padding:4px 14px 0}
footer{text-align:center;color:var(--suave);padding:40px 20px;font-size:13px}
@media(max-width:700px){.marca-topo{grid-template-columns:1fr}}
'''


def site():
    S = os.path.join(RAIZ, 'site'); os.makedirs(S, exist_ok=True)
    corpo = []
    for mid, m in CAT['marcas'].items():
        os.makedirs(os.path.join(S, mid), exist_ok=True)
        jpg(os.path.join(RAIZ, 'kv', f'{mid}.jpg'), os.path.join(S, mid, 'kv.jpg'), 1600)
        sec = [f'<section id="{mid}"><div class="marca-topo"><div><h2>{html.escape(m["nome"])}</h2><p class="sub">{html.escape(m["titulo"])} · {html.escape(m["subtitulo"])}</p>'
               f'<div class="acoes"><a class="ar" href="{URL_AR.format(mid)}">Todas as peças em AR</a><a href="revisao/{mid}.jpg">Folha de revisão ChatGPT x 3D</a></div></div>'
               f'<img src="site/{mid}/kv.jpg" alt="Key visual {html.escape(m["nome"])}" loading="lazy"></div>']
        for cat, rot in CAT['categorias'].items():
            sec.append(f'<h3>{rot}</h3><div class="grade">')
            for p in [q for q in m['pecas'] if q['categoria'] == cat]:
                pid = p['id']
                a = jpg(p['arteChatgpt'], os.path.join(S, mid, f'{pid}-arte.jpg'))
                hsrc = os.path.join(saida(mid, pid), 'hero.jpg')
                hh = jpg(hsrc, os.path.join(S, mid, f'{pid}-3d.jpg'))
                eng = f"engenharia/{mid}/{pid}/ARCOR-{mid.upper()}-{pid.upper()}-R00"
                tem_eng = os.path.exists(os.path.join(RAIZ, eng + '.pdf'))
                acoes = (f'<a class="ar" href="{URL_AR.format(mid)}?modelo={pid}">Ver em AR</a>' if pronto(mid, p) else '<small>AR em produção</small>')
                if tem_eng: acoes += f'<a href="{eng}.pdf">Executivo PDF</a><a href="{eng}.dxf">DXF</a>'
                sec.append(f'<article class="cartao"><div class="fotos">'
                           f'<img class="arte" src="site/{mid}/{pid}-arte.jpg?v={V}" alt="Arte ChatGPT" loading="lazy" {"" if a else "style=visibility:hidden"}>'
                           f'<img src="site/{mid}/{pid}-3d.jpg?v={V}" alt="3D no PDV" loading="lazy" {"" if hh else "style=visibility:hidden"}></div>'
                           f'<div class="leg"><span>Arte (ChatGPT)</span><span>3D no PDV</span></div>'
                           f'<div class="info"><b>{html.escape(curto(p, m))}</b><small>{p["larguraCm"]:g} x {p["alturaCm"]:g} x {p["profundidadeCm"]:g} cm · {html.escape(p["funcao"])}</small>'
                           f'<div class="acoes">{acoes}</div></div></article>')
            sec.append('</div>')
        sec.append('</section>')
        corpo.append(''.join(sec))
    nav = ''.join(f'<a href="#{mid}">{html.escape(m["nome"])}</a>' for mid, m in CAT['marcas'].items())
    pag = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>Arcor · Peças de PDV | 75 LAB</title><meta name="robots" content="noindex">'
           f'<link href="https://fonts.googleapis.com/css2?family=Anton&family=Lexend:wght@300;400;600&display=swap" rel="stylesheet"><style>{CSS}</style></head><body>'
           f'<header><h1>Arcor · Peças de PDV</h1><p class="sub">60 peças para 7Belo, Butter Toffees, Rocklets e Tortuguita, em três categorias: leves (régua, wobbler, stopper, testeira, clip strip, adesivo de chão), '
           f'médias (display de chão e de balcão, totem, ponta de gôndola, portal) e pesadas (ilha, store in store, degustação, fachada). Cada peça tem a arte criada no ChatGPT a partir do KV, o 3D, o AR em tamanho real e a engenharia (PDF executivo e DXF).</p></header>'
           f'<nav><div>{nav}</div></nav>{"".join(corpo)}<footer>Projeto 75 LAB para Arcor · medidas de referência · validar prova de corte e cor antes da produção</footer></body></html>')
    open(os.path.join(RAIZ, 'index.html'), 'w', encoding='utf-8').write(pag)
    sh('git', 'add', 'index.html', 'site', 'revisao', 'engenharia', 'ferramentas', 'catalogo.json', '.gitignore', cwd=RAIZ)
    print(sh('git', 'commit', '-qm', 'Catálogo Arcor PDV atualizado\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>', cwd=RAIZ)[1][-200:])
    print(sh('git', 'push', '-q', cwd=RAIZ)[1][-300:])


def drive():
    D = os.path.join(RAIZ, 'drive')
    shutil.rmtree(D, ignore_errors=True)
    for mid, m in CAT['marcas'].items():
        b = os.path.join(D, mid)
        for p in m['pecas']:
            n = f"{p['categoria'].upper()} - {curto(p, m)}"
            s = saida(mid, p['id'])
            alvo = {'01. ChatGPT (artes)': [(p['arteChatgpt'], f"{p['id']}-arte-chatgpt.png"), (p['arteFace'], f"{p['id']}-arte-face-{p['facePrincipal']}.png")],
                    f'02. 3D e renders/{n}': [(os.path.join(s, 'hero.jpg'), f"{p['id']}-render-pdv.jpg"), (os.path.join(s, 'poster.png'), f"{p['id']}-3d.png"), (os.path.join(s, 'modelo.glb'), f"{p['id']}.glb")],
                    f'03. AR/{n}': [(os.path.join(s, 'modelo.usdz'), f"{p['id']}.usdz")],
                    f'04. Engenharia/{n}': [(os.path.join(RAIZ, 'engenharia', mid, p['id'], f"ARCOR-{mid.upper()}-{p['id'].upper()}-R00{e}"), f"ARCOR-{mid.upper()}-{p['id'].upper()}-R00{e}") for e in ('.pdf', '.dxf')]}
            for pasta, arqs in alvo.items():
                for src, nome in arqs:
                    if os.path.exists(src):
                        os.makedirs(os.path.join(b, pasta), exist_ok=True); shutil.copy(src, os.path.join(b, pasta, nome))
        for x in ('packshot.png', 'logo.png'):
            src = os.path.join(RAIZ, 'chatgpt', mid, x)
            if os.path.exists(src): shutil.copy(src, os.path.join(b, '01. ChatGPT (artes)', x))
        if os.path.exists(os.path.join(RAIZ, 'revisao', f'{mid}.jpg')):
            shutil.copy(os.path.join(RAIZ, 'revisao', f'{mid}.jpg'), os.path.join(b, '00 - revisao ChatGPT x 3D.jpg'))
        open(os.path.join(b, '00 - LEIA-ME.txt'), 'w').write(
            f"Arcor · {m['nome']} · peças de PDV (75 LAB)\n\nCatálogo: {URL_SITE}#{mid}\nAR (todas as peças): {URL_AR.format(mid)}\n\n"
            "01 ChatGPT: arte criada no ChatGPT a partir do KV e a mesma arte na proporção exata da face da peça.\n"
            "02 3D: render no PDV (Blender Cycles com HDR de supermercado), vista do 3D e o modelo GLB.\n"
            "03 AR: USDZ (iPhone). O link do AR abre direto no celular em tamanho real.\n"
            "04 Engenharia: PDF executivo A3 (vistas cotadas, planificados, materiais, aproveitamento, montagem) e DXF 1:1 em mm.\n"
            "Medidas de referência: validar prova de corte e cor com a gráfica e aprovar com a marca antes de produzir.\n")
    sh('rsync', '-a', '--delete', '-e', ' '.join(SSH[:3]), D + '/', SSH[3] + ':tmp/arcor/drive/')
    r = subprocess.run(SSH + ['cd agencia/motor && npx tsx zz_arcor_drive.ts 2>&1 | grep -E "PASTA|rro" | tail -8'], capture_output=True, text=True, timeout=7200)
    print(r.stdout[-1500:], r.stderr[-500:])
    open(os.path.join(RAIZ, 'logs', 'drive.txt'), 'w').write(r.stdout)


if __name__ == '__main__':
    o = sys.argv[1:] or ['ar', 'site', 'drive']
    if 'ar' in o: ar()
    if 'site' in o: site()
    if 'drive' in o: drive()
