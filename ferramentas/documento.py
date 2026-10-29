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


NOMECAT = {'leve': 'Peças leves', 'media': 'Peças médias', 'pesada': 'Peças pesadas'}


def web():
    """Apresentação: capa, abertura de cada marca e um conceito por tela (setas, toque ou clique para navegar)."""
    telas = ['<section class="t capa"><small>75 LAB para Arcor</small><h1>Conceitos de PDV</h1>'
             '<p>7Belo, Butter Toffees, Rocklets e Tortuguita. Peças leves, médias e pesadas criadas no ChatGPT a partir dos key visuals. '
             'Marque Aprovo ou Não aprovo em cada conceito; só o aprovado segue para 3D, AR e engenharia.</p><span class="dica">Use as setas ou toque nas laterais</span></section>']
    atual = None
    for mid, m, p, cod, arq in itens():
        im = Image.open(os.path.join(PASTA, arq + '.png')).convert('RGB'); im.thumbnail((1600, 1600))
        im.save(os.path.join(PASTA, arq + '.jpg'), quality=84)
        if mid != atual:
            atual = mid
            n = sum(1 for x in itens() if x[0] == mid)
            telas.append(f'<section class="t marca" style="--c:{m["cores"]["primaria"]}"><small>{n} conceitos</small><h1>{html.escape(m["nome"])}</h1></section>')
        telas.append(f'''<section class="t peca" data-cod="{cod}" style="--c:{m['cores']['primaria']}"><div class="foto"><img src="{arq}.jpg" alt="{html.escape(p['nome'])}"></div>
<aside><b>{cod}</b><h2>{html.escape(p['nome'].replace(' ' + m['nome'], ''))}</h2><p>{html.escape(m['nome'])} · {NOMECAT[p['categoria']]}<br>{p['larguraCm']:g} x {p['alturaCm']:g} x {p['profundidadeCm']:g} cm</p>
<div class="voto"><button data-v="sim">Aprovo</button><button data-v="nao">Não aprovo</button></div></aside></section>''')
    telas.append('<section class="t fim"><h1>Sua resposta</h1><pre id="resumo"></pre><button id="copiar">Copiar resposta</button></section>')
    open(os.path.join(PASTA, 'index.html'), 'w').write('''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Arcor PDV · Conceitos</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Lexend:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{--fundo:#f3f2ef;--tinta:#16161a;--suave:#6b6b73;--linha:#dcdad5}
*{box-sizing:border-box}html,body{margin:0;height:100%;overflow:hidden;background:var(--fundo);color:var(--tinta);font:16px/1.5 Lexend,system-ui,sans-serif}
.t{position:fixed;inset:0;display:none;padding:5vh 5vw 9vh}.t.on{display:flex}
.capa,.marca,.fim{flex-direction:column;justify-content:center}.capa h1,.marca h1,.fim h1{font:400 clamp(56px,11vw,160px)/.9 Anton,sans-serif;text-transform:uppercase;margin:8px 0 20px}
.capa small,.marca small{font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--suave)}.capa p{max-width:620px;color:var(--suave);font-size:18px}
.dica{margin-top:32px;color:var(--suave);font-size:14px}.marca{border-left:24px solid var(--c)}
.peca{gap:4vw;align-items:center}.foto{flex:1 1 auto;height:100%;display:flex;align-items:center;justify-content:center;min-width:0}
.foto img{max-width:100%;max-height:100%;border-radius:10px;box-shadow:0 20px 50px rgba(0,0,0,.12)}
aside{flex:0 0 300px;border-top:8px solid var(--c);padding-top:20px}aside b{font:400 64px/1 Anton,sans-serif}
aside h2{font-size:26px;line-height:1.2;margin:10px 0}aside p{color:var(--suave);margin:0 0 24px}
.voto{display:flex;flex-direction:column;gap:10px}.voto button,#copiar{font:600 16px Lexend;padding:14px;border-radius:12px;border:1px solid var(--linha);background:#fff;cursor:pointer}
.peca.sim [data-v=sim]{background:#1f9d55;color:#fff;border-color:#1f9d55}.peca.nao [data-v=nao]{background:#d64545;color:#fff;border-color:#d64545}
#resumo{font:18px/1.6 Lexend;white-space:pre-wrap;max-width:900px}#copiar{background:var(--tinta);color:#fff;align-self:flex-start;padding:14px 28px}
#barra{position:fixed;left:5vw;right:5vw;bottom:4vh;display:flex;align-items:center;gap:16px;color:var(--suave);font-size:14px;z-index:3}
#barra i{flex:1;height:3px;background:var(--linha);border-radius:3px;overflow:hidden}#barra i b{display:block;height:100%;background:var(--tinta);transition:width .2s}
#barra button{font:600 20px Lexend;width:44px;height:44px;border-radius:50%;border:1px solid var(--linha);background:#fff;cursor:pointer}
@media(max-width:800px){.peca{flex-direction:column;gap:16px;padding-bottom:12vh}.foto{height:auto;flex:1}aside{flex:none;width:100%;padding-top:12px}
aside b{font-size:36px}aside h2{font-size:20px;margin:4px 0}aside p{margin-bottom:12px}.voto{flex-direction:row}.voto button{flex:1;padding:10px}.marca{border-left-width:12px}}
</style></head><body>''' + '\n'.join(telas) + '''
<div id="barra"><button id="ant" aria-label="Anterior">‹</button><span id="num"></span><i><b></b></i><button id="prox" aria-label="Próxima">›</button></div>
<script>
const T=[...document.querySelectorAll('.t')],K='arcor-conceitos-votos';let i=0,v={};try{v=JSON.parse(localStorage.getItem(K))||{}}catch(e){}
try{i=Math.min(+(location.hash.slice(1))||0,T.length-1)}catch(e){}
const resumo=()=>{const s=Object.keys(v).filter(k=>v[k]==='sim').sort(),n=Object.keys(v).filter(k=>v[k]==='nao').sort();
 return 'Aprovados: '+(s.join(', ')||'nenhum')+'\\nNão aprovados: '+(n.join(', ')||'nenhum')};
const ver=()=>{T.forEach((t,k)=>{t.classList.toggle('on',k===i);if(t.dataset.cod){t.classList.remove('sim','nao');if(v[t.dataset.cod])t.classList.add(v[t.dataset.cod])}});
 document.getElementById('num').textContent=(i+1)+' / '+T.length;document.querySelector('#barra i b').style.width=(100*(i+1)/T.length)+'%';
 document.getElementById('resumo').textContent=resumo();history.replaceState(null,'','#'+i)};
const ir=d=>{i=Math.max(0,Math.min(T.length-1,i+d));ver()};ver();
document.getElementById('ant').onclick=()=>ir(-1);document.getElementById('prox').onclick=()=>ir(1);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();ir(1)}if(['ArrowLeft','PageUp'].includes(e.key))ir(-1)});
let x0=null;addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});addEventListener('touchend',e=>{if(x0===null)return;const d=e.changedTouches[0].clientX-x0;if(Math.abs(d)>50)ir(d<0?1:-1);x0=null});
document.addEventListener('click',e=>{const b=e.target.closest('.voto button');if(!b)return;const c=b.closest('.peca').dataset.cod;
 if(v[c]===b.dataset.v)delete v[c];else v[c]=b.dataset.v;try{localStorage.setItem(K,JSON.stringify(v))}catch(e){}ver()});
document.getElementById('copiar').onclick=()=>navigator.clipboard.writeText(resumo()).then(()=>{document.getElementById('copiar').textContent='Copiado'});
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
