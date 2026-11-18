"""Gera a planta baixa esquemática da luderia em SVG editável (escala 1 px = 1 cm).

Saída: textos/figuras/planta-baixa.svg. Cada móvel ou peça é um grupo (<g>) com nome
próprio, pronto para virar componente num editor vetorial.

Desenho do autor (15/11/2026, "A4 - 2"), ajustado às normas: ponto retangular de
8,00 x 13,75 m externos (110 m²), fachada no lado de 13,75 m, com a entrada em frente ao
balcão e ao lado do caixa; 8 mesas de 6 lugares (4 booths e 4 mesas soltas, 48 lugares,
um deles no módulo da cadeira de rodas); sanitários masculino, feminino e PCD com fraldário (Código de Obras
de Salvador, Lei 9.281/2017, art. 32) e um da equipe, com armários (NR-24, itens
24.2.2.2 e 24.6.1 f), sem comunicação direta com a cozinha (RDC 216/2004).

Convenções do desenho:
- Toda porta abre de modo que, a 90°, a folha fique paralela e quase encostada a uma
  parede; em frente a cada porta fica livre um quadrado de pelo menos 0,80 m.
- Cada cômodo tem nome em negrito e a área logo abaixo, no centro. Ambientes sem
  parede (circulação, balcão) são separados por linhas tracejadas cinza-claras.
- Setas duplas marcam a largura das passagens; atrás do balcão, de 0,60 a 0,90 m.
- Mesas com textura de madeira (pínus); pia, fogão, geladeira, freezer, refrigerador
  e caixa com gradiente cinza metálico.

Medidas de referência:
- Portas: entrada de 1,10 m em duas folhas de 0,55 m abrindo para fora, num nicho de
  0,60 m que não invade a calçada; sanitário PCD 0,90 m (vão livre >= 0,80 m, NBR 9050), abrindo
  para dentro, com o giro de 1,50 m fora da varredura da folha; sanitários 0,60 m;
  cozinha e despensa 0,80 m.
- Circulação: 1,20 m no corredor dos sanitários (giro de 90° da cadeira de rodas para
  a porta do PCD); 1,00 a 1,20 m entre mesas e estantes; 2,39 m em frente ao balcão;
  0,80 m atrás do balcão, com acesso por tampa basculante de 0,60 m.
- Sanitário PCD 1,90 x 2,20 m (mínimo de 1,50 x 1,70 m, NBR 9050), com giro de 1,50 m
  e trocador dobrável (fraldário); sanitários masculino, feminino e da equipe
  1,75 x 1,30 m.
- Bacia 0,38 x 0,65 m; lavatório 0,45 x 0,35 m; mictório 0,35 x 0,30 m.
- Mesa solta de 6 lugares 1,80 x 0,90 m; cadeira 0,45 x 0,45 m. Booth com mesa
  1,80 x 0,72 m entre dois bancos de 1,80 x 0,45 m (assento com encosto de 0,10 m).
- Módulo de referência da cadeira de rodas 0,80 x 1,20 m (NBR 9050) no lugar de uma
  cadeira da mesa 7, a primeira depois da entrada.
- Cozinha 5,80 x 2,42 m: bancada de preparo; geladeira industrial 4 portas
  1,20 x 0,75 m; freezer vertical 0,70 x 0,75 m; fogão industrial 6 bocas
  1,10 x 0,85 m com coifa; bancada sul com pia inox de 2 cubas e a janela do
  passa-pratos para o balcão; lavatório exclusivo de mãos junto à porta (RDC 216).
  Despensa com prateleiras, com acesso só pela cozinha.
- Balcão 0,60 m de profundidade, junto à cozinha, com pia de bar, refrigerador, caixa
  no canto inferior direito e trecho rebaixado a 0,90 m de altura (NBR 9050).
- Estantes do acervo 0,40 m de profundidade sob o PCD (1,80 m) e uma estante central
  de dupla face (2 x 3,35 m, 0,60 m de profundidade) entre o balcão e as mesas: 8,50 m
  de frente. As mesas encostam no fundo do salão, sem faixa de circulação vazia.
"""
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SAIDA = ROOT / "textos" / "figuras" / "planta-baixa.svg"

W, D = 770, 1345           # medidas internas (cm): 8,00 x 13,75 m externos
NICHO = (695, 456, 606)    # nicho da entrada na fachada: x da parede da porta, y inicial e final
EXT, INT = 15, 15          # espessura das paredes externas e internas
M = 90                     # margem do desenho

