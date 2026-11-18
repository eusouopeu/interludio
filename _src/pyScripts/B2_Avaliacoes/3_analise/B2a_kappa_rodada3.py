"""
Bloco B2 - concordância da rodada 3 da recodificação cega (coleta de 16/11/2026).

Compara a recodificação cega do autor (banco "3b - Recodificação 16/11" do Notion,
100 comentários sorteados por B2b_amostra_recodificacao.py) com a codificação do
Claude (B2b_codificacao_16_11.py), pelo id_avaliacao.

Mesmo método das rodadas 1 e 2 (B2a_temas_grade2.py):
  - temas: kappa de Cohen agrupado, unidade = comentário x tema x polaridade
    (presença/ausência), sobre os temas marcados por ao menos um codificador;
  - contexto: kappa agrupado, unidade = comentário x contexto;
  - "costuma ir" e "voltará": kappa nominal, vazio = "não foi dito";
  - critério de aceitação: kappa >= 0,70.
Acrescenta, para o fechamento da análise de conteúdo:
  - kappa e alfa de Krippendorff (nominal) dos temas também sobre a grade inteira
    (22 temas x 2 polaridades), que não depende de quais temas foram marcados;
  - kappa por polaridade, por estrato da amostra e por tema (com acordos e
    discordâncias, para localizar os temas que puxam o kappa para baixo);
  - índices de Jaccard (marcas em comum / marcas da união) e concordância exata
    por comentário;
  - intervalo de confiança de 95% do kappa agrupado dos temas por bootstrap de
    comentários (2.000 reamostras, semente 20261116).

Entradas (fora do git: têm texto):
  dados-brutos/B2_avaliacoes/analise_conteudo/recodificacao_rodada3/3ba-recodificacao-3.csv
      exportação crua do banco 3b feita pelo autor no Notion (arquivo "_all"), lida sem
      transcrição: o código do autor entra no cálculo como saiu do Notion
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_comentarios_codificados.csv
Sem a exportação, o script usa B2_recodificacao_rodada3.csv já gravado. Com ela, regrava esse
arquivo e informa quantos códigos do autor diferem da versão gravada antes.
Saídas (em dados-agregados/B2_avaliacoes/analise_conteudo/):
  B2_recodificacao_rodada3.csv
  B2_recodificacao_kappa_rodada3.csv        kappa por variável (formato das rodadas 1 e 2)
  B2_recodificacao_kappa_rodada3_temas.csv  acordos, discordâncias e kappa por tema e polaridade

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/3_analise/B2a_kappa_rodada3.py" [--autor exportacao_3b.csv]
"""
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import argparse  # noqa: E402
import collections  # noqa: E402
import random  # noqa: E402
import re  # noqa: E402

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
PASTA = ROOT / "dados-agregados" / "B2_avaliacoes" / "analise_conteudo"
RODADA3 = PASTA / "B2_recodificacao_rodada3.csv"
CODIFICADOS = ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo" / "2026-11-16_comentarios_codificados.csv"
AUTOR_NOTION = (ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo" / "recodificacao_rodada3"
                / "3ba-recodificacao-3.csv")
CRITERIO_KAPPA = 0.70
SEMENTE, N_BOOT = 20261116, 2000
GRADE = [
    "ambiente e decoração", "atendimento online", "atendimento presencial", "bebidas", "comemorações e grupos",
    "comida", "conforto e barulho", "curadoria e conservação do acervo", "espaço e lotação",
    "eventos e comunidade", "explicação de jogos", "indicações de jogos", "limpeza", "localização e acesso",
    "porções", "preço da entrada", "preço do cardápio", "preço de outros itens", "rapidez do serviço",
    "regras da casa", "variedade do acervo", "variedade do cardápio",
]


def sp(v):
    """Itens separados por "|" (rodadas e Notion) ou ";" (base do Claude)."""
    return {x.strip() for x in re.split(r"[|;]", str(v)) if x.strip()} if pd.notna(v) else set()


