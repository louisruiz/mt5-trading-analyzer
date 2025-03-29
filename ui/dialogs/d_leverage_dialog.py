#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Boîte de dialogue d'optimisation D-Leverage pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime
from utils.constants import TRADING_CATEGORIES

class DLeverageDialog:
    """Boîte de dialogue d'optimisation du D-Leverage"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation de la boîte de dialogue D-Leverage
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        # Création de la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("D-Leverage Optimizer")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)  # Dialogue modal
        self.dialog.grab_set()
        
        # Centrer la fenêtre
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        self.create_widgets()
        
        # Attendre la fermeture de la fenêtre
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Création des widgets pour la boîte de dialogue"""
        # Titre et description
        ttk.Label(self.dialog, text="D-Leverage Optimizer", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        info_text = (
            "Cet outil vous permet d'optimiser automatiquement la taille des positions pour maintenir "
            "un D-Leverage idéal selon la durée des trades:\n\n"
            "• Scalping (<30min): D-Leverage max de 16.25\n"
            "• Intraday (30-60min): D-Leverage max de 13\n"
            "• Swing (>60min): D-Leverage max de 9.75\n\n"
            "L'algorithme surveillera constamment le D-Leverage global du portefeuille et ajustera "
            "automatiquement la taille des positions en fonction de ces seuils."
        )
        
        info_label = ttk.Label(self.dialog, text=info_text, wraplength=550, justify="left")
        info_label.pack(padx=20, pady=10, fill=tk.X)
        
        # Frame pour les positions actuelles
        positions_frame = ttk.LabelFrame(self.dialog, text="Positions actuelles")
        positions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Calculer les métriques actuelles
        self.calculate_current_metrics(positions_frame)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Bouton Fermer
        close_button = ttk.Button(button_frame, text="Fermer", command=self.dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)
        
        # Bouton Appliquer (désactivé car fonctionnalité future)
        apply_button = ttk.Button(button_frame, text="Appliquer les recommandations", state="disabled")
        apply_button.pack(side=tk.RIGHT, padx=10)
    
    def calculate_current_metrics(self, parent_frame):
        """
        Calcule et affiche les métriques actuelles de D-Leverage
        
        Args:
            parent_frame: Frame parent pour l'affichage
        """
        try:
            # Vérifier si des positions sont ouvertes
            if self.data_manager.positions is None or self.data_manager.positions.empty:
                ttk.Label(parent_frame, text="Aucune position ouverte").pack(anchor=tk.W, padx=10, pady=10)
                return
            
            # Calculer le D-Leverage actuel
            d_leverage = self.data_manager.calculate_d_leverage()
            
            # Déterminer la durée moyenne des positions
            avg_duration = self.data_manager.get_average_position_duration()
            
            # Déterminer la catégorie et le D-Leverage cible
            if avg_duration < 30:  # Scalping
                target_d_leverage = TRADING_CATEGORIES["Scalping"]["max_d_leverage"]
                category = "Scalping (<30min)"
            elif avg_duration < 60:  # Intraday
                target_d_leverage = TRADING_CATEGORIES["Intraday"]["max_d_leverage"]
                category = "Intraday (30-60min)"
            else:  # Swing
                target_d_leverage = TRADING_CATEGORIES["Swing"]["max_d_leverage"]
                category = "Swing (>60min)"
            
            # Afficher les informations
            ttk.Label(parent_frame, text=f"D-Leverage actuel: {d_leverage:.2f}").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(parent_frame, text=f"Durée moyenne des positions: {avg_duration:.1f} minutes").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(parent_frame, text=f"Catégorie détectée: {category}").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(parent_frame, text=f"D-Leverage cible recommandé: {target_d_leverage}").pack(anchor=tk.W, padx=10, pady=2)
            
            # Proposer des ajustements si nécessaire
            if d_leverage > target_d_leverage:
                reduction_needed = (d_leverage - target_d_leverage) / d_leverage
                ttk.Label(parent_frame, 
                          text=f"Réduction recommandée: {reduction_needed*100:.1f}% du volume total", 
                          foreground="red").pack(anchor=tk.W, padx=10, pady=5)
                
                # Créer un frame pour la table des suggestions
                suggestions_frame = ttk.Frame(parent_frame)
                suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
                
                # Titre pour les suggestions
                ttk.Label(suggestions_frame, text="Suggestions de réduction par position:", 
                          font=("TkDefaultFont", 9, "bold")).pack(anchor=tk.W, pady=5)
                
                # Créer un tableau pour les suggestions
                columns = ("symbol", "current", "new", "reduction")
                suggestions_tree = ttk.Treeview(suggestions_frame, columns=columns, show='headings', height=6)
                
                suggestions_tree.heading("symbol", text="Symbole")
                suggestions_tree.heading("current", text="Volume actuel")
                suggestions_tree.heading("new", text="Volume recommandé")
                suggestions_tree.heading("reduction", text="Réduction")
                
                suggestions_tree.column("symbol", width=100)
                suggestions_tree.column("current", width=100)
                suggestions_tree.column("new", width=130)
                suggestions_tree.column("reduction", width=100)
                
                suggestions_tree.pack(fill=tk.BOTH, expand=True)
                
                # Ajouter les suggestions pour chaque position
                for _, position in self.data_manager.positions.iterrows():
                    symbol = position["symbol"]
                    current_volume = position["volume"]
                    new_volume = current_volume * (1 - reduction_needed)
                    vol_reduction = current_volume - new_volume
                    
                    suggestions_tree.insert("", tk.END, values=(
                        symbol,
                        f"{current_volume:.2f} lots",
                        f"{new_volume:.2f} lots",
                        f"-{vol_reduction:.2f} lots"
                    ))
            else:
                ttk.Label(parent_frame, 
                          text="Le D-Leverage actuel est dans les limites recommandées.", 
                          foreground="green").pack(anchor=tk.W, padx=10, pady=5)
                
        except Exception as e:
            self.logger.exception("Erreur lors du calcul des métriques de D-Leverage")
            ttk.Label(parent_frame, text=f"Erreur lors du calcul: {str(e)}").pack(anchor=tk.W, padx=10, pady=10)