"""
Génération de rapports lisibles pour l'utilisateur.
"""
from __future__ import annotations

from typing import Dict, List

from .network import NetworkResult


class Reporter:
    """Assemble les métriques en sections formatées."""

    def build_network_section(self, results: Dict[str, NetworkResult]) -> str:
        lines = ["[ANALYSE RÉSEAU]"]
        for name, res in results.items():
            lines.append(
                f"{name:<20} Ping: {res.latency_display} | "
                f"Pertes: {res.packet_loss:.1f}% | Jitter: {res.jitter_display} | "
                f"Stabilité: {'★'*res.stability_score}{'☆'*(5-res.stability_score)}"
            )
            if not res.has_data:
                lines.append(" " * 6 + "⚠ Aucun paquet reçu (serveur peut filtrer l'ICMP).")
        return "\n".join(lines)

    def build_system_section(self, actions: List[str]) -> str:
        lines = ["[OPTIMISATIONS SYSTÈME]"]
        lines.extend(f" - {action}" for action in actions)
        return "\n".join(lines)

    def build_performance_section(self, before: Dict[str, float] | None, after: Dict[str, float]) -> str:
        lines = ["[GAINS PERFORMANCE]"]
        if before and "fps" in before and "fps" in after:
            delta = after["fps"] - before["fps"]
            pct = (delta / before["fps"]) * 100 if before["fps"] else 0
            lines.append(f"FPS moyens: {before['fps']:.0f} → {after['fps']:.0f} ({pct:+.1f}%)")
        if (
            before
            and "latency" in before
            and "latency" in after
            and before["latency"] > 0
            and after["latency"] > 0
        ):
            delta = after["latency"] - before["latency"]
            pct = (delta / before["latency"]) * 100
            lines.append(f"Latence: {before['latency']:.0f}ms → {after['latency']:.0f}ms ({pct:+.1f}%)")
        if len(lines) == 1:
            lines.append("Collectez des métriques avant/après pour voir les gains.")
        return "\n".join(lines)

