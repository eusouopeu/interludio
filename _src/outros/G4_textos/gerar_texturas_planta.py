"""Texturas procedurais (1 px = 1 cm) das plantas baixas no Figma.

Uso: python3 gerar_texturas_planta.py <pasta_saida>. Gera PNGs tileáveis (piso
vinílico, porcelanatos, madeiras e inox) e um JSON com os JPEG em base64.
"""
import base64, io, json, sys
import numpy as np
from PIL import Image

OUT = sys.argv[1]
rng = np.random.default_rng(7)


def ruido(h, w, escala_y, escala_x, seed):
    """Ruído periódico (tileável) por filtro no domínio da frequência."""
    r = np.random.default_rng(seed).standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    filtro = np.exp(-((fy * escala_y) ** 2 + (fx * escala_x) ** 2))
    n = np.real(np.fft.ifft2(np.fft.fft2(r) * filtro))
    return (n - n.mean()) / (n.std() + 1e-9)


def cor(hexa):
    return np.array([int(hexa[i:i + 2], 16) for i in (1, 3, 5)], float)


def veio(h, w, seed, aneis=9.0):
    """Veio de madeira ao longo de x: faixas onduladas + fibras finas."""
    y = np.arange(h)[:, None] / h
    dist = ruido(h, w, 25, w * 0.35, seed) * 0.10
    fibras = ruido(h, w, 1.5, w * 0.6, seed + 1)
    an = np.sin((y + dist) * np.pi * 2 * aneis + ruido(h, w, 30, w * 0.25, seed + 2) * 0.6)
    return 0.55 * an + 0.35 * fibras


def madeira(h, w, base, seed, contraste=22, aneis=9.0):
    v = veio(h, w, seed, aneis)
    img = cor(base)[None, None, :] + v[..., None] * contraste * np.array([1.0, 0.85, 0.65])
    return img


def salvar(nome, img, q=80):
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    im.save(f"{OUT}/{nome}.png")
    return base64.b64encode(buf.getvalue()).decode()


tex = {}

# 1. piso vinílico amadeirado (carvalho claro): réguas de 20 x 120 cm, tile 240 x 240
H = W = 240
img = np.zeros((H, W, 3))
for i in range(12):
    y0 = i * 20
    off = (i * 60 + (37 if i % 2 else 0)) % 120
    for j in range(-1, 3):
        x0 = off + j * 120
        s = int(rng.integers(1e6))
        tabua = madeira(20, 120, "#e9d8b8", s, contraste=10, aneis=2.5)
        tabua += rng.normal(0, 7)  # cada régua com tom próprio
        for xx in range(120):
            X = (x0 + xx) % W
            img[y0:y0 + 20, X] = tabua[:, xx]
    img[y0, :] = img[y0, :] * 0.82  # junta longitudinal
for i in range(12):
    off = (i * 60 + (37 if i % 2 else 0)) % 120
    for x in (off, off + 120):
        img[i * 20:(i + 1) * 20, x % W] *= 0.85  # topo das réguas
img += ruido(H, W, 60, 60, 99)[..., None] * 2
tex["piso_madeira"] = salvar("piso_madeira", img)

# 2. porcelanato branco 30 x 30 com veio de mármore leve, tile 120 x 120
H = W = 120
m = ruido(H, W, 12, 12, 3)
veios = np.exp(-np.abs(np.sin(m * 2.2)) * 9)
img = cor("#f7f7f5")[None, None, :] - veios[..., None] * 18 + ruido(H, W, 80, 80, 4)[..., None] * 2
for k in range(0, 120, 30):
    img[k:k + 1, :] = cor("#cfcfcf"); img[:, k:k + 1] = cor("#cfcfcf")
tex["porcelanato_branco"] = salvar("porcelanato_branco", img)

# 3. porcelanato cinza antiderrapante 45 x 45, tile 180 x 180
H = W = 180
img = cor("#e1e4e8")[None, None, :] + ruido(H, W, 140, 140, 5)[..., None] * 5 + ruido(H, W, 10, 10, 6)[..., None] * 3
for k in range(0, 180, 45):
    img[k:k + 1, :] = cor("#aab1b9"); img[:, k:k + 1] = cor("#aab1b9")
tex["porcelanato_cinza"] = salvar("porcelanato_cinza", img)

# 4. tampo de madeira clara (freijó), 360 x 180, veio em x
tex["madeira_clara"] = salvar("madeira_clara", madeira(180, 360, "#dcb47c", 11, 20, 7))
# 5. madeira média (balcão), 400 x 120
tex["madeira_media"] = salvar("madeira_media", madeira(120, 400, "#9c6a40", 12, 18, 5))
# 6. madeira escura (estantes), 240 x 60
tex["madeira_escura"] = salvar("madeira_escura", madeira(60, 240, "#7a4e27", 13, 14, 3))

# 7. inox escovado, tile 200 x 200, escovado em x
H = W = 200
esc = ruido(H, W, 1.2, W * 0.9, 8)
img = cor("#cfd3d8")[None, None, :] + esc[..., None] * 9 + ruido(H, W, 3, 3, 9)[..., None] * 6
tex["inox"] = salvar("inox", img, q=82)

json.dump(tex, open(f"{OUT}/texturas.json", "w"))
for k, v in tex.items():
    print(k, len(v))
