# Catálogo único das peças de PDV Arcor (4 marcas x 15 peças). Fonte de verdade para ChatGPT, 3D, AR, engenharia e site.
#   python3 catalogo.py   -> grava catalogo.json e lotes/<marca>/pedido.json
import json, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARCAS = {
    '7belo': {
        'nome': '7Belo', 'produto': '7Belo Pirulito Recheado', 'cores': {'primaria': '#1B2A6B', 'secundaria': '#E6194B'},
        'titulo': 'Agora em pirulito!', 'destaque': 'pirulito', 'subtitulo': 'Framboesa por fora, bala mastigável por dentro',
        'textos': ['7Belo', 'O sabor inconfundível de 7Belo agora em pirulito!', 'Pirulito recheado', 'Não tem como ficar melhor!'],
        'visual': 'fundo azul-marinho com losangos vermelhos e faixa de padrão rosa/vermelho em ziguezague, pirulitos vermelhos de framboesa, tipografia condensada branca com destaque rosa',
        'emb': {'tipo': 'saco', 'larguraCm': 18, 'alturaCm': 24, 'profundidadeCm': 4},
    },
    'butter-toffees': {
        'nome': 'Butter Toffees', 'produto': 'Butter Toffees Intense', 'cores': {'primaria': '#2A1810', 'secundaria': '#C9A15A'},
        'titulo': 'Recheada com 53% cacau', 'destaque': '53% cacau', 'subtitulo': 'Butter Toffees Intense: chocolate, trufa, menta e pistache',
        'textos': ['Butter Toffees Intense', 'Recheada com 53% cacau', 'Chocolate', 'Trufa', 'Menta', 'Pistache'],
        'visual': 'fundo marrom-chocolate escuro e premium, splash de chocolate derretido, bombons partidos, detalhes dourados, tipografia serifada dourada',
        'emb': {'tipo': 'saco', 'larguraCm': 15, 'alturaCm': 18, 'profundidadeCm': 4},
    },
    'rocklets': {
        'nome': 'Rocklets', 'produto': 'Rocklets', 'cores': {'primaria': '#141414', 'secundaria': '#E52421'},
        'titulo': 'Crocante por fora, irresistível por dentro!', 'destaque': 'irresistível', 'subtitulo': 'Confeitos de chocolate coloridos Rocklets',
        'textos': ['Rocklets', 'Crocante por fora', 'Irresistível por dentro!'],
        'visual': 'fundo preto com linhas circulares em espiral, explosão de confeitos coloridos (vermelho, amarelo, verde, azul, laranja), confeito vermelho partido mostrando chocolate, letreiro marrom 3D brilhante',
        'emb': {'tipo': 'saco', 'larguraCm': 14, 'alturaCm': 9, 'profundidadeCm': 2},
    },
    'tortuguita': {
        'nome': 'Tortuguita', 'produto': 'Tortuguita', 'cores': {'primaria': '#1E5FD0', 'secundaria': '#FFD200'},
        'titulo': 'Cremosa, recheada e agora com mais leite!', 'destaque': 'mais leite', 'subtitulo': 'Tortuguita: chocolate recheado Arcor',
        'textos': ['Tortuguita', 'Cremosa, recheada e agora com mais leite!'],
        'visual': 'fundo azul com espiral clara, onda de leite e chocolate, tartaruga mascote surfando na prancha, letreiro amarelo com contorno azul',
        'emb': {'tipo': 'saco', 'larguraCm': 9, 'alturaCm': 6, 'profundidadeCm': 2.5},
    },
}

