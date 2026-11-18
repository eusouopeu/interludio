"""
Bloco B1 - resumo do Instagram por casa da população (63 casas desde 12/11/2026),
a partir da coleta de 12/11/2026 (período de 01/07 a 01/11/2026, quatro meses).
Substitui o retrato do Notion de 15/10/2026 (B1_instagram_resumo_notion.csv,
54 casas, período de 01/09 a 01/10/2026), que fica só como fonte do primeiro
post desde a criação do perfil.

Entradas:
  dados-agregados/B1_estabelecimentos/B1_resumo_estabelecimentos.xlsx (aba estabelecimentos: as 63 casas)
  dados-agregados/B1_redes_sociais/rs_<cidade>/rs_<perfil>/AAAA-MM-DD_<perfil>_instagram_perfis.csv
      (coletor instagram.user.js; vale o arquivo de data mais recente de cada perfil)
  dados-agregados/B1_redes_sociais/B1_instagram_resumo_notion.csv  (perfil e primeiro post das 54 casas de outubro)
  dados-agregados/B1_estabelecimentos/3_triagem/B1_instagram_aprovadas.csv (perfil das casas novas)

Regras:
  - cada place_id recebe no máximo um perfil, e cada perfil conta numa só casa;
  - perfil da casa: o do Notion; LudoCafé e Dominaria passam aos perfis da casa
    aprovada (@ludocafebh e @dominariacg, de Fortaleza), que o Notion trazia
    errados (editora e unidade de São Paulo); casas novas: o @ da lista aprovada;
  - Covil Game Bar SBC fica sem perfil: o @covilgb, da marca, já conta no
    Covil Game Bar; Reduto não tem perfil encontrado;
  - posts, curtidas e comentários do período incluem as colaborações da grade
    (colunas *_com_compart do coletor), como no retrato do Notion;
  - primeiro post: o do Notion, quando o perfil é o mesmo; nos demais, o mais
    antigo coletado só quando o coletor marca a grade como completa
    (primeiro_post_definitivo = "sim");
  - perfil com coleta duvidosa no período (POSTS_DUVIDOSOS) fica sem posts,
    curtidas e comentários, com o motivo em observacao.

Saída:
  dados-agregados/B1_redes_sociais/B1_instagram_resumo.csv  (uma linha por casa com perfil)

Uso:
    python3 "_src/pyScripts/B1_Redes_sociais/2_build/B1b_instagram_resumo.py"
"""
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import re

import pandas as pd

ROOT = _AQUI.parents[4]
REDES = ROOT / "dados-agregados" / "B1_redes_sociais"
RESUMO = ROOT / "dados-agregados" / "B1_estabelecimentos" / "B1_resumo_estabelecimentos.xlsx"
NOTION = REDES / "B1_instagram_resumo_notion.csv"
APROVADAS = ROOT / "dados-agregados" / "B1_estabelecimentos" / "3_triagem" / "B1_instagram_aprovadas.csv"
SAIDA = REDES / "B1_instagram_resumo.csv"

CORRECOES = {"LudoCafé": "ludocafebh", "Dominaria Cards & Games": "dominariacg"}
SEM_PERFIL = {"Covil Game Bar SBC": "perfil da marca (@covilgb) já conta no Covil Game Bar",
              "Reduto": "perfil não encontrado"}
POSTS_DUVIDOSOS = {"cineplay_sc": "grade salta de 23/04 a 05/11/2026 com 89 mil seguidores; "
                                  "posts do período a conferir à mão"}


# Só coletas dos 10 dias até 16/11/2026 (decisão de 16/11/2026: contadores e auditoria; as legendas usam o histórico).
COLETA_MINIMA = "2026-11-06"


def perfis_coletados() -> pd.DataFrame:
    linhas = {}
    for f in REDES.glob("rs_*/rs_*/*_instagram_perfis.csv"):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_", f.name)
        if m.group(1) < COLETA_MINIMA:
            continue
        d = pd.read_csv(f, sep=";", encoding="utf-8-sig")
        for _, r in d.iterrows():
            chave = r["perfil"]
            if chave not in linhas or m.group(1) > linhas[chave][0]:
                linhas[chave] = (m.group(1), r)
    return pd.DataFrame([r for _, r in linhas.values()])


def main():
    casas = pd.read_excel(RESUMO, sheet_name="estabelecimentos")[["place_id", "nome"]]
    notion = pd.read_csv(NOTION, sep=";", encoding="utf-8-sig")
    aprov = pd.read_csv(APROVADAS, sep=";", encoding="utf-8-sig")
    perfil_notion = dict(zip(notion.place_id, notion.perfil_instagram))
    primeiro_notion = dict(zip(notion.perfil_instagram, notion.primeiro_post))
    perfil_aprov = dict(zip(aprov.place_id, aprov.instagram_usuario))

    col = perfis_coletados().set_index("perfil")
    linhas = []
    for _, c in casas.iterrows():
        if c.nome in SEM_PERFIL:
            continue
        p = CORRECOES.get(c.nome) or perfil_notion.get(c.place_id) or perfil_aprov.get(c.place_id)
        if pd.isna(p) or p not in col.index:
            continue
        r = col.loc[p]
        primeiro = primeiro_notion.get(p)
        if pd.isna(primeiro) if primeiro is not None else True:
            primeiro = str(r.primeiro_post)[:10] if r.primeiro_post_definitivo == "sim" else None
        obs = POSTS_DUVIDOSOS.get(p)
        linhas.append(dict(
            place_id=c.place_id, estabelecimento=c.nome, perfil_instagram=p,
            seguidores=r.seguidores, n_posts_total=r.n_posts_declarado, primeiro_post=primeiro,
            n_posts_periodo=None if obs else r.n_posts_periodo_com_compart,
            curtidas_periodo=None if obs else r.curtidas_periodo_com_compart,
            comentarios_periodo=None if obs else r.comentarios_periodo_com_compart,
            observacao=obs, coletado_em=r.coletado_em))
    out = pd.DataFrame(linhas)
    assert out.place_id.is_unique and out.perfil_instagram.is_unique, "casa ou perfil repetido"
    out.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")
    faltam = casas[~casas.place_id.isin(out.place_id)].nome.tolist()
    print(f"{len(out)} de {len(casas)} casas com perfil; sem perfil: {faltam}")
    print(f"-> {SAIDA.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
