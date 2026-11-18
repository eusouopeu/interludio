"""Recoleta dos cardápios on-line com coleta anterior a 06/11/2026 (pedido do autor, 16/11/2026).

Objetivo: deixar todos os preços do B1 na mesma semana, sem comparar o hoje de uma casa
com o mês passado de outra. Para cada fonte on-line (PDF, imagem, página Wix, página em texto),
baixa a versão de hoje e compara o conteúdo com o original já transcrito:
  - igual byte a byte (ou mesmas imagens do cardápio): a transcrição vale; só a data de coleta muda;
  - diferente: o arquivo novo fica para nova extração (OCR ou transcrição).
Os cardápios digitais (Saipos, VUCA Food, Goomer, Menudino, Cloudfy) são relidos por
B1c_cardapios_digitais.py e comparados item a item na reconstrução.

Saída:
  dados-brutos/B1_cardapios/ca_<cidade>/ca_<estabelecimento>/recoleta_<data>/  (arquivos baixados)
  dados-agregados/B1_cardapios/B1_cardapios_recoleta.csv
      (arquivo_transcricao;url;tipo;situacao;arquivos;sha_iguais;baixado_em)

Uso:
    python3 "_src/pyScripts/B1_Cardapios/1_collect/B1c_cardapios_recoleta.py"
"""
# Caminhos: _src/extras/ (log comum) e outros/ do objeto (auxiliares); log em ../logs/
import sys
from pathlib import Path
_AQUI = Path(__file__).resolve()
sys.path[:0] = [*map(str, (_AQUI.parents[3] / "outros").glob("G[0-9]_*")), str(_AQUI.parents[1] / "5_outros")]
from log_execucao import registrar_execucao  # noqa: E402
if __name__ == "__main__":
    registrar_execucao(__file__)

import csv
import hashlib
import re
import ssl
import urllib.request
from datetime import date, datetime

import certifi

ROOT = _AQUI.parents[4]
BRUTOS = ROOT / "dados-brutos" / "B1_cardapios"
SAIDA = ROOT / "dados-agregados" / "B1_cardapios" / "B1_cardapios_recoleta.csv"
CTX = ssl.create_default_context(cafile=certifi.where())
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
HOJE = date.today().isoformat()
MAGIC = {b"%PDF": ".pdf", b"\xff\xd8\xff": ".jpg", b"\x89PNG": ".png", b"RIFF": ".webp", b"<": ".html"}

# arquivo de transcrição -> (pasta ca_<cidade>/ca_<estab>, tipo, url)
# tipo: "arquivo" = download direto; "wix" = imagens static.wixstatic.com da página; "pagina" = HTML
FONTES = {
    "ludus": ("ca_sao_paulo/ca_ludus_luderia", "arquivo",
              "https://drive.google.com/uc?export=download&id=1s7GHW2xdsauEU55oIFPCojKY-nSrrKTB"),
    "bodogami": ("ca_sao_paulo/ca_bodogami", "arquivo",
                 "https://www.bodogami.com.br/wp-content/uploads/2025/03/cardapio_bodogami_19mar2025.pdf"),
    "arcadea": ("ca_porto_alegre/ca_arcadea_gaming_pub", "arquivo",
                "https://arcadeapub.com.br/wp-content/uploads/2025/03/CARDAPIO-ARCADEA-3.pdf"),
    "fortaludica": ("ca_brasilia/ca_fortaludica", "arquivo",
                    "https://drive.google.com/uc?export=download&id=1cl7YIKdJhuuhNCUKAO0-96czajLGInqJ"),
    "tabuclub": ("ca_rio_de_janeiro/ca_tabuclub", "arquivo",
                 "https://drive.google.com/uc?export=download&id=1-KDTgvYRZKe4R9KCWVQHRD5xiWqjSgPW"),
    "luderia_carioca": ("ca_rio_de_janeiro/ca_luderia_carioca", "arquivo", "https://i.postimg.cc/T3qJVwfn/cardapio.jpg"),
    "alcapao": ("ca_curitiba/ca_alcapao_jogos", "wix", "https://www.alcapaojogos.com.br/card%C3%A1pio"),
    "boardz": ("ca_curitiba/ca_boardz_game_pub", "wix", "https://www.boardzgamepub.com.br/card%C3%A1pio"),
    "boardz_couvert": ("ca_curitiba/ca_boardz_game_pub", "pagina", "https://www.boardzgamepub.com.br/"),
    "castelos": ("ca_sao_paulo/ca_castelos_bar", "wix", "https://www.castelosbar.com.br/cardapio"),
    "placegames": ("ca_sao_paulo/ca_place_games", "wix", "https://www.placegames.com.br/cardapio"),
    "arenabg": ("ca_sao_paulo/ca_arena_bg", "pagina", "https://www.arenabg.com.br/cardapio"),
    "asgard": ("ca_brasilia/ca_asgard", "pagina", "https://asgard.app.br/cardapio"),
    "gameofboards": ("ca_rio_de_janeiro/ca_game_of_boards", "pagina", "https://www.gameofboards.com.br/"),
    "garagemdonerd": ("ca_belo_horizonte/ca_garagem_do_nerd", "pagina", "https://garagemdonerd.com.br/cardapio"),
    "joyjoy": ("ca_curitiba/ca_joyjoy", "pagina",
               "https://curitibandoemfamilia.com.br/experiencias/ctba-indoor/joyjoy-cafe/"),
}


