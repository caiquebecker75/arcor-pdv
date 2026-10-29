# Rodada 2: 3D por receita a partir do conceito aprovado (Blender da agência) e folha de/para conceito x 3D.
#   python3 tres_d2.py COD [COD ...] [--ar]     cena + poster + de/para; --ar também faz luz assada, GLB e USDZ
import json, os, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.expanduser('~/agencia-75lab/motor/ar-pdv')
BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
PY = os.path.expanduser('~/Library/Application Support/agencia-75lab/venv/bin/python')
SIGLA = {'7B': '7belo', 'BT': 'butter-toffees', 'RK': 'rocklets', 'TG': 'tortuguita'}
AR = '--ar' in sys.argv
F = ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc', 34, index=1)


def rodar(cmd, minutos):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=MOD, capture_output=True, text=True, timeout=minutos * 60)
        return r.returncode == 0, (r.stdout or '') + (r.stderr or ''), time.time() - t0
    except subprocess.TimeoutExpired:
        return False, 'timeout', time.time() - t0


def blender(lote, pid, etapa, minutos, rapido=False):
    fs = ['--factory-startup'] if etapa == 'cena' else []
    return rodar([BLENDER, '-b', *fs, '--python-exit-code', '1', '-P', os.path.join(MOD, 'blender', 'gerar.py'), '--',
                  '--lote', lote, '--peca', pid, '--etapa', etapa, *(['--rapido'] if rapido else [])], minutos)


def depara(cod, conceito, poster, destino):
    a = Image.open(conceito).convert('RGB'); a.thumbnail((1100, 1100))
    b = Image.new('RGB', (1100, 1100), (233, 233, 231))
    if os.path.exists(poster):
        b = Image.open(poster).convert('RGB'); b.thumbnail((1100, 1100))
    f = Image.new('RGB', (2240, 1180), 'white')
    f.paste(a, (10 + (1100 - a.width) // 2, 70 + (1100 - a.height) // 2)); f.paste(b, (1130, 70))
    d = ImageDraw.Draw(f)
    d.text((20, 14), f'{cod}  conceito aprovado (ChatGPT)', fill='black', font=F)
    d.text((1140, 14), '3D Blender', fill='black', font=F)
    f.save(destino, quality=85)


def um(cod):
    mid = SIGLA[cod[:2]]
    lote = os.path.join(RAIZ, 'lotes2', mid)
    ok, out, _ = rodar([PY, os.path.join(RAIZ, 'ferramentas', 'preparar3d.py'), cod], 10)
    if not ok:
        print(cod, 'preparo falhou', out[-600:]); return False
    mont = json.load(open(os.path.join(lote, 'montagem.json')))
    p = next(x for x in mont['pecas'] if x.get('cod') == cod)
    pid = p['id']
    s = os.path.join(lote, 'saida', pid)
    etapas = [('cena', 6, False)] + ([('poster', 15, True), ('ar', 45, False)] if AR else [])
    for etapa, mins, rap in etapas:
        ok, out, dt = blender(lote, pid, etapa, mins, rap)
        print(time.strftime('%H:%M:%S'), cod, etapa, 'ok' if ok else 'FALHOU', f'{dt:.0f}s', flush=True)
        if not ok:
            print('\n'.join(l for l in out.split('\n') if any(k in l for k in ('Error', 'Traceback', 'line ', 'erro')))[-1500:]); return False
    if AR:
        ok, out, dt = rodar([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '-P', os.path.join(MOD, 'blender', 'usdz.py'), '--',
                             '--glb', os.path.join(s, 'modelo.glb'), '--usdz', os.path.join(s, 'modelo.usdz')], 15)
        print(cod, 'usdz', 'ok' if ok else 'FALHOU')
    cam = p['receita'].get('camera', {})
    foto = os.path.join(s, 'depara.jpg')
    ok, out, dt = rodar([BLENDER, '-b', os.path.join(s, 'cena.blend'), '--python-exit-code', '1', '-P', os.path.join(MOD, 'blender', 'depara.py'), '--',
                         '--saida', foto, *sum([[f'--{k}', str(v)] for k, v in cam.items()], [])], 15)
    print(time.strftime('%H:%M:%S'), cod, 'foto de conferência', 'ok' if ok else 'FALHOU', f'{dt:.0f}s', flush=True)
    if not ok: print(out[-1200:])
    os.makedirs(os.path.join(RAIZ, 'depara'), exist_ok=True)
    depara(cod, p['conceito'], foto, os.path.join(RAIZ, 'depara', f'{cod}.jpg'))
    return True


if __name__ == '__main__':
    for c in [a for a in sys.argv[1:] if not a.startswith('--')]:
        um(c)