# categoria, id, tipo, nome, L, H, D (cm), material, quantidade, face principal (arte do ChatGPT), função
PECAS = [
    ('leve', 'regua', 'faixa_gondola', 'Régua de gôndola', 100, 5, 0.3, 'pvc', 2000, 'frente', 'Marca a prateleira da marca no ponto de preço'),
    ('leve', 'wobbler', 'wobbler', 'Wobbler', 15, 15, 0.05, 'pvc', 3000, 'frente', 'Balança na frente da prateleira e chama o olhar para o produto'),
    ('leve', 'stopper', 'stopper', 'Stopper', 20, 30, 0.2, 'pvc', 2000, 'frente', 'Para o shopper no corredor, perpendicular à gôndola'),
    ('leve', 'testeira', 'testeira', 'Testeira de gôndola', 100, 30, 0.3, 'pvc', 800, 'frente', 'Identifica o bloco da marca no topo do módulo'),
    ('leve', 'clipstrip', 'clip_strip', 'Clip strip', 12, 80, 1, 'pet', 1500, 'topo', 'Exposição pendurada para compra por impulso em cross merchandising'),
    ('leve', 'adesivo-chao', 'adesivo_chao', 'Adesivo de chão', 60, 60, 0.05, 'vinil', 600, 'frente', 'Conduz o shopper até a gôndola da marca'),
    ('media', 'display-chao', 'display_chao', 'Display de chão', 60, 160, 40, 'papelao_e', 300, 'header', 'Ponto extra com produto e header da campanha'),
    ('media', 'display-balcao', 'display_balcao', 'Display de balcão', 40, 35, 28, 'papelao_e', 1500, 'header', 'Impulso no checkout, perto do caixa'),
    ('media', 'totem', 'totem', 'Totem', 60, 180, 35, 'mdf', 120, 'frente', 'Sinaliza a campanha na entrada e no corredor'),
    ('media', 'ponta-gondola', 'ponta_gondola', 'Ponta de gôndola', 100, 200, 50, 'mdf', 60, 'header', 'Ponta de gôndola temática com produto e header'),
    ('media', 'portal', 'portal_corredor', 'Portal de corredor', 240, 260, 45, 'metalon_lona', 20, 'viga', 'Arco sobre o corredor da categoria de doces'),
    ('pesada', 'ilha', 'ilha', 'Ilha promocional', 200, 140, 120, 'mdf', 15, 'header', 'Ilha de pallet no corredor principal com volume de produto'),
    ('pesada', 'store-in-store', 'gondola_marca', 'Store in store', 300, 200, 60, 'mdf', 10, 'fundo', 'Espaço próprio da marca dentro da loja'),
    ('pesada', 'degustacao', 'sampling_station', 'Ambientação de degustação', 120, 200, 60, 'mdf', 10, 'frente', 'Balcão de degustação com promotora e header'),
    ('pesada', 'fachada', 'fachada_loja', 'Fachada de loja', 400, 320, 40, 'acm_lona', 4, 'parede', 'Fachada temática de loja ou quiosque da marca'),
]

CATEGORIAS = {'leve': 'Peças leves', 'media': 'Peças médias', 'pesada': 'Peças pesadas'}


def dims_face(tipo, face, L, H, D):
    """Medida (cm) da face principal, igual ao faces_da_peca do artes.py."""
    if tipo == 'display_chao': return L, min(max(H * 0.2, 22), 40)
    if tipo == 'display_balcao': return L, H * 0.42
    if tipo == 'ponta_gondola': return L, min(50, H * 0.26)
    if tipo == 'ilha': return L * 0.8, 40
    if tipo == 'gondola_marca': return L, H * 0.7
    if tipo == 'clip_strip': return L, min(H * 0.3, 18)
    if tipo == 'sampling_station': return L, min(95, H) - 3
    if tipo == 'portal_corredor': return L, 50
    if tipo == 'fachada_loja': return L, H - 60
    if tipo == 'wobbler': return L, L
    return L, H


def montar():
    cat = {'marcas': {}, 'categorias': CATEGORIAS}
    for mid, m in MARCAS.items():
        lote = os.path.join(RAIZ, 'lotes', mid)
        os.makedirs(os.path.join(lote, 'entrada'), exist_ok=True)
        pecas = []
        for (c, pid, tipo, nome, L, H, D, mat, qtd, fp, funcao) in PECAS:
            fw, fh = dims_face(tipo, fp, L, H, D)
            arte = os.path.join(RAIZ, 'chatgpt', mid, f'{pid}-arte.png')       # saída do ChatGPT
            face = os.path.join(lote, 'entrada', f'{pid}-{fp}.png')            # arte na proporção exata da face
            pecas.append({'categoria': c, 'id': pid, 'tipo': tipo, 'nome': f"{nome} {m['nome']}", 'larguraCm': L, 'alturaCm': H,
                          'profundidadeCm': D, 'material': mat, 'quantidade': qtd, 'titulo': m['titulo'], 'funcao': funcao,
                          'facePrincipal': fp, 'faceCm': [round(fw, 1), round(fh, 1)], 'arteChatgpt': arte, 'arteFace': face,
                          'produtos': ['emb'], 'artes': {fp: face} if os.path.exists(face) else {}})
        ped = {'marca': m['nome'], 'projeto': f"Arcor · {m['nome']} · peças de PDV", 'cores': m['cores'], 'kvFoco': [0.5, 0.5],
               'titulo': m['titulo'], 'destaque': m['destaque'], 'subtitulo': m['subtitulo'], 'beneficios': [],
               'chamadaQr': 'Veja a peça em realidade aumentada', 'qrUrl': f'https://projetos.75lab.com.br/ar/arcor-{mid}/',
               'logo': os.path.join(RAIZ, 'chatgpt', mid, 'logo.png'), 'kv': os.path.join(RAIZ, 'kv', f'{mid}.jpg'),
               'produtos': [{'id': 'emb', 'nome': m['produto'], 'imagem': os.path.join(RAIZ, 'chatgpt', mid, 'packshot.png'), 'verso': None, **m['emb']}],
               'pecas': pecas}
        json.dump(ped, open(os.path.join(lote, 'pedido.json'), 'w'), ensure_ascii=False, indent=1)
        cat['marcas'][mid] = {**m, 'pecas': pecas}
    json.dump(cat, open(os.path.join(RAIZ, 'catalogo.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    montar()
