#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de calcul des métriques de performance pour MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np
import scipy.stats as stats
from utils.helpers import (
    calculate_returns, calculate_drawdown, calculate_sharpe_ratio,
    calculate_sortino_ratio, calculate_calmar_ratio, calculate_win_ratio
)

class PerformanceMetrics:
    """Classe pour le calcul des métriques de performance"""
    
    def __init__(self):
        """Initialisation de la classe de métriques de performance"""
        self.logger = logging.getLogger(__name__)
    
    def calculate_metrics(self, equity_series, risk_free_rate=0.03, periods_per_year=252):
        """
        Calcule toutes les métriques de performance à partir d'une série d'équité
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            risk_free_rate (float): Taux sans risque annualisé
            periods_per_year (int): Nombre de périodes par an
            
        Returns:
            dict: Dictionnaire des métriques de performance
        """
        if equity_series is None or len(equity_series) < 2:
            return {}
        
        try:
            # Calcul des rendements
            returns = calculate_returns(equity_series)
            
            # Calcul du drawdown
            drawdown_series = calculate_drawdown(equity_series)
            max_drawdown = drawdown_series.min() if not drawdown_series.empty else 0
            
            # Métriques de base
            total_return = (equity_series.iloc[-1] / equity_series.iloc[0] - 1) * 100
            period_count = len(returns)
            annualized_return = total_return * (periods_per_year / period_count) if period_count > 0 else 0
            
            # Volatilité
            volatility = returns.std() * np.sqrt(periods_per_year) * 100
            
            # Ratios de performance
            sharpe_ratio = calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year)
            sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate, periods_per_year)
            calmar_ratio = calculate_calmar_ratio(returns, max_drawdown / 100, periods_per_year)
            
            # Statistiques de distribution
            skewness = stats.skew(returns) if len(returns) > 2 else 0
            kurtosis = stats.kurtosis(returns) if len(returns) > 2 else 0
            
            # Ratio de gains/pertes
            win_ratio = calculate_win_ratio(returns)
            
            # Calculer les statistiques de rendement moyen
            avg_win = returns[returns > 0].mean() * 100 if len(returns[returns > 0]) > 0 else 0
            avg_loss = returns[returns < 0].mean() * 100 if len(returns[returns < 0]) > 0 else 0
            win_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            # Retour des métriques sous forme de dictionnaire
            metrics = {
                "total_return": total_return,
                "annualized_return": annualized_return,
                "volatility": volatility,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "calmar_ratio": calmar_ratio,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "win_ratio": win_ratio,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "win_loss_ratio": win_loss_ratio,
                "period_count": period_count
            }
            
            return metrics
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul des métriques de performance")
            return {}
    
    def calculate_rolling_metrics(self, equity_series, window=30, risk_free_rate=0.03, periods_per_year=252):
        """
        Calcule les métriques de performance glissantes
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            window (int): Taille de la fenêtre glissante en jours
            risk_free_rate (float): Taux sans risque annualisé
            periods_per_year (int): Nombre de périodes par an
            
        Returns:
            dict: Dictionnaire des séries de métriques glissantes
        """
        if equity_series is None or len(equity_series) < window + 1:
            return {}
        
        try:
            # Calculer les rendements
            returns = calculate_returns(equity_series)
            
            # Initialiser les séries pour stocker les métriques glissantes
            rolling_metrics = {
                "returns": pd.Series(index=returns.index),
                "volatility": pd.Series(index=returns.index),
                "sharpe": pd.Series(index=returns.index),
                "drawdown": pd.Series(index=returns.index)
            }
            
            # Calculer les métriques glissantes
            for i in range(window, len(returns) + 1):
                window_returns = returns.iloc[i-window:i]
                window_equity = equity_series.iloc[i-window:i+1]
                
                # Rendement de la fenêtre
                window_return = (window_equity.iloc[-1] / window_equity.iloc[0] - 1) * 100
                rolling_metrics["returns"].iloc[i-1] = window_return
                
                # Volatilité de la fenêtre
                window_volatility = window_returns.std() * np.sqrt(periods_per_year) * 100
                rolling_metrics["volatility"].iloc[i-1] = window_volatility
                
                # Ratio de Sharpe de la fenêtre
                window_sharpe = calculate_sharpe_ratio(window_returns, risk_free_rate, periods_per_year)
                rolling_metrics["sharpe"].iloc[i-1] = window_sharpe
                
                # Drawdown maximal de la fenêtre
                window_drawdown = calculate_drawdown(window_equity).min()
                rolling_metrics["drawdown"].iloc[i-1] = window_drawdown
            
            return rolling_metrics
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul des métriques glissantes")
            return {}
    
    def analyze_return_distribution(self, equity_series):
        """
        Analyse la distribution des rendements
        
        Args:
            equity_series (pd.Series): Série temporelle d'équité
            
        Returns:
            dict: Statistiques de distribution
        """
        if equity_series is None or len(equity_series) < 2:
            return {}
        
        try:
            # Calculer les rendements
            returns = calculate_returns(equity_series)
            
            # Statistiques de base
            mean = returns.mean() * 100
            median = returns.median() * 100
            std = returns.std() * 100
            min_return = returns.min() * 100
            max_return = returns.max() * 100
            
            # Statistiques de distribution
            skewness = stats.skew(returns) if len(returns) > 2 else 0
            kurtosis = stats.kurtosis(returns) if len(returns) > 2 else 0
            
            # Test de normalité (Jarque-Bera)
            jb_stat, jb_pvalue = stats.jarque_bera(returns) if len(returns) > 2 else (0, 1)
            
            # Quantiles
            q1 = returns.quantile(0.25) * 100
            q3 = returns.quantile(0.75) * 100
            p1 = returns.quantile(0.01) * 100  # 1% pire rendement
            p99 = returns.quantile(0.99) * 100  # 1% meilleur rendement
            
            # VAR et ES à 95%
            var_95 = returns.quantile(0.05) * 100
            es_95 = returns[returns <= returns.quantile(0.05)].mean() * 100
            
            # Retour des statistiques sous forme de dictionnaire
            stats_dict = {
                "mean": mean,
                "median": median,
                "std": std,
                "min": min_return,
                "max": max_return,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "jarque_bera_stat": jb_stat,
                "jarque_bera_pvalue": jb_pvalue,
                "q1": q1,
                "q3": q3,
                "p1": p1,
                "p99": p99,
                "var_95": var_95,
                "es_95": es_95
            }
            
            return stats_dict
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse de la distribution des rendements")
            return {}