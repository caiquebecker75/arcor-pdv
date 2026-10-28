# Noite Arcor: espera o ChatGPT de cada marca, roda 3D/AR, engenharia e revisão, publica AR + catálogo; no fim, nova
# tentativa das artes que faltaram e Drive.   nohup python3 orquestra.py > ../logs/orquestra.log &
import os, subprocess, sys, time, json
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(RAIZ, 'ferramentas')
PY = os.path.expanduser('~/Library/Application Support/agencia-75lab/venv/bin/python')
LOG = os.path.join(RAIZ, 'logs', 'chatgpt.log')
MARCAS = ['7belo', 'butter-toffees', 'rocklets', 'tortuguita']


def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)


def run(*c):
    t = time.time(); r = subprocess.run(c, cwd=F, capture_output=True, text=True)
    log(' '.join(os.path.basename(x) for x in c[:3]), 'rc', r.returncode, f'{time.time() - t:.0f}s', (r.stdout + r.stderr).strip().split('\n')[-1][:200])
    return r.returncode


def gpt_vivo(): return subprocess.run(['pgrep', '-f', 'chatgpt.py'], capture_output=True).returncode == 0


def marca_pronta(m):
    t = open(LOG).read() if os.path.exists(LOG) else ''
    return f' {m} pronta' in t or f' {m} faltam' in t or not gpt_vivo()


def ciclo(m):
    run('python3', 'tres_d.py', m)
    run(PY, 'engenharia.py', m)
    run('python3', 'revisao.py', m)
    run('python3', 'publicar.py', 'ar', 'site')


subprocess.Popen(['caffeinate', '-dims', '-w', str(os.getpid())])
for m in MARCAS:
    while not marca_pronta(m): time.sleep(30)
    log('marca', m); ciclo(m)
while gpt_vivo(): time.sleep(30)
# segunda chance para as artes que falharam (o chatgpt.py pula o que já existe)
run('python3', 'chatgpt.py', *MARCAS)
for m in MARCAS: ciclo(m)
run('python3', 'publicar.py', 'drive')
log('FIM')
