#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MT5 Trading Analyzer - Application d'analyse de trading pour MetaTrader 5
Point d'entrée principal de l'application
"""

import sys
import tkinter as tk
import logging
from pathlib import Path
from ui.main_window import MainWindow

# Configuration du logging
def setup_logging():
    """Configure le système de logging pour l'application"""
    log_dir = Path.home() / ".mt5_analyzer" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "mt5_analyzer.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Fonction principale de démarrage de l'application"""
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Démarrage de l'application MT5 Trading Analyzer")
    
    # Création de la fenêtre principale Tkinter
    root = tk.Tk()
    app = MainWindow(root)
    
    # Lancement de la boucle principale
    logger.info("Application prête, démarrage de la boucle principale")
    root.mainloop()
    
    logger.info("Fermeture de l'application")

if __name__ == "__main__":
    main()