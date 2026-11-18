"""
Cap. 9 - modelo financeiro da luderia (_docs/_instrucoes/8_financeiro.md).

Gera `textos/planilhas/P9_financeiro.xlsx`, dirigido por premissas:
aba sumario (índice das abas), abas premissas, pessoal, simples, receitas, custos, investimento, dre,
fluxo_caixa, indicadores, sensibilidade e checagens. Toda fórmula de cálculo lê
a aba premissas (coluna "Valor usado", escolhida pelo cenário ativo em
premissas!D2: 1 pessimista, 2 provável, 3 otimista) pelos nomes definidos
P_<ID> (ex.: P_R01). Nenhum número fica digitado dentro de fórmula.

O mesmo modelo é calculado em Python para o tornado (§4.2), o ponto de ruptura
(§4.3), a tabela dos três cenários e a simulação de Monte Carlo (§4.4),
gravados como valores nas abas sensibilidade e monte_carlo. A planilha é recalculada no LibreOffice nos três cenários e o
VPL de cada um tem de bater com o do Python (diferença < R$ 1,00); senão o
script para.

Modelo em preços constantes (out/2026), com TMA real. Mensal nos 60 meses
(rampa de maturação no ano 1), anual na DRE e no fluxo de caixa. No ano 5
entra o valor residual (M03): perpetuidade sem crescimento do EBITDA do ano 5
menos o reinvestimento anual (igual à depreciação), à TMA, com piso zero. Com
valor residual, o negócio segue aberto, e a caução e o capital de giro ficam
nele (já estão no valor da perpetuidade); sem valor residual (M03 = 0 ou
perpetuidade negativa), o negócio fecha no ano 5 e os dois voltam ao caixa
(correção de 09/11/2026: antes os dois voltavam junto com o valor residual, o
que contava o mesmo dinheiro duas vezes). A aba sensibilidade mostra o VPL com
e sem o valor residual.

Receita (decisão do autor, 02/11/2026): pessoas por dia de fim de semana =
circulação no pico (pessoas que entram por hora nas visitas do B3, sem escala
pelas mesas; pessimista pelas NFC-e) × horas de pico equivalentes do fim de semana
(R02); dia útil = mesma circulação × horas de pico equivalentes do dia útil (R03).
As horas vêm do índice "Horários de pico" do Google Maps dos concorrentes (soma do
índice médio nas horas do plano ÷ índice médio nas janelas das visitas;
B1a_horas_pico_indice.py, decisão do autor de 12/11/2026, que trocou a contagem de
casas abertas, a razão de gasto com cartão da ANR e o ajuste do horário R19). A
demanda madura fica constante depois da rampa (R18 retirada em 12/11/2026).
Receita por pessoa = gasto por pessoa declarado no Google Maps (B2), média das
13 casas com taxa de entrada conhecida. A taxa de entrada (R05) é o preço
adotado na seção 6.3, R$ 19,62 em todos os cenários (média da taxa das 29 casas
que cobram, fora a São Jogue; R$ 18,68 e 22 casas até a busca de 11/11/2026), e o restante do gasto é A&B (anexo I e CMV);
antes de 09/11/2026, a taxa era 28,4% do gasto (R$ 22,32 no provável), o que
não batia com o preço adotado.

Desenho adotado (P7 de _docs/_instrucoes/1a_principios.md; decisão do autor, 16/11/2026): a casa
abre com 8 mesas e 48 lugares, em ponto de 100 a 150 m² (C03 a C05), com layout
preliminar estimado entre 115 e 135 m². A abertura é de terça a sábado, das 14h às 23h (45 h),
com 3 empregados (1 cozinheiro-chefe e 2 atendentes-instrutores, 5 dias de 8 h, 40 h por semana)
e o sócio na gestão, no caixa e no salão (pró-labore, C08). A etapa futura é exclusivamente de
equipe e horário: se a demanda de pico atinge o limiar de GATILHO_MESAS, a partir do ano 2 do
Monte Carlo, entram mais um instrutor, um segundo cozinheiro e o domingo (14h às 20h), com a
escala de ESCALA_EXP. O imóvel e as 8 mesas já estão completos desde a abertura.
A remuneração soma ao salário os adicionais legais da escala (ESCALA): noturno,
hora noturna reduzida, repouso sobre eles e feriados em dobro; os encargos e o
vale-transporte (C07) saem da mesma conta, linha a linha (custo_empregado).
A São Jogue entra como referência de comportamento (circulação, pessoas por
mesa, permanência), não de porte. A circulação fica limitada ao salão:
pessoas por hora ≤ mesas × pessoas por mesa ÷ permanência (B3).

Entradas: B1 (cesta de jogos; couvert dos cardápios; horas de pico pelo índice,
B1a_horas_pico_indice.py), B2 (gasto por pessoa e cesta por casa,
B2a_gasto_por_pessoa.py), B3 (contagem_resumo_visitas.csv,
contagem_notas_intervalo.csv), B5 (orçamento e anúncios de aluguel), B4 (CAGED,
BCB, Simples Nacional, IBGE PAS e população). As premissas de valor fixo
(decisões e estimativas do autor) ficam em textos/capitulos/modelo_financeiro/
P9_premissas_autor.xlsx, com fonte, código do tipo de evidência e justificativa:
muda-se a planilha, não o código. As que saem de dados são calculadas em premissas().

Saídas: o .xlsx em textos/capitulos/ (Apêndice E), o registro completo em
textos/capitulos/modelo_financeiro/P9_premissas_registro.xlsx e as figuras 9-4_tornado.png e
G-1_monte_carlo.png (apêndice G) em textos/graficos/; imprime os números citados no
texto do capítulo. Log em _src/outros/G3_modelo_financeiro/logs/.
Uso: python3 "_src/outros/G3_modelo_financeiro/gerar_modelo_financeiro.py"
"""
import os
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[2] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import random
import shutil
import subprocess
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import openpyxl  # noqa: E402
import pandas as pd  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402
from openpyxl.workbook.defined_name import DefinedName  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
DADOS = ROOT / "dados"
DADOS_AGREGADOS = ROOT / "dados-agregados"
TAXA_SAO_JOGUE = (22.0, 28.0)  # taxa de entrada da São Jogue: terça a quinta e sexta a domingo (cap. 5)
DADOS_BRUTOS = ROOT / "dados-brutos"
MODELO = ROOT / "textos" / "capitulos" / "modelo_financeiro"
PREMISSAS_AUTOR = MODELO / "P9_premissas_autor.xlsx"  # entrada: premissas de valor fixo (decisões e estimativas do autor)
REGISTRO = MODELO / "P9_premissas_registro.xlsx"  # saída: as premissas com os valores resolvidos
COLS_PREMISSAS = ["id", "nome", "unidade", "pessimista", "provavel", "otimista", "fonte", "nivel", "justificativa"]
B3 = DADOS_AGREGADOS / "B3_contagem"
SAIDA = ROOT / "textos" / "planilhas" / "P9_financeiro.xlsx"
FIGURA = ROOT / "textos" / "graficos" / "9-4_tornado.png"
FIGURA_MC = ROOT / "textos" / "graficos" / "G-1_monte_carlo.png"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

MESES = 60
INSTR = "Atendente e instrutor de jogos (recreador)"
COZ = "Cozinheiro-chefe"
# Folgas de cada semana do ciclo, entre os dias de terça a domingo (a segunda é sempre fechada).
# Etapa 1 (decisão do autor, 12/11/2026): terça a sábado, das 14h às 23h, turnos de 8 h com 1 h de
# intervalo; os 3 empregados trabalham os 5 dias e folgam no domingo e na segunda (casa fechada).
ESCALA = {INSTR: ((("dom",),), (("dom",),)), COZ: ((("dom",),),)}
JORNADA_SEM = {INSTR: 40, COZ: 40}  # 5 turnos de 8 h
# turnos que fecham às 23h por semana (1 h depois das 22h), somados no cargo: todos ficam até o fechamento
NOITES_SEM = {INSTR: 10, COZ: 5}
# Etapa de equipe (expansão operacional, só no Monte Carlo; decisões do autor, 04 e 12/11/2026): abre o domingo das
# 14h às 20h (turno de 6 h com 15 min) com 2 cozinheiros, condição para abrir no domingo. Todos folgam
# dois dias por semana (a segunda e mais um); metade da equipe é de mulheres (atendentes 1 e 2), que
# folgam domingo sim, domingo não (CLT, art. 386); o homem folga 1 domingo a cada 3 semanas (Portaria MTP
# n. 671/2021, art. 58, § 3º, aplicado a bares e restaurantes por decisão do autor, 16/11/2026; a CCT
# SHRBS × Sindbares 2024/2026 pede ao menos 1 domingo por mês). Ciclo de 6 semanas: em 2 domingos
# (semanas 3 e 6) folgam 2 atendentes e o salão fica com 1 atendente e o sócio (L41, opção a).
# Atendentes: 3 no salão de quinta a sábado e 2 nos demais dias; cozinheiros alternam a folga entre
# terça e domingo: 2 na cozinha de quarta a sábado e 1 na terça e no domingo.
ESCALA_EXP = {
    INSTR: (
        (("dom",), ("ter",), ("dom",), ("qua",), ("dom",), ("qua",)),
        (("ter",), ("dom",), ("ter",), ("dom",), ("qua",), ("dom",)),
        (("qua",), ("qua",), ("dom",), ("ter",), ("ter",), ("dom",))),
    COZ: (
        (("ter",), ("dom",)),
        (("dom",), ("ter",))),
}
JORNADA_SEM_EXP = {INSTR: 39, COZ: 39}  # média: 8 h de terça a sábado, 6 h no domingo
# atendentes, 15 turnos menos as folgas de terça e quarta (10 em 6 semanas: 13,33 por semana); cozinheiros, 2 de quarta a sábado e 1 na terça
NOITES_SEM_EXP = {INSTR: 15 - 10 / 6, COZ: 9}
ETAPAS = {"etapa1": (ESCALA, JORNADA_SEM, NOITES_SEM), "expansao": (ESCALA_EXP, JORNADA_SEM_EXP, NOITES_SEM_EXP)}
# Carga máxima de mesas por pessoa no salão (instrutores e sócio): 7 mesas ocupadas para 3 instrutores
# no pico da Paralela em 30/10/2026, a maior carga vista nas visitas, com o atendimento em dia (B3; P7)
MESAS_POR_INSTRUTOR = 7 / 3
# carga da etapa 1: 2 instrutores e o sócio atendem até 7 mesas ocupadas (MESAS_POR_INSTRUTOR); a 8ª
# mesa ocupada pede o terceiro instrutor, que entra com a etapa de equipe
CARGA_ETAPA1 = 7
MESAS = 8  # decisão do autor (16/11/2026): o ponto abre com as 8 mesas e 48 lugares
# gatilho operacional da etapa de equipe (cap. 10): demanda no pico ≥ 7/8 da capacidade do salão
# de 8 mesas (87,5%) por 3 meses seguidos depois da maturação; o Monte Carlo aplica o limiar ao
# cenário sorteado a partir do ano 2, sem simular a persistência mês a mês
GATILHO_MESAS = CARGA_ETAPA1 / MESAS  # limiar de 87,5% da capacidade do salão
# utilidades (C09) crescem com as horas abertas quando o domingo abre: 51 h ÷ 45 h
HORAS_SEM, HORAS_SEM_EXP = 45, 51
# CCT SHRBS × Sindbares 2024/2026 (BA000301/2025): 35% das 22h às 5h, acima dos 20% da CLT (art. 73),
# com a hora noturna de 52 min 30 s (art. 73, § 1º); conferida pelo autor em 16/11/2026 (L17)
ADIC_NOTURNO = 0.35
ROT_NOTURNO = f"Adicional noturno ({ADIC_NOTURNO:.0%})"
HORA_EXTRA = 0.50  # CF, art. 7º, XVI: a hora reduzida das 22h às 23h passa da jornada contratada
FERIADOS_ANO = 14  # 9 nacionais, 2 de julho (BA) e 4 de Salvador (Lei n. 9.093/1995) [AV]
TARIFA_VT = 5.90  # ônibus de Salvador desde 05/01/2026; ida e volta por dia trabalhado (Lei n. 7.418/1985)
SEMANAS_MES = 365.25 / 7 / 12
# vida útil (anos) dos itens depreciáveis, a mesma da aba investimento
VIDA_UTIL = dict(reforma=10, mobiliario=10, cozinha=10, ti=5, acervo=5, preop=5, outros=5)
# reinvestimento anual na perpetuidade do valor residual (15/11/2026, pedido do autor): só os itens
# físicos que se repõem; o acervo já se repõe pela C13 nos custos fixos e os gastos pré-operacionais
# não se repetem. A DRE segue com a depreciação e a amortização de todos os itens (VIDA_UTIL)
REPOE_PERPETUIDADE = ("reforma", "mobiliario", "cozinha", "ti", "outros")


def reinvestimento(inv: dict) -> float:
    return sum(inv[k] / VIDA_UTIL[k] for k in REPOE_PERPETUIDADE)
ANOS = 5
CENARIOS = ("pessimista", "provavel", "otimista")
N_SIMULACOES = 10_000
SEMENTE = 20261031
# Monte Carlo: faixas próprias pedidas pelo autor (2 ou 3 pessoas por mesa no
# pessimista, 5 ou 6 no otimista) e premissas discretas (giros e pessoas por cesta)
# Monte Carlo (02/11/2026, pedido do autor): distribuição PERT contínua entre o pessimista e o
# otimista, com moda no provável; faixa própria onde indicado. A TMA fica fora do sorteio (o risco já
# está no fluxo). A demanda sorteada aciona a etapa de equipe em GATILHO_MESAS da capacidade; não há
# ampliação física, pois as 8 mesas abrem com a luderia (MC_EXPANSAO = 0). Os gatilhos G5 e G6 do cap. 10
# agem na simulação (calcula_mc).
# valor residual incerto (18/11/2026, decisão do autor, L16 b): no sorteio, o M03 vira a fração da
# perpetuidade que se realiza, PERT entre 0 (nada além do ano 5) e 1 (perpetuidade inteira), moda em 1;
# os três cenários determinísticos seguem com M03 = 1
MC_FAIXA = {"O02": (2.0, 6.0), "M03": (0.0, 1.0)}
# decisões do sócio, não estado do mundo: ficam fora do sorteio mesmo se os três cenários voltarem a
# divergir (C08 pró-labore, C10 marketing, I08 capital de giro e R08 preço do aluguel, 16/11/2026)
MC_FIXAS = {"M01", "C08", "C10", "I08", "R08"}
MC_EXPANSAO = 0  # mesas a mais na etapa de equipe: nenhuma, as 8 mesas abrem com a luderia (15/11/2026)
# dez bairros de maior renda familiar per capita do QUALISalvador (Tabela 6.1); Ondina/Chame-Chame
# aparece nos portais como Ondina
# utilidades (C09), estimadas pelas tarifas vigentes em nov/2026 (pedido do autor, 15/11/2026): preços
# N1/N2, consumos do autor (N6) a partir dos equipamentos do orçamento do B5 e da escala do cap. 7
ENERGIA_TARIFA = 0.87773  # R$/kWh sem tributos, B3 convencional (TUSD 0,62008 + TE 0,25765), Neoenergia Coelba, ANEEL REH n. 3.578/2026, de 22/04/2026 a 21/04/2027
ENERGIA_ICMS, ENERGIA_PIS_COFINS = 0.205, 0.06  # ICMS da Bahia (alíquota modal) e PIS/Cofins médio, por dentro
# equipamentos: (nome, kW médio, horas por mês: "aberto" = horas abertas, "operacao" = abertas mais
# 1 h de preparo por dia aberto, "cozinha" = h por dia aberto, "24h" = o mês inteiro)
ENERGIA_EQUIP = [
    ("Ar-condicionado split 30.000 BTU/h inverter (2), a 60% da potência de 2,75 kW", 2 * 2.75 * 0.60, "aberto", None),
    ("Geladeira comercial 4 portas, freezer horizontal e expositor de bebidas (7 + 3 + 4 kWh por dia)", 14 / 24, "24h", None),
    ("Coifa com exaustor", 0.37, "operacao", None),
    ("Forno elétrico de bancada", 1.8, "cozinha", 1.0),
    ("Micro-ondas", 1.4, "cozinha", 0.5),
    ("Liquidificador e multiprocessador", 1.2, "cozinha", 0.3),
    ("Iluminação LED, 7 W por m² do ponto", None, "operacao", None),
    ("Computador e impressora de NFC-e", 0.10, "operacao", None),
    ("Som ambiente", 0.10, "aberto", None),
    ("Roteador e câmeras", 0.04, "24h", None),
]
ILUMINACAO_W_M2 = 7
# água e esgoto: Embasa, tabela de 2026 (Resolução AGERSA n. 001/2026, desde 20/07/2026), categoria
# comercial: até 6 m³ fixo; R$/m³ de 7 a 10, de 11 a 50 e acima de 50; esgoto = 80% da água
AGUA_FIXA, AGUA_FAIXAS, ESGOTO_PCT = 129.94, ((10, 4.96), (50, 28.50), (float("inf"), 33.60)), 0.80
AGUA_L_PESSOA, AGUA_L_EMPREGADO_DIA, AGUA_L_M2_DIA = 19, 50, 1.0  # sanitário (6 L da bacia e 1 L do lavatório) e cozinha e louça (12 L); equipe; limpeza do piso
# gás: GLP pela média do P13 em Salvador no levantamento da ANP (28/10 a 02/11/2026, 101 revendas)
GLP_P13, GLP_KG_PESSOA, GLP_KG_DIA = 122.21, 0.06, 0.30  # R$ por 13 kg; kg por cliente; preaquecimento da chapa e do fogão
INTERNET = 150.0  # plano de fibra para empresa (estimativa do autor)
UTIL_FAIXA = (1.25, 0.85)  # pessimista e otimista sobre o consumo provável (N6)


