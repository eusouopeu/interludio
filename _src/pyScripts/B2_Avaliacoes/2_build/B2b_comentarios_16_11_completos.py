"""
Bloco B2 - base completa da análise de conteúdo da coleta de 16/11/2026 (L41, opção c).

Junta, no formato da base da grade 2 (lido por B2a_temas_grade2.py e
B2a_retorno_e_clusters.py com --base):
  - os 1.280 comentários com código herdado da grade 2
    (2026-11-16_2_comentarios_grade2_reaproveitados.csv, B2b_comentarios_reaproveitados.py);
  - os 678 codificados pelo Claude em 16/11 (2026-11-16_comentarios_codificados.csv,
    B2b_codificacao_16_11.py), validados pela rodada 3 da recodificação cega
    (B2a_kappa_rodada3.py: kappa dos temas 0,79).
O código dos 678 fica o do Claude, também nos 100 recodificados pelo autor (mesma
regra das rodadas 1 e 2: a recodificação mede a concordância, não substitui o código).

Conversões: itens separados por ", " (formato do Notion); "não foi dito" vira vazio
em Costuma ir e Voltará; "R$ 80–100" vira "80–100" no preço por pessoa; a capital
vem de B1_resumo_estabelecimentos.xlsx pelo place_id.

Conferência (o script para se falhar): 1.280 + 678 = 1.958 linhas, id_avaliacao sem
repetição, todas as casas com capital, temas só da grade.

Saída (tem texto; fora do git):
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_2_comentarios_grade2_completos.csv

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/2_build/B2b_comentarios_16_11_completos.py"
"""
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import re  # noqa: E402

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
BRUTOS = ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo"
HERDADOS = BRUTOS / "2026-11-16_2_comentarios_grade2_reaproveitados.csv"
NOVOS = BRUTOS / "2026-11-16_comentarios_codificados.csv"
RESUMO_B1 = ROOT / "dados-agregados" / "B1_estabelecimentos" / "B1_resumo_estabelecimentos.xlsx"
SAIDA = BRUTOS / "2026-11-16_2_comentarios_grade2_completos.csv"
N_HERDADOS, N_NOVOS = 1280, 678


def lista(v):
    itens = [x.strip() for x in re.split(r"[;,|]", str(v)) if x.strip()]
    return ", ".join(itens) if itens else None


def main():
    h = pd.read_csv(HERDADOS, dtype=str)
    n = pd.read_csv(NOVOS, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    assert len(h) == N_HERDADOS and len(n) == N_NOVOS, (len(h), len(n))
    cap = pd.read_excel(RESUMO_B1, sheet_name="estabelecimentos", dtype=str).set_index("place_id")["capital_endereco"]
    falta = set(n["place_id"]) - set(cap.index)
    assert not falta, f"casas sem capital: {falta}"

    vazio = lambda v: None if v in ("", "não foi dito") else v
    novos = pd.DataFrame({
        "Texto": n["texto_avaliacao"],
        "Estabelecimento": n["nome_estabelecimento"],
        "Capital do endereço": n["place_id"].map(cap),
        "Place ID": n["place_id"],
        "Nota geral": n["nota_avaliacao"],
        "Data relativa": n["data_relativa"],
        "Preço por pessoa (R$)": n["preco_por_pessoa"].map(
            lambda v: re.sub(r"^R\$\s*", "", v.replace("\xa0", " ")).strip() or None),
        "Tamanho do grupo": n["tamanho_grupo"].map(vazio),
        "Tempo de espera": n["tempo_espera"].map(vazio),
        "Itens positivos": n["itens_positivos"].map(lista),
        "Itens negativos": n["itens_negativos"].map(lista),
        "Contexto": n["contexto"].map(lista),
        "Costuma ir": n["costuma_ir"].map(vazio),
        "Voltará": n["voltara"].map(vazio),
        "Análise de temas": "Claude 16/11/2026",
        "review_id": n["review_id"],
        "id_avaliacao": n["id_avaliacao"],
        "Data da coleta": n["coletado_em"].str[:10],
    })
    d = pd.concat([h.assign(origem_codigo="herdado da grade 2"), novos.assign(origem_codigo="Claude 16/11/2026")],
                  ignore_index=True)
    # Um só nome por casa (o do B1): os novos pelo place_id; os herdados pelo nome sem
    # pontuação (o Notion tirava a vírgula dos nomes no select).
    b1 = pd.read_excel(RESUMO_B1, sheet_name="estabelecimentos", dtype=str)
    chave = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
    por_nome = dict(zip(b1["nome"].map(chave), b1["place_id"]))
    pid = d["Place ID"].where(d["origem_codigo"] == "Claude 16/11/2026", d["Estabelecimento"].map(chave).map(por_nome))
    assert pid.notna().all(), sorted(set(d.loc[pid.isna(), "Estabelecimento"]))
    d["Place ID"] = pid
    d["Estabelecimento"] = pid.map(dict(zip(b1["place_id"], b1["nome"])))
    d["Capital do endereço"] = pid.map(cap)
    assert len(d) == N_HERDADOS + N_NOVOS
    assert d["id_avaliacao"].notna().all() and not d["id_avaliacao"].duplicated().any()
    assert d["Capital do endereço"].notna().all()
    d.to_csv(SAIDA, index=False)
    print(f"OK: {SAIDA.relative_to(ROOT)} ({len(d)} linhas: {N_HERDADOS} herdadas + {N_NOVOS} novas; "
          f"{d['Estabelecimento'].nunique()} casas)")
    print(d.groupby("origem_codigo")["Capital do endereço"].nunique().to_dict())


if __name__ == "__main__":
    main()
