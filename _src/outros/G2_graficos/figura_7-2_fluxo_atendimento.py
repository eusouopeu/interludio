"""
Figura - Fluxo do atendimento ao grupo (seção 7.5).

Fluxo geral do salão, como o autor o pediu (24/11/2026): chegada e registro pelo
sócio-gerente, recepção pelo instrutor, subfluxo dos jogos, anotação e entrega
dos pedidos, limpeza da mesa depois do consumo, fechamento da comanda no caixa
e conferência das peças depois da saída do grupo. O detalhe da sugestão e da
explicação dos jogos fica na figura do subfluxo (figura_7-2_fluxo_instrutor.py).
Diagrama sem dados, no padrão visual dos demais (diagramas_comum).
Saída: textos-tcc/figuras/7-2_fluxo_atendimento.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-2_fluxo_atendimento.png"


def main():
    fig, ax = dc.figura(6.3, 6.6, ymax=10.0)
    caixa, seta = dc.caixa, dc.seta
    x, w = 4.0, 7.2
    passos = [
        (0.45, "Grupo chega: o sócio-gerente confere a reserva ou registra o grupo no sistema de mesas", "inicio"),
        (1.6, "Recepção: o instrutor apresenta a casa, as regras da casa e o cardápio", "destaque_leve"),
        (2.75, "Subfluxo dos jogos: sugestão e explicação, se o grupo pedir", "destaque"),
        (3.9, "O instrutor anota os pedidos na comanda da mesa e os passa à cozinha", "destaque_leve"),
        (5.05, "O instrutor entrega os pedidos à mesa", "destaque_leve"),
        (6.2, "Depois do consumo, o instrutor recolhe a louça e limpa a mesa", "destaque_leve"),
        (7.45, "Fim do turno de 3 horas: o grupo fecha a comanda no caixa com o sócio-gerente", "inicio"),
        (8.6, "Depois da saída, o instrutor confere as peças dos jogos usados e prepara a mesa", "destaque"),
    ]
    for i, (y, texto, tipo) in enumerate(passos):
        caixa(ax, x, y, w, 0.78, texto, tipo, largura=52)
        if i:
            seta(ax, [(x, passos[i - 1][0] + 0.39), (x, y - 0.39)])
    # novo pedido durante o turno
    seta(ax, [(x + w / 2, 6.2), (9.2, 6.2), (9.2, 3.9), (x + w / 2, 3.9)], "Novo\npedido", (9.2, 5.05))
    caixa(ax, 5.0, 9.55, 10, 0.55,
          "O grupo pode pedir outro jogo a qualquer momento, e o subfluxo dos jogos recomeça.", "nota")
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