def utilidades(area: float, pessoas: float) -> dict:
    """Utilidades por mês (C09) no provável: energia, água e esgoto, gás e internet."""
    abertas = HORAS_SEM * 52 / 12
    dias = 5 * 52 / 12
    horas = {"aberto": abertas, "operacao": abertas + dias, "24h": 365.25 * 24 / 12}
    kwh = 0.0
    for _, kw, uso, h_dia in ENERGIA_EQUIP:
        kw = kw if kw is not None else ILUMINACAO_W_M2 * area / 1000
        kwh += kw * (h_dia * dias if uso == "cozinha" else horas[uso])
    preco_kwh = ENERGIA_TARIFA / (1 - ENERGIA_ICMS - ENERGIA_PIS_COFINS)
    m3 = (pessoas * AGUA_L_PESSOA + 3 * AGUA_L_EMPREGADO_DIA * dias + area * AGUA_L_M2_DIA * dias) / 1000
    agua, ant = AGUA_FIXA, 6
    for teto, preco in AGUA_FAIXAS:
        agua += max(0.0, min(m3, teto) - ant) * preco
        ant = teto
    glp_kg = pessoas * GLP_KG_PESSOA + GLP_KG_DIA * dias
    partes = dict(energia=kwh * preco_kwh, agua_esgoto=agua * (1 + ESGOTO_PCT), gas=glp_kg * GLP_P13 / 13, internet=INTERNET)
    return dict(partes, total=sum(partes.values()), kwh=kwh, preco_kwh=preco_kwh, m3=m3, glp_kg=glp_kg)


# classes de área dos anúncios (m²) e recorte do ponto (decisão do autor, 15/11/2026)
CLASSE_AREA, CLASSE_AREA_MAX = 25, 500
# gastos pré-operacionais (I06): base do autor (projeto, licenças, contratação e lançamento; N6) mais o
# aluguel dos meses entre o contrato e a abertura (Quadro 7.3: contrato no mês 2, abertura no mês 6), pelo
# custo total do cenário (decisão do autor, 16/11/2026, L40)
PREOP_BASE = {"pessimista": 30000, "provavel": 20000, "otimista": 12000}
MESES_ALUGUEL_IMPLANTACAO = 4
AREA_PONTO = (100, 150)  # inclusive nas duas pontas (decisão do autor, 15/11/2026, 22h)
BAIRROS_ALUGUEL = ("Pituba", "Itaigara", "Graça", "Patamares", "Caminho das Árvores", "Vitória", "Barra",
                   "Ondina", "Chame-Chame", "Rio Vermelho", "Canela")


# ---------------------------------------------------------------- dados-fonte
def ler_fontes() -> dict:
    f = {}
    # B3: médias das visitas (observador válido) e notas por dia
    r = pd.read_csv(B3 / "contagem_resumo_visitas.csv", sep=";", encoding="utf-8-sig")
    r = r[r["observador"] != "media"]
    f["visitas"] = r
    # mesas ocupadas em média em cada visita (ocupação média × mesas da unidade)
    f["mesas_ocupadas"] = r["ocupacao_mesas_media_pct"] / 100 * r["mesas_denominador"]
    f["notas"] = pd.read_csv(B3 / "contagem_notas_intervalo.csv", sep=";", encoding="utf-8-sig")
    # B1: cesta de jogos (acervo inicial) e taxas de jogo dos concorrentes
    ai = pd.read_excel(DADOS_AGREGADOS / "B1_acervo_jogos" / "B1_cesta_jogos.xlsx", sheet_name="acervo_inicial")
    f["acervo"] = dict(zip(ai["tamanho"], ai["custo_provavel_rs"]))
    f["acervo_faixa"] = ai.set_index("tamanho")[["custo_pessimista_rs", "custo_provavel_rs", "custo_otimista_rs"]].to_dict("index")
    f["acervo_titulos"] = dict(zip(ai["tamanho"], ai["titulos"]))
    # B5: orçamento da etapa 1 por premissa (SINAPI e coletas em sites; B5b_orcamento_itens.py), o mês mais recente
    orc = sorted((DADOS_AGREGADOS / "B5_mobiliario").glob("[[]B5[]] Orçamento por Premissa Etapa 1 *.csv"))[-1]
    f["b5"] = pd.read_csv(orc, sep=";", decimal=",", encoding="utf-8-sig").set_index("premissa")
    f["b5_arquivo"] = orc.name
    ps = pd.read_excel(DADOS_AGREGADOS / "B1_cardapios" / "B1_cardapios_itens_precos.xlsx", sheet_name="precos_subcategoria")
    taxa = ps["couvert ou taxa de jogo | couvert ou taxa de jogo"].dropna()
    taxa = taxa[taxa > 0]
    f["taxa_b1_mediana"], f["taxa_b1_n"] = taxa.median(), len(taxa)
    # couvert e cesta de consumo por casa (B1_resumo_estabelecimentos, aba cesta):
    # couvert só nas casas que cobram (encontrado e > 0); cesta de consumo =
    # bebida mediana + hambúrguer não vegetariano mais barato, só nas casas com os dois
    ce = pd.read_excel(DADOS_AGREGADOS / "B1_estabelecimentos" / "B1_resumo_estabelecimentos.xlsx", sheet_name="cesta")
    cv = ce.loc[ce["couvert_no_cardapio"] == "sim", "couvert_mediana"]
    cv = cv[cv > 0]
    # taxa de entrada em dois valores (decisões do autor, 15/11 e 18/11/2026, L44): só as casas que
    # cobram valores diferentes conforme o dia. De cada uma, o menor e o maior valor positivo da taxa
    # por pessoa no cardápio (sem a sala por hora); terça a quinta pela média dos menores, sexta a
    # domingo pela média dos maiores. Saem as casas de preço único (mínimo = máximo), a Balboa's (preço
    # por duração), o Café Geek (por nível de jogo) e as linhas do LudoCafé com consumo mínimo. A São
    # Jogue entra com R$ 22,00 e R$ 28,00 (cap. 5), a mesma base de 21 casas do sumário executivo
    it = pd.read_excel(DADOS_AGREGADOS / "B1_cardapios" / "B1_cardapios_itens_precos.xlsx", sheet_name="itens")
    it = it[(it.linha_referencia == "S") & (it.categoria == "couvert ou taxa de jogo")].dropna(subset=["preco"])
    it = it[~it["item"].str.contains("sala", case=False) & (it.preco > 0)]
    it = it[~it["estabelecimento"].str.contains("Balboa|Café Geek")]
    it = it[~it["variacao"].fillna("").str.contains("com consumo mínimo")]
    tx = it.groupby("place_id").preco.agg(["min", "max"])
    tx = tx[tx["min"] < tx["max"]]
    tx.loc["sao_jogue"] = [TAXA_SAO_JOGUE[0], TAXA_SAO_JOGUE[1]]
    f["taxa_menor"], f["taxa_maior"], f["taxa_n"] = tx["min"].mean(), tx["max"].mean(), len(tx)
    f["taxa_menor_mediana"], f["taxa_maior_mediana"] = tx["min"].median(), tx["max"].median()
    co = (ce["bebida_mediana"] + ce["hamburguer_min_nao_veg"]).dropna()
    f["couvert_media"], f["couvert_n"], f["couvert_mediana"] = cv.mean(), len(cv), cv.median()
    f["cesta_consumo_media"], f["cesta_consumo_n"], f["cesta_consumo_mediana"] = co.mean(), len(co), co.median()
    f["couvert_q"], f["cesta_q"] = cv.quantile([.25, .75]).tolist(), co.quantile([.25, .75]).tolist()
    # B2: gasto por pessoa declarado e cesta de consumo (com a taxa) das casas no recorte
    gc = pd.read_csv(DADOS_AGREGADOS / "B2_avaliacoes" / "gasto_por_pessoa" / "B2_gasto_cesta_por_casa.csv",
                     sep=";", encoding="utf-8-sig")
    f["gasto_casas"] = gc[gc["no_recorte"] == "sim"]
    # B1: horas de pico equivalentes por dia pelo índice "Horários de pico" dos concorrentes (curva
    # média e mediana das casas abertas ÷ curva nas janelas das visitas; B1a_horas_pico_indice.py)
    hp = pd.read_csv(DADOS_AGREGADOS / "B1_estabelecimentos" / "B1_horas_pico_indice.csv", sep=";", encoding="utf-8-sig")
    for casa, chave in (("plano", "horas_pico"), ("São Jogue", "horas_pico_sj")):
        f[chave] = {est: dict(zip(h["dia"], h["horas_pico_equivalentes"]))
                    for est, h in hp[hp["casa"] == casa].groupby("curva")}
    f["n_casas_indice"] = pd.read_csv(DADOS_AGREGADOS / "B1_estabelecimentos" / "B1_horarios_pico_concorrentes_horas.csv",
                                      sep=";", encoding="utf-8-sig")["place_id"].nunique()
    # B5: anúncios de aluguel de 150 a 200 m² nos dez bairros de maior renda (Tabela 6.1; decisão do
    # autor, 15/11/2026, que trocou o recorte só da Pituba), área para 8 mesas; fora as salas em prédio
    # e, nas possíveis duplicatas do mesmo tipo com até 5 m² de diferença, o segundo anúncio do par
    an = pd.read_csv(DADOS_AGREGADOS / "B5_aluguel" / "[B5] Anúncios de Aluguel 2026-11 (OLX, ZAP, Viva Real).csv",
                     sep=";", decimal=",", encoding="utf-8-sig")
    an = an[an["bairro"].isin(BAIRROS_ALUGUEL) & (an["subtipo"] != "sala") & ~an["titulo"].str.contains("Salas", na=False)]
    dup = pd.read_csv(DADOS_AGREGADOS / "B5_aluguel" / "[B5] Possíveis Duplicatas de Aluguel 2026-11 (OLX, ZAP, Viva Real).csv",
                      sep=";", decimal=",", encoding="utf-8-sig")
    tipo, fora = dict(zip(an["id"], an["subtipo"])), set()
    for _, r in dup.iterrows():
        if (r["id_a"] in tipo and r["id_b"] in tipo and tipo[r["id_a"]] == tipo[r["id_b"]]
                and abs(r["area_m2_a"] - r["area_m2_b"]) <= 5 and r["id_a"] not in fora):
            fora.add(r["id_b"])
    an = an[~an["id"].isin(fora)].copy()
    an["encargos"] = an["condominio"].fillna(0) + an["iptu"].fillna(0)  # condomínio vazio = isento
    an["custo_total"] = an["aluguel"] + an["encargos"]
    an["iptu_informado_sim"] = an["iptu"].notna()
    # classes de 25 m² de área (decisão do autor, 15/11/2026): cada anúncio numa só classe, pela área
    an["classe_area"] = pd.cut(an["area_m2"], bins=list(range(0, CLASSE_AREA_MAX + 1, CLASSE_AREA)) + [float("inf")],
                               right=False, labels=[f"{a} a {a + CLASSE_AREA}" for a in range(0, CLASSE_AREA_MAX, CLASSE_AREA)]
                               + [f"{CLASSE_AREA_MAX} ou mais"])
    f["aluguel_anuncios_todos"] = an
    # ponto: anúncios de 100 a 150 m²; custo total = aluguel + condomínio + IPTU, só nos anúncios que
    # informam o IPTU. Provável na mediana do custo total, otimista no 1º e pessimista no 3º quartil
    # (decisão do autor, 15/11/2026): C04 é calibrado para que C03 × C04 × (1 + C05) dê esses valores
    rec = an[an["area_m2"].between(*AREA_PONTO, inclusive="both")]
    inf = rec[rec["iptu_informado_sim"]]
    f["aluguel_anuncios"] = inf
    f["aluguel_n_classe"], f["aluguel_n"], f["aluguel_dup"] = len(rec), len(inf), len(fora)
    f["aluguel_n_encargos"] = len(inf)
    f["area_media"] = inf["area_m2"].median()  # área mediana do recorte (C03)
    f["encargos_pct"] = inf["encargos"].sum() / inf["aluguel"].sum()  # repartição fixa nos três cenários
    f["custo_total_q"] = inf["custo_total"].quantile([.25, .5, .75]).tolist()
    f["aluguel_m2_q"] = [c / (f["area_media"] * (1 + f["encargos_pct"])) for c in f["custo_total_q"]]
    f["custo_total_medio"] = f["custo_total_q"][1]  # mediana
    # B4
    bcb = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Selic IPCA e Salário Mínimo Último Valor 2026 (BCB).csv")
    f["selic"] = bcb.loc[bcb["serie"] == "selic_meta", "valor"].iloc[0]
    focus = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Expectativas Focus 2026-2030 (BCB).csv")
    f["ipca_2027"] = focus[(focus["Indicador"] == "IPCA") & (focus["DataReferencia"] == 2027)]["Mediana"].iloc[0]
    f["juro_real"] = ((1 + f["selic"] / 100) / (1 + f["ipca_2027"] / 100) - 1) * 100
    pas_c = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Serviços às Famílias Custos 2019-2023 (IBGE PAS).csv")
    pas_r = pd.read_csv(DADOS_AGREGADOS / "B4_financeiro" / "[B4] Serviços às Famílias Receita 2019-2023 (IBGE PAS).csv")
    sel = lambda d, var: d[(d["periodo"] == 2023) & (d["variavel"] == var)
                           & d["Serviços prestados às famílias"].str.startswith("1.2")]["valor"].iloc[0]
    f["pas_mercadorias_pct"] = sel(pas_c, "Mercadorias, materiais de consumo e de reposição") / sel(pas_r, "Receita operacional líquida") * 100
    cg = pd.read_csv(DADOS_AGREGADOS / "B4_multiuso" / "[B4] Salário Admissão por Capital 2025-2026 (CAGED).csv")
    f["caged"] = cg[cg["capital"] == "Salvador"]
    sn = pd.read_csv(DADOS_AGREGADOS / "B4_juridico" / "[B4] Faixas e Alíquotas por Anexo 2026 (Simples Nacional).csv")
    f["simples"] = {a: sn[sn["anexo"] == a].reset_index(drop=True) for a in ("I", "III")}
    pop = pd.read_csv(DADOS_AGREGADOS / "B4_marketing" / "[B4] Resumo de População e Renda por Capital 2022-2026 (IBGE).csv")
    f["pop_salvador"] = pop.loc[pop["capital"] == "Salvador", "pop_estimada_2026"].iloc[0]
    return f


def salario(f, ocupacao: str, recorte: str = "CNAE 56 - alimentação") -> float:
    c = f["caged"]
    return float(c[(c["ocupacao"] == ocupacao) & (c["recorte"] == recorte)]["salario_mediana"].iloc[0])


