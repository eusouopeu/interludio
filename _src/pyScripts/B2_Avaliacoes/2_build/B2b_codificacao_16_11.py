"""
Bloco B2 - base codificada dos 678 comentários sem código herdado (coleta de 16/11/2026).

Lê a codificação feita fora do Notion (Claude, 16/11/2026), em blocos de texto
`idx|positivos|negativos|contexto|costuma|voltará` com siglas, e junta aos 678
comentários de 2026-11-16_comentarios_a_codificar.csv pela posição da linha.

Regras aplicadas na montagem (dicionário da grade 2):
  - aniversário no Contexto também marca "comemorações e grupos" positivo,
    salvo crítica ao mesmo tema no comentário (decisão de 02/11);
  - Costuma ir e Voltará vazios viram "não foi dito".

Saídas (têm texto; fora do git):
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_comentarios_codificados.csv
  dados-brutos/B2_avaliacoes/analise_conteudo/codificacao_16_11/notion_lote_<n>.json
      lotes de até 100 páginas para o banco "3 - Comentários 16/11"

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/2_build/B2b_codificacao_16_11.py"
"""
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import json  # noqa: E402
import re  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
BRUTOS = ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo"
FALTA = BRUTOS / "2026-11-16_comentarios_a_codificar.csv"
PASTA_COD = BRUTOS / "codificacao_16_11"
SAIDA = BRUTOS / "2026-11-16_comentarios_codificados.csv"
AMOSTRA = (ROOT / "dados-agregados" / "B2_avaliacoes" / "analise_conteudo"
           / "coleta_2026-11-16_reaproveitada" / "B2_amostra_recodificacao_ids.csv")
LOTE = 100
LIMITE_TEXTO = 1990  # limite de 2.000 caracteres do Notion por campo de texto

TEMAS = {
    "VA": "variedade do acervo", "CU": "curadoria e conservação do acervo",
    "EX": "explicação de jogos", "IN": "indicações de jogos",
    "AP": "atendimento presencial", "AO": "atendimento online", "RA": "rapidez do serviço",
    "CO": "comida", "BE": "bebidas", "VC": "variedade do cardápio", "PO": "porções",
    "PE": "preço da entrada", "PC": "preço do cardápio", "PX": "preço de outros itens",
    "RG": "regras da casa", "AM": "ambiente e decoração", "CB": "conforto e barulho",
    "EL": "espaço e lotação", "LI": "limpeza", "LO": "localização e acesso",
    "CG": "comemorações e grupos", "EV": "eventos e comunidade",
}
CONTEXTO = {"AMG": "amigos", "FAM": "família", "CAS": "casal", "ANI": "aniversário",
            "ALU": "aluguel", "LOJ": "loja", "APL": "apenas loja"}
COSTUMA = {"s": "sim", "n": "não", "2": "segunda vez", "": "não foi dito"}
VOLTA = {"s": "sim", "n": "não", "": "não foi dito"}


def siglas(campo, mapa):
    itens = [s for s in campo.split(",") if s]
    desconhecidas = set(itens) - set(mapa)
    assert not desconhecidas, f"sigla desconhecida: {desconhecidas}"
    return [mapa[s] for s in dict.fromkeys(itens)]


def ler_blocos():
    linhas = {}
    for arq in sorted(PASTA_COD.glob("bloco*.txt")):
        for ln in arq.read_text(encoding="utf-8").splitlines():
            if not ln.strip():
                continue
            idx, pos, neg, ctx, cos, vol = ln.split("|")
            assert int(idx) not in linhas, f"linha {idx} repetida ({arq.name})"
            pos, neg, ctx = siglas(pos, TEMAS), siglas(neg, TEMAS), siglas(ctx, CONTEXTO)
            if "aniversário" in ctx and "comemorações e grupos" not in pos + neg:
                pos.append("comemorações e grupos")
            linhas[int(idx)] = {"itens_positivos": pos, "itens_negativos": neg, "contexto": ctx,
                                "costuma_ir": COSTUMA[cos], "voltara": VOLTA[vol]}
    return linhas


