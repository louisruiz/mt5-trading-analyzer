#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'analyse d'allocation pour MT5 Trading Analyzer
"""

import logging
import pandas as pd
import numpy as np

class AllocationAnalysis:
    """Classe pour l'analyse de l'allocation"""
    
    def __init__(self):
        """Initialisation de la classe d'analyse d'allocation"""
        self.logger = logging.getLogger(__name__)
    
    def analyze_symbol_allocation(self, positions_df):
        """
        Analyse l'allocation par symbole
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            
        Returns:
            tuple: (allocation_pct, exposure)
        """
        try:
            if positions_df is None or positions_df.empty:
                return pd.Series(), pd.Series()
            
            # Calculer la taille des positions
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Calculer l'exposition (en tenant compte du sens des positions)
            positions_df['exposure'] = positions_df.apply(
                lambda row: row['volume'] * row['price_current'] * (1 if row['type'] == 0 else -1),
                axis=1
            )
            
            # Grouper par symbole
            allocation = positions_df.groupby('symbol')['position_size'].sum()
            exposure = positions_df.groupby('symbol')['exposure'].sum()
            
            # Calculer les proportions pour l'allocation
            total_size = allocation.sum()
            if total_size <= 0:
                allocation_pct = pd.Series()
            else:
                allocation_pct = (allocation / total_size * 100).sort_values(ascending=False)
            
            return allocation_pct, exposure
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse de l'allocation par symbole")
            return pd.Series(), pd.Series()
    
    def analyze_direction_allocation(self, positions_df):
        """
        Analyse l'allocation par direction (buy/sell)
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            
        Returns:
            tuple: (allocation_pct, symbol_direction_allocation)
        """
        try:
            if positions_df is None or positions_df.empty:
                return pd.Series(), pd.DataFrame()
            
            # Ajouter une colonne pour la direction
            positions_df['direction'] = positions_df['type'].map({0: 'BUY', 1: 'SELL'})
            
            # Calculer la taille des positions
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Grouper par direction
            allocation = positions_df.groupby('direction')['position_size'].sum()
            
            # Calculer les proportions
            total_size = allocation.sum()
            if total_size <= 0:
                allocation_pct = pd.Series()
            else:
                allocation_pct = (allocation / total_size * 100)
            
            # Créer un tableau croisé pour l'allocation par symbole et direction
            pivot = pd.pivot_table(positions_df, values='position_size', 
                                   index='symbol', columns='direction', 
                                   aggfunc='sum', fill_value=0)
            
            # Ajouter une colonne pour le total
            pivot['total'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('total', ascending=False)
            
            return allocation_pct, pivot
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse de l'allocation par direction")
            return pd.Series(), pd.DataFrame()
    
    def analyze_duration_allocation(self, positions_df):
        """
        Analyse l'allocation par durée des positions
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            
        Returns:
            tuple: (allocation_pct, duration_direction_allocation)
        """
        try:
            if positions_df is None or positions_df.empty:
                return pd.Series(), pd.DataFrame()
            
            # S'assurer que la colonne 'time' existe
            if 'time' not in positions_df.columns:
                return pd.Series(), pd.DataFrame()
            
            # Calculer la durée de chaque position en minutes
            now = pd.Timestamp.now()
            positions_df['duration_minutes'] = positions_df['time'].apply(
                lambda x: (now - pd.Timestamp.fromtimestamp(x)).total_seconds() / 60
            )
            
            # Catégoriser les durées
            def categorize_duration(minutes):
                if minutes < 30:
                    return "< 30 min (Scalping)"
                elif minutes < 60:
                    return "30-60 min (Intraday)"
                elif minutes < 1440:  # 24 heures
                    return "1-24 h (Day Trading)"
                else:
                    return "> 24 h (Swing/Position)"
            
            positions_df['duration_category'] = positions_df['duration_minutes'].apply(categorize_duration)
            
            # Calculer la taille des positions
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Grouper par catégorie de durée
            allocation = positions_df.groupby('duration_category')['position_size'].sum()
            
            # Définir l'ordre des catégories
            category_order = ["< 30 min (Scalping)", "30-60 min (Intraday)", 
                             "1-24 h (Day Trading)", "> 24 h (Swing/Position)"]
            allocation = allocation.reindex(category_order).dropna()
            
            # Calculer les proportions
            total_size = allocation.sum()
            if total_size <= 0:
                allocation_pct = pd.Series()
            else:
                allocation_pct = (allocation / total_size * 100)
            
            # Ajouter une colonne pour la direction
            positions_df['direction'] = positions_df['type'].map({0: 'BUY', 1: 'SELL'})
            
            # Créer un tableau croisé par durée et direction
            pivot = pd.pivot_table(positions_df, values='position_size', 
                                 index='duration_category', columns='direction', 
                                 aggfunc='sum', fill_value=0)
            
            # Réordonner selon la catégorie
            pivot = pivot.reindex(category_order).dropna(how='all')
            
            return allocation_pct, pivot
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse de l'allocation par durée")
            return pd.Series(), pd.DataFrame()
    
    def calculate_portfolio_exposure(self, positions_df):
        """
        Calcule l'exposition totale du portefeuille en long et short
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            
        Returns:
            dict: Métriques d'exposition
        """
        try:
            if positions_df is None or positions_df.empty:
                return {
                    "long_exposure": 0,
                    "short_exposure": 0,
                    "net_exposure": 0,
                    "gross_exposure": 0,
                    "long_pct": 0,
                    "short_pct": 0
                }
            
            # Calculer l'exposition (en tenant compte du sens des positions)
            positions_df['exposure'] = positions_df.apply(
                lambda row: row['volume'] * row['price_current'] * (1 if row['type'] == 0 else -1),
                axis=1
            )
            
            # Calculer les expositions long et short
            long_exposure = positions_df[positions_df['exposure'] > 0]['exposure'].sum()
            short_exposure = positions_df[positions_df['exposure'] < 0]['exposure'].sum()
            
            # Calculer l'exposition nette et brute
            net_exposure = long_exposure + short_exposure
            gross_exposure = long_exposure - short_exposure
            
            # Calculer les pourcentages
            total_exposure = abs(long_exposure) + abs(short_exposure)
            if total_exposure > 0:
                long_pct = (long_exposure / total_exposure) * 100
                short_pct = (abs(short_exposure) / total_exposure) * 100
            else:
                long_pct = 0
                short_pct = 0
            
            return {
                "long_exposure": long_exposure,
                "short_exposure": short_exposure,
                "net_exposure": net_exposure,
                "gross_exposure": gross_exposure,
                "long_pct": long_pct,
                "short_pct": short_pct
            }
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de l'exposition du portefeuille")
            return {
                "long_exposure": 0,
                "short_exposure": 0,
                "net_exposure": 0,
                "gross_exposure": 0,
                "long_pct": 0,
                "short_pct": 0
            }
    
    def analyze_position_sizing(self, positions_df, account_equity):
        """
        Analyse le dimensionnement des positions
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            account_equity (float): Équité du compte
            
        Returns:
            dict: Métriques de dimensionnement
        """
        try:
            if positions_df is None or positions_df.empty or account_equity <= 0:
                return {
                    "avg_position_size_pct": 0,
                    "max_position_size_pct": 0,
                    "min_position_size_pct": 0,
                    "total_positions": 0,
                    "position_concentration": 0
                }
            
            # Calculer la taille des positions
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Calculer les pourcentages par rapport à l'équité
            positions_df['position_size_pct'] = (positions_df['position_size'] / account_equity) * 100
            
            # Calculer les métriques
            avg_position_size_pct = positions_df['position_size_pct'].mean()
            max_position_size_pct = positions_df['position_size_pct'].max()
            min_position_size_pct = positions_df['position_size_pct'].min()
            total_positions = len(positions_df)
            
            # Calculer la concentration des positions (HHI)
            position_sizes = positions_df['position_size']
            total_size = position_sizes.sum()
            
            if total_size > 0:
                position_weights = position_sizes / total_size
                position_concentration = (position_weights ** 2).sum()
            else:
                position_concentration = 0
            
            return {
                "avg_position_size_pct": avg_position_size_pct,
                "max_position_size_pct": max_position_size_pct,
                "min_position_size_pct": min_position_size_pct,
                "total_positions": total_positions,
                "position_concentration": position_concentration
            }
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'analyse du dimensionnement des positions")
            return {
                "avg_position_size_pct": 0,
                "max_position_size_pct": 0,
                "min_position_size_pct": 0,
                "total_positions": 0,
                "position_concentration": 0
            }
    
    def generate_allocation_recommendations(self, positions_df, account_equity, allocation_metrics=None, risk_metrics=None):
        """
        Génère des recommandations d'allocation
        
        Args:
            positions_df (pd.DataFrame): DataFrame des positions
            account_equity (float): Équité du compte
            allocation_metrics (dict, optional): Métriques d'allocation
            risk_metrics (dict, optional): Métriques de risque
            
        Returns:
            list: Liste de recommandations
        """
        try:
            if positions_df is None or positions_df.empty:
                return ["Aucune position ouverte pour analyse."]
            
            recommendations = []
            
            # 1. Analyser la concentration des positions
            position_sizing = self.analyze_position_sizing(positions_df, account_equity)
            if position_sizing["position_concentration"] > 0.25:  # HHI > 0.25 indique une forte concentration
                recommendations.append(
                    "Concentration élevée des positions. Envisagez de diversifier davantage pour réduire le risque spécifique."
                )
            
            # 2. Vérifier les positions surdimensionnées
            if position_sizing["max_position_size_pct"] > 10:  # Plus de 10% de l'équité
                # Trouver la position concernée
                positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
                positions_df['position_size_pct'] = (positions_df['position_size'] / account_equity) * 100
                
                max_pos = positions_df.loc[positions_df['position_size_pct'].idxmax()]
                
                recommendations.append(
                    f"Position surdimensionnée sur {max_pos['symbol']} ({max_pos['position_size_pct']:.1f}% de l'équité). "
                    f"Envisagez de réduire cette position pour diminuer le risque."
                )
            
            # 3. Vérifier l'équilibre long/short
            portfolio_exposure = self.calculate_portfolio_exposure(positions_df)
            if portfolio_exposure["long_pct"] > 80 or portfolio_exposure["short_pct"] > 80:
                dominant_dir = "LONG" if portfolio_exposure["long_pct"] > 80 else "SHORT"
                recommendations.append(
                    f"Exposition fortement déséquilibrée ({dominant_dir}: {portfolio_exposure['long_pct' if dominant_dir == 'LONG' else 'short_pct']:.1f}%). "
                    f"Envisagez d'ajouter des positions dans la direction opposée pour réduire le risque directionnel."
                )
            
            # 4. Vérifier la cohérence entre le style de trading et la durée des positions
            _, duration_pivot = self.analyze_duration_allocation(positions_df)
            
            if not duration_pivot.empty:
                scalping_pct = duration_pivot.loc["< 30 min (Scalping)"].sum() / duration_pivot.values.sum() * 100 if "< 30 min (Scalping)" in duration_pivot.index else 0
                swing_pct = duration_pivot.loc["> 24 h (Swing/Position)"].sum() / duration_pivot.values.sum() * 100 if "> 24 h (Swing/Position)" in duration_pivot.index else 0
                
                if scalping_pct > 50 and swing_pct > 30:
                    recommendations.append(
                        "Mélange incohérent de styles de trading: positions de scalping (court terme) et de swing (long terme) simultanées. "
                        "Envisagez de vous concentrer sur un style de trading plus cohérent."
                    )
            
            # 5. Recommandations basées sur les métriques de risque
            if risk_metrics and 'd_leverage' in risk_metrics:
                d_leverage = risk_metrics['d_leverage']
                
                # Analyser la durée moyenne des positions
                avg_duration = positions_df['duration_minutes'].mean() if 'duration_minutes' in positions_df.columns else 0
                
                if avg_duration < 30 and d_leverage > 16.25:  # Scalping
                    recommendations.append(
                        f"D-Leverage trop élevé ({d_leverage:.2f}) pour un style de trading intraday. "
                        f"Pour l'intraday (30-60min), maintenez un D-Leverage inférieur à 13."
                    )
                elif d_leverage > 9.75:  # Swing
                    recommendations.append(
                        f"D-Leverage trop élevé ({d_leverage:.2f}) pour un style de trading swing. "
                        f"Pour le swing (>60min), maintenez un D-Leverage inférieur à 9.75."
                    )
            
            # Retourner les recommandations ou un message par défaut
            if not recommendations:
                recommendations.append("L'allocation du portefeuille semble bien équilibrée. Aucune recommandation spécifique à ce stade.")
            
            return recommendations
            
        except Exception as e:
            self.logger.exception("Erreur lors de la génération des recommandations d'allocation")
            return ["Erreur lors de l'analyse d'allocation."]