"""
Peças comuns dos diagramas (fluxogramas, árvores e esquemas) do TCC.

Caixas arredondadas e setas em ângulo reto, no padrão visual dos gráficos
(graficos_comum: fonte Source Sans 3, cinzas e o roxo purple-700 como
destaque). Coordenadas em unidades do eixo; o eixo y cresce para baixo
(ax.set_ylim(altura, 0)).
"""

import textwrap

import graficos_comum as gc
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FONTE_PT = 8.6

ESTILOS = {
    "inicio": dict(fc="white", ec=gc.BASE, lw=1.1, cor=gc.TINTA, peso="semibold"),
    "pergunta": dict(fc="white", ec=gc.MEDIO, lw=0.9, cor=gc.TINTA, peso="normal"),
    "nota": dict(fc="#f5f5f5", ec="#f5f5f5", lw=0.9, cor=gc.TINTA2, peso="normal"),
    "destaque": dict(fc=gc.ROXO, ec=gc.ROXO, lw=0.9, cor="white", peso="semibold"),
    "destaque_leve": dict(fc="#f3e8ff", ec=gc.ROXO, lw=0.9, cor=gc.TINTA, peso="normal"),
    "apagado": dict(fc=gc.APAGADO, ec=gc.CLARO, lw=0.9, cor=gc.TINTA2, peso="semibold"),
}


def figura(largura=6.3, altura=7.6, xmax=10, ymax=10):
    """Figura sem eixos, com y crescendo para baixo."""
    fig, ax = plt.subplots(figsize=(largura, altura))
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymax, 0)
    ax.axis("off")
    return fig, ax


def caixa(ax, x, y, w, h, texto, tipo="pergunta", largura=None, tamanho=None, peso=None):
    """Caixa centrada em (x, y); `largura` quebra o texto em linhas desse tamanho."""
    e = ESTILOS[tipo]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.12",
                                fc=e["fc"], ec=e["ec"], lw=e["lw"], zorder=2))
    if largura:
        texto = "\n".join(textwrap.fill(p, largura) for p in texto.split("\n"))
    ax.text(x, y, texto, ha="center", va="center", fontsize=tamanho or FONTE_PT, color=e["cor"],
            fontweight=peso or e["peso"], linespacing=1.15, zorder=3)


def seta(ax, pontos, rotulo=None, pos_rotulo=None, ponta=True):
    """Linha por uma lista de pontos (cotovelos em ângulo reto), com ponta no fim."""
    xs, ys = zip(*pontos)
    ax.plot(xs, ys, color=gc.TINTA3, lw=1.0, zorder=1, solid_capstyle="butt")
    if ponta:
        ax.annotate("", xy=pontos[-1], xytext=pontos[-2],
                    arrowprops=dict(arrowstyle="-|>", color=gc.TINTA3, lw=1.0,
                                    shrinkA=0, shrinkB=0, mutation_scale=9), zorder=1)
    if rotulo:
        rx, ry = pos_rotulo
        ax.text(rx, ry, rotulo, ha="center", va="center", fontsize=FONTE_PT - 0.4,
                color=gc.TINTA2, fontstyle="italic",
                bbox=dict(fc="white", ec="none", pad=1.2), zorder=4)


def salvar(fig, caminho, raiz):
    fig.tight_layout(pad=0.2)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=300, facecolor="white")
    print(f"gravado: {caminho.relative_to(raiz)}")
