"""
Bloco B2 - plano B da análise de conteúdo da coleta de 16/11/2026: reaproveita
a codificação da grade 2 (02/11/2026, 1.628 comentários da coleta de outubro)
nos comentários da coleta de 16/11 que já tinham sido codificados.

Por quê: a coleta de 16/11 refez as 63 casas no mesmo dia, para que o intervalo
da análise fique claro (rótulo até "3 meses atrás" em 16/11/2026). A
recodificação completa pode não caber no prazo; este script entrega o que dá
para entregar sem ela: os comentários de 16/11 com código herdado, e a lista
dos que faltam codificar (os publicados depois da coleta de outubro e os das
casas que entraram na população depois dela).

Ligação entre as duas coletas: a base da grade 2 não guarda o review_id do
Google (a coluna "ID da avaliação" veio vazia do Notion). O par sai do texto:
minúsculas, sem pontuação nem espaços, 150 primeiros caracteres, e o mesmo
estabelecimento (nome normalizado). Texto editado depois de outubro não casa e
fica como "a codificar", que é o certo: a codificação antiga era de outro texto.
Textos iguais na mesma casa (ex.: "Excelente") herdam o mesmo código.

Entradas:
  dados-agregados/B2_avaliacoes/B2_avaliacoes_periodo.csv        (B2b_avaliacoes.py; recorte de 16/11)
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-03_2_comentarios_grade2.csv
Saídas:
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_2_comentarios_grade2_reaproveitados.csv
      comentários de 16/11 com código herdado, no formato da base da grade 2
      (lida por B2a_temas_grade2.py e B2a_retorno_e_clusters.py com --base);
      fora do git: tem texto
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_comentarios_a_codificar.csv
      comentários de 16/11 sem código (fora do git: tem texto)
  dados-agregados/B2_avaliacoes/analise_conteudo/coleta_2026-11-16_reaproveitada/B2_cobertura_codificacao.csv
      uma linha por casa: comentários de 16/11, com código herdado, a codificar

Conferência (o script para se falhar): por casa, com código + a codificar =
comentários de 16/11; soma das casas = total do recorte com texto.

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/2_build/B2b_comentarios_reaproveitados.py"
"""
# Caminhos: _src/outros/G*/ (log comum); log em ../4_logs/
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import hashlib  # noqa: E402
import re  # noqa: E402
import unicodedata  # noqa: E402

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
PERIODO = ROOT / "dados-agregados" / "B2_avaliacoes" / "B2_avaliacoes_periodo.csv"
BRUTOS = ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo"
GRADE2 = BRUTOS / "2026-11-03_2_comentarios_grade2.csv"
SAIDA_BASE = BRUTOS / "2026-11-16_2_comentarios_grade2_reaproveitados.csv"
SAIDA_FALTA = BRUTOS / "2026-11-16_comentarios_a_codificar.csv"
PASTA = ROOT / "dados-agregados" / "B2_avaliacoes" / "analise_conteudo" / "coleta_2026-11-16_reaproveitada"


# Casas renomeadas no Google Maps entre outubro e 16/11: nome de 16/11 -> nome na grade 2.
ALIAS = {
    "Bravo Jogos | Loja de Jogos de Tabuleiro": "Bravo Jogos",
    "Dungeon Games Store - Hambúrgueria, TCG & Board Games": "Dungeon Games Store",
    "Joyjoy Café Cristo Rei": "Joyjoy Café",
    "Magic Store Brasil": "Magic Store Brazil",
    "Paladins Games Store": "Paladins Game Store",
    "São Jogue": "São Jogue - Bela Vista",
}


def chave(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    return re.sub(r"[\W_]+", "", s)[:150]


def nome(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def main():
    novo = pd.read_csv(PERIODO, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    novo = novo[novo["tem_texto"] == "sim"].copy()
    novo["k"] = novo["texto_avaliacao"].map(chave)
    novo["n"] = novo["nome_estabelecimento"].map(lambda e: nome(ALIAS.get(e, e)))
    novo["id_avaliacao"] = novo["review_id"].map(lambda r: hashlib.sha1(r.encode()).hexdigest()[:10])

    g = pd.read_csv(GRADE2, dtype=str, keep_default_na=False)
    # Texto vazio no retrato do Notion: o texto é o último campo do "Comentário original".
    txt = g["Texto"].where(g["Texto"] != "", g["Comentário original"].str.split(" :: ").str[-1])
    g["k"] = txt.map(chave)
    g["n"] = g["Estabelecimento"].map(nome)
    g1 = g.drop_duplicates(["n", "k"])

    m = novo.merge(g1.drop(columns=["Texto"]), on=["n", "k"], how="left", suffixes=("", "_g2"))
    com = m["id"].notna()
    # Nomes que não casam entre as duas bases (casa renomeada no Maps) aparecem aqui.
    sem_nome = sorted(set(novo["n"]) - set(g["n"]))

    base = m[com].copy()
    base["Texto"] = base["texto_avaliacao"]
    base["review_id"], base["data_coleta_nova"] = base["review_id"], base["coletado_em"]
    cols = list(g.columns.drop(["k", "n"])) + ["review_id", "id_avaliacao", "data_coleta_nova"]
    base = base[cols]
    base.to_csv(SAIDA_BASE, index=False, encoding="utf-8")

    falta = m.loc[~com, ["place_id", "nome_estabelecimento", "review_id", "id_avaliacao", "nota_avaliacao",
                         "data_relativa", "idade_dias_ref", "preco_por_pessoa", "notas_por_aspecto",
                         "tamanho_grupo", "tempo_espera", "texto_avaliacao", "coletado_em"]]
    falta.to_csv(SAIDA_FALTA, sep=";", index=False, encoding="utf-8-sig")

    cob = (m.assign(com=com).groupby(["place_id", "nome_estabelecimento"])
           .agg(comentarios_16_11=("review_id", "size"), com_codigo_herdado=("com", "sum")).reset_index())
    cob["a_codificar"] = cob["comentarios_16_11"] - cob["com_codigo_herdado"]
    cob["pct_herdado"] = (100 * cob["com_codigo_herdado"] / cob["comentarios_16_11"]).round(1)
    cob = cob.sort_values("comentarios_16_11", ascending=False)
    assert (cob["com_codigo_herdado"] + cob["a_codificar"] == cob["comentarios_16_11"]).all()
    assert cob["comentarios_16_11"].sum() == len(novo) == len(base) + len(falta), "cobertura não fecha"
    PASTA.mkdir(parents=True, exist_ok=True)
    cob.to_csv(PASTA / "B2_cobertura_codificacao.csv", sep=";", index=False, encoding="utf-8-sig")

    print(f"{len(novo)} comentários de 16/11: {len(base)} com código herdado ({100 * len(base) / len(novo):.1f}%), "
          f"{len(falta)} a codificar; {cob['com_codigo_herdado'].gt(0).sum()} de {len(cob)} casas com algum código")
    print(f"comentários da grade 2 reencontrados: {g['k'].isin(base['Texto'].map(chave)).sum()} de {len(g)}")
    print(f"casas de 16/11 sem nome correspondente na grade 2: {len(sem_nome)}")
    print(f"soma por casa = {cob['comentarios_16_11'].sum()}, diferença {len(novo) - cob['comentarios_16_11'].sum()}")
    print(f"OK: {SAIDA_BASE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
