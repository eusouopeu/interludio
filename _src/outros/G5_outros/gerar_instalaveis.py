"""
Gera a versão instalável de cada webscript de _src/webScripts/<bloco>/, para qualquer pessoa
repetir as coletas do TCC sem ter o repositório no disco.

O script de trabalho (<script>.user.js) lê a lista do menu de um arquivo ao lado
(lista_<script>.js, @require relativo), e o carregador local (gerar_carregadores.py) aponta
para o caminho desta máquina. O instalável junta os dois num arquivo só:
cabeçalho + lista do menu + script, com @downloadURL e @updateURL do repositório público.
Instala-se com um clique no Tampermonkey, pelo endereço "raw" do GitHub, e se atualiza sozinho.

Saída: _src/webScripts/_instalaveis/<script>.user.js (no git; vai para o repositório público
com publicar_interludio.sh). Rodar depois de mudar um script, a lista dele ou o kit.

Uso:
    python3 _src/outros/G5_outros/gerar_instalaveis.py             # gera
    python3 _src/outros/G5_outros/gerar_instalaveis.py --conferir  # sai com erro se algum estiver velho
"""
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[2] / "webScripts"  # _src/webScripts/
SAIDA = PASTA / "_instalaveis"
URL_BASE = "https://raw.githubusercontent.com/eusouopeu/interludio/main/_src/webScripts/_instalaveis"
RE_CABECALHO = re.compile(r"// ==UserScript==\n(.*?)// ==/UserScript==\n?", re.S)


def instalavel(script):
    texto = script.read_text(encoding="utf-8")
    m = RE_CABECALHO.search(texto)
    if not m:
        raise ValueError(f"{script.name}: sem bloco ==UserScript==")
    saida, listas = ["// ==UserScript=="], []
    for l in m.group(1).splitlines():
        if not l.strip() or l.startswith(("// @updateURL", "// @downloadURL")):
            continue
        if l.startswith("// @require"):
            alvo = l.split(None, 2)[2].strip()
            if not re.match(r"[a-z]+:", alvo):  # lista do menu, ao lado do script: entra no corpo
                arquivo = script.parent / alvo
                if not arquivo.exists():
                    raise FileNotFoundError(f"{script.name}: @require {alvo} não existe")
                listas.append(arquivo)
                continue
        saida.append(l)
    url = f"{URL_BASE}/{script.name}"
    saida += [f"// @downloadURL  {url}", f"// @updateURL    {url}", "// ==/UserScript=="]
    saida.append(f"// Gerado por gerar_instalaveis.py a partir de {script.parent.name}/{script.name}; não editar aqui.")
    for a in listas:
        saida += ["", f"// ---------- {a.name} ----------", a.read_text(encoding="utf-8").strip()]
    saida += ["", f"// ---------- {script.name} ----------", texto[m.end():].strip(), ""]
    return "\n".join(saida)


def main():
    conferir = "--conferir" in sys.argv
    SAIDA.mkdir(exist_ok=True)
    scripts = sorted(PASTA.glob("B[0-9]_*/*.user.js"))
    velhos = 0
    for script in scripts:
        destino = SAIDA / script.name
        novo = instalavel(script)
        if destino.exists() and destino.read_text(encoding="utf-8") == novo:
            continue
        velhos += 1
        if conferir:
            print(f"instalável desatualizado: {script.name}", file=sys.stderr)
        else:
            destino.write_text(novo, encoding="utf-8")
            print(f"instalável gerado: {script.name}")
    nomes = {s.name for s in scripts}
    for sobra in SAIDA.glob("*.user.js"):
        if sobra.name not in nomes:
            velhos += 1
            if conferir:
                print(f"instalável sem script: {sobra.name}", file=sys.stderr)
            else:
                sobra.unlink()
                print(f"instalável apagado: {sobra.name}")
    if not velhos:
        print("instaláveis em dia.")
    if conferir and velhos:
        sys.exit(1)


if __name__ == "__main__":
    main()
