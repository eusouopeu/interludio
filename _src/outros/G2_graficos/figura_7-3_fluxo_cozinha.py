"""
Figura 7.3 - Fluxo do cozinheiro: cinco etapas do turno (seção 7.5).

Cada etapa tem o nome, o que o cozinheiro faz e o horário no turno das 14h às 23h;
o intervalo de 1 h fica das 16h às 17h, antes do pico. Diagrama sem dados, no padrão visual dos demais
(diagramas_comum), com o mesmo desenho da Figura 7.2.
Saída: textos-tcc/figuras/7-3_fluxo_cozinha.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-3_fluxo_cozinha.png"

ETAPAS = [
    ("1. Mise en place", "Pré-preparo dos ingredientes do dia, com data de preparo e validade na etiqueta", "14:00 às 15:00"),
    ("2. Refeição", "Preparo da refeição da equipe, uma por turno", "15:00 às 15:30"),
    ("3. Serviço", "Preparo dos pedidos anotados à mesa e reposição do mise en place", "15:30 às 22:30"),
    ("4. Limpeza", "Higienização dos equipamentos, dos utensílios e das bancadas, com registro", "22:30 às 22:50"),
    ("5. Contagem", "Contagem dos itens menores (temperos, folhas e molhos) para o pedido do dia seguinte", "22:50 às 23:00"),
]


def main():
    fig, ax = dc.figura(7.0, 3.1, xmax=10, ymax=4.45)
    w, folga = 1.8, 0.25
    x0 = w / 2
    for i, (nome, texto, quando) in enumerate(ETAPAS):
        x = x0 + i * (w + folga)
        dc.caixa(ax, x, 0.45, w, 0.7, nome, "destaque", tamanho=9.4)
        dc.caixa(ax, x, 1.85, w, 1.7, texto, "pergunta", largura=16, tamanho=8.8)
        dc.caixa(ax, x, 3.2, w, 0.7, quando, "destaque_leve", tamanho=8.6)
        if i < len(ETAPAS) - 1:
            dc.seta(ax, [(x + w / 2, 1.85), (x + w / 2 + folga, 1.85)])
    dc.caixa(ax, 5.0, 4.05, 10, 0.5, "Intervalo de 1 hora das 16:00 às 17:00, antes do pico; nele, o salão serve só itens prontos. Último pedido às 22:30.", "nota", tamanho=8.8)
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
