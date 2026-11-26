"""
Figura 9.1 - Árvore de direcionadores do modelo financeiro.

Desenha como árvore o antigo Quadro 9.1: o fluxo de caixa se desdobra em
receita, custos e investimento, e cada folha traz o cálculo resumido e os
códigos do registro de premissas (seção 9.1). Diagrama sem dados.
Saída: textos-tcc/figuras/9-1_arvore_direcionadores.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402
import graficos_comum as gc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "9-1_arvore_direcionadores.png"
TAM = dc.FONTE_PT - 0.6

# (ramo, título da folha, cálculo e premissas)
FOLHAS = [
    ("Receita", "Taxa de entrada", "pessoas × taxa de entrada\nR05, R06"),
    ("Receita", "A&B", "pessoas × (gasto por pessoa − taxa)\nR04 a R06"),
    ("Receita", "Aluguel de jogos", "aluguéis × preço médio × rampa\nR07 a R10"),
    ("Custos", "Custos variáveis", "Simples, CMV do A&B, cartão\nC01, C02, aba simples"),
    ("Custos", "Custos fixos", "aluguel, pessoal, pró-labore e outros\nC03 a C15"),
    ("Investimento", "Investimento inicial", "obra, móveis, acervo, caução e giro\nI01 a I08, I10"),
]


def liga(ax, x0, y0, x1, y1):
    """Conector em cotovelo, da borda direita do pai à borda esquerda do filho."""
    xm = (x0 + x1) / 2
    ax.plot([x0, xm, xm, x1], [y0, y0, y1, y1], color=gc.TINTA3, lw=1.0, zorder=1)


def main():
    fig, ax = dc.figura(6.3, 4.2, ymax=6.1)
    x1, w1 = 0.85, 1.65
    x2, w2 = 2.7, 1.6
    x3, w3 = 5.55, 3.3
    x4, w4 = 8.65, 2.5
    h, passo, y0 = 0.82, 0.98, 0.5

    ys = [y0 + i * passo for i in range(len(FOLHAS))]
    ramos = {}
    for (ramo, titulo, calc), y in zip(FOLHAS, ys):
        ramos.setdefault(ramo, []).append(y)
        caixa_txt = f"{titulo}\n{calc}"
        dc.caixa(ax, x3, y, w3, h, caixa_txt, "pergunta", tamanho=TAM)

    yr = (ys[0] + ys[-1]) / 2
    dc.caixa(ax, x1, yr, w1, 1.3, "Fluxo de caixa\nVPL, TIR e payback", "destaque", tamanho=TAM)
    for ramo, yy in ramos.items():
        yc = (yy[0] + yy[-1]) / 2
        dc.caixa(ax, x2, yc, w2, 0.7, ramo, "destaque_leve", tamanho=TAM, peso="semibold")
        liga(ax, x1 + w1 / 2, yr, x2 - w2 / 2, yc)
        for y in yy:
            liga(ax, x2 + w2 / 2, yc, x3 - w3 / 2, y)

    # pessoas por mês alimenta a taxa de entrada e o A&B
    yp = (ys[0] + ys[1]) / 2
    dc.caixa(ax, x4, yp, w4, 1.75,
             "Pessoas por mês\ncirculação no pico × horas equivalentes × dias × rampa × semanas\n"
             "R01 a R03, R09, R10, O06, O07, M02", "destaque_leve", largura=30, tamanho=TAM)
    for y in ys[:2]:
        dc.seta(ax, [(x4 - w4 / 2, y), (x3 + w3 / 2, y)])
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
