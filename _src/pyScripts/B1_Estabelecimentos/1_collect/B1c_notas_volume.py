"""Recoleta da nota média e do volume de avaliações do Google das casas da população do B1.

Pedido do autor (16/11/2026): as notas e os volumes vinham de três datas (47 casas em 01/09, 4 em
16/09 e 9 em 12/11, além das luderias novas do Acervo de Jogos em 12/10). Esta coleta põe todas as
casas no mesmo dia.

Chamada: Place Details (New) só com id, displayName, rating, userRatingCount e businessStatus,
SKU "Place Details Enterprise" (sem `reviews`, que promove ao Atmosphere).

Entradas (as mesmas que B1b_resumo.py junta para formar a população):
  dados-agregados/B1_estabelecimentos/3_triagem/B1_aprovadas_metro_av100.xlsx
  dados-agregados/B1_acervo_jogos/B1_acervodejogos_luderias_novas.csv
Saídas:
  dados-brutos/B1_estabelecimentos/B1_notas_volume_<data>.jsonl   (resposta da API, uma linha por casa)
  dados-agregados/B1_estabelecimentos/B1_notas_volume.csv          (antes × depois, por casa)
  as duas entradas, com avaliacao_media, volume_avaliacoes e data_coleta trocadas
  (as versões anteriores vão antes para o _arquivo/ de cada pasta, com data e hora no nome).

Uso:
    python3 "_src/pyScripts/B1_Estabelecimentos/1_collect/B1c_notas_volume.py"
"""
# Caminhos: _src/extras/ (log comum) e outros/ do objeto (auxiliares); log em ../logs/
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*")), str(_AQUI.parents[1] / "5_outros")]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import json
import shutil
from datetime import datetime

import openpyxl
import pandas as pd

from places_client import PlacesClient

ROOT = _AQUI.parents[4]
APROVADAS = ROOT / "dados-agregados" / "B1_estabelecimentos" / "3_triagem" / "B1_aprovadas_metro_av100.xlsx"
NOVAS = ROOT / "dados-agregados" / "B1_acervo_jogos" / "B1_acervodejogos_luderias_novas.csv"
BRUTOS = ROOT / "dados-brutos" / "B1_estabelecimentos"
SAIDA = ROOT / "dados-agregados" / "B1_estabelecimentos" / "B1_notas_volume.csv"
MASCARA = "id,displayName,rating,userRatingCount,businessStatus"
AGORA = datetime.now()
HOJE = AGORA.date().isoformat()
CARIMBO = AGORA.strftime("%Y-%m-%d_%H%M")


def arquivar(p: Path) -> None:
    destino = p.parent / "_arquivo" / f"{p.stem}_{CARIMBO}{p.suffix}"
    destino.parent.mkdir(exist_ok=True)
    shutil.copy2(p, destino)
    print(f"arquivado: {destino.relative_to(ROOT)}")


def main():
    a = pd.read_excel(APROVADAS)
    n = pd.read_csv(NOVAS)
    casas = pd.concat([a[["place_id", "nome", "capital_endereco", "avaliacao_media", "volume_avaliacoes", "data_coleta"]]
                       .assign(fonte="aprovadas"),
                       n[["place_id", "nome", "capital_endereco", "avaliacao_media", "volume_avaliacoes", "data_coleta"]]
                       .assign(fonte="novas")]).drop_duplicates("place_id")
    bruto = BRUTOS / f"B1_notas_volume_{HOJE}.jsonl"
    # a coleta do dia já feita é reaproveitada (não paga a chamada duas vezes)
    resp = {}
    if bruto.exists():
        resp = {d["id"]: d for d in map(json.loads, bruto.read_text(encoding="utf-8").splitlines())}
    falta = [p for p in casas["place_id"] if p not in resp]
    cli = PlacesClient() if falta else None
    with open(bruto, "a", encoding="utf-8") as f:
        for pid in falta:
            d = cli._get(f"places/{pid}", MASCARA)
            d["data_coleta"] = HOJE
            resp[pid] = d
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"{len(resp)} casas consultadas -> {bruto.relative_to(ROOT)}")

    t = casas.rename(columns={"avaliacao_media": "nota_antes", "volume_avaliacoes": "volume_antes",
                              "data_coleta": "data_antes"})
    t["data_antes"] = pd.to_datetime(t["data_antes"].astype(str), format="mixed").dt.date.astype(str)
    t["nota_depois"] = t["place_id"].map(lambda p: resp[p].get("rating"))
    t["volume_depois"] = t["place_id"].map(lambda p: resp[p].get("userRatingCount", 0))
    t["status_google"] = t["place_id"].map(lambda p: resp[p].get("businessStatus", ""))
    t["data_depois"] = HOJE
    t["volume_variacao"] = t["volume_depois"] - t["volume_antes"]
    t.to_csv(SAIDA, sep=";", index=False, encoding="utf-8-sig")

    # aprovadas: troca só as três colunas, célula a célula, para manter a formatação da planilha
    arquivar(APROVADAS)
    wb = openpyxl.load_workbook(APROVADAS)
    ws = wb.active
    cab = {c.value: c.column for c in ws[1]}
    for r in range(2, ws.max_row + 1):
        pid = ws.cell(r, cab["place_id"]).value
        if pid in resp:
            ws.cell(r, cab["avaliacao_media"]).value = resp[pid].get("rating")
            ws.cell(r, cab["volume_avaliacoes"]).value = resp[pid].get("userRatingCount", 0)
            ws.cell(r, cab["data_coleta"]).value = HOJE
    wb.save(APROVADAS)

    arquivar(NOVAS)
    n["avaliacao_media"] = n["place_id"].map(lambda p: resp[p].get("rating"))
    n["volume_avaliacoes"] = n["place_id"].map(lambda p: resp[p].get("userRatingCount", 0))
    n["data_coleta"] = HOJE
    n.to_csv(NOVAS, index=False)

    abaixo = t[t["volume_depois"] <= 100]
    print(f"volume: soma antes {t.volume_antes.sum()}, depois {t.volume_depois.sum()}; "
          f"nota média antes {t.nota_antes.mean():.3f}, depois {t.nota_depois.mean():.3f}")
    print(f"status: {t.status_google.value_counts().to_dict()}")
    print(f"com 100 avaliações ou menos: {abaixo[['nome', 'volume_antes', 'volume_depois']].to_dict('records')}")


if __name__ == "__main__":
    main()
