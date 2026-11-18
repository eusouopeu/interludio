"""
Figura 3.3 - Triagem final da população do Bloco B1.

Fluxograma (sem dados) da curadoria manual, como o autor a aplicou: o
candidato sai se o Google Maps o marca como "Permanentemente fechado"; depois,
a foto da estante com jogos de caixa completos e a foto de um jogo aberto ou
em uso bastam para a inclusão. Sem a foto da estante, o nome do
estabelecimento precisa remeter a jogos de mesa (sem termo de videogame); quando
falta uma das provas, a política ou a declaração explícita do estabelecimento
decide. Servir alimentos e bebidas não foi critério.
Saída: textos/figuras/3-3_triagem_populacao.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos" / "figuras" / "3-3_triagem_populacao.png"


def main():
    fig, ax = dc.figura(6.3, 6.9, ymax=9.0)
    caixa, seta = dc.caixa, dc.seta

    caixa(ax, 5.0, 0.5, 9.4, 0.8,
          "Candidato: estabelecimento do Google Maps numa das 15 metrópoles,\ncom mais de 100 avaliações",
          "inicio")
    caixa(ax, 4.3, 1.85, 5.6, 0.8,
          "O Google Maps o marca como\n\"Permanentemente fechado\"?", "pergunta")
    caixa(ax, 8.75, 1.85, 1.9, 0.7, "Eliminado", "apagado")
    seta(ax, [(4.3, 0.9), (4.3, 1.45)])
    seta(ax, [(7.1, 1.85), (7.8, 1.85)], "Sim", (7.45, 1.85))

    caixa(ax, 5.0, 3.35, 7.0, 0.9,
          "Há foto de uma estante com pelo menos dois jogos\nde caixa completos?", "pergunta")
    seta(ax, [(4.3, 2.25), (4.3, 2.9)], "Não", (4.3, 2.57))

    caixa(ax, 2.2, 5.0, 3.9, 1.2,
          "Há foto de pelo menos um jogo de caixa completo aberto sobre a mesa ou em uso?",
          "pergunta", largura=30)
    caixa(ax, 7.8, 5.0, 3.9, 1.2,
          "O nome remete a jogos de mesa, com termo ou trocadilho ligado a jogos e sem termo "
          "de videogame?", "pergunta", largura=31)
    seta(ax, [(2.2, 3.8), (2.2, 4.4)], "Sim", (2.2, 4.1))
    seta(ax, [(7.8, 3.8), (7.8, 4.4)], "Não", (7.8, 4.1))

    caixa(ax, 5.0, 6.65, 3.6, 1.4,
          "Há política ou declaração explícita, no site, no Instagram ou na bio, de jogos de "
          "cartas ou de tabuleiro para uso no local?", "pergunta", largura=31)
    seta(ax, [(4.15, 5.0), (4.4, 5.0), (4.4, 5.95)], "Não", (4.4, 5.45))
    seta(ax, [(5.85, 5.0), (5.6, 5.0), (5.6, 5.95)], "Sim", (5.6, 5.45))

    caixa(ax, 2.2, 8.5, 3.4, 0.8, "Incluído na população\n(63 luderias)", "destaque")
    caixa(ax, 7.8, 8.5, 3.4, 0.8, "Eliminado", "apagado")
    seta(ax, [(2.2, 5.6), (2.2, 8.1)], "Sim", (2.2, 6.65))
    seta(ax, [(7.8, 5.6), (7.8, 8.1)], "Não", (7.8, 6.65))
    seta(ax, [(3.2, 6.65), (3.0, 6.65), (3.0, 8.1)], "Sim", (3.0, 7.5))
    seta(ax, [(6.8, 6.65), (7.0, 6.65), (7.0, 8.1)], "Não", (7.0, 7.5))

    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