PAREDE = "#2f2f2f"
TRACO = "#333333"
CLARO = "#ffffff"
CINZA = "#f2f2f2"
TRACEJADO = "#8a8a8a"
DIVISORIA = "#c4c4c4"
COTA = "#4a4a4a"
MADEIRA = "#e4c48f"
VEIO = "#b98a4e"
METAL = "url(#metal)"
MADEIRA_ESCURA = "#a8754a"
VEIO_ESCURO = "#74492a"
ASSENTO = "#5a3a26"
ENCOSTO = "#3a2416"
ESTANTE = "#8b5a2b"
PISO = "#f6f0e6"
AZULEJO = "#ffffff"          # sanitários: cerâmica branca 30 x 30 cm
JUNTA_AZULEJO = "#dcdcdc"
PISO_COZINHA = "#e8eaed"     # cozinha e despensa: porcelanato cinza-claro 45 x 45 cm
JUNTA_COZINHA = "#c9ced4"
LARANJA = "#fdba74"          # Tailwind orange-300 (assento)
LARANJA_ENCOSTO = "#fb923c"  # Tailwind orange-400
JUNTA = "#e6dccb"
CORES_JOGOS = ["#d94841", "#f2a541", "#3b7dd8", "#2f9e6f", "#8e5bd0", "#e8d44d",
               "#1f2937", "#f07f9c", "#2bb3c0", "#c2410c"]

out = []
a = out.append
AREA_PAREDES = []          # área das paredes internas (cm²), para fechar a área do salão


def attrs(**kw):
    return " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())


def rect(x, y, w, h, fill=CLARO, stroke=TRACO, sw=1.5, nome=None, **kw):
    n = f'id="{nome}" ' if nome else ""
    a(f'<rect {n}x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
      f'stroke="{stroke}" stroke-width="{sw}" {attrs(**kw)}/>')


def ellipse(cx, cy, rx, ry, fill=CLARO, sw=1.5, stroke=TRACO, **kw):
    a(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" '
      f'stroke="{stroke}" stroke-width="{sw}" {attrs(**kw)}/>')


