#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget des positions ouvertes pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime
from utils.helpers import format_currency, format_timespan

class PositionsWidget(ttk.Frame):
    """Widget affichant les positions ouvertes MT5"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget des positions
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage des positions"""
        # Frame de contrôle pour les filtres et options
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label et combobox pour le filtre de symbole
        ttk.Label(control_frame, text="Filtre symbole:").pack(side=tk.LEFT, padx=5)
        self.symbol_var = tk.StringVar(value="Tous")
        self.symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, width=15)
        self.symbol_combo.pack(side=tk.LEFT, padx=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.filter_positions)
        
        # Label et combobox pour le filtre de type
        ttk.Label(control_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="Tous")
        self.type_combo = ttk.Combobox(control_frame, textvariable=self.type_var, 
                                      values=["Tous", "BUY", "SELL"], width=10)
        self.type_combo.pack(side=tk.LEFT, padx=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.filter_positions)
        
        # Bouton pour rafraîchir les positions
        refresh_button = ttk.Button(control_frame, text="Rafraîchir", command=self.update)
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Affichage du nombre de positions
        self.positions_count_label = ttk.Label(control_frame, text="0 position(s)")
        self.positions_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Création du tableau des positions
        columns = ("symbol", "type", "volume", "open_price", "current_price", 
                  "profit", "swap", "time")
        
        self.positions_tree = ttk.Treeview(self, columns=columns, show='headings', height=10)
        
        # Définition des en-têtes
        self.positions_tree.heading("symbol", text="Symbole")
        self.positions_tree.heading("type", text="Type")
        self.positions_tree.heading("volume", text="Volume")
        self.positions_tree.heading("open_price", text="Prix d'ouverture")
        self.positions_tree.heading("current_price", text="Prix actuel")
        self.positions_tree.heading("profit", text="Profit")
        self.positions_tree.heading("swap", text="Swap")
        self.positions_tree.heading("time", text="Temps ouvert")
        
        # Définition des largeurs de colonnes
        self.positions_tree.column("symbol", width=80)
        self.positions_tree.column("type", width=60)
        self.positions_tree.column("volume", width=60)
        self.positions_tree.column("open_price", width=100)
        self.positions_tree.column("current_price", width=100)
        self.positions_tree.column("profit", width=80)
        self.positions_tree.column("swap", width=80)
        self.positions_tree.column("time", width=120)
        
        # Création de la barre de défilement
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.positions_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.positions_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement du tableau
        self.positions_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Binding pour les événements de clic sur une position
        self.positions_tree.bind("<Double-1>", self.on_position_double_click)
        
        # Stockage interne des positions
        self.positions_data = None
    
    def update(self):
        """Met à jour la liste des positions ouvertes"""
        if not self.data_manager.connected:
            self.clear_positions()
            return
        
        try:
            # Rafraîchir les positions depuis le gestionnaire de données
            self.data_manager.refresh_positions()
            self.positions_data = self.data_manager.positions
            
            # Mettre à jour la liste des symboles disponibles
            if self.positions_data is not None and not self.positions_data.empty:
                # Obtenir la liste unique des symboles
                symbols = ["Tous"] + sorted(self.positions_data["symbol"].unique().tolist())
                self.symbol_combo["values"] = symbols
            else:
                self.symbol_combo["values"] = ["Tous"]
            
            # Filtrer et afficher les positions
            self.filter_positions()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des positions")
            self.clear_positions()
    
    def filter_positions(self, event=None):
        """
        Filtre et affiche les positions selon les critères sélectionnés
        
        Args:
            event: Événement Tkinter (non utilisé directement)
        """
        # Effacer les positions actuelles
        self.clear_positions_tree()
        
        if self.positions_data is None or self.positions_data.empty:
            self.positions_count_label.config(text="0 position(s)")
            return
        
        try:
            # Copier les données pour filtrage
            filtered_positions = self.positions_data.copy()
            
            # Filtrer par symbole si nécessaire
            if self.symbol_var.get() != "Tous":
                filtered_positions = filtered_positions[filtered_positions["symbol"] == self.symbol_var.get()]
            
            # Filtrer par type si nécessaire
            if self.type_var.get() != "Tous":
                if self.type_var.get() == "BUY":
                    filtered_positions = filtered_positions[filtered_positions["type"] == 0]
                else:  # SELL
                    filtered_positions = filtered_positions[filtered_positions["type"] == 1]
            
            # Mettre à jour le nombre de positions
            count = len(filtered_positions)
            self.positions_count_label.config(text=f"{count} position(s)")
            
            # Obtenir la devise du compte pour le formatage
            currency = self.data_manager.account_info.currency if self.data_manager.account_info else ""
            
            # Remplir le tableau avec les positions filtrées
            now = datetime.now()
            for _, position in filtered_positions.iterrows():
                # Déterminer le type de position
                position_type = "BUY" if position["type"] == 0 else "SELL"
                
                # Calculer la durée d'ouverture
                if "time" in position:
                    open_time = datetime.fromtimestamp(position["time"])
                    time_diff = (now - open_time).total_seconds()
                    duration = format_timespan(time_diff)
                else:
                    duration = "-"
                
                # Insérer la position dans le tableau
                item_id = self.positions_tree.insert("", tk.END, values=(
                    position["symbol"],
                    position_type,
                    f"{position['volume']:.2f}",
                    f"{position['price_open']:.5f}",
                    f"{position['price_current']:.5f}",
                    format_currency(position["profit"], currency, include_sign=True),
                    format_currency(position["swap"], currency),
                    duration
                ))
                
                # Appliquer une couleur selon le profit
                if position["profit"] > 0:
                    self.positions_tree.item(item_id, tags=("profit",))
                elif position["profit"] < 0:
                    self.positions_tree.item(item_id, tags=("loss",))
            
            # Configurer les tags pour la coloration
            self.positions_tree.tag_configure("profit", foreground="green")
            self.positions_tree.tag_configure("loss", foreground="red")
            
        except Exception as e:
            self.logger.exception("Erreur lors du filtrage des positions")
    
    def clear_positions_tree(self):
        """Efface le tableau des positions"""
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
    
    def clear_positions(self):
        """Réinitialise complètement le widget des positions"""
        self.clear_positions_tree()
        self.positions_data = None
        self.positions_count_label.config(text="0 position(s)")
        self.symbol_combo["values"] = ["Tous"]
    
    def on_position_double_click(self, event):
        """
        Gère le double clic sur une position
        
        Args:
            event: Événement Tkinter
        """
        try:
            # Récupérer l'identifiant de l'élément sélectionné
            item_id = self.positions_tree.selection()[0]
            
            # Récupérer les valeurs de l'élément
            values = self.positions_tree.item(item_id, "values")
            
            # Récupérer le symbole de la position
            symbol = values[0]
            
            # Afficher les détails de la position (à implémenter)
            self.show_position_details(symbol)
            
        except IndexError:
            # Aucun élément sélectionné
            pass
        except Exception as e:
            self.logger.exception("Erreur lors du traitement du double clic sur une position")
    
    def show_position_details(self, symbol):
        """
        Affiche les détails d'une position
        
        Args:
            symbol (str): Symbole de la position
        """
        # Cette méthode sera implémentée ultérieurement
        # Elle pourrait ouvrir une fenêtre de dialogue avec plus de détails sur la position
        self.logger.info(f"Affichage des détails de la position pour {symbol} (non implémenté)")
        
        # TODO: Implémenter l'affichage des détails de position