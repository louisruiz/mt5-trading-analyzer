#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fonctions utilitaires pour l'application MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def format_number(value, decimal_places=2, include_sign=False, as_percentage=False):
    """
    Formate un nombre pour l'affichage
    
    Args:
        value (float): Valeur à formater
        decimal_places (int): Nombre de décimales
        include_sign (bool): Inclure le signe +/- même pour les nombres positifs
        as_percentage (bool): Formater comme un pourcentage
        
    Returns:
        str: Nombre formaté
    """
    try:
        if value is None:
            return "-"
            
        if as_percentage:
            value = value * 100 if abs(value) < 1 else value
            
        # Formater le nombre avec les décimales spécifiées
        formatted = f"{value:.{decimal_places}f}"
        
        # Ajouter le signe +/- si demandé
        if include_sign and value > 0:
            formatted = f"+{formatted}"
            
        # Ajouter le symbole % si c'est un pourcentage
        if as_percentage:
            formatted = f"{formatted}%"
            
        return formatted
    except:
        return "-"

def format_currency(value, currency="EUR", decimal_places=2, include_sign=False):
    """
    Formate un montant avec le symbole de devise
    
    Args:
        value (float): Valeur à formater
        currency (str): Code de devise
        decimal_places (int): Nombre de décimales
        include_sign (bool): Inclure le signe +/- même pour les nombres positifs
        
    Returns:
        str: Montant formaté avec la devise
    """
    try:
        if value is None:
            return "-"
            
        # Formater le nombre
        formatted = format_number(value, decimal_places, include_sign)
        
        # Ajouter le symbole de devise
        return f"{formatted} {currency}"
    except:
        return "-"

def format_percentage(value, decimal_places=2, include_sign=True):
    """
    Formate un nombre comme un pourcentage
    
    Args:
        value (float): Valeur à formater
        decimal_places (int): Nombre de décimales
        include_sign (bool): Inclure le signe +/- même pour les nombres positifs
        
    Returns:
        str: Pourcentage formaté
    """
    return format_number(value, decimal_places, include_sign, as_percentage=True)

def format_timespan(seconds):
    """
    Formate une durée en secondes en format lisible
    
    Args:
        seconds (int): Durée en secondes
        
    Returns:
        str: Durée formatée (ex: "2j 3h 45m")
    """
    try:
        if seconds is None:
            return "-"
            
        # Calculer les jours, heures, minutes
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Générer le format lisible
        parts = []
        if days > 0:
            parts.append(f"{days}j")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        
        return " ".join(parts)
    except:
        return "-"

def calculate_drawdown(equity_series):
    """
    Calcule la série de drawdowns à partir d'une série d'équité
    
    Args:
        equity_series (pd.Series): Série temporelle d'équité
        
    Returns:
        pd.Series: Série de drawdowns en pourcentage
    """
    try:
        if equity_series is None or len(equity_series) == 0:
            return pd.Series()
            
        # Calculer les maxima cumulatifs
        rolling_max = equity_series.cummax()
        
        # Calculer le drawdown en pourcentage
        drawdown_series = (equity_series - rolling_max) / rolling_max * 100
        
        return drawdown_series
    except Exception as e:
        logger.exception("Erreur lors du calcul du drawdown")
        return pd.Series()

def calculate_returns(equity_series, period='D'):
    """
    Calcule les rendements à partir d'une série d'équité
    
    Args:
        equity_series (pd.Series): Série temporelle d'équité
        period (str): Période pour les rendements ('D' pour quotidien, 'W' pour hebdomadaire, etc.)
        
    Returns:
        pd.Series: Série de rendements
    """
    try:
        if equity_series is None or len(equity_series) < 2:
            return pd.Series()
            
        # Rééchantillonner si nécessaire
        if period != 'D':
            equity_resampled = equity_series.resample(period).last()
        else:
            equity_resampled = equity_series
            
        # Calculer les rendements
        returns = equity_resampled.pct_change().dropna()
        
        return returns
    except Exception as e:
        logger.exception("Erreur lors du calcul des rendements")
        return pd.Series()

