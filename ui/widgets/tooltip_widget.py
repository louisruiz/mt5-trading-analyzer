#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget de tooltip avancé pour l'affichage des interprétations de métriques
"""

import tkinter as tk
from tkinter import ttk
import logging

class AdvancedTooltip:
    """
    Classe pour créer des tooltips avancés avec interprétation de métriques
    """
    
    def __init__(self, widget, interpretation_data=None, delay=500, wrap_length=350):
        """
        Initialisation du tooltip
        
        Args:
            widget: Widget Tkinter auquel attacher le tooltip
            interpretation_data (dict): Données d'interprétation de la métrique
            delay (int): Délai en ms avant l'affichage du tooltip
            wrap_length (int): Longueur maximale du texte avant saut de ligne
        """
        self.widget = widget
        self.interpretation_data = interpretation_data
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.after_id = None
        
        # Lier les événements de la souris
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide)
        self.widget.bind("<ButtonPress>", self.hide)
    
    def schedule(self, event=None):
        """Planifie l'affichage du tooltip après le délai"""
        self.after_id = self.widget.after(self.delay, self.show)
    
    def show(self):
        """Affiche le tooltip"""
        if self.tooltip_window or not self.interpretation_data:
            return
        
        # Créer une nouvelle fenêtre top-level
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.overrideredirect(True)  # Pas de décorations de fenêtre
        
        # Position du tooltip
        x = self.widget.winfo_rootx() + self.widget.winfo_width()
        y = self.widget.winfo_rooty()
        self.tooltip_window.geometry(f"+{x}+{y}")
        
        # Construire le contenu du tooltip
        self.create_tooltip_content()
        
        # Définir la couleur de fond et la bordure
        self.tooltip_window.configure(background="#f9f9f9", bd=1, relief="solid")
        
        # Mettre au premier plan
        self.tooltip_window.lift()
        
        # Animer l'apparition
        self.tooltip_window.attributes("-alpha", 0.0)
        self.fade_in()
    
    def create_tooltip_content(self):
        """Construit le contenu du tooltip basé sur les données d'interprétation"""
        frame = ttk.Frame(self.tooltip_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre avec la métrique et sa valeur
        title_text = f"{self.interpretation_data['metric']}: {self.interpretation_data['value']:.3f}"
        title = ttk.Label(frame, text=title_text, font=("TkDefaultFont", 11, "bold"))
        title.pack(anchor=tk.W, pady=(0, 5))
        
        # Rating avec couleur appropriée
        rating_frame = ttk.Frame(frame)
        rating_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(rating_frame, text="Évaluation: ").pack(side=tk.LEFT)
        rating_label = ttk.Label(rating_frame, text=self.interpretation_data['rating'], foreground=self.interpretation_data['color'])
        rating_label.pack(side=tk.LEFT)
        
        # Séparateur
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Interprétation principale
        interp_label = ttk.Label(frame, text=self.interpretation_data['interpretation'], 
                               wraplength=self.wrap_length, justify=tk.LEFT)
        interp_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Analyse de tendance si disponible
        if 'trend_analysis' in self.interpretation_data and self.interpretation_data['trend_analysis']:
            trend_frame = ttk.LabelFrame(frame, text="Analyse de tendance", padding=5)
            trend_frame.pack(fill=tk.X, pady=(5, 5))
            
            trend_label = ttk.Label(trend_frame, text=self.interpretation_data['trend_analysis'], 
                                  wraplength=self.wrap_length - 10, justify=tk.LEFT)
            trend_label.pack(anchor=tk.W)
        
        # Analyse comparative si disponible (pour Sortino)
        if 'comparative_analysis' in self.interpretation_data and self.interpretation_data['comparative_analysis']:
            comp_frame = ttk.LabelFrame(frame, text="Analyse comparative", padding=5)
            comp_frame.pack(fill=tk.X, pady=(5, 5))
            
            comp_label = ttk.Label(comp_frame, text=self.interpretation_data['comparative_analysis'], 
                                 wraplength=self.wrap_length - 10, justify=tk.LEFT)
            comp_label.pack(anchor=tk.W)
        
        # Analyse contextuelle si disponible (pour Calmar)
        if 'contextual_analysis' in self.interpretation_data and self.interpretation_data['contextual_analysis']:
            context_frame = ttk.LabelFrame(frame, text="Analyse contextuelle", padding=5)
            context_frame.pack(fill=tk.X, pady=(5, 5))
            
            context_label = ttk.Label(context_frame, text=self.interpretation_data['contextual_analysis'], 
                                    wraplength=self.wrap_length - 10, justify=tk.LEFT)
            context_label.pack(anchor=tk.W)
        
        # Recommandations
        if 'recommendations' in self.interpretation_data and self.interpretation_data['recommendations']:
            recom_frame = ttk.LabelFrame(frame, text="Recommandations", padding=5)
            recom_frame.pack(fill=tk.X, pady=(5, 0))
            
            for i, rec in enumerate(self.interpretation_data['recommendations']):
                rec_label = ttk.Label(recom_frame, text=f"{i+1}. {rec}", 
                                    wraplength=self.wrap_length - 10, justify=tk.LEFT)
                rec_label.pack(anchor=tk.W, pady=(0, 3))
    
    def fade_in(self, alpha=0.0):
        """Anime l'apparition progressive du tooltip"""
        if self.tooltip_window:
            alpha += 0.1
            self.tooltip_window.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.widget.after(20, lambda: self.fade_in(alpha))
    
    def hide(self, event=None):
        """Cache le tooltip"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_interpretation(self, new_data):
        """
        Met à jour les données d'interprétation
        
        Args:
            new_data (dict): Nouvelles données d'interprétation
        """
        self.interpretation_data = new_data
        
        # Si le tooltip est déjà affiché, le mettre à jour
        if self.tooltip_window:
            self.hide()
            self.show()