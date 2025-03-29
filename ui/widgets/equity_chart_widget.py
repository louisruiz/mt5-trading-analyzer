#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de graphique d'équité pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.constants import CHART_PERIODS
from analysis.drawdown_analyzer import DrawdownAnalyzer

class EquityChartWidget(ttk.LabelFrame):
    """Widget affichant le graphique d'évolution de l'équité"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget de graphique d'équité
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent, text="Évolution de l'équité", padding=5)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.drawdown_analyzer = DrawdownAnalyzer()
        
        # Période sélectionnée (par défaut 3 mois)
        self.period_var = tk.StringVar(value="3m")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage du graphique d'équité"""
        # Frame de contrôle pour les options du graphique
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label et combobox pour la période
        ttk.Label(control_frame, text="Période:").pack(side=tk.LEFT, padx=5)
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var,
                               values=list(CHART_PERIODS.keys()), width=10)
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.update)
        
        # Options d'affichage
        self.show_trend_var = tk.BooleanVar(value=True)
        trend_check = ttk.Checkbutton(control_frame, text="Tendance", 
                                    variable=self.show_trend_var,
                                    command=self.update)
        trend_check.pack(side=tk.LEFT, padx=10)
        
        self.show_drawdown_var = tk.BooleanVar(value=True)
        drawdown_check = ttk.Checkbutton(control_frame, text="Drawdown", 
                                       variable=self.show_drawdown_var,
                                       command=self.update)
        drawdown_check.pack(side=tk.LEFT, padx=10)
        
        # Options avancées
        self.show_all_drawdowns_var = tk.BooleanVar(value=False)
        all_drawdowns_check = ttk.Checkbutton(control_frame, text="Tous les drawdowns", 
                                             variable=self.show_all_drawdowns_var,
                                             command=self.update)
        all_drawdowns_check.pack(side=tk.LEFT, padx=10)

        self.show_change_points_var = tk.BooleanVar(value=False)
        change_points_check = ttk.Checkbutton(control_frame, text="Points de changement", 
                                             variable=self.show_change_points_var,
                                             command=self.update)
        change_points_check.pack(side=tk.LEFT, padx=10)
        
        # Frame principale pour le graphique
        chart_frame = ttk.Frame(self)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Création de la figure matplotlib
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Intégration dans le widget Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les informations statistiques
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Labels pour les statistiques de performance
        self.period_return_label = ttk.Label(stats_frame, text="Rendement sur la période: -")
        self.period_return_label.grid(row=0, column=0, padx=10, sticky=tk.W)
        
        self.max_drawdown_label = ttk.Label(stats_frame, text="Drawdown maximum: -")
        self.max_drawdown_label.grid(row=0, column=1, padx=10, sticky=tk.W)
        
        self.volatility_label = ttk.Label(stats_frame, text="Volatilité (ann.): -")
        self.volatility_label.grid(row=1, column=0, padx=10, sticky=tk.W)
        
        self.sharpe_label = ttk.Label(stats_frame, text="Ratio de Sharpe: -")
        self.sharpe_label.grid(row=1, column=1, padx=10, sticky=tk.W)
    
    def update(self, event=None):
        """Met à jour le graphique d'équité selon la période sélectionnée"""
        if not self.data_manager.connected or self.data_manager.equity_data is None:
            self.clear_chart()
            return
        
        try:
            # Obtenir la période sélectionnée
            period = self.period_var.get()
            
            # Récupérer les données d'équité pour la période
            equity_data = self.data_manager.get_equity_data_for_period(period)
            
            if equity_data.empty:
                self.clear_chart()
                return
            
            # Traiter les données pour le graphique
            equity_series = equity_data['equity']
            
            # Effacer le graphique précédent
            self.plot.clear()
            
            # Tracer la courbe d'équité
            self.plot.plot(equity_series.index, equity_series.values, 'b-', linewidth=2)
            
            # Calculer et tracer le drawdown si demandé
            if self.show_drawdown_var.get():
                rolling_max = equity_series.cummax()
                drawdown = (equity_series - rolling_max) / rolling_max * 100
                
                # Trouver le drawdown maximum et sa date
                max_dd = drawdown.min()
                max_dd_date = drawdown.idxmin()
                
                # Colorer la zone de drawdown maximum
                self.plot.fill_between(drawdown.index, 0, drawdown.values, 
                                     alpha=0.3, color='red', 
                                     where=(drawdown < 0), 
                                     label=f'Drawdown (Max: {max_dd:.2f}%)')
                
                # Marquer le point de drawdown maximum
                self.plot.plot([max_dd_date], [equity_series[max_dd_date]], 'ro', markersize=6)
                
                # Annotation du drawdown maximum
                self.plot.annotate(f'{max_dd:.2f}%', 
                                 xy=(max_dd_date, equity_series[max_dd_date]),
                                 xytext=(-30, -30),
                                 textcoords='offset points',
                                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=.2'),
                                 bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))
            
            # Tracer la ligne de tendance si demandé
            if self.show_trend_var.get():
                # Convertir les dates en valeurs numériques pour la régression
                x = np.arange(len(equity_series))
                y = equity_series.values
                
                # Calculer la ligne de tendance (régression polynomiale de degré 1)
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                
                # Tracer la ligne de tendance
                self.plot.plot(equity_series.index, p(x), 'g--', linewidth=1.5, 
                             label=f'Tendance ({z[0]:.2f})')
            
            # Tracer tous les drawdowns significatifs si demandé
            if self.show_all_drawdowns_var.get():
                drawdowns = self.drawdown_analyzer.identify_drawdowns(equity_series, threshold_pct=-5)
                
                for i, dd in enumerate(drawdowns):
                    if dd["start_date"] and dd["bottom_date"]:
                        # Colorer la période de drawdown
                        self.plot.axvspan(dd["start_date"], dd["bottom_date"], 
                                        alpha=0.1, color='red', label=f'Drawdown {i+1}' if i == 0 else "")
                    
                    if dd["bottom_date"] and dd["end_date"]:
                        # Colorer la période de récupération
                        self.plot.axvspan(dd["bottom_date"], dd["end_date"], 
                                        alpha=0.1, color='green', label=f'Récupération {i+1}' if i == 0 else "")
                    
                    # Annoter le drawdown maximum
                    if dd["bottom_date"]:
                        dd_value = dd["max_drawdown_pct"]
                        bottom_value = equity_series[dd["bottom_date"]]
                        self.plot.annotate(
                            f"{dd_value:.1f}%",
                            xy=(dd["bottom_date"], bottom_value),
                            xytext=(0, -30),
                            textcoords="offset points",
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
                            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8)
                        )
            
            # Tracer les points de changement significatifs si demandé
            if self.show_change_points_var.get():
                change_points = self.drawdown_analyzer.find_change_points(equity_series)
                
                for date in change_points:
                    # Marquer le point de changement par une ligne verticale
                    self.plot.axvline(x=date, color='purple', linestyle=':', alpha=0.7)
                    
                    # Annoter le point de changement
                    self.plot.annotate(
                        "Changement",
                        xy=(date, equity_series[date]),
                        xytext=(0, 30),
                        textcoords="offset points",
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="purple", alpha=0.8)
                    )
            
            # Calculer et afficher les indices de robustesse
            pain_index = self.drawdown_analyzer.calculate_pain_index(equity_series)
            ulcer_index = self.drawdown_analyzer.calculate_ulcer_index(equity_series)
            
            # Ajouter ces indices comme texte dans le graphique
            self.plot.text(0.02, 0.05, f"Pain Index: {pain_index:.2f}\nUlcer Index: {ulcer_index:.2f}", 
                         transform=self.plot.transAxes,
                         bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
            
            # Configurer le graphique
            self.plot.set_title(f"Évolution de l'équité ({CHART_PERIODS.get(period, period)})")
            self.plot.set_xlabel("Date")
            self.plot.set_ylabel("Équité")
            self.plot.grid(True, linestyle='--', alpha=0.7)
            self.plot.legend(loc='upper left')
            
            # Formater l'axe des dates
            self.figure.autofmt_xdate()
            
            # Redessiner le graphique
            self.canvas.draw()
            
            # Mettre à jour les statistiques
            self.update_statistics(equity_series)
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du graphique d'équité")
            self.clear_chart()
    
    def update_statistics(self, equity_series):
        """Met à jour les statistiques de performance pour la période affichée"""
        try:
            # Calculer le rendement sur la période
            start_equity = equity_series.iloc[0]
            end_equity = equity_series.iloc[-1]
            period_return = (end_equity - start_equity) / start_equity * 100
            
            # Calculer le drawdown maximum
            rolling_max = equity_series.cummax()
            drawdown = (equity_series - rolling_max) / rolling_max * 100
            max_drawdown = drawdown.min()
            
            # Calculer la volatilité annualisée
            daily_returns = equity_series.pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualisé en %
            
            # Calculer le ratio de Sharpe
            # Supposons un taux sans risque de 0%
            risk_free_rate = 0
            mean_daily_return = daily_returns.mean()
            annualized_return = ((1 + mean_daily_return) ** 252) - 1
            sharpe_ratio = (annualized_return - risk_free_rate) / (volatility / 100) if volatility != 0 else 0
            
            # Mettre à jour les labels
            self.period_return_label.config(
                text=f"Rendement sur la période: {period_return:.2f}%",
                foreground="green" if period_return >= 0 else "red"
            )
            
            self.max_drawdown_label.config(
                text=f"Drawdown maximum: {max_drawdown:.2f}%",
                foreground="red"
            )
            
            self.volatility_label.config(
                text=f"Volatilité (ann.): {volatility:.2f}%"
            )
            
            self.sharpe_label.config(
                text=f"Ratio de Sharpe: {sharpe_ratio:.2f}",
                foreground="green" if sharpe_ratio > 1 else (
                    "black" if sharpe_ratio > 0 else "red"
                )
            )
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des statistiques")
            
            # Réinitialiser les labels en cas d'erreur
            self.period_return_label.config(text="Rendement sur la période: -")
            self.max_drawdown_label.config(text="Drawdown maximum: -")
            self.volatility_label.config(text="Volatilité (ann.): -")
            self.sharpe_label.config(text="Ratio de Sharpe: -")
    
    def clear_chart(self):
        """Efface le graphique"""
        self.plot.clear()
        self.plot.set_title("Aucune donnée disponible")
        self.plot.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()
        
        # Réinitialiser les statistiques
        self.period_return_label.config(text="Rendement sur la période: -")
        self.max_drawdown_label.config(text="Drawdown maximum: -")
        self.volatility_label.config(text="Volatilité (ann.): -")
        self.sharpe_label.config(text="Ratio de Sharpe: -")