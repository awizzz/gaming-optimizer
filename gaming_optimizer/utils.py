"""
Fonctions utilitaires partagées.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional


class CommandError(RuntimeError):
    """Exception levée lorsqu'une commande système échoue."""


def ensure_windows() -> None:
    """Valide que le script est exécuté sur Windows 10/11."""
    if os.name != "nt" or platform.system().lower() != "windows":
        raise EnvironmentError("Cet outil fonctionne uniquement sous Windows 10/11.")


def run_command(cmd: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess:
    """
    Exécute une commande système en capturant stdout/stderr.

    Args:
        cmd: commande à exécuter
        check: lève CommandError si le retour est non nul
    """
    process = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        shell=False,
    )
    if check and process.returncode != 0:
        raise CommandError(f"Commande {' '.join(cmd)} échouée: {process.stderr.strip()}")
    return process


def powershell(script: str, *, check: bool = True) -> subprocess.CompletedProcess:
    """Raccourci pour exécuter des commandes PowerShell."""
    return run_command(["powershell", "-NoProfile", "-Command", script], check=check)


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

