#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Constantes pour l'application MT5 Trading Analyzer
"""

# Informations sur l'application
APP_NAME = "MT5 Analyste de Trading Pro"
APP_VERSION = "1.0.0"
APP_AUTHOR = "© 2025"

# Valeurs par défaut
DEFAULT_WINDOW_SIZE = "1280x900"
MIN_WINDOW_SIZE = (1024, 768)

# Couleurs
COLORS = {
    "primary": "#1a73e8",
    "secondary": "#5f6368",
    "success": "#0f9d58",
    "warning": "#f4b400",
    "error": "#d93025",
    "background": "#f8f9fa",
    "text": "#202124",
    "light_text": "#5f6368",
    "border": "#dadce0",
    "chart_blue": "#4285f4",
    "chart_red": "#ea4335",
    "chart_green": "#34a853",
    "chart_yellow": "#fbbc04",
    "profit_green": "#0f9d58",
    "loss_red": "#d93025"
}

# Styles de graphique
CHART_STYLES = {
    "default": {
        "background_color": "#ffffff",
        "grid_color": "#f0f0f0",
        "text_color": "#202124",
        "line_color": "#4285f4",
        "fill_color": "#e8f0fe"
    },
    "dark": {
        "background_color": "#202124",
        "grid_color": "#3c4043",
        "text_color": "#e8eaed",
        "line_color": "#8ab4f8",
        "fill_color": "#3c4043"
    }
}

# Périodes pour les graphiques
CHART_PERIODS = {
    "1m": "1 mois",
    "3m": "3 mois",
    "6m": "6 mois",
    "1a": "1 an",
    "2a": "2 ans",
    "5a": "5 ans"
}

# Mapping des périodes en jours
PERIOD_DAYS = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1a": 365,
    "2a": 730,
    "5a": 1825
}

# Symbols pour le benchmarking
BENCHMARK_SYMBOLS = {
    "SPX": "^GSPC",
    "NDX": "^NDX",
    "DJI": "^DJI", 
    "RUT": "^RUT",
    "VIX": "^VIX",
    "EURUSD": "EURUSD=X"
}

# Types de rafraîchissement
REFRESH_INTERVALS = {
    "30s": 30,
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600
}

# Ajoutez ce bloc aux constantes existantes du fichier utils/constants.py

# Catégories de trading basées sur la durée
TRADING_CATEGORIES = {
    "Scalping": {
        "sous-optimal": 10.0,
        "optimal_max": 16.25
    },
    "Intraday": {
        "sous-optimal": 8.0,
        "optimal_max": 13.0
    },
    "Swing": {
        "sous-optimal": 5.0,
        "optimal_max": 9.75
    }
}

# Messages d'erreur
ERROR_MESSAGES = {
    "not_connected": "Non connecté à MT5. Veuillez vous connecter d'abord.",
    "no_data": "Aucune donnée disponible.",
    "no_positions": "Aucune position ouverte.",
    "no_history": "Aucun historique disponible.",
    "invalid_config": "Configuration invalide.",
    "export_failed": "Échec de l'exportation."
}

# Messages d'état
STATUS_MESSAGES = {
    "connecting": "Connexion à MT5 en cours...",
    "connected": "Connecté à MT5",
    "disconnected": "Déconnecté de MT5",
    "refreshing": "Rafraîchissement des données en cours...",
    "refreshed": "Données rafraîchies",
    "error": "Erreur"
}