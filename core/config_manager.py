#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de configuration pour l'application MT5 Trading Analyzer
Gère le chargement, la sauvegarde et l'accès aux paramètres de configuration
"""

import json
import logging
from pathlib import Path

class ConfigManager:
    """Classe de gestion de la configuration de l'application"""
    
    # Valeurs par défaut
    DEFAULT_CONFIG = {
        "alert_thresholds": {
            "margin_pct": 50,        # Alerte si la marge utilisée dépasse 50%
            "daily_loss": -5,        # Alerte si perte journalière > 5%
            "drawdown": -15,         # Alerte si drawdown > 15%
            "d_leverage": 16.25,     # Alerte si D-Leverage > 16.25
            "var_monthly": 12,       # Alerte si VaR mensuelle > 12%
            "correlation": 0.8,      # Alerte si corrélation > 0.8
            "sector_concentration": 30 # Alerte si concentration sectorielle > 30%
        },
        "ui_settings": {
            "theme": "default",
            "chart_style": "default",
            "language": "fr",
            "show_welcome": True
        },
        "email_notifications": {
            "enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "recipient": ""
        },
        "data_refresh": {
            "auto_refresh": True,
            "refresh_interval": 60,  # en secondes
            "history_days": 90
        }
    }
    
    def __init__(self):
        """Initialisation du gestionnaire de configuration"""
        self.logger = logging.getLogger(__name__)
        self.config_dir = Path.home() / ".mt5_analyzer"
        self.config_file = self.config_dir / "config.json"
        self.config = None
        
        # Créer le répertoire de configuration s'il n'existe pas
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger la configuration
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis le fichier"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.logger.info("Configuration chargée depuis %s", self.config_file)
            else:
                self.logger.info("Fichier de configuration non trouvé, utilisation des valeurs par défaut")
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
        except Exception as e:
            self.logger.exception("Erreur lors du chargement de la configuration")
            self.config = self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Enregistre la configuration dans le fichier"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration enregistrée dans %s", self.config_file)
            return True
        except Exception as e:
            self.logger.exception("Erreur lors de l'enregistrement de la configuration")
            return False
    
    def get_alert_thresholds(self):
        """Récupère les seuils d'alerte"""
        return self.config["alert_thresholds"]
    
    def set_alert_thresholds(self, thresholds):
        """Définit les seuils d'alerte"""
        self.config["alert_thresholds"] = thresholds
        self.save_config()
    
    def get_ui_settings(self):
        """Récupère les paramètres d'interface utilisateur"""
        return self.config["ui_settings"]
    
    def set_ui_settings(self, settings):
        """Définit les paramètres d'interface utilisateur"""
        self.config["ui_settings"] = settings
        self.save_config()
    
    def get_email_settings(self):
        """Récupère les paramètres de notification par email"""
        return self.config["email_notifications"]
    
    def set_email_settings(self, settings):
        """Définit les paramètres de notification par email"""
        self.config["email_notifications"] = settings
        self.save_config()
    
    def get_data_refresh_settings(self):
        """Récupère les paramètres de rafraîchissement des données"""
        return self.config["data_refresh"]
    
    def set_data_refresh_settings(self, settings):
        """Définit les paramètres de rafraîchissement des données"""
        self.config["data_refresh"] = settings
        self.save_config()
    
    def get(self, section, key=None, default=None):
        """
        Récupère une valeur de configuration
        
        Args:
            section (str): Section de configuration
            key (str, optional): Clé spécifique dans la section. Si None, retourne toute la section.
            default: Valeur par défaut à retourner si la clé n'est pas trouvée
            
        Returns:
            La valeur de configuration ou la valeur par défaut
        """
        try:
            if section in self.config:
                if key is not None:
                    return self.config[section].get(key, default)
                return self.config[section]
            return default
        except:
            return default
    
    def set(self, section, key, value):
        """
        Définit une valeur de configuration
        
        Args:
            section (str): Section de configuration
            key (str): Clé à définir
            value: Valeur à enregistrer
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            return self.save_config()
        except:
            return False