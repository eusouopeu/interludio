"""Copia para public/downloads/ os arquivos que o site oferece para baixar e grava o índice em
src/conteudo/downloads.json (lido pelo bloco "downloads" da aba Introdução).

- Texto do TMin: o textos/TCC_luderia_v<n>.docx de maior n (só a versão mais atual).
- Apresentação: slides-video-apresentacao/slides-vfinal.pptx (o .pptx mais atual, versionado; na falta dele,
  o deck-canva.pptx exportado do Canva).
- Planilhas de dados agregados: textos/planilhas/B<n>_dados_agregados*.xlsx.

Roda sozinho antes do `pnpm dev` e do `pnpm build` (predev e prebuild no package.json). Arquivo que não existe
nesta máquina entra no índice como indisponível, e o botão aparece desativado. public/downloads/ fica fora do git:
os originais já estão versionados (ou são exportações).
"""
import json
import re
import shutil
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
# Projeto do TCC (tcc-luderia), pasta irmã do interludio.
ROOT = Path(__file__).resolve().parents[3] / "tcc-luderia"
DESTINO = APP / "public" / "downloads"
INDICE = APP / "src" / "conteudo" / "downloads.json"

PLANILHAS = {
    "B1_dados_agregados.xlsx": ("B1 · Concorrentes", "Estabelecimentos, cardápios, acervos e redes sociais"),
    "B1_dados_agregados_resumido.xlsx": ("B1 · Concorrentes (resumida)", "As abas principais do B1"),
    "B2_dados_agregados.xlsx": ("B2 · Avaliações", "Análise de conteúdo das avaliações do Google Maps"),
    "B3_dados_agregados.xlsx": ("B3 · Contagem", "Ocupação, giro e NFC-e na São Jogue"),
    "B4_dados_agregados.xlsx": ("B4 · Bases públicas", "IBGE, Novo CAGED, FipeZap, Simples Nacional e BCB"),
}


def versao(p: Path) -> int:
    m = re.search(r"_v(\d+)\.docx$", p.name)
    return int(m.group(1)) if m else -1


def pptx() -> Path | None:
    pasta = ROOT / "slides-video-apresentacao"
    return next((pasta / n for n in ("slides-vfinal.pptx", "deck-canva.pptx") if (pasta / n).is_file()), None)


def item(origem: Path | None, rotulo: str, detalhe: str, formato: str) -> dict:
    if origem is None or not origem.is_file():
        return {"rotulo": rotulo, "detalhe": detalhe, "formato": formato, "arquivo": None, "tamanho": None}
    shutil.copy2(origem, DESTINO / origem.name)
    return {
        "rotulo": rotulo,
        "detalhe": detalhe,
        "formato": formato,
        "arquivo": f"downloads/{origem.name}",
        "tamanho": origem.stat().st_size,
    }


def main() -> None:
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)

    docx = max((ROOT / "textos").glob("TCC_luderia_v*.docx"), key=versao, default=None)
    n = versao(docx) if docx else None
    trabalho = [
        item(docx, "Texto do TCC", f"Versão mais atual (v{n})" if n else "Versão mais atual", "DOCX"),
        item(pptx(), "Slides da apresentação", "Deck da defesa", "PPTX"),
    ]
    planilhas = [item(ROOT / "textos" / "planilhas" / nome, r, d, "XLSX") for nome, (r, d) in PLANILHAS.items()]

    INDICE.write_text(
        json.dumps({"trabalho": trabalho, "planilhas": planilhas}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    faltam = [i["rotulo"] for i in trabalho + planilhas if not i["arquivo"]]
    print(f"downloads: {len(trabalho + planilhas) - len(faltam)} arquivos copiados para public/downloads/")
    if faltam:
        print("indisponíveis nesta máquina:", ", ".join(faltam))


if __name__ == "__main__":
    main()
