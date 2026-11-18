"""
Bloco B2 - amostra da rodada 3 da recodificação cega (coleta de 16/11/2026).

Sorteia 100 comentários entre os 678 sem código herdado
(2026-11-16_comentarios_a_codificar.csv, saída de B2b_comentarios_reaproveitados.py),
antes de qualquer codificação, para que o sorteio não dependa do código.

Estratos (semente fixa 20261116):
  1. casas novas (entraram na população em 12/11): 1 comentário de cada uma das 9;
  2. notas 1 a 3: até 30 comentários (as críticas são raras e definem a polaridade
     negativa, que é onde o kappa mais oscila);
  3. notas 4 e 5: o restante, até completar 100.
Cada comentário cai em um só estrato, na ordem acima.

Saídas:
  dados-brutos/B2_avaliacoes/analise_conteudo/2026-11-16_amostra_recodificacao.csv  (tem texto; fora do git)
  dados-agregados/B2_avaliacoes/analise_conteudo/coleta_2026-11-16_reaproveitada/B2_amostra_recodificacao_ids.csv
      id_avaliacao, estrato, ordem (sem texto)

Uso:
    python3 "_src/pyScripts/B2_Avaliacoes/2_build/B2b_amostra_recodificacao.py"
"""
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*"))]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
BRUTOS = ROOT / "dados-brutos" / "B2_avaliacoes" / "analise_conteudo"
FALTA = BRUTOS / "2026-11-16_comentarios_a_codificar.csv"
SAIDA = BRUTOS / "2026-11-16_amostra_recodificacao.csv"
PASTA = ROOT / "dados-agregados" / "B2_avaliacoes" / "analise_conteudo" / "coleta_2026-11-16_reaproveitada"
SEMENTE, N, N_CRITICAS = 20261116, 100, 30

# Casas que entraram na população em 12/11/2026 (sem nenhum comentário na grade 2).
CASAS_NOVAS = [
    "60 Minutos Escape, Hamburgueria e Boardgames", "CHQ Jogos", "Cheio de Fome - Vila da Penha",
    "Covil Game Bar SBC", "Espaço 162 - Meu Karaokê Box", "Metropoly Bar",
    "Muito Geek | TCG • Board Games • Fliperama", "Nergeek", "Paladino Hobbies",
]


def main():
    a = pd.read_csv(FALTA, sep=";", dtype=str, keep_default_na=False, encoding="utf-8-sig")
    faltam = set(CASAS_NOVAS) - set(a["nome_estabelecimento"])
    assert not faltam, f"casas novas sem comentário a codificar: {faltam}"
    nota = a["nota_avaliacao"].astype(int)

    e1 = (a[a["nome_estabelecimento"].isin(CASAS_NOVAS)]
          .groupby("nome_estabelecimento", group_keys=False).sample(1, random_state=SEMENTE))
    resto = a.drop(e1.index)
    crit = resto[nota.loc[resto.index] <= 3]
    e2 = crit.sample(min(N_CRITICAS, len(crit)), random_state=SEMENTE)
    resto = resto.drop(e2.index)
    e3 = resto[nota.loc[resto.index] >= 4].sample(N - len(e1) - len(e2), random_state=SEMENTE)

    amostra = pd.concat([e1.assign(estrato="casa nova"), e2.assign(estrato="nota 1 a 3"),
                         e3.assign(estrato="nota 4 e 5")])
    # Ordem de leitura embaralhada, para o estrato não ficar visível na sequência.
    amostra = amostra.sample(frac=1, random_state=SEMENTE).reset_index(drop=True)
    amostra["ordem"] = range(1, len(amostra) + 1)
    assert len(amostra) == N and amostra["id_avaliacao"].is_unique
    assert amostra["estrato"].value_counts().sum() == N

    amostra.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")
    PASTA.mkdir(parents=True, exist_ok=True)
    amostra[["id_avaliacao", "estrato", "ordem"]].to_csv(
        PASTA / "B2_amostra_recodificacao_ids.csv", sep=";", index=False, encoding="utf-8-sig")
    print(amostra["estrato"].value_counts().to_string())
    print(f"{len(amostra)} comentários; {amostra['nome_estabelecimento'].nunique()} casas; "
          f"notas {amostra['nota_avaliacao'].value_counts().sort_index().to_dict()}")


if __name__ == "__main__":
    main()