def baixar(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
        return r.read()


def extensao(dados):
    return next((e for m, e in MAGIC.items() if dados.lstrip()[:4].startswith(m)), ".bin")


def imagens_wix(html):
    achadas = re.findall(r"https://static\.wixstatic\.com/media/[^\s\"'<>\\)]+?\.(?:png|jpe?g|avif|webp)", html)
    return sorted({re.sub(r"/v1/.*", "", x).replace("%7E", "~") for x in achadas})


def shas_antigos(pasta):
    """sha256 dos originais já guardados (fora das pastas recoleta_)."""
    if not pasta.exists():
        return set()
    return {hashlib.sha256(p.read_bytes()).hexdigest() for p in pasta.rglob("*")
            if p.is_file() and "recoleta_" not in str(p.relative_to(pasta))}


def main():
    linhas = []
    for arq, (rel, tipo, url) in FONTES.items():
        pasta = BRUTOS / rel
        antigos = shas_antigos(pasta)
        destino = pasta / f"recoleta_{HOJE}"
        try:
            dados = baixar(url)
            alvos = [(f"{arq}{extensao(dados)}", dados)]
            if tipo == "wix":
                imgs = imagens_wix(dados.decode("utf8", "ignore"))
                alvos = []
                for i, u in enumerate(imgs, 1):
                    d = baixar(u)
                    if len(d) >= 20_000:  # ícones e logos ficam de fora
                        alvos.append((f"{arq}_{i:02d}{extensao(d)}", d))
        except Exception as e:  # noqa: BLE001
            linhas.append([arq, url, tipo, f"falha: {e}", 0, 0, datetime.now().isoformat(timespec="seconds")])
            print(f"FALHA {arq}: {e}")
            continue
        destino.mkdir(parents=True, exist_ok=True)
        iguais = 0
        for nome, d in alvos:
            (destino / nome).write_bytes(d)
            iguais += hashlib.sha256(d).hexdigest() in antigos
        situacao = "igual ao original" if alvos and iguais == len(alvos) else "mudou ou sem original para comparar"
        linhas.append([arq, url, tipo, situacao, len(alvos), iguais, datetime.now().isoformat(timespec="seconds")])
        print(f"{arq}: {len(alvos)} arquivo(s), {iguais} iguais -> {situacao}")
    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["arquivo_transcricao", "url", "tipo", "situacao", "arquivos", "sha_iguais", "baixado_em"])
        w.writerows(linhas)


if __name__ == "__main__":
    main()
