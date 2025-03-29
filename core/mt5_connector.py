#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de connexion à MetaTrader 5
Gère la connexion, l'initialisation et les requêtes MT5
"""

import logging
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pytz
import pandas as pd

class MT5Connector:
    """Classe de gestion de la connexion à MetaTrader 5"""
    
    def __init__(self):
        """Initialisation de la connexion MT5"""
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.account_info = None
        self.timezone = pytz.timezone("Etc/UTC")
    
    def connect(self):
        """Établit la connexion à MetaTrader 5"""
        try:
            # Initialisation de MT5
            if not mt5.initialize():
                error = mt5.last_error()
                self.logger.error(f"Échec d'initialisation de MT5: {error}")
                return False, f"Erreur d'initialisation MT5: {error}"
            
            # Vérifier si le terminal est disponible
            if not mt5.terminal_info():
                self.logger.error("Terminal MT5 non trouvé")
                return False, "Terminal MT5 non trouvé"
            
            # Obtenir les informations du compte
            self.account_info = mt5.account_info()
            if not self.account_info:
                error = mt5.last_error()
                self.logger.error(f"Échec d'obtention des informations du compte: {error}")
                return False, f"Échec d'obtention des informations du compte: {error}"
            
            self.connected = True
            self.logger.info(f"Connecté au compte MT5 {self.account_info.login} ({self.account_info.server})")
            return True, f"Connecté au compte {self.account_info.login} ({self.account_info.server})"
            
        except Exception as e:
            self.logger.exception("Erreur lors de la connexion à MT5")
            return False, f"Erreur de connexion: {str(e)}"
    
    def disconnect(self):
        """Ferme la connexion à MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.account_info = None
            self.logger.info("Déconnecté de MT5")
    
    def refresh_account_info(self):
        """Rafraîchit les informations du compte"""
        if not self.connected:
            return None
        
        try:
            self.account_info = mt5.account_info()
            return self.account_info
        except Exception as e:
            self.logger.exception("Erreur lors du rafraîchissement des informations du compte")
            return None
    
    def get_positions(self):
        """Récupère les positions ouvertes"""
        if not self.connected:
            return None
        
        try:
            positions = mt5.positions_get()
            if positions:
                # Convertir en DataFrame
                return pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
            return pd.DataFrame()
        except Exception as e:
            self.logger.exception("Erreur lors de la récupération des positions")
            return None
    
    def get_historical_deals(self, days=90):
        """Récupère l'historique des transactions sur une période donnée"""
        if not self.connected:
            return None
        
        try:
            # Définir la période
            now = datetime.now()
            from_date = now - timedelta(days=days)
            
            # Localiser les dates avec le fuseau horaire
            from_date = self.timezone.localize(from_date)
            to_date = self.timezone.localize(now)
            
            # Récupérer l'historique
            deals = mt5.history_deals_get(from_date, to_date)
            if deals:
                # Convertir en DataFrame
                deals_df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
                
                # Convertir les timestamps en datetime
                deals_df['time'] = pd.to_datetime(deals_df['time'], unit='s')
                deals_df.sort_values('time', inplace=True)
                
                return deals_df
                
            return pd.DataFrame()
        except Exception as e:
            self.logger.exception("Erreur lors de la récupération de l'historique des transactions")
            return None
    
    def get_historical_orders(self, days=90):
        """Récupère l'historique des ordres sur une période donnée"""
        if not self.connected:
            return None
        
        try:
            # Définir la période
            now = datetime.now()
            from_date = now - timedelta(days=days)
            
            # Localiser les dates avec le fuseau horaire
            from_date = self.timezone.localize(from_date)
            to_date = self.timezone.localize(now)
            
            # Récupérer l'historique
            orders = mt5.history_orders_get(from_date, to_date)
            if orders:
                # Convertir en DataFrame
                orders_df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
                
                # Convertir les timestamps en datetime
                orders_df['time_setup'] = pd.to_datetime(orders_df['time_setup'], unit='s')
                orders_df.sort_values('time_setup', inplace=True)
                
                return orders_df
                
            return pd.DataFrame()
        except Exception as e:
            self.logger.exception("Erreur lors de la récupération de l'historique des ordres")
            return None
    
    def get_symbol_info(self, symbol):
        """Récupère les informations d'un symbole"""
        if not self.connected:
            return None
        
        try:
            return mt5.symbol_info(symbol)
        except Exception as e:
            self.logger.exception(f"Erreur lors de la récupération des informations du symbole {symbol}")
            return None
    
    def get_historical_data(self, symbol, timeframe=mt5.TIMEFRAME_D1, count=100):
        """Récupère les données historiques d'un symbole"""
        if not self.connected:
            return None
        
        try:
            # Récupérer les données historiques
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is not None:
                # Convertir en DataFrame
                df = pd.DataFrame(rates)
                # Convertir le temps en datetime
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
            return None
        except Exception as e:
            self.logger.exception(f"Erreur lors de la récupération des données historiques pour {symbol}")
            return None