def path(d, fill="none", stroke=TRACO, sw=1.5, **kw):
    a(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {attrs(**kw)}/>')


def linha(x1, y1, x2, y2, cor=TRACO, sw=1, **kw):
    a(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor}" stroke-width="{sw}" {attrs(**kw)}/>')


def texto(x, y, s, tam=18, anchor="middle", peso="normal", cor="#222", rot=None):
    t = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    a(f'<text x="{x}" y="{y}" font-family="Inter, Arial, sans-serif" font-size="{tam}" '
      f'font-weight="{peso}" fill="{cor}" text-anchor="{anchor}"{t}>{s}</text>')


class grupo:
    def __init__(self, nome):
        self.nome = nome

    def __enter__(self):
        a(f'<g id="{self.nome}">')

    def __exit__(self, *_):
        a("</g>")


def m2(cm2):
    return f"{cm2 / 1e4:.1f}".replace(".", ",") + " m²"


# ---------------------------------------------------------------- paredes
def parede_h(y, x0, x1, t, vaos, nome, interna=False):
    """Parede horizontal de x0 a x1, com vãos [(xa, xb), ...]."""
    if interna:
        AREA_PAREDES.append((x1 - x0) * t)
    xs = [x0] + [v for par in sorted(vaos) for v in par] + [x1]
    for i in range(0, len(xs), 2):
        if xs[i + 1] > xs[i]:
            rect(xs[i], y, xs[i + 1] - xs[i], t, fill=PAREDE, stroke=PAREDE, sw=0,
                 nome=f"{nome}-{i // 2 + 1}")


def parede_v(x, y0, y1, t, vaos, nome, interna=False):
    if interna:
        AREA_PAREDES.append((y1 - y0) * t)
    ys = [y0] + [v for par in sorted(vaos) for v in par] + [y1]
    for i in range(0, len(ys), 2):
        if ys[i + 1] > ys[i]:
            rect(x, ys[i], t, ys[i + 1] - ys[i], fill=PAREDE, stroke=PAREDE, sw=0,
                 nome=f"{nome}-{i // 2 + 1}")


# ---------------------------------------------------------------- componentes
def porta(nome, hx, hy, largura, sentido):
    """Folha aberta a 90° e arco de abertura.

    hx, hy: dobradiça; sentido: ((dx, dy) da folha aberta, (dx, dy) da folha fechada).
    A folha aberta deve ficar paralela a uma parede próxima.
    """
    (fx, fy), (gx, gy) = sentido
    with grupo(nome):
        ex, ey = hx + fx * largura, hy + fy * largura
        px, py = hx + gx * largura, hy + gy * largura
        linha(hx, hy, ex, ey, sw=3)
        cross = fx * gy - fy * gx
        path(f"M {ex} {ey} A {largura} {largura} 0 0 {1 if cross > 0 else 0} {px} {py}",
             sw=1, stroke=TRACEJADO)


def janela(nome, x, y, w, h):
    with grupo(nome):
        rect(x, y, w, h, fill=CLARO, sw=1)
        if w > h:
            linha(x, y + h / 2, x + w, y + h / 2)
        else:
            linha(x + w / 2, y, x + w / 2, y + h)


def bacia(nome, cx, y, para_baixo=True):
    """Bacia 38 x 65 cm: caixa acoplada + assento, encostada na parede em y."""
    with grupo(nome):
        s = 1 if para_baixo else -1
        cy0 = y if para_baixo else y - 18
        rect(cx - 19, cy0, 38, 18, rx=3)
        ellipse(cx, y + s * 42, 17, 23)


def lavatorio(nome, x, y, w=45, h=35):
    with grupo(nome):
        rect(x, y, w, h, rx=3)
        ellipse(x + w / 2, y + h / 2, w / 2 - 8, h / 2 - 7)


def mictorio(nome, x, y, para_baixo=True):
    """Mictório 35 x 30 cm encostado na parede em y."""
    s = 1 if para_baixo else -1
    with grupo(nome):
        path(f"M {x} {y} L {x + 35} {y} L {x + 35} {y + s * 10} "
             f"Q {x + 17.5} {y + s * 40} {x} {y + s * 10} Z", fill=CLARO)


def cadeira(nome, cx, y, encosto_em_cima, laranja=False):
    """Cadeira 45 x 45 cm: marrom-escura ou laranja (Tailwind orange-300/400)."""
    assento, encosto, veio, borda = ((LARANJA, LARANJA_ENCOSTO, "#f59e4b", "#c2410c")
                                     if laranja else (ASSENTO, ENCOSTO, "#6e4a32", "#2b1a10"))
    with grupo(nome):
        rect(cx - 22.5, y, 45, 45, rx=6, fill=assento, stroke=borda)
        for dx in (-9, 0, 9):
            linha(cx + dx, y + 12, cx + dx, y + 36, cor=veio, sw=0.8)
        ey = y if encosto_em_cima else y + 45 - 9
        rect(cx - 22.5, ey, 45, 9, fill=encosto, stroke=borda, rx=3)


def tampo_madeira(nome, x, y, w, h, cor=MADEIRA, veio=VEIO):
    """Tampo de madeira com veios ondulados no sentido do comprimento, em vetor."""
    with grupo(nome):
        rect(x, y, w, h, fill=cor, stroke="#6b4a2a")
        for i, f in enumerate((0.18, 0.36, 0.55, 0.74, 0.88)):
            amp = 3 if i % 2 else -3
            if w >= h:
                yy = y + h * f
                path(f"M {x + 6} {yy} C {x + w * 0.3} {yy + amp}, {x + w * 0.55} {yy - amp}, "
                     f"{x + w - 6} {yy + amp / 2}", stroke=veio, sw=0.9)
            else:
                xx = x + w * f
                path(f"M {xx} {y + 6} C {xx + amp} {y + h * 0.3}, {xx - amp} {y + h * 0.55}, "
                     f"{xx + amp / 2} {y + h - 6}", stroke=veio, sw=0.9)
        if w >= h:
            ellipse(x + w * 0.68, y + h * 0.45, 9, 4, fill="none", stroke=veio, sw=0.9)
        else:
            ellipse(x + w * 0.45, y + h * 0.68, 4, 9, fill="none", stroke=veio, sw=0.9)


def mesa6(nome, x, y, omitir=None):
    """Mesa 180 x 90 com 3 cadeiras de cada lado, em pilha vertical pronta para Auto Layout.

    Pilha: cadeiras-norte (linha de 3, espaço 15, margem 7,5) / tampo / cadeiras-sul,
    com espaço de -5 cm (a cadeira entra 5 cm sob o tampo). Cores alternadas em xadrez.
    omitir: número da cadeira retirada para o módulo da cadeira de rodas.
    """
    with grupo(nome):
        cxs = (x + 30, x + 90, x + 150)
        with grupo(f"{nome}-cadeiras-norte"):
            for k, cx in enumerate(cxs, 1):
                if k != omitir:
                    cadeira(f"{nome}-cadeira-{k}", cx, y - 40, True, laranja=k % 2 == 1)
        tampo_madeira(f"{nome}-tampo", x, y, 180, 90)
        with grupo(f"{nome}-cadeiras-sul"):
            for k, cx in enumerate(cxs, 1):
                if k + 3 != omitir:
                    cadeira(f"{nome}-cadeira-{k + 3}", cx, y + 85, False, laranja=k % 2 == 0)


def estante(nome, x, y, w, h, jogos=True):
    """Estante marrom vista de cima; com jogos coloridos, um pouco desalinhados."""
    rnd = random.Random(nome)
    with grupo(nome):
        rect(x, y, w, h, fill=ESTANTE, stroke="#5b3a1a")
        if not jogos:
            for k in range(1, 4):
                if w < h:
                    linha(x + 3, y + h * k / 4, x + w - 3, y + h * k / 4, cor="#5b3a1a")
                else:
                    linha(x + w * k / 4, y + 3, x + w * k / 4, y + h - 3, cor="#5b3a1a")
            return
        with grupo(f"{nome}-jogos"):
            comp, prof = (h, w) if w < h else (w, h)
            pos = 4
            while True:
                esp = rnd.choice((5, 6, 7, 8, 10, 12))
                if pos + esp > comp - 4:
                    break
                fundo = rnd.uniform(prof * 0.62, prof * 0.82)
                folga = rnd.uniform(2, prof - fundo - 3)
                giro = rnd.uniform(-5, 5)
                cor = rnd.choice(CORES_JOGOS)
                if w < h:
                    bx, by, bw, bh = x + folga, y + pos, fundo, esp
                else:
                    bx, by, bw, bh = x + pos, y + folga, esp, fundo
                cx, cy = bx + bw / 2, by + bh / 2
                rect(round(bx, 1), round(by, 1), round(bw, 1), round(bh, 1), fill=cor,
                     stroke="#1f1f1f", sw=0.5, transform=f"rotate({giro:.1f} {cx:.1f} {cy:.1f})")
                pos += esp + rnd.choice((0, 0.5, 1, 2))


def fogao6(nome, x, y):
    with grupo(nome):
        rect(x, y, 110, 85, fill=METAL)
        for i in range(3):
            for j in range(2):
                cx, cy = x + 20 + i * 35, y + 25 + j * 35
                ellipse(cx, cy, 13, 13)
                ellipse(cx, cy, 5, 5, fill=TRACO, sw=0)


def seta(nome, x1, y1, x2, y2, rotulo):
    """Seta dupla com a largura da passagem escrita acima dela."""
    with grupo(nome):
        linha(x1, y1, x2, y2, cor=COTA, sw=1.2)
        if y1 == y2:      # horizontal
            for x, s in ((x1, 1), (x2, -1)):
                path(f"M {x} {y1} L {x + s * 10} {y1 - 4} L {x + s * 10} {y1 + 4} Z",
                     fill=COTA, stroke=COTA, sw=0.5)
            texto((x1 + x2) / 2, y1 - 6, rotulo, 12, peso="bold", cor=COTA)
        else:             # vertical: texto girado, à esquerda da linha
            for y, s in ((y1, 1), (y2, -1)):
                path(f"M {x1} {y} L {x1 - 4} {y + s * 10} L {x1 + 4} {y + s * 10} Z",
                     fill=COTA, stroke=COTA, sw=0.5)
            texto(x1 - 6, (y1 + y2) / 2, rotulo, 12, peso="bold", cor=COTA, rot=-90)


def seta_diagonal(nome, x1, y1, x2, y2, dx=0, dy=-8):
    """Seta dupla inclinada com a distância real entre dois cantos."""
    dist = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
    with grupo(nome):
        linha(x1, y1, x2, y2, cor=COTA, sw=1.2)
        for (px, py), s in (((x1, y1), 1), ((x2, y2), -1)):
            bx, by = px + s * 10 * ux, py + s * 10 * uy
            path(f"M {px:.1f} {py:.1f} L {bx - 4 * uy:.1f} {by + 4 * ux:.1f} "
                 f"L {bx + 4 * uy:.1f} {by - 4 * ux:.1f} Z", fill=COTA, stroke=COTA, sw=0.5)
        rot = ang if -90 <= ang <= 90 else ang - 180
        tx, ty = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        texto(round(tx, 1), round(ty, 1), f"{dist / 100:.2f} m".replace(".", ","), 11,
              peso="bold", cor=COTA, rot=round(rot, 1))
    return dist


def rotulo_comodo(nome, cx, cy, titulo, area_cm2, tam=13):
    with grupo(f"rotulo-{nome}"):
        texto(cx, cy, titulo, tam, peso="bold")
        texto(cx, cy + tam + 3, m2(area_cm2), tam - 2, cor="#444")


def divisoria(nome, pontos):
    with grupo(nome):
        d = "M " + " L ".join(f"{x} {y}" for x, y in pontos)
        path(d, stroke=DIVISORIA, sw=2, stroke_dasharray="10 6")


def cota(nome, x1, y1, x2, y2, rotulo, desloc):
    """Linha de cota externa com marcas nas pontas; desloc: (dx, dy) do texto."""
    with grupo(nome):
        linha(x1, y1, x2, y2, cor="#555", sw=1)
        hor = y1 == y2
        for x, y in ((x1, y1), (x2, y2)):
            if hor:
                linha(x, y - 8, x, y + 8, cor="#555", sw=1)
            else:
                linha(x - 8, y, x + 8, y, cor="#555", sw=1)
        texto((x1 + x2) / 2 + desloc[0], (y1 + y2) / 2 + desloc[1], rotulo, 16,
              peso="bold", rot=None if hor else -90)


# ---------------------------------------------------------------- cômodos (x0, y0, x1, y1)
COMODOS = {
    "deposito": (0, 0, 175, 242),
    "cozinha": (190, 0, W, 242),
    "masc": (0, 256, 175, 386),
    "fem": (0, 401, 175, 531),
    "equipe": (0, 546, 175, 676),
    "circulacao-sanitarios": (190, 256, 310, 491),
    "pcd": (325, 256, 515, 476),
    "balcao": (530, 256, W, 456),
}


def area(nome):
    x0, y0, x1, y1 = COMODOS[nome]
    return (x1 - x0) * (y1 - y0)


BANCO, TAMPO_BOOTH = 45, 72      # booth: banco com encosto e mesa, em cm


def booth(nome, y, laranja):
    """Booth de 6 lugares: banco 180 x 45 (com encosto de 10), mesa 180 x 72, banco 180 x 45."""
    assento, encosto, borda = ((LARANJA, LARANJA_ENCOSTO, "#c2410c") if laranja
                               else ("#7a5238", ENCOSTO, "#2b1a10"))
    ys = y + BANCO + TAMPO_BOOTH
    with grupo(nome):
        with grupo(f"{nome}-banco-norte"):
            rect(0, y, 180, BANCO, fill=assento, stroke=borda, rx=4)
            rect(0, y, 180, 10, fill=encosto, stroke=borda, rx=3)
            for k in (60, 120):
                linha(k, y + 10, k, y + BANCO, cor=borda, sw=0.8)
        tampo_madeira(f"{nome}-tampo", 0, y + BANCO, 180, TAMPO_BOOTH)
        with grupo(f"{nome}-banco-sul"):
            rect(0, ys, 180, BANCO, fill=assento, stroke=borda, rx=4)
            rect(0, ys + BANCO - 10, 180, 10, fill=encosto, stroke=borda, rx=3)
            for k in (60, 120):
                linha(k, ys, k, ys + BANCO - 10, cor=borda, sw=0.8)


# ---------------------------------------------------------------- desenho
LARG = W + 2 * EXT + 2 * M + 40
ALT = D + 2 * EXT + 2 * M + 90
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARG} {ALT}" width="{LARG}" height="{ALT}">')
a('<defs><linearGradient id="metal" x1="0" y1="0" x2="1" y2="1">'
  '<stop offset="0" stop-color="#f3f4f6"/><stop offset="0.45" stop-color="#c3c8ce"/>'
  '<stop offset="0.55" stop-color="#e2e5e8"/><stop offset="1" stop-color="#a9afb6"/>'
  '</linearGradient></defs>')
