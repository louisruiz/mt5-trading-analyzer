#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de score de risque global pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from analysis.risk_score_calculator import RiskScoreCalculator

class RiskScoreWidget(ttk.LabelFrame):
    """Widget affichant le score de risque global"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget de score de risque
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent, text="Score de risque global", padding=5)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.risk_calculator = RiskScoreCalculator()
        
        # Historique des scores de risque
        self.risk_history = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage du score de risque"""
        # Frame supérieure pour le score et la jauge
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame pour le score numérique et le rating
        score_frame = ttk.Frame(top_frame)
        score_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Score numérique
        self.score_label = ttk.Label(score_frame, text="--", font=("Helvetica", 24, "bold"))
        self.score_label.pack(anchor=tk.CENTER, pady=5)
        
        # Rating textuel
        self.rating_label = ttk.Label(score_frame, text="Indéterminé")
        self.rating_label.pack(anchor=tk.CENTER)
        
        # Frame pour la jauge
        gauge_frame = ttk.Frame(top_frame)
        gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Création de la jauge avec matplotlib
        self.gauge_figure = Figure(figsize=(4, 2), dpi=100)
        self.gauge_plot = self.gauge_figure.add_subplot(111)
        
        # Intégration dans le widget Tkinter
        self.gauge_canvas = FigureCanvasTkAgg(self.gauge_figure, gauge_frame)
        self.gauge_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Frame inférieure pour les composantes du score
        bottom_frame = ttk.LabelFrame(self, text="Composantes du risque")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Création de la grille pour les composantes
        self.component_bars = {}
        
        components = [
            ("D-Leverage", "d_leverage"),
            ("VaR", "var"),
            ("Drawdown", "drawdown"),
            ("Marge", "margin_pct"),
            ("Concentration", "concentration"),
            ("Volatilité", "volatility")
        ]
        
        for i, (name, key) in enumerate(components):
            # Label pour le nom de la composante
            ttk.Label(bottom_frame, text=name).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Frame pour la barre de progression
            bar_frame = ttk.Frame(bottom_frame, height=15)
            bar_frame.grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            bottom_frame.columnconfigure(1, weight=1)
            
            # Canvas pour la barre colorée
            bar_canvas = tk.Canvas(bar_frame, height=15, bg="lightgray")
            bar_canvas.pack(fill=tk.X, expand=True)
            
            # Créer la barre (initialement vide)
            bar = bar_canvas.create_rectangle(0, 0, 0, 15, fill="gray", width=0)
            
            # Label pour la valeur
            value_label = ttk.Label(bottom_frame, text="-")
            value_label.grid(row=i, column=2, sticky=tk.E, padx=5, pady=2)
            
            # Stocker les références
            self.component_bars[key] = {
                "canvas": bar_canvas,
                "bar": bar,
                "label": value_label
            }
    
    def update(self):
        """Met à jour le score de risque et ses composantes"""
        if not self.data_manager.connected:
            self.clear_score()
            return
        
        try:
            # Collecter les métriques nécessaires au calcul du score
            metrics = {}
            
            # D-Leverage
            metrics["d_leverage"] = self.data_manager.calculate_d_leverage()
            
            # Style de trading basé sur la durée moyenne des positions
            avg_duration = self.data_manager.get_average_position_duration()
            if avg_duration < 30:
                metrics["trading_style"] = "scalping"
            elif avg_duration < 60:
                metrics["trading_style"] = "intraday"
            else:
                metrics["trading_style"] = "swing"
            
            # VaR mensuelle
            metrics["var_monthly"] = self.data_manager.calculate_monthly_var()
            
            # Drawdown maximum
            if self.data_manager.equity_data is not None and not self.data_manager.equity_data.empty:
                equity_series = self.data_manager.equity_data
                rolling_max = equity_series.cummax()
                drawdown_series = (equity_series - rolling_max) / rolling_max * 100
                metrics["max_drawdown"] = drawdown_series.min()
            else:
                metrics["max_drawdown"] = 0
            
            # Pourcentage de marge utilisée
            metrics["margin_pct"] = self.data_manager.get_current_margin_percentage()
            
            # Indice de concentration (HHI normalisé)
            if self.data_manager.positions is not None and not self.data_manager.positions.empty:
                positions_df = self.data_manager.positions
                positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
                total_size = positions_df['position_size'].sum()
                
                if total_size > 0:
                    # Calculer les poids normalisés
                    weights = positions_df['position_size'] / total_size
                    # Calculer l'indice HHI
                    hhi = (weights ** 2).sum()
                    # Normaliser l'indice HHI (0-1)
                    n = len(positions_df)
                    if n > 1:
                        hhi_normalized = (hhi - 1/n) / (1 - 1/n)
                    else:
                        hhi_normalized = 1
                    
                    metrics["concentration"] = hhi_normalized
                else:
                    metrics["concentration"] = 0
            else:
                metrics["concentration"] = 0
            
            # Volatilité
            if self.data_manager.equity_data is not None and not self.data_manager.equity_data.empty:
                equity_series = self.data_manager.equity_data
                returns = equity_series.pct_change().dropna()
                metrics["volatility"] = returns.std() * np.sqrt(252) * 100  # Annualisée en pourcentage
            else:
                metrics["volatility"] = 0
            
            # Calculer le score de risque global
            risk_score = self.risk_calculator.calculate_global_risk_score(metrics)
            
            # Ajouter à l'historique
            self.risk_history.append(risk_score["score"])
            if len(self.risk_history) > 30:  # Garder un historique limité
                self.risk_history = self.risk_history[-30:]
            
            # Mettre à jour l'affichage du score
            self.score_label.config(text=str(risk_score["score"]), foreground=risk_score["color"])
            self.rating_label.config(text=risk_score["rating"], foreground=risk_score["color"])
            
            # Mettre à jour la jauge
            self.update_gauge(risk_score["score"], risk_score["color"])
            
            # Mettre à jour les barres des composantes
            for component, details in self.component_bars.items():
                if component in risk_score["details"]:
                    score = risk_score["details"][component]
                    self.update_component_bar(component, score)
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du score de risque")
            self.clear_score()
    
    def update_gauge(self, score, color):
        """
        Met à jour la jauge graphique du score de risque
        
        Args:
            score (int): Score de risque (0-100)
            color (str): Couleur hex représentant le niveau de risque
        """
        try:
            # Effacer le graphique précédent
            self.gauge_plot.clear()
            
            # Créer un graphique de type jauge semi-circulaire
            # Les valeurs sont en radians, 0 étant à droite, pi étant à gauche
            theta = np.linspace(0, np.pi, 100)
            
            # Arrière-plan gris clair
            self.gauge_plot.plot(theta, [1] * 100, color='lightgray', linewidth=15)
            
            # Déterminer jusqu'où la jauge doit être remplie
            fill_ratio = score / 100
            fill_idx = int(fill_ratio * 100)
            
            if fill_idx > 0:
                # Gradients de couleur de bleu à rouge
                if score < 20:
                    gauge_color = "#0070C0"  # Bleu
                elif score < 40:
                    gauge_color = "#00B050"  # Vert
                elif score < 60:
                    gauge_color = "#FFC000"  # Jaune
                elif score < 80:
                    gauge_color = "#FF6600"  # Orange
                else:
                    gauge_color = "#C00000"  # Rouge
                
                # Tracer la partie remplie de la jauge
                self.gauge_plot.plot(theta[:fill_idx], [1] * fill_idx, color=gauge_color, linewidth=15)
            
            # Configurer le plot
            self.gauge_plot.set_ylim(0, 2)
            self.gauge_plot.axis('equal')
            self.gauge_plot.axis('off')
            
            # Ajouter les marqueurs de niveau
            for i, level in enumerate([0, 25, 50, 75, 100]):
                angle = np.pi * (1 - level / 100)
                self.gauge_plot.plot([angle, angle], [0.85, 1.15], color='gray', linewidth=1)
                
                # Ajouter les étiquettes
                x = 1.25 * np.cos(angle)
                y = 1.25 * np.sin(angle)
                self.gauge_plot.text(x, y, str(level), ha='center', va='center', fontsize=8)
            
            # Ajouter le marqueur de position
            angle = np.pi * (1 - score / 100)
            marker_x = np.cos(angle)
            marker_y = np.sin(angle)
            self.gauge_plot.plot(angle, 1, 'ko', markersize=10)
            
            # Mettre à jour la figure
            self.gauge_figure.tight_layout()
            self.gauge_canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour de la jauge de risque")
    
    def update_component_bar(self, component, score):
        """
        Met à jour une barre de composante de risque
        
        Args:
            component (str): Identifiant de la composante
            score (float): Score de la composante (0-100)
        """
        try:
            if component not in self.component_bars:
                return
            
            details = self.component_bars[component]
            canvas = details["canvas"]
            bar = details["bar"]
            label = details["label"]
            
            # Déterminer la couleur en fonction du score
            if score < 20:
                color = "#0070C0"  # Bleu
            elif score < 40:
                color = "#00B050"  # Vert
            elif score < 60:
                color = "#FFC000"  # Jaune
            elif score < 80:
                color = "#FF6600"  # Orange
            else:
                color = "#C00000"  # Rouge
            
            # Mettre à jour la largeur de la barre
            width = canvas.winfo_width()
            bar_width = (score / 100) * width
            canvas.coords(bar, 0, 0, bar_width, 15)
            canvas.itemconfig(bar, fill=color)
            
            # Mettre à jour le label
            label.config(text=f"{score:.1f}")
            
        except Exception as e:
            self.logger.exception(f"Erreur lors de la mise à jour de la barre {component}")
    
    def clear_score(self):
        """Efface le score et les composantes"""
        self.score_label.config(text="--", foreground="black")
        self.rating_label.config(text="Indéterminé", foreground="black")
        
        # Effacer la jauge
        self.gauge_plot.clear()
        self.gauge_plot.axis('off')
        self.gauge_canvas.draw()
        
        # Effacer les barres des composantes
        for component, details in self.component_bars.items():
            canvas = details["canvas"]
            bar = details["bar"]
            label = details["label"]
            
            canvas.coords(bar, 0, 0, 0, 15)
            label.config(text="-")