def instrutores(mesas: int) -> int:
    """Instrutores empregados para a carga máxima por pessoa no salão; o sócio é a primeira pessoa."""
    return -(-mesas // MESAS_POR_INSTRUTOR) - 1


def quadro_pessoal(f, etapa: str = "etapa1") -> list[tuple]:
    """(cargo, CBO, quantidade, salário, fonte). Na abertura, 8 mesas instaladas, capacidade operacional
    de 7 mesas, 45 h semanais de terça a sábado, 1 cozinheiro e 2 instrutores; gestão, caixa e salão
    também ficam com o sócio (pró-labore, C08). Na expansão, 3 instrutores, 2 cozinheiros e domingo."""
    cn56 = "CAGED, admissões ago/2025-jul/2026, Salvador, CNAE 56, mediana"
    todas = "CAGED, admissões ago/2025-jul/2026, Salvador, todas as atividades, mediana (CNAE 56 com amostra pequena)"
    rec = salario(f, "Recreador", "todas as atividades")
    mesas = CARGA_ETAPA1 if etapa == "etapa1" else MESAS + MC_EXPANSAO
    q_coz = 1 if etapa == "etapa1" else 2
    return [
        (COZ, "513205", q_coz, salario(f, "Cozinheiro geral"),
         cn56 + "; cozinheiro geral, sem chefe de cozinha no recorte"),
        (INSTR, "371410", int(instrutores(mesas)), rec, todas),
    ]


def custo_empregado(sal: float, cargo: str, folgas: tuple, anos_aviso: int = 5, vt: bool = True,
                    etapa: str = "etapa1") -> dict:
    """Custo mensal de um empregado, linha a linha (R$). Remuneração: salário mais adicionais da
    escala; encargos do empregador no Simples (a contribuição patronal fica no DAS dos anexos I e
    III, LC n. 123/2006, art. 13); provisão de uma rescisão sem justa causa a cada anos_aviso anos."""
    escala, jornada, noites = ETAPAS[etapa]
    sh = sal / (jornada[cargo] * 5)  # salário-hora: divisor de 5 × a jornada semanal
    n = noites[cargo] / len(escala[cargo]) * SEMANAS_MES  # noites depois das 22h por mês
    dias_sem = 6 - sum(len(sem) for sem in folgas) / len(folgas)  # dias trabalhados por semana
    dom, fer = 365.25 / 7 / 12, FERIADOS_ANO / 12
    repouso = (dom + fer) / (365.25 / 12 - dom - fer)  # dias de repouso ÷ dias úteis do mês
    c = {"Salário": sal,
         ROT_NOTURNO: n * 1.0 * sh * ADIC_NOTURNO,
         "Hora noturna reduzida (hora extra de 50%)": n / 7 * sh * (1 + ADIC_NOTURNO) * (1 + HORA_EXTRA)}
    c["Repouso semanal sobre os adicionais"] = (c[ROT_NOTURNO] + c["Hora noturna reduzida (hora extra de 50%)"]) * repouso
    c["Feriados trabalhados em dobro"] = FERIADOS_ANO * 6 / 7 * dias_sem / 6 / 12 * 2 * sal / 30
    rem = sum(c.values())
    c["Remuneração"] = rem
    c["FGTS (8%)"] = 0.08 * rem
    c["13º salário (1/12)"] = rem / 12
    c["Férias com 1/3 (1/12 × 4/3)"] = rem / 12 * 4 / 3
    c["FGTS sobre 13º e férias"] = 0.08 * (c["13º salário (1/12)"] + c["Férias com 1/3 (1/12 × 4/3)"])
    dias = 30 + 3 * (anos_aviso - 1)
    c[f"Aviso prévio indenizado (provisão, {dias} dias em {anos_aviso * 12} meses)"] = av = sal * dias / 30 / (12 * anos_aviso)
    c["FGTS sobre o aviso prévio"] = 0.08 * av
    c["Multa de 40% do FGTS (provisão)"] = 0.4 * (c["FGTS (8%)"] + c["FGTS sobre 13º e férias"] + c["FGTS sobre o aviso prévio"])
    c["INSS patronal, RAT e terceiros (no DAS)"] = 0.0
    c["Vale-transporte (parte do empregador)"] = max(0.0, 2 * TARIFA_VT * dias_sem * SEMANAS_MES - 0.06 * sal) if vt else 0.0
    ks = list(c)
    c["Custo mensal"] = rem + sum(c[k] for k in ks[ks.index("Remuneração") + 1:])
    return c


def pessoal_detalhe(quadro, etapa: str = "etapa1") -> dict:
    """Por cargo: remuneração média por pessoa e custo linha a linha de cada pessoa da escala."""
    out = {}
    for cargo, _, q, s, _ in quadro:
        pessoas = [custo_empregado(s, cargo, fl, etapa=etapa) for fl in ETAPAS[etapa][0][cargo]]
        assert len(pessoas) == q, cargo
        out[cargo] = dict(pessoas=pessoas, remuneracao=sum(p["Remuneração"] for p in pessoas) / q)
    return out


def refeicoes_mes(etapa: str = "etapa1") -> float:
    """Refeições da equipe por mês (C15): uma por turno trabalhado."""
    esc = ETAPAS[etapa][0]
    return sum(6 - sum(len(sem) for sem in fl) / len(fl) for cargo in esc for fl in esc[cargo]) * SEMANAS_MES


def encargos_c07(quadro, anos_aviso: int, vt: bool) -> float:
    """Encargos, provisões e vale-transporte ÷ remuneração, na equipe inteira (premissa C07)."""
    rem = enc = 0.0
    for cargo, _, q, s, _ in quadro:
        for fl in ESCALA[cargo]:
            c = custo_empregado(s, cargo, fl, anos_aviso, vt)
            rem += c["Remuneração"]
            enc += c["Custo mensal"] - c["Remuneração"]
    return enc / rem


def premissas(f) -> list[dict]:
    # I01 a I04: totais do orçamento do B5 (P75, mediana e P25 das ofertas; I01 em R$ por m²)
    def b5(pid, col="total"):
        return tuple(round(float(f["b5"].at[pid, f"{col}_{c}"]), 2) for c in CENARIOS)

    def cob(pid):
        r = f["b5"].loc[pid]
        falta = "" if r["itens_com_preco"] == r["itens"] else f", {r['itens'] - r['itens_com_preco']} sem preço ainda"
        return f"{r['itens_com_preco']} de {r['itens']} itens com preço{falta}."
    """Registro de premissas (§3). Percentuais como fração. Ordem = ordem da aba."""
    vis = f["visitas"]
    pg, pm = vis["tamanho_grupo_mesa"], vis["permanencia_mesa_media_min"]
    # circulação no pico: pessoas que entram por hora nas visitas, sem escala pelas mesas (a demanda
    # vem do público, não do salão, até ele lotar); provável na média e otimista na maior visita.
    # Pessimista: NFC-e por dia de cada unidade convertidas em pessoas por hora no pico, com as horas
    # de pico equivalentes dos sete dias do horário da São Jogue pela curva média do índice; média
    # das duas unidades (decisões do autor, 02/11/2026; curva do índice em 12/11/2026)
    circ = vis["pessoas_por_hora"]
    f["circulacao_visitas"] = circ
    eq_sj = sum(f["horas_pico_sj"]["media"].values())
    nf = f["notas"].set_index("unidade")
    por_nota = [nf.loc[u, "notas_emitidas"] / nf.loc[u, "dias"] * 7 / eq_sj for u in ("BV", "PA")]
    circ_nfce = sum(por_nota) / len(por_nota)
    f["circulacao_nfce"], f["horas_pico_sj_semana"] = por_nota, eq_sj
    # gasto por pessoa: média, mínimo e máximo dos gastos médios das casas (B2); parcela da taxa
    gc = f["gasto_casas"]
    gasto = (gc["gasto_medio"].min(), gc["gasto_medio"].mean(), gc["gasto_medio"].max())
    gcc = gc.dropna(subset=["cesta_consumo"])
    parcela = gcc["taxa_ponderada"].mean() / gcc["cesta_consumo"].mean()
    f["gasto_casas_cesta"] = gcc
    f["gasto"], f["parcela_taxa"] = gasto, parcela
    # horas de pico equivalentes: provável e otimista pela curva média do índice, pessimista pela
    # mediana; etapa inicial com fim de semana = sexta e sábado (domingo fechado), dia útil = terça a
    # quinta; a etapa de equipe abre o domingo
    hp, hpm = f["horas_pico"]["media"], f["horas_pico"]["mediana"]
    fds = lambda h: (h["sexta"] + h["sabado"]) / 2
    du = lambda h: (h["terca"] + h["quarta"] + h["quinta"]) / 3
    r15, r15_pess, r05, r05_pess = fds(hp), fds(hpm), du(hp), du(hpm)
    f["r15_exp"] = (hp["sexta"] + hp["sabado"] + hp["domingo"]) / 3
    f["teto_circ"] = MESAS * pg.mean() * 60 / pm.mean()
    # acréscimo salarial máximo (C06), provisório: maior distância entre o 3º quartil
    # e a mediana do salário de admissão entre os cargos do quadro
    c = f["caged"]
    acr = max(float(c[(c["ocupacao"] == o) & (c["recorte"] == rc)].eval("salario_p75 / salario_mediana - 1").iloc[0])
              for o, rc in (("Cozinheiro geral", "CNAE 56 - alimentação"), ("Recreador", "todas as atividades")))
    a = f["acervo"]
    q_ = quadro_pessoal(f)
    refeicoes = refeicoes_mes()
    R = lambda *x: dict(zip(("id", "nome", "unidade", "pess", "prov", "otim", "fonte", "nivel", "just"), x))
    # premissas de valor fixo: lidas de textos/capitulos/modelo_financeiro/P9_premissas_autor.xlsx (edita-se a planilha, não o código)
    au = pd.read_excel(PREMISSAS_AUTOR, sheet_name="premissas", dtype={"id": str}).set_index("id")
    num = lambda x: int(x) if float(x).is_integer() else float(x)
    pessoas_ref = circ.mean() * (r15 * au.at["O06", "provavel"] + r05 * au.at["O07", "provavel"]) * 52 / 12
    u = utilidades(f["area_media"], pessoas_ref)
    f["utilidades"], f["utilidades_pessoas"] = u, pessoas_ref
    A = lambda pid: R(pid, au.at[pid, "nome"], au.at[pid, "unidade"], *[num(au.at[pid, c]) for c in ("pessimista", "provavel", "otimista")],
                      au.at[pid, "fonte"], au.at[pid, "nivel"], au.at[pid, "justificativa"])
    return [
        R("O01", "Mesas do salão", "mesas", MESAS, MESAS, MESAS,
          "Decisão do autor (16/11/2026): 8 mesas e 48 lugares desde a abertura; layout preliminar de 115 a 135 m²", "N6",
          f"Capacidade física completa desde a abertura, sem expansão de mesas nem mudança de imóvel; limita a circulação no pico a {f['teto_circ']:.1f} pessoas por hora (mesas × pessoas por mesa ÷ permanência). O imóvel selecionado, na faixa de 100 a 150 m², deve comportar o layout preliminar de 115 a 135 m²."),
        R("O02", "Pessoas por mesa ocupada", "pessoas", 2.5, round(pg.mean(), 1), 5.5,
          "B3, 4 visitas (out/2026); faixa do autor", "N5 + N6",
          f"Média das visitas {pg.mean():.1f} (de {pg.min():.1f} a {pg.max():.1f}); não entra na receita, só no teto do salão (O01)."),
        R("O03", "Permanência média", "min", 137, round(pm.mean()), 83,
          "B3, 4 visitas (out/2026)", "N5",
          f"Médias por visita de {pm.min():.0f} a {pm.max():.0f} min; não entra na receita, só no teto do salão (O01)."),
        R("R01", "Circulação no pico de fim de semana", "pessoas por hora", *[round(z, 2) for z in (circ_nfce, circ.mean(), circ.max())],
          "B3, 4 visitas nas noites de sexta e sábado e NFC-e entre visitas (out/2026)", "N5",
          f"Pessoas que entram por hora na São Jogue, sem escala pelas mesas: provável na média das visitas e otimista na maior. Pessimista: NFC-e por semana (uma nota por pessoa, só a pedido) ÷ {eq_sj:.2f} h de pico equivalentes nos sete dias do horário da São Jogue (curva média do índice); média da Bela Vista ({por_nota[0]:.2f}) e da Paralela ({por_nota[1]:.2f})."),
        R("R03", "Horas de pico equivalentes por dia útil", "h", round(r05_pess, 2), round(r05, 2), round(r05, 2),
          f"B1: índice \"Horários de pico\" do Google Maps de {f['n_casas_indice']} concorrentes (nov/2026)", "N3",
          f"Soma do índice médio das casas abertas em cada hora do plano (14h às 23h) ÷ índice médio nas janelas das visitas do B3; média de terça ({hp['terca']:.2f}), quarta ({hp['quarta']:.2f}) e quinta ({hp['quinta']:.2f}), {r05 / r15:.1%} do fim de semana. Pessimista pela curva mediana."),
        R("R04", "Gasto por pessoa (cesta de consumo)", "R$ por pessoa", *[round(z, 2) for z in gasto],
          f"B2, preço por pessoa declarado no Google Maps, {int(gc['avaliacoes'].sum())} avaliações de {len(gc)} casas", "N3",
          "Média dos gastos médios das casas com taxa de entrada conhecida; pessimista e otimista na casa de menor e de maior gasto."),
        R("R05", "Taxa de entrada de terça a quinta", "R$ por pessoa", *[round(f["taxa_menor"], 2)] * 3,
          f"B1, média do menor valor da taxa nas {f['taxa_n']} casas que cobram conforme o dia, incluída a São Jogue (seção 6.3)", "N3",
          "Preço adotado nos dias úteis, igual nos cenários; o restante do gasto por pessoa (R04) é A&B. Separa a receita de taxa (anexo III) da de A&B (anexo I e CMV)."),
        R("R06", "Taxa de entrada de sexta a domingo", "R$ por pessoa", *[round(f["taxa_maior"], 2)] * 3,
          f"B1, média do maior valor da taxa nas {f['taxa_n']} casas que cobram conforme o dia, incluída a São Jogue (seção 6.3)", "N3",
          "Preço adotado no fim de semana, igual nos cenários. O gasto por pessoa (R04) é a média da semana: o A&B do mês é o gasto total menos a taxa."),
        A("R07"),
        A("R08"),
        A("R09"),
        A("R10"),
        A("O04"),
        A("O05"),
        R("R02", "Horas de pico equivalentes por dia de fim de semana", "h", round(r15_pess, 2), round(r15, 2), round(r15, 2),
          f"B1: índice \"Horários de pico\" do Google Maps de {f['n_casas_indice']} concorrentes (nov/2026)", "N3",
          f"Soma do índice médio das casas abertas em cada hora do plano ÷ índice médio nas janelas das visitas do B3; média de sexta ({hp['sexta']:.2f}) e sábado ({hp['sabado']:.2f}); com o domingo ({hp['domingo']:.2f}), na etapa de equipe, {f['r15_exp']:.2f}. Pessimista pela curva mediana."),
        A("O06"),
        A("O07"),
        R("C01", "CMV de alimentos e bebidas", "% do A&B", 0.35, 0.30, 0.26,
          "IBGE PAS 2023, serviços de alimentação (B4)", "N2",
          f"Mercadorias e materiais = {f['pas_mercadorias_pct']:.1f}% da receita líquida do setor."),
        A("C02"),
        R("C03", "Área do ponto", "m²", *[round(f["area_media"], 1)] * 3,
          f"B5: {f['aluguel_n']} anúncios de 100 a 150 m² com IPTU informado nos dez bairros de maior renda (OLX, ZAP e Viva Real, nov/2026); decisão do autor", "N3 + N6",
          f"Área mediana dos anúncios de 100 a 150 m² que informam o IPTU ({f['aluguel_n']} de {f['aluguel_n_classe']}; decisão do autor, 15/11/2026)."),
        R("C04", "Aluguel comercial", "R$ por m² ao mês", round(f["aluguel_m2_q"][2], 2), round(f["aluguel_m2_q"][1], 2), round(f["aluguel_m2_q"][0], 2),
          f"B5: {f['aluguel_n']} anúncios de 100 a 150 m² com IPTU informado nos dez bairros de maior renda (OLX, ZAP e Viva Real, nov/2026), sem salas e sem duplicatas", "N3",
          f"Custo total (aluguel + condomínio + IPTU) na mediana dos anúncios, R$ {f['custo_total_q'][1]:,.2f}, no provável, no 3º quartil (R$ {f['custo_total_q'][2]:,.2f}) no pessimista e no 1º (R$ {f['custo_total_q'][0]:,.2f}) no otimista; C04 = custo total ÷ C03 ÷ (1 + C05)."),
        R("C05", "Condomínio e IPTU", "% do aluguel", *[round(f["encargos_pct"], 4)] * 3,
          f"B5: os {f['aluguel_n']} anúncios de 100 a 150 m² com IPTU informado (condomínio vazio = isento)", "N3",
          "Soma do condomínio e do IPTU ÷ soma do aluguel, igual nos três cenários: a faixa do custo total fica na C04."),
        R("C06", "Acréscimo sobre o salário de admissão", "% do salário do CAGED", round(acr, 4), 0.0, 0.0,
          "Novo CAGED, Salvador, 3º quartil ÷ mediana do salário de admissão (B4)", "N2 + N6",
          f"O CAGED registra a admissão, que tende a pagar menos que o estoque; variação só para cima, de 0% a {acr:.1%} (provisório: maior distância do 3º quartil à mediana entre os cargos; x a definir pelo autor)."),
        R("C07", "Encargos, provisões e vale-transporte", "% da remuneração",
          encargos_c07(q_, 1, True), encargos_c07(q_, 5, True), encargos_c07(q_, 5, False),
          "CLT e Lei n. 8.036/1990 (FGTS, 13º, férias, aviso prévio e multa de 40%), Lei n. 7.418/1985 (vale-transporte)", "N1 + N6",
          "No Simples, a contribuição patronal fica no DAS dos anexos I e III. Provável: uma rescisão sem justa causa por vaga em 5 anos; pessimista: uma por ano; otimista: sem vale-transporte."),
        A("C08"),
        R("C09", "Utilidades (energia, água e esgoto, gás, internet)", "R$ por mês",
          *[round(u["total"] * k, 2) for k in (UTIL_FAIXA[0], 1, UTIL_FAIXA[1])],
          "Neoenergia Coelba (ANEEL REH n. 3.578/2026, B3), Embasa (AGERSA n. 001/2026, comercial) e ANP (GLP P13 em Salvador, out-nov/2026); consumos do autor", "N2 + N6",
          f"Energia {u['kwh']:,.0f} kWh a R$ {u['preco_kwh']:.4f} com ICMS e PIS/Cofins (R$ {u['energia']:,.0f}); água {u['m3']:.1f} m³ com esgoto de 80% (R$ {u['agua_esgoto']:,.0f}); GLP {u['glp_kg']:.0f} kg (R$ {u['gas']:,.0f}); internet R$ {u['internet']:,.0f}. Consumo dos equipamentos do B5 nas {HORAS_SEM} h abertas e de {pessoas_ref:,.0f} pessoas por mês no provável; pessimista e otimista com {UTIL_FAIXA[0] - 1:.0%} a mais e {1 - UTIL_FAIXA[1]:.0%} a menos de consumo. Cresce com as horas abertas quando o domingo abre."),
        A("C10"),
        A("C11"),
        A("C12"),
        A("C13"),
        A("C14"),
        R("C15", "Refeições da equipe", "refeições por mês", round(refeicoes, 1), round(refeicoes, 1), round(refeicoes, 1),
          "Escala do cap. 7; decisão do autor (04/11/2026)", "N6", "Uma por turno: dias trabalhados por semana de cada empregado × semanas do mês (etapa inicial; a etapa de equipe soma os turnos da escala com o domingo)."),
        R("I01", "Reforma e instalações", "R$ por m²", *b5("I01", "i01_rs_m2"),
          "B5: SINAPI BA (Caixa, set/2026, com BDI do TCU) e coletas em sites (nov/2026); quantidades do autor", "N2 + N3 + N6",
          f"{cob('I01')} Ponto alugado sem obra estrutural; piso, forro e paredes por cenário; split de 30.000 BTU/h."),
        R("I02", "Mobiliário (mesas, cadeiras, estantes)", "R$", *b5("I02"),
          "B5: coletas na Amazon e no Mercado Livre (nov/2026); quantidades do autor", "N3 + N6",
          f"{cob('I02')} 8 mesas, 44 cadeiras, 8 pendentes, estantes do acervo e armário, em estilo industrial."),
        R("I03", "Cozinha e bar", "R$", *b5("I03"),
          "B5: coletas na Amazon e no Mercado Livre (nov/2026); quantidades do autor", "N3 + N6",
          f"{cob('I03')} Cocção, exaustão, refrigeração, preparo, louça e talheres; lava-louças só no pessimista."),
        R("I04", "Caixa e informática", "R$", *b5("I04"),
          "B5: coletas na Amazon e no Mercado Livre (nov/2026); quantidades do autor", "N3 + N6",
          f"{cob('I04')} Computador, impressora de nota, roteador, som e câmeras; maquininha cedida sem custo a PJ."),
        R("I05", "Acervo inicial de jogos", "R$", *[round(f["acervo_faixa"]["joelho"][c], 2) for c in ("custo_pessimista_rs", "custo_provavel_rs", "custo_otimista_rs")],
          "B1, acervos de 39 concorrentes (out. a nov./2026) e preço de venda nas lojas online", "N3",
          f"Joelho da curva de presença: os {f['acervo_titulos']['joelho']} jogos presentes em 13 ou mais dos 39 acervos (regra do joelho, decisão do autor de 02/11 mantida em 15/11/2026, L39; etapa 1 da P7); provável pela mediana de venda de cada jogo, ± 15% (3º quartil da variação do preço do mesmo jogo entre lojas); a São Jogue lista 370."),
        R("I06", "Gastos pré-operacionais", "R$",
          *[round(PREOP_BASE[c] + MESES_ALUGUEL_IMPLANTACAO * f["custo_total_q"][i], 2) for c, i in (("pessimista", 2), ("provavel", 1), ("otimista", 0))],
          "Estimativa do autor (projeto, licenças, contratação e lançamento) e B5 (aluguel)", "N3 + N6",
          f"Base de R$ {PREOP_BASE['otimista']:,} a R$ {PREOP_BASE['pessimista']:,} (provável R$ {PREOP_BASE['provavel']:,}) mais {MESES_ALUGUEL_IMPLANTACAO} meses de aluguel com condomínio e IPTU entre o contrato e a abertura (Quadro 7.3), pelo custo total do cenário (C03 × C04 × (1 + C05)); decisão do autor, 16/11/2026."),
        A("I07"),
        A("I08"),
        A("I09"),
        A("I10"),
        R("M01", "Taxa mínima de atratividade (real)", "% ao ano", 0.18, 0.15, 0.12,
          "BCB: Selic meta e Focus (B4); prêmio de risco do autor", "N2 + N6",
          f"Juro real de {f['juro_real']:.1f}% (Selic {f['selic']:.1f}% e IPCA esperado de {f['ipca_2027']:.1f}% para 2027) mais 3 a 9 p.p. de risco de pequeno negócio."),
        R("M02", "Semanas por mês", "semanas", 52 / 12, 52 / 12, 52 / 12, "Calendário", "N1", "52 semanas ÷ 12 meses."),
        A("M03"),
    ]


# --------------------------------------------------------------- modelo (Py)
def aliquota(f, anexo: str, rbt: float) -> float:
    t = f["simples"][anexo]
    if rbt <= 0:
        return 0.0
    linha = t[t["rbt12_min"] <= rbt].iloc[-1]
    return max(0.0, (rbt * linha["aliquota_nominal_pct"] / 100 - linha["parcela_deduzir"]) / rbt)


def calcula(f, v: dict, folha: float) -> dict:
    m = []
    # etapa de equipe (só no Monte Carlo, a partir do ano 2): v["EXP"] mantém as 8 mesas e traz as
    # horas de pico e dias de fim de semana com o domingo, além da folha e refeições da escala com 2 cozinheiros
    exp = v.get("EXP")
    for mes in range(1, MESES + 1):
        ano_ = (mes - 1) // 12 + 1
        rampa = min(1.0, v["R09"] + (1 - v["R09"]) * (mes - 1) / (v["R10"] - 1))
        # demanda madura constante depois da rampa (a R18, variação anual a partir do ano 3, saiu em
        # 12/11/2026: estimativa do autor sem dado), limitada pelo salão: mesas × pessoas por mesa
        # ÷ permanência
        etapa = exp if (exp and ano_ >= 2) else None
        mesas = etapa["O01"] if etapa else v["O01"]
        r04 = min(mesas * v["O02"] * 60 / v["O03"], v["R01"])
        r15, r16 = (etapa["R02"], etapa["O06"]) if etapa else (v["R02"], v["O06"])
        p_fds = r04 * r15 * r16 * rampa * v["M02"]
        p_du = r04 * v["R03"] * v["O07"] * rampa * v["M02"]
        taxa_fds, taxa_du = p_fds * v["R06"], p_du * v["R05"]
        ab = (p_fds + p_du) * v["R04"] - taxa_fds - taxa_du
        alug = v["R07"] * v["R08"] * rampa
        m.append(dict(ano=(mes - 1) // 12 + 1, pessoas=p_fds + p_du, taxa=taxa_fds + taxa_du,
                      ab=ab, alug=alug, bruta=taxa_fds + taxa_du + ab + alug, expandido=bool(etapa)))
    m = pd.DataFrame(m)
    rbt = m.groupby("ano")["bruta"].sum()
    al_i = {a: aliquota(f, "I", rbt[a]) for a in rbt.index}
    al_iii = {a: aliquota(f, "III", rbt[a]) for a in rbt.index}
    m["simples"] = m["ab"] * m["ano"].map(al_i) + (m["taxa"] + m["alug"]) * m["ano"].map(al_iii)
    m["cmv"] = m["ab"] * v["C01"]
    m["cartao"] = m["bruta"] * v["C02"]
    aluguel = v["C03"] * v["C04"]

    def custo_fixo(fl, refeicoes, util):
        return (aluguel * (1 + v["C05"]) + fl * (1 + v["C06"]) * (1 + v["C07"]) + v["C08"] + v["C09"] * util
                + v["C10"] + v["C11"] + v["C12"] + v["I05"] * v["C13"] / 12 + v["C14"] * refeicoes)
    fixos = custo_fixo(folha, v["C15"], 1.0)
    m["fixos"] = fixos
    if exp:
        m.loc[m["expandido"], "fixos"] = custo_fixo(exp["folha"], exp["C15"], HORAS_SEM_EXP / HORAS_SEM)
    m["ebitda"] = m["bruta"] - m["simples"] - m["cmv"] - m["cartao"] - m["fixos"]
    inv = dict(reforma=v["I01"] * v["C03"], mobiliario=v["I02"], cozinha=v["I03"], ti=v["I04"],
               acervo=v["I05"], preop=v["I06"], outros=v["I10"], caucao=v["I07"] * aluguel, giro=v["I08"] * fixos)
    total_inv = sum(inv.values())
    ano = m.groupby("ano")[["bruta", "simples", "cmv", "cartao", "fixos", "ebitda"]].sum()
    residual = v["M03"] * max(0.0, (ano.loc[ANOS, "ebitda"] - reinvestimento(inv)) / v["M01"])
    fc = [-total_inv] + list(ano["ebitda"])
    # com valor residual o negócio continua, e a caução e o capital de giro ficam nele; sem, voltam
    fc[-1] += residual if residual > 0 else inv["caucao"] + inv["giro"]
    desc = [x / (1 + v["M01"]) ** t for t, x in enumerate(fc)]
    vpl = sum(desc)
    acum, payback = 0.0, float("nan")
    for t, d in enumerate(desc):
        if t and acum < 0 <= acum + d:
            payback = t - 1 + (-acum) / d
            break
        acum += d
    mc_pct = 1 - (ano.loc[ANOS, ["simples", "cmv", "cartao"]].sum() / ano.loc[ANOS, "bruta"])
    return dict(vpl=vpl, tir=tir(fc), payback=payback, investimento=total_inv, inv=inv, fc=fc, residual=residual,
                receita_madura=m["bruta"].iloc[-1], pessoas_madura=m["pessoas"].iloc[-1],
                fixos=fixos, ebitda5=ano.loc[ANOS, "ebitda"], mc_pct=mc_pct,
                receita_equilibrio=fixos / mc_pct, alug_madura=m["alug"].iloc[-1], ano=ano, m=m)


def tir(fc: list) -> float:
    def vpl(r):
        return sum(x / (1 + r) ** t for t, x in enumerate(fc))
    lo, hi = -0.99, 10.0
    if vpl(lo) * vpl(hi) > 0:
        return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        if vpl(lo) * vpl(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def valores(prem: list[dict], cenario: str) -> dict:
    return {p["id"]: p[cenario[:4] if cenario != "provavel" else "prov"] for p in prem}


def ruptura(f, prem, folha, pid: str):
    """Valor da premissa que zera o VPL (demais no provável), por bisseção."""
    base = valores(prem, "provavel")
    def vpl(x):
        v = dict(base, **{pid: x})
        return calcula(f, v, folha)["vpl"]
    p0 = base[pid]
    lo, hi = p0 * 0.05, p0 * 6
    if vpl(lo) * vpl(hi) > 0:
        return float("nan")
    for _ in range(80):
        mid = (lo + hi) / 2
        if vpl(lo) * vpl(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def pert(rng, lo, moda, hi):
    """Sorteio da distribuição PERT (beta com moda e extremos dados)."""
    if hi <= lo:
        return lo
    a = 1 + 4 * (moda - lo) / (hi - lo)
    b = 1 + 4 * (hi - moda) / (hi - lo)
    return lo + (hi - lo) * rng.betavariate(a, b)


def calcula_mc(f, v: dict, folha: float, quadro) -> dict:
    """Um cenário do Monte Carlo com as decisões de gestão do cap. 10 (02/11/2026):
    - etapa de equipe: se a demanda sorteada no pico (R01) alcança GATILHO_MESAS, isto é, 87,5% da
      capacidade de 8 mesas, a partir do ano 2 passa a considerar 3 instrutores, 2 cozinheiros e o
      domingo das 14h às 20h (f["exp"]). As 8 mesas já estão instaladas na abertura (MC_EXPANSAO = 0);
    - G5: ano (a partir do 2) com EBITDA negativo corta, no ano seguinte, um cozinheiro
      (cardápio de comidas recebidas prontas), com encargos;
    - G6: se o EBITDA segue negativo com o G5 ativo, a luderia fecha no fim desse ano e recupera
      caução, capital de giro e a revenda dos ativos (I09); sem valor residual."""
    teto = v["O01"] * v["O02"] * 60 / v["O03"]
    expande = v["R01"] >= GATILHO_MESAS * teto
    w = dict(v, EXP=f["exp"]) if expande else v
    r = calcula(f, w, folha)
    inv, ano = r["inv"], r["ano"]
    deprec = reinvestimento(inv)
    corte = pessoal_detalhe(quadro)["Cozinheiro-chefe"]["remuneracao"] * 12 * (1 + v["C06"]) * (1 + v["C07"])
    revenda = v["I09"] * (inv["mobiliario"] + inv["cozinha"] + inv["ti"] + inv["acervo"])
    fc = [-r["investimento"], float(ano.loc[1, "ebitda"])]
    if expande:
        fc[1] -= v["I02"] * MC_EXPANSAO / v["O01"]
    g5, fechou, e = False, False, 0.0
    for t in range(2, ANOS + 1):
        e = float(ano.loc[t, "ebitda"]) + (corte if g5 else 0.0)
        if g5 and e < 0:
            fc.append(e + inv["caucao"] + inv["giro"] + revenda)
            fc += [0.0] * (ANOS - t)
            fechou = True
            break
        fc.append(e)
        g5 = g5 or e < 0
    fc_sem = list(fc)
    if not fechou:
        res = v["M03"] * max(0.0, (e - deprec) / v["M01"])
        fc[-1] += res if res > 0 else inv["caucao"] + inv["giro"]
        fc_sem[-1] += inv["caucao"] + inv["giro"]
    desc = [x / (1 + v["M01"]) ** t for t, x in enumerate(fc)]
    acum, payback = 0.0, float("nan")
    for t, dsc in enumerate(desc):
        if t and acum < 0 <= acum + dsc:
            payback = t - 1 + (-acum) / dsc
            break
        acum += dsc
    vpl_sem = sum(x / (1 + v["M01"]) ** t for t, x in enumerate(fc_sem))
    return dict(vpl=sum(desc), payback=payback, expande=expande, g5=g5, fechou=fechou,
                vpl_sem=vpl_sem, tir=tir(fc), tir_sem=tir(fc_sem), investimento=r["investimento"],
                receita_madura=r["receita_madura"], equilibrio=r["receita_equilibrio"],
                ebitda5=0.0 if fechou else e)


def monte_carlo(f, prem, folha, quadro) -> dict:
    """Simulação de Monte Carlo (§4.4): PERT entre o pessimista e o otimista, moda no provável, salvo
    MC_FAIXA (faixa própria), MC_FIXAS (fora do sorteio) e as mesas ocupadas, que sorteiam a demanda até
    o maior valor visto nas visitas; premissas independentes entre si; gatilhos e etapa em calcula_mc."""
    rng = random.Random(SEMENTE)
    base = valores(prem, "provavel")
    vpls, paybacks, exp, g5, fech, linhas = [], [], 0, 0, 0, []
    for _ in range(N_SIMULACOES):
        v = dict(base)
        for p in prem:
            if p["id"] in MC_FIXAS or (p["pess"] == p["otim"] and p["id"] not in MC_FAIXA):
                continue
            lo, hi = MC_FAIXA.get(p["id"], (min(p["pess"], p["otim"]), max(p["pess"], p["otim"])))
            v[p["id"]] = pert(rng, lo, p["prov"], hi)
        r = calcula_mc(f, v, folha, quadro)
        vpls.append(r["vpl"])
        paybacks.append(r["payback"])
        exp += r["expande"]; g5 += r["g5"]; fech += r["fechou"]
        linhas.append(r)
    s = pd.Series(vpls)
    pb = pd.Series(paybacks)
    n = N_SIMULACOES
    # P10, mediana e P90 de cada indicador, cada um na sua própria distribuição (Tabela 9.4): payback
    # que não fecha em 5 anos conta como infinito e TIR inexistente (fluxo sem troca de sinal), como -infinito
    ind = pd.DataFrame(linhas)
    ind["payback"] = ind["payback"].fillna(float("inf"))
    for c in ("tir", "tir_sem"):
        ind[c] = ind[c].fillna(float("-inf"))
    cols = ["investimento", "receita_madura", "equilibrio", "ebitda5", "vpl", "vpl_sem", "tir", "tir_sem", "payback"]
    percentis = {c: {q: float(ind[c].quantile(q, interpolation="nearest")) for q in (.10, .50, .90)} for c in cols}
    return dict(vpls=vpls, percentis=percentis, prob_positivo=(s > 0).mean(), media=s.mean(),
                # percentis pelo cenário mais próximo, como os da Tabela 8 (mesma mediana nas duas tabelas)
                **{k: s.quantile(q, interpolation="nearest") for k, q in (("p05", .05), ("p10", .10), ("p25", .25), ("mediana", .50),
                                                                          ("p75", .75), ("p90", .90), ("p95", .95))},
                payback_5anos=pb.notna().mean(), payback_mediana=pb.dropna().median() if pb.notna().any() else float("nan"),
                expansao=exp / n, g5=g5 / n, fechamento=fech / n,
                erro_prob=((s > 0).mean() * (1 - (s > 0).mean()) / n) ** 0.5)


# --------------------------------------------------------------- planilha
FONTE = Font(name="Arial", size=10, color="000000")
NEGRITO = Font(name="Arial", size=10, color="000000", bold=True)
BRANCO = PatternFill("solid", fgColor="FFFFFF")
FINA = Side(style="thin", color="000000")
MOEDA, PCT, DEC1, DEC2, INT = "#,##0.00", "0.00%", "#,##0.0", "#,##0.00", "#,##0"
COL_MES = [get_column_letter(3 + i) for i in range(MESES)]  # C..BJ



SUMARIO_ABAS = {
    "premissas": "Premissas do modelo, com os três cenários, a fonte e o código do tipo de evidência; o cenário ativo fica em D2",
    "pessoal": "Quadro de pessoal, salários, encargos e benefícios",
    "simples": "Tributação pelo Simples Nacional",
    "receitas": "Receitas projetadas",
    "custos": "Custos fixos e variáveis",
    "investimento": "Investimento inicial",
    "aluguel_faixas": "Anúncios de aluguel dos dez bairros por classe de 25 m² de área e o recorte do ponto (C03 a C05)",
    "utilidades": "Energia, água e esgoto, gás e internet pelas tarifas vigentes (C09)",
    "dre": "Demonstração do resultado do exercício",
    "fluxo_caixa": "Fluxo de caixa projetado",
    "indicadores": "VPL, TIR, payback e ponto de equilíbrio",
    "sensibilidade": "Tornado e ponto de ruptura das premissas",
    "monte_carlo": "Simulação de Monte Carlo do VPL",
    "checagens": "Conferências de consistência do modelo",
    "sobre": "Origem do arquivo e sincronia com o modelo",
}


def sumario(wb, titulo_planilha):
    """Primeira aba: lista as demais abas, com link e descrição (regra das planilhas dos planos)."""
    ws = wb.create_sheet("sumario", 0)
    ws["A1"] = titulo_planilha
    ws["A1"].font = NEGRITO
    ws["A3"], ws["B3"] = "Aba", "Conteúdo"
    ws["A3"].font = ws["B3"].font = NEGRITO
    for i, nome in enumerate(wb.sheetnames[1:], 4):
        c = ws.cell(i, 1, nome)
        c.hyperlink = f"#'{nome}'!A1"
        c.font = Font(name="Arial", size=10, color="0563C1", underline="single")
        ws.cell(i, 2, SUMARIO_ABAS.get(nome, ""))
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 100
    wb.active = 0

def titulo(ws, texto, ncol):
    ws.cell(1, 1, texto)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncol)


def estilo(ws, linha_cab, ultima, ncol, fmt=None):
    """Arial 10, fundo branco, cabeçalho centralizado em negrito com borda em cima e embaixo,
    borda inferior na última linha; texto à esquerda e número à direita."""
    for row in ws.iter_rows(min_row=1, max_row=max(ws.max_row, ultima), max_col=ncol):
        for c in row:
            c.font, c.fill = FONTE, BRANCO
            if c.row == 1:
                c.font, c.alignment = NEGRITO, Alignment(horizontal="center")
            elif c.row == linha_cab:
                c.font = NEGRITO
                c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                c.border = Border(top=FINA, bottom=FINA)
            elif linha_cab < c.row <= ultima:
                txt = isinstance(c.value, str) and not str(c.value).startswith("=")
                c.alignment = Alignment(horizontal="left" if txt else "right", vertical="top", wrap_text=txt)
                if c.row == ultima:
                    c.border = Border(bottom=FINA)
                if fmt and not txt and c.column > 1:
                    c.number_format = fmt


def nota(ws, linha, texto, ncol):
    ws.cell(linha, 1, texto).font = FONTE
    ws.cell(linha, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=linha, start_column=1, end_row=linha, end_column=ncol)
    ws.row_dimensions[linha].height = 15 * max(1, len(texto) // 110 + 1)


def planilha(f, prem, quadro, resultados, tornado, rupt, mc, sem_residual):
    wb = openpyxl.Workbook()
    # ---- premissas
    ws = wb.active
    ws.title = "premissas"
    titulo(ws, "Registro de premissas do modelo financeiro", 11)
    ws["A2"], ws["D2"] = "Cenário ativo (1 = pessimista, 2 = provável, 3 = otimista)", 2
    cab = ["ID", "Premissa", "Unidade", "Pessimista", "Provável", "Otimista", "Valor usado",
           "Fonte", "Código(s)", "Justificativa da faixa", "Impacto no VPL"]
    for j, h in enumerate(cab, 1):
        ws.cell(4, j, h)
    impacto = {t["id"]: ("Alto" if i < 5 else "Médio" if i < 10 else "Baixo") for i, t in enumerate(tornado)}
    linha_de = {}
    for i, p in enumerate(prem):
        r = 5 + i
        linha_de[p["id"]] = r
        for j, k in enumerate(("id", "nome", "unidade", "pess", "prov", "otim"), 1):
            ws.cell(r, j, p[k])
        ws.cell(r, 7, f"=CHOOSE($D$2,D{r},E{r},F{r})")
        ws.cell(r, 8, p["fonte"]); ws.cell(r, 9, p["nivel"]); ws.cell(r, 10, p["just"])
        ws.cell(r, 11, impacto.get(p["id"], "Baixo"))
        wb.defined_names[f"P_{p['id']}"] = DefinedName(f"P_{p['id']}", attr_text=f"premissas!$G${r}")
    ult = 4 + len(prem)
    estilo(ws, 4, ult, 11)
    for p in prem:
        r = linha_de[p["id"]]
        fmt = PCT if p["unidade"].startswith("%") else (MOEDA if p["unidade"].startswith("R$") else DEC2)
        for c in range(4, 8):
            ws.cell(r, c).number_format = fmt
    ws["A2"].font = NEGRITO
    ws["D2"].font = NEGRITO
    nota(ws, ult + 2, "Fonte: elaboração própria com dados dos Blocos B1, B3 e B4 (out/2026). Os códigos N1–N6 identificam tipos de evidência e não uma escala universal de confiabilidade, conforme _docs/_instrucoes/8_financeiro.md. Impacto no VPL pelo tornado (aba sensibilidade): 5 maiores = Alto, 5 seguintes = Médio.", 11)
    for col, w in zip("ABCDEFGHIJK", (6, 34, 16, 12, 12, 12, 12, 36, 9, 52, 10)):
        ws.column_dimensions[col].width = w

    # ---- pessoal
    ws = wb.create_sheet("pessoal")
    titulo(ws, "Quadro de pessoal de referência, salários de admissão em Salvador e adicionais da escala", 7)
    det = pessoal_detalhe(quadro)
    for j, h in enumerate(["Cargo", "CBO", "Quantidade", "Salário mensal (R$)", "Adicionais da escala por pessoa (R$)",
                           "Remuneração total mensal (R$)", "Fonte"], 1):
        ws.cell(2, j, h)
    for i, (cargo, cbo, q, s, fonte) in enumerate(quadro):
        r = 3 + i
        ws.cell(r, 1, cargo); ws.cell(r, 2, cbo); ws.cell(r, 3, q); ws.cell(r, 4, s)
        ws.cell(r, 5, det[cargo]["remuneracao"] - s)
        ws.cell(r, 6, f"=C{r}*(D{r}+E{r})"); ws.cell(r, 7, fonte)
    rt = 3 + len(quadro)
    ws.cell(rt, 1, "Total"); ws.cell(rt, 3, f"=SUM(C3:C{rt - 1})"); ws.cell(rt, 6, f"=SUM(F3:F{rt - 1})")
    estilo(ws, 2, rt, 7)
    for r in range(3, rt + 1):
        ws.cell(r, 3).number_format = INT
        ws.cell(r, 4).number_format = ws.cell(r, 5).number_format = ws.cell(r, 6).number_format = MOEDA
    wb.defined_names["FOLHA_REF"] = DefinedName("FOLHA_REF", attr_text=f"pessoal!$F${rt}")
    wb.defined_names["QUADRO_N"] = DefinedName("QUADRO_N", attr_text=f"pessoal!$C${rt}")
    nota(ws, rt + 2, "Fonte: Novo CAGED (MTE), salário de admissão, mediana, ago/2025 a jul/2026 (B4). Adicionais pela escala de turnos de 7 h "
         "(noturno, hora noturna reduzida, repouso sobre eles e feriados em dobro; CLT, art. 73; Lei n. 605/1949, art. 9º). "
         "Acréscimo salarial e encargos na aba premissas (C06 e C07); custo linha a linha abaixo.", 7)
    # custo linha a linha de cada pessoa da escala (provável)
    r0 = rt + 4
    ws.cell(r0, 1, "Custo mensal por pessoa, cenário provável (R$)")
    linhas = list(det[quadro[0][0]]["pessoas"][0])
    nomes = [f"{cargo} {i + 1}" for cargo, *_ in quadro for i in range(len(det[cargo]["pessoas"]))]
    ws.cell(r0 + 1, 1, "Linha")
    for j, nm in enumerate(nomes, 2):
        ws.cell(r0 + 1, j, nm)
    pessoas = [p for cargo, *_ in quadro for p in det[cargo]["pessoas"]]
    for i, ln in enumerate(linhas):
        ws.cell(r0 + 2 + i, 1, ln)
        for j, p in enumerate(pessoas, 2):
            ws.cell(r0 + 2 + i, j, round(p[ln], 2)).number_format = MOEDA
    estilo(ws, r0 + 1, r0 + 1 + len(linhas), 1 + len(pessoas))
    for col, w in zip("ABCDEFG", (44, 16, 16, 16, 16, 16, 50)):
        ws.column_dimensions[col].width = w

    # ---- simples
    ws = wb.create_sheet("simples")
    titulo(ws, "Simples Nacional: faixas dos anexos I e III e alíquota efetiva por ano", 6)
    blocos = {"I": 4, "III": 13}
    for anexo, r0 in blocos.items():
        ws.cell(r0 - 1, 1, f"Anexo {anexo}")
        for j, h in enumerate(["Faixa", "RBT12 mínima (R$)", "RBT12 máxima (R$)", "Alíquota nominal (%)", "Parcela a deduzir (R$)"], 1):
            ws.cell(r0, j, h)
        for i, row in f["simples"][anexo].iterrows():
            r = r0 + 1 + i
            for j, k in enumerate(("faixa", "rbt12_min", "rbt12_max", "aliquota_nominal_pct", "parcela_deduzir"), 1):
                ws.cell(r, j, float(row[k]) if j > 1 else int(row[k]))
    ws.cell(22, 1, "Ano")
    for a in range(1, ANOS + 1):
        ws.cell(22, 1 + a, a)
    ws.cell(23, 1, "Receita bruta do ano (R$)")
    ws.cell(24, 1, "Alíquota efetiva, anexo I (A&B)")
    ws.cell(25, 1, "Alíquota efetiva, anexo III (taxa de entrada e aluguel de jogos)")
    for a in range(1, ANOS + 1):
        c = get_column_letter(1 + a)
        ws[f"{c}23"] = f"=SUMIF(receitas!$C$3:$BJ$3,{c}22,receitas!$C$12:$BJ$12)"
        for r, r0 in ((24, 4), (25, 13)):
            mins, noms, pds = f"$B${r0 + 1}:$B${r0 + 6}", f"$D${r0 + 1}:$D${r0 + 6}", f"$E${r0 + 1}:$E${r0 + 6}"
            ws[f"{c}{r}"] = f"=IF({c}23<=0,0,MAX(0,({c}23*LOOKUP({c}23,{mins},{noms})/100-LOOKUP({c}23,{mins},{pds}))/{c}23))"
    for row in ws.iter_rows(min_row=1, max_row=25, max_col=6):
        for c in row:
            c.font, c.fill = FONTE, BRANCO
            if isinstance(c.value, (int, float)) and c.column > 1:
                c.alignment = Alignment(horizontal="right")
    ws["A1"].font = NEGRITO
    for r in (3, 4, 12, 13, 22):
        for c in range(1, 7):
            ws.cell(r, c).font = NEGRITO
    for r in (4, 13, 22):
        for c in range(1, 7 if r != 22 else 2 + ANOS):
            ws.cell(r, c).border = Border(top=FINA, bottom=FINA)
            ws.cell(r, c).alignment = Alignment(horizontal="center", wrap_text=True)
    for r in list(range(5, 11)) + list(range(14, 20)):
        for c in (2, 3, 5):
            ws.cell(r, c).number_format = MOEDA
        ws.cell(r, 4).number_format = DEC2
    for a in range(2, 2 + ANOS):
        ws.cell(23, a).number_format = MOEDA
        ws.cell(24, a).number_format = ws.cell(25, a).number_format = PCT
        ws.cell(25, a).border = Border(bottom=FINA)
    ws.cell(25, 1).border = Border(bottom=FINA)
    nota(ws, 27, "Fonte: LC 123/2006, anexos I e III, valores de 2026 (B4). Enquadramento a confirmar no cap. 8: A&B no anexo I (CNAE 5611-2/01); taxa de entrada e aluguel de jogos no anexo III. RBT12 aproximada pela receita do próprio ano.", 6)
    ws.column_dimensions["A"].width = 44
    for col in "BCDEF":
        ws.column_dimensions[col].width = 18

    # ---- receitas (mensal)
    ws = wb.create_sheet("receitas")
    titulo(ws, "Receitas mensais projetadas (preços de out/2026)", 2 + MESES)
    ws["A2"], ws["A3"] = "Mês", "Ano"
    linhas = {4: "Fator de rampa (% da ocupação madura)", 5: "Pessoas, fim de semana", 6: "Pessoas, dia útil",
              7: "Pessoas atendidas", 8: "Taxa de entrada, fim de semana (R$)", 9: "Taxa de entrada, dia útil (R$)",
              10: "Alimentos e bebidas (R$)", 11: "Aluguel de jogos (R$)", 12: "Receita bruta (R$)",
              14: "Circulação no pico (limitada ao salão)",
              16: "Teto da circulação no pico (O01 × O02 × 60 ÷ O03, pessoas por hora)"}
    for r, t in linhas.items():
        ws.cell(r, 1, t)
    ws["B16"] = "=P_O01*P_O02*60/P_O03"
    for i, c in enumerate(COL_MES):
        ws[f"{c}2"] = i + 1
        ws[f"{c}3"] = f"=ROUNDUP({c}2/12,0)"
        ws[f"{c}4"] = f"=MIN(1,P_R09+(1-P_R09)*({c}2-1)/(P_R10-1))"
        ws[f"{c}14"] = f"=MIN($B$16,P_R01)"
        ws[f"{c}5"] = f"={c}14*P_R02*P_O06*{c}4*P_M02"
        ws[f"{c}6"] = f"={c}14*P_R03*P_O07*{c}4*P_M02"
        ws[f"{c}7"] = f"={c}5+{c}6"
        ws[f"{c}8"] = f"={c}5*P_R06"
        ws[f"{c}9"] = f"={c}6*P_R05"
        ws[f"{c}10"] = f"={c}7*P_R04-{c}8-{c}9"
        ws[f"{c}11"] = f"=P_R07*P_R08*{c}4"
        ws[f"{c}12"] = f"=SUM({c}8:{c}11)"
    estilo(ws, 2, 14, 2 + MESES)
    ws["B16"].number_format = DEC2
    for c in COL_MES:
        ws[f"{c}4"].number_format = PCT
        ws[f"{c}14"].number_format = DEC2
        for r in (5, 6, 7):
            ws[f"{c}{r}"].number_format = DEC1
        for r in range(8, 13):
            ws[f"{c}{r}"].number_format = MOEDA
    ws.column_dimensions["A"].width = 40
    ws.freeze_panes = "C4"

    # ---- custos (mensal)
    ws = wb.create_sheet("custos")
    titulo(ws, "Custos e despesas mensais projetados (preços de out/2026)", 2 + MESES)
    ws["A2"], ws["A3"] = "Mês", "Ano"
    linhas = {4: "Simples Nacional (R$)", 5: "CMV de alimentos e bebidas (R$)", 6: "Taxa de cartão (R$)",
              7: "Custos variáveis (R$)", 8: "Aluguel (R$)", 9: "Condomínio e IPTU (R$)",
              10: "Pessoal com encargos (R$)", 11: "Pró-labore (R$)", 12: "Utilidades (R$)", 13: "Marketing (R$)",
              14: "Contabilidade (R$)", 15: "Sistemas (R$)", 16: "Reposição do acervo (R$)",
              17: "Refeição da equipe (R$)", 18: "Custos fixos (R$)", 19: "Custos totais (R$)"}
    for r, t in linhas.items():
        ws.cell(r, 1, t)
    for i, c in enumerate(COL_MES):
        ws[f"{c}2"] = i + 1
        ws[f"{c}3"] = f"=receitas!{c}3"
        ws[f"{c}4"] = (f"=receitas!{c}10*INDEX(simples!$B$24:$F$24,{c}3)"
                       f"+(receitas!{c}8+receitas!{c}9+receitas!{c}11)*INDEX(simples!$B$25:$F$25,{c}3)")
        ws[f"{c}5"] = f"=receitas!{c}10*P_C01"
        ws[f"{c}6"] = f"=receitas!{c}12*P_C02"
        ws[f"{c}7"] = f"=SUM({c}4:{c}6)"
        ws[f"{c}8"] = "=P_C03*P_C04"
        ws[f"{c}9"] = f"={c}8*P_C05"
        ws[f"{c}10"] = "=FOLHA_REF*(1+P_C06)*(1+P_C07)"
        ws[f"{c}11"] = "=P_C08"
        ws[f"{c}12"] = "=P_C09"
        ws[f"{c}13"] = "=P_C10"
        ws[f"{c}14"] = "=P_C11"
        ws[f"{c}15"] = "=P_C12"
        ws[f"{c}16"] = "=P_I05*P_C13/12"
        ws[f"{c}17"] = "=P_C14*P_C15"
        ws[f"{c}18"] = f"=SUM({c}8:{c}17)"
        ws[f"{c}19"] = f"={c}7+{c}18"
    estilo(ws, 2, 19, 2 + MESES, MOEDA)
    for c in COL_MES:
        ws[f"{c}2"].number_format = ws[f"{c}3"].number_format = "0"
    ws.column_dimensions["A"].width = 36
    ws.freeze_panes = "C4"

    # ---- investimento
    ws = wb.create_sheet("investimento")
    titulo(ws, "Investimento inicial e depreciação", 4)
    for j, h in enumerate(["Item", "Valor (R$)", "Vida útil (anos)", "Depreciação anual (R$)", "Reinvestimento anual na perpetuidade (R$)"], 1):
        ws.cell(2, j, h)
    itens = [("Reforma e instalações", "=P_I01*P_C03", VIDA_UTIL["reforma"]), ("Mobiliário", "=P_I02", 10),
             ("Cozinha e bar", "=P_I03", 10), ("Caixa e informática", "=P_I04", 5),
             ("Acervo inicial de jogos", "=P_I05", 5), ("Gastos pré-operacionais", "=P_I06", 5),
             ("Itens sem cotação", "=P_I10", 5),
             ("Caução do aluguel", "=P_I07*custos!$C$8", 0), ("Capital de giro", "=P_I08*custos!$C$18", 0)]
    for i, (n, fo, vida) in enumerate(itens):
        r = 3 + i
        ws.cell(r, 1, n); ws.cell(r, 2, fo); ws.cell(r, 3, vida)
        ws.cell(r, 4, f"=IF(C{r}>0,B{r}/C{r},0)")
        ws.cell(r, 5, f"=D{r}" if n in ("Reforma e instalações", "Mobiliário", "Cozinha e bar", "Caixa e informática", "Itens sem cotação") else 0)
    rt = 3 + len(itens)
    ws.cell(rt, 1, "Total"); ws.cell(rt, 2, f"=SUM(B3:B{rt - 1})"); ws.cell(rt, 4, f"=SUM(D3:D{rt - 1})"); ws.cell(rt, 5, f"=SUM(E3:E{rt - 1})")
    estilo(ws, 2, rt, 5, MOEDA)
    for r in range(3, rt):
        ws.cell(r, 3).number_format = "0"
    nota(ws, rt + 2, "Fonte: aba premissas (I01 a I08, I10, C03). Reforma depreciada em 10 anos. O reinvestimento da perpetuidade repõe só os itens físicos: o acervo já se repõe pela C13 nos custos fixos, e os gastos pré-operacionais não se repetem. Caução e capital de giro voltam no ano 5 só sem valor residual (o negócio fecha). Valor residual na aba fluxo_caixa (M03).", 4)
    ws.column_dimensions["A"].width = 30
    for col in "BCDE":
        ws.column_dimensions[col].width = 18

    # ---- aluguel por classe de área (C03 a C05)
    ws = wb.create_sheet("aluguel_faixas")
    titulo(ws, "Anúncios de aluguel comercial nos dez bairros de maior renda, por classe de área (B5, nov/2026)", 7)
    cab = ["Classe de área (m²)", "Anúncios", "Com IPTU informado", "Área média (m²)", "Aluguel médio (R$)",
           "Custo total médio com IPTU informado (R$)", "Custo total por m² (R$)"]
    for j, h in enumerate(cab, 1):
        ws.cell(2, j, h)
    an = f["aluguel_anuncios_todos"]
    r = 3
    for classe, g in an.groupby("classe_area", observed=False):
        gi = g[g["iptu_informado_sim"]]
        vals = [str(classe), len(g), len(gi), g["area_m2"].mean() if len(g) else None, g["aluguel"].mean() if len(g) else None,
                gi["custo_total"].mean() if len(gi) else None, gi["custo_total"].sum() / gi["area_m2"].sum() if len(gi) else None]
        for j, x in enumerate(vals, 1):
            ws.cell(r, j, None if x is None or x != x else x)
        r += 1
    ws.cell(r, 1, "Total"); ws.cell(r, 2, f"=SUM(B3:B{r - 1})"); ws.cell(r, 3, f"=SUM(C3:C{r - 1})")
    assert an["classe_area"].value_counts().sum() == len(an)  # cada anúncio numa só classe
    estilo(ws, 2, r, 7, MOEDA)
    for rr in range(3, r + 1):
        for cc in (2, 3):
            ws.cell(rr, cc).number_format = "0"
        ws.cell(rr, 4).number_format = DEC2
    nota(ws, r + 2, f"Fonte: B5, anúncios de imóveis comerciais para alugar no OLX, no ZAP e no Viva Real (nov/2026), nos dez bairros da Tabela 6.1, sem salas e sem duplicatas ({len(an)} anúncios). Custo total = aluguel + condomínio (vazio = isento) + IPTU. O ponto usa os anúncios de {AREA_PONTO[0]} a {AREA_PONTO[1]} m² ({f['aluguel_n_classe']} anúncios, {f['aluguel_n']} com IPTU informado): custo total mediano de R$ {f['custo_total_q'][1]:,.2f} por mês, de R$ {f['custo_total_q'][0]:,.2f} (1º quartil) a R$ {f['custo_total_q'][2]:,.2f} (3º quartil) (decisão do autor, 15/11/2026).", 7)
    ws.column_dimensions["A"].width = 20
    for col in "BCDEFG":
        ws.column_dimensions[col].width = 18

    # ---- utilidades (C09)
    ws = wb.create_sheet("utilidades")
    u = f["utilidades"]
    titulo(ws, "Utilidades por mês no provável (C09), pelas tarifas vigentes em nov/2026", 3)
    for j, h in enumerate(["Item", "Quantidade por mês", "Valor (R$ por mês)"], 1):
        ws.cell(2, j, h)
    linhas = [("Energia elétrica (kWh), Neoenergia Coelba, B3", u["kwh"], u["energia"]),
              ("Água e esgoto (m³), Embasa, comercial", u["m3"], u["agua_esgoto"]),
              ("Gás GLP (kg), média do P13 em Salvador (ANP)", u["glp_kg"], u["gas"]),
              ("Internet (plano de fibra)", 1, u["internet"])]
    for i, (n, q, val) in enumerate(linhas, 3):
        ws.cell(i, 1, n); ws.cell(i, 2, q); ws.cell(i, 3, val)
    ws.cell(7, 1, "Total"); ws.cell(7, 3, "=SUM(C3:C6)")
    estilo(ws, 2, 7, 3, MOEDA)
    for rr in range(3, 8):
        ws.cell(rr, 2).number_format = DEC2
    nota(ws, 9, f"Fonte: Neoenergia Coelba, tarifa B3 convencional de R$ {ENERGIA_TARIFA:.5f} por kWh sem tributos (ANEEL, REH n. 3.578/2026), com ICMS de {ENERGIA_ICMS:.1%} e PIS/Cofins de {ENERGIA_PIS_COFINS:.0%} por dentro (R$ {u['preco_kwh']:.4f} por kWh); Embasa, tabela de 2026 (AGERSA n. 001/2026), comercial, R$ {AGUA_FIXA:.2f} até 6 m³ e esgoto de {ESGOTO_PCT:.0%} da água; ANP, GLP P13 em Salvador a R$ {GLP_P13:.2f}. Consumos do autor (N6): equipamentos do orçamento do B5 nas {HORAS_SEM} h abertas por semana, {AGUA_L_PESSOA} L de água e {GLP_KG_PESSOA:.2f} kg de GLP por cliente, com {f['utilidades_pessoas']:,.0f} clientes por mês no provável.", 3)
    for i, (n, kw, uso, h) in enumerate(ENERGIA_EQUIP, 12):
        ws.cell(i, 1, n); ws.cell(i, 2, ILUMINACAO_W_M2 * f["area_media"] / 1000 if kw is None else kw); ws.cell(i, 3, f"{h} h por dia aberto" if uso == "cozinha" else uso)
    ws.cell(11, 1, "Equipamento"); ws.cell(11, 2, "kW médio"); ws.cell(11, 3, "Horas")
    estilo(ws, 11, 11 + len(ENERGIA_EQUIP), 3, DEC2)
    ws.column_dimensions["A"].width = 60
    for col in "BC":
        ws.column_dimensions[col].width = 20

    # ---- dre (anual)
    ws = wb.create_sheet("dre")
    titulo(ws, "Demonstração do resultado projetada (R$, preços de out/2026)", 1 + ANOS)
    ws["A2"] = "Conta"
    for a in range(1, ANOS + 1):
        ws.cell(2, 1 + a, f"Ano {a}")
        ws.cell(3, 1 + a, a)
    ws["A3"] = "Ano (número)"
    soma = lambda aba, lin, c: f"SUMIF({aba}!$C$3:$BJ$3,{c}$3,{aba}!$C${lin}:$BJ${lin})"
    contas = [(4, "Receita bruta", lambda c: "=" + soma("receitas", 12, c)),
              (5, "(-) Simples Nacional", lambda c: "=-" + soma("custos", 4, c)),
              (6, "Receita líquida", lambda c: f"={c}4+{c}5"),
              (7, "(-) CMV de alimentos e bebidas", lambda c: "=-" + soma("custos", 5, c)),
              (8, "(-) Taxa de cartão", lambda c: "=-" + soma("custos", 6, c)),
              (9, "Margem de contribuição", lambda c: f"={c}6+{c}7+{c}8"),
              (10, "(-) Custos fixos", lambda c: "=-" + soma("custos", 18, c)),
              (11, "EBITDA", lambda c: f"={c}9+{c}10"),
              (12, "(-) Depreciação e amortização", lambda c: "=-investimento!$D$12"),
              (13, "Lucro líquido", lambda c: f"={c}11+{c}12"),
              (14, "Margem líquida", lambda c: f"=IF({c}4=0,0,{c}13/{c}4)")]
    for r, n, fo in contas:
        ws.cell(r, 1, n)
        for a in range(1, ANOS + 1):
            c = get_column_letter(1 + a)
            ws[f"{c}{r}"] = fo(c)
    estilo(ws, 2, 14, 1 + ANOS, MOEDA)
    for a in range(2, 2 + ANOS):
        ws.cell(14, a).number_format = PCT
        ws.cell(3, a).number_format = "0"
    nota(ws, 16, "Fonte: abas receitas, custos e investimento. No Simples Nacional, IRPJ e CSLL estão no DAS; não há imposto sobre o lucro à parte.", 1 + ANOS)
    ws.column_dimensions["A"].width = 34
    for a in range(2, 2 + ANOS):
        ws.column_dimensions[get_column_letter(a)].width = 16

    # ---- fluxo de caixa (anual)
    ws = wb.create_sheet("fluxo_caixa")
    titulo(ws, "Fluxo de caixa projetado (R$, preços de out/2026)", 2 + ANOS)
    ws["A2"] = "Linha"
    for t in range(ANOS + 1):
        ws.cell(2, 2 + t, f"Ano {t}")
        ws.cell(3, 2 + t, t)
    ws["A3"] = "Ano (número)"
    rot = {4: "Investimento", 5: "EBITDA", 6: "Retorno da caução e do capital de giro (só sem valor residual)", 7: "Fluxo líquido",
           8: "Fator de desconto", 9: "Fluxo descontado", 10: "Fluxo descontado acumulado",
           11: "Payback descontado (auxiliar)", 12: "Valor residual (perpetuidade sem crescimento, piso zero)"}
    for r, n in rot.items():
        ws.cell(r, 1, n)
    for t in range(ANOS + 1):
        c = get_column_letter(2 + t)
        ws[f"{c}4"] = "=-investimento!$B$12" if t == 0 else 0
        ws[f"{c}5"] = 0 if t == 0 else f"=dre!{get_column_letter(1 + t)}11"
        ws[f"{c}6"] = f"=IF({c}12>0,0,investimento!$B$10+investimento!$B$11)" if t == ANOS else 0
        ws[f"{c}12"] = (f"=P_M03*MAX(0,(dre!{get_column_letter(1 + t)}11-investimento!$E$12)/P_M01)"
                        if t == ANOS else 0)
        ws[f"{c}7"] = f"=SUM({c}4:{c}6)+{c}12"
        ws[f"{c}8"] = f"=1/(1+P_M01)^{c}3"
        ws[f"{c}9"] = f"={c}7*{c}8"
        ws[f"{c}10"] = f"={c}9" if t == 0 else f"={get_column_letter(1 + t)}10+{c}9"
        if t:
            p = get_column_letter(1 + t)
            ws[f"{c}11"] = f'=IF(AND({p}10<0,{c}10>=0),{p}3+(-{p}10)/{c}9,"")'
    estilo(ws, 2, 12, 2 + ANOS, MOEDA)
    for t in range(ANOS + 1):
        c = get_column_letter(2 + t)
        ws[f"{c}3"].number_format = "0"
        ws[f"{c}8"].number_format = "0.0000"
        ws[f"{c}11"].number_format = DEC2
    ws.column_dimensions["A"].width = 38
    for t in range(ANOS + 1):
        ws.column_dimensions[get_column_letter(2 + t)].width = 16

    # ---- indicadores
    ws = wb.create_sheet("indicadores")
    titulo(ws, "Indicadores de viabilidade do cenário ativo", 3)
    for j, h in enumerate(["Indicador", "Valor", "Unidade"], 1):
        ws.cell(2, j, h)
    ind = [("Cenário ativo", '=CHOOSE(P_CEN,"pessimista","provável","otimista")', ""),
           ("Investimento inicial", "=investimento!B12", "R$"),
           ("VPL a TMA real", "=SUM(fluxo_caixa!B9:G9)", "R$"),
           ("TIR real", '=IFERROR(IRR(fluxo_caixa!B7:G7),"não há")', "% ao ano"),
           ("Payback descontado", '=IF(COUNT(fluxo_caixa!C11:G11)=0,"mais de 5 anos",MIN(fluxo_caixa!C11:G11))', "anos"),
           ("Receita bruta mensal madura (mês 60)", "=receitas!BJ12", "R$"),
           ("Custos fixos mensais", "=custos!BJ18", "R$"),
           ("Margem de contribuição (ano 5)", "=dre!F9/dre!F4", "% da receita bruta"),
           ("Receita bruta mensal de equilíbrio", "=B9/B10", "R$"),
           ("Receita madura ÷ receita de equilíbrio", "=B8/B11", "vezes"),
           ("Circulação de equilíbrio no pico de fim de semana (dia útil na mesma proporção)", "=P_R01*(B11-receitas!BJ11)/(B8-receitas!BJ11)", "pessoas por hora"),
           ("Pessoas por dia de equilíbrio, fim de semana", "=B13*P_R02", "pessoas")]
    for i, (n, fo, u) in enumerate(ind):
        ws.cell(3 + i, 1, n); ws.cell(3 + i, 2, fo); ws.cell(3 + i, 3, u)
    rt = 2 + len(ind)
    wb.defined_names["P_CEN"] = DefinedName("P_CEN", attr_text="premissas!$D$2")
    estilo(ws, 2, rt, 3, MOEDA)
    ws["B6"].number_format = PCT
    ws["B7"].number_format = DEC2
    ws["B11"].number_format = MOEDA
    ws["B10"].number_format = PCT
    ws["B13"].number_format = ws["B14"].number_format = DEC2
    ws["B12"].number_format = DEC2
    ws["B3"].alignment = Alignment(horizontal="right")
    nota(ws, rt + 2, "Fonte: abas fluxo_caixa, dre, receitas e custos. Circulação de equilíbrio por aproximação linear: a receita sem o aluguel de jogos cresce na proporção da circulação.", 3)
    ws.column_dimensions["A"].width = 58
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 20

    # ---- sensibilidade (valores do Python)
    ws = wb.create_sheet("sensibilidade")
    titulo(ws, "Cenários, tornado e pontos de ruptura (calculados pelo script com as mesmas fórmulas)", 7)
    for j, h in enumerate(["Cenário", "Investimento (R$)", "Receita mensal madura (R$)", "EBITDA do ano 5 (R$)", "VPL (R$)", "TIR real", "Payback descontado (anos)"], 1):
        ws.cell(2, j, h)
    for i, cen in enumerate(CENARIOS):
        res = resultados[cen]
        r = 3 + i
        vals = [("pessimista", "provável", "otimista")[i], res["investimento"], res["receita_madura"], res["ebitda5"],
                res["vpl"], res["tir"] if res["tir"] == res["tir"] else "não há",
                res["payback"] if res["payback"] == res["payback"] else "mais de 5"]
        for j, x in enumerate(vals, 1):
            ws.cell(r, j, x)
    estilo(ws, 2, 5, 7, MOEDA)
    for r in range(3, 6):
        ws.cell(r, 6).number_format = PCT
        ws.cell(r, 7).number_format = DEC2
    r0 = 8
    ws.cell(r0 - 1, 1, "Tornado: VPL com a premissa no extremo e as demais no provável")
    for j, h in enumerate(["ID", "Premissa", "VPL no pessimista (R$)", "VPL no otimista (R$)", "Amplitude (R$)", "Ordem"], 1):
        ws.cell(r0, j, h)
    for i, t in enumerate(tornado):
        r = r0 + 1 + i
        for j, x in enumerate((t["id"], t["nome"], t["vpl_pess"], t["vpl_otim"], t["amplitude"], i + 1), 1):
            ws.cell(r, j, x)
    ultt = r0 + len(tornado)
    r1 = ultt + 3
    ws.cell(r1 - 1, 1, "Ponto de ruptura das premissas críticas (VPL = 0, demais no provável)")
    for j, h in enumerate(["ID", "Premissa", "Pessimista", "Provável", "Otimista", "Valor de ruptura", "Unidade"], 1):
        ws.cell(r1, j, h)
    for i, rp in enumerate(rupt):
        r = r1 + 1 + i
        for j, x in enumerate((rp["id"], rp["nome"], rp["pess"], rp["prov"], rp["otim"],
                               rp["ruptura"] if rp["ruptura"] == rp["ruptura"] else "fora do intervalo testado", rp["unidade"]), 1):
            ws.cell(r, j, x)
    ultr = r1 + len(rupt)
    # estilo dos três blocos
    for row in ws.iter_rows(min_row=1, max_row=ultr + 3, max_col=7):
        for c in row:
            c.font, c.fill = FONTE, BRANCO
    for rc, ru in ((2, 5), (r0, ultt), (r1, ultr)):
        for c in range(1, 8):
            ws.cell(rc, c).font = NEGRITO
            ws.cell(rc, c).alignment = Alignment(horizontal="center", wrap_text=True, vertical="center")
            ws.cell(rc, c).border = Border(top=FINA, bottom=FINA)
            ws.cell(ru, c).border = Border(bottom=FINA)
        for r in range(rc + 1, ru + 1):
            for c in range(1, 8):
                v = ws.cell(r, c).value
                ws.cell(r, c).alignment = Alignment(horizontal="left" if isinstance(v, str) else "right", wrap_text=True)
    ws["A1"].font = NEGRITO
    ws["A1"].alignment = Alignment(horizontal="center")
    for r in (r0 - 1, r1 - 1):
        ws.cell(r, 1).font = NEGRITO
    for r in range(r0 + 1, ultt + 1):
        for c in (3, 4, 5):
            ws.cell(r, c).number_format = MOEDA
    for i, rp in enumerate(rupt):
        r = r1 + 1 + i
        fmt = PCT if rp["unidade"].startswith("%") else (MOEDA if rp["unidade"].startswith("R$") else DEC2)
        for c in (3, 4, 5, 6):
            ws.cell(r, c).number_format = fmt
    r2 = ultr + 3
    ws.cell(r2 - 1, 1, "VPL com e sem valor residual (M03)").font = NEGRITO
    for j, h in enumerate(["Cenário", "Valor residual no ano 5 (R$)", "VPL com (R$)", "VPL sem (R$)", "Diferença (R$)"], 1):
        ws.cell(r2, j, h).font = NEGRITO
    for i, cen in enumerate(CENARIOS):
        com, sem = resultados[cen], sem_residual[cen]
        for j, x in enumerate((("pessimista", "provável", "otimista")[i], com["residual"], com["vpl"], sem["vpl"], com["vpl"] - sem["vpl"]), 1):
            ws.cell(r2 + 1 + i, j, x)
            if j > 1:
                ws.cell(r2 + 1 + i, j).number_format = MOEDA
    ultr = r2 + len(CENARIOS)
    nota(ws, ultr + 2, "Fonte: elaboração própria. Valores gravados pelo script _src/outros/gerar_modelo_financeiro.py, que recalcula o modelo em Python e confere o VPL com esta planilha nos três cenários; mudar a aba premissas não atualiza esta aba (rodar o script de novo).", 7)
    for col, w in zip("ABCDEFG", (12, 44, 18, 18, 18, 18, 18)):
        ws.column_dimensions[col].width = w

    # ---- monte carlo (valores do Python)
    ws = wb.create_sheet("monte_carlo")
    titulo(ws, f"Simulação de Monte Carlo: {N_SIMULACOES:,} cenários".replace(",", "."), 2)
    for j, h in enumerate(["Medida", "Valor"], 1):
        ws.cell(2, j, h)
    medidas = [("Probabilidade de VPL > 0", mc["prob_positivo"], PCT), ("VPL médio (R$)", mc["media"], MOEDA),
               ("VPL, percentil 5 (R$)", mc["p05"], MOEDA), ("VPL, percentil 25 (R$)", mc["p25"], MOEDA),
               ("VPL, mediana (R$)", mc["mediana"], MOEDA), ("VPL, percentil 75 (R$)", mc["p75"], MOEDA),
               ("VPL, percentil 95 (R$)", mc["p95"], MOEDA),
               ("Probabilidade de payback descontado em até 5 anos", mc["payback_5anos"], PCT),
               ("Payback descontado mediano, entre os que se pagam (anos)", mc["payback_mediana"], DEC2),
               ("VPL, percentil 10 (R$)", mc["p10"], MOEDA), ("VPL, percentil 90 (R$)", mc["p90"], MOEDA),
               ("Cenários com a etapa de equipe", mc["expansao"], PCT), ("Cenários com o gatilho G5", mc["g5"], PCT),
               ("Cenários encerrados pelo gatilho G6", mc["fechamento"], PCT),
               ("Erro padrão da probabilidade de VPL > 0", mc["erro_prob"], PCT)]
    for i, (n, x, fmt) in enumerate(medidas):
        ws.cell(3 + i, 1, n)
        ws.cell(3 + i, 2, x if x == x else "não há")
        ws.cell(3 + i, 2).number_format = fmt
    rt = 2 + len(medidas)
    estilo(ws, 2, rt, 2)
    for i, (_, _, fmt) in enumerate(medidas):
        ws.cell(3 + i, 2).number_format = fmt
    # percentis de cada indicador (Tabela 9.4 do cap. 9)
    rp = rt + 4
    ws.cell(rp - 1, 1, "Indicadores: percentis 10, 50 e 90 de cada um na simulação").font = NEGRITO
    for j, h in enumerate(["Indicador", "P10", "Mediana", "P90"], 1):
        ws.cell(rp, j, h).font = NEGRITO
    nomes = [("investimento", "Investimento inicial (R$)", MOEDA), ("receita_madura", "Receita bruta mensal madura (R$)", MOEDA),
             ("equilibrio", "Ponto de equilíbrio mensal (R$)", MOEDA), ("ebitda5", "EBITDA do ano 5 (R$)", MOEDA),
             ("vpl", "VPL (R$)", MOEDA), ("vpl_sem", "VPL sem valor residual (R$)", MOEDA),
             ("tir", "TIR real", PCT), ("tir_sem", "TIR real sem valor residual", PCT),
             ("payback", "Payback descontado (anos)", DEC2)]
    for i, (k, nome, fmt) in enumerate(nomes):
        ws.cell(rp + 1 + i, 1, nome)
        for j, q in enumerate((.10, .50, .90), 2):
            x = mc["percentis"][k][q]
            ws.cell(rp + 1 + i, j, x if abs(x) != float("inf") else ("mais de 5" if k == "payback" else "não há"))
            ws.cell(rp + 1 + i, j).number_format = fmt
    rt = rp + len(nomes)
    ws.column_dimensions["C"].width = ws.column_dimensions["D"].width = 18
    nota(ws, rt + 2, "Fonte: elaboração própria. Distribuição PERT contínua entre o pessimista e o otimista da aba premissas, com moda no "
         "provável, salvo: pessoas por mesa de 2 a 6; TMA fixa "
         "no provável; valor residual realizado de 0 a 1, moda em 1 (M03). Demanda no pico a 87,5% do salão abre a etapa de equipe "
         "(instrutor, segundo cozinheiro e domingo) a partir do ano 2, sem mesas novas; EBITDA anual negativo a partir do ano 2 aciona o G5 "
         "(corte de um cozinheiro) e, se persistir, o G6 (encerramento com revenda dos ativos, I09). "
         f"Premissas independentes entre si; semente {SEMENTE}. Valores gravados pelo script.", 2)
    ws.column_dimensions["A"].width = 58
    ws.column_dimensions["B"].width = 18

    # ---- checagens de coerência (§5) e triangulação (§4.1)
    ws = wb.create_sheet("checagens")
    titulo(ws, "Triangulação da receita e checagens de coerência (cenário ativo, mês 60)", 4)
    for j, h in enumerate(["Checagem", "Modelo", "Referência", "Fonte da referência"], 1):
        ws.cell(2, j, h)
    notas = f["notas"].set_index("unidade")
    ch = [
        ("Pessoas atendidas por dia", "=receitas!BJ7/(P_M02*7)", "=P_O01*P_O02*(P_O04+P_O05)*60/P_O03/7",
         "Capacidade: todas as mesas ocupadas todas as horas, com a permanência média"),
        ("Uso da capacidade", "=B3/C3", "", "Tem de ficar abaixo de 100%"),
        ("Mesas ocupadas no pico ÷ mesas do salão", "=P_R01*P_O03/60/P_O02/P_O01", "", "Tem de ficar abaixo de 100%"),
        ("Horas de pico equivalentes por dia de fim de semana", "=P_R02", "=P_O04/P_O06",
         "Horas abertas por dia de fim de semana: as horas de pico equivalentes têm de caber no horário"),
        ("Pessoas atendidas por dia × NFC-e da Bela Vista", "=B3", float(notas.loc["BV", "notas_emitidas"] / notas.loc["BV", "dias"]),
         "NFC-e emitidas por dia, São Jogue Bela Vista, 10/10 a 16/10/2026 (B3); nota emitida só a pedido, sem medida de pessoas por nota: ordem de grandeza"),
        ("Pessoas atendidas por dia × NFC-e da Paralela", "=B3", float(notas.loc["PA", "notas_emitidas"] / notas.loc["PA", "dias"]),
         "NFC-e por dia, São Jogue Paralela, 17/10 a 30/10/2026 (B3), com o fim de semana da eleição; ordem de grandeza"),
        ("Receita por pessoa (R$)", "=receitas!BJ12/receitas!BJ7", float(f["gasto_casas_cesta"]["cesta_consumo"].mean()),
         "Cesta de consumo média (taxa de entrada + bebida + hambúrguer) das casas da R04 (B1)"),
        ("Taxa de entrada média por pessoa (R$)", "=(receitas!BJ8+receitas!BJ9)/receitas!BJ7", float(f["taxa_b1_mediana"]),
         f"Mediana do couvert ou taxa de jogo nos cardápios de {f['taxa_b1_n']} concorrentes (B1)"),
        ("Pessoas atendidas por dia por funcionário", "=B3/QUADRO_N", "",
         "Equipe do desenho enxuto (aba pessoal)"),
        ("Visitas por ano ÷ população de Salvador", "=receitas!BJ7*12/C12", float(f["pop_salvador"]),
         "População estimada de Salvador em 2026 (IBGE, B4); visitas, não pessoas distintas"),
        ("Meses até a maturidade", "=P_R10", "", "Entre 6 e 12 meses (estimativa do autor)"),
    ]
    for i, (n, mo, ref, fonte) in enumerate(ch):
        r = 3 + i
        ws.cell(r, 1, n); ws.cell(r, 2, mo); ws.cell(r, 3, ref if ref != "" else None); ws.cell(r, 4, fonte)
    rt = 2 + len(ch)
    estilo(ws, 2, rt, 4, DEC2)
    ws["B4"].number_format = ws["B5"].number_format = ws["B12"].number_format = "0.000%"
    for r in (9, 10):
        ws[f"B{r}"].number_format = ws[f"C{r}"].number_format = MOEDA
    ws["C12"].number_format = INT
    nota(ws, rt + 2, "Fonte: abas do modelo e Blocos B1, B3 e B4. A comparação com as notas é de ordem de grandeza: a NFC-e só é emitida quando o cliente pede.", 4)
    for col, w in zip("ABCD", (48, 18, 18, 70)):
        ws.column_dimensions[col].width = w
    sumario(wb, "P9 - Plano financeiro: modelo da luderia")
    return wb


# --------------------------------------------------------------- conferência
def recalcula(xlsx: Path, cenario: int) -> float:
    """Abre uma cópia no LibreOffice com o cenário dado, recalcula e devolve o VPL."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wb = openpyxl.load_workbook(xlsx)
        wb["premissas"]["D2"] = cenario
        src = tmp / "modelo.xlsx"
        wb.save(src)
        out = tmp / "out"
        subprocess.run([SOFFICE, "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                       check=True, capture_output=True, timeout=180)
        v = openpyxl.load_workbook(out / "modelo.xlsx", data_only=True)
        erros = [f"{ws.title}!{c.coordinate}" for ws in v for row in ws.iter_rows() for c in row
                 if isinstance(c.value, str) and c.value.startswith(("#", "Err:"))]
        if erros:
            raise SystemExit(f"Erros de fórmula no LibreOffice: {erros[:10]}")
        return v["indicadores"]["B5"].value


def figura_tornado(tornado, base_vpl):
    top = tornado[:10][::-1]
    fig, ax = plt.subplots(figsize=(6.3, 4.2), dpi=300)
    y = range(len(top))
    mil = lambda x: x / 1000
    for i, t in enumerate(top):
        ax.barh(i, mil(t["vpl_pess"] - base_vpl), left=mil(base_vpl), height=0.6, color="#54278f", label="Premissa no pessimista" if i == 0 else None)
        ax.barh(i, mil(t["vpl_otim"] - base_vpl), left=mil(base_vpl), height=0.6, color="#bcbddc", label="Premissa no otimista" if i == 0 else None)
    ax.axvline(mil(base_vpl), color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8, linestyle=":")
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{t['id']} {t['nome']}" for t in top], fontsize=7, fontname="Arial")
    ax.set_xlabel("VPL (R$ mil)", fontsize=8, fontname="Arial")
    ax.tick_params(axis="x", labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(prop={"family": "Arial", "size": 7}, frameon=False, loc="lower right")
    for t in ax.get_xticklabels():
        t.set_fontname("Arial")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout()
    FIGURA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURA, facecolor="white")
    plt.close(fig)


def figura_monte_carlo(mc):
    fig, ax = plt.subplots(figsize=(6.3, 3.6), dpi=300)
    mil = [x / 1000 for x in mc["vpls"]]
    ax.hist(mil, bins=60, color="#7f7f7f", edgecolor="white", linewidth=0.3)
    ax.axvline(0, color="black", linewidth=0.8, linestyle=":", label="VPL = 0")
    ax.axvline(mc["mediana"] / 1000, color="black", linewidth=0.8,
               label=f"Mediana (R$ {mc['mediana'] / 1000:,.0f} mil)".replace(",", "."))
    ax.legend(fontsize=7, frameon=False, prop={"family": "Arial", "size": 7})
    ax.set_xlabel("VPL (R$ mil)", fontsize=8, fontname="Arial")
    ax.set_ylabel("Cenários simulados", fontsize=8, fontname="Arial")
    ax.tick_params(labelsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for t in ax.get_xticklabels() + ax.get_yticklabels():
        t.set_fontname("Arial")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))
    fig.tight_layout()
    fig.savefig(FIGURA_MC, facecolor="white")
    plt.close(fig)


def gravar_premissas(df: pd.DataFrame, destino: Path, titulo_aba: str) -> None:
    """Grava as premissas em .xlsx (aba premissas), com cabeçalho na linha 1, para leitura direta pelo pandas."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(destino, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="premissas", index=False)
        ws = xw.sheets["premissas"]
        for c in ws[1]:
            c.font = NEGRITO
        for col, w in zip("ABCDEFGHI", (6, 40, 18, 12, 12, 12, 50, 10, 70)):
            ws.column_dimensions[col].width = w
        ws.freeze_panes = "B2"
        info = xw.book.create_sheet("sobre")
        info["A1"] = titulo_aba
        info["A2"] = (f"Sincronizado com textos/planilhas/{SAIDA.name} (aba premissas): o modelo confere a cada execução, "
                      "e python3 _src/outros/G3_modelo_financeiro/gerar_modelo_financeiro.py --conferir confere sem regerar.")
        sumario(xw.book, titulo_aba)


def conferir_sincronia() -> None:
    """Confere se o registro, as premissas do autor e a aba premissas do modelo .xlsx têm os mesmos valores."""
    def norm(x):
        if x is None or (isinstance(x, float) and x != x):
            return ""
        return round(float(x), 6) if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x).strip()
    ws = openpyxl.load_workbook(SAIDA, read_only=True)["premissas"]
    modelo = {}
    for linha in ws.iter_rows(min_row=5, values_only=True):
        if not linha[0] or str(linha[0]).startswith("Fonte"):
            break
        modelo[str(linha[0])] = [norm(v) for v in (linha[1], linha[2], linha[3], linha[4], linha[5], linha[7], linha[8], linha[9])]
    erros = []
    cols = ["nome", "unidade", "pessimista", "provavel", "otimista", "fonte", "nivel", "justificativa"]
    for nome_arq, arq in (("registro", REGISTRO), ("autor", PREMISSAS_AUTOR)):
        df = pd.read_excel(arq, sheet_name="premissas", dtype={"id": str})
        for r in df.itertuples(index=False):
            esperado = modelo.get(r.id)
            achado = [norm(getattr(r, c)) for c in cols]
            if esperado is None:
                erros.append(f"{nome_arq}: {r.id} fora da aba premissas do modelo")
            elif achado != esperado:
                difs = [c for c, a, b in zip(cols, achado, esperado) if a != b]
                erros.append(f"{nome_arq}: {r.id} diverge do modelo em {', '.join(difs)}")
        if nome_arq == "registro" and set(df.id) != set(modelo):
            erros.append(f"registro: ids {sorted(set(modelo) ^ set(df.id))} sem par")
    if erros:
        raise SystemExit("Premissas fora de sincronia com o modelo:\n- " + "\n- ".join(erros))
    print(f"Sincronia: {REGISTRO.name} e {PREMISSAS_AUTOR.name} = aba premissas de {SAIDA.name} ({len(modelo)} premissas)")


def main():
    f = ler_fontes()
    # ordem da aba premissas: operação (O), receita (R), custos (C), investimento (I) e macro (M)
    prem = sorted(premissas(f), key=lambda p: ("ORCIM".index(p["id"][0]), p["id"]))
    quadro = quadro_pessoal(f)
    det = pessoal_detalhe(quadro)
    folha = sum(q * det[cargo]["remuneracao"] for cargo, _, q, _, _ in quadro)
    q_exp = quadro_pessoal(f, "expansao")
    d_exp = pessoal_detalhe(q_exp, "expansao")
    f["exp"] = dict(O01=MESAS + MC_EXPANSAO, R02=f["r15_exp"], O06=3, C15=refeicoes_mes("expansao"),
                    folha=sum(q * d_exp[c]["remuneracao"] for c, _, q, _, _ in q_exp))
    f["exp_quadro"] = {c: q for c, _, q, _, _ in q_exp}
    resultados = {c: calcula(f, valores(prem, c), folha) for c in CENARIOS}
    base = resultados["provavel"]
    tornado = []
    for p in prem:
        if p["pess"] == p["otim"]:
            continue
        vp = calcula(f, dict(valores(prem, "provavel"), **{p["id"]: p["pess"]}), folha)["vpl"]
        vo = calcula(f, dict(valores(prem, "provavel"), **{p["id"]: p["otim"]}), folha)["vpl"]
        if abs(vo - vp) < 1:  # premissa só de checagem (ex.: permanência)
            continue
        tornado.append(dict(id=p["id"], nome=p["nome"], vpl_pess=vp, vpl_otim=vo, amplitude=abs(vo - vp)))
    tornado.sort(key=lambda t: -t["amplitude"])
    por_id = {p["id"]: p for p in prem}
    rupt = [dict(por_id[t["id"]], ruptura=ruptura(f, prem, folha, t["id"])) for t in tornado[:5]]
    mc = monte_carlo(f, prem, folha, quadro)

    sem_residual = {c: calcula(f, dict(valores(prem, c), M03=0), folha) for c in CENARIOS}
    print(f"Etapa de equipe: {f['exp']['O01']} mesas fixas, {f['exp_quadro']}, folha R$ {f['exp']['folha']:,.2f}"
          f" (etapa 1: R$ {folha:,.2f}), {f['exp']['C15']:.1f} refeições, horas de pico do fim de semana {f['exp']['R02']:.2f}")
    wb = planilha(f, prem, quadro, resultados, tornado, rupt, mc, sem_residual)
    registro = pd.DataFrame(prem).rename(columns={"pess": "pessimista", "prov": "provavel", "otim": "otimista", "just": "justificativa"})
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SAIDA)
    gravar_premissas(registro[COLS_PREMISSAS], REGISTRO, "Registro de premissas do modelo financeiro (saída de gerar_modelo_financeiro.py; não editar)")
    conferir_sincronia()
    for i, cen in enumerate(CENARIOS, 1):
        # SEM_LIBREOFFICE=1 pula só a conferência cruzada das fórmulas (quando o soffice headless não
        # converte, como em sessão sem permissão de automação); as fórmulas recalculam ao abrir o arquivo
        if os.environ.get("SEM_LIBREOFFICE") == "1":
            print(f"Conferência {cen}: pulada (SEM_LIBREOFFICE=1)")
            continue
        vpl_lo = recalcula(SAIDA, i)
        dif = abs(vpl_lo - resultados[cen]["vpl"])
        print(f"Conferência {cen}: VPL Python {resultados[cen]['vpl']:,.2f} × LibreOffice {vpl_lo:,.2f} (diferença {dif:.4f})")
        if dif >= 1:
            raise SystemExit("VPL da planilha diverge do Python")
    figura_tornado(tornado, base["vpl"])
    figura_monte_carlo(mc)

    # números citados no capítulo
    print(f"\nTaxa de entrada: terça a quinta R$ {f['taxa_menor']:.2f} (mediana {f['taxa_menor_mediana']:.2f}), sexta a domingo R$ {f['taxa_maior']:.2f} (mediana {f['taxa_maior_mediana']:.2f}), n={f['taxa_n']};"
          f" média das medianas R$ {f['couvert_media']:.2f} (n={f['couvert_n']}, mediana {f['couvert_mediana']:.2f});"
          f" consumo (bebida + hambúrguer) médio: R$ {f['cesta_consumo_media']:.2f} (n={f['cesta_consumo_n']}, mediana {f['cesta_consumo_mediana']:.2f})")
    print("Mesas ocupadas por visita:", [round(x, 2) for x in f["mesas_ocupadas"]])
    print("Circulação no pico por visita:", [round(x, 2) for x in f["circulacao_visitas"]],
          f"| pelas NFC-e (BV, PA): {[round(x, 2) for x in f['circulacao_nfce']]} com {f['horas_pico_sj_semana']:.2f} h de pico por semana"
          f" | teto do salão {f['teto_circ']:.2f} pessoas/h")
    print(f"Gasto por pessoa (B2): {[round(x, 2) for x in f['gasto']]}; parcela da taxa {f['parcela_taxa']:.4f};"
          f" horas de pico equivalentes: {f['horas_pico']}")
    print(f"Folha de referência (remuneração com adicionais): R$ {folha:,.2f} ({sum(q for _, _, q, _, _ in quadro)} pessoas;"
          f" salários R$ {sum(q * s for _, _, q, s, _ in quadro):,.2f})")
    for cargo, *_ in quadro:
        for i, p in enumerate(det[cargo]["pessoas"], 1):
            print(f"  {cargo} {i}: " + " | ".join(f"{k} {x:,.2f}" for k, x in p.items()))
    print(f"Juro real: {f['juro_real']:.2f}%; PAS mercadorias: {f['pas_mercadorias_pct']:.1f}%; taxa B1 mediana {f['taxa_b1_mediana']} (n={f['taxa_b1_n']})")
    for cen in CENARIOS:
        r = resultados[cen]
        print(f"\n[{cen}] invest {r['investimento']:,.0f} | receita madura {r['receita_madura']:,.0f}/mês | pessoas {r['pessoas_madura']:,.0f}/mês"
              f" | fixos {r['fixos']:,.0f} | MC {r['mc_pct']:.1%} | equilíbrio {r['receita_equilibrio']:,.0f} | EBITDA5 {r['ebitda5']:,.0f}"
              f" | VPL {r['vpl']:,.0f} (sem valor residual {sem_residual[cen]['vpl']:,.0f}; residual {r['residual']:,.0f})"
              f" | TIR {r['tir']:.1%} | payback {r['payback']:.2f}")
        print("   inv:", {k: round(x) for k, x in r["inv"].items()})
        print("   anos:", r["ano"].round(0).to_dict("index"))
        # decomposição entre remuneração do capital (VPL) e do trabalho (pró-labore a valor presente,
        # na mesma perpetuidade do valor residual): o ganho total do sócio é a soma dos dois
        vp_prolabore = valores(prem, cen)["C08"] * 12 / valores(prem, cen)["M01"]
        print(f"   pró-labore {valores(prem, cen)['C08']:,.0f}/mês | VP {vp_prolabore:,.0f}"
              f" | ganho total do sócio {r['vpl'] + vp_prolabore:,.0f}")
    print("\nTornado:")
    for t in tornado:
        print(f"  {t['id']} {t['nome']}: pess {t['vpl_pess']:,.0f} | otim {t['vpl_otim']:,.0f} | amplitude {t['amplitude']:,.0f}")
    print("\nRuptura:")
    for rp in rupt:
        print(f"  {rp['id']} {rp['nome']}: provável {rp['prov']} → ruptura {rp['ruptura']}")
    print(f"\nMonte Carlo ({N_SIMULACOES}): etapa {mc['expansao']:.1%} | G5 {mc['g5']:.1%} | G6 {mc['fechamento']:.1%} | P10 {mc['p10']:,.0f} | P90 {mc['p90']:,.0f} | erro {mc['erro_prob']:.2%}")
    print(f"Monte Carlo: P(VPL>0) {mc['prob_positivo']:.1%} | média {mc['media']:,.0f} | P5 {mc['p05']:,.0f}"
          f" | P25 {mc['p25']:,.0f} | mediana {mc['mediana']:,.0f} | P75 {mc['p75']:,.0f} | P95 {mc['p95']:,.0f}"
          f" | payback em 5 anos {mc['payback_5anos']:.1%} | payback mediano {mc['payback_mediana']:.2f}")
    print("Percentis (P10 | mediana | P90):")
    for k, q in mc["percentis"].items():
        print(f"  {k}: " + " | ".join(f"{x:,.4f}" for x in q.values()))
    for cen in CENARIOS:
        g = calcula_mc(f, valores(prem, cen), folha, quadro)
        print(f"[{cen}] com os gatilhos G5 e G6: VPL {g['vpl']:,.0f} | G5 {g['g5']} | G6 {g['fechou']}"
              f" | TIR sem valor residual {tir(sem_residual[cen]['fc']):.1%}")
    print(f"\nOK: {SAIDA.relative_to(ROOT)}, {REGISTRO.relative_to(ROOT)}, {FIGURA.relative_to(ROOT)} e {FIGURA_MC.relative_to(ROOT)}")


if __name__ == "__main__":
    if "--conferir" in sys.argv:
        conferir_sincronia()
    else:
        main()