a(f'<rect id="fundo" width="{LARG}" height="{ALT}" fill="#ffffff"/>')
a(f'<g id="planta-baixa" transform="translate({M + EXT},{M + EXT})">')

NX, NY0, NY1 = NICHO        # nicho da entrada (com as paredes): x da parede da porta, y inicial e final

# --- piso em porcelanato bege-claro, placas de 60 x 60 cm
with grupo("piso"):
    contorno = [(0, 0), (W, 0), (W, NY0), (NX, NY0), (NX, NY1), (W, NY1), (W, D), (0, D)]
    path("M " + " L ".join(f"{x} {y}" for x, y in contorno) + " Z", fill=PISO, stroke="none", sw=0)
    for x in range(60, W, 60):
        if x < NX:
            linha(x, 0, x, D, cor=JUNTA, sw=1)
        else:
            linha(x, 0, x, NY0, cor=JUNTA, sw=1)
            linha(x, NY1, x, D, cor=JUNTA, sw=1)
    for y in range(60, D, 60):
        linha(0, y, NX if NY0 < y < NY1 else W, y, cor=JUNTA, sw=1)


def piso_comodo(nome, cor, junta, passo):
    x0, y0, x1, y1 = COMODOS[nome]
    with grupo(f"piso-{nome}"):
        rect(x0, y0, x1 - x0, y1 - y0, fill=cor, stroke="none", sw=0)
        for x in range(x0 + passo, x1, passo):
            linha(x, y0, x, y1, cor=junta, sw=1)
        for y in range(y0 + passo, y1, passo):
            linha(x0, y, x1, y, cor=junta, sw=1)


