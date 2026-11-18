"""
Figura 7.2 - Fluxo do instrutor no atendimento ao grupo (seção 7.3).

Só as tarefas do instrutor, como o autor as definiu (18/11/2026): recepção com
as regras da casa e o cardápio; sugestão de jogo pelo perfil, se o grupo
quiser; explicação das regras, se o grupo pedir; volta em 10 minutos se o grupo
pediu explicação e em 30 minutos se não pediu, com ou sem sugestão; sem clientes, estudo do
acervo. O registro no sistema de gestão de mesas fica com o sócio.
Diagrama sem dados, no padrão visual dos demais (diagramas_comum).
Saída: textos/figuras/7-2_fluxo_instrutor.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos" / "figuras" / "7-2_fluxo_instrutor.png"


def main():
    fig, ax = dc.figura(6.3, 5.9, ymax=9.0)
    caixa, seta = dc.caixa, dc.seta

    caixa(ax, 5.0, 0.45, 7.6, 0.7,
          "Grupo chega, já registrado pelo sócio no sistema de gestão de mesas", "inicio")
    caixa(ax, 5.0, 1.55, 7.6, 0.8,
          "Recepção: o instrutor apresenta a casa, as regras da casa\ne onde fica o cardápio",
          "destaque_leve")
    seta(ax, [(5.0, 0.8), (5.0, 1.15)])

    caixa(ax, 3.0, 2.85, 4.4, 0.8, "O grupo quer sugestão\nde jogo?", "pergunta")
    seta(ax, [(3.0, 1.95), (3.0, 2.45)])
    caixa(ax, 7.8, 2.85, 3.8, 1.0,
          "Pergunta o perfil do grupo e sugere o jogo", "destaque_leve", largura=24)
    seta(ax, [(5.2, 2.85), (5.9, 2.85)], "Sim", (5.55, 2.85))

    caixa(ax, 3.0, 4.45, 4.4, 0.8, "O grupo quer explicação\ndas regras?", "pergunta")
    seta(ax, [(3.0, 3.25), (3.0, 4.05)], "Não", (3.0, 3.55))
    seta(ax, [(7.8, 3.35), (7.8, 3.8), (3.0, 3.8)], ponta=False)

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
