# Rodada 2: conceitos criativos de cada peça gerados no ChatGPT (foto realista da peça montada na loja), para aprovação antes do 3D.
#   python3 conceitos.py [marca ...]   -> conceitos/<marca>/<nn>-<id>.png   (2 em paralelo; pula o que já existe)
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from chatgpt import rodar_servidor, RAIZ, CAT, LIMITE, log

# Linguagem de cada marca levada para a ESTRUTURA da peça (recortes, volumes, formas), não só para a impressão.
IDEIA = {
    '7belo': 'a bala virou pirulito: um ou dois pirulitos grandes em volume (esfera vermelha em acrílico ou PS termoformado, palito em tubo branco) '
             'como elemento principal, padrão de losangos azul e rosa do KV nas laterais',
    'butter-toffees': 'premium, quase boutique de chocolate: marrom profundo fosco com detalhes em dourado metalizado (hot stamping), '
                      'recortes em camadas que lembram uma onda de chocolate, poucos elementos e muito respiro',
    'rocklets': 'confetes coloridos: drágeas grandes em volume (meias esferas termoformadas nas cores da marca) aplicadas em pontos certos, '
                'fundo preto, recorte que segue a silhueta das drágeas',
    'tortuguita': 'a mascote Tortuguita como recorte grande em camadas (como um standee premium), onda de leite e chocolate como recorte '
                  'na base, azul e amarelo do KV',
}

PECA = {
    'regua': 'régua de gôndola (faixa de 5 cm na borda da prateleira, com aba recortada e pequeno elemento em volume saindo da régua)',
    'wobbler': 'wobbler (peça recortada no formato de um elemento da marca, presa na prateleira por haste flexível)',
    'stopper': 'stopper de gôndola (peça perpendicular à prateleira, recortada no formato da marca, que interrompe o corredor)',
    'testeira': 'testeira de gôndola (topo da gôndola, com recorte que sai do retângulo e elementos em volume)',
    'clipstrip': 'clip strip (fita vertical de 80 cm com ganchos segurando embalagens, topo recortado com o logo)',
    'adesivo-chao': 'adesivo de chão (recortado no formato da marca, perto da gôndola, guiando o cliente)',
    'display-chao': 'display de chão de papelão com 3 bandejas de produto, header recortado e elementos em volume',
    'display-balcao': 'display de balcão de caixa, compacto, com produto à mostra e recorte criativo',
    'totem': 'totem autoportante de 1,80 m com a marca em volume e silhueta recortada',
    'ponta-gondola': 'ponta de gôndola completa (prateleiras abastecidas, header grande recortado, laterais e rodapé tematizados)',
    'portal': 'portal de corredor (arco de entrada do corredor de doces, com elementos gigantes em volume nos pilares e no topo)',
    'ilha': 'ilha promocional no meio do corredor (abastecida, com elementos gigantes em volume e header suspenso)',
    'store-in-store': 'store in store (espaço exclusivo da marca com gôndolas próprias, piso, teto e iluminação tematizados)',
    'degustacao': 'ambientação de degustação (balcão de sampling tematizado, backdrop e elementos em volume)',
    'fachada': 'fachada de loja conceito (quiosque ou loja pop-up da marca dentro do shopping, com vitrine e letreiro em volume)',
}


GONDOLA = ('regua', 'wobbler', 'stopper', 'testeira', 'clipstrip')


def FUNDO(p):
    if p['id'] in GONDOLA:
        return ('fundo neutro com um trecho de gôndola de supermercado toda em cinza claro fosco, VAZIA, sem nenhum produto, '
                'só com as embalagens da marca na prateleira onde a peça está aplicada, e parede cinza claro atrás.')
    return 'fundo infinito cinza claro liso (ciclorama), piso cinza claro, nada mais no quadro.'


def prompt(m, mid, p):
    return (f"Use a imagem anexada, que é o KEY VISUAL OFICIAL de {m['nome']} (Arcor), como referência obrigatória: mesmo logo, mesma embalagem "
            f"({m['produto']}), mesmas cores e mesma linguagem visual ({m['visual']}). "
            f"Crie o CONCEITO CRIATIVO de uma peça de ponto de venda: {PECA[p['id']]}, medida aproximada {p['larguraCm']:g} x {p['alturaCm']:g} cm. "
            f"Ideia da marca para levar à forma da peça: {IDEIA[mid]}. "
            'Seja INOVADOR NA IDEIA E NA FORMA (estrutura inesperada, uso inteligente do espaço, interação com o cliente ou com o produto), '
            'nunca nos efeitos. Nada de caixa retangular com arte colada. Acabamento de agência de primeira linha, com materiais reais e '
            'visíveis: impressão fosca, verniz localizado, hot stamping, recorte eletrônico com bordas reais, camadas de PS e papelão com '
            'espessura aparente, acrílico com reflexo verdadeiro. Uma ideia forte por peça, com contenção e respiro: poucos elementos. '
            'PROIBIDO (dá cara de IA): neon, LED brilhando em tudo, brilho mágico, partículas, chocolate ou líquido em computação gráfica, '
            'cores saturadas demais, HDR, luz cinematográfica, bokeh exagerado, tudo plástico e brilhante, excesso de elementos, simetria perfeita. '
            'A IMAGEM TEM QUE PARECER FOTO DE VERDADE: foto de estúdio de portfólio de agência de trade marketing, câmera full frame, '
            'lente 50 mm, luz de estúdio suave e neutra, balanço de branco natural, sombra real e suave da peça no piso, '
            'pequenas imperfeições de material real. A peça é o ÚNICO destaque: ' + FUNDO(p) + ' '
            'Sem loja, sem pessoas, sem outros produtos ou marcas. A peça montada, abastecida com as embalagens reais, inteira no quadro. '
            f"Textos permitidos, exatamente assim: {' | '.join(m['textos'])}. Nenhum outro texto, nenhum preço; na dúvida, sem texto.")


def marca(mid):
    m = CAT['marcas'][mid]
    ref = os.path.join(RAIZ, 'kv', f'{mid}-ref.jpg')
    tarefas = []
    for i, p in enumerate(m['pecas'], 1):
        d = os.path.join(RAIZ, 'conceitos', mid, f"{i:02d}-{p['id']}.png")
        prop = 'retrato' if p['alturaCm'] >= p['larguraCm'] * 1.2 and p['id'] not in ('regua',) else 'paisagem' if p['larguraCm'] > p['alturaCm'] * 1.2 else 'quadrada'
        if not os.path.exists(d): tarefas.append((prompt(m, mid, p), d, prop))

    def uma(t):
        for _ in range(2):
            if LIMITE['bateu']: return False
            if rodar_servidor(t[0], ref, t[1], t[2]): return True
        return False
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(uma, tarefas))
    log(mid, 'conceitos', len(os.listdir(os.path.join(RAIZ, 'conceitos', mid))) if os.path.isdir(os.path.join(RAIZ, 'conceitos', mid)) else 0, 'de', len(m['pecas']))


if __name__ == '__main__':
    for mid in (sys.argv[1:] or list(CAT['marcas'])):
        marca(mid)
        if LIMITE['bateu']: log('parando: limite'); sys.exit(3)
