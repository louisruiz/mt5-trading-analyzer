#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget des statistiques de performance pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
from analysis.performance_metrics import PerformanceMetrics
from analysis.metrics_interpreter import MetricsInterpreter
from utils.helpers import format_percentage
from ui.widgets.tooltip_widget import AdvancedTooltip

class PerformanceWidget(ttk.LabelFrame):
    """Widget affichant les statistiques de performance avec interprétations"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget des statistiques de performance
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent, text="Statistiques de performance", padding=5)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.performance_metrics = PerformanceMetrics()
        self.metrics_interpreter = MetricsInterpreter()
        
        # Historique des métriques pour analyse de tendance
        self.metrics_history = {
            "sharpe": [],
            "sortino": [],
            "calmar": [],
            "max_drawdown": [],
            "max_drawdown_date": None
        }
        
        # Storage for tooltips
        self.tooltips = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage des statistiques"""
        # Frame principale avec onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Onglet des métriques de base
        basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_tab, text="Métriques de base")
        self.create_basic_metrics_tab(basic_tab)
        
        # Onglet des métriques avancées
        advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(advanced_tab, text="Métriques avancées")
        self.create_advanced_metrics_tab(advanced_tab)
        
        # Onglet des analyses de rendement
        returns_tab = ttk.Frame(self.notebook)
        self.notebook.add(returns_tab, text="Analyse de rendement")
        self.create_returns_analysis_tab(returns_tab)
    
    def create_basic_metrics_tab(self, parent):
        """Création de l'onglet des métriques de base"""
        # Création du tableau des statistiques
        self.stats_tree = ttk.Treeview(parent, columns=("1", "2"), show='headings', height=10)
        self.stats_tree.heading("1", text="Métrique")
        self.stats_tree.heading("2", text="Valeur")
        self.stats_tree.column("1", width=150)
        self.stats_tree.column("2", width=150)
        
        # Ajout de la barre de défilement
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.stats_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        # Positionnement du tableau
        self.stats_tree.pack(fill=tk.BOTH, expand=True)
        
        # Créer les éléments du tableau pour toutes les métriques de base
        metrics = [
            ("Rendement total", "total_return"),
            ("Rendement annualisé", "annualized_return"),
            ("Volatilité annualisée", "volatility"),
            ("Drawdown maximum", "max_drawdown"),
            ("Ratio de Sharpe", "sharpe_ratio"),
            ("Ratio de Sortino", "sortino_ratio"),
            ("Ratio de Calmar", "calmar_ratio"),
            ("Ratio de gain", "win_ratio"),
            ("Gain moyen", "avg_win"),
            ("Perte moyenne", "avg_loss")
        ]
        
        # Insérer les métriques dans le tableau
        self.metric_items = {}
        for name, key in metrics:
            item_id = self.stats_tree.insert("", tk.END, values=(name, "-"))
            self.metric_items[key] = item_id
    
    def create_advanced_metrics_tab(self, parent):
        """Création de l'onglet des métriques avancées"""
        # À implémenter: métriques avancées comme Treynor, Information Ratio, MAR, etc.
        ttk.Label(parent, text="Métriques avancées à implémenter").pack(pady=20)
    
    def create_returns_analysis_tab(self, parent):
        """Création de l'onglet d'analyse de rendement"""
        # À implémenter: analyse de la distribution des rendements, etc.
        ttk.Label(parent, text="Analyse de rendement à implémenter").pack(pady=20)
    
    def update(self):
        """Met à jour les statistiques de performance"""
        if not self.data_manager.connected or self.data_manager.equity_data is None:
            self.clear_stats()
            return
        
        try:
            # Calculer les métriques de performance
            metrics = self.performance_metrics.calculate_metrics(self.data_manager.equity_data)
            
            if not metrics:
                self.clear_stats()
                return
            
            # Stocker les métriques clés dans l'historique pour analyse de tendance
            self.metrics_history["sharpe"].append(metrics["sharpe_ratio"])
            self.metrics_history["sortino"].append(metrics["sortino_ratio"])
            self.metrics_history["calmar"].append(metrics["calmar_ratio"])
            self.metrics_history["max_drawdown"].append(metrics["max_drawdown"])
            
            # Garder un historique limité (par exemple, 30 derniers points)
            max_history = 30
            self.metrics_history["sharpe"] = self.metrics_history["sharpe"][-max_history:]
            self.metrics_history["sortino"] = self.metrics_history["sortino"][-max_history:]
            self.metrics_history["calmar"] = self.metrics_history["calmar"][-max_history:]
            self.metrics_history["max_drawdown"] = self.metrics_history["max_drawdown"][-max_history:]
            
            # Mettre à jour les valeurs dans le tableau
            for key, item_id in self.metric_items.items():
                if key in metrics:
                    value = metrics[key]
                    
                    # Formatter la valeur selon son type
                    if key in ["total_return", "annualized_return", "volatility", "max_drawdown", "win_ratio", "avg_win", "avg_loss"]:
                        formatted_value = format_percentage(value)
                    else:  # Ratios
                        formatted_value = f"{value:.3f}"
                    
                    # Définir la couleur selon la valeur
                    tag = None
                    if key in ["total_return", "annualized_return", "sharpe_ratio", "sortino_ratio", "calmar_ratio"]:
                        tag = "positive" if value > 0 else "negative"
                    elif key == "max_drawdown":
                        tag = "negative"  # Drawdown est toujours négatif
                    
                    # Mettre à jour l'élément du tableau
                    self.stats_tree.item(item_id, values=(self.stats_tree.item(item_id)["values"][0], formatted_value), tags=(tag,))
                    
                    # Créer ou mettre à jour les tooltips pour les métriques clés
                    if key == "sharpe_ratio":
                        interpretation = self.metrics_interpreter.interpret_sharpe_ratio(value, self.metrics_history["sharpe"])
                        self.create_or_update_tooltip(item_id, interpretation)
                    elif key == "sortino_ratio":
                        sharpe = metrics.get("sharpe_ratio")
                        interpretation = self.metrics_interpreter.interpret_sortino_ratio(value, sharpe, self.metrics_history["sortino"])
                        self.create_or_update_tooltip(item_id, interpretation)
                    elif key == "calmar_ratio":
                        max_dd = metrics.get("max_drawdown")
                        interpretation = self.metrics_interpreter.interpret_calmar_ratio(value, max_dd, 
                                                                                      self.metrics_history["max_drawdown_date"], 
                                                                                      self.metrics_history["calmar"])
                        self.create_or_update_tooltip(item_id, interpretation)
            
            # Configurer les tags pour la coloration
            self.stats_tree.tag_configure("positive", foreground="green")
            self.stats_tree.tag_configure("negative", foreground="red")
            self.stats_tree.tag_configure("neutral", foreground="black")
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des statistiques de performance")
            self.clear_stats()
    
    def create_or_update_tooltip(self, item_id, interpretation):
        """
        Crée ou met à jour un tooltip avancé pour un élément du tableau
        
        Args:
            item_id: Identifiant de l'élément du tableau
            interpretation (dict): Données d'interprétation
        """
        # Obtenir l'ID du widget réel associé à l'élément du tableau
        # Note: Ceci est spécifique à l'implémentation de Treeview dans tkinter
        widget_id = self.stats_tree.identify_row(item_id)
        
        if widget_id and widget_id in self.tooltips:
            # Mettre à jour le tooltip existant
            self.tooltips[widget_id].update_interpretation(interpretation)
        else:
            # Créer un nouveau tooltip
            self.tooltips[item_id] = AdvancedTooltip(self.stats_tree, interpretation)
    
    def clear_stats_tree(self):
        """Efface le tableau des statistiques"""
        for key, item_id in self.metric_items.items():
            self.stats_tree.item(item_id, values=(self.stats_tree.item(item_id)["values"][0], "-"))
    
    def clear_stats(self):
        """Réinitialise complètement les statistiques"""
        self.clear_stats_tree()