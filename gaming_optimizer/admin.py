"""
Gestion des privilèges administrateur.
"""
import ctypes

from .utils import ensure_windows


class AdminManager:
    """Vérifie les privilèges et relance si besoin."""

    @staticmethod
    def ensure_admin() -> None:
        ensure_windows()
        if ctypes.windll.shell32.IsUserAnAdmin():
            return
        raise PermissionError(
            "Privilèges administrateur requis. Relancez le programme en tant qu'administrateur."
        )

