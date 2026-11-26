"""
Planilhas com os dados agregados da pesquisa (B1, B3 e B4) e gráficos, uma por bloco.

Lê só arquivos processados de `dados-agregados/` e grava em `textos-tcc/planilhas/`
(DMax = versão completa, com todos os dados coletados; a DMin, essencial, será
definida pelo autor; ver _docs/_instrucoes/1c_versoes.md):
`B1_dados_agregados.xlsx`, `B1_dados_agregados_resumido.xlsx` (sem
eventos, dias e temas do Instagram e sem o custo do acervo),
`B3_dados_agregados.xlsx` e `B4_dados_agregados.xlsx`, uma aba por tabela,
com a figura ao lado, e os gráficos em PNG (300 dpi) em `textos-tcc/graficos/agregados/`. Monta
tudo numa pasta só e depois separa, renumerando as tabelas de cada arquivo.

Fora por pedido do autor (30/10/2026): os comentários do B2 (texto, temas e
contagens de avaliações) e, no entorno, tudo o que vem do OpenStreetMap
(`shopping_porte_*` e `B1_entorno.csv`). Do entorno ficam só as leituras do
coletor do Google Maps (estações de metrô, trem, VLT e "trilhos" =
metrô + trem + VLT, e distância ao shopping).

Tabelas do B1 usam fórmulas sobre a aba "Dados B1" (54 casas, valores do
`B1_estatistica_descritiva_geral.xlsx`); as de Instagram, B3 e B4 trazem os
valores das análises já feitas, com fonte no rodapé. Paleta e desenho dos
gráficos seguem o desenho do documento de referência do autor (rótulos em
negrito na ponta da barra; legenda acima do gráfico), com cores só das paletas
slate e purple do Tailwind CSS.

Uso: python3 _src/outros/G1_planilhas/gerar_planilha_agregada.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Border
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.formula import ArrayFormula

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [*map(str, ((ROOT / "_src") / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
import planilha_estilo as est  # noqa: E402
from planilha_estilo import *  # noqa: E402,F403

D = ROOT / "dados"

DADOS_AGREGADOS = ROOT / "dados-agregados"

DADOS_BRUTOS = ROOT / "dados-brutos"
B3 = DADOS_AGREGADOS / "B3_contagem"
SAIDA = ROOT / "textos-tcc" / "planilhas"
GRAF = ROOT / "textos-tcc" / "graficos" / "agregados"

# ---------------------------------------------------------------- B1: base
registrar_execucao(__file__)
est.GRAF = GRAF

ARQ_DESC = DADOS_AGREGADOS / "B1_estabelecimentos" / "4_estatistica_descritiva" / "B1_estatistica_descritiva_geral.xlsx"
base = pd.read_excel(ARQ_DESC, sheet_name="dados")
COLS = [
    ("nome", "casa", "txt"), ("metropole", "metrópole", "txt"), ("regiao", "região", "txt"),
    ("avaliacao_media", "nota no Google", "dec"), ("volume_avaliacoes", "avaliações no Google", "int"),
    ("dias_abertos", "dias abertos", "int"), ("horas_semana", "horas por semana", "int"),
    ("abre_cedo_h", "abre mais cedo (h)", "dec"), ("fecha_tarde_h", "fecha mais tarde (h)", "dec"),
    ("abre_segunda", "abre segunda", "int"), ("abre_terca", "abre terça", "int"), ("abre_quarta", "abre quarta", "int"),
    ("abre_quinta", "abre quinta", "int"), ("abre_sexta", "abre sexta", "int"), ("abre_sabado", "abre sábado", "int"),
    ("abre_domingo", "abre domingo", "int"),
    ("metro_500m", "metrô até 500 m", "int"), ("metro_1000m", "metrô até 1000 m", "int"),
    ("dist_metro_m", "distância ao metrô (m)", "int"),
    ("dist_shopping_m", "distância ao shopping (m)", "int"),
    ("seguidores", "seguidores", "int"), ("n_posts_total", "posts desde o início", "int"),
    ("idade_perfil_anos", "idade do perfil (anos)", "dec"), ("n_posts_periodo", "posts 01/07 a 01/11/2026", "int"),
    ("interacoes_por_post", "interações por post", "dec"), ("engajamento_pct", "engajamento", "pct"),
    ("itens_com_preco", "itens com preço", "int"), ("tem_cardapio", "cardápio transcrito", "int"),
    ("cobra_couvert", "couvert encontrado", "int"),
    ("couvert_mediana", "couvert (R$)", "dec"), ("bebida_mediana", "bebida (R$)", "dec"),
    ("entrada_ou_prato_mediana", "entrada ou prato (R$)", "dec"), ("consumo_baixa", "consumo baixo (R$)", "dec"),
    ("consumo_mediana", "consumo mediano (R$)", "dec"), ("consumo_alta", "consumo alto (R$)", "dec"),
    ("cesta_baixa", "cesta completa baixa (R$)", "dec"),
    ("cesta_mediana", "cesta completa mediana (R$)", "dec"), ("cesta_alta", "cesta completa alta (R$)", "dec"),
    ("hamburguer_mediana", "hambúrguer (R$)", "dec"), ("batata_mediana", "batata (R$)", "dec"),
    ("cerveja_mediana", "cerveja (R$)", "dec"), ("refrigerante_mediana", "refrigerante (R$)", "dec"),
    ("drinks_mediana", "drinks (R$)", "dec"), ("titulos_acervo", "títulos no acervo", "int"),
]
# Sem uso em nenhuma tabela: ficam no fim da base da versão completa e saem da resumida.
COLS_SO_COMPLETA = [
    ("trem_1000m", "trem até 1000 m", "int"), ("vlt_1000m", "VLT até 1000 m", "int"),
    ("trilhos_500m", "trilhos até 500 m", "int"), ("trilhos_1000m", "trilhos até 1000 m", "int"),
    ("dist_trilhos_m", "distância aos trilhos (m)", "int"),
]
# Onde cada dado foi encontrado (Tabela 8, pedido do autor, 25/11/2026): uma categoria por casa e por
# dado, pela fonte de maior prioridade (cardápio > site > Instagram > fotos > outra fonte), para cada bloco fechar em N.
CARD = DADOS_AGREGADOS / "B1_cardapios"
ONDE = {"cardapio": "cardápio digital, delivery ou PDF", "site": "site da casa", "instagram": "Instagram ou TikTok",
        "fotos": "fotos no Google Maps ou no Instagram", "outra": "outra fonte (imprensa, guia, reservas)"}
PRIOR = ["cardapio", "site", "instagram", "fotos", "outra"]


def canal(txt):
    t = str(txt).lower()
    if "foto" in t:  # fotos de clientes ou do cartaz, no Google Maps ou no Instagram
        return "fotos"
    if any(k in t for k in ("imprensa", "guia", "get in", "google maps", "covil")):
        return "outra"
    if any(k in t for k in ("instagram", "tiktok")):
        return "instagram"
    if any(k in t for k in ("pdf", "canva", "cardápio digital", "delivery", "takeat", "goomer", "menudino", "anota.ai",
                            "saipos", "vuca", "cloudfy", "linktree")):
        return "cardapio"
    if any(k in t for k in ("site", "wix", "como funciona")):
        return "site"
    return "outra"


def melhor(canais):
    canais = [c for c in canais if c]
    return ONDE[min(canais, key=PRIOR.index)] if canais else None


_it = pd.read_excel(CARD / "B1_cardapios_itens_precos.xlsx", sheet_name="itens")
_fo = pd.read_excel(CARD / "B1_cardapios_itens_precos.xlsx", sheet_name="fontes")
_bm = pd.read_csv(CARD / "B1_busca_minuciosa_taxa_cardapio_acervo.csv", sep=";")
_sec = pd.read_csv(CARD / "B1_couvert_fontes_secundarias.csv", sep=";")
# "prints transcritos à mão" diz o canal na coluna da URL (foto do Google Maps, destaque do Instagram)
_it["canal"] = [canal(u if f == "prints transcritos à mão" else f) for f, u in zip(_it.formato_fonte, _it.url_cardapio)]
_fo["canal"] = [canal(f"{f} {u}") if f == "prints transcritos à mão" else canal(f) for f, u in zip(_fo.formato, _fo.url)]
_cv = _it[_it.categoria == "couvert ou taxa de jogo"].groupby("place_id").canal.apply(list)
_bmt = _bm[_bm.dado == "taxa de entrada"]
_bm_enc = _bmt[_bmt.situacao == "encontrada"].groupby("place_id").fonte.apply(lambda f: [canal(x) for x in f])
_bm_evento = set(_bmt[_bmt.situacao.str.startswith(("só em evento", "sem cobrança"))].place_id)
SO_EVENTO = "só em evento ou sem cobrança declarada"


def onde_couvert(pid):
    if pid in _cv.index:
        return melhor(_cv[pid])
    if pid in _bm_enc.index:
        return melhor(_bm_enc[pid])
    if pid in set(_sec.place_id):
        return ONDE["outra"]
    return SO_EVENTO if pid in _bm_evento else "não encontrado"


_fo_casa = _fo.groupby("place_id").canal.apply(list)
base["onde_couvert"] = base.place_id.map(onde_couvert)
base["couvert_na_cesta"] = base.place_id.isin(_cv.index).astype(int)
base["onde_cardapio"] = [melhor(_fo_casa[p]) if (p in _fo_casa.index and t == 1) else "não encontrado ou não transcrito"
                         for p, t in zip(base.place_id, base.tem_cardapio)]
_ac = pd.read_excel(DADOS_AGREGADOS / "B1_estabelecimentos" / "B1_resumo_estabelecimentos.xlsx",
                    sheet_name="estabelecimentos").set_index("place_id")
PLATAFORMA = {"acervodejogos", "ludopedia", "rejoy"}
base["onde_acervo"] = [("plataforma de acervo (Acervo de Jogos, Ludopedia, Rejoy)" if f in PLATAFORMA else
                        "site da casa ou da marca") if isinstance(f, str) else "não encontrado"
                       for f in base.place_id.map(_ac.fonte_acervo)]
_ap = pd.read_csv(DADOS_AGREGADOS / "B1_estabelecimentos" / "3_triagem" / "B1_instagram_aprovadas.csv", sep=None,
                  engine="python").drop_duplicates("place_id").set_index("place_id").site_ou_rede_social
REDE = ("instagram.com", "facebook.com", "linktr.ee", "anota.ai")
base["onde_site"] = ["sem site no Google Maps" if not isinstance(u, str) else
                     "rede social ou página de links no lugar do site" if any(r in u for r in REDE) else
                     "site próprio (link do Google Maps)" for u in base.place_id.map(_ap)]
COLS += [("onde_couvert", "couvert: onde foi encontrado", "txt"), ("couvert_na_cesta", "couvert na cesta", "int"),
         ("onde_cardapio", "cardápio: onde foi encontrado", "txt"), ("onde_acervo", "acervo: onde foi encontrado", "txt"),
         ("onde_site", "site", "txt")]
COLS = COLS + COLS_SO_COMPLETA
base = base.sort_values(["regiao", "metropole", "nome"]).reset_index(drop=True)
N = len(base)
LETRA = {c: get_column_letter(i) for i, (c, _, _) in enumerate(COLS, 1)}
ABA_BASE = "Dados B1"


def R(col):
    return f"'{ABA_BASE}'!${LETRA[col]}$3:${LETRA[col]}${N + 2}"


ORDEM_REG = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]


def mediana_se(col, crit_col, crit_ref):
    return ArrayFormula("A1", f'=IFERROR(MEDIAN(IF({R(crit_col)}={crit_ref},IF({R(col)}<>"",{R(col)}))),"")')


FONTE_B1 = "B1, Google Places API (09/2026 e 15/10/2026), coletor de entorno do Google Maps (15/10/2026), Instagram (01/07 a 01/11/2026) e cardápios"

# Tab 1: casas por região e metrópole
cont = base.groupby(["regiao", "metropole"]).size().reset_index(name="n")
cont["ord"] = cont.regiao.map(ORDEM_REG.index)
cont = cont.sort_values(["ord", "n", "metropole"], ascending=[True, False, True])
linhas_t1 = []
for k, r in enumerate(cont.itertuples(), 3):
    linhas_t1.append([r.regiao, r.metropole, f'=COUNTIF({R("metropole")},B{k})', f"=C{k}/C${3 + len(cont)}"])
tot = 3 + len(cont)
linhas_t1.append(["Total", "", f"=SUM(C3:C{tot - 1})", f"=SUM(D3:D{tot - 1})"])
linhas_t1.append(["Conferência (total − casas da base; deve ser 0)", "", f'=C{tot}-COUNTA({R("nome")})', ""])
c1 = cont.sort_values("n", ascending=False)
g1 = barras_h("01_casas_por_metropole", c1.metropole.tolist(), {"casas": c1.n.tolist()}, lambda v: br(v, 0),
              destaque="Salvador")
nova_aba("Tab 1", "Tabela 1 – Luderias por região e metrópole",
         ["Região", "Metrópole", "Casas", "% do total"], linhas_t1, ["cen", "txt", "int", "pct"], FONTE_B1,
         [16, 20, 10, 12], g1, ["Nota: cada casa conta uma vez, na metrópole do endereço."],
         nome="Luderias por região e metrópole")

# Tab 2: estatística descritiva geral
VARS_DESC = [
    ("Google Maps", "avaliacao_media", "Nota média no Google (1 a 5)"),
    ("Google Maps", "volume_avaliacoes", "Avaliações no Google"),
    ("Horários", "dias_abertos", "Dias abertos por semana"),
    ("Horários", "horas_semana", "Horas abertas por semana"),
    ("Horários", "abre_cedo_h", "Abertura mais cedo (hora do dia)"),
    ("Horários", "fecha_tarde_h", "Fechamento mais tarde (25 = 1h)"),
    ("Entorno (Maps)", "metro_500m", "Estações de metrô até 500 m"),
    ("Entorno (Maps)", "metro_1000m", "Estações de metrô até 1000 m"),
    ("Entorno (Maps)", "dist_metro_m", "Distância ao metrô mais próximo (m)"),
    ("Entorno (Maps)", "dist_shopping_m", "Distância ao shopping mais próximo (m)"),
    ("Instagram", "seguidores", "Seguidores"),
    ("Instagram", "n_posts_total", "Posts desde a criação do perfil"),
    ("Instagram", "idade_perfil_anos", "Idade do perfil (anos)"),
    ("Instagram", "n_posts_periodo", "Posts de 01/07 a 01/11/2026"),
    ("Instagram", "interacoes_por_post", "Interações por post"),
    ("Instagram", "engajamento_pct", "Engajamento (interações por post ÷ seguidores)"),
    ("Cardápio", "itens_com_preco", "Itens com preço no cardápio"),
    ("Cardápio", "couvert_mediana", "Couvert ou taxa de jogo (R$, casas que cobram)"),
    ("Cardápio", "bebida_mediana", "Bebida, mediana do cardápio (R$)"),
    ("Cardápio", "entrada_ou_prato_mediana", "Entrada ou prato, mediana (R$)"),
    ("Cardápio", "consumo_baixa", "Consumo por pessoa (bebida + entrada ou prato), nível baixo (R$)"),
    ("Cardápio", "consumo_mediana", "Consumo por pessoa (bebida + entrada ou prato), nível mediano (R$)"),
    ("Cardápio", "consumo_alta", "Consumo por pessoa (bebida + entrada ou prato), nível alto (R$)"),
    ("Cardápio", "cesta_baixa", "Cesta completa (consumo + couvert encontrado), nível baixo (R$)"),
    ("Cardápio", "cesta_mediana", "Cesta completa (consumo + couvert encontrado), nível mediano (R$)"),
    ("Cardápio", "cesta_alta", "Cesta completa (consumo + couvert encontrado), nível alto (R$)"),
    ("Acervo", "titulos_acervo", "Títulos no acervo publicado"),
]
linhas_t2 = []
for g, v, d in VARS_DESC:
    rg = R(v)
    linhas_t2.append([g, d, f"=COUNT({rg})", f"=ROWS({rg})-COUNT({rg})", f'=IFERROR(AVERAGE({rg}),"")',
                      f'=IFERROR(MEDIAN({rg}),"")', f'=IFERROR(STDEV({rg}),"")', f'=IFERROR(MIN({rg}),"")',
                      f'=IFERROR(PERCENTILE({rg},0.25),"")', f'=IFERROR(PERCENTILE({rg},0.75),"")',
                      f'=IFERROR(MAX({rg}),"")'])
nova_aba("Tab 2", f"Tabela 2 – Estatística descritiva das {N} casas",
         ["Grupo", "Variável", "n (com dado)", "Sem dado", "Média", "Mediana", "Desvio padrão", "Mínimo",
          "1º quartil", "3º quartil", "Máximo"],
         linhas_t2, ["cen", "txt", "int", "int"] + ["dec"] * 7, FONTE_B1, [16, 42] + [11] * 9, nome="Estatística descritiva",
         notas=["Nota: desvio padrão amostral; quartis pelo método inclusivo. Engajamento em fração (0,01 = 1%).",
                "Entorno sem OpenStreetMap: shoppings de porte fora. Distância ao metrô vazia onde a cidade não tem metrô lido (Curitiba, Florianópolis, Belém, Goiânia, Vitória)."])

# Tab 3: dias de funcionamento
DIAS = [("abre_segunda", "Segunda"), ("abre_terca", "Terça"), ("abre_quarta", "Quarta"), ("abre_quinta", "Quinta"),
        ("abre_sexta", "Sexta"), ("abre_sabado", "Sábado"), ("abre_domingo", "Domingo")]
linhas_t3 = [[d, f"=COUNTIF({R(c)},1)", f"=COUNT({R(c)})", f"=B{k}/C{k}"] for k, (c, d) in enumerate(DIAS, 3)]
pct_dias = [base[c].sum() / base[c].count() for c, _ in DIAS]
g3 = barras_v("03_dias_funcionamento", [d for _, d in DIAS], {"% das casas que abrem": pct_dias},
              lambda v: br(v * 100, 1, suf="%"), eixo_pct=True, ymax=1.12)
nova_aba("Tab 3", "Tabela 3 – Dias de funcionamento: todas abrem de quinta a sábado; só 28% abrem na segunda",
         ["Dia", "Casas que abrem", "Casas com horário", "% das casas"], linhas_t3, ["txt", "int", "int", "pct"],
         "B1, Google Places API (regularOpeningHours, 15/10/2026)", [18, 14, 14, 12], g3,
         ["Nota: contagem não exclusiva (cada casa abre em vários dias); cada linha tem o próprio total."],
         nome="Dias de funcionamento")

# Tab 4 e 5: painéis por região e por metrópole
PAINEL_CAB = ["casas", "nota (mediana)", "horas abertas por semana (média)", "abre domingo (%)",
              "abre segunda (%)", "metrô até 1000 m (% das casas)", "seguidores (mediana)",
              "casas com consumo", "consumo mediano (mediana, R$)", "casas com cesta completa",
              "cesta completa mediana (mediana, R$)"]
PAINEL_TIPOS = ["int", "dec", "dec", "pct", "pct", "pct", "int", "int", "dec", "int", "dec"]


def painel(chave, ref):
    return [
        f'=COUNTIF({R(chave)},{ref})',
        mediana_se("avaliacao_media", chave, ref),
        f'=IFERROR(AVERAGEIFS({R("horas_semana")},{R(chave)},{ref}),"")',
        f'=IFERROR(AVERAGEIFS({R("abre_domingo")},{R(chave)},{ref}),"")',
        f'=IFERROR(AVERAGEIFS({R("abre_segunda")},{R(chave)},{ref}),"")',
        f'=IFERROR(COUNTIFS({R(chave)},{ref},{R("metro_1000m")},">0")/COUNTIF({R(chave)},{ref}),"")',
        mediana_se("seguidores", chave, ref),
        f'=COUNTIFS({R(chave)},{ref},{R("consumo_mediana")},"<>")',
        mediana_se("consumo_mediana", chave, ref),
        f'=COUNTIFS({R(chave)},{ref},{R("cesta_mediana")},"<>")',
        mediana_se("cesta_mediana", chave, ref),
    ]


linhas_t4 = [[r] + painel("regiao", f"$A{k}") for k, r in enumerate(ORDEM_REG, 3)]
linhas_t4.append(["Total", f"=SUM(B3:B7)", f'=MEDIAN({R("avaliacao_media")})', f'=AVERAGE({R("horas_semana")})',
                  f'=AVERAGE({R("abre_domingo")})', f'=AVERAGE({R("abre_segunda")})',
                  f'=COUNTIF({R("metro_1000m")},">0")/COUNTA({R("nome")})', f'=MEDIAN({R("seguidores")})',
                  f'=COUNT({R("consumo_mediana")})', f'=MEDIAN({R("consumo_mediana")})',
                  f'=COUNT({R("cesta_mediana")})', f'=MEDIAN({R("cesta_mediana")})'])
por_reg = base.groupby("regiao")
g4 = barras_h("04_regiao_funcionamento_metro", ORDEM_REG, {
    "abre domingo": [por_reg.abre_domingo.mean()[r] for r in ORDEM_REG],
    "abre segunda": [por_reg.abre_segunda.mean()[r] for r in ORDEM_REG],
    "metrô até 1000 m": [(por_reg.metro_1000m.apply(lambda s: (s > 0).sum()) / por_reg.size())[r] for r in ORDEM_REG],
}, lambda v: br(v * 100, 1, suf="%"), eixo_pct=True, xmax=1.18)
NOTA_CESTA = ("Consumo = bebida + entrada ou prato, nas casas com os dois no cardápio; cesta completa = consumo + couvert, "
              "só nas casas com couvert encontrado (couvert não encontrado não entra como 0).")
nova_aba("Tab 4", "Tabela 4 – Painel por região",
         ["Região"] + PAINEL_CAB, linhas_t4, ["txt"] + PAINEL_TIPOS, FONTE_B1, [16] + [13] * 11, g4,
         ["Nota: medianas calculadas só entre as casas com dado. " + NOTA_CESTA], nome="Painel por região")

metros = cont.sort_values(["ord", "metropole"])
linhas_t5 = [[r.metropole, r.regiao] + painel("metropole", f"$A{k}") for k, r in enumerate(metros.itertuples(), 3)]
fim5 = 2 + len(linhas_t5)
linhas_t5.append(["Total", "", f"=SUM(C3:C{fim5})", f'=MEDIAN({R("avaliacao_media")})', f'=AVERAGE({R("horas_semana")})',
                  f'=AVERAGE({R("abre_domingo")})', f'=AVERAGE({R("abre_segunda")})',
                  f'=COUNTIF({R("metro_1000m")},">0")/COUNTA({R("nome")})', f'=MEDIAN({R("seguidores")})',
                  f'=COUNT({R("consumo_mediana")})', f'=MEDIAN({R("consumo_mediana")})',
                  f'=COUNT({R("cesta_mediana")})', f'=MEDIAN({R("cesta_mediana")})'])
cm = base.groupby("metropole").consumo_mediana.median().dropna().sort_values(ascending=False)
g5 = barras_h("05_consumo_mediano_por_metropole", cm.index.tolist(), {"consumo mediano": cm.tolist()},
              lambda v: br(v, 2, pre="R$ "), destaque="Salvador")
nova_aba("Tab 5", "Tabela 5 – Painel por metrópole: o consumo por pessoa varia de metrópole para metrópole",
         ["Metrópole", "Região"] + PAINEL_CAB, linhas_t5, ["txt", "cen"] + PAINEL_TIPOS, FONTE_B1,
         [18, 14] + [13] * 11, g5,
         ["Nota: o gráfico mostra a mediana do consumo mediano das casas com consumo em cada metrópole; metrópoles sem consumo ficam fora.",
          NOTA_CESTA], nome="Painel por metrópole")

# Tab 6: entorno (só Google Maps)
FAIXAS = [("Até 500 m", '"<=500"', None), ("De 501 a 1000 m", '">500"', '"<=1000"'),
          ("De 1001 a 2000 m", '">1000"', '"<=2000"'), ("Mais de 2000 m", '">2000"', None)]
linhas_t6 = []
for k, (rot, a, b) in enumerate(FAIXAS, 3):
    cel = []
    for col in ("dist_metro_m", "dist_shopping_m"):
        cel.append(f"=COUNTIFS({R(col)},{a}" + (f",{R(col)},{b})" if b else ")"))
    linhas_t6.append([rot, cel[0], f"=B{k}/B$9", cel[1], f"=D{k}/D$9"])
linhas_t6.append(["Sem leitura (cidade sem metrô ou leitura a mais de 50 km)",
                  f'=COUNTA({R("nome")})-COUNT({R("dist_metro_m")})', "=B7/B$9",
                  f'=COUNTA({R("nome")})-COUNT({R("dist_shopping_m")})', "=D7/D$9"])
linhas_t6.append(["Conferência (total − casas; deve ser 0)", f'=B9-COUNTA({R("nome")})', "",
                  f'=D9-COUNTA({R("nome")})', ""])
linhas_t6.append(["Total", "=SUM(B3:B7)", "=SUM(C3:C7)", "=SUM(D3:D7)", "=SUM(E3:E7)"])


def faixa(s):
    s = s.dropna()
    return [(s <= 500).sum(), ((s > 500) & (s <= 1000)).sum(), ((s > 1000) & (s <= 2000)).sum(), (s > 2000).sum()]


fm, fs = faixa(base.dist_metro_m), faixa(base.dist_shopping_m)
nm, ns = N - base.dist_metro_m.count(), N - base.dist_shopping_m.count()
g6 = empilhado_100("06_entorno_distancias", ["Estação de metrô", "Shopping"],
                   {rot: [fm[i] if i < 4 else nm, fs[i] if i < 4 else ns]
                    for i, rot in enumerate([f[0] for f in FAIXAS] + ["Sem leitura"])})
nova_aba("Tab 6", "Tabela 6 – Entorno pelo Google Maps: a maioria das casas tem shopping a até 1 km; metrô perto é minoria",
         ["Distância (linha reta)", "Metrô: casas", "Metrô: %", "Shopping: casas", "Shopping: %"], linhas_t6,
         ["txt", "int", "pct", "int", "pct"], "B1, coletor de entorno do Google Maps (15/10/2026)",
         [44, 13, 11, 14, 12], g6,
         ["Nota: sem dados do OpenStreetMap (porte do shopping fora). Shopping de qualquer porte lido pelo Maps."],
         nome="Entorno pelo Google Maps")

# Tab 7: preços do cardápio
CATS = [("couvert_mediana", "Couvert ou taxa de jogo (casas que cobram)"), ("bebida_mediana", "Bebida"),
        ("entrada_ou_prato_mediana", "Entrada ou prato"), ("hamburguer_mediana", "Hambúrguer"),
        ("batata_mediana", "Batata"), ("cerveja_mediana", "Cerveja"), ("refrigerante_mediana", "Refrigerante"),
        ("drinks_mediana", "Drinks"), ("consumo_baixa", "Consumo por pessoa, nível baixo"),
        ("consumo_mediana", "Consumo por pessoa, nível mediano"), ("consumo_alta", "Consumo por pessoa, nível alto"),
        ("cesta_baixa", "Cesta completa, nível baixo"), ("cesta_mediana", "Cesta completa, nível mediano"),
        ("cesta_alta", "Cesta completa, nível alto")]
linhas_t7 = [[d, f"=COUNT({R(c)})", f'=IFERROR(PERCENTILE({R(c)},0.25),"")', f'=IFERROR(MEDIAN({R(c)}),"")',
              f'=IFERROR(PERCENTILE({R(c)},0.75),"")'] for c, d in CATS]
g7 = barras_h("07_precos_cardapio", [d for _, d in CATS], {"mediana entre as casas": [base[c].median() for c, _ in CATS]},
              lambda v: br(v, 2, pre="R$ "), larg_rotulo=26)
nova_aba("Tab 7", "Tabela 7 – Preços nos cardápios",
         ["Categoria", "Casas com preço", "1º quartil (R$)", "Mediana (R$)", "3º quartil (R$)"], linhas_t7,
         ["txt", "int", "dec", "dec", "dec"], "B1, cardápios transcritos (B1_cardapios_itens_precos.xlsx)",
         [42, 14, 14, 14, 14], g7,
         ["Nota: cada casa entra com a mediana do próprio cardápio na categoria; quartis entre as casas.",
          NOTA_CESTA], nome="Preços nos cardápios")

# Tab 8: onde couvert, cardápio, acervo e site foram encontrados (pedido do autor, 25/11/2026)
BLOCOS8 = [
    ("Couvert ou taxa de entrada", "onde_couvert",
     [ONDE[c] for c in PRIOR] + [SO_EVENTO, "não encontrado"]),
    ("Cardápio", "onde_cardapio", [ONDE[c] for c in PRIOR] + ["não encontrado ou não transcrito"]),
    ("Acervo de jogos", "onde_acervo",
     ["plataforma de acervo (Acervo de Jogos, Ludopedia, Rejoy)", "site da casa ou da marca", "não encontrado"]),
    ("Site", "onde_site", ["site próprio (link do Google Maps)", "rede social ou página de links no lugar do site",
                           "sem site no Google Maps"]),
]
for _, col, cats in BLOCOS8:
    sobra = set(base[col]) - set(cats)
    assert not sobra, (col, sobra)
linhas_t8, r8, NC = [], 3, f'COUNTA({R("nome")})'
for bloco, col, cats in BLOCOS8:
    ini = r8
    for c in cats:
        cesta = (f'=COUNTIFS({R(col)},A{r8},{R("couvert_na_cesta")},1)'.replace(f",A{r8},", f",B{r8},") if col == "onde_couvert" else "")
        linhas_t8.append([bloco if r8 == ini else "", c, f'=COUNTIF({R(col)},B{r8})', f"=C{r8}/{NC}", cesta])
        r8 += 1
    linhas_t8.append([f"Total – {bloco.lower()}", "", f"=SUM(C{ini}:C{r8 - 1})", f"=SUM(D{ini}:D{r8 - 1})",
                      f"=SUM(E{ini}:E{r8 - 1})" if col == "onde_couvert" else ""])
    r8 += 1
linhas_t8.append(["Conferência (cada total − casas; deve ser 0)", "",
                  "=" + "+".join(f"ABS(C{k}-{NC})" for k, l in enumerate(linhas_t8, 3) if str(l[0]).startswith("Total")),
                  "", ""])
NAO8 = {"não encontrado", "não encontrado ou não transcrito", SO_EVENTO, "sem site no Google Maps",
        "rede social ou página de links no lugar do site"}
g8 = barras_h("08_onde_encontrado", [bl for bl, _, _ in BLOCOS8],
              {"% das casas com o dado encontrado": [(~base[col].isin(NAO8)).mean() for _, col, _ in BLOCOS8]},
              lambda v: br(v * 100, 1, suf="%"), eixo_pct=True, larg_rotulo=20)
nova_aba("Tab 8", "Tabela 8 – Onde couvert, cardápio, acervo e site foram encontrados",
         ["Dado", "Onde foi encontrado", "Casas", "% das casas", "Couvert na cesta completa"], linhas_t8,
         ["cen", "txt", "int", "pct", "int"],
         "B1, cardápios transcritos (B1_cardapios_itens_precos.xlsx), busca minuciosa de taxa, cardápio e acervo, "
         "fontes secundárias do couvert, acervos publicados e site no Google Maps (Places API)",
         [16, 48, 9, 11, 13], g8,
         ["Nota: cada casa entra em uma só linha de cada bloco, pela fonte de maior prioridade (cardápio, site, "
          "Instagram, fotos, outra fonte). Cada bloco fecha nas 63 casas.".replace("63", str(N)),
          "Nota: só o couvert encontrado junto com o cardápio transcrito entra na cesta completa (Tabelas 2 e 7); "
          "o achado só no Instagram, na imprensa ou na busca minuciosa fica fora dela. \"Não encontrado\" não quer "
          "dizer que a casa não cobra."], nome="Onde os dados foram encontrados")

# ---------------------------------------------------------------- B1: Instagram
LEG = DADOS_AGREGADOS / "B1_redes_sociais" / "analise_legendas"
FONTE_IG = "B1, legendas do Instagram das casas (coletor do Instagram, 2026), análise de legendas"


def n_de(t):
    a, b = str(t).split(" de ")
    return int(a), int(b)


def tabelas_instagram(sub="", suf="", fonte_ig=FONTE_IG):
    """Tabelas 9 a 12 (cobrança, eventos, dias e temas); sub = subpasta do recorte, suf = sufixo das abas e gráficos."""
    mc = pd.read_csv(LEG / "precos" / sub / "B1_instagram_modelos_cobranca.csv", sep=";")
    linhas_t9, gj, gl = [], [], []
    for k, r in enumerate(mc.itertuples(index=False), 3):
        a, b = n_de(r[3])
        c, d = n_de(r[4])
        linhas_t9.append([r[0], r[1], r[2], a, b, f"=D{k}/E{k}", c, d, f"=G{k}/H{k}"])
        gj.append(a / b)
        gl.append(c / d)
    ordem = np.argsort(gj)[::-1]
    g9 = barras_h("09_instagram_modelos_cobranca" + suf, [mc.iloc[i, 0] for i in ordem],
                  {"Casas de jogos": [gj[i] for i in ordem], "Lojas com espaço de jogo": [gl[i] for i in ordem]},
                  lambda v: br(v * 100, 1, suf="%"), eixo_pct=True, xmax=1.2, larg_rotulo=26)
    nova_aba(f"Tab 9{suf}", "Tabela 9 – Modelos de cobrança citados no Instagram: couvert lúdico e inscrição em evento são os mais comuns",
             ["Modelo", "Posts que citam", "Estabelecimentos que citam", "Casas de jogos que citam", "Casas de jogos (total)",
              "Casas de jogos (%)", "Lojas que citam", "Lojas (total)", "Lojas (%)"], linhas_t9,
             ["txt", "int", "int", "int", "int", "pct", "int", "int", "pct"], fonte_ig, [36] + [12] * 8, g9, nome="Cobrança citada no Instagram",
             notas=["Nota: contagem não exclusiva (um post pode citar vários modelos)."])

    ev = pd.read_csv(LEG / "eventos" / sub / "B1_instagram_eventos_por_categoria.csv", sep=";")
    linhas_t10 = []
    for k, r in enumerate(ev.itertuples(index=False), 3):
        a, b = n_de(r[3])
        c, d = n_de(r[5])
        linhas_t10.append([r[0], r[1], r[2], a, b, r[4], c, d, r[6]])
    evg = ev[~ev.iloc[:, 0].str.contains("todos|sorteio")].sort_values(ev.columns[4], ascending=False)
    g10 = barras_h("10_instagram_eventos_categoria" + suf, evg.iloc[:, 0].tolist(),
                   {"Casas de jogos": evg.iloc[:, 4].tolist(), "Lojas com espaço de jogo": evg.iloc[:, 6].tolist()},
                   lambda v: br(v, 2))
    nova_aba(f"Tab 10{suf}", "Tabela 10 – Eventos no Instagram: encontros/RPG, competições e noites temáticas puxam a agenda",
             ["Categoria", "Posts", "Estabelecimentos", "Casas de jogos com o evento", "Casas de jogos (total)",
              "Casas de jogos: posts por casa por mês", "Lojas com o evento", "Lojas (total)", "Lojas: posts por casa por mês"],
             linhas_t10, ["txt", "int", "int", "int", "int", "dec", "int", "int", "dec"], fonte_ig, [30] + [13] * 8, g10, nome="Eventos no Instagram",
             notas=["Nota: categorias não exclusivas; o gráfico mostra posts por casa por mês, sem \"todos os eventos\" e sem sorteio (que não é evento)."])

    dw = pd.read_csv(LEG / "eventos" / sub / "B1_instagram_eventos_dias_da_semana.csv", sep=";")
    linhas_t11 = [[r[0], r[2], r[3] / 100, r[4], r[5], r[6] / 100, r[7]] for r in dw.itertuples(index=False)]
    g11 = barras_v("11_instagram_eventos_dia" + suf, [d.capitalize() for d in dw.iloc[:, 0]],
                   {"Casas de jogos": (dw.iloc[:, 3] / 100).tolist(), "Lojas com espaço de jogo": (dw.iloc[:, 6] / 100).tolist()},
                   lambda v: br(v * 100, 1, suf="%"), eixo_pct=True)
    nova_aba(f"Tab 11{suf}", "Tabela 11 – Dia citado nos eventos: casas de jogos anunciam mais domingo e quinta; lojas, sábado",
             ["Dia", "Casas de jogos: eventos que citam", "Casas de jogos: % dos eventos", "Casas de jogos: estabelecimentos",
              "Lojas: eventos que citam", "Lojas: % dos eventos", "Lojas: estabelecimentos"], linhas_t11,
             ["txt", "int", "pct", "int", "int", "pct", "int"], fonte_ig, [14] + [14] * 6, g11, nome="Dia citado nos eventos",
             notas=["Nota: % sobre os eventos prováveis de cada tipo de casa; um evento pode citar mais de um dia ou nenhum."])

    tf = pd.read_csv(LEG / "temas" / sub / "B1_instagram_temas_frequencia.csv", sep=";")
    tf = tf.iloc[:, [0, 1, 2, 3, 4, 5]]  # só legendas; colunas do B2 ficam fora
    linhas_t12 = [[r[0], r[1], r[2], r[3] / 100, r[4] / 100, r[5]] for r in tf.itertuples(index=False)]
    tg = tf.sort_values(tf.columns[4], ascending=False)
    g12 = barras_h("12_instagram_temas" + suf, tg.iloc[:, 1].tolist(), {"% ponderado por estabelecimento": (tg.iloc[:, 4] / 100).tolist()},
                   lambda v: br(v * 100, 1, suf="%"), eixo_pct=True, larg_rotulo=30)
    nova_aba(f"Tab 12{suf}", "Tabela 12 – Temas das legendas do Instagram: programação, varejo e preço dominam",
             ["Código", "Tema", "Posts com o tema", "% dos posts", "% ponderado por estabelecimento", "Estabelecimentos com o tema"],
             linhas_t12, ["cen", "txt", "int", "pct", "pct", "int"], fonte_ig, [10, 36, 12, 12, 14, 14], g12, nome="Temas das legendas",
             notas=["Nota: temas não exclusivos; o % ponderado dá peso igual a cada estabelecimento. Comparação com o B2 retirada desta planilha."])


tabelas_instagram()
# Versão resumida (pedido do autor, 25/11/2026): as mesmas tabelas só com os posts do recorte da
# estatística descritiva (01/07 a 01/11/2026), rodadas com --recorte em B1a_instagram_*.py.
tabelas_instagram("recorte_2026-07_2026-11", "r",
                  "B1, legendas do Instagram das casas publicadas de 01/07 a 01/11/2026 (coletor do Instagram), análise de legendas")


# ---------------------------------------------------------------- B1: acervo
AC = DADOS_AGREGADOS / "B1_acervo_jogos"
bj = pd.read_csv(AC / "B1_banco_jogos.csv")
cj = pd.read_excel(AC / "B1_cesta_jogos.xlsx", sheet_name="cesta")
top = bj.sort_values(["n_casas_acervo", "jogo"], ascending=[False, True]).head(20).merge(
    cj[["jogo", "preco_provavel_rs"]], on="jogo", how="left")
n_acervos = bj.acervo_no_local.dropna().str.split("; ").explode().nunique()
linhas_t13 = [[r.jogo, r.n_casas_acervo, r.jogadores_min, r.jogadores_max, r.duracao_min, r.preco_provavel_rs,
               r.aluguel_mediana_rs] for r in top.itertuples()]
g13 = barras_h("13_jogos_mais_presentes", top.jogo.tolist(), {"casas com o jogo": top.n_casas_acervo.tolist()},
               lambda v: br(v, 0))
nova_aba("Tab 13", f"Tabela 13 – Os 20 jogos mais presentes nos acervos publicados ({n_acervos} acervos): Catan, Saboteur e Potion Explosion lideram",
         ["Jogo", "Casas com o jogo", "Jogadores (mín.)", "Jogadores (máx.)", "Duração (min)", "Preço provável (R$)",
          "Aluguel (mediana, R$)"], linhas_t13, ["txt", "int", "int", "int", "int", "dec", "dec"],
         "B1, acervos publicados (acervodejogos, Ludopedia, Rejoy e listas das casas) e preços de lojas (B1_cesta_jogos.xlsx)",
         [30, 12, 12, 12, 12, 14, 14], g13, ["Nota: preço vazio = jogo sem preço nas lojas consultadas."],
         nome="Jogos mais presentes")

# Tab 14: curva do custo do acervo (pedido do autor, 25/11/2026): uma linha por mínimo de casas com o
# jogo, do jogo mais presente até passar do 3º quartil dos acervos publicados, com o joelho marcado.
cv = pd.read_excel(AC / "B1_cesta_jogos.xlsx", sheet_name="acervo_curva")
linhas_t14 = [[r.casas_minimas, r.titulos, r.titulos_novos, r.com_preco, r.custo_otimista_rs, r.custo_provavel_rs,
               r.custo_pessimista_rs, r.marco if isinstance(r.marco, str) else ""] for r in cv.itertuples()]
g14 = linhas("14_custo_acervo_curva", cv.titulos.to_numpy(dtype=float),
             {"Pessimista": cv.custo_pessimista_rs.tolist(), "Provável": cv.custo_provavel_rs.tolist(),
              "Otimista": cv.custo_otimista_rs.tolist()},
             lambda v: br(v / 1000, 1, pre="R$ ", suf=" mil"), cores=[SLATE_600, ROXO_700, ROXO_300],
             fmt_eixo=lambda v, _: br(v / 1000, 0, pre="R$ ", suf=" mil"))
jo = cv[cv.marco.fillna("").str.contains("joelho")].iloc[0]
nova_aba("Tab 14", "Tabela 14 – Custo do acervo inicial pelo número de títulos",
         ["Mínimo de casas com o jogo", "Títulos", "Títulos novos", "Títulos com preço", "Custo otimista (R$)",
          "Custo provável (R$)", "Custo pessimista (R$)", "Marco"], linhas_t14,
         ["int", "int", "int", "int", "dec", "dec", "dec", "txt"],
         "B1, acervos publicados e preços de lojas (B1_cesta_jogos.xlsx, aba acervo_curva)", [14, 10, 10, 11, 15, 15, 15, 26],
         g14, [f"Nota: cada linha soma os jogos presentes em pelo menos aquele número de casas, do mais presente ao menos presente. "
               f"Joelho da curva = {int(jo.casas_minimas)} casas ou mais ({int(jo.titulos)} títulos), acervo inicial do plano. "
               "Jogo sem loja entra pelo preço médio por título; otimista e pessimista = provável × (1 ∓ 15%), "
               "o 3º quartil da variação de preço do mesmo jogo entre lojas.",
               "Nota: quartis e mediana marcados pelo tamanho dos acervos publicados das casas."],
         nome="Custo do acervo")

# ---------------------------------------------------------------- B3
rv = pd.read_csv(B3 / "contagem_resumo_visitas.csv", sep=";", encoding="utf-8-sig")
rv = rv[rv.observador != "media"].reset_index(drop=True)
UNID = {"BV": "Bela Vista", "PA": "Paralela"}
rot_vis = [f"{pd.to_datetime(r.visita_inicio):%d/%m} {UNID.get(r.unidade, r.unidade)}" for r in rv.itertuples()]
# Três tabelas (pedido do autor, 25/11/2026): fluxo e circulação, ocupação e tamanho dos grupos, permanência.
FONTE_B3 = ("B3, contagem direta nas unidades da São Jogue (app de observação, "
            + ", ".join(f"{pd.to_datetime(x):%d/%m}" for x in rv.visita_inicio) + "/2026)")
NOTA_B3 = ("Nota: visitas de 2,5 a 3,3 h nas noites de sexta e sábado; 10/10 só com o POV1. Entrada (porta): sem quem "
           "já estava dentro na chegada; mesa: inclui quem já estava sentado.")
nv = len(rv)


def tabela_b3(aba, titulo, nome, vars_, formulas, grafico):
    """Uma tabela do B3: uma linha por medida, uma coluna por visita. formulas: {linha: (num, den)},
    linhas contadas a partir de 0 na ordem de vars_, recalculadas por fórmula a partir das contagens."""
    lin = [[d] + [rv.loc[i, c] for i in range(nv)] for c, d, _ in vars_]
    for k, (num, den) in formulas.items():
        for i in range(nv):
            L = get_column_letter(2 + i)
            lin[k][1 + i] = f"=IFERROR({L}{3 + num}/{L}{3 + den},\"\")"
    nova_aba(aba, titulo, ["Medida"] + rot_vis, lin, ["txt"] + ["dec"] * nv, FONTE_B3, [38] + [16] * nv, grafico,
             [NOTA_B3], nome=nome)
    for r, (_, _, t) in enumerate(vars_, 3):
        for j in range(2, 2 + nv):
            wb[aba].cell(r, j).number_format = FMT[t]


g15a = barras_v("15a_b3_fluxo", rot_vis, {"pessoas por hora": (rv.pessoas_entraram / rv.horas_observadas).tolist()},
                lambda v: br(v, 1))
tabela_b3("Tab 15a", "Tabela 15 – Fluxo e circulação na São Jogue", "Fluxo e circulação",
          [("horas_observadas", "Horas observadas", "dec"), ("grupos_porta", "Grupos que entraram (porta)", "int"),
           ("pessoas_entraram", "Pessoas que entraram", "int"), ("pessoas_por_hora", "Pessoas por hora", "dec")],
          {3: (2, 0)}, g15a)
g15b = barras_v("15b_b3_grupos", rot_vis,
                {"pela porta": rv.tamanho_grupo_porta.tolist(), "na mesa": (rv.pessoas_mesa / rv.grupos_mesa).tolist()},
                lambda v: br(v, 1))
tabela_b3("Tab 15b", "Tabela 16 – Ocupação e tamanho dos grupos na São Jogue", "Ocupação e tamanho dos grupos",
          [("grupos_mesa", "Grupos acompanhados na mesa", "int"), ("pessoas_mesa", "Pessoas nas mesas", "int"),
           ("tamanho_grupo_mesa", "Pessoas por grupo (mesa)", "dec"),
           ("tamanho_grupo_porta", "Pessoas por grupo (porta)", "dec")],
          {2: (1, 0)}, g15b)
g15c = barras_v("15c_b3_permanencia", rot_vis,
                {"pela porta (média)": rv.permanencia_porta_media_min.tolist(),
                 "na mesa (média)": rv.permanencia_mesa_media_min.tolist(),
                 "na mesa (mediana)": rv.permanencia_mesa_mediana_min.tolist()},
                lambda v: br(v, 0, suf=" min"))
tabela_b3("Tab 15c", "Tabela 17 – Permanência na São Jogue", "Permanência",
          [("permanencia_porta_media_min", "Permanência média pela porta (min)", "dec"),
           ("permanencia_mesa_media_min", "Permanência média na mesa (min)", "dec"),
           ("permanencia_mesa_mediana_min", "Permanência mediana na mesa (min)", "dec")],
          {}, g15c)

# ---------------------------------------------------------------- B4
CAP_B1 = sorted(base.metropole.unique())
# Tab 16: município e região metropolitana lado a lado (pedido do autor, 25/11/2026: a capital sozinha
# subestima Vitória e Florianópolis); renda habitual do trabalho retirada (nenhum capítulo a usa).
B4M = DADOS_AGREGADOS / "B4_marketing"
rp = pd.read_csv(B4M / "[B4] Resumo de População e Renda por Capital 2022-2026 (IBGE).csv")
rm = pd.read_csv(B4M / "[B4] Resumo de População e Renda por Região Metropolitana 2022-2026 (IBGE).csv").set_index("metropole")
COD_MUN = dict(zip(rp.capital, rp.codigo_ibge)) | {"Campinas": 3509502}
UF_MUN = dict(zip(rp.capital, rp.uf)) | {"Campinas": "SP"}
_p22 = pd.read_csv(B4M / "[B4] População Residente dos Municípios das RMs 2022 (IBGE Censo).csv").set_index("localidade_id").valor
_p26 = pd.read_csv(B4M / "[B4] População Estimada por Município 2026 (IBGE).csv").set_index("localidade_id").valor
_id = pd.read_csv(B4M / "[B4] População por Idade dos Municípios das RMs 2022 (IBGE Censo).csv").groupby("localidade_id").valor.sum()
_re = pd.read_csv(B4M / "[B4] Renda dos Municípios das RMs 2022 (IBGE Censo).csv")
_med = _re[_re.variavel_id == 13502].set_index("localidade_id").valor
_mdn = _re[_re.variavel_id == 13503].set_index("localidade_id").valor
linhas_t16 = []
for m in CAP_B1:
    c = COD_MUN[m]
    r = rm.loc[m]
    linhas_t16.append([m, UF_MUN[m], _p22[c], _p26[c], _id[c], _med[c], _mdn[c],
                       r.municipios, r.pop_censo_2022_rm, r.pop_estimada_2026_rm, r.pop_20_39_censo_2022_rm,
                       r.renda_media_14mais_censo_2022_rm])
linhas_t16.sort(key=lambda l: -l[9])
for k, l in enumerate(linhas_t16, 3):
    l.insert(5, f"=E{k}/C{k}")       # % de 20 a 39 anos no município
    l.insert(12, f"=L{k}/J{k}")      # % de 20 a 39 anos na RM (colunas já deslocadas)
    l.append(f"=K{k}/D{k}")          # RM ÷ município, 2026
k16 = 3 + len(linhas_t16)
linhas_t16.append(["Conferência (Salvador, RM 2026 − cap. 5; deve ser 0)", "", "", "", "", "", "", "", "", "", "",
                   "", "", "", f'=SUMIF(A3:A{k16 - 1},"Salvador",K3:K{k16 - 1})-3623067'])
g16 = barras_h("16_populacao_rm", [l[0] for l in linhas_t16[:-1]],
               {"Município": [l[3] for l in linhas_t16[:-1]], "Região metropolitana": [l[10] for l in linhas_t16[:-1]]},
               lambda v: br(v / 1e6, 1, suf=" mi"), cores=[ROXO_300, ROXO_700], larg_rotulo=16)
nova_aba("Tab 16", "Tabela 16 – População e renda das metrópoles do B1, no município e na região metropolitana",
         ["Metrópole", "UF", "Município: população 2022", "Município: população estimada 2026",
          "Município: 20 a 39 anos (2022)", "Município: % de 20 a 39 anos", "Município: renda média (2022, R$)",
          "Município: renda mediana (2022, R$)", "RM: municípios", "RM: população 2022", "RM: população estimada 2026",
          "RM: 20 a 39 anos (2022)", "RM: % de 20 a 39 anos", "RM: renda média (2022, R$)", "RM ÷ município (2026)"],
         linhas_t16, ["txt", "cen", "int", "int", "int", "pct", "dec", "dec", "int", "int", "int", "int", "pct", "dec", "dec"],
         "B4, IBGE: Censo 2022 (tabelas 4709, 9514 e 10299), estimativas de população 2026 (tabela 6579) e "
         "composição das regiões metropolitanas (2025)", [18, 6, 13, 13, 13, 11, 13, 13, 10, 13, 13, 13, 11, 13, 11], g16,
         notas=["Nota: RM = soma dos municípios da região metropolitana (ou RIDE, em Brasília) na composição do IBGE de 2025. "
                "Renda das pessoas de 14 anos ou mais; a média da RM pondera os municípios pelas pessoas de 14 anos ou mais. "
                "A mediana não se soma entre municípios e fica só no município."],
         nome="População e renda das metrópoles")

al = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Aluguel Comercial por Capital 2026-07 (FipeZap).csv")
al = al[al.capital.isin(CAP_B1)].copy()
al["valor"] = al.comercial_locacao_preco_m2.fillna(al.comercial_estimado_preco_m2_mediana)
al["origem"] = np.where(al.comercial_locacao_preco_m2.notna(), "FipeZap comercial",
                        "estimado (residencial × razão comercial/residencial)")
al = al.sort_values("valor", ascending=False)
linhas_t17 = [[r.capital, r.uf, r.comercial_locacao_preco_m2, r.comercial_estimado_preco_m2_mediana,
               f"=IF(C{k}<>\"\",C{k},D{k})", r.comercial_locacao_var_12m_pct / 100 if pd.notna(r.comercial_locacao_var_12m_pct) else None,
               r.origem] for k, r in enumerate(al.itertuples(), 3)]
g17 = barras_h("17_aluguel_comercial", al.capital.tolist(), {"R$/m²": al.valor.tolist()},
               lambda v: br(v, 2, pre="R$ "), destaque="Salvador")
nova_aba("Tab 17", "Tabela 17 – Aluguel comercial por m²: Salvador está entre as capitais mais caras do grupo",
         ["Capital", "UF", "Locação comercial (R$/m²)", "Estimativa, mediana (R$/m²)", "Valor usado (R$/m²)",
          "Variação em 12 meses", "Origem do valor"], linhas_t17, ["txt", "cen", "dec", "dec", "dec", "pct", "txt"],
         "B4, FipeZap (índice de locação comercial e residencial, julho de 2026)", [18, 6, 14, 14, 13, 12, 40], g17, nome="Aluguel comercial por m²",
         notas=["Nota: onde o FipeZap não cobre o comercial, estimativa pelo residencial vezes a razão comercial/residencial das capitais cobertas."])

sa = pd.read_csv(DADOS_AGREGADOS / "B4_multiuso" / "[B4] Salário Admissão por Capital 2025-2026 (CAGED).csv")
sa = sa[sa.recorte == "CNAE 56 - alimentação"]
ssa = sa[sa.capital == "Salvador"].set_index("ocupacao")
sbr = sa[sa.capital == "27 capitais"].set_index("ocupacao")
ocup = ssa.salario_mediana.sort_values(ascending=False).index.tolist()
linhas_t18 = [[o, ssa.loc[o, "admissoes"], ssa.loc[o, "salario_mediana"], sbr.loc[o, "admissoes"],
               sbr.loc[o, "salario_mediana"], f"=C{k}/E{k}", "sim" if ssa.loc[o, "amostra_pequena"] else "não"]
              for k, o in enumerate(ocup, 3)]
g18 = barras_h("18_salario_admissao", ocup, {"Salvador": [ssa.loc[o, "salario_mediana"] for o in ocup],
                                             "27 capitais": [sbr.loc[o, "salario_mediana"] for o in ocup]},
               lambda v: br(v, 0, pre="R$ "), larg_rotulo=24)
nova_aba("Tab 18", "Tabela 18 – Salário de admissão em alimentação: Salvador paga perto do salário mínimo e abaixo das capitais",
         ["Ocupação", "Salvador: admissões", "Salvador: salário mediano (R$)", "27 capitais: admissões",
          "27 capitais: salário mediano (R$)", "Salvador ÷ 27 capitais", "Amostra pequena em Salvador"], linhas_t18,
         ["txt", "int", "dec", "int", "dec", "pct", "cen"],
         "B4, Novo CAGED (admissões de 08/2025 a 07/2026, CNAE 56 – alimentação)", [34, 12, 14, 12, 14, 12, 12], g18, nome="Salário de admissão")

sn = pd.read_csv(DADOS_AGREGADOS / "B4_juridico" / "[B4] Faixas e Alíquotas por Anexo 2026 (Simples Nacional).csv")
sn = sn[sn.anexo.isin(["I", "III"])]
linhas_t19 = [[r.anexo, r.faixa, r.rbt12_min, r.rbt12_max, r.aliquota_nominal_pct / 100, r.parcela_deduzir,
               f"=IFERROR((D{k}*E{k}-F{k})/D{k},\"\")"] for k, r in enumerate(sn.itertuples(), 3)]
x19 = [f"Faixa {f}" for f in sn[sn.anexo == "I"].faixa]
efet = lambda a: ((sn[sn.anexo == a].rbt12_max * sn[sn.anexo == a].aliquota_nominal_pct / 100 - sn[sn.anexo == a].parcela_deduzir)
                  / sn[sn.anexo == a].rbt12_max).tolist()
g19 = barras_v("19_simples_aliquota_efetiva", x19, {"Anexo I (A&B)": efet("I"), "Anexo III (couvert e eventos)": efet("III")},
               lambda v: br(v * 100, 1, suf="%"), eixo_pct=True)
nova_aba("Tab 19", "Tabela 19 – Simples Nacional, anexos I e III: alíquota efetiva no teto de cada faixa",
         ["Anexo", "Faixa", "Receita bruta em 12 meses, de (R$)", "Até (R$)", "Alíquota nominal", "Parcela a deduzir (R$)",
          "Alíquota efetiva no teto da faixa"], linhas_t19, ["cen", "int", "dec", "dec", "pct", "dec", "pct"],
         "B4, Lei Complementar 123/2006, anexos I e III (Simples Nacional, 2026)", [8, 7, 18, 16, 12, 16, 16], g19, nome="Simples Nacional",
         notas=["Nota: alíquota efetiva = (receita × alíquota nominal − parcela a deduzir) ÷ receita."])

bc = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Selic IPCA e Salário Mínimo 2017-2026 (BCB).csv", parse_dates=["data"])
fo = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Expectativas Focus 2026-2030 (BCB).csv")
DATA_FOCUS = pd.to_datetime(fo["Data"]).max().strftime("%d/%m/%Y")  # data do relatório Focus coletado
anual = {}
for serie, rot in (("selic_meta", "selic"), ("ipca_acumulado_12_meses", "ipca")):
    s = bc[bc.serie == serie].sort_values("data")
    s = s.groupby(s.data.dt.year).last()
    for ano, r in s.iterrows():
        anual.setdefault(ano, {})[rot] = r.valor
        anual[ano][f"{rot}_data"] = r.data
linhas_t20 = []
for ano in sorted(anual):
    a = anual[ano]
    linhas_t20.append([str(ano), "realizado", a.get("selic", np.nan) / 100, a.get("ipca", np.nan) / 100,
                       f"Selic {a['selic_data']:%m/%Y}; IPCA {a['ipca_data']:%m/%Y}"])
for ano in range(int(max(anual)), 2031):
    f_s = fo[(fo.Indicador == "Selic") & (fo.DataReferencia == ano)]
    f_i = fo[(fo.Indicador == "IPCA") & (fo.DataReferencia == ano)]
    if len(f_s) and len(f_i):
        linhas_t20.append([str(ano), "Focus (mediana)", f_s.Mediana.iloc[0] / 100, f_i.Mediana.iloc[0] / 100, DATA_FOCUS])
real = [l for l in linhas_t20 if l[1] == "realizado"]
proj = [l for l in linhas_t20 if l[1] != "realizado"]
anos = [int(l[0]) for l in real] + [int(l[0]) + 0.0 for l in proj if int(l[0]) > int(real[-1][0])]
sel = [l[2] * 100 for l in real] + [l[2] * 100 for l in proj if int(l[0]) > int(real[-1][0])]
ipc = [l[3] * 100 for l in real] + [l[3] * 100 for l in proj if int(l[0]) > int(real[-1][0])]
g20 = linhas("20_selic_ipca", np.array(anos), {"Selic meta": sel, "IPCA em 12 meses": ipc},
             lambda v: br(v, 2, suf="%"), tracejar_depois=int(real[-1][0]))
nova_aba("Tab 20", "Tabela 20 – Selic e IPCA: juros altos em 2026, com queda esperada até 2030",
         ["Ano", "Tipo", "Selic meta", "IPCA em 12 meses", "Referência"], linhas_t20, ["txt", "cen", "pct", "pct", "txt"],
         f"B4, Banco Central do Brasil: SGS (séries 432 e 13522) e Relatório Focus de {DATA_FOCUS}", [8, 16, 12, 14, 30], g20, nome="Selic e IPCA",
         notas=["Nota: realizado = último valor do ano (2026 até a data indicada); Focus = mediana das expectativas para o fim do ano."])

ip = pd.read_csv(DADOS_AGREGADOS / "B4_multiuso" / "[B4] IPCA Alimentação Fora do Domicílio 2023-2026 (IBGE).csv")
col_item = ip.columns[8]
ip = ip[ip.variavel.str.contains("12 meses") & ip.localidade.isin(["Brasil", "Salvador - BA"])
        & ip[col_item].isin(["Índice geral", "1201.Alimentação fora do domicílio"])]
pv = ip.pivot_table(index="periodo", columns=["localidade", col_item], values="valor").dropna().sort_index()
pv = pv[pv.index % 100 == pv.index.max() % 100]  # mesmo mês de cada ano
linhas_t21 = [[f"{str(p)[4:]}/{str(p)[:4]}", pv.loc[p, ("Brasil", "Índice geral")] / 100,
               pv.loc[p, ("Brasil", "1201.Alimentação fora do domicílio")] / 100,
               pv.loc[p, ("Salvador - BA", "Índice geral")] / 100,
               pv.loc[p, ("Salvador - BA", "1201.Alimentação fora do domicílio")] / 100] for p in pv.index]
g21 = barras_v("21_ipca_alimentacao_fora", [l[0] for l in linhas_t21],
               {"Brasil: geral": [l[1] for l in linhas_t21], "Brasil: alimentação fora": [l[2] for l in linhas_t21],
                "Salvador: geral": [l[3] for l in linhas_t21], "Salvador: alimentação fora": [l[4] for l in linhas_t21]},
               lambda v: br(v * 100, 1, suf="%"), cores=[SLATE_700, SLATE_400, ROXO_700, ROXO_300], eixo_pct=True)
nova_aba("Tab 21", "Tabela 21 – IPCA em 12 meses: alimentação fora do domicílio sobe mais que o índice geral",
         ["Mês", "Brasil: índice geral", "Brasil: alimentação fora do domicílio", "Salvador: índice geral",
          "Salvador: alimentação fora do domicílio"], linhas_t21, ["txt", "pct", "pct", "pct", "pct"],
         "B4, IBGE, IPCA (tabela 7060, variação acumulada em 12 meses)", [12, 14, 16, 14, 16], g21,
         nome="IPCA em 12 meses")

# ---------------------------------------------------------------- base e índice
ws = wb.create_sheet(ABA_BASE)
ws.sheet_view.showGridLines = False
ws.cell(1, 1, f"Base – as {N} casas do B1 (valores; as Tabelas 1 a 8 calculam por fórmula sobre esta aba)")
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(COLS))
for j, (_, rot, _) in enumerate(COLS, 1):
    ws.cell(2, j, rot)
for i, r in enumerate(base.itertuples(index=False), 3):
    for j, (c, _, _) in enumerate(COLS, 1):
        v = getattr(r, c)
        ws.cell(i, j, None if (isinstance(v, float) and np.isnan(v)) else (v.item() if hasattr(v, "item") else v))
ult = N + 2
for rr in range(1, ult + 1):
    for j, (_, _, t) in enumerate(COLS, 1):
        cel = ws.cell(rr, j)
        cel.fill = BRANCO
        if rr == 1:
            cel.font, cel.alignment = ARIAL_N, Alignment(horizontal="left")
        elif rr == 2:
            cel.font = ARIAL_N
            cel.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cel.border = Border(top=FINA, bottom=FINA, left=SEM, right=SEM)
        else:
            cel.font = ARIAL
            cel.alignment = Alignment(horizontal="left" if t == "txt" else "right")
            if t != "txt":
                cel.number_format = FMT[t]
            cel.border = Border(top=SEM, left=SEM, right=SEM, bottom=FINA if rr == ult else SEM)
        if rr > 2 and t == "txt":
            cel.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        elif rr > 2:
            cel.alignment = Alignment(horizontal="right", vertical="center")
ws.freeze_panes = "B3"
acabamento(ws, [30] + [13] * (len(COLS) - 1), corpo=range(3, ult + 1), larg_titulo=60)
ws.cell(ult + 1, 1, f"Fonte: {FONTE_B1}; arquivo B1_estatistica_descritiva_geral.xlsx (aba dados).").font = ARIAL
ws.cell(ult + 2, 1, "Nota: 1 = sim, 0 = não nas colunas de dia e de cardápio; \"couvert encontrado\" 0 = não encontrado no cardápio, não \"não cobra\".").font = ARIAL

SAIDA.mkdir(parents=True, exist_ok=True)
for velho in ("dados_agregados.xlsx",):  # pasta única de antes da divisão por bloco (30/10/2026)
    (SAIDA / velho).unlink(missing_ok=True)
total = SAIDA / "_todas_as_tabelas.tmp.xlsx"
wb.save(total)
TABS = [a for a, _, _ in INDICE]
IG = ["Tab 9", "Tab 10", "Tab 11", "Tab 12"]
B1_COMPLETA = [f"Tab {k}" for k in range(1, 15)]
# Resumida: as tabelas do Instagram trocadas pelas do recorte de 01/07 a 01/11/2026 (mesma numeração).
B1_RESUMIDA = [(a, a + "r") if a in IG else a for a in B1_COMPLETA]
B3_TABS, B4_TABS = ["Tab 15a", "Tab 15b", "Tab 15c"], [f"Tab {k}" for k in range(16, 22)]
assert set(B1_COMPLETA + [a + "r" for a in IG] + B3_TABS + B4_TABS) == set(TABS)
BASE_B1 = [(ABA_BASE, f"Base das {N} casas do B1", FONTE_B1)]
NOTA_GRAF = "Gráficos em PNG de 300 dpi em textos-tcc/graficos/agregados/. Gerado por _src/outros/G1_planilhas/gerar_planilha_agregada.py."
NOTA_FORA = "Fora, por pedido do autor (30/10/2026): comentários do B2 (planilha própria) e dados do OpenStreetMap no entorno."
feitos = dividir(total, INDICE, [
    (SAIDA / "B1_dados_agregados.xlsx", "Dados agregados do B1 (estabelecimentos) – TCC Luderia, versão completa",
     B1_COMPLETA, BASE_B1, [NOTA_FORA, "Tabelas 9 a 12: todos os posts coletados das casas, de qualquer data.", NOTA_GRAF]),
    (SAIDA / "B1_dados_agregados_resumido.xlsx", "Dados agregados do B1 (estabelecimentos) – TCC Luderia, versão resumida",
     B1_RESUMIDA, BASE_B1,
     [NOTA_FORA, "Versão resumida: tabelas 9 a 12 só com os posts publicados de 01/07 a 01/11/2026, a janela da "
      "estatística descritiva; base sem as colunas de trilhos (trem, VLT), que nenhuma tabela usa.", NOTA_GRAF]),
    (SAIDA / "B3_dados_agregados.xlsx", "Dados agregados do B3 (contagem direta) – TCC Luderia", B3_TABS, [], [NOTA_GRAF]),
    (SAIDA / "B4_dados_agregados.xlsx", "Dados agregados do B4 (bases públicas) – TCC Luderia", B4_TABS, [], [NOTA_GRAF]),
])
total.unlink()
# Resumida: tira da base as colunas sem uso (as últimas, para não deslocar as fórmulas).
from openpyxl import load_workbook
res = SAIDA / "B1_dados_agregados_resumido.xlsx"
wr = load_workbook(res)
wsb = wr[ABA_BASE]
n_ok = len(COLS) - len(COLS_SO_COMPLETA)
for m in list(wsb.merged_cells.ranges):
    wsb.unmerge_cells(str(m))
wsb.delete_cols(n_ok + 1, len(COLS_SO_COMPLETA))
wsb.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_ok)
wr.save(res)
for caminho, n in feitos:
    print(f"{caminho.relative_to(ROOT)}: {n} tabelas")
print(f"{len(list(GRAF.glob('*.png')))} gráficos em {GRAF.relative_to(ROOT)}")
print(f"Conferência: {N} casas na base; soma por metrópole = {int(cont.n.sum())} (diferença {N - int(cont.n.sum())})")
