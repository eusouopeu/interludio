"""Alias compatível: a Figura 3.1 agora apresenta tipos N1–N6 sem hierarquia."""
from pathlib import Path
from runpy import run_path


if __name__ == "__main__":
    nova_figura = Path(__file__).with_name("figura_3-1_tipos_evidencia.py")
    run_path(str(nova_figura), run_name="__main__")
