"""
Bloco B1 - Figuras 5.5 e 5.6: distribuição das luderias por número de seguidores e por
número de publicações (posts) no Instagram.

Dois histogramas iguais: faixas de largura fixa até um corte e uma última barra "mais de
<corte>" (largura diferente, hachurada), com a mediana e a São Jogue (Salvador) marcadas.
Cada casa conta em uma única faixa (place_id) e a soma das faixas, com a última barra, é
conferida contra o total de casas com perfil coletado (diferença zero).

Entrada: dados-agregados/B1_redes_sociais/B1_instagram_resumo.csv (coletas de 12 e
16/11/2026; as 61 casas com perfil, todas na população do B1), com o nome da casa de
dados-agregados/B1_estabelecimentos/B1_resumo_estabelecimentos.xlsx.
Saídas: textos-tcc/graficos/5-5_seguidores_instagram.png e 5-6_posts_instagram.png (estilo dos
gráficos dos capítulos, `planilha_estilo`: slate-400 nas barras, purple-700 para Salvador) e
os valores desenhados em dados-agregados/B1_estabelecimentos/5_graficos/graficos/valores/.
"Posts" é o total de publicações do perfil na coleta (`n_posts_total`), não o do período.

Uso:
    python3 "_src/pyScripts/B1_Estabelecimentos/3_analise/B1a_instagram_histogramas.py"
"""
# Caminhos: _src/outros/G*/ (log comum e estilo dos gráficos); log em ../4_logs/
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import planilha_estilo as est  # noqa: E402

ROOT = _AQUI.parents[4]
IG = ROOT / "dados-agregados" / "B1_redes_sociais" / "B1_instagram_resumo.csv"
B1 = ROOT / "dados-agregados" / "B1_estabelecimentos" / "B1_resumo_estabelecimentos.xlsx"
GRAFICOS = ROOT / "textos-tcc" / "graficos"
VALORES = ROOT / "dados-agregados" / "B1_estabelecimentos" / "5_graficos" / "graficos" / "valores"


def mil(v):
    return "0" if v == 0 else f"{v // 1000} mil"


def inteiro(v):
    return est.br(v, 0)


def histograma(valores, sj, largura, corte, passo_tick, fmt_tick, xlabel, saida, csv):
    s = np.asarray(valores, dtype=float)
    mediana = float(np.median(s))
    bordas = np.arange(0, corte + largura, largura)
    cont, _ = np.histogram(s[s < corte], bins=bordas)
    acima = s[s >= corte]
    assert cont.sum() + len(acima) == len(s), "faixas não somam o total de casas"
    print(f"\n{saida}: {len(s)} casas; mediana {mediana:,.0f}; São Jogue {sj:,.0f}")
    print(f"  faixas de {largura:,} até {corte:,}: {cont.tolist()} | acima: {len(acima)} "
          f"({acima.min():,.0f} a {acima.max():,.0f}) | soma = {cont.sum() + len(acima)} = total")

    x_acima = corte + 2 * largura  # a última barra fica separada por uma folga, por ter outra largura
    topo = max(cont.max(), len(acima))
    fig, ax = plt.subplots(figsize=(8, 4.4))
    faixa_sj = int(sj // largura)
    sozinha = cont[faixa_sj] == 1  # com a São Jogue sozinha na faixa, a barra inteira vai em roxo
    cores = [est.ROXO_700 if (sozinha and i == faixa_sj) else est.SLATE_400 for i in range(len(cont))]
    ax.bar(bordas[:-1], cont, width=largura, align="edge", color=cores, edgecolor="white", linewidth=1.2, zorder=3)
    ax.bar(x_acima, len(acima), width=largura, align="edge", color=est.SLATE_400, edgecolor="white",
           linewidth=1.2, hatch="////", zorder=3)
    for x, n in list(zip(bordas[:-1], cont)) + [(x_acima, len(acima))]:
        ax.text(x + largura / 2, n + topo * 0.015, str(n), ha="center", va="bottom", fontsize=9.5,
                fontweight="bold", color=est.ROXO_700 if (sozinha and x == bordas[faixa_sj]) else est.SLATE_700)
    ax.axvline(mediana, color=est.SLATE_600, lw=1.0, ls=(0, (4, 3)), zorder=4)
    ax.text(mediana + largura * 0.25, topo * 1.06, f"mediana: {est.br(mediana, 0)}", fontsize=9.5,
            fontweight="bold", color=est.SLATE_600, va="center", ha="left")
    # São Jogue: leitura em roxo; se a faixa tem outras casas, um traço roxo marca a posição exata
    topo_faixa = cont[faixa_sj]
    if not sozinha:
        ax.plot([sj, sj], [0, topo_faixa], color=est.ROXO_700, lw=2.2, zorder=5, solid_capstyle="butt")
    ax.annotate(f"São Jogue: {est.br(sj, 0)}", xy=(sj, topo_faixa + topo * 0.09),
                xytext=(sj + largura * 0.8, topo * 0.62), fontsize=9.5, fontweight="bold", color=est.ROXO_700,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=est.ROXO_700, lw=1.0, shrinkA=2, shrinkB=2), zorder=6)
    ax.set_xlim(0, x_acima + largura + largura * 0.3)
    ax.set_ylim(0, topo * 1.16)
    ticks = list(range(0, corte + 1, passo_tick)) + [x_acima + largura / 2]
    ax.set_xticks(ticks, [fmt_tick(b) for b in ticks[:-1]] + [f"mais de\n{fmt_tick(corte)}"])
    ax.set_xlabel(xlabel, fontsize=10.5, color=est.SLATE_700, labelpad=8)
    ax.set_ylabel("Luderias", fontsize=10.5, color=est.SLATE_700, labelpad=8)
    est._estilo_eixo(ax, "y")
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color("#334155")
    ax.tick_params(axis="x", labelsize=9.5, colors="#334155")
    ax.tick_params(axis="y", labelsize=9.5)
    est.GRAF = GRAFICOS
    caminho = est._salvar(fig, saida)

    VALORES.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"de": [*bordas[:-1], corte], "ate": [*bordas[1:], int(s.max())],
                  "luderias": [*cont, len(acima)]}).to_csv(VALORES / f"{csv}.csv", sep=";", index=False,
                                                           encoding="utf-8-sig")
    print(f"  OK: {caminho.relative_to(ROOT)}")


def main():
    ig = pd.read_csv(IG, sep=";", encoding="utf-8-sig")
    pop = set(pd.read_excel(B1, sheet_name="estabelecimentos").place_id)
    assert set(ig.place_id) <= pop, "perfil de casa fora da população do B1"
    ig = ig.dropna(subset=["seguidores", "n_posts_total"])
    assert ig.place_id.is_unique
    sj = ig[ig.estabelecimento.str.contains("São Jogue")].iloc[0]
    histograma(ig.seguidores, sj.seguidores, 5_000, 50_000, 10_000, mil, "Seguidores no Instagram",
               "5-5_seguidores_instagram", "B1_seguidores_histograma")
    histograma(ig.n_posts_total, sj.n_posts_total, 250, 2_500, 500, inteiro, "Publicações no perfil do Instagram",
               "5-6_posts_instagram", "B1_posts_histograma")


if __name__ == "__main__":
    main()
