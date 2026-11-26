"""
Figura - Ciclo do caixa (seção 7.5).

O sócio-gerente opera o caixa, como o autor definiu (24/11/2026): abertura do
caixa e conferência das reservas; registro de cada grupo na chegada; fechamento
da comanda e emissão da NFC-e na saída, grupo a grupo; conferência no fechamento.
Diagrama sem dados, no padrão visual dos demais (diagramas_comum).
Saída: textos-tcc/figuras/7-4_fluxo_caixa.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "7-4_fluxo_caixa.png"


def main():
    fig, ax = dc.figura(6.3, 4.6, ymax=7.0)
    caixa, seta = dc.caixa, dc.seta
    x, w = 4.0, 7.2
    passos = [
        (0.45, "Abertura: o sócio-gerente abre o caixa e confere as reservas do dia no site", "inicio"),
        (1.6, "Chegada do grupo: confere a reserva ou registra a hora e o número de pessoas no sistema de mesas", "destaque_leve"),
        (2.75, "Durante o turno, o instrutor lança os pedidos na comanda da mesa", "apagado"),
        (3.9, "Saída do grupo: fecha a comanda, recebe e emite a NFC-e, com taxa de entrada e consumo discriminados", "destaque_leve"),
        (5.25, "Fechamento: confere o caixa com as NFC-e do dia e encerra o sistema de mesas", "destaque"),
    ]
    for i, (y, texto, tipo) in enumerate(passos):
        caixa(ax, x, y, w, 0.85, texto, tipo, largura=52)
        if i:
            seta(ax, [(x, passos[i - 1][0] + 0.425), (x, y - 0.425)])
    seta(ax, [(x + w / 2, 3.9), (9.2, 3.9), (9.2, 1.6), (x + w / 2, 1.6)], "Próximo\ngrupo", (9.2, 2.75))
    caixa(ax, 5.0, 6.45, 10, 0.6,
          "Os dados do caixa e do sistema de mesas alimentam o fluxo da gestão (Figura 13).", "nota")
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
