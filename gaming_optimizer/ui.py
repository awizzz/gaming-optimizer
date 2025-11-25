"""
Outils d'affichage pour le menu interactif et les sections stylisées.
"""
from __future__ import annotations

import os
from typing import Dict, Tuple

from colorama import Fore, Style, init

from .config import MENU_OPTIONS

init(autoreset=True)

LOGO = r"""
   ____                  _               ____        _ _
  / ___| _   _ _ __ ___ | |__   ___ _ __/ ___| _   _(_) |_ ___
  \___ \| | | | '_ ` _ \| '_ \ / _ \ '__\___ \| | | | | __/ _ \
   ___) | |_| | | | | | | |_) |  __/ |   ___) | |_| | | ||  __/
  |____/ \__,_|_| |_| |_|_.__/ \___|_|  |____/ \__,_|_|\__\___|
"""


class MenuUI:
    """Rend un menu coloré et gère les entrées utilisateur."""

    def __init__(self, options: Dict[str, Tuple[str, str]] | None = None) -> None:
        self.options = options or MENU_OPTIONS

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def render(self) -> None:
        self.clear()
        print(Fore.CYAN + LOGO + Style.RESET_ALL)
        print(Fore.MAGENTA + "  Optimisation réseau • système • GPU".center(60) + Style.RESET_ALL)
        print(Fore.WHITE + "  Choisissez une action (Q pour quitter):" + Style.RESET_ALL)
        for key, (_, label) in self.options.items():
            color = Fore.YELLOW if key.lower() != "q" else Fore.RED
            print(f"    {color}[{key.upper():>2}]{Style.RESET_ALL} {label}")
        print()

    def prompt(self) -> str:
        self.render()
        choice = input(Fore.GREEN + "Votre sélection > " + Style.RESET_ALL).strip().lower()
        return choice

    def pause(self) -> None:
        input(Fore.BLUE + "\nAppuyez sur Entrée pour revenir au menu..." + Style.RESET_ALL)

