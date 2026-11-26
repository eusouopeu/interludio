"""Gera a planta baixa da alternativa (b) da L37: 11,00 x 11,60 m, sem booths (1 px = 1 cm).

Saída: textos-tcc/figuras/planta-baixa-10x12.svg. Mesmo estilo e componentes de
gerar_planta_baixa_svg.py, lidos de lá para não duplicar código.

Pedido do autor (15/11/2026, revisão): até 130 m², só mesas soltas (0,95 m entre mesas,
1,20 m entre fileiras), podendo encostar na parede a cabeceira sem cadeiras; despensa
própria; sanitários com louças bem dispostas e portas fora da vista das mesas; sanitário
de funcionários folgado; cozinha escondida do salão; metade da estante da versão anterior.
Desenho:
- bloco de sanitários a oeste, com corredor próprio e uma só abertura para o salão; a
  parede do corredor recebe a estante (4,0 m);
- a leste, cozinha, despensa e sanitário com vestiário de funcionários, abertos para a
  área de trabalho atrás do balcão: a cozinha só se comunica com o bar;
- salão com duas fileiras de 4 mesas de 1,80 x 0,90 m, as das pontas com a cabeceira na
  parede: 8 mesas, 47 cadeiras e o módulo da cadeira de rodas (48 lugares);
- entrada no eixo do corredor central, de frente para o caixa, com banco de espera e
  expositor de jogos à venda junto à fachada.
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
_BASE = Path(__file__).with_name("gerar_planta_baixa_svg.py").read_text(encoding="utf-8")
exec(_BASE.split("# ---------------------------------------------------------------- desenho")[0])

SAIDA = ROOT / "textos-tcc" / "figuras" / "planta-baixa-10x12.svg"
W, D = 1070, 1130          # medidas internas (cm): 11,00 x 11,60 m externos
EXT, INT = 15, 15
M = 90

COMODOS = {
    "fem": (0, 0, 150, 230),
    "masc": (165, 0, 315, 230),
    "pcd": (330, 0, 500, 230),
    "circulacao-sanitarios": (0, 245, 500, 345),
    "cozinha": (515, 0, 855, 280),
    "despensa": (870, 0, W, 120),
    "func": (870, 135, W, 280),
    "balcao": (515, 295, W, 455),
}

# tampos (x, y) das mesas: cabeceiras das pontas encostadas nas paredes oeste e leste
MESAS = [(0, 540), (275, 540), (615, 615), (890, 615),
         (0, 830), (275, 830), (615, 905), (890, 905)]


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

with grupo("piso"):
    rect(0, 0, W, D, fill=PISO, stroke="none", sw=0)


def piso_comodo(nome, cor):
    x0, y0, x1, y1 = COMODOS[nome]
    with grupo(f"piso-{nome}"):
        rect(x0, y0, x1 - x0, y1 - y0, fill=cor, stroke="none", sw=0)


with grupo("pisos-especiais"):
    for nome in ("fem", "masc", "pcd", "circulacao-sanitarios", "func"):
        piso_comodo(nome, AZULEJO)
    for nome in ("cozinha", "despensa", "balcao"):
        piso_comodo(nome, PISO_COZINHA)

# --- paredes externas; fachada ao sul, entrada no eixo do corredor central
ENTRADA = (485, 585)
with grupo("paredes-externas"):
    parede_h(-EXT, -EXT, W + EXT, EXT, [], "parede-norte")
    parede_v(-EXT, 0, D + EXT, EXT, [], "parede-oeste")
    parede_v(W, 0, D + EXT, EXT, [], "parede-leste")
    parede_h(D, 0, W, EXT, [ENTRADA], "parede-fachada")

with grupo("janelas"):
    janela("janela-cozinha", 640, -EXT, 140, EXT)
    janela("vitrine-fachada-oeste", 40, D, 400, EXT)
    janela("vitrine-fachada-leste", 640, D, 380, EXT)

# --- paredes internas
PASSA = (560, 690)
with grupo("paredes-internas"):
    parede_v(150, 0, 230, INT, [], "parede-fem-masc", True)
    parede_v(315, 0, 230, INT, [], "parede-masc-pcd", True)
    parede_h(230, 0, 500, INT, [(20, 90), (185, 255), (340, 430)], "parede-sanitarios-corredor", True)
    parede_h(345, 0, 500, INT, [(400, 500)], "parede-corredor-salao", True)
    parede_v(500, 0, 455, INT, [], "parede-sanitarios-servico", True)
    parede_v(855, 0, 280, INT, [(20, 100)], "parede-cozinha-despensa", True)
    parede_h(120, 870, W, INT, [], "parede-despensa-func", True)
    parede_h(280, 515, W, INT, [PASSA, (760, 840), (970, 1040)], "parede-servico-bar", True)
    with grupo("passa-pratos"):
        rect(PASSA[0], 280, PASSA[1] - PASSA[0], INT, fill=CINZA, sw=1)

# --- portas: a 90°, folha paralela à parede mais próxima
with grupo("portas"):
    porta("porta-sanitario-fem", 20, 230, 70, ((0, -1), (1, 0)))
    porta("porta-sanitario-masc", 185, 230, 70, ((0, -1), (1, 0)))
    porta("porta-sanitario-pcd", 340, 230, 90, ((0, -1), (1, 0)))
    porta("porta-despensa", 870, 20, 80, ((1, 0), (0, 1)))
    porta("porta-cozinha", 840, 280, 80, ((0, -1), (-1, 0)))
    porta("porta-sanitario-func", 1040, 280, 70, ((0, -1), (-1, 0)))
    porta("porta-entrada", ENTRADA[1], D, 100, ((0, -1), (-1, 0)))

# --- sanitários: louças na parede do fundo, lavatório ao lado da bacia
with grupo("sanitario-feminino"):
    bacia("bacia-fem", 45, 0)
    lavatorio("lavatorio-fem", 95, 0, 45, 35)

with grupo("sanitario-masculino"):
    bacia("bacia-masc", 210, 0)
    mictorio("mictorio", 255, 0)
    lavatorio("lavatorio-masc", 280, 105, 35, 45)

with grupo("sanitario-pcd"):
    with grupo("giro-150"):
        a(f'<circle cx="410" cy="150" r="75" fill="none" stroke="{TRACEJADO}" '
          f'stroke-width="1" stroke-dasharray="8 5"/>')
    bacia("bacia-pcd", 460, 0)
    with grupo("barras-de-apoio-pcd"):
        rect(494, 24, 5, 80, fill=TRACO, sw=0)
        rect(410, 3, 30, 5, fill=TRACO, sw=0)
    lavatorio("lavatorio-pcd", 331, 40, 35, 45)
    with grupo("trocador-fraldario"):
        rect(450, 120, 50, 80, fill=CLARO, stroke=TRACEJADO, stroke_dasharray="6 4")

with grupo("sanitario-funcionarios"):
    bacia("bacia-func", 1030, 135)
    lavatorio("lavatorio-func", 950, 135, 45, 35)
    with grupo("armarios-funcionarios"):
        rect(870, 165, 40, 110, fill=CINZA, stroke=TRACO)
        for k in (202, 239):
            linha(870, k, 910, k)

# --- despensa, com acesso só pela cozinha
with grupo("despensa"):
    estante("prateleira-despensa-leste", W - 40, 0, 40, 120, jogos=False)
    estante("prateleira-despensa-sul", 940, 80, W - 40 - 940, 40, jogos=False)

# --- cozinha: abre só para a área de trabalho do bar
with grupo("cozinha"):
    with grupo("coifa"):
        rect(515, 5, 100, 120, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="8 5")
    fogao6_vertical("fogao-industrial-6-bocas", 515, 10)
    with grupo("bancada-de-preparo"):
        rect(515, 125, 60, 90, fill=METAL)
    with grupo("bancada-norte"):
        rect(630, 0, 145, 60, fill=METAL)
        with grupo("pia-inox-2-cubas"):
            rect(638, 6, 62, 48, rx=4, fill=CLARO)
            rect(706, 6, 62, 48, rx=4, fill=CLARO)
    with grupo("freezer-vertical"):
        rect(780, 0, 75, 65, fill=METAL)
        texto(817, 37, "FRZ", 12)
    with grupo("geladeira-industrial-4-portas"):
        rect(780, 70, 75, 120, fill=METAL)
        linha(780, 130, 855, 130)
        texto(817, 130, "GEL", 12, rot=-90)
    with grupo("bancada-passa-pratos"):
        rect(PASSA[0], 220, PASSA[1] - PASSA[0], 60, fill=METAL)
        texto(625, 212, "passa-pratos ↓", 11)
    lavatorio("lavatorio-de-maos", 705, 245, 45, 35)

# --- balcão: área de trabalho atrás do balcão, que esconde a cozinha do salão
with grupo("balcao"):
    with grupo("pia-de-bar"):
        rect(870, 295, 55, 48, fill=METAL)
        rect(878, 303, 39, 32, rx=4, fill=CLARO)
    with grupo("balcao-frontal"):
        tampo_madeira("balcao-frontal-tampo", 600, 395, W - 600, 60, MADEIRA_ESCURA, VEIO_ESCURO)
        rect(680, 398, 90, 54, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="5 4")
        texto(725, 430, "rebaixado", 10)
        rect(940, 398, 120, 54, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="5 4")
        texto(1000, 430, "refrigerador sob o balcão", 9)
    with grupo("caixa"):
        rect(615, 405, 36, 30, fill=METAL)

# --- acervo: estante na parede do corredor dos sanitários
with grupo("acervo"):
    estante("estante-corredor", 0, 360, 400, 40)

# --- espera junto à fachada: banco estofado e expositor de jogos à venda
with grupo("espera"):
    with grupo("banco-de-espera"):
        rect(40, D - 45, 200, 45, fill=LARANJA, stroke="#c2410c", rx=4)
        rect(40, D - 10, 200, 10, fill=LARANJA_ENCOSTO, stroke="#c2410c", rx=3)
        for k in (107, 173):
            linha(k, D - 45, k, D - 10, cor="#c2410c", sw=0.8)
    estante("expositor-jogos-a-venda", 290, D - 40, 150, 40)

# --- mesas: duas fileiras de 4, cabeceiras das pontas nas paredes (8 mesas, 48 lugares)
with grupo("mesas"):
    for i, (x, y) in enumerate(MESAS, 1):
        mesa6(f"mesa-{i}", x, y, omitir=5 if i == 2 else None)

with grupo("modulo-cadeira-de-rodas"):
    rect(325, 580, 80, 120, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="6 4")
    texto(365, 690, "M.R.", 13)

# --- setas de circulação
with grupo("circulacao"):
    seta("seta-corredor-sanitarios", 60, 245, 60, 345, "1,00 m")
    seta("seta-frente-estante", 330, 400, 330, 500, "1,00 m")
    seta("seta-mesas-1-2", 180, 585, 275, 585, "0,95 m")
    seta("seta-mesas-3-4", 795, 660, 890, 660, "0,95 m")
    seta("seta-corredor-central", 455, 760, 615, 760, "1,60 m")
    seta("seta-fileiras-oeste", 150, 670, 150, 790, "1,20 m")
    seta("seta-fileiras-leste", 950, 745, 950, 865, "1,20 m")
    seta("seta-frente-balcao", 840, 455, 840, 575, "1,20 m")
    seta("seta-modulo", 365, 700, 365, 790, "0,90 m")
    seta("seta-espera", 150, 960, 150, D - 45, "1,25 m")
    seta("seta-fachada-leste", 950, 1035, 950, D, "0,95 m")
    seta("seta-atras-balcao", 640, 295, 640, 395, "1,00 m")
    seta("seta-acesso-balcao", 515, 425, 600, 425, "0,85 m")
    seta("seta-cozinha", 600, 150, 780, 150, "1,80 m")

# --- nome e área de cada cômodo
with grupo("rotulos"):
    ROT = {
        "fem": ("Fem.", 75, 130), "masc": ("Masc.", 220, 150),
        "pcd": ("PCD + fraldário", 400, 215), "circulacao-sanitarios": ("Circ.", 250, 300),
        "cozinha": ("Cozinha", 690, 110), "despensa": ("Despensa", 935, 45),
        "func": ("Func. + vestiário", 975, 220), "balcao": ("Bar e caixa", 790, 340),
    }
    for nome, (titulo, cx, cy) in ROT.items():
        rotulo_comodo(nome, cx, cy, titulo, area(nome), 15 if nome == "cozinha" else 11)
    TOTAL = W * D
    SALAO = TOTAL - sum(area(n) for n in COMODOS) - sum(AREA_PAREDES)
    rotulo_comodo("salao", 535, 520, "Salão de jogos", SALAO, 15)
    texto(335, 1060, "Espera", 13, peso="bold")
    texto((ENTRADA[0] + ENTRADA[1]) / 2, D + EXT + 30, "Entrada", 15, peso="bold")

# --- cotas externas
cota("cota-largura", -EXT, -EXT - 45, W + EXT, -EXT - 45, "11,00 m", (0, -10))
cota("cota-profundidade", -EXT - 45, -EXT, -EXT - 45, D + EXT, "11,60 m", (-12, 0))

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
print(f"área externa {m2((W + 2 * EXT) * (D + 2 * EXT))}; interna {m2(TOTAL)}; "
      f"cômodos + salão + paredes = {m2(soma)}")
for n in COMODOS:
    print(f"  {n}: {m2(area(n))}")
print(f"  salão: {m2(SALAO)}; paredes internas: {m2(sum(AREA_PAREDES))}")
