"""
Gestion des sauvegardes et rapports.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

from .config import BACKUP_FILE, NETWORK_LOG, REPORT_DIR
from .utils import load_json, save_json


class StorageManager:
    """Centralise la persistence des données."""

    def __init__(self, backup_path: Path = BACKUP_FILE) -> None:
        self.backup_path = backup_path
        self.data = load_json(backup_path)

    def snapshot(self, key: str, payload: Dict[str, Any]) -> None:
        self.data.setdefault("snapshots", {})
        self.data["snapshots"][key] = payload
        save_json(self.backup_path, self.data)

    def get_snapshot(self, key: str) -> Dict[str, Any]:
        return self.data.get("snapshots", {}).get(key, {})

    def append_network_report(self, report: Dict[str, Any]) -> None:
        payload = load_json(NETWORK_LOG)
        payload.setdefault("reports", [])
        payload["reports"].append(
            {
                "timestamp": dt.datetime.utcnow().isoformat(),
                **report,
            }
        )
        save_json(NETWORK_LOG, payload)

    def export_report_text(self, name: str, content: str) -> Path:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = REPORT_DIR / f"{name}_{dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
        path.write_text(content, encoding="utf-8")
        return path

