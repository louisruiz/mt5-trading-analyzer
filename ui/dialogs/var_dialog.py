#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Boîte de dialogue d'analyse de VaR pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta

class VarDialog:
    """Boîte de dialogue d'analyse de Value at Risk (VaR)"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation de la boîte de dialogue VaR
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        # Création de la fenêtre de dialogue
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Analyse de VaR")
        self.dialog.geometry("600x500")
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
        ttk.Label(self.dialog, text="VaR Stabilizer", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        info_text = (
            "Cet outil maintient la VaR (Value at Risk) dans une fourchette étroite pour maximiser le VaR Ratio. "
            "L'algorithme ajuste automatiquement l'exposition pour maintenir une VaR mensuelle entre 8% et 10% "
            "et évite les fluctuations de VaR supérieures à un ratio 1.8:1 sur 6 mois."
        )
        
        info_label = ttk.Label(self.dialog, text=info_text, wraplength=550, justify="left")
        info_label.pack(padx=20, pady=10, fill=tk.X)
        
        # Frame pour les méthodes de calcul
        methods_frame = ttk.LabelFrame(self.dialog, text="Méthodes de calcul de VaR")
        methods_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Variables pour les méthodes de calcul
        self.method_var = tk.StringVar(value="Paramétrique")
        methods = ["Paramétrique", "Historique", "Monte Carlo"]
        
        # Créer les radiobuttons pour chaque méthode
        for i, method in enumerate(methods):
            ttk.Radiobutton(methods_frame, text=method, variable=self.method_var, 
                           value=method, command=self.update_var_calculation).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Frame pour le graphique
        chart_frame = ttk.Frame(self.dialog)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Création de la figure matplotlib
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Intégration dans le widget Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les résultats
        results_frame = ttk.LabelFrame(self.dialog, text="Résultats de VaR")
        results_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame pour les labels des résultats
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.pack(fill=tk.X, expand=True, padx=10, pady=10)
        
        # Colonnes pour les résultats
        columns = ["Métrique", "Daily", "Weekly", "Monthly"]
        for i, col in enumerate(columns):
            ttk.Label(metrics_frame, text=col, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=i, padx=5, pady=2, sticky=tk.W)
        
        # Labels pour les résultats de VaR
        self.var_labels = {}
        confidence_levels = ["95%", "99%"]
        
        for i, level in enumerate(confidence_levels, start=1):
            ttk.Label(metrics_frame, text=f"VaR {level}").grid(
                row=i, column=0, padx=5, pady=2, sticky=tk.W)
            
            # Labels pour chaque période (daily, weekly, monthly)
            for j, period in enumerate(["daily", "weekly", "monthly"], start=1):
                label_id = f"var_{level}_{period}"
                self.var_labels[label_id] = ttk.Label(metrics_frame, text="-")
                self.var_labels[label_id].grid(row=i, column=j, padx=5, pady=2, sticky=tk.W)
        
        # Labels pour ES/CVaR 95%
        ttk.Label(metrics_frame, text="ES/CVaR 95%").grid(
            row=3, column=0, padx=5, pady=2, sticky=tk.W)
        
        for j, period in enumerate(["daily", "weekly", "monthly"], start=1):
            label_id = f"es_95_{period}"
            self.var_labels[label_id] = ttk.Label(metrics_frame, text="-")
            self.var_labels[label_id].grid(row=3, column=j, padx=5, pady=2, sticky=tk.W)
        
        # Labels pour ES/CVaR 99%
        ttk.Label(metrics_frame, text="ES/CVaR 99%").grid(
            row=4, column=0, padx=5, pady=2, sticky=tk.W)
        
        for j, period in enumerate(["daily", "weekly", "monthly"], start=1):
            label_id = f"es_99_{period}"
            self.var_labels[label_id] = ttk.Label(metrics_frame, text="-")
            self.var_labels[label_id].grid(row=4, column=j, padx=5, pady=2, sticky=tk.W)
        
        # Label pour le VaR Ratio
        ttk.Label(metrics_frame, text="VaR Ratio (6m)").grid(
            row=5, column=0, padx=5, pady=2, sticky=tk.W)
        self.var_labels["var_ratio"] = ttk.Label(metrics_frame, text="-")
        self.var_labels["var_ratio"].grid(row=5, column=1, columnspan=3, padx=5, pady=2, sticky=tk.W)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Bouton de fermeture
        close_button = ttk.Button(button_frame, text="Fermer", command=self.dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)
        
        # Mettre à jour les calculs de VaR
        self.update_var_calculation()
    
    def update_var_calculation(self):
        """Met à jour les calculs et l'affichage de VaR selon la méthode sélectionnée"""
        try:
            # Vérifier si des données d'équité sont disponibles
            if not self.data_manager.connected or self.data_manager.equity_data is None:
                self.clear_var_display()
                return
            
            # Récupérer la méthode sélectionnée
            method = self.method_var.get()
            
            # Calculer les rendements à partir des données d'équité
            equity_series = self.data_manager.equity_data
            if equity_series is None or len(equity_series) < 10:  # Au moins 10 points de données nécessaires
                self.clear_var_display()
                return
            
            # Calculer les rendements journaliers
            returns = equity_series.pct_change().dropna()
            
            # Calculer l'historique de VaR
            self.calculate_var_history(returns, method)
            
            # Calculer les VaR actuelles pour différentes périodes et niveaux de confiance
            self.calculate_current_var(returns, method)
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de VaR")
            self.clear_var_display()
    
    def calculate_var_history(self, returns, method):
        """
        Calcule et affiche l'historique de VaR
        
        Args:
            returns (pd.Series): Série de rendements
            method (str): Méthode de calcul de VaR
        """
        try:
            # Période de VaR (6 mois par défaut)
            window_size = 126  # Environ 6 mois de jours de trading
            
            if len(returns) < window_size:
                window_size = len(returns) // 2  # Utiliser la moitié des données si moins de 6 mois
            
            # Créer des séries pour stocker l'historique de VaR
            var_history = pd.Series(index=returns.index[window_size-1:], dtype=float)
            
            # Calculer la VaR glissante
            for i in range(window_size-1, len(returns)):
                window_returns = returns.iloc[i-window_size+1:i+1]
                
                if method == "Paramétrique":
                    # VaR paramétrique (normale) à 95%
                    mean = window_returns.mean()
                    std = window_returns.std()
                    var_95 = -(mean + 1.645 * std) * 100  # En pourcentage
                elif method == "Historique":
                    # VaR historique à 95%
                    var_95 = -window_returns.quantile(0.05) * 100  # En pourcentage
                else:  # Monte Carlo
                    # VaR Monte Carlo à 95%
                    var_95 = self.calculate_monte_carlo_var(window_returns, 0.95) * 100  # En pourcentage
                
                var_history.iloc[i-window_size+1] = var_95
            
            # Tracer le graphique
            self.plot.clear()
            self.plot.plot(var_history.index, var_history.values, 'b-', linewidth=2, label='VaR mensuelle (95%)')
            
            # Ajouter les limites recommandées
            self.plot.axhline(y=8, color='g', linestyle='--', alpha=0.7, label='Min recommandé (8%)')
            self.plot.axhline(y=10, color='r', linestyle='--', alpha=0.7, label='Max recommandé (10%)')
            
            # Formater le graphique
            self.plot.set_title(f"Évolution de la VaR mensuelle (95%) - Méthode {method}")
            self.plot.set_xlabel("Date")
            self.plot.set_ylabel("VaR mensuelle (%)")
            self.plot.legend()
            self.plot.grid(True, linestyle='--', alpha=0.7)
            self.figure.autofmt_xdate()
            self.canvas.draw()
            
            # Calculer le VaR Ratio (max/min sur la période)
            max_var = var_history.max()
            min_var = var_history.min()
            var_ratio = max_var / min_var if min_var > 0 else float('inf')
            
            # Mettre à jour le label de VaR Ratio
            self.var_labels["var_ratio"].config(
                text=f"{var_ratio:.2f}",
                foreground="green" if var_ratio < 1.8 else "red"
            )
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de l'historique de VaR")
            self.plot.clear()
            self.plot.text(0.5, 0.5, "Données insuffisantes pour le calcul de VaR", ha='center', va='center')
            self.canvas.draw()
    
    def calculate_current_var(self, returns, method):
        """
        Calcule et affiche les VaR actuelles pour différentes périodes
        
        Args:
            returns (pd.Series): Série de rendements
            method (str): Méthode de calcul de VaR
        """
        try:
            # Prendre les 126 derniers rendements (environ 6 mois)
            if len(returns) > 126:
                recent_returns = returns.iloc[-126:]
            else:
                recent_returns = returns
            
            # Facteurs pour différentes périodes
            period_factors = {
                "daily": 1,
                "weekly": np.sqrt(5),
                "monthly": np.sqrt(22)
            }
            
            # Niveaux de confiance
            confidence_levels = {
                "95%": 0.95,
                "99%": 0.99
            }
            
            # Calculer la VaR pour chaque combinaison de période et niveau de confiance
            for level_name, level in confidence_levels.items():
                for period_name, factor in period_factors.items():
                    # Calculer la VaR selon la méthode sélectionnée
                    if method == "Paramétrique":
                        # VaR paramétrique (normale)
                        mean = recent_returns.mean()
                        std = recent_returns.std()
                        z_score = 1.645 if level == 0.95 else 2.326  # Z-score pour 95% ou 99%
                        var_value = -(mean + z_score * std) * factor * 100  # En pourcentage
                    elif method == "Historique":
                        # VaR historique
                        quantile = 1 - level
                        var_value = -recent_returns.quantile(quantile) * factor * 100  # En pourcentage
                    else:  # Monte Carlo
                        # VaR Monte Carlo
                        var_value = self.calculate_monte_carlo_var(recent_returns, level) * factor * 100  # En pourcentage
                    
                    # Mettre à jour le label correspondant
                    label_id = f"var_{level_name}_{period_name}"
                    self.var_labels[label_id].config(text=f"{var_value:.2f}%")
            
            # Calculer l'Expected Shortfall (ES/CVaR)
            es_95 = self.calculate_expected_shortfall(recent_returns, 0.95, period_factors)
            es_99 = self.calculate_expected_shortfall(recent_returns, 0.99, period_factors)
            
            # Mettre à jour les labels pour ES/CVaR
            for period in ["daily", "weekly", "monthly"]:
                # ES 95%
                label_id = f"es_95_{period}"
                self.var_labels[label_id].config(text=f"{es_95[period]:.2f}%")
                
                # ES 99%
                label_id = f"es_99_{period}"
                self.var_labels[label_id].config(text=f"{es_99[period]:.2f}%")
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la VaR actuelle")
            self.clear_var_metrics()
    
    def calculate_monte_carlo_var(self, returns, confidence_level):
        """
        Calcule la VaR par simulation Monte Carlo
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (0.95 ou 0.99)
            
        Returns:
            float: VaR calculée
        """
        try:
            # Estimer les paramètres de la distribution
            mean = returns.mean()
            std = returns.std()
            
            # Générer des scénarios aléatoires (10000 simulations)
            np.random.seed(42)  # Pour la reproductibilité
            n_simulations = 10000
            simulated_returns = np.random.normal(mean, std, n_simulations)
            
            # Calculer la VaR à partir des simulations
            var_quantile = 1 - confidence_level
            var_value = -np.percentile(simulated_returns, var_quantile * 100)
            
            return var_value
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de la VaR Monte Carlo")
            return 0
    
    def calculate_expected_shortfall(self, returns, confidence_level, period_factors):
        """
        Calcule l'Expected Shortfall (ES) ou Conditional Value at Risk (CVaR)
        
        Args:
            returns (pd.Series): Série de rendements
            confidence_level (float): Niveau de confiance (entre 0 et 1)
            period_factors (dict): Dictionnaire avec facteurs pour différentes périodes
            
        Returns:
            dict: ES pour différentes périodes
        """
        try:
            # Résultats pour différentes périodes
            es_values = {}
            
            # Calculer le quantile pour la VaR
            var_quantile = 1 - confidence_level
            var_threshold = returns.quantile(var_quantile)
            
            # Filtrer les rendements dans la queue de distribution
            tail_returns = returns[returns <= var_threshold]
            
            if len(tail_returns) == 0:
                # Si aucun rendement ne tombe dans la queue, retourner zéros
                return {period: 0 for period in period_factors}
            
            # Moyenne des rendements dans la queue
            es_daily = tail_returns.mean()
            
            # Appliquer les facteurs de période
            for period, factor in period_factors.items():
                es_values[period] = abs(es_daily * factor * 100)  # En pourcentage
            
            return es_values
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul de l'Expected Shortfall")
            return {period: 0 for period in period_factors}
    
    def clear_var_display(self):
        """Efface l'affichage de VaR"""
        self.clear_var_chart()
        self.clear_var_metrics()
    
    def clear_var_chart(self):
        """Efface le graphique de VaR"""
        self.plot.clear()
        self.plot.text(0.5, 0.5, "Données insuffisantes pour le calcul de VaR", ha='center', va='center')
        self.canvas.draw()
    
    def clear_var_metrics(self):
        """Efface les métriques de VaR"""
        for label in self.var_labels.values():
            label.config(text="-", foreground="black")