#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de visualisation du D-Leverage pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.constants import TRADING_CATEGORIES
from analysis.metrics_interpreter import MetricsInterpreter

class DLeverageChartWidget(ttk.LabelFrame):
    """Widget affichant l'évolution du D-Leverage avec zones optimales"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget de visualisation D-Leverage
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent, text="Évolution du D-Leverage", padding=5)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        self.metrics_interpreter = MetricsInterpreter()
        
        # Historique des valeurs de D-Leverage
        self.d_leverage_history = {
            "timestamp": [],
            "value": [],
            "avg_duration": []
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour le graphique D-Leverage"""
        # Frame de contrôle en haut
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Choix du nombre de jours à afficher
        ttk.Label(control_frame, text="Période:").pack(side=tk.LEFT, padx=5)
        self.period_var = tk.StringVar(value="30j")
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var,
                                  values=["7j", "30j", "90j", "Max"], width=10)
        period_combo.pack(side=tk.LEFT, padx=5)
        period_combo.bind("<<ComboboxSelected>>", self.update_chart)
        
        # Afficher les zones optimales
        self.show_zones_var = tk.BooleanVar(value=True)
        zones_check = ttk.Checkbutton(control_frame, text="Zones optimales", 
                                     variable=self.show_zones_var,
                                     command=self.update_chart)
        zones_check.pack(side=tk.LEFT, padx=10)
        
        # Afficher les suggestions
        self.show_suggestions_var = tk.BooleanVar(value=True)
        suggestions_check = ttk.Checkbutton(control_frame, text="Suggestions", 
                                          variable=self.show_suggestions_var,
                                          command=self.update_chart)
        suggestions_check.pack(side=tk.LEFT, padx=10)
        
        # Frame principale pour le graphique
        chart_frame = ttk.Frame(self)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Création de la figure matplotlib
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.plot = self.figure.add_subplot(111)
        
        # Intégration dans le widget Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Panneau d'informations en dessous du graphique
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Valeur actuelle de D-Leverage
        self.current_value_label = ttk.Label(info_frame, text="D-Leverage actuel: -")
        self.current_value_label.pack(side=tk.LEFT, padx=10)
        
        # Style de trading détecté
        self.trading_style_label = ttk.Label(info_frame, text="Style détecté: -")
        self.trading_style_label.pack(side=tk.LEFT, padx=10)
        
        # Statut (optimal/sous-optimal/excessif)
        self.status_label = ttk.Label(info_frame, text="Statut: -")
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def update(self):
        """Met à jour le graphique et les informations D-Leverage"""
        if not self.data_manager.connected:
            self.clear_chart()
            return
        
        try:
            # Récupérer la valeur actuelle de D-Leverage
            current_d_leverage = self.data_manager.calculate_d_leverage()
            
            # Récupérer la durée moyenne des positions
            avg_duration = self.data_manager.get_average_position_duration()
            
            # Ajouter au historique
            timestamp = pd.Timestamp.now()
            self.d_leverage_history["timestamp"].append(timestamp)
            self.d_leverage_history["value"].append(current_d_leverage)
            self.d_leverage_history["avg_duration"].append(avg_duration)
            
            # Limiter la taille de l'historique (par exemple, 1000 points maximum)
            max_history = 1000
            if len(self.d_leverage_history["timestamp"]) > max_history:
                self.d_leverage_history["timestamp"] = self.d_leverage_history["timestamp"][-max_history:]
                self.d_leverage_history["value"] = self.d_leverage_history["value"][-max_history:]
                self.d_leverage_history["avg_duration"] = self.d_leverage_history["avg_duration"][-max_history:]
            
            # Mise à jour des labels d'information
            self.current_value_label.config(text=f"D-Leverage actuel: {current_d_leverage:.2f}")
            
            # Déterminer le style de trading
            if avg_duration < 30:
                style = "Scalping"
                style_key = "Scalping"
                self.trading_style_label.config(text=f"Style détecté: {style} (<30min)")
            elif avg_duration < 60:
                style = "Intraday"
                style_key = "Intraday"
                self.trading_style_label.config(text=f"Style détecté: {style} (30-60min)")
            else:
                style = "Swing/Position"
                style_key = "Swing"
                self.trading_style_label.config(text=f"Style détecté: {style} (>60min)")
            
            # Obtenir les seuils pour ce style
            sous_optimal = TRADING_CATEGORIES[style_key]["sous-optimal"]
            optimal_max = TRADING_CATEGORIES[style_key]["optimal_max"]
            
            # Déterminer le statut
            if current_d_leverage < sous_optimal:
                self.status_label.config(text="Statut: Sous-optimal", foreground="blue")
            elif current_d_leverage <= optimal_max:
                self.status_label.config(text="Statut: Optimal", foreground="green")
            else:
                excess = (current_d_leverage / optimal_max - 1) * 100
                self.status_label.config(text=f"Statut: Excessif (+{excess:.1f}%)", foreground="red")
            
            # Mettre à jour le graphique
            self.update_chart()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du D-Leverage")
            self.clear_chart()
    
    def update_chart(self, event=None):
        """Met à jour le graphique D-Leverage selon les options sélectionnées"""
        try:
            # Vérifier si l'historique est vide
            if not self.d_leverage_history["timestamp"]:
                self.clear_chart()
                return
            
            # Convertir les listes en Series pandas pour faciliter le filtrage
            df = pd.DataFrame({
                "timestamp": self.d_leverage_history["timestamp"],
                "value": self.d_leverage_history["value"],
                "avg_duration": self.d_leverage_history["avg_duration"]
            })
            
            # Filtrer selon la période sélectionnée
            period = self.period_var.get()
            if period == "7j":
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=7)
                df = df[df["timestamp"] >= cutoff]
            elif period == "30j":
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=30)
                df = df[df["timestamp"] >= cutoff]
            elif period == "90j":
                cutoff = pd.Timestamp.now() - pd.Timedelta(days=90)
                df = df[df["timestamp"] >= cutoff]
            
            # Vérifier si des données restent après filtrage
            if df.empty:
                self.clear_chart()
                return
            
            # Effacer le graphique précédent
            self.plot.clear()
            
            # Tracer le D-Leverage
            self.plot.plot(df["timestamp"], df["value"], 'b-', linewidth=2, label='D-Leverage')
            
            # Déterminer le style de trading moyen pour la période
            avg_duration_period = df["avg_duration"].mean()
            
            if avg_duration_period < 30:
                style = "Scalping"
                style_key = "Scalping"
            elif avg_duration_period < 60:
                style = "Intraday"
                style_key = "Intraday"
            else:
                style = "Swing/Position"
                style_key = "Swing"
            
            # Obtenir les seuils pour ce style
            sous_optimal = TRADING_CATEGORIES[style_key]["sous-optimal"]
            optimal_max = TRADING_CATEGORIES[style_key]["optimal_max"]
            
            # Tracer les zones optimales si demandé
            if self.show_zones_var.get():
                # Zone optimale
                self.plot.axhspan(sous_optimal, optimal_max, alpha=0.2, color='green', label=f'Zone optimale ({style})')
                
                # Zone sous-optimale
                self.plot.axhspan(0, sous_optimal, alpha=0.1, color='blue', label='Zone sous-optimale')
                
                # Zone excessive
                y_max = max(df["value"].max() * 1.1, optimal_max * 1.5)  # Limiter la hauteur
                self.plot.axhspan(optimal_max, y_max, alpha=0.1, color='red', label='Zone excessive')
                
                # Lignes horizontales aux seuils
                self.plot.axhline(y=sous_optimal, color='blue', linestyle='--', alpha=0.7)
                self.plot.axhline(y=optimal_max, color='red', linestyle='--', alpha=0.7)
            
            # Ajouter des suggestions si demandé
            if self.show_suggestions_var.get():
                # Valeur actuelle de D-Leverage
                current_d_leverage = df["value"].iloc[-1]
                
                # Déterminer si des ajustements sont nécessaires
                if current_d_leverage < sous_optimal:
                    # Suggestion d'augmentation
                    target = (sous_optimal + optimal_max) / 2  # Milieu de la plage optimale
                    increase_pct = ((target / current_d_leverage) - 1) * 100
                    
                    # Annotation pour la suggestion
                    self.plot.annotate(
                        f"Sous-optimal: +{increase_pct:.1f}%",
                        xy=(df["timestamp"].iloc[-1], current_d_leverage),
                        xytext=(20, 20),
                        textcoords="offset points",
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="blue", alpha=0.8)
                    )
                    
                    # Marquer le niveau cible
                    self.plot.axhline(y=target, color='green', linestyle=':', alpha=0.7)
                    self.plot.annotate(
                        f"Cible: {target:.2f}",
                        xy=(df["timestamp"].iloc[-1], target),
                        xytext=(-70, -20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8)
                    )
                elif current_d_leverage > optimal_max:
                    # Suggestion de réduction
                    reduction_needed = 1 - (optimal_max / current_d_leverage)
                    reduction_pct = reduction_needed * 100
                    
                    # Annotation pour la suggestion
                    self.plot.annotate(
                        f"Excessif: -{reduction_pct:.1f}%",
                        xy=(df["timestamp"].iloc[-1], current_d_leverage),
                        xytext=(20, 20),
                        textcoords="offset points",
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"),
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8)
                    )
                    
                    # Marquer le niveau cible
                    self.plot.axhline(y=optimal_max, color='green', linestyle=':', alpha=0.7)
                    self.plot.annotate(
                        f"Cible: {optimal_max:.2f}",
                        xy=(df["timestamp"].iloc[-1], optimal_max),
                        xytext=(-70, -20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="green", alpha=0.8)
                    )
            
            # Configurer le graphique
            self.plot.set_title(f"Évolution du D-Leverage - {style}")
            self.plot.set_xlabel("Date")
            self.plot.set_ylabel("D-Leverage")
            self.plot.grid(True, linestyle='--', alpha=0.7)
            self.plot.legend(loc='upper left')
            
            # Limiter l'axe Y pour éviter les graphiques trop étirés
            y_min = max(0, min(df["value"].min() * 0.9, sous_optimal * 0.8))
            y_max = max(df["value"].max() * 1.1, optimal_max * 1.2)
            self.plot.set_ylim(y_min, y_max)
            
            # Formater l'axe des dates
            self.figure.autofmt_xdate()
            
            # Redessiner le graphique
            self.canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour du graphique D-Leverage")
            self.clear_chart()
    
    def clear_chart(self):
        """Efface le graphique"""
        self.plot.clear()
        self.plot.set_title("Aucune donnée disponible")
        self.plot.grid(True, linestyle='--', alpha=0.7)
        self.canvas.draw()
        
        # Réinitialiser les informations
        self.current_value_label.config(text="D-Leverage actuel: -")
        self.trading_style_label.config(text="Style détecté: -")
        self.status_label.config(text="Statut: -", foreground="black")