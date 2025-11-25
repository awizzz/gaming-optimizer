"""
Analyse réseau: ping, jitter, pertes, stabilité.
"""
from __future__ import annotations

import statistics
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from ping3 import ping

from .config import PING_TARGETS, PING_THRESHOLD
from .storage import StorageManager


@dataclass
class NetworkResult:
    name: str
    host: str
    samples: List[float] = field(default_factory=list)
    packet_loss: float = 0.0
    jitter: float = 0.0

    @property
    def average(self) -> float:
        return statistics.mean(self.samples) if self.samples else float("inf")

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

    def as_dict(self) -> Dict[str, float]:
        return {
            "host": self.host,
            "avg": round(self.average, 2),
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
            outcome = NetworkResult(name=name, host=host)
            dropped = 0
            for _ in range(attempts):
                latency = ping(host, unit="ms", timeout=timeout)
                if latency is None:
                    dropped += 1
                else:
                    outcome.samples.append(latency)
                time.sleep(delay)
            outcome.packet_loss = round((dropped / attempts) * 100, 2)
            outcome.jitter = round(statistics.pstdev(outcome.samples) if len(outcome.samples) > 1 else 0.0, 2)
            results[name] = outcome
        self.storage.append_network_report({k: v.as_dict() for k, v in results.items()})
        return results

    def format_report(self, results: Dict[str, NetworkResult]) -> str:
        lines = ["[ANALYSE RÉSEAU]"]
        for name, data in results.items():
            lines.append(
                f"{name:<20} Ping moyen: {data.average:.1f} ms | "
                f"Pertes: {data.packet_loss:.1f}% | Jitter: {data.jitter:.1f} ms | "
                f"Stabilité: {'★'*data.stability_score}{'☆'*(5-data.stability_score)}"
            )
            if data.average > PING_THRESHOLD:
                lines.append(" " * 6 + "⚠ Latence élevée détectée, vérifiez votre connexion.")
        return "\n".join(lines)

