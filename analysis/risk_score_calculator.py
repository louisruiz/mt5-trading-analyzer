#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Calculateur de score de risque global pour MT5 Trading Analyzer
"""

import logging
import numpy as np
from utils.constants import TRADING_CATEGORIES

class RiskScoreCalculator:
    """Classe pour calculer un score de risque global composite"""
    
    def __init__(self):
        """Initialisation du calculateur de score de risque"""
        self.logger = logging.getLogger(__name__)
        
        # Poids pour les différentes composantes du score
        self.weights = {
            "d_leverage": 0.25,
            "var": 0.20,
            "drawdown": 0.15,
            "margin_pct": 0.15,
            "concentration": 0.15,
            "volatility": 0.10,
        }
    
    def calculate_global_risk_score(self, metrics):
        """
        Calcule un score de risque global normalisé (0-100)
        
        Args:
            metrics (dict): Dictionnaire des métriques de risque
                Required keys:
                - d_leverage: D-Leverage actuel
                - trading_style: Style de trading ('scalping', 'intraday', 'swing')
                - var_monthly: VaR mensuelle à 95%
                - max_drawdown: Drawdown maximum en pourcentage
                - margin_pct: Pourcentage de marge utilisée
                - concentration: Indice de concentration (HHI normalisé)
                - volatility: Volatilité annualisée en pourcentage
                
        Returns:
            dict: Score de risque global et détails par composante
        """
        try:
            if not all(k in metrics for k in ["d_leverage", "trading_style", "var_monthly", 
                                             "max_drawdown", "margin_pct", "concentration", 
                                             "volatility"]):
                return {"score": 50, "details": {}, "rating": "Indéterminé", "color": "gray"}
            
            # Initialiser les scores par composante
            component_scores = {}
            
            # 1. Score D-Leverage (0-100, plus haut = plus risqué)
            style = metrics["trading_style"]
            d_leverage = metrics["d_leverage"]
            
            if style == "scalping":
                threshold_min = 0
                threshold_optimal = 10
                threshold_max = TRADING_CATEGORIES["Scalping"]["optimal_max"]
                threshold_extreme = threshold_max * 1.5
            elif style == "intraday":
                threshold_min = 0
                threshold_optimal = 8
                threshold_max = TRADING_CATEGORIES["Intraday"]["optimal_max"]
                threshold_extreme = threshold_max * 1.5
            else:  # swing
                threshold_min = 0
                threshold_optimal = 5
                threshold_max = TRADING_CATEGORIES["Swing"]["optimal_max"]
                threshold_extreme = threshold_max * 1.5
            
            if d_leverage <= threshold_min:
                d_leverage_score = 0  # Pas de risque
            elif d_leverage <= threshold_optimal:
                d_leverage_score = 20 + (d_leverage / threshold_optimal) * 30  # 20-50
            elif d_leverage <= threshold_max:
                progress = (d_leverage - threshold_optimal) / (threshold_max - threshold_optimal)
                d_leverage_score = 50 + progress * 20  # 50-70
            elif d_leverage <= threshold_extreme:
                progress = (d_leverage - threshold_max) / (threshold_extreme - threshold_max)
                d_leverage_score = 70 + progress * 30  # 70-100
            else:
                d_leverage_score = 100  # Risque maximal
            
            component_scores["d_leverage"] = d_leverage_score
            
            # 2. Score VaR (0-100, plus haut = plus risqué)
            var_monthly = metrics["var_monthly"]
            
            threshold_var_low = 5  # VaR mensuelle de 5% considérée comme faible
            threshold_var_medium = 10  # VaR mensuelle de 10% considérée comme moyenne
            threshold_var_high = 15  # VaR mensuelle de 15% considérée comme élevée
            threshold_var_extreme = 25  # VaR mensuelle de 25% considérée comme extrême
            
            if var_monthly <= threshold_var_low:
                var_score = (var_monthly / threshold_var_low) * 30  # 0-30
            elif var_monthly <= threshold_var_medium:
                progress = (var_monthly - threshold_var_low) / (threshold_var_medium - threshold_var_low)
                var_score = 30 + progress * 30  # 30-60
            elif var_monthly <= threshold_var_high:
                progress = (var_monthly - threshold_var_medium) / (threshold_var_high - threshold_var_medium)
                var_score = 60 + progress * 20  # 60-80
            elif var_monthly <= threshold_var_extreme:
                progress = (var_monthly - threshold_var_high) / (threshold_var_extreme - threshold_var_high)
                var_score = 80 + progress * 20  # 80-100
            else:
                var_score = 100  # Risque maximal
            
            component_scores["var"] = var_score
            
            # 3. Score Drawdown (0-100, plus haut = plus risqué)
            drawdown = abs(metrics["max_drawdown"])
            
            threshold_dd_low = 5  # Drawdown de 5% considéré comme faible
            threshold_dd_medium = 15  # Drawdown de 15% considéré comme moyen
            threshold_dd_high = 25  # Drawdown de 25% considéré comme élevé
            threshold_dd_extreme = 40  # Drawdown de 40% considéré comme extrême
            
            if drawdown <= threshold_dd_low:
                drawdown_score = (drawdown / threshold_dd_low) * 20  # 0-20
            elif drawdown <= threshold_dd_medium:
                progress = (drawdown - threshold_dd_low) / (threshold_dd_medium - threshold_dd_low)
                drawdown_score = 20 + progress * 40  # 20-60
            elif drawdown <= threshold_dd_high:
                progress = (drawdown - threshold_dd_medium) / (threshold_dd_high - threshold_dd_medium)
                drawdown_score = 60 + progress * 20  # 60-80
            elif drawdown <= threshold_dd_extreme:
                progress = (drawdown - threshold_dd_high) / (threshold_dd_extreme - threshold_dd_high)
                drawdown_score = 80 + progress * 20  # 80-100
            else:
                drawdown_score = 100  # Risque maximal
            
            component_scores["drawdown"] = drawdown_score
            
            # 4. Score Marge (0-100, plus haut = plus risqué)
            margin_pct = metrics["margin_pct"]
            
            threshold_margin_low = 20  # Marge de 20% considérée comme faible
            threshold_margin_medium = 40  # Marge de 40% considérée comme moyenne
            threshold_margin_high = 70  # Marge de 70% considérée comme élevée
            threshold_margin_extreme = 90  # Marge de 90% considérée comme extrême
            
            if margin_pct <= threshold_margin_low:
                margin_score = (margin_pct / threshold_margin_low) * 20  # 0-20
            elif margin_pct <= threshold_margin_medium:
                progress = (margin_pct - threshold_margin_low) / (threshold_margin_medium - threshold_margin_low)
                margin_score = 20 + progress * 30  # 20-50
            elif margin_pct <= threshold_margin_high:
                progress = (margin_pct - threshold_margin_medium) / (threshold_margin_high - threshold_margin_medium)
                margin_score = 50 + progress * 30  # 50-80
            elif margin_pct <= threshold_margin_extreme:
                progress = (margin_pct - threshold_margin_high) / (threshold_margin_extreme - threshold_margin_high)
                margin_score = 80 + progress * 20  # 80-100
            else:
                margin_score = 100  # Risque maximal
            
            component_scores["margin_pct"] = margin_score
            
            # 5. Score Concentration (0-100, plus haut = plus risqué)
            concentration = metrics["concentration"]  # HHI normalisé (0-1)
            
            # Conversion linéaire simple en score 0-100
            concentration_score = concentration * 100
            component_scores["concentration"] = concentration_score
            
            # 6. Score Volatilité (0-100, plus haut = plus risqué)
            volatility = metrics["volatility"]
            
            threshold_vol_low = 10  # Volatilité annualisée de 10% considérée comme faible
            threshold_vol_medium = 20  # Volatilité annualisée de 20% considérée comme moyenne
            threshold_vol_high = 30  # Volatilité annualisée de 30% considérée comme élevée
            threshold_vol_extreme = 50  # Volatilité annualisée de 50% considérée comme extrême
            
            if volatility <= threshold_vol_low:
                volatility_score = (volatility / threshold_vol_low) * 25  # 0-25
            elif volatility <= threshold_vol_medium:
                progress = (volatility - threshold_vol_low) / (threshold_vol_medium - threshold_vol_low)
                volatility_score = 25 + progress * 25  # 25-50
            elif volatility <= threshold_vol_high:
                progress = (volatility - threshold_vol_medium) / (threshold_vol_high - threshold_vol_medium)
                volatility_score = 50 + progress * 25  # 50-75
            elif volatility <= threshold_vol_extreme:
                progress = (volatility - threshold_vol_high) / (threshold_vol_extreme - threshold_vol_high)
                volatility_score = 75 + progress * 25  # 75-100
            else:
                volatility_score = 100  # Risque maximal
            
            component_scores["volatility"] = volatility_score
            
            # Calculer le score global pondéré
            global_score = 0
            for component, score in component_scores.items():
                global_score += score * self.weights.get(component, 0)
            
            # Arrondir à l'entier le plus proche
            global_score = round(global_score)
            
            # Déterminer le rating et la couleur
            if global_score < 20:
                rating = "Très faible"
                color = "#0070C0"  # Bleu
            elif global_score < 40:
                rating = "Faible"
                color = "#00B050"  # Vert
            elif global_score < 60:
                rating = "Modéré"
                color = "#FFC000"  # Jaune
            elif global_score < 80:
                rating = "Élevé"
                color = "#FF6600"  # Orange
            else:
                rating = "Extrême"
                color = "#C00000"  # Rouge
            
            return {
                "score": global_score,
                "details": component_scores,
                "rating": rating,
                "color": color
            }
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul du score de risque global")
            return {"score": 50, "details": {}, "rating": "Erreur", "color": "gray"}