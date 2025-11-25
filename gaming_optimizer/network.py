"""
Analyse réseau: ping, jitter, pertes, stabilité.
"""
from __future__ import annotations

import re
import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ping3 import ping

from .config import PING_TARGETS, PING_THRESHOLD
from .storage import StorageManager
from .utils import run_command


@dataclass
class NetworkResult:
    name: str
    host: str
    samples: List[float] = field(default_factory=list)
    packet_loss: float = 0.0
    jitter: float = 0.0
    attempts: int = 0
    timeouts: int = 0

    @property
    def average(self) -> float:
        return statistics.mean(self.samples) if self.samples else float("inf")

    @property
    def has_data(self) -> bool:
        return bool(self.samples)

    @property
    def stability_score(self) -> int:
        if self.average <= 30 and self.packet_loss < 0.5 and self.jitter < 3:
            return 5
        if self.average <= 45 and self.packet_loss < 1.0 and self.jitter < 6:
            return 4
        if self.average <= 60 and self.packet_loss < 2.0:
            return 3
        if self.average <= 90:
            return 2
        return 1

    @property
    def latency_display(self) -> str:
        return f"{self.average:.1f} ms" if self.has_data else "timeout"

    @property
    def jitter_display(self) -> str:
        return f"{self.jitter:.1f} ms" if self.has_data else "n/a"

    def as_dict(self) -> Dict[str, float]:
        return {
            "host": self.host,
            "avg": round(self.average, 2) if self.has_data else None,
            "loss": self.packet_loss,
            "jitter": self.jitter,
            "stability": self.stability_score,
        }


class NetworkAnalyzer:
    """Effectue les tests de latence et produit un rapport."""

    def __init__(
        self,
        targets: Dict[str, str] | None = None,
        storage: StorageManager | None = None,
    ) -> None:
        self.targets = targets or PING_TARGETS
        self.storage = storage or StorageManager()

    def run_tests(self, *, attempts: int = 5, delay: float = 0.2, timeout: float = 1.0) -> Dict[str, NetworkResult]:
        results: Dict[str, NetworkResult] = {}
        for name, host in self.targets.items():
            outcome = NetworkResult(name=name, host=host, attempts=attempts)
            dropped = 0
            for _ in range(attempts):
                latency = self._ping_host(host, timeout)
                if latency is None:
                    dropped += 1
                else:
                    outcome.samples.append(latency)
                time.sleep(delay)
            outcome.packet_loss = round((dropped / attempts) * 100, 2)
            outcome.timeouts = dropped
            outcome.jitter = round(statistics.pstdev(outcome.samples) if len(outcome.samples) > 1 else 0.0, 2)
            results[name] = outcome
        self.storage.append_network_report({k: v.as_dict() for k, v in results.items()})
        return results

    def _ping_host(self, host: str, timeout: float) -> Optional[float]:
        latency = ping(host, unit="ms", timeout=timeout)
        if latency is not None:
            return latency
        return self._ping_via_system(host, timeout)

    @staticmethod
    def _ping_via_system(host: str, timeout: float) -> Optional[float]:
        timeout_ms = max(int(timeout * 1000), 100)
        proc = run_command(["ping", "-n", "1", "-w", str(timeout_ms), host], check=False)
        if proc.returncode != 0:
            return None
        match = re.search(r"time[=<]\s*(\d+)\s*ms", proc.stdout)
        if match:
            return float(match.group(1))
        return None

    def format_report(self, results: Dict[str, NetworkResult]) -> str:
        lines = ["[ANALYSE RÉSEAU]"]
        for name, data in results.items():
            lines.append(
                f"{name:<20} Ping moyen: {data.latency_display} | "
                f"Pertes: {data.packet_loss:.1f}% | Jitter: {data.jitter_display} | "
                f"Stabilité: {'★'*data.stability_score}{'☆'*(5-data.stability_score)}"
            )
            if not data.has_data:
                lines.append(" " * 6 + "⚠ Serveur injoignable (timeout ICMP).")
            elif data.average > PING_THRESHOLD:
                lines.append(" " * 6 + "⚠ Latence élevée détectée, vérifiez votre connexion.")
        return "\n".join(lines)

