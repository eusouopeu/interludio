"""
Bloco B2 - pictogramas do que o público escreve nas avaliações do Google
(análise de conteúdo de Bardin na grade de 22 temas, avaliações com texto até
"3 meses atrás").

Três figuras, todas em "de cada N avaliações com texto":
- temas: quantas falam de cada tema, em qualquer tom (1 ícone = 5 em 100);
- reclamações: quantas trazem o tema como crítica (1 ícone = 1 em 100);
- ocasião: com quem e para que o público vai (amigos, família, aniversário,
  casal), em grade de 100 ícones (1 ícone = 1 avaliação em 100).

Entradas (saídas do B2a_temas_grade2.py, em dados-agregados/B2_avaliacoes/analise_conteudo/):
  B2_temas_frequencia.csv      comentários e % por tema, com elogio e crítica
  B2_temas_contexto.csv        ocasião e outros contextos declarados
  B2_temas_estabelecimentos.csv  comentários por casa (n e número de casas)

Estilo editorial (`graficos_comum`): temas e ocasiões em cinza, reclamações
em vermelho; o título diz o tema que lidera.

Regras:
- o percentual desenhado é o simples (comentários com o tema ÷ avaliações com
  texto), o mesmo do texto (Gráfico 4 e Apêndice F); grade de 22 temas desde
  16/11/2026 (o livro de 15/10, das tabelas B2_bardin_*, saiu de uso);
- um comentário pode cair em vários temas (contagem não exclusiva por
  desenho), então as linhas não somam 100%; por isso não há total como soma.
- o total de avaliações é a soma da tabela por estabelecimento (cada
  avaliação em uma só casa) e é conferido contra o B2 (1.628).

Saídas (dados-agregados/B2_avaliacoes/graficos/): png/ (300 dpi), svg/ (texto
editável) e valores/ (B2_pict_*). Para atualizar depois de refazer a
codificação, rodar o B2a_temas_grade2.py e depois este script.

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/3_analise/B2a_pictogramas.py"
"""
# Caminhos: _src/extras/ (log e padrão visual); log em ../logs/
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import pandas as pd  # noqa: E402

from graficos_comum import (APAGADO, BASE, HALO, TINTA, TINTA2, VERMELHO, br, figura, margens,  # noqa: E402
                            pessoa, pictograma_linhas, salvar)

ROOT = _AQUI.parents[4]
B2 = ROOT / "dados-agregados" / "B2_avaliacoes"
AC = B2 / "analise_conteudo"
PASTA = B2 / "graficos"
FONTE = ("Fonte: elaboração própria com avaliações com texto do Google Maps até \"3 meses atrás\" "
         "(coletadas de 9 a 30/10/2026), codificadas por análise de conteúdo (Bardin) em 22 temas (B2).")
TOTAL_B2 = 1628


def milhar(v):
    return f"{v:,}".replace(",", ".")


OCASIOES = {"amigos": "Ocasião: amigos", "família": "Ocasião: família", "aniversário": "Ocasião: aniversário",
            "casal": "Ocasião: casal"}


def ler():
    """Lê as tabelas da grade de 22 temas e confere o total de avaliações."""
    est = pd.read_csv(AC / "B2_temas_estabelecimentos.csv", sep=";", encoding="utf-8-sig")
    n, casas = int(est.comentarios.sum()), len(est)
    assert n == TOTAL_B2, f"tabela por estabelecimento soma {n}, não {TOTAL_B2}"
    f = pd.read_csv(AC / "B2_temas_frequencia.csv", sep=";", encoding="utf-8-sig")
    rot = f.tema.str[0].str.upper() + f.tema.str[1:]
    q = pd.DataFrame({"categoria": rot, "avaliacoes": f.comentarios_com_tema, "pct": f.pct_com_tema})
    neg = pd.DataFrame({"categoria": rot, "avaliacoes": f.comentarios_critica, "pct": f.pct_critica})
    for t in (q, neg):  # o % publicado confere com a contagem
        assert ((100 * t.avaliacoes / n - t.pct).abs() <= 0.051).all(), "percentual difere da contagem"
    c = pd.read_csv(AC / "B2_temas_contexto.csv", sep=";", encoding="utf-8-sig")
    c = c[c.contexto.isin(OCASIOES)]
    ctx = pd.DataFrame({"categoria": c.contexto.map(OCASIOES), "avaliacoes": c.comentarios, "pct": c.pct_comentarios})
    print(f"  {n} avaliações de {casas} casas; percentuais conferem com as contagens")
    return n, casas, q, neg, ctx


def tabela_valores(tab, n):
    return tab[["categoria", "avaliacoes", "pct"]].rename(columns={"pct": "pct_avaliacoes"}).assign(n_avaliacoes=n)