with grupo("pisos-especiais"):
    for nome in ("masc", "fem", "pcd", "equipe"):
        piso_comodo(nome, AZULEJO, JUNTA_AZULEJO, 30)
    for nome in ("cozinha", "deposito"):
        piso_comodo(nome, PISO_COZINHA, JUNTA_COZINHA, 45)

# --- paredes externas; a fachada é o lado direito, com a entrada junto ao caixa
with grupo("paredes-externas"):
    parede_h(-EXT, -EXT, W + EXT, EXT, [], "parede-fundo")
    parede_v(-EXT, 0, D + EXT, EXT, [], "parede-lateral-esquerda")
    parede_h(D, -EXT, W + EXT, EXT, [], "parede-lateral-sul")
    parede_v(W, -EXT, D + EXT, EXT, [(NY0 + EXT, NY1 - EXT)], "parede-fachada")
    parede_h(NY0, NX, W + EXT, EXT, [], "parede-nicho-norte")
    parede_h(NY1 - EXT, NX, W + EXT, EXT, [], "parede-nicho-sul")
    parede_v(NX, NY0 + EXT, NY1 - EXT, EXT, [(NY0 + 20, NY0 + 130)], "parede-porta-entrada")

with grupo("janelas"):
    janela("janela-cozinha", 250, -EXT, 180, EXT)
    janela("vitrine-1", W, 650, EXT, 300)
    janela("vitrine-2", W, 1000, EXT, 280)

