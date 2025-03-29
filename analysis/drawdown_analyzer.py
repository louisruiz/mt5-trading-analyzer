#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'analyse avancée de drawdown pour MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np

class DrawdownAnalyzer:
    """Classe pour l'analyse avancée des drawdowns"""
    
    def __init__(self):
        """Initialisation de l'analyseur de drawdown"""
        self.logger = logging.getLogger(__name__)
    
    def identify_drawdowns(self, equity_series, threshold_pct=-5):
        """
        Identifie tous les drawdowns significatifs dans une série d'équité
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            threshold_pct (float): Seuil en pourcentage pour considérer un drawdown comme significatif
            
        Returns:
            list: Liste des drawdowns significatifs
        """
        try:
            if equity_series is None or len(equity_series) < 5:
                return []
            
            # Calculer la série de drawdowns
            rolling_max = equity_series.cummax()
            drawdown_series = (equity_series - rolling_max) / rolling_max * 100
            
            # Initialiser les variables pour suivre les drawdowns
            drawdowns = []
            in_drawdown = False
            start_idx = None
            start_value = None
            current_dd = 0
            current_idx = None
            
            for date, value in drawdown_series.items():
                if not in_drawdown and value < threshold_pct:
                    # Début d'un nouveau drawdown
                    in_drawdown = True
                    start_idx = date
                    start_value = equity_series[date]
                    current_dd = value
                    current_idx = date
                elif in_drawdown:
                    if value < current_dd:
                        # Drawdown s'aggrave
                        current_dd = value
                        current_idx = date
                    elif value >= 0:
                        # Fin du drawdown, calculer les métriques
                        end_idx = date
                        recovery_value = equity_series[date]
                        bottom_value = equity_series[current_idx]
                        
                        # Calculer les durées
                        drawdown_duration = (current_idx - start_idx).days
                        recovery_duration = (end_idx - current_idx).days
                        total_duration = (end_idx - start_idx).days
                        
                        # Calculer les pertes et gains
                        drawdown_amount = (bottom_value - start_value) / start_value * 100
                        recovery_amount = (recovery_value - bottom_value) / bottom_value * 100
                        
                        # Ajouter le drawdown à la liste
                        drawdowns.append({
                            "start_date": start_idx,
                            "bottom_date": current_idx,
                            "end_date": end_idx,
                            "max_drawdown_pct": current_dd,
                            "drawdown_amount_pct": drawdown_amount,
                            "recovery_amount_pct": recovery_amount,
                            "drawdown_duration_days": drawdown_duration,
                            "recovery_duration_days": recovery_duration,
                            "total_duration_days": total_duration,
                            "pain_index": abs(current_dd) * total_duration / 365,  # Pain Index normalisé
                            "recovery_ratio": abs(recovery_amount / drawdown_amount) if drawdown_amount != 0 else 0
                        })
                        
                        # Réinitialiser les variables
                        in_drawdown = False
                        start_idx = None
                        start_value = None
                        current_dd = 0
                        current_idx = None
            
            # Si toujours en drawdown à la fin de la série
            if in_drawdown:
                end_idx = drawdown_series.index[-1]
                recovery_value = equity_series[end_idx]
                bottom_value = equity_series[current_idx]
                
                # Calculer les durées
                drawdown_duration = (current_idx - start_idx).days
                recovery_duration = 0  # Pas encore récupéré
                total_duration = (end_idx - start_idx).days
                
                # Calculer les pertes et gains
                drawdown_amount = (bottom_value - start_value) / start_value * 100
                recovery_amount = (recovery_value - bottom_value) / bottom_value * 100
                
                # Ajouter le drawdown en cours à la liste
                drawdowns.append({
                    "start_date": start_idx,
                    "bottom_date": current_idx,
                    "end_date": None,  # Pas encore terminé
                    "max_drawdown_pct": current_dd,
                    "drawdown_amount_pct": drawdown_amount,
                    "recovery_amount_pct": recovery_amount,
                    "drawdown_duration_days": drawdown_duration,
                    "recovery_duration_days": recovery_duration,
                    "total_duration_days": total_duration,
                    "pain_index": abs(current_dd) * total_duration / 365,  # Pain Index normalisé
                    "recovery_ratio": abs(recovery_amount / drawdown_amount) if drawdown_amount != 0 else 0,
                    "active": True  # Drawdown toujours actif
                })
            
            # Trier les drawdowns par ampleur
            return sorted(drawdowns, key=lambda x: x["max_drawdown_pct"])
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'identification des drawdowns")
            return []
    
    def calculate_ulcer_index(self, equity_series, period=14):
        """
        Calcule l'Ulcer Index qui mesure la profondeur et la durée des drawdowns
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            period (int): Période pour le calcul (en jours)
            
        Returns:
            float: Ulcer Index
        """
        try:
            if equity_series is None or len(equity_series) < period:
                return 0
            
            # Calculer les drawdowns au carré
            rolling_max = equity_series.rolling(window=period, min_periods=1).max()
            drawdown_pct = (equity_series - rolling_max) / rolling_max * 100
            squared_dd = drawdown_pct ** 2
            
            # Calculer l'Ulcer Index (racine carrée de la moyenne des drawdowns au carré)
            ulcer_index = np.sqrt(squared_dd.mean())
            
            return abs(ulcer_index)
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de l'Ulcer Index")
            return 0
    
    def calculate_pain_index(self, equity_series, period=None):
        """
        Calcule le Pain Index qui mesure la moyenne des drawdowns
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            period (int, optional): Période pour le calcul (en jours). Si None, utilise toute la série.
            
        Returns:
            float: Pain Index
        """
        try:
            if equity_series is None or len(equity_series) < 2:
                return 0
            
            # Filtrer la série si une période est spécifiée
            if period is not None and period < len(equity_series):
                equity_series = equity_series.iloc[-period:]
            
            # Calculer la série de drawdowns
            rolling_max = equity_series.cummax()
            drawdown_series = (equity_series - rolling_max) / rolling_max * 100
            
            # Le Pain Index est la moyenne des drawdowns absolus
            pain_index = abs(drawdown_series).mean()
            
            return pain_index
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul du Pain Index")
            return 0
    
    def find_change_points(self, equity_series, sensitivity=0.05):
        """
        Identifie les points de changement statistiquement significatifs dans la courbe d'équité
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            sensitivity (float): Sensibilité pour la détection des changements (0-1)
            
        Returns:
            list: Liste des dates de changement significatif
        """
        try:
            if equity_series is None or len(equity_series) < 30:
                return []
            
            # Calculer les rendements pour détecter les changements de tendance
            returns = equity_series.pct_change().dropna()
            
            # Calculer les moyennes mobiles court et long terme
            short_ma = returns.rolling(window=10).mean()
            long_ma = returns.rolling(window=30).mean()
            
            # Détecter les croisements des moyennes mobiles
            prev_diff = None
            change_points = []
            
            for date, short, long in zip(returns.index[30:], short_ma[30:], long_ma[30:]):
                diff = short - long
                
                if prev_diff is not None:
                    # Détecter un croisement (changement de signe)
                    if (prev_diff < 0 and diff > 0) or (prev_diff > 0 and diff < 0):
                        # Vérifier si la différence est significative
                        if abs(diff) > sensitivity:
                            change_points.append(date)
                
                prev_diff = diff
            
            return change_points
            
        except Exception as e:
            self.logger.exception("Erreur lors de la recherche des points de changement")
            return []