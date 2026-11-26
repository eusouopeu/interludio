"""
Bloco B2 - Figura 7 do cap. 6: distribuição do gasto por pessoa declarado no
Google Maps, no mesmo recorte da premissa de gasto (R04): as casas com taxa de
entrada conhecida e gasto declarado (coluna no_recorte de
B2_gasto_cesta_por_casa.csv), na coleta de 16/11/2026.

Substitui, a partir de 18/11/2026, o gráfico da base de comentários de outubro
(602 declarações, gerar_planilha_comentarios.py), que tinha recorte diferente
do usado no texto e no modelo (D115).

Entradas: dados-agregados/B2_avaliacoes/B2_avaliacoes_periodo.csv;
          dados-agregados/B2_avaliacoes/gasto_por_pessoa/B2_gasto_cesta_por_casa.csv
Saída: textos-tcc/graficos/6-2_gasto_declarado_por_pessoa.png

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/3_analise/B2a_figura_gasto_declarado.py"
"""
import re
import sys
from pathlib import Path

_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import pandas as pd  # noqa: E402
import planilha_estilo as est  # noqa: E402

ROOT = _AQUI.parents[4]
B2 = ROOT / "dados-agregados" / "B2_avaliacoes"
FAIXAS = [(1, 20), (20, 40), (40, 60), (60, 80), (80, 100), (100, 120), (120, 140), (140, 160), (160, 180),
          (180, 200), (200, None)]
ROT = [f"R$ {a} a {b}" if b else "R$ 200 ou mais" for a, b in FAIXAS]


def rotulo(v: str) -> str:
    a = int(re.findall(r"\d+", v)[0])
    return ROT[-1] if v.startswith("+") else next(r for (x, _), r in zip(FAIXAS, ROT) if x == a)


def main():
    av = pd.read_csv(B2 / "B2_avaliacoes_periodo.csv", sep=";", dtype=str)
    casas = pd.read_csv(B2 / "gasto_por_pessoa" / "B2_gasto_cesta_por_casa.csv", sep=";")
    ids = set(casas.loc[casas.no_recorte == "sim", "place_id"])
    d = av[av.preco_por_pessoa.notna() & av.place_id.isin(ids)]
    n_recorte = int(casas.loc[casas.no_recorte == "sim", "avaliacoes"].sum())
    assert len(d) == n_recorte, (len(d), n_recorte)
    vc = d.preco_por_pessoa.map(rotulo).value_counts().reindex(ROT).fillna(0).astype(int)
    assert vc.sum() == len(d)
    acum = vc.cumsum() / vc.sum()
    est.GRAF = ROOT / "textos-tcc" / "graficos"
    caminho = est.barras_h("6-2_gasto_declarado_por_pessoa", ROT, {"% das declarações": (vc / vc.sum()).tolist()},
                           lambda v: est.br(v * 100, 1, suf="%"), eixo_pct=True)
    print(f"{len(d)} declarações em {d.place_id.nunique()} casas; faixa mediana {acum[acum >= .5].index[0]}")
    print(dict(vc))
    sem = d[~d.nome_estabelecimento.str.startswith("Bodogami")]
    vs = sem.preco_por_pessoa.map(rotulo).value_counts().reindex(ROT).fillna(0)
    a2 = vs.cumsum() / vs.sum()
    print(f"sem a Bodogami: {len(sem)} declarações; faixa mediana {a2[a2 >= .5].index[0]}")
    print(f"gravado: {caminho.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
