"""
Optimisations GPU multi-vendeurs (NVIDIA / AMD / Intel).
"""
from __future__ import annotations

from pathlib import Path
from typing import List

try:
    import wmi  # type: ignore
except ImportError:
    wmi = None

from .utils import run_command


class GPUOptimizer:
    """Applique des réglages recommandés selon le GPU détecté."""

    def __init__(self) -> None:
        self.actions: List[str] = []

    def optimize(self) -> str:
        self.actions.clear()
        if self._has_nvidia():
            self._optimize_nvidia()
        if self._has_amd():
            self._optimize_amd()
        if self._has_intel():
            self._optimize_intel()
        if not self.actions:
            return "Aucun GPU compatible détecté"
        return " | ".join(self.actions)

    @staticmethod
    def _exists(path: str) -> bool:
        return Path(path).exists()

    def _has_nvidia(self) -> bool:
        return self._exists(r"C:\Windows\System32\nvapi64.dll")

    def _has_amd(self) -> bool:
        return self._exists(r"C:\Program Files\AMD\CNext\CNext\RadeonSoftware.exe")

    def _has_intel(self) -> bool:
        return self._exists(r"C:\Windows\System32\DriverStore\FileRepository\iigd_dch")

    def _optimize_nvidia(self) -> None:
        exe = r"C:\Program Files\NVIDIA Corporation\nvidia-smi.exe"
        if Path(exe).exists():
            run_command([exe, "-pm", "1"], check=False)
            run_command([exe, "-ac", "5000,1900"], check=False)
            self.actions.append("NVIDIA: mode performance maximale")
        else:
            self.actions.append("NVIDIA détecté (appliquer profil via GeForce Experience)")

    def _optimize_amd(self) -> None:
        script = (
            r'$profiles = Get-ItemProperty '
            r'-Path "HKLM:\SOFTWARE\AMD\CN" -ErrorAction SilentlyContinue; '
            r'if ($profiles) { Set-ItemProperty '
            r'-Path "HKLM:\SOFTWARE\AMD\CN" -Name "PP_PhmSoftPowerPlayTable" -Value 2 -ErrorAction SilentlyContinue }'
        )
        from .utils import powershell  # import local pour éviter cycle

        powershell(script, check=False)
        self.actions.append("AMD: Anti-Lag/Radeon Boost recommandés")

    def _optimize_intel(self) -> None:
        self.actions.append("Intel: activer le mode Performance globale via l'app Arc Control")

    def telemetry(self) -> str:
        if not wmi:
            return "WMI indisponible"
        try:
            computer = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temps = [
                s.Value
                for s in computer.Sensor()
                if s.SensorType == "Temperature" and "GPU" in s.Name
            ]
            if temps:
                return f"{temps[0]}°C"
        except Exception:
            return "Lecture capteurs impossible"
        return "N/A"