# --- paredes internas
with grupo("paredes-internas"):
    parede_v(175, 0, 242, INT, [(10, 90)], "parede-despensa-cozinha", True)
    parede_h(242, 0, W, INT, [(200, 280), (620, 700)], "parede-cozinha-sul", True)
    parede_v(175, 256, 691, INT, [(266, 326), (411, 471), (556, 616)],
             "parede-sanitarios-corredor", True)
    parede_h(386, 0, 175, INT, [], "parede-masc-fem", True)
    parede_h(531, 0, 175, INT, [], "parede-fem-equipe", True)
    parede_h(676, 0, 175, INT, [], "parede-equipe-salao", True)
    parede_v(310, 256, 476, INT, [(266, 356)], "parede-corredor-pcd", True)
    parede_h(476, 310, 530, INT, [], "parede-pcd-salao", True)
    parede_v(515, 256, 476, INT, [], "parede-pcd-balcao", True)
    with grupo("passa-pratos"):
        rect(620, 242, 80, 14, fill=CINZA, sw=1)

# --- portas: a 90°, cada folha fica paralela e quase encostada a uma parede
with grupo("portas"):
    porta("porta-deposito", 175, 10, 80, ((-1, 0), (0, 1)))                # junto à parede do fundo
    porta("porta-cozinha", 200, 242, 80, ((0, -1), (1, 0)))                # junto à parede da despensa
    porta("porta-sanitario-masc", 175, 266, 60, ((-1, 0), (0, 1)))         # junto à parede da cozinha
    porta("porta-sanitario-fem", 175, 411, 60, ((-1, 0), (0, 1)))          # junto à parede masc/fem
    porta("porta-sanitario-equipe", 175, 556, 60, ((-1, 0), (0, 1)))       # junto à parede fem/equipe
    porta("porta-sanitario-pcd", 325, 266, 90, ((1, 0), (0, 1)))           # junto à parede da cozinha
    # entrada: duas folhas de 0,55 m (1,10 m, 2 unidades de passagem), abrindo para fora,
    # cada uma encostada numa parede do nicho, que não deixa a folha invadir a calçada
    porta("porta-entrada-norte", NX + EXT, NY0 + 20, 55, ((1, 0), (0, 1)))
    porta("porta-entrada-sul", NX + EXT, NY0 + 130, 55, ((1, 0), (0, -1)))

