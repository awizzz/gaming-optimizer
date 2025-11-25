"""
Coordination principale de l'outil Gaming Optimizer.
"""
from __future__ import annotations

import statistics
import time
from typing import Dict, List, Optional

from .admin import AdminManager
from .gpu import GPUOptimizer
from .monitor import RealTimeMonitor
from .network import NetworkAnalyzer, NetworkResult
from .reporter import Reporter
from .storage import StorageManager
from .system import SystemOptimizer


class GamingOptimizer:
    """API de haut niveau consommée par la CLI."""

    def __init__(self) -> None:
        self.storage = StorageManager()
        self.network = NetworkAnalyzer(storage=self.storage)
        self.system = SystemOptimizer(storage=self.storage)
        self.gpu = GPUOptimizer()
        self.reporter = Reporter()

    # ---------- Helpers ----------
    def _synthetic_benchmark(self, iterations: int = 2_000_000) -> float:
        """Retourne une estimation d'un score FPS relatif."""
        start = time.perf_counter()
        acc = 0
        for i in range(iterations):
            acc += (i * 3) % 7
        duration = time.perf_counter() - start
        # Valeur arbitraire convertie en pseudo FPS
        fps_estimate = (iterations / duration) / 50_000
        return round(fps_estimate, 2)

    def collect_performance_metrics(self, network_results: Optional[Dict[str, NetworkResult]] = None) -> Dict[str, float]:
        fps_score = self._synthetic_benchmark()
        if network_results:
            valid_latencies = [res.average for res in network_results.values() if res.has_data]
            latency = statistics.mean(valid_latencies) if valid_latencies else 0.0
        else:
            latency = 0.0
        return {"fps": fps_score, "latency": latency}

    # ---------- Commandes ----------
    def analyze(self) -> None:
        AdminManager.ensure_admin()
        results = self.network.run_tests()
        perf = self.collect_performance_metrics(results)
        self.storage.snapshot("analysis_last", {"network": {k: v.as_dict() for k, v in results.items()}, "perf": perf})
        self.storage.snapshot("performance_before", perf)
        report_text = "\n\n".join(
            [
                self.reporter.build_network_section(results),
                self.reporter.build_performance_section(None, perf),
            ]
        )
        path = self.storage.export_report_text("analysis", report_text)
        print(report_text)
        print(f"\nRapport sauvegardé: {path}")

    def optimize(self, *, force: bool = False) -> None:
        AdminManager.ensure_admin()
        if not force:
            confirmation = input("Appliquer les optimisations système ? (o/N) ").strip().lower()
            if confirmation not in {"o", "oui", "y", "yes"}:
                print("Optimisation annulée.")
                return
        actions: List[str] = []
        for func in [
            self.system.optimize_tcp,
            self.system.optimize_power_plan,
            self.system.disable_background_services,
            self.system.optimize_dns,
            self.system.optimize_windows_gaming,
            self.system.prioritize_game_processes,
        ]:
            try:
                actions.append(func())
            except Exception as exc:  # capture pour continuer les autres étapes
                actions.append(f"{func.__name__}: échec ({exc})")
        gpu_message = self.gpu.optimize()
        actions.append(gpu_message)
        results = self.network.run_tests()
        before = self.storage.get_snapshot("performance_before")
        after = self.collect_performance_metrics(results)
        self.storage.snapshot("performance_after", after)
        report_text = "\n\n".join(
            [
                self.reporter.build_system_section(actions),
                self.reporter.build_network_section(results),
                self.reporter.build_performance_section(before, after),
            ]
        )
        path = self.storage.export_report_text("optimize", report_text)
        print(report_text)
        print(f"\nRapport sauvegardé: {path}")

    def network_test(self) -> None:
        AdminManager.ensure_admin()
        results = self.network.run_tests(attempts=10)
        print(self.reporter.build_network_section(results))

    def restore(self) -> None:
        AdminManager.ensure_admin()
        messages = [
            self.system.restore_power_plan(),
            self.system.restore_tcp(),
            self.system.restore_windows_gaming(),
        ]
        print("[RESTAURATION]")
        for message in messages:
            print(f" - {message}")

    def monitor(self, interval: float = 2.0) -> None:
        AdminManager.ensure_admin()
        RealTimeMonitor(self.gpu).run(interval=interval)

