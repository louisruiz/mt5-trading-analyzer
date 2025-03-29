#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de calcul des métriques de risque pour MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np
import scipy.stats as stats
from utils.helpers import calculate_drawdown

class RiskMetrics:
    """Classe pour le calcul des métriques de risque"""
    
    def __init__(self):
        """Initialisation de la classe de métriques de risque"""
        self.logger = logging.getLogger(__name__)
    
    def calculate_value_at_risk(self, returns, confidence_level=0.95, period_days=1):
        """
        Calcule la Value at Risk (VaR) paramétrique
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (entre 0 et 1)
            period_days (int): Période en jours
            
        Returns:
            float: VaR en pourcentage
        """
        try:
            if returns is None or len(returns) < 2:
                return 0
            
            # Calculer les paramètres
            mean = returns.mean()
            std = returns.std()
            
            # Facteur de scaling pour la période
            scaling_factor = np.sqrt(period_days)
            
            # Z-score pour le niveau de confiance
            z_score = stats.norm.ppf(1 - confidence_level)
            
            # Calculer la VaR
            var = -(mean + z_score * std) * scaling_factor * 100  # En pourcentage
            
            return var
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la VaR")
            return 0
    
    def calculate_expected_shortfall(self, returns, confidence_level=0.95, period_days=1):
        """
        Calcule l'Expected Shortfall (ES)
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (entre 0 et 1)
            period_days (int): Période en jours
            
        Returns:
            float: ES en pourcentage
        """
        try:
            if returns is None or len(returns) < 2:
                return 0
            
            # VaR comme seuil
            var_quantile = 1 - confidence_level
            var_threshold = returns.quantile(var_quantile)
            
            # Filtrer les rendements inférieurs à la VaR
            tail_returns = returns[returns <= var_threshold]
            
            # Si aucun rendement dans la queue
            if len(tail_returns) == 0:
                return 0
            
            # Calculer l'ES
            es = tail_returns.mean() * np.sqrt(period_days) * 100  # En pourcentage
            
            return -es  # Valeur positive pour faciliter l'interprétation
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de l'ES")
            return 0
    
    def calculate_var_by_historical(self, returns, confidence_level=0.95, period_days=1):
        """
        Calcule la Value at Risk (VaR) par méthode historique
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (entre 0 et 1)
            period_days (int): Période en jours
            
        Returns:
            float: VaR en pourcentage
        """
        try:
            if returns is None or len(returns) < 2:
                return 0
            
            # Facteur de scaling pour la période
            scaling_factor = np.sqrt(period_days)
            
            # Calculer la VaR historique
            var_quantile = 1 - confidence_level
            var = -returns.quantile(var_quantile) * scaling_factor * 100  # En pourcentage
            
            return var
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la VaR historique")
            return 0
    
    def calculate_var_by_monte_carlo(self, returns, confidence_level=0.95, period_days=1, simulations=10000):
        """
        Calcule la Value at Risk (VaR) par simulation Monte Carlo
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (entre 0 et 1)
            period_days (int): Période en jours
            simulations (int): Nombre de simulations
            
        Returns:
            float: VaR en pourcentage
        """
        try:
            if returns is None or len(returns) < 2:
                return 0
            
            # Calculer les paramètres
            mean = returns.mean()
            std = returns.std()
            
            # Facteur de scaling pour la période
            scaling_factor = np.sqrt(period_days)
            
            # Générer des scénarios aléatoires
            np.random.seed(42)  # Pour la reproductibilité
            simulated_returns = np.random.normal(mean, std, simulations)
            
            # Calculer la VaR à partir des simulations
            var_quantile = 1 - confidence_level
            var = -np.percentile(simulated_returns, var_quantile * 100) * scaling_factor * 100  # En pourcentage
            
            return var
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la VaR Monte Carlo")
            return 0
    
    def calculate_d_leverage(self, positions_volume, account_equity, contract_size=100000):
        """
        Calcule le D-Leverage (levier dynamique)
        
        Args:
            positions_volume (float): Somme des volumes des positions
            account_equity (float): Équité du compte
            contract_size (int): Taille standard d'un contrat
            
        Returns:
            float: D-Leverage
        """
        try:
            if account_equity <= 0:
                return 0
            
            d_leverage = (positions_volume * contract_size) / account_equity
            
            return d_leverage
        except Exception as e:
            self.logger.exception("Erreur lors du calcul du D-Leverage")
            return 0
    
    def calculate_position_correlation(self, returns_dict):
        """
        Calcule la matrice de corrélation entre les rendements des positions
        
        Args:
            returns_dict (dict): Dictionnaire des séries de rendements par symbole
            
        Returns:
            pd.DataFrame: Matrice de corrélation
        """
        try:
            # Créer un DataFrame à partir du dictionnaire
            returns_df = pd.DataFrame(returns_dict)
            
            # Calculer la matrice de corrélation
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la matrice de corrélation")
            return pd.DataFrame()
    
    def calculate_risk_concentration(self, positions_exposure):
        """
        Calcule la concentration du risque
        
        Args:
            positions_exposure (dict): Dictionnaire des expositions par position ou catégorie
            
        Returns:
            dict: Métriques de concentration
        """
        try:
            # Convertir en Series si c'est un dictionnaire
            if isinstance(positions_exposure, dict):
                exposure_series = pd.Series(positions_exposure)
            else:
                exposure_series = positions_exposure
            
            # Calculer l'exposition totale (en valeur absolue)
            total_exposure = exposure_series.abs().sum()
            
            if total_exposure == 0:
                return {
                    "hhi": 0,
                    "top_concentration": 0,
                    "max_exposure_pct": 0
                }
            
            # Calculer les pourcentages
            exposure_pct = (exposure_series.abs() / total_exposure) * 100
            
            # Indice de Herfindahl-Hirschman (HHI)
            hhi = ((exposure_pct / 100) ** 2).sum()
            
            # Concentration des 3 principales expositions
            top_concentration = exposure_pct.nlargest(3).sum()
            
            # Exposition maximale
            max_exposure_pct = exposure_pct.max()
            
            return {
                "hhi": hhi,
                "top_concentration": top_concentration,
                "max_exposure_pct": max_exposure_pct
            }
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la concentration du risque")
            return {
                "hhi": 0,
                "top_concentration": 0,
                "max_exposure_pct": 0
            }
    
    def calculate_maximum_drawdown(self, equity_series):
        """
        Calcule le drawdown maximum
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            
        Returns:
            tuple: (Drawdown maximum en pourcentage, Date de début, Date de fin, Durée en jours)
        """
        try:
            if equity_series is None or len(equity_series) < 2:
                return (0, None, None, 0)
            
            # Calculer la série de drawdowns
            drawdown_series = calculate_drawdown(equity_series)
            
            # Trouver le drawdown maximum
            max_drawdown = drawdown_series.min()
            max_drawdown_idx = drawdown_series.idxmin()
            
            # Trouver le pic précédent
            peak_equity = equity_series.loc[:max_drawdown_idx].cummax()
            peak_idx = peak_equity.loc[:max_drawdown_idx].idxmax()
            
            # Calculer la durée
            if peak_idx and max_drawdown_idx:
                duration_days = (max_drawdown_idx - peak_idx).days
            else:
                duration_days = 0
            
            return (max_drawdown, peak_idx, max_drawdown_idx, duration_days)
        except Exception as e:
            self.logger.exception("Erreur lors du calcul du drawdown maximum")
            return (0, None, None, 0)
    
    def analyze_drawdown_profile(self, equity_series, threshold=-5):
        """
        Analyse le profil de drawdown
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            threshold (float): Seuil de drawdown en pourcentage pour considérer un drawdown significatif
            
        Returns:
            dict: Statistiques sur les drawdowns
        """
        try:
            if equity_series is None or len(equity_series) < 10:
                return {}
            
            # Calculer la série de drawdowns
            drawdown_series = calculate_drawdown(equity_series)
            
            # Identifier les drawdowns significatifs
            significant_drawdowns = []
            in_drawdown = False
            start_idx = None
            current_dd = 0
            
            for date, dd in drawdown_series.items():
                if not in_drawdown and dd < threshold:
                    # Début d'un nouveau drawdown
                    in_drawdown = True
                    start_idx = date
                    current_dd = dd
                elif in_drawdown:
                    if dd < current_dd:
                        # Drawdown s'aggrave
                        current_dd = dd
                    elif dd >= 0:
                        # Fin du drawdown
                        in_drawdown = False
                        significant_drawdowns.append({
                            "start": start_idx,
                            "end": date,
                            "max_drawdown": current_dd,
                            "duration_days": (date - start_idx).days,
                            "recovery_duration": None  # À calculer
                        })
                        start_idx = None
                        current_dd = 0
            
            # Si encore en drawdown à la fin de la série
            if in_drawdown:
                significant_drawdowns.append({
                    "start": start_idx,
                    "end": drawdown_series.index[-1],
                    "max_drawdown": current_dd,
                    "duration_days": (drawdown_series.index[-1] - start_idx).days,
                    "recovery_duration": None  # À calculer (pas encore récupéré)
                })
            
            # Calculer les statistiques
            if significant_drawdowns:
                max_drawdowns = [dd["max_drawdown"] for dd in significant_drawdowns]
                durations = [dd["duration_days"] for dd in significant_drawdowns]
                
                stats = {
                    "count": len(significant_drawdowns),
                    "avg_drawdown": sum(max_drawdowns) / len(max_drawdowns),
                    "avg_duration": sum(durations) / len(durations) if durations else 0,
                    "max_drawdown": min(max_drawdowns) if max_drawdowns else 0,
                    "max_duration": max(durations) if durations else 0,
                    "drawdowns": significant_drawdowns
                }
                
                return stats
            else:
                return {
                    "count": 0,
                    "avg_drawdown": 0,
                    "avg_duration": 0,
                    "max_drawdown": 0,
                    "max_duration": 0,
                    "drawdowns": []
                }
                
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse du profil de drawdown")
            return {}

    # Ajoutez cette nouvelle méthode à la classe RiskMetrics dans le fichier analysis/risk_metrics.py

def calculate_expected_shortfall(self, returns, confidence_level=0.95, period_days=1):
    """
    Calcule l'Expected Shortfall (ES) ou Conditional Value at Risk (CVaR)
    
    Args:
        returns (pd.Series): Série de rendements
        confidence_level (float): Niveau de confiance (entre 0 et 1)
        period_days (int): Période en jours
        
    Returns:
        float: ES en pourcentage
    """
    try:
        if returns is None or len(returns) < 2:
            return 0
        
        # Calculer le quantile pour la VaR
        var_quantile = 1 - confidence_level
        var_threshold = returns.quantile(var_quantile)
        
        # Filtrer les rendements dans la queue de distribution
        tail_returns = returns[returns <= var_threshold]
        
        if len(tail_returns) == 0:
            return 0
        
        # Calculer l'ES
        es = tail_returns.mean() * np.sqrt(period_days) * 100  # En pourcentage
        
        return abs(es)  # Valeur positive pour faciliter l'interprétation
    except Exception as e:
        self.logger.exception("Erreur lors du calcul de l'Expected Shortfall")
        return 0