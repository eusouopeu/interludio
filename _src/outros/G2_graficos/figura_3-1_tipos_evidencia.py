"""Renderiza a Figura 3.1 (categorias N1–N6, sem hierarquia) a partir do SVG-fonte."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
FONTE = Path(__file__).with_suffix(".svg")
SAIDA = ROOT / "textos-tcc" / "figuras" / "3-1_tipos_evidencia.png"


def main() -> None:
    renderizador = shutil.which("rsvg-convert")
    if not renderizador:
        raise SystemExit("Instale o rsvg-convert (librsvg) para renderizar a figura.")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [renderizador, "--width", "1890", "--height", "1260", "--output", str(SAIDA), str(FONTE)],
        check=True,
    )
    print(f"Figura gravada em {SAIDA}")


if __name__ == "__main__":
    main()
