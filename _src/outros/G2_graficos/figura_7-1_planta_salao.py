"""
Figura 7.1 - Planta esquemática do salão (8 mesas e 48 lugares desde a abertura).

Esquema sem escala da seção 7.1: salão com as estantes do acervo à vista das
mesas, balcão com caixa junto à entrada, cozinha, depósito de A&B, quatro
sanitários e rota acessível. As 8 mesas entram na abertura (decisão do autor,
    16/11/2026). O croqui definitivo
sai do projeto do imóvel. Saída: textos-tcc/figuras/7-1_planta_salao.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402
import graficos_comum as gc  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-1_planta_salao.png"
LARG, PROF = 16.0, 12.0  # unidades do esquema, sem escala
ROXO_CLARO = "#f3e8ff"


def ambiente(ax, x, y, w, h, texto, fc="white", rot=0, tam=None):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=gc.TINTA2, lw=1.0, zorder=2))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", rotation=rot,
            fontsize=tam or dc.FONTE_PT, color=gc.TINTA, linespacing=1.1, zorder=3)


def mesa(ax, x, y, reservada=False):
    """Mesa de 6 lugares centrada em (x, y): 2 cadeiras em cada lado longo e 1 em cada ponta."""
    ec, fc, ls = (gc.MEDIO, "white", (0, (3, 2))) if reservada else (gc.ROXO, ROXO_CLARO, "-")
    ax.add_patch(FancyBboxPatch((x - 0.75, y - 0.5), 1.5, 1.0,
                                boxstyle="round,pad=0,rounding_size=0.12",
                                fc=fc, ec=ec, lw=1.0, ls=ls, zorder=3))
    for cx, cy in [(x - 0.4, y - 0.8), (x + 0.4, y - 0.8), (x - 0.4, y + 0.8),
                   (x + 0.4, y + 0.8), (x - 1.05, y), (x + 1.05, y)]:
        ax.add_patch(Circle((cx, cy), 0.2, fc="white", ec=ec, lw=0.9, ls=ls, zorder=3))


def main():
    fig, ax = dc.figura(6.3, 5.2, xmax=LARG + 0.4, ymax=PROF + 1.0)
    ax.set_xlim(-0.4, LARG + 0.4)
    ax.set_aspect("equal")

    # fundo de serviço: cozinha, depósito e sanitários
    ambiente(ax, 0, 0, 5.0, 3.2, "Cozinha", fc=gc.APAGADO)
    ambiente(ax, 5.0, 0, 2.4, 3.2, "Depósito\nde A&B", fc=gc.APAGADO)
    sanitarios = ["Equipe", "Masc.", "Fem.", "Adaptado\ne fraldário"]
    w_s = (LARG - 7.4) / len(sanitarios)
    for i, nome in enumerate(sanitarios):
        ambiente(ax, 7.4 + i * w_s, 0, w_s, 2.4, nome, fc=gc.APAGADO, tam=dc.FONTE_PT - 0.6)

    # balcão com caixa junto à entrada e estantes do acervo à vista das mesas
    ambiente(ax, 0, 4.4, 1.3, 6.4, "Balcão e caixa", fc=gc.APAGADO, rot=90)
    ambiente(ax, LARG - 0.8, 3.6, 0.8, 7.6, "Estantes do acervo", fc=ROXO_CLARO, rot=90)

    # mesas: 4 colunas x 2 fileiras, todas desde a abertura
    for i, x in enumerate([3.4, 6.4, 10.4, 13.2]):
        for y in [5.6, 9.2]:
            mesa(ax, x, y)

    # paredes externas e fachada com porta
    porta = (7.6, 9.2)
    ax.add_patch(Rectangle((0, 0), LARG, PROF, fc="none", ec=gc.TINTA, lw=2.0, zorder=4))
    ax.plot(porta, [PROF, PROF], color="white", lw=3.0, zorder=5)
    ax.text(sum(porta) / 2, PROF + 0.55, "Entrada (rua)", ha="center", va="center",
            fontsize=dc.FONTE_PT, color=gc.TINTA2, fontweight="semibold")

    # rota acessível: entrada → mesas, balcão e sanitário adaptado
    xr = sum(porta) / 2
    rota = dict(color=gc.ROXO, lw=1.4, ls=(0, (1.2, 1.6)), zorder=1, solid_capstyle="round")
    ax.plot([xr, xr], [PROF - 0.1, 3.0], **rota)
    ax.plot([1.3, xr], [7.4, 7.4], **rota)
    ax.plot([xr, LARG - 1.1, LARG - 1.1], [3.0, 3.0, 2.4], **rota)

    legenda = [
        Line2D([], [], marker="s", ls="none", ms=8, mfc=ROXO_CLARO, mec=gc.ROXO,
               label="Mesa (8, 6 lugares cada; 48 no total)"),
        Line2D([], [], color=gc.ROXO, lw=1.4, ls=(0, (1.2, 1.6)), label="Rota acessível"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2,
              frameon=False, fontsize=dc.FONTE_PT - 0.4, handlelength=1.6,
              columnspacing=1.4)
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
