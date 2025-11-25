# Gaming Optimizer CLI

Outil en ligne de commande pour Windows 10/11 qui mesure et optimise automatiquement la latence réseau, la stabilité système et les performances GPU pour les jeux compétitifs. Il peut être empaqueté en exécutable (`pyinstaller --onefile gaming_optimizer/cli.py`) ou utilisé tel quel en Python 3.8+.

## Fonctionnalités clés
- **Analyse réseau** : ping multi-serveurs (Valorant, CS2, Fortnite, LoL), jitter, pertes, score de stabilité, export JSON.
- **Optimisations système** : réglages `netsh` (TCP/IP), plan d’énergie Performance Max, services Windows non critiques désactivés, DNS Cloudflare (1.1.1.1), mode Jeu Windows + désactivation DVR, priorité CPU sur les processus de jeux populaires.
- **Optimisations GPU** : détection NVIDIA/AMD/Intel, ajustements rapides via `nvidia-smi`, recommandations AMD/Intel, monitoring température via WMI/OpenHardwareMonitor.
- **Backups & restauration** : instantané automatique AVANT chaque changement (`storage/system_backup.json`) et commande `restore` pour revenir à l’état initial.
- **Monitoring temps réel** : suivi du ping vers 1.1.1.1, CPU/RAM et capteurs GPU.
- **Rapports** : chaque analyse/optimisation produit un rapport texte horodaté dans `reports/` + journal JSON dans `reports/network_reports.json`.

## Prérequis
- Windows 10/11 (64 bits) avec droits administrateur.
- Python 3.8+ installé (ou exécutable PyInstaller).
- Modules Python : `psutil`, `ping3`, `wmi` (voir `requirements.txt`).
- `OpenHardwareMonitor` facultatif pour les capteurs GPU via WMI.

## Installation rapide
```bash
cd gaming_optimizer
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Commandes disponibles
```bash
python -m gaming_optimizer --help          # aide détaillée
python -m gaming_optimizer                 # menu interactif (sans sous-commande)
python -m gaming_optimizer analyze         # analyse réseau + benchmark
python -m gaming_optimizer optimize --yes  # applique toutes les optimisations
python -m gaming_optimizer network-test    # tests réseau approfondis (10 pings)
python -m gaming_optimizer monitor --interval 5
python -m gaming_optimizer restore         # restaure les paramètres sauvegardés
```

## Workflow recommandé
1. **Analyse initiale** : `python -m gaming_optimizer analyze` (sauvegarde des métriques de référence).
2. **Optimisation** : `python -m gaming_optimizer optimize` (répondre `o` ou utiliser `--yes`).
3. **Vérification** : `python -m gaming_optimizer network-test` puis `monitor` pour surveiller la stabilité.
4. **Restauration** (si besoin) : `python -m gaming_optimizer restore`.

Chaque étape génère un rapport (fichier `.txt`) disponible dans `reports/` pour comparer avant/après.

## Structure des fichiers importants
- `gaming_optimizer/`: code Python modulaire (network, system, gpu, monitor, reporter…).
- `storage/system_backup.json`: sauvegarde cumulée des paramètres d’origine.
- `reports/*.txt`: rapports lisibles générés par `analyze` et `optimize`.
- `reports/network_reports.json`: historique des résultats de ping.

## Compilation en .exe (Windows)
```bash
pyinstaller --onefile gaming_optimizer/cli.py -n gaming-optimizer
```
L’exécutable se lancera avec les mêmes sous-commandes (`gaming-optimizer analyze`, etc.). Vérifiez que `ping3`, `psutil` et `wmi` sont inclus par PyInstaller (hook automatique par défaut).

## Sécurité & bonnes pratiques
- Le script bloque l’exécution si les privilèges administrateur ne sont pas présents.
- Toute opération potentiellement intrusive sauvegarde un instantané avant d’écrire.
- Certains réglages (notamment `netsh`) nécessitent une restauration manuelle complète ; le rapport indique toujours la commande à rejouer en sens inverse.

## Support & contributions
1. Forker le dépôt GitHub.
2. Installer les dépendances (section “Installation rapide”).
3. Créer une branche: `git checkout -b feature/ma-feature`.
4. Lancer les tests manuels (`analyze`, `optimize`, etc.) sur une machine Windows.
5. Soumettre une Pull Request en décrivant les optimisations/testes réalisés.

Bon jeu et faibles latences ! 🎮

