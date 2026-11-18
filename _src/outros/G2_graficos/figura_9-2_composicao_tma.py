"""
Figura 9.2 - Composição da TMA: da Selic ao juro real e do juro real à TMA.

Mostra a equação (3) do capítulo 9 (juro real pela Selic meta e pelo IPCA
esperado) e o prêmio de risco somado em três parcelas, na ordem pedida pelo
autor: risco do setor, risco-país e liquidez. O prêmio total (5,7 pp) é N6 e
não é repartido entre as parcelas. Diagrama sem dados novos.
Saída: textos/figuras/9-2_composicao_tma.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402
import graficos_comum as gc  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

SAIDA = ROOT / "textos" / "figuras" / "9-2_composicao_tma.png"


def main():
    fig, ax = dc.figura(6.3, 4.4, ymax=6.45)
    caixa, seta = dc.caixa, dc.seta

    caixa(ax, 5.0, 0.45, 5.2, 0.7, "Selic meta: 14,0% ao ano\nBanco Central, setembro de 2026",
          "inicio")
    seta(ax, [(5.0, 0.8), (5.0, 1.6)], "descontada a inflação esperada: IPCA de 4,3% (Focus)",
         (5.0, 1.2))
    caixa(ax, 5.0, 1.95, 5.2, 0.7, "Juro real: 9,3% ao ano\n(1 + Selic) ÷ (1 + IPCA) − 1",
          "destaque_leve")
    seta(ax, [(5.0, 2.3), (5.0, 3.05)], "+", (5.0, 2.68))

    # prêmio de risco em três parcelas, dentro de um grupo tracejado
    ax.add_patch(FancyBboxPatch((0.15, 3.05), 9.7, 1.75, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="none", ec=gc.MEDIO, lw=0.9, ls=(0, (3, 2)), zorder=1))
    ax.text(5.0, 3.28, "Prêmio de risco: 5,7 pontos percentuais (N6)", ha="center", va="center",
            fontsize=dc.FONTE_PT, color=gc.TINTA2, fontweight="semibold")
    parcelas = [
        "Risco do setor\npequeno negócio novo: 25,8% fecham em cinco anos",
        "Risco-país\nambiente econômico e institucional do Brasil",
        "Liquidez\ninvestimento sem mercado para venda rápida",
    ]
    xs, w = [1.75, 5.0, 8.25], 2.95
    for i, (x, texto) in enumerate(zip(xs, parcelas)):
        caixa(ax, x, 4.1, w, 1.0, texto, "pergunta", largura=27)
        if i:
            ax.text((xs[i - 1] + x) / 2, 4.1, "+", ha="center", va="center",
                    fontsize=dc.FONTE_PT + 2, color=gc.TINTA2, fontweight="semibold")
    seta(ax, [(5.0, 4.8), (5.0, 5.5)])
    caixa(ax, 5.0, 5.95, 5.2, 0.85,
          "TMA provável: 15% ao ano\ncenários: 12% (otimista) e 18% (pessimista)", "destaque")
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
