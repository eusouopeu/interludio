"""Gera a planta baixa da alternativa de 12,00 x 12,00 m em SVG editável (1 px = 1 cm).

Saída: textos-tcc/figuras/planta-baixa-12x12.svg. Mesmo estilo e mesmos componentes de
gerar_planta_baixa_svg.py (texturas, cores, rótulos com área, setas de circulação), lidos
de lá para não duplicar código.

Desenho do autor (15/11/2026, "A4 - 1"): ponto em L de 12,00 x 12,00 m externos, sem o
canto inferior direito (4,18 x 4,00 m, fora do imóvel); fachada a leste, com a entrada
em frente ao balcão e ao caixa. Cômodos do protótipo: sanitários feminino e masculino
(1,75 x 1,30 m), corredor de 1,00 m, PCD com fraldário (1,90 x 2,20 m), despensa com
acesso pela cozinha, cozinha, balcão em L com caixa e refrigerador. Salão com 8 mesas
e 48 lugares: 5 mesas soltas de 6 lugares (uma com o módulo da cadeira de rodas), uma
mesa de 6 lugares no centro do fundo e dois sofás de canto em L com mesa quadrada.
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_BASE = Path(__file__).with_name("gerar_planta_baixa_svg.py").read_text(encoding="utf-8")
exec(_BASE.split("# ---------------------------------------------------------------- desenho")[0])

SAIDA = ROOT / "textos-tcc" / "figuras" / "planta-baixa-12x12.svg"
W, D = 1170, 1170          # medidas internas (cm): 12,00 x 12,00 m externos
NX, NY = 752, 770          # canto interno do recorte (fora do imóvel) no canto inferior direito
EXT, INT = 15, 15
M = 90

COMODOS = {
    "fem": (0, 0, 175, 130),
    "masc": (0, 145, 175, 275),
    "circulacao-sanitarios": (190, 0, 290, 290),
    "pcd": (305, 0, 495, 220),
    "deposito": (510, 0, 752, 130),
    "cozinha": (767, 0, W, 390),
    "balcao": (857, 405, W, 655),
}


def cadeira_lateral(nome, x, cy, encosto_a_esquerda, laranja=False):
    """Cadeira 45 x 45 cm virada para leste ou oeste (encosto na lateral)."""
    assento, encosto, veio, borda = ((LARANJA, LARANJA_ENCOSTO, "#f59e4b", "#c2410c")
                                     if laranja else (ASSENTO, ENCOSTO, "#6e4a32", "#2b1a10"))
    with grupo(nome):
        rect(x, cy - 22.5, 45, 45, rx=6, fill=assento, stroke=borda)
        for dy in (-9, 0, 9):
            linha(x + 12, cy + dy, x + 36, cy + dy, cor=veio, sw=0.8)
        ex = x if encosto_a_esquerda else x + 45 - 9
        rect(ex, cy - 22.5, 9, 45, fill=encosto, stroke=borda, rx=3)


def mesa6_vertical(nome, x, y):
    """Mesa 90 x 180 com 3 cadeiras a oeste e 3 a leste (pilha horizontal para Auto Layout)."""
    cys = (y + 30, y + 90, y + 150)
    with grupo(nome):
        with grupo(f"{nome}-cadeiras-oeste"):
            for k, cy in enumerate(cys, 1):
                cadeira_lateral(f"{nome}-cadeira-{k}", x - 40, cy, True, laranja=k % 2 == 1)
        tampo_madeira(f"{nome}-tampo", x, y, 90, 180)
        with grupo(f"{nome}-cadeiras-leste"):
            for k, cy in enumerate(cys, 1):
                cadeira_lateral(f"{nome}-cadeira-{k + 3}", x + 85, cy, False, laranja=k % 2 == 0)


def sofa_canto(nome, x0, y0, espelhar, laranja):
    """Sofá de canto em L (6 lugares) com mesa quadrada de 1,20 x 1,15 m; 1,90 x 1,80 m."""
    assento, encosto, borda = ((LARANJA, LARANJA_ENCOSTO, "#c2410c") if laranja
                               else ("#7a5238", ENCOSTO, "#2b1a10"))
    with grupo(nome):
        with grupo(f"{nome}-sofa"):
            xl = x0 + 180 if espelhar else x0          # encosto lateral
            xs = x0 + 135 if espelhar else x0 + 10     # assento lateral
            rect(xs, y0, 45, 125, fill=assento, stroke=borda, rx=4)
            rect(x0, y0 + 125, 190, 45, fill=assento, stroke=borda, rx=4)
            rect(xl, y0, 10, 180, fill=encosto, stroke=borda, rx=3)
            rect(x0, y0 + 170, 190, 10, fill=encosto, stroke=borda, rx=3)
            linha(xs, y0 + 62, xs + 45, y0 + 62, cor=borda, sw=0.8)
            for k in (63, 127):
                linha(x0 + k, y0 + 125, x0 + k, y0 + 170, cor=borda, sw=0.8)
        tampo_madeira(f"{nome}-tampo", x0 + (10 if espelhar else 60), y0 + 5, 120, 115)


def fogao6_vertical(nome, x, y):
    """Fogão industrial de 6 bocas, 0,85 x 1,10 m, encostado na parede oeste."""
    with grupo(nome):
        rect(x, y, 85, 110, fill=METAL)
        for i in range(2):
            for j in range(3):
                cx, cy = x + 25 + i * 35, y + 20 + j * 35
                ellipse(cx, cy, 13, 13)
                ellipse(cx, cy, 5, 5, fill=TRACO, sw=0)


# ---------------------------------------------------------------- desenho
LARG = W + 2 * EXT + 2 * M + 60
ALT = D + 2 * EXT + 2 * M + 130
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARG} {ALT}" width="{LARG}" height="{ALT}">')
a('<defs><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">'
  '<stop offset="0" stop-color="#f3f4f6"/><stop offset="0.45" stop-color="#c3c8ce"/>'
  '<stop offset="0.55" stop-color="#e2e5e8"/><stop offset="1" stop-color="#a9afb6"/>'
  '</linearGradient></defs>')
a(f'<rect id="fundo" width="{LARG}" height="{ALT}" fill="#ffffff"/>')
a(f'<g id="planta-baixa" transform="translate({M + EXT},{M + EXT})">')

# --- área fora do imóvel (recorte do L), em cinza hachurado
with grupo("fora-do-imovel"):
    x0, y0, x1, y1 = NX + EXT, NY + EXT, W + EXT, D + EXT
    rect(x0, y0, x1 - x0, y1 - y0, fill="#eceef1", stroke="none", sw=0)
    for k in range(0, (x1 - x0) + (y1 - y0), 30):
        xa, ya = x0 + k, y0
        xb, yb = x0, y0 + k
        if xa > x1:
            ya += xa - x1
            xa = x1
        if yb > y1:
            xb += yb - y1
            yb = y1
        linha(xa, ya, xb, yb, cor="#d5d9de", sw=1)
    texto((x0 + x1) / 2, (y0 + y1) / 2, "Fora do imóvel", 14, cor="#6b7280")

# --- piso do salão: porcelanato bege-claro, placas de 60 x 60 cm
with grupo("piso"):
    contorno = [(0, 0), (W, 0), (W, NY), (NX, NY), (NX, D), (0, D)]
    path("M " + " L ".join(f"{x} {y}" for x, y in contorno) + " Z", fill=PISO, stroke="none", sw=0)
    for x in range(60, W, 60):
        linha(x, 0, x, D if x < NX else NY, cor=JUNTA, sw=1)
    for y in range(60, D, 60):
        linha(0, y, W if y < NY else NX, y, cor=JUNTA, sw=1)


def piso_comodo(nome, cor, junta, passo):
    x0, y0, x1, y1 = COMODOS[nome]
    with grupo(f"piso-{nome}"):
        rect(x0, y0, x1 - x0, y1 - y0, fill=cor, stroke="none", sw=0)
        for x in range(x0 + passo, x1, passo):
            linha(x, y0, x, y1, cor=junta, sw=1)
        for y in range(y0 + passo, y1, passo):
            linha(x0, y, x1, y, cor=junta, sw=1)


with grupo("pisos-especiais"):
    for nome in ("fem", "masc", "pcd"):
        piso_comodo(nome, AZULEJO, JUNTA_AZULEJO, 30)
    for nome in ("cozinha", "deposito"):
        piso_comodo(nome, PISO_COZINHA, JUNTA_COZINHA, 45)

# --- paredes externas; fachada a leste, com a entrada em frente ao balcão
ENTRADA = (670, NY)        # vão da porta de entrada na fachada (y inicial e final)
with grupo("paredes-externas"):
    parede_h(-EXT, -EXT, W + EXT, EXT, [], "parede-norte")
    parede_v(-EXT, 0, D + EXT, EXT, [], "parede-oeste")
    parede_h(D, 0, NX + EXT, EXT, [], "parede-sul")
    parede_v(W, 0, NY, EXT, [ENTRADA], "parede-fachada")
    parede_h(NY, NX, W + EXT, EXT, [], "parede-recorte-norte")
    parede_v(NX, NY + EXT, D + EXT, EXT, [], "parede-recorte-oeste")

with grupo("janelas"):
    janela("janela-cozinha", 880, -EXT, 180, EXT)

# --- paredes internas
with grupo("paredes-internas"):
    parede_v(175, 0, 275, INT, [(10, 70), (155, 215)], "parede-sanitarios-corredor", True)
    parede_h(130, 0, 175, INT, [], "parede-fem-masc", True)
    parede_h(275, 0, 190, INT, [], "parede-masc-salao", True)
    parede_v(290, 0, 220, INT, [(10, 100)], "parede-corredor-pcd", True)
    parede_v(495, 0, 220, INT, [], "parede-pcd-despensa", True)
    parede_h(220, 290, 510, INT, [], "parede-pcd-salao", True)
    parede_h(130, 510, NX, INT, [], "parede-despensa-salao", True)
    parede_v(NX, 0, 405, INT, [(5, 85)], "parede-cozinha-oeste", True)
    parede_h(390, NX + INT, W, INT, [(775, 935), (1075, 1155)], "parede-cozinha-sul", True)
    with grupo("passa-pratos"):
        rect(775, 390, 160, 15, fill=CINZA, sw=1)

# --- portas: a 90°, cada folha fica paralela e quase encostada a uma parede
with grupo("portas"):
    porta("porta-sanitario-fem", 175, 10, 60, ((-1, 0), (0, 1)))
    porta("porta-sanitario-masc", 175, 155, 60, ((-1, 0), (0, 1)))
    porta("porta-sanitario-pcd", 305, 10, 90, ((1, 0), (0, 1)))
    porta("porta-despensa", NX, 5, 80, ((-1, 0), (0, 1)))
    porta("porta-cozinha", 1155, 390, 80, ((0, -1), (-1, 0)))
    # entrada de 1,00 m; aberta, a folha encosta na parede do recorte
    porta("porta-entrada", W, NY, 100, ((-1, 0), (0, -1)))

# --- sanitários
with grupo("sanitario-feminino"):
    bacia("bacia-fem", 45, 130, para_baixo=False)
    lavatorio("lavatorio-fem", 128, 95, 45, 35)

with grupo("sanitario-masculino"):
    bacia("bacia-masc", 45, 275, para_baixo=False)
    mictorio("mictorio", 85, 275, para_baixo=False)
    lavatorio("lavatorio-masc", 128, 240, 45, 35)

with grupo("sanitario-pcd"):
    with grupo("giro-150"):
        a(f'<circle cx="400" cy="125" r="75" fill="none" stroke="{TRACEJADO}" '
          f'stroke-width="1" stroke-dasharray="8 5"/>')
    bacia("bacia-pcd", 460, 0)
    with grupo("barras-de-apoio-pcd"):
        rect(489, 24, 5, 80, fill=TRACO, sw=0)
        rect(410, 3, 30, 5, fill=TRACO, sw=0)
    lavatorio("lavatorio-pcd", 306, 112, 35, 45)
    with grupo("trocador-fraldario"):
        rect(400, 170, 80, 50, fill=CLARO, stroke=TRACEJADO, stroke_dasharray="6 4")

# --- despensa (acesso pela cozinha) e cozinha
with grupo("despensa"):
    estante("prateleira-despensa-oeste", 510, 0, 40, 90, jogos=False)
    estante("prateleira-despensa-sul", 510, 90, NX - 510, 40, jogos=False)

with grupo("cozinha"):
    with grupo("bancada-norte"):
        rect(767, 0, 60, 90, fill=METAL)
    with grupo("coifa"):
        rect(767, 90, 100, 120, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="8 5")
    fogao6_vertical("fogao-industrial-6-bocas", 767, 95)
    with grupo("bancada-de-preparo"):
        rect(767, 215, 60, 115, fill=METAL)
    with grupo("bancada-sul"):
        rect(767, 330, 263, 60, fill=METAL)
        with grupo("pia-inox-2-cubas"):
            rect(845, 336, 65, 48, rx=4, fill=CLARO)
            rect(918, 336, 65, 48, rx=4, fill=CLARO)
        texto(855, 323, "passa-pratos ↓", 11)
    lavatorio("lavatorio-de-maos", 1035, 355, 40, 35)
    with grupo("geladeira-industrial-4-portas"):
        rect(1095, 0, 75, 120, fill=METAL)
        linha(1095, 60, 1170, 60)
        texto(1137, 60, "GEL", 12, rot=-90)
    with grupo("freezer-vertical"):
        rect(1095, 125, 75, 85, fill=METAL)
        texto(1137, 167, "FRZ", 12, rot=-90)

# --- balcão em L, em frente à entrada, com caixa e trecho rebaixado
with grupo("balcao"):
    with grupo("pia-de-bar"):
        rect(960, 405, 55, 48, fill=METAL)
        rect(968, 413, 39, 32, rx=4, fill=CLARO)
    with grupo("refrigerador"):
        rect(1095, 495, 75, 90, fill=METAL)
        texto(1137, 540, "refrig.", 11, rot=-90)
    tampo_madeira("balcao-lateral-tampo", 857, 495, 60, 100, MADEIRA_ESCURA, VEIO_ESCURO)
    with grupo("balcao-frontal"):
        tampo_madeira("balcao-frontal-tampo", 857, 595, W - 857, 60, MADEIRA_ESCURA, VEIO_ESCURO)
        rect(1010, 598, 93, 54, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="5 4")
        texto(1056, 640, "rebaixado", 10)
    with grupo("caixa"):
        rect(960, 603, 36, 30, fill=METAL)

# --- acervo: estantes sob o PCD, sob a despensa e junto à parede da cozinha
with grupo("acervo"):
    estante("estante-pcd", 292, 235, 216, 40)
    estante("estante-despensa", 512, 145, NX - 512, 40)
    estante("estante-cozinha", NX - 40, 190, 40, 210)

# --- mesas: 5 mesas soltas, uma mesa no centro do fundo e dois sofás de canto (48 lugares)
with grupo("mesas"):
    with grupo("fileira-1"):
        mesa6("mesa-1", 0, 443)
        mesa6("mesa-2", 275, 443)
    with grupo("fileira-2"):
        mesa6("mesa-3", 0, 733)
        mesa6("mesa-4", 275, 733)
        mesa6("mesa-5", 555, 733, omitir=2)
    with grupo("fileira-3"):
        sofa_canto("sofa-canto-oeste", 0, 990, False, True)
        mesa6_vertical("mesa-7", 331, 990)
        sofa_canto("sofa-canto-leste", NX - 190, 990, True, False)

with grupo("modulo-cadeira-de-rodas"):
    rect(605, 638, 80, 120, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="6 4")
    texto(645, 667, "M.R.", 14)

# --- divisórias tracejadas dos ambientes sem parede
with grupo("divisorias"):
    divisoria("divisoria-circulacao-sanitarios", [(190, 290), (290, 290)])
    divisoria("divisoria-balcao", [(857, 405), (857, 495)])

# --- setas de circulação
with grupo("circulacao"):
    seta("seta-corredor-sanitarios", 190, 250, 290, 250, "1,00 m")
    seta("seta-estante-mesas", 335, 275, 335, 403, "1,28 m")
    seta("seta-fileiras-1-2", 335, 573, 335, 693, "1,20 m")
    seta("seta-fileiras-2-3", 240, 863, 240, 990, "1,27 m")
    seta("seta-mesas-1-2", 180, 488, 275, 488, "0,95 m")
    seta("seta-mesas-4-5", 455, 778, 555, 778, "1,00 m")
    seta("seta-sofa-mesa", 180, 1060, 291, 1060, "1,11 m")
    seta("seta-frente-balcao", 1030, 655, 1030, NY, "1,15 m")
    seta("seta-acesso-balcao", 887, 405, 887, 495, "0,90 m")
    seta("seta-atras-balcao", 1060, 453, 1060, 595, "1,42 m")
    seta("seta-cozinha", 852, 160, 1095, 160, "2,43 m")
    seta("seta-entrada", 1150, 670, 1150, NY, "1,00 m")

# --- nome e área de cada cômodo, no centro
with grupo("rotulos"):
    ROT = {
        "fem": ("Fem.", 80, 40), "masc": ("Masc.", 80, 185),
        "circulacao-sanitarios": ("Circ.", 240, 120), "pcd": ("PCD + fraldário", 400, 128),
        "deposito": ("Despensa", 611, 45), "cozinha": ("Cozinha", 960, 255),
        "balcao": ("Balcão e caixa", 985, 515),
    }
    for nome, (titulo, cx, cy) in ROT.items():
        rotulo_comodo(nome, cx, cy, titulo, area(nome), 16 if nome == "cozinha" else 12)
    TOTAL = W * D - (W - NX) * (D - NY)
    SALAO = TOTAL - sum(area(n) for n in COMODOS) - sum(AREA_PAREDES)
    rotulo_comodo("salao", 585, 310, "Salão de jogos", SALAO, 15)
    texto(W + EXT + 30, (ENTRADA[0] + ENTRADA[1]) / 2, "Entrada", 15, peso="bold", rot=-90)

# --- cotas externas
cota("cota-largura", -EXT, -EXT - 45, W + EXT, -EXT - 45, "12,00 m", (0, -10))
cota("cota-profundidade", -EXT - 45, -EXT, -EXT - 45, D + EXT, "12,00 m", (-12, 0))
cota("cota-recorte-largura", NX + EXT, D + EXT + 45, W + EXT, D + EXT + 45, "4,18 m", (0, 24))
cota("cota-recorte-profundidade", W + EXT + 45, NY + EXT, W + EXT + 45, D + EXT, "4,00 m", (24, 0))

a("</g>")

# --- escala gráfica e nota de área
with grupo("escala-grafica"):
    x0, y0 = M + EXT, M + 2 * EXT + D + 120
    for i in range(5):
        rect(x0 + i * 100, y0, 100, 10, fill=TRACO if i % 2 == 0 else CLARO, sw=1)
    for i in (0, 1, 2, 5):
        texto(x0 + i * 100, y0 + 30, f"{i} m", 14)
    texto(x0 + 560, y0 + 10, f"Área interna: {m2(TOTAL)}", 16, anchor="start")

a("</svg>")

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text("\n".join(out), encoding="utf-8")
soma = sum(area(n) for n in COMODOS) + SALAO + sum(AREA_PAREDES)
print(f"gravado: {SAIDA}")
print(f"área interna {m2(TOTAL)}; cômodos + salão + paredes = {m2(soma)}")
for n in COMODOS:
    print(f"  {n}: {m2(area(n))}")
print(f"  salão: {m2(SALAO)}; paredes internas: {m2(sum(AREA_PAREDES))}")
