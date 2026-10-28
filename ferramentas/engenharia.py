# Engenharia de cada peça: DXF R2018 (planificados e facas 1:1 em mm, camadas CORTE/VINCO/FURO/COTA/TEXTO) e PDF A3
# executivo (vistas cotadas, render, arte aplicada, lista de materiais, plano de corte por chapa, montagem e notas).
# Medidas saem do catalogo.json (mesma fonte do 3D e do AR). Montagem por encaixe sempre que possível, sem fita nem cola.
#   python3 engenharia.py [marca ...]
import json, os, sys, math, datetime, textwrap
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(RAIZ, 'catalogo.json')))
LOGO = os.path.expanduser('~/materiais-75lab/marca/75lab-logo-preto-1600.png')
HOJE = datetime.date.today().strftime('%d/%m/%Y')

MAT = {  # código: (descrição, espessura mm, chapa comercial mm)
    'pvc3': ('PVC expandido 3 mm, impressão UV direta', 3, (2000, 1000)),
    'pvc05': ('PVC rígido 0,5 mm, impressão UV + verniz', 0.5, (1000, 700)),
    'pet08': ('PET cristal 0,8 mm', 0.8, (1000, 700)),
    'ps2': ('PS branco 2 mm, impressão UV', 2, (2000, 1000)),
    'vinil': ('Vinil adesivo de piso + laminação antiderrapante R10', 0.2, (1370, 50000)),
    'bc': ('Papelão ondulado BC 7 mm, capa branca, impressão digital/offset + verniz', 7, (2400, 1600)),
    'e': ('Microondulado E 1,5 mm, capa branca, impressão offset + verniz', 1.5, (1000, 700)),
    'mdf15': ('MDF 15 mm, revestido com adesivo impresso + laminação fosca', 15, (2750, 1850)),
    'mdf18': ('MDF 18 mm, pintura PU / adesivo impresso laminado', 18, (2750, 1850)),
    'acm3': ('ACM 3 mm (alumínio composto), adesivo impresso laminado', 3, (5000, 1500)),
    'acril3': ('Acrílico leitoso 3 mm (face luminosa), adesivo translúcido', 3, (2000, 1000)),
    'metalon': ('Tubo metalon 30 x 30 x 1,2 mm, pintura eletrostática preta', 30, (6000, 30)),
    'lona': ('Lona front-light 440 g, impressão solvente, ilhoses a cada 300 mm', 0.5, (3200, 50000)),
}


def P(nome, w, h, mat, qtd=1, vincos=(), furos=(), rasgos=(), contorno=None, obs=''):
    return dict(nome=nome, w=round(w), h=round(h), mat=mat, qtd=qtd, vincos=list(vincos), furos=list(furos), rasgos=list(rasgos), contorno=contorno, obs=obs)