# --- sanitários
with grupo("sanitario-masculino"):
    bacia("bacia-masc", 45, 386, para_baixo=False)
    mictorio("mictorio", 85, 386, para_baixo=False)
    lavatorio("lavatorio-masc", 128, 351, 45, 35)

with grupo("sanitario-feminino"):
    bacia("bacia-fem", 45, 531, para_baixo=False)
    lavatorio("lavatorio-fem", 128, 496, 45, 35)

with grupo("sanitario-equipe"):
    bacia("bacia-equipe", 45, 676, para_baixo=False)
    lavatorio("lavatorio-equipe", 128, 641, 45, 35)
    with grupo("armarios-equipe"):
        rect(0, 546, 105, 35, fill=CINZA)
        for xx in (35, 70):
            linha(xx, 546, xx, 581)

with grupo("sanitario-pcd"):
    with grupo("giro-150"):
        a(f'<circle cx="440" cy="400" r="75" fill="none" stroke="{TRACEJADO}" '
          f'stroke-width="1" stroke-dasharray="8 5"/>')
    bacia("bacia-pcd", 470, 256)
    with grupo("barras-de-apoio-pcd"):
        rect(509, 280, 5, 80, fill=TRACO, sw=0)
        rect(425, 259, 30, 5, fill=TRACO, sw=0)
    lavatorio("lavatorio-pcd", 326, 372, 35, 45)
    with grupo("trocador-fraldario"):
        rect(372, 426, 80, 50, fill=CLARO, stroke=TRACEJADO, stroke_dasharray="6 4")

# --- despensa (acesso só pela cozinha) e cozinha
with grupo("despensa"):
    estante("prateleira-despensa-oeste", 0, 0, 40, 242, jogos=False)
    estante("prateleira-despensa-sul", 40, 202, 135, 40, jogos=False)

with grupo("cozinha"):
    with grupo("bancada-de-preparo"):
        rect(230, 0, 210, 60, fill=METAL)
    with grupo("geladeira-industrial-4-portas"):
        rect(450, 0, 120, 75, fill=METAL)
        linha(510, 0, 510, 75)
        texto(510, 92, "GEL", 12)
    with grupo("freezer-vertical"):
        rect(580, 0, 70, 75, fill=METAL)
        texto(615, 92, "FRZ", 12)
    with grupo("coifa"):
        rect(655, 0, 115, 100, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="8 5")
    fogao6("fogao-industrial-6-bocas", 660, 0)
    lavatorio("lavatorio-de-maos", 286, 207, 40, 35)
    with grupo("bancada-sul"):
        rect(330, 182, 440, 60, fill=METAL)
        with grupo("pia-inox-2-cubas"):
            rect(345, 188, 70, 48, rx=4, fill=CLARO)
            rect(425, 188, 70, 48, rx=4, fill=CLARO)
        texto(660, 216, "passa-pratos", 11)

# --- balcão e caixa, em frente à entrada
with grupo("balcao"):
    with grupo("balcao-traseiro"):
        tampo_madeira("balcao-traseiro-tampo", 530, 256, 170, 60, MADEIRA_ESCURA, VEIO_ESCURO)
        with grupo("pia-de-bar"):
            rect(540, 262, 55, 48, fill=METAL)
            rect(548, 270, 39, 32, rx=4, fill=CLARO)
    with grupo("refrigerador"):
        rect(700, 256, 70, 60, fill=METAL)
        texto(735, 290, "refrig.", 11)
    with grupo("balcao-frontal"):
        tampo_madeira("balcao-frontal-tampo", 530, 396, 240, 60, MADEIRA_ESCURA, VEIO_ESCURO)
        with grupo("tampa-basculante"):
            rect(533, 399, 54, 54, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="5 4")
            texto(560, 430, "tampa", 10)
        rect(597, 399, 93, 54, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="5 4")
        texto(620, 440, "rebaixado", 10)
    with grupo("caixa"):
        rect(652, 403, 36, 30, fill=METAL)

