"""
Figura - Subfluxo dos jogos: sugestão e explicação pelo instrutor (seção 7.5).

Em 24/11/2026 o autor separou o fluxo geral do atendimento (figura_7-2_fluxo_atendimento.py)
e deixou nesta figura só a indicação e a explicação dos jogos.

Só as tarefas do instrutor, como o autor as definiu (18/11/2026): recepção com
as regras da casa e o cardápio; sugestão de jogo pelo perfil, se o grupo
quiser; explicação das regras, se o grupo pedir; volta em 10 minutos se o grupo
pediu explicação e em 30 minutos se não pediu, com ou sem sugestão; sem clientes, estudo do
acervo. O registro no sistema de gestão de mesas fica com o sócio.
Diagrama sem dados, no padrão visual dos demais (diagramas_comum).
Saída: textos-tcc/figuras/7-2_fluxo_instrutor.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-2_fluxo_instrutor.png"


def main():
    fig, ax = dc.figura(6.3, 5.3, ymax=9.0)
    ax.set_ylim(9.0, 1.05)  # o topo antigo (chegada e recepção) passou à figura do atendimento
    caixa, seta = dc.caixa, dc.seta

    caixa(ax, 5.0, 1.55, 7.6, 0.8,
          "Grupo à mesa, depois da recepção", "inicio")
    caixa(ax, 3.0, 2.85, 4.4, 0.8, "O grupo quer sugestão\nde jogo?", "pergunta")
    seta(ax, [(3.0, 1.95), (3.0, 2.45)])
    caixa(ax, 7.8, 2.85, 3.8, 1.25,
          "Pergunta o perfil do grupo e sugere o jogo pelo site de recomendação", "destaque_leve", largura=27)
    seta(ax, [(5.2, 2.85), (5.9, 2.85)], "Sim", (5.55, 2.85))

    caixa(ax, 3.0, 4.45, 4.4, 0.8, "O grupo quer explicação\ndas regras?", "pergunta")
    seta(ax, [(3.0, 3.25), (3.0, 4.05)], "Não", (3.0, 3.55))
    seta(ax, [(7.8, 3.475), (7.8, 3.8), (3.0, 3.8)], ponta=False)

    caixa(ax, 3.0, 5.9, 4.4, 0.75, "Explica as regras à mesa", "destaque_leve")
    seta(ax, [(3.0, 4.85), (3.0, 5.52)], "Sim", (3.0, 5.15))
    caixa(ax, 3.0, 7.2, 4.4, 0.95,
          "Volta 10 minutos depois: confere se o grupo segue bem no jogo", "destaque", largura=34)
    seta(ax, [(3.0, 6.28), (3.0, 6.72)])

    caixa(ax, 7.8, 7.2, 3.8, 0.95,
          "Volta 30 minutos depois: pergunta se o grupo quer mais alguma coisa",
          "destaque", largura=28)
    seta(ax, [(5.2, 4.45), (7.8, 4.45), (7.8, 6.72)], "Não", (6.5, 4.45))

    caixa(ax, 5.0, 8.45, 9.6, 0.7,
          "Sem clientes na casa: o instrutor estuda os jogos do acervo, com a leitura das regras "
          "e vídeos tutoriais.", "nota")
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