def nd(v):
    return v if pd.notna(v) and str(v).strip() else "não foi dito"


def kappa(pares):
    n = len(pares)
    if not n:
        return float("nan"), float("nan")
    po = sum(a == b for a, b in pares) / n
    ca, cb = collections.Counter(a for a, _ in pares), collections.Counter(b for _, b in pares)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return ((po - pe) / (1 - pe) if pe < 1 else float("nan")), po


def alfa_krippendorff(pares):
    """Alfa nominal para dois codificadores sem dados faltantes."""
    valores = [v for p in pares for v in p]
    n = len(valores)
    freq = collections.Counter(valores)
    do = sum(a != b for a, b in pares) * 2 / n
    de = sum(freq[x] * freq[y] for x in freq for y in freq if x != y) / (n * (n - 1))
    return 1 - do / de if de else float("nan")


def ler_autor(autor_csv):
    """Lê a recodificação do autor: a exportação crua do banco 3b do Notion (vírgula como
    separador de colunas e de itens) ou o formato ordem;id_avaliacao;autor_...
    Imprime a identidade do arquivo lido (caminho, data, tamanho, SHA-256), para conferir
    que é o mesmo exportado pelo autor (comparar com `shasum -a 256 <arquivo>`)."""
    import datetime
    import hashlib
    p = Path(autor_csv).resolve()
    print("ARQUIVO DO AUTOR LIDO PELO SCRIPT")
    print(f"  caminho:    {p}")
    print(f"  modificado: {datetime.datetime.fromtimestamp(p.stat().st_mtime):%d/%m/%Y %H:%M}")
    print(f"  tamanho:    {p.stat().st_size} bytes")
    print(f"  SHA-256:    {hashlib.sha256(p.read_bytes()).hexdigest()}\n")
    a = pd.read_csv(autor_csv, sep=None, engine="python", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if "Itens positivos" not in a:
        return a
    assert (a["Lido"] == "Yes").all(), "há comentário do 3b não marcado como lido"
    return pd.DataFrame({
        "ordem": a["Ordem"], "id_avaliacao": a["id_avaliacao"],
        "autor_positivos": a["Itens positivos"].str.replace(",", "|"),
        "autor_negativos": a["Itens negativos"].str.replace(",", "|"),
        "autor_contexto": a["Contexto"].str.replace(",", "|"),
        "autor_costuma_ir": a["Costuma ir"], "autor_voltara": a["Voltará"],
    })


def montar_rodada3(autor_csv):
    a = ler_autor(autor_csv)
    c = pd.read_csv(CODIFICADOS, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    c = c[c["amostra"] == "recodificação"]
    m = a.merge(c[["id_avaliacao", "estrato", "nota_avaliacao", "itens_positivos", "itens_negativos",
                   "contexto", "costuma_ir", "voltara"]], on="id_avaliacao", how="inner", validate="one_to_one")
    assert len(m) == len(a) == len(c) == 100, (len(m), len(a), len(c))
    norm = lambda v: " | ".join(sorted(sp(v)))
    r = pd.DataFrame({
        "n_amostra": m["ordem"].astype(int), "id_avaliacao": m["id_avaliacao"], "estrato": m["estrato"],
        "nota_avaliacao": m["nota_avaliacao"],
        "autor_positivos": m["autor_positivos"].map(norm), "autor_negativos": m["autor_negativos"].map(norm),
        "autor_contexto": m["autor_contexto"].map(norm), "autor_costuma_ir": m["autor_costuma_ir"].map(nd),
        "autor_voltara": m["autor_voltara"].map(nd),
        "claude_positivos": m["itens_positivos"].map(norm), "claude_negativos": m["itens_negativos"].map(norm),
        "claude_contexto": m["contexto"].map(norm), "claude_costuma_ir": m["costuma_ir"].map(nd),
        "claude_voltara": m["voltara"].map(nd),
    }).sort_values("n_amostra")
    fora = set().union(*[sp(v) for col in ("autor_positivos", "autor_negativos", "claude_positivos",
                                           "claude_negativos") for v in r[col]]) - set(GRADE)
    assert not fora, f"temas fora da grade: {fora}"
    r.to_csv(RODADA3, sep=";", index=False, encoding="utf-8-sig")
    return r


def pares_temas(r, temas, polos=("positivos", "negativos")):
    pares = []
    for pol in polos:
        for a, c in zip(r[f"autor_{pol}"].map(sp), r[f"claude_{pol}"].map(sp)):
            pares += [(t in a, t in c) for t in temas]
    return pares


def temas_marcados(r):
    return sorted(set().union(*[sp(v) for col in ("autor_positivos", "autor_negativos", "claude_positivos",
                                                  "claude_negativos") for v in r[col]]))


def kappa_temas(r, grade=False):
    return kappa(pares_temas(r, GRADE if grade else temas_marcados(r)))


def marcas(r, pol_cols):
    ma = sum(len(sp(v)) for col in pol_cols for v in r[f"autor_{col}"])
    mc = sum(len(sp(v)) for col in pol_cols for v in r[f"claude_{col}"])
    mm = sum(len(sp(a) & sp(c)) for col in pol_cols for a, c in zip(r[f"autor_{col}"], r[f"claude_{col}"]))
    return ma, mc, mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--autor", default=AUTOR_NOTION,
                    help="recodificação do autor (padrão: a exportação crua do banco 3b do Notion)")
    args = ap.parse_args()
    anterior = (pd.read_csv(RODADA3, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
                if RODADA3.exists() else None)
    if Path(args.autor).exists():
        r = montar_rodada3(args.autor)
        if anterior is not None:  # o que mudou no lado do autor em relação à versão gravada
            cols = [c for c in r.columns if c.startswith("autor_")]
            a = anterior.set_index("id_avaliacao")[cols].sort_index()
            b = r.set_index("id_avaliacao")[cols].sort_index()
            dif = (a != b).any(axis=1)
            print(f"autor: {int(dif.sum())} de {len(b)} comentários diferentes da versão gravada antes"
                  + (f" ({', '.join(dif[dif].index)})" if dif.any() else ""))
    else:
        r = anterior
    n = len(r)

    lin = []
    def add(variavel, k, po=None, ma=None, mc=None, mm=None, linhas=n, alfa=None, ic=None):
        lin.append({"rodada": 3, "variavel": variavel, "linhas": linhas, "kappa": round(k, 2),
                    "ic95": ic, "alfa_krippendorff": None if alfa is None else round(alfa, 2),
                    "concordancia_pct": None if po is None else round(100 * po, 1),
                    "marcas_autor": ma, "marcas_claude": mc, "marcas_em_comum": mm,
                    "jaccard": None if ma is None else round(mm / (ma + mc - mm), 2) if (ma + mc - mm) else None})

    # temas agrupados (método das rodadas 1 e 2) + IC por bootstrap de comentários
    k, po = kappa_temas(r)
    rng = random.Random(SEMENTE)
    boots = []
    for _ in range(N_BOOT):
        b = r.iloc[[rng.randrange(n) for _ in range(n)]]
        kb, _ = kappa_temas(b)
        if kb == kb:
            boots.append(kb)
    boots.sort()
    ic = f"{boots[int(0.025 * len(boots))]:.2f} a {boots[int(0.975 * len(boots)) - 1]:.2f}"
    add("temas (positivos e negativos, agrupados)", k, po, *marcas(r, ("positivos", "negativos")),
        alfa=alfa_krippendorff(pares_temas(r, temas_marcados(r))), ic=ic)
    if set(temas_marcados(r)) != set(GRADE):  # com os 22 temas marcados, coincide com o agrupado
        k, po = kappa_temas(r, grade=True)
        add("temas, grade inteira (22 x 2)", k, po, *marcas(r, ("positivos", "negativos")),
            alfa=alfa_krippendorff(pares_temas(r, GRADE)))
    for pol in ("positivos", "negativos"):
        k, po = kappa(pares_temas(r, temas_marcados(r), (pol,)))
        add(f"temas {pol}", k, po, *marcas(r, (pol,)))
    for est, g in r.groupby("estrato", sort=False):
        k, po = kappa(pares_temas(g, temas_marcados(r)))
        add(f"temas, estrato {est}", k, po, *marcas(g, ("positivos", "negativos")), linhas=len(g))

    ctx = sorted(set().union(*[sp(v) for col in ("autor_contexto", "claude_contexto") for v in r[col]]))
    pares = [(t in sp(a), t in sp(c)) for a, c in zip(r["autor_contexto"], r["claude_contexto"]) for t in ctx]
    k, po = kappa(pares)
    add("contexto", k, po, *marcas(r, ("contexto",)), alfa=alfa_krippendorff(pares))
    for var, col in (("costuma ir", "costuma_ir"), ("voltará", "voltara")):
        pares = list(zip(r[f"autor_{col}"].map(nd), r[f"claude_{col}"].map(nd)))
        k, po = kappa(pares)
        add(var, k, po, alfa=alfa_krippendorff(pares))

    # concordância exata por comentário (mesmo conjunto de temas nas duas polaridades)
    exato = sum(sp(a1) == sp(c1) and sp(a2) == sp(c2) for a1, c1, a2, c2 in
                zip(r["autor_positivos"], r["claude_positivos"], r["autor_negativos"], r["claude_negativos"]))

    kt = pd.DataFrame(lin)
    kt["aceita"] = kt["kappa"].map(lambda x: "" if pd.isna(x) else ("sim" if x >= CRITERIO_KAPPA else "não"))
    kt.to_csv(PASTA / "B2_recodificacao_kappa_rodada3.csv", sep=";", index=False, encoding="utf-8-sig")

    # por tema e polaridade
    pt = []
    for pol in ("positivos", "negativos"):
        A, C = r[f"autor_{pol}"].map(sp), r[f"claude_{pol}"].map(sp)
        for t in GRADE:
            a = [t in x for x in A]; c = [t in x for x in C]
            ambos = sum(x and y for x, y in zip(a, c))
            so_a = sum(x and not y for x, y in zip(a, c)); so_c = sum(y and not x for x, y in zip(a, c))
            if ambos + so_a + so_c == 0:
                continue
            k, _ = kappa(list(zip(a, c)))
            pt.append({"tema": t, "polaridade": pol, "ambos": ambos, "so_autor": so_a, "so_claude": so_c,
                       "kappa": round(k, 2) if k == k else None})
    pt = pd.DataFrame(pt).sort_values(["polaridade", "ambos"], ascending=[False, False])
    pt.to_csv(PASTA / "B2_recodificacao_kappa_rodada3_temas.csv", sep=";", index=False, encoding="utf-8-sig")

    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(kt.to_string(index=False))
        print(f"\nconcordância exata por comentário (temas): {exato} de {n} ({100 * exato / n:.0f}%)")
        print(f"bootstrap: {len(boots)} reamostras válidas")
        print("\npor tema:\n" + pt.to_string(index=False))
    # conferência: soma das marcas por tema = total de marcas
    for pol in ("positivos", "negativos"):
        g = pt[pt.polaridade == pol]
        ma, mc, mm = marcas(r, (pol,))
        assert g["ambos"].sum() == mm and (g["ambos"] + g["so_autor"]).sum() == ma \
            and (g["ambos"] + g["so_claude"]).sum() == mc, pol
    print("\nOK: marcas por tema fecham com os totais")


if __name__ == "__main__":
    main()
