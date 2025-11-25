"""
Monitoring temps réel: ping + ressources système.
"""
from __future__ import annotations

import time
from typing import Optional

import psutil
from ping3 import ping

from .gpu import GPUOptimizer


class RealTimeMonitor:
    """Affiche en continu les métriques principales."""

    def __init__(self, gpu: Optional[GPUOptimizer] = None) -> None:
        self.gpu = gpu or GPUOptimizer()

    def run(self, interval: float = 2.0) -> None:
        print("[MONITORING TEMPS RÉEL] Ctrl+C pour quitter.")
        try:
            while True:
                latency = ping("1.1.1.1", unit="ms", timeout=1.0)
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                gpu_temp = self.gpu.telemetry()
                print(
                    f"Ping 1.1.1.1: {latency if latency else 'timeout'} ms | "
                    f"CPU: {cpu:.1f}% | RAM: {mem:.1f}% | GPU: {gpu_temp}"
                )
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring interrompu.")

