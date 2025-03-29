#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget des alertes et optimisations pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime

class AlertsWidget(ttk.Frame):
    """Widget affichant les alertes de risque et les suggestions d'optimisation"""
    
    def __init__(self, parent, data_manager, config_manager):
        """
        Initialisation du widget des alertes
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
            config_manager (ConfigManager): Instance du gestionnaire de configuration
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.config_manager = config_manager
        
        # Charger les seuils d'alerte
        self.load_thresholds()
        
        self.create_widgets()
    
    def load_thresholds(self):
        """Charge les seuils d'alerte depuis la configuration"""
        try:
            self.alert_thresholds = self.config_manager.get_alert_thresholds()
        except Exception as e:
            self.logger.exception("Erreur lors du chargement des seuils d'alerte")
            # Valeurs par défaut en cas d'erreur
            self.alert_thresholds = {
                'margin_pct': 50,
                'daily_loss': -5,
                'drawdown': -15,
                'd_leverage': 16.25,
                'var_monthly': 12,
                'correlation': 0.8,
                'sector_concentration': 30
            }
    
    def create_widgets(self):
        """Création des widgets pour l'affichage des alertes et suggestions"""
        # Panneau principal
        main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les alertes
        alerts_frame = ttk.LabelFrame(main_paned, text="Alertes de risque")
        main_paned.add(alerts_frame, weight=1)
        
        # Tableau des alertes
        columns = ("timestamp", "type", "message", "value")
        self.alerts_tree = ttk.Treeview(alerts_frame, columns=columns, show='headings', height=5)
        
        self.alerts_tree.heading("timestamp", text="Horodatage")
        self.alerts_tree.heading("type", text="Type")
        self.alerts_tree.heading("message", text="Message")
        self.alerts_tree.heading("value", text="Valeur")
        
        self.alerts_tree.column("timestamp", width=150)
        self.alerts_tree.column("type", width=100)
        self.alerts_tree.column("message", width=300)
        self.alerts_tree.column("value", width=100)
        
        # Ajout de la barre de défilement
        scrollbar = ttk.Scrollbar(alerts_frame, orient="vertical", command=self.alerts_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)
        
        self.alerts_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les optimisations
        optim_frame = ttk.LabelFrame(main_paned, text="Optimisations suggérées")
        main_paned.add(optim_frame, weight=1)
        
        # Zone de texte pour les optimisations
        self.optim_text = tk.Text(optim_frame, height=10, wrap=tk.WORD)
        
        # Ajout de la barre de défilement
        optim_scrollbar = ttk.Scrollbar(optim_frame, orient="vertical", command=self.optim_text.yview)
        optim_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.optim_text.configure(yscrollcommand=optim_scrollbar.set)
        
        self.optim_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update(self):
        """Met à jour les alertes et optimisations"""
        if not self.data_manager.connected:
            return
        
        try:
            # Vérifier les alertes
            self.check_alerts()
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des alertes")
    
    def check_alerts(self):
        """Vérifie et génère les alertes de risque"""
        try:
            # Obtenir les informations actuelles
            account_info = self.data_manager.account_info
            if not account_info:
                return
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Vérifier le niveau de marge
            margin_pct = self.data_manager.get_current_margin_percentage()
            if margin_pct > self.alert_thresholds['margin_pct']:
                self.add_alert(current_time, "RISQUE", "Niveau de marge élevé", f"{margin_pct:.1f}%")
                self.suggest_optimization("RÉDUCTION DE MARGE", 
                    f"Le niveau de marge actuel ({margin_pct:.1f}%) dépasse le seuil recommandé de {self.alert_thresholds['margin_pct']}%. "
                    f"Envisagez de réduire les positions ou d'augmenter votre capital pour améliorer votre sécurité de trading.")
            
            # Vérifier le D-Leverage
            d_leverage = self.data_manager.calculate_d_leverage()
            if d_leverage > self.alert_thresholds['d_leverage']:
                self.add_alert(current_time, "RISQUE", "D-Leverage élevé", f"{d_leverage:.2f}")
                
                # Déterminer le D-Leverage cible selon la durée moyenne des positions
                avg_duration = self.data_manager.get_average_position_duration()
                
                if avg_duration < 30:  # Scalping
                    target_d_leverage = 16.25
                    category = "Scalping (<30min)"
                elif avg_duration < 60:  # Intraday
                    target_d_leverage = 13
                    category = "Intraday (30-60min)"
                else:  # Swing
                    target_d_leverage = 9.75
                    category = "Swing (>60min)"
                
                if d_leverage > target_d_leverage:
                    reduction_needed = (d_leverage - target_d_leverage) / d_leverage * 100
                    self.suggest_optimization("OPTIMISATION D-LEVERAGE", 
                        f"Votre D-Leverage actuel ({d_leverage:.2f}) dépasse le seuil recommandé de {target_d_leverage} "
                        f"pour la durée moyenne de vos positions ({avg_duration:.0f} min - {category}). "
                        f"Une réduction d'environ {reduction_needed:.1f}% du volume total serait nécessaire pour atteindre le niveau optimal. "
                        f"Réduisez progressivement vos positions pour éviter une exposition excessive au risque.")
            
            # Vérifier la VaR mensuelle
            monthly_var = self.data_manager.calculate_monthly_var()
            if monthly_var > self.alert_thresholds['var_monthly']:
                self.add_alert(current_time, "RISQUE", "VaR mensuelle élevée", f"{monthly_var:.2f}%")
                self.suggest_optimization("RÉDUCTION DE LA VAR", 
                    f"Votre VaR mensuelle ({monthly_var:.2f}%) est supérieure au seuil configuré de {self.alert_thresholds['var_monthly']}%. "
                    f"Envisagez de diversifier davantage votre portefeuille ou de réduire l'exposition sur les instruments volatils.")
            
            # TODO: Ajouter d'autres vérifications (perte quotidienne, drawdown, etc.)
            
        except Exception as e:
            self.logger.exception("Erreur lors de la vérification des alertes")
    
    def add_alert(self, timestamp, alert_type, message, value):
        """
        Ajoute une alerte à la liste
        
        Args:
            timestamp (str): Horodatage de l'alerte
            alert_type (str): Type d'alerte
            message (str): Message de l'alerte
            value (str): Valeur associée à l'alerte
        """
        try:
            # Insérer en haut de la liste
            self.alerts_tree.insert("", 0, values=(timestamp, alert_type, message, value))
            
            # Colorer selon le type d'alerte
            if alert_type == "RISQUE":
                self.alerts_tree.item(self.alerts_tree.get_children()[0], tags=("risk",))
            elif alert_type == "ATTENTION":
                self.alerts_tree.item(self.alerts_tree.get_children()[0], tags=("warning",))
            elif alert_type == "INFO":
                self.alerts_tree.item(self.alerts_tree.get_children()[0], tags=("info",))
            
            # Configurer les tags pour la coloration
            self.alerts_tree.tag_configure("risk", foreground="red")
            self.alerts_tree.tag_configure("warning", foreground="orange")
            self.alerts_tree.tag_configure("info", foreground="blue")
            
            # Limiter le nombre d'alertes affichées
            if len(self.alerts_tree.get_children()) > 50:
                last = self.alerts_tree.get_children()[-1]
                self.alerts_tree.delete(last)
        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout d'une alerte")
    
    def suggest_optimization(self, title, message):
        """
        Ajoute une suggestion d'optimisation
        
        Args:
            title (str): Titre de la suggestion
            message (str): Message détaillé de la suggestion
        """
        try:
            # Insérer au début avec timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"[{timestamp}] {title}:\n{message}\n\n"
            
            self.optim_text.insert("1.0", full_message)
            
            # Limiter la taille du texte (conserver les 10 dernières suggestions)
            all_text = self.optim_text.get("1.0", tk.END)
            suggestions = all_text.split("\n\n")
            
            if len(suggestions) > 10:
                # Reconstruire le texte avec seulement les 10 premières suggestions
                new_text = "\n\n".join(suggestions[:10])
                self.optim_text.delete("1.0", tk.END)
                self.optim_text.insert("1.0", new_text)
            
            # Appliquer des tags pour la mise en forme
            self.optim_text.tag_add("title", "1.0", f"1.{len(timestamp) + len(title) + 3}")
            self.optim_text.tag_configure("title", font=('TkDefaultFont', 9, 'bold'))
            
        except Exception as e:
            self.logger.exception("Erreur lors de l'ajout d'une suggestion d'optimisation")
    
    def clear_alerts(self):
        """Efface toutes les alertes"""
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
    
    def clear_optimizations(self):
        """Efface toutes les suggestions d'optimisation"""
        self.optim_text.delete("1.0", tk.END)