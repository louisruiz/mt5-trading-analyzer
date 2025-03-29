#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget d'allocation pour MT5 Trading Analyzer
"""

import tkinter as tk
from tkinter import ttk
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class AllocationWidget(ttk.Frame):
    """Widget affichant la répartition des allocations"""
    
    def __init__(self, parent, data_manager):
        """
        Initialisation du widget d'allocation
        
        Args:
            parent: Widget parent Tkinter
            data_manager (DataManager): Instance du gestionnaire de données
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = data_manager
        
        # Type de vue sélectionné
        self.view_type_var = tk.StringVar(value="Symbole")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Création des widgets pour l'affichage de l'allocation"""
        # Frame de contrôle pour les options
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label et combobox pour le type de vue
        ttk.Label(control_frame, text="Vue par:").pack(side=tk.LEFT, padx=5)
        view_combo = ttk.Combobox(control_frame, textvariable=self.view_type_var,
                               values=["Symbole", "Direction", "Durée"], width=15)
        view_combo.pack(side=tk.LEFT, padx=5)
        view_combo.bind("<<ComboboxSelected>>", self.update)
        
        # Frame pour les graphiques
        charts_frame = ttk.Frame(self)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Division en deux parties
        left_frame = ttk.Frame(charts_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(charts_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Graphique de répartition par allocation (gauche)
        allocation_frame = ttk.LabelFrame(left_frame, text="Répartition des allocations")
        allocation_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.allocation_figure = Figure(figsize=(5, 4), dpi=100)
        self.allocation_plot = self.allocation_figure.add_subplot(111)
        self.allocation_canvas = FigureCanvasTkAgg(self.allocation_figure, allocation_frame)
        self.allocation_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Graphique de répartition par exposition (droite)
        exposure_frame = ttk.LabelFrame(right_frame, text="Exposition")
        exposure_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.exposure_figure = Figure(figsize=(5, 4), dpi=100)
        self.exposure_plot = self.exposure_figure.add_subplot(111)
        self.exposure_canvas = FigureCanvasTkAgg(self.exposure_figure, exposure_frame)
        self.exposure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update(self, event=None):
        """
        Met à jour les graphiques d'allocation
        
        Args:
            event: Événement Tkinter (non utilisé directement)
        """
        if not self.data_manager.connected or self.data_manager.positions is None:
            self.clear_charts()
            return
        
        try:
            # Mettre à jour les graphiques selon le type de vue sélectionné
            view_type = self.view_type_var.get()
            
            if view_type == "Symbole":
                self.update_symbol_allocation()
            elif view_type == "Direction":
                self.update_direction_allocation()
            elif view_type == "Durée":
                self.update_duration_allocation()
            else:
                self.update_symbol_allocation()  # Par défaut
                
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour des graphiques d'allocation")
            self.clear_charts()
    
    def update_symbol_allocation(self):
        """Met à jour les graphiques d'allocation par symbole"""
        try:
            # Vérifier si des positions sont disponibles
            if self.data_manager.positions is None or self.data_manager.positions.empty:
                self.clear_charts()
                return
            
            # Copier les données de positions
            positions_df = self.data_manager.positions.copy()
            
            # Calculer l'exposition par symbole (en tenant compte du sens)
            positions_df['exposure'] = positions_df.apply(
                lambda row: row['volume'] * row['price_current'] * (1 if row['type'] == 0 else -1),
                axis=1
            )
            
            # Calculer la taille des positions par symbole
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Grouper par symbole
            allocation = positions_df.groupby('symbol')['position_size'].sum()
            exposure = positions_df.groupby('symbol')['exposure'].sum()
            
            # Calculer les proportions pour l'allocation
            total_size = allocation.sum()
            if total_size <= 0:
                self.clear_charts()
                return
                
            allocation_pct = (allocation / total_size * 100).sort_values(ascending=False)
            
            # Calculer les proportions pour l'exposition (longue/courte)
            total_long = exposure[exposure > 0].sum()
            total_short = abs(exposure[exposure < 0].sum())
            
            # Tracer le graphique d'allocation
            self.allocation_plot.clear()
            bars = self.allocation_plot.bar(allocation_pct.index, allocation_pct.values, color='blue')
            
            # Ajouter les labels
            for bar in bars:
                height = bar.get_height()
                self.allocation_plot.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f"{height:.1f}%", ha='center', va='bottom', rotation=0)
            
            # Formater le graphique d'allocation
            self.allocation_plot.set_title("Répartition des allocations par symbole")
            self.allocation_plot.set_ylabel("% de l'allocation totale")
            self.allocation_plot.set_ylim(0, max(allocation_pct.values) * 1.2 if len(allocation_pct) > 0 else 100)
            self.allocation_figure.autofmt_xdate(rotation=45)
            self.allocation_figure.tight_layout()
            self.allocation_canvas.draw()
            
            # Tracer le graphique d'exposition
            self.exposure_plot.clear()
            
            # Créer les données pour le graphique d'exposition
            exposure_data = [total_long, total_short]
            exposure_labels = ['Long', 'Short']
            exposure_colors = ['green', 'red']
            
            # Graphique en camembert pour l'exposition
            if sum(exposure_data) > 0:
                self.exposure_plot.pie(exposure_data, labels=exposure_labels, colors=exposure_colors,
                        autopct='%1.1f%%', startangle=90, shadow=True)
                self.exposure_plot.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            else:
                self.exposure_plot.text(0.5, 0.5, "Aucune exposition", ha='center', va='center')
                
            # Formater le graphique d'exposition
            self.exposure_plot.set_title("Exposition Long/Short")
            self.exposure_figure.tight_layout()
            self.exposure_canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour de l'allocation par symbole")
            self.clear_charts()
    
    def update_direction_allocation(self):
        """Met à jour les graphiques d'allocation par direction (buy/sell)"""
        try:
            # Vérifier si des positions sont disponibles
            if self.data_manager.positions is None or self.data_manager.positions.empty:
                self.clear_charts()
                return
            
            # Copier les données de positions
            positions_df = self.data_manager.positions.copy()
            
            # Ajouter une colonne pour la direction
            positions_df['direction'] = positions_df['type'].map({0: 'BUY', 1: 'SELL'})
            
            # Calculer la taille des positions par direction
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Grouper par direction
            allocation = positions_df.groupby('direction')['position_size'].sum()
            
            # Calculer les proportions
            total_size = allocation.sum()
            if total_size <= 0:
                self.clear_charts()
                return
                
            allocation_pct = (allocation / total_size * 100)
            
            # Tracer le graphique d'allocation
            self.allocation_plot.clear()
            bars = self.allocation_plot.bar(allocation_pct.index, allocation_pct.values, 
                              color=['green' if idx == 'BUY' else 'red' for idx in allocation_pct.index])
            
            # Ajouter les labels
            for bar in bars:
                height = bar.get_height()
                self.allocation_plot.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f"{height:.1f}%", ha='center', va='bottom', rotation=0)
            
            # Formater le graphique d'allocation
            self.allocation_plot.set_title("Répartition des allocations par direction")
            self.allocation_plot.set_ylabel("% de l'allocation totale")
            self.allocation_plot.set_ylim(0, 100)
            self.allocation_figure.tight_layout()
            self.allocation_canvas.draw()
            
            # Tracer le graphique d'exposition par symbole et direction
            self.exposure_plot.clear()
            
            # Calculer l'exposition par symbole et direction
            pivot = pd.pivot_table(positions_df, values='position_size', 
                                 index='symbol', columns='direction', 
                                 aggfunc='sum', fill_value=0)
            
            # Trier par exposition totale
            pivot['total'] = pivot.sum(axis=1)
            pivot = pivot.sort_values('total', ascending=False).drop('total', axis=1)
            
            # Limiter à 10 symboles maximum pour la lisibilité
            if len(pivot) > 10:
                pivot = pivot.iloc[:10]
            
            # Créer le graphique à barres empilées
            if not pivot.empty and 'BUY' in pivot.columns and 'SELL' in pivot.columns:
                pivot.plot(kind='bar', stacked=True, ax=self.exposure_plot, 
                        color=['green', 'red'])
                
                # Formater le graphique d'exposition
                self.exposure_plot.set_title("Exposition par symbole et direction")
                self.exposure_plot.set_ylabel("Taille de position")
                self.exposure_plot.legend(title="Direction")
                self.exposure_figure.autofmt_xdate(rotation=45)
                self.exposure_figure.tight_layout()
            else:
                self.exposure_plot.text(0.5, 0.5, "Données insuffisantes", ha='center', va='center')
                
            self.exposure_canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour de l'allocation par direction")
            self.clear_charts()
    
    def update_duration_allocation(self):
        """Met à jour les graphiques d'allocation par durée des positions"""
        try:
            # Vérifier si des positions sont disponibles
            if self.data_manager.positions is None or self.data_manager.positions.empty:
                self.clear_charts()
                return
            
            # Copier les données de positions
            positions_df = self.data_manager.positions.copy()
            
            # Calculer la durée de chaque position en minutes
            now = pd.Timestamp.now()
            positions_df['duration_minutes'] = positions_df['time'].apply(
                lambda x: (now - pd.Timestamp.fromtimestamp(x)).total_seconds() / 60
            )
            
            # Catégoriser les durées
            def categorize_duration(minutes):
                if minutes < 30:
                    return "< 30 min (Scalping)"
                elif minutes < 60:
                    return "30-60 min (Intraday)"
                elif minutes < 1440:  # 24 heures
                    return "1-24 h (Day Trading)"
                else:
                    return "> 24 h (Swing/Position)"
            
            positions_df['duration_category'] = positions_df['duration_minutes'].apply(categorize_duration)
            
            # Calculer la taille des positions par catégorie de durée
            positions_df['position_size'] = positions_df['volume'] * positions_df['price_current']
            
            # Grouper par catégorie de durée
            allocation = positions_df.groupby('duration_category')['position_size'].sum()
            
            # Définir l'ordre des catégories
            category_order = ["< 30 min (Scalping)", "30-60 min (Intraday)", 
                             "1-24 h (Day Trading)", "> 24 h (Swing/Position)"]
            allocation = allocation.reindex(category_order).dropna()
            
            # Calculer les proportions
            total_size = allocation.sum()
            if total_size <= 0:
                self.clear_charts()
                return
                
            allocation_pct = (allocation / total_size * 100)
            
            # Tracer le graphique d'allocation
            self.allocation_plot.clear()
            
            # Définir les couleurs pour chaque catégorie
            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
            
            # Créer le graphique à secteurs (pie chart)
            wedges, texts, autotexts = self.allocation_plot.pie(
                allocation_pct.values, 
                labels=allocation_pct.index, 
                colors=colors[:len(allocation_pct)],
                autopct='%1.1f%%', 
                startangle=90, 
                shadow=True
            )
            
            # Ajuster les propriétés des textes
            for text in texts:
                text.set_fontsize(8)
            
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_weight('bold')
            
            # Formater le graphique d'allocation
            self.allocation_plot.set_title("Répartition des allocations par durée")
            self.allocation_plot.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            self.allocation_figure.tight_layout()
            self.allocation_canvas.draw()
            
            # Tracer le graphique d'exposition par catégorie et direction
            self.exposure_plot.clear()
            
            # Ajouter une colonne pour la direction
            positions_df['direction'] = positions_df['type'].map({0: 'BUY', 1: 'SELL'})
            
            # Créer un tableau croisé par durée et direction
            pivot = pd.pivot_table(positions_df, values='position_size', 
                                 index='duration_category', columns='direction', 
                                 aggfunc='sum', fill_value=0)
            
            # Réordonner selon la catégorie
            pivot = pivot.reindex(category_order).dropna(how='all')
            
            # Créer le graphique à barres empilées
            if not pivot.empty and len(pivot.columns) > 0:
                pivot.plot(kind='bar', stacked=True, ax=self.exposure_plot, 
                        color=['green', 'red'])
                
                # Formater le graphique d'exposition
                self.exposure_plot.set_title("Exposition par durée et direction")
                self.exposure_plot.set_ylabel("Taille de position")
                self.exposure_plot.set_xlabel("")
                self.exposure_plot.legend(title="Direction")
                self.exposure_figure.tight_layout()
            else:
                self.exposure_plot.text(0.5, 0.5, "Données insuffisantes", ha='center', va='center')
                
            self.exposure_canvas.draw()
            
        except Exception as e:
            self.logger.exception("Erreur lors de la mise à jour de l'allocation par durée")
            self.clear_charts()
    
    def clear_charts(self):
        """Efface les graphiques"""
        # Graphique d'allocation
        self.allocation_plot.clear()
        self.allocation_plot.text(0.5, 0.5, "Aucune donnée disponible", ha='center', va='center')
        self.allocation_figure.tight_layout()
        self.allocation_canvas.draw()
        
        # Graphique d'exposition
        self.exposure_plot.clear()
        self.exposure_plot.text(0.5, 0.5, "Aucune donnée disponible", ha='center', va='center')
        self.exposure_figure.tight_layout()
        self.exposure_canvas.draw()