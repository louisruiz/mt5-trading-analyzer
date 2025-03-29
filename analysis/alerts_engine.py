#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur d'alertes pour MT5 Trading Analyzer
"""

import logging
from datetime import datetime
import pandas as pd
import numpy as np
from utils.constants import TRADING_CATEGORIES

class AlertsEngine:
    """Classe pour la génération et la gestion des alertes"""
    
    def __init__(self, data_manager, config_manager):
        """
        Initialisation du moteur d'alertes
        
        Args:
            data_manager: Instance du gestionnaire de données
            config_manager: Instance du gestionnaire de configuration
        """
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.alerts = []
        self.optimizations = []
        
        # Charger les seuils d'alerte
        self.load_thresholds()
    
    def load_thresholds(self):
        """Charge les seuils d'alerte depuis la configuration"""
        try:
            self.alert_thresholds = self.config_manager.get_alert_thresholds()
        except Exception as e:
            self.logger.exception("Erreur lors du chargement des seuils d'alerte")
            # Valeurs par défaut en cas d'erreur
            self.alert_thresholds = {
                'margin_pct': 50,
                'daily_loss': -5,
                'drawdown': -15,
                'd_leverage': 16.25,
                'var_monthly': 12,
                'correlation': 0.8,
                'sector_concentration': 30
            }
    
    def check_alerts(self):
        """
        Vérifie toutes les conditions d'alerte et génère les alertes appropriées
        
        Returns:
            tuple: (Nouvelles alertes, Nouvelles suggestions d'optimisation)
        """
        if not self.data_manager.connected:
            return [], []
        
        # Réinitialiser les listes d'alertes et d'optimisations
        new_alerts = []
        new_optimizations = []
        
        try:
            # Récupérer les données nécessaires
            account_info = self.data_manager.account_info
            positions = self.data_manager.positions
            equity_data = self.data_manager.equity_data
            
            if not account_info:
                return [], []
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Vérifier le niveau de marge
            margin_pct = self.data_manager.get_current_margin_percentage()
            if margin_pct > self.alert_thresholds['margin_pct']:
                alert = self.create_alert(current_time, "RISQUE", "Niveau de marge élevé", f"{margin_pct:.1f}%")
                new_alerts.append(alert)
                
                optimization = self.create_optimization("RÉDUCTION DE MARGE", 
                    f"Le niveau de marge actuel ({margin_pct:.1f}%) dépasse le seuil recommandé de {self.alert_thresholds['margin_pct']}%. "
                    f"Envisagez de réduire les positions ou d'augmenter votre capital pour améliorer votre sécurité de trading.")
                new_optimizations.append(optimization)
            
            # Vérifier le D-Leverage
            d_leverage = self.data_manager.calculate_d_leverage()
            if d_leverage > self.alert_thresholds['d_leverage']:
                alert = self.create_alert(current_time, "RISQUE", "D-Leverage élevé", f"{d_leverage:.2f}")
                new_alerts.append(alert)
                
                # Déterminer le D-Leverage cible selon la durée moyenne des positions
                avg_duration = self.data_manager.get_average_position_duration()
                
                if avg_duration < 30:  # Scalping
                    target_d_leverage = TRADING_CATEGORIES["Scalping"]["max_d_leverage"]
                    category = "Scalping (<30min)"
                elif avg_duration < 60:  # Intraday
                    target_d_leverage = TRADING_CATEGORIES["Intraday"]["max_d_leverage"]
                    category = "Intraday (30-60min)"
                else:  # Swing
                    target_d_leverage = TRADING_CATEGORIES["Swing"]["max_d_leverage"]
                    category = "Swing (>60min)"
                
                if d_leverage > target_d_leverage:
                    reduction_needed = (d_leverage - target_d_leverage) / d_leverage * 100
                    optimization = self.create_optimization("OPTIMISATION D-LEVERAGE", 
                        f"Votre D-Leverage actuel ({d_leverage:.2f}) dépasse le seuil recommandé de {target_d_leverage} "
                        f"pour la durée moyenne de vos positions ({avg_duration:.0f} min - {category}). "
                        f"Une réduction d'environ {reduction_needed:.1f}% du volume total serait nécessaire pour atteindre le niveau optimal. "
                        f"Réduisez progressivement vos positions pour éviter une exposition excessive au risque.")
                    new_optimizations.append(optimization)
            
            # Vérifier la VaR mensuelle
            monthly_var = self.data_manager.calculate_monthly_var()
            if monthly_var > self.alert_thresholds['var_monthly']:
                alert = self.create_alert(current_time, "RISQUE", "VaR mensuelle élevée", f"{monthly_var:.2f}%")
                new_alerts.append(alert)
                
                optimization = self.create_optimization("RÉDUCTION DE LA VAR", 
                    f"Votre VaR mensuelle ({monthly_var:.2f}%) est supérieure au seuil configuré de {self.alert_thresholds['var_monthly']}%. "
                    f"Envisagez de diversifier davantage votre portefeuille ou de réduire l'exposition sur les instruments volatils.")
                new_optimizations.append(optimization)
            
            # Vérifier la perte journalière
            daily_pnl = self.calculate_daily_pnl()
            if daily_pnl < self.alert_thresholds['daily_loss']:
                alert = self.create_alert(current_time, "RISQUE", "Perte journalière importante", f"{daily_pnl:.2f}%")
                new_alerts.append(alert)
                
                optimization = self.create_optimization("GESTION DE RISQUE QUOTIDIEN", 
                    f"Votre perte journalière ({daily_pnl:.2f}%) dépasse le seuil configuré de {abs(self.alert_thresholds['daily_loss'])}%. "
                    f"Envisagez de réduire votre exposition pour le reste de la journée ou d'appliquer des stops plus serrés.")
                new_optimizations.append(optimization)
            
            # Vérifier le drawdown
            if equity_data is not None and not equity_data.empty:
                max_equity = equity_data.cummax()
                drawdown_series = (equity_data - max_equity) / max_equity * 100
                current_drawdown = drawdown_series.iloc[-1]
                
                if current_drawdown < self.alert_thresholds['drawdown']:
                    alert = self.create_alert(current_time, "RISQUE", "Drawdown important", f"{current_drawdown:.2f}%")
                    new_alerts.append(alert)
                    
                    optimization = self.create_optimization("GESTION DE DRAWDOWN", 
                        f"Votre drawdown actuel ({current_drawdown:.2f}%) dépasse le seuil configuré de {abs(self.alert_thresholds['drawdown'])}%. "
                        f"Envisagez de réduire temporairement la taille des positions et de revoir votre stratégie de gestion des risques.")
                    new_optimizations.append(optimization)
            
            # Mettre à jour les listes d'alertes et d'optimisations
            self.alerts.extend(new_alerts)
            self.optimizations.extend(new_optimizations)
            
            # Limiter la taille des listes
            self.alerts = self.alerts[-50:]  # Garder les 50 dernières alertes
            self.optimizations = self.optimizations[-20:]  # Garder les 20 dernières optimisations
            
            return new_alerts, new_optimizations
            
        except Exception as e:
            self.logger.exception("Erreur lors de la vérification des alertes")
            return [], []
    
    def create_alert(self, timestamp, alert_type, message, value):
        """
        Crée une alerte
        
        Args:
            timestamp (str): Horodatage de l'alerte
            alert_type (str): Type d'alerte
            message (str): Message de l'alerte
            value (str): Valeur associée à l'alerte
            
        Returns:
            dict: Alerte créée
        """
        return {
            "timestamp": timestamp,
            "type": alert_type,
            "message": message,
            "value": value
        }
    
    def create_optimization(self, title, message):
        """
        Crée une suggestion d'optimisation
        
        Args:
            title (str): Titre de la suggestion
            message (str): Message détaillé de la suggestion
            
        Returns:
            dict: Suggestion d'optimisation créée
        """
        return {
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "title": title,
            "message": message
        }
    
    def calculate_daily_pnl(self):
        """
        Calcule le P&L journalier en pourcentage
        
        Returns:
            float: P&L journalier en pourcentage
        """
        try:
            account_info = self.data_manager.account_info
            if not account_info:
                return 0
            
            # Calculer les positions
            positions = self.data_manager.positions
            if positions is None or positions.empty:
                return 0
            
            # Somme des profits flottants des positions ouvertes
            floating_profit = positions['profit'].sum()
            
            # P&L en pourcentage de la balance
            daily_pnl_pct = (floating_profit / account_info.balance) * 100
            
            return daily_pnl_pct
        
        except Exception as e:
            self.logger.exception("Erreur lors du calcul du P&L journalier")
            return 0
    
    def get_alerts(self, count=None):
        """
        Récupère les alertes
        
        Args:
            count (int, optional): Nombre d'alertes à récupérer
            
        Returns:
            list: Liste d'alertes
        """
        if count is None:
            return self.alerts
        else:
            return self.alerts[-count:]
    
    def get_optimizations(self, count=None):
        """
        Récupère les suggestions d'optimisation
        
        Args:
            count (int, optional): Nombre de suggestions à récupérer
            
        Returns:
            list: Liste de suggestions d'optimisation
        """
        if count is None:
            return self.optimizations
        else:
            return self.optimizations[-count:]
    
    def clear_alerts(self):
        """Efface toutes les alertes"""
        self.alerts = []
    
    def clear_optimizations(self):
        """Efface toutes les suggestions d'optimisation"""
        self.optimizations = []