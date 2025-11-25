"""
Interface CLI basée sur argparse + menu interactif.
"""
from __future__ import annotations

import argparse
import time

from .config import MENU_OPTIONS
from .main import GamingOptimizer
from .ui import MenuUI

try:
    from colorama import Fore, Style
except ImportError:  # fallback si colorama absent
    class _Fallback:
        RESET_ALL = ""

        def __getattr__(self, name: str) -> str:
            return ""

    Fore = Style = _Fallback()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gaming-optimizer",
        description="Optimiseur de performances gaming (Windows 10/11).",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("analyze", help="Analyse complète du réseau et du système.")

    optimize_parser = sub.add_parser("optimize", help="Appliquer toutes les optimisations.")
    optimize_parser.add_argument("-y", "--yes", action="store_true", help="Ne pas demander de confirmation.")

    sub.add_parser("network-test", help="Tests réseau approfondis.")
    sub.add_parser("restore", help="Restaurer les paramètres sauvegardés.")

    monitor = sub.add_parser("monitor", help="Monitoring temps réel.")
    monitor.add_argument("--interval", type=float, default=2.0, help="Intervalle entre les mesures (s).")

    return parser


def interactive_menu(opt: GamingOptimizer) -> None:
    ui = MenuUI(MENU_OPTIONS)
    while True:
        choice = ui.prompt()
        command, _ = MENU_OPTIONS.get(choice, (None, None))
        if command is None:
            print(Fore.RED + "Sélection invalide. Merci de réessayer." + Style.RESET_ALL)
            time.sleep(1.2)
            continue
        if command == "quit":
            print(Fore.CYAN + "À bientôt et bon jeu !" + Style.RESET_ALL)
            break
        args = argparse.Namespace(command=command, yes=False, interval=2.0)
        dispatch_command(opt, args)
        ui.pause()


def dispatch_command(opt: GamingOptimizer, args: argparse.Namespace) -> None:
    if args.command == "analyze":
        opt.analyze()
    elif args.command == "optimize":
        opt.optimize(force=args.yes)
    elif args.command == "network-test":
        opt.network_test()
    elif args.command == "restore":
        opt.restore()
    elif args.command == "monitor":
        opt.monitor(interval=getattr(args, "interval", 2.0))
    else:
        raise SystemExit(1)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    optimizer = GamingOptimizer()
    if not args.command:
        interactive_menu(optimizer)
        return
    dispatch_command(optimizer, args)


if __name__ == "__main__":
    main()

