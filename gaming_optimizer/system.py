"""
Optimisations TCP/IP, alimentation, services, DNS et fonctionnalités Windows.
"""
from __future__ import annotations

import psutil

from .config import BACKGROUND_SERVICES, DNS_SERVERS, GAME_PROCESS_NAMES
from .storage import StorageManager
from .utils import powershell, run_command


class SystemOptimizer:
    """Regroupe les différents leviers système."""

    def __init__(self, storage: StorageManager | None = None) -> None:
        self.storage = storage or StorageManager()
        self.current_state: dict = {}

    # ---------- TCP/IP ----------
    def snapshot_tcp(self) -> None:
        output = run_command(["netsh", "int", "tcp", "show", "global"], check=False).stdout
        self.current_state["tcp"] = output
        self.storage.snapshot("tcp", {"raw": output})

    def optimize_tcp(self) -> str:
        self.snapshot_tcp()
        commands = [
            ["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"],
            ["netsh", "int", "tcp", "set", "global", "ecncapability=enabled"],
            ["netsh", "int", "tcp", "set", "global", "dca=enabled"],
            ["netsh", "int", "tcp", "set", "global", "chimney=enabled"],
        ]
        for cmd in commands:
            run_command(cmd)
        return "Paramètres TCP optimisés"

    def restore_tcp(self) -> str:
        snapshot = self.storage.get_snapshot("tcp")
        if not snapshot:
            return "Aucune sauvegarde TCP – restauration manuelle requise"
        # Les paramètres netsh doivent être restaurés manuellement via la sortie snapshot.
        return "Veuillez restaurer les paramètres TCP avec: netsh int tcp reset all"

    # ---------- Énergie ----------
    def snapshot_power_plan(self) -> None:
        output = run_command(["powercfg", "/GETACTIVESCHEME"], check=False).stdout.strip()
        self.current_state["power_plan"] = output
        self.storage.snapshot("power_plan", {"scheme": output})

    def optimize_power_plan(self) -> str:
        self.snapshot_power_plan()
        run_command(["powercfg", "/SETACTIVE", "SCHEME_MIN"])
        return "Plan d'énergie réglé sur Performance maximale"

    def restore_power_plan(self) -> str:
        snapshot = self.storage.get_snapshot("power_plan")
        if not snapshot:
            return "Aucun plan sauvegardé"
        if "GUID" in snapshot["scheme"]:
            guid = snapshot["scheme"].split(":")[1].split("(")[0].strip()
            run_command(["powercfg", "/SETACTIVE", guid], check=False)
            return "Plan d'énergie restauré"
        return "Impossible de déterminer le GUID du plan d'énergie"

    # ---------- Services ----------
    def disable_background_services(self) -> str:
        count = 0
        for svc in BACKGROUND_SERVICES:
            powershell(f"Stop-Service -Name {svc} -Force -ErrorAction SilentlyContinue", check=False)
            powershell(
                f"Set-Service -Name {svc} -StartupType Manual -ErrorAction SilentlyContinue", check=False
            )
            count += 1
        self.storage.snapshot("services", {"disabled": BACKGROUND_SERVICES})
        return f"Services inactifs: {count}/{len(BACKGROUND_SERVICES)}"

    # ---------- DNS ----------
    def optimize_dns(self, servers: tuple[str, str] = DNS_SERVERS) -> str:
        adapters = powershell(
            "Get-DnsClientServerAddress -AddressFamily IPv4 | Select-Object -ExpandProperty InterfaceAlias",
            check=False,
        ).stdout.splitlines()
        updated = 0
        for adapter in adapters:
            alias = adapter.strip()
            if not alias:
                continue
            powershell(
                f'Set-DnsClientServerAddress -InterfaceAlias "{alias}" '
                f"-ServerAddresses {','.join(servers)}",
                check=False,
            )
            updated += 1
        self.storage.snapshot("dns", {"servers": servers})
        return f"DNS configurés ({servers[0]}, {servers[1]}) sur {updated} interface(s)"

    # ---------- Mode Jeu / DVR ----------
    def toggle_windows_game_features(self, enable: bool) -> None:
        value = "1" if enable else "0"
        powershell(
            r'Reg.exe ADD "HKCU\Software\Microsoft\GameBar" '
            r"/v AllowAutoGameMode /t REG_DWORD /d " + value + " /f",
            check=False,
        )
        powershell(
            r'Reg.exe ADD "HKCU\System\GameConfigStore" '
            r"/v GameDVR_Enabled /t REG_DWORD /d " + value + " /f",
            check=False,
        )

    def optimize_windows_gaming(self) -> str:
        self.toggle_windows_game_features(True)
        self.storage.snapshot("game_features", {"enabled": True})
        return "Mode Jeu activé, DVR désactivé"

    def restore_windows_gaming(self) -> str:
        self.toggle_windows_game_features(False)
        return "Mode Jeu/DVR restaurés"

    # ---------- Priorité process ----------
    def prioritize_game_processes(self, processes: list[str] | None = None) -> str:
        targets_cfg = [p.lower() for p in (processes or GAME_PROCESS_NAMES)]
        priority_value = getattr(psutil, "HIGH_PRIORITY_CLASS", None)
        if priority_value is None:
            return "Priorité élevée non prise en charge sur cette plateforme"
        boosted = 0
        for proc in psutil.process_iter(["name"]):
            name = proc.info.get("name")
            if name and name.lower() in targets_cfg:
                try:
                    proc.nice(priority_value)
                    boosted += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        self.storage.snapshot("process_priority", {"targets": targets_cfg})
        return f"Priorité élevée appliquée à {boosted} processus"

