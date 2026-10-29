# Documento de aprovação dos conceitos do ChatGPT (rodada 2): página web (conceitos/index.html) e PDF (conceitos/Arcor-PDV-conceitos.pdf).
# Cada conceito tem um código (7B-01, BT-01, RK-01, TG-01) e botões Aprovo / Não aprovo; "Copiar resposta" monta o texto para mandar de volta.
#   python3 documento.py
import json, os, html
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RAIZ, 'catalogo.json')))
PASTA = os.path.join(RAIZ, 'conceitos')
SIGLA = {'7belo': '7B', 'butter-toffees': 'BT', 'rocklets': 'RK', 'tortuguita': 'TG'}
CATS = ['Leve', 'Média', 'Pesada']


def itens():
    for mid, m in CAT['marcas'].items():
        for i, p in enumerate(m['pecas'], 1):
            arq = f"{mid}/{i:02d}-{p['id']}"
            if os.path.exists(os.path.join(PASTA, arq + '.png')):
                yield mid, m, p, f'{SIGLA[mid]}-{i:02d}', arq


def web():
    secoes = {}
    for mid, m, p, cod, arq in itens():
        im = Image.open(os.path.join(PASTA, arq + '.png')).convert('RGB'); im.thumbnail((1400, 1400))
        im.save(os.path.join(PASTA, arq + '.jpg'), quality=84)
        secoes.setdefault(mid, {}).setdefault(p['categoria'], []).append(
            f'''<figure class="card" data-cod="{cod}"><img src="{arq}.jpg" loading="lazy" alt="{html.escape(p['nome'])}">
<figcaption><b>{cod}</b><span>{html.escape(p['nome'].replace(' ' + m['nome'], ''))}</span><small>{p['larguraCm']:g} x {p['alturaCm']:g} cm</small>
<div class="voto"><button data-v="sim">Aprovo</button><button data-v="nao">Não aprovo</button></div></figcaption></figure>''')
    corpo = ''
    for mid, cats in secoes.items():
        m = CAT['marcas'][mid]
        corpo += f'<section id="{mid}"><h2 style="--c:{m["cores"]["primaria"]}">{html.escape(m["nome"])}</h2>'
        for c in CATS:
            if c in cats: corpo += f'<h3>Peças {c.lower()}s</h3><div class="grade">{"".join(cats[c])}</div>'
        corpo += '</section>'
    nav = ''.join(f'<a href="#{mid}">{html.escape(CAT["marcas"][mid]["nome"])}</a>' for mid in secoes)
    open(os.path.join(PASTA, 'index.html'), 'w').write(f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Arcor PDV · Conceitos</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Lexend:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--fundo:#f6f5f2;--tinta:#16161a;--suave:#6b6b73;--linha:#e2e0db}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--fundo);color:var(--tinta);font:16px/1.5 Lexend,system-ui,sans-serif}}
header{{padding:56px 24px 24px;max-width:1280px;margin:auto}}h1{{font:400 clamp(40px,7vw,88px)/.95 Anton,sans-serif;margin:0 0 12px;text-transform:uppercase}}
header p{{color:var(--suave);max-width:640px;margin:0}}nav{{position:sticky;top:0;z-index:2;background:var(--fundo);border-bottom:1px solid var(--linha);
display:flex;gap:8px;padding:12px 24px;overflow-x:auto}}nav a{{color:var(--tinta);text-decoration:none;font-weight:600;padding:6px 14px;border:1px solid var(--linha);border-radius:99px;white-space:nowrap}}
nav button{{margin-left:auto;font:600 14px Lexend;background:var(--tinta);color:#fff;border:0;border-radius:99px;padding:8px 16px;cursor:pointer;white-space:nowrap}}
section{{max-width:1280px;margin:auto;padding:24px}}h2{{font:400 56px/1 Anton,sans-serif;text-transform:uppercase;border-left:10px solid var(--c);padding-left:16px;margin:40px 0 8px}}
h3{{font-size:14px;letter-spacing:.12em;text-transform:uppercase;color:var(--suave);margin:32px 0 12px}}
.grade{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}}
.card{{margin:0;background:#fff;border:1px solid var(--linha);border-radius:14px;overflow:hidden;transition:outline .15s}}
.card img{{width:100%;aspect-ratio:1;object-fit:cover;display:block;cursor:zoom-in;background:#ddd}}
figcaption{{padding:14px 16px;display:grid;grid-template-columns:auto 1fr;gap:2px 10px;align-items:baseline}}
figcaption b{{font:400 22px Anton,sans-serif}}figcaption small{{grid-column:2;color:var(--suave)}}
.voto{{grid-column:1/-1;display:flex;gap:8px;margin-top:10px}}.voto button{{flex:1;font:600 14px Lexend;padding:9px;border-radius:10px;border:1px solid var(--linha);background:#fff;cursor:pointer}}
.card.sim{{outline:3px solid #1f9d55}}.card.sim [data-v=sim]{{background:#1f9d55;color:#fff;border-color:#1f9d55}}
.card.nao{{outline:3px solid #d64545}}.card.nao [data-v=nao]{{background:#d64545;color:#fff;border-color:#d64545}}
#zoom{{position:fixed;inset:0;background:rgba(10,10,12,.92);display:none;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}}
#zoom img{{max-width:96vw;max-height:94vh}}#zoom.on{{display:flex}}
#aviso{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--tinta);color:#fff;padding:10px 18px;border-radius:99px;opacity:0;transition:.2s}}
@media(max-width:600px){{header,section{{padding-left:16px;padding-right:16px}}h2{{font-size:40px}}.grade{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>Arcor · conceitos de PDV</h1><p>60 conceitos criados no ChatGPT a partir dos key visuals de 7Belo, Butter Toffees, Rocklets e Tortuguita,
em peças leves, médias e pesadas. Marque Aprovo ou Não aprovo em cada um e toque em Copiar resposta. Só o que for aprovado segue para 3D, AR e engenharia.</p></header>
<nav>{nav}<button id="copiar">Copiar resposta</button></nav>{corpo}
<div id="zoom"><img alt=""></div><div id="aviso">Resposta copiada</div>
<script>
const K='arcor-conceitos-votos';let v={{}};try{{v=JSON.parse(localStorage.getItem(K))||{{}}}}catch(e){{}}
const pinta=()=>document.querySelectorAll('.card').forEach(c=>{{c.classList.remove('sim','nao');if(v[c.dataset.cod])c.classList.add(v[c.dataset.cod])}});pinta();
document.addEventListener('click',e=>{{const b=e.target.closest('.voto button');if(b){{const c=b.closest('.card').dataset.cod;v[c]=v[c]===b.dataset.v?undefined:b.dataset.v;
try{{localStorage.setItem(K,JSON.stringify(v))}}catch(e){{}}pinta();return}}
const i=e.target.closest('.card img');const z=document.getElementById('zoom');if(i){{z.querySelector('img').src=i.src;z.classList.add('on')}}else if(e.target.closest('#zoom'))z.classList.remove('on')}});
document.getElementById('copiar').onclick=()=>{{const s=Object.keys(v).filter(k=>v[k]==='sim'),n=Object.keys(v).filter(k=>v[k]==='nao');
const t='Aprovados: '+(s.join(', ')||'nenhum')+'\\nNão aprovados: '+(n.join(', ')||'nenhum');navigator.clipboard.writeText(t).then(()=>{{const a=document.getElementById('aviso');a.style.opacity=1;setTimeout(()=>a.style.opacity=0,1600)}})}};
</script></body></html>''')


def pdf():
    F = lambda s, i=0: ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc', s, index=i)
    paginas = []
    for mid, m, p, cod, arq in itens():
        pg = Image.new('RGB', (2480, 1754), (246, 245, 242)); d = ImageDraw.Draw(pg)
        im = Image.open(os.path.join(PASTA, arq + '.png')).convert('RGB'); im.thumbnail((1600, 1600))
        pg.paste(im, (100, (1754 - im.height) // 2))
        x = 1800
        d.rectangle((x, 140, x + 14, 330), fill=m['cores']['primaria'])
        d.text((x + 40, 130), cod, font=F(110, 1), fill=(22, 22, 26))
        d.text((x + 40, 270), m['nome'], font=F(48), fill=(22, 22, 26))
        d.text((x, 420), p['nome'].replace(' ' + m['nome'], ''), font=F(44, 1), fill=(22, 22, 26))
        d.text((x, 490), f"Peça {p['categoria'].lower()}", font=F(36), fill=(107, 107, 115))
        d.text((x, 545), f"{p['larguraCm']:g} x {p['alturaCm']:g} cm", font=F(36), fill=(107, 107, 115))
        d.text((x, 1500), '[  ] Aprovo     [  ] Não aprovo', font=F(36), fill=(22, 22, 26))
        d.text((x, 1600), '75 LAB · conceito ChatGPT', font=F(28), fill=(150, 150, 155))
        paginas.append(pg)
    if paginas:
        paginas[0].save(os.path.join(PASTA, 'Arcor-PDV-conceitos.pdf'), save_all=True, append_images=paginas[1:], resolution=200, quality=80)


if __name__ == '__main__':
    web(); pdf()
    print(sum(1 for _ in itens()), 'conceitos no documento')
