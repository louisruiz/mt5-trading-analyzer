#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget d'informations du compte pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from utils.helpers import format_currency, format_percentage

class AccountInfoWidget(ttk.LabelFrame):
    """Widget affichant les informations du compte MT5"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget d'informations du compte
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent, text="Informations du compte", padding=10)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage des informations du compte"""
        # Division en deux colonnes
        account_left_frame = ttk.Frame(self)
        account_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        account_right_frame = ttk.Frame(self)
        account_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Colonne gauche - Informations basiques
        self.account_label = ttk.Label(account_left_frame, text="Non connecté")
        self.account_label.pack(anchor=tk.W, pady=2)
        
        self.balance_label = ttk.Label(account_left_frame, text="Balance: -")
        self.balance_label.pack(anchor=tk.W, pady=2)
        
        self.equity_label = ttk.Label(account_left_frame, text="Équité: -")
        self.equity_label.pack(anchor=tk.W, pady=2)
        
        self.profit_label = ttk.Label(account_left_frame, text="Profit flottant: -")
        self.profit_label.pack(anchor=tk.W, pady=2)
        
        # Colonne droite - Informations de marge et risque
        self.margin_label = ttk.Label(account_right_frame, text="Marge utilisée: -")
        self.margin_label.pack(anchor=tk.W, pady=2)
        
        self.margin_level_label = ttk.Label(account_right_frame, text="Niveau de marge: -")
        self.margin_level_label.pack(anchor=tk.W, pady=2)
        
        self.d_leverage_label = ttk.Label(account_right_frame, text="D-Leverage: -")
        self.d_leverage_label.pack(anchor=tk.W, pady=2)
        
        self.var_label = ttk.Label(account_right_frame, text="VaR mensuelle: -")
        self.var_label.pack(anchor=tk.W, pady=2)
    
    def update(self):
        """Met à jour les informations du compte"""
        if not self.data_manager.connected or not self.data_manager.account_info:
            self.reset_labels()
            return
        
        try:
            # Informations de base
            account_info = self.data_manager.account_info
            currency = account_info.currency
            
            # Mise à jour des labels d'information de base
            self.account_label.config(text=f"Compte: {account_info.login} ({account_info.server})")
            self.balance_label.config(text=f"Balance: {format_currency(account_info.balance, currency)}")
            self.equity_label.config(text=f"Équité: {format_currency(account_info.equity, currency)}")
            
            # Calcul des profits
            self.profit_label.config(text=f"Profit flottant: {format_currency(account_info.profit, currency, include_sign=True)}")
            
            # Informations de marge
            margin_pct = self.data_manager.get_current_margin_percentage()
            self.margin_label.config(text=f"Marge utilisée: {format_currency(account_info.margin, currency)} ({format_percentage(margin_pct)})")
            
            margin_level = self.data_manager.get_margin_level()
            self.margin_level_label.config(text=f"Niveau de marge: {format_percentage(margin_level)}")
            
            # D-Leverage
            d_leverage = self.data_manager.calculate_d_leverage()
            self.d_leverage_label.config(text=f"D-Leverage: {d_leverage:.2f}")
            
            # VaR mensuelle
            monthly_var = self.data_manager.calculate_monthly_var()
            self.var_label.config(text=f"VaR mensuelle: {format_percentage(monthly_var)}")
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des informations du compte")
            self.reset_labels()
    
    def reset_labels(self):
        """Réinitialise les labels avec des valeurs par défaut"""
        self.account_label.config(text="Non connecté")
        self.balance_label.config(text="Balance: -")
        self.equity_label.config(text="Équité: -")
        self.profit_label.config(text="Profit flottant: -")
        self.margin_label.config(text="Marge utilisée: -")
        self.margin_level_label.config(text="Niveau de marge: -")
        self.d_leverage_label.config(text="D-Leverage: -")
        self.var_label.config(text="VaR mensuelle: -")