# --- acervo: 8,5 m de frente de estantes
with grupo("acervo"):
    estante("estante-pcd", 335, 491, 180, 40)
    with grupo("estante-central-dupla-face"):
        estante("estante-central-norte", 295, 695, 335, 30)
        estante("estante-central-sul", 295, 725, 335, 30)

# --- mesas: 4 booths junto à parede e 4 mesas soltas (8 mesas, 48 lugares)
C1, C2 = 295, 585
with grupo("mesas"):
    with grupo("booths"):
        for k in range(4):
            booth(f"booth-{k + 1}", 691 + k * (2 * BANCO + TAMPO_BOOTH), laranja=k % 2 == 0)
    with grupo("coluna-1"):
        mesa6("mesa-5", C1, 895)
        mesa6("mesa-6", C1, 1185)
    with grupo("coluna-2"):
        mesa6("mesa-7", C2, 895, omitir=2)
        mesa6("mesa-8", C2, 1185)

with grupo("modulo-cadeira-de-rodas"):
    rect(C2 + 50, 800, 80, 120, fill="none", stroke=TRACEJADO, sw=1, stroke_dasharray="6 4")
    texto(C2 + 90, 829, "M.R.", 14)

# --- divisórias tracejadas dos ambientes sem parede
with grupo("divisorias"):
    divisoria("divisoria-circulacao-sanitarios", [(190, 491), (310, 491)])

# --- setas de circulação
with grupo("circulacao"):
    seta("seta-corredor-sanitarios", 190, 440, 310, 440, "1,20 m")
    seta("seta-estantes", C1 + 60, 531, C1 + 60, 695, "1,64 m")
    seta("seta-estante-mesa", C1 + 60, 755, C1 + 60, 855, "1,00 m")
    seta("seta-fileiras-c1", C1 + 60, 1025, C1 + 60, 1145, "1,20 m")
    seta("seta-fileiras-c2", C2 + 60, 1025, C2 + 60, 1145, "1,20 m")
    seta("seta-booths", 180, 940, C1, 940, "1,15 m")
    seta("seta-colunas", C1 + 180, 1230, C2, 1230, "1,10 m")
    seta("seta-frente-balcao", 610, 456, 610, 695, "2,39 m")
    seta("seta-passagem-leste", 630, 725, W, 725, "1,40 m")
    seta("seta-atras-balcao", 760, 316, 760, 396, "0,80 m")
    seta("seta-tampa", 530, 470, 590, 470, "0,60 m")
    seta("seta-cozinha", 715, 85, 715, 182, "0,97 m")
    seta("seta-cozinha-preparo", 400, 60, 400, 182, "1,22 m")
    seta("seta-entrada", NX - 25, NY0 + 20, NX - 25, NY0 + 130, "1,10 m")

# --- nome e área de cada cômodo, no centro
with grupo("rotulos"):
    ROT = {
        "deposito": ("Despensa", 108, 130), "cozinha": ("Cozinha", 560, 135),
        "masc": ("Masc.", 80, 296), "fem": ("Fem.", 80, 441),
        "equipe": ("Equipe", 62, 596), "circulacao-sanitarios": ("Circ.", 250, 330),
        "pcd": ("PCD + fraldário", 440, 392), "balcao": ("Balcão e caixa", 650, 345),
    }
    for nome, (titulo, cx, cy) in ROT.items():
        rotulo_comodo(nome, cx, cy, titulo, area(nome),
                      16 if nome == "cozinha" else (11 if nome == "equipe" else 12))
    TOTAL = W * D - (W - NX) * (NY1 - NY0)
    SALAO = TOTAL - sum(area(n) for n in COMODOS) - sum(AREA_PAREDES)
    rotulo_comodo("salao", 455, 615, "Salão de jogos", SALAO, 15)
    texto(W + EXT + 30, (NY0 + NY1) / 2, "Entrada", 15, peso="bold", rot=-90)

# --- cotas externas
cota("cota-largura", -EXT, -EXT - 45, W + EXT, -EXT - 45, "8,00 m", (0, -10))
cota("cota-profundidade", -EXT - 45, -EXT, -EXT - 45, D + EXT, "13,75 m", (-12, 0))

a("</g>")

# --- escala gráfica e nota de área
with grupo("escala-grafica"):
    x0, y0 = M + EXT, M + 2 * EXT + D + 95
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
