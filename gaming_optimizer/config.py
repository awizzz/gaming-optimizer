"""
Configuration globale et constantes de l'application.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
REPORT_DIR = BASE_DIR.parent / "reports"
LOG_DIR = BASE_DIR.parent / "logs"
STORAGE_DIR = BASE_DIR.parent / "storage"
BACKUP_FILE = STORAGE_DIR / "system_backup.json"
NETWORK_LOG = REPORT_DIR / "network_reports.json"

PING_TARGETS = {
    "Valorant EU": "185.40.64.1",
    "Valorant NA": "192.207.0.1",
    "CS2 EU West": "146.66.152.12",
    "Fortnite NA": "199.255.40.175",
    "League EUW": "104.160.141.3",
}

BACKGROUND_SERVICES = [
    "DiagTrack",
    "SysMain",
    "WSearch",
    "RetailDemo",
    "XboxGipSvc",
    "XblAuthManager",
    "XblGameSave",
    "XboxNetApiSvc",
]

GAME_PROCESS_NAMES = [
    "cs2.exe",
    "valorant.exe",
    "fortniteclient-win64-shipping.exe",
    "leagueclientux.exe",
]

DNS_SERVERS = ("1.1.1.1", "1.0.0.1")

# Durée (ms) pour considérer qu'un ping est critique
PING_THRESHOLD = 60.0

MENU_OPTIONS = {
    "1": ("analyze", "Analyse complète du système"),
    "2": ("optimize", "Appliquer les optimisations"),
    "3": ("network-test", "Tests réseau détaillés"),
    "4": ("monitor", "Monitoring temps réel"),
    "5": ("restore", "Restaurer les paramètres"),
    "q": ("quit", "Quitter"),
}

