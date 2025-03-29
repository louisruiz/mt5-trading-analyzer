#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gestionnaire de données pour l'application MT5 Trading Analyzer
Centralise l'accès et la mise à jour des données
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.mt5_connector import MT5Connector

class DataManager:
    """
    Classe de gestion des données de trading
    Agit comme une couche d'abstraction entre l'interface utilisateur et les données MT5
    """
    
    def __init__(self):
        """Initialisation du gestionnaire de données"""
        self.logger = logging.getLogger(__name__)
        self.mt5_connector = MT5Connector()
        
        # Données en cache
        self.account_info = None
        self.positions = None
        self.historical_deals = None
        self.historical_orders = None
        self.equity_data = None
        
        # État de connexion
        self.connected = False
    
    def connect_to_mt5(self):
        """Établit la connexion à MT5"""
        success, message = self.mt5_connector.connect()
        if success:
            self.connected = True
            self.account_info = self.mt5_connector.account_info
            # Initial data loading
            self.refresh_all_data()
        return success, message
    
    def disconnect(self):
        """Ferme la connexion à MT5"""
        self.mt5_connector.disconnect()
        self.connected = False
    
    def refresh_all_data(self):
        """Rafraîchit toutes les données"""
        if not self.connected:
            self.logger.warning("Tentative de rafraîchissement des données sans connexion MT5")
            return False
        
        try:
            self.refresh_account_info()
            self.refresh_positions()
            self.refresh_historical_deals()
            self.refresh_historical_orders()
            self.calculate_equity_curve()
            return True
        except Exception as e:
            self.logger.exception("Erreur lors du rafraîchissement des données")
            return False
    
    def refresh_account_info(self):
        """Rafraîchit les informations du compte"""
        if not self.connected:
            return None
        
        self.account_info = self.mt5_connector.refresh_account_info()
        return self.account_info
    
    def refresh_positions(self):
        """Rafraîchit les positions ouvertes"""
        if not self.connected:
            return None
        
        self.positions = self.mt5_connector.get_positions()
        return self.positions
    
    def refresh_historical_deals(self, days=90):
        """Rafraîchit l'historique des transactions"""
        if not self.connected:
            return None
        
        self.historical_deals = self.mt5_connector.get_historical_deals(days)
        return self.historical_deals
    
    def refresh_historical_orders(self, days=90):
        """Rafraîchit l'historique des ordres"""
        if not self.connected:
            return None
        
        self.historical_orders = self.mt5_connector.get_historical_orders(days)
        return self.historical_orders
    
    def calculate_equity_curve(self, days=90):
        """Calcule la courbe d'équité basée sur l'historique des transactions"""
        if not self.connected or self.historical_deals is None or self.historical_deals.empty:
            return None
        
        try:
            # Définir la période
            now = datetime.now()
            from_date = now - timedelta(days=days)
            
            # Calculer l'équité cumulée
            if self.account_info:
                initial_balance = self.account_info.balance - self.historical_deals['profit'].sum()
            else:
                # Fallback si account_info n'est pas disponible
                initial_balance = self.historical_deals['profit'].sum()
            
            # Créer un DataFrame avec les deals
            deals_df = self.historical_deals.copy()
            deals_df['equity'] = initial_balance + deals_df['profit'].cumsum()
            
            # Créer des données journalières
            dates = pd.date_range(start=from_date, end=now, freq='D')
            equity_series = pd.Series(index=dates, dtype=float)
            
            # Remplir avec la dernière valeur connue pour chaque jour
            for date in dates:
                mask = deals_df['time'] <= date
                if mask.any():
                    equity_series[date] = deals_df.loc[mask, 'equity'].iloc[-1]
                else:
                    equity_series[date] = initial_balance
            
            # Stocker les données d'équité
            self.equity_data = equity_series
            
            return self.equity_data
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la courbe d'équité")
            return None
    
    def get_current_margin_percentage(self):
        """Calcule le pourcentage de marge utilisée"""
        if not self.connected or not self.account_info:
            return 0
        
        try:
            if hasattr(self.account_info, 'margin_free') and self.account_info.margin_free > 0:
                return (self.account_info.margin / self.account_info.margin_free) * 100
            return 0
        except:
            return 0
    
    def get_margin_level(self):
        """Calcule le niveau de marge"""
        if not self.connected or not self.account_info:
            return 0
        
        try:
            if hasattr(self.account_info, "margin_level"):
                return self.account_info.margin_level
            elif self.account_info.margin > 0:
                return (self.account_info.equity / self.account_info.margin * 100)
            return 0
        except:
            return 0
    
    def calculate_d_leverage(self):
        """Calcule le D-Leverage approximatif"""
        if not self.connected or not self.account_info or self.positions is None or self.positions.empty:
            return 0
        
        try:
            total_volume = self.positions['volume'].sum()
            if self.account_info.equity > 0:
                return (total_volume * 100000) / self.account_info.equity
            return 0
        except:
            return 0
    
    def calculate_positions_volatility(self):
        """Calcule la volatilité du portefeuille basée sur les positions ouvertes"""
        if not self.connected or not self.account_info or self.positions is None or self.positions.empty:
            return 0
        
        try:
            total_equity = self.account_info.equity
            if total_equity <= 0:
                return 0
            
            # Calculer la volatilité pour chaque position
            volatility_contributions = []
            total_exposure = 0
            
            for _, position in self.positions.iterrows():
                symbol = position['symbol']
                volume = position['volume']
                
                # Obtenir les données historiques récentes
                rates_df = self.mt5_connector.get_historical_data(symbol, count=30)
                if rates_df is None or len(rates_df) < 5:
                    continue
                
                rates_df['returns'] = rates_df['close'].pct_change().dropna()
                
                # Calculer la volatilité quotidienne
                daily_volatility = rates_df['returns'].std() * 100  # en pourcentage
                
                # Estimer l'exposition en devise de base
                symbol_info = self.mt5_connector.get_symbol_info(symbol)
                if symbol_info:
                    contract_size = symbol_info.trade_contract_size
                    exposure = volume * contract_size * position['price_current']
                    total_exposure += exposure
                    
                    # Contribution à la volatilité
                    volatility_contributions.append((exposure, daily_volatility))
            
            # Calculer la volatilité du portefeuille pondérée par l'exposition
            if total_exposure > 0 and volatility_contributions:
                weighted_volatility = sum(exposure / total_exposure * vol for exposure, vol in volatility_contributions)
                portfolio_ratio = total_exposure / total_equity
                return weighted_volatility * portfolio_ratio
            
            return 0
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la volatilité des positions")
            return 0
    
    def calculate_monthly_var(self):
        """Calcule la VaR mensuelle approximative (méthode simple)"""
        if not self.connected:
            return 0
        
        try:
            positions_volatility = self.calculate_positions_volatility()
            # 95% de confiance, 22 jours de trading
            monthly_var = positions_volatility * 1.65 * np.sqrt(22)
            return monthly_var
        except:
            return 0
    
    def get_average_position_duration(self):
        """Calcule la durée moyenne des positions ouvertes"""
        if not self.connected or self.positions is None or self.positions.empty:
            return 0
        
        try:
            now = datetime.now()
            durations = []
            
            for _, position in self.positions.iterrows():
                if 'time' in position:
                    position_time = datetime.fromtimestamp(position['time'])
                    duration_minutes = (now - position_time).total_seconds() / 60
                    durations.append(duration_minutes)
            
            if durations:
                return sum(durations) / len(durations)
            return 0
        except:
            return 0