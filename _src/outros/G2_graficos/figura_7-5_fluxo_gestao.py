"""
Figura - Fluxo da gestão: dados, logística e gatilhos (seção 7.5).

Pedido do autor (24/11/2026): separar do caixa o lançamento dos dados no
sistema de indicadores, com o planejamento da logística do dia seguinte, a
compra de insumos e o monitoramento dos gatilhos do acervo (seção 7.6), da
etapa de equipe e de perda máxima (seção 10.4).
Diagrama sem dados, no padrão visual dos demais (diagramas_comum).
Saída: textos-tcc/figuras/7-5_fluxo_gestao.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-5_fluxo_gestao.png"


def main():
    fig, ax = dc.figura(6.3, 6.5, ymax=9.9)
    caixa, seta = dc.caixa, dc.seta
    x, w = 3.4, 6.0
    passos = [
        (0.45, "Depois do fechamento do caixa", "inicio"),
        (1.6, "Lança os dados do dia no sistema de indicadores", "destaque"),
        (2.75, "Planeja o dia seguinte: escala, reservas e pedido de hortifrúti", "destaque_leve"),
        (3.95, "Toda semana: compra os insumos pela ficha técnica e pela contagem do estoque", "destaque_leve"),
        (5.15, "Todo mês: apura os indicadores e o CMV e os compara com os gatilhos", "destaque"),
    ]
    for i, (y, texto, tipo) in enumerate(passos):
        caixa(ax, x, y, w, 0.85, texto, tipo, largura=44)
        if i:
            seta(ax, [(x, passos[i - 1][0] + 0.425), (x, y - 0.425)])
    caixa(ax, 8.45, 2.0, 2.9, 2.3,
          "Dados do dia:\ncirculação, pessoas por mesa, ocupação no pico, gasto por pessoa, permanência, "
          "jogos pedidos fora do acervo e sugestões", "pergunta", largura=20, tamanho=8.2)
    seta(ax, [(x + w / 2, 1.6), (7.0, 1.6)])
    caixa(ax, x, 6.45, w, 0.8, "Algum gatilho disparou?", "pergunta")
    seta(ax, [(x, 5.575), (x, 6.05)])
    caixa(ax, x, 7.85, w, 1.0,
          "Aciona a medida prevista: ampliação do acervo, etapa de equipe ou medida de perda máxima",
          "destaque_leve", largura=44)
    seta(ax, [(x, 6.85), (x, 7.35)], "Sim", (x, 7.1))
    caixa(ax, 8.45, 6.45, 2.9, 0.8, "Mantém a operação", "destaque_leve", largura=20)
    seta(ax, [(x + w / 2, 6.45), (7.0, 6.45)], "Não", (6.7, 6.2))
    caixa(ax, 5.0, 9.1, 10, 0.75,
          "Fora dos picos, o sócio-gerente cuida também dos fornecedores e da atualização do site.",
          "nota", largura=90)
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