def projeto(p):
    """Painéis (mm), montagem e notas por tipo de peça."""
    L, H, D = p['larguraCm'] * 10, p['alturaCm'] * 10, p['profundidadeCm'] * 10
    t = p['tipo']
    if t == 'faixa_gondola':
        aba = 18
        return [P('Régua com aba de encaixe no trilho porta-preço', L, H + aba, 'pvc3', vincos=[(0, aba, L, aba)], obs='vinco a 90° na aba; a aba entra no trilho da prateleira')], \
            ['Dobrar a aba superior a 90° no vinco.', 'Encaixar a aba no trilho porta-preço da prateleira, sem cobrir a etiqueta de preço.', 'Centralizar no bloco da marca.']
    if t == 'wobbler':
        r = L / 2
        return [P('Disco do wobbler', L, L, 'pvc05', contorno='circulo', furos=[(L / 2, 12, 2.5)]),
                P('Haste flexível PET', 20, 160, 'pet08', furos=[(10, 150, 2.5), (10, 10, 2.5)], obs='a ponta inferior encaixa no trilho; rebite plástico Ø5 une disco e haste')], \
            ['Unir o disco à haste com rebite plástico Ø5 pelos furos.', 'Encaixar a ponta inferior da haste no trilho porta-preço (sem adesivo).', 'Conferir que o disco balança livre na frente do produto.']
    if t == 'stopper':
        aba = 60
        return [P('Stopper com aba de fixação', L, H + aba, 'pvc3', vincos=[(0, aba, L, aba)], rasgos=[(L / 2 - 20, aba / 2 - 2, 40, 4)],
                  obs='rasgo 40 x 4 para a presilha de trilho')], \
            ['Dobrar a aba a 90° no vinco.', 'Passar a presilha de trilho pelo rasgo e prender no trilho da prateleira.', 'O stopper fica perpendicular à gôndola, na altura dos olhos.']
    if t == 'testeira':
        aba = 40
        return [P('Testeira com abas de gancho', L, H + aba, 'pvc3', vincos=[(0, aba, L, aba)], rasgos=[(80, 10, 60, 5), (L - 140, 10, 60, 5)]),
                P('Gancho de testeira (par)', 60, 90, 'ps2', qtd=2, obs='encaixa nos rasgos da aba e no topo do montante da gôndola')], \
            ['Dobrar a aba superior a 90°.', 'Encaixar os 2 ganchos de PS nos rasgos da aba.', 'Apoiar os ganchos no topo da gôndola; a testeira fica faceando a prateleira de cima.']
    if t == 'clip_strip':
        n = int((H - 80) // 90)
        return [P('Fita clip strip', 60, H, 'pet08', furos=[(30, 40 + i * 90, 4) for i in range(n)] + [(30, H - 20, 5)], obs=f'{n} posições de gancho, passo 90 mm'),
                P('Topo com rasgo para a fita', L, min(H * 0.3, 180), 'ps2', rasgos=[(L / 2 - 31, 15, 62, 1.5)]),
                P('Gancho S de aço galvanizado', 0, 0, 'metalon', qtd=n, obs='componente comprado, fio 2 mm')], \
            ['Passar a fita pelo rasgo do topo e travar dobrando 15 mm.', 'Pendurar no gancho S pelo furo superior, na gondola de cross merchandising.', f'Pendurar as embalagens nos {n} ganchos.']
    if t == 'adesivo_chao':
        return [P('Adesivo de chão', L, L, 'vinil', contorno='raio20', obs='cantos raio 20 mm; laminação antiderrapante R10 obrigatória')], \
            ['Limpar e secar o piso.', 'Retirar o liner por partes e aplicar com espátula do centro para fora.', 'Não aplicar sobre rejunte aberto ou piso molhado.']
    if t == 'display_chao':
        hh = min(max(H * 0.2, 220), 400)
        hc = H - hh
        corpo_w = 2 * L + 2 * D + 30
        prat = [P(f'Bandeja {i + 1}', L - 14 + 2 * 50, D - 10 + 60 + 50, 'bc', vincos=[(50, 0, 50, D + 100), (L + 36, 0, L + 36, D + 100), (0, 60, L + 86, 60)],
                  obs='abas laterais de 50 mm travam por espiga nas fendas da lateral; lábio frontal 60 mm') for i in range(4)]
        return [P('Corpo (frente baixa, laterais, costas)', corpo_w, hc, 'bc', vincos=[(30, 0, 30, hc), (30 + D, 0, 30 + D, hc), (30 + D + L, 0, 30 + D + L, hc), (30 + 2 * D + L, 0, 30 + 2 * D + L, hc)],
                  rasgos=[(30 + D + 40, hc - 30, 60, 8), (30 + D + L - 100, hc - 30, 60, 8)], obs='aba de 30 mm fecha por espiga e fenda, sem cola'),
                P('Header com 2 espigas', L, hh + 40, 'bc', rasgos=[], vincos=[], obs='espigas 60 x 40 encaixam nas fendas do topo das costas'),
                P('Base / rodapé com fundo duplo', L + 2 * D + 2 * 120, D + 2 * 120, 'bc', vincos=[(120, 120, 120 + L + 2 * D, 120)]), *prat], \
            ['Armar a base (fundo duplo) dobrando as abas e travando pelas espigas.', 'Dobrar o corpo nos 4 vincos e fechar a aba de 30 mm pela espiga.', 'Encaixar o corpo na base.', 'Montar as 4 bandejas e encaixar de baixo para cima nas fendas das laterais.', 'Encaixar o header pelas 2 espigas no topo das costas.', 'Abastecer de baixo para cima.']
    if t == 'display_balcao':
        hh = H * 0.42
        return [P('Corpo (base, costas, laterais, frente baixa)', L + 2 * D, D + H + 60, 'e', vincos=[(D, 0, D, D + H), (D + L, 0, D + L, D + H), (0, D, L + 2 * D, D)], obs='laterais travam por linguetas nas costas'),
                P('Header', L, hh + 30, 'e', obs='lingueta de 30 mm entra na fenda das costas'),
                P('Divisórias de canal', D - 10, 60, 'e', qtd=2, obs='encaixe meia-altura no fundo')], \
            ['Dobrar a base e levantar costas e laterais.', 'Travar as laterais pelas linguetas.', 'Encaixar as 2 divisórias.', 'Encaixar o header na fenda das costas.', 'Abastecer com 3 colunas de embalagens.']
    if t == 'totem':
        return [P('Painel do totem', L, H, 'mdf15', rasgos=[(L / 2 - 8, 0, 16, 150)], obs='rasgo 16 x 150 mm na base para o pé em cruz'),
                P('Pé em cruz (meia-madeira)', 400, 300, 'mdf15', qtd=2, rasgos=[(192, 150, 16, 150)], obs='duas peças iguais, encaixe a meia altura'),
                P('Sapatas de feltro', 0, 0, 'mdf15', qtd=4, obs='componente comprado')], \
            ['Cruzar as duas peças do pé pelo encaixe meia-madeira.', 'Descer o painel pelo rasgo da base até apoiar no pé.', 'Colar as 4 sapatas de feltro.']
    if t == 'ponta_gondola':
        hh = min(500, H * 0.26)
        return [P('Header da ponta', L, hh, 'mdf15', furos=[(60, hh / 2, 4), (L - 60, hh / 2, 4)]),
                P('Painel lateral (par)', D, H * 0.82, 'ps2', qtd=2, obs='encaixe por presilhas no montante da gôndola'),
                P('Faixa de base / rodapé', L, 300 if H > 1200 else H * 0.15, 'ps2'),
                P('Stopper de ponta', 120, 300, 'pvc3', qtd=2),
                P('Suporte de header em aço', 40, hh + 300, 'metalon', qtd=2, obs='encaixa no furo do montante da gôndola')], \
            ['Encaixar os 2 suportes nos furos do montante da gôndola.', 'Fixar o header nos suportes (2 parafusos por lado).', 'Encaixar os painéis laterais pelas presilhas.', 'Encaixar a faixa de base no rodapé da gôndola.', 'Colocar os stoppers nas prateleiras de ponta.']
    if t == 'portal_corredor':
        return [P('Coluna em metalon (quadro)', 450, H - 500, 'metalon', qtd=2, obs='quadro 450 x (H-500) com travessas a cada 600 mm; base com chapa 400 x 400 x 6 mm'),
                P('Viga em metalon (quadro)', L, 500, 'metalon', obs='encaixe macho/fêmea nas colunas com pino trava'),
                P('Lona da coluna (frente e verso)', 450 + 60, H - 500 + 60, 'lona', qtd=4, obs='bainha de 30 mm com elástico tensionado'),
                P('Lona da viga (frente e verso)', L + 60, 500 + 60, 'lona', qtd=2),
                P('Fita de LED 24 V sob a viga', L - 900, 10, 'metalon', obs='componente comprado, fonte 24 V 60 W')], \
            ['Montar os quadros das colunas e chumbar ou lastrear as chapas de base (20 kg por coluna).', 'Encaixar a viga nas colunas e travar os pinos.', 'Vestir as lonas e tensionar os elásticos.', 'Ligar a fita de LED na fonte 24 V (instalação por eletricista da loja).']
    if t == 'ilha':
        hs = min(H * 0.35, 450)
        return [P('Saia frontal/traseira', L, hs, 'mdf15', qtd=2), P('Saia lateral', D, hs, 'mdf15', qtd=2),
                P('Tampo com bandejas', L, D, 'mdf18', obs='sobre 2 pallets PBR 1200 x 1000'),
                P('Header aéreo', L * 0.8, 400, 'ps2', qtd=2, obs='frente e verso, no mastro central'),
                P('Mastro central metalon', 30, 1500, 'metalon', obs='encaixa em luva no tampo'),
                P('Lábio de prateleira', L, 60, 'ps2', qtd=2)], \
            ['Posicionar os 2 pallets lado a lado.', 'Fixar as saias nos pallets por cantoneiras de encaixe.', 'Apoiar o tampo e encaixar o mastro na luva.', 'Encaixar os headers frente e verso no mastro.', 'Abastecer em degraus.']
    if t == 'gondola_marca':
        return [P('Fundo / backwall', L, H * 0.7, 'mdf15', obs='3 módulos de 1000 mm unidos por cavilha'), P('Lateral', D, H, 'mdf18', qtd=2),
                P('Prateleira', L / 3 - 18, D - 20, 'mdf18', qtd=12, obs='4 por módulo, apoiadas em suportes de encaixe'),
                P('Header', L, 400, 'mdf15'), P('Base / rodapé', L, 150, 'mdf18'), P('Lábio de preço', L / 3, 40, 'ps2', qtd=12)], \
            ['Montar as laterais e a base por cavilhas e minifix.', 'Encaixar os 3 fundos e travar.', 'Instalar os suportes e as prateleiras.', 'Fixar o header no topo.', 'Encaixar os lábios de preço.']
    if t == 'sampling_station':
        hb = min(950, H)
        return [P('Frente do balcão', L, hb - 30, 'mdf15'), P('Lateral do balcão', D, hb - 30, 'mdf15', qtd=2),
                P('Tampo', L + 40, D + 40, 'mdf18', obs='borda em fita PVC 2 mm'), P('Prateleira interna', L - 30, D - 30, 'mdf15'),
                P('Header', L * 0.7, 300, 'ps2'), P('Mastro do header', 30, H - hb, 'metalon', qtd=2)], \
            ['Montar frente e laterais por minifix.', 'Fixar a prateleira interna e o tampo.', 'Encaixar os mastros nas luvas do tampo e o header neles.', 'Higienizar o tampo antes da degustação.']
    if t == 'fachada_loja':
        hl = 600
        return [P('Estrutura da parede (quadro metalon)', L, H - hl, 'metalon', obs='montantes a cada 600 mm, fixados na parede existente com bucha 10'),
                P('Revestimento da parede', L, H - hl, 'acm3', obs='placas de 1500 mm, junta seca 10 mm, adesivo impresso laminado'),
                P('Caixa do letreiro', L, hl, 'acm3', obs='caixa de ACM com 250 mm de profundidade'),
                P('Face luminosa do letreiro', L - 40, hl - 40, 'acril3', obs='LED módulo 12 V, fonte selada IP67'),
                P('Porta de vidro temperado 8 mm', min(1200, L * 0.28), min(2300, (H - hl) * 0.86), 'acril3', obs='fornecimento da obra; aqui só a adesivagem jateada')], \
            ['Fixar o quadro de metalon na parede existente (nível e prumo).', 'Aplicar as placas de ACM adesivadas, da esquerda para a direita.', 'Instalar a caixa do letreiro e ligar a fonte (eletricista).', 'Adesivar a porta de vidro.', 'Aprovar com a marca antes de energizar o letreiro.']
    return [P('Painel', L, H, 'ps2')], ['Montagem conforme o 3D.']


def aproveitamento(paineis):
    """Encaixe por prateleiras (shelf packing) em cada chapa comercial: n.º de chapas e % de uso por material."""
    res = {}
    for mat in {p['mat'] for p in paineis}:
        cw, ch = MAT[mat][2]
        if mat in ('metalon', 'vinil', 'lona'):
            continue
        itens = []
        for p in paineis:
            if p['mat'] != mat or p['w'] <= 0: continue
            w, h = sorted((p['w'] + 10, p['h'] + 10), reverse=True)
            if w > cw: w, h = h, w
            itens += [(w, h)] * p['qtd']
        itens.sort(key=lambda x: -x[1])
        chapas, cur = 0, None
        for w, h in itens:
            if w > cw or h > ch:
                chapas += math.ceil(w / cw) * math.ceil(h / ch); continue
            if cur is None: cur = [0, 0, 0]; chapas += 1        # x, y, altura da prateleira
            if cur[0] + w > cw: cur = [0, cur[1] + cur[2], 0]
            if cur[1] + h > ch: cur = [0, 0, 0]; chapas += 1
            cur[0] += w; cur[2] = max(cur[2], h)
        area = sum(w * h for w, h in itens)
        res[mat] = (chapas, 100 * area / max(1, chapas * cw * ch))
    return res


def dxf(paineis, destino, titulo):
    doc = ezdxf.new('R2018', setup=True); doc.units = ezdxf.units.MM
    for n, c, lt in (('CORTE', 1, 'CONTINUOUS'), ('VINCO', 5, 'DASHED'), ('FURO', 3, 'CONTINUOUS'), ('COTA', 8, 'CONTINUOUS'), ('TEXTO', 7, 'CONTINUOUS')):
        doc.layers.add(n, color=c, linetype=lt)
    msp = doc.modelspace()
    x = 0
    for p in paineis:
        w, h = p['w'], p['h']
        if w <= 0 or p['mat'] in ('metalon',) and p['obs'].startswith('componente'): continue
        if p['contorno'] == 'circulo':
            msp.add_circle((x + w / 2, h / 2), w / 2, dxfattribs={'layer': 'CORTE'})
        elif p['contorno'] == 'raio20':
            r = 20
            pts = [(x + r, 0), (x + w - r, 0, ), (x + w, r), (x + w, h - r), (x + w - r, h), (x + r, h), (x, h - r), (x, r)]
            pl = msp.add_lwpolyline([(x + r, 0, 0), (x + w - r, 0, 0.4142), (x + w, r, 0), (x + w, h - r, 0.4142), (x + w - r, h, 0), (x + r, h, 0.4142), (x, h - r, 0), (x, r, 0.4142)], format='xyb', close=True, dxfattribs={'layer': 'CORTE'})
        else:
            msp.add_lwpolyline([(x, 0), (x + w, 0), (x + w, h), (x, h)], close=True, dxfattribs={'layer': 'CORTE'})
        for (x1, y1, x2, y2) in p['vincos']:
            msp.add_line((x + x1, y1), (x + x2, y2), dxfattribs={'layer': 'VINCO'})
        for (fx, fy, r) in p['furos']:
            msp.add_circle((x + fx, fy), r, dxfattribs={'layer': 'FURO'})
        for (rx, ry, rw, rh) in p['rasgos']:
            msp.add_lwpolyline([(x + rx, ry), (x + rx + rw, ry), (x + rx + rw, ry + rh), (x + rx, ry + rh)], close=True, dxfattribs={'layer': 'CORTE'})
        d = msp.add_linear_dim(base=(x, -60), p1=(x, 0), p2=(x + w, 0), dimstyle='EZDXF', dxfattribs={'layer': 'COTA'}); d.render()
        d = msp.add_linear_dim(base=(x - 60, 0), p1=(x, 0), p2=(x, h), angle=90, dimstyle='EZDXF', dxfattribs={'layer': 'COTA'}); d.render()
        msp.add_text(f"{p['nome']} | {MAT[p['mat']][0]} | qtd {p['qtd']}", height=max(8, min(40, w / 30)), dxfattribs={'layer': 'TEXTO'}).set_placement((x, h + 30))
        x += w + 200
    msp.add_text(titulo, height=60, dxfattribs={'layer': 'TEXTO'}).set_placement((0, -300))
    doc.saveas(destino)


def carimbo(fig, m, p, folha, total, titulo):
    ax = fig.add_axes([0.0, 0.0, 1, 0.075]); ax.axis('off')
    ax.add_patch(Rectangle((0.005, 0.08), 0.99, 0.84, fill=False, lw=1.2, transform=ax.transAxes))
    if os.path.exists(LOGO):
        im = Image.open(LOGO); la = fig.add_axes([0.012, 0.012, 0.08, 0.05]); la.imshow(im); la.axis('off')
    campos = [('CLIENTE', f"Arcor · {m['nome']}"), ('PEÇA', p['nome']), ('FOLHA', titulo), ('MEDIDAS (L x A x P)', f"{p['larguraCm']:g} x {p['alturaCm']:g} x {p['profundidadeCm']:g} cm"),
              ('REV.', 'R00'), ('DATA', HOJE), ('Nº', f'{folha}/{total}')]
    xs = [0.11, 0.25, 0.47, 0.64, 0.80, 0.86, 0.94]
    for (k, v), x0 in zip(campos, xs):
        ax.text(x0, 0.68, k, fontsize=6, color='#666', transform=ax.transAxes)
        ax.text(x0, 0.3, v, fontsize=8.5, weight='bold', transform=ax.transAxes)
    ax.text(0.11, -0.05, 'Projeto 75 LAB. Medidas em mm salvo indicação. Validar prova de corte e cor com a gráfica antes da tiragem.', fontsize=5.5, color='#666', transform=ax.transAxes)


def vista(ax, w, h, rotulo, cor='#ddd'):
    ax.add_patch(Rectangle((0, 0), w, h, fc=cor, ec='k', lw=1))
    ax.annotate('', (0, -0.08 * max(w, h)), (w, -0.08 * max(w, h)), arrowprops=dict(arrowstyle='<->', lw=0.7))
    ax.text(w / 2, -0.13 * max(w, h), f'{w:g}', ha='center', va='top', fontsize=8)
    ax.annotate('', (-0.08 * max(w, h), 0), (-0.08 * max(w, h), h), arrowprops=dict(arrowstyle='<->', lw=0.7))
    ax.text(-0.11 * max(w, h), h / 2, f'{h:g}', ha='right', va='center', fontsize=8, rotation=90)
    ax.set_title(rotulo, fontsize=9, loc='left'); ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(-0.25 * max(w, h), w + 0.05 * max(w, h)); ax.set_ylim(-0.25 * max(w, h), h + 0.05 * max(w, h))


def pdf(m, p, paineis, montagem, apr, destino, saida3d):
    L, H, D = p['larguraCm'] * 10, p['alturaCm'] * 10, p['profundidadeCm'] * 10
    A3 = (16.54, 11.69)
    total = 3
    with PdfPages(destino) as pp:
        # 1. vistas + render + arte
        fig = plt.figure(figsize=A3)
        fig.suptitle(f"{p['nome']} · projeto executivo", x=0.02, y=0.975, ha='left', fontsize=16, weight='bold')
        fig.text(0.02, 0.935, f"{p['funcao']}. Categoria: {CAT['categorias'][p['categoria']].lower()}. Quantidade de referência: {p['quantidade']} un.", fontsize=9)
        vista(fig.add_axes([0.02, 0.45, 0.22, 0.45]), L, H, 'VISTA FRONTAL (mm)')
        vista(fig.add_axes([0.25, 0.45, 0.14, 0.45]), max(D, 1), H, 'VISTA LATERAL')
        vista(fig.add_axes([0.02, 0.12, 0.22, 0.28]), L, max(D, 1), 'VISTA SUPERIOR')
        for i, (arq, tit) in enumerate(((os.path.join(saida3d, 'hero.jpg'), 'RENDER 3D NO PDV'), (p['arteFace'], f"ARTE DA FACE PRINCIPAL ({p['facePrincipal']}, {p['faceCm'][0]:g} x {p['faceCm'][1]:g} cm)"))):
            ax = fig.add_axes([0.42 + i * 0.29, 0.12, 0.27, 0.78]); ax.axis('off'); ax.set_title(tit, fontsize=9, loc='left')
            if os.path.exists(arq):
                im = Image.open(arq).convert('RGB'); im.thumbnail((1300, 1300)); ax.imshow(im)
        carimbo(fig, m, p, 1, total, 'Vistas, render e arte'); pp.savefig(fig); plt.close(fig)
        # 2. planificados / facas
        fig = plt.figure(figsize=A3)
        fig.suptitle('Planificados e facas (CORTE contínuo, VINCO tracejado, FURO verde). DXF 1:1 em anexo.', x=0.02, y=0.975, ha='left', fontsize=12, weight='bold')
        vis = [q for q in paineis if q['w'] > 0 and not q['obs'].startswith('componente')]
        n = len(vis); cols = min(4, n); rows = math.ceil(n / cols)
        for i, q in enumerate(vis):
            ax = fig.add_axes([0.03 + (i % cols) * (0.94 / cols), 0.12 + (rows - 1 - i // cols) * (0.8 / rows), 0.94 / cols - 0.03, 0.8 / rows - 0.05])
            w, h = q['w'], q['h']
            if q['contorno'] == 'circulo': ax.add_patch(Circle((w / 2, h / 2), w / 2, fc='#f4f4f4', ec='r', lw=1))
            else: ax.add_patch(Rectangle((0, 0), w, h, fc='#f4f4f4', ec='r', lw=1))
            for (x1, y1, x2, y2) in q['vincos']: ax.plot([x1, x2], [y1, y2], 'b--', lw=0.8)
            for (fx, fy, r) in q['furos']: ax.add_patch(Circle((fx, fy), max(r, w / 150), fc='none', ec='g'))
            for (rx, ry, rw, rh) in q['rasgos']: ax.add_patch(Rectangle((rx, ry), rw, max(rh, h / 200), fc='none', ec='r'))
            ax.set_xlim(-0.05 * max(w, h), w + 0.05 * max(w, h)); ax.set_ylim(-0.12 * max(w, h), h + 0.05 * max(w, h)); ax.set_aspect('equal'); ax.axis('off')
            ax.set_title(f"{q['nome']} · {w} x {h} mm · qtd {q['qtd']}", fontsize=7.5, loc='left')
            ax.text(0, -0.08 * max(w, h), textwrap.fill(MAT[q['mat']][0] + ('. ' + q['obs'] if q['obs'] else ''), int(150 / cols)), fontsize=6, va='top')
        carimbo(fig, m, p, 2, total, 'Planificados e facas'); pp.savefig(fig); plt.close(fig)
        # 3. lista de materiais, aproveitamento, montagem
        fig = plt.figure(figsize=A3)
        fig.suptitle('Lista de materiais, aproveitamento de chapa e montagem', x=0.02, y=0.975, ha='left', fontsize=12, weight='bold')
        ax = fig.add_axes([0.02, 0.5, 0.96, 0.42]); ax.axis('off')
        lin = [[q['nome'], f"{q['w']} x {q['h']}" if q['w'] else '-', MAT[q['mat']][0], str(q['qtd']), q['obs'] or '-'] for q in paineis]
        tb = ax.table(cellText=lin, colLabels=['Componente', 'Medida (mm)', 'Material', 'Qtd', 'Observação'], loc='upper left', cellLoc='left', colWidths=[0.2, 0.09, 0.3, 0.04, 0.37])
        tb.auto_set_font_size(False); tb.set_fontsize(7.5); tb.scale(1, 1.5)
        y = 0.45
        fig.text(0.02, y, 'APROVEITAMENTO DE CHAPA (por peça montada)', fontsize=10, weight='bold')
        for mat, (n_, pct) in apr.items():
            y -= 0.03; fig.text(0.02, y, f"{MAT[mat][0]}: chapa {MAT[mat][2][0]} x {MAT[mat][2][1]} mm, {n_} chapa(s), uso {pct:.0f}%", fontsize=8.5)
        y = 0.45
        fig.text(0.5, y, 'SEQUÊNCIA DE MONTAGEM', fontsize=10, weight='bold')
        for i, s in enumerate(montagem):
            y -= 0.03; fig.text(0.5, y, f'{i + 1}. {s}', fontsize=8.5)
        y -= 0.05
        fig.text(0.5, y, 'NOTAS', fontsize=10, weight='bold')
        for s in ['Arte final: aplicar a arte aprovada sobre a faca, sangria de 3 mm em todo o contorno.',
                  'Cores: perfil de cor da gráfica; prova de cor física obrigatória para logo e embalagem.',
                  'Encaixes com folga de 0,4 mm sobre a espessura nominal do material.',
                  'Logo, embalagem e textos seguem o KV oficial; aprovação da marca Arcor antes da produção.']:
            y -= 0.03; fig.text(0.5, y, '· ' + s, fontsize=8)
        carimbo(fig, m, p, 3, total, 'Materiais e montagem'); pp.savefig(fig); plt.close(fig)


def marca(mid):
    m = CAT['marcas'][mid]
    for p in m['pecas']:
        pasta = os.path.join(RAIZ, 'engenharia', mid, p['id']); os.makedirs(pasta, exist_ok=True)
        paineis, montagem = projeto(p)
        apr = aproveitamento(paineis)
        base = f"ARCOR-{mid.upper()}-{p['id'].upper()}-R00"
        dxf(paineis, os.path.join(pasta, base + '.dxf'), f"{p['nome']} · planificados 1:1 (mm)")
        pdf(m, p, paineis, montagem, apr, os.path.join(pasta, base + '.pdf'), os.path.join(RAIZ, 'lotes', mid, 'saida', p['id']))
        json.dump({'paineis': paineis, 'montagem': montagem, 'aproveitamento': apr}, open(os.path.join(pasta, 'ficha.json'), 'w'), ensure_ascii=False, indent=1)
        print(mid, p['id'], 'ok', flush=True)


if __name__ == '__main__':
    for mid in (sys.argv[1:] or list(CAT['marcas'])):
        marca(mid)