def ensure_directory_exists(directory_path):
    """
    Crée un répertoire s'il n'existe pas
    
    Args:
        directory_path (str or Path): Chemin du répertoire à créer
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.exception(f"Erreur lors de la création du répertoire {directory_path}")
        return False

def get_safe_filename(filename):
    """
    Génère un nom de fichier sûr en remplaçant les caractères non autorisés
    
    Args:
        filename (str): Nom de fichier original
        
    Returns:
        str: Nom de fichier sécurisé
    """
    # Remplacer les caractères non autorisés par des underscores
    safe_name = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return safe_name

def export_dataframe_to_csv(df, filename, directory=None):
    """
    Exporte un DataFrame vers un fichier CSV
    
    Args:
        df (pd.DataFrame): DataFrame à exporter
        filename (str): Nom du fichier
        directory (str, optional): Répertoire de destination
        
    Returns:
        bool: True si l'export a réussi, False sinon
    """
    try:
        if df is None or df.empty:
            logger.warning("Tentative d'export d'un DataFrame vide")
            return False
            
        # Générer un nom de fichier sûr
        safe_filename = get_safe_filename(filename)
        
        # Définir le chemin complet
        if directory:
            ensure_directory_exists(directory)
            full_path = Path(directory) / safe_filename
        else:
            full_path = Path(safe_filename)
        
        # Exporter vers CSV
        df.to_csv(full_path, index=True, encoding='utf-8')
        logger.info(f"DataFrame exporté avec succès vers {full_path}")
        return True
    except Exception as e:
        logger.exception(f"Erreur lors de l'export du DataFrame vers {filename}")
        return False

def moving_average(series, window):
    """
    Calcule la moyenne mobile d'une série
    
    Args:
        series (pd.Series): Série de données
        window (int): Taille de la fenêtre
        
    Returns:
        pd.Series: Série de moyennes mobiles
    """
    try:
        return series.rolling(window=window, min_periods=1).mean()
    except Exception as e:
        logger.exception("Erreur lors du calcul de la moyenne mobile")
        return pd.Series()

def exponential_moving_average(series, span):
    """
    Calcule la moyenne mobile exponentielle d'une série
    
    Args:
        series (pd.Series): Série de données
        span (int): Période pour l'EMA
        
    Returns:
        pd.Series: Série de moyennes mobiles exponentielles
    """
    try:
        return series.ewm(span=span, adjust=False).mean()
    except Exception as e:
        logger.exception("Erreur lors du calcul de l'EMA")
        return pd.Series()

def calculate_sharpe_ratio(returns, risk_free_rate=0.03, periods_per_year=252):
    """
    Calcule le ratio de Sharpe
    
    Args:
        returns (pd.Series): Série de rendements
        risk_free_rate (float): Taux sans risque annualisé
        periods_per_year (int): Nombre de périodes par an
        
    Returns:
        float: Ratio de Sharpe
    """
    try:
        if returns is None or len(returns) == 0:
            return 0
            
        # Convertir le taux sans risque en taux périodique
        rf_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
        
        # Calculer l'excès de rendement
        excess_returns = returns - rf_period
        
        # Calculer le ratio de Sharpe
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(periods_per_year)
        
        return sharpe
    except Exception as e:
        logger.exception("Erreur lors du calcul du ratio de Sharpe")
        return 0

def calculate_sortino_ratio(returns, risk_free_rate=0.03, periods_per_year=252):
    """
    Calcule le ratio de Sortino
    
    Args:
        returns (pd.Series): Série de rendements
        risk_free_rate (float): Taux sans risque annualisé
        periods_per_year (int): Nombre de périodes par an
        
    Returns:
        float: Ratio de Sortino
    """
    try:
        if returns is None or len(returns) == 0:
            return 0
            
        # Convertir le taux sans risque en taux périodique
        rf_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
        
        # Calculer l'excès de rendement
        excess_returns = returns - rf_period
        
        # Isoler les rendements négatifs
        negative_returns = excess_returns[excess_returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf')  # Pas de rendements négatifs
            
        # Calculer le ratio de Sortino
        downside_deviation = np.sqrt(np.sum(negative_returns ** 2) / len(negative_returns)) * np.sqrt(periods_per_year)
        sortino = excess_returns.mean() * periods_per_year / downside_deviation
        
        return sortino
    except Exception as e:
        logger.exception("Erreur lors du calcul du ratio de Sortino")
        return 0

def calculate_calmar_ratio(returns, max_drawdown, periods_per_year=252):
    """
    Calcule le ratio de Calmar
    
    Args:
        returns (pd.Series): Série de rendements
        max_drawdown (float): Drawdown maximum (en valeur absolue)
        periods_per_year (int): Nombre de périodes par an
        
    Returns:
        float: Ratio de Calmar
    """
    try:
        if returns is None or len(returns) == 0 or max_drawdown == 0:
            return 0
            
        # Calculer le rendement annualisé
        annualized_return = returns.mean() * periods_per_year
        
        # Calculer le ratio de Calmar
        calmar = annualized_return / abs(max_drawdown)
        
        return calmar
    except Exception as e:
        logger.exception("Erreur lors du calcul du ratio de Calmar")
        return 0

def calculate_win_ratio(returns):
    """
    Calcule le ratio de gains/pertes
    
    Args:
        returns (pd.Series): Série de rendements
        
    Returns:
        float: Ratio de gains en pourcentage
    """
    try:
        if returns is None or len(returns) == 0:
            return 0
            
        # Compter les rendements positifs et négatifs
        win_count = (returns > 0).sum()
        total_count = len(returns)
        
        # Calculer le ratio de gains
        win_ratio = (win_count / total_count) * 100 if total_count > 0 else 0
        
        return win_ratio
    except Exception as e:
        logger.exception("Erreur lors du calcul du ratio de gains")
        return 0