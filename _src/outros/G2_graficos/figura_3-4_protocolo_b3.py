"""
Figura 3.4 - Protocolo da contagem direta (Bloco B3).

Mostra o que é registrado na porta, nas mesas e na NFC-e, as medidas que
saem de cada registro e como a lei de Little (L = λ × W) junta circulação e
permanência para dimensionar o salão. Diagrama sem dados.
Saída: textos-tcc/figuras/3-4_protocolo_b3.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagramas_comum as dc  # noqa: E402

SAIDA = ROOT / "textos-tcc" / "figuras" / "3-4_protocolo_b3.png"


def main():
    fig, ax = dc.figura(6.3, 5.2, ymax=7.35)
    caixa, seta = dc.caixa, dc.seta
    xs, w = [1.7, 5.0, 8.3], 3.1

    caixa(ax, 5.0, 0.45, 9.7, 0.7,
          "Visita: observador sentado a uma mesa como cliente, sem interagir; "
          "essa mesa sai dos registros e do denominador", "inicio", largura=95)

    y1, h1 = 1.9, 1.1
    registros = [
        "Porta\nentrada de cada grupo e número de pessoas",
        "Mesas\nentrada e saída de cada grupo, pessoas, jogos e chamadas ao instrutor",
        "NFC-e\nnumeração da nota do autor em cada visita à mesma unidade",
    ]
    for x, texto in zip(xs, registros):
        seta(ax, [(x, 0.8), (x, y1 - h1 / 2)])
        caixa(ax, x, y1, w, h1, texto, "pergunta", largura=31)

    y2, h2 = 3.55, 1.2
    medidas = [
        "Circulação (λ)\npessoas que entram ÷ horas observadas",
        "Grupo, permanência (W) e ocupação\nmesas ocupadas minuto a minuto ÷ 10 "
        "(Bela Vista) ou 9 (Paralela)",
        "Notas emitidas entre as visitas\npiso das vendas, não contagem de clientes",
    ]
    for x, texto in zip(xs, medidas):
        seta(ax, [(x, y1 + h1 / 2), (x, y2 - h2 / 2)])
        caixa(ax, x, y2, w, h2, texto, "destaque_leve", largura=32)

    y3, h3 = 5.1, 0.85
    xl, wl = (xs[0] + xs[1]) / 2, xs[1] - xs[0] + w
    for x in xs[:2]:
        seta(ax, [(x, y2 + h2 / 2), (x, y3 - h3 / 2)])
    caixa(ax, xl, y3, wl, h3, "Lei de Little: L = λ × W\npessoas no salão ao mesmo tempo",
          "destaque")
    seta(ax, [(xs[2], y2 + h2 / 2), (xs[2], y3 - h3 / 2)])
    caixa(ax, xs[2], y3, w, h3, "Cenário pessimista da circulação", "pergunta", largura=30)

    y4, h4 = 6.65, 0.85
    seta(ax, [(xl, y3 + h3 / 2), (xl, y4 - h4 / 2)])
    seta(ax, [(xs[2], y3 + h3 / 2), (xs[2], y4 - h4 / 2)])
    caixa(ax, 5.0, y4, 9.7, h4,
          "Número de mesas e equipe (cap. 7) e pessoas por mês no modelo financeiro (seção 9.1); "
          "o índice de horários de pico do Google Maps leva a circulação às demais horas",
          "nota", largura=95)
    dc.salvar(fig, SAIDA, ROOT)


if __name__ == "__main__":
    main()
