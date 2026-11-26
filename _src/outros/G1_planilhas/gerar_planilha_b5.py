"""
Planilha dos dados agregados do B5 (ativos fixos: aluguel e orçamento da etapa 1), com o mesmo
estilo das planilhas dos blocos (planilha_estilo.py). Pedido do autor em 25/11/2026.

Lê `dados-agregados/B5_aluguel/` e `dados-agregados/B5_mobiliario/` e grava
`textos-tcc/planilhas/B5_dados_agregados.xlsx`, uma aba por tabela:

1. Buscas de aluguel: cada busca nos portais, com o total da busca, os anúncios lidos e a cobertura.
2. Orçamento por item da etapa 1: os 77 itens, com quantidade, preço e total nos três cenários.
3. Aluguel por bairro e área: anúncios dos bairros do recorte (o mesmo universo da aba
   aluguel_faixas do P9), por bairro e, dentro dele, por faixa de área.
4. Orçamento por premissa e grupo: os itens somados por grupo, com subtotal por premissa (I01 a I04).
5. Reforma pelo SINAPI: a reforma (I01) por grupo de serviço, em reais e por m² de cada cenário.

Uso: python3 _src/outros/G1_planilhas/gerar_planilha_b5.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [*map(str, ((ROOT / "_src") / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
import planilha_estilo as est  # noqa: E402
from planilha_estilo import *  # noqa: E402,F403

registrar_execucao(__file__)
AG = ROOT / "dados-agregados"
AL, MO = AG / "B5_aluguel", AG / "B5_mobiliario"
SAIDA = ROOT / "textos-tcc" / "planilhas"
est.GRAF = ROOT / "textos-tcc" / "graficos" / "B5"
est.GRAF.mkdir(parents=True, exist_ok=True)


def ler(arq):
    return pd.read_csv(arq, sep=";", decimal=",", encoding="utf-8-sig")


def ultimo(pasta, padrao):
    return sorted(pasta.glob(padrao))[-1]


FONTE_AL = "B5, anúncios de imóveis comerciais para alugar no OLX, no ZAP e no Viva Real (Salvador, nov/2026)"
FONTE_OR = "B5, orçamento da etapa 1: SINAPI BA (Caixa, set/2026, sem desoneração, com BDI) e coletas em sites (set/2026)"

# ---------------------------------------------------------------- Tab 1: buscas
cob = ler(ultimo(AL, "[[]B5[]] Cobertura das Buscas de Aluguel *.csv"))
NOMES = {"barra": "Barra", "caminho-das-arvores": "Caminho das Árvores", "canela": "Canela", "graca": "Graça",
         "itaigara": "Itaigara", "ondina": "Ondina", "patamares": "Patamares", "pituba": "Pituba",
         "rio-vermelho": "Rio Vermelho", "vitoria": "Vitória"}
PORTAL = {"olx": "OLX", "vivareal": "Viva Real", "zap": "ZAP"}


def busca(url):
    """Bairro e tipo de imóvel buscados, lidos da URL de cada portal."""
    m = re.search(r"/salvador/([a-z-]+)\?|/bairros/([a-z-]+)/|\+\+([a-z-]+)/", url)
    bairro = NOMES.get(next(g for g in m.groups() if g), "?") if m else "Salvador, todos os bairros"
    tipo = ("casa comercial" if "casa-comercial" in url else "loja e salão" if "loja-salao" in url
            else "ponto comercial" if "ponto-comercial" in url else "comércio e indústria")
    return bairro, tipo


cob[["bairro", "tipo"]] = cob.busca.apply(lambda u: pd.Series(busca(u)))
cob["portal"] = cob.portal.map(PORTAL)
cob = cob.sort_values(["portal", "bairro", "tipo"]).reset_index(drop=True)
assert (cob.bairro != "?").all(), cob[cob.bairro == "?"].busca.tolist()
lin1 = [[r.portal, r.bairro, r.tipo, r.total_busca, r.anuncios_lidos, r.paginas_lidas,
         pd.to_datetime(r.data_coleta).strftime("%d/%m/%Y"), f"=E{k}/D{k}"] for k, r in enumerate(cob.itertuples(), 3)]
t1 = 3 + len(cob)
lin1.append(["Total", "", "", f"=SUM(D3:D{t1 - 1})", f"=SUM(E3:E{t1 - 1})", f"=SUM(F3:F{t1 - 1})", "", f"=E{t1}/D{t1}"])
nova_aba("Tab 1", "Tabela 1 – Buscas de aluguel nos portais",
         ["Portal", "Bairro buscado", "Tipo de imóvel", "Anúncios na busca", "Anúncios lidos", "Páginas lidas",
          "Data da coleta", "Cobertura"], lin1, ["cen", "txt", "cen", "int", "int", "int", "cen", "pct"], FONTE_AL,
         [10, 24, 18, 11, 11, 9, 12, 10],
         notas=["Nota: cobertura = anúncios lidos ÷ anúncios na busca; as buscas da cidade inteira (cobertura baixa) "
                "completam as dos bairros. O mesmo anúncio pode aparecer em mais de uma busca e de um portal; as "
                "duplicatas saem na consolidação (Tabela 3)."],
         nome="Buscas de aluguel")

# ---------------------------------------------------------------- Tab 2: orçamento por item
oi = ler(ultimo(MO, "[[]B5[]] Orçamento por Item Etapa 1 *.csv"))
pr = ler(ultimo(MO, "[[]B5[]] Orçamento por Premissa Etapa 1 *.csv")).set_index("premissa")
PREM = {p: pr.loc[p, "descricao"] for p in pr.index}
lin2, r, sub2 = [], 3, []
for p, g in oi.groupby("premissa", sort=True):
    r0 = r
    for it in g.itertuples():
        lin2.append([it.id, it.grupo, it.item, it.unidade, it.qtd_provavel, it.preco_unit_provavel, it.total_pessimista,
                     it.total_provavel, it.total_otimista, it.fonte_preco, f"{it.nivel_preco} / {it.nivel_qtd}"])
        r += 1
    lin2.append([f"Subtotal – {p} {PREM[p].lower()}", "", "", "", "", "", f"=SUM(G{r0}:G{r - 1})",
                 f"=SUM(H{r0}:H{r - 1})", f"=SUM(I{r0}:I{r - 1})", "", ""])
    sub2.append(r)
    r += 1
lin2.append(["Total"] + [""] * 5 + ["=" + "+".join(f"{c}{x}" for x in sub2) for c in "GHI"] + ["", ""])
for c in ("total_pessimista", "total_provavel", "total_otimista"):  # o item soma o que o P9 usa
    assert abs(oi[c].sum() - pr[c].sum()) < 0.01, c
nova_aba("Tab 2", "Tabela 2 – Orçamento por item da etapa 1",
         ["Item", "Grupo", "Descrição", "Unidade", "Quantidade provável", "Preço unitário provável (R$)",
          "Total pessimista (R$)", "Total provável (R$)", "Total otimista (R$)", "Fonte do preço",
          "Tipo de evidência (preço / quantidade)"], lin2,
         ["cen", "txt", "txt", "cen", "dec", "dec", "dec", "dec", "dec", "txt", "cen"], FONTE_OR,
         [8, 18, 34, 8, 11, 13, 13, 13, 13, 26, 14],
         notas=["Nota: quantidade e preço unitário variam por cenário; só o provável aparece aqui, os três totais vêm "
                "do orçamento. Item sem preço entra com total zero (cobertura na Tabela 4)."],
         nome="Orçamento por item")

# ---------------------------------------------------------------- Tab 3: aluguel por bairro e área
# Mesmo universo da aba aluguel_faixas do P9 (gerar_modelo_financeiro.py, ler_fontes): os bairros do
# recorte, sem salas em prédio e sem o segundo anúncio das possíveis duplicatas do mesmo tipo com até
# 5 m² de diferença.
BAIRROS = ("Pituba", "Itaigara", "Graça", "Patamares", "Caminho das Árvores", "Vitória", "Barra",
           "Ondina", "Chame-Chame", "Rio Vermelho", "Canela")
an = ler(AL / "[B5] Anúncios de Aluguel 2026-11 (OLX, ZAP, Viva Real).csv")
an = an[an.bairro.isin(BAIRROS) & (an.subtipo != "sala") & ~an.titulo.str.contains("Salas", na=False)]
dup = ler(AL / "[B5] Possíveis Duplicatas de Aluguel 2026-11 (OLX, ZAP, Viva Real).csv")
tipo, fora = dict(zip(an.id, an.subtipo)), set()
for _, d in dup.iterrows():
    if (d.id_a in tipo and d.id_b in tipo and tipo[d.id_a] == tipo[d.id_b]
            and abs(d.area_m2_a - d.area_m2_b) <= 5 and d.id_a not in fora):
        fora.add(d.id_b)
an = an[~an.id.isin(fora)].copy()
an["custo_m2"] = (an.aluguel + an.condominio.fillna(0) + an.iptu.fillna(0)) / an.area_m2
FAIXAS = [("até 99 m²", 0, 100, "left"), ("100 a 150 m² (ponto do plano)", 100, 150, "both"),
          ("151 a 200 m²", 150, 200, "right"), ("mais de 200 m²", 200, np.inf, "neither")]


def faixa(a):
    for rot, lo, hi, inc in FAIXAS:
        if pd.Series([a]).between(lo, hi, inclusive=inc).iloc[0]:
            return rot
    return None


an["faixa"] = an.area_m2.map(faixa)
assert an.faixa.notna().all()
MIN_N = 5  # abaixo disso, só a contagem (quartis de menos de 5 anúncios não informam)
ordem_b = an.bairro.value_counts().index.tolist()


def resumo(g):
    if len(g) < MIN_N:
        return [None] * 5
    q = g.aluguel_m2.quantile([.25, .5, .75]).tolist()
    return q + [g.custo_m2.median(), g.area_m2.median()]


lin3, r, sub3 = [], 3, []
for b in ordem_b:
    g = an[an.bairro == b]
    r0 = r
    for rot, *_ in FAIXAS:
        h = g[g.faixa == rot]
        if len(h):
            lin3.append([b, rot, len(h)] + resumo(h))
            r += 1
    lin3.append([f"Subtotal – {b}", "", f"=SUM(C{r0}:C{r - 1})"] + resumo(g))
    sub3.append(r)
    r += 1
lin3.append(["Total", "", "=" + "+".join(f"C{x}" for x in sub3)] + resumo(an))
r += 1
lin3.append(["Conferência (total − anúncios do recorte; deve ser 0)", "", f"=C{r - 1}-{len(an)}", "", "", "", "", ""])
med = an.groupby("bairro").aluguel_m2.median().reindex(ordem_b)
g3 = barras_h("03_aluguel_m2_bairro", ordem_b, {"aluguel pedido por m², mediana": med.tolist()},
              lambda v: br(v, 2, pre="R$ "), destaque="Pituba")
nova_aba("Tab 3", "Tabela 3 – Aluguel pedido por bairro e faixa de área",
         ["Bairro", "Faixa de área", "Anúncios", "Aluguel por m², 1º quartil (R$)", "Aluguel por m², mediana (R$)",
          "Aluguel por m², 3º quartil (R$)", "Custo total por m², mediana (R$)", "Área mediana (m²)"], lin3,
         ["cen", "txt", "int", "dec", "dec", "dec", "dec", "dec"], FONTE_AL, [18, 26, 10, 13, 13, 13, 13, 11], g3,
         notas=[f"Nota: {len(an)} anúncios dos bairros do recorte do plano (Tabela 6.1), sem salas e sem duplicatas, o mesmo "
                "universo da aba aluguel_faixas do P9. Bairros em ordem de número de anúncios. Custo total = aluguel + "
                "condomínio (vazio = isento) + IPTU (vazio = não informado). "
                f"Com menos de {MIN_N} anúncios, só a contagem."],
         nome="Aluguel por bairro e área")

# ---------------------------------------------------------------- Tab 4: orçamento por premissa e grupo
lin4, r, sub4 = [], 3, []
tot_prov = oi.total_provavel.sum()
for p, g in oi.groupby("premissa", sort=True):
    r0 = r
    for gr, h in g.groupby("grupo", sort=False):
        lin4.append([p, gr, len(h), int(h.com_preco.sum()), int(h.ofertas.fillna(0).sum()), h.total_pessimista.sum(),
                     h.total_provavel.sum(), h.total_otimista.sum(), f"=G{r}/G$TOT"])
        r += 1
    lin4.append([f"Subtotal – {p} {PREM[p].lower()}", ""] + [f"=SUM({c}{r0}:{c}{r - 1})" for c in "CDEFGH"]
                + [f"=G{r}/G$TOT"])
    sub4.append(r)
    r += 1
lin4.append(["Total", ""] + ["=" + "+".join(f"{c}{x}" for x in sub4) for c in "CDEFGH"] + [f"=G{r}/G$TOT"])
lin4 = [[v.replace("$TOT", f"${r}") if isinstance(v, str) else v for v in ln] for ln in lin4]
for p in pr.index:
    h = oi[oi.premissa == p]
    assert len(h) == pr.loc[p, "itens"] and h.com_preco.sum() == pr.loc[p, "itens_com_preco"], p
prem_t = oi.groupby("premissa").total_provavel.sum()
g4 = barras_h("04_orcamento_premissa", [f"{p} {PREM[p]}" for p in prem_t.index], {"provável": prem_t.tolist()},
              lambda v: br(v / 1000, 1, pre="R$ ", suf=" mil"), larg_rotulo=26)
nova_aba("Tab 4", "Tabela 4 – Orçamento da etapa 1 por premissa e grupo",
         ["Premissa", "Grupo", "Itens", "Itens com preço", "Ofertas coletadas", "Total pessimista (R$)",
          "Total provável (R$)", "Total otimista (R$)", "% do total provável"], lin4,
         ["cen", "txt", "int", "int", "int", "dec", "dec", "dec", "pct"], FONTE_OR, [12, 22, 8, 10, 10, 14, 14, 14, 11], g4,
         notas=["Nota: os subtotais são as premissas I01 a I04 do P9. Ofertas coletadas = anúncios de sites usados no preço; "
                "item do SINAPI conta uma oferta."],
         nome="Orçamento por premissa")

# ---------------------------------------------------------------- Tab 5: reforma pelo SINAPI
ob = oi[oi.premissa == "I01"]
area = {c: pr.loc["I01", f"total_{c}"] / pr.loc["I01", f"i01_rs_m2_{c}"] for c in ("pessimista", "provavel", "otimista")}
lin5, r = [], 3
for gr, h in ob.groupby("grupo", sort=False):
    sin = h[h.fonte_preco.str.startswith("SINAPI")]
    lin5.append([gr, len(h), len(sin), h.total_pessimista.sum(), h.total_provavel.sum(), h.total_otimista.sum(),
                 f"=D{r}/{area['pessimista']}", f"=E{r}/{area['provavel']}", f"=F{r}/{area['otimista']}"])
    r += 1
lin5.append(["Total", f"=SUM(B3:B{r - 1})", f"=SUM(C3:C{r - 1})"] + [f"=SUM({c}3:{c}{r - 1})" for c in "DEF"]
            + [f"=D{r}/{area['pessimista']}", f"=E{r}/{area['provavel']}", f"=F{r}/{area['otimista']}"])
lin5.append(["Área do ponto no cenário (m²)", "", "", area["pessimista"], area["provavel"], area["otimista"], "", "", ""])
g5 = barras_h("05_reforma_m2_grupo", ob.groupby("grupo", sort=False).total_provavel.sum().sort_values(ascending=False).index.tolist(),
              {"R$ por m², provável": (ob.groupby("grupo", sort=False).total_provavel.sum()
                                       .sort_values(ascending=False) / area["provavel"]).tolist()},
              lambda v: br(v, 2, pre="R$ "))
nova_aba("Tab 5", "Tabela 5 – Reforma e instalações pelo SINAPI, por grupo de serviço",
         ["Grupo de serviço", "Itens", "Itens pelo SINAPI", "Pessimista (R$)", "Provável (R$)", "Otimista (R$)",
          "Pessimista (R$/m²)", "Provável (R$/m²)", "Otimista (R$/m²)"], lin5,
         ["txt", "int", "int", "dec", "dec", "dec", "dec", "dec", "dec"], FONTE_OR, [24, 8, 10, 14, 14, 14, 13, 13, 13], g5,
         notas=["Nota: R$/m² = total do grupo ÷ área do ponto no cenário; a linha Total por m² é a premissa I01 do P9. "
                "Itens fora do SINAPI (coleta em sites) entram no grupo com o preço coletado."],
         nome="Reforma pelo SINAPI")
for c, col in (("pessimista", "D"), ("provavel", "E"), ("otimista", "F")):
    assert abs(ob[f"total_{c}"].sum() - pr.loc["I01", f"total_{c}"]) < 0.01, c

# ---------------------------------------------------------------- gravar
SAIDA.mkdir(parents=True, exist_ok=True)
tmp = SAIDA / "_b5.tmp.xlsx"
est.wb.save(tmp)
saida = SAIDA / "B5_dados_agregados.xlsx"
dividir(tmp, INDICE, [(saida, "Dados agregados do B5 (ativos fixos) – TCC Luderia", [a for a, _, _ in INDICE], [],
                       ["Gráficos em PNG de 300 dpi em textos-tcc/graficos/B5/. "
                        "Gerado por _src/outros/G1_planilhas/gerar_planilha_b5.py."])])
tmp.unlink()
print(f"{saida.relative_to(ROOT)}: {len(INDICE)} tabelas")
print(f"Conferência: {len(cob)} buscas; {len(oi)} itens do orçamento; {len(an)} anúncios no recorte "
      f"({len(fora)} duplicatas fora); I01 provável R$ {pr.loc['I01', 'total_provavel']:,.2f}, "
      f"R$ {pr.loc['I01', 'i01_rs_m2_provavel']:,.2f}/m²")
