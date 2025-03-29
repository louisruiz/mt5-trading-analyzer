#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de benchmarking pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.constants import CHART_PERIODS, BENCHMARK_SYMBOLS
import yfinance as yf
from datetime import datetime, timedelta

class BenchmarkWidget(ttk.Frame):
    """Widget affichant les comparaisons de performance avec des benchmarks"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget de benchmarking
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        # Variables pour les sélections
        self.period_var = tk.StringVar(value="3m")
        self.benchmark_var = tk.StringVar(value="SPX")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage des comparaisons"""
        # Frame de contrôle pour les options
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label et combobox pour la période
        ttk.Label(control_frame, text="Période:").pack(side=tk.LEFT, padx=5)
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var,
                                   values=list(CHART_PERIODS.keys()), width=10)
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.update)
        
        # Label et combobox pour le benchmark
        ttk.Label(control_frame, text="Benchmark:").pack(side=tk.LEFT, padx=15)
        benchmark_combo = ttk.Combobox(control_frame, textvariable=self.benchmark_var,
                                      values=list(BENCHMARK_SYMBOLS.keys()), width=15)
        benchmark_combo.pack(side=tk.LEFT, padx=5)
        benchmark_combo.bind("<<ComboboxSelected>>", self.update)
        
        # Frame pour le graphique
        chart_frame = ttk.LabelFrame(self, text="Comparaison de performance")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Création de la figure matplotlib
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Intégration dans le widget Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pour les métriques comparatives
        metrics_frame = ttk.LabelFrame(self, text="Métriques comparatives")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Création de la grille pour les métriques
        self.metrics_grid = ttk.Frame(metrics_frame)
        self.metrics_grid.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # Labels pour les en-têtes des métriques
        ttk.Label(self.metrics_grid, text="Métrique", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.metrics_grid, text="Stratégie", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.metrics_grid, text="Benchmark", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.metrics_grid, text="Différence", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Séparateur
        ttk.Separator(self.metrics_grid, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=4, sticky=tk.EW, pady=5)
        
        # Labels pour les métriques
        self.metric_labels = {}
        
        metrics = [
            ("Rendement total", "total_return"),
            ("Rendement annualisé", "ann_return"),
            ("Volatilité", "volatility"),
            ("Ratio de Sharpe", "sharpe"),
            ("Drawdown maximum", "max_dd"),
            ("Alpha", "alpha"),
            ("Beta", "beta"),
            ("Corrélation", "correlation")
        ]
        
        for i, (metric_name, metric_id) in enumerate(metrics, start=2):
            ttk.Label(self.metrics_grid, text=metric_name).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Labels pour chaque colonne (stratégie, benchmark, différence)
            self.metric_labels[f"{metric_id}_strategy"] = ttk.Label(self.metrics_grid, text="-")
            self.metric_labels[f"{metric_id}_strategy"].grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            
            self.metric_labels[f"{metric_id}_benchmark"] = ttk.Label(self.metrics_grid, text="-")
            self.metric_labels[f"{metric_id}_benchmark"].grid(row=i, column=2, sticky=tk.W, padx=5, pady=2)
            
            self.metric_labels[f"{metric_id}_diff"] = ttk.Label(self.metrics_grid, text="-")
            self.metric_labels[f"{metric_id}_diff"].grid(row=i, column=3, sticky=tk.W, padx=5, pady=2)
    
    def update(self, event=None):
        """
        Met à jour les comparaisons de performance
        
        Args:
            event: Événement Tkinter (non utilisé directement)
        """
        if not self.data_manager.connected or self.data_manager.equity_data is None:
            self.clear_chart()
            self.clear_metrics()
            return
        
        try:
            # Récupérer les sélections
            period = self.period_var.get()
            benchmark_key = self.benchmark_var.get()
            
            # Obtenir le nombre de jours pour la période
            days = CHART_PERIODS.get(period, 90)
            
            # Obtenir le symbole du benchmark
            benchmark_symbol = BENCHMARK_SYMBOLS.get(benchmark_key, "^GSPC")
            
            # Définir la période pour les données
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Obtenir les données d'équité pour notre stratégie
            equity_series = self.data_manager.equity_data
            
            if equity_series is None or equity_series.empty:
                self.clear_chart()
                self.clear_metrics()
                return
            
            # Filtrer l'équité pour la période sélectionnée
            equity_series = equity_series[equity_series.index >= start_date]
            
            if equity_series.empty:
                self.clear_chart()
                self.clear_metrics()
                return
            
            # Obtenir les données du benchmark
            try:
                benchmark_data = yf.download(benchmark_symbol, start=start_date, end=end_date, progress=False)
                
                if benchmark_data.empty:
                    self.logger.warning(f"Impossible d'obtenir les données pour le benchmark {benchmark_symbol}")
                    benchmark_data = None
            except Exception as e:
                self.logger.exception(f"Erreur lors de l'obtention des données du benchmark {benchmark_symbol}")
                benchmark_data = None
            
            # Effacer le graphique précédent
            self.plot.clear()
            
            # Normaliser l'équité à 100 au début de la période
            strategy_returns = (equity_series / equity_series.iloc[0] * 100)
            
            # Tracer la courbe de la stratégie
            self.plot.plot(strategy_returns.index, strategy_returns.values, 'b-', linewidth=2, label='Ma stratégie')
            
            # Tracer la courbe du benchmark si disponible
            if benchmark_data is not None and not benchmark_data.empty:
                # Normaliser le benchmark à 100 au début de la période
                benchmark_returns = (benchmark_data['Close'] / benchmark_data['Close'].iloc[0] * 100)
                
                # Tracer la courbe du benchmark
                self.plot.plot(benchmark_returns.index, benchmark_returns.values, 'r-', linewidth=2, label=benchmark_key)
                
                # Calculer les métriques comparatives
                self.calculate_comparative_metrics(strategy_returns, benchmark_returns)
            else:
                self.clear_metrics()
            
            # Configurer le graphique
            self.plot.set_title(f"Performance comparative - {CHART_PERIODS.get(period, period)}")
            self.plot.set_xlabel("Date")
            self.plot.set_ylabel("Performance relative (%)")
            self.plot.grid(True, linestyle='--', alpha=0.7)
            self.plot.legend()
            
            # Formater l'axe des dates
            self.figure.autofmt_xdate()
            
            # Dessiner le graphique
            self.canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du benchmark")
            self.clear_chart()
            self.clear_metrics()
    
    def calculate_comparative_metrics(self, strategy_returns, benchmark_returns):
        """
        Calcule les métriques comparatives entre la stratégie et le benchmark
        
        Args:
            strategy_returns (pd.Series): Série de rendements normalisés de la stratégie
            benchmark_returns (pd.Series): Série de rendements normalisés du benchmark
        """
        try:
            # Aligner les séries sur les mêmes dates
            common_dates = strategy_returns.index.intersection(benchmark_returns.index)
            strategy_aligned = strategy_returns.reindex(common_dates)
            benchmark_aligned = benchmark_returns.reindex(common_dates)
            
            if len(common_dates) < 2:
                self.clear_metrics()
                return
            
            # Convertir en rendements quotidiens
            strategy_daily_returns = strategy_aligned.pct_change().dropna()
            benchmark_daily_returns = benchmark_aligned.pct_change().dropna()
            
            # Aligner à nouveau après le calcul des rendements
            common_dates = strategy_daily_returns.index.intersection(benchmark_daily_returns.index)
            strategy_daily_returns = strategy_daily_returns.reindex(common_dates)
            benchmark_daily_returns = benchmark_daily_returns.reindex(common_dates)
            
            # Rendement total
            strategy_total_return = (strategy_aligned.iloc[-1] / strategy_aligned.iloc[0] - 1) * 100
            benchmark_total_return = (benchmark_aligned.iloc[-1] / benchmark_aligned.iloc[0] - 1) * 100
            return_diff = strategy_total_return - benchmark_total_return
            
            # Annualiser le rendement (supposer 252 jours de trading par an)
            days = (strategy_aligned.index[-1] - strategy_aligned.index[0]).days
            ann_factor = 252 / max(days, 1)
            
            strategy_ann_return = ((1 + strategy_total_return / 100) ** ann_factor - 1) * 100
            benchmark_ann_return = ((1 + benchmark_total_return / 100) ** ann_factor - 1) * 100
            ann_return_diff = strategy_ann_return - benchmark_ann_return
            
            # Volatilité annualisée
            strategy_volatility = strategy_daily_returns.std() * np.sqrt(252) * 100
            benchmark_volatility = benchmark_daily_returns.std() * np.sqrt(252) * 100
            volatility_diff = strategy_volatility - benchmark_volatility
            
            # Ratio de Sharpe (supposer taux sans risque de 0% pour simplifier)
            strategy_sharpe = strategy_ann_return / strategy_volatility if strategy_volatility > 0 else 0
            benchmark_sharpe = benchmark_ann_return / benchmark_volatility if benchmark_volatility > 0 else 0
            sharpe_diff = strategy_sharpe - benchmark_sharpe
            
            # Drawdown maximum
            strategy_cum_returns = (1 + strategy_daily_returns).cumprod()
            strategy_max_drawdown = ((strategy_cum_returns / strategy_cum_returns.cummax()) - 1).min() * 100
            
            benchmark_cum_returns = (1 + benchmark_daily_returns).cumprod()
            benchmark_max_drawdown = ((benchmark_cum_returns / benchmark_cum_returns.cummax()) - 1).min() * 100
            
            max_dd_diff = strategy_max_drawdown - benchmark_max_drawdown
            
            # Beta et Alpha
            covariance = np.cov(strategy_daily_returns, benchmark_daily_returns)[0, 1]
            benchmark_variance = np.var(benchmark_daily_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            
            # Alpha annualisé (CAPM)
            alpha_daily = strategy_daily_returns.mean() - (beta * benchmark_daily_returns.mean())
            alpha = alpha_daily * 252 * 100  # Annualiser et convertir en pourcentage
            
            # Corrélation
            correlation = np.corrcoef(strategy_daily_returns, benchmark_daily_returns)[0, 1]
            
            # Mettre à jour les labels des métriques
            # Rendement total
            self.metric_labels["total_return_strategy"].config(
                text=f"{strategy_total_return:.2f}%",
                foreground="green" if strategy_total_return > 0 else "red"
            )
            self.metric_labels["total_return_benchmark"].config(
                text=f"{benchmark_total_return:.2f}%",
                foreground="green" if benchmark_total_return > 0 else "red"
            )
            self.metric_labels["total_return_diff"].config(
                text=f"{return_diff:+.2f}%",
                foreground="green" if return_diff > 0 else "red"
            )
            
            # Rendement annualisé
            self.metric_labels["ann_return_strategy"].config(
                text=f"{strategy_ann_return:.2f}%",
                foreground="green" if strategy_ann_return > 0 else "red"
            )
            self.metric_labels["ann_return_benchmark"].config(
                text=f"{benchmark_ann_return:.2f}%",
                foreground="green" if benchmark_ann_return > 0 else "red"
            )
            self.metric_labels["ann_return_diff"].config(
                text=f"{ann_return_diff:+.2f}%",
                foreground="green" if ann_return_diff > 0 else "red"
            )
            
            # Volatilité
            self.metric_labels["volatility_strategy"].config(
                text=f"{strategy_volatility:.2f}%",
                foreground="black"
            )
            self.metric_labels["volatility_benchmark"].config(
                text=f"{benchmark_volatility:.2f}%",
                foreground="black"
            )
            self.metric_labels["volatility_diff"].config(
                text=f"{volatility_diff:+.2f}%",
                foreground="red" if volatility_diff > 0 else "green"  # Moins de volatilité est mieux
            )
            
            # Ratio de Sharpe
            self.metric_labels["sharpe_strategy"].config(
                text=f"{strategy_sharpe:.2f}",
                foreground="green" if strategy_sharpe > 1 else "black"
            )
            self.metric_labels["sharpe_benchmark"].config(
                text=f"{benchmark_sharpe:.2f}",
                foreground="green" if benchmark_sharpe > 1 else "black"
            )
            self.metric_labels["sharpe_diff"].config(
                text=f"{sharpe_diff:+.2f}",
                foreground="green" if sharpe_diff > 0 else "red"
            )
            
            # Drawdown maximum
            self.metric_labels["max_dd_strategy"].config(
                text=f"{strategy_max_drawdown:.2f}%",
                foreground="red"
            )
            self.metric_labels["max_dd_benchmark"].config(
                text=f"{benchmark_max_drawdown:.2f}%",
                foreground="red"
            )
            self.metric_labels["max_dd_diff"].config(
                text=f"{max_dd_diff:+.2f}%",
                foreground="green" if max_dd_diff > 0 else "red"  # Moins de drawdown est mieux (valeurs négatives)
            )
            
            # Alpha
            self.metric_labels["alpha_strategy"].config(
                text=f"{alpha:.4f}%",
                foreground="green" if alpha > 0 else "red"
            )
            self.metric_labels["alpha_benchmark"].config(
                text="0.00%",
                foreground="black"
            )
            self.metric_labels["alpha_diff"].config(
                text=f"{alpha:+.4f}%",
                foreground="green" if alpha > 0 else "red"
            )
            
            # Beta
            self.metric_labels["beta_strategy"].config(
                text=f"{beta:.2f}",
                foreground="black"
            )
            self.metric_labels["beta_benchmark"].config(
                text="1.00",
                foreground="black"
            )
            self.metric_labels["beta_diff"].config(
                text=f"{beta-1:+.2f}",
                foreground="black"
            )
            
            # Corrélation
            self.metric_labels["correlation_strategy"].config(
                text=f"{correlation:.2f}",
                foreground="black"
            )
            self.metric_labels["correlation_benchmark"].config(
                text="1.00",
                foreground="black"
            )
            self.metric_labels["correlation_diff"].config(
                text=f"{correlation-1:+.2f}",
                foreground="black"
            )
            
            # Ajouter une annotation sur le graphique pour l'alpha et le beta
            self.plot.annotate(
                f"α: {alpha:.4f}%  β: {beta:.2f}",
                xy=(0.02, 0.05),
                xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
            )
            
        except Exception as e:
            self.logger.exception("Erreur lors du calcul des métriques comparatives")
            self.clear_metrics()
    
    def clear_chart(self):
        """Efface le graphique"""
        self.plot.clear()
        self.plot.text(0.5, 0.5, "Aucune donnée disponible", ha='center', va='center')
        self.canvas.draw()
    
    def clear_metrics(self):
        """Réinitialise les métriques comparatives"""
        for label in self.metric_labels.values():
            label.config(text="-", foreground="black")