def nota_aspecto(txt, aspecto):
    m = re.search(rf"{aspecto} (\d)", txt or "")
    return int(m.group(1)) if m else None


def pagina(r):
    texto = r.texto_avaliacao
    titulo = texto if len(texto) <= LIMITE_TEXTO else texto[:1900] + "… (texto completo no corpo da página)"
    props = {
        "Comentário original": titulo,
        "Texto": texto[:LIMITE_TEXTO],
        "Estabelecimento": r.nome_estabelecimento.replace(",", ""),
        "Place ID": r.place_id, "Nota geral": int(r.nota_avaliacao),
        "Preço por pessoa (R$)": r.preco_por_pessoa, "Tamanho do grupo": r.tamanho_grupo,
        "Tempo de espera": r.tempo_espera, "Data relativa": r.data_relativa,
        "Coletado em": r.coletado_em, "ID da avaliação": r.review_id, "id_avaliacao": r.id_avaliacao,
        "Itens positivos": json.dumps(r.itens_positivos, ensure_ascii=False),
        "Itens negativos": json.dumps(r.itens_negativos, ensure_ascii=False),
        "Contexto": json.dumps(r.contexto, ensure_ascii=False),
        "Costuma ir": r.costuma_ir, "Voltará": r.voltara,
        "Análise de temas": "Claude 16/11/2026", "Origem do código": "novo",
        "Amostra": r.amostra, "Estrato": r.estrato,
    }
    if r.idade_dias_ref:
        props["Idade (dias)"] = int(r.idade_dias_ref)
    for col, asp in (("Comida", "comida"), ("Serviço", "serviço"), ("Ambiente", "ambiente")):
        n = nota_aspecto(r.notas_por_aspecto, asp)
        if n is not None:
            props[col] = n
    props = {k: v for k, v in props.items() if v != ""}
    p = {"properties": props}
    if len(texto) > LIMITE_TEXTO:
        p["content"] = texto
    return p


def main():
    a = pd.read_csv(FALTA, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    cod = ler_blocos()
    assert sorted(cod) == list(range(len(a))), "blocos não cobrem as 678 linhas uma vez cada"
    c = pd.concat([a, pd.DataFrame.from_dict(cod, orient="index").sort_index()], axis=1)
    am = pd.read_csv(AMOSTRA, sep=";", dtype=str, encoding="utf-8-sig")
    c = c.merge(am[["id_avaliacao", "estrato"]], on="id_avaliacao", how="left")
    c["estrato"] = c["estrato"].fillna("")
    c["amostra"] = c["estrato"].map(lambda e: "recodificação" if e else "nenhuma")
    assert len(c) == len(a) and c["id_avaliacao"].is_unique
    assert (c["amostra"] == "recodificação").sum() == len(am)

    saida = c.copy()
    for col in ("itens_positivos", "itens_negativos", "contexto"):
        saida[col] = saida[col].map("; ".join)
    saida.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")

    paginas = [pagina(r) for r in c.itertuples()]
    for velho in PASTA_COD.glob("notion_lote_*.json"):
        velho.unlink()
    for i in range(0, len(paginas), LOTE):
        (PASTA_COD / f"notion_lote_{i // LOTE + 1}.json").write_text(
            json.dumps(paginas[i:i + LOTE], ensure_ascii=False), encoding="utf-8")

    com_tema = ((c["itens_positivos"].str.len() + c["itens_negativos"].str.len()) > 0).sum()
    print(f"{len(c)} comentários codificados; {com_tema} com tema; "
          f"{(c['amostra'] == 'recodificação').sum()} na amostra; "
          f"{-(-len(paginas) // LOTE)} lotes para o Notion")
    temas = pd.Series([t for l in c["itens_positivos"] for t in l]).value_counts()
    print("positivos:", temas.head(8).to_dict())
    print("negativos:", pd.Series([t for l in c["itens_negativos"] for t in l]).value_counts().head(8).to_dict())


if __name__ == "__main__":
    main()