def proporcao(pct):
    """Fração por extenso para o título (ex.: 56% -> "mais da metade")."""
    if pct > 50:
        return "mais da metade"
    if 30 <= pct < 36:
        return "cerca de um terço"
    return f"{br(pct, 0)}%"


def linhas_icones(tab, titulo, subtitulo, por_icone, total_icones, cor, nome, n, casas, nota):
    tab = tab.sort_values("pct", ascending=False).reset_index(drop=True)
    linhas = [{"rotulo": r.categoria, "icones": r.pct / por_icone, "valor": f"{br(r.pct, 1)}%",
               "extra": f"{r.avaliacoes} aval.", "cor": cor} for r in tab.itertuples()]
    fig, _ = pictograma_linhas(linhas, total_icones, "pessoa", titulo, subtitulo, FONTE,
                               nota=f"{nota} n = {milhar(n)} avaliações de {casas} casas.", esq=2.9)
    salvar(fig, PASTA, nome, tabela_valores(tab, n))


def grade_100(tab, titulo, subtitulo, nome, n, casas, nota):
    """Uma grade de 10 x 10 por categoria (1 pessoa = 1 em cada 100 avaliações)."""
    k, cols = len(tab), 4
    lin = (k + cols - 1) // cols
    lado, gap, rot, entre = 2.0, 0.45, 0.7, 0.3  # polegadas: grade, espaço lateral, rótulo acima, entre fileiras
    largura = 0.25 + cols * lado + (cols - 1) * gap + 0.25
    cab, rod = margens(largura, titulo, subtitulo, FONTE, nota=nota)
    altura = cab + lin * (lado + rot) + (lin - 1) * entre + rod
    fig, ax0 = figura(largura, altura, titulo, subtitulo, FONTE, nota=nota)
    ax0.remove()
    for i, r in enumerate(tab.itertuples()):
        c, li = i % cols, i // cols
        x0 = 0.18 + c * (lado + gap)
        y0 = rod + (lin - 1 - li) * (lado + rot + entre)
        ax = fig.add_axes([x0 / largura, y0 / altura, lado / largura, lado / altura])
        cheios = round(r.pct)  # 1 ícone = 1 em 100, arredondado
        for j in range(100):
            pessoa(ax, j % 10, 9 - j // 10, BASE if j < cheios else APAGADO, s=0.9)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_axis_off()
        ax.text(0.05, 10.3, f"{br(r.pct, 0)}%", fontsize=16, fontweight="semibold", color=TINTA, va="bottom")
        rotulo = r.categoria.replace("Ocasião: ", "")
        ax.text(0.05, 12.0, rotulo[0].upper() + rotulo[1:], fontsize=10.5, color=TINTA2, va="bottom",
                path_effects=HALO)
    salvar(fig, PASTA, nome, tabela_valores(tab, n))


def main():
    n, casas, q, neg, ctx = ler()
    top = q.sort_values("pct", ascending=False).iloc[0]
    linhas_icones(q, f"{top.categoria} aparece em {proporcao(top.pct)} das avaliações com texto",
                  "Temas citados, em qualquer tom, de cada 20 avaliações com texto.", 5, 20, BASE,
                  "B2_pict_temas", n, casas,
                  "Cada pessoa = 5% das avaliações. Uma avaliação pode tratar de vários temas: as linhas não "
                  "somam 100%.")
    neg = neg[neg.avaliacoes >= 5]
    pior = neg.sort_values("pct", ascending=False).iloc[0]
    linhas_icones(neg, f"A reclamação mais comum é sobre {pior.categoria.lower()}: "
                       f"{br(pior.pct, 0)} de cada 100 avaliações",
                  "Avaliações que citam o tema como crítica, de cada 100 avaliações com texto.", 1, 10,
                  VERMELHO, "B2_pict_reclamacoes", n, casas,
                  "Cada pessoa = 1% das avaliações. Só as críticas; temas com menos de 5 reclamações ficam de fora.")
    ctx = ctx.sort_values("pct", ascending=False)
    primeira = ctx.iloc[0]
    grade_100(ctx, f"Ir com {primeira.categoria.split(': ')[1]} é a ocasião mais declarada: "
                   f"{br(primeira.pct, 0)} de cada 100 avaliações",
              "Com quem e por que o público vai, de cada 100 avaliações com texto.", "B2_pict_ocasiao_perfil",
              n, casas,
              "Cada pessoa = 1 avaliação em 100. A ocasião só conta quando a avaliação a declara; "
              f"o resto não é \"não\", é \"não dito\". n = {milhar(n)} avaliações de {casas} casas.")


if __name__ == "__main__":
    main()
