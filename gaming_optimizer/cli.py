"""
Interface CLI basée sur argparse + menu interactif.
"""
from __future__ import annotations

import argparse
import sys

from .config import MENU_OPTIONS
from .main import GamingOptimizer


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
    print("=== Gaming Optimizer ===")
    for key, (_, label) in MENU_OPTIONS.items():
        print(f"[{key}] {label}")
    choice = input("Choisissez une option: ").strip().lower()
    command, _ = MENU_OPTIONS.get(choice, (None, None))
    if command is None or command == "quit":
        print("À bientôt.")
        return
    dispatch_command(opt, argparse.Namespace(command=command, yes=False, interval=2.0))


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

