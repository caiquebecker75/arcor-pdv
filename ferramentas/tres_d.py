# 3D + AR das peças de uma marca com o gerador de PDV da agência (Blender): cena, foto na loja (hero), poster, luz assada,
# GLB e USDZ. A arte da face principal é a do ChatGPT (lotes/<marca>/entrada/<id>-<face>.png); o resto vem do KV.
#   python3 tres_d.py <marca> [peça ...] [--final]     (--final = hero em 2400x3000; sem ele, hero rápido 1200x1500)
import json, os, subprocess, sys, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.expanduser('~/agencia-75lab/motor/ar-pdv')
BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
PY = os.path.expanduser('~/Library/Application Support/agencia-75lab/venv/bin/python')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
FINAL = '--final' in sys.argv
RAPIDO = '--rapido' in sys.argv
MARCA, SO = args[0], set(args[1:])
LOTE = os.path.join(RAIZ, 'lotes', MARCA)
EST = os.path.join(LOTE, 'estado.json')


def log(*a):
    print(time.strftime('%H:%M:%S'), MARCA, *a, flush=True)


def rodar(cmd, minutos, cwd=MOD):
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=minutos * 60)
        ok, out = r.returncode == 0, (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        ok, out = False, 'timeout'
    return ok, out, time.time() - t0


def blender(peca, etapa, minutos, extra=()):
    fs = ['--factory-startup'] if etapa == 'cena' else []
    return rodar([BLENDER, '-b', *fs, '--python-exit-code', '1', '-P', os.path.join(MOD, 'blender', 'gerar.py'), '--',
                  '--lote', LOTE, '--peca', peca, '--etapa', etapa, *(['--rapido'] if RAPIDO else []), *extra], minutos)


def main():
    subprocess.run(['python3', os.path.join(RAIZ, 'ferramentas', 'catalogo.py')], check=True)
    ok, out, _ = rodar([PY, os.path.join(MOD, 'artes.py'), LOTE], 15)
    if not ok:
        log('artes.py falhou', out[-800:]); sys.exit(2)
    estado = json.load(open(EST)) if os.path.exists(EST) else {}
    ped = json.load(open(os.path.join(LOTE, 'pedido.json')))
    for p in ped['pecas']:
        pid = p['id']
        if SO and pid not in SO: continue
        s = os.path.join(LOTE, 'saida', pid)
        etapas = [('cena', lambda: blender(pid, 'cena', 6), 'cena.blend'),
                  ('hero', lambda: blender(pid, 'hero', 40), 'hero.jpg'),
                  ('poster', lambda: blender(pid, 'poster', 15), 'poster.png'),
                  ('ar', lambda: blender(pid, 'ar', 45), 'modelo.glb'),
                  ('usdz', lambda: rodar([BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '-P', os.path.join(MOD, 'blender', 'usdz.py'), '--',
                                          '--glb', os.path.join(s, 'modelo.glb'), '--usdz', os.path.join(s, 'modelo.usdz')], 15), 'modelo.usdz')]
        e = estado.setdefault(pid, {'tempos': {}})
        e.pop('falha', None)
        com_arte = os.path.exists(p.get('arteFace', ''))
        if e.get('comArte') != com_arte: e['feito'] = {}      # a arte do ChatGPT chegou depois: refaz a peça
        e['comArte'] = com_arte
        for nome, f, arq in etapas:
            if FINAL and nome != 'hero': continue
            if not FINAL and e.get('feito', {}).get(nome) and os.path.exists(os.path.join(s, arq)): continue
            ok, out, dt = f()
            e['tempos'][nome] = round(dt)
            if not ok or not os.path.exists(os.path.join(s, arq)):
                linhas = [l for l in out.split('\n') if any(k in l for k in ('Error', 'Traceback', 'line ', 'erro', 'timeout'))]
                e['falha'] = f"{nome}: {' | '.join(linhas[-5:]) or out[-400:]}"
                log(pid, 'FALHOU', e['falha'][:300]); break
            e.setdefault('feito', {})[nome] = True
            log(pid, nome, f'{dt:.0f}s')
        if not e.get('falha') and not FINAL:
            ok, out, _ = rodar(['/usr/bin/usdchecker', '--arkit', os.path.join(s, 'modelo.usdz')], 3)
            e['usdchecker'] = 'passou' if 'Success' in out else out.strip()[-300:]
        if FINAL and not e.get('falha'): e['heroFinal'] = True
        json.dump(estado, open(EST, 'w'), ensure_ascii=False, indent=1)
    log('fim', sum(1 for v in estado.values() if not v.get('falha')), 'ok de', len(estado))


if __name__ == '__main__':
    main()
