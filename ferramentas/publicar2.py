# Rodada 2: publica um lote de 3D. AR (projetos.75lab.com.br/ar/arcor-3d/, todas as peças prontas numa página),
# de/para no GitHub (arcor-pdv) e pasta do lote no Drive ("PDV ARCOR · 3D RODADA 2" dentro de 01. CRIAÇÃO).
#   python3 publicar2.py "Lote 01 · Réguas de gôndola" 7B-01 BT-01 RK-01 TG-01
import json, os, re, shutil, subprocess, sys, time
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AR = os.path.expanduser('~/ar-75lab')
SIGLA = {'7B': '7belo', 'BT': 'butter-toffees', 'RK': 'rocklets', 'TG': 'tortuguita'}
URL = 'https://projetos.75lab.com.br/ar/arcor-3d/'
SSH = ['ssh', '-i', os.path.expanduser('~/.ssh/agencia_motor'), 'motor@187.77.253.75']
CRIACAO = '1nvMxUKIle_Gs0SyI66YJFMPrIc_keMqC'
V = time.strftime('%Y%m%d%H%M')


def sh(*c, cwd=None):
    r = subprocess.run(c, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def pecas():
    """Todas as peças da rodada 2 com GLB e USDZ prontos, na ordem dos códigos."""
    out = []
    for mid in SIGLA.values():
        arq = os.path.join(RAIZ, 'lotes2', mid, 'montagem.json')
        if not os.path.exists(arq): continue
        for p in json.load(open(arq))['pecas']:
            s = os.path.join(RAIZ, 'lotes2', mid, 'saida', p['id'])
            if all(os.path.exists(os.path.join(s, f)) for f in ('modelo.glb', 'modelo.usdz', 'poster.png')):
                out.append((p['cod'], mid, p, s))
    return sorted(out)


def ar():
    d = os.path.join(AR, 'arcor-3d'); os.makedirs(d, exist_ok=True)
    itens = []
    for cod, mid, p, s in pecas():
        shutil.copy(os.path.join(s, 'modelo.glb'), os.path.join(d, f'{cod}.glb'))
        shutil.copy(os.path.join(s, 'modelo.usdz'), os.path.join(d, f'{cod}.usdz'))
        im = Image.open(os.path.join(s, 'poster.png')); im.thumbnail((1200, 1200)); im.save(os.path.join(d, f'{cod}-poster.webp'), quality=82)
        itens.append({'id': cod, 'nome': f"{cod} · {p['nome']}", 'alt': f"{p['nome']} em 3D", 'src': f'{cod}.glb?v={V}', 'ios': f'{cod}.usdz?v={V}', 'poster': f'{cod}-poster.webp?v={V}'})
    h = open(os.path.join(AR, 'semp-split-hw', 'index.html'), encoding='utf-8').read()
    h = re.sub(r'(<script type="application/json" id="modelos">)(.*?)(</script>)', lambda x: x.group(1) + '\n' + json.dumps(itens, ensure_ascii=False, indent=1) + '\n' + x.group(3), h, flags=re.S)
    for a, b in (('semp-split-hw', 'arcor-3d'), ('SEMP · Lançamento Split HW', 'Arcor · Peças de PDV em AR'), ('Projeto 75 LAB para SEMP', 'Projeto 75 LAB para Arcor'),
                 ('do lançamento SEMP Split HW', 'de 7Belo, Butter Toffees, Rocklets e Tortuguita'), ('SEMP Split HW', 'Arcor PDV'), ('quinze peças', f'{len(itens)} peças')):
        h = h.replace(a, b)
    h = re.sub(r'og\.jpg\?v=\d+', f'og.jpg?v={V}', h)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(h)
    if itens:
        foto = os.path.join(pecas()[0][3], 'depara.jpg')
        im = Image.open(foto).convert('RGB'); w, hh = im.size; ch = w * 630 // 1200
        im.crop((0, (hh - ch) // 2, w, (hh - ch) // 2 + ch)).resize((1200, 630)).save(os.path.join(d, 'og.jpg'), quality=85)
    if not os.path.exists(os.path.join(d, 'qr.png')):
        sh('node', os.path.join(AR, 'tools', 'qr-png.mjs'), URL, os.path.join(d, 'qr.png'), cwd=os.path.join(AR, 'tools'))
    sh('git', 'add', 'arcor-3d', cwd=AR)
    sh('git', 'commit', '-m', f'Arcor: AR da rodada 2 ({len(itens)} peças)\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>', cwd=AR)
    print('ar', sh('git', 'push', '-q', cwd=AR)[0], len(itens), 'peças')


def github(lote):
    sh('git', 'add', 'depara', 'ferramentas', cwd=RAIZ)
    sh('git', 'commit', '-m', f'Arcor PDV 3D: {lote}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>', cwd=RAIZ)
    print('github', sh('git', 'push', '-q', cwd=RAIZ)[0])


def drive(lote, cods):
    st = os.path.join(RAIZ, 'drive2', lote); shutil.rmtree(st, ignore_errors=True); os.makedirs(st)
    todas = {c: (mid, p, s) for c, mid, p, s in pecas()}
    for cod in cods:
        mid = SIGLA[cod[:2]]
        if cod not in todas: continue
        _, p, s = todas[cod]
        pasta = os.path.join(st, f"{cod} · {p['nome']}"); os.makedirs(pasta)
        shutil.copy(os.path.join(RAIZ, 'depara', f'{cod}.jpg'), os.path.join(pasta, f'{cod} · de-para conceito x 3D.jpg'))
        shutil.copy(os.path.join(s, 'depara.jpg'), os.path.join(pasta, f'{cod} · 3D.jpg'))
        shutil.copy(os.path.join(s, 'modelo.glb'), os.path.join(pasta, f'{cod}.glb'))
        shutil.copy(os.path.join(s, 'modelo.usdz'), os.path.join(pasta, f'{cod}.usdz'))
        shutil.copy(os.path.join(s, 'cena.blend'), os.path.join(pasta, f'{cod}.blend'))
    open(os.path.join(st, '00 - LEIA-ME.txt'), 'w').write(
        f'{lote}\nArcor PDV, rodada 2: 3D feito no Blender a partir dos conceitos aprovados (sem imagem nova).\n'
        f'Cada pasta tem o de/para (conceito x 3D), a foto do 3D, o modelo GLB, o USDZ (iPhone) e o arquivo Blender.\n'
        f'AR de todas as peças prontas: {URL}\n75 LAB\n')
    sh(*SSH, 'mkdir -p tmp/arcor/drive2 && rm -rf "tmp/arcor/drive2/lote"')
    print('rsync', sh('rsync', '-a', '-e', f"ssh -i {os.path.expanduser('~/.ssh/agencia_motor')}", st + '/', 'motor@187.77.253.75:tmp/arcor/drive2/lote/')[0])
    rc, out = sh(*SSH, f'cd agencia/motor && npx tsx zz_arcor_drive2.ts ~/tmp/arcor/drive2/lote {CRIACAO} "PDV ARCOR · 3D RODADA 2" "{lote}" 2>&1 | tail -3')
    print(out.strip())
    with open(os.path.join(RAIZ, 'logs', 'drive2.txt'), 'a') as f:
        f.write(out)


if __name__ == '__main__':
    lote, cods = sys.argv[1], sys.argv[2:]
    ar(); github(lote); drive(lote, cods)
