#!/usr/bin/env python3
"""Figura 7 do TCC: planta compacta (área mínima), em cinco figuras separadas.

Lê o desenho-base exportado do Figma (textos-tcc/figuras/planta-baixa-basica-area-minima/,
8,00 x 13,69 m, 1 m = 100 unidades) e gera, em textos-tcc/figuras/:
  7-1_planta_salao_48_lugares.(svg|png)            planta na horizontal (a do texto)
  7-1_planta_salao_48_lugares_vertical.(svg|png)   a mesma planta girada 90°, com todos os
                                                   textos de pé (cada rótulo é contragirado)
  7-1_quadro_areas.png                             quadro de áreas
  7-1_posicao_faixa_busca.png                      posição do estudo na faixa de 100 a 150 m²
  7-1_legenda.png                                  legenda e notas
Complementos sobre o desenho-base: cadeiras que faltavam à mesa 3 (cópia das da mesa 4,
deslocada 2,90 m), estante do acervo, "6 lug." sob cada mesa, folgas cotadas e rota acessível
esquemática. Título e rodapé do desenho-base saem (o título fica na legenda do documento).
Os números do quadro saem das medidas do desenho (ver MEDIDAS).
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "textos-tcc/figuras/planta-baixa-basica-area-minima/Luderia — planta baixa minimalista · figura para TCC.svg"
FIG = ROOT / "textos-tcc/figuras"
NOME = "7-1_planta_salao_48_lugares"

# Medidas lidas do desenho (unidades = cm; paredes de 15 cm)
LARG_EXT, ALT_EXT = 13.69, 8.00
PAREDE = 0.15
AMBIENTES = [  # rótulos do desenho
    ("Salão de jogos (8 mesas, 48 lugares, estante e circulação)", 61.6),
    ("Cozinha", 14.0),
    ("Balcão e caixa", 4.8),
    ("Sanitário acessível", 4.2),
    ("Despensa", 4.2),
    ("Sanitários feminino, masculino e da equipe (3 × 2,3)", 6.9),
]
SOMA_AMB = round(sum(v for _, v in AMBIENTES), 1)                    # 95,7
BRUTO = LARG_EXT * ALT_EXT                                           # 109,5
INTERNA = (LARG_EXT - 2 * PAREDE) * (ALT_EXT - 2 * PAREDE)           # 103,1
LUGARES = 48

FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"
INK, MUTED, GREEN, PURPLE = "#2E2E2E", "#5b5b5b", "#15803D", "#7e22ce"
LARG_CHAR = 0.56  # largura média de um caractere, em múltiplos do corpo da fonte


def br(x, casas=1):
    return f"{x:.{casas}f}".replace(".", ",")


def pct(x):
    return br(100 * x / round(BRUTO, 1)) + "%"


def txt(x, y, s, size=15, weight=400, fill=INK, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>')


MARCAS = ('<defs>'
          f'<marker id="seta" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M1 1L9 5L1 9z" fill="{INK}"/></marker>'
          f'<marker id="seta_verde" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
          f'<path d="M0 0L10 5L0 10z" fill="{GREEN}"/></marker>'
          '</defs>')


def svg(vb, corpo, escala=1.0):
    x, y, w, h = vb
    return (f'<svg width="{w * escala:.0f}" height="{h * escala:.0f}" viewBox="{x} {y} {w} {h}" fill="none" '
            f'xmlns="http://www.w3.org/2000/svg">\n<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white"/>\n'
            f'{MARCAS}\n{corpo}\n</svg>\n')


def png(svg_path, largura):
    subprocess.run(["rsvg-convert", "-w", str(largura), "-b", "white", "-o", str(svg_path.with_suffix(".png")),
                    str(svg_path)], check=True)


# ---------------------------------------------------------------- planta ----
def bbox(d):
    """Caixa envolvente aproximada de um path em comandos absolutos (M L H V C Z)."""
    assert not re.search(r"[a-z]", d), "path com comando relativo"
    xs, ys, cmd, nums = [], [], None, []
    for t in re.findall(r"[MLHVCZ]|-?\d+\.?\d*|-?\.\d+", d):
        if t.isalpha():
            cmd = t
            nums = []
            continue
        nums.append(float(t))
        if cmd == "H":
            xs.append(nums.pop())
        elif cmd == "V":
            ys.append(nums.pop())
        elif cmd in "ML" and len(nums) == 2:
            xs.append(nums[0]); ys.append(nums[1]); nums = []
        elif cmd == "C" and len(nums) == 2:
            xs.append(nums[0]); ys.append(nums[1]); nums = []
    return min(xs), min(ys), max(xs), max(ys)


class Plano:
    """Elementos da planta; em modo vertical cada texto é contragirado em torno do centro."""

    def __init__(self, vertical):
        self.v = vertical
        self.partes = []

    def glifo(self, linha, dx=0, dy=0, centro=None):
        """Path de glifos do desenho-base (fill #141414). Em modo vertical gira -90° em torno de
        `centro` (o do rótulo, ou o do par nome + área, para que o par continue empilhado)."""
        if not self.v:
            return linha
        if centro is None:
            x0, y0, x1, y1 = bbox(re.search(r' d="([^"]*)"', linha).group(1))
            centro = ((x0 + x1) / 2, (y0 + y1) / 2)
        cx, cy = centro
        return f'<g transform="translate({dx} {dy}) rotate(-90 {cx:.2f} {cy:.2f})">{linha}</g>'

    def texto(self, centro_h, s, size=14, weight=600, fill=INK, centro_v=None):
        """Texto centrado em centro_h (horizontal) ou centro_v (vertical, de pé)."""
        cx, cy = (centro_v or centro_h) if self.v else centro_h
        rot = f'transform="rotate(-90 {cx} {cy})"' if self.v else ""
        self.partes.append(txt(cx, cy + 0.35 * size, s, size, weight, fill, "middle", rot))

    def cota(self, eixo, pos, a, b, rotulo, centro_h, centro_v):
        if eixo == "v":
            self.partes.append(f'<path d="M{pos} {a}V{b}" stroke="{INK}" stroke-width="1" marker-start="url(#seta)" marker-end="url(#seta)"/>')
        else:
            self.partes.append(f'<path d="M{a} {pos}H{b}" stroke="{INK}" stroke-width="1" marker-start="url(#seta)" marker-end="url(#seta)"/>')
        self.texto(centro_h, rotulo, centro_v=centro_v)


# deslocamento (em y da planta; +y = esquerda na página girada) dos pares de rótulos na versão vertical
AJUSTE_V = {243: -12, 244: -12, 245: -22, 246: -22, 247: -22, 248: -22, 249: -22, 250: -22,
            253: -8, 254: -8, 257: 40, 258: 40}


def planta(vertical):
    linhas = BASE.read_text(encoding="utf-8").split("\n")
    # linhas (1-based): 1 = <svg>, 2 = fundo, 259/260 = título, 261 = rodapé, 262 = </svg>
    # 5, 221 e 222: contorno de construção (linha fina que cruzava a porta de entrada e o L) e suas máscaras brancas
    base = [(i, l) for i, l in enumerate(linhas, 1) if i not in (1, 2, 5, 221, 222, 259, 260, 261, 262) and l.strip()]
    P = Plano(vertical)
    # rótulos em pares (nome + área): giram juntos em torno do centro do par
    pares = {}
    if vertical:
        cen = {}
        for i, l in base:
            if 'fill="#141414"' in l and ' stroke' not in l:
                x0, y0, x1, y1 = bbox(re.search(r' d="([^"]*)"', l).group(1))
                cen[i] = ((x0 + x1) / 2, (y0 + y1) / 2)
        for a in (243, 245, 247, 249, 251, 253, 255, 257):
            c = ((cen[a][0] + cen[a + 1][0]) / 2, (cen[a][1] + cen[a + 1][1]) / 2)
            pares[a] = pares[a + 1] = c
    saida, janela = [], []
    for i, l in base:
        if 'M973 418V598H1063V418H973Z' in l:       # mesa 3: cadeiras do lado esquerdo que faltavam
            cad = "\n".join(linhas[159:165])        # linhas 160-165 (cadeiras da mesa 4), -2,90 m
            saida.append(f'<g id="cadeiras_mesa3_esq" transform="translate(-290 0)">\n{cad}\n</g>')
        if i in (3, 4):              # janela da cozinha: sai de fora da parede e entra nela (depois das paredes)
            janela.append(l)
            continue
        if i == 45:                  # "L" externo cozinha-despensa: paredes alinhadas (x 295,5-310,5 como a da despensa)
            l = f'<path d="M215.5 620.5H310.5V721H295.5V635.5H215.5Z" fill="#2E2E2E"/>'
        elif i in (87, 88):          # lavatório da cozinha: encostado na parede (face em x = 471,5), não sobre ela
            l = f'<g transform="translate(-16.5 0)">{l}</g>'
        elif i in (223, 224):        # batentes da porta de entrada: na altura da parede (y 110,5-125,5)
            l = l.replace("101.255", "110.5").replace("113.86", "125.5")
        if 'fill="#141414"' in l and ' stroke' not in l and i != 242:
            dx, dy = 0, 0
            if 217 <= i <= 220:      # rótulos da escala gráfica: afastar da barra
                dy = 12
            elif i in (229, 238):    # "Entrada" e "13,69 m": afastar da parede e da linha de cota
                dy = -25
            elif i in AJUSTE_V:      # pares nome + área: afastar de louças, cotas e portas (só na vertical)
                dy = AJUSTE_V[i]
            l = P.glifo(l, dx, dy, pares.get(i))
        saida.append(l)

    # janela da cozinha: dentro da espessura da parede esquerda (x 215,5-230,5), abrindo vão nela
    saida.append(f'<g id="janela_cozinha" transform="translate(12.5 0)">' + "".join(janela) + '</g>')

    # --- complementos -------------------------------------------------------
    # estante do acervo (faixa de 60 cm na parede direita): o texto já gira -90° na planta
    P.partes.append(txt(1522, 363 + 4, "ESTANTE DO ACERVO", 15, 700, anchor="middle",
                        extra='transform="rotate(-90 1522 363)" letter-spacing="1"'))
    for cx, cy in ((1011, 213), (1308, 213), (1018, 508), (1308, 508), (1000.5, 803), (1162.5, 803), (1324.5, 803), (1486, 803)):
        P.texto((cx, cy + 28), "6 lug.", 13, 600, MUTED, centro_v=(cx + 25, cy))
    # rota acessível esquemática: porta de entrada -> corredor -> sanitário acessível
    P.partes.append(f'<path d="M791 168V657.5H529V608" fill="none" stroke="{GREEN}" stroke-width="3.5" '
                    f'stroke-dasharray="11 7" stroke-linejoin="round" marker-end="url(#seta_verde)"/>')
    P.partes.append(f'<circle cx="791" cy="168" r="5.5" fill="{GREEN}"/>')
    # cotas das folgas (medidas no desenho): eixo, posição, extremos, rótulo, centro (horizontal), centro (vertical)
    P.cota("v", 1018, 302.5, 418, "1,15 m", (1050, 360), (1033, 360))        # mesa 1 a mesa 3
    P.cota("v", 1018, 598, 713.5, "1,15 m", (1050, 656), (1033, 656))        # mesa 3 aos booths
    P.cota("h", 216, 1103, 1223, "1,20 m", (1163, 203), (1163, 186))         # cadeira da mesa 1 a cadeira da mesa 2
    P.cota("h", 216, 1393, 1507, "1,14 m", (1450, 203), (1450, 186))         # cadeira da mesa 2 a estante
    P.cota("h", 448, 722.5, 933, "2,03 m", (878, 440), (878, 418))           # parede do sanitário a cadeira da mesa 3
    P.cota("v", 700, 601.5, 713.5, "1,12 m", (668, 688), (686, 685))         # parede do sanitário à parede dos sanitários
    P.texto((873, 146), "1,10 m", 13, 600, centro_v=(872, 166))              # porta de entrada

    return "\n".join(saida + P.partes)


def fig_planta(vertical):
    corpo = planta(vertical)
    # extensão da planta com cotas e escala (unidades do desenho-base)
    xmin, xmax, ymin, ymax = 130, 1600, 80, 1090
    if not vertical:
        return svg((xmin, ymin, xmax - xmin, ymax - ymin), corpo, 1.0)
    ymin_v = 40  # "Entrada" afastada da parede
    # rotate(90): (x, y) -> (-y, x)
    vb = (-ymax - 10, xmin - 10, ymax - ymin_v + 20, xmax - xmin + 20)
    return svg(vb, f'<g transform="rotate(90)">\n{corpo}\n</g>', 1.0)


# ------------------------------------------------------- quadro de áreas ----
def fig_quadro():
    larg = 700
    p = [txt(10, 24, "Quadro de áreas", 22, 700)]
    yy = 40
    x_m2, x_pct = 540, 690
    p.append(f'<rect x="0" y="{yy}" width="{larg}" height="30" fill="#efefef"/>')
    p += [txt(10, yy + 21, "Ambiente", 16, 700), txt(x_m2, yy + 21, "m²", 16, 700, anchor="end"),
          txt(x_pct, yy + 21, "% do bruto", 16, 700, anchor="end")]
    yy += 30
    paredes_int = round(INTERNA - SOMA_AMB, 1)
    paredes_ext = round(BRUTO - INTERNA, 1)
    linhas = [(n, v, False) for n, v in AMBIENTES] + [
        ("Soma dos ambientes rotulados", SOMA_AMB, True),
        ("Paredes internas e ajustes", paredes_int, False),
        ("Área interna (paredes externas de 15 cm descontadas)", round(INTERNA, 1), True),
        ("Paredes externas", paredes_ext, False),
        (f"Envelope bruto externo ({br(ALT_EXT, 2)} × {br(LARG_EXT, 2)} m)", round(BRUTO, 1), True),
    ]
    for nome, v, forte in linhas:
        w = 700 if forte else 400
        if forte:
            p.append(f'<rect x="0" y="{yy}" width="{larg}" height="28" fill="#f7f7f7"/>')
        p += [txt(10, yy + 20, nome, 15, w), txt(x_m2, yy + 20, br(v), 15, w, anchor="end"),
              txt(x_pct, yy + 20, pct(v), 15, w, anchor="end"),
              f'<path d="M0 {yy + 28}H{larg}" stroke="#dddddd" stroke-width="1"/>']
        yy += 28
    p.append(txt(10, yy + 26, f"Salão por lugar: {br(61.6 / LUGARES, 2)} m²  ·  bruto por lugar: {br(BRUTO / LUGARES, 2)} m²  ·  "
                              f"{LUGARES} lugares (8 mesas × 6)", 15, 600))
    return svg((-15, -5, larg + 30, yy + 26 + 20), "\n".join(p))


# ----------------------------------------------- posição na faixa de busca ----
def fig_faixa():
    xa, xb = 20, 580
    a0, a1 = 90.0, 160.0
    X = lambda m2: xa + (m2 - a0) * (xb - xa) / (a1 - a0)
    p = [txt(0, 24, "Posição do estudo na faixa de busca (m²)", 22, 700)]
    yb1, yb2 = 80, 150
    p.append(txt(X(100), yb1 - 8, "Faixa de busca de imóveis (B5): 100 a 150 m²", 14, 600))
    p.append(f'<rect x="{X(100)}" y="{yb1}" width="{X(150) - X(100)}" height="24" fill="#e8e8e8" stroke="{INK}" stroke-width="1"/>')
    p.append(txt(X(115), yb2 - 8, "Layout completo estimado: 115 a 135 m²", 14, 600, fill=PURPLE))
    p.append(f'<rect x="{X(115)}" y="{yb2}" width="{X(135) - X(115)}" height="24" fill="{PURPLE}" opacity="0.85"/>')
    yax = yb2 + 60
    p.append(f'<path d="M{xa} {yax}H{xb}" stroke="{INK}" stroke-width="1"/>')
    for m in range(90, 161, 10):
        p.append(f'<path d="M{X(m)} {yax}v6" stroke="{INK}" stroke-width="1"/>')
        p.append(txt(X(m), yax + 24, str(m), 14, 400, anchor="middle"))
    for val, cor in ((INTERNA, INK), (BRUTO, INK), (133.5, PURPLE)):
        p.append(f'<path d="M{X(val)} {yax}l-6 -12h12z" fill="{cor}"/>')
    p.append(txt(X(INTERNA) - 6, yax + 52, f"Estudo: interna {br(INTERNA)}", 14, 700, anchor="end"))
    p.append(txt(X(BRUTO) + 6, yax + 52, f"bruta {br(BRUTO)}", 14, 700))
    p.append(txt(X(133.5) + 14, yax + 52, "mediana B5: 133,5", 14, 600, fill=PURPLE))
    p.append(txt(0, yax + 90, "O estudo ocupa o piso da faixa; a diferença até 135 m² é a margem", 13, 400, fill=MUTED))
    p.append(txt(0, yax + 108, "para circulação e apoio que o croqui não desenha.", 13, 400, fill=MUTED))
    return svg((-60, -5, 670, yax + 108 + 25), "\n".join(p))


# ------------------------------------------------------------- legenda ----
def fig_legenda():
    p = [txt(0, 24, "Legenda", 22, 700)]
    y = 54
    p.append(f'<path d="M0 {y}H50" stroke="{GREEN}" stroke-width="3.5" stroke-dasharray="11 7"/>')
    p.append(txt(62, y + 5, "Rota acessível esquemática (faixa-alvo de 1,20 m, NBR 9050)", 15))
    y += 34
    p.append(f'<path d="M0 {y}H50" stroke="{INK}" stroke-width="1" marker-start="url(#seta)" marker-end="url(#seta)"/>')
    p.append(txt(62, y + 5, "Folga medida no desenho entre mobiliários e paredes", 15))
    for rot in ("Mesas 1 a 4: mesa avulsa com 6 cadeiras", "Mesas 5 a 8: booth, com 2 bancos de 3 lugares",
                "Estante do acervo, com 60 cm de profundidade"):
        y += 34
        p.append(f'<rect x="0" y="{y - 10}" width="50" height="20" fill="#F2F2F2" stroke="{INK}" stroke-width="1.5"/>')
        p.append(txt(62, y + 5, rot, 15))
    y += 50
    p.append(f'<path d="M0 {y - 22}H800" stroke="#bdbdbd" stroke-width="1"/>')
    for n in ("Estudo compacto em escala gráfica. Não é projeto legal nem executivo.",
              "Portas: entrada 1,10 m; sanitário acessível 0,90 m; sanitários de 2,3 m² e da equipe 0,60 m (a conferir).",
              "O trecho de 1,12 m do corredor do sanitário acessível fica abaixo da faixa-alvo de 1,20 m.",
              "Medidas, rota acessível e lotação (CBMBA) devem ser confirmadas no imóvel escolhido."):
        p.append(txt(0, y, n, 14, 400, fill=MUTED))
        y += 22
    return svg((-15, -5, 830, y + 5), "\n".join(p))


def main():
    saidas = [
        (NOME, fig_planta(False), 2400),
        (NOME + "_vertical", fig_planta(True), 2000),
        ("7-1_quadro_areas", fig_quadro(), 2200),
        ("7-1_posicao_faixa_busca", fig_faixa(), 2200),
        ("7-1_legenda", fig_legenda(), 2400),
    ]
    for nome, conteudo, larg in saidas:
        s = FIG / f"{nome}.svg"
        s.write_text(conteudo, encoding="utf-8")
        png(s, larg)
        print("OK", s.relative_to(ROOT))
    # as figuras pequenas só existem em PNG para o documento; o SVG fica ao lado como fonte
    print(f"ambientes={SOMA_AMB} interna={INTERNA:.2f} bruto={BRUTO:.2f}")


if __name__ == "__main__":
    main()
