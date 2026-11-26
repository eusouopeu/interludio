"""
Figura 3.2 - Do dado à decisão: blocos de coleta, tratamento e uso no plano.

Resume o Quadro 3.2 e a seção 3.3 como um fluxo: cada bloco (B1 a B5) passa
por um tratamento próprio e alimenta capítulos do plano; todas as premissas
recebem um nível de evidência (N1 a N6) e entram no modelo financeiro.
Diagrama sem dados. Saída: textos-tcc/figuras/3-2_dado_decisao.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402
import graficos_comum as gc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "3-2_dado_decisao.png"

# (bloco, tratamento, uso no plano)
LINHAS = [
    ("B1 – Concorrentes\nGoogle Maps, Instagram, acervos",
     "Triagem da população; medianas de preço e cardápio; cesta de jogos",
     "Concorrência e ponto (cap. 5); preço e ticket (cap. 6); receita (cap. 9)"),
    ("B2 – Avaliações recentes\nGoogle Maps",
     "Codificação dos temas; penalidade e recompensa; velocidade de avaliações",
     "Proposta de valor e reclamações (cap. 6); fluxo relativo (cap. 9)"),
    ("B3 – Contagem direta\nSão Jogue e NFC-e",
     "Circulação, grupo, permanência e ocupação; notas como piso das vendas",
     "Mesas e equipe (cap. 7); pessoas por mês (cap. 9)"),
    ("B4 – Bases públicas\nIBGE, CAGED, FipeZap, BCB",
     "Recorte por cidade e data; séries de preços e juros",
     "Público e renda (cap. 5); tributos (cap. 8); salários e TMA (cap. 9)"),
    ("B5 – Ativos fixos\nSINAPI e anúncios",
     "Quartis das ofertas de cada item; composições com BDI",
     "Investimento inicial, aluguel e condomínio (cap. 9)"),
]


def main():
    fig, ax = dc.figura(6.3, 5.0, xmax=10.25, ymax=7.55)
    xb, wb = 1.25, 2.4
    xt, wt = 4.6, 3.7
    xu, wu = 8.3, 3.2
    h, passo, y0 = 0.95, 1.18, 0.95

    for x, titulo in [(xb, "Bloco e fonte"), (xt, "Tratamento"), (xu, "Uso no plano")]:
        ax.text(x, 0.2, titulo, ha="center", va="center", fontsize=dc.FONTE_PT,
                color=gc.TINTA2, fontweight="semibold")

    for i, (bloco, trat, uso) in enumerate(LINHAS):
        y = y0 + i * passo
        dc.caixa(ax, xb, y, wb, h, bloco, "destaque_leve", largura=26)
        dc.caixa(ax, xt, y, wt, h, trat, "pergunta", largura=40)
        dc.caixa(ax, xu, y, wu, h, uso, "pergunta", largura=34)
        dc.seta(ax, [(xb + wb / 2, y), (xt - wt / 2, y)])
        dc.seta(ax, [(xt + wt / 2, y), (xu - wu / 2, y)])

    # todas as linhas convergem para a matriz de premissas
    y_ult = y0 + (len(LINHAS) - 1) * passo
    yf = y_ult + 1.35
    xr = xu + wu / 2 + 0.12
    for i in range(len(LINHAS)):
        y = y0 + i * passo
        ax.plot([xu + wu / 2, xr], [y, y], color=gc.TINTA3, lw=1.0, zorder=1)
    dc.seta(ax, [(xr, y0), (xr, yf - 0.1), (5.1 + 4.6, yf - 0.1)])
    dc.caixa(ax, 5.1, yf, 9.2, 0.75,
             "Premissas com fonte e nível de evidência (N1 a N6) → modelo financeiro, "
             "cenários e sensibilidade (cap. 9) → decisões do plano",
             "destaque", largura=90)
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
