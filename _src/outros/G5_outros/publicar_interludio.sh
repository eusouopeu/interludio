#!/usr/bin/env bash
# Atualiza o repositório público "interludio" a partir deste projeto.
#
# Copia só arquivos versionados aqui (respeita o .gitignore):
#   dados-agregados/ -> dados-agregados/
#   _src/            -> _src/
#   textos/{figuras,graficos,planilhas,quadros}/ -> texto/...
#   textos/TCC_luderia_v<N>.pdf de maior N -> texto/
#   slides-video-apresentacao/: só deck-apresentacao.pdf, deck-canva.pptx e
#   notas-do-apresentador.pdf (exportações, fora do git) -> apresentacao/
# O que sumiu daqui some de lá. README.md e .gitignore do interludio ficam.
#
# Uso: publicar_interludio.sh [--sem-push]
#   --sem-push  atualiza a pasta e mostra o resumo, sem commit nem push
set -euo pipefail

ORIGEM="$(cd "$(dirname "$0")/../../.." && pwd)"
DESTINO="${INTERLUDIO_DIR:-$(dirname "$ORIGEM")/interludio}"
PUSH=1
[[ "${1:-}" == "--sem-push" ]] && PUSH=0

[[ -d "$DESTINO/.git" ]] || { echo "Repositório interludio não encontrado em $DESTINO" >&2; exit 1; }

PDF="$(cd "$ORIGEM/textos" && ls TCC_luderia_v*.pdf 2>/dev/null | sort -t v -k2 -n | tail -1)"
[[ -n "$PDF" ]] || { echo "Nenhum textos/TCC_luderia_v*.pdf encontrado" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

copiar() {  # copiar <pasta de origem> <pasta no destino>
  mkdir -p "$TMP/$2"
  (cd "$ORIGEM/$1" && git ls-files -z . | rsync -a --from0 --files-from=- ./ "$TMP/$2/")
}

copiar dados-agregados dados-agregados
copiar _src _src
for p in figuras graficos planilhas quadros; do copiar "textos/$p" "texto/$p"; done
cp "$ORIGEM/textos/$PDF" "$TMP/texto/"
mkdir -p "$TMP/apresentacao"
for f in deck-apresentacao.pdf deck-canva.pptx notas-do-apresentador.pdf; do
  [[ -f "$ORIGEM/slides-video-apresentacao/$f" ]] && cp "$ORIGEM/slides-video-apresentacao/$f" "$TMP/apresentacao/"
done

for p in dados-agregados _src texto apresentacao; do
  rsync -a --delete "$TMP/$p/" "$DESTINO/$p/"
done

cd "$DESTINO"
git add -A
if git diff --cached --quiet; then
  echo "interludio já está em dia (PDF: $PDF)."
  exit 0
fi
git diff --cached --stat | tail -1

if (( PUSH )); then
  git commit -qm "Atualiza a partir do TCC (texto: $PDF)"
  git push -q
  echo "Publicado: $(git remote get-url origin) ($PDF)"
else
  git reset -q
  echo "Pasta atualizada sem commit (--sem-push)."
fi
